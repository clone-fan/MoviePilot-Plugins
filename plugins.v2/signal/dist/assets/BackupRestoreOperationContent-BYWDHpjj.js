import { importShared } from './__federation_fn_import-JrT3xvdd.js';
import { a1 as useTheme, am as _export_sfc, bI as mdiClose } from './mdi-DveizHBi.js';

const hasOwn$1 = (value, key) => Object.prototype.hasOwnProperty.call(value || {}, key);

// The MoviePilot host can attach the API after the federated component mounts.
// Resolve refs at request time so delayed host injection is observable.
function resolvePluginApi(api) {
  if (api && typeof api === 'object' && 'value' in api) return api.value
  return api
}

function readPayloadContextValue(context, source) {
  const parts = String(source || '').split('.').filter(Boolean);
  let value = context;
  for (const part of parts) {
    if (!value || typeof value !== 'object' || !hasOwn$1(value, part)) return undefined
    value = value[part];
  }
  return value
}

function isEmptyPayloadValue(value) {
  if (value === undefined || value === null) return true
  if (Array.isArray(value)) return value.length === 0
  return typeof value === 'string' && value.trim().length === 0
}

function payloadConditionMatches(condition, context) {
  if (!condition) return true
  const value = readPayloadContextValue(context, condition.source);
  if (condition.kind === 'defined') return value !== undefined && value !== null
  if (condition.kind === 'non_empty') return !isEmptyPayloadValue(value)
  return Boolean(value)
}

function normalizePayloadValue(value, type) {
  if (type === 'array') return Array.isArray(value) ? [...value] : []
  if (type === 'boolean') return Boolean(value)
  return Array.isArray(value) ? [...value] : value
}

function buildPayloadFromParameters(parameters = [], context = {}) {
  const payload = {};
  const source = context && typeof context === 'object' ? context : {};
  for (const parameter of Array.isArray(parameters) ? parameters : []) {
    if (!parameter?.key || !payloadConditionMatches(parameter.when, source)) continue
    let value = hasOwn$1(parameter, 'value')
      ? parameter.value
      : readPayloadContextValue(source, parameter.source);
    if (value === undefined && hasOwn$1(parameter, 'default')) value = parameter.default;
    if (value === undefined || (parameter.omitEmpty && isEmptyPayloadValue(value))) continue
    payload[parameter.key] = normalizePayloadValue(value, parameter.type);
  }
  return payload
}

function unwrapResponse(response) {
  const data = response?.data ?? response;
  if (data && typeof data === 'object' && 'data' in data) return data.data
  return data
}

const DEFAULT_PLUGIN_API_TIMEOUT_MS = 60000;

function sanitizeActionMessage(value) {
  return String(value ?? '')
    .replace(/bot\d{5,}:[A-Za-z0-9_-]{20,}/g, 'bot***')
    .replace(/\d{5,}:[A-Za-z0-9_-]{20,}/g, '***TOKEN***')
}

function normalizeActionResponse(res) {
  if (
    res &&
    typeof res === 'object' &&
    ('code' in res || 'msg' in res)
  ) {
    return res
  }
  const inner = res?.data;
  if (
    inner &&
    typeof inner === 'object' &&
    ('code' in inner || 'msg' in inner || 'last_error' in inner || 'error' in inner || 'message' in inner)
  ) {
    return inner
  }
  return res
}

function isActionEnvelope(value) {
  return !!(
    value &&
    typeof value === 'object' &&
    ('code' in value || 'msg' in value || 'last_error' in value || 'error' in value || 'message' in value)
  )
}

function normalizePostActionResponse(path, response) {
  const payload = response?.data ?? response;
  if (
    path === 'create_tg_console_card' &&
    payload &&
    typeof payload === 'object' &&
    !('code' in payload) &&
    !('msg' in payload) &&
    ('message_id' in payload || 'chat_configured' in payload || 'last_error' in payload)
  ) {
    const detail = String(payload.last_error || payload.error || payload.message || '').trim();
    if (detail) {
      return { code: 1, msg: '融合通知卡创建失败', data: payload }
    }
    const messageId = Number(payload.message_id || 0);
    if (messageId > 0) {
      return { code: 0, msg: `融合通知卡已创建 #${messageId}`, data: payload }
    }
  }
  if (isActionEnvelope(response)) return response
  if (isActionEnvelope(payload)) return payload
  return payload
}

function actionMessageFromResponse(res, label = '操作') {
  const payload = normalizeActionResponse(res);
  const ok = !!payload && payload.code === 0;
  const msg = String(payload?.msg ?? '').trim();
  const detailCandidates = [
    payload?.data?.last_error,
    payload?.data?.message,
    payload?.data?.error,
    payload?.last_error,
    payload?.message,
    payload?.error,
    payload?.text,
  ];
  const detail = detailCandidates.find(item => String(item ?? '').trim());
  if (ok && msg) return sanitizeActionMessage(msg)
  if (!ok && detail) return sanitizeActionMessage(detail)
  if (msg) return sanitizeActionMessage(msg)
  return sanitizeActionMessage(detail || `${label}已${ok ? '完成' : '失败'}`)
}

async function withTimeout(promise, path, timeoutMs = DEFAULT_PLUGIN_API_TIMEOUT_MS) {
  if (!Number.isFinite(timeoutMs) || timeoutMs <= 0) return promise

  let timer;
  try {
    return await Promise.race([
      promise,
      new Promise((_, reject) => {
        timer = setTimeout(() => {
          reject(new Error(`MoviePilot plugin API timeout/超时: ${path}`));
        }, timeoutMs);
      }),
    ])
  } finally {
    clearTimeout(timer);
  }
}

async function postPluginApi(api, path, payload = {}, timeoutMs = DEFAULT_PLUGIN_API_TIMEOUT_MS) {
  const apiClient = resolvePluginApi(api);
  if (!apiClient?.post) throw new Error('MoviePilot 插件 API 未就绪')
  const response = await withTimeout(apiClient.post(`plugin/Signal/${path}`, payload), path, timeoutMs);
  return normalizePostActionResponse(path, response)
}

async function getPluginApi(api, path) {
  const apiClient = resolvePluginApi(api);
  if (!apiClient?.get) throw new Error('MoviePilot 插件 API 未就绪')
  const response = await apiClient.get(`plugin/Signal/${path}`);
  return unwrapResponse(response)
}

async function getPluginApiEnvelope(api, path) {
  const apiClient = resolvePluginApi(api);
  if (!apiClient?.get) throw new Error('MoviePilot 插件 API 未就绪')
  const response = await apiClient.get(`plugin/Signal/${path}`);
  return response?.data ?? response
}

function createPluginWorkflowClient(api) {
  return Object.freeze({
    load: path => getPluginApi(api, path),
    execute: (path, payload = {}) => postPluginApi(api, path, payload),
  })
}

// Signal 手动动作 SSOT：动作身份、API path、分组、参数和各表面展示元数据只在这里声明。

const freeze = value => Object.freeze(value);
const hasOwn = (value, key) => Object.prototype.hasOwnProperty.call(value || {}, key);

const ACTION_OPERATION_MODE = freeze({
  direct: 'direct',
  confirm: 'confirm',
  previewConfirm: 'preview_confirm',
});

const ACTION_DISABLED_REASON = freeze({
  plugin: '插件总开关未启用，手动动作已暂停。',
  component: '当前组件未启用，手动动作已暂停。',
});

const actionGroupRegistry = freeze({
  reporting: freeze({ id: 'reporting', label: '汇报与追新', icon: 'mdi-newspaper-variant-outline' }),
  site_downloaders: freeze({ id: 'site_downloaders', label: '站点与下载器', icon: 'mdi-download-network-outline' }),
  system_maintenance: freeze({ id: 'system_maintenance', label: '系统维护', icon: 'mdi-cog-outline' }),
  plugin_governance: freeze({ id: 'plugin_governance', label: '插件治理', icon: 'mdi-puzzle-check-outline' }),
  fusion: freeze({ id: 'fusion', label: '融合卡', icon: 'mdi-message-badge-outline' }),
  subscription_fill: freeze({ id: 'subscription_fill', label: '订阅填充', icon: 'mdi-auto-fix' }),
});

function freezePresentations(presentations = {}) {
  return freeze(Object.fromEntries(
    Object.entries(presentations).map(([surface, presentation]) => [surface, freeze({ ...presentation })]),
  ))
}

function freezePrerequisites(prerequisites = []) {
  return freeze(prerequisites.map(item => freeze({ ...item })))
}

function freezeParameterValue(value) {
  if (Array.isArray(value)) return freeze(value.map(freezeParameterValue))
  if (value && typeof value === 'object') {
    return freeze(Object.fromEntries(
      Object.entries(value).map(([key, item]) => [key, freezeParameterValue(item)]),
    ))
  }
  return value
}

function freezeActionParameters(parameters = []) {
  return freeze(parameters.map(parameter => {
    const normalized = { ...parameter };
    if (hasOwn(normalized, 'value')) normalized.value = freezeParameterValue(normalized.value);
    if (hasOwn(normalized, 'default')) normalized.default = freezeParameterValue(normalized.default);
    if (normalized.when) normalized.when = freezeParameterValue(normalized.when);
    return freeze(normalized)
  }))
}

function defineActionRefresh(refresh = {}) {
  return freeze({
    siteChart: refresh.siteChart === true,
    fusionCard: refresh.fusionCard === true,
  })
}

function defineActionOperation(options = {}, parameters = []) {
  const mode = options.operationMode || ACTION_OPERATION_MODE.direct;
  if (!Object.values(ACTION_OPERATION_MODE).includes(mode)) {
    throw new Error(`Unknown Signal action operation mode: ${mode}`)
  }
  return freeze({
    mode,
    opensPanel: mode !== ACTION_OPERATION_MODE.direct,
    requiresPreview: mode === ACTION_OPERATION_MODE.previewConfirm,
    requiresConfirmation: mode !== ACTION_OPERATION_MODE.direct,
    danger: options.operationDanger === true,
    parameterSource: parameters.length ? 'registry' : 'none',
    confirmationInput: options.operationConfirmationInput
      ? freezeParameterValue(options.operationConfirmationInput)
      : null,
  })
}

function defineAvailability(options = {}) {
  const componentKey = hasOwn(options, 'availabilityComponent')
    ? String(options.availabilityComponent || '')
    : String(options.component || '');
  const componentConfigKeys = hasOwn(options, 'componentConfigKeys')
    ? [...(options.componentConfigKeys || [])]
    : (componentKey ? [`${componentKey}_enabled`] : []);
  const taskKey = hasOwn(options, 'taskKey')
    ? String(options.taskKey || '')
    : componentKey;
  return freeze({
    requiresPlugin: options.requiresPlugin !== false,
    componentKey,
    componentLabel: options.componentLabel || options.label || '',
    componentConfigKeys: freeze(componentConfigKeys),
    componentMode: options.componentMode === 'any' ? 'any' : 'all',
    taskKey,
    prerequisites: freezePrerequisites(options.prerequisites),
  })
}

function defineAction(id, options) {
  const group = actionGroupRegistry[options.groupId];
  if (!group) throw new Error(`Unknown Signal action group: ${options.groupId}`)
  const parameters = freezeActionParameters(options.parameters);
  return freeze({
    id,
    path: options.apiPath || id,
    apiPath: options.apiPath || id,
    key: options.key || id,
    component: options.component || '',
    groupId: group.id,
    group: group.label,
    label: options.label,
    desc: options.desc,
    icon: options.icon,
    iconKey: options.iconKey || '',
    tone: options.tone,
    availability: defineAvailability(options),
    refresh: defineActionRefresh(options.refresh),
    parameters,
    operation: defineActionOperation(options, parameters),
    presentations: freezePresentations(options.presentations),
  })
}

const actionDefinitions = [
  defineAction('run_subscribe_reminder', {
    key: 'subscribe', component: 'subscribe_reminder', groupId: 'reporting',
    label: '订阅追新', desc: '推送今日追新', icon: 'mdi-bell-badge-outline', iconKey: 'rss', tone: 'blue',
    presentations: { config: { label: '手动推送', icon: 'mdi-send-outline' } },
  }),
  defineAction('run_today_transfer', {
    key: 'transfer', groupId: 'reporting',
    label: '今日入库', desc: '刷新今日入库', icon: 'mdi-download-circle-outline', iconKey: 'calendarToday', tone: 'blue',
  }),
  defineAction('run_site_stat', {
    key: 'site_stat', component: 'site_stat', groupId: 'site_downloaders',
    label: '站点统计', desc: '刷新站点增量', icon: 'mdi-chart-pie', iconKey: 'chartPie', tone: 'blue',
    refresh: { siteChart: true },
    presentations: { config: { label: '立即统计', icon: 'mdi-chart-line' } },
  }),
  defineAction('run_backup', {
    key: 'backup', component: 'backup', groupId: 'system_maintenance',
    label: '立即备份', desc: '生成完整归档并投递到已保存目标', icon: 'mdi-database-arrow-up-outline', iconKey: 'database', tone: 'violet',
    presentations: { config: { icon: 'mdi-archive-arrow-up-outline' } },
  }),
  defineAction('run_backup_restore', {
    key: 'backup_restore', groupId: 'system_maintenance',
    availabilityComponent: '', taskKey: '',
    operationMode: ACTION_OPERATION_MODE.confirm, operationDanger: true,
    label: '立即恢复', desc: '选择受检归档和在线恢复范围', icon: 'mdi-backup-restore', iconKey: 'restore', tone: 'violet',
  }),
  defineAction('run_log_clean', {
    key: 'log_clean', component: 'log_clean', groupId: 'system_maintenance',
    label: '清理日志', desc: '按已保存规则截断日志', icon: 'mdi-broom', iconKey: 'broom', tone: 'violet',
  }),
  defineAction('run_health_check', {
    key: 'health', component: 'health_check', groupId: 'system_maintenance',
    label: '健康巡查', desc: '检查关键状态', icon: 'mdi-heart-pulse', iconKey: 'heartPulse', tone: 'green',
    presentations: { config: { icon: 'mdi-heart-pulse-solid' } },
  }),
  defineAction('run_mp_update', {
    key: 'mp_update', component: 'mp_update', groupId: 'system_maintenance',
    label: 'MP 更新', desc: '检查主程序更新', icon: 'mdi-update', iconKey: 'refresh', tone: 'amber',
    presentations: { config: { label: '立即检查并更新' } },
  }),
  defineAction('run_market_update', {
    key: 'plugin_market_sync', component: 'market_update', groupId: 'system_maintenance',
    label: '插件库同步', desc: '同步插件库记录', icon: 'mdi-cloud-sync-outline', iconKey: 'cloudUpload', tone: 'amber',
    presentations: { config: { label: '立即同步插件库', icon: 'mdi-database-sync-outline' } },
  }),
  defineAction('run_plugin_update_reminder', {
    key: 'plugin_update_reminder', component: 'plugin_update_reminder', groupId: 'system_maintenance',
    label: '插件更新', desc: '检查已安装插件更新', icon: 'mdi-bell-alert-outline', iconKey: 'bell', tone: 'amber',
    presentations: { config: { label: '立即检查并更新插件', icon: 'mdi-puzzle-check-outline' } },
  }),
  defineAction('create_tg_console_card', {
    key: 'fusion_build', component: 'fusion_notify', groupId: 'fusion',
    taskKey: '',
    label: '立即建卡', desc: '创建融合汇报卡', icon: 'mdi-card-plus-outline', iconKey: 'cardPlus', tone: 'blue',
    refresh: { fusionCard: true },
    presentations: {
      config: { icon: 'mdi-plus-circle-outline' },
      dashboardFusion: { label: '建卡' },
    },
  }),
  defineAction('refresh_tg_console_card', {
    key: 'fusion_refresh', component: 'fusion_notify', groupId: 'fusion',
    taskKey: '',
    label: '立即刷新', desc: '刷新融合汇报', icon: 'mdi-refresh', iconKey: 'refresh', tone: 'blue',
    refresh: { fusionCard: true },
    presentations: {
      config: { icon: 'mdi-sync' },
      dashboardFusion: { label: '刷新融合卡' },
    },
  }),
  defineAction('run_seed_clean', {
    key: 'seed_clean', component: 'seedclean', groupId: 'site_downloaders',
    taskKey: 'seed_clean',
    label: '立即删种', desc: '按已保存规则处理匹配种子', icon: 'mdi-play', tone: 'red',
    presentations: {
      dashboard: { iconKey: 'trash' },
      mpWidget: { iconKey: 'trash' },
    },
  }),
  defineAction('run_downloader_helper', {
    key: 'downloader_helper', component: 'dltag', groupId: 'site_downloaders',
    taskKey: 'downloader_helper',
    operationMode: ACTION_OPERATION_MODE.previewConfirm, operationDanger: true,
    parameters: [
      {
        key: 'dltag_confirm',
        value: true,
        type: 'boolean',
        when: { source: 'runtime.downloaderHelperPreview.scope_token', kind: 'non_empty' },
      },
      {
        key: 'dltag_preview_token',
        source: 'runtime.downloaderHelperPreview.scope_token',
        omitEmpty: true,
      },
    ],
    label: '下载器助手', desc: '执行下载器标签、辅种与清理任务', icon: 'mdi-play', tone: 'violet',
    presentations: {
      config: { label: '立即执行下载器助手' },
      dashboard: { iconKey: 'tagMultiple' },
      mpWidget: { iconKey: 'tagMultiple' },
    },
  }),
  defineAction('subfill_clear_history', {
    key: 'subfill_clear_history', component: 'subfill', groupId: 'subscription_fill',
    componentConfigKeys: ['subfill_enabled', 'subfill_category_enabled'], componentMode: 'any', taskKey: '',
    label: '清理填充历史', desc: '清理订阅填充历史记录', icon: 'mdi-history', tone: 'violet',
    presentations: {
      dashboard: { iconKey: 'calendarCheck' },
      mpWidget: { iconKey: 'calendarCheck' },
    },
  }),
  defineAction('subfill_clear_handled', {
    key: 'subfill_clear_handled', component: 'subfill', groupId: 'subscription_fill',
    componentConfigKeys: ['subfill_enabled', 'subfill_category_enabled'], componentMode: 'any', taskKey: '',
    label: '清理已处理记录', desc: '清理订阅填充已处理记录', icon: 'mdi-broom', tone: 'violet',
    presentations: {
      dashboard: { iconKey: 'broom' },
      mpWidget: { iconKey: 'broom' },
    },
  }),
  defineAction('run_plugin_uninstall', {
    key: 'plugin_uninstall', component: 'plugin_uninstall', groupId: 'plugin_governance',
    availabilityComponent: '', taskKey: '',
    operationMode: ACTION_OPERATION_MODE.confirm, operationDanger: true,
    prerequisites: [
      { key: 'plugin_uninstall_ids', kind: 'non_empty_array', reason: '请先选择要卸载的插件。' },
    ],
    parameters: [
      { key: 'plugin_uninstall_ids', source: 'config.plugin_uninstall_ids', type: 'array', default: [] },
      { key: 'plugin_uninstall_clear_config', source: 'config.plugin_uninstall_clear_config', type: 'boolean', default: false },
      { key: 'plugin_uninstall_clear_data', source: 'config.plugin_uninstall_clear_data', type: 'boolean', default: false },
      { key: 'plugin_uninstall_delete_source', source: 'config.plugin_uninstall_delete_source', type: 'boolean', default: false },
    ],
    label: '插件卸载', desc: '卸载选中的插件并执行所选清理项', icon: 'mdi-alert-outline', tone: 'red',
    presentations: {
      config: { label: '执行卸载' },
      dashboard: { iconKey: 'trash' },
      mpWidget: { iconKey: 'trash' },
    },
  }),
  defineAction('run_agentopsassistant_purge', {
    key: 'agentopsassistant_purge', component: 'plugin_uninstall', groupId: 'plugin_governance',
    availabilityComponent: '', taskKey: '', requiresPlugin: false,
    operationMode: ACTION_OPERATION_MODE.confirm, operationDanger: true,
    parameters: [
      { key: 'agentopsassistant_purge_confirm', value: true, type: 'boolean' },
    ],
    label: 'mp运维助手专杀', desc: '彻底清除 AgentOpsAssistant 及其运行、配置、数据和源码残留', icon: 'mdi-shield-remove-outline', tone: 'red',
    presentations: {
      config: { label: 'mp运维助手专杀' },
    },
  }),
];

const actionRegistry = freeze(Object.fromEntries(
  actionDefinitions.map(action => [action.id, action]),
));

const manualActionPaths = freeze(actionDefinitions.map(action => action.id));

const quickActionPaths = freeze([
  'run_backup',
  'run_backup_restore',
  'run_health_check',
  'run_seed_clean',
  'run_log_clean',
]);

const fusionCardActionPaths = freeze([
  'create_tg_console_card',
  'refresh_tg_console_card',
]);

const configActionPaths = freeze([
  'create_tg_console_card',
  'refresh_tg_console_card',
  'run_subscribe_reminder',
  'run_site_stat',
  'run_health_check',
  'run_seed_clean',
  'run_downloader_helper',
  'subfill_clear_history',
  'subfill_clear_handled',
  'run_backup',
  'run_backup_restore',
  'run_log_clean',
  'run_mp_update',
  'run_plugin_update_reminder',
  'run_market_update',
  'run_plugin_uninstall',
  'run_agentopsassistant_purge',
]);

const mpWidgetActionPaths = quickActionPaths;

const actionSurfaceRegistry = freeze({
  config: configActionPaths,
  dashboard: quickActionPaths,
  dashboardFusion: fusionCardActionPaths,
  mpWidget: mpWidgetActionPaths,
});

function getActionById(id) {
  return actionRegistry[id] || null
}

function buildActionPayload(itemOrId, context = {}) {
  const id = typeof itemOrId === 'string'
    ? itemOrId
    : (itemOrId?.id || itemOrId?.path || itemOrId?.apiPath || '');
  const action = getActionById(id);
  return buildPayloadFromParameters(action?.parameters, context)
}

function getActionsByIds(ids = []) {
  return ids.map(getActionById).filter(Boolean)
}

function getActionForSurface(id, surface = '') {
  const action = getActionById(id);
  if (!action) return null
  const { presentations, ...base } = action;
  const presentation = presentations[surface] || {};
  return {
    ...base,
    ...presentation,
    key: presentation.key || base.key || base.id,
    label: presentation.label || base.label,
    icon: presentation.icon || base.icon,
    iconKey: presentation.iconKey || base.iconKey,
  }
}

function getActionsForSurface(ids, surface = '') {
  return ids.map(id => getActionForSurface(id, surface)).filter(Boolean)
}

function isActionVisibleOnSurface(itemOrId, surface = '') {
  const id = typeof itemOrId === 'string'
    ? itemOrId
    : (itemOrId?.id || itemOrId?.path || itemOrId?.apiPath || '');
  const visiblePaths = actionSurfaceRegistry[surface];
  return !visiblePaths || visiblePaths.includes(id)
}

function resolveAction(itemOrId) {
  if (typeof itemOrId === 'string') return getActionById(itemOrId)
  if (!itemOrId || typeof itemOrId !== 'object') return null
  const registered = getActionById(itemOrId.id || itemOrId.path || itemOrId.apiPath);
  if (!registered) return itemOrId
  return {
    ...registered,
    ...itemOrId,
    availability: registered.availability,
    refresh: registered.refresh,
    parameters: registered.parameters,
    operation: registered.operation,
  }
}

function actionRefreshes(itemOrId, target) {
  const action = resolveAction(itemOrId);
  return Boolean(action?.refresh?.[target])
}

function readComponentState(componentStates, key) {
  if (!key || !componentStates) return undefined
  if (componentStates instanceof Map) {
    if (!componentStates.has(key)) return undefined
    const value = componentStates.get(key);
    return value && typeof value === 'object' && hasOwn(value, 'enabled') ? value.enabled !== false : value !== false
  }
  if (!hasOwn(componentStates, key)) return undefined
  const value = componentStates[key];
  return value && typeof value === 'object' && hasOwn(value, 'enabled') ? value.enabled !== false : value !== false
}

function findTask(tasks, taskKey) {
  if (!taskKey || !Array.isArray(tasks)) return null
  return tasks.find(task => [task?.key, task?.id, task?.service_id].some(value => String(value || '') === taskKey)) || null
}

function resolveComponentEnabled(policy, context = {}) {
  if (!policy.componentKey && !policy.componentConfigKeys.length && !policy.taskKey) return true

  const explicitState = readComponentState(context.componentStates, policy.componentKey);
  if (explicitState !== undefined) return explicitState

  const task = findTask(context.tasks, policy.taskKey);
  if (task) {
    if (hasOwn(task, 'enabled')) return task.enabled !== false
    if (hasOwn(task?.effective_state, 'component_enabled')) return task.effective_state.component_enabled !== false
  }

  if (context.config && policy.componentConfigKeys.length) {
    const states = policy.componentConfigKeys.map(key => Boolean(context.config[key]));
    return policy.componentMode === 'any' ? states.some(Boolean) : states.every(Boolean)
  }

  return true
}

function hasConfiguredValue(value, kind = '') {
  if (kind === 'non_empty_array') return Array.isArray(value) && value.length > 0
  if (Array.isArray(value)) return value.length > 0
  return String(value ?? '').trim().length > 0
}

function resolvePrerequisiteReason(policy, context = {}) {
  for (const prerequisite of policy.prerequisites) {
    const values = context.preconditionValues || {};
    const value = hasOwn(values, prerequisite.key) ? values[prerequisite.key] : context.config?.[prerequisite.key];
    if (!hasConfiguredValue(value, prerequisite.kind)) return prerequisite.reason || ''
  }
  return ''
}

function actionMatchesRunning(action, runningActionId) {
  if (!runningActionId) return false
  const running = String(runningActionId);
  return [action?.id, action?.path, action?.apiPath, action?.key].some(value => String(value || '') === running)
}

function resolveActionAvailability(itemOrId, context = {}) {
  const action = resolveAction(itemOrId);
  if (!action) {
    return freeze({ visible: false, disabled: true, disabledReason: '', pluginEnabled: true, componentEnabled: true, prerequisitesMet: true, running: false })
  }

  const policy = action.availability || defineAvailability(action);
  const visible = isActionVisibleOnSurface(action, context.surface || '');
  const pluginEnabled = policy.requiresPlugin ? context.pluginEnabled !== false : true;
  const componentEnabled = resolveComponentEnabled(policy, context);
  const prerequisiteReason = resolvePrerequisiteReason(policy, context);
  const running = actionMatchesRunning(action, context.runningActionId);
  const busy = Boolean(context.runningActionId);

  let disabledReason = '';
  if (!pluginEnabled) {
    disabledReason = ACTION_DISABLED_REASON.plugin;
  } else if (!componentEnabled) {
    disabledReason = policy.componentLabel
      ? `${policy.componentLabel}未启用，手动动作已暂停。`
      : ACTION_DISABLED_REASON.component;
  } else if (prerequisiteReason) {
    disabledReason = prerequisiteReason;
  } else if (running || (context.blockWhileBusy && busy)) {
    disabledReason = `${context.runningActionLabel || action.label || '当前动作'}正在执行，请等待完成。`;
  }

  return freeze({
    visible,
    disabled: !visible || Boolean(disabledReason),
    disabledReason,
    pluginEnabled,
    componentEnabled,
    prerequisitesMet: !prerequisiteReason,
    running,
  })
}

function createV31QuickActions(iconSet = {}, surface = 'dashboard') {
  const surfacePaths = actionSurfaceRegistry[surface] || quickActionPaths;
  return getActionsForSurface(surfacePaths, surface).map(action => ({
    ...action,
    icon: iconSet[action.iconKey] || action.icon,
  }))
}

freeze(getActionsByIds(manualActionPaths));
const quickActionItems = freeze(getActionsByIds(quickActionPaths));
freeze(getActionsByIds(fusionCardActionPaths));
freeze(getActionsByIds(mpWidgetActionPaths));

const quickActionGroupIds = freeze([...new Set(quickActionItems.map(action => action.groupId))]);
freeze(quickActionGroupIds.map(groupId => {
  const group = actionGroupRegistry[groupId];
  return freeze({
    id: group.id,
    group: group.label,
    icon: group.icon,
    actions: freeze(quickActionItems.filter(action => action.groupId === groupId)),
  })
}));

const {computed: computed$4,reactive: reactive$1,ref: ref$1} = await importShared('vue');

function resolveMaybeRef(value) {
  if (typeof value === 'function') return value()
  if (value && typeof value === 'object' && 'value' in value) return value.value
  return value
}

function normalizeAction(actionOrId, label = '') {
  const source = actionOrId && typeof actionOrId === 'object' ? actionOrId : null;
  const requestedId = String(source?.id || source?.path || source?.apiPath || actionOrId || '');
  const registered = getActionById(requestedId);
  const action = { ...(registered || {}), ...(source || {}) };
  const id = String(action.id || requestedId);
  const path = String(action.apiPath || action.path || id);
  return {
    ...action,
    id,
    path,
    apiPath: path,
    label: String(label || action.label || path || '操作'),
  }
}

function actionExecutionId(actionOrId) {
  const action = normalizeAction(actionOrId);
  return action.id || action.path
}

function useActionRunner(options = {}) {
  const {
    api,
    getDisabledMessage = () => '',
    getPayloadContext = () => ({}),
    onSuccess = null,
    onFailure = null,
    messageTimeoutMs = 5000,
  } = options;
  const runningActions = reactive$1(new Map());
  const inFlight = new Map();
  const actionMessage = ref$1('');
  const actionOk = ref$1(true);
  let clearTimer = 0;

  const runningActionIds = computed$4(() => Array.from(runningActions.keys()));
  const runningActionLabels = computed$4(() => Array.from(runningActions.values()).map(item => item.label));
  const actionRunning = computed$4(() => runningActionIds.value[0] || '');
  const runningActionLabel = computed$4(() => runningActions.get(actionRunning.value)?.label || '');

  function cancelMessageClear() {
    if (!clearTimer) return
    clearTimeout(clearTimer);
    clearTimer = 0;
  }

  function scheduleClear() {
    cancelMessageClear();
    if (!Number.isFinite(messageTimeoutMs) || messageTimeoutMs <= 0) return
    clearTimer = setTimeout(() => {
      actionMessage.value = '';
      clearTimer = 0;
    }, messageTimeoutMs);
  }

  function setMessage(message, ok = false, { autoClear = true } = {}) {
    cancelMessageClear();
    actionOk.value = Boolean(ok);
    actionMessage.value = String(message || '');
    if (autoClear && actionMessage.value) scheduleClear();
  }

  function clearMessage() {
    cancelMessageClear();
    actionMessage.value = '';
  }

  function isActionRunning(actionOrId) {
    const id = actionExecutionId(actionOrId);
    // The reactive map is the render-state source; inFlight remains the promise guard.
    return Boolean(id && runningActions.has(id))
  }

  function rejectedResult(action, reason, flags = {}) {
    setMessage(reason, false);
    return Promise.resolve({
      started: false,
      ok: false,
      requestOk: false,
      refreshOk: false,
      action,
      path: action.path,
      ...flags,
    })
  }

  function runAction(actionOrId, label = '') {
    const action = normalizeAction(actionOrId, label);
    const id = actionExecutionId(action);
    const path = action.path;
    if (!id || !path) return rejectedResult(action, '动作定义不完整，已阻止执行。', { invalid: true })
    if (inFlight.has(id)) {
      return rejectedResult(action, `${runningActions.get(id)?.label || action.label}正在执行，请等待完成。`, { duplicate: true })
    }

    const apiClient = resolveMaybeRef(api);
    if (!apiClient) return rejectedResult(action, 'MoviePilot 插件 API 未就绪', { unavailable: true })
    const disabledMessage = getDisabledMessage(action) || '';
    if (disabledMessage) return rejectedResult(action, disabledMessage, { disabled: true })

    clearMessage();
    actionOk.value = true;
    runningActions.set(id, { id, path, label: action.label });
    setMessage(`${action.label}正在执行，请稍候。`, true, { autoClear: false });
    inFlight.set(id, null);

    const execution = (async () => {
      let payload = {};
      let response = null;
      try {
        const payloadContext = typeof getPayloadContext === 'function'
          ? getPayloadContext(action)
          : resolveMaybeRef(getPayloadContext);
        payload = buildActionPayload(action, payloadContext || {});
        response = await postPluginApi(apiClient, path, payload);
        const requestOk = !!response && response.code === 0;
        const responseMessage = actionMessageFromResponse(response, action.label);
        if (!requestOk) {
          actionOk.value = false;
          actionMessage.value = responseMessage;
          if (typeof onFailure === 'function') {
            try { await onFailure({ action, res: response, path, payload }); } catch (refreshError) { /* keep API error as primary */ }
          }
          return { started: true, ok: false, requestOk: false, refreshOk: false, action, path, payload, response }
        }

        try {
          if (typeof onSuccess === 'function') await onSuccess({ action, res: response, path, payload });
        } catch (refreshError) {
          const refreshMessage = actionMessageFromResponse({ code: 1, msg: refreshError?.message }, '刷新');
          actionOk.value = false;
          actionMessage.value = `${responseMessage}，但刷新失败：${refreshMessage}`;
          return {
            started: true,
            ok: false,
            requestOk: true,
            refreshOk: false,
            action,
            path,
            payload,
            response,
            refreshError,
          }
        }

        actionOk.value = true;
        actionMessage.value = responseMessage;
        return { started: true, ok: true, requestOk: true, refreshOk: true, action, path, payload, response }
      } catch (error) {
        actionOk.value = false;
        actionMessage.value = actionMessageFromResponse({ code: 1, msg: error?.message }, action.label);
        if (typeof onFailure === 'function') {
          try { await onFailure({ action, error, path, payload, response }); } catch (refreshError) { /* keep request error as primary */ }
        }
        return { started: true, ok: false, requestOk: false, refreshOk: false, action, path, payload, response, error }
      } finally {
        inFlight.delete(id);
        runningActions.delete(id);
        scheduleClear();
      }
    })();

    inFlight.set(id, execution);
    return execution
  }

  return {
    runningActions,
    runningActionIds,
    runningActionLabels,
    actionRunning,
    runningActionLabel,
    actionMessage,
    actionOk,
    isActionRunning,
    setMessage,
    clearMessage,
    runAction,
  }
}

// Config action-operation orchestration lives in its feature composable; this adapter owns runner context and post-success refresh only.
function useConfigActionRunner(form, api, installedPlugins, loadInstalledPlugins) {
  const notificationLockedByFusion = computed$4(() => !!form.fusion_notify_enabled);
  const downloaderHelperPreview = ref$1(null);
  const operationPayloadSnapshot = ref$1(null);
  let runner = null;

  function configAction(itemOrPath, label = '') {
    return normalizeAction(itemOrPath, label)
  }

  function getActionAvailability(itemOrPath, context = {}) {
    const current = configAction(itemOrPath);
    const running = runner?.isActionRunning(current) === true;
    return resolveActionAvailability(current, {
      surface: 'config',
      pluginEnabled: form.enabled !== false,
      config: form,
      runningActionId: running ? current.id : '',
      runningActionLabel: running ? current.label : '',
      ...context,
    })
  }

  function actionDisabledMessage(itemOrPath, context = {}) {
    return getActionAvailability(itemOrPath, context).disabledReason
  }

  function actionPayloadContext() {
    return operationPayloadSnapshot.value || {
      config: form,
      runtime: {
        downloaderHelperPreview: downloaderHelperPreview.value,
      },
    }
  }

  function installedPluginValues() {
    return new Set((installedPlugins.value || []).map(item => String(item?.value ?? item?.id ?? item?.title ?? item ?? '')))
  }

  async function refreshAfterPluginUninstall(res) {
    const uninstalled = Array.isArray(res?.data?.uninstalled) ? res.data.uninstalled : [];
    const removed = new Set(uninstalled
      .filter(item => item && item.success !== false)
      .map(item => String(item.plugin_id || item.id || item.value || ''))
      .filter(Boolean));
    await loadInstalledPlugins({ throwOnError: true });
    const available = installedPluginValues();
    form.plugin_uninstall_ids = (Array.isArray(form.plugin_uninstall_ids) ? form.plugin_uninstall_ids : [])
      .filter(id => !removed.has(String(id)) && available.has(String(id)));
  }

  runner = useActionRunner({
    api,
    getDisabledMessage: current => actionDisabledMessage(current),
    getPayloadContext: actionPayloadContext,
    onSuccess: async ({ action: current, res }) => {
      if (current.id === 'run_downloader_helper') {
        downloaderHelperPreview.value = res?.data?.confirm_required ? res.data : null;
      }
      if (['run_plugin_uninstall', 'run_agentopsassistant_purge'].includes(current.id)) {
        await refreshAfterPluginUninstall(res);
      }
    },
  });

  const action = {};
  Object.defineProperties(action, {
    running: {
      enumerable: true,
      get: () => runner.actionRunning.value,
    },
    message: {
      enumerable: true,
      get: () => runner.actionMessage.value,
      set: value => runner.setMessage(value, runner.actionOk.value, { autoClear: false }),
    },
    ok: {
      enumerable: true,
      get: () => runner.actionOk.value,
      set: value => { runner.actionOk.value = Boolean(value); },
    },
    downloaderHelperPreview: {
      enumerable: true,
      get: () => downloaderHelperPreview.value,
      set: value => { downloaderHelperPreview.value = value; },
    },
    operationPayloadSnapshot: {
      enumerable: true,
      get: () => operationPayloadSnapshot.value,
      set: value => { operationPayloadSnapshot.value = value; },
    },
  });

  function executeConfigAction(path, label = '') {
    return runner.runAction(configAction(path, label))
  }

  return {
    action,
    // Expose the computed running state directly so consumers can bind it
    // reactively. The legacy `action.running` getter is kept for operation
    // panel compatibility, but plain-object getters are not a reliable
    // template dependency boundary in the MoviePilot host.
    actionRunning: runner.actionRunning,
    notificationLockedByFusion,
    getActionAvailability,
    actionDisabledMessage,
    isActionRunning: runner.isActionRunning,
    runningActionIds: runner.runningActionIds,
    clearActionMessage: runner.clearMessage,
    runAction: executeConfigAction,
  }
}

const {computed: computed$3,reactive} = await importShared('vue');

const BACKUP_RESTORE_SOURCES = Object.freeze([
  Object.freeze({ value: 'local', label: '本地归档' }),
  Object.freeze({ value: 'webdav', label: '已保存 WebDAV' }),
  Object.freeze({ value: 'temporary_webdav', label: '临时 WebDAV' }),
  Object.freeze({ value: 'upload', label: '浏览器导入' }),
]);

const BACKUP_RESTORE_PLUGIN_SCOPES = Object.freeze([
  Object.freeze({ value: 'all', label: '全部插件' }),
  Object.freeze({ value: 'include', label: '仅恢复指定插件' }),
  Object.freeze({ value: 'exclude', label: '排除指定插件' }),
]);

function resolveMaybeValue(value) {
  if (typeof value === 'function') return value()
  if (value && typeof value === 'object' && Object.prototype.hasOwnProperty.call(value, 'value')) return value.value
  return value
}

function responseMessage(response, fallback) {
  return String(response?.msg || response?.data?.message || response?.text || fallback || '')
}

function cloneJson(value) {
  try {
    return JSON.parse(JSON.stringify(value))
  } catch {
    return {}
  }
}

function normalizePluginOptions(inspection) {
  const manifestItems = inspection?.manifest?.components?.plugins?.items;
  const rawItems = Array.isArray(inspection?.plugin_options)
    ? inspection.plugin_options
    : Array.isArray(inspection?.descriptor?.plugins)
      ? inspection.descriptor.plugins
      : Array.isArray(manifestItems)
        ? manifestItems
        : [];
  const seen = new Set();
  return rawItems
    .map(item => {
      if (item && typeof item === 'object') {
        const value = String(item.id || item.value || item.key || '').trim();
        return value ? { value, label: String(item.label || item.name || value) } : null
      }
      const value = String(item || '').trim();
      return value ? { value, label: value } : null
    })
    .filter(item => {
      if (!item || seen.has(item.value)) return false
      seen.add(item.value);
      return true
    })
}

function downloadBase64File(payload) {
  if (typeof document === 'undefined' || typeof atob !== 'function') return false
  const binary = atob(String(payload?.content_base64 || ''));
  const bytes = new Uint8Array(binary.length);
  for (let index = 0; index < binary.length; index += 1) bytes[index] = binary.charCodeAt(index);
  const url = URL.createObjectURL(new Blob([bytes], { type: 'application/zip' }));
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = String(payload?.name || 'signal-backup.zip');
  anchor.click();
  URL.revokeObjectURL(url);
  return true
}

function useBackupRestore(api, options = {}) {
  const client = createPluginWorkflowClient(api);
  const state = reactive({
    source: 'local',
    archives: [],
    archiveName: '',
    inspection: null,
    components: { moviepilot: true, plugins: true },
    pluginScope: 'all',
    pluginIds: [],
    temporaryWebdav: {
      hostname: '',
      login: '',
      password: '',
      digest_auth: false,
      disable_check: false,
    },
    message: '',
    result: null,
    operationStatus: null,
  });
  const loading = reactive({ list: false, inspect: false, import: false, download: false, execute: false, status: false });

  const pluginEnabled = computed$3(() => resolveMaybeValue(options.pluginEnabled) !== false);
  const unavailableMessage = computed$3(() => pluginEnabled.value ? '' : '插件总开关未启用，恢复操作不可用。');
  const pluginOptions = computed$3(() => normalizePluginOptions(state.inspection));
  const selectedComponents = computed$3(() => Object.entries(state.components)
    .filter(([, enabled]) => enabled)
    .map(([key]) => key));
  const scopeNeedsPlugins = computed$3(() => ['include', 'exclude'].includes(state.pluginScope));
  const canExecute = computed$3(() => Boolean(
    pluginEnabled.value
    && state.inspection?.descriptor?.backup_id
    && selectedComponents.value.length
    && (!scopeNeedsPlugins.value || state.pluginIds.length),
  ));
  const busy = computed$3(() => Object.values(loading).some(Boolean));

  function temporaryWebdavPayload() {
    if (state.source !== 'temporary_webdav') return undefined
    return cloneJson(state.temporaryWebdav)
  }

  function clearSelection() {
    state.archives = [];
    state.archiveName = '';
    state.inspection = null;
    state.pluginScope = 'all';
    state.pluginIds = [];
    state.message = '';
    state.result = null;
  }

  function reset() {
    state.source = 'local';
    clearSelection();
    state.components.moviepilot = true;
    state.components.plugins = true;
    state.temporaryWebdav.hostname = '';
    state.temporaryWebdav.login = '';
    state.temporaryWebdav.password = '';
    state.temporaryWebdav.digest_auth = false;
    state.temporaryWebdav.disable_check = false;
    state.operationStatus = null;
  }

  function changeSource(source) {
    state.source = String(source || 'local');
    clearSelection();
  }

  async function loadArchives() {
    if (!pluginEnabled.value || loading.list) return { code: 1, msg: unavailableMessage.value }
    loading.list = true;
    state.message = '';
    try {
      const response = await client.execute('backup_archives', {
        source: state.source,
        temporary_webdav: temporaryWebdavPayload(),
      });
      if (response?.code !== 0) throw new Error(responseMessage(response, '备份归档列表获取失败'))
      state.archives = Array.isArray(response?.items)
        ? response.items
        : (Array.isArray(response?.data?.items) ? response.data.items : []);
      state.archiveName = state.archives[0]?.name || '';
      state.inspection = null;
      state.message = state.archives.length ? '' : '当前来源没有可用归档。';
      return response
    } catch (error) {
      state.archives = [];
      state.archiveName = '';
      state.inspection = null;
      state.message = error?.message || '备份归档列表获取失败';
      return { code: 1, msg: state.message }
    } finally {
      loading.list = false;
    }
  }

  function applyInspection(response) {
    if (response?.code !== 0 || !response?.data?.descriptor?.backup_id) {
      throw new Error(responseMessage(response, '备份归档检查失败'))
    }
    state.inspection = response.data;
    state.archiveName = response.data.descriptor.name || state.archiveName;
    const online = new Set(response.data.online_components || []);
    state.components.moviepilot = online.has('moviepilot');
    state.components.plugins = online.has('plugins');
    state.pluginScope = 'all';
    state.pluginIds = [];
    state.message = '';
    return response
  }

  async function inspectArchive() {
    if (!state.archiveName || loading.inspect) return { code: 1, msg: '请选择归档。' }
    loading.inspect = true;
    state.message = '';
    try {
      const response = await client.execute('backup_archive', {
        source: state.source,
        archive_name: state.archiveName,
        temporary_webdav: temporaryWebdavPayload(),
      });
      return applyInspection(response)
    } catch (error) {
      state.inspection = null;
      state.message = error?.message || '备份归档检查失败';
      return { code: 1, msg: state.message }
    } finally {
      loading.inspect = false;
    }
  }

  async function importArchive(filename, contentBase64) {
    if (loading.import) return { code: 1, msg: '归档正在导入。' }
    loading.import = true;
    state.message = '';
    try {
      const response = await client.execute('import_backup_archive', {
        filename: String(filename || 'signal-backup.zip'),
        content_base64: String(contentBase64 || ''),
      });
      changeSource('upload');
      return applyInspection(response)
    } catch (error) {
      state.inspection = null;
      state.message = error?.message || '浏览器归档导入失败';
      return { code: 1, msg: state.message }
    } finally {
      loading.import = false;
    }
  }

  async function downloadArchive() {
    if (!state.archiveName || loading.download) return { code: 1, msg: '请选择归档。' }
    loading.download = true;
    state.message = '';
    try {
      const response = await client.execute('download_backup_archive', {
        source: state.source,
        archive_name: state.archiveName,
        temporary_webdav: temporaryWebdavPayload(),
      });
      if (response?.code !== 0 || !response?.data?.content_base64) {
        throw new Error(responseMessage(response, '备份归档下载失败'))
      }
      downloadBase64File(response.data);
      return response
    } catch (error) {
      state.message = error?.message || '备份归档下载失败';
      return { code: 1, msg: state.message }
    } finally {
      loading.download = false;
    }
  }

  async function queryOperationStatus() {
    if (loading.status) return state.operationStatus
    loading.status = true;
    try {
      state.operationStatus = await client.load('backup_operation_status');
      return state.operationStatus
    } catch (error) {
      state.message = error?.message || '恢复状态查询失败';
      return null
    } finally {
      loading.status = false;
    }
  }

  function resultFromOperationStatus(status, backupId) {
    const current = status?.current;
    if (current?.backup_id === backupId) {
      return { code: 1, msg: '恢复请求连接已中断，但服务端仍在执行，请稍后查询当前操作。', data: current, disconnected: true }
    }
    const recent = [...(status?.recent || [])].reverse().find(item => item?.backup_id === backupId);
    if (!recent) return null
    return {
      code: ['success', 'partial'].includes(recent.status) ? 0 : 1,
      msg: recent.message || '已从最近操作记录恢复结果。',
      data: recent,
      disconnected: true,
    }
  }

  async function executeRestore() {
    if (!canExecute.value || loading.execute) {
      const message = unavailableMessage.value || '请先检查归档并完成恢复范围选择。';
      state.result = { code: 1, msg: message };
      return state.result
    }
    loading.execute = true;
    state.message = '';
    const backupId = state.inspection.descriptor.backup_id;
    try {
      state.result = await client.execute('run_backup_restore', {
        backup_id: backupId,
        components: selectedComponents.value,
        plugin_scope: state.pluginScope,
        plugin_ids: scopeNeedsPlugins.value ? [...state.pluginIds] : [],
      });
      return state.result
    } catch (error) {
      const status = await queryOperationStatus();
      state.result = resultFromOperationStatus(status, backupId) || {
        code: 1,
        msg: error?.message || '备份恢复执行失败',
        data: { status: 'unknown' },
        disconnected: true,
      };
      return state.result
    } finally {
      loading.execute = false;
    }
  }

  return {
    state,
    loading,
    sources: BACKUP_RESTORE_SOURCES,
    pluginScopes: BACKUP_RESTORE_PLUGIN_SCOPES,
    pluginOptions,
    selectedComponents,
    scopeNeedsPlugins,
    pluginEnabled,
    unavailableMessage,
    canExecute,
    busy,
    reset,
    changeSource,
    loadArchives,
    inspectArchive,
    importArchive,
    downloadArchive,
    queryOperationStatus,
    executeRestore,
  }
}

const {computed: computed$2} = await importShared('vue');

const supportedThemes = ['transparent', 'dark', 'light', 'purple', 'glass', 'system'];

function normalizeThemeName(value) {
  const name = String(value || '').toLowerCase();
  const matched = supportedThemes.find(theme => name.includes(theme));
  if (matched !== 'system') return matched || 'dark'
  if (typeof window !== 'undefined' && window.matchMedia) {
    return window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark'
  }
  return 'dark'
}

// Federation roots use this class instead of relying on Vuetify's .v-theme--*
// selectors, which are removed from plugin CSS during the MoviePilot build.
function useAgentOpsTheme() {
  const vuetifyTheme = useTheme();
  const themeName = computed$2(() => normalizeThemeName(vuetifyTheme.global.name.value));
  const rootThemeClass = computed$2(() => `agentops-theme--${themeName.value}`);

  return { themeName, rootThemeClass }
}

const {toDisplayString:_toDisplayString$1,openBlock:_openBlock$1,createElementBlock:_createElementBlock$1,createCommentVNode:_createCommentVNode$1,createElementVNode:_createElementVNode$1,unref:_unref,renderSlot:_renderSlot,vShow:_vShow,withDirectives:_withDirectives$1,mergeProps:_mergeProps,withModifiers:_withModifiers,Teleport:_Teleport,createBlock:_createBlock} = await importShared('vue');


const _hoisted_1$1 = ["data-action-id", "data-action-mode"];
const _hoisted_2$1 = ["aria-labelledby", "aria-describedby", "aria-busy", "data-operation-state"];
const _hoisted_3$1 = { class: "aoa-action-operation-panel__head" };
const _hoisted_4$1 = {
  key: 0,
  class: "aoa-action-operation-panel__kicker"
};
const _hoisted_5$1 = ["id"];
const _hoisted_6$1 = ["disabled"];
const _hoisted_7$1 = {
  viewBox: "0 0 24 24",
  width: "18",
  height: "18",
  "aria-hidden": "true"
};
const _hoisted_8$1 = ["d"];
const _hoisted_9$1 = { class: "aoa-action-operation-panel__body" };
const _hoisted_10$1 = {
  class: "aoa-action-operation-panel__stage",
  "data-operation-stage": "editing"
};
const _hoisted_11$1 = {
  class: "aoa-action-operation-panel__stage",
  "data-operation-stage": "running",
  role: "status",
  "aria-live": "polite"
};
const _hoisted_12$1 = { class: "aoa-action-operation-panel__running" };
const _hoisted_13$1 = ["id", "role", "aria-live"];
const _hoisted_14$1 = ["data-tone"];
const _hoisted_15$1 = { key: 0 };
const _hoisted_16$1 = { class: "aoa-action-operation-panel__actions" };
const _hoisted_17$1 = ["disabled"];
const _hoisted_18$1 = ["disabled", "aria-busy"];
const _hoisted_19$1 = {
  key: 0,
  viewBox: "0 0 24 24",
  width: "15",
  height: "15",
  "aria-hidden": "true"
};
const _hoisted_20$1 = ["d"];
const _hoisted_21$1 = {
  key: 2,
  type: "button",
  class: "aoa-action-operation-panel__button aoa-action-operation-panel__button--confirm aoa-button",
  disabled: ""
};

const {computed: computed$1,nextTick,onBeforeUnmount,onMounted,ref,useAttrs,watch} = await importShared('vue');


const _sfc_main$1 = /*@__PURE__*/Object.assign({ inheritAttrs: false }, {
  __name: 'ActionOperationPanel',
  props: {
  open: { type: Boolean, default: false },
  action: { type: Object, default: () => ({}) },
  title: { type: String, default: '' },
  kicker: { type: String, default: '' },
  danger: { type: Boolean, default: false },
  state: {
    type: String,
    default: 'editing',
    validator: value => ['editing', 'running', 'result'].includes(value),
  },
  result: { type: Object, default: null },
  confirmLabel: { type: String, default: '确认执行' },
  cancelLabel: { type: String, default: '取消' },
  closeLabel: { type: String, default: '关闭' },
  runningLabel: { type: String, default: '正在执行…' },
  confirmIconPath: { type: String, default: '' },
  confirmDisabled: { type: Boolean, default: false },
  busy: { type: Boolean, default: false },
  returnFocusSelector: { type: String, default: '' },
  themeClass: { type: [String, Array, Object], default: '' },
  portalStyle: { type: Object, default: () => ({}) },
  rootAttrs: { type: Object, default: () => ({}) },
  confirmAttrs: { type: Object, default: () => ({}) },
  cancelAttrs: { type: Object, default: () => ({}) },
},
  emits: ['cancel', 'confirm'],
  setup(__props, { emit: __emit }) {



const props = __props;

const emit = __emit;
const attrs = useAttrs();
const dialogRef = ref(null);
const confirmLocked = ref(false);
let previousFocus = null;

const actionId = computed$1(() => String(props.action?.id || props.action?.path || 'action'));
const actionMode = computed$1(() => String(props.action?.operation?.mode || 'confirm'));
const panelState = computed$1(() => props.busy ? 'running' : props.state);
const isRunning = computed$1(() => panelState.value === 'running');
const isResult = computed$1(() => panelState.value === 'result');
const overlayAttrs = computed$1(() => ({ ...attrs, ...props.rootAttrs }));
const dialogTitle = computed$1(() => props.title || props.action?.label || '确认操作');
const dialogId = computed$1(() => `aoa-action-operation-${actionId.value.replace(/[^a-zA-Z0-9_-]/g, '-')}`);
const resultId = computed$1(() => `${dialogId.value}-result`);
const dialogDescriptionIds = computed$1(() => isResult.value ? resultId.value : undefined);
const confirmButtonDisabled = computed$1(() => panelState.value !== 'editing' || confirmLocked.value || props.confirmDisabled);
const resultOk = computed$1(() => {
  if (props.result?.requestOk === true && props.result?.refreshOk === false) return false
  if (typeof props.result?.ok === 'boolean') return props.result.ok
  if (typeof props.result?.success === 'boolean') return props.result.success
  return props.result?.code === 0
});
const resultMessage = computed$1(() => String(
  props.result?.message
  || props.result?.msg
  || props.result?.response?.msg
  || props.result?.response?.data?.message
  || props.result?.data?.message
  || (resultOk.value ? '操作已完成。' : '操作未完成，请检查结果后重试。'),
));
const resultDetail = computed$1(() => {
  if (props.result?.requestOk === true && props.result?.refreshOk === false) return '业务操作已完成，但界面刷新失败；请手动刷新页面核对最新状态。'
  if (props.result?.partial === true || props.result?.data?.partial === true || props.result?.data?.status === 'partial') return '操作部分完成，请查看结果明细。'
  if (props.result?.disconnected === true) return '连接中断后已查询服务端操作状态，请勿直接重复提交。'
  return ''
});

function focusInitialControl() {
  nextTick(() => {
    const closeButton = dialogRef.value?.querySelector?.('[data-action-operation-close]:not(:disabled)');
    const target = closeButton || focusableElements()[0] || dialogRef.value;
    target?.focus?.({ preventScroll: true });
  });
}

function queryReturnFocusTarget() {
  if (!props.returnFocusSelector || typeof document === 'undefined') return null
  try {
    return document.querySelector(props.returnFocusSelector)
  } catch {
    return null
  }
}

function canReceiveFocus(target) {
  if (!target?.isConnected || target.disabled || target.getAttribute?.('aria-disabled') === 'true') return false
  return target.getClientRects?.().length > 0
}

function restoreFocus() {
  const selectorTarget = queryReturnFocusTarget();
  const previousTarget = canReceiveFocus(previousFocus) ? previousFocus : null;
  const fallbackTarget = typeof document !== 'undefined'
    ? document.querySelector('.v31-quick-action:not(:disabled), [data-actions-widget-refresh]:not(:disabled)')
    : null;
  const target = canReceiveFocus(selectorTarget)
    ? selectorTarget
    : previousTarget || (canReceiveFocus(fallbackTarget) ? fallbackTarget : null);
  target?.focus?.({ preventScroll: true });
  previousFocus = null;
}

function requestCancel(reason = 'cancel') {
  if (!props.open || isRunning.value || confirmLocked.value) return
  emit('cancel', { reason, action: props.action });
}

function requestConfirm() {
  if (!props.open || confirmButtonDisabled.value) return
  confirmLocked.value = true;
  emit('confirm', { action: props.action });
}

function focusableElements() {
  if (!dialogRef.value) return []
  return Array.from(dialogRef.value.querySelectorAll(
    'button:not(:disabled), input:not(:disabled), textarea:not(:disabled), select:not(:disabled), [tabindex]:not([tabindex="-1"])',
  )).filter(element => element.getClientRects().length > 0)
}

function handleDialogKeydown(event) {
  if (event.key !== 'Tab') return
  const focusable = focusableElements();
  if (!focusable.length) {
    event.preventDefault();
    dialogRef.value?.focus?.();
    return
  }
  const first = focusable[0];
  const last = focusable.at(-1);
  if (event.shiftKey && document.activeElement === first) {
    event.preventDefault();
    last.focus();
  } else if (!event.shiftKey && document.activeElement === last) {
    event.preventDefault();
    first.focus();
  }
}

function handleWindowKeydown(event) {
  if (props.open && event.key === 'Escape') {
    event.preventDefault();
    requestCancel('escape');
  }
}

watch(() => props.open, open => {
  if (open) {
    previousFocus = typeof document !== 'undefined' ? document.activeElement : null;
    confirmLocked.value = false;
    focusInitialControl();
  } else {
    confirmLocked.value = false;
    restoreFocus();
  }
});

watch(actionId, () => {
  confirmLocked.value = false;
  if (props.open) focusInitialControl();
});

watch(panelState, state => {
  if (state !== 'editing') confirmLocked.value = false;
  if (props.open && state === 'result') focusInitialControl();
});

onMounted(() => {
  window.addEventListener('keydown', handleWindowKeydown);
  if (props.open) {
    previousFocus = document.activeElement;
    confirmLocked.value = false;
    focusInitialControl();
  }
});
onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleWindowKeydown);
  restoreFocus();
});

return (_ctx, _cache) => {
  return (_openBlock$1(), _createBlock(_Teleport, { to: "body" }, [
    (__props.open)
      ? (_openBlock$1(), _createElementBlock$1("div", _mergeProps({ key: 0 }, overlayAttrs.value, {
          class: ["aoa-action-operation-overlay aoa-root", __props.themeClass],
          style: __props.portalStyle,
          "data-action-id": actionId.value,
          "data-action-mode": actionMode.value,
          "data-action-operation-panel": "",
          role: "presentation",
          onClick: _cache[3] || (_cache[3] = _withModifiers($event => (requestCancel('overlay')), ["self"]))
        }), [
          _createElementVNode$1("section", {
            ref_key: "dialogRef",
            ref: dialogRef,
            class: "aoa-action-operation-panel",
            role: "dialog",
            "aria-modal": "true",
            "aria-labelledby": dialogId.value,
            "aria-describedby": dialogDescriptionIds.value,
            "aria-busy": isRunning.value ? 'true' : 'false',
            "data-operation-state": panelState.value,
            tabindex: "-1",
            onKeydown: handleDialogKeydown
          }, [
            _createElementVNode$1("header", _hoisted_3$1, [
              _createElementVNode$1("div", null, [
                (__props.kicker)
                  ? (_openBlock$1(), _createElementBlock$1("span", _hoisted_4$1, _toDisplayString$1(__props.kicker), 1))
                  : _createCommentVNode$1("", true),
                _createElementVNode$1("h2", { id: dialogId.value }, _toDisplayString$1(dialogTitle.value), 9, _hoisted_5$1)
              ]),
              _createElementVNode$1("button", {
                type: "button",
                class: "aoa-action-operation-panel__close aoa-interactive",
                "aria-label": "关闭操作面板",
                title: "关闭",
                "data-action-operation-close": "",
                disabled: isRunning.value || confirmLocked.value,
                onClick: _cache[0] || (_cache[0] = $event => (requestCancel('close')))
              }, [
                (_openBlock$1(), _createElementBlock$1("svg", _hoisted_7$1, [
                  _createElementVNode$1("path", {
                    d: _unref(mdiClose),
                    fill: "currentColor"
                  }, null, 8, _hoisted_8$1)
                ]))
              ], 8, _hoisted_6$1)
            ]),
            _createElementVNode$1("div", _hoisted_9$1, [
              _withDirectives$1(_createElementVNode$1("div", _hoisted_10$1, [
                _renderSlot(_ctx.$slots, "editing", {}, () => [
                  _renderSlot(_ctx.$slots, "default", {}, undefined, true)
                ], true)
              ], 512), [
                [_vShow, panelState.value === 'editing']
              ]),
              _withDirectives$1(_createElementVNode$1("div", _hoisted_11$1, [
                _renderSlot(_ctx.$slots, "running", {}, () => [
                  _createElementVNode$1("div", _hoisted_12$1, [
                    _cache[4] || (_cache[4] = _createElementVNode$1("span", {
                      class: "aoa-action-operation-panel__spinner",
                      "aria-hidden": "true"
                    }, null, -1)),
                    _createElementVNode$1("strong", null, _toDisplayString$1(__props.runningLabel), 1)
                  ])
                ], true)
              ], 512), [
                [_vShow, panelState.value === 'running']
              ]),
              _withDirectives$1(_createElementVNode$1("div", {
                id: resultId.value,
                class: "aoa-action-operation-panel__stage",
                "data-operation-stage": "result",
                role: resultOk.value ? 'status' : 'alert',
                "aria-live": resultOk.value ? 'polite' : 'assertive'
              }, [
                _renderSlot(_ctx.$slots, "result", {
                  result: __props.result,
                  ok: resultOk.value,
                  message: resultMessage.value,
                  detail: resultDetail.value
                }, () => [
                  _createElementVNode$1("div", {
                    class: "aoa-action-operation-panel__result",
                    "data-tone": resultOk.value ? 'success' : 'error'
                  }, [
                    _createElementVNode$1("strong", null, _toDisplayString$1(resultMessage.value), 1),
                    (resultDetail.value)
                      ? (_openBlock$1(), _createElementBlock$1("span", _hoisted_15$1, _toDisplayString$1(resultDetail.value), 1))
                      : _createCommentVNode$1("", true)
                  ], 8, _hoisted_14$1)
                ], true)
              ], 8, _hoisted_13$1), [
                [_vShow, panelState.value === 'result']
              ])
            ]),
            _createElementVNode$1("footer", _hoisted_16$1, [
              (panelState.value === 'editing')
                ? (_openBlock$1(), _createElementBlock$1("button", _mergeProps({ key: 0 }, __props.cancelAttrs, {
                    type: "button",
                    class: "aoa-action-operation-panel__button aoa-action-operation-panel__button--ghost aoa-button aoa-interactive",
                    "data-action-operation-cancel": "",
                    disabled: confirmLocked.value,
                    onClick: _cache[1] || (_cache[1] = $event => (requestCancel('cancel')))
                  }), _toDisplayString$1(__props.cancelLabel), 17, _hoisted_17$1))
                : _createCommentVNode$1("", true),
              (panelState.value === 'editing')
                ? (_openBlock$1(), _createElementBlock$1("button", _mergeProps({ key: 1 }, __props.confirmAttrs, {
                    type: "button",
                    class: ["aoa-action-operation-panel__button aoa-action-operation-panel__button--confirm aoa-button aoa-interactive", { 'aoa-action-operation-panel__button--danger': __props.danger }],
                    "data-action-operation-confirm": "",
                    disabled: confirmButtonDisabled.value,
                    "aria-busy": confirmLocked.value ? 'true' : 'false',
                    onClick: requestConfirm
                  }), [
                    (__props.confirmIconPath)
                      ? (_openBlock$1(), _createElementBlock$1("svg", _hoisted_19$1, [
                          _createElementVNode$1("path", {
                            d: __props.confirmIconPath,
                            fill: "currentColor"
                          }, null, 8, _hoisted_20$1)
                        ]))
                      : _createCommentVNode$1("", true),
                    _createElementVNode$1("span", null, _toDisplayString$1(__props.confirmLabel), 1)
                  ], 16, _hoisted_18$1))
                : (panelState.value === 'running')
                  ? (_openBlock$1(), _createElementBlock$1("button", _hoisted_21$1, _toDisplayString$1(__props.runningLabel), 1))
                  : (_openBlock$1(), _createElementBlock$1("button", {
                      key: 3,
                      type: "button",
                      class: "aoa-action-operation-panel__button aoa-action-operation-panel__button--confirm aoa-button aoa-interactive",
                      "data-action-operation-close-result": "",
                      onClick: _cache[2] || (_cache[2] = $event => (requestCancel('result-close')))
                    }, _toDisplayString$1(__props.closeLabel), 1))
            ])
          ], 40, _hoisted_2$1)
        ], 16, _hoisted_1$1))
      : _createCommentVNode$1("", true)
  ]))
}
}

});
const ActionOperationPanel = /*#__PURE__*/_export_sfc(_sfc_main$1, [['__scopeId',"data-v-f7cef3a7"]]);

const {createElementVNode:_createElementVNode,renderList:_renderList,Fragment:_Fragment,openBlock:_openBlock,createElementBlock:_createElementBlock,toDisplayString:_toDisplayString,vModelText:_vModelText,withDirectives:_withDirectives,createCommentVNode:_createCommentVNode,createTextVNode:_createTextVNode} = await importShared('vue');


const _hoisted_1 = {
  class: "aoa-backup-restore-operation",
  "data-backup-restore-operation": ""
};
const _hoisted_2 = { class: "aoa-backup-restore-operation__grid" };
const _hoisted_3 = ["value", "disabled"];
const _hoisted_4 = ["value"];
const _hoisted_5 = {
  key: 1,
  class: "aoa-backup-restore-operation__file"
};
const _hoisted_6 = ["disabled"];
const _hoisted_7 = { class: "aoa-backup-restore-operation__archive" };
const _hoisted_8 = ["value", "disabled"];
const _hoisted_9 = ["value"];
const _hoisted_10 = { class: "aoa-backup-restore-operation__tools" };
const _hoisted_11 = ["disabled"];
const _hoisted_12 = ["disabled"];
const _hoisted_13 = {
  key: 0,
  class: "aoa-backup-restore-operation__selection",
  "data-backup-restore-selection": ""
};
const _hoisted_14 = { class: "aoa-backup-restore-operation__archive-meta" };
const _hoisted_15 = ["checked"];
const _hoisted_16 = ["checked"];
const _hoisted_17 = { key: 0 };
const _hoisted_18 = ["value"];
const _hoisted_19 = ["value"];
const _hoisted_20 = {
  key: 1,
  class: "aoa-backup-restore-operation__plugin-picker",
  "data-backup-restore-plugin-picker": ""
};
const _hoisted_21 = { class: "aoa-backup-restore-operation__plugin-picker-head" };
const _hoisted_22 = { class: "aoa-backup-restore-operation__plugin-count" };
const _hoisted_23 = { class: "aoa-backup-restore-operation__plugin-tools" };
const _hoisted_24 = ["disabled"];
const _hoisted_25 = ["disabled"];
const _hoisted_26 = {
  key: 0,
  class: "aoa-backup-restore-operation__plugin-list",
  role: "group",
  "aria-label": "选择要处理的插件"
};
const _hoisted_27 = ["value", "checked", "onChange"];
const _hoisted_28 = {
  key: 1,
  class: "aoa-backup-restore-operation__plugin-empty",
  role: "status"
};
const _hoisted_29 = ["disabled"];
const _hoisted_30 = {
  key: 1,
  class: "aoa-backup-restore-operation__message",
  role: "alert"
};

const {computed} = await importShared('vue');



const _sfc_main = {
  __name: 'BackupRestoreOperationContent',
  props: {
  workflow: { type: Object, required: true },
},
  setup(__props) {

const props = __props;

const state = computed(() => props.workflow.state || {});
const loading = computed(() => props.workflow.loading || {});
const pluginOptions = computed(() => props.workflow.pluginOptions?.value || props.workflow.pluginOptions || []);
const scopeNeedsPlugins = computed(() => props.workflow.scopeNeedsPlugins?.value ?? props.workflow.scopeNeedsPlugins ?? false);
const busy = computed(() => Boolean(props.workflow.busy?.value ?? props.workflow.busy ?? false));
const selectedPluginCount = computed(() => Array.isArray(state.value.pluginIds) ? state.value.pluginIds.length : 0);
const pluginOptionCount = computed(() => pluginOptions.value.length);

function sourceChanged(event) {
  props.workflow.changeSource?.(event.target.value);
}

function archiveChanged(event) {
  state.value.archiveName = event.target.value;
  state.value.inspection = null;
}

function componentChanged(key, event) {
  state.value.components[key] = event.target.checked;
}

function scopeChanged(event) {
  state.value.pluginScope = event.target.value;
  state.value.pluginIds = [];
}

function togglePlugin(pluginId, event) {
  const current = new Set(Array.isArray(state.value.pluginIds) ? state.value.pluginIds : []);
  if (event.target.checked) current.add(pluginId);
  else current.delete(pluginId);
  state.value.pluginIds = pluginOptions.value
    .map(item => item.value)
    .filter(value => current.has(value));
}

function selectAllPlugins() {
  state.value.pluginIds = pluginOptions.value.map(item => item.value);
}

function clearPlugins() {
  state.value.pluginIds = [];
}

function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(String(reader.result || '').split(',', 2).at(-1) || '');
    reader.onerror = () => reject(reader.error || new Error('读取归档失败'));
    reader.readAsDataURL(file);
  })
}

async function importSelectedFile(event) {
  const file = event.target.files?.[0];
  if (!file) return
  try {
    await props.workflow.importArchive?.(file.name, await fileToBase64(file));
  } finally {
    event.target.value = '';
  }
}

return (_ctx, _cache) => {
  return (_openBlock(), _createElementBlock("div", _hoisted_1, [
    _createElementVNode("div", _hoisted_2, [
      _createElementVNode("label", null, [
        _cache[8] || (_cache[8] = _createElementVNode("span", null, "归档来源", -1)),
        _createElementVNode("select", {
          value: state.value.source,
          disabled: busy.value,
          onChange: sourceChanged
        }, [
          (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(__props.workflow.sources || [], (source) => {
            return (_openBlock(), _createElementBlock("option", {
              key: source.value,
              value: source.value
            }, _toDisplayString(source.label), 9, _hoisted_4))
          }), 128))
        ], 40, _hoisted_3)
      ]),
      (state.value.source === 'temporary_webdav')
        ? (_openBlock(), _createElementBlock(_Fragment, { key: 0 }, [
            _createElementVNode("label", null, [
              _cache[9] || (_cache[9] = _createElementVNode("span", null, "WebDAV 地址", -1)),
              _withDirectives(_createElementVNode("input", {
                "onUpdate:modelValue": _cache[0] || (_cache[0] = $event => ((state.value.temporaryWebdav.hostname) = $event)),
                type: "url",
                autocomplete: "off"
              }, null, 512), [
                [_vModelText, state.value.temporaryWebdav.hostname]
              ])
            ]),
            _createElementVNode("label", null, [
              _cache[10] || (_cache[10] = _createElementVNode("span", null, "账号", -1)),
              _withDirectives(_createElementVNode("input", {
                "onUpdate:modelValue": _cache[1] || (_cache[1] = $event => ((state.value.temporaryWebdav.login) = $event)),
                type: "text",
                autocomplete: "off"
              }, null, 512), [
                [_vModelText, state.value.temporaryWebdav.login]
              ])
            ]),
            _createElementVNode("label", null, [
              _cache[11] || (_cache[11] = _createElementVNode("span", null, "密码", -1)),
              _withDirectives(_createElementVNode("input", {
                "onUpdate:modelValue": _cache[2] || (_cache[2] = $event => ((state.value.temporaryWebdav.password) = $event)),
                type: "password",
                autocomplete: "new-password"
              }, null, 512), [
                [_vModelText, state.value.temporaryWebdav.password]
              ])
            ])
          ], 64))
        : _createCommentVNode("", true),
      (state.value.source === 'upload')
        ? (_openBlock(), _createElementBlock("label", _hoisted_5, [
            _cache[12] || (_cache[12] = _createElementVNode("span", null, "浏览器归档", -1)),
            _createElementVNode("input", {
              type: "file",
              accept: ".zip,application/zip",
              disabled: loading.value.import,
              onChange: importSelectedFile
            }, null, 40, _hoisted_6)
          ]))
        : (_openBlock(), _createElementBlock(_Fragment, { key: 2 }, [
            _createElementVNode("label", _hoisted_7, [
              _cache[14] || (_cache[14] = _createElementVNode("span", null, "备份归档", -1)),
              _createElementVNode("select", {
                value: state.value.archiveName,
                disabled: loading.value.list || !state.value.archives.length,
                onChange: archiveChanged
              }, [
                _cache[13] || (_cache[13] = _createElementVNode("option", { value: "" }, "请选择归档", -1)),
                (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(state.value.archives, (archive) => {
                  return (_openBlock(), _createElementBlock("option", {
                    key: archive.name,
                    value: archive.name
                  }, _toDisplayString(archive.name), 9, _hoisted_9))
                }), 128))
              ], 40, _hoisted_8)
            ]),
            _createElementVNode("div", _hoisted_10, [
              _createElementVNode("button", {
                type: "button",
                disabled: loading.value.list,
                onClick: _cache[3] || (_cache[3] = $event => (__props.workflow.loadArchives?.()))
              }, _toDisplayString(loading.value.list ? '读取中…' : '读取归档'), 9, _hoisted_11),
              _createElementVNode("button", {
                type: "button",
                disabled: !state.value.archiveName || loading.value.inspect,
                onClick: _cache[4] || (_cache[4] = $event => (__props.workflow.inspectArchive?.()))
              }, _toDisplayString(loading.value.inspect ? '检查中…' : '检查归档'), 9, _hoisted_12)
            ])
          ], 64))
    ]),
    (state.value.inspection)
      ? (_openBlock(), _createElementBlock("div", _hoisted_13, [
          _createElementVNode("div", _hoisted_14, [
            _createElementVNode("strong", null, _toDisplayString(state.value.inspection.descriptor?.name), 1),
            _createElementVNode("span", null, _toDisplayString(state.value.inspection.descriptor?.created_at || ''), 1)
          ]),
          _createElementVNode("fieldset", null, [
            _cache[17] || (_cache[17] = _createElementVNode("legend", null, "在线恢复范围", -1)),
            _createElementVNode("label", null, [
              _createElementVNode("input", {
                type: "checkbox",
                checked: state.value.components.moviepilot,
                onChange: _cache[5] || (_cache[5] = $event => (componentChanged('moviepilot', $event)))
              }, null, 40, _hoisted_15),
              _cache[15] || (_cache[15] = _createTextVNode("MoviePilot 配置", -1))
            ]),
            _createElementVNode("label", null, [
              _createElementVNode("input", {
                type: "checkbox",
                checked: state.value.components.plugins,
                onChange: _cache[6] || (_cache[6] = $event => (componentChanged('plugins', $event)))
              }, null, 40, _hoisted_16),
              _cache[16] || (_cache[16] = _createTextVNode("插件状态", -1))
            ])
          ]),
          (state.value.components.plugins)
            ? (_openBlock(), _createElementBlock("label", _hoisted_17, [
                _cache[18] || (_cache[18] = _createElementVNode("span", null, "插件范围", -1)),
                _createElementVNode("select", {
                  value: state.value.pluginScope,
                  onChange: scopeChanged
                }, [
                  (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(__props.workflow.pluginScopes || [], (scope) => {
                    return (_openBlock(), _createElementBlock("option", {
                      key: scope.value,
                      value: scope.value
                    }, _toDisplayString(scope.label), 9, _hoisted_19))
                  }), 128))
                ], 40, _hoisted_18)
              ]))
            : _createCommentVNode("", true),
          (state.value.components.plugins && scopeNeedsPlugins.value)
            ? (_openBlock(), _createElementBlock("div", _hoisted_20, [
                _createElementVNode("div", _hoisted_21, [
                  _cache[19] || (_cache[19] = _createElementVNode("span", null, "插件", -1)),
                  _createElementVNode("span", _hoisted_22, "已选 " + _toDisplayString(selectedPluginCount.value) + " / " + _toDisplayString(pluginOptionCount.value), 1),
                  _createElementVNode("div", _hoisted_23, [
                    _createElementVNode("button", {
                      type: "button",
                      disabled: !pluginOptionCount.value,
                      onClick: selectAllPlugins
                    }, "全选", 8, _hoisted_24),
                    _createElementVNode("button", {
                      type: "button",
                      disabled: !selectedPluginCount.value,
                      onClick: clearPlugins
                    }, "清空", 8, _hoisted_25)
                  ])
                ]),
                (pluginOptionCount.value)
                  ? (_openBlock(), _createElementBlock("div", _hoisted_26, [
                      (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(pluginOptions.value, (plugin) => {
                        return (_openBlock(), _createElementBlock("label", {
                          key: plugin.value,
                          class: "aoa-backup-restore-operation__plugin-option"
                        }, [
                          _createElementVNode("input", {
                            type: "checkbox",
                            value: plugin.value,
                            checked: state.value.pluginIds.includes(plugin.value),
                            onChange: $event => (togglePlugin(plugin.value, $event))
                          }, null, 40, _hoisted_27),
                          _createElementVNode("span", null, _toDisplayString(plugin.label), 1)
                        ]))
                      }), 128))
                    ]))
                  : (_openBlock(), _createElementBlock("p", _hoisted_28, "此归档没有可选择的插件。"))
              ]))
            : _createCommentVNode("", true),
          _createElementVNode("button", {
            type: "button",
            class: "aoa-backup-restore-operation__download",
            disabled: loading.value.download,
            onClick: _cache[7] || (_cache[7] = $event => (__props.workflow.downloadArchive?.()))
          }, _toDisplayString(loading.value.download ? '准备下载…' : '下载完整归档'), 9, _hoisted_29),
          _cache[20] || (_cache[20] = _createElementVNode("p", { class: "aoa-backup-restore-operation__sensitive" }, "归档未加密，包含敏感离线恢复材料。", -1))
        ]))
      : _createCommentVNode("", true),
    (state.value.message)
      ? (_openBlock(), _createElementBlock("p", _hoisted_30, _toDisplayString(state.value.message), 1))
      : _createCommentVNode("", true)
  ]))
}
}

};
const BackupRestoreOperationContent = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-074fff7c"]]);

export { ACTION_OPERATION_MODE as A, BackupRestoreOperationContent as B, DEFAULT_PLUGIN_API_TIMEOUT_MS as D, getActionForSurface as a, useBackupRestore as b, useConfigActionRunner as c, getActionsForSurface as d, ActionOperationPanel as e, actionRefreshes as f, getPluginApi as g, getPluginApiEnvelope as h, createV31QuickActions as i, useActionRunner as j, resolveActionAvailability as k, actionGroupRegistry as l, ACTION_DISABLED_REASON as m, resolvePluginApi as r, useAgentOpsTheme as u, withTimeout as w };
