import { importShared } from './__federation_fn_import-JrT3xvdd.js';
import { _ as _export_sfc, g as getPluginApi, p as postPluginApi } from './_plugin-vue_export-helper-DGWTz_NE.js';

const {resolveComponent:_resolveComponent,createVNode:_createVNode,withCtx:_withCtx,createTextVNode:_createTextVNode,toDisplayString:_toDisplayString,createElementVNode:_createElementVNode,renderList:_renderList,Fragment:_Fragment,openBlock:_openBlock,createElementBlock:_createElementBlock,createBlock:_createBlock,normalizeClass:_normalizeClass,vShow:_vShow,withDirectives:_withDirectives,unref:_unref,createCommentVNode:_createCommentVNode} = await importShared('vue');


const _hoisted_1 = { class: "aoa-config" };
const _hoisted_2 = { class: "d-flex align-center" };
const _hoisted_3 = { class: "aoa-body" };
const _hoisted_4 = { class: "aoa-nav" };
const _hoisted_5 = { class: "aoa-content" };
const _hoisted_6 = { class: "aoa-subtabs" };
const _hoisted_7 = ["onClick"];
const _hoisted_8 = { class: "aoa-window" };
const _hoisted_9 = { class: "aoa-pane" };
const _hoisted_10 = { class: "aoa-btn-row" };
const _hoisted_11 = { class: "aoa-pane" };
const _hoisted_12 = { class: "aoa-btn-row" };
const _hoisted_13 = { class: "aoa-pane" };
const _hoisted_14 = { class: "aoa-pane" };
const _hoisted_15 = { class: "aoa-btn-row" };
const _hoisted_16 = { class: "aoa-pane" };
const _hoisted_17 = { class: "d-flex align-center justify-space-between mb-1" };
const _hoisted_18 = { class: "aoa-btn-row" };
const _hoisted_19 = { class: "aoa-pane" };
const _hoisted_20 = { class: "aoa-pane" };
const _hoisted_21 = { class: "aoa-btn-row" };
const _hoisted_22 = { class: "aoa-pane" };
const _hoisted_23 = { class: "aoa-btn-row" };
const _hoisted_24 = { class: "aoa-pane" };
const _hoisted_25 = { class: "aoa-btn-row" };
const _hoisted_26 = { class: "aoa-pane" };
const _hoisted_27 = { class: "aoa-btn-row" };
const _hoisted_28 = { class: "aoa-pane" };
const _hoisted_29 = { class: "aoa-btn-row" };
const _hoisted_30 = { class: "aoa-pane" };
const _hoisted_31 = { class: "aoa-pane" };
const _hoisted_32 = { class: "aoa-btn-row" };

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

// 插件库仓库（更新黑名单用）
const pluginMarkets = ref([]);
const marketsLoading = ref(false);
async function loadPluginMarkets() {
  marketsLoading.value = true;
  try {
    const res = await getPluginApi(props.api, 'plugin_markets');
    pluginMarkets.value = Array.isArray(res) ? res : (res?.data || []);
  } catch {
    pluginMarkets.value = [];
  } finally {
    marketsLoading.value = false;
  }
}

// 下载器列表（自动删种用）
const downloaderOptions = ref([]);
const downloadersLoading = ref(false);
async function loadDownloaders() {
  downloadersLoading.value = true;
  try {
    const res = await getPluginApi(props.api, 'downloaders');
    downloaderOptions.value = Array.isArray(res) ? res : (res?.data || []);
  } catch {
    downloaderOptions.value = [];
  } finally {
    downloadersLoading.value = false;
  }
}

// 媒体服务器列表（媒体库通知按服务器过滤用）
const mediaserverOptions = ref([]);
const mediaserversLoading = ref(false);
async function loadMediaservers() {
  mediaserversLoading.value = true;
  try {
    const res = await getPluginApi(props.api, 'mediaservers');
    mediaserverOptions.value = Array.isArray(res) ? res : (res?.data || []);
  } catch {
    mediaserverOptions.value = [];
  } finally {
    mediaserversLoading.value = false;
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
  report_version: true,
  report_site_status: true,
  report_site_increment: true,
  report_today_download: true,
  report_transfer: true,
  report_subscribe: true,
  report_storage: true,
  report_media_stat: true,
  report_summary: true,
  subscribe_reminder_enabled: true,
  subscribe_reminder_onlyonce: false,
  subscribe_reminder_time: '9',
  subscribe_reminder_cron: '0 9 * * *',
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
  market_update_blacklist: [],
  market_update_auto_install: false,
  market_update_install_ids: [],
  market_update_exclude_ids: [],
  market_update_skip_running: true,
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
  seedclean_enabled: false,
  seedclean_cron: '0 */12 * * *',
  seedclean_action: 'pause',
  seedclean_downloaders: [],
  seedclean_size: '',
  seedclean_ratio: '',
  seedclean_time: '',
  seedclean_upspeed: '',
  seedclean_labels: '',
  seedclean_pathkeywords: '',
  seedclean_trackerkeywords: '',
  seedclean_errorkeywords: '',
  seedclean_torrentstates: '',
  seedclean_torrentcategorys: '',
  seedclean_samedata: false,
  seedclean_mponly: false,
  seedclean_notify: true,
  subfill_enabled: false,
  subfill_details: [],
  subfill_notify: false,
  subfill_category_enabled: false,
  subfill_category_confs: '',
  msgnotify_enabled: false,
  msgnotify_types: [],
  msgnotify_servers: [],
  dltag_downloaders: [],
  dltag_prefix: '',
  dltag_notify: true,
};

const mainTabs = [
  { key: 'report', group: '汇报中心', title: '每日汇报', icon: 'mdi-newspaper-variant-outline', desc: '聚合汇报中心：勾选要并入每日汇报的内容，按计划统一推送。' },
  { key: 'subreminder', group: '订阅与站点', title: '订阅提醒', icon: 'mdi-bell-ring-outline', desc: '定时推送订阅追新提醒。' },
  { key: 'subfill', group: '订阅与站点', title: '订阅规则自动填充', icon: 'mdi-auto-fix', desc: '下载到资源后自动回填订阅的空规则，锁定后续剧集追同款。' },
  { key: 'sitestat', group: '订阅与站点', title: '站点数据统计', icon: 'mdi-chart-line', desc: '采集站点上传/下载/做种等数据，可上仪表盘与日报。' },
  { key: 'seedclean', group: '下载与媒体', title: '种子治理', icon: 'mdi-delete-sweep-outline', desc: '按规则自动暂停/删除下载器中的种子（功能移植自“自动删种”）。' },
  { key: 'dltag', group: '下载与媒体', title: '下载器助手', icon: 'mdi-download-network-outline', desc: '下载器活动种子概览（见仪表盘）+ 按站点为种子批量补打标签。' },
  { key: 'msgnotify', group: '下载与媒体', title: '媒体通知', icon: 'mdi-television-play', desc: 'Emby/Jellyfin/Plex 的播放、入库、登录等 webhook 事件推送通知。' },
  { key: 'backup', group: '系统维护', title: '自动备份', icon: 'mdi-archive-arrow-up-outline', desc: '设置本地备份、保留数量和 WebDAV 远端备份。' },
  { key: 'cleanup', group: '系统维护', title: '日志清理', icon: 'mdi-file-document-remove-outline', desc: '设置插件日志保留行数、清理时间和结果通知。' },
  { key: 'updates', group: '系统维护', title: '更新检查', icon: 'mdi-update', desc: '检查 MoviePilot 与插件库更新，可自动更新已安装插件。' },
  { key: 'plugin', group: '系统维护', title: '插件残留清理', icon: 'mdi-puzzle-remove-outline', desc: '清理已卸载插件留下的配置、数据、日志或本地源码残留。' },
];

const navGroups = computed(() => {
  const order = [];
  const map = {};
  for (const item of mainTabs) {
    const g = item.group || '其他';
    if (!map[g]) { map[g] = { name: g, items: [] }; order.push(map[g]); }
    map[g].items.push(item);
  }
  return order
});

const subTabs = {
  report: [
    { key: 'basic', title: '汇报栏目', icon: 'mdi-tune-variant' },
  ],
  subreminder: [
    { key: 'subscribe', title: '订阅提醒', icon: 'mdi-bell-ring-outline' },
  ],
  subfill: [
    { key: 'subfill', title: '订阅规则自动填充', icon: 'mdi-auto-fix' },
  ],
  sitestat: [
    { key: 'sites', title: '站点数据统计', icon: 'mdi-chart-line' },
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
  seedclean: [
    { key: 'seedremove', title: '自动删种', icon: 'mdi-delete-sweep-outline' },
  ],
  dltag: [
    { key: 'dltagmain', title: '批量打标签', icon: 'mdi-tag-multiple-outline' },
  ],
  msgnotify: [
    { key: 'server', title: '服务器通知', icon: 'mdi-television-play' },
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
const seedActionItems = [{ title: '暂停', value: 'pause' }, { title: '删除种子', value: 'delete' }, { title: '删除种子和文件', value: 'deletefile' }];
const subfillDetailItems = ['分辨率', '资源质量', '特效', '制作组', '站点'].map(v => ({ title: v, value: v }));
const msgGroupItems = ['新入库', '开始播放', '停止播放', '登录成功', '登录失败', '标记'].map(v => ({ title: v, value: v }));
const reportSections = [
  { key: 'report_version', label: 'MoviePilot 版本' },
  { key: 'report_site_status', label: '站点状态' },
  { key: 'report_site_increment', label: '站点增量' },
  { key: 'report_today_download', label: '今日下载' },
  { key: 'report_transfer', label: '入库整理' },
  { key: 'report_subscribe', label: '订阅追新' },
  { key: 'report_storage', label: '存储空间' },
  { key: 'report_media_stat', label: '媒体统计' },
  { key: 'report_summary', label: '今日摘要' },
];

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
  form.market_update_blacklist = toArr(form.market_update_blacklist);
  form.market_update_install_ids = toArr(form.market_update_install_ids);
  form.market_update_exclude_ids = toArr(form.market_update_exclude_ids);
  form.seedclean_downloaders = toArr(form.seedclean_downloaders);
  form.subfill_details = toArr(form.subfill_details);
  form.msgnotify_types = toArr(form.msgnotify_types);
  form.msgnotify_servers = toArr(form.msgnotify_servers);
  form.dltag_downloaders = toArr(form.dltag_downloaders);
}, { immediate: true, deep: true });

function saveConfig() {
  emit('save', { ...form });
}

function selectMain(key) {
  if (activeMain.value === key) return
  activeMain.value = key;
  activeSub.value = subTabs[key]?.[0]?.key || '';
}

onMounted(() => {
  loadInstalledPlugins();
  loadPluginMarkets();
  loadDownloaders();
  loadMediaservers();
});

return (_ctx, _cache) => {
  const _component_VIcon = _resolveComponent("VIcon");
  const _component_VAvatar = _resolveComponent("VAvatar");
  const _component_VCardTitle = _resolveComponent("VCardTitle");
  const _component_VCardSubtitle = _resolveComponent("VCardSubtitle");
  const _component_VSwitch = _resolveComponent("VSwitch");
  const _component_VCardItem = _resolveComponent("VCardItem");
  const _component_VDivider = _resolveComponent("VDivider");
  const _component_VListSubheader = _resolveComponent("VListSubheader");
  const _component_VListItemTitle = _resolveComponent("VListItemTitle");
  const _component_VListItem = _resolveComponent("VListItem");
  const _component_VList = _resolveComponent("VList");
  const _component_VCol = _resolveComponent("VCol");
  const _component_VCronField = _resolveComponent("VCronField");
  const _component_VRow = _resolveComponent("VRow");
  const _component_VTextField = _resolveComponent("VTextField");
  const _component_VBtn = _resolveComponent("VBtn");
  const _component_VForm = _resolveComponent("VForm");
  const _component_VSelect = _resolveComponent("VSelect");
  const _component_VTextarea = _resolveComponent("VTextarea");
  const _component_VChip = _resolveComponent("VChip");
  const _component_VSlider = _resolveComponent("VSlider");
  const _component_VExpansionPanelText = _resolveComponent("VExpansionPanelText");
  const _component_VExpansionPanel = _resolveComponent("VExpansionPanel");
  const _component_VExpansionPanels = _resolveComponent("VExpansionPanels");
  const _component_VAlert = _resolveComponent("VAlert");
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
              default: _withCtx(() => [...(_cache[98] || (_cache[98] = [
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
                (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(navGroups.value, (grp) => {
                  return (_openBlock(), _createElementBlock(_Fragment, {
                    key: grp.name
                  }, [
                    _createVNode(_component_VListSubheader, { class: "aoa-nav-group" }, {
                      default: _withCtx(() => [
                        _createTextVNode(_toDisplayString(grp.name), 1)
                      ]),
                      _: 2
                    }, 1024),
                    (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(grp.items, (item) => {
                      return (_openBlock(), _createBlock(_component_VListItem, {
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
                      }, 1032, ["active", "onClick"]))
                    }), 128))
                  ], 64))
                }), 128))
              ]),
              _: 1
            })
          ]),
          _createElementVNode("section", _hoisted_5, [
            _createElementVNode("div", _hoisted_6, [
              (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(currentSubs.value, (sub) => {
                return (_openBlock(), _createElementBlock("button", {
                  key: sub.key,
                  type: "button",
                  class: _normalizeClass(["aoa-subtab", { 'aoa-subtab--active': activeSub.value === sub.key }]),
                  onClick: $event => (activeSub.value = sub.key)
                }, [
                  _createVNode(_component_VIcon, {
                    icon: sub.icon,
                    size: "18",
                    class: "mr-1"
                  }, null, 8, ["icon"]),
                  _createTextVNode(_toDisplayString(sub.title), 1)
                ], 10, _hoisted_7))
              }), 128))
            ]),
            _createVNode(_component_VDivider),
            _createElementVNode("div", _hoisted_8, [
              _withDirectives(_createElementVNode("div", _hoisted_9, [
                _createVNode(_component_VForm, null, {
                  default: _withCtx(() => [
                    _cache[102] || (_cache[102] = _createElementVNode("div", { class: "aoa-section-title" }, "汇报开关", -1)),
                    _createVNode(_component_VRow, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "6"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSwitch, {
                              modelValue: form.daily_report_enabled,
                              "onUpdate:modelValue": _cache[1] || (_cache[1] = $event => ((form.daily_report_enabled) = $event)),
                              color: "primary",
                              inset: "",
                              "hide-details": "",
                              label: "启用定时每日汇报"
                            }, null, 8, ["modelValue"]),
                            _cache[99] || (_cache[99] = _createElementVNode("div", { class: "aoa-hint" }, "关闭后将不再按计划自动发送汇报，仍可在下方手动触发。", -1))
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
                              "onUpdate:modelValue": _cache[2] || (_cache[2] = $event => ((form.daily_report_cron) = $event)),
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
                              "onUpdate:modelValue": _cache[3] || (_cache[3] = $event => ((form.daily_report_greeting) = $event)),
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
                    _cache[103] || (_cache[103] = _createElementVNode("div", { class: "aoa-section-title" }, "汇报栏目", -1)),
                    _cache[104] || (_cache[104] = _createElementVNode("div", { class: "aoa-hint mb-2" }, "每日汇报是聚合中心：逐栏目勾选要并入日报的内容（关掉则该栏目不出现在汇报里）。", -1)),
                    _createVNode(_component_VRow, null, {
                      default: _withCtx(() => [
                        (_openBlock(), _createElementBlock(_Fragment, null, _renderList(reportSections, (s) => {
                          return _createVNode(_component_VCol, {
                            key: s.key,
                            cols: "6",
                            md: "4"
                          }, {
                            default: _withCtx(() => [
                              _createVNode(_component_VSwitch, {
                                modelValue: form[s.key],
                                "onUpdate:modelValue": $event => ((form[s.key]) = $event),
                                color: "primary",
                                inset: "",
                                "hide-details": "",
                                density: "compact",
                                label: s.label
                              }, null, 8, ["modelValue", "onUpdate:modelValue", "label"])
                            ]),
                            _: 2
                          }, 1024)
                        }), 64))
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_VDivider, { class: "my-4" }),
                    _cache[105] || (_cache[105] = _createElementVNode("div", { class: "aoa-section-title" }, "手动触发", -1)),
                    _createElementVNode("div", _hoisted_10, [
                      _createVNode(_component_VBtn, {
                        color: "primary",
                        variant: "tonal",
                        "prepend-icon": "mdi-send-outline",
                        loading: action.running === 'run_daily_report',
                        onClick: _cache[4] || (_cache[4] = $event => (runAction('run_daily_report', '发送每日汇报')))
                      }, {
                        default: _withCtx(() => [...(_cache[100] || (_cache[100] = [
                          _createTextVNode(" 立即发送汇报 ", -1)
                        ]))]),
                        _: 1
                      }, 8, ["loading"]),
                      _createVNode(_component_VBtn, {
                        color: "primary",
                        variant: "tonal",
                        "prepend-icon": "mdi-heart-pulse",
                        loading: action.running === 'run_health_check',
                        onClick: _cache[5] || (_cache[5] = $event => (runAction('run_health_check', '健康巡查')))
                      }, {
                        default: _withCtx(() => [...(_cache[101] || (_cache[101] = [
                          _createTextVNode(" 立即健康巡查 ", -1)
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
              _withDirectives(_createElementVNode("div", _hoisted_11, [
                _createVNode(_component_VForm, null, {
                  default: _withCtx(() => [
                    _cache[108] || (_cache[108] = _createElementVNode("div", { class: "aoa-section-title" }, "订阅提醒", -1)),
                    _createVNode(_component_VRow, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_VCol, { cols: "12" }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSwitch, {
                              modelValue: form.subscribe_reminder_enabled,
                              "onUpdate:modelValue": _cache[6] || (_cache[6] = $event => ((form.subscribe_reminder_enabled) = $event)),
                              color: "primary",
                              inset: "",
                              "hide-details": "",
                              label: "启用独立订阅提醒推送"
                            }, null, 8, ["modelValue"]),
                            _cache[106] || (_cache[106] = _createElementVNode("div", { class: "aoa-hint" }, "在指定时间单独推送订阅追新提醒（是否并入每日汇报见基础设置）。", -1))
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
                            _createVNode(_component_VCronField, {
                              modelValue: form.subscribe_reminder_cron,
                              "onUpdate:modelValue": _cache[7] || (_cache[7] = $event => ((form.subscribe_reminder_cron) = $event)),
                              label: "推送时间 (Cron)",
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
                              "onUpdate:modelValue": _cache[8] || (_cache[8] = $event => ((form.subscribe_reminder_subtype) = $event)),
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
                              "onUpdate:modelValue": _cache[9] || (_cache[9] = $event => ((form.subscribe_reminder_msgtype) = $event)),
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
                    _createVNode(_component_VDivider, { class: "my-4" }),
                    _cache[109] || (_cache[109] = _createElementVNode("div", { class: "aoa-section-title" }, "手动触发", -1)),
                    _cache[110] || (_cache[110] = _createElementVNode("div", { class: "aoa-hint mb-2" }, "立即按当前设置推送一次今日订阅追新（独立于每日汇报）。", -1)),
                    _createElementVNode("div", _hoisted_12, [
                      _createVNode(_component_VBtn, {
                        color: "primary",
                        variant: "tonal",
                        "prepend-icon": "mdi-bell-ring-outline",
                        loading: action.running === 'run_subscribe_reminder',
                        onClick: _cache[10] || (_cache[10] = $event => (runAction('run_subscribe_reminder', '订阅提醒')))
                      }, {
                        default: _withCtx(() => [...(_cache[107] || (_cache[107] = [
                          _createTextVNode(" 立即推送订阅提醒 ", -1)
                        ]))]),
                        _: 1
                      }, 8, ["loading"])
                    ])
                  ]),
                  _: 1
                })
              ], 512), [
                [_vShow, activeSub.value === 'subscribe']
              ]),
              _withDirectives(_createElementVNode("div", _hoisted_13, [
                _createVNode(_component_VForm, null, {
                  default: _withCtx(() => [
                    _cache[112] || (_cache[112] = _createElementVNode("div", { class: "aoa-section-title" }, "站点数据统计", -1)),
                    _createVNode(_component_VRow, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_VCol, { cols: "12" }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSwitch, {
                              modelValue: form.site_stat_enabled,
                              "onUpdate:modelValue": _cache[11] || (_cache[11] = $event => ((form.site_stat_enabled) = $event)),
                              color: "primary",
                              inset: "",
                              "hide-details": "",
                              label: "启用站点数据统计采集"
                            }, null, 8, ["modelValue"]),
                            _cache[111] || (_cache[111] = _createElementVNode("div", { class: "aoa-hint" }, "关闭后不再统计站点数据（是否并入每日汇报见基础设置）。", -1))
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
                              "onUpdate:modelValue": _cache[12] || (_cache[12] = $event => ((form.site_stat_dashboard_type) = $event)),
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
                              "onUpdate:modelValue": _cache[13] || (_cache[13] = $event => ((form.site_stat_notify_type) = $event)),
                              items: siteNotifyItems,
                              label: "通知方式",
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
              _withDirectives(_createElementVNode("div", _hoisted_14, [
                _createVNode(_component_VForm, null, {
                  default: _withCtx(() => [
                    _cache[117] || (_cache[117] = _createElementVNode("div", { class: "aoa-section-title" }, "订阅规则自动填充", -1)),
                    _cache[118] || (_cache[118] = _createElementVNode("div", { class: "aoa-hint mb-2" }, "电视剧订阅下载到资源后，用该资源的实际规格自动回填订阅中“尚为空”的规则，锁定后续剧集追同款版本（功能移植自“订阅规则自动填充”）。已设置的字段不会被覆盖。", -1)),
                    _createVNode(_component_VRow, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "6"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSwitch, {
                              modelValue: form.subfill_enabled,
                              "onUpdate:modelValue": _cache[14] || (_cache[14] = $event => ((form.subfill_enabled) = $event)),
                              color: "primary",
                              inset: "",
                              "hide-details": "",
                              label: "启用订阅规则自动填充"
                            }, null, 8, ["modelValue"]),
                            _cache[113] || (_cache[113] = _createElementVNode("div", { class: "aoa-hint" }, "监听下载添加事件（仅电视剧），每个剧集 tmdbid 只填充一次。", -1))
                          ]),
                          _: 1
                        }),
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "6"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSwitch, {
                              modelValue: form.subfill_notify,
                              "onUpdate:modelValue": _cache[15] || (_cache[15] = $event => ((form.subfill_notify) = $event)),
                              color: "primary",
                              inset: "",
                              "hide-details": "",
                              label: "填充后发送通知",
                              disabled: !form.subfill_enabled
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
                            _createVNode(_component_VSelect, {
                              modelValue: form.subfill_details,
                              "onUpdate:modelValue": _cache[16] || (_cache[16] = $event => ((form.subfill_details) = $event)),
                              items: _unref(subfillDetailItems),
                              label: "自动填充哪些规则",
                              multiple: "",
                              chips: "",
                              "closable-chips": "",
                              clearable: "",
                              "prepend-inner-icon": "mdi-auto-fix",
                              disabled: !form.subfill_enabled
                            }, null, 8, ["modelValue", "items", "disabled"]),
                            _cache[114] || (_cache[114] = _createElementVNode("div", { class: "aoa-hint" }, "从下载资源中提取并回填：分辨率 / 资源质量 / 特效 / 制作组 / 站点。留空则不填充。", -1))
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_VDivider, { class: "my-4" }),
                    _cache[119] || (_cache[119] = _createElementVNode("div", { class: "aoa-section-title" }, "二级分类自定义填充", -1)),
                    _cache[120] || (_cache[120] = _createElementVNode("div", { class: "aoa-hint mb-2" }, "新增订阅时，按媒体的二级分类自动套用预设规则。每行一个分类，用 # 分隔字段；可用键：category、resolution、quality、effect、include、exclude、sites（站点名,逗号分隔）、savepath（支持 {name}）、filter_groups。", -1)),
                    _createVNode(_component_VRow, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "6"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSwitch, {
                              modelValue: form.subfill_category_enabled,
                              "onUpdate:modelValue": _cache[17] || (_cache[17] = $event => ((form.subfill_category_enabled) = $event)),
                              color: "primary",
                              inset: "",
                              "hide-details": "",
                              label: "启用二级分类自定义填充"
                            }, null, 8, ["modelValue"])
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
                              modelValue: form.subfill_category_confs,
                              "onUpdate:modelValue": _cache[18] || (_cache[18] = $event => ((form.subfill_category_confs) = $event)),
                              label: "二级分类规则（每行一个分类）",
                              "auto-grow": "",
                              rows: "3",
                              placeholder: "category:国漫,日番#resolution:1080p#quality:WEB-DL#include:简体#sites:馒头,青蛙#savepath:/media/动漫/{name}",
                              disabled: !form.subfill_category_enabled
                            }, null, 8, ["modelValue", "disabled"])
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_VDivider, { class: "my-4" }),
                    _cache[121] || (_cache[121] = _createElementVNode("div", { class: "aoa-section-title" }, "维护", -1)),
                    _createElementVNode("div", _hoisted_15, [
                      _createVNode(_component_VBtn, {
                        color: "primary",
                        variant: "tonal",
                        "prepend-icon": "mdi-history",
                        loading: action.running === 'subfill_clear_history',
                        onClick: _cache[19] || (_cache[19] = $event => (runAction('subfill_clear_history', '清理填充历史')))
                      }, {
                        default: _withCtx(() => [...(_cache[115] || (_cache[115] = [
                          _createTextVNode(" 清理历史记录 ", -1)
                        ]))]),
                        _: 1
                      }, 8, ["loading"]),
                      _createVNode(_component_VBtn, {
                        color: "warning",
                        variant: "tonal",
                        "prepend-icon": "mdi-backup-restore",
                        loading: action.running === 'subfill_clear_handled',
                        onClick: _cache[20] || (_cache[20] = $event => (runAction('subfill_clear_handled', '清理已处理记录')))
                      }, {
                        default: _withCtx(() => [...(_cache[116] || (_cache[116] = [
                          _createTextVNode(" 清理已处理记录 ", -1)
                        ]))]),
                        _: 1
                      }, 8, ["loading"])
                    ]),
                    _cache[122] || (_cache[122] = _createElementVNode("div", { class: "aoa-hint mt-2" }, "“清理已处理记录”后，已处理过的剧集下次下载会重新尝试填充。", -1))
                  ]),
                  _: 1
                })
              ], 512), [
                [_vShow, activeSub.value === 'subfill']
              ]),
              _withDirectives(_createElementVNode("div", _hoisted_16, [
                _createVNode(_component_VForm, null, {
                  default: _withCtx(() => [
                    _cache[127] || (_cache[127] = _createElementVNode("div", { class: "aoa-section-title" }, "本地备份", -1)),
                    _createVNode(_component_VRow, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "6"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSwitch, {
                              modelValue: form.backup_enabled,
                              "onUpdate:modelValue": _cache[21] || (_cache[21] = $event => ((form.backup_enabled) = $event)),
                              color: "primary",
                              inset: "",
                              "hide-details": "",
                              label: "启用定时本地备份"
                            }, null, 8, ["modelValue"]),
                            _cache[123] || (_cache[123] = _createElementVNode("div", { class: "aoa-hint" }, "按计划打包配置目录到本地备份路径。", -1))
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
                              "onUpdate:modelValue": _cache[22] || (_cache[22] = $event => ((form.backup_cron) = $event)),
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
                              "onUpdate:modelValue": _cache[23] || (_cache[23] = $event => ((form.backup_path) = $event)),
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
                            _createElementVNode("div", _hoisted_17, [
                              _cache[124] || (_cache[124] = _createElementVNode("span", { class: "text-body-2" }, "本地保留份数", -1)),
                              _createVNode(_component_VChip, {
                                size: "small",
                                color: "primary",
                                variant: "tonal"
                              }, {
                                default: _withCtx(() => [
                                  _createTextVNode(_toDisplayString(form.backup_keep_count) + " 份", 1)
                                ]),
                                _: 1
                              })
                            ]),
                            _createVNode(_component_VSlider, {
                              modelValue: form.backup_keep_count,
                              "onUpdate:modelValue": _cache[24] || (_cache[24] = $event => ((form.backup_keep_count) = $event)),
                              min: 1,
                              max: 30,
                              step: 1,
                              color: "primary",
                              "thumb-label": "",
                              "hide-details": "",
                              disabled: !form.backup_enabled
                            }, null, 8, ["modelValue", "disabled"]),
                            _cache[125] || (_cache[125] = _createElementVNode("div", { class: "aoa-hint" }, "超出份数时自动删除最旧的备份，范围 1-30 份。", -1))
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
                              "onUpdate:modelValue": _cache[25] || (_cache[25] = $event => ((form.backup_notify) = $event)),
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
                              "onUpdate:modelValue": _cache[26] || (_cache[26] = $event => ((form.backup_onlyonce) = $event)),
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
                    _createElementVNode("div", _hoisted_18, [
                      _createVNode(_component_VBtn, {
                        color: "primary",
                        variant: "tonal",
                        "prepend-icon": "mdi-archive-arrow-up-outline",
                        loading: action.running === 'run_backup',
                        onClick: _cache[27] || (_cache[27] = $event => (runAction('run_backup', '立即备份')))
                      }, {
                        default: _withCtx(() => [...(_cache[126] || (_cache[126] = [
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
              _withDirectives(_createElementVNode("div", _hoisted_19, [
                _createVNode(_component_VForm, null, {
                  default: _withCtx(() => [
                    _cache[129] || (_cache[129] = _createElementVNode("div", { class: "aoa-section-title" }, "WebDAV 远端备份", -1)),
                    _createVNode(_component_VRow, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_VCol, { cols: "12" }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSwitch, {
                              modelValue: form.backup_webdav_enabled,
                              "onUpdate:modelValue": _cache[28] || (_cache[28] = $event => ((form.backup_webdav_enabled) = $event)),
                              color: "primary",
                              inset: "",
                              "hide-details": "",
                              label: "启用 WebDAV 远端备份"
                            }, null, 8, ["modelValue"]),
                            _cache[128] || (_cache[128] = _createElementVNode("div", { class: "aoa-hint" }, "本地备份完成后同步上传到 WebDAV。", -1))
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
                              "onUpdate:modelValue": _cache[29] || (_cache[29] = $event => ((form.backup_webdav_hostname) = $event)),
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
                              "onUpdate:modelValue": _cache[30] || (_cache[30] = $event => ((form.backup_webdav_login) = $event)),
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
                              "onUpdate:modelValue": _cache[31] || (_cache[31] = $event => ((form.backup_webdav_password) = $event)),
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
                              "onUpdate:modelValue": _cache[32] || (_cache[32] = $event => ((form.backup_webdav_max_count) = $event)),
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
                              "onUpdate:modelValue": _cache[33] || (_cache[33] = $event => ((form.backup_webdav_notify) = $event)),
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
                              "onUpdate:modelValue": _cache[34] || (_cache[34] = $event => ((form.backup_webdav_digest_auth) = $event)),
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
                              "onUpdate:modelValue": _cache[35] || (_cache[35] = $event => ((form.backup_webdav_disable_check) = $event)),
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
              _withDirectives(_createElementVNode("div", _hoisted_20, [
                _createVNode(_component_VForm, null, {
                  default: _withCtx(() => [
                    _cache[133] || (_cache[133] = _createElementVNode("div", { class: "aoa-section-title" }, "插件日志清理", -1)),
                    _createVNode(_component_VRow, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "6"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSwitch, {
                              modelValue: form.log_clean_enabled,
                              "onUpdate:modelValue": _cache[36] || (_cache[36] = $event => ((form.log_clean_enabled) = $event)),
                              color: "primary",
                              inset: "",
                              "hide-details": "",
                              label: "启用定时日志清理"
                            }, null, 8, ["modelValue"]),
                            _cache[130] || (_cache[130] = _createElementVNode("div", { class: "aoa-hint" }, "按计划裁剪插件日志文件，仅保留指定行数。", -1))
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
                              "onUpdate:modelValue": _cache[37] || (_cache[37] = $event => ((form.log_clean_cron) = $event)),
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
                              "onUpdate:modelValue": _cache[38] || (_cache[38] = $event => ((form.log_clean_rows) = $event)),
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
                              "onUpdate:modelValue": _cache[39] || (_cache[39] = $event => ((form.log_clean_selected_ids) = $event)),
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
                            _cache[131] || (_cache[131] = _createElementVNode("div", { class: "aoa-hint" }, "从已安装插件中选择；不选则清理全部插件日志。", -1))
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
                              "onUpdate:modelValue": _cache[40] || (_cache[40] = $event => ((form.log_clean_notify) = $event)),
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
                              "onUpdate:modelValue": _cache[41] || (_cache[41] = $event => ((form.log_clean_onlyonce) = $event)),
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
                    _cache[134] || (_cache[134] = _createElementVNode("div", { class: "aoa-section-title" }, "手动触发", -1)),
                    _createElementVNode("div", _hoisted_21, [
                      _createVNode(_component_VBtn, {
                        color: "primary",
                        variant: "tonal",
                        "prepend-icon": "mdi-broom",
                        loading: action.running === 'run_log_clean',
                        onClick: _cache[42] || (_cache[42] = $event => (runAction('run_log_clean', '日志清理')))
                      }, {
                        default: _withCtx(() => [...(_cache[132] || (_cache[132] = [
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
              _withDirectives(_createElementVNode("div", _hoisted_22, [
                _createVNode(_component_VForm, null, {
                  default: _withCtx(() => [
                    _cache[137] || (_cache[137] = _createElementVNode("div", { class: "aoa-section-title" }, "MoviePilot 更新检查", -1)),
                    _cache[138] || (_cache[138] = _createElementVNode("div", { class: "aoa-hint mb-2" }, "仅检查并通知是否有新版本，不会在这里直接升级。", -1)),
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
                            _cache[135] || (_cache[135] = _createElementVNode("div", { class: "aoa-hint" }, "默认仅提醒；开启后将在更新后尝试重启 MoviePilot。", -1))
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_VDivider, { class: "my-4" }),
                    _createElementVNode("div", _hoisted_23, [
                      _createVNode(_component_VBtn, {
                        color: "primary",
                        variant: "tonal",
                        "prepend-icon": "mdi-update",
                        loading: action.running === 'run_mp_update',
                        onClick: _cache[48] || (_cache[48] = $event => (runAction('run_mp_update', '检查主程序更新')))
                      }, {
                        default: _withCtx(() => [...(_cache[136] || (_cache[136] = [
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
              _withDirectives(_createElementVNode("div", _hoisted_24, [
                _createVNode(_component_VForm, null, {
                  default: _withCtx(() => [
                    _cache[143] || (_cache[143] = _createElementVNode("div", { class: "aoa-section-title" }, "插件库更新检查", -1)),
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
                            _cache[139] || (_cache[139] = _createElementVNode("div", { class: "aoa-hint" }, "按间隔检查已安装插件是否有新版本。", -1))
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
                                        _createVNode(_component_VSelect, {
                                          modelValue: form.market_update_blacklist,
                                          "onUpdate:modelValue": _cache[59] || (_cache[59] = $event => ((form.market_update_blacklist) = $event)),
                                          items: pluginMarkets.value,
                                          loading: marketsLoading.value,
                                          label: "黑名单插件库（不参与更新检查）",
                                          multiple: "",
                                          chips: "",
                                          "closable-chips": "",
                                          clearable: "",
                                          "prepend-inner-icon": "mdi-block-helper",
                                          "no-data-text": "未配置任何插件库",
                                          disabled: !form.market_update_enabled || !form.market_update_blacklist_enabled
                                        }, null, 8, ["modelValue", "items", "loading", "disabled"])
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
                    _cache[144] || (_cache[144] = _createElementVNode("div", { class: "aoa-section-title" }, "自动更新已安装插件", -1)),
                    _cache[145] || (_cache[145] = _createElementVNode("div", { class: "aoa-hint mb-2" }, "检测到已安装插件有新版时自动下载安装并重载（功能移植自“插件自动更新”）。不开启则仅在检查时提醒有新版。", -1)),
                    _createVNode(_component_VRow, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "6"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSwitch, {
                              modelValue: form.market_update_auto_install,
                              "onUpdate:modelValue": _cache[61] || (_cache[61] = $event => ((form.market_update_auto_install) = $event)),
                              color: "warning",
                              inset: "",
                              "hide-details": "",
                              label: "自动安装插件新版",
                              disabled: !form.market_update_enabled
                            }, null, 8, ["modelValue", "disabled"]),
                            _cache[140] || (_cache[140] = _createElementVNode("div", { class: "aoa-hint" }, "高风险：会自动替换插件代码并重载。默认关闭，仅提醒；本插件自身永不自动更新。", -1))
                          ]),
                          _: 1
                        }),
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "6"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSwitch, {
                              modelValue: form.market_update_skip_running,
                              "onUpdate:modelValue": _cache[62] || (_cache[62] = $event => ((form.market_update_skip_running) = $event)),
                              color: "primary",
                              inset: "",
                              "hide-details": "",
                              label: "跳过正在运行的插件",
                              disabled: !form.market_update_enabled || !form.market_update_auto_install
                            }, null, 8, ["modelValue", "disabled"]),
                            _cache[141] || (_cache[141] = _createElementVNode("div", { class: "aoa-hint" }, "插件正在执行任务时不升级，避免中断。", -1))
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
                              modelValue: form.market_update_install_ids,
                              "onUpdate:modelValue": _cache[63] || (_cache[63] = $event => ((form.market_update_install_ids) = $event)),
                              items: installedPlugins.value,
                              loading: installedLoading.value,
                              label: "仅自动更新这些插件（留空＝全部已安装）",
                              multiple: "",
                              chips: "",
                              "closable-chips": "",
                              clearable: "",
                              "prepend-inner-icon": "mdi-puzzle-check-outline",
                              disabled: !form.market_update_enabled || !form.market_update_auto_install
                            }, null, 8, ["modelValue", "items", "loading", "disabled"])
                          ]),
                          _: 1
                        }),
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "6"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSelect, {
                              modelValue: form.market_update_exclude_ids,
                              "onUpdate:modelValue": _cache[64] || (_cache[64] = $event => ((form.market_update_exclude_ids) = $event)),
                              items: installedPlugins.value,
                              loading: installedLoading.value,
                              label: "排除（这些插件不自动更新）",
                              multiple: "",
                              chips: "",
                              "closable-chips": "",
                              clearable: "",
                              "prepend-inner-icon": "mdi-block-helper",
                              disabled: !form.market_update_enabled || !form.market_update_auto_install
                            }, null, 8, ["modelValue", "items", "loading", "disabled"])
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_VDivider, { class: "my-4" }),
                    _createElementVNode("div", _hoisted_25, [
                      _createVNode(_component_VBtn, {
                        color: "primary",
                        variant: "tonal",
                        "prepend-icon": "mdi-cloud-sync-outline",
                        loading: action.running === 'run_market_update',
                        onClick: _cache[65] || (_cache[65] = $event => (runAction('run_market_update', '插件库更新')))
                      }, {
                        default: _withCtx(() => [...(_cache[142] || (_cache[142] = [
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
              _withDirectives(_createElementVNode("div", _hoisted_26, [
                _createVNode(_component_VForm, null, {
                  default: _withCtx(() => [
                    _cache[149] || (_cache[149] = _createElementVNode("div", { class: "aoa-section-title" }, "目标插件", -1)),
                    _createVNode(_component_VRow, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_VCol, { cols: "12" }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSelect, {
                              modelValue: form.plugin_uninstall_ids,
                              "onUpdate:modelValue": _cache[66] || (_cache[66] = $event => ((form.plugin_uninstall_ids) = $event)),
                              items: installedPlugins.value,
                              loading: installedLoading.value,
                              label: "选择要清理残留的已安装插件",
                              multiple: "",
                              chips: "",
                              "closable-chips": "",
                              clearable: "",
                              "prepend-inner-icon": "mdi-puzzle-remove-outline"
                            }, null, 8, ["modelValue", "items", "loading"]),
                            _cache[146] || (_cache[146] = _createElementVNode("div", { class: "aoa-hint" }, "从已安装插件中多选。先“预览”确认范围，再“执行”清理。", -1))
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_VDivider, { class: "my-4" }),
                    _cache[150] || (_cache[150] = _createElementVNode("div", { class: "aoa-section-title" }, "清理范围", -1)),
                    _createVNode(_component_VRow, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "6"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSwitch, {
                              modelValue: form.plugin_uninstall_clear_config,
                              "onUpdate:modelValue": _cache[67] || (_cache[67] = $event => ((form.plugin_uninstall_clear_config) = $event)),
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
                              "onUpdate:modelValue": _cache[68] || (_cache[68] = $event => ((form.plugin_uninstall_clear_data) = $event)),
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
                              "onUpdate:modelValue": _cache[69] || (_cache[69] = $event => ((form.plugin_uninstall_notify) = $event)),
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
                              "onUpdate:modelValue": _cache[70] || (_cache[70] = $event => ((form.plugin_uninstall_delete_source) = $event)),
                              color: "error",
                              inset: "",
                              "hide-details": "",
                              label: "删除本地源码（高风险，不可恢复）"
                            }, null, 8, ["modelValue"]),
                            _cache[147] || (_cache[147] = _createElementVNode("div", { class: "aoa-hint" }, "仅对本地源码插件生效，删除后需重新安装。", -1))
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_VDivider, { class: "my-4" }),
                    _cache[151] || (_cache[151] = _createElementVNode("div", { class: "aoa-section-title" }, "执行", -1)),
                    _createElementVNode("div", _hoisted_27, [
                      _createVNode(_component_VBtn, {
                        color: "error",
                        variant: "tonal",
                        "prepend-icon": "mdi-broom",
                        disabled: !form.plugin_uninstall_ids || !form.plugin_uninstall_ids.length,
                        loading: action.running === 'run_plugin_uninstall',
                        onClick: _cache[71] || (_cache[71] = $event => (runAction('run_plugin_uninstall', '插件残留治理')))
                      }, {
                        default: _withCtx(() => [...(_cache[148] || (_cache[148] = [
                          _createTextVNode(" 执行清理 ", -1)
                        ]))]),
                        _: 1
                      }, 8, ["disabled", "loading"])
                    ]),
                    _cache[152] || (_cache[152] = _createElementVNode("div", { class: "aoa-hint mt-2" }, "残留清理为不可逆操作，执行前请务必先预览确认。", -1))
                  ]),
                  _: 1
                })
              ], 512), [
                [_vShow, activeSub.value === 'clean']
              ]),
              _withDirectives(_createElementVNode("div", _hoisted_28, [
                _createVNode(_component_VForm, null, {
                  default: _withCtx(() => [
                    _createVNode(_component_VAlert, {
                      type: "warning",
                      variant: "tonal",
                      class: "mb-4",
                      text: "自动删种有风险，设置不当可能丢数据！建议先用“暂停”动作验证条件命中正确，再改“删除”。未填写任何筛选条件时不会执行。"
                    }),
                    _cache[155] || (_cache[155] = _createElementVNode("div", { class: "aoa-section-title" }, "自动删种", -1)),
                    _createVNode(_component_VRow, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "6"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSwitch, {
                              modelValue: form.seedclean_enabled,
                              "onUpdate:modelValue": _cache[72] || (_cache[72] = $event => ((form.seedclean_enabled) = $event)),
                              color: "primary",
                              inset: "",
                              "hide-details": "",
                              label: "启用定时自动删种"
                            }, null, 8, ["modelValue"]),
                            _cache[153] || (_cache[153] = _createElementVNode("div", { class: "aoa-hint" }, "按计划在所选下载器中处理符合条件的种子。", -1))
                          ]),
                          _: 1
                        }),
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "6"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VCronField, {
                              modelValue: form.seedclean_cron,
                              "onUpdate:modelValue": _cache[73] || (_cache[73] = $event => ((form.seedclean_cron) = $event)),
                              label: "执行周期 (Cron)",
                              disabled: !form.seedclean_enabled
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
                              modelValue: form.seedclean_action,
                              "onUpdate:modelValue": _cache[74] || (_cache[74] = $event => ((form.seedclean_action) = $event)),
                              items: seedActionItems,
                              label: "动作",
                              disabled: !form.seedclean_enabled
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
                              modelValue: form.seedclean_downloaders,
                              "onUpdate:modelValue": _cache[75] || (_cache[75] = $event => ((form.seedclean_downloaders) = $event)),
                              items: downloaderOptions.value,
                              loading: downloadersLoading.value,
                              label: "下载器（必选）",
                              multiple: "",
                              chips: "",
                              "closable-chips": "",
                              clearable: "",
                              "prepend-inner-icon": "mdi-download-network-outline",
                              "no-data-text": "未配置下载器",
                              disabled: !form.seedclean_enabled
                            }, null, 8, ["modelValue", "items", "loading", "disabled"])
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_VDivider, { class: "my-4" }),
                    _cache[156] || (_cache[156] = _createElementVNode("div", { class: "aoa-section-title" }, "筛选条件", -1)),
                    _cache[157] || (_cache[157] = _createElementVNode("div", { class: "aoa-hint mb-2" }, "仅处理“同时满足所有已填条件”的种子；留空的条件不参与。全部留空则跳过不处理。", -1)),
                    _createVNode(_component_VRow, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "6"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VTextField, {
                              modelValue: form.seedclean_size,
                              "onUpdate:modelValue": _cache[76] || (_cache[76] = $event => ((form.seedclean_size) = $event)),
                              label: "种子大小（GB）",
                              placeholder: "例如 1-10",
                              disabled: !form.seedclean_enabled
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
                              modelValue: form.seedclean_ratio,
                              "onUpdate:modelValue": _cache[77] || (_cache[77] = $event => ((form.seedclean_ratio) = $event)),
                              label: "分享率不小于",
                              placeholder: "例如 2",
                              disabled: !form.seedclean_enabled
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
                              modelValue: form.seedclean_time,
                              "onUpdate:modelValue": _cache[78] || (_cache[78] = $event => ((form.seedclean_time) = $event)),
                              label: "做种时间不少于（小时）",
                              placeholder: "例如 240",
                              disabled: !form.seedclean_enabled
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
                              modelValue: form.seedclean_upspeed,
                              "onUpdate:modelValue": _cache[79] || (_cache[79] = $event => ((form.seedclean_upspeed) = $event)),
                              label: "平均上传速度上限（KB/s）",
                              placeholder: "低于此值才处理",
                              disabled: !form.seedclean_enabled
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
                              modelValue: form.seedclean_labels,
                              "onUpdate:modelValue": _cache[80] || (_cache[80] = $event => ((form.seedclean_labels) = $event)),
                              label: "标签",
                              placeholder: "用,分隔多个标签",
                              disabled: !form.seedclean_enabled
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
                              modelValue: form.seedclean_torrentcategorys,
                              "onUpdate:modelValue": _cache[81] || (_cache[81] = $event => ((form.seedclean_torrentcategorys) = $event)),
                              label: "任务分类",
                              placeholder: "用,分隔多个分类",
                              disabled: !form.seedclean_enabled
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
                              modelValue: form.seedclean_pathkeywords,
                              "onUpdate:modelValue": _cache[82] || (_cache[82] = $event => ((form.seedclean_pathkeywords) = $event)),
                              label: "保存路径关键词",
                              placeholder: "支持正则",
                              disabled: !form.seedclean_enabled
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
                              modelValue: form.seedclean_trackerkeywords,
                              "onUpdate:modelValue": _cache[83] || (_cache[83] = $event => ((form.seedclean_trackerkeywords) = $event)),
                              label: "Tracker 关键词",
                              placeholder: "支持正则",
                              disabled: !form.seedclean_enabled
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
                              modelValue: form.seedclean_torrentstates,
                              "onUpdate:modelValue": _cache[84] || (_cache[84] = $event => ((form.seedclean_torrentstates) = $event)),
                              label: "任务状态（仅 QB）",
                              placeholder: "用,分隔，如 pausedUP,stalledUP",
                              disabled: !form.seedclean_enabled
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
                              modelValue: form.seedclean_errorkeywords,
                              "onUpdate:modelValue": _cache[85] || (_cache[85] = $event => ((form.seedclean_errorkeywords) = $event)),
                              label: "错误信息关键词（仅 TR）",
                              placeholder: "支持正则",
                              disabled: !form.seedclean_enabled
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
                              modelValue: form.seedclean_samedata,
                              "onUpdate:modelValue": _cache[86] || (_cache[86] = $event => ((form.seedclean_samedata) = $event)),
                              color: "primary",
                              inset: "",
                              "hide-details": "",
                              label: "处理辅种（同名同大小一并处理）",
                              disabled: !form.seedclean_enabled
                            }, null, 8, ["modelValue", "disabled"])
                          ]),
                          _: 1
                        }),
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "4"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSwitch, {
                              modelValue: form.seedclean_mponly,
                              "onUpdate:modelValue": _cache[87] || (_cache[87] = $event => ((form.seedclean_mponly) = $event)),
                              color: "primary",
                              inset: "",
                              "hide-details": "",
                              label: "仅 MoviePilot 任务",
                              disabled: !form.seedclean_enabled
                            }, null, 8, ["modelValue", "disabled"])
                          ]),
                          _: 1
                        }),
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "4"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSwitch, {
                              modelValue: form.seedclean_notify,
                              "onUpdate:modelValue": _cache[88] || (_cache[88] = $event => ((form.seedclean_notify) = $event)),
                              color: "primary",
                              inset: "",
                              "hide-details": "",
                              label: "处理结果通知",
                              disabled: !form.seedclean_enabled
                            }, null, 8, ["modelValue", "disabled"])
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_VDivider, { class: "my-4" }),
                    _cache[158] || (_cache[158] = _createElementVNode("div", { class: "aoa-section-title" }, "手动触发", -1)),
                    _createElementVNode("div", _hoisted_29, [
                      _createVNode(_component_VBtn, {
                        color: "error",
                        variant: "tonal",
                        "prepend-icon": "mdi-delete-sweep-outline",
                        disabled: !form.seedclean_downloaders || !form.seedclean_downloaders.length,
                        loading: action.running === 'run_seed_clean',
                        onClick: _cache[89] || (_cache[89] = $event => (runAction('run_seed_clean', '自动删种')))
                      }, {
                        default: _withCtx(() => [...(_cache[154] || (_cache[154] = [
                          _createTextVNode(" 立即执行 ", -1)
                        ]))]),
                        _: 1
                      }, 8, ["disabled", "loading"])
                    ]),
                    _cache[159] || (_cache[159] = _createElementVNode("div", { class: "aoa-hint mt-2" }, "立即执行将按上面已填条件处理；建议先把动作设为“暂停”确认无误。", -1))
                  ]),
                  _: 1
                })
              ], 512), [
                [_vShow, activeSub.value === 'seedremove']
              ]),
              _withDirectives(_createElementVNode("div", _hoisted_30, [
                _createVNode(_component_VForm, null, {
                  default: _withCtx(() => [
                    _cache[161] || (_cache[161] = _createElementVNode("div", { class: "aoa-section-title" }, "媒体库服务器通知", -1)),
                    _cache[162] || (_cache[162] = _createElementVNode("div", { class: "aoa-hint mb-2" }, "监听 Emby/Jellyfin/Plex 的 webhook 事件并推送通知（需先在 MoviePilot 把媒体服务器 webhook 指向 MP）。不含原插件的剧集聚合/IP定位/海报抓取。", -1)),
                    _createVNode(_component_VRow, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "6"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSwitch, {
                              modelValue: form.msgnotify_enabled,
                              "onUpdate:modelValue": _cache[90] || (_cache[90] = $event => ((form.msgnotify_enabled) = $event)),
                              color: "primary",
                              inset: "",
                              "hide-details": "",
                              label: "启用媒体库服务器通知"
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
                            _createVNode(_component_VSelect, {
                              modelValue: form.msgnotify_types,
                              "onUpdate:modelValue": _cache[91] || (_cache[91] = $event => ((form.msgnotify_types) = $event)),
                              items: _unref(msgGroupItems),
                              label: "通知哪些事件",
                              multiple: "",
                              chips: "",
                              "closable-chips": "",
                              clearable: "",
                              "prepend-inner-icon": "mdi-bell-cog-outline",
                              disabled: !form.msgnotify_enabled
                            }, null, 8, ["modelValue", "items", "disabled"]),
                            _cache[160] || (_cache[160] = _createElementVNode("div", { class: "aoa-hint" }, "新入库 / 开始播放 / 停止播放 / 登录成功 / 登录失败 / 标记。留空则不通知。", -1))
                          ]),
                          _: 1
                        }),
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "6"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSelect, {
                              modelValue: form.msgnotify_servers,
                              "onUpdate:modelValue": _cache[92] || (_cache[92] = $event => ((form.msgnotify_servers) = $event)),
                              items: mediaserverOptions.value,
                              loading: mediaserversLoading.value,
                              label: "仅这些媒体服务器（留空＝全部）",
                              multiple: "",
                              chips: "",
                              "closable-chips": "",
                              clearable: "",
                              "prepend-inner-icon": "mdi-server-network",
                              "no-data-text": "未获取到媒体服务器",
                              disabled: !form.msgnotify_enabled
                            }, null, 8, ["modelValue", "items", "loading", "disabled"])
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
                [_vShow, activeSub.value === 'server']
              ]),
              _withDirectives(_createElementVNode("div", _hoisted_31, [
                _createVNode(_component_VForm, null, {
                  default: _withCtx(() => [
                    _cache[164] || (_cache[164] = _createElementVNode("div", { class: "aoa-section-title" }, "按站点为种子批量补打标签", -1)),
                    _cache[165] || (_cache[165] = _createElementVNode("div", { class: "aoa-hint mb-2" }, "遍历下载器中的种子，按其 tracker 所属站点补打标签（已打的跳过，幂等安全）；活动种子概览见仪表盘。功能移植自“下载器助手”。", -1)),
                    _createVNode(_component_VRow, null, {
                      default: _withCtx(() => [
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "6"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSelect, {
                              modelValue: form.dltag_downloaders,
                              "onUpdate:modelValue": _cache[93] || (_cache[93] = $event => ((form.dltag_downloaders) = $event)),
                              items: downloaderOptions.value,
                              loading: downloadersLoading.value,
                              label: "下载器（留空＝全部已配置）",
                              multiple: "",
                              chips: "",
                              "closable-chips": "",
                              clearable: "",
                              "prepend-inner-icon": "mdi-download-network-outline"
                            }, null, 8, ["modelValue", "items", "loading"])
                          ]),
                          _: 1
                        }),
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "3"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VTextField, {
                              modelValue: form.dltag_prefix,
                              "onUpdate:modelValue": _cache[94] || (_cache[94] = $event => ((form.dltag_prefix) = $event)),
                              label: "标签前缀（可选）",
                              placeholder: "如 站点-",
                              clearable: ""
                            }, null, 8, ["modelValue"])
                          ]),
                          _: 1
                        }),
                        _createVNode(_component_VCol, {
                          cols: "12",
                          md: "3"
                        }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VSwitch, {
                              modelValue: form.dltag_notify,
                              "onUpdate:modelValue": _cache[95] || (_cache[95] = $event => ((form.dltag_notify) = $event)),
                              color: "primary",
                              inset: "",
                              "hide-details": "",
                              label: "完成后通知"
                            }, null, 8, ["modelValue"])
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    _createVNode(_component_VDivider, { class: "my-4" }),
                    _createElementVNode("div", _hoisted_32, [
                      _createVNode(_component_VBtn, {
                        color: "primary",
                        variant: "tonal",
                        "prepend-icon": "mdi-tag-multiple-outline",
                        loading: action.running === 'run_downloader_tag',
                        onClick: _cache[96] || (_cache[96] = $event => (runAction('run_downloader_tag', '种子打标签')))
                      }, {
                        default: _withCtx(() => [...(_cache[163] || (_cache[163] = [
                          _createTextVNode(" 立即按站点打标签 ", -1)
                        ]))]),
                        _: 1
                      }, 8, ["loading"])
                    ])
                  ]),
                  _: 1
                })
              ], 512), [
                [_vShow, activeSub.value === 'dltagmain']
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
              onClick: _cache[97] || (_cache[97] = $event => (emit('close')))
            }, {
              default: _withCtx(() => [...(_cache[166] || (_cache[166] = [
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
              default: _withCtx(() => [...(_cache[167] || (_cache[167] = [
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
const Config = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-21056c3d"]]);

export { Config as default };
