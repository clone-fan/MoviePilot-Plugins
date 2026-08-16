"""Active-database snapshot adapters used by Signal backup archives."""

from __future__ import annotations

import os
import shutil
import sqlite3
import subprocess
from pathlib import Path
from typing import Any, Dict, Optional


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
        for candidate in sorted(glob.glob(pattern)):
            if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
                return candidate
    return ""


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
    pg_dump = _find_binary("pg_dump")
    if not pg_dump:
        raise DatabaseSnapshotError("当前环境未找到 pg_dump，无法生成 PostgreSQL 完整归档。")
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / "moviepilot.postgresql.dump"
    if target.exists():
        target.unlink()
    host = str(getattr(settings, "DB_POSTGRESQL_HOST", "localhost") or "localhost")
    port = str(getattr(settings, "DB_POSTGRESQL_PORT", "5432") or "5432")
    username = str(getattr(settings, "DB_POSTGRESQL_USERNAME", "") or "")
    database = str(getattr(settings, "DB_POSTGRESQL_DATABASE", "") or "")
    env = os.environ.copy()
    env["PGPASSWORD"] = str(getattr(settings, "DB_POSTGRESQL_PASSWORD", "") or "")
    command = [
        pg_dump,
        "--format=custom",
        "--no-password",
        "--host", host,
        "--port", port,
        "--username", username,
        "--file", str(target),
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
        raise DatabaseSnapshotError(f"pg_dump 执行失败：{err}") from err
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "pg_dump 返回失败")[-300:]
        raise DatabaseSnapshotError(f"pg_dump -Fc 失败：{detail}")
    if not target.is_file() or target.stat().st_size <= 5 or target.read_bytes()[:5] != b"PGDMP":
        raise DatabaseSnapshotError("pg_dump 未生成有效的 custom-format 归档。")
    return {
        "type": "postgresql",
        "path": target.name,
        "source": {"host": host, "port": port, "database": database},
        "method": "pg_dump-custom",
        "size": target.stat().st_size,
        "online_restore": False,
    }


def create_active_database_snapshot(target_dir: Path) -> Dict[str, Any]:
    if active_database_type() == "postgresql":
        return create_postgresql_snapshot(target_dir)
    return create_sqlite_snapshot(target_dir)
