"""Dashboard card / schema constructors extracted from the main plugin class.

Pure dict builders for the MP dashboard ``get_page`` payload. Instance
methods (``self``) read live state via MRO; staticmethods are stateless.
"""

from typing import Any, Dict, List, Tuple

from .effective_state import derive_effective_state


class DashboardSchemaMixin:
    """Mixin bundling dashboard card / schema construction helpers."""

    def _task_definitions(self) -> List[Dict[str, Any]]:
        return [
            {"key": "daily_report", "name": "每日汇报", "enabled": self._daily_report_enabled, "schedule_required": True, "schedule_enabled": self._daily_report_enabled, "cron": self._daily_report_cron, "last_keys": ["last_daily_report", "last_daily_report_preview"], "next": self._daily_report_cron, "icon": "mdi-newspaper-variant"},
            {"key": "subscribe_reminder", "name": "订阅追新", "enabled": self._subscribe_reminder_enabled, "schedule_required": True, "schedule_enabled": self._subscribe_reminder_schedule_enabled, "cron": self._subscribe_reminder_cron, "last_keys": ["last_subscribe_reminder"], "next": self._subscribe_reminder_cron, "icon": "mdi-bell-ring"},
            {"key": "site_stat", "name": "站点统计", "enabled": self._site_stat_enabled, "schedule_required": True, "schedule_enabled": self._site_stat_schedule_enabled, "cron": self._site_stat_cron, "last_keys": ["last_site_stat"], "next": self._site_stat_cron, "icon": "mdi-chart-pie"},
            {"key": "health_check", "name": "健康巡查", "enabled": self._health_check_enabled, "schedule_required": True, "schedule_enabled": self._health_check_schedule_enabled, "cron": self._health_check_cron, "last_keys": ["last_health_check"], "next": self._health_check_cron, "icon": "mdi-heart-pulse"},
            {"key": "log_clean", "name": "日志清理", "enabled": self._log_clean_enabled, "schedule_required": True, "schedule_enabled": self._log_clean_schedule_enabled, "cron": self._log_clean_cron, "last_keys": ["last_log_clean", "last_log_clean_preview"], "next": self._log_clean_cron, "icon": "mdi-broom"},
            {"key": "backup", "name": "自动备份", "enabled": self._backup_enabled, "schedule_required": True, "schedule_enabled": self._backup_schedule_enabled, "cron": self._backup_cron, "last_keys": ["last_backup"], "next": self._backup_cron, "icon": "mdi-database-arrow-up"},
            {"key": "mp_update", "name": "MP 更新", "enabled": self._mp_update_enabled, "schedule_required": True, "schedule_enabled": self._mp_update_schedule_enabled, "cron": self._mp_update_cron, "last_keys": ["last_update_preview"], "next": self._mp_update_cron, "icon": "mdi-update"},
            {"key": "market_update", "name": "插件库", "enabled": self._market_update_enabled, "schedule_required": True, "schedule_enabled": self._market_update_schedule_enabled, "cron": self._market_update_cron, "last_keys": ["last_market_update"], "next": self._market_update_cron, "icon": "mdi-puzzle-check"},
            {"key": "downloader_helper", "name": "下载器助手", "enabled": self._dltag_enabled, "required_config_ready": bool(self._dltag_tasks), "last_keys": ["last_downloader_helper"], "next": self._dltag_cron or "事件触发", "icon": "mdi-download-network-outline"},
            {"key": "seed_clean", "name": "自动删种", "enabled": self._seedclean_enabled, "required_config_ready": bool(self._seedclean_downloaders), "schedule_required": True, "schedule_enabled": self._seedclean_schedule_enabled, "cron": self._seedclean_cron, "last_keys": ["last_seed_clean"], "next": self._seedclean_cron, "icon": "mdi-delete-sweep"},
        ]

    def _task_snapshot(self) -> List[Dict[str, Any]]:
        rows = []
        for task in self._task_definitions():
            effective_state = derive_effective_state(
                plugin_enabled=bool(self._enabled),
                component_enabled=bool(task.get("enabled")),
                required_config_ready=bool(task.get("required_config_ready", True)),
                schedule_required=bool(task.get("schedule_required", False)),
                schedule_enabled=bool(task.get("schedule_enabled", True)),
                cron=task.get("cron", ""),
                fusion_notification_managed=bool(self._fusion_notify_enabled),
            )
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
            rows.append({**task, "effective_state": effective_state, "effective_enabled": effective_state["active"], "latest": latest, "state": state, "color": color})
        return rows

    def _task_flow_panel(self) -> dict:
        rows = []
        for item in (task for task in self._task_snapshot() if task["effective_enabled"]):
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
