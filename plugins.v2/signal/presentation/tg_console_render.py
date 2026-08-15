import re
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from app.log import logger
from app.schemas import NotificationType

from ..domain.fusion_card_model import build_v7_card_model, validate_v7_card_model
from ..domain.fusion_composition import (
    compose_v7_snapshot,
    parse_storage_rows,
    parse_subscription_rows,
)
from ..domain.fusion_event_ledger import append_actual_task_event, event_ledger_rows
from ..domain.fusion_rich_message import render_v7_rich_message


class TgConsoleRenderMixin:
    """Telegram fusion card HTML rendering ? chunks, tabs, metrics, icons, sections"""

    def _build_tg_console_rich_message(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Build the canonical V7 explicit-block payload for the current render path only."""
        model = state.get("v7_model") if isinstance(state, dict) else None
        try:
            model = validate_v7_card_model(model)
        except (TypeError, ValueError):
            model = None
        if model is None:
            model = validate_v7_card_model(self._compose_tg_console_v7_model(state))
            if isinstance(state, dict):
                state["v7_model"] = model
        return render_v7_rich_message(model)

    def _prepare_tg_console_v7_loading(self, state: Dict[str, Any]) -> Dict[str, Any]:
        snapshot = {
            "identity": self._v7_identity(),
            "loading": {
                "status": "collecting",
                "tasks": [["站点、存储", "采集中"], ["订阅追新", "等待"], ["实时活动", "等待"], ["今日完成", "等待"]],
            },
        }
        state["v7_state"] = "loading"
        state["v7_snapshot"] = snapshot
        state["v7_model"] = build_v7_card_model(snapshot, state="loading")
        return state["v7_model"]

    def _compose_tg_console_v7_model(self, state: Dict[str, Any]) -> Dict[str, Any]:
        site_snapshot = self._site_increment_snapshot()
        site_rows = [
            [str(item.get("name") or "站点"), f"↑{self._format_bytes(item.get('upload', 0))} · ↓{self._format_bytes(item.get('download', 0))}"]
            for item in site_snapshot.get("sites") or []
            if isinstance(item, dict)
        ]
        site_total = int(site_snapshot.get("active_count") or site_snapshot.get("visible_count") or len(site_rows))
        site_online = max(0, site_total - int(site_snapshot.get("error_count") or 0) - int(site_snapshot.get("stale_count") or 0))
        site_count = f"{site_online} / {site_total} 在线" if site_total else ""

        storage_lines = self._get_storage_health_locked()
        storage_rows = parse_storage_rows(storage_lines)
        subscription_rows = parse_subscription_rows(self._get_today_subscribe_updates_locked())
        completion_rows = event_ledger_rows(state.get("v7_event_ledger"), str(state.get("date") or self._today_prefix()))
        realtime = self._current_v7_realtime(state)
        anomalies = self._merge_v7_anomalies(state, self._current_v7_anomalies(site_snapshot, storage_lines))
        enabled = set()
        if bool(getattr(self, "_site_stat_enabled", False)):
            enabled.add("sites")
        if bool(getattr(self, "_health_check_enabled", False)):
            enabled.add("storage")
        if bool(getattr(self, "_subscribe_reminder_enabled", False)):
            enabled.add("subscriptions")
        snapshot, card_state = compose_v7_snapshot(
            identity=self._v7_identity(),
            site_rows=site_rows,
            site_count=site_count,
            storage_rows=storage_rows,
            subscription_rows=subscription_rows,
            completion_rows=completion_rows,
            realtime=realtime,
            anomalies=anomalies,
            enabled_persistent=enabled,
        )
        state["v7_snapshot"] = snapshot
        state["v7_state"] = card_state
        state["v7_model"] = build_v7_card_model(snapshot, state=card_state)
        return state["v7_model"]

    @staticmethod
    def _record_v7_anomaly(state: Dict[str, Any], key: str, anomaly: Dict[str, Any]) -> None:
        anomaly_key = str(key or "").strip()
        if not anomaly_key or not isinstance(anomaly, dict):
            return
        stored = state.get("v7_anomalies") if isinstance(state.get("v7_anomalies"), dict) else {}
        stored[anomaly_key] = dict(anomaly)
        state["v7_anomalies"] = stored

    @staticmethod
    def _clear_v7_anomaly(state: Dict[str, Any], key: str) -> None:
        anomaly_key = str(key or "").strip()
        stored = state.get("v7_anomalies") if isinstance(state.get("v7_anomalies"), dict) else {}
        if anomaly_key:
            stored.pop(anomaly_key, None)
        state["v7_anomalies"] = stored

    @staticmethod
    def _record_v7_event(state: Dict[str, Any], record: Dict[str, Any]) -> bool:
        event_date = str(state.get("date") or "").strip()
        ledger, added = append_actual_task_event(state.get("v7_event_ledger"), record, event_date)
        state["v7_event_ledger"] = ledger
        state.pop("v7_completion_events", None)
        return added

    @staticmethod
    def _merge_v7_anomalies(state: Dict[str, Any], collector_anomalies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        stored = state.get("v7_anomalies") if isinstance(state.get("v7_anomalies"), dict) else {}
        items = [dict(item) for item in stored.values() if isinstance(item, dict)]
        items.extend(dict(item) for item in collector_anomalies or [] if isinstance(item, dict))
        if not items:
            return []
        if len(items) == 1:
            return items
        affected = []
        details = []
        primary = []
        for item in items:
            primary_value = str(item.get("primary") or "").strip()
            if primary_value and primary_value not in primary:
                primary.append(primary_value)
            for owner in item.get("affected_owners") or []:
                owner_key = str(owner or "").strip()
                if owner_key and owner_key not in affected:
                    affected.append(owner_key)
            rows = item.get("details_rows") if isinstance(item.get("details_rows"), list) else []
            details.extend(rows)
        return [{
            "owner": "current-anomalies",
            "kicker": "当前异常",
            "count": f"{len(items)} 项",
            "primary": "、".join(primary[:3]) or "需要关注",
            "context": "需要关注 · 多个组件",
            "meta": next((str(item.get("meta") or "") for item in items if item.get("meta")), ""),
            "affected_owners": affected,
            "details_rows": details[:8],
        }]

    def _v7_identity(self) -> Dict[str, str]:
        version = str(getattr(self, "plugin_version", "1.0.13") or "1.0.13")
        return {"version": version if version.startswith("v") else f"v{version}", "refreshed_at": datetime.now().strftime("%H:%M")}

    @staticmethod
    def _current_v7_realtime(state: Dict[str, Any]) -> List[Dict[str, Any]]:
        model = state.get("v7_model") if isinstance(state, dict) else None
        if isinstance(model, dict):
            return [dict(item) for item in model.get("modules") or [] if item.get("owner") in {"realtime-media", "realtime-task-backup"}]
        snapshot = state.get("v7_snapshot") if isinstance(state, dict) else None
        return [dict(item) for item in (snapshot or {}).get("realtime") or [] if isinstance(item, dict)]

    @staticmethod
    def _current_v7_anomalies(site_snapshot: Dict[str, Any], storage_lines: List[str]) -> List[Dict[str, Any]]:
        rows = []
        affected = []
        if int(site_snapshot.get("error_count") or 0) or int(site_snapshot.get("stale_count") or 0):
            rows.append(["站点快照存在异常或过期", datetime.now().strftime("%H:%M")])
            affected.append("persistent-sites")
        for line in storage_lines or []:
            text = str(line or "")
            if "空间偏紧" in text or "检查异常" in text:
                rows.append([re.sub(r"^[\s⦁•]+", "", text), datetime.now().strftime("%H:%M")])
                if "persistent-storage" not in affected:
                    affected.append("persistent-storage")
        if not rows:
            return []
        return [{
            "owner": "current-anomalies",
            "kicker": "当前异常",
            "count": f"{len(rows)} 项",
            "primary": "、".join("站点数据" if owner == "persistent-sites" else "存储空间" for owner in affected),
            "context": "需要关注 · 健康巡查",
            "meta": f"最近 {rows[0][1]}",
            "affected_owners": affected,
            "details_rows": rows,
        }]

    def _build_tg_console_reply_markup(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return {"inline_keyboard": []}

    def _build_tg_console_html(self, state: Dict[str, Any]) -> str:
        self._sanitize_fusion_media_activity_state(state)
        self._sanitize_fusion_update_state(state)
        now_label = datetime.now().strftime("%H:%M:%S")
        reports = state.get("reports") or {}
        daily_report = reports.get("daily_report") or {}
        daily_text = str(daily_report.get("text") or "")
        chunks = self._build_fusion_console_chunks(state, daily_text, now_label)

        running = state.get("running_actions") or {}
        if running:
            chunks.append(self._telegram_quote_html("运行中", [f"{v.get('label') or k}：{v.get('time') or ''}" for k, v in running.items()], max_items=5))
        pending = [
            f"{v.get('label') or v.get('action')}（60 秒内确认）"
            for v in (state.get("pending_actions") or {}).values()
            if v.get("confirm_for") and not v.get("done")
        ]
        if pending:
            chunks.append(self._telegram_details_html("待确认动作", self._telegram_list_html(pending)))
        if state.get("last_error"):
            chunks.append(self._telegram_quote_html("最近错误", [str(state.get("last_error"))], max_items=1))
        return self._clip_telegram_html("\n".join(chunks))

    def _build_fusion_console_chunks(self, state: Dict[str, Any], daily_text: str, now_label: str) -> List[str]:
        stamp = datetime.now().strftime("%Y-%m-%d") + f" {now_label}"
        greeting = self._daily_greeting_locked()
        chunks = [
            f"<h2>📮 MP 运维日报｜🕒 {self._html_escape(stamp)}</h2>",
            f"<p>{self._html_escape(greeting)}</p>",
            self._build_fusion_system_line(daily_text, state),
        ]
        media_html = self._build_fusion_media_headline(state)
        if media_html:
            chunks.append(media_html)
        update_html = self._build_fusion_update_headline(state)
        if update_html:
            chunks.append(update_html)
        chunks.append("<p>───────────────────<br><i>💡 请点击下方的横向分类按钮，查阅今日具体运行指标。</i></p>")
        has_stream_data = bool((state.get("reports") or {}) or (state.get("columns") or {}) or daily_text.strip() or state.get("tab_touched"))
        if has_stream_data:
            active_tab = self._normalize_fusion_tab(str(state.get("active_tab") or "subscribe_site"))
            chunks.append(self._build_fusion_tab_html(active_tab, state, daily_text))
        return [x for x in chunks if x]

    @staticmethod
    def _daypart_label() -> str:
        hour = datetime.now().hour
        if hour < 6:
            return "凌晨"
        if hour < 12:
            return "早上"
        if hour < 14:
            return "中午"
        if hour < 18:
            return "下午"
        return "晚上"

    def _build_fusion_system_line(self, daily_text: str, state: Optional[Dict[str, Any]] = None) -> str:
        if not str(daily_text or "").strip() and state:
            daily_text = str(((state.get("reports") or {}).get("daily_report") or {}).get("text") or "")
        version = self._fusion_version_label(daily_text)
        normal, stale, failed, total = self._fusion_site_counts(daily_text)
        if (not total or (total and normal == 0 and failed == 0 and stale == 0)) and state:
            normal, stale, failed, total = self._fusion_site_counts_from_state(state)
        pending_version = self._fusion_pending_update_label(state, daily_text) if state else ""
        parts = [f"🟢 正常 ({normal}/{total})"]
        if stale:
            parts.append(f"🟡 过期 ({stale}/{total})")
        parts.append(f"🔴 失败 ({failed}/{total})")
        system_tail = f" ｜ <b>待更新：</b> <code>{self._telegram_text_html(pending_version)}</code>" if pending_version else ""
        return (
            "<p>"
            f"<b>🤖 系统：</b> <code>{self._telegram_text_html(version)}</code>{system_tail}<br>"
            f"<b>🩺 站点：</b> {' ｜ '.join(self._html_escape(x) for x in parts)}"
            "</p>"
        )

    def _build_fusion_media_headline(self, state: Dict[str, Any]) -> str:
        self._prune_fusion_media_activity_state(state)
        media = self._fusion_media_activity_report(state)
        text = str((media or {}).get("text") or "")
        if not text:
            return ""
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not lines:
            return ""
        headline = lines[0]
        detail = lines[1:4]
        body = f"<b>🎬 {self._html_escape(headline)}</b>"
        if detail:
            body += "<br>" + "<br>".join(f"  {self._html_escape(x)}" for x in detail)
        return f"<blockquote>{body}</blockquote>"

    def _build_fusion_update_headline(self, state: Dict[str, Any]) -> str:
        return ""

    @classmethod
    def _fusion_line_icon(cls, column_key: str, line: str = "") -> str:
        text = str(line or "")
        if column_key == "health":
            if any(key in text for key in ("异常", "失败", "错误", "失联", "过期")) and "0 项异常" not in text:
                return "⚠️"
            if any(key in text for key in ("全部正常", "正常项", "状态：正常", "状态:正常")):
                return "✅"
            if text.startswith(("状态：", "状态:")):
                return "✅"
            return "🩺"
        icons = {
            "site_stats": "📈",
            "download_transfer": "📥",
            "subscribe": "📺",
            "storage": "💾",
            "media": "🎬",
            "maintenance": "🧰",
            "updates": "🆙",
        }
        return icons.get(column_key, "•")

    @classmethod
    def _fusion_line_body(cls, line: str) -> str:
        text = re.sub(r"^[\s⦁•·*\-]+", "", str(line or "").strip()).strip()
        for icon in ("📊", "📈", "📥", "📺", "💾", "🎬", "🩺", "🧰", "🆙", "✅", "⚠️", "⚠", "⏳"):
            if text.startswith(icon):
                text = text[len(icon):].strip()
                text = re.sub(r"^[\s:：|｜\-]+", "", text).strip()
                break
        return text or "无"

    def _fusion_line_html(self, column_key: str, line: str, show_chips: bool = True) -> str:
        if show_chips and column_key == "site_stats":
            return self._fusion_site_metric_html(line)
        if show_chips and column_key == "storage":
            return self._fusion_storage_metric_html(line)
        if show_chips and column_key in {"health", "maintenance", "updates", "subscribe"}:
            return self._fusion_compact_metric_html(column_key, line)
        icon = self._fusion_line_icon(column_key, line)
        body = self._fusion_line_body(line)
        title, chips, note = self._fusion_line_layout(body)
        title_html = self._telegram_text_html(title)
        head = f"<b>{self._html_escape(icon)} {title_html}</b>"
        if not show_chips:
            return head
        if chips:
            chip_rows = [self._telegram_text_html(item) for item in chips[:6]]
            if len(chip_rows) == 1 and not note and len(self._strip_html_tags(chip_rows[0])) <= 28:
                return f"{head}：{chip_rows[0]}"
            note_rows = [self._telegram_text_html(note)] if note else []
            return f"{head}<br>{'<br>'.join(chip_rows + note_rows)}"
        if note:
            return f"{head}<br>{self._telegram_text_html(note)}"
        return head

    def _fusion_site_metric_html(self, line: str) -> str:
        body = self._fusion_line_body(line)
        title, detail = self._split_fusion_line_title(body)
        source = detail or body
        metrics = [
            ("⬆️", self._fusion_match_metric(source, r"(?:↑|⬆️?|上传[：:]?)\s*([\d,.]+\s*(?:[KMGTPE]?i?B|[KMGTPE]?B|[KMGTPE]?|B)?)")),
            ("⬇️", self._fusion_match_metric(source, r"(?:↓|⬇️?|下载[：:]?)\s*([\d,.]+\s*(?:[KMGTPE]?i?B|[KMGTPE]?B|[KMGTPE]?|B)?)")),
            ("📊", self._fusion_match_metric(source, r"(?:分享率|分享|📊)\s*[：:]?\s*([\d,.]+)")),
            ("🪙", self._fusion_match_metric(source, r"(?:魔力|🪙|💰)\s*[：:]?\s*([\d,.]+)")),
        ]
        metric_parts = [f"{icon} {self._format_fusion_metric_value(value)}" for icon, value in metrics if value]
        if not metric_parts:
            return self._fusion_compact_metric_html("site_stats", line)
        return self._fusion_bullet_html("📈", title, [" | ".join(metric_parts)])

    def _fusion_storage_metric_html(self, line: str) -> str:
        body = self._fusion_line_body(line)
        title, detail = self._split_fusion_line_title(body)
        source = detail or body
        usage_match = re.search(
            r"(?P<used>[\d.]+\s*[KMGTPE]?i?B?|[\d.]+\s*[KMGTPE])\s*/\s*"
            r"(?P<total>[\d.]+\s*[KMGTPE]?i?B?|[\d.]+\s*[KMGTPE]).*?"
            r"(?P<icon>[🟢🟠🔴])?\s*已用\s*(?P<pct>\d{1,3})%",
            source,
            re.I,
        )
        if not usage_match:
            usage_match = re.search(
                r"已用\s*(?P<pct>\d{1,3})%.*?"
                r"(?P<used>[\d.]+\s*[KMGTPE]?i?B?|[\d.]+\s*[KMGTPE])\s*/\s*"
                r"(?P<total>[\d.]+\s*[KMGTPE]?i?B?|[\d.]+\s*[KMGTPE]).*?"
                r"(?P<icon>[🟢🟠🔴])?",
                source,
                re.I,
            )
        if usage_match:
            pct = int(usage_match.group("pct"))
            icon = usage_match.group("icon") or ("🔴" if pct >= 85 else ("🟠" if pct >= 70 else "🟢"))
            used = self._format_fusion_metric_value(usage_match.group("used"))
            total = self._format_fusion_metric_value(usage_match.group("total"))
            bar = self._fusion_usage_bar(float(pct), width=8)
            return self._fusion_bullet_html("💾", title, [f"{used}/{total}", f"{bar} {icon} 已用 {pct}%"])
        simple = self._format_fusion_metric_value(source)
        return self._fusion_bullet_html("💾", title, [simple] if simple else [])

    def _fusion_compact_metric_html(self, column_key: str, line: str) -> str:
        body = self._fusion_line_body(line)
        title, detail = self._split_fusion_line_title(body)
        icon = self._fusion_compact_icon(column_key, title, detail or body)
        if not detail:
            return f"<b>{self._html_escape(icon)} {self._telegram_text_html(title)}</b>"
        return self._fusion_bullet_html(icon, title, self._fusion_compact_detail_lines(column_key, title, detail))

    @classmethod
    def _fusion_compact_icon(cls, column_key: str, title: str, detail: str = "") -> str:
        text = f"{title} {detail}"
        if column_key == "health":
            if str(title).startswith("状态"):
                return "⚠️" if any(key in text for key in ("异常", "失败", "错误")) and "异常 0" not in text else "✅"
            if str(title).startswith("巡查项"):
                return "🩺"
            if str(title).startswith("正常项"):
                return "✅"
            return "⚠️" if any(key in text for key in ("异常", "失败", "错误")) and "异常 0" not in text else "🩺"
        return {
            "site_stats": "📈",
            "subscribe": "📺",
            "maintenance": "🧰",
            "updates": "🆙",
        }.get(column_key, cls._fusion_line_icon(column_key, text))

    @classmethod
    def _fusion_compact_detail_lines(cls, column_key: str, title: str, detail: str) -> List[str]:
        text = str(detail or "").strip()
        if column_key == "health" and str(title).startswith("巡查项"):
            return [text]
        if column_key == "maintenance":
            summarized = cls._summarize_fusion_maintenance_line(f"{title}：{text}" if title else text)
            _, text = cls._split_fusion_line_title(summarized)
        parts = re.split(r"\s*[｜|]\s*|[；;]\s*|\n+", text)
        cleaned = [cls._format_fusion_metric_value(part.strip()) for part in parts if part and part.strip()]
        return cleaned or [cls._format_fusion_metric_value(text)]

    def _fusion_bullet_html(self, icon: str, title: str, details: List[str]) -> str:
        head = f"<b>{self._html_escape(icon)} {self._telegram_text_html(title)}</b>"
        rows = [self._html_escape(str(item or "").strip()) for item in (details or []) if str(item or "").strip()]
        if not rows:
            return head
        return f"{head}<br>{'<br>'.join(rows)}"

    @staticmethod
    def _fusion_match_metric(text: str, pattern: str) -> str:
        match = re.search(pattern, str(text or ""), re.I)
        return match.group(1).strip() if match else ""

    @staticmethod
    def _format_fusion_metric_value(value: str) -> str:
        text = re.sub(r"\s+", " ", str(value or "").strip())
        if not text:
            return ""
        def repl(match: re.Match) -> str:
            number = match.group(1)
            unit = match.group(2).upper()
            if unit in {"K", "M", "G", "T", "P", "E"}:
                unit = f"{unit}B"
            return f"{number} {unit}"
        return re.sub(r"(\d(?:[\d,.]*\d)?)(?:\s*)([KMGTPE]i?B|[KMGTPE]B|[KMGTPE]\b|B\b)", repl, text, flags=re.I)

    @staticmethod
    def _strip_html_tags(value: str) -> str:
        return re.sub(r"<[^>]+>", "", str(value or ""))

    @classmethod
    def _fusion_line_layout(cls, body: str) -> Tuple[str, List[str], str]:
        text = str(body or "").strip()
        if not text:
            return "无数据", [], ""
        title, detail = cls._split_fusion_line_title(text)
        if not detail:
            return title, [], ""
        parts = cls._split_fusion_detail_parts(detail)
        chips = [cls._normalize_fusion_chip(part) for part in parts]
        chips = [part for part in chips if part]
        long_parts = [part for part in chips if len(part) > 26]
        if long_parts and len(chips) <= 2:
            return title, [], "；".join(chips)
        compact = [part for part in chips if len(part) <= 32]
        overflow = [part for part in chips if len(part) > 32]
        return title, compact[:5], "；".join(overflow[:2])

    @classmethod
    def _split_fusion_line_title(cls, text: str) -> Tuple[str, str]:
        normalized = re.sub(r"\s+", " ", str(text or "").strip())
        for sep in ("：", ":"):
            if sep in normalized:
                head, tail = normalized.split(sep, 1)
                head = head.strip(" -｜|·")
                tail = tail.strip(" -｜|·")
                if head and tail:
                    return head, tail
        return normalized, ""

    @classmethod
    def _split_fusion_detail_parts(cls, detail: str) -> List[str]:
        raw = str(detail or "").strip()
        if not raw:
            return []
        parts = re.split(r"\s*[｜|]\s*|\s*/\s*|\s+·\s+|；|;|，(?=\S)", raw)
        return [part.strip(" -") for part in parts if part and part.strip(" -")]

    @classmethod
    def _normalize_fusion_chip(cls, text: str) -> str:
        item = str(text or "").strip()
        replacements = [
            (r"^(?:上传[：:]?|[⬆↑])\s*", "⬆ 上传："),
            (r"^(?:下载[：:]?|[⬇↓])\s*", "⬇ 下载："),
            (r"^(?:分享率|📊)\s*[：:]?\s*", "📊 分享："),
            (r"^[🪙💰]\s*", "🪙 魔力："),
            (r"^✅\s*", "✅ 通过："),
            (r"^⚠️?\s*", "⚠️ 异常："),
            (r"^🆙\s*", "🆙 更新："),
            (r"^💾\s*", "💾 存储："),
            (r"^📥\s*", "📥 入库："),
            (r"^🎬\s*", "🎬 媒体："),
        ]
        for pattern, repl in replacements:
            item = re.sub(pattern, repl, item).strip()
        label_icons = {
            "季集": "📦",
            "时间": "🕘",
            "类别": "🎭",
            "站点": "🌐",
            "质量": "🌟",
            "大小": "💾",
            "做种": "🌱",
            "标签": "🏷️",
            "名称": "🧾",
            "设备": "📺",
            "用户": "👤",
            "IP地址": "🌐",
            "巡查项": "🩺",
            "状态": "✅",
        }
        for label, prefix in label_icons.items():
            if re.match(rf"^{re.escape(label)}\s*[：:]", item) and not item.startswith(prefix):
                item = f"{prefix} {item}"
                break
        item = re.sub(r"\s+", " ", item)
        item = re.sub(r"(\d)([KMGTPE]i?B\b)", r"\1 \2", item, flags=re.I)
        return item.strip(" -｜|·")

    @classmethod
    def _fusion_metric_codes(cls, column_key: str, lines: List[str]) -> List[str]:
        merged = " ｜ ".join(cls._fusion_line_body(line) for line in (lines or []) if str(line or "").strip())
        if not merged:
            return []
        specs = {
            "site_stats": [
                ("↑", r"(?:↑|⬆|上传[：:]?)\s*([\d,.]+\s*(?:[KMGTPE]?B|[KMGTPE]?iB)?)"),
                ("↓", r"(?:↓|⬇|下载[：:]?)\s*([\d,.]+\s*(?:[KMGTPE]?B|[KMGTPE]?iB)?)"),
                ("分享", r"(?:分享率|📊)\s*[：:]?\s*([\d,.]+)"),
                ("魔力", r"(?:魔力|🪙)\s*[：:]?\s*([\d,.]+)"),
            ],
            "media": [
                ("电影", r"电影\s*([\d,.]+)"),
                ("电视剧", r"电视剧\s*([\d,.]+)"),
                ("剧集", r"剧集\s*([\d,.]+)"),
                ("用户", r"用户\s*([\d,.]+)"),
            ],
            "health": [
                ("通过", r"通过\s*([\d,.]+)\s*项"),
                ("异常", r"异常\s*([\d,.]+)\s*项"),
            ],
            "storage": [
                ("已用", r"(\d{1,3})\s*%"),
            ],
        }
        result = []
        for label, pattern in specs.get(column_key, []):
            match = re.search(pattern, merged, re.I)
            if not match:
                continue
            value = match.group(1).strip()
            if label == "已用":
                value = f"{value}%"
            result.append(f"{label} {value}")
        if column_key == "subscribe":
            count = len([x for x in lines or [] if str(x or "").strip() and "暂无" not in str(x)])
            if count:
                result.append(f"今日 {count} 项")
        if column_key == "download_transfer":
            if "无" in merged and len(merged) <= 8:
                return []
            count = len([x for x in lines or [] if str(x or "").strip() and str(x).strip() != "无"])
            if count:
                result.append(f"今日 {count} 项")
        return result[:4]

    def _fusion_prepare_section_lines(self, column_key: str, lines: List[str]) -> List[str]:
        if column_key == "health":
            return self._summarize_fusion_health_lines(lines)
        if column_key == "maintenance":
            return [self._summarize_fusion_maintenance_line(line) for line in (lines or [])]
        return lines

    @classmethod
    def _summarize_fusion_health_lines(cls, lines: List[str]) -> List[str]:
        cleaned = [re.sub(r"^[\s⦁•·*\-]+", "", str(line or "").strip()).strip() for line in (lines or [])]
        cleaned = [line for line in cleaned if line]
        if not cleaned:
            return []

        known_labels = set(cls._health_name_map().values())
        status_line = ""
        count_line = ""
        ok_labels: List[str] = []
        failures: List[str] = []
        passthrough: List[str] = []

        for line in cleaned:
            body = re.sub(r"^(?:✅|⚠️|⚠|🩺)\s*", "", line).strip()
            if body.startswith("状态：") or body.startswith("状态:"):
                status_line = body
                continue
            if body.startswith("巡查项：") or body.startswith("巡查项:"):
                count_line = body
                continue
            if body.startswith("正常项：") or body.startswith("正常项:"):
                _, detail = cls._split_fusion_line_title(body)
                ok_labels.extend([x.strip() for x in re.split(r"[、,，]\s*", detail) if x.strip()])
                continue

            label, detail = cls._split_fusion_line_title(body)
            is_failure = any(key in body for key in ("异常", "失败", "错误", "超时", "不存在", "权限不足", "超过", "偏紧", "无法", "无响应")) and "异常 0" not in body
            if is_failure:
                compact = cls._compact_health_detail(detail or body)
                failures.append(f"异常：{label} - {compact}" if compact and label else f"异常：{compact or body}")
            elif label in known_labels:
                ok_labels.append(label)
            else:
                passthrough.append(body)

        output: List[str] = []
        if status_line:
            output.append(status_line)
        elif failures:
            output.append(f"状态：发现 {len(failures)} 项异常")
        else:
            output.append("状态：全部正常")
        if count_line:
            output.append(count_line)
        if ok_labels:
            unique_ok = cls._unique_keep_order(ok_labels)
            output.append(f"正常项：{'、'.join(unique_ok)}")
        output.extend(failures)
        if len(output) <= 1 and passthrough:
            output.extend(passthrough[:3])
        return output

    @classmethod
    def _summarize_fusion_maintenance_line(cls, line: str) -> str:
        body = cls._fusion_line_body(line)
        title, detail = cls._split_fusion_line_title(body)
        if not detail:
            return body
        parts = [part.strip() for part in re.split(r"\s*[｜|]\s*|[；;]\s*", detail) if part and part.strip()]
        if not parts:
            return body
        status = parts[0]
        tail = "；".join(parts[1:])
        summary = cls._summarize_fusion_task_text(title, tail) if tail else ""
        if summary and summary != status:
            return f"{title}：{status}｜{summary}"
        return f"{title}：{status}"

    def _fusion_section_html(self, column_key: str, title: str, lines: List[str], max_items: int = 12) -> str:
        all_lines = [str(x or "").strip() for x in (lines or []) if str(x or "").strip()]
        all_lines = self._fusion_prepare_section_lines(column_key, all_lines)
        visible = all_lines[:max_items]
        if not visible:
            label = re.sub(r"^[^\w\u4e00-\u9fff]+\s*", "", title) or "栏目"
            visible = [f"今日暂无{label}数据"]
        line_html = [self._fusion_line_html(column_key, line, show_chips=True) for line in visible]
        body = "<ul>" + "".join(f"<li>{item}</li>" for item in line_html) + "</ul>" if line_html else "<p>📭 无</p>"
        total = len(all_lines)
        if total > max_items:
            more = f"<b>{self._html_escape(self._fusion_line_icon(column_key))} {self._html_escape(f'另 {total - max_items} 项')}</b>"
            body = body.replace("</ul>", f"<li>{more}</li></ul>")
        return self._telegram_details_html(title, body)

    def _build_fusion_tab_html(self, tab_key: str, state: Dict[str, Any], daily_text: str) -> str:
        category_key = self._normalize_fusion_tab(tab_key)
        category = next((x for x in self._fusion_category_registry() if x["key"] == category_key), None)
        if category:
            column_meta = {x["key"]: x for x in self._fusion_column_registry()}
            sections = []
            for child in self._fusion_category_children(category_key):
                meta = column_meta.get(child) or {}
                if child == "download_transfer":
                    today_lines, library_lines = self._fusion_download_transfer_groups(state, daily_text)
                    sections.append(self._fusion_section_html("download_transfer", "📥 今日下载", today_lines))
                    sections.append(self._fusion_section_html("download_transfer", "📦 入库整理", library_lines))
                    continue
                lines = self._fusion_tab_lines(child, state, daily_text)
                if child == "site_stats":
                    title = "📈 站点增量"
                elif child == "media":
                    title = "🎬 媒体统计"
                else:
                    title = f"{meta.get('icon') or ''} {meta.get('label') or child}".strip()
                sections.append(self._fusion_section_html(child, title, lines))
            body = "".join(sections) if sections else "暂无数据"
            return body
        meta = next((x for x in self._fusion_column_registry() if x["key"] == tab_key), self._fusion_column_registry()[0])
        lines = self._fusion_tab_lines(tab_key, state, daily_text)
        if not lines:
            lines = [f"暂无{meta['label']}数据"]
        title = f"{meta.get('icon') or ''} {meta.get('label') or tab_key}".strip()
        return self._fusion_section_html(tab_key, title, lines)

    def _fusion_download_transfer_groups(self, state: Dict[str, Any], daily_text: str) -> Tuple[List[str], List[str]]:
        today = self._extract_report_section_items(daily_text, ("今日下载",))
        library = self._extract_report_section_items(daily_text, ("入库整理",))
        if today or library:
            return today, library
        lines = self._fusion_tab_lines("download_transfer", state, daily_text)
        today_lines: List[str] = []
        library_lines: List[str] = []
        for line in lines:
            text = str(line or "")
            if "入库" in text or "整理" in text or "转移" in text:
                library_lines.append(text)
            else:
                today_lines.append(text)
        return today_lines, library_lines

    def _fusion_tab_lines(self, tab_key: str, state: Dict[str, Any], daily_text: str) -> List[str]:
        items = ((state.get("columns") or {}).get(tab_key) or {}).get("items") or []
        if items:
            rows = []
            for item in items[:8]:
                if tab_key == "media" and self._is_fusion_media_activity(item):
                    continue
                title = str(item.get("title") or "").strip()
                text = str(item.get("text") or "").strip()
                text_lines = self._clean_fusion_item_text_lines(text)
                rows.extend(text_lines or ([title] if title else []))
            return rows
        if tab_key == "site_stats":
            return self._extract_report_section_items(daily_text, ("站点状态", "站点增量"))
        if tab_key == "download_transfer":
            return self._extract_report_section_items(daily_text, ("今日下载", "入库整理"))
        if tab_key == "subscribe":
            return self._extract_report_section_items(daily_text, ("订阅追新",))
        if tab_key == "storage":
            return self._format_fusion_storage_items(self._extract_report_section_items(daily_text, ("存储空间",)))
        if tab_key == "media":
            report = (state.get("reports") or {}).get("media_stat") or {}
            return self._clean_fusion_item_text_lines(str(report.get("text") or ""))
        if tab_key == "health":
            return self._extract_report_section_items(daily_text, ("健康巡查",))
        return []

    @staticmethod
    def _clean_fusion_item_text_lines(text: str) -> List[str]:
        rows = []
        for raw in str(text or "").splitlines():
            line = re.sub(r"^[\s⦁•·*-]+", "", str(raw or "").strip()).strip()
            if line:
                rows.append(line)
        return rows

    def _build_tg_console_daily_chunks(self, daily_text: str) -> List[str]:
        parts = self._split_daily_report_text(daily_text)
        chunks = [f"<h2>{self._html_escape(parts.get('title') or 'MP 运维日报')}</h2>"]
        intro = [self._html_escape(line) for line in (parts.get("intro") or []) if str(line or "").strip()]
        if intro:
            chunks.append("<p>" + "<br>".join(intro) + "</p>")
        overview = self._telegram_overview_table(parts)
        if overview:
            chunks.append(overview)

        appended_site = False
        appended_storage = False
        for section in parts.get("sections") or []:
            header = str(section.get("title") or "").strip()
            lines = section.get("lines") or []
            if header.startswith("🤖"):
                chunks.append(self._telegram_quote_html(header, self._telegram_section_items(lines), max_items=3))
            elif header.startswith("📡"):
                if not appended_site:
                    site_html = self._build_tg_console_site_lights(daily_text)
                    if site_html:
                        chunks.append(site_html)
                    appended_site = True
            elif header.startswith("📈"):
                chunks.append(self._telegram_details_html(header, self._telegram_increment_table("", lines)))
            elif header.startswith("📥") or header.startswith("📦") or header.startswith("📺"):
                chunks.append(self._telegram_details_html(header, self._telegram_general_list_html(header, self._telegram_section_items(lines))))
            elif header.startswith("💾"):
                if not appended_storage:
                    storage_html = self._build_tg_console_storage_matrix(daily_text)
                    chunks.append(storage_html or self._telegram_details_html(header, self._telegram_storage_table("", lines)))
                    appended_storage = True
            elif header.startswith("🎬"):
                continue
            elif header.startswith("🩺"):
                chunks.append(self._telegram_details_html(header, self._telegram_health_list_html(self._telegram_section_items(lines))))
            elif header.startswith("🧾") or header.startswith("⚠️"):
                continue
            else:
                chunks.append(f"<h3>{self._html_escape(header)}</h3>{self._telegram_list_html(self._telegram_section_items(lines))}")

        if not appended_site:
            site_html = self._build_tg_console_site_lights(daily_text)
            if site_html:
                chunks.append(site_html)
        if not appended_storage:
            storage_html = self._build_tg_console_storage_matrix(daily_text)
            if storage_html:
                chunks.append(storage_html)
        return chunks

    def _build_tg_console_core_badges(self, reports: Dict[str, Any], daily_text: str = "") -> str:
        version = self._match_text(r"(?:当前版本|版本)[:：]\s*([^\n]+)", daily_text) or "MoviePilot"
        update_status = self._match_text(r"(?:最新版本|更新状态)[:：]\s*([^\n]+)", daily_text) or "记录抽空更新"
        health_section = reports.get("health_check") or {}
        health_text = str(health_section.get("text") or "")
        health_line = self._match_text(r"状态[:：]\s*([^\n]+)", health_text) or self._match_text(r"健康巡查[:：]\s*([^\n]+)", daily_text) or "等待巡查"
        health_icon = "🟢" if ("全部正常" in health_text or "异常 0" in health_text or "全部正常" in daily_text) else "🟡"
        health_count = self._tg_console_health_count_label(health_text)
        health_count_html = f" <code>{self._telegram_text_html(health_count)}</code>" if health_count else ""
        return (
            "<blockquote>"
            f"<b>🤖 核心系统：</b> <code>{self._telegram_text_html(version)}</code><br>"
            f"<b>🆙 更新状态：</b> <code>{self._telegram_text_html(update_status)}</code><br>"
            f"<b>🩺 健康巡查：</b> {self._html_escape(health_icon)} {self._telegram_text_html(health_line)}{health_count_html}"
            "</blockquote>"
        )

    @classmethod
    def _tg_console_health_count_label(cls, health_text: str) -> str:
        match = re.search(r"共\s*(\d+)\s*项[，,]\s*通过\s*(\d+)\s*项[，,]\s*异常\s*(\d+)\s*项", str(health_text or ""))
        if not match:
            return ""
        total, passed, _failed = match.groups()
        return f"{passed}/{total}"

    def _build_tg_console_storage_matrix(self, daily_text: str) -> str:
        items = self._extract_report_section_items(daily_text, ("存储空间",))
        if not items:
            return ""
        normalized = []
        for item in items[:8]:
            text = re.sub(r"^\s*[•\-\s]+", "", str(item or "").strip())
            if text:
                normalized.append(f"📁 {text}")
        return self._telegram_details_html("💾 存储空间", self._telegram_list_html(normalized))

    def _build_tg_console_site_lights(self, daily_text: str) -> str:
        items = self._extract_report_section_items(daily_text, ("站点状态",))
        if not items:
            return ""
        green: List[Tuple[str, str]] = []
        amber: List[Tuple[str, str]] = []
        red: List[Tuple[str, str]] = []
        for item in items:
            text = re.sub(r"^\s*[•\-\s]+", "", str(item or "").strip())
            if not text:
                continue
            name, detail = self._tg_console_site_name_detail(text)
            if "异常" in text or "Cookie" in text or "失联" in text or "失败" in text:
                red.append((name, detail))
            elif "过期" in text:
                amber.append((name, detail))
            else:
                green.append((name, detail))
        rows = [
            self._tg_console_site_group_html("🟢 同步正常", green, "暂无正常站点"),
            self._tg_console_site_group_html("🟡 数据过期", amber, "暂无过期站点"),
            self._tg_console_site_group_html("🔴 失联故障", red, "无严重故障断连站点"),
        ]
        body = "<ul>" + "".join(f"<li>{row}</li>" for row in rows if row) + "</ul>"
        return f"<details open><summary>📊 站点统计</summary>{body}</details>"

    @staticmethod
    def _tg_console_site_name_detail(text: str) -> Tuple[str, str]:
        clean = str(text or "").strip()
        parts = re.split(r"\s*(?:\||：|:)\s*", clean, maxsplit=1)
        name = parts[0].strip() if parts else clean
        detail = parts[1].strip() if len(parts) > 1 else ""
        return name or clean, detail

    @classmethod
    def _tg_console_site_group_html(cls, label: str, sites: List[Tuple[str, str]], empty_text: str) -> str:
        title = f"{cls._html_escape(label)} ({len(sites)})"
        if not sites:
            return f"{title}：{cls._html_escape(empty_text)}"
        chips = []
        for name, detail in sites[:12]:
            chip = f"<code>{cls._telegram_text_html(name)}</code>"
            if detail:
                chip += f" {cls._telegram_text_html(detail)}"
            chips.append(chip)
        if len(sites) > 12:
            chips.append(cls._html_escape(f"另 {len(sites) - 12} 个"))
        return f"{title}：" + "、".join(chips)

    def _build_tg_console_footer(self, daily_text: str, time_label: str = "") -> str:
        media_items = self._extract_report_section_items(daily_text, ("媒体统计",))
        stats = self._tg_console_media_footer_parts(media_items)
        if not stats and not time_label:
            return ""
        lines = []
        if stats:
            lines.append(" ｜ ".join(stats))
        if time_label:
            lines.append(f"🕓 {self._html_escape(time_label)}")
        return "<blockquote>" + "<br>".join(lines) + "</blockquote>"

    @classmethod
    def _tg_console_media_footer_parts(cls, media_items: List[str]) -> List[str]:
        label_icons = {"电影": "🎬", "电视剧": "📺", "剧集": "📺", "用户": "👤"}
        found: Dict[str, str] = {}
        for item in media_items or []:
            for label, value in re.findall(r"(电影|电视剧|剧集|用户)\s+(\d+)", str(item or "")):
                found[label] = value
        parts = []
        for label in ("电影", "剧集"):
            if label in found:
                parts.append(f"{label_icons[label]} {cls._html_escape(found[label])} {cls._html_escape(label)}")
        if "剧集" not in found and "电视剧" in found:
            parts.append(f"{label_icons['电视剧']} {cls._html_escape(found['电视剧'])} 电视剧")
        if "用户" in found:
            parts.append(f"{label_icons['用户']} {cls._html_escape(found['用户'])} 用户")
        return parts

    @staticmethod
    def _extract_report_section_items(text: str, needles: Tuple[str, ...]) -> List[str]:
        lines = [str(line or "").strip() for line in str(text or "").splitlines()]
        items: List[str] = []
        collecting = False
        for line in lines:
            if not line:
                continue
            is_header = not re.match(r"^[•\-\s]", line) and any(ch in line for ch in ("🤖", "📡", "📈", "📥", "📦", "📺", "💾", "🎬", "🩺", "🧾", "⚠️", "📗", "📊", "📜", "💱"))
            if is_header and any(needle in line for needle in needles):
                collecting = True
                continue
            if collecting and is_header:
                break
            if collecting:
                items.append(line)
        return items

    def _build_media_activity_html(self, section: Dict[str, Any]) -> str:
        text = str((section or {}).get("text") or "")
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if not lines:
            return ""
        title = f"媒体动态｜{(section or {}).get('time') or ''}".rstrip("｜")
        level = str((section or {}).get("level") or "")
        headline = "当前暂无媒体播放" if level == "idle" else lines[0]
        detail = ([lines[0]] + lines[2:]) if level == "idle" and len(lines) > 1 else (lines[1:] if len(lines) > 1 else [])
        body = f"<b>{self._telegram_text_html(headline)}</b>"
        if detail:
            body += self._telegram_list_html(detail)
        return f"<blockquote><b>{self._html_escape(title)}</b><br>{body}</blockquote>"
