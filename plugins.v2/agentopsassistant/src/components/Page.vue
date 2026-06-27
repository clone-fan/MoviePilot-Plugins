<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useTheme } from 'vuetify'
import { actionMessageFromResponse, getPluginApi, getPluginApiRaw, postPluginApi } from './api'

const props = defineProps({
  api: { type: [Object, Function], default: null },
  surface: { type: String, default: 'dialog' },
})
const emit = defineEmits(['close', 'switch'])

const loading = ref(true)
const error = ref('')
const actionRunning = ref('')
const actionMessage = ref('')
const actionOk = ref(true)
const vuetifyTheme = useTheme()
const data = reactive({
  enabled: false,
  summary: '',
  tasks: [],
  task_total: 0,
  task_on: 0,
  task_failed: 0,
  health: { time: '', success: null, output: '' },
})

const siteChart = reactive({
  date: '',
  basis: 'idle',
  sites: [],
  upload_total: 0,
  download_total: 0,
  data_valid: false,
  message: '',
  error: '',
  last_error: '',
})
const downloaders = ref([])
const downloaderOverviewMessage = ref('')
const dashboardThemeClass = computed(() => {
  const name = String(vuetifyTheme.global.name.value || '').toLowerCase()
  if (name.includes('transparent')) return 'agentops-theme--transparent'
  if (name.includes('light')) return 'agentops-theme--light'
  return ''
})
const isSidebarSurface = computed(() => props.surface === 'sidebar')
const isPluginDisabled = computed(() => !data.enabled)
const actionsDisabled = computed(() => isPluginDisabled.value)

const overallColor = computed(() => {
  if (!data.enabled) return 'muted'
  if (data.task_failed > 0 || data.health.success === false) return 'red'
  return 'green'
})
const overallText = computed(() => {
  if (!data.enabled) return '未启用'
  return '正常'
})
const healthColor = computed(() => {
  if (data.health.success === true) return 'success'
  if (data.health.success === false) return 'error'
  return 'grey'
})
const healthText = computed(() => {
  if (data.health.success === true) return '通过'
  if (data.health.success === false) return '存在异常'
  return '尚未巡查'
})

async function loadDashboard() {
  loading.value = true
  error.value = ''
  try {
    const res = await getPluginApi(props.api, 'dashboard')
    Object.assign(data, res || {})
  } catch (err) {
    error.value = err?.message || '仪表盘数据加载失败'
  } finally {
    loading.value = false
  }
}

function actionComponentEnabled(action) {
  if (!action?.component) return true
  const task = (data.tasks || []).find(item => item?.key === action.component)
  return !!data.enabled && !!task?.enabled
}

function actionComponentDisabledMessage(action) {
  if (!action?.component || actionComponentEnabled(action)) return ''
  const task = (data.tasks || []).find(item => item?.key === action.component)
  return `${task?.name || action.label || '组件'}未启用，手动命令已暂停`
}

async function runAction(action) {
  if (actionRunning.value) return
  if (actionsDisabled.value) {
    actionOk.value = false
    actionMessage.value = '插件总开关未启用，手动命令已暂停'
    setTimeout(() => { actionMessage.value = '' }, 5000)
    return
  }
  const disabledMessage = actionComponentDisabledMessage(action)
  if (disabledMessage) {
    actionOk.value = false
    actionMessage.value = disabledMessage
    setTimeout(() => { actionMessage.value = '' }, 5000)
    return
  }
  const path = action.path
  actionRunning.value = path
  actionMessage.value = ''
  actionOk.value = true
  try {
    const res = await postPluginApi(props.api, path)
    const ok = !!res && res.code === 0
    actionOk.value = ok
    actionMessage.value = actionMessageFromResponse(res, action.label)
    setTimeout(() => { actionMessage.value = '' }, 5000)
    if (ok) {
      loadDashboard()
      loadSiteChart()
      loadDownloaderOverview()
    }
  } catch (err) {
    actionOk.value = false
    actionMessage.value = actionMessageFromResponse({ code: 1, msg: err?.message }, action.label)
    setTimeout(() => { actionMessage.value = '' }, 5000)
  } finally {
    actionRunning.value = ''
  }
}

function formatGB(bytes) {
  const n = Number(bytes) || 0
  const gb = n / (1024 ** 3)
  if (gb >= 1) return gb.toFixed(2) + ' GB'
  return (n / (1024 ** 2)).toFixed(1) + ' MB'
}

const siteRows = computed(() => [...(siteChart.sites || [])].sort((a, b) => ((b.upload || 0) + (b.download || 0)) - ((a.upload || 0) + (a.download || 0))))
const sitePieColors = [
  { color: 'rgba(var(--green), 0.94)', glow: 'rgba(var(--green), 0.28)' },
  { color: 'rgba(var(--cyan), 0.90)', glow: 'rgba(var(--cyan), 0.26)' },
  { color: 'rgba(var(--amber), 0.88)', glow: 'rgba(var(--amber), 0.24)' },
  { color: 'rgba(var(--blue), 0.88)', glow: 'rgba(var(--blue), 0.24)' },
  { color: 'rgba(var(--red), 0.84)', glow: 'rgba(var(--red), 0.22)' },
  { color: 'rgba(var(--violet), 0.86)', glow: 'rgba(var(--violet), 0.23)' },
  { color: 'color-mix(in srgb, rgb(var(--green)) 62%, rgb(var(--blue)))', glow: 'rgba(var(--green), 0.20)' },
  { color: 'color-mix(in srgb, rgb(var(--amber)) 68%, rgb(var(--cyan)))', glow: 'rgba(var(--amber), 0.20)' },
]
const siteTrafficTotal = computed(() => siteRows.value.reduce((sum, site) => sum + (Number(site.upload) || 0) + (Number(site.download) || 0), 0))
const siteDateLabel = computed(() => {
  if (!siteChart.date) return '—'
  return siteChart.basis === 'latest' ? `最近快照 ${siteChart.date}` : siteChart.date
})
const siteDateNote = computed(() => {
  if (!siteChart.date) return '等待统计'
  return siteChart.basis === 'latest' ? '最近快照' : '今天 00:00 后'
})
const sitePieSegments = computed(() => {
  const total = siteTrafficTotal.value
  if (!total) return []
  let cursor = 0
  return siteRows.value.map((site, index) => {
    const value = (Number(site.upload) || 0) + (Number(site.download) || 0)
    const start = cursor
    const end = cursor + (value / total) * 100
    cursor = end
    const palette = sitePieColors[index % sitePieColors.length]
    return { ...site, value, start, end, color: palette.color, glow: palette.glow }
  })
})
const sitePieStyle = computed(() => {
  if (!sitePieSegments.value.length) {
    return {
      background: 'conic-gradient(rgba(var(--line), 0.16) 0 82deg, rgba(var(--line), 0.055) 82deg 360deg)',
    }
  }
  const stops = sitePieSegments.value
    .map(item => `${item.color} ${item.start.toFixed(2)}% ${item.end.toFixed(2)}%`)
    .join(', ')
  return { background: `conic-gradient(${stops})` }
})
const siteTableRows = computed(() => sitePieSegments.value.slice(0, 6))
const hasSiteChart = computed(() => !!(siteChart.sites && siteChart.sites.length))
const siteEmptyTitle = computed(() => {
  if (siteChart.last_error || siteChart.error) return '站点统计失败'
  if (siteChart.basis === 'skipped') return '站点统计未启用'
  if (siteChart.data_valid === true) return '暂无站点增量'
  if (siteChart.basis === 'latest') return '暂无今日增量'
  return '等待站点统计'
})
const siteEmptyDesc = computed(() => {
  if (siteChart.last_error || siteChart.error) return siteChart.last_error || siteChart.error
  if (siteChart.message) return siteChart.message
  if (siteChart.basis === 'skipped') return '启用插件和站点统计组件后，可手动刷新生成数据'
  if (siteChart.data_valid === true) return '已刷新但没有可展示的上传/下载增量'
  if (siteChart.basis === 'latest') return '今日基线不足，暂用最近快照等待下一次刷新'
  return '点击立即刷新或站点统计后显示最新可用数据'
})

function sitePercent(value) {
  const total = siteTrafficTotal.value
  if (!total) return '0%'
  return `${Math.round(((Number(value) || 0) / total) * 100)}%`
}

async function loadSiteChart() {
  try {
    const res = await getPluginApiRaw(props.api, 'site_stat_chart')
    const payload = res && typeof res === 'object' && 'data' in res ? res.data : res
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
    })
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
    })
  }
}

async function loadDownloaderOverview() {
  try {
    const res = await getPluginApiRaw(props.api, 'downloader_overview')
    const payload = res && typeof res === 'object' && 'data' in res ? res.data : res
    downloaders.value = (payload && payload.downloaders) || []
    downloaderOverviewMessage.value = payload?.message || res?.msg || ''
  } catch {
    downloaders.value = []
    downloaderOverviewMessage.value = '下载器活动获取失败'
  }
}

const healthItems = computed(() => {
  const iconMap = {
    订阅: 'mdi-bell-ring-outline',
    站点: 'mdi-satellite-uplink',
    下载器: 'mdi-download-network-outline',
    本插件任务: 'mdi-puzzle-check-outline',
    数据库: 'mdi-database-check-outline',
    存储空间: 'mdi-harddisk',
    目录权限: 'mdi-folder-check-outline',
  }
  return String(data.health.output || '')
    .split('\n')
    .map(line => line.replace(/^[⦁•\s]+/, '').trim())
    .filter(line => line && !line.includes('状态') && !line.includes('巡查项'))
    .map(line => {
      const ok = !/[⚠❌✖]/.test(line) && !line.includes('异常') && !line.includes('失败')
      const cleaned = line.replace(/[✅⚠️❌✖]/g, '').trim()
      const parts = cleaned.split(/[:：]/)
      const name = (parts.shift() || '巡查项').trim()
      const detail = (parts.join('：') || '无更多信息').trim()
      const detailRows = detail.split(/[；;]/).map(v => v.trim()).filter(Boolean)
      return { name, detail, detailRows, ok, color: ok ? 'success' : 'error', icon: iconMap[name] || 'mdi-check-decagram-outline' }
    })
    .sort((a, b) => Number(a.ok) - Number(b.ok))
})

function isTaskBad(task) {
  if (!isTaskOn(task)) return false
  return task?.color === 'error' || /失败|异常|错误/.test(String(task?.state || ''))
}

function isTaskOn(task) {
  return !!data.enabled && !!task?.enabled
}

const taskCards = computed(() => [...(data.tasks || [])].sort((a, b) => {
  const aw = isTaskBad(a) ? 0 : isTaskOn(a) ? 1 : 2
  const bw = isTaskBad(b) ? 0 : isTaskOn(b) ? 1 : 2
  return aw - bw
}))

const issueItems = computed(() => {
  if (isPluginDisabled.value) return []
  const healthProblems = healthItems.value.filter(item => !item.ok)
  if (healthProblems.length) return healthProblems
  const taskProblems = taskCards.value
    .filter(isTaskBad)
    .map(task => ({
      name: task.name || '任务异常',
      detail: `${task.state || '异常'}${task.last_time ? `，最近 ${task.last_time}` : ''}`,
      detailRows: [],
      ok: false,
    }))
  if (taskProblems.length) return taskProblems
  return []
})
const issueCount = computed(() => (isPluginDisabled.value ? 0 : Math.max(Number(data.task_failed) || 0, issueItems.value.length)))
const primaryIssue = computed(() => {
  if (isPluginDisabled.value) return { name: '运行状态', detail: '插件当前未启用', detailRows: [], ok: true }
  return issueItems.value[0] || { name: '系统状态', detail: '当前任务和健康巡查未发现阻塞项', detailRows: [], ok: true }
})
const issueTitle = computed(() => {
  if (isPluginDisabled.value) return '插件已停用'
  return issueCount.value > 0 ? `${issueCount.value} 项需要处理` : '运行平稳'
})
const issueDesc = computed(() => {
  if (error.value) return error.value
  if (isPluginDisabled.value) return '插件未启用时不会运行定时任务或业务链路，仪表盘仅展示当前配置快照'
  if (issueCount.value > 0) return `健康巡查发现${primaryIssue.value.name}异常，仪表盘优先展示具体路径和原因`
  return '任务调度与健康巡查处于稳定状态'
})

const lastRunLabel = computed(() => {
  if (data.health.time) return data.health.time.slice(11, 16) || data.health.time
  const last = taskCards.value.find(task => task.last_time)?.last_time
  return last ? String(last).slice(11, 16) : '—'
})

const metricCards = computed(() => [
  { label: '运行状态', value: overallText.value, icon: 'mdi-check', tone: overallColor.value },
  { label: '启用组件', value: `${data.enabled ? data.task_on : 0} / ${data.task_total}`, icon: 'mdi-layers-triple-outline', tone: 'blue' },
  { label: '异常组件', value: String(issueCount.value), icon: 'mdi-shield-alert-outline', tone: issueCount.value ? 'red' : 'green' },
  { label: '站点流量', value: formatGB(siteTrafficTotal.value), icon: 'mdi-chart-line-variant', tone: 'amber' },
])

const quickActions = [
  { path: 'create_tg_console_card', component: '', label: '立即建卡', icon: 'mdi-card-plus-outline', tone: 'green' },
  { path: 'run_daily_report', component: 'daily_report', label: '立即刷新', icon: 'mdi-refresh', tone: 'green' },
]

const actionGroups = [
  {
    group: '汇报与追新',
    icon: 'mdi-newspaper-variant-outline',
    actions: [
      { path: 'run_subscribe_reminder', component: 'subscribe_reminder', label: '订阅追新', icon: 'mdi-bell-badge-outline', tone: 'blue' },
    ],
  },
  {
    group: '站点与下载器',
    icon: 'mdi-download-network-outline',
    actions: [
      { path: 'run_site_stat', component: 'site_stat', label: '站点统计', icon: 'mdi-chart-pie', tone: 'blue' },
      { path: 'run_downloader_tag', component: 'downloader_tag', label: '种子标签', icon: 'mdi-tag-plus-outline', tone: 'cyan' },
      { path: 'run_seed_clean', component: 'seed_clean', label: '自动删种', icon: 'mdi-delete-sweep-outline', tone: 'red' },
    ],
  },
  {
    group: '系统维护',
    icon: 'mdi-cog-outline',
    actions: [
      { path: 'run_backup', component: 'backup', label: '配置备份', icon: 'mdi-database-arrow-up-outline', tone: 'violet' },
      { path: 'run_log_clean', component: 'log_clean', label: '日志清理', icon: 'mdi-broom', tone: 'violet' },
      { path: 'run_health_check', component: 'health_check', label: '健康巡查', icon: 'mdi-heart-pulse', tone: 'green' },
      { path: 'run_mp_update', component: 'mp_update', label: 'MP 更新', icon: 'mdi-update', tone: 'amber' },
    ],
  },
  {
    group: '插件治理',
    icon: 'mdi-puzzle-check-outline',
    actions: [
      { path: 'run_market_update', component: 'market_update', label: '插件更新', icon: 'mdi-cloud-sync-outline', tone: 'amber' },
    ],
  },
]
const actionItems = computed(() => actionGroups.flatMap(group => group.actions))

onMounted(() => {
  loadDashboard()
  loadSiteChart()
  loadDownloaderOverview()
})
</script>

<template>
  <div class="agentops-dashboard dashboard-shell" :class="[dashboardThemeClass, { 'dashboard-shell--sidebar': isSidebarSurface }]">
    <VCard class="agentops-frame" elevation="0">
      <header class="agentops-toolbar">
        <div class="brand">
          <span class="brand-mark"><VIcon icon="mdi-view-dashboard-outline" size="20" /></span>
          <span class="brand-title">MP 运维助手 · 仪表盘</span>
          <small>最后 {{ lastRunLabel }}</small>
        </div>
        <div class="toolbar-space"></div>
        <VBtn size="small" variant="text" class="top-button top-button--primary text-none" :loading="loading" @click="loadDashboard">
          刷新
        </VBtn>
        <VBtn v-if="!isSidebarSurface" size="small" variant="text" class="top-button text-none" @click="emit('switch')">设置</VBtn>
        <VBtn v-if="!isSidebarSurface" size="small" icon="mdi-close" variant="text" class="top-button top-button--icon" @click="emit('close')" />
      </header>

      <section class="dashboard-canvas">
        <article class="panel alert-panel" :class="{ 'alert-panel--ok': issueCount === 0 && !error && !isPluginDisabled, 'alert-panel--idle': isPluginDisabled && !error }">
          <div class="alert-top">
            <div class="alert-icon">
              <VIcon :icon="isPluginDisabled && !error ? 'mdi-power-standby' : issueCount || error ? 'mdi-alert-outline' : 'mdi-shield-check-outline'" size="28" />
            </div>
            <div class="alert-copy">
              <h1>{{ error ? '数据加载失败' : issueTitle }}</h1>
              <p>{{ issueDesc }}</p>
            </div>
          </div>
          <div class="alert-line">
            <b>{{ primaryIssue.name }}</b>
            <strong>{{ primaryIssue.detail }}</strong>
            <span class="badge" :class="{ 'badge--ok': issueCount === 0 && !error && !isPluginDisabled, 'badge--idle': isPluginDisabled && !error }">{{ error ? '异常' : isPluginDisabled ? '停用' : issueCount ? '异常' : '正常' }}</span>
          </div>
        </article>

        <section class="metrics-panel">
          <article v-for="metric in metricCards" :key="metric.label" class="metric-card" :class="`metric-card--${metric.tone}`">
            <div class="metric-symbol"><VIcon :icon="metric.icon" size="28" /></div>
            <div class="metric-copy">
              <p>{{ metric.label }}</p>
              <strong>{{ metric.value }}</strong>
            </div>
          </article>
        </section>

        <article class="panel site-panel">
          <div class="panel-head">
            <span class="panel-icon panel-icon--cyan"><VIcon icon="mdi-chart-line" size="20" /></span>
            <h2>站点数据统计</h2>
            <span class="panel-note">{{ siteDateNote }}</span>
          </div>
          <div v-if="hasSiteChart" class="site-body">
            <div class="donut-zone">
              <div class="donut" :style="sitePieStyle">
                <div class="donut-core">
                  <strong>{{ siteRows.length }}</strong>
                  <span>站点</span>
                </div>
              </div>
            </div>
            <div class="site-data">
              <div class="site-stats">
                <div class="site-stat">
                  <span>上传增量</span>
                  <strong>{{ formatGB(siteChart.upload_total) }}</strong>
                </div>
                <div class="site-stat">
                  <span>下载增量</span>
                  <strong>{{ formatGB(siteChart.download_total) }}</strong>
                </div>
                <div class="site-stat">
                  <span>统计日期</span>
                  <strong>{{ siteDateLabel }}</strong>
                </div>
              </div>
              <div class="site-list site-legend">
                <div v-for="site in siteTableRows" :key="site.name" class="site-card">
                  <div class="site-card-head">
                    <span class="site-table-name">
                      <i class="dot" :style="{ background: site.color, boxShadow: `0 0 8px ${site.glow}` }"></i>
                      <span class="site-name">{{ site.name }}</span>
                    </span>
                    <strong class="site-percent">{{ sitePercent(site.value) }}</strong>
                  </div>
                  <div class="site-card-metrics">
                    <span class="site-row-cell site-upload">↑ {{ formatGB(site.upload) }}</span>
                    <span class="site-row-cell site-download">↓ {{ formatGB(site.download) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div v-else class="site-empty-state">
            <div class="site-empty-main">
              <span class="site-empty-icon"><VIcon icon="mdi-chart-pie" size="19" /></span>
              <div>
                <strong>{{ siteEmptyTitle }}</strong>
                <span>{{ siteEmptyDesc }}</span>
              </div>
            </div>
            <div class="site-empty-stats">
                <div class="site-stat">
                  <span>上传增量</span>
                  <strong>0.0 MB</strong>
                </div>
                <div class="site-stat">
                  <span>下载增量</span>
                  <strong>0.0 MB</strong>
                </div>
                <div class="site-stat">
                  <span>统计日期</span>
                  <strong>等待统计</strong>
                </div>
            </div>
          </div>
        </article>

        <aside class="panel command-panel action-panel">
          <div class="panel-head command-head">
            <span class="panel-icon panel-icon--cyan"><VIcon icon="mdi-view-grid-outline" size="20" /></span>
            <h2>命令面板</h2>
            <span class="panel-note">{{ actionItems.length }} 项</span>
          </div>
          <div class="command-body action-scroll">
            <section class="command-group command-quick-card" aria-label="融合通知快捷操作">
              <div class="command-quick-copy">
                <span>融合通知</span>
                <strong>运维卡快捷操作</strong>
              </div>
              <div class="command-quick-buttons">
                <VBtn
                  v-for="quick in quickActions"
                  :key="quick.path"
                  variant="text"
                  density="comfortable"
                  :loading="actionRunning === quick.path"
                  :disabled="actionsDisabled || !actionComponentEnabled(quick) || (!!actionRunning && actionRunning !== quick.path)"
                  :title="quick.label"
                  class="command-quick-btn text-none"
                  @click="runAction(quick)"
                >
                  <VIcon :icon="quick.icon" size="20" />
                  <span class="command-quick-label">{{ quick.label }}</span>
                </VBtn>
              </div>
            </section>
            <section v-for="group in actionGroups" :key="group.group" class="command-group">
              <div class="group-head">
                <span>{{ group.group }}</span>
                <span>{{ group.actions.length }} 项</span>
              </div>
              <div class="cmd-grid action-buttons">
                <VBtn
                  v-for="action in group.actions"
                  :key="action.path"
                  variant="text"
                  density="comfortable"
                  :loading="actionRunning === action.path"
                  :disabled="actionsDisabled || !actionComponentEnabled(action) || (!!actionRunning && actionRunning !== action.path)"
                  :title="actionComponentDisabledMessage(action)"
                  class="cmd-btn action-btn action-item text-none"
                  :class="[`cmd-btn--${action.tone}`, `action-btn--${action.tone}`]"
                  @click="runAction(action)"
                >
                  <VIcon :icon="action.icon" size="16" />
                  <span class="action-btn-label">{{ action.label }}</span>
                </VBtn>
              </div>
            </section>
          </div>
          <VAlert v-if="actionMessage" :type="actionOk ? 'success' : 'error'" variant="tonal" density="compact" class="action-message" :icon="false" :text="actionMessage" />
        </aside>

        <article class="panel download-panel">
          <div class="panel-head">
            <span class="panel-icon panel-icon--blue"><VIcon icon="mdi-download" size="20" /></span>
            <h2>下载器活动</h2>
          </div>
          <div v-if="downloaders.length" class="download-body">
            <div v-for="d in downloaders" :key="d.name" class="downloader-card">
              <div>
                <strong>{{ d.name }}</strong>
                <span>下载中 {{ d.count }} 个 ｜ ↓ {{ formatGB(d.dl_speed) }}/s ｜ ↑ {{ formatGB(d.up_speed) }}/s</span>
              </div>
              <span class="ok-chip">运行中</span>
            </div>
          </div>
          <div v-else class="download-body download-body--empty">
            <div class="downloader-card downloader-card--empty">
              <div>
                <strong>{{ downloaderOverviewMessage ? '下载器活动已跳过' : '暂无活动下载器' }}</strong>
                <span>{{ downloaderOverviewMessage || '刷新后同步正在下载的任务' }}</span>
              </div>
              <span class="ok-chip ok-chip--idle">等待</span>
            </div>
            <div v-if="!downloaderOverviewMessage" class="downloader-card downloader-card--empty downloader-card--ghost">
              <div>
                <strong>下载器快照</strong>
                <span>连接后显示实时上下行速度</span>
              </div>
              <span class="ok-chip ok-chip--idle">空闲</span>
            </div>
          </div>
        </article>

        <article class="panel runtime-panel">
          <div class="panel-head">
            <span class="panel-icon panel-icon--cyan"><VIcon icon="mdi-format-list-bulleted" size="20" /></span>
            <h2>组件运行状况</h2>
            <span class="panel-note">异常优先</span>
          </div>
          <VSkeletonLoader v-if="loading" class="runtime-loader" type="list-item-two-line@4" />
          <div v-else class="runtime-track task-grid">
            <div v-for="task in taskCards" :key="task.key" class="module task-card" :class="{ 'module--bad': isTaskBad(task), 'module--off': !isTaskOn(task) }">
              <div class="module-top">
                <i class="dot" :class="{ red: isTaskBad(task), gray: !isTaskOn(task) }"></i>
                <span class="module-title">{{ task.name }}</span>
                <span class="state" :class="{ bad: isTaskBad(task), off: !isTaskOn(task) }">{{ isTaskBad(task) ? '失败' : isTaskOn(task) ? 'ON' : 'OFF' }}</span>
              </div>
              <div class="module-note">{{ task.next ? `下次 ${task.next}` : task.last_time ? `最近 ${task.last_time}` : '等待调度' }}</div>
            </div>
            <div v-if="!taskCards.length" class="module module--empty">
              <div class="module-top">
                <i class="dot gray"></i>
                <span class="module-title">暂无任务</span>
                <span class="state off">OFF</span>
              </div>
              <div class="module-note">启用配置后显示调度状态</div>
            </div>
          </div>
        </article>
      </section>
    </VCard>
  </div>
</template>

<style scoped>
.agentops-dashboard {
  /* 外框：MP 官方 surface */
  --aoa-dashboard-radius: var(--v-card-border-radius, var(--app-surface-radius, 12px));
  --mp-panel-radius: var(--app-surface-radius, 12px);
  --mp-cell-radius: var(--app-field-radius, 10px);
  --mp-panel-border: var(--app-surface-border, 1px solid rgba(var(--v-border-color), var(--v-border-opacity, 0.12)));
  --mp-panel-shadow: var(--app-surface-shadow, none);
  --mp-cell-hover-shadow: var(--app-surface-hover-shadow, none);
  --aoa-outer-surface-opacity: var(--transparent-opacity, var(--v-card-opacity, 1));
  --aoa-outer-surface: rgba(var(--v-theme-surface), var(--aoa-outer-surface-opacity));
  --aoa-inner-surface-alpha-hi: 0.56;
  --aoa-inner-surface-alpha-lo: 0.42;
  --aoa-inner-surface-tint: 0.10;
  --aoa-inner-strong-alpha-hi: 0.66;
  --aoa-inner-strong-alpha-lo: 0.50;
  --aoa-inner-strong-tint: 0.14;
  --aoa-inner-muted-alpha-hi: 0.48;
  --aoa-inner-muted-alpha-lo: 0.34;
  --aoa-inner-muted-tint: 0.09;
  --aoa-inner-surface:
    linear-gradient(180deg, rgba(var(--v-theme-surface), var(--aoa-inner-surface-alpha-hi)), rgba(var(--v-theme-surface), var(--aoa-inner-surface-alpha-lo))),
    rgba(var(--v-theme-on-surface), var(--aoa-inner-surface-tint));
  --aoa-inner-surface-strong:
    linear-gradient(180deg, rgba(var(--v-theme-surface), var(--aoa-inner-strong-alpha-hi)), rgba(var(--v-theme-surface), var(--aoa-inner-strong-alpha-lo))),
    rgba(var(--v-theme-on-surface), var(--aoa-inner-strong-tint));
  --aoa-inner-surface-muted:
    linear-gradient(180deg, rgba(var(--v-theme-surface), var(--aoa-inner-muted-alpha-hi)), rgba(var(--v-theme-surface), var(--aoa-inner-muted-alpha-lo))),
    rgba(var(--v-theme-on-surface), var(--aoa-inner-muted-tint));
  --aoa-inner-border: 1px solid rgba(var(--v-border-color), 0.18);
  --aoa-inner-shadow:
    inset 0 1px 0 rgba(var(--v-theme-on-surface), 0.10),
    inset 0 -1px 0 rgba(0, 0, 0, 0.10),
    0 10px 26px rgba(0, 0, 0, 0.14);
  --aoa-inner-blur: 12px;
  --mp-panel-surface: var(--aoa-outer-surface);
  --mp-cell-surface: var(--aoa-inner-surface-strong);
  --mp-cell-hover-surface: var(--aoa-inner-surface-strong);
  --mp-cell-muted-surface: var(--aoa-inner-surface-muted);
  --mp-cell-shadow: var(--aoa-inner-shadow);
  --mp-blur: none;
  /* 主题着色 token */
  --ink: var(--v-theme-on-surface, 240, 247, 255);
  --muted: var(--v-theme-on-surface, 151, 171, 201);
  --faint: var(--v-theme-on-surface, 111, 131, 163);
  --line: var(--v-theme-on-surface, 255, 255, 255);
  --panel: var(--v-theme-surface, 28, 38, 57);
  --stage: var(--v-theme-background, 8, 15, 27);
  --cyan: var(--v-theme-info, 124, 194, 224);
  --blue: var(--v-theme-primary, 142, 169, 222);
  --green: var(--v-theme-success, 91, 204, 155);
  --amber: var(--v-theme-warning, 218, 179, 93);
  --red: var(--v-theme-error, 232, 104, 124);
  --violet: var(--v-theme-primary, 162, 151, 211);
  /* 默认主题：外框不叠玻璃，内框用 on-surface 透白做层次 */
  --shell-panel-hi: 0.00;
  --shell-panel-lo: 0.00;
  --shell-stage-alpha: 0.00;
  --frame-panel-hi: 0.00;
  --frame-panel-lo: 0.00;
  --frame-stage-alpha: 0.00;
  --toolbar-panel-hi: 0.00;
  --toolbar-panel-lo: 0.00;
  --panel-glass-hi: 0.00;
  --panel-glass-lo: 0.00;
  --panel-fill-alpha: 0.00;
  --panel-inner-alpha: 0.10;
  --panel-inner-strong-alpha: 0.14;
  --status-panel-alpha: 0.00;
  --shell-cyan-alpha: 0.00;
  --shell-blue-alpha: 0.00;
  --frame-cyan-alpha: 0.00;
  --frame-violet-alpha: 0.00;
  --top-button-alpha: 0.04;
  --top-button-primary-alpha: 0.06;
  --status-red-glow-alpha: 0.06;
  --status-green-glow-alpha: 0.05;
  --status-mix-alpha: 0.00;
  --alert-line-alpha: 0.04;
  --metric-accent-alpha: 0.04;
  --site-cyan-alpha: 0.00;
  --site-blue-alpha: 0.00;
  --soft-line-alpha: 0.04;
  --donut-core-line-alpha: 0.04;
  --donut-core-panel-alpha: 0.85;
  --site-cell-line-alpha: 0.04;
  --site-cell-line-low-alpha: 0.02;
  --site-cell-border-alpha: 0.18;
  --site-cell-fill-alpha: 0.12;
  --site-cell-shadow:
    inset 0 1px 0 rgba(var(--line), 0.10),
    inset 0 -1px 0 rgba(0, 0, 0, 0.08),
    0 8px 18px rgba(0, 0, 0, 0.075),
    0 2px 6px rgba(0, 0, 0, 0.045);
  --command-cyan-alpha: 0.060;
  --download-blue-alpha: 0.060;
  --runtime-violet-alpha: 0.050;
  --shadow-panel:
    inset 0 1px 0 rgba(var(--line), 0.105),
    inset 0 -1px 0 rgba(0, 0, 0, 0.13),
    0 12px 26px rgba(0, 0, 0, 0.12),
    0 3px 9px rgba(0, 0, 0, 0.075);
  --shadow-block:
    inset 0 1px 0 rgba(var(--line), 0.085),
    inset 0 -1px 0 rgba(0, 0, 0, 0.11),
    0 8px 16px rgba(0, 0, 0, 0.09),
    0 2px 6px rgba(0, 0, 0, 0.060);
  --shadow-button:
    inset 0 1px 0 rgba(var(--line), 0.095),
    inset 0 -1px 0 rgba(0, 0, 0, 0.10),
    0 4px 9px rgba(0, 0, 0, 0.075),
    0 1px 3px rgba(0, 0, 0, 0.050);
  width: 100%;
  box-sizing: border-box;
  max-height: calc(100dvh - 32px);
  overflow-x: hidden;
  overflow-y: auto;
  overscroll-behavior: contain;
  padding: 8px;
  color: rgba(var(--ink), 0.94);
  font-family: "Microsoft YaHei", "PingFang SC", "Noto Sans SC", system-ui, sans-serif;
}

:global(html[data-theme="transparent"]) .agentops-dashboard,
:global(body[data-theme="transparent"]) .agentops-dashboard,
:global([data-theme="transparent"]) .agentops-dashboard,
:global(.v-theme--transparent) .agentops-dashboard,
:global(.theme--transparent) .agentops-dashboard {
  --aoa-outer-surface-opacity: var(--transparent-opacity, 0.42);
  --aoa-outer-surface: rgba(var(--v-theme-surface), var(--transparent-opacity, 0.42));
  --aoa-inner-surface-alpha-hi: var(--transparent-opacity-heavy, 0.58);
  --aoa-inner-surface-alpha-lo: var(--transparent-opacity, 0.42);
  --aoa-inner-surface-tint: 0.13;
  --aoa-inner-strong-alpha-hi: var(--transparent-opacity-heavy, 0.66);
  --aoa-inner-strong-alpha-lo: var(--transparent-opacity, 0.48);
  --aoa-inner-strong-tint: 0.17;
  --aoa-inner-muted-alpha-hi: var(--transparent-opacity, 0.48);
  --aoa-inner-muted-alpha-lo: var(--transparent-opacity-light, 0.34);
  --aoa-inner-muted-tint: 0.12;
  --aoa-inner-border: 1px solid rgba(var(--v-border-color), 0.22);
  --aoa-inner-blur: var(--transparent-blur, 12px);
  --mp-panel-surface: var(--aoa-outer-surface);
  --mp-cell-surface: var(--aoa-inner-surface-strong);
  --mp-cell-hover-surface: var(--aoa-inner-surface-strong);
  --mp-cell-muted-surface: var(--aoa-inner-surface-muted);
  --mp-panel-border: var(--app-surface-border, 1px solid rgba(var(--v-border-color), var(--v-border-opacity, 0.12)));
  --mp-panel-shadow: var(--app-surface-shadow, none);
  --mp-cell-shadow: var(--aoa-inner-shadow);
  --mp-blur: blur(var(--transparent-blur, 0px));
}

.agentops-dashboard.agentops-theme--light {
  --aoa-inner-surface-alpha-hi: 0.72;
  --aoa-inner-surface-alpha-lo: 0.58;
  --aoa-inner-surface-tint: 0.06;
  --aoa-inner-strong-alpha-hi: 0.82;
  --aoa-inner-strong-alpha-lo: 0.66;
  --aoa-inner-strong-tint: 0.08;
  --aoa-inner-muted-alpha-hi: 0.66;
  --aoa-inner-muted-alpha-lo: 0.50;
  --aoa-inner-muted-tint: 0.05;
  --mp-cell-surface: var(--aoa-inner-surface-strong);
  --mp-cell-hover-surface: var(--aoa-inner-surface-strong);
  --mp-cell-muted-surface: var(--aoa-inner-surface-muted);
  --panel-inner-alpha: 0.08;
  --panel-inner-strong-alpha: 0.12;
  --site-cell-fill-alpha: 0.10;
  --donut-core-panel-alpha: 0.90;
  --site-cell-shadow:
    inset 0 1px 0 rgba(var(--line), 0.10),
    inset 0 -1px 0 rgba(var(--line), 0.030),
    0 8px 18px rgba(15, 23, 42, 0.060),
    0 2px 7px rgba(15, 23, 42, 0.035);
  --shadow-panel:
    inset 0 1px 0 rgba(var(--line), 0.080),
    inset 0 -1px 0 rgba(var(--line), 0.035),
    0 10px 22px rgba(0, 0, 0, 0.055),
    0 2px 8px rgba(0, 0, 0, 0.035);
  --shadow-block:
    inset 0 1px 0 rgba(var(--line), 0.065),
    inset 0 -1px 0 rgba(var(--line), 0.026),
    0 6px 14px rgba(0, 0, 0, 0.045),
    0 1px 4px rgba(0, 0, 0, 0.025);
  --shadow-button:
    inset 0 1px 0 rgba(var(--line), 0.070),
    inset 0 -1px 0 rgba(var(--line), 0.025),
    0 3px 7px rgba(0, 0, 0, 0.035),
    0 1px 2px rgba(0, 0, 0, 0.020);
}

.agentops-dashboard.agentops-theme--transparent {
  /* 透明主题：外框跟 v-card 一致用 transparent-opacity，内框继续 on-surface 透白做层次 */
  --aoa-outer-surface-opacity: var(--transparent-opacity, 0.42);
  --aoa-outer-surface: rgba(var(--v-theme-surface), var(--transparent-opacity, 0.42));
  --aoa-inner-surface-alpha-hi: var(--transparent-opacity-heavy, 0.58);
  --aoa-inner-surface-alpha-lo: var(--transparent-opacity, 0.42);
  --aoa-inner-surface-tint: 0.13;
  --aoa-inner-strong-alpha-hi: var(--transparent-opacity-heavy, 0.66);
  --aoa-inner-strong-alpha-lo: var(--transparent-opacity, 0.48);
  --aoa-inner-strong-tint: 0.17;
  --aoa-inner-muted-alpha-hi: var(--transparent-opacity, 0.48);
  --aoa-inner-muted-alpha-lo: var(--transparent-opacity-light, 0.34);
  --aoa-inner-muted-tint: 0.12;
  --aoa-inner-border: 1px solid rgba(var(--v-border-color), 0.22);
  --aoa-inner-blur: var(--transparent-blur, 12px);
  --mp-panel-surface: var(--aoa-outer-surface);
  --mp-cell-surface: var(--aoa-inner-surface-strong);
  --mp-cell-hover-surface: var(--aoa-inner-surface-strong);
  --mp-cell-muted-surface: var(--aoa-inner-surface-muted);
  --mp-panel-border: var(--app-surface-border, 1px solid rgba(var(--v-border-color), var(--v-border-opacity, 0.12)));
  --mp-panel-shadow: var(--app-surface-shadow, none);
  --mp-cell-shadow: var(--aoa-inner-shadow);
  --mp-blur: blur(var(--transparent-blur, 0px));
  --shell-panel-hi: 0.00;
  --shell-panel-lo: 0.00;
  --shell-stage-alpha: 0.00;
  --frame-panel-hi: 0.00;
  --frame-panel-lo: 0.00;
  --frame-stage-alpha: 0.00;
  --toolbar-panel-hi: 0.00;
  --toolbar-panel-lo: 0.00;
  --panel-glass-hi: 0.00;
  --panel-glass-lo: 0.00;
  --panel-fill-alpha: 0.00;
  --panel-inner-alpha: 0.12;
  --panel-inner-strong-alpha: 0.18;
  --status-panel-alpha: 0.00;
  --shell-cyan-alpha: 0.00;
  --shell-blue-alpha: 0.00;
  --frame-cyan-alpha: 0.00;
  --frame-violet-alpha: 0.00;
  --top-button-alpha: 0.04;
  --top-button-primary-alpha: 0.06;
  --status-red-glow-alpha: 0.04;
  --status-green-glow-alpha: 0.04;
  --status-mix-alpha: 0.00;
  --alert-line-alpha: 0.04;
  --metric-accent-alpha: 0.04;
  --site-cyan-alpha: 0.00;
  --site-blue-alpha: 0.00;
  --soft-line-alpha: 0.03;
  --donut-core-line-alpha: 0.03;
  --donut-core-panel-alpha: var(--transparent-opacity-heavy, 0.55);
  --site-cell-line-alpha: 0.04;
  --site-cell-line-low-alpha: 0.02;
  --site-cell-border-alpha: var(--v-border-opacity, 0.12);
  --site-cell-fill-alpha: 0.14;
  --site-cell-shadow:
    inset 0 1px 0 rgba(var(--line), 0.050),
    inset 0 -1px 0 rgba(0, 0, 0, 0.014),
    0 4px 10px rgba(0, 0, 0, 0.024),
    0 1px 3px rgba(0, 0, 0, 0.014);
  --command-cyan-alpha: 0.010;
  --download-blue-alpha: 0.010;
  --runtime-violet-alpha: 0.010;
  --shadow-panel:
    inset 0 1px 0 rgba(var(--line), 0.060),
    inset 0 -1px 0 rgba(0, 0, 0, 0.016),
    0 3px 8px rgba(0, 0, 0, 0.020),
    0 1px 2px rgba(0, 0, 0, 0.012);
  --shadow-block:
    inset 0 1px 0 rgba(var(--line), 0.050),
    inset 0 -1px 0 rgba(0, 0, 0, 0.014),
    0 2px 5px rgba(0, 0, 0, 0.018),
    0 1px 2px rgba(0, 0, 0, 0.010);
  --shadow-button:
    inset 0 1px 0 rgba(var(--line), 0.052),
    inset 0 -1px 0 rgba(0, 0, 0, 0.012),
    0 1px 3px rgba(0, 0, 0, 0.016),
    0 1px 1px rgba(0, 0, 0, 0.008);
}

.agentops-dashboard,
.agentops-dashboard * {
  box-sizing: border-box;
}

.agentops-dashboard::-webkit-scrollbar,
.agentops-dashboard :deep(*)::-webkit-scrollbar {
  width: 1px !important;
  height: 1px !important;
  background: transparent !important;
}
.agentops-dashboard::-webkit-scrollbar-track,
.agentops-dashboard :deep(*)::-webkit-scrollbar-track,
.agentops-dashboard::-webkit-scrollbar-track-piece,
.agentops-dashboard :deep(*)::-webkit-scrollbar-track-piece {
  background: transparent !important;
}
.agentops-dashboard::-webkit-scrollbar-thumb,
.agentops-dashboard :deep(*)::-webkit-scrollbar-thumb {
  border-radius: 999px !important;
  border: 0 !important;
  background: rgba(var(--line), 0.13) !important;
}
.agentops-dashboard::-webkit-scrollbar-button,
.agentops-dashboard :deep(*)::-webkit-scrollbar-button,
.agentops-dashboard::-webkit-scrollbar-corner,
.agentops-dashboard :deep(*)::-webkit-scrollbar-corner {
  display: none !important;
  width: 0 !important;
  height: 0 !important;
  appearance: none !important;
  background: transparent !important;
  opacity: 0 !important;
}

.dashboard-shell {
  border-radius: var(--aoa-dashboard-radius);
  padding: 26px clamp(18px, 3vw, 40px) 34px;
  border: 0;
  background: transparent;
  background-color: transparent !important;
  box-shadow: none;
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
}

.dashboard-shell--sidebar {
  min-height: calc(100dvh - 72px);
  max-height: none;
  overflow: visible;
  padding: 28px 22px 30px;
  border: 0;
  border-radius: 0 !important;
  background: transparent;
  background-color: transparent !important;
  box-shadow: none;
  backdrop-filter: none;
}

.dashboard-shell--sidebar .agentops-frame {
  width: 100%;
  min-height: calc(100dvh - 96px);
  margin: 0;
  overflow: visible;
  border: 0;
  border-radius: 0 !important;
  background: transparent;
  background-color: transparent !important;
  box-shadow: none;
  backdrop-filter: none;
}

.dashboard-shell--sidebar .dashboard-canvas {
  box-sizing: border-box;
  height: calc(100dvh - 180px);
  min-height: 730px;
  padding: 16px 0 0;
  gap: 16px;
  grid-template-columns: minmax(320px, 1.15fr) minmax(320px, 1.15fr) minmax(280px, 0.9fr);
}

.dashboard-shell--sidebar .metric-card {
  grid-template-columns: 32px minmax(0, 1fr);
  gap: 8px;
  padding: 14px 12px;
}

.dashboard-shell--sidebar .metric-symbol {
  width: 32px;
  height: 32px;
  border-radius: 12px;
}

.dashboard-shell--sidebar .metric-copy strong {
  font-size: 20px;
  letter-spacing: 0;
}

.dashboard-shell--sidebar .command-panel {
  padding: 20px 22px 22px;
}

.dashboard-shell--sidebar .command-body {
  gap: 12px;
  padding: 0 4px 12px 0;
}

.dashboard-shell--sidebar .command-group {
  padding: 14px 12px;
}

.dashboard-shell--sidebar .cmd-grid {
  gap: 8px;
}

.agentops-frame {
  width: 100%;
  max-width: 1680px;
  min-height: 790px;
  margin: 0 auto;
  overflow: visible;
  border-radius: var(--aoa-dashboard-radius);
  border: 0;
  background: transparent;
  background-color: transparent !important;
  box-shadow: none;
  backdrop-filter: none !important;
  -webkit-backdrop-filter: none !important;
}

.agentops-toolbar {
  height: 56px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 22px;
  margin-bottom: 18px;
  border-bottom: 0;
  background: transparent;
  background-color: transparent !important;
  box-shadow: none;
  backdrop-filter: none;
}

.brand {
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 16px;
  font-weight: 860;
  letter-spacing: 0;
}
.brand-mark {
  width: 22px;
  height: 22px;
  display: grid;
  place-items: center;
  color: rgb(var(--cyan));
  filter: drop-shadow(0 0 10px rgba(var(--cyan), 0.14));
}
.brand-title {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.brand small {
  margin-left: 8px;
  color: rgba(var(--muted), 0.70);
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
}
.toolbar-space {
  flex: 1;
}

.top-button {
  min-width: 56px;
  height: 30px;
  border-radius: 999px;
  border: 1px solid rgba(var(--line), 0.11);
  color: rgba(var(--ink), 0.84);
  background:
    linear-gradient(180deg, rgba(var(--line), 0.070), rgba(var(--line), 0.025)),
    rgba(var(--panel), var(--top-button-alpha));
  box-shadow: var(--shadow-button);
  font-size: 12px;
  font-weight: 760;
}
.top-button--primary {
  border-color: rgba(var(--cyan), 0.34);
  color: rgb(var(--cyan));
  background:
    linear-gradient(180deg, rgba(var(--cyan), 0.12), rgba(var(--cyan), 0.035)),
    rgba(var(--panel), var(--top-button-primary-alpha));
}
.top-button--icon {
  width: 30px;
  min-width: 30px;
  color: rgba(var(--muted), 0.88);
}
.top-button :deep(.v-btn__overlay),
.cmd-btn :deep(.v-btn__overlay) {
  display: none;
}

.dashboard-canvas {
  height: min(746px, calc(100dvh - 150px));
  min-height: 620px;
  padding: 18px;
  display: grid;
  grid-template-columns: minmax(320px, 1.08fr) minmax(320px, 1.08fr) minmax(300px, 0.92fr);
  grid-template-rows: minmax(136px, 0.72fr) minmax(250px, 1.25fr) minmax(180px, 0.9fr);
  gap: 14px;
}

.panel {
  position: relative;
  min-width: 0;
  overflow: hidden;
  border-radius: var(--mp-panel-radius);
  border: var(--mp-panel-border);
  background: var(--mp-panel-surface);
  box-shadow: var(--mp-panel-shadow);
  backdrop-filter: var(--mp-blur);
  -webkit-backdrop-filter: var(--mp-blur);
}
.panel::before {
  content: "";
  position: absolute;
  inset: 0 0 auto 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(var(--line), 0.28), transparent);
  opacity: 0.50;
  pointer-events: none;
}

.panel-head {
  height: 38px;
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 0 14px;
}
.panel-head h2 {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 15px;
  line-height: 1;
  font-weight: 860;
}
.panel-note {
  margin-left: auto;
  color: rgba(var(--muted), 0.66);
  font-size: 12px;
  font-weight: 720;
  white-space: nowrap;
}
.panel-icon {
  width: 20px;
  height: 20px;
  display: grid;
  place-items: center;
  flex: 0 0 auto;
}
.panel-icon--cyan {
  color: rgb(var(--cyan));
}
.panel-icon--blue {
  color: rgb(var(--blue));
}

.alert-panel {
  grid-column: 1;
  grid-row: 1;
  padding: 16px;
  border-color: rgba(var(--red), 0.22);
  background:
    radial-gradient(circle at 7% 0%, rgba(var(--red), var(--status-red-glow-alpha)), transparent 44%),
    linear-gradient(145deg, rgba(var(--red), 0.070), rgba(var(--panel), var(--status-mix-alpha))),
    rgba(var(--panel), var(--status-panel-alpha));
}
.alert-panel--ok {
  border-color: rgba(var(--green), 0.20);
  background:
    radial-gradient(circle at 7% 0%, rgba(var(--green), var(--status-green-glow-alpha)), transparent 44%),
    linear-gradient(145deg, rgba(var(--green), 0.055), rgba(var(--panel), var(--status-mix-alpha))),
    rgba(var(--panel), var(--status-panel-alpha));
}
.alert-panel--idle {
  border-color: rgba(var(--blue), 0.16);
  background:
    radial-gradient(circle at 7% 0%, rgba(var(--blue), 0.075), transparent 44%),
    linear-gradient(145deg, rgba(var(--line), 0.030), rgba(var(--panel), var(--status-mix-alpha))),
    rgba(var(--panel), var(--status-panel-alpha));
}
.alert-top {
  display: flex;
  align-items: center;
  gap: 14px;
}
.alert-icon {
  width: 42px;
  height: 42px;
  display: grid;
  place-items: center;
  flex: 0 0 auto;
  border-radius: 14px;
  color: rgba(var(--red), 0.96);
  background: rgba(var(--red), 0.22);
  box-shadow:
    inset 0 1px 0 rgba(var(--line), 0.18),
    inset 0 -1px 0 rgba(0, 0, 0, 0.09),
    0 5px 10px rgba(0, 0, 0, 0.060),
    0 5px 12px rgba(var(--red), 0.045);
}
.alert-panel--ok .alert-icon {
  color: rgb(var(--green));
  background: rgba(var(--green), 0.20);
}
.alert-panel--idle .alert-icon {
  color: rgba(var(--blue), 0.92);
  background: rgba(var(--blue), 0.16);
  box-shadow:
    inset 0 1px 0 rgba(var(--line), 0.14),
    0 4px 10px rgba(0, 0, 0, 0.045);
}
.alert-copy {
  min-width: 0;
}
.alert-copy h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 900;
  line-height: 1.05;
}
.alert-copy p {
  margin: 9px 0 0;
  color: rgba(var(--ink), 0.74);
  font-size: 13px;
  line-height: 1.45;
  font-weight: 650;
}
.alert-line {
  height: 44px;
  margin-top: 14px;
  display: grid;
  grid-template-columns: 74px minmax(0, 1fr) auto;
  gap: 8px;
  align-items: center;
  border-radius: 14px;
  padding: 0 10px;
  border: 1px solid rgba(var(--red), 0.22);
  background: rgba(var(--panel), var(--alert-line-alpha));
  box-shadow:
    inset 0 1px 0 rgba(var(--line), 0.075),
    inset 0 -1px 0 rgba(0, 0, 0, 0.09),
    0 3px 7px rgba(0, 0, 0, 0.050);
  font-size: 12px;
}
.alert-panel--ok .alert-line {
  border-color: rgba(var(--green), 0.20);
}
.alert-panel--idle .alert-line {
  border-color: rgba(var(--blue), 0.14);
}
.alert-line b {
  color: rgba(var(--red), 0.98);
  font-weight: 850;
  white-space: nowrap;
}
.alert-panel--ok .alert-line b {
  color: rgba(var(--green), 0.98);
}
.alert-panel--idle .alert-line b {
  color: rgba(var(--blue), 0.96);
}
.alert-line strong {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: rgba(var(--ink), 0.88);
}
.badge {
  height: 22px;
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 0 8px;
  color: rgba(var(--red), 0.96);
  background: rgba(var(--red), 0.20);
  box-shadow:
    inset 0 1px 0 rgba(var(--line), 0.060),
    0 2px 5px rgba(0, 0, 0, 0.040);
  font-size: 11px;
  font-weight: 850;
  white-space: nowrap;
}
.badge--ok {
  color: rgb(var(--green));
  background: rgba(var(--green), 0.16);
}
.badge--idle {
  color: rgba(var(--blue), 0.96);
  background: rgba(var(--blue), 0.14);
}

.metrics-panel {
  grid-column: 2;
  grid-row: 1;
  min-width: 0;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}
.metric-card {
  min-width: 0;
  border-radius: var(--mp-panel-radius);
  padding: 16px 14px;
  display: grid;
  grid-template-columns: 44px minmax(0, 1fr);
  gap: 12px;
  align-items: center;
  border: var(--mp-panel-border);
  background: var(--mp-panel-surface);
  box-shadow: var(--mp-panel-shadow);
  backdrop-filter: var(--mp-blur);
  -webkit-backdrop-filter: var(--mp-blur);
}
.metric-card--green { --accent: var(--green); }
.metric-card--blue { --accent: var(--blue); }
.metric-card--red { --accent: var(--red); }
.metric-card--amber { --accent: var(--amber); }
.metric-card--muted { --accent: var(--faint); }
.metric-symbol {
  width: 40px;
  height: 40px;
  display: grid;
  place-items: center;
  border-radius: 15px;
  color: rgba(var(--accent), 1);
  background: rgba(var(--line), 0.045);
  box-shadow:
    inset 0 1px 0 rgba(var(--line), 0.10),
    inset 0 -1px 0 rgba(0, 0, 0, 0.08),
    0 3px 7px rgba(0, 0, 0, 0.050);
}
.metric-copy {
  min-width: 0;
}
.metric-copy p {
  margin: 0;
  color: rgba(var(--muted), 0.72);
  font-size: 12px;
  line-height: 1;
  font-weight: 720;
}
.metric-copy strong {
  display: block;
  margin-top: 7px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 24px;
  line-height: 1;
  font-weight: 920;
  letter-spacing: 0;
}

.site-panel {
  grid-column: 1 / 3;
  grid-row: 2;
  background:
    radial-gradient(circle at 13% 10%, rgba(var(--cyan), var(--site-cyan-alpha)), transparent 38%),
    radial-gradient(circle at 76% 22%, rgba(var(--blue), var(--site-blue-alpha)), transparent 35%),
    linear-gradient(180deg, rgba(var(--panel), var(--panel-glass-hi)), rgba(var(--panel), var(--panel-glass-lo))),
    rgba(var(--line), var(--panel-fill-alpha));
}
.site-body {
  height: calc(100% - 38px);
  display: grid;
  grid-template-columns: clamp(160px, 22%, 230px) minmax(0, 1fr);
  gap: 18px;
  padding: 14px 18px 18px;
}
.donut-zone {
  display: grid;
  place-items: center;
  border-radius: 17px;
  background:
    radial-gradient(circle at 50% 44%, rgba(var(--line), var(--soft-line-alpha)), transparent 54%),
    rgba(var(--line), 0.022);
  border: 1px solid rgba(var(--line), 0.050);
  box-shadow: var(--shadow-block);
}
.donut {
  position: relative;
  width: 176px;
  height: 176px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  box-shadow:
    inset 0 1px 16px rgba(var(--line), 0.18),
    inset 0 -14px 24px rgba(0, 0, 0, 0.12),
    0 7px 18px rgba(0, 0, 0, 0.055);
}
.donut--empty {
  opacity: 0.72;
}
.donut::after {
  content: "";
  position: absolute;
  inset: 35px;
  border-radius: 50%;
  background:
    radial-gradient(circle at 50% 18%, rgba(var(--line), var(--donut-core-line-alpha)), transparent 48%),
    rgba(var(--panel), var(--donut-core-panel-alpha));
  box-shadow:
    inset 0 1px 0 rgba(var(--line), 0.08),
    0 0 0 1px rgba(var(--line), 0.045);
}
.donut-core {
  position: relative;
  z-index: 1;
  text-align: center;
}
.donut-core strong {
  display: block;
  font-size: 31px;
  line-height: 1;
  font-weight: 930;
}
.donut-core span {
  display: block;
  margin-top: 8px;
  color: rgba(var(--muted), 0.70);
  font-size: 12px;
  font-weight: 680;
}
.site-data {
  min-width: 0;
  min-height: 0;
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
  gap: 9px;
  overflow: hidden;
}
.site-stats {
  min-height: 0;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
  overflow: hidden;
}
.site-stat {
  min-width: 0;
  min-height: 32px;
  height: 32px;
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  align-items: center;
  gap: 6px;
  border-radius: 15px;
  border: 1px solid rgba(var(--line), var(--site-cell-border-alpha));
  padding: 0 10px;
  background:
    linear-gradient(180deg, rgba(var(--line), var(--site-cell-line-alpha)), rgba(var(--line), var(--site-cell-line-low-alpha))),
    rgba(var(--panel), var(--site-cell-fill-alpha));
  box-shadow: var(--site-cell-shadow);
  overflow: hidden;
  contain: layout paint;
}
.site-stat span {
  color: rgba(var(--muted), 0.70);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 11px;
  line-height: 1;
  font-weight: 720;
}
.site-stat strong {
  display: block;
  margin: 0;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  text-align: right;
  font-size: 14px;
  line-height: 1;
  font-weight: 890;
}
.site-list {
  min-height: 0;
  display: grid;
  gap: 8px;
  align-content: start;
  overflow: auto;
  padding-right: 2px;
  color: rgba(var(--ink), 0.88);
  font-size: 13px;
  font-weight: 700;
  scrollbar-width: thin;
}
.site-card {
  min-width: 0;
  display: grid;
  grid-template-rows: 18px 30px;
  gap: 7px;
  border-radius: 12px;
  border: 1px solid rgba(var(--line), var(--site-cell-border-alpha));
  padding: 8px;
  background:
    linear-gradient(180deg, rgba(var(--line), var(--site-cell-line-alpha)), rgba(var(--line), var(--site-cell-line-low-alpha))),
    rgba(var(--panel), var(--site-cell-fill-alpha));
  box-shadow: var(--site-cell-shadow);
  overflow: hidden;
  contain: layout paint;
}
.site-card-head,
.site-card-metrics {
  min-width: 0;
  display: grid;
  align-items: center;
  overflow: hidden;
}
.site-card-head {
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 8px;
  line-height: 1;
}
.site-card-metrics {
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 7px;
}
.site-table-name {
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  overflow: hidden;
}
.site-percent {
  min-width: 0;
  display: block;
  text-align: right;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1;
}
.site-percent {
  color: rgba(var(--ink), 0.84);
  font-size: 12px;
  font-weight: 820;
}
.site-list--empty {
  grid-auto-rows: auto;
}
.site-empty-state {
  min-height: 136px;
  display: grid;
  grid-template-columns: minmax(190px, 0.72fr) minmax(0, 1fr);
  align-items: stretch;
  gap: 10px;
  padding: 14px 18px 18px;
  overflow: hidden;
}
.site-empty-main,
.site-empty-stats {
  min-width: 0;
  border-radius: var(--mp-cell-radius);
  border: 1px solid rgba(var(--line), var(--site-cell-border-alpha));
  background: var(--mp-cell-surface);
  box-shadow: var(--site-cell-shadow);
}
.site-empty-main {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  color: rgba(var(--muted), 0.78);
}
.site-empty-icon {
  width: 36px;
  height: 36px;
  flex: 0 0 auto;
  display: grid;
  place-items: center;
  border-radius: var(--mp-cell-radius);
  color: rgba(var(--ink), 0.72);
  background: var(--mp-cell-muted-surface);
}
.site-empty-main > div {
  min-width: 0;
  display: grid;
  gap: 5px;
}
.site-empty-main strong {
  color: rgba(var(--ink), 0.90);
  font-size: 13px;
  line-height: 1.15;
}
.site-empty-main span {
  font-size: 12px;
  line-height: 1.2;
}
.site-empty-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  align-content: center;
  gap: 8px;
  padding: 10px;
}
.site-name {
  flex: 1 1 auto;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.site-table-percent {
  font-size: 13px;
  line-height: 1;
  font-weight: 820;
}
.site-row-cell {
  min-width: 0;
  min-height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 11px;
  border: 1px solid rgba(var(--line), var(--site-cell-border-alpha));
  padding: 0 9px;
  background:
    linear-gradient(180deg, rgba(var(--line), var(--site-cell-line-alpha)), rgba(var(--line), var(--site-cell-line-low-alpha))),
    rgba(var(--panel), var(--site-cell-fill-alpha));
  box-shadow: var(--site-cell-shadow);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1;
}
.site-empty-row {
  grid-column: 1 / -1;
  min-height: 72px;
  gap: 12px;
  justify-content: center;
  color: rgba(var(--muted), 0.78);
  background:
    linear-gradient(180deg, rgba(var(--line), 0.045), rgba(var(--line), 0.014)),
    rgba(var(--panel), var(--panel-inner-alpha));
  white-space: normal;
}
.site-empty-row > div {
  min-width: 0;
  display: grid;
  gap: 5px;
}
.site-empty-row strong {
  color: rgba(var(--ink), 0.90);
  font-size: 13px;
  line-height: 1;
}
.site-empty-row span {
  font-size: 12px;
  line-height: 1;
}
.dot {
  width: 8px;
  height: 8px;
  flex: 0 0 auto;
  border-radius: 999px;
  background: rgb(var(--green));
  box-shadow: 0 0 8px rgba(var(--green), 0.32);
}
.dot.red {
  background: rgb(var(--red));
  box-shadow: 0 0 8px rgba(var(--red), 0.26);
}
.dot.gray {
  background: rgba(var(--faint), 0.70);
  box-shadow: none;
}
.site-empty {
  height: calc(100% - 38px);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: rgba(var(--muted), 0.80);
}
.site-empty div {
  display: grid;
  gap: 6px;
}
.site-empty strong {
  color: rgba(var(--ink), 0.92);
}
.site-empty span {
  font-size: 12px;
}

.command-panel {
  grid-column: 3;
  grid-row: 1 / 4;
  container-type: inline-size;
  display: grid;
  grid-template-rows: auto minmax(0, 1fr) auto;
  gap: 12px;
  padding: 24px;
  background:
    radial-gradient(circle at 14% 0%, rgba(var(--cyan), var(--command-cyan-alpha)), transparent 34%),
    linear-gradient(180deg, rgba(var(--panel), var(--panel-glass-hi)), rgba(var(--panel), var(--panel-glass-lo))),
    rgba(var(--line), var(--panel-fill-alpha));
  box-shadow: var(--shadow-panel);
}
.command-head {
  height: auto;
  min-height: 24px;
  padding: 0;
  margin-bottom: 0;
}
.command-body {
  min-height: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
  overflow: auto;
  padding: 0 4px 10px 0;
}
.command-group {
  min-width: 0;
  flex: 0 0 auto;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  border-radius: 16px;
  padding: 14px 14px;
  border: 1px solid rgba(var(--line), 0.036);
  background:
    linear-gradient(180deg, rgba(var(--line), 0.026), rgba(var(--line), 0.008)),
    rgba(var(--panel), var(--panel-inner-alpha));
  box-shadow:
    inset 0 1px 0 rgba(var(--line), 0.052),
    inset 0 -1px 0 rgba(0, 0, 0, 0.08),
    0 4px 9px rgba(0, 0, 0, 0.050);
}
.group-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 12px;
  color: rgba(var(--muted), 0.70);
  font-size: 12px;
  font-weight: 760;
}
.command-quick-card {
  min-height: 0;
  display: grid;
  grid-template-columns: minmax(112px, 0.72fr) minmax(220px, 1.28fr);
  align-items: center;
  gap: 12px;
  padding: 12px 12px 12px 14px;
}
.command-quick-copy {
  min-width: 0;
  display: grid;
  gap: 4px;
}
.command-quick-copy span {
  color: rgba(var(--muted), 0.70);
  font-size: 12px;
  line-height: 1;
  font-weight: 760;
}
.command-quick-copy strong {
  color: rgba(var(--ink), 0.94);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 14px;
  line-height: 1.15;
  font-weight: 880;
}
.command-quick-buttons {
  min-width: 0;
  width: 100%;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  align-items: center;
  gap: 8px;
}
.command-quick-btn {
  width: 100%;
  height: 38px;
  min-width: 0;
  border-radius: 13px;
  border: 1px solid rgba(var(--line), 0.095);
  color: rgba(var(--green), 0.98);
  background:
    linear-gradient(180deg, rgba(var(--green), 0.115), rgba(var(--green), 0.030)),
    rgba(var(--panel), var(--panel-inner-alpha));
  box-shadow: var(--shadow-button);
}
.command-quick-btn :deep(.v-btn__content) {
  width: 100%;
  min-width: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  overflow: hidden;
}
.command-quick-label {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 12px;
  line-height: 1;
  font-weight: 820;
}
.command-quick-btn:hover {
  border-color: rgba(var(--green), 0.25);
  background:
    linear-gradient(180deg, rgba(var(--green), 0.155), rgba(var(--green), 0.045)),
    rgba(var(--panel), var(--panel-inner-strong-alpha));
}
.command-quick-btn :deep(.v-btn__overlay) {
  display: none;
}

@container (max-width: 360px) {
  .command-quick-card {
    align-items: stretch;
    grid-template-columns: 1fr;
    gap: 10px;
  }

  .command-quick-copy strong {
    white-space: normal;
    line-height: 1.18;
  }

  .command-quick-buttons {
    width: 100%;
    justify-content: flex-start;
  }

  .command-quick-btn {
    height: 34px;
  }
}

@container (max-width: 300px) {
  .command-quick-buttons {
    grid-template-columns: 1fr;
    gap: 6px;
  }

  .command-quick-btn {
    width: auto;
    min-width: 0;
  }
}
.cmd-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}
.cmd-btn {
  min-width: 0;
  height: 36px;
  border-radius: 12px;
  border: 1px solid rgba(var(--line), 0.095);
  color: rgba(var(--ink), 0.90);
  background:
    linear-gradient(180deg, rgba(var(--line), 0.080), rgba(var(--line), 0.024)),
    rgba(var(--panel), var(--panel-inner-alpha));
  box-shadow: var(--shadow-button);
  font-size: 12px;
  font-weight: 840;
  white-space: nowrap;
}
.cmd-btn.v-btn {
  padding-inline: 10px;
}
.cmd-btn:hover {
  border-color: rgba(var(--line), 0.16);
  background:
    linear-gradient(180deg, rgba(var(--line), 0.105), rgba(var(--line), 0.032)),
    rgba(var(--panel), var(--panel-inner-strong-alpha));
}
.cmd-btn :deep(.v-btn__content) {
  min-width: 0;
  width: 100%;
  max-width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
  overflow: visible;
  line-height: 1.18;
}
.cmd-btn :deep(.v-icon) {
  flex: 0 0 auto;
}
.action-btn-label {
  flex: 0 0 auto;
  min-width: max-content;
  overflow: visible !important;
  text-overflow: clip !important;
  line-height: 1.18;
  white-space: nowrap;
}
.cmd-btn .action-btn-label {
  overflow: visible !important;
  text-overflow: clip !important;
}
.action-message {
  margin-top: 14px;
  flex: 0 0 auto;
}

.download-panel {
  grid-column: 1;
  grid-row: 3;
  background:
    radial-gradient(circle at 12% 10%, rgba(var(--blue), var(--download-blue-alpha)), transparent 38%),
    linear-gradient(180deg, rgba(var(--panel), var(--panel-glass-hi)), rgba(var(--panel), var(--panel-glass-lo))),
    rgba(var(--line), var(--panel-fill-alpha));
}
.download-body {
  height: calc(100% - 38px);
  display: grid;
  gap: 10px;
  align-content: start;
  overflow: auto;
  padding: 2px 14px 14px;
}
.downloader-card {
  min-width: 0;
  min-height: 72px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
  column-gap: 12px;
  border-radius: 14px;
  padding: 0 12px;
  border: 1px solid rgba(var(--line), 0.060);
  background:
    linear-gradient(180deg, rgba(var(--line), 0.055), rgba(var(--line), 0.018)),
    rgba(var(--panel), var(--panel-inner-alpha));
  box-shadow: var(--shadow-block);
}
.downloader-card div {
  min-width: 0;
}
.downloader-card strong {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 14px;
  line-height: 1;
  font-weight: 850;
}
.downloader-card span:not(.ok-chip) {
  display: block;
  margin-top: 10px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: rgba(var(--muted), 0.70);
  font-size: 12px;
  line-height: 1;
  font-weight: 680;
}
.ok-chip {
  min-width: 54px;
  height: 24px;
  display: inline-grid;
  place-items: center;
  border-radius: 999px;
  padding: 0 10px;
  color: rgb(var(--green));
  background: rgba(var(--green), 0.16);
  box-shadow:
    inset 0 1px 0 rgba(var(--line), 0.060),
    0 2px 5px rgba(0, 0, 0, 0.040);
  font-size: 11px;
  font-weight: 850;
  line-height: 1;
}
.ok-chip--idle {
  color: rgba(var(--muted), 0.82);
  background: rgba(var(--faint), 0.13);
}
.downloader-card--empty {
  border-color: rgba(var(--line), 0.050);
}
.downloader-card--ghost {
  opacity: 0.74;
}
.download-empty {
  height: calc(100% - 38px);
  display: grid;
  place-items: center;
  align-content: center;
  gap: 8px;
  color: rgba(var(--muted), 0.72);
  font-size: 12px;
}
.download-empty strong {
  color: rgba(var(--ink), 0.90);
  font-size: 14px;
}

.runtime-panel {
  grid-column: 2;
  grid-row: 3;
  background:
    radial-gradient(circle at 85% 8%, rgba(var(--violet), var(--runtime-violet-alpha)), transparent 38%),
    linear-gradient(180deg, rgba(var(--panel), var(--panel-glass-hi)), rgba(var(--panel), var(--panel-glass-lo))),
    rgba(var(--line), var(--panel-fill-alpha));
}
.runtime-loader {
  margin: 4px 14px 10px;
}
.runtime-track {
  height: calc(100% - 38px);
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  grid-auto-rows: 68px;
  align-content: start;
  gap: 8px;
  overflow: auto;
  padding: 4px 14px 8px;
}
.module {
  min-width: 0;
  height: 68px;
  border-radius: 13px;
  padding: 9px 10px 8px;
  border: 1px solid rgba(var(--line), 0.052);
  background:
    linear-gradient(180deg, rgba(var(--line), 0.052), rgba(var(--line), 0.016)),
    rgba(var(--panel), var(--panel-inner-alpha));
  box-shadow: var(--shadow-block);
}
.module--bad {
  border-color: rgba(var(--red), 0.18);
}
.module-top {
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 8px;
}
.module-title {
  min-width: 0;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 13px;
  font-weight: 850;
}
.module-note {
  margin-top: 6px;
  color: rgba(var(--muted), 0.64);
  font-size: 11px;
  line-height: 1.1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.state {
  height: 20px;
  min-width: 34px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  padding: 1px 8px 0;
  color: rgb(var(--green));
  background: rgba(var(--green), 0.15);
  box-shadow:
    inset 0 1px 0 rgba(var(--line), 0.055),
    0 2px 4px rgba(0, 0, 0, 0.035);
  font-size: 10px;
  font-weight: 900;
  line-height: 1;
  white-space: nowrap;
}
.state.off {
  color: rgba(var(--muted), 0.82);
  background: rgba(var(--faint), 0.13);
}
.state.bad {
  color: rgba(var(--red), 0.96);
  background: rgba(var(--red), 0.17);
}

.agentops-dashboard.agentops-theme--transparent.dashboard-shell {
  border: 0;
  background: transparent;
  background-color: transparent !important;
  box-shadow: none;
  backdrop-filter: none;
}

.agentops-dashboard.agentops-theme--transparent .agentops-frame {
  border: 0;
  background: transparent;
  background-color: transparent !important;
  box-shadow: none;
  backdrop-filter: none;
}

.agentops-dashboard.agentops-theme--transparent.dashboard-shell--sidebar,
.agentops-dashboard.agentops-theme--transparent.dashboard-shell--sidebar .agentops-frame {
  border: 0;
  background: transparent;
  background-color: transparent !important;
  box-shadow: none;
  backdrop-filter: none;
}

.agentops-dashboard.agentops-theme--transparent .agentops-toolbar {
  border-bottom: 0;
  background: transparent;
  background-color: transparent !important;
  box-shadow: none;
}

.agentops-dashboard.agentops-theme--transparent .panel {
  border-color: rgba(var(--line), 0.060);
  background:
    linear-gradient(180deg, rgba(var(--line), 0.012), rgba(var(--line), 0.003)),
    rgba(var(--stage), 0.002);
  box-shadow: var(--shadow-panel);
}

.agentops-dashboard.agentops-theme--transparent .panel::before {
  opacity: 0.34;
}

.agentops-dashboard.agentops-theme--transparent .alert-panel {
  border-color: rgba(var(--red), 0.18);
  background:
    radial-gradient(circle at 7% 0%, rgba(var(--red), var(--status-red-glow-alpha)), transparent 44%),
    linear-gradient(145deg, rgba(var(--red), 0.030), rgba(var(--line), 0.006)),
    rgba(var(--stage), 0.002);
}

.agentops-dashboard.agentops-theme--transparent .alert-panel--ok {
  border-color: rgba(var(--green), 0.16);
  background:
    radial-gradient(circle at 7% 0%, rgba(var(--green), var(--status-green-glow-alpha)), transparent 44%),
    linear-gradient(145deg, rgba(var(--green), 0.026), rgba(var(--line), 0.006)),
    rgba(var(--stage), 0.002);
}

.agentops-dashboard.agentops-theme--transparent .metric-card,
.agentops-dashboard.agentops-theme--transparent .site-panel,
.agentops-dashboard.agentops-theme--transparent .command-panel,
.agentops-dashboard.agentops-theme--transparent .download-panel,
.agentops-dashboard.agentops-theme--transparent .runtime-panel {
  background:
    radial-gradient(circle at 100% 0%, rgba(var(--accent, var(--line)), var(--metric-accent-alpha)), transparent 52%),
    linear-gradient(180deg, rgba(var(--line), 0.012), rgba(var(--line), 0.003)),
    rgba(var(--stage), 0.002);
}

.agentops-dashboard.agentops-theme--transparent .site-panel {
  background:
    radial-gradient(circle at 13% 10%, rgba(var(--cyan), var(--site-cyan-alpha)), transparent 38%),
    radial-gradient(circle at 76% 22%, rgba(var(--blue), var(--site-blue-alpha)), transparent 35%),
    linear-gradient(180deg, rgba(var(--line), 0.012), rgba(var(--line), 0.003)),
    rgba(var(--stage), 0.002);
}

.agentops-dashboard.agentops-theme--transparent .command-panel {
  background:
    radial-gradient(circle at 14% 0%, rgba(var(--cyan), var(--command-cyan-alpha)), transparent 34%),
    linear-gradient(180deg, rgba(var(--line), 0.012), rgba(var(--line), 0.003)),
    rgba(var(--stage), 0.002);
}

.agentops-dashboard.agentops-theme--transparent .download-panel {
  background:
    radial-gradient(circle at 12% 10%, rgba(var(--blue), var(--download-blue-alpha)), transparent 38%),
    linear-gradient(180deg, rgba(var(--line), 0.012), rgba(var(--line), 0.003)),
    rgba(var(--stage), 0.002);
}

.agentops-dashboard.agentops-theme--transparent .runtime-panel {
  background:
    radial-gradient(circle at 85% 8%, rgba(var(--violet), var(--runtime-violet-alpha)), transparent 38%),
    linear-gradient(180deg, rgba(var(--line), 0.012), rgba(var(--line), 0.003)),
    rgba(var(--stage), 0.002);
}

.agentops-dashboard.agentops-theme--transparent .top-button,
.agentops-dashboard.agentops-theme--transparent .command-quick-btn,
.agentops-dashboard.agentops-theme--transparent .alert-line,
.agentops-dashboard.agentops-theme--transparent .site-empty-row,
.agentops-dashboard.agentops-theme--transparent .command-group,
.agentops-dashboard.agentops-theme--transparent .cmd-btn,
.agentops-dashboard.agentops-theme--transparent .downloader-card,
.agentops-dashboard.agentops-theme--transparent .module {
  background:
    linear-gradient(180deg, rgba(var(--line), 0.014), rgba(var(--line), 0.004)),
    rgba(var(--stage), 0.002);
  box-shadow: var(--shadow-block);
}

.agentops-dashboard.agentops-theme--transparent .top-button,
.agentops-dashboard.agentops-theme--transparent .command-quick-btn,
.agentops-dashboard.agentops-theme--transparent .cmd-btn {
  box-shadow: var(--shadow-button);
}

.agentops-dashboard.agentops-theme--transparent .cmd-btn:hover {
  border-color: rgba(var(--line), 0.14);
  background:
    linear-gradient(180deg, rgba(var(--line), 0.022), rgba(var(--line), 0.006)),
    rgba(var(--stage), 0.002);
}

.agentops-dashboard.agentops-theme--transparent .alert-icon {
  background: rgba(var(--red), 0.12);
  box-shadow:
    inset 0 1px 0 rgba(var(--line), 0.070),
    0 2px 5px rgba(0, 0, 0, 0.016);
}

.agentops-dashboard.agentops-theme--transparent .alert-panel--ok .alert-icon {
  background: rgba(var(--green), 0.10);
}

.agentops-dashboard.agentops-theme--transparent .metric-symbol,
.agentops-dashboard.agentops-theme--transparent .donut-zone {
  background: rgba(var(--line), 0.010);
  box-shadow: var(--shadow-block);
}

.agentops-dashboard.agentops-theme--transparent .donut {
  box-shadow:
    inset 0 1px 10px rgba(var(--line), 0.075),
    inset 0 -10px 18px rgba(0, 0, 0, 0.035),
    0 3px 9px rgba(0, 0, 0, 0.018);
}

.agentops-dashboard.agentops-theme--transparent .donut::after {
  background:
    radial-gradient(circle at 50% 18%, rgba(var(--line), var(--donut-core-line-alpha)), transparent 48%),
    rgba(var(--line), var(--donut-core-panel-alpha));
  box-shadow:
    inset 0 1px 0 rgba(var(--line), 0.045),
    0 0 0 1px rgba(var(--line), 0.026);
}

.agentops-dashboard.agentops-theme--transparent .badge,
.agentops-dashboard.agentops-theme--transparent .ok-chip,
.agentops-dashboard.agentops-theme--transparent .state {
  box-shadow:
    inset 0 1px 0 rgba(var(--line), 0.042),
    0 1px 2px rgba(0, 0, 0, 0.010);
}

@supports (-moz-appearance: none) {
  .agentops-dashboard,
  .agentops-dashboard :deep(*) {
    scrollbar-width: thin;
    scrollbar-color: rgba(var(--line), 0.13) transparent;
  }
}

@media (min-width: 1181px) and (max-height: 820px) {
  .dashboard-shell {
    padding: 14px 24px 18px;
  }
  .agentops-frame {
    min-height: 0;
  }
  .agentops-toolbar {
    height: 44px;
    min-height: 44px;
    padding: 0 16px;
    margin-bottom: 10px;
  }
  .dashboard-canvas {
    height: calc(100dvh - 150px);
    min-height: 560px;
    padding: 14px;
    gap: 12px;
    grid-template-rows: minmax(118px, 0.58fr) minmax(214px, 1fr) minmax(150px, 0.68fr);
  }
  .alert-panel {
    padding: 18px 18px 16px;
  }
  .alert-top {
    gap: 14px;
  }
  .alert-copy h1 {
    font-size: 26px;
  }
  .metrics-panel {
    gap: 12px;
  }
  .metric-card {
    padding: 15px 14px;
  }
  .site-body {
    gap: 14px;
    padding: 12px 16px 16px;
  }
  .site-empty-state {
    min-height: 118px;
    padding: 12px 16px 16px;
  }
  .donut-zone {
    min-height: 180px;
  }
  .site-data {
    grid-template-rows: auto minmax(0, 1fr);
    gap: 8px;
  }
  .site-stats {
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 6px;
  }
  .site-stat {
    gap: 4px;
    padding: 0 8px;
    min-height: 30px;
    height: 30px;
  }
  .site-stat:nth-child(3) {
    min-height: 28px;
    height: 28px;
  }
  .site-stat strong {
    font-size: 12px;
  }
  .command-panel {
    padding: 18px;
  }
  .command-head {
    margin-bottom: 14px;
  }
  .command-body {
    gap: 10px;
  }
  .command-group {
    padding: 10px 12px;
  }
  .command-quick-card {
    padding: 9px 10px 9px 12px;
  }
  .command-quick-copy strong {
    font-size: 13px;
  }
  .command-quick-btn {
    width: 34px;
    height: 34px;
    min-width: 34px;
  }
  .group-head {
    margin-bottom: 8px;
  }
  .cmd-grid {
    gap: 8px;
  }
  .cmd-btn {
    height: 34px;
  }
  .download-body {
    gap: 8px;
    padding: 2px 12px 12px;
  }
  .downloader-card {
    min-height: 58px;
  }
  .runtime-track {
    grid-auto-rows: 64px;
    padding: 3px 12px 10px;
  }
  .module {
    height: 64px;
    padding: 8px 9px;
  }
}

@media (max-width: 1180px) {
  .dashboard-shell {
    padding: 0;
  }
  .dashboard-shell--sidebar {
    padding: 22px 18px 26px;
  }
  .agentops-frame {
    min-height: 0;
  }
  .dashboard-canvas {
    height: auto;
    min-height: 0;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    grid-template-rows: auto;
  }
  .dashboard-shell--sidebar .dashboard-canvas {
    height: auto;
    min-height: 0;
    padding: 14px 0 0;
    gap: 16px;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    grid-template-rows: auto;
  }
  .alert-panel,
  .metrics-panel,
  .site-panel,
  .command-panel,
  .download-panel,
  .runtime-panel {
    grid-column: auto;
    grid-row: auto;
  }
  .site-panel,
  .command-panel {
    grid-column: 1 / -1;
  }
  .command-panel {
    min-height: 420px;
  }
  .download-panel,
  .runtime-panel {
    min-height: 180px;
  }
  .dashboard-shell--sidebar .metric-copy strong {
    font-size: 15px;
  }
}

@media (max-width: 760px) {
  .agentops-dashboard {
    padding: 0;
  }
  .dashboard-shell {
    padding: 0;
    border-radius: var(--mp-panel-radius);
  }
  .dashboard-shell--sidebar {
    padding: 16px 10px calc(116px + env(safe-area-inset-bottom));
    border-radius: 0 !important;
  }
  .dashboard-shell--sidebar,
  .dashboard-shell--sidebar .agentops-frame {
    min-height: 0;
  }
  .agentops-toolbar {
    height: auto;
    min-height: 56px;
    flex-wrap: nowrap;
    gap: 8px;
    padding: 10px 16px;
    margin-bottom: 12px;
  }
  .brand {
    flex: 1 1 auto;
    width: auto;
    gap: 8px;
  }
  .brand-title {
    font-size: 14px;
  }
  .brand small {
    display: none;
  }
  .toolbar-space {
    display: none;
  }
  .top-button {
    min-width: 44px;
    height: 36px;
    padding-inline: 10px;
  }
  .top-button--icon {
    width: 36px;
    min-width: 36px;
    padding-inline: 0;
  }
  .dashboard-canvas,
  .metrics-panel,
  .site-body,
  .site-empty-state,
  .site-stats,
  .cmd-grid,
  .runtime-track {
    grid-template-columns: 1fr;
  }
  .dashboard-canvas {
    height: auto;
    min-height: 0;
    padding: 12px;
    gap: 14px;
    grid-template-rows: auto;
    overflow: visible;
  }
  .dashboard-shell--sidebar .dashboard-canvas {
    height: auto;
    min-height: 0;
    padding: 12px 0 0;
    gap: 14px;
    grid-template-columns: 1fr;
    grid-template-rows: auto;
  }
  .dashboard-shell--sidebar .metrics-panel {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 8px;
  }
  .dashboard-shell--sidebar .metric-card {
    min-height: 64px;
    grid-template-columns: 28px minmax(0, 1fr);
    gap: 7px;
    padding: 11px 9px;
    border-radius: 15px;
  }
  .dashboard-shell--sidebar .metric-symbol {
    width: 28px;
    height: 28px;
    border-radius: 10px;
  }
  .dashboard-shell--sidebar .metric-copy p {
    font-size: 11px;
  }
  .dashboard-shell--sidebar .metric-copy strong {
    font-size: 14px;
  }
  .site-panel,
  .command-panel {
    grid-column: auto;
  }
  .alert-panel,
  .site-panel,
  .download-panel,
  .runtime-panel {
    min-height: 0;
    height: auto;
  }
  .alert-panel {
    padding: 16px;
  }
  .command-panel {
    min-height: 0;
    height: auto;
    padding: 18px 16px;
    overflow: visible;
  }
  .command-head {
    margin-bottom: 18px;
  }
  .command-body {
    height: auto;
    min-height: 0;
    display: flex;
    flex-direction: column;
    gap: 14px;
    overflow: visible;
    padding-right: 0;
  }
  .command-group {
    justify-content: flex-start;
    padding: 16px 14px;
  }
  .cmd-grid {
    gap: 10px;
  }
  .cmd-btn {
    min-height: 40px;
  }
  .site-body,
  .download-body,
  .runtime-track {
    height: auto;
  }
  .site-empty-state {
    min-height: 0;
    grid-template-columns: 1fr;
    padding: 12px;
  }
  .site-empty-stats {
    grid-template-columns: 1fr;
  }
  .site-list {
    padding-right: 0;
  }
  .site-table {
    padding: 7px;
  }
  .site-table-head,
  .site-table-row {
    grid-template-columns: minmax(0, 1.2fr) minmax(70px, 0.8fr) minmax(70px, 0.8fr) 46px;
    gap: 6px;
    padding-inline: 7px;
  }
  .site-table-head {
    font-size: 10px;
  }
  .site-table-row {
    min-height: 32px;
  }
  .site-row-cell {
    min-height: 30px;
    white-space: nowrap;
    line-height: 1.25;
  }
  .alert-copy h1 {
    font-size: 21px;
  }
  .alert-line {
    grid-template-columns: minmax(68px, auto) minmax(0, 1fr);
  }
  .badge {
    display: none;
  }
}

@media (max-width: 520px) {
  .dashboard-shell--sidebar {
    padding: 12px 8px calc(96px + env(safe-area-inset-bottom));
  }

  .agentops-toolbar {
    min-height: 0;
    flex-wrap: wrap;
    gap: 6px;
    padding: 8px 10px;
  }

  .brand {
    flex: 1 0 100%;
  }

  .top-button {
    flex: 1 1 0;
    min-width: 0;
  }

  .top-button--icon {
    flex: 0 0 36px;
  }

  .dashboard-canvas {
    padding: 8px;
    gap: 10px;
  }

  .dashboard-shell--sidebar .dashboard-canvas {
    padding: 8px 0 0;
    gap: 10px;
  }

  .dashboard-shell--sidebar .metrics-panel,
  .metrics-panel,
  .cmd-grid,
  .runtime-track {
    grid-template-columns: 1fr;
  }

  .alert-top {
    align-items: flex-start;
    gap: 10px;
  }

  .alert-icon {
    width: 36px;
    height: 36px;
    border-radius: 12px;
  }

  .alert-copy h1 {
    font-size: 19px;
  }

  .alert-copy p {
    font-size: 12px;
  }

  .alert-line {
    height: auto;
    min-height: 44px;
    grid-template-columns: 1fr;
    align-items: flex-start;
    padding: 8px 10px;
  }

  .alert-line b,
  .alert-line strong {
    white-space: normal;
  }

  .site-body {
    gap: 12px;
    padding: 12px;
  }
  .site-empty-state {
    grid-template-columns: 1fr;
    padding: 12px;
  }
  .site-empty-stats {
    grid-template-columns: 1fr;
  }

  .site-list {
    gap: 8px;
  }

  .command-panel {
    padding: 14px 12px;
  }

  .command-quick-card {
    align-items: stretch;
    flex-direction: column;
    gap: 10px;
  }

  .command-quick-buttons {
    width: 100%;
  }

  .command-quick-btn {
    flex: 1 1 0;
    min-width: 0;
  }

  .cmd-btn {
    min-height: 42px;
    height: auto;
  }

  .cmd-btn :deep(.v-btn__content) {
    justify-content: flex-start;
  }

  .action-btn-label {
    flex: 1 1 auto;
    min-width: 0;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    white-space: normal;
  }

  .downloader-card {
    min-height: 64px;
    grid-template-columns: minmax(0, 1fr);
    row-gap: 6px;
    padding: 10px 12px;
  }

  .ok-chip {
    justify-self: start;
  }

  .runtime-track {
    grid-auto-rows: auto;
  }

  .module {
    height: auto;
    min-height: 64px;
  }
}

@media (max-width: 380px) {
  .agentops-toolbar {
    padding: 8px;
  }

  .dashboard-shell--sidebar {
    padding-inline: 6px;
  }

  .dashboard-canvas {
    padding: 6px;
    gap: 8px;
  }

  .command-quick-card {
    padding: 10px;
  }

  .command-quick-buttons {
    gap: 6px;
  }

  .alert-panel,
  .command-panel,
  .site-body,
  .download-body,
  .runtime-track {
    padding-inline: 10px;
  }

  .alert-line {
    grid-template-columns: 1fr;
    gap: 4px;
  }

  .site-stat strong,
  .metric-copy strong {
    font-size: 16px;
  }
}

/* MP native theme alignment: keep layout custom, let material follow MoviePilot tokens. */
.agentops-dashboard .panel,
.agentops-dashboard .metric-card,
.agentops-dashboard .site-panel,
.agentops-dashboard .command-panel,
.agentops-dashboard .download-panel,
.agentops-dashboard .runtime-panel {
  border: var(--mp-panel-border);
  border-radius: var(--mp-panel-radius);
  background: var(--mp-panel-surface);
  box-shadow: var(--mp-panel-shadow);
  backdrop-filter: var(--mp-blur);
  -webkit-backdrop-filter: var(--mp-blur);
}

.agentops-dashboard .top-button,
.agentops-dashboard .alert-line,
.agentops-dashboard .site-stat,
.agentops-dashboard .site-table,
.agentops-dashboard .site-table-row,
.agentops-dashboard .site-empty-row,
.agentops-dashboard .command-quick-card,
.agentops-dashboard .command-group,
.agentops-dashboard .cmd-btn,
.agentops-dashboard .downloader-card,
.agentops-dashboard .module {
  border: var(--mp-panel-border);
  border-radius: var(--mp-cell-radius);
  background: var(--mp-cell-surface);
  box-shadow: var(--mp-cell-shadow);
}

.agentops-dashboard .top-button:hover,
.agentops-dashboard .command-quick-btn:hover,
.agentops-dashboard .cmd-btn:hover {
  background: var(--mp-cell-hover-surface);
  box-shadow: var(--mp-cell-hover-shadow);
}

.agentops-dashboard .alert-icon,
.agentops-dashboard .metric-symbol,
.agentops-dashboard .donut-zone,
.agentops-dashboard .command-quick-btn,
.agentops-dashboard .cmd-icon {
  border-radius: var(--mp-cell-radius);
  background: var(--mp-cell-muted-surface);
  box-shadow: var(--mp-cell-shadow);
}

.agentops-dashboard .donut::after {
  background: var(--mp-panel-surface);
  box-shadow: inset 0 0 0 1px rgba(var(--v-border-color), var(--v-border-opacity, 0.12));
}

.dashboard-shell--sidebar .top-button,
.dashboard-shell--sidebar .top-button:hover,
.dashboard-shell--sidebar .top-button:focus,
.dashboard-shell--sidebar .top-button:focus-visible,
.dashboard-shell--sidebar .top-button:active {
  --v-hover-opacity: 0;
  --v-focus-opacity: 0;
  --v-activated-opacity: 0;
  border-color: transparent !important;
  background: transparent !important;
  box-shadow: none !important;
}

.dashboard-shell--sidebar .top-button :deep(.v-btn__overlay),
.dashboard-shell--sidebar .top-button :deep(.v-btn__underlay) {
  display: none !important;
  opacity: 0 !important;
  background: transparent !important;
}

</style>

<style>
.dashboard-shell--sidebar .top-button [class~="v-btn__overlay"],
.dashboard-shell--sidebar .top-button [class~="v-btn__underlay"] {
  display: none !important;
  opacity: 0 !important;
  background: transparent !important;
}
</style>
