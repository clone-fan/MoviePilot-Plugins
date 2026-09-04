"""Explicit legacy AgentOpsAssistant purge adapter.

This module is intentionally isolated from Signal's ordinary plugin-operation
paths.  The fixed-target purge contract remains available for migration and
cleanup, but normal Signal scheduling, notification, and uninstall flows do
not depend on this identity.
"""

import re
from pathlib import Path
from typing import Any, Dict, List

from app.sdk.logging import logger

from ..domain.plugin_generations import generation_roots


AGENTOPSASSISTANT_PURGE_TARGET = "AgentOpsAssistant"
_PURGE_REMOVE = object()


class LegacyAgentOpsAssistantPurgeMixin:
    """Fixed-target, no-backup purge operations for the legacy plugin."""

    @staticmethod
    def _agentopsassistant_reference(value: Any) -> bool:
        text = str(value or "").strip().lower()
        if not text:
            return False
        target = AGENTOPSASSISTANT_PURGE_TARGET.lower()
        if text == target:
            return True
        return bool(re.search(rf"(^|[^a-z0-9]){re.escape(target)}([^a-z0-9]|$)", text))

    @classmethod
    def _agentopsassistant_reference_count(cls, value: Any) -> int:
        if isinstance(value, dict):
            return sum(
                int(cls._agentopsassistant_reference(key)) + cls._agentopsassistant_reference_count(item)
                for key, item in value.items()
            )
        if isinstance(value, (list, tuple, set)):
            return sum(cls._agentopsassistant_reference_count(item) for item in value)
        return int(cls._agentopsassistant_reference(value))

    @classmethod
    def _agentopsassistant_target_component(cls, value: Any) -> bool:
        if not isinstance(value, dict):
            return False
        identity_keys = {
            "id", "key", "plugin", "pluginid", "plugin_id", "component",
            "componentid", "component_id", "widget", "widgetid", "widget_id",
        }
        for key, item in value.items():
            normalized = str(key or "").replace("-", "_").lower()
            if normalized in identity_keys and cls._agentopsassistant_reference(item):
                return True
        nested = value.get("config")
        return isinstance(nested, dict) and cls._agentopsassistant_target_component(nested)

    @classmethod
    def _scrub_agentopsassistant_references(cls, value: Any) -> Any:
        if isinstance(value, dict):
            if cls._agentopsassistant_target_component(value):
                return _PURGE_REMOVE
            cleaned: Dict[Any, Any] = {}
            for key, item in value.items():
                if cls._agentopsassistant_reference(key):
                    continue
                scrubbed = cls._scrub_agentopsassistant_references(item)
                if scrubbed is not _PURGE_REMOVE:
                    cleaned[key] = scrubbed
            return cleaned
        if isinstance(value, list):
            cleaned_items = []
            for item in value:
                scrubbed = cls._scrub_agentopsassistant_references(item)
                if scrubbed is not _PURGE_REMOVE:
                    cleaned_items.append(scrubbed)
            return cleaned_items
        if isinstance(value, tuple):
            scrubbed = cls._scrub_agentopsassistant_references(list(value))
            return tuple(scrubbed)
        if cls._agentopsassistant_reference(value):
            return _PURGE_REMOVE
        return value

    @staticmethod
    def _agentopsassistant_config_root() -> Path:
        try:
            from app.sdk.config import settings

            return Path(str(getattr(settings, "CONFIG_PATH", None) or "/config"))
        except Exception:
            return Path("/config")

    def _agentopsassistant_purge_candidates(self) -> List[Dict[str, Any]]:
        target = AGENTOPSASSISTANT_PURGE_TARGET.lower()
        config_root = self._agentopsassistant_config_root()
        candidates: List[Dict[str, Any]] = []

        def add_exact_children(kind: str, root: Path) -> None:
            if not root.exists() or not root.is_dir():
                return
            try:
                for item in root.iterdir():
                    if item.name.lower() == target:
                        candidates.append(self._path_candidate(kind, item))
            except OSError:
                return

        add_exact_children("runtime_data", config_root / "plugins")
        add_exact_children("plugin_backup", config_root / "plugins_backup")
        ffplugin_roots = generation_roots(config_root / "FFplugin")
        for root in ffplugin_roots:
            add_exact_children("local_source", root)
        runtime_source_root = self._plugin_runtime_source_root()
        if runtime_source_root:
            add_exact_children("runtime_source", runtime_source_root)
        if self._local_plugin_repo:
            known = {root.resolve(strict=False) for root in ffplugin_roots}
            for configured_source in generation_roots(Path(self._local_plugin_repo)):
                if configured_source.resolve(strict=False) not in known:
                    add_exact_children("configured_local_source", configured_source)

        log_root = config_root / "logs" / "plugins"
        if log_root.exists() and log_root.is_dir():
            try:
                for item in log_root.iterdir():
                    if item.name.lower().split(".log", 1)[0] == target:
                        candidates.append(self._path_candidate("log", item))
            except OSError:
                pass

        isolation_root = config_root / ".signal-uninstall-isolation"
        if isolation_root.exists() and isolation_root.is_dir():
            try:
                for item in isolation_root.iterdir():
                    if item.name.lower() == target or item.name.lower().startswith(f"{target}-"):
                        candidates.append(self._path_candidate("uninstall_isolation", item))
            except OSError:
                pass

        residue_root = config_root / "plugins" / "Signal" / "PluginUninstallBackup"
        if residue_root.exists() and residue_root.is_dir():
            try:
                for item in residue_root.iterdir():
                    name = item.name.lower()
                    if item.is_file() and name.startswith(f"{target}-residue-") and name.endswith(".zip"):
                        candidates.append(self._path_candidate("uninstall_backup", item))
            except OSError:
                pass

        deduped: List[Dict[str, Any]] = []
        seen = set()
        for item in candidates:
            path = str(item.get("path") or "")
            if path and path not in seen:
                seen.add(path)
                deduped.append(item)
        return deduped

    def _agentopsassistant_purge_path_allowed(self, path: Path) -> bool:
        config_root = self._agentopsassistant_config_root()
        roots = [
            config_root / "plugins",
            config_root / "plugins_backup",
            config_root / "logs" / "plugins",
            config_root / ".signal-uninstall-isolation",
        ]
        roots.extend(generation_roots(config_root / "FFplugin"))
        runtime_source_root = self._plugin_runtime_source_root()
        if runtime_source_root:
            roots.append(runtime_source_root)
        if self._local_plugin_repo:
            roots.extend(generation_roots(Path(self._local_plugin_repo)))
        try:
            resolved = path.resolve(strict=False)
        except Exception:
            return False
        for root in roots:
            try:
                root_resolved = root.resolve(strict=False)
                if resolved != root_resolved and root_resolved in resolved.parents:
                    return True
            except Exception:
                continue
        return False

    @staticmethod
    def _agentopsassistant_system_config_snapshot(config_oper: Any) -> Dict[str, Any]:
        if callable(getattr(config_oper, "all", None)):
            return dict(config_oper.all() or {})
        return dict(config_oper.get() or {})

    @staticmethod
    def _agentopsassistant_raw_config_rows(config_oper: Any) -> List[str]:
        """列出仍存在的目标配置键。

        V3 的 Oper 不再持有会话，宿主 Model 也需要显式 Session，因此这里改用
        SystemConfigOper 的公开快照读取，不再直连 Model。
        """
        target = f"plugin.{AGENTOPSASSISTANT_PURGE_TARGET}".lower()
        snapshot = LegacyAgentOpsAssistantPurgeMixin._agentopsassistant_system_config_snapshot(config_oper)
        return [str(key) for key in snapshot if str(key).lower() == target]

    @staticmethod
    def _agentopsassistant_system_key_value(config_oper: Any, key: Any) -> Any:
        """读取单个系统配置键的当前值。"""
        return config_oper.get(key)

    @classmethod
    def _agentopsassistant_raw_system_values(cls, config_oper: Any, key: Any) -> List[Any]:
        return [cls._agentopsassistant_system_key_value(config_oper, key)]

    @classmethod
    def _scrub_agentopsassistant_system_key(cls, config_oper: Any, key: Any) -> bool:
        """清除单个系统配置键中的目标引用，并回读确认已经清空。"""
        try:
            cached = cls._agentopsassistant_system_key_value(config_oper, key)
            cleaned = cls._scrub_agentopsassistant_references(cached)
            if cleaned is _PURGE_REMOVE:
                cleaned = [] if isinstance(cached, (list, tuple)) else {} if isinstance(cached, dict) else None
            if cleaned != cached:
                config_oper.set(key, cleaned)
            return not any(
                cls._agentopsassistant_reference_count(value)
                for value in cls._agentopsassistant_raw_system_values(config_oper, key)
            )
        except Exception as err:
            logger.warning(f"Signal 清理系统配置键 {key} 失败：{err}")
            return False

    @staticmethod
    def _delete_agentopsassistant_raw_config(config_oper: Any, key: str) -> bool:
        """删除目标配置键，并回读确认。"""
        try:
            if callable(getattr(config_oper, "delete", None)):
                config_oper.delete(key)
            else:
                config_oper.set(key, None)
        except Exception as err:
            logger.warning(f"Signal 删除配置键 {key} 失败：{err}")
            return False
        return key not in LegacyAgentOpsAssistantPurgeMixin._agentopsassistant_raw_config_rows(config_oper)

    @staticmethod
    def _agentopsassistant_plugin_data_rows(data_oper: Any) -> List[Any]:
        """读取目标插件的自有数据，全部经 PluginDataOper 公开方法。"""
        try:
            rows = data_oper.get_data_all(AGENTOPSASSISTANT_PURGE_TARGET) or []
            return list(rows) if isinstance(rows, (list, tuple, set)) else [rows]
        except Exception:
            try:
                value = data_oper.get_data(AGENTOPSASSISTANT_PURGE_TARGET)
            except Exception as err:
                logger.warning(f"Signal 读取 PluginData 失败：{err}")
                return []
            return [value] if value else []

    @staticmethod
    def _agentopsassistant_user_config_entries(user_oper: Any) -> List[Dict[str, Any]]:
        def is_dashboard_key(value: Any) -> bool:
            key = str(value or "")
            return key in {"Dashboard", "DashboardOrder", "DashboardGridLayout"} or key.startswith("DashboardGridLayout.")

        entries: List[Dict[str, Any]] = []
        try:
            all_users = user_oper.get(None) or {}
        except TypeError:
            all_users = user_oper.get("") or {}
        except Exception as err:
            logger.warning(f"Signal 读取用户配置失败：{err}")
            all_users = {}
        if isinstance(all_users, dict):
            for username, values in all_users.items():
                if not isinstance(values, dict):
                    continue
                for key, value in values.items():
                    if is_dashboard_key(key):
                        entries.append({"username": str(username), "key": str(key), "value": value})
        return entries

    def _build_agentopsassistant_purge_status(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "target": AGENTOPSASSISTANT_PURGE_TARGET,
            "read_only": True,
            "no_backup": True,
            "irreversible": True,
            "clean": False,
            "success": True,
            "installed_list": [],
            "plugin_folders": 0,
            "config_keys": [],
            "plugin_data_rows": 0,
            "dashboard_refs": [],
            "api_clean": False,
            "scheduler_clean": False,
            "runtime_clean": False,
            "candidates": [],
            "residue_count": 0,
            "errors": [],
        }
        target = AGENTOPSASSISTANT_PURGE_TARGET
        try:
            from app.sdk.plugins import PluginManager
            from app.db.oper.plugindata import PluginDataOper
            from app.db.oper.systemconfig import SystemConfigOper
            from app.db.oper.userconfig import UserConfigOper
            from app.scheduler import Scheduler
            from app.schemas.types import SystemConfigKey

            config_oper = SystemConfigOper()
            installed_key = getattr(SystemConfigKey, "UserInstalledPlugins", "UserInstalledPlugins")
            folder_key = getattr(SystemConfigKey, "PluginFolders", "PluginFolders")
            installed_values = self._agentopsassistant_raw_system_values(config_oper, installed_key)
            result["installed_list"] = [
                str(item)
                for value in installed_values
                for item in (value if isinstance(value, (list, tuple, set)) else [value])
                if str(item).lower() == target.lower()
            ]
            result["plugin_folders"] = sum(
                self._agentopsassistant_reference_count(value)
                for value in self._agentopsassistant_raw_system_values(config_oper, folder_key)
            )
            result["config_keys"] = self._agentopsassistant_raw_config_rows(config_oper)
            result["plugin_data_rows"] = len(self._agentopsassistant_plugin_data_rows(PluginDataOper()))
            for entry in self._agentopsassistant_user_config_entries(UserConfigOper()):
                count = self._agentopsassistant_reference_count(entry.get("value"))
                if count:
                    result["dashboard_refs"].append({
                        "username": entry.get("username"),
                        "key": entry.get("key"),
                        "count": count,
                    })
            result["api_clean"] = self._verify_plugin_api_removed(target)
            result["scheduler_clean"] = self._verify_plugin_scheduler_removed(Scheduler(), target)
            plugin_manager = PluginManager()
            if hasattr(plugin_manager, "get_plugin_ids"):
                runtime_ids = [str(item) for item in (plugin_manager.get_plugin_ids() or [])]
            else:
                runtime_ids = [str(getattr(item, "id", "")) for item in (plugin_manager.get_local_plugins() or [])]
            result["runtime_clean"] = not any(item.lower() == target.lower() for item in runtime_ids)
        except Exception as err:
            result["success"] = False
            result["errors"].append(f"MoviePilot 状态读取失败：{err}")
        try:
            result["candidates"] = self._agentopsassistant_purge_candidates()
        except Exception as err:
            result["success"] = False
            result["errors"].append(f"残留路径读取失败：{err}")
        result["residue_count"] = (
            len(result["installed_list"])
            + int(result["plugin_folders"])
            + len(result["config_keys"])
            + int(result["plugin_data_rows"])
            + sum(int(item.get("count") or 0) for item in result["dashboard_refs"])
            + int(not result["api_clean"])
            + int(not result["scheduler_clean"])
            + int(not result["runtime_clean"])
            + len(result["candidates"])
        )
        result["clean"] = bool(result["success"] and result["residue_count"] == 0)
        return result

    def _purge_agentopsassistant_system_state(self, result: Dict[str, Any]) -> None:
        target = AGENTOPSASSISTANT_PURGE_TARGET
        from app.db.oper.plugindata import PluginDataOper
        from app.db.oper.systemconfig import SystemConfigOper
        from app.db.oper.userconfig import UserConfigOper
        from app.schemas.types import SystemConfigKey

        config_oper = SystemConfigOper()
        installed_key = getattr(SystemConfigKey, "UserInstalledPlugins", "UserInstalledPlugins")
        installed_refs = sum(
            self._agentopsassistant_reference_count(value)
            for value in self._agentopsassistant_raw_system_values(config_oper, installed_key)
        )
        if not self._scrub_agentopsassistant_system_key(config_oper, installed_key):
            result["errors"].append("UserInstalledPlugins 清理后仍有残留")
        elif installed_refs:
            result["actions"].append("已移出 UserInstalledPlugins")
        if not self._scrub_agentopsassistant_system_key(config_oper, getattr(SystemConfigKey, "PluginFolders", "PluginFolders")):
            result["errors"].append("PluginFolders 清理后仍有残留")
        else:
            result["actions"].append("已清理 PluginFolders")

        for key in self._agentopsassistant_raw_config_rows(config_oper):
            deleted = self._delete_agentopsassistant_raw_config(config_oper, key)
            if deleted:
                result["actions"].append(f"已删除原始配置键 {key}")
            else:
                result["errors"].append(f"原始配置键删除失败：{key}")
        remaining_config = self._agentopsassistant_raw_config_rows(config_oper)
        if remaining_config:
            result["errors"].append(f"配置键仍有残留：{'、'.join(remaining_config)}")

        data_oper = PluginDataOper()
        rows = self._agentopsassistant_plugin_data_rows(data_oper)
        if rows:
            try:
                if not callable(getattr(data_oper, "del_data", None)):
                    raise RuntimeError("MoviePilot 未提供 PluginData 删除接口")
                data_oper.del_data(target)
                data_oper.del_data(target.lower())
                result["actions"].append("已删除 PluginData")
            except Exception as err:
                result["errors"].append(f"PluginData 删除失败：{err}")
        if self._agentopsassistant_plugin_data_rows(data_oper):
            result["errors"].append("PluginData 清理后仍有残留")

        user_oper = UserConfigOper()
        for entry in self._agentopsassistant_user_config_entries(user_oper):
            value = entry.get("value")
            if not self._agentopsassistant_reference_count(value):
                continue
            cleaned = self._scrub_agentopsassistant_references(value)
            if cleaned is _PURGE_REMOVE:
                cleaned = [] if isinstance(value, (list, tuple)) else {} if isinstance(value, dict) else ""
            try:
                user_oper.set(entry.get("username"), entry.get("key"), cleaned)
                result["actions"].append(f"已清理仪表盘引用 {entry.get('username')}:{entry.get('key')}")
            except Exception as err:
                result["errors"].append(f"仪表盘引用清理失败 {entry.get('username')}:{entry.get('key')}：{err}")

    def _run_agentopsassistant_purge(self) -> Dict[str, Any]:
        before = self._build_agentopsassistant_purge_status()
        result: Dict[str, Any] = {
            "target": AGENTOPSASSISTANT_PURGE_TARGET,
            "no_backup": True,
            "irreversible": True,
            "success": False,
            "already_clean": bool(before.get("clean")),
            "before": before,
            "uninstall": {},
            "actions": [],
            "deleted": [],
            "remaining": [],
            "errors": [],
            "warnings": [],
            "verification": {},
        }
        if before.get("clean"):
            result["success"] = True
            result["verification"] = before
            return result

        try:
            ok, message, cleaned = self._uninstall_moviepilot_plugin(
                AGENTOPSASSISTANT_PURGE_TARGET,
                clear_config=True,
                clear_data=True,
            )
            result["uninstall"] = {"success": ok, "message": message, "verification": cleaned}
            if not ok:
                result["warnings"].append(f"MoviePilot 通用卸载未完全确认：{message}")
        except Exception as err:
            result["warnings"].append(f"MoviePilot 通用卸载异常，继续执行固定专杀：{err}")

        try:
            self._purge_agentopsassistant_system_state(result)
        except Exception as err:
            result["errors"].append(f"MoviePilot 原始状态清理失败：{err}")

        for item in self._agentopsassistant_purge_candidates():
            path = Path(item.get("path") or "")
            if not self._agentopsassistant_purge_path_allowed(path):
                result["errors"].append(f"拒绝越界路径：{path}")
                continue
            try:
                self._delete_plugin_path_with_retry(path)
                result["deleted"].append(item)
            except Exception as err:
                result["errors"].append(f"{path}: {err}")
        self._remove_empty_isolation_root()

        verification = self._build_agentopsassistant_purge_status()
        result["verification"] = verification
        result["remaining"] = list(verification.get("candidates") or [])
        if not verification.get("clean"):
            result["errors"].append(
                f"终态复核未通过，仍检测到 {verification.get('residue_count', 0)} 项 AgentOpsAssistant 残留。"
            )
        result["success"] = not result["errors"] and bool(verification.get("clean"))
        return result
