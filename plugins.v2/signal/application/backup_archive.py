"""Creation and validation of the ``signal-backup/v2`` archive contract."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import tempfile
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

from .backup_models import (
    ARCHIVE_COMPONENT_MOVIEPILOT,
    ARCHIVE_COMPONENT_OFFLINE,
    ARCHIVE_COMPONENT_PLUGINS,
    ARCHIVE_COMPONENTS,
    ARCHIVE_FORMAT,
    ArchiveDescriptor,
    PLUGIN_REGISTRY_KEYS,
    SIGNAL_ARCHIVE_EXCLUDED_DIR_NAMES,
    encode_json_value,
    utc_now,
)
from ..infrastructure.database_snapshot import create_active_database_snapshot


MAX_ARCHIVE_ENTRIES = 100_000
MAX_ARCHIVE_UNCOMPRESSED_BYTES = 50 * 1024 * 1024 * 1024


class BackupArchiveError(RuntimeError):
    pass


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(encode_json_value(value), ensure_ascii=False, indent=2), encoding="utf-8")


def _safe_plugin_id(value: Any) -> str:
    raw = str(value or "").strip()
    safe = "".join(character for character in raw if character.isalnum() or character in {"_", "-"})[:80]
    return safe


def _plugin_data_records(data_oper: Any, plugin_id: str) -> List[Dict[str, Any]]:
    rows: Any = []
    getter = getattr(data_oper, "get_data_all", None)
    if callable(getter):
        rows = getter(plugin_id) or []
    if not rows:
        getter = getattr(data_oper, "get_data", None)
        if callable(getter):
            rows = getter(plugin_id) or []
    if isinstance(rows, Mapping):
        return [{"key": str(key), "value": encode_json_value(value)} for key, value in rows.items()]
    if not isinstance(rows, (list, tuple, set)):
        rows = [rows] if rows else []
    records: List[Dict[str, Any]] = []
    for index, row in enumerate(rows):
        if isinstance(row, Mapping):
            key = row.get("key", index)
            value = row.get("value", row)
        else:
            key = getattr(row, "key", index)
            value = getattr(row, "value", row)
        records.append({"key": str(key), "value": encode_json_value(value)})
    return records


def _copy_tree(
    source: Path,
    target: Path,
    *,
    signal_tree: bool = False,
    include_dist: bool = False,
) -> int:
    if not source.is_dir():
        return 0
    ignored_names = {
        "__pycache__", ".git", "node_modules", ".tmp", "artifacts",
    }
    if not include_dist:
        ignored_names.add("dist")
    copied = 0
    source_resolved = source.resolve(strict=False)
    for current_root, directories, files in os.walk(source):
        current = Path(current_root)
        relative = current.relative_to(source)
        directories[:] = [
            name for name in directories
            if name.lower() not in ignored_names
            and (not signal_tree or name.lower() not in SIGNAL_ARCHIVE_EXCLUDED_DIR_NAMES)
        ]
        for filename in files:
            if filename.endswith((".pyc", ".pyo")):
                continue
            source_file = current / filename
            try:
                if source_file.is_symlink():
                    continue
                resolved = source_file.resolve(strict=True)
                if source_resolved != resolved and source_resolved not in resolved.parents:
                    continue
            except OSError:
                continue
            target_file = target / relative / filename
            target_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_file, target_file)
            copied += 1
    return copied


def _installed_plugin_ids(plugin_manager: Any, config_oper: Any) -> Tuple[List[str], Dict[str, Any]]:
    ids: List[str] = []
    try:
        from app.schemas.types import SystemConfigKey
        installed_key = getattr(SystemConfigKey, "UserInstalledPlugins", PLUGIN_REGISTRY_KEYS[0])
        folders_key = getattr(SystemConfigKey, "PluginFolders", PLUGIN_REGISTRY_KEYS[1])
    except Exception as err:
        raise BackupArchiveError(f"无法加载插件注册表合同：{err}") from err
    try:
        installed = config_oper.get(installed_key)
        folders = config_oper.get(folders_key)
    except Exception as err:
        raise BackupArchiveError(f"读取插件注册表失败：{err}") from err
    if installed is None:
        installed = []
    if not isinstance(installed, (list, tuple, set)):
        raise BackupArchiveError("UserInstalledPlugins 插件注册表格式无效。")
    if folders is not None and not isinstance(folders, (Mapping, list)):
        raise BackupArchiveError("PluginFolders 插件注册表格式无效。")
    installed_values = list(installed)
    for value in installed_values:
        plugin_id = _safe_plugin_id(value)
        if plugin_id and plugin_id not in ids:
            ids.append(plugin_id)
    try:
        local_plugins = plugin_manager.get_local_plugins() or []
        for plugin in local_plugins:
            raw_id = plugin.get("id") if isinstance(plugin, Mapping) else getattr(plugin, "id", "")
            plugin_id = _safe_plugin_id(raw_id)
            if plugin_id and plugin_id not in ids:
                ids.append(plugin_id)
    except Exception as err:
        raise BackupArchiveError(f"枚举本地插件失败：{err}") from err
    return ids, {
        "installed": encode_json_value(installed_values),
        "folders": encode_json_value(folders) if folders is not None else None,
    }


def _restore_readme(manifest: Mapping[str, Any]) -> str:
    offline = manifest.get("offline") or {}
    database = (offline.get("database") or {})
    db_type = database.get("type") or "unknown"
    db_path = database.get("path") or "offline/"
    config_root = offline.get("config_root") or "MoviePilot CONFIG_PATH"
    app_env_target = (offline.get("app_env") or {}).get("target_path") or f"{config_root}/app.env"
    cookies_target = (offline.get("cookies") or {}).get("target_path") or f"{config_root}/cookies"
    database_source = database.get("source") or "活动数据库"
    lines = [
        "# Signal 离线恢复材料",
        "",
        "此归档包含未加密的敏感配置、Cookie 与数据库材料。请只存放在可信位置。",
        "HTTPS 只保护传输过程，不等于归档静态加密。",
        "",
        "## 恢复顺序",
        "",
        "1. 停止 MoviePilot，并额外备份当前配置和数据库。",
        "2. 核对备份时的容器来源、卷映射和目标路径。",
        "3. 仅在 MoviePilot 停止后覆盖 app.env、Cookies 或数据库材料。",
        "4. 启动 MoviePilot，检查数据库、插件、下载器、站点和通知配置。",
        "",
        f"备份时 MoviePilot 配置根目录：`{config_root}`。若使用 Docker，请先将该容器路径映射回宿主卷路径。",
        f"app.env 目标：`{app_env_target}`；Cookies 目标：`{cookies_target}`。",
        f"活动数据库类型：`{db_type}`；实际来源：`{database_source}`；归档材料：`{db_path}`。",
    ]
    if db_type == "postgresql":
        lines.extend([
            "",
            "PostgreSQL 没有可直接覆盖的配置目录数据库文件。请创建空目标库后执行：",
            "",
            "```sh",
            f"pg_restore --clean --if-exists --no-owner --dbname <目标数据库> {db_path}",
            "```",
        ])
    else:
        lines.extend([
            "",
            "SQLite 只能在 MoviePilot 停止后，用归档中的一致性快照覆盖实际 user.db；不要复制归档外的 WAL/SHM。",
        ])
    return "\n".join(lines) + "\n"


class BackupArchiveService:
    def __init__(self, owner: Any):
        self.owner = owner

    @staticmethod
    def _settings():
        from app.core.config import settings

        return settings

    def _collect_moviepilot_settings(self, work_dir: Path) -> Dict[str, Any]:
        from app.db.systemconfig_oper import SystemConfigOper

        all_settings = SystemConfigOper().all() or {}
        plugin_registry_keys = {key.lower() for key in PLUGIN_REGISTRY_KEYS}
        logical = {
            str(key): value for key, value in all_settings.items()
            if not str(key).lower().startswith("plugin.")
            and str(key).lower() not in plugin_registry_keys
        }
        target = work_dir / "moviepilot" / "settings.json"
        _write_json(target, logical)
        return {
            "present": True,
            "path": target.relative_to(work_dir).as_posix(),
            "keys": len(logical),
        }

    def _plugin_source_candidates(self, plugin_id: str) -> Iterable[Path]:
        settings = self._settings()
        root_value = str(getattr(settings, "ROOT_PATH", "") or "").strip()
        if root_value:
            root = Path(root_value)
            yield root / "app" / "plugins" / plugin_id.lower()
            yield root / "app" / "plugins" / plugin_id
        local_repo = str(getattr(self.owner, "_local_plugin_repo", "") or "").strip()
        if local_repo:
            yield Path(local_repo) / "plugins.v2" / plugin_id.lower()
            yield Path(local_repo) / "plugins.v2" / plugin_id

    def _collect_plugins(self, work_dir: Path) -> Tuple[List[Dict[str, Any]], List[str], Dict[str, Any]]:
        from app.core.plugin import PluginManager
        from app.db.plugindata_oper import PluginDataOper
        from app.db.systemconfig_oper import SystemConfigOper

        plugin_manager = PluginManager()
        config_oper = SystemConfigOper()
        data_oper = PluginDataOper()
        plugin_ids, registry = _installed_plugin_ids(plugin_manager, config_oper)
        records: List[Dict[str, Any]] = []
        config_template = str(getattr(plugin_manager, "_config_key", "plugin.%s") or "plugin.%s")
        config_path = Path(str(getattr(self._settings(), "CONFIG_PATH", "/config") or "/config"))

        for plugin_id in plugin_ids:
            plugin_root = work_dir / "plugins" / plugin_id
            plugin_root.mkdir(parents=True, exist_ok=True)
            config = config_oper.get(config_template % plugin_id)
            data = _plugin_data_records(data_oper, plugin_id)
            # An explicitly saved empty object is still plugin state and must
            # be distinguishable from a plugin that never had configuration.
            config_present = config is not None
            data_present = bool(data)
            if config_present:
                _write_json(plugin_root / "config.json", config)
            if data_present:
                _write_json(plugin_root / "data.json", data)

            runtime_path = config_path / "plugins" / plugin_id
            if not runtime_path.exists():
                lower_candidate = config_path / "plugins" / plugin_id.lower()
                runtime_path = lower_candidate if lower_candidate.exists() else runtime_path
            files_count = _copy_tree(
                runtime_path,
                plugin_root / "files",
                signal_tree=plugin_id.lower() == "signal",
            )
            source_count = 0
            for candidate in self._plugin_source_candidates(plugin_id):
                if candidate.is_dir():
                    source_count = _copy_tree(
                        candidate,
                        plugin_root / "source",
                        signal_tree=plugin_id.lower() == "signal",
                        include_dist=True,
                    )
                    if source_count:
                        break
            records.append({
                "id": plugin_id,
                "config": {"present": config_present, "path": f"plugins/{plugin_id}/config.json" if config_present else ""},
                "data": {"present": data_present, "path": f"plugins/{plugin_id}/data.json" if data_present else "", "records": len(data)},
                "files": {"present": files_count > 0, "path": f"plugins/{plugin_id}/files" if files_count else "", "count": files_count},
                "source": {"present": source_count > 0, "path": f"plugins/{plugin_id}/source" if source_count else "", "count": source_count, "online_restore": False},
            })
        return records, plugin_ids, registry

    def _collect_offline(self, work_dir: Path) -> Dict[str, Any]:
        settings = self._settings()
        config_path = Path(str(getattr(settings, "CONFIG_PATH", "/config") or "/config"))
        offline_root = work_dir / "offline"
        offline_root.mkdir(parents=True, exist_ok=True)
        app_env = config_path / "app.env"
        app_env_present = app_env.is_file()
        if app_env_present:
            shutil.copy2(app_env, offline_root / "app.env")
        cookies = config_path / "cookies"
        cookie_files = _copy_tree(cookies, offline_root / "cookies") if cookies.is_dir() else 0
        database = create_active_database_snapshot(offline_root)
        return {
            "config_root": str(config_path),
            "app_env": {
                "present": app_env_present,
                "path": "offline/app.env" if app_env_present else "",
                "target_path": str(app_env),
                "online_restore": False,
            },
            "cookies": {
                "present": cookie_files > 0,
                "path": "offline/cookies" if cookie_files else "",
                "target_path": str(cookies),
                "count": cookie_files,
                "online_restore": False,
            },
            "database": {**database, "path": f"offline/{database['path']}"},
        }

    @staticmethod
    def _payload_checksums(work_dir: Path) -> List[Tuple[str, str]]:
        checksums: List[Tuple[str, str]] = []
        for path in sorted(work_dir.rglob("*"), key=lambda item: item.relative_to(work_dir).as_posix()):
            if not path.is_file() or path.name in {"manifest.json", "checksums.sha256"}:
                continue
            checksums.append((path.relative_to(work_dir).as_posix(), sha256_file(path)))
        return checksums

    @staticmethod
    def _checksums_text(rows: Sequence[Tuple[str, str]]) -> str:
        return "".join(f"{digest}  {path}\n" for path, digest in rows)

    @staticmethod
    def _fingerprint(manifest_without_fingerprint: Mapping[str, Any], payload_rows: Sequence[Tuple[str, str]]) -> str:
        digest = hashlib.sha256()
        digest.update(canonical_json(manifest_without_fingerprint))
        digest.update(b"\n")
        digest.update(BackupArchiveService._checksums_text(payload_rows).encode("utf-8"))
        return digest.hexdigest()

    def create_archive(self, output_dir: Path, *, trigger: str) -> Dict[str, Any]:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        backup_id = str(uuid.uuid4())
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        archive_name = f"signal-backup-{stamp}-{backup_id[:8]}.zip"
        with tempfile.TemporaryDirectory(prefix="signal_backup_build_", dir=str(output_dir)) as temp:
            work_dir = Path(temp) / "archive"
            work_dir.mkdir(parents=True, exist_ok=True)
            moviepilot = self._collect_moviepilot_settings(work_dir)
            plugins, plugin_ids, plugin_registry = self._collect_plugins(work_dir)
            offline = self._collect_offline(work_dir)
            settings = self._settings()
            manifest: Dict[str, Any] = {
                "format": ARCHIVE_FORMAT,
                "backup_id": backup_id,
                "created_at": utc_now(),
                "trigger": str(trigger or "manual"),
                "moviepilot_version": str(
                    getattr(settings, "APP_VERSION", None)
                    or getattr(settings, "VERSION", None)
                    or "unknown"
                ),
                "signal_version": str(getattr(self.owner, "plugin_version", "unknown") or "unknown"),
                "components": {
                    ARCHIVE_COMPONENT_MOVIEPILOT: moviepilot,
                    ARCHIVE_COMPONENT_PLUGINS: {
                        "present": True,
                        "registry": plugin_registry,
                        "items": plugins,
                    },
                    ARCHIVE_COMPONENT_OFFLINE: {"present": True, "online_restore": False},
                },
                "offline": offline,
                "sensitive": True,
                "encryption": "none",
                "transport_security_is_not_archive_encryption": True,
            }
            (work_dir / "RESTORE.md").write_text(_restore_readme(manifest), encoding="utf-8")
            payload_rows = self._payload_checksums(work_dir)
            manifest["archive_fingerprint"] = self._fingerprint(manifest, payload_rows)
            _write_json(work_dir / "manifest.json", manifest)
            all_rows = payload_rows + [("manifest.json", sha256_file(work_dir / "manifest.json"))]
            (work_dir / "checksums.sha256").write_text(self._checksums_text(all_rows), encoding="utf-8", newline="\n")

            staged = output_dir / f".{archive_name}.staging"
            if staged.exists():
                staged.unlink()
            with zipfile.ZipFile(staged, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
                for path in sorted(work_dir.rglob("*"), key=lambda item: item.relative_to(work_dir).as_posix()):
                    if path.is_file():
                        archive.write(path, path.relative_to(work_dir).as_posix())
            final = output_dir / archive_name
            staged.replace(final)

        descriptor = self.inspect_archive(final, source="staging", source_ref=archive_name)
        return {
            "success": True,
            "archive_path": str(final),
            "zip_file": str(final),
            "descriptor": descriptor.to_dict(),
            "backup_id": backup_id,
            "fingerprint": descriptor.fingerprint,
            "plugins": plugin_ids,
            "warnings": ["归档未加密，包含敏感离线恢复材料。"],
            "errors": [],
        }

    @staticmethod
    def _zip_entries(archive: zipfile.ZipFile) -> List[zipfile.ZipInfo]:
        entries = archive.infolist()
        if len(entries) > MAX_ARCHIVE_ENTRIES:
            raise BackupArchiveError("归档文件数量超过安全上限。")
        total_size = 0
        names = set()
        for entry in entries:
            name = str(entry.filename or "").replace("\\", "/")
            parts = PurePosixPath(name).parts
            if not name or name.startswith("/") or ".." in parts or ":" in parts[0]:
                raise BackupArchiveError(f"归档包含非法路径：{entry.filename}")
            if name in names:
                raise BackupArchiveError(f"归档包含重复路径：{name}")
            names.add(name)
            total_size += int(entry.file_size or 0)
            if total_size > MAX_ARCHIVE_UNCOMPRESSED_BYTES:
                raise BackupArchiveError("归档解压后大小超过安全上限。")
            mode = (entry.external_attr >> 16) & 0o170000
            if mode == stat.S_IFLNK:
                raise BackupArchiveError(f"归档不允许符号链接：{name}")
        return entries

    @staticmethod
    def _parse_checksums(text: str) -> List[Tuple[str, str]]:
        rows: List[Tuple[str, str]] = []
        seen = set()
        for raw_line in text.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            try:
                digest, path = line.split("  ", 1)
            except ValueError as err:
                raise BackupArchiveError("checksums.sha256 格式无效。") from err
            path = path.strip().replace("\\", "/")
            if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest.lower()):
                raise BackupArchiveError(f"校验摘要无效：{path}")
            if path in seen:
                raise BackupArchiveError(f"校验清单包含重复路径：{path}")
            seen.add(path)
            rows.append((path, digest.lower()))
        return rows

    @staticmethod
    def _validate_manifest_contract(manifest: Any, names: set[str]) -> None:
        if not isinstance(manifest, Mapping):
            raise BackupArchiveError("归档 manifest 格式无效。")
        components = manifest.get("components")
        if not isinstance(components, Mapping) or set(components) != set(ARCHIVE_COMPONENTS):
            raise BackupArchiveError("归档组件清单不完整。")
        fingerprint = str(manifest.get("archive_fingerprint") or "").strip().lower()
        if len(fingerprint) != 64 or any(character not in "0123456789abcdef" for character in fingerprint):
            raise BackupArchiveError("归档指纹格式无效。")

        allowed_exact = {"manifest.json", "checksums.sha256", "RESTORE.md"}
        allowed_prefixes: List[str] = []

        moviepilot = components.get(ARCHIVE_COMPONENT_MOVIEPILOT)
        if not isinstance(moviepilot, Mapping):
            raise BackupArchiveError("MoviePilot 组件清单格式无效。")
        moviepilot_path = str(moviepilot.get("path") or "")
        if moviepilot.get("present") is not False:
            if moviepilot_path != "moviepilot/settings.json" or moviepilot_path not in names:
                raise BackupArchiveError("MoviePilot 配置材料清单无效。")
            allowed_exact.add(moviepilot_path)
        elif moviepilot_path:
            raise BackupArchiveError("MoviePilot 缺失组件不应声明材料路径。")

        plugins = components.get(ARCHIVE_COMPONENT_PLUGINS)
        if not isinstance(plugins, Mapping) or not isinstance(plugins.get("items"), list):
            raise BackupArchiveError("插件组件清单格式无效。")
        registry = plugins.get("registry")
        if not isinstance(registry, Mapping) or set(registry) != {"installed", "folders"}:
            raise BackupArchiveError("插件注册表清单格式无效。")
        installed_registry = registry.get("installed")
        folder_registry = registry.get("folders")
        if not isinstance(installed_registry, list):
            raise BackupArchiveError("UserInstalledPlugins 归档格式无效。")
        installed_ids = []
        for value in installed_registry:
            plugin_id = _safe_plugin_id(value)
            if not plugin_id or plugin_id != str(value or "").strip():
                raise BackupArchiveError("UserInstalledPlugins 归档包含无效插件 ID。")
            if plugin_id in installed_ids:
                raise BackupArchiveError(f"UserInstalledPlugins 归档包含重复 ID：{plugin_id}")
            installed_ids.append(plugin_id)
        if folder_registry is not None and not isinstance(folder_registry, (Mapping, list)):
            raise BackupArchiveError("PluginFolders 归档格式无效。")
        plugin_ids = set()
        for item in plugins.get("items") or []:
            if not isinstance(item, Mapping):
                raise BackupArchiveError("插件清单包含无效条目。")
            plugin_id = _safe_plugin_id(item.get("id"))
            if not plugin_id or plugin_id != str(item.get("id") or "").strip():
                raise BackupArchiveError("插件清单包含无效插件 ID。")
            if plugin_id in plugin_ids:
                raise BackupArchiveError(f"插件清单包含重复 ID：{plugin_id}")
            plugin_ids.add(plugin_id)
            expected = {
                "config": f"plugins/{plugin_id}/config.json",
                "data": f"plugins/{plugin_id}/data.json",
                "files": f"plugins/{plugin_id}/files",
                "source": f"plugins/{plugin_id}/source",
            }
            for key, expected_path in expected.items():
                metadata = item.get(key)
                if not isinstance(metadata, Mapping):
                    raise BackupArchiveError(f"{plugin_id} 的 {key} 清单格式无效。")
                present = bool(metadata.get("present"))
                declared_path = str(metadata.get("path") or "")
                if not present:
                    if declared_path:
                        raise BackupArchiveError(f"{plugin_id} 的缺失 {key} 不应声明材料路径。")
                    continue
                if declared_path != expected_path:
                    raise BackupArchiveError(f"{plugin_id} 的 {key} 材料路径无效。")
                if key in {"config", "data"}:
                    if declared_path not in names:
                        raise BackupArchiveError(f"{plugin_id} 的 {key} 材料不存在。")
                    allowed_exact.add(declared_path)
                else:
                    prefix = f"{declared_path}/"
                    if not any(name.startswith(prefix) for name in names):
                        raise BackupArchiveError(f"{plugin_id} 的 {key} 材料不存在。")
                    allowed_prefixes.append(prefix)

        offline_component = components.get(ARCHIVE_COMPONENT_OFFLINE)
        offline = manifest.get("offline")
        if not isinstance(offline_component, Mapping) or not isinstance(offline, Mapping):
            raise BackupArchiveError("离线恢复清单格式无效。")
        if offline_component.get("online_restore") is not False:
            raise BackupArchiveError("离线材料不得声明在线恢复能力。")
        for key, expected_path, directory in (
            ("app_env", "offline/app.env", False),
            ("cookies", "offline/cookies", True),
        ):
            metadata = offline.get(key)
            if not isinstance(metadata, Mapping):
                raise BackupArchiveError(f"离线 {key} 清单格式无效。")
            present = bool(metadata.get("present"))
            declared_path = str(metadata.get("path") or "")
            if not present:
                if declared_path:
                    raise BackupArchiveError(f"缺失的离线 {key} 不应声明材料路径。")
                continue
            if declared_path != expected_path:
                raise BackupArchiveError(f"离线 {key} 材料路径无效。")
            if directory:
                prefix = f"{declared_path}/"
                if not any(name.startswith(prefix) for name in names):
                    raise BackupArchiveError(f"离线 {key} 材料不存在。")
                allowed_prefixes.append(prefix)
            else:
                if declared_path not in names:
                    raise BackupArchiveError(f"离线 {key} 材料不存在。")
                allowed_exact.add(declared_path)

        database = offline.get("database")
        if not isinstance(database, Mapping):
            raise BackupArchiveError("离线数据库清单格式无效。")
        database_path = str(database.get("path") or "")
        if not database_path.startswith("offline/") or database_path not in names:
            raise BackupArchiveError("离线数据库材料不存在。")
        if database.get("online_restore") is not False:
            raise BackupArchiveError("完整数据库不得声明在线恢复能力。")
        allowed_exact.add(database_path)

        unexpected = sorted(
            name for name in names
            if name not in allowed_exact and not any(name.startswith(prefix) for prefix in allowed_prefixes)
        )
        if unexpected:
            raise BackupArchiveError(f"归档包含合同外材料：{unexpected[:3]}")

    def inspect_archive(self, archive_path: Path, *, source: str, source_ref: str = "") -> ArchiveDescriptor:
        archive_path = Path(archive_path)
        if not archive_path.is_file():
            raise BackupArchiveError("备份归档不存在。")
        try:
            with zipfile.ZipFile(archive_path, "r") as archive:
                entries = self._zip_entries(archive)
                names = {entry.filename.replace("\\", "/") for entry in entries if not entry.is_dir()}
                if not {"manifest.json", "checksums.sha256", "RESTORE.md"}.issubset(names):
                    raise BackupArchiveError("归档缺少 manifest、校验清单或离线恢复说明。")
                try:
                    manifest = json.loads(archive.read("manifest.json").decode("utf-8"))
                    checksum_rows = self._parse_checksums(archive.read("checksums.sha256").decode("utf-8"))
                except BackupArchiveError:
                    raise
                except Exception as err:
                    raise BackupArchiveError(f"归档合同读取失败：{err}") from err
                if manifest.get("format") != ARCHIVE_FORMAT:
                    raise BackupArchiveError("不支持的备份归档格式。")
                self._validate_manifest_contract(manifest, names)
                backup_id = str(manifest.get("backup_id") or "").strip()
                fingerprint = str(manifest.get("archive_fingerprint") or "").strip().lower()
                try:
                    uuid.UUID(backup_id)
                except (ValueError, AttributeError) as err:
                    raise BackupArchiveError("归档 backup_id 无效。") from err
                listed = {path for path, _ in checksum_rows}
                expected = names - {"checksums.sha256"}
                if listed != expected:
                    missing = sorted(expected - listed)
                    extra = sorted(listed - expected)
                    raise BackupArchiveError(f"归档校验清单不完整：missing={missing[:3]} extra={extra[:3]}")
                for path, expected_digest in checksum_rows:
                    digest = hashlib.sha256()
                    with archive.open(path) as stream:
                        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                            digest.update(chunk)
                    if digest.hexdigest() != expected_digest:
                        raise BackupArchiveError(f"归档完整性校验失败：{path}")
                manifest_core = dict(manifest)
                manifest_core.pop("archive_fingerprint", None)
                payload_rows = [(path, digest) for path, digest in checksum_rows if path != "manifest.json"]
                calculated = self._fingerprint(manifest_core, payload_rows)
                if calculated != fingerprint:
                    raise BackupArchiveError("归档指纹校验失败。")
        except zipfile.BadZipFile as err:
            raise BackupArchiveError("备份归档不是有效 ZIP 文件。") from err

        plugin_items = (((manifest.get("components") or {}).get(ARCHIVE_COMPONENT_PLUGINS) or {}).get("items") or [])
        plugins = tuple(
            plugin_id for plugin_id in (_safe_plugin_id(item.get("id")) for item in plugin_items if isinstance(item, dict))
            if plugin_id
        )
        components = tuple(
            component for component in ARCHIVE_COMPONENTS
            if ((manifest.get("components") or {}).get(component) or {}).get("present") is not False
        )
        return ArchiveDescriptor(
            backup_id=backup_id,
            name=archive_path.name,
            source=source,
            fingerprint=fingerprint,
            created_at=str(manifest.get("created_at") or ""),
            size=archive_path.stat().st_size,
            components=components,
            plugins=plugins,
            sensitive=bool(manifest.get("sensitive", True)),
            source_ref=source_ref or archive_path.name,
        )

    def read_manifest(self, archive_path: Path) -> Dict[str, Any]:
        # Always perform the full validation before returning archive metadata.
        self.inspect_archive(archive_path, source="internal", source_ref=Path(archive_path).name)
        with zipfile.ZipFile(archive_path, "r") as archive:
            return json.loads(archive.read("manifest.json").decode("utf-8"))

    def extract_verified(self, archive_path: Path, target_dir: Path) -> Dict[str, Any]:
        descriptor = self.inspect_archive(archive_path, source="internal", source_ref=Path(archive_path).name)
        target_dir = Path(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(archive_path, "r") as archive:
            entries = self._zip_entries(archive)
            for entry in entries:
                if entry.is_dir():
                    continue
                relative = PurePosixPath(entry.filename.replace("\\", "/"))
                target = target_dir.joinpath(*relative.parts).resolve(strict=False)
                target_root = target_dir.resolve(strict=False)
                if target != target_root and target_root not in target.parents:
                    raise BackupArchiveError(f"归档解压路径越界：{entry.filename}")
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(entry) as source, target.open("wb") as destination:
                    shutil.copyfileobj(source, destination)
        return {"descriptor": descriptor.to_dict(), "manifest": self.read_manifest(archive_path)}
