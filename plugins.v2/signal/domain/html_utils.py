"""HTML utility functions extracted from __init__.py.

Pure functions for HTML escaping, text matching, and report splitting.
"""
import html
import re
from typing import Any, Dict, List, Optional

def html_escape(value: Any) -> str:
    return html.escape(str(value or ""), quote=True)

def match_text(pattern: str, text: str) -> str:
    match = re.search(pattern, str(text or ""))
    return match.group(1).strip() if match else ""

def clip_telegram_html(value: str, limit: int = 32768) -> str:
    text = str(value or "")
    if len(text.encode("utf-8")) <= limit:
        return text
    encoded = text.encode("utf-8")[: max(0, limit - 64)]
    clipped = encoded.decode("utf-8", errors="ignore").rstrip()
    return f"{clipped}\n<p>…（已截断）</p>"

def split_daily_report_text(text: str) -> Dict[str, Any]:
    lines = [line.rstrip() for line in str(text or "").splitlines()]
    title = next((line.strip() for line in lines if line.strip()), "Signal 每日汇报")
    known_headers = {
        "🤖 MoviePilot", "📡 站点状态", "📈 站点增量", "📥 今日下载", "📦 入库整理",
        "📺 订阅追新", "💾 存储空间", "🎬 媒体统计", "🩺 健康巡查", "🧾 今日摘要", "⚠️ 今日提醒",
    }
    intro: List[str] = []
    sections: List[Dict[str, Any]] = []
    current: Optional[Dict[str, Any]] = None
    for raw in lines[1:]:
        line = raw.strip()
        if not line:
            continue
        if line in known_headers:
            current = {"title": line, "lines": []}
            sections.append(current)
            continue
        if current is None:
            intro.append(line)
        else:
            current.setdefault("lines", []).append(line)
    return {"title": title, "intro": intro, "sections": sections}
