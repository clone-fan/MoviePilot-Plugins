"""Signal lifecycle: init, stop, reload, scheduler cleanup, uninstall orchestration.

V3 migration note:
- remove_plugin_job() in V3 returns None (not bool). Success is silent; failure
  throws. The old `if removed is False:` check was dead code — removed.
"""
import re
import sys
import threading
import time
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime
from types import ModuleType
from typing import Any, Dict, List, Mapping, Optional
from uuid import uuid4

from app.sdk.logging import logger

from ..application.backup_models import BackupSettings
from ..domain import site_helpers

# Default local plugin source repository. Empty means disabled.
# Source cleanup is only enabled after an explicit user path is configured.
DEFAULT_LOCAL_PLUGIN_REPO = ""


def _site_refresh_process_runtime():
    # MoviePilot evicts the plugin module tree on reload while native host
    # requests can still be running. Keep coordination data outside that tree.
    # This module retains no plugin classes or callbacks, only the current
    # operation, its lock, caller-local results, and the short result cache.
    name = "_signal_site_refresh_runtime_v1"
    runtime = ModuleType(name)
    runtime._site_refresh_condition = threading.Condition(threading.RLock())
    runtime._site_refresh_running = False
    runtime._site_refresh_started_at = 0.0
    runtime._site_refresh_running_key = None
    runtime._site_refresh_running_started_at = ""
    runtime._site_refresh_partial_result = None
    runtime._site_refresh_run_context = None
    runtime._site_refresh_completion_local = threading.local()
    runtime._site_refresh_last_result = None
    runtime._site_refresh_last_finished_at = 0.0
    runtime._site_refresh_last_key = None
    return sys.modules.setdefault(name, runtime)


SITE_REFRESH_RUNTIME = _site_refresh_process_runtime()


class LifecycleMixin:
    _local_plugin_repo = DEFAULT_LOCAL_PLUGIN_REPO
    _site_refresh_state_key = "site_stat_refresh_state_v1"
    _site_refresh_condition = SITE_REFRESH_RUNTIME._site_refresh_condition
    _site_refresh_cache_ttl_seconds = 5.0
    _fusion_site_refresh_timeout_seconds = 30.0
    _notice_site_refresh_timeout_seconds = 1.0
    _site_refresh_completion_timeout_seconds = 600.0
    SITE_REFRESH_SOURCES = {"site_stat_manual", "site_stat_scheduled", "fusion_create_manual", "fusion_create_scheduled", "fusion_refresh", "notice_site"}

    @staticmethod
    def _clear_site_refresh_cache():
        cls = SITE_REFRESH_RUNTIME
        with cls._site_refresh_condition:
            cls._site_refresh_last_result = None
            cls._site_refresh_last_finished_at = 0.0
            cls._site_refresh_last_key = None

    def _save_site_refresh_state(self, result: Mapping[str, Any]) -> None:
        """Checkpoint the actual collection independently of a caller's wait."""
        saver = getattr(self, "save_data", None)
        if not callable(saver):
            return
        status = str(result.get("status") or "error")
        if status not in {"running", "ok", "partial", "empty", "active_sites_error", "timeout", "error"}:
            status = "error"
        sites = []
        for item in result.get("sites") or []:
            if not isinstance(item, dict):
                continue
            item_status = item.get("status") if item.get("status") in {"ok", "fault", "checker_error"} else "checker_error"
            code, reason = "ok", ""
            if item_status == "fault":
                code = item.get("reason_code")
                if code not in {"fetch_login", "fetch_timeout", "fetch_connect", "fetch_empty", "fetch_error"}:
                    code, _ = self._site_error_details(item.get("reason"))
                reason = self.SITE_STAT_REASONS[code].removeprefix("采集失败：")
            elif item_status == "checker_error":
                code, reason = "checker_error", "站点身份匹配失败"
            sites.append({"name": self._site_safe_name(item.get("name")),
                          "domain": site_helpers.normalize_site_domain(item.get("domain")),
                          "status": item_status, "reason_code": code, "reason": reason,
                          "attempted_at": self._site_timestamp(item.get("attempted_at")),
                          "finished_at": self._site_timestamp(item.get("finished_at"))})
        payload = {
            "success": bool(result.get("success")), "status": status,
            "pending": status == "running",
            "operation_id": str(result.get("operation_id") or "")[:64],
            "message": {"active_sites_error": "读取启用站点失败", "timeout": "等待站点刷新超时", "error": "站点刷新检查失败"}.get(status, ""),
            "active_count": int(result.get("active_count") or 0),
            "active_scope_known": result.get("active_scope_known") is True,
            "active_domains": sorted({site_helpers.normalize_site_domain(item) for item in result.get("active_domains") or [] if item}),
            "count": int(result.get("count") or 0), "ok_count": int(result.get("ok_count") or 0),
            "source": result.get("source") if result.get("source") in self.SITE_REFRESH_SOURCES else "unknown",
            "started_at": self._site_timestamp(result.get("started_at")),
            "finished_at": self._site_timestamp(result.get("finished_at")),
            "data_date": self._site_timestamp(str(result.get("data_date") or "") + " 00:00:00")[:10],
            "sites": sites,
            "errors": [f"{item['name']}：{item['reason']}" for item in sites if item["status"] != "ok"],
        }
        # Coordinator callers hold the condition through checkpoint persistence.
        context = SITE_REFRESH_RUNTIME._site_refresh_run_context
        if context and context.get("operation_id") == payload["operation_id"]:
            context["result"] = deepcopy(payload)
        try:
            saver(self._site_refresh_state_key, payload)
        except Exception:
            logger.warning("Signal 站点刷新状态保存失败")

    def _load_site_refresh_state(self) -> Dict[str, Any]:
        loader = getattr(self, "get_data", None)
        if not callable(loader):
            return {}
        try:
            raw = loader(self._site_refresh_state_key)
        except Exception:
            logger.warning("Signal 站点刷新状态读取失败")
            return {}
        return dict(raw) if isinstance(raw, dict) else {}

    @contextmanager
    def _site_refresh_completion_scope(self):
        """Retain this caller's operations until its card registration finishes."""
        local = SITE_REFRESH_RUNTIME._site_refresh_completion_local
        previous = getattr(local, "contexts", None)
        local.contexts = {}
        try:
            yield
        finally:
            if previous is None:
                del local.contexts
            else:
                local.contexts = previous

    def _retain_site_refresh_completion(self, result: Dict[str, Any]) -> Dict[str, Any]:
        # Called under the coordinator lock before returning a waiting result.
        # The caller and worker hold the same context; no global result archive
        # or retention timeout is needed, and later collections cannot erase it.
        contexts = getattr(SITE_REFRESH_RUNTIME._site_refresh_completion_local, "contexts", None)
        context = SITE_REFRESH_RUNTIME._site_refresh_run_context
        if contexts is not None and context and result.get("operation_id") == context.get("operation_id"):
            contexts[result["operation_id"]] = context
        return result

    def _site_refresh_result_for_operation(self, operation_id: str) -> Dict[str, Any]:
        if not operation_id:
            return {}
        with SITE_REFRESH_RUNTIME._site_refresh_condition:
            contexts = getattr(SITE_REFRESH_RUNTIME._site_refresh_completion_local, "contexts", {})
            context = contexts.get(operation_id)
            if context is not None:
                return deepcopy(context.get("result") or {})
            latest = self._load_site_refresh_state()
            return latest if latest.get("operation_id") == operation_id else {}

    @staticmethod
    def _site_refresh_inflight_snapshot() -> Dict[str, Any]:
        cls = SITE_REFRESH_RUNTIME
        with cls._site_refresh_condition:
            key = cls._site_refresh_running_key
            running = bool(cls._site_refresh_running and key and cls._site_refresh_running_started_at)
            return {"running": running, "scope": sorted(key[2]) if running else [],
                    "operation_id": str((cls._site_refresh_run_context or {}).get("operation_id") or ""),
                    "date": key[0] if running else "", "started_at": cls._site_refresh_running_started_at if running else "",
                    "elapsed_seconds": max(0.0, time.monotonic() - cls._site_refresh_started_at) if running else 0.0}

    def _refresh_site_userdata_coordinated(self, *, source: str = "site_stat_manual", generation: Optional[int] = None) -> Dict[str, Any]:
        source = source if source in self.SITE_REFRESH_SOURCES else "unknown"
        wait_seconds = (self._notice_site_refresh_timeout_seconds if source == "notice_site" else
                        self._fusion_site_refresh_timeout_seconds if source.startswith("fusion_") else 60.0)
        started_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data_date = started_at[:10]
        active_sites = []
        active_domains = set()
        cls = SITE_REFRESH_RUNTIME
        runtime_generation = getattr(self, "_runtime_generation", 0) if generation is None else generation
        operation_id = ""
        deadline_timer = None

        def cancelled():
            return self._should_cancel(runtime_generation)

        def finish(result: Dict[str, Any]) -> Dict[str, Any]:
            result.setdefault("active_count", len(active_sites))
            result.setdefault("active_domains", sorted(active_domains))
            result.setdefault("active_scope_known", True)
            result.setdefault("count", 0)
            result.setdefault("ok_count", 0)
            result.setdefault("sites", [])
            result.setdefault("errors", [])
            result.update(started_at=started_at, finished_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                          data_date=data_date, source=source, operation_id=operation_id)
            return result

        def stopped_result():
            return finish({"success": False, "status": "cancelled", "message": "站点刷新已停止"})

        def wait_result(*, expired=False):
            # A response deadline does not stop MoviePilot's serial collection.
            # Only the independent collection deadline is a terminal timeout.
            key = (data_date, len(active_sites), frozenset(active_domains))
            same_scope = cls._site_refresh_running_key == key
            partial = cls._site_refresh_partial_result if same_scope else None
            partial = deepcopy(partial) if partial else {}
            sites = partial.get("sites") or []
            elapsed = max(0.0, time.monotonic() - cls._site_refresh_started_at)
            pending = same_scope and not expired and elapsed < self._site_refresh_completion_timeout_seconds
            result = finish({"success": pending, "status": "running" if pending else "timeout",
                             "pending": pending, "message": "站点正在后台更新" if pending else "等待站点刷新超时",
                             "sites": sites, "count": len(partial.get("returned_domains") or []),
                             "ok_count": sum(item["status"] == "ok" for item in sites)})
            if same_scope:
                result.update({key: value for key, value in (cls._site_refresh_run_context or {}).items()
                               if key in {"operation_id", "started_at", "data_date", "source"}})
            if pending:
                result["finished_at"] = ""
            return result

        def complete_card(result):
            callback = getattr(self, "_settle_fusion_site_refresh", None)
            if callable(callback) and not cancelled():
                try:
                    callback(result, generation=runtime_generation)
                except Exception:
                    logger.warning("Signal 站点采集结果回填原卡失败")
            notice_callback = getattr(self, "_notice_settle_site_refresh", None)
            if callable(notice_callback) and not cancelled():
                try:
                    notice_callback(result, generation=runtime_generation)
                except Exception:
                    logger.warning("Signal 站点采集结果回填普通通知失败")

        def deadline_expired():
            with cls._site_refresh_condition:
                if cancelled() or (cls._site_refresh_run_context or {}).get("operation_id") != operation_id:
                    return
                result = wait_result(expired=True)
                self._save_site_refresh_state(result)
            complete_card(result)

        if cancelled():
            return stopped_result()
        try:
            from app.db.oper.site import SiteOper
            active_sites = site_helpers.select_user_data_sites(SiteOper().list_active() or [])
            active_domains = {site_helpers.normalize_site_domain(getattr(site, "domain", "")) for site in active_sites}
            active_domains.discard("")
        except Exception:
            with cls._site_refresh_condition:
                if cancelled():
                    return stopped_result()
                result = finish({"success": False, "status": "active_sites_error", "active_scope_known": False,
                                 "message": "读取启用站点失败"})
                self._save_site_refresh_state(result)
                return result
        if len(active_domains) != len(active_sites):
            with cls._site_refresh_condition:
                if cancelled():
                    return stopped_result()
                result = finish({"success": False, "status": "active_sites_error", "active_identity_invalid": True,
                                 "message": "启用站点身份匹配失败"})
                self._save_site_refresh_state(result)
                return result

        with cls._site_refresh_condition:
            if cancelled():
                return stopped_result()

            def cached_result():
                key = (datetime.now().strftime("%Y-%m-%d"), len(active_sites), frozenset(active_domains))
                age = time.monotonic() - cls._site_refresh_last_finished_at
                if (cls._site_refresh_last_result is not None and cls._site_refresh_last_key == key
                        and cls._site_refresh_last_result.get("data_date") == key[0]
                        and 0 <= age <= self._site_refresh_cache_ttl_seconds):
                    return deepcopy(cls._site_refresh_last_result)
                return None

            cached = cached_result()
            if cached is not None:
                return cached
            if cls._site_refresh_running:
                completed = cls._site_refresh_condition.wait_for(
                    lambda: cancelled() or not cls._site_refresh_running, timeout=wait_seconds)
                if cancelled():
                    return stopped_result()
                if not completed:
                    data_date = datetime.now().strftime("%Y-%m-%d")
                    result = wait_result()
                    self._save_site_refresh_state(result)
                    return self._retain_site_refresh_completion(result)
                cached = cached_result()
                if cached is not None:
                    return cached
            started_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data_date = started_at[:10]
            cache_key = (data_date, len(active_sites), frozenset(active_domains))
            operation_id = uuid4().hex
            cls._site_refresh_started_at = time.monotonic()
            cls._site_refresh_running_key = cache_key
            cls._site_refresh_running_started_at = started_at
            cls._site_refresh_partial_result = None
            cls._site_refresh_running = True
            cls._site_refresh_run_context = {"operation_id": operation_id, "started_at": started_at,
                                             "data_date": data_date, "source": source}
            self._save_site_refresh_state(wait_result())

        results = []

        def collect():
            try:
                from app.chain.site import SiteChain
                from app.sdk.network import SitesHelper
                from app.sdk.utilities import StringUtils

                host_normalizer = getattr(StringUtils, "get_url_domain", site_helpers.normalize_site_domain)
                def host_domain(value):
                    return str(host_normalizer(str(value or "")) or "").strip().lower()

                exact_lookup: Dict[str, List[Dict[str, Any]]] = {}
                host_lookup: Dict[str, List[Dict[str, Any]]] = {}
                for indexer in (SitesHelper().get_indexers() or []) if active_sites else []:
                    if not isinstance(indexer, dict):
                        continue
                    raw_domain = indexer.get("domain") or indexer.get("url")
                    domain = site_helpers.normalize_site_domain(raw_domain)
                    if domain:
                        exact_lookup.setdefault(domain, []).append(indexer)
                        host_lookup.setdefault(host_domain(raw_domain), []).append(indexer)
                active_host_domains = [host_domain(getattr(site, "domain", "")) for site in active_sites]
                returned_domains = set()
                sites = []
                chain = SiteChain() if active_sites else None
                for site in active_sites:
                    if cancelled():
                        break
                    raw_domain = getattr(site, "domain", "")
                    domain = site_helpers.normalize_site_domain(raw_domain)
                    label = self._site_safe_name(getattr(site, "name", None) or domain or "未知站点")
                    candidates = exact_lookup.get(domain)
                    if candidates is None:
                        key = host_domain(raw_domain)
                        candidates = host_lookup.get(key, []) if active_host_domains.count(key) == 1 else []
                    item = {"name": label, "domain": domain, "status": "ok", "reason_code": "ok", "reason": "",
                            "attempted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                    if len(candidates) != 1:
                        item.update(status="checker_error", reason_code="checker_error", reason="站点身份匹配失败")
                    else:
                        error = ""
                        try:
                            userdata = chain.refresh_userdata(site=candidates[0])
                            if userdata is None:
                                error = "未返回用户数据"
                            else:
                                returned_domains.add(domain)
                                error = str(getattr(userdata, "err_msg", "") or "").strip()
                        except Exception as err:
                            error = str(err)
                        if error:
                            code, reason = self._site_error_details(error)
                            item.update(status="fault", reason_code=code, reason=reason)
                    item["finished_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    sites.append(item)
                    with cls._site_refresh_condition:
                        if not cancelled():
                            cls._site_refresh_partial_result = {
                                "sites": deepcopy(sites), "returned_domains": sorted(returned_domains)}
                            self._save_site_refresh_state(wait_result())
                ok_count = sum(item["status"] == "ok" for item in sites)
                result = {"success": True, "status": "ok" if ok_count == len(active_sites) else ("partial" if ok_count else "empty"),
                          "count": len(returned_domains), "ok_count": ok_count, "sites": sites,
                          "returned_domains": sorted(returned_domains),
                          "faults": [item for item in sites if item["status"] == "fault"],
                          "checker_errors": [item for item in sites if item["status"] == "checker_error"],
                          "errors": [f"{item['name']}：{item['reason']}" for item in sites if item["status"] != "ok"],
                          "identity_missing": bool(active_domains - returned_domains), "identity_mismatch": active_domains != returned_domains,
                          "active_identity_invalid": False, "message": ""}
            except Exception:
                result = {"success": False, "status": "error", "message": "站点刷新检查失败"}
            finally:
                if deadline_timer is not None:
                    deadline_timer.cancel()
                    self._untrack_runtime_timer(deadline_timer)
                result = finish(result)
                with cls._site_refresh_condition:
                    if cancelled():
                        result = stopped_result()
                    else:
                        self._save_site_refresh_state(result)
                        cls._site_refresh_last_result = deepcopy(result)
                        cls._site_refresh_last_finished_at = time.monotonic()
                        cls._site_refresh_last_key = cache_key
                    results.append(result)
                    cls._site_refresh_started_at = 0.0
                    cls._site_refresh_running_key = None
                    cls._site_refresh_running_started_at = ""
                    cls._site_refresh_partial_result = None
                    cls._site_refresh_run_context = None
                    cls._site_refresh_running = False
                    cls._site_refresh_condition.notify_all()
                complete_card(result)
            return result

        deadline_timer = self._track_runtime_timer(threading.Timer(
            self._site_refresh_completion_timeout_seconds, deadline_expired))
        deadline_timer.daemon = True
        deadline_timer.start()
        if not (source.startswith("fusion_") or source == "notice_site"):
            return collect()

        # A slow host parser keeps the one shared collection running, but must not
        # leave an interactive notification in its loading state indefinitely.
        worker = threading.Thread(target=collect, name="Signal-site-refresh", daemon=True)
        try:
            worker.start()
        except Exception:
            deadline_timer.cancel()
            self._untrack_runtime_timer(deadline_timer)
            with cls._site_refresh_condition:
                cls._site_refresh_running = False
                cls._site_refresh_started_at = 0.0
                cls._site_refresh_running_key = None
                cls._site_refresh_running_started_at = ""
                cls._site_refresh_run_context = None
                cls._site_refresh_condition.notify_all()
                if cancelled():
                    return stopped_result()
                result = finish({"success": False, "status": "error", "message": "站点刷新检查失败"})
                self._save_site_refresh_state(result)
            return result
        with cls._site_refresh_condition:
            if not results:
                cls._site_refresh_condition.wait_for(lambda: bool(results) or cancelled(), timeout=wait_seconds)
            if cancelled():
                return stopped_result()
            if results:
                return deepcopy(results[0])
            # Persist under the same lock as completion so a late result wins.
            result = wait_result()
            self._save_site_refresh_state(result)
            return self._retain_site_refresh_completion(result)

    def _schedule_site_refresh_recovery(self) -> None:
        """Resume one interrupted current-day collection after host startup."""
        if (getattr(self, "_site_refresh_recovery_scheduled", False) or self._should_cancel()
                or not getattr(self, "_site_stat_enabled", False)):
            return
        previous = self._load_site_refresh_state()
        if previous.get("source") == "notice_site":
            # A user's notification refresh is recovered by its own read-only
            # result path. It must not turn into a scheduled broadcast.
            return
        if (previous.get("status") not in {"running", "timeout"}
                or previous.get("data_date") != datetime.now().strftime("%Y-%m-%d")
                or previous.get("active_scope_known") is not True):
            return
        self._site_refresh_recovery_scheduled = True
        generation = getattr(self, "_runtime_generation", 0)

        def still_interrupted():
            if self._should_cancel(generation) or not getattr(self, "_site_stat_enabled", False):
                return False
            latest = self._load_site_refresh_state()
            return (latest.get("status") in {"running", "timeout"}
                    and latest.get("data_date") == self._today_prefix()
                    and latest.get("active_scope_known") is True
                    and latest.get("operation_id") == previous.get("operation_id")
                    and latest.get("started_at") == previous.get("started_at"))

        def recover():
            self._untrack_runtime_timer(timer)
            cls = SITE_REFRESH_RUNTIME
            with cls._site_refresh_condition:
                if not still_interrupted():
                    return
                # Reload can leave an old host call alive. Wait for its exit
                # instead of joining an operation whose generation is cancelled.
                cls._site_refresh_condition.wait_for(
                    lambda: self._should_cancel(generation) or not cls._site_refresh_running
                    or (cls._site_refresh_run_context or {}).get("operation_id") != previous.get("operation_id"))
                if not still_interrupted():
                    return
            if getattr(self, "_fusion_notify_enabled", False):
                self.run_fusion_card_refresh()
            else:
                self.api_run_site_stat(trigger="scheduled")

        timer = self._track_runtime_timer(threading.Timer(5.0, recover))
        timer.daemon = True
        timer.start()


    def _load_plugin_config(self, config: Dict[str, Any]):
        self._load_report_config(config)
        self._load_health_site_config(config)
        self._load_maintenance_config(config)
        self._load_download_media_config(config)

    def _reset_runtime_state(self):
        with SITE_REFRESH_RUNTIME._site_refresh_condition:
            self._runtime_generation = int(getattr(self, "_runtime_generation", 0) or 0) + 1
            self._runtime_cancel_event = threading.Event()
            self._runtime_active = bool(getattr(self, "_enabled", False))
        self._runtime_timers = set()
        self._site_refresh_recovery_scheduled = False
        self._msg_seen = {}
        self._backup_selection_cache = {}
        self._backup_operation_current = None
        self._backup_operation_recent = []
        try:
            loader = getattr(self, "get_data", None)
            persisted = loader("backup_operation_recent") if callable(loader) else None
            if isinstance(persisted, Mapping):
                self._backup_operation_recent = [dict(persisted)]
            elif isinstance(persisted, list):
                self._backup_operation_recent = [dict(item) for item in persisted[-10:] if isinstance(item, Mapping)]
        except Exception:
            self._backup_operation_recent = []
        self._last_summary = self._build_summary()
        # Plugin initialization must not perform destructive filesystem work.
        # Uninstall isolation is handled only by the explicitly confirmed
        # uninstall workflow, never as an implicit startup side effect.
        resume_notices = getattr(self, "_notice_resume", None)
        if callable(resume_notices):
            resume_notices()

    def _stop_runtime_state(self) -> bool:
        cls = SITE_REFRESH_RUNTIME
        with cls._site_refresh_condition:
            self._runtime_active = False
            cls._site_refresh_partial_result = None
            self._runtime_generation = int(getattr(self, "_runtime_generation", 0) or 0) + 1
            cancel_event = getattr(self, "_runtime_cancel_event", None)
            if cancel_event is None:
                cancel_event = threading.Event()
                self._runtime_cancel_event = cancel_event
            cancel_event.set()
            self._clear_site_refresh_cache()
            cls._site_refresh_condition.notify_all()
        errors = []
        for timer in list(getattr(self, "_runtime_timers", set()) or set()):
            try:
                timer.cancel()
            except Exception as err:
                errors.append(f"{type(timer).__name__}: {err}")
        self._runtime_timers = set()
        if errors:
            logger.error(f"Signal 运行时停止未完成：定时器取消失败：{'；'.join(errors[:3])}")
            return False
        return True

    @classmethod
    def _scheduler_nested_value_matches_plugin(cls, value: Any, plugin_id: str) -> bool:
        if isinstance(value, dict):
            return any(
                cls._scheduler_nested_value_matches_plugin(key, plugin_id)
                or cls._scheduler_nested_value_matches_plugin(item, plugin_id)
                for key, item in value.items()
            )
        if isinstance(value, (list, tuple, set)):
            return any(cls._scheduler_nested_value_matches_plugin(item, plugin_id) for item in value)
        return cls._scheduler_value_matches_plugin(value, plugin_id)

    @staticmethod
    def _scheduler_value_matches_plugin(value: Any, plugin_id: str) -> bool:
        target = str(plugin_id or "").strip().lower()
        text = str(value or "").strip().lower()
        if not target or not text:
            return False
        return text == target or any(
            text.startswith(f"{target}{separator}")
            for separator in (".", ":", "-", "_", "|")
        )

    @classmethod
    def _scheduler_record_matches_plugin(cls, record: Any, plugin_id: str) -> bool:
        if isinstance(record, dict):
            values = [
                record.get(key)
                for key in ("pid", "plugin_id", "plugin", "id", "job_id", "provider", "provider_name", "kwargs")
            ]
        else:
            values = [
                getattr(record, key, "")
                for key in ("pid", "plugin_id", "plugin", "id", "job_id", "provider", "provider_name", "kwargs")
            ]
        return any(cls._scheduler_nested_value_matches_plugin(value, plugin_id) for value in values)

    @classmethod
    def _verify_scheduler_jobs_removed(cls, scheduler: Any, plugin_id: str) -> Dict[str, Any]:
        """Verify both MoviePilot's registry and APScheduler contain no plugin jobs."""
        residues = []
        errors = []
        inspected = 0

        def inspect_jobs(source: str, jobs: Any):
            nonlocal inspected
            inspected += 1
            if isinstance(jobs, dict):
                records = list(jobs.items())
            else:
                records = [(None, item) for item in list(jobs or [])]
            for key, record in records:
                if (
                    (key is not None and cls._scheduler_value_matches_plugin(key, plugin_id))
                    or cls._scheduler_record_matches_plugin(record, plugin_id)
                ):
                    identity = key if key is not None else getattr(record, "id", "") or getattr(record, "name", "")
                    residues.append(f"{source}:{identity or type(record).__name__}")

        if hasattr(scheduler, "_jobs"):
            try:
                inspect_jobs("registry", getattr(scheduler, "_jobs", None) or {})
            except Exception as err:
                errors.append(f"读取 MoviePilot 调度注册表失败：{err}")

        if hasattr(scheduler, "_scheduler"):
            backend = getattr(scheduler, "_scheduler", None)
            if backend is None:
                inspected += 1
            else:
                get_backend_jobs = getattr(backend, "get_jobs", None)
                if callable(get_backend_jobs):
                    try:
                        inspect_jobs("apscheduler", get_backend_jobs() or [])
                    except Exception as err:
                        errors.append(f"读取 APScheduler 任务失败：{err}")
                else:
                    errors.append("APScheduler 不支持任务复核")

        if not hasattr(scheduler, "_jobs") and not hasattr(scheduler, "_scheduler"):
            list_jobs = getattr(scheduler, "list", None) or getattr(scheduler, "get_jobs", None)
            if callable(list_jobs):
                try:
                    inspect_jobs("public", list_jobs() or [])
                except Exception as err:
                    errors.append(f"读取 MoviePilot 调度任务失败：{err}")

        return {
            "verified": inspected > 0 and not errors,
            "residues": sorted(set(residues)),
            "errors": errors,
        }

    def _cleanup_scheduler_jobs(self) -> bool:
        try:
            from app.scheduler import Scheduler
            scheduler = Scheduler()
        except Exception as err:
            logger.error(f"Signal 调度注销未完成：无法加载 MoviePilot 调度器：{err}")
            return False

        remove_plugin_job = getattr(scheduler, "remove_plugin_job", None)
        if not callable(remove_plugin_job):
            logger.error("Signal 调度注销未完成：MoviePilot 调度器缺少 remove_plugin_job")
            return False
        try:
            # V3 的 remove_plugin_job 返回 None，不携带成功信号；
            # 真正的失败通过异常暴露，由上面的 except 处理。
            remove_plugin_job("Signal")
        except Exception as err:
            logger.error(f"Signal 调度注销未完成：remove_plugin_job 执行失败：{err}")
            return False

        verification = self._verify_scheduler_jobs_removed(scheduler, "Signal")
        if verification["errors"]:
            logger.error(f"Signal 调度注销未完成：{'；'.join(verification['errors'][:3])}")
            return False
        if not verification["verified"]:
            logger.error("Signal 调度注销未完成：MoviePilot 未提供可验证的任务注册表")
            return False
        if verification["residues"]:
            logger.error(f"Signal 调度注销未完成：复核仍有残留：{'；'.join(verification['residues'][:5])}")
            return False
        return True

    def _is_runtime_active(self, generation: Optional[int] = None) -> bool:
        if not bool(getattr(self, "_enabled", False)):
            return False
        if not bool(getattr(self, "_runtime_active", False)):
            return False
        if generation is not None and int(generation) != int(getattr(self, "_runtime_generation", 0) or 0):
            return False
        cancel_event = getattr(self, "_runtime_cancel_event", None)
        return not bool(cancel_event and cancel_event.is_set())

    def _should_cancel(self, generation: Optional[int] = None) -> bool:
        return not self._is_runtime_active(generation)

    def _event_should_noop_after_stop(self) -> bool:
        return bool(getattr(self, "_enabled", False)) and not self._is_runtime_active()

    def _runtime_gate(
        self,
        operation: str,
        component: Optional[str] = None,
        name: str = "",
        allow_disabled_readonly: bool = False,
    ):
        display_name = name or operation
        if allow_disabled_readonly and operation == "read":
            return True, ""
        if not bool(getattr(self, "_enabled", False)):
            return False, f"插件未启用，已跳过{display_name}。"
        if not self._is_runtime_active():
            return False, f"Plugin stopped, skipped {display_name}."
        if component and not self._component_enabled(component):
            return False, f"{display_name}未启用，已跳过。"
        return True, ""

    def _track_runtime_timer(self, timer):
        timers = getattr(self, "_runtime_timers", None)
        if timers is None:
            timers = set()
            self._runtime_timers = timers
        timers.add(timer)
        return timer

    def _untrack_runtime_timer(self, timer):
        timers = getattr(self, "_runtime_timers", None)
        if timers is not None:
            timers.discard(timer)

    @staticmethod
    def _valid_cron_part(value: str, minimum: int, maximum: int) -> bool:
        for segment in str(value or "").split(","):
            if not segment:
                return False
            pieces = segment.split("/")
            if len(pieces) > 2:
                return False
            base = pieces[0]
            if len(pieces) == 2 and (not pieces[1].isdigit() or not 1 <= int(pieces[1]) <= (maximum - minimum + 1)):
                return False
            if base == "*":
                continue
            if base.isdigit():
                if not minimum <= int(base) <= maximum:
                    return False
                continue
            matched = re.fullmatch(r"(\d+)-(\d+)", base)
            if not matched:
                return False
            start, end = map(int, matched.groups())
            if start < minimum or end > maximum or start > end:
                return False
        return True

    @classmethod
    def _normalize_fusion_refresh_cron(cls, value: Any, fallback: str = "0 * * * *") -> str:
        ranges = ((0, 59), (0, 23), (1, 31), (1, 12), (0, 7))
        for candidate in (value, fallback, "0 * * * *"):
            parts = str(candidate or "").strip().split()
            if len(parts) == 5 and all(cls._valid_cron_part(part, *ranges[index]) for index, part in enumerate(parts)):
                return " ".join(parts)
        return "0 * * * *"

    @classmethod
    def _normalize_optional_cron(cls, value: Any) -> str:
        ranges = ((0, 59), (0, 23), (1, 31), (1, 12), (0, 7))
        parts = str(value or "").strip().split()
        if len(parts) == 5 and all(cls._valid_cron_part(part, *ranges[index]) for index, part in enumerate(parts)):
            return " ".join(parts)
        return ""

    def _load_report_config(self, config: Dict[str, Any]):
        previous_fusion_enabled = getattr(self, "_fusion_notify_enabled", None)
        self._enabled = bool(config.get("enabled"))
        self._local_plugin_repo = config.get("local_plugin_repo") or DEFAULT_LOCAL_PLUGIN_REPO
        self._fusion_notify_enabled = bool(config.get("fusion_notify_enabled")) if "fusion_notify_enabled" in config else True
        self._fusion_card_create_cron = self._normalize_fusion_refresh_cron(config.get("fusion_card_create_cron"), "5 0 * * *")
        self._fusion_card_refresh_cron = self._normalize_fusion_refresh_cron(config.get("fusion_card_refresh_cron"), "0 * * * *")
        self._fusion_report_greeting = "少爷"
        self._fusion_notify_schedule_enabled = self._fusion_notify_enabled
        self._fusion_notify_cron = self._fusion_card_refresh_cron
        self._fusion_notify_msgtype = config.get("fusion_notify_msgtype") or "Plugin"
        self._fusion_notify_columns = [x["key"] for x in self._fusion_column_registry()]
        self._report_storage_targets = ["config", "download", "library", "storages"]
        self._tg_console_enabled = self._fusion_notify_enabled
        self._tg_console_poll_enabled = False
        self._tg_console_poll_interval = 0
        self._tg_console_allowed_user_ids = []
        self._tg_console_full_remote_enabled = False
        self._tg_console_suppress_individual_notifications = bool(self._fusion_notify_enabled)
        self._tg_console_max_notices = 20
        self._tg_console_last_error = ""
        self._sync_fusion_card_enablement(previous_fusion_enabled)
        self._health_in_report = True
        self._subscribe_reminder_enabled = bool(config.get("subscribe_reminder_enabled", True))
        self._site_stat_enabled = bool(config.get("site_stat_enabled", True))
        self._subscribe_in_report = self._subscribe_reminder_enabled
        self._site_stat_in_report = self._site_stat_enabled
        self._report_version = True
        self._report_site_status = True
        self._report_site_increment = self._site_stat_in_report
        self._report_today_download = True
        self._report_transfer = True
        self._report_subscribe = self._subscribe_in_report
        self._report_storage = True
        self._report_media_stat = True
        self._report_summary = self._health_in_report

    def _load_health_site_config(self, config: Dict[str, Any]):
        self._health_check_enabled = bool(config.get("health_check_enabled", True))
        self._health_check_schedule_enabled = self._schedule_flag(config, "health_check_schedule_enabled", self._health_check_enabled)
        self._health_check_cron = config.get("health_check_cron") or "0 */6 * * *"
        self._health_check_items = self._parse_csv(config.get("health_check_items"))
        self._health_check_database_targets = self._parse_csv(config.get("health_check_database_targets"))
        self._health_check_storage_targets = self._parse_csv(config.get("health_check_storage_targets"))
        self._health_check_directory_targets = self._parse_csv(config.get("health_check_directory_targets"))
        self._health_check_storage_threshold = self._safe_int(config.get("health_check_storage_threshold"), 85, 1)
        if self._health_check_storage_threshold > 99:
            self._health_check_storage_threshold = 99
        self._health_check_notify = self._config_bool(config, "health_check_notify", True)
        self._health_check_completion_notify_enabled = self._config_bool(
            config, "health_check_completion_notify_enabled", False
        )
        self._health_check_notify_type = config.get("health_check_notify_type") or "Plugin"
        self._health_check_completion_notify_type = config.get("health_check_completion_notify_type") or "Plugin"
        self._report_health = True
        self._subscribe_reminder_cron = self._normalize_optional_cron(config.get("subscribe_reminder_cron")) or "0 9 * * *"
        self._subscribe_reminder_msgtype = config.get("subscribe_reminder_msgtype") or "Subscribe"
        self._subscribe_reminder_schedule_enabled = self._schedule_flag(config, "subscribe_reminder_schedule_enabled", self._subscribe_reminder_enabled)
        # Only the current-day increment mode is implemented.  Normalize old
        # or manually supplied aggregate values to the one truthful mode.
        self._site_stat_dashboard_type = "today"
        self._site_stat_schedule_enabled = self._schedule_flag(config, "site_stat_schedule_enabled", self._site_stat_enabled)
        self._site_stat_cron = self._normalize_optional_cron(config.get("site_stat_cron")) or "0 8 * * *"
        self._site_stat_schedule_notify_enabled = self._config_bool(
            config, "site_stat_schedule_notify_enabled", True
        )
        notify_type = str(config.get("site_stat_notify_type") or "Plugin").strip()
        self._site_stat_notify_type = "Plugin" if notify_type.lower() in {"inc", "all", "none", "off", ""} else notify_type

    def _load_maintenance_config(self, config: Dict[str, Any]):
        self._log_clean_enabled = bool(config.get("log_clean_enabled", False))
        self._log_clean_schedule_enabled = self._schedule_flag(config, "log_clean_schedule_enabled", self._log_clean_enabled)
        self._log_clean_cron = config.get("log_clean_cron") or "0 3 * * 1"
        self._log_clean_rows = self._safe_int(config.get("log_clean_rows"), 300, 0)
        self._log_clean_selected_ids = self._parse_csv(config.get("log_clean_selected_ids"))
        self._log_clean_notify = bool(config.get("log_clean_notify", True))
        self._log_clean_notify_type = config.get("log_clean_notify_type") or "Plugin"
        backup = BackupSettings.from_config(config)
        self._backup_config = backup.current_config()
        self._backup_legacy_config_keys = list(backup.migrated_legacy_keys)
        self._backup_enabled = backup.enabled
        self._backup_database_enabled = backup.database_enabled
        self._backup_cron = backup.cron
        self._backup_keep_count = backup.local_keep_count
        self._backup_path = backup.local_path
        self._backup_notify = backup.notify
        self._backup_notify_type = backup.notify_type
        self._backup_webdav_enabled = backup.webdav_enabled
        self._backup_webdav_digest_auth = backup.webdav.digest_auth
        self._backup_webdav_disable_check = backup.webdav.disable_check
        self._backup_webdav_hostname = backup.webdav.hostname
        self._backup_webdav_login = backup.webdav.login
        self._backup_webdav_password = backup.webdav.password
        self._backup_webdav_max_count = backup.webdav_keep_count
        self._mp_update_enabled = self._config_bool(config, "mp_update_enabled", False)
        # The task switch is now the only scheduler switch.  The old schedule
        # flags are retained in config solely so older installations can save
        # and reload without losing unknown compatibility keys.
        self._mp_update_schedule_enabled = self._mp_update_enabled
        self._mp_update_cron = config.get("mp_update_cron") or "0 9 * * *"
        self._mp_update_types = config.get("mp_update_types") or ["后端", "前端"]
        if isinstance(self._mp_update_types, str):
            self._mp_update_types = self._parse_csv(self._mp_update_types) or ["后端", "前端"]
        legacy_market_enabled = self._config_bool(config, "market_update_enabled", False)
        legacy_market_schedule_enabled = self._config_bool(
            config, "market_update_schedule_enabled", legacy_market_enabled
        )
        legacy_market_cron = self._normalize_optional_cron(config.get("market_update_cron")) or "0 9 * * *"
        has_current_plugin_update_config = any(
            key in config for key in (
                "plugin_update_reminder_enabled",
                "plugin_update_execution_mode",
                "plugin_auto_install_scope_mode",
            )
        )
        # The old schedule flag is only meaningful during the one-time legacy
        # migration. Once the new plugin-update fields exist, the visible
        # library switch is the scheduler authority and the hidden flag must
        # not override it on a later reload.
        legacy_market_effective = bool(legacy_market_enabled and legacy_market_schedule_enabled)
        self._market_update_enabled = bool(
            legacy_market_enabled if has_current_plugin_update_config else legacy_market_effective
        )
        self._market_update_schedule_enabled = self._market_update_enabled
        self._market_update_cron = legacy_market_cron
        self._market_update_strategy = str(config.get("market_update_strategy") or "check").strip().lower()
        if self._market_update_strategy not in {"check", "sync", "install"}:
            self._market_update_strategy = "check"
        self._market_update_install_ids = self._parse_csv(config.get("market_update_install_ids"))
        self._market_update_exclude_ids = self._parse_csv(config.get("market_update_exclude_ids"))
        self._market_update_blacklist = self._parse_csv(config.get("market_update_blacklist"))
        market_mode = str(config.get("market_update_execution_mode") or "manual").strip().lower()
        self._market_update_execution_mode = market_mode if market_mode in {"auto", "manual"} else "manual"
        mp_mode = str(config.get("mp_update_execution_mode") or "manual").strip().lower()
        self._mp_update_execution_mode = mp_mode if mp_mode in {"auto", "manual"} else "manual"
        reminder_enabled = self._config_bool(
            config,
            "plugin_update_reminder_enabled",
            legacy_market_enabled if has_current_plugin_update_config else legacy_market_effective,
        )
        self._plugin_update_reminder_enabled = bool(reminder_enabled)
        self._plugin_update_reminder_schedule_enabled = self._plugin_update_reminder_enabled
        self._plugin_update_reminder_cron = self._normalize_optional_cron(
            config.get("plugin_update_reminder_cron") or legacy_market_cron
        ) or "0 9 * * *"
        plugin_mode = str(config.get("plugin_update_execution_mode") or "").strip().lower()
        if plugin_mode not in {"auto", "manual"}:
            plugin_mode = "auto" if self._market_update_strategy == "install" else "manual"
        self._plugin_update_execution_mode = plugin_mode
        self._plugin_auto_install_enabled = plugin_mode == "auto"
        self._plugin_auto_install_schedule_enabled = self._plugin_auto_install_enabled
        self._plugin_auto_install_cron = self._normalize_optional_cron(
            config.get("plugin_auto_install_cron") or legacy_market_cron
        ) or "0 9 * * *"
        self._plugin_auto_install_install_ids = self._parse_csv(
            config.get("plugin_auto_install_install_ids")
            if "plugin_auto_install_install_ids" in config
            else config.get("market_update_install_ids")
        )
        self._plugin_auto_install_exclude_ids = self._parse_csv(
            config.get("plugin_auto_install_exclude_ids")
            if "plugin_auto_install_exclude_ids" in config
            else config.get("market_update_exclude_ids")
        )
        scope_mode = str(config.get("plugin_auto_install_scope_mode") or "").strip().lower()
        if scope_mode not in {"all", "include", "exclude"}:
            if self._plugin_auto_install_install_ids and self._plugin_auto_install_exclude_ids:
                excluded = set(self._plugin_auto_install_exclude_ids)
                self._plugin_auto_install_install_ids = [
                    plugin_id for plugin_id in self._plugin_auto_install_install_ids if plugin_id not in excluded
                ]
                self._plugin_auto_install_exclude_ids = []
                scope_mode = "include"
            elif self._plugin_auto_install_install_ids:
                scope_mode = "include"
            elif self._plugin_auto_install_exclude_ids:
                scope_mode = "exclude"
            else:
                scope_mode = "all"
        self._plugin_auto_install_scope_mode = scope_mode
        legacy_update_notify = self._config_bool(config, "update_scheduled_notify", False)
        legacy_update_notify_type = config.get("update_notify_type") or "Plugin"
        self._update_scheduled_notify = legacy_update_notify
        self._update_notify_type = legacy_update_notify_type
        self._mp_update_scheduled_notify = self._config_bool(config, "mp_update_scheduled_notify", legacy_update_notify)
        self._mp_update_notify_type = config.get("mp_update_notify_type") or legacy_update_notify_type
        self._market_update_scheduled_notify = self._config_bool(config, "market_update_scheduled_notify", legacy_update_notify)
        self._market_update_notify_type = config.get("market_update_notify_type") or legacy_update_notify_type
        self._plugin_update_reminder_scheduled_notify = self._config_bool(config, "plugin_update_reminder_scheduled_notify", legacy_update_notify)
        self._plugin_update_reminder_notify_type = config.get("plugin_update_reminder_notify_type") or legacy_update_notify_type
        self._plugin_auto_install_scheduled_notify = self._config_bool(config, "plugin_auto_install_scheduled_notify", legacy_update_notify)
        self._plugin_auto_install_notify_type = config.get("plugin_auto_install_notify_type") or legacy_update_notify_type
        self._plugin_uninstall_ids = config.get("plugin_uninstall_ids") or []
        if isinstance(self._plugin_uninstall_ids, str):
            self._plugin_uninstall_ids = self._parse_csv(self._plugin_uninstall_ids)
        self._plugin_uninstall_clear_config = bool(config.get("plugin_uninstall_clear_config", True))
        self._plugin_uninstall_clear_data = bool(config.get("plugin_uninstall_clear_data", True))
        self._plugin_uninstall_delete_source = bool(config.get("plugin_uninstall_delete_source", False))

    def _load_download_media_config(self, config: Dict[str, Any]):
        self._seedclean_enabled = bool(config.get("seedclean_enabled", False))
        self._seedclean_schedule_enabled = self._schedule_flag(config, "seedclean_schedule_enabled", self._seedclean_enabled)
        self._seedclean_cron = config.get("seedclean_cron") or "0 */12 * * *"
        self._seedclean_action = config.get("seedclean_action") or "pause"
        self._seedclean_downloaders = self._parse_csv(config.get("seedclean_downloaders"))
        self._seedclean_size = str(config.get("seedclean_size") or "").strip()
        self._seedclean_ratio = str(config.get("seedclean_ratio") or "").strip()
        self._seedclean_time = str(config.get("seedclean_time") or "").strip()
        self._seedclean_upspeed = str(config.get("seedclean_upspeed") or "").strip()
        self._seedclean_labels = str(config.get("seedclean_labels") or "").strip()
        self._seedclean_pathkeywords = str(config.get("seedclean_pathkeywords") or "").strip()
        self._seedclean_trackerkeywords = str(config.get("seedclean_trackerkeywords") or "").strip()
        self._seedclean_errorkeywords = str(config.get("seedclean_errorkeywords") or "").strip()
        self._seedclean_torrentstates = str(config.get("seedclean_torrentstates") or "").strip()
        self._seedclean_trtorrentstates = str(config.get("seedclean_trtorrentstates") or "").strip()
        self._seedclean_torrentcategorys = str(config.get("seedclean_torrentcategorys") or "").strip()
        self._seedclean_samedata = bool(config.get("seedclean_samedata", False))
        self._seedclean_mponly = bool(config.get("seedclean_mponly", False))
        self._seedclean_notify = bool(config.get("seedclean_notify", True))
        self._seedclean_notify_type = config.get("seedclean_notify_type") or "Plugin"
        self._subfill_enabled = bool(config.get("subfill_enabled", False))
        self._subfill_details = self._parse_csv(config.get("subfill_details"))
        self._subfill_category_enabled = bool(config.get("subfill_category_enabled", False))
        self._subfill_category_confs = config.get("subfill_category_confs") or ""
        self._subfill_completion_notify_enabled = self._config_bool(config, "subfill_completion_notify_enabled", False)
        self._subfill_completion_notify_type = config.get("subfill_completion_notify_type") or "Plugin"
        self._subfill_confs = self._parse_subfill_confs(self._subfill_category_confs)
        self._msgnotify_enabled = bool(config.get("msgnotify_enabled", False))
        self._msgnotify_types = self._parse_csv(config.get("msgnotify_types"))
        self._msgnotify_servers = self._parse_csv(config.get("msgnotify_servers"))
        self._msgnotify_notify_type = config.get("msgnotify_notify_type") or "MediaServer"
        self._dltag_enabled = bool(config.get("dltag_enabled", False))
        self._dltag_downloaders = self._parse_csv(config.get("dltag_downloaders"))
        self._dltag_tasks = self._parse_csv(config.get("dltag_tasks") or ["tagging", "seeding", "cleanup"])
        dltag_cron = config["dltag_cron"] if "dltag_cron" in config else "0 */6 * * *"
        self._dltag_cron = self._normalize_optional_cron(dltag_cron)
        self._dltag_listen_download = self._config_bool(config, "dltag_listen_download", True)
        # The old source_file value was tagging context, never deletion consent.
        self._dltag_listen_source_file = self._config_bool(config, "dltag_listen_source_file", False)
        self._dltag_prefix = str(config.get("dltag_prefix") or "").strip()
        self._dltag_all_tags = self._parse_csv(config.get("dltag_all_tags"))
        self._dltag_excluded_tags = self._parse_csv(config.get("dltag_excluded_tags"))
        self._dltag_not_select_all_tag = str(config.get("dltag_not_select_all_tag") or "非全").strip()
        self._dltag_tracker_mappings = str(config.get("dltag_tracker_mappings") or "").strip()
        strategy = str(config.get("dltag_source_delete_strategy") or "delayed").strip().lower()
        self._dltag_source_delete_strategy = strategy if strategy in {"early", "delayed"} else "delayed"
        self._dltag_scheduled_notify = self._config_bool(config, "dltag_scheduled_notify", False)
        self._dltag_notify_type = config.get("dltag_notify_type") or "Plugin"
