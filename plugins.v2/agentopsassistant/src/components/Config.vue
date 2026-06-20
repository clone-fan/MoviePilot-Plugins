<script setup>
import { reactive, ref, computed, watch, onMounted, onBeforeUnmount, defineComponent, h, resolveComponent } from 'vue'
import { postPluginApi, getPluginApi } from './api'

const props = defineProps({
  api: { type: [Object, Function], default: null },
  initialConfig: { type: Object, default: () => ({}) },
})
const emit = defineEmits(['save', 'close', 'switch'])

const form = reactive({})
const activeMain = ref('report')
const activeSub = ref('overview')
const configRoot = ref(null)
let dialogScrollHost = null

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
      const VIcon = resolveComponent('VIcon')
      const VChip = resolveComponent('VChip')
      const VSwitch = resolveComponent('VSwitch')
      const descLines = String(props.desc || '').split(/\n|\|/)
      const descChildren = []
      descLines.forEach((line, index) => {
        if (index) descChildren.push(h('br'))
        descChildren.push(line)
      })
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
})

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
})

// 手动触发动作状态
const action = reactive({ running: '', message: '', ok: true })
async function runAction(path, label) {
  if (action.running) return
  action.running = path
  action.message = ''
  try {
    const res = await postPluginApi(props.api, path)
    const ok = !res || res.code === 0 || res.code === undefined
    action.ok = ok
    action.message = (res && res.msg) || `${label}已${ok ? '完成' : '失败'}`
  } catch (err) {
    action.ok = false
    action.message = err?.message || `${label}失败`
  } finally {
    action.running = ''
  }
}

// 已安装插件（插件卸载 / 日志限定 共用）
const installedPlugins = ref([])
const installedLoading = ref(false)
async function loadInstalledPlugins() {
  installedLoading.value = true
  try {
    const res = await getPluginApi(props.api, 'installed_plugins')
    installedPlugins.value = Array.isArray(res) ? res : (res?.data || [])
  } catch {
    installedPlugins.value = []
  } finally {
    installedLoading.value = false
  }
}

// 插件库仓库（更新黑名单用）
const pluginMarkets = ref([])
const marketsLoading = ref(false)
async function loadPluginMarkets() {
  marketsLoading.value = true
  try {
    const res = await getPluginApi(props.api, 'plugin_markets')
    pluginMarkets.value = Array.isArray(res) ? res : (res?.data || [])
  } catch {
    pluginMarkets.value = []
  } finally {
    marketsLoading.value = false
  }
}

// 下载器列表（自动删种用）
const downloaderOptions = ref([])
const downloadersLoading = ref(false)
async function loadDownloaders() {
  downloadersLoading.value = true
  try {
    const res = await getPluginApi(props.api, 'downloaders')
    downloaderOptions.value = Array.isArray(res) ? res : (res?.data || [])
  } catch {
    downloaderOptions.value = []
  } finally {
    downloadersLoading.value = false
  }
}

// 媒体服务器列表（媒体库通知按服务器过滤用）
const mediaserverOptions = ref([])
const mediaserversLoading = ref(false)
async function loadMediaservers() {
  mediaserversLoading.value = true
  try {
    const res = await getPluginApi(props.api, 'mediaservers')
    mediaserverOptions.value = Array.isArray(res) ? res : (res?.data || [])
  } catch {
    mediaserverOptions.value = []
  } finally {
    mediaserversLoading.value = false
  }
}

const defaults = {
  enabled: false,
  sidebar_nav_enabled: true,
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
}

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
]

const navGroups = computed(() => {
  const order = []
  const map = {}
  for (const item of mainTabs) {
    const g = item.group || '其他'
    if (!map[g]) { map[g] = { name: g, items: [] }; order.push(map[g]) }
    map[g].items.push(item)
  }
  return order
})

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
}

const subscribeSubtypeItems = [{ title: '电影', value: 'movie' }, { title: '电视剧', value: 'tv' }]
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
]
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
]
const siteStatRangeItems = [{ title: '今日数据', value: 'today' }, { title: '汇总数据', value: 'total' }, { title: '所有数据', value: 'all' }]
const siteNotifyItems = [{ title: '增量变化', value: 'inc' }, { title: '全部数据', value: 'all' }, { title: '不通知', value: 'none' }]
const marketNotifyItems = notificationTypeItems
const mpUpdateTypes = ['后端', '前端'].map(v => ({ title: v, value: v }))
const keepCountPresets = [3, 5, 7, 10, 15].map(v => ({ title: `保留 ${v} 份`, value: v }))
const logRowsPresets = [100, 300, 500, 1000, 2000].map(v => ({ title: `保留 ${v} 行`, value: v }))
const intervalPresets = [3600, 21600, 43200, 86400, 604800].map(v => ({ title: v < 86400 ? `${v / 3600} 小时` : `${v / 86400} 天`, value: v }))
const seedActionItems = [{ title: '暂停', value: 'pause' }, { title: '删除种子', value: 'delete' }, { title: '删除种子和文件', value: 'deletefile' }]
const subfillDetailItems = ['分辨率', '资源质量', '特效', '制作组', '站点'].map(v => ({ title: v, value: v }))
const msgGroupItems = ['新入库', '开始播放', '停止播放', '登录成功', '登录失败', '标记'].map(v => ({ title: v, value: v }))
const healthCheckItems = [
  { title: '数据库', value: '数据库', icon: 'mdi-database-check-outline', desc: '连接与基础读写状态' },
  { title: '存储空间', value: '存储空间', icon: 'mdi-harddisk', desc: '下载与媒体库容量余量' },
  { title: '目录权限', value: '目录权限', icon: 'mdi-folder-key-outline', desc: '关键路径可访问性' },
]
const healthDatabaseTargets = [
  { title: '当前主库', value: 'current' },
  { title: 'SQLite 配置库', value: 'sqlite' },
  { title: 'PostgreSQL 主库', value: 'postgresql' },
]
const healthStorageTargets = [
  { title: 'MoviePilot 存储配置', value: 'storages' },
  { title: '配置目录', value: 'config' },
  { title: '下载目录', value: 'download' },
  { title: '媒体库目录', value: 'library' },
]
const healthDirectoryTargets = [
  { title: '配置目录', value: 'config' },
  { title: '插件目录', value: 'plugin' },
  { title: '下载目录', value: 'download' },
  { title: '媒体库目录', value: 'library' },
]
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
}
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
]

const currentMain = computed(() => mainTabs.find(item => item.key === activeMain.value) || mainTabs[0])
const currentSubs = computed(() => subTabs[activeMain.value] || [])
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
  }
  return actions[activeSub.value] || []
})
const healthSelectedCount = computed(() => {
  const selected = Array.isArray(form.health_check_items) ? form.health_check_items : []
  return selected.length || healthCheckItems.length
})
const reportEnabledCount = computed(() => reportSections.filter(item => form[item.key]).length)
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
].filter(Boolean).length)

function selectionValue(item) {
  return item?.raw?.value ?? item?.value ?? item?.props?.value ?? item
}

function selectionTitle(item) {
  const value = selectionValue(item)
  const title = healthChipLabels[value] || item?.props?.title || item?.raw?.title || item?.title || value
  return String(title || '')
}

watch(() => props.initialConfig, value => {
  Object.keys(form).forEach(key => delete form[key])
  Object.assign(form, defaults, value || {})
  const toArr = v => typeof v === 'string' ? v.split(',').map(s => s.trim()).filter(Boolean) : (Array.isArray(v) ? v : [])
  form.subscribe_reminder_subtype = toArr(form.subscribe_reminder_subtype)
  form.mp_update_types = toArr(form.mp_update_types)
  form.plugin_uninstall_ids = toArr(form.plugin_uninstall_ids)
  form.log_clean_selected_ids = toArr(form.log_clean_selected_ids)
  form.market_update_blacklist = toArr(form.market_update_blacklist)
  form.market_update_install_ids = toArr(form.market_update_install_ids)
  form.market_update_exclude_ids = toArr(form.market_update_exclude_ids)
  form.seedclean_downloaders = toArr(form.seedclean_downloaders)
  form.subfill_details = toArr(form.subfill_details)
  form.msgnotify_types = toArr(form.msgnotify_types)
  form.msgnotify_servers = toArr(form.msgnotify_servers)
  form.dltag_downloaders = toArr(form.dltag_downloaders)
  form.health_check_items = toArr(form.health_check_items)
  form.health_check_database_targets = toArr(form.health_check_database_targets)
  form.health_check_storage_targets = toArr(form.health_check_storage_targets)
  form.health_check_directory_targets = toArr(form.health_check_directory_targets)
}, { immediate: true, deep: true })

function saveConfig() {
  emit('save', {
    ...form,
    daily_report_telegram_rich_enabled: true,
    daily_report_telegram_bot_token: '',
    daily_report_telegram_chat_id: '',
  })
}

function selectMain(key) {
  if (activeMain.value === key) return
  activeMain.value = key
  activeSub.value = subTabs[key]?.[0]?.key || ''
}

function bindDialogScrollHost() {
  const host = configRoot.value?.closest?.('.v-card-text.pa-0')
  if (!host || host === dialogScrollHost) return
  dialogScrollHost?.classList.remove('aoa-config-scroll-host')
  dialogScrollHost = host
  dialogScrollHost.classList.add('aoa-config-scroll-host')
}

onMounted(() => {
  bindDialogScrollHost()
  loadInstalledPlugins()
  loadPluginMarkets()
  loadDownloaders()
  loadMediaservers()
})

onBeforeUnmount(() => {
  dialogScrollHost?.classList.remove('aoa-config-scroll-host')
  dialogScrollHost = null
})
</script>
<template>
  <div ref="configRoot" class="aoa-config">
    <VCard flat class="aoa-card">
      <VCardItem class="aoa-header">
        <template #prepend>
          <VAvatar color="primary" variant="tonal" size="44" rounded="lg">
            <VIcon icon="mdi-shield-sync-outline" size="24" />
          </VAvatar>
        </template>
        <VCardTitle class="text-h6 aoa-header-title">MP 运维助手</VCardTitle>
        <VCardSubtitle class="text-caption aoa-header-subtitle">配置中心</VCardSubtitle>
        <template #append>
          <div class="d-flex align-center ga-2 aoa-header-controls">
            <VSwitch
              v-model="form.enabled"
              color="primary"
              class="aoa-header-switch"
              density="compact"
              hide-details
              inset
              :label="form.enabled ? '已启用' : '已停用'"
            />
            <VSwitch
              v-model="form.sidebar_nav_enabled"
              color="primary"
              class="aoa-header-switch"
              density="compact"
              hide-details
              inset
              label="侧边栏入口"
            />
            <VBtn size="small" variant="text" color="primary" prepend-icon="mdi-view-dashboard-outline" class="text-none aoa-header-link" @click="emit('switch')">
              仪表盘
            </VBtn>
            <VBtn icon="mdi-close" variant="text" @click="emit('close')" />
          </div>
        </template>
      </VCardItem>
      <VDivider class="aoa-hairline" />
      <div class="aoa-body">
        <nav class="aoa-nav">
          <div class="aoa-nav-scroll">
            <VList density="comfortable" nav class="py-2">
              <template v-for="grp in navGroups" :key="grp.name">
                <VListSubheader class="aoa-nav-group">{{ grp.name }}</VListSubheader>
                <VListItem
                  v-for="item in grp.items"
                  :key="item.key"
                  :active="activeMain === item.key"
                  color="primary"
                  rounded="lg"
                  class="aoa-nav-item"
                  @click="selectMain(item.key)"
                >
                  <template #prepend>
                    <VIcon :icon="item.icon" class="aoa-nav-icon" />
                  </template>
                  <VListItemTitle>{{ item.title }}</VListItemTitle>
                </VListItem>
              </template>
            </VList>
          </div>
        </nav>
        <section class="aoa-content">
          <div class="aoa-subtabs">
            <div class="aoa-subtab-list">
              <button
                v-for="sub in currentSubs"
                :key="sub.key"
                type="button"
                class="aoa-subtab"
                :class="{ 'aoa-subtab--active': activeSub === sub.key }"
                @click="activeSub = sub.key"
              >
                <VIcon :icon="sub.icon" size="18" class="mr-1" />{{ sub.title }}
              </button>
            </div>
            <div v-if="currentMain.desc" class="aoa-subtab-desc">
              {{ currentMain.desc }}
            </div>
          </div>
          <VDivider class="aoa-hairline" />
          <div class="aoa-window">
            <!-- 每日汇报 · 汇报总览 -->
            <div v-show="activeSub === 'overview'" class="aoa-pane">
              <VForm>
                <ModuleHero
                  v-model:enabled="form.daily_report_enabled"
                  icon="mdi-newspaper-variant-outline"
                  kicker="MP 每日汇报"
                  on-title="定时汇报已启用"
                  off-title="定时汇报未启用"
                  desc="按计划聚合站点、订阅与入库|同步整理存储与健康信息"
                  :count-label="`${reportEnabledCount} 个栏目`"
                />
                <SettingSection title="汇报设置" note="推送使用 MoviePilot 全局 Telegram 通知配置">
                  <VRow class="aoa-setting-grid">
                    <VCol cols="12" md="6">
                      <VCronField v-model="form.daily_report_cron" label="汇报时间 (Cron)"
                        :disabled="!form.daily_report_enabled" />
                    </VCol>
                    <VCol cols="12" md="6">
                      <VTextField v-model="form.daily_report_greeting" label="汇报称呼"
                        placeholder="少爷" prepend-inner-icon="mdi-account-heart-outline"
                        persistent-hint hint="汇报开头与提醒中对你的称呼，留空默认“少爷”" clearable
                        :disabled="!form.daily_report_enabled" />
                    </VCol>
                  </VRow>
                </SettingSection>
              </VForm>
            </div>

            <!-- 每日汇报 · 汇报栏目 -->
            <div v-show="activeSub === 'columns'" class="aoa-pane aoa-columns-pane">
              <VForm class="aoa-columns-form">
                <ModuleHero
                  :enabled="reportEnabledCount > 0"
                  icon="mdi-view-column-outline"
                  kicker="MP 每日汇报"
                  on-title="日报栏目已编排"
                  off-title="日报栏目未启用"
                  desc="统一控制并入日报的内容|组件状态会同步提示"
                  :count-label="`${reportEnabledCount} / ${reportSections.length} 个栏目`"
                  state-on="已配置"
                  state-off="待配置"
                  :toggle="false"
                />
                <SettingSection title="汇报栏目" note="勾选决定日报展示的完整栏目，对应组件未启用时自动提示">
                  <div class="aoa-table-wrap">
                    <div class="aoa-report-table-scroll">
                      <VTable class="aoa-report-table">
                        <thead>
                          <tr>
                            <th scope="col" class="aoa-col-enable">启用</th>
                            <th scope="col">组件</th>
                            <th scope="col">日报栏目</th>
                            <th scope="col">备注</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr v-for="s in reportSections" :key="s.key">
                            <td class="aoa-col-enable" data-label="启用">
                              <VCheckbox
                                v-model="form[s.key]"
                                color="primary"
                                hide-details
                                density="compact"
                                :disabled="s.requires && !form[`${s.requires}_enabled`]"
                              />
                            </td>
                            <td data-label="组件">
                              <VChip size="small" variant="tonal" color="primary">{{ s.component }}</VChip>
                            </td>
                            <td class="aoa-table-strong" data-label="栏目">{{ s.label }}</td>
                            <td class="aoa-table-note" data-label="备注">
                              <span v-if="s.requires && !form[`${s.requires}_enabled`]">需启用对应组件</span>
                              <span v-else>{{ s.note }}</span>
                            </td>
                          </tr>
                        </tbody>
                      </VTable>
                    </div>
                  </div>
                </SettingSection>
              </VForm>
            </div>

            <!-- 订阅与站点 · 订阅追新 -->
            <div v-show="activeSub === 'subscribe'" class="aoa-pane">
              <VForm>
                <ModuleHero
                  v-model:enabled="form.subscribe_reminder_enabled"
                  icon="mdi-bell-ring-outline"
                  kicker="MP 订阅管理"
                  on-title="订阅追新已启用"
                  off-title="订阅追新未启用"
                  desc="按计划推送今日订阅追新|日报展示由汇报栏目控制"
                  :count-label="`${form.subscribe_reminder_subtype?.length || 0} 类提醒`"
                />
                <SettingSection title="追新设置" note="推送时间、订阅类型与消息渠道集中配置">
                  <VRow class="aoa-setting-grid">
                    <VCol cols="12" md="4">
                      <VCronField v-model="form.subscribe_reminder_cron" label="推送时间 (Cron)"
                        :disabled="!form.subscribe_reminder_enabled" />
                    </VCol>
                    <VCol cols="12" md="5">
                      <VSelect v-model="form.subscribe_reminder_subtype" :items="subscribeSubtypeItems"
                        label="提醒类型" multiple chips closable-chips :disabled="!form.subscribe_reminder_enabled" />
                    </VCol>
                    <VCol cols="12" md="3">
                      <VSelect v-model="form.subscribe_reminder_msgtype" :items="messageTypeItems"
                        label="消息类型" :disabled="!form.subscribe_reminder_enabled" />
                    </VCol>
                  </VRow>
                </SettingSection>
              </VForm>
            </div>

            <!-- 每日汇报 · 站点数据统计 -->
            <div v-show="activeSub === 'sites'" class="aoa-pane">
              <VForm>
                <ModuleHero
                  v-model:enabled="form.site_stat_enabled"
                  icon="mdi-chart-line"
                  kicker="MP 站点统计"
                  on-title="站点数据采集已启用"
                  off-title="站点数据采集未启用"
                  desc="为仪表盘和日报提供站点状态|统计上传下载增量与趋势"
                  :count-label="form.site_stat_dashboard_type === 'today' ? '今日数据' : '统计数据'"
                />
                <SettingSection title="统计设置" note="控制仪表盘站点数据口径与通知方式">
                  <VRow class="aoa-setting-grid">
                    <VCol cols="12" md="6">
                      <VSelect v-model="form.site_stat_dashboard_type" :items="siteStatRangeItems"
                        label="统计数据范围" :disabled="!form.site_stat_enabled" />
                    </VCol>
                    <VCol cols="12" md="6">
                      <VSelect v-model="form.site_stat_notify_type" :items="siteNotifyItems"
                        label="通知方式" :disabled="!form.site_stat_enabled" />
                    </VCol>
                  </VRow>
                </SettingSection>
              </VForm>
            </div>

            <!-- 系统维护 · 健康巡查 -->
            <div v-show="activeSub === 'hc'" class="aoa-pane">
              <VForm class="aoa-health-form">
                <ModuleHero
                  v-model:enabled="form.health_check_enabled"
                  icon="mdi-heart-pulse"
                  kicker="MP 健康巡查"
                  on-title="自动巡查已启用"
                  off-title="自动巡查未启用"
                  desc="数据库、存储空间、目录权限|按计划检查，异常进入通知链路"
                  :count-label="`${healthSelectedCount} 项巡查`"
                />

                <SettingSection title="巡查设置" note="项目、时间、数据库、存储、目录和容量阈值集中配置">
                  <div class="aoa-health-scope-grid">
                    <VCronField v-model="form.health_check_cron" label="巡查时间 (Cron)" class="aoa-health-field-third"
                      :disabled="!form.health_check_enabled" />
                    <VTextField v-model.number="form.health_check_storage_threshold" label="容量阈值" type="number" class="aoa-health-field-third"
                      min="1" max="99" suffix="%" :disabled="!form.health_check_enabled" />
                    <VSelect v-model="form.health_check_notify_type" :items="notificationTypeItems" label="异常通知渠道"
                      class="aoa-health-field-third" :disabled="!form.health_check_enabled" />
                    <VSelect v-model="form.health_check_items" :items="healthCheckItems" class="aoa-health-field-full aoa-health-select"
                      label="巡查项目" multiple chips closable-chips clearable :disabled="!form.health_check_enabled">
                      <template #chip="{ item, props }">
                        <VChip v-bind="props" class="aoa-health-selection-chip" variant="tonal">
                          {{ selectionTitle(item) }}
                        </VChip>
                      </template>
                    </VSelect>
                    <VSelect v-model="form.health_check_database_targets" :items="healthDatabaseTargets" class="aoa-health-field-full aoa-health-select"
                      label="数据库" multiple chips closable-chips clearable :disabled="!form.health_check_enabled">
                      <template #chip="{ item, props }">
                        <VChip v-bind="props" class="aoa-health-selection-chip" variant="tonal">
                          {{ selectionTitle(item) }}
                        </VChip>
                      </template>
                    </VSelect>
                    <VSelect v-model="form.health_check_storage_targets" :items="healthStorageTargets" class="aoa-health-field-full aoa-health-select"
                      label="存储空间" multiple chips closable-chips clearable :disabled="!form.health_check_enabled">
                      <template #chip="{ item, props }">
                        <VChip v-bind="props" class="aoa-health-selection-chip" variant="tonal">
                          {{ selectionTitle(item) }}
                        </VChip>
                      </template>
                    </VSelect>
                    <VSelect v-model="form.health_check_directory_targets" :items="healthDirectoryTargets" class="aoa-health-field-full aoa-health-select"
                      label="目录权限" multiple chips closable-chips clearable :disabled="!form.health_check_enabled">
                      <template #chip="{ item, props }">
                        <VChip v-bind="props" class="aoa-health-selection-chip" variant="tonal">
                          {{ selectionTitle(item) }}
                        </VChip>
                      </template>
                    </VSelect>
                  </div>
                </SettingSection>
              </VForm>
            </div>

            <!-- 每日汇报 · 订阅规则填充 -->
            <div v-show="activeSub === 'subfill'" class="aoa-pane">
              <VForm>
                <ModuleHero
                  v-model:enabled="form.subfill_enabled"
                  icon="mdi-auto-fix"
                  kicker="MP 订阅管理"
                  on-title="订阅规则填充已启用"
                  off-title="订阅规则填充未启用"
                  desc="用已下载资源规格回填订阅规则|锁定后续剧集追同款版本"
                  :count-label="`${form.subfill_details?.length || 0} 项填充`"
                />
                <SettingSection title="规则填充" note="选择自动填充范围，并配置完成后的通知渠道">
                  <VRow class="aoa-setting-grid">
                    <VCol cols="12" md="6">
                      <VSwitch v-model="form.subfill_notify" color="primary" inset hide-details
                        label="填充后发送通知" :disabled="!form.subfill_enabled" />
                    </VCol>
                    <VCol cols="12" md="6">
                      <VSelect v-model="form.subfill_notify_type" :items="notificationTypeItems"
                        label="消息类型" :disabled="!form.subfill_enabled || !form.subfill_notify" />
                    </VCol>
                    <VCol cols="12">
                      <VSelect v-model="form.subfill_details" :items="subfillDetailItems"
                        label="自动填充哪些规则" multiple chips closable-chips clearable
                        prepend-inner-icon="mdi-auto-fix"
                        :disabled="!form.subfill_enabled" />
                    </VCol>
                  </VRow>
                </SettingSection>

                <SettingSection title="二级分类自定义填充" note="每行一个分类，用 # 分隔字段">
                  <VRow class="aoa-setting-grid">
                    <VCol cols="12" md="6">
                      <VSwitch v-model="form.subfill_category_enabled" color="primary" inset hide-details
                        label="启用二级分类自定义填充" />
                    </VCol>
                    <VCol cols="12">
                      <VTextarea v-model="form.subfill_category_confs"
                        label="二级分类规则（每行一个分类）" auto-grow rows="3"
                        placeholder="category:国漫,日番#resolution:1080p#quality:WEB-DL#include:简体#sites:馒头,青蛙#savepath:/media/动漫/{name}"
                        :disabled="!form.subfill_category_enabled" />
                    </VCol>
                  </VRow>
                </SettingSection>
              </VForm>
            </div>
            <!-- 自动备份 · 本地备份 -->
            <div v-show="activeSub === 'local'" class="aoa-pane">
              <VForm>
                <ModuleHero
                  v-model:enabled="form.backup_enabled"
                  icon="mdi-folder-arrow-up-outline"
                  kicker="MP 自动备份"
                  on-title="本地备份已启用"
                  off-title="本地备份未启用"
                  desc="按计划打包配置和关键数据|保留最近备份版本"
                  :count-label="`${form.backup_keep_count} 份保留`"
                />
                <SettingSection title="本地策略" note="备份时间、路径和保留份数集中配置">
                  <VRow class="aoa-setting-grid">
                    <VCol cols="12" md="6">
                      <VCronField v-model="form.backup_cron" label="备份时间 (Cron)"
                        :disabled="!form.backup_enabled" />
                    </VCol>
                    <VCol cols="12" md="6">
                      <VTextField v-model="form.backup_path" label="本地备份路径"
                        prepend-inner-icon="mdi-folder-outline" :disabled="!form.backup_enabled" />
                    </VCol>
                    <VCol cols="12">
                      <div class="d-flex align-center justify-space-between mb-1">
                        <span class="text-body-2">本地保留份数</span>
                        <VChip size="small" color="primary" variant="tonal">{{ form.backup_keep_count }} 份</VChip>
                      </div>
                      <VSlider v-model="form.backup_keep_count" :min="1" :max="30" :step="1"
                        color="primary" thumb-label hide-details :disabled="!form.backup_enabled" />
                    </VCol>
                  </VRow>
                </SettingSection>
                <SettingSection title="通知与触发" note="备份完成通知和手动触发开关">
                  <VRow class="aoa-setting-grid">
                    <VCol cols="12" md="4">
                      <VSwitch v-model="form.backup_notify" color="primary" inset hide-details
                        label="备份结果通知" :disabled="!form.backup_enabled" />
                    </VCol>
                    <VCol cols="12" md="4">
                      <VSelect v-model="form.backup_notify_type" :items="notificationTypeItems"
                        label="消息类型" :disabled="!form.backup_enabled || !form.backup_notify" />
                    </VCol>
                    <VCol cols="12" md="4">
                      <VSwitch v-model="form.backup_onlyonce" color="warning" inset hide-details
                        label="保存后立即备份一次" :disabled="!form.backup_enabled" />
                    </VCol>
                  </VRow>
                </SettingSection>
              </VForm>
            </div>

            <!-- 自动备份 · WebDAV -->
            <div v-show="activeSub === 'webdav'" class="aoa-pane">
              <VForm>
                <ModuleHero
                  v-model:enabled="form.backup_webdav_enabled"
                  icon="mdi-cloud-upload-outline"
                  kicker="MP 自动备份"
                  on-title="WebDAV 远端备份已启用"
                  off-title="WebDAV 远端备份未启用"
                  desc="本地备份完成后同步上传远端|按策略保留历史版本"
                  :count-label="`${form.backup_webdav_max_count} 份保留`"
                />
                <SettingSection title="远端连接" note="WebDAV 地址、账号和密码">
                  <VRow class="aoa-setting-grid">
                    <VCol cols="12" md="6">
                      <VTextField v-model="form.backup_webdav_hostname" label="WebDAV 地址"
                        placeholder="https://dav.example.com/backup" prepend-inner-icon="mdi-web"
                        :disabled="!form.backup_webdav_enabled" />
                    </VCol>
                    <VCol cols="12" md="3">
                      <VTextField v-model="form.backup_webdav_login" label="账号"
                        :disabled="!form.backup_webdav_enabled" />
                    </VCol>
                    <VCol cols="12" md="3">
                      <VTextField v-model="form.backup_webdav_password" label="密码"
                        type="password" :disabled="!form.backup_webdav_enabled" />
                    </VCol>
                  </VRow>
                </SettingSection>
                <SettingSection title="远端策略" note="保留份数、通知渠道和连接校验">
                  <VRow class="aoa-setting-grid">
                    <VCol cols="12" md="4">
                      <VSelect v-model="form.backup_webdav_max_count" :items="keepCountPresets"
                        label="远端保留份数" :disabled="!form.backup_webdav_enabled" />
                    </VCol>
                    <VCol cols="12" md="4">
                      <VSwitch v-model="form.backup_webdav_notify" color="primary" inset hide-details
                        label="远端备份结果通知" :disabled="!form.backup_webdav_enabled" />
                    </VCol>
                    <VCol cols="12" md="4">
                      <VSelect v-model="form.backup_webdav_notify_type" :items="notificationTypeItems"
                        label="消息类型" :disabled="!form.backup_webdav_enabled || !form.backup_webdav_notify" />
                    </VCol>
                    <VCol cols="12" md="4">
                      <VSwitch v-model="form.backup_webdav_digest_auth" color="primary" inset hide-details
                        label="使用 Digest 认证" :disabled="!form.backup_webdav_enabled" />
                    </VCol>
                    <VCol cols="12" md="8">
                      <VSwitch v-model="form.backup_webdav_disable_check" color="warning" inset hide-details
                        label="跳过证书校验（自签名时启用）" :disabled="!form.backup_webdav_enabled" />
                    </VCol>
                  </VRow>
                </SettingSection>
              </VForm>
            </div>
            <!-- 日志清理 · 插件日志 -->
            <div v-show="activeSub === 'logs'" class="aoa-pane">
              <VForm>
                <ModuleHero
                  v-model:enabled="form.log_clean_enabled"
                  icon="mdi-file-document-remove-outline"
                  kicker="MP 日志清理"
                  on-title="插件日志清理已启用"
                  off-title="插件日志清理未启用"
                  desc="按计划裁剪插件日志|保留排查信息和最近记录"
                  :count-label="`保留 ${form.log_clean_rows} 行`"
                />
                <SettingSection title="清理策略" note="清理时间、保留行数和限定插件">
                  <VRow class="aoa-setting-grid">
                    <VCol cols="12" md="4">
                      <VCronField v-model="form.log_clean_cron" label="清理时间 (Cron)"
                        :disabled="!form.log_clean_enabled" />
                    </VCol>
                    <VCol cols="12" md="4">
                      <VSelect v-model="form.log_clean_rows" :items="logRowsPresets"
                        label="保留行数" :disabled="!form.log_clean_enabled" />
                    </VCol>
                    <VCol cols="12" md="4">
                      <VSelect v-model="form.log_clean_selected_ids" :items="installedPlugins"
                        :loading="installedLoading" label="限定插件"
                        persistent-hint hint="留空＝全部插件"
                        multiple chips closable-chips clearable
                        prepend-inner-icon="mdi-puzzle-outline"
                        :disabled="!form.log_clean_enabled" />
                    </VCol>
                  </VRow>
                </SettingSection>
                <SettingSection title="通知与触发" note="清理完成通知和手动触发开关">
                  <VRow class="aoa-setting-grid">
                    <VCol cols="12" md="4">
                      <VSwitch v-model="form.log_clean_notify" color="primary" inset hide-details
                        label="清理结果通知" :disabled="!form.log_clean_enabled" />
                    </VCol>
                    <VCol cols="12" md="4">
                      <VSelect v-model="form.log_clean_notify_type" :items="notificationTypeItems"
                        label="消息类型" :disabled="!form.log_clean_enabled || !form.log_clean_notify" />
                    </VCol>
                    <VCol cols="12" md="4">
                      <VSwitch v-model="form.log_clean_onlyonce" color="warning" inset hide-details
                        label="保存后立即清理一次" :disabled="!form.log_clean_enabled" />
                    </VCol>
                  </VRow>
                </SettingSection>
              </VForm>
            </div>

            <!-- 更新检查 · 主程序 -->
            <div v-show="activeSub === 'mp'" class="aoa-pane">
              <VForm>
                <ModuleHero
                  v-model:enabled="form.mp_update_enabled"
                  icon="mdi-movie-open-cog-outline"
                  kicker="MP 更新检查"
                  on-title="主程序更新检查已启用"
                  off-title="主程序更新检查未启用"
                  desc="定时检查后端和前端版本|默认提醒，不直接升级"
                  :count-label="`${form.mp_update_types?.length || 0} 个范围`"
                />
                <SettingSection title="检查策略" note="检查时间、范围和通知渠道">
                  <VRow class="aoa-setting-grid">
                    <VCol cols="12" md="4">
                      <VCronField v-model="form.mp_update_cron" label="检查时间 (Cron)"
                        :disabled="!form.mp_update_enabled" />
                    </VCol>
                    <VCol cols="12" md="4">
                      <VSelect v-model="form.mp_update_types" :items="mpUpdateTypes"
                        label="检查范围" multiple chips closable-chips :disabled="!form.mp_update_enabled" />
                    </VCol>
                    <VCol cols="12" md="4">
                      <VSelect v-model="form.mp_update_notify_type" :items="notificationTypeItems"
                        label="消息类型" :disabled="!form.mp_update_enabled || !form.mp_update_notify" />
                    </VCol>
                    <VCol cols="12" md="6">
                      <VSwitch v-model="form.mp_update_notify" color="primary" inset hide-details
                        label="发现新版本时通知" :disabled="!form.mp_update_enabled" />
                    </VCol>
                    <VCol cols="12" md="6">
                      <VSwitch v-model="form.mp_update_restart_confirm" color="warning" inset hide-details
                        label="允许自动重启以应用更新（高风险，谨慎开启）" :disabled="!form.mp_update_enabled" />
                    </VCol>
                  </VRow>
                </SettingSection>
              </VForm>
            </div>

            <!-- 更新检查 · 插件库 -->
            <div v-show="activeSub === 'market'" class="aoa-pane">
              <VForm>
                <ModuleHero
                  v-model:enabled="form.market_update_enabled"
                  icon="mdi-puzzle-plus-outline"
                  kicker="MP 插件库"
                  on-title="插件库更新检查已启用"
                  off-title="插件库更新检查未启用"
                  desc="检查已安装插件新版本|按策略提醒或自动处理"
                  :count-label="form.market_update_auto_install ? '自动安装' : '仅提醒'"
                />
                <SettingSection title="检查策略" note="检查间隔、通知方式和插件库访问方式">
                  <VRow class="aoa-setting-grid">
                    <VCol cols="12" md="4">
                      <VSelect v-model="form.market_update_interval" :items="intervalPresets"
                        label="检查间隔" :disabled="!form.market_update_enabled" />
                    </VCol>
                    <VCol cols="12" md="4">
                      <VSelect v-model="form.market_update_notify_type" :items="marketNotifyItems"
                        label="通知消息类型" :disabled="!form.market_update_enabled" />
                    </VCol>
                    <VCol cols="12" md="4">
                      <VTextField v-model="form.market_update_timeout" label="请求超时（秒）"
                        type="number" min="1" :disabled="!form.market_update_enabled" />
                    </VCol>
                    <VCol cols="12" md="4">
                      <VSwitch v-model="form.market_update_notify" color="primary" inset hide-details
                        label="发现更新时通知" :disabled="!form.market_update_enabled" />
                    </VCol>
                    <VCol cols="12" md="4">
                      <VSwitch v-model="form.market_update_proxy" color="primary" inset hide-details
                        label="使用代理访问插件库" :disabled="!form.market_update_enabled" />
                    </VCol>
                    <VCol cols="12" md="4">
                      <VSwitch v-model="form.market_update_auto_get" color="primary" inset hide-details
                        label="自动抓取 Wiki 更新说明" :disabled="!form.market_update_enabled" />
                    </VCol>
                  </VRow>
                  <VExpansionPanels class="mt-2" variant="accordion">
                    <VExpansionPanel title="高级选项">
                      <VExpansionPanelText>
                        <VRow class="aoa-setting-grid">
                          <VCol cols="12" md="6">
                            <VSwitch v-model="form.market_update_write_settings" color="warning" inset hide-details
                              label="写回插件设置" :disabled="!form.market_update_enabled" />
                          </VCol>
                          <VCol cols="12" md="6">
                            <VSwitch v-model="form.market_update_write_env" color="warning" inset hide-details
                              label="写回环境变量" :disabled="!form.market_update_enabled" />
                          </VCol>
                          <VCol cols="12" md="6">
                            <VSwitch v-model="form.market_update_blacklist_enabled" color="primary" inset hide-details
                              label="启用更新黑名单" :disabled="!form.market_update_enabled" />
                          </VCol>
                          <VCol cols="12" md="6">
                            <VTextField v-model="form.market_update_wiki_url" label="Wiki 地址"
                              :disabled="!form.market_update_enabled" />
                          </VCol>
                          <VCol cols="12">
                            <VSelect v-model="form.market_update_blacklist" :items="pluginMarkets"
                              :loading="marketsLoading" label="黑名单插件库（不参与更新检查）"
                              multiple chips closable-chips clearable
                              prepend-inner-icon="mdi-block-helper"
                              no-data-text="未配置任何插件库"
                              :disabled="!form.market_update_enabled || !form.market_update_blacklist_enabled" />
                          </VCol>
                        </VRow>
                      </VExpansionPanelText>
                    </VExpansionPanel>
                  </VExpansionPanels>
                </SettingSection>
                <SettingSection title="自动更新已安装插件" note="控制自动安装范围和排除范围">
                  <VRow class="aoa-setting-grid">
                    <VCol cols="12" md="6">
                      <VSwitch v-model="form.market_update_auto_install" color="warning" inset hide-details
                        label="自动安装插件新版" :disabled="!form.market_update_enabled" />
                    </VCol>
                    <VCol cols="12" md="6">
                      <VSwitch v-model="form.market_update_skip_running" color="primary" inset hide-details
                        label="跳过正在运行的插件" :disabled="!form.market_update_enabled || !form.market_update_auto_install" />
                    </VCol>
                    <VCol cols="12">
                      <VSelect v-model="form.market_update_install_ids" :items="installedPlugins"
                        :loading="installedLoading" label="自动更新范围"
                        persistent-hint hint="留空＝全部已安装"
                        multiple chips closable-chips clearable prepend-inner-icon="mdi-puzzle-check-outline"
                        :disabled="!form.market_update_enabled || !form.market_update_auto_install" />
                    </VCol>
                    <VCol cols="12">
                      <VSelect v-model="form.market_update_exclude_ids" :items="installedPlugins"
                        :loading="installedLoading" label="排除插件"
                        persistent-hint hint="这些插件不自动更新"
                        multiple chips closable-chips clearable prepend-inner-icon="mdi-block-helper"
                        :disabled="!form.market_update_enabled || !form.market_update_auto_install" />
                    </VCol>
                  </VRow>
                </SettingSection>
              </VForm>
            </div>

            <!-- 插件卸载 · 卸载清理（合并单页） -->
            <div v-show="activeSub === 'clean'" class="aoa-pane">
              <VForm>
                <ModuleHero
                  :enabled="!!(form.plugin_uninstall_ids && form.plugin_uninstall_ids.length)"
                  icon="mdi-puzzle-remove-outline"
                  kicker="MP 插件卸载"
                  on-title="已选择卸载目标"
                  off-title="尚未选择卸载目标"
                  desc="统一处理插件卸载与配置清理|数据清理与本地源码残留"
                  :count-label="`${form.plugin_uninstall_ids?.length || 0} 个插件`"
                  state-on="待执行"
                  state-off="待选择"
                  :toggle="false"
                />
                <SettingSection title="目标插件" note="选择需要卸载或清理残留的已安装插件">
                  <VRow class="aoa-setting-grid">
                    <VCol cols="12">
                      <VSelect v-model="form.plugin_uninstall_ids" :items="installedPlugins"
                        :loading="installedLoading" label="选择要卸载的已安装插件"
                        multiple chips closable-chips clearable
                        prepend-inner-icon="mdi-puzzle-remove-outline" />
                    </VCol>
                  </VRow>
                </SettingSection>
                <SettingSection title="清理范围" note="卸载插件、清除配置和清除数据可独立选择">
                  <VRow class="aoa-setting-grid">
                    <VCol cols="12" md="4">
                      <VSwitch v-model="form.plugin_uninstall_remove_plugin" color="error" inset hide-details
                        label="卸载插件" />
                    </VCol>
                    <VCol cols="12" md="4">
                      <VSwitch v-model="form.plugin_uninstall_clear_config" color="primary" inset hide-details
                        label="清除插件配置" />
                    </VCol>
                    <VCol cols="12" md="4">
                      <VSwitch v-model="form.plugin_uninstall_clear_data" color="primary" inset hide-details
                        label="清除插件数据" />
                    </VCol>
                  </VRow>
                </SettingSection>
                <SettingSection title="通知与残留" note="清理结果通知和本地源码残留处理">
                  <VRow class="aoa-setting-grid">
                    <VCol cols="12" md="4">
                      <VSwitch v-model="form.plugin_uninstall_notify" color="primary" inset hide-details
                        label="清理结果通知" />
                    </VCol>
                    <VCol cols="12" md="4">
                      <VSelect v-model="form.plugin_uninstall_notify_type" :items="notificationTypeItems"
                        label="消息类型" :disabled="!form.plugin_uninstall_notify" />
                    </VCol>
                    <VCol cols="12" md="4">
                      <VSwitch v-model="form.plugin_uninstall_delete_source" color="error" inset hide-details
                        label="删除本地源码" />
                    </VCol>
                  </VRow>
                </SettingSection>
              </VForm>
            </div>

            <!-- 下载器管理 · 自动删种 -->
            <div v-show="activeSub === 'seedremove'" class="aoa-pane">
              <VForm class="aoa-seed-form">
                <ModuleHero
                  v-model:enabled="form.seedclean_enabled"
                  icon="mdi-delete-sweep-outline"
                  kicker="MP 下载器管理"
                  on-title="自动删种已启用"
                  off-title="自动删种未启用"
                  desc="按下载器、动作和筛选条件治理种子|未填写筛选条件时不会处理"
                  :count-label="`${seedFilterCount} 个条件`"
                />
                <SettingSection title="执行策略" note="执行周期、动作和下载器范围">
                  <VRow class="aoa-setting-grid aoa-seed-basic-row">
                    <VCol cols="12" md="6">
                      <VCronField v-model="form.seedclean_cron" label="执行周期 (Cron)"
                        :disabled="!form.seedclean_enabled" />
                    </VCol>
                    <VCol cols="12" md="6">
                      <VSelect v-model="form.seedclean_action" :items="seedActionItems"
                        hide-details label="动作" :disabled="!form.seedclean_enabled" />
                    </VCol>
                    <VCol cols="12">
                      <VSelect v-model="form.seedclean_downloaders" :items="downloaderOptions"
                        :loading="downloadersLoading" label="下载器（必选）"
                        multiple chips closable-chips clearable
                        hide-details
                        prepend-inner-icon="mdi-download-network-outline"
                        no-data-text="未配置下载器" :disabled="!form.seedclean_enabled" />
                    </VCol>
                  </VRow>
                </SettingSection>

                <SettingSection title="筛选条件" note="任一条件命中后按动作处理，未填写条件时跳过">
                  <VRow class="aoa-setting-grid aoa-seed-filter-grid">
                    <VCol cols="12" sm="6" md="4">
                      <VTextField v-model="form.seedclean_size" label="种子大小（GB）" hide-details
                        placeholder="1-10" :disabled="!form.seedclean_enabled" />
                    </VCol>
                    <VCol cols="12" sm="6" md="4">
                      <VTextField v-model="form.seedclean_ratio" label="分享率不小于" hide-details
                        placeholder="2" :disabled="!form.seedclean_enabled" />
                    </VCol>
                    <VCol cols="12" sm="6" md="4">
                      <VTextField v-model="form.seedclean_time" label="做种不少于（小时）" hide-details
                        placeholder="240" :disabled="!form.seedclean_enabled" />
                    </VCol>
                    <VCol cols="12" sm="6" md="4">
                      <VTextField v-model="form.seedclean_upspeed" label="均速上限（KB/s）" hide-details
                        placeholder="低于才处理" :disabled="!form.seedclean_enabled" />
                    </VCol>
                    <VCol cols="12" sm="6" md="4">
                      <VTextField v-model="form.seedclean_labels" label="标签" hide-details
                        placeholder="逗号分隔" :disabled="!form.seedclean_enabled" />
                    </VCol>
                    <VCol cols="12" sm="6" md="4">
                      <VTextField v-model="form.seedclean_torrentcategorys" label="任务分类" hide-details
                        placeholder="逗号分隔" :disabled="!form.seedclean_enabled" />
                    </VCol>
                    <VCol cols="12" sm="6" md="4">
                      <VTextField v-model="form.seedclean_pathkeywords" label="保存路径关键词" hide-details
                        placeholder="支持正则" :disabled="!form.seedclean_enabled" />
                    </VCol>
                    <VCol cols="12" sm="6" md="4">
                      <VTextField v-model="form.seedclean_trackerkeywords" label="Tracker 关键词" hide-details
                        placeholder="支持正则" :disabled="!form.seedclean_enabled" />
                    </VCol>
                    <VCol cols="12" sm="6" md="4">
                      <VTextField v-model="form.seedclean_torrentstates" label="任务状态（仅 QB）" hide-details
                        placeholder="pausedUP,stalledUP" :disabled="!form.seedclean_enabled" />
                    </VCol>
                    <VCol cols="12" sm="6" md="4">
                      <VTextField v-model="form.seedclean_errorkeywords" label="错误信息（仅 TR）" hide-details
                        placeholder="支持正则" :disabled="!form.seedclean_enabled" />
                    </VCol>
                  </VRow>
                </SettingSection>

                <SettingSection title="保护与通知" note="辅种保护、MoviePilot 任务限制和通知渠道">
                  <VRow class="aoa-setting-grid">
                    <VCol cols="12" md="8">
                      <div class="aoa-seed-options">
                        <VSwitch v-model="form.seedclean_samedata" color="primary" inset hide-details
                          label="处理辅种" :disabled="!form.seedclean_enabled" />
                        <VSwitch v-model="form.seedclean_mponly" color="primary" inset hide-details
                          label="仅 MoviePilot 任务" :disabled="!form.seedclean_enabled" />
                        <VSwitch v-model="form.seedclean_notify" color="primary" inset hide-details
                          label="处理结果通知" :disabled="!form.seedclean_enabled" />
                      </div>
                    </VCol>
                    <VCol cols="12" md="4">
                      <VSelect v-model="form.seedclean_notify_type" :items="notificationTypeItems"
                        hide-details label="消息类型" :disabled="!form.seedclean_enabled || !form.seedclean_notify" />
                    </VCol>
                  </VRow>
                </SettingSection>
              </VForm>
            </div>
            <!-- 媒体通知 · 服务器通知 -->
            <div v-show="activeSub === 'server'" class="aoa-pane aoa-media-pane">
              <VForm class="aoa-media-form">
                <ModuleHero
                  v-model:enabled="form.msgnotify_enabled"
                  icon="mdi-television-play"
                  kicker="MP 媒体通知"
                  on-title="媒体服务器通知已启用"
                  off-title="媒体服务器通知未启用"
                  desc="监听 Emby、Jellyfin、Plex 事件|按媒体服务器规则推送"
                  :count-label="`${form.msgnotify_types?.length || 0} 类事件`"
                />
                <SettingSection title="通知范围" note="选择事件类型和媒体服务器范围">
                  <VRow class="aoa-setting-grid aoa-media-field-row">
                    <VCol cols="12" md="4">
                      <VSelect v-model="form.msgnotify_notify_type" :items="notificationTypeItems"
                        label="消息类型" prepend-inner-icon="mdi-message-badge-outline"
                        :disabled="!form.msgnotify_enabled" />
                    </VCol>
                    <VCol cols="12" md="8">
                      <VSelect v-model="form.msgnotify_types" :items="msgGroupItems"
                        label="通知哪些事件" multiple chips closable-chips clearable
                        prepend-inner-icon="mdi-bell-cog-outline"
                        :disabled="!form.msgnotify_enabled" />
                    </VCol>
                    <VCol cols="12">
                      <VSelect v-model="form.msgnotify_servers" :items="mediaserverOptions"
                        :loading="mediaserversLoading" label="媒体服务器范围"
                        persistent-hint hint="留空＝全部媒体服务器"
                        multiple chips closable-chips clearable
                        prepend-inner-icon="mdi-server-network"
                        no-data-text="未获取到媒体服务器"
                        :disabled="!form.msgnotify_enabled" />
                    </VCol>
                  </VRow>
                </SettingSection>
              </VForm>
            </div>
            <!-- 下载器助手 · 批量打标签 -->
            <div v-show="activeSub === 'dltagmain'" class="aoa-pane">
              <VForm class="aoa-dltag-form">
                <ModuleHero
                  v-model:enabled="form.dltag_enabled"
                  icon="mdi-tag-multiple-outline"
                  kicker="MP 下载器管理"
                  on-title="批量打标签已启用"
                  off-title="批量打标签未启用"
                  desc="遍历下载器种子并识别站点|按 tracker 所属站点补标签"
                  :count-label="`${form.dltag_downloaders?.length || 0} 个下载器`"
                />
                <SettingSection title="打标设置" note="选择下载器范围并配置标签前缀">
                  <VRow class="aoa-setting-grid aoa-dltag-field-row">
                    <VCol cols="12" md="7">
                      <VSelect v-model="form.dltag_downloaders" :items="downloaderOptions"
                        :loading="downloadersLoading" label="下载器范围"
                        persistent-hint hint="留空＝全部已配置"
                        multiple chips closable-chips clearable prepend-inner-icon="mdi-download-network-outline"
                        :disabled="!form.dltag_enabled" />
                    </VCol>
                    <VCol cols="12" md="5">
                      <VTextField v-model="form.dltag_prefix" label="标签前缀（可选）" placeholder="如 站点-" clearable
                        :disabled="!form.dltag_enabled" />
                    </VCol>
                  </VRow>
                </SettingSection>
                <SettingSection title="通知设置" note="打标完成后按选择渠道通知">
                  <VRow class="aoa-setting-grid aoa-dltag-notify-row">
                    <VCol cols="12" md="4">
                      <VSwitch v-model="form.dltag_notify" color="primary" inset hide-details label="完成后通知"
                        :disabled="!form.dltag_enabled" />
                    </VCol>
                    <VCol cols="12" md="4">
                      <VSelect v-model="form.dltag_notify_type" :items="notificationTypeItems"
                        label="消息类型" :disabled="!form.dltag_enabled || !form.dltag_notify" />
                    </VCol>
                  </VRow>
                </SettingSection>
              </VForm>
            </div>
          </div>
          <div v-if="activeActionItems.length" class="aoa-action-dock">
            <div class="aoa-action-dock-list">
              <div v-for="item in activeActionItems" :key="item.path" class="aoa-action-dock-item">
                <VBtn
                  size="small"
                  :color="item.color || 'primary'"
                  variant="tonal"
                  :prepend-icon="item.icon"
                  class="aoa-action-btn text-none"
                  :disabled="item.disabled"
                  :loading="action.running === item.path"
                  @click="runAction(item.path, item.label)"
                >
                  {{ item.label }}
                </VBtn>
                <span class="aoa-action-note">{{ item.note }}</span>
              </div>
            </div>
          </div>
        </section>
      </div>
      <VDivider class="aoa-hairline" />
      <VCardActions class="aoa-actions">
        <VFadeTransition>
          <span v-if="action.message" :class="action.ok ? 'text-success' : 'text-error'" class="text-caption">
            {{ action.message }}
          </span>
        </VFadeTransition>
        <VSpacer />
        <VBtn variant="text" @click="emit('close')">取消</VBtn>
        <VBtn color="primary" variant="flat" prepend-icon="mdi-content-save-outline" @click="saveConfig">保存配置</VBtn>
      </VCardActions>
    </VCard>
  </div>
</template>
<style>
.aoa-config-scroll-host {
  -ms-overflow-style: auto;
}
.aoa-config-scroll-host::-webkit-scrollbar {
  width: 1px !important;
  height: 1px !important;
  background: transparent !important;
}
.aoa-config-scroll-host::-webkit-scrollbar-track,
.aoa-config-scroll-host::-webkit-scrollbar-track-piece {
  background: transparent !important;
}
.aoa-config-scroll-host::-webkit-scrollbar-thumb {
  border-radius: 999px !important;
  border: 0 !important;
  background: rgba(var(--v-theme-on-surface), 0.14) !important;
}
.aoa-config-scroll-host::-webkit-scrollbar-thumb:hover {
  background: rgba(var(--v-theme-on-surface), 0.22) !important;
}
.aoa-config-scroll-host::-webkit-scrollbar-button,
.aoa-config-scroll-host::-webkit-scrollbar-corner {
  display: none !important;
  width: 0 !important;
  height: 0 !important;
  appearance: none !important;
  background: transparent !important;
  opacity: 0 !important;
}
@supports (-moz-appearance: none) {
  .aoa-config-scroll-host {
    scrollbar-width: thin;
    scrollbar-color: rgba(var(--v-theme-on-surface), 0.14) transparent;
  }
}
</style>

<style scoped>
.aoa-config {
  --aoa-pane-x: 24px;
  --aoa-pane-y: 22px;
  --aoa-pane-bottom: 20px;
  --aoa-block-gap: 18px;
  --aoa-section-pad: 18px;
  --aoa-section-gap: 14px;
  --aoa-grid-gutter-x: 18px;
  --aoa-grid-gutter-y: 14px;
  --aoa-control-radius: 14px;
  --aoa-hairline-alpha: 0.045;
  --aoa-scrollbar-size: 1px;
  --aoa-scrollbar-alpha: 0.14;
  --aoa-scrollbar-hover-alpha: 0.22;
  padding: 10px;
  font-size: 14px;
}
.aoa-config::-webkit-scrollbar,
.aoa-config :deep(*)::-webkit-scrollbar {
  width: var(--aoa-scrollbar-size) !important;
  height: var(--aoa-scrollbar-size) !important;
  background: transparent !important;
}
.aoa-config::-webkit-scrollbar-track,
.aoa-config :deep(*)::-webkit-scrollbar-track {
  background: transparent !important;
}
.aoa-config::-webkit-scrollbar-thumb,
.aoa-config :deep(*)::-webkit-scrollbar-thumb {
  border-radius: 999px;
  border: 0 !important;
  background: rgba(var(--v-theme-on-surface), var(--aoa-scrollbar-alpha)) !important;
}
.aoa-config::-webkit-scrollbar-thumb:hover,
.aoa-config :deep(*)::-webkit-scrollbar-thumb:hover {
  background: rgba(var(--v-theme-on-surface), var(--aoa-scrollbar-hover-alpha)) !important;
}
.aoa-config::-webkit-scrollbar-corner,
.aoa-config :deep(*)::-webkit-scrollbar-corner {
  background: transparent !important;
}
.aoa-config::-webkit-scrollbar-button,
.aoa-config :deep(*)::-webkit-scrollbar-button {
  display: none !important;
  width: 0 !important;
  height: 0 !important;
  appearance: none !important;
  background: transparent !important;
  opacity: 0 !important;
}
.aoa-config::-webkit-scrollbar-track-piece,
.aoa-config :deep(*)::-webkit-scrollbar-track-piece {
  background: transparent !important;
}
.aoa-window,
.aoa-report-table-scroll,
.aoa-nav-scroll,
.aoa-subtab-list {
  -ms-overflow-style: auto;
}
.aoa-window::-webkit-scrollbar,
.aoa-report-table-scroll::-webkit-scrollbar,
.aoa-nav-scroll::-webkit-scrollbar,
.aoa-subtab-list::-webkit-scrollbar {
  width: var(--aoa-scrollbar-size) !important;
  height: var(--aoa-scrollbar-size) !important;
  background: transparent !important;
}
.aoa-window::-webkit-scrollbar-track,
.aoa-report-table-scroll::-webkit-scrollbar-track,
.aoa-nav-scroll::-webkit-scrollbar-track,
.aoa-subtab-list::-webkit-scrollbar-track,
.aoa-window::-webkit-scrollbar-track-piece,
.aoa-report-table-scroll::-webkit-scrollbar-track-piece,
.aoa-nav-scroll::-webkit-scrollbar-track-piece,
.aoa-subtab-list::-webkit-scrollbar-track-piece {
  background: transparent !important;
}
.aoa-window::-webkit-scrollbar-thumb,
.aoa-report-table-scroll::-webkit-scrollbar-thumb,
.aoa-nav-scroll::-webkit-scrollbar-thumb,
.aoa-subtab-list::-webkit-scrollbar-thumb {
  border-radius: 999px !important;
  border: 0 !important;
  background: rgba(var(--v-theme-on-surface), var(--aoa-scrollbar-alpha)) !important;
}
.aoa-window::-webkit-scrollbar-thumb:hover,
.aoa-report-table-scroll::-webkit-scrollbar-thumb:hover,
.aoa-nav-scroll::-webkit-scrollbar-thumb:hover,
.aoa-subtab-list::-webkit-scrollbar-thumb:hover {
  background: rgba(var(--v-theme-on-surface), var(--aoa-scrollbar-hover-alpha)) !important;
}
.aoa-window::-webkit-scrollbar-button,
.aoa-report-table-scroll::-webkit-scrollbar-button,
.aoa-nav-scroll::-webkit-scrollbar-button,
.aoa-subtab-list::-webkit-scrollbar-button,
.aoa-window::-webkit-scrollbar-corner,
.aoa-report-table-scroll::-webkit-scrollbar-corner,
.aoa-nav-scroll::-webkit-scrollbar-corner,
.aoa-subtab-list::-webkit-scrollbar-corner {
  display: none !important;
  width: 0 !important;
  height: 0 !important;
  appearance: none !important;
  background: transparent !important;
  opacity: 0 !important;
}
@supports (-moz-appearance: none) {
  .aoa-config,
  .aoa-config :deep(*),
  .aoa-window,
  .aoa-report-table-scroll,
  .aoa-nav-scroll,
  .aoa-nav-scroll :deep(*),
  .aoa-subtab-list,
  .aoa-subtab-list :deep(*) {
    scrollbar-width: thin;
    scrollbar-color: rgba(var(--v-theme-on-surface), var(--aoa-scrollbar-alpha)) transparent;
  }
}
.aoa-card {
  display: flex;
  flex-direction: column;
  max-height: calc(100vh - 20px);
  border-radius: 18px;
  overflow: hidden;
  border: 1px solid rgba(var(--v-border-color), 0.075);
  background:
    linear-gradient(180deg, rgba(var(--v-theme-surface), 0.72), rgba(var(--v-theme-surface), 0.54)),
    rgba(var(--v-theme-on-surface), 0.016);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
}
.aoa-hairline {
  display: block;
  flex: 0 0 1px;
  height: 1px;
  min-height: 1px;
  margin: 0;
  opacity: 1 !important;
  border: 0 !important;
  background:
    linear-gradient(
      90deg,
      transparent 0%,
      rgba(var(--v-border-color), var(--aoa-hairline-alpha)) 14%,
      rgba(var(--v-border-color), var(--aoa-hairline-alpha)) 86%,
      transparent 100%
    );
}
.aoa-hairline.v-divider--horizontal {
  height: 1px;
  min-height: 1px;
  border: 0 !important;
}
.aoa-hairline.v-divider--vertical {
  width: 1px;
  min-width: 1px;
  border: 0 !important;
  background:
    linear-gradient(
      180deg,
      transparent 0%,
      rgba(var(--v-border-color), var(--aoa-hairline-alpha)) 14%,
      rgba(var(--v-border-color), var(--aoa-hairline-alpha)) 86%,
      transparent 100%
    );
}
.aoa-header {
  padding: 16px 20px;
}
.aoa-header-controls {
  min-width: 0;
  flex-wrap: wrap;
  justify-content: flex-end;
}
.aoa-header-switch {
  flex: 0 0 auto;
}
.aoa-header-switch :deep(.v-label) {
  font-size: 13px;
  opacity: 0.78;
}
.aoa-header-link {
  min-width: 0;
  height: 32px;
  padding: 0 10px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 600;
  transition: background-color 160ms ease, box-shadow 160ms ease;
}
.aoa-header-link :deep(.v-btn__prepend) {
  margin-inline-end: 5px;
}
.aoa-header-link:hover,
.aoa-header-link:focus-visible {
  background: rgba(var(--v-theme-primary), 0.12);
  box-shadow: 0 6px 18px rgba(var(--v-theme-primary), 0.12);
}
.aoa-body {
  display: flex;
  flex: 1 1 auto;
  height: min(76vh, 690px);
  min-height: 540px;
  overflow: hidden;
}
.aoa-nav {
  position: relative;
  width: 208px;
  flex: 0 0 208px;
  border-right: 1px solid rgba(var(--v-border-color), var(--aoa-hairline-alpha));
  background: rgba(var(--v-theme-on-surface), 0.012);
}
.aoa-nav-scroll {
  height: 100%;
  overflow-y: auto;
  overflow-x: hidden;
  padding-bottom: 44px;
  -ms-overflow-style: auto;
}
.aoa-nav-scroll,
.aoa-nav-scroll :deep(*) {
  -ms-overflow-style: auto;
}
.aoa-nav-scroll::-webkit-scrollbar {
  width: var(--aoa-scrollbar-size) !important;
  height: var(--aoa-scrollbar-size) !important;
  background: transparent !important;
}
.aoa-nav-scroll::-webkit-scrollbar-thumb {
  border-radius: 999px;
  background: rgba(var(--v-theme-on-surface), var(--aoa-scrollbar-alpha)) !important;
}
.aoa-nav-scroll::-webkit-scrollbar-track,
.aoa-nav-scroll::-webkit-scrollbar-corner,
.aoa-nav-scroll::-webkit-scrollbar-button {
  appearance: none !important;
  width: 0 !important;
  height: 0 !important;
  background: transparent !important;
  display: none !important;
  opacity: 0 !important;
}
.aoa-nav-scroll :deep(*)::-webkit-scrollbar {
  width: var(--aoa-scrollbar-size) !important;
  height: var(--aoa-scrollbar-size) !important;
  background: transparent !important;
}
.aoa-nav-scroll :deep(*)::-webkit-scrollbar-thumb,
.aoa-nav-scroll :deep(*)::-webkit-scrollbar-track,
.aoa-nav-scroll :deep(*)::-webkit-scrollbar-corner,
.aoa-nav-scroll :deep(*)::-webkit-scrollbar-button {
  appearance: none !important;
  width: 0 !important;
  height: 0 !important;
  background: transparent !important;
  display: none !important;
  opacity: 0 !important;
}
.aoa-nav-item {
  margin: 3px 10px;
  min-height: 46px;
  border-radius: 12px;
}
.aoa-nav-item :deep(.v-list-item__prepend) {
  width: 30px;
  min-width: 30px;
  margin-inline-end: 12px;
  opacity: 1;
}
.aoa-nav-icon {
  width: 23px;
  height: 23px;
  color: rgba(var(--v-theme-on-surface), 0.88);
}
.aoa-nav-item.v-list-item--active {
  background: rgba(var(--v-theme-primary), 0.14);
}
.aoa-nav-item.v-list-item--active .aoa-nav-icon,
.aoa-nav-item.v-list-item--active :deep(.v-list-item-title) {
  color: rgb(var(--v-theme-primary));
}
.aoa-nav-item :deep(.v-list-item-title) {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.aoa-content {
  position: relative;
  flex: 1 1 auto;
  min-width: 0;
  min-height: 0;
  display: flex;
  flex-direction: column;
}
.aoa-subtabs {
  position: relative;
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 10px 14px;
}
.aoa-subtab-list {
  display: flex;
  flex: 0 1 auto;
  flex-wrap: wrap;
  gap: 6px;
  min-width: 0;
  max-width: 48%;
  max-height: 42px;
  overflow-x: hidden;
  overflow-y: auto;
  padding-bottom: 2px;
  -ms-overflow-style: auto;
}
.aoa-subtab-list,
.aoa-subtab-list :deep(*) {
  -ms-overflow-style: auto;
}
.aoa-subtab-list::-webkit-scrollbar {
  width: var(--aoa-scrollbar-size) !important;
  height: var(--aoa-scrollbar-size) !important;
  background: transparent !important;
}
.aoa-subtab-list::-webkit-scrollbar-thumb {
  border-radius: 999px;
  background: rgba(var(--v-theme-on-surface), var(--aoa-scrollbar-alpha)) !important;
}
.aoa-subtab-list::-webkit-scrollbar-track,
.aoa-subtab-list::-webkit-scrollbar-corner,
.aoa-subtab-list::-webkit-scrollbar-button {
  appearance: none !important;
  width: 0 !important;
  height: 0 !important;
  background: transparent !important;
  display: none !important;
  opacity: 0 !important;
}
.aoa-subtab-list :deep(*)::-webkit-scrollbar {
  width: var(--aoa-scrollbar-size) !important;
  height: var(--aoa-scrollbar-size) !important;
  background: transparent !important;
}
.aoa-subtab-list :deep(*)::-webkit-scrollbar-thumb,
.aoa-subtab-list :deep(*)::-webkit-scrollbar-track,
.aoa-subtab-list :deep(*)::-webkit-scrollbar-corner,
.aoa-subtab-list :deep(*)::-webkit-scrollbar-button {
  appearance: none !important;
  width: 0 !important;
  height: 0 !important;
  background: transparent !important;
  display: none !important;
  opacity: 0 !important;
}
.aoa-subtab {
  display: inline-flex;
  align-items: center;
  min-height: 34px;
  padding: 7px 15px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  color: rgba(var(--v-theme-on-surface), 0.7);
  background: transparent;
  border: none;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
  white-space: nowrap;
}
.aoa-subtab:hover {
  background: rgba(var(--v-theme-primary), 0.08);
  color: rgb(var(--v-theme-primary));
}
.aoa-subtab--active {
  background: rgba(var(--v-theme-primary), 0.14);
  color: rgb(var(--v-theme-primary));
  font-weight: 600;
}
.aoa-subtab-desc {
  display: block;
  flex: 0 0 auto;
  margin-left: auto;
  width: max-content;
  max-width: calc(100% - 220px);
  min-height: 36px;
  min-width: 0;
  padding-right: 6px;
  font-size: 13px;
  font-weight: 500;
  line-height: 36px;
  color: rgba(var(--v-theme-on-surface), 0.58);
  text-align: right;
  overflow: visible;
  text-overflow: clip;
  white-space: nowrap;
}
.aoa-window {
  flex: 1 1 auto;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
  padding-bottom: calc(var(--aoa-pane-bottom) + 14px);
}
.aoa-pane {
  padding: var(--aoa-pane-y) var(--aoa-pane-x) var(--aoa-pane-bottom);
}
.aoa-pane > form,
.aoa-columns-form,
.aoa-health-form,
.aoa-seed-form,
.aoa-media-form,
.aoa-dltag-form {
  display: grid;
  gap: var(--aoa-block-gap);
  width: 100%;
}
.aoa-setting-section {
  display: grid;
  gap: var(--aoa-section-gap);
  width: 100%;
  box-sizing: border-box;
  padding: var(--aoa-section-pad);
  border-radius: 18px;
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  background:
    linear-gradient(180deg, rgba(var(--v-theme-surface), 0.48), rgba(var(--v-theme-surface), 0.30)),
    rgba(var(--v-theme-on-surface), 0.018);
  box-shadow:
    inset 0 0 0 1px rgba(var(--v-border-color), 0.11),
    0 10px 26px rgba(var(--v-theme-on-surface), 0.022);
}
.aoa-setting-section-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding: 0 2px;
}
.aoa-setting-section-title {
  font-size: 14px;
  font-weight: 800;
  line-height: 1.35;
  color: rgba(var(--v-theme-on-surface), 0.88);
}
.aoa-setting-section-note {
  margin-top: 3px;
  max-width: 560px;
  font-size: 12px;
  line-height: 1.45;
  color: rgba(var(--v-theme-on-surface), 0.48);
  display: -webkit-box;
  overflow: hidden;
  text-overflow: ellipsis;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  text-wrap: balance;
}
.aoa-setting-section-body {
  min-width: 0;
}
.aoa-setting-grid {
  --aoa-row-x: var(--aoa-grid-gutter-x);
  --aoa-row-y: var(--aoa-grid-gutter-y);
  margin: calc(var(--aoa-row-y) / -2) calc(var(--aoa-row-x) / -2);
}
.aoa-setting-grid :deep(.v-col),
.aoa-pane :deep(.v-col) {
  padding:
    calc(var(--aoa-row-y, var(--aoa-grid-gutter-y)) / 2)
    calc(var(--aoa-row-x, var(--aoa-grid-gutter-x)) / 2);
}
.aoa-hint {
  font-size: 12px;
  line-height: 1.45;
  color: rgba(var(--v-theme-on-surface), 0.52);
  margin-top: 2px;
  display: -webkit-box;
  overflow: hidden;
  text-overflow: ellipsis;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  text-wrap: balance;
}
.aoa-pane :deep(.v-field) {
  border-radius: var(--aoa-control-radius);
  background: rgba(var(--v-theme-surface), 0.34);
  box-shadow: inset 0 0 0 1px rgba(var(--v-border-color), 0.06);
}
.aoa-pane :deep(.v-field__input) {
  row-gap: 6px;
}
.aoa-pane :deep(.v-select .v-field__input) {
  min-width: 0;
  align-content: center;
}
.aoa-pane :deep(.v-select .v-chip) {
  max-width: 100%;
  margin: 2px 4px 2px 0;
}
.aoa-pane :deep(.v-selection-control) {
  min-height: 44px;
}
.aoa-pane :deep(.v-divider) {
  margin: 4px 0 !important;
  opacity: 0;
}
.aoa-pane :deep(.v-alert) {
  border-radius: 18px;
  box-shadow: inset 0 0 0 1px rgba(var(--v-border-color), 0.12);
}
.aoa-pane :deep(.v-expansion-panels) {
  display: grid;
  gap: 12px;
}
.aoa-pane :deep(.v-expansion-panel) {
  border-radius: 18px !important;
  background:
    linear-gradient(180deg, rgba(var(--v-theme-surface), 0.42), rgba(var(--v-theme-surface), 0.25)),
    rgba(var(--v-theme-on-surface), 0.018) !important;
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  box-shadow: inset 0 0 0 1px rgba(var(--v-border-color), 0.09) !important;
}
.aoa-pane :deep(.v-expansion-panel-title) {
  min-height: 48px;
  font-size: 14px;
  font-weight: 750;
}
.aoa-line-hint {
  min-width: 0;
  display: -webkit-box;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: normal;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  text-wrap: balance;
}
.aoa-action-dock {
  flex: 0 0 auto;
  padding: 12px var(--aoa-pane-x) 16px;
  background:
    linear-gradient(180deg, rgba(var(--v-theme-surface), 0.16), rgba(var(--v-theme-surface), 0.26)),
    rgba(var(--v-theme-on-surface), 0.006);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  box-shadow: inset 0 1px 0 rgba(var(--v-border-color), 0.035);
}
.aoa-action-dock-list {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: calc(var(--aoa-grid-gutter-y) - 4px) var(--aoa-grid-gutter-x);
}
.aoa-action-dock-item {
  min-width: 0;
  display: inline-flex;
  align-items: center;
  gap: 10px;
}
.aoa-action-btn {
  min-height: 38px;
  border-radius: 999px;
  font-weight: 750;
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  background: rgba(var(--v-theme-surface), 0.46) !important;
  box-shadow:
    inset 0 0 0 1px rgba(var(--v-border-color), 0.12),
    0 8px 22px rgba(var(--v-theme-on-surface), 0.04);
  transition: background-color 160ms ease, box-shadow 160ms ease, color 160ms ease;
}
.aoa-action-btn:hover {
  background: rgba(var(--v-theme-primary), 0.12) !important;
  box-shadow:
    inset 0 0 0 1px rgba(var(--v-theme-primary), 0.20),
    0 10px 24px rgba(var(--v-theme-primary), 0.10);
}
.aoa-action-note {
  max-width: 240px;
  min-width: 150px;
  display: -webkit-box;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: normal;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  color: rgba(var(--v-theme-on-surface), 0.52);
  font-size: 12px;
  line-height: 1.38;
  text-wrap: balance;
}
.aoa-seed-options {
  min-height: 48px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--aoa-grid-gutter-x);
  align-items: center;
}
.aoa-seed-options :deep(.v-selection-control) {
  min-height: 42px;
}
.aoa-pane :deep(.aoa-module-hero) {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--aoa-block-gap);
  width: 100%;
  min-height: 116px;
  box-sizing: border-box;
  padding: 17px var(--aoa-section-pad);
  border-radius: 22px;
  color: rgba(var(--v-theme-on-surface), 0.92);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  background:
    radial-gradient(circle at 16% 0%, rgba(var(--v-theme-primary), 0.13), transparent 36%),
    linear-gradient(135deg, rgba(var(--v-theme-surface), 0.50), rgba(var(--v-theme-surface), 0.30)),
    rgba(var(--v-theme-on-surface), 0.018);
  box-shadow:
    inset 0 0 0 1px rgba(var(--v-border-color), 0.11),
    0 12px 30px rgba(var(--v-theme-on-surface), 0.028);
}
.aoa-pane :deep(.aoa-module-hero--off) {
  background:
    radial-gradient(circle at 16% 0%, rgba(var(--v-theme-warning), 0.11), transparent 36%),
    linear-gradient(135deg, rgba(var(--v-theme-surface), 0.46), rgba(var(--v-theme-surface), 0.28)),
    rgba(var(--v-theme-on-surface), 0.014);
  box-shadow:
    inset 0 0 0 1px rgba(var(--v-border-color), 0.10),
    0 10px 28px rgba(var(--v-theme-on-surface), 0.025);
}
.aoa-pane :deep(.aoa-module-heading) {
  min-width: 0;
  flex: 1 1 auto;
  display: flex;
  align-items: center;
  gap: 14px;
}
.aoa-pane :deep(.aoa-module-emblem) {
  width: 46px;
  height: 46px;
  flex: 0 0 46px;
  display: grid;
  place-items: center;
  border-radius: 17px;
  color: rgb(var(--v-theme-primary));
  background: rgba(var(--v-theme-surface), 0.44);
  box-shadow: inset 0 0 0 1px rgba(var(--v-theme-primary), 0.16);
}
.aoa-pane :deep(.aoa-module-heading-text) {
  min-width: 0;
  width: min(382px, 100%);
  display: grid;
  align-content: center;
}
.aoa-pane :deep(.aoa-module-kicker) {
  font-size: 12px;
  font-weight: 700;
  line-height: 1.18;
  color: rgba(var(--v-theme-on-surface), 0.58);
}
.aoa-pane :deep(.aoa-module-title) {
  margin-top: 4px;
  font-size: 18px;
  font-weight: 800;
  line-height: 1.2;
  letter-spacing: 0;
}
.aoa-pane :deep(.aoa-module-desc) {
  margin-top: 6px;
  max-width: 360px;
  min-height: 35px;
  font-size: 12.5px;
  line-height: 1.42;
  color: rgba(var(--v-theme-on-surface), 0.66);
  display: -webkit-box;
  overflow: hidden;
  text-overflow: ellipsis;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  text-wrap: balance;
  word-break: break-word;
}
.aoa-pane :deep(.aoa-module-state) {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  margin-left: auto;
  white-space: nowrap;
}
.aoa-pane :deep(.aoa-module-state .v-selection-control) {
  min-height: 34px;
}
.aoa-field-note {
  height: 100%;
  display: flex;
  align-items: center;
  margin-top: 0;
}
.aoa-health-scope-grid {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: var(--aoa-grid-gutter-y) var(--aoa-grid-gutter-x);
  align-items: stretch;
}
.aoa-health-field-third {
  grid-column: span 2;
}
.aoa-health-field-half {
  grid-column: span 3;
}
.aoa-health-field-full {
  grid-column: 1 / -1;
}
.aoa-health-selection-chip {
  flex: 0 0 auto;
  max-width: none;
  margin-inline-end: 4px;
  color: rgba(var(--v-theme-on-surface), 0.78);
}
.aoa-table-wrap {
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(var(--v-border-color), 0.10);
  border-radius: 16px;
  background:
    linear-gradient(180deg, rgba(var(--v-theme-surface), 0.22), rgba(var(--v-theme-surface), 0.14)),
    rgba(var(--v-theme-on-surface), 0.014);
}
.aoa-columns-pane {
  display: block;
  min-height: auto;
  box-sizing: border-box;
}
.aoa-columns-form {
  width: 100%;
  max-width: 100%;
  min-height: auto;
  grid-template-rows: none;
}
.aoa-columns-pane :deep(.aoa-module-hero),
.aoa-columns-pane .aoa-setting-section {
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
}
.aoa-columns-pane .aoa-table-wrap {
  display: block;
  width: 100%;
  max-width: 100%;
  min-height: auto;
}
.aoa-report-table-scroll {
  flex: 1 1 auto;
  min-height: 0;
  max-height: 430px;
  overflow: auto;
}
.aoa-columns-pane .aoa-report-table-scroll {
  max-height: none;
  overflow: visible;
}
.aoa-report-table {
  width: 100%;
  min-width: 0;
  font-size: 13px;
}
.aoa-report-table :deep(table) {
  width: 100%;
  min-width: 620px;
}
.aoa-report-table :deep(th) {
  position: sticky;
  top: 0;
  z-index: 1;
  height: 42px;
  padding: 0 14px;
  color: rgba(var(--v-theme-on-surface), 0.82);
  background: rgba(var(--v-theme-surface), 0.96);
  font-weight: 700;
  text-align: left;
}
.aoa-report-table :deep(td) {
  height: 50px;
  padding: 0 14px;
  color: rgba(var(--v-theme-on-surface), 0.74);
}
.aoa-report-table :deep(tbody tr) {
  transition: background 0.15s;
}
.aoa-report-table :deep(tbody tr:hover) {
  background: rgba(var(--v-theme-primary), 0.04);
}
.aoa-col-enable {
  width: 58px;
  text-align: center !important;
}
.aoa-table-strong {
  font-weight: 650;
  color: rgba(var(--v-theme-on-surface), 0.84) !important;
}
.aoa-table-note {
  color: rgba(var(--v-theme-on-surface), 0.46) !important;
  font-size: 12px;
}
.aoa-actions {
  padding: 12px 20px;
}
@media (max-width: 960px) {
  .aoa-report-table :deep(table) {
    min-width: 0;
    table-layout: fixed;
  }
  .aoa-report-table :deep(th),
  .aoa-report-table :deep(td) {
    padding-inline: 10px;
  }
  .aoa-report-table :deep(th:nth-child(1)),
  .aoa-report-table :deep(td:nth-child(1)) {
    width: 58px;
  }
  .aoa-report-table :deep(th:nth-child(2)),
  .aoa-report-table :deep(td:nth-child(2)) {
    width: 128px;
  }
  .aoa-report-table :deep(th:nth-child(3)),
  .aoa-report-table :deep(td:nth-child(3)) {
    width: 128px;
  }
  .aoa-report-table :deep(td) {
    white-space: normal;
    word-break: break-word;
  }
}
@media (max-width: 760px) {
  .aoa-config {
    --aoa-pane-x: 16px;
    --aoa-pane-y: 18px;
    --aoa-pane-bottom: 18px;
    --aoa-block-gap: 16px;
    --aoa-section-pad: 16px;
    --aoa-grid-gutter-x: 14px;
    --aoa-grid-gutter-y: 12px;
  }
  .aoa-header {
    padding: 12px 14px;
  }
  .aoa-header-title,
  .aoa-header-subtitle {
    display: none;
  }
  .aoa-header :deep(.v-card-item__append) {
    margin-inline-start: auto;
    padding-inline-start: 0;
  }
  .aoa-header :deep(.v-switch .v-label) {
    font-size: 13px;
    opacity: 0.78;
  }
  .aoa-header-controls {
    gap: 4px !important;
  }
  .aoa-header-link {
    height: 30px;
    padding: 0 8px;
  }
  .aoa-card {
    height: calc(100vh - 20px);
    max-height: calc(100vh - 20px);
  }
  .aoa-body {
    height: auto;
    min-height: 0;
    flex-direction: column;
  }
  .aoa-nav {
    width: 100%;
    flex: 0 0 180px;
    height: 180px;
    min-height: 0;
    overflow: hidden;
    border-right: none;
    border-bottom: 1px solid rgba(var(--v-border-color), var(--aoa-hairline-alpha));
  }
  .aoa-nav-scroll {
    height: 100%;
    padding-bottom: 40px;
  }
  .aoa-content {
    flex: 1 1 auto;
    min-height: 0;
  }
  .aoa-subtabs {
    align-items: flex-start;
    flex-direction: column;
    padding-right: 48px;
  }
  .aoa-subtab-list {
    max-width: 100%;
    width: 100%;
  }
  .aoa-subtab-desc {
    max-width: 100%;
    width: 100%;
    min-height: 0;
    padding-right: 0;
    line-height: 1.4;
    text-align: left;
  }
  .aoa-action-dock {
    padding: 8px var(--aoa-pane-x) 14px;
  }
  .aoa-action-dock-list {
    align-items: flex-start;
    flex-direction: column;
    gap: 10px;
  }
  .aoa-action-dock-item {
    width: 100%;
    align-items: flex-start;
    flex-direction: column;
    gap: 6px;
  }
  .aoa-action-note {
    max-width: 100%;
  }
  .aoa-pane {
    padding: var(--aoa-pane-y) var(--aoa-pane-x) var(--aoa-pane-bottom);
  }
  .aoa-report-table :deep(table),
  .aoa-report-table :deep(tbody) {
    display: block;
    width: 100%;
    min-width: 0;
  }
  .aoa-report-table :deep(thead) {
    display: none;
  }
  .aoa-report-table :deep(tbody) {
    display: grid;
    gap: 10px;
  }
  .aoa-report-table :deep(tr) {
    display: grid;
    grid-template-columns: 36px minmax(0, 1fr);
    grid-auto-rows: min-content;
    align-items: start;
    gap: 5px 10px;
    width: 100%;
    min-width: 0;
    padding: 12px;
    border-radius: 14px;
    background:
      linear-gradient(180deg, rgba(var(--v-theme-surface), 0.34), rgba(var(--v-theme-surface), 0.20)),
      rgba(var(--v-theme-on-surface), 0.010);
    box-shadow: inset 0 0 0 1px rgba(var(--v-border-color), 0.09);
  }
  .aoa-report-table :deep(td) {
    display: flex;
    align-items: center;
    width: auto !important;
    min-width: 0;
    max-width: 100%;
    height: auto;
    padding: 0;
    border-bottom: 0 !important;
  }
  .aoa-report-table :deep(td)::before {
    display: none;
  }
  .aoa-report-table :deep(td.aoa-col-enable) {
    grid-column: 1;
    grid-row: 1 / span 3;
    width: 36px !important;
    align-self: stretch;
    justify-content: center;
  }
  .aoa-report-table :deep(td.aoa-col-enable)::before {
    display: none;
  }
  .aoa-report-table :deep(td:not(.aoa-col-enable)) {
    grid-column: 2;
  }
  .aoa-report-table :deep(td[data-label="组件"]) {
    grid-row: 1;
    align-items: flex-start;
  }
  .aoa-report-table :deep(td[data-label="栏目"]) {
    grid-row: 2;
    align-items: flex-start;
    color: rgba(var(--v-theme-on-surface), 0.86) !important;
    font-size: 14px;
    line-height: 1.35;
  }
  .aoa-report-table :deep(td[data-label="备注"]) {
    grid-row: 3;
    align-items: flex-start;
    color: rgba(var(--v-theme-on-surface), 0.52) !important;
    line-height: 1.35;
  }
  .aoa-report-table :deep(td[data-label="备注"] span) {
    min-width: 0;
    overflow-wrap: anywhere;
  }
  .aoa-report-table :deep(.v-chip) {
    max-width: 100%;
    height: 24px;
  }
  .aoa-report-table :deep(.v-chip__content) {
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  .aoa-seed-options {
    grid-template-columns: 1fr;
  }
  .aoa-pane :deep(.aoa-module-hero),
  .aoa-pane :deep(.aoa-module-state),
  .aoa-setting-section-head {
    align-items: stretch;
    flex-direction: column;
  }
  .aoa-pane :deep(.aoa-module-state) {
    justify-content: flex-start;
    white-space: normal;
  }
  .aoa-health-scope-grid {
    grid-template-columns: 1fr;
  }
  .aoa-health-field-third,
  .aoa-health-field-half {
    grid-column: 1 / -1;
  }
}
</style>
