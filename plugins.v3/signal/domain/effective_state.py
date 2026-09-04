"""Authoritative runtime/display state precedence for every plugin component."""

from typing import Any, Dict


ACTIVE = "active"
PLUGIN_DISABLED = "plugin_disabled"
COMPONENT_DISABLED = "component_disabled"
CONFIGURATION_MISSING = "configuration_missing"
SCHEDULE_DISABLED = "schedule_disabled"
CRON_MISSING = "cron_missing"


def derive_effective_state(
    *,
    plugin_enabled: bool = False,
    component_enabled: bool = False,
    required_config_ready: bool = True,
    schedule_required: bool = False,
    schedule_enabled: bool = True,
    cron: Any = "",
    fusion_notification_managed: bool = False,
) -> Dict[str, Any]:
    """Return one deterministic state; Fusion ownership never disables business work."""

    code = ACTIVE
    if not plugin_enabled:
        code = PLUGIN_DISABLED
    elif not component_enabled:
        code = COMPONENT_DISABLED
    elif not required_config_ready:
        code = CONFIGURATION_MISSING
    elif schedule_required and not schedule_enabled:
        code = SCHEDULE_DISABLED
    elif schedule_required and not str(cron or "").strip():
        code = CRON_MISSING

    return {
        "code": code,
        "active": code == ACTIVE,
        "plugin_enabled": bool(plugin_enabled),
        "component_enabled": bool(component_enabled),
        "notification_managed_by_fusion": bool(fusion_notification_managed),
    }
