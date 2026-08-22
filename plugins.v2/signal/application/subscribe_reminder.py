"""Subscribe reminder service mixin."""

from datetime import datetime
from typing import List, Tuple

from app.log import logger

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
    def run_subscribe_reminder_scheduled(self) -> bool:
        return self.run_subscribe_reminder(scheduled=True)

    def run_subscribe_reminder(self, scheduled: bool = False) -> bool:
        """独立推送今日订阅追新（与每日汇报分开，按 subscribe_reminder_cron 调度，也可手动触发）。"""
        name = "订阅追新"
        ok, _ = self._guard_task(name, "subscribe_reminder")
        if not ok:
            return False
        try:
            mtype = self._notification_type(self._subscribe_reminder_msgtype, "Subscribe")
        except Exception:
            mtype = self._notification_type("Plugin")
        try:
            items = (
                self._unique_keep_order(self._compute_today_subscribe_updates_impl())
                if scheduled and not self._fusion_notify_enabled
                else self._get_today_subscribe_updates_locked()
            )
            if items:
                body = "📺 今日订阅追新：\n" + "\n".join(f"⦁ {x}" for x in items)
            else:
                body = "📺 今日订阅追新：暂无更新"
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
            elif scheduled:
                notification_status = "changed" if items else "noop"
                self._notify_fusion_task_outcome(
                    mtype=mtype,
                    title="Signal - 订阅追新",
                    text=body,
                    outcome=f"今日订阅追新 {len(items)} 项" if items else "今日订阅追新暂无更新",
                    success=True,
                    component="subscribe_reminder",
                    task_key="subscribe_reminder",
                    task_group="订阅追新",
                    notification_status=notification_status,
                    notification_target="daily_updates",
                    notification_fingerprint=(
                        self._notification_outcome_fingerprint({
                            "date": datetime.now().date().isoformat(),
                            "items": sorted(str(item) for item in items),
                        })
                        if items else ""
                    ),
                    notification_cooldown=bool(items),
                )
            else:
                self._notify_or_console(mtype=mtype, title="Signal - 订阅追新", text=body)
            self._save_task_result(name, True, 0, body)
            return True
        except Exception as err:
            self._save_task_result(name, False, -1, str(err))
            if scheduled and not self._fusion_notify_enabled:
                self._notify_fusion_task_outcome(
                    mtype=mtype,
                    title="Signal - 订阅追新异常",
                    text=f"订阅追新执行失败：{err}",
                    outcome=f"订阅追新执行失败：{str(err)[:120]}",
                    success=False,
                    component="subscribe_reminder",
                    task_key="subscribe_reminder",
                    task_group="订阅追新",
                    notification_status="error",
                    notification_target="daily_updates",
                    notification_fingerprint=self._notification_error_fingerprint(err),
                    notification_cooldown=True,
                )
            logger.error(f"Signal 订阅追新推送失败：{err}")
            return False
    def _load_subscribereminder_today_realtime_locked(self) -> Tuple[bool, List[str]]:
        try:
            return True, self._compute_today_subscribe_updates_impl()
        except Exception as err:
            logger.warning(f"Signal 订阅追新实时计算失败：{err}")
            return False, []
    def _load_subscribereminder_today_locked(self) -> List[str]:
        """Never consume another plugin's cache after live calculation fails."""
        return []
    def _compute_today_subscribe_updates_impl(self) -> List[str]:
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
