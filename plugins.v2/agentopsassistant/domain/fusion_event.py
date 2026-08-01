"""Typed event envelope for the single Fusion Notification outbound owner."""

from copy import deepcopy
from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Any, Dict, Optional
from uuid import uuid4


FUSION_EVENT_SCHEMA = "agentopsassistant-fusion-event/v2"
FUSION_EVENT_OWNERS = {
    "site_stats", "download_transfer", "subscribe", "storage", "media",
    "health", "maintenance", "current-anomalies", "realtime-media",
    "realtime-task-backup", "persistent-sites", "persistent-storage",
    "persistent-subscriptions", "today-completion", "card-creation",
}
FUSION_EVENT_TYPES = {"snapshot", "realtime", "anomaly", "completion", "loading", "refresh"}
FUSION_EVENT_LEVELS = {"info", "success", "warning", "error", "idle"}
FUSION_EVENT_EXECUTION_STATUSES = {"executed", "skipped", "no-op"}
FUSION_EVENT_RESULT_STATUSES = {"success", "error"}
SENSITIVE_EVENT_KEYS = {
    "api_key", "api_token", "authorization", "bot_token", "cookie",
    "telegram_bot_token", "password", "secret",
    "telegram_token", "token",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _local_date() -> str:
    return datetime.now().astimezone().date().isoformat()


def _event_date(value: Any, created_at: Any = "") -> str:
    candidate = str(value or "").strip()
    if not candidate:
        created = str(created_at or "").strip()
        candidate = created[:10] if len(created) >= 10 else datetime.now(timezone.utc).date().isoformat()
    try:
        parsed = date.fromisoformat(candidate)
    except ValueError as exc:
        raise ValueError("Fusion event date must use YYYY-MM-DD") from exc
    if parsed.isoformat() != candidate:
        raise ValueError("Fusion event date must use YYYY-MM-DD")
    return candidate


def _result_for_level(level: Any) -> str:
    return "error" if str(level or "").strip() == "error" else "success"


def _is_sensitive_key(value: Any) -> bool:
    key = str(value or "").strip().lower().replace("-", "_")
    return key in SENSITIVE_EVENT_KEYS or any(
        key.endswith(suffix) for suffix in ("_api_key", "_password", "_secret", "_token")
    )


def _redact_payload(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            str(key): _redact_payload(item)
            for key, item in value.items()
            if not _is_sensitive_key(key)
        }
    if isinstance(value, (list, tuple)):
        return [_redact_payload(item) for item in value]
    return deepcopy(value)


@dataclass(frozen=True)
class FusionEvent:
    owner: str
    event_type: str
    title: str
    body: str = ""
    level: str = "info"
    payload: Dict[str, Any] = field(default_factory=dict)
    component: str = ""
    realtime: bool = False
    execution_status: str = "executed"
    result_status: str = ""
    outcome: str = ""
    event_date: str = ""
    event_id: str = field(default_factory=lambda: uuid4().hex)
    created_at: str = field(default_factory=_now)

    def __post_init__(self) -> None:
        owner = str(self.owner or "").strip()
        event_type = str(self.event_type or "").strip()
        level = str(self.level or "info").strip()
        execution_status = str(self.execution_status or "").strip()
        result_status = str(self.result_status or "").strip() or _result_for_level(level)
        if owner not in FUSION_EVENT_OWNERS:
            raise ValueError(f"unsupported Fusion event owner: {owner}")
        if event_type not in FUSION_EVENT_TYPES:
            raise ValueError(f"unsupported Fusion event type: {event_type}")
        if level not in FUSION_EVENT_LEVELS:
            raise ValueError(f"unsupported Fusion event level: {level}")
        if execution_status not in FUSION_EVENT_EXECUTION_STATUSES:
            raise ValueError(f"unsupported Fusion execution status: {execution_status}")
        if result_status not in FUSION_EVENT_RESULT_STATUSES:
            raise ValueError(f"unsupported Fusion result status: {result_status}")
        if not str(self.title or "").strip():
            raise ValueError("Fusion event title is required")
        if not isinstance(self.payload, dict):
            raise TypeError("Fusion event payload must be a dict")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "event_type", event_type)
        object.__setattr__(self, "title", str(self.title or "").strip())
        object.__setattr__(self, "body", str(self.body or "").strip())
        object.__setattr__(self, "level", level)
        object.__setattr__(self, "payload", deepcopy(self.payload))
        object.__setattr__(self, "component", str(self.component or "").strip())
        object.__setattr__(self, "execution_status", execution_status)
        object.__setattr__(self, "result_status", result_status)
        object.__setattr__(self, "outcome", str(self.outcome or self.body or self.title).strip())
        object.__setattr__(self, "event_date", _event_date(self.event_date, self.created_at))
        object.__setattr__(self, "event_id", str(self.event_id or uuid4().hex).strip())
        object.__setattr__(self, "created_at", str(self.created_at or _now()).strip())

    @classmethod
    def create(
        cls,
        *,
        owner: str,
        event_type: str,
        title: str,
        body: str = "",
        level: str = "info",
        payload: Optional[Dict[str, Any]] = None,
        component: str = "",
        realtime: bool = False,
        execution_status: str = "executed",
        result_status: Optional[str] = None,
        outcome: str = "",
        event_date: str = "",
    ) -> "FusionEvent":
        return cls(
            owner=str(owner or "").strip(),
            event_type=str(event_type or "").strip(),
            title=str(title or "").strip(),
            body=str(body or "").strip(),
            level=str(level or "info").strip(),
            payload=deepcopy(payload or {}),
            component=str(component or "").strip(),
            realtime=bool(realtime),
            execution_status=str(execution_status or "").strip(),
            result_status=str(result_status or "").strip(),
            outcome=str(outcome or "").strip(),
            event_date=str(event_date or _local_date()).strip(),
        )

    @classmethod
    def from_record(cls, record: Dict[str, Any]) -> "FusionEvent":
        if not isinstance(record, dict):
            raise TypeError("Fusion event record must be a dict")
        schema = str(record.get("schema") or "").strip()
        if schema != FUSION_EVENT_SCHEMA:
            raise ValueError(f"unsupported Fusion event schema: {schema}")
        level = str(record.get("level") or "info").strip()
        body = str(record.get("text") or record.get("body") or "").strip()
        return cls(
            owner=str(record.get("owner") or "").strip(),
            event_type=str(record.get("event_type") or "").strip(),
            title=str(record.get("title") or "").strip(),
            body=body,
            level=level,
            payload=deepcopy(record.get("payload") or {}),
            component=str(record.get("component") or "").strip(),
            realtime=bool(record.get("realtime")),
            execution_status=str(record.get("execution_status") or "executed").strip(),
            result_status=str(record.get("result_status") or _result_for_level(level)).strip(),
            outcome=str(record.get("outcome") or body or record.get("title") or "").strip(),
            event_date=str(record.get("event_date") or "").strip(),
            event_id=str(record.get("event_id") or uuid4().hex).strip(),
            created_at=str(record.get("created_at") or _now()).strip(),
        )

    def to_record(self) -> Dict[str, Any]:
        return {
            "schema": FUSION_EVENT_SCHEMA,
            "event_id": self.event_id,
            "owner": self.owner,
            "event_type": self.event_type,
            "title": self.title,
            "text": self.body,
            "level": self.level,
            "payload": _redact_payload(self.payload),
            "component": self.component,
            "realtime": self.realtime,
            "execution_status": self.execution_status,
            "result_status": self.result_status,
            "outcome": self.outcome,
            "event_date": self.event_date,
            "created_at": self.created_at,
        }
