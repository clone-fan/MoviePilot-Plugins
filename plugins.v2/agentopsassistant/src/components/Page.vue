<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { getPluginApi, postPluginApi } from './api'

const props = defineProps({ api: { type: [Object, Function], default: null } })
const emit = defineEmits(['close', 'switch'])

const loading = ref(true)
const error = ref('')
const actionRunning = ref('')
const actionMessage = ref('')
const data = reactive({
  enabled: false,
  summary: '',
  tasks: [],
  task_total: 0,
  task_on: 0,
  task_failed: 0,
  health: { time: '', success: null, output: '' },
})

const overallColor = computed(() => {
  if (!data.enabled) return 'default'
  if (data.task_failed > 0) return 'error'
  return 'success'
})
const overallText = computed(() => {
  if (!data.enabled) return '未启用'
  if (data.task_failed > 0) return `${data.task_failed} 项异常`
  return '运行正常'
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
  try {
    const res = await postPluginApi(props.api, path)
    const ok = !res || res.code === 0 || res.code === undefined
    actionMessage.value = (res && res.msg) || `${label}已${ok ? '完成' : '失败'}`
    setTimeout(() => { actionMessage.value = '' }, 5000)
    if (ok) {
      loadDashboard()
      loadSiteChart()
      loadDownloaderOverview()
    }
  } catch (err) {
    actionMessage.value = err?.message || `${label}失败`
    setTimeout(() => { actionMessage.value = '' }, 5000)
  } finally {
    actionRunning.value = ''
  }
}

const siteChart = reactive({ date: '', basis: 'today', sites: [], upload_total: 0, download_total: 0 })
function formatGB(bytes) {
  const n = Number(bytes) || 0
  const gb = n / (1024 ** 3)
  if (gb >= 1) return gb.toFixed(2) + ' GB'
  return (n / (1024 ** 2)).toFixed(1) + ' MB'
}
const siteRows = computed(() => [...(siteChart.sites || [])].sort((a, b) => ((b.upload || 0) + (b.download || 0)) - ((a.upload || 0) + (a.download || 0))))
const sitePieColors = ['#22c55e', '#38bdf8', '#f59e0b', '#a78bfa', '#fb7185', '#14b8a6', '#eab308', '#60a5fa']
const siteTrafficTotal = computed(() => siteRows.value.reduce((sum, site) => sum + (Number(site.upload) || 0) + (Number(site.download) || 0), 0))
const siteDateLabel = computed(() => {
  if (!siteChart.date) return '—'
  return siteChart.basis === 'latest' ? `最近快照 ${siteChart.date}` : siteChart.date
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
    return { ...site, value, start, end, color: sitePieColors[index % sitePieColors.length] }
  })
})
const sitePieStyle = computed(() => {
  if (!sitePieSegments.value.length) {
    return { background: 'rgba(var(--v-theme-on-surface), 0.08)' }
  }
  const stops = sitePieSegments.value
    .map(item => `${item.color} ${item.start.toFixed(2)}% ${item.end.toFixed(2)}%`)
    .join(', ')
  return { background: `conic-gradient(${stops})` }
})
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
    /* 无站点数据时静默不显示 */
  }
}

const downloaders = ref([])
async function loadDownloaderOverview() {
  try {
    const res = await getPluginApi(props.api, 'downloader_overview')
    downloaders.value = (res && res.downloaders) || []
  } catch {
    downloaders.value = []
  }
}

const hasSiteChart = computed(() => !!(siteChart.sites && siteChart.sites.length))
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
      return { name, detail, ok, color: ok ? 'success' : 'error', icon: iconMap[name] || 'mdi-check-decagram-outline' }
    })
})

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
]

onMounted(() => { loadDashboard(); loadSiteChart(); loadDownloaderOverview() })
</script>

<template>
  <div class="agentops-dashboard">
    <VCard class="agentops-card" elevation="0">
      <VToolbar density="compact" class="agentops-toolbar">
        <VIcon icon="mdi-view-dashboard-outline" class="ms-3 me-2" color="primary" />
        <div class="text-subtitle-1 font-weight-bold">MP 运维助手 · 仪表盘</div>
        <VSpacer />
        <VBtn size="small" color="primary" variant="tonal" prepend-icon="mdi-refresh" class="text-none me-1" :loading="loading" @click="loadDashboard">刷新</VBtn>
        <VBtn size="small" variant="text" prepend-icon="mdi-cog-outline" class="text-none" @click="emit('switch')">设置</VBtn>
        <VBtn size="small" icon="mdi-close" variant="text" @click="emit('close')" />
      </VToolbar>
      <VDivider />

      <div class="agentops-body">
        <VAlert v-if="error" type="error" variant="tonal" class="mb-3" :icon="false" :text="error" />

      <!-- 状态总览 -->
      <div class="overview-strip">
        <div class="overview-item">
          <VIcon icon="mdi-shield-check-outline" :color="overallColor" size="22" />
          <span>运行状态</span>
          <strong>{{ overallText }}</strong>
        </div>
        <div class="overview-item">
          <VIcon icon="mdi-view-grid-check-outline" color="primary" size="22" />
          <span>启用组件</span>
          <strong>{{ data.task_on }} / {{ data.task_total }}</strong>
        </div>
        <div class="overview-item">
          <VIcon :icon="data.task_failed > 0 ? 'mdi-close-circle-outline' : 'mdi-check-circle-outline'" :color="data.task_failed > 0 ? 'error' : 'success'" size="22" />
          <span>异常组件</span>
          <strong>{{ data.task_failed }}</strong>
        </div>
        <div class="overview-item">
          <VIcon icon="mdi-heart-pulse" :color="healthColor" size="22" />
          <span>健康巡查</span>
          <strong>{{ healthText }}</strong>
        </div>
      </div>

      <!-- 站点数据统计 + 手动触发：左右各一个 -->
      <VRow dense class="mt-2 dashboard-main-grid">
        <VCol cols="12" lg="7">
          <VCard elevation="0" class="glass-panel h-100">
            <VCardTitle class="compact-card-title">
              <VIcon icon="mdi-chart-pie" color="primary" class="me-2" />站点数据统计
              <VSpacer />
              <VBtn size="small" variant="tonal" color="primary" prepend-icon="mdi-refresh"
                :loading="actionRunning === 'run_site_stat'" @click="runAction('run_site_stat', '刷新站点数据')">
                刷新
              </VBtn>
            </VCardTitle>
            <VCardText class="compact-card-text">
              <div v-if="hasSiteChart" class="site-stat-layout">
                <div class="site-pie-wrap">
                  <div class="site-pie" :style="sitePieStyle">
                    <div class="site-pie-center">
                      <strong>{{ siteRows.length }}</strong>
                      <span>站点</span>
                    </div>
                  </div>
                </div>
                <div class="site-stat-content">
                  <div class="site-summary">
                    <div class="site-summary-item">
                      <VIcon icon="mdi-upload-network-outline" color="success" size="20" />
                      <span>上传增量</span>
                      <strong>{{ formatGB(siteChart.upload_total) }}</strong>
                    </div>
                    <div class="site-summary-item">
                      <VIcon icon="mdi-download-network-outline" color="info" size="20" />
                      <span>下载增量</span>
                      <strong>{{ formatGB(siteChart.download_total) }}</strong>
                    </div>
                    <div class="site-summary-item">
                      <VIcon icon="mdi-calendar-blank-outline" color="primary" size="20" />
                      <span>统计日期</span>
                      <strong>{{ siteDateLabel }}</strong>
                    </div>
                  </div>
                  <div class="site-legend">
                    <div v-for="site in sitePieSegments" :key="site.name" class="site-legend-row">
                      <span class="site-dot" :style="{ background: site.color }"></span>
                      <strong class="site-name">{{ site.name }}</strong>
                      <span class="site-traffic">↑ {{ formatGB(site.upload) }} ｜ ↓ {{ formatGB(site.download) }}</span>
                      <span class="site-percent">{{ sitePercent(site.value) }}</span>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="site-empty">
                <VIcon icon="mdi-chart-pie" size="24" color="primary" />
                <div>
                  <div class="font-weight-medium">暂无站点增量</div>
                  <div class="text-caption text-medium-emphasis">刷新后显示最近可用快照</div>
                </div>
              </div>
            </VCardText>
          </VCard>
        </VCol>

        <!-- 手动触发：模块化放在站点数据右边 -->
        <VCol cols="12" lg="5">
          <VCard elevation="0" class="glass-panel action-panel h-100">
            <VCardText class="compact-card-text action-panel-body">
              <div class="action-scroll">
                <div v-for="grp in actionGroups" :key="grp.group" class="action-group">
                  <div class="action-group-title">{{ grp.group }}</div>
                  <div class="action-buttons">
                    <VBtn
                      v-for="action in grp.actions"
                      :key="action.path"
                      block
                      variant="text"
                      density="comfortable"
                      :loading="actionRunning === action.path"
                      @click="runAction(action.path, action.label)"
                      class="action-btn text-none"
                      :class="`action-btn--${action.tone}`"
                    >
                      <span class="action-btn-main">
                        <VIcon :icon="action.icon" size="18" />
                        <span class="action-btn-label">{{ action.label }}</span>
                      </span>
                      <span class="action-btn-desc">{{ action.desc }}</span>
                    </VBtn>
                  </div>
                </div>
              </div>
              <VAlert v-if="actionMessage" type="info" variant="tonal" density="compact" class="mt-3" :icon="false" :text="actionMessage" />
            </VCardText>
          </VCard>
        </VCol>
      </VRow>

      <!-- 下载器活动种子 -->
      <VCard v-if="downloaders.length" elevation="0" class="glass-panel mt-2">
        <VCardTitle class="compact-card-title">
          <VIcon icon="mdi-download-network-outline" color="primary" class="me-2" />下载器活动种子
        </VCardTitle>
        <VList class="bg-transparent py-0" density="compact">
          <template v-for="(d, i) in downloaders" :key="d.name">
            <VListItem class="py-1">
              <VListItemTitle class="font-weight-medium">{{ d.name }}</VListItemTitle>
              <VListItemSubtitle class="mt-1">下载中 {{ d.count }} 个｜↓ {{ formatGB(d.dl_speed) }}/s　↑ {{ formatGB(d.up_speed) }}/s</VListItemSubtitle>
            </VListItem>
          </template>
        </VList>
      </VCard>

      <!-- 组件运行状况 + 健康巡查：模块化展示 -->
      <VRow dense class="mt-2">
        <VCol cols="12" md="6">
          <VCard elevation="0" class="glass-panel h-100">
            <VCardTitle class="compact-card-title">
              <VIcon icon="mdi-view-grid-check-outline" color="primary" class="me-2" />组件运行状况
            </VCardTitle>
            <VSkeletonLoader v-if="loading" type="list-item-avatar-three-line@3" />
            <VCardText v-else class="compact-card-text">
              <div class="task-grid">
                <div v-for="task in data.tasks" :key="task.key" class="task-card">
                  <div class="task-head">
                    <VAvatar size="34" variant="tonal" :color="task.enabled ? task.color : 'default'">
                      <VIcon :icon="task.icon" size="18" />
                    </VAvatar>
                    <div class="task-title-wrap">
                      <div class="task-name">{{ task.name }}</div>
                      <div class="task-meta">下次 {{ task.next || '—' }}</div>
                    </div>
                    <VChip size="x-small" variant="tonal" :color="task.enabled ? 'success' : 'default'">{{ task.enabled ? 'ON' : 'OFF' }}</VChip>
                  </div>
                  <div class="task-foot">
                    <span>最近 {{ task.last_time || '—' }}</span>
                    <VChip size="x-small" variant="tonal" :color="task.color">{{ task.state }}</VChip>
                  </div>
                  <div class="task-summary">{{ task.last_summary }}</div>
                </div>
              </div>
            </VCardText>
          </VCard>
        </VCol>

        <VCol cols="12" md="6">
          <VCard elevation="0" class="glass-panel h-100">
            <VCardTitle class="compact-card-title">
              <VIcon icon="mdi-heart-pulse" color="primary" class="me-2" />健康巡查
              <VSpacer />
              <VChip size="x-small" variant="tonal" :color="healthColor">{{ healthText }}</VChip>
            </VCardTitle>
            <VCardText class="compact-card-text">
              <div v-if="data.health.time" class="panel-note">最近 {{ data.health.time }}</div>
              <div v-if="healthItems.length" class="health-grid">
                <div v-for="item in healthItems" :key="item.name" class="health-card">
                  <div class="health-card-head">
                    <VIcon :icon="item.icon" :color="item.color" size="20" />
                    <strong>{{ item.name }}</strong>
                    <VChip size="x-small" variant="tonal" :color="item.color">{{ item.ok ? '正常' : '异常' }}</VChip>
                  </div>
                  <div class="health-detail">{{ item.detail }}</div>
                </div>
              </div>
              <div v-else class="empty-soft">暂无记录</div>
            </VCardText>
          </VCard>
        </VCol>
      </VRow>
      </div>
    </VCard>
  </div>
</template>

<style scoped>
.agentops-dashboard {
  padding: 10px;
}
.agentops-card {
  border-radius: 18px;
  overflow: hidden;
  border: 1px solid rgba(var(--v-theme-on-surface), 0.08);
  background:
    linear-gradient(145deg, rgba(var(--v-theme-surface), 0.94), rgba(var(--v-theme-surface), 0.76));
  box-shadow: 0 18px 48px rgba(0, 0, 0, 0.16);
}
.agentops-toolbar {
  position: sticky;
  top: 0;
  z-index: 10;
  background: rgba(var(--v-theme-surface), 0.86);
  backdrop-filter: blur(18px);
}
.agentops-body {
  padding: 14px;
}
.agentops-dashboard :deep(.v-card) { border-radius: 14px; }
.agentops-dashboard :deep(.v-row) { margin: -4px; }
.agentops-dashboard :deep(.v-col) { padding: 4px; }
.glass-panel {
  border: 1px solid rgba(var(--v-theme-on-surface), 0.08);
  background:
    radial-gradient(circle at top left, rgba(var(--v-theme-primary), 0.08), transparent 34%),
    linear-gradient(180deg, rgba(var(--v-theme-surface), 0.78), rgba(var(--v-theme-surface), 0.58));
  backdrop-filter: blur(18px);
  box-shadow: inset 0 1px 0 rgba(var(--v-theme-on-surface), 0.05), 0 12px 32px rgba(0, 0, 0, 0.10);
}
.compact-card-title {
  display: flex;
  align-items: center;
  min-height: 44px;
  padding: 10px 12px 6px;
  font-size: 15px;
  font-weight: 700;
  line-height: 1.2;
}
.compact-card-text {
  padding: 10px 12px 12px;
}
.overview-strip {
  display: grid;
  grid-template-columns: repeat(4, minmax(118px, 1fr));
  align-items: center;
  gap: 8px;
}
.overview-item {
  display: grid;
  grid-template-columns: 28px minmax(0, 1fr);
  align-items: center;
  column-gap: 8px;
  min-height: 58px;
  padding: 10px 12px;
  min-width: 0;
  border: 1px solid rgba(var(--v-theme-on-surface), 0.08);
  border-radius: 14px;
  background:
    linear-gradient(180deg, rgba(var(--v-theme-surface), 0.72), rgba(var(--v-theme-surface), 0.50));
  box-shadow: inset 0 1px 0 rgba(var(--v-theme-on-surface), 0.04);
}
.overview-item span {
  color: rgba(var(--v-theme-on-surface), 0.62);
  font-size: 12px;
  line-height: 1.2;
}
.overview-item strong {
  grid-column: 2;
  font-size: 15px;
  white-space: nowrap;
  line-height: 1.25;
}
.dashboard-main-grid {
  align-items: stretch;
}
.site-stat-layout {
  display: grid;
  grid-template-columns: 166px minmax(0, 1fr);
  gap: 16px;
  align-items: center;
  min-height: 246px;
}
.site-pie-wrap {
  display: grid;
  place-items: center;
  min-width: 0;
}
.site-pie {
  width: 150px;
  aspect-ratio: 1;
  position: relative;
  display: grid;
  place-items: center;
  border-radius: 50%;
  box-shadow: inset 0 0 0 1px rgba(var(--v-theme-on-surface), 0.08), 0 12px 30px rgba(0, 0, 0, 0.16);
}
.site-pie::after {
  content: "";
  position: absolute;
  inset: 28px;
  border-radius: 50%;
  background: rgba(var(--v-theme-surface), 0.92);
  box-shadow: inset 0 1px 0 rgba(var(--v-theme-on-surface), 0.05);
}
.site-pie-center {
  position: relative;
  z-index: 1;
  display: grid;
  place-items: center;
  line-height: 1.1;
}
.site-pie-center strong {
  font-size: 24px;
  font-weight: 800;
}
.site-pie-center span {
  color: rgba(var(--v-theme-on-surface), 0.62);
  font-size: 12px;
}
.site-stat-content {
  min-width: 0;
  display: grid;
  gap: 10px;
}
.site-summary {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
}
.site-summary-item {
  display: grid;
  grid-template-columns: 22px minmax(0, 1fr);
  align-items: center;
  gap: 5px 7px;
  min-height: 52px;
  padding: 8px 10px;
  border: 1px solid rgba(var(--v-theme-on-surface), 0.07);
  border-radius: 12px;
  background: rgba(var(--v-theme-on-surface), 0.035);
}
.site-summary-item span {
  min-width: 0;
  color: rgba(var(--v-theme-on-surface), 0.64);
  font-size: 12px;
}
.site-summary-item strong {
  grid-column: 2;
  font-size: 12px;
  white-space: nowrap;
}
.site-legend {
  display: grid;
  gap: 7px;
  max-height: 150px;
  overflow: auto;
  padding-right: 2px;
}
.site-legend-row {
  display: grid;
  grid-template-columns: 10px minmax(72px, 0.85fr) minmax(150px, 1.3fr) 44px;
  gap: 8px;
  align-items: center;
  min-height: 31px;
  padding: 5px 8px;
  border-radius: 10px;
  background: rgba(var(--v-theme-on-surface), 0.035);
}
.site-dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
}
.site-name,
.site-traffic {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.site-name {
  font-weight: 600;
  font-size: 12px;
}
.site-traffic {
  color: rgba(var(--v-theme-on-surface), 0.68);
  font-size: 12px;
}
.site-percent {
  justify-self: end;
  color: rgba(var(--v-theme-on-surface), 0.58);
  font-size: 12px;
  font-weight: 700;
}
.site-empty {
  display: flex;
  align-items: center;
  gap: 10px;
  min-height: 72px;
  margin-top: 8px;
  padding: 12px 14px;
  border-radius: 14px;
  background: rgba(var(--v-theme-primary), 0.06);
}
.action-panel {
  background:
    linear-gradient(180deg, rgba(var(--v-theme-surface), 0.8), rgba(var(--v-theme-surface), 0.62)),
    rgba(var(--v-theme-on-surface), 0.018);
}
.action-panel-body {
  padding: 14px !important;
}
.action-scroll {
  display: grid;
  gap: 13px;
  max-height: 285px;
  overflow: auto;
  padding-right: 3px;
}
.action-group {
  display: grid;
  gap: 7px;
}
.action-group-title {
  padding: 0 2px;
  color: rgba(var(--v-theme-on-surface), 0.46);
  font-size: 11px;
  font-weight: 750;
  line-height: 1.2;
}
.action-buttons {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}
.action-btn {
  --action-rgb: var(--v-theme-primary);
  min-height: 62px;
  justify-content: flex-start;
  border-radius: 12px;
  color: rgba(var(--v-theme-on-surface), 0.9);
  background: rgba(var(--v-theme-on-surface), 0.032);
  border: 1px solid rgba(var(--v-theme-on-surface), 0.075);
  box-shadow:
    inset 0 1px 0 rgba(var(--v-theme-on-surface), 0.035),
    0 10px 28px rgba(var(--v-theme-on-surface), 0.035);
  transition: background 180ms ease, border-color 180ms ease, box-shadow 180ms ease, color 180ms ease;
}
.action-btn:hover {
  color: rgb(var(--action-rgb));
  border-color: rgba(var(--action-rgb), 0.28);
  background: rgba(var(--action-rgb), 0.12);
  box-shadow:
    inset 0 1px 0 rgba(var(--v-theme-on-surface), 0.045),
    0 12px 30px rgba(var(--action-rgb), 0.08);
}
.action-btn--green { --action-rgb: var(--v-theme-success); }
.action-btn--blue { --action-rgb: var(--v-theme-primary); }
.action-btn--cyan { --action-rgb: var(--v-theme-info); }
.action-btn--red { --action-rgb: var(--v-theme-error); }
.action-btn--purple { --action-rgb: var(--v-theme-secondary); }
.action-btn--amber { --action-rgb: var(--v-theme-warning); }
.action-btn :deep(.v-btn__overlay) {
  display: none;
}
.action-btn :deep(.v-btn__content) {
  width: 100%;
  min-width: 0;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  gap: 7px;
  line-height: 1.2;
}
.action-btn-main {
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 7px;
}
.action-btn-main :deep(.v-icon) {
  color: rgb(var(--action-rgb));
}
.action-btn-label {
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 13px;
  font-weight: 800;
}
.action-btn-desc {
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: rgba(var(--v-theme-on-surface), 0.52);
  font-size: 11px;
  font-weight: 650;
  line-height: 1.15;
}
.task-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 9px;
  max-height: 272px;
  overflow: auto;
  padding-right: 2px;
}
.task-card,
.health-card {
  min-width: 0;
  border-radius: 13px;
  padding: 10px;
  border: 1px solid rgba(var(--v-theme-on-surface), 0.07);
  background: rgba(var(--v-theme-on-surface), 0.035);
  box-shadow: inset 0 1px 0 rgba(var(--v-theme-on-surface), 0.035);
}
.task-head {
  display: flex;
  align-items: center;
  gap: 8px;
}
.task-title-wrap {
  min-width: 0;
  flex: 1 1 auto;
}
.task-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 13px;
  font-weight: 750;
}
.task-meta,
.panel-note,
.task-foot,
.task-summary,
.health-detail,
.empty-soft {
  color: rgba(var(--v-theme-on-surface), 0.55);
  font-size: 11px;
  line-height: 1.35;
}
.task-foot {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  margin-top: 9px;
}
.task-foot span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.task-summary {
  margin-top: 6px;
  overflow: auto;
  white-space: nowrap;
  text-overflow: ellipsis;
}
.health-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 9px;
  max-height: 252px;
  overflow: auto;
  padding-right: 2px;
}
.panel-note {
  margin: -2px 0 8px;
}
.health-card-head {
  display: grid;
  grid-template-columns: 22px minmax(0, 1fr) auto;
  align-items: center;
  gap: 7px;
}
.health-card-head strong {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 13px;
}
.health-detail {
  margin-top: 7px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.empty-soft {
  min-height: 72px;
  display: grid;
  place-items: center;
  border-radius: 14px;
  background: rgba(var(--v-theme-on-surface), 0.035);
}
@media (max-width: 760px) {
  .overview-strip {
    grid-template-columns: 1fr;
  }
  .site-stat-layout,
  .site-summary,
  .action-buttons,
  .task-grid,
  .health-grid {
    grid-template-columns: 1fr;
  }
  .site-stat-layout {
    min-height: 0;
  }
  .site-legend-row {
    grid-template-columns: 10px minmax(80px, 1fr) 46px;
  }
  .site-traffic {
    grid-column: 2 / 4;
  }
}
</style>
