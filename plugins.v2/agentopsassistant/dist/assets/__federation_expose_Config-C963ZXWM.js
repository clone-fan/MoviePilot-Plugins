import { importShared } from './__federation_fn_import-JrT3xvdd.js';
import { _ as _export_sfc, g as getPluginApi, p as postPluginApi } from './_plugin-vue_export-helper-Dc5i-DQA.js';

const {resolveComponent:_resolveComponent,createVNode:_createVNode,withCtx:_withCtx,createTextVNode:_createTextVNode,createElementVNode:_createElementVNode,renderList:_renderList,Fragment:_Fragment,openBlock:_openBlock,createElementBlock:_createElementBlock,toDisplayString:_toDisplayString,createBlock:_createBlock,normalizeClass:_normalizeClass,createCommentVNode:_createCommentVNode,unref:_unref,vShow:_vShow,withDirectives:_withDirectives,mergeProps:_mergeProps} = await importShared('vue');


const _hoisted_1 = { class: "d-flex align-center ga-2" };
const _hoisted_2 = { class: "aoa-body" };
const _hoisted_3 = { class: "aoa-nav" };
const _hoisted_4 = { class: "aoa-nav-scroll" };
const _hoisted_5 = { class: "aoa-content" };
const _hoisted_6 = { class: "aoa-subtabs" };
const _hoisted_7 = { class: "aoa-subtab-list" };
const _hoisted_8 = ["onClick"];
const _hoisted_9 = {
  key: 0,
  class: "aoa-subtab-desc"
};
const _hoisted_10 = { class: "aoa-window" };
const _hoisted_11 = { class: "aoa-pane" };
const _hoisted_12 = { class: "aoa-pane aoa-columns-pane" };
const _hoisted_13 = { class: "aoa-table-wrap" };
const _hoisted_14 = { class: "aoa-report-table-scroll" };
const _hoisted_15 = {
  class: "aoa-col-enable",
  "data-label": "启用"
};
const _hoisted_16 = { "data-label": "组件" };
const _hoisted_17 = {
  class: "aoa-table-strong",
  "data-label": "栏目"
};
const _hoisted_18 = {
  class: "aoa-table-note",
  "data-label": "备注"
};
const _hoisted_19 = { key: 0 };
const _hoisted_20 = { key: 1 };
const _hoisted_21 = { class: "aoa-pane" };
const _hoisted_22 = { class: "aoa-pane" };
const _hoisted_23 = { class: "aoa-pane" };
const _hoisted_24 = { class: "aoa-health-scope-grid" };
const _hoisted_25 = { class: "aoa-pane" };
const _hoisted_26 = { class: "aoa-pane" };
const _hoisted_27 = { class: "d-flex align-center justify-space-between mb-1" };
const _hoisted_28 = { class: "aoa-pane" };
const _hoisted_29 = { class: "aoa-pane" };
const _hoisted_30 = { class: "aoa-pane" };
const _hoisted_31 = { class: "aoa-pane" };
const _hoisted_32 = { class: "aoa-pane" };
const _hoisted_33 = { class: "aoa-pane" };
const _hoisted_34 = { class: "aoa-seed-options" };
const _hoisted_35 = { class: "aoa-pane aoa-media-pane" };
const _hoisted_36 = { class: "aoa-pane" };
const _hoisted_37 = {
  key: 0,
  class: "aoa-action-dock"
};
const _hoisted_38 = { class: "aoa-action-dock-list" };
const _hoisted_39 = { class: "aoa-action-note" };

const {reactive,ref,computed,watch,onMounted,onBeforeUnmount,defineComponent,h,resolveComponent} = await importShared('vue');


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
const activeSub = ref('overview');
const configRoot = ref(null);
let dialogScrollHost = null;

const ModuleHero = defineComponent({
  name: 'ModuleHero',
  props: {
    enabled: { type: Boolean, default: false },
    icon: { type: String, required: true },
    kicker: { type: String, required: true },
    onTitle: { type: String, required: true },
    offTitle: { type: String, default: '' },
    desc: { type: String, required: true },
    countLabel: { type: String, default: '' },
    stateOn: { type: String, default: '运行中' },
    stateOff: { type: String, default: '待启用' },
    switchLabel: { type: String, default: '启用' },
    toggle: { type: Boolean, default: true },
  },
  emits: ['update:enabled'],
  setup(props, { emit }) {
    return () => {
      const VIcon = resolveComponent('VIcon');
      const VChip = resolveComponent('VChip');
      const VSwitch = resolveComponent('VSwitch');
      const descLines = String(props.desc || '').split(/\n|\|/);
      const descChildren = [];
      descLines.forEach((line, index) => {
        if (index) descChildren.push(h('br'));
        descChildren.push(line);
      });
      return h('div', { class: ['aoa-module-hero', { 'aoa-module-hero--off': !props.enabled }] }, [
        h('div', { class: 'aoa-module-heading' }, [
          h('div', { class: 'aoa-module-emblem' }, [h(VIcon, { icon: props.icon, size: 28 })]),
          h('div', { class: 'aoa-module-heading-text' }, [
            h('div', { class: 'aoa-module-kicker' }, props.kicker),
            h('div', { class: 'aoa-module-title' }, props.enabled ? props.onTitle : (props.offTitle || props.onTitle)),
            h('div', { class: 'aoa-module-desc' }, descChildren),
          ]),
        ]),
        h('div', { class: 'aoa-module-state' }, [
          h(VChip, { size: 'small', color: props.enabled ? 'success' : 'warning', variant: 'flat' }, () => props.enabled ? props.stateOn : props.stateOff),
          props.countLabel ? h(VChip, { size: 'small', color: 'primary', variant: 'tonal' }, () => props.countLabel) : null,
          props.toggle ? h(VSwitch, {
            modelValue: props.enabled,
            'onUpdate:modelValue': value => emit('update:enabled', value),
            color: 'primary',
            inset: true,
            hideDetails: true,
            label: props.switchLabel,
          }) : null,
        ]),
      ])
    }
  },
});

const SettingSection = defineComponent({
  name: 'SettingSection',
  props: {
    title: { type: String, required: true },
    note: { type: String, default: '' },
  },
  setup(props, { slots }) {
    return () => h('section', { class: 'aoa-setting-section' }, [
      h('div', { class: 'aoa-setting-section-head' }, [
        h('div', [
          h('div', { class: 'aoa-setting-section-title' }, props.title),
          props.note ? h('div', { class: 'aoa-setting-section-note' }, props.note) : null,
        ]),
      ]),
      h('div', { class: 'aoa-setting-section-body' }, slots.default?.()),
    ])
  },
});

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

// 已安装插件（插件卸载 / 日志限定 共用）
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
  daily_report_msgtype: 'Plugin',
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
  health_check_enabled: true,
  health_check_cron: '0 */6 * * *',
  health_check_items: [],
  health_check_database_targets: ['current'],
  health_check_storage_targets: ['storages', 'config', 'download', 'library'],
  health_check_directory_targets: ['config', 'plugin', 'download', 'library'],
  health_check_storage_threshold: 85,
  health_check_notify_type: 'Plugin',
  report_health: true,
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
  log_clean_notify_type: 'Plugin',
  log_clean_onlyonce: false,
  backup_enabled: false,
  backup_onlyonce: false,
  backup_cron: '0 4 * * 1',
  backup_keep_count: 5,
  backup_path: '/config/plugins/AgentOpsAssistant/Backup',
  backup_notify: true,
  backup_notify_type: 'Plugin',
  backup_webdav_enabled: false,
  backup_webdav_notify: false,
  backup_webdav_notify_type: 'Plugin',
  backup_webdav_digest_auth: false,
  backup_webdav_disable_check: false,
  backup_webdav_hostname: '',
  backup_webdav_login: '',
  backup_webdav_password: '',
  backup_webdav_max_count: 5,
  mp_update_enabled: false,
  mp_update_cron: '0 9 * * *',
  mp_update_notify: true,
  mp_update_notify_type: 'Plugin',
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
  plugin_uninstall_remove_plugin: true,
  plugin_uninstall_clear_config: true,
  plugin_uninstall_clear_data: true,
  plugin_uninstall_delete_source: false,
  plugin_uninstall_notify: true,
  plugin_uninstall_notify_type: 'Plugin',
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
  seedclean_notify_type: 'Plugin',
  subfill_enabled: false,
  subfill_details: [],
  subfill_notify: false,
  subfill_notify_type: 'Plugin',
  subfill_category_enabled: false,
  subfill_category_confs: '',
  msgnotify_enabled: false,
  msgnotify_types: [],
  msgnotify_servers: [],
  msgnotify_notify_type: 'MediaServer',
  dltag_enabled: false,
  dltag_downloaders: [],
  dltag_prefix: '',
  dltag_notify: true,
  dltag_notify_type: 'Plugin',
};

const mainTabs = [
  { key: 'report', group: '汇报中心', title: '每日汇报', icon: 'mdi-newspaper-variant-outline', desc: '日报发送、手动推送与栏目控制' },
  { key: 'subreminder', group: '订阅与站点', title: '订阅管理', icon: 'mdi-bell-cog-outline', desc: '订阅追新与规则填充' },
  { key: 'sitestat', group: '订阅与站点', title: '站点数据统计', icon: 'mdi-chart-line', desc: '仪表盘站点数据与日报栏目' },
  { key: 'seedclean', group: '下载与媒体', title: '下载器管理', icon: 'mdi-download-network-outline', desc: '自动删种、种子标签与下载器治理' },
  { key: 'msgnotify', group: '下载与媒体', title: '媒体通知', icon: 'mdi-television-play', desc: '媒体服务器 webhook 事件通知' },
  { key: 'healthcheck', group: '系统维护', title: '健康巡查', icon: 'mdi-heart-pulse', desc: '数据库、存储、目录健康检查' },
  { key: 'backup', group: '系统维护', title: '自动备份', icon: 'mdi-archive-arrow-up-outline', desc: '本地与 WebDAV 备份' },
  { key: 'cleanup', group: '系统维护', title: '日志清理', icon: 'mdi-file-document-remove-outline', desc: '插件日志保留与清理通知' },
  { key: 'updates', group: '系统维护', title: '更新检查', icon: 'mdi-update', desc: 'MoviePilot 与插件库更新' },
  { key: 'plugin', group: '系统维护', title: '插件卸载', icon: 'mdi-puzzle-remove-outline', desc: '卸载插件并清理残留' },
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
    { key: 'overview', title: '汇报总览', icon: 'mdi-newspaper-variant-outline' },
    { key: 'columns', title: '汇报栏目', icon: 'mdi-view-column-outline' },
  ],
  subreminder: [
    { key: 'subscribe', title: '订阅追新', icon: 'mdi-bell-ring-outline' },
    { key: 'subfill', title: '订阅规则填充', icon: 'mdi-auto-fix' },
  ],
  sitestat: [
    { key: 'sites', title: '站点数据统计', icon: 'mdi-chart-line' },
  ],
  healthcheck: [
    { key: 'hc', title: '健康巡查', icon: 'mdi-heart-pulse' },
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
    { key: 'clean', title: '卸载清理', icon: 'mdi-puzzle-remove-outline' },
  ],
  seedclean: [
    { key: 'seedremove', title: '自动删种', icon: 'mdi-delete-sweep-outline' },
    { key: 'dltagmain', title: '批量打标签', icon: 'mdi-tag-multiple-outline' },
  ],
  msgnotify: [
    { key: 'server', title: '服务器通知', icon: 'mdi-television-play' },
  ],
};

const subscribeSubtypeItems = [{ title: '电影', value: 'movie' }, { title: '电视剧', value: 'tv' }];
const notificationTypeItems = [
  { title: '插件', value: 'Plugin' },
  { title: '其他', value: 'Other' },
  { title: '手动处理', value: 'Manual' },
  { title: '订阅', value: 'Subscribe' },
  { title: '资源下载', value: 'Download' },
  { title: '整理入库', value: 'Organize' },
  { title: '站点', value: 'SiteMessage' },
  { title: '媒体服务器', value: 'MediaServer' },
  { title: '智能体', value: 'Agent' },
];
const messageTypeItems = [
  { title: '订阅', value: 'Subscribe' },
  { title: '插件', value: 'Plugin' },
  { title: '其他', value: 'Other' },
  { title: '手动处理', value: 'Manual' },
  { title: '资源下载', value: 'Download' },
  { title: '整理入库', value: 'Organize' },
  { title: '站点', value: 'SiteMessage' },
  { title: '媒体服务器', value: 'MediaServer' },
  { title: '智能体', value: 'Agent' },
];
const siteStatRangeItems = [{ title: '今日数据', value: 'today' }, { title: '汇总数据', value: 'total' }, { title: '所有数据', value: 'all' }];
const siteNotifyItems = [{ title: '增量变化', value: 'inc' }, { title: '全部数据', value: 'all' }, { title: '不通知', value: 'none' }];
const marketNotifyItems = notificationTypeItems;
const mpUpdateTypes = ['后端', '前端'].map(v => ({ title: v, value: v }));
const keepCountPresets = [3, 5, 7, 10, 15].map(v => ({ title: `保留 ${v} 份`, value: v }));
const logRowsPresets = [100, 300, 500, 1000, 2000].map(v => ({ title: `保留 ${v} 行`, value: v }));
const intervalPresets = [3600, 21600, 43200, 86400, 604800].map(v => ({ title: v < 86400 ? `${v / 3600} 小时` : `${v / 86400} 天`, value: v }));
const seedActionItems = [{ title: '暂停', value: 'pause' }, { title: '删除种子', value: 'delete' }, { title: '删除种子和文件', value: 'deletefile' }];
const subfillDetailItems = ['分辨率', '资源质量', '特效', '制作组', '站点'].map(v => ({ title: v, value: v }));
const msgGroupItems = ['新入库', '开始播放', '停止播放', '登录成功', '登录失败', '标记'].map(v => ({ title: v, value: v }));
const healthCheckItems = [
  { title: '数据库', value: '数据库', icon: 'mdi-database-check-outline', desc: '连接与基础读写状态' },
  { title: '存储空间', value: '存储空间', icon: 'mdi-harddisk', desc: '下载与媒体库容量余量' },
  { title: '目录权限', value: '目录权限', icon: 'mdi-folder-key-outline', desc: '关键路径可访问性' },
];
const healthDatabaseTargets = [
  { title: '当前主库', value: 'current' },
  { title: 'SQLite 配置库', value: 'sqlite' },
  { title: 'PostgreSQL 主库', value: 'postgresql' },
];
const healthStorageTargets = [
  { title: 'MoviePilot 存储配置', value: 'storages' },
  { title: '配置目录', value: 'config' },
  { title: '下载目录', value: 'download' },
  { title: '媒体库目录', value: 'library' },
];
const healthDirectoryTargets = [
  { title: '配置目录', value: 'config' },
  { title: '插件目录', value: 'plugin' },
  { title: '下载目录', value: 'download' },
  { title: '媒体库目录', value: 'library' },
];
const healthChipLabels = {
  数据库: '数据库',
  存储空间: '存储',
  目录权限: '目录',
  current: '当前主库',
  sqlite: 'SQLite',
  postgresql: 'PG 主库',
  storages: '存储配置',
  config: '配置目录',
  plugin: '插件目录',
  download: '下载目录',
  library: '媒体库',
};
const reportSections = [
  { key: 'report_version', label: 'MoviePilot 版本', component: '每日汇报', requires: null, note: '基础版本信息' },
  { key: 'report_site_status', label: '站点状态', component: '站点数据统计', requires: null, note: '逐站状态' },
  { key: 'report_site_increment', label: '站点增量', component: '站点数据统计', requires: 'site_stat', note: '上传 / 下载 / 分享率 / 魔力' },
  { key: 'report_today_download', label: '今日下载', component: '下载入库', requires: null, note: '今日已下载入库明细' },
  { key: 'report_transfer', label: '入库整理', component: '下载入库', requires: null, note: '今日入库成功 / 失败' },
  { key: 'report_subscribe', label: '订阅追新', component: '订阅追新', requires: 'subscribe_reminder', note: '今日追新内容' },
  { key: 'report_storage', label: '存储空间', component: '存储空间', requires: null, note: '下载 / 媒体库目录用量' },
  { key: 'report_media_stat', label: '媒体统计', component: '媒体库', requires: null, note: '电影 / 剧集 / 用户统计' },
  { key: 'report_health', label: '健康巡查', component: '健康巡查', requires: 'health_check', note: '最近一次健康巡查结果' },
  { key: 'report_summary', label: '今日摘要', component: '每日汇报', requires: null, note: '前文摘要' },
];

const currentMain = computed(() => mainTabs.find(item => item.key === activeMain.value) || mainTabs[0]);
const currentSubs = computed(() => subTabs[activeMain.value] || []);
const activeActionItems = computed(() => {
  const actions = {
    overview: [
      { path: 'run_daily_report', label: '立即发送汇报', icon: 'mdi-send-outline', note: '按当前设置发送一次完整日报' },
      { path: 'run_health_check', label: '立即健康巡查', icon: 'mdi-heart-pulse', note: '顺手刷新日报里的健康巡查结果' },
    ],
    subscribe: [
      { path: 'run_subscribe_reminder', label: '立即推送订阅追新', icon: 'mdi-bell-ring-outline', note: '按当前设置推送今日订阅追新' },
    ],
    sites: [
      { path: 'run_site_stat', label: '立即统计', icon: 'mdi-chart-line', note: '刷新站点数据与仪表盘统计' },
    ],
    hc: [
      { path: 'run_health_check', label: '立即巡查', icon: 'mdi-heart-pulse', note: '按当前范围检查系统健康' },
    ],
    subfill: [
      { path: 'subfill_clear_history', label: '清理历史记录', icon: 'mdi-history', note: '清理订阅规则填充历史' },
      { path: 'subfill_clear_handled', label: '清理已处理记录', icon: 'mdi-backup-restore', note: '让已处理剧集下次重新尝试填充', color: 'warning' },
    ],
    local: [
      { path: 'run_backup', label: '立即备份', icon: 'mdi-archive-arrow-up-outline', note: '按当前本地配置备份一次' },
    ],
    logs: [
      { path: 'run_log_clean', label: '立即清理', icon: 'mdi-broom', note: '按当前保留行数裁剪插件日志' },
    ],
    mp: [
      { path: 'run_mp_update', label: '检查更新', icon: 'mdi-update', note: '仅检查 MoviePilot 主程序版本' },
    ],
    market: [
      { path: 'run_market_update', label: '立即检查', icon: 'mdi-cloud-sync-outline', note: '检查插件库并处理已安装插件更新' },
    ],
    clean: [
      {
        path: 'run_plugin_uninstall',
        label: '执行卸载',
        icon: 'mdi-puzzle-remove-outline',
        note: '不可逆操作，执行前确认插件和清理范围',
        color: 'error',
        disabled: !form.plugin_uninstall_ids || !form.plugin_uninstall_ids.length,
      },
    ],
    seedremove: [
      {
        path: 'run_seed_clean',
        label: '立即执行',
        icon: 'mdi-delete-sweep-outline',
        note: '按当前条件处理种子，建议先暂停验证命中',
        color: 'error',
        disabled: !form.seedclean_downloaders || !form.seedclean_downloaders.length,
      },
    ],
    dltagmain: [
      { path: 'run_downloader_tag', label: '立即打标签', icon: 'mdi-tag-multiple-outline', note: '按 tracker 站点为种子补标签' },
    ],
  };
  return actions[activeSub.value] || []
});
const healthSelectedCount = computed(() => {
  const selected = Array.isArray(form.health_check_items) ? form.health_check_items : [];
  return selected.length || healthCheckItems.length
});
const reportEnabledCount = computed(() => reportSections.filter(item => form[item.key]).length);
const seedFilterCount = computed(() => [
  form.seedclean_size,
  form.seedclean_ratio,
  form.seedclean_time,
  form.seedclean_upspeed,
  form.seedclean_labels,
  form.seedclean_torrentcategorys,
  form.seedclean_pathkeywords,
  form.seedclean_trackerkeywords,
  form.seedclean_torrentstates,
  form.seedclean_errorkeywords,
].filter(Boolean).length);

function selectionValue(item) {
  return item?.raw?.value ?? item?.value ?? item?.props?.value ?? item
}

function selectionTitle(item) {
  const value = selectionValue(item);
  const title = healthChipLabels[value] || item?.props?.title || item?.raw?.title || item?.title || value;
  return String(title || '')
}

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
  form.health_check_items = toArr(form.health_check_items);
  form.health_check_database_targets = toArr(form.health_check_database_targets);
  form.health_check_storage_targets = toArr(form.health_check_storage_targets);
  form.health_check_directory_targets = toArr(form.health_check_directory_targets);
}, { immediate: true, deep: true });

function saveConfig() {
  emit('save', { ...form });
}

function selectMain(key) {
  if (activeMain.value === key) return
  activeMain.value = key;
  activeSub.value = subTabs[key]?.[0]?.key || '';
}

function bindDialogScrollHost() {
  const host = configRoot.value?.closest?.('.v-card-text.pa-0');
  if (!host || host === dialogScrollHost) return
  dialogScrollHost?.classList.remove('aoa-config-scroll-host');
  dialogScrollHost = host;
  dialogScrollHost.classList.add('aoa-config-scroll-host');
}

onMounted(() => {
  bindDialogScrollHost();
  loadInstalledPlugins();
  loadPluginMarkets();
  loadDownloaders();
  loadMediaservers();
});

onBeforeUnmount(() => {
  dialogScrollHost?.classList.remove('aoa-config-scroll-host');
  dialogScrollHost = null;
});

return (_ctx, _cache) => {
  const _component_VIcon = _resolveComponent("VIcon");
  const _component_VAvatar = _resolveComponent("VAvatar");
  const _component_VCardTitle = _resolveComponent("VCardTitle");
  const _component_VCardSubtitle = _resolveComponent("VCardSubtitle");
  const _component_VSwitch = _resolveComponent("VSwitch");
  const _component_VBtn = _resolveComponent("VBtn");
  const _component_VCardItem = _resolveComponent("VCardItem");
  const _component_VDivider = _resolveComponent("VDivider");
  const _component_VListSubheader = _resolveComponent("VListSubheader");
  const _component_VListItemTitle = _resolveComponent("VListItemTitle");
  const _component_VListItem = _resolveComponent("VListItem");
  const _component_VList = _resolveComponent("VList");
  const _component_VCronField = _resolveComponent("VCronField");
  const _component_VCol = _resolveComponent("VCol");
  const _component_VSelect = _resolveComponent("VSelect");
  const _component_VTextField = _resolveComponent("VTextField");
  const _component_VRow = _resolveComponent("VRow");
  const _component_VForm = _resolveComponent("VForm");
  const _component_VCheckbox = _resolveComponent("VCheckbox");
  const _component_VChip = _resolveComponent("VChip");
  const _component_VTable = _resolveComponent("VTable");
  const _component_VTextarea = _resolveComponent("VTextarea");
  const _component_VSlider = _resolveComponent("VSlider");
  const _component_VExpansionPanelText = _resolveComponent("VExpansionPanelText");
  const _component_VExpansionPanel = _resolveComponent("VExpansionPanel");
  const _component_VExpansionPanels = _resolveComponent("VExpansionPanels");
  const _component_VFadeTransition = _resolveComponent("VFadeTransition");
  const _component_VSpacer = _resolveComponent("VSpacer");
  const _component_VCardActions = _resolveComponent("VCardActions");
  const _component_VCard = _resolveComponent("VCard");

  return (_openBlock(), _createElementBlock("div", {
    ref_key: "configRoot",
    ref: configRoot,
    class: "aoa-config"
  }, [
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
            _createElementVNode("div", _hoisted_1, [
              _createVNode(_component_VSwitch, {
                modelValue: form.enabled,
                "onUpdate:modelValue": _cache[0] || (_cache[0] = $event => ((form.enabled) = $event)),
                color: "primary",
                "hide-details": "",
                inset: "",
                label: form.enabled ? '已启用' : '已停用'
              }, null, 8, ["modelValue", "label"]),
              _createVNode(_component_VBtn, {
                size: "small",
                variant: "text",
                color: "primary",
                "prepend-icon": "mdi-view-dashboard-outline",
                class: "text-none aoa-header-link",
                onClick: _cache[1] || (_cache[1] = $event => (emit('switch')))
              }, {
                default: _withCtx(() => [...(_cache[110] || (_cache[110] = [
                  _createTextVNode(" 仪表盘 ", -1)
                ]))]),
                _: 1
              }),
              _createVNode(_component_VBtn, {
                icon: "mdi-close",
                variant: "text",
                onClick: _cache[2] || (_cache[2] = $event => (emit('close')))
              })
            ])
          ]),
          default: _withCtx(() => [
            _createVNode(_component_VCardTitle, { class: "text-h6 aoa-header-title" }, {
              default: _withCtx(() => [...(_cache[108] || (_cache[108] = [
                _createTextVNode("MP 运维助手", -1)
              ]))]),
              _: 1
            }),
            _createVNode(_component_VCardSubtitle, { class: "text-caption aoa-header-subtitle" }, {
              default: _withCtx(() => [...(_cache[109] || (_cache[109] = [
                _createTextVNode("配置中心", -1)
              ]))]),
              _: 1
            })
          ]),
          _: 1
        }),
        _createVNode(_component_VDivider, { class: "aoa-hairline" }),
        _createElementVNode("div", _hoisted_2, [
          _createElementVNode("nav", _hoisted_3, [
            _createElementVNode("div", _hoisted_4, [
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
                              icon: item.icon,
                              class: "aoa-nav-icon"
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
            ])
          ]),
          _createElementVNode("section", _hoisted_5, [
            _createElementVNode("div", _hoisted_6, [
              _createElementVNode("div", _hoisted_7, [
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
                  ], 10, _hoisted_8))
                }), 128))
              ]),
              (currentMain.value.desc)
                ? (_openBlock(), _createElementBlock("div", _hoisted_9, _toDisplayString(currentMain.value.desc), 1))
                : _createCommentVNode("", true)
            ]),
            _createVNode(_component_VDivider, { class: "aoa-hairline" }),
            _createElementVNode("div", _hoisted_10, [
              _withDirectives(_createElementVNode("div", _hoisted_11, [
                _createVNode(_component_VForm, null, {
                  default: _withCtx(() => [
                    _createVNode(_unref(ModuleHero), {
                      enabled: form.daily_report_enabled,
                      "onUpdate:enabled": _cache[3] || (_cache[3] = $event => ((form.daily_report_enabled) = $event)),
                      icon: "mdi-newspaper-variant-outline",
                      kicker: "MP 每日汇报",
                      "on-title": "定时汇报已启用",
                      "off-title": "定时汇报未启用",
                      desc: "按计划聚合站点、订阅与入库|同步整理存储与健康信息",
                      "count-label": `${reportEnabledCount.value} 个栏目`
                    }, null, 8, ["enabled", "count-label"]),
                    _createVNode(_unref(SettingSection), {
                      title: "汇报设置",
                      note: "发送时间、消息渠道与称呼集中配置"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_VRow, { class: "aoa-setting-grid" }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VCol, {
                              cols: "12",
                              md: "6"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_VCronField, {
                                  modelValue: form.daily_report_cron,
                                  "onUpdate:modelValue": _cache[4] || (_cache[4] = $event => ((form.daily_report_cron) = $event)),
                                  label: "汇报时间 (Cron)",
                                  disabled: !form.daily_report_enabled
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
                                  modelValue: form.daily_report_msgtype,
                                  "onUpdate:modelValue": _cache[5] || (_cache[5] = $event => ((form.daily_report_msgtype) = $event)),
                                  items: notificationTypeItems,
                                  label: "消息类型",
                                  disabled: !form.daily_report_enabled
                                }, null, 8, ["modelValue", "disabled"])
                              ]),
                              _: 1
                            }),
                            _createVNode(_component_VCol, { cols: "12" }, {
                              default: _withCtx(() => [
                                _createVNode(_component_VTextField, {
                                  modelValue: form.daily_report_greeting,
                                  "onUpdate:modelValue": _cache[6] || (_cache[6] = $event => ((form.daily_report_greeting) = $event)),
                                  label: "汇报称呼",
                                  placeholder: "少爷",
                                  "prepend-inner-icon": "mdi-account-heart-outline",
                                  "persistent-hint": "",
                                  hint: "汇报开头与提醒中对你的称呼，留空默认“少爷”",
                                  clearable: "",
                                  disabled: !form.daily_report_enabled
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
              ], 512), [
                [_vShow, activeSub.value === 'overview']
              ]),
              _withDirectives(_createElementVNode("div", _hoisted_12, [
                _createVNode(_component_VForm, { class: "aoa-columns-form" }, {
                  default: _withCtx(() => [
                    _createVNode(_unref(ModuleHero), {
                      enabled: reportEnabledCount.value > 0,
                      icon: "mdi-view-column-outline",
                      kicker: "MP 每日汇报",
                      "on-title": "日报栏目已编排",
                      "off-title": "日报栏目未启用",
                      desc: "统一控制并入日报的内容|组件状态会同步提示",
                      "count-label": `${reportEnabledCount.value} / ${reportSections.length} 个栏目`,
                      "state-on": "已配置",
                      "state-off": "待配置",
                      toggle: false
                    }, null, 8, ["enabled", "count-label"]),
                    _createVNode(_unref(SettingSection), {
                      title: "汇报栏目",
                      note: "勾选决定日报展示的完整栏目，对应组件未启用时自动提示"
                    }, {
                      default: _withCtx(() => [
                        _createElementVNode("div", _hoisted_13, [
                          _createElementVNode("div", _hoisted_14, [
                            _createVNode(_component_VTable, { class: "aoa-report-table" }, {
                              default: _withCtx(() => [
                                _cache[111] || (_cache[111] = _createElementVNode("thead", null, [
                                  _createElementVNode("tr", null, [
                                    _createElementVNode("th", {
                                      scope: "col",
                                      class: "aoa-col-enable"
                                    }, "启用"),
                                    _createElementVNode("th", { scope: "col" }, "组件"),
                                    _createElementVNode("th", { scope: "col" }, "日报栏目"),
                                    _createElementVNode("th", { scope: "col" }, "备注")
                                  ])
                                ], -1)),
                                _createElementVNode("tbody", null, [
                                  (_openBlock(), _createElementBlock(_Fragment, null, _renderList(reportSections, (s) => {
                                    return _createElementVNode("tr", {
                                      key: s.key
                                    }, [
                                      _createElementVNode("td", _hoisted_15, [
                                        _createVNode(_component_VCheckbox, {
                                          modelValue: form[s.key],
                                          "onUpdate:modelValue": $event => ((form[s.key]) = $event),
                                          color: "primary",
                                          "hide-details": "",
                                          density: "compact",
                                          disabled: s.requires && !form[`${s.requires}_enabled`]
                                        }, null, 8, ["modelValue", "onUpdate:modelValue", "disabled"])
                                      ]),
                                      _createElementVNode("td", _hoisted_16, [
                                        _createVNode(_component_VChip, {
                                          size: "small",
                                          variant: "tonal",
                                          color: "primary"
                                        }, {
                                          default: _withCtx(() => [
                                            _createTextVNode(_toDisplayString(s.component), 1)
                                          ]),
                                          _: 2
                                        }, 1024)
                                      ]),
                                      _createElementVNode("td", _hoisted_17, _toDisplayString(s.label), 1),
                                      _createElementVNode("td", _hoisted_18, [
                                        (s.requires && !form[`${s.requires}_enabled`])
                                          ? (_openBlock(), _createElementBlock("span", _hoisted_19, "需启用对应组件"))
                                          : (_openBlock(), _createElementBlock("span", _hoisted_20, _toDisplayString(s.note), 1))
                                      ])
                                    ])
                                  }), 64))
                                ])
                              ]),
                              _: 1
                            })
                          ])
                        ])
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                })
              ], 512), [
                [_vShow, activeSub.value === 'columns']
              ]),
              _withDirectives(_createElementVNode("div", _hoisted_21, [
                _createVNode(_component_VForm, null, {
                  default: _withCtx(() => [
                    _createVNode(_unref(ModuleHero), {
                      enabled: form.subscribe_reminder_enabled,
                      "onUpdate:enabled": _cache[7] || (_cache[7] = $event => ((form.subscribe_reminder_enabled) = $event)),
                      icon: "mdi-bell-ring-outline",
                      kicker: "MP 订阅管理",
                      "on-title": "订阅追新已启用",
                      "off-title": "订阅追新未启用",
                      desc: "按计划推送今日订阅追新|日报展示由汇报栏目控制",
                      "count-label": `${form.subscribe_reminder_subtype?.length || 0} 类提醒`
                    }, null, 8, ["enabled", "count-label"]),
                    _createVNode(_unref(SettingSection), {
                      title: "追新设置",
                      note: "推送时间、订阅类型与消息渠道集中配置"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_VRow, { class: "aoa-setting-grid" }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VCol, {
                              cols: "12",
                              md: "4"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_VCronField, {
                                  modelValue: form.subscribe_reminder_cron,
                                  "onUpdate:modelValue": _cache[8] || (_cache[8] = $event => ((form.subscribe_reminder_cron) = $event)),
                                  label: "推送时间 (Cron)",
                                  disabled: !form.subscribe_reminder_enabled
                                }, null, 8, ["modelValue", "disabled"])
                              ]),
                              _: 1
                            }),
                            _createVNode(_component_VCol, {
                              cols: "12",
                              md: "5"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_VSelect, {
                                  modelValue: form.subscribe_reminder_subtype,
                                  "onUpdate:modelValue": _cache[9] || (_cache[9] = $event => ((form.subscribe_reminder_subtype) = $event)),
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
                              md: "3"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_VSelect, {
                                  modelValue: form.subscribe_reminder_msgtype,
                                  "onUpdate:modelValue": _cache[10] || (_cache[10] = $event => ((form.subscribe_reminder_msgtype) = $event)),
                                  items: messageTypeItems,
                                  label: "消息类型",
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
                  ]),
                  _: 1
                })
              ], 512), [
                [_vShow, activeSub.value === 'subscribe']
              ]),
              _withDirectives(_createElementVNode("div", _hoisted_22, [
                _createVNode(_component_VForm, null, {
                  default: _withCtx(() => [
                    _createVNode(_unref(ModuleHero), {
                      enabled: form.site_stat_enabled,
                      "onUpdate:enabled": _cache[11] || (_cache[11] = $event => ((form.site_stat_enabled) = $event)),
                      icon: "mdi-chart-line",
                      kicker: "MP 站点统计",
                      "on-title": "站点数据采集已启用",
                      "off-title": "站点数据采集未启用",
                      desc: "为仪表盘和日报提供站点状态|统计上传下载增量与趋势",
                      "count-label": form.site_stat_dashboard_type === 'today' ? '今日数据' : '统计数据'
                    }, null, 8, ["enabled", "count-label"]),
                    _createVNode(_unref(SettingSection), {
                      title: "统计设置",
                      note: "控制仪表盘站点数据口径与通知方式"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_VRow, { class: "aoa-setting-grid" }, {
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
                  ]),
                  _: 1
                })
              ], 512), [
                [_vShow, activeSub.value === 'sites']
              ]),
              _withDirectives(_createElementVNode("div", _hoisted_23, [
                _createVNode(_component_VForm, { class: "aoa-health-form" }, {
                  default: _withCtx(() => [
                    _createVNode(_unref(ModuleHero), {
                      enabled: form.health_check_enabled,
                      "onUpdate:enabled": _cache[14] || (_cache[14] = $event => ((form.health_check_enabled) = $event)),
                      icon: "mdi-heart-pulse",
                      kicker: "MP 健康巡查",
                      "on-title": "自动巡查已启用",
                      "off-title": "自动巡查未启用",
                      desc: "数据库、存储空间、目录权限|按计划检查，异常进入通知链路",
                      "count-label": `${healthSelectedCount.value} 项巡查`
                    }, null, 8, ["enabled", "count-label"]),
                    _createVNode(_unref(SettingSection), {
                      title: "巡查设置",
                      note: "项目、时间、数据库、存储、目录和容量阈值集中配置"
                    }, {
                      default: _withCtx(() => [
                        _createElementVNode("div", _hoisted_24, [
                          _createVNode(_component_VCronField, {
                            modelValue: form.health_check_cron,
                            "onUpdate:modelValue": _cache[15] || (_cache[15] = $event => ((form.health_check_cron) = $event)),
                            label: "巡查时间 (Cron)",
                            class: "aoa-health-field-third",
                            disabled: !form.health_check_enabled
                          }, null, 8, ["modelValue", "disabled"]),
                          _createVNode(_component_VTextField, {
                            modelValue: form.health_check_storage_threshold,
                            "onUpdate:modelValue": _cache[16] || (_cache[16] = $event => ((form.health_check_storage_threshold) = $event)),
                            modelModifiers: { number: true },
                            label: "容量阈值",
                            type: "number",
                            class: "aoa-health-field-third",
                            min: "1",
                            max: "99",
                            suffix: "%",
                            disabled: !form.health_check_enabled
                          }, null, 8, ["modelValue", "disabled"]),
                          _createVNode(_component_VSelect, {
                            modelValue: form.health_check_notify_type,
                            "onUpdate:modelValue": _cache[17] || (_cache[17] = $event => ((form.health_check_notify_type) = $event)),
                            items: notificationTypeItems,
                            label: "异常通知渠道",
                            class: "aoa-health-field-third",
                            disabled: !form.health_check_enabled
                          }, null, 8, ["modelValue", "disabled"]),
                          _createVNode(_component_VSelect, {
                            modelValue: form.health_check_items,
                            "onUpdate:modelValue": _cache[18] || (_cache[18] = $event => ((form.health_check_items) = $event)),
                            items: healthCheckItems,
                            class: "aoa-health-field-full aoa-health-select",
                            label: "巡查项目",
                            multiple: "",
                            chips: "",
                            "closable-chips": "",
                            clearable: "",
                            disabled: !form.health_check_enabled
                          }, {
                            chip: _withCtx(({ item, props }) => [
                              _createVNode(_component_VChip, _mergeProps(props, {
                                class: "aoa-health-selection-chip",
                                variant: "tonal"
                              }), {
                                default: _withCtx(() => [
                                  _createTextVNode(_toDisplayString(selectionTitle(item)), 1)
                                ]),
                                _: 2
                              }, 1040)
                            ]),
                            _: 1
                          }, 8, ["modelValue", "disabled"]),
                          _createVNode(_component_VSelect, {
                            modelValue: form.health_check_database_targets,
                            "onUpdate:modelValue": _cache[19] || (_cache[19] = $event => ((form.health_check_database_targets) = $event)),
                            items: healthDatabaseTargets,
                            class: "aoa-health-field-full aoa-health-select",
                            label: "数据库",
                            multiple: "",
                            chips: "",
                            "closable-chips": "",
                            clearable: "",
                            disabled: !form.health_check_enabled
                          }, {
                            chip: _withCtx(({ item, props }) => [
                              _createVNode(_component_VChip, _mergeProps(props, {
                                class: "aoa-health-selection-chip",
                                variant: "tonal"
                              }), {
                                default: _withCtx(() => [
                                  _createTextVNode(_toDisplayString(selectionTitle(item)), 1)
                                ]),
                                _: 2
                              }, 1040)
                            ]),
                            _: 1
                          }, 8, ["modelValue", "disabled"]),
                          _createVNode(_component_VSelect, {
                            modelValue: form.health_check_storage_targets,
                            "onUpdate:modelValue": _cache[20] || (_cache[20] = $event => ((form.health_check_storage_targets) = $event)),
                            items: healthStorageTargets,
                            class: "aoa-health-field-full aoa-health-select",
                            label: "存储空间",
                            multiple: "",
                            chips: "",
                            "closable-chips": "",
                            clearable: "",
                            disabled: !form.health_check_enabled
                          }, {
                            chip: _withCtx(({ item, props }) => [
                              _createVNode(_component_VChip, _mergeProps(props, {
                                class: "aoa-health-selection-chip",
                                variant: "tonal"
                              }), {
                                default: _withCtx(() => [
                                  _createTextVNode(_toDisplayString(selectionTitle(item)), 1)
                                ]),
                                _: 2
                              }, 1040)
                            ]),
                            _: 1
                          }, 8, ["modelValue", "disabled"]),
                          _createVNode(_component_VSelect, {
                            modelValue: form.health_check_directory_targets,
                            "onUpdate:modelValue": _cache[21] || (_cache[21] = $event => ((form.health_check_directory_targets) = $event)),
                            items: healthDirectoryTargets,
                            class: "aoa-health-field-full aoa-health-select",
                            label: "目录权限",
                            multiple: "",
                            chips: "",
                            "closable-chips": "",
                            clearable: "",
                            disabled: !form.health_check_enabled
                          }, {
                            chip: _withCtx(({ item, props }) => [
                              _createVNode(_component_VChip, _mergeProps(props, {
                                class: "aoa-health-selection-chip",
                                variant: "tonal"
                              }), {
                                default: _withCtx(() => [
                                  _createTextVNode(_toDisplayString(selectionTitle(item)), 1)
                                ]),
                                _: 2
                              }, 1040)
                            ]),
                            _: 1
                          }, 8, ["modelValue", "disabled"])
                        ])
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                })
              ], 512), [
                [_vShow, activeSub.value === 'hc']
              ]),
              _withDirectives(_createElementVNode("div", _hoisted_25, [
                _createVNode(_component_VForm, null, {
                  default: _withCtx(() => [
                    _createVNode(_unref(ModuleHero), {
                      enabled: form.subfill_enabled,
                      "onUpdate:enabled": _cache[22] || (_cache[22] = $event => ((form.subfill_enabled) = $event)),
                      icon: "mdi-auto-fix",
                      kicker: "MP 订阅管理",
                      "on-title": "订阅规则填充已启用",
                      "off-title": "订阅规则填充未启用",
                      desc: "用已下载资源规格回填订阅规则|锁定后续剧集追同款版本",
                      "count-label": `${form.subfill_details?.length || 0} 项填充`
                    }, null, 8, ["enabled", "count-label"]),
                    _createVNode(_unref(SettingSection), {
                      title: "规则填充",
                      note: "选择自动填充范围，并配置完成后的通知渠道"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_VRow, { class: "aoa-setting-grid" }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VCol, {
                              cols: "12",
                              md: "6"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_VSwitch, {
                                  modelValue: form.subfill_notify,
                                  "onUpdate:modelValue": _cache[23] || (_cache[23] = $event => ((form.subfill_notify) = $event)),
                                  color: "primary",
                                  inset: "",
                                  "hide-details": "",
                                  label: "填充后发送通知",
                                  disabled: !form.subfill_enabled
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
                                  modelValue: form.subfill_notify_type,
                                  "onUpdate:modelValue": _cache[24] || (_cache[24] = $event => ((form.subfill_notify_type) = $event)),
                                  items: notificationTypeItems,
                                  label: "消息类型",
                                  disabled: !form.subfill_enabled || !form.subfill_notify
                                }, null, 8, ["modelValue", "disabled"])
                              ]),
                              _: 1
                            }),
                            _createVNode(_component_VCol, { cols: "12" }, {
                              default: _withCtx(() => [
                                _createVNode(_component_VSelect, {
                                  modelValue: form.subfill_details,
                                  "onUpdate:modelValue": _cache[25] || (_cache[25] = $event => ((form.subfill_details) = $event)),
                                  items: _unref(subfillDetailItems),
                                  label: "自动填充哪些规则",
                                  multiple: "",
                                  chips: "",
                                  "closable-chips": "",
                                  clearable: "",
                                  "prepend-inner-icon": "mdi-auto-fix",
                                  disabled: !form.subfill_enabled
                                }, null, 8, ["modelValue", "items", "disabled"])
                              ]),
                              _: 1
                            })
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    _createVNode(_unref(SettingSection), {
                      title: "二级分类自定义填充",
                      note: "每行一个分类，用 # 分隔字段"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_VRow, { class: "aoa-setting-grid" }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VCol, {
                              cols: "12",
                              md: "6"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_VSwitch, {
                                  modelValue: form.subfill_category_enabled,
                                  "onUpdate:modelValue": _cache[26] || (_cache[26] = $event => ((form.subfill_category_enabled) = $event)),
                                  color: "primary",
                                  inset: "",
                                  "hide-details": "",
                                  label: "启用二级分类自定义填充"
                                }, null, 8, ["modelValue"])
                              ]),
                              _: 1
                            }),
                            _createVNode(_component_VCol, { cols: "12" }, {
                              default: _withCtx(() => [
                                _createVNode(_component_VTextarea, {
                                  modelValue: form.subfill_category_confs,
                                  "onUpdate:modelValue": _cache[27] || (_cache[27] = $event => ((form.subfill_category_confs) = $event)),
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
                        })
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                })
              ], 512), [
                [_vShow, activeSub.value === 'subfill']
              ]),
              _withDirectives(_createElementVNode("div", _hoisted_26, [
                _createVNode(_component_VForm, null, {
                  default: _withCtx(() => [
                    _createVNode(_unref(ModuleHero), {
                      enabled: form.backup_enabled,
                      "onUpdate:enabled": _cache[28] || (_cache[28] = $event => ((form.backup_enabled) = $event)),
                      icon: "mdi-folder-arrow-up-outline",
                      kicker: "MP 自动备份",
                      "on-title": "本地备份已启用",
                      "off-title": "本地备份未启用",
                      desc: "按计划打包配置和关键数据|保留最近备份版本",
                      "count-label": `${form.backup_keep_count} 份保留`
                    }, null, 8, ["enabled", "count-label"]),
                    _createVNode(_unref(SettingSection), {
                      title: "本地策略",
                      note: "备份时间、路径和保留份数集中配置"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_VRow, { class: "aoa-setting-grid" }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VCol, {
                              cols: "12",
                              md: "6"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_VCronField, {
                                  modelValue: form.backup_cron,
                                  "onUpdate:modelValue": _cache[29] || (_cache[29] = $event => ((form.backup_cron) = $event)),
                                  label: "备份时间 (Cron)",
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
                                _createVNode(_component_VTextField, {
                                  modelValue: form.backup_path,
                                  "onUpdate:modelValue": _cache[30] || (_cache[30] = $event => ((form.backup_path) = $event)),
                                  label: "本地备份路径",
                                  "prepend-inner-icon": "mdi-folder-outline",
                                  disabled: !form.backup_enabled
                                }, null, 8, ["modelValue", "disabled"])
                              ]),
                              _: 1
                            }),
                            _createVNode(_component_VCol, { cols: "12" }, {
                              default: _withCtx(() => [
                                _createElementVNode("div", _hoisted_27, [
                                  _cache[112] || (_cache[112] = _createElementVNode("span", { class: "text-body-2" }, "本地保留份数", -1)),
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
                                  "onUpdate:modelValue": _cache[31] || (_cache[31] = $event => ((form.backup_keep_count) = $event)),
                                  min: 1,
                                  max: 30,
                                  step: 1,
                                  color: "primary",
                                  "thumb-label": "",
                                  "hide-details": "",
                                  disabled: !form.backup_enabled
                                }, null, 8, ["modelValue", "disabled"])
                              ]),
                              _: 1
                            })
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    _createVNode(_unref(SettingSection), {
                      title: "通知与触发",
                      note: "备份完成通知和手动触发开关"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_VRow, { class: "aoa-setting-grid" }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VCol, {
                              cols: "12",
                              md: "4"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_VSwitch, {
                                  modelValue: form.backup_notify,
                                  "onUpdate:modelValue": _cache[32] || (_cache[32] = $event => ((form.backup_notify) = $event)),
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
                              md: "4"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_VSelect, {
                                  modelValue: form.backup_notify_type,
                                  "onUpdate:modelValue": _cache[33] || (_cache[33] = $event => ((form.backup_notify_type) = $event)),
                                  items: notificationTypeItems,
                                  label: "消息类型",
                                  disabled: !form.backup_enabled || !form.backup_notify
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
                                  modelValue: form.backup_onlyonce,
                                  "onUpdate:modelValue": _cache[34] || (_cache[34] = $event => ((form.backup_onlyonce) = $event)),
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
                        })
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                })
              ], 512), [
                [_vShow, activeSub.value === 'local']
              ]),
              _withDirectives(_createElementVNode("div", _hoisted_28, [
                _createVNode(_component_VForm, null, {
                  default: _withCtx(() => [
                    _createVNode(_unref(ModuleHero), {
                      enabled: form.backup_webdav_enabled,
                      "onUpdate:enabled": _cache[35] || (_cache[35] = $event => ((form.backup_webdav_enabled) = $event)),
                      icon: "mdi-cloud-upload-outline",
                      kicker: "MP 自动备份",
                      "on-title": "WebDAV 远端备份已启用",
                      "off-title": "WebDAV 远端备份未启用",
                      desc: "本地备份完成后同步上传远端|按策略保留历史版本",
                      "count-label": `${form.backup_webdav_max_count} 份保留`
                    }, null, 8, ["enabled", "count-label"]),
                    _createVNode(_unref(SettingSection), {
                      title: "远端连接",
                      note: "WebDAV 地址、账号和密码"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_VRow, { class: "aoa-setting-grid" }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VCol, {
                              cols: "12",
                              md: "6"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_VTextField, {
                                  modelValue: form.backup_webdav_hostname,
                                  "onUpdate:modelValue": _cache[36] || (_cache[36] = $event => ((form.backup_webdav_hostname) = $event)),
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
                                  "onUpdate:modelValue": _cache[37] || (_cache[37] = $event => ((form.backup_webdav_login) = $event)),
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
                                  "onUpdate:modelValue": _cache[38] || (_cache[38] = $event => ((form.backup_webdav_password) = $event)),
                                  label: "密码",
                                  type: "password",
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
                    }),
                    _createVNode(_unref(SettingSection), {
                      title: "远端策略",
                      note: "保留份数、通知渠道和连接校验"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_VRow, { class: "aoa-setting-grid" }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VCol, {
                              cols: "12",
                              md: "4"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_VSelect, {
                                  modelValue: form.backup_webdav_max_count,
                                  "onUpdate:modelValue": _cache[39] || (_cache[39] = $event => ((form.backup_webdav_max_count) = $event)),
                                  items: _unref(keepCountPresets),
                                  label: "远端保留份数",
                                  disabled: !form.backup_webdav_enabled
                                }, null, 8, ["modelValue", "items", "disabled"])
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
                                  "onUpdate:modelValue": _cache[40] || (_cache[40] = $event => ((form.backup_webdav_notify) = $event)),
                                  color: "primary",
                                  inset: "",
                                  "hide-details": "",
                                  label: "远端备份结果通知",
                                  disabled: !form.backup_webdav_enabled
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
                                  modelValue: form.backup_webdav_notify_type,
                                  "onUpdate:modelValue": _cache[41] || (_cache[41] = $event => ((form.backup_webdav_notify_type) = $event)),
                                  items: notificationTypeItems,
                                  label: "消息类型",
                                  disabled: !form.backup_webdav_enabled || !form.backup_webdav_notify
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
                                  modelValue: form.backup_webdav_digest_auth,
                                  "onUpdate:modelValue": _cache[42] || (_cache[42] = $event => ((form.backup_webdav_digest_auth) = $event)),
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
                                  "onUpdate:modelValue": _cache[43] || (_cache[43] = $event => ((form.backup_webdav_disable_check) = $event)),
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
                  ]),
                  _: 1
                })
              ], 512), [
                [_vShow, activeSub.value === 'webdav']
              ]),
              _withDirectives(_createElementVNode("div", _hoisted_29, [
                _createVNode(_component_VForm, null, {
                  default: _withCtx(() => [
                    _createVNode(_unref(ModuleHero), {
                      enabled: form.log_clean_enabled,
                      "onUpdate:enabled": _cache[44] || (_cache[44] = $event => ((form.log_clean_enabled) = $event)),
                      icon: "mdi-file-document-remove-outline",
                      kicker: "MP 日志清理",
                      "on-title": "插件日志清理已启用",
                      "off-title": "插件日志清理未启用",
                      desc: "按计划裁剪插件日志|保留排查信息和最近记录",
                      "count-label": `保留 ${form.log_clean_rows} 行`
                    }, null, 8, ["enabled", "count-label"]),
                    _createVNode(_unref(SettingSection), {
                      title: "清理策略",
                      note: "清理时间、保留行数和限定插件"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_VRow, { class: "aoa-setting-grid" }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VCol, {
                              cols: "12",
                              md: "4"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_VCronField, {
                                  modelValue: form.log_clean_cron,
                                  "onUpdate:modelValue": _cache[45] || (_cache[45] = $event => ((form.log_clean_cron) = $event)),
                                  label: "清理时间 (Cron)",
                                  disabled: !form.log_clean_enabled
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
                                  modelValue: form.log_clean_rows,
                                  "onUpdate:modelValue": _cache[46] || (_cache[46] = $event => ((form.log_clean_rows) = $event)),
                                  items: _unref(logRowsPresets),
                                  label: "保留行数",
                                  disabled: !form.log_clean_enabled
                                }, null, 8, ["modelValue", "items", "disabled"])
                              ]),
                              _: 1
                            }),
                            _createVNode(_component_VCol, {
                              cols: "12",
                              md: "4"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_VSelect, {
                                  modelValue: form.log_clean_selected_ids,
                                  "onUpdate:modelValue": _cache[47] || (_cache[47] = $event => ((form.log_clean_selected_ids) = $event)),
                                  items: installedPlugins.value,
                                  loading: installedLoading.value,
                                  label: "限定插件",
                                  "persistent-hint": "",
                                  hint: "留空＝全部插件",
                                  multiple: "",
                                  chips: "",
                                  "closable-chips": "",
                                  clearable: "",
                                  "prepend-inner-icon": "mdi-puzzle-outline",
                                  disabled: !form.log_clean_enabled
                                }, null, 8, ["modelValue", "items", "loading", "disabled"])
                              ]),
                              _: 1
                            })
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    _createVNode(_unref(SettingSection), {
                      title: "通知与触发",
                      note: "清理完成通知和手动触发开关"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_VRow, { class: "aoa-setting-grid" }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VCol, {
                              cols: "12",
                              md: "4"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_VSwitch, {
                                  modelValue: form.log_clean_notify,
                                  "onUpdate:modelValue": _cache[48] || (_cache[48] = $event => ((form.log_clean_notify) = $event)),
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
                              md: "4"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_VSelect, {
                                  modelValue: form.log_clean_notify_type,
                                  "onUpdate:modelValue": _cache[49] || (_cache[49] = $event => ((form.log_clean_notify_type) = $event)),
                                  items: notificationTypeItems,
                                  label: "消息类型",
                                  disabled: !form.log_clean_enabled || !form.log_clean_notify
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
                                  modelValue: form.log_clean_onlyonce,
                                  "onUpdate:modelValue": _cache[50] || (_cache[50] = $event => ((form.log_clean_onlyonce) = $event)),
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
                        })
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                })
              ], 512), [
                [_vShow, activeSub.value === 'logs']
              ]),
              _withDirectives(_createElementVNode("div", _hoisted_30, [
                _createVNode(_component_VForm, null, {
                  default: _withCtx(() => [
                    _createVNode(_unref(ModuleHero), {
                      enabled: form.mp_update_enabled,
                      "onUpdate:enabled": _cache[51] || (_cache[51] = $event => ((form.mp_update_enabled) = $event)),
                      icon: "mdi-movie-open-cog-outline",
                      kicker: "MP 更新检查",
                      "on-title": "主程序更新检查已启用",
                      "off-title": "主程序更新检查未启用",
                      desc: "定时检查后端和前端版本|默认提醒，不直接升级",
                      "count-label": `${form.mp_update_types?.length || 0} 个范围`
                    }, null, 8, ["enabled", "count-label"]),
                    _createVNode(_unref(SettingSection), {
                      title: "检查策略",
                      note: "检查时间、范围和通知渠道"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_VRow, { class: "aoa-setting-grid" }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VCol, {
                              cols: "12",
                              md: "4"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_VCronField, {
                                  modelValue: form.mp_update_cron,
                                  "onUpdate:modelValue": _cache[52] || (_cache[52] = $event => ((form.mp_update_cron) = $event)),
                                  label: "检查时间 (Cron)",
                                  disabled: !form.mp_update_enabled
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
                                  modelValue: form.mp_update_types,
                                  "onUpdate:modelValue": _cache[53] || (_cache[53] = $event => ((form.mp_update_types) = $event)),
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
                              md: "4"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_VSelect, {
                                  modelValue: form.mp_update_notify_type,
                                  "onUpdate:modelValue": _cache[54] || (_cache[54] = $event => ((form.mp_update_notify_type) = $event)),
                                  items: notificationTypeItems,
                                  label: "消息类型",
                                  disabled: !form.mp_update_enabled || !form.mp_update_notify
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
                                  modelValue: form.mp_update_notify,
                                  "onUpdate:modelValue": _cache[55] || (_cache[55] = $event => ((form.mp_update_notify) = $event)),
                                  color: "primary",
                                  inset: "",
                                  "hide-details": "",
                                  label: "发现新版本时通知",
                                  disabled: !form.mp_update_enabled
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
                                  modelValue: form.mp_update_restart_confirm,
                                  "onUpdate:modelValue": _cache[56] || (_cache[56] = $event => ((form.mp_update_restart_confirm) = $event)),
                                  color: "warning",
                                  inset: "",
                                  "hide-details": "",
                                  label: "允许自动重启以应用更新（高风险，谨慎开启）",
                                  disabled: !form.mp_update_enabled
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
              ], 512), [
                [_vShow, activeSub.value === 'mp']
              ]),
              _withDirectives(_createElementVNode("div", _hoisted_31, [
                _createVNode(_component_VForm, null, {
                  default: _withCtx(() => [
                    _createVNode(_unref(ModuleHero), {
                      enabled: form.market_update_enabled,
                      "onUpdate:enabled": _cache[57] || (_cache[57] = $event => ((form.market_update_enabled) = $event)),
                      icon: "mdi-puzzle-plus-outline",
                      kicker: "MP 插件库",
                      "on-title": "插件库更新检查已启用",
                      "off-title": "插件库更新检查未启用",
                      desc: "检查已安装插件新版本|按策略提醒或自动处理",
                      "count-label": form.market_update_auto_install ? '自动安装' : '仅提醒'
                    }, null, 8, ["enabled", "count-label"]),
                    _createVNode(_unref(SettingSection), {
                      title: "检查策略",
                      note: "检查间隔、通知方式和插件库访问方式"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_VRow, { class: "aoa-setting-grid" }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VCol, {
                              cols: "12",
                              md: "4"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_VSelect, {
                                  modelValue: form.market_update_interval,
                                  "onUpdate:modelValue": _cache[58] || (_cache[58] = $event => ((form.market_update_interval) = $event)),
                                  items: _unref(intervalPresets),
                                  label: "检查间隔",
                                  disabled: !form.market_update_enabled
                                }, null, 8, ["modelValue", "items", "disabled"])
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
                                  "onUpdate:modelValue": _cache[59] || (_cache[59] = $event => ((form.market_update_notify_type) = $event)),
                                  items: _unref(marketNotifyItems),
                                  label: "通知消息类型",
                                  disabled: !form.market_update_enabled
                                }, null, 8, ["modelValue", "items", "disabled"])
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
                                  "onUpdate:modelValue": _cache[60] || (_cache[60] = $event => ((form.market_update_timeout) = $event)),
                                  label: "请求超时（秒）",
                                  type: "number",
                                  min: "1",
                                  disabled: !form.market_update_enabled
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
                                  modelValue: form.market_update_notify,
                                  "onUpdate:modelValue": _cache[61] || (_cache[61] = $event => ((form.market_update_notify) = $event)),
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
                              md: "4"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_VSwitch, {
                                  modelValue: form.market_update_proxy,
                                  "onUpdate:modelValue": _cache[62] || (_cache[62] = $event => ((form.market_update_proxy) = $event)),
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
                              md: "4"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_VSwitch, {
                                  modelValue: form.market_update_auto_get,
                                  "onUpdate:modelValue": _cache[63] || (_cache[63] = $event => ((form.market_update_auto_get) = $event)),
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
                            _createVNode(_component_VExpansionPanel, { title: "高级选项" }, {
                              default: _withCtx(() => [
                                _createVNode(_component_VExpansionPanelText, null, {
                                  default: _withCtx(() => [
                                    _createVNode(_component_VRow, { class: "aoa-setting-grid" }, {
                                      default: _withCtx(() => [
                                        _createVNode(_component_VCol, {
                                          cols: "12",
                                          md: "6"
                                        }, {
                                          default: _withCtx(() => [
                                            _createVNode(_component_VSwitch, {
                                              modelValue: form.market_update_write_settings,
                                              "onUpdate:modelValue": _cache[64] || (_cache[64] = $event => ((form.market_update_write_settings) = $event)),
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
                                              "onUpdate:modelValue": _cache[65] || (_cache[65] = $event => ((form.market_update_write_env) = $event)),
                                              color: "warning",
                                              inset: "",
                                              "hide-details": "",
                                              label: "写回环境变量",
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
                                              modelValue: form.market_update_blacklist_enabled,
                                              "onUpdate:modelValue": _cache[66] || (_cache[66] = $event => ((form.market_update_blacklist_enabled) = $event)),
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
                                              modelValue: form.market_update_wiki_url,
                                              "onUpdate:modelValue": _cache[67] || (_cache[67] = $event => ((form.market_update_wiki_url) = $event)),
                                              label: "Wiki 地址",
                                              disabled: !form.market_update_enabled
                                            }, null, 8, ["modelValue", "disabled"])
                                          ]),
                                          _: 1
                                        }),
                                        _createVNode(_component_VCol, { cols: "12" }, {
                                          default: _withCtx(() => [
                                            _createVNode(_component_VSelect, {
                                              modelValue: form.market_update_blacklist,
                                              "onUpdate:modelValue": _cache[68] || (_cache[68] = $event => ((form.market_update_blacklist) = $event)),
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
                    _createVNode(_unref(SettingSection), {
                      title: "自动更新已安装插件",
                      note: "控制自动安装范围和排除范围"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_VRow, { class: "aoa-setting-grid" }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VCol, {
                              cols: "12",
                              md: "6"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_VSwitch, {
                                  modelValue: form.market_update_auto_install,
                                  "onUpdate:modelValue": _cache[69] || (_cache[69] = $event => ((form.market_update_auto_install) = $event)),
                                  color: "warning",
                                  inset: "",
                                  "hide-details": "",
                                  label: "自动安装插件新版",
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
                                  modelValue: form.market_update_skip_running,
                                  "onUpdate:modelValue": _cache[70] || (_cache[70] = $event => ((form.market_update_skip_running) = $event)),
                                  color: "primary",
                                  inset: "",
                                  "hide-details": "",
                                  label: "跳过正在运行的插件",
                                  disabled: !form.market_update_enabled || !form.market_update_auto_install
                                }, null, 8, ["modelValue", "disabled"])
                              ]),
                              _: 1
                            }),
                            _createVNode(_component_VCol, { cols: "12" }, {
                              default: _withCtx(() => [
                                _createVNode(_component_VSelect, {
                                  modelValue: form.market_update_install_ids,
                                  "onUpdate:modelValue": _cache[71] || (_cache[71] = $event => ((form.market_update_install_ids) = $event)),
                                  items: installedPlugins.value,
                                  loading: installedLoading.value,
                                  label: "自动更新范围",
                                  "persistent-hint": "",
                                  hint: "留空＝全部已安装",
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
                            _createVNode(_component_VCol, { cols: "12" }, {
                              default: _withCtx(() => [
                                _createVNode(_component_VSelect, {
                                  modelValue: form.market_update_exclude_ids,
                                  "onUpdate:modelValue": _cache[72] || (_cache[72] = $event => ((form.market_update_exclude_ids) = $event)),
                                  items: installedPlugins.value,
                                  loading: installedLoading.value,
                                  label: "排除插件",
                                  "persistent-hint": "",
                                  hint: "这些插件不自动更新",
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
                        })
                      ]),
                      _: 1
                    })
                  ]),
                  _: 1
                })
              ], 512), [
                [_vShow, activeSub.value === 'market']
              ]),
              _withDirectives(_createElementVNode("div", _hoisted_32, [
                _createVNode(_component_VForm, null, {
                  default: _withCtx(() => [
                    _createVNode(_unref(ModuleHero), {
                      enabled: !!(form.plugin_uninstall_ids && form.plugin_uninstall_ids.length),
                      icon: "mdi-puzzle-remove-outline",
                      kicker: "MP 插件卸载",
                      "on-title": "已选择卸载目标",
                      "off-title": "尚未选择卸载目标",
                      desc: "统一处理插件卸载与配置清理|数据清理与本地源码残留",
                      "count-label": `${form.plugin_uninstall_ids?.length || 0} 个插件`,
                      "state-on": "待执行",
                      "state-off": "待选择",
                      toggle: false
                    }, null, 8, ["enabled", "count-label"]),
                    _createVNode(_unref(SettingSection), {
                      title: "目标插件",
                      note: "选择需要卸载或清理残留的已安装插件"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_VRow, { class: "aoa-setting-grid" }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VCol, { cols: "12" }, {
                              default: _withCtx(() => [
                                _createVNode(_component_VSelect, {
                                  modelValue: form.plugin_uninstall_ids,
                                  "onUpdate:modelValue": _cache[73] || (_cache[73] = $event => ((form.plugin_uninstall_ids) = $event)),
                                  items: installedPlugins.value,
                                  loading: installedLoading.value,
                                  label: "选择要卸载的已安装插件",
                                  multiple: "",
                                  chips: "",
                                  "closable-chips": "",
                                  clearable: "",
                                  "prepend-inner-icon": "mdi-puzzle-remove-outline"
                                }, null, 8, ["modelValue", "items", "loading"])
                              ]),
                              _: 1
                            })
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    _createVNode(_unref(SettingSection), {
                      title: "清理范围",
                      note: "卸载插件、清除配置和清除数据可独立选择"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_VRow, { class: "aoa-setting-grid" }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VCol, {
                              cols: "12",
                              md: "4"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_VSwitch, {
                                  modelValue: form.plugin_uninstall_remove_plugin,
                                  "onUpdate:modelValue": _cache[74] || (_cache[74] = $event => ((form.plugin_uninstall_remove_plugin) = $event)),
                                  color: "error",
                                  inset: "",
                                  "hide-details": "",
                                  label: "卸载插件"
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
                                  modelValue: form.plugin_uninstall_clear_config,
                                  "onUpdate:modelValue": _cache[75] || (_cache[75] = $event => ((form.plugin_uninstall_clear_config) = $event)),
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
                              md: "4"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_VSwitch, {
                                  modelValue: form.plugin_uninstall_clear_data,
                                  "onUpdate:modelValue": _cache[76] || (_cache[76] = $event => ((form.plugin_uninstall_clear_data) = $event)),
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
                        })
                      ]),
                      _: 1
                    }),
                    _createVNode(_unref(SettingSection), {
                      title: "通知与残留",
                      note: "清理结果通知和本地源码残留处理"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_VRow, { class: "aoa-setting-grid" }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VCol, {
                              cols: "12",
                              md: "4"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_VSwitch, {
                                  modelValue: form.plugin_uninstall_notify,
                                  "onUpdate:modelValue": _cache[77] || (_cache[77] = $event => ((form.plugin_uninstall_notify) = $event)),
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
                              md: "4"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_VSelect, {
                                  modelValue: form.plugin_uninstall_notify_type,
                                  "onUpdate:modelValue": _cache[78] || (_cache[78] = $event => ((form.plugin_uninstall_notify_type) = $event)),
                                  items: notificationTypeItems,
                                  label: "消息类型",
                                  disabled: !form.plugin_uninstall_notify
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
                                  modelValue: form.plugin_uninstall_delete_source,
                                  "onUpdate:modelValue": _cache[79] || (_cache[79] = $event => ((form.plugin_uninstall_delete_source) = $event)),
                                  color: "error",
                                  inset: "",
                                  "hide-details": "",
                                  label: "删除本地源码"
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
                  ]),
                  _: 1
                })
              ], 512), [
                [_vShow, activeSub.value === 'clean']
              ]),
              _withDirectives(_createElementVNode("div", _hoisted_33, [
                _createVNode(_component_VForm, { class: "aoa-seed-form" }, {
                  default: _withCtx(() => [
                    _createVNode(_unref(ModuleHero), {
                      enabled: form.seedclean_enabled,
                      "onUpdate:enabled": _cache[80] || (_cache[80] = $event => ((form.seedclean_enabled) = $event)),
                      icon: "mdi-delete-sweep-outline",
                      kicker: "MP 下载器管理",
                      "on-title": "自动删种已启用",
                      "off-title": "自动删种未启用",
                      desc: "按下载器、动作和筛选条件治理种子|未填写筛选条件时不会处理",
                      "count-label": `${seedFilterCount.value} 个条件`
                    }, null, 8, ["enabled", "count-label"]),
                    _createVNode(_unref(SettingSection), {
                      title: "执行策略",
                      note: "执行周期、动作和下载器范围"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_VRow, { class: "aoa-setting-grid aoa-seed-basic-row" }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VCol, {
                              cols: "12",
                              md: "6"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_VCronField, {
                                  modelValue: form.seedclean_cron,
                                  "onUpdate:modelValue": _cache[81] || (_cache[81] = $event => ((form.seedclean_cron) = $event)),
                                  label: "执行周期 (Cron)",
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
                                  modelValue: form.seedclean_action,
                                  "onUpdate:modelValue": _cache[82] || (_cache[82] = $event => ((form.seedclean_action) = $event)),
                                  items: seedActionItems,
                                  "hide-details": "",
                                  label: "动作",
                                  disabled: !form.seedclean_enabled
                                }, null, 8, ["modelValue", "disabled"])
                              ]),
                              _: 1
                            }),
                            _createVNode(_component_VCol, { cols: "12" }, {
                              default: _withCtx(() => [
                                _createVNode(_component_VSelect, {
                                  modelValue: form.seedclean_downloaders,
                                  "onUpdate:modelValue": _cache[83] || (_cache[83] = $event => ((form.seedclean_downloaders) = $event)),
                                  items: downloaderOptions.value,
                                  loading: downloadersLoading.value,
                                  label: "下载器（必选）",
                                  multiple: "",
                                  chips: "",
                                  "closable-chips": "",
                                  clearable: "",
                                  "hide-details": "",
                                  "prepend-inner-icon": "mdi-download-network-outline",
                                  "no-data-text": "未配置下载器",
                                  disabled: !form.seedclean_enabled
                                }, null, 8, ["modelValue", "items", "loading", "disabled"])
                              ]),
                              _: 1
                            })
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    _createVNode(_unref(SettingSection), {
                      title: "筛选条件",
                      note: "任一条件命中后按动作处理，未填写条件时跳过"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_VRow, { class: "aoa-setting-grid aoa-seed-filter-grid" }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VCol, {
                              cols: "12",
                              sm: "6",
                              md: "4"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_VTextField, {
                                  modelValue: form.seedclean_size,
                                  "onUpdate:modelValue": _cache[84] || (_cache[84] = $event => ((form.seedclean_size) = $event)),
                                  label: "种子大小（GB）",
                                  "hide-details": "",
                                  placeholder: "1-10",
                                  disabled: !form.seedclean_enabled
                                }, null, 8, ["modelValue", "disabled"])
                              ]),
                              _: 1
                            }),
                            _createVNode(_component_VCol, {
                              cols: "12",
                              sm: "6",
                              md: "4"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_VTextField, {
                                  modelValue: form.seedclean_ratio,
                                  "onUpdate:modelValue": _cache[85] || (_cache[85] = $event => ((form.seedclean_ratio) = $event)),
                                  label: "分享率不小于",
                                  "hide-details": "",
                                  placeholder: "2",
                                  disabled: !form.seedclean_enabled
                                }, null, 8, ["modelValue", "disabled"])
                              ]),
                              _: 1
                            }),
                            _createVNode(_component_VCol, {
                              cols: "12",
                              sm: "6",
                              md: "4"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_VTextField, {
                                  modelValue: form.seedclean_time,
                                  "onUpdate:modelValue": _cache[86] || (_cache[86] = $event => ((form.seedclean_time) = $event)),
                                  label: "做种不少于（小时）",
                                  "hide-details": "",
                                  placeholder: "240",
                                  disabled: !form.seedclean_enabled
                                }, null, 8, ["modelValue", "disabled"])
                              ]),
                              _: 1
                            }),
                            _createVNode(_component_VCol, {
                              cols: "12",
                              sm: "6",
                              md: "4"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_VTextField, {
                                  modelValue: form.seedclean_upspeed,
                                  "onUpdate:modelValue": _cache[87] || (_cache[87] = $event => ((form.seedclean_upspeed) = $event)),
                                  label: "均速上限（KB/s）",
                                  "hide-details": "",
                                  placeholder: "低于才处理",
                                  disabled: !form.seedclean_enabled
                                }, null, 8, ["modelValue", "disabled"])
                              ]),
                              _: 1
                            }),
                            _createVNode(_component_VCol, {
                              cols: "12",
                              sm: "6",
                              md: "4"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_VTextField, {
                                  modelValue: form.seedclean_labels,
                                  "onUpdate:modelValue": _cache[88] || (_cache[88] = $event => ((form.seedclean_labels) = $event)),
                                  label: "标签",
                                  "hide-details": "",
                                  placeholder: "逗号分隔",
                                  disabled: !form.seedclean_enabled
                                }, null, 8, ["modelValue", "disabled"])
                              ]),
                              _: 1
                            }),
                            _createVNode(_component_VCol, {
                              cols: "12",
                              sm: "6",
                              md: "4"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_VTextField, {
                                  modelValue: form.seedclean_torrentcategorys,
                                  "onUpdate:modelValue": _cache[89] || (_cache[89] = $event => ((form.seedclean_torrentcategorys) = $event)),
                                  label: "任务分类",
                                  "hide-details": "",
                                  placeholder: "逗号分隔",
                                  disabled: !form.seedclean_enabled
                                }, null, 8, ["modelValue", "disabled"])
                              ]),
                              _: 1
                            }),
                            _createVNode(_component_VCol, {
                              cols: "12",
                              sm: "6",
                              md: "4"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_VTextField, {
                                  modelValue: form.seedclean_pathkeywords,
                                  "onUpdate:modelValue": _cache[90] || (_cache[90] = $event => ((form.seedclean_pathkeywords) = $event)),
                                  label: "保存路径关键词",
                                  "hide-details": "",
                                  placeholder: "支持正则",
                                  disabled: !form.seedclean_enabled
                                }, null, 8, ["modelValue", "disabled"])
                              ]),
                              _: 1
                            }),
                            _createVNode(_component_VCol, {
                              cols: "12",
                              sm: "6",
                              md: "4"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_VTextField, {
                                  modelValue: form.seedclean_trackerkeywords,
                                  "onUpdate:modelValue": _cache[91] || (_cache[91] = $event => ((form.seedclean_trackerkeywords) = $event)),
                                  label: "Tracker 关键词",
                                  "hide-details": "",
                                  placeholder: "支持正则",
                                  disabled: !form.seedclean_enabled
                                }, null, 8, ["modelValue", "disabled"])
                              ]),
                              _: 1
                            }),
                            _createVNode(_component_VCol, {
                              cols: "12",
                              sm: "6",
                              md: "4"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_VTextField, {
                                  modelValue: form.seedclean_torrentstates,
                                  "onUpdate:modelValue": _cache[92] || (_cache[92] = $event => ((form.seedclean_torrentstates) = $event)),
                                  label: "任务状态（仅 QB）",
                                  "hide-details": "",
                                  placeholder: "pausedUP,stalledUP",
                                  disabled: !form.seedclean_enabled
                                }, null, 8, ["modelValue", "disabled"])
                              ]),
                              _: 1
                            }),
                            _createVNode(_component_VCol, {
                              cols: "12",
                              sm: "6",
                              md: "4"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_VTextField, {
                                  modelValue: form.seedclean_errorkeywords,
                                  "onUpdate:modelValue": _cache[93] || (_cache[93] = $event => ((form.seedclean_errorkeywords) = $event)),
                                  label: "错误信息（仅 TR）",
                                  "hide-details": "",
                                  placeholder: "支持正则",
                                  disabled: !form.seedclean_enabled
                                }, null, 8, ["modelValue", "disabled"])
                              ]),
                              _: 1
                            })
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    _createVNode(_unref(SettingSection), {
                      title: "保护与通知",
                      note: "辅种保护、MoviePilot 任务限制和通知渠道"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_VRow, { class: "aoa-setting-grid" }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VCol, {
                              cols: "12",
                              md: "8"
                            }, {
                              default: _withCtx(() => [
                                _createElementVNode("div", _hoisted_34, [
                                  _createVNode(_component_VSwitch, {
                                    modelValue: form.seedclean_samedata,
                                    "onUpdate:modelValue": _cache[94] || (_cache[94] = $event => ((form.seedclean_samedata) = $event)),
                                    color: "primary",
                                    inset: "",
                                    "hide-details": "",
                                    label: "处理辅种",
                                    disabled: !form.seedclean_enabled
                                  }, null, 8, ["modelValue", "disabled"]),
                                  _createVNode(_component_VSwitch, {
                                    modelValue: form.seedclean_mponly,
                                    "onUpdate:modelValue": _cache[95] || (_cache[95] = $event => ((form.seedclean_mponly) = $event)),
                                    color: "primary",
                                    inset: "",
                                    "hide-details": "",
                                    label: "仅 MoviePilot 任务",
                                    disabled: !form.seedclean_enabled
                                  }, null, 8, ["modelValue", "disabled"]),
                                  _createVNode(_component_VSwitch, {
                                    modelValue: form.seedclean_notify,
                                    "onUpdate:modelValue": _cache[96] || (_cache[96] = $event => ((form.seedclean_notify) = $event)),
                                    color: "primary",
                                    inset: "",
                                    "hide-details": "",
                                    label: "处理结果通知",
                                    disabled: !form.seedclean_enabled
                                  }, null, 8, ["modelValue", "disabled"])
                                ])
                              ]),
                              _: 1
                            }),
                            _createVNode(_component_VCol, {
                              cols: "12",
                              md: "4"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_VSelect, {
                                  modelValue: form.seedclean_notify_type,
                                  "onUpdate:modelValue": _cache[97] || (_cache[97] = $event => ((form.seedclean_notify_type) = $event)),
                                  items: notificationTypeItems,
                                  "hide-details": "",
                                  label: "消息类型",
                                  disabled: !form.seedclean_enabled || !form.seedclean_notify
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
              ], 512), [
                [_vShow, activeSub.value === 'seedremove']
              ]),
              _withDirectives(_createElementVNode("div", _hoisted_35, [
                _createVNode(_component_VForm, { class: "aoa-media-form" }, {
                  default: _withCtx(() => [
                    _createVNode(_unref(ModuleHero), {
                      enabled: form.msgnotify_enabled,
                      "onUpdate:enabled": _cache[98] || (_cache[98] = $event => ((form.msgnotify_enabled) = $event)),
                      icon: "mdi-television-play",
                      kicker: "MP 媒体通知",
                      "on-title": "媒体服务器通知已启用",
                      "off-title": "媒体服务器通知未启用",
                      desc: "监听 Emby、Jellyfin、Plex 事件|按媒体服务器规则推送",
                      "count-label": `${form.msgnotify_types?.length || 0} 类事件`
                    }, null, 8, ["enabled", "count-label"]),
                    _createVNode(_unref(SettingSection), {
                      title: "通知范围",
                      note: "选择事件类型和媒体服务器范围"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_VRow, { class: "aoa-setting-grid aoa-media-field-row" }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VCol, {
                              cols: "12",
                              md: "4"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_VSelect, {
                                  modelValue: form.msgnotify_notify_type,
                                  "onUpdate:modelValue": _cache[99] || (_cache[99] = $event => ((form.msgnotify_notify_type) = $event)),
                                  items: notificationTypeItems,
                                  label: "消息类型",
                                  "prepend-inner-icon": "mdi-message-badge-outline",
                                  disabled: !form.msgnotify_enabled
                                }, null, 8, ["modelValue", "disabled"])
                              ]),
                              _: 1
                            }),
                            _createVNode(_component_VCol, {
                              cols: "12",
                              md: "8"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_VSelect, {
                                  modelValue: form.msgnotify_types,
                                  "onUpdate:modelValue": _cache[100] || (_cache[100] = $event => ((form.msgnotify_types) = $event)),
                                  items: _unref(msgGroupItems),
                                  label: "通知哪些事件",
                                  multiple: "",
                                  chips: "",
                                  "closable-chips": "",
                                  clearable: "",
                                  "prepend-inner-icon": "mdi-bell-cog-outline",
                                  disabled: !form.msgnotify_enabled
                                }, null, 8, ["modelValue", "items", "disabled"])
                              ]),
                              _: 1
                            }),
                            _createVNode(_component_VCol, { cols: "12" }, {
                              default: _withCtx(() => [
                                _createVNode(_component_VSelect, {
                                  modelValue: form.msgnotify_servers,
                                  "onUpdate:modelValue": _cache[101] || (_cache[101] = $event => ((form.msgnotify_servers) = $event)),
                                  items: mediaserverOptions.value,
                                  loading: mediaserversLoading.value,
                                  label: "媒体服务器范围",
                                  "persistent-hint": "",
                                  hint: "留空＝全部媒体服务器",
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
                  ]),
                  _: 1
                })
              ], 512), [
                [_vShow, activeSub.value === 'server']
              ]),
              _withDirectives(_createElementVNode("div", _hoisted_36, [
                _createVNode(_component_VForm, { class: "aoa-dltag-form" }, {
                  default: _withCtx(() => [
                    _createVNode(_unref(ModuleHero), {
                      enabled: form.dltag_enabled,
                      "onUpdate:enabled": _cache[102] || (_cache[102] = $event => ((form.dltag_enabled) = $event)),
                      icon: "mdi-tag-multiple-outline",
                      kicker: "MP 下载器管理",
                      "on-title": "批量打标签已启用",
                      "off-title": "批量打标签未启用",
                      desc: "遍历下载器种子并识别站点|按 tracker 所属站点补标签",
                      "count-label": `${form.dltag_downloaders?.length || 0} 个下载器`
                    }, null, 8, ["enabled", "count-label"]),
                    _createVNode(_unref(SettingSection), {
                      title: "打标设置",
                      note: "选择下载器范围并配置标签前缀"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_VRow, { class: "aoa-setting-grid aoa-dltag-field-row" }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VCol, {
                              cols: "12",
                              md: "7"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_VSelect, {
                                  modelValue: form.dltag_downloaders,
                                  "onUpdate:modelValue": _cache[103] || (_cache[103] = $event => ((form.dltag_downloaders) = $event)),
                                  items: downloaderOptions.value,
                                  loading: downloadersLoading.value,
                                  label: "下载器范围",
                                  "persistent-hint": "",
                                  hint: "留空＝全部已配置",
                                  multiple: "",
                                  chips: "",
                                  "closable-chips": "",
                                  clearable: "",
                                  "prepend-inner-icon": "mdi-download-network-outline",
                                  disabled: !form.dltag_enabled
                                }, null, 8, ["modelValue", "items", "loading", "disabled"])
                              ]),
                              _: 1
                            }),
                            _createVNode(_component_VCol, {
                              cols: "12",
                              md: "5"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_VTextField, {
                                  modelValue: form.dltag_prefix,
                                  "onUpdate:modelValue": _cache[104] || (_cache[104] = $event => ((form.dltag_prefix) = $event)),
                                  label: "标签前缀（可选）",
                                  placeholder: "如 站点-",
                                  clearable: "",
                                  disabled: !form.dltag_enabled
                                }, null, 8, ["modelValue", "disabled"])
                              ]),
                              _: 1
                            })
                          ]),
                          _: 1
                        })
                      ]),
                      _: 1
                    }),
                    _createVNode(_unref(SettingSection), {
                      title: "通知设置",
                      note: "打标完成后按选择渠道通知"
                    }, {
                      default: _withCtx(() => [
                        _createVNode(_component_VRow, { class: "aoa-setting-grid aoa-dltag-notify-row" }, {
                          default: _withCtx(() => [
                            _createVNode(_component_VCol, {
                              cols: "12",
                              md: "4"
                            }, {
                              default: _withCtx(() => [
                                _createVNode(_component_VSwitch, {
                                  modelValue: form.dltag_notify,
                                  "onUpdate:modelValue": _cache[105] || (_cache[105] = $event => ((form.dltag_notify) = $event)),
                                  color: "primary",
                                  inset: "",
                                  "hide-details": "",
                                  label: "完成后通知",
                                  disabled: !form.dltag_enabled
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
                                  modelValue: form.dltag_notify_type,
                                  "onUpdate:modelValue": _cache[106] || (_cache[106] = $event => ((form.dltag_notify_type) = $event)),
                                  items: notificationTypeItems,
                                  label: "消息类型",
                                  disabled: !form.dltag_enabled || !form.dltag_notify
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
              ], 512), [
                [_vShow, activeSub.value === 'dltagmain']
              ])
            ]),
            (activeActionItems.value.length)
              ? (_openBlock(), _createElementBlock("div", _hoisted_37, [
                  _createElementVNode("div", _hoisted_38, [
                    (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(activeActionItems.value, (item) => {
                      return (_openBlock(), _createElementBlock("div", {
                        key: item.path,
                        class: "aoa-action-dock-item"
                      }, [
                        _createVNode(_component_VBtn, {
                          size: "small",
                          color: item.color || 'primary',
                          variant: "tonal",
                          "prepend-icon": item.icon,
                          class: "aoa-action-btn text-none",
                          disabled: item.disabled,
                          loading: action.running === item.path,
                          onClick: $event => (runAction(item.path, item.label))
                        }, {
                          default: _withCtx(() => [
                            _createTextVNode(_toDisplayString(item.label), 1)
                          ]),
                          _: 2
                        }, 1032, ["color", "prepend-icon", "disabled", "loading", "onClick"]),
                        _createElementVNode("span", _hoisted_39, _toDisplayString(item.note), 1)
                      ]))
                    }), 128))
                  ])
                ]))
              : _createCommentVNode("", true)
          ])
        ]),
        _createVNode(_component_VDivider, { class: "aoa-hairline" }),
        _createVNode(_component_VCardActions, { class: "aoa-actions" }, {
          default: _withCtx(() => [
            _createVNode(_component_VFadeTransition, null, {
              default: _withCtx(() => [
                (action.message)
                  ? (_openBlock(), _createElementBlock("span", {
                      key: 0,
                      class: _normalizeClass([action.ok ? 'text-success' : 'text-error', "text-caption"])
                    }, _toDisplayString(action.message), 3))
                  : _createCommentVNode("", true)
              ]),
              _: 1
            }),
            _createVNode(_component_VSpacer),
            _createVNode(_component_VBtn, {
              variant: "text",
              onClick: _cache[107] || (_cache[107] = $event => (emit('close')))
            }, {
              default: _withCtx(() => [...(_cache[113] || (_cache[113] = [
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
              default: _withCtx(() => [...(_cache[114] || (_cache[114] = [
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
  ], 512))
}
}

};
const Config = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-5ea76afd"]]);

export { Config as default };
