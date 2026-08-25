"""Site statistics helper functions extracted from __init__.py.

Pure functions that do not require plugin instance state.
Imported by Signal to keep __init__.py focused on orchestration.
"""
from typing import Any, List, Optional, Tuple


def _row_sort_key(row: Any) -> Tuple[str, str, int]:
    day = str(getattr(row, "updated_day", None) or "")[:10]
    clock = str(getattr(row, "updated_time", None) or "")
    try:
        row_id = int(getattr(row, "id", 0) or 0)
    except (TypeError, ValueError):
        row_id = 0
    return day, clock, row_id


def select_latest_site_userdata_rows(
    rows: List[Any], domains: Optional[set] = None, *, include_errors: bool = True
) -> List[Any]:
    """Select one newest typed row per domain.

    ``SiteOper.get_userdata_latest`` filters errors and several consumers used
    lexical string sorting for numeric IDs.  This helper keeps the V2 snapshot
    and report paths on the same identity/date/time ordering.
    """
    # ``None`` means no domain filter; an explicit empty set means there are
    # no active domains and must therefore return no historical rows.
    allowed = None if domains is None else {
        str(value).strip() for value in domains if str(value).strip()
    }
    newest = {}
    for row in rows or []:
        if not row:
            continue
        domain = str(getattr(row, "domain", None) or getattr(row, "name", None) or "").strip()
        if not domain or (allowed is not None and domain not in allowed):
            continue
        if not include_errors and str(getattr(row, "err_msg", None) or "").strip():
            continue
        previous = newest.get(domain)
        if previous is None or _row_sort_key(row) > _row_sort_key(previous):
            newest[domain] = row
    return list(newest.values())

def find_site_userdata_snapshot(rows: List[Any], name: str, domain: Optional[str] = None) -> Optional[Any]:
    # Pick the newest row before filtering errors.  A newer failed refresh must
    # invalidate the baseline instead of silently falling back to an older
    # successful counter value.
    latest_rows = select_latest_site_userdata_rows(rows, include_errors=True)
    valid_rows = [
        row for row in latest_rows
        if not str(getattr(row, "err_msg", None) or "").strip()
    ]
    domain = str(domain or "").strip()
    if domain:
        for row in valid_rows:
            if str(getattr(row, "domain", None) or "").strip() == domain:
                return row
        for row in valid_rows:
            if not str(getattr(row, "domain", None) or "").strip() and getattr(row, "name", None) == name:
                return row
        return None
    if name:
        for row in valid_rows:
            if getattr(row, "name", None) == name:
                return row
    return None

def site_userdata_number(row: Any, key: str) -> Optional[int]:
    value = getattr(row, key, None)
    if value in (None, ""):
        return None
    try:
        return int(float(value))
    except Exception:
        return None

def format_metric_number(value: Any) -> str:
    try:
        num = float(value)
        if num.is_integer():
            return f"{int(num):,}"
        return f"{num:,.1f}".rstrip("0").rstrip(".")
    except Exception:
        return str(value)

def format_duration(seconds: Any) -> str:
    try:
        seconds = int(seconds or 0)
        return f"{seconds // 3600}时{(seconds % 3600) // 60:02d}分"
    except Exception:
        return "0时00分"

def fusion_usage_bar(pct: float, width: int = 8) -> str:
    pct = max(0.0, min(100.0, float(pct or 0)))
    filled = int(round((pct / 100) * width))
    filled = max(0, min(width, filled))
    return "[" + ("█" * filled) + ("░" * (width - filled)) + "]"

def format_compact_bytes(size: Any) -> str:
    try:
        value = float(size or 0)
    except Exception:
        return str(size)
    units = ["B", "K", "M", "G", "T", "P"]
    unit = 0
    while abs(value) >= 1024 and unit < len(units) - 1:
        value /= 1024
        unit += 1
    if unit == 0:
        return f"{value:.0f}B"
    return f"{value:.2f}{units[unit]}"

def normalize_compact_unit(unit: str) -> str:
    raw = str(unit or "").upper().replace("B", "")
    return raw or "B"

def unique_keep_order(items: List[Any]) -> List[str]:
    seen = set(); result = []
    for item in items or []:
        text = str(item or "").strip()
        if text and text not in seen:
            seen.add(text); result.append(text)
    return result
