"""Plugin uninstall helpers extracted from the main plugin class.

Handles plugin uninstall, path candidates, text formatting and
installed-plugin id enumeration. Local imports
of PluginManager / Scheduler / SystemConfigOper / SystemConfigKey are
kept inside _uninstall_moviepilot_plugin as in the original.
"""

import re
from importlib import import_module
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..domain import site_helpers


class PluginUninstallMixin:
    """Mixin bundling plugin uninstall helpers."""

    def _normalize_plugin_id(self, value: Any) -> str:
        raw = str(value or "").strip()
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]{0,79}", raw):
            return ""
        return raw

    @staticmethod
    def _installed_plugin_canonical_ids() -> List[str]:
        """Return exact installed IDs, preferring the host runtime casing."""
        try:
            from app.core.plugin import PluginManager
            from app.db.systemconfig_oper import SystemConfigOper
            from app.schemas.types import SystemConfigKey
        except Exception:
            return []

        values: List[str] = []
        try:
            manager = PluginManager()
            if hasattr(manager, "get_local_plugins"):
                for plugin in manager.get_local_plugins() or []:
                    plugin_id = str(getattr(plugin, "id", "") or "").strip()
                    if plugin_id and getattr(plugin, "installed", True) is not False:
                        values.append(plugin_id)
            elif hasattr(manager, "get_plugin_ids"):
                values.extend(str(item).strip() for item in (manager.get_plugin_ids() or []))
        except Exception:
            pass
        try:
            installed = SystemConfigOper().get(SystemConfigKey.UserInstalledPlugins) or []
            values.extend(str(item).strip() for item in installed)
        except Exception:
            pass

        canonical: List[str] = []
        seen = set()
        for plugin_id in values:
            key = plugin_id.lower()
            if plugin_id and key not in seen:
                seen.add(key)
                canonical.append(plugin_id)
        return canonical

    def _uninstall_moviepilot_plugin(self, plugin_id: str, clear_config: Optional[bool] = None, clear_data: Optional[bool] = None) -> Tuple[bool, str, Dict[str, Any]]:
        cleaned = {
            "config": False,
            "data": False,
            "config_missing": False,
            "data_missing": False,
            "installed_list": False,
            "plugin_folders": False,
            "api": False,
            "scheduler": False,
            "runtime": False,
        }
        try:
            from app.core.plugin import PluginManager
            from app.db.systemconfig_oper import SystemConfigOper
            from app.scheduler import Scheduler
            from app.schemas.types import SystemConfigKey
        except Exception as err:
            message = f"当前 MoviePilot 环境缺少插件卸载依赖：{err}"
            return False, message, {
                **cleaned,
                "status": "failed",
                "persistent_errors": [message],
                "host_residuals": [],
            }

        messages: List[str] = []
        persistent_errors: List[str] = []
        host_residuals: List[str] = []
        config_oper = SystemConfigOper()
        plugin_manager = PluginManager()
        installed_plugins = config_oper.get(SystemConfigKey.UserInstalledPlugins) or []
        runtime_plugin_ids: List[str] = []
        try:
            if hasattr(plugin_manager, "get_plugin_ids"):
                runtime_plugin_ids = [str(item) for item in (plugin_manager.get_plugin_ids() or [])]
            elif hasattr(plugin_manager, "get_local_plugins"):
                runtime_plugin_ids = [str(getattr(item, "id", "")) for item in (plugin_manager.get_local_plugins() or [])]
        except Exception:
            runtime_plugin_ids = []
        canonical_id = next(
            (item for item in runtime_plugin_ids if item.lower() == plugin_id.lower()),
            next((str(item) for item in installed_plugins if str(item).lower() == plugin_id.lower()), plugin_id),
        )
        try:
            remaining = [p for p in installed_plugins if str(p).lower() != canonical_id.lower()]
            if len(remaining) != len(installed_plugins):
                config_oper.set(SystemConfigKey.UserInstalledPlugins, remaining)
                messages.append("已移出已安装列表")
            else:
                messages.append("未在已安装列表中")
            if any(str(item).lower() == canonical_id.lower() for item in (config_oper.get(SystemConfigKey.UserInstalledPlugins) or [])):
                persistent_errors.append("仍存在于已安装列表")
            else:
                cleaned["installed_list"] = True
        except Exception as err:
            persistent_errors.append(f"清理已安装列表失败：{err}")

        api_removed = self._remove_plugin_api_safely(canonical_id)
        if not api_removed:
            host_residuals.append("插件 API 路由注销失败")
        elif not self._verify_plugin_api_removed(canonical_id):
            host_residuals.append("插件 API 路由注销后仍有残留或无法确认")
        else:
            cleaned["api"] = True

        scheduler = Scheduler()
        scheduler_removed = self._remove_plugin_job_safely(scheduler, canonical_id)
        if not scheduler_removed:
            host_residuals.append("插件调度任务注销失败")
        elif not self._verify_plugin_scheduler_removed(scheduler, canonical_id):
            host_residuals.append("插件调度任务注销后仍有残留或无法确认")
        else:
            cleaned["scheduler"] = True

        folders_removed = self._remove_plugin_from_folders_safely(config_oper, SystemConfigKey, canonical_id)
        if not folders_removed:
            persistent_errors.append("插件文件夹注册项注销失败")
        else:
            cleaned["plugin_folders"] = True

        clear_config_enabled = self._plugin_uninstall_clear_config if clear_config is None else clear_config
        clear_data_enabled = self._plugin_uninstall_clear_data if clear_data is None else clear_data
        config_key_template = getattr(plugin_manager, "_config_key", "plugin.%s")
        config_key = config_key_template % canonical_id
        config_known = hasattr(config_oper, "get")
        config_before = None
        if clear_config_enabled and config_known:
            try:
                config_before = config_oper.get(config_key) or {}
            except Exception as err:
                persistent_errors.append(f"读取配置状态失败：{err}")
                config_known = False
        if clear_config_enabled:
            try:
                try:
                    deleted = plugin_manager.delete_plugin_config(canonical_id, force=True)
                except TypeError:
                    deleted = plugin_manager.delete_plugin_config(canonical_id)
                if deleted:
                    cleaned["config"] = True
                    messages.append("配置已清理")
                elif config_known and not config_before:
                    cleaned["config_missing"] = True
                    messages.append("配置本来不存在")
                else:
                    persistent_errors.append("配置删除失败或无法确认")
                if config_known and (config_oper.get(config_key) or {}):
                    persistent_errors.append("配置删除后仍有残留")
            except Exception as err:
                persistent_errors.append(f"配置清理失败：{err}")
        data_known = False
        data_before = None
        data_oper = None
        if clear_data_enabled:
            try:
                from app.db.plugindata_oper import PluginDataOper
                data_oper = PluginDataOper()
                data_before = data_oper.get_data(canonical_id)
                data_known = True
            except Exception:
                data_known = False
        if clear_data_enabled:
            try:
                try:
                    deleted = plugin_manager.delete_plugin_data(canonical_id, force=True)
                except TypeError:
                    deleted = plugin_manager.delete_plugin_data(canonical_id)
                data_after = None
                data_after_known = data_oper is not None
                if data_oper is not None:
                    try:
                        data_after = data_oper.get_data(canonical_id)
                    except Exception as err:
                        data_after_known = False
                        persistent_errors.append(f"数据删除后无法确认：{err}")
                if data_after_known and data_after:
                    persistent_errors.append("数据删除后仍有残留")
                if deleted is False and data_known and not data_before:
                    cleaned["data_missing"] = True
                    messages.append("数据本来不存在")
                elif deleted is False:
                    persistent_errors.append("数据删除失败或无法确认")
                elif deleted is True and data_known and not data_before:
                    cleaned["data_missing"] = True
                    messages.append("数据本来不存在")
                elif deleted is True:
                    cleaned["data"] = True
                    messages.append("数据已清理")
                elif data_after_known and not data_after:
                    if data_known and not data_before:
                        cleaned["data_missing"] = True
                        messages.append("数据本来不存在")
                    else:
                        cleaned["data"] = True
                        messages.append("数据已清理")
                else:
                    persistent_errors.append("数据删除失败或无法确认")
            except Exception as err:
                persistent_errors.append(f"数据清理失败：{err}")
        try:
            removed = plugin_manager.remove_plugin(canonical_id)
            if removed is False:
                host_residuals.append("运行实例移除返回失败")
            else:
                messages.append("运行实例已移除")
            if hasattr(plugin_manager, "get_plugin_state") and plugin_manager.get_plugin_state(canonical_id):
                host_residuals.append("运行实例复核仍处于运行状态")
            local_plugins = plugin_manager.get_local_plugins() if hasattr(plugin_manager, "get_local_plugins") else None
            if local_plugins is None:
                host_residuals.append("无法确认运行实例是否已移除")
            elif any(str(getattr(item, "id", "")).lower() == canonical_id.lower() for item in local_plugins):
                host_residuals.append("运行实例复核仍存在")
            else:
                cleaned["runtime"] = True
        except Exception as err:
            host_residuals.append(f"移除运行实例失败：{err}")

        if persistent_errors:
            status = "failed"
            success = False
            message = "；".join(persistent_errors + host_residuals)
        elif host_residuals:
            status = "restart_required"
            success = True
            message = "持久化清理已完成；MoviePilot 内存仍有残留，请重启后复核：" + "；".join(host_residuals)
        else:
            status = "completed"
            success = True
            message = "；".join(messages)
        return success, message, {
            **cleaned,
            "status": status,
            "persistent_errors": persistent_errors,
            "host_residuals": host_residuals,
        }

    @staticmethod
    def _verify_plugin_api_removed(plugin_id: str) -> bool:
        """Verify known MoviePilot API registries when the host exposes them.

        Current MoviePilot versions register plugin routes directly on the
        FastAPI application. Older versions may additionally expose a plugin
        registry. Any matching route or registry entry is a residual failure.
        """
        try:
            module = import_module("app.api.endpoints.plugin")
        except Exception:
            return False
        registries = [
            getattr(module, name, None)
            for name in ("PLUGIN_APIS", "plugin_apis", "_plugin_apis", "PLUGIN_API")
        ]
        target = str(plugin_id or "").strip().lower()

        application = getattr(module, "app", None)
        routes = getattr(application, "routes", None)
        if routes is not None:
            route_prefixes = []
            for name in ("PLUGIN_PREFIX", "PLUGIN_V2_PREFIX"):
                prefix = str(getattr(module, name, "") or "").strip().rstrip("/")
                if prefix:
                    route_prefixes.append(f"{prefix}/{target}/".lower())
            for route in routes:
                route_path = str(getattr(route, "path", "") or "").strip().lower()
                if any(route_path.startswith(prefix) for prefix in route_prefixes):
                    return False

        def contains(value: Any) -> bool:
            if isinstance(value, dict):
                return any(contains(key) or contains(item) for key, item in value.items())
            if isinstance(value, (list, tuple, set)):
                return any(contains(item) for item in value)
            if hasattr(value, "id") or hasattr(value, "plugin_id"):
                return contains(getattr(value, "id", "")) or contains(getattr(value, "plugin_id", ""))
            text = str(value or "").strip().lower()
            return text == target or text.startswith(f"{target}.") or text.startswith(f"{target}:")

        for registry in registries:
            if registry is None:
                continue
            if contains(registry):
                return False
        return True

    @staticmethod
    def _verify_plugin_scheduler_removed(scheduler: Any, plugin_id: str) -> bool:
        """Verify the host scheduler no longer exposes a job for this plugin."""
        list_jobs = getattr(scheduler, "list", None) or getattr(scheduler, "get_jobs", None)
        if not callable(list_jobs):
            return False
        target = str(plugin_id or "").strip().lower()
        try:
            jobs = list_jobs() or []
        except Exception:
            return False
        for job in jobs:
            values = [getattr(job, key, "") for key in ("plugin_id", "plugin", "pid", "id", "name")]
            if any(
                (value := str(item or "").strip().lower())
                and (
                    value == target
                    or any(value.startswith(f"{target}{separator}") for separator in (".", ":", "-", "_", "|"))
                )
                for item in values
            ):
                return False
        return True

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

    @staticmethod
    def _format_plugin_uninstall_text(data: Dict[str, Any]) -> str:
        title = "🧩 插件卸载预览" if data.get("dry_run") else "🧩 插件卸载结果"
        lines = [title, f"⦁ 插件ID：{data.get('plugin_id') or '未填写'}", f"⦁ 说明：{data.get('note')}"]
        if data.get("blocked"):
            lines.append(f"⦁ 阻止原因：{data.get('blocked')}")
            return "\n".join(lines)
        actions = ["卸载插件"]
        if data.get("clear_config"):
            actions.append("清配置")
        if data.get("clear_data"):
            actions.append("清数据")
        actions.append("删运行与本地源码" if data.get("delete_source") else "保留运行与本地源码")
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
            status = str(data.get("status") or "failed")
            if status == "completed":
                lines.append("⦁ 终态：已完成，宿主注册与文件复核无残留")
            elif status == "restart_required":
                lines.append("⦁ 终态：持久化清理已完成，请重启 MoviePilot 后复核内存残留")
            else:
                lines.append("⦁ 终态：失败，仍有选定持久化内容或文件残留")
            if data.get("cleaned_config") or data.get("cleaned_data"):
                lines.append(f"⦁ 配置/数据：配置 {len(data.get('cleaned_config') or [])} 个 ｜ 数据 {len(data.get('cleaned_data') or [])} 个")
            lines.append(f"⦁ 已删除：{len(data.get('deleted') or [])} 项")
        if data.get("errors"):
            lines.append("异常：")
            lines.extend([f"⦁ {e}" for e in data.get("errors", [])[:5]])
        if data.get("host_residuals"):
            lines.append("需重启复核：")
            lines.extend([f"⦁ {e}" for e in data.get("host_residuals", [])[:5]])
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
