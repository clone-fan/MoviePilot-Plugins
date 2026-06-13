<script setup>
import { reactive, ref, computed, watch, onMounted } from 'vue'
import { postPluginApi, postPluginApiRaw, getPluginApi } from './api'

const props = defineProps({
  api: { type: [Object, Function], default: null },
  initialConfig: { type: Object, default: () => ({}) },
})
const emit = defineEmits(['save', 'close', 'switch'])

const form = reactive({})
const activeMain = ref('report')
const activeSub = ref('basic')

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

// 预览弹窗：展示后端返回的 text 正文
const preview = reactive({ open: false, title: '', text: '', loading: '' })
async function runPreview(path, title) {
  if (preview.loading) return
  preview.loading = path
  try {
    const res = await postPluginApiRaw(props.api, path)
    const ok = !res || res.code === 0 || res.code === undefined
    preview.title = title
    preview.text = (res && res.text) || (res && res.msg) || (ok ? '（无预览内容）' : '预览失败')
    preview.open = true
  } catch (err) {
    preview.title = title
    preview.text = err?.message || `${title}失败`
    preview.open = true
  } finally {
    preview.loading = ''
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
  market_update_blacklist: [],
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
}

const mainTabs = [
  { key: 'report', title: '每日汇报', icon: 'mdi-newspaper-variant-outline', desc: '设置每日汇报、订阅提醒、站点统计与健康巡查。' },
  { key: 'backup', title: '自动备份', icon: 'mdi-archive-arrow-up-outline', desc: '设置本地备份、保留数量和 WebDAV 远端备份。' },
  { key: 'cleanup', title: '日志清理', icon: 'mdi-file-document-remove-outline', desc: '设置插件日志保留行数、清理时间和结果通知。' },
  { key: 'updates', title: '更新检查', icon: 'mdi-update', desc: '设置 MoviePilot 和插件库更新检查，不在这里直接升级。' },
  { key: 'plugin', title: '插件残留清理', icon: 'mdi-puzzle-remove-outline', desc: '清理已卸载插件留下的配置、数据、日志或本地源码残留。' },
]

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
}

const subscribeSubtypeItems = [{ title: '电影', value: 'movie' }, { title: '电视剧', value: 'tv' }]
const messageTypeItems = [{ title: '订阅', value: 'Subscribe' }, { title: '插件', value: 'Plugin' }, { title: '手动处理', value: 'Manual' }]
const siteStatRangeItems = [{ title: '今日数据', value: 'today' }, { title: '汇总数据', value: 'total' }, { title: '所有数据', value: 'all' }]
const siteNotifyItems = [{ title: '增量变化', value: 'inc' }, { title: '全部数据', value: 'all' }, { title: '不通知', value: 'none' }]
const marketNotifyItems = [{ title: '插件通知', value: 'Plugin' }, { title: '手动处理', value: 'Manual' }]
const mpUpdateTypes = ['后端', '前端'].map(v => ({ title: v, value: v }))
const keepCountPresets = [3, 5, 7, 10, 15].map(v => ({ title: `保留 ${v} 份`, value: v }))
const logRowsPresets = [100, 300, 500, 1000, 2000].map(v => ({ title: `保留 ${v} 行`, value: v }))
const intervalPresets = [3600, 21600, 43200, 86400, 604800].map(v => ({ title: v < 86400 ? `${v / 3600} 小时` : `${v / 86400} 天`, value: v }))

const currentMain = computed(() => mainTabs.find(item => item.key === activeMain.value) || mainTabs[0])
const currentSubs = computed(() => subTabs[activeMain.value] || [])

watch(() => props.initialConfig, value => {
  Object.keys(form).forEach(key => delete form[key])
  Object.assign(form, defaults, value || {})
  const toArr = v => typeof v === 'string' ? v.split(',').map(s => s.trim()).filter(Boolean) : (Array.isArray(v) ? v : [])
  form.subscribe_reminder_subtype = toArr(form.subscribe_reminder_subtype)
  form.mp_update_types = toArr(form.mp_update_types)
  form.plugin_uninstall_ids = toArr(form.plugin_uninstall_ids)
  form.log_clean_selected_ids = toArr(form.log_clean_selected_ids)
  form.market_update_blacklist = toArr(form.market_update_blacklist)
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
        <VCardSubtitle class="text-caption">{{ currentMain.desc }}</VCardSubtitle>
        <template #append>
          <div class="d-flex align-center">
            <VSwitch
              v-model="form.enabled"
              color="primary"
              hide-details
              inset
              :label="form.enabled ? '已启用' : '已停用'"
            />
          </div>
        </template>
      </VCardItem>
      <VDivider />
      <div class="aoa-body">
        <nav class="aoa-nav">
          <VList density="comfortable" nav class="py-2">
            <VListItem
              v-for="item in mainTabs"
              :key="item.key"
              :active="activeMain === item.key"
              color="primary"
              rounded="lg"
              class="aoa-nav-item"
              @click="selectMain(item.key)"
            >
              <template #prepend>
                <VIcon :icon="item.icon" />
              </template>
              <VListItemTitle>{{ item.title }}</VListItemTitle>
            </VListItem>
          </VList>
        </nav>
        <section class="aoa-content">
          <div class="aoa-subtabs">
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
          <VDivider />
          <div class="aoa-window">
            <!-- 每日汇报 · 基础设置 -->
            <div v-show="activeSub === 'basic'" class="aoa-pane">
              <VForm>
                <div class="aoa-section-title">汇报开关</div>
                <VRow>
                  <VCol cols="12" md="6">
                    <VSwitch v-model="form.daily_report_enabled" color="primary" inset hide-details
                      label="启用定时每日汇报" />
                    <div class="aoa-hint">关闭后将不再按计划自动发送汇报，仍可在下方手动触发。</div>
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
                      persistent-hint hint="汇报开头与提醒中对你的称呼，留空默认“少爷”。" clearable />
                  </VCol>
                </VRow>
                <VDivider class="my-4" />
                <div class="aoa-section-title">手动触发</div>
                <div class="aoa-btn-row">
                  <VBtn color="primary" variant="tonal" prepend-icon="mdi-send-outline"
                    :loading="action.running === 'run_daily_report'" @click="runAction('run_daily_report', '发送每日汇报')">
                    立即发送
                  </VBtn>
                  <VBtn color="primary" variant="outlined" prepend-icon="mdi-eye-outline"
                    :loading="preview.loading === 'preview_daily_report'" @click="runPreview('preview_daily_report', '每日汇报预览')">
                    预览（不发送）
                  </VBtn>
                </div>
              </VForm>
            </div>

            <!-- 每日汇报 · 订阅提醒 -->
            <div v-show="activeSub === 'subscribe'" class="aoa-pane">
              <VForm>
                <div class="aoa-section-title">订阅提醒</div>
                <VRow>
                  <VCol cols="12" md="6">
                    <VSwitch v-model="form.subscribe_in_report" color="primary" inset hide-details
                      label="在每日汇报中包含订阅追新" />
                    <div class="aoa-hint">汇报正文加入今日订阅追新清单。</div>
                  </VCol>
                  <VCol cols="12" md="6">
                    <VSwitch v-model="form.subscribe_reminder_enabled" color="primary" inset hide-details
                      label="启用独立订阅提醒推送" />
                    <div class="aoa-hint">在指定时间单独推送订阅追新提醒。</div>
                  </VCol>
                </VRow>
                <VRow>
                  <VCol cols="12" md="4">
                    <VTextField v-model="form.subscribe_reminder_time" label="提醒时间（小时 0-23）"
                      type="number" min="0" max="23" :disabled="!form.subscribe_reminder_enabled" />
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
                <VRow>
                  <VCol cols="12">
                    <VSwitch v-model="form.subscribe_reminder_onlyonce" color="warning" inset hide-details
                      label="保存后立即运行一次订阅提醒" :disabled="!form.subscribe_reminder_enabled" />
                  </VCol>
                </VRow>
              </VForm>
            </div>

            <!-- 每日汇报 · 站点数据统计 -->
            <div v-show="activeSub === 'sites'" class="aoa-pane">
              <VForm>
                <div class="aoa-section-title">站点数据统计</div>
                <VRow>
                  <VCol cols="12" md="6">
                    <VSwitch v-model="form.site_stat_in_report" color="primary" inset hide-details
                      label="在每日汇报中包含站点增量" />
                    <div class="aoa-hint">汇报正文加入站点上传/做种等增量数据。</div>
                  </VCol>
                  <VCol cols="12" md="6">
                    <VSwitch v-model="form.site_stat_enabled" color="primary" inset hide-details
                      label="启用站点数据统计采集" />
                    <div class="aoa-hint">关闭后不再统计站点数据。</div>
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
                <VRow>
                  <VCol cols="12">
                    <VSwitch v-model="form.site_stat_onlyonce" color="warning" inset hide-details
                      label="保存后立即运行一次站点统计" :disabled="!form.site_stat_enabled" />
                  </VCol>
                </VRow>
              </VForm>
            </div>

            <!-- 每日汇报 · 健康巡查 -->
            <div v-show="activeSub === 'health'" class="aoa-pane">
              <VForm>
                <div class="aoa-section-title">健康巡查</div>
                <VRow>
                  <VCol cols="12">
                    <VSwitch v-model="form.health_in_report" color="primary" inset hide-details
                      label="在每日汇报中包含健康巡查摘要" />
                    <div class="aoa-hint">汇报正文加入站点 / 下载器 / 存储 / 入库的健康检查结论。</div>
                  </VCol>
                </VRow>
                <VDivider class="my-4" />
                <div class="aoa-section-title">手动触发</div>
                <div class="aoa-btn-row">
                  <VBtn color="primary" variant="tonal" prepend-icon="mdi-heart-pulse"
                    :loading="action.running === 'run_health_check'" @click="runAction('run_health_check', '健康巡查')">
                    立即巡查
                  </VBtn>
                </div>
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
                    <div class="aoa-hint">按计划打包配置目录到本地备份路径。</div>
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
                    <VSelect v-model="form.backup_keep_count" :items="keepCountPresets"
                      label="本地保留份数" :disabled="!form.backup_enabled" />
                  </VCol>
                </VRow>
                <VRow>
                  <VCol cols="12" md="6">
                    <VSwitch v-model="form.backup_notify" color="primary" inset hide-details
                      label="备份结果通知" :disabled="!form.backup_enabled" />
                  </VCol>
                  <VCol cols="12" md="6">
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
                    <div class="aoa-hint">本地备份完成后同步上传到 WebDAV。</div>
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
                  <VCol cols="12" md="6">
                    <VSelect v-model="form.backup_webdav_max_count" :items="keepCountPresets"
                      label="远端保留份数" :disabled="!form.backup_webdav_enabled" />
                  </VCol>
                  <VCol cols="12" md="6">
                    <VSwitch v-model="form.backup_webdav_notify" color="primary" inset hide-details
                      label="远端备份结果通知" :disabled="!form.backup_webdav_enabled" />
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
                    <div class="aoa-hint">按计划裁剪插件日志文件，仅保留指定行数。</div>
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
                    <div class="aoa-hint">从已安装插件中选择；不选则清理全部插件日志。</div>
                  </VCol>
                </VRow>
                <VRow>
                  <VCol cols="12" md="6">
                    <VSwitch v-model="form.log_clean_notify" color="primary" inset hide-details
                      label="清理结果通知" :disabled="!form.log_clean_enabled" />
                  </VCol>
                  <VCol cols="12" md="6">
                    <VSwitch v-model="form.log_clean_onlyonce" color="warning" inset hide-details
                      label="保存后立即清理一次" :disabled="!form.log_clean_enabled" />
                  </VCol>
                </VRow>
                <VDivider class="my-4" />
                <div class="aoa-section-title">手动触发</div>
                <div class="aoa-btn-row">
                  <VBtn color="primary" variant="outlined" prepend-icon="mdi-eye-outline"
                    :loading="preview.loading === 'preview_log_clean'" @click="runPreview('preview_log_clean', '日志清理预览')">
                    预览清理范围
                  </VBtn>
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
                <div class="aoa-hint mb-2">仅检查并通知是否有新版本，不会在这里直接升级。</div>
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
                  <VCol cols="12" md="6">
                    <VSelect v-model="form.mp_update_types" :items="mpUpdateTypes"
                      label="检查范围" multiple chips closable-chips :disabled="!form.mp_update_enabled" />
                  </VCol>
                  <VCol cols="12" md="6">
                    <VSwitch v-model="form.mp_update_notify" color="primary" inset hide-details
                      label="发现新版本时通知" :disabled="!form.mp_update_enabled" />
                  </VCol>
                </VRow>
                <VRow>
                  <VCol cols="12">
                    <VSwitch v-model="form.mp_update_restart_confirm" color="warning" inset hide-details
                      label="允许自动重启以应用更新（高风险，谨慎开启）" :disabled="!form.mp_update_enabled" />
                    <div class="aoa-hint">默认仅提醒；开启后将在更新后尝试重启 MoviePilot。</div>
                  </VCol>
                </VRow>
                <VDivider class="my-4" />
                <div class="aoa-btn-row">
                  <VBtn color="primary" variant="outlined" prepend-icon="mdi-eye-outline"
                    :loading="preview.loading === 'preview_updates'" @click="runPreview('preview_updates', '更新状态预览')">
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
                    <div class="aoa-hint">按间隔检查已安装插件是否有新版本。</div>
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
                <div class="aoa-btn-row">
                  <VBtn color="primary" variant="outlined" prepend-icon="mdi-eye-outline"
                    :loading="preview.loading === 'preview_market_update'" @click="runPreview('preview_market_update', '插件库更新预览')">
                    预览更新
                  </VBtn>
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
                    <div class="aoa-hint">从已安装插件中多选。先“预览”确认范围，再“执行”清理。</div>
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
                  <VCol cols="12" md="6">
                    <VSwitch v-model="form.plugin_uninstall_notify" color="primary" inset hide-details
                      label="清理结果通知" />
                  </VCol>
                  <VCol cols="12" md="6">
                    <VSwitch v-model="form.plugin_uninstall_delete_source" color="error" inset hide-details
                      label="删除本地源码（高风险，不可恢复）" />
                    <div class="aoa-hint">仅对本地源码插件生效，删除后需重新安装。</div>
                  </VCol>
                </VRow>
                <VDivider class="my-4" />
                <div class="aoa-section-title">执行</div>
                <div class="aoa-btn-row">
                  <VBtn color="primary" variant="outlined" prepend-icon="mdi-eye-outline"
                    :disabled="!form.plugin_uninstall_ids || !form.plugin_uninstall_ids.length"
                    :loading="preview.loading === 'preview_plugin_uninstall'" @click="runPreview('preview_plugin_uninstall', '插件残留治理预览')">
                    预览清理范围
                  </VBtn>
                  <VBtn color="error" variant="tonal" prepend-icon="mdi-broom"
                    :disabled="!form.plugin_uninstall_ids || !form.plugin_uninstall_ids.length"
                    :loading="action.running === 'run_plugin_uninstall'" @click="runAction('run_plugin_uninstall', '插件残留治理')">
                    执行清理
                  </VBtn>
                </div>
                <div class="aoa-hint mt-2">残留清理为不可逆操作，执行前请务必先预览确认。</div>
              </VForm>
            </div>
          </div>
        </section>
      </div>
      <VDivider />
      <VCardActions class="aoa-actions">
        <VFadeTransition>
          <span v-if="action.message" :class="action.ok ? 'text-success' : 'text-error'" class="text-caption">
            <VIcon :icon="action.ok ? 'mdi-check-circle-outline' : 'mdi-alert-circle-outline'" size="16" class="mr-1" />{{ action.message }}
          </span>
        </VFadeTransition>
        <VSpacer />
        <VBtn variant="text" @click="emit('close')">取消</VBtn>
        <VBtn color="primary" variant="flat" prepend-icon="mdi-content-save-outline" @click="saveConfig">保存配置</VBtn>
      </VCardActions>
    </VCard>

    <VDialog v-model="preview.open" max-width="640" scrollable>
      <VCard class="aoa-preview-card">
        <VCardItem>
          <template #prepend>
            <VIcon icon="mdi-eye-outline" color="primary" />
          </template>
          <VCardTitle class="text-subtitle-1">{{ preview.title }}</VCardTitle>
        </VCardItem>
        <VDivider />
        <VCardText class="aoa-preview-body">
          <pre class="aoa-preview-text">{{ preview.text }}</pre>
        </VCardText>
        <VDivider />
        <VCardActions>
          <VSpacer />
          <VBtn variant="text" @click="preview.open = false">关闭</VBtn>
        </VCardActions>
      </VCard>
    </VDialog>
  </div>
</template>
<style scoped>
.aoa-config {
  padding: 8px;
}
.aoa-card {
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
}
.aoa-header {
  padding: 14px 18px;
}
.aoa-body {
  display: flex;
  min-height: 460px;
}
.aoa-nav {
  width: 188px;
  flex: 0 0 188px;
  border-right: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  background: rgba(var(--v-theme-on-surface), 0.02);
}
.aoa-nav-item {
  margin: 2px 8px;
}
.aoa-content {
  flex: 1 1 auto;
  min-width: 0;
  display: flex;
  flex-direction: column;
}
.aoa-subtabs {
  flex: 0 0 auto;
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  padding: 8px 12px;
}
.aoa-subtab {
  display: inline-flex;
  align-items: center;
  padding: 6px 14px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 500;
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
.aoa-window {
  flex: 1 1 auto;
}
.aoa-pane {
  padding: 18px 20px;
}
.aoa-section-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 8px;
  color: rgb(var(--v-theme-primary));
}
.aoa-hint {
  font-size: 12px;
  line-height: 1.5;
  color: rgba(var(--v-theme-on-surface), 0.6);
  margin-top: 2px;
}
.aoa-btn-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}
.aoa-actions {
  padding: 10px 18px;
}
.aoa-preview-body {
  max-height: 60vh;
  padding: 16px 20px;
}
.aoa-preview-text {
  margin: 0;
  font-family: inherit;
  font-size: 13px;
  line-height: 1.7;
  white-space: pre-wrap;
  word-break: break-word;
  color: rgba(var(--v-theme-on-surface), 0.85);
}
@media (max-width: 760px) {
  .aoa-body {
    flex-direction: column;
  }
  .aoa-nav {
    width: 100%;
    flex: 0 0 auto;
    border-right: none;
    border-bottom: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  }
}
</style>
