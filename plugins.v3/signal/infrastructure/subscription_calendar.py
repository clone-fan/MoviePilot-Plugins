"""MoviePilot V3 订阅日历：按官方后端方式进程内直读订阅与 TMDB 排期。"""

from dataclasses import dataclass
from datetime import date, datetime
import locale
import threading
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple

class SubscriptionCalendarError(RuntimeError):
    """订阅日历宿主读取失败。"""


class SubscriptionCalendarContractError(SubscriptionCalendarError):
    """MoviePilot V3 宿主返回了非法的订阅或排期结构。"""


class SubscriptionCalendarSourceUnsupported(SubscriptionCalendarError):
    """订阅主身份不是 TMDB 来源，排期无单源实现可用。

    这不是缺陷：V3 允许订阅来自 douban、bangumi 等来源，而日历排期只有 TmdbChain
    一条单源实现。这类订阅应被跳过，不能当作数据缺失让整次日历失败。
    """


@dataclass(frozen=True)
class SubscriptionCalendarSnapshot:
    """一次 MoviePilot v2 订阅日历读取的不可变结果。"""

    status: str
    items: Tuple[str, ...] = ()
    total_subscriptions: int = 0
    resolved_subscriptions: int = 0
    failed_subscriptions: int = 0
    errors: Tuple[str, ...] = ()
    business_date: str = ""

    @property
    def is_failure(self) -> bool:
        """只有没有可消费结果的失败才阻断调用方。"""
        return self.status in {"failed", "invalid"}

    @property
    def is_partial(self) -> bool:
        """兼容保留的状态判断；read_today 复刻官方丢弃语义后不再产出 partial。"""
        return self.status == "partial"

    @property
    def has_errors(self) -> bool:
        return self.status in {"partial", "failed", "invalid"}

    @property
    def is_empty(self) -> bool:
        return self.status == "empty"

    def failure_message(self) -> str:
        if not self.has_errors:
            return ""
        detail = "；".join(self.errors[:3])
        if self.status == "partial":
            prefix = "订阅日历部分读取失败"
        elif self.status == "invalid":
            prefix = "订阅日历返回结构非法"
        else:
            prefix = "订阅日历读取失败"
        return f"{prefix}：{detail or '宿主未返回可用数据'}"


class MoviePilotHostCalendarReader:
    """进程内读取宿主订阅与 TMDB 排期。

    与 MoviePilot 官方后端 `SubscribeChain.cache_calendar` 使用同一组进程内接口
    （`SubscribeOper` 与 `TmdbChain`），因此直接复用宿主 `subscribe_calendar_cache`
    定时任务已经预热的 TMDB 缓存，不再经由本机 HTTP、鉴权和响应模型校验。
    """

    def __init__(self) -> None:
        self._tmdb_chain: Optional[Any] = None

    def _chain(self) -> Any:
        """整次日历读取复用一个 TmdbChain 实例，避免逐条订阅重复构建。"""
        if self._tmdb_chain is None:
            from app.chain.tmdb import TmdbChain

            self._tmdb_chain = TmdbChain()
        return self._tmdb_chain

    def list_subscriptions(self) -> List[Dict[str, Any]]:
        """读取全部订阅并规范为日历所需字段。

        经官方只读查询门面 `app.sdk.queries` 读取 DTO：其基类会把脏的半对身份
        归一为空身份，未知旧来源也不会让整页查询失败。分页由 host_queries 走到尾，
        不做静默截断。
        """
        from .host_queries import list_all_subscriptions

        try:
            records = list_all_subscriptions()
        except Exception as err:
            raise SubscriptionCalendarError(f"订阅列表读取失败：{self._reason(err)}") from err
        return [self._normalize(record) for record in records or []]

    def movie_release_date(self, subscribe: Dict[str, Any]) -> str:
        """读取电影上映日期，等价于官方日历的 release_date。"""
        from app.schemas.types import MediaType

        tmdbid = self._tmdb_id(subscribe)
        try:
            info = self._chain().tmdb_info(tmdbid=tmdbid, mtype=MediaType.MOVIE)
        except Exception as err:
            raise SubscriptionCalendarError(f"媒体详情读取失败：tmdb:{tmdbid}：{self._reason(err)}") from err
        if not isinstance(info, dict):
            return ""
        return str(info.get("release_date") or "").strip()

    def season_episodes(self, subscribe: Dict[str, Any], season: int) -> List[Dict[str, Any]]:
        """读取指定季的分集排期，等价于官方日历的 air_date 列表。"""
        tmdbid = self._tmdb_id(subscribe)
        episode_group = str(subscribe.get("episode_group") or "").strip() or None
        try:
            episodes = self._chain().tmdb_episodes(
                tmdbid=tmdbid,
                season=int(season),
                episode_group=episode_group,
            )
        except Exception as err:
            raise SubscriptionCalendarError(f"季集读取失败：tmdb:{tmdbid} S{season}：{self._reason(err)}") from err
        return [self._normalize_episode(episode) for episode in episodes or []]

    @staticmethod
    def _tmdb_id(subscribe: Dict[str, Any]) -> int:
        """解析 TMDB 原生 ID；仅对 media_source 确为 TMDB 的订阅有效。

        V3 的通用主身份是 media_source + media_id，日历排期只有 TmdbChain 这一条
        单源实现，因此非 TMDB 来源的订阅不参与排期，而不是被当作数据缺失。
        """
        if not MoviePilotHostCalendarReader.is_tmdb_source(subscribe):
            raise SubscriptionCalendarSourceUnsupported(
                str(subscribe.get("media_source") or "").strip() or "未知来源"
            )
        value = subscribe.get("media_id")
        try:
            number = int(value)
        except (TypeError, ValueError) as err:
            raise SubscriptionCalendarContractError("订阅缺少 TMDB ID") from err
        if number <= 0:
            raise SubscriptionCalendarContractError("订阅缺少 TMDB ID")
        return number

    @staticmethod
    def is_tmdb_source(subscribe: Dict[str, Any]) -> bool:
        """判断订阅主身份是否属于 TMDB 来源。"""
        from app.schemas.types import MediaSource

        source = str(subscribe.get("media_source") or "").strip().lower()
        return bool(source) and source == str(MediaSource.TMDB.value).lower()

    @staticmethod
    def _normalize(record: Any) -> Dict[str, Any]:
        """把宿主订阅行规范为日历字段，主身份使用 V3 的 media_source + media_id。"""
        from app.sdk.media import resolve_media_identity

        media_source, media_id = resolve_media_identity(
            media_source=getattr(record, "media_source", None),
            media_id=getattr(record, "media_id", None),
        )
        return {
            "type": str(getattr(record, "type", "") or "").strip(),
            "name": str(getattr(record, "name", "") or "").strip(),
            "year": str(getattr(record, "year", "") or "").strip(),
            "season": getattr(record, "season", None),
            "episode_group": str(getattr(record, "episode_group", "") or "").strip(),
            "media_source": media_source.value if media_source else "",
            "media_id": media_id or "",
        }

    @staticmethod
    def _normalize_episode(episode: Any) -> Dict[str, Any]:
        if isinstance(episode, dict):
            return {
                "air_date": episode.get("air_date"),
                "episode_number": episode.get("episode_number"),
            }
        return {
            "air_date": getattr(episode, "air_date", None),
            "episode_number": getattr(episode, "episode_number", None),
        }

    @staticmethod
    def _reason(error: BaseException) -> str:
        text = str(error or "").strip()
        return text[:160] or type(error).__name__


class MoviePilotV2SubscriptionCalendar:
    """按官方日历语义聚合今天的订阅事件。"""

    _SOURCE = "moviepilot-v2-calendar-inprocess"
    _LOCALE_LOCK = threading.RLock()

    def __init__(
        self,
        *,
        reader: Optional[Any] = None,
        today_provider: Optional[Callable[[], date]] = None,
    ) -> None:
        self._reader = reader if reader is not None else MoviePilotHostCalendarReader()
        self._today_provider = today_provider or self._moviepilot_today

    def read_today(self) -> SubscriptionCalendarSnapshot:
        """读取今天的订阅日历快照，并保留部分失败状态。"""
        try:
            business_date = self._today_provider().isoformat()
        except SubscriptionCalendarError as err:
            return SubscriptionCalendarSnapshot(status="failed", errors=(self._safe_error(err),))
        except Exception as err:
            return SubscriptionCalendarSnapshot(status="failed", errors=(f"MoviePilot 业务日期读取失败：{self._safe_error(err)}",))
        try:
            subscriptions = self._get_subscriptions()
        except SubscriptionCalendarContractError as err:
            return SubscriptionCalendarSnapshot(
                status="invalid",
                failed_subscriptions=0,
                errors=(self._safe_error(err),),
                business_date=business_date,
            )
        except SubscriptionCalendarError as err:
            return SubscriptionCalendarSnapshot(
                status="failed",
                failed_subscriptions=0,
                errors=(self._safe_error(err),),
                business_date=business_date,
            )

        total = len(subscriptions)
        if total == 0:
            return SubscriptionCalendarSnapshot(
                status="empty",
                business_date=business_date,
            )

        events: List[Tuple[str, str, int, str]] = []
        errors: List[str] = []
        invalid_failures = 0
        resolved = 0
        for index, subscribe in enumerate(subscriptions):
            try:
                events.extend(self._read_subscription_events(subscribe, business_date, index))
                resolved += 1
            except SubscriptionCalendarContractError as err:
                invalid_failures += 1
                errors.append(self._safe_error(err))
            except SubscriptionCalendarError as err:
                errors.append(self._safe_error(err))

        self._sort_events(events)
        items = tuple(event[3] for event in events)
        failed = len(errors)
        # 官方 V2 前端用 Promise.allSettled 组合日历：单条订阅读取失败被直接丢弃，
        # 只在控制台留痕，不对用户可见。这里复刻同一语义——逐条失败只保留为诊断计数，
        # 只有全部订阅都失败（等价于官方渲染不出任何事件）才升级为可见错误。
        if failed and failed == total:
            status = "invalid" if invalid_failures == total else "failed"
        elif not items:
            status = "empty"
        else:
            status = "success"
        return SubscriptionCalendarSnapshot(
            status=status,
            items=items,
            total_subscriptions=total,
            resolved_subscriptions=resolved,
            failed_subscriptions=failed,
            errors=tuple(errors),
            business_date=business_date,
        )

    @staticmethod
    def _moviepilot_today() -> date:
        """Use MoviePilot v2's configured system timezone for the browser-local date equivalent."""
        from app.sdk.config import settings

        timezone_name = str(getattr(settings, "TZ", "") or "").strip()
        if not timezone_name:
            raise SubscriptionCalendarError("MoviePilot TZ 未配置")
        try:
            import pytz
            return datetime.now(pytz.timezone(timezone_name)).date()
        except Exception as err:
            raise SubscriptionCalendarError("MoviePilot TZ 无法解析") from err

    def _get_subscriptions(self) -> List[Dict[str, Any]]:
        try:
            payload = self._reader.list_subscriptions()
        except SubscriptionCalendarError:
            raise
        except Exception as err:
            raise SubscriptionCalendarError(f"订阅列表读取失败：{self._safe_error(err)}") from err
        if not isinstance(payload, list):
            raise SubscriptionCalendarContractError("宿主未返回订阅列表")
        if any(not isinstance(item, dict) for item in payload):
            raise SubscriptionCalendarContractError("宿主返回了非法订阅条目")
        return payload

    def _read_subscription_events(
        self,
        subscribe: Dict[str, Any],
        business_date: str,
        index: int,
    ) -> List[Tuple[str, str, int, str]]:
        if not isinstance(subscribe, dict):
            raise SubscriptionCalendarContractError(f"订阅条目 {index + 1} 结构非法")
        media_type = str(subscribe.get("type") or "").strip()
        name = str(subscribe.get("name") or "?????").strip() or "?????"
        year = str(subscribe.get("year") or "????").strip() or "????"
        if not MoviePilotHostCalendarReader.is_tmdb_source(subscribe):
            # 非 TMDB 来源没有排期单源实现，跳过而不是让整次日历失败。
            return []
        media_id = self._positive_int(subscribe.get("media_id"))
        if not media_id:
            raise SubscriptionCalendarContractError(f"订阅条目 {index + 1} 缺少 TMDB ID")

        if media_type == "电影":
            release_date = self._read_movie_release_date(subscribe, index)
            if not release_date:
                return []
            self._parse_local_date(release_date, index)
            if release_date != business_date:
                return []
            return [(release_date, name, index, f"{name} ({year})")]

        season = self._positive_or_zero_int(subscribe.get("season"))
        if season is None:
            raise SubscriptionCalendarContractError(f"订阅条目 {index + 1} 缺少季号")
        episodes = self._read_season_episodes(subscribe, season, index)

        grouped: Dict[str, List[int]] = {}
        for episode in episodes:
            if not isinstance(episode, dict):
                raise SubscriptionCalendarContractError(f"订阅条目 {index + 1} 包含非法剧集条目")
            air_date = str(episode.get("air_date") or "").strip()
            if not air_date:
                continue
            self._parse_local_date(air_date, index)
            if air_date != business_date:
                continue
            grouped.setdefault(air_date, [])
            episode_number = self._positive_int(episode.get("episode_number"))
            if episode_number:
                grouped[air_date].append(episode_number)

        result: List[Tuple[str, str, int, str]] = []
        for air_date, numbers in grouped.items():
            unique_numbers = sorted(set(numbers))
            episode_suffix = self._episode_ranges(unique_numbers) if unique_numbers else ""
            result.append((
                air_date,
                name,
                index,
                f"{name} ({year}) S{season:02d}{episode_suffix}",
            ))
        return result

    def _read_movie_release_date(self, subscribe: Dict[str, Any], index: int) -> str:
        try:
            release_date = self._reader.movie_release_date(subscribe)
        except SubscriptionCalendarError:
            raise
        except Exception as err:
            raise SubscriptionCalendarError(f"订阅条目 {index + 1} 电影详情读取失败：{self._safe_error(err)}") from err
        return str(release_date or "").strip()

    def _read_season_episodes(
        self,
        subscribe: Dict[str, Any],
        season: int,
        index: int,
    ) -> List[Any]:
        try:
            episodes = self._reader.season_episodes(subscribe, season)
        except SubscriptionCalendarError:
            raise
        except Exception as err:
            raise SubscriptionCalendarError(f"订阅条目 {index + 1} 季集读取失败：{self._safe_error(err)}") from err
        if episodes is None:
            return []
        if not isinstance(episodes, list):
            raise SubscriptionCalendarContractError(f"订阅条目 {index + 1} 季集结构非法")
        return episodes

    @staticmethod
    def _positive_int(value: Any) -> Optional[int]:
        try:
            number = int(value)
        except (TypeError, ValueError):
            return None
        return number if number > 0 else None

    @staticmethod
    def _positive_or_zero_int(value: Any) -> Optional[int]:
        try:
            number = int(value)
        except (TypeError, ValueError):
            return None
        return number if number >= 0 else None

    @staticmethod
    def _parse_local_date(value: str, index: int) -> datetime:
        try:
            year, month, day = (int(part) for part in value.split("-"))
            return datetime(year, month, day)
        except (TypeError, ValueError) as err:
            raise SubscriptionCalendarContractError(f"订阅条目 {index + 1} 日期结构非法") from err

    @classmethod
    def _sort_events(cls, events: List[Tuple[str, str, int, str]]) -> None:
        """使用宿主前端所在系统的 localeCompare 等价顺序。"""
        with cls._LOCALE_LOCK:
            previous = locale.setlocale(locale.LC_COLLATE)
            try:
                try:
                    locale.setlocale(locale.LC_COLLATE, "")
                except locale.Error:
                    pass
                events.sort(key=lambda item: (item[0], locale.strxfrm(item[1]), item[2]))
            finally:
                try:
                    locale.setlocale(locale.LC_COLLATE, previous)
                except locale.Error:
                    pass

    @staticmethod
    def _episode_ranges(numbers: Iterable[int]) -> str:
        values = list(numbers)
        ranges: List[str] = []
        start = end = values[0]
        for current in values[1:]:
            if current == end + 1:
                end = current
                continue
            ranges.append(MoviePilotV2SubscriptionCalendar._episode_range(start, end))
            start = end = current
        ranges.append(MoviePilotV2SubscriptionCalendar._episode_range(start, end))
        return "、".join(ranges)

    @staticmethod
    def _episode_range(start: int, end: int) -> str:
        if start == end:
            return f"E{start:02d}"
        return f"E{start:02d}-E{end:02d}"

    @staticmethod
    def _safe_error(error: BaseException) -> str:
        text = str(error or "").strip()
        return text[:240] or type(error).__name__
