"""Canonical, presentation-neutral Today Completion task rows."""

import re
from typing import Any, Dict, Iterable, List, Optional


GENERIC_OUTCOMES = {"完成", "成功", "已完成", "任务完成", "执行完成"}
NON_EXECUTION_MARKERS = ("预览", "未执行", "已跳过", "无需处理", "未配置", "未启用", "no-op", "skip")


def normalize_completion_task(value: Any) -> Optional[Dict[str, Any]]:
    stable_fields = False
    if isinstance(value, dict):
        title = _compact(value.get("title"))
        outcome = _without_time(value.get("outcome"))
        result_status = str(value.get("result_status") or "").strip().lower()
        if result_status not in {"success", "error"}:
            result_status = "error" if str(value.get("event_type") or "") == "anomaly" else "success"
        payload = value.get("payload") if isinstance(value.get("payload"), dict) else {}
        stable_fields = any(key in payload or key in value for key in ("task_key", "task_group", "execution_count", "last_result_at"))
    elif isinstance(value, (list, tuple)) and value:
        first = _compact(value[0])
        parts = re.split(r"\s*[·｜|]\s*", first, maxsplit=1)
        title = parts[0] if parts else ""
        outcome = parts[1] if len(parts) > 1 else ""
        if not outcome:
            outcome = first
        if len(value) > 1:
            detail = _without_time(value[1])
            if detail and detail not in outcome:
                outcome = f"{outcome} · {detail}" if outcome else detail
        result_status = "success"
        payload = {}
    else:
        return None
    if not title or not outcome or outcome in GENERIC_OUTCOMES:
        return None
    lowered = f"{title} {outcome}".lower()
    if any(marker.lower() in lowered for marker in NON_EXECUTION_MARKERS):
        return None
    value_execution_count = value.get("execution_count") if isinstance(value, dict) else None
    try:
        execution_count = max(1, int(payload.get("execution_count") or value_execution_count or 1))
    except (TypeError, ValueError):
        execution_count = 1
    result = {
        "title": title,
        "outcome": outcome,
        "result_status": result_status,
    }
    if stable_fields:
        result.update({
            "task_key": str(payload.get("task_key") or value.get("component") or "").strip(),
            "task_group": str(payload.get("task_group") or "").strip(),
            "execution_count": execution_count,
            "last_time": str(payload.get("last_result_at") or value.get("created_at") or "").strip(),
        })
    return result


def normalize_completion_tasks(values: Any) -> List[Dict[str, Any]]:
    if not isinstance(values, (list, tuple)):
        return []
    tasks = []
    for value in values:
        task = normalize_completion_task(value)
        if task:
            tasks.append(task)
    return tasks


def _compact(value: Any) -> str:
    return " ".join(str(value or "").split()).strip()


def _without_time(value: Any) -> str:
    text = _compact(value)
    text = re.sub(r"(?<!\d)(?:[01]\d|2[0-3]):[0-5]\d(?!\d)", "", text)
    text = re.sub(r"^\s*[·｜|]\s*|\s*[·｜|]\s*$", "", text)
    return re.sub(r"\s{2,}", " ", text).strip(" ·｜|")


def _looks_like_time(value: Any) -> bool:
    return bool(re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", str(value or "").strip()))
