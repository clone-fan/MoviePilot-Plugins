import { configSchemaFields } from './config-schema.js'

const schemaByKey = new Map(configSchemaFields.map(field => [field.key, field]))

export const auditedCompactSelectionFieldKeys = Object.freeze([
  'health_check_database_targets',
  'health_check_directory_targets',
  'health_check_items',
  'health_check_storage_targets',
  'log_clean_selected_ids',
  'market_update_exclude_ids',
  'market_update_install_ids',
  'mp_update_types',
  'msgnotify_servers',
  'msgnotify_types',
  'plugin_uninstall_ids',
  'seedclean_downloaders',
  'subfill_details',
  'subscribe_reminder_subtype',
  'dltag_downloaders',
  'dltag_tasks',
])

const auditedCompactSelectionFieldKeySet = new Set(auditedCompactSelectionFieldKeys)

const compactSelectionEmptyText = Object.freeze({
  seedclean_downloaders: '全部可用',
  dltag_downloaders: '全部可用',
})

export const replicaFieldVisibilityDependencies = Object.freeze({
  backup_notify_type: Object.freeze({ key: 'backup_notify', value: true }),
  log_clean_notify_type: Object.freeze({ key: 'log_clean_notify', value: true }),
  seedclean_notify_type: Object.freeze({ key: 'seedclean_notify', value: true }),
  update_notify_type: Object.freeze({ key: 'update_scheduled_notify', value: true }),
  dltag_notify_type: Object.freeze({ key: 'dltag_scheduled_notify', value: true }),
  dltag_source_delete_strategy: Object.freeze({ key: 'dltag_listen_source_file', value: true }),
  market_update_install_ids: Object.freeze({ key: 'market_update_strategy', value: 'install' }),
  market_update_exclude_ids: Object.freeze({ key: 'market_update_strategy', value: 'install' }),
})

export function isReplicaFieldVisible(field, values = {}) {
  if (!field || field.hidden) return false
  const dependency = replicaFieldVisibilityDependencies[field.key]
  if (!dependency) return true
  return values[dependency.key] === dependency.value
}

// Hero / subtab masters own the authority switches.  Schedule enable flags stay
// persisted and still inherit from the master toggle, but must not reappear as a
// second visible switch inside notify/schedule cards.
export const heroManagedReplicaFieldKeys = Object.freeze({
  fusion: Object.freeze(['fusion_notify_enabled']),
  server: Object.freeze(['msgnotify_enabled']),
  subscribe: Object.freeze(['subscribe_reminder_enabled', 'subscribe_reminder_schedule_enabled']),
  sites: Object.freeze(['site_stat_enabled', 'site_stat_schedule_enabled']),
  hc: Object.freeze(['health_check_enabled', 'health_check_schedule_enabled']),
  seedremove: Object.freeze(['seedclean_enabled', 'seedclean_schedule_enabled']),
  dltagmain: Object.freeze(['dltag_enabled']),
  subfill: Object.freeze(['subfill_enabled']),
  backup: Object.freeze(['backup_enabled']),
  logs: Object.freeze(['log_clean_enabled', 'log_clean_schedule_enabled']),
  updates: Object.freeze([
    'mp_update_enabled',
    'mp_update_schedule_enabled',
    'market_update_enabled',
    'market_update_schedule_enabled',
  ]),
})

export const shellManagedReplicaFieldKeys = Object.freeze(['enabled'])
export const actionManagedReplicaFieldKeys = Object.freeze([])

export const sharedCardOwnership = Object.freeze({
  fusion: Object.freeze({
    schedule: Object.freeze({ title: '刷新计划', note: '使用 Cron 控制活动卡片的数据刷新频率。', masterKey: 'fusion_notify_enabled' }),
    notify: Object.freeze({ title: '融合通知渠道', note: '统一卡片通过 MoviePilot 通知渠道发送。', masterKey: 'fusion_notify_enabled' }),
  }),
  server: Object.freeze({
    notify: Object.freeze({ title: '媒体通知', note: '选择事件、媒体服务器与投递消息类型。', masterKey: 'msgnotify_enabled', fusionManaged: true, fusionChannelOnly: true }),
  }),
  subscribe: Object.freeze({
    schedule: Object.freeze({ title: '订阅检查计划', note: '按 Cron 检查订阅更新并生成提醒。', masterKey: 'subscribe_reminder_enabled', scheduleKey: 'subscribe_reminder_schedule_enabled' }),
    notify: Object.freeze({ title: '订阅提醒通知', note: '设置订阅检查结果的投递类型。', masterKey: 'subscribe_reminder_enabled', fusionManaged: true, fusionChannelOnly: true }),
  }),
  sites: Object.freeze({
    schedule: Object.freeze({ title: '站点统计计划', note: '按 Cron 自动刷新站点上传与下载统计。', masterKey: 'site_stat_enabled', scheduleKey: 'site_stat_schedule_enabled' }),
    notify: Object.freeze({ title: '站点统计通知', note: '定时统计完成后通过所选 MoviePilot 通知类型发送。', masterKey: 'site_stat_enabled', fusionManaged: true, fusionChannelOnly: true }),
  }),
  hc: Object.freeze({
    schedule: Object.freeze({ title: '健康巡检计划', note: '按 Cron 定时巡查数据库、存储和目录。', masterKey: 'health_check_enabled', scheduleKey: 'health_check_schedule_enabled' }),
    notify: Object.freeze({ title: '巡检异常通知', note: '设置健康巡检异常的投递类型。', masterKey: 'health_check_enabled', fusionManaged: true, fusionChannelOnly: true }),
  }),
  seedremove: Object.freeze({
    schedule: Object.freeze({ title: '自动删种计划', note: '按 Cron 定时检查并处理匹配的下载任务。', masterKey: 'seedclean_enabled', scheduleKey: 'seedclean_schedule_enabled' }),
  }),
  dltagmain: Object.freeze({
    notify: Object.freeze({ title: '定时执行通知', note: '只设置 Cron 执行结果的通知方式。', masterKey: 'dltag_enabled', resultKey: 'dltag_scheduled_notify', fusionManaged: true, fusionChannelOnly: true }),
  }),
  backup: Object.freeze({
    notify: Object.freeze({ title: '定时执行通知', note: '只设置 Cron 执行后的通知方式。', masterKey: 'backup_enabled', resultKey: 'backup_notify', fusionManaged: true, fusionChannelOnly: true }),
  }),
  logs: Object.freeze({
    schedule: Object.freeze({ title: '日志清理计划', note: '按 Cron 定时裁剪插件日志。', masterKey: 'log_clean_enabled', scheduleKey: 'log_clean_schedule_enabled' }),
    notify: Object.freeze({ title: '定时执行通知', note: '只设置 Cron 执行后的通知方式。', masterKey: 'log_clean_enabled', resultKey: 'log_clean_notify', fusionManaged: true, fusionChannelOnly: true }),
  }),
  updates: Object.freeze({
    schedule: Object.freeze({ title: '更新检查计划', note: '分别设置 MoviePilot 系统更新和插件库更新的 Cron。' }),
    notify: Object.freeze({ title: '定时执行通知', note: '系统更新和插件库更新共用一套 Cron 执行结果通知。', resultKey: 'update_scheduled_notify', fusionManaged: true, fusionChannelOnly: true, dependencies: Object.freeze({ update_notify_type: 'update_scheduled_notify' }) }),
  }),
})

function schemaFieldPresentation(field) {
  const isArray = field.type === 'array' || field.dataType === 'array'
  return {
    key: field.key,
    cardType: field.cardType || 'feature',
    icon: field.cardType === 'notify' ? 'mdi-bell-outline' : (field.cardType === 'cron' ? 'mdi-calendar-clock' : 'mdi-cog-outline'),
    label: field.label || field.key,
    sensitive: /(?:password|token|secret)/i.test(field.key),
    multiple: isArray,
    chips: isArray,
    fullRow: isArray,
    retainInCard: field.key === 'backup_cron' || field.retainInCard === true,
  }
}

function isSettingsCard(card) {
  return !!card && card.type !== 'actions'
}

function cardMatchesType(card, cardType) {
  const title = card?.title || ''
  const keys = (card?.fields || []).map(field => field?.key || '')
  if (cardType === 'advanced') return card?.type === 'advanced'
  if (cardType === 'cron') {
    return /定时|计划|执行|巡检|备份|清理|更新|生命周期|规则/.test(title)
      || keys.some(key => /(?:cron|schedule|time)$/i.test(key) || /_(?:cron|schedule|time)\b/i.test(key))
  }
  if (cardType === 'notify') {
    return /通知|消息|渠道/.test(title)
      || keys.some(key => /notify|msgtype|msg_type/i.test(key))
  }
  return card?.type === 'section' || card?.type === 'advanced'
}

function pickPrimaryCard(cards, cardType) {
  const settings = (cards || []).filter(isSettingsCard)
  if (!settings.length) return null
  return settings.find(card => cardMatchesType(card, cardType))
    || settings.find(card => card.type === 'section')
    || settings.find(card => card.type === 'advanced')
    || settings[0]
}

/**
 * 将尚未在手工卡片中出现的可见 schema 字段并入既有主卡。
 *
 * schema 保持字段覆盖唯一真源；不再创建「…补充/…补全」独立卡片岛。
 */
export function completeReplicaCards(cardsBySubtab) {
  const completed = Object.fromEntries(Object.entries(cardsBySubtab).map(([subtab, cards]) => [
    subtab,
    (cards || []).map(card => ({ ...card, fields: Array.isArray(card.fields) ? [...card.fields] : card.fields })),
  ]))
  const existingKeys = new Set(Object.values(completed)
    .flatMap(cards => cards || [])
    .flatMap(card => card.fields || [])
    .map(field => field?.key)
    .filter(Boolean))

  for (const field of configSchemaFields) {
    const isHeroManaged = heroManagedReplicaFieldKeys[field.subtab]?.includes(field.key)
    const isShellManaged = shellManagedReplicaFieldKeys.includes(field.key)
    const isActionManaged = actionManagedReplicaFieldKeys.includes(field.key)
    if (field.isDisplayed === false || isHeroManaged || isShellManaged || isActionManaged || existingKeys.has(field.key)) continue
    if (!completed[field.subtab]) completed[field.subtab] = []
    const cards = completed[field.subtab]
    const moduleCards = field.module ? cards.filter(card => card.module === field.module) : []
    let target = pickPrimaryCard(moduleCards.length ? moduleCards : cards, field.cardType)
    if (!target) {
      // Fallback only when a subtab has no settings card yet; keep a neutral title
      // so schema coverage never revives independent supplemental islands.
      target = {
        type: field.cardType === 'advanced' ? 'advanced' : 'section',
        icon: field.cardType === 'notify' ? 'mdi-bell-outline' : (field.cardType === 'cron' ? 'mdi-calendar-clock' : 'mdi-cog-outline'),
        title: '配置项',
        note: '插件持久化配置。',
        grid: field.cardType === 'advanced' ? 'grid-2' : 'grid-3',
        fields: [],
      }
      cards.push(target)
    }
    if (!Array.isArray(target.fields)) target.fields = []
    target.fields.push(schemaFieldPresentation(field))
    existingKeys.add(field.key)
  }
  return completed
}

function bindField(field, subtab, itemSources) {
  const key = field?.key
  if (!key) throw new Error(`Replica field is missing a backend config key in subtab: ${subtab}`)
  const schema = schemaByKey.get(key)
  if (!schema) throw new Error(`Replica field key is missing from config schema: ${key}`)
  if (schema.subtab !== subtab) {
    throw new Error(`Replica field subtab mismatch for ${key}: visual ${subtab}, schema ${schema.subtab}`)
  }
  const itemSource = schema.itemSource || ''
  if (itemSource && !Object.prototype.hasOwnProperty.call(itemSources, itemSource)) {
    throw new Error(`Replica field item source is not registered for ${key}: ${itemSource}`)
  }
  const items = itemSource ? itemSources[itemSource] : (schema.items || [])
  const isArray = field.multiple || field.chips || schema.type === 'array' || schema.dataType === 'array'
  const control = itemSource ? 'select' : (isArray ? 'combobox' : (schema.control || 'text'))
  // A long option list does not make a single-select control multi-line. Only
  // values that can themselves expand need the full-row layout.
  const fullRow = !!(field.fullRow || isArray || control === 'textarea')
  return {
    ...field,
    cardType: schema.cardType || field.cardType || 'feature',
    control,
    items,
    multiple: isArray,
    chips: isArray,
    closableChips: isArray,
    compactSelection: auditedCompactSelectionFieldKeySet.has(key),
    emptySelectionText: compactSelectionEmptyText[key] || '',
    clearable: true,
    fullRow,
  }
}

export function bindReplicaCards(cardsBySubtab, itemSources = {}) {
  return Object.fromEntries(Object.entries(cardsBySubtab).map(([subtab, cards]) => {
    const boundCards = (cards || []).map(card => {
      if (!Array.isArray(card.fields)) return card
      const fields = card.fields.map(field => bindField(field, subtab, itemSources))
      return { ...card, fields }
    })
    return [subtab, boundCards]
  }))
}

function uniqueFields(fields) {
  const keys = new Set()
  return fields.filter((field) => {
    if (!field?.key || keys.has(field.key)) return false
    keys.add(field.key)
    return true
  })
}

function sharedCard(type, fields, ownership = {}) {
  return {
    type,
    icon: type === 'schedule' ? 'mdi-calendar-clock' : 'mdi-bell-outline',
    title: ownership.title || (type === 'schedule' ? '执行计划' : '结果通知'),
    note: ownership.note || '',
    fields,
    ...ownership,
  }
}

export function composeSharedReplicaCards(cardsBySubtab) {
  return Object.fromEntries(Object.entries(cardsBySubtab).map(([subtab, cards]) => {
    const isSharedScheduleField = field => field.cardType === 'cron' && !field.retainInCard
    const isSharedNotifyField = field => field.cardType === 'notify' && !field.retainInCard
    const actions = (cards || []).filter(card => card.type === 'actions')
    const settings = (cards || []).filter(card => card.type !== 'actions')
    const sourceModuleCards = settings.filter(card => card.type === 'module')
    const moduleNotifyFields = sourceModuleCards.flatMap(card => (
      card.fields || []
    ).filter(isSharedNotifyField))
    const moduleCards = sourceModuleCards
      .map(card => ({
        ...card,
        fields: (card.fields || []).filter(field => !isSharedNotifyField(field)),
      }))
      .filter(card => card.fields.length > 0 || (card.actions || []).length > 0)
    const sharedSettings = settings.filter(card => card.type !== 'module')
    const allFields = sharedSettings.flatMap(card => card.fields || [])
    const scheduleFields = uniqueFields(allFields.filter(isSharedScheduleField))
    const notifyFields = uniqueFields([
      ...allFields.filter(isSharedNotifyField),
      ...moduleNotifyFields,
    ])
    const remainingCards = sharedSettings
      .map(card => ({
        ...card,
        fields: (card.fields || []).filter(field => !isSharedScheduleField(field) && !isSharedNotifyField(field)),
      }))
      .filter(card => card.fields.length > 0 || card.previewKey || (card.actions || []).length > 0)
    const ownership = sharedCardOwnership[subtab] || {}
    const composed = [...moduleCards]
    if (scheduleFields.length) composed.push(sharedCard('schedule', scheduleFields, ownership.schedule))
    composed.push(...remainingCards)
    const notifyGroups = ownership.notifyGroups || (ownership.notify ? [ownership.notify] : [])
    const claimedNotifyKeys = new Set()
    for (const notifyOwner of notifyGroups) {
      const groupedFields = notifyFields.filter(field => {
        const module = schemaByKey.get(field.key)?.module || ''
        const matches = !notifyOwner.module || notifyOwner.module === module
        if (matches) claimedNotifyKeys.add(field.key)
        return matches
      })
      if (groupedFields.length) composed.push(sharedCard('notify', groupedFields, notifyOwner))
    }
    const unclaimedNotifyFields = notifyFields.filter(field => !claimedNotifyKeys.has(field.key))
    if (unclaimedNotifyFields.length) composed.push(sharedCard('notify', unclaimedNotifyFields, ownership.notify))
    composed.push(...actions)
    return [subtab, composed]
  }))
}

export function updateReplicaFieldValue(form, field, value) {
  if (!field?.key) throw new Error('Replica field update requires a backend config key')
  form[field.key] = value
  return value
}

export function createReplicaFieldControlProps(form, field) {
  if (!field?.key) throw new Error('Replica field control props require a backend config key')
  return {
    field,
    modelValue: form[field.key],
    'onUpdate:modelValue': value => updateReplicaFieldValue(form, field, value),
  }
}
