import json
import os
import shutil
import subprocess
import zipfile
import re
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from app.core.config import settings
from app.core.event import Event, eventmanager
from app.log import logger
from app.plugins import _PluginBase
from app.schemas import NotificationType
from app.utils.http import RequestUtils
from app.schemas.types import EventType

# 本地插件源码仓库默认路径。留空表示未配置：
# 「插件卸载」的本地源码清理功能仅在用户显式配置后才会生效，
# 避免对未知系统使用写死的开发期路径执行删除。
DEFAULT_LOCAL_PLUGIN_REPO = ""


class AgentOpsAssistant(_PluginBase):
    """MP 运维助手：每日汇报、日志清理、备份、更新检查和插件卸载。"""

    plugin_name = "MP 运维助手"
    plugin_desc = "面向 MoviePilot 的运维中枢：每日汇报、健康巡查、订阅追新、站点统计、日志清理、备份与更新治理。"
    plugin_icon = "https://raw.githubusercontent.com/clone-fan/MoviePilot-Plugins/main/icons/agentopsassistant.png"
    plugin_version = "1.0.41"
    plugin_author = "wenking"
    author_url = "https://github.com/clone-fan"
    plugin_config_prefix = "agentopsassistant_"
    plugin_order = 50
    auth_level = 1

    MODULES: List[Dict[str, str]] = [
        {"key": "daily_report", "category": "report", "subcategory": "日报编排", "name": "每日汇报", "phase": "v1.4", "risk": "低", "status": "已直接接替", "source": "AgentOpsAssistant", "goal": "固定模板日报与定时/手动发送"},

        {"key": "subscribe_today", "category": "subscribe_center", "subcategory": "今日追新", "name": "今日追新", "phase": "v2.0", "risk": "低", "status": "待接替", "source": "SubscribeReminder + SubscribeOper", "goal": "直接接替订阅追新的今日播出口径"},
        {"key": "subscribe_status", "category": "subscribe_center", "subcategory": "订阅状态", "name": "订阅状态总览", "phase": "v2.0", "risk": "低", "status": "待接替", "source": "SubscribeOper", "goal": "启用、待处理、缺集、今日追新统计"},
        {"key": "subscribe_lack", "category": "subscribe_center", "subcategory": "缺集提醒", "name": "缺集提醒", "phase": "v2.0", "risk": "低", "status": "规划中", "source": "SubscribeOper", "goal": "缺集订阅 Top 列表与提醒"},
        {"key": "subscribe_notify", "category": "subscribe_center", "subcategory": "追新推送", "name": "订阅追新推送", "phase": "v2.0", "risk": "低", "status": "规划中", "source": "AgentOpsAssistant", "goal": "由本插件独立发送订阅追新，原插件可卸载"},

        {"key": "site_snapshot", "category": "site_center", "subcategory": "站点快照", "name": "站点快照", "phase": "v2.1", "risk": "低", "status": "待接替", "source": "SiteStatistic + SiteOper", "goal": "复刻站点统计快照口径"},
        {"key": "site_increment", "category": "site_center", "subcategory": "站点增量", "name": "站点增量", "phase": "v2.1", "risk": "低", "status": "待接替", "source": "SiteStatistic + SiteOper", "goal": "复刻上传/下载/分享率/魔力增量口径"},
        {"key": "site_signin", "category": "site_center", "subcategory": "站点签到", "name": "站点签到", "phase": "v2.2", "risk": "中", "status": "待接替", "source": "AutoSignIn", "goal": "直接接替站点自动签到并记录成功/失败"},
        {"key": "site_auth_health", "category": "site_center", "subcategory": "认证健康", "name": "站点认证健康", "phase": "v2.2", "risk": "低", "status": "规划中", "source": "SiteOper", "goal": "Cookie/认证异常提醒"},

        {"key": "downloader_status", "category": "download_transfer", "subcategory": "下载器状态", "name": "下载器状态", "phase": "v2.3", "risk": "低", "status": "规划中", "source": "Downloader", "goal": "下载器连接正常/异常统计"},
        {"key": "downloading", "category": "download_transfer", "subcategory": "当前下载", "name": "当前下载", "phase": "v1.4", "risk": "低", "status": "已接入", "source": "DownloadChain", "goal": "当前正在下载任务"},
        {"key": "download_done", "category": "download_transfer", "subcategory": "完成统计", "name": "今日完成下载", "phase": "v2.3", "risk": "低", "status": "规划中", "source": "DownloadHistoryOper", "goal": "今日完成下载统计"},
        {"key": "transfer_today", "category": "download_transfer", "subcategory": "今日入库", "name": "今日入库", "phase": "v1.4", "risk": "低", "status": "已接入", "source": "TransferHistoryOper", "goal": "今日转移成功/失败与媒体聚合"},
        {"key": "transfer_failed", "category": "download_transfer", "subcategory": "转移失败", "name": "转移失败提醒", "phase": "v2.3", "risk": "低", "status": "规划中", "source": "TransferHistoryOper", "goal": "失败转移提醒与后续重试入口"},

        {"key": "mediaserver_config", "category": "library_center", "subcategory": "媒体服务器", "name": "媒体服务器配置", "phase": "v2.4", "risk": "低", "status": "规划中", "source": "MediaServers", "goal": "媒体服务器配置状态"},
        {"key": "mediaserver_sync", "category": "library_center", "subcategory": "同步任务", "name": "媒体库同步", "phase": "v2.4", "risk": "低", "status": "规划中", "source": "Scheduler", "goal": "mediaserver_sync 调度状态"},
        {"key": "latest_library", "category": "library_center", "subcategory": "最近入库", "name": "最近入库可见性", "phase": "v2.4", "risk": "低", "status": "规划中", "source": "TransferHistoryOper/MediaServer", "goal": "最近入库与媒体服务器可见性"},

        {"key": "directory_health", "category": "system_storage", "subcategory": "目录配置", "name": "目录健康", "phase": "v2.5", "risk": "低", "status": "规划中", "source": "Directories", "goal": "按 MoviePilot 目录设置检查路径可访问"},
        {"key": "storage_space", "category": "system_storage", "subcategory": "存储空间", "name": "存储空间", "phase": "v2.5", "risk": "低", "status": "规划中", "source": "Directories + disk_usage", "goal": "按设置里的下载/媒体库路径实际汇报"},
        {"key": "database_health", "category": "system_storage", "subcategory": "数据库", "name": "数据库状态", "phase": "v2.5", "risk": "低", "status": "规划中", "source": "DB connection", "goal": "轻量数据库健康检查"},
        {"key": "system_health", "category": "system_storage", "subcategory": "系统基础", "name": "系统基础健康", "phase": "v2.5", "risk": "低", "status": "规划中", "source": "local system", "goal": "基础资源与配置目录健康"},

        {"key": "log_clean", "category": "ops_tools", "subcategory": "日志清理", "name": "日志清理", "phase": "v0.9", "risk": "中", "status": "已直接接替", "source": "/config/logs/plugins", "goal": "扫描插件日志、按保留行数直接清理"},
        {"key": "backup", "category": "ops_tools", "subcategory": "配置备份", "name": "自动备份", "phase": "v1.1", "risk": "中", "status": "已直接接替", "source": "AgentOpsAssistant", "goal": "打包配置/数据库/关键目录、保留策略清理"},
        {"key": "mp_update", "category": "ops_tools", "subcategory": "主程序", "name": "MoviePilot 更新推送", "phase": "v1.2", "risk": "中", "status": "已直接接替", "source": "AgentOpsAssistant", "goal": "检查后端/前端 release 并通知"},
        {"key": "market_update", "category": "ops_tools", "subcategory": "插件库", "name": "插件库更新推送", "phase": "v1.3", "risk": "中", "status": "已直接接替", "source": "AgentOpsAssistant", "goal": "抓取插件库记录、对比当前配置、通知变化"},

        {"key": "plugin_uninstall", "category": "plugin", "subcategory": "插件卸载", "name": "插件卸载", "phase": "v1.4", "risk": "高", "status": "已接入", "source": "AgentOpsAssistant", "goal": "插件卸载、配置/数据清理与残留文件备份删除"},
    ]

    _enabled = False
    _local_plugin_repo = DEFAULT_LOCAL_PLUGIN_REPO
    _daily_report_enabled = True
    _daily_report_cron = "0 22 * * *"
    _daily_report_greeting = "少爷"
    _daily_report_msgtype = "Plugin"
    _health_in_report = True
    _subscribe_in_report = True
    _site_stat_in_report = True
    _report_version = True
    _report_site_status = True
    _report_site_increment = True
    _report_today_download = True
    _report_transfer = True
    _report_subscribe = True
    _report_storage = True
    _report_media_stat = True
    _report_summary = True
    _health_check_enabled: bool = True
    _health_check_cron: str = "0 */6 * * *"
    _health_check_items: List[str] = []
    _health_check_database_targets: List[str] = []
    _health_check_storage_targets: List[str] = []
    _health_check_directory_targets: List[str] = []
    _health_check_storage_threshold: int = 85
    _health_check_notify_type: str = "Plugin"
    _report_health: bool = True
    _log_clean_enabled = False
    _log_clean_cron = "0 3 * * 1"
    _log_clean_rows = 300
    _log_clean_selected_ids: List[str] = []
    _log_clean_notify = True
    _log_clean_notify_type = "Plugin"
    _backup_enabled = False
    _backup_cron = "0 4 * * 1"
    _backup_keep_count = 5
    _backup_path = "/config/plugins/AgentOpsAssistant/Backup"
    _backup_notify = True
    _backup_notify_type = "Plugin"
    _backup_webdav_notify_type = "Plugin"
    _mp_update_enabled = False
    _mp_update_cron = "0 9 * * *"
    _mp_update_notify = True
    _mp_update_notify_type = "Plugin"
    _mp_update_restart_confirm = False
    _mp_update_types: List[str] = ["后端", "前端"]
    _market_update_enabled = False
    _market_update_interval = 86400
    _market_update_notify = True
    _market_update_notify_type = "Plugin"
    _market_update_write_settings = False
    _market_update_write_env = False
    _market_update_blacklist: List[str] = []
    _market_update_auto_install = False
    _market_update_install_ids: List[str] = []
    _market_update_exclude_ids: List[str] = []
    _market_update_skip_running = True
    _market_update_wiki_url = "https://wiki.movie-pilot.org/zh/plugin"
    _plugin_uninstall_id = ""
    _plugin_uninstall_remove_plugin = True
    _plugin_uninstall_clear_config = True
    _plugin_uninstall_clear_data = True
    _plugin_uninstall_delete_source = False
    _plugin_uninstall_notify = True
    _plugin_uninstall_notify_type = "Plugin"
    _seedclean_enabled = False
    _seedclean_cron = "0 */12 * * *"
    _seedclean_action = "pause"
    _seedclean_downloaders: List[str] = []
    _seedclean_size = ""
    _seedclean_ratio = ""
    _seedclean_time = ""
    _seedclean_upspeed = ""
    _seedclean_labels = ""
    _seedclean_pathkeywords = ""
    _seedclean_trackerkeywords = ""
    _seedclean_errorkeywords = ""
    _seedclean_torrentstates = ""
    _seedclean_torrentcategorys = ""
    _seedclean_samedata = False
    _seedclean_mponly = False
    _seedclean_notify = True
    _seedclean_notify_type = "Plugin"
    _subfill_enabled = False
    _subfill_details: List[str] = []
    _subfill_notify = False
    _subfill_notify_type = "Plugin"
    _subfill_category_enabled = False
    _subfill_category_confs = ""
    _subfill_confs: Dict[str, Any] = {}
    _msgnotify_enabled = False
    _msgnotify_types: List[str] = []
    _msgnotify_servers: List[str] = []
    _msgnotify_notify_type = "MediaServer"
    _dltag_enabled = False
    _dltag_downloaders: List[str] = []
    _dltag_prefix = ""
    _dltag_notify = True
    _dltag_notify_type = "Plugin"
    _sidebar_nav_enabled = True
    _msg_seen: Dict[str, float] = {}
    _MSG_GROUPS = {
        "新入库": {"library.new", "ItemAdded"},
        "开始播放": {"playback.start", "media.play", "PlaybackStart"},
        "停止播放": {"playback.stop", "media.stop", "PlaybackStop"},
        "登录成功": {"user.authenticated"},
        "登录失败": {"user.authenticationfailed"},
        "标记": {"item.rate"},
    }
    _MSG_LABEL = {"新入库": "新入库", "开始播放": "开始播放", "停止播放": "停止播放",
                  "登录成功": "登录成功", "登录失败": "登录失败", "标记": "标记了"}
    _webhook_images = {
        "emby": "https://emby.media/notificationicon.png",
        "plex": "https://www.plex.tv/wp-content/uploads/2022/04/new-logo-process-lines-gray.png",
        "jellyfin": "https://play-lh.googleusercontent.com/SCsUK3hCCRqkJbmLDctNYCfehLxsS4ggD1ZPHIFrrAN1Tn9yhjmGMPep2D9lMaaa9eQi",
    }
    _last_summary = "尚未执行"
    MP_DASHBOARD_WIDGETS: List[Dict[str, Any]] = [
        {
            "key": "site",
            "name": "MP 运维助手 - 站点数据统计",
            "title": "站点数据统计",
            "subtitle": "上传下载增量与站点占比",
            "md": 8,
            "rows": 18,
        },
        {
            "key": "actions",
            "name": "MP 运维助手 - 手动操作",
            "title": "手动操作",
            "subtitle": "常用运维动作",
            "md": 4,
            "rows": 18,
        },
    ]
    def init_plugin(self, config: dict = None):
        config = config or {}
        self._enabled = bool(config.get("enabled"))
        self._sidebar_nav_enabled = bool(config.get("sidebar_nav_enabled", True))
        self._local_plugin_repo = config.get("local_plugin_repo") or DEFAULT_LOCAL_PLUGIN_REPO
        self._daily_report_enabled = bool(config.get("daily_report_enabled", True))
        self._daily_report_cron = config.get("daily_report_cron") or "0 22 * * *"
        self._daily_report_greeting = str(config.get("daily_report_greeting") or "少爷").strip() or "少爷"
        self._daily_report_msgtype = config.get("daily_report_msgtype") or "Plugin"
        self._health_in_report = bool(config.get("health_in_report", True))
        self._subscribe_reminder_enabled = bool(config.get("subscribe_reminder_enabled", config.get("subscribe_in_report", True)))
        self._site_stat_enabled = bool(config.get("site_stat_enabled", config.get("site_stat_in_report", True)))
        self._subscribe_in_report = bool(config.get("subscribe_in_report", self._subscribe_reminder_enabled)) and self._subscribe_reminder_enabled
        self._site_stat_in_report = bool(config.get("site_stat_in_report", self._site_stat_enabled)) and self._site_stat_enabled
        self._report_version = bool(config.get("report_version", True))
        self._report_site_status = bool(config.get("report_site_status", True))
        self._report_site_increment = bool(config.get("report_site_increment", self._site_stat_in_report))
        self._report_today_download = bool(config.get("report_today_download", True))
        self._report_transfer = bool(config.get("report_transfer", True))
        self._report_subscribe = bool(config.get("report_subscribe", self._subscribe_in_report))
        self._report_storage = bool(config.get("report_storage", True))
        self._report_media_stat = bool(config.get("report_media_stat", True))
        self._report_summary = bool(config.get("report_summary", self._health_in_report))
        self._health_check_enabled = bool(config.get("health_check_enabled", True))
        self._health_check_cron = config.get("health_check_cron") or "0 */6 * * *"
        self._health_check_items = self._parse_csv(config.get("health_check_items"))
        self._health_check_database_targets = self._parse_csv(config.get("health_check_database_targets"))
        self._health_check_storage_targets = self._parse_csv(config.get("health_check_storage_targets"))
        self._health_check_directory_targets = self._parse_csv(config.get("health_check_directory_targets"))
        self._health_check_storage_threshold = self._safe_int(config.get("health_check_storage_threshold"), 85, 1)
        if self._health_check_storage_threshold > 99:
            self._health_check_storage_threshold = 99
        self._health_check_notify_type = config.get("health_check_notify_type") or "Plugin"
        self._report_health = bool(config.get("report_health", True))
        self._subscribe_reminder_onlyonce = bool(config.get("subscribe_reminder_onlyonce", False))
        self._subscribe_reminder_time = str(config.get("subscribe_reminder_time") or "9")
        self._subscribe_reminder_cron = config.get("subscribe_reminder_cron") or ""
        if not self._subscribe_reminder_cron:
            self._subscribe_reminder_cron = f"0 {self._subscribe_reminder_time} * * *" if self._subscribe_reminder_time.isdigit() else "0 9 * * *"
        self._subscribe_reminder_subtype = config.get("subscribe_reminder_subtype") or ["movie", "tv"]
        if isinstance(self._subscribe_reminder_subtype, str):
            self._subscribe_reminder_subtype = self._parse_csv(self._subscribe_reminder_subtype)
        self._subscribe_reminder_msgtype = config.get("subscribe_reminder_msgtype") or "Subscribe"
        self._site_stat_onlyonce = bool(config.get("site_stat_onlyonce", False))
        self._site_stat_dashboard_type = config.get("site_stat_dashboard_type") or "today"
        self._site_stat_notify_type = config.get("site_stat_notify_type") or "inc"
        self._log_clean_enabled = bool(config.get("log_clean_enabled", False))
        self._log_clean_cron = config.get("log_clean_cron") or "0 3 * * 1"
        self._log_clean_rows = self._safe_int(config.get("log_clean_rows"), 300, 0)
        self._log_clean_selected_ids = self._parse_csv(config.get("log_clean_selected_ids"))
        self._log_clean_notify = bool(config.get("log_clean_notify", True))
        self._log_clean_notify_type = config.get("log_clean_notify_type") or "Plugin"
        self._backup_enabled = bool(config.get("backup_enabled", False))
        self._backup_onlyonce = bool(config.get("backup_onlyonce", False))
        self._backup_cron = config.get("backup_cron") or "0 4 * * 1"
        self._backup_keep_count = self._safe_int(config.get("backup_keep_count"), 5, 1)
        self._backup_path = config.get("backup_path") or "/config/plugins/AgentOpsAssistant/Backup"
        self._backup_notify = bool(config.get("backup_notify", True))
        self._backup_notify_type = config.get("backup_notify_type") or "Plugin"
        self._backup_webdav_enabled = bool(config.get("backup_webdav_enabled", False))
        self._backup_webdav_notify = bool(config.get("backup_webdav_notify", False))
        self._backup_webdav_notify_type = config.get("backup_webdav_notify_type") or "Plugin"
        self._backup_webdav_digest_auth = bool(config.get("backup_webdav_digest_auth", False))
        self._backup_webdav_disable_check = bool(config.get("backup_webdav_disable_check", False))
        self._backup_webdav_hostname = str(config.get("backup_webdav_hostname") or "").strip()
        self._backup_webdav_login = str(config.get("backup_webdav_login") or "").strip()
        self._backup_webdav_password = str(config.get("backup_webdav_password") or "")
        self._backup_webdav_max_count = self._safe_int(config.get("backup_webdav_max_count"), 5, 1)
        self._mp_update_enabled = bool(config.get("mp_update_enabled", False))
        self._mp_update_cron = config.get("mp_update_cron") or "0 9 * * *"
        self._mp_update_notify = bool(config.get("mp_update_notify", True))
        self._mp_update_notify_type = config.get("mp_update_notify_type") or "Plugin"
        self._mp_update_restart_confirm = bool(config.get("mp_update_restart_confirm", config.get("mp_update_restart", False)))
        self._mp_update_types = config.get("mp_update_types") or ["后端", "前端"]
        if isinstance(self._mp_update_types, str):
            self._mp_update_types = self._parse_csv(self._mp_update_types) or ["后端", "前端"]
        self._market_update_enabled = bool(config.get("market_update_enabled", False))
        self._market_update_onlyonce = bool(config.get("market_update_onlyonce", False))
        self._market_update_interval = self._safe_int(config.get("market_update_interval"), 86400, 60)
        self._market_update_notify = bool(config.get("market_update_notify", True))
        self._market_update_write_notify = bool(config.get("market_update_write_notify", False))
        self._market_update_notify_type = config.get("market_update_notify_type") or "Plugin"
        self._market_update_write_settings = bool(config.get("market_update_write_settings", False))
        self._market_update_write_env = bool(config.get("market_update_write_env", False))
        self._market_update_blacklist_enabled = bool(config.get("market_update_blacklist_enabled", False))
        self._market_update_blacklist = self._parse_csv(config.get("market_update_blacklist"))
        self._market_update_auto_install = bool(config.get("market_update_auto_install", False))
        self._market_update_install_ids = self._parse_csv(config.get("market_update_install_ids"))
        self._market_update_exclude_ids = self._parse_csv(config.get("market_update_exclude_ids"))
        self._market_update_skip_running = bool(config.get("market_update_skip_running", True))
        self._market_update_auto_get = bool(config.get("market_update_auto_get", False))
        self._market_update_proxy = bool(config.get("market_update_proxy", True))
        self._market_update_timeout = self._safe_int(config.get("market_update_timeout"), 5, 1)
        self._market_update_wiki_url = config.get("market_update_wiki_url") or "https://wiki.movie-pilot.org/zh/plugin"
        self._market_update_wiki_xpath = config.get("market_update_wiki_xpath") or '//pre[@class="prismjs line-numbers" and @v-pre="true"]/code/text()'
        self._plugin_uninstall_id = str(config.get("plugin_uninstall_id") or "").strip()
        self._plugin_uninstall_ids = config.get("plugin_uninstall_ids") or ([] if not self._plugin_uninstall_id else [self._plugin_uninstall_id])
        if isinstance(self._plugin_uninstall_ids, str):
            self._plugin_uninstall_ids = self._parse_csv(self._plugin_uninstall_ids)
        self._plugin_uninstall_remove_plugin = bool(config.get("plugin_uninstall_remove_plugin", True))
        self._plugin_uninstall_clear_config = bool(config.get("plugin_uninstall_clear_config", True))
        self._plugin_uninstall_clear_data = bool(config.get("plugin_uninstall_clear_data", True))
        self._plugin_uninstall_delete_source = bool(config.get("plugin_uninstall_delete_source", False))
        self._plugin_uninstall_notify = bool(config.get("plugin_uninstall_notify", True))
        self._plugin_uninstall_notify_type = config.get("plugin_uninstall_notify_type") or "Plugin"
        self._seedclean_enabled = bool(config.get("seedclean_enabled", False))
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
        self._seedclean_torrentcategorys = str(config.get("seedclean_torrentcategorys") or "").strip()
        self._seedclean_samedata = bool(config.get("seedclean_samedata", False))
        self._seedclean_mponly = bool(config.get("seedclean_mponly", False))
        self._seedclean_notify = bool(config.get("seedclean_notify", True))
        self._seedclean_notify_type = config.get("seedclean_notify_type") or "Plugin"
        self._subfill_enabled = bool(config.get("subfill_enabled", False))
        self._subfill_details = self._parse_csv(config.get("subfill_details"))
        self._subfill_notify = bool(config.get("subfill_notify", False))
        self._subfill_notify_type = config.get("subfill_notify_type") or "Plugin"
        self._subfill_category_enabled = bool(config.get("subfill_category_enabled", False))
        self._subfill_category_confs = config.get("subfill_category_confs") or ""
        self._subfill_confs = self._parse_subfill_confs(self._subfill_category_confs)
        self._msgnotify_enabled = bool(config.get("msgnotify_enabled", False))
        self._msgnotify_types = self._parse_csv(config.get("msgnotify_types"))
        self._msgnotify_servers = self._parse_csv(config.get("msgnotify_servers"))
        self._msgnotify_notify_type = config.get("msgnotify_notify_type") or "MediaServer"
        self._dltag_enabled = bool(config.get("dltag_enabled", False))
        self._dltag_downloaders = self._parse_csv(config.get("dltag_downloaders"))
        self._dltag_prefix = str(config.get("dltag_prefix") or "").strip()
        self._dltag_notify = bool(config.get("dltag_notify", True))
        self._dltag_notify_type = config.get("dltag_notify_type") or "Plugin"
        self._msg_seen = {}
        self._last_summary = self._build_summary()
        self._fire_onlyonce(config or {})

    def _fire_onlyonce(self, config: Dict[str, Any]) -> List[str]:
        """“保存后立即运行一次”：对置位的 onlyonce 开关各跑一次对应任务并清除该开关，
        避免下次重载重复触发。任务异步执行，不阻塞插件初始化。"""
        once = [
            ("backup_onlyonce", self.run_backup),
            ("log_clean_onlyonce", self.run_log_clean),
            ("market_update_onlyonce", self.run_market_update),
            ("subscribe_reminder_onlyonce", self.run_subscribe_reminder),
            ("site_stat_onlyonce", lambda: (self.api_run_site_stat() or {}).get("code") == 0),
        ]
        pending = [(k, fn) for k, fn in once if config.get(k)]
        if not pending:
            return []
        for k, _ in pending:
            config[k] = False
        try:
            self.update_config(config)
        except Exception as err:
            logger.warning(f"AgentOpsAssistant 清除 onlyonce 开关失败：{err}")

        def _runner():
            for key, fn in pending:
                try:
                    fn()
                except Exception as err:
                    logger.error(f"AgentOpsAssistant onlyonce {key} 执行失败：{err}")
        timer = threading.Timer(2.0, _runner)
        timer.daemon = True
        timer.start()
        return [k for k, _ in pending]

    def get_state(self) -> bool:
        return self._enabled

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        return [
            {"cmd": "/mpops_report", "event": EventType.PluginAction, "desc": "发送 MP 运维每日汇报", "category": "MP运维", "data": {"action": "mpops_report"}},
            {"cmd": "/mpops_subscribe", "event": EventType.PluginAction, "desc": "立即推送订阅追新", "category": "MP运维", "data": {"action": "mpops_subscribe"}},
            {"cmd": "/mpops_report_preview", "event": EventType.PluginAction, "desc": "预览 MP 运维每日汇报（不发送）", "category": "MP运维", "data": {"action": "mpops_report_preview"}},
            {"cmd": "/mpops_health", "event": EventType.PluginAction, "desc": "执行 MP 运维健康巡查", "category": "MP运维", "data": {"action": "mpops_health"}},
            {"cmd": "/mpops_logs", "event": EventType.PluginAction, "desc": "预览 MoviePilot 日志清理范围", "category": "MP运维", "data": {"action": "mpops_logs"}},
            {"cmd": "/mpops_logs_clean", "event": EventType.PluginAction, "desc": "执行插件日志清理（按保留行数截断）", "category": "MP运维", "data": {"action": "mpops_logs_clean"}},
            {"cmd": "/mpops_backup", "event": EventType.PluginAction, "desc": "执行 MP 运维助手自动备份", "category": "MP运维", "data": {"action": "mpops_backup"}},
            {"cmd": "/mpops_updates", "event": EventType.PluginAction, "desc": "检查 MoviePilot 后端/前端更新", "category": "MP运维", "data": {"action": "mpops_updates"}},
            {"cmd": "/mpops_market", "event": EventType.PluginAction, "desc": "检查插件库更新并按确认写入", "category": "MP运维", "data": {"action": "mpops_market"}},
            {"cmd": "/mpops_run_all", "event": EventType.PluginAction, "desc": "依次执行每日汇报与健康巡查", "category": "MP运维", "data": {"action": "mpops_run_all"}},
            {"cmd": "/mpops_plugin_preview", "event": EventType.PluginAction, "desc": "预览插件卸载与残留清理范围", "category": "MP运维", "data": {"action": "mpops_plugin_preview"}},
            {"cmd": "/mpops_plugin_clean", "event": EventType.PluginAction, "desc": "执行插件卸载（需配置页显式确认）", "category": "MP运维", "data": {"action": "mpops_plugin_clean"}},
            {"cmd": "/mpops_seed_clean", "event": EventType.PluginAction, "desc": "执行自动删种（按规则暂停/删除种子）", "category": "MP运维", "data": {"action": "mpops_seed_clean"}},
            {"cmd": "/mpops_downloader_tag", "event": EventType.PluginAction, "desc": "按站点为种子批量补打标签", "category": "MP运维", "data": {"action": "mpops_downloader_tag"}},
            {"cmd": "/agentops_heartbeat", "event": EventType.PluginAction, "desc": "兼容旧命令：发送每日汇报", "category": "MP运维", "data": {"action": "mpops_report"}},
            {"cmd": "/agentops_run_all", "event": EventType.PluginAction, "desc": "兼容旧命令：执行全部低风险任务", "category": "MP运维", "data": {"action": "mpops_run_all"}},
        ]

    def get_api(self) -> List[Dict[str, Any]]:
        return [
            {"path": "/dashboard", "endpoint": self.api_dashboard, "auth": "bear", "methods": ["GET"], "summary": "仪表盘数据：模块状态、最近执行、健康概览"},
            {"path": "/installed_plugins", "endpoint": self.api_installed_plugins, "auth": "bear", "methods": ["GET"], "summary": "已安装插件列表，供插件卸载下拉选择"},
            {"path": "/plugin_markets", "endpoint": self.api_plugin_markets, "auth": "bear", "methods": ["GET"], "summary": "已配置插件库仓库列表，供更新黑名单下拉选择"},
            {"path": "/run_daily_report", "endpoint": self.api_run_daily_report, "auth": "bear", "methods": ["POST"], "summary": "立即发送每日汇报"},
            {"path": "/run_subscribe_reminder", "endpoint": self.api_run_subscribe_reminder, "auth": "bear", "methods": ["POST"], "summary": "立即推送订阅追新"},
            {"path": "/preview_daily_report", "endpoint": self.api_preview_daily_report, "auth": "bear", "methods": ["POST"], "summary": "预览每日汇报（不发送）"},
            {"path": "/run_health_check", "endpoint": self.api_run_health_check, "auth": "bear", "methods": ["POST"], "summary": "立即执行健康巡查"},
            {"path": "/preview_log_clean", "endpoint": self.api_preview_log_clean, "auth": "bear", "methods": ["POST"], "summary": "预览日志清理范围"},
            {"path": "/run_log_clean", "endpoint": self.api_run_log_clean, "auth": "bear", "methods": ["POST"], "summary": "执行插件日志清理"},
            {"path": "/run_backup", "endpoint": self.api_run_backup, "auth": "bear", "methods": ["POST"], "summary": "执行MP运维助手自动备份"},
            {"path": "/preview_updates", "endpoint": self.api_preview_updates, "auth": "bear", "methods": ["POST"], "summary": "预览MoviePilot后端/前端更新状态（不通知、不重启）"},
            {"path": "/run_mp_update", "endpoint": self.api_run_mp_update, "auth": "bear", "methods": ["POST"], "summary": "立即检查MoviePilot后端/前端更新并通知"},
            {"path": "/preview_market_update", "endpoint": self.api_preview_market_update, "auth": "bear", "methods": ["POST"], "summary": "预览插件库更新"},
            {"path": "/run_market_update", "endpoint": self.api_run_market_update, "auth": "bear", "methods": ["POST"], "summary": "执行插件库更新检查并按确认写入"},
            {"path": "/preview_plugin_uninstall", "endpoint": self.api_preview_plugin_uninstall, "auth": "bear", "methods": ["POST"], "summary": "预览插件卸载与残留清理范围"},
            {"path": "/run_plugin_uninstall", "endpoint": self.api_run_plugin_uninstall, "auth": "bear", "methods": ["POST"], "summary": "执行插件卸载与残留清理"},
            {"path": "/run_seed_clean", "endpoint": self.api_run_seed_clean, "auth": "bear", "methods": ["POST"], "summary": "立即执行自动删种"},
            {"path": "/downloaders", "endpoint": self.api_downloaders, "auth": "bear", "methods": ["GET"], "summary": "已配置下载器列表，供自动删种下拉选择"},
            {"path": "/mediaservers", "endpoint": self.api_mediaservers, "auth": "bear", "methods": ["GET"], "summary": "已配置媒体服务器列表，供媒体库通知过滤"},
            {"path": "/subfill_clear_history", "endpoint": self.api_subfill_clear_history, "auth": "bear", "methods": ["POST"], "summary": "清理订阅规则填充历史记录"},
            {"path": "/subfill_clear_handled", "endpoint": self.api_subfill_clear_handled, "auth": "bear", "methods": ["POST"], "summary": "清理订阅规则填充已处理记录"},
            {"path": "/site_stat_chart", "endpoint": self.api_site_stat_chart, "auth": "bear", "methods": ["GET"], "summary": "今日各站点上传/下载增量，供仪表盘饼图"},
            {"path": "/run_site_stat", "endpoint": self.api_run_site_stat, "auth": "bear", "methods": ["POST"], "summary": "刷新站点数据统计"},
            {"path": "/run_downloader_tag", "endpoint": self.api_run_downloader_tag, "auth": "bear", "methods": ["POST"], "summary": "按站点为种子批量补打标签"},
            {"path": "/downloader_overview", "endpoint": self.api_downloader_overview, "auth": "bear", "methods": ["GET"], "summary": "下载器活动种子概览"},
            {"path": "/run_heartbeat_report", "endpoint": self.api_run_daily_report, "auth": "bear", "methods": ["POST"], "summary": "兼容旧接口：立即发送每日汇报"},
        ]

    @staticmethod
    def get_render_mode() -> Tuple[str, str]:
        """声明使用 MoviePilot Vue 联邦组件渲染。"""
        return "vue", "dist/assets"

    def get_service(self) -> List[Dict[str, Any]]:
        if not self.get_state():
            return []
        services = []
        if self._daily_report_enabled:
            self._append_cron_service(services, "AgentOpsAssistant.DailyReport", "MP 运维助手 - 每日汇报", self._daily_report_cron, self.run_daily_report)
        if self._subscribe_reminder_enabled:
            self._append_cron_service(services, "AgentOpsAssistant.SubscribeReminder", "MP 运维助手 - 订阅追新推送", self._subscribe_reminder_cron, self.run_subscribe_reminder)
        if self._health_check_enabled:
            self._append_cron_service(services, "AgentOpsAssistant.HealthCheck", "MP 运维助手 - 健康巡查", self._health_check_cron, self.run_health_check)
        if self._log_clean_enabled:
            self._append_cron_service(services, "AgentOpsAssistant.LogClean", "MP 运维助手 - 插件日志清理", self._log_clean_cron, self.run_log_clean)
        if self._backup_enabled:
            self._append_cron_service(services, "AgentOpsAssistant.Backup", "MP 运维助手 - 自动备份", self._backup_cron, self.run_backup)
        if self._mp_update_enabled:
            self._append_cron_service(services, "AgentOpsAssistant.MPUpdate", "MP 运维助手 - MoviePilot更新检查", self._mp_update_cron, self.run_mp_update_check)
        if self._market_update_enabled:
            services.append({"id": "AgentOpsAssistant.MarketUpdate", "name": "MP 运维助手 - 插件库更新检查", "trigger": IntervalTrigger(seconds=self._market_update_interval), "func": self.run_market_update, "kwargs": {}})
        if self._seedclean_enabled and self._seedclean_downloaders:
            self._append_cron_service(services, "AgentOpsAssistant.SeedClean", "MP 运维助手 - 自动删种", self._seedclean_cron, self.run_seed_clean)
        return services

    @staticmethod
    def _append_cron_service(services: List[Dict[str, Any]], service_id: str, name: str, cron: str, func) -> None:
        cron_text = str(cron or "").strip()
        if len(cron_text.split()) != 5:
            logger.warning(f"AgentOpsAssistant 定时服务 {name} cron 配置无效，已跳过：{cron}")
            return
        try:
            trigger = CronTrigger.from_crontab(cron_text)
        except Exception as err:
            logger.warning(f"AgentOpsAssistant 定时服务 {name} cron 配置无效，已跳过：{cron}；{err}")
            return
        services.append({"id": service_id, "name": name, "trigger": trigger, "func": func, "kwargs": {}})

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        """Vue 模式下配置页由 Config 组件渲染，这里只返回安全配置模型。"""
        return [], self._default_config()

    def get_page(self) -> List[dict]:
        """Vue 模式下详情页由 Page 组件（仪表盘）渲染，这里返回空列表以注册入口。"""
        return []

    def get_sidebar_nav(self) -> List[Dict[str, Any]]:
        """声明插件在 MoviePilot 主界面左侧导航中的仪表盘入口。"""
        if not self.get_state() or not self._sidebar_nav_enabled:
            return []
        return [{
            "nav_key": "main",
            "title": "MP 运维助手",
            "icon": "mdi-view-dashboard-outline",
            "section": "start",
            "permission": "manage",
            "order": 50,
        }]

    def get_dashboard_meta(self) -> List[Dict[str, str]]:
        if not self.get_state():
            return []
        return [
            {"key": item["key"], "name": item["name"]}
            for item in self.MP_DASHBOARD_WIDGETS
        ]

    def get_dashboard(self, key: str = "", **kwargs):
        if not self.get_state():
            return None
        widget_key = key or "site"
        widget = next((item for item in self.MP_DASHBOARD_WIDGETS if item["key"] == widget_key), None)
        if not widget:
            return None
        cols = {"cols": 12, "md": widget.get("md", 4)}
        attrs = {
            "title": widget.get("title") or widget.get("name"),
            "subtitle": widget.get("subtitle", ""),
            "border": False,
            "component": widget["key"],
            "rows": widget.get("rows", 5),
            "refresh": 60,
        }
        return cols, attrs, []

    def stop_service(self):
        pass

    @eventmanager.register(EventType.PluginAction)
    def handle_command(self, event: Event = None):
        if not event:
            return
        action = (event.event_data or {}).get("action", "")
        handlers = {
            "mpops_report": [("每日汇报", self.run_daily_report)],
            "mpops_subscribe": [("订阅追新", self.run_subscribe_reminder)],
            "mpops_report_preview": [("预览每日汇报", self.run_daily_report_preview)],
            "mpops_health": [("健康巡查", self.run_health_check)],
            "mpops_logs": [("日志清理预览", self.run_log_preview)],
            "mpops_logs_clean": [("日志清理", self.run_log_clean)],
            "mpops_backup": [("自动备份", self.run_backup)],
            "mpops_updates": [("主程序更新检查", self.run_mp_update_check)],
            "mpops_market": [("插件库更新", self.run_market_update)],
            "mpops_run_all": [("每日汇报", self.run_daily_report), ("健康巡查", self.run_health_check)],
            "mpops_plugin_preview": [("插件卸载预览", self.run_plugin_uninstall_preview)],
            "mpops_plugin_clean": [("插件卸载", self.run_plugin_uninstall_clean)],
            "mpops_seed_clean": [("自动删种", self.run_seed_clean)],
            "mpops_downloader_tag": [("种子打标签", self.run_downloader_tag)],
        }
        tasks = handlers.get(action)
        if not tasks:
            return
        results = []
        has_failed_task = False
        task_sent_message = False
        original_post_message = self.post_message
        had_instance_post_message = "post_message" in getattr(self, "__dict__", {})

        def tracked_post_message(*args, **kwargs):
            nonlocal task_sent_message
            task_sent_message = True
            return original_post_message(*args, **kwargs)

        try:
            # 远程命令只在任务本身没有发业务通知时补发结果，避免用户收到两条近似消息。
            self.post_message = tracked_post_message
            for name, runner in tasks:
                ok = bool(runner())
                has_failed_task = has_failed_task or not ok
                results.append(f"{name}：{'成功' if ok else '失败'}")
        finally:
            if had_instance_post_message:
                self.post_message = original_post_message
            else:
                try:
                    delattr(self, "post_message")
                except AttributeError:
                    pass
        if has_failed_task or not task_sent_message:
            original_post_message(mtype=NotificationType.Plugin, title="MP 运维助手命令执行结果", text="\n".join(results))

    @eventmanager.register(EventType.DownloadAdded)
    def on_download_fill_subscribe(self, event: Event = None):
        """下载添加后，用实际下载到的资源回填对应电视剧订阅的空规则（移植自 thsrite SubscribeGroup 下载填充）。
        仅填充订阅中尚为空的字段，已设置的不覆盖；按 tmdbid 去重，仅处理一次。"""
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
            logger.warning(f"AgentOpsAssistant 订阅填充加载依赖失败：{err}")
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
                if self._subfill_notify:
                    self.post_message(mtype=self._notification_type(self._subfill_notify_type), title="MP 运维助手 - 订阅规则自动填充", text=text)
        except Exception as err:
            logger.error(f"AgentOpsAssistant 订阅规则填充失败：{err}")

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
            for conf in str(line).split("#"):
                if ":" not in conf:
                    continue
                k = conf.split(":")[0].strip()
                v = ":".join(conf.split(":")[1:]).strip()
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

    @eventmanager.register(EventType.SubscribeAdded)
    def on_subscribe_added_fill(self, event: Event = None):
        """新增订阅时按媒体二级分类套用自定义规则（移植自 thsrite SubscribeGroup 二级分类填充）。"""
        if not self._subfill_category_enabled or not self._subfill_confs:
            return
        data = getattr(event, "event_data", None) if event else None
        if not data or not data.get("subscribe_id") or not data.get("mediainfo"):
            return
        try:
            from app.db.subscribe_oper import SubscribeOper
        except Exception as err:
            logger.warning(f"AgentOpsAssistant 订阅二级分类填充加载依赖失败：{err}")
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
            if self._subfill_notify:
                self.post_message(mtype=self._notification_type(self._subfill_notify_type), title="MP 运维助手 - 订阅规则自动填充",
                                  text=self._format_subfill([{"name": getattr(sub, "name", str(sid)), "update": upd}]))
        except Exception as err:
            logger.error(f"AgentOpsAssistant 订阅二级分类填充失败：{err}")

    def run_subfill_clear_history(self) -> bool:
        self.save_data("subfill_history", [])
        self._save_task_result("清理填充历史", True, 0, "已清理订阅规则填充历史记录")
        return True

    def run_subfill_clear_handled(self) -> bool:
        self.save_data("subfill_handled", [])
        self._save_task_result("清理已处理", True, 0, "已清理已处理记录，后续下载可重新填充")
        return True

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

    @eventmanager.register(EventType.WebhookMessage)
    def on_webhook_message(self, event: Event = None):
        """媒体库服务器通知（移植自 jxxghp MediaServerMsg 核心）：把 Emby/Jellyfin/Plex 的
        播放/入库/登录等 webhook 事件按配置推送通知。不含原插件的剧集聚合/IP定位/海报抓取。"""
        if not self._msgnotify_enabled or not self._msgnotify_types:
            return
        info = getattr(event, "event_data", None) if event else None
        if not info:
            return
        try:
            group = self._msg_group_of(getattr(info, "event", None))
            if not group or group not in self._msgnotify_types:
                return
            server_name = getattr(info, "server_name", None)
            if self._msgnotify_servers and server_name and server_name not in self._msgnotify_servers:
                return
            item_id = getattr(info, "item_id", "") or ""
            if item_id and not self._msg_dedupe(f"{server_name}-{group}-{item_id}"):
                return
            title = self._msg_title(group, info)
            text = self._msg_text(info)
            image = getattr(info, "image_url", None) or self._webhook_images.get(getattr(info, "channel", "") or "")
            self.post_message(mtype=self._notification_type(self._msgnotify_notify_type, "MediaServer"), title=title, text=text, image=image)
        except Exception as err:
            logger.error(f"AgentOpsAssistant 媒体库通知处理失败：{err}")

    @classmethod
    def _msg_group_of(cls, etype):
        if not etype:
            return None
        for group, members in cls._MSG_GROUPS.items():
            if etype in members:
                return group
        return None

    def _msg_dedupe(self, key: str) -> bool:
        """30 秒内重复事件返回 False（不再通知）；新事件返回 True 并记录。"""
        now = datetime.now().timestamp()
        seen = self._msg_seen if isinstance(self._msg_seen, dict) else {}
        for k in [k for k, ts in seen.items() if now - ts > 30]:
            seen.pop(k, None)
        if key in seen:
            return False
        seen[key] = now
        self._msg_seen = seen
        return True

    def _msg_title(self, group: str, info: Any) -> str:
        action = self._MSG_LABEL.get(group, group)
        item_type = getattr(info, "item_type", "") or ""
        name = getattr(info, "item_name", "") or ""
        if item_type in ("TV", "SHOW"):
            return f"{action}剧集 {name}".strip()
        if item_type == "MOV":
            return f"{action}电影 {name}".strip()
        if item_type == "AUD":
            return f"{action}有声书 {name}".strip()
        return action

    @staticmethod
    def _msg_text(info: Any) -> str:
        parts = []
        user = getattr(info, "user_name", None)
        if user:
            parts.append(f"用户：{user}")
        device = getattr(info, "device_name", None)
        client = getattr(info, "client", None)
        if device:
            parts.append(f"设备：{(client or '')} {device}".strip())
        elif client:
            parts.append(f"设备：{client}")
        ip = getattr(info, "ip", None)
        if ip:
            parts.append(f"IP地址：{ip}")
        pct = getattr(info, "percentage", None)
        if pct:
            try:
                parts.append(f"进度：{round(float(pct), 2)}%")
            except (ValueError, TypeError):
                pass
        overview = getattr(info, "overview", None)
        if overview:
            parts.append(f"剧情：{overview}")
        parts.append("时间：" + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        return "\n".join(parts)

    def run_subscribe_reminder(self) -> bool:
        """独立推送今日订阅追新（与每日汇报分开，按 subscribe_reminder_cron 调度，也可手动触发）。"""
        name = "订阅追新"
        try:
            items = self._get_today_subscribe_updates_locked()
            if items:
                body = "📺 今日订阅追新：\n" + "\n".join(f"⦁ {x}" for x in items)
            else:
                body = "📺 今日订阅追新：暂无更新"
            try:
                mtype = self._notification_type(self._subscribe_reminder_msgtype, "Subscribe")
            except Exception:
                mtype = self._notification_type("Plugin")
            self.post_message(mtype=mtype, title="MP 运维助手 - 订阅追新", text=body)
            self._save_task_result(name, True, 0, body)
            return True
        except Exception as err:
            self._save_task_result(name, False, -1, str(err))
            logger.error(f"AgentOpsAssistant 订阅追新推送失败：{err}")
            return False

    def run_daily_report(self) -> bool:
        name = "MP运维每日汇报"
        try:
            text = self._build_daily_report_message()
            self.post_message(mtype=self._notification_type(self._daily_report_msgtype), title="MP 运维每日汇报", text=text)
            self._save_daily_report_result(sent=True, success=True, text=text, error="")
            self._save_task_result(name, True, 0, "OK plugin_notification_channel")
            return True
        except Exception as err:
            self._save_daily_report_result(sent=True, success=False, text="", error=str(err))
            self._save_task_result(name, False, -1, str(err))
            logger.error(f"AgentOpsAssistant MP运维每日汇报 执行失败：{err}")
            return False

    def run_daily_report_preview(self) -> bool:
        name = "预览每日汇报"
        try:
            text = self._build_daily_report_message(preview=True)
            self._save_daily_report_result(sent=False, success=True, text=text, error="")
            self._save_task_result("日报预览", True, 0, text)
            self._save_task_result(name, True, 0, text)
            return True
        except Exception as err:
            self._save_daily_report_result(sent=False, success=False, text="", error=str(err))
            self._save_task_result("日报预览", False, -1, str(err))
            self._save_task_result(name, False, -1, str(err))
            logger.error(f"AgentOpsAssistant 预览每日汇报 执行失败：{err}")
            return False

    def _save_daily_report_result(self, sent: bool, success: bool, text: str = "", error: str = ""):
        self.save_data("last_daily_report", {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "template": "2026-05-29.fixed-v1-locked",
            "sent": bool(sent),
            "success": bool(success),
            "chars": len(text or ""),
            "sections": self._count_report_sections(text or ""),
            "preview": (text or "")[:2000],
            "error": (error or "")[:1000],
        })

    @staticmethod
    def _count_report_sections(text: str) -> int:
        icons = ["🕒", "🤖", "📡", "📈", "⬇️", "📥", "📦", "📺", "💾", "🎬", "🩺", "✅", "⚠️"]
        return sum(1 for icon in icons if icon in (text or ""))

    def api_preview_daily_report(self) -> Dict[str, Any]:
        try:
            text = self._build_daily_report_message(preview=True)
            data = {
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "template": "2026-05-29.fixed-v1-locked",
                "sent": False,
                "success": True,
                "chars": len(text or ""),
                "sections": self._count_report_sections(text or ""),
                "preview": text,
                "error": "",
            }
            return {"code": 0, "msg": "每日汇报预览已生成", "data": data, "text": text}
        except Exception as err:
            return {"code": 1, "msg": f"每日汇报预览失败：{err}", "data": {}, "text": ""}

    def api_run_daily_report(self) -> Dict[str, Any]:
        return self._api_run_task("每日汇报", self.run_daily_report)

    def api_run_subscribe_reminder(self) -> Dict[str, Any]:
        return self._api_run_task("订阅追新", self.run_subscribe_reminder)

    def run_health_check(self) -> bool:
        data = self._build_health_summary()
        text = self._format_health_summary(data)
        self._save_task_result("健康巡查", True, 0, text)
        self.save_data("last_health_check", {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "success": bool(data.get("success")),
            "output": text,
        })
        self._notify_health_failures(data)
        return True

    def api_run_health_check(self) -> Dict[str, Any]:
        self.run_health_check()
        data = self.get_data("last_health_check") or {}
        failed = 0
        match = re.search(r"发现\s*(\d+)\s*项异常", str(data.get("output") or ""))
        if match:
            failed = self._safe_int(match.group(1), 0, 0)
        if data.get("success") is False:
            msg = f"健康巡查已完成，发现 {failed or '若干'} 项异常。"
        else:
            msg = "健康巡查已完成，未发现异常。"
        return {"code": 0, "msg": msg}

    def api_run_mp_update(self) -> Dict[str, Any]:
        return self._api_run_task("主程序更新检查", self.run_mp_update_check)

    def api_dashboard(self) -> Dict[str, Any]:
        """仪表盘数据：插件总状态、各模块快照、最近健康巡查概览。"""
        try:
            tasks = []
            for item in self._task_snapshot():
                latest = item.get("latest") or {}
                tasks.append({
                    "key": item.get("key"),
                    "name": item.get("name"),
                    "icon": item.get("icon"),
                    "enabled": bool(item.get("enabled")),
                    "state": item.get("state"),
                    "color": item.get("color"),
                    "next": item.get("next"),
                    "last_time": latest.get("time") or "",
                    "last_summary": self._task_result_summary(latest),
                })
            failed = [t for t in tasks if t["state"] == "失败"]
            health = self.get_data("last_health_check") or {}
            return {
                "code": 0,
                "data": {
                    "enabled": bool(self._enabled),
                    "summary": self._build_summary(),
                    "tasks": tasks,
                    "task_total": len(tasks),
                    "task_on": len([t for t in tasks if t["enabled"]]),
                    "task_failed": len(failed),
                    "health": {
                        "time": health.get("time") or "",
                        "success": health.get("success"),
                        "output": health.get("output") or "",
                    },
                },
            }
        except Exception as err:
            logger.error(f"仪表盘数据获取失败：{err}")
            return {"code": 1, "msg": f"仪表盘数据获取失败：{err}", "data": {}}

    def api_installed_plugins(self) -> Dict[str, Any]:
        """已安装插件列表，供插件卸载下拉选择（排除本插件自身）。"""
        try:
            from app.core.plugin import PluginManager
            plugins = PluginManager().get_local_plugins() or []
            items = []
            for p in plugins:
                pid = getattr(p, "id", None)
                if not pid or not getattr(p, "installed", False):
                    continue
                if str(pid).lower() == "agentopsassistant":
                    continue
                name = getattr(p, "plugin_name", None) or pid
                version = getattr(p, "plugin_version", "") or ""
                items.append({
                    "value": pid,
                    "title": f"{name} v{version}" if version else str(name),
                })
            items.sort(key=lambda x: x["title"])
            return {"code": 0, "data": items}
        except Exception as err:
            logger.error(f"已安装插件列表获取失败：{err}")
            return {"code": 1, "msg": f"已安装插件列表获取失败：{err}", "data": []}

    def api_plugin_markets(self) -> Dict[str, Any]:
        """已配置的插件库仓库地址列表，供更新黑名单下拉多选。"""
        try:
            markets = self._valid_markets_list(settings.PLUGIN_MARKET)
            items = []
            for url in markets:
                short = url.rstrip("/").split("/")
                label = "/".join(short[-2:]) if len(short) >= 2 else url
                items.append({"value": url, "title": label})
            items.sort(key=lambda x: x["title"].lower())
            return {"code": 0, "data": items}
        except Exception as err:
            logger.error(f"插件库仓库列表获取失败：{err}")
            return {"code": 1, "msg": f"插件库仓库列表获取失败：{err}", "data": []}

    def api_preview_log_clean(self) -> Dict[str, Any]:
        try:
            data = self._build_log_preview()
            return {"code": 0, "msg": "日志清理预览完成，未删除任何文件。", "data": data, "text": self._format_log_preview_text(data)}
        except Exception as err:
            logger.error(f"AgentOpsAssistant 日志清理预览失败：{err}")
            return {"code": 1, "msg": f"日志清理预览失败：{err}", "data": {}, "text": ""}

    def api_run_log_clean(self) -> Dict[str, Any]:
        ok = self.run_log_clean()
        return {"code": 0 if ok else 1, "msg": "插件日志清理执行成功" if ok else "插件日志清理执行失败，详情请查看插件日志。"}

    def run_log_preview(self) -> bool:
        data = self._build_log_preview()
        text = self._format_log_preview_text(data)
        self.post_message(mtype=NotificationType.Plugin, title="MP 运维助手 - 日志清理预览", text=text)
        self._save_task_result("日志清理预览", True, 0, text)
        return True

    def run_log_clean(self) -> bool:
        try:
            data = self._build_log_clean_stats(clean=True)
            text = self._format_log_clean_result_text(data)
            if self._log_clean_notify:
                self.post_message(mtype=self._notification_type(self._log_clean_notify_type), title="MP 运维助手 - 日志清理完成", text=text)
            self._save_task_result("日志清理", True, 0, text)
            return True
        except Exception as err:
            self._save_task_result("日志清理", False, -1, str(err))
            logger.error(f"AgentOpsAssistant 日志清理执行失败：{err}")
            return False

    def api_run_backup(self) -> Dict[str, Any]:
        ok = self.run_backup()
        data = self._build_backup_status()
        return {"code": 0 if ok else 1, "msg": "自动备份执行成功" if ok else "自动备份执行失败，详情请查看插件日志。", "data": data}

    def api_preview_updates(self) -> Dict[str, Any]:
        try:
            data = self._build_update_status()
            return {"code": 0, "msg": "更新状态预览完成，未执行更新或重启。", "data": data, "text": self._format_update_status_text(data)}
        except Exception as err:
            logger.error(f"AgentOpsAssistant 更新状态预览失败：{err}")
            return {"code": 1, "msg": f"更新状态预览失败：{err}", "data": {}, "text": ""}

    def api_preview_market_update(self) -> Dict[str, Any]:
        try:
            data = self._build_market_update_status(apply=False)
            return {"code": 0, "msg": "插件库更新预览完成，未写入配置。", "data": data, "text": self._format_market_update_text(data)}
        except Exception as err:
            return {"code": 1, "msg": f"插件库更新预览失败：{err}", "data": {}, "text": ""}

    def api_run_market_update(self) -> Dict[str, Any]:
        ok = self.run_market_update()
        data = self._build_market_status()
        return {"code": 0 if ok else 1, "msg": "插件库更新检查执行成功" if ok else "插件库更新检查失败，详情请查看插件日志。", "data": data}

    def api_preview_plugin_uninstall(self) -> Dict[str, Any]:
        try:
            data = self._build_plugin_uninstall_status(clean=False)
            success = bool(data.get("success", True))
            if success:
                msg = "插件卸载预览完成，未执行卸载或删除文件。"
            else:
                reason = data.get("blocked") or "；".join((data.get("errors") or [])[:2]) or "请检查插件卸载配置。"
                msg = f"插件卸载预览未通过：{reason}"
            return {"code": 0 if success else 1, "msg": msg, "data": data, "text": self._format_plugin_uninstall_text(data)}
        except Exception as err:
            logger.error(f"AgentOpsAssistant 插件卸载预览失败：{err}")
            return {"code": 1, "msg": f"插件卸载预览失败：{err}", "data": {}, "text": ""}

    def api_run_plugin_uninstall(self) -> Dict[str, Any]:
        ok = self.run_plugin_uninstall_clean()
        data = self._build_plugin_uninstall_status(clean=False)
        return {"code": 0 if ok else 1, "msg": "插件卸载执行成功" if ok else "插件卸载未执行或失败，详情请查看插件日志。", "data": data}

    def run_plugin_uninstall_preview(self) -> bool:
        data = self._build_plugin_uninstall_status(clean=False)
        text = self._format_plugin_uninstall_text(data)
        self.post_message(mtype=NotificationType.Plugin, title="MP 运维助手 - 插件卸载预览", text=text)
        self._save_task_result("插件卸载预览", bool(data.get("success", True)), 0 if data.get("success", True) else 1, text)
        return bool(data.get("success", True))

    def run_plugin_uninstall_clean(self) -> bool:
        if not (self._plugin_uninstall_ids or self._plugin_uninstall_id):
            text = "未执行：请先在配置页选择目标插件。"
            self._save_task_result("插件卸载", False, 2, text)
            if self._plugin_uninstall_notify:
                self.post_message(mtype=self._notification_type(self._plugin_uninstall_notify_type), title="MP 运维助手 - 插件卸载未执行", text=text)
            return False
        try:
            data = self._build_plugin_uninstall_status(clean=True)
            text = self._format_plugin_uninstall_text(data)
            if self._plugin_uninstall_notify:
                self.post_message(mtype=self._notification_type(self._plugin_uninstall_notify_type), title="MP 运维助手 - 插件卸载结果", text=text)
            self._save_task_result("插件卸载", bool(data.get("success")), 0 if data.get("success") else 1, text)
            return bool(data.get("success"))
        except Exception as err:
            self._save_task_result("插件卸载", False, -1, str(err))
            logger.error(f"AgentOpsAssistant 插件卸载执行失败：{err}")
            return False

    def run_update_preview(self) -> bool:
        data = self._build_update_status()
        text = self._format_update_status_text(data)
        self._save_task_result("更新状态预览", True, 0, text)
        return True

    def run_mp_update_check(self) -> bool:
        data = self._build_update_status()
        text = self._format_update_status_text(data)
        mp = data.get("moviepilot") or {}
        checks = mp.get("checks") or []
        errors = [f"{item.get('type') or '未知'}：{item.get('error')}" for item in checks if item.get("error")]
        if mp.get("version_error"):
            errors.append(f"本地版本：{mp.get('version_error')}")
        success = bool(checks) and not errors
        if mp.get("has_update") and self._mp_update_restart_confirm:
            self._dispatch_moviepilot_restart(data)
        if self._mp_update_notify and (mp.get("has_update") or errors):
            title = "MP 运维助手 - MoviePilot更新检查"
            if errors and not mp.get("has_update"):
                title = "MP 运维助手 - MoviePilot更新检查异常"
            self.post_message(mtype=self._notification_type(self._mp_update_notify_type), title=title, text=text)
        self._save_task_result("主程序更新检查", success, 0 if success else 1, text)
        return success

    def run_market_update(self) -> bool:
        try:
            data = self._build_market_update_status(apply=True)
            data["plugin_update"] = self._auto_update_installed_plugins(apply=True)
            text = self._format_market_update_text(data)
            pu = data.get("plugin_update") or {}
            notify_needed = data.get("has_update") or pu.get("updated") or pu.get("updatable") or pu.get("failed")
            if self._market_update_notify and notify_needed:
                self.post_message(mtype=self._notification_type(self._market_update_notify_type), title="MP 运维助手 - 插件库更新检查", text=text)
            self._save_task_result("插件库更新", bool(data.get("success")), 0 if data.get("success") else 1, text)
            return bool(data.get("success"))
        except Exception as err:
            self._save_task_result("插件库更新", False, -1, str(err))
            logger.error(f"AgentOpsAssistant 插件库更新检查失败：{err}")
            return False

    def run_backup(self) -> bool:
        try:
            data = self._create_agentops_backup()
            text = self._format_backup_status_text(data)
            if self._backup_notify:
                self.post_message(mtype=self._notification_type(self._backup_notify_type), title="MP 运维助手 - 自动备份完成", text=text)
            self._save_task_result("自动备份", bool(data.get("success")), 0 if data.get("success") else 1, text)
            return bool(data.get("success"))
        except Exception as err:
            self._save_task_result("自动备份", False, -1, str(err))
            logger.error(f"AgentOpsAssistant 自动备份执行失败：{err}")
            return False

    def _api_run_task(self, name: str, runner) -> Dict[str, Any]:
        try:
            success = bool(runner())
            return {"code": 0 if success else 1, "msg": f"{name}执行{'成功' if success else '失败'}，详情请查看插件日志。"}
        except Exception as err:
            try:
                self._save_task_result(name, False, -1, str(err))
            except Exception:
                pass
            logger.error(f"AgentOpsAssistant {name}执行异常：{err}")
            return {"code": 1, "msg": f"{name}执行失败：{err}"}

    def _build_daily_report_message(self, preview: bool = False) -> str:
        """复刻 locked-heartbeat-report fixed-v1 模板。"""
        return self._build_heartbeat_message(preview=preview)

    def _build_heartbeat_message(self, preview: bool = False) -> str:
        site_increment = self._get_site_increment_locked()
        site_health = self._get_site_health_locked()
        transfer_health = self._get_transfer_health_locked()
        subs = self._get_today_subscribe_updates_locked()
        downloader_health = self._get_downloader_health_locked()
        storage_health = self._get_storage_health_locked()
        today_downloads = self._get_today_downloads_locked()
        media_stats = self._get_media_stats_locked()

        lines = [
            self._daily_report_title(),
            self._daily_greeting_locked(),
            "",
            f"🕒 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        ]

        def section(enabled: bool, header: str, body: List[str]):
            if enabled and body:
                lines.extend(["", header, ""])
                lines.extend(self._report_body_lines(body))

        if self._report_version:
            lines.extend(["", "🤖 MoviePilot", ""])
            lines.extend(self._report_body_lines(self._version_report_lines()))
        section(self._report_site_status, "📡 站点状态", site_health)
        section(self._report_site_increment, "📈 站点增量", site_increment)
        # 「下载器/正在下载」与「今日下载」重复，统一只保留今日下载
        section(self._report_today_download, "📥 今日下载", today_downloads)
        section(self._report_transfer, "📦 入库整理", transfer_health)
        section(self._report_subscribe, "📺 订阅追新", ([f"⦁ {x}" for x in subs] if subs else ["⦁ 无"]))
        section(self._report_storage, "💾 存储空间", storage_health)
        section(self._report_media_stat, "🎬 媒体统计", media_stats)
        section(self._report_health and self._health_check_enabled, "🩺 健康巡查", self._get_health_report_locked(persist_missing=not preview))
        if self._report_summary:
            summary = self._get_summary_locked(site_health, transfer_health, downloader_health, storage_health)
            if summary:
                header = "🧾 今日摘要"
                first = str(summary[0] or "").strip()
                if first.startswith("⚠"):
                    header = "⚠️ 今日提醒"
                    summary = summary[1:]
                elif "今日摘要" in first:
                    summary = summary[1:]
                lines.extend(["", header, ""])
                lines.extend(self._report_body_lines(summary or ["⦁ 系统正常"]))
        return "\n".join(lines)

    @staticmethod
    def _daily_report_title() -> str:
        weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        now = datetime.now()
        return f"📮 MP 运维日报｜{now.strftime('%Y-%m-%d')} {weekdays[now.weekday()]}"

    @classmethod
    def _report_body_lines(cls, items: List[str]) -> List[str]:
        """将日报内容转成图标化数据条；短项横向排布，长项保留纵向。"""
        cleaned = [cls._report_visual_line(item) for item in (items or []) if str(item or "").strip()]
        cleaned = [line for line in cleaned if line]
        if not cleaned:
            return ["• 无"]
        compact: List[str] = []
        run: List[str] = []

        def flush_run():
            nonlocal run
            if run:
                compact.extend(cls._pack_report_pairs(run))
                run = []

        for text in cleaned:
            if len(text) <= 22:
                run.append(text)
            else:
                flush_run()
                compact.append(text)
        flush_run()
        return compact

    @classmethod
    def _pack_report_pairs(cls, items: List[str]) -> List[str]:
        pairs = [items[i:i + 2] for i in range(0, len(items), 2)]
        left_width = max((cls._display_width(pair[0]) for pair in pairs if len(pair) == 2), default=0)
        rows = []
        for pair in pairs:
            if len(pair) == 1:
                rows.append(pair[0])
            else:
                rows.append(f"{cls._pad_display(pair[0], left_width)} ｜ {pair[1]}")
        return rows

    @staticmethod
    def _display_width(text: str) -> int:
        width = 0
        for ch in str(text or ""):
            width += 1 if ch == "\u00a0" else (2 if ord(ch) > 127 else 1)
        return width

    @classmethod
    def _pad_display(cls, text: str, width: int) -> str:
        pad = max(0, width - cls._display_width(text))
        full, half = divmod(pad, 2)
        tail = ("　" * full) + ("\u00a0" if half else "")
        return f"{text}{tail}"

    @staticmethod
    def _report_visual_line(item: Any) -> str:
        text = str(item or "").strip()
        if text.startswith("- "):
            text = f"⦁ {text[2:].strip()}"
        if text.startswith("  - "):
            text = f"⦁ {text[4:].strip()}"
        text = text.replace("⦁ ", "• ").replace("⦁", "•").strip()
        body = text[2:].strip() if text.startswith("• ") else text

        version_match = re.match(r"当前版本：前端\s*(.*?)\s*/\s*后端\s*(.*)$", body)
        if version_match:
            return f"• 🖥 前端 {version_match.group(1)} ｜ ⚙ 后端 {version_match.group(2)}"

        if body.startswith("最新版本："):
            latest = body.replace("最新版本：", "", 1).strip()
            icon = "✅" if "已是最新" in latest else ("🆕" if "新版" in latest else "⚠")
            return f"• {icon} 最新 {latest}"

        status_match = re.match(r"(.+?)\s*\|\s*(.+)$", body)
        if status_match:
            name, status = status_match.group(1).strip(), status_match.group(2).strip()
            icon = "✅" if status == "正常" else ("⏳" if "过期" in status else "⚠")
            return f"• {name}：{icon} {status}"

        transfer_match = re.match(r"今日成功：(\d+)｜失败：(\d+)", body)
        if transfer_match:
            return f"• ✅ 成功 {transfer_match.group(1)} ｜ ❌ 失败 {transfer_match.group(2)}"

        if body.startswith("失败："):
            detail = body.replace("失败：", "", 1)
            if " - " in detail:
                title, reason = detail.split(" - ", 1)
                return f"• ❌ {title.strip()} ｜ {reason.strip()}"
            return f"• ❌ {detail.strip()}"

        if body.startswith("异常："):
            detail = body.replace("异常：", "", 1).strip()
            return f"• ⚠ {detail}"

        if body.startswith("今日下载："):
            value = body.replace("今日下载：", "", 1).strip()
            return "• 无" if value == "无" else f"• 📦 {value}"

        seed_match = re.match(r"(.+?)（做种：(.*?)）$", body)
        if seed_match:
            label, seed = seed_match.group(1).strip(), seed_match.group(2).strip()
            icon = "📺" if re.search(r"S\d{1,2}E", label, re.I) else "🎬"
            return f"• {icon} {label} ｜ 🌱 {seed}"

        if re.search(r"S\d{1,2}(?:E\d{1,4}|E\d{1,4}-E\d{1,4}|$)", body, re.I):
            return f"• 📺 {body}"

        if re.search(r"\(\d{4}\)", body):
            return f"• 🎬 {body}"

        if re.search(r"电影\s+\d+", body) and ("电视剧" in body or "剧集" in body or "用户" in body):
            parts = []
            for part in re.split(r"\s*｜\s*", body):
                part = part.strip()
                if part.startswith("电影 "):
                    parts.append("🎞 " + part)
                elif part.startswith("电视剧 "):
                    parts.append("📺 " + part)
                elif part.startswith("剧集 "):
                    parts.append("🎞 " + part)
                elif part.startswith("用户 "):
                    parts.append("👤 " + part)
                elif part:
                    parts.append(part)
            return f"• {' ｜ '.join(parts)}"

        storage_match = re.match(r"(.+?)：(.+)$", body)
        if storage_match and ("剩余" in body or "已用" in body):
            name, rest = storage_match.group(1).strip(), storage_match.group(2).strip()
            parts = []
            for part in re.split(r"\s*｜\s*", rest):
                part = part.strip()
                if not part:
                    continue
                plain = re.sub(r"^[🔴🟠🟡🟢]\s*", "", part)
                if part.startswith("剩余"):
                    continue
                if part.startswith("💽"):
                    parts.append(part)
                elif plain.startswith("已用"):
                    pct_match = re.search(r"(\d+)", part)
                    pct = int(pct_match.group(1)) if pct_match else 0
                    icon = "🔴" if pct >= 85 else ("🟠" if pct >= 70 else "🟢")
                    parts.append(f"{icon} {plain}")
                else:
                    parts.append(f"💽 {part}")
            return f"• {name}：{' ｜ '.join(parts)}"

        return text if text.startswith("• ") else f"• {body}"

    def _version_report_lines(self) -> List[str]:
        """当前/最新版本 + 按检查结果区分话术（已是最新 / 有新版 / 检查失败）。"""
        local = self._get_local_versions()
        fe = local.get("frontend_version") or "未知"
        be = local.get("backend_version") or "未知"
        lines = [f"⦁ 当前版本：前端 {fe} / 后端 {be}"]
        try:
            check = self._check_one_release("后端", "https://api.github.com/repos/jxxghp/MoviePilot/releases", be)
        except Exception as err:
            check = {"error": str(err)}
        latest = check.get("latest_version") or ""
        err = check.get("error") or ""
        if err or not latest:
            lines.append(f"⦁ 最新版本：暂时查不到（{err or '无响应'}），稍后再看")
        elif check.get("has_update"):
            lines.append(f"⦁ 最新版本：后端 {latest} —— 有新版，{self._daily_report_greeting}记得抽空更新")
        else:
            lines.append(f"⦁ 最新版本：{latest}，已是最新 ✅")
        return lines

    @staticmethod
    def _normalize_version(value: Any) -> str:
        text = str(value or "").strip()
        return text[1:] if text.startswith("v") else text

    @staticmethod
    def _backend_version_value() -> str:
        try:
            from version import APP_VERSION
            return str(APP_VERSION or "")
        except Exception:
            return ""

    @staticmethod
    def _frontend_backend_version_line() -> str:
        try:
            from version import APP_VERSION, FRONTEND_VERSION
            # 显示格式：前端版本 / 后端版本（后端版本可能有 -1 等构建号后缀）
            return f"{FRONTEND_VERSION} / {APP_VERSION}"
        except Exception as err:
            return f"版本读取失败：{err}"

    def _github_latest_v2(self) -> str:
        version = self._backend_version_value()
        return version if version.startswith("v") else f"v{version}"

    def _daily_greeting_locked(self) -> str:
        hour = datetime.now().hour
        if 0 <= hour <= 5:
            part = "凌晨"
        elif 6 <= hour <= 11:
            part = "早上"
        elif 12 <= hour <= 17:
            part = "下午"
        else:
            part = "晚上"
        who = (self._daily_report_greeting or "少爷").strip() or "少爷"
        return f"{who}，{part}好。给你送上今天的心跳播报。"

    @staticmethod
    def _today_prefix() -> str:
        return datetime.now().strftime("%Y-%m-%d")

    @staticmethod
    def _normalize_day(value: Any) -> str:
        if value in (None, ""):
            return ""
        try:
            if hasattr(value, "strftime"):
                return value.strftime("%Y-%m-%d")
            text = str(value).strip()
            match = re.search(r"(\d{4})-(\d{1,2})-(\d{1,2})", text)
            if match:
                year, month, day = match.groups()
                return f"{int(year):04d}-{int(month):02d}-{int(day):02d}"
            return text[:10]
        except Exception:
            return str(value or "").strip()[:10]

    def _today_transfer_rows_locked(self) -> List[Any]:
        try:
            from app.db.transferhistory_oper import TransferHistoryOper
            return TransferHistoryOper().list_by_date(f"{self._today_prefix()} 00:00:00") or []
        except Exception:
            return []

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
        rows = self._today_transfer_rows_locked()
        failed_rows = [r for r in rows if not getattr(r, "status", False)]
        if not failed_rows:
            return ["⦁ 无"]
        items = []
        for r in failed_rows:
            title = getattr(r, "title", None) or "未命名"
            errmsg = str(getattr(r, "errmsg", None) or getattr(r, "message", None) or "").strip()
            items.append(f"⦁ 失败：{title} - {errmsg[:36]}" if errmsg else f"⦁ 失败：{title}")
        return items

    @staticmethod
    def _find_site_userdata_snapshot(rows: List[Any], name: str, domain: Optional[str] = None) -> Optional[Any]:
        valid_rows = [row for row in (rows or []) if row and not str(getattr(row, "err_msg", None) or "").strip()]
        domain = str(domain or "").strip()
        if domain:
            for row in valid_rows:
                if str(getattr(row, "domain", None) or "").strip() == domain:
                    return row
            for row in valid_rows:
                if not str(getattr(row, "domain", None) or "").strip() and getattr(row, "name", None) == name:
                    return row
            return None
        if name:
            for row in valid_rows:
                if getattr(row, "name", None) == name:
                    return row
        return None

    @staticmethod
    def _site_userdata_number(row: Any, key: str) -> Optional[int]:
        value = getattr(row, key, None)
        if value in (None, ""):
            return None
        try:
            return int(float(value))
        except Exception:
            return None

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
            upload_delta = max(0, current_upload - previous_upload)
        if current_download is not None and previous_download is not None and previous_download > 0:
            download_delta = max(0, current_download - previous_download)
        return upload_delta, download_delta

    def _get_site_increment_locked(self) -> List[str]:
        try:
            from app.db.site_oper import SiteOper
            site_oper = SiteOper()
            latest_data = site_oper.get_userdata_latest() or []
            active_domains = {site.domain for site in (site_oper.list_active() or []) if getattr(site, "domain", None)}
            latest_data = [data for data in latest_data if data and getattr(data, "domain", None) in active_domains]
            if not latest_data:
                return ["⦁ 无"]
            today = self._today_prefix()
            result = []
            previous_cache: Dict[str, List[Any]] = {}
            for current in sorted(latest_data, key=lambda row: (getattr(row, "name", None) or getattr(row, "domain", None) or "").lower()):
                site_name = getattr(current, "name", None) or getattr(current, "domain", None) or "未知站点"
                site_domain = getattr(current, "domain", None)
                current_day = self._normalize_day(getattr(current, "updated_day", None))
                err_msg = str(getattr(current, "err_msg", None) or "").strip()
                if current_day != today:
                    continue
                if err_msg:
                    result.append(f"⦁ {site_name}：异常 - {err_msg}")
                    continue
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
                    continue
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
            return result or ["⦁ 无"]
        except Exception as e:
            return [f"⦁ 异常 - {e}"]

    @staticmethod
    def _format_metric_number(value: Any) -> str:
        try:
            num = float(value)
            if num.is_integer():
                return f"{int(num):,}"
            return f"{num:,.1f}".rstrip("0").rstrip(".")
        except Exception:
            return str(value)

    def _site_increment_snapshot(self) -> Dict[str, Any]:
        """站点上传/下载增量快照，优先今日；今日未生成时回退到最近有效快照。"""
        result = {"date": self._today_prefix(), "basis": "today", "sites": [], "upload_total": 0, "download_total": 0}
        try:
            from app.db.site_oper import SiteOper
            site_oper = SiteOper()
            latest_data = site_oper.get_userdata_latest() or []
            active_domains = {s.domain for s in (site_oper.list_active() or []) if getattr(s, "domain", None)}
            latest_data = [
                d for d in latest_data
                if d and getattr(d, "domain", None) in active_domains and not str(getattr(d, "err_msg", None) or "").strip()
            ]
            today = self._today_prefix()
            days = sorted({self._normalize_day(getattr(d, "updated_day", None)) for d in latest_data if self._normalize_day(getattr(d, "updated_day", None))}, reverse=True)
            basis_day = today if any(day == today for day in days) else (days[0] if days else today)
            result["date"] = basis_day
            result["basis"] = "today" if basis_day == today else "latest"
            if not latest_data:
                return result
            previous_cache: Dict[str, List[Any]] = {}
            out: List[Dict[str, Any]] = []
            for current in latest_data:
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
                    continue
                up, dl = delta
                if up == 0 and dl == 0:
                    continue
                out.append({"name": name, "upload": up, "download": dl})
            result["sites"] = out
            result["upload_total"] = sum(int(d.get("upload", 0)) for d in out)
            result["download_total"] = sum(int(d.get("download", 0)) for d in out)
        except Exception as err:
            logger.warning(f"AgentOpsAssistant 站点增量数据获取失败：{err}")
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
            latest = [row for row in latest if row and getattr(row, "domain", None) in active_domains]
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

    def _downloader_overview_data(self) -> List[Dict[str, Any]]:
        """各下载器当前下载中任务数与上下行速度（结构化），供仪表盘活动种子概览。"""
        out: List[Dict[str, Any]] = []
        try:
            from app.chain.download import DownloadChain
            stats: Dict[str, Dict[str, Any]] = {}
            for t in (DownloadChain().downloading() or []):
                name = getattr(t, "downloader", None) or "未知"
                s = stats.setdefault(name, {"name": name, "count": 0, "dl_speed": 0, "up_speed": 0})
                s["count"] += 1
                s["dl_speed"] += int(getattr(t, "dlspeed", 0) or 0)
                s["up_speed"] += int(getattr(t, "upspeed", 0) or 0)
            out = list(stats.values())
        except Exception as err:
            logger.warning(f"AgentOpsAssistant 下载器概览获取失败：{err}")
        return out

    def run_downloader_tag(self) -> bool:
        """按种子 tracker 站点为种子补打标签（移植自 hotlcc 下载器助手；幂等，已打的跳过）。"""
        name = "种子打标签"
        try:
            from app.helper.downloader import DownloaderHelper
            from app.utils.string import StringUtils
            helper = DownloaderHelper()
            names = self._dltag_downloaders or [getattr(c, "name", None) for c in (helper.get_configs() or {}).values() if getattr(c, "name", None)]
            services = helper.get_services(name_filters=names) or {}
            tagged = 0
            for _dn, svc in services.items():
                inst = getattr(svc, "instance", None)
                if not inst or (hasattr(inst, "is_inactive") and inst.is_inactive()):
                    continue
                is_qb = str(getattr(getattr(svc, "config", None), "type", "")).lower() == "qbittorrent"
                try:
                    torrents, error = inst.get_torrents()
                except Exception:
                    continue
                if error:
                    continue
                qb_groups: Dict[str, List[str]] = {}
                for tor in (torrents or []):
                    if is_qb:
                        site = StringUtils.get_url_sld(getattr(tor, "tracker", "") or "")
                        if not site:
                            continue
                        tag = (self._dltag_prefix or "") + site
                        existing = [x.strip() for x in str(getattr(tor, "tags", "") or "").split(",")]
                        if tag in existing:
                            continue
                        qb_groups.setdefault(tag, []).append(tor.hash)
                    else:
                        trackers = getattr(tor, "trackers", None) or []
                        site = trackers[0].get("sitename") if trackers else ""
                        if not site:
                            continue
                        tag = (self._dltag_prefix or "") + site
                        labels = list(getattr(tor, "labels", []) or [])
                        if tag in labels:
                            continue
                        try:
                            inst.set_torrent_tag(ids=tor.hashString, tags=[tag], org_tags=labels)
                            tagged += 1
                        except Exception:
                            pass
                for tag, hashes in qb_groups.items():
                    try:
                        inst.set_torrents_tag(ids=hashes, tags=[tag])
                        tagged += len(hashes)
                    except Exception:
                        pass
            text = f"已为 {tagged} 个种子按站点补打标签" if tagged else "没有需要补打标签的种子（均已打标签或无 tracker 站点信息）"
            self._save_task_result(name, True, 0, text)
            if self._dltag_notify and tagged:
                self.post_message(mtype=self._notification_type(self._dltag_notify_type), title="MP 运维助手 - 种子打标签", text=text)
            return True
        except Exception as err:
            self._save_task_result(name, False, -1, str(err))
            logger.error(f"AgentOpsAssistant 种子打标签失败：{err}")
            return False

    @staticmethod
    def _format_duration(seconds: Any) -> str:
        try:
            seconds = int(seconds or 0)
            return f"{seconds // 3600}时{(seconds % 3600) // 60:02d}分"
        except Exception:
            return "0时00分"

    def _get_media_stats_locked(self) -> List[str]:
        """媒体统计（电影/电视剧/剧集/用户）——尝试媒体服务器统计接口，取不到则提示。"""
        try:
            # MoviePilot 官方仪表盘同款：app.chain.dashboard.DashboardChain.media_statistic()
            from app.chain.dashboard import DashboardChain
            stats = DashboardChain().media_statistic() or []
            if not stats:
                return ["⦁ 未取到（媒体服务器未配置）"]
            stat = {
                "movie_count": sum(int(getattr(s, "movie_count", 0) or 0) for s in stats),
                "tv_count": sum(int(getattr(s, "tv_count", 0) or 0) for s in stats),
                "episode_count": sum(int(getattr(s, "episode_count", 0) or 0) for s in stats),
                "user_count": sum(int(getattr(s, "user_count", 0) or 0) for s in stats),
            }

            def _g(obj, *keys):
                for k in keys:
                    v = obj.get(k) if isinstance(obj, dict) else getattr(obj, k, None)
                    if v is not None:
                        return v
                return None

            movie = _g(stat, "movie_count", "MovieCount", "movies", "movie")
            tv = _g(stat, "tv_count", "SeriesCount", "series", "tvs", "tv")
            ep = _g(stat, "episode_count", "EpisodeCount", "episodes", "episode")
            user = _g(stat, "user_count", "UserCount", "users", "user")
            parts = []
            if movie is not None:
                parts.append(f"电影 {movie}")
            if tv is not None:
                parts.append(f"电视剧 {tv}")
            if ep is not None:
                parts.append(f"剧集 {ep}")
            if user is not None:
                parts.append(f"用户 {user}")
            return [f"⦁ {' ｜ '.join(parts)}"] if parts else ["⦁ 未取到"]
        except Exception as e:
            return [f"⦁ 媒体统计异常：{e}"]

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

    def _downloader_seed_map(self) -> Dict[str, int]:
        """汇总所有下载器的 {种子hash: 做种秒数}，供入库记录的 download_hash 互相印证做种时长。
        做种时长口径对齐官方“自动删种(TorrentRemover)”插件：优先用完成时间算 now−完成
        （qb completion_on / tr date_done，未完成回退 added_on/date_added），取不到再退化到
        seeding_time 字段。兼容 qbittorrent 与 transmission 的字段命名。"""
        seed_map: Dict[str, int] = {}
        try:
            from app.helper.downloader import DownloaderHelper
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
            comp = _f(t, "completion_on", "completionOn")          # qb 完成时间(秒)
            if comp is not None and _since(comp):
                return _since(comp)
            dd = _f(t, "date_done", "done_date", "date_added", "added_date")  # tr 完成/添加(datetime)
            if dd is not None and _since(dd):
                return _since(dd)
            add = _f(t, "added_on", "addedDate")                   # qb 添加时间(秒)回退
            if add is not None and _since(add):
                return _since(add)
            st = _f(t, "seeding_time", "seedingTime", "seconds_seeding", "secondsSeeding")  # 兜底
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

    # ===== 自动删种（功能移植自 jxxghp/MoviePilot-Plugins「自动删种」TorrentRemover，适配本插件）=====
    def api_run_seed_clean(self) -> Dict[str, Any]:
        return self._api_run_task("自动删种", self.run_seed_clean)

    def api_downloaders(self) -> Dict[str, Any]:
        """已配置下载器列表，供自动删种下拉选择。"""
        try:
            from app.helper.downloader import DownloaderHelper
            items = []
            for conf in (DownloaderHelper().get_configs() or {}).values():
                nm = getattr(conf, "name", None)
                if nm:
                    items.append({"value": nm, "title": nm})
            items.sort(key=lambda x: x["title"])
            return {"code": 0, "data": items}
        except Exception as err:
            logger.error(f"下载器列表获取失败：{err}")
            return {"code": 1, "msg": f"下载器列表获取失败：{err}", "data": []}

    def api_mediaservers(self) -> Dict[str, Any]:
        """已配置媒体服务器列表，供媒体库通知按服务器过滤。"""
        try:
            from app.helper.mediaserver import MediaServerHelper
            items = []
            for conf in (MediaServerHelper().get_configs() or {}).values():
                nm = getattr(conf, "name", None)
                if nm:
                    items.append({"value": nm, "title": nm})
            items.sort(key=lambda x: x["title"])
            return {"code": 0, "data": items}
        except Exception as err:
            logger.error(f"媒体服务器列表获取失败：{err}")
            return {"code": 1, "msg": f"媒体服务器列表获取失败：{err}", "data": []}

    def api_subfill_clear_history(self) -> Dict[str, Any]:
        return self._api_run_task("清理填充历史", self.run_subfill_clear_history)

    def api_subfill_clear_handled(self) -> Dict[str, Any]:
        return self._api_run_task("清理已处理", self.run_subfill_clear_handled)

    def api_site_stat_chart(self) -> Dict[str, Any]:
        """今日各站点上传/下载增量，供仪表盘饼图。"""
        try:
            return {"code": 0, "data": self._site_increment_snapshot()}
        except Exception as err:
            logger.error(f"站点统计图数据获取失败：{err}")
            return {"code": 1, "msg": str(err), "data": {"date": "", "basis": "today", "sites": [], "upload_total": 0, "download_total": 0}}

    def api_run_site_stat(self) -> Dict[str, Any]:
        """刷新站点数据统计：站点快照来自 MoviePilot SiteOper，这里重新汇总并记录一次任务结果。"""
        try:
            chart = self.api_site_stat_chart()
            if (chart or {}).get("code", 0) != 0:
                msg = (chart or {}).get("msg") or "站点统计图数据获取失败"
                payload = (chart or {}).get("data") or {"date": "", "basis": "today", "sites": [], "upload_total": 0, "download_total": 0}
                self._save_task_result("站点数据统计", False, 1, msg)
                return {"code": 1, "msg": msg, "data": payload}
            payload = chart.get("data") or {}
            site_count = len(payload.get("sites") or [])
            upload = self._format_bytes(payload.get("upload_total", 0))
            download = self._format_bytes(payload.get("download_total", 0))
            label = "今日" if payload.get("basis") != "latest" else f"最近快照 {payload.get('date') or ''}".strip()
            text = f"已刷新 {site_count} 个站点｜{label}｜上传 {upload}｜下载 {download}" if site_count else "已刷新站点数据，暂无可用增量"
            self._save_task_result("站点数据统计", True, 0, text)
            return {"code": 0, "msg": text, "data": payload}
        except Exception as err:
            self._save_task_result("站点数据统计", False, -1, str(err))
            logger.error(f"站点数据统计刷新失败：{err}")
            return {"code": 1, "msg": f"站点数据统计刷新失败：{err}", "data": {"date": "", "basis": "today", "sites": [], "upload_total": 0, "download_total": 0}}

    def api_run_downloader_tag(self) -> Dict[str, Any]:
        return self._api_run_task("种子打标签", self.run_downloader_tag)

    def api_downloader_overview(self) -> Dict[str, Any]:
        return {"code": 0, "data": {"downloaders": self._downloader_overview_data()}}

    def run_seed_clean(self) -> bool:
        """按规则在所选下载器中暂停/删除种子。默认动作为暂停，安全优先。"""
        name = "自动删种"
        if not self._seedclean_downloaders:
            text = "未执行：请先在配置页选择下载器。"
            self._save_task_result(name, False, 2, text)
            if self._seedclean_notify:
                self.post_message(mtype=self._notification_type(self._seedclean_notify_type), title="MP 运维助手 - 自动删种未执行", text=text)
            return False
        # 安全：未设置任何筛选条件时不处理，避免误伤全部种子
        if not self._seedclean_has_any_condition():
            text = "未执行：未设置任何筛选条件（大小/分享率/做种时间/上传速度/标签/路径/Tracker/状态/分类），为避免误删已跳过。"
            self._save_task_result(name, False, 2, text)
            if self._seedclean_notify:
                self.post_message(mtype=self._notification_type(self._seedclean_notify_type), title="MP 运维助手 - 自动删种未执行", text=text)
            return False
        try:
            summary = self._seed_clean_run()
            text = "\n".join(summary) if summary else "本次没有符合条件的种子。"
            if self._seedclean_notify and summary:
                self.post_message(mtype=self._notification_type(self._seedclean_notify_type), title="MP 运维助手 - 自动删种", text=text)
            self._save_task_result(name, True, 0, text)
            return True
        except Exception as err:
            self._save_task_result(name, False, -1, str(err))
            logger.error(f"AgentOpsAssistant 自动删种执行失败：{err}")
            return False

    def _seedclean_has_any_condition(self) -> bool:
        return any([
            self._seedclean_size, self._seedclean_ratio, self._seedclean_time, self._seedclean_upspeed,
            self._seedclean_labels, self._seedclean_pathkeywords, self._seedclean_trackerkeywords,
            self._seedclean_errorkeywords, self._seedclean_torrentstates, self._seedclean_torrentcategorys,
        ])

    def _seed_clean_run(self) -> List[str]:
        from app.helper.downloader import DownloaderHelper
        from app.utils.string import StringUtils
        services = DownloaderHelper().get_services(name_filters=self._seedclean_downloaders) or {}
        verb_map = {"pause": "暂停", "delete": "删除种子", "deletefile": "删除种子和文件"}
        lines: List[str] = []
        for dl_name in self._seedclean_downloaders:
            service = services.get(dl_name)
            inst = getattr(service, "instance", None) if service else None
            if not inst:
                lines.append(f"⦁ {dl_name}：未找到下载器实例，跳过")
                continue
            try:
                if hasattr(inst, "is_inactive") and inst.is_inactive():
                    lines.append(f"⦁ {dl_name}：下载器未连接，跳过")
                    continue
            except Exception:
                pass
            dtype = str(getattr(getattr(service, "config", None), "type", "") or "")
            targets = self._seed_remove_targets(inst, dtype)
            if not targets:
                continue
            act = self._seedclean_action
            done = 0
            for t in targets:
                tid = t.get("id")
                try:
                    if act == "pause":
                        inst.stop_torrents(ids=[tid])
                    elif act == "delete":
                        inst.delete_torrents(delete_file=False, ids=[tid])
                    elif act == "deletefile":
                        inst.delete_torrents(delete_file=True, ids=[tid])
                    else:
                        continue
                    done += 1
                    logger.info(f"自动删种 {verb_map.get(act, act)}：{t.get('name')}")
                except Exception as e:
                    logger.warning(f"自动删种处理失败 {t.get('name')}：{e}")
            lines.append(f"⦁ {dl_name}：{verb_map.get(act, act)} {done} 个")
            for t in targets[:8]:
                lines.append(f"  - {t.get('name')}｜{StringUtils.str_filesize(t.get('size'))}｜{t.get('site') or ''}")
        return lines

    def _seed_remove_targets(self, inst, dtype: str) -> List[Dict[str, Any]]:
        from app.utils.string import StringUtils
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
            return []
        if error_flag:
            return []
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
                        plus.append({"id": pid, "name": pname, "site": psite, "size": psize})
            result.extend(plus)
        return result

    def _seed_match_qb(self, torrent) -> Any:
        """qBittorrent 种子条件匹配，命中返回精简 dict，否则 None。任意异常按不匹配处理（安全方向）。"""
        from app.utils.string import StringUtils
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
            date_done = torrent.date_done or torrent.date_added
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
            items.append(f"⦁ {name}：💽 {self._format_bytes(used)}/{self._format_bytes(total)} ｜ {icon} 已用 {pct:.0f}%{risk}")
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

    def _get_summary_locked(self, site_health: List[str], transfer_health: List[str], downloads: List[str], storage_health: List[str]) -> List[str]:
        warnings = []
        for line in site_health + transfer_health + downloads + storage_health:
            clean = str(line or "")
            risky = (
                "未取到" in clean
                or "空间偏紧" in clean
                or ("失败：" in clean and "失败：0" not in clean)
                or ("异常" in clean and "异常 0" not in clean)
                or ("过期" in clean and "过期 0" not in clean)
            )
            if risky:
                warnings.append(clean.replace("⦁ ", "⦁ "))
        if warnings:
            return ["⚠️ 今日提醒"] + warnings[:5]
        return ["✅ 今日摘要", "⦁ 系统正常", "⦁ 站点快照正常", "⦁ 无失败转移", "⦁ 下载器无异常"]

    def _get_today_subscribe_updates_locked(self) -> List[str]:
        items = self._load_subscribereminder_today_locked()
        if items:
            return self._unique_keep_order(items)
        return self._load_subscribereminder_today_fallback_locked()

    @staticmethod
    def _unique_keep_order(items: List[Any]) -> List[str]:
        seen = set(); result = []
        for item in items or []:
            text = str(item or "").strip()
            if text and text not in seen:
                seen.add(text); result.append(text)
        return result

    def _load_subscribereminder_today_locked(self) -> List[str]:
        try:
            sub_file = Path("/config/agent/runtime/cache/subscribereminder_last_push.json")
            if not sub_file.exists():
                return []
            data = json.loads(sub_file.read_text(encoding="utf-8"))
            if not str(data.get("time") or "").startswith(self._today_prefix()):
                return []
            lines = []
            for raw in str(data.get("text") or "").splitlines():
                s = raw.strip()
                if not s:
                    continue
                lines.append(s.lstrip("📺︎").lstrip("📺").strip())
            return lines
        except Exception:
            return []

    def _load_subscribereminder_today_fallback_locked(self) -> List[str]:
        try:
            from app.chain.media import MediaChain
            from app.chain.tmdb import TmdbChain
            from app.db.subscribe_oper import SubscribeOper
            from app.schemas.types import MediaType
            subscribe_oper = SubscribeOper(); tmdb = TmdbChain(); media = MediaChain()
            current_date = datetime.now().date().strftime("%Y-%m-%d")
            items = []
            for subscribe in subscribe_oper.list() or []:
                sub_type = str(getattr(subscribe, "type", "") or "").strip().lower()
                year = getattr(subscribe, "year", None) or "未知年份"
                name = getattr(subscribe, "name", None) or "未命名订阅"
                if sub_type in {"电视剧", "tv"}:
                    tmdbid = getattr(subscribe, "tmdbid", None); season = getattr(subscribe, "season", None)
                    if not tmdbid or season in (None, ""):
                        continue
                    try:
                        season_num = int(season)
                    except Exception:
                        continue
                    episodes_info = tmdb.tmdb_episodes(tmdbid=tmdbid, season=season_num, episode_group=getattr(subscribe, "episode_group", None)) or []
                    episodes = []
                    for episode in episodes_info:
                        if episode and getattr(episode, "air_date", None) and str(episode.air_date) == current_date:
                            episode_number = getattr(episode, "episode_number", None)
                            if episode_number:
                                episodes.append(int(episode_number))
                    if episodes:
                        items.append(f"{name} ({year}) S{season_num:02d}{self._episode_ranges(sorted(set(episodes)))}")
                    continue
                if sub_type in {"电影", "movie"}:
                    tmdbid = getattr(subscribe, "tmdbid", None)
                    if not tmdbid:
                        continue
                    mediainfo = media.recognize_media(tmdbid=tmdbid, mtype=MediaType.MOVIE)
                    if mediainfo and str(getattr(mediainfo, "release_date", None) or "") == current_date:
                        items.append(f"{name} ({year})")
            return self._unique_keep_order(items)
        except Exception:
            return []

    def _build_update_status(self) -> Dict[str, Any]:
        result = {"safe_mode": True, "note": "本插件直接检查 MoviePilot 后端/前端 release；默认只通知，不重启。", "moviepilot": {}, "plugin_market": self._build_market_status()}
        local = self._get_local_versions()
        result["moviepilot"].update(local)
        checks = []
        if "后端" in self._mp_update_types:
            checks.append(self._check_one_release("后端", "https://api.github.com/repos/jxxghp/MoviePilot/releases", local.get("backend_version")))
        if "前端" in self._mp_update_types:
            checks.append(self._check_one_release("前端", "https://api.github.com/repos/jxxghp/MoviePilot-Frontend/releases", local.get("frontend_version")))
        result["moviepilot"]["checks"] = checks
        result["moviepilot"]["has_update"] = any(x.get("has_update") for x in checks)
        result["moviepilot"]["notify"] = self._mp_update_notify
        result["moviepilot"]["restart_confirm"] = self._mp_update_restart_confirm
        return result

    @staticmethod
    def _dispatch_moviepilot_restart(data: Dict[str, Any]) -> None:
        mp = data.setdefault("moviepilot", {})
        try:
            from app.helper.system import SystemHelper
            SystemHelper.restart()
            mp["restart_dispatched"] = True
        except Exception as err:
            mp["restart_error"] = str(err)

    @staticmethod
    def _get_local_versions() -> Dict[str, Any]:
        data = {}
        try:
            from version import APP_VERSION, FRONTEND_VERSION
            data.update({"backend_version": str(APP_VERSION), "frontend_version": str(FRONTEND_VERSION)})
        except Exception as err:
            data["version_error"] = str(err)
        return data

    @staticmethod
    def _version_nums(value: Any) -> List[int]:
        return [int(x) for x in re.findall(r"\d+", str(value or ""))]

    def _check_one_release(self, label: str, url: str, local_version: Any) -> Dict[str, Any]:
        item = {"type": label, "local_version": str(local_version or "未知"), "latest_version": "", "has_update": False, "error": ""}
        try:
            response = RequestUtils(proxies=settings.PROXY, headers=settings.GITHUB_HEADERS).get_res(url)
            if not response:
                item["error"] = "未获取到 release 响应"
                return item
            releases = response.json() or []
            v2 = [r for r in releases if re.match(r"^v2\.", str(r.get("tag_name", "")))]
            if not v2:
                item["error"] = "未找到 v2 release"
                return item
            latest = sorted(v2, key=lambda r: self._version_nums(r.get("tag_name")))[-1]
            latest_version = str(latest.get("tag_name") or "")
            item.update({"latest_version": latest_version, "published_at": latest.get("published_at"), "body": (latest.get("body") or "")[:1000]})
            if self._version_nums(latest_version) > self._version_nums(local_version):
                item["has_update"] = True
        except Exception as err:
            item["error"] = str(err)
        return item

    @staticmethod
    def _format_update_status_text(data: Dict[str, Any]) -> str:
        mp = data.get("moviepilot") or {}
        lines = ["🔄 MoviePilot 更新检查（MP运维助手直接接替）", f"⦁ 后端本地：{mp.get('backend_version', '未知')}", f"⦁ 前端本地：{mp.get('frontend_version', '未知')}"]
        for item in mp.get("checks") or []:
            status = "有更新" if item.get("has_update") else "无更新"
            if item.get("error"):
                status = f"异常：{item.get('error')}"
            lines.append(f"⦁ {item.get('type')}：{status}｜最新 {item.get('latest_version') or '未知'}")
        if data.get("plugin_market"):
            lines.append(f"⦁ 插件库更新：{data['plugin_market'].get('note')}")
        return "\n".join(lines)

    def _build_market_status(self) -> Dict[str, Any]:
        settings_markets = self._valid_markets_list(settings.PLUGIN_MARKET)
        last = self.get_data("last_market_update") or {}
        return {"status": "已直接接替", "note": "本插件直接检查插件库记录，不依赖 原插件库更新推送插件。", "enabled": self._market_update_enabled, "interval": self._market_update_interval, "settings_count": len(settings_markets), "last_update": last.get("time"), "last_wiki_count": len(last.get("wiki_markets") or [])}

    def _build_market_update_status(self, apply: bool = False) -> Dict[str, Any]:
        wiki_markets = self._fetch_wiki_markets()
        settings_markets = self._valid_markets_list(settings.PLUGIN_MARKET)
        blacklist = set(self._valid_markets_list(self._market_update_blacklist))
        other_markets = [x for x in settings_markets if x not in wiki_markets]
        full_markets = self._dedupe(wiki_markets + other_markets)
        write_markets = [x for x in full_markets if x not in blacklist]
        last = self.get_data("last_market_update") or {}
        last_wiki = self._valid_markets_list(last.get("wiki_markets") or [])
        new_markets = [x for x in wiki_markets if x not in last_wiki and x not in settings_markets]
        has_update = set(wiki_markets) != set(last_wiki) or bool(new_markets)
        result = {"success": True, "dry_run": not apply, "has_update": has_update, "wiki_markets": wiki_markets, "settings_markets": settings_markets, "other_markets": other_markets, "blacklist": sorted(blacklist), "write_markets": write_markets, "new_markets": new_markets, "settings_written": False, "env_written": False, "write_settings_enabled": self._market_update_write_settings, "write_env_enabled": self._market_update_write_env}
        if apply:
            if self._market_update_write_settings:
                settings.PLUGIN_MARKET = ",".join(write_markets)
                result["settings_written"] = True
            if self._market_update_write_env:
                self._write_app_env_key("PLUGIN_MARKET", ",".join(write_markets))
                result["env_written"] = True
            self.save_data("last_market_update", {"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "wiki_markets": wiki_markets, "settings_markets": settings_markets, "new_markets": new_markets, "has_update": has_update})
        return result

    def _fetch_wiki_markets(self) -> List[str]:
        url = self._market_update_wiki_url or "https://wiki.movie-pilot.org/zh/plugin"
        response = RequestUtils(proxies=settings.PROXY, timeout=15).get_res(url=url)
        if not response or response.status_code != 200:
            raise RuntimeError(f"插件库记录页面获取失败：{getattr(response, 'status_code', 'no_response')}")
        text = response.text or ""
        urls = re.findall(r"https?://[^\s\"'<>]+", text)
        markets = [u for u in urls if ("github" in u.lower() or "gitee" in u.lower() or "gitlab" in u.lower() or u.endswith("/"))]
        return self._valid_markets_list(self._dedupe(markets))

    @staticmethod
    def _valid_markets_list(value: Any) -> List[str]:
        raw = []
        if not value:
            return []
        if isinstance(value, str):
            raw = [x.strip() for x in value.split(",")]
        elif isinstance(value, dict):
            raw = [str(v).strip() for v in value.values()]
        elif isinstance(value, list):
            for item in value:
                raw.extend(AgentOpsAssistant._valid_markets_list(item))
        else:
            raw = [str(value).strip()]
        result = []
        for item in raw:
            if not item:
                continue
            result.append(item if item.endswith("/") else item + "/")
        return AgentOpsAssistant._dedupe(result)

    @staticmethod
    def _dedupe(items: List[str]) -> List[str]:
        seen = set()
        result = []
        for item in items or []:
            if item and item not in seen:
                seen.add(item)
                result.append(item)
        return result

    @staticmethod
    def _write_app_env_key(key: str, value: str):
        env_path = Path(settings.CONFIG_PATH) / "app.env"
        lines = []
        if env_path.exists():
            lines = env_path.read_text(encoding="utf-8", errors="ignore").splitlines()
        prefix = key + "="
        replaced = False
        out = []
        for line in lines:
            if line.startswith(prefix):
                out.append(f"{key}={value}")
                replaced = True
            else:
                out.append(line)
        if not replaced:
            out.append(f"{key}={value}")
        env_path.write_text("\n".join(out) + "\n", encoding="utf-8")

    @staticmethod
    def _format_market_update_text(data: Dict[str, Any]) -> str:
        lines = [
            "🧩 插件库更新检查（MP运维助手直接接替）",
            f"⦁ Wiki记录：{len(data.get('wiki_markets') or [])} 个",
            f"⦁ 当前配置：{len(data.get('settings_markets') or [])} 个",
            f"⦁ 第三方保留：{len(data.get('other_markets') or [])} 个",
            f"⦁ 黑名单：{len(data.get('blacklist') or [])} 个",
            f"⦁ 新发现：{len(data.get('new_markets') or [])} 个",
            f"⦁ 写入当前配置：{'已执行' if data.get('settings_written') else '未执行'}",
            f"⦁ 写入 app.env：{'已执行' if data.get('env_written') else '未执行'}",
        ]
        for url in (data.get('new_markets') or [])[:5]:
            lines.append(f"⦁ 新库：{url}")
        pu = data.get("plugin_update") or {}
        if pu:
            if pu.get("error"):
                lines.append(f"⦁ 插件自动更新：{pu['error']}")
            elif pu.get("auto_install"):
                lines.append(f"⦁ 插件自动更新：已更新 {len(pu.get('updated') or [])}｜失败 {len(pu.get('failed') or [])}｜跳过 {len(pu.get('skipped') or [])}")
                for it in (pu.get("updated") or [])[:6]:
                    extra = f"｜{it['history']}" if it.get("history") else ""
                    lines.append(f"  ✓ {it['name']}：v{it['old']} → v{it['new']}{extra}")
                for it in (pu.get("failed") or [])[:5]:
                    lines.append(f"  ✗ {it['name']}：{it.get('msg')}")
                for it in (pu.get("skipped") or [])[:5]:
                    lines.append(f"  – {it['name']}：跳过（{it.get('reason')}）")
            elif pu.get("updatable"):
                lines.append(f"⦁ 发现可更新插件：{len(pu['updatable'])} 个（未开启自动安装，仅提醒）")
                for it in pu["updatable"][:8]:
                    lines.append(f"  - {it['name']}：v{it['old']} → v{it['new']}")
        return "\n".join(lines)

    def _auto_update_installed_plugins(self, apply: bool = True) -> Dict[str, Any]:
        """检查已安装插件是否有新版（移植自 thsrite/PluginAutoUpdate，适配本插件）。
        开启“自动安装”且 apply 时下载安装新版并重载；否则仅汇总可更新清单供通知。
        全程 try/except，任何失败只反映在结果里，不抛出。"""
        out: Dict[str, Any] = {"auto_install": bool(self._market_update_auto_install),
                               "updatable": [], "updated": [], "failed": [], "skipped": []}
        try:
            from app.core.plugin import PluginManager
            from app.db.systemconfig_oper import SystemConfigOper
            from app.schemas.types import SystemConfigKey
        except Exception as err:
            out["error"] = f"加载插件管理器失败：{str(err)[:120]}"
            return out
        try:
            installed_ids = SystemConfigOper().get(SystemConfigKey.UserInstalledPlugins) or []
            online = PluginManager().get_online_plugins() or []
            if not online:
                out["error"] = "未获取到在线插件列表"
                return out
            # 每个插件 id 取最大版本
            maxver: Dict[str, Any] = {}
            for p in online:
                if p.id not in maxver or p.plugin_version > maxver[p.id]:
                    maxver[p.id] = p.plugin_version
            online = [p for p in online if p.plugin_version == maxver[p.id]]
            # 已安装版本
            local_ver: Dict[str, Any] = {}
            for p in (PluginManager().get_local_plugins() or []):
                local_ver[p.id] = p.plugin_version
            # 正在运行的插件服务（可选跳过）
            running = set()
            if self._market_update_skip_running:
                try:
                    from app.scheduler import Scheduler
                    for s in (Scheduler().list() or []):
                        if getattr(s, "status", "") == "正在运行":
                            running.add(s.id)
                except Exception:
                    pass
            exclude = set(self._market_update_exclude_ids or [])
            include = set(self._market_update_install_ids or [])
            for p in online:
                pid = str(p.id)
                if pid not in installed_ids:
                    continue
                if not (getattr(p, "has_update", False) or not getattr(p, "installed", True)):
                    continue
                oldv = local_ver.get(p.id)
                if not oldv or str(oldv) == "None":
                    continue
                info = {"id": pid, "name": getattr(p, "plugin_name", pid), "old": str(oldv), "new": str(p.plugin_version)}
                out["updatable"].append(info)
                if not (apply and self._market_update_auto_install):
                    continue
                # 安全：永不自动更新本插件自身；尊重排除/仅选名单；运行中不动
                if pid.lower() in {"agentopsassistant", "mpops", "moviepilot"} or pid in exclude:
                    out["skipped"].append({**info, "reason": "排除/本体"})
                    continue
                if include and pid not in include:
                    out["skipped"].append({**info, "reason": "不在自动更新列表"})
                    continue
                if pid in running or p.id in running:
                    out["skipped"].append({**info, "reason": "正在运行"})
                    continue
                try:
                    from app.helper.plugin import PluginHelper
                    state, msg = PluginHelper().install(pid=p.id, repo_url=getattr(p, "repo_url", ""))
                except Exception as err:
                    state, msg = False, str(err)
                if not state:
                    out["failed"].append({**info, "msg": str(msg)[:120]})
                    continue
                try:
                    PluginManager().reload_plugin(p.id)
                    from app.scheduler import Scheduler
                    Scheduler().update_plugin_job(p.id)
                except Exception as err:
                    logger.warning(f"AgentOpsAssistant 重载插件 {pid} 失败：{err}")
                hist = ""
                try:
                    for ver, note in (getattr(p, "history", None) or {}).items():
                        if str(ver).replace("v", "") == str(p.plugin_version).replace("v", ""):
                            hist = str(note)
                            break
                except Exception:
                    pass
                out["updated"].append({**info, "history": hist})
            return out
        except Exception as err:
            out["error"] = f"插件自动更新异常：{str(err)[:160]}"
            return out

    def _build_backup_status(self) -> Dict[str, Any]:
        backup_path = Path(self._backup_path or "/config/plugins/AgentOpsAssistant/Backup")
        files = []
        if backup_path.exists():
            for item in backup_path.glob("bk_*.zip"):
                try:
                    stat = item.stat()
                except Exception:
                    continue
                files.append({"path": str(item), "name": item.name, "size": stat.st_size, "size_text": self._format_bytes(stat.st_size), "mtime": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")})
        files.sort(key=lambda x: x["mtime"], reverse=True)
        return {"enabled": bool(self._backup_enabled), "cron": self._backup_cron, "keep_count": self._backup_keep_count, "back_path": str(backup_path), "backup_count": len(files), "backup_size": sum(x["size"] for x in files), "backup_size_text": self._format_bytes(sum(x["size"] for x in files)), "latest": files[:5], "direct": True}

    def _create_agentops_backup(self) -> Dict[str, Any]:
        backup_path = Path(self._backup_path or "/config/plugins/AgentOpsAssistant/Backup")
        backup_path.mkdir(parents=True, exist_ok=True)
        config_path = Path(settings.CONFIG_PATH)
        stamp = datetime.now().strftime("%Y%m%d%H%M%S")
        work_dir = backup_path / f"bk_{stamp}"
        work_dir.mkdir(parents=True, exist_ok=True)
        copied = []
        errors = []
        warnings = []
        zip_path = ""
        try:
            for name in ["category.yaml", "app.env"]:
                src = config_path / name
                if src.exists():
                    shutil.copy2(src, work_dir / src.name)
                    copied.append(str(src))
            cookies = config_path / "cookies"
            if cookies.exists():
                shutil.copytree(cookies, work_dir / "cookies", dirs_exist_ok=True)
                copied.append(str(cookies))
            if str(settings.DB_TYPE).lower() == "sqlite":
                for db_file in config_path.glob("user.db*"):
                    if db_file.is_file():
                        shutil.copy2(db_file, work_dir / db_file.name)
                        copied.append(str(db_file))
            elif str(settings.DB_TYPE).lower() == "postgresql":
                dump_target = work_dir / "postgresql_backup.sql"
                ok, msg = self._dump_postgresql(dump_target)
                if ok:
                    copied.append(f"postgresql_backup.sql（{msg}）")
                else:
                    warnings.append(msg)
            manifest = {"created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "db_type": str(settings.DB_TYPE), "copied": copied, "errors": errors, "warnings": warnings}
            (work_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
            zip_base = str(work_dir)
            zip_path = shutil.make_archive(zip_base, "zip", str(work_dir))
        finally:
            if work_dir.exists():
                shutil.rmtree(work_dir, ignore_errors=True)

        removed = self._cleanup_old_backups(backup_path)

        # WebDAV 远端备份
        webdav_success = False
        webdav_error = ""
        if self._backup_webdav_enabled and zip_path and Path(zip_path).exists():
            webdav_success, webdav_error = self._upload_to_webdav(zip_path)

        success = Path(zip_path).exists() and not errors
        status = self._build_backup_status()
        status.update({
            "success": success,
            "zip_file": zip_path,
            "copied": copied,
            "errors": errors,
            "warnings": warnings,
            "removed": removed,
            "webdav_enabled": self._backup_webdav_enabled,
            "webdav_success": webdav_success,
            "webdav_error": webdav_error,
        })
        return status

    def _upload_to_webdav(self, local_zip_path: str) -> Tuple[bool, str]:
        """上传备份到 WebDAV"""
        try:
            from webdav3.client import Client
            from webdav3.exceptions import WebDavException
        except ImportError:
            return False, "webdav3-client 未安装，请运行: pip install webdav3-client"

        if not self._backup_webdav_hostname:
            return False, "WebDAV 地址未配置"

        try:
            options = {
                "webdav_hostname": self._backup_webdav_hostname.rstrip("/"),
                "webdav_login": self._backup_webdav_login,
                "webdav_password": self._backup_webdav_password,
                "disable_check": self._backup_webdav_disable_check,
            }
            if self._backup_webdav_digest_auth:
                options["webdav_auth_type"] = "digest"

            client = Client(options)

            # 检查连接
            if not self._backup_webdav_disable_check:
                if not client.check():
                    return False, "WebDAV 连接测试失败"

            # 上传文件
            remote_path = Path(local_zip_path).name
            client.upload_sync(remote_path=remote_path, local_path=local_zip_path)

            # 清理远端旧备份
            try:
                remote_files = client.list()
                backup_files = [f for f in remote_files if f.startswith("bk_") and f.endswith(".zip")]
                backup_files.sort(reverse=True)
                for old_file in backup_files[self._backup_webdav_max_count:]:
                    try:
                        client.clean(old_file)
                    except Exception as e:
                        logger.warning(f"清理远端旧备份 {old_file} 失败：{e}")
            except Exception as e:
                logger.warning(f"清理远端旧备份失败：{e}")

            if self._backup_webdav_notify:
                self.post_message(
                    mtype=self._notification_type(self._backup_webdav_notify_type),
                    title="MP 运维助手 - WebDAV 备份成功",
                    text=f"⦁ 已上传：{remote_path}\n⦁ 目标：{self._backup_webdav_hostname}"
                )

            return True, "上传成功"
        except WebDavException as e:
            error_msg = f"WebDAV 错误：{str(e)[:200]}"
            logger.error(f"WebDAV 备份失败：{e}")
            return False, error_msg
        except Exception as e:
            error_msg = f"上传失败：{str(e)[:200]}"
            logger.error(f"WebDAV 备份异常：{e}")
            return False, error_msg

    def _dump_postgresql(self, target: Path) -> Tuple[bool, str]:
        """导出 PostgreSQL：优先 pg_dump（PATH 或常见安装目录），无则用 SQLAlchemy 兜底。
        返回 (是否导出, 说明)。导不出时调用方按“提示/警告”处理，不算备份失败。"""
        pg_dump = self._find_pg_dump()
        if pg_dump:
            err = ""
            try:
                env = os.environ.copy()
                env["PGPASSWORD"] = str(settings.DB_POSTGRESQL_PASSWORD)
                cmd = [pg_dump, "-h", str(settings.DB_POSTGRESQL_HOST), "-p", str(settings.DB_POSTGRESQL_PORT),
                       "-U", str(settings.DB_POSTGRESQL_USERNAME), "-d", str(settings.DB_POSTGRESQL_DATABASE), "-f", str(target)]
                result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=600, check=False)
                if result.returncode == 0 and target.exists():
                    return True, "pg_dump"
                err = (result.stderr or result.stdout or "pg_dump 执行失败")[-300:]
            except Exception as e:
                err = str(e)[:300]
            ok2, msg2 = self._dump_postgresql_python(target)
            if ok2:
                return True, f"SQLAlchemy 兜底（pg_dump 失败：{err[:80]}）"
            return False, f"PostgreSQL 未导出：pg_dump 失败（{err}）；SQLAlchemy 兜底也失败（{msg2}）。配置文件已正常备份。"
        # 无 pg_dump：SQLAlchemy 兜底
        ok2, msg2 = self._dump_postgresql_python(target)
        if ok2:
            return True, "SQLAlchemy 兜底（容器内无 pg_dump）"
        return False, ("PostgreSQL 未导出：容器内无 pg_dump，SQLAlchemy 兜底失败（" + msg2 +
                       "）。配置文件已正常备份；如需完整数据库备份请在容器内安装 postgresql-client（提供 pg_dump）。")

    @staticmethod
    def _find_pg_dump() -> str:
        """在 PATH 与常见安装目录中查找 pg_dump，找不到返回空串。"""
        found = shutil.which("pg_dump")
        if found:
            return found
        import glob as _glob
        for pattern in ("/usr/bin/pg_dump", "/usr/local/bin/pg_dump",
                        "/usr/lib/postgresql/*/bin/pg_dump", "/opt/homebrew/bin/pg_dump",
                        "/opt/homebrew/opt/postgresql*/bin/pg_dump"):
            for p in sorted(_glob.glob(pattern)):
                if os.path.isfile(p) and os.access(p, os.X_OK):
                    return p
        return ""

    @staticmethod
    def _sql_literal(v: Any) -> str:
        """把一个 Python 值转成 SQL 字面量（单引号转义防注入/坏 SQL）。"""
        if v is None:
            return "NULL"
        if isinstance(v, bool):
            return "TRUE" if v else "FALSE"
        if isinstance(v, (int, float)):
            return repr(v)
        if isinstance(v, (bytes, bytearray)):
            return "'\\x" + bytes(v).hex() + "'"
        return "'" + str(v).replace("'", "''") + "'"

    def _dump_postgresql_python(self, target: Path) -> Tuple[bool, str]:
        """无 pg_dump 时，用 MoviePilot 已有的 SQLAlchemy 引擎导出（CREATE TABLE + INSERT）。
        尽力而为：全程 try/except，失败只返回 (False, 原因)，绝不影响其它备份。
        注：应急数据导出，可能缺少部分序列/约束，正式恢复仍建议 pg_dump。"""
        try:
            from app.db import Engine
            from sqlalchemy import MetaData, select
            from sqlalchemy.schema import CreateTable
        except Exception as e:
            return False, f"无法加载 SQLAlchemy 引擎：{str(e)[:120]}"
        try:
            meta = MetaData()
            meta.reflect(bind=Engine)
            if not meta.tables:
                return False, "未反射到任何表"
            out = ["-- MoviePilot PostgreSQL 应急备份（AgentOpsAssistant SQLAlchemy 导出，无 pg_dump）",
                   "-- 含表结构与数据，可能缺少部分序列/约束；正式恢复建议用 pg_dump。", ""]
            with Engine.connect() as conn:
                for table in meta.sorted_tables:
                    try:
                        out.append(str(CreateTable(table).compile(Engine)).strip() + ";")
                    except Exception:
                        pass
                    try:
                        rows = conn.execute(select(table)).fetchall()
                    except Exception:
                        rows = []
                    collist = ", ".join('"' + c.name + '"' for c in table.columns)
                    for row in rows:
                        vals = ", ".join(self._sql_literal(v) for v in row)
                        out.append(f'INSERT INTO "{table.name}" ({collist}) VALUES ({vals});')
                    out.append("")
            target.write_text("\n".join(out), encoding="utf-8")
            return (target.exists() and target.stat().st_size > 0), "已导出表结构+数据"
        except Exception as e:
            return False, f"SQLAlchemy 导出失败：{str(e)[:200]}"

    def _cleanup_old_backups(self, backup_path: Path) -> List[str]:
        keep = max(1, int(self._backup_keep_count or 5))
        files = sorted([x for x in backup_path.glob("bk_*.zip") if x.is_file()], key=lambda x: x.stat().st_mtime, reverse=True)
        removed = []
        for item in files[keep:]:
            try:
                removed.append(item.name)
                item.unlink()
            except Exception as err:
                logger.warning(f"AgentOpsAssistant 删除旧备份失败 {item}: {err}")
        return removed

    def _format_backup_status_text(self, data: Dict[str, Any]) -> str:
        lines = [
            "🗄️ MP 运维助手自动备份",
            "⦁ 模式：直接接替 AutoBackup",
            f"⦁ 状态：{'成功' if data.get('success', True) else '异常'}",
            f"⦁ 路径：{data.get('back_path')}",
            f"⦁ 保留数量：{data.get('keep_count')}",
            f"⦁ 当前备份：{data.get('backup_count', 0)} 个 / {data.get('backup_size_text')}",
        ]
        if data.get("zip_file"):
            lines.append(f"⦁ 本次备份：{Path(data['zip_file']).name}")
        if data.get("removed"):
            lines.append(f"⦁ 清理旧备份：{len(data.get('removed') or [])} 个")
        if data.get("webdav_enabled"):
            if data.get("webdav_success"):
                lines.append("⦁ WebDAV 备份：成功")
            elif data.get("webdav_error"):
                lines.append(f"⦁ WebDAV 备份：失败 - {data.get('webdav_error')[:60]}")
            else:
                lines.append("⦁ WebDAV 备份：未执行")
        if data.get("latest"):
            lines.append("最近备份：")
            for item in data["latest"][:3]:
                lines.append(f"⦁ {item['name']}｜{item['size_text']}｜{item['mtime']}")
        if data.get("warnings"):
            lines.append("提示：")
            lines.extend([f"⦁ {str(w)[:160]}" for w in data.get("warnings", [])[:5]])
        if data.get("errors"):
            lines.append("异常：")
            lines.extend([f"⦁ {str(e)[:120]}" for e in data.get("errors", [])[:5]])
        return "\n".join(lines)

    def _build_log_preview(self) -> Dict[str, Any]:
        return self._build_log_clean_stats(clean=False)

    def _build_log_clean_stats(self, clean: bool = False) -> Dict[str, Any]:
        log_dir = Path("/config/logs/plugins")
        rows = max(0, int(self._log_clean_rows or 0))
        selected = {x.lower() for x in (self._log_clean_selected_ids or []) if x}
        files = []
        cleaned = []
        errors = []
        installed_ids = self._get_installed_plugin_ids()
        if not log_dir.exists():
            return {"root": str(log_dir), "file_count": 0, "candidate_count": 0, "total_size": 0, "total_size_text": "0 B", "candidate_size": 0, "candidate_size_text": "0 B", "top_files": [], "candidates": [], "cleaned": [], "errors": [], "rows": rows, "selected_ids": sorted(selected), "dry_run": not clean}
        for item in sorted(list(log_dir.glob("*.log")) + list(log_dir.glob("*.log.*"))):
            if not item.is_file():
                continue
            name = item.name
            original_id = name.split(".log", 1)[0]
            if selected and original_id.lower() not in selected and name.lower() not in selected:
                continue
            try:
                stat = item.stat()
                line_count = self._count_file_lines(item)
            except Exception as err:
                errors.append(f"{name}: {err}")
                continue
            is_split = bool(".log." in name)
            is_deleted_plugin = original_id.lower() not in installed_ids and not self._is_special_log(original_id)
            candidate = (not is_split and line_count > rows) or is_split or is_deleted_plugin
            entry = {"path": str(item), "name": name, "plugin_id": original_id, "size": stat.st_size, "size_text": self._format_bytes(stat.st_size), "mtime": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"), "lines_count": line_count, "is_split": is_split, "is_deleted_plugin": is_deleted_plugin, "candidate": candidate}
            files.append(entry)
            if clean and candidate:
                try:
                    if is_split or is_deleted_plugin:
                        item.unlink()
                        action = "delete"
                        cleaned_lines = line_count
                    else:
                        kept = self._truncate_file_tail(item, rows)
                        action = "truncate"
                        cleaned_lines = max(0, line_count - kept)
                    cleaned.append({**entry, "action": action, "cleaned_lines": cleaned_lines})
                except Exception as err:
                    errors.append(f"{name}: {err}")
        candidates = [x for x in files if x["candidate"]]
        files.sort(key=lambda x: x["size"], reverse=True)
        return {"root": str(log_dir), "file_count": len(files), "candidate_count": len(candidates), "total_size": sum(x["size"] for x in files), "total_size_text": self._format_bytes(sum(x["size"] for x in files)), "candidate_size": sum(x["size"] for x in candidates), "candidate_size_text": self._format_bytes(sum(x["size"] for x in candidates)), "top_files": files[:10], "candidates": candidates[:30], "cleaned": cleaned, "errors": errors[:20], "rows": rows, "selected_ids": sorted(selected), "dry_run": not clean}

    def _format_log_preview_text(self, data: Dict[str, Any]) -> str:
        lines = [
            "🧹 日志清理预览（未执行清理）",
            f"⦁ 扫描文件：{data.get('file_count', 0)} 个",
            f"⦁ 总体积：{data.get('total_size_text')}",
            f"⦁ 候选：{data.get('candidate_count', 0)} 个 / {data.get('candidate_size_text')}",
            "",
            "体积 Top：",
        ]
        for item in data.get("top_files", [])[:8]:
            lines.append(f"⦁ {item['name']}｜{item['size_text']}｜{item['mtime']}")
        lines.append("")
        lines.append(f"规则：标准 .log 按最后 {data.get('rows')} 行保留；.log.N 分割日志和已卸载插件日志列为可清理候选。")
        return "\n".join(lines)

    def _format_log_clean_result_text(self, data: Dict[str, Any]) -> str:
        lines = [
            "🧹 插件日志清理结果",
            f"⦁ 扫描文件：{data.get('file_count', 0)} 个",
            f"⦁ 候选文件：{data.get('candidate_count', 0)} 个 / {data.get('candidate_size_text')}",
            f"⦁ 已处理：{len(data.get('cleaned') or [])} 个",
            f"⦁ 保留行数：{data.get('rows')}",
        ]
        for item in (data.get('cleaned') or [])[:8]:
            action = "删除" if item.get("action") == "delete" else "截断"
            lines.append(f"⦁ {action} {item['name']}｜清理行数 {item.get('cleaned_lines', 0)}")
        if data.get('errors'):
            lines.append("异常：")
            lines.extend([f"⦁ {e}" for e in data.get('errors', [])[:5]])
        return "\n".join(lines)

    def _normalize_plugin_id(self, value: Any) -> str:
        raw = str(value or "").strip()
        safe = re.sub(r"[^A-Za-z0-9_\-]", "", raw)[:80]
        return safe

    def _build_plugin_uninstall_status(self, clean: bool = False) -> Dict[str, Any]:
        # 目标插件：优先用配置页的多选列表 plugin_uninstall_ids，回退到旧的单个 plugin_uninstall_id
        raw_ids = list(self._plugin_uninstall_ids or [])
        if not raw_ids and self._plugin_uninstall_id:
            raw_ids = [self._plugin_uninstall_id]
        ids: List[str] = []
        for rid in raw_ids:
            pid = self._normalize_plugin_id(rid)
            if pid and pid not in ids:
                ids.append(pid)
        result = {"success": True, "dry_run": not clean, "plugin_id": "、".join(ids),
                  "note": "卸载插件并按勾选项清理配置、数据、日志、备份或本地源码残留；不会删除媒体文件、下载任务或 MoviePilot 核心源码。",
                  "remove_plugin": self._plugin_uninstall_remove_plugin,
                  "clear_config": self._plugin_uninstall_clear_config,
                  "clear_data": self._plugin_uninstall_clear_data,
                  "delete_source": self._plugin_uninstall_delete_source,
                  "uninstalled": [], "cleaned_config": [], "cleaned_data": [],
                  "candidates": [], "deleted": [], "errors": [], "backup_path": "", "blocked": ""}
        if not ids:
            result.update({"success": False, "blocked": "请先在配置页选择目标插件。"})
            return result
        forbidden = {"agentopsassistant", "mpops", "moviepilot"}
        backups: List[str] = []
        for pid in ids:
            if pid.lower() in forbidden:
                result["errors"].append(f"{pid}: 为避免自毁或误删核心组件，禁止卸载 AgentOpsAssistant / MoviePilot 本体，已跳过。")
                continue
            candidates = self._plugin_uninstall_candidates(pid)
            for item in candidates:
                item["plugin_id"] = pid
            result["candidates"].extend(candidates)
            if not clean:
                continue
            allowed_candidates = []
            for item in candidates:
                path = Path(item.get("path") or "")
                if self._plugin_uninstall_path_allowed(path):
                    allowed_candidates.append(item)
                else:
                    result["errors"].append(f"{path}: 路径越界，不在允许范围内，已跳过删除。")
            if self._plugin_uninstall_remove_plugin:
                ok, message, cleaned = self._uninstall_moviepilot_plugin(pid)
                result["uninstalled"].append({"plugin_id": pid, "success": ok, "message": message})
                if cleaned.get("config"):
                    result["cleaned_config"].append(pid)
                if cleaned.get("data"):
                    result["cleaned_data"].append(pid)
                if not ok:
                    result["errors"].append(f"{pid}: {message}")
                    continue
            if allowed_candidates:
                backups.append(self._backup_plugin_uninstall_candidates(pid, allowed_candidates))
            for item in allowed_candidates:
                path = Path(item.get("path") or "")
                if not path.exists():
                    continue
                try:
                    if path.is_dir():
                        shutil.rmtree(path)
                    else:
                        path.unlink()
                    result["deleted"].append(item)
                except Exception as err:
                    result["errors"].append(f"{path}: {err}")
        result["backup_path"] = "；".join([b for b in backups if b])
        result["success"] = not result["errors"]
        return result

    def _uninstall_moviepilot_plugin(self, plugin_id: str) -> Tuple[bool, str, Dict[str, bool]]:
        cleaned = {"config": False, "data": False}
        try:
            from app.core.plugin import PluginManager
            from app.db.systemconfig_oper import SystemConfigOper
            from app.scheduler import Scheduler
            from app.schemas.types import SystemConfigKey
        except Exception as err:
            return False, f"当前 MoviePilot 环境缺少插件卸载依赖：{err}", cleaned

        messages: List[str] = []
        config_oper = SystemConfigOper()
        installed_plugins = config_oper.get(SystemConfigKey.UserInstalledPlugins) or []
        remaining = [p for p in installed_plugins if p != plugin_id]
        if len(remaining) != len(installed_plugins):
            config_oper.set(SystemConfigKey.UserInstalledPlugins, remaining)
            messages.append("已移出已安装列表")
        else:
            messages.append("未在已安装列表中")

        self._remove_plugin_api_safely(plugin_id)
        self._remove_plugin_job_safely(Scheduler(), plugin_id)
        self._remove_plugin_from_folders_safely(config_oper, SystemConfigKey, plugin_id)

        plugin_manager = PluginManager()
        if self._plugin_uninstall_clear_config:
            try:
                cleaned["config"] = bool(plugin_manager.delete_plugin_config(plugin_id))
                messages.append("配置已清理" if cleaned["config"] else "配置未找到")
            except Exception as err:
                messages.append(f"配置清理失败：{err}")
        if self._plugin_uninstall_clear_data:
            try:
                cleaned["data"] = bool(plugin_manager.delete_plugin_data(plugin_id))
                messages.append("数据已清理" if cleaned["data"] else "数据未找到")
            except Exception as err:
                messages.append(f"数据清理失败：{err}")
        try:
            plugin_manager.remove_plugin(plugin_id)
            messages.append("运行实例已移除")
        except Exception as err:
            return False, f"移除运行实例失败：{err}", cleaned
        return True, "；".join(messages), cleaned

    @staticmethod
    def _remove_plugin_api_safely(plugin_id: str):
        try:
            from app.api.endpoints.plugin import remove_plugin_api
            remove_plugin_api(plugin_id)
        except Exception as err:
            logger.debug(f"AgentOpsAssistant 移除插件 API 路由跳过：{plugin_id} {err}")

    @staticmethod
    def _remove_plugin_job_safely(scheduler: Any, plugin_id: str):
        try:
            if hasattr(scheduler, "remove_plugin_job"):
                scheduler.remove_plugin_job(plugin_id)
        except Exception as err:
            logger.warning(f"AgentOpsAssistant 移除插件调度失败：{plugin_id} {err}")

    @staticmethod
    def _remove_plugin_from_folders_safely(config_oper: Any, system_config_key: Any, plugin_id: str):
        try:
            folders_key = getattr(system_config_key, "PluginFolders", "PluginFolders")
            folders = config_oper.get(folders_key) or {}
            modified = False
            for _, folder_data in folders.items():
                if isinstance(folder_data, dict) and isinstance(folder_data.get("plugins"), list):
                    if plugin_id in folder_data["plugins"]:
                        folder_data["plugins"].remove(plugin_id)
                        modified = True
                elif isinstance(folder_data, list) and plugin_id in folder_data:
                    folder_data.remove(plugin_id)
                    modified = True
            if modified:
                config_oper.set(folders_key, folders)
        except Exception as err:
            logger.warning(f"AgentOpsAssistant 从插件文件夹移除失败：{plugin_id} {err}")

    def _plugin_uninstall_candidates(self, plugin_id: str) -> List[Dict[str, Any]]:
        lower = plugin_id.lower()
        candidates: List[Dict[str, Any]] = []
        roots = [
            ("runtime_data", Path("/config/plugins") / plugin_id),
            ("runtime_data", Path("/config/plugins") / lower),
            ("backup", Path("/config/plugins_backup") / plugin_id),
            ("backup", Path("/config/plugins_backup") / lower),
        ]
        if self._plugin_uninstall_delete_source and self._local_plugin_repo:
            roots.append(("local_source", Path(self._local_plugin_repo) / "plugins.v2" / lower))
        for kind, path in roots:
            if path.exists():
                candidates.append(self._path_candidate(kind, path))
        log_root = Path("/config/logs/plugins")
        for item in sorted(list(log_root.glob(f"{lower}.log*")) + list(log_root.glob(f"{plugin_id}.log*"))):
            if item.exists():
                candidates.append(self._path_candidate("log", item))
        seen = set()
        deduped = []
        for item in candidates:
            key = item.get("path")
            if key not in seen:
                seen.add(key)
                deduped.append(item)
        return deduped

    def _plugin_uninstall_path_allowed(self, path: Path) -> bool:
        roots = [Path("/config/plugins"), Path("/config/plugins_backup"), Path("/config/logs/plugins")]
        if self._plugin_uninstall_delete_source and self._local_plugin_repo:
            roots.append(Path(self._local_plugin_repo) / "plugins.v2")
        try:
            resolved = path.resolve(strict=False)
        except Exception:
            return False
        for root in roots:
            try:
                root_resolved = root.resolve(strict=False)
                if resolved == root_resolved or root_resolved in resolved.parents:
                    return True
            except Exception:
                continue
        return False

    def _path_candidate(self, kind: str, path: Path) -> Dict[str, Any]:
        try:
            size = self._path_size(path) if path.exists() else 0
            mtime = datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            size = 0
            mtime = "未知"
        return {"kind": kind, "path": str(path), "type": "dir" if path.is_dir() else "file", "size": size, "size_text": self._format_bytes(size), "mtime": mtime}

    @staticmethod
    def _path_size(path: Path) -> int:
        if path.is_file():
            return path.stat().st_size
        total = 0
        for item in path.rglob("*"):
            if item.is_file():
                try:
                    total += item.stat().st_size
                except Exception:
                    pass
        return total

    def _backup_plugin_uninstall_candidates(self, plugin_id: str, candidates: List[Dict[str, Any]]) -> str:
        backup_dir = Path("/config/plugins/AgentOpsAssistant/PluginUninstallBackup")
        backup_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        zip_path = backup_dir / f"{plugin_id}-residue-{stamp}.zip"
        manifest = {"created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "plugin_id": plugin_id, "candidates": candidates}
        with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            zf.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
            for item in candidates:
                path = Path(item.get("path") or "")
                if not path.exists():
                    continue
                base = f"{item.get('kind')}/{path.name}"
                if path.is_file():
                    zf.write(path, base)
                else:
                    for child in path.rglob("*"):
                        if child.is_file():
                            zf.write(child, f"{base}/{child.relative_to(path)}")
        return str(zip_path)

    @staticmethod
    def _format_plugin_uninstall_text(data: Dict[str, Any]) -> str:
        title = "🧩 插件卸载预览" if data.get("dry_run") else "🧩 插件卸载结果"
        lines = [title, f"⦁ 插件ID：{data.get('plugin_id') or '未填写'}", f"⦁ 说明：{data.get('note')}"]
        if data.get("blocked"):
            lines.append(f"⦁ 阻止原因：{data.get('blocked')}")
            return "\n".join(lines)
        actions = []
        actions.append("卸载插件" if data.get("remove_plugin") else "仅清残留")
        if data.get("clear_config"):
            actions.append("清配置")
        if data.get("clear_data"):
            actions.append("清数据")
        actions.append("删本地源码" if data.get("delete_source") else "保留本地源码")
        lines.append(f"⦁ 动作：{' ｜ '.join(actions)}")
        candidates = data.get("candidates") or []
        lines.append(f"⦁ 候选残留：{len(candidates)} 项")
        for item in candidates[:8]:
            lines.append(f"⦁ {item.get('kind')}｜{item.get('type')}｜{item.get('size_text')}｜{item.get('path')}")
        if data.get("dry_run"):
            lines.append("⦁ 状态：仅预览，未卸载或删除")
        else:
            uninstalled = data.get("uninstalled") or []
            if uninstalled:
                ok_count = sum(1 for item in uninstalled if item.get("success"))
                lines.append(f"⦁ 卸载：{ok_count}/{len(uninstalled)} 个")
                for item in uninstalled[:5]:
                    lines.append(f"⦁ {item.get('plugin_id')}｜{item.get('message')}")
            if data.get("cleaned_config") or data.get("cleaned_data"):
                lines.append(f"⦁ 配置/数据：配置 {len(data.get('cleaned_config') or [])} 个 ｜ 数据 {len(data.get('cleaned_data') or [])} 个")
            lines.append(f"⦁ 已删除：{len(data.get('deleted') or [])} 项")
            lines.append(f"⦁ 备份：{data.get('backup_path') or '未生成'}")
        if data.get("errors"):
            lines.append("异常：")
            lines.extend([f"⦁ {e}" for e in data.get("errors", [])[:5]])
        return "\n".join(lines)

    @staticmethod
    def _count_file_lines(path: Path) -> int:
        with path.open('r', encoding='utf-8', errors='ignore') as fh:
            return sum(1 for _ in fh)

    @staticmethod
    def _truncate_file_tail(path: Path, rows: int) -> int:
        if rows <= 0:
            path.write_text('', encoding='utf-8')
            return 0
        with path.open('r', encoding='utf-8', errors='ignore') as fh:
            lines = fh.readlines()
        kept = lines[-min(rows, len(lines)):]
        with path.open('w', encoding='utf-8') as fh:
            fh.writelines(kept)
        return len(kept)

    @staticmethod
    def _is_special_log(plugin_id: str) -> bool:
        return plugin_id.lower() in {"plugin", "system", "main", "error"}

    @staticmethod
    def _get_installed_plugin_ids() -> set:
        try:
            from app.core.plugin import PluginManager
            plugins = PluginManager().get_local_plugins() or []
            return {str(getattr(p, 'id', '')).lower() for p in plugins if getattr(p, 'installed', False) and getattr(p, 'id', None)}
        except Exception:
            return set()

    @staticmethod
    def _settings_value(settings_obj: Any, *names: str, default: Any = "") -> Any:
        for name in names:
            value = getattr(settings_obj, name, None)
            if value not in (None, ""):
                return value
        return default

    @staticmethod
    def _dedupe_pairs(items: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
        seen = set()
        result = []
        for label, path in items or []:
            clean = str(path or "").strip()
            if not clean or clean in seen:
                continue
            seen.add(clean)
            result.append((label, clean))
        return result

    @staticmethod
    def _is_local_storage(storage: Any) -> bool:
        name = str(storage or "").strip().lower()
        return name in ("", "local", "本地")

    @staticmethod
    def _dedupe_directory_entries(items: List[Tuple[str, str, Any]]) -> List[Tuple[str, str, Any]]:
        seen = set()
        result = []
        for label, path, storage in items or []:
            clean = str(path or "").strip()
            if not clean or clean in seen:
                continue
            seen.add(clean)
            result.append((label, clean, storage))
        return result

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
            checks.append({"name": "agentops_services", "ok": True, "detail": f"已调度 {len(services)} 个"})
        except Exception as err:
            checks.append({"name": "agentops_services", "ok": False, "detail": str(err)[:120]})
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
        return {"subscribe": "订阅", "sites": "站点", "downloaders": "下载器", "agentops_services": "本插件任务", "database": "数据库", "storage": "存储空间", "directory": "目录权限"}

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

    def _notify_health_failures(self, data: Dict[str, Any]):
        failures = self._health_failure_lines(data)
        if not failures:
            return
        failed = data.get("fail") or len(failures)
        text = "\n".join([f"发现 {failed} 项异常", *failures])
        self.post_message(mtype=self._notification_type(self._health_check_notify_type), title=f"MP 运维助手 - 健康巡查发现 {failed} 项异常", text=text)

    @staticmethod
    def _format_health_summary(data: Dict[str, Any]) -> str:
        name_map = AgentOpsAssistant._health_name_map()
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

    def _run_named_task(self, name: str, cmd: List[str], expect: str = "") -> bool:
        result = self._run_command_capture(cmd, timeout=600)
        output = result["output"]
        ok = result["returncode"] == 0 and (not expect or expect in output)
        self._save_task_result(name, ok, result["returncode"], output)
        return ok

    @staticmethod
    def _run_command_capture(cmd: List[str], timeout: int = 600) -> Dict[str, Any]:
        try:
            env = os.environ.copy()
            env["PYTHONDONTWRITEBYTECODE"] = "1"
            result = subprocess.run(cmd, cwd="/config", env=env, capture_output=True, text=True, timeout=timeout, check=False)
            output = "\n".join([result.stdout or "", result.stderr or ""]).strip()
            return {"returncode": result.returncode, "output": output[-4000:]}
        except Exception as err:
            return {"returncode": -1, "output": str(err)}

    def _save_task_result(self, name: str, success: bool, returncode: int, output: str):
        self.save_data(f"last_{self._slug(name)}", {"time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "returncode": returncode, "success": bool(success), "output": (output or "")[-2000:]})

    @staticmethod
    def _episode_ranges(eps: List[int]) -> str:
        ranges = []
        i = 0
        while i < len(eps):
            start = end = eps[i]
            while i + 1 < len(eps) and eps[i + 1] == eps[i] + 1:
                i += 1
                end = eps[i]
            ranges.append(f"E{start:02d}" if start == end else f"E{start:02d}-E{end:02d}")
            i += 1
        return ",".join(ranges)

    @staticmethod
    def _format_bytes(value: int) -> str:
        size = float(value or 0)
        for unit in ["B", "KB", "MB", "GB", "TB", "PB"]:
            if size < 1024 or unit == "PB":
                return f"{int(size)} {unit}" if unit == "B" else f"{size:.2f} {unit}"
            size /= 1024
        return "0 B"

    def _build_summary(self) -> str:
        return "；".join([f"插件：{'启用' if self._enabled else '未启用'}", f"每日汇报：{'启用' if self._daily_report_enabled else '停用'} {self._daily_report_cron}", f"汇报栏目：健康={'开' if self._health_in_report else '关'} / 订阅={'开' if self._subscribe_in_report else '关'} / 站点={'开' if self._site_stat_in_report else '关'}", f"插件日志清理：{'启用' if self._log_clean_enabled else '停用'} {self._log_clean_cron} 保留{self._log_clean_rows}行", f"自动备份：{'启用' if self._backup_enabled else '停用'} {self._backup_cron} 保留{self._backup_keep_count}个", f"更新检查：{'启用' if self._mp_update_enabled else '停用'} {self._mp_update_cron}", f"插件库检查：{'启用' if self._market_update_enabled else '停用'} 每{self._market_update_interval}秒"])

    def _task_definitions(self) -> List[Dict[str, Any]]:
        return [
            {"key": "daily_report", "name": "每日汇报", "enabled": self._daily_report_enabled, "last_keys": ["last_daily_report", "last_daily_report_preview"], "next": self._daily_report_cron, "icon": "mdi-newspaper-variant"},
            {"key": "subscribe_reminder", "name": "订阅追新", "enabled": self._subscribe_reminder_enabled, "last_keys": ["last_subscribe_reminder"], "next": self._subscribe_reminder_cron, "icon": "mdi-bell-ring"},
            {"key": "site_stat", "name": "站点统计", "enabled": self._site_stat_enabled, "last_keys": ["last_site_stat"], "next": "手动刷新", "icon": "mdi-chart-pie"},
            {"key": "health_check", "name": "健康巡查", "enabled": self._health_check_enabled, "last_keys": ["last_health_check"], "next": self._health_check_cron, "icon": "mdi-heart-pulse"},
            {"key": "log_clean", "name": "日志清理", "enabled": self._log_clean_enabled, "last_keys": ["last_log_clean", "last_log_clean_preview"], "next": self._log_clean_cron, "icon": "mdi-broom"},
            {"key": "backup", "name": "自动备份", "enabled": self._backup_enabled, "last_keys": ["last_backup"], "next": self._backup_cron, "icon": "mdi-database-arrow-up"},
            {"key": "mp_update", "name": "MP 更新", "enabled": self._mp_update_enabled, "last_keys": ["last_update_preview"], "next": self._mp_update_cron, "icon": "mdi-update"},
            {"key": "market_update", "name": "插件库", "enabled": self._market_update_enabled, "last_keys": ["last_market_update"], "next": f"每 {self._market_update_interval // 3600 if self._market_update_interval else 0} 小时", "icon": "mdi-puzzle-check"},
            {"key": "downloader_tag", "name": "种子标签", "enabled": self._dltag_enabled, "last_keys": ["last_downloader_tag"], "next": "手动执行", "icon": "mdi-tag-plus"},
            {"key": "seed_clean", "name": "自动删种", "enabled": self._seedclean_enabled, "last_keys": ["last_seed_clean"], "next": self._seedclean_cron, "icon": "mdi-delete-sweep"},
        ]

    def _task_snapshot(self) -> List[Dict[str, Any]]:
        rows = []
        for task in self._task_definitions():
            records = [self.get_data(k) or {} for k in task.get("last_keys", [])]
            records = [r for r in records if r]
            latest = sorted(records, key=lambda r: str(r.get("time") or ""), reverse=True)[0] if records else {}
            success = latest.get("success")
            if success is True:
                state, color = "成功", "success"
            elif success is False:
                state, color = "失败", "error"
            else:
                state, color = "无记录", "default"
            rows.append({**task, "latest": latest, "state": state, "color": color})
        return rows

    def _task_flow_panel(self) -> dict:
        rows = []
        for item in self._task_snapshot():
            rows.append({"component": "VListItem", "props": {"density": "compact", "class": "rounded mb-1 border"}, "content": [
                {"component": "template", "props": {"v-slot:prepend": True}, "content": [{"component": "VAvatar", "props": {"size": "32", "variant": "tonal", "color": item["color"] if item["enabled"] else "default"}, "content": [{"component": "VIcon", "props": {"icon": item["icon"], "size": "18"}}]}]},
                {"component": "VListItemTitle", "text": item["name"]},
                {"component": "VListItemSubtitle", "text": f"最近 {item['latest'].get('time') or '—'}｜下次 {item['next']}｜{self._task_result_summary(item['latest'])}"},
                {"component": "template", "props": {"v-slot:append": True}, "content": [
                    {"component": "VChip", "props": {"size": "x-small", "variant": "tonal", "color": "success" if item["enabled"] else "default", "class": "mr-1"}, "text": "ON" if item["enabled"] else "OFF"},
                    {"component": "VChip", "props": {"size": "x-small", "variant": "tonal", "color": item["color"]}, "text": item["state"]},
                ]},
            ]})
        return {"component": "VCard", "props": {"variant": "outlined", "class": "mb-4"}, "content": [{"component": "VCardTitle", "props": {"class": "text-subtitle-2 d-flex align-center"}, "content": [{"component": "VIcon", "props": {"icon": "mdi-timeline-clock", "class": "mr-2", "color": "primary"}}, {"component": "span", "text": "任务流"}]}, {"component": "VCardText", "props": {"class": "pt-0"}, "content": [{"component": "VList", "props": {"density": "compact", "class": "bg-transparent"}, "content": rows}]}]}

    @staticmethod
    def _task_result_summary(data: Dict[str, Any]) -> str:
        if not data:
            return "无记录"
        output = str(data.get("error") or data.get("message") or data.get("output") or "").strip().replace("\n", " ")
        if not output:
            return "成功" if data.get("success") else "失败"
        return output[:36] + ("…" if len(output) > 36 else "")

    def _task_exception_panel(self) -> dict:
        rows = self._task_snapshot()
        failed = [r for r in rows if r["latest"].get("success") is False]
        pending = self._pending_gate_count()
        title = f"失败 {len(failed)}｜待确认 {pending}"
        color = "error" if failed else "warning" if pending else "success"
        text = " / ".join([r["name"] for r in failed[:3]]) if failed else ("存在高影响开关开启" if pending else "全部正常")
        return {"component": "VCard", "props": {"variant": "tonal", "color": color, "class": "mb-2"}, "content": [{"component": "VCardText", "props": {"class": "d-flex align-center justify-space-between py-3"}, "content": [{"component": "div", "content": [{"component": "div", "props": {"class": "text-caption"}, "text": "异常与待办"}, {"component": "div", "props": {"class": "text-h5 font-weight-bold"}, "text": title}]}, {"component": "VChip", "props": {"variant": "tonal", "color": color}, "text": text}]}]}

    @staticmethod
    def _status_card(title: str, value: str, icon: str, color: str, subtitle: str) -> dict:
        return {"component": "VCol", "props": {"cols": 12, "md": 4}, "content": [{"component": "VCard", "props": {"variant": "tonal", "color": color, "class": "mb-4 h-100"}, "content": [{"component": "VCardText", "content": [{"component": "div", "props": {"class": "d-flex align-center justify-space-between mb-2"}, "content": [{"component": "div", "props": {"class": "text-caption"}, "text": title}, {"component": "VIcon", "props": {"icon": icon, "size": "28"}}]}, {"component": "div", "props": {"class": "text-h6 font-weight-bold"}, "text": value}, {"component": "div", "props": {"class": "text-caption text-medium-emphasis mt-1"}, "text": subtitle[:120]}]}]}]}

    @staticmethod
    def _workflow_card(title: str, icon: str, color: str, modules: List[Dict[str, str]]) -> dict:
        chips = []
        for m in modules:
            status = m.get("status", "")
            chip_color = "success" if status == "已直接接替" else "info" if status == "已接入" else "default"
            chips.append({"component": "VChip", "props": {"size": "small", "variant": "tonal", "color": chip_color, "class": "ma-1"}, "text": f"{m.get('name')}｜{status}"})
        return {"component": "VCol", "props": {"cols": 12, "md": 6}, "content": [{"component": "VCard", "props": {"variant": "tonal", "color": color, "class": "h-100"}, "content": [{"component": "VCardTitle", "props": {"class": "text-subtitle-2"}, "content": [{"component": "VIcon", "props": {"icon": icon, "class": "mr-2"}}, {"component": "span", "text": title}]}, {"component": "VCardText", "content": chips}]}]}

    @staticmethod
    def _action_button(text: str, icon: str, color: str, api_path: str) -> dict:
        return {"component": "VCol", "props": {"cols": 12, "md": 4}, "content": [{"component": "VBtn", "props": {"block": True, "variant": "tonal", "color": color, "prepend-icon": icon, "class": "text-none mb-2"}, "text": text, "events": {"click": {"api": f"plugin/AgentOpsAssistant/{api_path}", "method": "post"}}}]}

    @staticmethod
    def _alert(kind: str, text: str) -> dict:
        return {"component": "VAlert", "props": {"type": kind, "variant": "tonal", "class": "mb-3", "text": text}}

    @staticmethod
    def _section_title(title: str, subtitle: str) -> dict:
        return {"component": "div", "props": {"class": "mb-2"}, "content": [{"component": "div", "props": {"class": "text-h6"}, "text": title}, {"component": "div", "props": {"class": "text-caption text-medium-emphasis"}, "text": subtitle}]}

    @staticmethod
    def _expansion_panel(value: str, title: str, icon: str, color: str, content: List[dict]) -> dict:
        return {"component": "VExpansionPanel", "props": {"value": value, "class": "rounded border config-card", "eager": True}, "content": [
            {"component": "VExpansionPanelTitle", "props": {"class": "text-subtitle-2 d-flex align-center px-3 py-2"}, "content": [{"component": "VIcon", "props": {"icon": icon, "class": "mr-2", "color": color, "size": "small"}}, {"component": "span", "text": title}]},
            {"component": "VExpansionPanelText", "props": {"class": "pa-3", "eager": True}, "content": content},
        ]}

    @staticmethod
    def _mini_hint(text: str) -> dict:
        return {"component": "VAlert", "props": {"type": "info", "variant": "tonal", "density": "compact", "class": "mb-3 text-caption", "text": text}}


    def _form_group(self, title: str, subtitle: str, icon: str, color: str, fields: List[dict], actions: List[dict] = None, tips: List[str] = None) -> dict:
        body = [{"component": "VRow", "content": fields}]
        if tips:
            body.append({"component": "VAlert", "props": {"type": "info", "variant": "tonal", "density": "compact", "class": "mt-3", "text": "｜".join(tips)}})
        content = [
            {"component": "VCardTitle", "props": {"class": "d-flex align-center"}, "content": [{"component": "VIcon", "props": {"icon": icon, "color": color, "class": "mr-2"}}, {"component": "span", "text": title}, {"component": "VSpacer"}, {"component": "VChip", "props": {"size": "small", "variant": "tonal", "color": color}, "text": "开关 / 下拉优先"}]},
            {"component": "VCardSubtitle", "text": subtitle},
            {"component": "VCardText", "content": body},
        ]
        if actions:
            content.append({"component": "VDivider"})
            content.append({"component": "VCardActions", "props": {"class": "flex-wrap ga-2 px-4 pb-4"}, "content": actions})
        return {"component": "VCard", "props": {"variant": "outlined", "class": "mb-4"}, "content": content}

    @staticmethod
    def _select_col(model: str, label: str, items: List[Tuple[str, Any]], md: int) -> dict:
        return {"component": "VCol", "props": {"cols": 12, "md": md}, "content": [{"component": "VSelect", "props": {"model": model, "label": label, "items": [{"title": title, "value": value} for title, value in items], "density": "comfortable", "variant": "outlined", "persistent-hint": True, "hint": "下拉预设，免手写"}}]}

    @staticmethod
    def _switch_col(model: str, label: str, md: int, hint: str = "") -> dict:
        props = {"model": model, "label": label, "color": "primary", "inset": True}
        if hint:
            props.update({"hint": hint, "persistent-hint": True})
        return {"component": "VCol", "props": {"cols": 12, "md": md}, "content": [{"component": "VSwitch", "props": props}]}

    @staticmethod
    def _text_col(model: str, label: str, hint: str, md: int, field_type: str = "text") -> dict:
        props = {"model": model, "label": label, "hint": hint, "persistent-hint": True}
        if field_type:
            props["type"] = field_type
        return {"component": "VCol", "props": {"cols": 12, "md": md}, "content": [{"component": "VTextField", "props": props}]}

    @staticmethod
    def _safe_int(value: Any, default: int, minimum: int) -> int:
        try:
            number = int(value)
            return number if number >= minimum else default
        except Exception:
            return default

    @staticmethod
    def _notification_type(value: Any, default: str = "Plugin"):
        aliases = {
            "下载": "Download",
            "资源下载": "Download",
            "整理": "Organize",
            "整理入库": "Organize",
            "订阅": "Subscribe",
            "站点": "SiteMessage",
            "站点消息": "SiteMessage",
            "媒体服务器": "MediaServer",
            "手动": "Manual",
            "手动处理": "Manual",
            "插件": "Plugin",
            "智能体": "Agent",
            "其他": "Other",
            "其它": "Other",
        }
        key = aliases.get(str(value or default or "Plugin").strip(), str(value or default or "Plugin").strip())
        fallback_key = aliases.get(str(default or "Plugin").strip(), str(default or "Plugin").strip()) or "Plugin"
        for candidate in (key, fallback_key, "Plugin"):
            try:
                return NotificationType[candidate]
            except Exception:
                pass
            try:
                return NotificationType.__getitem__(candidate)
            except Exception:
                pass
            try:
                return NotificationType(candidate)
            except Exception:
                pass
            try:
                for item in NotificationType:
                    if getattr(item, "name", "").lower() == candidate.lower() or str(getattr(item, "value", "")) == candidate:
                        return item
            except Exception:
                pass
            if hasattr(NotificationType, candidate):
                return getattr(NotificationType, candidate)
        return getattr(NotificationType, "Plugin", "Plugin")

    @staticmethod
    def _slug(name: str) -> str:
        return {"MP运维每日汇报": "daily_report", "每日汇报": "daily_report", "订阅提醒": "subscribe_reminder", "订阅追新": "subscribe_reminder", "预览每日汇报": "daily_report_preview", "日报预览": "daily_report_preview", "健康巡查": "health_check", "站点数据统计": "site_stat", "日志清理": "log_clean", "日志清理预览": "log_clean_preview", "自动备份": "backup", "插件库更新": "market_update", "更新状态预览": "update_preview", "主程序更新检查": "update_preview", "MoviePilot更新检查": "update_preview", "插件治理预览": "plugin_uninstall_preview", "插件卸载预览": "plugin_uninstall_preview", "插件残留治理": "plugin_uninstall", "插件卸载": "plugin_uninstall", "自动删种": "seed_clean", "订阅规则填充": "subfill", "清理填充历史": "subfill_clear_history", "清理已处理": "subfill_clear_handled", "种子打标签": "downloader_tag"}.get(name, "task")

    @staticmethod
    def _parse_csv(value: Any) -> List[str]:
        if isinstance(value, list):
            return [str(x).strip() for x in value if str(x).strip()]
        return [x.strip() for x in str(value or "").split(",") if x.strip()]

    @staticmethod
    def _default_config() -> Dict[str, Any]:
        return {"enabled": False, "sidebar_nav_enabled": True, "daily_report_enabled": True, "daily_report_cron": "0 22 * * *", "daily_report_greeting": "少爷", "daily_report_msgtype": "Plugin", "health_in_report": True, "subscribe_in_report": True, "site_stat_in_report": True, "report_version": True, "report_site_status": True, "report_site_increment": True, "report_today_download": True, "report_transfer": True, "report_subscribe": True, "report_storage": True, "report_media_stat": True, "report_summary": True, "health_check_enabled": True, "health_check_cron": "0 */6 * * *", "health_check_items": [], "health_check_database_targets": ["current"], "health_check_storage_targets": ["storages", "config", "download", "library"], "health_check_directory_targets": ["config", "plugin", "download", "library"], "health_check_storage_threshold": 85, "health_check_notify_type": "Plugin", "report_health": True, "subscribe_reminder_enabled": True, "subscribe_reminder_onlyonce": False, "subscribe_reminder_time": "9", "subscribe_reminder_cron": "0 9 * * *", "subscribe_reminder_subtype": ["movie", "tv"], "subscribe_reminder_msgtype": "Subscribe", "site_stat_enabled": True, "site_stat_onlyonce": False, "site_stat_dashboard_type": "today", "site_stat_notify_type": "inc", "log_clean_enabled": False, "log_clean_cron": "0 3 * * 1", "log_clean_rows": 300, "log_clean_selected_ids": [], "log_clean_notify": True, "log_clean_notify_type": "Plugin", "log_clean_onlyonce": False, "backup_enabled": False, "backup_onlyonce": False, "backup_cron": "0 4 * * 1", "backup_keep_count": 5, "backup_path": "/config/plugins/AgentOpsAssistant/Backup", "backup_notify": True, "backup_notify_type": "Plugin", "backup_webdav_enabled": False, "backup_webdav_notify": False, "backup_webdav_notify_type": "Plugin", "backup_webdav_digest_auth": False, "backup_webdav_disable_check": False, "backup_webdav_hostname": "", "backup_webdav_login": "", "backup_webdav_password": "", "backup_webdav_max_count": 5, "mp_update_enabled": False, "mp_update_cron": "0 9 * * *", "mp_update_notify": True, "mp_update_notify_type": "Plugin", "mp_update_restart_confirm": False, "mp_update_types": ["后端", "前端"], "market_update_enabled": False, "market_update_onlyonce": False, "market_update_interval": 86400, "market_update_notify": True, "market_update_write_notify": False, "market_update_notify_type": "Plugin", "market_update_write_settings": False, "market_update_write_env": False, "market_update_blacklist_enabled": False, "market_update_blacklist": [], "market_update_auto_install": False, "market_update_install_ids": [], "market_update_exclude_ids": [], "market_update_skip_running": True, "market_update_auto_get": False, "market_update_proxy": True, "market_update_timeout": 5, "market_update_wiki_url": "https://wiki.movie-pilot.org/zh/plugin", "market_update_wiki_xpath": '//pre[@class="prismjs line-numbers" and @v-pre="true"]/code/text()', "plugin_uninstall_id": "", "plugin_uninstall_ids": [], "plugin_uninstall_remove_plugin": True, "plugin_uninstall_clear_config": True, "plugin_uninstall_clear_data": True, "plugin_uninstall_delete_source": False, "plugin_uninstall_notify": True, "plugin_uninstall_notify_type": "Plugin", "seedclean_enabled": False, "seedclean_cron": "0 */12 * * *", "seedclean_action": "pause", "seedclean_downloaders": [], "seedclean_size": "", "seedclean_ratio": "", "seedclean_time": "", "seedclean_upspeed": "", "seedclean_labels": "", "seedclean_pathkeywords": "", "seedclean_trackerkeywords": "", "seedclean_errorkeywords": "", "seedclean_torrentstates": "", "seedclean_torrentcategorys": "", "seedclean_samedata": False, "seedclean_mponly": False, "seedclean_notify": True, "seedclean_notify_type": "Plugin", "subfill_enabled": False, "subfill_details": [], "subfill_notify": False, "subfill_notify_type": "Plugin", "subfill_category_enabled": False, "subfill_category_confs": "", "msgnotify_enabled": False, "msgnotify_types": [], "msgnotify_servers": [], "msgnotify_notify_type": "MediaServer", "dltag_enabled": False, "dltag_downloaders": [], "dltag_prefix": "", "dltag_notify": True, "dltag_notify_type": "Plugin"}
