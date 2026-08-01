"""Downloader helper workflows for tags, seeding and bounded cleanup."""

import os
import re
import hashlib
import json
from typing import Any, Dict, List, Optional, Tuple

from app.log import logger


class DownloaderHelperMixin:
    """Unified downloader helper workflow shared by the plugin API and events."""

    def _dltag_tracker_rules(self) -> List[Tuple[str, str]]:
        rules: List[Tuple[str, str]] = []
        for line in str(getattr(self, "_dltag_tracker_mappings", "") or "").splitlines():
            text = line.strip()
            if not text or text.startswith("#"):
                continue
            separator = "=>" if "=>" in text else "="
            if separator not in text:
                continue
            pattern, tag = (part.strip() for part in text.split(separator, 1))
            if pattern and tag:
                rules.append((pattern, tag))
        return rules

    @staticmethod
    def _dltag_value(source: Any, *names: str) -> Any:
        for name in names:
            value = source.get(name) if isinstance(source, dict) else getattr(source, name, None)
            if value not in (None, ""):
                return value
        return None

    @staticmethod
    def _dltag_list(value: Any) -> List[str]:
        if isinstance(value, (list, tuple, set)):
            return [str(item).strip() for item in value if str(item).strip()]
        return [item.strip() for item in str(value or "").split(",") if item.strip()]

    def _dltag_event_site(self, event_context: Optional[Dict[str, Any]], torrent_id: str) -> str:
        data = dict(event_context or {})
        context = data.get("context")
        torrent_info = data.get("torrent_info") or self._dltag_value(context, "torrent_info")
        source_file = data.get("source_file") or self._dltag_value(context, "source_file")
        candidates = [
            data.get("site_name"), data.get("sitename"),
            self._dltag_value(torrent_info, "site_name", "sitename", "site"),
            self._dltag_value(source_file, "site_name", "sitename", "site"),
        ]
        expected = str(torrent_id or "").lower()
        event_hash = str(data.get("hash") or data.get("download_hash") or data.get("torrent_hash") or "").lower()
        if expected and event_hash and expected != event_hash:
            return ""
        for value in candidates:
            text = str(value or "").strip()
            if text and not text.isdigit():
                return text
        return ""

    def _dltag_site(self, torrent: Any, is_qb: bool, event_context: Optional[Dict[str, Any]] = None) -> str:
        from app.utils.string import StringUtils

        torrent_id = str(self._dltag_value(torrent, "hash", "hashString", "infohash") or "")
        event_site = self._dltag_event_site(event_context, torrent_id)
        tracker_urls: List[str] = []
        tracker_sites: List[str] = []
        primary = str(self._dltag_value(torrent, "tracker") or "").strip()
        if primary:
            tracker_urls.append(primary)
        for tracker in (self._dltag_value(torrent, "trackers") or []):
            url = str(self._dltag_value(tracker, "announce", "url", "tracker") or "").strip()
            site = str(self._dltag_value(tracker, "sitename", "site_name", "name") or "").strip()
            if url:
                tracker_urls.append(url)
            if site:
                tracker_sites.append(site)
        mapped = ""
        for pattern, tag in self._dltag_tracker_rules():
            try:
                if any(re.search(pattern, url, re.I) for url in tracker_urls):
                    mapped = tag
                    break
            except re.error:
                if any(pattern.lower() in url.lower() for url in tracker_urls):
                    mapped = tag
                    break
        tracker_domain = ""
        for url in tracker_urls:
            tracker_domain = StringUtils.get_url_sld(url) or ""
            if tracker_domain:
                break
        # Stable source -> known Tracker site -> explicit mapping -> domain fallback.
        order = [event_site, *tracker_sites, mapped, tracker_domain]
        return next((str(value).strip() for value in order if str(value or "").strip()), "")

    def _dltag_task_set(self, override: Optional[List[str]] = None) -> set:
        values = override if override is not None else getattr(self, "_dltag_tasks", ["tagging", "seeding", "cleanup"])
        return {str(value).strip().lower() for value in (values or []) if str(value).strip()}

    @staticmethod
    def _dltag_torrent_id(torrent: Any) -> str:
        return str(DownloaderHelperMixin._dltag_value(torrent, "hash", "hashString", "infohash", "infohash_v1") or "").strip()

    def _dltag_existing_tags(self, torrent: Any, is_qb: bool) -> List[str]:
        return self._dltag_list(self._dltag_value(torrent, "tags") if is_qb else self._dltag_value(torrent, "labels", "tags"))

    def _dltag_is_private(self, inst: Any, torrent: Any, is_qb: bool) -> bool:
        explicit = self._dltag_value(torrent, "isPrivate", "is_private", "private")
        if explicit is not None:
            return bool(explicit)
        if not is_qb:
            return bool(self._dltag_value(torrent, "tracker") or self._dltag_value(torrent, "trackers"))
        trackers = self._dltag_value(torrent, "trackers") or []
        if trackers and any(bool(self._dltag_value(item, "private", "is_private")) for item in trackers):
            return True
        try:
            qbc = getattr(inst, "qbc", None)
            rows = qbc.torrents_trackers(torrent_hash=self._dltag_torrent_id(torrent)) if qbc else []
            private_markers = {"** [DHT] **", "** [PeX] **", "** [LSD] **"}
            return any(
                bool(self._dltag_value(row, "private", "is_private"))
                or (str(self._dltag_value(row, "url") or "") in private_markers and self._dltag_value(row, "status") == 0)
                for row in (rows or [])
            )
        except Exception:
            return bool(trackers or self._dltag_value(torrent, "tracker"))

    def _dltag_site_for_torrent(self, inst: Any, torrent: Any, is_qb: bool, event_context: Optional[Dict[str, Any]]) -> str:
        if not self._dltag_is_private(inst, torrent, is_qb):
            return ""
        return self._dltag_site(torrent, is_qb, event_context=event_context)

    def _dltag_all_selected(self, torrent: Any, is_qb: bool) -> bool:
        selected = self._dltag_value(torrent, "selected_size", "size_when_done", "sizeWhenDone")
        total = self._dltag_value(torrent, "size", "total_size", "totalSize")
        if selected is not None and total is not None:
            try:
                return float(selected) >= float(total)
            except (TypeError, ValueError):
                pass
        if is_qb:
            return self._dltag_value(torrent, "availability") == -1
        return True

    def _dltag_desired_tags(self, inst: Any, torrent: Any, is_qb: bool, event_context: Optional[Dict[str, Any]]) -> List[str]:
        private = self._dltag_is_private(inst, torrent, is_qb)
        desired = ["PT" if private else "BT"]
        site = self._dltag_site_for_torrent(inst, torrent, is_qb, event_context)
        if site:
            desired.append(f"{getattr(self, '_dltag_prefix', '') or ''}{site}")
        desired.extend(self._dltag_list(getattr(self, "_dltag_all_tags", [])))
        incomplete = str(getattr(self, "_dltag_not_select_all_tag", "非全") or "非全").strip()
        if incomplete and not self._dltag_all_selected(torrent, is_qb):
            desired.append(incomplete)
        return list(dict.fromkeys(tag for tag in desired if tag))

    def _dltag_apply_tags(self, inst: Any, torrent: Any, is_qb: bool, desired: List[str]) -> bool:
        torrent_id = self._dltag_torrent_id(torrent)
        existing = self._dltag_existing_tags(torrent, is_qb)
        managed_prefix = str(getattr(self, "_dltag_prefix", "") or "")
        managed = {"BT", "PT", str(getattr(self, "_dltag_not_select_all_tag", "非全") or "非全")}
        if managed_prefix:
            managed.update(tag for tag in existing if tag.startswith(managed_prefix))
        final = list(dict.fromkeys([tag for tag in existing if tag not in managed] + desired))
        if final == existing:
            return False
        if is_qb:
            remove = [tag for tag in existing if tag not in final]
            remover = getattr(inst, "remove_torrents_tag", None)
            if remove and callable(remover):
                remover(ids=[torrent_id], tags=remove)
            elif remove and callable(getattr(torrent, "remove_tags", None)):
                torrent.remove_tags(tags=remove)
            adder = getattr(inst, "set_torrents_tag", None)
            add = [tag for tag in final if tag not in existing]
            if add and callable(adder):
                adder(ids=[torrent_id], tags=add)
            if hasattr(torrent, "tags"):
                torrent.tags = ",".join(final)
            return True
        setter = getattr(inst, "set_torrent_tag", None)
        if not callable(setter):
            return False
        try:
            setter(torrent_id, final)
        except TypeError:
            setter(ids=torrent_id, tags=final, org_tags=[])
        if hasattr(torrent, "labels"):
            torrent.labels = final
        return True

    def _dltag_is_complete(self, torrent: Any, is_qb: bool) -> bool:
        progress = self._dltag_value(torrent, "progress")
        if progress is not None:
            try:
                return float(progress) >= (1 if float(progress) <= 1 else 100)
            except (TypeError, ValueError):
                pass
        state = str(self._dltag_value(torrent, "state", "status") or "").lower()
        return state in {"complete", "completed", "seeding", "pausedup", "paused_up", "stopped"}

    def _dltag_resume(self, inst: Any, torrent: Any, is_qb: bool) -> bool:
        if not self._dltag_is_complete(torrent, is_qb):
            return False
        state = str(self._dltag_value(torrent, "state", "status") or "").lower()
        if is_qb:
            paused = bool(self._dltag_value(torrent, "paused")) or state in {"pausedup", "paused_up", "paused", "stopped"}
            if not paused:
                return False
            for method in ("resume_torrents", "start_torrents"):
                fn = getattr(inst, method, None)
                if callable(fn):
                    fn(ids=[self._dltag_torrent_id(torrent)])
                    return True
            fn = getattr(torrent, "resume", None)
            if callable(fn):
                fn()
                return True
            return False
        stopped = bool(self._dltag_value(torrent, "stopped")) or state in {"stopped", "paused"}
        if self._dltag_value(torrent, "error", "error_string") not in (None, 0, "", False):
            return False
        fn = getattr(inst, "start_torrents", None)
        if stopped and callable(fn):
            fn(ids=self._dltag_torrent_id(torrent))
            return True
        return False

    def _dltag_path_match(self, torrent: Any, event_context: Dict[str, Any]) -> Tuple[bool, str]:
        source = str((event_context or {}).get("source_file_path") or "").strip()
        name = str(self._dltag_value(torrent, "name", "title") or "").strip()
        if not source or not name:
            return False, ""
        source_norm = source.replace("\\", "/").rstrip("/")
        name_norm = name.replace("\\", "/").strip("/")
        if source_norm.rsplit("/", 1)[-1] == name_norm:
            return True, source
        parent = source_norm.rsplit("/", 2)[-2] if "/" in source_norm else ""
        if parent == name_norm:
            return True, source_norm.rsplit("/", 1)[0]
        marker = f"/{name_norm}/"
        if marker in f"{source_norm}/":
            return True, source_norm.split(marker, 1)[0] + "/" + name_norm
        return False, ""

    def _dltag_cleanup_reason(self, torrent: Any, is_qb: bool, event_context: Optional[Dict[str, Any]]) -> Optional[Tuple[str, bool]]:
        if not self._dltag_is_complete(torrent, is_qb):
            return None
        state = str(self._dltag_value(torrent, "state") or "")
        error_text = str(self._dltag_value(torrent, "error_string", "error") or "")
        if (is_qb and state.lower() == "missingfiles") or (not is_qb and "no data found" in error_text.lower()):
            return "失效下载任务", False
        context = event_context or {}
        if context.get("source_file_path"):
            matched, data_path = self._dltag_path_match(torrent, context)
            if matched:
                strategy = str(getattr(self, "_dltag_source_delete_strategy", "delayed") or "delayed").lower()
                if strategy == "early" or not os.path.exists(data_path):
                    return "源文件删除事件", not (strategy == "early")
        deleted = context.get("deleted_torrent") or {}
        if deleted:
            name = str(self._dltag_value(torrent, "name", "title") or "")
            size = self._dltag_value(torrent, "size", "total_size", "totalSize")
            if name and name == str(self._dltag_value(deleted, "title", "name") or "") and str(size) == str(self._dltag_value(deleted, "size", "total_size", "totalSize") or ""):
                return "下载任务删除事件", True
        return None

    def _dltag_services(self):
        from app.helper.downloader import DownloaderHelper
        helper = DownloaderHelper()
        names = getattr(self, "_dltag_downloaders", None) or [getattr(c, "name", None) for c in (helper.get_configs() or {}).values() if getattr(c, "name", None)]
        return helper.get_services(name_filters=names) or {}

    def _dltag_collect_candidates(self, event_context: Optional[Dict[str, Any]] = None, target_hashes: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        targets = {str(value).strip().lower() for value in (target_hashes or []) if str(value).strip()}
        protected = {tag.lower() for tag in self._dltag_list(getattr(self, "_dltag_excluded_tags", []))}
        out: List[Dict[str, Any]] = []
        for name, service in self._dltag_services().items():
            inst = getattr(service, "instance", None)
            dtype = str(getattr(getattr(service, "config", None), "type", "") or "").lower()
            if not inst or dtype not in {"qbittorrent", "transmission"}:
                continue
            try:
                torrents, error = inst.get_torrents()
            except Exception as err:
                out.append({"downloader": name, "items": [], "error": str(err)})
                continue
            if error:
                out.append({"downloader": name, "items": [], "error": str(error)})
                continue
            for torrent in torrents or []:
                torrent_id = self._dltag_torrent_id(torrent)
                if not torrent_id or (targets and torrent_id.lower() not in targets):
                    continue
                tags = self._dltag_existing_tags(torrent, dtype == "qbittorrent")
                if protected.intersection(tag.lower() for tag in tags):
                    continue
                reason = self._dltag_cleanup_reason(torrent, dtype == "qbittorrent", event_context)
                if reason:
                    out.append({"downloader": name, "id": torrent_id, "name": self._dltag_value(torrent, "name", "title") or torrent_id, "reason": reason[0], "delete_file": reason[1]})
        return out

    def downloader_helper_preview(self, event_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        items = self._dltag_collect_candidates(event_context=event_context)
        raw = json.dumps([{key: item.get(key) for key in ("downloader", "id", "reason", "delete_file")} for item in items], ensure_ascii=False, sort_keys=True)
        return {"total": len(items), "items": items, "scope_token": hashlib.sha256(raw.encode("utf-8")).hexdigest()}

    def run_downloader_helper(self, target_hashes: Optional[List[str]] = None, event_context: Optional[Dict[str, Any]] = None, trigger: str = "manual", confirmed_candidates: Optional[List[Dict[str, Any]]] = None, task_override: Optional[List[str]] = None) -> bool:
        name = "下载器助手"
        ok, _ = self._guard_task(name, "dltag")
        if not ok:
            return False
        tasks = self._dltag_task_set(task_override)
        counts = {"tagged": 0, "seeded": 0, "cleaned": 0, "failed": 0, "total": 0}
        cleanup_scope_is_confirmed = confirmed_candidates is not None
        selected = {(str(item.get("downloader")), str(item.get("id"))) for item in (confirmed_candidates or [])}
        try:
            for downloader, service in self._dltag_services().items():
                inst = getattr(service, "instance", None)
                dtype = str(getattr(getattr(service, "config", None), "type", "") or "").lower()
                if not inst or dtype not in {"qbittorrent", "transmission"}:
                    continue
                try:
                    torrents, error = inst.get_torrents()
                    if error:
                        raise RuntimeError(str(error))
                    is_qb = dtype == "qbittorrent"
                    for torrent in torrents or []:
                        torrent_id = self._dltag_torrent_id(torrent)
                        if not torrent_id or (target_hashes and torrent_id.lower() not in {str(v).lower() for v in target_hashes}):
                            continue
                        counts["total"] += 1
                        tags = self._dltag_existing_tags(torrent, is_qb)
                        protected = {tag.lower() for tag in self._dltag_list(getattr(self, "_dltag_excluded_tags", []))}
                        if "tagging" in tasks and self._dltag_apply_tags(inst, torrent, is_qb, self._dltag_desired_tags(inst, torrent, is_qb, event_context)):
                            counts["tagged"] += 1
                        if "seeding" in tasks and not protected.intersection(tag.lower() for tag in tags) and self._dltag_resume(inst, torrent, is_qb):
                            counts["seeded"] += 1
                        if "cleanup" in tasks and not protected.intersection(tag.lower() for tag in tags):
                            reason = self._dltag_cleanup_reason(torrent, is_qb, event_context)
                            if reason and (not cleanup_scope_is_confirmed or (str(downloader), torrent_id) in selected):
                                inst.delete_torrents(delete_file=reason[1], ids=[torrent_id])
                                counts["cleaned"] += 1
                except Exception as err:
                    counts["failed"] += 1
                    logger.warning(f"下载器助手处理 {downloader} 失败，已继续其它下载器：{err}")
            success = counts["failed"] == 0
            text = f"下载器助手完成：处理 {counts['total']} 个任务，标签 {counts['tagged']}，做种 {counts['seeded']}，清理 {counts['cleaned']}"
            if counts["failed"]:
                text += f"，失败 {counts['failed']} 个下载器"
            self._save_task_result(name, success, 0 if success else 1, text)
            if trigger == "scheduled" and getattr(self, "_dltag_scheduled_notify", False):
                self._notify_fusion_task_outcome(mtype=self._notification_type(self._dltag_notify_type), title=name, text=text, outcome=text, success=success, component="downloader_helper")
            return success
        except Exception as err:
            self._save_task_result(name, False, -1, str(err))
            logger.error(f"Signal 下载器助手失败：{err}")
            return False

    def run_downloader_helper_scheduled(self) -> bool:
        return self.run_downloader_helper(trigger="scheduled")
