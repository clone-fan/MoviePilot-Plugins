"""MoviePilot adapter and composition root for Signal."""

# AOA-OWNERSHIP: plugin-contract composition boundary. Host decorators stay here;
# behavior belongs to the imported owned mixins.

from app.core.event import Event, eventmanager
from app.plugins import _PluginBase
from app.schemas.types import EventType

from .adapters import events as _events
from .adapters import downloader_tag_events as _downloader_tag_events
from .adapters import lifecycle as _lifecycle
from .adapters import moviepilot_contract as _moviepilot_contract
from .adapters import runtime_state as _runtime_state
from .application import backup as _backup
from .application import daily_report as _daily_report
from .application import downloader_helper as _downloader_helper
from .application import fusion as _fusion
from .application import log_ops as _log_ops
from .application import plugin_uninstall as _plugin_uninstall
from .application import seed_clean as _seed_clean
from .application import site_stats as _site_stats
from .application import subscribe_reminder as _subscribe_reminder
from .application import update_governance as _update_governance
from .domain import dashboard_schema as _dashboard_schema
from .domain import formatters as _formatters
from .infrastructure import mp_api as _mp_api
from .infrastructure import legacy_agentopsassistant as _legacy_agentopsassistant
from .infrastructure import plugin_ops as _plugin_ops
from .presentation import tg_console as _tg_console
from .presentation import tg_report_html as _tg_report_html


class Signal(_runtime_state.RuntimeStateMixin, _lifecycle.LifecycleMixin, _formatters.FormattersMixin, _dashboard_schema.DashboardSchemaMixin, _fusion.FusionMixin, _plugin_uninstall.PluginUninstallMixin, _backup.BackupMixin, _daily_report.DailyReportMixin, _tg_report_html.TgReportHtmlMixin, _events.EventsMixin, _downloader_tag_events.DownloaderTagEventsMixin, _tg_console.TgConsoleMixin, _mp_api.MpApiMixin, _moviepilot_contract.PluginContractMixin, _update_governance.UpdateGovernanceMixin, _site_stats.SiteStatsMixin, _downloader_helper.DownloaderHelperMixin, _seed_clean.SeedCleanMixin, _log_ops.LogOpsMixin, _plugin_ops.PluginOpsMixin, _legacy_agentopsassistant.LegacyAgentOpsAssistantPurgeMixin, _subscribe_reminder.SubscribeReminderMixin, _PluginBase):
    """MoviePilot plugin host adapter composed from owned backend layers."""

    @eventmanager.register(EventType.PluginAction)
    def handle_command(self, event: Event = None):
        return _events.EventsMixin.handle_command(self, event)

    @eventmanager.register(EventType.MessageAction)
    def on_message_action(self, event: Event = None):
        return _events.EventsMixin.on_message_action(self, event)

    @eventmanager.register(EventType.DownloadAdded)
    def on_download_fill_subscribe(self, event: Event = None):
        return _events.EventsMixin.on_download_fill_subscribe(self, event)

    @eventmanager.register(EventType.DownloadAdded)
    def on_download_tag(self, event: Event = None):
        return _downloader_tag_events.DownloaderTagEventsMixin.on_download_tag(self, event)

    @eventmanager.register(EventType.DownloadFileDeleted)
    def on_download_file_deleted(self, event: Event = None):
        return _downloader_tag_events.DownloaderTagEventsMixin.on_download_file_deleted(self, event)

    @eventmanager.register(EventType.DownloadDeleted)
    def on_download_deleted(self, event: Event = None):
        return _downloader_tag_events.DownloaderTagEventsMixin.on_download_deleted(self, event)

    @eventmanager.register(EventType.SubscribeAdded)
    def on_subscribe_added_fill(self, event: Event = None):
        return _events.EventsMixin.on_subscribe_added_fill(self, event)

    @eventmanager.register(EventType.WebhookMessage)
    def on_webhook_message(self, event: Event = None):
        return _events.EventsMixin.on_webhook_message(self, event)
