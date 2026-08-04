import json
import re
from datetime import datetime
from typing import Any, Dict, List

from app.core.event import Event
from app.log import logger
from app.schemas import NotificationType


def _split_subfill_fields(line: str) -> List[str]:
    """按未转义的井号切分规则字段，同时保留其他反斜杠。"""
    fields: List[str] = []
    value: List[str] = []
    index = 0
    while index < len(line):
        character = line[index]
        if character == "\\" and index + 1 < len(line) and line[index + 1] == "#":
            value.append("#")
            index += 2
            continue
        if character == "#":
            fields.append("".join(value))
            value = []
        else:
            value.append(character)
        index += 1
    fields.append("".join(value))
    return fields


class EventsMixin:
    """MoviePilot event and remote-command entrypoints."""

    def handle_command(self, event: Event = None):
        if not event:
            return
        if self._event_should_noop_after_stop():
            return
        action = (event.event_data or {}).get("action", "")
        handlers = {
            "signal_report": [("每日汇报", self.run_daily_report, "daily_report")],
            "signal_subscribe": [("订阅追新", self.run_subscribe_reminder, "subscribe_reminder")],
            "signal_report_preview": [("预览每日汇报", self.run_daily_report_preview, "daily_report")],
            "signal_health": [("健康巡查", self.run_health_check, "health_check")],
            "signal_logs": [("日志清理预览", self.run_log_preview, "log_clean")],
            "signal_logs_clean": [("日志清理", self.run_log_clean, "log_clean")],
            "signal_backup": [("自动备份", self.run_backup, "backup")],
            "signal_updates": [("主程序更新检查", self.run_mp_update_check, "mp_update")],
            "signal_market": [("插件库更新", self.run_market_update, "market_update")],
            "signal_run_all": [("每日汇报", self.run_daily_report, "daily_report"), ("健康巡查", self.run_health_check, "health_check")],
            "signal_plugin_preview": [("插件卸载预览", self.run_plugin_uninstall_preview, None)],
            "signal_plugin_clean": [("插件卸载", self.run_plugin_uninstall_confirm_required, None)],
            "signal_seed_clean": [("自动删种", self.run_seed_clean, "seed_clean")],
        }
        tasks = handlers.get(action)
        if not tasks:
            return
        ok, _ = self._runtime_gate("command", name=action)
        if not ok:
            return
        quiet_success_actions = {"signal_updates"}
        results = []
        has_failed_task = False
        task_sent_message = False
        original_post_message = self.post_message
        original_emit_console_notice = self._emit_console_notice
        had_instance_post_message = "post_message" in getattr(self, "__dict__", {})
        had_instance_emit_console_notice = "_emit_console_notice" in getattr(self, "__dict__", {})

        def tracked_post_message(*args, **kwargs):
            nonlocal task_sent_message
            task_sent_message = True
            return original_post_message(*args, **kwargs)

        def tracked_emit_console_notice(*args, **kwargs):
            nonlocal task_sent_message
            ok = original_emit_console_notice(*args, **kwargs)
            if ok:
                task_sent_message = True
            return ok

        try:
            # 远程命令只在任务本身没有发业务通知时补发结果，避免用户收到两条近似消息。
            self.post_message = tracked_post_message
            self._emit_console_notice = tracked_emit_console_notice
            for name, runner, component in tasks:
                ok, _ = self._runtime_gate("command", component=component, name=name)
                if not ok:
                    continue
                ok = bool(runner())
                has_failed_task = has_failed_task or not ok
                results.append(f"{name}：{'成功' if ok else '失败'}")
        finally:
            if had_instance_emit_console_notice:
                self._emit_console_notice = original_emit_console_notice
            else:
                try:
                    delattr(self, "_emit_console_notice")
                except AttributeError:
                    pass
            if had_instance_post_message:
                self.post_message = original_post_message
            else:
                try:
                    delattr(self, "post_message")
                except AttributeError:
                    pass
        if results and not self._fusion_notify_enabled and (has_failed_task or (not task_sent_message and action not in quiet_success_actions)):
            self._notify_or_console(mtype=NotificationType.Plugin, title="MP 运维助手命令执行结果", text="\n".join(results))

    def on_message_action(self, event: Event = None):
        """接收 MoviePilot 通知渠道转发的 `[PLUGIN]Signal|...` 按钮回调。"""
        if self._event_should_noop_after_stop():
            return
        ok, _ = self._runtime_gate("event", component="fusion_notify", name="MessageAction")
        if not ok:
            return
        info = getattr(event, "event_data", None) if event else None
        if not isinstance(info, dict):
            return
        plugin_id = str(info.get("plugin_id") or "").strip()
        if plugin_id.lower() not in {self.__class__.__name__.lower(), "signal"}:
            return
        data = str(info.get("text") or "").strip()
        if not data:
            return
        token, chat_id, _source = self._resolve_daily_report_telegram_config()
        if not token or not chat_id:
            return
        callback = {
            "id": "",
            "from": {"id": str(info.get("userid") or "")},
            "message": {"chat": {"id": chat_id}},
            "data": data,
        }
        self._handle_tg_console_callback(callback)

    def on_download_fill_subscribe(self, event: Event = None):
        """下载添加后，用实际下载到的资源回填对应电视剧订阅的空规则（移植自 thsrite SubscribeGroup 下载填充）。
        仅填充订阅中尚为空的字段，已设置的不覆盖；按 tmdbid 去重，仅处理一次。"""
        if self._event_should_noop_after_stop():
            return
        ok, _ = self._runtime_gate("event", component="subfill", name="DownloadAdded")
        if not ok:
            return
        if not self._subfill_enabled or not self._subfill_details:
            return
        if not event or not getattr(event, "event_data", None):
            return
        data = event.event_data or {}
        dhash, context = data.get("hash"), data.get("context")
        if not dhash or not context:
            return
        try:
            from app.db.downloadhistory_oper import DownloadHistoryOper
            from app.db.subscribe_oper import SubscribeOper
        except Exception as err:
            logger.warning(f"Signal 订阅填充加载依赖失败：{err}")
            return
        try:
            dh = DownloadHistoryOper().get_by_hash(dhash)
            if not dh or str(getattr(dh, "type", "")) != "电视剧":
                return
            handled = self.get_data("subfill_handled") or []
            key = f"{getattr(dh, 'type', '')}:{getattr(dh, 'tmdbid', '')}"
            if key in handled:
                return
            seasons = getattr(dh, "seasons", "") or ""
            season = int(seasons.replace("S", "")) if seasons and seasons.count("-") == 0 else None
            subs = SubscribeOper().list_by_tmdbid(tmdbid=dh.tmdbid, season=season) or []
            meta = getattr(context, "meta_info", None)
            torrent = getattr(context, "torrent_info", None)
            filled = []
            for sub in subs:
                if str(getattr(sub, "type", "")) != "电视剧":
                    continue
                upd = self._subfill_build_update(sub, meta, torrent)
                if not upd:
                    continue
                SubscribeOper().update(sub.id, upd)
                filled.append({"name": getattr(sub, "name", ""), "update": upd})
                self._subfill_log(getattr(sub, "name", ""), "下载填充", upd)
            if filled:
                handled.append(key)
                self.save_data("subfill_handled", handled)
                text = self._format_subfill(filled)
                self._save_task_result("订阅规则填充", True, 0, text)
        except Exception as err:
            logger.error(f"Signal 订阅规则填充失败：{err}")

    def _subfill_build_update(self, sub: Any, meta: Any, torrent: Any) -> Dict[str, Any]:
        """根据已下载资源的 meta/torrent，构造订阅“空字段”的回填字典（仅填空，不覆盖）。"""
        details = self._subfill_details or []
        upd: Dict[str, Any] = {}
        if "分辨率" in details and not getattr(sub, "resolution", None):
            pix = self._parse_pix(getattr(meta, "resource_pix", None) if meta else None)
            if pix:
                upd["resolution"] = pix
        if "资源质量" in details and not getattr(sub, "quality", None):
            rt = self._parse_type(getattr(meta, "resource_type", None) if meta else None)
            if rt:
                upd["quality"] = rt
        if "特效" in details and not getattr(sub, "effect", None):
            ef = self._parse_effect(getattr(meta, "resource_effect", None) if meta else None)
            if ef:
                upd["effect"] = ef
        if "制作组" in details and not getattr(sub, "include", None):
            team = getattr(meta, "resource_team", None) if meta else None
            cust = getattr(meta, "customization", None) if meta else None
            if team and cust:
                team = f"{cust}.+{team}"
            elif cust and not team:
                team = cust
            if team:
                upd["include"] = team
        if "站点" in details and not getattr(sub, "sites", None):
            try:
                from app.db.systemconfig_oper import SystemConfigOper
                from app.schemas.types import SystemConfigKey
                rss_sites = SystemConfigOper().get(SystemConfigKey.RssSites) or []
                if torrent and getattr(torrent, "site", None) and int(torrent.site) in rss_sites:
                    upd["sites"] = [torrent.site]
            except Exception:
                pass
        return upd

    @staticmethod
    def _format_subfill(filled: List[Dict[str, Any]]) -> str:
        lines = ["🧷 订阅规则自动填充"]
        for it in filled[:8]:
            pairs = "，".join(f"{k}={v}" for k, v in (it.get("update") or {}).items())
            lines.append(f"⦁ {it.get('name')}：{pairs}")
        return "\n".join(lines)

    def _subfill_log(self, name: str, kind: str, update: Dict[str, Any]):
        """记录一条订阅填充历史（供配置页/审计查看，最多留 100 条）。"""
        try:
            hist = self.get_data("subfill_history") or []
            hist.insert(0, {"name": name, "type": kind,
                            "content": json.dumps(update, ensure_ascii=False),
                            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
            self.save_data("subfill_history", hist[:100])
        except Exception:
            pass

    def _parse_subfill_confs(self, text: str) -> Dict[str, Dict[str, Any]]:
        """解析二级分类自定义填充配置文本（移植自 thsrite SubscribeGroup）。
        每行一个分类块，`#` 分隔 `key:value`：
        category:国漫,日番#resolution:1080p#quality:WEB-DL#include:...#exclude:...#sites:馒头,青蛙#savepath:/media/{name}#filter_groups:...
        """
        confs: Dict[str, Dict[str, Any]] = {}
        if not text:
            return confs
        active_sites = []
        try:
            from app.db.site_oper import SiteOper
            active_sites = SiteOper().list_active() or []
        except Exception:
            active_sites = []
        for line in str(text).split("\n"):
            if not line.strip():
                continue
            category = resolution = quality = effect = include = exclude = savepath = None
            sites, filter_groups = [], []
            for conf in _split_subfill_fields(str(line)):
                if ":" not in conf:
                    continue
                k, v = (part.strip() for part in conf.split(":", 1))
                if k == "category":
                    category = v
                elif k == "resolution":
                    resolution = v
                elif k == "quality":
                    quality = v
                elif k == "effect":
                    effect = v
                elif k == "include":
                    include = v
                elif k == "exclude":
                    exclude = v
                elif k == "savepath":
                    savepath = v
                elif k == "sites":
                    for sn in str(v).split(","):
                        for s in active_sites:
                            if str(sn).strip() == str(getattr(s, "name", "")):
                                sites.append(s.id)
                                break
                elif k == "filter_groups":
                    filter_groups = [g for g in str(v).split(",") if g]
            if category:
                for c in str(category).split(","):
                    if c.strip():
                        confs[c.strip()] = {"resolution": resolution, "quality": quality, "effect": effect,
                                            "include": include, "exclude": exclude, "savepath": savepath,
                                            "sites": sites, "filter_groups": filter_groups}
        return confs

    def on_subscribe_added_fill(self, event: Event = None):
        """新增订阅时按媒体二级分类套用自定义规则（移植自 thsrite SubscribeGroup 二级分类填充）。"""
        if self._event_should_noop_after_stop():
            return
        ok, _ = self._runtime_gate("event", component="subfill", name="SubscribeAdded")
        if not ok:
            return
        if not self._subfill_category_enabled or not self._subfill_confs:
            return
        data = getattr(event, "event_data", None) if event else None
        if not data or not data.get("subscribe_id") or not data.get("mediainfo"):
            return
        try:
            from app.db.subscribe_oper import SubscribeOper
        except Exception as err:
            logger.warning(f"Signal 订阅二级分类填充加载依赖失败：{err}")
            return
        try:
            sid = data.get("subscribe_id")
            category = (data.get("mediainfo") or {}).get("category")
            if not category or category not in self._subfill_confs:
                return
            sub = SubscribeOper().get(sid)
            conf = self._subfill_confs.get(category) or {}
            upd: Dict[str, Any] = {}
            if conf.get("include"):
                upd["include"] = conf["include"]
            if conf.get("exclude"):
                upd["exclude"] = conf["exclude"]
            if conf.get("sites"):
                upd["sites"] = conf["sites"]
            if conf.get("filter_groups"):
                upd["filter_groups"] = conf["filter_groups"]
            if conf.get("resolution"):
                upd["resolution"] = self._parse_pix(conf["resolution"])
            if conf.get("quality"):
                upd["quality"] = self._parse_type(conf["quality"])
            if conf.get("effect"):
                upd["effect"] = self._parse_effect(conf["effect"])
            if conf.get("savepath"):
                sp = conf["savepath"]
                if "{name}" in sp and sub:
                    sp = sp.replace("{name}", f"{getattr(sub, 'name', '')} ({getattr(sub, 'year', '')})")
                upd["save_path"] = sp
            if not upd:
                return
            SubscribeOper().update(sid, upd)
            self._subfill_log(getattr(sub, "name", str(sid)), f"二级分类[{category}]", upd)
        except Exception as err:
            logger.error(f"Signal 订阅二级分类填充失败：{err}")

    @staticmethod
    def _parse_pix(resource_pix):
        if not resource_pix:
            return resource_pix
        if re.match(r"1080[pi]|x1080", resource_pix, re.IGNORECASE):
            return "1080[pi]|x1080"
        if re.match(r"4K|2160p|x2160", resource_pix, re.IGNORECASE):
            return "4K|2160p|x2160"
        if re.match(r"720[pi]|x720", resource_pix, re.IGNORECASE):
            return "720[pi]|x720"
        return resource_pix

    @staticmethod
    def _parse_type(resource_type):
        if not resource_type:
            return resource_type
        if re.match(r"Blu-?Ray.+VC-?1|Blu-?Ray.+AVC|UHD.+blu-?ray.+HEVC|MiniBD", resource_type, re.IGNORECASE):
            resource_type = "Blu-?Ray.+VC-?1|Blu-?Ray.+AVC|UHD.+blu-?ray.+HEVC|MiniBD"
        if re.match(r"Remux", resource_type, re.IGNORECASE):
            resource_type = "Remux"
        if re.match(r"Blu-?Ray", resource_type, re.IGNORECASE):
            resource_type = "Blu-?Ray"
        if re.match(r"UHD|UltraHD", resource_type, re.IGNORECASE):
            resource_type = "UHD|UltraHD"
        if re.match(r"WEB-?DL|WEB-?RIP", resource_type, re.IGNORECASE):
            resource_type = "WEB-?DL|WEB-?RIP"
        if re.match(r"HDTV", resource_type, re.IGNORECASE):
            resource_type = "HDTV"
        if re.match(r"[Hx].?265|HEVC", resource_type, re.IGNORECASE):
            resource_type = "[Hx].?265|HEVC"
        if re.match(r"[Hx].?264|AVC", resource_type, re.IGNORECASE):
            resource_type = "[Hx].?264|AVC"
        return resource_type

    @staticmethod
    def _parse_effect(resource_effect):
        if not resource_effect:
            return resource_effect
        if re.match(r"Dolby[\\s.]+Vision|DOVI|[\\s.]+DV[\\s.]+", resource_effect, re.IGNORECASE):
            resource_effect = "Dolby[\\s.]+Vision|DOVI|[\\s.]+DV[\\s.]+"
        if re.match(r"Dolby[\\s.]*\\+?Atmos|Atmos", resource_effect, re.IGNORECASE):
            resource_effect = "Dolby[\\s.]*\\+?Atmos|Atmos"
        if re.match(r"[\\s.]+HDR[\\s.]+|HDR10|HDR10\\+", resource_effect, re.IGNORECASE):
            resource_effect = "[\\s.]+HDR[\\s.]+|HDR10|HDR10\\+"
        if re.match(r"[\\s.]+SDR[\\s.]+", resource_effect, re.IGNORECASE):
            resource_effect = "[\\s.]+SDR[\\s.]+"
        return resource_effect

    def on_webhook_message(self, event: Event = None):
        """媒体库服务器通知（移植自 jxxghp MediaServerMsg 核心）：把 Emby/Jellyfin/Plex 的
        播放/入库/登录等 webhook 事件按配置推送通知。不含原插件的剧集聚合/IP定位/海报抓取。"""
        if self._event_should_noop_after_stop():
            return
        ok, _ = self._runtime_gate("event", name="WebhookMessage")
        if not ok:
            return
        info = getattr(event, "event_data", None) if event else None
        if not info:
            return
        try:
            group = self._msg_group_of(getattr(info, "event", None))
            if not group:
                return
            server_name = getattr(info, "server_name", None)
            server_allowed = not (self._msgnotify_servers and server_name and server_name not in self._msgnotify_servers)
            legacy_notify = bool(self._msgnotify_enabled and self._msgnotify_types and group in self._msgnotify_types and server_allowed)
            fusion_stream = self._fusion_media_event_enabled(group, server_name)
            if not legacy_notify and not fusion_stream:
                return
            item_id = getattr(info, "item_id", "") or ""
            if item_id and not self._msg_dedupe(f"{server_name}-{group}-{item_id}"):
                return
            title = self._msg_title(group, info)
            text = self._msg_text(info)
            image = getattr(info, "image_url", None) or self._webhook_images.get(getattr(info, "channel", "") or "")
            if self._fusion_notify_enabled:
                self._emit_console_media_activity(group, info, title)
                return
            if fusion_stream or (self._tg_console_enabled and self._tg_console_suppress_individual_notifications):
                self._emit_console_media_activity(group, info, title)
            if self._tg_console_enabled and self._tg_console_suppress_individual_notifications:
                return
            if legacy_notify:
                self._post_moviepilot_notification(
                    {
                        "mtype": self._notification_type(self._msgnotify_notify_type, "MediaServer"),
                        "title": title,
                        "text": text,
                        "image": image,
                    },
                    component="msgnotify",
                    title=title,
                )
        except Exception as err:
            logger.error(f"Signal 媒体库通知处理失败：{err}")
