import re
import os
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from app.log import logger
from app.schemas import NotificationType

from ..domain.fusion_composition import media_playback_url, media_session_ip
from ..domain.fusion_stream import apply_v7_realtime_update



class TgConsoleFusionMixin:
    """Telegram fusion card column/category logic, media activity, site counts, update state"""

    def _sync_v7_stream_owner(self, state: Dict[str, Any], owner: str, module: Optional[Dict[str, Any]] = None, *, active: bool = True) -> None:
        """Mutate only one realtime owner before the persistent card edit."""
        model = state.get("v7_model") if isinstance(state, dict) else None
        if isinstance(model, dict):
            state["v7_model"] = apply_v7_realtime_update(model, owner, module, active=active)
            state["v7_state"] = "active" if state["v7_model"].get("modules") else "normal"
            return
        snapshot = state.setdefault("v7_snapshot", {})
        realtime = [item for item in list(snapshot.get("realtime") or []) if isinstance(item, dict) and item.get("owner") != owner]
        if active and isinstance(module, dict):
            realtime.append(dict(module))
        snapshot["realtime"] = realtime
        state["v7_state"] = "active" if realtime else "normal"

    @staticmethod
    def _v7_stream_module(owner: str, title: str, text: str, level: str = "info", payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        data = payload if isinstance(payload, dict) else {}
        return {
            "owner": owner,
            "tier": "realtime",
            "kind": "realtime",
            "kicker": str(data.get("kicker") or ("媒体播放" if owner == "realtime-media" else "配置备份")),
            "count": str(data.get("count") or "1 个会话" if owner == "realtime-media" else "1 个任务"),
            "primary": str(data.get("primary") or title or ("媒体活动" if owner == "realtime-media" else "执行中")),
            "status": str(data.get("status") or level or "进行中"),
            "context": str(data.get("context") or text or ""),
            "meta": str(data.get("meta") or datetime.now().strftime("%H:%M:%S")),
            "progress": str(data.get("progress") or ""),
            "session_ip": str(data.get("session_ip") or ""),
            "playback_url": str(data.get("playback_url") or ""),
            "details_rows": list(data.get("details_rows") or []),
            "preview_rows": [],
            "always_visible_preview": False,
            "streaming": True,
        }

    def _fusion_media_event_enabled(self, group: str, server_name: Any = None) -> bool:
        if not self._tg_console_enabled or not self._fusion_notify_enabled:
            return False
        enabled_columns = set(self._fusion_notify_columns or [x["key"] for x in self._fusion_column_registry()])
        if "media" not in enabled_columns:
            return False
        if group not in {"开始播放", "暂停播放", "停止播放"}:
            return False
        if self._msgnotify_servers and server_name and server_name not in self._msgnotify_servers:
            return False
        return True

    @classmethod
    def _msg_group_of(cls, etype):
        if not etype:
            return None
        for group, members in cls._MSG_GROUPS.items():
            if etype in members:
                return group
        return None

    def _msg_dedupe(self, key: str) -> bool:
        """30 秒内重复事件返回 False（不再通知）；新事件返回 True 并记录。"""
        now = datetime.now().timestamp()
        seen = self._msg_seen if isinstance(self._msg_seen, dict) else {}
        for k in [k for k, ts in seen.items() if now - ts > 30]:
            seen.pop(k, None)
        if key in seen:
            return False
        seen[key] = now
        self._msg_seen = seen
        return True

    def _msg_title(self, group: str, info: Any) -> str:
        action = self._MSG_LABEL.get(group, group)
        item_type = getattr(info, "item_type", "") or ""
        name = getattr(info, "item_name", "") or ""
        if item_type in ("TV", "SHOW"):
            return f"{action}剧集 {name}".strip()
        if item_type == "MOV":
            return f"{action}电影 {name}".strip()
        if item_type == "AUD":
            return f"{action}有声书 {name}".strip()
        return action

    @staticmethod
    def _msg_text(info: Any) -> str:
        parts = []
        user = getattr(info, "user_name", None)
        if user:
            parts.append(f"用户：{user}")
        device = getattr(info, "device_name", None)
        client = getattr(info, "client", None)
        if device:
            parts.append(f"设备：{(client or '')} {device}".strip())
        elif client:
            parts.append(f"设备：{client}")
        ip = getattr(info, "ip", None)
        if ip:
            parts.append(f"IP地址：{ip}")
        pct = getattr(info, "percentage", None)
        if pct:
            try:
                parts.append(f"进度：{round(float(pct), 2)}%")
            except (ValueError, TypeError):
                pass
        parts.append("时间：" + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return "\n".join(parts)

    def _emit_console_media_activity(self, group: str, info: Any, title: str = "") -> bool:
        if not self._tg_console_enabled:
            return False
        token, chat_id, _source = self._resolve_daily_report_telegram_config()
        if not token or not chat_id:
            self._tg_console_last_error = "Telegram 融合汇报卡 Bot Token/Chat ID 未配置"
            state = self._tg_console_state(chat_id=chat_id)
            state["last_error"] = self._tg_console_last_error
            self._save_tg_console_state(state)
            return False
        state = self._tg_console_state(chat_id=chat_id)
        if not state.get("message_id"):
            state["last_error"] = "融合通知当前没有可更新的 active card"
            self._save_tg_console_state(state)
            return False
        media_payload = self._v7_media_payload(group, info, title)
        item = {
            "title": "媒体动态",
            "group": str(group or ""),
            "text": " · ".join(item for item in (media_payload.get("context"), media_payload.get("status")) if item),
            "raw_title": str(title or ""),
            "level": "idle" if group in {"暂停播放", "停止播放"} else "info",
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "time": datetime.now().strftime("%H:%M:%S"),
        }
        state.setdefault("reports", {})["media_activity"] = dict(item)
        self._sync_v7_stream_owner(
            state,
            "realtime-media",
            self._v7_stream_module(
                "realtime-media",
                media_payload["primary"],
                item["text"],
                item["level"],
                media_payload,
            ),
            active=group != "停止播放",
        )
        media_col = (state.setdefault("columns", {}).get("media") or {})
        media_items = media_col.get("items") if isinstance(media_col, dict) else []
        if isinstance(media_items, list):
            kept_items = [row for row in media_items if not self._is_fusion_media_activity(row)]
            if kept_items:
                state.setdefault("columns", {})["media"] = {"items": kept_items, "updated_at": media_col.get("updated_at") or item["updated_at"]}
            else:
                state.setdefault("columns", {}).pop("media", None)
        try:
            ok = self._tg_console_upsert_card(token, chat_id, state)
        except Exception as err:
            self._tg_console_last_error = f"Telegram 融合通知媒体动态更新异常：{self._telegram_safe_error(err, limit=500)}"
            state["last_error"] = self._tg_console_last_error
            self._save_tg_console_state(state)
            logger.warning(f"Signal {self._tg_console_last_error}")
            return False
        if ok:
            self._tg_console_last_error = ""
            state["last_error"] = ""
        self._save_tg_console_state(state)
        return ok

    @classmethod
    def _v7_media_payload(cls, group: str, info: Any, title: str = "") -> Dict[str, Any]:
        def first(*names: str) -> str:
            for name in names:
                value = getattr(info, name, None)
                if value not in (None, ""):
                    return str(value).strip()
            return ""

        primary = first("item_name", "title", "media_name") or str(title or "媒体活动").strip()
        player = first("user_name", "username", "player_name")
        device = first("device_name", "device")
        mode = first("play_mode", "play_method", "streaming_method", "transcode_decision") or first("client")
        context = " · ".join(item for item in (player, device, mode) if item)
        percentage = cls._media_percentage(getattr(info, "percentage", None))
        status_label = {"开始播放": "播放中", "暂停播放": "已暂停", "停止播放": "已停止"}.get(str(group or ""), str(group or "播放中"))
        status = " · ".join(item for item in (status_label, percentage) if item)
        elapsed = cls._media_duration(first("elapsed", "position", "playback_position", "view_offset"))
        total = cls._media_duration(first("duration", "total_duration", "item_duration", "runtime"))
        meta = " / ".join(item for item in (elapsed, total) if item)
        session_ip = media_session_ip(info)
        playback_url = media_playback_url(info)
        return {
            "kicker": "媒体播放",
            "count": "1 个会话",
            "primary": primary,
            "status": status,
            "context": context,
            "meta": meta,
            "progress": cls._media_progress_bar(percentage),
            "session_ip": session_ip,
            "playback_url": playback_url,
            "details_rows": [],
        }

    @staticmethod
    def _media_percentage(value: Any) -> str:
        try:
            number = max(0.0, min(100.0, float(value)))
        except (TypeError, ValueError):
            return ""
        return f"{number:.0f}%" if number.is_integer() else f"{number:.1f}%"

    @staticmethod
    def _media_progress_bar(percentage: str) -> str:
        try:
            filled = max(0, min(10, round(float(str(percentage).rstrip("%")) / 10)))
        except (TypeError, ValueError):
            filled = 0
        return "▰" * filled + "▱" * (10 - filled)

    @staticmethod
    def _media_duration(value: Any) -> str:
        text = str(value or "").strip()
        if not text:
            return ""
        if ":" in text:
            return text
        try:
            seconds = int(float(text))
            if seconds > 100000:
                seconds //= 1000
        except (TypeError, ValueError):
            return ""
        hours, remainder = divmod(max(0, seconds), 3600)
        minutes, secs = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}" if hours else f"{minutes:02d}:{secs:02d}"

    def _format_media_console_text(self, group: str, info: Any) -> str:
        item_type = getattr(info, "item_type", "") or ""
        type_label = "剧集" if item_type in ("TV", "SHOW") else ("电影" if item_type == "MOV" else ("有声书" if item_type == "AUD" else "媒体"))
        name = str(getattr(info, "item_name", "") or "").strip() or "未命名媒体"
        user = str(getattr(info, "user_name", "") or "").strip()
        device = " ".join(x for x in [str(getattr(info, "client", "") or "").strip(), str(getattr(info, "device_name", "") or "").strip()] if x)
        ip_label = self._format_media_ip_label(getattr(info, "ip", ""))
        pct = getattr(info, "percentage", None)
        pct_text = ""
        if pct:
            try:
                pct_text = f"{round(float(pct), 2)}%"
            except (ValueError, TypeError):
                pct_text = ""
        if group == "停止播放":
            lines = [f"停止播放{type_label} {name}"]
        elif group == "暂停播放":
            lines = [f"暂停播放{type_label} {name}"]
        elif group == "开始播放":
            lines = [f"开始播放{type_label} {name}"]
        elif group == "新入库":
            lines = [f"新入库：{type_label}《{name}》"]
        elif group in {"登录成功", "登录失败"}:
            lines = [f"{group}：{user or '未知用户'}"]
        else:
            lines = [f"{group or '媒体事件'}：{type_label}《{name}》"]
        if device:
            lines.append(f"设备：{device}")
        if user and group not in {"登录成功", "登录失败"}:
            lines.append(f"用户：{user}")
        if ip_label:
            lines.append(f"IP地址：{ip_label}")
        if pct_text:
            lines.append(f"进度：{pct_text}")
        lines.append("时间：" + datetime.now().strftime("%H:%M:%S"))
        return "\n".join(lines)

    def _emit_console_notice(self, title: str, text: str = "", level: str = "info") -> bool:
        if not self._fusion_notify_enabled:
            return False
        return self._emit_fusion_notice(self._fusion_column_for_title(title), title, text, level=level)

    def _emit_console_report(self, section_key: str, title: str, text: str = "", level: str = "info") -> bool:
        return self._emit_fusion_notice(section_key, title, text, level=level)

    def _refresh_fusion_card(self, daily_text: str = "", live_result: Optional[Dict[str, Any]] = None) -> bool:
        if not self._fusion_notify_enabled:
            return False
        token, chat_id, _source = self._resolve_daily_report_telegram_config()
        if not token or not chat_id:
            self._tg_console_last_error = "Telegram 融合通知 Bot Token/Chat ID 未配置"
            state = self._tg_console_state(chat_id=chat_id)
            state["last_error"] = self._tg_console_last_error
            self._save_tg_console_state(state)
            return False
        state = self._tg_console_state(chat_id=chat_id)
        if not state.get("message_id"):
            state["last_error"] = "融合通知当前没有可刷新的 active card"
            self._save_tg_console_state(state)
            return False
        self._tg_console_set_report_section(state, "daily_report", "立即刷新", daily_text, level="success")
        previous_context = getattr(self, "_fusion_refresh_context", None)
        self._fusion_refresh_context = {"live_result": live_result or {}}
        try:
            self._refresh_fusion_columns(state)
            self._compose_tg_console_v7_model(state)
        finally:
            if previous_context is None:
                try:
                    delattr(self, "_fusion_refresh_context")
                except Exception:
                    pass
            else:
                self._fusion_refresh_context = previous_context
        try:
            ok = self._tg_console_upsert_card(token, chat_id, state)
        except Exception as err:
            self._tg_console_last_error = f"Telegram 融合通知全量刷新异常：{self._telegram_safe_error(err, limit=500)}"
            state["last_error"] = self._tg_console_last_error
            self._save_tg_console_state(state)
            logger.warning(f"Signal {self._tg_console_last_error}")
            return False
        if ok:
            self._tg_console_last_error = ""
            state["last_error"] = ""
        self._save_tg_console_state(state)
        return ok

    def _refresh_fusion_columns(self, state: Dict[str, Any]) -> bool:
        valid_columns = {x["key"] for x in self._fusion_column_registry()}
        enabled = set(self._fusion_notify_columns or valid_columns) & valid_columns
        ok = True
        for item in self._fusion_column_registry():
            key = item["key"]
            if key not in enabled:
                continue
            try:
                ok = bool(self._refresh_fusion_column(key, state)) and ok
            except Exception as err:
                ok = False
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                state.setdefault("columns", {})[key] = {
                    "items": [{
                        "title": item.get("label") or key,
                        "text": f"栏目刷新失败：{err}",
                        "level": "error",
                        "time": now[11:],
                        "updated_at": now,
                    }],
                    "updated_at": now,
                }
        return ok

    def _refresh_fusion_column(self, key: str, state: Dict[str, Any]) -> bool:
        column_key = self._normalize_fusion_column(key)
        meta = next((x for x in self._fusion_column_registry() if x["key"] == column_key), None)
        if not meta:
            return False
        title, text, level = self._fusion_column_snapshot(column_key, state)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        item = {
            "title": title or meta.get("label") or column_key,
            "text": text or f"暂无{meta.get('label') or column_key}数据",
            "level": level or "info",
            "time": now[11:],
            "updated_at": now,
        }
        columns = state.setdefault("columns", {})
        columns[column_key] = {"items": [item], "updated_at": now}
        reports = state.setdefault("reports", {})
        reports[self._fusion_report_key(column_key)] = dict(item)
        return True

    def _refresh_fusion_category(self, key: str, state: Dict[str, Any]) -> bool:
        valid_columns = {x["key"] for x in self._fusion_column_registry()}
        enabled = set(self._fusion_notify_columns or valid_columns) & valid_columns
        children = [child for child in self._fusion_category_children(key) if child in enabled]
        if not children:
            return False
        ok = True
        for child in children:
            ok = bool(self._refresh_fusion_column(child, state)) and ok
        return ok

    def _tg_console_set_report_section(self, state: Dict[str, Any], section_key: str, title: str, text: str = "", level: str = "info") -> None:
        key = str(section_key or "").strip() or "general"
        reports = state.setdefault("reports", {})
        reports[key] = {
            "title": str(title or key).strip()[:120],
            "text": str(text or "").strip()[:20000],
            "level": str(level or "info"),
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "time": datetime.now().strftime("%H:%M:%S"),
        }
        if key == "daily_report":
            return
        column_key = self._normalize_fusion_column(key)
        columns = state.setdefault("columns", {})
        columns[column_key] = {
            "items": [{
                "title": str(title or key).strip()[:120],
                "text": str(text or "").strip()[:20000],
                "level": str(level or "info"),
                "time": datetime.now().strftime("%H:%M:%S"),
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }],
            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    def _tg_console_record_notice_section(self, state: Dict[str, Any], notice: Dict[str, Any]) -> None:
        title = str((notice or {}).get("title") or "")
        if title.startswith("TG 远控") or title.startswith("TG 指令"):
            return
        section_map = [
            ("订阅追新", "subscribe_reminder", "订阅追新"),
            ("站点统计", "site_stat", "站点统计"),
            ("健康巡查", "health_check", "健康巡查"),
        ]
        for needle, key, label in section_map:
            if needle in title:
                self._tg_console_set_report_section(state, key, label, str((notice or {}).get("text") or ""), level=str((notice or {}).get("level") or "info"))
                return

    @staticmethod
    def _fusion_column_registry() -> List[Dict[str, str]]:
        return [
            {"key": "site_stats", "label": "站点统计", "icon": "📊", "component": "站点数据统计"},
            {"key": "download_transfer", "label": "下载入库", "icon": "📥", "component": "下载器管理"},
            {"key": "subscribe", "label": "订阅追新", "icon": "📺", "component": "订阅管理"},
            {"key": "storage", "label": "存储空间", "icon": "💾", "component": "健康巡查"},
            {"key": "media", "label": "媒体动态", "icon": "🎬", "component": "媒体通知"},
            {"key": "health", "label": "健康巡查", "icon": "🩺", "component": "健康巡查"},
            {"key": "maintenance", "label": "维护任务", "icon": "🧰", "component": "系统维护"},
        ]

    @staticmethod
    def _fusion_category_registry() -> List[Dict[str, Any]]:
        return [
            {"key": "subscribe_site", "label": "订阅与站点", "icon": "📊", "children": ["site_stats", "subscribe"]},
            {"key": "download_media", "label": "下载与媒体", "icon": "📥", "children": ["download_transfer", "media"]},
            {"key": "system_health", "label": "健康巡查", "icon": "🩺", "children": ["health"]},
            {"key": "system_maintenance", "label": "系统维护", "icon": "🧰", "children": ["storage", "maintenance"]},
        ]

    @classmethod
    def _fusion_category_for_column(cls, key: str) -> Optional[str]:
        column_key = cls._normalize_fusion_column(key)
        for category in cls._fusion_category_registry():
            if column_key in list(category.get("children") or []):
                return str(category.get("key") or "")
        return None

    @classmethod
    def _normalize_fusion_tab(cls, key: str) -> str:
        raw = str(key or "").strip()
        category_keys = {x["key"] for x in cls._fusion_category_registry()}
        if raw in category_keys:
            return raw
        return cls._fusion_category_for_column(raw) or "subscribe_site"

    @classmethod
    def _fusion_category_children(cls, key: str) -> List[str]:
        category_key = cls._normalize_fusion_tab(key)
        category = next((x for x in cls._fusion_category_registry() if x["key"] == category_key), None)
        return [str(x) for x in ((category or {}).get("children") or []) if str(x)]

    @classmethod
    def _fusion_enabled_categories(cls, enabled_columns: set) -> List[Dict[str, Any]]:
        enabled = set(enabled_columns or [])
        return [
            category for category in cls._fusion_category_registry()
            if any(child in enabled for child in (category.get("children") or []))
        ]

    @classmethod
    def _normalize_fusion_column(cls, key: str) -> str:
        aliases = {
            "daily_report": "site_stats",
            "site_stat": "site_stats",
            "today_transfer": "download_transfer",
            "run_today_transfer": "download_transfer",
            "subscribe_reminder": "subscribe",
            "subfill": "subscribe",
            "media_activity": "media",
            "media_stat": "media",
            "realtime-media": "media",
            "health_check": "health",
            "current-anomalies": "health",
            "persistent-sites": "site_stats",
            "persistent-storage": "storage",
            "persistent-subscriptions": "subscribe",
            "realtime-task-backup": "maintenance",
            "today-completion": "maintenance",
            "mp_update": "maintenance",
            "market_update": "maintenance",
            "update_preview": "maintenance",
            "backup": "maintenance",
            "log_clean": "maintenance",
            "plugin_uninstall": "maintenance",
            "seed_clean": "maintenance",
            "downloader_tag": "maintenance",
            "downloader_helper": "maintenance",
        }
        raw = str(key or "").strip()
        known = {x["key"] for x in cls._fusion_column_registry()}
        return raw if raw in known else aliases.get(raw, "maintenance")

    @classmethod
    def _fusion_column_for_title(cls, title: str) -> str:
        text = str(title or "")
        checks = [
            ("站点", "site_stats"),
            ("今日入库", "download_transfer"),
            ("入库", "download_transfer"),
            ("下载", "download_transfer"),
            ("订阅", "subscribe"),
            ("存储", "storage"),
            ("媒体", "media"),
            ("播放", "media"),
            ("健康巡查", "health"),
            ("更新", "maintenance"),
            ("备份", "maintenance"),
            ("日志", "maintenance"),
            ("插件卸载", "maintenance"),
            ("自动删种", "maintenance"),
            ("种子打标签", "maintenance"),
        ]
        for needle, key in checks:
            if needle in text:
                return key
        return "maintenance"

    def _fusion_version_label(self, daily_text: str) -> str:
        line = self._match_text(r"当前版本[:：]\s*([^\n]+)", daily_text)
        if line:
            backend = self._match_text(r"后端\s*([vV]?\d+(?:\.\d+){1,3}(?:[-\w.]*)?)", line)
            frontend = self._match_text(r"前端\s*([vV]?\d+(?:\.\d+){1,3}(?:[-\w.]*)?)", line)
            return backend or frontend or line
        local = self._get_local_versions()
        return str(local.get("backend_version") or local.get("frontend_version") or "MoviePilot")

    def _fusion_site_counts(self, daily_text: str) -> Tuple[int, int, int, int]:
        items = self._extract_report_section_items(daily_text, ("站点状态",))
        if not items:
            text = str(daily_text or "")
            match = re.search(r"全部\s*(\d+)\s*个站点正常", text)
            if match:
                total = int(match.group(1))
                return total, 0, 0, total
            match = re.search(r"站点[:：]\s*(?:共\s*)?(\d+)\s*个(?:[，,｜|]\s*启用\s*(\d+)\s*个)?", text)
            if match:
                total = int(match.group(2) or match.group(1))
                return total, 0, 0, total
            return 0, 0, 0, 0
        normal = stale = failed = 0
        for item in items:
            text = str(item or "")
            all_normal = re.search(r"全部\s*(\d+)\s*个站点正常", text)
            if all_normal:
                normal += int(all_normal.group(1))
            elif match := re.search(r"正常\s*(\d+)\s*个站点", text):
                normal += int(match.group(1))
            elif "异常" in text or "失败" in text or "Cookie" in text or "失联" in text:
                failed += 1
            elif "过期" in text:
                stale += 1
            else:
                normal += 1
        total = normal + stale + failed
        return normal, stale, failed, total

    def _fusion_site_counts_from_state(self, state: Dict[str, Any]) -> Tuple[int, int, int, int]:
        candidates: List[str] = []
        reports = (state or {}).get("reports") or {}
        report_site = reports.get("site_status") or reports.get("daily_report") or {}
        if isinstance(report_site, dict):
            candidates.append(str(report_site.get("text") or ""))
        for key in ("health_check", "health"):
            report = reports.get(key) or {}
            if isinstance(report, dict):
                candidates.append(str(report.get("text") or ""))
        for key in ("health", "health_check"):
            items = (((state or {}).get("columns") or {}).get(key) or {}).get("items") or []
            for item in items:
                if isinstance(item, dict):
                    candidates.append(str(item.get("text") or item.get("title") or ""))
        try:
            health_state = self.get_data("last_health_check") or {}
        except Exception:
            health_state = {}
        if isinstance(health_state, dict):
            candidates.append(str(health_state.get("output") or ""))
            candidates.append(str(health_state.get("text") or ""))
            for check in health_state.get("checks") or []:
                if not isinstance(check, dict):
                    continue
                name = str(check.get("name") or check.get("title") or "")
                detail = str(check.get("detail") or check.get("text") or "")
                if name == "sites" or "站点" in name:
                    candidates.append(f"站点：{detail}")
        try:
            last_report = self.get_data("last_daily_report") or {}
        except Exception:
            last_report = {}
        if isinstance(last_report, dict):
            candidates.append(str(last_report.get("preview") or last_report.get("text") or ""))
        for text in candidates:
            parsed = self._fusion_site_counts(text)
            if parsed[3]:
                return parsed
        return 0, 0, 0, 0

    def _fusion_has_pending_moviepilot_update(self, state: Optional[Dict[str, Any]]) -> bool:
        return bool(self._fusion_pending_update_label(state, ""))

    def _sanitize_fusion_update_state(self, state: Optional[Dict[str, Any]]) -> bool:
        if not isinstance(state, dict):
            return False
        has_pending = bool(self._fusion_pending_update_label(state, ""))
        changed = False
        if not has_pending:
            for container_key in ("reports", "columns"):
                container = state.get(container_key)
                if isinstance(container, dict):
                    for key in ("updates", "update_preview"):
                        if key in container:
                            container.pop(key, None)
                            changed = True
            actions = state.get("pending_actions")
            if isinstance(actions, dict):
                for nonce, action in list(actions.items()):
                    if isinstance(action, dict) and action.get("action") == "run_mp_update_apply":
                        actions.pop(nonce, None)
                        changed = True
        return changed

    def _fusion_current_version_for_update_check(self, check: Dict[str, Any]) -> str:
        local = self._get_local_versions()
        label = str(check.get("type") or check.get("label") or check.get("name") or "").lower()
        if "前端" in label or "frontend" in label:
            return str(local.get("frontend_version") or check.get("local_version") or "")
        if "后端" in label or "backend" in label:
            return str(local.get("backend_version") or check.get("local_version") or "")
        return str(local.get("backend_version") or local.get("frontend_version") or check.get("local_version") or "")

    @classmethod
    def _fusion_version_newer(cls, latest: Any, current: Any) -> bool:
        latest_nums = cls._version_nums(latest)
        current_nums = cls._version_nums(current)
        if not latest_nums:
            return False
        if not current_nums:
            return True
        return latest_nums > current_nums

    def _fusion_text_pending_update_label(self, text: str) -> str:
        raw = str(text or "")
        if not raw or not any(key in raw for key in ("有更新", "新版", "可更新")):
            return ""
        if not any(key in raw for key in ("MoviePilot", "MP 更新", "后端", "前端", "backend", "frontend")):
            return ""
        versions = re.findall(r"v\d+(?:\.\d+){1,3}(?:[-\w.]*)?", raw, re.I)
        if not versions:
            return "有新版"
        local = self._get_local_versions()
        current_versions = [local.get("backend_version"), local.get("frontend_version")]
        if any(self._fusion_version_newer(version, current) for version in versions for current in current_versions if current):
            newer = [version for version in versions if any(self._fusion_version_newer(version, current) for current in current_versions if current)]
            return self._unique_keep_order(newer)[-1] if newer else versions[-1]
        if not any(self._version_nums(current) for current in current_versions if current):
            return versions[-1]
        return ""

    def _fusion_pending_update_label(self, state: Optional[Dict[str, Any]], daily_text: str = "") -> str:
        if not isinstance(state, dict):
            return ""
        candidates: List[Any] = []
        reports = state.get("reports") or {}
        columns = state.get("columns") or {}
        for container in (reports, columns):
            if not isinstance(container, dict):
                continue
            update = container.get("updates") or container.get("update_preview") or {}
            if isinstance(update, dict):
                candidates.append(update)
                for item in update.get("items") or []:
                    candidates.append(item)
        for candidate in candidates:
            if not isinstance(candidate, dict):
                continue
            data = candidate.get("data") if isinstance(candidate.get("data"), dict) else candidate
            mp = data.get("moviepilot") if isinstance(data, dict) else {}
            if isinstance(mp, dict) and mp.get("has_update"):
                checks = mp.get("checks") or []
                versions = []
                for check in checks:
                    if not isinstance(check, dict) or not check.get("has_update"):
                        continue
                    latest = str(check.get("latest_version") or "").strip()
                    if latest and self._fusion_version_newer(latest, self._fusion_current_version_for_update_check(check)):
                        versions.append(latest)
                if versions:
                    return " / ".join(self._unique_keep_order(versions))
                if checks:
                    continue
            text = "\n".join(str(candidate.get(k) or "") for k in ("title", "text", "msg", "message"))
            pending = self._fusion_text_pending_update_label(text)
            if pending:
                return pending
        return self._fusion_text_pending_update_label(str(daily_text or ""))

    def prune_fusion_media_activity(self) -> bool:
        ok, _ = self._runtime_gate("scheduler", component="fusion_notify", name="FusionMediaActivityPrune")
        if not ok:
            return False
        if not self._tg_console_enabled:
            return False
        token, chat_id, _source = self._resolve_daily_report_telegram_config()
        state = self._tg_console_state(chat_id=chat_id)
        if not self._prune_fusion_media_activity_state(state):
            return False
        self._save_tg_console_state(state)
        if not token or not chat_id or not state.get("message_id"):
            return True
        try:
            return bool(self._tg_console_upsert_card(token, chat_id, state))
        except Exception as err:
            self._tg_console_last_error = f"Telegram 融合通知媒体动态清理异常：{self._telegram_safe_error(err, limit=500)}"
            state["last_error"] = self._tg_console_last_error
            self._save_tg_console_state(state)
            logger.warning(f"Signal {self._tg_console_last_error}")
            return False

    @classmethod
    def _fusion_media_activity_report(cls, state: Dict[str, Any]) -> Dict[str, Any]:
        reports = (state or {}).get("reports") or {}
        media = reports.get("media_activity") or {}
        if cls._is_fusion_media_activity(media):
            return media
        items = (((state or {}).get("columns") or {}).get("media") or {}).get("items") or []
        for item in items:
            if cls._is_fusion_media_activity(item):
                return item
        return {}

    @classmethod
    def _sanitize_fusion_media_activity_state(cls, state: Dict[str, Any]) -> bool:
        if not isinstance(state, dict):
            return False
        changed = False
        reports = state.get("reports") or {}
        removed_invalid_report = False
        if isinstance(reports, dict):
            media = reports.get("media_activity")
            if media is not None and not cls._is_fusion_media_activity(media):
                reports.pop("media_activity", None)
                removed_invalid_report = True
                changed = True
        columns = state.get("columns") or {}
        if isinstance(columns, dict):
            media_col = columns.get("media") or {}
            items = media_col.get("items") if isinstance(media_col, dict) else None
            if removed_invalid_report and items and not any(cls._is_fusion_media_activity(item) for item in items):
                columns.pop("media", None)
                changed = True
        return changed

    @classmethod
    def _prune_fusion_media_activity_state(cls, state: Dict[str, Any], ttl_seconds: int = 300) -> bool:
        if not isinstance(state, dict):
            return False
        media = cls._fusion_media_activity_report(state)
        if not media or not cls._fusion_media_activity_expired(media, ttl_seconds=ttl_seconds):
            return False
        reports = state.get("reports") or {}
        if isinstance(reports, dict):
            reports.pop("media_activity", None)
        columns = state.get("columns") or {}
        if isinstance(columns, dict):
            media_col = columns.get("media") or {}
            items = media_col.get("items") if isinstance(media_col, dict) else []
            if isinstance(items, list):
                media_col["items"] = [item for item in items if not cls._is_fusion_media_activity(item)]
                if not media_col.get("items"):
                    columns.pop("media", None)
            else:
                columns.pop("media", None)
        return True

    @classmethod
    def _fusion_media_activity_expired(cls, media: Dict[str, Any], ttl_seconds: int = 300) -> bool:
        raw = (media or {}).get("updated_at") or (media or {}).get("created_at")
        if raw in (None, ""):
            return False
        try:
            if isinstance(raw, (int, float)):
                updated = datetime.fromtimestamp(float(raw))
            else:
                text = str(raw).strip().replace("T", " ").split("+", 1)[0].split(".", 1)[0]
                updated = datetime.strptime(text, "%Y-%m-%d %H:%M:%S")
        except Exception:
            return False
        if str((media or {}).get("group") or "") not in {"暂停播放", "停止播放"} and str((media or {}).get("level") or "") != "idle":
            return False
        return (datetime.now() - updated).total_seconds() > ttl_seconds

    @staticmethod
    def _is_fusion_media_activity(media: Any) -> bool:
        if not isinstance(media, dict):
            return False
        text = str(media.get("text") or "").strip()
        if not text:
            return False
        if media.get("group") or media.get("raw_title"):
            return True
        first = next((line.strip() for line in text.splitlines() if line.strip()), "")
        return first.startswith(("开始播放", "正在播放：", "停止播放", "新入库：", "登录成功：", "登录失败：", "媒体事件："))
