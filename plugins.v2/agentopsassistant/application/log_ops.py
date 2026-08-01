"""Log cleaning service mixin."""

import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.log import logger
from app.schemas import NotificationType


class LogOpsMixin:
    """Plugin log preview, cleaning, and truncation."""


    def run_log_preview(self) -> bool:
        ok, _ = self._guard_task("日志清理预览", "log_clean")
        if not ok:
            return False
        data = self._build_log_preview()
        text = self._format_log_preview_text(data)
        self._save_task_result("日志清理预览", True, 0, text)
        return True
    def run_log_clean_scheduled(self) -> bool:
        """Run the configured log cleanup from the scheduler."""
        return self.run_log_clean(scheduled=True)

    def run_log_clean(self, scheduled: bool = False) -> bool:
        ok, _ = self._guard_task("日志清理", "log_clean")
        if not ok:
            return False
        try:
            data = self._build_log_clean_stats(clean=True)
            text = self._format_log_clean_result_text(data)
            attempted = int(data.get("attempted_count") or 0)
            success = not bool(data.get("errors"))
            cleaned = len(data.get("cleaned") or [])
            if scheduled and attempted and self._task_outcome_notification_enabled(self._log_clean_notify):
                outcome = (
                    f"已清理 {cleaned} 个日志文件"
                    if success
                    else f"日志清理执行失败：已处理 {cleaned} 个，失败 {len(data.get('errors') or [])} 个"
                )
                self._notify_fusion_task_outcome(
                    mtype=self._notification_type(self._log_clean_notify_type),
                    title="日志清理",
                    text=text,
                    outcome=outcome,
                    success=success,
                    component="log_clean",
                )
            self._save_task_result("日志清理", success, 0 if success else 1, text)
            return success
        except Exception as err:
            self._save_task_result("日志清理", False, -1, str(err))
            logger.error(f"AgentOpsAssistant 日志清理执行失败：{err}")
            return False
    def _build_log_preview(self) -> Dict[str, Any]:
        return self._build_log_clean_stats(clean=False)
    def _build_log_clean_stats(self, clean: bool = False) -> Dict[str, Any]:
        log_dir = Path("/config/logs/plugins")
        rows = max(0, int(self._log_clean_rows or 0))
        selected = {x.lower() for x in (self._log_clean_selected_ids or []) if x}
        files = []
        cleaned = []
        errors = []
        attempted_count = 0
        installed_ids = self._get_installed_plugin_ids()
        if not log_dir.exists():
            return {"root": str(log_dir), "file_count": 0, "candidate_count": 0, "attempted_count": 0, "total_size": 0, "total_size_text": "0 B", "candidate_size": 0, "candidate_size_text": "0 B", "top_files": [], "candidates": [], "cleaned": [], "errors": [], "rows": rows, "selected_ids": sorted(selected), "dry_run": not clean}
        for item in sorted(list(log_dir.glob("*.log")) + list(log_dir.glob("*.log.*"))):
            if not item.is_file():
                continue
            name = item.name
            original_id = name.split(".log", 1)[0]
            if selected and original_id.lower() not in selected and name.lower() not in selected:
                continue
            try:
                stat = item.stat()
                line_count = self._count_file_lines(item)
            except Exception as err:
                errors.append(f"{name}: {err}")
                continue
            is_split = bool(".log." in name)
            is_deleted_plugin = original_id.lower() not in installed_ids and not self._is_special_log(original_id)
            candidate = (not is_split and line_count > rows) or is_split or is_deleted_plugin
            entry = {"path": str(item), "name": name, "plugin_id": original_id, "size": stat.st_size, "size_text": self._format_bytes(stat.st_size), "mtime": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"), "lines_count": line_count, "is_split": is_split, "is_deleted_plugin": is_deleted_plugin, "candidate": candidate}
            files.append(entry)
            if clean and candidate:
                attempted_count += 1
                try:
                    if is_split or is_deleted_plugin:
                        item.unlink()
                        action = "delete"
                        cleaned_lines = line_count
                    else:
                        kept = self._truncate_file_tail(item, rows)
                        action = "truncate"
                        cleaned_lines = max(0, line_count - kept)
                    cleaned.append({**entry, "action": action, "cleaned_lines": cleaned_lines})
                except Exception as err:
                    errors.append(f"{name}: {err}")
        candidates = [x for x in files if x["candidate"]]
        files.sort(key=lambda x: x["size"], reverse=True)
        return {"root": str(log_dir), "file_count": len(files), "candidate_count": len(candidates), "attempted_count": attempted_count, "total_size": sum(x["size"] for x in files), "total_size_text": self._format_bytes(sum(x["size"] for x in files)), "candidate_size": sum(x["size"] for x in candidates), "candidate_size_text": self._format_bytes(sum(x["size"] for x in candidates)), "top_files": files[:10], "candidates": candidates[:30], "cleaned": cleaned, "errors": errors[:20], "rows": rows, "selected_ids": sorted(selected), "dry_run": not clean}
    def _format_log_preview_text(self, data: Dict[str, Any]) -> str:
        lines = [
            "🧹 日志清理预览（未执行清理）",
            f"⦁ 扫描文件：{data.get('file_count', 0)} 个",
            f"⦁ 总体积：{data.get('total_size_text')}",
            f"⦁ 候选：{data.get('candidate_count', 0)} 个 / {data.get('candidate_size_text')}",
            "",
            "体积 Top：",
        ]
        for item in data.get("top_files", [])[:8]:
            lines.append(f"⦁ {item['name']}｜{item['size_text']}｜{item['mtime']}")
        lines.append("")
        lines.append(f"规则：标准 .log 按最后 {data.get('rows')} 行保留；.log.N 分割日志和已卸载插件日志列为可清理候选。")
        return "\n".join(lines)
    def _format_log_clean_result_text(self, data: Dict[str, Any]) -> str:
        lines = [
            "🧹 插件日志清理结果",
            f"⦁ 扫描文件：{data.get('file_count', 0)} 个",
            f"⦁ 候选文件：{data.get('candidate_count', 0)} 个 / {data.get('candidate_size_text')}",
            f"⦁ 已处理：{len(data.get('cleaned') or [])} 个",
            f"⦁ 保留行数：{data.get('rows')}",
        ]
        for item in (data.get('cleaned') or [])[:8]:
            action = "删除" if item.get("action") == "delete" else "截断"
            lines.append(f"⦁ {action} {item['name']}｜清理行数 {item.get('cleaned_lines', 0)}")
        if data.get('errors'):
            lines.append("异常：")
            lines.extend([f"⦁ {e}" for e in data.get('errors', [])[:5]])
        return "\n".join(lines)
    @staticmethod
    def _is_special_log(plugin_id: str) -> bool:
        return plugin_id.lower() in {"plugin", "system", "main", "error"}
