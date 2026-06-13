import { importShared } from './__federation_fn_import-JrT3xvdd.js';
import { _ as _export_sfc, g as getPluginApi, p as postPluginApi } from './_plugin-vue_export-helper-DGWTz_NE.js';

const {resolveComponent:_resolveComponent,createVNode:_createVNode,withCtx:_withCtx,createTextVNode:_createTextVNode,toDisplayString:_toDisplayString,createElementVNode:_createElementVNode,renderList:_renderList,Fragment:_Fragment,openBlock:_openBlock,createElementBlock:_createElementBlock,createBlock:_createBlock,vShow:_vShow,withDirectives:_withDirectives,unref:_unref,normalizeClass:_normalizeClass,createCommentVNode:_createCommentVNode} = await importShared('vue');


const _hoisted_1 = { class: "aoa-config" };
const _hoisted_2 = { class: "d-flex align-center" };
const _hoisted_3 = { class: "aoa-body" };
const _hoisted_4 = { class: "aoa-nav" };
const _hoisted_5 = { class: "aoa-content" };
const _hoisted_6 = { class: "aoa-window" };
const _hoisted_7 = { class: "aoa-pane" };
const _hoisted_8 = { class: "aoa-btn-row" };
const _hoisted_9 = { class: "aoa-pane" };
const _hoisted_10 = { class: "aoa-pane" };
const _hoisted_11 = { class: "aoa-pane" };
const _hoisted_12 = { class: "aoa-btn-row" };
const _hoisted_13 = { class: "aoa-pane" };
const _hoisted_14 = { class: "aoa-btn-row" };
const _hoisted_15 = { class: "aoa-pane" };
const _hoisted_16 = { class: "aoa-pane" };
const _hoisted_17 = { class: "aoa-btn-row" };
const _hoisted_18 = { class: "aoa-pane" };
const _hoisted_19 = { class: "aoa-btn-row" };
const _hoisted_20 = { class: "aoa-pane" };
const _hoisted_21 = { class: "aoa-btn-row" };
const _hoisted_22 = { class: "aoa-pane" };
const _hoisted_23 = { class: "aoa-btn-row" };

const {reactive,ref,computed,watch,onMounted} = await importShared('vue');


const _sfc_main = {
  __name: 'Config',
  props: {
  api: { type: [Object, Function], default: null },
  initialConfig: { type: Object, default: () => ({}) },
},
  emits: ['save', 'close', 'switch'],
  setup(__props, { emit: __emit }) {

const props = __props;
const emit = __emit;

const form = reactive({});
const activeMain = ref('report');
const activeSub = ref('basic');

// 手动触发动作状态
const action = reactive({ running: '', message: '', ok: true });
async function runAction(path, label) {
  if (action.running) return
  action.running = path;
  action.message = '';
  try {
    const res = await postPluginApi(props.api, path);
    const ok = !res || res.code === 0 || res.code === undefined;
    action.ok = ok;
    action.message = (res && res.msg) || `${label}已${ok ? '完成' : '失败'}`;
  } catch (err) {
    action.ok = false;
    action.message = err?.message || `${label}失败`;
  } finally {
    action.running = '';
  }
}

// 已安装插件（残留清理 / 日志限定 共用）
const installedPlugins = ref([]);
const installedLoading = ref(false);
async function loadInstalledPlugins() {
  installedLoading.value = true;
  try {
    const res = await getPluginApi(props.api, 'installed_plugins');
    installedPlugins.value = Array.isArray(res) ? res : (res?.data || []);
  } catch {
    installedPlugins.value = [];
  } finally {
    installedLoading.value = false;
  }
}

const defaults = {
  enabled: false,
  daily_report_enabled: true,
  daily_report_cron: '0 22 * * *',
  daily_report_greeting: '少爷',
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
  log_clean_selected_ids: [],
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
  { key: 'report', title: '每日汇报', icon: 'mdi-newspaper-variant-outline', desc: '设置每日汇报、订阅提醒、站点统计与健康巡查。' },
  { key: 'backup', title: '自动备份', icon: 'mdi-archive-arrow-up-outline', desc: '设置本地备份、保留数量和 WebDAV 远端备份。' },
  { key: 'cleanup', title: '日志清理', icon: 'mdi-file-document-remove-outline', desc: '设置插件日志保留行数、清理时间和结果通知。' },
  { key: 'updates', title: '更新检查', icon: 'mdi-update', desc: '设置 MoviePilot 和插件库更新检查，不在这里直接升级。' },
  { key: 'plugin', title: '插件残留清理', icon: 'mdi-puzzle-remove-outline', desc: '清理已卸载插件留下的配置、数据、日志或本地源码残留。' },
];

const subTabs = {
  report: [
    { key: 'basic', title: '基础设置', icon: 'mdi-tune-variant' },
    { key: 'subscribe', title: '订阅提醒', icon: 'mdi-bell-ring-outline' },
    { key: 'sites', title: '站点数据统计', icon: 'mdi-chart-line' },
    { key: 'health', title: '健康巡查', icon: 'mdi-heart-pulse' },
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
    { key: 'clean', title: '残留清理', icon: 'mdi-broom' },
  ],
};

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
const currentSubs = computed(() => subTabs[activeMain.value] || []);

watch(() => props.initialConfig, value => {
  Object.keys(form).forEach(key => delete form[key]);
  Object.assign(form, defaults, value || {});
  const toArr = v => typeof v === 'string' ? v.split(',').map(s => s.trim()).filter(Boolean) : (Array.isArray(v) ? v : []);
  form.subscribe_reminder_subtype = toArr(form.subscribe_reminder_subtype);
  form.mp_update_types = toArr(form.mp_update_types);
  form.plugin_uninstall_ids = toArr(form.plugin_uninstall_ids);
  form.log_clean_selected_ids = toArr(form.log_clean_selected_ids);
}, { immediate: true, deep: true });

function saveConfig() {
  emit('save', { ...form });
}

function selectMain(key) {
  if (activeMain.value === key) return
  activeMain.value = key;
  activeSub.value = subTabs[key]?.[0]?.key || '';
}

onMounted(loadInstalledPlugins);

return (_ctx, _cache) => {
  const _component_VIcon = _resolveComponent("VIcon");
  const _component_VAvatar = _resolveComponent("VAvatar");
  const _component_VCardTitle = _resolveComponent("VCardTitle");
  const _component_VCardSubtitle = _resolveComponent("VCardSubtitle");
  const _component_VSwitch = _resolveComponent("VSwitch");
  const _component_VCardItem = _resolveComponent("VCardItem");
  const _component_VDivider = _resolveComponent("VDivider");
  const _component_VListItemTitle = _resolveComponent("VListItemTitle");
  const _component_VListItem = _resolveComponent("VListItem");
  const _component_VList = _resolveComponent("VList");
  const _component_VTab = _resolveComponent("VTab");
  const _component_VTabs = _resolveComponent("VTabs");
  const _component_VCol = _resolveComponent("VCol");
  const _component_VCronField = _resolveComponent("VCronField");
  const _component_VRow = _resolveComponent("VRow");
  const _component_VTextField = _resolveComponent("VTextField");
  const _component_VBtn = _resolveComponent("VBtn");
  const _component_VForm = _resolveComponent("VForm");
  const _component_VSelect = _resolveComponent("VSelect");
  const _component_VTextarea = _resolveComponent("VTextarea");
  const _component_VExpansionPanelText = _resolveComponent("VExpansionPanelText");
  const _component_VExpansionPanel = _resolveComponent("VExpansionPanel");
  const _component_VExpansionPanels = _resolveComponent("VExpansionPanels");
  const _component_VFadeTransition = _resolveComponent("VFadeTransition");
  const _component_VSpacer = _resolveComponent("VSpacer");
  const _component_VCardActions = _resolveComponent("VCardActions");
  const _component_VCard = _resolveComponent("VCard");

  return (_openBlock(), _createElementBlock("div", _hoisted_1, [
    _createVNode(_component_VCard, {
      flat: "",
      class: "aoa-card"
    }, {
      default: _withCtx(() => [
        _createVNode(_component_VCardItem, { class: "aoa-header" }, {
          prepend: _withCtx(() => [
            _createVNode(_component_VAvatar, {
              color: "primary",
              variant: "tonal",
              size: "44",
              rounded: "lg"
            }, {
              default: _withCtx(() => [
                _createVNode(_component_VIcon, {
                  icon: "mdi-shield-sync-outline",
                  size: "24"
                })
              ]),
              _: 1
            })
          ]),
          append: _withCtx(() => [
            _createElementVNode("div", _hoisted_2, [
              _createVNode(_component_VSwitch, {
                modelValue: form.enabled,
                "onUpdate:modelValue": _cache[0] || (_cache[0] = $event => ((form.enabled) = $event)),
                color: "primary",
                "hide-details": "",
                inset: "",
                label: form.enabled ? '已启用' : '已停用'
              }, null, 8, ["modelValue", "label"])
            ])
          ]),
          default: _withCtx(() => [
            _createVNode(_component_VCardTitle, { class: "text-h6" }, {
              default: _withCtx(() => [...(_cache[71] || (_cache[71] = [
                _createTextVNode("MP 运维助手", -1)
              ]))]),
              _: 1
            }),
            _createVNode(_component_VCardSubtitle, { class: "text-caption" }, {
              default: _withCtx(() => [
                _createTextVNode(_toDisplayString(currentMain.value.desc), 1)
              ]),
              _: 1
            })
          ]),
          _: 1
        }),
        _createVNode(_component_VDivider),
        _createElementVNode("div", _hoisted_3, [
          _createElementVNode("nav", _hoisted_4, [
            _createVNode(_component_VList, {
              density: "comfortable",
              nav: "",
              class: "py-2"
            }, {
              default: _withCtx(() => [
                (_openBlock(), _createElementBlock(_Fragment, null, _renderList(mainTabs, (item) => {
                  return _createVNode(_component_VListItem, {
                    key: item.key,
                    active: activeMain.value === item.key,
                    color: "primary",
                    rounded: "lg",
                    class: "aoa-nav-item",
                    onClick: $event => (selectMain(item.key))
                  }, {
                    prepend: _withCtx(() => [
                      _createVNode(_component_VIcon, {
                        icon: item.icon
                      }, null, 8, ["icon"])
                    ]),
                    default: _withCtx(() => [
                      _createVNode(_component_VListItemTitle, null, {
                        default: _withCtx(() => [
                          _createTextVNode(_toDisplayString(item.title), 1)
                        ]),
                        _: 2
                      }, 1024)
                    ]),
                    _: 2
                  }, 1032, ["active", "onClick"])
                }), 64))
              ]),
              _: 1
            })
          ]),
          _createElementVNode("section", _hoisted_5, [
            _createVNode(_component_VTabs, {
              modelValue: activeSub.value,
              "onUpdate:modelValue": _cache[1] || (_cache[1] = $event => ((activeSub).value = $event)),
              color: "primary",
              density: "comfortable",
              "show-arrows": "",
              class: "aoa-subtabs"
            }, {
              default: _withCtx(() => [
                (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(currentSubs.value, (sub) => {
                  return (_openBlock(), _createBlock(_component_VTab, {
                    key: sub.key,
                    value: sub.key
                  }, {
                    default: _withCtx(() => [
                      _createVNode(_component_VIcon, {
                        icon: sub.icon,
                        size: "18",
                        class: "mr-1"
                      }, null, 8, ["icon"]),
                      _createTextVNode(_toDisplayString(sub.title), 1)
                    ]),
                    _: 2
                  }, 1032, ["value"]))
                }), 128))
              ]),
              _: 1
            }, 8, ["modelValue"]),
            _createVNode(_component_VDivider),
            _createElementVNode("div", _hoisted_6, [
              _withDirectives(_createElementVNode("div", _hoisted_7, [
                _createVNode(_component_VForm, null, {
                  default: _withCtx(() => [
                    _cache[75] || (_cache[75] = _createElementVNode("div", { class: "aoa-section-title" }, "汇报开关", -1)),
                    _createVNode(_component_VRow, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "6"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSwitch, {
                              modelValue: form.daily_report_enabled,
                              "onUpdate:modelValue": _cache[2] || (_cache[2] = $event => ((form.daily_report_enabled) = $event)),
                              color: "primary",
                              inset: "",
                              "hide-details": "",
                              label: "启用定时每日汇报"
                            }, null, 8, ["modelValue"]),
                            _cache[72] || (_cache[72] = _createElementVNode("div", { class: "aoa-hint" }, "关闭后将不再按计划自动发送汇报，仍可在下方手动触发。", -1))
                          ]),
                          _: 1
                        }),
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "6"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VCronField, {
                              modelValue: form.daily_report_cron,
                              "onUpdate:modelValue": _cache[3] || (_cache[3] = $event => ((form.daily_report_cron) = $event)),
                              label: "汇报时间 (Cron)",
                              disabled: !form.daily_report_enabled
                            }, null, 8, ["modelValue", "disabled"])
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_VRow, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "6"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VTextField, {
                              modelValue: form.daily_report_greeting,
                              "onUpdate:modelValue": _cache[4] || (_cache[4] = $event => ((form.daily_report_greeting) = $event)),
                              label: "汇报称呼",
                              placeholder: "少爷",
                              "prepend-inner-icon": "mdi-account-heart-outline",
                              "persistent-hint": "",
                              hint: "汇报开头与提醒中对你的称呼，留空默认“少爷”。",
                              clearable: ""
                            }, null, 8, ["modelValue"])
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_VDivider, { class: "my-4" }),
                    _cache[76] || (_cache[76] = _createElementVNode("div", { class: "aoa-section-title" }, "手动触发", -1)),
                    _createElementVNode("div", _hoisted_8, [
                      _createVNode(_component_VBtn, {
                        color: "primary",
                        variant: "tonal",
                        "prepend-icon": "mdi-send-outline",
                        loading: action.running === 'run_daily_report',
                        onClick: _cache[5] || (_cache[5] = $event => (runAction('run_daily_report', '发送每日汇报')))
                      }, {
                        default: _withCtx(() => [...(_cache[73] || (_cache[73] = [
                          _createTextVNode(" 立即发送 ", -1)
                        ]))]),
                        _: 1
                      }, 8, ["loading"]),
                      _createVNode(_component_VBtn, {
                        color: "primary",
                        variant: "outlined",
                        "prepend-icon": "mdi-eye-outline",
                        loading: action.running === 'preview_daily_report',
                        onClick: _cache[6] || (_cache[6] = $event => (runAction('preview_daily_report', '预览每日汇报')))
                      }, {
                        default: _withCtx(() => [...(_cache[74] || (_cache[74] = [
                          _createTextVNode(" 预览（不发送） ", -1)
                        ]))]),
                        _: 1
                      }, 8, ["loading"])
                    ])
                  ]),
                  _: 1
                })
              ], 512), [
                [_vShow, activeSub.value === 'basic']
              ]),
              _withDirectives(_createElementVNode("div", _hoisted_9, [
                _createVNode(_component_VForm, null, {
                  default: _withCtx(() => [
                    _cache[79] || (_cache[79] = _createElementVNode("div", { class: "aoa-section-title" }, "订阅提醒", -1)),
                    _createVNode(_component_VRow, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "6"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSwitch, {
                              modelValue: form.subscribe_in_report,
                              "onUpdate:modelValue": _cache[7] || (_cache[7] = $event => ((form.subscribe_in_report) = $event)),
                              color: "primary",
                              inset: "",
                              "hide-details": "",
                              label: "在每日汇报中包含订阅追新"
                            }, null, 8, ["modelValue"]),
                            _cache[77] || (_cache[77] = _createElementVNode("div", { class: "aoa-hint" }, "汇报正文加入今日订阅追新清单。", -1))
                          ]),
                          _: 1
                        }),
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "6"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSwitch, {
                              modelValue: form.subscribe_reminder_enabled,
                              "onUpdate:modelValue": _cache[8] || (_cache[8] = $event => ((form.subscribe_reminder_enabled) = $event)),
                              color: "primary",
                              inset: "",
                              "hide-details": "",
                              label: "启用独立订阅提醒推送"
                            }, null, 8, ["modelValue"]),
                            _cache[78] || (_cache[78] = _createElementVNode("div", { class: "aoa-hint" }, "在指定时间单独推送订阅追新提醒。", -1))
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_VRow, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "4"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VTextField, {
                              modelValue: form.subscribe_reminder_time,
                              "onUpdate:modelValue": _cache[9] || (_cache[9] = $event => ((form.subscribe_reminder_time) = $event)),
                              label: "提醒时间（小时 0-23）",
                              type: "number",
                              min: "0",
                              max: "23",
                              disabled: !form.subscribe_reminder_enabled
                            }, null, 8, ["modelValue", "disabled"])
                          ]),
                          _: 1
                        }),
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "4"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSelect, {
                              modelValue: form.subscribe_reminder_subtype,
                              "onUpdate:modelValue": _cache[10] || (_cache[10] = $event => ((form.subscribe_reminder_subtype) = $event)),
                              items: subscribeSubtypeItems,
                              label: "提醒类型",
                              multiple: "",
                              chips: "",
                              "closable-chips": "",
                              disabled: !form.subscribe_reminder_enabled
                            }, null, 8, ["modelValue", "disabled"])
                          ]),
                          _: 1
                        }),
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "4"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSelect, {
                              modelValue: form.subscribe_reminder_msgtype,
                              "onUpdate:modelValue": _cache[11] || (_cache[11] = $event => ((form.subscribe_reminder_msgtype) = $event)),
                              items: messageTypeItems,
                              label: "消息类型",
                              disabled: !form.subscribe_reminder_enabled
                            }, null, 8, ["modelValue", "disabled"])
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_VRow, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_VCol, { cols: "12" }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSwitch, {
                              modelValue: form.subscribe_reminder_onlyonce,
                              "onUpdate:modelValue": _cache[12] || (_cache[12] = $event => ((form.subscribe_reminder_onlyonce) = $event)),
                              color: "warning",
                              inset: "",
                              "hide-details": "",
                              label: "保存后立即运行一次订阅提醒",
                              disabled: !form.subscribe_reminder_enabled
                            }, null, 8, ["modelValue", "disabled"])
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                })
              ], 512), [
                [_vShow, activeSub.value === 'subscribe']
              ]),
              _withDirectives(_createElementVNode("div", _hoisted_10, [
                _createVNode(_component_VForm, null, {
                  default: _withCtx(() => [
                    _cache[82] || (_cache[82] = _createElementVNode("div", { class: "aoa-section-title" }, "站点数据统计", -1)),
                    _createVNode(_component_VRow, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "6"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSwitch, {
                              modelValue: form.site_stat_in_report,
                              "onUpdate:modelValue": _cache[13] || (_cache[13] = $event => ((form.site_stat_in_report) = $event)),
                              color: "primary",
                              inset: "",
                              "hide-details": "",
                              label: "在每日汇报中包含站点增量"
                            }, null, 8, ["modelValue"]),
                            _cache[80] || (_cache[80] = _createElementVNode("div", { class: "aoa-hint" }, "汇报正文加入站点上传/做种等增量数据。", -1))
                          ]),
                          _: 1
                        }),
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "6"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSwitch, {
                              modelValue: form.site_stat_enabled,
                              "onUpdate:modelValue": _cache[14] || (_cache[14] = $event => ((form.site_stat_enabled) = $event)),
                              color: "primary",
                              inset: "",
                              "hide-details": "",
                              label: "启用站点数据统计采集"
                            }, null, 8, ["modelValue"]),
                            _cache[81] || (_cache[81] = _createElementVNode("div", { class: "aoa-hint" }, "关闭后不再统计站点数据。", -1))
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_VRow, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "6"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSelect, {
                              modelValue: form.site_stat_dashboard_type,
                              "onUpdate:modelValue": _cache[15] || (_cache[15] = $event => ((form.site_stat_dashboard_type) = $event)),
                              items: siteStatRangeItems,
                              label: "统计数据范围",
                              disabled: !form.site_stat_enabled
                            }, null, 8, ["modelValue", "disabled"])
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
                              label: "通知方式",
                              disabled: !form.site_stat_enabled
                            }, null, 8, ["modelValue", "disabled"])
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_VRow, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_VCol, { cols: "12" }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSwitch, {
                              modelValue: form.site_stat_onlyonce,
                              "onUpdate:modelValue": _cache[17] || (_cache[17] = $event => ((form.site_stat_onlyonce) = $event)),
                              color: "warning",
                              inset: "",
                              "hide-details": "",
                              label: "保存后立即运行一次站点统计",
                              disabled: !form.site_stat_enabled
                            }, null, 8, ["modelValue", "disabled"])
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                })
              ], 512), [
                [_vShow, activeSub.value === 'sites']
              ]),
              _withDirectives(_createElementVNode("div", _hoisted_11, [
                _createVNode(_component_VForm, null, {
                  default: _withCtx(() => [
                    _cache[85] || (_cache[85] = _createElementVNode("div", { class: "aoa-section-title" }, "健康巡查", -1)),
                    _createVNode(_component_VRow, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_VCol, { cols: "12" }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSwitch, {
                              modelValue: form.health_in_report,
                              "onUpdate:modelValue": _cache[18] || (_cache[18] = $event => ((form.health_in_report) = $event)),
                              color: "primary",
                              inset: "",
                              "hide-details": "",
                              label: "在每日汇报中包含健康巡查摘要"
                            }, null, 8, ["modelValue"]),
                            _cache[83] || (_cache[83] = _createElementVNode("div", { class: "aoa-hint" }, "汇报正文加入站点 / 下载器 / 存储 / 入库的健康检查结论。", -1))
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_VDivider, { class: "my-4" }),
                    _cache[86] || (_cache[86] = _createElementVNode("div", { class: "aoa-section-title" }, "手动触发", -1)),
                    _createElementVNode("div", _hoisted_12, [
                      _createVNode(_component_VBtn, {
                        color: "primary",
                        variant: "tonal",
                        "prepend-icon": "mdi-heart-pulse",
                        loading: action.running === 'run_health_check',
                        onClick: _cache[19] || (_cache[19] = $event => (runAction('run_health_check', '健康巡查')))
                      }, {
                        default: _withCtx(() => [...(_cache[84] || (_cache[84] = [
                          _createTextVNode(" 立即巡查 ", -1)
                        ]))]),
                        _: 1
                      }, 8, ["loading"])
                    ])
                  ]),
                  _: 1
                })
              ], 512), [
                [_vShow, activeSub.value === 'health']
              ]),
              _withDirectives(_createElementVNode("div", _hoisted_13, [
                _createVNode(_component_VForm, null, {
                  default: _withCtx(() => [
                    _cache[89] || (_cache[89] = _createElementVNode("div", { class: "aoa-section-title" }, "本地备份", -1)),
                    _createVNode(_component_VRow, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "6"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSwitch, {
                              modelValue: form.backup_enabled,
                              "onUpdate:modelValue": _cache[20] || (_cache[20] = $event => ((form.backup_enabled) = $event)),
                              color: "primary",
                              inset: "",
                              "hide-details": "",
                              label: "启用定时本地备份"
                            }, null, 8, ["modelValue"]),
                            _cache[87] || (_cache[87] = _createElementVNode("div", { class: "aoa-hint" }, "按计划打包配置目录到本地备份路径。", -1))
                          ]),
                          _: 1
                        }),
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "6"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VCronField, {
                              modelValue: form.backup_cron,
                              "onUpdate:modelValue": _cache[21] || (_cache[21] = $event => ((form.backup_cron) = $event)),
                              label: "备份时间 (Cron)",
                              disabled: !form.backup_enabled
                            }, null, 8, ["modelValue", "disabled"])
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_VRow, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "6"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VTextField, {
                              modelValue: form.backup_path,
                              "onUpdate:modelValue": _cache[22] || (_cache[22] = $event => ((form.backup_path) = $event)),
                              label: "本地备份路径",
                              "prepend-inner-icon": "mdi-folder-outline",
                              disabled: !form.backup_enabled
                            }, null, 8, ["modelValue", "disabled"])
                          ]),
                          _: 1
                        }),
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "6"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSelect, {
                              modelValue: form.backup_keep_count,
                              "onUpdate:modelValue": _cache[23] || (_cache[23] = $event => ((form.backup_keep_count) = $event)),
                              items: _unref(keepCountPresets),
                              label: "本地保留份数",
                              disabled: !form.backup_enabled
                            }, null, 8, ["modelValue", "items", "disabled"])
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_VRow, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "6"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSwitch, {
                              modelValue: form.backup_notify,
                              "onUpdate:modelValue": _cache[24] || (_cache[24] = $event => ((form.backup_notify) = $event)),
                              color: "primary",
                              inset: "",
                              "hide-details": "",
                              label: "备份结果通知",
                              disabled: !form.backup_enabled
                            }, null, 8, ["modelValue", "disabled"])
                          ]),
                          _: 1
                        }),
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "6"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSwitch, {
                              modelValue: form.backup_onlyonce,
                              "onUpdate:modelValue": _cache[25] || (_cache[25] = $event => ((form.backup_onlyonce) = $event)),
                              color: "warning",
                              inset: "",
                              "hide-details": "",
                              label: "保存后立即备份一次",
                              disabled: !form.backup_enabled
                            }, null, 8, ["modelValue", "disabled"])
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_VDivider, { class: "my-4" }),
                    _createElementVNode("div", _hoisted_14, [
                      _createVNode(_component_VBtn, {
                        color: "primary",
                        variant: "tonal",
                        "prepend-icon": "mdi-archive-arrow-up-outline",
                        loading: action.running === 'run_backup',
                        onClick: _cache[26] || (_cache[26] = $event => (runAction('run_backup', '立即备份')))
                      }, {
                        default: _withCtx(() => [...(_cache[88] || (_cache[88] = [
                          _createTextVNode(" 立即备份 ", -1)
                        ]))]),
                        _: 1
                      }, 8, ["loading"])
                    ])
                  ]),
                  _: 1
                })
              ], 512), [
                [_vShow, activeSub.value === 'local']
              ]),
              _withDirectives(_createElementVNode("div", _hoisted_15, [
                _createVNode(_component_VForm, null, {
                  default: _withCtx(() => [
                    _cache[91] || (_cache[91] = _createElementVNode("div", { class: "aoa-section-title" }, "WebDAV 远端备份", -1)),
                    _createVNode(_component_VRow, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_VCol, { cols: "12" }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSwitch, {
                              modelValue: form.backup_webdav_enabled,
                              "onUpdate:modelValue": _cache[27] || (_cache[27] = $event => ((form.backup_webdav_enabled) = $event)),
                              color: "primary",
                              inset: "",
                              "hide-details": "",
                              label: "启用 WebDAV 远端备份"
                            }, null, 8, ["modelValue"]),
                            _cache[90] || (_cache[90] = _createElementVNode("div", { class: "aoa-hint" }, "本地备份完成后同步上传到 WebDAV。", -1))
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_VRow, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "6"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VTextField, {
                              modelValue: form.backup_webdav_hostname,
                              "onUpdate:modelValue": _cache[28] || (_cache[28] = $event => ((form.backup_webdav_hostname) = $event)),
                              label: "WebDAV 地址",
                              placeholder: "https://dav.example.com/backup",
                              "prepend-inner-icon": "mdi-web",
                              disabled: !form.backup_webdav_enabled
                            }, null, 8, ["modelValue", "disabled"])
                          ]),
                          _: 1
                        }),
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "3"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VTextField, {
                              modelValue: form.backup_webdav_login,
                              "onUpdate:modelValue": _cache[29] || (_cache[29] = $event => ((form.backup_webdav_login) = $event)),
                              label: "账号",
                              disabled: !form.backup_webdav_enabled
                            }, null, 8, ["modelValue", "disabled"])
                          ]),
                          _: 1
                        }),
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "3"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VTextField, {
                              modelValue: form.backup_webdav_password,
                              "onUpdate:modelValue": _cache[30] || (_cache[30] = $event => ((form.backup_webdav_password) = $event)),
                              label: "密码",
                              type: "password",
                              disabled: !form.backup_webdav_enabled
                            }, null, 8, ["modelValue", "disabled"])
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_VRow, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "6"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSelect, {
                              modelValue: form.backup_webdav_max_count,
                              "onUpdate:modelValue": _cache[31] || (_cache[31] = $event => ((form.backup_webdav_max_count) = $event)),
                              items: _unref(keepCountPresets),
                              label: "远端保留份数",
                              disabled: !form.backup_webdav_enabled
                            }, null, 8, ["modelValue", "items", "disabled"])
                          ]),
                          _: 1
                        }),
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "6"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSwitch, {
                              modelValue: form.backup_webdav_notify,
                              "onUpdate:modelValue": _cache[32] || (_cache[32] = $event => ((form.backup_webdav_notify) = $event)),
                              color: "primary",
                              inset: "",
                              "hide-details": "",
                              label: "远端备份结果通知",
                              disabled: !form.backup_webdav_enabled
                            }, null, 8, ["modelValue", "disabled"])
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_VRow, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "4"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSwitch, {
                              modelValue: form.backup_webdav_digest_auth,
                              "onUpdate:modelValue": _cache[33] || (_cache[33] = $event => ((form.backup_webdav_digest_auth) = $event)),
                              color: "primary",
                              inset: "",
                              "hide-details": "",
                              label: "使用 Digest 认证",
                              disabled: !form.backup_webdav_enabled
                            }, null, 8, ["modelValue", "disabled"])
                          ]),
                          _: 1
                        }),
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "8"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSwitch, {
                              modelValue: form.backup_webdav_disable_check,
                              "onUpdate:modelValue": _cache[34] || (_cache[34] = $event => ((form.backup_webdav_disable_check) = $event)),
                              color: "warning",
                              inset: "",
                              "hide-details": "",
                              label: "跳过证书校验（自签名时启用）",
                              disabled: !form.backup_webdav_enabled
                            }, null, 8, ["modelValue", "disabled"])
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                })
              ], 512), [
                [_vShow, activeSub.value === 'webdav']
              ]),
              _withDirectives(_createElementVNode("div", _hoisted_16, [
                _createVNode(_component_VForm, null, {
                  default: _withCtx(() => [
                    _cache[96] || (_cache[96] = _createElementVNode("div", { class: "aoa-section-title" }, "插件日志清理", -1)),
                    _createVNode(_component_VRow, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "6"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSwitch, {
                              modelValue: form.log_clean_enabled,
                              "onUpdate:modelValue": _cache[35] || (_cache[35] = $event => ((form.log_clean_enabled) = $event)),
                              color: "primary",
                              inset: "",
                              "hide-details": "",
                              label: "启用定时日志清理"
                            }, null, 8, ["modelValue"]),
                            _cache[92] || (_cache[92] = _createElementVNode("div", { class: "aoa-hint" }, "按计划裁剪插件日志文件，仅保留指定行数。", -1))
                          ]),
                          _: 1
                        }),
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "6"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VCronField, {
                              modelValue: form.log_clean_cron,
                              "onUpdate:modelValue": _cache[36] || (_cache[36] = $event => ((form.log_clean_cron) = $event)),
                              label: "清理时间 (Cron)",
                              disabled: !form.log_clean_enabled
                            }, null, 8, ["modelValue", "disabled"])
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_VRow, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "6"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSelect, {
                              modelValue: form.log_clean_rows,
                              "onUpdate:modelValue": _cache[37] || (_cache[37] = $event => ((form.log_clean_rows) = $event)),
                              items: _unref(logRowsPresets),
                              label: "保留行数",
                              disabled: !form.log_clean_enabled
                            }, null, 8, ["modelValue", "items", "disabled"])
                          ]),
                          _: 1
                        }),
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "6"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSelect, {
                              modelValue: form.log_clean_selected_ids,
                              "onUpdate:modelValue": _cache[38] || (_cache[38] = $event => ((form.log_clean_selected_ids) = $event)),
                              items: installedPlugins.value,
                              loading: installedLoading.value,
                              label: "限定插件（留空＝全部插件）",
                              multiple: "",
                              chips: "",
                              "closable-chips": "",
                              clearable: "",
                              "prepend-inner-icon": "mdi-puzzle-outline",
                              disabled: !form.log_clean_enabled
                            }, null, 8, ["modelValue", "items", "loading", "disabled"]),
                            _cache[93] || (_cache[93] = _createElementVNode("div", { class: "aoa-hint" }, "从已安装插件中选择；不选则清理全部插件日志。", -1))
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_VRow, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "6"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSwitch, {
                              modelValue: form.log_clean_notify,
                              "onUpdate:modelValue": _cache[39] || (_cache[39] = $event => ((form.log_clean_notify) = $event)),
                              color: "primary",
                              inset: "",
                              "hide-details": "",
                              label: "清理结果通知",
                              disabled: !form.log_clean_enabled
                            }, null, 8, ["modelValue", "disabled"])
                          ]),
                          _: 1
                        }),
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "6"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSwitch, {
                              modelValue: form.log_clean_onlyonce,
                              "onUpdate:modelValue": _cache[40] || (_cache[40] = $event => ((form.log_clean_onlyonce) = $event)),
                              color: "warning",
                              inset: "",
                              "hide-details": "",
                              label: "保存后立即清理一次",
                              disabled: !form.log_clean_enabled
                            }, null, 8, ["modelValue", "disabled"])
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_VDivider, { class: "my-4" }),
                    _cache[97] || (_cache[97] = _createElementVNode("div", { class: "aoa-section-title" }, "手动触发", -1)),
                    _createElementVNode("div", _hoisted_17, [
                      _createVNode(_component_VBtn, {
                        color: "primary",
                        variant: "outlined",
                        "prepend-icon": "mdi-eye-outline",
                        loading: action.running === 'preview_log_clean',
                        onClick: _cache[41] || (_cache[41] = $event => (runAction('preview_log_clean', '日志清理预览')))
                      }, {
                        default: _withCtx(() => [...(_cache[94] || (_cache[94] = [
                          _createTextVNode(" 预览清理范围 ", -1)
                        ]))]),
                        _: 1
                      }, 8, ["loading"]),
                      _createVNode(_component_VBtn, {
                        color: "primary",
                        variant: "tonal",
                        "prepend-icon": "mdi-broom",
                        loading: action.running === 'run_log_clean',
                        onClick: _cache[42] || (_cache[42] = $event => (runAction('run_log_clean', '日志清理')))
                      }, {
                        default: _withCtx(() => [...(_cache[95] || (_cache[95] = [
                          _createTextVNode(" 立即清理 ", -1)
                        ]))]),
                        _: 1
                      }, 8, ["loading"])
                    ])
                  ]),
                  _: 1
                })
              ], 512), [
                [_vShow, activeSub.value === 'logs']
              ]),
              _withDirectives(_createElementVNode("div", _hoisted_18, [
                _createVNode(_component_VForm, null, {
                  default: _withCtx(() => [
                    _cache[100] || (_cache[100] = _createElementVNode("div", { class: "aoa-section-title" }, "MoviePilot 更新检查", -1)),
                    _cache[101] || (_cache[101] = _createElementVNode("div", { class: "aoa-hint mb-2" }, "仅检查并通知是否有新版本，不会在这里直接升级。", -1)),
                    _createVNode(_component_VRow, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "6"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSwitch, {
                              modelValue: form.mp_update_enabled,
                              "onUpdate:modelValue": _cache[43] || (_cache[43] = $event => ((form.mp_update_enabled) = $event)),
                              color: "primary",
                              inset: "",
                              "hide-details": "",
                              label: "启用定时更新检查"
                            }, null, 8, ["modelValue"])
                          ]),
                          _: 1
                        }),
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "6"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VCronField, {
                              modelValue: form.mp_update_cron,
                              "onUpdate:modelValue": _cache[44] || (_cache[44] = $event => ((form.mp_update_cron) = $event)),
                              label: "检查时间 (Cron)",
                              disabled: !form.mp_update_enabled
                            }, null, 8, ["modelValue", "disabled"])
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_VRow, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "6"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSelect, {
                              modelValue: form.mp_update_types,
                              "onUpdate:modelValue": _cache[45] || (_cache[45] = $event => ((form.mp_update_types) = $event)),
                              items: _unref(mpUpdateTypes),
                              label: "检查范围",
                              multiple: "",
                              chips: "",
                              "closable-chips": "",
                              disabled: !form.mp_update_enabled
                            }, null, 8, ["modelValue", "items", "disabled"])
                          ]),
                          _: 1
                        }),
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "6"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSwitch, {
                              modelValue: form.mp_update_notify,
                              "onUpdate:modelValue": _cache[46] || (_cache[46] = $event => ((form.mp_update_notify) = $event)),
                              color: "primary",
                              inset: "",
                              "hide-details": "",
                              label: "发现新版本时通知",
                              disabled: !form.mp_update_enabled
                            }, null, 8, ["modelValue", "disabled"])
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_VRow, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_VCol, { cols: "12" }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSwitch, {
                              modelValue: form.mp_update_restart_confirm,
                              "onUpdate:modelValue": _cache[47] || (_cache[47] = $event => ((form.mp_update_restart_confirm) = $event)),
                              color: "warning",
                              inset: "",
                              "hide-details": "",
                              label: "允许自动重启以应用更新（高风险，谨慎开启）",
                              disabled: !form.mp_update_enabled
                            }, null, 8, ["modelValue", "disabled"]),
                            _cache[98] || (_cache[98] = _createElementVNode("div", { class: "aoa-hint" }, "默认仅提醒；开启后将在更新后尝试重启 MoviePilot。", -1))
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_VDivider, { class: "my-4" }),
                    _createElementVNode("div", _hoisted_19, [
                      _createVNode(_component_VBtn, {
                        color: "primary",
                        variant: "outlined",
                        "prepend-icon": "mdi-eye-outline",
                        loading: action.running === 'preview_updates',
                        onClick: _cache[48] || (_cache[48] = $event => (runAction('preview_updates', '更新状态预览')))
                      }, {
                        default: _withCtx(() => [...(_cache[99] || (_cache[99] = [
                          _createTextVNode(" 检查更新 ", -1)
                        ]))]),
                        _: 1
                      }, 8, ["loading"])
                    ])
                  ]),
                  _: 1
                })
              ], 512), [
                [_vShow, activeSub.value === 'mp']
              ]),
              _withDirectives(_createElementVNode("div", _hoisted_20, [
                _createVNode(_component_VForm, null, {
                  default: _withCtx(() => [
                    _cache[105] || (_cache[105] = _createElementVNode("div", { class: "aoa-section-title" }, "插件库更新检查", -1)),
                    _createVNode(_component_VRow, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "6"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSwitch, {
                              modelValue: form.market_update_enabled,
                              "onUpdate:modelValue": _cache[49] || (_cache[49] = $event => ((form.market_update_enabled) = $event)),
                              color: "primary",
                              inset: "",
                              "hide-details": "",
                              label: "启用插件库更新检查"
                            }, null, 8, ["modelValue"]),
                            _cache[102] || (_cache[102] = _createElementVNode("div", { class: "aoa-hint" }, "按间隔检查已安装插件是否有新版本。", -1))
                          ]),
                          _: 1
                        }),
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "6"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSelect, {
                              modelValue: form.market_update_interval,
                              "onUpdate:modelValue": _cache[50] || (_cache[50] = $event => ((form.market_update_interval) = $event)),
                              items: _unref(intervalPresets),
                              label: "检查间隔",
                              disabled: !form.market_update_enabled
                            }, null, 8, ["modelValue", "items", "disabled"])
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_VRow, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "6"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSwitch, {
                              modelValue: form.market_update_notify,
                              "onUpdate:modelValue": _cache[51] || (_cache[51] = $event => ((form.market_update_notify) = $event)),
                              color: "primary",
                              inset: "",
                              "hide-details": "",
                              label: "发现更新时通知",
                              disabled: !form.market_update_enabled
                            }, null, 8, ["modelValue", "disabled"])
                          ]),
                          _: 1
                        }),
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "6"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSelect, {
                              modelValue: form.market_update_notify_type,
                              "onUpdate:modelValue": _cache[52] || (_cache[52] = $event => ((form.market_update_notify_type) = $event)),
                              items: marketNotifyItems,
                              label: "通知消息类型",
                              disabled: !form.market_update_enabled
                            }, null, 8, ["modelValue", "disabled"])
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_VRow, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "6"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSwitch, {
                              modelValue: form.market_update_proxy,
                              "onUpdate:modelValue": _cache[53] || (_cache[53] = $event => ((form.market_update_proxy) = $event)),
                              color: "primary",
                              inset: "",
                              "hide-details": "",
                              label: "使用代理访问插件库",
                              disabled: !form.market_update_enabled
                            }, null, 8, ["modelValue", "disabled"])
                          ]),
                          _: 1
                        }),
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "6"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSwitch, {
                              modelValue: form.market_update_auto_get,
                              "onUpdate:modelValue": _cache[54] || (_cache[54] = $event => ((form.market_update_auto_get) = $event)),
                              color: "primary",
                              inset: "",
                              "hide-details": "",
                              label: "自动抓取 Wiki 更新说明",
                              disabled: !form.market_update_enabled
                            }, null, 8, ["modelValue", "disabled"])
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_VExpansionPanels, {
                      class: "mt-2",
                      variant: "accordion"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_VExpansionPanel, { title: "高级选项（写回设置 / 黑名单 / Wiki 源）" }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VExpansionPanelText, null, {
                              default: _withCtx(() => [
                                _createVNode(_component_VRow, null, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VCol, {
                                      cols: "12",
                                      md: "6"
                                    }, {
                                      default: _withCtx(() => [
                                        _createVNode(_component_VSwitch, {
                                          modelValue: form.market_update_write_settings,
                                          "onUpdate:modelValue": _cache[55] || (_cache[55] = $event => ((form.market_update_write_settings) = $event)),
                                          color: "warning",
                                          inset: "",
                                          "hide-details": "",
                                          label: "写回插件设置",
                                          disabled: !form.market_update_enabled
                                        }, null, 8, ["modelValue", "disabled"])
                                      ]),
                                      _: 1
                                    }),
                                    _createVNode(_component_VCol, {
                                      cols: "12",
                                      md: "6"
                                    }, {
                                      default: _withCtx(() => [
                                        _createVNode(_component_VSwitch, {
                                          modelValue: form.market_update_write_env,
                                          "onUpdate:modelValue": _cache[56] || (_cache[56] = $event => ((form.market_update_write_env) = $event)),
                                          color: "warning",
                                          inset: "",
                                          "hide-details": "",
                                          label: "写回环境变量",
                                          disabled: !form.market_update_enabled
                                        }, null, 8, ["modelValue", "disabled"])
                                      ]),
                                      _: 1
                                    })
                                  ]),
                                  _: 1
                                }),
                                _createVNode(_component_VRow, null, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VCol, {
                                      cols: "12",
                                      md: "6"
                                    }, {
                                      default: _withCtx(() => [
                                        _createVNode(_component_VSwitch, {
                                          modelValue: form.market_update_blacklist_enabled,
                                          "onUpdate:modelValue": _cache[57] || (_cache[57] = $event => ((form.market_update_blacklist_enabled) = $event)),
                                          color: "primary",
                                          inset: "",
                                          "hide-details": "",
                                          label: "启用更新黑名单",
                                          disabled: !form.market_update_enabled
                                        }, null, 8, ["modelValue", "disabled"])
                                      ]),
                                      _: 1
                                    }),
                                    _createVNode(_component_VCol, {
                                      cols: "12",
                                      md: "6"
                                    }, {
                                      default: _withCtx(() => [
                                        _createVNode(_component_VTextField, {
                                          modelValue: form.market_update_timeout,
                                          "onUpdate:modelValue": _cache[58] || (_cache[58] = $event => ((form.market_update_timeout) = $event)),
                                          label: "请求超时（秒）",
                                          type: "number",
                                          min: "1",
                                          disabled: !form.market_update_enabled
                                        }, null, 8, ["modelValue", "disabled"])
                                      ]),
                                      _: 1
                                    })
                                  ]),
                                  _: 1
                                }),
                                _createVNode(_component_VRow, null, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VCol, { cols: "12" }, {
                                      default: _withCtx(() => [
                                        _createVNode(_component_VTextarea, {
                                          modelValue: form.market_update_blacklist,
                                          "onUpdate:modelValue": _cache[59] || (_cache[59] = $event => ((form.market_update_blacklist) = $event)),
                                          label: "黑名单插件 ID（逗号分隔）",
                                          rows: "2",
                                          "auto-grow": "",
                                          disabled: !form.market_update_enabled || !form.market_update_blacklist_enabled
                                        }, null, 8, ["modelValue", "disabled"])
                                      ]),
                                      _: 1
                                    })
                                  ]),
                                  _: 1
                                }),
                                _createVNode(_component_VRow, null, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VCol, { cols: "12" }, {
                                      default: _withCtx(() => [
                                        _createVNode(_component_VTextField, {
                                          modelValue: form.market_update_wiki_url,
                                          "onUpdate:modelValue": _cache[60] || (_cache[60] = $event => ((form.market_update_wiki_url) = $event)),
                                          label: "Wiki 地址",
                                          disabled: !form.market_update_enabled
                                        }, null, 8, ["modelValue", "disabled"])
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
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_VDivider, { class: "my-4" }),
                    _createElementVNode("div", _hoisted_21, [
                      _createVNode(_component_VBtn, {
                        color: "primary",
                        variant: "outlined",
                        "prepend-icon": "mdi-eye-outline",
                        loading: action.running === 'preview_market_update',
                        onClick: _cache[61] || (_cache[61] = $event => (runAction('preview_market_update', '插件库更新')))
                      }, {
                        default: _withCtx(() => [...(_cache[103] || (_cache[103] = [
                          _createTextVNode(" 预览更新 ", -1)
                        ]))]),
                        _: 1
                      }, 8, ["loading"]),
                      _createVNode(_component_VBtn, {
                        color: "primary",
                        variant: "tonal",
                        "prepend-icon": "mdi-cloud-sync-outline",
                        loading: action.running === 'run_market_update',
                        onClick: _cache[62] || (_cache[62] = $event => (runAction('run_market_update', '插件库更新')))
                      }, {
                        default: _withCtx(() => [...(_cache[104] || (_cache[104] = [
                          _createTextVNode(" 立即检查 ", -1)
                        ]))]),
                        _: 1
                      }, 8, ["loading"])
                    ])
                  ]),
                  _: 1
                })
              ], 512), [
                [_vShow, activeSub.value === 'market']
              ]),
              _withDirectives(_createElementVNode("div", _hoisted_22, [
                _createVNode(_component_VForm, null, {
                  default: _withCtx(() => [
                    _cache[110] || (_cache[110] = _createElementVNode("div", { class: "aoa-section-title" }, "目标插件", -1)),
                    _createVNode(_component_VRow, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_VCol, { cols: "12" }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSelect, {
                              modelValue: form.plugin_uninstall_ids,
                              "onUpdate:modelValue": _cache[63] || (_cache[63] = $event => ((form.plugin_uninstall_ids) = $event)),
                              items: installedPlugins.value,
                              loading: installedLoading.value,
                              label: "选择要清理残留的已安装插件",
                              multiple: "",
                              chips: "",
                              "closable-chips": "",
                              clearable: "",
                              "prepend-inner-icon": "mdi-puzzle-remove-outline"
                            }, null, 8, ["modelValue", "items", "loading"]),
                            _cache[106] || (_cache[106] = _createElementVNode("div", { class: "aoa-hint" }, "从已安装插件中多选。先“预览”确认范围，再“执行”清理。", -1))
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_VDivider, { class: "my-4" }),
                    _cache[111] || (_cache[111] = _createElementVNode("div", { class: "aoa-section-title" }, "清理范围", -1)),
                    _createVNode(_component_VRow, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "6"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSwitch, {
                              modelValue: form.plugin_uninstall_clear_config,
                              "onUpdate:modelValue": _cache[64] || (_cache[64] = $event => ((form.plugin_uninstall_clear_config) = $event)),
                              color: "primary",
                              inset: "",
                              "hide-details": "",
                              label: "清除插件配置"
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
                              "onUpdate:modelValue": _cache[65] || (_cache[65] = $event => ((form.plugin_uninstall_clear_data) = $event)),
                              color: "primary",
                              inset: "",
                              "hide-details": "",
                              label: "清除插件数据"
                            }, null, 8, ["modelValue"])
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_VRow, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "6"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSwitch, {
                              modelValue: form.plugin_uninstall_notify,
                              "onUpdate:modelValue": _cache[66] || (_cache[66] = $event => ((form.plugin_uninstall_notify) = $event)),
                              color: "primary",
                              inset: "",
                              "hide-details": "",
                              label: "清理结果通知"
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
                              "onUpdate:modelValue": _cache[67] || (_cache[67] = $event => ((form.plugin_uninstall_delete_source) = $event)),
                              color: "error",
                              inset: "",
                              "hide-details": "",
                              label: "删除本地源码（高风险，不可恢复）"
                            }, null, 8, ["modelValue"]),
                            _cache[107] || (_cache[107] = _createElementVNode("div", { class: "aoa-hint" }, "仅对本地源码插件生效，删除后需重新安装。", -1))
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_VDivider, { class: "my-4" }),
                    _cache[112] || (_cache[112] = _createElementVNode("div", { class: "aoa-section-title" }, "执行", -1)),
                    _createElementVNode("div", _hoisted_23, [
                      _createVNode(_component_VBtn, {
                        color: "primary",
                        variant: "outlined",
                        "prepend-icon": "mdi-eye-outline",
                        disabled: !form.plugin_uninstall_ids || !form.plugin_uninstall_ids.length,
                        loading: action.running === 'preview_plugin_uninstall',
                        onClick: _cache[68] || (_cache[68] = $event => (runAction('preview_plugin_uninstall', '插件治理预览')))
                      }, {
                        default: _withCtx(() => [...(_cache[108] || (_cache[108] = [
                          _createTextVNode(" 预览清理范围 ", -1)
                        ]))]),
                        _: 1
                      }, 8, ["disabled", "loading"]),
                      _createVNode(_component_VBtn, {
                        color: "error",
                        variant: "tonal",
                        "prepend-icon": "mdi-broom",
                        disabled: !form.plugin_uninstall_ids || !form.plugin_uninstall_ids.length,
                        loading: action.running === 'run_plugin_uninstall',
                        onClick: _cache[69] || (_cache[69] = $event => (runAction('run_plugin_uninstall', '插件残留治理')))
                      }, {
                        default: _withCtx(() => [...(_cache[109] || (_cache[109] = [
                          _createTextVNode(" 执行清理 ", -1)
                        ]))]),
                        _: 1
                      }, 8, ["disabled", "loading"])
                    ]),
                    _cache[113] || (_cache[113] = _createElementVNode("div", { class: "aoa-hint mt-2" }, "残留清理为不可逆操作，执行前请务必先预览确认。", -1))
                  ]),
                  _: 1
                })
              ], 512), [
                [_vShow, activeSub.value === 'clean']
              ])
            ])
          ])
        ]),
        _createVNode(_component_VDivider),
        _createVNode(_component_VCardActions, { class: "aoa-actions" }, {
          default: _withCtx(() => [
            _createVNode(_component_VFadeTransition, null, {
              default: _withCtx(() => [
                (action.message)
                  ? (_openBlock(), _createElementBlock("span", {
                      key: 0,
                      class: _normalizeClass([action.ok ? 'text-success' : 'text-error', "text-caption"])
                    }, [
                      _createVNode(_component_VIcon, {
                        icon: action.ok ? 'mdi-check-circle-outline' : 'mdi-alert-circle-outline',
                        size: "16",
                        class: "mr-1"
                      }, null, 8, ["icon"]),
                      _createTextVNode(_toDisplayString(action.message), 1)
                    ], 2))
                  : _createCommentVNode("", true)
              ]),
              _: 1
            }),
            _createVNode(_component_VSpacer),
            _createVNode(_component_VBtn, {
              variant: "text",
              onClick: _cache[70] || (_cache[70] = $event => (emit('close')))
            }, {
              default: _withCtx(() => [...(_cache[114] || (_cache[114] = [
                _createTextVNode("取消", -1)
              ]))]),
              _: 1
            }),
            _createVNode(_component_VBtn, {
              color: "primary",
              variant: "flat",
              "prepend-icon": "mdi-content-save-outline",
              onClick: saveConfig
            }, {
              default: _withCtx(() => [...(_cache[115] || (_cache[115] = [
                _createTextVNode("保存配置", -1)
              ]))]),
              _: 1
            })
          ]),
          _: 1
        })
      ]),
      _: 1
    })
  ]))
}
}

};
const Config = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-014639cf"]]);

export { Config as default };
