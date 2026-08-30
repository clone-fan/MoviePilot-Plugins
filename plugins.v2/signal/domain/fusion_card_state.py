"""Pure Fusion Notification active-card lifecycle and module ownership model."""

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional
from uuid import uuid4


FUSION_CARD_SCHEMA = "signal-fusion-card-state/v1"
FUSION_TIER_ORDER = ("identity", "anomalies", "realtime", "persistent", "completion", "footer")
FUSION_OWNER_ORDER = {
    "card": 0,
    "current-anomalies": 10,
    "realtime-media": 20,
    "realtime-task-backup": 21,
    "persistent-sites": 30,
    "persistent-subscriptions": 31,
    "persistent-storage": 32,
    "today-completion": 40,
    "card-footer": 50,
}
ACTIVE_LIFECYCLES = {"creating", "active"}
SENSITIVE_PERSISTED_KEYS = {
    "api_key",
    "api_token",
    "authorization",
    "bot_token",
    "cookie",
    "telegram_bot_token",
    "password",
    "secret",
    "telegram_token",
    "token",
}
LEGACY_TEMPLATE_PERSISTED_KEYS = {
    "html",
    "rich_html",
    "telegram_html",
    "template",
}


def _timestamp(now: Optional[datetime] = None) -> str:
    value = now or datetime.now(timezone.utc)
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def empty_fusion_card_state(now: Optional[datetime] = None) -> Dict[str, Any]:
    stamp = _timestamp(now)
    return {
        "schema": FUSION_CARD_SCHEMA,
        "lifecycle": "awaiting_create",
        "card_id": "",
        "generation": 0,
        "message_id": 0,
        "chat_id": "",
        "trigger": "",
        "created_at": "",
        "activated_at": "",
        "updated_at": stamp,
        "retired_at": "",
        "retirement_reason": "",
        "last_refresh_at": "",
        "tier_order": list(FUSION_TIER_ORDER),
        "modules": {},
        "previous_card": None,
    }


def sanitize_fusion_persisted_state(raw: Any) -> Dict[str, Any]:
    """Remove credential and legacy-template material before state persistence."""
    if not isinstance(raw, dict):
        return {}

    def clean(value: Any) -> Any:
        if isinstance(value, dict):
            result = {}
            for key, item in value.items():
                normalized = str(key or "").strip().lower()
                if normalized in SENSITIVE_PERSISTED_KEYS or normalized in LEGACY_TEMPLATE_PERSISTED_KEYS:
                    continue
                result[key] = clean(item)
            return result
        if isinstance(value, list):
            return [clean(item) for item in value]
        if isinstance(value, tuple):
            return [clean(item) for item in value]
        return deepcopy(value)

    return clean(raw)


def normalize_fusion_card_state(
    raw: Any,
    *,
    enabled: bool = True,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    stamp = _timestamp(now)
    state = deepcopy(raw) if isinstance(raw, dict) else {}
    if state.get("schema") != FUSION_CARD_SCHEMA:
        state = empty_fusion_card_state(now)
    state.setdefault("schema", FUSION_CARD_SCHEMA)
    state["generation"] = max(0, _positive_int(state.get("generation")))
    state["message_id"] = _positive_int(state.get("message_id"))
    state["chat_id"] = str(state.get("chat_id") or "")
    state["tier_order"] = list(FUSION_TIER_ORDER)
    state["modules"] = state.get("modules") if isinstance(state.get("modules"), dict) else {}
    state.setdefault("previous_card", None)
    for key in ("card_id", "trigger", "created_at", "activated_at", "retired_at", "retirement_reason", "last_refresh_at"):
        state[key] = str(state.get(key) or "")
    lifecycle = str(state.get("lifecycle") or "awaiting_create")
    if lifecycle not in {"awaiting_create", "creating", "active", "retired", "disabled"}:
        lifecycle = "awaiting_create"
    if lifecycle == "active" and not state["message_id"]:
        lifecycle = "retired"
        state["retired_at"] = state["retired_at"] or stamp
        state["retirement_reason"] = state["retirement_reason"] or "missing-message-id"
    if lifecycle == "creating" and state["message_id"]:
        lifecycle = "active"
        state["activated_at"] = state["activated_at"] or stamp
    if not enabled and lifecycle in ACTIVE_LIFECYCLES:
        lifecycle = "disabled"
        state["retired_at"] = state["retired_at"] or stamp
        state["retirement_reason"] = "fusion-disabled"
    state["lifecycle"] = lifecycle
    state["updated_at"] = stamp
    return state


def begin_fusion_card_creation(
    previous: Any,
    *,
    trigger: str,
    chat_id: str = "",
    card_id: str = "",
    reuse_active: bool = True,
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    stamp = _timestamp(now)
    old = normalize_fusion_card_state(previous, enabled=True, now=now)
    if reuse_active and not card_id and can_update_fusion_card(old):
        reused = deepcopy(old)
        reused.update({
            "lifecycle": "active",
            "trigger": str(trigger or reused.get("trigger") or "manual"),
            "updated_at": stamp,
            "last_refresh_at": stamp,
            "retired_at": "",
            "retirement_reason": "",
            "modules": {},
        })
        return reused
    previous_summary = None
    if old.get("card_id") or old.get("message_id"):
        previous_summary = {
            "card_id": old.get("card_id") or "",
            "message_id": old.get("message_id") or 0,
            "generation": old.get("generation") or 0,
            "retired_at": stamp,
            "retirement_reason": "replaced-by-create",
        }
    return {
        **empty_fusion_card_state(now),
        "lifecycle": "creating",
        "card_id": str(card_id or uuid4().hex),
        "generation": int(old.get("generation") or 0) + 1,
        "chat_id": str(chat_id or old.get("chat_id") or ""),
        "trigger": str(trigger or "manual"),
        "created_at": stamp,
        "updated_at": stamp,
        "previous_card": previous_summary,
    }


def activate_fusion_card(
    state: Any,
    *,
    message_id: Any,
    chat_id: str = "",
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    result = normalize_fusion_card_state(state, enabled=True, now=now)
    value = _positive_int(message_id)
    if not value:
        raise ValueError("message_id must be positive")
    stamp = _timestamp(now)
    result.update({
        "lifecycle": "active",
        "message_id": value,
        "chat_id": str(chat_id or result.get("chat_id") or ""),
        "activated_at": result.get("activated_at") or stamp,
        "updated_at": stamp,
        "retired_at": "",
        "retirement_reason": "",
    })
    return result


def retire_fusion_card(state: Any, *, reason: str, now: Optional[datetime] = None) -> Dict[str, Any]:
    result = normalize_fusion_card_state(state, enabled=True, now=now)
    stamp = _timestamp(now)
    result.update({
        "lifecycle": "retired",
        "retired_at": result.get("retired_at") or stamp,
        "retirement_reason": str(reason or "retired"),
        "updated_at": stamp,
    })
    return result


def disable_fusion_card(state: Any, *, now: Optional[datetime] = None) -> Dict[str, Any]:
    result = normalize_fusion_card_state(state, enabled=True, now=now)
    stamp = _timestamp(now)
    result.update({
        "lifecycle": "disabled",
        "retired_at": result.get("retired_at") or stamp,
        "retirement_reason": "fusion-disabled",
        "updated_at": stamp,
    })
    return result


def resume_fusion_card(state: Any, *, enabled: bool, now: Optional[datetime] = None) -> Dict[str, Any]:
    result = normalize_fusion_card_state(state, enabled=enabled, now=now)
    if enabled and result.get("lifecycle") == "creating" and not result.get("message_id"):
        return retire_fusion_card(result, reason="interrupted-create", now=now)
    return result


def can_update_fusion_card(state: Any) -> bool:
    return bool(isinstance(state, dict) and state.get("lifecycle") == "active" and _positive_int(state.get("message_id")))


def touch_fusion_card_refresh(state: Any, *, now: Optional[datetime] = None) -> Dict[str, Any]:
    result = normalize_fusion_card_state(state, enabled=True, now=now)
    if not can_update_fusion_card(result):
        return result
    stamp = _timestamp(now)
    result["last_refresh_at"] = stamp
    result["updated_at"] = stamp
    return result


def set_fusion_card_module(
    state: Any,
    *,
    owner: str,
    tier: str,
    value: Any,
    status: str = "ready",
    now: Optional[datetime] = None,
) -> Dict[str, Any]:
    owner_key = str(owner or "").strip()
    tier_key = str(tier or "").strip()
    if not owner_key:
        raise ValueError("owner is required")
    if tier_key not in FUSION_TIER_ORDER:
        raise ValueError(f"unsupported tier: {tier_key}")
    result = normalize_fusion_card_state(state, enabled=True, now=now)
    modules = dict(result.get("modules") or {})
    modules[owner_key] = {
        "owner": owner_key,
        "tier": tier_key,
        "status": str(status or "ready"),
        "value": deepcopy(value),
        "updated_at": _timestamp(now),
    }
    result["modules"] = modules
    result["updated_at"] = _timestamp(now)
    return result


def ordered_fusion_card_modules(state: Any) -> List[Dict[str, Any]]:
    data = normalize_fusion_card_state(state, enabled=True)
    tier_rank = {tier: index for index, tier in enumerate(FUSION_TIER_ORDER)}
    return sorted(
        (deepcopy(item) for item in (data.get("modules") or {}).values()),
        key=lambda item: (tier_rank.get(item.get("tier"), 999), FUSION_OWNER_ORDER.get(item.get("owner"), 999), item.get("owner", "")),
    )


def remove_fusion_card_modules(state: Any, owners: Iterable[str], *, now: Optional[datetime] = None) -> Dict[str, Any]:
    result = normalize_fusion_card_state(state, enabled=True, now=now)
    modules = dict(result.get("modules") or {})
    for owner in owners:
        modules.pop(str(owner or ""), None)
    result["modules"] = modules
    result["updated_at"] = _timestamp(now)
    return result


def _positive_int(value: Any) -> int:
    try:
        parsed = int(value or 0)
    except (TypeError, ValueError):
        return 0
    return parsed if parsed > 0 else 0
