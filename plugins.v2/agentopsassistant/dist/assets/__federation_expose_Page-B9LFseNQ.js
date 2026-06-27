import { importShared } from './__federation_fn_import-JrT3xvdd.js';
import { _ as _export_sfc, g as getPluginApi, b as getPluginApiRaw, p as postPluginApi, a as actionMessageFromResponse } from './_plugin-vue_export-helper-DVCctbmq.js';

// Utilities
const {getCurrentInstance:_getCurrentInstance} = await importShared('vue');
function getCurrentInstance(name, message) {
  const vm = _getCurrentInstance();
  if (!vm) {
    throw new Error(`[Vuetify] ${name} ${'must be called from inside a setup function'}`);
  }
  return vm;
}

// Utilities
const {computed: computed$1,inject,provide,ref: ref$1,watch,watchEffect} = await importShared('vue');
const ThemeSymbol = Symbol.for('vuetify:theme');
function useTheme() {
  getCurrentInstance('useTheme');
  const theme = inject(ThemeSymbol, null);
  if (!theme) throw new Error('Could not find Vuetify theme injection');
  return theme;
}

const {resolveComponent:_resolveComponent,createVNode:_createVNode,createElementVNode:_createElementVNode,toDisplayString:_toDisplayString,createTextVNode:_createTextVNode,withCtx:_withCtx,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,normalizeClass:_normalizeClass,renderList:_renderList,Fragment:_Fragment,createElementBlock:_createElementBlock,normalizeStyle:_normalizeStyle} = await importShared('vue');


const _hoisted_1 = { class: "agentops-toolbar" };
const _hoisted_2 = { class: "brand" };
const _hoisted_3 = { class: "brand-mark" };
const _hoisted_4 = { class: "dashboard-canvas" };
const _hoisted_5 = { class: "alert-top" };
const _hoisted_6 = { class: "alert-icon" };
const _hoisted_7 = { class: "alert-copy" };
const _hoisted_8 = { class: "alert-line" };
const _hoisted_9 = { class: "metrics-panel" };
const _hoisted_10 = { class: "metric-symbol" };
const _hoisted_11 = { class: "metric-copy" };
const _hoisted_12 = { class: "panel site-panel" };
const _hoisted_13 = { class: "panel-head" };
const _hoisted_14 = { class: "panel-icon panel-icon--cyan" };
const _hoisted_15 = { class: "panel-note" };
const _hoisted_16 = {
  key: 0,
  class: "site-body"
};
const _hoisted_17 = { class: "donut-zone" };
const _hoisted_18 = { class: "donut-core" };
const _hoisted_19 = { class: "site-data" };
const _hoisted_20 = { class: "site-stats" };
const _hoisted_21 = { class: "site-stat" };
const _hoisted_22 = { class: "site-stat" };
const _hoisted_23 = { class: "site-stat" };
const _hoisted_24 = { class: "site-list site-legend" };
const _hoisted_25 = { class: "site-card-head" };
const _hoisted_26 = { class: "site-table-name" };
const _hoisted_27 = { class: "site-name" };
const _hoisted_28 = { class: "site-percent" };
const _hoisted_29 = { class: "site-card-metrics" };
const _hoisted_30 = { class: "site-row-cell site-upload" };
const _hoisted_31 = { class: "site-row-cell site-download" };
const _hoisted_32 = {
  key: 1,
  class: "site-empty-state"
};
const _hoisted_33 = { class: "site-empty-main" };
const _hoisted_34 = { class: "site-empty-icon" };
const _hoisted_35 = { class: "panel command-panel action-panel" };
const _hoisted_36 = { class: "panel-head command-head" };
const _hoisted_37 = { class: "panel-icon panel-icon--cyan" };
const _hoisted_38 = { class: "panel-note" };
const _hoisted_39 = { class: "command-body action-scroll" };
const _hoisted_40 = {
  class: "command-group command-quick-card",
  "aria-label": "融合通知快捷操作"
};
const _hoisted_41 = { class: "command-quick-buttons" };
const _hoisted_42 = { class: "command-quick-label" };
const _hoisted_43 = { class: "group-head" };
const _hoisted_44 = { class: "cmd-grid action-buttons" };
const _hoisted_45 = { class: "action-btn-label" };
const _hoisted_46 = { class: "panel download-panel" };
const _hoisted_47 = { class: "panel-head" };
const _hoisted_48 = { class: "panel-icon panel-icon--blue" };
const _hoisted_49 = {
  key: 0,
  class: "download-body"
};
const _hoisted_50 = {
  key: 1,
  class: "download-body download-body--empty"
};
const _hoisted_51 = { class: "downloader-card downloader-card--empty" };
const _hoisted_52 = {
  key: 0,
  class: "downloader-card downloader-card--empty downloader-card--ghost"
};
const _hoisted_53 = { class: "panel runtime-panel" };
const _hoisted_54 = { class: "panel-head" };
const _hoisted_55 = { class: "panel-icon panel-icon--cyan" };
const _hoisted_56 = {
  key: 1,
  class: "runtime-track task-grid"
};
const _hoisted_57 = { class: "module-top" };
const _hoisted_58 = { class: "module-title" };
const _hoisted_59 = { class: "module-note" };
const _hoisted_60 = {
  key: 0,
  class: "module module--empty"
};

const {ref,reactive,computed,onMounted} = await importShared('vue');


const _sfc_main = {
  __name: 'Page',
  props: {
  api: { type: [Object, Function], default: null },
  surface: { type: String, default: 'dialog' },
},
  emits: ['close', 'switch'],
  setup(__props, { emit: __emit }) {

const props = __props;
const emit = __emit;

const loading = ref(true);
const error = ref('');
const actionRunning = ref('');
const actionMessage = ref('');
const actionOk = ref(true);
const vuetifyTheme = useTheme();
const data = reactive({
  enabled: false,
  summary: '',
  tasks: [],
  task_total: 0,
  task_on: 0,
  task_failed: 0,
  health: { time: '', success: null, output: '' },
});

const siteChart = reactive({
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
const downloaders = ref([]);
const downloaderOverviewMessage = ref('');
const dashboardThemeClass = computed(() => {
  const name = String(vuetifyTheme.global.name.value || '').toLowerCase();
  if (name.includes('transparent')) return 'agentops-theme--transparent'
  if (name.includes('light')) return 'agentops-theme--light'
  return ''
});
const isSidebarSurface = computed(() => props.surface === 'sidebar');
const isPluginDisabled = computed(() => !data.enabled);
const actionsDisabled = computed(() => isPluginDisabled.value);

const overallColor = computed(() => {
  if (!data.enabled) return 'muted'
  if (data.task_failed > 0 || data.health.success === false) return 'red'
  return 'green'
});
const overallText = computed(() => {
  if (!data.enabled) return '未启用'
  return '正常'
});
computed(() => {
  if (data.health.success === true) return 'success'
  if (data.health.success === false) return 'error'
  return 'grey'
});
computed(() => {
  if (data.health.success === true) return '通过'
  if (data.health.success === false) return '存在异常'
  return '尚未巡查'
});

async function loadDashboard() {
  loading.value = true;
  error.value = '';
  try {
    const res = await getPluginApi(props.api, 'dashboard');
    Object.assign(data, res || {});
  } catch (err) {
    error.value = err?.message || '仪表盘数据加载失败';
  } finally {
    loading.value = false;
  }
}

function actionComponentEnabled(action) {
  if (!action?.component) return true
  const task = (data.tasks || []).find(item => item?.key === action.component);
  return !!data.enabled && !!task?.enabled
}

function actionComponentDisabledMessage(action) {
  if (!action?.component || actionComponentEnabled(action)) return ''
  const task = (data.tasks || []).find(item => item?.key === action.component);
  return `${task?.name || action.label || '组件'}未启用，手动命令已暂停`
}

async function runAction(action) {
  if (actionRunning.value) return
  if (actionsDisabled.value) {
    actionOk.value = false;
    actionMessage.value = '插件总开关未启用，手动命令已暂停';
    setTimeout(() => { actionMessage.value = ''; }, 5000);
    return
  }
  const disabledMessage = actionComponentDisabledMessage(action);
  if (disabledMessage) {
    actionOk.value = false;
    actionMessage.value = disabledMessage;
    setTimeout(() => { actionMessage.value = ''; }, 5000);
    return
  }
  const path = action.path;
  actionRunning.value = path;
  actionMessage.value = '';
  actionOk.value = true;
  try {
    const res = await postPluginApi(props.api, path);
    const ok = !!res && res.code === 0;
    actionOk.value = ok;
    actionMessage.value = actionMessageFromResponse(res, action.label);
    setTimeout(() => { actionMessage.value = ''; }, 5000);
    if (ok) {
      loadDashboard();
      loadSiteChart();
      loadDownloaderOverview();
    }
  } catch (err) {
    actionOk.value = false;
    actionMessage.value = actionMessageFromResponse({ code: 1, msg: err?.message }, action.label);
    setTimeout(() => { actionMessage.value = ''; }, 5000);
  } finally {
    actionRunning.value = '';
  }
}

function formatGB(bytes) {
  const n = Number(bytes) || 0;
  const gb = n / (1024 ** 3);
  if (gb >= 1) return gb.toFixed(2) + ' GB'
  return (n / (1024 ** 2)).toFixed(1) + ' MB'
}

const siteRows = computed(() => [...(siteChart.sites || [])].sort((a, b) => ((b.upload || 0) + (b.download || 0)) - ((a.upload || 0) + (a.download || 0))));
const sitePieColors = [
  { color: 'rgba(var(--green), 0.94)', glow: 'rgba(var(--green), 0.28)' },
  { color: 'rgba(var(--cyan), 0.90)', glow: 'rgba(var(--cyan), 0.26)' },
  { color: 'rgba(var(--amber), 0.88)', glow: 'rgba(var(--amber), 0.24)' },
  { color: 'rgba(var(--blue), 0.88)', glow: 'rgba(var(--blue), 0.24)' },
  { color: 'rgba(var(--red), 0.84)', glow: 'rgba(var(--red), 0.22)' },
  { color: 'rgba(var(--violet), 0.86)', glow: 'rgba(var(--violet), 0.23)' },
  { color: 'color-mix(in srgb, rgb(var(--green)) 62%, rgb(var(--blue)))', glow: 'rgba(var(--green), 0.20)' },
  { color: 'color-mix(in srgb, rgb(var(--amber)) 68%, rgb(var(--cyan)))', glow: 'rgba(var(--amber), 0.20)' },
];
const siteTrafficTotal = computed(() => siteRows.value.reduce((sum, site) => sum + (Number(site.upload) || 0) + (Number(site.download) || 0), 0));
const siteDateLabel = computed(() => {
  if (!siteChart.date) return '—'
  return siteChart.basis === 'latest' ? `最近快照 ${siteChart.date}` : siteChart.date
});
const siteDateNote = computed(() => {
  if (!siteChart.date) return '等待统计'
  return siteChart.basis === 'latest' ? '最近快照' : '今天 00:00 后'
});
const sitePieSegments = computed(() => {
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
const sitePieStyle = computed(() => {
  if (!sitePieSegments.value.length) {
    return {
      background: 'conic-gradient(rgba(var(--line), 0.16) 0 82deg, rgba(var(--line), 0.055) 82deg 360deg)',
    }
  }
  const stops = sitePieSegments.value
    .map(item => `${item.color} ${item.start.toFixed(2)}% ${item.end.toFixed(2)}%`)
    .join(', ');
  return { background: `conic-gradient(${stops})` }
});
const siteTableRows = computed(() => sitePieSegments.value.slice(0, 6));
const hasSiteChart = computed(() => !!(siteChart.sites && siteChart.sites.length));
const siteEmptyTitle = computed(() => {
  if (siteChart.last_error || siteChart.error) return '站点统计失败'
  if (siteChart.basis === 'skipped') return '站点统计未启用'
  if (siteChart.data_valid === true) return '暂无站点增量'
  if (siteChart.basis === 'latest') return '暂无今日增量'
  return '等待站点统计'
});
const siteEmptyDesc = computed(() => {
  if (siteChart.last_error || siteChart.error) return siteChart.last_error || siteChart.error
  if (siteChart.message) return siteChart.message
  if (siteChart.basis === 'skipped') return '启用插件和站点统计组件后，可手动刷新生成数据'
  if (siteChart.data_valid === true) return '已刷新但没有可展示的上传/下载增量'
  if (siteChart.basis === 'latest') return '今日基线不足，暂用最近快照等待下一次刷新'
  return '点击立即刷新或站点统计后显示最新可用数据'
});

function sitePercent(value) {
  const total = siteTrafficTotal.value;
  if (!total) return '0%'
  return `${Math.round(((Number(value) || 0) / total) * 100)}%`
}

async function loadSiteChart() {
  try {
    const res = await getPluginApiRaw(props.api, 'site_stat_chart');
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

async function loadDownloaderOverview() {
  try {
    const res = await getPluginApiRaw(props.api, 'downloader_overview');
    const payload = res && typeof res === 'object' && 'data' in res ? res.data : res;
    downloaders.value = (payload && payload.downloaders) || [];
    downloaderOverviewMessage.value = payload?.message || res?.msg || '';
  } catch {
    downloaders.value = [];
    downloaderOverviewMessage.value = '下载器活动获取失败';
  }
}

const healthItems = computed(() => {
  const iconMap = {
    订阅: 'mdi-bell-ring-outline',
    站点: 'mdi-satellite-uplink',
    下载器: 'mdi-download-network-outline',
    本插件任务: 'mdi-puzzle-check-outline',
    数据库: 'mdi-database-check-outline',
    存储空间: 'mdi-harddisk',
    目录权限: 'mdi-folder-check-outline',
  };
  return String(data.health.output || '')
    .split('\n')
    .map(line => line.replace(/^[⦁•\s]+/, '').trim())
    .filter(line => line && !line.includes('状态') && !line.includes('巡查项'))
    .map(line => {
      const ok = !/[⚠❌✖]/.test(line) && !line.includes('异常') && !line.includes('失败');
      const cleaned = line.replace(/[✅⚠️❌✖]/g, '').trim();
      const parts = cleaned.split(/[:：]/);
      const name = (parts.shift() || '巡查项').trim();
      const detail = (parts.join('：') || '无更多信息').trim();
      const detailRows = detail.split(/[；;]/).map(v => v.trim()).filter(Boolean);
      return { name, detail, detailRows, ok, color: ok ? 'success' : 'error', icon: iconMap[name] || 'mdi-check-decagram-outline' }
    })
    .sort((a, b) => Number(a.ok) - Number(b.ok))
});

function isTaskBad(task) {
  if (!isTaskOn(task)) return false
  return task?.color === 'error' || /失败|异常|错误/.test(String(task?.state || ''))
}

function isTaskOn(task) {
  return !!data.enabled && !!task?.enabled
}

const taskCards = computed(() => [...(data.tasks || [])].sort((a, b) => {
  const aw = isTaskBad(a) ? 0 : isTaskOn(a) ? 1 : 2;
  const bw = isTaskBad(b) ? 0 : isTaskOn(b) ? 1 : 2;
  return aw - bw
}));

const issueItems = computed(() => {
  if (isPluginDisabled.value) return []
  const healthProblems = healthItems.value.filter(item => !item.ok);
  if (healthProblems.length) return healthProblems
  const taskProblems = taskCards.value
    .filter(isTaskBad)
    .map(task => ({
      name: task.name || '任务异常',
      detail: `${task.state || '异常'}${task.last_time ? `，最近 ${task.last_time}` : ''}`,
      detailRows: [],
      ok: false,
    }));
  if (taskProblems.length) return taskProblems
  return []
});
const issueCount = computed(() => (isPluginDisabled.value ? 0 : Math.max(Number(data.task_failed) || 0, issueItems.value.length)));
const primaryIssue = computed(() => {
  if (isPluginDisabled.value) return { name: '运行状态', detail: '插件当前未启用', detailRows: [], ok: true }
  return issueItems.value[0] || { name: '系统状态', detail: '当前任务和健康巡查未发现阻塞项', detailRows: [], ok: true }
});
const issueTitle = computed(() => {
  if (isPluginDisabled.value) return '插件已停用'
  return issueCount.value > 0 ? `${issueCount.value} 项需要处理` : '运行平稳'
});
const issueDesc = computed(() => {
  if (error.value) return error.value
  if (isPluginDisabled.value) return '插件未启用时不会运行定时任务或业务链路，仪表盘仅展示当前配置快照'
  if (issueCount.value > 0) return `健康巡查发现${primaryIssue.value.name}异常，仪表盘优先展示具体路径和原因`
  return '任务调度与健康巡查处于稳定状态'
});

const lastRunLabel = computed(() => {
  if (data.health.time) return data.health.time.slice(11, 16) || data.health.time
  const last = taskCards.value.find(task => task.last_time)?.last_time;
  return last ? String(last).slice(11, 16) : '—'
});

const metricCards = computed(() => [
  { label: '运行状态', value: overallText.value, icon: 'mdi-check', tone: overallColor.value },
  { label: '启用组件', value: `${data.enabled ? data.task_on : 0} / ${data.task_total}`, icon: 'mdi-layers-triple-outline', tone: 'blue' },
  { label: '异常组件', value: String(issueCount.value), icon: 'mdi-shield-alert-outline', tone: issueCount.value ? 'red' : 'green' },
  { label: '站点流量', value: formatGB(siteTrafficTotal.value), icon: 'mdi-chart-line-variant', tone: 'amber' },
]);

const quickActions = [
  { path: 'create_tg_console_card', component: '', label: '立即建卡', icon: 'mdi-card-plus-outline', tone: 'green' },
  { path: 'run_daily_report', component: 'daily_report', label: '立即刷新', icon: 'mdi-refresh', tone: 'green' },
];

const actionGroups = [
  {
    group: '汇报与追新',
    icon: 'mdi-newspaper-variant-outline',
    actions: [
      { path: 'run_subscribe_reminder', component: 'subscribe_reminder', label: '订阅追新', icon: 'mdi-bell-badge-outline', tone: 'blue' },
    ],
  },
  {
    group: '站点与下载器',
    icon: 'mdi-download-network-outline',
    actions: [
      { path: 'run_site_stat', component: 'site_stat', label: '站点统计', icon: 'mdi-chart-pie', tone: 'blue' },
      { path: 'run_downloader_tag', component: 'downloader_tag', label: '种子标签', icon: 'mdi-tag-plus-outline', tone: 'cyan' },
      { path: 'run_seed_clean', component: 'seed_clean', label: '自动删种', icon: 'mdi-delete-sweep-outline', tone: 'red' },
    ],
  },
  {
    group: '系统维护',
    icon: 'mdi-cog-outline',
    actions: [
      { path: 'run_backup', component: 'backup', label: '配置备份', icon: 'mdi-database-arrow-up-outline', tone: 'violet' },
      { path: 'run_log_clean', component: 'log_clean', label: '日志清理', icon: 'mdi-broom', tone: 'violet' },
      { path: 'run_health_check', component: 'health_check', label: '健康巡查', icon: 'mdi-heart-pulse', tone: 'green' },
      { path: 'run_mp_update', component: 'mp_update', label: 'MP 更新', icon: 'mdi-update', tone: 'amber' },
    ],
  },
  {
    group: '插件治理',
    icon: 'mdi-puzzle-check-outline',
    actions: [
      { path: 'run_market_update', component: 'market_update', label: '插件更新', icon: 'mdi-cloud-sync-outline', tone: 'amber' },
    ],
  },
];
const actionItems = computed(() => actionGroups.flatMap(group => group.actions));

onMounted(() => {
  loadDashboard();
  loadSiteChart();
  loadDownloaderOverview();
});

return (_ctx, _cache) => {
  const _component_VIcon = _resolveComponent("VIcon");
  const _component_VBtn = _resolveComponent("VBtn");
  const _component_VAlert = _resolveComponent("VAlert");
  const _component_VSkeletonLoader = _resolveComponent("VSkeletonLoader");
  const _component_VCard = _resolveComponent("VCard");

  return (_openBlock(), _createElementBlock("div", {
    class: _normalizeClass(["agentops-dashboard dashboard-shell", [dashboardThemeClass.value, { 'dashboard-shell--sidebar': isSidebarSurface.value }]])
  }, [
    _createVNode(_component_VCard, {
      class: "agentops-frame",
      elevation: "0"
    }, {
      default: _withCtx(() => [
        _createElementVNode("header", _hoisted_1, [
          _createElementVNode("div", _hoisted_2, [
            _createElementVNode("span", _hoisted_3, [
              _createVNode(_component_VIcon, {
                icon: "mdi-view-dashboard-outline",
                size: "20"
              })
            ]),
            _cache[2] || (_cache[2] = _createElementVNode("span", { class: "brand-title" }, "MP 运维助手 · 仪表盘", -1)),
            _createElementVNode("small", null, "最后 " + _toDisplayString(lastRunLabel.value), 1)
          ]),
          _cache[5] || (_cache[5] = _createElementVNode("div", { class: "toolbar-space" }, null, -1)),
          _createVNode(_component_VBtn, {
            size: "small",
            variant: "text",
            class: "top-button top-button--primary text-none",
            loading: loading.value,
            onClick: loadDashboard
          }, {
            default: _withCtx(() => [...(_cache[3] || (_cache[3] = [
              _createTextVNode(" 刷新 ", -1)
            ]))]),
            _: 1
          }, 8, ["loading"]),
          (!isSidebarSurface.value)
            ? (_openBlock(), _createBlock(_component_VBtn, {
                key: 0,
                size: "small",
                variant: "text",
                class: "top-button text-none",
                onClick: _cache[0] || (_cache[0] = $event => (emit('switch')))
              }, {
                default: _withCtx(() => [...(_cache[4] || (_cache[4] = [
                  _createTextVNode("设置", -1)
                ]))]),
                _: 1
              }))
            : _createCommentVNode("", true),
          (!isSidebarSurface.value)
            ? (_openBlock(), _createBlock(_component_VBtn, {
                key: 1,
                size: "small",
                icon: "mdi-close",
                variant: "text",
                class: "top-button top-button--icon",
                onClick: _cache[1] || (_cache[1] = $event => (emit('close')))
              }))
            : _createCommentVNode("", true)
        ]),
        _createElementVNode("section", _hoisted_4, [
          _createElementVNode("article", {
            class: _normalizeClass(["panel alert-panel", { 'alert-panel--ok': issueCount.value === 0 && !error.value && !isPluginDisabled.value, 'alert-panel--idle': isPluginDisabled.value && !error.value }])
          }, [
            _createElementVNode("div", _hoisted_5, [
              _createElementVNode("div", _hoisted_6, [
                _createVNode(_component_VIcon, {
                  icon: isPluginDisabled.value && !error.value ? 'mdi-power-standby' : issueCount.value || error.value ? 'mdi-alert-outline' : 'mdi-shield-check-outline',
                  size: "28"
                }, null, 8, ["icon"])
              ]),
              _createElementVNode("div", _hoisted_7, [
                _createElementVNode("h1", null, _toDisplayString(error.value ? '数据加载失败' : issueTitle.value), 1),
                _createElementVNode("p", null, _toDisplayString(issueDesc.value), 1)
              ])
            ]),
            _createElementVNode("div", _hoisted_8, [
              _createElementVNode("b", null, _toDisplayString(primaryIssue.value.name), 1),
              _createElementVNode("strong", null, _toDisplayString(primaryIssue.value.detail), 1),
              _createElementVNode("span", {
                class: _normalizeClass(["badge", { 'badge--ok': issueCount.value === 0 && !error.value && !isPluginDisabled.value, 'badge--idle': isPluginDisabled.value && !error.value }])
              }, _toDisplayString(error.value ? '异常' : isPluginDisabled.value ? '停用' : issueCount.value ? '异常' : '正常'), 3)
            ])
          ], 2),
          _createElementVNode("section", _hoisted_9, [
            (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(metricCards.value, (metric) => {
              return (_openBlock(), _createElementBlock("article", {
                key: metric.label,
                class: _normalizeClass(["metric-card", `metric-card--${metric.tone}`])
              }, [
                _createElementVNode("div", _hoisted_10, [
                  _createVNode(_component_VIcon, {
                    icon: metric.icon,
                    size: "28"
                  }, null, 8, ["icon"])
                ]),
                _createElementVNode("div", _hoisted_11, [
                  _createElementVNode("p", null, _toDisplayString(metric.label), 1),
                  _createElementVNode("strong", null, _toDisplayString(metric.value), 1)
                ])
              ], 2))
            }), 128))
          ]),
          _createElementVNode("article", _hoisted_12, [
            _createElementVNode("div", _hoisted_13, [
              _createElementVNode("span", _hoisted_14, [
                _createVNode(_component_VIcon, {
                  icon: "mdi-chart-line",
                  size: "20"
                })
              ]),
              _cache[6] || (_cache[6] = _createElementVNode("h2", null, "站点数据统计", -1)),
              _createElementVNode("span", _hoisted_15, _toDisplayString(siteDateNote.value), 1)
            ]),
            (hasSiteChart.value)
              ? (_openBlock(), _createElementBlock("div", _hoisted_16, [
                  _createElementVNode("div", _hoisted_17, [
                    _createElementVNode("div", {
                      class: "donut",
                      style: _normalizeStyle(sitePieStyle.value)
                    }, [
                      _createElementVNode("div", _hoisted_18, [
                        _createElementVNode("strong", null, _toDisplayString(siteRows.value.length), 1),
                        _cache[7] || (_cache[7] = _createElementVNode("span", null, "站点", -1))
                      ])
                    ], 4)
                  ]),
                  _createElementVNode("div", _hoisted_19, [
                    _createElementVNode("div", _hoisted_20, [
                      _createElementVNode("div", _hoisted_21, [
                        _cache[8] || (_cache[8] = _createElementVNode("span", null, "上传增量", -1)),
                        _createElementVNode("strong", null, _toDisplayString(formatGB(siteChart.upload_total)), 1)
                      ]),
                      _createElementVNode("div", _hoisted_22, [
                        _cache[9] || (_cache[9] = _createElementVNode("span", null, "下载增量", -1)),
                        _createElementVNode("strong", null, _toDisplayString(formatGB(siteChart.download_total)), 1)
                      ]),
                      _createElementVNode("div", _hoisted_23, [
                        _cache[10] || (_cache[10] = _createElementVNode("span", null, "统计日期", -1)),
                        _createElementVNode("strong", null, _toDisplayString(siteDateLabel.value), 1)
                      ])
                    ]),
                    _createElementVNode("div", _hoisted_24, [
                      (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(siteTableRows.value, (site) => {
                        return (_openBlock(), _createElementBlock("div", {
                          key: site.name,
                          class: "site-card"
                        }, [
                          _createElementVNode("div", _hoisted_25, [
                            _createElementVNode("span", _hoisted_26, [
                              _createElementVNode("i", {
                                class: "dot",
                                style: _normalizeStyle({ background: site.color, boxShadow: `0 0 8px ${site.glow}` })
                              }, null, 4),
                              _createElementVNode("span", _hoisted_27, _toDisplayString(site.name), 1)
                            ]),
                            _createElementVNode("strong", _hoisted_28, _toDisplayString(sitePercent(site.value)), 1)
                          ]),
                          _createElementVNode("div", _hoisted_29, [
                            _createElementVNode("span", _hoisted_30, "↑ " + _toDisplayString(formatGB(site.upload)), 1),
                            _createElementVNode("span", _hoisted_31, "↓ " + _toDisplayString(formatGB(site.download)), 1)
                          ])
                        ]))
                      }), 128))
                    ])
                  ])
                ]))
              : (_openBlock(), _createElementBlock("div", _hoisted_32, [
                  _createElementVNode("div", _hoisted_33, [
                    _createElementVNode("span", _hoisted_34, [
                      _createVNode(_component_VIcon, {
                        icon: "mdi-chart-pie",
                        size: "19"
                      })
                    ]),
                    _createElementVNode("div", null, [
                      _createElementVNode("strong", null, _toDisplayString(siteEmptyTitle.value), 1),
                      _createElementVNode("span", null, _toDisplayString(siteEmptyDesc.value), 1)
                    ])
                  ]),
                  _cache[11] || (_cache[11] = _createElementVNode("div", { class: "site-empty-stats" }, [
                    _createElementVNode("div", { class: "site-stat" }, [
                      _createElementVNode("span", null, "上传增量"),
                      _createElementVNode("strong", null, "0.0 MB")
                    ]),
                    _createElementVNode("div", { class: "site-stat" }, [
                      _createElementVNode("span", null, "下载增量"),
                      _createElementVNode("strong", null, "0.0 MB")
                    ]),
                    _createElementVNode("div", { class: "site-stat" }, [
                      _createElementVNode("span", null, "统计日期"),
                      _createElementVNode("strong", null, "等待统计")
                    ])
                  ], -1))
                ]))
          ]),
          _createElementVNode("aside", _hoisted_35, [
            _createElementVNode("div", _hoisted_36, [
              _createElementVNode("span", _hoisted_37, [
                _createVNode(_component_VIcon, {
                  icon: "mdi-view-grid-outline",
                  size: "20"
                })
              ]),
              _cache[12] || (_cache[12] = _createElementVNode("h2", null, "命令面板", -1)),
              _createElementVNode("span", _hoisted_38, _toDisplayString(actionItems.value.length) + " 项", 1)
            ]),
            _createElementVNode("div", _hoisted_39, [
              _createElementVNode("section", _hoisted_40, [
                _cache[13] || (_cache[13] = _createElementVNode("div", { class: "command-quick-copy" }, [
                  _createElementVNode("span", null, "融合通知"),
                  _createElementVNode("strong", null, "运维卡快捷操作")
                ], -1)),
                _createElementVNode("div", _hoisted_41, [
                  (_openBlock(), _createElementBlock(_Fragment, null, _renderList(quickActions, (quick) => {
                    return _createVNode(_component_VBtn, {
                      key: quick.path,
                      variant: "text",
                      density: "comfortable",
                      loading: actionRunning.value === quick.path,
                      disabled: actionsDisabled.value || !actionComponentEnabled(quick) || (!!actionRunning.value && actionRunning.value !== quick.path),
                      title: quick.label,
                      class: "command-quick-btn text-none",
                      onClick: $event => (runAction(quick))
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_VIcon, {
                          icon: quick.icon,
                          size: "20"
                        }, null, 8, ["icon"]),
                        _createElementVNode("span", _hoisted_42, _toDisplayString(quick.label), 1)
                      ]),
                      _: 2
                    }, 1032, ["loading", "disabled", "title", "onClick"])
                  }), 64))
                ])
              ]),
              (_openBlock(), _createElementBlock(_Fragment, null, _renderList(actionGroups, (group) => {
                return _createElementVNode("section", {
                  key: group.group,
                  class: "command-group"
                }, [
                  _createElementVNode("div", _hoisted_43, [
                    _createElementVNode("span", null, _toDisplayString(group.group), 1),
                    _createElementVNode("span", null, _toDisplayString(group.actions.length) + " 项", 1)
                  ]),
                  _createElementVNode("div", _hoisted_44, [
                    (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(group.actions, (action) => {
                      return (_openBlock(), _createBlock(_component_VBtn, {
                        key: action.path,
                        variant: "text",
                        density: "comfortable",
                        loading: actionRunning.value === action.path,
                        disabled: actionsDisabled.value || !actionComponentEnabled(action) || (!!actionRunning.value && actionRunning.value !== action.path),
                        title: actionComponentDisabledMessage(action),
                        class: _normalizeClass(["cmd-btn action-btn action-item text-none", [`cmd-btn--${action.tone}`, `action-btn--${action.tone}`]]),
                        onClick: $event => (runAction(action))
                      }, {
                        default: _withCtx(() => [
                          _createVNode(_component_VIcon, {
                            icon: action.icon,
                            size: "16"
                          }, null, 8, ["icon"]),
                          _createElementVNode("span", _hoisted_45, _toDisplayString(action.label), 1)
                        ]),
                        _: 2
                      }, 1032, ["loading", "disabled", "title", "class", "onClick"]))
                    }), 128))
                  ])
                ])
              }), 64))
            ]),
            (actionMessage.value)
              ? (_openBlock(), _createBlock(_component_VAlert, {
                  key: 0,
                  type: actionOk.value ? 'success' : 'error',
                  variant: "tonal",
                  density: "compact",
                  class: "action-message",
                  icon: false,
                  text: actionMessage.value
                }, null, 8, ["type", "text"]))
              : _createCommentVNode("", true)
          ]),
          _createElementVNode("article", _hoisted_46, [
            _createElementVNode("div", _hoisted_47, [
              _createElementVNode("span", _hoisted_48, [
                _createVNode(_component_VIcon, {
                  icon: "mdi-download",
                  size: "20"
                })
              ]),
              _cache[14] || (_cache[14] = _createElementVNode("h2", null, "下载器活动", -1))
            ]),
            (downloaders.value.length)
              ? (_openBlock(), _createElementBlock("div", _hoisted_49, [
                  (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(downloaders.value, (d) => {
                    return (_openBlock(), _createElementBlock("div", {
                      key: d.name,
                      class: "downloader-card"
                    }, [
                      _createElementVNode("div", null, [
                        _createElementVNode("strong", null, _toDisplayString(d.name), 1),
                        _createElementVNode("span", null, "下载中 " + _toDisplayString(d.count) + " 个 ｜ ↓ " + _toDisplayString(formatGB(d.dl_speed)) + "/s ｜ ↑ " + _toDisplayString(formatGB(d.up_speed)) + "/s", 1)
                      ]),
                      _cache[15] || (_cache[15] = _createElementVNode("span", { class: "ok-chip" }, "运行中", -1))
                    ]))
                  }), 128))
                ]))
              : (_openBlock(), _createElementBlock("div", _hoisted_50, [
                  _createElementVNode("div", _hoisted_51, [
                    _createElementVNode("div", null, [
                      _createElementVNode("strong", null, _toDisplayString(downloaderOverviewMessage.value ? '下载器活动已跳过' : '暂无活动下载器'), 1),
                      _createElementVNode("span", null, _toDisplayString(downloaderOverviewMessage.value || '刷新后同步正在下载的任务'), 1)
                    ]),
                    _cache[16] || (_cache[16] = _createElementVNode("span", { class: "ok-chip ok-chip--idle" }, "等待", -1))
                  ]),
                  (!downloaderOverviewMessage.value)
                    ? (_openBlock(), _createElementBlock("div", _hoisted_52, [...(_cache[17] || (_cache[17] = [
                        _createElementVNode("div", null, [
                          _createElementVNode("strong", null, "下载器快照"),
                          _createElementVNode("span", null, "连接后显示实时上下行速度")
                        ], -1),
                        _createElementVNode("span", { class: "ok-chip ok-chip--idle" }, "空闲", -1)
                      ]))]))
                    : _createCommentVNode("", true)
                ]))
          ]),
          _createElementVNode("article", _hoisted_53, [
            _createElementVNode("div", _hoisted_54, [
              _createElementVNode("span", _hoisted_55, [
                _createVNode(_component_VIcon, {
                  icon: "mdi-format-list-bulleted",
                  size: "20"
                })
              ]),
              _cache[18] || (_cache[18] = _createElementVNode("h2", null, "组件运行状况", -1)),
              _cache[19] || (_cache[19] = _createElementVNode("span", { class: "panel-note" }, "异常优先", -1))
            ]),
            (loading.value)
              ? (_openBlock(), _createBlock(_component_VSkeletonLoader, {
                  key: 0,
                  class: "runtime-loader",
                  type: "list-item-two-line@4"
                }))
              : (_openBlock(), _createElementBlock("div", _hoisted_56, [
                  (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(taskCards.value, (task) => {
                    return (_openBlock(), _createElementBlock("div", {
                      key: task.key,
                      class: _normalizeClass(["module task-card", { 'module--bad': isTaskBad(task), 'module--off': !isTaskOn(task) }])
                    }, [
                      _createElementVNode("div", _hoisted_57, [
                        _createElementVNode("i", {
                          class: _normalizeClass(["dot", { red: isTaskBad(task), gray: !isTaskOn(task) }])
                        }, null, 2),
                        _createElementVNode("span", _hoisted_58, _toDisplayString(task.name), 1),
                        _createElementVNode("span", {
                          class: _normalizeClass(["state", { bad: isTaskBad(task), off: !isTaskOn(task) }])
                        }, _toDisplayString(isTaskBad(task) ? '失败' : isTaskOn(task) ? 'ON' : 'OFF'), 3)
                      ]),
                      _createElementVNode("div", _hoisted_59, _toDisplayString(task.next ? `下次 ${task.next}` : task.last_time ? `最近 ${task.last_time}` : '等待调度'), 1)
                    ], 2))
                  }), 128)),
                  (!taskCards.value.length)
                    ? (_openBlock(), _createElementBlock("div", _hoisted_60, [...(_cache[20] || (_cache[20] = [
                        _createElementVNode("div", { class: "module-top" }, [
                          _createElementVNode("i", { class: "dot gray" }),
                          _createElementVNode("span", { class: "module-title" }, "暂无任务"),
                          _createElementVNode("span", { class: "state off" }, "OFF")
                        ], -1),
                        _createElementVNode("div", { class: "module-note" }, "启用配置后显示调度状态", -1)
                      ]))]))
                    : _createCommentVNode("", true)
                ]))
          ])
        ])
      ]),
      _: 1
    })
  ], 2))
}
}

};
const Page = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-5342a647"]]);

export { Page as default };
