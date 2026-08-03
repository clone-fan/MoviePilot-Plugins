import os
import json
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path, PurePosixPath
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from app.core.config import settings
from app.schemas import NotificationType
from app.log import logger


class BackupMixin:
    """Backup creation, restore, WebDAV, PostgreSQL dump, and log preview/clean."""

    def _build_backup_status(self) -> Dict[str, Any]:
        backup_path = Path(self._backup_path or "/config/plugins/Signal/Backup")
        files = []
        if backup_path.exists():
            for item in backup_path.glob("bk_*.zip"):
                try:
                    stat = item.stat()
                except Exception:
                    continue
                files.append({"path": str(item), "name": item.name, "size": stat.st_size, "size_text": self._format_bytes(stat.st_size), "mtime": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")})
        files.sort(key=lambda x: x["mtime"], reverse=True)
        return {"enabled": bool(self._backup_enabled), "cron": self._backup_cron, "keep_count": self._backup_keep_count, "back_path": str(backup_path), "backup_count": len(files), "backup_size": sum(x["size"] for x in files), "backup_size_text": self._format_bytes(sum(x["size"] for x in files)), "latest": files[:5], "direct": True}

    def _list_backup_archives(self) -> List[Dict[str, Any]]:
        backup_path = Path(self._backup_path or "/config/plugins/Signal/Backup")
        files: List[Dict[str, Any]] = []
        if not backup_path.exists():
            return files
        for item in backup_path.glob("bk_*.zip"):
            if not item.is_file():
                continue
            try:
                stat = item.stat()
            except Exception:
                continue
            files.append({
                "name": item.name,
                "path": str(item),
                "size": stat.st_size,
                "size_text": self._format_bytes(stat.st_size),
                "mtime": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            })
        files.sort(key=lambda x: x["name"], reverse=True)
        return files

    def _resolve_backup_archive(self, archive: Any) -> Path:
        backup_root = Path(self._backup_path or "/config/plugins/Signal/Backup").resolve(strict=False)
        raw = str(archive or "").strip()
        if not raw:
            raise ValueError("请选择要恢复的备份包。")
        candidate = Path(raw)
        archive_path = candidate.resolve(strict=False) if candidate.is_absolute() else (backup_root / raw).resolve(strict=False)
        if archive_path.suffix.lower() != ".zip" or not archive_path.name.startswith("bk_"):
            raise ValueError("只允许恢复备份目录内的 bk_*.zip 备份包。")
        if backup_root != archive_path and backup_root not in archive_path.parents:
            raise ValueError("备份包必须位于配置的备份目录内，禁止路径穿越。")
        if not archive_path.is_file():
            raise ValueError(f"备份包不存在：{archive_path.name}")
        return archive_path

    @staticmethod
    def _validate_backup_zip_entries(zf: zipfile.ZipFile) -> None:
        names = set(zf.namelist())
        if "manifest.json" not in names:
            raise ValueError("备份包缺少 manifest.json。")
        for info in zf.infolist():
            name = str(info.filename or "").replace("\\", "/")
            parts = PurePosixPath(name).parts
            if not name or name.startswith("/") or ".." in parts:
                raise ValueError(f"备份包包含非法路径：{info.filename}")

    def _inspect_backup_archive(self, archive_path: Path) -> Dict[str, Any]:
        with zipfile.ZipFile(archive_path, "r") as zf:
            self._validate_backup_zip_entries(zf)
            try:
                manifest = json.loads(zf.read("manifest.json").decode("utf-8"))
            except Exception as err:
                raise ValueError(f"manifest.json 读取失败：{err}") from err
            names = set(zf.namelist())
        stat = archive_path.stat()
        return {
            "archive": {
                "name": archive_path.name,
                "path": str(archive_path),
                "size": stat.st_size,
                "size_text": self._format_bytes(stat.st_size),
                "mtime": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
            },
            "manifest": manifest,
            "contains": {
                "config": [name for name in ("category.yaml", "app.env") if name in names],
                "cookies": any(name == "cookies" or name.startswith("cookies/") for name in names),
                "sqlite": sorted([name for name in names if name.startswith("user.db")]),
                "postgresql": "postgresql_backup.sql" in names,
            },
            "entries": sorted(names),
        }

    def _backup_restore_options(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "archive": payload.get("archive") or payload.get("name") or payload.get("path"),
            "restore_config": self._payload_bool(payload.get("restore_config", True)),
            "restore_cookies": self._payload_bool(payload.get("restore_cookies", True)),
            "restore_database": self._payload_bool(payload.get("restore_database", True)),
        }

    def _build_backup_restore_preview(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        options = self._backup_restore_options(payload)
        archive_path = self._resolve_backup_archive(options["archive"])
        data = self._inspect_backup_archive(archive_path)
        contains = data.get("contains") or {}
        selected: List[str] = []
        warnings: List[str] = []
        if options["restore_config"] and contains.get("config"):
            selected.extend([f"配置文件：{name}" for name in contains.get("config", [])])
        if options["restore_cookies"] and contains.get("cookies"):
            selected.append("cookies 目录")
        if options["restore_database"]:
            if contains.get("sqlite"):
                selected.extend([f"SQLite：{name}" for name in contains.get("sqlite", [])])
            if contains.get("postgresql"):
                selected.append("PostgreSQL：postgresql_backup.sql")
                if not self._find_psql():
                    warnings.append("当前环境未找到 psql，执行 PostgreSQL 恢复会失败。")
        data.update({
            "success": True,
            "dry_run": True,
            "selected": selected,
            "options": options,
            "config_path": str(Path(settings.CONFIG_PATH)),
            "warnings": warnings,
            "errors": [],
            "emergency_backup": "",
            "restored": [],
        })
        return data

    def _run_backup_restore(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        try:
            data = self._build_backup_restore_preview(payload)
        except Exception as err:
            return {"success": False, "dry_run": False, "errors": [str(err)], "warnings": [], "restored": [], "emergency_backup": ""}
        data["dry_run"] = False
        data["restored"] = []
        data["errors"] = []
        data["restore_attempts"] = 0
        options = data.get("options") or {}
        contains = data.get("contains") or {}
        if options.get("restore_database") and contains.get("postgresql") and not self._find_psql():
            data["success"] = False
            data["errors"].append("当前环境未找到 psql，无法自动恢复 PostgreSQL 数据库。")
            return data

        try:
            emergency = self._create_signal_backup()
            emergency_path = emergency.get("zip_file") or ""
            if not emergency.get("success") or not emergency_path or not Path(emergency_path).exists():
                data["success"] = False
                data["errors"].append("恢复前应急备份创建失败，已取消恢复。")
                return data
            data["emergency_backup"] = emergency_path
        except Exception as err:
            data["success"] = False
            data["errors"].append(f"恢复前应急备份创建失败：{err}")
            return data

        archive_path = Path(data["archive"]["path"])
        config_path = Path(settings.CONFIG_PATH)
        backup_root = Path(self._backup_path or "/config/plugins/Signal/Backup")
        try:
            with tempfile.TemporaryDirectory(prefix="signal_restore_", dir=str(backup_root)) as tmp:
                tmp_dir = Path(tmp)
                with zipfile.ZipFile(archive_path, "r") as zf:
                    self._validate_backup_zip_entries(zf)
                    for name in data.get("entries") or []:
                        if name.endswith("/"):
                            continue
                        target = tmp_dir / name
                        target.parent.mkdir(parents=True, exist_ok=True)
                        with zf.open(name) as src, target.open("wb") as dst:
                            shutil.copyfileobj(src, dst)
                if options.get("restore_config"):
                    for name in ("category.yaml", "app.env"):
                        src = tmp_dir / name
                        if src.exists():
                            data["restore_attempts"] += 1
                            shutil.copy2(src, config_path / name)
                            data["restored"].append(name)
                if options.get("restore_cookies") and (tmp_dir / "cookies").exists():
                    data["restore_attempts"] += 1
                    target = config_path / "cookies"
                    if target.exists():
                        shutil.rmtree(target)
                    shutil.copytree(tmp_dir / "cookies", target)
                    data["restored"].append("cookies/")
                if options.get("restore_database"):
                    sqlite_files = [name for name in (data.get("contains", {}).get("sqlite") or []) if (tmp_dir / name).is_file()]
                    for name in sqlite_files:
                        data["restore_attempts"] += 1
                        shutil.copy2(tmp_dir / name, config_path / name)
                        data["restored"].append(name)
                    if contains.get("postgresql"):
                        data["restore_attempts"] += 1
                        ok, msg = self._restore_postgresql_backup(tmp_dir / "postgresql_backup.sql")
                        if ok:
                            data["restored"].append("postgresql_backup.sql")
                        else:
                            data["errors"].append(msg)
        except Exception as err:
            data["errors"].append(str(err))

        data["success"] = not data.get("errors")
        text = self._format_backup_restore_text(data)
        self._save_task_result("备份恢复", bool(data.get("success")), 0 if data.get("success") else 1, text)
        return data

    @staticmethod
    def _backup_restore_outcome(data: Dict[str, Any]) -> str:
        restored = len(data.get("restored") or [])
        archive = (data.get("archive") or {}).get("name") or "所选备份包"
        if data.get("success"):
            return f"已从 {archive} 恢复 {restored} 项数据"
        errors = data.get("errors") or []
        detail = str(errors[0])[:120] if errors else "恢复未完成"
        return f"备份恢复失败：{detail}"

    def _restore_postgresql_backup(self, sql_path: Path) -> Tuple[bool, str]:
        psql = self._find_psql()
        if not psql:
            return False, "当前环境未找到 psql，无法自动恢复 PostgreSQL 数据库。"
        if not sql_path.exists():
            return False, "备份包缺少 postgresql_backup.sql。"
        env = os.environ.copy()
        env["PGPASSWORD"] = str(getattr(settings, "DB_POSTGRESQL_PASSWORD", ""))
        cmd = [
            psql,
            "-h", str(getattr(settings, "DB_POSTGRESQL_HOST", "localhost")),
            "-p", str(getattr(settings, "DB_POSTGRESQL_PORT", "5432")),
            "-U", str(getattr(settings, "DB_POSTGRESQL_USERNAME", "")),
            "-d", str(getattr(settings, "DB_POSTGRESQL_DATABASE", "")),
            "-f", str(sql_path),
        ]
        try:
            result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=600, check=False)
        except Exception as err:
            return False, f"PostgreSQL 恢复执行失败：{err}"
        if result.returncode == 0:
            return True, "psql 恢复成功"
        return False, f"PostgreSQL 恢复失败：{(result.stderr or result.stdout or '').strip()[-300:]}"

    @staticmethod
    def _find_psql() -> str:
        found = shutil.which("psql")
        if found:
            return found
        import glob as _glob
        for pattern in ("/usr/bin/psql", "/usr/local/bin/psql",
                        "/usr/lib/postgresql/*/bin/psql", "/opt/homebrew/bin/psql",
                        "/opt/homebrew/opt/postgresql*/bin/psql"):
            for p in sorted(_glob.glob(pattern)):
                if os.path.isfile(p) and os.access(p, os.X_OK):
                    return p
        return ""

    def _format_backup_restore_text(self, data: Dict[str, Any]) -> str:
        lines = [
            "🧰 MP 运维助手备份恢复",
            f"⦁ 状态：{'成功' if data.get('success') else '异常'}",
            f"⦁ 备份包：{(data.get('archive') or {}).get('name') or '未选择'}",
        ]
        if data.get("dry_run"):
            lines.append("⦁ 模式：预览，未覆盖文件")
        if data.get("emergency_backup"):
            lines.append(f"⦁ 应急备份：{Path(data['emergency_backup']).name}")
        if data.get("selected"):
            lines.append("将恢复：")
            lines.extend([f"⦁ {x}" for x in data.get("selected", [])[:8]])
        if data.get("restored"):
            lines.append("已恢复：")
            lines.extend([f"⦁ {x}" for x in data.get("restored", [])[:8]])
        if data.get("warnings"):
            lines.append("提示：")
            lines.extend([f"⦁ {str(x)[:160]}" for x in data.get("warnings", [])[:5]])
        if data.get("errors"):
            lines.append("异常：")
            lines.extend([f"⦁ {str(x)[:160]}" for x in data.get("errors", [])[:5]])
        return "\n".join(lines)

    def _create_signal_backup(self) -> Dict[str, Any]:
        backup_path = Path(self._backup_path or "/config/plugins/Signal/Backup")
        backup_path.mkdir(parents=True, exist_ok=True)
        config_path = Path(settings.CONFIG_PATH)
        stamp = datetime.now().strftime("%Y%m%d%H%M%S")
        work_dir = backup_path / f"bk_{stamp}"
        work_dir.mkdir(parents=True, exist_ok=True)
        copied = []
        errors = []
        warnings = []
        zip_path = ""
        try:
            for name in ["category.yaml", "app.env"]:
                src = config_path / name
                if src.exists():
                    shutil.copy2(src, work_dir / src.name)
                    copied.append(str(src))
            cookies = config_path / "cookies"
            if cookies.exists():
                shutil.copytree(cookies, work_dir / "cookies", dirs_exist_ok=True)
                copied.append(str(cookies))
            if str(settings.DB_TYPE).lower() == "sqlite":
                for db_file in config_path.glob("user.db*"):
                    if db_file.is_file():
                        shutil.copy2(db_file, work_dir / db_file.name)
                        copied.append(str(db_file))
            elif str(settings.DB_TYPE).lower() == "postgresql":
                dump_target = work_dir / "postgresql_backup.sql"
                ok, msg = self._dump_postgresql(dump_target)
                if ok:
                    copied.append(f"postgresql_backup.sql（{msg}）")
                else:
                    warnings.append(msg)
            manifest = {"created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "db_type": str(settings.DB_TYPE), "copied": copied, "errors": errors, "warnings": warnings}
            (work_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
            zip_base = str(work_dir)
            zip_path = shutil.make_archive(zip_base, "zip", str(work_dir))
        finally:
            if work_dir.exists():
                shutil.rmtree(work_dir, ignore_errors=True)

        removed = self._cleanup_old_backups(backup_path)

        # WebDAV 远端备份
        webdav_success = False
        webdav_error = ""
        if self._backup_webdav_enabled and zip_path and Path(zip_path).exists():
            webdav_success, webdav_error = self._upload_to_webdav(zip_path)

        success = Path(zip_path).exists() and not errors
        status = self._build_backup_status()
        status.update({
            "success": success,
            "zip_file": zip_path,
            "copied": copied,
            "errors": errors,
            "warnings": warnings,
            "removed": removed,
            "webdav_enabled": self._backup_webdav_enabled,
            "webdav_success": webdav_success,
            "webdav_error": webdav_error,
        })
        return status

    def _webdav_client_options(self) -> Dict[str, Any]:
        if not self._backup_webdav_hostname:
            raise ValueError("WebDAV 地址未配置")
        options = {
            "webdav_hostname": self._backup_webdav_hostname.rstrip("/"),
            "webdav_login": self._backup_webdav_login,
            "webdav_password": self._backup_webdav_password,
            "disable_check": self._backup_webdav_disable_check,
        }
        if self._backup_webdav_digest_auth:
            options["webdav_auth_type"] = "digest"
        return options

    def _create_webdav_client(self):
        try:
            from webdav3.client import Client
        except ImportError:
            raise RuntimeError("webdav3-client 未安装，请运行: pip install webdav3-client")
        client = Client(self._webdav_client_options())
        if not self._backup_webdav_disable_check and not client.check():
            raise RuntimeError("WebDAV 连接测试失败")
        return client

    @staticmethod
    def _normalize_webdav_archive_name(archive: Any) -> str:
        raw = str(archive or "").strip().replace("\\", "/")
        name = PurePosixPath(raw).name
        if not name or name != raw.strip("/") and "/" in raw.strip("/"):
            raise ValueError("只允许选择 WebDAV 根目录内的 bk_*.zip 备份包。")
        if not name.startswith("bk_") or not name.endswith(".zip"):
            raise ValueError("只允许恢复 WebDAV 根目录内的 bk_*.zip 备份包。")
        return name

    def _list_webdav_backup_archives(self) -> List[Dict[str, Any]]:
        client = self._create_webdav_client()
        remote_files = client.list() or []
        files: List[Dict[str, Any]] = []
        seen = set()
        for item in remote_files:
            try:
                name = self._normalize_webdav_archive_name(item)
            except Exception:
                continue
            if name in seen:
                continue
            seen.add(name)
            size = 0
            mtime = ""
            try:
                info = client.info(name) or {}
                size = self._safe_int(info.get("size") or info.get("content_length"), 0, 0)
                mtime = str(info.get("modified") or info.get("mtime") or "")
            except Exception:
                pass
            files.append({
                "name": name,
                "path": name,
                "size": size,
                "size_text": self._format_bytes(size) if size else "",
                "mtime": mtime,
                "source": "webdav",
            })
        files.sort(key=lambda x: x["name"], reverse=True)
        return files

    def _download_webdav_backup_archive(self, archive: Any) -> Path:
        name = self._normalize_webdav_archive_name(archive)
        backup_root = Path(self._backup_path or "/config/plugins/Signal/Backup").resolve(strict=False)
        backup_root.mkdir(parents=True, exist_ok=True)
        target = (backup_root / name).resolve(strict=False)
        if backup_root != target and backup_root not in target.parents:
            raise ValueError("WebDAV 备份包只能下载到配置的备份目录内。")
        tmp_target = target.with_name(f".webdav_{target.name}.download")
        if tmp_target.exists():
            tmp_target.unlink()
        client = self._create_webdav_client()
        client.download_sync(remote_path=name, local_path=str(tmp_target))
        self._inspect_backup_archive(tmp_target)
        tmp_target.replace(target)
        return target

    def _upload_to_webdav(self, local_zip_path: str) -> Tuple[bool, str]:
        """上传备份到 WebDAV"""
        if not self._backup_webdav_hostname:
            return False, "WebDAV 地址未配置"
        try:
            from webdav3.exceptions import WebDavException
        except ImportError:
            error_msg = "webdav3-client 未安装，请运行: pip install webdav3-client"
            return False, error_msg

        try:
            client = self._create_webdav_client()

            # 上传文件
            remote_path = Path(local_zip_path).name
            client.upload_sync(remote_path=remote_path, local_path=local_zip_path)

            # 清理远端旧备份
            try:
                remote_files = client.list()
                backup_files = [f for f in remote_files if f.startswith("bk_") and f.endswith(".zip")]
                backup_files.sort(reverse=True)
                for old_file in backup_files[self._backup_webdav_max_count:]:
                    try:
                        client.clean(old_file)
                    except Exception as e:
                        logger.warning(f"清理远端旧备份 {old_file} 失败：{e}")
            except Exception as e:
                logger.warning(f"清理远端旧备份失败：{e}")

            return True, "上传成功"
        except WebDavException as e:
            error_msg = f"WebDAV 错误：{str(e)[:200]}"
            logger.error(f"WebDAV 备份失败：{e}")
            return False, error_msg
        except Exception as e:
            error_msg = f"上传失败：{str(e)[:200]}"
            logger.error(f"WebDAV 备份异常：{e}")
            return False, error_msg

    def _dump_postgresql(self, target: Path) -> Tuple[bool, str]:
        """导出 PostgreSQL：优先 pg_dump（PATH 或常见安装目录），无则用 SQLAlchemy 兜底。
        返回 (是否导出, 说明)。导不出时调用方按“提示/警告”处理，不算备份失败。"""
        pg_dump = self._find_pg_dump()
        if pg_dump:
            err = ""
            try:
                env = os.environ.copy()
                env["PGPASSWORD"] = str(settings.DB_POSTGRESQL_PASSWORD)
                cmd = [pg_dump, "-h", str(settings.DB_POSTGRESQL_HOST), "-p", str(settings.DB_POSTGRESQL_PORT),
                       "-U", str(settings.DB_POSTGRESQL_USERNAME), "-d", str(settings.DB_POSTGRESQL_DATABASE), "-f", str(target)]
                result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=600, check=False)
                if result.returncode == 0 and target.exists():
                    return True, "pg_dump"
                err = (result.stderr or result.stdout or "pg_dump 执行失败")[-300:]
            except Exception as e:
                err = str(e)[:300]
            ok2, msg2 = self._dump_postgresql_python(target)
            if ok2:
                return True, f"SQLAlchemy 兜底（pg_dump 失败：{err[:80]}）"
            return False, f"PostgreSQL 未导出：pg_dump 失败（{err}）；SQLAlchemy 兜底也失败（{msg2}）。配置文件已正常备份。"
        # 无 pg_dump：SQLAlchemy 兜底
        ok2, msg2 = self._dump_postgresql_python(target)
        if ok2:
            return True, "SQLAlchemy 兜底（容器内无 pg_dump）"
        return False, ("PostgreSQL 未导出：容器内无 pg_dump，SQLAlchemy 兜底失败（" + msg2 +
                       "）。配置文件已正常备份；如需完整数据库备份请在容器内安装 postgresql-client（提供 pg_dump）。")

    @staticmethod
    def _find_pg_dump() -> str:
        """在 PATH 与常见安装目录中查找 pg_dump，找不到返回空串。"""
        found = shutil.which("pg_dump")
        if found:
            return found
        import glob as _glob
        for pattern in ("/usr/bin/pg_dump", "/usr/local/bin/pg_dump",
                        "/usr/lib/postgresql/*/bin/pg_dump", "/opt/homebrew/bin/pg_dump",
                        "/opt/homebrew/opt/postgresql*/bin/pg_dump"):
            for p in sorted(_glob.glob(pattern)):
                if os.path.isfile(p) and os.access(p, os.X_OK):
                    return p
        return ""

    @staticmethod
    def _sql_literal(v: Any) -> str:
        """把一个 Python 值转成 SQL 字面量（单引号转义防注入/坏 SQL）。"""
        if v is None:
            return "NULL"
        if isinstance(v, bool):
            return "TRUE" if v else "FALSE"
        if isinstance(v, (int, float)):
            return repr(v)
        if isinstance(v, (bytes, bytearray)):
            return "'\\x" + bytes(v).hex() + "'"
        return "'" + str(v).replace("'", "''") + "'"

    def _dump_postgresql_python(self, target: Path) -> Tuple[bool, str]:
        """无 pg_dump 时，用 MoviePilot 已有的 SQLAlchemy 引擎导出（CREATE TABLE + INSERT）。
        尽力而为：全程 try/except，失败只返回 (False, 原因)，绝不影响其它备份。
        注：应急数据导出，可能缺少部分序列/约束，正式恢复仍建议 pg_dump。"""
        try:
            from app.db import Engine
            from sqlalchemy import MetaData, select
            from sqlalchemy.schema import CreateTable
        except Exception as e:
            return False, f"无法加载 SQLAlchemy 引擎：{str(e)[:120]}"
        try:
            meta = MetaData()
            meta.reflect(bind=Engine)
            if not meta.tables:
                return False, "未反射到任何表"
            out = ["-- MoviePilot PostgreSQL 应急备份（Signal SQLAlchemy 导出，无 pg_dump）",
                   "-- 含表结构与数据，可能缺少部分序列/约束；正式恢复建议用 pg_dump。", ""]
            with Engine.connect() as conn:
                for table in meta.sorted_tables:
                    try:
                        out.append(str(CreateTable(table).compile(Engine)).strip() + ";")
                    except Exception:
                        pass
                    try:
                        rows = conn.execute(select(table)).fetchall()
                    except Exception:
                        rows = []
                    collist = ", ".join('"' + c.name + '"' for c in table.columns)
                    for row in rows:
                        vals = ", ".join(self._sql_literal(v) for v in row)
                        out.append(f'INSERT INTO "{table.name}" ({collist}) VALUES ({vals});')
                    out.append("")
            target.write_text("\n".join(out), encoding="utf-8")
            return (target.exists() and target.stat().st_size > 0), "已导出表结构+数据"
        except Exception as e:
            return False, f"SQLAlchemy 导出失败：{str(e)[:200]}"

    def _cleanup_old_backups(self, backup_path: Path) -> List[str]:
        keep = max(1, int(self._backup_keep_count or 5))
        files = sorted([x for x in backup_path.glob("bk_*.zip") if x.is_file()], key=lambda x: x.stat().st_mtime, reverse=True)
        removed = []
        for item in files[keep:]:
            try:
                removed.append(item.name)
                item.unlink()
            except Exception as err:
                logger.warning(f"Signal 删除旧备份失败 {item}: {err}")
        return removed

    def _format_backup_status_text(self, data: Dict[str, Any]) -> str:
        lines = [
            "🗄️ MP 运维助手自动备份",
            "⦁ 模式：直接接替 AutoBackup",
            f"⦁ 状态：{'成功' if data.get('success', True) else '异常'}",
            f"⦁ 路径：{data.get('back_path')}",
            f"⦁ 保留数量：{data.get('keep_count')}",
            f"⦁ 当前备份：{data.get('backup_count', 0)} 个 / {data.get('backup_size_text')}",
        ]
        if data.get("zip_file"):
            lines.append(f"⦁ 本次备份：{Path(data['zip_file']).name}")
        if data.get("removed"):
            lines.append(f"⦁ 清理旧备份：{len(data.get('removed') or [])} 个")
        if data.get("webdav_enabled"):
            if data.get("webdav_success"):
                lines.append("⦁ WebDAV 备份：成功")
            elif data.get("webdav_error"):
                lines.append(f"⦁ WebDAV 备份：失败 - {data.get('webdav_error')[:60]}")
            else:
                lines.append("⦁ WebDAV 备份：未执行")
        if data.get("latest"):
            lines.append("最近备份：")
            for item in data["latest"][:3]:
                lines.append(f"⦁ {item['name']}｜{item['size_text']}｜{item['mtime']}")
        if data.get("warnings"):
            lines.append("提示：")
            lines.extend([f"⦁ {str(w)[:160]}" for w in data.get("warnings", [])[:5]])
        if data.get("errors"):
            lines.append("异常：")
            lines.extend([f"⦁ {str(e)[:120]}" for e in data.get("errors", [])[:5]])
        return "\n".join(lines)

    @staticmethod
    def _backup_outcome(data: Dict[str, Any]) -> str:
        if data.get("success"):
            copied = len(data.get("copied") or [])
            removed = len(data.get("removed") or [])
            if not copied and not removed:
                return "备份已创建"
            suffix = f"，清理 {removed} 份" if removed else ""
            return f"备份 {copied} 项{suffix}"
        errors = data.get("errors") or []
        detail = str(errors[0])[:120] if errors else "备份包创建失败"
        return f"配置备份失败：{detail}"

    def run_backup_scheduled(self) -> bool:
        """Run the configured backup from the scheduler."""
        return self.run_backup(scheduled=True)

    def run_backup(self, scheduled: bool = False) -> bool:
        ok, _ = self._guard_task("自动备份", "backup")
        if not ok:
            return False
        try:
            data = self._create_signal_backup()
            text = self._format_backup_status_text(data)
            if self._fusion_notify_enabled:
                self._notify_fusion_task_outcome(
                    mtype=NotificationType.Plugin,
                    title="自动备份",
                    text=text,
                    outcome=self._backup_outcome(data),
                    success=bool(data.get("success")),
                    component="backup",
                    affected_owner="realtime-task-backup",
                )
            elif scheduled and self._task_outcome_notification_enabled(self._backup_notify):
                self._notify_fusion_task_outcome(
                    mtype=self._notification_type(self._backup_notify_type),
                    title="自动备份",
                    text=text,
                    outcome=self._backup_outcome(data),
                    success=bool(data.get("success")),
                    component="backup",
                )
            self._save_task_result("自动备份", bool(data.get("success")), 0 if data.get("success") else 1, text)
            return bool(data.get("success"))
        except Exception as err:
            text = f"自动备份执行异常：{err}"
            if self._fusion_notify_enabled:
                self._notify_fusion_task_outcome(
                    mtype=NotificationType.Plugin,
                    title="自动备份执行异常",
                    text=text,
                    outcome="自动备份执行异常",
                    success=False,
                    component="backup",
                    affected_owner="realtime-task-backup",
                )
            elif scheduled and self._task_outcome_notification_enabled(self._backup_notify):
                self._notify_fusion_task_outcome(
                    mtype=self._notification_type(self._backup_notify_type),
                    title="自动备份执行异常",
                    text=text,
                    outcome="自动备份执行异常",
                    success=False,
                    component="backup",
                )
            self._save_task_result("自动备份", False, -1, str(err))
            logger.error(f"Signal 自动备份执行失败：{err}")
            return False
