"""Manual and scheduled entry points for the unified Signal backup service."""

from __future__ import annotations

import tempfile
import uuid
from pathlib import Path
from typing import Any, Dict, Mapping

from app.log import logger
from app.schemas import NotificationType

from .backup_archive import BackupArchiveService
from .backup_models import BACKUP_OPERATION_LOCK, BackupOperation, BackupSettings
from .backup_restore import BackupRestoreService
from ..infrastructure.backup_targets import BackupTargetService


class BackupMixin:
    """Create one validated archive and deliver the same bytes to each target."""

    def _backup_settings(self) -> BackupSettings:
        source = getattr(self, "_backup_config", None)
        if isinstance(source, Mapping):
            return BackupSettings.from_config(source)
        return BackupSettings.from_config({
            "backup_enabled": getattr(self, "_backup_enabled", False),
            "backup_database_enabled": getattr(self, "_backup_database_enabled", False),
            "backup_cron": getattr(self, "_backup_cron", "0 4 * * 1"),
            "backup_keep_count": getattr(self, "_backup_keep_count", 5),
            "backup_path": getattr(self, "_backup_path", "/config/plugins/Signal/Backup"),
            "backup_notify": getattr(self, "_backup_notify", False),
            "backup_notify_type": getattr(self, "_backup_notify_type", "Plugin"),
            "backup_webdav_enabled": getattr(self, "_backup_webdav_enabled", False),
            "backup_webdav_hostname": getattr(self, "_backup_webdav_hostname", ""),
            "backup_webdav_login": getattr(self, "_backup_webdav_login", ""),
            "backup_webdav_password": getattr(self, "_backup_webdav_password", ""),
            "backup_webdav_digest_auth": getattr(self, "_backup_webdav_digest_auth", False),
            "backup_webdav_disable_check": getattr(self, "_backup_webdav_disable_check", False),
            "backup_webdav_max_count": getattr(self, "_backup_webdav_max_count", 5),
        })

    def _backup_restore_service(self) -> BackupRestoreService:
        return BackupRestoreService(self)

    def _set_backup_operation(self, operation: BackupOperation | None) -> None:
        if not hasattr(self, "_backup_operation_recent"):
            self._backup_operation_recent = []
        self._backup_operation_current = operation
        try:
            saver = getattr(self, "save_data", None)
            if callable(saver) and operation is not None:
                saver("backup_operation_recent", operation.to_dict())
        except Exception:
            pass

    def _finish_backup_operation(self, operation: BackupOperation) -> None:
        if not hasattr(self, "_backup_operation_recent"):
            self._backup_operation_recent = []
        self._backup_operation_current = None
        self._backup_operation_recent.append(operation.to_dict())
        self._backup_operation_recent = self._backup_operation_recent[-10:]
        try:
            saver = getattr(self, "save_data", None)
            if callable(saver):
                saver("backup_operation_recent", operation.to_dict())
        except Exception:
            pass

    def _build_backup_status(self) -> Dict[str, Any]:
        settings = self._backup_settings()
        archives = BackupTargetService(settings).local.list()
        total_size = sum(int(item.get("size") or 0) for item in archives)
        formatter = getattr(self, "_format_bytes", None)
        size_text = formatter(total_size) if callable(formatter) else f"{total_size} B"
        return {
            "enabled": settings.enabled,
            "cron": settings.cron,
            "back_path": settings.local_path,
            "keep_count": settings.local_keep_count,
            "backup_count": len(archives),
            "backup_size": total_size,
            "backup_size_text": size_text,
            "latest": archives[:5],
            "webdav_enabled": settings.webdav_enabled,
            "webdav_configured": settings.webdav.ready,
            "archive_format": "signal-backup/v2",
            "database_backup_enabled": settings.database_enabled,
            "database_included": settings.database_enabled,
            "complete_archive": settings.database_enabled,
        }

    def _create_signal_backup(self, trigger: str = "manual") -> Dict[str, Any]:
        settings = self._backup_settings()
        targets = BackupTargetService(settings)
        with tempfile.TemporaryDirectory(prefix="signal_backup_staging_") as temp:
            created = BackupArchiveService(self).create_archive(
                Path(temp),
                trigger=trigger,
                include_database=settings.database_enabled,
            )
            target_results = targets.deliver(Path(created["archive_path"]))
        successful = [item for item in target_results if item.get("success")]
        failed = [item for item in target_results if not item.get("success")]
        status = "success" if successful and not failed else "partial" if successful else "failed"
        local_result = next((item for item in successful if item.get("target") == "local"), None)
        result = self._build_backup_status()
        result.update({
            # ``success`` means every enabled target received the archive.
            # A locally usable archive is exposed separately so partial
            # delivery cannot be rendered as a green full success.
            "success": status == "success",
            "archive_created": True,
            "successful_targets": [str(item.get("target") or "") for item in successful],
            "partial": status == "partial",
            "status": status,
            "backup_id": created.get("backup_id"),
            "fingerprint": created.get("fingerprint"),
            "archive": created.get("descriptor"),
            "zip_file": (local_result or {}).get("path") or "",
            "targets": target_results,
            "copied": ["moviepilot", "plugins", "offline"],
            "errors": [str(item.get("error") or "目标投递失败") for item in failed],
            "warnings": list(created.get("warnings") or []),
            "database_included": bool(created.get("database_included")),
            "complete_archive": bool(created.get("database_included")),
        })
        return result

    @staticmethod
    def _backup_outcome(data: Dict[str, Any]) -> str:
        target_labels = {"local": "本地", "webdav": "WebDAV"}

        def label(item: Dict[str, Any]) -> str:
            return target_labels.get(str(item.get("target") or ""), str(item.get("target") or "目标"))

        def detail(item: Dict[str, Any]) -> str:
            text = str(item.get("error") or "目标投递失败").strip()
            for prefix in (f"{label(item)}：", f"{label(item)} "):
                if text.startswith(prefix):
                    return text[len(prefix):].strip()
            return text

        database_included = bool(data.get("database_included", data.get("complete_archive")))
        targets = list(data.get("targets") or [])
        successful = [item for item in targets if item.get("success")]
        failed = [item for item in targets if not item.get("success")]
        if data.get("status") == "success":
            labels = "、".join(label(item) for item in successful) or "全部启用目标"
            if database_included:
                return f"完整备份已完成：{labels}投递成功。"
            return f"应用备份已完成（不含数据库）：{labels}投递成功。"
        if data.get("status") == "partial":
            success_text = "、".join(f"{label(item)}备份成功" for item in successful) or "归档已创建"
            failed_item = failed[0] if failed else {}
            failed_status = str(failed_item.get("status") or "failed")
            failure_word = "未投递" if failed_status == "not_configured" else "投递失败"
            reason = detail(failed_item).rstrip("。.!！")
            return f"{success_text}；{label(failed_item)} {failure_word}：{reason}。"
        errors = data.get("errors") or []
        prefix = "完整备份" if database_included else "应用备份"
        return f"{prefix}失败：{str(errors[0])[:120] if errors else '没有目标接收归档'}"

    def _format_backup_status_text(self, data: Dict[str, Any]) -> str:
        database_included = bool(data.get("database_included", data.get("complete_archive")))
        lines = [
            "🗄️ Signal 完整备份" if database_included else "🗄️ Signal 应用备份（不含数据库）",
            f"⦁ 状态：{data.get('status') or ('成功' if data.get('success') else '失败')}",
            f"⦁ 归档：{(data.get('archive') or {}).get('name') or '未生成'}",
            "⦁ 内容：MoviePilot 配置、逐插件状态、离线恢复材料"
            + ("、活动数据库" if database_included else "（数据库未包含）"),
        ]
        for target in data.get("targets") or []:
            label = "本地" if target.get("target") == "local" else "WebDAV"
            target_status = "成功" if target.get("success") else "未配置" if target.get("status") == "not_configured" else "失败"
            lines.append(f"⦁ {label}：{target_status}")
        for warning in (data.get("warnings") or [])[:3]:
            lines.append(f"⦁ 提示：{str(warning)[:160]}")
        for error in (data.get("errors") or [])[:3]:
            lines.append(f"⦁ 异常：{str(error)[:160]}")
        return "\n".join(lines)

    def run_backup_scheduled(self) -> bool:
        return self.run_backup(scheduled=True)

    def run_backup(self, scheduled: bool = False, notify: bool = False) -> bool:
        ok, _ = self._guard_task("自动备份", "backup")
        if not ok:
            return False
        if not BACKUP_OPERATION_LOCK.acquire(blocking=False):
            message = "已有备份或恢复操作正在执行，本次请求未重复启动。"
            self._last_backup_result = {
                **self._build_backup_status(),
                "success": False,
                "partial": False,
                "status": "conflict",
                "conflict": True,
                "errors": [message],
                "targets": [],
            }
            self._save_task_result("自动备份", False, 2, message)
            return False
        operation = BackupOperation(operation_id=str(uuid.uuid4()), kind="backup")
        self._set_backup_operation(operation)
        try:
            data = self._create_signal_backup(trigger="scheduled" if scheduled else "manual")
            self._last_backup_result = data
            operation.backup_id = str(data.get("backup_id") or "")
            operation.components = [
                {
                    "component": "backup_target",
                    "target": item.get("target"),
                    "status": item.get("status") or ("success" if item.get("success") else "failed"),
                    "error": item.get("error") or "",
                }
                for item in data.get("targets") or []
            ]
            operation.errors = list(data.get("errors") or [])
            operation.warnings = list(data.get("warnings") or [])
            operation.finish(
                status=str(data.get("status") or ("success" if data.get("success") else "failed")),
                message=self._backup_outcome(data),
            )
            text = self._format_backup_status_text(data)
            success = bool(data.get("success"))
            if self._fusion_notify_enabled:
                self._notify_fusion_task_outcome(
                    mtype=NotificationType.Plugin,
                    title="自动备份",
                    text=text,
                    outcome=self._backup_outcome(data),
                    success=success,
                    component="backup",
                    task_key="backup",
                    task_group="维护任务",
                    affected_owner="realtime-task-backup",
                )
            elif (scheduled or notify) and self._task_outcome_notification_enabled(self._backup_notify):
                self._notify_fusion_task_outcome(
                    mtype=self._notification_type(self._backup_notify_type),
                    title="自动备份",
                    text=text,
                    outcome=self._backup_outcome(data),
                    success=success,
                    component="backup",
                    task_key="backup",
                    task_group="维护任务",
                )
            self._save_task_result("自动备份", success, 0 if success else 1, text)
            return success
        except Exception as err:
            text = f"自动备份执行异常：{err}"
            try:
                status = self._build_backup_status()
            except Exception:
                status = {}
            self._last_backup_result = {
                **status,
                "success": False,
                "partial": False,
                "status": "failed",
                "errors": [str(err)],
                "targets": [],
            }
            operation.errors = [str(err)]
            operation.finish(status="failed", message=text)
            self._save_task_result("自动备份", False, -1, text)
            logger.error(f"Signal 自动备份执行失败：{err}")
            if (scheduled or notify) and self._task_outcome_notification_enabled(self._backup_notify):
                self._notify_fusion_task_outcome(
                    mtype=self._notification_type(self._backup_notify_type),
                    title="自动备份执行异常",
                    text=text,
                    outcome="自动备份执行异常",
                    success=False,
                    component="backup",
                    task_key="backup",
                    task_group="维护任务",
                )
            return False
        finally:
            self._finish_backup_operation(operation)
            BACKUP_OPERATION_LOCK.release()
