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

const siteChart = reactive({ date: '', sites: [], upload_total: 0, download_total: 0 })
function formatGB(bytes) {
  const n = Number(bytes) || 0
  const gb = n / (1024 ** 3)
  if (gb >= 1) return gb.toFixed(2) + ' GB'
  return (n / (1024 ** 2)).toFixed(1) + ' MB'
}
const siteRows = computed(() => [...(siteChart.sites || [])].sort((a, b) => ((b.upload || 0) + (b.download || 0)) - ((a.upload || 0) + (a.download || 0))))
const maxSiteTraffic = computed(() => Math.max(1, ...siteRows.value.map(s => Math.max(s.upload || 0, s.download || 0))))
function barWidth(value) {
  return `${Math.max(4, Math.round(((Number(value) || 0) / maxSiteTraffic.value) * 100))}%`
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

// 手动触发按钮分组
const actionGroups = [
  {
    group: '汇报中心',
    icon: 'mdi-newspaper-variant-outline',
    actions: [
      { path: 'run_daily_report', label: '立即推送每日汇报', desc: '手动发送一份汇报到通知渠道' },
    ]
  },
  {
    group: '订阅与站点',
    icon: 'mdi-bell-ring-outline',
    actions: [
      { path: 'run_subscribe_reminder', label: '推送订阅追新', desc: '手动推送一次今日订阅追新' },
      { path: 'run_site_stat', label: '刷新站点数据', desc: '重新汇总站点上传/下载增量' },
    ]
  },
  {
    group: '下载与媒体',
    icon: 'mdi-download-network-outline',
    actions: [
      { path: 'run_downloader_tag', label: '按站点打标签', desc: '为下载器种子补打站点标签' },
    ]
  },
  {
    group: '系统维护',
    icon: 'mdi-cog-outline',
    actions: [
      { path: 'run_backup', label: '执行备份', desc: '立即执行一次配置备份' },
      { path: 'run_log_clean', label: '清理日志', desc: '立即清理插件日志（按保留行数）' },
      { path: 'run_mp_update', label: '检查MP更新', desc: '检查 MoviePilot 后端/前端更新' },
      { path: 'run_market_update', label: '检查插件库更新', desc: '检查插件库及已安装插件更新' },
      { path: 'run_health_check', label: '执行健康巡查', desc: '手动执行一次系统健康巡查' },
      { path: 'run_seed_clean', label: '自动删种', desc: '按规则自动暂停/删除种子' },
    ]
  }
]

onMounted(() => { loadDashboard(); loadSiteChart(); loadDownloaderOverview() })
</script>

<template>
  <div class="agentops-dashboard">
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
      <VAlert v-if="error" type="error" variant="tonal" class="mb-3" :text="error" />

      <!-- 状态总览 -->
      <VCard variant="tonal" color="primary" class="overview-strip">
        <div class="overview-item">
          <VIcon icon="mdi-shield-check-outline" :color="overallColor" size="20" />
          <span>状态</span>
          <strong>{{ overallText }}</strong>
        </div>
        <div class="overview-item">
          <VIcon icon="mdi-format-list-checks" color="primary" size="20" />
          <span>任务</span>
          <strong>{{ data.task_on }} / {{ data.task_total }}</strong>
        </div>
        <div class="overview-item">
          <VIcon :icon="data.task_failed > 0 ? 'mdi-alert-circle-outline' : 'mdi-check-circle-outline'" :color="data.task_failed > 0 ? 'error' : 'success'" size="20" />
          <span>异常</span>
          <strong>{{ data.task_failed }}</strong>
        </div>
        <div class="overview-summary">{{ data.summary }}</div>
      </VCard>

      <!-- 站点数据统计 + 手动触发：左右各一个 -->
      <VRow dense class="mt-2">
        <VCol cols="12" lg="8">
          <VCard variant="outlined" class="rounded-lg h-100">
            <VCardTitle class="compact-card-title">
              <VIcon icon="mdi-chart-line" color="primary" class="me-2" />站点数据统计
              <VSpacer />
              <VBtn size="x-small" variant="tonal" color="primary" prepend-icon="mdi-refresh"
                :loading="actionRunning === 'run_site_stat'" @click="runAction('run_site_stat', '刷新站点数据')">
                刷新
              </VBtn>
            </VCardTitle>
            <VDivider />
            <VCardText class="compact-card-text">
              <div class="site-summary">
                <div class="site-summary-item">
                  <VIcon icon="mdi-upload-network-outline" color="success" size="20" />
                  <span>今日上传</span>
                  <strong>{{ formatGB(siteChart.upload_total) }}</strong>
                </div>
                <div class="site-summary-item">
                  <VIcon icon="mdi-download-network-outline" color="info" size="20" />
                  <span>今日下载</span>
                  <strong>{{ formatGB(siteChart.download_total) }}</strong>
                </div>
                <div class="site-summary-item">
                  <VIcon icon="mdi-calendar-blank-outline" color="primary" size="20" />
                  <span>统计日期</span>
                  <strong>{{ siteChart.date || '—' }}</strong>
                </div>
              </div>

              <div v-if="hasSiteChart" class="site-table mt-3">
                <div v-for="site in siteRows" :key="site.name" class="site-row">
                  <div class="site-name">{{ site.name }}</div>
                  <div class="site-bars">
                    <div class="site-metric">
                      <span class="site-metric-label">↑ {{ formatGB(site.upload) }}</span>
                      <span class="site-bar site-bar-up"><i :style="{ width: barWidth(site.upload) }"></i></span>
                    </div>
                    <div class="site-metric">
                      <span class="site-metric-label">↓ {{ formatGB(site.download) }}</span>
                      <span class="site-bar site-bar-down"><i :style="{ width: barWidth(site.download) }"></i></span>
                    </div>
                  </div>
                </div>
              </div>
              <div v-else class="site-empty">
                <VIcon icon="mdi-chart-line-variant" size="24" color="primary" />
                <div>
                  <div class="font-weight-medium">暂无今日站点增量</div>
                  <div class="text-caption text-medium-emphasis">可手动刷新查看最新上传/下载增量。</div>
                </div>
              </div>
            </VCardText>
          </VCard>
        </VCol>

        <!-- 手动触发：模块化放在站点数据右边 -->
        <VCol cols="12" lg="4">
          <VCard variant="outlined" class="rounded-lg h-100">
            <VCardTitle class="compact-card-title">
              <VIcon icon="mdi-play-circle-outline" color="primary" class="me-2" />手动触发
            </VCardTitle>
            <VDivider />
            <VCardText class="compact-card-text">
              <div v-for="grp in actionGroups" :key="grp.group" class="action-group">
                <div class="action-group-title">
                  <VIcon :icon="grp.icon" size="16" color="primary" />
                  <span>{{ grp.group }}</span>
                </div>
                <div class="action-buttons">
                  <VBtn
                    v-for="action in grp.actions"
                    :key="action.path"
                    size="x-small"
                    variant="outlined"
                    color="primary"
                    density="comfortable"
                    :loading="actionRunning === action.path"
                    @click="runAction(action.path, action.label)"
                    class="text-none"
                  >
                    {{ action.label }}
                  </VBtn>
                </div>
              </div>
              <VAlert v-if="actionMessage" type="info" variant="tonal" density="compact" class="mt-3" :text="actionMessage" />
            </VCardText>
          </VCard>
        </VCol>
      </VRow>

      <!-- 下载器活动种子 -->
      <VCard v-if="downloaders.length" variant="outlined" class="rounded-lg mt-2">
        <VCardTitle class="compact-card-title">
          <VIcon icon="mdi-download-network-outline" color="primary" class="me-2" />下载器活动种子
        </VCardTitle>
        <VDivider />
        <VList class="bg-transparent py-0" density="compact">
          <template v-for="(d, i) in downloaders" :key="d.name">
            <VListItem class="py-1">
              <VListItemTitle class="font-weight-medium">{{ d.name }}</VListItemTitle>
              <VListItemSubtitle class="mt-1">下载中 {{ d.count }} 个｜↓ {{ formatGB(d.dl_speed) }}/s　↑ {{ formatGB(d.up_speed) }}/s</VListItemSubtitle>
            </VListItem>
            <VDivider v-if="i < downloaders.length - 1" />
          </template>
        </VList>
      </VCard>

      <!-- 模块运行概览 + 最近健康巡查：横向并排 -->
      <VRow dense class="mt-2">
        <VCol cols="12" md="6">
          <VCard variant="outlined" class="rounded-lg h-100">
            <VCardTitle class="compact-card-title">
              <VIcon icon="mdi-timeline-clock-outline" color="primary" class="me-2" />模块运行概览
            </VCardTitle>
            <VDivider />
            <VSkeletonLoader v-if="loading" type="list-item-avatar-three-line@3" />
            <VList v-else class="bg-transparent py-0 task-list" density="compact">
              <template v-for="(task, i) in data.tasks" :key="task.key">
                <VListItem class="py-1">
                  <template #prepend>
                    <VAvatar size="30" variant="tonal" :color="task.enabled ? task.color : 'default'">
                      <VIcon :icon="task.icon" size="17" />
                    </VAvatar>
                  </template>
                  <VListItemTitle class="font-weight-medium text-body-2">{{ task.name }}</VListItemTitle>
                  <VListItemSubtitle class="task-subtitle">
                    最近 {{ task.last_time || '—' }}｜下次 {{ task.next }}｜{{ task.last_summary }}
                  </VListItemSubtitle>
                  <template #append>
                    <div class="d-flex align-center ga-2">
                      <VChip size="x-small" variant="tonal" :color="task.enabled ? 'success' : 'default'">{{ task.enabled ? 'ON' : 'OFF' }}</VChip>
                      <VChip size="x-small" variant="tonal" :color="task.color">{{ task.state }}</VChip>
                    </div>
                  </template>
                </VListItem>
                <VDivider v-if="i < data.tasks.length - 1" />
              </template>
            </VList>
          </VCard>
        </VCol>

        <VCol cols="12" md="6">
          <VCard variant="outlined" class="rounded-lg h-100">
            <VCardTitle class="compact-card-title">
              <VIcon icon="mdi-heart-pulse" color="primary" class="me-2" />最近健康巡查
              <VSpacer />
              <VChip size="x-small" variant="tonal" :color="healthColor">{{ healthText }}</VChip>
            </VCardTitle>
            <VDivider />
            <VCardText class="compact-card-text">
              <div v-if="data.health.time" class="text-caption text-medium-emphasis mb-2">巡查时间：{{ data.health.time }}</div>
              <pre v-if="data.health.output" class="health-output">{{ data.health.output }}</pre>
              <div v-else class="text-medium-emphasis text-body-2">尚无健康巡查记录，可在设置页手动触发或等待每日汇报自动执行。</div>
            </VCardText>
          </VCard>
        </VCol>
      </VRow>
    </div>
  </div>
</template>

<style scoped>
.agentops-toolbar { position: sticky; top: 0; z-index: 10; background: rgb(var(--v-theme-surface)); }
.agentops-body {
  padding: 8px;
}
.agentops-dashboard :deep(.v-card) { border-radius: 8px; }
.agentops-dashboard :deep(.v-row) { margin: -4px; }
.agentops-dashboard :deep(.v-col) { padding: 4px; }
.compact-card-title {
  display: flex;
  align-items: center;
  min-height: 38px;
  padding: 7px 10px;
  font-size: 14px;
  font-weight: 650;
  line-height: 1.2;
}
.compact-card-text {
  padding: 8px 10px;
}
.overview-strip {
  display: grid;
  grid-template-columns: repeat(3, minmax(96px, 150px)) minmax(0, 1fr);
  align-items: center;
  gap: 6px;
  min-height: 48px;
  padding: 6px 10px;
}
.overview-item {
  display: flex;
  align-items: center;
  gap: 6px;
  min-width: 0;
}
.overview-item span {
  color: rgba(var(--v-theme-on-surface), 0.62);
  font-size: 12px;
}
.overview-item strong {
  font-size: 14px;
  white-space: nowrap;
}
.overview-summary {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: rgba(var(--v-theme-on-surface), 0.72);
  font-size: 12px;
}
.site-summary {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 6px;
}
.site-summary-item {
  display: flex;
  align-items: center;
  gap: 6px;
  min-height: 34px;
  padding: 5px 8px;
  border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity));
  border-radius: 8px;
  background: rgba(var(--v-theme-on-surface), 0.025);
}
.site-summary-item span {
  flex: 1 1 auto;
  min-width: 0;
  color: rgba(var(--v-theme-on-surface), 0.64);
  font-size: 12px;
}
.site-summary-item strong {
  font-size: 12px;
  white-space: nowrap;
}
.site-table {
  display: grid;
  gap: 4px;
}
.site-row {
  display: grid;
  grid-template-columns: minmax(84px, 150px) minmax(0, 1fr);
  gap: 10px;
  align-items: center;
  padding: 5px 0;
  border-top: 1px solid rgba(var(--v-border-color), 0.5);
}
.site-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 600;
}
.site-bars {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}
.site-metric {
  display: grid;
  gap: 3px;
}
.site-metric-label {
  color: rgba(var(--v-theme-on-surface), 0.68);
  font-size: 12px;
}
.site-bar {
  display: block;
  height: 6px;
  overflow: hidden;
  border-radius: 999px;
  background: rgba(var(--v-theme-on-surface), 0.08);
}
.site-bar i {
  display: block;
  height: 100%;
  border-radius: inherit;
}
.site-bar-up i { background: rgb(var(--v-theme-success)); }
.site-bar-down i { background: rgb(var(--v-theme-info)); }
.site-empty {
  display: flex;
  align-items: center;
  gap: 8px;
  min-height: 54px;
  margin-top: 8px;
  padding: 8px 10px;
  border: 1px dashed rgba(var(--v-theme-primary), 0.42);
  border-radius: 8px;
  background: rgba(var(--v-theme-primary), 0.04);
}
.action-group {
  display: grid;
  gap: 6px;
  padding: 6px 0;
  border-bottom: 1px solid rgba(var(--v-border-color), 0.38);
}
.action-group:first-child {
  padding-top: 0;
}
.action-group:last-of-type {
  border-bottom: 0;
  padding-bottom: 0;
}
.action-group-title {
  display: flex;
  align-items: center;
  gap: 6px;
  color: rgba(var(--v-theme-on-surface), 0.72);
  font-size: 12px;
  font-weight: 650;
}
.action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.task-list {
  max-height: 220px;
  overflow: auto;
}
.task-subtitle {
  display: -webkit-box;
  overflow: hidden;
  -webkit-line-clamp: 1;
  -webkit-box-orient: vertical;
  font-size: 12px;
  line-height: 1.4;
}
.health-output {
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 12px;
  line-height: 1.45;
  margin: 0;
  max-height: 220px;
  overflow: auto;
  font-family: 'JetBrains Mono', Consolas, Menlo, monospace;
  color: rgb(var(--v-theme-on-surface));
  opacity: .85;
}
@media (max-width: 760px) {
  .overview-strip {
    grid-template-columns: 1fr;
  }
  .site-summary,
  .site-bars {
    grid-template-columns: 1fr;
  }
  .site-row {
    grid-template-columns: 1fr;
    gap: 6px;
  }
}
</style>
