<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useTheme } from 'vuetify'
import { getPluginApi, postPluginApi } from './api'

const props = defineProps({ api: { type: [Object, Function], default: null } })
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

const siteChart = reactive({ date: '', basis: 'today', sites: [], upload_total: 0, download_total: 0 })
const downloaders = ref([])
const dashboardThemeClass = computed(() => {
  const name = String(vuetifyTheme.global.name.value || '').toLowerCase()
  if (name.includes('transparent')) return 'agentops-theme--transparent'
  if (name.includes('light')) return 'agentops-theme--light'
  return ''
})

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

async function runAction(path, label) {
  if (actionRunning.value) return
  actionRunning.value = path
  actionMessage.value = ''
  actionOk.value = true
  try {
    const res = await postPluginApi(props.api, path)
    const ok = !res || res.code === 0 || res.code === undefined
    actionOk.value = ok
    actionMessage.value = (res && res.msg) || `${label}已${ok ? '完成' : '失败'}`
    setTimeout(() => { actionMessage.value = '' }, 5000)
    if (ok) {
      loadDashboard()
      loadSiteChart()
      loadDownloaderOverview()
    }
  } catch (err) {
    actionOk.value = false
    actionMessage.value = err?.message || `${label}失败`
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

function sitePercent(value) {
  const total = siteTrafficTotal.value
  if (!total) return '0%'
  return `${Math.round(((Number(value) || 0) / total) * 100)}%`
}

async function loadSiteChart() {
  try {
    const res = await getPluginApi(props.api, 'site_stat_chart')
    Object.assign(siteChart, res || {})
  } catch {
    /* 无站点数据时静默显示空态 */
  }
}

async function loadDownloaderOverview() {
  try {
    const res = await getPluginApi(props.api, 'downloader_overview')
    downloaders.value = (res && res.downloaders) || []
  } catch {
    downloaders.value = []
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
  return task?.color === 'error' || /失败|异常|错误/.test(String(task?.state || ''))
}

const taskCards = computed(() => [...(data.tasks || [])].sort((a, b) => {
  const aw = isTaskBad(a) ? 0 : a.enabled ? 1 : 2
  const bw = isTaskBad(b) ? 0 : b.enabled ? 1 : 2
  return aw - bw
}))

const issueItems = computed(() => {
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
  if (!data.enabled) return [{ name: '运行状态', detail: '插件当前未启用', detailRows: [], ok: false }]
  return []
})
const issueCount = computed(() => Math.max(Number(data.task_failed) || 0, issueItems.value.length))
const primaryIssue = computed(() => issueItems.value[0] || { name: '系统状态', detail: '当前任务和健康巡查未发现阻塞项', detailRows: [], ok: true })
const issueTitle = computed(() => issueCount.value > 0 ? `${issueCount.value} 项需要处理` : '运行平稳')
const issueDesc = computed(() => {
  if (error.value) return error.value
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
  { label: '启用组件', value: `${data.task_on} / ${data.task_total}`, icon: 'mdi-layers-triple-outline', tone: 'blue' },
  { label: '异常组件', value: String(issueCount.value), icon: 'mdi-shield-alert-outline', tone: issueCount.value ? 'red' : 'green' },
  { label: '站点流量', value: formatGB(siteTrafficTotal.value), icon: 'mdi-chart-line-variant', tone: 'amber' },
])

const actionGroups = [
  {
    group: '汇报与追新',
    icon: 'mdi-newspaper-variant-outline',
    actions: [
      { path: 'run_daily_report', label: '每日汇报', icon: 'mdi-send-clock-outline', tone: 'green' },
      { path: 'run_subscribe_reminder', label: '订阅追新', icon: 'mdi-bell-badge-outline', tone: 'blue' },
    ],
  },
  {
    group: '站点与下载器',
    icon: 'mdi-download-network-outline',
    actions: [
      { path: 'run_site_stat', label: '站点统计', icon: 'mdi-chart-pie', tone: 'blue' },
      { path: 'run_downloader_tag', label: '种子标签', icon: 'mdi-tag-plus-outline', tone: 'cyan' },
      { path: 'run_seed_clean', label: '自动删种', icon: 'mdi-delete-sweep-outline', tone: 'red' },
    ],
  },
  {
    group: '系统维护',
    icon: 'mdi-cog-outline',
    actions: [
      { path: 'run_backup', label: '配置备份', icon: 'mdi-database-arrow-up-outline', tone: 'violet' },
      { path: 'run_log_clean', label: '日志清理', icon: 'mdi-broom', tone: 'violet' },
      { path: 'run_health_check', label: '健康巡查', icon: 'mdi-heart-pulse', tone: 'green' },
      { path: 'run_mp_update', label: 'MP 更新', icon: 'mdi-update', tone: 'amber' },
    ],
  },
  {
    group: '插件治理',
    icon: 'mdi-puzzle-check-outline',
    actions: [
      { path: 'run_market_update', label: '插件更新', icon: 'mdi-cloud-sync-outline', tone: 'amber' },
      { path: 'run_plugin_uninstall', label: '插件卸载', icon: 'mdi-puzzle-remove-outline', tone: 'red' },
    ],
  },
]
const actionItems = computed(() => actionGroups.flatMap(group => group.actions))

onMounted(() => { loadDashboard(); loadSiteChart(); loadDownloaderOverview() })
</script>

<template>
  <div class="agentops-dashboard dashboard-shell" :class="dashboardThemeClass">
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
        <VBtn size="small" variant="text" class="top-button text-none" @click="emit('switch')">设置</VBtn>
        <VBtn size="small" icon="mdi-close" variant="text" class="top-button top-button--icon" @click="emit('close')" />
      </header>

      <section class="dashboard-canvas">
        <article class="panel alert-panel" :class="{ 'alert-panel--ok': issueCount === 0 && !error }">
          <div class="alert-top">
            <div class="alert-icon">
              <VIcon :icon="issueCount || error ? 'mdi-alert-outline' : 'mdi-shield-check-outline'" size="28" />
            </div>
            <div class="alert-copy">
              <h1>{{ error ? '数据加载失败' : issueTitle }}</h1>
              <p>{{ issueDesc }}</p>
            </div>
          </div>
          <div class="alert-line">
            <b>{{ primaryIssue.name }}</b>
            <strong>{{ primaryIssue.detail }}</strong>
            <span class="badge" :class="{ 'badge--ok': issueCount === 0 && !error }">{{ issueCount || error ? '异常' : '正常' }}</span>
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
              <div class="site-table site-legend">
                <div class="th">站点</div><div class="th">上传</div><div class="th">下载</div><div class="th">占比</div>
                <template v-for="site in siteTableRows" :key="site.name">
                  <div class="site-row-cell site-name"><i class="dot" :style="{ background: site.color, boxShadow: `0 0 8px ${site.glow}` }"></i>{{ site.name }}</div>
                  <div class="site-row-cell">↑ {{ formatGB(site.upload) }}</div>
                  <div class="site-row-cell">↓ {{ formatGB(site.download) }}</div>
                  <div class="site-row-cell">{{ sitePercent(site.value) }}</div>
                </template>
              </div>
            </div>
          </div>
          <div v-else class="site-body site-body--empty">
            <div class="donut-zone">
              <div class="donut donut--empty" :style="sitePieStyle">
                <div class="donut-core">
                  <strong>0</strong>
                  <span>待刷新</span>
                </div>
              </div>
            </div>
            <div class="site-data">
              <div class="site-stats">
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
              <div class="site-table site-table--empty">
                <div class="th">站点</div><div class="th">上传</div><div class="th">下载</div><div class="th">占比</div>
                <div class="site-row-cell site-empty-row">
                  <VIcon icon="mdi-chart-pie" size="18" />
                  <div>
                    <strong>暂无站点增量</strong>
                    <span>刷新后显示最近可用快照</span>
                  </div>
                </div>
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
                  class="cmd-btn action-btn action-item text-none"
                  :class="[`cmd-btn--${action.tone}`, `action-btn--${action.tone}`]"
                  @click="runAction(action.path, action.label)"
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
                <strong>暂无活动下载器</strong>
                <span>刷新后同步正在下载的任务</span>
              </div>
              <span class="ok-chip ok-chip--idle">等待</span>
            </div>
            <div class="downloader-card downloader-card--empty downloader-card--ghost">
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
            <div v-for="task in taskCards" :key="task.key" class="module task-card" :class="{ 'module--bad': isTaskBad(task), 'module--off': !task.enabled }">
              <div class="module-top">
                <i class="dot" :class="{ red: isTaskBad(task), gray: !task.enabled }"></i>
                <span class="module-title">{{ task.name }}</span>
                <span class="state" :class="{ bad: isTaskBad(task), off: !task.enabled }">{{ isTaskBad(task) ? '失败' : task.enabled ? 'ON' : 'OFF' }}</span>
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
  --shell-panel-hi: 0.48;
  --shell-panel-lo: 0.22;
  --shell-stage-alpha: 0.18;
  --frame-panel-hi: 0.66;
  --frame-panel-lo: 0.42;
  --frame-stage-alpha: 0.14;
  --toolbar-panel-hi: 0.54;
  --toolbar-panel-lo: 0.28;
  --panel-glass-hi: 0.62;
  --panel-glass-lo: 0.34;
  --panel-fill-alpha: 0.010;
  --panel-inner-alpha: 0.18;
  --panel-inner-strong-alpha: 0.22;
  --status-panel-alpha: 0.40;
  --shell-cyan-alpha: 0.13;
  --shell-blue-alpha: 0.11;
  --frame-cyan-alpha: 0.060;
  --frame-violet-alpha: 0.052;
  --top-button-alpha: 0.18;
  --top-button-primary-alpha: 0.20;
  --status-red-glow-alpha: 0.16;
  --status-green-glow-alpha: 0.13;
  --status-mix-alpha: 0.38;
  --alert-line-alpha: 0.44;
  --metric-accent-alpha: 0.060;
  --site-cyan-alpha: 0.070;
  --site-blue-alpha: 0.055;
  --soft-line-alpha: 0.075;
  --donut-core-line-alpha: 0.060;
  --donut-core-panel-alpha: 0.96;
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
  padding: 8px;
  color: rgba(var(--ink), 0.94);
  font-family: "Microsoft YaHei", "PingFang SC", "Noto Sans SC", system-ui, sans-serif;
}

.agentops-dashboard.agentops-theme--light {
  --shell-panel-hi: 0.34;
  --shell-panel-lo: 0.16;
  --shell-stage-alpha: 0.30;
  --frame-panel-hi: 0.50;
  --frame-panel-lo: 0.30;
  --frame-stage-alpha: 0.26;
  --toolbar-panel-hi: 0.38;
  --toolbar-panel-lo: 0.20;
  --panel-glass-hi: 0.48;
  --panel-glass-lo: 0.25;
  --panel-fill-alpha: 0.018;
  --panel-inner-alpha: 0.12;
  --panel-inner-strong-alpha: 0.16;
  --status-panel-alpha: 0.32;
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
  --shell-panel-hi: 0.026;
  --shell-panel-lo: 0.006;
  --shell-stage-alpha: 0.002;
  --frame-panel-hi: 0.032;
  --frame-panel-lo: 0.008;
  --frame-stage-alpha: 0.002;
  --toolbar-panel-hi: 0.034;
  --toolbar-panel-lo: 0.010;
  --panel-glass-hi: 0.040;
  --panel-glass-lo: 0.010;
  --panel-fill-alpha: 0.002;
  --panel-inner-alpha: 0.012;
  --panel-inner-strong-alpha: 0.018;
  --status-panel-alpha: 0.030;
  --shell-cyan-alpha: 0.012;
  --shell-blue-alpha: 0.010;
  --frame-cyan-alpha: 0.010;
  --frame-violet-alpha: 0.009;
  --top-button-alpha: 0.018;
  --top-button-primary-alpha: 0.028;
  --status-red-glow-alpha: 0.038;
  --status-green-glow-alpha: 0.032;
  --status-mix-alpha: 0.022;
  --alert-line-alpha: 0.024;
  --metric-accent-alpha: 0.014;
  --site-cyan-alpha: 0.012;
  --site-blue-alpha: 0.010;
  --soft-line-alpha: 0.012;
  --donut-core-line-alpha: 0.010;
  --donut-core-panel-alpha: 0.040;
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
  border-radius: 30px;
  padding: 28px;
  border: 1px solid rgba(var(--line), 0.075);
  background:
    radial-gradient(circle at 78% 8%, rgba(var(--cyan), var(--shell-cyan-alpha)), transparent 31%),
    radial-gradient(circle at 16% 10%, rgba(var(--blue), var(--shell-blue-alpha)), transparent 29%),
    linear-gradient(180deg, rgba(var(--panel), var(--shell-panel-hi)), rgba(var(--panel), var(--shell-panel-lo))),
    rgba(var(--stage), var(--shell-stage-alpha));
  box-shadow:
    inset 0 1px 0 rgba(var(--line), 0.055),
    inset 0 -1px 0 rgba(0, 0, 0, 0.10),
    0 18px 48px rgba(0, 0, 0, 0.10),
    0 5px 16px rgba(0, 0, 0, 0.060);
  backdrop-filter: blur(26px) saturate(145%);
}

.agentops-frame {
  width: min(1208px, 100%);
  min-height: 790px;
  margin: 0 auto;
  overflow: hidden;
  border-radius: 22px;
  border: 1px solid rgba(var(--line), 0.105);
  background:
    radial-gradient(circle at 82% 0%, rgba(var(--cyan), var(--frame-cyan-alpha)), transparent 34%),
    radial-gradient(circle at 9% 100%, rgba(var(--violet), var(--frame-violet-alpha)), transparent 35%),
    linear-gradient(145deg, rgba(var(--panel), var(--frame-panel-hi)), rgba(var(--panel), var(--frame-panel-lo))),
    rgba(var(--stage), var(--frame-stage-alpha));
  background-color: rgba(var(--stage), var(--frame-stage-alpha)) !important;
  box-shadow:
    inset 0 1px 0 rgba(var(--line), 0.095),
    inset 0 -1px 0 rgba(0, 0, 0, 0.10),
    0 14px 34px rgba(0, 0, 0, 0.09),
    0 4px 12px rgba(0, 0, 0, 0.055);
  backdrop-filter: blur(30px) saturate(155%);
}

.agentops-toolbar {
  height: 50px;
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 0 16px;
  border-bottom: 1px solid rgba(var(--line), 0.072);
  background:
    linear-gradient(180deg, rgba(var(--panel), var(--toolbar-panel-hi)), rgba(var(--panel), var(--toolbar-panel-lo))),
    rgba(var(--line), 0.018);
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
  height: 740px;
  padding: 12px;
  display: grid;
  grid-template-columns: minmax(300px, 410px) minmax(300px, 410px) minmax(280px, 1fr);
  grid-template-rows: 164px 300px 218px;
  gap: 10px;
}

.panel {
  position: relative;
  min-width: 0;
  overflow: hidden;
  border-radius: 18px;
  border: 1px solid rgba(var(--line), 0.092);
  background:
    linear-gradient(180deg, rgba(var(--panel), var(--panel-glass-hi)), rgba(var(--panel), var(--panel-glass-lo))),
    rgba(var(--line), var(--panel-fill-alpha));
  box-shadow: var(--shadow-panel);
  backdrop-filter: blur(24px) saturate(150%);
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
.alert-line b {
  color: rgba(var(--red), 0.98);
  font-weight: 850;
  white-space: nowrap;
}
.alert-panel--ok .alert-line b {
  color: rgba(var(--green), 0.98);
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
  border-radius: 18px;
  padding: 16px 14px;
  display: grid;
  grid-template-columns: 44px minmax(0, 1fr);
  gap: 12px;
  align-items: center;
  border: 1px solid rgba(var(--line), 0.085);
  background:
    radial-gradient(circle at 100% 0%, rgba(var(--accent), var(--metric-accent-alpha)), transparent 52%),
    linear-gradient(180deg, rgba(var(--panel), var(--panel-glass-hi)), rgba(var(--panel), var(--panel-glass-lo))),
    rgba(var(--line), var(--panel-fill-alpha));
  box-shadow: var(--shadow-block);
  backdrop-filter: blur(22px) saturate(145%);
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
  grid-template-columns: 230px minmax(0, 1fr);
  gap: 16px;
  padding: 8px 16px 16px;
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
  filter: saturate(82%);
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
  display: grid;
  grid-template-rows: 76px minmax(0, 1fr);
  gap: 12px;
}
.site-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}
.site-stat {
  min-width: 0;
  border-radius: 15px;
  border: 1px solid rgba(var(--line), 0.070);
  padding: 12px 13px;
  background:
    linear-gradient(180deg, rgba(var(--line), 0.068), rgba(var(--line), 0.022)),
    rgba(var(--panel), var(--panel-inner-strong-alpha));
  box-shadow: var(--shadow-block);
}
.site-stat span,
.site-table .th {
  color: rgba(var(--muted), 0.70);
  font-size: 12px;
  font-weight: 720;
}
.site-stat strong {
  display: block;
  margin-top: 9px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 18px;
  line-height: 1;
  font-weight: 890;
}
.site-table {
  min-height: 0;
  display: grid;
  grid-template-columns: 1.05fr 1fr 1fr 0.72fr;
  gap: 8px 12px;
  align-content: start;
  overflow: auto;
  padding-right: 2px;
  color: rgba(var(--ink), 0.88);
  font-size: 13px;
  font-weight: 700;
}
.site-row-cell {
  min-width: 0;
  min-height: 32px;
  display: flex;
  align-items: center;
  border-radius: 11px;
  padding: 0 10px;
  background: rgba(var(--line), 0.022);
  box-shadow:
    inset 0 1px 0 rgba(var(--line), 0.045),
    inset 0 -1px 0 rgba(0, 0, 0, 0.07),
    0 2px 5px rgba(0, 0, 0, 0.040);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.site-table--empty {
  grid-auto-rows: 32px;
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
.site-name {
  gap: 8px;
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
  display: flex;
  flex-direction: column;
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
  margin-bottom: 26px;
}
.command-body {
  min-height: 0;
  flex: 1;
  display: grid;
  grid-template-rows: 112px 146px 146px 112px;
  gap: 18px;
  align-content: stretch;
  overflow: visible;
  padding-right: 2px;
}
.command-group {
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  border-radius: 16px;
  padding: 17px 14px;
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
  margin-bottom: 16px;
  color: rgba(var(--muted), 0.70);
  font-size: 12px;
  font-weight: 760;
}
.cmd-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(118px, 1fr));
  gap: 9px;
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
  overflow: visible;
  text-overflow: clip;
  line-height: 1.18;
  white-space: nowrap;
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
  grid-auto-rows: 79px;
  align-content: start;
  gap: 8px;
  overflow: auto;
  padding: 4px 14px 10px;
}
.module {
  min-width: 0;
  height: 79px;
  border-radius: 13px;
  padding: 10px 10px 9px;
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
  border-color: rgba(var(--line), 0.055);
  background:
    radial-gradient(circle at 78% 8%, rgba(var(--cyan), var(--shell-cyan-alpha)), transparent 31%),
    radial-gradient(circle at 16% 10%, rgba(var(--blue), var(--shell-blue-alpha)), transparent 29%),
    linear-gradient(180deg, rgba(var(--line), 0.008), rgba(var(--line), 0.002)),
    rgba(var(--stage), var(--shell-stage-alpha));
  box-shadow:
    inset 0 1px 0 rgba(var(--line), 0.026),
    0 6px 16px rgba(0, 0, 0, 0.018);
}

.agentops-dashboard.agentops-theme--transparent .agentops-frame {
  border-color: rgba(var(--line), 0.074);
  background:
    radial-gradient(circle at 82% 0%, rgba(var(--cyan), var(--frame-cyan-alpha)), transparent 34%),
    radial-gradient(circle at 9% 100%, rgba(var(--violet), var(--frame-violet-alpha)), transparent 35%),
    linear-gradient(145deg, rgba(var(--line), 0.010), rgba(var(--line), 0.003)),
    rgba(var(--stage), var(--frame-stage-alpha));
  background-color: rgba(var(--stage), var(--frame-stage-alpha)) !important;
  box-shadow:
    inset 0 1px 0 rgba(var(--line), 0.032),
    0 4px 12px rgba(0, 0, 0, 0.016);
}

.agentops-dashboard.agentops-theme--transparent .agentops-toolbar {
  border-bottom-color: rgba(var(--line), 0.050);
  background:
    linear-gradient(180deg, rgba(var(--line), 0.012), rgba(var(--line), 0.003)),
    rgba(var(--stage), 0.002);
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
.agentops-dashboard.agentops-theme--transparent .alert-line,
.agentops-dashboard.agentops-theme--transparent .site-stat,
.agentops-dashboard.agentops-theme--transparent .site-row-cell,
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

@media (max-width: 1180px) {
  .dashboard-shell {
    padding: 18px;
  }
  .agentops-frame {
    min-height: 0;
  }
  .dashboard-canvas {
    min-height: 0;
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
}

@media (max-width: 760px) {
  .agentops-dashboard {
    padding: 4px;
  }
  .dashboard-shell {
    padding: 10px;
    border-radius: 22px;
  }
  .agentops-toolbar {
    height: auto;
    min-height: 50px;
    flex-wrap: wrap;
    padding: 10px 12px;
  }
  .brand {
    width: 100%;
  }
  .toolbar-space {
    display: none;
  }
  .dashboard-canvas,
  .metrics-panel,
  .site-body,
  .site-stats,
  .cmd-grid,
  .runtime-track {
    grid-template-columns: 1fr;
  }
  .dashboard-canvas {
    padding: 10px;
  }
  .site-panel,
  .command-panel {
    grid-column: auto;
  }
  .site-body,
  .download-body,
  .runtime-track {
    height: auto;
  }
  .site-table {
    grid-template-columns: minmax(92px, 1fr) 0.75fr;
  }
  .site-table .th:nth-child(3),
  .site-table .th:nth-child(4),
  .site-row-cell:nth-of-type(4n),
  .site-row-cell:nth-of-type(4n + 1) {
    display: none;
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
</style>
