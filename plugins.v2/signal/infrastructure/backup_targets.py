"""Local, saved-WebDAV and temporary-WebDAV archive adapters."""

from __future__ import annotations

import base64
import hashlib
import shutil
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any, Dict, List, Mapping, Optional, Tuple

from ..application.backup_models import (
    BackupSettings,
    SOURCE_LOCAL,
    SOURCE_TEMP_WEBDAV,
    SOURCE_UPLOAD,
    SOURCE_WEBDAV,
    WebDavCredentials,
)


class BackupTargetError(RuntimeError):
    pass


def _safe_archive_name(value: Any) -> str:
    raw = str(value or "").strip().replace("\\", "/")
    name = PurePosixPath(raw).name
    if not name or raw.strip("/") != name:
        raise BackupTargetError("归档名称无效。")
    if not name.lower().endswith(".zip"):
        raise BackupTargetError("只允许选择 ZIP 备份归档。")
    return name


def _is_signal_archive_name(name: str) -> bool:
    """Return whether a ZIP is owned by Signal's retention policy."""
    return str(name or "").lower().startswith("signal-backup-")


def _atomic_copy(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(f".{target.name}.uploading")
    if temporary.exists():
        temporary.unlink()
    shutil.copy2(source, temporary)
    if source.stat().st_size != temporary.stat().st_size:
        temporary.unlink(missing_ok=True)
        raise BackupTargetError("归档复制后大小不一致。")
    temporary.replace(target)


class LocalBackupTarget:
    def __init__(self, root: Path, keep_count: int):
        self.root = Path(root).resolve(strict=False)
        self.keep_count = max(1, int(keep_count or 1))

    def deliver(self, archive_path: Path) -> Dict[str, Any]:
        self.root.mkdir(parents=True, exist_ok=True)
        target = (self.root / _safe_archive_name(archive_path.name)).resolve(strict=False)
        if self.root != target and self.root not in target.parents:
            raise BackupTargetError("本地备份目标越界。")
        _atomic_copy(Path(archive_path), target)
        removed = self.cleanup()
        return {
            "target": SOURCE_LOCAL,
            "success": True,
            "name": target.name,
            "path": str(target),
            "removed": removed,
        }

    def cleanup(self) -> List[str]:
        archives = sorted(
            [path for path in self.root.glob("signal-backup-*.zip") if path.is_file()],
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
        removed: List[str] = []
        for archive in archives[self.keep_count:]:
            archive.unlink()
            removed.append(archive.name)
        return removed

    def list(self) -> List[Dict[str, Any]]:
        if not self.root.is_dir():
            return []
        result = []
        for path in self.root.glob("*.zip"):
            if not path.is_file():
                continue
            stat = path.stat()
            result.append({
                "name": path.name,
                "source": SOURCE_LOCAL,
                "size": stat.st_size,
                "mtime": stat.st_mtime,
            })
        return sorted(result, key=lambda item: (item["mtime"], item["name"]), reverse=True)

    def resolve(self, archive_name: Any) -> Path:
        name = _safe_archive_name(archive_name)
        target = (self.root / name).resolve(strict=False)
        if self.root != target and self.root not in target.parents:
            raise BackupTargetError("本地归档路径越界。")
        if not target.is_file():
            raise BackupTargetError("本地备份归档不存在。")
        return target


class WebDavBackupTarget:
    def __init__(self, credentials: WebDavCredentials, keep_count: int):
        if not credentials.ready:
            raise BackupTargetError("WebDAV 地址、账号或密码未完整配置。")
        self.credentials = credentials
        self.keep_count = max(1, int(keep_count or 1))

    def _client(self):
        try:
            from webdav3.client import Client
        except ImportError as err:
            raise BackupTargetError("webdav3-client 未安装。") from err
        options = {
            "webdav_hostname": self.credentials.hostname.rstrip("/"),
            "webdav_login": self.credentials.login,
            "webdav_password": self.credentials.password,
            "disable_check": self.credentials.disable_check,
        }
        if self.credentials.digest_auth:
            options["webdav_auth_type"] = "digest"
        client = Client(options)
        if not self.credentials.disable_check and not client.check():
            raise BackupTargetError("WebDAV 连接检查失败。")
        return client

    def deliver(self, archive_path: Path) -> Dict[str, Any]:
        client = self._client()
        name = _safe_archive_name(archive_path.name)
        client.upload_sync(remote_path=name, local_path=str(archive_path))
        removed = self.cleanup(client=client)
        return {"target": SOURCE_WEBDAV, "success": True, "name": name, "removed": removed}

    def list(self, client=None, *, managed_only: bool = False) -> List[Dict[str, Any]]:
        client = client or self._client()
        result: List[Dict[str, Any]] = []
        for value in client.list() or []:
            try:
                name = _safe_archive_name(value)
            except BackupTargetError:
                continue
            if managed_only and not _is_signal_archive_name(name):
                continue
            info: Mapping[str, Any] = {}
            try:
                info = client.info(name) or {}
            except Exception:
                pass
            result.append({
                "name": name,
                "source": SOURCE_WEBDAV,
                "size": int(info.get("size") or info.get("content_length") or 0),
                "mtime": str(info.get("modified") or info.get("mtime") or ""),
            })
        return sorted(result, key=lambda item: item["name"], reverse=True)

    def cleanup(self, client=None) -> List[str]:
        client = client or self._client()
        archives = self.list(client=client, managed_only=True)
        removed: List[str] = []
        for item in archives[self.keep_count:]:
            client.clean(item["name"])
            removed.append(item["name"])
        return removed

    def download(self, archive_name: Any, target_dir: Path) -> Path:
        client = self._client()
        name = _safe_archive_name(archive_name)
        target_dir = Path(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / name
        temporary = target.with_name(f".{target.name}.downloading")
        temporary.unlink(missing_ok=True)
        client.download_sync(remote_path=name, local_path=str(temporary))
        if not temporary.is_file() or temporary.stat().st_size <= 0:
            temporary.unlink(missing_ok=True)
            raise BackupTargetError("WebDAV 归档下载失败。")
        temporary.replace(target)
        return target


class BackupTargetService:
    def __init__(self, settings: BackupSettings):
        self.settings = settings

    @property
    def local(self) -> LocalBackupTarget:
        return LocalBackupTarget(Path(self.settings.local_path), self.settings.local_keep_count)

    @property
    def imports_root(self) -> Path:
        return Path(self.settings.local_path).resolve(strict=False) / ".imports"

    def saved_webdav(self) -> WebDavBackupTarget:
        if not self.settings.webdav_enabled:
            raise BackupTargetError("WebDAV 备份目标未启用。")
        return WebDavBackupTarget(self.settings.webdav, self.settings.webdav_keep_count)

    @staticmethod
    def temporary_webdav(payload: Optional[Mapping[str, Any]], keep_count: int = 1) -> WebDavBackupTarget:
        source = dict(payload or {})
        credentials = WebDavCredentials(
            hostname=str(source.get("hostname") or "").strip().rstrip("/"),
            login=str(source.get("login") or "").strip(),
            password=str(source.get("password") or ""),
            digest_auth=bool(source.get("digest_auth", False)),
            disable_check=bool(source.get("disable_check", False)),
        )
        return WebDavBackupTarget(credentials, keep_count)

    def deliver(self, archive_path: Path) -> List[Dict[str, Any]]:
        results: List[Dict[str, Any]] = []
        try:
            local_result = self.local.deliver(archive_path)
            local_result.setdefault("status", "success")
            results.append(local_result)
        except Exception as err:
            results.append({"target": SOURCE_LOCAL, "success": False, "status": "failed", "error": str(err)})
        if self.settings.webdav_enabled:
            if not self.settings.webdav.ready:
                results.append({
                    "target": SOURCE_WEBDAV,
                    "success": False,
                    "status": "not_configured",
                    "error": "WebDAV 地址、账号或密码未完整配置。",
                })
            else:
                try:
                    webdav_result = self.saved_webdav().deliver(archive_path)
                    webdav_result.setdefault("status", "success")
                    results.append(webdav_result)
                except Exception as err:
                    results.append({"target": SOURCE_WEBDAV, "success": False, "status": "failed", "error": str(err)})
        return results

    def list_source(
        self,
        source: str,
        temporary_credentials: Optional[Mapping[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        if source == SOURCE_LOCAL:
            return self.local.list()
        if source == SOURCE_UPLOAD:
            target = LocalBackupTarget(self.imports_root, 1000)
            return [{**item, "source": SOURCE_UPLOAD} for item in target.list()]
        if source == SOURCE_WEBDAV:
            return self.saved_webdav().list()
        if source == SOURCE_TEMP_WEBDAV:
            return [
                {**item, "source": SOURCE_TEMP_WEBDAV}
                for item in self.temporary_webdav(temporary_credentials).list()
            ]
        raise BackupTargetError("未知的备份来源。")

    def resolve_source(
        self,
        source: str,
        archive_name: Any,
        *,
        cache_dir: Path,
        temporary_credentials: Optional[Mapping[str, Any]] = None,
    ) -> Path:
        if source == SOURCE_LOCAL:
            return self.local.resolve(archive_name)
        if source == SOURCE_UPLOAD:
            return LocalBackupTarget(self.imports_root, 1000).resolve(archive_name)
        if source == SOURCE_WEBDAV:
            return self.saved_webdav().download(archive_name, cache_dir)
        if source == SOURCE_TEMP_WEBDAV:
            return self.temporary_webdav(temporary_credentials).download(archive_name, cache_dir)
        raise BackupTargetError("未知的备份来源。")

    def import_base64(self, content: str, filename: str, max_bytes: int = 2 * 1024 * 1024 * 1024) -> Path:
        name = _safe_archive_name(filename)
        raw = str(content or "")
        if raw.startswith("data:"):
            raw = raw.split(",", 1)[-1]
        try:
            decoded = base64.b64decode(raw, validate=True)
        except Exception as err:
            raise BackupTargetError("浏览器归档内容不是有效 Base64。") from err
        if not decoded or len(decoded) > max_bytes:
            raise BackupTargetError("浏览器归档为空或超过大小上限。")
        self.imports_root.mkdir(parents=True, exist_ok=True)
        digest = hashlib.sha256(decoded).hexdigest()[:12]
        stem = Path(name).stem[:100]
        target = self.imports_root / f"{stem}-{digest}.zip"
        temporary = target.with_name(f".{target.name}.importing")
        temporary.write_bytes(decoded)
        temporary.replace(target)
        return target

    @staticmethod
    def download_base64(path: Path, max_bytes: int = 2 * 1024 * 1024 * 1024) -> Dict[str, Any]:
        path = Path(path)
        size = path.stat().st_size
        if size > max_bytes:
            raise BackupTargetError("归档过大，不能通过浏览器接口下载。")
        return {
            "name": path.name,
            "size": size,
            "content_base64": base64.b64encode(path.read_bytes()).decode("ascii"),
        }
