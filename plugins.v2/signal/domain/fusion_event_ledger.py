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
    normalized = event.to_record()
    payload = normalized.get("payload") if isinstance(normalized.get("payload"), dict) else {}
    stable_fields = {"task_key", "task_group", "execution_count", "last_result_at"}
    has_stable_fields = any(field in payload for field in stable_fields)
    if has_stable_fields:
        payload["task_key"] = str(payload.get("task_key") or "").strip()
        payload["task_group"] = str(payload.get("task_group") or "").strip()
        try:
            payload["execution_count"] = max(1, int(payload.get("execution_count") or 1))
        except (TypeError, ValueError):
            payload["execution_count"] = 1
    normalized["payload"] = payload
    return normalized


def _task_key(event: Dict[str, Any]) -> str:
    payload = event.get("payload") if isinstance(event.get("payload"), dict) else {}
    return str(payload.get("task_key") or "").strip()


def _is_success_event(event: Dict[str, Any]) -> bool:
    return str(event.get("event_type") or "") == "completion" and str(event.get("result_status") or "") == "success"


def _is_anomaly_event(event: Dict[str, Any]) -> bool:
    return str(event.get("event_type") or "") == "anomaly" and str(event.get("result_status") or "") == "error"


def _execution_count(event: Dict[str, Any]) -> int:
    payload = event.get("payload") if isinstance(event.get("payload"), dict) else {}
    try:
        return max(1, int(payload.get("execution_count") or 1))
    except (TypeError, ValueError):
        return 1


def _merge_success_event(previous: Dict[str, Any], current: Dict[str, Any]) -> Dict[str, Any]:
    merged = deepcopy(current)
    payload = merged.get("payload") if isinstance(merged.get("payload"), dict) else {}
    previous_payload = previous.get("payload") if isinstance(previous.get("payload"), dict) else {}
    payload["task_key"] = str(payload.get("task_key") or previous_payload.get("task_key") or "").strip()
    payload["task_group"] = str(payload.get("task_group") or previous_payload.get("task_group") or "").strip()
    payload["execution_count"] = _execution_count(previous) + _execution_count(current)
    payload["last_result_at"] = str(current.get("created_at") or previous_payload.get("last_result_at") or "").strip()
    merged["payload"] = payload
    return merged


def _insert_or_merge(events: List[Dict[str, Any]], event: Dict[str, Any], limit: int) -> List[Dict[str, Any]]:
    key = _task_key(event)
    if key and _is_success_event(event):
        # A successful execution clears the current anomaly for the same task.
        events = [item for item in events if not (_task_key(item) == key and _is_anomaly_event(item))]
        for index, previous in enumerate(events):
            if _task_key(previous) == key and _is_success_event(previous):
                events[index] = _merge_success_event(previous, event)
                return events[:max(1, int(limit or FUSION_EVENT_LEDGER_LIMIT))]
    elif key and _is_anomaly_event(event):
        events = [item for item in events if not (_task_key(item) == key and _is_anomaly_event(item))]
    return [deepcopy(event), *events][:max(1, int(limit or FUSION_EVENT_LEDGER_LIMIT))]


def normalize_event_ledger(raw: Any, event_date: str, limit: int = FUSION_EVENT_LEDGER_LIMIT) -> Dict[str, Any]:
    today = str(event_date or "").strip()
    result = empty_event_ledger(today)
    if not isinstance(raw, dict) or str(raw.get("date") or "").strip() != today:
        return result
    seen = set()
    normalized_events = []
    for item in raw.get("events") or []:
        event = normalize_actual_task_event(item, today)
        event_id = str((event or {}).get("event_id") or "")
        if not event or event_id in seen:
            continue
        seen.add(event_id)
        normalized_events.append(event)
    normalized_events.sort(key=lambda item: (
        str(item.get("created_at") or ""),
        str(item.get("event_id") or ""),
    ))
    for event in normalized_events:
        result["events"] = _insert_or_merge(result["events"], event, limit)
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
    ledger["events"] = _insert_or_merge(ledger["events"], event, limit)
    return ledger, True


def event_ledger_rows(raw: Any, event_date: str, limit: int = FUSION_EVENT_LEDGER_LIMIT) -> List[Dict[str, Any]]:
    ledger = normalize_event_ledger(raw, event_date, limit=limit)
    rows = []
    for event in ledger["events"]:
        task = normalize_completion_task(event)
        if task:
            rows.append(task)
    return rows
