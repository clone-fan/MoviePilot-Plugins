import html
import json
import os
import re
import shutil
import subprocess
import tempfile
import zipfile
from datetime import datetime, timedelta
from functools import wraps
from pathlib import Path, PurePosixPath
from typing import Any, Dict, List, Optional, Tuple

from app.core.config import settings
from app.log import logger
from app.schemas import NotificationType
from app.utils.http import RequestUtils

from ..application.backup_models import BACKUP_OPERATION_LOCK
from ..domain import html_utils, site_helpers
from .lifecycle import DEFAULT_LOCAL_PLUGIN_REPO


def _serialize_backup_config_mutation(method):
    """Serialize Signal config activation with backup and restore operations."""
    @wraps(method)
    def wrapped(self, *args, **kwargs):
        with BACKUP_OPERATION_LOCK:
            return method(self, *args, **kwargs)
    return wrapped


class RuntimeStateMixin:
    plugin_name = "媒体融合 Signal"
    plugin_desc = "通知汇报、数据监控、下载管理、系统维护、插件卸载，你要的全在里面。"
    plugin_icon = "https://raw.githubusercontent.com/clone-fan/MoviePilot-Plugins/main/icons/signal.png"
    plugin_version = "1.0.25"
    plugin_author = "wenking"
    author_url = "https://github.com/clone-fan"
    plugin_config_prefix = "signal_"
    plugin_order = 50
    auth_level = 1

    MODULES: List[Dict[str, str]] = [

        {"key": "subscribe_today", "category": "subscribe_center", "subcategory": "今日追新", "name": "今日追新", "phase": "v2.0", "risk": "低", "status": "已直接接替", "source": "MoviePilot v2 订阅日历复合 API", "goal": "复用宿主日历今日播出口径"},
        {"key": "subscribe_status", "category": "subscribe_center", "subcategory": "订阅状态", "name": "订阅状态总览", "phase": "v2.0", "risk": "低", "status": "待接替", "source": "SubscribeOper", "goal": "启用、待处理、缺集、今日追新统计"},
        {"key": "subscribe_lack", "category": "subscribe_center", "subcategory": "缺集提醒", "name": "缺集提醒", "phase": "v2.0", "risk": "低", "status": "规划中", "source": "SubscribeOper", "goal": "缺集订阅 Top 列表与提醒"},
        {"key": "subscribe_notify", "category": "subscribe_center", "subcategory": "追新推送", "name": "订阅追新推送", "phase": "v2.0", "risk": "低", "status": "已直接接替", "source": "Signal + MoviePilot v2 订阅日历复合 API", "goal": "定时、手动、Fusion 和 Telegram 共用同一快照"},

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
        {"key": "backup", "category": "ops_tools", "subcategory": "配置备份", "name": "自动备份", "phase": "v1.1", "risk": "中", "status": "已直接接替", "source": "Signal", "goal": "打包配置/数据库/关键目录、保留策略清理"},
        {"key": "mp_update", "category": "ops_tools", "subcategory": "主程序", "name": "MoviePilot 更新推送", "phase": "v1.2", "risk": "中", "status": "已直接接替", "source": "Signal", "goal": "检查后端/前端 release 并通知"},
        {"key": "market_update", "category": "ops_tools", "subcategory": "更新管理", "name": "插件库同步", "phase": "v1.3", "risk": "中", "status": "已直接接替", "source": "Signal", "goal": "同步插件库记录、对比当前配置、通知变化"},

        {"key": "plugin_uninstall", "category": "plugin", "subcategory": "插件卸载", "name": "插件卸载", "phase": "v1.4", "risk": "高", "status": "已接入", "source": "Signal", "goal": "插件卸载、配置/数据清理与残留文件彻底删除"},
    ]

    _enabled = False
    _local_plugin_repo = DEFAULT_LOCAL_PLUGIN_REPO
    _fusion_report_greeting = "少爷"
    _tg_console_enabled = True
    _tg_console_poll_enabled = False
    _tg_console_poll_interval = 15
    _tg_console_allowed_user_ids: List[str] = []
    _tg_console_full_remote_enabled = False
    _tg_console_suppress_individual_notifications = True
    _tg_console_max_notices = 20
    _tg_console_last_error = ""
    _fusion_notify_enabled = True
    _fusion_notify_schedule_enabled = True
    _fusion_notify_cron = "0 * * * *"
    _fusion_card_create_cron = "5 0 * * *"
    _fusion_card_refresh_cron = "0 * * * *"
    _fusion_notify_msgtype = "Plugin"
    _fusion_notify_columns: List[str] = []
    _report_storage_targets: List[str] = ["config", "download", "library", "storages"]
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
    _subscribe_reminder_enabled = True
    _subscribe_reminder_schedule_enabled = True
    _subscribe_reminder_cron = "0 9 * * *"
    _site_stat_enabled = True
    _site_stat_schedule_enabled = True
    _site_stat_cron = "0 8 * * *"
    _site_stat_schedule_notify_enabled = True
    _site_stat_notify_type = "Plugin"
    _health_check_enabled: bool = True
    _health_check_schedule_enabled: bool = True
    _health_check_cron: str = "0 */6 * * *"
    _health_check_items: List[str] = []
    _health_check_database_targets: List[str] = []
    _health_check_storage_targets: List[str] = []
    _health_check_directory_targets: List[str] = []
    _health_check_storage_threshold: int = 85
    _health_check_notify: bool = True
    _health_check_completion_notify_enabled: bool = False
    _health_check_notify_type: str = "Plugin"
    _health_check_completion_notify_type: str = "Plugin"
    _report_health: bool = True
    _log_clean_enabled = False
    _log_clean_schedule_enabled = False
    _log_clean_cron = "0 3 * * 1"
    _log_clean_rows = 300
    _log_clean_selected_ids: List[str] = []
    _log_clean_notify = True
    _log_clean_notify_type = "Plugin"
    _backup_enabled = False
    _backup_database_enabled = False
    _backup_cron = "0 4 * * 1"
    _backup_keep_count = 5
    _backup_path = "/config/plugins/Signal/Backup"
    _backup_notify = False
    _backup_notify_type = "Plugin"
    _backup_webdav_enabled = False
    _backup_webdav_hostname = ""
    _backup_webdav_login = ""
    _backup_webdav_password = ""
    _backup_webdav_max_count = 5
    _backup_config: Dict[str, Any] = {}
    _backup_legacy_config_keys: List[str] = []
    _mp_update_enabled = False
    _mp_update_schedule_enabled = False
    _mp_update_cron = "0 9 * * *"
    _mp_update_types: List[str] = ["后端", "前端"]
    _market_update_enabled = False
    _market_update_schedule_enabled = False
    _market_update_cron = "0 9 * * *"
    _market_update_strategy = "check"
    _market_update_install_ids: List[str] = []
    _market_update_exclude_ids: List[str] = []
    _market_update_blacklist: List[str] = []
    _plugin_update_reminder_enabled = False
    _plugin_update_reminder_schedule_enabled = False
    _plugin_update_reminder_cron = "0 9 * * *"
    _mp_update_scheduled_notify = False
    _mp_update_notify_type = "Plugin"
    _market_update_scheduled_notify = False
    _market_update_notify_type = "Plugin"
    _plugin_update_reminder_scheduled_notify = False
    _plugin_update_reminder_notify_type = "Plugin"
    _plugin_auto_install_enabled = False
    _plugin_auto_install_schedule_enabled = False
    _plugin_auto_install_cron = "0 9 * * *"
    _plugin_auto_install_scheduled_notify = False
    _plugin_auto_install_notify_type = "Plugin"
    _plugin_auto_install_scope_mode = "all"
    _plugin_auto_install_install_ids: List[str] = []
    _plugin_auto_install_exclude_ids: List[str] = []
    _update_scheduled_notify = False
    _update_notify_type = "Plugin"
    _plugin_uninstall_clear_config = True
    _plugin_uninstall_clear_data = True
    _plugin_uninstall_delete_source = False
    _seedclean_enabled = False
    _seedclean_schedule_enabled = False
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
    _seedclean_trtorrentstates = ""
    _seedclean_torrentcategorys = ""
    _seedclean_samedata = False
    _seedclean_mponly = False
    _seedclean_notify = True
    _seedclean_notify_type = "Plugin"
    _subfill_enabled = False
    _subfill_details: List[str] = []
    _subfill_category_enabled = False
    _subfill_category_confs = ""
    _subfill_completion_notify_enabled = False
    _subfill_completion_notify_type = "Plugin"
    _subfill_confs: Dict[str, Any] = {}
    _msgnotify_enabled = False
    _msgnotify_types: List[str] = []
    _msgnotify_servers: List[str] = []
    _msgnotify_notify_type = "MediaServer"
    _dltag_enabled = False
    _dltag_downloaders: List[str] = []
    _dltag_tasks: List[str] = ["tagging", "seeding", "cleanup"]
    _dltag_cron = "0 */6 * * *"
    _dltag_listen_download = True
    _dltag_listen_source_file = False
    _dltag_prefix = ""
    _dltag_all_tags: List[str] = []
    _dltag_excluded_tags: List[str] = []
    _dltag_not_select_all_tag = "非全"
    _dltag_tracker_mappings = ""
    _dltag_source_delete_strategy = "delayed"
    _dltag_scheduled_notify = False
    _dltag_notify_type = "Plugin"
    _msg_seen: Dict[str, float] = {}
    _MSG_GROUPS = {
        "新入库": {"library.new", "ItemAdded"},
        "开始播放": {"playback.start", "media.play", "PlaybackStart"},
        "暂停播放": {"playback.pause", "media.pause", "PlaybackPause"},
        "停止播放": {"playback.stop", "media.stop", "PlaybackStop"},
        "登录成功": {"user.authenticated"},
        "登录失败": {"user.authenticationfailed"},
        "标记": {"item.rate"},
    }
    _MSG_LABEL = {"新入库": "新入库", "开始播放": "开始播放", "暂停播放": "暂停播放", "停止播放": "停止播放",
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
            "name": "Signal - 站点数据",
            "title": "站点数据",
            "subtitle": "上传下载增量、统计时间与站点占比",
            "md": 8,
            "rows": 29,
            "density": "comfortable",
        },
        {
            "key": "actions",
            "name": "Signal - 快捷操作",
            "title": "快捷操作",
            "subtitle": "常用运维动作",
            "md": 4,
            "rows": 27,
            "density": "compact",
        },
    ]
    COMPONENT_ENABLED_ATTRS: Dict[str, str] = {
        "fusion_notify": "_fusion_notify_enabled",
        "subscribe_reminder": "_subscribe_reminder_enabled",
        "site_stat": "_site_stat_enabled",
        "health_check": "_health_check_enabled",
        "log_clean": "_log_clean_enabled",
        "backup": "_backup_enabled",
        "mp_update": "_mp_update_enabled",
        "market_update": "_market_update_enabled",
        "plugin_update_reminder": "_plugin_update_reminder_enabled",
        "plugin_auto_install": "_plugin_auto_install_enabled",
        "seed_clean": "_seedclean_enabled",
        "seedclean": "_seedclean_enabled",
        "downloader_tag": "_dltag_enabled",
        "downloader_helper": "_dltag_enabled",
        "dltag": "_dltag_enabled",
        "msgnotify": "_msgnotify_enabled",
        "subfill_category": "_subfill_category_enabled",
    }

    @_serialize_backup_config_mutation
    def init_plugin(self, config: dict = None):
        config = config or {}
        self._load_plugin_config(config)
        self._reset_runtime_state()

    def get_state(self) -> bool:
        return self._is_runtime_active()

    def _component_enabled(self, key: Optional[str]) -> bool:
        if not key:
            return True
        if key == "subfill":
            return bool(getattr(self, "_subfill_enabled", False) or getattr(self, "_subfill_category_enabled", False))
        attr = self.COMPONENT_ENABLED_ATTRS.get(key)
        return bool(attr and getattr(self, attr, False))

    def _can_run_task(self, name: str, component: Optional[str] = None) -> Tuple[bool, str]:
        return self._runtime_gate("action", component=component, name=name)

    def _guard_task(self, name: str, component: Optional[str] = None) -> Tuple[bool, str]:
        ok, msg = self._can_run_task(name, component)
        if not ok:
            self._save_task_result(name, False, 2, msg)
        return ok, msg

    @staticmethod
    def _skipped_data(msg: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        payload = dict(data or {})
        payload.update({"code": 1, "msg": msg, "message": msg, "skipped": True})
        payload.setdefault("success", False)
        return payload

    @staticmethod
    def _config_bool(config: Dict[str, Any], key: str, default: bool = False) -> bool:
        if key not in config:
            return bool(default)
        value = config.get(key)
        if isinstance(value, str):
            return value.strip().lower() not in {"0", "false", "no", "off", ""}
        return bool(value)

    @classmethod
    def _schedule_flag(cls, config: Dict[str, Any], schedule_key: str, component_enabled: bool) -> bool:
        return cls._config_bool(config, schedule_key, component_enabled)


    @staticmethod
    def _format_media_ip_label(ip_value: Any) -> str:
        ip = str(ip_value or "").strip()
        if not ip:
            return ""
        local = False
        try:
            import ipaddress
            addr = ipaddress.ip_address(ip)
            local = addr.is_private or addr.is_loopback or addr.is_link_local
        except Exception:
            local = bool(re.match(r"^(10\.|192\.168\.|172\.(1[6-9]|2\d|3[01])\.)", ip))
        return f"{ip} 本地局域网" if local else ip


    # ===== 自动删种（功能移植自 jxxghp/MoviePilot-Plugins「自动删种」TorrentRemover，适配本插件）=====


    @staticmethod
    def _default_config() -> Dict[str, Any]:
        return {
            "enabled": False,
            "local_plugin_repo": DEFAULT_LOCAL_PLUGIN_REPO,
            "fusion_notify_enabled": True,
            "fusion_notify_msgtype": "Plugin",
            "fusion_card_create_cron": "5 0 * * *",
            "fusion_card_refresh_cron": "0 * * * *",
            "health_check_enabled": True,
            "health_check_schedule_enabled": True,
            "health_check_cron": "0 */6 * * *",
            "health_check_items": [],
            "health_check_database_targets": ["current"],
            "health_check_storage_targets": ["storages", "config", "download", "library"],
            "health_check_directory_targets": ["config", "plugin", "download", "library"],
            "health_check_storage_threshold": 85,
            "health_check_notify": True,
            "health_check_completion_notify_enabled": False,
            "health_check_notify_type": "Plugin",
            "health_check_completion_notify_type": "Plugin",
            "subscribe_reminder_enabled": True,
            "subscribe_reminder_schedule_enabled": True,
            "subscribe_reminder_cron": "0 9 * * *",
            "subscribe_reminder_msgtype": "Subscribe",
            "site_stat_enabled": True,
            "site_stat_schedule_enabled": True,
            "site_stat_cron": "0 8 * * *",
            "site_stat_schedule_notify_enabled": True,
            "site_stat_dashboard_type": "today",
            "site_stat_notify_type": "Plugin",
            "log_clean_enabled": False,
            "log_clean_schedule_enabled": False,
            "log_clean_cron": "0 3 * * 1",
            "log_clean_rows": 300,
            "log_clean_selected_ids": [],
            "log_clean_notify": True,
            "log_clean_notify_type": "Plugin",
            "backup_enabled": False,
            "backup_database_enabled": False,
            "backup_cron": "0 4 * * 1",
            "backup_keep_count": 5,
            "backup_path": "/config/plugins/Signal/Backup",
            "backup_notify": False,
            "backup_notify_type": "Plugin",
            "backup_webdav_enabled": False,
            "backup_webdav_digest_auth": False,
            "backup_webdav_disable_check": False,
            "backup_webdav_hostname": "",
            "backup_webdav_login": "",
            "backup_webdav_password": "",
            "backup_webdav_max_count": 5,
            "mp_update_enabled": False,
            "mp_update_schedule_enabled": False,
            "mp_update_cron": "0 9 * * *",
            "mp_update_types": ["后端", "前端"],
            "market_update_enabled": False,
            "market_update_schedule_enabled": False,
            "market_update_cron": "0 9 * * *",
            "market_update_strategy": "check",
            "market_update_install_ids": [],
            "market_update_exclude_ids": [],
            "market_update_blacklist": [],
            "plugin_update_reminder_enabled": False,
            "plugin_update_reminder_schedule_enabled": False,
            "plugin_update_reminder_cron": "0 9 * * *",
            "mp_update_scheduled_notify": False,
            "mp_update_notify_type": "Plugin",
            "market_update_scheduled_notify": False,
            "market_update_notify_type": "Plugin",
            "plugin_update_reminder_scheduled_notify": False,
            "plugin_update_reminder_notify_type": "Plugin",
            "plugin_auto_install_enabled": False,
            "plugin_auto_install_schedule_enabled": False,
            "plugin_auto_install_cron": "0 9 * * *",
            "plugin_auto_install_scheduled_notify": False,
            "plugin_auto_install_notify_type": "Plugin",
            "plugin_auto_install_scope_mode": "all",
            "plugin_auto_install_install_ids": [],
            "plugin_auto_install_exclude_ids": [],
            "update_scheduled_notify": False,
            "update_notify_type": "Plugin",
            "plugin_uninstall_ids": [],
            "plugin_uninstall_clear_config": True,
            "plugin_uninstall_clear_data": True,
            "plugin_uninstall_delete_source": False,
            "seedclean_enabled": False,
            "seedclean_schedule_enabled": False,
            "seedclean_cron": "0 */12 * * *",
            "seedclean_action": "pause",
            "seedclean_downloaders": [],
            "seedclean_size": "",
            "seedclean_ratio": "",
            "seedclean_time": "",
            "seedclean_upspeed": "",
            "seedclean_labels": "",
            "seedclean_pathkeywords": "",
            "seedclean_trackerkeywords": "",
            "seedclean_errorkeywords": "",
            "seedclean_torrentstates": "",
            "seedclean_trtorrentstates": "",
            "seedclean_torrentcategorys": "",
            "seedclean_samedata": False,
            "seedclean_mponly": False,
            "seedclean_notify": True,
            "seedclean_notify_type": "Plugin",
            "subfill_enabled": False,
            "subfill_details": [],
            "subfill_category_enabled": False,
            "subfill_category_confs": "",
            "subfill_completion_notify_enabled": False,
            "subfill_completion_notify_type": "Plugin",
            "msgnotify_enabled": False,
            "msgnotify_types": [],
            "msgnotify_servers": [],
            "msgnotify_notify_type": "MediaServer",
            "dltag_enabled": False,
            "dltag_downloaders": [],
            "dltag_tasks": ["tagging", "seeding", "cleanup"],
            "dltag_cron": "0 */6 * * *",
            "dltag_listen_download": True,
            "dltag_listen_source_file": False,
            "dltag_prefix": "",
            "dltag_all_tags": [],
            "dltag_excluded_tags": [],
            "dltag_not_select_all_tag": "非全",
            "dltag_tracker_mappings": "",
            "dltag_source_delete_strategy": "delayed",
            "dltag_scheduled_notify": False,
            "dltag_notify_type": "Plugin",
        }
