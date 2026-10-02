import re
import os
import hashlib
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from app.sdk.logging import logger
from app.schemas.types import MessageType

from ..domain.fusion_card_model import build_v7_card_model, validate_v7_card_model
from ..domain.fusion_composition import (
    compose_v7_snapshot,
    parse_storage_rows,
    parse_subscription_rows,
    normalize_transfer_rows,
    update_change_count,
)
from ..domain.fusion_event_ledger import append_actual_task_event, event_ledger_rows
from ..domain.fusion_rich_message import action_status_blocks, render_v7_rich_message
from ..domain.update_jobs import (
    UPDATE_KINDS,
    expire_update_jobs,
    job_is_actionable,
    render_signature,
    visible_jobs,
)


# 动作状态行的生命周期（秒）：成功提示只短暂停留，失败保留更久方便回看，
# running 超过上限视为超时（worker 异常退出时不再让卡片长期挂着「⏳」）。
# success 与回调层 FUSION_STATUS_EXPIRY_DELAY(20s) 保持一致：定时器因插件重载
# 丢失时，超龄成功状态会在下次渲染被剔除，不会一直挂在卡片上。
_FUSION_ACTION_TTL = {"running": 180, "success": 20, "error": 600}

# 融合卡「需要注意」里的失败异常与动作状态同口径：失败保留 10 分钟后从视图
# 剔除，避免一次网络抖动在卡片上长期挂着。仅影响视图，不改动落盘状态。
_V7_ANOMALY_TTL_SECONDS = 600


def _fusion_feed_timestamp(item: Any) -> float:
    try:
        return float((item or {}).get("updated_at") or 0) if isinstance(item, dict) else 0.0
    except (TypeError, ValueError):
        return 0.0


def _live_fusion_action_feed(state: Any) -> List[Dict[str, Any]]:
    """按状态过滤已过期的动作条目；仅影响视图，不改动落盘状态。"""
    feed = state.get("fusion_action_feed") if isinstance(state, dict) else None
    if not isinstance(feed, list):
        return []
    now = datetime.now().timestamp()
    live: List[Dict[str, Any]] = []
    for item in feed:
        if not isinstance(item, dict):
            continue
        status = str(item.get("status") or "")
        updated_at = _fusion_feed_timestamp(item)
        if updated_at and now - updated_at > _FUSION_ACTION_TTL.get(status, 300):
            continue
        live.append(item)
    return live


def _v7_transfer_label(rows: Any) -> str:
    """下载入库结论：内容为空态时不报条数（与内容页口径一致）。"""
    empty = {"", "无", "暂无", "未取到", "-", "--"}
    items = list(rows or [])
    for row in items:
        cells = list(row) if isinstance(row, (list, tuple)) else [row]
        value = str(cells[-1] if cells else "").strip()
        if value and value not in empty and "未取到" not in value:
            return f"{len(items)} 项"
    return "无"


def _v7_update_label(rows: Any) -> str:
    """更新管理结论：按行内真实更新指示统计「系统 N · 插件 M」。"""
    system_count = plugin_count = 0
    check_failed = False
    for row in rows or []:
        cells = list(row) if isinstance(row, (list, tuple)) else [row]
        label = str(cells[0] if cells else "").strip()
        value = str(cells[-1] if len(cells) > 1 else "").strip()
        check_failed = check_failed or any(word in value for word in ("异常", "检查失败", "请求失败"))
        # 同一处更新可能同时出现「有更新」和「可更新」，避免重复计数
        hits = update_change_count(value)
        if not hits:
            continue
        if "MP" in label or "系统" in label:
            system_count += hits
        elif "插件" in label:
            plugin_count += hits
    unconfigured = any("未配置" in str(cell) for row in rows or []
                       for cell in (list(row) if isinstance(row, (list, tuple)) else [row]))
    if system_count or plugin_count:
        return f"系统 {system_count} · 插件 {plugin_count}" + (" · 检查失败" if check_failed else "")
    if unconfigured:
        return "未配置"
    return "检查失败" if check_failed else "无"


class TgConsoleRenderMixin:
    """Telegram fusion card HTML rendering ? chunks, tabs, metrics, icons, sections"""

    def _update_center_job_changed(self, kind: str, job: Dict[str, Any], state: Dict[str, Any]) -> None:
        """Auto-edit the active card when an update job materially changes."""
        if not getattr(self, "_fusion_notify_enabled", False) or not isinstance(state, dict) or not state.get("message_id"):
            return
        token, chat_id, _ = self._resolve_fusion_telegram_config()
        if not token or not chat_id:
            return
        signature = (str(kind or ""), render_signature(job))
        last_signatures = getattr(self, "_update_center_last_signatures", None)
        if not isinstance(last_signatures, dict):
            last_signatures = {}
        last_edits = getattr(self, "_update_center_last_edits", None)
        if not isinstance(last_edits, dict):
            last_edits = {}
        phase = str(job.get("phase") or "")
        immediate = phase not in {"checking", "downloading", "installing", "updating", "syncing"}
        if signature == last_signatures.get(kind) and immediate:
            return
        now = time.monotonic()
        if not immediate and now - float(last_edits.get(kind) or 0) < 2.0:
            return
        with self._tg_console_card_lock:
            latest = self._tg_console_state(chat_id=chat_id)
            latest.setdefault("update_jobs", {})[kind] = dict(job)
            self._save_tg_console_state(latest)
            self._tg_console_upsert_card(token, chat_id, latest)
        last_signatures[kind] = signature
        last_edits[kind] = now
        self._update_center_last_signatures = last_signatures
        self._update_center_last_edits = last_edits
        expires_at = float(job.get("expires_at") or 0)
        if expires_at > 0:
            self._schedule_update_center_expiry(kind, expires_at, token, chat_id)

    def _schedule_update_center_expiry(self, kind: str, expires_at: float, token: str, chat_id: str) -> None:
        """Schedule one expiry redraw per job kind, replacing any older timer."""
        timers = getattr(self, "_update_center_expiry_timers", None)
        if not isinstance(timers, dict):
            timers = {}
            self._update_center_expiry_timers = timers
        previous = timers.get(kind)
        if previous is not None:
            try:
                previous.cancel()
            except Exception:
                pass
        delay = max(1.0, expires_at - time.time())
        generation = getattr(self, "_runtime_generation", 0)

        def cleanup() -> None:
            logger.debug(f"Signal 更新中心状态到期重绘：kind={kind} expires_at={expires_at}")
            with self._tg_console_card_lock:
                state = self._tg_console_state(chat_id=chat_id)
                if not state.get("message_id"):
                    return
                jobs = state.get("update_jobs") if isinstance(state.get("update_jobs"), dict) else {}
                state["update_jobs"] = expire_update_jobs(jobs, now=time.time())
                self._save_tg_console_state(state)
                self._tg_console_upsert_card(token, chat_id, state, generation=generation)

        try:
            timer = threading.Timer(delay, cleanup)
            timer.daemon = True
            timer.name = f"Signal-update-center-expiry-{kind}"
            timer.start()
            timers[kind] = timer
        except Exception:
            timers.pop(kind, None)
            logger.warning(f"Signal 更新中心过期重绘定时器未能启动：{kind}")

    def _v7_card_buttons(self, state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """卡片内按钮行：页签 + 更新，回调格式与回调处理保持一致。"""
        if not isinstance(state, dict):
            return []
        registry = getattr(self, "_fusion_category_registry", None)
        if not callable(registry):
            return []
        wrapper = getattr(self, "_tg_console_plugin_callback_data", None)
        if not callable(wrapper):
            name = type(self).__name__
            wrapper = lambda payload: f"[PLUGIN]{name}|{payload}"
        active = self._v7_active_tab(state)
        known = {str(item.get("key") or "") for item in registry()}
        if active not in known:
            active = "overview"
        items: List[Dict[str, Any]] = []
        for meta in registry():
            key = str(meta.get("key") or "")
            children = [str(x) for x in (meta.get("children") or [])]
            configured = getattr(self, "_fusion_notify_columns", None)
            column_registry = getattr(self, "_fusion_column_registry", None)
            enabled = set(configured or ([x["key"] for x in column_registry()] if callable(column_registry) else []))
            if key != "overview" and children and not any(child in enabled for child in children):
                continue
            label = f'{meta.get("icon") or ""} {meta.get("label") or key}'.strip()
            wrapped = wrapper(f"aoatab:{key}")
            item: Dict[str, Any] = {"text": label, "callback_data": wrapped}
            if key == active:
                item["style"] = "primary"
            items.append(item)
        # 刷新按钮走和 📦/⬆/🧩 相同的动作机制（fusion_update + 卡内状态块）：
        # 点下去立刻写一条「⏳ 刷新中」并原地重绘，几十秒站点采集结束后同一条
        # 状态块变成「✅ 已刷新 / ⚠️ 失败」。旧实现只回一个 toast、不写卡内状态，
        # 采集期间没有任何变化，结果又常与当前内容一致（Telegram 直接判
        # message is not modified），用户看到的就是「按了没反应」。
        ensure = getattr(self, "_tg_console_ensure_fusion_action", None)
        nonce = ""
        if callable(ensure):
            try:
                nonce = ensure(state, "card_refresh", {}, "🔄 刷新")
            except Exception:
                nonce = ""
        if nonce:
            items.append({"text": "🔄 刷新",
                          "callback_data": wrapper(f"aoav1:{nonce}"),
                          "style": "success"})
        return items

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
        return render_v7_rich_message(
            model,
            active_tab=self._v7_active_tab(state),
            buttons=self._v7_card_buttons(state),
            action_buttons=self._v7_update_action_buttons(state),
            status_blocks=self._v7_action_status_blocks(state),
        )

    def _v7_update_action_buttons(self, state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """只把最近一次真实更新检查产生的动作候选渲染成卡片按钮。"""
        if not isinstance(state, dict):
            return []
        candidates = state.get("fusion_update_actions")
        candidates = candidates if isinstance(candidates, dict) else {}
        wrapper = getattr(self, "_tg_console_plugin_callback_data", None)
        if not callable(wrapper):
            wrapper = lambda payload: f"[PLUGIN]{type(self).__name__}|{payload}"
        ensure = getattr(self, "_tg_console_ensure_fusion_action", None)
        if not callable(ensure):
            return []
        running_kinds = {str(item.get("kind") or "") for item in _live_fusion_action_feed(state)
                         if str(item.get("status") or "") == "running"}
        jobs = state.get("update_jobs")
        if isinstance(jobs, dict) and jobs:
            # 只渲染仍然可见的任务：失败/部分成功超过 10 分钟后与状态行一起收起。
            jobs = {str(job.get("kind") or ""): job for job in visible_jobs(jobs)}
            if not jobs:
                return []
            buttons: List[Dict[str, Any]] = []
            seen_labels: set = set()
            component_gate = getattr(self, "_component_enabled", None)

            def component_on(key: str) -> bool:
                """按钮只在对应功能启用时出现，与执行端门阀保持一致。"""
                return (not callable(component_gate)) or bool(component_gate(key))

            def add_action(label: str, action_kind: str, payload: Dict[str, Any]) -> None:
                if label in seen_labels:
                    return
                nonce = ensure(state, action_kind, payload, label)
                buttons.append({"text": label, "callback_data": wrapper(f"aoav1:{nonce}")})
                seen_labels.add(label)

            plugin = jobs.get("plugin_update") if isinstance(jobs.get("plugin_update"), dict) else {}
            plugin_phase = str(plugin.get("phase") or "")
            plugin_items = [item for item in plugin.get("items") or [] if isinstance(item, dict)]
            plugin_retry_buttons = False
            if (component_on("plugin_update_reminder")
                    and plugin_phase in {"available", "failed", "partial"}
                    and plugin_items and "plugin_update" not in running_kinds):
                for item in plugin_items:
                    name = str(item.get("name") or item.get("id") or "插件").strip()
                    prefix = "📦 重试 " if plugin_phase in {"failed", "partial"} else "📦 更新 "
                    label = f"{prefix}{name[:24]}"
                    add_action(label, "plugin_update", item)
                plugin_retry_buttons = True
            if plugin_phase == "available" and not plugin_items:
                plugin_phase = "failed"
            mp = jobs.get("mp_update") if isinstance(jobs.get("mp_update"), dict) else {}
            phase = str(mp.get("phase") or "")
            mp_expires_at = float(mp.get("expires_at") or 0)
            if phase in {"available", "ready"} and mp_expires_at and mp_expires_at <= datetime.now().timestamp():
                phase = "failed"
            if component_on("mp_update") and phase in {"available", "ready"} and "mp_update" not in running_kinds:
                step = "download" if phase == "available" else "install"
                # 旧缓存或宿主暂不允许执行时先读状态，不展示点了也不能执行的确认。
                if step not in (mp.get("steps") or []):
                    step = "status"
                label = {"download": "📥 确认下载", "install": "⚠️ 确认重启安装", "status": "🔄 更新进度"}[step]
                component = str(mp.get("target_component") or "").strip()
                if component and step != "status":
                    label += f" {component}"
                if mp.get("target_version") and step != "status":
                    label += f" {mp.get('target_version')}"
                payload = {"step": step, "session": mp.get("session") or "", "version": mp.get("target_version") or ""}
                add_action(label, "mp_update", payload)
            market = jobs.get("market_update") if isinstance(jobs.get("market_update"), dict) else {}
            market_phase = str(market.get("phase") or "")
            if component_on("market_update") and market_phase == "available" and "market_update" not in running_kinds:
                payload = {"markets": list(market.get("items") or [])}
                add_action("🧩 同步插件库", "market_update", payload)

            # 恢复类按钮全局只保留一个，避免同一张卡同时出现多个重试入口。
            recovery = None
            if component_on("market_update") and plugin_phase == "unconfigured":
                recovery = ("🧩 同步插件库", "market_update", {"markets": []})
            elif phase in {"failed", "partial"}:
                recovery = ("🔎 重新检查", "card_refresh", {})
            elif plugin_phase in {"failed", "partial"} and not plugin_retry_buttons:
                recovery = ("🔎 重新检查", "card_refresh", {})
            elif component_on("market_update") and market_phase in {"unconfigured", "failed"}:
                recovery = ("🧩 同步插件库", "market_update", {"markets": list(market.get("items") or [])})
            if recovery:
                add_action(*recovery)
            return buttons
        buttons: List[Dict[str, Any]] = []
        plugin_entry = candidates.get("plugin_update") or {}
        plugin_items = [] if "plugin_update" in running_kinds else ((plugin_entry.get("payload") or {}).get("plugins") or [])
        for item in plugin_items:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name") or item.get("id") or "插件").strip()
            label = f"📦 更新 {name[:24]}"
            nonce = ensure(state, "plugin_update", item, label)
            buttons.append({"text": label, "callback_data": wrapper(f"aoav1:{nonce}")})
        mp_entry = candidates.get("mp_update") or {}
        panel = state.get("moviepilot_update_panel") or {}
        if panel and "mp_update" not in running_kinds:
            labels = {"download": "📥 确认下载", "install": "⚠️ 确认重启安装", "status": "🔄 更新进度", "check": "🔎 重新检查"}
            for step in panel.get("steps", []):
                panel_expires_at = float(panel.get("expires_at") or 0)
                if step in {"download", "install"} and panel_expires_at and panel_expires_at <= datetime.now().timestamp():
                    continue
                label = labels[step]
                if step in {"download", "install"}:
                    label += f" {panel.get('version') or ''}"
                payload = {"step": step, "session": panel["session"], "version": panel.get("version")}
                nonce = ensure(state, "mp_update", payload, label)
                buttons.append({"text": label, "callback_data": wrapper(f"aoav1:{nonce}")})
        elif mp_entry and "mp_update" not in running_kinds:
            payload = dict(mp_entry.get("payload") or {})
            label = "⬆ 更新 MoviePilot"
            nonce = ensure(state, "mp_update", payload, label)
            buttons.append({"text": label, "callback_data": wrapper(f"aoav1:{nonce}")})
        market_entry = candidates.get("market_update") or {}
        if market_entry and "market_update" not in running_kinds:
            payload = dict(market_entry.get("payload") or {})
            label = "🧩 同步插件库"
            nonce = ensure(state, "market_update", payload, label)
            buttons.append({"text": label, "callback_data": wrapper(f"aoav1:{nonce}")})
        return buttons

    @staticmethod
    def _v7_action_status_blocks(state: Dict[str, Any]) -> List[Dict[str, Any]]:
        """动作状态行：执行中到最终结果原地更新，成功后短暂停留即下线。"""
        blocks: List[Dict[str, Any]] = []
        for job in visible_jobs(state.get("update_jobs")):
            phase = str(job.get("phase") or "")
            # 「有更新可下载 / 待安装」是持久信息，总览与更新管理已经在显示；
            # 状态行只报「正在执行」和刚结束的结果，不长期占位。
            if phase in {"available", "ready"}:
                continue
            status = ("success" if phase in {"success", "up_to_date"}
                      else "error" if phase in {"failed", "partial", "unconfigured"}
                      else "running" if phase in {"checking", "downloading", "installing", "updating", "syncing"}
                      else "info")
            message = str(job.get("error") or job.get("message") or "")
            if phase == "partial" and message and not message.startswith("部分成功"):
                message = "部分成功：" + message
            if (float(job.get("expires_at") or 0) and float(job.get("expires_at") or 0) <= datetime.now().timestamp()
                    and phase not in {"unconfigured"}):
                message = "上次状态：" + message
            if job.get("progress") is not None and phase in {"downloading", "installing", "updating", "syncing"}:
                message += f" · {job.get('progress')}%"
            updated_at = float(job.get("updated_at") or 0)
            blocks.extend(action_status_blocks([{
                "status": status,
                "message": message,
                "time": datetime.fromtimestamp(updated_at).strftime("%H:%M") if updated_at else "",
            }]))
        feed = [item for item in _live_fusion_action_feed(state)[:3]
                if str(item.get("kind") or "") not in UPDATE_KINDS]
        blocks.extend(action_status_blocks(feed))
        return blocks

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
        refresh_input = state.pop("site_refresh", None)
        site_enabled = bool(getattr(self, "_site_stat_enabled", False))
        site_snapshot = self._site_increment_snapshot(refresh_result=refresh_input) if site_enabled else {"site_states": [], "active_count": 0}
        # The snapshot separates nonzero details from complete states and counts.
        site_rows = [[str(item.get("name") or "站点"),
                      f"↑{self._format_bytes(item['upload'])} · ↓{self._format_bytes(item['download'])}"]
                     for item in site_snapshot.get("sites") or []]
        site_notices = [[str(item.get("name") or "站点"), self._site_notice_detail(item, site_snapshot.get("date"))]
                        for item in site_snapshot.get("site_states") or [] if item.get("status") != "ok"]
        site_total = int(site_snapshot.get("active_count") or 0)
        counted = int(site_snapshot.get("counted_count") or 0)
        site_count = (f"{site_snapshot.get('updated_count', 0)}/{site_total}已更新 · {site_snapshot.get('counted_count', 0)}/{site_total}可统计"
                      if site_total else "未启用 PT 站点")
        site_summary = (f"↑{self._format_bytes(site_snapshot['upload_total'])}  ↓{self._format_bytes(site_snapshot['download_total'])}"
                        if counted else "暂不可用")
        if not site_total:
            site_count = "站点统计检查失败" if site_snapshot.get("error") else "未启用 PT 站点"
            site_rows = [[site_count, ""]]
            site_summary = ""
        if site_enabled:
            source = (refresh_input or {}).get("source") if isinstance(refresh_input, dict) else ""
            self._record_site_diagnostic(state, site_snapshot, source or site_snapshot.get("refresh_source") or "render")
        # The collector owns current site anomalies. Other component events stay intact.
        for key in ("site_stat", "persistent-sites"):
            self._clear_v7_anomaly(state, key)

        storage_lines = self._get_storage_health_locked()
        storage_rows = parse_storage_rows(storage_lines)
        storage_table_rows = self._v7_labeled_rows(storage_lines)
        transfer_rows = normalize_transfer_rows(self._v7_labeled_rows(self._v7_column_lines(state, "download_transfer")))
        media_rows = self._v7_labeled_rows(self._v7_column_lines(state, "media"))
        health_rows: List[List[str]] = []
        if bool(getattr(self, "_health_check_enabled", False)):
            health_rows = self._v7_health_rows()
        maintenance_rows = self._v7_component_rows(
            "_fusion_recent_task_lines", ["backup", "log_clean", "plugin_uninstall", "seed_clean", "downloader_helper"])
        update_rows = self._v7_update_rows(state)
        try:
            calendar_snapshot = self._read_today_subscription_calendar_snapshot()
            state["subscription_calendar_status"] = calendar_snapshot.status
            state["subscription_calendar_errors"] = list(calendar_snapshot.errors)
            subscription_lines = list(calendar_snapshot.items)
            if calendar_snapshot.is_partial:
                warning = calendar_snapshot.failure_message()
                observed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._record_v7_anomaly(state, "subscribe_reminder", {
                    "owner": "current-anomalies",
                    "kicker": "当前异常",
                    "count": "1 项",
                    "primary": "订阅日历部分读取失败",
                    "context": "需要关注 · 订阅追新",
                    "meta": f"最近 {observed_at[5:16]}",
                    "observed_at": observed_at,
                    "affected_owners": ["persistent-subscriptions"],
                    "details_rows": [[warning, observed_at[5:16]]],
                })
            else:
                self._clear_v7_anomaly(state, "subscribe_reminder")
        except Exception as err:
            snapshot = self._subscription_calendar_snapshot_for_scope()
            status = str(getattr(snapshot, "status", "failed") or "failed")
            error = getattr(snapshot, "failure_message", lambda: f"订阅日历读取失败：{err}")()
            state["subscription_calendar_status"] = status
            state["subscription_calendar_errors"] = list(getattr(snapshot, "errors", ()) or ()) or [error]
            subscription_lines = []
            observed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self._record_v7_anomaly(state, "subscribe_reminder", {
                "owner": "current-anomalies",
                "kicker": "当前异常",
                "count": "1 项",
                "primary": "订阅日历读取失败",
                "context": "需要关注 · 订阅追新",
                "meta": f"最近 {observed_at[5:16]}",
                "observed_at": observed_at,
                "affected_owners": ["persistent-subscriptions"],
                "details_rows": [[error, observed_at[5:16]]],
            })
        subscription_rows = parse_subscription_rows(subscription_lines)
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
        if bool(getattr(self, "_health_check_enabled", False)):
            enabled.add("health")
        enabled.update({"maintenance", "updates", "transfer", "media"})
        overview_rows = self._v7_overview_rows(
            site_count=site_count,
            health_rows=health_rows,
            subscription_rows=subscription_rows,
            storage_rows=storage_rows,
            transfer_rows=transfer_rows,
            maintenance_rows=maintenance_rows,
            media_rows=media_rows,
            update_rows=update_rows,
            state=state,
        )
        subscription_status = str(state.get("subscription_calendar_status") or "ok")
        subscription_problem = subscription_status in {"partial", "failed", "invalid"}
        if subscription_problem:
            for row in overview_rows:
                if row[0] == "📺 订阅追新":
                    row[1] = f"{len(subscription_rows)} 部 · 部分读取失败" if subscription_rows else "读取失败"
        if any(item.get("owner") == "realtime-media" for item in realtime):
            for row in overview_rows:
                if row[0] == "🎬 媒体动态":
                    row[1] = "有实时会话"
        enabled.add("overview")
        snapshot, card_state = compose_v7_snapshot(
            identity=self._v7_identity(),
            site_rows=site_rows,
            site_count=site_count,
            site_summary=site_summary,
            site_notice_rows=site_notices,
            subscription_rows=subscription_rows,
            storage_rows=storage_table_rows or storage_rows,
            health_rows=health_rows,
            maintenance_rows=maintenance_rows,
            update_rows=update_rows,
            transfer_rows=transfer_rows,
            media_rows=media_rows,
            overview_rows=overview_rows,
            update_attention_rows=self._v7_update_attention_rows(state),
            completion_rows=completion_rows,
            realtime=realtime,
            anomalies=anomalies,
            enabled_persistent=enabled,
        )
        subscription = snapshot["persistent"].get("subscriptions")
        if subscription is not None and subscription_problem:
            subscription["availability"] = "partial" if subscription_rows else "failed"
            subscription["count"] = f"{len(subscription_rows)} 部 · 部分读取失败" if subscription_rows else "读取失败"
            if not subscription_rows:
                subscription["preview_rows"] = []
                subscription["details_rows"] = []
        state["v7_snapshot"] = snapshot
        state["v7_state"] = card_state
        state["v7_model"] = build_v7_card_model(snapshot, state=card_state)
        self._attach_site_metric_rows(state["v7_model"], site_snapshot)
        self._attach_tab_counts(state["v7_model"], site_snapshot, storage_rows, update_rows)
        return state["v7_model"]

    def _attach_tab_counts(self, model: Dict[str, Any], site_snapshot: Dict[str, Any],
                           storage_rows: List[List[str]], update_rows: List[List[str]]) -> None:
        """栏目标题右侧的结论值对齐定稿模板：站点「X/Y 正常」、存储「N%」、更新「系统 N · 插件 M」。"""
        if not isinstance(model, dict):
            return
        modules = {str(item.get("owner") or ""): item for item in model.get("modules") or []}

        sites = modules.get("persistent-sites")
        if sites is not None:
            # 与站点明细和总览使用同一份完整快照。最近一次刷新可能只覆盖
            # 一个站点，不能拿局部操作计数替换全站计数，也不能按可见行数计数。
            raw_ok = site_snapshot.get("refresh_ok_count")
            if raw_ok is None:
                raw_ok = site_snapshot.get("updated_count")
            raw_total = site_snapshot.get("active_count")
            try:
                ok = int(raw_ok or 0)
            except (TypeError, ValueError):
                ok = 0
            try:
                total = int(raw_total or 0)
            except (TypeError, ValueError):
                total = 0
            sites["tab_count"] = f"{ok}/{total} 正常" if total else ""

        storage = modules.get("persistent-storage")
        if storage is not None:
            percentages = []
            for row in storage_rows or []:
                for value in row:
                    match = re.search(r"(\d{1,3})%", str(value))
                    if match:
                        percentages.append(int(match.group(1)))
                        break
            storage["tab_count"] = f"{max(percentages)}%" if percentages else ""

        updates = modules.get("persistent-update")
        if updates is not None:
            updates["tab_count"] = _v7_update_label(update_rows)

    def _v7_active_tab(self, state: Any) -> str:
        """取当前页签键；缺少归一化实现时回落到总览，保证渲染永不因页签失败。"""
        raw = str((state or {}).get("active_tab") or "overview") if isinstance(state, dict) else "overview"
        normalizer = getattr(self, "_normalize_fusion_tab", None)
        if callable(normalizer):
            try:
                return str(normalizer(raw) or "overview")
            except Exception:
                return "overview"
        return "overview"

    def _v7_health_rows(self) -> List[List[str]]:
        """只读最近一次巡查结果：渲染期不触发新巡查也不写状态。"""
        try:
            data = self.get_data("last_health_check") or {}
        except Exception:
            return []
        if not isinstance(data, dict):
            return []
        if data.get("checks"):
            try:
                return self._v7_labeled_rows(self._format_health_report_lines(data))
            except Exception:
                return []
        lines = [line for line in str(data.get("output") or "").splitlines() if line.strip()]
        return self._v7_labeled_rows(lines)

    def _v7_task_output_lines(self, key: str) -> List[str]:
        """读取某个组件最近一次执行输出（原文行）。"""
        try:
            data = self.get_data(f"last_{key}") or {}
        except Exception:
            return []
        if not isinstance(data, dict):
            return []
        text = str(data.get("output") or data.get("message") or "")
        rows: List[str] = []
        for raw in text.splitlines():
            line = re.sub(r"^[\s⦁•·*\-✅⚠️\U0001F504\U0001F514]+", "", str(raw or "").strip()).strip()
            if line:
                rows.append(line)
        return rows

    def _v7_update_rows(self, state: Optional[Dict[str, Any]] = None) -> List[List[str]]:
        """更新管理明细：优先使用 update_jobs，旧文本只作迁移期回退。"""
        jobs = state.get("update_jobs") if isinstance(state, dict) else None
        if isinstance(jobs, dict) and jobs:
            visible = {str(job.get("kind") or ""): job for job in visible_jobs(jobs)}
            if not visible:
                return []
            rows = []
            mp = visible.get("mp_update") if isinstance(visible.get("mp_update"), dict) else {}
            if mp:
                phase = str(mp.get("phase") or "")
                if phase == "partial":
                    mp_value = f"部分成功｜后端 {mp.get('backend_version') or '未知'} · 前端 {mp.get('frontend_version') or '未知'}"
                elif phase == "available":
                    component = str(mp.get("target_component") or "").strip()
                    mp_value = f"有更新｜{component + ' ' if component else ''}最新 {mp.get('target_version') or '未知'}"
                    backend = str(mp.get("backend_version") or "").strip().lstrip("vV")
                    frontend = str(mp.get("frontend_version") or "").strip().lstrip("vV")
                    if backend and frontend and backend != frontend:
                        mp_value += f"｜后端 {mp.get('backend_version')} · 前端 {mp.get('frontend_version')}"
                elif phase in {"downloading", "installing"}:
                    mp_value = f"{mp.get('message') or '处理中'}｜{mp.get('progress') if mp.get('progress') is not None else 0}%"
                else:
                    mp_value = str(mp.get("error") or mp.get("message") or "暂无记录")
                rows.append(["MP 更新", mp_value])
            plugin = visible.get("plugin_update") if isinstance(visible.get("plugin_update"), dict) else {}
            if plugin:
                phase = str(plugin.get("phase") or "")
                if phase == "unconfigured":
                    plugin_value = "未配置插件市场"
                elif phase == "available":
                    plugin_value = f"可更新插件：{len(plugin.get('items') or [])}"
                elif phase in {"updating", "success"}:
                    plugin_value = str(plugin.get("message") or "正在更新")
                else:
                    plugin_value = str(plugin.get("error") or plugin.get("message") or "暂无记录")
                rows.append(["插件更新", plugin_value])
            market = visible.get("market_update") if isinstance(visible.get("market_update"), dict) else {}
            if market:
                rows.append(["插件库同步", str(market.get("error") or market.get("message") or "暂无记录")])
            if rows:
                return rows
        fallback = self._v7_component_rows(
            "_fusion_recent_task_lines", ["update_preview", "plugin_update_reminder", "market_update"])

        def fallback_row(index: int, label: str) -> List[str]:
            if index < len(fallback):
                return fallback[index]
            return [label, "暂无记录"]

        rows: List[List[str]] = []

        mp_output = self._v7_task_output_lines("update_preview")
        mp_lines = [ln for ln in mp_output
                    if ln.startswith(("后端", "前端"))]
        # 优先只保留「有更新/可更新/→」这类变化的行，和定稿模板一样保持一行；
        # 没有变化行时才退回展示本地版本行。
        mp_changed = [ln for ln in mp_lines if any(k in ln for k in ("有更新", "可更新", "→"))]
        # 一侧有更新不能遮住另一侧的检查错误。
        mp_errors = [ln for ln in mp_output if ln.startswith("更新检查：") or any(word in ln for word in ("异常", "失败"))]
        mp_detail = list(dict.fromkeys((mp_changed or mp_lines) + mp_errors))
        rows.append(["MP 更新", " · ".join(mp_detail)] if mp_detail else fallback_row(0, "MP 更新"))

        plugin_lines = self._v7_task_output_lines("plugin_update_reminder")
        discovered = next((ln for ln in plugin_lines if "可更新插件" in ln), "")
        plugin_detail = [ln for ln in plugin_lines if "→" in ln or ln.startswith("-") or ln.startswith("•")]
        plugin_cell = " · ".join([item for item in ([discovered] if discovered else []) + plugin_detail if item])
        rows.append(["插件更新", plugin_cell] if plugin_cell else fallback_row(1, "插件更新"))

        market_lines = self._v7_task_output_lines("market_update")
        market_cell = market_lines[1] if len(market_lines) > 1 else (market_lines[0] if market_lines else "")
        if market_cell:
            market_label = market_cell.split("：", 1)[0].strip() or "插件库同步"
            market_value = market_cell.split("：", 1)[1].strip() if "：" in market_cell else market_cell
            rows.append([market_label, market_value])
        else:
            rows.append(fallback_row(2, "插件库同步"))
        return rows

    def _v7_update_attention_rows(self, state: Optional[Dict[str, Any]] = None) -> List[List[str]]:
        """总览页「需要注意」用的逐项更新清单（系统后端/系统前端/插件·名称）。

        与系统页的「更新管理」不同：那里是合并成单行的摘要，这里是模板口径的逐项。
        """
        jobs = state.get("update_jobs") if isinstance(state, dict) else None
        if isinstance(jobs, dict) and jobs:
            jobs = {str(job.get("kind") or ""): job for job in visible_jobs(jobs)}
            if not jobs:
                return []
            rows = []
            mp = jobs.get("mp_update") if isinstance(jobs.get("mp_update"), dict) else {}
            if str(mp.get("phase") or "") in {"available", "ready", "downloading"}:
                component = str(mp.get("target_component") or "").strip()
                value = str(mp.get("target_version") or "有新版本")
                rows.append(["系统更新", f"{component} {value}".strip()])
            plugin = jobs.get("plugin_update") if isinstance(jobs.get("plugin_update"), dict) else {}
            if str(plugin.get("phase") or "") == "unconfigured":
                rows.append(["插件更新", "未配置插件市场"])
            elif str(plugin.get("phase") or "") == "available":
                for item in plugin.get("items") or []:
                    if isinstance(item, dict):
                        rows.append([f"插件·{item.get('name') or item.get('id') or '插件'}",
                                     f"v{item.get('old') or '?'} → v{item.get('new') or '?'}"])
            market = jobs.get("market_update") if isinstance(jobs.get("market_update"), dict) else {}
            if str(market.get("phase") or "") == "available":
                rows.append(["插件库同步", f"{len(market.get('items') or [])} 个待同步"])
            if rows:
                return rows
        rows = []
        lines = self._v7_task_output_lines("update_preview")
        local = {}
        for line in lines:
            match = re.match(r"^(后端|前端)本地：(.+)$", line)
            if match:
                local[match.group(1)] = match.group(2).strip()
        for side in ("后端", "前端"):
            match = next((re.match(rf"^{side}：有更新[｜|]最新\s*(.+)$", ln) for ln in lines if ln.startswith(side + "：")), None)
            if not match:
                continue
            newest = match.group(1).strip()
            old = local.get(side, "")
            rows.append([f"系统{side}", f"{old} → {newest}" if old else f"有更新｜最新 {newest}"])
        for line in self._v7_task_output_lines("plugin_update_reminder"):
            match = re.match(r"^[-•]?\s*(.+?)：([^：]+\s*→\s*.+)$", line)
            if match:
                rows.append([f"插件·{match.group(1).strip()}", match.group(2).strip()])
        return rows

    def _v7_component_rows(self, method: str, *args: Any, **kwargs: Any) -> List[List[str]]:
        """取某个组件原文并切成左右两列；取数或解析失败都只让该栏目为空，不影响整卡。"""
        handler = getattr(self, method, None)
        if not callable(handler):
            return []
        try:
            return self._v7_labeled_rows(handler(*args, **kwargs))
        except Exception:
            return []

    @staticmethod
    def _v7_column_lines(state: Dict[str, Any], column_key: str) -> List[str]:
        """从已刷新栏目里取出该组件原文的文本行。"""
        items = ((state.get("columns") or {}).get(column_key) or {}).get("items") or []
        rows: List[str] = []
        for item in items:
            for line in str(item.get("text") or "").splitlines():
                if line.strip():
                    rows.append(line)
        return rows

    def _v7_overview_rows(self, *, site_count: str, health_rows: List[List[str]], subscription_rows: List[List[str]],
                          storage_rows: List[List[str]], transfer_rows: List[List[str]],
                          maintenance_rows: List[List[str]], media_rows: List[List[str]],
                          update_rows: List[List[str]],
                          state: Optional[Dict[str, Any]] = None) -> List[List[str]]:
        """总览八宫格：全部数值都从已采集的真实行推导，缺数据写「无」。"""
        # 站点格子对齐定稿模板口径：「X/Y 正常」；site_count 形如「7/7已更新 · 7/7可统计」。
        site_value = "无"
        raw_count = str(site_count or "").strip()
        match = re.search(r"(\d+)\s*/\s*(\d+)\s*已更新", raw_count)
        if match:
            site_value = f"{match.group(1)}/{match.group(2)} 正常"
        elif raw_count:
            site_value = raw_count
        health_value = "无"
        for row in health_rows:
            joined = " ".join(str(x) for x in row)
            match = re.search(r"共\s*(\d+)\s*项[，,]\s*通过\s*(\d+)\s*项", joined)
            if match:
                health_value = f"{match.group(2)}/{match.group(1)} 通过"
                break
        storage_value = "无"
        pcts = []
        for row in storage_rows:
            for value in row:
                match = re.search(r"(\d{1,3})%", str(value))
                if match:
                    pcts.append(int(match.group(1)))
        if pcts:
            storage_value = f"{max(pcts)}%"
        maintenance_value = "无"
        if maintenance_rows:
            joined = " ".join(" ".join(str(x) for x in row) for row in maintenance_rows)
            maintenance_value = "今日无任务" if "暂无记录" in joined and "：成功" not in joined else f"{len(maintenance_rows)} 项"
        media_value = "暂无动态"
        if media_rows and not all("未取到" in " ".join(str(x) for x in row) for row in media_rows):
            # 只有真在播放、或真有新入库才算动态。播放结束、暂停、以及残留的采集记录
            # 一律显示「暂无动态」——没在放却写「有动态」只会让人误会。
            # 同时不复用「更新」这个词，它专指版本更新。
            activity_group = str((self._fusion_media_activity_report(state or {}) or {}).get("group") or "")
            if activity_group == "开始播放":
                media_value = "播放中"
            elif activity_group == "新入库":
                media_value = "有新入库"
        update_value = _v7_update_label(update_rows)
        return [
            ["📡 站点状态", site_value],
            ["❤️ 健康巡查", health_value],
            ["📺 订阅追新", f"{len(subscription_rows)} 部" if subscription_rows else "今日无追新"],
            ["💾 存储空间", storage_value],
            ["📥 下载入库", f"今日 {len(transfer_rows)} 个" if transfer_rows else "今日 0 个"],
            ["🔧 维护任务", maintenance_value],
            ["🎬 媒体动态", media_value],
            ["⬆️ 更新管理", update_value],
        ]

    @staticmethod
    def _v7_labeled_rows(lines: Any) -> List[List[str]]:
        """把组件原文行「⦁ 名称：值」切成左右两列行，供子表格渲染。"""
        rows: List[List[str]] = []
        for raw in lines or []:
            text = re.sub(r"^[\s⦁•·*\-✅⚠️]+", "", str(raw or "").strip()).strip()
            if not text:
                continue
            parts = re.split(r"[：:]", text, maxsplit=1)
            if len(parts) == 2:
                rows.append([parts[0].strip(), parts[1].strip()])
            else:
                rows.append([text, ""])
        return rows

    def _attach_site_metric_rows(self, model: Dict[str, Any], site_snapshot: Dict[str, Any]) -> None:
        """把站点指标附到站点模块，供站点栏目渲染使用（当前渲染只取名称/上传/下载）。

        只列有流量变化的有效站点；正常站点计数仍取完整采集结果，异常仍走 notice_rows。
        不为增加斑马纹行数展示零流量站点。
        """
        if not isinstance(model, dict):
            return
        target = next((item for item in model.get("modules") or [] if item.get("owner") == "persistent-sites"), None)
        if target is None:
            return
        metric_rows = []
        states = [item for item in (site_snapshot.get("site_states") or [])
                  if isinstance(item, dict) and item.get("status") == "ok"]
        for item in states:
            if not (item.get("upload") or item.get("download")):
                continue
            metric_rows.append([
                str(item.get("name") or item.get("domain") or "站点"),
                self._format_bytes(item.get("upload")),
                self._format_bytes(item.get("download")),
            ])
        target["metric_rows"] = metric_rows
        target["no_traffic_change"] = bool(states) and not metric_rows

    def _prepare_tg_console_v7_failure(self, state: Dict[str, Any], message: str) -> None:
        """Build a terminal card without calling the collector that just failed."""
        observed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        snapshot = {
            "identity": self._v7_identity(),
            "anomalies": [{
                "owner": "current-anomalies",
                "kicker": "当前异常",
                "count": "1 项",
                "primary": "融合卡采集未完成",
                "context": message,
                "meta": f"最近 {observed_at[5:16]}",
                "observed_at": observed_at,
                "details_rows": [["稍后使用刷新重试", observed_at[5:16]]],
                "affected_owners": [],
            }],
        }
        state["v7_snapshot"] = snapshot
        state["v7_state"] = "alert"
        state["v7_model"] = build_v7_card_model(snapshot, state="alert")

    @classmethod
    def _site_notice_detail(cls, item: Dict[str, Any], statistics_day: Any) -> str:
        # Do not repeat the same collection time as the last successful time.
        evidence = dict(item)
        if not cls._site_failure_at(item) and evidence.get("last_success_at") == evidence.get("snapshot_at"):
            evidence["last_success_at"] = ""
        detail = cls._site_state_detail(evidence)
        code = str(item.get("reason_code") or "")
        if code not in {"baseline_missing", "baseline_invalid", "baseline_discontinuous", "counter_reset"}:
            return detail
        try:
            yesterday = (datetime.strptime(str(statistics_day), "%Y-%m-%d") - timedelta(days=1)).strftime("%Y-%m-%d")
        except ValueError:
            return detail
        # This is the required comparison date, never a fabricated collection time.
        reference = f"昨日（{yesterday}）"
        reason = {
            "baseline_missing": f"缺少{reference}的记录",
            "baseline_invalid": f"{reference}的记录无效",
            "baseline_discontinuous": f"{reference}累计值低于更早记录",
            "counter_reset": f"今日累计值低于{reference}",
        }[code] + "，今日增量暂不可用"
        return detail.replace(cls.SITE_STAT_REASONS[code], reason, 1)

    def _record_site_diagnostic(self, state: Dict[str, Any], site_snapshot: Dict[str, Any], source: str) -> None:
        sites = sorted((item for item in site_snapshot.get("site_states") or [] if isinstance(item, dict)), key=lambda item: str(item.get("domain") or ""))
        semantics = [(item.get("domain", ""), item.get("status", ""), item.get("reason_code", ""), item.get("baseline_status", "")) for item in sites]
        fingerprint = hashlib.sha256(json.dumps(semantics, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()
        history = self._normalize_site_diagnostic(state.get("site_diagnostic"))
        if not history or history[-1]["fingerprint"] != fingerprint:
            history.append({"source": source, "observed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "fingerprint": fingerprint, "omitted_count": max(0, len(sites) - 50), "sites": sites[:50]})
        state["site_diagnostic"] = self._normalize_site_diagnostic(history)

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
    def _v7_anomaly_is_expired(item: Dict[str, Any], now: datetime) -> bool:
        """按落盘时间过滤过期失败；无时间戳的历史条目保持原样。"""
        stamp = str(item.get("observed_at") or "").strip()
        if not stamp:
            return False
        try:
            observed = datetime.strptime(stamp, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return False
        return (now - observed).total_seconds() > _V7_ANOMALY_TTL_SECONDS

    @classmethod
    def _merge_v7_anomalies(cls, state: Dict[str, Any], collector_anomalies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        stored = state.get("v7_anomalies") if isinstance(state.get("v7_anomalies"), dict) else {}
        now = datetime.now()
        items = [
            dict(item) for item in stored.values()
            if isinstance(item, dict) and not cls._v7_anomaly_is_expired(item, now)
        ]
        items.extend(dict(item) for item in collector_anomalies or [] if isinstance(item, dict))
        if not items:
            return []
        # Compare complete event timestamps, never the shortened display labels.
        # Older stored events without a timestamp remain unknown.
        for item in items:
            stamp = str(item.get("observed_at") or "")
            try:
                item["observed_at"] = datetime.strptime(stamp, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                item["observed_at"] = ""
        items.sort(key=lambda item: item["observed_at"], reverse=True)
        latest = items[0]["observed_at"]
        meta = f"最近 {latest[5:16]}" if latest else "异常时间未知"
        if len(items) == 1:
            items[0]["meta"] = meta if latest else str(items[0].get("meta") or meta)
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
            "meta": meta,
            "observed_at": latest,
            "affected_owners": affected,
            "details_rows": details,
        }]

    def _v7_identity(self) -> Dict[str, str]:
        version = str(getattr(self, "plugin_version", "3.1.1") or "3.1.1")
        # 与定稿模板一致：头部时间带日期（09-26 14:08），不是只有时分。
        return {"version": version if version.startswith("v") else f"v{version}",
                "refreshed_at": datetime.now().strftime("%m-%d %H:%M")}

    @staticmethod
    def _current_v7_realtime(state: Dict[str, Any]) -> List[Dict[str, Any]]:
        model = state.get("v7_model") if isinstance(state, dict) else None
        if isinstance(model, dict):
            return [dict(item) for item in model.get("modules") or [] if item.get("owner") in {"realtime-media", "realtime-task-backup"}]
        snapshot = state.get("v7_snapshot") if isinstance(state, dict) else None
        return [dict(item) for item in (snapshot or {}).get("realtime") or [] if isinstance(item, dict)]

    @classmethod
    def _current_v7_anomalies(cls, site_snapshot: Dict[str, Any], storage_lines: List[str]) -> List[Dict[str, Any]]:
        anomalies = []
        site_rows = []
        site_times = []
        ignored = {"ok", "baseline_missing", "baseline_invalid", "baseline_discontinuous", "counter_reset", "refresh_running"}
        for item in site_snapshot.get("site_states") or []:
            code = item.get("reason_code")
            if code in ignored:
                continue
            reason = cls.SITE_STAT_REASONS.get(code, "站点统计检查失败")
            detail = f"{item.get('name') or item.get('domain') or '站点'}：{reason}"
            if item.get("last_success_at"):
                detail += f"；最后成功 {item['last_success_at']}"
            failed_at = cls._site_failure_at(item)
            stamp = failed_at or cls._site_timestamp(item.get("snapshot_at"))
            site_times.append(stamp)
            time_label = "本次失败" if failed_at else "实际采集"
            site_rows.append([detail, f"{time_label} {stamp[5:16]}" if stamp else "采集时间未知"])
        if site_snapshot.get("error") and not site_rows:
            site_rows.append([f"站点统计检查失败：{site_snapshot['error']}", "采集时间未知"])
        if site_rows:
            latest = max(site_times, default="")
            anomalies.append({"owner": "current-anomalies", "kicker": "当前异常", "count": f"{len(site_rows)} 项",
                              "primary": "站点数据", "context": "需要关注 · 站点数据",
                              "meta": f"最近 {latest[5:16]}" if latest else "异常时间未知",
                              "observed_at": latest,
                              # Keep valid totals and site explanations visible alongside anomalies.
                              "affected_owners": [], "details_rows": site_rows})
        rows = []
        observed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for line in storage_lines or []:
            text = str(line or "")
            if "空间偏紧" in text or "检查异常" in text:
                rows.append([re.sub(r"^[\s⦁•]+", "", text), observed_at[5:16]])
        if rows:
            anomalies.append({
            "owner": "current-anomalies",
            "kicker": "当前异常",
            "count": f"{len(rows)} 项",
            "primary": "存储空间",
            "context": "需要关注 · 健康巡查",
            "meta": f"最近 {observed_at[5:16]}",
            "observed_at": observed_at,
            "affected_owners": ["persistent-storage"],
            "details_rows": rows,
            })
        return anomalies

    def _build_tg_console_reply_markup(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """按钮只放在卡片内（与定稿模板一致），消息键盘保持为空。

        卡片内 buttons 的回调数据已按宿主约定包装为 ``[PLUGIN]Signal|<payload>``，
        由 MoviePilot 的消息回调链路转给插件，因此无需额外挂消息键盘。
        """
        return {"inline_keyboard": []}

    def _build_tg_console_html(self, state: Dict[str, Any]) -> str:
        self._sanitize_fusion_media_activity_state(state)
        self._sanitize_fusion_update_state(state)
        now_label = datetime.now().strftime("%H:%M:%S")
        reports = state.get("reports") or {}
        fusion_report = reports.get("fusion_report") or {}
        fusion_text = str(fusion_report.get("text") or "")
        chunks = self._build_fusion_console_chunks(state, fusion_text, now_label)

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

    def _build_fusion_console_chunks(self, state: Dict[str, Any], fusion_text: str, now_label: str) -> List[str]:
        stamp = datetime.now().strftime("%Y-%m-%d") + f" {now_label}"
        greeting = self._fusion_greeting_locked()
        chunks = [
            f"<h2>📮 MP 融合汇报｜🕒 {self._html_escape(stamp)}</h2>",
            f"<p>{self._html_escape(greeting)}</p>",
            self._build_fusion_system_line(fusion_text, state),
        ]
        media_html = self._build_fusion_media_headline(state)
        if media_html:
            chunks.append(media_html)
        update_html = self._build_fusion_update_headline(state)
        if update_html:
            chunks.append(update_html)
        chunks.append("<p>───────────────────<br><i>💡 请点击下方的横向分类按钮，查阅今日具体运行指标。</i></p>")
        has_stream_data = bool((state.get("reports") or {}) or (state.get("columns") or {}) or fusion_text.strip() or state.get("tab_touched"))
        if has_stream_data:
            active_tab = self._normalize_fusion_tab(str(state.get("active_tab") or "subscribe_site"))
            chunks.append(self._build_fusion_tab_html(active_tab, state, fusion_text))
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

    def _build_fusion_system_line(self, fusion_text: str, state: Optional[Dict[str, Any]] = None) -> str:
        if not str(fusion_text or "").strip() and state:
            fusion_text = str(((state.get("reports") or {}).get("fusion_report") or {}).get("text") or "")
        version = self._fusion_version_label(fusion_text)
        normal, stale, failed, total = self._fusion_site_counts(fusion_text)
        if (not total or (total and normal == 0 and failed == 0 and stale == 0)) and state:
            normal, stale, failed, total = self._fusion_site_counts_from_state(state)
        pending_version = self._fusion_pending_update_label(state, fusion_text) if state else ""
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

    def _build_fusion_tab_html(self, tab_key: str, state: Dict[str, Any], fusion_text: str) -> str:
        category_key = self._normalize_fusion_tab(tab_key)
        category = next((x for x in self._fusion_category_registry() if x["key"] == category_key), None)
        if category:
            column_meta = {x["key"]: x for x in self._fusion_column_registry()}
            sections = []
            for child in self._fusion_category_children(category_key):
                meta = column_meta.get(child) or {}
                if child == "download_transfer":
                    today_lines, library_lines = self._fusion_download_transfer_groups(state, fusion_text)
                    sections.append(self._fusion_section_html("download_transfer", "📥 今日下载", today_lines))
                    sections.append(self._fusion_section_html("download_transfer", "📦 入库整理", library_lines))
                    continue
                lines = self._fusion_tab_lines(child, state, fusion_text)
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
        lines = self._fusion_tab_lines(tab_key, state, fusion_text)
        if not lines:
            lines = [f"暂无{meta['label']}数据"]
        title = f"{meta.get('icon') or ''} {meta.get('label') or tab_key}".strip()
        return self._fusion_section_html(tab_key, title, lines)

    def _fusion_download_transfer_groups(self, state: Dict[str, Any], fusion_text: str) -> Tuple[List[str], List[str]]:
        today = self._extract_report_section_items(fusion_text, ("今日下载",))
        library = self._extract_report_section_items(fusion_text, ("入库整理",))
        if today or library:
            return today, library
        lines = self._fusion_tab_lines("download_transfer", state, fusion_text)
        today_lines: List[str] = []
        library_lines: List[str] = []
        for line in lines:
            text = str(line or "")
            if "入库" in text or "整理" in text or "转移" in text:
                library_lines.append(text)
            else:
                today_lines.append(text)
        return today_lines, library_lines

    def _fusion_tab_lines(self, tab_key: str, state: Dict[str, Any], fusion_text: str) -> List[str]:
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
            return self._extract_report_section_items(fusion_text, ("站点状态", "站点增量"))
        if tab_key == "download_transfer":
            return self._extract_report_section_items(fusion_text, ("今日下载", "入库整理"))
        if tab_key == "subscribe":
            return self._extract_report_section_items(fusion_text, ("订阅追新",))
        if tab_key == "storage":
            return self._format_fusion_storage_items(self._extract_report_section_items(fusion_text, ("存储空间",)))
        if tab_key == "media":
            report = (state.get("reports") or {}).get("media_stat") or {}
            return self._clean_fusion_item_text_lines(str(report.get("text") or ""))
        if tab_key == "health":
            return self._extract_report_section_items(fusion_text, ("健康巡查",))
        return []

    @staticmethod
    def _clean_fusion_item_text_lines(text: str) -> List[str]:
        rows = []
        for raw in str(text or "").splitlines():
            line = re.sub(r"^[\s⦁•·*-]+", "", str(raw or "").strip()).strip()
            if line:
                rows.append(line)
        return rows

    def _build_tg_console_fusion_chunks(self, fusion_text: str) -> List[str]:
        parts = self._split_fusion_report_text(fusion_text)
        chunks = [f"<h2>{self._html_escape(parts.get('title') or 'Signal 融合汇报')}</h2>"]
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
                    site_html = self._build_tg_console_site_lights(fusion_text)
                    if site_html:
                        chunks.append(site_html)
                    appended_site = True
            elif header.startswith("📈"):
                chunks.append(self._telegram_details_html(header, self._telegram_increment_table("", lines)))
            elif header.startswith("📥") or header.startswith("📦") or header.startswith("📺"):
                chunks.append(self._telegram_details_html(header, self._telegram_general_list_html(header, self._telegram_section_items(lines))))
            elif header.startswith("💾"):
                if not appended_storage:
                    storage_html = self._build_tg_console_storage_matrix(fusion_text)
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
            site_html = self._build_tg_console_site_lights(fusion_text)
            if site_html:
                chunks.append(site_html)
        if not appended_storage:
            storage_html = self._build_tg_console_storage_matrix(fusion_text)
            if storage_html:
                chunks.append(storage_html)
        return chunks

    def _build_tg_console_core_badges(self, reports: Dict[str, Any], fusion_text: str = "") -> str:
        version = self._match_text(r"(?:当前版本|版本)[:：]\s*([^\n]+)", fusion_text) or "MoviePilot"
        update_status = self._match_text(r"(?:最新版本|更新状态)[:：]\s*([^\n]+)", fusion_text) or "记录抽空更新"
        health_section = reports.get("health_check") or {}
        health_text = str(health_section.get("text") or "")
        health_line = self._match_text(r"状态[:：]\s*([^\n]+)", health_text) or self._match_text(r"健康巡查[:：]\s*([^\n]+)", fusion_text) or "等待巡查"
        health_icon = "🟢" if ("全部正常" in health_text or "异常 0" in health_text or "全部正常" in fusion_text) else "🟡"
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

    def _build_tg_console_storage_matrix(self, fusion_text: str) -> str:
        items = self._extract_report_section_items(fusion_text, ("存储空间",))
        if not items:
            return ""
        normalized = []
        for item in items[:8]:
            text = re.sub(r"^\s*[•\-\s]+", "", str(item or "").strip())
            if text:
                normalized.append(f"📁 {text}")
        return self._telegram_details_html("💾 存储空间", self._telegram_list_html(normalized))

    def _build_tg_console_site_lights(self, fusion_text: str) -> str:
        items = self._extract_report_section_items(fusion_text, ("站点状态",))
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

    def _build_tg_console_footer(self, fusion_text: str, time_label: str = "") -> str:
        media_items = self._extract_report_section_items(fusion_text, ("媒体统计",))
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
