"""Owner-scoped realtime updates for the V7 active card."""

from copy import deepcopy
from typing import Any, Dict, Optional

from .fusion_card_model import remove_v7_module, replace_v7_module, validate_v7_card_model


STREAM_OWNERS = {"realtime-media", "realtime-task-backup"}


def apply_v7_realtime_update(
    model: Dict[str, Any],
    owner: str,
    module: Optional[Dict[str, Any]] = None,
    *,
    active: bool = True,
) -> Dict[str, Any]:
    """Replace or remove only one streaming owner in a validated card model."""
    owner_key = str(owner or "").strip()
    if owner_key not in STREAM_OWNERS:
        raise ValueError(f"unsupported realtime owner: {owner_key}")
    current = validate_v7_card_model(model)
    if not active or not isinstance(module, dict):
        result = remove_v7_module(current, owner_key)
    else:
        replacement = deepcopy(module)
        replacement.update({
            "owner": owner_key,
            "tier": "realtime",
            "streaming": True,
            "always_visible_preview": False,
            "preview_rows": list(replacement.get("preview_rows") or []),
            "details_rows": list(replacement.get("details_rows") or []),
        })
        result = replace_v7_module(current, owner_key, replacement)
    if current.get("state") != "alert":
        has_realtime = any(item.get("owner") in STREAM_OWNERS for item in result.get("modules") or [])
        result["state"] = "active" if has_realtime else "normal"
    return validate_v7_card_model(result)
