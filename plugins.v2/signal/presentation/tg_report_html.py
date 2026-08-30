"""Telegram report HTML rendering helpers.

Pure classmethod/staticmethod helpers extracted from FusionReportMixin so that
both FusionReportMixin and TgConsoleRenderMixin
share one canonical HTML rendering layer without coupling to each other.
"""
import re
from typing import Any, Dict, List


class TgReportHtmlMixin:
    """Shared Telegram HTML rendering helpers (tables/lists/quotes/status)."""

    @classmethod
    def _telegram_text_html(cls, value: Any) -> str:
        escaped = cls._html_escape(value)
        if len(escaped) <= 16:
            return escaped
        parts = re.split(r"(&(?:#[0-9]+|#x[0-9A-Fa-f]+|[A-Za-z][A-Za-z0-9]+);)", escaped)
        return "".join(cls._telegram_soft_breaks(part) for part in parts)

    @staticmethod
    def _telegram_soft_breaks(text: str, chunk_size: int = 12) -> str:
        if not text:
            return text
        if text.startswith("&") and text.endswith(";"):
            return text
        marker = "\u200b"
        text = re.sub(r"([/_.:@|\-])(?=\S)", lambda match: f"{match.group(1)}{marker}", text)

        def chunk_token(match: re.Match) -> str:
            token = match.group(0)
            return marker.join(token[i:i + chunk_size] for i in range(0, len(token), chunk_size))

        return re.sub(r"[A-Za-z0-9]{13,}", chunk_token, text)

    @classmethod
    def _telegram_section_items(cls, lines: List[str]) -> List[str]:
        items: List[str] = []
        for line in lines or []:
            text = str(line or "").strip()
            if not text:
                continue
            for part in re.split(r"\s*｜\s*(?=•\s*)", text):
                item = re.sub(r"^(?:[•⦁]\s*)+", "", part.strip())
                if item:
                    items.append(item)
        return items

    @classmethod
    def _telegram_overview_table(cls, parts: Dict[str, Any]) -> str:
        sections = {str(s.get("title") or ""): cls._telegram_section_items(s.get("lines") or []) for s in parts.get("sections") or []}
        rows: List[str] = []

        site_items = sections.get("📡 站点状态") or []
        site_total = 0
        for item in site_items:
            match = re.search(r"全部\s*(\d+)\s*个站点正常", item)
            if match:
                site_total = max(site_total, int(match.group(1)))
        if not site_total:
            site_total = len([x for x in site_items if x and "未取到" not in x and x != "无"])
        site_bad = len([x for x in site_items if "异常" in x or "失效" in x or "过期" in x])
        if site_items:
            site_state = f"异常 {site_bad}" if site_bad else "全部正常"
            rows.append(f"站点：{site_total or len(site_items)} 个，{site_state}")

        inc_items = sections.get("📈 站点增量") or []
        if "📈 站点增量" in sections:
            inc_metrics = cls._telegram_increment_metrics(inc_items)
            if inc_metrics["count"]:
                upload_label = str(inc_metrics["upload"])
                download_label = str(inc_metrics["download"])
                rows.append(f"增量：↑ {upload_label} / ↓ {download_label}（{inc_metrics['count']} 站点）")
            else:
                rows.append("增量：无新增")

        download_items = sections.get("📥 今日下载") or []
        if "📥 今日下载" in sections:
            download_count = len([x for x in download_items if x and x != "无"])
            rows.append(f"下载：{download_count} 个完成" if download_count else "下载：无完成")

        health_items = sections.get("🩺 健康巡查") or []
        if "🩺 健康巡查" in sections:
            health_line = next((x for x in health_items if "状态" in x), "")
            health_state = "异常" if ("异常" in health_line and "0 项异常" not in health_line) else ("正常" if health_items else "无记录")
            health_summary = health_line.split("：", 1)[-1] if "：" in health_line else health_state
            rows.append(f"健康：{health_summary}")

        return cls._telegram_quote_html("📌 今日结论", rows, max_items=8) if rows else ""

    @classmethod
    def _telegram_quote_html(cls, title: str, items: List[str], max_items: int = 5) -> str:
        visible = [str(x or "").strip() for x in (items or []) if str(x or "").strip()][:max_items]
        body = "<br>".join(cls._html_escape(item) for item in visible)
        if len(items or []) > max_items:
            body = (body + "<br>" if body else "") + cls._html_escape(f"…另 {len(items) - max_items} 项")
        return f"<blockquote><b>{cls._html_escape(title)}</b><br>{body or '无'}</blockquote>"

    @classmethod
    def _telegram_status_summary(cls, title: str, lines: List[str]) -> str:
        all_items: List[str] = []
        risk_items: List[str] = []
        ok_count = 0
        compressed_ok_count = 0
        for item in cls._telegram_section_items(lines):
            detail = cls._telegram_status_detail_label(item)
            all_items.append(detail)
            if any(key in item for key in ("异常", "失效", "过期")):
                risk_items.append(detail)
            else:
                match = re.search(r"全部\s*(\d+)\s*个站点正常", item)
                if match:
                    compressed_ok_count = max(compressed_ok_count, int(match.group(1)))
                ok_count += 1

        if risk_items:
            alert_items = risk_items[:3]
            if len(risk_items) > 3:
                alert_items.append(f"另 {len(risk_items) - 3} 项异常在明细中")
            headline = cls._telegram_quote_html("🚨 站点风险", alert_items, max_items=4)
            detail_title = title
        else:
            count = compressed_ok_count or ok_count or len(all_items)
            headline = ""
            detail_title = f"{title}（{count} 个正常）"
        detail_items = cls._telegram_expand_compressed_site_items(all_items)
        return headline + cls._telegram_details_html(detail_title, cls._telegram_list_html(detail_items))

    @staticmethod
    def _telegram_status_label(item: str) -> str:
        clean = re.sub(r"^\s*[✅⚠️⚠]\s*", "", str(item or "").strip())
        clean = re.sub(r"：\s*[✅⚠️⚠]\s*", "：", clean)
        return clean.replace(" | ", "：", 1)

    @classmethod
    def _telegram_status_detail_label(cls, item: str) -> str:
        clean = cls._telegram_status_label(item)
        if any(key in clean for key in ("异常", "失效")):
            return f"⚠️ {clean}"
        if "过期" in clean:
            return f"⏳ {clean}"
        if "正常" in clean:
            return f"✅ {clean}"
        return clean

    @classmethod
    def _telegram_expand_compressed_site_items(cls, items: List[str]) -> List[str]:
        if not items or not any(re.search(r"全部\s*\d+\s*个站点正常", str(item or "")) for item in items):
            return items
        try:
            from app.db.site_oper import SiteOper
            site_oper = SiteOper()
            from ..domain.site_helpers import normalize_site_domain, select_latest_site_userdata_rows, select_user_data_sites
            active_domains = {
                normalize_site_domain(getattr(site, "domain", ""))
                for site in select_user_data_sites(site_oper.list_active() or [])
                if normalize_site_domain(getattr(site, "domain", ""))
            }
            rows = site_oper.get_userdata() if callable(getattr(site_oper, "get_userdata", None)) else site_oper.get_userdata_latest()
            latest = select_latest_site_userdata_rows(rows, active_domains)
            today = cls._today_prefix()
            detail_items: List[str] = []
            for row in latest:
                name = getattr(row, "name", None) or getattr(row, "domain", None) or "未知站点"
                err = str(getattr(row, "err_msg", None) or "").strip()
                day = cls._normalize_day(getattr(row, "updated_day", None))
                if err:
                    detail_items.append(f"⚠️ {name}：异常（{err[:30]}）")
                elif day == today:
                    detail_items.append(f"✅ {name}：正常")
                else:
                    detail_items.append(f"⏳ {name}：数据过期")
            return detail_items or items
        except Exception:
            return items

    @classmethod
    def _telegram_details_html(cls, title: str, body: str) -> str:
        return f"<details><summary>{cls._html_escape(title)}</summary>{body or '<p>无</p>'}</details>"

    @classmethod
    def _telegram_list_html(cls, items: List[str]) -> str:
        if not items:
            return "<p>无</p>"
        return "<ul>" + "".join(f"<li>{cls._telegram_text_html(item)}</li>" for item in items) + "</ul>"

    @classmethod
    def _telegram_compact_lines_html(cls, items: List[str]) -> str:
        visible = [str(x or "").strip() for x in (items or []) if str(x or "").strip()]
        return "<br>".join(cls._telegram_text_html(item) for item in visible) if visible else "无"

    @classmethod
    def _telegram_general_list_html(cls, title: str, items: List[str]) -> str:
        normalized: List[str] = []
        for item in items or []:
            text = str(item or "").strip()
            if text in {"无", "暂无", "暂无记录"}:
                normalized.append("📭 无")
            elif text:
                normalized.append(text)
        return cls._telegram_list_html(normalized)

    @classmethod
    def _telegram_health_list_html(cls, items: List[str]) -> str:
        enriched: List[str] = []
        for item in items or []:
            text = str(item or "").strip()
            if text.startswith("状态："):
                icon = "✅" if "全部正常" in text or "异常 0" in text else "⚠️"
                enriched.append(f"{icon} {text}")
            elif text.startswith("巡查项："):
                enriched.append(f"🩺 {text}")
            elif text.startswith("正常项："):
                enriched.append(f"✅ {text}")
            elif "异常" in text or "失败" in text:
                enriched.append(f"⚠️ {text}")
            elif text:
                enriched.append(text)
        return cls._telegram_list_html(enriched)

    @classmethod
    def _telegram_mobile_rows_html(cls, title: str, rows: List[List[Any]]) -> str:
        heading = f"<h3>{cls._html_escape(title)}</h3>" if str(title or "").strip() else ""
        items: List[str] = []
        for row in rows or []:
            cells = [str(cell or "").strip() for cell in row if str(cell or "").strip()]
            if not cells:
                continue
            label = cells[0]
            details = cells[1:]
            detail_html = "".join(f"<br>{cls._telegram_text_html(detail)}" for detail in details)
            items.append(f"<li><b>{cls._telegram_text_html(label)}</b>{detail_html}</li>")
        if not items:
            return f"{heading}<p>无</p>"
        return f"{heading}<ul>{''.join(items)}</ul>"

    @classmethod
    def _telegram_table_html(cls, title: str, headers: List[str], rows: List[List[Any]]) -> str:
        heading = f"<h3>{cls._html_escape(title)}</h3>" if str(title or "").strip() else ""
        if not rows:
            return f"{heading}<p>无</p>"
        head = "".join(f"<th>{cls._html_escape(h)}</th>" for h in headers)
        body = []
        for row in rows:
            cells = list(row)[:len(headers)]
            cells.extend([""] * max(0, len(headers) - len(cells)))
            body.append("<tr>" + "".join(f"<td>{cls._telegram_text_html(cell)}</td>" for cell in cells) + "</tr>")
        return f"{heading}<table><thead><tr>{head}</tr></thead><tbody>{''.join(body)}</tbody></table>"

    @classmethod
    def _telegram_status_table(cls, title: str, lines: List[str]) -> str:
        rows = []
        for item in cls._telegram_section_items(lines):
            match = re.match(r"(.+?)：(.+)$", item)
            rows.append([match.group(1).strip(), match.group(2).strip()] if match else [item, ""])
        return cls._telegram_table_html(title, ["站点", "状态"], rows)

    @classmethod
    def _telegram_increment_table(cls, title: str, lines: List[str]) -> str:
        rows = []
        notes = []
        for item in cls._telegram_section_items(lines):
            if "基线不足" in item or item in {"无", "暂无增量"}:
                notes.append(item)
                continue
            name, rest = (item.split("：", 1) + [""])[:2] if "：" in item else (item, "")
            upload = cls._match_text(r"⬆\s*([^｜]+)", rest)
            download = cls._match_text(r"⬇\s*([^｜]+)", rest)
            ratio = cls._match_text(r"📊\s*([^｜]+)", rest)
            bonus = cls._match_text(r"🪙\s*([^｜]+)", rest)
            metric = f"分享 {ratio}" if ratio else "分享 -"
            if bonus:
                metric = f"{metric} / 魔力 {bonus}"
            rows.append([f"📈 {name.strip()}", f"流量：↑ {upload or '-'} / ↓ {download or '-'}", f"指标：{metric}"])
        table = cls._telegram_mobile_rows_html(title, rows)
        if notes and not rows:
            heading = f"<h3>{cls._html_escape(title)}</h3>" if str(title or "").strip() else ""
            return f"{heading}{cls._telegram_list_html(notes)}"
        if notes:
            return table + cls._telegram_list_html(notes)
        return table

    @classmethod
    def _telegram_increment_metrics(cls, items: List[str]) -> Dict[str, Any]:
        count = 0
        upload_total = 0
        download_total = 0
        for item in items or []:
            if "基线不足" in item or item in {"无", "暂无增量"}:
                continue
            rest = item.split("：", 1)[1] if "：" in item else item
            upload = cls._match_text(r"⬆\s*([^｜]+)", rest)
            download = cls._match_text(r"⬇\s*([^｜]+)", rest)
            upload_total += cls._telegram_size_to_bytes(upload)
            download_total += cls._telegram_size_to_bytes(download)
            count += 1
        return {
            "count": count,
            "upload": cls._format_bytes(upload_total) if upload_total else "0 B",
            "download": cls._format_bytes(download_total) if download_total else "0 B",
        }

    @staticmethod
    def _telegram_size_to_bytes(value: Any) -> int:
        match = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*([KMGTPE]?B)", str(value or ""), re.I)
        if not match:
            return 0
        number = float(match.group(1))
        units = ["B", "KB", "MB", "GB", "TB", "PB", "EB"]
        unit = match.group(2).upper()
        power = units.index(unit) if unit in units else 0
        return int(number * (1024 ** power))

    @classmethod
    def _telegram_storage_table(cls, title: str, lines: List[str]) -> str:
        rows = []
        for item in cls._telegram_section_items(lines):
            if "：" not in item:
                rows.append([item, "", ""])
                continue
            name, rest = item.split("：", 1)
            fields = [part.strip() for part in rest.split("｜") if part.strip()]
            usage = next((part for part in fields if "💽" in part), fields[0] if fields else "")
            status = next((part for part in fields if "已用" in part), "")
            rows.append([f"💾 {name.strip()}", f"容量：{usage}" if usage else "", f"状态：{status}" if status else ""])
        return cls._telegram_mobile_rows_html(title, rows)

    @classmethod
    def _telegram_media_table(cls, title: str, lines: List[str]) -> str:
        rows = []
        icons = {"电影": "🎬", "电视剧": "📺", "剧集": "🎞", "用户": "👤"}
        for item in cls._telegram_section_items(lines):
            for label, value in re.findall(r"(电影|电视剧|剧集|用户)\s+(\d+)", item):
                rows.append([f"{icons.get(label, '•')} {label}", f"数量：{value}"])
        return cls._telegram_mobile_rows_html(title, rows)
