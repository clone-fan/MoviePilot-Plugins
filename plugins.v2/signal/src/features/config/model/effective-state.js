export const EFFECTIVE_STATE = Object.freeze({
  ACTIVE: 'active',
  PLUGIN_DISABLED: 'plugin_disabled',
  COMPONENT_DISABLED: 'component_disabled',
  CONFIGURATION_MISSING: 'configuration_missing',
  SCHEDULE_DISABLED: 'schedule_disabled',
  CRON_MISSING: 'cron_missing',
})

export function deriveEffectiveState({
  pluginEnabled = false,
  componentEnabled = false,
  requiredConfigReady = true,
  scheduleRequired = false,
  scheduleEnabled = true,
  cron = '',
  fusionNotificationManaged = false,
} = {}) {
  let code = EFFECTIVE_STATE.ACTIVE
  if (!pluginEnabled) code = EFFECTIVE_STATE.PLUGIN_DISABLED
  else if (!componentEnabled) code = EFFECTIVE_STATE.COMPONENT_DISABLED
  else if (!requiredConfigReady) code = EFFECTIVE_STATE.CONFIGURATION_MISSING
  else if (scheduleRequired && !scheduleEnabled) code = EFFECTIVE_STATE.SCHEDULE_DISABLED
  else if (scheduleRequired && !String(cron || '').trim()) code = EFFECTIVE_STATE.CRON_MISSING

  return Object.freeze({
    code,
    active: code === EFFECTIVE_STATE.ACTIVE,
    pluginEnabled: Boolean(pluginEnabled),
    componentEnabled: Boolean(componentEnabled),
    notificationManagedByFusion: Boolean(fusionNotificationManaged),
  })
}

