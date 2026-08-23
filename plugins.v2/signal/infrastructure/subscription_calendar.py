"""MoviePilot v2 官方订阅日历组合契约适配器。"""

from dataclasses import dataclass
from datetime import date, datetime
import locale
import threading
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple

class SubscriptionCalendarError(RuntimeError):
    """订阅日历宿主读取失败。"""


class SubscriptionCalendarContractError(SubscriptionCalendarError):
    """MoviePilot v2 日历复合接口返回了非法结构。"""


@dataclass(frozen=True)
class SubscriptionCalendarSnapshot:
    """一次 MoviePilot v2 复合日历读取的不可变结果。"""

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


class MoviePilotV2SubscriptionCalendar:
    """按 MoviePilot v2 官方前端组合方式读取订阅日历。"""

    _SOURCE = "moviepilot-v2-calendar-composite"
    _REQUEST_TIMEOUT = 20
    _LOCALE_LOCK = threading.RLock()

    def __init__(
        self,
        *,
        request_utils: Optional[Any] = None,
        api_token: Optional[str] = None,
        port: Optional[int] = None,
        api_prefix: Optional[str] = None,
        today_provider: Optional[Callable[[], date]] = None,
    ) -> None:
        self._request_utils = request_utils
        self._api_token = api_token
        self._port = port
        self._api_prefix = api_prefix
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
        if failed == total:
            status = "invalid" if invalid_failures == total else "failed"
        elif failed:
            status = "partial"
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
        from app.core.config import settings

        timezone_name = str(getattr(settings, "TZ", "") or "").strip()
        if not timezone_name:
            raise SubscriptionCalendarError("MoviePilot TZ 未配置")
        try:
            import pytz
            return datetime.now(pytz.timezone(timezone_name)).date()
        except Exception as err:
            raise SubscriptionCalendarError("MoviePilot TZ 无法解析") from err

    def _get_subscriptions(self) -> List[Dict[str, Any]]:
        payload = self._get_json("subscribe/", params={})
        if not isinstance(payload, list):
            raise SubscriptionCalendarContractError("subscribe/ 返回非订阅数组")
        if any(not isinstance(item, dict) for item in payload):
            raise SubscriptionCalendarContractError("subscribe/ 包含非法订阅条目")
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
        tmdbid = self._positive_int(subscribe.get("tmdbid"))
        if not tmdbid:
            raise SubscriptionCalendarContractError(f"订阅条目 {index + 1} 缺少 TMDB ID")

        if media_type == "电影":
            media = self._get_json(
                f"media/tmdb:{tmdbid}",
                params={"type_name": media_type},
            )
            if not isinstance(media, dict):
                raise SubscriptionCalendarContractError(f"订阅条目 {index + 1} 电影详情结构非法")
            release_date = str(media.get("release_date") or "").strip()
            if not release_date:
                return []
            self._parse_local_date(release_date, index)
            if release_date != business_date:
                return []
            return [(release_date, name, index, f"{name} ({year})")]

        season = self._positive_or_zero_int(subscribe.get("season"))
        if season is None:
            raise SubscriptionCalendarContractError(f"订阅条目 {index + 1} 缺少季号")
        params = {}
        episode_group = str(subscribe.get("episode_group") or "").strip()
        if episode_group:
            params["episode_group"] = episode_group
        episodes = self._get_json(f"tmdb/{tmdbid}/{season}", params=params)
        if not isinstance(episodes, list):
            raise SubscriptionCalendarContractError(f"订阅条目 {index + 1} 季集响应结构非法")

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

    def _get_json(self, path: str, *, params: Dict[str, Any]) -> Any:
        token = str(self._api_token if self._api_token is not None else self._settings_value("API_TOKEN", "") or "").strip()
        if not token:
            raise SubscriptionCalendarError("MoviePilot API_TOKEN 未配置")
        query = dict(params or {})
        try:
            response = self._client(token).get_res(
                self._url(path),
                params=query,
                raise_exception=True,
            )
        except SubscriptionCalendarError:
            raise
        except Exception as err:
            raise SubscriptionCalendarError(f"宿主请求异常：{path}") from err
        if response is None:
            raise SubscriptionCalendarError(f"宿主请求失败：{path}")
        try:
            if not 200 <= int(response.status_code) < 300:
                raise SubscriptionCalendarError(f"宿主请求 HTTP {response.status_code}：{path}")
            try:
                return response.json()
            except Exception as err:
                raise SubscriptionCalendarError(f"宿主响应不是 JSON：{path}") from err
        finally:
            close = getattr(response, "close", None)
            if callable(close):
                close()

    def _client(self, token: str) -> Any:
        if self._request_utils is not None:
            return self._request_utils
        from app.utils.http import RequestUtils

        return RequestUtils(
            headers={"X-API-KEY": token, "Accept": "application/json"},
            proxies=None,
            timeout=self._REQUEST_TIMEOUT,
        )

    def _url(self, path: str) -> str:
        port = int(self._port if self._port is not None else self._settings_value("PORT", 3001) or 3001)
        prefix_value = self._api_prefix if self._api_prefix is not None else self._settings_value("API_V1_STR", "/api/v1")
        api_prefix = str(prefix_value or "/api/v1").rstrip("/")
        return f"http://127.0.0.1:{port}{api_prefix}/{str(path).lstrip('/')}"

    @staticmethod
    def _settings_value(name: str, default: Any) -> Any:
        from app.core.config import settings

        return getattr(settings, name, default)

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
