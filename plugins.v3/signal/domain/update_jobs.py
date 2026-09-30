"""Pure state model for the unified Signal update center.

The update center covers MoviePilot updates, plugin updates, and plugin-market
synchronization. This module normalizes state and decides visibility/buttons;
host calls, Telegram edits, and threads stay outside the domain layer.
"""

from copy import deepcopy
from datetime import datetime, timezone
import time
import secrets
from typing import Any, Dict, List, Optional


UPDATE_KINDS = ("mp_update", "plugin_update", "market_update")
UPDATE_PHASES = {
    "idle", "checking", "available", "downloading", "ready", "installing",
    "updating", "syncing", "up_to_date", "success", "partial", "failed", "unconfigured",
}
RUNNING_PHASES = {"checking", "downloading", "installing", "updating", "syncing"}
ACTIONABLE_PHASES = {"unconfigured", "available", "ready", "partial", "failed"}
STALE_VISIBLE_PHASES = {"available", "ready"}
TERMINAL_PHASES = {"idle", "up_to_date", "success", "partial", "failed", "unconfigured"}

TERMINAL_TTL_SECONDS = {"up_to_date": 20, "success": 20, "partial": 600, "failed": 600}
RUNNING_TIMEOUT_SECONDS = 1800
PROGRESS_BUCKET_SIZE = 5

_KIND_ACTIONS = {
    "mp_update": {"available": ("download",), "ready": ("install",), "partial": ("check",), "failed": ("check",)},
    "plugin_update": {"unconfigured": ("sync_market",), "available": ("update_plugins",), "partial": ("check",), "failed": ("check",)},
    "market_update": {"unconfigured": ("sync_market",), "available": ("sync_market",), "failed": ("sync_market",)},
}

_DEFAULT_MESSAGES = {
    "mp_update": {
        "idle": "MoviePilot 已是最新版本。", "checking": "正在检查 MoviePilot 更新…",
        "available": "发现 MoviePilot 更新。", "downloading": "更新包下载中…",
        "ready": "更新包已就绪，等待确认安装。", "installing": "正在安装 MoviePilot…",
        "success": "MoviePilot 更新完成。", "partial": "MoviePilot 更新不完整，请检查前后端版本。",
        "failed": "MoviePilot 更新失败。",
    },
    "plugin_update": {
        "unconfigured": "尚未配置插件市场。", "checking": "正在检查插件更新…",
        "up_to_date": "插件均已是最新版本。", "available": "发现可更新插件。",
        "updating": "正在更新插件…", "success": "插件更新完成。",
        "partial": "只有部分插件更新完成。", "failed": "插件更新检查失败。",
    },
    "market_update": {
        "unconfigured": "尚未配置插件市场。", "checking": "正在检查插件库…",
        "up_to_date": "插件库已是最新。", "available": "发现插件库更新。",
        "syncing": "正在同步插件库…", "success": "插件库同步完成。", "failed": "插件库同步失败。",
    },
}

_PUBLIC_FIELDS = (
    "kind", "phase", "message", "detail", "error", "progress", "target_version",
    "backend_version", "frontend_version", "target_component", "items", "actions", "session", "actor_id", "steps",
    "updated_at", "expires_at",
)


def _now_seconds(now: Any = None) -> float:
    if now is None:
        return time.time()
    if isinstance(now, datetime):
        value = now if now.tzinfo else now.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc).timestamp()
    try:
        return float(now)
    except (TypeError, ValueError):
        return time.time()


def _timestamp(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return number if number > 0 else default


def _phase_message(kind: str, phase: str, message: Any = "") -> str:
    return str(message or "").strip() or _DEFAULT_MESSAGES.get(kind, {}).get(phase, "")


def _clean_actions(kind: str, phase: str, actions: Any = None) -> List[str]:
    allowed = set(_KIND_ACTIONS.get(kind, {}).get(phase, ()))
    values = actions if isinstance(actions, (list, tuple, set)) else []
    cleaned = []
    for item in values:
        action = str(item or "").strip()
        if action and action in allowed and action not in cleaned:
            cleaned.append(action)
    return cleaned or list(_KIND_ACTIONS.get(kind, {}).get(phase, ()))


def _progress(value: Any) -> Optional[int]:
    if value is None or value == "":
        return None
    try:
        number = int(float(value))
    except (TypeError, ValueError):
        return None
    return max(0, min(100, number))


def progress_bucket(value: Any) -> Optional[int]:
    number = _progress(value)
    return None if number is None else (number // PROGRESS_BUCKET_SIZE) * PROGRESS_BUCKET_SIZE


def normalize_update_job(kind: str, raw: Any = None, *, patch: Any = None, now: Any = None) -> Dict[str, Any]:
    kind = str(kind or "").strip()
    if kind not in UPDATE_KINDS:
        return {}
    base = deepcopy(raw) if isinstance(raw, dict) else {}
    if isinstance(patch, dict):
        base.update(patch)
    phase = str(base.get("phase") or "idle").strip()
    if phase not in UPDATE_PHASES:
        phase = "failed" if base.get("error") else "idle"
    stamp = _now_seconds(now)
    previous_phase = str((raw or {}).get("phase") or "") if isinstance(raw, dict) else ""
    updated_at = _timestamp(base.get("updated_at"), 0.0) or stamp
    if previous_phase and previous_phase != phase:
        updated_at = stamp
    phase_changed = bool(previous_phase and previous_phase != phase)
    expires_at = _timestamp(base.get("expires_at"), 0.0)
    if phase in TERMINAL_TTL_SECONDS:
        if phase_changed or not expires_at:
            expires_at = updated_at + TERMINAL_TTL_SECONDS[phase]
    elif phase in RUNNING_PHASES:
        expires_at = updated_at + RUNNING_TIMEOUT_SECONDS
    elif kind == "mp_update" and phase in {"available", "ready"}:
        # 可更新/待安装状态不按确认窗口自动失效；动作执行时仍会复核
        # 目标版本、会话和宿主当前状态。
        expires_at = 0.0
    elif phase_changed or not expires_at:
        expires_at = 0.0
    session = str(base.get("session") or "").strip()
    if kind == "mp_update" and phase in {"available", "ready"} and not session:
        session = secrets.token_hex(5)
    default_steps = (["download", "status", "check"] if phase == "available"
                     else ["install", "status", "check"] if phase == "ready"
                     else ["status", "check"] if kind == "mp_update" else [])
    steps = [str(item).strip() for item in base.get("steps") or [] if str(item).strip()] \
        if isinstance(base.get("steps"), list) else []
    result = {
        "kind": kind, "phase": phase, "message": _phase_message(kind, phase, base.get("message")),
        "detail": str(base.get("detail") or "").strip(), "error": str(base.get("error") or "").strip(),
        "progress": _progress(base.get("progress")), "target_version": str(base.get("target_version") or "").strip(),
        "target_component": str(base.get("target_component") or "").strip(),
        "backend_version": str(base.get("backend_version") or "").strip(),
        "frontend_version": str(base.get("frontend_version") or "").strip(),
        "items": deepcopy(base.get("items")) if isinstance(base.get("items"), list) else [],
        "actions": _clean_actions(kind, phase, base.get("actions")),
        "session": session,
        "actor_id": str(base.get("actor_id") or "").strip(),
        "steps": steps or default_steps,
        "updated_at": updated_at, "expires_at": expires_at,
    }
    return {key: result[key] for key in _PUBLIC_FIELDS}


def set_update_job(jobs: Any, kind: str, patch: Any, *, now: Any = None) -> Dict[str, Any]:
    result = deepcopy(jobs) if isinstance(jobs, dict) else {}
    current = result.get(kind) if isinstance(result.get(kind), dict) else {}
    normalized = normalize_update_job(kind, current, patch=patch, now=now)
    if normalized:
        result[kind] = normalized
    return result


def job_is_visible(job: Any, *, now: Any = None) -> bool:
    if not isinstance(job, dict):
        return False
    phase = str(job.get("phase") or "")
    if phase in {"idle", ""}:
        return False
    expires_at = _timestamp(job.get("expires_at"), 0.0)
    stamp = _now_seconds(now)
    if (expires_at and expires_at <= stamp and phase not in RUNNING_PHASES
            and phase not in STALE_VISIBLE_PHASES and phase != "unconfigured"):
        return False
    return True


def job_is_actionable(job: Any) -> bool:
    return isinstance(job, dict) and str(job.get("phase") or "") in ACTIONABLE_PHASES and bool(job.get("actions"))


def render_signature(job: Any) -> tuple:
    if not isinstance(job, dict):
        return ()
    return (str(job.get("phase") or ""), str(job.get("message") or ""), str(job.get("detail") or ""),
            str(job.get("error") or ""), progress_bucket(job.get("progress")),
            str(job.get("target_version") or ""), tuple(job.get("actions") or []))


def migrate_legacy_update_state(state: Any, *, now: Any = None) -> Dict[str, Dict[str, Any]]:
    if not isinstance(state, dict):
        return {}
    jobs = state.get("update_jobs") if isinstance(state.get("update_jobs"), dict) else {}
    normalized = {kind: normalize_update_job(kind, jobs.get(kind), now=now) for kind in UPDATE_KINDS if isinstance(jobs.get(kind), dict)}
    panel = state.get("moviepilot_update_panel")
    if isinstance(panel, dict) and "mp_update" not in normalized:
        phase = str(panel.get("phase") or "")
        if phase == "idle":
            phase = "up_to_date"
        normalized["mp_update"] = normalize_update_job("mp_update", {
            "phase": phase or "idle", "message": panel.get("message") or "", "error": panel.get("error") or "",
            "progress": panel.get("progress"), "target_version": panel.get("version") or "",
            "backend_version": panel.get("current_version") or "", "frontend_version": panel.get("frontend_version") or "",
            "session": panel.get("session") or "",
            "actor_id": panel.get("actor_id") or "", "steps": list(panel.get("steps") or []),
            "updated_at": panel.get("updated_at") or panel.get("checked_at") or now, "expires_at": panel.get("expires_at") or 0,
        }, now=now)
    candidates = state.get("fusion_update_actions") if isinstance(state.get("fusion_update_actions"), dict) else {}
    for kind in UPDATE_KINDS:
        if kind in normalized or not isinstance(candidates.get(kind), dict):
            continue
        entry = candidates[kind]
        payload = entry.get("payload") if isinstance(entry.get("payload"), dict) else {}
        if kind == "plugin_update":
            items = [item for item in payload.get("plugins") or [] if isinstance(item, dict)]
            normalized[kind] = normalize_update_job(kind, {"phase": "available" if items else "up_to_date", "items": items,
                "message": entry.get("text") or "", "updated_at": entry.get("updated_at") or now}, now=now)
        elif kind == "market_update":
            markets = [str(item).strip() for item in payload.get("markets") or [] if str(item).strip()]
            normalized[kind] = normalize_update_job(kind, {"phase": "available" if markets else "up_to_date",
                "message": entry.get("text") or "", "updated_at": entry.get("updated_at") or now}, now=now)
        else:
            checks = [item for item in payload.get("checks") or [] if isinstance(item, dict)]
            normalized[kind] = normalize_update_job(kind, {"phase": "available" if checks else "idle", "items": checks,
                "target_version": next((str(item.get("latest_version") or item.get("latest") or "")
                                        for item in checks if item.get("has_update")), ""),
                "message": entry.get("text") or "", "updated_at": entry.get("updated_at") or now}, now=now)
    return normalized


def normalize_update_center_state(state: Any, *, now: Any = None) -> Dict[str, Any]:
    result = deepcopy(state) if isinstance(state, dict) else {}
    jobs = migrate_legacy_update_state(result, now=now)
    result["update_jobs"] = expire_update_jobs(jobs, now=now)
    return result


def visible_jobs(jobs: Any, *, now: Any = None) -> List[Dict[str, Any]]:
    if not isinstance(jobs, dict):
        return []
    return [job for kind in UPDATE_KINDS for job in [jobs.get(kind)] if job_is_visible(job, now=now)]


def expire_update_jobs(jobs: Any, *, now: Any = None) -> Dict[str, Any]:
    """把超过运行时限仍没有新进展的任务转成失败，并重新给出恢复按钮。"""
    result = deepcopy(jobs) if isinstance(jobs, dict) else {}
    stamp = _now_seconds(now)
    for kind in UPDATE_KINDS:
        job = result.get(kind)
        if not isinstance(job, dict) or str(job.get("phase") or "") not in RUNNING_PHASES:
            continue
        updated_at = _timestamp(job.get("updated_at"), 0.0)
        expires_at = _timestamp(job.get("expires_at"), 0.0) or (updated_at + RUNNING_TIMEOUT_SECONDS)
        if not expires_at or expires_at > stamp:
            continue
        result[kind] = normalize_update_job(kind, job, patch={
            "phase": "failed",
            "message": "任务超时，请重试。",
            "error": "任务超过 30 分钟未更新，已转为失败。",
            "progress": None,
            "updated_at": stamp,
        }, now=stamp)
    return result


def update_job_actions(job: Any) -> List[str]:
    """返回当前阶段允许显示的动作，避免渲染层重新实现状态规则。"""
    if not isinstance(job, dict) or not job_is_actionable(job):
        return []
    return [str(item) for item in job.get("actions") or [] if str(item)]


visible_update_jobs = visible_jobs
