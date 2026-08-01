<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { getPluginApiEnvelope } from '../../../shared/api.js'
import { useSiteChart } from '../../../shared/composables/useSiteChart.js'
import { usePanelActionRunner as useActionRunner } from '../../../shared/composables/useActionRunner.js'
import { useSignalTheme } from '../../../shared/composables/useSignalTheme.js'
import { formatGB } from '../../../shared/utils/format.js'
import '../../../shared/styles/tokens.css'
import '../../../shared/styles/themes.css'
import '../styles/dashboard.css'
import DashboardShell from './DashboardShell.vue'
import DashboardToolbar from './DashboardToolbar.vue'
import KpiStrip from './KpiStrip.vue'
import SiteDataPanel from '../../../shared/SiteDataPanel.vue'
import TaskRuntimePanel from './TaskRuntimePanel.vue'
import QuickActionsBand from '../../../shared/QuickActionsBand.vue'
import FusionMiniCard from './FusionMiniCard.vue'
import { signalIcons } from '../../../shared/icons.js'

const props = defineProps({
  api: { type: [Object, Function], default: null },
  config: { type: Object, default: () => ({}) },
  allowRefresh: { type: Boolean, default: true },
  surface: { type: String, default: 'dialog' },
  pluginId: { type: String, default: 'Signal' },
})

const emit = defineEmits(['update:refreshStatus', 'loaded', 'close', 'switch'])

const { themeName, rootThemeClass } = useSignalTheme()
const loading = ref(false)
const error = ref('')
const localActionMessage = ref('')
const localActionOk = ref(true)
let localActionTimer = 0

const dashboard = reactive({
  enabled: true,
  summary: '',
  tasks: [],
  task_total: 0,
  task_on: 0,
  task_failed: 0,
  health: { success: true, output: '' },
})

const fusionCard = reactive({
  id: '',
  updatedAt: '',
  isBuilt: false,
})

const themeClass = computed(() => {
  return `signal-dashboard-shell--${themeName.value} ${rootThemeClass.value}`
})

const {
  siteChart,
  siteRows,
  siteTrafficTotal,
  siteDateNote,
  sitePieSegments,
  sitePieStyle,
  sitePercent,
  loadSiteChart,
} = useSiteChart(props.api)

const quickActions = [
  { key: 'subscribe', label: '订阅追新', icon: signalIcons.rss, path: 'run_subscribe_reminder' },
  { key: 'transfer', label: '今日入库', icon: signalIcons.calendarToday, path: 'run_today_transfer' },
  { key: 'site_stat', label: '站点统计', icon: signalIcons.chartPie, path: 'run_site_stat' },
  { key: 'backup', label: '配置备份', icon: signalIcons.database, path: 'run_backup' },
  { key: 'log_clean', label: '日志清理', icon: signalIcons.broom, path: 'run_log_clean' },
  { key: 'health', label: '健康巡查', icon: signalIcons.heartPulse, path: 'run_health_check' },
  { key: 'mp_update', label: 'MP 更新', icon: signalIcons.refresh, path: 'run_mp_update' },
  { key: 'plugin_update', label: '插件更新', icon: signalIcons.cloudUpload, path: 'run_market_update' },
]

const actionRunner = useActionRunner({
  api: () => props.api,
  onSuccess: async ({ action }) => {
    if (action?.path === 'run_site_stat') await loadSiteChart()
    if (action?.path === 'create_tg_console_card' || action?.path === 'run_daily_report') await loadFusionCard()
  },
})

const healthOk = computed(() => dashboard.health?.success !== false && Number(dashboard.task_failed || 0) === 0)
const enabledCount = computed(() => runtimeTasks.value.filter(task => task.enabled).length)
const totalCount = computed(() => Number(dashboard.task_total || 0) || Math.max(enabledCount.value, runtimeTasks.value.length))
const trafficLabel = computed(() => formatGB(siteTrafficTotal.value || siteChart.upload_total + siteChart.download_total))
const trafficParts = computed(() => {
  const [value, unit = 'GB'] = trafficLabel.value.split(' ')
  return { value: value || '122.5', unit }
})

const kpiItems = computed(() => [
  {
    key: 'system',
    label: '系统状态',
    icon: signalIcons.checkCircle,
    iconColor: dashboard.enabled !== false ? '#34C759' : '#8E8E93',
    value: dashboard.enabled !== false ? '运行平稳' : '插件已停用',
    detail: dashboard.enabled !== false
      ? (healthOk.value ? '当前任务未发现异常' : `当前有 ${Number(dashboard.task_failed || 0)} 个异常组件`)
      : '开启插件总开关后恢复运行',
  },
  {
    key: 'runtime',
    label: '运行状态',
    dot: dashboard.enabled !== false,
    pulse: dashboard.enabled !== false,
    value: dashboard.enabled !== false ? '正常' : '停用',
    detail: `异常组件 ${Number(dashboard.task_failed || 0)}`,
  },
  {
    key: 'enabled',
    label: '启用组件',
    icon: signalIcons.checkCircle,
    iconColor: '#8E8E93',
    value: String(enabledCount.value),
    total: String(totalCount.value),
    large: true,
    detail: dashboard.enabled !== false ? '组件运行正常' : '组件当前均未运行',
  },
  {
    key: 'traffic',
    label: '站点流量',
    icon: signalIcons.chartPie,
    iconColor: '#60A5FA',
    value: trafficParts.value.value,
    unit: trafficParts.value.unit,
    large: true,
    detail: '任务调度与健康巡查',
  },
])

const trafficSummaryRows = computed(() => [
  { label: '上传增量', value: formatGB(siteChart.upload_total || 0), icon: signalIcons.arrowUp },
  { label: '下载增量', value: formatGB(siteChart.download_total || 0), icon: signalIcons.arrowDown },
  { label: '统计时间', value: siteChart.date || '2026-07-04', icon: signalIcons.calendarToday },
])

const siteCards = computed(() => {
  const siteIcons = [signalIcons.yinYang, signalIcons.eye, signalIcons.chartPie, signalIcons.leaf, signalIcons.database]
  const siteColors = ['#34C759', '#60A5FA', '#FFB020', '#AF52DE', '#64D2FF']
  const rows = siteRows.value
  return rows.map((site, siteIndex) => {
    const traffic = Number(site.upload || 0) + Number(site.download || 0)
    return {
      name: site.name || (siteIndex === 0 ? '馒头' : '观众'),
      icon: siteIcons[siteIndex % siteIcons.length],
      iconColor: siteColors[siteIndex % siteColors.length],
      percent: sitePercent(traffic),
      upload: formatGB(site.upload || 0),
      download: formatGB(site.download || 0),
    }
  })
})

const runtimeTasks = computed(() => {
  const sourceTasks = Array.isArray(dashboard.tasks) ? dashboard.tasks : []
  return sourceTasks.map((task) => {
    const rawSchedule = String(task?.next_run || task?.schedule || task?.next || '已注册').trim()
    const schedule = dashboard.enabled === false
      ? '插件已停用'
      : (rawSchedule.startsWith('下次') ? rawSchedule : `下次 ${rawSchedule}`)
    return {
      key: task?.key || task?.service_id || task?.name,
      name: task?.name || '注册任务',
      enabled: dashboard.enabled !== false && task?.effective_enabled === true,
      state: task?.state || '',
      schedule,
    }
  }).filter(task => task.enabled)
})

const donutValue = computed(() => String(sitePieSegments.value.length || siteRows.value.length || 0))
const actionHint = computed(() => {
  if (!actionRunner.actionRunning.value) return ''
  return `${actionRunner.runningActionLabel.value || '当前动作'}执行中，请稍候。`
})
const actionFeedbackMessage = computed(() => actionHint.value || localActionMessage.value || actionRunner.actionMessage.value)
const actionFeedbackOk = computed(() => {
  if (actionHint.value) return true
  if (localActionMessage.value) return localActionOk.value
  return actionRunner.actionOk.value
})

function showLocalActionMessage(message, ok = true) {
  localActionOk.value = ok
  localActionMessage.value = message
  if (localActionTimer) clearTimeout(localActionTimer)
  localActionTimer = setTimeout(() => {
    localActionMessage.value = ''
    localActionTimer = 0
  }, 4000)
}

async function loadFusionCard() {
  if (dashboard.enabled === false) {
    fusionCard.id = ''
    fusionCard.updatedAt = ''
    fusionCard.isBuilt = false
    return
  }
  if (!props.api) return
  const response = await getPluginApiEnvelope(props.api, 'tg_console_status').catch(() => null)
  const payload = response?.data || response
  if (!payload || typeof payload !== 'object') return
  fusionCard.id = String(payload.id || payload.message_id || fusionCard.id || '')
  fusionCard.updatedAt = String(payload.updated_at || payload.date || fusionCard.updatedAt || '')
  fusionCard.isBuilt = payload.built === true || Number(payload.message_id || 0) > 0 || payload.isBuilt === true
}

async function loadDashboard() {
  if (!props.api) return
  loading.value = true
  error.value = ''
  emit('update:refreshStatus', 'loading')
  try {
    const response = await getPluginApiEnvelope(props.api, 'dashboard')
    const payload = response?.data || response
    if (payload && typeof payload === 'object') {
      Object.assign(dashboard, {
        enabled: payload.enabled !== false,
        summary: payload.summary || '',
        tasks: Array.isArray(payload.tasks) ? payload.tasks : [],
        task_total: Number(payload.task_total || payload.taskTotal || payload.tasks?.length || dashboard.task_total),
        task_on: Number(payload.task_on || payload.taskOn || payload.tasks?.filter?.(task => task?.state !== false)?.length || dashboard.task_on),
        task_failed: Number(payload.task_failed || payload.taskFailed || 0),
        health: payload.health || dashboard.health,
      })
    }
    await Promise.all([loadSiteChart(), loadFusionCard()])
    emit('loaded')
    emit('update:refreshStatus', 'success')
  } catch (err) {
    error.value = err?.message || '仪表盘数据加载失败'
    emit('update:refreshStatus', 'error')
  } finally {
    loading.value = false
  }
}

function handleQuickAction(action) {
  actionRunner.runAction(action)
}

function handleFusionBuild() {
  actionRunner.runAction({ key: 'fusion_build', label: '建卡', path: 'create_tg_console_card' })
}

function handleFusionRefresh() {
  actionRunner.runAction({ key: 'fusion_refresh', label: '刷新融合卡', path: 'run_daily_report' })
}

function switchPluginAppNav(navKey) {
  if (typeof window === 'undefined') return false
  const pluginAppPrefix = `#/plugin-app/${props.pluginId}/`
  if (!window.location.hash.startsWith(pluginAppPrefix)) return false
  window.location.hash = `${pluginAppPrefix}${navKey}`
  return true
}

function openSettings() {
  if (switchPluginAppNav('config')) return
  emit('switch')
}

onMounted(loadDashboard)
</script>

<template>
  <DashboardShell :surface="surface" :theme-class="themeClass">
    <DashboardToolbar :loading="loading" @refresh="loadDashboard" @settings="openSettings" />
    <KpiStrip :items="kpiItems" />
    <div class="signal-core-grid">
      <SiteDataPanel
        :date-note="siteDateNote || '今天 00:00 起'"
        :donut-value="donutValue"
        donut-label="个站点"
        :donut-segments="sitePieSegments"
        :donut-style="sitePieStyle"
        :summary-rows="trafficSummaryRows"
        :sites="siteCards"
      />
      <TaskRuntimePanel :tasks="runtimeTasks" />
    </div>
    <div class="signal-glass-card signal-bottom-row">
      <QuickActionsBand
        :actions="quickActions"
        :running-key="actionRunner.actionRunning.value"
        :feedback-message="actionFeedbackMessage"
        :feedback-ok="actionFeedbackOk"
        @action="handleQuickAction"
      />
      <FusionMiniCard
        :card-id="fusionCard.id"
        :updated-at="fusionCard.updatedAt"
        :is-built="fusionCard.isBuilt"
        :enabled="dashboard.enabled !== false"
        :refreshing="actionRunner.actionRunning.value === 'run_daily_report'"
        :building="actionRunner.actionRunning.value === 'create_tg_console_card'"
        @build="handleFusionBuild"
        @refresh="handleFusionRefresh"
      />
    </div>
    <div v-if="error" class="signal-error">{{ error }}</div>
    <div v-else-if="loading" class="signal-loading">正在刷新仪表盘...</div>
  </DashboardShell>
</template>
