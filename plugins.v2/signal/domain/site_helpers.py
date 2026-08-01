"""Site statistics helper functions extracted from __init__.py.

Pure functions that do not require plugin instance state.
Imported by Signal to keep __init__.py focused on orchestration.
"""
from typing import Any, List, Optional, Tuple

def find_site_userdata_snapshot(rows: List[Any], name: str, domain: Optional[str] = None) -> Optional[Any]:
    valid_rows = [row for row in (rows or []) if row and not str(getattr(row, "err_msg", None) or "").strip()]
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
