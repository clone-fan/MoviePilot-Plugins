"""Plugin uninstall service mixin."""

import os
import re
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from app.log import logger
from app.schemas import NotificationType


class PluginOpsMixin:
    """Plugin uninstall preview, clean, and safe removal operations."""


    def run_plugin_uninstall_preview(self) -> bool:
        ok, _ = self._guard_task("插件卸载预览")
        if not ok:
            return False
        data = self._build_plugin_uninstall_status(clean=False)
        text = self._format_plugin_uninstall_text(data)
        self._save_task_result("插件卸载预览", bool(data.get("success", True)), 0 if data.get("success", True) else 1, text)
        return bool(data.get("success", True))
    def run_plugin_uninstall_clean(self, override: Optional[Dict[str, Any]] = None) -> bool:
        ok, _ = self._guard_task("插件卸载")
        if not ok:
            return False
        ok, _ = self._run_plugin_uninstall_clean(override=override)
        return ok
    def run_plugin_uninstall_confirm_required(self) -> bool:
        ok, _ = self._guard_task("插件卸载")
        if not ok:
            return False
        text = "插件卸载属于高风险操作，请在配置页选择目标插件并打开显式确认后点击执行；远程命令不会直接卸载插件。"
        self._save_task_result("插件卸载", False, 2, text)
        return False
    def _run_plugin_uninstall_clean(self, override: Optional[Dict[str, Any]] = None) -> Tuple[bool, Dict[str, Any]]:
        options = self._plugin_uninstall_options(override)
        if not options["raw_ids"]:
            text = "未执行：请先在配置页选择目标插件。"
            self._save_task_result("插件卸载", False, 2, text)
            return False, {"success": False, "dry_run": False, "plugin_id": "", "uninstalled": [], "errors": [], "blocked": "请先在配置页选择目标插件。", "attempted_actions": 0}
        try:
            data = self._build_plugin_uninstall_status(clean=True, override=override)
            text = self._format_plugin_uninstall_text(data)
            self._save_task_result("插件卸载", bool(data.get("success")), 0 if data.get("success") else 1, text)
            return bool(data.get("success")), data
        except Exception as err:
            self._save_task_result("插件卸载", False, -1, str(err))
            logger.error(f"AgentOpsAssistant 插件卸载执行失败：{err}")
            return False, {"success": False, "dry_run": False, "plugin_id": "", "uninstalled": [], "errors": [str(err)], "blocked": "", "attempted_actions": 0}

    @staticmethod
    def _plugin_uninstall_outcome(data: Dict[str, Any]) -> str:
        uninstalled = sum(1 for item in (data.get("uninstalled") or []) if item.get("success"))
        cleaned = len(data.get("cleaned_config") or []) + len(data.get("cleaned_data") or [])
        deleted = len(data.get("deleted") or [])
        if data.get("success"):
            parts = [f"卸载 {uninstalled} 个插件"]
            if cleaned:
                parts.append(f"清理 {cleaned} 项配置或数据")
            if deleted:
                parts.append(f"删除 {deleted} 项残留")
            return "，".join(parts)
        errors = data.get("errors") or []
        detail = str(errors[0])[:120] if errors else "操作未完成"
        return f"插件卸载执行失败：{detail}"
    def _plugin_uninstall_config_from_payload(self, payload: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        if not isinstance(payload, dict):
            return {}
        override: Dict[str, Any] = {}
        if "plugin_uninstall_ids" in payload:
            override["plugin_uninstall_ids"] = self._parse_csv(payload.get("plugin_uninstall_ids"))
        for key in (
            "plugin_uninstall_remove_plugin",
            "plugin_uninstall_clear_config",
            "plugin_uninstall_clear_data",
            "plugin_uninstall_delete_source",
        ):
            if key in payload:
                override[key] = self._payload_bool(payload.get(key))
        return override
    def _plugin_uninstall_options(self, override: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        override = override or {}
        raw_ids = override.get("plugin_uninstall_ids", self._plugin_uninstall_ids or [])
        if isinstance(raw_ids, str):
            raw_ids = self._parse_csv(raw_ids)
        elif not isinstance(raw_ids, (list, tuple, set)):
            raw_ids = [raw_ids] if raw_ids else []
        raw_ids = list(raw_ids or [])
        return {
            "raw_ids": raw_ids,
            "remove_plugin": bool(override.get("plugin_uninstall_remove_plugin", self._plugin_uninstall_remove_plugin)),
            "clear_config": bool(override.get("plugin_uninstall_clear_config", self._plugin_uninstall_clear_config)),
            "clear_data": bool(override.get("plugin_uninstall_clear_data", self._plugin_uninstall_clear_data)),
            "delete_source": bool(override.get("plugin_uninstall_delete_source", self._plugin_uninstall_delete_source)),
        }
    def _build_plugin_uninstall_status(self, clean: bool = False, override: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        options = self._plugin_uninstall_options(override)
        raw_ids = list(options["raw_ids"])
        ids: List[str] = []
        for rid in raw_ids:
            pid = self._normalize_plugin_id(rid)
            if pid and pid not in ids:
                ids.append(pid)
        result = {"success": True, "dry_run": not clean, "plugin_id": "、".join(ids),
                  "note": "卸载插件并按勾选项清理配置、数据、日志、备份或本地源码残留；不会删除媒体文件、下载任务或 MoviePilot 核心源码。",
                  "remove_plugin": options["remove_plugin"],
                  "clear_config": options["clear_config"],
                  "clear_data": options["clear_data"],
                  "delete_source": options["delete_source"],
                  "uninstalled": [], "cleaned_config": [], "cleaned_data": [],
                  "candidates": [], "deleted": [], "errors": [], "backup_path": "", "blocked": "",
                  "attempted_actions": 0}
        if not ids:
            result.update({"success": False, "blocked": "请先在配置页选择目标插件。"})
            return result
        forbidden = {"agentopsassistant", "mpops", "moviepilot"}
        backups: List[str] = []
        for pid in ids:
            if pid.lower() in forbidden:
                result["errors"].append(f"{pid}: 为避免自毁或误删核心组件，禁止卸载 AgentOpsAssistant / MoviePilot 本体，已跳过。")
                continue
            candidates = self._plugin_uninstall_candidates(pid, delete_source=options["delete_source"])
            for item in candidates:
                item["plugin_id"] = pid
            result["candidates"].extend(candidates)
            if not clean:
                continue
            allowed_candidates = []
            for item in candidates:
                path = Path(item.get("path") or "")
                if self._plugin_uninstall_path_allowed(path, delete_source=options["delete_source"]):
                    allowed_candidates.append(item)
                else:
                    result["errors"].append(f"{path}: 路径越界，不在允许范围内，已跳过删除。")
            if options["remove_plugin"]:
                result["attempted_actions"] += 1
                ok, message, cleaned = self._uninstall_moviepilot_plugin(pid, clear_config=options["clear_config"], clear_data=options["clear_data"])
                result["uninstalled"].append({"plugin_id": pid, "success": ok, "message": message})
                if cleaned.get("config"):
                    result["cleaned_config"].append(pid)
                if cleaned.get("data"):
                    result["cleaned_data"].append(pid)
                if not ok:
                    result["errors"].append(f"{pid}: {message}")
                    continue
            if allowed_candidates:
                backups.append(self._backup_plugin_uninstall_candidates(pid, allowed_candidates))
            for item in allowed_candidates:
                path = Path(item.get("path") or "")
                if not path.exists():
                    continue
                result["attempted_actions"] += 1
                try:
                    if path.is_dir():
                        shutil.rmtree(path)
                    else:
                        path.unlink()
                    result["deleted"].append(item)
                except Exception as err:
                    result["errors"].append(f"{path}: {err}")
        result["backup_path"] = "；".join([b for b in backups if b])
        result["success"] = not result["errors"]
        return result
    @staticmethod
    def _remove_plugin_api_safely(plugin_id: str):
        try:
            from app.api.endpoints.plugin import remove_plugin_api
            remove_plugin_api(plugin_id)
        except Exception as err:
            logger.debug(f"AgentOpsAssistant 移除插件 API 路由跳过：{plugin_id} {err}")
    @staticmethod
    def _remove_plugin_job_safely(scheduler: Any, plugin_id: str):
        try:
            if hasattr(scheduler, "remove_plugin_job"):
                scheduler.remove_plugin_job(plugin_id)
        except Exception as err:
            logger.warning(f"AgentOpsAssistant 移除插件调度失败：{plugin_id} {err}")
    @staticmethod
    def _remove_plugin_from_folders_safely(config_oper: Any, system_config_key: Any, plugin_id: str):
        try:
            folders_key = getattr(system_config_key, "PluginFolders", "PluginFolders")
            folders = config_oper.get(folders_key) or {}
            modified = False
            for _, folder_data in folders.items():
                if isinstance(folder_data, dict) and isinstance(folder_data.get("plugins"), list):
                    if plugin_id in folder_data["plugins"]:
                        folder_data["plugins"].remove(plugin_id)
                        modified = True
                elif isinstance(folder_data, list) and plugin_id in folder_data:
                    folder_data.remove(plugin_id)
                    modified = True
            if modified:
                config_oper.set(folders_key, folders)
        except Exception as err:
            logger.warning(f"AgentOpsAssistant 从插件文件夹移除失败：{plugin_id} {err}")
    def _plugin_uninstall_candidates(self, plugin_id: str, delete_source: Optional[bool] = None) -> List[Dict[str, Any]]:
        lower = plugin_id.lower()
        candidates: List[Dict[str, Any]] = []
        roots = [
            ("runtime_data", Path("/config/plugins") / plugin_id),
            ("runtime_data", Path("/config/plugins") / lower),
            ("backup", Path("/config/plugins_backup") / plugin_id),
            ("backup", Path("/config/plugins_backup") / lower),
        ]
        delete_source = self._plugin_uninstall_delete_source if delete_source is None else delete_source
        if delete_source and self._local_plugin_repo:
            roots.append(("local_source", Path(self._local_plugin_repo) / "plugins.v2" / lower))
        for kind, path in roots:
            if path.exists():
                candidates.append(self._path_candidate(kind, path))
        log_root = Path("/config/logs/plugins")
        for item in sorted(list(log_root.glob(f"{lower}.log*")) + list(log_root.glob(f"{plugin_id}.log*"))):
            if item.exists():
                candidates.append(self._path_candidate("log", item))
        seen = set()
        deduped = []
        for item in candidates:
            key = item.get("path")
            if key not in seen:
                seen.add(key)
                deduped.append(item)
        return deduped
    def _plugin_uninstall_path_allowed(self, path: Path, delete_source: Optional[bool] = None) -> bool:
        roots = [Path("/config/plugins"), Path("/config/plugins_backup"), Path("/config/logs/plugins")]
        delete_source = self._plugin_uninstall_delete_source if delete_source is None else delete_source
        if delete_source and self._local_plugin_repo:
            roots.append(Path(self._local_plugin_repo) / "plugins.v2")
        try:
            resolved = path.resolve(strict=False)
        except Exception:
            return False
        for root in roots:
            try:
                root_resolved = root.resolve(strict=False)
                if resolved == root_resolved or root_resolved in resolved.parents:
                    return True
            except Exception:
                continue
        return False
