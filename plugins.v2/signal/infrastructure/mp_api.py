import re
from contextlib import nullcontext
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.core.config import settings
from app.log import logger

class MpApiMixin:
    """HTTP API endpoint methods exposed through MoviePilot plugin get_api()."""

    def api_refresh_tg_console_card(self) -> Dict[str, Any]:
        success = bool(self.run_fusion_card_refresh())
        message = "融合通知卡已刷新" if success else (self._tg_console_last_error or "融合通知卡刷新失败")
        return {
            "code": 0 if success else 1,
            "msg": message,
            "data": self._tg_console_action_status_data(0 if success else 1, message),
        }

    def api_create_tg_console_card(self, trigger: str = "manual") -> Dict[str, Any]:
        scope_factory = getattr(self, "_subscription_calendar_read_scope", None)
        with (scope_factory() if callable(scope_factory) else nullcontext()):
            return self._api_create_tg_console_card_scoped(trigger=trigger)

    def _api_create_tg_console_card_scoped(self, trigger: str = "manual") -> Dict[str, Any]:
        ok, msg = self._can_run_task("融合通知卡", "fusion_notify")
        if not ok:
            self._save_task_result("融合通知卡", False, 2, msg)
            return {"code": 1, "msg": msg, "data": self._skipped_data(msg)}
        token, chat_id, _source = self._resolve_fusion_telegram_config()
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
            columns_ok = self._refresh_fusion_columns(state)
            self._compose_tg_console_v7_model(state)
            ok = bool(self._tg_console_upsert_card(token, chat_id, state)) and bool(columns_ok)
        calendar_status = str(state.get("subscription_calendar_status") or "").strip()
        if calendar_status in {"partial", "failed", "invalid"}:
            ok = False
            state["last_error"] = (
                f"订阅日历状态：{calendar_status}"
                + (f"；{state.get('subscription_calendar_errors', [''])[:1][0]}" if state.get("subscription_calendar_errors") else "")
            )
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
        ok, msg = self._can_run_task("今日入库")
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
        self.run_health_check(notify=True)
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
        return self._api_run_task("系统更新检查", self.run_mp_update_check, "mp_update", notify=True)

    def api_run_mp_update_apply(self) -> Dict[str, Any]:
        return self._api_run_task("主程序更新执行", self.run_mp_update_apply, "mp_update", notify=True)

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
                    "status": item.get("status"),
                    "color": item.get("color"),
                    "next": item.get("next"),
                    "last_time": latest.get("time") or "",
                    "last_summary": self._task_result_summary(latest),
                    "data_error": bool(item.get("data_error")),
                    "data_error_summary": item.get("data_error_summary") or "",
                    "duplicate_count": int(item.get("duplicate_count") or 0),
                })
            failed = [t for t in tasks if self._enabled and t["enabled"] and t["status"] in {"failed", "data_error"}]
            try:
                health, health_duplicates = self._read_dashboard_task_data("last_health_check")
                health_error = ""
            except Exception as error:
                health = {}
                health_duplicates = 0
                health_error = str(error)[:160]
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
                        "data_error": bool(health_error),
                        "data_error_summary": health_error,
                        "duplicate_count": health_duplicates,
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
        """插件库仓库地址候选：已配置、上次同步发现与已拉黑三者并集，供插件库黑名单下拉多选。"""
        try:
            configured = self._valid_markets_list(settings.PLUGIN_MARKET)
            last = self.get_data("last_market_update") or {}
            discovered = self._valid_markets_list(last.get("wiki_markets") or [])
            blacklist = self._market_update_blacklist_list()
            blocked_addresses, blocked_hosts = self._market_blacklist_matchers(blacklist)
            items = []
            index = {}
            for source, values in (("configured", configured), ("discovered", discovered), ("blacklisted", blacklist)):
                for value in values:
                    key = self._normalize_market_address(value)
                    if not key:
                        continue
                    existing = index.get(key)
                    if existing is None:
                        index[key] = {"value": value, "source": source, "blocked": self._market_address_blocked(value, blocked_addresses, blocked_hosts)}
                        items.append(index[key])
                    elif source == "blacklisted":
                        existing["value"] = value
                        existing["source"] = source
            labels = {}
            for item in items:
                short = str(item["value"]).rstrip("/").split("/")
                label = "/".join(short[-2:]) if len(short) >= 2 else str(item["value"])
                item["title"] = label
                labels[label] = labels.get(label, 0) + 1
            for item in items:
                if labels.get(item["title"], 0) > 1:
                    item["title"] = str(item["value"])
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
        ok = self.run_log_clean(notify=True)
        return {"code": 0 if ok else 1, "msg": "插件日志清理执行成功" if ok else "插件日志清理执行失败，详情请查看插件日志。"}

    def api_run_backup(self) -> Dict[str, Any]:
        try:
            ok_guard, msg = self._can_run_task("自动备份", "backup")
            if not ok_guard:
                self._save_task_result("自动备份", False, 2, msg)
                return {"code": 1, "msg": msg, "data": self._skipped_data(msg, self._build_backup_status())}
            ok = self.run_backup(notify=True)
            data = getattr(self, "_last_backup_result", None) or self._build_backup_status()
            if data.get("status") == "conflict":
                message = "已有备份或恢复操作正在执行，请先查询当前操作状态。"
            elif data.get("status") in {"success", "partial", "failed"}:
                message = self._backup_outcome(data)
            else:
                message = "备份执行成功" if ok else "备份执行失败，详情请查看结果。"
            return {"code": 0 if ok else 1, "msg": message, "data": data, "text": message}
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

    def api_backup_archives(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        ok, msg = self._can_run_task("备份恢复")
        if not ok:
            return {"code": 1, "msg": msg, "data": {"items": []}}
        request = dict(payload or {})
        try:
            data = self._backup_restore_service().list_archives(
                str(request.get("source") or "local"),
                request.get("temporary_webdav"),
            )
            return {"code": 0, "msg": "备份归档列表获取成功", "data": data}
        except Exception as err:
            return {"code": 1, "msg": f"备份归档列表获取失败：{err}", "data": {"items": []}}

    def api_backup_archive(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        ok, msg = self._can_run_task("备份归档检查")
        if not ok:
            return {"code": 1, "msg": msg, "data": {}}
        request = dict(payload or {})
        try:
            data = self._backup_restore_service().inspect_archive(
                str(request.get("source") or "local"),
                str(request.get("archive_name") or ""),
                request.get("temporary_webdav"),
            )
            return {"code": 0, "msg": "备份归档检查通过", "data": data}
        except Exception as err:
            return {"code": 1, "msg": f"备份归档检查失败：{err}", "data": {}}

    def api_import_backup_archive(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        ok, msg = self._can_run_task("导入备份归档")
        if not ok:
            return {"code": 1, "msg": msg, "data": {}}
        request = dict(payload or {})
        try:
            data = self._backup_restore_service().import_archive(
                str(request.get("content_base64") or ""),
                str(request.get("filename") or "backup.zip"),
            )
            return {"code": 0, "msg": "备份归档导入并检查通过", "data": data}
        except Exception as err:
            return {"code": 1, "msg": f"备份归档导入失败：{err}", "data": {}}

    def api_download_backup_archive(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        ok, msg = self._can_run_task("下载备份归档")
        if not ok:
            return {"code": 1, "msg": msg, "data": {}}
        request = dict(payload or {})
        try:
            data = self._backup_restore_service().download_archive(
                str(request.get("source") or "local"),
                str(request.get("archive_name") or ""),
                request.get("temporary_webdav"),
            )
            return {"code": 0, "msg": "备份归档已准备下载", "data": data}
        except Exception as err:
            return {"code": 1, "msg": f"备份归档下载失败：{err}", "data": {}}

    def api_run_backup_restore(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        ok_guard, msg = self._can_run_task("备份恢复")
        if not ok_guard:
            self._save_task_result("备份恢复", False, 2, msg)
            return {"code": 1, "msg": msg, "data": self._skipped_data(msg)}
        try:
            data = self._backup_restore_service().execute(payload or {})
            success = bool(data.get("success"))
            status = str(data.get("status") or "failed")
            message = data.get("message") or ("备份恢复完成" if success else "备份恢复失败")
            self._save_task_result("备份恢复", success, 0 if success else 1, str(message))
            return {"code": 0 if success else 1, "msg": str(message), "data": data, "text": str(message)}
        except Exception as err:
            logger.error(f"Signal 备份恢复执行失败：{err}")
            self._save_task_result("备份恢复", False, -1, str(err))
            return {"code": 1, "msg": f"备份恢复执行失败：{err}", "data": {"success": False, "status": "failed", "errors": [str(err)]}, "text": str(err)}

    def api_backup_operation_status(self) -> Dict[str, Any]:
        ok, msg = self._can_run_task("备份操作状态")
        if not ok:
            return {"code": 1, "msg": msg, "data": {"current": None, "recent": []}}
        return {"code": 0, "msg": "备份操作状态获取成功", "data": self._backup_restore_service().operation_status()}

    def api_preview_market_update(self) -> Dict[str, Any]:
        ok, msg = self._can_run_task("插件库同步", "market_update")
        if not ok:
            return {"code": 1, "msg": msg, "data": self._skipped_data(msg), "text": msg}
        try:
            data = self._build_market_update_status(apply=False)
            success = bool(data.get("success"))
            message = (
                "插件库同步预览完成，未写入配置。"
                if success
                else str(data.get("error") or "插件库同步预览失败。")
            )
            return {
                "code": 0 if success else 1,
                "msg": message,
                "data": data,
                "text": self._format_market_update_text(data),
            }
        except Exception as err:
            return {"code": 1, "msg": f"插件库同步预览失败：{err}", "data": {}, "text": ""}

    def api_run_market_update(self) -> Dict[str, Any]:
        ok_guard, msg = self._can_run_task("插件库同步", "market_update")
        if not ok_guard:
            self._save_task_result("插件库同步", False, 2, msg)
            return {"code": 1, "msg": msg, "data": self._skipped_data(msg, self._build_market_status())}
        ok = self.run_market_update(notify=True)
        detail = getattr(self, "_last_market_update_result", {}) or {}
        data = {**self._build_market_status(), **detail}
        message = "插件库同步执行成功" if ok else str(detail.get("error") or "插件库同步执行失败。")
        return {
            "code": 0 if ok else 1,
            "msg": message,
            "data": data,
            "text": self._format_market_update_text(data),
        }

    def api_preview_plugin_update_reminder(self) -> Dict[str, Any]:
        ok, msg = self._can_run_task("插件更新", "plugin_update_reminder")
        if not ok:
            return {"code": 1, "msg": msg, "data": self._skipped_data(msg), "text": msg}
        try:
            data = self._auto_update_installed_plugins(apply=False)
            data["auto_install"] = False
            text = self._format_plugin_update_text(data)
            success = not bool(data.get("error"))
            return {"code": 0 if success else 1, "msg": "插件更新预览完成，未安装插件。" if success else "插件更新预览失败。", "data": data, "text": text}
        except Exception as err:
            return {"code": 1, "msg": f"插件更新预览失败：{err}", "data": {}, "text": ""}

    def api_run_plugin_update_reminder(self) -> Dict[str, Any]:
        return self._api_run_task("插件更新", self.run_plugin_update_reminder, "plugin_update_reminder", notify=True)

    def api_preview_plugin_auto_install(self) -> Dict[str, Any]:
        ok, msg = self._can_run_task("插件更新", "plugin_update_reminder")
        if not ok:
            return {"code": 1, "msg": msg, "data": self._skipped_data(msg), "text": msg}
        try:
            data = self._auto_update_installed_plugins(apply=False)
            text = self._format_plugin_update_text(data, "📦 插件自动安装预览")
            success = not bool(data.get("error"))
            return {"code": 0 if success else 1, "msg": "插件自动安装预览完成，未安装插件。" if success else "插件自动安装预览失败。", "data": data, "text": text}
        except Exception as err:
            return {"code": 1, "msg": f"插件自动安装预览失败：{err}", "data": {}, "text": ""}

    def api_run_plugin_auto_install(self) -> Dict[str, Any]:
        return self._api_run_task("插件更新", self.run_plugin_auto_install, "plugin_update_reminder", notify=True)

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
        try:
            override = self._plugin_uninstall_config_from_payload(request_payload)
        except ValueError as err:
            self._save_task_result("插件卸载", False, 2, str(err))
            return {"code": 1, "msg": str(err), "data": self._skipped_data(str(err), {"blocked": str(err), "uninstalled": []})}
        ok, data = self._run_plugin_uninstall_clean(override=override)
        status = str(data.get("status") or "failed")
        if status == "completed":
            message = "插件卸载执行成功，终态复核无残留。"
        elif status == "restart_required":
            message = "插件持久化清理已完成，请重启 MoviePilot 后复核内存残留。"
        else:
            message = "插件卸载未执行或失败，详情请查看逐项复核。"
        return {"code": 0 if ok else 1, "msg": message, "data": data}

    def api_agentopsassistant_purge_status(self) -> Dict[str, Any]:
        """Read-only fixed-target audit; never deletes or creates a backup."""
        try:
            data = self._build_agentopsassistant_purge_status()
            if data.get("clean"):
                msg = "AgentOpsAssistant 已彻底清除，未发现残留。"
            else:
                msg = f"检测到 {data.get('residue_count', 0)} 项 AgentOpsAssistant 残留。"
            return {"code": 0 if data.get("success") else 1, "msg": msg, "data": data}
        except Exception as err:
            logger.error(f"Signal AgentOpsAssistant 专杀状态读取失败：{err}")
            return {"code": 1, "msg": f"AgentOpsAssistant 专杀状态读取失败：{err}", "data": {}}

    def api_run_agentopsassistant_purge(self, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Irreversibly purge the one hard-coded legacy target without backup."""
        request = dict(payload or {})
        confirmed = (
            set(request) == {"agentopsassistant_purge_confirm"}
            and type(request.get("agentopsassistant_purge_confirm")) is bool
            and request.get("agentopsassistant_purge_confirm") is True
        )
        if not confirmed:
            msg = "mp运维助手专杀只接受固定目标 AgentOpsAssistant 的一次性布尔确认；不会备份，操作不可恢复。"
            return {
                "code": 1,
                "msg": msg,
                "data": {
                    "target": "AgentOpsAssistant",
                    "confirm_required": True,
                    "no_backup": True,
                    "irreversible": True,
                    "success": False,
                    "errors": [msg],
                },
            }
        try:
            data = self._run_agentopsassistant_purge()
            ok = bool(data.get("success"))
            msg = "AgentOpsAssistant 专杀完成，终态复核无残留。" if ok else "AgentOpsAssistant 专杀未完成，终态复核仍有残留。"
            return {"code": 0 if ok else 1, "msg": msg, "data": data}
        except Exception as err:
            logger.error(f"Signal AgentOpsAssistant 专杀执行失败：{err}")
            return {
                "code": 1,
                "msg": f"AgentOpsAssistant 专杀执行失败：{err}",
                "data": {"target": "AgentOpsAssistant", "no_backup": True, "success": False, "errors": [str(err)]},
            }

    def api_tg_console_status(self) -> Dict[str, Any]:
        return {"code": 0, "data": self._tg_console_status_data()}

    def api_preview_tg_console(self) -> Dict[str, Any]:
        scope_factory = getattr(self, "_subscription_calendar_read_scope", None)
        with (scope_factory() if callable(scope_factory) else nullcontext()):
            token, chat_id, _source = self._resolve_fusion_telegram_config()
            state = self._tg_console_state(chat_id=chat_id)
            state.pop("v7_model", None)
            try:
                self._compose_tg_console_v7_model(state)
                rich_message = self._build_tg_console_rich_message(state)
            except Exception as err:
                rich_message = {"html": "", "skip_entity_detection": True}
                state.setdefault("subscription_calendar_status", "failed")
                state.setdefault("subscription_calendar_errors", [str(err)[:240]])
            status = str(state.get("subscription_calendar_status") or "")
            errors = list(state.get("subscription_calendar_errors") or [])
            snapshot_getter = getattr(self, "_subscription_calendar_snapshot_for_scope", None)
            snapshot = snapshot_getter() if callable(snapshot_getter) else None
            data = {
                "telegram_rich_message": rich_message,
                "calendar_status": status,
                "calendar_items": list(getattr(snapshot, "items", ()) or ()),
                "calendar_errors": errors[:3],
                "success": status not in {"partial", "failed", "invalid"},
            }
            return {
                "code": 0 if data["success"] else 1,
                "msg": "TG 融合汇报卡预览已生成" if data["success"] else f"订阅日历状态：{status}",
                "data": data,
            }

    def api_reset_tg_console_card(self) -> Dict[str, Any]:
        ok, msg = self._can_run_task("融合通知卡", "fusion_notify")
        if not ok:
            self._save_task_result("融合通知卡", False, 2, msg)
            return {"code": 1, "msg": msg, "data": self._skipped_data(msg)}
        token, chat_id, _source = self._resolve_fusion_telegram_config()
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
        try:
            success = bool(self.run_seed_clean(notify=True))
            return {
                "code": 0 if success else 1,
                "msg": f"自动删种执行{'成功' if success else '失败'}",
                "data": {"source": "saved_config"},
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
            data = self._site_increment_snapshot()
            if data.get("error"):
                return {"code": 1, "msg": f"站点统计图数据获取失败：{data['error']}", "data": data}
            state_loader = getattr(self, "_load_site_refresh_state", None)
            refresh_state = state_loader() if callable(state_loader) else {}
            if self._site_refresh_state_is_current_failure(refresh_state, data):
                message = str(refresh_state.get("message") or "站点数据刷新失败，已取消统计以避免使用旧快照")
                data["refresh_state"] = refresh_state
                data["error"] = message
                data["data_valid"] = False
                data["stale"] = True
                return {"code": 1, "msg": message, "data": data}
            return {"code": 0, "data": data}
        except Exception as err:
            logger.error(f"站点统计图数据获取失败：{err}")
            return {
                "code": 1,
                "msg": str(err),
                "data": {
                    "date": "",
                    "basis": "today",
                    "sites": [],
                    "upload_total": 0,
                    "download_total": 0,
                    "error": str(err),
                },
            }

    def run_site_stat_scheduled(self) -> bool:
        return self.api_run_site_stat(trigger="scheduled").get("code") == 0

    def api_run_site_stat(self, trigger: str = "manual") -> Dict[str, Any]:
        """刷新站点数据统计并汇总当前 MoviePilot 站点快照。

        A run is a real refresh operation, not merely a re-read of yesterday's
        database row.  Refresh first; only then calculate and notify.  This
        prevents a midnight stale snapshot from being reported as a successful
        current-day result.
        """
        ok, msg = self._can_run_task("站点数据统计", "site_stat")
        # 手动执行（配置页按钮 / TG 控制台）与定时执行一样发送结果通知；
        # 手动通知不参与冷却与"无变化"抑制，见 _notify_fusion_task_outcome(notification_manual=...)。
        notify = trigger == "manual"
        scheduled_failure_notify = trigger == "scheduled" or notify
        scheduled_success_notify = scheduled_failure_notify and bool(
            getattr(self, "_site_stat_schedule_notify_enabled", True)
        )
        if not ok:
            self._save_task_result("站点数据统计", False, 2, msg)
            data = self._skipped_data(msg, {"date": "", "basis": "skipped", "sites": [], "upload_total": 0, "download_total": 0})
            return {"code": 1, "msg": msg, "data": data}
        try:
            refresh = self._refresh_site_userdata_for_stat()
            if not refresh.get("success"):
                msg = str(refresh.get("message") or "站点用户数据刷新失败")
                payload = {
                    "date": self._today_prefix(),
                    "basis": "today",
                    "sites": [],
                    "upload_total": 0,
                    "download_total": 0,
                    "refresh": refresh,
                }
                self._save_task_result("站点数据统计", False, 1, msg)
                if scheduled_failure_notify:
                    self._notify_fusion_task_outcome(
                        mtype=self._notification_type(self._site_stat_notify_type),
                        title="Signal - 站点统计",
                        text=msg,
                        outcome=f"站点统计失败：{msg}",
                        success=False,
                        component="site_stat",
                        task_key="site_stat",
                        task_group="站点统计",
                        affected_owner="persistent-sites",
                        notification_status="error",
                        notification_target="daily_increment",
                        notification_fingerprint=self._notification_error_fingerprint(msg),
                        notification_cooldown=False,
                        notification_manual=notify,
                    )
                return {"code": 1, "msg": msg, "data": payload}
            chart = self.api_site_stat_chart()
            if (chart or {}).get("code", 0) != 0:
                msg = (chart or {}).get("msg") or "站点统计图数据获取失败"
                payload = (chart or {}).get("data") or {"date": "", "basis": "today", "sites": [], "upload_total": 0, "download_total": 0}
                self._save_task_result("站点数据统计", False, 1, msg)
                if scheduled_failure_notify:
                    self._notify_fusion_task_outcome(
                        mtype=self._notification_type(self._site_stat_notify_type),
                        title="Signal - 站点统计",
                        text=msg,
                        outcome=f"站点统计失败：{msg}",
                        success=False,
                        component="site_stat",
                        task_key="site_stat",
                        task_group="站点统计",
                        affected_owner="persistent-sites",
                        notification_status="error",
                        notification_target="daily_increment",
                        notification_fingerprint=self._notification_error_fingerprint(msg),
                        notification_cooldown=False,
                        notification_manual=notify,
                    )
                return {"code": 1, "msg": msg, "data": payload}
            payload = chart.get("data") or {}
            snapshot_error = str(payload.get("error") or "").strip()
            # 刷新协调器只贡献逐站点原因，快照层决定可计入集合，
            # 发布层只做"有无可计入站点"的二分：个别站点故障不取消整次统计。
            states = self._merge_site_states(payload.get("site_states"), refresh.get("sites"))
            counted = self._site_state_counted(states)
            faults = self._site_state_faults(states)
            excluded_lines = self._format_site_state_lines(states)
            if snapshot_error:
                msg = f"站点统计图数据获取失败：{snapshot_error}"
                self._save_task_result("站点数据统计", False, 1, msg)
                if scheduled_failure_notify:
                    self._notify_fusion_task_outcome(
                        mtype=self._notification_type(self._site_stat_notify_type),
                        title="Signal - 站点统计",
                        text=msg,
                        outcome=msg,
                        success=False,
                        component="site_stat",
                        task_key="site_stat",
                        task_group="站点统计",
                        affected_owner="persistent-sites",
                        notification_status="error",
                        notification_target="daily_increment",
                        notification_fingerprint=self._notification_error_fingerprint(snapshot_error),
                        notification_cooldown=False,
                        notification_manual=notify,
                    )
                return {"code": 1, "msg": msg, "data": payload}
            if not counted and int(payload.get("active_count") or 0) > 0:
                # 没有任何可计入站点：只发一条统计侧通知并逐站列出原因，
                # 不再额外触发站点故障目标，避免成对重复告警。
                msg = "本次没有可计入今日增量的站点"
                text = "\n".join([msg, *excluded_lines]) if excluded_lines else msg
                payload["site_states"] = states
                payload["counted_count"] = 0
                payload["fault_count"] = len(faults)
                payload["unavailable_count"] = len([
                    item for item in states if str(item.get("status") or "") == "unavailable"
                ])
                payload["checker_error_count"] = len([
                    item for item in states if str(item.get("status") or "") == "checker_error"
                ])
                self._save_task_result("站点数据统计", False, 1, text)
                if scheduled_failure_notify:
                    self._notify_fusion_task_outcome(
                        mtype=self._notification_type(self._site_stat_notify_type),
                        title="Signal - 站点统计",
                        text=text,
                        outcome=f"站点统计失败：{msg}",
                        success=False,
                        component="site_stat",
                        task_key="site_stat",
                        task_group="站点统计",
                        affected_owner="persistent-sites",
                        notification_status="error",
                        notification_target="daily_increment",
                        notification_fingerprint=self._notification_outcome_fingerprint({
                            "excluded": self._site_state_fingerprint_items(states),
                        }),
                        notification_cooldown=True,
                        notification_manual=notify,
                    )
                return {"code": 1, "msg": msg, "data": payload}
            # 返回体必须和通知口径一致：快照层只知道快照结论，
            # 刷新侧的站点故障要写回 payload，否则 API 会出现
            # "通知说站点异常、payload 说全部正常" 的矛盾。
            payload["site_states"] = states
            payload["counted_count"] = len(counted)
            payload["fault_count"] = len(faults)
            payload["unavailable_count"] = len([
                item for item in states if str(item.get("status") or "") == "unavailable"
            ])
            payload["checker_error_count"] = len([
                item for item in states if str(item.get("status") or "") == "checker_error"
            ])
            site_count = len(payload.get("sites") or [])
            upload = self._format_bytes(payload.get("upload_total", 0))
            download = self._format_bytes(payload.get("download_total", 0))
            text = f"已刷新 {site_count} 个站点｜今日｜上传 {upload}｜下载 {download}" if site_count else "已刷新站点数据，暂无可用增量"
            self._save_task_result("站点数据统计", True, 0, text)
            if scheduled_success_notify:
                has_increment = bool(payload.get("upload_total") or payload.get("download_total"))
                notification_text = text
                if not getattr(self, "_fusion_notify_enabled", False):
                    notification_text = self._format_site_stat_success_notification(payload, text, states)
                fingerprint_sites = sorted([
                    {
                        "name": str(item.get("name") or ""),
                        "upload": item.get("upload") or 0,
                        "download": item.get("download") or 0,
                    }
                    for item in payload.get("sites") or [] if isinstance(item, dict)
                ], key=lambda item: (item["name"], str(item["upload"]), str(item["download"])))
                self._notify_fusion_task_outcome(
                    mtype=self._notification_type(self._site_stat_notify_type),
                    title="Signal - 站点统计",
                    text=notification_text,
                    outcome="站点统计完成",
                    success=True,
                    component="site_stat",
                    task_key="site_stat",
                    task_group="站点统计",
                    affected_owner="persistent-sites",
                    notification_status="changed" if has_increment else "noop",
                    notification_target="daily_increment",
                    notification_fingerprint=(
                        self._notification_outcome_fingerprint({
                            "date": str(payload.get("date") or ""),
                            "basis": str(payload.get("basis") or ""),
                            "sites": fingerprint_sites,
                        })
                        if has_increment and not self._fusion_notify_enabled else ""
                    ),
                    notification_cooldown=has_increment,
                    notification_manual=notify,
                )
            if scheduled_failure_notify:
                self._notify_site_fault_outcome(faults, manual=notify)
            return {"code": 0, "msg": text, "data": payload}
        except Exception as err:
            self._save_task_result("站点数据统计", False, -1, str(err))
            logger.error(f"站点数据统计刷新失败：{err}")
            if scheduled_failure_notify:
                self._notify_fusion_task_outcome(
                    mtype=self._notification_type(self._site_stat_notify_type),
                    title="Signal - 站点统计",
                    text=f"站点数据统计刷新失败：{err}",
                    outcome=f"站点统计失败：{err}",
                    success=False,
                    component="site_stat",
                    task_key="site_stat",
                    task_group="站点统计",
                    affected_owner="persistent-sites",
                    notification_status="error",
                    notification_target="daily_increment",
                    notification_fingerprint=self._notification_error_fingerprint(err),
                    notification_cooldown=False,
                    notification_manual=notify,
                )
            return {"code": 1, "msg": f"站点数据统计刷新失败：{err}", "data": {"date": "", "basis": "today", "sites": [], "upload_total": 0, "download_total": 0}}

    def _format_site_stat_success_notification(
        self,
        payload: Dict[str, Any],
        summary: str,
        states: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """Format the standalone MoviePilot success body from the current payload.

        A partially available run publishes the countable sites and then lists
        every excluded site with its own reason; there is no aggregate count.
        """
        sites = payload.get("sites") or []
        detail_lines = []
        for item in sites:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name") or "未知站点")
            upload = self._format_bytes(item.get("upload", 0))
            download = self._format_bytes(item.get("download", 0))
            detail_lines.append(f"⦁ {name}：上传 {upload}｜下载 {download}")
        excluded_lines = self._format_site_state_lines(
            states if states is not None else payload.get("site_states")
        )
        body = [*detail_lines, *excluded_lines]
        return "\n".join([summary, *body]) if body else summary

    def _notify_site_fault_outcome(self, faults: List[Dict[str, Any]], *, manual: bool = False) -> None:
        """Deliver site faults through their own notification target.

        Cooldown, the four outcome states and the single recovery message are
        owned by ``notification_outcome_state_v1``; this only classifies.  With
        Fusion enabled the same call becomes an anomaly event, so the ordinary
        recovery bookkeeping is skipped there and the two routes stay exclusive.
        """
        if faults:
            self._notify_fusion_task_outcome(
                mtype=self._notification_type(self._site_stat_notify_type),
                title="Signal - 站点异常",
                text="\n".join([
                    f"发现 {len(faults)} 个站点异常",
                    *self._format_site_state_lines(faults, suffix="需要处理"),
                ]),
                outcome=f"站点异常 {len(faults)} 个",
                success=False,
                component="site_stat",
                task_key="site_stat",
                task_group="站点统计",
                affected_owner="persistent-sites",
                notification_status="error",
                notification_target="site_faults",
                notification_fingerprint=self._notification_outcome_fingerprint({
                    "faults": self._site_state_fingerprint_items(faults),
                }),
                notification_cooldown=True,
                notification_manual=manual,
            )
            return
        if getattr(self, "_fusion_notify_enabled", False):
            return
        self._notify_fusion_task_outcome(
            mtype=self._notification_type(self._site_stat_notify_type),
            title="Signal - 站点异常恢复",
            text="全部启用站点刷新正常",
            outcome="站点异常已恢复",
            success=True,
            component="site_stat",
            task_key="site_stat",
            task_group="站点统计",
            affected_owner="persistent-sites",
            notification_status="recovered",
            notification_target="site_faults",
            notification_manual=False,
        )

    @staticmethod
    def _site_refresh_state_is_current_failure(state: Dict[str, Any], data: Dict[str, Any]) -> bool:
        if not state or state.get("success") is not False:
            return False
        if state.get("active_scope_known") is not True:
            return False
        if state.get("active_count") is not None and data.get("active_count") is not None:
            try:
                if int(state.get("active_count")) != int(data.get("active_count")):
                    return False
            except (TypeError, ValueError):
                return False
        persisted_domains = {str(item).strip() for item in (state.get("active_domains") or []) if str(item).strip()}
        current_domains = {str(item).strip() for item in (data.get("active_domains") or []) if str(item).strip()}
        if persisted_domains != current_domains:
            return False
        finished_at = str(state.get("finished_at") or "").strip()
        latest_updated_at = str(data.get("latest_updated_at") or "").strip()
        # A later host refresh can recover the persisted Signal failure.  If
        # no newer snapshot exists, keep surfacing the failure after reload.
        # MoviePilot V2 stores updated_time at one-second precision.  Treat an
        # equal-second host row as the recovery edge rather than holding the
        # error until the next second; a later row is the authoritative signal.
        failure_second = finished_at[:19].replace("T", " ")
        return not latest_updated_at or not finished_at or latest_updated_at < failure_second

    def _refresh_site_userdata_for_stat(self) -> Dict[str, Any]:
        """Refresh active MoviePilot site data before a stat run.

        This is intentionally kept out of ``api_site_stat_chart`` because GET
        chart reads must remain side-effect free.  An empty result is only a
        success when MoviePilot has no active sites; otherwise it means the
        refresh produced no usable current-day data.
        """
        return self._refresh_site_userdata_coordinated()

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
            success = self.run_downloader_helper(trigger="manual", confirmed_candidates=confirmed, notify=True)
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
