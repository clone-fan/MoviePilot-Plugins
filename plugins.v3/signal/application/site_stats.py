"""Site statistics and health check service mixin."""

import os
import re
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from app.sdk.logging import logger
from ..domain import site_helpers


class SiteStatsMixin:
    """Site statistics, health checks, storage inspection, and report data collection."""

    @staticmethod
    def _health_result(
        name: str,
        status: str,
        detail: str,
        *,
        affected_owner: str,
        target: str = "",
        alert_detail: str = "",
    ) -> Dict[str, Any]:
        status = status if status in {"ok", "fault", "unavailable", "checker_error"} else "checker_error"
        return {
            "name": name,
            "status": status,
            "ok": status in {"ok", "unavailable"},
            "complete": status == "ok",
            "alertable": status == "fault",
            "affected_owner": affected_owner,
            "target": target,
            "detail": str(detail or ""),
            "alert_detail": str(alert_detail or detail or "") if status == "fault" else "",
        }

    @classmethod
    def _normalize_health_result(cls, item: Any) -> Dict[str, Any]:
        source = dict(item or {}) if isinstance(item, dict) else {}
        status = str(source.get("status") or ("ok" if source.get("ok") else "checker_error"))
        normalized = cls._health_result(
            str(source.get("name") or "health_check"),
            status,
            str(source.get("detail") or source.get("error") or ""),
            affected_owner=str(source.get("affected_owner") or "signal-health-checker"),
            target=str(source.get("target") or source.get("path") or ""),
            alert_detail=str(source.get("alert_detail") or ""),
        )
        normalized.update({key: value for key, value in source.items() if key not in normalized})
        return normalized

    @classmethod
    def _aggregate_health_results(
        cls,
        name: str,
        outcomes: List[Dict[str, Any]],
        *,
        affected_owner: str,
        unavailable_detail: str,
    ) -> Dict[str, Any]:
        normalized = [cls._normalize_health_result(item) for item in outcomes]
        if not normalized:
            return cls._health_result(name, "unavailable", unavailable_detail, affected_owner=affected_owner)
        faults = [item for item in normalized if item["status"] == "fault"]
        checker_errors = [item for item in normalized if item["status"] == "checker_error"]
        oks = [item for item in normalized if item["status"] == "ok"]
        if faults:
            status = "fault"
            owner = faults[0].get("affected_owner") or affected_owner
        elif checker_errors:
            status = "checker_error"
            owner = "signal-health-checker"
        elif oks:
            status = "ok"
            owner = affected_owner
        else:
            status = "unavailable"
            owner = affected_owner
        detail = "；".join(str(item.get("detail") or "") for item in normalized if item.get("detail"))
        alert_detail = "；".join(str(item.get("alert_detail") or item.get("detail") or "") for item in faults)
        return cls._health_result(
            name,
            status,
            detail or unavailable_detail,
            affected_owner=owner,
            alert_detail=alert_detail,
        )


    SITE_STAT_STATE_LABELS = {
        "ok": "正常",
        "fault": "站点异常",
        "unavailable": "无今日数据",
        "checker_error": "Signal 检查异常",
    }

    @staticmethod
    def _site_stat_state(
        name: Any,
        domain: Any,
        status: str,
        reason: str = "",
        **extra: Any,
    ) -> Dict[str, Any]:
        """Normalize one site into the shared four-state vocabulary.

        ``fault`` is the only alertable state: it means the site itself failed
        (login, connection, site error, or missing user data).  ``unavailable``
        means the value cannot be computed today, and ``checker_error`` means
        Signal's own matching failed.  Neither cancels the whole run.
        """
        status = status if status in {"ok", "fault", "unavailable", "checker_error"} else "checker_error"
        normalized_domain = site_helpers.normalize_site_domain(domain)
        state: Dict[str, Any] = {
            "name": str(name or normalized_domain or "未知站点"),
            "domain": normalized_domain,
            "status": status,
            "reason": str(reason or ""),
            "alertable": status == "fault",
        }
        state.update({key: value for key, value in extra.items() if key not in state})
        return state

    @classmethod
    def _sorted_site_states(cls, states: Any) -> List[Dict[str, Any]]:
        normalized = [dict(item) for item in (states or []) if isinstance(item, dict)]
        return sorted(
            normalized,
            key=lambda item: (
                str(item.get("name") or ""),
                str(item.get("domain") or ""),
                str(item.get("status") or ""),
            ),
        )

    @classmethod
    def _merge_site_states(cls, snapshot_states: Any, refresh_states: Any) -> List[Dict[str, Any]]:
        """Merge the snapshot conclusion with the refresh-side per-site outcome.

        The snapshot layer decides whether today's increment can be computed.
        The refresh layer knows whether the site itself just failed, so a
        refresh ``fault``/``checker_error`` overrides an otherwise countable
        snapshot conclusion.
        """
        merged: Dict[str, Dict[str, Any]] = {}
        order: List[str] = []

        def state_key(item: Dict[str, Any]) -> str:
            return str(item.get("domain") or item.get("name") or "").strip().lower()

        def label_key(item: Dict[str, Any]) -> str:
            return str(item.get("name") or "").strip().lower()

        for item in (snapshot_states or []):
            if not isinstance(item, dict):
                continue
            key = state_key(item)
            if key not in merged:
                order.append(key)
            merged[key] = dict(item)

        def resolve_key(item: Dict[str, Any]) -> Optional[str]:
            """Match one refresh entry to a snapshot entry.

            The refresh coordinator normalizes host names through the
            MoviePilot helper while the snapshot layer uses the Signal domain
            helper, so a sub-domain site can produce two different keys for the
            same site.  Fall back to the display name and then to a
            dot-boundary suffix relation before treating it as a new site.
            """
            key = state_key(item)
            if key in merged:
                return key
            name = label_key(item)
            if name:
                for candidate_key, candidate in merged.items():
                    if label_key(candidate) == name:
                        return candidate_key
            if key:
                for candidate_key in merged:
                    if not candidate_key:
                        continue
                    if key.endswith(f".{candidate_key}") or candidate_key.endswith(f".{key}"):
                        return candidate_key
            return None

        for item in (refresh_states or []):
            if not isinstance(item, dict):
                continue
            key = resolve_key(item)
            if key is None:
                key = state_key(item)
                order.append(key)
                merged[key] = dict(item)
                continue
            current = merged[key]
            status = str(item.get("status") or "")
            if status in {"fault", "checker_error"}:
                current["status"] = status
                current["reason"] = str(item.get("reason") or current.get("reason") or "")
                current["alertable"] = status == "fault"
                if not str(current.get("name") or "").strip():
                    current["name"] = str(item.get("name") or "")
        return [merged[key] for key in order]

    @classmethod
    def _site_state_faults(cls, states: Any) -> List[Dict[str, Any]]:
        return [item for item in cls._sorted_site_states(states) if item.get("status") == "fault"]

    @classmethod
    def _site_state_counted(cls, states: Any) -> List[Dict[str, Any]]:
        return [item for item in cls._sorted_site_states(states) if item.get("status") == "ok"]

    @classmethod
    def _site_state_fingerprint_items(cls, states: Any) -> List[Dict[str, str]]:
        return [
            {"site": str(item.get("name") or item.get("domain") or ""), "reason": str(item.get("reason") or "")}
            for item in cls._sorted_site_states(states)
            if item.get("status") != "ok"
        ]

    @classmethod
    def _format_site_state_lines(cls, states: Any, *, suffix: str = "未计入今日增量") -> List[str]:
        """Render one line per excluded site instead of an aggregate count."""
        lines = []
        for item in cls._sorted_site_states(states):
            status = str(item.get("status") or "")
            if status == "ok":
                continue
            name = str(item.get("name") or item.get("domain") or "未知站点")
            label = cls.SITE_STAT_STATE_LABELS.get(status, "状态未知")
            reason = str(item.get("reason") or "").strip()
            detail = f"（{reason}）" if reason else ""
            lines.append(f"⦁ {name}：{label}{detail}，{suffix}")
        return lines

    def run_health_check_scheduled(self) -> bool:
        return self.run_health_check(scheduled=True)

    def run_health_check(self, scheduled: bool = False, notify: bool = False) -> bool:
        ok, _ = self._guard_task("健康巡查", "health_check")
        if not ok:
            return False
        try:
            data = self._build_health_summary()
        except Exception as err:
            logger.error(f"Signal 健康巡查执行失败：{err}", exc_info=True)
            check = self._health_result(
                "health_check",
                "checker_error",
                f"检查未完成：{str(err)[:160]}",
                affected_owner="signal-health-checker",
            )
            data = {"success": False, "complete": False, "checks": [check], "total": 1, "pass": 0, "fail": 1, "alertable_fail": 0, "incomplete": 1}
        checks = [self._normalize_health_result(item) for item in (data.get("checks") or [])]
        data["checks"] = checks
        text = self._format_health_summary(data)
        failed = int(data.get("fail") or 0)
        alertable_checks = [item for item in checks if item.get("alertable") is True]
        success = bool(data.get("success")) and failed == 0
        complete = bool(data.get("complete", all(item.get("complete") for item in checks)))
        self._save_task_result("健康巡查", success, 0 if success else 1, text)
        self.save_data("last_health_check", {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "success": success,
            "checks": data.get("checks") or [],
            "total": data.get("total") or 0,
            "pass": data.get("pass") or 0,
            "fail": failed,
            "alertable_fail": len(alertable_checks),
            "incomplete": int(data.get("incomplete") or 0),
            "complete": complete,
            "output": text,
        })
        if alertable_checks:
            if self._health_check_notify:
                failed_checks = []
                ordinary_scheduled = scheduled and not self._fusion_notify_enabled
                if ordinary_scheduled:
                    for item in alertable_checks:
                        failed_checks.append({
                            "name": str(item.get("name") or ""),
                            "target": str(item.get("target") or item.get("path") or ""),
                            "severity": str(item.get("severity") or "error"),
                            "detail": self._normalize_notification_error_summary(
                                item.get("detail") or item.get("error") or ""
                            ),
                        })
                    failed_checks.sort(key=lambda item: (
                        item["name"], item["target"], item["severity"], item["detail"]
                    ))
                owners = sorted({str(item.get("affected_owner") or "") for item in alertable_checks if item.get("affected_owner")})
                affected_owner = owners[0] if len(owners) == 1 else "multiple:" + ",".join(owners)
                labels = self._health_name_map()
                title = (
                    f"Signal - {labels.get(alertable_checks[0].get('name'), alertable_checks[0].get('name') or '巡查项')}异常"
                    if len(alertable_checks) == 1
                    else f"Signal - 健康巡查发现 {len(alertable_checks)} 项异常"
                )
                self._notify_fusion_task_outcome(
                    mtype=self._notification_type(self._health_check_notify_type),
                    title=title,
                    text="\n".join([f"发现 {len(alertable_checks)} 项异常", *self._health_failure_lines({"checks": alertable_checks})]),
                    outcome=f"巡检发现 {len(alertable_checks)} 项异常",
                    success=False,
                    component="health_check",
                    task_key="health_check",
                    task_group="维护任务",
                    affected_owner=affected_owner,
                    notification_status="error" if ordinary_scheduled else "",
                    notification_target="health_check",
                    notification_fingerprint=(
                        self._notification_outcome_fingerprint({"checks": failed_checks})
                        if ordinary_scheduled else ""
                    ),
                    notification_cooldown=ordinary_scheduled,
                    notification_manual=notify,
                )
        elif success and complete and (
            scheduled or (notify and self._health_check_completion_notify_enabled)
        ) and not self._fusion_notify_enabled:
            self._notify_fusion_task_outcome(
                mtype=self._notification_type(
                    self._health_check_completion_notify_type
                    if self._health_check_completion_notify_enabled
                    else self._health_check_notify_type
                ),
                title="Signal - 健康巡查完成",
                text=text,
                outcome="巡检完成，未发现异常",
                success=True,
                component="health_check",
                task_key="health_check",
                task_group="维护任务",
                affected_owner="health",
                notification_status="recovered",
                notification_target="health_check",
                notification_notify_noop=self._health_check_completion_notify_enabled,
                notification_manual=notify,
            )
        elif success and complete and self._health_check_completion_notify_enabled:
            self._notify_fusion_task_outcome(
                mtype=self._notification_type(self._health_check_completion_notify_type),
                title="Signal - 健康巡查完成",
                text=text,
                outcome="巡检完成，未发现异常",
                success=True,
                component="health_check",
                task_key="health_check",
                task_group="维护任务",
                affected_owner="health",
            )
        return success
    def _get_today_transfers_locked(self) -> List[str]:
        try:
            rows = self._today_transfer_rows_locked()
            grouped: Dict[Any, Dict[str, Any]] = {}
            for r in rows:
                if not getattr(r, "status", False):
                    continue
                title = getattr(r, "title", None) or "未命名"
                year = getattr(r, "year", None) or "未知年份"
                media_type = str(getattr(r, "type", None) or "").strip().lower()
                season = getattr(r, "seasons", None) or ""
                episode = getattr(r, "episodes", None) or ""
                key = (title, year)
                grouped.setdefault(key, {"is_tv": media_type in {"电视剧", "tv"}, "seasons": {}})
                if grouped[key]["is_tv"] and season and episode:
                    try:
                        s_num = int(str(season).replace("S", ""))
                        e_num = int(str(episode).replace("E", ""))
                        grouped[key]["seasons"].setdefault(s_num, []).append(e_num)
                    except Exception:
                        pass
            items = []
            for (title, year), info in grouped.items():
                seasons_dict = info.get("seasons") or {}
                if not info.get("is_tv") or not seasons_dict:
                    items.append(f"⦁ {title} ({year})")
                    continue
                season_strs = []
                for s_num in sorted(seasons_dict.keys()):
                    season_strs.append(f"S{s_num:02d}" + self._episode_ranges(sorted(set(seasons_dict[s_num]))))
                items.append(f"⦁ {title} ({year}) {', '.join(season_strs)}")
            return items or ["⦁ 无"]
        except Exception:
            return ["⦁ 未取到"]
    def _get_transfer_health_locked(self) -> List[str]:
        success_items = [str(x or "").strip() for x in self._get_today_downloads_locked() if str(x or "").strip()]
        success_items = [x for x in success_items if x not in {"⦁ 无", "• 无", "无"}]
        failed_items = self._get_transfer_failures_locked()
        failed_items = [x for x in failed_items if x not in {"⦁ 无", "• 无", "无"}]
        return (success_items + failed_items) or ["⦁ 无"]
    def _get_site_increment_locked(self) -> List[str]:
        """Return the canonical site-increment presentation used by reports and Fusion.

        The dashboard API and the report used to maintain two subtly different
        implementations.  Rendering the API snapshot here keeps stale, partial
        and counter-reset states consistent across every notification surface.
        """
        try:
            snapshot = self._site_increment_snapshot()
            if snapshot.get("error"):
                return [f"⦁ 异常 - {snapshot['error']}"]

            rows = []
            for item in snapshot.get("sites") or []:
                name = str(item.get("name") or "未知站点")
                extras = []
                if item.get("ratio") not in (None, ""):
                    extras.append(f"📊 {item['ratio']}")
                if item.get("bonus") not in (None, ""):
                    extras.append(f"🪙 {self._format_metric_number(item['bonus'])}")
                suffix = "｜" + "｜".join(extras) if extras else ""
                rows.append(
                    f"⦁ {name}：⬆ {self._format_bytes(item.get('upload', 0))} ｜ "
                    f"⬇ {self._format_bytes(item.get('download', 0))}{suffix}"
                )
            rows.extend(self._format_site_state_lines(snapshot.get("site_states")))
            if rows:
                return rows
            if snapshot.get("baseline_missing") and not snapshot.get("baseline_ready"):
                return ["⦁ 暂无增量（基线不足）"]
            return ["⦁ 无"]
        except Exception as e:
            return [f"⦁ 异常 - {e}"]
    def _site_increment_snapshot(self) -> Dict[str, Any]:
        """站点上传/下载增量快照，逐站点四态、只认今日口径。

        Every active site gets its own ``ok``/``fault``/``unavailable``/
        ``checker_error`` state in ``site_states``.  ``basis`` is always
        ``today``: a snapshot that was not updated today is ``unavailable``
        rather than a fallback increment, so an old value can never be
        published as today's result.  Individual unavailable sites never
        cancel the run; the publishing layer only asks whether any countable
        site remains.
        """
        result = {"date": self._today_prefix(), "basis": "today", "sites": [], "upload_total": 0, "download_total": 0,
                  "baseline_ready": False, "baseline_missing": 0, "latest_date": "", "stale": False,
                  "stale_count": 0, "error_count": 0, "invalid_count": 0, "counter_reset_count": 0,
                  "data_valid": False, "active_count": 0, "visible_count": 0, "missing_count": 0,
                  "active_domains": [], "site_states": [], "counted_count": 0, "fault_count": 0,
                  "unavailable_count": 0,
                  "latest_updated_at": "", "error": ""}
        try:
            from app.db.oper.site import SiteOper
            site_oper = SiteOper()
            latest_data = self._latest_site_userdata_rows(site_oper)
            active_sites = site_helpers.select_user_data_sites(site_oper.list_active() or [])
            active_domains = {
                site_helpers.normalize_site_domain(getattr(site, "domain", ""))
                for site in active_sites
                if site_helpers.normalize_site_domain(getattr(site, "domain", ""))
            }
            latest_data = [d for d in latest_data if d]
            # An explicit empty active-site set means there is nothing to report.
            # Falling back to every historical row can leak disabled/deleted sites.
            active_latest = [
                d for d in latest_data
                if site_helpers.normalize_site_domain(getattr(d, "domain", "")) in active_domains
            ]
            result["active_count"] = len(active_sites)
            result["visible_count"] = len(active_latest)
            result["missing_count"] = max(0, result["active_count"] - result["visible_count"])
            result["active_domains"] = sorted(active_domains)
            if len(active_domains) != result["active_count"]:
                result["error"] = "启用站点存在无效域名，已取消统计以避免使用旧快照"
                return result
            today = self._today_prefix()
            result["date"] = today
            result["basis"] = "today"
            error_count = len([d for d in active_latest if str(getattr(d, "err_msg", None) or "").strip()])
            valid_latest = [d for d in active_latest if not str(getattr(d, "err_msg", None) or "").strip()]
            all_days = sorted({self._normalize_day(getattr(d, "updated_day", None)) for d in active_latest if self._normalize_day(getattr(d, "updated_day", None))}, reverse=True)
            latest_day = all_days[0] if all_days else ""
            result["latest_date"] = latest_day
            latest_timestamps = []
            for row in active_latest:
                day = self._normalize_day(getattr(row, "updated_day", None))
                clock = str(getattr(row, "updated_time", None) or "")[:8]
                if day and re.match(r"^\d{2}:\d{2}:\d{2}$", clock):
                    latest_timestamps.append(f"{day} {clock}")
            result["latest_updated_at"] = max(latest_timestamps, default="")
            result["error_count"] = error_count
            result["invalid_count"] = len([d for d in active_latest if not self._normalize_day(getattr(d, "updated_day", None))])
            result["stale_count"] = len([d for d in active_latest if self._normalize_day(getattr(d, "updated_day", None)) not in ("", today)])
            result["stale"] = bool(result["stale_count"])
            result["data_valid"] = (
                result["visible_count"] == result["active_count"]
                and error_count == 0
                and result["invalid_count"] == 0
                and result["stale_count"] == 0
            )
            site_labels: Dict[str, str] = {}
            for site in active_sites:
                label_key = site_helpers.normalize_site_domain(getattr(site, "domain", ""))
                if label_key:
                    site_labels.setdefault(label_key, str(getattr(site, "name", None) or label_key))
            rows_by_domain: Dict[str, Any] = {}
            for row in active_latest:
                row_key = site_helpers.normalize_site_domain(getattr(row, "domain", ""))
                if row_key:
                    rows_by_domain.setdefault(row_key, row)
            states: Dict[str, Dict[str, Any]] = {}
            countable: Dict[str, Any] = {}
            for site_domain in sorted(active_domains):
                row = rows_by_domain.get(site_domain)
                label = site_labels.get(site_domain) or site_domain
                if row is None:
                    states[site_domain] = self._site_stat_state(label, site_domain, "unavailable", "没有最新快照")
                    continue
                label = str(getattr(row, "name", None) or label)
                row_error = str(getattr(row, "err_msg", None) or "").strip()
                if row_error:
                    states[site_domain] = self._site_stat_state(label, site_domain, "fault", row_error[:120])
                    continue
                row_day = self._normalize_day(getattr(row, "updated_day", None))
                if not row_day:
                    states[site_domain] = self._site_stat_state(label, site_domain, "unavailable", "缺少有效日期")
                    continue
                if row_day != today:
                    states[site_domain] = self._site_stat_state(
                        label, site_domain, "unavailable", f"快照未更新到今日（最新 {row_day}）"
                    )
                    continue
                states[site_domain] = self._site_stat_state(label, site_domain, "unavailable", "今日增量未计算")
                countable[site_domain] = row

            def publish_states() -> None:
                site_states = self._sorted_site_states(states.values())
                result["site_states"] = site_states
                result["counted_count"] = len(self._site_state_counted(site_states))
                result["fault_count"] = len(self._site_state_faults(site_states))
                result["unavailable_count"] = len([item for item in site_states if item.get("status") == "unavailable"])

            if not active_latest:
                publish_states()
                return result
            previous_cache: Dict[str, List[Any]] = {}
            out: List[Dict[str, Any]] = []
            baseline_ready_count = 0
            baseline_missing_count = 0
            counter_reset_count = 0
            for current in valid_latest:
                name = getattr(current, "name", None) or getattr(current, "domain", None) or "未知站点"
                domain = getattr(current, "domain", None)
                state_key = site_helpers.normalize_site_domain(domain)
                if state_key not in countable:
                    continue
                delta = None
                baseline_found = False
                base_dt = datetime.strptime(today, "%Y-%m-%d")
                for i in range(1, 8):
                    prev_day = (base_dt - timedelta(days=i)).strftime("%Y-%m-%d")
                    if prev_day not in previous_cache:
                        previous_cache[prev_day] = site_oper.get_userdata_by_date(prev_day) or []
                    previous = self._find_site_userdata_snapshot(previous_cache[prev_day], name, domain)
                    if previous:
                        baseline_found = True
                        delta, reason = self._site_userdata_delta_with_reason(current, previous)
                        if reason == "counter_reset":
                            counter_reset_count += 1
                            states[state_key] = self._site_stat_state(name, domain, "unavailable", "累计值回退")
                            break
                        if reason == "invalid":
                            baseline_missing_count += 1
                            states[state_key] = self._site_stat_state(name, domain, "unavailable", "基线数据无效")
                            break
                    if delta is not None:
                        break
                if delta is None and not baseline_found:
                    baseline_missing_count += 1
                    states[state_key] = self._site_stat_state(name, domain, "unavailable", "缺少有效基线")
                    continue
                if delta is None:
                    continue
                baseline_ready_count += 1
                up, dl = delta
                states[state_key] = self._site_stat_state(name, domain, "ok", "", upload=up, download=dl)
                if up == 0 and dl == 0:
                    continue
                out.append({
                    "name": name,
                    "upload": up,
                    "download": dl,
                    "ratio": getattr(current, "ratio", None),
                    "bonus": getattr(current, "bonus", None),
                })
            publish_states()
            result["sites"] = out
            result["upload_total"] = sum(int(d.get("upload", 0)) for d in out)
            result["download_total"] = sum(int(d.get("download", 0)) for d in out)
            result["baseline_ready"] = bool(baseline_ready_count)
            result["baseline_missing"] = baseline_missing_count
            result["counter_reset_count"] = counter_reset_count
            result["data_valid"] = bool(active_latest) and not any(
                (
                    result["stale_count"],
                    result["error_count"],
                    result["invalid_count"],
                    result["counter_reset_count"],
                    result["baseline_missing"],
                    result["missing_count"],
                )
            )
        except Exception as err:
            result["error"] = str(err)
            logger.warning(f"Signal 站点增量数据获取失败：{err}")
        return result

    @classmethod
    def _latest_site_userdata_rows(cls, site_oper: Any) -> List[Any]:
        """Return one newest row per domain, including the newest error row.

        MoviePilot's ``get_userdata_latest`` intentionally filters error rows.
        That is useful for healthy-site consumers but loses the fact that a
        refresh just failed.  Site statistics must retain that signal so an
        error cannot silently look like an old successful snapshot.
        """
        getter = getattr(site_oper, "get_userdata", None)
        rows = getter() if callable(getter) else None
        if not rows:
            rows = site_oper.get_userdata_latest() or []
        return site_helpers.select_latest_site_userdata_rows(rows)
    def _site_increment_data(self) -> List[Dict[str, Any]]:
        """今日各站点上传/下载增量（原始字节），供旧调用兼容。"""
        return list((self._site_increment_snapshot().get("sites") or []))
    def _get_site_health_locked(self) -> List[str]:
        try:
            from app.db.oper.site import SiteOper
            site_oper = SiteOper()
            latest = self._latest_site_userdata_rows(site_oper)
            active_sites = site_helpers.select_user_data_sites(site_oper.list_active() or [])
            active_domains = {
                site_helpers.normalize_site_domain(getattr(site, "domain", ""))
                for site in active_sites
                if site_helpers.normalize_site_domain(getattr(site, "domain", ""))
            }
            latest = [
                row for row in latest
                if row and site_helpers.normalize_site_domain(getattr(row, "domain", "")) in active_domains
            ]
            if not latest:
                return ["⦁ 未取到站点快照"]
            today = self._today_prefix()
            normal_count = 0
            warnings = []
            for row in latest:
                name = getattr(row, "name", None) or getattr(row, "domain", None) or "未知站点"
                err = str(getattr(row, "err_msg", None) or "").strip()
                day = self._normalize_day(getattr(row, "updated_day", None))
                if err:
                    warnings.append(f"⦁ {name} | 异常（{err[:30]}）")
                elif day == today:
                    normal_count += 1
                else:
                    warnings.append(f"⦁ {name} | 数据过期")
            if warnings:
                prefix = [f"⦁ 正常 {normal_count} 个站点"] if normal_count else []
                return prefix + warnings
            return [f"⦁ 全部 {normal_count} 个站点正常"]
        except Exception as e:
            return [f"⦁ 未取到 - {e}"]
    def _get_downloader_health_locked(self) -> List[str]:
        """获取下载器状态，支持多下载器显示"""
        try:
            from app.sdk.services import DownloaderHelper
            from app.chain.download import DownloadChain

            downloader_helper = DownloaderHelper()
            services = downloader_helper.get_services()

            if not services:
                return ["⦁ 未配置下载器"]

            # 获取所有正在下载的任务
            downloading = DownloadChain().downloading() or []

            if not downloading:
                return ["⦁ 正在下载：无"]

            # 按下载器分组统计
            downloader_stats = {}
            for torrent in downloading:
                dl_name = getattr(torrent, "downloader", None) or "未知"
                if dl_name not in downloader_stats:
                    downloader_stats[dl_name] = {"count": 0, "down_speed": 0, "up_speed": 0}
                downloader_stats[dl_name]["count"] += 1
                downloader_stats[dl_name]["down_speed"] += int(getattr(torrent, "dlspeed", 0) or 0)
                downloader_stats[dl_name]["up_speed"] += int(getattr(torrent, "upspeed", 0) or 0)

            items = []
            for dl_name, stats in downloader_stats.items():
                speed_info = f"↓ {self._format_bytes(stats['down_speed'])}/s ↑ {self._format_bytes(stats['up_speed'])}/s" if (stats['down_speed'] or stats['up_speed']) else ""
                if speed_info:
                    items.append(f"⦁ {dl_name}：{stats['count']} 个任务｜{speed_info}")
                else:
                    items.append(f"⦁ {dl_name}：{stats['count']} 个任务")

            return items or ["⦁ 正在下载：无"]
        except Exception as e:
            logger.warning(f"获取下载器状态失败：{e}")
            return ["⦁ 正在下载：无"]
    def _get_downloading_locked(self, limit: int = 10) -> List[str]:
        try:
            from app.chain.download import DownloadChain
            tasks = DownloadChain().downloading() or []
            items = []
            for t in tasks[:limit]:
                title = getattr(t, "title", None) or getattr(t, "name", None) or "未命名任务"
                progress = getattr(t, "progress", None)
                if progress is not None:
                    try:
                        items.append(f"⦁ {title} ({float(progress):.1f}%)")
                    except Exception:
                        items.append(f"⦁ {title}")
                else:
                    items.append(f"⦁ {title}")
            return items or ["⦁ 无"]
        except Exception:
            return ["⦁ 未查询"]
    def _get_today_downloads_locked(self) -> List[str]:
        """今日下载明细：以今日入库(转移历史)成功记录为准，展示“哪部剧·哪些集数”，
        并用下载器种子的做种时长(按 download_hash 命中)互相印证，得到“（做种：Xh）”。
        采用用户建议的口径：今日成功入库即今日已下载入库，比单纯数下载器做种数更准确。"""
        try:
            rows = self._today_transfer_rows_locked()
        except Exception:
            rows = []
        success_rows = [r for r in rows if getattr(r, "status", False)]
        if not success_rows:
            return ["⦁ 无"]
        # download_hash -> 做种秒数（尽力获取，用于互相印证；取不到则不展示做种时长）
        seed_map = self._downloader_seed_map()
        grouped: Dict[Any, Dict[str, Any]] = {}
        order: List[Any] = []
        for r in success_rows:
            title = getattr(r, "title", None) or "未命名"
            year = getattr(r, "year", None) or ""
            media_type = str(getattr(r, "type", None) or "").strip().lower()
            season = getattr(r, "seasons", None) or ""
            episode = getattr(r, "episodes", None) or ""
            dl_hash = str(getattr(r, "download_hash", None) or "").strip().lower()
            key = (title, year)
            if key not in grouped:
                grouped[key] = {"is_tv": media_type in {"电视剧", "tv"}, "seasons": {}, "seed": 0}
                order.append(key)
            if grouped[key]["is_tv"] and season and episode:
                try:
                    s_num = int(str(season).replace("S", ""))
                    e_num = int(str(episode).replace("E", ""))
                    grouped[key]["seasons"].setdefault(s_num, []).append(e_num)
                except Exception:
                    pass
            if dl_hash and dl_hash in seed_map:
                grouped[key]["seed"] = max(grouped[key]["seed"], seed_map[dl_hash])
        items = []
        for key in order:
            title, year = key
            info = grouped[key]
            label = f"{title} ({year})" if year else f"{title}"
            seasons_dict = info.get("seasons") or {}
            if info.get("is_tv") and seasons_dict:
                season_strs = []
                for s_num in sorted(seasons_dict.keys()):
                    season_strs.append(f"S{s_num:02d}" + self._episode_ranges(sorted(set(seasons_dict[s_num]))))
                label = f"{label} {', '.join(season_strs)}"
            seed = info.get("seed") or 0
            tail = f"（做种：{self._format_duration(seed)}）" if seed else ""
            items.append(f"  - {label}{tail}")
        return items
    def _get_storage_health_locked(self) -> List[str]:
        """按 MP 配置的存储分别显示真实用量。
        与 MoviePilot 官方仪表盘 _build_storage 口径一致：只展示能取到真实用量的存储；
        取不到用量的（未真正配置/不支持用量查询）一律不展示，避免“已配置”噪声行。"""
        try:
            from app.db.oper.systemconfig import SystemConfigOper
            from app.schemas.types import SystemConfigKey
            from app.application.directory import DirectoryHelper

            try:
                storages = SystemConfigOper().get(SystemConfigKey.Storages) or []
            except Exception:
                storages = []

            # 各存储用量（网络盘）——不同版本 API 可能不同，取不到则回退
            usage_map = {}
            try:
                from app.chain.storage import StorageChain
                sc = StorageChain()
                for s in storages:
                    try:
                        u = sc.storage_usage(s.get("type") or "local")
                        if u:
                            usage_map[s.get("name")] = u
                    except Exception:
                        pass
            except Exception:
                pass

            # 本地磁盘路径（供 local 存储 disk_usage）
            local_path = None
            try:
                dirs = (DirectoryHelper().get_library_dirs() or []) + (DirectoryHelper().get_download_dirs() or [])
                for d in dirs:
                    p = getattr(d, "library_path", None) or getattr(d, "download_path", None) or getattr(d, "path", None)
                    st = getattr(d, "library_storage", None) or getattr(d, "storage", None)
                    if p and st in (None, "", "local"):
                        local_path = p
                        break
            except Exception:
                pass

            items = []
            for s in storages:
                name = s.get("name") or s.get("type") or "存储"
                stype = s.get("type") or "local"
                u = usage_map.get(s.get("name"))
                if u is not None:
                    total = u.get("total") if isinstance(u, dict) else getattr(u, "total", None)
                    used = u.get("used") if isinstance(u, dict) else getattr(u, "used", None)
                    free = (u.get("available") or u.get("free")) if isinstance(u, dict) else (getattr(u, "available", None) or getattr(u, "free", None))
                    self._append_usage_line(items, name, total, used, free)
                elif stype == "local" and local_path:
                    try:
                        total, used, free = shutil.disk_usage(local_path)
                        self._append_usage_line(items, name, total, used, free)
                    except Exception:
                        pass
                # 取不到真实用量的存储（未配置/不支持用量查询）不展示，避免“已配置”噪声行

            # 无任何存储配置时回退本地常见路径
            if not items:
                for candidate, label in [("/media", "媒体库"), ("/downloads", "下载目录"), ("/config", "配置目录")]:
                    if os.path.exists(candidate):
                        try:
                            total, used, free = shutil.disk_usage(candidate)
                            self._append_usage_line(items, label, total, used, free)
                        except Exception:
                            pass
            return items or ["⦁ 未检测到存储"]
        except Exception as e:
            logger.warning(f"获取存储空间失败：{e}")
            return [f"⦁ 存储检查异常：{e}"]
    def _health_directory_entries(self) -> List[Tuple[str, str, Any]]:
        from app.sdk.config import settings
        from app.application.directory import DirectoryHelper

        config_path = str(self._settings_value(settings, "CONFIG_PATH", "config_path", default="/config"))
        targets = [("配置目录", config_path, "local"), ("插件目录", str(Path(__file__).resolve().parent), "local")]
        helper = DirectoryHelper()
        for d in helper.get_download_dirs() or []:
            targets.append(("下载目录", getattr(d, "download_path", None) or getattr(d, "path", None), getattr(d, "storage", None)))
        for d in helper.get_library_dirs() or []:
            targets.append(("媒体库目录", getattr(d, "library_path", None) or getattr(d, "path", None), getattr(d, "library_storage", None) or getattr(d, "storage", None)))
        return self._dedupe_directory_entries(targets)
    def _health_directory_targets(self) -> List[Tuple[str, str]]:
        return [(label, path) for label, path, _ in self._health_directory_entries()]
    def _check_storage(self) -> Dict[str, Any]:
        """按 MoviePilot 配置的存储、下载目录与媒体库目录检查容量。"""
        try:
            from app.sdk.config import settings
        except Exception as err:
            return self._health_result(
                "storage",
                "checker_error",
                f"检查未完成：无法加载存储检查环境：{str(err)[:100]}",
                affected_owner="signal-health-checker",
            )

        selected = set(getattr(self, "_health_check_storage_targets", None) or ["storages", "config", "download", "library"])
        outcomes: List[Dict[str, Any]] = []

        def add_usage(label: str, path: str, storage: Any = "local") -> None:
            if not path:
                outcomes.append(self._health_result("storage", "unavailable", f"{label} 无可检查路径", affected_owner="persistent-storage", target=label))
                return
            if not self._is_local_storage(storage):
                outcomes.append(self._health_result("storage", "unavailable", f"{label} {storage} 无本地容量接口", affected_owner="persistent-storage", target=label))
                return
            try:
                stat = shutil.disk_usage(path)
            except (FileNotFoundError, PermissionError, OSError) as err:
                outcomes.append(self._health_result("storage", "fault", f"{label} 容量查询失败：{err}", affected_owner="persistent-storage", target=path))
                return
            except Exception as err:
                outcomes.append(self._health_result("storage", "checker_error", f"{label} 容量解析失败：{err}", affected_owner="signal-health-checker", target=path))
                return
            try:
                item_ok, detail = self._storage_usage_detail(label, stat.total, stat.used, stat.free)
                status = "ok" if item_ok else "fault"
                outcomes.append(self._health_result("storage", status, detail, affected_owner="persistent-storage", target=path))
            except Exception as err:
                outcomes.append(self._health_result("storage", "checker_error", f"{label} 容量解析失败：{err}", affected_owner="signal-health-checker", target=path))

        if "config" in selected:
            add_usage("配置目录", str(self._settings_value(settings, "CONFIG_PATH", "config_path", default="/config")))

        if selected.intersection({"download", "library"}):
            try:
                directory_entries = self._health_directory_entries()
            except Exception as err:
                outcomes.append(self._health_result("storage", "checker_error", f"目录配置解析失败：{str(err)[:100]}", affected_owner="signal-health-checker"))
            else:
                for label, path, storage in directory_entries:
                    if label.startswith("下载目录") and "download" in selected:
                        add_usage(label, path, storage)
                    if label.startswith("媒体库目录") and "library" in selected:
                        add_usage(label, path, storage)

        if "storages" in selected:
            try:
                from app.db.oper.systemconfig import SystemConfigOper
                from app.schemas.types import SystemConfigKey
                from app.chain.storage import StorageChain
            except Exception as err:
                outcomes.append(self._health_result("storage", "checker_error", f"存储检查依赖加载失败：{str(err)[:100]}", affected_owner="signal-health-checker"))
            else:
                try:
                    storages = SystemConfigOper().get(SystemConfigKey.Storages) or []
                except Exception as err:
                    outcomes.append(self._health_result("storage", "checker_error", f"存储配置读取失败：{str(err)[:100]}", affected_owner="signal-health-checker"))
                    storages = []
                if not storages:
                    outcomes.append(self._health_result("storage", "unavailable", "未配置可查询容量的存储", affected_owner="persistent-storage"))
                else:
                    sc = StorageChain()
                    for storage in storages:
                        if not isinstance(storage, dict):
                            outcomes.append(self._health_result("storage", "checker_error", "存储配置条目格式无效", affected_owner="signal-health-checker"))
                            continue
                        name = storage.get("name") or storage.get("type") or "存储"
                        storage_type = storage.get("type") or "local"
                        try:
                            usage = sc.storage_usage(storage_type)
                        except Exception as err:
                            outcomes.append(self._health_result("storage", "fault", f"{name} 容量查询失败：{str(err)[:100]}", affected_owner="persistent-storage", target=str(name)))
                            continue
                        if not usage:
                            outcomes.append(self._health_result("storage", "unavailable", f"{name} 无法检查容量", affected_owner="persistent-storage", target=str(name)))
                            continue
                        try:
                            total = usage.get("total") if isinstance(usage, dict) else getattr(usage, "total", None)
                            used = usage.get("used") if isinstance(usage, dict) else getattr(usage, "used", None)
                            free = (usage.get("available") or usage.get("free")) if isinstance(usage, dict) else (getattr(usage, "available", None) or getattr(usage, "free", None))
                            if int(total or 0) <= 0:
                                outcomes.append(self._health_result("storage", "unavailable", f"{name} 无法检查容量", affected_owner="persistent-storage", target=str(name)))
                                continue
                            item_ok, detail = self._storage_usage_detail(str(name), total, used, free)
                        except Exception as err:
                            outcomes.append(self._health_result("storage", "checker_error", f"{name} 容量数据解析失败：{str(err)[:100]}", affected_owner="signal-health-checker", target=str(name)))
                            continue
                        outcomes.append(self._health_result("storage", "ok" if item_ok else "fault", detail, affected_owner="persistent-storage", target=str(name)))

        return self._aggregate_health_results(
            "storage",
            outcomes,
            affected_owner="persistent-storage",
            unavailable_detail="未检测到可检查的存储",
        )
    def _build_health_summary(self, persist: bool = True) -> Dict[str, Any]:
        checks: List[Dict[str, Any]] = []
        try:
            from ..infrastructure.host_queries import count_subscriptions
        except Exception as err:
            checks.append(self._health_result("subscribe", "checker_error", f"订阅检查依赖加载失败：{str(err)[:120]}", affected_owner="signal-health-checker"))
        else:
            try:
                count = count_subscriptions()
                checks.append(self._health_result("subscribe", "ok", f"订阅 {count} 个", affected_owner="persistent-subscriptions"))
            except Exception as err:
                checks.append(self._health_result("subscribe", "fault", f"订阅查询失败：{str(err)[:120]}", affected_owner="persistent-subscriptions"))
        try:
            from app.db.oper.site import SiteOper
        except Exception as err:
            checks.append(self._health_result("sites", "checker_error", f"站点检查依赖加载失败：{str(err)[:120]}", affected_owner="signal-health-checker"))
        else:
            try:
                site_oper = SiteOper()
                sites = site_oper.list() or []
                active = site_oper.list_active() or []
                checks.append(self._health_result("sites", "ok", f"共 {len(sites)} 个，启用 {len(active)} 个", affected_owner="persistent-sites"))
            except Exception as err:
                checks.append(self._health_result("sites", "fault", f"站点查询失败：{str(err)[:120]}", affected_owner="persistent-sites"))
        try:
            from app.sdk.services import DownloaderHelper
        except Exception as err:
            checks.append(self._health_result("downloaders", "checker_error", f"下载器检查依赖加载失败：{str(err)[:120]}", affected_owner="signal-health-checker"))
        else:
            try:
                services = DownloaderHelper().get_services()
                checks.append(self._health_result("downloaders", "ok", f"在线 {len(services)} 个", affected_owner="downloaders"))
            except Exception as err:
                checks.append(self._health_result("downloaders", "fault", f"下载器查询失败：{str(err)[:120]}", affected_owner="downloaders"))
        try:
            services = self.get_service() or []
            checks.append(self._health_result("signal_services", "ok", f"已调度 {len(services)} 个", affected_owner="signal-runtime"))
        except Exception as err:
            checks.append(self._health_result("signal_services", "checker_error", f"本插件任务汇总失败：{str(err)[:120]}", affected_owner="signal-health-checker"))
        selected_items = set(self._health_check_items or ["数据库", "存储空间", "目录权限"])
        if "数据库" in selected_items:
            checks.append(self._check_database())
        if "存储空间" in selected_items:
            checks.append(self._check_storage())
        if "目录权限" in selected_items:
            checks.append(self._check_directory())
        checks = [self._normalize_health_result(item) for item in checks]
        faults = [item for item in checks if item["status"] == "fault"]
        checker_errors = [item for item in checks if item["status"] == "checker_error"]
        incomplete = [item for item in checks if item["status"] in {"unavailable", "checker_error"}]
        success = not faults and not checker_errors
        complete = not incomplete
        result = {
            "success": success,
            "complete": complete,
            "checks": checks,
            "total": len(checks),
            "pass": len([item for item in checks if item["ok"]]),
            "fail": len([item for item in checks if not item["ok"]]),
            "alertable_fail": len(faults),
            "incomplete": len(incomplete),
        }
        if persist:
            self.save_data("last_health_check", {
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "success": success,
                "checks": checks,
                "total": result["total"],
                "pass": result["pass"],
                "fail": result["fail"],
                "alertable_fail": result["alertable_fail"],
                "incomplete": result["incomplete"],
                "complete": complete,
                "output": self._format_health_summary(result),
            })
        return result
    @staticmethod
    def _health_name_map() -> Dict[str, str]:
        return {"subscribe": "订阅", "sites": "站点", "downloaders": "下载器", "signal_services": "本插件任务", "database": "数据库", "storage": "存储空间", "directory": "目录权限"}
    def _health_failure_lines(self, data: Dict[str, Any]) -> List[str]:
        name_map = self._health_name_map()
        lines = []
        for item in data.get("checks") or []:
            if item.get("ok"):
                continue
            label = name_map.get(item.get("name"), item.get("name") or "巡查项")
            detail = str(item.get("detail") or "未返回详情").strip()
            lines.append(f"⦁ {label}：{detail}")
        return lines
    @staticmethod
    def _format_health_summary(data: Dict[str, Any]) -> str:
        name_map = SiteStatsMixin._health_name_map()
        total = data.get("total", 0)
        passed = data.get("pass", 0)
        failed = data.get("fail", 0)
        head = "⦁ 状态：全部正常" if not failed else f"⦁ 状态：发现 {failed} 项异常"
        lines = [head, f"⦁ 巡查项：共 {total} 项，通过 {passed} 项，异常 {failed} 项"]
        for item in data.get("checks") or []:
            label = name_map.get(item.get("name"), item.get("name"))
            mark = "✅" if item.get("ok") else "⚠️"
            lines.append(f"⦁ {mark} {label}：{item.get('detail')}")
        return "\n".join(lines)
    @classmethod
    def _format_health_report_lines(cls, data: Dict[str, Any]) -> List[str]:
        """融合卡健康摘要：正常项只列名称，异常项才展开关键原因。"""
        name_map = cls._health_name_map()
        checks = data.get("checks") or []
        total = data.get("total", len(checks))
        passed = data.get("pass", len([item for item in checks if item.get("ok")]))
        failed = data.get("fail", len([item for item in checks if not item.get("ok")]))
        lines = [
            "⦁ 状态：全部正常" if not failed else f"⦁ 状态：发现 {failed} 项异常",
            f"⦁ 巡查项：共 {total} 项，通过 {passed} 项，异常 {failed} 项",
        ]
        ok_labels = []
        failure_lines = []
        for item in checks:
            label = name_map.get(item.get("name"), item.get("name") or "巡查项")
            if item.get("ok"):
                ok_labels.append(label)
                continue
            detail = cls._compact_health_detail(item.get("detail"))
            failure_lines.append(f"⦁ 异常：{label} - {detail}" if detail else f"⦁ 异常：{label}")
        if ok_labels:
            lines.append(f"⦁ 正常项：{'、'.join(ok_labels)}")
        lines.extend(failure_lines)
        return lines
    @staticmethod
    def _compact_health_detail(detail: Any, limit: int = 2) -> str:
        text = str(detail or "").strip()
        if not text:
            return ""
        parts = [part.strip() for part in re.split(r"[；;\n]+", text) if part and part.strip()]
        if not parts:
            return text[:120]
        important_keys = ("异常", "失败", "错误", "超时", "不存在", "权限不足", "超过", "偏紧", "未检测", "未取到", "无法", "不可", "未连接", "无响应")
        noise_keys = (" 正常", "连接正常", "由存储服务管理")
        important = [part for part in parts if any(key in part for key in important_keys)]
        useful = important or [part for part in parts if not any(key in part for key in noise_keys)]
        chosen = (useful or parts)[:limit]
        return "；".join(chosen)[:120]
    @classmethod
    def _compact_health_output_lines(cls, output: str) -> List[str]:
        lines = [line.strip() for line in str(output or "").splitlines() if line.strip()]
        if not lines:
            return []
        name_map = cls._health_name_map()
        known_labels = set(name_map.values())
        head = []
        ok_labels = []
        failures = []
        passthrough = []
        for line in lines:
            body = line.replace("⦁ ", "", 1).replace("• ", "", 1).strip()
            if body.startswith("状态：") or body.startswith("巡查项："):
                head.append(f"⦁ {body}")
                continue
            match = re.match(r"(✅|⚠️|⚠)\s*(.+?)：(.+)$", body)
            if not match:
                passthrough.append(line)
                continue
            mark, label, detail = match.group(1), match.group(2).strip(), match.group(3).strip()
            if mark == "✅" and label in known_labels:
                ok_labels.append(label)
            elif label in known_labels:
                compact = cls._compact_health_detail(detail)
                failures.append(f"⦁ 异常：{label} - {compact}" if compact else f"⦁ 异常：{label}")
            else:
                passthrough.append(line)
        if ok_labels or failures:
            out = head or (["⦁ 状态：全部正常"] if not failures else [f"⦁ 状态：发现 {len(failures)} 项异常"])
            if ok_labels:
                out.append(f"⦁ 正常项：{'、'.join(ok_labels)}")
            out.extend(failures)
            return out
        return head + passthrough
    def _github_latest_v2(self) -> str:
        version = self._backend_version_value()
        return version if version.startswith("v") else f"v{version}"

    @staticmethod
    def _today_prefix() -> str:
        return datetime.now().strftime("%Y-%m-%d")

    @staticmethod
    def _find_site_userdata_snapshot(rows: List[Any], name: str, domain: Optional[str] = None) -> Optional[Any]:
        return site_helpers.find_site_userdata_snapshot(rows, name, domain)

    @staticmethod
    def _site_userdata_number(row: Any, key: str) -> Optional[int]:
        return site_helpers.site_userdata_number(row, key)

    def _site_userdata_delta(self, current: Any, previous: Any) -> Optional[Tuple[int, int]]:
        delta, _reason = self._site_userdata_delta_with_reason(current, previous)
        return delta

    def _site_userdata_delta_with_reason(
        self, current: Any, previous: Any
    ) -> Tuple[Optional[Tuple[int, int]], str]:
        current_upload = self._site_userdata_number(current, "upload")
        current_download = self._site_userdata_number(current, "download")
        previous_upload = self._site_userdata_number(previous, "upload")
        previous_download = self._site_userdata_number(previous, "download")
        if current_upload is None or current_download is None:
            return None, "invalid"
        if previous_upload is None or previous_download is None:
            return None, "invalid"
        upload_delta = 0
        download_delta = 0
        if current_upload is not None and previous_upload is not None:
            if current_upload < previous_upload:
                return None, "counter_reset"
            upload_delta = max(0, current_upload - previous_upload)
        if current_download is not None and previous_download is not None:
            if current_download < previous_download:
                return None, "counter_reset"
            download_delta = max(0, current_download - previous_download)
        return (upload_delta, download_delta), "ok"

    def _downloader_overview_data(self) -> List[Dict[str, Any]]:
        """Return fixed, common downloader activity fields for the Dashboard."""
        out: List[Dict[str, Any]] = []
        try:
            from app.sdk.services import DownloaderHelper
            services = DownloaderHelper().get_services(name_filters=getattr(self, "_dltag_downloaders", None) or None) or {}
            for name, service in services.items():
                inst = getattr(service, "instance", None)
                dtype = str(getattr(getattr(service, "config", None), "type", "") or "").lower()
                if not inst or dtype not in {"qbittorrent", "transmission"}:
                    continue
                torrents, error = inst.get_torrents()
                if error:
                    out.append({"name": name, "type": dtype, "connected": False, "count": 0, "active": 0, "dl_speed": 0, "up_speed": 0, "downloaded": 0, "uploaded": 0, "activities": []})
                    continue
                row = {"name": name, "type": dtype, "connected": True, "count": 0, "active": 0, "dl_speed": 0, "up_speed": 0, "downloaded": 0, "uploaded": 0, "activities": []}
                for torrent in torrents or []:
                    row["count"] += 1
                    dl_speed = int(self._dltag_value(torrent, "dlspeed", "download_speed", "rateDownload") or 0)
                    up_speed = int(self._dltag_value(torrent, "upspeed", "upload_speed", "rateUpload") or 0)
                    row["dl_speed"] += dl_speed
                    row["up_speed"] += up_speed
                    row["downloaded"] += int(self._dltag_value(torrent, "downloaded", "downloadedEver") or 0)
                    row["uploaded"] += int(self._dltag_value(torrent, "uploaded", "uploadedEver") or 0)
                    state = str(self._dltag_value(torrent, "state", "status") or "")
                    if dl_speed > 0 or up_speed > 0 or state.lower() in {"downloading", "stalledup", "stalleddl", "seeding"}:
                        row["active"] += 1
                        if len(row["activities"]) < 3:
                            row["activities"].append({
                                "id": self._dltag_torrent_id(torrent),
                                "name": self._dltag_value(torrent, "name", "title") or "未命名任务",
                                "state": state or "活动中",
                                "progress": self._dltag_value(torrent, "progress") or 0,
                                "dl_speed": dl_speed,
                                "up_speed": up_speed,
                            })
                out.append(row)
        except Exception as err:
            logger.warning(f"Signal 下载器概览获取失败：{err}")
        return out

    def _append_usage_line(self, items: List[str], name: str, total: Any, used: Any, free: Any) -> bool:
        try:
            total = int(total or 0)
            if total <= 0:
                return False  # 无有效容量：视为未真正配置/不支持用量查询，不展示
            if used is None and free is not None:
                used = total - int(free)
            used = int(used or 0)
            if free is None:
                free = total - used
            free = int(free or 0)
            pct = used / total * 100 if total else 0
            icon = "🔴" if pct >= 85 else ("🟠" if pct >= 70 else "🟢")
            risk = " 空间偏紧" if pct >= 85 else ""
            items.append(f"⦁ {name}：已用 {pct:.0f}% ｜ {self._format_compact_bytes(used)}/{self._format_compact_bytes(total)} {icon}{risk}")
            return True
        except Exception:
            return False

    def _add_storage_item(self, items: List[str], path: str, label: str, storage_type: str):
        """添加存储项到列表"""
        try:
            if storage_type == "local":
                total, used, free = shutil.disk_usage(path)
                self._append_usage_line(items, label, total, used, free)
            else:
                # 网络存储类型（115/alipan/rclone等）暂时标记为已配置
                items.append(f"⦁ {label}：已配置")
        except Exception as e:
            items.append(f"⦁ {label}：检查失败 - {str(e)[:30]}")

    def _check_database(self) -> Dict[str, Any]:
        """检查 MoviePilot 当前主库，详情里明确数据库类型与目标。"""
        try:
            from app.sdk.config import settings
            from sqlalchemy import create_engine, text
        except Exception as err:
            return self._health_result(
                "database",
                "checker_error",
                f"检查未完成：数据库检查依赖加载失败：{str(err)[:100]}",
                affected_owner="signal-health-checker",
            )

        outcomes: List[Dict[str, Any]] = []
        try:
            db_type = str(self._settings_value(settings, "DB_TYPE", "db_type", default="sqlite")).lower()
            targets = getattr(self, "_health_check_database_targets", None) or ["current"]
        except Exception as err:
            return self._health_result("database", "checker_error", f"数据库检查参数解析失败：{str(err)[:100]}", affected_owner="signal-health-checker")
        for target in targets:
            target = str(target or "current").lower()
            use_type = db_type if target in ("current", "main", "moviepilot") else target
            try:
                if use_type in ("postgres", "postgresql"):
                    url_getter = getattr(settings, "DB_POSTGRESQL_URL", None)
                    db_url = url_getter() if callable(url_getter) else self._settings_value(settings, "DB_URL", "db_url")
                    if not db_url:
                        outcomes.append(self._health_result("database", "unavailable", "PostgreSQL 连接地址为空，无法检查", affected_owner="persistent-database", target="postgresql"))
                        continue
                    label = "PostgreSQL 主库"
                else:
                    config_path = Path(str(self._settings_value(settings, "CONFIG_PATH", "config_path", default="/config")))
                    db_file = config_path / "user.db"
                    if not db_file.exists():
                        outcomes.append(self._health_result("database", "fault", f"SQLite 主库不存在：{db_file}", affected_owner="persistent-database", target=str(db_file)))
                        continue
                    db_url = f"sqlite:///{db_file.as_posix()}"
                    label = f"SQLite 主库 {db_file}"
                engine = create_engine(db_url, echo=False, pool_pre_ping=True)
            except Exception as err:
                outcomes.append(self._health_result("database", "checker_error", f"数据库检查参数或引擎创建失败：{str(err)[:100]}", affected_owner="signal-health-checker", target=use_type))
                continue
            try:
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
            except Exception as err:
                outcomes.append(self._health_result("database", "fault", f"{label} 查询失败：{str(err)[:100]}", affected_owner="persistent-database", target=label))
            else:
                outcomes.append(self._health_result("database", "ok", f"{label} 连接正常", affected_owner="persistent-database", target=label))
            finally:
                dispose = getattr(engine, "dispose", None)
                if callable(dispose):
                    dispose()
        return self._aggregate_health_results(
            "database",
            outcomes,
            affected_owner="persistent-database",
            unavailable_detail="没有可检查的数据库目标",
        )

    def _storage_usage_detail(self, label: str, total: Any, used: Any, free: Any) -> Tuple[bool, str]:
        total = int(total or 0)
        if total <= 0:
            return True, f"{label} 未取到容量"
        if used is None and free is not None:
            used = total - int(free or 0)
        used = int(used or 0)
        pct = used / total * 100 if total else 0
        ok = pct < self._health_check_storage_threshold
        risk = "" if ok else f" 超过阈值 {self._health_check_storage_threshold}%"
        return ok, f"{label} {pct:.0f}% 已用｜{self._format_bytes(used)}/{self._format_bytes(total)}{risk}"

    def _check_directory(self) -> Dict[str, Any]:
        """按选择范围检查关键目录是否存在且可读写进入。"""
        try:
            selected = set(getattr(self, "_health_check_directory_targets", None) or ["config", "plugin", "download", "library"])
            wanted = {
                "config": "配置目录",
                "plugin": "插件目录",
                "download": "下载目录",
                "library": "媒体库目录",
            }
            entries = self._health_directory_entries()
        except Exception as err:
            return self._health_result("directory", "checker_error", f"目录检查参数解析失败：{str(err)[:100]}", affected_owner="signal-health-checker")
        outcomes: List[Dict[str, Any]] = []
        for label, path, storage in entries:
            if not any(label.startswith(wanted[key]) for key in selected if key in wanted):
                continue
            if not self._is_local_storage(storage):
                outcomes.append(self._health_result("directory", "unavailable", f"{label} {storage} 由存储服务管理，无法本地检查", affected_owner="persistent-directory", target=str(path or label)))
                continue
            try:
                exists = os.path.exists(path)
                accessible = os.access(path, os.R_OK | os.W_OK | os.X_OK) if exists else False
            except Exception as err:
                outcomes.append(self._health_result("directory", "checker_error", f"{label} 路径解析失败：{str(err)[:100]}", affected_owner="signal-health-checker", target=str(path or label)))
                continue
            if not exists:
                outcomes.append(self._health_result("directory", "fault", f"{label} 不存在 {path}", affected_owner="persistent-directory", target=str(path)))
            elif not accessible:
                outcomes.append(self._health_result("directory", "fault", f"{label} 权限不足 {path}", affected_owner="persistent-directory", target=str(path)))
            else:
                outcomes.append(self._health_result("directory", "ok", f"{label} 正常", affected_owner="persistent-directory", target=str(path)))
        return self._aggregate_health_results(
            "directory",
            outcomes,
            affected_owner="persistent-directory",
            unavailable_detail="未选择目录",
        )

    def _get_health_report_locked(self, persist_missing: bool = True) -> List[str]:
        """融合卡健康巡查栏目：优先使用最近巡查结果，没有记录时现场生成一次。"""
        data = self.get_data("last_health_check") or {}
        if data.get("checks"):
            return self._format_health_report_lines(data)
        output = str(data.get("output") or "").strip()
        if not output and self._health_check_enabled:
            try:
                summary = self._build_health_summary(persist=persist_missing)
                return self._format_health_report_lines(summary)
            except Exception as err:
                output = f"⦁ 状态：巡查失败\n⦁ 异常：{str(err)[:120]}"
        return self._compact_health_output_lines(output) or ["⦁ 尚无健康巡查记录"]
