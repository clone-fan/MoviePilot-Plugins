import re
import os
import threading
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from app.sdk.logging import logger
from app.schemas.types import MessageType

from ..domain.fusion_transport import (
    build_edit_message_text_payload,
    build_send_rich_message_draft_payload,
    build_send_rich_message_payload,
)
from ..domain.update_jobs import set_update_job


# 交互式「🔄 刷新」的线程级标记：点按钮后的重绘由动作 worker 统一负责
# （running → success/error）。底层 _refresh_fusion_card_scoped 自带一次
# editMessageText，若不标记就会在采集结束时让卡片连续闪两下；按线程隔离，
# 不影响同进程内调度器触发的周期刷新。
_FUSION_INTERACTIVE_REFRESH = threading.local()


class TgConsoleCallbackMixin:
    """Telegram polling, message/callback handling, action execution, card upsert"""

    _tg_console_card_lock = threading.RLock()

    def poll_tg_console_updates(self) -> bool:
        ok, _ = self._runtime_gate("scheduler", component="fusion_notify", name="TGConsolePoll")
        if not ok:
            return False
        if not (self._tg_console_enabled and self._tg_console_poll_enabled):
            return False
        token, chat_id, _source = self._resolve_fusion_telegram_config()
        if not token or not chat_id:
            self._tg_console_last_error = "Telegram 融合汇报卡轮询缺少 Bot Token/Chat ID"
            return False
        state = self._tg_console_state(chat_id=chat_id)
        base_url = f"https://api.telegram.org/bot{token}"
        payload: Dict[str, Any] = {"timeout": 0, "allowed_updates": ["callback_query", "message"]}
        last_update_id = self._safe_int(state.get("last_update_id"), 0, 0)
        if last_update_id:
            payload["offset"] = last_update_id + 1
        res = self._telegram_http_post_json(f"{base_url}/getUpdates", payload, timeout=max(5, self._tg_console_poll_interval))
        ok, data = self._telegram_response_data(res, "getUpdates")
        if not ok:
            state["last_error"] = self._tg_console_last_error
            self._save_tg_console_state(state)
            return False
        seen: set = set()
        for update in data.get("result") or []:
            if not isinstance(update, dict):
                continue
            update_id = self._safe_int(update.get("update_id"), 0, 0)
            callback = update.get("callback_query") or {}
            if update_id in seen:
                if callback.get("id"):
                    self._tg_console_answer_callback(callback.get("id"), "重复回调已忽略")
                continue
            seen.add(update_id)
            if update_id and update_id <= last_update_id:
                if callback.get("id"):
                    self._tg_console_answer_callback(callback.get("id"), "重复回调已忽略")
                continue
            if callback:
                self._handle_tg_console_callback(callback, update_id=update_id)
            message = update.get("message") or {}
            if message:
                self._handle_tg_console_message(message, update_id=update_id)
            if update_id:
                last_update_id = max(last_update_id, update_id)
        state = self._tg_console_state(chat_id=chat_id)
        state["last_update_id"] = last_update_id
        self._save_tg_console_state(state)
        return True

    def _tg_console_start_background_action(self, action_key: str, label: str, user_id: Optional[str]) -> None:
        """后台执行长任务动作；完成后按既有语义回报结果通知。"""

        def work() -> None:
            try:
                ok, message = self._tg_console_execute_action(action_key, user_id=user_id)
                self._emit_console_notice(f"TG 远控 - {label}", message, "success" if ok else "error")
            except Exception as err:
                logger.warning(f"Signal TG 远控后台执行失败：{err}")

        try:
            threading.Thread(target=work, name=f"Signal-tg-{action_key}", daemon=True).start()
        except Exception:
            logger.warning(f"Signal TG 远控后台线程未能启动：{action_key}")

    @staticmethod
    def _fusion_update_running_text(kind: str, action: Dict[str, Any], payload: Dict[str, Any]) -> str:
        if kind == "plugin_update":
            name = str(payload.get("name") or payload.get("id") or "插件")
            target = str(payload.get("new") or "")
            return f"正在更新 {name}{f' → {target}' if target else ''}…"
        if kind == "mp_update":
            return "正在请求 MoviePilot 原生更新流程…"
        if kind == "market_update":
            return "正在同步插件库…"
        if kind == "card_refresh":
            return "正在刷新卡片数据…"
        return f"正在执行 {action.get('label') or '更新操作'}…"

    @staticmethod
    def _fusion_action_feed_set(state: Dict[str, Any], action_id: str, kind: str, label: str,
                                status: str, message: str) -> None:
        feed = [item for item in list(state.get("fusion_action_feed") or [])
                if isinstance(item, dict) and str(item.get("id") or "") != str(action_id)]
        now = datetime.now()
        feed.insert(0, {
            "id": str(action_id),
            "kind": str(kind),
            "label": str(label or "更新操作"),
            "status": str(status),
            "message": str(message or ""),
            "time": now.strftime("%H:%M"),
            "updated_at": now.timestamp(),
        })
        state["fusion_action_feed"] = feed[:5]

    @staticmethod
    def _fusion_action_remove_candidate(state: Dict[str, Any], kind: str, payload: Dict[str, Any]) -> None:
        candidates = state.get("fusion_update_actions")
        if not isinstance(candidates, dict):
            return
        if kind == "plugin_update" and isinstance(payload, dict):
            entry = candidates.get(kind) or {}
            items = list((entry.get("payload") or {}).get("plugins") or [])
            target = (str(payload.get("id") or ""), str(payload.get("new") or ""))
            remaining = [item for item in items if isinstance(item, dict)
                         and (str(item.get("id") or ""), str(item.get("new") or "")) != target]
            if remaining:
                entry["payload"] = {"plugins": remaining}
                candidates[kind] = entry
            else:
                candidates.pop(kind, None)
        else:
            candidates.pop(kind, None)

    def _handle_fusion_update_action(self, nonce: str, action: Dict[str, Any], callback: Dict[str, Any],
                                     state: Dict[str, Any], token: str, chat_id: str, user_id: str) -> bool:
        # nonce 的检查和消费必须原子化，避免连点同时启动两次更新。
        with self._tg_console_card_lock:
            state = self._tg_console_state(chat_id=chat_id)
            action = (state.get("pending_actions") or {}).get(nonce) or {}
            if not action or action.get("done"):
                return self._show_fusion_action_problem(state, callback, token, chat_id, user_id,
                    "这个按钮已失效，已刷新卡片，请使用当前按钮。")
            return self._handle_fusion_update_action_locked(nonce, action, callback, state, token, chat_id, user_id)

    def _handle_fusion_update_action_locked(self, nonce, action, callback, state, token, chat_id, user_id):
        kind = str(action.get("kind") or "")
        payload = dict(action.get("payload") or {})
        mp_session_hint = ""
        if kind == "mp_update":
            # 只读操作可以恢复旧面板；下载和安装只接受当前发起人的有效确认。
            identity = {"userid": user_id, "source": callback.get("source"),
                        "channel": callback.get("channel"),
                        "original_chat_id": callback.get("original_chat_id") or (callback.get("message") or {}).get("chat", {}).get("id")}
            _, _, source = self._find_moviepilot_telegram_config(getattr(self, "_fusion_notify_msgtype", "Plugin"))
            if not self._notice_moviepilot_actor_allowed(identity, target_source=source):
                self._tg_console_answer_callback(str(callback.get("id") or ""), "仅当前通知通道的管理员可操作")
                return False
            panel = state.get("moviepilot_update_panel") or {}
            job = ((state.get("update_jobs") or {}).get("mp_update") or {})
            # 更新中心是唯一状态源：确认凭据必须以 job 为准，legacy panel 只作兜底。
            # 反过来会让「刚刷新出来的新按钮」和「旧 panel 的老 session」对不上，一点就报失效。
            panel_session = job.get("session") or panel.get("session")
            panel_actor = job.get("actor_id") or panel.get("actor_id")
            panel_expires = job.get("expires_at") or panel.get("expires_at") or 0
            panel_steps = list(job.get("steps") or panel.get("steps") or [])
            step = payload.get("step", "open")
            callback_message = (callback.get("message") or {}).get("message_id") or callback.get("original_message_id")
            if str(callback_message) != str(state.get("message_id")):
                return False
            if step not in {"open", "status", "check", "download", "install"}:
                return self._show_fusion_action_problem(state, callback, token, chat_id, user_id,
                    "更新操作无效，已刷新卡片，请使用当前按钮。")
            if step in {"download", "install"}:
                if panel_actor and str(panel_actor) != str(user_id):
                    return self._show_fusion_action_problem(state, callback, token, chat_id, user_id,
                        "只能由发起人确认更新。可点击更新进度，重新查看并确认。")
                panel_expires_value = float(panel_expires or 0)
                if (payload.get("session") != panel_session
                        or (panel_expires_value and panel_expires_value < time.time())
                        or step not in panel_steps):
                    # 过期确认只读当前状态，绝不执行旧下载/安装授权。
                    payload = {"step": "status", "expired_confirmation": True}
            if any(item.get("kind") == kind and item.get("status") == "running"
                   and time.time() - float(item.get("updated_at") or 0) < 900
                   for item in state.get("fusion_action_feed") or []):
                return False
            # 一次点击不应换 session：否则卡片没来得及重绘时，旧按钮会立刻失效。
            mp_session_hint = str(job.get("session") or panel.get("session") or "")
            state.pop("moviepilot_update_panel", None)
        label = "🔄 更新进度" if payload.get("expired_confirmation") else str(action.get("label") or "更新操作")
        action_id = str(action.get("action_key") or nonce)
        running = self._fusion_update_running_text(kind, action, payload)
        action["done"] = True
        action["user_id"] = str(user_id or "")
        state.setdefault("pending_actions", {})[nonce] = action
        self._fusion_action_feed_set(state, action_id, kind, label, "running", running)
        self._save_tg_console_state(state)
        try:
            self._tg_console_upsert_card(token, chat_id, state)
        except Exception as err:
            state["last_error"] = f"更新动作卡片状态更新异常：{self._telegram_safe_error(err, limit=300)}"
            self._save_tg_console_state(state)
        callback_id = str((callback or {}).get("id") or "")
        self._tg_console_answer_callback(callback_id, "已开始")
        generation = getattr(self, "_runtime_generation", 0)
        context = {
            "userid": str(user_id or ""),
            "channel": str(callback.get("channel") or "Telegram"),
            "source": str(callback.get("source") or ""),
            "original_message_id": callback.get("original_message_id") or state.get("message_id") or 0,
            "original_chat_id": callback.get("original_chat_id") or chat_id,
            "moviepilot_update_panel": ({"session": mp_session_hint} if mp_session_hint else {}),
        }
        try:
            worker = threading.Thread(
                target=self._fusion_update_action_worker,
                args=(action_id, kind, payload, label, context, generation, token, chat_id),
                name="Signal-fusion-update-action",
                daemon=True,
            )
            worker.start()
        except Exception:
            self._fusion_action_feed_set(state, action_id, kind, label, "error", "后台任务未能启动，请重试。")
            self._save_tg_console_state(state)
            return False
        return True

    def _fusion_update_action_worker(self, action_id: str, kind: str, payload: Dict[str, Any], label: str,
                                     context: Dict[str, Any], generation: int, token: str, chat_id: str) -> None:
        try:
            ok, message = self._execute_fusion_update_action(kind, payload, context)
        except Exception as err:
            ok, message = False, f"更新操作异常：{self._telegram_safe_error(err, limit=180)}"
        if self._should_cancel(generation):
            return
        with self._tg_console_card_lock:
            state = self._tg_console_state(chat_id=chat_id)
            if (self._should_cancel(generation)
                    or str(state.get("message_id")) != str(context.get("original_message_id"))):
                return
            # panel 仍承载宿主的下载进度轮询；点击校验已改为以 update_jobs 为准，
            # 所以这里保留写入不会再把「刷新出来的按钮」判成失效。
            if context.get("moviepilot_update_panel"):
                state["moviepilot_update_panel"] = context["moviepilot_update_panel"]
            job_patch = context.get("update_job_patch")
            if isinstance(job_patch, dict) and isinstance(job_patch.get("patch"), dict):
                state["update_jobs"] = set_update_job(state.get("update_jobs"), str(job_patch.get("kind") or "mp_update"),
                                                       job_patch["patch"], now=time.time())
            elif kind in {"plugin_update", "market_update"}:
                candidate_items = []
                if kind == "plugin_update":
                    entry = (state.get("fusion_update_actions") or {}).get(kind) or {}
                    candidate_items = list((entry.get("payload") or {}).get("plugins") or [])
                terminal_jobs = set_update_job(state.get("update_jobs"), kind, {
                    "phase": "success" if ok else "failed",
                    "message": message,
                    "error": "" if ok else message,
                    "items": [] if ok else candidate_items,
                    "updated_at": time.time(),
                }, now=time.time())
                state["update_jobs"] = terminal_jobs
                terminal_job = terminal_jobs.get(kind) or {}
                expires_at = float(terminal_job.get("expires_at") or 0)
                if expires_at > 0 and callable(getattr(self, "_schedule_update_center_expiry", None)):
                    self._schedule_update_center_expiry(kind, expires_at, token, chat_id)
            self._fusion_action_feed_set(state, action_id, kind, label, "success" if ok else "error", message)
            panel = context.get("moviepilot_update_panel") or {}
            if ok and (not panel or panel.get("phase") in {"idle", "installing"}):
                self._fusion_action_remove_candidate(state, kind, payload)
            self._save_tg_console_state(state)
            try:
                self._tg_console_upsert_card(token, chat_id, state, generation=generation)
            except Exception as err:
                state["last_error"] = f"更新动作结果卡片更新异常：{self._telegram_safe_error(err, limit=300)}"
            self._save_tg_console_state(state)
        if ok:
            self._schedule_fusion_status_expiry(action_id, token, chat_id, generation)
        if (context.get("moviepilot_update_panel") or {}).get("phase") == "downloading":
            self._schedule_fusion_moviepilot_progress(context, generation, token, chat_id)

    def _show_fusion_action_problem(self, state, callback, token, chat_id, user_id, message):
        """宿主已应答 TG 回调；失效按钮的反馈必须写回原卡，不能只尝试空回调 ID。"""
        identity = {"userid": user_id, "source": callback.get("source"), "channel": callback.get("channel"),
                    "original_chat_id": callback.get("original_chat_id") or (callback.get("message") or {}).get("chat", {}).get("id")}
        message_id = callback.get("original_message_id") or (callback.get("message") or {}).get("message_id")
        _, _, source = self._find_moviepilot_telegram_config(getattr(self, "_fusion_notify_msgtype", "Plugin"))
        if (not self._notice_moviepilot_actor_allowed(identity, target_source=source)
                or str(message_id) != str(state.get("message_id"))):
            return False
        with self._tg_console_card_lock:
            state = self._tg_console_state(chat_id=chat_id)
            if str(message_id) != str(state.get("message_id")):
                return False
            self._fusion_action_feed_set(state, "interaction-recovery", "interaction", "操作提示", "error", message)
            self._save_tg_console_state(state)
            self._tg_console_upsert_card(token, chat_id, state)
        return False

    def _refresh_fusion_moviepilot_progress(self, context, generation, token, chat_id):
        """只读宿主下载状态；仅进度或终态变化时编辑卡片。"""
        stopped = context.get("_monitor_stop")
        if self._should_cancel(generation) or (stopped is not None and stopped.is_set()):
            return False
        with self._tg_console_card_lock:
            state = self._tg_console_state(chat_id=chat_id)
            panel = dict(state.get("moviepilot_update_panel") or {})
            if panel.get("phase") != "downloading" or str(state.get("message_id")) != str(context.get("original_message_id")):
                return False
        refreshed = {**context, "userid": panel.get("actor_id"), "moviepilot_update_panel": panel}
        self._notice_execute_moviepilot_fusion_action(refreshed, {"step": "status"})
        next_panel = refreshed.get("moviepilot_update_panel") or {}
        if not next_panel:
            return False
        with self._tg_console_card_lock:
            if self._should_cancel(generation) or (stopped is not None and stopped.is_set()):
                return False
            state = self._tg_console_state(chat_id=chat_id)
            if str(state.get("message_id")) != str(context.get("original_message_id")):
                return False
            current = state.get("moviepilot_update_panel") or {}
            if current.get("session") != panel.get("session"):
                return current.get("phase") == "downloading"
            fields = ("phase", "version", "progress", "message", "error")
            changed_job = None
            panel_changed = False
            if any(current.get(key) != next_panel.get(key) for key in fields):
                panel_changed = True
                state["moviepilot_update_panel"] = next_panel
                job_patch = refreshed.get("update_job_patch")
                if isinstance(job_patch, dict) and isinstance(job_patch.get("patch"), dict):
                    kind = str(job_patch.get("kind") or "mp_update")
                    state["update_jobs"] = set_update_job(state.get("update_jobs"), kind,
                                                           job_patch["patch"], now=time.time())
                    changed_job = dict((state.get("update_jobs") or {}).get(kind) or {})
                self._save_tg_console_state(state)
        if panel_changed:
            hook = getattr(self, "_update_center_job_changed", None)
            if changed_job and callable(hook):
                hook("mp_update", changed_job, state)
            else:
                with self._tg_console_card_lock:
                    self._tg_console_upsert_card(token, chat_id, state, generation=generation)
        return next_panel.get("phase") == "downloading"

    def _schedule_fusion_moviepilot_progress(self, context, generation, token, chat_id):
        """下载期间每秒读一次本地状态；卡片编辑由 2 秒节流与 5% 进度桶控制。"""
        with self._tg_console_card_lock:
            if self._should_cancel(generation):
                return
            panel = context.get("moviepilot_update_panel") or {}
            key = (generation, chat_id, context.get("original_message_id"), panel.get("session"))
            previous = getattr(self, "_fusion_mp_monitor", None)
            if previous and previous["key"] == key and not previous["stop"].is_set():
                return
            if previous:
                previous["stop"].set()
            monitor_state = {"key": key, "stop": threading.Event()}
            self._fusion_mp_monitor = monitor_state
        # 每次新的手动操作替换旧监控。旧线程退出不能清除新监控，也不能回写旧结果。
        monitor_context = {**context, "_monitor_stop": monitor_state["stop"]}
        def monitor():
            try:
                for _ in range(3600):
                    if monitor_state["stop"].wait(1):
                        return
                    if not self._refresh_fusion_moviepilot_progress(monitor_context, generation, token, chat_id):
                        return
            except Exception as err:
                logger.warning(f"Signal 更新进度同步失败：{self._telegram_safe_error(err, limit=180)}")
            finally:
                with self._tg_console_card_lock:
                    if getattr(self, "_fusion_mp_monitor", None) is monitor_state:
                        self._fusion_mp_monitor = None
        try:
            threading.Thread(target=monitor, name="Signal-moviepilot-progress", daemon=True).start()
        except Exception:
            with self._tg_console_card_lock:
                monitor_state["stop"].set()
                if getattr(self, "_fusion_mp_monitor", None) is monitor_state:
                    self._fusion_mp_monitor = None

    # 成功状态行在卡片上停留的秒数；到点后自动重绘一次把它去掉。
    # 只做短暂停留：用户看得见结果，又不会一直挂着一张「框」。
    FUSION_STATUS_EXPIRY_DELAY = 20

    def _schedule_fusion_status_expiry(self, action_id: str, token: str, chat_id: str, generation: int) -> None:
        """成功提示自动下线：延迟一次重绘，避免结果行一直挂在卡片上。"""
        try:
            delay = max(5.0, float(getattr(self, "FUSION_STATUS_EXPIRY_DELAY", 20)))
        except (TypeError, ValueError):
            delay = 20.0

        def cleanup() -> None:
            if self._should_cancel(generation):
                return
            with self._tg_console_card_lock:
                state = self._tg_console_state(chat_id=chat_id)
                feed = state.get("fusion_action_feed")
                if not isinstance(feed, list):
                    return
                kept = [item for item in feed
                        if not (isinstance(item, dict)
                                and str(item.get("id") or "") == str(action_id)
                                and str(item.get("status") or "") != "running")]
                if len(kept) == len(feed):
                    return
                state["fusion_action_feed"] = kept
                self._save_tg_console_state(state)
                try:
                    self._tg_console_upsert_card(token, chat_id, state, generation=generation)
                except Exception as err:
                    state["last_error"] = f"更新动作状态自动下线异常：{self._telegram_safe_error(err, limit=300)}"
                    self._save_tg_console_state(state)

        try:
            timer = threading.Timer(delay, cleanup)
            timer.daemon = True
            timer.name = "Signal-fusion-status-expiry"
            timer.start()
        except Exception:
            logger.warning(f"Signal 融合卡状态自动下线定时器未能启动：{action_id}")

    def _execute_fusion_update_action(self, kind: str, payload: Dict[str, Any],
                                      context: Dict[str, Any]) -> Tuple[bool, str]:
        # 门阀：卡片按钮只是「插件已启用功能」的入口，不能绕过插件设置。
        # 功能被关掉后，即使旧消息里还留着按钮，执行到这里也会被拒绝。
        gate = {"plugin_update": "plugin_update_reminder",
                "mp_update": "mp_update",
                "market_update": "market_update"}.get(kind)
        checker = getattr(self, "_component_enabled", None)
        if gate and callable(checker) and not checker(gate):
            return False, "该功能未在插件设置中启用，融合卡不会执行。"
        if kind == "plugin_update":
            success, text, _result = self._notice_execute_install_target(payload)
            return bool(success), text
        if kind == "mp_update":
            return self._notice_execute_moviepilot_fusion_action(context, payload)
        if kind == "market_update":
            return self._notice_execute_market_action()
        if kind == "card_refresh":
            # 底部「🔄 刷新」按钮：复用融合更新动作的流式状态通道，
            # 点下去立刻出现「⏳ 正在刷新卡片数据…」，采集结束后原地变成
            # 「✅ 已刷新 / ⚠️ 失败」，不再是点了没有任何反馈。
            # 标记本次刷新为交互式：底层不再自行 editMessageText，
            # 由动作 worker 统一重绘（running → success/error），避免连续闪两次。
            _FUSION_INTERACTIVE_REFRESH.active = True
            try:
                result = self.api_refresh_tg_console_card()
            finally:
                _FUSION_INTERACTIVE_REFRESH.active = False
            if isinstance(result, dict):
                ok = int(result.get("code") or 0) == 0
                return ok, str(result.get("msg") or ("融合通知卡已刷新" if ok else "融合通知卡刷新失败"))
            ok = bool(result)
            return ok, "融合通知卡已刷新" if ok else "融合通知卡刷新失败"
        return False, "未知更新操作。"

    @staticmethod
    def _fusion_tab_action_id(tab_key: str) -> str:
        return f"tab-refresh:{str(tab_key or '').strip()}"

    @classmethod
    def _fusion_tab_action_finish(cls, state: Dict[str, Any], action_id: str, ok: bool) -> bool:
        """把「正在补采」标记改成成功/失败；没有该标记时不做任何事。"""
        feed = state.get("fusion_action_feed")
        if not isinstance(feed, list):
            return False
        item = next((x for x in feed if isinstance(x, dict) and str(x.get("id") or "") == action_id), None)
        if not isinstance(item, dict):
            return False
        cls._fusion_action_feed_set(
            state, action_id, str(item.get("kind") or "card_refresh"),
            str(item.get("label") or "更新栏目"), "success" if ok else "error",
            "栏目数据已更新" if ok else "栏目数据更新失败")
        return True

    @staticmethod
    def _fusion_tab_action_remove(state: Dict[str, Any], action_id: str) -> bool:
        """用户已切走或运行时被取消：静默移除补采标记，不显示失败。"""
        feed = state.get("fusion_action_feed")
        if not isinstance(feed, list):
            return False
        kept = [x for x in feed if not (isinstance(x, dict) and str(x.get("id") or "") == action_id)]
        if len(kept) == len(feed):
            return False
        state["fusion_action_feed"] = kept
        return True

    def _start_fusion_tab_refresh(self, tab_key: str, token: str, chat_id: str) -> None:
        """后台采集当前页签数据，完成后原地更新卡片；不阻塞回调。"""
        generation = getattr(self, "_runtime_generation", 0)
        action_id = self._fusion_tab_action_id(tab_key)

        def work() -> None:
            try:
                state = self._tg_console_state(chat_id=chat_id)
                if str(state.get("active_tab") or "") != str(tab_key) or self._should_cancel(generation):
                    self._fusion_tab_action_remove(state, action_id)
                    self._save_tg_console_state(state)
                    return
                before = self._build_tg_console_rich_message(state)
                ok = bool(self._refresh_fusion_category(tab_key, state, force=False))
                # 采集期间用户可能又切了页签：只有仍停在本页签才回写，避免覆盖更新的视图
                if str(state.get("active_tab") or "") != str(tab_key) or self._should_cancel(generation):
                    self._fusion_tab_action_remove(state, action_id)
                    self._save_tg_console_state(state)
                    return
                # 补采结果显性化：把「正在更新」改成成功/失败。带标记时这一笔收尾
                # 编辑是必须的；没有标记（数据本就新鲜）时仍然遵守「内容没变不编辑」。
                finished = self._fusion_tab_action_finish(state, action_id, ok)
                changed = self._build_tg_console_rich_message(state) != before
                if changed or finished:
                    self._tg_console_upsert_card(token, chat_id, state, generation=generation)
                self._save_tg_console_state(state)
            except Exception as err:
                try:
                    state = self._tg_console_state(chat_id=chat_id)
                    self._fusion_tab_action_finish(state, action_id, False)
                    state["last_error"] = f"页签后台采集失败：{self._telegram_safe_error(err, limit=300)}"
                    self._save_tg_console_state(state)
                except Exception:
                    pass

        try:
            worker = threading.Thread(target=work, name="Signal-fusion-tab-refresh", daemon=True)
            worker.start()
        except Exception:
            logger.warning("Signal 页签后台采集线程未能启动")

    def _handle_tg_console_message(self, message: Dict[str, Any], update_id: int = 0) -> bool:
        token, chat_id, _source = self._resolve_fusion_telegram_config()
        state = self._tg_console_state(chat_id=chat_id)
        if update_id:
            state["last_update_id"] = max(self._safe_int(state.get("last_update_id"), 0, 0), int(update_id))
        msg_chat = ((message or {}).get("chat") or {}).get("id")
        user_id = str(((message or {}).get("from") or {}).get("id") or "")
        text = str((message or {}).get("text") or "").strip()
        if not self._tg_console_same_chat(msg_chat, chat_id):
            self._save_tg_console_state(state)
            return False
        if self._tg_console_allowed_user_ids and user_id not in self._tg_console_allowed_user_ids:
            self._save_tg_console_state(state)
            return False
        command = text.split()[0].split("@", 1)[0].lower() if text else ""
        command_map = {
            "/aoa_create": "create_tg_console_card",
            "/aoa_subscribe": "run_subscribe_reminder",
            "/aoa_site": "run_site_stat",
            "/aoa_transfer": "run_today_transfer",
            "/aoa_health": "run_health_check",
        }
        action_key = command_map.get(command)
        if not action_key:
            self._save_tg_console_state(state)
            return False
        ok, result = self._tg_console_execute_action(action_key, user_id=user_id)
        self._save_tg_console_state(self._tg_console_state(chat_id=chat_id))
        self._emit_console_notice(f"TG 指令 - {self._tg_console_action_registry().get(action_key, {}).get('label') or action_key}", result, "success" if ok else "error")
        return ok

    def _handle_tg_console_callback(self, callback: Dict[str, Any], update_id: int = 0) -> bool:
        token, chat_id, _source = self._resolve_fusion_telegram_config()
        state = self._tg_console_state(chat_id=chat_id)
        callback_id = str((callback or {}).get("id") or "")
        user_id = str(((callback or {}).get("from") or {}).get("id") or "")
        cb_chat = ((((callback or {}).get("message") or {}).get("chat") or {}).get("id"))
        data = str((callback or {}).get("data") or "")
        if update_id:
            state["last_update_id"] = max(self._safe_int(state.get("last_update_id"), 0, 0), int(update_id))
        processed = [str(x) for x in list(state.get("processed_callbacks") or []) if str(x)]
        if callback_id and callback_id in set(processed):
            self._save_tg_console_state(state)
            self._tg_console_answer_callback(callback_id, "重复回调已忽略")
            return True
        if callback_id:
            processed.append(callback_id)
            state["processed_callbacks"] = processed[-100:]
        tab_key = self._tg_console_callback_tab_key(data)
        if tab_key is not None:
            valid_columns = {x["key"] for x in self._fusion_column_registry()}
            enabled_columns = set(self._fusion_notify_columns or valid_columns) & valid_columns
            category_keys = {x["key"] for x in self._fusion_category_registry()}
            column_keys = {x["key"] for x in self._fusion_column_registry()}
            if tab_key not in category_keys and tab_key not in column_keys:
                self._save_tg_console_state(state)
                self._tg_console_answer_callback(callback_id, "未知栏目")
                return False
            active_tab = self._normalize_fusion_tab(tab_key)
            if not self._tg_console_same_chat(cb_chat, chat_id):
                self._save_tg_console_state(state)
                self._tg_console_answer_callback(callback_id, "会话不匹配")
                return False
            if self._tg_console_allowed_user_ids and user_id not in self._tg_console_allowed_user_ids:
                self._save_tg_console_state(state)
                self._tg_console_answer_callback(callback_id, "未授权的 Telegram 用户")
                return False
            # 「总览」这类页签本身没有子栏目，children 为空属于正常情况，
            # 只有「有子栏目但全部未启用」才拒绝切换。
            children = self._fusion_category_children(active_tab)
            if children and not any(child in enabled_columns for child in children):
                self._save_tg_console_state(state)
                self._tg_console_answer_callback(callback_id, "栏目未启用")
                return False
            state["active_tab"] = active_tab
            state["tab_touched"] = True
            # 页签内有过期栏目时，先把「正在更新该栏目」放进卡面再重绘：
            # 后台补采要几十秒，没有这条提示用户会以为点击没反应。
            tab_children = [child for child in self._fusion_category_children(active_tab) if child in enabled_columns]
            if any(not self._fusion_column_is_fresh(child, state) for child in tab_children):
                tab_label = next((str(x.get("label") or x.get("key") or "") for x in self._fusion_category_registry()
                                  if str(x.get("key") or "") == active_tab), active_tab)
                self._fusion_action_feed_set(state, self._fusion_tab_action_id(active_tab), "card_refresh",
                                             f"更新 {tab_label}".strip(), "running", "正在补采该栏目…")
            # 页签切换只保留一个可见动作：一次 editMessageText。实测（测试环境
            # 2026-09-27 21:47）宿主 telegram.py 轮询线程在把回调转给插件之前，
            # 已经自行 answerCallbackQuery 把按钮加载态复位；插件再抢答一次只是白白
            # 多花 0.3~1 秒，让「按钮已复位、卡片还没切」的空档变长，看起来就是不同步。
            # tab_seq 记录点击序号：连点多个页签时只有最后一次点击真正重绘，
            # 避免同一张卡连续重绘多次造成的闪烁。
            with self._tg_console_card_lock:
                self._fusion_tab_seq = int(getattr(self, "_fusion_tab_seq", 0) or 0) + 1
                tab_seq = self._fusion_tab_seq
            state["tab_seq"] = tab_seq
            # 页签切换必须立即生效：先按新页签重渲染卡片（一次 editMessageText），
            # 采集放到后台线程。采样动辄几十秒，放在回调里会堵住宿主的更新队列。
            try:
                with self._tg_console_card_lock:
                    if int(getattr(self, "_fusion_tab_seq", 0) or 0) != tab_seq:
                        # 期间用户又点了别的页签：让最新那次点击负责重绘，避免多余闪动。
                        self._save_tg_console_state(state)
                        return True
                    ok = bool(self._tg_console_upsert_card_locked(token, chat_id, state))
            except Exception as err:
                ok = False
                state["last_error"] = f"Telegram 融合通知栏目切换异常：{self._telegram_safe_error(err, limit=500)}"
            self._save_tg_console_state(state)
            if ok:
                self._start_fusion_tab_refresh(active_tab, token, chat_id)
            return bool(ok)
        nonce = self._tg_console_callback_action_nonce(data)
        if nonce is None:
            self._save_tg_console_state(state)
            self._tg_console_answer_callback(callback_id, "未知操作")
            return False
        if not self._tg_console_same_chat(cb_chat, chat_id):
            self._save_tg_console_state(state)
            self._tg_console_answer_callback(callback_id, "会话不匹配")
            return False
        if self._tg_console_allowed_user_ids and user_id not in self._tg_console_allowed_user_ids:
            self._save_tg_console_state(state)
            self._tg_console_answer_callback(callback_id, "未授权的 Telegram 用户")
            return False
        actions = state.setdefault("pending_actions", {})
        action = actions.get(nonce) or {}
        if not action or action.get("done"):
            self._save_tg_console_state(state)
            self._tg_console_answer_callback(callback_id, "操作已过期")
            return self._show_fusion_action_problem(state, callback, token, chat_id, user_id,
                "这个按钮已失效，已刷新卡片，请使用当前按钮。")
        now = datetime.now().timestamp()
        if action.get("expires_at") and float(action.get("expires_at") or 0) < now:
            action["done"] = True
            self._save_tg_console_state(state)
            self._tg_console_answer_callback(callback_id, "确认已过期")
            return self._show_fusion_action_problem(state, callback, token, chat_id, user_id,
                "这个确认已过期，已刷新卡片，请重新查看并确认。")
        if action.get("fusion_update"):
            return self._handle_fusion_update_action(nonce, action, callback, state, token, chat_id, user_id)
        registry = self._tg_console_action_registry()
        if action.get("confirm_for"):
            original = actions.get(action.get("confirm_for")) or {}
            original_key = str(original.get("action") or "")
            if original_key not in registry:
                action["done"] = True
                original["done"] = True
                self._save_tg_console_state(state)
                self._tg_console_answer_callback(callback_id, "未知操作")
                return False
            if str(original.get("user_id") or "") != user_id:
                self._save_tg_console_state(state)
                self._tg_console_answer_callback(callback_id, "只能由发起人确认")
                return False
            ok, message = self._tg_console_execute_action(str(original.get("action") or ""), user_id=user_id)
            action["done"] = True
            original["done"] = True
            self._save_tg_console_state(state)
            self._emit_console_notice(f"TG 远控 - {original.get('label') or original.get('action')}", message, "success" if ok else "error")
            self._tg_console_answer_callback(callback_id, "已执行" if ok else "执行失败")
            return ok
        action_key = str(action.get("action") or "")
        if action_key not in registry:
            action["done"] = True
            self._save_tg_console_state(state)
            self._tg_console_answer_callback(callback_id, "未知操作")
            return False
        if action.get("destructive"):
            confirm_nonce = self._tg_console_new_nonce(actions)
            actions[confirm_nonce] = {
                "action": action.get("action"),
                "label": f"确认 {action.get('label') or action.get('action')}",
                "user_id": user_id,
                "confirm_for": nonce,
                "expires_at": now + 60,
                "destructive": False,
                "created_at": now,
            }
            action["user_id"] = user_id
            self._save_tg_console_state(state)
            self._emit_console_notice("TG 远控等待确认", f"{action.get('label')} 需要 60 秒内二次确认", "warning")
            self._tg_console_answer_callback(callback_id, "请在 60 秒内再次确认")
            return True
        label = str(action.get("label") or action.get("action") or action_key)
        if action.get("background"):
            # 长任务（如整卡刷新要重跑站点采集，几十秒）放到后台执行，
            # 先把回调确认掉，宿主更新队列就不会被堵住。
            action["done"] = True
            self._save_tg_console_state(state)
            self._tg_console_answer_callback(callback_id, "已开始")
            self._tg_console_start_background_action(action_key, label, user_id)
            return True
        ok, message = self._tg_console_execute_action(action_key, user_id=user_id)
        action["done"] = True
        self._save_tg_console_state(state)
        self._emit_console_notice(f"TG 远控 - {label}", message, "success" if ok else "error")
        self._tg_console_answer_callback(callback_id, "已执行" if ok else "执行失败")
        return ok

    def _tg_console_execute_action(self, action_key: str, user_id: Optional[str] = None) -> Tuple[bool, str]:
        registry = self._tg_console_action_registry()
        action = registry.get(action_key)
        if not action:
            return False, "未知操作"
        if not self._enabled:
            return False, "插件未启用"
        component = action.get("component")
        if component and not self._component_enabled(component):
            return False, f"{action.get('label')} 未启用"
        try:
            result = action["runner"]()
            if isinstance(result, dict):
                ok = result.get("code") == 0
                return ok, str(result.get("msg") or ("执行成功" if ok else "执行失败"))
            ok = bool(result)
            return ok, f"{action.get('label')}执行{'成功' if ok else '失败'}"
        except Exception as err:
            logger.error(f"Signal TG 远控 {action_key} 执行失败：{err}")
            return False, str(err)

    def _tg_console_action_registry(self) -> Dict[str, Dict[str, Any]]:
        return {
            "create_tg_console_card": {"label": "立即建卡", "runner": self.api_create_tg_console_card, "component": "", "destructive": False},
            "refresh_tg_console_card": {"label": "立即刷新", "runner": self.api_refresh_tg_console_card, "component": "fusion_notify",
                                        "destructive": False, "background": True},
            "run_subscribe_reminder": {"label": "订阅追新", "runner": self.api_run_subscribe_reminder, "component": "subscribe_reminder", "destructive": False},
            "run_site_stat": {"label": "站点统计", "runner": self.api_run_site_stat, "component": "site_stat", "destructive": False},
            "run_today_transfer": {"label": "今日入库", "runner": self.api_run_today_transfer, "component": "", "destructive": False},
            "run_health_check": {"label": "健康巡查", "runner": self.api_run_health_check, "component": "health_check", "destructive": False},
            "run_mp_update_apply": {"label": "立即更新", "runner": self.api_run_mp_update_apply, "component": "mp_update", "destructive": True},
        }

    def _tg_console_action_groups(self) -> List[List[str]]:
        return [
            ["create_tg_console_card", "refresh_tg_console_card"],
            ["run_site_stat", "run_today_transfer"],
        ]

    @classmethod
    def _tg_console_callback_tab_key(cls, data: str) -> Optional[str]:
        raw = cls._tg_console_unwrap_plugin_callback(data)
        if raw.startswith("aoatab:"):
            key = raw.split(":", 1)[1].split("?", 1)[0].strip()
            return "system" if key in {"health", "storage", "maintenance", "system_health", "system_maintenance"} else key
        if raw.startswith("aoa:tab:"):
            key = raw.split(":", 2)[-1].split("?", 1)[0].strip()
            return "system" if key in {"health", "storage", "maintenance", "system_health", "system_maintenance"} else key
        return None

    @classmethod
    def _tg_console_callback_action_nonce(cls, data: str) -> Optional[str]:
        raw = cls._tg_console_unwrap_plugin_callback(data)
        if raw.startswith("aoav1:"):
            return raw.split(":", 1)[1].split("?", 1)[0].strip()
        if raw.startswith("aoa:v1:"):
            return raw.split(":", 2)[-1].split("?", 1)[0].strip()
        return None

    @classmethod
    def _tg_console_plugin_callback_data(cls, payload: str) -> str:
        return f"[PLUGIN]{cls.__name__}|{str(payload or '').strip()}"

    @classmethod
    def _tg_console_unwrap_plugin_callback(cls, data: str) -> str:
        raw = str(data or "").strip()
        if raw.startswith("[PLUGIN]"):
            try:
                plugin_id, payload = raw.split("|", 1)
            except ValueError:
                return raw
            plugin_name = plugin_id.replace("[PLUGIN]", "").strip()
            if plugin_name.lower() in {cls.__name__.lower(), "signal"}:
                return payload.strip()
        return raw

    @staticmethod
    def _telegram_message_not_modified_error(value: Any) -> bool:
        text = str(value or "").lower()
        return "message is not modified" in text or "message not modified" in text

    def _tg_console_upsert_card(self, token: str, chat_id: str, state: Dict[str, Any], *, generation: Optional[int] = None) -> bool:
        # Telegram can cancel an edit when another edit of the same card arrives.
        with self._tg_console_card_lock:
            if generation is not None and self._should_cancel(generation):
                return False
            return self._tg_console_upsert_card_locked(token, chat_id, state)

    def _tg_console_upsert_card_locked(self, token: str, chat_id: str, state: Dict[str, Any]) -> bool:
        ok, _ = self._runtime_gate("telegram", component="fusion_notify", name="Telegram fusion card upsert")
        if not ok:
            return False
        base_url = f"https://api.telegram.org/bot{token}"
        rich_message = self._build_tg_console_rich_message(state)
        reply_markup = self._build_tg_console_reply_markup(state)
        # 渲染更新按钮时会在 state.pending_actions 里生成 nonce；必须先落盘，
        # 否则用户点下刚发出的按钮时，回调进程在数据库里找不到它。
        save_state = getattr(self, "_save_tg_console_state", None)
        if callable(save_state):
            save_state(state)
        if state.get("message_id"):
            payload = build_edit_message_text_payload(chat_id, state.get("message_id"), rich_message, reply_markup)
            started = time.monotonic()
            ok = unchanged = False
            for attempt in range(3):
                try:
                    res = self._telegram_http_post_json(f"{base_url}/editMessageText", payload, timeout=15)
                except Exception as err:
                    self._tg_console_last_error = f"Telegram editMessageText 异常：{self._telegram_safe_error(err, limit=300)}"
                    if attempt < 2:
                        time.sleep(0.6 * (attempt + 1))
                        continue
                    raise
                ok, _ = self._telegram_response_data(res, "editMessageText")
                unchanged = self._telegram_message_not_modified_error(getattr(self, "_tg_console_last_error", ""))
                if ok or unchanged:
                    break
                if attempt < 2 and self._telegram_edit_error_is_retryable(self._tg_console_last_error):
                    time.sleep(0.6 * (attempt + 1))
                    continue
                break
            logger.debug(
                "Signal 融合卡 editMessageText "
                f"tab={state.get('active_tab')} ok={bool(ok)} unchanged={unchanged} "
                f"elapsed={int((time.monotonic() - started) * 1000)}ms"
            )
            if ok or unchanged:
                self._tg_console_last_error = ""
                state["last_error"] = ""
                state.pop("card_pending_edit", None)
                return True
            # 状态已变但编辑没成功：记一笔待补发，下一次定时任务会重试，
            # 避免卡片与真实状态长期不一致（例如媒体结束后仍显示旧会话）。
            state["last_error"] = self._tg_console_last_error
            state["card_pending_edit"] = True
            if callable(save_state):
                save_state(state)
            return False
        payload = build_send_rich_message_payload(chat_id, rich_message, reply_markup)
        res = self._telegram_http_post_json(f"{base_url}/sendRichMessage", payload, timeout=15)
        ok, data = self._telegram_response_data(res, "sendRichMessage")
        if ok:
            result = data.get("result") or {}
            if isinstance(result, dict):
                state["message_id"] = self._safe_int(result.get("message_id"), 0, 0)
            self._tg_console_last_error = ""
            state["last_error"] = ""
            state.pop("card_pending_edit", None)
            return True
        state["last_error"] = self._tg_console_last_error
        state["card_pending_edit"] = True
        if callable(save_state):
            save_state(state)
        return False

    @staticmethod
    def _telegram_edit_error_is_retryable(value: Any) -> bool:
        text = str(value or "").lower()
        return any(marker in text for marker in (
            "timeout", "timed out", "ssl", "unexpected_eof", "connection reset",
            "connection aborted", "max retries exceeded", "http 5", "http 429",
            "bad gateway", "gateway timeout", "service unavailable",
        ))

    def _tg_console_send_rich_message_draft(self, token: str, chat_id: str, draft_id: int, state: Dict[str, Any]) -> bool:
        """Send an ephemeral draft only when the caller has a proven private-chat route."""
        ok, _ = self._runtime_gate("telegram", component="fusion_notify", name="Telegram sendRichMessageDraft")
        if not ok:
            return False
        payload = build_send_rich_message_draft_payload(chat_id, draft_id, self._build_tg_console_rich_message(state))
        res = self._telegram_http_post_json(f"https://api.telegram.org/bot{token}/sendRichMessageDraft", payload, timeout=15)
        ok, _ = self._telegram_response_data(res, "sendRichMessageDraft")
        return ok

    def _tg_console_answer_callback(self, callback_query_id: str, text: str = "") -> bool:
        if not callback_query_id:
            return False
        ok, _ = self._runtime_gate("telegram", component="fusion_notify", name="Telegram answerCallbackQuery")
        if not ok:
            return False
        token, _chat_id, _source = self._resolve_fusion_telegram_config()
        if not token:
            return False
        payload = {"callback_query_id": callback_query_id}
        if text:
            payload["text"] = str(text)[:180]
        res = self._telegram_http_post_json(f"https://api.telegram.org/bot{token}/answerCallbackQuery", payload, timeout=10)
        ok, _ = self._telegram_response_data(res, "answerCallbackQuery")
        return ok

    @staticmethod
    def _tg_console_same_chat(callback_chat_id: Any, expected_chat_id: Any) -> bool:
        if expected_chat_id in (None, ""):
            return True
        return str(callback_chat_id or "").strip() == str(expected_chat_id or "").strip()
