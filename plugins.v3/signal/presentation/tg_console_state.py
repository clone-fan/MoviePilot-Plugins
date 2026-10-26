import hashlib
import json
import re
import os
from copy import deepcopy
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
    fusion_card_day,
    normalize_fusion_card_state,
    resume_fusion_card,
    retire_fusion_card,
    sanitize_fusion_persisted_state,
)
from ..domain.fusion_event_ledger import empty_event_ledger, normalize_event_ledger
from ..domain.update_jobs import normalize_update_center_state
from ..domain import site_helpers


class TgConsoleStateMixin:
    """Telegram console state management, action registration, status data"""

    @classmethod
    def _normalize_site_diagnostic(cls, records: Any) -> List[Dict[str, Any]]:
        if not isinstance(records, list):
            return []
        sources = {"render", "unknown", "site_stat_manual", "site_stat_scheduled", "fusion_create_manual", "fusion_create_scheduled", "fusion_refresh"}
        def enum(value, allowed, default):
            return value if isinstance(value, str) and value in allowed else default

        result = []
        for record in [item for item in records if isinstance(item, dict)][-5:]:
            raw_sites = record.get("sites") if isinstance(record.get("sites"), list) else []
            valid_sites = [item for item in raw_sites if isinstance(item, dict)]
            sites = []
            for item in valid_sites[:50]:
                raw_domain = item.get("domain") if isinstance(item.get("domain"), str) else ""
                try:
                    domain = site_helpers.normalize_site_domain(raw_domain)
                except ValueError:
                    domain = ""
                site = {
                    "name": cls._site_safe_name(item.get("name") if isinstance(item.get("name"), str) else ""),
                    "domain": domain,
                    "status": enum(item.get("status"), {"ok", "fault", "unavailable", "checker_error"}, "checker_error"),
                    "reason_code": item.get("reason_code") if isinstance(item.get("reason_code"), str) and item["reason_code"] in cls.SITE_STAT_REASONS else "checker_error",
                    "baseline_status": enum(item.get("baseline_status"), {"ready", "missing", "invalid", "discontinuous", "counter_reset"}, "invalid"),
                    "snapshot_day": cls._site_timestamp(str(item.get("snapshot_day") or "") + " 00:00:00")[:10],
                    "snapshot_at": cls._site_timestamp(item.get("snapshot_at")),
                    "baseline_day": cls._site_timestamp(str(item.get("baseline_day") or "") + " 00:00:00")[:10],
                    "refresh_status": enum(item.get("refresh_status"), {"ok", "fault", "checker_error", "running", "timeout", "error", "unknown"}, "unknown"),
                    "refresh_at": cls._site_timestamp(item.get("refresh_at")),
                    "refresh_source": enum(item.get("refresh_source"), sources - {"render", "unknown"}, ""),
                }
                sites.append(site)
            try:
                omitted = max(0, int(record.get("omitted_count") or 0))
            except (TypeError, ValueError, OverflowError):
                omitted = 0
            fingerprint = str(record.get("fingerprint") or "")
            result.append({"source": enum(record.get("source"), sources, "render"),
                           "observed_at": cls._site_timestamp(record.get("observed_at")),
                           "fingerprint": fingerprint if re.fullmatch(r"[0-9a-fA-F]{64}", fingerprint) else "",
                           "omitted_count": omitted + max(0, len(valid_sites) - 50), "sites": sites})
        return result

    def _tg_console_state(self, chat_id: str = "") -> Dict[str, Any]:
        today = self._today_prefix()
        state = self.get_data("tg_console_state") or {}
        if not isinstance(state, dict):
            state = {}
        state = sanitize_fusion_persisted_state(state)
        normalized_update_state = normalize_update_center_state(state)
        update_state_changed = normalized_update_state.get("update_jobs") != state.get("update_jobs")
        state = normalized_update_state
        previous_message_id = self._safe_int(state.get("message_id"), 0, 0)
        previous_card = state.get("fusion_card")
        state_chat_id = str(state.get("chat_id") or "")
        target_chat_id = str(chat_id or state_chat_id)
        update_actions = state.get("fusion_update_actions")
        if not isinstance(update_actions, dict) or state_chat_id != target_chat_id:
            update_actions = {}
        diagnostic = self._normalize_site_diagnostic(state.get("site_diagnostic")) if state_chat_id and target_chat_id and state_chat_id == target_chat_id else []
        changed = update_state_changed or state.get("site_diagnostic") != diagnostic or "site_refresh" in state
        state.pop("site_refresh", None)
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
                "active_tab": "overview",
                "tab_touched": False,
                "running_actions": {},
                "pending_actions": {},
                "fusion_update_actions": update_actions,
                "update_jobs": deepcopy(state.get("update_jobs") or {}),
                "fusion_card_gc": deepcopy(state.get("fusion_card_gc") or []),
                "last_error": "",
                "fusion_card": previous_card,
                "v7_event_ledger": empty_event_ledger(today),
                "site_diagnostic": diagnostic,
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
            state["active_tab"] = self._normalize_fusion_tab(state.get("active_tab") or "overview")
            state.setdefault("tab_touched", False)
            state.setdefault("running_actions", {})
            state.setdefault("pending_actions", {})
            state.setdefault("last_error", "")
            state.setdefault("fusion_card", previous_card)
            ledger = normalize_event_ledger(state.get("v7_event_ledger"), today)
            if state.get("v7_event_ledger") != ledger:
                changed = True
            state["v7_event_ledger"] = ledger
            state["site_diagnostic"] = diagnostic
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
        if card.get("lifecycle") == "retired" and card.get("retirement_reason") == "day-rolled":
            self._queue_fusion_card_gc(state, card)
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
        same_day = fusion_card_day(previous_card) == today
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
            "active_tab": "overview",
            "tab_touched": False,
            "running_actions": {},
            "pending_actions": {},
            "fusion_update_actions": deepcopy(previous.get("fusion_update_actions") or {}),
            "update_jobs": deepcopy(previous.get("update_jobs") or {}),
            "fusion_card_gc": deepcopy(previous.get("fusion_card_gc") or []),
            "last_error": "",
            "fusion_card": fusion_card,
            "v7_event_ledger": normalize_event_ledger(previous.get("v7_event_ledger"), today),
            "site_diagnostic": self._normalize_site_diagnostic(previous.get("site_diagnostic")),
        }

    def _save_tg_console_state(self, state: Dict[str, Any]) -> None:
        # 显式清空标记（重置卡片状态）先摘出来：它是本次写入的意图，不落盘。
        notices_cleared = bool(state.pop("notices_cleared", False))
        normalized = normalize_update_center_state(state)
        state.clear()
        state.update(normalized)
        sanitized = sanitize_fusion_persisted_state(state)
        sanitized["site_diagnostic"] = self._normalize_site_diagnostic(sanitized.get("site_diagnostic"))
        sanitized.pop("site_refresh", None)
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
        state["fusion_card_gc"] = [
            item for item in (state.get("fusion_card_gc") or [])
            if isinstance(item, dict) and self._safe_int(item.get("message_id"), 0, 0)
        ][-5:]
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
        latest = self.get_data("tg_console_state")
        if isinstance(latest, dict):
            latest_card = normalize_fusion_card_state(
                latest.get("fusion_card"),
                enabled=bool(getattr(self, "_fusion_notify_enabled", False)),
            )
            if self._fusion_card_supersedes(latest_card, card):
                # 持久化里的当天卡片比本次快照新：旧快照不能把身份顶回旧卡。
                state["fusion_card"] = latest_card
                state["message_id"] = latest_card.get("message_id", 0) if can_update_fusion_card(latest_card) else 0
            latest_date = str(latest.get("date") or "")
            incoming_date = str(state.get("date") or "")
            stale_day = bool(latest_date and incoming_date and latest_date > incoming_date)
            if stale_day:
                # 陈旧快照（例如跨零点仍未结束的长轮询）不能把日期写回昨天，
                # 否则后续所有逻辑都会按昨天的日期重建，卡片指针跟着一起错。
                state["date"] = latest_date
                incoming_date = latest_date
            if stale_day:
                # 昨天的快照带着昨天的通知，跨天之后一律由当天状态说了算。
                state["notices"] = list(latest.get("notices") or [])[:self._tg_console_max_notices]
            elif notices_cleared:
                # 重置入口显式清空：写入方意图就是空列表，不能把旧通知并回来。
                state["notices"] = notices[:self._tg_console_max_notices]
            elif not latest_date or incoming_date == latest_date:
                # 只有同一天的陈旧快照才取并集，避免丢掉当天刚产生的通知；
                # 新一天的第一笔写入从空列表开始，不继承昨天的通知。
                merged = self._merge_fusion_notices(latest.get("notices"), state.get("notices"))
                if merged:
                    state["notices"] = merged[:self._tg_console_max_notices]
            merged_done = self._merge_fusion_card_gc_done(
                latest.get("fusion_card_gc_done"), state.get("fusion_card_gc_done"))
            state["fusion_card_gc_done"] = merged_done[-20:]
            merged_gc = self._merge_fusion_card_gc(latest.get("fusion_card_gc"), state.get("fusion_card_gc"),
                                                   merged_done)
            state["fusion_card_gc"] = merged_gc[-5:]
        self.save_data("tg_console_state", state)

    def _merge_fusion_card_gc_done(self, latest: Any, incoming: Any) -> list:
        """合并「已处理」名单：陈旧快照不能把已经销毁的旧卡重新塞回队列。"""
        ids = []
        for source in (latest, incoming):
            for item in (source or []):
                message_id = self._safe_int(item, 0, 0)
                if message_id:
                    ids.append(message_id)
        return list(dict.fromkeys(ids))

    def _merge_fusion_card_gc(self, latest: Any, incoming: Any, done: Any = None) -> list:
        """合并待销毁队列：旧快照整份覆盖保存时，不能把还没销毁的旧卡从队列里弄丢。"""
        done_ids = {self._safe_int(item, 0, 0) for item in (done or [])}
        rows: Dict[int, Dict[str, Any]] = {}
        order: list = []
        for source in (latest, incoming):
            for item in (source or []):
                if not isinstance(item, dict):
                    continue
                message_id = self._safe_int(item.get("message_id"), 0, 0)
                if not message_id or message_id in done_ids:
                    continue
                if message_id not in rows:
                    rows[message_id] = dict(item)
                    order.append(message_id)
                    continue
                base = rows[message_id]
                base["attempts"] = max(
                    self._safe_int(base.get("attempts"), 0, 0),
                    self._safe_int(item.get("attempts"), 0, 0),
                )
        return [rows[message_id] for message_id in order]

    @staticmethod
    def _merge_fusion_notices(latest: Any, incoming: Any) -> list:
        """合并双方通知列表：按（标题, 时间）取并集，旧快照写入时不丢当天新通知。"""
        rows = []
        seen = set()
        for source in (latest, incoming):
            for item in (source or []):
                if not isinstance(item, dict):
                    continue
                key = (str(item.get("title") or ""), str(item.get("updated_at") or item.get("time") or ""))
                if key in seen:
                    continue
                seen.add(key)
                rows.append(item)
        rows.sort(key=lambda item: str(item.get("updated_at") or item.get("time") or ""), reverse=True)
        return rows

    @staticmethod
    def _fusion_card_supersedes(latest: Any, incoming: Any) -> bool:
        """持久化卡片是否应当压过本次写入：新卡永远赢，旧快照不能复活旧卡。"""
        if not isinstance(latest, dict) or not isinstance(incoming, dict):
            return False
        latest_writable = can_update_fusion_card(latest)
        if not latest_writable:
            return False
        if not can_update_fusion_card(incoming):
            return True
        try:
            return int(latest.get("generation") or 0) > int(incoming.get("generation") or 0)
        except (TypeError, ValueError):
            return False

    def _queue_fusion_card_gc(self, state: Dict[str, Any], card: Any) -> None:
        """旧卡退役后登记待销毁，避免删除失败后残留一张永远不更新的卡。"""
        if not isinstance(card, dict):
            return
        message_id = self._safe_int(card.get("message_id"), 0, 0)
        if not message_id:
            return
        entries = [item for item in (state.get("fusion_card_gc") or []) if isinstance(item, dict)]
        if any(self._safe_int(item.get("message_id"), 0, 0) == message_id for item in entries):
            return
        entries.append({
            "message_id": message_id,
            "card_id": str(card.get("card_id") or ""),
            "retired_at": str(card.get("retired_at") or ""),
        })
        state["fusion_card_gc"] = entries[-5:]

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

    def _tg_console_capture_fusion_update_action(self, action: Dict[str, Any], *, title: str = "", text: str = "",
                                                state: Optional[Dict[str, Any]] = None) -> bool:
        """Persist only real, manual update candidates so the fusion card can offer inline actions."""
        if not isinstance(action, dict):
            return False
        kind = str(action.get("kind") or "").strip()
        if kind not in {"plugin_update", "mp_update", "market_update"}:
            return False
        payload = dict(action.get("payload") or {})
        if kind == "plugin_update":
            plugins = [dict(item) for item in (payload.get("plugins") or [])
                       if isinstance(item, dict) and not item.get("completed") and not item.get("blocked")
                       and all(str(item.get(key) or "") for key in ("id", "old", "new", "repo_url"))]
            payload = {"plugins": plugins}
            keep = bool(plugins)
        elif kind == "market_update":
            markets = [str(item).strip() for item in (payload.get("markets") or []) if str(item).strip()]
            payload = {"markets": markets}
            keep = bool(markets)
        else:
            checks = [dict(item) for item in (payload.get("checks") or []) if isinstance(item, dict)]
            payload = {"checks": checks}
            # 没有真实可执行检查项时不能留下空壳按钮；空 payload 会移除旧候选。
            keep = bool(checks)
        persist = state is None
        if persist:
            state = self._tg_console_state()
        candidates = state.setdefault("fusion_update_actions", {})
        if keep:
            candidates[kind] = {
                "kind": kind,
                "payload": payload,
                "title": str(title or "").strip()[:200],
                "text": str(text or "").strip()[:500],
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
        else:
            candidates.pop(kind, None)
        if persist:
            self._save_tg_console_state(state)
        return True

    def _tg_console_ensure_fusion_action(self, state: Dict[str, Any], kind: str, payload: Dict[str, Any],
                                         label: str) -> str:
        """Return a stable nonce for one fusion-card update action payload."""
        raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
        action_key = f"fusion-update:{kind}:{hashlib.sha256(raw.encode('utf-8')).hexdigest()[:16]}"
        actions = state.setdefault("pending_actions", {})
        for nonce, item in actions.items():
            if item.get("action_key") == action_key and not item.get("done"):
                return str(nonce)
        nonce = self._tg_console_new_nonce(actions)
        now = datetime.now().timestamp()
        actions[nonce] = {
            "action": "fusion_update_action",
            "action_key": action_key,
            "fusion_update": True,
            "kind": kind,
            "payload": dict(payload),
            "label": str(label or "").strip()[:80],
            "created_at": now,
            "expires_at": now + 7 * 86400,
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
            "render_state": state.get("v7_state") or "",
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
