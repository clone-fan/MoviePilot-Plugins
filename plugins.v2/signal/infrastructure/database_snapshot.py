"""Active-database snapshot adapters used by Signal backup archives."""

from __future__ import annotations

import os
import re
import shutil
import socket
import sqlite3
import subprocess
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple


class DatabaseSnapshotError(RuntimeError):
    pass


def _settings():
    from app.core.config import settings

    return settings


def active_database_type() -> str:
    value = str(getattr(_settings(), "DB_TYPE", "sqlite") or "sqlite").strip().lower()
    if "postgres" in value:
        return "postgresql"
    return "sqlite"


def sqlite_database_path() -> Path:
    settings = _settings()
    configured = (
        getattr(settings, "DB_SQLITE_PATH", None)
        or getattr(settings, "DATABASE_PATH", None)
    )
    if configured:
        return Path(str(configured))
    return Path(str(getattr(settings, "CONFIG_PATH", "/config"))) / "user.db"


def _find_binary(name: str) -> str:
    found = shutil.which(name)
    if found:
        return found
    import glob

    patterns = (
        f"/usr/bin/{name}",
        f"/usr/local/bin/{name}",
        f"/usr/lib/postgresql/*/bin/{name}",
        f"/opt/homebrew/bin/{name}",
        f"/opt/homebrew/opt/postgresql*/bin/{name}",
    )
    for pattern in patterns:
        for candidate in sorted(glob.glob(pattern), reverse=True):
            if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
                return candidate
    return ""


_PG_MAJOR_PATTERN = re.compile(r"(?<!\d)(\d+)(?:\.\d+)?")
_DOCKER_STDERR_LIMIT = 8192


def _redact(value: Any, secrets: Iterable[str] = ()) -> str:
    text = str(value or "")
    for secret in secrets:
        if secret:
            text = text.replace(str(secret), "***")
    return text[-400:]


def _parse_postgresql_major(value: Any) -> Optional[int]:
    match = _PG_MAJOR_PATTERN.search(str(value or ""))
    if not match:
        return None
    try:
        major = int(match.group(1))
    except (TypeError, ValueError):
        return None
    return major if major > 0 else None


def _postgresql_server_major() -> int:
    """Read the connected server version instead of guessing from image tags."""
    settings = _settings()
    password = str(getattr(settings, "DB_POSTGRESQL_PASSWORD", "") or "")
    try:
        from app.db import Engine
        from sqlalchemy import text

        with Engine.connect() as connection:
            raw = connection.execute(text("SHOW server_version_num")).scalar()
    except Exception as err:
        detail = _redact(err, (password,))
        raise DatabaseSnapshotError(f"无法读取 PostgreSQL 服务端版本，已停止数据库备份：{detail}") from err

    try:
        numeric = int(str(raw).strip())
    except (TypeError, ValueError):
        numeric = 0
    major = numeric // 10000 if numeric else _parse_postgresql_major(raw)
    if not major:
        raise DatabaseSnapshotError("无法解析 PostgreSQL 服务端主版本，已停止数据库备份。")
    return int(major)


def _local_pg_dump_major(pg_dump: str) -> Optional[int]:
    try:
        result = subprocess.run(
            [pg_dump, "--version"],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
    except Exception:
        return None
    if result.returncode != 0:
        return None
    return _parse_postgresql_major(result.stdout or result.stderr)


def _snapshot_file_is_valid(path: Path) -> bool:
    try:
        if not path.is_file() or path.stat().st_size <= 5:
            return False
        with path.open("rb") as stream:
            return stream.read(5) == b"PGDMP"
    except OSError:
        return False


def _docker_endpoints(settings: Any) -> List[str]:
    endpoints: List[str] = []
    socket_path = Path("/var/run/docker.sock")
    if socket_path.exists():
        endpoints.append("unix:///var/run/docker.sock")
    configured = str(getattr(settings, "DOCKER_CLIENT_API", "") or "").strip()
    if configured and configured not in endpoints:
        endpoints.append(configured)
    return endpoints


def _container_attrs(container: Any) -> Mapping[str, Any]:
    attrs = getattr(container, "attrs", None)
    return attrs if isinstance(attrs, Mapping) else {}


def _container_networks(container: Any) -> Mapping[str, Any]:
    network_settings = _container_attrs(container).get("NetworkSettings") or {}
    networks = network_settings.get("Networks") if isinstance(network_settings, Mapping) else {}
    return networks if isinstance(networks, Mapping) else {}


def _compose_labels(attrs: Mapping[str, Any]) -> Tuple[str, str]:
    config = attrs.get("Config") or {}
    if not isinstance(config, Mapping):
        return "", ""
    labels = config.get("Labels") or {}
    if not isinstance(labels, Mapping):
        return "", ""
    project = str(labels.get("com.docker.compose.project") or "").strip().lower()
    service = str(labels.get("com.docker.compose.service") or "").strip().lower()
    return project, service


def _current_container_context(client: Any) -> Tuple[Set[str], str]:
    identifiers = []
    for value in (socket.gethostname(), os.environ.get("HOSTNAME")):
        value = str(value or "").strip()
        if value and value not in identifiers:
            identifiers.append(value)
    try:
        hostname_file = Path("/etc/hostname")
        if hostname_file.is_file():
            value = hostname_file.read_text(encoding="utf-8").strip()
            if value and value not in identifiers:
                identifiers.append(value)
    except OSError:
        pass
    for identifier in identifiers:
        try:
            container = client.containers.get(identifier)
            project, _service = _compose_labels(_container_attrs(container))
            if not project:
                continue
            return set(_container_networks(container).keys()), project
        except Exception:
            continue
    return set(), ""


def _postgresql_identity(attrs: Mapping[str, Any], compose_project: str) -> bool:
    config = attrs.get("Config") or {}
    if not isinstance(config, Mapping):
        return False
    image = str(config.get("Image") or "").split("@", 1)[0].rsplit("/", 1)[-1]
    image_name = image.split(":", 1)[0].strip().lower()
    project, service = _compose_labels(attrs)
    return bool(
        image_name == "postgres"
        and compose_project
        and project == compose_project
        and service
    )


def _candidate_host_identities(container: Any, shared_networks: Set[str]) -> Set[str]:
    attrs = _container_attrs(container)
    _project, service = _compose_labels(attrs)
    identities: Set[str] = set()
    if service:
        identities.add(service)
    for network_name in shared_networks:
        network = _container_networks(container).get(network_name) or {}
        if not isinstance(network, Mapping):
            continue
        for value in network.get("Aliases") or []:
            value = str(value or "").strip().lower()
            if value:
                identities.add(value)
        value = str(network.get("IPAddress") or "").strip().lower()
        if value:
            identities.add(value)
    return identities


def _find_postgresql_container(client: Any, host: str) -> Any:
    host_key = str(host or "").strip().lower().rstrip(".")
    if not host_key or host_key in {"localhost", "127.0.0.1", "::1"}:
        raise RuntimeError("数据库 host 不是可安全匹配的 Compose 服务名或容器地址。")
    current_networks, compose_project = _current_container_context(client)
    if not current_networks or not compose_project:
        raise RuntimeError("无法确认 MoviePilot 所属 Compose project 与 Docker 网络。")
    candidates = []
    for container in client.containers.list(filters={"status": "running"}):
        attrs = _container_attrs(container)
        state = attrs.get("State") or {}
        if state and state.get("Running") is False:
            continue
        networks = _container_networks(container)
        shared = current_networks.intersection(networks.keys())
        if not shared or not _postgresql_identity(attrs, compose_project):
            continue
        identities = _candidate_host_identities(container, shared)
        if host_key in identities:
            candidates.append(container)
    if len(candidates) != 1:
        raise RuntimeError(
            "未找到唯一且安全匹配的 PostgreSQL 容器。"
            if not candidates
            else "PostgreSQL 容器匹配不唯一，已拒绝执行。"
        )
    return candidates[0]


def _docker_exec(
    api: Any,
    container_id: str,
    command: Sequence[str],
    *,
    environment: Optional[Mapping[str, str]] = None,
    output_path: Optional[Path] = None,
) -> Tuple[int, bytes, bytes]:
    """Run one fixed argv and stream stdout to disk when requested."""
    created = api.exec_create(
        container_id,
        cmd=list(command),
        stdout=True,
        stderr=True,
        stdin=False,
        tty=False,
        environment=dict(environment or {}),
    )
    exec_id = str((created or {}).get("Id") or "")
    if not exec_id:
        raise RuntimeError("Docker exec 未返回执行 ID。")
    stdout_capture = bytearray()
    stderr_capture = bytearray()
    stream = api.exec_start(exec_id, detach=False, tty=False, stream=True, demux=True)
    if isinstance(stream, (bytes, bytearray)):
        frames = (stream,)
    else:
        frames = stream
    output = output_path.open("wb") if output_path is not None else None
    try:
        for frame in frames:
            if isinstance(frame, tuple):
                stdout_chunk, stderr_chunk = frame
            else:
                stdout_chunk, stderr_chunk = frame, None
            if isinstance(stdout_chunk, int):
                stdout_chunk = bytes([stdout_chunk])
            if isinstance(stderr_chunk, int):
                stderr_chunk = bytes([stderr_chunk])
            if stdout_chunk:
                if output is not None:
                    output.write(stdout_chunk)
                elif len(stdout_capture) < _DOCKER_STDERR_LIMIT:
                    stdout_capture.extend(stdout_chunk[: _DOCKER_STDERR_LIMIT - len(stdout_capture)])
            if stderr_chunk and len(stderr_capture) < _DOCKER_STDERR_LIMIT:
                stderr_capture.extend(stderr_chunk[: _DOCKER_STDERR_LIMIT - len(stderr_capture)])
    finally:
        if output is not None:
            output.close()
    inspected = api.exec_inspect(exec_id) or {}
    exit_code = inspected.get("ExitCode")
    try:
        exit_code = int(exit_code)
    except (TypeError, ValueError):
        exit_code = -1
    return exit_code, bytes(stdout_capture), bytes(stderr_capture)


def _docker_postgresql_snapshot(
    target: Path,
    settings: Any,
    *,
    host: str,
    username: str,
    database: str,
    port: str,
    password: str,
    server_major: int,
) -> Dict[str, Any]:
    try:
        import docker
    except Exception as err:
        raise RuntimeError("当前环境未提供 Docker SDK。") from err

    endpoint_errors: List[str] = []
    for endpoint in _docker_endpoints(settings):
        client = None
        temp = target.with_name(f".{target.name}.docker-part")
        try:
            client = docker.DockerClient(base_url=endpoint, timeout=900)
            container = _find_postgresql_container(client, host)
            api = client.api
            version_exit, version_stdout, version_stderr = _docker_exec(
                api,
                container.id,
                ["pg_dump", "--version"],
            )
            container_version = _parse_postgresql_major(
                version_stdout.decode("utf-8", "replace") or version_stderr.decode("utf-8", "replace")
            )
            if version_exit != 0 or not container_version:
                raise RuntimeError("匹配的 PostgreSQL 容器未提供可识别的 pg_dump 版本。")
            if container_version < server_major:
                raise RuntimeError(
                    f"匹配容器内 pg_dump {container_version} 低于 PostgreSQL 服务端 {server_major}。"
                )
            command: List[str] = ["pg_dump", "--format=custom", "--no-password"]
            if username:
                command.extend(["--username", username])
            if port:
                command.extend(["--port", port])
            command.append(database)
            temp.unlink(missing_ok=True)
            exit_code, _stdout, stderr = _docker_exec(
                api,
                container.id,
                command,
                environment={"PGPASSWORD": password},
                output_path=temp,
            )
            if exit_code != 0:
                detail = _redact(stderr.decode("utf-8", "replace"), (password,)) or "pg_dump 返回失败"
                raise RuntimeError(f"容器内 pg_dump -Fc 失败：{detail}")
            if not _snapshot_file_is_valid(temp):
                raise RuntimeError("容器内 pg_dump 未生成有效的 custom-format 归档。")
            temp.replace(target)
            return {
                "type": "postgresql",
                "path": target.name,
                "source": {"host": host, "port": port, "database": database},
                "method": "pg_dump-custom",
                "executor": "postgresql-container",
                "server_major": server_major,
                "pg_dump_major": container_version,
                "size": target.stat().st_size,
                "online_restore": False,
            }
        except Exception as err:
            temp.unlink(missing_ok=True)
            endpoint_errors.append(_redact(err, (password,)))
        finally:
            try:
                if client is not None:
                    client.close()
            except Exception:
                pass
    detail = "; ".join(item for item in endpoint_errors if item)[:600]
    raise RuntimeError(detail or "没有可用的 Docker API 端点。")


def create_sqlite_snapshot(target_dir: Path) -> Dict[str, Any]:
    source = sqlite_database_path()
    if not source.is_file():
        raise DatabaseSnapshotError(f"活动 SQLite 数据库不存在：{source}")
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / "moviepilot.sqlite3"
    if target.exists():
        target.unlink()
    source_connection: Optional[sqlite3.Connection] = None
    target_connection: Optional[sqlite3.Connection] = None
    try:
        # SQLite Online Backup API produces a transactionally consistent copy
        # even when the source uses WAL.  user.db-wal/user.db-shm are therefore
        # deliberately not copied into the archive.
        source_connection = sqlite3.connect(f"file:{source.as_posix()}?mode=ro", uri=True, timeout=30)
        target_connection = sqlite3.connect(str(target), timeout=30)
        source_connection.backup(target_connection)
        target_connection.commit()
        integrity = target_connection.execute("PRAGMA integrity_check").fetchone()
        if not integrity or str(integrity[0]).lower() != "ok":
            raise DatabaseSnapshotError(f"SQLite 快照完整性检查失败：{integrity}")
    except DatabaseSnapshotError:
        raise
    except Exception as err:
        raise DatabaseSnapshotError(f"SQLite Online Backup 失败：{err}") from err
    finally:
        if target_connection is not None:
            target_connection.close()
        if source_connection is not None:
            source_connection.close()
    if not target.is_file() or target.stat().st_size <= 0:
        raise DatabaseSnapshotError("SQLite Online Backup 未生成有效快照。")
    return {
        "type": "sqlite",
        "path": target.name,
        "source": str(source),
        "method": "sqlite-online-backup",
        "size": target.stat().st_size,
        "online_restore": False,
    }


def create_postgresql_snapshot(target_dir: Path) -> Dict[str, Any]:
    settings = _settings()
    server_major = _postgresql_server_major()
    pg_dump = _find_binary("pg_dump")
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / "moviepilot.postgresql.dump"
    if target.exists():
        target.unlink()
    host = str(getattr(settings, "DB_POSTGRESQL_HOST", "localhost") or "localhost")
    port = str(getattr(settings, "DB_POSTGRESQL_PORT", "5432") or "5432")
    username = str(getattr(settings, "DB_POSTGRESQL_USERNAME", "") or "")
    database = str(getattr(settings, "DB_POSTGRESQL_DATABASE", "") or "")
    password = str(getattr(settings, "DB_POSTGRESQL_PASSWORD", "") or "")
    env = os.environ.copy()
    env["PGPASSWORD"] = password
    local_major = _local_pg_dump_major(pg_dump) if pg_dump else None
    local_reason = ""
    if pg_dump and local_major is not None and local_major >= server_major:
        temp = target.with_name(f".{target.name}.local-part")
        temp.unlink(missing_ok=True)
        command = [
            pg_dump,
            "--format=custom",
            "--no-password",
            "--host", host,
            "--port", port,
            "--username", username,
            "--file", str(temp),
            database,
        ]
        try:
            result = subprocess.run(
                command,
                env=env,
                capture_output=True,
                text=True,
                timeout=900,
                check=False,
            )
        except Exception as err:
            temp.unlink(missing_ok=True)
            raise DatabaseSnapshotError(f"pg_dump 执行失败：{_redact(err, (password,))}") from err
        if result.returncode != 0:
            temp.unlink(missing_ok=True)
            detail = _redact(result.stderr or result.stdout or "pg_dump 返回失败", (password,))
            raise DatabaseSnapshotError(f"pg_dump -Fc 失败：{detail}")
        if not _snapshot_file_is_valid(temp):
            temp.unlink(missing_ok=True)
            raise DatabaseSnapshotError("pg_dump 未生成有效的 custom-format 归档。")
        temp.replace(target)
        return {
            "type": "postgresql",
            "path": target.name,
            "source": {"host": host, "port": port, "database": database},
            "method": "pg_dump-custom",
            "executor": "local",
            "server_major": server_major,
            "pg_dump_major": local_major,
            "size": target.stat().st_size,
            "online_restore": False,
        }

    if not pg_dump:
        local_reason = "当前环境未找到 pg_dump"
    elif local_major is None:
        local_reason = "当前 pg_dump 版本无法识别"
    else:
        local_reason = f"当前 pg_dump {local_major} 低于 PostgreSQL 服务端 {server_major}"
    try:
        return _docker_postgresql_snapshot(
            target,
            settings,
            host=host,
            username=username,
            database=database,
            port=port,
            password=password,
            server_major=server_major,
        )
    except Exception as err:
        detail = _redact(err, (password,))
        raise DatabaseSnapshotError(
            f"{local_reason}；PostgreSQL {server_major} 需要兼容的 pg_dump，且未能安全调用匹配的 PostgreSQL 容器：{detail}"
        ) from err


def create_active_database_snapshot(target_dir: Path) -> Dict[str, Any]:
    if active_database_type() == "postgresql":
        return create_postgresql_snapshot(target_dir)
    return create_sqlite_snapshot(target_dir)
