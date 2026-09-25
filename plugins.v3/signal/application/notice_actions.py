"""Persisted actions owned by individual non-fusion notifications."""
from copy import deepcopy
from contextlib import nullcontext
import secrets
import sys
import threading
import time
from types import ModuleType

from app.sdk.logging import logger

from ..domain.notice_actions import ACTIVE, COMPONENTS, STATE_KEY, TTL_SECONDS, new_state, parse_callback, prune, target_identity, target_key
from ..infrastructure import notice_transport


def _process_runtime():
    name = "_signal_notice_action_runtime"
    runtime = ModuleType(name)
    runtime.lock = threading.RLock()
    runtime.workers = {}
    return sys.modules.setdefault(name, runtime)


NOTICE_RUNTIME = _process_runtime()


class NoticeActionsMixin:
    _notice_lock = NOTICE_RUNTIME.lock

    @staticmethod
    def _notice_now():
        return time.time()

    def _notice_load(self):
        return prune(new_state(deepcopy(self.get_data(STATE_KEY))), self._notice_now())

    def _notice_save(self, state):
        if self.save_data(STATE_KEY, deepcopy(state)) is False:
            raise RuntimeError("通知操作状态保存失败")

    def _notice_targets(self, mtype):
        return notice_transport.notification_targets(mtype)

    def _notice_target(self, record):
        return next((target for target in self._notice_targets(record["mtype"])
                     if target["source"] == record["source"] and target["chat_id"] == record["chat_id"]
                     and notice_transport.can_interact(target)), None)

    def _notice_allowed(self, kind):
        if kind not in COMPONENTS or getattr(self, "_fusion_notify_enabled", False):
            return False
        ok, _ = self._runtime_gate("action", component=COMPONENTS[kind], name="通知交互")
        return bool(ok)

    def _notice_deliver(self, payload, action):
        """Return None to retain the normal host path, otherwise delivery status."""
        kind = (action or {}).get("kind")
        if not self._notice_allowed(kind):
            return None
        try:
            targets = self._notice_targets(payload.get("mtype"))
        except Exception:
            return None
        if not any(notice_transport.can_interact(target) for target in targets):
            return None
        sent = True
        for target in targets:
            if not notice_transport.can_interact(target):
                self.post_message(**{**payload, "source": target["source"]})
                continue
            try:
                with self._notice_lock:
                    state = self._notice_load()
                    action_payload = deepcopy(action.get("payload") or {})
                    if kind == "plugin_update":
                        action_payload["plugins"] = [item for item in action_payload.get("plugins", [])
                            if state["ignored_versions"].get(target_key(target["source"], item)) != str(item.get("new") or "")]
                        if not action_payload["plugins"]:
                            continue
                    nonce = secrets.token_urlsafe(9)
                    now = self._notice_now()
                    record = {"nonce": nonce, "kind": kind, "payload": action_payload,
                              "source": target["source"], "chat_id": target["chat_id"], "message_id": 0,
                              "mtype": str(getattr(payload.get("mtype"), "value", payload.get("mtype"))),
                              "created_at": now, "expires_at": now + TTL_SECONDS, "status": "ready", "page": 0,
                              "initial_pending": True,
                              "text": "\n".join(str(payload.get(key) or "") for key in ("title", "text")).strip()}
                    record["detail"] = str(action.get("detail") or record["text"])
                    formatter = getattr(self, "_format_plugin_update_text", None)
                    if kind == "plugin_update" and callable(formatter):
                        items = action_payload["plugins"]
                        record["text"] = formatter({"auto_install": False, "updatable": items})
                        record["detail"] = record["text"] + "\n\n" + "\n\n".join(
                            f"{item.get('name') or item.get('id')}：{item.get('history') or '未提供更新说明'}"
                            + (f"\n{item['blocked']}" if item.get("blocked") else "") for item in items)
                    state["records"][nonce] = record
                    self._notice_save(state)
                    if not notice_transport.enqueue_notice(self, nonce):
                        state = self._notice_load()
                        state["records"].pop(nonce, None)
                        self._notice_save(state)
                        self.post_message(**{**payload, "source": target["source"]})
            except Exception:
                logger.warning("Signal 普通 TG 交互通知投递失败")
                sent = False
        return sent

    def _notice_publish(self, nonce, target=None):
        """Persist message identity and retry only output, never business actions."""
        with self._notice_lock:
            state = self._notice_load()
            record = state["records"].get(nonce)
            if not record or not self._notice_allowed(record["kind"]):
                return False
            if record.get("initial_pending") and record["kind"] == "plugin_update":
                remaining = [item for item in record["payload"].get("plugins", [])
                             if state["ignored_versions"].get(target_key(record["source"], item)) != str(item.get("new") or "")]
                if not remaining or getattr(self, "_plugin_auto_install_enabled", False):
                    record.update(status="dismissed", initial_pending=False)
                    self._notice_save(state)
                    return True
            target = target or self._notice_target(record)
            if not target:
                return False
            generation = getattr(self, "_runtime_generation", 0)
            expected = (record.get("claim_id"), record.get("status"), record.get("message_id"))
            text, buttons = self._notice_render(record, native_update=notice_transport.moviepilot_update_available(),
                                                host_url=notice_transport.moviepilot_url())
            try:
                if self._should_cancel(generation):
                    return False
                message_id = notice_transport.telegram_message(self, target, text, buttons, record.get("message_id"))
                if not message_id:
                    raise RuntimeError("通知缺少消息标识")
                if self._should_cancel(generation):
                    return False
                state = self._notice_load()
                record = state["records"].get(nonce)
                if not record or (record.get("claim_id"), record.get("status"), record.get("message_id")) != expected:
                    return False
                record["message_id"] = message_id
                record.pop("initial_pending", None)
                record.pop("delivery_error", None)
                record.pop("delivery_retry_at", None)
                record.pop("delivery_attempts", None)
                self._notice_save(state)
                return True
            except Exception:
                if self._should_cancel(generation):
                    return False
                state = self._notice_load()
                record = state["records"].get(nonce)
                if not record or (record.get("claim_id"), record.get("status"), record.get("message_id")) != expected:
                    return False
                record["delivery_error"] = True
                attempts = int(record.get("delivery_attempts", 0)) + 1
                record["delivery_attempts"] = attempts
                if record.get("message_id") and attempts < 3:
                    record["delivery_retry_at"] = self._notice_now() + 30 * attempts
                else:
                    record.pop("delivery_retry_at", None)
                self._notice_save(state)
                self._notice_schedule_wakeup()
                return False

    def _notice_handle_action(self, info):
        parsed = parse_callback(info.get("text"))
        if not parsed:
            return False
        nonce, action, index = parsed
        try:
            with self._notice_lock:
                state = self._notice_load()
                record = state["records"].get(nonce)
                channel = str(getattr(info.get("channel"), "value", info.get("channel"))).lower()
                if not record or channel != "telegram" or not self._notice_allowed(record["kind"]):
                    return False
                target = self._notice_target(record)
                if (not target or str(info.get("userid")) not in target["admins"]
                        or str(info.get("source")) != record["source"]
                        or str(info.get("original_chat_id")) != record["chat_id"]
                        or str(info.get("original_message_id")) != str(record.get("message_id"))
                        or not record.get("message_id") or record.get("expires_at", 0) < self._notice_now()):
                    return False
                self._notice_reconcile_plugins()
                state = self._notice_load()
                record = state["records"].get(nonce)
                if not record:
                    return False
                allowed = {"plugin_update": {"details", "back", "page", "install", "remind", "ignore"},
                           "mp_update": {"details", "back", "mp"}, "site_stat": {"details", "back", "page", "refresh"}}
                if action not in allowed[record["kind"]] or record["status"] in ACTIVE | {"handed_off"}:
                    return False
                if action in {"install", "mp", "remind", "ignore"} and record["status"] != "ready":
                    return False
                if action in {"install", "remind", "ignore"} and getattr(self, "_plugin_auto_install_enabled", False):
                    return False
                if action == "details":
                    record.update(view="details", page=0)
                elif action == "back":
                    record.update(view="summary", page=0)
                elif action == "page":
                    if index is None:
                        return False
                    record["page"] = index
                elif action in {"remind", "ignore"}:
                    items = record["payload"].get("plugins", [])
                    if action == "ignore":
                        for item in items:
                            state["ignored_versions"][target_key(record["source"], item)] = str(item.get("new") or "")
                        record.update(status="dismissed", text="已忽略这批插件的目标版本；后续新版本仍会提醒。")
                    else:
                        record.update(status="snoozed", remind_at=self._notice_now() + 3600,
                                      expires_at=max(record["expires_at"], self._notice_now() + 86400),
                                      text="1 小时后再次提醒这批更新；不会自动安装。")
                else:
                    selected = None
                    if action == "install":
                        items = record["payload"].get("plugins", [])
                        if index is None or index >= len(items) or items[index].get("completed") or items[index].get("blocked"):
                            return False
                        selected = deepcopy(items[index])
                        for other in state["records"].values():
                            if other.get("status") in ACTIVE and str((other.get("selected") or {}).get("id")) == str(selected["id"]):
                                return False
                    record.update(status="running", selected=selected, actor_id=str(info["userid"]),
                                  claim_id=secrets.token_hex(8), claim_generation=getattr(self, "_runtime_generation", 0),
                                  view="summary", text={"install": "正在更新所选插件…", "mp": "正在读取 MoviePilot 更新状态…", "refresh": "正在采集站点数据，完成后更新本条通知。"}[action])
                self._notice_save(state)
                worker_context = {**info, "_notice_claim_id": record.get("claim_id"),
                                  "_notice_generation": record.get("claim_generation")}
            self._notice_publish(nonce)
            if action in {"install", "mp", "refresh"}:
                self._notice_start_worker(nonce, action, worker_context)
            elif action == "remind":
                self._notice_schedule_wakeup()
            return True
        except Exception:
            logger.warning("Signal 通知操作未执行或状态保存失败")
            return False

    def _notice_start_worker(self, nonce, action, context):
        generation = context["_notice_generation"]
        with self._notice_lock:
            record = self._notice_load()["records"].get(nonce)
            if not self._notice_claim_valid(record, context, generation):
                return False
            worker = threading.Thread(target=self._notice_worker, args=(nonce, action, context, generation),
                                      name="Signal-notice-action", daemon=True)
            NOTICE_RUNTIME.workers[context["_notice_claim_id"]] = worker
            try:
                worker.start()
            except Exception:
                NOTICE_RUNTIME.workers.pop(context["_notice_claim_id"], None)
                state = self._notice_load()
                record = state["records"].get(nonce)
                if self._notice_claim_valid(record, context, generation):
                    record.update(status="ready", text="任务未能启动，请重试。", selected=None, site_waiting=False)
                    self._notice_save(state)
                self._notice_publish(nonce)
                return False
        return True

    def _notice_claim_valid(self, record, context, generation):
        return bool(record and not self._should_cancel(generation) and record.get("status") == "running"
                    and record.get("claim_generation") == generation
                    and record.get("claim_id") == context.get("_notice_claim_id"))

    def _notice_worker(self, nonce, action, context, generation):
        try:
            if self._should_cancel(generation):
                return
            runner = getattr(self, {"install": "_notice_run_install", "mp": "_notice_run_mp",
                                    "refresh": "_notice_run_site"}[action])
            runner(nonce, context, generation)
        except Exception:
            changed = False
            with self._notice_lock:
                state = self._notice_load()
                record = state["records"].get(nonce)
                if self._notice_claim_valid(record, context, generation):
                    record.update(status="failed" if action == "refresh" else "uncertain",
                                  site_waiting=False,
                                  text="站点刷新检查失败，请稍后重试。" if action == "refresh" else "操作中断，执行结果待核实；请先检查实际状态，不要重复执行。")
                    self._notice_save(state)
                    changed = True
            if changed and not self._should_cancel(generation):
                self._notice_publish(nonce)
        finally:
            with self._notice_lock:
                NOTICE_RUNTIME.workers.pop(context.get("_notice_claim_id"), None)

    def _notice_busy_plugin_ids(self):
        self._notice_reconcile_plugins()
        with self._notice_lock:
            return {str(record["selected"]["id"]) for record in self._notice_load()["records"].values()
                    if record.get("status") in ACTIVE and record.get("selected")}

    def _notice_reconcile_plugins(self):
        """Release interrupted claims only after the worker exited and version is known."""
        resolved = []
        with self._notice_lock:
            state = self._notice_load()
            pending = [record for record in state["records"].values()
                       if record.get("status") == "uncertain" and record.get("selected")
                       and record.get("claim_id") not in NOTICE_RUNTIME.workers]
            if not pending or self._should_cancel():
                return
            try:
                versions = notice_transport.installed_plugin_versions()
            except Exception:
                return
            for record in pending:
                selected = record["selected"]
                actual = versions.get(str(selected["id"]))
                if not actual or actual != str(selected.get("new")):
                    continue
                for item in record["payload"].get("plugins", []):
                    if target_identity(item) == target_identity(selected):
                        item["completed"] = True
                remaining = any(not item.get("completed") and not item.get("blocked") for item in record["payload"].get("plugins", []))
                record.update(status="ready" if remaining else "done", selected=None,
                              text=f"已核实 {selected.get('name') or selected['id']} 当前版本为 {actual}；不会重复更新。")
                record["detail"] = record["text"]
                resolved.append(record["nonce"])
            if resolved:
                self._notice_save(state)
        for nonce in resolved:
            self._notice_publish(nonce)

    def _notice_run_mp(self, nonce, context, generation):
        with self._notice_lock:
            state = self._notice_load()
            record = state["records"].get(nonce)
            target = self._notice_target(record) if record else None
            if (not self._notice_claim_valid(record, context, generation) or not target or str(context["userid"]) not in target["admins"]
                    or not self._notice_allowed("mp_update") or self._should_cancel(generation)):
                raise RuntimeError("更新条件已改变")
        try:
            if not notice_transport.moviepilot_update_available():
                raise RuntimeError("当前宿主没有通知更新入口")
            handled = notice_transport.start_moviepilot_update(context)
            if not handled:
                raise RuntimeError("宿主未处理更新会话")
        except Exception:
            changed = False
            with self._notice_lock:
                state = self._notice_load()
                record = state["records"].get(nonce)
                if self._notice_claim_valid(record, context, generation):
                    record.update(status="failed", text="当前无法打开宿主更新流程，请从 MoviePilot 设置页处理。")
                    self._notice_save(state)
                    changed = True
            if changed and not self._should_cancel(generation):
                self._notice_publish(nonce)
            return
        if not self._should_cancel(generation):
            with self._notice_lock:
                state = self._notice_load()
                record = state["records"].get(nonce)
                if self._notice_claim_valid(record, context, generation):
                    record.update(status="handed_off", text="已进入 MoviePilot 原生更新流程。")
                    for key in ("delivery_error", "delivery_retry_at", "delivery_attempts"):
                        record.pop(key, None)
                    self._notice_save(state)
            self._notice_schedule_wakeup()
        # The host owns the original message and native update: callbacks now.
        # Do not replace its download/restart keyboard with a Signal result.

    def _notice_run_install(self, nonce, context, generation):
        with self._notice_lock:
            record = self._notice_load()["records"].get(nonce)
            target = self._notice_target(record) if record else None
            if (not self._notice_claim_valid(record, context, generation) or not target or str(context["userid"]) not in target["admins"]
                    or not self._notice_allowed("plugin_update") or self._should_cancel(generation)
                    or getattr(self, "_plugin_auto_install_enabled", False)):
                raise RuntimeError("更新条件已改变")
            selected = deepcopy(record["selected"])
        result = self._auto_update_installed_plugins(apply=True, manual_targets=[selected])
        if self._should_cancel(generation):
            return
        updated = result.get("updated") or []
        current = [item for item in result.get("skipped", []) if item.get("already_current")]
        success = bool(updated or current) and not result.get("error") and not result.get("failed")
        if success:
            text = f"{selected.get('name') or selected['id']} 已更新至 {selected['new']}，版本已核实。"
        else:
            text = f"{selected.get('name') or selected['id']} 更新未完成，请查看详情后重新检查更新。"
        formatter = getattr(self, "_format_plugin_update_text", None)
        detail = formatter(result) if callable(formatter) else text
        with self._notice_lock:
            state = self._notice_load()
            record = state["records"].get(nonce)
            if not self._notice_claim_valid(record, context, generation):
                return
            for item in record["payload"].get("plugins", []):
                if target_identity(item) == target_identity(selected):
                    item["completed"] = True
            remaining = any(not item.get("completed") and not item.get("blocked") for item in record["payload"].get("plugins", []))
            record.update(status="ready" if remaining else "done", text=text, detail=str(detail), result=result)
            record.pop("selected", None)
            self._notice_save(state)
        self._notice_publish(nonce)

    def _notice_run_site(self, nonce, context, generation):
        with self._notice_lock:
            state = self._notice_load()
            record = state["records"].get(nonce)
            target = self._notice_target(record) if record else None
            if (not self._notice_claim_valid(record, context, generation) or not target or str(context["userid"]) not in target["admins"]
                    or not self._notice_allowed("site_stat") or self._should_cancel(generation)):
                raise RuntimeError("采集条件已改变")
            record.update(site_day=self._today_prefix(), refresh_generation=generation, site_waiting=True)
            record.pop("site_fingerprint", None)
            record.pop("operation_id", None)
            self._notice_save(state)
        scope = getattr(self, "_site_refresh_completion_scope", nullcontext)
        with scope():
            result = self._refresh_site_userdata_coordinated(source="notice_site", generation=generation)
            if self._should_cancel(generation):
                return
            with self._notice_lock:
                state = self._notice_load()
                record = state["records"].get(nonce)
                if not self._notice_claim_valid(record, context, generation):
                    return
                record["operation_id"] = str(result.get("operation_id") or "")
                record["status"] = "pending" if result.get("pending") else "running"
                self._notice_save(state)
            if result.get("pending"):
                # The completion callback can run before operation_id was bound.
                latest = self._site_refresh_result_for_operation(record["operation_id"])
                if latest and not latest.get("pending") and latest.get("status") != "running":
                    self._notice_complete_site(nonce, latest, generation)
                else:
                    self._notice_publish(nonce)
                self._notice_schedule_wakeup()
            else:
                self._notice_complete_site(nonce, result, generation)

    def _notice_settle_site_refresh(self, result, *, generation=None):
        generation = getattr(self, "_runtime_generation", 0) if generation is None else generation
        if (not isinstance(result, dict) or not result.get("operation_id") or result.get("pending")
                or result.get("status") == "running" or self._should_cancel(generation)):
            return
        with self._notice_lock:
            matching = [nonce for nonce, record in self._notice_load()["records"].items()
                        if record.get("kind") == "site_stat" and record.get("site_waiting")
                        and record.get("operation_id") == result["operation_id"]
                        and record.get("refresh_generation") == generation]
        for nonce in matching:
            self._notice_complete_site(nonce, result, generation)

    def _notice_complete_site(self, nonce, result, generation):
        with self._notice_lock:
            state = self._notice_load()
            record = state["records"].get(nonce)
            if (not record or not record.get("site_waiting") or self._should_cancel(generation)
                    or not self._notice_allowed("site_stat") or record.get("refresh_generation") != generation
                    or str(result.get("operation_id") or "") != record.get("operation_id", "")):
                return False
            fingerprint = [result.get("operation_id"), result.get("status"), result.get("finished_at")]
            expected_claim = record.get("claim_id")
            if record.get("site_fingerprint") == fingerprint:
                return False
            if record.get("site_day") != self._today_prefix() or result.get("data_date", record["site_day"]) != record["site_day"]:
                text, detail, status, waiting = "本次刷新已跨日，请重新刷新今日数据。", "本次旧数据未写入通知。", "failed", False
            elif result.get("success") is False or result.get("status") in {"timeout", "cancelled", "error"}:
                text = self._site_refresh_failure_message(result) or "站点刷新未完成"
                detail, status, waiting = text, "failed", result.get("status") == "timeout"
            else:
                snapshot = self._site_increment_snapshot(refresh_result=result)
                states = list(snapshot.get("site_states") or [])
                counted = self._site_state_counted(states)
                active = int(snapshot.get("active_count") or 0)
                stamp = snapshot.get("latest_updated_at") or snapshot.get("refresh_at") or result.get("finished_at") or "未知"
                if snapshot.get("error"):
                    summary, status = "站点统计检查失败，请查看逐站结果。", "failed"
                elif not counted and active:
                    summary, status = "今日增量暂不可用，请查看逐站原因。", "failed"
                else:
                    summary = (f"站点统计：可统计 {len(counted)}/{active} 站｜今日上传 {self._format_bytes(snapshot.get('upload_total', 0))}"
                               f"｜下载 {self._format_bytes(snapshot.get('download_total', 0))}") if active else "未启用 PT 站点"
                    status = "done"
                summary += f"\n数据时间：{stamp}"
                text = self._format_site_stat_success_notification(snapshot, summary, states)
                detail, waiting = text, False
            # Snapshot/formatting can enter host code and synchronously reload
            # the plugin. Reload the ledger instead of committing the old copy.
            state = self._notice_load()
            record = state["records"].get(nonce)
            if (not record or self._should_cancel(generation) or not self._notice_allowed("site_stat")
                    or not record.get("site_waiting") or record.get("refresh_generation") != generation
                    or record.get("claim_id") != expected_claim
                    or str(result.get("operation_id") or "") != record.get("operation_id", "")):
                return False
            record.update(status=status, text=text, detail=detail, page=0, view="summary", site_waiting=waiting,
                          site_fingerprint=fingerprint)
            self._notice_save(state)
        self._notice_publish(nonce)
        return True

    def _notice_schedule_wakeup(self):
        """Only a persisted reminder/output timer, not a second business scheduler."""
        with self._notice_lock:
            previous = getattr(self, "_notice_timer", None)
            if previous is not None:
                previous.cancel()
                self._untrack_runtime_timer(previous)
            due = [record["remind_at"] for record in self._notice_load()["records"].values()
                   if record.get("remind_at") and record.get("status") == "snoozed"]
            if any(record.get("site_waiting") for record in self._notice_load()["records"].values()):
                due.append(self._notice_now() + 5)
            due.extend(record["delivery_retry_at"] for record in self._notice_load()["records"].values()
                       if record.get("delivery_retry_at") and record.get("message_id")
                       and record.get("status") != "handed_off"
                       and self._notice_allowed(record["kind"]))
            if not due or self._should_cancel():
                self._notice_timer = None
                return
            generation = getattr(self, "_runtime_generation", 0)
            timer = self._track_runtime_timer(threading.Timer(max(1, min(due) - self._notice_now()), self._notice_tick, args=(generation,)))
            timer.daemon = True
            self._notice_timer = timer
            timer.start()

    def _notice_tick(self, generation):
        if self._should_cancel(generation):
            return
        with self._notice_lock:
            state = self._notice_load()
            ready = []
            for nonce, record in state["records"].items():
                if record.get("status") == "snoozed" and record.get("remind_at", float("inf")) <= self._notice_now():
                    record.pop("remind_at", None)
                    record.update(status="ready", message_id=0, initial_pending=True, text=record.get("detail") or "插件更新提醒")
                    ready.append(nonce)
            self._notice_save(state)
        for nonce in ready:
            if not notice_transport.enqueue_notice(self, nonce):
                with self._notice_lock:
                    state = self._notice_load()
                    record = state["records"].get(nonce)
                    if record:
                        attempts = int(record.get("reminder_attempts", 0)) + 1
                        record["reminder_attempts"] = attempts
                        record.update(status="snoozed" if attempts < 3 else "failed")
                        if attempts < 3:
                            record["remind_at"] = self._notice_now() + 300
                        self._notice_save(state)
        self._notice_recover_sites(generation)
        self._notice_retry_delivery(generation)
        self._notice_schedule_wakeup()

    def _notice_retry_delivery(self, generation, *, restart=False):
        if self._should_cancel(generation):
            return
        with self._notice_lock:
            state = self._notice_load()
            due = []
            for nonce, record in state["records"].items():
                if (not record.get("delivery_error") or not record.get("message_id")
                        or record.get("status") == "handed_off" or not self._notice_allowed(record["kind"])):
                    continue
                if restart:
                    record["delivery_attempts"] = 0
                    record["delivery_retry_at"] = self._notice_now()
                if record.get("delivery_retry_at", float("inf")) <= self._notice_now():
                    due.append(nonce)
                    # Consume this retry even if the source was removed; an
                    # unavailable target must not create a one-second loop.
                    record.pop("delivery_retry_at", None)
            self._notice_save(state)
        for nonce in due:
            self._notice_publish(nonce)

    def _notice_recover_sites(self, generation):
        with self._notice_lock:
            pending = [(nonce, record.get("operation_id")) for nonce, record in self._notice_load()["records"].items()
                       if record.get("site_waiting") and record.get("operation_id")]
        for nonce, operation_id in pending:
            result = self._site_refresh_result_for_operation(operation_id)
            inflight_reader = getattr(self, "_site_refresh_inflight_snapshot", None)
            if result and (result.get("pending") or result.get("status") == "running") and callable(inflight_reader):
                inflight = inflight_reader()
                if not inflight.get("running") or inflight.get("operation_id") != operation_id:
                    result = {**result, "status": "cancelled", "success": False, "pending": False}
            if result and not result.get("pending") and result.get("status") != "running":
                self._notice_complete_site(nonce, result, generation)

    def _notice_resume(self):
        try:
            if (getattr(self, "_fusion_notify_enabled", False) or self._should_cancel()
                    or not isinstance(self.get_data(STATE_KEY), dict)):
                return
            with self._notice_lock:
                state = self._notice_load()
                interrupted = []
                for record in state["records"].values():
                    if record.get("status") == "running":
                        record.update(status="failed" if record.get("kind") == "site_stat" and not record.get("operation_id") else "uncertain",
                                      text="宿主已重新加载，之前操作结果待核实，请检查实际状态。")
                        interrupted.append(record["nonce"])
                        if not record.get("operation_id"):
                            record["site_waiting"] = False
                    if record.get("site_waiting") and record.get("operation_id"):
                        record["refresh_generation"] = getattr(self, "_runtime_generation", 0)
                self._notice_save(state)
            self._notice_reconcile_plugins()
            self._notice_recover_sites(getattr(self, "_runtime_generation", 0))
            for nonce, record in self._notice_load()["records"].items():
                if record.get("initial_pending") and not record.get("message_id") and self._notice_allowed(record["kind"]):
                    notice_transport.enqueue_notice(self, nonce)
            for nonce in interrupted:
                latest = self._notice_load()["records"].get(nonce) or {}
                if latest.get("status") in {"uncertain", "failed"}:
                    self._notice_publish(nonce)
            self._notice_retry_delivery(getattr(self, "_runtime_generation", 0), restart=True)
            self._notice_schedule_wakeup()
        except Exception:
            logger.warning("Signal 通知操作恢复失败")
