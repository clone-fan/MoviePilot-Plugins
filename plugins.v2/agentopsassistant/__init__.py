import json
import os
import shutil
import subprocess
import zipfile
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Tuple

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
# 「插件残留治理」的本地源码清理功能仅在用户显式配置后才会生效，
# 避免对未知系统使用写死的开发期路径执行删除。
DEFAULT_LOCAL_PLUGIN_REPO = ""


class AgentOpsAssistant(_PluginBase):
    """MP 运维助手：每日汇报、日志清理、备份、更新检查和插件残留治理。"""

    plugin_name = "MP 运维助手"
    plugin_desc = "面向 MoviePilot 的运维中枢：每日汇报、健康巡查、订阅提醒、站点统计、日志清理、备份与更新治理。"
    plugin_icon = "https://raw.githubusercontent.com/clone-fan/MoviePilot-Plugins/main/icons/agentopsassistant.png"
    plugin_version = "0.0.8"
    plugin_author = "wenking"
    author_url = "https://github.com/clone-fan"
    plugin_config_prefix = "agentopsassistant_"
    plugin_order = 50
    auth_level = 1

    MODULES: List[Dict[str, str]] = [
        {"key": "daily_report", "category": "report", "subcategory": "日报编排", "name": "每日汇报", "phase": "v1.4", "risk": "低", "status": "已直接接替", "source": "AgentOpsAssistant", "goal": "固定模板日报与定时/手动发送"},

        {"key": "subscribe_today", "category": "subscribe_center", "subcategory": "今日追新", "name": "今日追新", "phase": "v2.0", "risk": "低", "status": "待接替", "source": "SubscribeReminder + SubscribeOper", "goal": "直接接替订阅提醒的今日播出口径"},
        {"key": "subscribe_status", "category": "subscribe_center", "subcategory": "订阅状态", "name": "订阅状态总览", "phase": "v2.0", "risk": "低", "status": "待接替", "source": "SubscribeOper", "goal": "启用、待处理、缺集、今日追新统计"},
        {"key": "subscribe_lack", "category": "subscribe_center", "subcategory": "缺集提醒", "name": "缺集提醒", "phase": "v2.0", "risk": "低", "status": "规划中", "source": "SubscribeOper", "goal": "缺集订阅 Top 列表与提醒"},
        {"key": "subscribe_notify", "category": "subscribe_center", "subcategory": "提醒推送", "name": "订阅提醒推送", "phase": "v2.0", "risk": "低", "status": "规划中", "source": "AgentOpsAssistant", "goal": "由本插件独立发送订阅提醒，原插件可卸载"},

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

        {"key": "plugin_uninstall", "category": "plugin", "subcategory": "插件残留", "name": "插件残留治理", "phase": "v1.4", "risk": "高", "status": "预览已接替", "source": "AgentOpsAssistant", "goal": "插件残留预览、备份与确认删除"},
    ]

    _enabled = False
    _local_plugin_repo = DEFAULT_LOCAL_PLUGIN_REPO
    _daily_report_enabled = True
    _daily_report_cron = "0 22 * * *"
    _daily_report_greeting = "少爷"
    _health_in_report = True
    _subscribe_in_report = True
    _site_stat_in_report = True
    _log_clean_enabled = False
    _log_clean_cron = "0 3 * * 1"
    _log_clean_rows = 300
    _log_clean_selected_ids: List[str] = []
    _log_clean_notify = True
    _backup_enabled = False
    _backup_cron = "0 4 * * 1"
    _backup_keep_count = 5
    _backup_path = "/config/plugins/AgentOpsAssistant/Backup"
    _backup_notify = True
    _mp_update_enabled = False
    _mp_update_cron = "0 9 * * *"
    _mp_update_notify = True
    _mp_update_restart_confirm = False
    _mp_update_types: List[str] = ["后端", "前端"]
    _market_update_enabled = False
    _market_update_interval = 86400
    _market_update_notify = True
    _market_update_write_settings = False
    _market_update_write_env = False
    _market_update_blacklist: List[str] = []
    _market_update_wiki_url = "https://wiki.movie-pilot.org/zh/plugin"
    _plugin_uninstall_id = ""
    _plugin_uninstall_delete_source = False
    _plugin_uninstall_notify = True
    _last_summary = "尚未执行"


    def init_plugin(self, config: dict = None):
        config = config or {}
        self._enabled = bool(config.get("enabled"))
        self._local_plugin_repo = config.get("local_plugin_repo") or DEFAULT_LOCAL_PLUGIN_REPO
        self._daily_report_enabled = bool(config.get("daily_report_enabled", True))
        self._daily_report_cron = config.get("daily_report_cron") or "0 22 * * *"
        self._daily_report_greeting = str(config.get("daily_report_greeting") or "少爷").strip() or "少爷"
        self._health_in_report = bool(config.get("health_in_report", True))
        self._subscribe_reminder_enabled = bool(config.get("subscribe_reminder_enabled", config.get("subscribe_in_report", True)))
        self._site_stat_enabled = bool(config.get("site_stat_enabled", config.get("site_stat_in_report", True)))
        self._subscribe_in_report = bool(config.get("subscribe_in_report", self._subscribe_reminder_enabled)) and self._subscribe_reminder_enabled
        self._site_stat_in_report = bool(config.get("site_stat_in_report", self._site_stat_enabled)) and self._site_stat_enabled
        self._subscribe_reminder_onlyonce = bool(config.get("subscribe_reminder_onlyonce", False))
        self._subscribe_reminder_time = str(config.get("subscribe_reminder_time") or "9")
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
        self._backup_enabled = bool(config.get("backup_enabled", False))
        self._backup_onlyonce = bool(config.get("backup_onlyonce", False))
        self._backup_cron = config.get("backup_cron") or "0 4 * * 1"
        self._backup_keep_count = self._safe_int(config.get("backup_keep_count"), 5, 1)
        self._backup_path = config.get("backup_path") or "/config/plugins/AgentOpsAssistant/Backup"
        self._backup_notify = bool(config.get("backup_notify", True))
        self._backup_webdav_enabled = bool(config.get("backup_webdav_enabled", False))
        self._backup_webdav_notify = bool(config.get("backup_webdav_notify", False))
        self._backup_webdav_digest_auth = bool(config.get("backup_webdav_digest_auth", False))
        self._backup_webdav_disable_check = bool(config.get("backup_webdav_disable_check", False))
        self._backup_webdav_hostname = str(config.get("backup_webdav_hostname") or "").strip()
        self._backup_webdav_login = str(config.get("backup_webdav_login") or "").strip()
        self._backup_webdav_password = str(config.get("backup_webdav_password") or "")
        self._backup_webdav_max_count = self._safe_int(config.get("backup_webdav_max_count"), 5, 1)
        self._mp_update_enabled = bool(config.get("mp_update_enabled", False))
        self._mp_update_cron = config.get("mp_update_cron") or "0 9 * * *"
        self._mp_update_notify = bool(config.get("mp_update_notify", True))
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
        self._market_update_auto_get = bool(config.get("market_update_auto_get", False))
        self._market_update_proxy = bool(config.get("market_update_proxy", True))
        self._market_update_timeout = self._safe_int(config.get("market_update_timeout"), 5, 1)
        self._market_update_wiki_url = config.get("market_update_wiki_url") or "https://wiki.movie-pilot.org/zh/plugin"
        self._market_update_wiki_xpath = config.get("market_update_wiki_xpath") or '//pre[@class="prismjs line-numbers" and @v-pre="true"]/code/text()'
        self._plugin_uninstall_id = str(config.get("plugin_uninstall_id") or "").strip()
        self._plugin_uninstall_ids = config.get("plugin_uninstall_ids") or ([] if not self._plugin_uninstall_id else [self._plugin_uninstall_id])
        if isinstance(self._plugin_uninstall_ids, str):
            self._plugin_uninstall_ids = self._parse_csv(self._plugin_uninstall_ids)
        self._plugin_uninstall_clear_config = bool(config.get("plugin_uninstall_clear_config", True))
        self._plugin_uninstall_clear_data = bool(config.get("plugin_uninstall_clear_data", True))
        self._plugin_uninstall_delete_source = bool(config.get("plugin_uninstall_delete_source", False))
        self._plugin_uninstall_notify = bool(config.get("plugin_uninstall_notify", True))
        self._last_summary = self._build_summary()

    def get_state(self) -> bool:
        return self._enabled

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        return [
            {"cmd": "/mpops_report", "event": EventType.PluginAction, "desc": "发送 MP 运维每日汇报", "category": "MP运维", "data": {"action": "mpops_report"}},
            {"cmd": "/mpops_report_preview", "event": EventType.PluginAction, "desc": "预览 MP 运维每日汇报（不发送）", "category": "MP运维", "data": {"action": "mpops_report_preview"}},
            {"cmd": "/mpops_health", "event": EventType.PluginAction, "desc": "执行 MP 运维健康巡查", "category": "MP运维", "data": {"action": "mpops_health"}},
            {"cmd": "/mpops_logs", "event": EventType.PluginAction, "desc": "预览 MoviePilot 日志清理范围", "category": "MP运维", "data": {"action": "mpops_logs"}},
            {"cmd": "/mpops_logs_clean", "event": EventType.PluginAction, "desc": "执行插件日志清理（按保留行数截断）", "category": "MP运维", "data": {"action": "mpops_logs_clean"}},
            {"cmd": "/mpops_backup", "event": EventType.PluginAction, "desc": "执行 MP 运维助手自动备份", "category": "MP运维", "data": {"action": "mpops_backup"}},
            {"cmd": "/mpops_updates", "event": EventType.PluginAction, "desc": "检查 MoviePilot 后端/前端更新", "category": "MP运维", "data": {"action": "mpops_updates"}},
            {"cmd": "/mpops_market", "event": EventType.PluginAction, "desc": "检查插件库更新并按确认写入", "category": "MP运维", "data": {"action": "mpops_market"}},
            {"cmd": "/mpops_run_all", "event": EventType.PluginAction, "desc": "依次执行每日汇报与健康巡查", "category": "MP运维", "data": {"action": "mpops_run_all"}},
            {"cmd": "/mpops_plugin_preview", "event": EventType.PluginAction, "desc": "预览插件残留治理范围", "category": "MP运维", "data": {"action": "mpops_plugin_preview"}},
            {"cmd": "/mpops_plugin_clean", "event": EventType.PluginAction, "desc": "执行插件残留治理（需配置页显式确认）", "category": "MP运维", "data": {"action": "mpops_plugin_clean"}},
            {"cmd": "/agentops_heartbeat", "event": EventType.PluginAction, "desc": "兼容旧命令：发送每日汇报", "category": "MP运维", "data": {"action": "mpops_report"}},
            {"cmd": "/agentops_run_all", "event": EventType.PluginAction, "desc": "兼容旧命令：执行全部低风险任务", "category": "MP运维", "data": {"action": "mpops_run_all"}},
        ]

    def get_api(self) -> List[Dict[str, Any]]:
        return [
            {"path": "/dashboard", "endpoint": self.api_dashboard, "auth": "bear", "methods": ["GET"], "summary": "仪表盘数据：模块状态、最近执行、健康概览"},
            {"path": "/installed_plugins", "endpoint": self.api_installed_plugins, "auth": "bear", "methods": ["GET"], "summary": "已安装插件列表，供残留清理下拉选择"},
            {"path": "/plugin_markets", "endpoint": self.api_plugin_markets, "auth": "bear", "methods": ["GET"], "summary": "已配置插件库仓库列表，供更新黑名单下拉选择"},
            {"path": "/run_daily_report", "endpoint": self.api_run_daily_report, "auth": "bear", "methods": ["POST"], "summary": "立即发送每日汇报"},
            {"path": "/preview_daily_report", "endpoint": self.api_preview_daily_report, "auth": "bear", "methods": ["POST"], "summary": "预览每日汇报（不发送）"},
            {"path": "/run_health_check", "endpoint": self.api_run_health_check, "auth": "bear", "methods": ["POST"], "summary": "立即执行健康巡查"},
            {"path": "/preview_log_clean", "endpoint": self.api_preview_log_clean, "auth": "bear", "methods": ["POST"], "summary": "预览日志清理范围"},
            {"path": "/run_log_clean", "endpoint": self.api_run_log_clean, "auth": "bear", "methods": ["POST"], "summary": "执行插件日志清理"},
            {"path": "/run_backup", "endpoint": self.api_run_backup, "auth": "bear", "methods": ["POST"], "summary": "执行MP运维助手自动备份"},
            {"path": "/run_mp_update", "endpoint": self.api_run_mp_update, "auth": "bear", "methods": ["POST"], "summary": "立即检查MoviePilot后端/前端更新并通知"},
            {"path": "/preview_market_update", "endpoint": self.api_preview_market_update, "auth": "bear", "methods": ["POST"], "summary": "预览插件库更新"},
            {"path": "/run_market_update", "endpoint": self.api_run_market_update, "auth": "bear", "methods": ["POST"], "summary": "执行插件库更新检查并按确认写入"},
            {"path": "/preview_plugin_uninstall", "endpoint": self.api_preview_plugin_uninstall, "auth": "bear", "methods": ["POST"], "summary": "预览插件残留治理范围"},
            {"path": "/run_plugin_uninstall", "endpoint": self.api_run_plugin_uninstall, "auth": "bear", "methods": ["POST"], "summary": "执行插件残留治理"},
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
            services.append({"id": "AgentOpsAssistant.DailyReport", "name": "MP 运维助手 - 每日汇报", "trigger": CronTrigger.from_crontab(self._daily_report_cron), "func": self.run_daily_report, "kwargs": {}})
        if self._log_clean_enabled:
            services.append({"id": "AgentOpsAssistant.LogClean", "name": "MP 运维助手 - 插件日志清理", "trigger": CronTrigger.from_crontab(self._log_clean_cron), "func": self.run_log_clean, "kwargs": {}})
        if self._backup_enabled:
            services.append({"id": "AgentOpsAssistant.Backup", "name": "MP 运维助手 - 自动备份", "trigger": CronTrigger.from_crontab(self._backup_cron), "func": self.run_backup, "kwargs": {}})
        if self._mp_update_enabled:
            services.append({"id": "AgentOpsAssistant.MPUpdate", "name": "MP 运维助手 - MoviePilot更新检查", "trigger": CronTrigger.from_crontab(self._mp_update_cron), "func": self.run_update_preview, "kwargs": {}})
        if self._market_update_enabled:
            services.append({"id": "AgentOpsAssistant.MarketUpdate", "name": "MP 运维助手 - 插件库更新检查", "trigger": IntervalTrigger(seconds=self._market_update_interval), "func": self.run_market_update, "kwargs": {}})
        return services

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        """Vue 模式下配置页由 Config 组件渲染，这里只返回安全配置模型。"""
        return [], self._default_config()

    def get_page(self) -> List[dict]:
        """Vue 模式下详情页由 Page 组件（仪表盘）渲染，这里返回空列表以注册入口。"""
        return []

    def stop_service(self):
        pass

    @eventmanager.register(EventType.PluginAction)
    def handle_command(self, event: Event = None):
        if not event:
            return
        action = (event.event_data or {}).get("action", "")
        handlers = {
            "mpops_report": [("每日汇报", self.run_daily_report)],
            "mpops_report_preview": [("预览每日汇报", self.run_daily_report_preview)],
            "mpops_health": [("健康巡查", self.run_health_check)],
            "mpops_logs": [("日志清理预览", self.run_log_preview)],
            "mpops_logs_clean": [("日志清理", self.run_log_clean)],
            "mpops_backup": [("自动备份", self.run_backup)],
            "mpops_updates": [("更新状态预览", self.run_update_preview)],
            "mpops_market": [("插件库更新", self.run_market_update)],
            "mpops_run_all": [("每日汇报", self.run_daily_report), ("健康巡查", self.run_health_check)],
            "mpops_plugin_preview": [("插件治理预览", self.run_plugin_uninstall_preview)],
            "mpops_plugin_clean": [("插件残留治理", self.run_plugin_uninstall_clean)],
        }
        tasks = handlers.get(action)
        if not tasks:
            return
        results = []
        for name, runner in tasks:
            ok = bool(runner())
            results.append(f"{name}：{'成功' if ok else '失败'}")
        self.post_message(mtype=NotificationType.Plugin, title="MP 运维助手命令执行结果", text="\n".join(results))

    def run_daily_report(self) -> bool:
        name = "MP运维每日汇报"
        try:
            text = self._build_daily_report_message()
            self.post_message(mtype=NotificationType.Plugin, title="MP 运维每日汇报", text=text)
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
            text = self._build_daily_report_message()
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
        icons = ["🕒", "🤖", "📡", "📈", "⬇️", "📦", "📺", "💾", "✅", "⚠️"]
        return sum(1 for icon in icons if icon in (text or ""))

    def api_preview_daily_report(self) -> Dict[str, Any]:
        success = bool(self.run_daily_report_preview())
        data = self.get_data("last_daily_report_preview") or self.get_data("last_daily_report") or {}
        return {"code": 0 if success else 1, "msg": "每日汇报预览已生成" if success else "每日汇报预览失败", "data": data, "text": (data or {}).get("text", "")}

    def api_run_daily_report(self) -> Dict[str, Any]:
        return self._api_run_task("每日汇报", self.run_daily_report)

    def run_health_check(self) -> bool:
        data = self._build_health_summary()
        text = self._format_health_summary(data)
        self._save_task_result("健康巡查", bool(data.get("success")), 0 if data.get("success") else 1, text)
        return bool(data.get("success"))

    def api_run_health_check(self) -> Dict[str, Any]:
        return self._api_run_task("健康巡查", self.run_health_check)

    def api_run_mp_update(self) -> Dict[str, Any]:
        return self._api_run_task("主程序更新检查", self.run_update_preview)

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
                        "output": (health.get("output") or "")[:600],
                    },
                },
            }
        except Exception as err:
            logger.error(f"仪表盘数据获取失败：{err}")
            return {"code": 1, "msg": f"仪表盘数据获取失败：{err}", "data": {}}

    def api_installed_plugins(self) -> Dict[str, Any]:
        """已安装插件列表，供残留清理下拉选择（排除本插件自身）。"""
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
        data = self._build_log_preview()
        return {"code": 0, "msg": "日志清理预览完成，未删除任何文件。", "data": data, "text": self._format_log_preview_text(data)}

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
                self.post_message(mtype=NotificationType.Plugin, title="MP 运维助手 - 日志清理完成", text=text)
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
        data = self._build_update_status()
        return {"code": 0, "msg": "更新状态预览完成，未执行更新或重启。", "data": data, "text": self._format_update_status_text(data)}

    def api_preview_market_update(self) -> Dict[str, Any]:
        data = self._build_market_update_status(apply=False)
        return {"code": 0, "msg": "插件库更新预览完成，未写入配置。", "data": data, "text": self._format_market_update_text(data)}

    def api_run_market_update(self) -> Dict[str, Any]:
        ok = self.run_market_update()
        data = self._build_market_status()
        return {"code": 0 if ok else 1, "msg": "插件库更新检查执行成功" if ok else "插件库更新检查失败，详情请查看插件日志。", "data": data}

    def api_preview_plugin_uninstall(self) -> Dict[str, Any]:
        data = self._build_plugin_uninstall_status(clean=False)
        return {"code": 0 if data.get("success", True) else 1, "msg": "插件残留治理预览完成，未删除任何文件。", "data": data, "text": self._format_plugin_uninstall_text(data)}

    def api_run_plugin_uninstall(self) -> Dict[str, Any]:
        ok = self.run_plugin_uninstall_clean()
        data = self._build_plugin_uninstall_status(clean=False)
        return {"code": 0 if ok else 1, "msg": "插件残留治理执行成功" if ok else "插件残留治理未执行或失败，详情请查看插件日志。", "data": data}

    def run_plugin_uninstall_preview(self) -> bool:
        data = self._build_plugin_uninstall_status(clean=False)
        text = self._format_plugin_uninstall_text(data)
        self.post_message(mtype=NotificationType.Plugin, title="MP 运维助手 - 插件残留治理预览", text=text)
        self._save_task_result("插件治理预览", bool(data.get("success", True)), 0 if data.get("success", True) else 1, text)
        return bool(data.get("success", True))

    def run_plugin_uninstall_clean(self) -> bool:
        if not (self._plugin_uninstall_id or self._plugin_uninstall_ids):
            text = "未执行：请先在配置页填写目标插件 ID。"
            self._save_task_result("插件残留治理", False, 2, text)
            if self._plugin_uninstall_notify:
                self.post_message(mtype=NotificationType.Plugin, title="MP 运维助手 - 插件残留清理未执行", text=text)
            return False
        try:
            data = self._build_plugin_uninstall_status(clean=True)
            text = self._format_plugin_uninstall_text(data)
            if self._plugin_uninstall_notify:
                self.post_message(mtype=NotificationType.Plugin, title="MP 运维助手 - 插件残留治理结果", text=text)
            self._save_task_result("插件残留治理", bool(data.get("success")), 0 if data.get("success") else 1, text)
            return bool(data.get("success"))
        except Exception as err:
            self._save_task_result("插件残留治理", False, -1, str(err))
            logger.error(f"AgentOpsAssistant 插件残留治理执行失败：{err}")
            return False

    def run_update_preview(self) -> bool:
        data = self._build_update_status()
        text = self._format_update_status_text(data)
        self.post_message(mtype=NotificationType.Plugin, title="MP 运维助手 - 更新状态预览", text=text)
        self._save_task_result("更新状态预览", True, 0, text)
        return True

    def run_market_update(self) -> bool:
        try:
            data = self._build_market_update_status(apply=True)
            text = self._format_market_update_text(data)
            if self._market_update_notify and data.get("has_update"):
                self.post_message(mtype=NotificationType.Plugin, title="MP 运维助手 - 插件库更新检查", text=text)
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
                self.post_message(mtype=NotificationType.Plugin, title="MP 运维助手 - 自动备份完成", text=text)
            self._save_task_result("自动备份", bool(data.get("success")), 0 if data.get("success") else 1, text)
            return bool(data.get("success"))
        except Exception as err:
            self._save_task_result("自动备份", False, -1, str(err))
            logger.error(f"AgentOpsAssistant 自动备份执行失败：{err}")
            return False

    def _api_run_task(self, name: str, runner) -> Dict[str, Any]:
        success = bool(runner())
        return {"code": 0 if success else 1, "msg": f"{name}执行{'成功' if success else '失败'}，详情请查看插件日志。"}

    def _build_daily_report_message(self) -> str:
        """复刻 locked-heartbeat-report fixed-v1 模板。"""
        return self._build_heartbeat_message()

    def _build_heartbeat_message(self) -> str:
        latest = self._github_latest_v2()
        site_increment = self._get_site_increment_locked()
        site_health = self._get_site_health_locked()
        transfers = self._get_today_transfers_locked()
        transfer_health = self._get_transfer_health_locked()
        subs = self._get_today_subscribe_updates_locked()
        downloads = self._get_downloading_locked()
        downloader_health = self._get_downloader_health_locked()
        storage_health = self._get_storage_health_locked()
        version_line = f"⦁ 版本：{self._frontend_backend_version_line()}"
        app_version = self._backend_version_value()
        if latest != "未取到" and self._normalize_version(latest) == self._normalize_version(app_version):
            version_line += "，已是最新"

        lines = [
            self._daily_greeting_locked(),
            "",
            f"🕒 时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "🤖 MoviePilot：",
            version_line,
        ]
        if latest != "未取到" and self._normalize_version(latest) != self._normalize_version(app_version):
            lines.append(f"⦁ 最新版本：{latest} / {latest}，{self._daily_report_greeting}记得抽空更新一下")

        lines.extend(["", "📡 站点状态："])
        lines.extend(site_health)
        lines.extend(["", "📈 站点增量："])
        lines.extend(site_increment)
        lines.extend(["", "⬇️ 下载器："])
        lines.extend(downloader_health)
        if not (downloader_health == ["⦁ 正在下载：无"] or downloader_health == ["⦁ 无"]) and downloads != ["⦁ 无"]:
            lines.append("⦁ 当前任务：")
            lines.extend(downloads[:5])
        lines.extend(["", "📦 入库整理："])
        lines.extend(transfer_health)
        lines.extend(transfers if transfers != ["⦁ 无"] else ["⦁ 今日入库：无"])
        lines.extend(["", "📺 订阅追新："])
        lines.extend([f"⦁ {x}" for x in subs] if subs else ["⦁ 今日追新：无"])
        lines.extend(["", "💾 存储空间："])
        lines.extend(storage_health)
        lines.extend([""])
        lines.extend(self._get_summary_locked(site_health, transfer_health, downloader_health, storage_health))
        return "\n".join(lines)

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
        success = sum(1 for r in rows if getattr(r, "status", False))
        failed_rows = [r for r in rows if not getattr(r, "status", False)]
        items = [f"⦁ 今日成功：{success}｜失败：{len(failed_rows)}"]
        for r in failed_rows[:3]:
            title = getattr(r, "title", None) or "未命名"
            errmsg = str(getattr(r, "errmsg", None) or getattr(r, "message", None) or "").strip()
            items.append(f"⦁ 失败：{title} - {errmsg[:36]}" if errmsg else f"⦁ 失败：{title}")
        return items

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
                current_day = getattr(current, "updated_day", None) or ""
                err_msg = str(getattr(current, "err_msg", None) or "").strip()
                if current_day != today:
                    continue
                if err_msg:
                    result.append(f"⦁ {site_name}：异常 - {err_msg}")
                    continue
                previous = None
                for i in range(1, 8):
                    prev_day = (datetime.strptime(current_day, "%Y-%m-%d") - timedelta(days=i)).strftime("%Y-%m-%d")
                    if prev_day not in previous_cache:
                        previous_cache[prev_day] = site_oper.get_userdata_by_date(prev_day) or []
                    prev_map = {getattr(row, "name", None): row for row in previous_cache[prev_day] if row and not getattr(row, "err_msg", None)}
                    previous = prev_map.get(site_name)
                    if previous:
                        break
                if not previous:
                    continue
                upload_delta = max(0, int(getattr(current, "upload", 0) or 0) - int(getattr(previous, "upload", 0) or 0))
                download_delta = max(0, int(getattr(current, "download", 0) or 0) - int(getattr(previous, "download", 0) or 0))
                if upload_delta == 0 and download_delta == 0:
                    continue
                extras = []
                ratio = getattr(current, "ratio", None)
                bonus = getattr(current, "bonus", None)
                if ratio not in (None, ""):
                    extras.append(f"分享率 {ratio}")
                if bonus not in (None, ""):
                    try:
                        extras.append(f"魔力 {float(bonus):.0f}")
                    except Exception:
                        extras.append(f"魔力 {bonus}")
                suffix = "｜" + "｜".join(extras) if extras else ""
                result.append(f"⦁ {site_name}：↑ {self._format_bytes(upload_delta)} ｜ ↓ {self._format_bytes(download_delta)}{suffix}")
            return result or ["⦁ 无"]
        except Exception as e:
            return [f"⦁ 异常 - {e}"]

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
            normal = stale = 0
            errors = []
            for row in latest:
                name = getattr(row, "name", None) or getattr(row, "domain", None) or "未知站点"
                err = str(getattr(row, "err_msg", None) or "").strip()
                day = getattr(row, "updated_day", None) or ""
                if err:
                    errors.append(f"{name}：{err[:24]}")
                elif day == today:
                    normal += 1
                else:
                    stale += 1
            items = [f"⦁ 今日快照：正常 {normal}｜数据过期 {stale}｜异常 {len(errors)}"]
            items.extend([f"⦁ {err}" for err in errors[:3]])
            return items
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

    def _get_storage_health_locked(self) -> List[str]:
        """获取存储空间状态，优先使用MP配置的目录和存储类型"""
        try:
            from app.helper.directory import DirectoryHelper
            from app.db.systemconfig_oper import SystemConfigOper
            from app.schemas.types import SystemConfigKey

            items = []
            seen_paths = set()

            # 优先读取 MP 配置的下载目录和媒体库目录
            dir_helper = DirectoryHelper()
            download_dirs = dir_helper.get_download_dirs() or []
            library_dirs = dir_helper.get_library_dirs() or []

            # 获取存储配置
            storage_configs = {}
            try:
                storage_conf_list = SystemConfigOper().get(SystemConfigKey.Storages) or []
                for sc in storage_conf_list:
                    storage_configs[sc.get("name")] = sc.get("type", "local")
            except Exception:
                pass

            # 处理下载目录
            for d in download_dirs:
                path = getattr(d, "download_path", None) or getattr(d, "path", None)
                storage_name = getattr(d, "storage", None)
                if not path or path in seen_paths:
                    continue
                seen_paths.add(path)
                storage_type = storage_configs.get(storage_name, "local") if storage_name else "local"
                label = f"下载目录（{storage_type}）"
                self._add_storage_item(items, path, label, storage_type)

            # 处理媒体库目录
            for d in library_dirs:
                path = getattr(d, "library_path", None) or getattr(d, "path", None)
                storage_name = getattr(d, "library_storage", None) or getattr(d, "storage", None)
                if not path or path in seen_paths:
                    continue
                seen_paths.add(path)
                storage_type = storage_configs.get(storage_name, "local") if storage_name else "local"
                label = f"媒体库（{storage_type}）"
                self._add_storage_item(items, path, label, storage_type)

            # 如果没有配置目录，回退到硬编码路径
            if not items:
                for candidate, label in [("/downloads", "下载目录"), ("/media", "媒体库"), ("/config", "配置目录")]:
                    if os.path.exists(candidate) and candidate not in seen_paths:
                        seen_paths.add(candidate)
                        self._add_storage_item(items, candidate, f"{label}（本地）", "local")

            return items or ["⦁ 未检测到存储"]
        except Exception as e:
            logger.warning(f"获取存储空间失败：{e}")
            return [f"⦁ 存储检查异常：{e}"]

    def _add_storage_item(self, items: List[str], path: str, label: str, storage_type: str):
        """添加存储项到列表"""
        try:
            if storage_type == "local":
                total, used, free = shutil.disk_usage(path)
                pct = used / total * 100 if total else 0
                risk = "，空间偏紧" if pct >= 85 else ""
                items.append(f"⦁ {label}：剩余 {self._format_bytes(free)}｜已用 {pct:.0f}%{risk}")
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
            return ["⚠️ 今日提醒："] + warnings[:5]
        return ["✅ 今日摘要：", "⦁ 系统正常", "⦁ 站点快照正常", "⦁ 无失败转移", "⦁ 下载器无异常"]

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
        if result["moviepilot"]["has_update"] and self._mp_update_notify:
            text = self._format_update_status_text(result)
            self.post_message(mtype=NotificationType.Plugin, title="MP 运维助手 - MoviePilot更新检查", text=text)
        if result["moviepilot"]["has_update"] and self._mp_update_restart_confirm:
            try:
                from app.helper.system import SystemHelper
                SystemHelper.restart()
                result["moviepilot"]["restart_dispatched"] = True
            except Exception as err:
                result["moviepilot"]["restart_error"] = str(err)
        return result

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
        return "\n".join(lines)

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
                    copied.append("postgresql_backup.sql")
                else:
                    errors.append(msg)
            manifest = {"created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "db_type": str(settings.DB_TYPE), "copied": copied, "errors": errors}
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
                    mtype=NotificationType.Plugin,
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

    @staticmethod
    def _dump_postgresql(target: Path) -> Tuple[bool, str]:
        if not shutil.which("pg_dump"):
            return False, "pg_dump 不存在，无法导出 PostgreSQL 数据库；已保留配置文件备份。"
        env = os.environ.copy()
        env["PGPASSWORD"] = str(settings.DB_POSTGRESQL_PASSWORD)
        cmd = ["pg_dump", "-h", str(settings.DB_POSTGRESQL_HOST), "-p", str(settings.DB_POSTGRESQL_PORT), "-U", str(settings.DB_POSTGRESQL_USERNAME), "-d", str(settings.DB_POSTGRESQL_DATABASE), "-f", str(target)]
        result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=600, check=False)
        if result.returncode != 0:
            return False, (result.stderr or result.stdout or "pg_dump 执行失败")[-500:]
        return True, "OK"

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
            f"⦁ 模式：直接接替 AutoBackup",
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
        plugin_id = self._normalize_plugin_id(self._plugin_uninstall_id)
        result = {"success": True, "dry_run": not clean, "plugin_id": plugin_id, "note": "只治理插件残留文件/日志/备份目录；不会删除媒体文件、下载任务或 MoviePilot 核心源码。", "candidates": [], "deleted": [], "errors": [], "backup_path": "", "blocked": ""}
        if not plugin_id:
            result.update({"success": False, "blocked": "请先填写插件ID。"})
            return result
        if plugin_id.lower() in {"agentopsassistant", "mpops", "moviepilot"}:
            result.update({"success": False, "blocked": "为避免自毁或误删核心组件，禁止治理 AgentOpsAssistant / MoviePilot 本体。"})
            return result
        candidates = self._plugin_uninstall_candidates(plugin_id)
        result["candidates"] = candidates
        if not clean:
            return result
        backup_path = self._backup_plugin_uninstall_candidates(plugin_id, candidates)
        result["backup_path"] = backup_path
        for item in candidates:
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
        result["success"] = not result["errors"]
        return result

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
        title = "🧩 插件残留治理预览" if data.get("dry_run") else "🧩 插件残留治理结果"
        lines = [title, f"⦁ 插件ID：{data.get('plugin_id') or '未填写'}", f"⦁ 说明：{data.get('note')}"]
        if data.get("blocked"):
            lines.append(f"⦁ 阻止原因：{data.get('blocked')}")
            return "\n".join(lines)
        candidates = data.get("candidates") or []
        lines.append(f"⦁ 候选残留：{len(candidates)} 项")
        for item in candidates[:8]:
            lines.append(f"⦁ {item.get('kind')}｜{item.get('type')}｜{item.get('size_text')}｜{item.get('path')}")
        if data.get("dry_run"):
            lines.append("⦁ 状态：仅预览，未删除。")
        else:
            lines.append(f"⦁ 已删除：{len(data.get('deleted') or [])} 项")
            lines.append(f"⦁ 备份：{data.get('backup_path') or '未生成'}")
        if data.get("errors"):
            lines.append("异常：")
            lines.extend([f"⦁ {e}" for e in data.get("errors", [])[:5]])
        return "\n".join(lines)

    @staticmethod
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

    def _build_health_summary(self) -> Dict[str, Any]:
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
        success = all(x["ok"] for x in checks)
        result = {"success": success, "checks": checks, "total": len(checks), "pass": len([x for x in checks if x["ok"]]), "fail": len([x for x in checks if not x["ok"]])}
        # 保存健康巡查结果
        self.save_data("last_health_check", {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "success": success,
            "output": self._format_health_summary(result),
        })
        return result

    @staticmethod
    def _format_health_summary(data: Dict[str, Any]) -> str:
        name_map = {"subscribe": "订阅", "sites": "站点", "downloaders": "下载器", "agentops_services": "本插件任务"}
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
            {"key": "log_clean", "name": "日志清理", "enabled": self._log_clean_enabled, "last_keys": ["last_log_clean", "last_log_clean_preview"], "next": self._log_clean_cron, "icon": "mdi-broom"},
            {"key": "backup", "name": "自动备份", "enabled": self._backup_enabled, "last_keys": ["last_backup"], "next": self._backup_cron, "icon": "mdi-database-arrow-up"},
            {"key": "mp_update", "name": "MP 更新", "enabled": self._mp_update_enabled, "last_keys": ["last_update_preview"], "next": self._mp_update_cron, "icon": "mdi-update"},
            {"key": "market_update", "name": "插件库", "enabled": self._market_update_enabled, "last_keys": ["last_market_update"], "next": f"每 {self._market_update_interval // 3600 if self._market_update_interval else 0} 小时", "icon": "mdi-puzzle-check"},
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
    @staticmethod
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
    @staticmethod
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
    @staticmethod
    @staticmethod
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
    def _slug(name: str) -> str:
        return {"MP运维每日汇报": "daily_report", "每日汇报": "daily_report", "预览每日汇报": "daily_report_preview", "日报预览": "daily_report_preview", "健康巡查": "health_check", "日志清理": "log_clean", "日志清理预览": "log_clean_preview", "自动备份": "backup", "插件库更新": "market_update", "更新状态预览": "update_preview", "插件治理预览": "plugin_uninstall_preview", "插件残留治理": "plugin_uninstall"}.get(name, "task")

    @staticmethod
    def _parse_csv(value: Any) -> List[str]:
        if isinstance(value, list):
            return [str(x).strip() for x in value if str(x).strip()]
        return [x.strip() for x in str(value or "").split(",") if x.strip()]

    @staticmethod
    def _default_config() -> Dict[str, Any]:
        return {"enabled": False, "daily_report_enabled": True, "daily_report_cron": "0 22 * * *", "daily_report_greeting": "少爷", "health_in_report": True, "subscribe_in_report": True, "site_stat_in_report": True, "subscribe_reminder_enabled": True, "subscribe_reminder_onlyonce": False, "subscribe_reminder_time": "9", "subscribe_reminder_subtype": ["movie", "tv"], "subscribe_reminder_msgtype": "Subscribe", "site_stat_enabled": True, "site_stat_onlyonce": False, "site_stat_dashboard_type": "today", "site_stat_notify_type": "inc", "log_clean_enabled": False, "log_clean_cron": "0 3 * * 1", "log_clean_rows": 300, "log_clean_selected_ids": "", "log_clean_notify": True, "log_clean_onlyonce": False, "backup_enabled": False, "backup_onlyonce": False, "backup_cron": "0 4 * * 1", "backup_keep_count": 5, "backup_path": "/config/plugins/AgentOpsAssistant/Backup", "backup_notify": True, "backup_webdav_enabled": False, "backup_webdav_notify": False, "backup_webdav_digest_auth": False, "backup_webdav_disable_check": False, "backup_webdav_hostname": "", "backup_webdav_login": "", "backup_webdav_password": "", "backup_webdav_max_count": 5, "mp_update_enabled": False, "mp_update_cron": "0 9 * * *", "mp_update_notify": True, "mp_update_restart_confirm": False, "mp_update_types": ["后端", "前端"], "market_update_enabled": False, "market_update_onlyonce": False, "market_update_interval": 86400, "market_update_notify": True, "market_update_write_notify": False, "market_update_notify_type": "Plugin", "market_update_write_settings": False, "market_update_write_env": False, "market_update_blacklist_enabled": False, "market_update_blacklist": "", "market_update_auto_get": False, "market_update_proxy": True, "market_update_timeout": 5, "market_update_wiki_url": "https://wiki.movie-pilot.org/zh/plugin", "market_update_wiki_xpath": '//pre[@class="prismjs line-numbers" and @v-pre="true"]/code/text()', "plugin_uninstall_id": "", "plugin_uninstall_ids": [], "plugin_uninstall_clear_config": True, "plugin_uninstall_clear_data": True, "plugin_uninstall_delete_source": False, "plugin_uninstall_notify": True}
