<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { getPluginApi, postPluginApi } from './api'
import SiteStatsWidget from './dashboard/SiteStatsWidget.vue'
import ActionsWidget from './dashboard/ActionsWidget.vue'

const props = defineProps({
  api: { type: [Object, Function], default: null },
  config: { type: Object, default: () => ({}) },
  allowRefresh: { type: Boolean, default: true },
})

const emit = defineEmits(['update:refreshStatus', 'loaded'])

const loading = ref(false)
const error = ref('')
const loadedOnce = ref(false)
const actionRunning = ref('')
const actionMessage = ref('')
const actionOk = ref(true)

const siteChart = reactive({
  date: '',
  basis: 'today',
  sites: [],
  upload_total: 0,
  download_total: 0,
})

const actionItems = [
  { path: 'run_site_stat', label: '站点统计', desc: '刷新站点增量', icon: 'mdi-chart-pie', tone: 'blue' },
  { path: 'run_daily_report', label: '每日汇报', desc: '发送运维摘要', icon: 'mdi-send-clock-outline', tone: 'green' },
  { path: 'run_subscribe_reminder', label: '订阅追新', desc: '推送今日追新', icon: 'mdi-bell-badge-outline', tone: 'cyan' },
  { path: 'run_health_check', label: '健康巡查', desc: '检查关键状态', icon: 'mdi-heart-pulse', tone: 'violet' },
]

const componentKey = computed(() => props.config?.attrs?.component || props.config?.key || 'site')
const componentMap = {
  site: SiteStatsWidget,
  actions: ActionsWidget,
}
const activeComponent = computed(() => componentMap[componentKey.value] || SiteStatsWidget)

const sitePieColors = [
  { color: 'rgba(var(--v-theme-success), 0.94)', glow: 'rgba(var(--v-theme-success), 0.28)' },
  { color: 'rgba(var(--v-theme-info), 0.90)', glow: 'rgba(var(--v-theme-info), 0.26)' },
  { color: 'rgba(var(--v-theme-warning), 0.88)', glow: 'rgba(var(--v-theme-warning), 0.24)' },
  { color: 'rgba(var(--v-theme-primary), 0.88)', glow: 'rgba(var(--v-theme-primary), 0.24)' },
  { color: 'rgba(var(--v-theme-error), 0.84)', glow: 'rgba(var(--v-theme-error), 0.22)' },
]

const siteRows = computed(() => [...(siteChart.sites || [])].sort((a, b) => {
  const av = (Number(a.upload) || 0) + (Number(a.download) || 0)
  const bv = (Number(b.upload) || 0) + (Number(b.download) || 0)
  return bv - av
}))

const siteTrafficTotal = computed(() => siteRows.value.reduce((sum, site) => {
  return sum + (Number(site.upload) || 0) + (Number(site.download) || 0)
}, 0))

const siteDateLabel = computed(() => {
  if (!siteChart.date) return '等待统计'
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
      background: 'conic-gradient(rgba(var(--v-theme-on-surface), 0.16) 0 82deg, rgba(var(--v-theme-on-surface), 0.055) 82deg 360deg)',
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

function formatBytes(bytes) {
  const n = Number(bytes) || 0
  const gb = n / (1024 ** 3)
  if (gb >= 1) return `${gb.toFixed(2)} GB`
  return `${(n / (1024 ** 2)).toFixed(1)} MB`
}

async function loadSiteChart() {
  if (!props.api) return
  loading.value = true
  error.value = ''
  emit('update:refreshStatus', true)
  try {
    const site = await getPluginApi(props.api, 'site_stat_chart')
    Object.assign(siteChart, site || {})
  } catch (err) {
    error.value = err?.message || '站点数据加载失败'
  } finally {
    loading.value = false
    emit('update:refreshStatus', false)
    if (!loadedOnce.value) {
      loadedOnce.value = true
      emit('loaded')
    }
  }
}

async function runAction(action) {
  if (!props.api || actionRunning.value) return
  actionRunning.value = action.path
  actionMessage.value = ''
  actionOk.value = true
  try {
    const res = await postPluginApi(props.api, action.path)
    const ok = !res || res.code === 0 || res.code === undefined
    actionOk.value = ok
    actionMessage.value = (res && res.msg) || `${action.label}已${ok ? '完成' : '失败'}`
    if (ok && action.path === 'run_site_stat') await loadSiteChart()
  } catch (err) {
    actionOk.value = false
    actionMessage.value = err?.message || `${action.label}失败`
  } finally {
    actionRunning.value = ''
    window.setTimeout(() => { actionMessage.value = '' }, 5000)
  }
}

watch(componentKey, () => {
  if (componentKey.value === 'site') loadSiteChart()
})
onMounted(loadSiteChart)
</script>

<template>
  <div class="aoa-dashboard-widget">
    <component
      :is="activeComponent"
      :loading="loading"
      :error="error"
      :site-chart="siteChart"
      :site-rows="siteRows"
      :site-table-rows="siteTableRows"
      :site-traffic-total="siteTrafficTotal"
      :site-date-label="siteDateLabel"
      :site-date-note="siteDateNote"
      :site-pie-style="sitePieStyle"
      :has-site-chart="hasSiteChart"
      :format-bytes="formatBytes"
      :site-percent="sitePercent"
      :actions="actionItems"
      :action-running="actionRunning"
      :action-message="actionMessage"
      :action-ok="actionOk"
      :allow-refresh="allowRefresh"
      @refresh="loadSiteChart"
      @run-action="runAction"
    />
  </div>
</template>

<style scoped>
.aoa-dashboard-widget {
  width: 100%;
  height: 100%;
  min-height: 100%;
  color: rgba(var(--v-theme-on-surface), 0.92);
}
</style>
