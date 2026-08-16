"""Domain contracts for Signal backup archives and restore operations.

The MoviePilot plugin configuration remains a flat JSON object because that is
the host contract.  This module is the single place that translates that flat
object into the backup domain model used by schedulers, actions and APIs.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import base64
from enum import Enum
import threading
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


ARCHIVE_FORMAT = "signal-backup/v2"
ARCHIVE_COMPONENT_MOVIEPILOT = "moviepilot"
ARCHIVE_COMPONENT_PLUGINS = "plugins"
ARCHIVE_COMPONENT_OFFLINE = "offline"
ARCHIVE_COMPONENTS = (
    ARCHIVE_COMPONENT_MOVIEPILOT,
    ARCHIVE_COMPONENT_PLUGINS,
    ARCHIVE_COMPONENT_OFFLINE,
)

# MoviePilot keeps plugin installation/folder governance in systemconfig rather
# than under the ``plugin.<id>`` namespace.  It is part of the plugin component
# and must never be restored as generic MoviePilot settings.
PLUGIN_REGISTRY_KEYS = ("UserInstalledPlugins", "PluginFolders")

# Signal's own operational material is deliberately excluded from a plugin
# source/files snapshot.  Restore preserves these directories while replacing
# the managed plugin file tree.
SIGNAL_ARCHIVE_EXCLUDED_DIR_NAMES = frozenset({
    "backup", "backups", "temp", "tmp", ".restore-cache", ".imports", ".emergency",
    "pluginuninstallbackup",
})

# Backup creation, restore and backup-config mutations share one lightweight
# in-process conflict boundary.  The host runs one Signal instance per plugin.
BACKUP_OPERATION_LOCK = threading.Lock()
ONLINE_RESTORE_COMPONENTS = (
    ARCHIVE_COMPONENT_MOVIEPILOT,
    ARCHIVE_COMPONENT_PLUGINS,
)

SOURCE_LOCAL = "local"
SOURCE_WEBDAV = "webdav"
SOURCE_TEMP_WEBDAV = "temporary_webdav"
SOURCE_UPLOAD = "upload"
RESTORE_SOURCES = (SOURCE_LOCAL, SOURCE_WEBDAV, SOURCE_TEMP_WEBDAV, SOURCE_UPLOAD)

PLUGIN_SCOPE_ALL = "all"
PLUGIN_SCOPE_INCLUDE = "include"
PLUGIN_SCOPE_EXCLUDE = "exclude"
PLUGIN_SCOPE_MODES = (PLUGIN_SCOPE_ALL, PLUGIN_SCOPE_INCLUDE, PLUGIN_SCOPE_EXCLUDE)

# These keys belonged to the removed dual restore/UI state or to a second
# scheduler switch.  They may be read once but are never emitted by the new
# save payload, so MoviePilot's replace-style plugin PUT removes them.
LEGACY_BACKUP_CONFIG_KEYS = frozenset({
    "backup_schedule_enabled",
    "backup_restore_source",
    "backup_restore_archive",
    "backup_restore_confirm",
    "backup_restore_workflow",
    "webdav_backup_restore_archive",
    "webdav_backup_restore_confirm",
    "restore_config",
    "restore_cookies",
    "restore_database",
})


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def as_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return bool(default)
    if isinstance(value, str):
        return value.strip().lower() not in {"", "0", "false", "no", "off"}
    return bool(value)


def as_int(value: Any, default: int, minimum: int = 0, maximum: Optional[int] = None) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = int(default)
    parsed = max(int(minimum), parsed)
    if maximum is not None:
        parsed = min(int(maximum), parsed)
    return parsed


def unique_strings(value: Any) -> List[str]:
    if isinstance(value, str):
        values: Iterable[Any] = value.split(",")
    elif isinstance(value, (list, tuple, set)):
        values = value
    elif value:
        values = [value]
    else:
        values = []
    result: List[str] = []
    for item in values:
        text = str(item or "").strip()
        if text and text not in result:
            result.append(text)
    return result


def encode_json_value(value: Any) -> Any:
    """Convert host values to a loss-aware JSON representation."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, bytes):
        return {"__signal_type__": "bytes", "base64": base64.b64encode(value).decode("ascii")}
    if isinstance(value, bytearray):
        return encode_json_value(bytes(value))
    if isinstance(value, datetime):
        return {"__signal_type__": "datetime", "iso": value.isoformat()}
    if isinstance(value, Enum):
        return encode_json_value(value.value)
    if isinstance(value, Mapping):
        return {str(key): encode_json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [encode_json_value(item) for item in value]
    if hasattr(value, "dict") and callable(value.dict):
        return encode_json_value(value.dict())
    if hasattr(value, "model_dump") and callable(value.model_dump):
        return encode_json_value(value.model_dump())
    if hasattr(value, "__dict__"):
        return encode_json_value({
            key: item for key, item in vars(value).items()
            if not str(key).startswith("_")
        })
    return str(value)


def decode_json_value(value: Any) -> Any:
    if isinstance(value, list):
        return [decode_json_value(item) for item in value]
    if not isinstance(value, dict):
        return value
    marker = value.get("__signal_type__")
    if marker == "bytes":
        return base64.b64decode(str(value.get("base64") or ""), validate=True)
    if marker == "datetime":
        return str(value.get("iso") or "")
    return {key: decode_json_value(item) for key, item in value.items()}


@dataclass(frozen=True)
class WebDavCredentials:
    hostname: str = ""
    login: str = ""
    password: str = ""
    digest_auth: bool = False
    disable_check: bool = False

    @property
    def ready(self) -> bool:
        return bool(self.hostname and self.login and self.password)

    def public_dict(self) -> Dict[str, Any]:
        """Return non-secret state suitable for API responses and logs."""
        return {
            "configured": self.ready,
            "hostname": self.hostname,
            "login_configured": bool(self.login),
            "password_configured": bool(self.password),
            "digest_auth": self.digest_auth,
            "disable_check": self.disable_check,
        }


@dataclass(frozen=True)
class BackupSettings:
    enabled: bool = False
    cron: str = "0 4 * * 1"
    local_path: str = "/config/plugins/Signal/Backup"
    local_keep_count: int = 5
    webdav_enabled: bool = False
    webdav_keep_count: int = 5
    webdav: WebDavCredentials = field(default_factory=WebDavCredentials)
    notify: bool = False
    notify_type: str = "Plugin"
    migrated_legacy_keys: Tuple[str, ...] = ()

    @classmethod
    def from_config(cls, config: Optional[Mapping[str, Any]]) -> "BackupSettings":
        source = dict(config or {})
        webdav = WebDavCredentials(
            hostname=str(source.get("backup_webdav_hostname") or "").strip().rstrip("/"),
            login=str(source.get("backup_webdav_login") or "").strip(),
            password=str(source.get("backup_webdav_password") or ""),
            digest_auth=as_bool(source.get("backup_webdav_digest_auth"), False),
            disable_check=as_bool(source.get("backup_webdav_disable_check"), False),
        )
        # Existing installations with complete credentials are migrated once
        # when the explicit target switch did not yet exist.
        webdav_enabled = as_bool(
            source.get("backup_webdav_enabled"),
            default=webdav.ready if "backup_webdav_enabled" not in source else False,
        )
        migrated = tuple(sorted(key for key in LEGACY_BACKUP_CONFIG_KEYS if key in source))
        return cls(
            enabled=as_bool(source.get("backup_enabled"), False),
            cron=str(source.get("backup_cron") or "0 4 * * 1").strip(),
            local_path=str(source.get("backup_path") or "/config/plugins/Signal/Backup").strip(),
            local_keep_count=as_int(source.get("backup_keep_count"), 5, 1, 1000),
            webdav_enabled=bool(webdav_enabled),
            webdav_keep_count=as_int(source.get("backup_webdav_max_count"), 5, 1, 1000),
            webdav=webdav,
            notify=as_bool(source.get("backup_notify"), False),
            notify_type=str(source.get("backup_notify_type") or "Plugin").strip() or "Plugin",
            migrated_legacy_keys=migrated,
        )

    def current_config(self) -> Dict[str, Any]:
        """Return only current persisted keys; legacy restore state is omitted."""
        return {
            "backup_enabled": self.enabled,
            "backup_cron": self.cron,
            "backup_path": self.local_path,
            "backup_keep_count": self.local_keep_count,
            "backup_notify": self.notify,
            "backup_notify_type": self.notify_type,
            "backup_webdav_enabled": self.webdav_enabled,
            "backup_webdav_hostname": self.webdav.hostname,
            "backup_webdav_login": self.webdav.login,
            "backup_webdav_password": self.webdav.password,
            "backup_webdav_digest_auth": self.webdav.digest_auth,
            "backup_webdav_disable_check": self.webdav.disable_check,
            "backup_webdav_max_count": self.webdav_keep_count,
        }


@dataclass(frozen=True)
class ArchiveDescriptor:
    backup_id: str
    name: str
    source: str
    fingerprint: str
    created_at: str
    size: int = 0
    components: Tuple[str, ...] = ARCHIVE_COMPONENTS
    plugins: Tuple[str, ...] = ()
    sensitive: bool = True
    source_ref: str = ""

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["components"] = list(self.components)
        data["plugins"] = list(self.plugins)
        return data


@dataclass(frozen=True)
class RestoreSelection:
    backup_id: str
    components: Tuple[str, ...]
    plugin_scope: str = PLUGIN_SCOPE_ALL
    plugin_ids: Tuple[str, ...] = ()

    @classmethod
    def from_payload(cls, payload: Optional[Mapping[str, Any]]) -> "RestoreSelection":
        source = dict(payload or {})
        allowed = {"backup_id", "components", "plugin_scope", "plugin_ids"}
        unexpected = sorted(set(source) - allowed)
        if unexpected:
            raise ValueError(f"恢复请求包含未授权字段：{'、'.join(unexpected)}")
        backup_id = str(source.get("backup_id") or "").strip()
        if not backup_id:
            raise ValueError("请选择并检查一个可恢复归档。")
        raw_components = source.get("components")
        if isinstance(raw_components, str):
            component_values = [item.strip() for item in raw_components.split(",") if item.strip()]
        elif isinstance(raw_components, (list, tuple)):
            component_values = [str(item or "").strip() for item in raw_components if str(item or "").strip()]
        else:
            component_values = []
        duplicates = sorted({item for item in component_values if component_values.count(item) > 1})
        if duplicates:
            raise ValueError(f"恢复请求包含重复组件：{'、'.join(duplicates)}")
        unknown = sorted(set(component_values) - set(ONLINE_RESTORE_COMPONENTS))
        if unknown:
            raise ValueError(f"恢复请求包含不支持的组件：{'、'.join(unknown)}")
        components = tuple(component_values)
        if not components:
            raise ValueError("请至少选择 MoviePilot 配置或插件恢复。")
        scope = str(source.get("plugin_scope") or PLUGIN_SCOPE_ALL).strip().lower()
        if scope not in PLUGIN_SCOPE_MODES:
            raise ValueError("插件恢复范围无效。")
        plugin_ids = tuple(unique_strings(source.get("plugin_ids")))
        if ARCHIVE_COMPONENT_PLUGINS in components and scope in {PLUGIN_SCOPE_INCLUDE, PLUGIN_SCOPE_EXCLUDE} and not plugin_ids:
            raise ValueError("当前插件恢复范围需要选择插件。")
        return cls(
            backup_id=backup_id,
            components=components,
            plugin_scope=scope,
            plugin_ids=plugin_ids,
        )

    def select_plugins(self, available: Sequence[str]) -> List[str]:
        ordered = unique_strings(available)
        selected = set(self.plugin_ids)
        if self.plugin_scope == PLUGIN_SCOPE_INCLUDE:
            return [plugin_id for plugin_id in ordered if plugin_id in selected]
        if self.plugin_scope == PLUGIN_SCOPE_EXCLUDE:
            return [plugin_id for plugin_id in ordered if plugin_id not in selected]
        return ordered


@dataclass
class BackupOperation:
    operation_id: str
    kind: str
    status: str = "running"
    started_at: str = field(default_factory=utc_now)
    finished_at: str = ""
    backup_id: str = ""
    success: bool = False
    partial: bool = False
    message: str = ""
    components: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def finish(self, *, status: str, message: str = "") -> None:
        self.status = status
        self.success = status == "success"
        self.partial = status == "partial"
        self.message = message
        self.finished_at = utc_now()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
