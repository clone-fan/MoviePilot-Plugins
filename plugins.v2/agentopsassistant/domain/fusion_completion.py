"""Canonical, presentation-neutral Today Completion task rows."""

import re
from typing import Any, Dict, Iterable, List, Optional


GENERIC_OUTCOMES = {"完成", "成功", "已完成", "任务完成", "执行完成"}
NON_EXECUTION_MARKERS = ("预览", "未执行", "已跳过", "无需处理", "未配置", "未启用", "no-op", "skip")


def normalize_completion_task(value: Any) -> Optional[Dict[str, str]]:
    if isinstance(value, dict):
        title = _compact(value.get("title"))
        outcome = _without_time(value.get("outcome"))
        result_status = str(value.get("result_status") or "").strip().lower()
        if result_status not in {"success", "error"}:
            result_status = "error" if str(value.get("event_type") or "") == "anomaly" else "success"
    else:
        return None
    if not title or not outcome or outcome in GENERIC_OUTCOMES:
        return None
    lowered = f"{title} {outcome}".lower()
    if any(marker.lower() in lowered for marker in NON_EXECUTION_MARKERS):
        return None
    return {"title": title, "outcome": outcome, "result_status": result_status}


def normalize_completion_tasks(values: Any) -> List[Dict[str, str]]:
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
