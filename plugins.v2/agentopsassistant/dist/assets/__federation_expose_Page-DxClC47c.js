import { importShared } from './__federation_fn_import-JrT3xvdd.js';
import { _ as _export_sfc, g as getPluginApi, p as postPluginApi } from './_plugin-vue_export-helper-DGWTz_NE.js';

const {resolveComponent:_resolveComponent,createVNode:_createVNode,createElementVNode:_createElementVNode,createTextVNode:_createTextVNode,withCtx:_withCtx,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,toDisplayString:_toDisplayString,normalizeStyle:_normalizeStyle,renderList:_renderList,Fragment:_Fragment,createElementBlock:_createElementBlock,normalizeClass:_normalizeClass} = await importShared('vue');


const _hoisted_1 = { class: "agentops-dashboard" };
const _hoisted_2 = { class: "agentops-body" };
const _hoisted_3 = { class: "overview-strip" };
const _hoisted_4 = { class: "overview-item" };
const _hoisted_5 = { class: "overview-item" };
const _hoisted_6 = { class: "overview-item" };
const _hoisted_7 = { class: "overview-item" };
const _hoisted_8 = {
  key: 0,
  class: "site-stat-layout"
};
const _hoisted_9 = { class: "site-pie-wrap" };
const _hoisted_10 = { class: "site-pie-center" };
const _hoisted_11 = { class: "site-stat-content" };
const _hoisted_12 = { class: "site-summary" };
const _hoisted_13 = { class: "site-summary-item" };
const _hoisted_14 = { class: "site-summary-item" };
const _hoisted_15 = { class: "site-summary-item" };
const _hoisted_16 = { class: "site-legend" };
const _hoisted_17 = { class: "site-name" };
const _hoisted_18 = { class: "site-traffic" };
const _hoisted_19 = { class: "site-percent" };
const _hoisted_20 = {
  key: 1,
  class: "site-empty"
};
const _hoisted_21 = { class: "action-scroll" };
const _hoisted_22 = { class: "action-buttons" };
const _hoisted_23 = { class: "action-btn-main" };
const _hoisted_24 = { class: "action-btn-label" };
const _hoisted_25 = { class: "action-btn-desc" };
const _hoisted_26 = { class: "task-grid" };
const _hoisted_27 = { class: "task-head" };
const _hoisted_28 = { class: "task-title-wrap" };
const _hoisted_29 = { class: "task-name" };
const _hoisted_30 = { class: "task-meta" };
const _hoisted_31 = { class: "task-foot" };
const _hoisted_32 = {
  key: 0,
  class: "panel-note"
};
const _hoisted_33 = {
  key: 1,
  class: "health-grid"
};
const _hoisted_34 = { class: "health-card-head" };
const _hoisted_35 = {
  key: 2,
  class: "empty-soft"
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
const data = reactive({
  enabled: false,
  summary: '',
  tasks: [],
  task_total: 0,
  task_on: 0,
  task_failed: 0,
  health: { time: '', success: null, output: '' },
});

const overallColor = computed(() => {
  if (!data.enabled) return 'default'
  if (data.task_failed > 0) return 'error'
  return 'success'
});
const overallText = computed(() => {
  if (!data.enabled) return '未启用'
  if (data.task_failed > 0) return `${data.task_failed} 项异常`
  return '运行正常'
});
const healthColor = computed(() => {
  if (data.health.success === true) return 'success'
  if (data.health.success === false) return 'error'
  return 'grey'
});
const healthText = computed(() => {
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
  try {
    const res = await postPluginApi(props.api, path);
    const ok = !res || res.code === 0 || res.code === undefined;
    actionMessage.value = (res && res.msg) || `${label}已${ok ? '完成' : '失败'}`;
    setTimeout(() => { actionMessage.value = ''; }, 5000);
    if (ok) {
      loadDashboard();
      loadSiteChart();
      loadDownloaderOverview();
    }
  } catch (err) {
    actionMessage.value = err?.message || `${label}失败`;
    setTimeout(() => { actionMessage.value = ''; }, 5000);
  } finally {
    actionRunning.value = '';
  }
}

const siteChart = reactive({ date: '', basis: 'today', sites: [], upload_total: 0, download_total: 0 });
function formatGB(bytes) {
  const n = Number(bytes) || 0;
  const gb = n / (1024 ** 3);
  if (gb >= 1) return gb.toFixed(2) + ' GB'
  return (n / (1024 ** 2)).toFixed(1) + ' MB'
}
const siteRows = computed(() => [...(siteChart.sites || [])].sort((a, b) => ((b.upload || 0) + (b.download || 0)) - ((a.upload || 0) + (a.download || 0))));
const sitePieColors = ['#22c55e', '#38bdf8', '#f59e0b', '#a78bfa', '#fb7185', '#14b8a6', '#eab308', '#60a5fa'];
const siteTrafficTotal = computed(() => siteRows.value.reduce((sum, site) => sum + (Number(site.upload) || 0) + (Number(site.download) || 0), 0));
const siteDateLabel = computed(() => {
  if (!siteChart.date) return '—'
  return siteChart.basis === 'latest' ? `最近快照 ${siteChart.date}` : siteChart.date
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
    return { ...site, value, start, end, color: sitePieColors[index % sitePieColors.length] }
  })
});
const sitePieStyle = computed(() => {
  if (!sitePieSegments.value.length) {
    return { background: 'rgba(var(--v-theme-on-surface), 0.08)' }
  }
  const stops = sitePieSegments.value
    .map(item => `${item.color} ${item.start.toFixed(2)}% ${item.end.toFixed(2)}%`)
    .join(', ');
  return { background: `conic-gradient(${stops})` }
});
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
    /* 无站点数据时静默不显示 */
  }
}

const downloaders = ref([]);
async function loadDownloaderOverview() {
  try {
    const res = await getPluginApi(props.api, 'downloader_overview');
    downloaders.value = (res && res.downloaders) || [];
  } catch {
    downloaders.value = [];
  }
}

const hasSiteChart = computed(() => !!(siteChart.sites && siteChart.sites.length));
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

// 手动触发按钮分组
const actionGroups = [
  {
    group: '汇报中心',
    icon: 'mdi-newspaper-variant-outline',
    actions: [
      { path: 'run_daily_report', label: '每日汇报', icon: 'mdi-send-clock-outline', desc: '发送完整日报', tone: 'green' },
    ]
  },
  {
    group: '订阅与站点',
    icon: 'mdi-bell-ring-outline',
    actions: [
      { path: 'run_subscribe_reminder', label: '订阅追新', icon: 'mdi-bell-badge-outline', desc: '推送今日追新', tone: 'blue' },
      { path: 'run_site_stat', label: '站点统计', icon: 'mdi-chart-pie', desc: '刷新增量数据', tone: 'blue' },
    ]
  },
  {
    group: '下载与媒体',
    icon: 'mdi-download-network-outline',
    actions: [
      { path: 'run_downloader_tag', label: '种子标签', icon: 'mdi-tag-plus-outline', desc: '按站点补标签', tone: 'cyan' },
      { path: 'run_seed_clean', label: '自动删种', icon: 'mdi-delete-sweep-outline', desc: '执行删种规则', tone: 'red' },
    ]
  },
  {
    group: '系统维护',
    icon: 'mdi-cog-outline',
    actions: [
      { path: 'run_backup', label: '配置备份', icon: 'mdi-database-arrow-up-outline', desc: '备份关键配置', tone: 'purple' },
      { path: 'run_log_clean', label: '日志清理', icon: 'mdi-broom', desc: '清理插件日志', tone: 'purple' },
      { path: 'run_health_check', label: '健康巡查', icon: 'mdi-heart-pulse', desc: '检查运行健康', tone: 'green' },
      { path: 'run_mp_update', label: 'MP 更新', icon: 'mdi-update', desc: '检查主程序更新', tone: 'amber' },
      { path: 'run_market_update', label: '插件更新', icon: 'mdi-puzzle-check-outline', desc: '检查插件市场', tone: 'amber' },
    ]
  }
];
const actionItems = computed(() => actionGroups.flatMap(group => group.actions));

onMounted(() => { loadDashboard(); loadSiteChart(); loadDownloaderOverview(); });

return (_ctx, _cache) => {
  const _component_VIcon = _resolveComponent("VIcon");
  const _component_VSpacer = _resolveComponent("VSpacer");
  const _component_VBtn = _resolveComponent("VBtn");
  const _component_VToolbar = _resolveComponent("VToolbar");
  const _component_VDivider = _resolveComponent("VDivider");
  const _component_VAlert = _resolveComponent("VAlert");
  const _component_VCardTitle = _resolveComponent("VCardTitle");
  const _component_VCardText = _resolveComponent("VCardText");
  const _component_VCard = _resolveComponent("VCard");
  const _component_VCol = _resolveComponent("VCol");
  const _component_VRow = _resolveComponent("VRow");
  const _component_VListItemTitle = _resolveComponent("VListItemTitle");
  const _component_VListItemSubtitle = _resolveComponent("VListItemSubtitle");
  const _component_VListItem = _resolveComponent("VListItem");
  const _component_VList = _resolveComponent("VList");
  const _component_VSkeletonLoader = _resolveComponent("VSkeletonLoader");
  const _component_VAvatar = _resolveComponent("VAvatar");
  const _component_VChip = _resolveComponent("VChip");

  return (_openBlock(), _createElementBlock("div", _hoisted_1, [
    _createVNode(_component_VCard, {
      class: "agentops-card",
      elevation: "0"
    }, {
      default: _withCtx(() => [
        _createVNode(_component_VToolbar, {
          density: "compact",
          class: "agentops-toolbar"
        }, {
          default: _withCtx(() => [
            _createVNode(_component_VIcon, {
              icon: "mdi-view-dashboard-outline",
              class: "ms-3 me-2",
              color: "primary"
            }),
            _cache[5] || (_cache[5] = _createElementVNode("div", { class: "text-subtitle-1 font-weight-bold" }, "MP 运维助手 · 仪表盘", -1)),
            _createVNode(_component_VSpacer),
            _createVNode(_component_VBtn, {
              size: "small",
              color: "primary",
              variant: "tonal",
              "prepend-icon": "mdi-refresh",
              class: "text-none me-1",
              loading: loading.value,
              onClick: loadDashboard
            }, {
              default: _withCtx(() => [...(_cache[3] || (_cache[3] = [
                _createTextVNode("刷新", -1)
              ]))]),
              _: 1
            }, 8, ["loading"]),
            _createVNode(_component_VBtn, {
              size: "small",
              variant: "text",
              "prepend-icon": "mdi-cog-outline",
              class: "text-none",
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
              onClick: _cache[1] || (_cache[1] = $event => (emit('close')))
            })
          ]),
          _: 1
        }),
        _createVNode(_component_VDivider),
        _createElementVNode("div", _hoisted_2, [
          (error.value)
            ? (_openBlock(), _createBlock(_component_VAlert, {
                key: 0,
                type: "error",
                variant: "tonal",
                class: "mb-3",
                icon: false,
                text: error.value
              }, null, 8, ["text"]))
            : _createCommentVNode("", true),
          _createElementVNode("div", _hoisted_3, [
            _createElementVNode("div", _hoisted_4, [
              _createVNode(_component_VIcon, {
                icon: "mdi-shield-check-outline",
                color: overallColor.value,
                size: "22"
              }, null, 8, ["color"]),
              _cache[6] || (_cache[6] = _createElementVNode("span", null, "运行状态", -1)),
              _createElementVNode("strong", null, _toDisplayString(overallText.value), 1)
            ]),
            _createElementVNode("div", _hoisted_5, [
              _createVNode(_component_VIcon, {
                icon: "mdi-view-grid-check-outline",
                color: "primary",
                size: "22"
              }),
              _cache[7] || (_cache[7] = _createElementVNode("span", null, "启用组件", -1)),
              _createElementVNode("strong", null, _toDisplayString(data.task_on) + " / " + _toDisplayString(data.task_total), 1)
            ]),
            _createElementVNode("div", _hoisted_6, [
              _createVNode(_component_VIcon, {
                icon: data.task_failed > 0 ? 'mdi-close-circle-outline' : 'mdi-check-circle-outline',
                color: data.task_failed > 0 ? 'error' : 'success',
                size: "22"
              }, null, 8, ["icon", "color"]),
              _cache[8] || (_cache[8] = _createElementVNode("span", null, "异常组件", -1)),
              _createElementVNode("strong", null, _toDisplayString(data.task_failed), 1)
            ]),
            _createElementVNode("div", _hoisted_7, [
              _createVNode(_component_VIcon, {
                icon: "mdi-heart-pulse",
                color: healthColor.value,
                size: "22"
              }, null, 8, ["color"]),
              _cache[9] || (_cache[9] = _createElementVNode("span", null, "健康巡查", -1)),
              _createElementVNode("strong", null, _toDisplayString(healthText.value), 1)
            ])
          ]),
          _createVNode(_component_VRow, {
            dense: "",
            class: "mt-2 dashboard-main-grid"
          }, {
            default: _withCtx(() => [
              _createVNode(_component_VCol, {
                cols: "12",
                lg: "8"
              }, {
                default: _withCtx(() => [
                  _createVNode(_component_VCard, {
                    elevation: "0",
                    class: "glass-panel site-stat-panel h-100"
                  }, {
                    default: _withCtx(() => [
                      _createVNode(_component_VCardTitle, { class: "compact-card-title" }, {
                        default: _withCtx(() => [
                          _createVNode(_component_VIcon, {
                            icon: "mdi-chart-pie",
                            color: "primary",
                            class: "me-2"
                          }),
                          _cache[11] || (_cache[11] = _createTextVNode("站点数据统计 ", -1)),
                          _createVNode(_component_VSpacer),
                          _createVNode(_component_VBtn, {
                            size: "small",
                            variant: "tonal",
                            color: "primary",
                            "prepend-icon": "mdi-refresh",
                            loading: actionRunning.value === 'run_site_stat',
                            onClick: _cache[2] || (_cache[2] = $event => (runAction('run_site_stat', '刷新站点数据')))
                          }, {
                            default: _withCtx(() => [...(_cache[10] || (_cache[10] = [
                              _createTextVNode(" 刷新 ", -1)
                            ]))]),
                            _: 1
                          }, 8, ["loading"])
                        ]),
                        _: 1
                      }),
                      _createVNode(_component_VCardText, { class: "compact-card-text" }, {
                        default: _withCtx(() => [
                          (hasSiteChart.value)
                            ? (_openBlock(), _createElementBlock("div", _hoisted_8, [
                                _createElementVNode("div", _hoisted_9, [
                                  _createElementVNode("div", {
                                    class: "site-pie",
                                    style: _normalizeStyle(sitePieStyle.value)
                                  }, [
                                    _createElementVNode("div", _hoisted_10, [
                                      _createElementVNode("strong", null, _toDisplayString(siteRows.value.length), 1),
                                      _cache[12] || (_cache[12] = _createElementVNode("span", null, "站点", -1))
                                    ])
                                  ], 4)
                                ]),
                                _createElementVNode("div", _hoisted_11, [
                                  _createElementVNode("div", _hoisted_12, [
                                    _createElementVNode("div", _hoisted_13, [
                                      _createVNode(_component_VIcon, {
                                        icon: "mdi-upload-network-outline",
                                        color: "success",
                                        size: "20"
                                      }),
                                      _cache[13] || (_cache[13] = _createElementVNode("span", null, "上传增量", -1)),
                                      _createElementVNode("strong", null, _toDisplayString(formatGB(siteChart.upload_total)), 1)
                                    ]),
                                    _createElementVNode("div", _hoisted_14, [
                                      _createVNode(_component_VIcon, {
                                        icon: "mdi-download-network-outline",
                                        color: "info",
                                        size: "20"
                                      }),
                                      _cache[14] || (_cache[14] = _createElementVNode("span", null, "下载增量", -1)),
                                      _createElementVNode("strong", null, _toDisplayString(formatGB(siteChart.download_total)), 1)
                                    ]),
                                    _createElementVNode("div", _hoisted_15, [
                                      _createVNode(_component_VIcon, {
                                        icon: "mdi-calendar-blank-outline",
                                        color: "primary",
                                        size: "20"
                                      }),
                                      _cache[15] || (_cache[15] = _createElementVNode("span", null, "统计日期", -1)),
                                      _createElementVNode("strong", null, _toDisplayString(siteDateLabel.value), 1)
                                    ])
                                  ]),
                                  _createElementVNode("div", _hoisted_16, [
                                    (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(sitePieSegments.value, (site) => {
                                      return (_openBlock(), _createElementBlock("div", {
                                        key: site.name,
                                        class: "site-legend-row"
                                      }, [
                                        _createElementVNode("span", {
                                          class: "site-dot",
                                          style: _normalizeStyle({ background: site.color })
                                        }, null, 4),
                                        _createElementVNode("strong", _hoisted_17, _toDisplayString(site.name), 1),
                                        _createElementVNode("span", _hoisted_18, "↑ " + _toDisplayString(formatGB(site.upload)) + " ｜ ↓ " + _toDisplayString(formatGB(site.download)), 1),
                                        _createElementVNode("span", _hoisted_19, _toDisplayString(sitePercent(site.value)), 1)
                                      ]))
                                    }), 128))
                                  ])
                                ])
                              ]))
                            : (_openBlock(), _createElementBlock("div", _hoisted_20, [
                                _createVNode(_component_VIcon, {
                                  icon: "mdi-chart-pie",
                                  size: "24",
                                  color: "primary"
                                }),
                                _cache[16] || (_cache[16] = _createElementVNode("div", null, [
                                  _createElementVNode("div", { class: "font-weight-medium" }, "暂无站点增量"),
                                  _createElementVNode("div", { class: "text-caption text-medium-emphasis" }, "刷新后显示最近可用快照")
                                ], -1))
                              ]))
                        ]),
                        _: 1
                      })
                    ]),
                    _: 1
                  })
                ]),
                _: 1
              }),
              _createVNode(_component_VCol, {
                cols: "12",
                lg: "4"
              }, {
                default: _withCtx(() => [
                  _createVNode(_component_VCard, {
                    elevation: "0",
                    class: "glass-panel action-panel h-100"
                  }, {
                    default: _withCtx(() => [
                      _createVNode(_component_VCardText, { class: "compact-card-text action-panel-body" }, {
                        default: _withCtx(() => [
                          _createElementVNode("div", _hoisted_21, [
                            _createElementVNode("div", _hoisted_22, [
                              (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(actionItems.value, (action) => {
                                return (_openBlock(), _createElementBlock("div", {
                                  key: action.path,
                                  class: "action-item"
                                }, [
                                  _createVNode(_component_VBtn, {
                                    block: "",
                                    variant: "text",
                                    density: "comfortable",
                                    loading: actionRunning.value === action.path,
                                    onClick: $event => (runAction(action.path, action.label)),
                                    class: _normalizeClass(["action-btn text-none", `action-btn--${action.tone}`])
                                  }, {
                                    default: _withCtx(() => [
                                      _createElementVNode("span", _hoisted_23, [
                                        _createVNode(_component_VIcon, {
                                          icon: action.icon,
                                          size: "18"
                                        }, null, 8, ["icon"]),
                                        _createElementVNode("span", _hoisted_24, _toDisplayString(action.label), 1)
                                      ])
                                    ]),
                                    _: 2
                                  }, 1032, ["loading", "onClick", "class"]),
                                  _createElementVNode("span", _hoisted_25, _toDisplayString(action.desc), 1)
                                ]))
                              }), 128))
                            ])
                          ]),
                          (actionMessage.value)
                            ? (_openBlock(), _createBlock(_component_VAlert, {
                                key: 0,
                                type: "info",
                                variant: "tonal",
                                density: "compact",
                                class: "mt-3",
                                icon: false,
                                text: actionMessage.value
                              }, null, 8, ["text"]))
                            : _createCommentVNode("", true)
                        ]),
                        _: 1
                      })
                    ]),
                    _: 1
                  })
                ]),
                _: 1
              })
            ]),
            _: 1
          }),
          (downloaders.value.length)
            ? (_openBlock(), _createBlock(_component_VCard, {
                key: 1,
                elevation: "0",
                class: "glass-panel mt-2"
              }, {
                default: _withCtx(() => [
                  _createVNode(_component_VCardTitle, { class: "compact-card-title" }, {
                    default: _withCtx(() => [
                      _createVNode(_component_VIcon, {
                        icon: "mdi-download-network-outline",
                        color: "primary",
                        class: "me-2"
                      }),
                      _cache[17] || (_cache[17] = _createTextVNode("下载器活动种子 ", -1))
                    ]),
                    _: 1
                  }),
                  _createVNode(_component_VList, {
                    class: "bg-transparent py-0",
                    density: "compact"
                  }, {
                    default: _withCtx(() => [
                      (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(downloaders.value, (d, i) => {
                        return (_openBlock(), _createBlock(_component_VListItem, {
                          key: d.name,
                          class: "py-1"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VListItemTitle, { class: "font-weight-medium" }, {
                              default: _withCtx(() => [
                                _createTextVNode(_toDisplayString(d.name), 1)
                              ]),
                              _: 2
                            }, 1024),
                            _createVNode(_component_VListItemSubtitle, { class: "mt-1" }, {
                              default: _withCtx(() => [
                                _createTextVNode("下载中 " + _toDisplayString(d.count) + " 个｜↓ " + _toDisplayString(formatGB(d.dl_speed)) + "/s　↑ " + _toDisplayString(formatGB(d.up_speed)) + "/s", 1)
                              ]),
                              _: 2
                            }, 1024)
                          ]),
                          _: 2
                        }, 1024))
                      }), 128))
                    ]),
                    _: 1
                  })
                ]),
                _: 1
              }))
            : _createCommentVNode("", true),
          _createVNode(_component_VRow, {
            dense: "",
            class: "mt-2"
          }, {
            default: _withCtx(() => [
              _createVNode(_component_VCol, {
                cols: "12",
                md: "6"
              }, {
                default: _withCtx(() => [
                  _createVNode(_component_VCard, {
                    elevation: "0",
                    class: "glass-panel h-100"
                  }, {
                    default: _withCtx(() => [
                      _createVNode(_component_VCardTitle, { class: "compact-card-title" }, {
                        default: _withCtx(() => [
                          _createVNode(_component_VIcon, {
                            icon: "mdi-view-grid-check-outline",
                            color: "primary",
                            class: "me-2"
                          }),
                          _cache[18] || (_cache[18] = _createTextVNode("组件运行状况 ", -1))
                        ]),
                        _: 1
                      }),
                      (loading.value)
                        ? (_openBlock(), _createBlock(_component_VSkeletonLoader, {
                            key: 0,
                            type: "list-item-avatar-three-line@3"
                          }))
                        : (_openBlock(), _createBlock(_component_VCardText, {
                            key: 1,
                            class: "compact-card-text"
                          }, {
                            default: _withCtx(() => [
                              _createElementVNode("div", _hoisted_26, [
                                (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(data.tasks, (task) => {
                                  return (_openBlock(), _createElementBlock("div", {
                                    key: task.key,
                                    class: "task-card"
                                  }, [
                                    _createElementVNode("div", _hoisted_27, [
                                      _createVNode(_component_VAvatar, {
                                        size: "34",
                                        variant: "tonal",
                                        color: task.enabled ? task.color : 'default'
                                      }, {
                                        default: _withCtx(() => [
                                          _createVNode(_component_VIcon, {
                                            icon: task.icon,
                                            size: "18"
                                          }, null, 8, ["icon"])
                                        ]),
                                        _: 2
                                      }, 1032, ["color"]),
                                      _createElementVNode("div", _hoisted_28, [
                                        _createElementVNode("div", _hoisted_29, _toDisplayString(task.name), 1),
                                        _createElementVNode("div", _hoisted_30, "下次 " + _toDisplayString(task.next || '—'), 1)
                                      ]),
                                      _createVNode(_component_VChip, {
                                        size: "x-small",
                                        variant: "tonal",
                                        color: task.enabled ? 'success' : 'default'
                                      }, {
                                        default: _withCtx(() => [
                                          _createTextVNode(_toDisplayString(task.enabled ? 'ON' : 'OFF'), 1)
                                        ]),
                                        _: 2
                                      }, 1032, ["color"])
                                    ]),
                                    _createElementVNode("div", _hoisted_31, [
                                      _createElementVNode("span", null, "最近 " + _toDisplayString(task.last_time || '—'), 1),
                                      _createVNode(_component_VChip, {
                                        size: "x-small",
                                        variant: "tonal",
                                        color: task.color
                                      }, {
                                        default: _withCtx(() => [
                                          _createTextVNode(_toDisplayString(task.state), 1)
                                        ]),
                                        _: 2
                                      }, 1032, ["color"])
                                    ])
                                  ]))
                                }), 128))
                              ])
                            ]),
                            _: 1
                          }))
                    ]),
                    _: 1
                  })
                ]),
                _: 1
              }),
              _createVNode(_component_VCol, {
                cols: "12",
                md: "6"
              }, {
                default: _withCtx(() => [
                  _createVNode(_component_VCard, {
                    elevation: "0",
                    class: "glass-panel h-100"
                  }, {
                    default: _withCtx(() => [
                      _createVNode(_component_VCardTitle, { class: "compact-card-title" }, {
                        default: _withCtx(() => [
                          _createVNode(_component_VIcon, {
                            icon: "mdi-heart-pulse",
                            color: "primary",
                            class: "me-2"
                          }),
                          _cache[19] || (_cache[19] = _createTextVNode("健康巡查 ", -1)),
                          _createVNode(_component_VSpacer),
                          _createVNode(_component_VChip, {
                            size: "x-small",
                            variant: "tonal",
                            color: healthColor.value
                          }, {
                            default: _withCtx(() => [
                              _createTextVNode(_toDisplayString(healthText.value), 1)
                            ]),
                            _: 1
                          }, 8, ["color"])
                        ]),
                        _: 1
                      }),
                      _createVNode(_component_VCardText, { class: "compact-card-text" }, {
                        default: _withCtx(() => [
                          (data.health.time)
                            ? (_openBlock(), _createElementBlock("div", _hoisted_32, "最近 " + _toDisplayString(data.health.time), 1))
                            : _createCommentVNode("", true),
                          (healthItems.value.length)
                            ? (_openBlock(), _createElementBlock("div", _hoisted_33, [
                                (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(healthItems.value, (item) => {
                                  return (_openBlock(), _createElementBlock("div", {
                                    key: item.name,
                                    class: _normalizeClass(["health-card", { 'health-card--bad': !item.ok }])
                                  }, [
                                    _createElementVNode("div", _hoisted_34, [
                                      _createVNode(_component_VIcon, {
                                        icon: item.icon,
                                        color: item.color,
                                        size: "20"
                                      }, null, 8, ["icon", "color"]),
                                      _createElementVNode("strong", null, _toDisplayString(item.name), 1),
                                      _createVNode(_component_VChip, {
                                        size: "x-small",
                                        variant: "tonal",
                                        color: item.color
                                      }, {
                                        default: _withCtx(() => [
                                          _createTextVNode(_toDisplayString(item.ok ? '正常' : '异常'), 1)
                                        ]),
                                        _: 2
                                      }, 1032, ["color"])
                                    ]),
                                    _createElementVNode("div", {
                                      class: _normalizeClass(["health-detail", { 'health-detail--bad': !item.ok }])
                                    }, [
                                      (!item.ok && item.detailRows.length > 1)
                                        ? (_openBlock(true), _createElementBlock(_Fragment, { key: 0 }, _renderList(item.detailRows, (row) => {
                                            return (_openBlock(), _createElementBlock("div", {
                                              key: row,
                                              class: "health-detail-row"
                                            }, _toDisplayString(row), 1))
                                          }), 128))
                                        : (_openBlock(), _createElementBlock(_Fragment, { key: 1 }, [
                                            _createTextVNode(_toDisplayString(item.detail), 1)
                                          ], 64))
                                    ], 2)
                                  ], 2))
                                }), 128))
                              ]))
                            : (_openBlock(), _createElementBlock("div", _hoisted_35, "暂无记录"))
                        ]),
                        _: 1
                      })
                    ]),
                    _: 1
                  })
                ]),
                _: 1
              })
            ]),
            _: 1
          })
        ])
      ]),
      _: 1
    })
  ]))
}
}

};
const Page = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-2c53d16a"]]);

export { Page as default };
