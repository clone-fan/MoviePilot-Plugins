import { importShared } from './__federation_fn_import-JrT3xvdd.js';
import { f as getPluginApiEnvelope, h as createV31QuickActions, i as useActionRunner, j as resolveActionAvailability, A as ACTION_OPERATION_MODE, k as actionGroupRegistry, l as ACTION_DISABLED_REASON, u as useAgentOpsTheme, a as getActionForSurface, e as ActionOperationPanel } from './ActionOperationPanel-Bu1ZK3Qk.js';
import { ca as mdiYinYang, ar as mdiViewDashboardOutline, cb as mdiTrashCanOutline, cc as mdiTagMultiple, cd as mdiRss, aP as mdiRefresh, ce as mdiLeaf, ba as mdiHeartPulse, cf as mdiEye, cg as mdiDatabase, ch as mdiCog, bD as mdiCloudUploadOutline, ci as mdiCheckCircle, bN as mdiChartPie, bR as mdiCardPlusOutline, bS as mdiCardAccountDetailsOutline, cj as mdiCalendarToday, ck as mdiCalendarCheck, bU as mdiBroom, bX as mdiBellOutline, cl as mdiArrowUp, cm as mdiArrowDown, am as _export_sfc } from './mdi-DveizHBi.js';

// 共享格式化工具 — 跨组件复用，禁止在各 vue 里各写一份
/** 将字节数格式化为人类可读的 GB/MB 字符串 */
function formatGB(bytes) {
  const n = Number(bytes) || 0;
  const gb = n / (1024 ** 3);
  if (gb >= 1) return gb.toFixed(2) + ' GB'
  return (n / (1024 ** 2)).toFixed(1) + ' MB'
}

/** 计算站点流量占比百分比字符串 */
function sitePercent(value, total) {
  const t = Number(total) || 0;
  if (!t) return '0%'
  return `${Math.round(((Number(value) || 0) / t) * 100)}%`
}

/** 站点饼图配色（CSS 变量版，自动适配 MP 主题） */
const sitePieColors = [
  { color: 'rgba(var(--aoa-color-success-rgb), 0.94)', glow: 'rgba(var(--aoa-color-success-rgb), 0.28)' },
  { color: 'rgba(var(--aoa-color-info-rgb), 0.90)', glow: 'rgba(var(--aoa-color-info-rgb), 0.26)' },
  { color: 'rgba(var(--aoa-color-warning-rgb), 0.88)', glow: 'rgba(var(--aoa-color-warning-rgb), 0.24)' },
  { color: 'rgba(var(--aoa-color-primary-rgb), 0.88)', glow: 'rgba(var(--aoa-color-primary-rgb), 0.24)' },
  { color: 'rgba(var(--aoa-color-error-rgb), 0.84)', glow: 'rgba(var(--aoa-color-error-rgb), 0.22)' },
  { color: 'rgba(var(--aoa-color-accent-rgb), 0.86)', glow: 'rgba(var(--aoa-color-accent-rgb), 0.23)' },
  { color: 'color-mix(in srgb, rgb(var(--aoa-color-success-rgb)) 62%, rgb(var(--aoa-color-primary-rgb)))', glow: 'rgba(var(--aoa-color-success-rgb), 0.20)' },
  { color: 'color-mix(in srgb, rgb(var(--aoa-color-warning-rgb)) 68%, rgb(var(--aoa-color-info-rgb)))', glow: 'rgba(var(--aoa-color-warning-rgb), 0.20)' },
];

const {reactive: reactive$2,computed: computed$f} = await importShared('vue');

// 站点统计图表状态 — 跨 Dashboard.vue / Page.vue 共享，禁止各 vue 里各写一份
// 入参：api(MP 插件 API 句柄)
function useSiteChart(api) {
  const siteChart = reactive$2({
    date: '',
    basis: 'idle',
    sites: [],
    upload_total: 0,
    download_total: 0,
    data_valid: false,
    message: '',
    error: '',
    last_error: '',
  });

  const siteRows = computed$f(() => [...(siteChart.sites || [])].sort((a, b) => {
    const av = (Number(a.upload) || 0) + (Number(a.download) || 0);
    const bv = (Number(b.upload) || 0) + (Number(b.download) || 0);
    return bv - av
  }));

  const siteTrafficTotal = computed$f(() => siteRows.value.reduce((sum, site) => {
    return sum + (Number(site.upload) || 0) + (Number(site.download) || 0)
  }, 0));

  const siteDateLabel = computed$f(() => {
    if (!siteChart.date) return '等待统计'
    return siteChart.basis === 'latest' ? `最近快照 ${siteChart.date}` : siteChart.date
  });

  const siteDateNote = computed$f(() => {
    if (!siteChart.date) return '等待统计'
    return siteChart.basis === 'latest' ? '最近快照' : '今天 00:00 起'
  });

  const sitePieSegments = computed$f(() => {
    const total = siteTrafficTotal.value;
    if (!total) return []
    let cursor = 0;
    return siteRows.value.map((site, index) => {
      const value = (Number(site.upload) || 0) + (Number(site.download) || 0);
      const start = cursor;
      const end = cursor + (value / total) * 100;
      cursor = end;
      const palette = sitePieColors[index % sitePieColors.length];
      return { ...site, value, start, end, color: palette.color, glow: palette.glow }
    })
  });

  const sitePieStyle = computed$f(() => {
    if (!sitePieSegments.value.length) {
      return {
        background: 'conic-gradient(rgba(var(--aoa-color-line-rgb), 0.16) 0 82deg, rgba(var(--aoa-color-line-rgb), 0.055) 82deg 360deg)',
      }
    }
    const stops = sitePieSegments.value
      .map(item => `${item.color} ${item.start.toFixed(2)}% ${item.end.toFixed(2)}%`)
      .join(', ');
    return { background: `conic-gradient(${stops})` }
  });

  const siteTableRows = computed$f(() => sitePieSegments.value.slice(0, 6));
  const hasSiteChart = computed$f(() => !!(siteChart.sites && siteChart.sites.length));

  const siteEmptyTitle = computed$f(() => {
    if (siteChart.last_error || siteChart.error) return '站点统计失败'
    if (siteChart.basis === 'skipped') return '站点统计未启用'
    if (siteChart.data_valid === true) return '暂无站点增量'
    if (siteChart.basis === 'latest') return '暂无今日增量'
    return '等待站点统计'
  });

  const siteEmptyDesc = computed$f(() => {
    if (siteChart.last_error || siteChart.error) return siteChart.last_error || siteChart.error
    if (siteChart.message) return siteChart.message
    if (siteChart.basis === 'skipped') return '启用插件和站点统计组件后，可手动刷新生成数据'
    if (siteChart.data_valid === true) return '已刷新但没有可展示的上传/下载增量'
    if (siteChart.basis === 'latest') return '今日基线不足，暂用最近快照等待下一次刷新'
    return '点击立即刷新或站点统计后显示最新可用数据'
  });

  function sitePercent$1(value) {
    return sitePercent(value, siteTrafficTotal.value)
  }

  async function loadSiteChart() {
    if (!api) return
    try {
      const res = await getPluginApiEnvelope(api, 'site_stat_chart');
      const payload = res && typeof res === 'object' && 'data' in res ? res.data : res;
      Object.assign(siteChart, {
        date: '',
        basis: 'idle',
        sites: [],
        upload_total: 0,
        download_total: 0,
        data_valid: false,
        message: '',
        error: '',
        last_error: '',
        ...(payload || {}),
        message: payload?.message || res?.msg || '',
        last_error: payload?.last_error || payload?.error || (res?.code && res?.msg ? res.msg : ''),
      });
    } catch (err) {
      Object.assign(siteChart, {
        date: '',
        basis: 'error',
        sites: [],
        upload_total: 0,
        download_total: 0,
        data_valid: false,
        message: '',
        error: err?.message || '站点统计数据加载失败',
        last_error: err?.message || '站点统计数据加载失败',
      });
    }
  }

  return {
    siteChart,
    siteRows,
    siteTrafficTotal,
    siteDateLabel,
    siteDateNote,
    sitePieSegments,
    sitePieStyle,
    siteTableRows,
    hasSiteChart,
    siteEmptyTitle,
    siteEmptyDesc,
    sitePercent: sitePercent$1,
    loadSiteChart,
  }
}

const {computed: computed$e,nextTick,ref: ref$2} = await importShared('vue');

function resolveMaybeValue(value) {
  if (typeof value === 'function') return value()
  if (value && typeof value === 'object' && Object.prototype.hasOwnProperty.call(value, 'value')) return value.value
  return value
}

function actionId(action) {
  return String(action?.id || action?.path || action?.apiPath || '')
}

async function restoreActionTriggerFocus(action) {
  if (typeof document === 'undefined') return
  await nextTick();
  const id = actionId(action);
  const escapedId = globalThis.CSS?.escape ? globalThis.CSS.escape(id) : id.replace(/["\\]/g, '\\$&');
  const target = document.querySelector(`[data-action-id="${escapedId}"]`);
  if (target?.isConnected && !target.disabled && target.getAttribute('aria-disabled') !== 'true') {
    target.focus?.({ preventScroll: true });
  }
}

function normalizeConfigModel(response) {
  const model = response?.model ?? response?.data?.model;
  return model && typeof model === 'object' && !Array.isArray(model) ? model : {}
}

function selectedValues(value) {
  return Array.isArray(value) ? value.map(item => String(item || '').trim()).filter(Boolean) : []
}

function seedCleanSpec(action, config, common) {
  const downloaders = selectedValues(config.seedclean_downloaders);
  const actionLabel = config.seedclean_action === 'pause' ? '暂停任务' : '删除任务';
  return {
    ...common,
    kicker: '请确认本次处理',
    warning: '自动删种会按配置中心当前保存的筛选条件处理匹配任务，请确认后继续。',
    summaryPrimary: `${downloaders.length} 个下载器`,
    summarySecondary: actionLabel,
    sections: [{
      key: 'seed-clean-scope',
      items: [{
        key: 'seed-clean-current-scope',
        title: downloaders.join('、') || '当前保存的下载器范围',
        meta: actionLabel,
        detail: '使用配置中心当前保存的删种筛选条件',
      }],
    }],
    confirmLabel: '确认并执行',
  }
}

function downloaderHelperSpec(action, preview, common) {
  const items = Array.isArray(preview?.items) ? preview.items : [];
  return {
    ...common,
    kicker: '一次确认',
    title: '清理失效下载任务',
    warning: '标签和恢复做种无需确认；以下失效任务将从下载器移除。',
    summaryPrimary: `${items.length} 个清理候选`,
    summarySecondary: '确认后执行本次预览范围',
    sections: [{
      key: 'downloader-helper-preview',
      label: '清理预览',
      items: items.map(item => ({
        key: `${item.downloader || 'downloader'}-${item.id || item.name || 'item'}`,
        title: item.name || item.id || '未命名任务',
        meta: item.downloader || '',
        detail: `${item.reason || '失效下载任务'} · ${item.delete_file ? '数据已删除' : '不删除数据文件'}`,
      })),
      emptyText: '本次预览没有需要确认的清理项。',
    }],
    confirmLabel: '确认并执行',
  }
}

function pluginUninstallSpec(action, config, common) {
  const ids = selectedValues(config.plugin_uninstall_ids);
  const cleanupItems = [
    { key: 'uninstall', title: '卸载选中的插件', enabled: true },
    { key: 'config', title: '清理插件配置', enabled: config.plugin_uninstall_clear_config === true },
    { key: 'data', title: '清理插件数据', enabled: config.plugin_uninstall_clear_data === true },
    { key: 'source', title: '删除插件源文件', enabled: config.plugin_uninstall_delete_source === true },
  ].filter(item => item.enabled);
  return {
    ...common,
    title: '确认卸载插件',
    warning: '以下操作将立即执行且无法撤销，请核对目标插件和清理范围。',
    summaryPrimary: `${ids.length} 个目标插件`,
    summarySecondary: `${cleanupItems.length} 项卸载或清理操作`,
    sections: [
      {
        key: 'plugin-uninstall-targets',
        label: '目标插件',
        items: ids.map(id => ({ key: id, title: id })),
        emptyText: '尚未在配置中心选择目标插件。',
      },
      {
        key: 'plugin-uninstall-actions',
        label: '卸载与清理范围',
        items: cleanupItems.map(item => ({ key: item.key, title: item.title })),
      },
    ],
    confirmLabel: '确认卸载',
  }
}

function buildQuickActionOperationSpec(action, context = {}) {
  if (!action) return null
  const id = actionId(action);
  const config = context.config || {};
  const common = {
    action,
    title: action.label || '确认操作',
    kicker: action.group || '快捷操作',
    warning: action.operation?.danger ? `${action.desc || action.label}，执行前请确认。` : (action.desc || ''),
    danger: action.operation?.danger === true,
    summaryPrimary: action.desc || action.label || '',
    summarySecondary: action.operation?.requiresPreview ? '已完成预览，请确认执行范围' : '使用当前保存的配置执行',
    confirmationInput: action.operation?.confirmationInput || null,
    confirmLabel: '确认执行',
    cancelLabel: '取消',
    returnFocusSelector: `[data-action-id="${id}"]`,
    rootAttrs: { 'data-quick-action-operation-dialog': '', 'data-quick-action-operation-id': id },
    confirmAttrs: { 'data-quick-action-operation-confirm': '' },
    cancelAttrs: { 'data-quick-action-operation-cancel': '' },
  };
  if (id === 'run_seed_clean') return seedCleanSpec(action, config, common)
  if (id === 'run_downloader_helper') return downloaderHelperSpec(action, context.downloaderHelperPreview, common)
  if (id === 'run_plugin_uninstall') return pluginUninstallSpec(action, config, common)
  return common
}

function useQuickActionController(options = {}) {
  const {
    api,
    surface = 'dashboard',
    iconSet = {},
    actions: suppliedActions = null,
    pluginId = 'Signal',
    pluginEnabled = true,
    tasks = [],
    componentStates = {},
    onSuccess = null,
  } = options;

  const actionConfig = ref$2({});
  const actionContextLoaded = ref$2(false);
  const actionContextError = ref$2('');
  const activeAction = ref$2(null);
  const operationSubmitting = ref$2(false);
  const downloaderHelperPreview = ref$2(null);
  const registeredActions = suppliedActions || createV31QuickActions(iconSet, surface);
  let actionRunner = null;

  function availabilityContext(action, overrides = {}) {
    const running = actionRunner?.isActionRunning(action) === true;
    return {
      surface: overrides.surface || surface,
      pluginEnabled: resolveMaybeValue(pluginEnabled) !== false,
      tasks: resolveMaybeValue(tasks) || [],
      config: actionConfig.value,
      componentStates: resolveMaybeValue(componentStates) || {},
      preconditionValues: actionConfig.value,
      runningActionId: running ? actionId(action) : '',
      runningActionLabel: running ? action?.label : '',
      ...overrides,
    }
  }

  function getActionAvailability(action, overrides = {}) {
    return resolveActionAvailability(action, availabilityContext(action, overrides))
  }

  function getDisabledMessage(action) {
    return getActionAvailability(action, { runningActionId: '', runningActionLabel: '' }).disabledReason
  }

  function getPayloadContext() {
    return {
      config: actionConfig.value,
      runtime: { downloaderHelperPreview: downloaderHelperPreview.value },
    }
  }

  actionRunner = useActionRunner({
    api,
    getDisabledMessage,
    getPayloadContext,
    onSuccess: async context => {
      if (actionId(context.action) === 'run_downloader_helper') {
        downloaderHelperPreview.value = context.res?.data?.confirm_required ? context.res.data : null;
      }
      if (typeof onSuccess === 'function') await onSuccess(context);
    },
  });

  const actions = computed$e(() => registeredActions
    .map(action => ({ ...action, availability: getActionAvailability(action) }))
    .filter(action => action.availability.visible));

  const operationSpec = computed$e(() => buildQuickActionOperationSpec(activeAction.value, {
    config: actionConfig.value,
    downloaderHelperPreview: downloaderHelperPreview.value,
  }));

  const operationBusy = computed$e(() => operationSubmitting.value || actionRunner.isActionRunning(activeAction.value));

  async function loadActionContext() {
    const apiClient = resolveMaybeValue(api);
    if (!apiClient?.get) {
      actionContextLoaded.value = false;
      actionContextError.value = 'MoviePilot 插件配置 API 未就绪';
      actionConfig.value = {};
      return false
    }
    try {
      const currentPluginId = String(resolveMaybeValue(pluginId) || 'Signal');
      const response = await apiClient.get(`plugin/form/${currentPluginId}`);
      actionConfig.value = normalizeConfigModel(response);
      actionContextLoaded.value = true;
      actionContextError.value = '';
      return true
    } catch (error) {
      actionConfig.value = {};
      actionContextLoaded.value = false;
      actionContextError.value = error?.message || '插件配置上下文加载失败';
      return false
    }
  }

  function openOperation(action) {
    const disabledMessage = getDisabledMessage(action);
    if (disabledMessage) {
      actionRunner.setMessage(disabledMessage, false);
      return false
    }
    activeAction.value = action;
    return true
  }

  async function triggerAction(action) {
    if (!action) return null
    const mode = action.operation?.mode || ACTION_OPERATION_MODE.direct;
    if (mode === ACTION_OPERATION_MODE.direct) return actionRunner.runAction(action)
    if (mode === ACTION_OPERATION_MODE.confirm) {
      return { started: false, panelOpened: openOperation(action), action }
    }
    if (mode === ACTION_OPERATION_MODE.previewConfirm) {
      downloaderHelperPreview.value = null;
      const result = await actionRunner.runAction(action);
      const panelOpened = result?.ok === true && downloaderHelperPreview.value?.confirm_required === true
        ? openOperation(action)
        : false;
      return { ...result, panelOpened }
    }
    return actionRunner.runAction(action)
  }

  function cancelOperation() {
    const closingId = actionId(activeAction.value);
    activeAction.value = null;
    if (closingId === 'run_downloader_helper') downloaderHelperPreview.value = null;
  }

  async function confirmOperation() {
    if (operationSubmitting.value) return null
    const action = activeAction.value;
    if (!action) return null
    operationSubmitting.value = true;
    activeAction.value = null;
    try {
      return await actionRunner.runAction(action)
    } finally {
      if (actionId(action) === 'run_downloader_helper') downloaderHelperPreview.value = null;
      operationSubmitting.value = false;
      await restoreActionTriggerFocus(action);
    }
  }

  return {
    actions,
    actionConfig,
    actionContextLoaded,
    actionContextError,
    actionRunner,
    activeAction,
    downloaderHelperPreview,
    operationSpec,
    operationBusy,
    getActionAvailability,
    getDisabledMessage,
    loadActionContext,
    triggerAction,
    cancelOperation,
    confirmOperation,
  }
}

const SITE_ICON_KEYS = Object.freeze(['yinYang', 'eye', 'chartPie', 'leaf', 'database']);
const SITE_ICON_COLORS = Object.freeze(['#34C759', '#60A5FA', '#FFB020', '#AF52DE', '#64D2FF']);

function finiteNumber(value, fallback = 0) {
  if (value === undefined || value === null || value === '') return finiteNumber(fallback, 0)
  const number = Number(value);
  return Number.isFinite(number) ? number : finiteNumber(fallback, 0)
}

function objectValue(value, fallback = {}) {
  return value && typeof value === 'object' && !Array.isArray(value) ? value : fallback
}

function createDashboardState(overrides = {}) {
  const source = objectValue(overrides);
  return {
    enabled: source.enabled !== false,
    summary: String(source.summary || ''),
    tasks: Array.isArray(source.tasks) ? [...source.tasks] : [],
    task_total: finiteNumber(source.task_total ?? source.taskTotal, 0),
    task_on: finiteNumber(source.task_on ?? source.taskOn, 0),
    task_failed: finiteNumber(source.task_failed ?? source.taskFailed, 0),
    health: { success: true, output: '', ...objectValue(source.health) },
  }
}

function normalizeDashboardPayload(payload, current = {}) {
  const source = objectValue(payload);
  const previous = objectValue(current);
  const tasks = Array.isArray(source.tasks) ? source.tasks : [];
  return {
    enabled: source.enabled !== false,
    summary: String(source.summary || ''),
    tasks,
    task_total: finiteNumber(source.task_total ?? source.taskTotal, tasks.length),
    task_on: finiteNumber(
      source.task_on ?? source.taskOn,
      tasks.filter(task => task?.state !== false).length,
    ),
    task_failed: finiteNumber(source.task_failed ?? source.taskFailed, 0),
    health: objectValue(source.health, objectValue(previous.health, { success: true, output: '' })),
  }
}

function applyDashboardPayload(target, payload) {
  return Object.assign(target, normalizeDashboardPayload(payload, target))
}

function createFusionCardState(overrides = {}) {
  const source = objectValue(overrides);
  return {
    id: String(source.id || source.message_id || ''),
    updatedAt: String(source.updatedAt || source.updated_at || source.date || ''),
    isBuilt: source.isBuilt === true || source.built === true || finiteNumber(source.message_id, 0) > 0,
    enabled: source.enabled !== false,
  }
}

function applyFusionCardPayload(target, payload) {
  const source = objectValue(payload);
  return Object.assign(target, {
    id: String(source.id || source.message_id || target.id || ''),
    updatedAt: String(source.updated_at || source.date || target.updatedAt || ''),
    isBuilt: source.built === true || finiteNumber(source.message_id, 0) > 0 || source.isBuilt === true,
    enabled: source.enabled !== false,
  })
}

function resetFusionCardState(target, enabled = false) {
  return Object.assign(target, createFusionCardState({ enabled }))
}

function buildRuntimeTasks(dashboard) {
  const pluginEnabled = dashboard.enabled !== false;
  const tasks = Array.isArray(dashboard.tasks) ? dashboard.tasks : [];
  return tasks.map((task) => {
    const rawSchedule = String(task?.next_run || task?.schedule || task?.next || '已注册').trim();
    return {
      key: task?.key || task?.service_id || task?.id || task?.name,
      name: task?.name || '注册任务',
      enabled: pluginEnabled && task?.effective_enabled === true,
      state: task?.state || '',
      schedule: pluginEnabled
        ? (rawSchedule.startsWith('下次') ? rawSchedule : `下次 ${rawSchedule}`)
        : '插件已停用',
    }
  }).filter(task => task.enabled)
}

function buildSiteCards(rows, total, icons) {
  return rows.map((site, index) => {
    const traffic = finiteNumber(site?.upload) + finiteNumber(site?.download);
    const iconKey = SITE_ICON_KEYS[index % SITE_ICON_KEYS.length];
    return {
      name: String(site?.name || `站点 ${index + 1}`),
      icon: icons[iconKey] || '',
      iconColor: SITE_ICON_COLORS[index % SITE_ICON_COLORS.length],
      percent: sitePercent(traffic, total),
      upload: formatGB(site?.upload || 0),
      download: formatGB(site?.download || 0),
    }
  })
}

function buildActionFeedback(actionState) {
  const runningLabels = Array.isArray(actionState.runningLabels) ? actionState.runningLabels.filter(Boolean) : [];
  if (runningLabels.length === 1) {
    return { message: `${runningLabels[0] || '当前动作'}执行中，请稍候。`, ok: true }
  }
  if (runningLabels.length > 1) {
    return { message: `${runningLabels.length} 个动作正在执行，请稍候。`, ok: true }
  }
  return {
    message: String(actionState.message || ''),
    ok: actionState.ok !== false,
  }
}

function buildActionGroups(actions) {
  const source = Array.isArray(actions) ? actions.filter(Boolean) : [];
  const grouped = new Map();

  for (const action of source) {
    const groupId = String(action?.groupId || 'other');
    if (!grouped.has(groupId)) {
      const registered = actionGroupRegistry[groupId];
      grouped.set(groupId, {
        id: groupId,
        group: String(registered?.label || action?.group || '其他操作'),
        icon: String(registered?.icon || ''),
        actions: [],
      });
    }
    grouped.get(groupId).actions.push(action);
  }

  const canonicalOrder = Object.keys(actionGroupRegistry);
  const orderedIds = [
    ...canonicalOrder.filter(groupId => grouped.has(groupId)),
    ...[...grouped.keys()].filter(groupId => !canonicalOrder.includes(groupId)),
  ];
  return orderedIds.map(groupId => grouped.get(groupId))
}

function buildDashboardViewSnapshot(input = {}) {
  const dashboard = objectValue(input.dashboard);
  const siteChart = objectValue(input.siteChart);
  const siteRows = Array.isArray(input.siteRows) ? input.siteRows : [];
  const sitePieSegments = Array.isArray(input.sitePieSegments) ? input.sitePieSegments : [];
  const sitePieStyle = objectValue(input.sitePieStyle);
  const quickActions = Array.isArray(input.quickActions) ? input.quickActions : [];
  const actionState = objectValue(input.actionState);
  const fusionCard = objectValue(input.fusionCard);
  const icons = objectValue(input.icons);
  const pluginEnabled = dashboard.enabled !== false;
  const runtimeTasks = buildRuntimeTasks(dashboard);
  const enabledCount = runtimeTasks.length;
  const inferredTaskTotal = Math.max(enabledCount, Array.isArray(dashboard.tasks) ? dashboard.tasks.length : 0);
  const totalCount = finiteNumber(dashboard.task_total, 0) || inferredTaskTotal;
  const taskFailed = finiteNumber(dashboard.task_failed, 0);
  const healthOk = dashboard.health?.success !== false && taskFailed === 0;
  const chartTrafficTotal = finiteNumber(siteChart.upload_total) + finiteNumber(siteChart.download_total);
  const trafficTotal = finiteNumber(input.siteTrafficTotal, 0) || chartTrafficTotal;
  const [trafficValue = '0.0', trafficUnit = 'MB'] = formatGB(trafficTotal).split(' ');
  const actionFeedback = buildActionFeedback(actionState);

  return {
    pluginEnabled,
    kpis: {
      items: [
        {
          key: 'system',
          label: '系统状态',
          icon: icons.checkCircle,
          iconColor: pluginEnabled ? '#34C759' : '#8E8E93',
          value: pluginEnabled ? '运行平稳' : '插件已停用',
          detail: pluginEnabled
            ? (healthOk ? '当前任务未发现异常' : `当前有 ${taskFailed} 个异常组件`)
            : '开启插件总开关后恢复运行',
        },
        {
          key: 'runtime',
          label: '运行状态',
          dot: pluginEnabled,
          pulse: pluginEnabled,
          value: pluginEnabled ? '正常' : '停用',
          detail: `异常组件 ${taskFailed}`,
        },
        {
          key: 'enabled',
          label: '启用组件',
          icon: icons.checkCircle,
          iconColor: '#8E8E93',
          value: String(enabledCount),
          total: String(totalCount),
          large: true,
          detail: pluginEnabled ? '组件运行正常' : '组件当前均未运行',
        },
        {
          key: 'traffic',
          label: '站点流量',
          icon: icons.chartPie,
          iconColor: '#60A5FA',
          value: trafficValue,
          unit: trafficUnit,
          large: true,
          detail: '任务调度与健康巡查',
        },
      ],
      healthOk,
      enabledCount,
      totalCount,
    },
    site: {
      dateNote: String(input.siteDateNote || '今天 00:00 起'),
      donutValue: String(sitePieSegments.length || siteRows.length || 0),
      donutSegments: sitePieSegments,
      donutStyle: sitePieStyle,
      summaryRows: [
        { label: '上传增量', value: formatGB(siteChart.upload_total || 0), icon: icons.arrowUp },
        { label: '下载增量', value: formatGB(siteChart.download_total || 0), icon: icons.arrowDown },
        { label: '统计时间', value: siteChart.date || '等待统计', icon: icons.calendarToday },
      ],
      cards: buildSiteCards(siteRows, trafficTotal, icons),
      trafficTotal,
    },
    runtime: {
      tasks: runtimeTasks,
      enabledCount,
      totalCount,
    },
    actions: {
      items: quickActions,
      groups: buildActionGroups(quickActions),
      runningKey: String(actionState.runningKey || ''),
      runningKeys: Array.isArray(actionState.runningKeys) ? actionState.runningKeys : [],
      feedbackMessage: actionFeedback.message,
      feedbackOk: actionFeedback.ok,
    },
    fusion: {
      cardId: String(fusionCard.id || ''),
      updatedAt: String(fusionCard.updatedAt || ''),
      isBuilt: fusionCard.isBuilt === true,
      enabled: pluginEnabled && fusionCard.enabled !== false,
    },
  }
}

const {computed: computed$d,unref} = await importShared('vue');

function resolveValue(value, fallback) {
  const resolved = typeof value === 'function' ? value() : unref(value);
  return resolved === undefined || resolved === null ? fallback : resolved
}

function useDashboardViewModel(options = {}) {
  const actionRunner = options.actionRunner || {};
  const snapshot = computed$d(() => buildDashboardViewSnapshot({
    dashboard: resolveValue(options.dashboard, {}),
    siteChart: resolveValue(options.siteChart, {}),
    siteRows: resolveValue(options.siteRows, []),
    siteTrafficTotal: resolveValue(options.siteTrafficTotal, 0),
    siteDateNote: resolveValue(options.siteDateNote, ''),
    sitePieSegments: resolveValue(options.sitePieSegments, []),
    sitePieStyle: resolveValue(options.sitePieStyle, {}),
    quickActions: resolveValue(options.quickActions, []),
    fusionCard: resolveValue(options.fusionCard, {}),
    icons: resolveValue(options.icons, {}),
    actionState: {
      runningKey: resolveValue(actionRunner.actionRunning, ''),
      runningKeys: resolveValue(actionRunner.runningActionIds, []),
      runningLabels: resolveValue(actionRunner.runningActionLabels, []),
      message: resolveValue(actionRunner.actionMessage, ''),
      ok: resolveValue(actionRunner.actionOk, true),
    },
  }));

  const pick = selector => computed$d(() => selector(snapshot.value));

  return {
    snapshot,
    kpiItems: pick(view => view.kpis.items),
    healthOk: pick(view => view.kpis.healthOk),
    enabledCount: pick(view => view.kpis.enabledCount),
    totalCount: pick(view => view.kpis.totalCount),
    siteView: pick(view => view.site),
    siteCards: pick(view => view.site.cards),
    sitePieSegments: pick(view => view.site.donutSegments),
    sitePieStyle: pick(view => view.site.donutStyle),
    siteTrafficTotal: pick(view => view.site.trafficTotal),
    trafficSummaryRows: pick(view => view.site.summaryRows),
    runtimeTasks: pick(view => view.runtime.tasks),
    donutValue: pick(view => view.site.donutValue),
    dateNote: pick(view => view.site.dateNote),
    actionsView: pick(view => view.actions),
    quickActions: pick(view => view.actions.items),
    actionRunning: pick(view => view.actions.runningKey),
    actionRunningKeys: pick(view => view.actions.runningKeys),
    actionFeedbackMessage: pick(view => view.actions.feedbackMessage),
    actionFeedbackOk: pick(view => view.actions.feedbackOk),
    fusionView: pick(view => view.fusion),
  }
}

const {renderSlot:_renderSlot$5,createElementVNode:_createElementVNode$b,normalizeClass:_normalizeClass$b,openBlock:_openBlock$l,createElementBlock:_createElementBlock$g} = await importShared('vue');


const _hoisted_1$e = { class: "v31-dashboard-canvas" };
const _hoisted_2$d = {
  class: "v31-core-grid",
  "data-dashboard-region": "core"
};
const _hoisted_3$b = {
  class: "v31-glass-card v31-bottom-row",
  "data-dashboard-region": "bottom"
};

const {computed: computed$c} = await importShared('vue');



const _sfc_main$l = {
  __name: 'DashboardV31Shell',
  props: {
  surface: { type: String, default: 'dialog' },
  themeClass: { type: String, default: '' },
},
  setup(__props) {

const props = __props;

const shellClass = computed$c(() => [
  `v31-dashboard-shell--${props.surface || 'dialog'}`,
  props.themeClass,
]);

return (_ctx, _cache) => {
  return (_openBlock$l(), _createElementBlock$g("section", {
    class: _normalizeClass$b(["dashboard-plugin-vue-renderer v31-dashboard-shell aoa-root aoa-plugin-shell", shellClass.value])
  }, [
    _createElementVNode$b("div", _hoisted_1$e, [
      _renderSlot$5(_ctx.$slots, "toolbar"),
      _renderSlot$5(_ctx.$slots, "metrics"),
      _createElementVNode$b("div", _hoisted_2$d, [
        _renderSlot$5(_ctx.$slots, "core-primary"),
        _renderSlot$5(_ctx.$slots, "core-secondary")
      ]),
      _createElementVNode$b("div", _hoisted_3$b, [
        _renderSlot$5(_ctx.$slots, "bottom-primary"),
        _renderSlot$5(_ctx.$slots, "bottom-secondary")
      ]),
      _renderSlot$5(_ctx.$slots, "status")
    ]),
    _renderSlot$5(_ctx.$slots, "overlay")
  ], 2))
}
}

};

const {createElementVNode:_createElementVNode$a,openBlock:_openBlock$k,createElementBlock:_createElementBlock$f,normalizeStyle:_normalizeStyle$1} = await importShared('vue');


const _hoisted_1$d = ["width", "height"];
const _hoisted_2$c = ["d"];

const {computed: computed$b} = await importShared('vue');



const _sfc_main$k = {
  __name: 'SvgIcon',
  props: {
  icon: { type: String, required: true },
  size: { type: [Number, String], default: 14 },
  color: { type: String, default: '' },
},
  setup(__props) {

const props = __props;

const normalizedSize = computed$b(() => {
  const rawSize = String(props.size).trim();
  return /^\d+(\.\d+)?$/.test(rawSize) ? `${rawSize}px` : rawSize
});

const iconStyle = computed$b(() => ({
  '--v31-icon-size': normalizedSize.value,
  inlineSize: normalizedSize.value,
  blockSize: normalizedSize.value,
  color: props.color || undefined,
}));

return (_ctx, _cache) => {
  return (_openBlock$k(), _createElementBlock$f("i", {
    class: "v31-svg-icon",
    style: _normalizeStyle$1(iconStyle.value),
    "aria-hidden": "true"
  }, [
    (_openBlock$k(), _createElementBlock$f("svg", {
      class: "v31-svg-icon__svg",
      xmlns: "http://www.w3.org/2000/svg",
      viewBox: "0 0 24 24",
      width: normalizedSize.value,
      height: normalizedSize.value,
      focusable: "false",
      role: "img"
    }, [
      _createElementVNode$a("path", {
        d: __props.icon,
        fill: "currentColor"
      }, null, 8, _hoisted_2$c)
    ], 8, _hoisted_1$d))
  ], 4))
}
}

};

const {openBlock:_openBlock$j,createElementBlock:_createElementBlock$e,createCommentVNode:_createCommentVNode$a,createBlock:_createBlock$b,renderSlot:_renderSlot$4,toDisplayString:_toDisplayString$a,createTextVNode:_createTextVNode$4,normalizeClass:_normalizeClass$a} = await importShared('vue');


const _hoisted_1$c = ["disabled", "aria-busy", "aria-label", "data-state"];
const _hoisted_2$b = {
  key: 0,
  class: "aoa-loading-indicator",
  "aria-hidden": "true"
};
const _hoisted_3$a = { key: 2 };


const _sfc_main$j = {
  __name: 'PillButton',
  props: {
  icon: { type: String, default: '' },
  label: { type: String, default: '' },
  iconOnly: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
  loading: { type: Boolean, default: false },
},
  setup(__props) {



return (_ctx, _cache) => {
  return (_openBlock$j(), _createElementBlock$e("button", {
    type: "button",
    class: _normalizeClass$a(["v31-glass-card v31-pill-button aoa-button aoa-interactive", { 'v31-pill-button--icon': __props.iconOnly, 'v31-pill-button--loading': __props.loading }]),
    disabled: __props.disabled || __props.loading,
    "aria-busy": __props.loading ? 'true' : undefined,
    "aria-label": __props.iconOnly ? __props.label || undefined : undefined,
    "data-state": __props.loading ? 'loading' : __props.disabled ? 'disabled' : 'idle'
  }, [
    (__props.loading)
      ? (_openBlock$j(), _createElementBlock$e("span", _hoisted_2$b))
      : (__props.icon)
        ? (_openBlock$j(), _createBlock$b(_sfc_main$k, {
            key: 1,
            icon: __props.icon,
            size: "14"
          }, null, 8, ["icon"]))
        : _createCommentVNode$a("", true),
    (!__props.iconOnly)
      ? (_openBlock$j(), _createElementBlock$e("span", _hoisted_3$a, [
          _renderSlot$4(_ctx.$slots, "default", {}, () => [
            _createTextVNode$4(_toDisplayString$a(__props.label), 1)
          ])
        ]))
      : _createCommentVNode$a("", true)
  ], 10, _hoisted_1$c))
}
}

};

const v31Icons = {
  arrowDown: mdiArrowDown,
  arrowUp: mdiArrowUp,
  bell: mdiBellOutline,
  broom: mdiBroom,
  calendarCheck: mdiCalendarCheck,
  calendarToday: mdiCalendarToday,
  cardAccount: mdiCardAccountDetailsOutline,
  cardPlus: mdiCardPlusOutline,
  chartPie: mdiChartPie,
  checkCircle: mdiCheckCircle,
  cloudUpload: mdiCloudUploadOutline,
  cog: mdiCog,
  database: mdiDatabase,
  eye: mdiEye,
  heartPulse: mdiHeartPulse,
  leaf: mdiLeaf,
  refresh: mdiRefresh,
  rss: mdiRss,
  tagMultiple: mdiTagMultiple,
  trash: mdiTrashCanOutline,
  viewDashboard: mdiViewDashboardOutline,
  yinYang: mdiYinYang,
};

const {unref:_unref$8,createVNode:_createVNode$b,createElementVNode:_createElementVNode$9,openBlock:_openBlock$i,createElementBlock:_createElementBlock$d} = await importShared('vue');


const _hoisted_1$b = { class: "v31-dashboard-toolbar" };
const _hoisted_2$a = { class: "v31-dashboard-toolbar__brand" };
const _hoisted_3$9 = { class: "v31-dashboard-toolbar__brand-icon" };
const _hoisted_4$9 = { class: "v31-dashboard-toolbar__actions" };


const _sfc_main$i = {
  __name: 'DashboardV31Toolbar',
  props: {
  loading: { type: Boolean, default: false },
},
  emits: ['refresh', 'settings'],
  setup(__props) {





return (_ctx, _cache) => {
  return (_openBlock$i(), _createElementBlock$d("header", _hoisted_1$b, [
    _createElementVNode$9("div", _hoisted_2$a, [
      _createElementVNode$9("span", _hoisted_3$9, [
        _createVNode$b(_sfc_main$k, {
          icon: _unref$8(v31Icons).viewDashboard,
          size: 20
        }, null, 8, ["icon"])
      ]),
      _cache[2] || (_cache[2] = _createElementVNode$9("div", { class: "v31-dashboard-toolbar__title-stack" }, [
        _createElementVNode$9("h1", { class: "v31-dashboard-toolbar__title" }, "仪表盘"),
        _createElementVNode$9("p", { class: "v31-dashboard-toolbar__subtitle" }, "运行状态、任务与站点概览")
      ], -1))
    ]),
    _createElementVNode$9("div", _hoisted_4$9, [
      _createVNode$b(_sfc_main$j, {
        icon: _unref$8(v31Icons).refresh,
        label: "刷新",
        loading: __props.loading,
        onClick: _cache[0] || (_cache[0] = $event => (_ctx.$emit('refresh')))
      }, null, 8, ["icon", "loading"]),
      _createVNode$b(_sfc_main$j, {
        icon: _unref$8(v31Icons).cog,
        "icon-only": "",
        label: "设置",
        onClick: _cache[1] || (_cache[1] = $event => (_ctx.$emit('settings')))
      }, null, 8, ["icon"])
    ])
  ]))
}
}

};

const {renderSlot:_renderSlot$3,resolveDynamicComponent:_resolveDynamicComponent$2,normalizeClass:_normalizeClass$9,withCtx:_withCtx$6,openBlock:_openBlock$h,createBlock:_createBlock$a} = await importShared('vue');


const {computed: computed$a} = await importShared('vue');



const _sfc_main$h = {
  __name: 'GlassCard',
  props: {
  tag: { type: String, default: 'section' },
  light: { type: Boolean, default: false },
  className: { type: [String, Array, Object], default: '' },
},
  setup(__props) {

const props = __props;

const cardClass = computed$a(() => [
  'aoa-surface-card',
  props.light ? 'v31-glass-card-light' : 'v31-glass-card',
  props.light ? 'aoa-surface-card--muted' : '',
  props.className,
]);

return (_ctx, _cache) => {
  return (_openBlock$h(), _createBlock$a(_resolveDynamicComponent$2(__props.tag), {
    class: _normalizeClass$9(cardClass.value)
  }, {
    default: _withCtx$6(() => [
      _renderSlot$3(_ctx.$slots, "default")
    ]),
    _: 3
  }, 8, ["class"]))
}
}

};

const {openBlock:_openBlock$g,createBlock:_createBlock$9,createCommentVNode:_createCommentVNode$9,normalizeClass:_normalizeClass$8,createElementBlock:_createElementBlock$c,createElementVNode:_createElementVNode$8,toDisplayString:_toDisplayString$9,withCtx:_withCtx$5} = await importShared('vue');


const _hoisted_1$a = { class: "v31-kpi-card__icon" };
const _hoisted_2$9 = { class: "v31-kpi-card__content" };
const _hoisted_3$8 = { class: "v31-kpi-card__label" };
const _hoisted_4$8 = { class: "v31-kpi-card__value-row" };
const _hoisted_5$5 = {
  key: 0,
  class: "v31-kpi-card__total"
};
const _hoisted_6$4 = {
  key: 1,
  class: "v31-kpi-card__unit"
};
const _hoisted_7$4 = { class: "v31-kpi-card__detail" };


const _sfc_main$g = {
  __name: 'KpiCard',
  props: {
  item: { type: Object, required: true },
},
  setup(__props) {



return (_ctx, _cache) => {
  return (_openBlock$g(), _createBlock$9(_sfc_main$h, { "class-name": "v31-kpi-card" }, {
    default: _withCtx$5(() => [
      _createElementVNode$8("span", _hoisted_1$a, [
        (__props.item.icon)
          ? (_openBlock$g(), _createBlock$9(_sfc_main$k, {
              key: 0,
              icon: __props.item.icon,
              color: __props.item.iconColor || undefined,
              size: "20"
            }, null, 8, ["icon", "color"]))
          : _createCommentVNode$9("", true),
        (__props.item.dot)
          ? (_openBlock$g(), _createElementBlock$c("span", {
              key: 1,
              class: _normalizeClass$8(["v31-status-dot", { 'v31-status-dot--pulse': __props.item.pulse }])
            }, null, 2))
          : _createCommentVNode$9("", true)
      ]),
      _createElementVNode$8("div", _hoisted_2$9, [
        _createElementVNode$8("span", _hoisted_3$8, _toDisplayString$9(__props.item.label), 1),
        _createElementVNode$8("div", _hoisted_4$8, [
          _createElementVNode$8("span", {
            class: _normalizeClass$8(["v31-kpi-card__value", { 'v31-kpi-card__value--large': __props.item.large }])
          }, _toDisplayString$9(__props.item.value), 3),
          (__props.item.total)
            ? (_openBlock$g(), _createElementBlock$c("span", _hoisted_5$5, "/ " + _toDisplayString$9(__props.item.total), 1))
            : _createCommentVNode$9("", true),
          (__props.item.unit)
            ? (_openBlock$g(), _createElementBlock$c("span", _hoisted_6$4, _toDisplayString$9(__props.item.unit), 1))
            : _createCommentVNode$9("", true)
        ]),
        _createElementVNode$8("span", _hoisted_7$4, _toDisplayString$9(__props.item.detail), 1)
      ])
    ]),
    _: 1
  }))
}
}

};

const {renderList:_renderList$4,Fragment:_Fragment$5,openBlock:_openBlock$f,createElementBlock:_createElementBlock$b,createBlock:_createBlock$8} = await importShared('vue');


const _hoisted_1$9 = {
  class: "v31-kpi-strip aoa-surface-grid aoa-surface-grid--metrics",
  "aria-label": "仪表盘指标"
};


const _sfc_main$f = {
  __name: 'KpiStrip',
  props: {
  items: { type: Array, default: () => [] },
},
  setup(__props) {



return (_ctx, _cache) => {
  return (_openBlock$f(), _createElementBlock$b("div", _hoisted_1$9, [
    (_openBlock$f(true), _createElementBlock$b(_Fragment$5, null, _renderList$4(__props.items, (item) => {
      return (_openBlock$f(), _createBlock$8(_sfc_main$g, {
        key: item.key,
        item: item
      }, null, 8, ["item"]))
    }), 128))
  ]))
}
}

};

const {toDisplayString:_toDisplayString$8,createElementVNode:_createElementVNode$7,normalizeClass:_normalizeClass$7,normalizeStyle:_normalizeStyle,openBlock:_openBlock$e,createElementBlock:_createElementBlock$a} = await importShared('vue');


const _hoisted_1$8 = ["aria-label"];
const _hoisted_2$8 = { class: "v31-donut__inner" };
const _hoisted_3$7 = { class: "v31-donut__value" };
const _hoisted_4$7 = { class: "v31-donut__label" };

const {computed: computed$9} = await importShared('vue');



const _sfc_main$e = {
  __name: 'DonutRing',
  props: {
  value: { type: [String, Number], default: '2' },
  label: { type: String, default: '个站点' },
  segments: { type: Array, default: () => [] },
  pieStyle: { type: Object, default: () => ({}) },
},
  setup(__props) {

const props = __props;

const normalizedSegments = computed$9(() => Array.isArray(props.segments) ? props.segments : []);
const ringStyle = computed$9(() => {
  if (props.pieStyle && typeof props.pieStyle === 'object' && Object.keys(props.pieStyle).length) {
    return props.pieStyle
  }
  return {
    background: 'conic-gradient(rgba(var(--aoa-color-line-rgb), 0.16) 0 82deg, rgba(var(--aoa-color-line-rgb), 0.055) 82deg 360deg)',
  }
});
const ariaLabel = computed$9(() => {
  if (!normalizedSegments.value.length) return `${props.value} ${props.label}，暂无站点流量分段`
  const names = normalizedSegments.value.map(item => item?.name).filter(Boolean).slice(0, 4).join('、');
  return `${props.value} ${props.label}，按 PT 站点${names ? ` ${names}` : ''} 流量分段`
});

return (_ctx, _cache) => {
  return (_openBlock$e(), _createElementBlock$a("div", {
    class: _normalizeClass$7(["v31-donut", { 'v31-donut--empty': !normalizedSegments.value.length }]),
    style: _normalizeStyle(ringStyle.value),
    "aria-label": ariaLabel.value
  }, [
    _createElementVNode$7("div", _hoisted_2$8, [
      _createElementVNode$7("span", null, [
        _createElementVNode$7("strong", _hoisted_3$7, _toDisplayString$8(__props.value), 1),
        _createElementVNode$7("small", _hoisted_4$7, _toDisplayString$8(__props.label), 1)
      ])
    ])
  ], 14, _hoisted_1$8))
}
}

};

const {renderList:_renderList$3,Fragment:_Fragment$4,openBlock:_openBlock$d,createElementBlock:_createElementBlock$9,createVNode:_createVNode$a,createCommentVNode:_createCommentVNode$8,toDisplayString:_toDisplayString$7,createElementVNode:_createElementVNode$6} = await importShared('vue');


const _hoisted_1$7 = { class: "v31-traffic-summary" };
const _hoisted_2$7 = {
  key: 0,
  class: "v31-traffic-summary__icon",
  "aria-hidden": "true"
};
const _hoisted_3$6 = { class: "v31-traffic-summary__text" };
const _hoisted_4$6 = { class: "v31-traffic-summary__label" };
const _hoisted_5$4 = { class: "v31-traffic-summary__value" };


const _sfc_main$d = {
  __name: 'TrafficSummary',
  props: {
  rows: { type: Array, default: () => [] },
},
  setup(__props) {



return (_ctx, _cache) => {
  return (_openBlock$d(), _createElementBlock$9("div", _hoisted_1$7, [
    (_openBlock$d(true), _createElementBlock$9(_Fragment$4, null, _renderList$3(__props.rows, (row) => {
      return (_openBlock$d(), _createElementBlock$9("div", {
        key: row.label,
        class: "v31-traffic-summary__pill"
      }, [
        (row.icon)
          ? (_openBlock$d(), _createElementBlock$9("span", _hoisted_2$7, [
              _createVNode$a(_sfc_main$k, {
                icon: row.icon,
                size: "12"
              }, null, 8, ["icon"])
            ]))
          : _createCommentVNode$8("", true),
        _createElementVNode$6("span", _hoisted_3$6, [
          _createElementVNode$6("span", _hoisted_4$6, _toDisplayString$7(row.label), 1),
          _createElementVNode$6("strong", _hoisted_5$4, _toDisplayString$7(row.value), 1)
        ])
      ]))
    }), 128))
  ]))
}
}

};

const {createVNode:_createVNode$9,createElementVNode:_createElementVNode$5,toDisplayString:_toDisplayString$6,unref:_unref$7,createTextVNode:_createTextVNode$3,openBlock:_openBlock$c,createElementBlock:_createElementBlock$8} = await importShared('vue');


const _hoisted_1$6 = { class: "v31-glass-card-light v31-site-traffic-card" };
const _hoisted_2$6 = { class: "v31-site-traffic-card__identity" };
const _hoisted_3$5 = { class: "v31-site-traffic-card__icon" };
const _hoisted_4$5 = { class: "v31-site-traffic-card__name" };
const _hoisted_5$3 = { class: "v31-site-traffic-card__metrics" };
const _hoisted_6$3 = { class: "v31-site-traffic-card__metric-pill v31-site-traffic-card__metric-pill--upload" };
const _hoisted_7$3 = { class: "v31-site-traffic-card__metric-pill v31-site-traffic-card__metric-pill--download" };
const _hoisted_8$2 = { class: "v31-site-traffic-card__percent" };
const _hoisted_9 = { class: "v31-site-traffic-card__percent-icon" };


const _sfc_main$c = {
  __name: 'SiteTrafficCard',
  props: {
  name: { type: String, default: '馒头' },
  icon: { type: String, default: v31Icons.yinYang },
  iconColor: { type: String, default: '#34C759' },
  percent: { type: String, default: '100%' },
  upload: { type: String, default: '64.45 GB' },
  download: { type: String, default: '58.00 GB' },
},
  setup(__props) {



return (_ctx, _cache) => {
  return (_openBlock$c(), _createElementBlock$8("article", _hoisted_1$6, [
    _createElementVNode$5("div", _hoisted_2$6, [
      _createElementVNode$5("span", _hoisted_3$5, [
        _createVNode$9(_sfc_main$k, {
          icon: __props.icon,
          color: __props.iconColor,
          size: "14"
        }, null, 8, ["icon", "color"])
      ]),
      _createElementVNode$5("span", _hoisted_4$5, _toDisplayString$6(__props.name), 1)
    ]),
    _createElementVNode$5("div", _hoisted_5$3, [
      _createElementVNode$5("span", _hoisted_6$3, [
        _createVNode$9(_sfc_main$k, {
          icon: _unref$7(v31Icons).arrowUp,
          size: "10"
        }, null, 8, ["icon"]),
        _createTextVNode$3(" " + _toDisplayString$6(__props.upload), 1)
      ]),
      _createElementVNode$5("span", _hoisted_7$3, [
        _createVNode$9(_sfc_main$k, {
          icon: _unref$7(v31Icons).arrowDown,
          size: "10"
        }, null, 8, ["icon"]),
        _createTextVNode$3(" " + _toDisplayString$6(__props.download), 1)
      ])
    ]),
    _createElementVNode$5("span", _hoisted_8$2, [
      _createElementVNode$5("span", _hoisted_9, [
        _createVNode$9(_sfc_main$k, {
          icon: _unref$7(v31Icons).chartPie,
          size: "9"
        }, null, 8, ["icon"])
      ]),
      _createTextVNode$3(" " + _toDisplayString$6(__props.percent), 1)
    ])
  ]))
}
}

};

const {unref:_unref$6,createVNode:_createVNode$8,createTextVNode:_createTextVNode$2,createElementVNode:_createElementVNode$4,toDisplayString:_toDisplayString$5,renderSlot:_renderSlot$2,renderList:_renderList$2,Fragment:_Fragment$3,openBlock:_openBlock$b,createElementBlock:_createElementBlock$7,createBlock:_createBlock$7,resolveDynamicComponent:_resolveDynamicComponent$1,normalizeClass:_normalizeClass$6,withCtx:_withCtx$4} = await importShared('vue');


const _hoisted_1$5 = { class: "v31-card-header" };
const _hoisted_2$5 = { class: "v31-card-heading" };
const _hoisted_3$4 = { class: "v31-card-header__aside" };
const _hoisted_4$4 = { class: "v31-card-note" };
const _hoisted_5$2 = { class: "v31-site-panel__body" };
const _hoisted_6$2 = { class: "v31-site-panel__content" };
const _hoisted_7$2 = ["data-empty"];

const {computed: computed$8} = await importShared('vue');


const _sfc_main$b = {
  __name: 'SiteDataPanel',
  props: {
  site: { type: Object, default: () => ({}) },
  loading: { type: Boolean, default: false },
  error: { type: [String, Boolean], default: '' },
  nativeContent: { type: Boolean, default: false },
},
  setup(__props) {

const props = __props;

const surfaceComponent = computed$8(() => props.nativeContent ? 'section' : _sfc_main$h);
const surfaceClass = computed$8(() => props.nativeContent ? 'v31-site-panel' : undefined);

const view = computed$8(() => {
  const site = props.site && typeof props.site === 'object' ? props.site : {};
  return {
    dateNote: String(site.dateNote || '今天 00:00 起'),
    donutValue: String(site.donutValue ?? 0),
    donutSegments: Array.isArray(site.donutSegments) ? site.donutSegments : [],
    donutStyle: site.donutStyle && typeof site.donutStyle === 'object' ? site.donutStyle : {},
    summaryRows: Array.isArray(site.summaryRows) ? site.summaryRows : [],
    cards: Array.isArray(site.cards) ? site.cards : [],
  }
});

const siteState = computed$8(() => {
  if (props.loading) return 'loading'
  if (props.error) return 'error'
  return view.value.cards.length ? 'ready' : 'empty'
});

return (_ctx, _cache) => {
  return (_openBlock$b(), _createBlock$7(_resolveDynamicComponent$1(surfaceComponent.value), {
    "class-name": "v31-site-panel",
    class: _normalizeClass$6(surfaceClass.value),
    "aria-busy": __props.loading || undefined,
    "data-site-state": siteState.value,
    "data-site-surface": __props.nativeContent ? 'content-only' : 'glass-card'
  }, {
    default: _withCtx$4(() => [
      _createElementVNode$4("div", _hoisted_1$5, [
        _createElementVNode$4("h2", _hoisted_2$5, [
          _createVNode$8(_sfc_main$k, {
            icon: _unref$6(v31Icons).leaf,
            color: "#34C759",
            size: "18"
          }, null, 8, ["icon"]),
          _cache[0] || (_cache[0] = _createTextVNode$2(" 站点数据 ", -1))
        ]),
        _createElementVNode$4("div", _hoisted_3$4, [
          _createElementVNode$4("span", _hoisted_4$4, _toDisplayString$5(view.value.dateNote), 1),
          _renderSlot$2(_ctx.$slots, "header-action", {}, undefined, true)
        ])
      ]),
      _createElementVNode$4("div", _hoisted_5$2, [
        _createVNode$8(_sfc_main$e, {
          value: view.value.donutValue,
          label: "个站点",
          segments: view.value.donutSegments,
          "pie-style": view.value.donutStyle
        }, null, 8, ["value", "segments", "pie-style"]),
        _createElementVNode$4("div", _hoisted_6$2, [
          _createVNode$8(_sfc_main$d, {
            rows: view.value.summaryRows
          }, null, 8, ["rows"]),
          _createElementVNode$4("div", {
            class: "v31-site-card-list",
            "data-empty": view.value.cards.length ? 'false' : 'true'
          }, [
            (_openBlock$b(true), _createElementBlock$7(_Fragment$3, null, _renderList$2(view.value.cards, (site) => {
              return (_openBlock$b(), _createBlock$7(_sfc_main$c, {
                key: site.name,
                name: site.name,
                icon: site.icon,
                "icon-color": site.iconColor,
                percent: site.percent,
                upload: site.upload,
                download: site.download
              }, null, 8, ["name", "icon", "icon-color", "percent", "upload", "download"]))
            }), 128))
          ], 8, _hoisted_7$2)
        ])
      ])
    ]),
    _: 3
  }, 8, ["class", "aria-busy", "data-site-state", "data-site-surface"]))
}
}

};
const SiteDataPanel = /*#__PURE__*/_export_sfc(_sfc_main$b, [['__scopeId',"data-v-9607fd8d"]]);

const {openBlock:_openBlock$a,createBlock:_createBlock$6,createCommentVNode:_createCommentVNode$7,renderSlot:_renderSlot$1,toDisplayString:_toDisplayString$4,createTextVNode:_createTextVNode$1,normalizeClass:_normalizeClass$5,createElementBlock:_createElementBlock$6} = await importShared('vue');


const {computed: computed$7} = await importShared('vue');


const _sfc_main$a = {
  __name: 'StatusChip',
  props: {
  label: { type: String, default: '' },
  tone: { type: String, default: '' },
  icon: { type: String, default: '' },
},
  setup(__props) {

const props = __props;

const toneClass = computed$7(() => props.tone ? `v31-status-chip--${props.tone}` : '');

return (_ctx, _cache) => {
  return (_openBlock$a(), _createElementBlock$6("span", {
    class: _normalizeClass$5(["v31-status-chip", toneClass.value])
  }, [
    (__props.icon)
      ? (_openBlock$a(), _createBlock$6(_sfc_main$k, {
          key: 0,
          icon: __props.icon,
          size: "10"
        }, null, 8, ["icon"]))
      : _createCommentVNode$7("", true),
    _renderSlot$1(_ctx.$slots, "default", {}, () => [
      _createTextVNode$1(_toDisplayString$4(__props.label), 1)
    ])
  ], 2))
}
}

};

const {toDisplayString:_toDisplayString$3,createElementVNode:_createElementVNode$3,createVNode:_createVNode$7,openBlock:_openBlock$9,createElementBlock:_createElementBlock$5} = await importShared('vue');


const _hoisted_1$4 = { class: "v31-glass-card-light v31-task-tile" };
const _hoisted_2$4 = { class: "v31-task-tile__top" };
const _hoisted_3$3 = { class: "v31-task-tile__name" };
const _hoisted_4$3 = { class: "v31-task-tile__schedule" };


const _sfc_main$9 = {
  __name: 'TaskTile',
  props: {
  task: { type: Object, required: true },
},
  setup(__props) {



return (_ctx, _cache) => {
  return (_openBlock$9(), _createElementBlock$5("article", _hoisted_1$4, [
    _createElementVNode$3("div", _hoisted_2$4, [
      _createElementVNode$3("span", _hoisted_3$3, _toDisplayString$3(__props.task.name), 1),
      _createVNode$7(_sfc_main$a, {
        label: __props.task.state || '运行中',
        tone: __props.task.state === '失败' ? 'danger' : 'plain-green'
      }, null, 8, ["label", "tone"])
    ]),
    _createElementVNode$3("span", _hoisted_4$3, _toDisplayString$3(__props.task.schedule), 1)
  ]))
}
}

};

const {unref:_unref$5,createVNode:_createVNode$6,createElementVNode:_createElementVNode$2,renderList:_renderList$1,Fragment:_Fragment$2,openBlock:_openBlock$8,createElementBlock:_createElementBlock$4,createBlock:_createBlock$5,createCommentVNode:_createCommentVNode$6,withCtx:_withCtx$3} = await importShared('vue');


const _hoisted_1$3 = { class: "v31-card-header" };
const _hoisted_2$3 = { class: "v31-card-heading" };
const _hoisted_3$2 = {
  key: 0,
  class: "v31-task-grid"
};
const _hoisted_4$2 = {
  key: 1,
  class: "v31-task-empty"
};


const _sfc_main$8 = {
  __name: 'TaskRuntimePanel',
  props: {
  tasks: { type: Array, default: () => [] },
},
  setup(__props) {



return (_ctx, _cache) => {
  return (_openBlock$8(), _createBlock$5(_sfc_main$h, { "class-name": "v31-task-panel" }, {
    default: _withCtx$3(() => [
      _createElementVNode$2("div", _hoisted_1$3, [
        _createElementVNode$2("div", _hoisted_2$3, [
          _createVNode$6(_sfc_main$k, {
            icon: _unref$5(v31Icons).calendarCheck,
            color: "#60A5FA",
            size: "18"
          }, null, 8, ["icon"]),
          _cache[0] || (_cache[0] = _createElementVNode$2("span", null, "任务运行", -1)),
          _cache[1] || (_cache[1] = _createElementVNode$2("small", null, "当前实时任务", -1))
        ]),
        _createVNode$6(_sfc_main$a, { label: "异常优先" })
      ]),
      (__props.tasks.length)
        ? (_openBlock$8(), _createElementBlock$4("div", _hoisted_3$2, [
            (_openBlock$8(true), _createElementBlock$4(_Fragment$2, null, _renderList$1(__props.tasks, (task) => {
              return (_openBlock$8(), _createBlock$5(_sfc_main$9, {
                key: task.key || task.name,
                task: task
              }, null, 8, ["task"]))
            }), 128))
          ]))
        : (_openBlock$8(), _createElementBlock$4("div", _hoisted_4$2, "当前没有正在运行的任务"))
    ]),
    _: 1
  }))
}
}

};

const {createElementVNode:_createElementVNode$1,renderSlot:_renderSlot,toDisplayString:_toDisplayString$2,normalizeClass:_normalizeClass$4,openBlock:_openBlock$7,createElementBlock:_createElementBlock$3,createCommentVNode:_createCommentVNode$5,renderList:_renderList,Fragment:_Fragment$1,createVNode:_createVNode$5} = await importShared('vue');


const _hoisted_1$2 = ["data-action-presentation", "data-action-size", "data-action-count"];
const _hoisted_2$2 = { class: "v31-quick-actions__header" };
const _hoisted_3$1 = { class: "v31-quick-actions__header-actions" };
const _hoisted_4$1 = ["data-tone"];
const _hoisted_5$1 = { class: "v31-quick-actions__grid" };
const _hoisted_6$1 = ["disabled", "aria-busy", "aria-disabled", "aria-haspopup", "data-state", "data-action-id", "data-action-mode", "data-tone", "data-disabled-reason", "aria-label", "title", "onClick"];
const _hoisted_7$1 = ["data-state"];
const _hoisted_8$1 = { class: "v31-quick-action__label" };

const {computed: computed$6} = await importShared('vue');


const _sfc_main$7 = {
  __name: 'QuickActionsBand',
  props: {
  presentation: {
    type: String,
    default: 'native-icon-grid',
  },
  size: {
    type: String,
    default: 'adaptive',
    validator: value => ['adaptive', 'max'].includes(value),
  },
  actions: {
    type: Object,
    default: () => ({
      items: [],
      runningKey: '',
      runningKeys: [],
      feedbackMessage: '',
      feedbackOk: true,
    }),
  },
},
  emits: ['action', 'operation'],
  setup(__props, { emit: __emit }) {

const props = __props;

const emit = __emit;

const actionView = computed$6(() => ({
  items: Array.isArray(props.actions?.items) ? props.actions.items : [],
  runningKey: String(props.actions?.runningKey || ''),
  runningKeys: Array.isArray(props.actions?.runningKeys) ? props.actions.runningKeys : [],
  feedbackMessage: String(props.actions?.feedbackMessage || ''),
  feedbackOk: props.actions?.feedbackOk !== false,
}));
const visibleActions = computed$6(() => actionView.value.items.filter(action => action?.availability?.visible !== false));
const runningKeySet = computed$6(() => new Set([
  actionView.value.runningKey,
  ...actionView.value.runningKeys,
].map(key => String(key || '')).filter(Boolean)));

function isActionRunning(action) {
  const keys = [action?.id, action?.key, action?.path, action?.apiPath].map(key => String(key || '')).filter(Boolean);
  return action?.availability?.running === true || keys.some(key => runningKeySet.value.has(key))
}

function actionDisabledReason(action) {
  const reason = action?.availability?.disabledReason || action?.disabledReason || '';
  if (reason) return reason
  return isActionRunning(action) ? `${action?.label || '当前动作'}正在执行，请等待完成。` : ''
}

function isActionDisabled(action) {
  return Boolean(actionDisabledReason(action))
}

function actionOperationMode(action) {
  return action?.operation?.mode || 'direct'
}

function actionOpensPanel(action) {
  return actionOperationMode(action) !== 'direct'
}

function actionTitle(action) {
  const reason = actionDisabledReason(action);
  if (reason) return reason
  return actionOpensPanel(action) ? `打开${action.label}操作面板` : `执行${action.label}`
}

function actionAriaLabel(action) {
  const reason = actionDisabledReason(action);
  if (reason) return `${action.label}，${reason}`
  return actionOpensPanel(action) ? `${action.label}，点击后打开操作面板` : `${action.label}，点击后执行`
}

function activateAction(action) {
  emit(actionOpensPanel(action) ? 'operation' : 'action', action);
}

return (_ctx, _cache) => {
  return (_openBlock$7(), _createElementBlock$3("section", {
    class: "v31-quick-actions",
    "data-action-layout": "flat-grid",
    "data-action-presentation": __props.presentation,
    "data-action-size": __props.size,
    "data-action-count": visibleActions.value.length,
    "aria-label": "快捷操作"
  }, [
    _createElementVNode$1("div", _hoisted_2$2, [
      _cache[0] || (_cache[0] = _createElementVNode$1("h2", { class: "v31-quick-actions__title" }, "快捷操作", -1)),
      _createElementVNode$1("div", _hoisted_3$1, [
        _renderSlot(_ctx.$slots, "header-action", {}, undefined, true)
      ]),
      (actionView.value.feedbackMessage)
        ? (_openBlock$7(), _createElementBlock$3("div", {
            key: 0,
            class: _normalizeClass$4(["v31-action-feedback aoa-feedback", { 'v31-action-feedback--bad': !actionView.value.feedbackOk }]),
            "data-tone": actionView.value.feedbackOk ? 'success' : 'error',
            role: "status",
            "aria-live": "polite",
            "aria-atomic": "true"
          }, _toDisplayString$2(actionView.value.feedbackMessage), 11, _hoisted_4$1))
        : _createCommentVNode$5("", true)
    ]),
    _createElementVNode$1("div", _hoisted_5$1, [
      (_openBlock$7(true), _createElementBlock$3(_Fragment$1, null, _renderList(visibleActions.value, (action) => {
        return (_openBlock$7(), _createElementBlock$3("button", {
          key: action.id || action.key || action.path,
          type: "button",
          class: _normalizeClass$4(["v31-quick-action aoa-button aoa-interactive", { 'v31-quick-action--running': isActionRunning(action) }]),
          disabled: isActionDisabled(action),
          "aria-busy": isActionRunning(action) ? 'true' : 'false',
          "aria-disabled": isActionDisabled(action) ? 'true' : 'false',
          "aria-haspopup": actionOpensPanel(action) ? 'dialog' : undefined,
          "data-state": isActionRunning(action) ? 'loading' : isActionDisabled(action) ? 'disabled' : 'idle',
          "data-action-id": action.id || action.path,
          "data-action-mode": actionOperationMode(action),
          "data-tone": action.tone || 'blue',
          "data-disabled-reason": actionDisabledReason(action) || undefined,
          "aria-label": actionAriaLabel(action),
          title: actionTitle(action),
          onClick: $event => (activateAction(action))
        }, [
          _createElementVNode$1("span", {
            class: "v31-quick-action__icon aoa-icon-badge",
            "data-state": isActionRunning(action) ? 'loading' : 'idle'
          }, [
            _createVNode$5(_sfc_main$k, {
              icon: action.icon,
              size: "18"
            }, null, 8, ["icon"])
          ], 8, _hoisted_7$1),
          _createElementVNode$1("span", _hoisted_8$1, _toDisplayString$2(action.label), 1)
        ], 10, _hoisted_6$1))
      }), 128))
    ])
  ], 8, _hoisted_1$2))
}
}

};
const QuickActionsBand = /*#__PURE__*/_export_sfc(_sfc_main$7, [['__scopeId',"data-v-a9d1c3e1"]]);

const {createVNode:_createVNode$4,normalizeClass:_normalizeClass$3,openBlock:_openBlock$6,createElementBlock:_createElementBlock$2} = await importShared('vue');


const {computed: computed$5} = await importShared('vue');


const _sfc_main$6 = {
  __name: 'IconCircle',
  props: {
  icon: { type: String, required: true },
  size: { type: [Number, String], default: 14 },
  tone: { type: String, default: '' },
},
  setup(__props) {

const props = __props;

const variantClass = computed$5(() => props.tone ? `v31-icon-circle--${props.tone}` : '');

return (_ctx, _cache) => {
  return (_openBlock$6(), _createElementBlock$2("span", {
    class: _normalizeClass$3(["v31-icon-circle", variantClass.value])
  }, [
    _createVNode$4(_sfc_main$k, {
      icon: __props.icon,
      size: __props.size
    }, null, 8, ["icon", "size"])
  ], 2))
}
}

};

const {toDisplayString:_toDisplayString$1,createElementVNode:_createElementVNode,unref:_unref$4,createVNode:_createVNode$3,createTextVNode:_createTextVNode,Fragment:_Fragment,openBlock:_openBlock$5,createElementBlock:_createElementBlock$1,createCommentVNode:_createCommentVNode$4,normalizeClass:_normalizeClass$2} = await importShared('vue');


const _hoisted_1$1 = { class: "v31-glass-card v31-fusion-mini" };
const _hoisted_2$1 = { class: "v31-fusion-mini__updated" };
const _hoisted_3 = { class: "v31-fusion-mini__identity" };
const _hoisted_4 = { class: "v31-fusion-mini__name" };
const _hoisted_5 = { class: "v31-fusion-mini__status" };
const _hoisted_6 = { class: "v31-fusion-mini__buttons" };
const _hoisted_7 = ["disabled", "aria-busy", "aria-label", "data-disabled-reason", "title"];
const _hoisted_8 = ["disabled", "aria-busy", "aria-label", "data-disabled-reason", "title"];


const _sfc_main$5 = {
  __name: 'FusionMiniCard',
  props: {
  cardId: { type: [String, Number], default: '' },
  updatedAt: { type: String, default: '' },
  isBuilt: { type: Boolean, default: false },
  enabled: { type: Boolean, default: true },
  refreshing: { type: Boolean, default: false },
  building: { type: Boolean, default: false },
  buildDisabledReason: { type: String, default: '' },
  refreshDisabledReason: { type: String, default: '' },
},
  emits: ['build', 'refresh'],
  setup(__props) {

const props = __props;



function busyReason() {
  if (props.building) return '融合卡建卡正在执行，请等待完成。'
  if (props.refreshing) return '融合卡刷新正在执行，请等待完成。'
  return ''
}

function buildReason() {
  return props.buildDisabledReason || (!props.enabled ? ACTION_DISABLED_REASON.plugin : '') || busyReason()
}

function refreshReason() {
  return props.refreshDisabledReason || (!props.enabled ? ACTION_DISABLED_REASON.plugin : '') || busyReason()
}

return (_ctx, _cache) => {
  return (_openBlock$5(), _createElementBlock$1("article", _hoisted_1$1, [
    _createElementVNode("span", _hoisted_2$1, _toDisplayString$1(__props.enabled ? `更新于 ${__props.updatedAt || '--'}` : '插件已停用'), 1),
    _createVNode$3(_sfc_main$6, {
      icon: _unref$4(v31Icons).cardAccount,
      tone: "blue",
      class: "v31-fusion-mini__icon"
    }, null, 8, ["icon"]),
    _createElementVNode("div", _hoisted_3, [
      _createElementVNode("strong", _hoisted_4, [
        _cache[2] || (_cache[2] = _createTextVNode("融合卡 ", -1)),
        (__props.enabled && __props.cardId)
          ? (_openBlock$5(), _createElementBlock$1(_Fragment, { key: 0 }, [
              _createTextVNode("#" + _toDisplayString$1(__props.cardId), 1)
            ], 64))
          : (__props.enabled)
            ? (_openBlock$5(), _createElementBlock$1(_Fragment, { key: 1 }, [
                _createTextVNode("未建卡")
              ], 64))
            : _createCommentVNode$4("", true)
      ]),
      _createElementVNode("div", _hoisted_5, [
        _cache[3] || (_cache[3] = _createElementVNode("span", null, "状态", -1)),
        _createVNode$3(_sfc_main$a, {
          label: __props.enabled ? (__props.isBuilt ? '已建立' : '未建立') : '已停用',
          tone: __props.enabled && __props.isBuilt ? 'green' : '',
          icon: __props.enabled && __props.isBuilt ? _unref$4(v31Icons).checkCircle : ''
        }, null, 8, ["label", "tone", "icon"])
      ])
    ]),
    _createElementVNode("div", _hoisted_6, [
      _createElementVNode("button", {
        type: "button",
        class: _normalizeClass$2(["v31-pill-button v31-pill-button--compact", { 'v31-status-chip--green': __props.enabled }]),
        disabled: Boolean(buildReason()),
        "aria-busy": __props.building ? 'true' : 'false',
        "aria-label": buildReason() ? `建卡，${buildReason()}` : '创建或更新融合卡',
        "data-disabled-reason": buildReason() || undefined,
        title: buildReason() || '创建或更新融合卡',
        onClick: _cache[0] || (_cache[0] = $event => (_ctx.$emit('build')))
      }, [
        _createVNode$3(_sfc_main$k, {
          icon: _unref$4(v31Icons).cardPlus,
          size: "11"
        }, null, 8, ["icon"]),
        _cache[4] || (_cache[4] = _createTextVNode(" 建卡 ", -1))
      ], 10, _hoisted_7),
      _createElementVNode("button", {
        type: "button",
        class: "v31-pill-button v31-pill-button--compact",
        disabled: Boolean(refreshReason()),
        "aria-busy": __props.refreshing ? 'true' : 'false',
        "aria-label": refreshReason() ? `刷新融合卡，${refreshReason()}` : '立即刷新融合卡',
        "data-disabled-reason": refreshReason() || undefined,
        title: refreshReason() || '立即刷新融合卡',
        "data-fusion-refresh-button": "",
        onClick: _cache[1] || (_cache[1] = $event => (_ctx.$emit('refresh')))
      }, [
        _createVNode$3(_sfc_main$k, {
          icon: _unref$4(v31Icons).refresh,
          size: "11"
        }, null, 8, ["icon"]),
        _createTextVNode(" " + _toDisplayString$1(__props.refreshing ? '刷新中' : '刷新'), 1)
      ], 8, _hoisted_8)
    ])
  ]))
}
}

};

const {createVNode:_createVNode$2,unref:_unref$3,toDisplayString:_toDisplayString,openBlock:_openBlock$4,createElementBlock:_createElementBlock,createCommentVNode:_createCommentVNode$3,mergeProps:_mergeProps$1,createBlock:_createBlock$4,withCtx:_withCtx$2} = await importShared('vue');


const _hoisted_1 = {
  key: 0,
  class: "v31-error"
};
const _hoisted_2 = {
  key: 1,
  class: "v31-loading"
};

const {computed: computed$4,onMounted: onMounted$1,reactive: reactive$1,ref: ref$1} = await importShared('vue');


const _sfc_main$4 = {
  __name: 'DashboardV31',
  props: {
  api: { type: [Object, Function], default: null },
  config: { type: Object, default: () => ({}) },
  allowRefresh: { type: Boolean, default: true },
  surface: { type: String, default: 'dialog' },
  pluginId: { type: String, default: 'Signal' },
},
  emits: ['update:refreshStatus', 'loaded', 'close', 'switch'],
  setup(__props, { emit: __emit }) {

const props = __props;

const emit = __emit;

const { themeName, rootThemeClass } = useAgentOpsTheme();
const dashboardRoot = ref$1(null);
const loading = ref$1(false);
const error = ref$1('');

const dashboard = reactive$1(createDashboardState());
const fusionCard = reactive$1(createFusionCardState());

const themeClass = computed$4(() => {
  return `v31-dashboard-shell--${themeName.value} ${rootThemeClass.value}`
});

const {
  siteChart,
  siteRows,
  siteTrafficTotal,
  siteDateNote,
  sitePieSegments: siteChartPieSegments,
  sitePieStyle: siteChartPieStyle,
  loadSiteChart,
} = useSiteChart(props.api);

const fusionBuildAction = getActionForSurface('create_tg_console_card', 'dashboardFusion');
const fusionRefreshAction = getActionForSurface('run_daily_report', 'dashboardFusion');

const quickActionController = useQuickActionController({
  api: () => props.api,
  pluginId: () => props.pluginId,
  surface: 'dashboard',
  iconSet: v31Icons,
  pluginEnabled: () => dashboard.enabled !== false,
  tasks: () => dashboard.tasks,
  componentStates: () => ({ fusion_notify: fusionCard.enabled !== false }),
  onSuccess: async ({ action }) => {
    if (action?.path === 'run_site_stat') {
      await loadSiteChart();
      const refreshError = String(siteChart.last_error || siteChart.error || '').trim();
      if (refreshError) throw new Error(refreshError)
    }
    if (action?.path === 'create_tg_console_card' || action?.path === 'run_daily_report') {
      await loadFusionCard({ throwOnError: true });
    }
  },
});

const actionRunner = quickActionController.actionRunner;
const fusionBuildAvailability = computed$4(() => quickActionController.getActionAvailability(fusionBuildAction, { surface: 'dashboardFusion' }));
const fusionRefreshAvailability = computed$4(() => quickActionController.getActionAvailability(fusionRefreshAction, { surface: 'dashboardFusion' }));

const {
  kpiItems,
  siteView,
  runtimeTasks,
  actionsView,
  fusionView,
} = useDashboardViewModel({
  dashboard,
  siteChart,
  siteRows,
  siteTrafficTotal,
  siteDateNote,
  sitePieSegments: siteChartPieSegments,
  sitePieStyle: siteChartPieStyle,
  quickActions: quickActionController.actions,
  actionRunner,
  fusionCard,
  icons: v31Icons,
});

async function loadFusionCard({ throwOnError = false } = {}) {
  if (dashboard.enabled === false) {
    resetFusionCardState(fusionCard, false);
    return
  }
  if (!props.api) return
  try {
    const response = await getPluginApiEnvelope(props.api, 'tg_console_status');
    const payload = response?.data || response;
    if (!payload || typeof payload !== 'object') throw new Error('融合通知卡状态刷新返回无效数据')
    applyFusionCardPayload(fusionCard, payload);
    return { ok: true, data: payload }
  } catch (error) {
    if (throwOnError) throw error
    return { ok: false, error }
  }
}

async function loadDashboard() {
  if (!props.api) return
  loading.value = true;
  error.value = '';
  emit('update:refreshStatus', 'loading');
  try {
    const response = await getPluginApiEnvelope(props.api, 'dashboard');
    const payload = response?.data || response;
    if (payload && typeof payload === 'object') {
      applyDashboardPayload(dashboard, payload);
    }
    await Promise.all([loadSiteChart(), loadFusionCard(), quickActionController.loadActionContext()]);
    emit('loaded');
    emit('update:refreshStatus', 'success');
  } catch (err) {
    error.value = err?.message || '仪表盘数据加载失败';
    emit('update:refreshStatus', 'error');
  } finally {
    loading.value = false;
  }
}

function handleQuickAction(action) {
  quickActionController.triggerAction(action);
}

function handleFusionBuild() {
  actionRunner.runAction(fusionBuildAction);
}

function handleFusionRefresh() {
  actionRunner.runAction(fusionRefreshAction);
}

function switchPluginAppNav(navKey) {
  if (typeof window === 'undefined') return false
  const rootElement = dashboardRoot.value?.$el ?? dashboardRoot.value;
  if (rootElement?.closest?.('[role="dialog"], .v-dialog, .v-overlay')) return false
  const pluginAppPrefix = `#/plugin-app/${props.pluginId}/`;
  if (!window.location.hash.startsWith(pluginAppPrefix)) return false
  window.location.hash = `${pluginAppPrefix}${navKey}`;
  return true
}

function openSettings() {
  if (switchPluginAppNav('config')) return
  emit('switch');
}

onMounted$1(loadDashboard);

return (_ctx, _cache) => {
  return (_openBlock$4(), _createBlock$4(_sfc_main$l, {
    ref_key: "dashboardRoot",
    ref: dashboardRoot,
    surface: __props.surface,
    "theme-class": themeClass.value
  }, {
    toolbar: _withCtx$2(() => [
      _createVNode$2(_sfc_main$i, {
        loading: loading.value,
        onRefresh: loadDashboard,
        onSettings: openSettings
      }, null, 8, ["loading"])
    ]),
    metrics: _withCtx$2(() => [
      _createVNode$2(_sfc_main$f, { items: _unref$3(kpiItems) }, null, 8, ["items"])
    ]),
    "core-primary": _withCtx$2(() => [
      _createVNode$2(SiteDataPanel, {
        site: _unref$3(siteView),
        loading: loading.value,
        error: error.value
      }, null, 8, ["site", "loading", "error"])
    ]),
    "core-secondary": _withCtx$2(() => [
      _createVNode$2(_sfc_main$8, { tasks: _unref$3(runtimeTasks) }, null, 8, ["tasks"])
    ]),
    "bottom-primary": _withCtx$2(() => [
      _createVNode$2(QuickActionsBand, {
        presentation: "native-icon-grid",
        size: "max",
        actions: _unref$3(actionsView),
        onAction: handleQuickAction,
        onOperation: handleQuickAction
      }, null, 8, ["actions"])
    ]),
    "bottom-secondary": _withCtx$2(() => [
      _createVNode$2(_sfc_main$5, {
        "card-id": _unref$3(fusionView).cardId,
        "updated-at": _unref$3(fusionView).updatedAt,
        "is-built": _unref$3(fusionView).isBuilt,
        enabled: _unref$3(fusionView).enabled,
        "build-disabled-reason": fusionBuildAvailability.value.disabledReason,
        "refresh-disabled-reason": fusionRefreshAvailability.value.disabledReason,
        refreshing: _unref$3(actionRunner).isActionRunning(_unref$3(fusionRefreshAction)),
        building: _unref$3(actionRunner).isActionRunning(_unref$3(fusionBuildAction)),
        onBuild: handleFusionBuild,
        onRefresh: handleFusionRefresh
      }, null, 8, ["card-id", "updated-at", "is-built", "enabled", "build-disabled-reason", "refresh-disabled-reason", "refreshing", "building"])
    ]),
    status: _withCtx$2(() => [
      (error.value)
        ? (_openBlock$4(), _createElementBlock("div", _hoisted_1, _toDisplayString(error.value), 1))
        : (loading.value)
          ? (_openBlock$4(), _createElementBlock("div", _hoisted_2, "正在刷新仪表盘..."))
          : _createCommentVNode$3("", true)
    ]),
    overlay: _withCtx$2(() => [
      (_unref$3(quickActionController).operationSpec.value)
        ? (_openBlock$4(), _createBlock$4(ActionOperationPanel, _mergeProps$1({ key: 0 }, _unref$3(quickActionController).operationSpec.value, {
            open: "",
            "theme-class": _unref$3(rootThemeClass),
            busy: _unref$3(quickActionController).operationBusy.value,
            onCancel: _unref$3(quickActionController).cancelOperation,
            onConfirm: _unref$3(quickActionController).confirmOperation
          }), null, 16, ["theme-class", "busy", "onCancel", "onConfirm"]))
        : _createCommentVNode$3("", true)
    ]),
    _: 1
  }, 8, ["surface", "theme-class"]))
}
}

};

const SIGNAL_PLUGIN_ID = 'Signal';
const MP_FREE_DASHBOARD_EXPOSE = 'Dashboard';
const MP_FREE_DASHBOARD_SURFACE = 'mp-widget';
const MP_FREE_QUICK_ACTION_SURFACE = 'mpWidget';
const MP_FREE_MODULE_CONTRACT = 'signal-mp-free-dashboard/v1';

function normalizedText(value) {
  return String(value ?? '').trim()
}

function resolveMpFreeHostPluginId(config, fallbackPluginId = SIGNAL_PLUGIN_ID) {
  return normalizedText(config?.id) || normalizedText(fallbackPluginId) || SIGNAL_PLUGIN_ID
}

function resolveMpFreeModuleIdentity(config, fallbackPluginId = SIGNAL_PLUGIN_ID, widget = 'site') {
  const attrs = config?.attrs && typeof config.attrs === 'object' ? config.attrs : {};
  const declared = attrs.moduleIdentity && typeof attrs.moduleIdentity === 'object'
    ? attrs.moduleIdentity
    : {};
  const hostPluginId = resolveMpFreeHostPluginId(config, fallbackPluginId);
  const expectedWidget = normalizedText(widget) || 'site';
  const identity = {
    hostPluginId,
    pluginId: normalizedText(declared.pluginId) || hostPluginId,
    expose: normalizedText(declared.expose) || MP_FREE_DASHBOARD_EXPOSE,
    surface: normalizedText(declared.surface) || normalizedText(attrs.surface) || MP_FREE_DASHBOARD_SURFACE,
    contract: normalizedText(declared.contract) || MP_FREE_MODULE_CONTRACT,
    widget: normalizedText(declared.widget) || expectedWidget,
    declared: Object.keys(declared).length > 0,
  };
  identity.valid = (
    identity.hostPluginId === SIGNAL_PLUGIN_ID &&
    identity.pluginId === SIGNAL_PLUGIN_ID &&
    identity.expose === MP_FREE_DASHBOARD_EXPOSE &&
    identity.surface === MP_FREE_DASHBOARD_SURFACE &&
    identity.contract === MP_FREE_MODULE_CONTRACT &&
    identity.widget === expectedWidget
  );
  return Object.freeze(identity)
}

const {reactive,ref} = await importShared('vue');

const mpFreeQuickActions = createV31QuickActions(v31Icons, MP_FREE_QUICK_ACTION_SURFACE);

function useDashboardFreeData(api) {
  const loading = ref(false);
  const error = ref('');
  const dashboard = reactive(createDashboardState());

  const {
    siteChart,
    siteRows,
    siteTrafficTotal,
    siteDateNote,
    sitePieSegments: siteChartPieSegments,
    sitePieStyle: siteChartPieStyle,
    loadSiteChart,
  } = useSiteChart(api);

  const actionController = useQuickActionController({
    api: () => api,
    surface: MP_FREE_QUICK_ACTION_SURFACE,
    iconSet: v31Icons,
    actions: mpFreeQuickActions,
    pluginEnabled: () => dashboard.enabled !== false,
    tasks: () => dashboard.tasks,
    onSuccess: async ({ action }) => {
      if (action?.path === 'run_site_stat') {
        await loadSiteChart();
        const refreshError = String(siteChart.last_error || siteChart.error || '').trim();
        if (refreshError) throw new Error(refreshError)
      }
    },
  });
  const actionRunner = actionController.actionRunner;
  const viewModel = useDashboardViewModel({
    dashboard,
    siteChart,
    siteRows,
    siteTrafficTotal,
    siteDateNote,
    sitePieSegments: siteChartPieSegments,
    sitePieStyle: siteChartPieStyle,
    quickActions: actionController.actions,
    actionRunner,
    icons: v31Icons,
  });

  async function loadDashboard() {
    if (!api) return
    loading.value = true;
    error.value = '';
    try {
      const response = await getPluginApiEnvelope(api, 'dashboard');
      const payload = response?.data || response;
      if (payload && typeof payload === 'object') {
        applyDashboardPayload(dashboard, payload);
      }
      await Promise.all([loadSiteChart(), actionController.loadActionContext()]);
    } catch (err) {
      error.value = err?.message || '仪表盘数据加载失败';
    } finally {
      loading.value = false;
    }
  }

  return {
    loading,
    error,
    dashboard,
    siteChart,
    ...viewModel,
    actionRunner,
    actionController,
    loadDashboard,
  }
}

const {unref:_unref$2,createVNode:_createVNode$1,resolveComponent:_resolveComponent$1,withCtx:_withCtx$1,openBlock:_openBlock$3,createBlock:_createBlock$3,createCommentVNode:_createCommentVNode$2,normalizeClass:_normalizeClass$1} = await importShared('vue');


const {computed: computed$3} = await importShared('vue');


const _sfc_main$3 = {
  __name: 'MpSiteDataWidget',
  props: {
  data: { type: Object, required: true },
  frame: { type: Object, default: () => ({}) },
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
  allowRefresh: { type: Boolean, default: true },
},
  emits: ['refresh'],
  setup(__props) {

const props = __props;



const { rootThemeClass } = useAgentOpsTheme();
const siteView = computed$3(() => props.data.siteView?.value || props.data.siteView || {});
const frameVariant = computed$3(() => props.frame?.variant || 'mp-native');
const frameDensity = computed$3(() => props.frame?.density || 'comfortable');

return (_ctx, _cache) => {
  const _component_VBtn = _resolveComponent$1("VBtn");
  const _component_VCard = _resolveComponent$1("VCard");

  return (_openBlock$3(), _createBlock$3(_component_VCard, {
    class: _normalizeClass$1(["aoa-mp-free-widget aoa-mp-native-card aoa-root dashboard-summary-card dashboard-grid-fill", _unref$2(rootThemeClass)]),
    elevation: "0",
    rounded: "lg",
    "data-free-widget": "site",
    "data-mp-frame-component": "site",
    "data-module-root-is-frame": "true",
    "data-mp-frame-variant": frameVariant.value,
    "data-mp-frame-density": frameDensity.value,
    "data-loading": __props.loading ? 'true' : 'false',
    "data-error": __props.error ? 'true' : 'false'
  }, {
    default: _withCtx$1(() => [
      _createVNode$1(SiteDataPanel, {
        class: "aoa-finalized-site-content aoa-mp-site-data-content",
        site: siteView.value,
        loading: __props.loading,
        error: __props.error,
        "native-content": ""
      }, {
        "header-action": _withCtx$1(() => [
          (__props.allowRefresh)
            ? (_openBlock$3(), _createBlock$3(_component_VBtn, {
                key: 0,
                class: "aoa-mp-site-refresh dashboard-grid-no-drag",
                icon: "",
                variant: "text",
                size: "small",
                loading: __props.loading,
                disabled: __props.loading,
                "aria-label": "刷新站点数据",
                "data-site-widget-refresh": "",
                onClick: _cache[0] || (_cache[0] = $event => (_ctx.$emit('refresh')))
              }, {
                default: _withCtx$1(() => [
                  _createVNode$1(_sfc_main$k, {
                    icon: _unref$2(v31Icons).refresh,
                    size: 16
                  }, null, 8, ["icon"])
                ]),
                _: 1
              }, 8, ["loading", "disabled"]))
            : _createCommentVNode$2("", true)
        ]),
        _: 1
      }, 8, ["site", "loading", "error"])
    ]),
    _: 1
  }, 8, ["class", "data-mp-frame-variant", "data-mp-frame-density", "data-loading", "data-error"]))
}
}

};
const MpSiteDataWidget = /*#__PURE__*/_export_sfc(_sfc_main$3, [['__scopeId',"data-v-dc9702d7"]]);

const {unref:_unref$1,createVNode:_createVNode,resolveComponent:_resolveComponent,withCtx:_withCtx,openBlock:_openBlock$2,createBlock:_createBlock$2,createCommentVNode:_createCommentVNode$1,mergeProps:_mergeProps,normalizeClass:_normalizeClass} = await importShared('vue');


const {computed: computed$2} = await importShared('vue');


const _sfc_main$2 = {
  __name: 'MpQuickActionsWidget',
  props: {
  data: { type: Object, required: true },
  frame: { type: Object, default: () => ({}) },
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
  allowRefresh: { type: Boolean, default: true },
},
  emits: ['refresh'],
  setup(__props) {

const props = __props;



const { rootThemeClass } = useAgentOpsTheme();
const actionsView = computed$2(() => props.data.actionsView?.value || props.data.actionsView || { items: [], groups: [] });
const actionController = computed$2(() => props.data.actionController || {});
const frameVariant = computed$2(() => props.frame?.variant || 'mp-native');
const frameDensity = computed$2(() => props.frame?.density || 'compact');
const actionOperationSpec = computed$2(() => actionController.value.operationSpec?.value || null);
const actionOperationBusy = computed$2(() => actionController.value.operationBusy?.value === true);

function triggerAction(action) {
  return actionController.value.triggerAction?.(action)
}

return (_ctx, _cache) => {
  const _component_VBtn = _resolveComponent("VBtn");
  const _component_VCard = _resolveComponent("VCard");

  return (_openBlock$2(), _createBlock$2(_component_VCard, {
    class: _normalizeClass(["aoa-mp-free-widget aoa-mp-native-card aoa-root dashboard-summary-card dashboard-grid-fill", _unref$1(rootThemeClass)]),
    elevation: "0",
    rounded: "lg",
    "data-free-widget": "actions",
    "data-mp-frame-component": "actions",
    "data-module-root-is-frame": "true",
    "data-action-surface": _unref$1(MP_FREE_QUICK_ACTION_SURFACE),
    "data-mp-frame-variant": frameVariant.value,
    "data-mp-frame-density": frameDensity.value,
    "data-loading": __props.loading ? 'true' : 'false',
    "data-error": __props.error ? 'true' : 'false'
  }, {
    default: _withCtx(() => [
      _createVNode(QuickActionsBand, {
        class: "aoa-finalized-actions-content",
        presentation: "native-icon-grid",
        size: "adaptive",
        actions: actionsView.value,
        onAction: triggerAction,
        onOperation: triggerAction
      }, {
        "header-action": _withCtx(() => [
          (__props.allowRefresh)
            ? (_openBlock$2(), _createBlock$2(_component_VBtn, {
                key: 0,
                class: "aoa-mp-actions-refresh dashboard-grid-no-drag",
                icon: "",
                variant: "text",
                size: "small",
                loading: __props.loading,
                disabled: __props.loading,
                "aria-label": "刷新快捷操作",
                "data-actions-widget-refresh": "",
                onClick: _cache[0] || (_cache[0] = $event => (_ctx.$emit('refresh')))
              }, {
                default: _withCtx(() => [
                  _createVNode(_sfc_main$k, {
                    icon: _unref$1(v31Icons).refresh,
                    size: 16
                  }, null, 8, ["icon"])
                ]),
                _: 1
              }, 8, ["loading", "disabled"]))
            : _createCommentVNode$1("", true)
        ]),
        _: 1
      }, 8, ["actions"]),
      (actionOperationSpec.value)
        ? (_openBlock$2(), _createBlock$2(ActionOperationPanel, _mergeProps({ key: 0 }, actionOperationSpec.value, {
            open: "",
            "theme-class": _unref$1(rootThemeClass),
            busy: actionOperationBusy.value,
            onCancel: _cache[1] || (_cache[1] = $event => (actionController.value.cancelOperation?.())),
            onConfirm: _cache[2] || (_cache[2] = $event => (actionController.value.confirmOperation?.()))
          }), null, 16, ["theme-class", "busy"]))
        : _createCommentVNode$1("", true)
    ]),
    _: 1
  }, 8, ["class", "data-action-surface", "data-mp-frame-variant", "data-mp-frame-density", "data-loading", "data-error"]))
}
}

};
const MpQuickActionsWidget = /*#__PURE__*/_export_sfc(_sfc_main$2, [['__scopeId',"data-v-b19a6676"]]);

const {unref:_unref,resolveDynamicComponent:_resolveDynamicComponent,openBlock:_openBlock$1,createBlock:_createBlock$1} = await importShared('vue');


const {computed: computed$1,onMounted} = await importShared('vue');

// AOA-HOST-CONSTRAINT: MoviePilot free-widget hosts own the visible outer frame.
// This adapter selects one content module and passes the host frame through unchanged.

const _sfc_main$1 = {
  __name: 'MpFreeDashboardRenderer',
  props: {
  api: { type: [Object, Function], default: null },
  config: { type: Object, default: () => ({}) },
  allowRefresh: { type: Boolean, default: true },
  surface: { type: String, default: 'mp-widget' },
  pluginId: { type: String, default: 'Signal' },
},
  emits: ['update:refreshStatus', 'loaded'],
  setup(__props, { emit: __emit }) {

const props = __props;

const emit = __emit;

const freeData = useDashboardFreeData(props.api);

const requestedWidget = computed$1(() => {
  const attrs = props.config?.attrs || {};
  const explicit = attrs.component || props.config?.component;
  if (explicit) return String(explicit)
  const components = attrs.components || props.config?.components || {};
  const firstEnabled = Object.entries(components).find(([, enabled]) => enabled);
  return firstEnabled?.[0] || 'site'
});

const widget = computed$1(() => {
  if (['site', 'actions'].includes(requestedWidget.value)) return requestedWidget.value
  return 'site'
});

const moduleIdentity = computed$1(() => (
  resolveMpFreeModuleIdentity(props.config, props.pluginId, widget.value)
));

const widgetFrame = computed$1(() => {
  const attrs = props.config?.attrs || {};
  return attrs.frame || {
    variant: 'mp-native',
    surface: 'dashboard-widget',
    density: widget.value === 'site' ? 'comfortable' : 'compact',
    radius: 'var(--app-surface-radius)',
    border: 'var(--app-surface-border)',
    shadow: 'var(--app-surface-shadow)',
    transparentOpacity: 'var(--transparent-opacity)',
    transparentBlur: 'var(--transparent-blur)',
  }
});

const fallbackMessage = computed$1(() => (
  requestedWidget.value === widget.value ? '' : `未知组件 ${requestedWidget.value}，已显示站点数据。`
));

const moduleIdentityError = computed$1(() => (
  moduleIdentity.value.valid
    ? ''
    : `模块身份不匹配：${moduleIdentity.value.hostPluginId}/${moduleIdentity.value.expose}/${moduleIdentity.value.widget}`
));

const currentComponent = computed$1(() => ({
  site: MpSiteDataWidget,
  actions: MpQuickActionsWidget,
}[widget.value] || MpSiteDataWidget));

async function refreshWidget() {
  emit('update:refreshStatus', 'loading');
  await freeData.loadDashboard();
  const status = freeData.error.value ? 'error' : 'success';
  emit('update:refreshStatus', status);
  return status === 'success'
}

onMounted(async () => {
  await refreshWidget();
  emit('loaded');
});

return (_ctx, _cache) => {
  return (_openBlock$1(), _createBlock$1(_resolveDynamicComponent(currentComponent.value), {
    key: `${moduleIdentity.value.contract}:${moduleIdentity.value.hostPluginId}:${moduleIdentity.value.widget}`,
    data: _unref(freeData),
    frame: widgetFrame.value,
    loading: _unref(freeData).loading.value,
    error: _unref(freeData).error.value || moduleIdentityError.value || fallbackMessage.value,
    "allow-refresh": __props.allowRefresh,
    "data-mp-module-host-plugin": moduleIdentity.value.hostPluginId,
    "data-mp-module-plugin": moduleIdentity.value.pluginId,
    "data-mp-module-expose": moduleIdentity.value.expose,
    "data-mp-module-surface": moduleIdentity.value.surface,
    "data-mp-module-contract": moduleIdentity.value.contract,
    "data-mp-module-widget": moduleIdentity.value.widget,
    "data-mp-module-identity-declared": moduleIdentity.value.declared ? 'true' : 'false',
    "data-mp-module-identity-valid": moduleIdentity.value.valid ? 'true' : 'false',
    onRefresh: refreshWidget
  }, null, 40, ["data", "frame", "loading", "error", "allow-refresh", "data-mp-module-host-plugin", "data-mp-module-plugin", "data-mp-module-expose", "data-mp-module-surface", "data-mp-module-contract", "data-mp-module-widget", "data-mp-module-identity-declared", "data-mp-module-identity-valid"]))
}
}

};

const {openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode} = await importShared('vue');


const {computed} = await importShared('vue');


const _sfc_main = {
  __name: 'Dashboard',
  props: {
  api: { type: [Object, Function], default: null },
  config: { type: Object, default: () => ({}) },
  allowRefresh: { type: Boolean, default: true },
  surface: { type: String, default: 'dialog' },
  pluginId: { type: String, default: 'Signal' },
},
  emits: ['update:refreshStatus', 'loaded', 'close', 'switch'],
  setup(__props, { emit: __emit }) {

const props = __props;

const emit = __emit;

const effectiveSurface = computed(() => {
  const surface = props.config?.attrs?.surface ?? props.config?.surface ?? props.surface;
  return String(surface || 'dialog').trim().toLowerCase()
});

const isMpFreeWidget = computed(() => effectiveSurface.value === 'mp-widget');
const effectivePluginId = computed(() => resolveMpFreeHostPluginId(props.config, props.pluginId));

return (_ctx, _cache) => {
  return (isMpFreeWidget.value)
    ? (_openBlock(), _createBlock(_sfc_main$1, {
        key: 0,
        api: __props.api,
        config: __props.config,
        "allow-refresh": __props.allowRefresh,
        surface: "mp-widget",
        "plugin-id": effectivePluginId.value,
        "onUpdate:refreshStatus": _cache[0] || (_cache[0] = value => emit('update:refreshStatus', value)),
        onLoaded: _cache[1] || (_cache[1] = $event => (emit('loaded')))
      }, null, 8, ["api", "config", "allow-refresh", "plugin-id"]))
    : (_openBlock(), _createBlock(_sfc_main$4, {
        key: 1,
        api: __props.api,
        config: __props.config,
        "allow-refresh": __props.allowRefresh,
        surface: effectiveSurface.value,
        "plugin-id": effectivePluginId.value,
        "onUpdate:refreshStatus": _cache[2] || (_cache[2] = value => emit('update:refreshStatus', value)),
        onLoaded: _cache[3] || (_cache[3] = $event => (emit('loaded'))),
        onClose: _cache[4] || (_cache[4] = $event => (emit('close'))),
        onSwitch: _cache[5] || (_cache[5] = $event => (emit('switch')))
      }, null, 8, ["api", "config", "allow-refresh", "surface", "plugin-id"]))
}
}

};

export { _sfc_main as default };
