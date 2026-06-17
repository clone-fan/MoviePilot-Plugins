<script setup>
import { reactive, ref, computed, watch, onMounted } from 'vue'
import { postPluginApi, getPluginApi } from './api'

const props = defineProps({
  api: { type: [Object, Function], default: null },
  initialConfig: { type: Object, default: () => ({}) },
})
const emit = defineEmits(['save', 'close', 'switch'])

const form = reactive({})
const activeMain = ref('report')
const activeSub = ref('overview')

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

// 已安装插件（残留清理 / 日志限定 共用）
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
  dltag_enabled: false,
  dltag_downloaders: [],
  dltag_prefix: '',
  dltag_notify: true,
  dltag_notify_type: 'Plugin',
}

const mainTabs = [
  { key: 'report', group: '汇报中心', title: '每日汇报', icon: 'mdi-newspaper-variant-outline', desc: '控制日报发送节奏、手动推送和所有并入日报的栏目' },
  { key: 'subreminder', group: '订阅与站点', title: '订阅管理', icon: 'mdi-bell-cog-outline', desc: '订阅追新与订阅规则填充统一管理' },
  { key: 'sitestat', group: '订阅与站点', title: '站点数据统计', icon: 'mdi-chart-line', desc: '提供仪表盘站点数据，以及日报里的站点状态、站点增量栏目' },
  { key: 'seedclean', group: '下载与媒体', title: '下载器管理', icon: 'mdi-download-network-outline', desc: '集中管理下载器相关能力：自动删种、种子批量打标签与下载器活动概览' },
  { key: 'msgnotify', group: '下载与媒体', title: '媒体通知', icon: 'mdi-television-play', desc: 'Emby/Jellyfin/Plex 的播放、入库、登录等 webhook 事件推送通知' },
  { key: 'healthcheck', group: '系统维护', title: '健康巡查', icon: 'mdi-heart-pulse', desc: '定期检查系统健康状态（数据库、存储、目录等），发现问题及时通知' },
  { key: 'backup', group: '系统维护', title: '自动备份', icon: 'mdi-archive-arrow-up-outline', desc: '设置本地备份、保留数量和 WebDAV 远端备份' },
  { key: 'cleanup', group: '系统维护', title: '日志清理', icon: 'mdi-file-document-remove-outline', desc: '设置插件日志保留行数、清理时间和结果通知' },
  { key: 'updates', group: '系统维护', title: '更新检查', icon: 'mdi-update', desc: '检查 MoviePilot 与插件库更新，可自动更新已安装插件' },
  { key: 'plugin', group: '系统维护', title: '插件残留清理', icon: 'mdi-puzzle-remove-outline', desc: '清理已卸载插件留下的配置、数据、日志或本地源码残留' },
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
    { key: 'clean', title: '残留清理', icon: 'mdi-broom' },
  ],
  seedclean: [
    { key: 'seedremove', title: '种子治理', icon: 'mdi-delete-sweep-outline' },
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
const healthSelectedCount = computed(() => {
  const selected = Array.isArray(form.health_check_items) ? form.health_check_items : []
  return selected.length || healthCheckItems.length
})
function healthItemActive(value) {
  const selected = Array.isArray(form.health_check_items) ? form.health_check_items : []
  return selected.length === 0 || selected.includes(value)
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
}, { immediate: true, deep: true })

function saveConfig() {
  emit('save', { ...form })
}

function selectMain(key) {
  if (activeMain.value === key) return
  activeMain.value = key
  activeSub.value = subTabs[key]?.[0]?.key || ''
}

onMounted(() => {
  loadInstalledPlugins()
  loadPluginMarkets()
  loadDownloaders()
  loadMediaservers()
})
</script>
<template>
  <div class="aoa-config">
    <VCard flat class="aoa-card">
      <VCardItem class="aoa-header">
        <template #prepend>
          <VAvatar color="primary" variant="tonal" size="44" rounded="lg">
            <VIcon icon="mdi-shield-sync-outline" size="24" />
          </VAvatar>
        </template>
        <VCardTitle class="text-h6">MP 运维助手</VCardTitle>
        <VCardSubtitle class="text-caption">配置中心</VCardSubtitle>
        <template #append>
          <div class="d-flex align-center ga-2">
            <VSwitch
              v-model="form.enabled"
              color="primary"
              hide-details
              inset
              :label="form.enabled ? '已启用' : '已停用'"
            />
            <VBtn size="small" variant="text" color="primary" prepend-icon="mdi-view-dashboard-outline" class="text-none aoa-header-link" @click="emit('switch')">
              仪表盘
            </VBtn>
            <VBtn icon="mdi-close" variant="text" @click="emit('close')" />
          </div>
        </template>
      </VCardItem>
      <VDivider />
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
          <VDivider />
          <div class="aoa-window">
            <!-- 每日汇报 · 汇报总览 -->
            <div v-show="activeSub === 'overview'" class="aoa-pane">
              <VForm>
                <div class="aoa-section-title">汇报开关</div>
                <VRow>
                  <VCol cols="12" md="6">
                    <VSwitch v-model="form.daily_report_enabled" color="primary" inset hide-details
                      label="启用定时每日汇报" />
                    <div class="aoa-hint">关闭后将不再按计划自动发送汇报，仍可在下方手动触发</div>
                  </VCol>
                  <VCol cols="12" md="6">
                    <VCronField v-model="form.daily_report_cron" label="汇报时间 (Cron)"
                      :disabled="!form.daily_report_enabled" />
                  </VCol>
                </VRow>
                <VRow>
                  <VCol cols="12" md="6">
                    <VTextField v-model="form.daily_report_greeting" label="汇报称呼"
                      placeholder="少爷" prepend-inner-icon="mdi-account-heart-outline"
                      persistent-hint hint="汇报开头与提醒中对你的称呼，留空默认“少爷”" clearable />
                  </VCol>
                  <VCol cols="12" md="6">
                    <VSelect v-model="form.daily_report_msgtype" :items="notificationTypeItems"
                      label="消息类型" :disabled="!form.daily_report_enabled" />
                  </VCol>
                </VRow>

                <VDivider class="my-4" />
                <div class="aoa-section-title">手动触发</div>
                <div class="aoa-btn-row">
                  <VBtn color="primary" variant="tonal" prepend-icon="mdi-send-outline"
                    :loading="action.running === 'run_daily_report'" @click="runAction('run_daily_report', '发送每日汇报')">
                    立即发送汇报
                  </VBtn>
                  <VBtn color="primary" variant="tonal" prepend-icon="mdi-heart-pulse"
                    :loading="action.running === 'run_health_check'" @click="runAction('run_health_check', '健康巡查')">
                    立即健康巡查
                  </VBtn>
                </div>
              </VForm>
            </div>

            <!-- 每日汇报 · 汇报栏目 -->
            <div v-show="activeSub === 'columns'" class="aoa-pane">
              <VForm>
                <div class="aoa-section-title">汇报栏目</div>
                <div class="aoa-hint mb-3">所有并入日报的栏目都在这里统一勾选，组件负责能力，栏目负责出现在日报里的内容</div>
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
                          <td class="aoa-col-enable">
                            <VCheckbox
                              v-model="form[s.key]"
                              color="primary"
                              hide-details
                              density="compact"
                              :disabled="s.requires && !form[`${s.requires}_enabled`]"
                            />
                          </td>
                          <td>
                            <VChip size="small" variant="tonal" color="primary">{{ s.component }}</VChip>
                          </td>
                          <td class="aoa-table-strong">{{ s.label }}</td>
                          <td class="aoa-table-note">
                            <span v-if="s.requires && !form[`${s.requires}_enabled`]">需启用对应组件</span>
                            <span v-else>{{ s.note }}</span>
                          </td>
                        </tr>
                      </tbody>
                    </VTable>
                  </div>
                </div>
              </VForm>
            </div>

            <!-- 订阅与站点 · 订阅追新 -->
            <div v-show="activeSub === 'subscribe'" class="aoa-pane">
              <VForm>
                <div class="aoa-section-title">订阅追新</div>
                <VRow>
                  <VCol cols="12">
                    <VSwitch v-model="form.subscribe_reminder_enabled" color="primary" inset hide-details
                      label="启用独立订阅追新推送" />
                    <div class="aoa-hint">在指定时间单独推送订阅追新，是否并入每日汇报见「汇报栏目」</div>
                  </VCol>
                </VRow>
                <VRow>
                  <VCol cols="12" md="4">
                    <VCronField v-model="form.subscribe_reminder_cron" label="推送时间 (Cron)"
                      :disabled="!form.subscribe_reminder_enabled" />
                  </VCol>
                  <VCol cols="12" md="4">
                    <VSelect v-model="form.subscribe_reminder_subtype" :items="subscribeSubtypeItems"
                      label="提醒类型" multiple chips closable-chips :disabled="!form.subscribe_reminder_enabled" />
                  </VCol>
                  <VCol cols="12" md="4">
                    <VSelect v-model="form.subscribe_reminder_msgtype" :items="messageTypeItems"
                      label="消息类型" :disabled="!form.subscribe_reminder_enabled" />
                  </VCol>
                </VRow>
                <VDivider class="my-4" />
                <div class="aoa-section-title">手动触发</div>
                <div class="aoa-hint mb-2">立即按当前设置推送一次今日订阅追新（独立于每日汇报）</div>
                <div class="aoa-btn-row">
                  <VBtn color="primary" variant="tonal" prepend-icon="mdi-bell-ring-outline"
                    :loading="action.running === 'run_subscribe_reminder'" @click="runAction('run_subscribe_reminder', '订阅追新')">
                    立即推送订阅追新
                  </VBtn>
                </div>
              </VForm>
            </div>

            <!-- 每日汇报 · 站点数据统计 -->
            <div v-show="activeSub === 'sites'" class="aoa-pane">
              <VForm>
                <div class="aoa-section-title">站点数据统计</div>
                <VRow>
                  <VCol cols="12">
                    <VSwitch v-model="form.site_stat_enabled" color="primary" inset hide-details
                      label="启用站点数据统计采集" />
                    <div class="aoa-hint">关闭后不再统计站点数据（是否并入每日汇报见基础设置）</div>
                  </VCol>
                </VRow>
                <VRow>
                  <VCol cols="12" md="6">
                    <VSelect v-model="form.site_stat_dashboard_type" :items="siteStatRangeItems"
                      label="统计数据范围" :disabled="!form.site_stat_enabled" />
                  </VCol>
                  <VCol cols="12" md="6">
                    <VSelect v-model="form.site_stat_notify_type" :items="siteNotifyItems"
                      label="通知方式" :disabled="!form.site_stat_enabled" />
                  </VCol>
                </VRow>
              </VForm>
            </div>

            <!-- 系统维护 · 健康巡查 -->
            <div v-show="activeSub === 'hc'" class="aoa-pane">
              <VForm class="aoa-health-form">
                <div class="aoa-health-hero" :class="{ 'aoa-health-hero--off': !form.health_check_enabled }">
                  <div class="aoa-health-heading">
                    <div class="aoa-health-emblem">
                      <VIcon icon="mdi-heart-pulse" size="28" />
                    </div>
                    <div class="aoa-health-heading-text">
                      <div class="aoa-health-kicker">MP 健康巡查</div>
                      <div class="aoa-health-title">{{ form.health_check_enabled ? '自动巡查已启用' : '自动巡查未启用' }}</div>
                      <div class="aoa-health-desc">数据库、存储空间、目录权限按计划检查，异常时进入通知链路</div>
                    </div>
                  </div>
                  <div class="aoa-health-state">
                    <VChip size="small" :color="form.health_check_enabled ? 'success' : 'warning'" variant="flat">
                      {{ form.health_check_enabled ? '运行中' : '待启用' }}
                    </VChip>
                    <VChip size="small" color="primary" variant="tonal">{{ healthSelectedCount }} 项巡查</VChip>
                    <VSwitch v-model="form.health_check_enabled" color="primary" inset hide-details label="启用" />
                  </div>
                </div>

                <div class="aoa-health-grid">
                  <div v-for="item in healthCheckItems" :key="item.value"
                    class="aoa-health-check" :class="{ 'aoa-health-check--active': healthItemActive(item.value) }">
                    <VIcon :icon="item.icon" size="24" class="aoa-health-check-icon" />
                    <div class="aoa-health-check-text">
                      <div class="aoa-health-check-title">{{ item.title }}</div>
                      <div class="aoa-health-check-desc">{{ item.desc }}</div>
                    </div>
                  </div>
                </div>

                <div class="aoa-health-controls">
                  <div class="aoa-health-control aoa-health-cron">
                    <VCronField v-model="form.health_check_cron" label="巡查时间 (Cron)"
                      :disabled="!form.health_check_enabled" />
                  </div>
                  <div class="aoa-health-control aoa-health-select">
                    <VSelect v-model="form.health_check_items" :items="healthCheckItems"
                      label="巡查项目" multiple chips closable-chips clearable
                      :disabled="!form.health_check_enabled" />
                  </div>
                  <VBtn color="primary" variant="flat" prepend-icon="mdi-heart-pulse" class="aoa-health-run"
                    :loading="action.running === 'run_health_check'" @click="runAction('run_health_check', '健康巡查')">
                    立即巡查
                  </VBtn>
                </div>
              </VForm>
            </div>

            <!-- 每日汇报 · 订阅规则填充 -->
            <div v-show="activeSub === 'subfill'" class="aoa-pane">
              <VForm>
                <div class="aoa-section-title">订阅规则填充</div>
                <div class="aoa-hint mb-2">电视剧订阅下载到资源后，用实际规格自动回填订阅中“尚为空”的规则，锁定后续剧集追同款版本，已设置的字段不会被覆盖</div>
                <VRow>
                  <VCol cols="12" md="4">
                    <VSwitch v-model="form.subfill_enabled" color="primary" inset hide-details
                      label="启用订阅规则填充" />
                    <div class="aoa-hint">监听下载添加事件（仅电视剧），每个剧集 tmdbid 只填充一次</div>
                  </VCol>
                  <VCol cols="12" md="4">
                    <VSwitch v-model="form.subfill_notify" color="primary" inset hide-details
                      label="填充后发送通知" :disabled="!form.subfill_enabled" />
                  </VCol>
                  <VCol cols="12" md="4">
                    <VSelect v-model="form.subfill_notify_type" :items="notificationTypeItems"
                      label="消息类型" :disabled="!form.subfill_enabled || !form.subfill_notify" />
                  </VCol>
                </VRow>
                <VRow>
                  <VCol cols="12">
                    <VSelect v-model="form.subfill_details" :items="subfillDetailItems"
                      label="自动填充哪些规则" multiple chips closable-chips clearable
                      prepend-inner-icon="mdi-auto-fix"
                      :disabled="!form.subfill_enabled" />
                    <div class="aoa-hint">从下载资源中提取并回填：分辨率 / 资源质量 / 特效 / 制作组 / 站点，留空则不填充</div>
                  </VCol>
                </VRow>

                <VDivider class="my-4" />
                <div class="aoa-section-title">二级分类自定义填充</div>
                <div class="aoa-hint mb-2">新增订阅时，按媒体的二级分类自动套用预设规则，每行一个分类，用 # 分隔字段，可用键：category、resolution、quality、effect、include、exclude、sites（站点名,逗号分隔）、savepath（支持 {name}）、filter_groups</div>
                <VRow>
                  <VCol cols="12" md="6">
                    <VSwitch v-model="form.subfill_category_enabled" color="primary" inset hide-details
                      label="启用二级分类自定义填充" />
                  </VCol>
                </VRow>
                <VRow>
                  <VCol cols="12">
                    <VTextarea v-model="form.subfill_category_confs"
                      label="二级分类规则（每行一个分类）" auto-grow rows="3"
                      placeholder="category:国漫,日番#resolution:1080p#quality:WEB-DL#include:简体#sites:馒头,青蛙#savepath:/media/动漫/{name}"
                      :disabled="!form.subfill_category_enabled" />
                  </VCol>
                </VRow>

                <VDivider class="my-4" />
                <div class="aoa-section-title">维护</div>
                <div class="aoa-btn-row">
                  <VBtn color="primary" variant="tonal" prepend-icon="mdi-history"
                    :loading="action.running === 'subfill_clear_history'" @click="runAction('subfill_clear_history', '清理填充历史')">
                    清理历史记录
                  </VBtn>
                  <VBtn color="warning" variant="tonal" prepend-icon="mdi-backup-restore"
                    :loading="action.running === 'subfill_clear_handled'" @click="runAction('subfill_clear_handled', '清理已处理记录')">
                    清理已处理记录
                  </VBtn>
                </div>
                <div class="aoa-hint mt-2">“清理已处理记录”后，已处理过的剧集下次下载会重新尝试填充</div>
              </VForm>
            </div>
            <!-- 自动备份 · 本地备份 -->
            <div v-show="activeSub === 'local'" class="aoa-pane">
              <VForm>
                <div class="aoa-section-title">本地备份</div>
                <VRow>
                  <VCol cols="12" md="6">
                    <VSwitch v-model="form.backup_enabled" color="primary" inset hide-details
                      label="启用定时本地备份" />
                    <div class="aoa-hint">按计划打包配置目录到本地备份路径</div>
                  </VCol>
                  <VCol cols="12" md="6">
                    <VCronField v-model="form.backup_cron" label="备份时间 (Cron)"
                      :disabled="!form.backup_enabled" />
                  </VCol>
                </VRow>
                <VRow>
                  <VCol cols="12" md="6">
                    <VTextField v-model="form.backup_path" label="本地备份路径"
                      prepend-inner-icon="mdi-folder-outline" :disabled="!form.backup_enabled" />
                  </VCol>
                  <VCol cols="12" md="6">
                    <div class="d-flex align-center justify-space-between mb-1">
                      <span class="text-body-2">本地保留份数</span>
                      <VChip size="small" color="primary" variant="tonal">{{ form.backup_keep_count }} 份</VChip>
                    </div>
                    <VSlider v-model="form.backup_keep_count" :min="1" :max="30" :step="1"
                      color="primary" thumb-label hide-details :disabled="!form.backup_enabled" />
                    <div class="aoa-hint">超出份数时自动删除最旧的备份，范围 1-30 份</div>
                  </VCol>
                </VRow>
                <VRow>
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
                <VDivider class="my-4" />
                <div class="aoa-btn-row">
                  <VBtn color="primary" variant="tonal" prepend-icon="mdi-archive-arrow-up-outline"
                    :loading="action.running === 'run_backup'" @click="runAction('run_backup', '立即备份')">
                    立即备份
                  </VBtn>
                </div>
              </VForm>
            </div>

            <!-- 自动备份 · WebDAV -->
            <div v-show="activeSub === 'webdav'" class="aoa-pane">
              <VForm>
                <div class="aoa-section-title">WebDAV 远端备份</div>
                <VRow>
                  <VCol cols="12">
                    <VSwitch v-model="form.backup_webdav_enabled" color="primary" inset hide-details
                      label="启用 WebDAV 远端备份" />
                    <div class="aoa-hint">本地备份完成后同步上传到 WebDAV</div>
                  </VCol>
                </VRow>
                <VRow>
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
                <VRow>
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
                </VRow>
                <VRow>
                  <VCol cols="12" md="4">
                    <VSwitch v-model="form.backup_webdav_digest_auth" color="primary" inset hide-details
                      label="使用 Digest 认证" :disabled="!form.backup_webdav_enabled" />
                  </VCol>
                  <VCol cols="12" md="8">
                    <VSwitch v-model="form.backup_webdav_disable_check" color="warning" inset hide-details
                      label="跳过证书校验（自签名时启用）" :disabled="!form.backup_webdav_enabled" />
                  </VCol>
                </VRow>
              </VForm>
            </div>
            <!-- 日志清理 · 插件日志 -->
            <div v-show="activeSub === 'logs'" class="aoa-pane">
              <VForm>
                <div class="aoa-section-title">插件日志清理</div>
                <VRow>
                  <VCol cols="12" md="6">
                    <VSwitch v-model="form.log_clean_enabled" color="primary" inset hide-details
                      label="启用定时日志清理" />
                    <div class="aoa-hint">按计划裁剪插件日志文件，仅保留指定行数</div>
                  </VCol>
                  <VCol cols="12" md="6">
                    <VCronField v-model="form.log_clean_cron" label="清理时间 (Cron)"
                      :disabled="!form.log_clean_enabled" />
                  </VCol>
                </VRow>
                <VRow>
                  <VCol cols="12" md="6">
                    <VSelect v-model="form.log_clean_rows" :items="logRowsPresets"
                      label="保留行数" :disabled="!form.log_clean_enabled" />
                  </VCol>
                  <VCol cols="12" md="6">
                    <VSelect v-model="form.log_clean_selected_ids" :items="installedPlugins"
                      :loading="installedLoading" label="限定插件（留空＝全部插件）"
                      multiple chips closable-chips clearable
                      prepend-inner-icon="mdi-puzzle-outline"
                      :disabled="!form.log_clean_enabled" />
                  </VCol>
                </VRow>
                <VRow>
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
                <VDivider class="my-4" />
                <div class="aoa-section-title">手动触发</div>
                <div class="aoa-btn-row">
                  <VBtn color="primary" variant="tonal" prepend-icon="mdi-broom"
                    :loading="action.running === 'run_log_clean'" @click="runAction('run_log_clean', '日志清理')">
                    立即清理
                  </VBtn>
                </div>
              </VForm>
            </div>

            <!-- 更新检查 · 主程序 -->
            <div v-show="activeSub === 'mp'" class="aoa-pane">
              <VForm>
                <div class="aoa-section-title">MoviePilot 更新检查</div>
                <div class="aoa-hint mb-2">仅检查并通知是否有新版本，不会在这里直接升级</div>
                <VRow>
                  <VCol cols="12" md="6">
                    <VSwitch v-model="form.mp_update_enabled" color="primary" inset hide-details
                      label="启用定时更新检查" />
                  </VCol>
                  <VCol cols="12" md="6">
                    <VCronField v-model="form.mp_update_cron" label="检查时间 (Cron)"
                      :disabled="!form.mp_update_enabled" />
                  </VCol>
                </VRow>
                <VRow>
                  <VCol cols="12" md="4">
                    <VSelect v-model="form.mp_update_types" :items="mpUpdateTypes"
                      label="检查范围" multiple chips closable-chips :disabled="!form.mp_update_enabled" />
                  </VCol>
                  <VCol cols="12" md="4">
                    <VSwitch v-model="form.mp_update_notify" color="primary" inset hide-details
                      label="发现新版本时通知" :disabled="!form.mp_update_enabled" />
                  </VCol>
                  <VCol cols="12" md="4">
                    <VSelect v-model="form.mp_update_notify_type" :items="notificationTypeItems"
                      label="消息类型" :disabled="!form.mp_update_enabled || !form.mp_update_notify" />
                  </VCol>
                </VRow>
                <VRow>
                  <VCol cols="12">
                    <VSwitch v-model="form.mp_update_restart_confirm" color="warning" inset hide-details
                      label="允许自动重启以应用更新（高风险，谨慎开启）" :disabled="!form.mp_update_enabled" />
                    <div class="aoa-hint">默认仅提醒，开启后将在更新后尝试重启 MoviePilot</div>
                  </VCol>
                </VRow>
                <VDivider class="my-4" />
                <div class="aoa-btn-row">
                  <VBtn color="primary" variant="tonal" prepend-icon="mdi-update"
                    :loading="action.running === 'run_mp_update'" @click="runAction('run_mp_update', '检查主程序更新')">
                    检查更新
                  </VBtn>
                </div>
              </VForm>
            </div>

            <!-- 更新检查 · 插件库 -->
            <div v-show="activeSub === 'market'" class="aoa-pane">
              <VForm>
                <div class="aoa-section-title">插件库更新检查</div>
                <VRow>
                  <VCol cols="12" md="6">
                    <VSwitch v-model="form.market_update_enabled" color="primary" inset hide-details
                      label="启用插件库更新检查" />
                    <div class="aoa-hint">按间隔检查已安装插件是否有新版本</div>
                  </VCol>
                  <VCol cols="12" md="6">
                    <VSelect v-model="form.market_update_interval" :items="intervalPresets"
                      label="检查间隔" :disabled="!form.market_update_enabled" />
                  </VCol>
                </VRow>
                <VRow>
                  <VCol cols="12" md="6">
                    <VSwitch v-model="form.market_update_notify" color="primary" inset hide-details
                      label="发现更新时通知" :disabled="!form.market_update_enabled" />
                  </VCol>
                  <VCol cols="12" md="6">
                    <VSelect v-model="form.market_update_notify_type" :items="marketNotifyItems"
                      label="通知消息类型" :disabled="!form.market_update_enabled" />
                  </VCol>
                </VRow>
                <VRow>
                  <VCol cols="12" md="6">
                    <VSwitch v-model="form.market_update_proxy" color="primary" inset hide-details
                      label="使用代理访问插件库" :disabled="!form.market_update_enabled" />
                  </VCol>
                  <VCol cols="12" md="6">
                    <VSwitch v-model="form.market_update_auto_get" color="primary" inset hide-details
                      label="自动抓取 Wiki 更新说明" :disabled="!form.market_update_enabled" />
                  </VCol>
                </VRow>
                <VExpansionPanels class="mt-2" variant="accordion">
                  <VExpansionPanel title="高级选项（写回设置 / 黑名单 / Wiki 源）">
                    <VExpansionPanelText>
                      <VRow>
                        <VCol cols="12" md="6">
                          <VSwitch v-model="form.market_update_write_settings" color="warning" inset hide-details
                            label="写回插件设置" :disabled="!form.market_update_enabled" />
                        </VCol>
                        <VCol cols="12" md="6">
                          <VSwitch v-model="form.market_update_write_env" color="warning" inset hide-details
                            label="写回环境变量" :disabled="!form.market_update_enabled" />
                        </VCol>
                      </VRow>
                      <VRow>
                        <VCol cols="12" md="6">
                          <VSwitch v-model="form.market_update_blacklist_enabled" color="primary" inset hide-details
                            label="启用更新黑名单" :disabled="!form.market_update_enabled" />
                        </VCol>
                        <VCol cols="12" md="6">
                          <VTextField v-model="form.market_update_timeout" label="请求超时（秒）"
                            type="number" min="1" :disabled="!form.market_update_enabled" />
                        </VCol>
                      </VRow>
                      <VRow>
                        <VCol cols="12">
                          <VSelect v-model="form.market_update_blacklist" :items="pluginMarkets"
                            :loading="marketsLoading" label="黑名单插件库（不参与更新检查）"
                            multiple chips closable-chips clearable
                            prepend-inner-icon="mdi-block-helper"
                            no-data-text="未配置任何插件库"
                            :disabled="!form.market_update_enabled || !form.market_update_blacklist_enabled" />
                        </VCol>
                      </VRow>
                      <VRow>
                        <VCol cols="12">
                          <VTextField v-model="form.market_update_wiki_url" label="Wiki 地址"
                            :disabled="!form.market_update_enabled" />
                        </VCol>
                      </VRow>
                    </VExpansionPanelText>
                  </VExpansionPanel>
                </VExpansionPanels>
                <VDivider class="my-4" />
                <div class="aoa-section-title">自动更新已安装插件</div>
                <div class="aoa-hint mb-2">检测到已安装插件有新版时自动下载安装并重载，不开启则仅在检查时提醒有新版</div>
                <VRow>
                  <VCol cols="12" md="6">
                    <VSwitch v-model="form.market_update_auto_install" color="warning" inset hide-details
                      label="自动安装插件新版" :disabled="!form.market_update_enabled" />
                    <div class="aoa-hint">高风险：会自动替换插件代码并重载，默认关闭，仅提醒，当前插件不会自动更新</div>
                  </VCol>
                  <VCol cols="12" md="6">
                    <VSwitch v-model="form.market_update_skip_running" color="primary" inset hide-details
                      label="跳过正在运行的插件" :disabled="!form.market_update_enabled || !form.market_update_auto_install" />
                    <div class="aoa-hint">插件正在执行任务时不升级，避免中断</div>
                  </VCol>
                </VRow>
                <VRow>
                  <VCol cols="12" md="6">
                    <VSelect v-model="form.market_update_install_ids" :items="installedPlugins"
                      :loading="installedLoading" label="仅自动更新这些插件（留空＝全部已安装）"
                      multiple chips closable-chips clearable prepend-inner-icon="mdi-puzzle-check-outline"
                      :disabled="!form.market_update_enabled || !form.market_update_auto_install" />
                  </VCol>
                  <VCol cols="12" md="6">
                    <VSelect v-model="form.market_update_exclude_ids" :items="installedPlugins"
                      :loading="installedLoading" label="排除（这些插件不自动更新）"
                      multiple chips closable-chips clearable prepend-inner-icon="mdi-block-helper"
                      :disabled="!form.market_update_enabled || !form.market_update_auto_install" />
                  </VCol>
                </VRow>
                <VDivider class="my-4" />
                <div class="aoa-btn-row">
                  <VBtn color="primary" variant="tonal" prepend-icon="mdi-cloud-sync-outline"
                    :loading="action.running === 'run_market_update'" @click="runAction('run_market_update', '插件库更新')">
                    立即检查
                  </VBtn>
                </div>
              </VForm>
            </div>

            <!-- 插件残留清理 · 残留清理（合并单页） -->
            <div v-show="activeSub === 'clean'" class="aoa-pane">
              <VForm>
                <div class="aoa-section-title">目标插件</div>
                <VRow>
                  <VCol cols="12">
                    <VSelect v-model="form.plugin_uninstall_ids" :items="installedPlugins"
                      :loading="installedLoading" label="选择要清理残留的已安装插件"
                      multiple chips closable-chips clearable
                      prepend-inner-icon="mdi-puzzle-remove-outline" />
                  </VCol>
                </VRow>
                <VDivider class="my-4" />
                <div class="aoa-section-title">清理范围</div>
                <VRow>
                  <VCol cols="12" md="6">
                    <VSwitch v-model="form.plugin_uninstall_clear_config" color="primary" inset hide-details
                      label="清除插件配置" />
                  </VCol>
                  <VCol cols="12" md="6">
                    <VSwitch v-model="form.plugin_uninstall_clear_data" color="primary" inset hide-details
                      label="清除插件数据" />
                  </VCol>
                </VRow>
                <VRow>
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
                      label="删除本地源码（高风险，不可恢复）" />
                    <div class="aoa-hint">仅对本地源码插件生效，删除后需重新安装</div>
                  </VCol>
                </VRow>
                <VDivider class="my-4" />
                <div class="aoa-section-title">执行</div>
                <div class="aoa-btn-row">
                  <VBtn color="error" variant="tonal" prepend-icon="mdi-broom"
                    :disabled="!form.plugin_uninstall_ids || !form.plugin_uninstall_ids.length"
                    :loading="action.running === 'run_plugin_uninstall'" @click="runAction('run_plugin_uninstall', '插件残留治理')">
                    执行清理
                  </VBtn>
                </div>
                <div class="aoa-hint mt-2">残留清理为不可逆操作，执行前请务必先预览确认</div>
              </VForm>
            </div>

            <!-- 种子治理 · 自动删种 -->
            <div v-show="activeSub === 'seedremove'" class="aoa-pane">
              <VForm class="aoa-compact-form">
                <VAlert type="warning" variant="tonal" density="compact" class="mb-3" :icon="false"
                  text="自动删种有风险，设置不当可能丢数据！建议先用“暂停”动作验证条件命中正确，再改“删除”，未填写任何筛选条件时不会执行" />
                <div class="aoa-section-title">基础设置</div>
                <VRow dense>
                  <VCol cols="12" md="3">
                    <VSwitch v-model="form.seedclean_enabled" color="primary" inset hide-details
                      label="启用定时自动删种" />
                  </VCol>
                  <VCol cols="12" md="3">
                    <VCronField v-model="form.seedclean_cron" label="执行周期 (Cron)"
                      :disabled="!form.seedclean_enabled" />
                  </VCol>
                  <VCol cols="12" md="2">
                    <VSelect v-model="form.seedclean_action" :items="seedActionItems"
                      density="compact" hide-details label="动作" :disabled="!form.seedclean_enabled" />
                  </VCol>
                  <VCol cols="12" md="4">
                    <VSelect v-model="form.seedclean_downloaders" :items="downloaderOptions"
                      :loading="downloadersLoading" label="下载器（必选）"
                      multiple chips closable-chips clearable
                      density="compact" hide-details
                      prepend-inner-icon="mdi-download-network-outline"
                      no-data-text="未配置下载器" :disabled="!form.seedclean_enabled" />
                  </VCol>
                </VRow>

                <VDivider class="my-3" />
                <div class="aoa-section-title">筛选条件</div>
                <div class="aoa-hint mb-2">仅处理“同时满足所有已填条件”的种子，留空的条件不参与，全部留空则跳过不处理</div>
                <VRow dense>
                  <VCol cols="12" sm="6" md="3">
                    <VTextField v-model="form.seedclean_size" label="种子大小（GB）" density="compact" hide-details
                      placeholder="1-10" :disabled="!form.seedclean_enabled" />
                  </VCol>
                  <VCol cols="12" sm="6" md="3">
                    <VTextField v-model="form.seedclean_ratio" label="分享率不小于" density="compact" hide-details
                      placeholder="2" :disabled="!form.seedclean_enabled" />
                  </VCol>
                  <VCol cols="12" sm="6" md="3">
                    <VTextField v-model="form.seedclean_time" label="做种不少于（小时）" density="compact" hide-details
                      placeholder="240" :disabled="!form.seedclean_enabled" />
                  </VCol>
                  <VCol cols="12" sm="6" md="3">
                    <VTextField v-model="form.seedclean_upspeed" label="均速上限（KB/s）" density="compact" hide-details
                      placeholder="低于才处理" :disabled="!form.seedclean_enabled" />
                  </VCol>
                </VRow>
                <VRow dense>
                  <VCol cols="12" sm="6" md="3">
                    <VTextField v-model="form.seedclean_labels" label="标签" density="compact" hide-details
                      placeholder="逗号分隔" :disabled="!form.seedclean_enabled" />
                  </VCol>
                  <VCol cols="12" sm="6" md="3">
                    <VTextField v-model="form.seedclean_torrentcategorys" label="任务分类" density="compact" hide-details
                      placeholder="逗号分隔" :disabled="!form.seedclean_enabled" />
                  </VCol>
                  <VCol cols="12" sm="6" md="3">
                    <VTextField v-model="form.seedclean_pathkeywords" label="保存路径关键词" density="compact" hide-details
                      placeholder="支持正则" :disabled="!form.seedclean_enabled" />
                  </VCol>
                  <VCol cols="12" sm="6" md="3">
                    <VTextField v-model="form.seedclean_trackerkeywords" label="Tracker 关键词" density="compact" hide-details
                      placeholder="支持正则" :disabled="!form.seedclean_enabled" />
                  </VCol>
                </VRow>
                <VRow dense>
                  <VCol cols="12" sm="6" md="3">
                    <VTextField v-model="form.seedclean_torrentstates" label="任务状态（仅 QB）" density="compact" hide-details
                      placeholder="pausedUP,stalledUP" :disabled="!form.seedclean_enabled" />
                  </VCol>
                  <VCol cols="12" sm="6" md="3">
                    <VTextField v-model="form.seedclean_errorkeywords" label="错误信息（仅 TR）" density="compact" hide-details
                      placeholder="支持正则" :disabled="!form.seedclean_enabled" />
                  </VCol>
                  <VCol cols="12" md="9">
                    <div class="aoa-seed-options">
                      <VSwitch v-model="form.seedclean_samedata" color="primary" inset hide-details density="compact"
                        label="处理辅种" :disabled="!form.seedclean_enabled" />
                      <VSwitch v-model="form.seedclean_mponly" color="primary" inset hide-details density="compact"
                        label="仅 MoviePilot 任务" :disabled="!form.seedclean_enabled" />
                      <VSwitch v-model="form.seedclean_notify" color="primary" inset hide-details density="compact"
                        label="处理结果通知" :disabled="!form.seedclean_enabled" />
                    </div>
                  </VCol>
                </VRow>

                <VDivider class="my-3" />
                <div class="aoa-seed-action-row">
                  <div class="aoa-seed-action-type">
                    <VSelect v-model="form.seedclean_notify_type" :items="notificationTypeItems"
                      density="compact" hide-details label="消息类型" :disabled="!form.seedclean_enabled || !form.seedclean_notify" />
                  </div>
                  <VBtn color="error" variant="tonal" prepend-icon="mdi-delete-sweep-outline"
                    :disabled="!form.seedclean_downloaders || !form.seedclean_downloaders.length"
                    :loading="action.running === 'run_seed_clean'" @click="runAction('run_seed_clean', '自动删种')">
                    立即执行
                  </VBtn>
                  <div class="aoa-hint">立即执行按当前条件处理，建议先用“暂停”确认命中无误</div>
                </div>
              </VForm>
            </div>
            <!-- 媒体通知 · 服务器通知 -->
            <div v-show="activeSub === 'server'" class="aoa-pane aoa-media-pane">
              <VForm class="aoa-media-form">
                <div class="aoa-section-title">媒体库服务器通知</div>
                <div class="aoa-hint aoa-line-hint mb-4">需先在 MoviePilot 把媒体服务器 webhook 指向 MP</div>
                <VRow class="aoa-media-enable-row">
                  <VCol cols="12">
                    <div class="aoa-inline-switch">
                      <VSwitch v-model="form.msgnotify_enabled" color="primary" inset hide-details
                        label="启用媒体库服务器通知" />
                      <span class="aoa-hint aoa-inline-hint">监听 Emby/Jellyfin/Plex 的 webhook 事件，按筛选规则推送通知</span>
                    </div>
                  </VCol>
                </VRow>
                <VRow class="aoa-media-field-row">
                  <VCol cols="12" md="6">
                    <VSelect v-model="form.msgnotify_types" :items="msgGroupItems"
                      label="通知哪些事件" multiple chips closable-chips clearable
                      prepend-inner-icon="mdi-bell-cog-outline"
                      :disabled="!form.msgnotify_enabled" />
                  </VCol>
                  <VCol cols="12" md="6">
                    <VSelect v-model="form.msgnotify_servers" :items="mediaserverOptions"
                      :loading="mediaserversLoading" label="仅这些媒体服务器（留空＝全部）"
                      multiple chips closable-chips clearable
                      prepend-inner-icon="mdi-server-network"
                      no-data-text="未获取到媒体服务器"
                      :disabled="!form.msgnotify_enabled" />
                  </VCol>
                </VRow>
              </VForm>
            </div>
            <!-- 下载器助手 · 批量打标签 -->
            <div v-show="activeSub === 'dltagmain'" class="aoa-pane">
              <VForm>
                <div class="aoa-section-title">按站点为种子批量补打标签</div>
                <VRow>
                  <VCol cols="12" md="6">
                    <VSwitch v-model="form.dltag_enabled" color="primary" inset hide-details
                      label="启用下载器助手(批量打标签)" />
                    <div class="aoa-hint">遍历下载器中的种子，按其 tracker 所属站点补打标签(已打的跳过，幂等安全)</div>
                  </VCol>
                </VRow>
                <VRow>
                  <VCol cols="12" md="5">
                    <VSelect v-model="form.dltag_downloaders" :items="downloaderOptions"
                      :loading="downloadersLoading" label="下载器（留空＝全部已配置）"
                      multiple chips closable-chips clearable prepend-inner-icon="mdi-download-network-outline"
                      :disabled="!form.dltag_enabled" />
                  </VCol>
                  <VCol cols="12" md="3">
                    <VTextField v-model="form.dltag_prefix" label="标签前缀（可选）" placeholder="如 站点-" clearable
                      :disabled="!form.dltag_enabled" />
                  </VCol>
                  <VCol cols="12" md="2">
                    <VSwitch v-model="form.dltag_notify" color="primary" inset hide-details label="完成后通知"
                      :disabled="!form.dltag_enabled" />
                  </VCol>
                  <VCol cols="12" md="2">
                    <VSelect v-model="form.dltag_notify_type" :items="notificationTypeItems"
                      label="消息类型" :disabled="!form.dltag_enabled || !form.dltag_notify" />
                  </VCol>
                </VRow>
                <VDivider class="my-4" />
                <div class="aoa-btn-row">
                  <VBtn color="primary" variant="tonal" prepend-icon="mdi-tag-multiple-outline"
                    :loading="action.running === 'run_downloader_tag'" @click="runAction('run_downloader_tag', '种子打标签')">
                    立即按站点打标签
                  </VBtn>
                </div>
              </VForm>
            </div>
          </div>
        </section>
      </div>
      <VDivider />
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
<style scoped>
.aoa-config {
  padding: 10px;
  font-size: 14px;
}
.aoa-card {
  border-radius: 18px;
  overflow: hidden;
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}
.aoa-header {
  padding: 16px 20px;
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
  height: min(72vh, 650px);
  min-height: 520px;
}
.aoa-nav {
  position: relative;
  width: 208px;
  flex: 0 0 208px;
  border-right: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  background: rgba(var(--v-theme-on-surface), 0.02);
}
.aoa-nav-scroll {
  height: 100%;
  overflow-y: auto;
  overflow-x: hidden;
  padding-bottom: 44px;
  scrollbar-width: thin;
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
  flex-wrap: wrap;
  gap: 6px;
  min-width: 0;
  max-width: 48%;
  max-height: 42px;
  overflow-x: hidden;
  overflow-y: auto;
  padding-bottom: 2px;
  scrollbar-width: thin;
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
  flex: 1 1 auto;
  justify-content: flex-end;
  max-width: 52%;
  min-height: 36px;
  min-width: 0;
  padding-right: 44px;
  font-size: 13px;
  font-weight: 500;
  line-height: 36px;
  color: rgba(var(--v-theme-on-surface), 0.58);
  text-align: right;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.aoa-window {
  flex: 1 1 auto;
  min-height: 0;
  overflow-y: auto;
  overflow-x: hidden;
  padding-bottom: 48px;
  scrollbar-width: thin;
}
.aoa-pane {
  padding: 22px 24px;
}
.aoa-section-title {
  font-size: 15px;
  font-weight: 700;
  margin-bottom: 10px;
  color: rgb(var(--v-theme-primary));
}
.aoa-hint {
  font-size: 12px;
  line-height: 1.6;
  color: rgba(var(--v-theme-on-surface), 0.48);
  margin-top: 2px;
}
.aoa-line-hint,
.aoa-inline-hint {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.aoa-media-form {
  padding-top: 2px;
}
.aoa-media-enable-row {
  margin-bottom: 12px;
}
.aoa-media-field-row :deep(.v-col) {
  padding-top: 10px;
  padding-bottom: 10px;
}
.aoa-inline-switch {
  display: flex;
  align-items: center;
  gap: 14px;
  min-height: 48px;
  min-width: 0;
}
.aoa-inline-switch :deep(.v-selection-control) {
  flex: 0 0 auto;
}
.aoa-inline-hint {
  margin-top: 0;
}
.aoa-btn-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}
.aoa-compact-form :deep(.v-row) {
  margin-top: -6px;
  margin-bottom: -6px;
}
.aoa-compact-form :deep(.v-col) {
  padding-top: 6px;
  padding-bottom: 6px;
}
.aoa-seed-options {
  min-height: 40px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
  align-items: center;
}
.aoa-seed-options :deep(.v-selection-control) {
  min-height: 36px;
}
.aoa-seed-action-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}
.aoa-seed-action-type {
  flex: 0 1 220px;
  min-width: 180px;
}
.aoa-health-form {
  display: grid;
  gap: 14px;
}
.aoa-health-hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 16px;
  border-radius: 14px;
  color: rgba(var(--v-theme-on-surface), 0.92);
  background:
    linear-gradient(135deg, rgba(var(--v-theme-success), 0.14), rgba(var(--v-theme-primary), 0.08)),
    rgba(var(--v-theme-surface), 0.78);
  box-shadow: inset 0 0 0 1px rgba(var(--v-theme-success), 0.18);
}
.aoa-health-hero--off {
  background:
    linear-gradient(135deg, rgba(var(--v-theme-warning), 0.13), rgba(var(--v-theme-on-surface), 0.04)),
    rgba(var(--v-theme-surface), 0.78);
  box-shadow: inset 0 0 0 1px rgba(var(--v-theme-warning), 0.18);
}
.aoa-health-heading {
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 12px;
}
.aoa-health-emblem {
  width: 46px;
  height: 46px;
  flex: 0 0 46px;
  display: grid;
  place-items: center;
  border-radius: 12px;
  color: rgb(var(--v-theme-success));
  background: rgba(var(--v-theme-surface), 0.8);
  box-shadow: inset 0 0 0 1px rgba(var(--v-theme-success), 0.22);
}
.aoa-health-heading-text {
  min-width: 0;
}
.aoa-health-kicker {
  font-size: 12px;
  font-weight: 700;
  color: rgba(var(--v-theme-on-surface), 0.58);
}
.aoa-health-title {
  margin-top: 2px;
  font-size: 18px;
  font-weight: 800;
  line-height: 1.2;
  letter-spacing: 0;
}
.aoa-health-desc {
  margin-top: 4px;
  font-size: 12px;
  line-height: 1.45;
  color: rgba(var(--v-theme-on-surface), 0.66);
}
.aoa-health-state {
  flex: 0 0 auto;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  white-space: nowrap;
}
.aoa-health-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}
.aoa-health-check {
  min-height: 74px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  border-radius: 12px;
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  color: rgba(var(--v-theme-on-surface), 0.68);
  background: rgba(var(--v-theme-on-surface), 0.025);
  transition: border-color 0.18s, background 0.18s, color 0.18s;
}
.aoa-health-check--active {
  color: rgba(var(--v-theme-on-surface), 0.92);
  border-color: rgba(var(--v-theme-primary), 0.28);
  background: rgba(var(--v-theme-primary), 0.07);
}
.aoa-health-check-icon {
  flex: 0 0 auto;
  color: rgb(var(--v-theme-primary));
}
.aoa-health-check-text {
  min-width: 0;
}
.aoa-health-check-title {
  font-size: 13px;
  font-weight: 700;
  line-height: 1.2;
}
.aoa-health-check-desc {
  margin-top: 4px;
  font-size: 12px;
  line-height: 1.35;
  color: rgba(var(--v-theme-on-surface), 0.58);
}
.aoa-health-controls {
  display: grid;
  grid-template-columns: minmax(220px, 0.8fr) minmax(280px, 1.2fr) auto;
  gap: 12px;
  align-items: start;
}
.aoa-health-control {
  min-width: 0;
}
.aoa-health-run {
  min-height: 48px;
  align-self: start;
}
.aoa-table-wrap {
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  border-radius: 14px;
  background: rgba(var(--v-theme-on-surface), 0.018);
}
.aoa-report-table-scroll {
  max-height: 430px;
  overflow: auto;
  scrollbar-width: thin;
}
.aoa-report-table {
  min-width: 680px;
  font-size: 13px;
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
@media (max-width: 760px) {
  .aoa-body {
    height: min(76vh, 680px);
    flex-direction: column;
  }
  .aoa-nav {
    width: 100%;
    flex: 0 0 180px;
    border-right: none;
    border-bottom: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  }
  .aoa-nav-scroll {
    padding-bottom: 40px;
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
  .aoa-pane {
    padding: 18px 16px;
  }
  .aoa-report-table {
    min-width: 620px;
  }
  .aoa-seed-options {
    grid-template-columns: 1fr;
  }
  .aoa-seed-action-row {
    align-items: stretch;
    flex-direction: column;
  }
  .aoa-seed-action-type {
    width: 100%;
    min-width: 0;
  }
  .aoa-health-hero,
  .aoa-health-state,
  .aoa-health-controls {
    align-items: stretch;
    flex-direction: column;
  }
  .aoa-health-state {
    justify-content: flex-start;
    white-space: normal;
  }
  .aoa-health-grid,
  .aoa-health-controls {
    grid-template-columns: 1fr;
  }
  .aoa-health-run {
    width: 100%;
  }
}
</style>
