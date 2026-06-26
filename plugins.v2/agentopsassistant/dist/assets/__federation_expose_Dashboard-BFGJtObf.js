import { importShared } from './__federation_fn_import-JrT3xvdd.js';
import { _ as _export_sfc, g as getPluginApi, p as postPluginApi, a as actionMessageFromResponse } from './_plugin-vue_export-helper-DVCctbmq.js';

const {resolveComponent:_resolveComponent$1,createVNode:_createVNode$1,createElementVNode:_createElementVNode$1,toDisplayString:_toDisplayString$1,openBlock:_openBlock$2,createBlock:_createBlock$2,createCommentVNode:_createCommentVNode$1,normalizeClass:_normalizeClass,normalizeStyle:_normalizeStyle,renderList:_renderList$1,Fragment:_Fragment$1,createElementBlock:_createElementBlock$2} = await importShared('vue');


const _hoisted_1$2 = { class: "mp-site-panel" };
const _hoisted_2$1 = { class: "mp-panel-head" };
const _hoisted_3$1 = { class: "mp-panel-icon" };
const _hoisted_4$1 = { class: "mp-donut-zone" };
const _hoisted_5$1 = { class: "mp-donut-core" };
const _hoisted_6$1 = { class: "mp-site-data" };
const _hoisted_7 = { class: "mp-site-stats" };
const _hoisted_8 = { class: "mp-site-stat mp-site-stat--upload" };
const _hoisted_9 = { class: "mp-site-stat mp-site-stat--download" };
const _hoisted_10 = { class: "mp-site-stat mp-site-stat--date" };
const _hoisted_11 = {
  key: 0,
  class: "mp-site-list"
};
const _hoisted_12 = { class: "mp-site-card-head" };
const _hoisted_13 = { class: "mp-site-name" };
const _hoisted_14 = { class: "mp-site-percent" };
const _hoisted_15 = { class: "mp-site-card-metrics" };
const _hoisted_16 = { class: "mp-site-row-cell mp-site-upload" };
const _hoisted_17 = { class: "mp-site-row-cell mp-site-download" };
const _hoisted_18 = {
  key: 1,
  class: "mp-site-list mp-site-list--empty"
};
const _hoisted_19 = { class: "mp-site-row-cell mp-site-empty-row" };


const _sfc_main$2 = {
  __name: 'SiteStatsWidget',
  props: {
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
  siteChart: { type: Object, default: () => ({}) },
  siteRows: { type: Array, default: () => [] },
  siteTableRows: { type: Array, default: () => [] },
  siteTrafficTotal: { type: Number, default: 0 },
  siteDateLabel: { type: String, default: '等待统计' },
  siteDateNote: { type: String, default: '等待统计' },
  sitePieStyle: { type: Object, default: () => ({}) },
  hasSiteChart: { type: Boolean, default: false },
  formatBytes: { type: Function, default: value => String(value || 0) },
  sitePercent: { type: Function, default: () => '0%' },
  allowRefresh: { type: Boolean, default: true },
},
  emits: ['refresh'],
  setup(__props, { emit: __emit }) {



const emit = __emit;

return (_ctx, _cache) => {
  const _component_VIcon = _resolveComponent$1("VIcon");
  const _component_VBtn = _resolveComponent$1("VBtn");
  const _component_VAlert = _resolveComponent$1("VAlert");

  return (_openBlock$2(), _createElementBlock$2("section", _hoisted_1$2, [
    _createElementVNode$1("header", _hoisted_2$1, [
      _createElementVNode$1("span", _hoisted_3$1, [
        _createVNode$1(_component_VIcon, {
          icon: "mdi-chart-line",
          size: "19"
        })
      ]),
      _createElementVNode$1("div", null, [
        _cache[1] || (_cache[1] = _createElementVNode$1("h3", null, "站点数据统计", -1)),
        _createElementVNode$1("p", null, _toDisplayString$1(__props.siteDateNote), 1)
      ]),
      (__props.allowRefresh)
        ? (_openBlock$2(), _createBlock$2(_component_VBtn, {
            key: 0,
            icon: "mdi-refresh",
            size: "small",
            variant: "text",
            class: "mp-refresh",
            loading: __props.loading,
            "aria-label": "刷新站点数据统计",
            onClick: _cache[0] || (_cache[0] = $event => (emit('refresh')))
          }, null, 8, ["loading"]))
        : _createCommentVNode$1("", true)
    ]),
    (__props.error)
      ? (_openBlock$2(), _createBlock$2(_component_VAlert, {
          key: 0,
          type: "error",
          density: "compact",
          variant: "tonal",
          text: __props.error
        }, null, 8, ["text"]))
      : (_openBlock$2(), _createElementBlock$2("div", {
          key: 1,
          class: _normalizeClass(["mp-site-body", { 'is-empty': !__props.hasSiteChart }])
        }, [
          _createElementVNode$1("div", _hoisted_4$1, [
            _createElementVNode$1("div", {
              class: _normalizeClass(["mp-donut", { 'mp-donut--empty': !__props.hasSiteChart }]),
              style: _normalizeStyle(__props.sitePieStyle)
            }, [
              _createElementVNode$1("div", _hoisted_5$1, [
                _createElementVNode$1("strong", null, _toDisplayString$1(__props.hasSiteChart ? __props.siteRows.length : 0), 1),
                _createElementVNode$1("span", null, _toDisplayString$1(__props.hasSiteChart ? '站点' : '待刷新'), 1)
              ])
            ], 6)
          ]),
          _createElementVNode$1("div", _hoisted_6$1, [
            _createElementVNode$1("div", _hoisted_7, [
              _createElementVNode$1("div", _hoisted_8, [
                _cache[2] || (_cache[2] = _createElementVNode$1("span", null, "上传增量", -1)),
                _createElementVNode$1("strong", null, _toDisplayString$1(__props.formatBytes(__props.siteChart.upload_total)), 1)
              ]),
              _createElementVNode$1("div", _hoisted_9, [
                _cache[3] || (_cache[3] = _createElementVNode$1("span", null, "下载增量", -1)),
                _createElementVNode$1("strong", null, _toDisplayString$1(__props.formatBytes(__props.siteChart.download_total)), 1)
              ]),
              _createElementVNode$1("div", _hoisted_10, [
                _cache[4] || (_cache[4] = _createElementVNode$1("span", null, "统计日期", -1)),
                _createElementVNode$1("strong", null, _toDisplayString$1(__props.siteDateLabel), 1)
              ])
            ]),
            (__props.hasSiteChart)
              ? (_openBlock$2(), _createElementBlock$2("div", _hoisted_11, [
                  (_openBlock$2(true), _createElementBlock$2(_Fragment$1, null, _renderList$1(__props.siteTableRows, (site) => {
                    return (_openBlock$2(), _createElementBlock$2("article", {
                      key: site.name,
                      class: "mp-site-card"
                    }, [
                      _createElementVNode$1("div", _hoisted_12, [
                        _createElementVNode$1("i", {
                          class: "mp-dot",
                          style: _normalizeStyle({ background: site.color, boxShadow: `0 0 8px ${site.glow}` })
                        }, null, 4),
                        _createElementVNode$1("span", _hoisted_13, _toDisplayString$1(site.name), 1),
                        _createElementVNode$1("strong", _hoisted_14, _toDisplayString$1(__props.sitePercent(site.value)), 1)
                      ]),
                      _createElementVNode$1("div", _hoisted_15, [
                        _createElementVNode$1("span", _hoisted_16, "↑ " + _toDisplayString$1(__props.formatBytes(site.upload)), 1),
                        _createElementVNode$1("span", _hoisted_17, "↓ " + _toDisplayString$1(__props.formatBytes(site.download)), 1)
                      ])
                    ]))
                  }), 128))
                ]))
              : (_openBlock$2(), _createElementBlock$2("div", _hoisted_18, [
                  _createElementVNode$1("div", _hoisted_19, [
                    _createVNode$1(_component_VIcon, {
                      icon: "mdi-chart-pie",
                      size: "18"
                    }),
                    _cache[5] || (_cache[5] = _createElementVNode$1("div", null, [
                      _createElementVNode$1("strong", null, "暂无站点增量"),
                      _createElementVNode$1("span", null, "刷新后显示最近可用快照")
                    ], -1))
                  ])
                ]))
          ])
        ], 2))
  ]))
}
}

};
const SiteStatsWidget = /*#__PURE__*/_export_sfc(_sfc_main$2, [['__scopeId',"data-v-cb0ec46c"]]);

const {resolveComponent:_resolveComponent,createVNode:_createVNode,createElementVNode:_createElementVNode,toDisplayString:_toDisplayString,renderList:_renderList,Fragment:_Fragment,openBlock:_openBlock$1,createElementBlock:_createElementBlock$1,withCtx:_withCtx,createBlock:_createBlock$1,createCommentVNode:_createCommentVNode} = await importShared('vue');


const _hoisted_1$1 = { class: "mp-actions-panel" };
const _hoisted_2 = { class: "mp-panel-head" };
const _hoisted_3 = { class: "mp-panel-icon" };
const _hoisted_4 = { class: "mp-action-list" };
const _hoisted_5 = { class: "mp-action-icon" };
const _hoisted_6 = { class: "mp-action-copy" };


const _sfc_main$1 = {
  __name: 'ActionsWidget',
  props: {
  actions: { type: Array, default: () => [] },
  actionRunning: { type: String, default: '' },
  actionMessage: { type: String, default: '' },
  actionOk: { type: Boolean, default: true },
  allowRefresh: { type: Boolean, default: true },
},
  emits: ['runAction'],
  setup(__props, { emit: __emit }) {



const emit = __emit;

return (_ctx, _cache) => {
  const _component_VIcon = _resolveComponent("VIcon");
  const _component_VBtn = _resolveComponent("VBtn");
  const _component_VAlert = _resolveComponent("VAlert");

  return (_openBlock$1(), _createElementBlock$1("section", _hoisted_1$1, [
    _createElementVNode("header", _hoisted_2, [
      _createElementVNode("span", _hoisted_3, [
        _createVNode(_component_VIcon, {
          icon: "mdi-lightning-bolt-outline",
          size: "19"
        })
      ]),
      _createElementVNode("div", null, [
        _cache[0] || (_cache[0] = _createElementVNode("h3", null, "手动操作", -1)),
        _createElementVNode("p", null, _toDisplayString(__props.actions.length) + " 个常用动作", 1)
      ])
    ]),
    _createElementVNode("div", _hoisted_4, [
      (_openBlock$1(true), _createElementBlock$1(_Fragment, null, _renderList(__props.actions, (action) => {
        return (_openBlock$1(), _createBlock$1(_component_VBtn, {
          key: action.path,
          variant: "text",
          class: "mp-action-btn text-none",
          loading: __props.actionRunning === action.path,
          disabled: action.disabled || (!!__props.actionRunning && __props.actionRunning !== action.path),
          title: action.reason || action.desc,
          onClick: $event => (emit('runAction', action))
        }, {
          default: _withCtx(() => [
            _createElementVNode("span", _hoisted_5, [
              _createVNode(_component_VIcon, {
                icon: action.icon,
                size: "19"
              }, null, 8, ["icon"])
            ]),
            _createElementVNode("span", _hoisted_6, [
              _createElementVNode("strong", null, _toDisplayString(action.label), 1),
              _createElementVNode("small", null, _toDisplayString(action.desc), 1)
            ]),
            _createVNode(_component_VIcon, {
              icon: "mdi-chevron-right",
              size: "17",
              class: "mp-action-arrow"
            })
          ]),
          _: 2
        }, 1032, ["loading", "disabled", "title", "onClick"]))
      }), 128))
    ]),
    (__props.actionMessage)
      ? (_openBlock$1(), _createBlock$1(_component_VAlert, {
          key: 0,
          variant: "tonal",
          density: "compact",
          class: "mp-action-message",
          icon: false,
          text: __props.actionMessage
        }, null, 8, ["text"]))
      : _createCommentVNode("", true)
  ]))
}
}

};
const ActionsWidget = /*#__PURE__*/_export_sfc(_sfc_main$1, [['__scopeId',"data-v-162dce6c"]]);

const {resolveDynamicComponent:_resolveDynamicComponent,openBlock:_openBlock,createBlock:_createBlock,createElementBlock:_createElementBlock} = await importShared('vue');


const _hoisted_1 = { class: "aoa-dashboard-widget" };

const {computed,onMounted,reactive,ref,watch} = await importShared('vue');


const _sfc_main = {
  __name: 'Dashboard',
  props: {
  api: { type: [Object, Function], default: null },
  config: { type: Object, default: () => ({}) },
  allowRefresh: { type: Boolean, default: true },
},
  emits: ['update:refreshStatus', 'loaded'],
  setup(__props, { emit: __emit }) {

const props = __props;

const emit = __emit;

const loading = ref(false);
const error = ref('');
const loadedOnce = ref(false);
const actionRunning = ref('');
const actionMessage = ref('');
const actionOk = ref(true);

const siteChart = reactive({
  date: '',
  basis: 'today',
  sites: [],
  upload_total: 0,
  download_total: 0,
});

const actionItems = [
  { path: 'run_site_stat', component: 'site_stat', label: '站点统计', desc: '刷新站点增量', icon: 'mdi-chart-pie' },
  { path: 'create_tg_console_card', component: '', label: '立即建卡', desc: '创建融合汇报卡', icon: 'mdi-card-plus-outline' },
  { path: 'run_daily_report', component: 'daily_report', label: '立即刷新', desc: '刷新融合汇报', icon: 'mdi-refresh' },
  { path: 'run_subscribe_reminder', component: 'subscribe_reminder', label: '订阅追新', desc: '推送今日追新', icon: 'mdi-bell-badge-outline' },
  { path: 'run_health_check', component: 'health_check', label: '健康巡查', desc: '检查关键状态', icon: 'mdi-heart-pulse' },
];

const componentKey = computed(() => props.config?.attrs?.component || props.config?.key || 'site');
const componentEnabledStates = computed(() => props.config?.attrs?.components || props.config?.components || {});
const componentMap = {
  site: SiteStatsWidget,
  actions: ActionsWidget,
};
const activeComponent = computed(() => componentMap[componentKey.value] || SiteStatsWidget);
function actionComponentEnabled(action) {
  const states = componentEnabledStates.value || {};
  if (!action?.component || !(action.component in states)) return true
  return !!states[action.component]
}
const widgetActions = computed(() => actionItems.map(action => {
  const enabled = actionComponentEnabled(action);
  return {
    ...action,
    disabled: !enabled,
    reason: enabled ? '' : '组件未启用，动作已暂停',
  }
}));

const sitePieColors = [
  { color: 'rgba(88, 204, 118, 0.95)', glow: 'rgba(88, 204, 118, 0.30)' },
  { color: 'rgba(45, 212, 191, 0.92)', glow: 'rgba(45, 212, 191, 0.28)' },
  { color: 'rgba(96, 165, 250, 0.92)', glow: 'rgba(96, 165, 250, 0.28)' },
  { color: 'rgba(251, 191, 36, 0.90)', glow: 'rgba(251, 191, 36, 0.26)' },
  { color: 'rgba(248, 113, 113, 0.88)', glow: 'rgba(248, 113, 113, 0.24)' },
  { color: 'rgba(167, 139, 250, 0.90)', glow: 'rgba(167, 139, 250, 0.25)' },
];

const siteRows = computed(() => [...(siteChart.sites || [])].sort((a, b) => {
  const av = (Number(a.upload) || 0) + (Number(a.download) || 0);
  const bv = (Number(b.upload) || 0) + (Number(b.download) || 0);
  return bv - av
}));

const siteTrafficTotal = computed(() => siteRows.value.reduce((sum, site) => {
  return sum + (Number(site.upload) || 0) + (Number(site.download) || 0)
}, 0));

const siteDateLabel = computed(() => {
  if (!siteChart.date) return '等待统计'
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
      background: 'conic-gradient(rgba(var(--v-theme-on-surface), 0.16) 0 82deg, rgba(var(--v-theme-on-surface), 0.055) 82deg 360deg)',
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

function formatBytes(bytes) {
  const n = Number(bytes) || 0;
  const gb = n / (1024 ** 3);
  if (gb >= 1) return `${gb.toFixed(2)} GB`
  return `${(n / (1024 ** 2)).toFixed(1)} MB`
}

async function loadSiteChart() {
  if (!props.api) return
  loading.value = true;
  error.value = '';
  emit('update:refreshStatus', true);
  try {
    const site = await getPluginApi(props.api, 'site_stat_chart');
    Object.assign(siteChart, site || {});
  } catch (err) {
    error.value = err?.message || '站点数据加载失败';
  } finally {
    loading.value = false;
    emit('update:refreshStatus', false);
    if (!loadedOnce.value) {
      loadedOnce.value = true;
      emit('loaded');
    }
  }
}

async function runAction(action) {
  if (!props.api || actionRunning.value) return
  if (action.disabled) {
    actionOk.value = false;
    actionMessage.value = action.reason || '组件未启用，动作已暂停';
    window.setTimeout(() => { actionMessage.value = ''; }, 5000);
    return
  }
  actionRunning.value = action.path;
  actionMessage.value = '';
  actionOk.value = true;
  try {
    const res = await postPluginApi(props.api, action.path);
    const ok = !!res && res.code === 0;
    actionOk.value = ok;
    actionMessage.value = actionMessageFromResponse(res, action.label);
    if (ok && action.path === 'run_site_stat') await loadSiteChart();
  } catch (err) {
    actionOk.value = false;
    actionMessage.value = actionMessageFromResponse({ code: 1, msg: err?.message }, action.label);
  } finally {
    actionRunning.value = '';
    window.setTimeout(() => { actionMessage.value = ''; }, 5000);
  }
}

watch(componentKey, () => {
  if (componentKey.value === 'site') loadSiteChart();
});
onMounted(loadSiteChart);

return (_ctx, _cache) => {
  return (_openBlock(), _createElementBlock("div", _hoisted_1, [
    (_openBlock(), _createBlock(_resolveDynamicComponent(activeComponent.value), {
      loading: loading.value,
      error: error.value,
      "site-chart": siteChart,
      "site-rows": siteRows.value,
      "site-table-rows": siteTableRows.value,
      "site-traffic-total": siteTrafficTotal.value,
      "site-date-label": siteDateLabel.value,
      "site-date-note": siteDateNote.value,
      "site-pie-style": sitePieStyle.value,
      "has-site-chart": hasSiteChart.value,
      "format-bytes": formatBytes,
      "site-percent": sitePercent,
      actions: widgetActions.value,
      "action-running": actionRunning.value,
      "action-message": actionMessage.value,
      "action-ok": actionOk.value,
      "allow-refresh": __props.allowRefresh,
      onRefresh: loadSiteChart,
      onRunAction: runAction
    }, null, 40, ["loading", "error", "site-chart", "site-rows", "site-table-rows", "site-traffic-total", "site-date-label", "site-date-note", "site-pie-style", "has-site-chart", "actions", "action-running", "action-message", "action-ok", "allow-refresh"]))
  ]))
}
}

};
const Dashboard = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-918b5563"]]);

export { Dashboard as default };
