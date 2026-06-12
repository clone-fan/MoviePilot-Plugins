import { importShared } from './__federation_fn_import-JrT3xvdd.js';

const _export_sfc = (sfc, props) => {
  const target = sfc.__vccOpts || sfc;
  for (const [key, val] of props) {
    target[key] = val;
  }
  return target;
};

const {createElementVNode:_createElementVNode,resolveComponent:_resolveComponent,createVNode:_createVNode,createTextVNode:_createTextVNode,withCtx:_withCtx,renderList:_renderList,Fragment:_Fragment,openBlock:_openBlock,createElementBlock:_createElementBlock,toDisplayString:_toDisplayString,createBlock:_createBlock,createCommentVNode:_createCommentVNode,unref:_unref} = await importShared('vue');


const _hoisted_1 = { class: "agentops-config" };
const _hoisted_2 = { class: "pa-3" };
const _hoisted_3 = { class: "d-flex flex-wrap ga-2" };

const {computed,reactive,watch} = await importShared('vue');



const _sfc_main = {
  __name: 'Config',
  props: { initialConfig: { type: Object, default: () => ({}) } },
  emits: ['save', 'close'],
  setup(__props, { emit: __emit }) {

const props = __props;
const emit = __emit;

const form = reactive({});
const activeMain = reactive({ value: 'report' });
const activeSub = reactive({
  report: 'basic',
  notices: 'subscribe',
  backup: 'local',
  cleanup: 'logs',
  updates: 'mp',
  plugin: 'target',
});

const defaults = {
  enabled: false,
  daily_report_enabled: true,
  daily_report_cron: '0 22 * * *',
  health_in_report: true,
  subscribe_in_report: true,
  site_stat_in_report: true,
  subscribe_reminder_enabled: true,
  subscribe_reminder_onlyonce: false,
  subscribe_reminder_time: '9',
  subscribe_reminder_subtype: ['movie', 'tv'],
  subscribe_reminder_msgtype: 'Subscribe',
  site_stat_enabled: true,
  site_stat_onlyonce: false,
  site_stat_dashboard_type: 'today',
  site_stat_notify_type: 'inc',
  log_clean_enabled: false,
  log_clean_cron: '0 3 * * 1',
  log_clean_rows: 300,
  log_clean_selected_ids: '',
  log_clean_notify: true,
  log_clean_onlyonce: false,
  backup_enabled: false,
  backup_onlyonce: false,
  backup_cron: '0 4 * * 1',
  backup_keep_count: 5,
  backup_path: '/config/plugins/AgentOpsAssistant/Backup',
  backup_notify: true,
  backup_webdav_enabled: false,
  backup_webdav_notify: false,
  backup_webdav_digest_auth: false,
  backup_webdav_disable_check: false,
  backup_webdav_hostname: '',
  backup_webdav_login: '',
  backup_webdav_password: '',
  backup_webdav_max_count: 5,
  mp_update_enabled: false,
  mp_update_cron: '0 9 * * *',
  mp_update_notify: true,
  mp_update_restart_confirm: false,
  mp_update_types: ['后端', '前端'],
  market_update_enabled: false,
  market_update_onlyonce: false,
  market_update_interval: 86400,
  market_update_notify: true,
  market_update_write_notify: false,
  market_update_notify_type: 'Plugin',
  market_update_write_settings: false,
  market_update_write_env: false,
  market_update_blacklist_enabled: false,
  market_update_blacklist: '',
  market_update_auto_get: false,
  market_update_proxy: true,
  market_update_timeout: 5,
  market_update_wiki_url: 'https://wiki.movie-pilot.org/zh/plugin',
  market_update_wiki_xpath: '//pre[@class="prismjs line-numbers" and @v-pre="true"]/code/text()',
  plugin_uninstall_id: '',
  plugin_uninstall_ids: [],
  plugin_uninstall_clear_config: true,
  plugin_uninstall_clear_data: true,
  plugin_uninstall_delete_source: false,
  plugin_uninstall_notify: true,
};

const mainTabs = [
  { key: 'report', title: '每日汇报', icon: 'mdi-newspaper-variant-outline', color: 'primary', desc: '设置每日汇报是否发送、发送时间和栏目内容。' },
  { key: 'notices', title: '订阅与站点', icon: 'mdi-bell-cog-outline', color: 'cyan', desc: '设置订阅提醒和站点统计是否写入汇报或单独通知。' },
  { key: 'backup', title: '自动备份', icon: 'mdi-archive-arrow-up-outline', color: 'success', desc: '设置本地备份、保留数量和 WebDAV 远端备份。' },
  { key: 'cleanup', title: '日志清理', icon: 'mdi-file-document-remove-outline', color: 'warning', desc: '设置插件日志保留行数、清理时间和结果通知。' },
  { key: 'updates', title: '更新检查', icon: 'mdi-update', color: 'info', desc: '设置 MoviePilot 和插件库更新检查，不在这里直接升级。' },
  { key: 'plugin', title: '插件残留清理', icon: 'mdi-puzzle-remove-outline', color: 'deep-orange', desc: '检查并清理已卸载插件留下的配置、数据、日志或本地源码残留。' },
];

const subTabs = {
  report: [
    { key: 'basic', title: '基础设置', icon: 'mdi-tune-variant' },
    { key: 'columns', title: '汇报栏目', icon: 'mdi-view-list-outline' },
  ],
  notices: [
    { key: 'subscribe', title: '订阅提醒', icon: 'mdi-bell-ring-outline' },
    { key: 'sites', title: '站点统计', icon: 'mdi-chart-line' },
  ],
  backup: [
    { key: 'local', title: '本地备份', icon: 'mdi-folder-arrow-up-outline' },
    { key: 'webdav', title: 'WebDAV', icon: 'mdi-cloud-upload-outline' },
  ],
  cleanup: [
    { key: 'logs', title: '插件日志', icon: 'mdi-file-document-remove-outline' },
  ],
  updates: [
    { key: 'mp', title: '主程序', icon: 'mdi-movie-open-cog-outline' },
    { key: 'market', title: '插件库', icon: 'mdi-puzzle-plus-outline' },
  ],
  plugin: [
    { key: 'target', title: '目标插件', icon: 'mdi-crosshairs-gps' },
    { key: 'scope', title: '清理范围', icon: 'mdi-folder-remove-outline' },
  ],
};

const cronPresets = [
  { title: '每天 22:00', value: '0 22 * * *' },
  { title: '每天 09:00', value: '0 9 * * *' },
  { title: '每周一 03:00', value: '0 3 * * 1' },
  { title: '每周一 04:00', value: '0 4 * * 1' },
];
const subscribeSubtypeItems = [{ title: '电影', value: 'movie' }, { title: '电视剧', value: 'tv' }];
const messageTypeItems = [{ title: '订阅', value: 'Subscribe' }, { title: '插件', value: 'Plugin' }, { title: '手动处理', value: 'Manual' }];
const siteStatRangeItems = [{ title: '今日数据', value: 'today' }, { title: '汇总数据', value: 'total' }, { title: '所有数据', value: 'all' }];
const siteNotifyItems = [{ title: '增量变化', value: 'inc' }, { title: '全部数据', value: 'all' }, { title: '不通知', value: 'none' }];
const marketNotifyItems = [{ title: '插件通知', value: 'Plugin' }, { title: '手动处理', value: 'Manual' }];
const mpUpdateTypes = ['后端', '前端'].map(v => ({ title: v, value: v }));
const keepCountPresets = [3, 5, 7, 10, 15].map(v => ({ title: `保留 ${v} 份`, value: v }));
const logRowsPresets = [100, 300, 500, 1000, 2000].map(v => ({ title: `保留 ${v} 行`, value: v }));
const intervalPresets = [3600, 21600, 43200, 86400, 604800].map(v => ({ title: v < 86400 ? `${v / 3600} 小时` : `${v / 86400} 天`, value: v }));

const currentMain = computed(() => mainTabs.find(item => item.key === activeMain.value) || mainTabs[0]);

watch(() => props.initialConfig, value => {
  Object.keys(form).forEach(key => delete form[key]);
  Object.assign(form, defaults, value || {});
  if (typeof form.subscribe_reminder_subtype === 'string') form.subscribe_reminder_subtype = form.subscribe_reminder_subtype.split(',').map(v => v.trim()).filter(Boolean);
  if (typeof form.mp_update_types === 'string') form.mp_update_types = form.mp_update_types.split(',').map(v => v.trim()).filter(Boolean);
  if (typeof form.plugin_uninstall_ids === 'string') form.plugin_uninstall_ids = form.plugin_uninstall_ids.split(',').map(v => v.trim()).filter(Boolean);
}, { immediate: true, deep: true });

function saveConfig() {
  emit('save', { ...form });
}

function selectMain(key) {
  activeMain.value = key;
  if (!activeSub[key]) activeSub[key] = subTabs[key]?.[0]?.key || 'basic';
}

return (_ctx, _cache) => {
  const _component_VSpacer = _resolveComponent("VSpacer");
  const _component_VBtn = _resolveComponent("VBtn");
  const _component_VToolbar = _resolveComponent("VToolbar");
  const _component_VDivider = _resolveComponent("VDivider");
  const _component_VCardText = _resolveComponent("VCardText");
  const _component_VIcon = _resolveComponent("VIcon");
  const _component_VAvatar = _resolveComponent("VAvatar");
  const _component_VCardTitle = _resolveComponent("VCardTitle");
  const _component_VCardSubtitle = _resolveComponent("VCardSubtitle");
  const _component_VCardItem = _resolveComponent("VCardItem");
  const _component_VTab = _resolveComponent("VTab");
  const _component_VTabs = _resolveComponent("VTabs");
  const _component_VSwitch = _resolveComponent("VSwitch");
  const _component_VCol = _resolveComponent("VCol");
  const _component_VSelect = _resolveComponent("VSelect");
  const _component_VRow = _resolveComponent("VRow");
  const _component_VWindowItem = _resolveComponent("VWindowItem");
  const _component_VTextField = _resolveComponent("VTextField");
  const _component_VCombobox = _resolveComponent("VCombobox");
  const _component_VWindow = _resolveComponent("VWindow");
  const _component_VCard = _resolveComponent("VCard");

  return (_openBlock(), _createElementBlock("div", _hoisted_1, [
    _createVNode(_component_VToolbar, {
      density: "comfortable",
      class: "agentops-toolbar"
    }, {
      default: _withCtx(() => [
        _cache[65] || (_cache[65] = _createElementVNode("div", { class: "text-h6 ms-3" }, "MP 运维助手配置", -1)),
        _createVNode(_component_VSpacer),
        _createVNode(_component_VBtn, {
          color: "primary",
          variant: "tonal",
          "prepend-icon": "mdi-content-save",
          class: "text-none",
          onClick: saveConfig
        }, {
          default: _withCtx(() => [...(_cache[64] || (_cache[64] = [
            _createTextVNode("保存配置", -1)
          ]))]),
          _: 1
        }),
        _createVNode(_component_VBtn, {
          icon: "mdi-close",
          variant: "text",
          onClick: _cache[0] || (_cache[0] = $event => (emit('close')))
        })
      ]),
      _: 1
    }),
    _createVNode(_component_VDivider),
    _createElementVNode("div", _hoisted_2, [
      _createVNode(_component_VCard, {
        flat: "",
        class: "rounded border mpops-shell"
      }, {
        default: _withCtx(() => [
          _createVNode(_component_VCardText, { class: "pb-0" }, {
            default: _withCtx(() => [
              _createElementVNode("div", _hoisted_3, [
                (_openBlock(), _createElementBlock(_Fragment, null, _renderList(mainTabs, (tab) => {
                  return _createVNode(_component_VBtn, {
                    key: tab.key,
                    color: activeMain.value === tab.key ? tab.color : undefined,
                    variant: activeMain.value === tab.key ? 'tonal' : 'text',
                    class: "text-none",
                    "prepend-icon": tab.icon,
                    onClick: $event => (selectMain(tab.key))
                  }, {
                    default: _withCtx(() => [
                      _createTextVNode(_toDisplayString(tab.title), 1)
                    ]),
                    _: 2
                  }, 1032, ["color", "variant", "prepend-icon", "onClick"])
                }), 64))
              ])
            ]),
            _: 1
          }),
          _createVNode(_component_VDivider, { class: "mt-3" }),
          _createVNode(_component_VCardItem, null, {
            prepend: _withCtx(() => [
              _createVNode(_component_VAvatar, {
                color: currentMain.value.color,
                variant: "tonal",
                size: "40"
              }, {
                default: _withCtx(() => [
                  _createVNode(_component_VIcon, {
                    icon: currentMain.value.icon
                  }, null, 8, ["icon"])
                ]),
                _: 1
              }, 8, ["color"])
            ]),
            default: _withCtx(() => [
              _createVNode(_component_VCardTitle, null, {
                default: _withCtx(() => [
                  _createTextVNode(_toDisplayString(currentMain.value.title), 1)
                ]),
                _: 1
              }),
              _createVNode(_component_VCardSubtitle, null, {
                default: _withCtx(() => [
                  _createTextVNode(_toDisplayString(currentMain.value.desc), 1)
                ]),
                _: 1
              })
            ]),
            _: 1
          }),
          _createVNode(_component_VCardText, null, {
            default: _withCtx(() => [
              _createVNode(_component_VTabs, {
                modelValue: activeSub[activeMain.value],
                "onUpdate:modelValue": _cache[1] || (_cache[1] = $event => ((activeSub[activeMain.value]) = $event)),
                color: currentMain.value.color,
                density: "comfortable",
                "show-arrows": "",
                class: "mpops-subtabs"
              }, {
                default: _withCtx(() => [
                  (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(subTabs[activeMain.value], (tab) => {
                    return (_openBlock(), _createBlock(_component_VTab, {
                      key: tab.key,
                      value: tab.key,
                      class: "text-none"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_VIcon, {
                          icon: tab.icon,
                          size: "small",
                          start: ""
                        }, null, 8, ["icon"]),
                        _createTextVNode(_toDisplayString(tab.title), 1)
                      ]),
                      _: 2
                    }, 1032, ["value"]))
                  }), 128))
                ]),
                _: 1
              }, 8, ["modelValue", "color"]),
              _createVNode(_component_VDivider),
              _createVNode(_component_VWindow, {
                modelValue: activeSub[activeMain.value],
                "onUpdate:modelValue": _cache[63] || (_cache[63] = $event => ((activeSub[activeMain.value]) = $event)),
                touch: false
              }, {
                default: _withCtx(() => [
                  (activeMain.value === 'report')
                    ? (_openBlock(), _createElementBlock(_Fragment, { key: 0 }, [
                        _createVNode(_component_VWindowItem, {
                          value: "basic",
                          class: "pa-3"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VRow, null, {
                              default: _withCtx(() => [
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "6"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VSwitch, {
                                      modelValue: form.enabled,
                                      "onUpdate:modelValue": _cache[2] || (_cache[2] = $event => ((form.enabled) = $event)),
                                      label: "启用插件",
                                      color: "primary",
                                      hint: "关闭后不注册本插件的定时任务，也不会自动发送汇报。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                }),
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "6"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VSwitch, {
                                      modelValue: form.daily_report_enabled,
                                      "onUpdate:modelValue": _cache[3] || (_cache[3] = $event => ((form.daily_report_enabled) = $event)),
                                      label: "启用每日汇报",
                                      color: "primary",
                                      hint: "开启后按下方时间自动发送 MP 运维汇报。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                }),
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "6"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VSelect, {
                                      modelValue: form.daily_report_cron,
                                      "onUpdate:modelValue": _cache[4] || (_cache[4] = $event => ((form.daily_report_cron) = $event)),
                                      items: cronPresets,
                                      label: "每日汇报时间",
                                      variant: "outlined",
                                      density: "comfortable",
                                      hint: "推荐选择每天 22:00；也可以手动输入 Cron。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                }),
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "6"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VSwitch, {
                                      modelValue: form.health_in_report,
                                      "onUpdate:modelValue": _cache[5] || (_cache[5] = $event => ((form.health_in_report) = $event)),
                                      label: "加入健康巡查摘要",
                                      color: "primary",
                                      hint: "在汇报中显示下载器、站点、入库和存储等状态摘要。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                })
                              ]),
                              _: 1
                            })
                          ]),
                          _: 1
                        }),
                        _createVNode(_component_VWindowItem, {
                          value: "columns",
                          class: "pa-3"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VRow, null, {
                              default: _withCtx(() => [
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "6"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VSwitch, {
                                      modelValue: form.subscribe_in_report,
                                      "onUpdate:modelValue": _cache[6] || (_cache[6] = $event => ((form.subscribe_in_report) = $event)),
                                      label: "显示订阅追新",
                                      color: "primary",
                                      hint: "开启后每日汇报会包含今日订阅更新；不需要订阅栏目时关闭。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                }),
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "6"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VSwitch, {
                                      modelValue: form.site_stat_in_report,
                                      "onUpdate:modelValue": _cache[7] || (_cache[7] = $event => ((form.site_stat_in_report) = $event)),
                                      label: "显示站点统计",
                                      color: "primary",
                                      hint: "开启后每日汇报会包含站点状态和增量数据。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                })
                              ]),
                              _: 1
                            })
                          ]),
                          _: 1
                        })
                      ], 64))
                    : _createCommentVNode("", true),
                  (activeMain.value === 'notices')
                    ? (_openBlock(), _createElementBlock(_Fragment, { key: 1 }, [
                        _createVNode(_component_VWindowItem, {
                          value: "subscribe",
                          class: "pa-3"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VRow, null, {
                              default: _withCtx(() => [
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "4"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VSwitch, {
                                      modelValue: form.subscribe_reminder_enabled,
                                      "onUpdate:modelValue": _cache[8] || (_cache[8] = $event => ((form.subscribe_reminder_enabled) = $event)),
                                      label: "启用订阅提醒",
                                      color: "cyan",
                                      hint: "开启后订阅追新数据会参与提醒和汇报。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                }),
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "4"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VSwitch, {
                                      modelValue: form.subscribe_reminder_onlyonce,
                                      "onUpdate:modelValue": _cache[9] || (_cache[9] = $event => ((form.subscribe_reminder_onlyonce) = $event)),
                                      label: "保存后立即运行一次",
                                      color: "cyan",
                                      hint: "只适合手动测试；运行后建议关闭。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                }),
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "4"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VTextField, {
                                      modelValue: form.subscribe_reminder_time,
                                      "onUpdate:modelValue": _cache[10] || (_cache[10] = $event => ((form.subscribe_reminder_time) = $event)),
                                      label: "提醒小时",
                                      variant: "outlined",
                                      density: "comfortable",
                                      hint: "填写 0-23 的小时，例如 9 表示上午 9 点提醒。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                }),
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "6"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VSelect, {
                                      modelValue: form.subscribe_reminder_subtype,
                                      "onUpdate:modelValue": _cache[11] || (_cache[11] = $event => ((form.subscribe_reminder_subtype) = $event)),
                                      items: subscribeSubtypeItems,
                                      label: "提醒媒体类型",
                                      variant: "outlined",
                                      density: "comfortable",
                                      multiple: "",
                                      chips: "",
                                      "closable-chips": "",
                                      hint: "选择需要统计和提醒的订阅类型。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                }),
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "6"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VSelect, {
                                      modelValue: form.subscribe_reminder_msgtype,
                                      "onUpdate:modelValue": _cache[12] || (_cache[12] = $event => ((form.subscribe_reminder_msgtype) = $event)),
                                      items: messageTypeItems,
                                      label: "通知类型",
                                      variant: "outlined",
                                      density: "comfortable",
                                      hint: "不确定时保持“订阅”。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                })
                              ]),
                              _: 1
                            })
                          ]),
                          _: 1
                        }),
                        _createVNode(_component_VWindowItem, {
                          value: "sites",
                          class: "pa-3"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VRow, null, {
                              default: _withCtx(() => [
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "4"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VSwitch, {
                                      modelValue: form.site_stat_enabled,
                                      "onUpdate:modelValue": _cache[13] || (_cache[13] = $event => ((form.site_stat_enabled) = $event)),
                                      label: "启用站点统计",
                                      color: "cyan",
                                      hint: "开启后采集站点状态，用于汇报和通知。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                }),
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "4"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VSwitch, {
                                      modelValue: form.site_stat_onlyonce,
                                      "onUpdate:modelValue": _cache[14] || (_cache[14] = $event => ((form.site_stat_onlyonce) = $event)),
                                      label: "保存后立即刷新一次",
                                      color: "cyan",
                                      hint: "用于手动更新站点数据；运行后建议关闭。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                }),
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "4"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VSelect, {
                                      modelValue: form.site_stat_dashboard_type,
                                      "onUpdate:modelValue": _cache[15] || (_cache[15] = $event => ((form.site_stat_dashboard_type) = $event)),
                                      items: siteStatRangeItems,
                                      label: "统计范围",
                                      variant: "outlined",
                                      density: "comfortable",
                                      hint: "今日数据适合日报；汇总/所有数据适合排查趋势。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                }),
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "6"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VSelect, {
                                      modelValue: form.site_stat_notify_type,
                                      "onUpdate:modelValue": _cache[16] || (_cache[16] = $event => ((form.site_stat_notify_type) = $event)),
                                      items: siteNotifyItems,
                                      label: "通知内容",
                                      variant: "outlined",
                                      density: "comfortable",
                                      hint: "选择站点数据变化时发送哪类通知。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                })
                              ]),
                              _: 1
                            })
                          ]),
                          _: 1
                        })
                      ], 64))
                    : _createCommentVNode("", true),
                  (activeMain.value === 'backup')
                    ? (_openBlock(), _createElementBlock(_Fragment, { key: 2 }, [
                        _createVNode(_component_VWindowItem, {
                          value: "local",
                          class: "pa-3"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VRow, null, {
                              default: _withCtx(() => [
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "4"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VSwitch, {
                                      modelValue: form.backup_enabled,
                                      "onUpdate:modelValue": _cache[17] || (_cache[17] = $event => ((form.backup_enabled) = $event)),
                                      label: "启用自动备份",
                                      color: "success",
                                      hint: "开启后按备份时间自动打包配置和关键数据。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                }),
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "4"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VSwitch, {
                                      modelValue: form.backup_onlyonce,
                                      "onUpdate:modelValue": _cache[18] || (_cache[18] = $event => ((form.backup_onlyonce) = $event)),
                                      label: "保存后立即备份一次",
                                      color: "success",
                                      hint: "用于手动生成一次备份；运行后建议关闭。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                }),
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "4"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VSwitch, {
                                      modelValue: form.backup_notify,
                                      "onUpdate:modelValue": _cache[19] || (_cache[19] = $event => ((form.backup_notify) = $event)),
                                      label: "备份后通知",
                                      color: "success",
                                      hint: "备份成功或失败后发送通知。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                }),
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "4"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VSelect, {
                                      modelValue: form.backup_cron,
                                      "onUpdate:modelValue": _cache[20] || (_cache[20] = $event => ((form.backup_cron) = $event)),
                                      items: cronPresets,
                                      label: "备份时间",
                                      variant: "outlined",
                                      density: "comfortable",
                                      hint: "推荐每周低峰期执行。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                }),
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "4"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VSelect, {
                                      modelValue: form.backup_keep_count,
                                      "onUpdate:modelValue": _cache[21] || (_cache[21] = $event => ((form.backup_keep_count) = $event)),
                                      items: _unref(keepCountPresets),
                                      label: "本地保留数量",
                                      variant: "outlined",
                                      density: "comfortable",
                                      hint: "超过数量后会清理最旧备份。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue", "items"])
                                  ]),
                                  _: 1
                                }),
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "4"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VTextField, {
                                      modelValue: form.backup_path,
                                      "onUpdate:modelValue": _cache[22] || (_cache[22] = $event => ((form.backup_path) = $event)),
                                      label: "备份保存路径",
                                      variant: "outlined",
                                      density: "comfortable",
                                      hint: "默认路径即可；如修改，请填写容器内可写目录。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                })
                              ]),
                              _: 1
                            })
                          ]),
                          _: 1
                        }),
                        _createVNode(_component_VWindowItem, {
                          value: "webdav",
                          class: "pa-3"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VRow, null, {
                              default: _withCtx(() => [
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "4"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VSwitch, {
                                      modelValue: form.backup_webdav_enabled,
                                      "onUpdate:modelValue": _cache[23] || (_cache[23] = $event => ((form.backup_webdav_enabled) = $event)),
                                      label: "启用 WebDAV 备份",
                                      color: "success",
                                      hint: "开启后会把备份同步到 WebDAV。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                }),
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "4"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VSwitch, {
                                      modelValue: form.backup_webdav_notify,
                                      "onUpdate:modelValue": _cache[24] || (_cache[24] = $event => ((form.backup_webdav_notify) = $event)),
                                      label: "WebDAV 结果通知",
                                      color: "success",
                                      hint: "上传成功或失败后发送通知。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                }),
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "4"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VSwitch, {
                                      modelValue: form.backup_webdav_digest_auth,
                                      "onUpdate:modelValue": _cache[25] || (_cache[25] = $event => ((form.backup_webdav_digest_auth) = $event)),
                                      label: "使用 Digest 认证",
                                      color: "success",
                                      hint: "服务端要求 Digest 时开启；普通账号密码认证保持关闭。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                }),
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "4"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VSwitch, {
                                      modelValue: form.backup_webdav_disable_check,
                                      "onUpdate:modelValue": _cache[26] || (_cache[26] = $event => ((form.backup_webdav_disable_check) = $event)),
                                      label: "跳过连通检查",
                                      color: "warning",
                                      hint: "只有服务端检查异常但实际可上传时才开启。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                }),
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "8"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VTextField, {
                                      modelValue: form.backup_webdav_hostname,
                                      "onUpdate:modelValue": _cache[27] || (_cache[27] = $event => ((form.backup_webdav_hostname) = $event)),
                                      label: "WebDAV 地址",
                                      variant: "outlined",
                                      density: "comfortable",
                                      hint: "填写完整地址，例如 https://example.com/dav。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                }),
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "4"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VTextField, {
                                      modelValue: form.backup_webdav_login,
                                      "onUpdate:modelValue": _cache[28] || (_cache[28] = $event => ((form.backup_webdav_login) = $event)),
                                      label: "WebDAV 用户名",
                                      variant: "outlined",
                                      density: "comfortable"
                                    }, null, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                }),
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "4"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VTextField, {
                                      modelValue: form.backup_webdav_password,
                                      "onUpdate:modelValue": _cache[29] || (_cache[29] = $event => ((form.backup_webdav_password) = $event)),
                                      label: "WebDAV 密码",
                                      type: "password",
                                      variant: "outlined",
                                      density: "comfortable"
                                    }, null, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                }),
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "4"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VSelect, {
                                      modelValue: form.backup_webdav_max_count,
                                      "onUpdate:modelValue": _cache[30] || (_cache[30] = $event => ((form.backup_webdav_max_count) = $event)),
                                      items: _unref(keepCountPresets),
                                      label: "远端保留数量",
                                      variant: "outlined",
                                      density: "comfortable",
                                      hint: "超过数量后会清理远端旧备份。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue", "items"])
                                  ]),
                                  _: 1
                                })
                              ]),
                              _: 1
                            })
                          ]),
                          _: 1
                        })
                      ], 64))
                    : _createCommentVNode("", true),
                  (activeMain.value === 'cleanup')
                    ? (_openBlock(), _createBlock(_component_VWindowItem, {
                        key: 3,
                        value: "logs",
                        class: "pa-3"
                      }, {
                        default: _withCtx(() => [
                          _createVNode(_component_VRow, null, {
                            default: _withCtx(() => [
                              _createVNode(_component_VCol, {
                                cols: "12",
                                md: "4"
                              }, {
                                default: _withCtx(() => [
                                  _createVNode(_component_VSwitch, {
                                    modelValue: form.log_clean_enabled,
                                    "onUpdate:modelValue": _cache[31] || (_cache[31] = $event => ((form.log_clean_enabled) = $event)),
                                    label: "启用插件日志定时清理",
                                    color: "warning",
                                    hint: "开启后按设定时间截断插件日志。",
                                    "persistent-hint": ""
                                  }, null, 8, ["modelValue"])
                                ]),
                                _: 1
                              }),
                              _createVNode(_component_VCol, {
                                cols: "12",
                                md: "4"
                              }, {
                                default: _withCtx(() => [
                                  _createVNode(_component_VSwitch, {
                                    modelValue: form.log_clean_onlyonce,
                                    "onUpdate:modelValue": _cache[32] || (_cache[32] = $event => ((form.log_clean_onlyonce) = $event)),
                                    label: "保存后立即清理一次",
                                    color: "warning",
                                    hint: "用于手动清理；运行后建议关闭。",
                                    "persistent-hint": ""
                                  }, null, 8, ["modelValue"])
                                ]),
                                _: 1
                              }),
                              _createVNode(_component_VCol, {
                                cols: "12",
                                md: "4"
                              }, {
                                default: _withCtx(() => [
                                  _createVNode(_component_VSwitch, {
                                    modelValue: form.log_clean_notify,
                                    "onUpdate:modelValue": _cache[33] || (_cache[33] = $event => ((form.log_clean_notify) = $event)),
                                    label: "清理后通知",
                                    color: "warning",
                                    hint: "清理完成后发送处理结果。",
                                    "persistent-hint": ""
                                  }, null, 8, ["modelValue"])
                                ]),
                                _: 1
                              }),
                              _createVNode(_component_VCol, {
                                cols: "12",
                                md: "4"
                              }, {
                                default: _withCtx(() => [
                                  _createVNode(_component_VSelect, {
                                    modelValue: form.log_clean_cron,
                                    "onUpdate:modelValue": _cache[34] || (_cache[34] = $event => ((form.log_clean_cron) = $event)),
                                    items: cronPresets,
                                    label: "日志清理时间",
                                    variant: "outlined",
                                    density: "comfortable",
                                    hint: "推荐每周低峰期执行。",
                                    "persistent-hint": ""
                                  }, null, 8, ["modelValue"])
                                ]),
                                _: 1
                              }),
                              _createVNode(_component_VCol, {
                                cols: "12",
                                md: "4"
                              }, {
                                default: _withCtx(() => [
                                  _createVNode(_component_VSelect, {
                                    modelValue: form.log_clean_rows,
                                    "onUpdate:modelValue": _cache[35] || (_cache[35] = $event => ((form.log_clean_rows) = $event)),
                                    items: _unref(logRowsPresets),
                                    label: "每个日志保留行数",
                                    variant: "outlined",
                                    density: "comfortable",
                                    hint: "保留越少占用越低；排障频繁时可保留 1000 行。",
                                    "persistent-hint": ""
                                  }, null, 8, ["modelValue", "items"])
                                ]),
                                _: 1
                              }),
                              _createVNode(_component_VCol, {
                                cols: "12",
                                md: "4"
                              }, {
                                default: _withCtx(() => [
                                  _createVNode(_component_VTextField, {
                                    modelValue: form.log_clean_selected_ids,
                                    "onUpdate:modelValue": _cache[36] || (_cache[36] = $event => ((form.log_clean_selected_ids) = $event)),
                                    label: "限定插件 ID",
                                    variant: "outlined",
                                    density: "comfortable",
                                    hint: "留空表示全部插件；多个 ID 用英文逗号分隔。",
                                    "persistent-hint": ""
                                  }, null, 8, ["modelValue"])
                                ]),
                                _: 1
                              })
                            ]),
                            _: 1
                          })
                        ]),
                        _: 1
                      }))
                    : _createCommentVNode("", true),
                  (activeMain.value === 'updates')
                    ? (_openBlock(), _createElementBlock(_Fragment, { key: 4 }, [
                        _createVNode(_component_VWindowItem, {
                          value: "mp",
                          class: "pa-3"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VRow, null, {
                              default: _withCtx(() => [
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "4"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VSwitch, {
                                      modelValue: form.mp_update_enabled,
                                      "onUpdate:modelValue": _cache[37] || (_cache[37] = $event => ((form.mp_update_enabled) = $event)),
                                      label: "启用主程序更新检查",
                                      color: "info",
                                      hint: "只检查并通知，不会自动升级。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                }),
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "4"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VSelect, {
                                      modelValue: form.mp_update_cron,
                                      "onUpdate:modelValue": _cache[38] || (_cache[38] = $event => ((form.mp_update_cron) = $event)),
                                      items: cronPresets,
                                      label: "检查时间",
                                      variant: "outlined",
                                      density: "comfortable",
                                      hint: "推荐每天 09:00。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                }),
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "4"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VSwitch, {
                                      modelValue: form.mp_update_notify,
                                      "onUpdate:modelValue": _cache[39] || (_cache[39] = $event => ((form.mp_update_notify) = $event)),
                                      label: "检查后通知",
                                      color: "info",
                                      hint: "有无更新都会按插件逻辑发送结果。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                }),
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "6"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VSelect, {
                                      modelValue: form.mp_update_types,
                                      "onUpdate:modelValue": _cache[40] || (_cache[40] = $event => ((form.mp_update_types) = $event)),
                                      items: _unref(mpUpdateTypes),
                                      label: "检查对象",
                                      variant: "outlined",
                                      density: "comfortable",
                                      multiple: "",
                                      chips: "",
                                      "closable-chips": "",
                                      hint: "一般同时选择后端和前端。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue", "items"])
                                  ]),
                                  _: 1
                                }),
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "6"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VSwitch, {
                                      modelValue: form.mp_update_restart_confirm,
                                      "onUpdate:modelValue": _cache[41] || (_cache[41] = $event => ((form.mp_update_restart_confirm) = $event)),
                                      label: "允许更新后重启",
                                      color: "error",
                                      hint: "开启后更新流程可在需要时重启 MoviePilot；不想自动重启就关闭。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                })
                              ]),
                              _: 1
                            })
                          ]),
                          _: 1
                        }),
                        _createVNode(_component_VWindowItem, {
                          value: "market",
                          class: "pa-3"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VRow, null, {
                              default: _withCtx(() => [
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "4"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VSwitch, {
                                      modelValue: form.market_update_enabled,
                                      "onUpdate:modelValue": _cache[42] || (_cache[42] = $event => ((form.market_update_enabled) = $event)),
                                      label: "启用插件库更新检查",
                                      color: "info",
                                      hint: "定期检查插件库地址是否变化。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                }),
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "4"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VSwitch, {
                                      modelValue: form.market_update_onlyonce,
                                      "onUpdate:modelValue": _cache[43] || (_cache[43] = $event => ((form.market_update_onlyonce) = $event)),
                                      label: "保存后立即检查一次",
                                      color: "info",
                                      hint: "用于手动测试；运行后建议关闭。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                }),
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "4"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VSelect, {
                                      modelValue: form.market_update_interval,
                                      "onUpdate:modelValue": _cache[44] || (_cache[44] = $event => ((form.market_update_interval) = $event)),
                                      items: _unref(intervalPresets),
                                      label: "检查间隔",
                                      variant: "outlined",
                                      density: "comfortable",
                                      hint: "推荐 1 天。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue", "items"])
                                  ]),
                                  _: 1
                                }),
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "4"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VSwitch, {
                                      modelValue: form.market_update_notify,
                                      "onUpdate:modelValue": _cache[45] || (_cache[45] = $event => ((form.market_update_notify) = $event)),
                                      label: "变化时通知",
                                      color: "info",
                                      hint: "发现插件库地址变化时发送通知。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                }),
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "4"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VSwitch, {
                                      modelValue: form.market_update_write_notify,
                                      "onUpdate:modelValue": _cache[46] || (_cache[46] = $event => ((form.market_update_write_notify) = $event)),
                                      label: "写入后通知",
                                      color: "info",
                                      hint: "启用写入时，写入完成后发送通知。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                }),
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "4"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VSelect, {
                                      modelValue: form.market_update_notify_type,
                                      "onUpdate:modelValue": _cache[47] || (_cache[47] = $event => ((form.market_update_notify_type) = $event)),
                                      items: marketNotifyItems,
                                      label: "通知类型",
                                      variant: "outlined",
                                      density: "comfortable",
                                      hint: "不确定时保持插件通知。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                }),
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "4"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VSwitch, {
                                      modelValue: form.market_update_write_settings,
                                      "onUpdate:modelValue": _cache[48] || (_cache[48] = $event => ((form.market_update_write_settings) = $event)),
                                      label: "允许写入当前配置",
                                      color: "error",
                                      hint: "开启后允许把检测到的插件库地址写入当前配置；不确定就关闭。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                }),
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "4"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VSwitch, {
                                      modelValue: form.market_update_write_env,
                                      "onUpdate:modelValue": _cache[49] || (_cache[49] = $event => ((form.market_update_write_env) = $event)),
                                      label: "允许写入 app.env",
                                      color: "error",
                                      hint: "开启后允许写入 app.env；通常保持关闭。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                }),
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "4"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VSwitch, {
                                      modelValue: form.market_update_blacklist_enabled,
                                      "onUpdate:modelValue": _cache[50] || (_cache[50] = $event => ((form.market_update_blacklist_enabled) = $event)),
                                      label: "启用写入黑名单",
                                      color: "info",
                                      hint: "开启后，黑名单中的插件库地址不会被写入。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                }),
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "4"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VSwitch, {
                                      modelValue: form.market_update_auto_get,
                                      "onUpdate:modelValue": _cache[51] || (_cache[51] = $event => ((form.market_update_auto_get) = $event)),
                                      label: "自动获取插件库地址",
                                      color: "info",
                                      hint: "从 Wiki 页面自动解析插件库地址。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                }),
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "4"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VSwitch, {
                                      modelValue: form.market_update_proxy,
                                      "onUpdate:modelValue": _cache[52] || (_cache[52] = $event => ((form.market_update_proxy) = $event)),
                                      label: "使用代理访问 Wiki",
                                      color: "info",
                                      hint: "访问 Wiki 慢或失败时开启。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                }),
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "4"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VTextField, {
                                      modelValue: form.market_update_timeout,
                                      "onUpdate:modelValue": _cache[53] || (_cache[53] = $event => ((form.market_update_timeout) = $event)),
                                      type: "number",
                                      label: "请求超时（秒）",
                                      variant: "outlined",
                                      density: "comfortable",
                                      hint: "网络慢时可调大，例如 10。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                }),
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "6"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VTextField, {
                                      modelValue: form.market_update_wiki_url,
                                      "onUpdate:modelValue": _cache[54] || (_cache[54] = $event => ((form.market_update_wiki_url) = $event)),
                                      label: "插件库 Wiki 地址",
                                      variant: "outlined",
                                      density: "comfortable",
                                      hint: "用于自动获取插件库地址，通常保持默认。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                }),
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "6"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VTextField, {
                                      modelValue: form.market_update_wiki_xpath,
                                      "onUpdate:modelValue": _cache[55] || (_cache[55] = $event => ((form.market_update_wiki_xpath) = $event)),
                                      label: "Wiki XPath",
                                      variant: "outlined",
                                      density: "comfortable",
                                      hint: "用于定位页面中的插件库地址，不懂 XPath 就保持默认。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                }),
                                _createVNode(_component_VCol, { cols: "12" }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VTextField, {
                                      modelValue: form.market_update_blacklist,
                                      "onUpdate:modelValue": _cache[56] || (_cache[56] = $event => ((form.market_update_blacklist) = $event)),
                                      label: "插件库黑名单",
                                      variant: "outlined",
                                      density: "comfortable",
                                      hint: "多个插件 ID 用英文逗号分隔。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                })
                              ]),
                              _: 1
                            })
                          ]),
                          _: 1
                        })
                      ], 64))
                    : _createCommentVNode("", true),
                  (activeMain.value === 'plugin')
                    ? (_openBlock(), _createElementBlock(_Fragment, { key: 5 }, [
                        _createVNode(_component_VWindowItem, {
                          value: "target",
                          class: "pa-3"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VRow, null, {
                              default: _withCtx(() => [
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "6"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VTextField, {
                                      modelValue: form.plugin_uninstall_id,
                                      "onUpdate:modelValue": _cache[57] || (_cache[57] = $event => ((form.plugin_uninstall_id) = $event)),
                                      label: "目标插件 ID",
                                      variant: "outlined",
                                      density: "comfortable",
                                      hint: "填写要检查残留的插件 ID；不要填写 AgentOpsAssistant。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                }),
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "6"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VCombobox, {
                                      modelValue: form.plugin_uninstall_ids,
                                      "onUpdate:modelValue": _cache[58] || (_cache[58] = $event => ((form.plugin_uninstall_ids) = $event)),
                                      label: "批量目标插件 ID",
                                      variant: "outlined",
                                      density: "comfortable",
                                      multiple: "",
                                      chips: "",
                                      "closable-chips": "",
                                      hint: "多个插件一起检查时填写；为空时使用左侧单个 ID。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                })
                              ]),
                              _: 1
                            })
                          ]),
                          _: 1
                        }),
                        _createVNode(_component_VWindowItem, {
                          value: "scope",
                          class: "pa-3"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VRow, null, {
                              default: _withCtx(() => [
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "6"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VSwitch, {
                                      modelValue: form.plugin_uninstall_clear_config,
                                      "onUpdate:modelValue": _cache[59] || (_cache[59] = $event => ((form.plugin_uninstall_clear_config) = $event)),
                                      label: "清理插件配置",
                                      color: "deep-orange",
                                      hint: "清理目标插件保存的配置项。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                }),
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "6"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VSwitch, {
                                      modelValue: form.plugin_uninstall_clear_data,
                                      "onUpdate:modelValue": _cache[60] || (_cache[60] = $event => ((form.plugin_uninstall_clear_data) = $event)),
                                      label: "清理插件数据",
                                      color: "deep-orange",
                                      hint: "删除目标插件保存的运行数据；不确定时先关闭。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                }),
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "6"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VSwitch, {
                                      modelValue: form.plugin_uninstall_delete_source,
                                      "onUpdate:modelValue": _cache[61] || (_cache[61] = $event => ((form.plugin_uninstall_delete_source) = $event)),
                                      label: "清理本地源码残留",
                                      color: "deep-orange",
                                      hint: "删除本地插件仓库中同名源码目录；只在确认源码不再需要时开启。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                }),
                                _createVNode(_component_VCol, {
                                  cols: "12",
                                  md: "6"
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VSwitch, {
                                      modelValue: form.plugin_uninstall_notify,
                                      "onUpdate:modelValue": _cache[62] || (_cache[62] = $event => ((form.plugin_uninstall_notify) = $event)),
                                      label: "清理后通知",
                                      color: "deep-orange",
                                      hint: "处理完成后发送结果通知。",
                                      "persistent-hint": ""
                                    }, null, 8, ["modelValue"])
                                  ]),
                                  _: 1
                                })
                              ]),
                              _: 1
                            })
                          ]),
                          _: 1
                        })
                      ], 64))
                    : _createCommentVNode("", true)
                ]),
                _: 1
              }, 8, ["modelValue"])
            ]),
            _: 1
          })
        ]),
        _: 1
      })
    ])
  ]))
}
}

};
const Config = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-723e4952"]]);

export { Config as default };
