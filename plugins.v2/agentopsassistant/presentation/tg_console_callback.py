import re
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from app.log import logger
from app.schemas import NotificationType

from ..domain.fusion_transport import (
    build_edit_message_text_payload,
    build_send_rich_message_draft_payload,
    build_send_rich_message_payload,
)


class TgConsoleCallbackMixin:
    """Telegram polling, message/callback handling, action execution, card upsert"""

    def poll_tg_console_updates(self) -> bool:
        ok, _ = self._runtime_gate("scheduler", component="fusion_notify", name="TGConsolePoll")
        if not ok:
            return False
        if not (self._tg_console_enabled and self._tg_console_poll_enabled):
            return False
        token, chat_id, _source = self._resolve_daily_report_telegram_config()
        if not token or not chat_id:
            self._tg_console_last_error = "Telegram 融合汇报卡轮询缺少 Bot Token/Chat ID"
            return False
        state = self._tg_console_state(chat_id=chat_id)
        base_url = f"https://api.telegram.org/bot{token}"
        payload: Dict[str, Any] = {"timeout": 0, "allowed_updates": ["callback_query", "message"]}
        last_update_id = self._safe_int(state.get("last_update_id"), 0, 0)
        if last_update_id:
            payload["offset"] = last_update_id + 1
        res = self._telegram_http_post_json(f"{base_url}/getUpdates", payload, timeout=max(5, self._tg_console_poll_interval))
        ok, data = self._telegram_response_data(res, "getUpdates")
        if not ok:
            state["last_error"] = self._tg_console_last_error
            self._save_tg_console_state(state)
            return False
        seen: set = set()
        for update in data.get("result") or []:
            if not isinstance(update, dict):
                continue
            update_id = self._safe_int(update.get("update_id"), 0, 0)
            callback = update.get("callback_query") or {}
            if update_id in seen:
                if callback.get("id"):
                    self._tg_console_answer_callback(callback.get("id"), "重复回调已忽略")
                continue
            seen.add(update_id)
            if update_id and update_id <= last_update_id:
                if callback.get("id"):
                    self._tg_console_answer_callback(callback.get("id"), "重复回调已忽略")
                continue
            if callback:
                self._handle_tg_console_callback(callback, update_id=update_id)
            message = update.get("message") or {}
            if message:
                self._handle_tg_console_message(message, update_id=update_id)
            if update_id:
                last_update_id = max(last_update_id, update_id)
        state = self._tg_console_state(chat_id=chat_id)
        state["last_update_id"] = last_update_id
        self._save_tg_console_state(state)
        return True

    def _handle_tg_console_message(self, message: Dict[str, Any], update_id: int = 0) -> bool:
        token, chat_id, _source = self._resolve_daily_report_telegram_config()
        state = self._tg_console_state(chat_id=chat_id)
        if update_id:
            state["last_update_id"] = max(self._safe_int(state.get("last_update_id"), 0, 0), int(update_id))
        msg_chat = ((message or {}).get("chat") or {}).get("id")
        user_id = str(((message or {}).get("from") or {}).get("id") or "")
        text = str((message or {}).get("text") or "").strip()
        if not self._tg_console_same_chat(msg_chat, chat_id):
            self._save_tg_console_state(state)
            return False
        if self._tg_console_allowed_user_ids and user_id not in self._tg_console_allowed_user_ids:
            self._save_tg_console_state(state)
            return False
        command = text.split()[0].split("@", 1)[0].lower() if text else ""
        command_map = {
            "/aoa_create": "create_tg_console_card",
            "/aoa_daily": "run_daily_report",
            "/aoa_report": "run_daily_report",
            "/aoa_subscribe": "run_subscribe_reminder",
            "/aoa_site": "run_site_stat",
            "/aoa_transfer": "run_today_transfer",
            "/aoa_health": "run_health_check",
        }
        action_key = command_map.get(command)
        if not action_key:
            self._save_tg_console_state(state)
            return False
        ok, result = self._tg_console_execute_action(action_key, user_id=user_id)
        self._save_tg_console_state(self._tg_console_state(chat_id=chat_id))
        self._emit_console_notice(f"TG 指令 - {self._tg_console_action_registry().get(action_key, {}).get('label') or action_key}", result, "success" if ok else "error")
        return ok

    def _handle_tg_console_callback(self, callback: Dict[str, Any], update_id: int = 0) -> bool:
        token, chat_id, _source = self._resolve_daily_report_telegram_config()
        state = self._tg_console_state(chat_id=chat_id)
        callback_id = str((callback or {}).get("id") or "")
        user_id = str(((callback or {}).get("from") or {}).get("id") or "")
        cb_chat = ((((callback or {}).get("message") or {}).get("chat") or {}).get("id"))
        data = str((callback or {}).get("data") or "")
        if update_id:
            state["last_update_id"] = max(self._safe_int(state.get("last_update_id"), 0, 0), int(update_id))
        processed = [str(x) for x in list(state.get("processed_callbacks") or []) if str(x)]
        if callback_id and callback_id in set(processed):
            self._save_tg_console_state(state)
            self._tg_console_answer_callback(callback_id, "重复回调已忽略")
            return True
        if callback_id:
            processed.append(callback_id)
            state["processed_callbacks"] = processed[-100:]
        tab_key = self._tg_console_callback_tab_key(data)
        if tab_key is not None:
            valid_columns = {x["key"] for x in self._fusion_column_registry()}
            enabled_columns = set(self._fusion_notify_columns or valid_columns) & valid_columns
            category_keys = {x["key"] for x in self._fusion_category_registry()}
            column_keys = {x["key"] for x in self._fusion_column_registry()}
            if tab_key not in category_keys and tab_key not in column_keys:
                self._save_tg_console_state(state)
                self._tg_console_answer_callback(callback_id, "未知栏目")
                return False
            active_tab = self._normalize_fusion_tab(tab_key)
            if not self._tg_console_same_chat(cb_chat, chat_id):
                self._save_tg_console_state(state)
                self._tg_console_answer_callback(callback_id, "会话不匹配")
                return False
            if self._tg_console_allowed_user_ids and user_id not in self._tg_console_allowed_user_ids:
                self._save_tg_console_state(state)
                self._tg_console_answer_callback(callback_id, "未授权的 Telegram 用户")
                return False
            if not any(child in enabled_columns for child in self._fusion_category_children(active_tab)):
                self._save_tg_console_state(state)
                self._tg_console_answer_callback(callback_id, "栏目未启用")
                return False
            state["active_tab"] = active_tab
            state["tab_touched"] = True
            try:
                refreshed = self._refresh_fusion_category(active_tab, state)
                ok = bool(refreshed) and self._tg_console_upsert_card(token, chat_id, state)
            except Exception as err:
                ok = False
                state["last_error"] = f"Telegram 融合通知栏目切换异常：{self._telegram_safe_error(err, limit=500)}"
            self._save_tg_console_state(state)
            self._tg_console_answer_callback(callback_id, "已刷新" if ok else "刷新失败")
            return bool(ok)
        nonce = self._tg_console_callback_action_nonce(data)
        if nonce is None:
            self._save_tg_console_state(state)
            self._tg_console_answer_callback(callback_id, "未知操作")
            return False
        if not self._tg_console_same_chat(cb_chat, chat_id):
            self._save_tg_console_state(state)
            self._tg_console_answer_callback(callback_id, "会话不匹配")
            return False
        if self._tg_console_allowed_user_ids and user_id not in self._tg_console_allowed_user_ids:
            self._save_tg_console_state(state)
            self._tg_console_answer_callback(callback_id, "未授权的 Telegram 用户")
            return False
        actions = state.setdefault("pending_actions", {})
        action = actions.get(nonce) or {}
        if not action or action.get("done"):
            self._save_tg_console_state(state)
            self._tg_console_answer_callback(callback_id, "操作已过期")
            return False
        now = datetime.now().timestamp()
        if action.get("expires_at") and float(action.get("expires_at") or 0) < now:
            action["done"] = True
            self._save_tg_console_state(state)
            self._tg_console_answer_callback(callback_id, "确认已过期")
            return False
        registry = self._tg_console_action_registry()
        if action.get("confirm_for"):
            original = actions.get(action.get("confirm_for")) or {}
            original_key = str(original.get("action") or "")
            if original_key not in registry:
                action["done"] = True
                original["done"] = True
                self._save_tg_console_state(state)
                self._tg_console_answer_callback(callback_id, "未知操作")
                return False
            if str(original.get("user_id") or "") != user_id:
                self._save_tg_console_state(state)
                self._tg_console_answer_callback(callback_id, "只能由发起人确认")
                return False
            ok, message = self._tg_console_execute_action(str(original.get("action") or ""), user_id=user_id)
            action["done"] = True
            original["done"] = True
            self._save_tg_console_state(state)
            self._emit_console_notice(f"TG 远控 - {original.get('label') or original.get('action')}", message, "success" if ok else "error")
            self._tg_console_answer_callback(callback_id, "已执行" if ok else "执行失败")
            return ok
        action_key = str(action.get("action") or "")
        if action_key not in registry:
            action["done"] = True
            self._save_tg_console_state(state)
            self._tg_console_answer_callback(callback_id, "未知操作")
            return False
        if action.get("destructive"):
            confirm_nonce = self._tg_console_new_nonce(actions)
            actions[confirm_nonce] = {
                "action": action.get("action"),
                "label": f"确认 {action.get('label') or action.get('action')}",
                "user_id": user_id,
                "confirm_for": nonce,
                "expires_at": now + 60,
                "destructive": False,
                "created_at": now,
            }
            action["user_id"] = user_id
            self._save_tg_console_state(state)
            self._emit_console_notice("TG 远控等待确认", f"{action.get('label')} 需要 60 秒内二次确认", "warning")
            self._tg_console_answer_callback(callback_id, "请在 60 秒内再次确认")
            return True
        ok, message = self._tg_console_execute_action(action_key, user_id=user_id)
        action["done"] = True
        self._save_tg_console_state(state)
        self._emit_console_notice(f"TG 远控 - {action.get('label') or action.get('action')}", message, "success" if ok else "error")
        self._tg_console_answer_callback(callback_id, "已执行" if ok else "执行失败")
        return ok

    def _tg_console_execute_action(self, action_key: str, user_id: Optional[str] = None) -> Tuple[bool, str]:
        registry = self._tg_console_action_registry()
        action = registry.get(action_key)
        if not action:
            return False, "未知操作"
        if not self._enabled:
            return False, "插件未启用"
        component = action.get("component")
        if component and not self._component_enabled(component):
            return False, f"{action.get('label')} 未启用"
        try:
            result = action["runner"]()
            if isinstance(result, dict):
                ok = result.get("code") == 0
                return ok, str(result.get("msg") or ("执行成功" if ok else "执行失败"))
            ok = bool(result)
            return ok, f"{action.get('label')}执行{'成功' if ok else '失败'}"
        except Exception as err:
            logger.error(f"AgentOpsAssistant TG 远控 {action_key} 执行失败：{err}")
            return False, str(err)

    def _tg_console_action_registry(self) -> Dict[str, Dict[str, Any]]:
        return {
            "create_tg_console_card": {"label": "立即建卡", "runner": self.api_create_tg_console_card, "component": "", "destructive": False},
            "run_daily_report": {"label": "立即刷新", "runner": self.api_run_daily_report, "component": "", "destructive": False},
            "run_subscribe_reminder": {"label": "订阅追新", "runner": self.api_run_subscribe_reminder, "component": "subscribe_reminder", "destructive": False},
            "run_site_stat": {"label": "站点统计", "runner": self.api_run_site_stat, "component": "site_stat", "destructive": False},
            "run_today_transfer": {"label": "今日入库", "runner": self.api_run_today_transfer, "component": "", "destructive": False},
            "run_health_check": {"label": "健康巡查", "runner": self.api_run_health_check, "component": "health_check", "destructive": False},
            "run_mp_update_apply": {"label": "立即更新", "runner": self.api_run_mp_update_apply, "component": "mp_update", "destructive": True},
        }

    def _tg_console_action_groups(self) -> List[List[str]]:
        return [
            ["create_tg_console_card", "run_daily_report"],
            ["run_site_stat", "run_today_transfer"],
        ]

    @classmethod
    def _tg_console_callback_tab_key(cls, data: str) -> Optional[str]:
        raw = cls._tg_console_unwrap_plugin_callback(data)
        if raw.startswith("aoatab:"):
            key = raw.split(":", 1)[1].split("?", 1)[0].strip()
            return "system_health" if key == "health" else key
        if raw.startswith("aoa:tab:"):
            key = raw.split(":", 2)[-1].split("?", 1)[0].strip()
            return "system_health" if key == "health" else key
        return None

    @classmethod
    def _tg_console_callback_action_nonce(cls, data: str) -> Optional[str]:
        raw = cls._tg_console_unwrap_plugin_callback(data)
        if raw.startswith("aoav1:"):
            return raw.split(":", 1)[1].split("?", 1)[0].strip()
        if raw.startswith("aoa:v1:"):
            return raw.split(":", 2)[-1].split("?", 1)[0].strip()
        return None

    @classmethod
    def _tg_console_plugin_callback_data(cls, payload: str) -> str:
        return f"[PLUGIN]{cls.__name__}|{str(payload or '').strip()}"

    @classmethod
    def _tg_console_unwrap_plugin_callback(cls, data: str) -> str:
        raw = str(data or "").strip()
        if raw.startswith("[PLUGIN]"):
            try:
                plugin_id, payload = raw.split("|", 1)
            except ValueError:
                return raw
            plugin_name = plugin_id.replace("[PLUGIN]", "").strip()
            if plugin_name.lower() in {cls.__name__.lower(), "agentopsassistant"}:
                return payload.strip()
        return raw

    @staticmethod
    def _telegram_message_not_modified_error(value: Any) -> bool:
        text = str(value or "").lower()
        return "message is not modified" in text or "message not modified" in text

    def _tg_console_upsert_card(self, token: str, chat_id: str, state: Dict[str, Any]) -> bool:
        ok, _ = self._runtime_gate("telegram", component="fusion_notify", name="Telegram fusion card upsert")
        if not ok:
            return False
        base_url = f"https://api.telegram.org/bot{token}"
        rich_message = self._build_tg_console_rich_message(state)
        reply_markup = self._build_tg_console_reply_markup(state)
        if state.get("message_id"):
            payload = build_edit_message_text_payload(chat_id, state.get("message_id"), rich_message, reply_markup)
            res = self._telegram_http_post_json(f"{base_url}/editMessageText", payload, timeout=15)
            ok, _ = self._telegram_response_data(res, "editMessageText")
            if ok or self._telegram_message_not_modified_error(self._tg_console_last_error):
                self._tg_console_last_error = ""
                state["last_error"] = ""
                return True
            state["last_error"] = self._tg_console_last_error
            return False
        payload = build_send_rich_message_payload(chat_id, rich_message, reply_markup)
        res = self._telegram_http_post_json(f"{base_url}/sendRichMessage", payload, timeout=15)
        ok, data = self._telegram_response_data(res, "sendRichMessage")
        if ok:
            result = data.get("result") or {}
            if isinstance(result, dict):
                state["message_id"] = self._safe_int(result.get("message_id"), 0, 0)
            self._tg_console_last_error = ""
            state["last_error"] = ""
            return True
        state["last_error"] = self._tg_console_last_error
        return False

    def _tg_console_send_rich_message_draft(self, token: str, chat_id: str, draft_id: int, state: Dict[str, Any]) -> bool:
        """Send an ephemeral draft only when the caller has a proven private-chat route."""
        ok, _ = self._runtime_gate("telegram", component="fusion_notify", name="Telegram sendRichMessageDraft")
        if not ok:
            return False
        payload = build_send_rich_message_draft_payload(chat_id, draft_id, self._build_tg_console_rich_message(state))
        res = self._telegram_http_post_json(f"https://api.telegram.org/bot{token}/sendRichMessageDraft", payload, timeout=15)
        ok, _ = self._telegram_response_data(res, "sendRichMessageDraft")
        return ok

    def _tg_console_answer_callback(self, callback_query_id: str, text: str = "") -> bool:
        if not callback_query_id:
            return False
        ok, _ = self._runtime_gate("telegram", component="fusion_notify", name="Telegram answerCallbackQuery")
        if not ok:
            return False
        token, _chat_id, _source = self._resolve_daily_report_telegram_config()
        if not token:
            return False
        payload = {"callback_query_id": callback_query_id}
        if text:
            payload["text"] = str(text)[:180]
        res = self._telegram_http_post_json(f"https://api.telegram.org/bot{token}/answerCallbackQuery", payload, timeout=10)
        ok, _ = self._telegram_response_data(res, "answerCallbackQuery")
        return ok

    @staticmethod
    def _tg_console_same_chat(callback_chat_id: Any, expected_chat_id: Any) -> bool:
        if expected_chat_id in (None, ""):
            return True
        return str(callback_chat_id or "").strip() == str(expected_chat_id or "").strip()
