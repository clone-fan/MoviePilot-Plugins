import { importShared } from './__federation_fn_import-JrT3xvdd.js';
import { _ as _export_sfc, g as getPluginApi, p as postPluginApi } from './_plugin-vue_export-helper-Dc5i-DQA.js';

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

const {resolveComponent:_resolveComponent,createVNode:_createVNode,createElementVNode:_createElementVNode,toDisplayString:_toDisplayString,createTextVNode:_createTextVNode,withCtx:_withCtx,normalizeClass:_normalizeClass,renderList:_renderList,Fragment:_Fragment,openBlock:_openBlock,createElementBlock:_createElementBlock,normalizeStyle:_normalizeStyle,createCommentVNode:_createCommentVNode,createBlock:_createBlock} = await importShared('vue');


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
const _hoisted_24 = { class: "site-table site-legend" };
const _hoisted_25 = { class: "site-row-cell site-name" };
const _hoisted_26 = { class: "site-row-cell" };
const _hoisted_27 = { class: "site-row-cell" };
const _hoisted_28 = { class: "site-row-cell" };
const _hoisted_29 = {
  key: 1,
  class: "site-body site-body--empty"
};
const _hoisted_30 = { class: "donut-zone" };
const _hoisted_31 = { class: "site-data" };
const _hoisted_32 = { class: "site-table site-table--empty" };
const _hoisted_33 = { class: "site-row-cell site-empty-row" };
const _hoisted_34 = { class: "panel command-panel action-panel" };
const _hoisted_35 = { class: "panel-head command-head" };
const _hoisted_36 = { class: "panel-icon panel-icon--cyan" };
const _hoisted_37 = { class: "panel-note" };
const _hoisted_38 = { class: "command-body action-scroll" };
const _hoisted_39 = { class: "group-head" };
const _hoisted_40 = { class: "cmd-grid action-buttons" };
const _hoisted_41 = { class: "action-btn-label" };
const _hoisted_42 = { class: "panel download-panel" };
const _hoisted_43 = { class: "panel-head" };
const _hoisted_44 = { class: "panel-icon panel-icon--blue" };
const _hoisted_45 = {
  key: 0,
  class: "download-body"
};
const _hoisted_46 = {
  key: 1,
  class: "download-body download-body--empty"
};
const _hoisted_47 = { class: "panel runtime-panel" };
const _hoisted_48 = { class: "panel-head" };
const _hoisted_49 = { class: "panel-icon panel-icon--cyan" };
const _hoisted_50 = {
  key: 1,
  class: "runtime-track task-grid"
};
const _hoisted_51 = { class: "module-top" };
const _hoisted_52 = { class: "module-title" };
const _hoisted_53 = { class: "module-note" };
const _hoisted_54 = {
  key: 0,
  class: "module module--empty"
};

const {ref,reactive,computed,onMounted} = await importShared('vue');


const _sfc_main = {
  __name: 'Page',
  props: { api: { type: [Object, Function], default: null } },
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

const siteChart = reactive({ date: '', basis: 'today', sites: [], upload_total: 0, download_total: 0 });
const downloaders = ref([]);
const dashboardThemeClass = computed(() => {
  const name = String(vuetifyTheme.global.name.value || '').toLowerCase();
  if (name.includes('transparent')) return 'agentops-theme--transparent'
  if (name.includes('light')) return 'agentops-theme--light'
  return ''
});

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

async function runAction(path, label) {
  if (actionRunning.value) return
  actionRunning.value = path;
  actionMessage.value = '';
  actionOk.value = true;
  try {
    const res = await postPluginApi(props.api, path);
    const ok = !res || res.code === 0 || res.code === undefined;
    actionOk.value = ok;
    actionMessage.value = (res && res.msg) || `${label}已${ok ? '完成' : '失败'}`;
    setTimeout(() => { actionMessage.value = ''; }, 5000);
    if (ok) {
      loadDashboard();
      loadSiteChart();
      loadDownloaderOverview();
    }
  } catch (err) {
    actionOk.value = false;
    actionMessage.value = err?.message || `${label}失败`;
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

function sitePercent(value) {
  const total = siteTrafficTotal.value;
  if (!total) return '0%'
  return `${Math.round(((Number(value) || 0) / total) * 100)}%`
}

async function loadSiteChart() {
  try {
    const res = await getPluginApi(props.api, 'site_stat_chart');
    Object.assign(siteChart, res || {});
  } catch {
    /* 无站点数据时静默显示空态 */
  }
}

async function loadDownloaderOverview() {
  try {
    const res = await getPluginApi(props.api, 'downloader_overview');
    downloaders.value = (res && res.downloaders) || [];
  } catch {
    downloaders.value = [];
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
  return task?.color === 'error' || /失败|异常|错误/.test(String(task?.state || ''))
}

const taskCards = computed(() => [...(data.tasks || [])].sort((a, b) => {
  const aw = isTaskBad(a) ? 0 : a.enabled ? 1 : 2;
  const bw = isTaskBad(b) ? 0 : b.enabled ? 1 : 2;
  return aw - bw
}));

const issueItems = computed(() => {
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
  if (!data.enabled) return [{ name: '运行状态', detail: '插件当前未启用', detailRows: [], ok: false }]
  return []
});
const issueCount = computed(() => Math.max(Number(data.task_failed) || 0, issueItems.value.length));
const primaryIssue = computed(() => issueItems.value[0] || { name: '系统状态', detail: '当前任务和健康巡查未发现阻塞项', detailRows: [], ok: true });
const issueTitle = computed(() => issueCount.value > 0 ? `${issueCount.value} 项需要处理` : '运行平稳');
const issueDesc = computed(() => {
  if (error.value) return error.value
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
  { label: '启用组件', value: `${data.task_on} / ${data.task_total}`, icon: 'mdi-layers-triple-outline', tone: 'blue' },
  { label: '异常组件', value: String(issueCount.value), icon: 'mdi-shield-alert-outline', tone: issueCount.value ? 'red' : 'green' },
  { label: '站点流量', value: formatGB(siteTrafficTotal.value), icon: 'mdi-chart-line-variant', tone: 'amber' },
]);

const actionGroups = [
  {
    group: '汇报与追新',
    icon: 'mdi-newspaper-variant-outline',
    actions: [
      { path: 'run_daily_report', label: '每日汇报', icon: 'mdi-send-clock-outline', tone: 'green' },
      { path: 'run_subscribe_reminder', label: '订阅追新', icon: 'mdi-bell-badge-outline', tone: 'blue' },
    ],
  },
  {
    group: '站点与下载器',
    icon: 'mdi-download-network-outline',
    actions: [
      { path: 'run_site_stat', label: '站点统计', icon: 'mdi-chart-pie', tone: 'blue' },
      { path: 'run_downloader_tag', label: '种子标签', icon: 'mdi-tag-plus-outline', tone: 'cyan' },
      { path: 'run_seed_clean', label: '自动删种', icon: 'mdi-delete-sweep-outline', tone: 'red' },
    ],
  },
  {
    group: '系统维护',
    icon: 'mdi-cog-outline',
    actions: [
      { path: 'run_backup', label: '配置备份', icon: 'mdi-database-arrow-up-outline', tone: 'violet' },
      { path: 'run_log_clean', label: '日志清理', icon: 'mdi-broom', tone: 'violet' },
      { path: 'run_health_check', label: '健康巡查', icon: 'mdi-heart-pulse', tone: 'green' },
      { path: 'run_mp_update', label: 'MP 更新', icon: 'mdi-update', tone: 'amber' },
    ],
  },
  {
    group: '插件治理',
    icon: 'mdi-puzzle-check-outline',
    actions: [
      { path: 'run_market_update', label: '插件更新', icon: 'mdi-cloud-sync-outline', tone: 'amber' },
      { path: 'run_plugin_uninstall', label: '插件卸载', icon: 'mdi-puzzle-remove-outline', tone: 'red' },
    ],
  },
];
const actionItems = computed(() => actionGroups.flatMap(group => group.actions));

onMounted(() => { loadDashboard(); loadSiteChart(); loadDownloaderOverview(); });

return (_ctx, _cache) => {
  const _component_VIcon = _resolveComponent("VIcon");
  const _component_VBtn = _resolveComponent("VBtn");
  const _component_VAlert = _resolveComponent("VAlert");
  const _component_VSkeletonLoader = _resolveComponent("VSkeletonLoader");
  const _component_VCard = _resolveComponent("VCard");

  return (_openBlock(), _createElementBlock("div", {
    class: _normalizeClass(["agentops-dashboard dashboard-shell", dashboardThemeClass.value])
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
          _createVNode(_component_VBtn, {
            size: "small",
            variant: "text",
            class: "top-button text-none",
            onClick: _cache[0] || (_cache[0] = $event => (emit('switch')))
          }, {
            default: _withCtx(() => [...(_cache[4] || (_cache[4] = [
              _createTextVNode("设置", -1)
            ]))]),
            _: 1
          }),
          _createVNode(_component_VBtn, {
            size: "small",
            icon: "mdi-close",
            variant: "text",
            class: "top-button top-button--icon",
            onClick: _cache[1] || (_cache[1] = $event => (emit('close')))
          })
        ]),
        _createElementVNode("section", _hoisted_4, [
          _createElementVNode("article", {
            class: _normalizeClass(["panel alert-panel", { 'alert-panel--ok': issueCount.value === 0 && !error.value }])
          }, [
            _createElementVNode("div", _hoisted_5, [
              _createElementVNode("div", _hoisted_6, [
                _createVNode(_component_VIcon, {
                  icon: issueCount.value || error.value ? 'mdi-alert-outline' : 'mdi-shield-check-outline',
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
                class: _normalizeClass(["badge", { 'badge--ok': issueCount.value === 0 && !error.value }])
              }, _toDisplayString(issueCount.value || error.value ? '异常' : '正常'), 3)
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
                      _cache[11] || (_cache[11] = _createElementVNode("div", { class: "th" }, "站点", -1)),
                      _cache[12] || (_cache[12] = _createElementVNode("div", { class: "th" }, "上传", -1)),
                      _cache[13] || (_cache[13] = _createElementVNode("div", { class: "th" }, "下载", -1)),
                      _cache[14] || (_cache[14] = _createElementVNode("div", { class: "th" }, "占比", -1)),
                      (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(siteTableRows.value, (site) => {
                        return (_openBlock(), _createElementBlock(_Fragment, {
                          key: site.name
                        }, [
                          _createElementVNode("div", _hoisted_25, [
                            _createElementVNode("i", {
                              class: "dot",
                              style: _normalizeStyle({ background: site.color, boxShadow: `0 0 8px ${site.glow}` })
                            }, null, 4),
                            _createTextVNode(_toDisplayString(site.name), 1)
                          ]),
                          _createElementVNode("div", _hoisted_26, "↑ " + _toDisplayString(formatGB(site.upload)), 1),
                          _createElementVNode("div", _hoisted_27, "↓ " + _toDisplayString(formatGB(site.download)), 1),
                          _createElementVNode("div", _hoisted_28, _toDisplayString(sitePercent(site.value)), 1)
                        ], 64))
                      }), 128))
                    ])
                  ])
                ]))
              : (_openBlock(), _createElementBlock("div", _hoisted_29, [
                  _createElementVNode("div", _hoisted_30, [
                    _createElementVNode("div", {
                      class: "donut donut--empty",
                      style: _normalizeStyle(sitePieStyle.value)
                    }, [...(_cache[15] || (_cache[15] = [
                      _createElementVNode("div", { class: "donut-core" }, [
                        _createElementVNode("strong", null, "0"),
                        _createElementVNode("span", null, "待刷新")
                      ], -1)
                    ]))], 4)
                  ]),
                  _createElementVNode("div", _hoisted_31, [
                    _cache[21] || (_cache[21] = _createElementVNode("div", { class: "site-stats" }, [
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
                    ], -1)),
                    _createElementVNode("div", _hoisted_32, [
                      _cache[17] || (_cache[17] = _createElementVNode("div", { class: "th" }, "站点", -1)),
                      _cache[18] || (_cache[18] = _createElementVNode("div", { class: "th" }, "上传", -1)),
                      _cache[19] || (_cache[19] = _createElementVNode("div", { class: "th" }, "下载", -1)),
                      _cache[20] || (_cache[20] = _createElementVNode("div", { class: "th" }, "占比", -1)),
                      _createElementVNode("div", _hoisted_33, [
                        _createVNode(_component_VIcon, {
                          icon: "mdi-chart-pie",
                          size: "18"
                        }),
                        _cache[16] || (_cache[16] = _createElementVNode("div", null, [
                          _createElementVNode("strong", null, "暂无站点增量"),
                          _createElementVNode("span", null, "刷新后显示最近可用快照")
                        ], -1))
                      ])
                    ])
                  ])
                ]))
          ]),
          _createElementVNode("aside", _hoisted_34, [
            _createElementVNode("div", _hoisted_35, [
              _createElementVNode("span", _hoisted_36, [
                _createVNode(_component_VIcon, {
                  icon: "mdi-view-grid-outline",
                  size: "20"
                })
              ]),
              _cache[22] || (_cache[22] = _createElementVNode("h2", null, "命令面板", -1)),
              _createElementVNode("span", _hoisted_37, _toDisplayString(actionItems.value.length) + " 项", 1)
            ]),
            _createElementVNode("div", _hoisted_38, [
              (_openBlock(), _createElementBlock(_Fragment, null, _renderList(actionGroups, (group) => {
                return _createElementVNode("section", {
                  key: group.group,
                  class: "command-group"
                }, [
                  _createElementVNode("div", _hoisted_39, [
                    _createElementVNode("span", null, _toDisplayString(group.group), 1),
                    _createElementVNode("span", null, _toDisplayString(group.actions.length) + " 项", 1)
                  ]),
                  _createElementVNode("div", _hoisted_40, [
                    (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(group.actions, (action) => {
                      return (_openBlock(), _createBlock(_component_VBtn, {
                        key: action.path,
                        variant: "text",
                        density: "comfortable",
                        loading: actionRunning.value === action.path,
                        class: _normalizeClass(["cmd-btn action-btn action-item text-none", [`cmd-btn--${action.tone}`, `action-btn--${action.tone}`]]),
                        onClick: $event => (runAction(action.path, action.label))
                      }, {
                        default: _withCtx(() => [
                          _createVNode(_component_VIcon, {
                            icon: action.icon,
                            size: "16"
                          }, null, 8, ["icon"]),
                          _createElementVNode("span", _hoisted_41, _toDisplayString(action.label), 1)
                        ]),
                        _: 2
                      }, 1032, ["loading", "class", "onClick"]))
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
          _createElementVNode("article", _hoisted_42, [
            _createElementVNode("div", _hoisted_43, [
              _createElementVNode("span", _hoisted_44, [
                _createVNode(_component_VIcon, {
                  icon: "mdi-download",
                  size: "20"
                })
              ]),
              _cache[23] || (_cache[23] = _createElementVNode("h2", null, "下载器活动", -1))
            ]),
            (downloaders.value.length)
              ? (_openBlock(), _createElementBlock("div", _hoisted_45, [
                  (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(downloaders.value, (d) => {
                    return (_openBlock(), _createElementBlock("div", {
                      key: d.name,
                      class: "downloader-card"
                    }, [
                      _createElementVNode("div", null, [
                        _createElementVNode("strong", null, _toDisplayString(d.name), 1),
                        _createElementVNode("span", null, "下载中 " + _toDisplayString(d.count) + " 个 ｜ ↓ " + _toDisplayString(formatGB(d.dl_speed)) + "/s ｜ ↑ " + _toDisplayString(formatGB(d.up_speed)) + "/s", 1)
                      ]),
                      _cache[24] || (_cache[24] = _createElementVNode("span", { class: "ok-chip" }, "运行中", -1))
                    ]))
                  }), 128))
                ]))
              : (_openBlock(), _createElementBlock("div", _hoisted_46, [...(_cache[25] || (_cache[25] = [
                  _createElementVNode("div", { class: "downloader-card downloader-card--empty" }, [
                    _createElementVNode("div", null, [
                      _createElementVNode("strong", null, "暂无活动下载器"),
                      _createElementVNode("span", null, "刷新后同步正在下载的任务")
                    ]),
                    _createElementVNode("span", { class: "ok-chip ok-chip--idle" }, "等待")
                  ], -1),
                  _createElementVNode("div", { class: "downloader-card downloader-card--empty downloader-card--ghost" }, [
                    _createElementVNode("div", null, [
                      _createElementVNode("strong", null, "下载器快照"),
                      _createElementVNode("span", null, "连接后显示实时上下行速度")
                    ]),
                    _createElementVNode("span", { class: "ok-chip ok-chip--idle" }, "空闲")
                  ], -1)
                ]))]))
          ]),
          _createElementVNode("article", _hoisted_47, [
            _createElementVNode("div", _hoisted_48, [
              _createElementVNode("span", _hoisted_49, [
                _createVNode(_component_VIcon, {
                  icon: "mdi-format-list-bulleted",
                  size: "20"
                })
              ]),
              _cache[26] || (_cache[26] = _createElementVNode("h2", null, "组件运行状况", -1)),
              _cache[27] || (_cache[27] = _createElementVNode("span", { class: "panel-note" }, "异常优先", -1))
            ]),
            (loading.value)
              ? (_openBlock(), _createBlock(_component_VSkeletonLoader, {
                  key: 0,
                  class: "runtime-loader",
                  type: "list-item-two-line@4"
                }))
              : (_openBlock(), _createElementBlock("div", _hoisted_50, [
                  (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(taskCards.value, (task) => {
                    return (_openBlock(), _createElementBlock("div", {
                      key: task.key,
                      class: _normalizeClass(["module task-card", { 'module--bad': isTaskBad(task), 'module--off': !task.enabled }])
                    }, [
                      _createElementVNode("div", _hoisted_51, [
                        _createElementVNode("i", {
                          class: _normalizeClass(["dot", { red: isTaskBad(task), gray: !task.enabled }])
                        }, null, 2),
                        _createElementVNode("span", _hoisted_52, _toDisplayString(task.name), 1),
                        _createElementVNode("span", {
                          class: _normalizeClass(["state", { bad: isTaskBad(task), off: !task.enabled }])
                        }, _toDisplayString(isTaskBad(task) ? '失败' : task.enabled ? 'ON' : 'OFF'), 3)
                      ]),
                      _createElementVNode("div", _hoisted_53, _toDisplayString(task.next ? `下次 ${task.next}` : task.last_time ? `最近 ${task.last_time}` : '等待调度'), 1)
                    ], 2))
                  }), 128)),
                  (!taskCards.value.length)
                    ? (_openBlock(), _createElementBlock("div", _hoisted_54, [...(_cache[28] || (_cache[28] = [
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
const Page = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-903c81ef"]]);

export { Page as default };
