import re
import threading
from typing import Any, Dict, Optional

from app.log import logger

# Default local plugin source repository. Empty means disabled.
# Source cleanup is only enabled after an explicit user path is configured.
DEFAULT_LOCAL_PLUGIN_REPO = ""

class LifecycleMixin:
    _local_plugin_repo = DEFAULT_LOCAL_PLUGIN_REPO

    def _load_plugin_config(self, config: Dict[str, Any]):
        self._load_report_config(config)
        self._load_health_site_config(config)
        self._load_maintenance_config(config)
        self._load_download_media_config(config)

    def _reset_runtime_state(self):
        self._runtime_generation = int(getattr(self, "_runtime_generation", 0) or 0) + 1
        self._runtime_cancel_event = threading.Event()
        self._runtime_active = bool(getattr(self, "_enabled", False))
        self._runtime_timers = set()
        self._msg_seen = {}
        self._last_summary = self._build_summary()
        try:
            cleanup = self._cleanup_pending_plugin_uninstall_isolation()
            if cleanup.get("errors"):
                logger.warning(f"Signal 插件卸载临时目录续清理未完成：{'；'.join(cleanup['errors'][:3])}")
        except Exception as err:
            logger.warning(f"Signal 插件卸载临时目录续清理失败：{err}")

    def _stop_runtime_state(self):
        self._runtime_active = False
        self._runtime_generation = int(getattr(self, "_runtime_generation", 0) or 0) + 1
        cancel_event = getattr(self, "_runtime_cancel_event", None)
        if cancel_event is None:
            cancel_event = threading.Event()
            self._runtime_cancel_event = cancel_event
        cancel_event.set()
        for timer in list(getattr(self, "_runtime_timers", set()) or set()):
            try:
                timer.cancel()
            except Exception:
                pass
        self._runtime_timers = set()

    def _cleanup_scheduler_jobs(self):
        try:
            from app.scheduler import Scheduler
            scheduler = Scheduler()
            if hasattr(scheduler, "remove_plugin_job"):
                scheduler.remove_plugin_job("Signal")
        except Exception as err:
            logger.warning(f"Signal scheduler cleanup failed: {err}")

    def _is_runtime_active(self, generation: Optional[int] = None) -> bool:
        if not bool(getattr(self, "_enabled", False)):
            return False
        if not bool(getattr(self, "_runtime_active", False)):
            return False
        if generation is not None and int(generation) != int(getattr(self, "_runtime_generation", 0) or 0):
            return False
        cancel_event = getattr(self, "_runtime_cancel_event", None)
        return not bool(cancel_event and cancel_event.is_set())

    def _should_cancel(self, generation: Optional[int] = None) -> bool:
        return not self._is_runtime_active(generation)

    def _event_should_noop_after_stop(self) -> bool:
        return bool(getattr(self, "_enabled", False)) and not self._is_runtime_active()

    def _runtime_gate(
        self,
        operation: str,
        component: Optional[str] = None,
        name: str = "",
        allow_disabled_readonly: bool = False,
    ):
        display_name = name or operation
        if allow_disabled_readonly and operation == "read":
            return True, ""
        if not bool(getattr(self, "_enabled", False)):
            return False, f"插件未启用，已跳过{display_name}。"
        if not self._is_runtime_active():
            return False, f"Plugin stopped, skipped {display_name}."
        if component and not self._component_enabled(component):
            return False, f"{display_name}未启用，已跳过。"
        return True, ""

    def _track_runtime_timer(self, timer):
        timers = getattr(self, "_runtime_timers", None)
        if timers is None:
            timers = set()
            self._runtime_timers = timers
        timers.add(timer)
        return timer

    def _untrack_runtime_timer(self, timer):
        timers = getattr(self, "_runtime_timers", None)
        if timers is not None:
            timers.discard(timer)

    @staticmethod
    def _valid_cron_part(value: str, minimum: int, maximum: int) -> bool:
        for segment in str(value or "").split(","):
            if not segment:
                return False
            pieces = segment.split("/")
            if len(pieces) > 2:
                return False
            base = pieces[0]
            if len(pieces) == 2 and (not pieces[1].isdigit() or not 1 <= int(pieces[1]) <= (maximum - minimum + 1)):
                return False
            if base == "*":
                continue
            if base.isdigit():
                if not minimum <= int(base) <= maximum:
                    return False
                continue
            matched = re.fullmatch(r"(\d+)-(\d+)", base)
            if not matched:
                return False
            start, end = map(int, matched.groups())
            if start < minimum or end > maximum or start > end:
                return False
        return True

    @classmethod
    def _normalize_fusion_refresh_cron(cls, value: Any, fallback: str = "0 * * * *") -> str:
        ranges = ((0, 59), (0, 23), (1, 31), (1, 12), (0, 7))
        for candidate in (value, fallback, "0 * * * *"):
            parts = str(candidate or "").strip().split()
            if len(parts) == 5 and all(cls._valid_cron_part(part, *ranges[index]) for index, part in enumerate(parts)):
                return " ".join(parts)
        return "0 * * * *"

    @classmethod
    def _normalize_optional_cron(cls, value: Any) -> str:
        ranges = ((0, 59), (0, 23), (1, 31), (1, 12), (0, 7))
        parts = str(value or "").strip().split()
        if len(parts) == 5 and all(cls._valid_cron_part(part, *ranges[index]) for index, part in enumerate(parts)):
            return " ".join(parts)
        return ""

    def _load_report_config(self, config: Dict[str, Any]):
        previous_fusion_enabled = getattr(self, "_fusion_notify_enabled", None)
        self._enabled = bool(config.get("enabled"))
        self._local_plugin_repo = config.get("local_plugin_repo") or DEFAULT_LOCAL_PLUGIN_REPO
        self._fusion_notify_enabled = bool(config.get("fusion_notify_enabled")) if "fusion_notify_enabled" in config else True
        self._fusion_card_create_cron = self._normalize_fusion_refresh_cron(config.get("fusion_card_create_cron"), "5 0 * * *")
        self._fusion_card_refresh_cron = self._normalize_fusion_refresh_cron(config.get("fusion_card_refresh_cron"), "0 * * * *")
        self._daily_report_enabled = True
        self._daily_report_schedule_enabled = True
        self._daily_report_cron = self._fusion_card_refresh_cron
        self._daily_report_greeting = "少爷"
        self._daily_report_telegram_rich_enabled = True
        self._daily_report_telegram_bot_token = ""
        self._daily_report_telegram_chat_id = ""
        self._fusion_notify_schedule_enabled = self._fusion_notify_enabled
        self._fusion_notify_cron = self._fusion_card_refresh_cron
        self._fusion_notify_msgtype = config.get("fusion_notify_msgtype") or "Plugin"
        self._fusion_notify_columns = [x["key"] for x in self._fusion_column_registry()]
        self._report_storage_targets = ["config", "download", "library", "storages"]
        self._tg_console_enabled = self._fusion_notify_enabled
        self._tg_console_poll_enabled = False
        self._tg_console_poll_interval = 0
        self._tg_console_allowed_user_ids = []
        self._tg_console_full_remote_enabled = False
        self._tg_console_suppress_individual_notifications = bool(self._fusion_notify_enabled)
        self._tg_console_max_notices = 20
        self._tg_console_last_error = ""
        self._sync_fusion_card_enablement(previous_fusion_enabled)
        self._health_in_report = True
        self._subscribe_reminder_enabled = bool(config.get("subscribe_reminder_enabled", True))
        self._site_stat_enabled = bool(config.get("site_stat_enabled", True))
        self._subscribe_in_report = self._subscribe_reminder_enabled
        self._site_stat_in_report = self._site_stat_enabled
        self._report_version = True
        self._report_site_status = True
        self._report_site_increment = self._site_stat_in_report
        self._report_today_download = True
        self._report_transfer = True
        self._report_subscribe = self._subscribe_in_report
        self._report_storage = True
        self._report_media_stat = True
        self._report_summary = self._health_in_report

    def _load_health_site_config(self, config: Dict[str, Any]):
        self._health_check_enabled = bool(config.get("health_check_enabled", True))
        self._health_check_schedule_enabled = self._schedule_flag(config, "health_check_schedule_enabled", self._health_check_enabled)
        self._health_check_cron = config.get("health_check_cron") or "0 */6 * * *"
        self._health_check_items = self._parse_csv(config.get("health_check_items"))
        self._health_check_database_targets = self._parse_csv(config.get("health_check_database_targets"))
        self._health_check_storage_targets = self._parse_csv(config.get("health_check_storage_targets"))
        self._health_check_directory_targets = self._parse_csv(config.get("health_check_directory_targets"))
        self._health_check_storage_threshold = self._safe_int(config.get("health_check_storage_threshold"), 85, 1)
        if self._health_check_storage_threshold > 99:
            self._health_check_storage_threshold = 99
        self._health_check_notify = self._config_bool(config, "health_check_notify", True)
        self._health_check_completion_notify_enabled = self._config_bool(
            config, "health_check_completion_notify_enabled", False
        )
        self._health_check_notify_type = config.get("health_check_notify_type") or "Plugin"
        self._health_check_completion_notify_type = config.get("health_check_completion_notify_type") or "Plugin"
        self._report_health = True
        self._subscribe_reminder_cron = self._normalize_optional_cron(config.get("subscribe_reminder_cron")) or "0 9 * * *"
        self._subscribe_reminder_subtype = config.get("subscribe_reminder_subtype") or ["movie", "tv"]
        if isinstance(self._subscribe_reminder_subtype, str):
            self._subscribe_reminder_subtype = self._parse_csv(self._subscribe_reminder_subtype)
        self._subscribe_reminder_msgtype = config.get("subscribe_reminder_msgtype") or "Subscribe"
        self._subscribe_reminder_schedule_enabled = self._schedule_flag(config, "subscribe_reminder_schedule_enabled", self._subscribe_reminder_enabled)
        self._site_stat_dashboard_type = config.get("site_stat_dashboard_type") or "today"
        self._site_stat_schedule_enabled = self._schedule_flag(config, "site_stat_schedule_enabled", self._site_stat_enabled)
        self._site_stat_cron = self._normalize_optional_cron(config.get("site_stat_cron")) or "0 8 * * *"
        self._site_stat_schedule_notify_enabled = self._config_bool(
            config, "site_stat_schedule_notify_enabled", True
        )
        notify_type = str(config.get("site_stat_notify_type") or "Plugin").strip()
        self._site_stat_notify_type = "Plugin" if notify_type.lower() in {"inc", "all", "none", "off", ""} else notify_type

    def _load_maintenance_config(self, config: Dict[str, Any]):
        self._log_clean_enabled = bool(config.get("log_clean_enabled", False))
        self._log_clean_schedule_enabled = self._schedule_flag(config, "log_clean_schedule_enabled", self._log_clean_enabled)
        self._log_clean_cron = config.get("log_clean_cron") or "0 3 * * 1"
        self._log_clean_rows = self._safe_int(config.get("log_clean_rows"), 300, 0)
        self._log_clean_selected_ids = self._parse_csv(config.get("log_clean_selected_ids"))
        self._log_clean_notify = bool(config.get("log_clean_notify", True))
        self._log_clean_notify_type = config.get("log_clean_notify_type") or "Plugin"
        self._backup_enabled = bool(config.get("backup_enabled", False))
        # The backup master switch is also the scheduler switch. There is no
        # second persisted toggle that can leave the page and runtime out of sync.
        self._backup_schedule_enabled = self._backup_enabled
        self._backup_cron = config.get("backup_cron") or "0 4 * * 1"
        self._backup_keep_count = self._safe_int(config.get("backup_keep_count"), 5, 1)
        self._backup_path = config.get("backup_path") or "/config/plugins/Signal/Backup"
        self._backup_notify = bool(config.get("backup_notify", False))
        self._backup_notify_type = config.get("backup_notify_type") or "Plugin"
        self._backup_webdav_digest_auth = bool(config.get("backup_webdav_digest_auth", False))
        self._backup_webdav_disable_check = bool(config.get("backup_webdav_disable_check", False))
        self._backup_webdav_hostname = str(config.get("backup_webdav_hostname") or "").strip()
        self._backup_webdav_login = str(config.get("backup_webdav_login") or "").strip()
        self._backup_webdav_password = str(config.get("backup_webdav_password") or "")
        self._backup_webdav_max_count = self._safe_int(config.get("backup_webdav_max_count"), 5, 1)
        webdav_credentials_ready = all((
            self._backup_webdav_hostname,
            self._backup_webdav_login,
            self._backup_webdav_password,
        ))
        # Keep existing WebDAV setups working once, while making the persisted
        # switch the runtime authority for all new and explicitly saved config.
        self._backup_webdav_enabled = self._config_bool(
            config,
            "backup_webdav_enabled",
            webdav_credentials_ready,
        )
        self._mp_update_enabled = self._config_bool(config, "mp_update_enabled", False)
        # The task switch is now the only scheduler switch.  The old schedule
        # flags are retained in config solely so older installations can save
        # and reload without losing unknown compatibility keys.
        self._mp_update_schedule_enabled = self._mp_update_enabled
        self._mp_update_cron = config.get("mp_update_cron") or "0 9 * * *"
        self._mp_update_types = config.get("mp_update_types") or ["后端", "前端"]
        if isinstance(self._mp_update_types, str):
            self._mp_update_types = self._parse_csv(self._mp_update_types) or ["后端", "前端"]
        legacy_market_enabled = self._config_bool(config, "market_update_enabled", False)
        legacy_market_schedule_enabled = self._config_bool(
            config, "market_update_schedule_enabled", legacy_market_enabled
        )
        legacy_market_cron = self._normalize_optional_cron(config.get("market_update_cron")) or "0 9 * * *"
        has_current_plugin_update_config = any(
            key in config for key in (
                "plugin_update_reminder_enabled",
                "plugin_auto_install_enabled",
                "plugin_auto_install_scope_mode",
            )
        )
        # The old schedule flag is only meaningful during the one-time legacy
        # migration. Once the new plugin-update fields exist, the visible
        # library switch is the scheduler authority and the hidden flag must
        # not override it on a later reload.
        legacy_market_effective = bool(legacy_market_enabled and legacy_market_schedule_enabled)
        self._market_update_enabled = bool(
            legacy_market_enabled if has_current_plugin_update_config else legacy_market_effective
        )
        self._market_update_schedule_enabled = self._market_update_enabled
        self._market_update_cron = legacy_market_cron
        self._market_update_strategy = str(config.get("market_update_strategy") or "check").strip().lower()
        if self._market_update_strategy not in {"check", "sync", "install"}:
            self._market_update_strategy = "check"
        self._market_update_install_ids = self._parse_csv(config.get("market_update_install_ids"))
        self._market_update_exclude_ids = self._parse_csv(config.get("market_update_exclude_ids"))
        reminder_enabled = self._config_bool(
            config,
            "plugin_update_reminder_enabled",
            legacy_market_enabled if has_current_plugin_update_config else legacy_market_effective,
        )
        self._plugin_update_reminder_enabled = bool(reminder_enabled)
        self._plugin_update_reminder_schedule_enabled = self._plugin_update_reminder_enabled
        self._plugin_update_reminder_cron = self._normalize_optional_cron(
            config.get("plugin_update_reminder_cron") or legacy_market_cron
        ) or "0 9 * * *"
        auto_install_enabled = self._config_bool(
            config, "plugin_auto_install_enabled", self._market_update_strategy == "install"
        )
        self._plugin_auto_install_enabled = bool(auto_install_enabled)
        self._plugin_auto_install_schedule_enabled = self._plugin_auto_install_enabled
        self._plugin_auto_install_cron = self._normalize_optional_cron(
            config.get("plugin_auto_install_cron") or legacy_market_cron
        ) or "0 9 * * *"
        self._plugin_auto_install_install_ids = self._parse_csv(
            config.get("plugin_auto_install_install_ids")
            if "plugin_auto_install_install_ids" in config
            else config.get("market_update_install_ids")
        )
        self._plugin_auto_install_exclude_ids = self._parse_csv(
            config.get("plugin_auto_install_exclude_ids")
            if "plugin_auto_install_exclude_ids" in config
            else config.get("market_update_exclude_ids")
        )
        scope_mode = str(config.get("plugin_auto_install_scope_mode") or "").strip().lower()
        if scope_mode not in {"all", "include", "exclude"}:
            if self._plugin_auto_install_install_ids and self._plugin_auto_install_exclude_ids:
                excluded = set(self._plugin_auto_install_exclude_ids)
                self._plugin_auto_install_install_ids = [
                    plugin_id for plugin_id in self._plugin_auto_install_install_ids if plugin_id not in excluded
                ]
                self._plugin_auto_install_exclude_ids = []
                scope_mode = "include"
            elif self._plugin_auto_install_install_ids:
                scope_mode = "include"
            elif self._plugin_auto_install_exclude_ids:
                scope_mode = "exclude"
            else:
                scope_mode = "all"
        self._plugin_auto_install_scope_mode = scope_mode
        legacy_update_notify = self._config_bool(config, "update_scheduled_notify", False)
        legacy_update_notify_type = config.get("update_notify_type") or "Plugin"
        self._update_scheduled_notify = legacy_update_notify
        self._update_notify_type = legacy_update_notify_type
        self._mp_update_scheduled_notify = self._config_bool(config, "mp_update_scheduled_notify", legacy_update_notify)
        self._mp_update_notify_type = config.get("mp_update_notify_type") or legacy_update_notify_type
        self._market_update_scheduled_notify = self._config_bool(config, "market_update_scheduled_notify", legacy_update_notify)
        self._market_update_notify_type = config.get("market_update_notify_type") or legacy_update_notify_type
        self._plugin_update_reminder_scheduled_notify = self._config_bool(config, "plugin_update_reminder_scheduled_notify", legacy_update_notify)
        self._plugin_update_reminder_notify_type = config.get("plugin_update_reminder_notify_type") or legacy_update_notify_type
        self._plugin_auto_install_scheduled_notify = self._config_bool(config, "plugin_auto_install_scheduled_notify", legacy_update_notify)
        self._plugin_auto_install_notify_type = config.get("plugin_auto_install_notify_type") or legacy_update_notify_type
        self._plugin_uninstall_ids = config.get("plugin_uninstall_ids") or []
        if isinstance(self._plugin_uninstall_ids, str):
            self._plugin_uninstall_ids = self._parse_csv(self._plugin_uninstall_ids)
        self._plugin_uninstall_clear_config = bool(config.get("plugin_uninstall_clear_config", True))
        self._plugin_uninstall_clear_data = bool(config.get("plugin_uninstall_clear_data", True))
        self._plugin_uninstall_delete_source = bool(config.get("plugin_uninstall_delete_source", False))

    def _load_download_media_config(self, config: Dict[str, Any]):
        self._seedclean_enabled = bool(config.get("seedclean_enabled", False))
        self._seedclean_schedule_enabled = self._schedule_flag(config, "seedclean_schedule_enabled", self._seedclean_enabled)
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
        self._seedclean_trtorrentstates = str(config.get("seedclean_trtorrentstates") or "").strip()
        self._seedclean_torrentcategorys = str(config.get("seedclean_torrentcategorys") or "").strip()
        self._seedclean_samedata = bool(config.get("seedclean_samedata", False))
        self._seedclean_mponly = bool(config.get("seedclean_mponly", False))
        self._seedclean_notify = bool(config.get("seedclean_notify", True))
        self._seedclean_notify_type = config.get("seedclean_notify_type") or "Plugin"
        self._subfill_enabled = bool(config.get("subfill_enabled", False))
        self._subfill_details = self._parse_csv(config.get("subfill_details"))
        self._subfill_category_enabled = bool(config.get("subfill_category_enabled", False))
        self._subfill_category_confs = config.get("subfill_category_confs") or ""
        self._subfill_completion_notify_enabled = self._config_bool(config, "subfill_completion_notify_enabled", False)
        self._subfill_completion_notify_type = config.get("subfill_completion_notify_type") or "Plugin"
        self._subfill_confs = self._parse_subfill_confs(self._subfill_category_confs)
        self._msgnotify_enabled = bool(config.get("msgnotify_enabled", False))
        self._msgnotify_types = self._parse_csv(config.get("msgnotify_types"))
        self._msgnotify_servers = self._parse_csv(config.get("msgnotify_servers"))
        self._msgnotify_notify_type = config.get("msgnotify_notify_type") or "MediaServer"
        self._dltag_enabled = bool(config.get("dltag_enabled", False))
        self._dltag_downloaders = self._parse_csv(config.get("dltag_downloaders"))
        self._dltag_tasks = self._parse_csv(config.get("dltag_tasks") or ["tagging", "seeding", "cleanup"])
        dltag_cron = config["dltag_cron"] if "dltag_cron" in config else "0 */6 * * *"
        self._dltag_cron = self._normalize_optional_cron(dltag_cron)
        self._dltag_listen_download = self._config_bool(config, "dltag_listen_download", True)
        # The old source_file value was tagging context, never deletion consent.
        self._dltag_listen_source_file = self._config_bool(config, "dltag_listen_source_file", False)
        self._dltag_prefix = str(config.get("dltag_prefix") or "").strip()
        self._dltag_all_tags = self._parse_csv(config.get("dltag_all_tags"))
        self._dltag_excluded_tags = self._parse_csv(config.get("dltag_excluded_tags"))
        self._dltag_not_select_all_tag = str(config.get("dltag_not_select_all_tag") or "非全").strip()
        self._dltag_tracker_mappings = str(config.get("dltag_tracker_mappings") or "").strip()
        strategy = str(config.get("dltag_source_delete_strategy") or "delayed").strip().lower()
        self._dltag_source_delete_strategy = strategy if strategy in {"early", "delayed"} else "delayed"
        self._dltag_scheduled_notify = self._config_bool(config, "dltag_scheduled_notify", False)
        self._dltag_notify_type = config.get("dltag_notify_type") or "Plugin"
