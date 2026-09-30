"""Telegram explicit-block renderer for the V7 Fusion card."""

import re
from copy import deepcopy
from typing import Any, Dict, Iterable, List, Optional, Sequence

from .fusion_completion import normalize_completion_tasks
from .fusion_composition import _site_count_label, update_change_count

from .fusion_card_model import validate_v7_card_model


RICH_TEXT_LIMIT = 32768
RICH_BLOCK_LIMIT = 500
_BLOCK_TYPES = {"paragraph", "heading", "pre", "footer", "divider", "list", "blockquote", "table", "details", "buttons"}

VALID_TABS = ("overview", "content", "system")
_TAB_OWNERS = {
    "content": (
        "persistent-sites", "persistent-subscriptions", "persistent-transfer",
        "persistent-media",
    ),
    "system": (
        "persistent-health", "persistent-storage", "persistent-maintenance", "persistent-update",
    ),
}
_SECTION_META = {
    "current-anomalies": ("⚠️", "需要注意"),
    "persistent-sites": ("📡", "站点状态"),
    "persistent-subscriptions": ("📺", "订阅追新"),
    "persistent-transfer": ("📥", "下载入库"),
    "realtime-media": ("🎬", "媒体动态"),
    "persistent-media": ("🎬", "媒体动态"),
    "persistent-health": ("❤️", "健康巡查"),
    "persistent-storage": ("💾", "存储空间"),
    "persistent-maintenance": ("🔧", "维护任务"),
    "persistent-update": ("⬆️", "更新管理"),
}
_TAB_FOOTER = "Signal 插件 · 每小时自动刷新"


def render_v7_rich_message(model: Dict[str, Any], *, active_tab: Optional[str] = None,
                           buttons: Optional[Sequence[Dict[str, Any]]] = None,
                           action_buttons: Optional[Sequence[Dict[str, Any]]] = None,
                           status_blocks: Optional[Sequence[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """Render a validated V7 model to one explicit InputRichMessage payload.

    ``active_tab`` selects the tabbed card view (overview / content / system).
    ``buttons`` renders the tab row as an in-card ``buttons`` block (matching the
    approved template) instead of relying on Telegram's message keyboard.
    Without ``active_tab`` the legacy whole-card view is rendered.
    """
    card = validate_v7_card_model(model)
    if active_tab is not None:
        blocks = _tab_blocks_within_limits(card, str(active_tab), buttons, action_buttons, status_blocks)
        return {"blocks": blocks}
    blocks = _render_card_blocks(card)
    anomaly = next((item for item in card.get("modules") or [] if item.get("owner") == "current-anomalies"), None)
    if anomaly is None or _within_rich_limits(blocks):
        return {"blocks": blocks}

    # Keep the stored report intact. Only the final Telegram view has a budget,
    # shared with every other module, and any omission must be visible.
    rows = _rows(anomaly.get("details_rows"))
    notice = ["异常详情超出 Telegram 消息容量，部分内容已省略。", ""]

    def render_rows(kept: List[List[str]]) -> List[Dict[str, Any]]:
        anomaly["details_rows"] = kept + [notice]
        return _render_card_blocks(card)

    blocks = render_rows([])
    if not _within_rich_limits(blocks):
        raise ValueError("融合卡其他内容已超出 Telegram 消息容量，无法容纳异常摘要")
    low, high = 0, len(rows)
    while low < high:
        middle = (low + high + 1) // 2
        candidate = render_rows(rows[:middle])
        if _within_rich_limits(candidate):
            low, blocks = middle, candidate
        else:
            high = middle - 1
    kept = rows[:low]
    if low < len(rows):
        left, right = _pair(rows[low])
        low, high = 0, len(left)
        while low < high:
            middle = (low + high + 1) // 2
            candidate = render_rows(kept + [[left[:middle] + "…", right]])
            if _within_rich_limits(candidate):
                low, blocks = middle, candidate
            else:
                high = middle - 1
    return {"blocks": blocks}


def action_status_blocks(items: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """无边框、无条纹的居中提示；表格仅提供段落没有的对齐能力。"""
    blocks: List[Dict[str, Any]] = []
    icons = {"running": "⏳", "success": "✅", "error": "⚠️"}
    for item in items or []:
        if not isinstance(item, dict):
            continue
        label = str(item.get("label") or "更新操作").strip()
        message = str(item.get("message") or "").strip()
        lines = [line.strip() for line in (message or label).splitlines() if line.strip()]
        headline = lines[0] if lines else label
        icon = icons.get(str(item.get("status") or ""), "ℹ️")
        inline: List[Any] = [{"type": "bold", "text": f"{icon} {headline}"}]
        timestamp = str(item.get("time") or "").strip()
        if timestamp:
            inline.append(_a_text(f"{_separator()}{timestamp}"))
        blocks.append(_table([_cell(inline, "center")]))
        if len(lines) > 1:
            blocks.append(_table([_cell(_a_text("\n".join(lines[1:])), "center")]))
    return blocks


def _within_rich_limits(value: Any) -> bool:
    characters, blocks = _rich_usage(value)
    return characters <= RICH_TEXT_LIMIT and blocks <= RICH_BLOCK_LIMIT


def _rich_usage(value: Any) -> tuple[int, int]:
    """Count the rendered RichText plus blocks, table rows and list items."""
    if isinstance(value, str):
        return len(value), 0
    if isinstance(value, list):
        usage = [_rich_usage(item) for item in value]
        return sum(item[0] for item in usage), sum(item[1] for item in usage)
    if not isinstance(value, dict):
        return 0, 0
    characters, blocks = _rich_usage([value[key] for key in ("text", "summary", "blocks", "cells", "items", "buttons") if key in value])
    blocks += int(value.get("type") in _BLOCK_TYPES)
    blocks += len(value.get("cells") or []) + len(value.get("items") or [])
    return characters, blocks


def _render_card_blocks(card: Dict[str, Any]) -> List[Dict[str, Any]]:
    identity = card["identity"]
    blocks: List[Dict[str, Any]] = _identity_blocks(identity, card["state"])
    modules = list(card.get("modules") or [])
    if card["state"] == "loading":
        loading = next((item for item in modules if item.get("kind") == "loading"), None)
        if loading:
            blocks.append(_loading_block(loading))
        blocks.append(_identity_footer())
        return blocks

    for index, module in enumerate(modules):
        previous = modules[index - 1] if index else None
        if index and not (_is_persistent_drawer(previous) and _is_persistent_drawer(module)):
            blocks.append({"type": "divider"})
        blocks.extend(_module_blocks(module, card["state"]))
    blocks.append(_identity_footer())
    return blocks


def _identity_blocks(identity: Dict[str, Any], state: str) -> List[Dict[str, Any]]:
    refreshed = str(identity.get("refreshed_at") or "").strip()
    stamp = refreshed[5:16] if len(refreshed) >= 16 else refreshed
    return [_table([
        _cell([{"type": "bold", "text": "🛰 融合通知"}, "\n", _a_text(f"更新 {stamp}")], "center"),
    ]), {"type": "divider"}]


def _identity_footer() -> Dict[str, Any]:
    return _table([_cell(_a_text("RichMessage · Details"), "center")])


def _module_blocks(module: Dict[str, Any], state: str) -> List[Dict[str, Any]]:
    owner = module.get("owner")
    if owner == "current-anomalies":
        return [_anomaly_block(module)]
    if owner == "realtime-media":
        return [_media_block(module, state)]
    if owner == "realtime-task-backup":
        return [_backup_block(module)]
    if owner in {"persistent-sites", "persistent-storage", "persistent-subscriptions"}:
        return _persistent_blocks(module, state)
    if owner == "today-completion":
        return _completion_blocks(module, state)
    return []


def _is_persistent_drawer(module: Any) -> bool:
    return isinstance(module, dict) and module.get("owner") in {
        "persistent-sites", "persistent-subscriptions", "persistent-storage", "today-completion",
    }


def _anomaly_block(module: Dict[str, Any]) -> Dict[str, Any]:
    body: List[Dict[str, Any]] = [
        _module_title_table(module, "当前异常", include_meta=True),
        {"type": "heading", "text": module.get("primary") or "需要关注", "size": 4},
        {"type": "paragraph", "text": module.get("context") or "需要关注"},
    ]
    details = _details_block(module.get("kicker") or "当前异常", _row_blocks(module.get("details_rows"), secondary_a=True), False)
    if details:
        body.append(details)
    return {"type": "blockquote", "blocks": body}


def _media_block(module: Dict[str, Any], state: str) -> Dict[str, Any]:
    status, percent = _media_status(module.get("status"))
    status_text = status or str(module.get("status") or "").strip()
    progress = str(module.get("progress") or "").strip()
    progress_text: Any = {"type": "code", "text": progress}
    if percent:
        progress_text = _join_inline([progress_text, _a_text(f" {percent}")])
    session_ip = str(module.get("session_ip") or "").strip()
    playback_url = str(module.get("playback_url") or "").strip()
    body: List[Dict[str, Any]] = [
        _module_title_table(module, "媒体播放", fallback_count="1 个会话"),
        {"type": "heading", "text": module.get("primary") or "媒体活动", "size": 4},
        _multirow_table([
            [_cell(module.get("context") or "", "left"), _cell(_a_text(status_text), "right")],
            [_cell(progress_text, "left"), _cell(_a_text(module.get("meta") or ""), "right")],
        ]),
    ]
    metadata_cells = []
    if session_ip:
        metadata_cells.append(_cell({"type": "subscript", "text": f"IP {session_ip}"}, "left"))
    if playback_url:
        metadata_cells.append(_cell({"type": "url", "text": "播放地址", "url": playback_url}, "right"))
    if metadata_cells:
        body.append(_table(metadata_cells))
    return {"type": "blockquote", "blocks": body}


def _backup_block(module: Dict[str, Any]) -> Dict[str, Any]:
    status_meta = " · ".join(item for item in (
        str(module.get("status") or "").strip(),
        str(module.get("meta") or "").strip(),
    ) if item)
    item_blocks: List[Dict[str, Any]] = [
        _module_title_table(module, "配置备份"),
        {"type": "heading", "text": module.get("primary") or "配置备份", "size": 4},
        _table([_cell(module.get("context") or "", "left"), _cell(_a_text(status_meta), "right")]),
    ]
    details = _details_block(module.get("kicker") or "配置备份", _backup_detail_blocks(module.get("details_rows")), False)
    if details:
        item_blocks.append(details)
    return {"type": "list", "items": [{"blocks": item_blocks, "has_checkbox": True, "is_checked": False}]}


def _backup_detail_blocks(rows: Any) -> List[Dict[str, Any]]:
    result = []
    for row in _rows(rows):
        left, right = _pair(row)
        right_value: Any = {"type": "code", "text": right} if right.startswith("▰") else _a_text(right)
        result.append({"type": "paragraph", "text": [left + _separator(), right_value]})
    return result


def _persistent_blocks(module: Dict[str, Any], state: str) -> List[Dict[str, Any]]:
    owner = module.get("owner")
    rows = _rows(module.get("preview_rows")) + _rows(module.get("details_rows"))
    summary = _summary(module)
    if owner == "persistent-storage":
        blocks: List[Dict[str, Any]] = []
        for row in rows:
            blocks.extend(_storage_row_blocks(row))
        return [_details_block(summary, blocks, False)] if blocks else []
    if owner == "persistent-subscriptions":
        items = []
        for row in rows:
            left, right = _pair(row)
            items.append({
                "blocks": [_table([
                    _cell(left.lstrip("·• "), "left"),
                    _cell({"type": "subscript", "text": right}, "right"),
                ])],
                "has_checkbox": False,
                "is_checked": False,
            })
        native_list = {"type": "list", "items": items}
        return [_details_block(summary, [native_list], True)] if items else []
    blocks: List[Dict[str, Any]] = []
    if owner == "persistent-sites":
        site_rows: List[List[Dict[str, Any]]] = []
        aggregate = str(module.get("context") or "").strip()
        metric_rows = module.get("metric_rows") or []
        if aggregate:
            site_rows.append([
                _cell({"type": "bold", "text": "今日流量"}, "left"),
                _cell({"type": "bold", "text": aggregate}, "right"),
            ])
        for item in metric_rows:
            values = [str(value) for value in list(item)]
            values += [""] * (3 - len(values))
            name, upload, download = values[:3]
            site_rows.append([
                _cell(name, "left"),
                _cell(_a_text(f"⬆ {upload} · ⬇ {download}"), "right"),
            ])
        if not metric_rows:
            for row in rows:
                left, right = _pair(row)
                site_rows.append([
                    _cell(left, "left"),
                    _cell({"type": "subscript", "text": right}, "right"),
                ])
        if site_rows:
            blocks.append(_multirow_table(site_rows, bordered=False, striped=True))
        notices = _details_block("未计入今日流量", _row_blocks(module.get("notice_rows"), secondary_a=True), False)
        if notices:
            blocks.append(notices)
    return [_details_block(summary, blocks, True)] if blocks else []


def _completion_blocks(module: Dict[str, Any], state: str) -> List[Dict[str, Any]]:
    tasks = normalize_completion_tasks(module.get("tasks"))
    groups: Dict[str, List[Dict[str, Any]]] = {}
    for task in tasks:
        groups.setdefault(str(task.get("task_group") or "").strip(), []).append(task)
    body: List[Dict[str, Any]] = []
    for group, grouped_tasks in groups.items():
        if group:
            body.append({"type": "heading", "text": group, "size": 5})
        cells = []
        for task in grouped_tasks:
            result = _completion_result_text(task["outcome"], task["result_status"])
            count = int(task.get("execution_count") or 1)
            title = task["title"] if count <= 1 else f"{task['title']}（{count}次）"
            cells.append([_cell(title, "center"), _cell(result, "right")])
        if cells:
            body.append(_multirow_table(cells))
    return [_details_block(_summary(module), body, False)] if body else []


def _completion_result_text(value: Any, result_status: str = "success") -> Any:
    text = str(value or "").strip()
    if not text:
        return ""
    if result_status == "error":
        return {"type": "code", "text": text}
    if any(marker in text for marker in ("有更新", "可更新")):
        remainder = text.replace("有更新", "", 1).replace("可更新", "", 1).strip(" ·，,")
        return _join_inline([{"type": "hashtag", "text": "#有更新"}, " ", _a_text(remainder) if remainder else ""])
    return {"type": "marked", "text": text}


def _plain_task_item(row: Sequence[Any], checked: bool) -> Dict[str, Any]:
    label, meta = _pair(row)
    text = " · ".join(item for item in (label, meta) if item)
    return {"blocks": [{"type": "paragraph", "text": text}], "has_checkbox": True, "is_checked": checked}


def _loading_block(module: Dict[str, Any]) -> Dict[str, Any]:
    items = []
    for row in _rows(module.get("tasks")):
        label, status = _pair(row)
        items.append({
            "blocks": [{"type": "paragraph", "text": [label + _separator(), _a_text(status)]}],
            "has_checkbox": True,
            "is_checked": status in {"完成", "已完成"},
        })
    return {"type": "list", "items": items}


def _preview_row(owner: Any, row: Sequence[Any], strong: bool = False, *, left_strong: Any = None, right_strong: Any = None) -> Dict[str, Any]:
    values = list(row)
    if left_strong is None:
        left_strong = strong
    if right_strong is None:
        right_strong = strong
    if owner == "persistent-storage" and len(values) >= 4:
        name = _bold_or_text(values[0]) if left_strong else f"{values[0]}{_separator()}"
        left = _join_inline([name, _separator() if left_strong else "", {"type": "code", "text": str(values[1])}, f" {values[2]}"])
        right = [_bold_or_text(values[3])] if right_strong else str(values[3])
    else:
        left_value, right_value = _pair(values)
        left = [_bold_or_text(left_value)] if left_strong else left_value
        right = [_bold_or_text(right_value)] if right_strong else right_value
    return _table([_cell(left, "left", "middle"), _cell(right, "right", "middle")])


def _storage_row_blocks(row: Sequence[Any], *, left_strong: bool = False, right_strong: bool = False) -> List[Dict[str, Any]]:
    values = list(row)
    if len(values) < 4:
        return [_preview_row("persistent-storage", values, left_strong=left_strong, right_strong=right_strong)]
    name: Any = [_bold_or_text(values[0])] if left_strong else {"type": "bold", "text": str(values[0])}
    right: Any = [_bold_or_text(values[3])] if right_strong else {"type": "subscript", "text": str(values[3])}
    left = _join_inline([name, "\n", {"type": "code", "text": str(values[1])}, {"type": "subscript", "text": f" {values[2]}"}])
    return [
        _table([_cell(left, "left", "top", colspan=3), _cell(right, "right", "top")]),
    ]


def _row_blocks(rows: Any, owner: str = "", *, secondary_a: bool = False) -> List[Dict[str, Any]]:
    result = []
    for row in _rows(rows):
        if owner == "persistent-storage" and len(row) >= 4:
            result.extend(_storage_row_blocks(row))
        else:
            left, right = _pair(row)
            right_value: Any = _a_text(right) if secondary_a else right
            result.append(_table([_cell(left, "left", "middle"), _cell(right_value, "right", "middle")]))
    return result


def _task_item(row: Sequence[Any], checked: bool, compact: bool) -> Dict[str, Any]:
    label, meta = _pair(row)
    if not compact:
        short_meta = str(meta).split(" · ", 1)[0].strip()
        plain = " · ".join(item for item in (label, short_meta) if item)
        return {"blocks": [{"type": "paragraph", "text": plain}], "has_checkbox": True, "is_checked": checked}
    label_parts = str(label).split(" · ", 1)
    tail = []
    if len(label_parts) > 1:
        tail.append(label_parts[1])
    if meta:
        tail.append(meta)
    text: List[Any] = [_bold_or_text(label_parts[0])]
    if tail:
        text.append(_separator() + _separator().join(tail))
    return {"blocks": [{"type": "paragraph", "text": text}], "has_checkbox": True, "is_checked": checked}


def _aggregate_cells(value: Any) -> List[Dict[str, Any]]:
    parts = [item.strip() for item in str(value or "").split(" · ") if item.strip()]
    if len(parts) < 2:
        return []
    if len(parts) == 2:
        parts.append("")
    return [_cell(parts[0], "left"), _cell(parts[1], "center"), _cell(parts[2], "right")]


def _details_block(summary: Any, blocks: Iterable[Dict[str, Any]], is_open: bool) -> Dict[str, Any]:
    nested = [deepcopy(item) for item in blocks if item]
    if not nested:
        return {}
    result: Dict[str, Any] = {"type": "details", "summary": summary, "blocks": nested, "is_open": bool(is_open)}
    return result


def _table(cells: List[Dict[str, Any]]) -> Dict[str, Any]:
    return _multirow_table([cells])


def _module_title_table(
    module: Dict[str, Any],
    fallback_title: str,
    *,
    fallback_count: str = "",
    include_meta: bool = False,
) -> Dict[str, Any]:
    title = str(module.get("kicker") or fallback_title).strip()
    count = _compact_summary_count(module.get("count") or fallback_count)
    metadata = str(module.get("meta") or "").strip() if include_meta else ""
    subtitle = "  ".join(value for value in (count, metadata) if value)
    cells = [
        _cell(_c_title(title), "left"),
    ]
    if subtitle:
        cells.append(_cell(_a_text(subtitle), "right"))
    return _table(cells)


def _multirow_table(rows: List[List[Dict[str, Any]]], bordered: bool = False, striped: bool = False,
                    compact: bool = True) -> Dict[str, Any]:
    """显式声明表格样式；compact 控制留白，striped 控制正文行交替。"""
    return {"type": "table", "cells": rows, "is_compact": compact,
            "is_bordered": bordered, "is_striped": striped}


def _cell(text: Any, align: str, valign: str = "middle", colspan: int = 1) -> Dict[str, Any]:
    # 统一 RichText 结构；数组包装本身不控制底色或行高。
    if isinstance(text, dict):
        text = [text]
    result = {"text": text, "align": align, "valign": valign}
    if colspan > 1:
        result["colspan"] = colspan
    return result


def _kicker(module: Dict[str, Any]) -> List[Any]:
    result: List[Any] = []
    kicker = str(module.get("kicker") or "").strip()
    count = str(module.get("count") or "").strip()
    meta = str(module.get("meta") or "").strip()
    if kicker:
        result.append({"type": "marked", "text": kicker})
    if count:
        suffix = _separator() + count
        if meta and module.get("owner") == "current-anomalies":
            suffix += _separator() + meta
        result.append(suffix)
    if meta and not count and module.get("owner") == "current-anomalies":
        result.append(_separator() + meta)
    return result or [""]


def _row_as_footer(row: Sequence[Any]) -> str:
    left, right = _pair(row)
    return _separator().join(item for item in (left, right) if item)


def _pair(row: Sequence[Any]) -> List[str]:
    values = [str(item or "") for item in list(row)]
    if not values:
        return ["", ""]
    if len(values) == 1:
        return [values[0], ""]
    return [values[0], values[-1]]


def _rows(value: Any) -> List[List[str]]:
    if not isinstance(value, list):
        return []
    return [list(item) if isinstance(item, (list, tuple)) else [str(item)] for item in value]


def _marked_or_text(value: Any) -> Any:
    text = str(value or "")
    return {"type": "marked", "text": text} if text else ""


def _media_status(value: Any) -> List[str]:
    parts = [item.strip() for item in str(value or "").split(" · ") if item.strip()]
    if len(parts) >= 2:
        return [parts[0], parts[-1]]
    return [str(value or ""), ""]


def _bold_or_text(value: Any, fallback: Any = "", enabled: bool = True) -> Any:
    text = str(value or fallback or "")
    return {"type": "bold", "text": text} if enabled and text else text


def _join_inline(values: Iterable[Any]) -> List[Any]:
    return [value for value in values if value not in (None, "")]


def _c_title(value: Any) -> Dict[str, Any]:
    return {"type": "marked", "text": {"type": "bold", "text": str(value or "")}}


def _a_text(value: Any) -> Dict[str, Any]:
    return {"type": "subscript", "text": str(value or "")}


def _separator() -> str:
    return "  ·  "


def _suffix(value: Any) -> str:
    text = str(value or "").strip()
    return f"  {text}" if text else ""


def _summary(module: Dict[str, Any]) -> List[Any]:
    owner = str(module.get("owner") or "").strip()
    kicker = str(module.get("kicker") or "").strip()
    count = _dynamic_summary_count(module)
    result: List[Any] = []
    if owner in {"persistent-sites", "persistent-subscriptions", "persistent-storage", "today-completion"}:
        result.extend([{"type": "code", "text": "▏"}, " "])
    if kicker:
        result.append({"type": "marked", "text": kicker})
    if count:
        result.extend(["  ", _a_text(count)])
    return result or [""]


def _dynamic_summary_count(module: Dict[str, Any]) -> str:
    owner = str(module.get("owner") or "").strip()
    if owner == "persistent-sites":
        count = str(module.get("count") or "").strip()
        # Detail filtering must never change the collector's population counts.
        return count if count == "等待首次采集" else _site_count_label(count, ())
    authored = _compact_summary_count(module.get("count"))
    if authored == "等待首次采集":
        return authored
    if owner == "persistent-storage":
        rows = _rows(module.get("preview_rows")) + _rows(module.get("details_rows"))
        return f"{len(rows)}个容器" if rows else ""
    if owner == "persistent-subscriptions":
        rows = _rows(module.get("preview_rows")) + _rows(module.get("details_rows"))
        return f"{len(rows)}个" if rows else ""
    if owner == "today-completion":
        tasks = normalize_completion_tasks(module.get("tasks"))
        return f"{len(tasks)}个任务" if tasks else ""
    return authored


def _compact_summary_count(value: Any) -> str:
    parts = []
    for item in str(value or "").split(" · "):
        compact = "".join(item.split())
        if compact and not compact.startswith("最近"):
            parts.append(compact)
    return "  ".join(parts)

def _tab_blocks_within_limits(card: Dict[str, Any], active_tab: str,
                              buttons: Optional[Sequence[Dict[str, Any]]] = None,
                              action_buttons: Optional[Sequence[Dict[str, Any]]] = None,
                              status_blocks: Optional[Sequence[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
    """按完整栏目分组裁剪，保护卡头/按钮并明确告知省略。"""
    tab = active_tab if active_tab in VALID_TABS else "overview"
    modules = {str(item.get("owner") or ""): item for item in card.get("modules") or []}
    prefix = list(_identity_blocks(card["identity"], card["state"]))
    groups: List[List[Dict[str, Any]]] = []
    if card["state"] == "loading":
        loading = next((item for item in modules.values() if item.get("kind") == "loading"), {})
        groups.append([{"type": "paragraph", "text": "⏳ 正在采集，尚未完成检查"}, _loading_block(loading)])
    elif tab == "overview":
        groups.append(_overview_blocks(card, modules))
    else:
        for owner in _TAB_OWNERS.get(tab, ()):
            module = modules.get(owner)
            if owner == "persistent-media" and modules.get("realtime-media"):
                module = dict(module or {"owner": owner})
                module["realtime"] = modules["realtime-media"]
                module["tab_count"] = str(modules["realtime-media"].get("count") or "1 个会话")
            if module:
                groups.append(_tab_section_blocks(module))
        # 总览中的异常也须在当前页可见，不能因页签切换而丢失失败说明。
        anomaly = modules.get("current-anomalies")
        if anomaly:
            groups.append([{"type": "paragraph", "text": [
                {"type": "bold", "text": "⚠️ 需要注意"},
                _a_text("；".join(_row_as_footer(row) for row in _rows(anomaly.get("details_rows")))),
            ]}])
    for block in status_blocks or []:
        if isinstance(block, dict):
            groups.append([dict(block)])
    tail = [{"type": "divider"}, _tab_footer_block()]
    tail_buttons: List[Dict[str, Any]] = []
    if buttons:
        tail_buttons.append({"type": "buttons", "align": "center",
                             "buttons": [dict(item) for item in buttons]})
    if action_buttons:
        tail_buttons.append({"type": "buttons", "align": "center",
                             "buttons": [dict(item) for item in action_buttons]})
    tail.extend(tail_buttons)
    def assemble(omitted: bool = False) -> List[Dict[str, Any]]:
        notice = [{"type": "paragraph", "text": "部分栏目或状态详情超出 Telegram 消息容量，已省略。"}] if omitted else []
        return prefix + [block for group in groups for block in group] + notice + tail

    blocks = assemble()
    while not _within_rich_limits(blocks) and groups:
        groups.pop()
        blocks = assemble(omitted=True)
    if not _within_rich_limits(blocks):
        raise ValueError("融合卡页签内容已超出 Telegram 消息容量")
    return blocks


def _tab_footer_block() -> Dict[str, Any]:
    return _table([_cell(_a_text(_TAB_FOOTER), "center")])


def _overview_blocks(card: Dict[str, Any], modules: Dict[str, Any]) -> List[Dict[str, Any]]:
    """总览页：需要注意块 + 八宫格 + 数据时间行，结构与定稿模板一致。"""
    blocks: List[Dict[str, Any]] = []
    rows, hint, counts = _overview_attention(modules)
    if rows:
        inner: List[Dict[str, Any]] = [
            _table([_cell({"type": "bold", "text": "需要注意"}, "left"),
                    _cell(_a_text(_attention_count_text(counts)), "right")]),
            {"type": "heading", "text": "⚠️ 需要注意", "size": 3},
            _multirow_table([[_cell(left, "left"), _cell(_a_text(right), "right")] for left, right in rows]),
        ]
        if hint:
            inner.append({"type": "paragraph", "text": _a_text(hint)})
        blocks.append({"type": "blockquote", "blocks": inner})
    else:
        # 没有需要注意项时这个区块直接不出现：没异常不需要专门声明，
        # 更不该占着「异常」的位置。只有「还没跑过巡查」保留一行，因为那是待办。
        health = modules.get("persistent-health") or {}
        checked = bool(health) and not health.get("is_empty", True)
        if not checked:
            blocks.append({"type": "heading", "text": "ℹ️ 尚无巡查结果", "size": 3})
    overview = modules.get("card-overview")
    if overview:
        grid = _overview_grid(overview)
        if grid:
            blocks.append(grid)
    refreshed = str((card.get("identity") or {}).get("refreshed_at") or "").strip()
    if refreshed:
        blocks.append(_table([_cell(_a_text(f"数据时间：更新 {refreshed}"), "center")]))
    return blocks


def _attention_count_text(counts: Any) -> str:
    """异常与更新分开计数：有可用更新不是故障，混在一起会让人误判。"""
    values = counts if isinstance(counts, dict) else {}
    anomaly = int(values.get("anomaly") or 0)
    update = int(values.get("update") or 0)
    parts = []
    if anomaly:
        parts.append(f"{anomaly} 个异常")
    if update:
        parts.append(f"{update} 条更新")
    return " · ".join(parts) or "无"


def _overview_attention(modules: Dict[str, Any]) -> tuple:
    """需要注意清单：按「异常」与「更新」分类，附处理提示。"""
    rows: List[tuple] = []
    counts = {"anomaly": 0, "update": 0}

    def add(left: str, right: str, category: str) -> None:
        entry = (left, right)
        if entry in rows:
            return
        rows.append(entry)
        counts[category] += 1

    anomaly = modules.get("current-anomalies")
    if anomaly:
        for left, right in (_pair(row) for row in _rows(anomaly.get("details_rows"))):
            if left or right:
                add(left, right, "anomaly")
    overview = modules.get("card-overview") or {}
    detailed = _rows(overview.get("attention_rows"))
    for left, right in (_pair(row) for row in detailed):
        if left or right:
            add(left, right, "update")
    updates = modules.get("persistent-update") or {}
    update_rows = _rows(updates.get("preview_rows")) + _rows(updates.get("details_rows"))
    for left, right in (_pair(row) for row in update_rows):
        # 逐项更新与检查失败独立合并，普通无更新/同步成功结果不算告警。
        parts = [part.strip() for part in right.split(" · ")]
        errors = [part for part in parts if any(word in part for word in ("异常", "失败"))]
        if errors:
            add(left, " · ".join(errors), "anomaly")
        changed = update_change_count(right) > 0
        if not detailed and changed and not errors:
            add(left, right, "update")
        elif not detailed and changed and errors:
            changes = [part for part in parts if part not in errors and ("→" in part or "有更新" in part)]
            if changes:
                add(left, " · ".join(changes), "update")
    hint = "可通过卡片下方更新按钮查看并确认操作" if counts["update"] else ""
    return rows, hint, counts


def _overview_grid(module: Dict[str, Any]) -> Dict[str, Any]:
    rows = _rows(module.get("preview_rows")) + _rows(module.get("details_rows"))
    pairs = [_pair(row) for row in rows]
    pairs = [(left, right) for left, right in pairs if left or right]
    if not pairs:
        return {}
    grid: List[List[Dict[str, Any]]] = []
    for index in range(0, len(pairs), 2):
        line: List[Dict[str, Any]] = []
        for offset in (0, 1):
            if index + offset < len(pairs):
                label, value = pairs[index + offset]
                line.append(_cell([{"type": "bold", "text": label}, "\n", _a_text(value)], "left"))
            else:
                line.append(_cell("", "left"))
        grid.append(line)
    # 与定稿模板一致：总览八宫格带边框、不紧凑、不加斑马纹
    return {"type": "table", "cells": grid, "is_compact": False, "is_bordered": True, "is_striped": False}


def _tab_section_blocks(module: Dict[str, Any]) -> List[Dict[str, Any]]:
    owner = str(module.get("owner") or "")
    icon, label = _SECTION_META.get(owner, ("", str(module.get("kicker") or "")))
    title = f"{icon} {label}".strip()
    count = str(module.get("count") or "").strip()
    count = str(module.get("tab_count") or "").strip() or count
    # 标题是独立对齐行；每个正文表自行交替，标题不占正文行号。
    header = [_cell({"type": "bold", "text": title}, "left"),
              _cell({"type": "bold", "text": count}, "right") if count else _cell("", "right")]
    rows_table = _tab_rows_table(module, owner)
    blocks: List[Dict[str, Any]] = [_table(header)]
    if rows_table:
        blocks.append(rows_table)
    for left, right in (_pair(row) for row in _rows(module.get("notice_rows"))):
        if not left and not right:
            continue
        inline: List[Any] = [{"type": "bold", "text": left}] if left else []
        if right:
            inline.append(_a_text(f"{_separator()}{right}" if inline else right))
        blocks.append({"type": "paragraph", "text": inline})
    return blocks


def _tab_rows_table(module: Dict[str, Any], owner: str) -> Dict[str, Any]:
    if owner == "persistent-sites":
        cells = _site_section_cells(module)
        if cells:
            return _multirow_table(cells, bordered=False, striped=True)
    realtime = module.get("realtime") if owner == "persistent-media" else None
    cells: List[List[Dict[str, Any]]] = _media_session_cells(realtime) if realtime else []
    rows = _rows(module.get("preview_rows")) + _rows(module.get("details_rows"))
    if realtime and module.get("is_empty"):
        rows = []
    for row in rows:
        left, right = _pair(row)
        if not left and not right:
            continue
        cells.append([_cell(left, "left"), _cell(_a_text(right), "right")])
    return _multirow_table(cells, bordered=False, striped=True) if cells else {}


def _media_session_cells(module: Dict[str, Any]) -> List[List[Dict[str, Any]]]:
    """把实时播放的完整信息并入唯一媒体正文表。"""
    rows = [[module.get("primary") or "媒体活动", module.get("status") or ""],
            [module.get("context") or "", module.get("meta") or ""],
            [module.get("progress") or "", ""]]
    if module.get("session_ip"):
        rows.append(["IP", module["session_ip"]])
    cells = [[_cell(left, "left"), _cell(_a_text(right), "right")] for left, right in rows if left or right]
    if module.get("playback_url"):
        cells.append([_cell("播放地址", "left"), _cell({"type": "url", "text": "打开", "url": module["playback_url"]}, "right")])
    return cells


def _site_section_cells(module: Dict[str, Any]) -> List[List[Dict[str, Any]]]:
    """一行一站：站名、上传、下载各占一列，指标跨站点纵向对齐。"""
    if module.get("no_traffic_change"):
        label = "可统计站点暂无流量变化" if module.get("notice_rows") else "今日暂无流量变化"
        return [[_cell(label, "left"), _cell("", "right"), _cell("", "right")]]
    metric_rows = module.get("metric_rows") or []
    site_rows: List[List[Dict[str, Any]]] = []
    for item in metric_rows:
        values = [str(value) for value in list(item)]
        values += [""] * (3 - len(values))
        name, upload, download = values[:3]
        site_rows.append([
            _cell(name, "left"),
            _cell(_a_text(f"⬆ {upload}"), "right"),
            _cell(_a_text(f"⬇ {download}"), "right"),
        ])
    if not metric_rows:
        for row in _rows(module.get("preview_rows")) + _rows(module.get("details_rows")):
            left, right = _pair(row)
            if not left and not right:
                continue
            site_rows.append([_cell(left, "left"), _cell(_a_text(right), "right")])
    return site_rows
