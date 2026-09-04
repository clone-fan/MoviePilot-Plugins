"""Auto Remove seed cleaning workflows."""

import os
import re
import hashlib
import json
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from app.sdk.logging import logger
from app.sdk.config import settings
from app.schemas.types import MessageType


class SeedCleanMixin:
    """Auto seed cleaning and seed matching; downloader helper lives in its own mixin."""

    def _downloader_seed_map(self) -> Dict[str, int]:
        """汇总所有下载器的 {种子hash: 做种秒数}，供入库记录的 download_hash 互相印证做种时长。
        做种时长口径对齐官方“自动删种(TorrentRemover)”插件：优先用完成时间算 now−完成
        （qb completion_on / tr done_date，未完成回退 added_on/added_date），取不到再退化到
        seeding_time 字段，分别对应 qbittorrent 与 transmission 的当前返回对象。"""
        seed_map: Dict[str, int] = {}
        try:
            from app.sdk.services import DownloaderHelper
            services = DownloaderHelper().get_services() or {}
        except Exception:
            return seed_map

        def _f(obj, *names):
            for n in names:
                v = obj.get(n) if isinstance(obj, dict) else getattr(obj, n, None)
                if v not in (None, ""):
                    return v
            return None

        now_ts = datetime.now().timestamp()

        def _since(ts_val) -> int:
            """把“完成/添加时间”换算成距今秒数；兼容 unix 秒(int) 与 datetime。"""
            try:
                ts = ts_val.timestamp() if hasattr(ts_val, "timetuple") else float(ts_val)
                if ts <= 0:
                    return 0
                return max(0, int(now_ts - ts))
            except Exception:
                return 0

        def _seed_seconds(t) -> int:
            comp = _f(t, "completion_on")                          # qb 完成时间(秒)
            if comp is not None and _since(comp):
                return _since(comp)
            dd = _f(t, "done_date", "added_date")                  # tr 完成/添加(datetime)
            if dd is not None and _since(dd):
                return _since(dd)
            add = _f(t, "added_on")                                 # qb 添加时间(秒)回退
            if add is not None and _since(add):
                return _since(add)
            st = _f(t, "seeding_time")                              # 兜底
            try:
                return int(st or 0)
            except Exception:
                return 0

        services_items = services.items() if isinstance(services, dict) else []
        for _name, service in services_items:
            inst = getattr(service, "instance", None)
            getter = getattr(inst, "get_torrents", None) if inst else None
            if not callable(getter):
                continue
            try:
                res = getter()
            except Exception:
                continue
            torrents = res[0] if isinstance(res, tuple) else res
            for t in (torrents or []):
                try:
                    h = _f(t, "hash", "hashString", "infohash_v1", "infohash")
                    if h is None:
                        continue
                    key = str(h).strip().lower()
                    seed_map[key] = max(seed_map.get(key, 0), _seed_seconds(t))
                except Exception:
                    continue
        return seed_map
    def run_seed_clean_scheduled(self) -> bool:
        return self.run_seed_clean(scheduled=True)

    def run_seed_clean(self, scheduled: bool = False, notify: bool = False) -> bool:
        """按规则在所选下载器中暂停/删除种子。默认动作为暂停，安全优先。"""
        name = "自动删种"
        ok, _ = self._guard_task(name, "seedclean")
        if not ok:
            return False
        if not self._seedclean_downloaders:
            text = "未执行：请先在配置页选择下载器。"
            self._save_task_result(name, False, 2, text)
            if (
                notify
                or (scheduled and not getattr(self, "_fusion_notify_enabled", False))
            ) and self._task_outcome_notification_enabled(self._seedclean_notify):
                self._notify_fusion_task_outcome(
                    mtype=self._notification_type(self._seedclean_notify_type),
                    title="自动删种异常",
                    text=text,
                    outcome="自动删种未执行：未选择下载器",
                    success=False,
                    component="seed_clean",
                    task_key="seed_clean",
                    task_group="维护任务",
                    notification_status="error",
                    notification_target="scheduled_run",
                    notification_fingerprint=self._notification_error_fingerprint(text),
                    notification_cooldown=True,
                    notification_manual=notify,
                )
            return False
        # 安全：未设置任何筛选条件时不处理，避免误伤全部种子
        if not self._seedclean_has_any_condition():
            text = "未执行：未设置任何筛选条件（大小/分享率/做种时间/上传速度/标签/路径/Tracker/状态/分类），为避免误删已跳过。"
            self._save_task_result(name, False, 2, text)
            if (
                notify
                or (scheduled and not getattr(self, "_fusion_notify_enabled", False))
            ) and self._task_outcome_notification_enabled(self._seedclean_notify):
                self._notify_fusion_task_outcome(
                    mtype=self._notification_type(self._seedclean_notify_type),
                    title="自动删种异常",
                    text=text,
                    outcome="自动删种未执行：未设置筛选条件",
                    success=False,
                    component="seed_clean",
                    task_key="seed_clean",
                    task_group="维护任务",
                    notification_status="error",
                    notification_target="scheduled_run",
                    notification_fingerprint=self._notification_error_fingerprint(text),
                    notification_cooldown=True,
                    notification_manual=notify,
                )
            return False
        try:
            result = self._seed_clean_run()
            lines = result.get("lines") or []
            text = "\n".join(lines) if lines else "本次没有符合条件的种子。"
            attempted = int(result.get("attempted") or 0)
            completed = int(result.get("completed") or 0)
            failed = int(result.get("failed") or 0)
            success = failed == 0
            notify_scheduled = (scheduled or notify) and self._task_outcome_notification_enabled(self._seedclean_notify)
            if notify_scheduled and (attempted or failed or notify or not getattr(self, "_fusion_notify_enabled", False)):
                notification_cooldown = bool(failed and not attempted)
                verb = str(result.get("verb") or "处理")
                outcome = (
                    f"已{verb} {completed} 个种子"
                    if success
                    else f"自动删种执行失败：成功处理 {completed} 个，失败 {failed} 项"
                )
                self._notify_fusion_task_outcome(
                    mtype=self._notification_type(self._seedclean_notify_type),
                    title="自动删种",
                    text=text,
                    outcome=outcome,
                    success=success,
                    component="seed_clean",
                    task_key="seed_clean",
                    task_group="维护任务",
                    notification_status=("error" if failed else ("changed" if attempted else "noop")),
                    notification_target="scheduled_run",
                    notification_fingerprint=(
                        self._notification_error_fingerprint(text)
                        if notification_cooldown else ""
                    ),
                    notification_cooldown=notification_cooldown,
                    notification_manual=notify,
                )
            self._save_task_result(name, success, 0 if success else 1, text)
            return success
        except Exception as err:
            self._save_task_result(name, False, -1, str(err))
            if (
                notify
                or (scheduled and not getattr(self, "_fusion_notify_enabled", False))
            ) and self._task_outcome_notification_enabled(self._seedclean_notify):
                self._notify_fusion_task_outcome(
                    mtype=self._notification_type(self._seedclean_notify_type),
                    title="自动删种异常",
                    text=f"自动删种执行失败：{err}",
                    outcome=f"自动删种执行失败：{str(err)[:120]}",
                    success=False,
                    component="seed_clean",
                    task_key="seed_clean",
                    task_group="维护任务",
                    notification_status="error",
                    notification_target="scheduled_run",
                    notification_fingerprint=self._notification_error_fingerprint(err),
                    notification_cooldown=True,
                    notification_manual=notify,
                )
            logger.error(f"Signal 自动删种执行失败：{err}")
            return False
    def _seedclean_has_any_condition(self) -> bool:
        return any([
            self._seedclean_size, self._seedclean_ratio, self._seedclean_time, self._seedclean_upspeed,
            self._seedclean_labels, self._seedclean_pathkeywords, self._seedclean_trackerkeywords,
            self._seedclean_errorkeywords, self._seedclean_torrentstates, self._seedclean_trtorrentstates, self._seedclean_torrentcategorys,
        ])

    def _seed_clean_candidates(self) -> List[Dict[str, Any]]:
        """Return the exact downloader targets consumed by execution."""
        from app.sdk.services import DownloaderHelper

        services = DownloaderHelper().get_services(name_filters=self._seedclean_downloaders) or {}
        candidates: List[Dict[str, Any]] = []
        for dl_name in self._seedclean_downloaders:
            service = services.get(dl_name)
            inst = getattr(service, "instance", None) if service else None
            if not inst:
                candidates.append({"downloader": dl_name, "type": "", "items": [], "error": "downloader_not_found"})
                continue
            try:
                if hasattr(inst, "is_inactive") and inst.is_inactive():
                    candidates.append({"downloader": dl_name, "type": "", "items": [], "error": "downloader_inactive"})
                    continue
            except Exception:
                pass
            dtype = str(getattr(getattr(service, "config", None), "type", "") or "")
            try:
                items = self._seed_remove_targets(inst, dtype)
                candidates.append({"downloader": dl_name, "type": dtype.lower(), "items": items, "error": ""})
            except Exception as err:
                logger.warning(f"Signal 自动删种候选计算失败 {dl_name}: {err}")
                candidates.append({"downloader": dl_name, "type": dtype.lower(), "items": [], "error": "candidate_calculation_failed"})
        return candidates

    def _seed_clean_run(self) -> Dict[str, Any]:
        from app.sdk.services import DownloaderHelper
        from app.sdk.utilities import StringUtils
        services = DownloaderHelper().get_services(name_filters=self._seedclean_downloaders) or {}
        verb_map = {"pause": "暂停", "delete": "删除种子", "deletefile": "删除种子和文件"}
        lines: List[str] = []
        attempted = 0
        completed = 0
        failed = 0
        action = self._seedclean_action
        candidate_groups = self._seed_clean_candidates()
        candidate_error_text = {
            "downloader_not_found": "未找到下载器实例，未执行",
            "downloader_inactive": "下载器未连接，未执行",
            "candidate_calculation_failed": "候选计算失败，未执行",
        }
        for group in candidate_groups:
            dl_name = group.get("downloader")
            group_error = str(group.get("error") or "")
            if group_error:
                failed += 1
                lines.append(f"⦁ {dl_name}：{candidate_error_text.get(group_error, '候选计算失败，未执行')}")
                continue
            service = services.get(dl_name)
            inst = getattr(service, "instance", None) if service else None
            if not inst:
                failed += 1
                lines.append(f"⦁ {dl_name}：未找到下载器实例，未执行")
                continue
            try:
                if hasattr(inst, "is_inactive") and inst.is_inactive():
                    failed += 1
                    lines.append(f"⦁ {dl_name}：下载器未连接，未执行")
                    continue
            except Exception:
                pass
            targets = group.get("items") or []
            if not targets:
                lines.append(f"⦁ {dl_name}：没有符合条件的种子")
                continue
            act = action
            done = 0
            group_failed = 0
            target_lines: List[str] = []
            for t in targets:
                tid = t.get("id")
                if act not in verb_map:
                    continue
                try:
                    size_text = StringUtils.str_filesize(t.get("size"))
                except Exception:
                    size_text = str(t.get("size") or "")
                target_text = f"{t.get('name')}｜{size_text}｜{t.get('site') or ''}"
                attempted += 1
                try:
                    if act == "pause":
                        action_ok = inst.stop_torrents(ids=[tid])
                    elif act == "delete":
                        action_ok = inst.delete_torrents(delete_file=False, ids=[tid])
                    elif act == "deletefile":
                        action_ok = inst.delete_torrents(delete_file=True, ids=[tid])
                    if not action_ok:
                        raise RuntimeError("MoviePilot 下载器接口返回失败")
                    done += 1
                    completed += 1
                    target_lines.append(f"  - 成功：{target_text}")
                    logger.info(f"自动删种 {verb_map.get(act, act)}：{t.get('name')}")
                except Exception as e:
                    failed += 1
                    group_failed += 1
                    target_lines.append(f"  - 失败：{target_text}")
                    logger.warning(f"自动删种处理失败 {t.get('name')}：{e}")
            summary = f"⦁ {dl_name}：{verb_map.get(act, act)} {done} 个"
            if group_failed:
                summary += f"，失败 {group_failed} 个"
            lines.append(summary)
            lines.extend(target_lines[:8])
        return {
            "lines": lines,
            "attempted": attempted,
            "completed": completed,
            "failed": failed,
            "action": action,
            "verb": verb_map.get(action, "处理"),
        }
    def _seed_remove_targets(self, inst, dtype: str) -> List[Dict[str, Any]]:
        from app.sdk.utilities import StringUtils
        tags = self._parse_csv(self._seedclean_labels)
        if self._seedclean_mponly:
            try:
                tags.append(settings.TORRENT_TAG)
            except Exception:
                pass
        try:
            torrents, error_flag = inst.get_torrents(tags=tags or None)
        except Exception as e:
            logger.warning(f"自动删种获取种子失败：{e}")
            raise RuntimeError("downloader_request_failed") from e
        if error_flag:
            raise RuntimeError("downloader_request_failed")
        is_qb = dtype.lower() == "qbittorrent"
        result: List[Dict[str, Any]] = []
        for torrent in (torrents or []):
            item = self._seed_match_qb(torrent) if is_qb else self._seed_match_tr(torrent)
            if item:
                result.append(item)
        # 辅种：同名同大小的其它种子一并处理
        if self._seedclean_samedata and result:
            remove_ids = {t.get("id") for t in result}
            plus = []
            for base in result:
                for torrent in (torrents or []):
                    if is_qb:
                        pid, pname, psize = torrent.hash, torrent.name, torrent.size
                        psite = StringUtils.get_url_sld(torrent.tracker)
                    else:
                        pid, pname, psize = torrent.hashString, torrent.name, torrent.total_size
                        psite = torrent.trackers[0].get("sitename") if getattr(torrent, "trackers", None) else ""
                    if pname == base.get("name") and psize == base.get("size") and pid not in remove_ids:
                        remove_ids.add(pid)
                        plus.append({
                            "id": pid,
                            "name": pname,
                            "site": psite,
                            "size": psize,
                        })
            result.extend(plus)
        return result
    def _seed_match_qb(self, torrent) -> Any:
        """qBittorrent 种子条件匹配，命中返回精简 dict，否则 None。任意异常按不匹配处理（安全方向）。"""
        from app.sdk.utilities import StringUtils
        try:
            date_done = torrent.completion_on if (torrent.completion_on and torrent.completion_on > 0) else torrent.added_on
            seeding = (datetime.now().timestamp() - date_done) if date_done else 0
            avg_up = (torrent.uploaded / seeding) if seeding else 0
            sizes = self._seedclean_size.split('-') if self._seedclean_size else []
            minsize = float(sizes[0]) * 1024 ** 3 if sizes else 0
            maxsize = float(sizes[-1]) * 1024 ** 3 if sizes else 0
            if self._seedclean_ratio and torrent.ratio <= float(self._seedclean_ratio):
                return None
            if self._seedclean_time and seeding <= float(self._seedclean_time) * 3600:
                return None
            if self._seedclean_size and (torrent.size >= int(maxsize) or torrent.size <= int(minsize)):
                return None
            if self._seedclean_upspeed and avg_up >= float(self._seedclean_upspeed) * 1024:
                return None
            if self._seedclean_pathkeywords and not re.findall(self._seedclean_pathkeywords, torrent.save_path or "", re.I):
                return None
            if self._seedclean_trackerkeywords and not re.findall(self._seedclean_trackerkeywords, torrent.tracker or "", re.I):
                return None
            if self._seedclean_torrentstates and torrent.state not in self._parse_csv(self._seedclean_torrentstates):
                return None
            if self._seedclean_torrentcategorys and (not torrent.category or torrent.category not in self._parse_csv(self._seedclean_torrentcategorys)):
                return None
            return {"id": torrent.hash, "name": torrent.name, "site": StringUtils.get_url_sld(torrent.tracker), "size": torrent.size}
        except Exception:
            return None
    def _seed_match_tr(self, torrent) -> Any:
        """Transmission 种子条件匹配，命中返回精简 dict，否则 None。任意异常按不匹配处理（安全方向）。"""
        try:
            if self._seedclean_trtorrentstates:
                tr_state_map = {"0": "stopped", "1": "check_pending", "2": "checking", "3": "download_pending", "4": "downloading", "5": "seed_pending", "6": "seeding"}
                expected = {tr_state_map.get(item.strip().lower(), item.strip().lower()) for item in self._parse_csv(self._seedclean_trtorrentstates)}
                status = str(getattr(torrent, "status", "") or "").lower()
                has_error = bool(getattr(torrent, "error", 0) or getattr(torrent, "error_string", ""))
                if status not in expected and not ("error" in expected and has_error):
                    return None
            # MoviePilot's transmission-rpc contract exposes these canonical
            # Python properties for the RPC doneDate/addedDate fields.
            date_done = torrent.done_date or torrent.added_date
            seeding = (datetime.now().timestamp() - date_done.timestamp()) if date_done else 0
            uploaded = torrent.ratio * torrent.total_size
            avg_up = (uploaded / seeding) if seeding else 0
            sizes = self._seedclean_size.split('-') if self._seedclean_size else []
            minsize = float(sizes[0]) * 1024 ** 3 if sizes else 0
            maxsize = float(sizes[-1]) * 1024 ** 3 if sizes else 0
            if self._seedclean_ratio and torrent.ratio <= float(self._seedclean_ratio):
                return None
            if self._seedclean_time and seeding <= float(self._seedclean_time) * 3600:
                return None
            if self._seedclean_size and (torrent.total_size >= int(maxsize) or torrent.total_size <= int(minsize)):
                return None
            if self._seedclean_upspeed and avg_up >= float(self._seedclean_upspeed) * 1024:
                return None
            if self._seedclean_pathkeywords and not re.findall(self._seedclean_pathkeywords, torrent.download_dir or "", re.I):
                return None
            if self._seedclean_trackerkeywords:
                trackers = getattr(torrent, "trackers", None)
                if not trackers or not any(re.findall(self._seedclean_trackerkeywords, tr.get("announce", ""), re.I) for tr in trackers):
                    return None
            if self._seedclean_errorkeywords and not re.findall(self._seedclean_errorkeywords, torrent.error_string or "", re.I):
                return None
            site = torrent.trackers[0].get("sitename") if getattr(torrent, "trackers", None) else ""
            return {"id": torrent.hashString, "name": torrent.name, "site": site, "size": torrent.total_size}
        except Exception:
            return None
