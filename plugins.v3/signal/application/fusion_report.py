import json
import re
from datetime import datetime
from typing import Any, Dict, List, Tuple

from app.sdk.config import settings
from app.sdk.logging import logger
from ..domain import html_utils


class FusionReportMixin:
    """Fusion card data aggregation, refresh orchestration, and Telegram transport helpers.

    V3 migration notes:
    - TransferHistoryQuery via app.sdk.queries: gets DTO, not ORM rows. No
      paging params in the query service itself, so large result sets get
      truncated at the internal default (50). Helper _query_transfer_history
      adds explicit paging to reach the enforced cap (200).
    - Subscription calendar via app.sdk.queries: SubscriptionCalendar returns
      List[SubscriptionDTO] with normalized identity. The legacy
      _normalize_subscription_calendar step now operates on already-normalized
      DTOs, keeping it idempotent but no longer strictly necessary.
    - Site data read: app.sdk.queries.query_site_data() returns SiteDataDTO
      with .site (SiteConfigDTO) nested, replacing direct SiteOper calls.
    - Error propagation: refresh_result.get("success") is False means upstream
      failure; the entire refresh aborts rather than rendering with stale data.
    """

    def run_fusion_card_create(self) -> bool:
        """Create or roll the Fusion card on its configured schedule."""
        ok, _ = self._runtime_gate("scheduler", component="fusion_notify", name="FusionCardCreate")
        if not ok:
            return False
        result = self.api_create_tg_console_card(trigger="scheduled")
        return int(result.get("code", 1)) == 0

    def run_fusion_card_refresh(self) -> bool:
        """Refresh the current Fusion card; never falls back to a second delivery route."""
        with self._subscription_calendar_read_scope():
            return self._run_fusion_card_refresh_scoped()

    def _run_fusion_card_refresh_scoped(self) -> bool:
        name = "融合卡刷新"
        ok, _ = self._guard_task(name, "fusion_notify")
        if not ok:
            return False
        try:
            refresh_result = self._refresh_fusion_report_live_data()
            if refresh_result.get("success") is False:
                error = str(refresh_result.get("message") or refresh_result.get("error") or "站点数据刷新失败，融合卡刷新已取消")
                self._save_task_result(name, False, 1, error)
                self._save_fusion_report_result(updated=False, success=False, text="", error=error, message=error, returncode=1)
                return False
            text = self._build_fusion_report_message()
            calendar_snapshot = self._subscription_calendar_snapshot_for_scope()
            calendar_partial = calendar_snapshot is not None and calendar_snapshot.is_partial
            calendar_error = calendar_snapshot.failure_message() if calendar_partial else ""
            if self._fusion_notify_enabled:
                refresh_ok = self._refresh_fusion_card(text, refresh_result)
                if calendar_partial:
                    self._notify_fusion_task_outcome(
                        mtype=self._notification_type("Plugin"),
                        title="Signal - 融合卡订阅日历部分失败",
                        text=calendar_error,
                        outcome=calendar_error,
                        success=False,
                        component="fusion_notify",
                        affected_owner="persistent-subscriptions",
                        task_key="fusion_card_refresh",
                        task_group="融合通知",
                            notification_status="error",
                            notification_target="fusion_subscription_calendar",
                            notification_fingerprint=self._notification_outcome_fingerprint({
                                "status": calendar_snapshot.status,
                                "failed_subscriptions": calendar_snapshot.failed_subscriptions,
                                "errors": self._subscription_calendar_error_fingerprint_values(calendar_snapshot.errors),
                            }),
                        notification_cooldown=True,
                    )
                    self._save_task_result(name, False, 1, calendar_error if refresh_ok else (self._tg_console_last_error or calendar_error))
                    self._save_fusion_report_result(updated=refresh_ok, success=False, text=text, error=calendar_error, message=calendar_error, returncode=1)
                    return False
                if refresh_ok:
                    self._save_task_result(name, True, 0, "OK tg_console_card")
                    self._save_fusion_report_result(updated=True, success=True, text=text, error="", message="OK tg_console_card", returncode=0)
                    return True
                error = self._tg_console_last_error or "Telegram 融合汇报卡更新失败"
                self._save_task_result(name, False, 1, error)
                self._save_fusion_report_result(updated=False, success=False, text=text, error=error, message=error, returncode=1)
                return False
            error = "融合通知未启用，禁止使用独立发送回退"
            self._save_task_result(name, False, 1, error)
            self._save_fusion_report_result(updated=False, success=False, text=text, error=error, message=error, returncode=1)
            return False
        except Exception as err:
            self._save_task_result(name, False, -1, str(err))
            self._save_fusion_report_result(updated=False, success=False, text="", error=str(err), message=str(err), returncode=-1)
            try:
                from ..infrastructure.subscription_calendar import SubscriptionCalendarError
                if isinstance(err, SubscriptionCalendarError):
                    self._notify_fusion_task_outcome(
                        mtype=self._notification_type("Plugin"),
                        title="Signal - 融合卡订阅日历异常",
                        text=f"融合卡读取订阅日历失败：{err}",
                        outcome=f"融合卡读取订阅日历失败：{str(err)[:120]}",
                        success=False,
                        component="fusion_notify",
                        affected_owner="persistent-subscriptions",
                        task_key="fusion_card_refresh",
                        task_group="融合通知",
                        notification_status="error",
                        notification_target="fusion_subscription_calendar",
                        notification_fingerprint=self._notification_error_fingerprint(err),
                        notification_cooldown=True,
                    )
            except Exception as notify_err:
                logger.warning(f"Signal 融合卡订阅日历失败通知发送异常：{notify_err}")
            logger.error(f"Signal 融合卡刷新失败：{err}")
            return False

    def _refresh_fusion_report_live_data(self) -> Dict[str, Any]:
        """Refresh the live data consumed by the Fusion card."""
        result: Dict[str, Any] = {"success": True}
        try:
            needs_site_data = self._report_site_status or self._report_site_increment or self._report_summary
            if needs_site_data:
                refresh = self._refresh_site_userdata_coordinated()
                active_count = int(refresh.get("active_count") or 0)
                if not refresh.get("success"):
                    message = str(refresh.get("message") or "站点数据刷新失败，融合卡刷新已取消以避免使用旧快照")
                    logger.warning(f"Signal {message}")
                    self._save_task_result("站点数据统计", False, 1, message)
                    return {"site_userdata": refresh.get("status") or "error", "success": False, "message": message, "active_count": active_count}
                # count 只表示"站点返回了数据"，其中可能包含带 err_msg 的故障站点。
                # 融合卡文案必须用真正健康的 ok_count，并逐站列出被排除的站点，
                # 否则 7 个站点里 1 个未登录时仍会写成"已刷新 7 个站点用户数据"。
                count = int(refresh.get("count") or 0)
                states = self._merge_site_states([], refresh.get("sites"))
                faults = self._site_state_faults(states)
                ok_count = int(refresh.get("ok_count") or 0)
                excluded_lines = self._format_site_state_lines(states, suffix="未计入本次刷新")
                if ok_count:
                    headline = (
                        f"已刷新 {ok_count}/{active_count} 个站点用户数据"
                        if active_count and ok_count != active_count
                        else f"已刷新 {ok_count} 个站点用户数据"
                    )
                else:
                    headline = "已触发站点用户数据刷新，未返回可用数据"
                message = "\n".join([headline, *excluded_lines]) if excluded_lines else headline
                refresh_success = bool(ok_count) or active_count == 0
                self._save_task_result("站点数据统计", refresh_success, 0 if refresh_success else 1, message)
                result.update({
                    "site_userdata": "ok" if ok_count == active_count else ("partial" if ok_count else "empty"),
                    "count": count,
                    "ok_count": ok_count,
                    "active_count": active_count,
                    "site_states": states,
                    "fault_count": len(faults),
                    "message": message,
                })
            else:
                result["site_userdata"] = "skipped"

            if self._report_health and self._health_check_enabled:
                result["health_summary"] = self._build_health_summary(persist=True)
                result["health_check"] = "ok"
            else:
                result["health_check"] = "skipped"

            return result
        except Exception as err:
            message = f"融合卡实时数据刷新失败：{err}"
            logger.warning(f"Signal {message}")
            self._save_task_result("融合卡实时刷新", False, 1, message)
            return {"site_userdata": "error", "success": False, "error": str(err), "message": message}

    def _save_fusion_report_result(self, updated: bool, success: bool, text: str = "", error: str = "", message: str = "", returncode: int = 0):
        snapshot = self._subscription_calendar_snapshot_for_scope()
        self.save_data("last_fusion_report", {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "template": "fusion-report-v1",
            "updated": bool(updated),
            "success": bool(success),
            "returncode": int(returncode),
            "chars": len(text or ""),
            "sections": self._count_fusion_report_sections(text or ""),
            "text": (text or "")[:2000],
            "message": (message or "")[:1000],
            "error": (error or "")[:1000],
            "calendar_status": str(getattr(snapshot, "status", "") or ""),
            "calendar_errors": list(getattr(snapshot, "errors", ()) or ())[:3],
    })

    @staticmethod
    def _count_fusion_report_sections(text: str) -> int:
        icons = ["🕒", "🤖", "📡", "📈", "⬇️", "📥", "📦", "📺", "💾", "🎬", "🩺", "✅", "⚠️"]
        return sum(1 for icon in icons if icon in (text or ""))

    def _build_fusion_report_message(self, preview: bool = False) -> str:
        return self._build_fusion_report_content(preview=preview)

    def _resolve_fusion_telegram_config(self) -> Tuple[str, str, str]:
        global_token, global_chat_id, name = self._find_moviepilot_telegram_config(self._fusion_notify_msgtype)
        if global_token and global_chat_id:
            return global_token, global_chat_id, f"复用 MoviePilot 通知渠道：{name or 'Telegram'}"
        return "", "", ""

    @staticmethod
    def _dict_or_attr(value: Any, key: str, default: Any = None) -> Any:
        if isinstance(value, dict):
            return value.get(key, default)
        return getattr(value, key, default)

    def _find_moviepilot_telegram_config(self, msgtype: str = "") -> Tuple[str, str, str]:
        try:
            from app.db.oper.systemconfig import SystemConfigOper
            from app.schemas.types import SystemConfigKey
            notifications = SystemConfigOper().get(SystemConfigKey.Notifications) or []
        except Exception as err:
            logger.warning(f"Signal 读取 MoviePilot Telegram 通知配置失败：{err}")
            return "", "", ""

        preferred_switches = self._notification_switch_labels(msgtype or "Plugin")
        candidates: List[Tuple[int, str, str, str]] = []
        for item in notifications or []:
            ntype = str(self._dict_or_attr(item, "type", "") or "").strip().lower()
            if ntype != "telegram":
                continue
            enabled = self._dict_or_attr(item, "enabled", True)
            if enabled is False or str(enabled).strip().lower() in {"false", "0", "no", "off"}:
                continue
            config = self._dict_or_attr(item, "config", {}) or {}
            token = str(self._dict_or_attr(config, "TELEGRAM_TOKEN", "") or "").strip()
            chat_id = str(self._dict_or_attr(config, "TELEGRAM_CHAT_ID", "") or "").strip()
            if not token or not chat_id:
                continue
            switches = self._parse_csv(self._dict_or_attr(item, "switchs", []) or [])
            score = 1
            if preferred_switches and any(str(x) in preferred_switches for x in switches):
                score += 100
            if any(x in switches for x in ("插件", "Plugin")):
                score += 20
            if any(x in switches for x in ("其它", "其他", "Other")):
                score += 5
            name = str(self._dict_or_attr(item, "name", "") or "Telegram").strip()
            candidates.append((score, token, chat_id, name))

        if not candidates:
            return "", "", ""
        candidates.sort(key=lambda x: x[0], reverse=True)
        _, token, chat_id, name = candidates[0]
        return token, chat_id, name

    @classmethod
    def _notification_switch_labels(cls, value: Any) -> set:
        item = cls._notification_type(value, "Plugin")
        name = str(getattr(item, "name", "") or value or "").strip()
        raw_value = str(getattr(item, "value", "") or value or "").strip()
        labels = {x for x in (name, raw_value, str(value or "").strip()) if x}
        cn_labels = {
            "Download": ("下载", "资源下载"),
            "Organize": ("整理", "整理入库"),
            "Subscribe": ("订阅",),
            "SiteMessage": ("站点", "站点消息"),
            "MediaServer": ("媒体服务器",),
            "Manual": ("手动", "手动处理"),
            "Plugin": ("插件",),
            "Agent": ("智能体",),
            "Other": ("其他", "其它"),
        }
        labels.update(cn_labels.get(name, ()))
        labels.update(cn_labels.get(raw_value, ()))
        return labels

    @staticmethod
    def _telegram_http_post_json(url: str, payload: Dict[str, Any], timeout: int = 15) -> Any:
        proxies = getattr(settings, "PROXY", None) or None
        try:
            import requests
            return requests.post(url, json=payload, timeout=timeout, proxies=proxies)
        except ImportError:
            import urllib.error
            import urllib.request

            body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            req = urllib.request.Request(url, data=body, method="POST", headers={"Content-Type": "application/json"})
            opener = urllib.request.build_opener(urllib.request.ProxyHandler(proxies)) if proxies else None
            try:
                if opener:
                    resp_ctx = opener.open(req, timeout=timeout)
                else:
                    resp_ctx = urllib.request.urlopen(req, timeout=timeout)
                with resp_ctx as resp:
                    status = resp.status
                    text = resp.read().decode("utf-8", errors="replace")
            except urllib.error.HTTPError as err:
                status = err.code
                text = err.read().decode("utf-8", errors="replace")

            class _Response:
                def __init__(self, status_code: int, response_text: str):
                    self.ok = 200 <= status_code < 300
                    self.status_code = status_code
                    self.text = response_text

                def json(self):
                    return json.loads(self.text)

            return _Response(status, text)

    @staticmethod
    def _telegram_safe_error(value: Any, limit: int = 200) -> str:
        text = str(value or "")
        text = re.sub(r"bot\d{5,}:[A-Za-z0-9_-]+", "bot***", text)
        text = re.sub(r"\d{5,}:[A-Za-z0-9_-]{20,}", "***TOKEN***", text)
        if limit and len(text) > limit:
            return text[:limit]
        return text

    def _telegram_response_data(self, response: Any, action: str) -> Tuple[bool, Dict[str, Any]]:
        if not getattr(response, "ok", False):
            self._tg_console_last_error = f"Telegram {action} HTTP {getattr(response, 'status_code', '')}：{self._telegram_safe_error(getattr(response, 'text', ''), limit=200)}"
            logger.warning(f"Signal {self._tg_console_last_error}")
            return False, {}
        try:
            data = response.json()
        except Exception:
            self._tg_console_last_error = f"Telegram {action} 返回非 JSON：{self._telegram_safe_error(getattr(response, 'text', ''), limit=200)}"
            logger.warning(f"Signal {self._tg_console_last_error}")
            return False, {}
        if isinstance(data, dict) and data.get("ok") is True:
            return True, data
        description = (data or {}).get("description") if isinstance(data, dict) else data
        self._tg_console_last_error = f"Telegram {action} 返回失败：{self._telegram_safe_error(description, limit=200)}"
        logger.warning(f"Signal {self._tg_console_last_error}")
        return False, data if isinstance(data, dict) else {}

    @staticmethod
    def _split_fusion_report_text(text: str) -> Dict[str, Any]:
        return html_utils.split_fusion_report_text(text)

    def _build_fusion_report_content(self, preview: bool = False) -> str:
        site_increment = self._get_site_increment_locked()
        site_health = self._get_site_health_locked()
        transfer_health = self._get_transfer_health_locked()
        subs = self._get_today_subscribe_updates_locked()
        downloader_health = self._get_downloader_health_locked()
        storage_health = self._get_storage_health_locked()
        today_downloads = self._get_today_downloads_locked()
        media_stats = self._get_media_stats_locked()

        lines = [
            self._fusion_report_title(),
            self._fusion_greeting_locked(),
            "",
            f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        ]

        def section(enabled: bool, header: str, body: List[str]):
            if enabled and body:
                lines.extend(["", header, ""])
                lines.extend(self._report_body_lines(body))

        if self._report_version:
            lines.extend(["", "🤖 MoviePilot", ""])
            lines.extend(self._report_body_lines(self._version_report_lines()))
        section(self._report_site_status, "📡 站点状态", site_health)
        section(self._report_site_increment, "📈 站点增量", site_increment)
        # 「下载器/正在下载」与「今日下载」重复，统一只保留今日下载
        section(self._report_today_download, "📥 今日下载", today_downloads)
        section(self._report_transfer, "📦 入库整理", transfer_health)
        section(self._report_subscribe, "📺 订阅追新", ([f"⦁ {x}" for x in subs] if subs else ["⦁ 无"]))
        section(self._report_storage, "💾 存储空间", storage_health)
        section(self._report_media_stat, "🎬 媒体统计", media_stats)
        section(self._report_health and self._health_check_enabled, "🩺 健康巡查", self._get_health_report_locked(persist_missing=not preview))
        if self._report_summary:
            summary = self._get_summary_locked(site_health, transfer_health, downloader_health, storage_health)
            if summary:
                header = "🧾 融合摘要"
                first = str(summary[0] or "").strip()
                if first.startswith("⚠"):
                    header = "⚠️ 融合提醒"
                    summary = summary[1:]
                elif "融合摘要" in first:
                    summary = summary[1:]
                lines.extend(["", header, ""])
                lines.extend(self._report_body_lines(summary or ["⦁ 系统正常"]))
        return "\n".join(lines)

    @staticmethod
    def _fusion_report_title() -> str:
        weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        now = datetime.now()
        return f"📮 MP 融合汇报｜{now.strftime('%Y-%m-%d')} {weekdays[now.weekday()]}"

    @classmethod
    def _report_body_lines(cls, items: List[str]) -> List[str]:
        """将融合内容转成图标化数据条；短项横向排布，长项保留纵向。"""
        cleaned = [cls._report_visual_line(item) for item in (items or []) if str(item or "").strip()]
        cleaned = [line for line in cleaned if line]
        if not cleaned:
            return ["• 无"]
        compact: List[str] = []
        run: List[str] = []

        def flush_run():
            nonlocal run
            if run:
                compact.extend(cls._pack_report_pairs(run))
                run = []

        for text in cleaned:
            if len(text) <= 22:
                run.append(text)
            else:
                flush_run()
                compact.append(text)
        flush_run()
        return compact

    @classmethod
    def _pack_report_pairs(cls, items: List[str]) -> List[str]:
        pairs = [items[i:i + 2] for i in range(0, len(items), 2)]
        left_width = max((cls._display_width(pair[0]) for pair in pairs if len(pair) == 2), default=0)
        rows = []
        for pair in pairs:
            if len(pair) == 1:
                rows.append(pair[0])
            else:
                rows.append(f"{cls._pad_display(pair[0], left_width)} ｜ {pair[1]}")
        return rows

    @staticmethod
    def _report_visual_line(item: Any) -> str:
        text = str(item or "").strip()
        if text.startswith("- "):
            text = f"⦁ {text[2:].strip()}"
        if text.startswith("  - "):
            text = f"⦁ {text[4:].strip()}"
        text = text.replace("⦁ ", "• ").replace("⦁", "•").strip()
        body = text[2:].strip() if text.startswith("• ") else text

        version_match = re.match(r"当前版本：前端\s*(.*?)\s*/\s*后端\s*(.*)$", body)
        if version_match:
            return f"• 🖥 前端 {version_match.group(1)} ｜ ⚙ 后端 {version_match.group(2)}"

        if body.startswith("最新版本："):
            latest = body.replace("最新版本：", "", 1).strip()
            icon = "✅" if "已是最新" in latest else ("🆕" if "新版" in latest else "⚠")
            return f"• {icon} 最新 {latest}"

        status_match = re.match(r"(.+?)\s*\|\s*(.+)$", body)
        if status_match:
            name, status = status_match.group(1).strip(), status_match.group(2).strip()
            icon = "✅" if status == "正常" else ("⏳" if "过期" in status else "⚠")
            return f"• {name}：{icon} {status}"

        transfer_match = re.match(r"今日成功：(\d+)｜失败：(\d+)", body)
        if transfer_match:
            return f"• ✅ 成功 {transfer_match.group(1)} ｜ ❌ 失败 {transfer_match.group(2)}"

        if body.startswith("失败："):
            detail = body.replace("失败：", "", 1)
            if " - " in detail:
                title, reason = detail.split(" - ", 1)
                return f"• ❌ {title.strip()} ｜ {reason.strip()}"
            return f"• ❌ {detail.strip()}"

        if body.startswith("异常："):
            detail = body.replace("异常：", "", 1).strip()
            return f"• ⚠ {detail}"

        if body.startswith("今日下载："):
            value = body.replace("今日下载：", "", 1).strip()
            return "• 无" if value == "无" else f"• 📦 {value}"

        seed_match = re.match(r"(.+?)（做种：(.*?)）$", body)
        if seed_match:
            label, seed = seed_match.group(1).strip(), seed_match.group(2).strip()
            icon = "📺" if re.search(r"S\d{1,2}E", label, re.I) else "🎬"
            return f"• {icon} {label} ｜ 🌱 {seed}"

        if re.search(r"S\d{1,2}(?:E\d{1,4}|E\d{1,4}-E\d{1,4}|$)", body, re.I):
            return f"• 📺 {body}"

        if re.search(r"\(\d{4}\)", body):
            return f"• 🎬 {body}"

        if re.search(r"电影\s+\d+", body) and ("电视剧" in body or "剧集" in body or "用户" in body):
            parts = []
            for part in re.split(r"\s*｜\s*", body):
                part = part.strip()
                if part.startswith("电影 "):
                    parts.append("🎞 " + part)
                elif part.startswith("电视剧 "):
                    parts.append("📺 " + part)
                elif part.startswith("剧集 "):
                    parts.append("🎞 " + part)
                elif part.startswith("用户 "):
                    parts.append("👤 " + part)
                elif part:
                    parts.append(part)
            return f"• {' ｜ '.join(parts)}"

        storage_match = re.match(r"(.+?)：(.+)$", body)
        if storage_match and ("剩余" in body or "已用" in body):
            name, rest = storage_match.group(1).strip(), storage_match.group(2).strip()
            parts = []
            for part in re.split(r"\s*｜\s*", rest):
                part = part.strip()
                if not part:
                    continue
                plain = re.sub(r"^[🔴🟠🟡🟢]\s*", "", part)
                if part.startswith("剩余"):
                    continue
                if part.startswith("💽"):
                    parts.append(part)
                elif plain.startswith("已用"):
                    pct_match = re.search(r"(\d+)", part)
                    pct = int(pct_match.group(1)) if pct_match else 0
                    icon = "🔴" if pct >= 85 else ("🟠" if pct >= 70 else "🟢")
                    parts.append(f"{icon} {plain}")
                else:
                    parts.append(f"💽 {part}")
            return f"• {name}：{' ｜ '.join(parts)}"

        return text if text.startswith("• ") else f"• {body}"

    def _version_report_lines(self) -> List[str]:
        """当前/最新版本 + 按检查结果区分话术（已是最新 / 有新版 / 检查失败）。"""
        local = self._get_local_versions()
        fe = local.get("frontend_version") or "未知"
        be = local.get("backend_version") or "未知"
        lines = [f"⦁ 当前版本：前端 {fe} / 后端 {be}"]
        try:
            check = self._check_one_release("后端", "https://api.github.com/repos/jxxghp/MoviePilot/releases", be)
        except Exception as err:
            check = {"error": str(err)}
        latest = check.get("latest_version") or ""
        err = check.get("error") or ""
        if err or not latest:
            lines.append(f"⦁ 最新版本：暂时查不到（{err or '无响应'}），稍后再看")
        elif check.get("has_update"):
            lines.append(f"⦁ 最新版本：后端 {latest} —— 有新版，{self._fusion_report_greeting}记得抽空更新")
        else:
            lines.append(f"⦁ 最新版本：{latest}，已是最新 ✅")
        return lines

    def _build_today_transfer_report_text(self) -> str:
        success_items = [str(x or "").strip() for x in self._get_today_downloads_locked() if str(x or "").strip()]
        failed_items = [str(x or "").strip() for x in self._get_transfer_failures_locked() if str(x or "").strip()]
        success_items = [x for x in success_items if x not in {"⦁ 无", "• 无", "无"}]
        failed_items = [x for x in failed_items if x not in {"⦁ 无", "• 无", "无"}]
        lines: List[str] = []
        if success_items:
            lines.append(f"✅ 成功入库 {len(success_items)} 项")
            lines.extend(success_items[:20])
        if failed_items:
            lines.append(f"⚠️ 入库异常 {len(failed_items)} 项")
            lines.extend(failed_items[:20])
        return "\n".join(lines or ["⦁ 无"])

    def _today_transfer_rows_locked(self) -> List[Any]:
        """读取当日整理记录。

        读取失败时记录日志再降级为空列表：静默吞错会把"读不到"渲染成"今天没有入库"，
        两者对用户含义完全不同。
        """
        from ..infrastructure.host_queries import list_transfer_history_for_date_prefix

        try:
            return list_transfer_history_for_date_prefix(self._today_prefix())
        except Exception as err:
            logger.warning(f"Signal 当日整理记录读取失败，本次汇报按空列表处理：{err}")
            return []

    def _get_transfer_failures_locked(self) -> List[str]:
        rows = self._today_transfer_rows_locked()
        failed_rows = [r for r in rows if not getattr(r, "status", False)]
        if not failed_rows:
            return ["⦁ 无"]
        items = []
        for r in failed_rows:
            title = getattr(r, "title", None) or "未命名"
            errmsg = str(getattr(r, "errmsg", None) or getattr(r, "message", None) or "").strip()
            items.append(f"⦁ 失败：{title} - {errmsg[:36]}" if errmsg else f"⦁ 失败：{title}")
        return items

    def _fusion_greeting_locked(self) -> str:
        hour = datetime.now().hour
        if 0 <= hour <= 5:
            part = "凌晨"
        elif 6 <= hour <= 11:
            part = "早上"
        elif 12 <= hour <= 17:
            part = "下午"
        else:
            part = "晚上"
        who = (self._fusion_report_greeting or "少爷").strip() or "少爷"
        return f"{who}，{part}好。当前融合状态已更新。"

    def _get_media_stats_locked(self) -> List[str]:
        """媒体统计（电影/电视剧/剧集/用户）——尝试媒体服务器统计接口，取不到则提示。"""
        try:
            # MoviePilot 官方仪表盘同款：app.chain.dashboard.DashboardChain.media_statistic()
            from app.chain.dashboard import DashboardChain
            stats = DashboardChain().media_statistic() or []
            if not stats:
                return ["⦁ 未取到（媒体服务器未配置）"]
            stat = {
                "movie_count": sum(int(getattr(s, "movie_count", 0) or 0) for s in stats),
                "tv_count": sum(int(getattr(s, "tv_count", 0) or 0) for s in stats),
                "episode_count": sum(int(getattr(s, "episode_count", 0) or 0) for s in stats),
                "user_count": sum(int(getattr(s, "user_count", 0) or 0) for s in stats),
            }

            def _g(obj, *keys):
                for k in keys:
                    v = obj.get(k) if isinstance(obj, dict) else getattr(obj, k, None)
                    if v is not None:
                        return v
                return None

            movie = _g(stat, "movie_count", "MovieCount", "movies", "movie")
            tv = _g(stat, "tv_count", "SeriesCount", "series", "tvs", "tv")
            ep = _g(stat, "episode_count", "EpisodeCount", "episodes", "episode")
            user = _g(stat, "user_count", "UserCount", "users", "user")
            parts = []
            if movie is not None:
                parts.append(f"电影 {movie}")
            if tv is not None:
                parts.append(f"电视剧 {tv}")
            if ep is not None:
                parts.append(f"剧集 {ep}")
            if user is not None:
                parts.append(f"用户 {user}")
            return [f"⦁ {' ｜ '.join(parts)}"] if parts else ["⦁ 未取到"]
        except Exception as e:
            return [f"⦁ 媒体统计异常：{e}"]

    def _get_summary_locked(self, site_health: List[str], transfer_health: List[str], downloads: List[str], storage_health: List[str]) -> List[str]:
        warnings = []
        for line in site_health + transfer_health + downloads + storage_health:
            clean = str(line or "")
            risky = (
                "未取到" in clean
                or "空间偏紧" in clean
                or ("失败：" in clean and "失败：0" not in clean)
                or ("异常" in clean and "异常 0" not in clean)
                or ("过期" in clean and "过期 0" not in clean)
            )
            if risky:
                warnings.append(clean.replace("⦁ ", "⦁ "))
        if warnings:
            return ["⚠️ 融合提醒"] + warnings[:5]
        return ["✅ 融合摘要", "⦁ 系统正常", "⦁ 站点快照正常", "⦁ 无失败转移", "⦁ 下载器无异常"]

    def _get_today_subscribe_updates_locked(self) -> List[str]:
        """读取 MoviePilot v2 官方复合日历快照，失败不得转为空结果。"""
        return self._read_today_subscribe_updates()

    def _build_summary(self) -> str:
        return "；".join([f"插件：{'启用' if self._enabled else '未启用'}", f"融合通知：{'启用' if self._fusion_notify_enabled else '停用'} 建卡 {self._fusion_card_create_cron} / 刷新 {self._fusion_card_refresh_cron}", f"融合栏目：健康={'开' if self._health_in_report else '关'} / 订阅={'开' if self._subscribe_in_report else '关'} / 站点={'开' if self._site_stat_in_report else '关'}", f"插件日志清理：{'启用' if self._log_clean_enabled else '停用'} {self._log_clean_cron} 保留{self._log_clean_rows}行", f"自动备份：{'启用' if self._backup_enabled else '停用'} {self._backup_cron} 保留{self._backup_keep_count}个", f"系统更新：{'启用' if self._mp_update_enabled else '停用'} {self._mp_update_cron}", f"插件更新：{'启用' if self._plugin_update_reminder_enabled else '停用'} {self._plugin_update_reminder_cron}（自动安装{'开' if self._plugin_auto_install_enabled else '关'}）", f"插件库同步：{'启用' if self._market_update_enabled else '停用'} {self._market_update_cron}"])
