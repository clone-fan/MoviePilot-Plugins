import { configSchemaFields } from './config-schema.js'
import { isValidFusionRefreshCron, normalizeCurrentFusionConfig, normalizeFusionRefreshCron } from './fusion-config.js'

export const DEFAULT_SUBSCRIBE_REMINDER_CRON = '0 9 * * *'
export const DEFAULT_MARKET_UPDATE_CRON = '0 9 * * *'
export const DEFAULT_SITE_STAT_CRON = '0 8 * * *'
const notificationTypes = new Set(['Plugin', 'Other', 'Manual', 'Subscribe', 'Download', 'Organize', 'SiteMessage', 'MediaServer', 'Agent'])

const currentConfigKeys = new Set(configSchemaFields.map(field => field.key))

function currentValues(config = {}) {
  const source = config && typeof config === 'object' && !Array.isArray(config) ? config : {}
  return Object.fromEntries(Object.entries(source).filter(([key]) => currentConfigKeys.has(key)))
}

function normalizeCron(value, fallback) {
  const candidate = String(value || '').trim().replace(/\s+/gu, ' ')
  return isValidFusionRefreshCron(candidate) ? candidate : fallback
}

export function normalizeCurrentConfig(config = {}) {
  const normalized = normalizeCurrentFusionConfig(currentValues(config))
  if (Object.hasOwn(normalized, 'subscribe_reminder_cron')) {
    normalized.subscribe_reminder_cron = normalizeCron(normalized.subscribe_reminder_cron, DEFAULT_SUBSCRIBE_REMINDER_CRON)
  }
  if (Object.hasOwn(normalized, 'market_update_cron')) {
    normalized.market_update_cron = normalizeCron(normalized.market_update_cron, DEFAULT_MARKET_UPDATE_CRON)
  }
  if (Object.hasOwn(normalized, 'site_stat_cron')) {
    normalized.site_stat_cron = normalizeCron(normalized.site_stat_cron, DEFAULT_SITE_STAT_CRON)
  }
  if (Object.hasOwn(normalized, 'dltag_cron')) {
    normalized.dltag_cron = normalizeCron(normalized.dltag_cron, '')
  }
  if (Object.hasOwn(normalized, 'dltag_tasks')) {
    const values = Array.isArray(normalized.dltag_tasks) ? normalized.dltag_tasks : String(normalized.dltag_tasks || '').split(',')
    const allowed = new Set(['tagging', 'seeding', 'cleanup'])
    normalized.dltag_tasks = [...new Set(values.map(value => String(value || '').trim()).filter(value => allowed.has(value)))]
  }
  if (Object.hasOwn(normalized, 'dltag_source_delete_strategy')) {
    normalized.dltag_source_delete_strategy = normalized.dltag_source_delete_strategy === 'early' ? 'early' : 'delayed'
  }
  if (Object.hasOwn(normalized, 'site_stat_notify_type')) {
    normalized.site_stat_notify_type = notificationTypes.has(normalized.site_stat_notify_type) ? normalized.site_stat_notify_type : 'Plugin'
  }
  if (Object.hasOwn(normalized, 'plugin_uninstall_ids')) {
    const source = normalized.plugin_uninstall_ids
    normalized.plugin_uninstall_ids = Array.isArray(source)
      ? [...new Set(source.map(value => String(value || '').trim()).filter(Boolean))]
      : String(source || '').split(',').map(value => value.trim()).filter(Boolean)
  }
  return normalized
}

export { normalizeFusionRefreshCron }
