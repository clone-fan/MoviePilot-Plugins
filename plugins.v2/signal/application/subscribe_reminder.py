"""Subscribe reminder service mixin."""

from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any, List

from app.log import logger

from ..domain.fusion_event import FusionEvent


_CALENDAR_SCOPE: ContextVar[tuple] = ContextVar("signal_subscription_calendar_scope", default=(None, 0, None))

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
        """在单次日历读取作用域内执行订阅追新。"""
        with self._subscription_calendar_read_scope():
            return self._run_subscribe_reminder_scoped(scheduled=scheduled)

    def _run_subscribe_reminder_scoped(self, scheduled: bool = False) -> bool:
        """独立推送今日订阅追新，按 subscribe_reminder_cron 调度，也可手动触发。"""
        name = "订阅追新"
        ok, _ = self._guard_task(name, "subscribe_reminder")
        if not ok:
            return False
        try:
            mtype = self._notification_type(self._subscribe_reminder_msgtype, "Subscribe")
        except Exception:
            mtype = self._notification_type("Plugin")
        try:
            snapshot = self._read_today_subscription_calendar_snapshot()
            items = list(snapshot.items)
            partial_message = snapshot.failure_message() if snapshot.is_partial else ""
            if items:
                body = "📺 今日订阅追新：\n" + "\n".join(f"⦁ {x}" for x in items)
            else:
                body = "📺 今日订阅追新：暂无更新"
            if partial_message:
                body = f"{body}\n⚠️ {partial_message}"
            if self._fusion_notify_enabled:
                self._emit_fusion_event(FusionEvent.create(
                    owner="persistent-subscriptions",
                    event_type="snapshot",
                    title="订阅追新",
                    body=body,
                    level="warning" if snapshot.is_partial else "success",
                    result_status="error" if snapshot.is_partial else "success",
                    payload={
                        "items": list(items or []),
                        "status": snapshot.status,
                        "failed_subscriptions": snapshot.failed_subscriptions,
                        "errors": list(snapshot.errors),
                    },
                    component="subscribe_reminder",
                ))
            elif scheduled:
                notification_status = "error" if snapshot.is_partial else ("changed" if items else "noop")
                self._notify_fusion_task_outcome(
                    mtype=mtype,
                    title="Signal - 订阅追新部分失败" if snapshot.is_partial else "Signal - 订阅追新",
                    text=body,
                    outcome=partial_message or (f"今日订阅追新 {len(items)} 项" if items else "今日订阅追新暂无更新"),
                    success=not snapshot.is_partial,
                    component="subscribe_reminder",
                    task_key="subscribe_reminder",
                    task_group="订阅追新",
                    notification_status=notification_status,
                    notification_target="daily_updates",
                    notification_fingerprint=(
                        self._notification_outcome_fingerprint({
                            "date": snapshot.business_date,
                            "status": snapshot.status,
                    "failed_subscriptions": snapshot.failed_subscriptions,
                    "items": sorted(str(item) for item in items),
                            "errors": self._subscription_calendar_error_fingerprint_values(snapshot.errors),
                        })
                        if items or snapshot.is_partial else ""
                    ),
                    notification_cooldown=bool(items) or snapshot.is_partial,
                )
            else:
                self._notify_or_console(
                    mtype=mtype,
                    title="Signal - 订阅追新",
                    text=body,
                )
            self._save_task_result(name, not snapshot.is_partial, 1 if snapshot.is_partial else 0, body)
            return not snapshot.is_partial
        except Exception as err:
            self._save_task_result(name, False, -1, str(err))
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

    @staticmethod
    def _load_today_subscription_calendar_snapshot() -> Any:
        """从 MoviePilot v2 官方复合日历契约读取一次快照。"""
        from ..infrastructure.subscription_calendar import MoviePilotV2SubscriptionCalendar
        return MoviePilotV2SubscriptionCalendar().read_today()

    def _read_today_subscription_calendar_snapshot(self) -> Any:
        """返回完整快照；部分失败和非法结果必须显式失败。"""
        from ..infrastructure.subscription_calendar import (
            SubscriptionCalendarError,
            SubscriptionCalendarSnapshot,
        )
        owner, depth, cached = _CALENDAR_SCOPE.get()
        same_owner = owner is self
        if same_owner and depth > 0 and isinstance(cached, SubscriptionCalendarSnapshot):
            snapshot = cached
        else:
            try:
                snapshot = self._load_today_subscription_calendar_snapshot()
            except SubscriptionCalendarError as err:
                snapshot = SubscriptionCalendarSnapshot(status="failed", errors=(str(err)[:240],))
                if same_owner and depth > 0:
                    _CALENDAR_SCOPE.set((self, depth, snapshot))
                raise
            except Exception as err:
                snapshot = SubscriptionCalendarSnapshot(status="failed", errors=(str(err)[:240],))
                if same_owner and depth > 0:
                    _CALENDAR_SCOPE.set((self, depth, snapshot))
                raise SubscriptionCalendarError(snapshot.failure_message()) from err
        if not isinstance(snapshot, SubscriptionCalendarSnapshot):
            snapshot = SubscriptionCalendarSnapshot(status="invalid", errors=("订阅日历适配器返回非法快照",))
            if same_owner and depth > 0:
                _CALENDAR_SCOPE.set((self, depth, snapshot))
            raise SubscriptionCalendarError(snapshot.failure_message())
        if snapshot.status not in {"success", "empty", "partial", "failed", "invalid"}:
            invalid = SubscriptionCalendarSnapshot(status="invalid", errors=(f"订阅日历适配器返回未知状态：{snapshot.status}",))
            if same_owner and depth > 0:
                _CALENDAR_SCOPE.set((self, depth, invalid))
            raise SubscriptionCalendarError(invalid.failure_message())
        if same_owner and depth > 0 and cached is None:
            _CALENDAR_SCOPE.set((self, depth, snapshot))
        if snapshot.is_failure:
            raise SubscriptionCalendarError(snapshot.failure_message())
        return snapshot

    def _read_today_subscribe_updates(self) -> List[str]:
        """为 Fusion 和 Telegram 提供同一宿主快照的文本条目。"""
        snapshot = self._read_today_subscription_calendar_snapshot()
        items = list(snapshot.items)
        if snapshot.is_partial:
            items.append(f"⚠️ {snapshot.failure_message()}")
        return items

    def _subscription_calendar_error_fingerprint_values(self, errors: Any) -> List[str]:
        """规范化并排序宿主错误，保证同一错误集合的指纹稳定。"""
        normalize = getattr(
            self,
            "_normalize_notification_error_summary",
            lambda value: str(value or "")[:240],
        )
        return sorted(normalize(error) for error in (errors or ()))

    @contextmanager
    def _subscription_calendar_read_scope(self):
        """让一次顶层业务操作内的所有消费者共享同一日历快照。"""
        owner, depth, snapshot = _CALENDAR_SCOPE.get()
        if owner is not self:
            depth, snapshot = 0, None
        token = _CALENDAR_SCOPE.set((self, depth + 1, snapshot if depth else None))
        try:
            yield
        finally:
            _CALENDAR_SCOPE.reset(token)

    def _subscription_calendar_snapshot_for_scope(self) -> Any:
        owner, _depth, snapshot = _CALENDAR_SCOPE.get()
        return snapshot if owner is self else None
