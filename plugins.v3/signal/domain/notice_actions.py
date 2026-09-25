"""Pure protocol for actions attached to ordinary notifications."""
import hashlib
import json
import re

SCHEMA = "signal-notice-actions/v1"
STATE_KEY = "notice_actions_v1"
TTL_SECONDS = 7 * 86400
PAGE_SIZE = 6
MAX_RECORDS = 200
COMPONENTS = {"plugin_update": "plugin_update_reminder", "mp_update": "mp_update",
              "site_stat": "site_stat", "market_update": "market_update"}
ACTIONS = {"details", "back", "page", "install", "remind", "ignore", "mp", "refresh", "sync"}
ACTIVE = {"running", "pending", "uncertain"}


def callback_data(nonce, action, index=None):
    value = f"[PLUGIN]Signal|sn1:{nonce}:{action}"
    if index is not None:
        value += f":{int(index)}"
    if len(value.encode("utf-8")) > 64:
        raise ValueError("Notification callback is too long")
    return value


def parse_callback(value):
    match = re.fullmatch(r"sn1:([A-Za-z0-9_-]{8,24}):([a-z]+)(?::([0-9]{1,4}))?", str(value or ""))
    if not match or match[2] not in ACTIONS:
        return None
    return match[1], match[2], int(match[3]) if match[3] is not None else None


def target_key(source, target):
    raw = [str(source), str(target.get("id") or ""), str(target.get("repo_url") or "")]
    return hashlib.sha256(json.dumps(raw, ensure_ascii=False).encode("utf-8")).hexdigest()


def target_identity(target):
    return tuple(str(target.get(key) or "") for key in ("id", "repo_url", "new"))


def new_state(value):
    if not isinstance(value, dict) or value.get("schema") != SCHEMA:
        return {"schema": SCHEMA, "records": {}, "ignored_versions": {}}
    return {"schema": SCHEMA,
            "records": dict(value.get("records") or {}),
            "ignored_versions": dict(value.get("ignored_versions") or {})}


def prune(state, now):
    records = state["records"]
    for key, record in list(records.items()):
        if not isinstance(record, dict) or (record.get("status") not in ACTIVE and float(record.get("expires_at", 0)) < now):
            records.pop(key, None)
    removable = sorted((key for key in records if records[key].get("status") not in ACTIVE),
                       key=lambda key: records[key].get("created_at", 0))
    for key in removable[:max(0, len(records) - MAX_RECORDS)]:
        records.pop(key, None)
    return state


def split_text(text, limit=3400):
    """Keep Telegram's UTF-16-sized text limit without slicing surrogate pairs."""
    pages, chars, units = [], [], 0
    for char in str(text or "暂无明细"):
        size = len(char.encode("utf-16-le")) // 2
        if units + size > limit:
            pages.append("".join(chars))
            chars, units = [], 0
        chars.append(char)
        units += size
    if chars:
        pages.append("".join(chars))
    return pages or ["暂无明细"]
