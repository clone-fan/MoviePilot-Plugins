"""Fusion notice / card-state aggregation helpers extracted from the main class.

Mixes instance methods (self), classmethods (cls) and staticmethods.
All resolve via MRO when ``FusionMixin`` is in the inheritance chain.
"""

import hashlib
import json
import re
import threading
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from app.schemas.types import MessageType

from app.sdk.logging import logger

from ..domain import site_helpers
from ..domain.fusion_event import FusionEvent
from ..domain.fusion_event_ledger import normalize_actual_task_event


class FusionMixin:
    """Mixin bundling fusion notice and card-state aggregation helpers."""

    _NOTIFICATION_OUTCOME_STATE_KEY = "notification_outcome_state_v1"
    _NOTIFICATION_OUTCOME_COOLDOWN = timedelta(hours=24)
    _notification_outcome_lock = threading.RLock()

    def _notify_or_console(self, mtype: Any = None, title: str = "", text: str = "", image: Any = None, **kwargs) -> bool:
        component = kwargs.pop("component", None)
        if self._fusion_notify_enabled:
            payload = dict(kwargs)
            if image:
                payload["image"] = image
            event = FusionEvent.create(
                owner=self._fusion_column_for_title(title),
                event_type="realtime",
                title=title or "融合通知",
                body=text,
                level=self._fusion_event_level(payload.pop("level", "info")),
                payload=payload,
                component=component or "",
            )
            return self._emit_fusion_event(event)
        payload = {"mtype": mtype or MessageType.Plugin, "title": title, "text": text}
        if image:
            payload["image"] = image
        payload.update(kwargs)
        if not self._post_moviepilot_notification(payload, component=component, title=title):
            return False
        return True

    def _post_moviepilot_notification(self, payload: Dict[str, Any], component: Optional[str] = None, title: str = "") -> bool:
        if self._fusion_notify_enabled:
            data = dict(payload or {})
            event = FusionEvent.create(
                owner=self._fusion_column_for_title(title or data.get("title", "")),
                event_type="realtime",
                title=title or str(data.get("title") or "融合通知"),
                body=str(data.get("text") or ""),
                level=self._fusion_event_level(data.get("level")),
                payload={key: value for key, value in data.items() if key not in {"title", "text", "mtype", "level"}},
                component=component or "",
            )
            return self._emit_fusion_event(event)
        component_key = component or self._moviepilot_notification_component(title or (payload or {}).get("title", ""))
        ok, _ = self._runtime_gate("notification", component=component_key, name=title or "MoviePilot notification")
        if not ok:
            return False
        self.post_message(**(payload or {}))
        return True

    def _emit_fusion_event(self, event: FusionEvent) -> bool:
        if not self._fusion_notify_enabled:
            return False
        if not isinstance(event, FusionEvent):
            raise TypeError("Fusion outbound gateway accepts FusionEvent only")
        record = event.to_record()
        return self._emit_fusion_notice(
            column_key=event.owner,
            title=event.title,
            text=event.body,
            level=event.level,
            payload=record,
        )

    def _emit_fusion_owned_event(
        self, *, owner: str, event_type: str, title: str, body: str = "", level: str = "info",
        payload: Optional[Dict[str, Any]] = None, component: str = "", realtime: bool = False,
        execution_status: str = "executed", result_status: Optional[str] = None, outcome: str = "", event_date: str = "",
    ) -> bool:
        return self._emit_fusion_event(FusionEvent.create(
            owner=owner, event_type=event_type, title=title, body=body, level=level, payload=payload, component=component,
            realtime=realtime, execution_status=execution_status, result_status=result_status, outcome=outcome, event_date=event_date))

    def _notify_fusion_task_outcome(
        self, *, mtype: Any, title: str, text: str, outcome: str,
        success: bool, component: str, affected_owner: str = "", task_key: str = "",
        task_group: str = "", execution_count: int = 1,
        notification_status: str = "", notification_target: str = "",
        notification_fingerprint: str = "", notification_cooldown: bool = False,
        notification_notify_noop: bool = False, notification_manual: bool = False,
    ) -> bool:
        concrete_outcome = str(outcome or "").strip()
        if not concrete_outcome:
            raise ValueError("Fusion task outcome requires concrete humanized copy")
        if self._fusion_notify_enabled:
            resolved_task_key = str(task_key or component or "").strip()
            resolved_task_group = str(task_group or self._fusion_task_group(component) or "").strip()
            event_payload = {
                "affected_owner": affected_owner,
                "task_key": resolved_task_key,
                "task_group": resolved_task_group,
                "execution_count": max(1, int(execution_count or 1)),
                "last_result_at": datetime.now().astimezone().isoformat(),
            }
            return self._emit_fusion_owned_event(
                owner="today-completion" if success else "current-anomalies", event_type="completion" if success else "anomaly",
                title=title, body=text, level="success" if success else "error", payload=event_payload,
                component=component, execution_status="executed", result_status="success" if success else "error", outcome=concrete_outcome)
        status = str(notification_status or "").strip().lower()
        if notification_manual:
            # 手动执行（配置页按钮或手动 API）是用户显式发起的一次性动作：
            # 结果通知必须真实发出，不参与 24 小时冷却，也不被"无变化"抑制。
            return self._notify_or_console(mtype=mtype, title=title, text=text, component=component)
        if not status:
            return self._notify_or_console(mtype=mtype, title=title, text=text, component=component)
        if status not in {"noop", "changed", "error", "recovered"}:
            raise ValueError(f"Unsupported notification outcome status: {status}")
        if notification_cooldown and status in {"changed", "error"} and not notification_fingerprint:
            raise ValueError("Cooled notification outcome requires a stable fingerprint")

        target = notification_target or task_key or component
        entry_key = self._notification_outcome_entry_key(component, target)
        with self._notification_outcome_lock:
            state = self._load_notification_outcome_state()
            entries = state["entries"]
            previous = entries.get(entry_key)

            if status == "noop":
                if previous is not None:
                    entries.pop(entry_key, None)
                    if not self._save_notification_outcome_state(state):
                        return False
                if not notification_notify_noop:
                    return True
                return self._notify_or_console(mtype=mtype, title=title, text=text, component=component)

            if status == "recovered":
                had_error = isinstance(previous, dict) and previous.get("status") == "error"
                if not had_error and not notification_notify_noop:
                    if previous is not None:
                        entries.pop(entry_key, None)
                        if not self._save_notification_outcome_state(state):
                            return False
                    return True
                delivered = self._notify_or_console(mtype=mtype, title=title, text=text, component=component)
                if delivered and previous is not None:
                    entries.pop(entry_key, None)
                    if not self._save_notification_outcome_state(state):
                        return False
                return delivered

            fingerprint = str(notification_fingerprint or "").strip()
            if notification_cooldown and self._notification_outcome_is_cooled(previous, status, fingerprint):
                return True

            delivered = self._notify_or_console(mtype=mtype, title=title, text=text, component=component)
            if not delivered:
                return False
            if notification_cooldown:
                entries[entry_key] = {
                    "status": status,
                    "fingerprint": fingerprint,
                    "last_notified_at": self._notification_outcome_now().isoformat(),
                }
                return self._save_notification_outcome_state(state)
            if previous is not None:
                entries.pop(entry_key, None)
                return self._save_notification_outcome_state(state)
            return True

    @staticmethod
    def _notification_outcome_entry_key(component: Any, target: Any) -> str:
        def normalize(value: Any, fallback: str) -> str:
            text = re.sub(r"[^a-zA-Z0-9_.-]+", "-", str(value or "").strip()).strip("-")
            return (text or fallback)[:80]

        return f"{normalize(component, 'notification')}:{normalize(target, 'default')}"

    @staticmethod
    def _notification_outcome_fingerprint(value: Any) -> str:
        raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @staticmethod
    def _normalize_notification_error_summary(error: Any) -> str:
        text = str(error or "").strip()
        text = re.sub(r"\b\d{4}-\d{1,2}-\d{1,2}[T ]\d{1,2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:?\d{2})?\b", "<datetime>", text)
        text = re.sub(r"\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b", "<date>", text)
        text = re.sub(r"\b\d{1,2}:\d{2}:\d{2}(?:\.\d+)?\b", "<time>", text)
        return re.sub(r"\s+", " ", text)[:500]

    def _notification_error_fingerprint(self, error: Any) -> str:
        error_type = type(error).__name__ if isinstance(error, BaseException) else "error"
        return self._notification_outcome_fingerprint({
            "type": error_type,
            "summary": self._normalize_notification_error_summary(error),
        })

    @staticmethod
    def _notification_outcome_now() -> datetime:
        return datetime.now().astimezone()

    def _load_notification_outcome_state(self) -> Dict[str, Any]:
        empty = {"version": 1, "entries": {}}
        try:
            raw = self.get_data(self._NOTIFICATION_OUTCOME_STATE_KEY)
        except Exception as err:
            logger.warning(f"Signal 普通通知状态读取失败，按空状态处理：{err}")
            return empty
        if not isinstance(raw, dict):
            return empty
        if raw.get("version") != 1:
            return empty
        raw_entries = raw.get("entries")
        if not isinstance(raw_entries, dict):
            return empty
        entries = {}
        for key, value in raw_entries.items():
            if not isinstance(key, str) or not isinstance(value, dict):
                continue
            status = str(value.get("status") or "").strip().lower()
            fingerprint = str(value.get("fingerprint") or "").strip()
            last_notified_at = str(value.get("last_notified_at") or "").strip()
            if status not in {"changed", "error"} or not fingerprint or not last_notified_at:
                continue
            entries[key[:161]] = {
                "status": status,
                "fingerprint": fingerprint,
                "last_notified_at": last_notified_at,
            }
        return {"version": 1, "entries": entries}

    def _save_notification_outcome_state(self, state: Dict[str, Any]) -> bool:
        try:
            self.save_data(self._NOTIFICATION_OUTCOME_STATE_KEY, {
                "version": 1,
                "entries": dict(state.get("entries") or {}),
            })
            return True
        except Exception as err:
            logger.error(f"Signal 普通通知状态保存失败：{err}")
            return False

    def _notification_outcome_is_cooled(
        self, previous: Any, status: str, fingerprint: str,
    ) -> bool:
        if not isinstance(previous, dict):
            return False
        if previous.get("status") != status or previous.get("fingerprint") != fingerprint:
            return False
        try:
            notified_at = datetime.fromisoformat(str(previous.get("last_notified_at") or "").replace("Z", "+00:00"))
            if notified_at.tzinfo is None:
                notified_at = notified_at.astimezone()
        except (TypeError, ValueError):
            return False
        elapsed = self._notification_outcome_now() - notified_at
        return timedelta(0) <= elapsed < self._NOTIFICATION_OUTCOME_COOLDOWN

    @staticmethod
    def _fusion_task_group(component: Any) -> str:
        """Resolve grouping from the stable component key, never from rendered title text."""
        return {
            "site_stat": "站点统计",
            "health_check": "维护任务",
            "backup": "维护任务",
            "log_clean": "维护任务",
            "seed_clean": "维护任务",
            "downloader_helper": "维护任务",
            "dltag": "维护任务",
            "mp_update": "更新管理",
            "update_preview": "更新管理",
            "market_update": "更新管理",
            "plugin_update_reminder": "更新管理",
            "subfill_download": "规则填充",
            "subfill_category": "规则填充",
            "subfill": "规则填充",
        }.get(str(component or "").strip(), "")

    @staticmethod
    def _task_outcome_notification_enabled(component_notify: Any) -> bool:
        return bool(component_notify)

    @staticmethod
    def _fusion_event_level(value: Any) -> str:
        raw = str(value or "info").strip().lower()
        return {
            "warn": "warning",
            "fatal": "error",
            "fail": "error",
            "failure": "error",
            "ok": "success",
        }.get(raw, raw if raw in {"info", "success", "warning", "error", "idle"} else "info")

    @staticmethod
    def _moviepilot_notification_component(title: str) -> Optional[str]:
        text = str(title or "")
        mapping = (
            ("健康巡查", "health_check"),
            ("站点数据", "site_stat"),
            ("日志清理", "log_clean"),
            ("备份", "backup"),
            ("MoviePilot更新", "mp_update"),
            ("主程序更新", "mp_update"),
            ("插件库同步", "market_update"),
            ("插件库更新", "market_update"),
            ("插件更新提醒", "plugin_update_reminder"),
            ("插件更新", "plugin_update_reminder"),
            ("插件自动安装", "plugin_update_reminder"),
            ("自动删种", "seed_clean"),
            ("下载器助手", "downloader_helper"),
            ("订阅规则自动填充", "subfill"),
            ("订阅追新", "subscribe_reminder"),
            ("媒体事件", "msgnotify"),
        )
        for marker, component in mapping:
            if marker in text:
                return component
        return None

    def _notice_output_enabled(self, component_notify: Any = True) -> bool:
        return bool(self._fusion_notify_enabled or component_notify)

    def _emit_fusion_notice(self, column_key: str, title: str, text: str = "", level: str = "info", payload: Optional[Dict[str, Any]] = None) -> bool:
        if not self._fusion_notify_enabled:
            return False
        raw_key = str(column_key or self._fusion_column_for_title(title) or "").strip()
        key = self._normalize_fusion_column(raw_key)
        valid_columns = {x["key"] for x in self._fusion_column_registry()}
        enabled_columns = set(self._fusion_notify_columns or valid_columns) & valid_columns
        if key not in enabled_columns:
            return False
        token, chat_id, _source = self._resolve_fusion_telegram_config()
        if not token or not chat_id:
            self._tg_console_last_error = "Telegram 融合通知 Bot Token/Chat ID 未配置"
            state = self._tg_console_state(chat_id=chat_id)
            state["last_error"] = self._tg_console_last_error
            self._save_tg_console_state(state)
            return False
        state = self._tg_console_state(chat_id=chat_id)
        if not state.get("message_id"):
            state["last_error"] = "融合通知当前没有可更新的 active card"
            self._save_tg_console_state(state)
            return False
        item = {
            "title": str(title or key).strip()[:120],
            "text": str(text or "").strip()[:20000],
            "level": str(level or "info"),
            "payload": payload or {},
            "time": datetime.now().strftime("%H:%M:%S"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        report_key = raw_key or key
        if report_key == "health" and "健康巡查" in str(title or ""):
            report_key = "health_check"
        if report_key:
            reports = state.setdefault("reports", {})
            reports[report_key] = {k: v for k, v in item.items() if k != "payload"}
        notices = list(state.get("notices") or [])
        notices.insert(0, {k: v for k, v in item.items() if k != "payload"})
        state["notices"] = notices[:self._tg_console_max_notices]
        columns = state.setdefault("columns", {})
        items = list((columns.get(key) or {}).get("items") or [])
        items.insert(0, item)
        columns[key] = {"items": items[:self._tg_console_max_notices], "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        stream_owner = self._fusion_stream_owner(raw_key, payload, item)
        if stream_owner:
            stream_payload = payload.get("payload") if isinstance(payload, dict) and isinstance(payload.get("payload"), dict) else payload
            self._sync_v7_stream_owner(
                state,
                stream_owner,
                self._v7_stream_module(stream_owner, item["title"], item["text"], item["level"], stream_payload),
                active=str(item.get("level") or "") not in {"success", "error"},
            )
        else:
            record = payload if isinstance(payload, dict) else {}
            actual_event = normalize_actual_task_event(record, str(state.get("date") or self._today_prefix()))
            component_key = str(record.get("component") or "").strip()
            event_payload = record.get("payload") if isinstance(record.get("payload"), dict) else {}
            affected = event_payload.get("affected_owner") or event_payload.get("affected_owners") or []
            affected_owners = [str(affected)] if isinstance(affected, str) and affected else [str(owner) for owner in affected if owner]
            for affected_owner in affected_owners:
                if affected_owner in {"realtime-media", "realtime-task-backup"}:
                    self._sync_v7_stream_owner(state, affected_owner, None, active=False)
            if raw_key == "current-anomalies":
                if actual_event:
                    self._record_v7_event(state, actual_event)
                anomaly = {
                    "owner": "current-anomalies",
                    "kicker": "当前异常",
                    "count": "1 项",
                    "primary": item["title"],
                    "context": f"需要关注 · {item['title']}",
                    "meta": f"最近 {item['time'][:5]}",
                    "affected_owners": affected_owners,
                    "details_rows": [[item["text"][:80] or item["title"], item["time"][:5]]],
                }
                self._record_v7_anomaly(state, component_key or (affected_owners[0] if affected_owners else item["title"]), anomaly)
            elif raw_key == "today-completion":
                if actual_event:
                    if actual_event.get("result_status") == "success":
                        self._clear_v7_anomaly(state, component_key or str(event_payload.get("affected_owner") or ""))
                    self._record_v7_event(state, actual_event)
            self._compose_tg_console_v7_model(state)
            calendar_status = str(state.get("subscription_calendar_status") or "").strip()
            if calendar_status in {"partial", "failed", "invalid"}:
                self._tg_console_last_error = (
                    f"订阅日历状态：{calendar_status}"
                    + (f"；{state.get('subscription_calendar_errors', [''])[:1][0]}" if state.get("subscription_calendar_errors") else "")
                )
                state["last_error"] = self._tg_console_last_error
                self._save_tg_console_state(state)
                return False
        try:
            ok = self._tg_console_upsert_card(token, chat_id, state)
        except Exception as err:
            self._tg_console_last_error = f"Telegram 融合通知更新异常：{self._telegram_safe_error(err, limit=500)}"
            state["last_error"] = self._tg_console_last_error
            self._save_tg_console_state(state)
            logger.warning(f"Signal {self._tg_console_last_error}")
            return False
        if ok:
            self._tg_console_last_error = ""
            state["last_error"] = ""
        self._save_tg_console_state(state)
        return ok

    @staticmethod
    def _fusion_stream_owner(raw_key: str, payload: Any, item: Dict[str, Any]) -> str:
        if raw_key in {"realtime-media", "realtime-task-backup"}:
            return raw_key
        record = payload if isinstance(payload, dict) else {}
        if record.get("owner") in {"realtime-media", "realtime-task-backup"}:
            return str(record.get("owner"))
        if record.get("event_type") == "realtime":
            component = str(record.get("component") or "").strip().lower()
            if component in {"backup", "config_backup", "configuration_backup"} or "配置备份" in str(item.get("title") or ""):
                return "realtime-task-backup"
            if component in {"media", "msgnotify"} or "媒体" in str(item.get("title") or "") or "播放" in str(item.get("title") or ""):
                return "realtime-media"
        return ""

    def _fusion_column_snapshot(self, key: str, state: Dict[str, Any]) -> Tuple[str, str, str]:
        if key == "site_stats":
            return "站点增量", "\n".join(self._fusion_site_stat_lines()), "success"
        if key == "download_transfer":
            return "下载入库", self._build_today_transfer_report_text(), "success"
        if key == "subscribe":
            snapshot = self._read_today_subscription_calendar_snapshot()
            items = list(snapshot.items)
            text = "\n".join(f"⦁ {x}" for x in items) if items else "⦁ 今日暂无订阅追新"
            if snapshot.is_partial:
                text = f"{text}\n⚠️ {snapshot.failure_message()}"
            return "订阅追新", text, "warning" if snapshot.is_partial else "success"
        if key == "storage":
            return "存储空间", "\n".join(self._get_storage_health_locked()), "success"
        if key == "media":
            media = self._fusion_media_activity_report(state)
            if media:
                return "媒体动态", str(media.get("text") or ""), str(media.get("level") or "info")
            stats = self._get_media_stats_locked()
            text = "\n".join(stats or [])
            return "媒体统计", text or "⦁ 暂无媒体统计数据", "success" if stats else "idle"
        if key == "health":
            context = getattr(self, "_fusion_refresh_context", {}) or {}
            live_result = context.get("live_result") or {}
            data = live_result.get("health_summary") if isinstance(live_result, dict) else None
            if not isinstance(data, dict):
                data = self._build_health_summary(persist=True)
            return "健康巡查", "\n".join(self._format_health_report_lines(data)), "success" if data.get("success") else "warning"
        if key == "maintenance":
            return "维护任务", "\n".join(self._fusion_recent_task_lines(["backup", "log_clean", "plugin_uninstall", "seed_clean", "downloader_helper"])), "info"
        if key == "updates":
            return "更新管理", "\n".join(self._fusion_recent_task_lines(["update_preview", "plugin_update_reminder", "market_update"])), "info"
        return "融合通知", "", "info"

    def _fusion_site_stat_lines(self) -> List[str]:
        rows = self._get_site_increment_locked()
        return rows[:8] if rows else ["⦁ 已刷新站点数据，暂无可用增量"]

    @staticmethod
    def _filter_fusion_health_lines(lines: List[str]) -> List[str]:
        rows = []
        for raw in lines or []:
            text = str(raw or "").strip()
            if not text:
                continue
            if "存储空间" in text or "storage" in text.lower():
                continue
            rows.append(text)
        return rows or ["⦁ 暂无健康巡查数据"]

    def _fusion_recent_task_lines(self, keys: List[str]) -> List[str]:
        labels = {
            "backup": "配置备份",
            "log_clean": "日志清理",
            "plugin_uninstall": "插件卸载",
            "seed_clean": "自动删种",
            "downloader_helper": "下载器助手",
            "update_preview": "MP 更新",
            "market_update": "插件库同步",
            "plugin_update_reminder": "插件更新",
        }
        rows = []
        for key in keys:
            data = self.get_data(f"last_{key}") or {}
            label = labels.get(key, key)
            if not data:
                rows.append(f"⦁ {label}：暂无记录")
                continue
            if key in {"update_preview", "market_update", "plugin_update_reminder", "plugin_auto_install"}:
                status = self._fusion_update_task_status(key, data)
                summary = self._fusion_update_task_summary(key, data)
            else:
                status = "成功" if data.get("success") is True else ("失败" if data.get("success") is False else "待确认")
                summary = self._fusion_task_result_summary(label, data)
            rows.append(f"⦁ {label}：{status}" + (f"｜{summary}" if summary else ""))
        return rows

    @classmethod
    def _fusion_update_task_status(cls, key: str, data: Dict[str, Any]) -> str:
        raw = cls._fusion_task_raw_text(data)
        raw_lower = raw.lower()
        if data.get("success") is False or data.get("error"):
            return "检查失败"
        if key == "update_preview":
            if data.get("upgrade_dispatched") or any(word in raw for word in ("已触发 MoviePilot 升级", "已触发 MoviePilot 重启", "更新执行：已触发")):
                return "已触发更新"
            if re.search(r"有更新|has_update['\"]?\s*[:=]\s*True", raw, re.I):
                return "有更新"
            if any(word in raw for word in ("无更新", "已是最新")):
                return "已是最新"
            return "检查完成" if data.get("success") is True else "待确认"
        if key == "market_update":
            if "写入当前配置：已执行" in raw or "写入 app.env：已执行" in raw:
                return "已同步"
            if data.get("has_update") or data.get("new_markets"):
                return "发现变化"
            if re.search(r"新发现\s*[：:]\s*[1-9]\d*", raw):
                return "发现变化"
            if any(word in raw for word in ("未执行", "新发现：0", "新发现:0", "新发现： 0")):
                return "已是最新"
            return "同步完成" if data.get("success") is True else "待确认"
        if key in {"plugin_update_reminder", "plugin_auto_install"}:
            install_match = re.search(r"自动安装：成功\s*(\d+)\s*个[｜|]\s*失败\s*(\d+)\s*个", raw)
            if install_match:
                if int(install_match.group(2)) > 0:
                    return "部分失败"
                return "已安装" if int(install_match.group(1)) > 0 else "无可安装更新"
            update_match = re.search(r"发现可更新插件：\s*(\d+)\s*个", raw)
            if update_match:
                return "有更新" if int(update_match.group(1)) > 0 else "已是最新"
            if any(word in raw for word in ("当前没有可更新插件", "无可安装更新")):
                return "已是最新"
            return "检查完成" if data.get("success") is True else "待确认"
        if any(word in raw for word in ("失败", "异常", "错误")) or any(word in raw_lower for word in ("error", "timeout", "failed")):
            return "检查失败"
        return "成功" if data.get("success") is True else ("失败" if data.get("success") is False else "待确认")

    @classmethod
    def _fusion_update_task_summary(cls, key: str, data: Dict[str, Any]) -> str:
        raw = cls._fusion_sanitize_update_task_text(cls._fusion_task_raw_text(data))
        if not raw:
            return ""
        if key == "update_preview":
            versions = re.findall(r"(?:本地|当前|最新)\s*[：:]\s*(v?\d+(?:\.\d+){1,4})", raw, re.I)
            if versions:
                return f"版本 {versions[-1]}"
            match = re.search(r"(?:后端|前端|backend|frontend)[^；。\n]*(?:无更新|已是最新|有更新)[^；。\n]*", raw, re.I)
            if match:
                return match.group(0).strip(" ⦁-")
        if key == "market_update":
            match = re.search(r"新发现\s*[：:]\s*\d+\s*个", raw)
            if match:
                return match.group(0)
            writes = sum(1 for marker in ("写入当前配置：已执行", "写入 app.env：已执行") if marker in raw)
            if writes:
                return f"同步 {writes} 处插件库配置"
        if key == "plugin_update_reminder":
            match = re.search(r"发现可更新插件：\s*\d+\s*个", raw)
            if match:
                return match.group(0)
        if key == "plugin_auto_install":
            match = re.search(r"自动安装：成功\s*\d+\s*个[｜|]\s*失败\s*\d+\s*个", raw)
            if match:
                return match.group(0)
        return cls._summarize_fusion_task_text("", raw)

    @staticmethod
    def _fusion_task_raw_text(data: Dict[str, Any]) -> str:
        return str(data.get("error") or data.get("message") or data.get("output") or "").strip()

    @staticmethod
    def _fusion_sanitize_update_task_text(text: str) -> str:
        lines = []
        for raw in str(text or "").splitlines():
            line = raw.strip()
            if not line:
                continue
            if "MP运维助手直接接替" in line or "MP 運維助手直接接替" in line:
                continue
            line = re.sub(r"^[🔄🧩]\s*", "", line).strip()
            lines.append(line)
        clean = "\n".join(lines)
        clean = clean.replace("MP运维助手直接接替", "").replace("（MP运维助手直接接替）", "")
        return clean.strip()

    @classmethod
    def _fusion_task_result_summary(cls, label: str, data: Dict[str, Any]) -> str:
        raw = cls._fusion_task_raw_text(data)
        if not raw:
            return ""
        return cls._summarize_fusion_task_text(label, raw)

    @classmethod
    def _summarize_fusion_task_text(cls, label: str, text: str) -> str:
        clean = re.sub(r"\s+", " ", str(text or "").replace("\n", "；")).strip(" ；。")
        clean = re.sub(r"^(?:成功|失败|OK|ERROR|Error|error)\s*[：:；。\-\s]*", "", clean).strip(" ；。")
        if not clean:
            return ""
        match = re.search(r"扫描文件\s*[：:]?\s*(\d+)\s*个.*?候选文件\s*[：:]?\s*(\d+)\s*个", clean)
        if match:
            return f"扫描 {match.group(1)} 个，候选 {match.group(2)} 个"
        match = re.search(r"已为\s*(\d+)\s*个种子.*?标签", clean)
        if match:
            return f"已为 {match.group(1)} 个种子按站点打标签"
        match = re.search(r"(?:处理|命中|暂停|删除)\s*(\d+)\s*个(?:种子|任务|项目)?", clean)
        if match:
            return f"处理 {match.group(1)} 个项目"
        match = re.search(r"模式\s*[：:]\s*([^；。|｜]+)", clean)
        if match:
            return f"模式：{match.group(1).strip()}"
        if any(key in clean for key in ("暂无记录", "无记录", "暂无可", "没有符合条件", "未发现")):
            return clean.split("；", 1)[0].strip()
        first = re.split(r"[；。]", clean, maxsplit=1)[0].strip()
        if first and len(first) <= 72:
            return first
        return "结果较长，详情请看任务记录"

    @staticmethod
    def _fusion_report_key(column_key: str) -> str:
        return {
            "site_stats": "site_stat",
            "download_transfer": "today_transfer",
            "subscribe": "subscribe_reminder",
            "storage": "storage",
            "media": "media_stat",
            "health": "health_check",
            "maintenance": "maintenance",
            "updates": "updates",
        }.get(column_key, column_key)

    @staticmethod
    def _fusion_usage_bar(pct: float, width: int = 8) -> str:
        return site_helpers.fusion_usage_bar(pct, width)

    def _format_fusion_storage_items(self, items: List[str]) -> List[str]:
        rows: List[str] = []
        for raw in items or []:
            text = re.sub(r"^\s*[•⦁\-\s]+", "", str(raw or "").strip())
            if not text:
                continue
            match = re.search(r"^(?P<name>[^：:]+)[：:]\s*(?:💽\s*)?(?P<used>[\d.]+)\s*(?P<uunit>[KMGTPE]?B?)\s*/\s*(?P<total>[\d.]+)\s*(?P<tunit>[KMGTPE]?B?).*?已用\s*(?P<pct>\d+)%", text, re.I)
            if match:
                name = match.group("name").strip()
                pct = float(match.group("pct"))
                used = f"{match.group('used')}{self._normalize_compact_unit(match.group('uunit'))}"
                total = f"{match.group('total')}{self._normalize_compact_unit(match.group('tunit'))}"
                rows.append(f"{name}：已用 {pct:.0f}% ｜ {used}/{total}")
            else:
                rows.append(re.sub(r"\[[█░]+\]\s*", "", text))
        return rows
