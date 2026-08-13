"""Plugin uninstall service mixin."""

import os
import re
import shutil
import time
from datetime import datetime
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
            logger.error(f"Signal 插件卸载执行失败：{err}")
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
                  "note": "执行按钮始终卸载插件本体；按勾选项额外清理配置、数据、运行源码和本地源码，同时删除日志与历史卸载残留；不会生成备份，操作不可逆。",
                  "clear_config": options["clear_config"],
                  "clear_data": options["clear_data"],
                  "delete_source": options["delete_source"],
                   "uninstalled": [], "cleaned_config": [], "cleaned_data": [],
                   "candidates": [], "deleted": [], "verification": [], "errors": [], "blocked": "",
                   "attempted_actions": 0}
        if not ids:
            result.update({"success": False, "blocked": "请先在配置页选择目标插件。"})
            return result
        forbidden = {"signal", "moviepilot"}
        for pid in ids:
            if pid.lower() in forbidden:
                result["errors"].append(f"{pid}: 为避免自毁或误删核心组件，禁止卸载 Signal / MoviePilot 本体，已跳过。")
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
            result["attempted_actions"] += 1
            ok, message, cleaned = self._uninstall_moviepilot_plugin(pid, clear_config=options["clear_config"], clear_data=options["clear_data"])
            result["uninstalled"].append({"plugin_id": pid, "success": ok, "message": message})
            result["uninstalled"][-1]["verification"] = {
                key: bool(value)
                for key, value in cleaned.items()
                if key in {"installed_list", "plugin_folders", "api", "scheduler", "runtime"}
            }
            if cleaned.get("config"):
                result["cleaned_config"].append(pid)
            if cleaned.get("data"):
                result["cleaned_data"].append(pid)
            if not ok:
                result["errors"].append(f"{pid}: {message}")
            if allowed_candidates:
                self._isolate_plugin_runtime_candidates(pid, allowed_candidates, result)
            for item in allowed_candidates:
                path = Path(item.get("path") or "")
                if not path.exists():
                    continue
                result["attempted_actions"] += 1
                try:
                    self._delete_plugin_path_with_retry(path)
                    result["deleted"].append(item)
                except Exception as err:
                    result["errors"].append(f"{path}: {err}")
            for item in allowed_candidates:
                original_path = Path(item.get("original_path") or item.get("path") or "")
                current_path = Path(item.get("path") or "")
                if original_path.exists() or current_path.exists():
                    result["errors"].append(f"{pid}: 清理后仍有残留：{current_path}")
            remaining = self._plugin_uninstall_candidates(pid, delete_source=options["delete_source"])
            path_clean = True
            for item in remaining:
                path = Path(item.get("path") or "")
                if path.exists() and self._plugin_uninstall_path_allowed(path, delete_source=options["delete_source"]):
                    path_clean = False
                    result["errors"].append(f"{pid}: 最终复核仍有残留：{path}")
            result["verification"].append({"plugin_id": pid, "paths": path_clean})
        self._remove_empty_isolation_root()
        result["success"] = not result["errors"]
        return result
    @staticmethod
    def _remove_plugin_api_safely(plugin_id: str) -> bool:
        try:
            from app.api.endpoints.plugin import remove_plugin_api
            result = remove_plugin_api(plugin_id)
            return result is not False
        except Exception as err:
            logger.debug(f"Signal 移除插件 API 路由跳过：{plugin_id} {err}")
            return False
    @staticmethod
    def _remove_plugin_job_safely(scheduler: Any, plugin_id: str) -> bool:
        try:
            if hasattr(scheduler, "remove_plugin_job"):
                result = scheduler.remove_plugin_job(plugin_id)
                return result is not False
            return True
        except Exception as err:
            logger.warning(f"Signal 移除插件调度失败：{plugin_id} {err}")
            return False
    @staticmethod
    def _remove_plugin_from_folders_safely(config_oper: Any, system_config_key: Any, plugin_id: str) -> bool:
        try:
            folders_key = getattr(system_config_key, "PluginFolders", "PluginFolders")
            folders = config_oper.get(folders_key) or {}
            modified = False
            folder_values = folders.values() if isinstance(folders, dict) else folders if isinstance(folders, list) else []
            for folder_data in folder_values:
                if isinstance(folder_data, dict) and isinstance(folder_data.get("plugins"), list):
                    original = list(folder_data["plugins"])
                    folder_data["plugins"] = [item for item in original if str(item).lower() != plugin_id.lower()]
                    if len(folder_data["plugins"]) != len(original):
                        modified = True
                elif isinstance(folder_data, list) and any(str(item).lower() == plugin_id.lower() for item in folder_data):
                    folder_data[:] = [item for item in folder_data if str(item).lower() != plugin_id.lower()]
                    modified = True
            if modified:
                config_oper.set(folders_key, folders)
            verify_values = folders.values() if isinstance(folders, dict) else folders if isinstance(folders, list) else []
            for folder_data in verify_values:
                values = folder_data.get("plugins") if isinstance(folder_data, dict) else folder_data
                if isinstance(values, list) and any(str(item).lower() == plugin_id.lower() for item in values):
                    return False
            return True
        except Exception as err:
            logger.warning(f"Signal 从插件文件夹移除失败：{plugin_id} {err}")
            return False
    def _plugin_uninstall_candidates(self, plugin_id: str, delete_source: Optional[bool] = None) -> List[Dict[str, Any]]:
        lower = plugin_id.lower()
        candidates: List[Dict[str, Any]] = []
        roots = [("runtime_data", Path("/config/plugins")), ("backup", Path("/config/plugins_backup"))]
        delete_source = self._plugin_uninstall_delete_source if delete_source is None else delete_source
        if delete_source:
            runtime_source_root = self._plugin_runtime_source_root()
            if runtime_source_root:
                roots.append(("runtime_source", runtime_source_root))
            if self._local_plugin_repo:
                roots.append(("local_source", Path(self._local_plugin_repo) / "plugins.v2"))
        for kind, root in roots:
            if not root.exists() or not root.is_dir():
                continue
            try:
                for path in root.iterdir():
                    if path.name.lower() == lower:
                        candidates.append(self._path_candidate(kind, path))
            except OSError:
                continue
        log_root = Path("/config/logs/plugins")
        if log_root.exists() and log_root.is_dir():
            try:
                for item in sorted(log_root.iterdir(), key=lambda path: path.name.lower()):
                    stem = item.name.split(".log", 1)[0].lower()
                    if stem == lower and item.exists():
                        candidates.append(self._path_candidate("log", item))
            except OSError:
                pass
        # Historical residue archives are deletion targets, never new backups.
        plugin_root = Path("/config/plugins")
        if plugin_root.exists() and plugin_root.is_dir():
            for signal_dir in plugin_root.iterdir():
                if signal_dir.name.lower() != "signal" or not signal_dir.is_dir():
                    continue
                for backup_dir in signal_dir.iterdir():
                    if backup_dir.name.lower() != "pluginuninstallbackup" or not backup_dir.is_dir():
                        continue
                    for archive in backup_dir.iterdir():
                        if archive.is_file() and archive.name.lower().startswith(f"{lower}-residue-") and archive.suffix.lower() == ".zip":
                            candidates.append(self._path_candidate("uninstall_backup", archive))
        seen = set()
        deduped = []
        for item in candidates:
            key = item.get("path")
            if key not in seen:
                seen.add(key)
                deduped.append(item)
        return deduped

    @staticmethod
    def _isolation_root() -> Path:
        return Path("/config/.signal-uninstall-isolation")

    @staticmethod
    def _plugin_runtime_source_root() -> Optional[Path]:
        """Return MoviePilot's installed plugin source root.

        MoviePilot copies local-repository plugins from ``/config/FFplugin``
        into ``<ROOT_PATH>/app/plugins``. ``PluginManager.remove_plugin`` only
        unregisters the running instance, so source deletion must explicitly
        include that installed directory.
        """
        try:
            from app.core.config import settings

            root_path = getattr(settings, "ROOT_PATH", None)
            return Path(root_path) / "app" / "plugins" if root_path else None
        except Exception as err:
            logger.warning(f"Signal 无法解析 MoviePilot 运行源码目录：{err}")
            return None

    def _isolate_plugin_runtime_candidates(self, plugin_id: str, candidates: List[Dict[str, Any]], result: Dict[str, Any]) -> None:
        root = self._isolation_root()
        runtime_items = [item for item in candidates if item.get("kind") == "runtime_data" and Path(item.get("path") or "").is_dir()]
        if not runtime_items:
            return
        try:
            root.mkdir(parents=True, exist_ok=True)
        except Exception as err:
            result["errors"].append(f"{plugin_id}: 创建临时隔离目录失败：{err}")
            return
        stamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        for index, item in enumerate(runtime_items):
            source = Path(item.get("path") or "")
            target = root / f"{self._normalize_plugin_id(plugin_id).lower()}-{stamp}-{index}"
            item["original_path"] = str(source)
            try:
                shutil.move(str(source), str(target))
                item["path"] = str(target)
                item["isolated"] = True
            except Exception as err:
                result["errors"].append(f"{source}: 临时隔离失败：{err}")

    @staticmethod
    def _delete_plugin_path_with_retry(path: Path, attempts: int = 3) -> None:
        last_error = None
        for attempt in range(max(1, attempts)):
            if not path.exists() and not path.is_symlink():
                return
            try:
                if path.is_symlink():
                    path.unlink()
                elif path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
                return
            except Exception as err:
                last_error = err
                if attempt + 1 < max(1, attempts):
                    time.sleep(0.05)
        raise last_error or OSError(f"删除失败：{path}")

    def _cleanup_pending_plugin_uninstall_isolation(self) -> Dict[str, Any]:
        """Retry deletion of temporary uninstall staging left by an earlier failed run."""
        root = self._isolation_root()
        result: Dict[str, Any] = {"success": True, "attempted": 0, "deleted": [], "errors": []}
        if not root.exists():
            return result
        if not root.is_dir():
            result["success"] = False
            result["errors"].append(f"卸载临时目录不是文件夹：{root}")
            return result
        try:
            children = list(root.iterdir())
        except Exception as err:
            result["success"] = False
            result["errors"].append(f"读取卸载临时目录失败：{err}")
            return result
        for path in children:
            if not self._plugin_uninstall_path_allowed(path, delete_source=False):
                result["errors"].append(f"卸载临时路径越界：{path}")
                continue
            result["attempted"] += 1
            try:
                self._delete_plugin_path_with_retry(path)
                result["deleted"].append(str(path))
            except Exception as err:
                result["errors"].append(f"{path}: {err}")
        self._remove_empty_isolation_root()
        if root.exists():
            result["errors"].append(f"卸载临时目录仍有残留：{root}")
        result["success"] = not result["errors"]
        return result

    def _remove_empty_isolation_root(self) -> None:
        root = self._isolation_root()
        try:
            if root.exists() and root.is_dir() and not any(root.iterdir()):
                root.rmdir()
        except Exception:
            pass
    def _plugin_uninstall_path_allowed(self, path: Path, delete_source: Optional[bool] = None) -> bool:
        roots = [Path("/config/plugins"), Path("/config/plugins_backup"), Path("/config/logs/plugins"), self._isolation_root()]
        delete_source = self._plugin_uninstall_delete_source if delete_source is None else delete_source
        if delete_source:
            runtime_source_root = self._plugin_runtime_source_root()
            if runtime_source_root:
                roots.append(runtime_source_root)
            if self._local_plugin_repo:
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
