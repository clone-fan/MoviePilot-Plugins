"""Telegram explicit-block renderer for the V7 Fusion card."""

import re
from copy import deepcopy
from typing import Any, Dict, Iterable, List, Sequence

from .fusion_completion import normalize_completion_tasks

from .fusion_card_model import validate_v7_card_model


def render_v7_rich_message(model: Dict[str, Any]) -> Dict[str, Any]:
    """Render a validated V7 model to one explicit InputRichMessage payload."""
    card = validate_v7_card_model(model)
    identity = card["identity"]
    blocks: List[Dict[str, Any]] = _identity_blocks(identity, card["state"])
    modules = list(card.get("modules") or [])
    if card["state"] == "loading":
        loading = next((item for item in modules if item.get("kind") == "loading"), None)
        if loading:
            blocks.append(_loading_block(loading))
        blocks.append(_identity_footer())
        return {"blocks": blocks}

    for index, module in enumerate(modules):
        previous = modules[index - 1] if index else None
        if index and not (_is_persistent_drawer(previous) and _is_persistent_drawer(module)):
            blocks.append({"type": "divider"})
        blocks.extend(_module_blocks(module, card["state"]))
    blocks.append(_identity_footer())
    return {"blocks": blocks}


def _identity_blocks(identity: Dict[str, Any], state: str) -> List[Dict[str, Any]]:
    refreshed = str(identity.get("refreshed_at") or "").strip()
    return [_table([
        _cell([{"type": "bold", "text": "融合通知"}, "\n", _a_text(f"更新 {refreshed}")], "center"),
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
        if aggregate:
            site_rows.append([
                _cell({"type": "bold", "text": "今日流量"}, "left"),
                _cell({"type": "bold", "text": aggregate}, "right"),
            ])
        for row in rows:
            left, right = _pair(row)
            site_rows.append([
                _cell(left, "left"),
                _cell({"type": "subscript", "text": right}, "right"),
            ])
        if site_rows:
            blocks.append(_multirow_table(site_rows))
    return [_details_block(summary, blocks, True)] if blocks else []


def _completion_blocks(module: Dict[str, Any], state: str) -> List[Dict[str, Any]]:
    tasks = normalize_completion_tasks(module.get("tasks"))
    cells = []
    for task in tasks:
        result = _completion_result_text(task["outcome"], task["result_status"])
        cells.append([_cell(task["title"], "center"), _cell(result, "right")])
    return [_details_block(_summary(module), [_multirow_table(cells)], False)] if cells else []


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


def _multirow_table(rows: List[List[Dict[str, Any]]], bordered: bool = False) -> Dict[str, Any]:
    return {"type": "table", "cells": rows, "is_bordered": bordered, "is_striped": False}


def _cell(text: Any, align: str, valign: str = "middle", colspan: int = 1) -> Dict[str, Any]:
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
    authored = _compact_summary_count(module.get("count"))
    if authored == "等待首次采集":
        return authored
    if owner == "persistent-sites":
        rows = _rows(module.get("preview_rows")) + _rows(module.get("details_rows"))
        match = re.fullmatch(r"(\d+)/(\d+)在线", authored)
        if match:
            online, total = (int(item) for item in match.groups())
            if not rows or total == len(rows):
                return f"{min(online, total)}/{total}在线"
        return f"{len(rows)}/{len(rows)}在线" if rows else ""
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
