import re
from datetime import datetime
from typing import Any, Dict, Optional

from app.core.config import settings
from app.log import logger


class MpApiMixin:
    """HTTP API endpoint methods exposed through MoviePilot plugin get_api()."""

    def api_preview_daily_report(self) -> Dict[str, Any]:
        ok, msg = self._can_run_task("每日汇报")
        if not ok:
            return {"code": 1, "msg": msg, "data": self._skipped_data(msg), "text": msg}
        try:
            text = self._build_daily_report_message(preview=True)
            data = {
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "template": "2026-06-20.card-v2-baseline-guard",
                "sent": False,
                "success": True,
                "chars": len(text or ""),
                "sections": self._count_report_sections(text or ""),
                "preview": text,
                "telegram_rich_message": self._build_daily_report_telegram_rich_message(preview=True, text=text),
                "error": "",
            }
            return {"code": 0, "msg": "每日汇报预览已生成", "data": data, "text": text}
        except Exception as err:
            return {"code": 1, "msg": f"每日汇报预览失败：{err}", "data": {}, "text": ""}

    def api_run_daily_report(self) -> Dict[str, Any]:
        return self._api_run_task("每日汇报", self.run_daily_report, "daily_report")

    def api_create_tg_console_card(self, trigger: str = "manual") -> Dict[str, Any]:
        ok, msg = self._can_run_task("融合通知卡", "fusion_notify")
        if not ok:
            self._save_task_result("融合通知卡", False, 2, msg)
            return {"code": 1, "msg": msg, "data": self._skipped_data(msg)}
        token, chat_id, _source = self._resolve_daily_report_telegram_config()
        if not token or not chat_id:
            msg = "融合通知 Bot Token/Chat ID 未配置"
            self._save_task_result("融合通知卡", False, 1, msg)
            state = self._tg_console_state(chat_id=chat_id)
            state["last_error"] = msg
            self._save_tg_console_state(state)
            return {"code": 1, "msg": msg, "data": self._tg_console_action_status_data(1, msg)}
        state = self._new_tg_console_card_state(chat_id=chat_id, trigger=trigger)
        self._prepare_tg_console_v7_loading(state)
        try:
            ok = self._tg_console_upsert_card(token, chat_id, state)
        except Exception as err:
            msg = f"融合通知卡创建异常：{self._telegram_safe_error(err, limit=500)}"
            state["last_error"] = msg
            self._save_tg_console_state(state)
            self._save_task_result("融合通知卡", False, -1, msg)
            logger.warning(f"Signal {msg}")
            return {"code": 1, "msg": msg, "data": self._tg_console_action_status_data(1, msg)}
        if ok:
            self._refresh_fusion_columns(state)
            self._compose_tg_console_v7_model(state)
            ok = self._tg_console_upsert_card(token, chat_id, state)
        self._save_tg_console_state(state)
        if not ok:
            msg = self._tg_console_last_error or state.get("last_error") or "融合通知卡创建失败"
            self._save_task_result("融合通知卡", False, 1, msg)
            return {"code": 1, "msg": msg, "data": self._tg_console_action_status_data(1, msg)}
        message_id = state.get("message_id") or 0
        msg = f"融合通知卡已创建 #{message_id}" if message_id else "融合通知卡已创建"
        self._save_task_result("融合通知卡", True, 0, msg)
        return {"code": 0, "msg": msg, "data": self._tg_console_action_status_data(0, msg)}

    def api_run_subscribe_reminder(self) -> Dict[str, Any]:
        return self._api_run_task("订阅追新", self.run_subscribe_reminder, "subscribe_reminder")

    def api_run_today_transfer(self) -> Dict[str, Any]:
        ok, msg = self._can_run_task("今日入库", "daily_report")
        if not ok:
            self._save_task_result("今日入库", False, 2, msg)
            return {"code": 1, "msg": msg, "data": self._skipped_data(msg), "text": msg}
        text = self._build_today_transfer_report_text()
        if self._tg_console_enabled and not self._emit_console_report("today_transfer", "今日入库", text, level="success"):
            msg = self._tg_console_last_error or "融合通知今日入库更新失败"
            self._save_task_result("今日入库", False, 1, msg)
            return {"code": 1, "msg": msg, "text": text}
        self._save_task_result("今日入库", True, 0, text)
        return {"code": 0, "msg": "今日入库已刷新", "text": text}

    def api_run_health_check(self) -> Dict[str, Any]:
        ok, msg = self._can_run_task("健康巡查", "health_check")
        if not ok:
            self._save_task_result("健康巡查", False, 2, msg)
            return {"code": 1, "msg": msg, "data": self._skipped_data(msg)}
        self.run_health_check()
        data = self.get_data("last_health_check") or {}
        failed = 0
        match = re.search(r"发现\s*(\d+)\s*项异常", str(data.get("output") or ""))
        if match:
            failed = self._safe_int(match.group(1), 0, 0)
        if data.get("success") is False:
            msg = f"健康巡查已完成，发现 {failed or '若干'} 项异常。"
        else:
            msg = "健康巡查已完成，未发现异常。"
        return {"code": 0, "msg": msg}

    def api_run_mp_update(self) -> Dict[str, Any]:
        return self._api_run_task("主程序更新检查", self.run_mp_update_check, "mp_update")

    def api_run_mp_update_apply(self) -> Dict[str, Any]:
        return self._api_run_task("主程序更新执行", self.run_mp_update_apply, "mp_update")

    def api_dashboard(self) -> Dict[str, Any]:
        """仪表盘数据：插件总状态、各模块快照、最近健康巡查概览。"""
        try:
            tasks = []
            for item in self._task_snapshot():
                latest = item.get("latest") or {}
                tasks.append({
                    "key": item.get("key"),
                    "name": item.get("name"),
                    "icon": item.get("icon"),
                    "enabled": bool(item.get("enabled")),
                    "effective_enabled": bool(item.get("effective_enabled")),
                    "effective_state": item.get("effective_state") or {},
                    "state": item.get("state"),
                    "color": item.get("color"),
                    "next": item.get("next"),
                    "last_time": latest.get("time") or "",
                    "last_summary": self._task_result_summary(latest),
                })
            failed = [t for t in tasks if self._enabled and t["enabled"] and t["state"] == "失败"]
            health = self.get_data("last_health_check") or {}
            return {
                "code": 0,
                "data": {
                    "enabled": bool(self._enabled),
                    "summary": self._build_summary(),
                    "tasks": tasks,
                    "task_total": len(tasks),
                    "task_on": len([t for t in tasks if t["effective_enabled"]]),
                    "task_failed": len(failed),
                    "health": {
                        "time": health.get("time") or "",
                        "success": health.get("success"),
                        "output": health.get("output") or "",
                    },
                    "tg_console": self._tg_console_status_data(),
                },
            }
        except Exception as err:
            logger.error(f"仪表盘数据获取失败：{err}")
            return {"code": 1, "msg": f"仪表盘数据获取失败：{err}", "data": {}}

    def api_installed_plugins(self) -> Dict[str, Any]:
        """已安装插件列表，供插件卸载下拉选择（排除本插件自身）。"""
        try:
            from app.core.plugin import PluginManager
            plugins = PluginManager().get_local_plugins() or []
            items = []
            for p in plugins:
                pid = getattr(p, "id", None)
                if not pid or not getattr(p, "installed", False):
                    continue
                if str(pid).lower() == "signal":
                    continue
                name = getattr(p, "plugin_name", None) or pid
                version = getattr(p, "plugin_version", "") or ""
                items.append({
                    "value": pid,
                    "title": f"{name} v{version}" if version else str(name),
                })
            items.sort(key=lambda x: x["title"])
            return {"code": 0, "data": items}
        except Exception as err:
            logger.error(f"已安装插件列表获取失败：{err}")
            return {"code": 1, "msg": f"已安装插件列表获取失败：{err}", "data": []}

    def api_plugin_markets(self) -> Dict[str, Any]:
        """已配置的插件库仓库地址列表，供更新黑名单下拉多选。"""
        try:
            markets = self._valid_markets_list(settings.PLUGIN_MARKET)
            items = []
            for url in markets:
                short = url.rstrip("/").split("/")
                label = "/".join(short[-2:]) if len(short) >= 2 else url
                items.append({"value": url, "title": label})
            items.sort(key=lambda x: x["title"].lower())
            return {"code": 0, "data": items}
        except Exception as err:
            logger.error(f"插件库仓库列表获取失败：{err}")
            return {"code": 1, "msg": f"插件库仓库列表获取失败：{err}", "data": []}

    def api_preview_log_clean(self) -> Dict[str, Any]:
        ok, msg = self._can_run_task("日志清理", "log_clean")
        if not ok:
            return {"code": 1, "msg": msg, "data": self._skipped_data(msg), "text": msg}
        try:
            data = self._build_log_preview()
            return {"code": 0, "msg": "日志清理预览完成，未删除任何文件。", "data": data, "text": self._format_log_preview_text(data)}
        except Exception as err:
            logger.error(f"Signal 日志清理预览失败：{err}")
            return {"code": 1, "msg": f"日志清理预览失败：{err}", "data": {}, "text": ""}

    def api_run_log_clean(self) -> Dict[str, Any]:
        ok_guard, msg = self._can_run_task("日志清理", "log_clean")
        if not ok_guard:
            self._save_task_result("日志清理", False, 2, msg)
            return {"code": 1, "msg": msg, "data": self._skipped_data(msg)}
        ok = self.run_log_clean()
        return {"code": 0 if ok else 1, "msg": "插件日志清理执行成功" if ok else "插件日志清理执行失败，详情请查看插件日志。"}

    def api_run_backup(self) -> Dict[str, Any]:
        try:
            ok_guard, msg = self._can_run_task("自动备份", "backup")
            if not ok_guard:
                self._save_task_result("自动备份", False, 2, msg)
                return {"code": 1, "msg": msg, "data": self._skipped_data(msg, self._build_backup_status())}
            ok = self.run_backup()
            data = self._build_backup_status()
            return {"code": 0 if ok else 1, "msg": "自动备份执行成功" if ok else "自动备份执行失败，详情请查看插件日志。", "data": data}
        except Exception as err:
            logger.error(f"Signal 自动备份接口执行失败：{err}")
            try:
                self._save_task_result("自动备份", False, -1, str(err))
            except Exception as save_err:
                logger.error(f"Signal 自动备份失败结果保存异常：{save_err}")
            try:
                data = self._build_backup_status()
            except Exception as status_err:
                logger.error(f"Signal 自动备份状态读取失败：{status_err}")
                data = {}
            return {"code": 1, "msg": f"自动备份执行失败：{err}", "data": data}

    def api_backup_archives(self) -> Dict[str, Any]:
        ok, msg = self._can_run_task("备份恢复", "backup")
        if not ok:
            return {"code": 1, "msg": msg, "data": []}
        try:
            return {"code": 0, "msg": "备份包列表获取成功", "data": self._list_backup_archives()}
        except Exception as err:
            return {"code": 1, "msg": f"备份包列表获取失败：{err}", "data": []}

    def api_preview_backup_restore(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        ok, msg = self._can_run_task("备份恢复", "backup")
        if not ok:
            return {"code": 1, "msg": msg, "data": self._skipped_data(msg, {"errors": [msg]}), "text": msg}
        try:
            data = self._build_backup_restore_preview(payload or {})
            return {"code": 0, "msg": "备份恢复预览完成，未覆盖任何文件。", "data": data, "text": self._format_backup_restore_text(data)}
        except Exception as err:
            return {"code": 1, "msg": f"备份恢复预览失败：{err}", "data": {}, "text": ""}

    def api_run_backup_restore(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        ok_guard, msg = self._can_run_task("备份恢复", "backup")
        if not ok_guard:
            self._save_task_result("备份恢复", False, 2, msg)
            return {"code": 1, "msg": msg, "data": self._skipped_data(msg, {"errors": [msg]}), "text": msg}
        restore_payload = dict(payload or {})
        if restore_payload.get("confirm") is not True:
            msg = "备份恢复需要在配置页显式确认后才能执行。"
            self._save_task_result("备份恢复", False, 2, msg)
            return {"code": 1, "msg": msg, "data": self._restore_confirm_required_data(msg), "text": msg}
        data = self._run_backup_restore(restore_payload)
        ok = bool(data.get("success"))
        return {"code": 0 if ok else 1, "msg": "备份恢复执行成功" if ok else f"备份恢复执行失败：{'；'.join(data.get('errors') or [])}", "data": data, "text": self._format_backup_restore_text(data)}

    def api_webdav_backup_archives(self) -> Dict[str, Any]:
        ok, msg = self._can_run_task("WebDAV 备份恢复", "backup")
        if not ok:
            return {"code": 1, "msg": msg, "data": []}
        if not self._backup_webdav_enabled:
            return {"code": 1, "msg": "WebDAV 远端备份未启用。", "data": []}
        try:
            return {"code": 0, "msg": "WebDAV 备份包列表获取成功", "data": self._list_webdav_backup_archives()}
        except Exception as err:
            return {"code": 1, "msg": f"WebDAV 备份包列表获取失败：{err}", "data": []}

    def api_preview_webdav_backup_restore(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        ok, msg = self._can_run_task("WebDAV 备份恢复", "backup")
        if not ok:
            return {"code": 1, "msg": msg, "data": self._skipped_data(msg, {"errors": [msg]}), "text": msg}
        if not self._backup_webdav_enabled:
            return {"code": 1, "msg": "WebDAV 远端备份未启用。", "data": {}, "text": ""}
        try:
            restore_payload = dict(payload or {})
            archive_path = self._download_webdav_backup_archive(restore_payload.get("archive") or restore_payload.get("name") or restore_payload.get("path"))
            restore_payload["archive"] = archive_path.name
            data = self._build_backup_restore_preview(restore_payload)
            data["source"] = "webdav"
            data["remote_archive"] = archive_path.name
            return {"code": 0, "msg": "WebDAV 备份恢复预览完成，未覆盖任何文件。", "data": data, "text": self._format_backup_restore_text(data)}
        except Exception as err:
            return {"code": 1, "msg": f"WebDAV 备份恢复预览失败：{err}", "data": {}, "text": ""}

    def api_run_webdav_backup_restore(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        ok_guard, msg = self._can_run_task("WebDAV 备份恢复", "backup")
        if not ok_guard:
            self._save_task_result("WebDAV 备份恢复", False, 2, msg)
            return {"code": 1, "msg": msg, "data": self._skipped_data(msg, {"errors": [msg]}), "text": msg}
        if not self._backup_webdav_enabled:
            msg = "WebDAV 远端备份未启用。"
            self._save_task_result("WebDAV 备份恢复", False, 2, msg)
            return {"code": 1, "msg": msg, "data": {"success": False, "errors": [msg]}, "text": msg}
        restore_payload = dict(payload or {})
        if restore_payload.get("confirm") is not True:
            msg = "WebDAV 备份恢复需要在配置页显式确认后才能执行。"
            self._save_task_result("WebDAV 备份恢复", False, 2, msg)
            data = self._restore_confirm_required_data(msg)
            data["source"] = "webdav"
            return {"code": 1, "msg": msg, "data": data, "text": msg}
        try:
            archive_path = self._download_webdav_backup_archive(restore_payload.get("archive") or restore_payload.get("name") or restore_payload.get("path"))
            restore_payload["archive"] = archive_path.name
            data = self._run_backup_restore(restore_payload)
            data["source"] = "webdav"
            data["remote_archive"] = archive_path.name
        except Exception as err:
            data = {"success": False, "dry_run": False, "errors": [str(err)], "warnings": [], "restored": [], "emergency_backup": "", "source": "webdav"}
        ok = bool(data.get("success"))
        return {"code": 0 if ok else 1, "msg": "WebDAV 备份恢复执行成功" if ok else f"WebDAV 备份恢复执行失败：{'；'.join(data.get('errors') or [])}", "data": data, "text": self._format_backup_restore_text(data)}

    def api_preview_updates(self) -> Dict[str, Any]:
        ok, msg = self._can_run_task("主程序更新检查", "mp_update")
        if not ok:
            return {"code": 1, "msg": msg, "data": self._skipped_data(msg), "text": msg}
        try:
            data = self._build_update_status()
            return {"code": 0, "msg": "更新状态预览完成，未执行更新或重启。", "data": data, "text": self._format_update_status_text(data)}
        except Exception as err:
            logger.error(f"Signal 更新状态预览失败：{err}")
            return {"code": 1, "msg": f"更新状态预览失败：{err}", "data": {}, "text": ""}

    def api_preview_market_update(self) -> Dict[str, Any]:
        ok, msg = self._can_run_task("插件库更新", "market_update")
        if not ok:
            return {"code": 1, "msg": msg, "data": self._skipped_data(msg), "text": msg}
        try:
            data = self._build_market_update_status(apply=False)
            return {"code": 0, "msg": "插件库更新预览完成，未写入配置。", "data": data, "text": self._format_market_update_text(data)}
        except Exception as err:
            return {"code": 1, "msg": f"插件库更新预览失败：{err}", "data": {}, "text": ""}

    def api_run_market_update(self) -> Dict[str, Any]:
        ok_guard, msg = self._can_run_task("插件库更新", "market_update")
        if not ok_guard:
            self._save_task_result("插件库更新", False, 2, msg)
            return {"code": 1, "msg": msg, "data": self._skipped_data(msg, self._build_market_status())}
        ok = self.run_market_update()
        data = self._build_market_status()
        return {"code": 0 if ok else 1, "msg": "插件库更新检查执行成功" if ok else "插件库更新检查失败，详情请查看插件日志。", "data": data}

    def api_preview_plugin_uninstall(self) -> Dict[str, Any]:
        ok, msg = self._can_run_task("插件卸载预览")
        if not ok:
            return {"code": 1, "msg": msg, "data": self._skipped_data(msg, {"blocked": msg, "uninstalled": []}), "text": msg}
        try:
            data = self._build_plugin_uninstall_status(clean=False)
            success = bool(data.get("success", True))
            if success:
                msg = "插件卸载预览完成，未执行卸载或删除文件。"
            else:
                reason = data.get("blocked") or "；".join((data.get("errors") or [])[:2]) or "请检查插件卸载配置。"
                msg = f"插件卸载预览未通过：{reason}"
            return {"code": 0 if success else 1, "msg": msg, "data": data, "text": self._format_plugin_uninstall_text(data)}
        except Exception as err:
            logger.error(f"Signal 插件卸载预览失败：{err}")
            return {"code": 1, "msg": f"插件卸载预览失败：{err}", "data": {}, "text": ""}

    def api_run_plugin_uninstall(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        ok_guard, msg = self._can_run_task("插件卸载")
        if not ok_guard:
            self._save_task_result("插件卸载", False, 2, msg)
            return {"code": 1, "msg": msg, "data": self._skipped_data(msg, {"blocked": msg, "uninstalled": []})}
        request_payload = dict(payload or {})
        if request_payload.get("plugin_uninstall_confirm") is not True:
            msg = "插件卸载属于高风险操作，需要在配置页显式确认后才能执行。"
            self._save_task_result("插件卸载", False, 2, msg)
            return {"code": 1, "msg": msg, "data": self._skipped_data(msg, {"blocked": msg, "uninstalled": []})}
        override = self._plugin_uninstall_config_from_payload(request_payload)
        ok, data = self._run_plugin_uninstall_clean(override=override)
        return {"code": 0 if ok else 1, "msg": "插件卸载执行成功" if ok else "插件卸载未执行或失败，详情请查看插件日志。", "data": data}

    def api_tg_console_status(self) -> Dict[str, Any]:
        return {"code": 0, "data": self._tg_console_status_data()}

    def api_preview_tg_console(self) -> Dict[str, Any]:
        token, chat_id, _source = self._resolve_daily_report_telegram_config()
        state = self._tg_console_state(chat_id=chat_id)
        rich_message = self._build_tg_console_rich_message(state)
        return {"code": 0, "msg": "TG 融合汇报卡预览已生成", "data": {"telegram_rich_message": rich_message}}

    def api_reset_tg_console_card(self) -> Dict[str, Any]:
        ok, msg = self._can_run_task("融合通知卡", "fusion_notify")
        if not ok:
            self._save_task_result("融合通知卡", False, 2, msg)
            return {"code": 1, "msg": msg, "data": self._skipped_data(msg)}
        token, chat_id, _source = self._resolve_daily_report_telegram_config()
        state = self._tg_console_state(chat_id=chat_id)
        state["message_id"] = 0
        state["notices"] = []
        state["reports"] = {}
        state["pending_actions"] = {}
        state["running_actions"] = {}
        state["last_error"] = ""
        self._save_tg_console_state(state)
        return {"code": 0, "msg": "TG 融合汇报卡状态已重置", "data": self._tg_console_status_data()}

    def api_run_seed_clean(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        ok, msg = self._can_run_task("自动删种", "seedclean")
        if not ok:
            self._save_task_result("自动删种", False, 2, msg)
            return {"code": 1, "msg": msg, "data": self._skipped_data(msg)}
        request = dict(payload or {})
        try:
            if request.get("seedclean_confirm") is not True:
                msg = "请确认本次自动删种操作"
                return {"code": 1, "msg": msg, "data": {"confirm_required": True}}
            success = bool(self.run_seed_clean())
            return {
                "code": 0 if success else 1,
                "msg": f"自动删种执行{'成功' if success else '失败'}",
                "data": {"confirmed": True},
            }
        except Exception as err:
            self._save_task_result("自动删种", False, -1, str(err))
            logger.error(f"Signal 自动删种执行异常：{err}")
            return {"code": 1, "msg": f"自动删种执行失败：{err}", "data": {}}

    def api_downloaders(self) -> Dict[str, Any]:
        """已配置下载器列表，供自动删种下拉选择。"""
        try:
            from app.helper.downloader import DownloaderHelper
            items = []
            for conf in (DownloaderHelper().get_configs() or {}).values():
                nm = getattr(conf, "name", None)
                if nm:
                    items.append({"value": nm, "title": nm})
            items.sort(key=lambda x: x["title"])
            return {"code": 0, "data": items}
        except Exception as err:
            logger.error(f"下载器列表获取失败：{err}")
            return {"code": 1, "msg": f"下载器列表获取失败：{err}", "data": []}

    def api_mediaservers(self) -> Dict[str, Any]:
        """已配置媒体服务器列表，供媒体库通知按服务器过滤。"""
        try:
            from app.helper.mediaserver import MediaServerHelper
            items = []
            for conf in (MediaServerHelper().get_configs() or {}).values():
                nm = getattr(conf, "name", None)
                if nm:
                    items.append({"value": nm, "title": nm})
            items.sort(key=lambda x: x["title"])
            return {"code": 0, "data": items}
        except Exception as err:
            logger.error(f"媒体服务器列表获取失败：{err}")
            return {"code": 1, "msg": f"媒体服务器列表获取失败：{err}", "data": []}

    def api_subfill_clear_history(self) -> Dict[str, Any]:
        return self._api_run_task("清理填充历史", self.run_subfill_clear_history, "subfill")

    def api_subfill_clear_handled(self) -> Dict[str, Any]:
        return self._api_run_task("清理已处理", self.run_subfill_clear_handled, "subfill")

    def api_site_stat_chart(self) -> Dict[str, Any]:
        """今日各站点上传/下载增量，供仪表盘饼图。"""
        ok, msg = self._can_run_task("站点数据统计", "site_stat")
        if not ok:
            data = self._skipped_data(msg, {"date": "", "basis": "skipped", "sites": [], "upload_total": 0, "download_total": 0})
            return {"code": 0, "msg": msg, "data": data}
        try:
            return {"code": 0, "data": self._site_increment_snapshot()}
        except Exception as err:
            logger.error(f"站点统计图数据获取失败：{err}")
            return {"code": 1, "msg": str(err), "data": {"date": "", "basis": "today", "sites": [], "upload_total": 0, "download_total": 0}}

    def run_site_stat_scheduled(self) -> bool:
        return self.api_run_site_stat(trigger="scheduled").get("code") == 0

    def api_run_site_stat(self, trigger: str = "manual") -> Dict[str, Any]:
        """刷新站点数据统计：站点快照来自 MoviePilot SiteOper，这里重新汇总并记录一次任务结果。"""
        ok, msg = self._can_run_task("站点数据统计", "site_stat")
        if not ok:
            self._save_task_result("站点数据统计", False, 2, msg)
            data = self._skipped_data(msg, {"date": "", "basis": "skipped", "sites": [], "upload_total": 0, "download_total": 0})
            return {"code": 1, "msg": msg, "data": data}
        try:
            chart = self.api_site_stat_chart()
            if (chart or {}).get("code", 0) != 0:
                msg = (chart or {}).get("msg") or "站点统计图数据获取失败"
                payload = (chart or {}).get("data") or {"date": "", "basis": "today", "sites": [], "upload_total": 0, "download_total": 0}
                self._save_task_result("站点数据统计", False, 1, msg)
                return {"code": 1, "msg": msg, "data": payload}
            payload = chart.get("data") or {}
            site_count = len(payload.get("sites") or [])
            upload = self._format_bytes(payload.get("upload_total", 0))
            download = self._format_bytes(payload.get("download_total", 0))
            label = "今日" if payload.get("basis") != "latest" else f"最近快照 {payload.get('date') or ''}".strip()
            text = f"已刷新 {site_count} 个站点｜{label}｜上传 {upload}｜下载 {download}" if site_count else "已刷新站点数据，暂无可用增量"
            self._save_task_result("站点数据统计", True, 0, text)
            if trigger == "scheduled":
                self._notify_or_console(
                    mtype=self._notification_type(self._site_stat_notify_type),
                    title="MP 运维助手 - 站点统计",
                    text=text,
                    component="site_stat",
                    owner="persistent-sites",
                    level="success",
                    payload=payload,
                )
            return {"code": 0, "msg": text, "data": payload}
        except Exception as err:
            self._save_task_result("站点数据统计", False, -1, str(err))
            logger.error(f"站点数据统计刷新失败：{err}")
            return {"code": 1, "msg": f"站点数据统计刷新失败：{err}", "data": {"date": "", "basis": "today", "sites": [], "upload_total": 0, "download_total": 0}}

    def api_preview_downloader_helper(self) -> Dict[str, Any]:
        ok, msg = self._can_run_task("下载器助手", "dltag")
        if not ok:
            return {"code": 1, "msg": msg, "data": self._skipped_data(msg)}
        try:
            return {"code": 0, "msg": "已检查失效任务", "data": self.downloader_helper_preview()}
        except Exception as err:
            return {"code": 1, "msg": f"下载器助手候选检查失败：{err}", "data": {}}

    def api_run_downloader_helper(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        ok, msg = self._can_run_task("下载器助手", "dltag")
        if not ok:
            self._save_task_result("下载器助手", False, 2, msg)
            return {"code": 1, "msg": msg, "data": self._skipped_data(msg)}
        request = dict(payload or {})
        try:
            cleanup_enabled = "cleanup" in self._dltag_task_set()
            preview = self.downloader_helper_preview() if cleanup_enabled else {"total": 0, "items": [], "scope_token": ""}
            if cleanup_enabled and preview.get("total") and request.get("dltag_confirm") is not True:
                return {"code": 0, "msg": "发现失效任务，请确认本次清理范围", "data": {**preview, "confirm_required": True}}
            if cleanup_enabled and preview.get("total"):
                if request.get("dltag_preview_token") != preview.get("scope_token"):
                    return {"code": 1, "msg": "失效任务范围已变化，请重新确认", "data": {**preview, "confirm_required": True}}
                confirmed = preview.get("items") or []
            else:
                confirmed = []
            success = self.run_downloader_helper(trigger="manual", confirmed_candidates=confirmed)
            result = {}
            try:
                loader = getattr(self, "get_data", None)
                if callable(loader):
                    result = loader(f"last_{self._slug('下载器助手')}") or {}
            except Exception:
                result = {}
            result_msg = result.get("output") or f"下载器助手执行{'完成' if success else '失败'}"
            return {"code": 0 if success else 1, "msg": result_msg, "data": {"confirm_required": False, "preview": preview, "result": result}}
        except Exception as err:
            self._save_task_result("下载器助手", False, -1, str(err))
            return {"code": 1, "msg": f"下载器助手执行失败：{err}", "data": {}}

    def api_run_downloader_tag(self, payload=None):
        ok, msg = self._can_run_task("种子打标签", "dltag")
        if not ok:
            self._save_task_result("种子打标签", False, 2, msg)
            return {"code": 1, "msg": msg, "data": self._skipped_data(msg)}
        try:
            success = self.run_downloader_tag()
            tag_msg = "种子打标签执行" + ("完成" if success else "失败")
            return {"code": 0 if success else 1, "msg": tag_msg, "data": {"confirm_required": False}}
        except Exception as err:
            self._save_task_result("种子打标签", False, -1, str(err))
            return {"code": 1, "msg": f"种子打标签执行失败：{err}", "data": {}}

    def api_downloader_overview(self) -> Dict[str, Any]:
        ok, msg = self._can_run_task("下载器活动", "dltag")
        if not ok:
            return {"code": 1, "msg": msg, "data": self._skipped_data(msg, {"downloaders": []})}
        return {"code": 0, "data": {"downloaders": self._downloader_overview_data()}}
