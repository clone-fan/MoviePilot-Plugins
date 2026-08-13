"""Site statistics and health check service mixin."""

import os
import re
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from app.log import logger
from ..domain import site_helpers


class SiteStatsMixin:
    """Site statistics, health checks, storage inspection, and report data collection."""


    def run_health_check(self) -> bool:
        ok, _ = self._guard_task("健康巡查", "health_check")
        if not ok:
            return False
        try:
            data = self._build_health_summary()
        except Exception as err:
            logger.error(f"Signal 健康巡查执行失败：{err}", exc_info=True)
            data = {"success": False, "checks": [{"name": "health_check", "ok": False, "detail": str(err)[:160]}], "total": 1, "pass": 0, "fail": 1}
        text = self._format_health_summary(data)
        failed = int(data.get("fail") or 0)
        success = bool(data.get("success")) and failed == 0
        self._save_task_result("健康巡查", success, 0 if success else 1, text)
        self.save_data("last_health_check", {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "success": success,
            "checks": data.get("checks") or [],
            "total": data.get("total") or 0,
            "pass": data.get("pass") or 0,
            "fail": failed,
            "output": text,
        })
        if failed:
            if self._health_check_notify:
                self._notify_fusion_task_outcome(
                    mtype=self._notification_type(self._health_check_notify_type),
                    title=f"MP 运维助手 - 健康巡查发现 {failed} 项异常",
                    text="\n".join([f"发现 {failed} 项异常", *self._health_failure_lines(data)]),
                    outcome=f"巡检发现 {failed} 项异常",
                    success=False,
                    component="health_check",
                    task_key="health_check",
                    task_group="维护任务",
                    affected_owner="persistent-storage",
                )
        elif self._health_check_completion_notify_enabled:
            self._notify_fusion_task_outcome(
                mtype=self._notification_type(self._health_check_completion_notify_type),
                title="MP 运维助手 - 健康巡查完成",
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
        try:
            from app.db.site_oper import SiteOper
            site_oper = SiteOper()
            latest_data = site_oper.get_userdata_latest() or []
            active_domains = {site.domain for site in (site_oper.list_active() or []) if getattr(site, "domain", None)}
            if active_domains:
                active_latest = [data for data in latest_data if data and getattr(data, "domain", None) in active_domains]
                latest_data = active_latest or [data for data in latest_data if data]
            else:
                latest_data = [data for data in latest_data if data]
            if not latest_data:
                return ["⦁ 无"]
            today = self._today_prefix()
            result = []
            previous_cache: Dict[str, List[Any]] = {}
            eligible_count = 0
            baseline_ready_count = 0
            baseline_missing_count = 0
            stale_count = 0
            stale_days: List[str] = []
            for current in sorted(latest_data, key=lambda row: (getattr(row, "name", None) or getattr(row, "domain", None) or "").lower()):
                site_name = getattr(current, "name", None) or getattr(current, "domain", None) or "未知站点"
                site_domain = getattr(current, "domain", None)
                current_day = self._normalize_day(getattr(current, "updated_day", None))
                err_msg = str(getattr(current, "err_msg", None) or "").strip()
                if err_msg:
                    result.append(f"⦁ {site_name}：异常 - {err_msg}")
                    continue
                if current_day != today:
                    stale_count += 1
                    if current_day:
                        stale_days.append(current_day)
                    continue
                eligible_count += 1
                delta = None
                for i in range(1, 8):
                    prev_day = (datetime.strptime(current_day, "%Y-%m-%d") - timedelta(days=i)).strftime("%Y-%m-%d")
                    if prev_day not in previous_cache:
                        previous_cache[prev_day] = site_oper.get_userdata_by_date(prev_day) or []
                    previous = self._find_site_userdata_snapshot(previous_cache[prev_day], site_name, site_domain)
                    if previous:
                        delta = self._site_userdata_delta(current, previous)
                    if delta is not None:
                        break
                if delta is None:
                    baseline_missing_count += 1
                    continue
                baseline_ready_count += 1
                upload_delta, download_delta = delta
                if upload_delta == 0 and download_delta == 0:
                    continue
                extras = []
                ratio = getattr(current, "ratio", None)
                bonus = getattr(current, "bonus", None)
                if ratio not in (None, ""):
                    extras.append(f"📊 {ratio}")
                if bonus not in (None, ""):
                    extras.append(f"🪙 {self._format_metric_number(bonus)}")
                suffix = "｜" + "｜".join(extras) if extras else ""
                result.append(f"⦁ {site_name}：⬆ {self._format_bytes(upload_delta)} ｜ ⬇ {self._format_bytes(download_delta)}{suffix}")
            if stale_count:
                latest_day = max(stale_days) if stale_days else "未知日期"
                if result:
                    result.append(f"⦁ 另 {stale_count} 个站点快照过期（最新 {latest_day}），未计入今日增量")
                elif not eligible_count:
                    return [f"⦁ 站点快照过期（最新 {latest_day}），等待今日站点数据刷新"]
            if result:
                return result
            if eligible_count and baseline_missing_count and not baseline_ready_count:
                return ["⦁ 暂无增量（基线不足）"]
            return ["⦁ 无"]
        except Exception as e:
            return [f"⦁ 异常 - {e}"]
    def _site_increment_snapshot(self) -> Dict[str, Any]:
        """站点上传/下载增量快照，优先今日；今日未生成时回退到最近有效快照。"""
        result = {"date": self._today_prefix(), "basis": "today", "sites": [], "upload_total": 0, "download_total": 0,
                  "baseline_ready": False, "baseline_missing": 0, "latest_date": "", "stale": False,
                  "stale_count": 0, "error_count": 0, "data_valid": False,
                  "active_count": 0, "visible_count": 0}
        try:
            from app.db.site_oper import SiteOper
            site_oper = SiteOper()
            latest_data = site_oper.get_userdata_latest() or []
            active_domains = {s.domain for s in (site_oper.list_active() or []) if getattr(s, "domain", None)}
            latest_data = [d for d in latest_data if d]
            active_latest = [d for d in latest_data if getattr(d, "domain", None) in active_domains] if active_domains else list(latest_data)
            if not active_latest and latest_data:
                active_latest = list(latest_data)
            result["active_count"] = len(active_domains) if active_domains else len(latest_data)
            result["visible_count"] = len(active_latest)
            today = self._today_prefix()
            error_count = len([d for d in active_latest if str(getattr(d, "err_msg", None) or "").strip()])
            valid_latest = [d for d in active_latest if not str(getattr(d, "err_msg", None) or "").strip()]
            all_days = sorted({self._normalize_day(getattr(d, "updated_day", None)) for d in active_latest if self._normalize_day(getattr(d, "updated_day", None))}, reverse=True)
            latest_day = all_days[0] if all_days else ""
            result["latest_date"] = latest_day
            result["error_count"] = error_count
            result["stale_count"] = len([d for d in active_latest if self._normalize_day(getattr(d, "updated_day", None)) not in ("", today)])
            result["stale"] = bool(latest_day and latest_day != today)
            result["data_valid"] = bool(active_latest) and error_count == 0 and result["stale_count"] == 0
            days = sorted({self._normalize_day(getattr(d, "updated_day", None)) for d in valid_latest if self._normalize_day(getattr(d, "updated_day", None))}, reverse=True)
            basis_day = today if any(day == today for day in days) else (days[0] if days else today)
            result["date"] = basis_day
            result["basis"] = "today" if basis_day == today else "latest"
            if result["basis"] == "latest":
                result["stale"] = True
            if not valid_latest:
                return result
            previous_cache: Dict[str, List[Any]] = {}
            out: List[Dict[str, Any]] = []
            baseline_ready_count = 0
            baseline_missing_count = 0
            for current in valid_latest:
                name = getattr(current, "name", None) or getattr(current, "domain", None) or "未知站点"
                domain = getattr(current, "domain", None)
                if self._normalize_day(getattr(current, "updated_day", None)) != basis_day:
                    continue
                delta = None
                try:
                    base_dt = datetime.strptime(basis_day, "%Y-%m-%d")
                except Exception:
                    base_dt = datetime.strptime(today, "%Y-%m-%d")
                for i in range(1, 8):
                    prev_day = (base_dt - timedelta(days=i)).strftime("%Y-%m-%d")
                    if prev_day not in previous_cache:
                        previous_cache[prev_day] = site_oper.get_userdata_by_date(prev_day) or []
                    previous = self._find_site_userdata_snapshot(previous_cache[prev_day], name, domain)
                    if previous:
                        delta = self._site_userdata_delta(current, previous)
                    if delta is not None:
                        break
                if delta is None:
                    baseline_missing_count += 1
                    continue
                baseline_ready_count += 1
                up, dl = delta
                if up == 0 and dl == 0:
                    continue
                out.append({"name": name, "upload": up, "download": dl})
            result["sites"] = out
            result["upload_total"] = sum(int(d.get("upload", 0)) for d in out)
            result["download_total"] = sum(int(d.get("download", 0)) for d in out)
            result["baseline_ready"] = bool(baseline_ready_count)
            result["baseline_missing"] = baseline_missing_count
        except Exception as err:
            logger.warning(f"Signal 站点增量数据获取失败：{err}")
        return result
    def _site_increment_data(self) -> List[Dict[str, Any]]:
        """今日各站点上传/下载增量（原始字节），供旧调用兼容。"""
        return list((self._site_increment_snapshot().get("sites") or []))
    def _get_site_health_locked(self) -> List[str]:
        try:
            from app.db.site_oper import SiteOper
            site_oper = SiteOper()
            latest = site_oper.get_userdata_latest() or []
            active_domains = {site.domain for site in (site_oper.list_active() or []) if getattr(site, "domain", None)}
            latest = [row for row in latest if row and getattr(row, "domain", None) in active_domains] if active_domains else [row for row in latest if row]
            if not latest:
                latest = [row for row in (site_oper.get_userdata_latest() or []) if row]
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
            from app.helper.downloader import DownloaderHelper
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
            from app.db.systemconfig_oper import SystemConfigOper
            from app.schemas.types import SystemConfigKey
            from app.helper.directory import DirectoryHelper

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
        from app.core.config import settings

        config_path = str(self._settings_value(settings, "CONFIG_PATH", "config_path", default="/config"))
        targets = [("配置目录", config_path, "local"), ("插件目录", str(Path(__file__).resolve().parent), "local")]
        try:
            from app.helper.directory import DirectoryHelper
            helper = DirectoryHelper()
            for d in helper.get_download_dirs() or []:
                targets.append(("下载目录", getattr(d, "download_path", None) or getattr(d, "path", None), getattr(d, "storage", None)))
            for d in helper.get_library_dirs() or []:
                targets.append(("媒体库目录", getattr(d, "library_path", None) or getattr(d, "path", None), getattr(d, "library_storage", None) or getattr(d, "storage", None)))
        except Exception:
            pass
        return self._dedupe_directory_entries(targets)
    def _health_directory_targets(self) -> List[Tuple[str, str]]:
        return [(label, path) for label, path, _ in self._health_directory_entries()]
    def _check_storage(self) -> Dict[str, Any]:
        """按 MoviePilot 配置的存储、下载目录与媒体库目录检查容量。"""
        try:
            from app.core.config import settings
            selected = set(self._health_check_storage_targets or ["storages", "config", "download", "library"])
            details = []
            ok = True

            def add_usage(label: str, path: str, storage: Any = "local"):
                nonlocal ok
                if not path:
                    return
                if not self._is_local_storage(storage):
                    details.append(f"{label} {storage} 由存储服务管理")
                    return
                try:
                    stat = shutil.disk_usage(path)
                    item_ok, detail = self._storage_usage_detail(label, stat.total, stat.used, stat.free)
                    ok = ok and item_ok
                    details.append(detail)
                except FileNotFoundError:
                    ok = False
                    details.append(f"{label} 不存在 {path}")
                except PermissionError:
                    ok = False
                    details.append(f"{label} 无权限 {path}")

            if "config" in selected:
                add_usage("配置目录", str(self._settings_value(settings, "CONFIG_PATH", "config_path", default="/config")))

            if selected.intersection({"download", "library"}):
                try:
                    for label, path, storage in self._health_directory_entries():
                        if label.startswith("下载目录") and "download" in selected:
                            add_usage(label, path, storage)
                        if label.startswith("媒体库目录") and "library" in selected:
                            add_usage(label, path, storage)
                except Exception as err:
                    ok = False
                    details.append(f"目录配置异常 {str(err)[:50]}")

            if "storages" in selected:
                try:
                    from app.db.systemconfig_oper import SystemConfigOper
                    from app.schemas.types import SystemConfigKey
                    from app.chain.storage import StorageChain
                    storages = SystemConfigOper().get(SystemConfigKey.Storages) or []
                    sc = StorageChain()
                    for s in storages:
                        name = s.get("name") or s.get("type") or "存储"
                        usage = sc.storage_usage(s.get("type") or "local")
                        if not usage:
                            continue
                        total = usage.get("total") if isinstance(usage, dict) else getattr(usage, "total", None)
                        used = usage.get("used") if isinstance(usage, dict) else getattr(usage, "used", None)
                        free = (usage.get("available") or usage.get("free")) if isinstance(usage, dict) else (getattr(usage, "available", None) or getattr(usage, "free", None))
                        item_ok, detail = self._storage_usage_detail(name, total, used, free)
                        ok = ok and item_ok
                        details.append(detail)
                except Exception:
                    pass

            if not details:
                add_usage("配置目录", str(self._settings_value(settings, "CONFIG_PATH", "config_path", default="/config")))
            return {"name": "storage", "ok": ok, "detail": "；".join(details[:6]) if details else "未检测到可检查的存储"}
        except Exception as err:
            return {"name": "storage", "ok": False, "detail": f"存储检查异常：{str(err)[:100]}"}
    def _build_health_summary(self, persist: bool = True) -> Dict[str, Any]:
        checks = []
        try:
            from app.db.subscribe_oper import SubscribeOper
            count = len(SubscribeOper().list() or [])
            checks.append({"name": "subscribe", "ok": True, "detail": f"订阅 {count} 个"})
        except Exception as err:
            checks.append({"name": "subscribe", "ok": False, "detail": str(err)[:120]})
        try:
            from app.db.site_oper import SiteOper
            sites = SiteOper().list() or []
            active = SiteOper().list_active() or []
            checks.append({"name": "sites", "ok": True, "detail": f"共 {len(sites)} 个，启用 {len(active)} 个"})
        except Exception as err:
            checks.append({"name": "sites", "ok": False, "detail": str(err)[:120]})
        try:
            from app.helper.downloader import DownloaderHelper
            downloader_helper = DownloaderHelper()
            services = downloader_helper.get_services()
            checks.append({"name": "downloaders", "ok": True, "detail": f"在线 {len(services)} 个"})
        except Exception as err:
            checks.append({"name": "downloaders", "ok": False, "detail": str(err)[:120]})
        try:
            services = self.get_service() or []
            checks.append({"name": "signal_services", "ok": True, "detail": f"已调度 {len(services)} 个"})
        except Exception as err:
            checks.append({"name": "signal_services", "ok": False, "detail": str(err)[:120]})
        selected_items = set(self._health_check_items or ["数据库", "存储空间", "目录权限"])
        if "数据库" in selected_items:
            checks.append(self._check_database())
        if "存储空间" in selected_items:
            checks.append(self._check_storage())
        if "目录权限" in selected_items:
            checks.append(self._check_directory())
        success = all(x["ok"] for x in checks)
        result = {"success": success, "checks": checks, "total": len(checks), "pass": len([x for x in checks if x["ok"]]), "fail": len([x for x in checks if not x["ok"]])}
        if persist:
            self.save_data("last_health_check", {
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "success": success,
                "checks": checks,
                "total": result["total"],
                "pass": result["pass"],
                "fail": result["fail"],
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
        """日报专用健康摘要：正常项只列名称，异常项才展开关键原因。"""
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
        current_upload = self._site_userdata_number(current, "upload")
        current_download = self._site_userdata_number(current, "download")
        previous_upload = self._site_userdata_number(previous, "upload")
        previous_download = self._site_userdata_number(previous, "download")
        if current_upload is None and current_download is None:
            return None
        if not ((previous_upload is not None and previous_upload > 0) or (previous_download is not None and previous_download > 0)):
            return None
        upload_delta = 0
        download_delta = 0
        if current_upload is not None and previous_upload is not None and previous_upload > 0:
            if current_upload < previous_upload:
                return None
            upload_delta = max(0, current_upload - previous_upload)
        if current_download is not None and previous_download is not None and previous_download > 0:
            if current_download < previous_download:
                return None
            download_delta = max(0, current_download - previous_download)
        return upload_delta, download_delta

    def _downloader_overview_data(self) -> List[Dict[str, Any]]:
        """Return fixed, common downloader activity fields for the Dashboard."""
        out: List[Dict[str, Any]] = []
        try:
            from app.helper.downloader import DownloaderHelper
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
            from app.core.config import settings
            from sqlalchemy import create_engine, text

            db_type = str(self._settings_value(settings, "DB_TYPE", "db_type", default="sqlite")).lower()
            targets = self._health_check_database_targets or ["current"]
            details = []
            for target in targets:
                target = str(target or "current").lower()
                use_type = db_type if target in ("current", "main", "moviepilot") else target
                if use_type in ("postgres", "postgresql"):
                    url_getter = getattr(settings, "DB_POSTGRESQL_URL", None)
                    db_url = url_getter() if callable(url_getter) else self._settings_value(settings, "DB_URL", "db_url")
                    if not db_url:
                        raise RuntimeError("PostgreSQL 连接地址为空")
                    engine = create_engine(db_url, echo=False, pool_pre_ping=True)
                    label = "PostgreSQL 主库"
                else:
                    config_path = Path(str(self._settings_value(settings, "CONFIG_PATH", "config_path", default="/config")))
                    db_file = config_path / "user.db"
                    db_url = f"sqlite:///{db_file.as_posix()}"
                    engine = create_engine(db_url, echo=False, pool_pre_ping=True)
                    label = f"SQLite 主库 {db_file}"
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                details.append(f"{label} 连接正常")
            return {"name": "database", "ok": True, "detail": "；".join(details)}
        except Exception as err:
            return {"name": "database", "ok": False, "detail": f"数据库异常：{str(err)[:100]}"}

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
            import os

            selected = set(self._health_check_directory_targets or ["config", "plugin", "download", "library"])
            wanted = {
                "config": "配置目录",
                "plugin": "插件目录",
                "download": "下载目录",
                "library": "媒体库目录",
            }
            details = []
            ok = True
            for label, path, storage in self._health_directory_entries():
                if not any(label.startswith(wanted[key]) for key in selected if key in wanted):
                    continue
                if not self._is_local_storage(storage):
                    details.append(f"{label} {storage} 由存储服务管理")
                    continue
                if not os.path.exists(path):
                    ok = False
                    details.append(f"{label} 不存在 {path}")
                    continue
                if not os.access(path, os.R_OK | os.W_OK | os.X_OK):
                    ok = False
                    details.append(f"{label} 权限不足 {path}")
                    continue
                details.append(f"{label} 正常")
            return {"name": "directory", "ok": ok, "detail": "；".join(details[:8]) if details else "未选择目录"}
        except Exception as err:
            return {"name": "directory", "ok": False, "detail": f"目录检查异常：{str(err)[:100]}"}

    def _get_health_report_locked(self, persist_missing: bool = True) -> List[str]:
        """日报中的健康巡查栏目：优先使用最近巡查结果，没有记录时现场生成一次。"""
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
