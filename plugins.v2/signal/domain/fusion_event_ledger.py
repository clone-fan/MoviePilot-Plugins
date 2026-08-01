"""Persistent same-day ledger for actual Fusion task events."""

from copy import deepcopy
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from .fusion_completion import normalize_completion_task
from .fusion_event import FUSION_EVENT_SCHEMA, FusionEvent


FUSION_EVENT_LEDGER_SCHEMA = "signal-fusion-event-ledger/v1"
FUSION_EVENT_LEDGER_LIMIT = 20
ACTUAL_EVENT_OWNERS = {"today-completion", "current-anomalies"}
ACTUAL_EVENT_TYPES = {"completion", "anomaly"}


def current_event_date() -> str:
    return datetime.now().astimezone().date().isoformat()


def empty_event_ledger(event_date: str) -> Dict[str, Any]:
    return {"schema": FUSION_EVENT_LEDGER_SCHEMA, "date": str(event_date or "").strip(), "events": []}


def normalize_actual_task_event(record: Any, event_date: str) -> Optional[Dict[str, Any]]:
    if not isinstance(record, dict) or not str(record.get("event_id") or "").strip():
        return None
    schema = str(record.get("schema") or "").strip()
    if schema != FUSION_EVENT_SCHEMA:
        return None
    try:
        event = FusionEvent.from_record(record)
    except (TypeError, ValueError):
        return None
    if event.event_date != str(event_date or "").strip():
        return None
    if event.execution_status != "executed":
        return None
    if event.owner not in ACTUAL_EVENT_OWNERS or event.event_type not in ACTUAL_EVENT_TYPES:
        return None
    if event.event_type == "anomaly" and event.result_status != "error":
        return None
    return event.to_record()


def normalize_event_ledger(raw: Any, event_date: str, limit: int = FUSION_EVENT_LEDGER_LIMIT) -> Dict[str, Any]:
    today = str(event_date or "").strip()
    result = empty_event_ledger(today)
    if not isinstance(raw, dict) or str(raw.get("date") or "").strip() != today:
        return result
    seen = set()
    for item in raw.get("events") or []:
        event = normalize_actual_task_event(item, today)
        event_id = str((event or {}).get("event_id") or "")
        if not event or event_id in seen:
            continue
        seen.add(event_id)
        result["events"].append(event)
        if len(result["events"]) >= max(1, int(limit or FUSION_EVENT_LEDGER_LIMIT)):
            break
    return result


def append_actual_task_event(
    raw: Any,
    record: Any,
    event_date: str,
    limit: int = FUSION_EVENT_LEDGER_LIMIT,
) -> Tuple[Dict[str, Any], bool]:
    ledger = normalize_event_ledger(raw, event_date, limit=limit)
    event = normalize_actual_task_event(record, event_date)
    if not event:
        return ledger, False
    event_id = str(event.get("event_id") or "")
    if any(str(item.get("event_id") or "") == event_id for item in ledger["events"]):
        return ledger, False
    ledger["events"] = [deepcopy(event), *ledger["events"]][:max(1, int(limit or FUSION_EVENT_LEDGER_LIMIT))]
    return ledger, True


def event_ledger_rows(raw: Any, event_date: str, limit: int = FUSION_EVENT_LEDGER_LIMIT) -> List[Dict[str, str]]:
    ledger = normalize_event_ledger(raw, event_date, limit=limit)
    rows = []
    for event in ledger["events"]:
        task = normalize_completion_task(event)
        if task:
            rows.append(task)
    return rows
