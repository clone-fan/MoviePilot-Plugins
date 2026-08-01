"""Plugin uninstall helpers extracted from the main plugin class.

Handles plugin uninstall, path candidates, backup of candidates,
text formatting and installed-plugin id enumeration. Local imports
of PluginManager / Scheduler / SystemConfigOper / SystemConfigKey are
kept inside _uninstall_moviepilot_plugin as in the original.
"""

import json
import re
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..domain import site_helpers


class PluginUninstallMixin:
    """Mixin bundling plugin uninstall helpers."""

    def _normalize_plugin_id(self, value: Any) -> str:
        raw = str(value or "").strip()
        safe = re.sub(r"[^A-Za-z0-9_\-]", "", raw)[:80]
        return safe

    def _uninstall_moviepilot_plugin(self, plugin_id: str, clear_config: Optional[bool] = None, clear_data: Optional[bool] = None) -> Tuple[bool, str, Dict[str, bool]]:
        cleaned = {"config": False, "data": False}
        try:
            from app.core.plugin import PluginManager
            from app.db.systemconfig_oper import SystemConfigOper
            from app.scheduler import Scheduler
            from app.schemas.types import SystemConfigKey
        except Exception as err:
            return False, f"当前 MoviePilot 环境缺少插件卸载依赖：{err}", cleaned

        messages: List[str] = []
        config_oper = SystemConfigOper()
        installed_plugins = config_oper.get(SystemConfigKey.UserInstalledPlugins) or []
        remaining = [p for p in installed_plugins if p != plugin_id]
        if len(remaining) != len(installed_plugins):
            config_oper.set(SystemConfigKey.UserInstalledPlugins, remaining)
            messages.append("已移出已安装列表")
        else:
            messages.append("未在已安装列表中")

        self._remove_plugin_api_safely(plugin_id)
        self._remove_plugin_job_safely(Scheduler(), plugin_id)
        self._remove_plugin_from_folders_safely(config_oper, SystemConfigKey, plugin_id)

        plugin_manager = PluginManager()
        if self._plugin_uninstall_clear_config if clear_config is None else clear_config:
            try:
                cleaned["config"] = bool(plugin_manager.delete_plugin_config(plugin_id))
                messages.append("配置已清理" if cleaned["config"] else "配置未找到")
            except Exception as err:
                messages.append(f"配置清理失败：{err}")
        if self._plugin_uninstall_clear_data if clear_data is None else clear_data:
            try:
                cleaned["data"] = bool(plugin_manager.delete_plugin_data(plugin_id))
                messages.append("数据已清理" if cleaned["data"] else "数据未找到")
            except Exception as err:
                messages.append(f"数据清理失败：{err}")
        try:
            plugin_manager.remove_plugin(plugin_id)
            messages.append("运行实例已移除")
        except Exception as err:
            return False, f"移除运行实例失败：{err}", cleaned
        return True, "；".join(messages), cleaned

    def _path_candidate(self, kind: str, path: Path) -> Dict[str, Any]:
        try:
            size = self._path_size(path) if path.exists() else 0
            mtime = datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            size = 0
            mtime = "未知"
        return {"kind": kind, "path": str(path), "type": "dir" if path.is_dir() else "file", "size": size, "size_text": self._format_bytes(size), "mtime": mtime}

    @staticmethod
    def _path_size(path: Path) -> int:
        if path.is_file():
            return path.stat().st_size
        total = 0
        for item in path.rglob("*"):
            if item.is_file():
                try:
                    total += item.stat().st_size
                except Exception:
                    pass
        return total

    def _backup_plugin_uninstall_candidates(self, plugin_id: str, candidates: List[Dict[str, Any]]) -> str:
        backup_dir = Path("/config/plugins/Signal/PluginUninstallBackup")
        backup_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        zip_path = backup_dir / f"{plugin_id}-residue-{stamp}.zip"
        manifest = {"created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "plugin_id": plugin_id, "candidates": candidates}
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
            for item in candidates:
                path = Path(item.get("path") or "")
                if not path.exists():
                    continue
                base = f"{item.get('kind')}/{path.name}"
                if path.is_file():
                    zf.write(path, base)
                else:
                    for child in path.rglob("*"):
                        if child.is_file():
                            zf.write(child, f"{base}/{child.relative_to(path)}")
        return str(zip_path)

    @staticmethod
    def _format_plugin_uninstall_text(data: Dict[str, Any]) -> str:
        title = "🧩 插件卸载预览" if data.get("dry_run") else "🧩 插件卸载结果"
        lines = [title, f"⦁ 插件ID：{data.get('plugin_id') or '未填写'}", f"⦁ 说明：{data.get('note')}"]
        if data.get("blocked"):
            lines.append(f"⦁ 阻止原因：{data.get('blocked')}")
            return "\n".join(lines)
        actions = []
        actions.append("卸载插件" if data.get("remove_plugin") else "仅清残留")
        if data.get("clear_config"):
            actions.append("清配置")
        if data.get("clear_data"):
            actions.append("清数据")
        actions.append("删本地源码" if data.get("delete_source") else "保留本地源码")
        lines.append(f"⦁ 动作：{' ｜ '.join(actions)}")
        candidates = data.get("candidates") or []
        lines.append(f"⦁ 候选残留：{len(candidates)} 项")
        for item in candidates[:8]:
            lines.append(f"⦁ {item.get('kind')}｜{item.get('type')}｜{item.get('size_text')}｜{item.get('path')}")
        if data.get("dry_run"):
            lines.append("⦁ 状态：仅预览，未卸载或删除")
        else:
            uninstalled = data.get("uninstalled") or []
            if uninstalled:
                ok_count = sum(1 for item in uninstalled if item.get("success"))
                lines.append(f"⦁ 卸载：{ok_count}/{len(uninstalled)} 个")
                for item in uninstalled[:5]:
                    lines.append(f"⦁ {item.get('plugin_id')}｜{item.get('message')}")
            if data.get("cleaned_config") or data.get("cleaned_data"):
                lines.append(f"⦁ 配置/数据：配置 {len(data.get('cleaned_config') or [])} 个 ｜ 数据 {len(data.get('cleaned_data') or [])} 个")
            lines.append(f"⦁ 已删除：{len(data.get('deleted') or [])} 项")
            lines.append(f"⦁ 备份：{data.get('backup_path') or '未生成'}")
        if data.get("errors"):
            lines.append("异常：")
            lines.extend([f"⦁ {e}" for e in data.get("errors", [])[:5]])
        return "\n".join(lines)

    @staticmethod
    def _count_file_lines(path: Path) -> int:
        with path.open('r', encoding='utf-8', errors='ignore') as fh:
            return sum(1 for _ in fh)

    @staticmethod
    def _truncate_file_tail(path: Path, rows: int) -> int:
        if rows <= 0:
            path.write_text('', encoding='utf-8')
            return 0
        with path.open('r', encoding='utf-8', errors='ignore') as fh:
            lines = fh.readlines()
        kept = lines[-min(rows, len(lines)):]
        with path.open('w', encoding='utf-8') as fh:
            fh.writelines(kept)
        return len(kept)

    @staticmethod
    def _get_installed_plugin_ids() -> set:
        try:
            from app.core.plugin import PluginManager
            plugins = PluginManager().get_local_plugins() or []
            return {str(getattr(p, 'id', '')).lower() for p in plugins if getattr(p, 'installed', False) and getattr(p, 'id', None)}
        except Exception:
            return set()

    @staticmethod
    def _settings_value(settings_obj: Any, *names: str, default: Any = "") -> Any:
        for name in names:
            value = getattr(settings_obj, name, None)
            if value not in (None, ""):
                return value
        return default
