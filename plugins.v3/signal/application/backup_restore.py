"""Unified online restore state machine for Signal backup archives."""

from __future__ import annotations

from copy import deepcopy
import json
import shutil
import tempfile
import time
import uuid
from pathlib import Path, PurePosixPath
from typing import Any, Dict, List, Mapping, Optional, Tuple

from .backup_archive import BackupArchiveError, BackupArchiveService
from .backup_models import (
    ARCHIVE_COMPONENT_MOVIEPILOT,
    ARCHIVE_COMPONENT_PLUGINS,
    BACKUP_OPERATION_LOCK,
    BackupOperation,
    BackupSettings,
    PLUGIN_REGISTRY_KEYS,
    RestoreSelection,
    SIGNAL_ARCHIVE_EXCLUDED_DIR_NAMES,
    SOURCE_LOCAL,
    SOURCE_TEMP_WEBDAV,
    SOURCE_UPLOAD,
    SOURCE_WEBDAV,
    decode_json_value,
    unique_strings,
)
from ..infrastructure.backup_targets import BackupTargetError, BackupTargetService


class BackupRestoreError(RuntimeError):
    pass


class BackupRestoreService:
    """Resolve, validate and apply a selected archive.

    The browser never submits a path or a component-specific restore boolean.
    ``inspect`` creates a short-lived server-side selection record; ``execute``
    accepts only its stable backup id and a bounded component selection, then
    resolves and verifies the source again before any write occurs.
    """

    SELECTION_TTL_SECONDS = 30 * 60

    def __init__(self, owner: Any):
        self.owner = owner
        self.settings = BackupSettings.from_config(self._current_config())
        self.targets = BackupTargetService(self.settings)
        self.archive_service = BackupArchiveService(owner)
        if not hasattr(owner, "_backup_selection_cache"):
            owner._backup_selection_cache = {}
        if not hasattr(owner, "_backup_operation_current"):
            owner._backup_operation_current = None
        if not hasattr(owner, "_backup_operation_recent"):
            owner._backup_operation_recent = []

    def _current_config(self) -> Mapping[str, Any]:
        value = getattr(self.owner, "_backup_config", None)
        if isinstance(value, Mapping):
            return value
        return {
            "backup_enabled": getattr(self.owner, "_backup_enabled", False),
            "backup_database_enabled": getattr(self.owner, "_backup_database_enabled", False),
            "backup_cron": getattr(self.owner, "_backup_cron", "0 4 * * 1"),
            "backup_path": getattr(self.owner, "_backup_path", "/config/plugins/Signal/Backup"),
            "backup_keep_count": getattr(self.owner, "_backup_keep_count", 5),
            "backup_webdav_enabled": getattr(self.owner, "_backup_webdav_enabled", False),
            "backup_webdav_hostname": getattr(self.owner, "_backup_webdav_hostname", ""),
            "backup_webdav_login": getattr(self.owner, "_backup_webdav_login", ""),
            "backup_webdav_password": getattr(self.owner, "_backup_webdav_password", ""),
            "backup_webdav_max_count": getattr(self.owner, "_backup_webdav_max_count", 5),
            "backup_webdav_digest_auth": getattr(self.owner, "_backup_webdav_digest_auth", False),
            "backup_webdav_disable_check": getattr(self.owner, "_backup_webdav_disable_check", False),
        }

    @property
    def cache_dir(self) -> Path:
        path = Path(self.settings.local_path).resolve(strict=False) / ".restore-cache"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _prune_selection_cache(self) -> None:
        now = time.time()
        cache = self.owner._backup_selection_cache
        expired = []
        for backup_id, value in cache.items():
            try:
                inspected_at = float(value.get("inspected_at") or 0) if isinstance(value, Mapping) else 0
            except (TypeError, ValueError):
                inspected_at = 0
            if now - inspected_at > self.SELECTION_TTL_SECONDS:
                expired.append(backup_id)
        for backup_id in expired:
            cache.pop(backup_id, None)

    def list_archives(self, source: str, temporary_credentials: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        if source not in {SOURCE_LOCAL, SOURCE_WEBDAV, SOURCE_TEMP_WEBDAV, SOURCE_UPLOAD}:
            raise BackupRestoreError("未知的备份来源。")
        items = []
        for item in self.targets.list_source(source, temporary_credentials):
            descriptor = dict(item)
            # Listing deliberately does not download remote archives.  The
            # inspect step validates the selected bytes and returns backup_id.
            descriptor.setdefault("backup_id", "")
            descriptor.setdefault("fingerprint", "")
            descriptor.setdefault("valid", None)
            items.append(descriptor)
        return {"source": source, "items": items, "temporary_credentials": False}

    def inspect_archive(
        self,
        source: str,
        archive_name: str,
        temporary_credentials: Optional[Mapping[str, Any]] = None,
    ) -> Dict[str, Any]:
        self._prune_selection_cache()
        try:
            archive_path = self.targets.resolve_source(
                source,
                archive_name,
                cache_dir=self.cache_dir,
                temporary_credentials=temporary_credentials,
            )
            descriptor = self.archive_service.inspect_archive(
                archive_path,
                source=source,
                source_ref=str(archive_name),
            )
            manifest = self.archive_service.read_manifest(archive_path)
        except (BackupTargetError, BackupArchiveError) as err:
            raise BackupRestoreError(str(err)) from err
        self.owner._backup_selection_cache[descriptor.backup_id] = {
            "source": source,
            "archive_name": descriptor.name,
            "archive_path": str(archive_path),
            "fingerprint": descriptor.fingerprint,
            "temporary_credentials": dict(temporary_credentials or {}),
            "inspected_at": time.time(),
        }
        database = (manifest.get("offline") or {}).get("database") or {}
        offline_components = [
            label for label, key in (("app.env", "app_env"), ("cookies", "cookies"))
            if bool(((manifest.get("offline") or {}).get(key) or {}).get("present"))
        ]
        if bool(database.get("present", bool(database.get("path")))):
            offline_components.append("database")
        return {
            "descriptor": descriptor.to_dict(),
            "manifest": manifest,
            # Keep the picker independent from the internal manifest shape.
            # The descriptor is already validated from the same archive bytes,
            # so this is a stable, explicit list for both include and exclude.
            "plugin_options": [
                {"value": plugin_id, "label": plugin_id}
                for plugin_id in descriptor.plugins
            ],
            "sensitive_warning": "归档未加密，包含敏感离线恢复材料。",
            "online_components": [ARCHIVE_COMPONENT_MOVIEPILOT, ARCHIVE_COMPONENT_PLUGINS],
            "offline_components": offline_components,
            "database_included": descriptor.database_included,
            "complete_archive": descriptor.database_included,
        }

    def import_archive(self, content_base64: str, filename: str) -> Dict[str, Any]:
        path: Optional[Path] = None
        try:
            path = self.targets.import_base64(content_base64, filename)
            descriptor = self.archive_service.inspect_archive(path, source=SOURCE_UPLOAD, source_ref=path.name)
        except (BackupTargetError, BackupArchiveError) as err:
            try:
                if path is not None:
                    path.unlink(missing_ok=True)
            except Exception:
                pass
            raise BackupRestoreError(str(err)) from err
        return self.inspect_archive(SOURCE_UPLOAD, descriptor.name)

    def download_archive(self, source: str, archive_name: str, temporary_credentials: Optional[Mapping[str, Any]] = None) -> Dict[str, Any]:
        try:
            path = self.targets.resolve_source(
                source,
                archive_name,
                cache_dir=self.cache_dir,
                temporary_credentials=temporary_credentials,
            )
            self.archive_service.inspect_archive(path, source=source, source_ref=archive_name)
            return self.targets.download_base64(path)
        except (BackupTargetError, BackupArchiveError) as err:
            raise BackupRestoreError(str(err)) from err

    def _resolve_selected_archive(self, backup_id: str) -> Tuple[Path, Dict[str, Any]]:
        self._prune_selection_cache()
        cached = self.owner._backup_selection_cache.get(backup_id)
        if not cached:
            raise BackupRestoreError("归档选择已过期，请重新选择并检查备份包。")
        source = str(cached.get("source") or "")
        archive_name = str(cached.get("archive_name") or "")
        path = self.targets.resolve_source(
            source,
            archive_name,
            cache_dir=self.cache_dir,
            temporary_credentials=cached.get("temporary_credentials") or None,
        )
        descriptor = self.archive_service.inspect_archive(path, source=source, source_ref=archive_name)
        if descriptor.backup_id != backup_id or descriptor.fingerprint != cached.get("fingerprint"):
            raise BackupRestoreError("归档在检查后发生变化，已阻止写入。")
        return path, {"descriptor": descriptor.to_dict(), "cache": cached}

    @staticmethod
    def _selected_plugin_items(manifest: Mapping[str, Any], selection: RestoreSelection):
        items = (((manifest.get("components") or {}).get(ARCHIVE_COMPONENT_PLUGINS) or {}).get("items") or [])
        records = [item for item in items if isinstance(item, Mapping) and str(item.get("id") or "").strip()]
        available = [str(item["id"]).strip() for item in records]
        selected = set(selection.select_plugins(available))
        return [item for item in records if str(item.get("id")) in selected]

    @staticmethod
    def _material_path(root: Path, relative: str, *, kind: str) -> Path:
        raw = str(relative or "").strip().replace("\\", "/")
        if not raw:
            raise BackupRestoreError(f"{kind}未声明归档路径。")
        parsed = PurePosixPath(raw)
        if parsed.is_absolute() or ".." in parsed.parts or (parsed.parts and ":" in parsed.parts[0]):
            raise BackupRestoreError(f"{kind}路径越界。")
        root_resolved = Path(root).resolve(strict=False)
        path = root_resolved.joinpath(*parsed.parts).resolve(strict=False)
        if path != root_resolved and root_resolved not in path.parents:
            raise BackupRestoreError(f"{kind}路径越界。")
        return path

    @classmethod
    def _read_json(cls, root: Path, relative: str, default: Any, *, required: bool = False, kind: str = "JSON 材料") -> Any:
        if not relative:
            if required:
                raise BackupRestoreError(f"{kind}未声明归档路径。")
            return default
        path = cls._material_path(root, relative, kind=kind)
        if not path.is_file():
            if required:
                raise BackupRestoreError(f"{kind}不存在。")
            return default
        try:
            return decode_json_value(json.loads(path.read_text(encoding="utf-8")))
        except BackupRestoreError:
            raise
        except Exception as err:
            raise BackupRestoreError(f"{kind}格式无效：{err}") from err

    @staticmethod
    def _validated_plugin_id(value: Any) -> str:
        plugin_id = str(value or "").strip()
        safe = "".join(character for character in plugin_id if character.isalnum() or character in {"_", "-"})[:80]
        if not plugin_id or safe != plugin_id:
            raise BackupRestoreError("归档包含无效插件 ID。")
        return plugin_id

    @staticmethod
    def _require_method(target: Any, method: str, capability: str) -> None:
        if not callable(getattr(target, method, None)):
            raise BackupRestoreError(f"当前 MoviePilot 不支持{capability}。")

    def _preflight_host_capabilities(self, selection: RestoreSelection, prepared_plugins: List[Dict[str, Any]]) -> None:
        if (
            ARCHIVE_COMPONENT_MOVIEPILOT in selection.components
            or ARCHIVE_COMPONENT_PLUGINS in selection.components
            or any(item.get("config_present") for item in prepared_plugins)
        ):
            from app.db.oper.systemconfig import SystemConfigOper

            oper = SystemConfigOper()
            self._require_method(oper, "all", "配置快照")
            self._require_method(oper, "get", "配置读取")
            self._require_method(oper, "set", "配置写回")
        if any(item.get("config_present") for item in prepared_plugins):
            from app.sdk.plugins import PluginManager

            self._require_method(PluginManager(), "delete_plugin_config", "插件配置补偿删除")
        if prepared_plugins:
            from app.db.oper.plugindata import PluginDataOper

            oper = PluginDataOper()
            self._require_method(oper, "get_data_all", "插件数据读取")
        if any(item.get("data_present") for item in prepared_plugins):
            from app.db.oper.plugindata import PluginDataOper

            oper = PluginDataOper()
            self._require_method(oper, "del_data", "插件数据清理")
            self._require_method(oper, "save", "插件数据写回")
        if any(item.get("files_present") for item in prepared_plugins):
            from app.sdk.config import settings

            config_value = str(getattr(settings, "CONFIG_PATH", "") or "").strip()
            config_path = Path(config_value) if config_value else None
            if config_path is None or (config_path.exists() and not config_path.is_dir()):
                raise BackupRestoreError("当前 MoviePilot 插件文件目录不可用。")

    def _prepare_selection(self, root: Path, manifest: Mapping[str, Any], selection: RestoreSelection) -> Dict[str, Any]:
        components = manifest.get("components") or {}
        if not isinstance(components, Mapping):
            raise BackupRestoreError("归档组件清单格式无效。")
        available_components = {
            key for key, value in components.items()
            if isinstance(value, Mapping) and value.get("present") is not False
        }
        if any(component not in available_components for component in selection.components):
            raise BackupRestoreError("选择的恢复范围不在归档能力范围内。")

        moviepilot_values: Optional[Mapping[str, Any]] = None
        if ARCHIVE_COMPONENT_MOVIEPILOT in selection.components:
            metadata = components.get(ARCHIVE_COMPONENT_MOVIEPILOT) or {}
            if not isinstance(metadata, Mapping):
                raise BackupRestoreError("MoviePilot 配置清单格式无效。")
            values = self._read_json(
                root,
                str(metadata.get("path") or ""),
                {},
                required=True,
                kind="MoviePilot 配置材料",
            )
            if not isinstance(values, Mapping):
                raise BackupRestoreError("MoviePilot 配置材料格式无效。")
            if any(str(key).lower().startswith("plugin.") for key in values):
                raise BackupRestoreError("MoviePilot 配置材料包含越界的插件配置键。")
            registry_keys = {key.lower() for key in PLUGIN_REGISTRY_KEYS}
            if any(str(key).lower() in registry_keys for key in values):
                raise BackupRestoreError("MoviePilot 配置材料包含越界的插件注册表键。")
            moviepilot_values = values

        prepared_plugins: List[Dict[str, Any]] = []
        prepared_registry: Optional[Dict[str, Any]] = None
        selected_plugin_ids: List[str] = []
        if ARCHIVE_COMPONENT_PLUGINS in selection.components:
            plugin_component = components.get(ARCHIVE_COMPONENT_PLUGINS) or {}
            if not isinstance(plugin_component, Mapping):
                raise BackupRestoreError("插件清单格式无效。")
            registry = plugin_component.get("registry")
            if not isinstance(registry, Mapping) or set(registry) != {"installed", "folders"}:
                raise BackupRestoreError("插件注册表清单格式无效。")
            installed_registry = registry.get("installed")
            folder_registry = registry.get("folders")
            if not isinstance(installed_registry, list):
                raise BackupRestoreError("UserInstalledPlugins 归档格式无效。")
            normalized_installed: List[str] = []
            for value in installed_registry:
                plugin_id = self._validated_plugin_id(value)
                if plugin_id in normalized_installed:
                    raise BackupRestoreError(f"UserInstalledPlugins 归档包含重复 ID：{plugin_id}")
                normalized_installed.append(plugin_id)
            if folder_registry is not None and not isinstance(folder_registry, (Mapping, list)):
                raise BackupRestoreError("PluginFolders 归档格式无效。")
            prepared_registry = {
                "installed": normalized_installed,
                "folders": deepcopy(folder_registry),
            }
            raw_items = plugin_component.get("items") or []
            if not isinstance(raw_items, list):
                raise BackupRestoreError("插件清单格式无效。")
            records: List[Mapping[str, Any]] = []
            seen_ids = set()
            for raw_item in raw_items:
                if not isinstance(raw_item, Mapping):
                    raise BackupRestoreError("插件清单包含无效条目。")
                plugin_id = self._validated_plugin_id(raw_item.get("id"))
                if plugin_id in seen_ids:
                    raise BackupRestoreError(f"插件清单包含重复 ID：{plugin_id}")
                seen_ids.add(plugin_id)
                records.append(raw_item)
            if selection.plugin_scope == "include":
                missing = sorted(set(selection.plugin_ids) - seen_ids)
                if missing:
                    raise BackupRestoreError(f"所选插件不在归档中：{'、'.join(missing)}")
            available_ids = [self._validated_plugin_id(item.get("id")) for item in records]
            selected_plugin_ids = selection.select_plugins(available_ids)
            selected_ids = set(selected_plugin_ids)
            for item in records:
                plugin_id = self._validated_plugin_id(item.get("id"))
                if plugin_id not in selected_ids:
                    continue
                config_meta = item.get("config") or {}
                data_meta = item.get("data") or {}
                files_meta = item.get("files") or {}
                if not all(isinstance(meta, Mapping) for meta in (config_meta, data_meta, files_meta)):
                    raise BackupRestoreError(f"{plugin_id} 的插件材料清单格式无效。")
                config_present = bool(config_meta.get("present"))
                data_present = bool(data_meta.get("present"))
                files_present = bool(files_meta.get("present"))
                config = None
                records_data: List[Mapping[str, Any]] = []
                files_path: Optional[Path] = None
                if config_present:
                    config = self._read_json(
                        root,
                        str(config_meta.get("path") or ""),
                        None,
                        required=True,
                        kind=f"{plugin_id} 配置材料",
                    )
                    if not isinstance(config, Mapping):
                        raise BackupRestoreError(f"{plugin_id} 配置材料格式无效。")
                if data_present:
                    data_value = self._read_json(
                        root,
                        str(data_meta.get("path") or ""),
                        [],
                        required=True,
                        kind=f"{plugin_id} 数据材料",
                    )
                    if not isinstance(data_value, list):
                        raise BackupRestoreError(f"{plugin_id} 数据材料格式无效。")
                    data_keys = set()
                    for record in data_value:
                        if not isinstance(record, Mapping) or not str(record.get("key") or "").strip():
                            raise BackupRestoreError(f"{plugin_id} 数据材料包含无效记录。")
                        key = str(record.get("key"))
                        if key in data_keys:
                            raise BackupRestoreError(f"{plugin_id} 数据材料包含重复键：{key}")
                        data_keys.add(key)
                        records_data.append(record)
                if files_present:
                    files_path = self._material_path(
                        root,
                        str(files_meta.get("path") or ""),
                        kind=f"{plugin_id} 文件材料",
                    )
                    if not files_path.is_dir():
                        raise BackupRestoreError(f"{plugin_id} 文件材料不存在。")
                prepared_plugins.append({
                    "plugin_id": plugin_id,
                    "config_present": config_present,
                    "config": config,
                    "data_present": data_present,
                    "records": records_data,
                    "files_present": files_present,
                    "files_path": files_path,
                    "files_count": int(files_meta.get("count") or 0),
                })

        self._preflight_host_capabilities(selection, prepared_plugins)
        return {
            "moviepilot": moviepilot_values,
            "plugins": prepared_plugins,
            "plugin_registry": prepared_registry,
            "selected_plugin_ids": selected_plugin_ids,
        }

    def _restore_moviepilot_settings(self, values: Mapping[str, Any], operation: BackupOperation) -> None:
        from app.db.oper.systemconfig import SystemConfigOper
        errors = []
        written = 0
        oper = SystemConfigOper()
        for key, value in values.items():
            try:
                oper.set(str(key), value)
                written += 1
            except Exception as err:
                errors.append(f"{key}: {err}")
        status = "success" if not errors else "partial"
        operation.components.append({"component": ARCHIVE_COMPONENT_MOVIEPILOT, "status": status, "written": written, "errors": errors[:8]})
        operation.errors.extend(errors[:8])

    def _plugin_config_key(self, plugin_id: str) -> str:
        try:
            from app.sdk.plugins import PluginManager

            template = str(getattr(PluginManager(), "_config_key", "plugin.%s") or "plugin.%s")
        except Exception:
            template = "plugin.%s"
        return template % plugin_id

    @staticmethod
    def _merge_installed_registry(current: Any, archived: List[str], selected_ids: List[str]) -> List[Any]:
        if current is None:
            current = []
        if not isinstance(current, (list, tuple, set)):
            raise BackupRestoreError("当前 UserInstalledPlugins 注册表格式无效。")
        selected = {plugin_id.lower() for plugin_id in selected_ids}
        result = [
            deepcopy(value)
            for value in current
            if str(value or "").strip().lower() not in selected
        ]
        existing = {str(value or "").strip().lower() for value in result}
        for plugin_id in archived:
            lowered = plugin_id.lower()
            if lowered in selected and lowered not in existing:
                result.append(plugin_id)
                existing.add(lowered)
        return result

    @classmethod
    def _merge_folder_registry(cls, current: Any, archived: Any, selected_ids: List[str]) -> Any:
        selected = {plugin_id.lower() for plugin_id in selected_ids}

        def strip_selected(value: Any) -> Any:
            if isinstance(value, Mapping):
                return {key: strip_selected(item) for key, item in value.items()}
            if isinstance(value, list):
                return [
                    strip_selected(item)
                    for item in value
                    if not isinstance(item, str) or item.strip().lower() not in selected
                ]
            return deepcopy(value)

        def add_archived(base: Any, source: Any) -> Any:
            if isinstance(source, Mapping):
                result = dict(base) if isinstance(base, Mapping) else {}
                for key, item in source.items():
                    if isinstance(item, (Mapping, list)):
                        result[key] = add_archived(result.get(key), item)
                    elif key not in result:
                        result[key] = deepcopy(item)
                return result
            if isinstance(source, list):
                result = list(base) if isinstance(base, list) else []
                existing = {
                    item.strip().lower()
                    for item in result
                    if isinstance(item, str)
                }
                for item in source:
                    if not isinstance(item, str):
                        continue
                    lowered = item.strip().lower()
                    if lowered in selected and lowered not in existing:
                        result.append(item)
                        existing.add(lowered)
                return result
            return base

        return add_archived(strip_selected(current), archived)

    @staticmethod
    def _system_config_snapshot(oper: Any, key: Any) -> Dict[str, Any]:
        values = oper.all()
        if not isinstance(values, Mapping):
            raise BackupRestoreError("当前 MoviePilot 配置快照格式无效。")
        matching_key = next((item for item in values if str(item) == str(key)), None)
        exists = matching_key is not None
        return {
            "key": key,
            "exists": exists,
            "value": deepcopy(values.get(matching_key)) if exists else None,
        }

    @classmethod
    def _verify_system_config_snapshot(cls, oper: Any, snapshot: Mapping[str, Any]) -> None:
        current = cls._system_config_snapshot(oper, snapshot.get("key"))
        if bool(current.get("exists")) != bool(snapshot.get("exists")) or current.get("value") != snapshot.get("value"):
            raise BackupRestoreError(f"配置复核不一致：{snapshot.get('key')}")

    def _restore_plugin_config_snapshot(self, plugin_id: str, snapshot: Mapping[str, Any]) -> None:
        from app.sdk.plugins import PluginManager
        from app.db.oper.systemconfig import SystemConfigOper

        oper = SystemConfigOper()
        if snapshot.get("exists"):
            oper.set(snapshot.get("key"), deepcopy(snapshot.get("value")))
        else:
            manager = PluginManager()
            try:
                deleted = manager.delete_plugin_config(plugin_id, force=True)
            except TypeError:
                deleted = manager.delete_plugin_config(plugin_id)
            if deleted is False and self._system_config_snapshot(oper, snapshot.get("key")).get("exists"):
                raise BackupRestoreError("旧配置不存在状态无法恢复。")
        self._verify_system_config_snapshot(oper, snapshot)

    @staticmethod
    def _plugin_data_records(oper: Any, plugin_id: str) -> List[Dict[str, Any]]:
        records: List[Dict[str, Any]] = []
        for row in oper.get_data_all(plugin_id) or []:
            if isinstance(row, Mapping):
                key = str(row.get("key") or "").strip()
                value = row.get("value")
            else:
                key = str(getattr(row, "key", "") or "").strip()
                value = getattr(row, "value", None)
            if not key:
                raise BackupRestoreError(f"{plugin_id} 当前 PluginData 包含无效记录。")
            records.append({"key": key, "value": deepcopy(value)})
        return records

    @classmethod
    def _replace_plugin_data_records(cls, oper: Any, plugin_id: str, records: List[Mapping[str, Any]]) -> int:
        current = cls._plugin_data_records(oper, plugin_id)
        for key in unique_strings([item["key"] for item in current]):
            oper.del_data(plugin_id, key)
        expected = [
            {"key": str(item["key"]), "value": deepcopy(item.get("value"))}
            for item in records
        ]
        for record in expected:
            oper.save(plugin_id, record["key"], deepcopy(record["value"]))
        if cls._plugin_data_records(oper, plugin_id) != expected:
            raise BackupRestoreError(f"{plugin_id} PluginData 写回复核不一致。")
        return len(expected)

    @staticmethod
    def _registry_keys() -> Tuple[Any, Any]:
        from app.schemas.types import SystemConfigKey

        return (
            getattr(SystemConfigKey, "UserInstalledPlugins", PLUGIN_REGISTRY_KEYS[0]),
            getattr(SystemConfigKey, "PluginFolders", PLUGIN_REGISTRY_KEYS[1]),
        )

    def _plugin_registry_snapshot(self, oper: Any) -> Dict[str, Any]:
        installed_key, folders_key = self._registry_keys()
        return {
            "installed": self._system_config_snapshot(oper, installed_key),
            "folders": self._system_config_snapshot(oper, folders_key),
        }

    def _apply_plugin_registry(
        self,
        oper: Any,
        registry: Mapping[str, Any],
        plugin_id: str,
        snapshot: Mapping[str, Any],
    ) -> int:
        installed_snapshot = snapshot["installed"]
        folders_snapshot = snapshot["folders"]
        merged_installed = self._merge_installed_registry(
            installed_snapshot.get("value"),
            list(registry.get("installed") or []),
            [plugin_id],
        )
        merged_folders = self._merge_folder_registry(
            folders_snapshot.get("value"),
            registry.get("folders"),
            [plugin_id],
        )
        writes = 0
        if not installed_snapshot.get("exists") or installed_snapshot.get("value") != merged_installed:
            oper.set(installed_snapshot.get("key"), merged_installed)
            writes += 1
        if (
            folders_snapshot.get("exists")
            or registry.get("folders") is not None
        ) and (not folders_snapshot.get("exists") or folders_snapshot.get("value") != merged_folders):
            oper.set(folders_snapshot.get("key"), merged_folders)
            writes += 1
        expected_installed = {**installed_snapshot, "exists": True, "value": merged_installed}
        self._verify_system_config_snapshot(oper, expected_installed)
        if folders_snapshot.get("exists") or registry.get("folders") is not None:
            expected_folders = {**folders_snapshot, "exists": True, "value": merged_folders}
            self._verify_system_config_snapshot(oper, expected_folders)
        return writes

    @classmethod
    def _restore_registry_snapshot(cls, oper: Any, snapshot: Mapping[str, Any]) -> None:
        for name in ("installed", "folders"):
            item = snapshot[name]
            if not item.get("exists"):
                delete = getattr(oper, "delete", None)
                if not callable(delete):
                    raise BackupRestoreError(f"{item.get('key')} 原不存在但宿主不支持删除补偿。")
                delete(item.get("key"))
            else:
                oper.set(item.get("key"), deepcopy(item.get("value")))
            cls._verify_system_config_snapshot(oper, item)

    @staticmethod
    def _commit_plugin_file_tree(transaction: Mapping[str, Any]) -> str:
        rollback = Path(transaction.get("rollback"))
        if not rollback.exists():
            return ""
        try:
            shutil.rmtree(rollback)
            return ""
        except Exception as err:
            return f"旧插件文件暂存目录清理失败：{err}"

    @staticmethod
    def _rollback_plugin_file_tree(transaction: Mapping[str, Any]) -> None:
        target = Path(transaction.get("target"))
        rollback = Path(transaction.get("rollback"))
        staging = Path(transaction.get("staging"))
        had_target = bool(transaction.get("had_target"))
        protected = list(transaction.get("moved_protected") or [])
        if had_target and not rollback.exists():
            raise BackupRestoreError("旧插件文件回滚点丢失。")
        if rollback.exists() and target.is_dir():
            for name in protected:
                source_path = target / name
                destination = rollback / name
                if source_path.exists():
                    if destination.exists():
                        raise BackupRestoreError(f"保留目录回滚冲突：{name}")
                    source_path.replace(destination)
        if target.exists() or target.is_symlink():
            if target.is_dir() and not target.is_symlink():
                shutil.rmtree(target)
            else:
                target.unlink()
        if rollback.exists():
            rollback.replace(target)
        if staging.exists():
            shutil.rmtree(staging)
        if had_target != target.exists():
            raise BackupRestoreError("插件文件存在性回滚复核失败。")

    @staticmethod
    def _replace_plugin_file_tree(source: Path, target: Path, plugin_id: str, *, retain_rollback: bool = False) -> Any:
        """Atomically replace managed plugin files and optionally retain rollback."""
        source = Path(source)
        target = Path(target)
        if not source.is_dir() or source.is_symlink():
            raise BackupRestoreError("插件文件材料不可用。")
        if target.is_symlink():
            raise BackupRestoreError("插件文件目标不能是符号链接。")
        if target.exists() and not target.is_dir():
            raise BackupRestoreError("插件文件目标不是目录。")
        target.parent.mkdir(parents=True, exist_ok=True)
        token = uuid.uuid4().hex
        staging = target.parent / f".{target.name}.signal-restore-{token}.new"
        rollback = target.parent / f".{target.name}.signal-restore-{token}.old"
        had_target = target.exists()
        shutil.copytree(source, staging)
        protected_names = SIGNAL_ARCHIVE_EXCLUDED_DIR_NAMES if plugin_id.lower() == "signal" else frozenset()
        moved_protected: List[str] = []

        def move_protected_back(destination_root: Path) -> None:
            for name in reversed(moved_protected):
                source_path = staging / name
                if source_path.exists():
                    source_path.replace(destination_root / name)

        try:
            if target.is_dir() and protected_names:
                for child in list(target.iterdir()):
                    if child.name.lower() not in protected_names:
                        continue
                    destination = staging / child.name
                    if destination.exists():
                        raise BackupRestoreError(f"Signal 归档越界包含保留目录：{child.name}")
                    child.replace(destination)
                    moved_protected.append(child.name)
            if target.exists():
                target.replace(rollback)
            try:
                staging.replace(target)
            except Exception:
                if rollback.exists() and not target.exists():
                    rollback.replace(target)
                if target.is_dir():
                    move_protected_back(target)
                raise
        except Exception:
            if target.is_dir() and staging.exists():
                move_protected_back(target)
            shutil.rmtree(staging, ignore_errors=True)
            raise

        transaction = {
            "target": target,
            "rollback": rollback,
            "staging": staging,
            "had_target": had_target,
            "moved_protected": list(moved_protected),
        }
        if retain_rollback:
            return transaction
        return BackupRestoreService._commit_plugin_file_tree(transaction)

    def _restore_plugin_item(
        self,
        item: Mapping[str, Any],
        registry: Mapping[str, Any],
        operation: BackupOperation,
    ) -> str:
        from app.sdk.config import settings
        from app.db.oper.plugindata import PluginDataOper
        from app.db.oper.systemconfig import SystemConfigOper

        plugin_id = str(item.get("plugin_id") or "").strip()
        config_oper = SystemConfigOper()
        data_oper = PluginDataOper()
        config_key = self._plugin_config_key(plugin_id)
        target_root = Path(str(getattr(settings, "CONFIG_PATH", "/config") or "/config")) / "plugins" / plugin_id
        try:
            snapshot = {
                "config": self._system_config_snapshot(config_oper, config_key),
                "data": self._plugin_data_records(data_oper, plugin_id),
                "registry": self._plugin_registry_snapshot(config_oper),
                "files_exist": target_root.exists(),
            }
        except Exception as err:
            message = f"{plugin_id}: 冻结旧状态失败：{err}"
            operation.errors.append(message)
            operation.components.append({
                "component": "plugin",
                "plugin_id": plugin_id,
                "status": "failed",
                "writes": 0,
                "rollback_complete": True,
                "errors": [str(err)],
            })
            return "failed"

        writes = 0
        registry_writes = 0
        touched = {"config": False, "data": False, "files": False, "registry": False}
        file_transaction: Optional[Mapping[str, Any]] = None
        try:
            if item.get("config_present"):
                touched["config"] = True
                SystemConfigOper().set(self._plugin_config_key(plugin_id), item.get("config"))
                expected = {"key": config_key, "exists": True, "value": deepcopy(item.get("config"))}
                self._verify_system_config_snapshot(config_oper, expected)
                writes += 1
            if item.get("data_present"):
                touched["data"] = True
                records = [
                    {"key": str(record["key"]), "value": decode_json_value(record.get("value"))}
                    for record in (item.get("records") or [])
                ]
                writes += self._replace_plugin_data_records(data_oper, plugin_id, records)
            if item.get("files_present"):
                touched["files"] = True
                source = item.get("files_path")
                if isinstance(source, Path) and source.is_dir():
                    file_transaction = self._replace_plugin_file_tree(
                        source,
                        target_root,
                        plugin_id,
                        retain_rollback=True,
                    )
                    writes += int(item.get("files_count") or 0)
                else:
                    raise BackupRestoreError("插件文件材料不可用。")
            touched["registry"] = True
            registry_writes = self._apply_plugin_registry(config_oper, registry, plugin_id, snapshot["registry"])
            if file_transaction:
                cleanup_warning = self._commit_plugin_file_tree(file_transaction)
                if cleanup_warning:
                    operation.warnings.append(f"{plugin_id}: {cleanup_warning}")
        except Exception as err:
            rollback_errors: List[str] = []
            unrecovered: List[str] = []

            def compensate(component: str, callback) -> None:
                try:
                    callback()
                except Exception as rollback_err:
                    unrecovered.append(component)
                    rollback_errors.append(f"{component}: {rollback_err}")

            if touched["registry"]:
                compensate("registry", lambda: self._restore_registry_snapshot(config_oper, snapshot["registry"]))
            if file_transaction is not None:
                compensate("files", lambda: self._rollback_plugin_file_tree(file_transaction))
            if touched["data"]:
                compensate("data", lambda: self._replace_plugin_data_records(data_oper, plugin_id, snapshot["data"]))
            if touched["config"]:
                compensate("config", lambda: self._restore_plugin_config_snapshot(plugin_id, snapshot["config"]))

            status = "rollback_failed" if rollback_errors else "failed"
            operation.errors.append(f"{plugin_id}: 写回失败：{err}")
            operation.errors.extend(f"{plugin_id}: 补偿失败：{item}" for item in rollback_errors)
            if rollback_errors:
                operation.rollback_complete = False
                operation.manual_recovery_required = True
                operation.unrecovered_components = unique_strings([
                    *operation.unrecovered_components,
                    *unrecovered,
                ])
            operation.components.append({
                "component": "plugin",
                "plugin_id": plugin_id,
                "status": status,
                "writes": writes,
                "registry_writes": registry_writes,
                "rollback_complete": not rollback_errors,
                "unrecovered_components": unrecovered,
                "errors": [str(err), *rollback_errors][:8],
            })
            return status

        operation.components.append({
            "component": "plugin",
            "plugin_id": plugin_id,
            "status": "success",
            "writes": writes,
            "registry_writes": registry_writes,
            "rollback_complete": True,
            "errors": [],
        })
        return "success"

    def _apply_prepared(self, prepared: Mapping[str, Any], selection: RestoreSelection, operation: BackupOperation) -> None:
        if ARCHIVE_COMPONENT_MOVIEPILOT in selection.components:
            values = prepared.get("moviepilot")
            if not isinstance(values, Mapping):
                raise BackupRestoreError("MoviePilot 配置预检状态无效。")
            self._restore_moviepilot_settings(values, operation)
        if ARCHIVE_COMPONENT_PLUGINS in selection.components:
            items = list(prepared.get("plugins") or [])
            if not items:
                operation.components.append({"component": ARCHIVE_COMPONENT_PLUGINS, "status": "absent", "message": "归档没有可恢复插件，视为正常。"})
            registry = prepared.get("plugin_registry")
            if not isinstance(registry, Mapping):
                raise BackupRestoreError("插件注册表预检状态无效。")
            for item in items:
                status = self._restore_plugin_item(item, registry, operation)
                if status == "rollback_failed":
                    break

    def _save_operation(self, operation: BackupOperation) -> None:
        try:
            saver = getattr(self.owner, "save_data", None)
            if callable(saver):
                saver("backup_operation_recent", operation.to_dict())
        except Exception:
            pass

    def operation_status(self) -> Dict[str, Any]:
        current = self.owner._backup_operation_current
        recent = list(self.owner._backup_operation_recent or [])
        return {
            "current": current.to_dict() if isinstance(current, BackupOperation) else current,
            "recent": [
                item.to_dict() if isinstance(item, BackupOperation) else item
                for item in recent[-10:]
            ],
        }

    def execute(self, payload: Optional[Mapping[str, Any]]) -> Dict[str, Any]:
        try:
            selection = RestoreSelection.from_payload(payload)
        except ValueError as err:
            return {
                "success": False,
                "partial": False,
                "status": "invalid",
                "message": str(err),
                "errors": [str(err)],
                "components": [],
                "rollback_complete": True,
                "manual_recovery_required": False,
                "unrecovered_components": [],
                "emergency_archive": "",
            }
        if not BACKUP_OPERATION_LOCK.acquire(blocking=False):
            return {
                "success": False,
                "partial": False,
                "status": "conflict",
                "conflict": True,
                "errors": ["已有恢复操作正在执行，请先查询当前操作状态。"],
                "rollback_complete": True,
                "manual_recovery_required": False,
                "unrecovered_components": [],
                "emergency_archive": "",
            }
        operation = BackupOperation(operation_id=str(uuid.uuid4()), kind="backup_restore", backup_id=selection.backup_id)
        self.owner._backup_operation_current = operation
        self._save_operation(operation)
        try:
            archive_path, context = self._resolve_selected_archive(selection.backup_id)
            descriptor = context["descriptor"]
            operation.backup_id = descriptor["backup_id"]
            with tempfile.TemporaryDirectory(prefix="signal_restore_verified_") as temp:
                extraction = Path(temp)
                verified = self.archive_service.extract_verified(archive_path, extraction)
                prepared = self._prepare_selection(extraction, verified["manifest"], selection)
                emergency_root = Path(self.settings.local_path).resolve(strict=False) / ".emergency"
                emergency_root.mkdir(parents=True, exist_ok=True)
                emergency = self.archive_service.create_archive(
                    emergency_root,
                    trigger="restore_emergency",
                    include_database=self.settings.database_enabled,
                )
                operation.emergency_archive = str(Path(emergency["archive_path"]).resolve(strict=False))
                operation.warnings.append(f"恢复前应急备份：{Path(emergency['archive_path']).name}")
                self._apply_prepared(prepared, selection, operation)
            if operation.manual_recovery_required:
                operation.finish(
                    status="rollback_failed",
                    message="恢复失败且自动补偿未完成；已停止后续插件，请使用应急归档人工恢复。",
                )
            else:
                failed = [item for item in operation.components if item.get("status") in {"failed", "partial"}]
                successful = [item for item in operation.components if item.get("status") == "success"]
                if failed:
                    status = "partial" if successful or any(item.get("status") == "partial" for item in failed) else "failed"
                    operation.finish(status=status, message="恢复未全部成功；失败插件已自动恢复旧状态。")
                else:
                    operation.finish(status="success", message="恢复完成，已按所选范围写回在线配置与插件状态。")
        except Exception as err:
            operation.errors.append(str(err))
            operation.finish(status="failed", message=str(err))
        finally:
            self.owner._backup_selection_cache.pop(selection.backup_id, None)
            self.owner._backup_operation_current = None
            self.owner._backup_operation_recent.append(operation.to_dict())
            self.owner._backup_operation_recent = self.owner._backup_operation_recent[-10:]
            self._save_operation(operation)
            BACKUP_OPERATION_LOCK.release()
        result = operation.to_dict()
        return result
