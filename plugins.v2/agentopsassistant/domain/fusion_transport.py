"""Pure Telegram transport payloads for the persistent V7 Fusion card."""

from copy import deepcopy
from typing import Any, Dict, Optional


def build_send_rich_message_payload(
    chat_id: Any,
    rich_message: Dict[str, Any],
    reply_markup: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    payload = {"chat_id": chat_id, "rich_message": _validate_rich_message(rich_message)}
    if reply_markup is not None:
        payload["reply_markup"] = deepcopy(reply_markup)
    return payload


def build_edit_message_text_payload(
    chat_id: Any,
    message_id: Any,
    rich_message: Dict[str, Any],
    reply_markup: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    message_key = _positive_int(message_id)
    if not message_key:
        raise ValueError("message_id must be positive for editMessageText")
    payload = {
        "chat_id": chat_id,
        "message_id": message_key,
        "rich_message": _validate_rich_message(rich_message),
    }
    if reply_markup is not None:
        payload["reply_markup"] = deepcopy(reply_markup)
    return payload


def build_send_rich_message_draft_payload(
    chat_id: Any,
    draft_id: Any,
    rich_message: Dict[str, Any],
) -> Dict[str, Any]:
    draft_key = _positive_int(draft_id)
    if not draft_key:
        raise ValueError("draft_id must be positive for sendRichMessageDraft")
    return {
        "chat_id": chat_id,
        "draft_id": draft_key,
        "rich_message": _validate_rich_message(rich_message),
    }


def _validate_rich_message(value: Any) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError("rich_message must be an object")
    sources = [key for key in ("html", "markdown", "blocks") if key in value]
    if sources != ["blocks"]:
        raise ValueError("V7 transport requires exactly the explicit blocks source")
    if not isinstance(value.get("blocks"), list) or not value["blocks"]:
        raise ValueError("rich_message.blocks must be a non-empty list")
    return deepcopy(value)


def _positive_int(value: Any) -> int:
    try:
        parsed = int(value or 0)
    except (TypeError, ValueError):
        return 0
    return parsed if parsed > 0 else 0
