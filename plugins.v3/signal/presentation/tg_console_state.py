import re
import os
from contextlib import nullcontext
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from app.sdk.logging import logger
from app.schemas.types import MessageType

from ..domain.fusion_card_state import (
    activate_fusion_card,
    begin_fusion_card_creation,
    can_update_fusion_card,
    disable_fusion_card,
    normalize_fusion_card_state,
    resume_fusion_card,
    retire_fusion_card,
    sanitize_fusion_persisted_state,
)
from ..domain.fusion_event_ledger import empty_event_ledger, normalize_event_ledger


class TgConsoleStateMixin:
    """Telegram console state management, action registration, status data"""

    def _tg_console_state(self, chat_id: str = "") -> Dict[str, Any]:
        today = self._today_prefix()
        state = self.get_data("tg_console_state") or {}
        if not isinstance(state, dict):
            state = {}
        state = sanitize_fusion_persisted_state(state)
        previous_message_id = self._safe_int(state.get("message_id"), 0, 0)
        previous_card = state.get("fusion_card")
        state_chat_id = str(state.get("chat_id") or "")
        changed = False
        if state.get("date") != today or (chat_id and state_chat_id and state_chat_id != str(chat_id)):
            state = {
                "date": today,
                "chat_id": str(chat_id or state.get("chat_id") or ""),
                "message_id": 0,
                "last_update_id": self._safe_int(state.get("last_update_id"), 0, 0),
                "processed_callbacks": [],
                "notices": [],
                "reports": {},
                "columns": {},
                "active_tab": "subscribe_site",
                "tab_touched": False,
                "running_actions": {},
                "pending_actions": {},
                "last_error": "",
                "fusion_card": previous_card,
                "v7_event_ledger": empty_event_ledger(today),
            }
            changed = True
        else:
            state["chat_id"] = str(chat_id or state.get("chat_id") or "")
            state.setdefault("message_id", 0)
            state.setdefault("last_update_id", 0)
            state.setdefault("processed_callbacks", [])
            state.setdefault("notices", [])
            state.setdefault("reports", {})
            state.setdefault("columns", {})
            state["active_tab"] = self._normalize_fusion_tab(state.get("active_tab") or "subscribe_site")
            state.setdefault("tab_touched", False)
            state.setdefault("running_actions", {})
            state.setdefault("pending_actions", {})
            state.setdefault("last_error", "")
            state.setdefault("fusion_card", previous_card)
            ledger = normalize_event_ledger(state.get("v7_event_ledger"), today)
            if state.get("v7_event_ledger") != ledger:
                changed = True
            state["v7_event_ledger"] = ledger
        if "v7_completion_events" in state:
            state.pop("v7_completion_events", None)
            changed = True
        card = normalize_fusion_card_state(
            state.get("fusion_card"),
            enabled=True,
        )
        card = resume_fusion_card(card, enabled=bool(getattr(self, "_fusion_notify_enabled", False)))
        state["fusion_card"] = card
        state["message_id"] = card.get("message_id", 0) if can_update_fusion_card(card) else 0
        if self._tg_console_prune_actions(state):
            changed = True
        if self._sanitize_fusion_update_state(state):
            changed = True
        if changed:
            self._save_tg_console_state(state)
        return state

    def _new_tg_console_card_state(self, chat_id: str = "", trigger: str = "manual") -> Dict[str, Any]:
        previous = self._tg_console_state(chat_id=chat_id)
        today = self._today_prefix()
        previous_card = previous.get("fusion_card") if isinstance(previous.get("fusion_card"), dict) else {}
        same_day = str(previous_card.get("created_at") or "").startswith(today)
        fusion_card = begin_fusion_card_creation(
            previous_card,
            trigger=trigger,
            chat_id=str(chat_id or previous.get("chat_id") or ""),
            reuse_active=same_day,
        )
        return {
            "date": today,
            "chat_id": str(chat_id or previous.get("chat_id") or ""),
            "message_id": fusion_card.get("message_id", 0) if can_update_fusion_card(fusion_card) else 0,
            "last_update_id": self._safe_int(previous.get("last_update_id"), 0, 0),
            "processed_callbacks": list(previous.get("processed_callbacks") or [])[-100:],
            "notices": [],
            "reports": {},
            "columns": {},
            "active_tab": "subscribe_site",
            "tab_touched": False,
            "running_actions": {},
            "pending_actions": {},
            "last_error": "",
            "fusion_card": fusion_card,
            "v7_event_ledger": normalize_event_ledger(previous.get("v7_event_ledger"), today),
        }

    def _save_tg_console_state(self, state: Dict[str, Any]) -> None:
        sanitized = sanitize_fusion_persisted_state(state)
        state.clear()
        state.update(sanitized)
        notices = list((state or {}).get("notices") or [])
        state["notices"] = notices[:self._tg_console_max_notices]
        callbacks = [str(x) for x in list((state or {}).get("processed_callbacks") or []) if str(x)]
        state["processed_callbacks"] = callbacks[-100:]
        reports = state.get("reports") or {}
        state["reports"] = reports if isinstance(reports, dict) else {}
        columns = state.get("columns") or {}
        state["columns"] = columns if isinstance(columns, dict) else {}
        ledger_date = str(state.get("date") or datetime.now().strftime("%Y-%m-%d"))
        state["v7_event_ledger"] = normalize_event_ledger(state.get("v7_event_ledger"), ledger_date)
        state.pop("v7_completion_events", None)
        card = normalize_fusion_card_state(
            state.get("fusion_card"),
            enabled=bool(getattr(self, "_fusion_notify_enabled", False)),
        )
        if state.get("message_id") and card.get("lifecycle") == "creating":
            card = activate_fusion_card(card, message_id=state.get("message_id"), chat_id=str(state.get("chat_id") or ""))
        state["fusion_card"] = card
        state["message_id"] = card.get("message_id", 0) if can_update_fusion_card(card) else 0
        self.save_data("tg_console_state", state)

    def _sync_fusion_card_enablement(self, previous_enabled: Optional[bool]) -> None:
        state = self.get_data("tg_console_state") or {}
        if not isinstance(state, dict):
            state = {}
        card = normalize_fusion_card_state(
            state.get("fusion_card"),
            enabled=True,
        )
        current_enabled = bool(getattr(self, "_fusion_notify_enabled", False))
        if previous_enabled is True and not current_enabled:
            card = disable_fusion_card(card)
        elif previous_enabled is False and current_enabled:
            card = retire_fusion_card(card, reason="re-enabled-requires-create")
        else:
            card = resume_fusion_card(card, enabled=current_enabled)
        state["fusion_card"] = card
        state["message_id"] = card.get("message_id", 0) if can_update_fusion_card(card) else 0
        self._save_tg_console_state(state)
        if previous_enabled is not None and current_enabled and state.get("message_id"):
            token, chat_id, _source = self._resolve_fusion_telegram_config()
            if token and chat_id:
                scope_factory = getattr(self, "_subscription_calendar_read_scope", None)
                with (scope_factory() if callable(scope_factory) else nullcontext()):
                    self._refresh_fusion_columns(state)
                    self._compose_tg_console_v7_model(state)
                self._tg_console_upsert_card(token, chat_id, state)
                self._save_tg_console_state(state)

    def _tg_console_prune_actions(self, state: Dict[str, Any]) -> bool:
        actions = state.setdefault("pending_actions", {})
        now = datetime.now().timestamp()
        changed = False
        for nonce in list(actions.keys()):
            item = actions.get(nonce) or {}
            if item.get("done"):
                actions.pop(nonce, None)
                changed = True
                continue
            expires_at = float(item.get("expires_at") or 0)
            if expires_at and expires_at < now:
                actions.pop(nonce, None)
                changed = True
        return changed

    def _tg_console_register_action(self, action_key: str, label: str, user_id: Optional[Any] = None, destructive: bool = False) -> str:
        state = self._tg_console_state()
        nonce = self._tg_console_ensure_action(state, action_key, label, destructive)
        action = state.setdefault("pending_actions", {}).get(nonce) or {}
        if user_id is not None:
            action["user_id"] = str(user_id)
        state["pending_actions"][nonce] = action
        self._save_tg_console_state(state)
        return nonce

    def _tg_console_ensure_action(self, state: Dict[str, Any], action_key: str, label: str, destructive: bool = False) -> str:
        actions = state.setdefault("pending_actions", {})
        for nonce, action in actions.items():
            if action.get("action") == action_key and not action.get("confirm_for") and not action.get("done"):
                return nonce
        nonce = self._tg_console_new_nonce(actions)
        actions[nonce] = {
            "action": action_key,
            "label": label,
            "destructive": bool(destructive),
            "created_at": datetime.now().timestamp(),
        }
        return nonce

    @staticmethod
    def _tg_console_new_nonce(actions: Dict[str, Any]) -> str:
        for _ in range(20):
            nonce = os.urandom(5).hex()
            if nonce not in actions:
                return nonce
        return str(int(datetime.now().timestamp() * 1000))[-10:]

    def _tg_console_status_data(self) -> Dict[str, Any]:
        token, chat_id, source = self._resolve_fusion_telegram_config()
        state = self._tg_console_state(chat_id=chat_id)
        chat_configured = bool(token and chat_id)
        last_error = state.get("last_error") or self._tg_console_last_error
        if not chat_configured and "Bot Token/Chat ID 未配置" in str(last_error or ""):
            last_error = ""
        return {
            "enabled": bool(self._tg_console_enabled),
            "poll_enabled": bool(self._tg_console_poll_enabled),
            "poll_interval": self._tg_console_poll_interval,
            "suppress_individual_notifications": bool(self._tg_console_suppress_individual_notifications),
            "chat_configured": chat_configured,
            "config_source": source,
            "config_hint": (source if chat_configured and source else "未找到可用 Telegram 通知渠道，融合卡暂未创建"),
            "date": state.get("date") or "",
            "chat_id": state.get("chat_id") or "",
            "message_id": state.get("message_id") or 0,
            "card_id": (state.get("fusion_card") or {}).get("card_id") or "",
            "card_generation": (state.get("fusion_card") or {}).get("generation") or 0,
            "card_lifecycle": (state.get("fusion_card") or {}).get("lifecycle") or "awaiting_create",
            "card_can_update": can_update_fusion_card(state.get("fusion_card")),
            "last_update_id": state.get("last_update_id") or 0,
            "notice_count": len(state.get("notices") or []),
            "pending_count": len([x for x in (state.get("pending_actions") or {}).values() if x.get("confirm_for")]),
            "last_error": last_error,
            "notices": (state.get("notices") or [])[:5],
        }

    def _tg_console_action_status_data(self, code: int, msg: str) -> Dict[str, Any]:
        data = self._tg_console_status_data()
        data["code"] = int(code)
        data["msg"] = str(msg or "")
        data["success"] = int(code) == 0
        if int(code) != 0 and msg and not data.get("last_error"):
            data["last_error"] = str(msg)
        return data
