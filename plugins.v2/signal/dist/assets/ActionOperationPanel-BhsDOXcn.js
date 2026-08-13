import { importShared } from './__federation_fn_import-JrT3xvdd.js';
import { a1 as useTheme, am as _export_sfc, bI as mdiClose, c4 as mdiAlertOutline } from './mdi-DNDHBjvE.js';

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
    presentations: { config: { label: '立即统计', icon: 'mdi-chart-line' } },
  }),
  defineAction('run_backup', {
    key: 'backup', component: 'backup', groupId: 'system_maintenance',
    label: '配置备份', desc: '执行自动备份', icon: 'mdi-database-arrow-up-outline', iconKey: 'database', tone: 'violet',
    presentations: { config: { label: '立即备份', icon: 'mdi-archive-arrow-up-outline' } },
  }),
  defineAction('run_log_clean', {
    key: 'log_clean', component: 'log_clean', groupId: 'system_maintenance',
    label: '日志清理', desc: '按保留行数截断日志', icon: 'mdi-broom', iconKey: 'broom', tone: 'violet',
    presentations: { config: { label: '立即清理' } },
  }),
  defineAction('run_health_check', {
    key: 'health', component: 'health_check', groupId: 'system_maintenance',
    label: '健康巡查', desc: '检查关键状态', icon: 'mdi-heart-pulse', iconKey: 'heartPulse', tone: 'green',
    presentations: { config: { label: '立即巡检', icon: 'mdi-heart-pulse-solid' } },
  }),
  defineAction('run_mp_update', {
    key: 'mp_update', component: 'mp_update', groupId: 'system_maintenance',
    label: 'MP 更新', desc: '检查主程序更新', icon: 'mdi-update', iconKey: 'refresh', tone: 'amber',
    presentations: { config: { label: '立即检查并更新' } },
  }),
  defineAction('run_market_update', {
    key: 'plugin_market_sync', component: 'market_update', groupId: 'plugin_governance',
    label: '插件库同步', desc: '同步插件库记录', icon: 'mdi-cloud-sync-outline', iconKey: 'cloudUpload', tone: 'amber',
    presentations: { config: { label: '立即同步插件库', icon: 'mdi-database-sync-outline' } },
  }),
  defineAction('run_plugin_update_reminder', {
    key: 'plugin_update_reminder', component: 'plugin_update_reminder', groupId: 'plugin_governance',
    label: '插件更新', desc: '检查已安装插件更新', icon: 'mdi-bell-alert-outline', iconKey: 'bell', tone: 'amber',
    presentations: { config: { label: '立即检查并更新插件', icon: 'mdi-puzzle-check-outline' } },
  }),
  defineAction('create_tg_console_card', {
    key: 'fusion_build', component: 'fusion_notify', groupId: 'fusion',
    taskKey: '',
    label: '立即建卡', desc: '创建融合汇报卡', icon: 'mdi-card-plus-outline', iconKey: 'cardPlus', tone: 'blue',
    presentations: {
      config: { icon: 'mdi-plus-circle-outline' },
      dashboardFusion: { label: '建卡' },
    },
  }),
  defineAction('run_daily_report', {
    key: 'fusion_refresh', component: 'daily_report', groupId: 'fusion',
    availabilityComponent: 'fusion_notify', taskKey: '',
    label: '立即刷新', desc: '刷新融合汇报', icon: 'mdi-refresh', iconKey: 'refresh', tone: 'blue',
    presentations: {
      config: { icon: 'mdi-sync' },
      dashboardFusion: { label: '刷新融合卡' },
    },
  }),
  defineAction('run_seed_clean', {
    key: 'seed_clean', component: 'seedclean', groupId: 'site_downloaders',
    taskKey: 'seed_clean',
    operationMode: ACTION_OPERATION_MODE.confirm, operationDanger: true,
    parameters: [
      { key: 'seedclean_confirm', value: true, type: 'boolean' },
    ],
    label: '自动删种', desc: '按当前规则处理匹配种子', icon: 'mdi-play', tone: 'red',
    presentations: {
      config: { label: '执行自动删种' },
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
      { key: 'plugin_uninstall_confirm', value: true, type: 'boolean' },
    ],
    label: '插件卸载', desc: '卸载选中的插件并执行所选清理项', icon: 'mdi-alert-outline', tone: 'red',
    presentations: {
      config: { label: '执行卸载' },
      dashboard: { iconKey: 'trash' },
      mpWidget: { iconKey: 'trash' },
    },
  }),
];

const actionRegistry = freeze(Object.fromEntries(
  actionDefinitions.map(action => [action.id, action]),
));

const manualActionPaths = freeze(actionDefinitions.map(action => action.id));

const quickActionPaths = freeze([
  'run_subscribe_reminder',
  'run_today_transfer',
  'run_site_stat',
  'run_backup',
  'run_health_check',
]);

const fusionCardActionPaths = freeze([
  'create_tg_console_card',
  'run_daily_report',
]);

const configActionPaths = freeze([
  'create_tg_console_card',
  'run_daily_report',
  'run_subscribe_reminder',
  'run_site_stat',
  'run_health_check',
  'run_seed_clean',
  'run_downloader_helper',
  'subfill_clear_history',
  'subfill_clear_handled',
  'run_backup',
  'run_log_clean',
  'run_mp_update',
  'run_plugin_update_reminder',
  'run_market_update',
  'run_plugin_uninstall',
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
    parameters: registered.parameters,
    operation: registered.operation,
  }
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

const {computed: computed$2,reactive,ref: ref$1} = await importShared('vue');

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
    messageTimeoutMs = 5000,
  } = options;
  const runningActions = reactive(new Map());
  const inFlight = new Map();
  const actionMessage = ref$1('');
  const actionOk = ref$1(true);
  let clearTimer = 0;

  const runningActionIds = computed$2(() => Array.from(runningActions.keys()));
  const runningActionLabels = computed$2(() => Array.from(runningActions.values()).map(item => item.label));
  const actionRunning = computed$2(() => runningActionIds.value[0] || '');
  const runningActionLabel = computed$2(() => runningActions.get(actionRunning.value)?.label || '');

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
    return Boolean(id && inFlight.has(id))
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
  const notificationLockedByFusion = computed$2(() => !!form.fusion_notify_enabled);
  const downloaderHelperPreview = ref$1(null);
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
    return {
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
      if (current.id === 'run_plugin_uninstall') await refreshAfterPluginUninstall(res);
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
  });

  function executeConfigAction(path, label = '') {
    return runner.runAction(configAction(path, label))
  }

  return {
    action,
    notificationLockedByFusion,
    getActionAvailability,
    actionDisabledMessage,
    isActionRunning: runner.isActionRunning,
    runningActionIds: runner.runningActionIds,
    runAction: executeConfigAction,
  }
}

const {computed: computed$1} = await importShared('vue');

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
  const themeName = computed$1(() => normalizeThemeName(vuetifyTheme.global.name.value));
  const rootThemeClass = computed$1(() => `agentops-theme--${themeName.value}`);

  return { themeName, rootThemeClass }
}

const {toDisplayString:_toDisplayString,openBlock:_openBlock,createElementBlock:_createElementBlock,createCommentVNode:_createCommentVNode,createElementVNode:_createElementVNode,unref:_unref,normalizeClass:_normalizeClass,renderList:_renderList,Fragment:_Fragment,mergeProps:_mergeProps,vModelText:_vModelText,withDirectives:_withDirectives,withModifiers:_withModifiers,Teleport:_Teleport,createBlock:_createBlock} = await importShared('vue');


const _hoisted_1 = ["data-action-id", "data-action-mode"];
const _hoisted_2 = ["aria-labelledby", "aria-describedby", "aria-busy"];
const _hoisted_3 = { class: "aoa-action-operation-panel__head" };
const _hoisted_4 = {
  key: 0,
  class: "aoa-action-operation-panel__kicker"
};
const _hoisted_5 = ["id"];
const _hoisted_6 = ["disabled"];
const _hoisted_7 = {
  viewBox: "0 0 24 24",
  width: "18",
  height: "18",
  "aria-hidden": "true"
};
const _hoisted_8 = ["d"];
const _hoisted_9 = ["id", "data-tone"];
const _hoisted_10 = {
  viewBox: "0 0 24 24",
  width: "19",
  height: "19",
  "aria-hidden": "true"
};
const _hoisted_11 = ["d"];
const _hoisted_12 = ["id"];
const _hoisted_13 = { key: 0 };
const _hoisted_14 = { key: 1 };
const _hoisted_15 = {
  key: 2,
  class: "aoa-action-operation-panel__fields",
  "data-action-operation-fields": ""
};
const _hoisted_16 = ["id", "aria-describedby", "checked", "disabled", "onChange"];
const _hoisted_17 = ["id", "aria-describedby", "value", "placeholder", "required", "disabled", "onInput"];
const _hoisted_18 = ["id", "aria-describedby", "value", "multiple", "required", "disabled", "onChange"];
const _hoisted_19 = ["value"];
const _hoisted_20 = ["id", "aria-describedby", "type", "value", "placeholder", "required", "disabled", "onInput"];
const _hoisted_21 = ["id"];
const _hoisted_22 = ["data-section-kind"];
const _hoisted_23 = { key: 0 };
const _hoisted_24 = { key: 0 };
const _hoisted_25 = { key: 1 };
const _hoisted_26 = {
  key: 0,
  class: "aoa-action-operation-panel__empty"
};
const _hoisted_27 = {
  key: 3,
  class: "aoa-action-operation-panel__confirmation"
};
const _hoisted_28 = ["id", "placeholder", "autocomplete", "aria-describedby", "disabled"];
const _hoisted_29 = ["id"];
const _hoisted_30 = { class: "aoa-action-operation-panel__actions" };
const _hoisted_31 = ["disabled"];
const _hoisted_32 = ["disabled", "aria-busy"];
const _hoisted_33 = {
  key: 0,
  viewBox: "0 0 24 24",
  width: "15",
  height: "15",
  "aria-hidden": "true"
};
const _hoisted_34 = ["d"];

const {computed,nextTick,onBeforeUnmount,onMounted,ref,useAttrs,watch} = await importShared('vue');


const _sfc_main = /*@__PURE__*/Object.assign({ inheritAttrs: false }, {
  __name: 'ActionOperationPanel',
  props: {
  open: { type: Boolean, default: false },
  action: { type: Object, default: () => ({}) },
  title: { type: String, default: '' },
  kicker: { type: String, default: '' },
  warning: { type: String, default: '' },
  danger: { type: Boolean, default: false },
  summaryPrimary: { type: String, default: '' },
  summarySecondary: { type: String, default: '' },
  sections: { type: Array, default: () => [] },
  fields: { type: Array, default: () => [] },
  confirmationInput: { type: Object, default: null },
  confirmLabel: { type: String, default: '确认执行' },
  cancelLabel: { type: String, default: '取消' },
  confirmIconPath: { type: String, default: '' },
  busy: { type: Boolean, default: false },
  returnFocusSelector: { type: String, default: '' },
  themeClass: { type: [String, Array, Object], default: '' },
  portalStyle: { type: Object, default: () => ({}) },
  rootAttrs: { type: Object, default: () => ({}) },
  confirmAttrs: { type: Object, default: () => ({}) },
  cancelAttrs: { type: Object, default: () => ({}) },
},
  emits: ['cancel', 'confirm', 'update:field'],
  setup(__props, { emit: __emit }) {



const props = __props;

const emit = __emit;
const attrs = useAttrs();
const dialogRef = ref(null);
const confirmationValue = ref('');
const confirmLocked = ref(false);
let previousFocus = null;

const actionId = computed(() => String(props.action?.id || props.action?.path || 'action'));
const actionMode = computed(() => String(props.action?.operation?.mode || 'confirm'));
const overlayAttrs = computed(() => ({ ...attrs, ...props.rootAttrs }));
const dialogTitle = computed(() => props.title || props.action?.label || '确认操作');
const dialogId = computed(() => `aoa-action-operation-${actionId.value.replace(/[^a-zA-Z0-9_-]/g, '-')}`);
const warningId = computed(() => `${dialogId.value}-warning`);
const summaryId = computed(() => `${dialogId.value}-summary`);
const confirmationHintId = computed(() => `${dialogId.value}-confirmation-hint`);
const dialogDescriptionIds = computed(() => [
  props.warning ? warningId.value : '',
  props.summaryPrimary || props.summarySecondary ? summaryId.value : '',
].filter(Boolean).join(' ') || undefined);
const expectedConfirmation = computed(() => String(props.confirmationInput?.expectedValue || ''));
const confirmationReady = computed(() => {
  if (!props.confirmationInput) return true
  const current = props.confirmationInput.caseSensitive === false
    ? confirmationValue.value.toLocaleLowerCase()
    : confirmationValue.value;
  const expected = props.confirmationInput.caseSensitive === false
    ? expectedConfirmation.value.toLocaleLowerCase()
    : expectedConfirmation.value;
  return current === expected
});
const confirmDisabled = computed(() => props.busy || confirmLocked.value || !confirmationReady.value);

function fieldValue(field) {
  return field?.value ?? field?.modelValue ?? (field?.multiple ? [] : '')
}

function optionValue(option) {
  return option && typeof option === 'object' ? (option.value ?? option.id ?? option.key ?? '') : option
}

function optionLabel(option) {
  return option && typeof option === 'object' ? (option.label ?? option.title ?? option.name ?? optionValue(option)) : option
}

function updateField(field, event) {
  let value;
  if (field.type === 'checkbox') value = event.target.checked;
  else if (field.multiple) value = Array.from(event.target.selectedOptions || []).map(option => option.value);
  else value = event.target.value;
  emit('update:field', { key: field.key, value });
}

function fieldControlId(field, index) {
  return String(field?.attrs?.id || `${dialogId.value}-field-${String(field?.key || index).replace(/[^a-zA-Z0-9_-]/g, '-')}`)
}

function fieldHintId(field, index) {
  return `${fieldControlId(field, index)}-hint`
}

function fieldDescribedBy(field, index) {
  return [field?.attrs?.['aria-describedby'], field?.hint ? fieldHintId(field, index) : '']
    .filter(Boolean)
    .join(' ') || undefined
}

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
  if (!props.open || props.busy || confirmLocked.value) return
  emit('cancel', { reason, action: props.action });
}

function requestConfirm() {
  if (!props.open || confirmDisabled.value) return
  confirmLocked.value = true;
  emit('confirm', {
    action: props.action,
    confirmationValue: confirmationValue.value,
  });
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
    confirmationValue.value = '';
    confirmLocked.value = false;
    focusInitialControl();
  } else {
    confirmLocked.value = false;
    confirmationValue.value = '';
    restoreFocus();
  }
});

watch(actionId, () => {
  confirmationValue.value = '';
  confirmLocked.value = false;
  if (props.open) focusInitialControl();
});

watch(() => props.busy, (busy, wasBusy) => {
  if (!busy && wasBusy && props.open) confirmLocked.value = false;
});

onMounted(() => {
  window.addEventListener('keydown', handleWindowKeydown);
  if (props.open) {
    previousFocus = document.activeElement;
    confirmationValue.value = '';
    confirmLocked.value = false;
    focusInitialControl();
  }
});
onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleWindowKeydown);
  restoreFocus();
});

return (_ctx, _cache) => {
  return (_openBlock(), _createBlock(_Teleport, { to: "body" }, [
    (__props.open)
      ? (_openBlock(), _createElementBlock("div", _mergeProps({ key: 0 }, overlayAttrs.value, {
          class: ["aoa-action-operation-overlay aoa-root", __props.themeClass],
          style: __props.portalStyle,
          "data-action-id": actionId.value,
          "data-action-mode": actionMode.value,
          "data-action-operation-panel": "",
          role: "presentation",
          onClick: _cache[3] || (_cache[3] = _withModifiers($event => (requestCancel('overlay')), ["self"]))
        }), [
          _createElementVNode("section", {
            ref_key: "dialogRef",
            ref: dialogRef,
            class: "aoa-action-operation-panel",
            role: "dialog",
            "aria-modal": "true",
            "aria-labelledby": dialogId.value,
            "aria-describedby": dialogDescriptionIds.value,
            "aria-busy": __props.busy || confirmLocked.value ? 'true' : 'false',
            tabindex: "-1",
            onKeydown: handleDialogKeydown
          }, [
            _createElementVNode("header", _hoisted_3, [
              _createElementVNode("div", null, [
                (__props.kicker)
                  ? (_openBlock(), _createElementBlock("span", _hoisted_4, _toDisplayString(__props.kicker), 1))
                  : _createCommentVNode("", true),
                _createElementVNode("h2", { id: dialogId.value }, _toDisplayString(dialogTitle.value), 9, _hoisted_5)
              ]),
              _createElementVNode("button", {
                type: "button",
                class: "aoa-action-operation-panel__close aoa-interactive",
                "aria-label": "关闭操作面板",
                title: "关闭",
                "data-action-operation-close": "",
                disabled: __props.busy || confirmLocked.value,
                onClick: _cache[0] || (_cache[0] = $event => (requestCancel('close')))
              }, [
                (_openBlock(), _createElementBlock("svg", _hoisted_7, [
                  _createElementVNode("path", {
                    d: _unref(mdiClose),
                    fill: "currentColor"
                  }, null, 8, _hoisted_8)
                ]))
              ], 8, _hoisted_6)
            ]),
            (__props.warning)
              ? (_openBlock(), _createElementBlock("div", {
                  key: 0,
                  id: warningId.value,
                  class: _normalizeClass(["aoa-action-operation-panel__warning", { 'aoa-action-operation-panel__warning--danger': __props.danger }]),
                  "data-tone": __props.danger ? 'danger' : 'warning'
                }, [
                  (_openBlock(), _createElementBlock("svg", _hoisted_10, [
                    _createElementVNode("path", {
                      d: _unref(mdiAlertOutline),
                      fill: "currentColor"
                    }, null, 8, _hoisted_11)
                  ])),
                  _createElementVNode("span", null, _toDisplayString(__props.warning), 1)
                ], 10, _hoisted_9))
              : _createCommentVNode("", true),
            (__props.summaryPrimary || __props.summarySecondary)
              ? (_openBlock(), _createElementBlock("div", {
                  key: 1,
                  id: summaryId.value,
                  class: "aoa-action-operation-panel__summary"
                }, [
                  (__props.summaryPrimary)
                    ? (_openBlock(), _createElementBlock("strong", _hoisted_13, _toDisplayString(__props.summaryPrimary), 1))
                    : _createCommentVNode("", true),
                  (__props.summarySecondary)
                    ? (_openBlock(), _createElementBlock("span", _hoisted_14, _toDisplayString(__props.summarySecondary), 1))
                    : _createCommentVNode("", true)
                ], 8, _hoisted_12))
              : _createCommentVNode("", true),
            (__props.fields.length)
              ? (_openBlock(), _createElementBlock("div", _hoisted_15, [
                  (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(__props.fields, (field, fieldIndex) => {
                    return (_openBlock(), _createElementBlock("label", {
                      key: field.key,
                      class: "aoa-action-operation-panel__field"
                    }, [
                      _createElementVNode("span", null, _toDisplayString(field.label), 1),
                      (field.type === 'checkbox')
                        ? (_openBlock(), _createElementBlock("input", _mergeProps({
                            key: 0,
                            ref_for: true
                          }, field.attrs || {}, {
                            id: fieldControlId(field, fieldIndex),
                            "aria-describedby": fieldDescribedBy(field, fieldIndex),
                            type: "checkbox",
                            checked: Boolean(fieldValue(field)),
                            disabled: __props.busy || confirmLocked.value || field.disabled,
                            onChange: $event => (updateField(field, $event))
                          }), null, 16, _hoisted_16))
                        : (field.type === 'textarea')
                          ? (_openBlock(), _createElementBlock("textarea", _mergeProps({
                              key: 1,
                              ref_for: true
                            }, field.attrs || {}, {
                              id: fieldControlId(field, fieldIndex),
                              "aria-describedby": fieldDescribedBy(field, fieldIndex),
                              value: fieldValue(field),
                              placeholder: field.placeholder || '',
                              required: field.required,
                              disabled: __props.busy || confirmLocked.value || field.disabled,
                              onInput: $event => (updateField(field, $event))
                            }), null, 16, _hoisted_17))
                          : (field.type === 'select')
                            ? (_openBlock(), _createElementBlock("select", _mergeProps({
                                key: 2,
                                ref_for: true
                              }, field.attrs || {}, {
                                id: fieldControlId(field, fieldIndex),
                                "aria-describedby": fieldDescribedBy(field, fieldIndex),
                                value: fieldValue(field),
                                multiple: field.multiple,
                                required: field.required,
                                disabled: __props.busy || confirmLocked.value || field.disabled,
                                onChange: $event => (updateField(field, $event))
                              }), [
                                (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(field.options || [], (option) => {
                                  return (_openBlock(), _createElementBlock("option", {
                                    key: String(optionValue(option)),
                                    value: optionValue(option)
                                  }, _toDisplayString(optionLabel(option)), 9, _hoisted_19))
                                }), 128))
                              ], 16, _hoisted_18))
                            : (_openBlock(), _createElementBlock("input", _mergeProps({
                                key: 3,
                                ref_for: true
                              }, field.attrs || {}, {
                                id: fieldControlId(field, fieldIndex),
                                "aria-describedby": fieldDescribedBy(field, fieldIndex),
                                type: field.type || 'text',
                                value: fieldValue(field),
                                placeholder: field.placeholder || '',
                                required: field.required,
                                disabled: __props.busy || confirmLocked.value || field.disabled,
                                onInput: $event => (updateField(field, $event))
                              }), null, 16, _hoisted_20)),
                      (field.hint)
                        ? (_openBlock(), _createElementBlock("small", {
                            key: 4,
                            id: fieldHintId(field, fieldIndex)
                          }, _toDisplayString(field.hint), 9, _hoisted_21))
                        : _createCommentVNode("", true)
                    ]))
                  }), 128))
                ]))
              : _createCommentVNode("", true),
            (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(__props.sections, (section) => {
              return (_openBlock(), _createElementBlock("section", {
                key: section.key,
                class: "aoa-action-operation-panel__section",
                "data-section-kind": section.kind || 'summary'
              }, [
                (section.label)
                  ? (_openBlock(), _createElementBlock("h3", _hoisted_23, _toDisplayString(section.label), 1))
                  : _createCommentVNode("", true),
                _createElementVNode("div", _mergeProps({ ref_for: true }, section.attrs || {}, { class: "aoa-action-operation-panel__items" }), [
                  (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(section.items || [], (item) => {
                    return (_openBlock(), _createElementBlock("div", {
                      key: item.key,
                      class: "aoa-action-operation-panel__item"
                    }, [
                      _createElementVNode("strong", null, _toDisplayString(item.title), 1),
                      (item.meta)
                        ? (_openBlock(), _createElementBlock("span", _hoisted_24, _toDisplayString(item.meta), 1))
                        : _createCommentVNode("", true),
                      (item.detail)
                        ? (_openBlock(), _createElementBlock("small", _hoisted_25, _toDisplayString(item.detail), 1))
                        : _createCommentVNode("", true)
                    ]))
                  }), 128)),
                  (!(section.items || []).length && section.emptyText)
                    ? (_openBlock(), _createElementBlock("p", _hoisted_26, _toDisplayString(section.emptyText), 1))
                    : _createCommentVNode("", true)
                ], 16)
              ], 8, _hoisted_22))
            }), 128)),
            (__props.confirmationInput)
              ? (_openBlock(), _createElementBlock("label", _hoisted_27, [
                  _createElementVNode("span", null, _toDisplayString(__props.confirmationInput.label || '二次确认'), 1),
                  _withDirectives(_createElementVNode("input", {
                    "onUpdate:modelValue": _cache[1] || (_cache[1] = $event => ((confirmationValue).value = $event)),
                    id: `${dialogId.value}-confirmation-input`,
                    type: "text",
                    placeholder: __props.confirmationInput.placeholder || expectedConfirmation.value,
                    autocomplete: __props.confirmationInput.autocomplete || 'off',
                    "aria-describedby": __props.confirmationInput.hint ? confirmationHintId.value : undefined,
                    disabled: __props.busy || confirmLocked.value,
                    "data-action-operation-confirmation-input": ""
                  }, null, 8, _hoisted_28), [
                    [_vModelText, confirmationValue.value]
                  ]),
                  (__props.confirmationInput.hint)
                    ? (_openBlock(), _createElementBlock("small", {
                        key: 0,
                        id: confirmationHintId.value
                      }, _toDisplayString(__props.confirmationInput.hint), 9, _hoisted_29))
                    : _createCommentVNode("", true)
                ]))
              : _createCommentVNode("", true),
            _createElementVNode("footer", _hoisted_30, [
              _createElementVNode("button", _mergeProps(__props.cancelAttrs, {
                type: "button",
                class: "aoa-action-operation-panel__button aoa-action-operation-panel__button--ghost aoa-button aoa-interactive",
                "data-action-operation-cancel": "",
                disabled: __props.busy || confirmLocked.value,
                onClick: _cache[2] || (_cache[2] = $event => (requestCancel('cancel')))
              }), _toDisplayString(__props.cancelLabel), 17, _hoisted_31),
              _createElementVNode("button", _mergeProps(__props.confirmAttrs, {
                type: "button",
                class: ["aoa-action-operation-panel__button aoa-action-operation-panel__button--confirm aoa-button aoa-interactive", { 'aoa-action-operation-panel__button--danger': __props.danger }],
                "data-action-operation-confirm": "",
                disabled: confirmDisabled.value,
                "aria-busy": __props.busy || confirmLocked.value ? 'true' : 'false',
                onClick: requestConfirm
              }), [
                (__props.confirmIconPath)
                  ? (_openBlock(), _createElementBlock("svg", _hoisted_33, [
                      _createElementVNode("path", {
                        d: __props.confirmIconPath,
                        fill: "currentColor"
                      }, null, 8, _hoisted_34)
                    ]))
                  : _createCommentVNode("", true),
                _createElementVNode("span", null, _toDisplayString(__props.confirmLabel), 1)
              ], 16, _hoisted_32)
            ])
          ], 40, _hoisted_2)
        ], 16, _hoisted_1))
      : _createCommentVNode("", true)
  ]))
}
}

});
const ActionOperationPanel = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-b57fe838"]]);

export { ACTION_OPERATION_MODE as A, getActionForSurface as a, useConfigActionRunner as b, createPluginWorkflowClient as c, getActionsForSurface as d, ActionOperationPanel as e, getPluginApiEnvelope as f, getPluginApi as g, createV31QuickActions as h, useActionRunner as i, resolveActionAvailability as j, actionGroupRegistry as k, ACTION_DISABLED_REASON as l, resolvePluginApi as r, useAgentOpsTheme as u };
