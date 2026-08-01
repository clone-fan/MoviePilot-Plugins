const DEFAULT_FUSION_CARD_REFRESH_CRON = '0 * * * *'
const DEFAULT_FUSION_CARD_CREATE_CRON = '5 0 * * *'
const cronRanges = [[0, 59], [0, 23], [1, 31], [1, 12], [0, 7]]

function validCronPart(part, min, max) {
  const segments = String(part || '').split(',')
  if (!segments.length || segments.some(segment => !segment)) return false
  return segments.every(segment => {
    const pieces = segment.split('/')
    if (pieces.length > 2) return false
    const [base, step] = pieces
    if (step !== undefined && (!/^\d+$/u.test(step) || Number(step) < 1 || Number(step) > (max - min + 1))) return false
    if (base === '*') return true
    if (/^\d+$/u.test(base)) {
      const value = Number(base)
      return value >= min && value <= max
    }
    const range = base.match(/^(\d+)-(\d+)$/u)
    if (!range) return false
    const start = Number(range[1])
    const end = Number(range[2])
    return start >= min && end <= max && start <= end
  })
}

export function isValidFusionRefreshCron(value) {
  const parts = String(value || '').trim().split(/\s+/u)
  return parts.length === 5 && parts.every((part, index) => validCronPart(part, ...cronRanges[index]))
}

export function normalizeFusionRefreshCron(value, fallback = DEFAULT_FUSION_CARD_REFRESH_CRON) {
  const candidate = String(value || '').trim()
  if (isValidFusionRefreshCron(candidate)) return candidate
  const fallbackValue = String(fallback || '').trim()
  return isValidFusionRefreshCron(fallbackValue) ? fallbackValue : DEFAULT_FUSION_CARD_REFRESH_CRON
}

export function normalizeFusionCreateCron(value, fallback = DEFAULT_FUSION_CARD_CREATE_CRON) {
  return normalizeFusionRefreshCron(value, fallback)
}

export function normalizeCurrentFusionConfig(config = {}) {
  const source = config && typeof config === 'object' && !Array.isArray(config) ? config : {}
  const normalized = { ...source }
  if (Object.hasOwn(source, 'fusion_notify_enabled')) normalized.fusion_notify_enabled = !!source.fusion_notify_enabled
  if (Object.hasOwn(source, 'fusion_card_create_cron')) normalized.fusion_card_create_cron = normalizeFusionCreateCron(source.fusion_card_create_cron)
  if (Object.hasOwn(source, 'fusion_card_refresh_cron')) normalized.fusion_card_refresh_cron = normalizeFusionRefreshCron(source.fusion_card_refresh_cron)
  return normalized
}
