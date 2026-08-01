"""Subscribe reminder service mixin."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from app.log import logger
from app.schemas import NotificationType

from ..domain.fusion_event import FusionEvent

class SubscribeReminderMixin:
    """Subscribe reminder pushing and subscription fill history management."""


    def run_subfill_clear_history(self) -> bool:
        self.save_data("subfill_history", [])
        self._save_task_result("清理填充历史", True, 0, "已清理订阅规则填充历史记录")
        return True
    def run_subfill_clear_handled(self) -> bool:
        self.save_data("subfill_handled", [])
        self._save_task_result("清理已处理", True, 0, "已清理已处理记录，后续下载可重新填充")
        return True
    def run_subscribe_reminder(self) -> bool:
        """独立推送今日订阅追新（与每日汇报分开，按 subscribe_reminder_cron 调度，也可手动触发）。"""
        name = "订阅追新"
        ok, _ = self._guard_task(name, "subscribe_reminder")
        if not ok:
            return False
        try:
            items = self._get_today_subscribe_updates_locked()
            if items:
                body = "📺 今日订阅追新：\n" + "\n".join(f"⦁ {x}" for x in items)
            else:
                body = "📺 今日订阅追新：暂无更新"
            try:
                mtype = self._notification_type(self._subscribe_reminder_msgtype, "Subscribe")
            except Exception:
                mtype = self._notification_type("Plugin")
            if self._fusion_notify_enabled:
                self._emit_fusion_event(FusionEvent.create(
                    owner="persistent-subscriptions",
                    event_type="snapshot",
                    title="订阅追新",
                    body=body,
                    level="success",
                    payload={"items": list(items or [])},
                    component="subscribe_reminder",
                ))
            else:
                self._notify_or_console(mtype=mtype, title="MP 运维助手 - 订阅追新", text=body)
            self._save_task_result(name, True, 0, body)
            return True
        except Exception as err:
            self._save_task_result(name, False, -1, str(err))
            logger.error(f"Signal 订阅追新推送失败：{err}")
            return False
    def _load_subscribereminder_today_realtime_locked(self) -> Tuple[bool, List[str]]:
        try:
            return True, self._load_subscribereminder_today_fallback_impl()
        except Exception as err:
            logger.warning(f"Signal 订阅追新实时计算失败：{err}")
            return False, []
    def _load_subscribereminder_today_locked(self) -> List[str]:
        try:
            sub_file = Path("/config/agent/runtime/cache/subscribereminder_last_push.json")
            if not sub_file.exists():
                return []
            data = json.loads(sub_file.read_text(encoding="utf-8"))
            if not str(data.get("time") or "").startswith(self._today_prefix()):
                return []
            lines = []
            for raw in str(data.get("text") or "").splitlines():
                s = raw.strip()
                if not s:
                    continue
                lines.append(s.lstrip("???").lstrip("??").strip())
            return lines
        except Exception:
            return []
    def _load_subscribereminder_today_fallback_locked(self) -> List[str]:
        try:
            return self._load_subscribereminder_today_fallback_impl()
        except Exception:
            return []
    def _load_subscribereminder_today_fallback_impl(self) -> List[str]:
        from app.chain.media import MediaChain
        from app.chain.tmdb import TmdbChain
        from app.db.subscribe_oper import SubscribeOper
        from app.schemas.types import MediaType
        subscribe_oper = SubscribeOper(); tmdb = TmdbChain(); media = MediaChain()
        current_date = datetime.now().date().strftime("%Y-%m-%d")
        items = []
        for subscribe in subscribe_oper.list() or []:
            sub_type = str(getattr(subscribe, "type", "") or "").strip().lower()
            year = getattr(subscribe, "year", None) or "????"
            name = getattr(subscribe, "name", None) or "?????"
            if sub_type in {"电视剧", "剧集", "tv", "series"}:
                tmdbid = getattr(subscribe, "tmdbid", None); season = getattr(subscribe, "season", None)
                if not tmdbid or season in (None, ""):
                    continue
                try:
                    season_num = int(season)
                except Exception:
                    continue
                episodes_info = tmdb.tmdb_episodes(tmdbid=tmdbid, season=season_num, episode_group=getattr(subscribe, "episode_group", None)) or []
                episodes = []
                for episode in episodes_info:
                    if episode and getattr(episode, "air_date", None) and str(episode.air_date) == current_date:
                        episode_number = getattr(episode, "episode_number", None)
                        if episode_number:
                            episodes.append(int(episode_number))
                if episodes:
                    items.append(f"{name} ({year}) S{season_num:02d}{self._episode_ranges(sorted(set(episodes)))}")
                continue
            if sub_type in {"电影", "movie"}:
                tmdbid = getattr(subscribe, "tmdbid", None)
                if not tmdbid:
                    continue
                mediainfo = media.recognize_media(tmdbid=tmdbid, mtype=MediaType.MOVIE)
                if mediainfo and str(getattr(mediainfo, "release_date", None) or "") == current_date:
                    items.append(f"{name} ({year})")
        return self._unique_keep_order(items)
