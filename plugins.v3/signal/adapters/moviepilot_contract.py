from typing import Any, Dict, List, Tuple

from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from app.sdk.logging import logger
from app.schemas.types import EventType

# SIGNAL-OWNERSHIP: plugin-contract host declaration boundary. Keep MoviePilot's
# public commands, APIs, pages, scheduler, and dashboard declarations together.
class PluginContractMixin:
    """MoviePilot plugin contract, render entry, scheduler, and dashboard declarations."""

    MP_FREE_MODULE_IDENTITY = {
        "pluginId": "Signal",
        "expose": "Dashboard",
        "surface": "mp-widget",
        "contract": "signal-mp-free-dashboard/v1",
    }

    @staticmethod
    def get_command() -> List[Dict[str, Any]]:
        return [
            {"cmd": "/signal_subscribe", "event": EventType.PluginAction, "desc": "立即推送订阅追新", "category": "Signal", "data": {"action": "signal_subscribe"}},
            {"cmd": "/signal_health", "event": EventType.PluginAction, "desc": "执行 Signal 健康巡查", "category": "Signal", "data": {"action": "signal_health"}},
            {"cmd": "/signal_logs", "event": EventType.PluginAction, "desc": "预览 MoviePilot 日志清理范围", "category": "Signal", "data": {"action": "signal_logs"}},
            {"cmd": "/signal_logs_clean", "event": EventType.PluginAction, "desc": "执行插件日志清理（按保留行数截断）", "category": "Signal", "data": {"action": "signal_logs_clean"}},
            {"cmd": "/signal_backup", "event": EventType.PluginAction, "desc": "执行 Signal 自动备份", "category": "Signal", "data": {"action": "signal_backup"}},
            {"cmd": "/signal_updates", "event": EventType.PluginAction, "desc": "检查 MoviePilot 后端/前端更新", "category": "Signal", "data": {"action": "signal_updates"}},
            {"cmd": "/signal_market", "event": EventType.PluginAction, "desc": "同步插件库记录", "category": "Signal", "data": {"action": "signal_market"}},
            {"cmd": "/signal_plugin_updates", "event": EventType.PluginAction, "desc": "检查插件更新并发送提醒", "category": "Signal", "data": {"action": "signal_plugin_updates"}},
            {"cmd": "/signal_plugin_install", "event": EventType.PluginAction, "desc": "按范围自动安装插件更新", "category": "Signal", "data": {"action": "signal_plugin_install"}},
            {"cmd": "/signal_run_all", "event": EventType.PluginAction, "desc": "依次执行健康巡查与站点统计", "category": "Signal", "data": {"action": "signal_run_all"}},
            {"cmd": "/signal_plugin_preview", "event": EventType.PluginAction, "desc": "预览插件卸载与残留清理范围", "category": "Signal", "data": {"action": "signal_plugin_preview"}},
            {"cmd": "/signal_plugin_clean", "event": EventType.PluginAction, "desc": "插件卸载安全提示（需在配置页显式确认后执行）", "category": "Signal", "data": {"action": "signal_plugin_clean"}},
            {"cmd": "/signal_seed_clean", "event": EventType.PluginAction, "desc": "执行自动删种（按规则暂停/删除种子）", "category": "Signal", "data": {"action": "signal_seed_clean"}},
        ]

    def get_api(self) -> List[Dict[str, Any]]:
        return [
            {"path": "/dashboard", "endpoint": self.api_dashboard, "auth": "bear", "methods": ["GET"], "summary": "仪表盘数据：模块状态、最近执行、健康概览"},
            {"path": "/tg_console_status", "endpoint": self.api_tg_console_status, "auth": "bear", "methods": ["GET"], "summary": "Telegram 融合汇报卡状态"},
            {"path": "/preview_tg_console", "endpoint": self.api_preview_tg_console, "auth": "bear", "methods": ["POST"], "summary": "预览 Telegram 融合汇报卡 HTML"},
            {"path": "/create_tg_console_card", "endpoint": self.api_create_tg_console_card, "auth": "bear", "methods": ["POST"], "summary": "立即创建融合通知卡"},
            {"path": "/reset_tg_console_card", "endpoint": self.api_reset_tg_console_card, "auth": "bear", "methods": ["POST"], "summary": "重置 Telegram 融合汇报卡"},
            {"path": "/installed_plugins", "endpoint": self.api_installed_plugins, "auth": "bear", "methods": ["GET"], "summary": "已安装插件列表，供插件卸载下拉选择"},
            {"path": "/plugin_markets", "endpoint": self.api_plugin_markets, "auth": "bear", "methods": ["GET"], "summary": "已配置插件库仓库列表，供更新黑名单下拉选择"},
            {"path": "/refresh_tg_console_card", "endpoint": self.api_refresh_tg_console_card, "auth": "bear", "methods": ["POST"], "summary": "刷新当前融合通知卡"},
            {"path": "/run_subscribe_reminder", "endpoint": self.api_run_subscribe_reminder, "auth": "bear", "methods": ["POST"], "summary": "立即推送订阅追新"},
            {"path": "/run_today_transfer", "endpoint": self.api_run_today_transfer, "auth": "bear", "methods": ["POST"], "summary": "立即刷新今日入库"},
            {"path": "/run_health_check", "endpoint": self.api_run_health_check, "auth": "bear", "methods": ["POST"], "summary": "立即执行健康巡查"},
            {"path": "/preview_log_clean", "endpoint": self.api_preview_log_clean, "auth": "bear", "methods": ["POST"], "summary": "预览日志清理范围"},
            {"path": "/run_log_clean", "endpoint": self.api_run_log_clean, "auth": "bear", "methods": ["POST"], "summary": "执行插件日志清理"},
            {"path": "/run_backup", "endpoint": self.api_run_backup, "auth": "bear", "methods": ["POST"], "summary": "执行完整 Signal 备份"},
            {"path": "/backup_archives", "endpoint": self.api_backup_archives, "auth": "bear", "methods": ["POST"], "summary": "按来源列出可恢复归档"},
            {"path": "/backup_archive", "endpoint": self.api_backup_archive, "auth": "bear", "methods": ["POST"], "summary": "检查归档 manifest、哈希与恢复能力"},
            {"path": "/import_backup_archive", "endpoint": self.api_import_backup_archive, "auth": "bear", "methods": ["POST"], "summary": "导入并检查浏览器归档"},
            {"path": "/download_backup_archive", "endpoint": self.api_download_backup_archive, "auth": "bear", "methods": ["POST"], "summary": "下载手动备份归档"},
            {"path": "/run_backup_restore", "endpoint": self.api_run_backup_restore, "auth": "bear", "methods": ["POST"], "summary": "按稳定 backup_id 执行选择性在线恢复"},
            {"path": "/backup_operation_status", "endpoint": self.api_backup_operation_status, "auth": "bear", "methods": ["GET"], "summary": "查询当前备份恢复操作和最近结果"},
            {"path": "/run_mp_update", "endpoint": self.api_run_mp_update, "auth": "bear", "methods": ["POST"], "summary": "立即检查并更新MoviePilot后端/前端"},
            {"path": "/run_mp_update_apply", "endpoint": self.api_run_mp_update_apply, "auth": "bear", "methods": ["POST"], "summary": "执行MoviePilot后端/前端更新并重启"},
            {"path": "/preview_market_update", "endpoint": self.api_preview_market_update, "auth": "bear", "methods": ["POST"], "summary": "预览插件库同步"},
            {"path": "/run_market_update", "endpoint": self.api_run_market_update, "auth": "bear", "methods": ["POST"], "summary": "执行插件库同步"},
            {"path": "/preview_plugin_update_reminder", "endpoint": self.api_preview_plugin_update_reminder, "auth": "bear", "methods": ["POST"], "summary": "预览插件更新"},
            {"path": "/run_plugin_update_reminder", "endpoint": self.api_run_plugin_update_reminder, "auth": "bear", "methods": ["POST"], "summary": "执行插件更新检查"},
            {"path": "/preview_plugin_auto_install", "endpoint": self.api_preview_plugin_auto_install, "auth": "bear", "methods": ["POST"], "summary": "预览插件自动安装"},
            {"path": "/run_plugin_auto_install", "endpoint": self.api_run_plugin_auto_install, "auth": "bear", "methods": ["POST"], "summary": "执行插件自动安装"},
            {"path": "/preview_plugin_uninstall", "endpoint": self.api_preview_plugin_uninstall, "auth": "bear", "methods": ["POST"], "summary": "预览插件卸载与残留清理范围"},
            {"path": "/run_plugin_uninstall", "endpoint": self.api_run_plugin_uninstall, "auth": "bear", "methods": ["POST"], "summary": "执行插件卸载与残留清理"},
            {"path": "/agentopsassistant_purge_status", "endpoint": self.api_agentopsassistant_purge_status, "auth": "bear", "methods": ["GET"], "summary": "只读检查 AgentOpsAssistant 固定目标残留"},
            {"path": "/run_agentopsassistant_purge", "endpoint": self.api_run_agentopsassistant_purge, "auth": "bear", "methods": ["POST"], "summary": "无备份彻底专杀固定目标 AgentOpsAssistant"},
            {"path": "/run_seed_clean", "endpoint": self.api_run_seed_clean, "auth": "bear", "methods": ["POST"], "summary": "立即执行自动删种"},
            {"path": "/downloaders", "endpoint": self.api_downloaders, "auth": "bear", "methods": ["GET"], "summary": "已配置下载器列表，供自动删种下拉选择"},
            {"path": "/mediaservers", "endpoint": self.api_mediaservers, "auth": "bear", "methods": ["GET"], "summary": "已配置媒体服务器列表，供媒体库通知过滤"},
            {"path": "/subfill_clear_history", "endpoint": self.api_subfill_clear_history, "auth": "bear", "methods": ["POST"], "summary": "清理订阅规则填充历史记录"},
            {"path": "/subfill_clear_handled", "endpoint": self.api_subfill_clear_handled, "auth": "bear", "methods": ["POST"], "summary": "清理订阅规则填充已处理记录"},
            {"path": "/site_stat_chart", "endpoint": self.api_site_stat_chart, "auth": "bear", "methods": ["GET"], "summary": "今日各站点上传/下载增量，供仪表盘饼图"},
            {"path": "/run_site_stat", "endpoint": self.api_run_site_stat, "auth": "bear", "methods": ["POST"], "summary": "刷新站点数据统计"},
            {"path": "/preview_downloader_helper", "endpoint": self.api_preview_downloader_helper, "auth": "bear", "methods": ["POST"], "summary": "预览下载器助手失效任务候选"},
            {"path": "/run_downloader_helper", "endpoint": self.api_run_downloader_helper, "auth": "bear", "methods": ["POST"], "summary": "执行下载器助手"},
            {"path": "/downloader_overview", "endpoint": self.api_downloader_overview, "auth": "bear", "methods": ["GET"], "summary": "下载器活动种子概览"},
        ]

    @staticmethod
    def get_render_mode() -> Tuple[str, str]:
        """声明使用 MoviePilot Vue 联邦组件渲染。"""
        return "vue", "dist/assets"

    def get_sidebar_nav(self) -> List[Dict[str, Any]]:
        """注册主界面侧栏全页入口。

        nav_key 为 `config` 时，V3 前端按 PascalCase 解析为 `./AppPageConfig`，
        与 Signal 既有的联邦暴露名一致，因此不需要新增或改名前端入口。
        """
        if not self.get_state():
            return []
        return [
            {
                "nav_key": "config",
                "title": "媒体融合 Signal",
                "icon": "mdi-radar",
                "section": "system",
                "permission": "admin",
                "order": 50,
            }
        ]

    def get_service(self) -> List[Dict[str, Any]]:
        if not self.get_state():
            return []
        services = []

        def can_register(component: str, schedule_enabled: bool = True) -> bool:
            ok, _ = self._runtime_gate("scheduler", component=component, name=component)
            return bool(schedule_enabled and ok)

        fusion_notify_on = can_register("fusion_notify")
        if fusion_notify_on:
            self._append_cron_service(services, "Signal.FusionCardCreate", "Signal - 建立融合卡", self._fusion_card_create_cron, self.run_fusion_card_create)
            self._append_cron_service(services, "Signal.FusionCardRefresh", "Signal - 周期刷新融合卡", self._fusion_card_refresh_cron, self.run_fusion_card_refresh)
        if can_register("subscribe_reminder", self._subscribe_reminder_schedule_enabled):
            self._append_cron_service(services, "Signal.SubscribeReminder", "Signal - 订阅追新推送", self._subscribe_reminder_cron, self.run_subscribe_reminder_scheduled)
        if can_register("site_stat", self._site_stat_schedule_enabled):
            self._append_cron_service(services, "Signal.SiteStat", "Signal - 站点数据统计", self._site_stat_cron, self.run_site_stat_scheduled)
        if can_register("health_check", self._health_check_schedule_enabled):
            self._append_cron_service(services, "Signal.HealthCheck", "Signal - 健康巡查", self._health_check_cron, self.run_health_check_scheduled)
        if can_register("log_clean", self._log_clean_schedule_enabled):
            self._append_cron_service(services, "Signal.LogClean", "Signal - 插件日志清理", self._log_clean_cron, self.run_log_clean_scheduled)
        if can_register("backup", self._backup_enabled):
            self._append_cron_service(services, "Signal.Backup", "Signal - 自动备份", self._backup_cron, self.run_backup_scheduled)
        if can_register("mp_update", bool(self._mp_update_enabled and self._mp_update_cron)):
            self._append_cron_service(services, "Signal.MPUpdate", "Signal - 系统更新检查", self._mp_update_cron, self.run_mp_update_scheduled)
        if can_register("market_update", bool(self._market_update_enabled and self._market_update_cron)):
            self._append_cron_service(services, "Signal.MarketUpdate", "Signal - 插件库同步", self._market_update_cron, self.run_market_update_scheduled)
        if can_register("plugin_update_reminder", bool(self._plugin_update_reminder_enabled and self._plugin_update_reminder_cron)):
            self._append_cron_service(services, "Signal.PluginUpdateReminder", "Signal - 插件更新", self._plugin_update_reminder_cron, self.run_plugin_update_reminder_scheduled)
        if can_register("seed_clean", self._seedclean_schedule_enabled) and self._seedclean_downloaders:
            self._append_cron_service(services, "Signal.SeedClean", "Signal - 自动删种", self._seedclean_cron, self.run_seed_clean_scheduled)
        if can_register("dltag", bool(self._dltag_cron)):
            self._append_cron_service(services, "Signal.DownloaderHelper", "Signal - 下载器助手", self._dltag_cron, self.run_downloader_helper_scheduled)
        if fusion_notify_on:
            services.append({"id": "Signal.FusionMediaActivityPrune", "name": "Signal - 媒体动态过期清理", "trigger": IntervalTrigger(seconds=60), "func": self.prune_fusion_media_activity, "kwargs": {}, "schedule": self._format_interval_schedule(60)})
        return services

    @staticmethod
    def _append_cron_service(services: List[Dict[str, Any]], service_id: str, name: str, cron: str, func) -> None:
        cron_text = str(cron or "").strip()
        if len(cron_text.split()) != 5:
            logger.warning(f"Signal 定时服务 {name} cron 配置无效，已跳过：{cron}")
            return
        try:
            trigger = CronTrigger.from_crontab(cron_text)
        except Exception as err:
            logger.warning(f"Signal 定时服务 {name} cron 配置无效，已跳过：{cron}；{err}")
            return
        services.append({"id": service_id, "name": name, "trigger": trigger, "func": func, "kwargs": {}, "schedule": cron_text})

    @staticmethod
    def _format_interval_schedule(seconds: Any) -> str:
        try:
            value = int(seconds or 0)
        except (TypeError, ValueError):
            value = 0
        if value <= 0:
            return "间隔未配置"
        if value % 86400 == 0:
            return f"每 {value // 86400} 天"
        if value % 3600 == 0:
            return f"每 {value // 3600} 小时"
        if value % 60 == 0:
            return f"每 {value // 60} 分钟"
        return f"每 {value} 秒"

    def get_form(self) -> Tuple[List[dict], Dict[str, Any]]:
        """Vue 模式下配置页由 Config 组件渲染，这里返回当前有效值。"""
        model = dict(self._default_config())
        # MoviePilot merges this model with the raw saved config.  Legacy
        # configs do not contain the database switch, so expose the migrated
        # runtime value instead of making the UI display the false default.
        model["backup_database_enabled"] = bool(
            getattr(self, "_backup_database_enabled", False)
        )
        return [], model

    def get_page(self) -> List[dict]:
        """Vue 模式下详情页由 Page 组件（仪表盘）渲染，这里返回空列表以注册入口。"""
        return []

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
        frame = {
            "variant": "mp-native",
            "surface": "dashboard-widget",
            "density": widget.get("density", "compact"),
            "radius": "var(--app-surface-radius)",
            "border": "var(--app-surface-border)",
            "shadow": "var(--app-surface-shadow)",
            "background": "rgba(var(--v-theme-surface), var(--transparent-opacity))",
            "nativeSurfaceToken": "var(--v-theme-surface)",
            "cardBackgroundToken": "rgba(var(--v-theme-surface), var(--transparent-opacity))",
            "onSurfaceToken": "var(--v-theme-on-surface)",
            "transparentOpacity": "var(--transparent-opacity)",
            "transparentBlur": "var(--transparent-blur)",
        }
        attrs = {
            "surface": "mp-widget",
            "title": widget.get("title") or widget.get("name"),
            "subtitle": widget.get("subtitle", ""),
            "border": True,
            "component": widget["key"],
            "moduleIdentity": dict(self.MP_FREE_MODULE_IDENTITY, widget=widget["key"]),
            "components": {
                "subscribe_reminder": bool(self._subscribe_reminder_enabled),
                "site_stat": bool(self._site_stat_enabled),
                "health_check": bool(self._health_check_enabled),
                "backup": bool(self._backup_enabled),
                "log_clean": bool(self._log_clean_enabled),
                "mp_update": bool(self._mp_update_enabled),
                "market_update": bool(self._market_update_enabled),
                "plugin_update_reminder": bool(self._plugin_update_reminder_enabled),
                "seedclean": bool(self._seedclean_enabled),
                "dltag": bool(self._dltag_enabled),
            },
            "rows": widget.get("rows", 5),
            "refresh": 60,
            "frame": frame,
        }
        return cols, attrs, []

    def stop_service(self):
        try:
            runtime_stopped = self._stop_runtime_state()
            if runtime_stopped is False:
                logger.error("Signal 运行时停止未完成")
        except Exception as err:
            logger.error(f"Signal 运行时停止未完成：{err}")
        try:
            scheduler_cleaned = self._cleanup_scheduler_jobs()
            if scheduler_cleaned is False:
                logger.error("Signal 调度注销未完成")
        except Exception as err:
            logger.error(f"Signal 调度注销未完成：{err}")
