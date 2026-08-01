"""Compose collector output into the transport-neutral V7 snapshot."""

import re
import ipaddress
from copy import deepcopy
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple
from urllib.parse import parse_qsl, quote, urlencode, urlsplit, urlunsplit

from .fusion_completion import normalize_completion_task, normalize_completion_tasks


PERSISTENT_KEYS = ("sites", "storage", "subscriptions")


def media_session_ip(info: Any) -> str:
    for name in ("ip", "remote_endpoint", "remote_ip", "client_ip", "ip_address", "address"):
        raw = str(getattr(info, name, None) or "").strip()
        if not raw:
            continue
        candidate = raw.split(",", 1)[0].strip()
        if candidate.startswith("[") and "]" in candidate:
            candidate = candidate[1:candidate.index("]")]
        elif candidate.count(":") == 1 and candidate.rsplit(":", 1)[1].isdigit():
            candidate = candidate.rsplit(":", 1)[0]
        try:
            return str(ipaddress.ip_address(candidate))
        except ValueError:
            continue
    return ""


def media_playback_url(info: Any) -> str:
    for name in ("playback_url", "item_url", "web_url", "url"):
        sanitized = _sanitize_media_url(getattr(info, name, None))
        if sanitized:
            return sanitized
    server_url = next((_sanitize_media_url(getattr(info, name, None)) for name in ("server_url", "server_address", "base_url", "host") if _sanitize_media_url(getattr(info, name, None))), "")
    item_id = next((str(getattr(info, name, None) or "").strip() for name in ("item_id", "itemid", "rating_key", "ratingKey", "key") if getattr(info, name, None) not in (None, "")), "")
    if not server_url or not item_id:
        return ""
    platform = " ".join(str(getattr(info, name, None) or "") for name in ("channel", "server_type", "provider")).lower()
    base = server_url.rstrip("/")
    if "plex" in platform:
        server_id = next((str(getattr(info, name, None) or "").strip() for name in ("server_id", "machine_identifier", "machineIdentifier") if getattr(info, name, None) not in (None, "")), "")
        path = f"/web/index.html#!/server/{quote(server_id, safe='')}/details" if server_id else "/web/index.html#!/details"
        return _sanitize_media_url(f"{base}{path}?key={quote(item_id, safe='')}")
    return _sanitize_media_url(f"{base}/web/index.html#!/details?id={quote(item_id, safe='')}")


def _sanitize_media_url(value: Any) -> str:
    raw = str(value or "").strip()
    if not raw:
        return ""
    try:
        parsed = urlsplit(raw)
        port = parsed.port
    except ValueError:
        return ""
    if parsed.scheme.lower() not in {"http", "https"} or not parsed.hostname:
        return ""
    host = parsed.hostname
    if ":" in host and not host.startswith("["):
        host = f"[{host}]"
    netloc = host + (f":{port}" if port else "")
    safe_keys = {"id", "key", "item", "itemid", "ratingkey", "server"}
    query = urlencode([(key, val) for key, val in parse_qsl(parsed.query, keep_blank_values=True) if key.lower() in safe_keys])
    fragment = parsed.fragment
    if "?" in fragment:
        fragment_path, fragment_query = fragment.split("?", 1)
        safe_fragment_query = urlencode([(key, val) for key, val in parse_qsl(fragment_query, keep_blank_values=True) if key.lower() in safe_keys])
        fragment = fragment_path + (f"?{safe_fragment_query}" if safe_fragment_query else "")
    return urlunsplit((parsed.scheme.lower(), netloc, parsed.path or "", query, fragment))


def compose_v7_snapshot(
    *,
    identity: Optional[Dict[str, Any]] = None,
    site_rows: Optional[Iterable[Any]] = None,
    site_count: str = "",
    storage_rows: Optional[Iterable[Any]] = None,
    subscription_rows: Optional[Iterable[Any]] = None,
    completion_rows: Optional[Iterable[Any]] = None,
    realtime: Optional[Iterable[Dict[str, Any]]] = None,
    anomalies: Optional[Iterable[Dict[str, Any]]] = None,
    enabled_persistent: Optional[Iterable[str]] = None,
) -> Tuple[Dict[str, Any], str]:
    enabled = set(PERSISTENT_KEYS if enabled_persistent is None else enabled_persistent)
    persistent: Dict[str, Any] = {}
    sites = _normalized_rows(site_rows)
    storage = _normalized_rows(storage_rows)
    subscriptions = _normalized_rows(subscription_rows)
    _persistent_module(persistent, "sites", sites, _site_count_label(site_count, sites), enabled)
    if sites and persistent.get("sites"):
        persistent["sites"]["context"] = _site_aggregate(sites)
    _persistent_module(persistent, "storage", storage, f"{len(storage)}个容器" if storage else "", enabled)
    _persistent_module(persistent, "subscriptions", subscriptions, f"{len(subscriptions)}个" if subscriptions else "", enabled)

    snapshot: Dict[str, Any] = {
        "identity": deepcopy(identity or {}),
        "persistent": persistent,
    }
    realtime_rows = [deepcopy(item) for item in realtime or [] if isinstance(item, dict)]
    anomaly_rows = [deepcopy(item) for item in anomalies or [] if isinstance(item, dict)]
    completion = normalize_completion_tasks(list(completion_rows or []))
    if realtime_rows:
        snapshot["realtime"] = realtime_rows
    if anomaly_rows:
        snapshot["anomalies"] = anomaly_rows
    if completion:
        snapshot["completion"] = {
            "kicker": "今日完成",
            "count": f"{len(completion)}个任务",
            "tasks": completion,
        }
    state = "alert" if anomaly_rows else ("active" if realtime_rows else "normal")
    return snapshot, state


def parse_site_rows(lines: Iterable[Any]) -> List[List[str]]:
    rows = []
    for raw in lines or []:
        text = _clean_line(raw)
        if not text or any(marker in text for marker in ("暂无", "无", "过期", "异常", "基线不足")):
            continue
        name, detail = _split_label(text)
        upload = _metric(detail, r"(?:↑|⬆)\s*([^｜|·]+)")
        download = _metric(detail, r"(?:↓|⬇)\s*([^｜|·]+)")
        if name and (upload or download):
            rows.append([name, " · ".join(item for item in (f"↑{upload}" if upload else "", f"↓{download}" if download else "") if item)])
    return rows


def parse_storage_rows(lines: Iterable[Any]) -> List[List[str]]:
    rows = []
    for raw in lines or []:
        text = _clean_line(raw)
        if not text or any(marker in text for marker in ("未检测到", "检查异常")):
            continue
        name, detail = _split_label(text)
        match = re.search(r"已用\s*(\d{1,3})%\s*[｜|]\s*([^/｜|]+)\s*/\s*(.+?)(?:\s*[🟢🟠🔴]|$)", detail)
        if not match:
            match = re.search(r"(\d{1,3})%\s*已用\s*[｜|]\s*([^/｜|]+)\s*/\s*(.+?)(?:\s*[🟢🟠🔴]|$)", detail)
        if not match or not name:
            continue
        pct = max(0, min(100, int(match.group(1))))
        rows.append([name, _progress(pct), f"{pct}%", match.group(3).strip()])
    return rows


def parse_subscription_rows(lines: Iterable[Any]) -> List[List[str]]:
    rows = []
    for raw in lines or []:
        text = _clean_line(raw)
        if not text or any(marker in text for marker in ("暂无", "无订阅")):
            continue
        pipe = re.split(r"\s*[｜|]\s*", text, maxsplit=1)
        if len(pipe) == 2:
            name, detail = pipe[0].strip(), pipe[1].strip()
        else:
            match = re.match(r"(.+)[：:]\s*(S\d{1,2}E\d{1,3}|发现新一集)$", text, re.I)
            if not match:
                match = re.match(r"(.+?)\s+(S\d{1,2}E\d{1,3}|发现新一集)$", text, re.I)
            name, detail = (match.group(1).strip(), match.group(2).strip()) if match else (text, "")
        rows.append([name or text, detail or "发现新一集"])
    return rows


def parse_completion_rows(lines: Iterable[Any]) -> List[Dict[str, str]]:
    rows = []
    for raw in lines or []:
        text = _clean_line(raw)
        if not text or "暂无记录" in text:
            continue
        label, detail = _split_label(text)
        task = normalize_completion_task([label, detail])
        if task:
            rows.append(task)
    return rows


def split_preview_details(rows: Sequence[Sequence[Any]], preview_limit: int = 2) -> Tuple[List[List[Any]], List[List[Any]]]:
    normalized = [list(row) for row in rows]
    return normalized[:preview_limit], normalized[preview_limit:]


def _persistent_module(target: Dict[str, Any], key: str, rows: List[List[str]], count: str, enabled: set) -> None:
    if key not in enabled:
        return
    visible = rows or [["等待首次采集", "已启用"]]
    preview, details = split_preview_details(visible)
    target[key] = {"count": count or "等待首次采集", "preview_rows": preview, "details_rows": details}


def _normalized_rows(rows: Optional[Iterable[Any]]) -> List[List[str]]:
    result = []
    for row in rows or []:
        if isinstance(row, (list, tuple)):
            values = [str(item or "").strip() for item in row]
        else:
            values = [str(row or "").strip()]
        if any(values):
            result.append(values)
    return result


def _clean_line(value: Any) -> str:
    return re.sub(r"^[\s⦁•·*\-✅⚠️]+", "", str(value or "").strip()).strip()


def _split_label(text: str) -> Tuple[str, str]:
    parts = re.split(r"[：:]", text, maxsplit=1)
    if len(parts) == 2:
        return parts[0].strip(), parts[1].strip()
    parts = re.split(r"\s*[｜|]\s*", text, maxsplit=1)
    return (parts[0].strip(), parts[1].strip()) if len(parts) == 2 else (text.strip(), "")


def _metric(text: str, pattern: str) -> str:
    match = re.search(pattern, text)
    return match.group(1).strip() if match else ""


def _site_aggregate(rows: Sequence[Sequence[Any]]) -> str:
    upload = _sum_data_metrics(_pair_metric(row, "↑") for row in rows)
    download = _sum_data_metrics(_pair_metric(row, "↓") for row in rows)
    return "  ".join(item for item in (f"↑{upload}" if upload else "", f"↓{download}" if download else "") if item)


def _pair_metric(row: Sequence[Any], marker: str) -> str:
    detail = str(row[-1] if row else "")
    match = re.search(rf"{re.escape(marker)}\s*([0-9]+(?:\.[0-9]+)?\s*[KMGTPE]?B)\b", detail, re.I)
    return match.group(1) if match else ""


def _sum_data_metrics(values: Iterable[str]) -> str:
    units = {unit: 1024 ** index for index, unit in enumerate(("B", "KB", "MB", "GB", "TB", "PB", "EB"))}
    total = 0.0
    largest = "B"
    found = False
    for value in values:
        match = re.fullmatch(r"\s*([0-9]+(?:\.[0-9]+)?)\s*([KMGTPE]?B)\s*", str(value or ""), re.I)
        if not match:
            continue
        unit = match.group(2).upper()
        total += float(match.group(1)) * units[unit]
        if units[unit] > units[largest]:
            largest = unit
        found = True
    if not found:
        return ""
    amount = total / units[largest]
    formatted = f"{amount:.1f}".rstrip("0").rstrip(".")
    return f"{formatted} {largest}"


def _progress(percent: int, width: int = 10) -> str:
    filled = max(0, min(width, round(percent / 100 * width)))
    return "▰" * filled + "▱" * (width - filled)


def _site_count_label(value: Any, rows: Sequence[Any]) -> str:
    compact = "".join(str(value or "").split())
    match = re.fullmatch(r"(\d+)/(\d+)在线", compact)
    if match:
        online, total = (int(item) for item in match.groups())
        return f"{min(online, total)}/{total}在线"
    return f"{len(rows)}/{len(rows)}在线" if rows else ""

