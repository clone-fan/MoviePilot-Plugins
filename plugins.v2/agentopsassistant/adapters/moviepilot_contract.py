from typing import Any, Dict, List, Tuple

from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from app.log import logger
from app.schemas.types import EventType

# AOA-OWNERSHIP: plugin-contract host declaration boundary. Keep MoviePilot's
# public commands, APIs, pages, scheduler, and dashboard declarations together.
class PluginContractMixin:
    """MoviePilot plugin contract, render entry, scheduler, and dashboard declarations."""

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
            {"cmd": "/mpops_plugin_clean", "event": EventType.PluginAction, "desc": "插件卸载安全提示（需在配置页显式确认后执行）", "category": "MP运维", "data": {"action": "mpops_plugin_clean"}},
            {"cmd": "/mpops_seed_clean", "event": EventType.PluginAction, "desc": "执行自动删种（按规则暂停/删除种子）", "category": "MP运维", "data": {"action": "mpops_seed_clean"}},
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
            {"path": "/run_daily_report", "endpoint": self.api_run_daily_report, "auth": "bear", "methods": ["POST"], "summary": "立即刷新融合汇报"},
            {"path": "/run_subscribe_reminder", "endpoint": self.api_run_subscribe_reminder, "auth": "bear", "methods": ["POST"], "summary": "立即推送订阅追新"},
            {"path": "/run_today_transfer", "endpoint": self.api_run_today_transfer, "auth": "bear", "methods": ["POST"], "summary": "立即刷新今日入库"},
            {"path": "/preview_daily_report", "endpoint": self.api_preview_daily_report, "auth": "bear", "methods": ["POST"], "summary": "预览每日汇报（不发送）"},
            {"path": "/run_health_check", "endpoint": self.api_run_health_check, "auth": "bear", "methods": ["POST"], "summary": "立即执行健康巡查"},
            {"path": "/preview_log_clean", "endpoint": self.api_preview_log_clean, "auth": "bear", "methods": ["POST"], "summary": "预览日志清理范围"},
            {"path": "/run_log_clean", "endpoint": self.api_run_log_clean, "auth": "bear", "methods": ["POST"], "summary": "执行插件日志清理"},
            {"path": "/run_backup", "endpoint": self.api_run_backup, "auth": "bear", "methods": ["POST"], "summary": "执行MP运维助手自动备份"},
            {"path": "/backup_archives", "endpoint": self.api_backup_archives, "auth": "bear", "methods": ["GET"], "summary": "列出本地可恢复备份包"},
            {"path": "/preview_backup_restore", "endpoint": self.api_preview_backup_restore, "auth": "bear", "methods": ["POST"], "summary": "预览本地备份恢复内容"},
            {"path": "/run_backup_restore", "endpoint": self.api_run_backup_restore, "auth": "bear", "methods": ["POST"], "summary": "执行本地备份一键恢复"},
            {"path": "/webdav_backup_archives", "endpoint": self.api_webdav_backup_archives, "auth": "bear", "methods": ["GET"], "summary": "列出 WebDAV 可恢复备份包"},
            {"path": "/preview_webdav_backup_restore", "endpoint": self.api_preview_webdav_backup_restore, "auth": "bear", "methods": ["POST"], "summary": "预览 WebDAV 备份恢复内容"},
            {"path": "/run_webdav_backup_restore", "endpoint": self.api_run_webdav_backup_restore, "auth": "bear", "methods": ["POST"], "summary": "执行 WebDAV 备份一键恢复"},
            {"path": "/preview_updates", "endpoint": self.api_preview_updates, "auth": "bear", "methods": ["POST"], "summary": "预览MoviePilot后端/前端更新状态（不通知、不重启）"},
            {"path": "/run_mp_update", "endpoint": self.api_run_mp_update, "auth": "bear", "methods": ["POST"], "summary": "立即检查MoviePilot后端/前端更新并记录状态"},
            {"path": "/run_mp_update_apply", "endpoint": self.api_run_mp_update_apply, "auth": "bear", "methods": ["POST"], "summary": "执行MoviePilot后端/前端更新并重启"},
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
            {"path": "/preview_downloader_helper", "endpoint": self.api_preview_downloader_helper, "auth": "bear", "methods": ["POST"], "summary": "预览下载器助手失效任务候选"},
            {"path": "/run_downloader_helper", "endpoint": self.api_run_downloader_helper, "auth": "bear", "methods": ["POST"], "summary": "执行下载器助手"},
            {"path": "/downloader_overview", "endpoint": self.api_downloader_overview, "auth": "bear", "methods": ["GET"], "summary": "下载器活动种子概览"},
        ]

    @staticmethod
    def get_render_mode() -> Tuple[str, str]:
        """声明使用 MoviePilot Vue 联邦组件渲染。"""
        return "vue", "dist/assets"

    def get_service(self) -> List[Dict[str, Any]]:
        if not self.get_state():
            return []
        services = []

        def can_register(component: str, schedule_enabled: bool = True) -> bool:
            ok, _ = self._runtime_gate("scheduler", component=component, name=component)
            return bool(schedule_enabled and ok)

        fusion_notify_on = can_register("fusion_notify")
        if fusion_notify_on:
            self._append_cron_service(services, "AgentOpsAssistant.FusionCardCreate", "MP 运维助手 - 每日建立融合卡", self._fusion_card_create_cron, self.run_daily_fusion_card_create)
            self._append_cron_service(services, "AgentOpsAssistant.FusionCardRefresh", "MP 运维助手 - 周期刷新融合卡", self._fusion_card_refresh_cron, self.run_daily_fusion_card_refresh)
        if can_register("subscribe_reminder", self._subscribe_reminder_schedule_enabled):
            self._append_cron_service(services, "AgentOpsAssistant.SubscribeReminder", "MP 运维助手 - 订阅追新推送", self._subscribe_reminder_cron, self.run_subscribe_reminder)
        if can_register("site_stat", self._site_stat_schedule_enabled):
            self._append_cron_service(services, "AgentOpsAssistant.SiteStat", "MP 运维助手 - 站点数据统计", self._site_stat_cron, self.run_site_stat_scheduled)
        if can_register("health_check", self._health_check_schedule_enabled):
            self._append_cron_service(services, "AgentOpsAssistant.HealthCheck", "MP 运维助手 - 健康巡查", self._health_check_cron, self.run_health_check)
        if can_register("log_clean", self._log_clean_schedule_enabled):
            self._append_cron_service(services, "AgentOpsAssistant.LogClean", "MP 运维助手 - 插件日志清理", self._log_clean_cron, self.run_log_clean_scheduled)
        if can_register("backup", self._backup_schedule_enabled):
            self._append_cron_service(services, "AgentOpsAssistant.Backup", "MP 运维助手 - 自动备份", self._backup_cron, self.run_backup_scheduled)
        if can_register("mp_update", self._mp_update_schedule_enabled):
            self._append_cron_service(services, "AgentOpsAssistant.MPUpdate", "MP 运维助手 - MoviePilot更新检查", self._mp_update_cron, self.run_mp_update_scheduled)
        if can_register("market_update", self._market_update_schedule_enabled):
            self._append_cron_service(services, "AgentOpsAssistant.MarketUpdate", "MP 运维助手 - 插件库更新检查", self._market_update_cron, self.run_market_update_scheduled)
        if can_register("seed_clean", self._seedclean_schedule_enabled) and self._seedclean_downloaders:
            self._append_cron_service(services, "AgentOpsAssistant.SeedClean", "MP 运维助手 - 自动删种", self._seedclean_cron, self.run_seed_clean_scheduled)
        if can_register("dltag", bool(self._dltag_cron)):
            self._append_cron_service(services, "AgentOpsAssistant.DownloaderHelper", "MP 运维助手 - 下载器助手", self._dltag_cron, self.run_downloader_helper_scheduled)
        if fusion_notify_on:
            services.append({"id": "AgentOpsAssistant.FusionMediaActivityPrune", "name": "MP 运维助手 - 媒体动态过期清理", "trigger": IntervalTrigger(seconds=60), "func": self.prune_fusion_media_activity, "kwargs": {}, "schedule": self._format_interval_schedule(60)})
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
        """Vue 模式下配置页由 Config 组件渲染，这里返回当前字段默认值。"""
        return [], dict(self._default_config())

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
            "components": {
                "subscribe_reminder": bool(self._subscribe_reminder_enabled),
                "site_stat": bool(self._site_stat_enabled),
                "health_check": bool(self._health_check_enabled),
                "backup": bool(self._backup_enabled),
                "log_clean": bool(self._log_clean_enabled),
                "mp_update": bool(self._mp_update_enabled),
                "market_update": bool(self._market_update_enabled),
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
            self._stop_runtime_state()
        except Exception as err:
            logger.warning(f"AgentOpsAssistant stop_service cleanup failed: {err}")
        try:
            self._cleanup_scheduler_jobs()
        except Exception as err:
            logger.warning(f"AgentOpsAssistant scheduler cleanup failed: {err}")
