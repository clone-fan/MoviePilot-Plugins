import { importShared } from './__federation_fn_import-JrT3xvdd.js';
import { b as getPluginApiEnvelope, u as useAgentOpsTheme, c as usePanelActionRunner } from './useAgentOpsTheme-C3_mdvlW.js';
import { c9 as mdiCheckCircle, bN as mdiChartPie, ca as mdiArrowUp, cb as mdiArrowDown, cc as mdiCalendarToday, cd as mdiYinYang, ce as mdiEye, cf as mdiLeaf, cg as mdiDatabase, ch as mdiRss, bU as mdiBroom, ba as mdiHeartPulse, aP as mdiRefresh, bD as mdiCloudUploadOutline, ar as mdiViewDashboardOutline, ci as mdiTrashCanOutline, cj as mdiTagMultiple, ck as mdiCog, bR as mdiCardPlusOutline, bS as mdiCardAccountDetailsOutline, cl as mdiCalendarCheck, am as _export_sfc } from './mdi-CTgwQT0_.js';

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
  { color: 'rgba(var(--green), 0.94)', glow: 'rgba(var(--green), 0.28)' },
  { color: 'rgba(var(--cyan), 0.90)', glow: 'rgba(var(--cyan), 0.26)' },
  { color: 'rgba(var(--amber), 0.88)', glow: 'rgba(var(--amber), 0.24)' },
  { color: 'rgba(var(--blue), 0.88)', glow: 'rgba(var(--blue), 0.24)' },
  { color: 'rgba(var(--red), 0.84)', glow: 'rgba(var(--red), 0.22)' },
  { color: 'rgba(var(--violet), 0.86)', glow: 'rgba(var(--violet), 0.23)' },
  { color: 'color-mix(in srgb, rgb(var(--green)) 62%, rgb(var(--blue)))', glow: 'rgba(var(--green), 0.20)' },
  { color: 'color-mix(in srgb, rgb(var(--amber)) 68%, rgb(var(--cyan)))', glow: 'rgba(var(--amber), 0.20)' },
];

const {reactive: reactive$2,computed: computed$c} = await importShared('vue');

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

  const siteRows = computed$c(() => [...(siteChart.sites || [])].sort((a, b) => {
    const av = (Number(a.upload) || 0) + (Number(a.download) || 0);
    const bv = (Number(b.upload) || 0) + (Number(b.download) || 0);
    return bv - av
  }));

  const siteTrafficTotal = computed$c(() => siteRows.value.reduce((sum, site) => {
    return sum + (Number(site.upload) || 0) + (Number(site.download) || 0)
  }, 0));

  const siteDateLabel = computed$c(() => {
    if (!siteChart.date) return '等待统计'
    return siteChart.basis === 'latest' ? `最近快照 ${siteChart.date}` : siteChart.date
  });

  const siteDateNote = computed$c(() => {
    if (!siteChart.date) return '等待统计'
    return siteChart.basis === 'latest' ? '最近快照' : '今天 00:00 起'
  });

  const sitePieSegments = computed$c(() => {
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

  const sitePieStyle = computed$c(() => {
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

  const siteTableRows = computed$c(() => sitePieSegments.value.slice(0, 6));
  const hasSiteChart = computed$c(() => !!(siteChart.sites && siteChart.sites.length));

  const siteEmptyTitle = computed$c(() => {
    if (siteChart.last_error || siteChart.error) return '站点统计失败'
    if (siteChart.basis === 'skipped') return '站点统计未启用'
    if (siteChart.data_valid === true) return '暂无站点增量'
    if (siteChart.basis === 'latest') return '暂无今日增量'
    return '等待站点统计'
  });

  const siteEmptyDesc = computed$c(() => {
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

const {renderSlot:_renderSlot$3,createElementVNode:_createElementVNode$c,normalizeClass:_normalizeClass$8,openBlock:_openBlock$l,createElementBlock:_createElementBlock$g} = await importShared('vue');


const _hoisted_1$e = { class: "v31-dashboard-canvas" };

const {computed: computed$b} = await importShared('vue');



const _sfc_main$l = {
  __name: 'DashboardV31Shell',
  props: {
  surface: { type: String, default: 'dialog' },
  themeClass: { type: String, default: '' },
},
  setup(__props) {

const props = __props;

const shellClass = computed$b(() => [
  `v31-dashboard-shell--${props.surface || 'dialog'}`,
  props.themeClass,
]);

return (_ctx, _cache) => {
  return (_openBlock$l(), _createElementBlock$g("section", {
    class: _normalizeClass$8(["dashboard-plugin-vue-renderer v31-dashboard-shell aoa-root aoa-plugin-shell", shellClass.value])
  }, [
    _createElementVNode$c("div", _hoisted_1$e, [
      _renderSlot$3(_ctx.$slots, "default")
    ])
  ], 2))
}
}

};

const {createElementVNode:_createElementVNode$b,openBlock:_openBlock$k,createElementBlock:_createElementBlock$f,normalizeStyle:_normalizeStyle$1} = await importShared('vue');


const _hoisted_1$d = ["width", "height"];
const _hoisted_2$c = ["d"];

const {computed: computed$a} = await importShared('vue');



const _sfc_main$k = {
  __name: 'SvgIcon',
  props: {
  icon: { type: String, required: true },
  size: { type: [Number, String], default: 14 },
  color: { type: String, default: '' },
},
  setup(__props) {

const props = __props;

const normalizedSize = computed$a(() => {
  const rawSize = String(props.size).trim();
  return /^\d+(\.\d+)?$/.test(rawSize) ? `${rawSize}px` : rawSize
});

const iconStyle = computed$a(() => ({
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
      _createElementVNode$b("path", {
        d: __props.icon,
        fill: "currentColor"
      }, null, 8, _hoisted_2$c)
    ], 8, _hoisted_1$d))
  ], 4))
}
}

};

const {openBlock:_openBlock$j,createBlock:_createBlock$b,createCommentVNode:_createCommentVNode$8,renderSlot:_renderSlot$2,toDisplayString:_toDisplayString$a,createTextVNode:_createTextVNode$4,createElementBlock:_createElementBlock$e,normalizeClass:_normalizeClass$7} = await importShared('vue');


const _hoisted_1$c = ["disabled"];
const _hoisted_2$b = { key: 1 };


const _sfc_main$j = {
  __name: 'PillButton',
  props: {
  icon: { type: String, default: '' },
  label: { type: String, default: '' },
  iconOnly: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
},
  setup(__props) {



return (_ctx, _cache) => {
  return (_openBlock$j(), _createElementBlock$e("button", {
    type: "button",
    class: _normalizeClass$7(["v31-glass-card v31-pill-button", { 'v31-pill-button--icon': __props.iconOnly }]),
    disabled: __props.disabled
  }, [
    (__props.icon)
      ? (_openBlock$j(), _createBlock$b(_sfc_main$k, {
          key: 0,
          icon: __props.icon,
          size: "14"
        }, null, 8, ["icon"]))
      : _createCommentVNode$8("", true),
    (!__props.iconOnly)
      ? (_openBlock$j(), _createElementBlock$e("span", _hoisted_2$b, [
          _renderSlot$2(_ctx.$slots, "default", {}, () => [
            _createTextVNode$4(_toDisplayString$a(__props.label), 1)
          ])
        ]))
      : _createCommentVNode$8("", true)
  ], 10, _hoisted_1$c))
}
}

};

const v31Icons = {
  arrowDown: mdiArrowDown,
  arrowUp: mdiArrowUp,
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

const {unref:_unref$6,createVNode:_createVNode$b,createElementVNode:_createElementVNode$a,openBlock:_openBlock$i,createElementBlock:_createElementBlock$d} = await importShared('vue');


const _hoisted_1$b = { class: "v31-dashboard-toolbar" };
const _hoisted_2$a = { class: "v31-dashboard-toolbar__brand" };
const _hoisted_3$a = { class: "v31-dashboard-toolbar__brand-icon" };
const _hoisted_4$a = { class: "v31-dashboard-toolbar__actions" };


const _sfc_main$i = {
  __name: 'DashboardV31Toolbar',
  props: {
  loading: { type: Boolean, default: false },
},
  emits: ['refresh', 'settings'],
  setup(__props) {





return (_ctx, _cache) => {
  return (_openBlock$i(), _createElementBlock$d("header", _hoisted_1$b, [
    _createElementVNode$a("div", _hoisted_2$a, [
      _createElementVNode$a("span", _hoisted_3$a, [
        _createVNode$b(_sfc_main$k, {
          icon: _unref$6(v31Icons).viewDashboard,
          size: 20
        }, null, 8, ["icon"])
      ]),
      _cache[2] || (_cache[2] = _createElementVNode$a("h1", { class: "v31-dashboard-toolbar__title" }, "仪表盘", -1))
    ]),
    _createElementVNode$a("div", _hoisted_4$a, [
      _createVNode$b(_sfc_main$j, {
        icon: _unref$6(v31Icons).refresh,
        label: "刷新",
        disabled: __props.loading,
        onClick: _cache[0] || (_cache[0] = $event => (_ctx.$emit('refresh')))
      }, null, 8, ["icon", "disabled"]),
      _createVNode$b(_sfc_main$j, {
        icon: _unref$6(v31Icons).cog,
        "icon-only": "",
        label: "设置",
        onClick: _cache[1] || (_cache[1] = $event => (_ctx.$emit('settings')))
      }, null, 8, ["icon"])
    ])
  ]))
}
}

};

const {renderSlot:_renderSlot$1,resolveDynamicComponent:_resolveDynamicComponent$1,normalizeClass:_normalizeClass$6,withCtx:_withCtx$6,openBlock:_openBlock$h,createBlock:_createBlock$a} = await importShared('vue');


const {computed: computed$9} = await importShared('vue');



const _sfc_main$h = {
  __name: 'GlassCard',
  props: {
  tag: { type: String, default: 'section' },
  light: { type: Boolean, default: false },
  className: { type: [String, Array, Object], default: '' },
},
  setup(__props) {

const props = __props;

const cardClass = computed$9(() => [
  props.light ? 'v31-glass-card-light' : 'v31-glass-card',
  props.className,
]);

return (_ctx, _cache) => {
  return (_openBlock$h(), _createBlock$a(_resolveDynamicComponent$1(__props.tag), {
    class: _normalizeClass$6(cardClass.value)
  }, {
    default: _withCtx$6(() => [
      _renderSlot$1(_ctx.$slots, "default")
    ]),
    _: 3
  }, 8, ["class"]))
}
}

};

const {openBlock:_openBlock$g,createBlock:_createBlock$9,createCommentVNode:_createCommentVNode$7,normalizeClass:_normalizeClass$5,createElementBlock:_createElementBlock$c,createElementVNode:_createElementVNode$9,toDisplayString:_toDisplayString$9,withCtx:_withCtx$5} = await importShared('vue');


const _hoisted_1$a = { class: "v31-kpi-card__icon" };
const _hoisted_2$9 = { class: "v31-kpi-card__content" };
const _hoisted_3$9 = { class: "v31-kpi-card__label" };
const _hoisted_4$9 = { class: "v31-kpi-card__value-row" };
const _hoisted_5$5 = {
  key: 0,
  class: "v31-kpi-card__total"
};
const _hoisted_6$4 = {
  key: 1,
  class: "v31-kpi-card__unit"
};
const _hoisted_7$2 = { class: "v31-kpi-card__detail" };


const _sfc_main$g = {
  __name: 'KpiCard',
  props: {
  item: { type: Object, required: true },
},
  setup(__props) {



return (_ctx, _cache) => {
  return (_openBlock$g(), _createBlock$9(_sfc_main$h, { "class-name": "v31-kpi-card" }, {
    default: _withCtx$5(() => [
      _createElementVNode$9("span", _hoisted_1$a, [
        (__props.item.icon)
          ? (_openBlock$g(), _createBlock$9(_sfc_main$k, {
              key: 0,
              icon: __props.item.icon,
              color: __props.item.iconColor || undefined,
              size: "20"
            }, null, 8, ["icon", "color"]))
          : _createCommentVNode$7("", true),
        (__props.item.dot)
          ? (_openBlock$g(), _createElementBlock$c("span", {
              key: 1,
              class: _normalizeClass$5(["v31-status-dot", { 'v31-status-dot--pulse': __props.item.pulse }])
            }, null, 2))
          : _createCommentVNode$7("", true)
      ]),
      _createElementVNode$9("div", _hoisted_2$9, [
        _createElementVNode$9("span", _hoisted_3$9, _toDisplayString$9(__props.item.label), 1),
        _createElementVNode$9("div", _hoisted_4$9, [
          _createElementVNode$9("span", {
            class: _normalizeClass$5(["v31-kpi-card__value", { 'v31-kpi-card__value--large': __props.item.large }])
          }, _toDisplayString$9(__props.item.value), 3),
          (__props.item.total)
            ? (_openBlock$g(), _createElementBlock$c("span", _hoisted_5$5, "/ " + _toDisplayString$9(__props.item.total), 1))
            : _createCommentVNode$7("", true),
          (__props.item.unit)
            ? (_openBlock$g(), _createElementBlock$c("span", _hoisted_6$4, _toDisplayString$9(__props.item.unit), 1))
            : _createCommentVNode$7("", true)
        ]),
        _createElementVNode$9("span", _hoisted_7$2, _toDisplayString$9(__props.item.detail), 1)
      ])
    ]),
    _: 1
  }))
}
}

};

const {renderList:_renderList$4,Fragment:_Fragment$5,openBlock:_openBlock$f,createElementBlock:_createElementBlock$b,createBlock:_createBlock$8} = await importShared('vue');


const _hoisted_1$9 = {
  class: "v31-kpi-strip",
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

const {toDisplayString:_toDisplayString$8,createElementVNode:_createElementVNode$8,normalizeClass:_normalizeClass$4,normalizeStyle:_normalizeStyle,openBlock:_openBlock$e,createElementBlock:_createElementBlock$a} = await importShared('vue');


const _hoisted_1$8 = ["aria-label"];
const _hoisted_2$8 = { class: "v31-donut__inner" };
const _hoisted_3$8 = { class: "v31-donut__value" };
const _hoisted_4$8 = { class: "v31-donut__label" };

const {computed: computed$8} = await importShared('vue');



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

const normalizedSegments = computed$8(() => Array.isArray(props.segments) ? props.segments : []);
const ringStyle = computed$8(() => {
  if (props.pieStyle && typeof props.pieStyle === 'object' && Object.keys(props.pieStyle).length) {
    return props.pieStyle
  }
  return {
    background: 'conic-gradient(rgba(var(--line), 0.16) 0 82deg, rgba(var(--line), 0.055) 82deg 360deg)',
  }
});
const ariaLabel = computed$8(() => {
  if (!normalizedSegments.value.length) return `${props.value} ${props.label}，暂无站点流量分段`
  const names = normalizedSegments.value.map(item => item?.name).filter(Boolean).slice(0, 4).join('、');
  return `${props.value} ${props.label}，按 PT 站点${names ? ` ${names}` : ''} 流量分段`
});

return (_ctx, _cache) => {
  return (_openBlock$e(), _createElementBlock$a("div", {
    class: _normalizeClass$4(["v31-donut", { 'v31-donut--empty': !normalizedSegments.value.length }]),
    style: _normalizeStyle(ringStyle.value),
    "aria-label": ariaLabel.value
  }, [
    _createElementVNode$8("div", _hoisted_2$8, [
      _createElementVNode$8("span", null, [
        _createElementVNode$8("strong", _hoisted_3$8, _toDisplayString$8(__props.value), 1),
        _createElementVNode$8("small", _hoisted_4$8, _toDisplayString$8(__props.label), 1)
      ])
    ])
  ], 14, _hoisted_1$8))
}
}

};

const {renderList:_renderList$3,Fragment:_Fragment$4,openBlock:_openBlock$d,createElementBlock:_createElementBlock$9,createVNode:_createVNode$a,createCommentVNode:_createCommentVNode$6,toDisplayString:_toDisplayString$7,createElementVNode:_createElementVNode$7} = await importShared('vue');


const _hoisted_1$7 = { class: "v31-traffic-summary" };
const _hoisted_2$7 = {
  key: 0,
  class: "v31-traffic-summary__icon",
  "aria-hidden": "true"
};
const _hoisted_3$7 = { class: "v31-traffic-summary__text" };
const _hoisted_4$7 = { class: "v31-traffic-summary__label" };
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
          : _createCommentVNode$6("", true),
        _createElementVNode$7("span", _hoisted_3$7, [
          _createElementVNode$7("span", _hoisted_4$7, _toDisplayString$7(row.label), 1),
          _createElementVNode$7("strong", _hoisted_5$4, _toDisplayString$7(row.value), 1)
        ])
      ]))
    }), 128))
  ]))
}
}

};

const {createVNode:_createVNode$9,createElementVNode:_createElementVNode$6,toDisplayString:_toDisplayString$6,unref:_unref$5,createTextVNode:_createTextVNode$3,openBlock:_openBlock$c,createElementBlock:_createElementBlock$8} = await importShared('vue');


const _hoisted_1$6 = { class: "v31-glass-card-light v31-site-traffic-card" };
const _hoisted_2$6 = { class: "v31-site-traffic-card__identity" };
const _hoisted_3$6 = { class: "v31-site-traffic-card__icon" };
const _hoisted_4$6 = { class: "v31-site-traffic-card__name" };
const _hoisted_5$3 = { class: "v31-site-traffic-card__metrics" };
const _hoisted_6$3 = { class: "v31-site-traffic-card__metric-pill v31-site-traffic-card__metric-pill--upload" };
const _hoisted_7$1 = { class: "v31-site-traffic-card__metric-pill v31-site-traffic-card__metric-pill--download" };
const _hoisted_8$1 = { class: "v31-site-traffic-card__percent" };
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
    _createElementVNode$6("div", _hoisted_2$6, [
      _createElementVNode$6("span", _hoisted_3$6, [
        _createVNode$9(_sfc_main$k, {
          icon: __props.icon,
          color: __props.iconColor,
          size: "14"
        }, null, 8, ["icon", "color"])
      ]),
      _createElementVNode$6("span", _hoisted_4$6, _toDisplayString$6(__props.name), 1)
    ]),
    _createElementVNode$6("div", _hoisted_5$3, [
      _createElementVNode$6("span", _hoisted_6$3, [
        _createVNode$9(_sfc_main$k, {
          icon: _unref$5(v31Icons).arrowUp,
          size: "10"
        }, null, 8, ["icon"]),
        _createTextVNode$3(" " + _toDisplayString$6(__props.upload), 1)
      ]),
      _createElementVNode$6("span", _hoisted_7$1, [
        _createVNode$9(_sfc_main$k, {
          icon: _unref$5(v31Icons).arrowDown,
          size: "10"
        }, null, 8, ["icon"]),
        _createTextVNode$3(" " + _toDisplayString$6(__props.download), 1)
      ])
    ]),
    _createElementVNode$6("span", _hoisted_8$1, [
      _createElementVNode$6("span", _hoisted_9, [
        _createVNode$9(_sfc_main$k, {
          icon: _unref$5(v31Icons).chartPie,
          size: "9"
        }, null, 8, ["icon"])
      ]),
      _createTextVNode$3(" " + _toDisplayString$6(__props.percent), 1)
    ])
  ]))
}
}

};

const {unref:_unref$4,createVNode:_createVNode$8,createTextVNode:_createTextVNode$2,createElementVNode:_createElementVNode$5,toDisplayString:_toDisplayString$5,renderList:_renderList$2,Fragment:_Fragment$3,openBlock:_openBlock$b,createElementBlock:_createElementBlock$7,createBlock:_createBlock$7,withCtx:_withCtx$4} = await importShared('vue');


const _hoisted_1$5 = { class: "v31-card-header" };
const _hoisted_2$5 = { class: "v31-card-heading" };
const _hoisted_3$5 = { class: "v31-card-note" };
const _hoisted_4$5 = { class: "v31-site-panel__body" };
const _hoisted_5$2 = { class: "v31-site-panel__content" };
const _hoisted_6$2 = { class: "v31-site-card-list" };


const _sfc_main$b = {
  __name: 'SiteDataPanel',
  props: {
  dateNote: { type: String, default: '今天 00:00 起' },
  donutValue: { type: [String, Number], default: '2' },
  donutLabel: { type: String, default: '个站点' },
  donutSegments: { type: Array, default: () => [] },
  donutStyle: { type: Object, default: () => ({}) },
  summaryRows: { type: Array, default: () => [] },
  sites: { type: Array, default: () => [] },
},
  setup(__props) {



return (_ctx, _cache) => {
  return (_openBlock$b(), _createBlock$7(_sfc_main$h, { "class-name": "v31-site-panel" }, {
    default: _withCtx$4(() => [
      _createElementVNode$5("div", _hoisted_1$5, [
        _createElementVNode$5("h2", _hoisted_2$5, [
          _createVNode$8(_sfc_main$k, {
            icon: _unref$4(v31Icons).leaf,
            color: "#34C759",
            size: "18"
          }, null, 8, ["icon"]),
          _cache[0] || (_cache[0] = _createTextVNode$2(" 站点数据 ", -1))
        ]),
        _createElementVNode$5("span", _hoisted_3$5, _toDisplayString$5(__props.dateNote), 1)
      ]),
      _createElementVNode$5("div", _hoisted_4$5, [
        _createVNode$8(_sfc_main$e, {
          value: __props.donutValue,
          label: __props.donutLabel,
          segments: __props.donutSegments,
          "pie-style": __props.donutStyle
        }, null, 8, ["value", "label", "segments", "pie-style"]),
        _createElementVNode$5("div", _hoisted_5$2, [
          _createVNode$8(_sfc_main$d, { rows: __props.summaryRows }, null, 8, ["rows"]),
          _createElementVNode$5("div", _hoisted_6$2, [
            (_openBlock$b(true), _createElementBlock$7(_Fragment$3, null, _renderList$2(__props.sites, (site) => {
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
          ])
        ])
      ])
    ]),
    _: 1
  }))
}
}

};

const {openBlock:_openBlock$a,createBlock:_createBlock$6,createCommentVNode:_createCommentVNode$5,renderSlot:_renderSlot,toDisplayString:_toDisplayString$4,createTextVNode:_createTextVNode$1,normalizeClass:_normalizeClass$3,createElementBlock:_createElementBlock$6} = await importShared('vue');


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
    class: _normalizeClass$3(["v31-status-chip", toneClass.value])
  }, [
    (__props.icon)
      ? (_openBlock$a(), _createBlock$6(_sfc_main$k, {
          key: 0,
          icon: __props.icon,
          size: "10"
        }, null, 8, ["icon"]))
      : _createCommentVNode$5("", true),
    _renderSlot(_ctx.$slots, "default", {}, () => [
      _createTextVNode$1(_toDisplayString$4(__props.label), 1)
    ])
  ], 2))
}
}

};

const {toDisplayString:_toDisplayString$3,createElementVNode:_createElementVNode$4,createVNode:_createVNode$7,openBlock:_openBlock$9,createElementBlock:_createElementBlock$5} = await importShared('vue');


const _hoisted_1$4 = { class: "v31-glass-card-light v31-task-tile" };
const _hoisted_2$4 = { class: "v31-task-tile__top" };
const _hoisted_3$4 = { class: "v31-task-tile__name" };
const _hoisted_4$4 = { class: "v31-task-tile__schedule" };


const _sfc_main$9 = {
  __name: 'TaskTile',
  props: {
  task: { type: Object, required: true },
},
  setup(__props) {



return (_ctx, _cache) => {
  return (_openBlock$9(), _createElementBlock$5("article", _hoisted_1$4, [
    _createElementVNode$4("div", _hoisted_2$4, [
      _createElementVNode$4("span", _hoisted_3$4, _toDisplayString$3(__props.task.name), 1),
      _createVNode$7(_sfc_main$a, {
        label: __props.task.state || '运行中',
        tone: __props.task.state === '失败' ? 'danger' : 'plain-green'
      }, null, 8, ["label", "tone"])
    ]),
    _createElementVNode$4("span", _hoisted_4$4, _toDisplayString$3(__props.task.schedule), 1)
  ]))
}
}

};

const {unref:_unref$3,createVNode:_createVNode$6,createElementVNode:_createElementVNode$3,renderList:_renderList$1,Fragment:_Fragment$2,openBlock:_openBlock$8,createElementBlock:_createElementBlock$4,createBlock:_createBlock$5,createCommentVNode:_createCommentVNode$4,withCtx:_withCtx$3} = await importShared('vue');


const _hoisted_1$3 = { class: "v31-card-header" };
const _hoisted_2$3 = { class: "v31-card-heading" };
const _hoisted_3$3 = {
  key: 0,
  class: "v31-task-grid"
};
const _hoisted_4$3 = {
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
      _createElementVNode$3("div", _hoisted_1$3, [
        _createElementVNode$3("div", _hoisted_2$3, [
          _createVNode$6(_sfc_main$k, {
            icon: _unref$3(v31Icons).calendarCheck,
            color: "#60A5FA",
            size: "18"
          }, null, 8, ["icon"]),
          _cache[0] || (_cache[0] = _createElementVNode$3("span", null, "任务运行", -1)),
          _cache[1] || (_cache[1] = _createElementVNode$3("small", null, "当前实时任务", -1))
        ]),
        _createVNode$6(_sfc_main$a, { label: "异常优先" })
      ]),
      (__props.tasks.length)
        ? (_openBlock$8(), _createElementBlock$4("div", _hoisted_3$3, [
            (_openBlock$8(true), _createElementBlock$4(_Fragment$2, null, _renderList$1(__props.tasks, (task) => {
              return (_openBlock$8(), _createBlock$5(_sfc_main$9, {
                key: task.key || task.name,
                task: task
              }, null, 8, ["task"]))
            }), 128))
          ]))
        : (_openBlock$8(), _createElementBlock$4("div", _hoisted_4$3, "当前没有正在运行的任务"))
    ]),
    _: 1
  }))
}
}

};

const {createElementVNode:_createElementVNode$2,toDisplayString:_toDisplayString$2,normalizeClass:_normalizeClass$2,openBlock:_openBlock$7,createElementBlock:_createElementBlock$3,createCommentVNode:_createCommentVNode$3,renderList:_renderList,Fragment:_Fragment$1,createVNode:_createVNode$5} = await importShared('vue');


const _hoisted_1$2 = { class: "v31-quick-actions" };
const _hoisted_2$2 = { class: "v31-quick-actions__header" };
const _hoisted_3$2 = { class: "v31-quick-actions__grid" };
const _hoisted_4$2 = ["disabled", "aria-busy", "aria-label", "title", "onClick"];
const _hoisted_5$1 = { class: "v31-quick-action__icon" };
const _hoisted_6$1 = { class: "v31-quick-action__label" };


const _sfc_main$7 = {
  __name: 'QuickActionsBand',
  props: {
  actions: { type: Array, default: () => [] },
  runningKey: { type: String, default: '' },
  feedbackMessage: { type: String, default: '' },
  feedbackOk: { type: Boolean, default: true },
},
  emits: ['action'],
  setup(__props) {

const props = __props;



function isActionRunning(action) {
  return !!props.runningKey && (props.runningKey === action?.key || props.runningKey === action?.path)
}

return (_ctx, _cache) => {
  return (_openBlock$7(), _createElementBlock$3("section", _hoisted_1$2, [
    _createElementVNode$2("div", _hoisted_2$2, [
      _cache[0] || (_cache[0] = _createElementVNode$2("h2", { class: "v31-quick-actions__title" }, "快捷操作", -1)),
      (__props.feedbackMessage)
        ? (_openBlock$7(), _createElementBlock$3("div", {
            key: 0,
            class: _normalizeClass$2(["v31-action-feedback", { 'v31-action-feedback--bad': !__props.feedbackOk }]),
            role: "status",
            "aria-live": "polite"
          }, _toDisplayString$2(__props.feedbackMessage), 3))
        : _createCommentVNode$3("", true)
    ]),
    _createElementVNode$2("div", _hoisted_3$2, [
      (_openBlock$7(true), _createElementBlock$3(_Fragment$1, null, _renderList(__props.actions, (action) => {
        return (_openBlock$7(), _createElementBlock$3("button", {
          key: action.key,
          type: "button",
          class: _normalizeClass$2(["v31-quick-action", { 'v31-quick-action--running': isActionRunning(action) }]),
          disabled: isActionRunning(action),
          "aria-busy": isActionRunning(action) ? 'true' : 'false',
          "aria-label": `${action.label}，点击后执行`,
          title: isActionRunning(action) ? `${action.label}执行中` : `执行${action.label}`,
          onClick: $event => (_ctx.$emit('action', action))
        }, [
          _createElementVNode$2("span", _hoisted_5$1, [
            _createVNode$5(_sfc_main$k, {
              icon: action.icon,
              size: "13"
            }, null, 8, ["icon"])
          ]),
          _createElementVNode$2("span", _hoisted_6$1, _toDisplayString$2(action.label), 1)
        ], 10, _hoisted_4$2))
      }), 128))
    ])
  ]))
}
}

};

const {createVNode:_createVNode$4,normalizeClass:_normalizeClass$1,openBlock:_openBlock$6,createElementBlock:_createElementBlock$2} = await importShared('vue');


const {computed: computed$6} = await importShared('vue');


const _sfc_main$6 = {
  __name: 'IconCircle',
  props: {
  icon: { type: String, required: true },
  size: { type: [Number, String], default: 14 },
  tone: { type: String, default: '' },
},
  setup(__props) {

const props = __props;

const variantClass = computed$6(() => props.tone ? `v31-icon-circle--${props.tone}` : '');

return (_ctx, _cache) => {
  return (_openBlock$6(), _createElementBlock$2("span", {
    class: _normalizeClass$1(["v31-icon-circle", variantClass.value])
  }, [
    _createVNode$4(_sfc_main$k, {
      icon: __props.icon,
      size: __props.size
    }, null, 8, ["icon", "size"])
  ], 2))
}
}

};

const {toDisplayString:_toDisplayString$1,createElementVNode:_createElementVNode$1,unref:_unref$2,createVNode:_createVNode$3,createTextVNode:_createTextVNode,Fragment:_Fragment,openBlock:_openBlock$5,createElementBlock:_createElementBlock$1,createCommentVNode:_createCommentVNode$2,normalizeClass:_normalizeClass} = await importShared('vue');


const _hoisted_1$1 = { class: "v31-glass-card v31-fusion-mini" };
const _hoisted_2$1 = { class: "v31-fusion-mini__updated" };
const _hoisted_3$1 = { class: "v31-fusion-mini__identity" };
const _hoisted_4$1 = { class: "v31-fusion-mini__name" };
const _hoisted_5 = { class: "v31-fusion-mini__status" };
const _hoisted_6 = { class: "v31-fusion-mini__buttons" };
const _hoisted_7 = ["disabled", "aria-busy"];
const _hoisted_8 = ["disabled", "aria-busy", "title"];


const _sfc_main$5 = {
  __name: 'FusionMiniCard',
  props: {
  cardId: { type: [String, Number], default: '' },
  updatedAt: { type: String, default: '' },
  isBuilt: { type: Boolean, default: false },
  enabled: { type: Boolean, default: true },
  refreshing: { type: Boolean, default: false },
  building: { type: Boolean, default: false },
},
  emits: ['build', 'refresh'],
  setup(__props) {





return (_ctx, _cache) => {
  return (_openBlock$5(), _createElementBlock$1("article", _hoisted_1$1, [
    _createElementVNode$1("span", _hoisted_2$1, _toDisplayString$1(__props.enabled ? `更新于 ${__props.updatedAt || '--'}` : '插件已停用'), 1),
    _createVNode$3(_sfc_main$6, {
      icon: _unref$2(v31Icons).cardAccount,
      tone: "blue",
      class: "v31-fusion-mini__icon"
    }, null, 8, ["icon"]),
    _createElementVNode$1("div", _hoisted_3$1, [
      _createElementVNode$1("strong", _hoisted_4$1, [
        _cache[2] || (_cache[2] = _createTextVNode("融合卡 ", -1)),
        (__props.enabled && __props.cardId)
          ? (_openBlock$5(), _createElementBlock$1(_Fragment, { key: 0 }, [
              _createTextVNode("#" + _toDisplayString$1(__props.cardId), 1)
            ], 64))
          : (__props.enabled)
            ? (_openBlock$5(), _createElementBlock$1(_Fragment, { key: 1 }, [
                _createTextVNode("未建卡")
              ], 64))
            : _createCommentVNode$2("", true)
      ]),
      _createElementVNode$1("div", _hoisted_5, [
        _cache[3] || (_cache[3] = _createElementVNode$1("span", null, "状态", -1)),
        _createVNode$3(_sfc_main$a, {
          label: __props.enabled ? (__props.isBuilt ? '已建立' : '未建立') : '已停用',
          tone: __props.enabled && __props.isBuilt ? 'green' : '',
          icon: __props.enabled && __props.isBuilt ? _unref$2(v31Icons).checkCircle : ''
        }, null, 8, ["label", "tone", "icon"])
      ])
    ]),
    _createElementVNode$1("div", _hoisted_6, [
      _createElementVNode$1("button", {
        type: "button",
        class: _normalizeClass(["v31-pill-button v31-pill-button--compact", { 'v31-status-chip--green': __props.enabled }]),
        disabled: !__props.enabled || __props.building || __props.refreshing,
        "aria-busy": __props.building ? 'true' : 'false',
        title: "创建或更新融合卡",
        onClick: _cache[0] || (_cache[0] = $event => (_ctx.$emit('build')))
      }, [
        _createVNode$3(_sfc_main$k, {
          icon: _unref$2(v31Icons).cardPlus,
          size: "11"
        }, null, 8, ["icon"]),
        _cache[4] || (_cache[4] = _createTextVNode(" 建卡 ", -1))
      ], 10, _hoisted_7),
      _createElementVNode$1("button", {
        type: "button",
        class: "v31-pill-button v31-pill-button--compact",
        disabled: !__props.enabled || __props.building || __props.refreshing,
        "aria-busy": __props.refreshing ? 'true' : 'false',
        title: __props.refreshing ? '融合卡刷新中' : '立即刷新融合卡',
        "data-fusion-refresh-button": "",
        onClick: _cache[1] || (_cache[1] = $event => (_ctx.$emit('refresh')))
      }, [
        _createVNode$3(_sfc_main$k, {
          icon: _unref$2(v31Icons).refresh,
          size: "11"
        }, null, 8, ["icon"]),
        _createTextVNode(" " + _toDisplayString$1(__props.refreshing ? '刷新中' : '刷新'), 1)
      ], 8, _hoisted_8)
    ])
  ]))
}
}

};

const {createVNode:_createVNode$2,unref:_unref$1,createElementVNode:_createElementVNode,toDisplayString:_toDisplayString,openBlock:_openBlock$4,createElementBlock:_createElementBlock,createCommentVNode:_createCommentVNode$1,withCtx:_withCtx$2,createBlock:_createBlock$4} = await importShared('vue');


const _hoisted_1 = { class: "v31-core-grid" };
const _hoisted_2 = { class: "v31-glass-card v31-bottom-row" };
const _hoisted_3 = {
  key: 0,
  class: "v31-error"
};
const _hoisted_4 = {
  key: 1,
  class: "v31-loading"
};

const {computed: computed$5,onMounted: onMounted$1,reactive: reactive$1,ref: ref$1} = await importShared('vue');


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
const loading = ref$1(false);
const error = ref$1('');
const localActionMessage = ref$1('');
const localActionOk = ref$1(true);

const dashboard = reactive$1({
  enabled: true,
  summary: '',
  tasks: [],
  task_total: 0,
  task_on: 0,
  task_failed: 0,
  health: { success: true, output: '' },
});

const fusionCard = reactive$1({
  id: '',
  updatedAt: '',
  isBuilt: false,
});

const themeClass = computed$5(() => {
  return `v31-dashboard-shell--${themeName.value} ${rootThemeClass.value}`
});

const {
  siteChart,
  siteRows,
  siteTrafficTotal,
  siteDateNote,
  sitePieSegments,
  sitePieStyle,
  sitePercent,
  loadSiteChart,
} = useSiteChart(props.api);

const quickActions = [
  { key: 'subscribe', label: '订阅追新', icon: v31Icons.rss, path: 'run_subscribe_reminder' },
  { key: 'transfer', label: '今日入库', icon: v31Icons.calendarToday, path: 'run_today_transfer' },
  { key: 'site_stat', label: '站点统计', icon: v31Icons.chartPie, path: 'run_site_stat' },
  { key: 'backup', label: '配置备份', icon: v31Icons.database, path: 'run_backup' },
  { key: 'log_clean', label: '日志清理', icon: v31Icons.broom, path: 'run_log_clean' },
  { key: 'health', label: '健康巡查', icon: v31Icons.heartPulse, path: 'run_health_check' },
  { key: 'mp_update', label: 'MP 更新', icon: v31Icons.refresh, path: 'run_mp_update' },
  { key: 'plugin_update', label: '插件更新', icon: v31Icons.cloudUpload, path: 'run_market_update' },
];

const actionRunner = usePanelActionRunner({
  api: () => props.api,
  onSuccess: async ({ action }) => {
    if (action?.path === 'run_site_stat') await loadSiteChart();
    if (action?.path === 'create_tg_console_card' || action?.path === 'run_daily_report') await loadFusionCard();
  },
});

const healthOk = computed$5(() => dashboard.health?.success !== false && Number(dashboard.task_failed || 0) === 0);
const enabledCount = computed$5(() => runtimeTasks.value.filter(task => task.enabled).length);
const totalCount = computed$5(() => Number(dashboard.task_total || 0) || Math.max(enabledCount.value, runtimeTasks.value.length));
const trafficLabel = computed$5(() => formatGB(siteTrafficTotal.value || siteChart.upload_total + siteChart.download_total));
const trafficParts = computed$5(() => {
  const [value, unit = 'GB'] = trafficLabel.value.split(' ');
  return { value: value || '122.5', unit }
});

const kpiItems = computed$5(() => [
  {
    key: 'system',
    label: '系统状态',
    icon: v31Icons.checkCircle,
    iconColor: dashboard.enabled !== false ? '#34C759' : '#8E8E93',
    value: dashboard.enabled !== false ? '运行平稳' : '插件已停用',
    detail: dashboard.enabled !== false
      ? (healthOk.value ? '当前任务未发现异常' : `当前有 ${Number(dashboard.task_failed || 0)} 个异常组件`)
      : '开启插件总开关后恢复运行',
  },
  {
    key: 'runtime',
    label: '运行状态',
    dot: dashboard.enabled !== false,
    pulse: dashboard.enabled !== false,
    value: dashboard.enabled !== false ? '正常' : '停用',
    detail: `异常组件 ${Number(dashboard.task_failed || 0)}`,
  },
  {
    key: 'enabled',
    label: '启用组件',
    icon: v31Icons.checkCircle,
    iconColor: '#8E8E93',
    value: String(enabledCount.value),
    total: String(totalCount.value),
    large: true,
    detail: dashboard.enabled !== false ? '组件运行正常' : '组件当前均未运行',
  },
  {
    key: 'traffic',
    label: '站点流量',
    icon: v31Icons.chartPie,
    iconColor: '#60A5FA',
    value: trafficParts.value.value,
    unit: trafficParts.value.unit,
    large: true,
    detail: '任务调度与健康巡查',
  },
]);

const trafficSummaryRows = computed$5(() => [
  { label: '上传增量', value: formatGB(siteChart.upload_total || 0), icon: v31Icons.arrowUp },
  { label: '下载增量', value: formatGB(siteChart.download_total || 0), icon: v31Icons.arrowDown },
  { label: '统计时间', value: siteChart.date || '2026-07-04', icon: v31Icons.calendarToday },
]);

const siteCards = computed$5(() => {
  const siteIcons = [v31Icons.yinYang, v31Icons.eye, v31Icons.chartPie, v31Icons.leaf, v31Icons.database];
  const siteColors = ['#34C759', '#60A5FA', '#FFB020', '#AF52DE', '#64D2FF'];
  const rows = siteRows.value;
  return rows.map((site, siteIndex) => {
    const traffic = Number(site.upload || 0) + Number(site.download || 0);
    return {
      name: site.name || (siteIndex === 0 ? '馒头' : '观众'),
      icon: siteIcons[siteIndex % siteIcons.length],
      iconColor: siteColors[siteIndex % siteColors.length],
      percent: sitePercent(traffic),
      upload: formatGB(site.upload || 0),
      download: formatGB(site.download || 0),
    }
  })
});

const runtimeTasks = computed$5(() => {
  const sourceTasks = Array.isArray(dashboard.tasks) ? dashboard.tasks : [];
  return sourceTasks.map((task) => {
    const rawSchedule = String(task?.next_run || task?.schedule || task?.next || '已注册').trim();
    const schedule = dashboard.enabled === false
      ? '插件已停用'
      : (rawSchedule.startsWith('下次') ? rawSchedule : `下次 ${rawSchedule}`);
    return {
      key: task?.key || task?.service_id || task?.name,
      name: task?.name || '注册任务',
      enabled: dashboard.enabled !== false && task?.effective_enabled === true,
      state: task?.state || '',
      schedule,
    }
  }).filter(task => task.enabled)
});

const donutValue = computed$5(() => String(sitePieSegments.value.length || siteRows.value.length || 0));
const actionHint = computed$5(() => {
  if (!actionRunner.actionRunning.value) return ''
  return `${actionRunner.runningActionLabel.value || '当前动作'}执行中，请稍候。`
});
const actionFeedbackMessage = computed$5(() => actionHint.value || localActionMessage.value || actionRunner.actionMessage.value);
const actionFeedbackOk = computed$5(() => {
  if (actionHint.value) return true
  if (localActionMessage.value) return localActionOk.value
  return actionRunner.actionOk.value
});

async function loadFusionCard() {
  if (dashboard.enabled === false) {
    fusionCard.id = '';
    fusionCard.updatedAt = '';
    fusionCard.isBuilt = false;
    return
  }
  if (!props.api) return
  const response = await getPluginApiEnvelope(props.api, 'tg_console_status').catch(() => null);
  const payload = response?.data || response;
  if (!payload || typeof payload !== 'object') return
  fusionCard.id = String(payload.id || payload.message_id || fusionCard.id || '');
  fusionCard.updatedAt = String(payload.updated_at || payload.date || fusionCard.updatedAt || '');
  fusionCard.isBuilt = payload.built === true || Number(payload.message_id || 0) > 0 || payload.isBuilt === true;
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
      Object.assign(dashboard, {
        enabled: payload.enabled !== false,
        summary: payload.summary || '',
        tasks: Array.isArray(payload.tasks) ? payload.tasks : [],
        task_total: Number(payload.task_total || payload.taskTotal || payload.tasks?.length || dashboard.task_total),
        task_on: Number(payload.task_on || payload.taskOn || payload.tasks?.filter?.(task => task?.state !== false)?.length || dashboard.task_on),
        task_failed: Number(payload.task_failed || payload.taskFailed || 0),
        health: payload.health || dashboard.health,
      });
    }
    await Promise.all([loadSiteChart(), loadFusionCard()]);
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
  actionRunner.runAction(action);
}

function handleFusionBuild() {
  actionRunner.runAction({ key: 'fusion_build', label: '建卡', path: 'create_tg_console_card' });
}

function handleFusionRefresh() {
  actionRunner.runAction({ key: 'fusion_refresh', label: '刷新融合卡', path: 'run_daily_report' });
}

function switchPluginAppNav(navKey) {
  if (typeof window === 'undefined') return false
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
    surface: __props.surface,
    "theme-class": themeClass.value
  }, {
    default: _withCtx$2(() => [
      _createVNode$2(_sfc_main$i, {
        loading: loading.value,
        onRefresh: loadDashboard,
        onSettings: openSettings
      }, null, 8, ["loading"]),
      _createVNode$2(_sfc_main$f, { items: kpiItems.value }, null, 8, ["items"]),
      _createElementVNode("div", _hoisted_1, [
        _createVNode$2(_sfc_main$b, {
          "date-note": _unref$1(siteDateNote) || '今天 00:00 起',
          "donut-value": donutValue.value,
          "donut-label": "个站点",
          "donut-segments": _unref$1(sitePieSegments),
          "donut-style": _unref$1(sitePieStyle),
          "summary-rows": trafficSummaryRows.value,
          sites: siteCards.value
        }, null, 8, ["date-note", "donut-value", "donut-segments", "donut-style", "summary-rows", "sites"]),
        _createVNode$2(_sfc_main$8, { tasks: runtimeTasks.value }, null, 8, ["tasks"])
      ]),
      _createElementVNode("div", _hoisted_2, [
        _createVNode$2(_sfc_main$7, {
          actions: quickActions,
          "running-key": _unref$1(actionRunner).actionRunning.value,
          "feedback-message": actionFeedbackMessage.value,
          "feedback-ok": actionFeedbackOk.value,
          onAction: handleQuickAction
        }, null, 8, ["running-key", "feedback-message", "feedback-ok"]),
        _createVNode$2(_sfc_main$5, {
          "card-id": fusionCard.id,
          "updated-at": fusionCard.updatedAt,
          "is-built": fusionCard.isBuilt,
          enabled: dashboard.enabled !== false,
          refreshing: _unref$1(actionRunner).actionRunning.value === 'run_daily_report',
          building: _unref$1(actionRunner).actionRunning.value === 'create_tg_console_card',
          onBuild: handleFusionBuild,
          onRefresh: handleFusionRefresh
        }, null, 8, ["card-id", "updated-at", "is-built", "enabled", "refreshing", "building"])
      ]),
      (error.value)
        ? (_openBlock$4(), _createElementBlock("div", _hoisted_3, _toDisplayString(error.value), 1))
        : (loading.value)
          ? (_openBlock$4(), _createElementBlock("div", _hoisted_4, "正在刷新仪表盘..."))
          : _createCommentVNode$1("", true)
    ]),
    _: 1
  }, 8, ["surface", "theme-class"]))
}
}

};

const {computed: computed$4,reactive,ref} = await importShared('vue');

const mpFreeQuickActions = [
  { key: 'subscribe', label: '订阅追新', icon: v31Icons.rss, path: 'run_subscribe_reminder' },
  { key: 'transfer', label: '今日入库', icon: v31Icons.calendarToday, path: 'run_today_transfer' },
  { key: 'site_stat', label: '站点统计', icon: v31Icons.chartPie, path: 'run_site_stat' },
  { key: 'backup', label: '配置备份', icon: v31Icons.database, path: 'run_backup' },
  { key: 'log_clean', label: '日志清理', icon: v31Icons.broom, path: 'run_log_clean' },
  { key: 'health', label: '健康巡查', icon: v31Icons.heartPulse, path: 'run_health_check' },
  { key: 'mp_update', label: 'MP 更新', icon: v31Icons.refresh, path: 'run_mp_update' },
  { key: 'plugin_update', label: '插件更新', icon: v31Icons.cloudUpload, path: 'run_market_update' },
];

function useDashboardFreeData(api) {
  const loading = ref(false);
  const error = ref('');
  const dashboard = reactive({
    enabled: true,
    tasks: [],
    task_total: 0,
    task_on: 0,
    task_failed: 0,
    health: { success: true, output: '' },
  });

  const {
    siteChart,
    siteRows,
    siteTrafficTotal,
    siteDateNote,
    sitePieSegments,
    sitePieStyle,
    sitePercent,
    loadSiteChart,
  } = useSiteChart(api);

  const actionRunner = usePanelActionRunner({
    api: () => api,
    onSuccess: async ({ action }) => {
      if (action?.path === 'run_site_stat') await loadSiteChart();
    },
  });

  const trafficSummaryRows = computed$4(() => [
    { label: '上传增量', value: formatGB(siteChart.upload_total || 0), icon: v31Icons.arrowUp },
    { label: '下载增量', value: formatGB(siteChart.download_total || 0), icon: v31Icons.arrowDown },
    { label: '统计时间', value: siteChart.date || '等待统计', icon: v31Icons.calendarToday },
  ]);

  const siteCards = computed$4(() => {
    const siteIcons = [v31Icons.yinYang, v31Icons.eye, v31Icons.chartPie, v31Icons.leaf, v31Icons.database];
    const siteColors = ['#34C759', '#60A5FA', '#FFB020', '#AF52DE', '#64D2FF'];
    return siteRows.value.map((site, index) => {
      const traffic = Number(site.upload || 0) + Number(site.download || 0);
      return {
        name: site.name || `站点 ${index + 1}`,
        icon: siteIcons[index % siteIcons.length],
        iconColor: siteColors[index % siteColors.length],
        percent: sitePercent(traffic),
        upload: formatGB(site.upload || 0),
        download: formatGB(site.download || 0),
      }
    })
  });

  const runtimeTasks = computed$4(() => {
    const sourceTasks = Array.isArray(dashboard.tasks) ? dashboard.tasks : [];
    return sourceTasks.map((task) => {
      const rawSchedule = String(task?.next_run || task?.schedule || task?.next || '已注册').trim();
      return {
        key: task?.key || task?.service_id || task?.id || task?.name,
        name: task?.name || '注册任务',
        enabled: dashboard.enabled !== false && task?.effective_enabled === true,
        state: task?.state || '',
        schedule: rawSchedule.startsWith('下次') ? rawSchedule : `下次 ${rawSchedule}`,
      }
    }).filter(task => task.enabled)
  });

  const donutValue = computed$4(() => String(sitePieSegments.value.length || siteRows.value.length || 0));
  const dateNote = computed$4(() => siteDateNote.value || '今天 00:00 起');

  async function loadDashboard() {
    if (!api) return
    loading.value = true;
    error.value = '';
    try {
      const response = await getPluginApiEnvelope(api, 'dashboard');
      const payload = response?.data || response;
      if (payload && typeof payload === 'object') {
        Object.assign(dashboard, {
          enabled: payload.enabled !== false,
          tasks: Array.isArray(payload.tasks) ? payload.tasks : [],
          task_total: Number(payload.task_total || payload.taskTotal || payload.tasks?.length || 0),
          task_on: Number(payload.task_on || payload.taskOn || payload.tasks?.filter?.(task => task?.state !== false)?.length || 0),
          task_failed: Number(payload.task_failed || payload.taskFailed || 0),
          health: payload.health || dashboard.health,
        });
      }
      await loadSiteChart();
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
    siteCards,
    sitePieSegments,
    sitePieStyle,
    siteTrafficTotal,
    trafficSummaryRows,
    runtimeTasks,
    donutValue,
    dateNote,
    quickActions: mpFreeQuickActions,
    actionRunner,
    loadDashboard,
  }
}

const {createVNode:_createVNode$1,resolveComponent:_resolveComponent$1,withCtx:_withCtx$1,openBlock:_openBlock$3,createBlock:_createBlock$3} = await importShared('vue');


const {computed: computed$3} = await importShared('vue');


const _sfc_main$3 = {
  __name: 'MpSiteDataWidget',
  props: {
  data: { type: Object, required: true },
  frame: { type: Object, default: () => ({}) },
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
},
  setup(__props) {

const props = __props;

const dateNote = computed$3(() => props.data.dateNote?.value || '今天 00:00 起');
const donutValue = computed$3(() => props.data.donutValue?.value || '0');
const sitePieSegments = computed$3(() => props.data.sitePieSegments?.value || []);
const sitePieStyle = computed$3(() => props.data.sitePieStyle?.value || {});
const dashboardDonutStyle = computed$3(() => {
  const style = sitePieStyle.value;
  const background = typeof style?.background === 'string' ? style.background : '';
  if (!background) return style

  const dashboardPalette = {
    '--line': '255, 255, 255',
    '--green': '91, 204, 155',
    '--cyan': '124, 194, 224',
    '--blue': '142, 169, 222',
    '--amber': '218, 179, 93',
    '--red': '232, 104, 124',
    '--violet': '162, 151, 211',
  };

  return {
    ...style,
    background: Object.entries(dashboardPalette).reduce(
      (value, [token, color]) => value.replaceAll(`var(${token})`, color),
      background,
    ),
  }
});
const trafficSummaryRows = computed$3(() => props.data.trafficSummaryRows?.value || []);
const siteCards = computed$3(() => props.data.siteCards?.value || []);
const frameVariant = computed$3(() => props.frame?.variant || 'mp-native');
const frameDensity = computed$3(() => props.frame?.density || 'comfortable');

return (_ctx, _cache) => {
  const _component_VCard = _resolveComponent$1("VCard");

  return (_openBlock$3(), _createBlock$3(_component_VCard, {
    class: "aoa-mp-free-widget aoa-mp-native-card dashboard-summary-card dashboard-grid-fill",
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
      _createVNode$1(_sfc_main$b, {
        class: "aoa-finalized-site-content",
        "date-note": dateNote.value,
        "donut-value": donutValue.value,
        "donut-label": "个站点",
        "donut-segments": sitePieSegments.value,
        "donut-style": dashboardDonutStyle.value,
        "summary-rows": trafficSummaryRows.value,
        sites: siteCards.value
      }, null, 8, ["date-note", "donut-value", "donut-segments", "donut-style", "summary-rows", "sites"])
    ]),
    _: 1
  }, 8, ["data-mp-frame-variant", "data-mp-frame-density", "data-loading", "data-error"]))
}
}

};
const MpSiteDataWidget = /*#__PURE__*/_export_sfc(_sfc_main$3, [['__scopeId',"data-v-4824c996"]]);

const {createVNode:_createVNode,resolveComponent:_resolveComponent,withCtx:_withCtx,openBlock:_openBlock$2,createBlock:_createBlock$2} = await importShared('vue');


const {computed: computed$2} = await importShared('vue');


const _sfc_main$2 = {
  __name: 'MpQuickActionsWidget',
  props: {
  data: { type: Object, required: true },
  frame: { type: Object, default: () => ({}) },
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
},
  setup(__props) {

const props = __props;

const quickActions = computed$2(() => props.data.quickActions || []);
const actionRunner = computed$2(() => props.data.actionRunner || {});
const actionRunning = computed$2(() => actionRunner.value.actionRunning?.value || '');
const actionMessage = computed$2(() => actionRunner.value.actionMessage?.value || '');
const actionOk = computed$2(() => actionRunner.value.actionOk?.value !== false);
const frameVariant = computed$2(() => props.frame?.variant || 'mp-native');
const frameDensity = computed$2(() => props.frame?.density || 'compact');

function runAction(action) {
  actionRunner.value.runAction?.(action);
}

return (_ctx, _cache) => {
  const _component_VCard = _resolveComponent("VCard");

  return (_openBlock$2(), _createBlock$2(_component_VCard, {
    class: "aoa-mp-free-widget aoa-mp-native-card dashboard-summary-card dashboard-grid-fill",
    elevation: "0",
    rounded: "lg",
    "data-free-widget": "actions",
    "data-mp-frame-component": "actions",
    "data-module-root-is-frame": "true",
    "data-mp-frame-variant": frameVariant.value,
    "data-mp-frame-density": frameDensity.value,
    "data-loading": __props.loading ? 'true' : 'false',
    "data-error": __props.error ? 'true' : 'false'
  }, {
    default: _withCtx(() => [
      _createVNode(_sfc_main$7, {
        class: "aoa-finalized-actions-content",
        actions: quickActions.value,
        "running-key": actionRunning.value,
        "feedback-message": actionMessage.value,
        "feedback-ok": actionOk.value,
        onAction: runAction
      }, null, 8, ["actions", "running-key", "feedback-message", "feedback-ok"])
    ]),
    _: 1
  }, 8, ["data-mp-frame-variant", "data-mp-frame-density", "data-loading", "data-error"]))
}
}

};
const MpQuickActionsWidget = /*#__PURE__*/_export_sfc(_sfc_main$2, [['__scopeId',"data-v-caaec426"]]);

const {unref:_unref,resolveDynamicComponent:_resolveDynamicComponent,openBlock:_openBlock$1,createBlock:_createBlock$1} = await importShared('vue');


const {computed: computed$1,onMounted,watch} = await importShared('vue');

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

const currentComponent = computed$1(() => ({
  site: MpSiteDataWidget,
  actions: MpQuickActionsWidget,
}[widget.value] || MpSiteDataWidget));

watch(() => freeData.loading.value, value => emit('update:refreshStatus', value ? 'loading' : 'success'));
watch(() => freeData.error.value, value => {
  if (value) emit('update:refreshStatus', 'error');
});

onMounted(async () => {
  await freeData.loadDashboard();
  emit('loaded');
});

return (_ctx, _cache) => {
  return (_openBlock$1(), _createBlock$1(_resolveDynamicComponent(currentComponent.value), {
    data: _unref(freeData),
    frame: widgetFrame.value,
    loading: _unref(freeData).loading.value,
    error: _unref(freeData).error.value || fallbackMessage.value,
    "allow-refresh": __props.allowRefresh,
    onRefresh: _unref(freeData).loadDashboard
  }, null, 40, ["data", "frame", "loading", "error", "allow-refresh", "onRefresh"]))
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

return (_ctx, _cache) => {
  return (isMpFreeWidget.value)
    ? (_openBlock(), _createBlock(_sfc_main$1, {
        key: 0,
        api: __props.api,
        config: __props.config,
        "allow-refresh": __props.allowRefresh,
        surface: "mp-widget",
        "plugin-id": __props.pluginId,
        "onUpdate:refreshStatus": _cache[0] || (_cache[0] = value => emit('update:refreshStatus', value)),
        onLoaded: _cache[1] || (_cache[1] = $event => (emit('loaded')))
      }, null, 8, ["api", "config", "allow-refresh", "plugin-id"]))
    : (_openBlock(), _createBlock(_sfc_main$4, {
        key: 1,
        api: __props.api,
        config: __props.config,
        "allow-refresh": __props.allowRefresh,
        surface: effectiveSurface.value,
        "plugin-id": __props.pluginId,
        "onUpdate:refreshStatus": _cache[2] || (_cache[2] = value => emit('update:refreshStatus', value)),
        onLoaded: _cache[3] || (_cache[3] = $event => (emit('loaded'))),
        onClose: _cache[4] || (_cache[4] = $event => (emit('close'))),
        onSwitch: _cache[5] || (_cache[5] = $event => (emit('switch')))
      }, null, 8, ["api", "config", "allow-refresh", "surface", "plugin-id"]))
}
}

};

export { _sfc_main as default };
