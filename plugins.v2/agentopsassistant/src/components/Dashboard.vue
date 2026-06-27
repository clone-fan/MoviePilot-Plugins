<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { actionMessageFromResponse, getPluginApi, postPluginApi } from './api'
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
  { path: 'run_site_stat', component: 'site_stat', label: '站点统计', desc: '刷新站点增量', icon: 'mdi-chart-pie' },
  { path: 'create_tg_console_card', component: '', label: '立即建卡', desc: '创建融合汇报卡', icon: 'mdi-card-plus-outline' },
  { path: 'run_daily_report', component: 'daily_report', label: '立即刷新', desc: '刷新融合汇报', icon: 'mdi-refresh' },
  { path: 'run_subscribe_reminder', component: 'subscribe_reminder', label: '订阅追新', desc: '推送今日追新', icon: 'mdi-bell-badge-outline' },
  { path: 'run_health_check', component: 'health_check', label: '健康巡查', desc: '检查关键状态', icon: 'mdi-heart-pulse' },
]

const componentKey = computed(() => props.config?.attrs?.component || props.config?.key || 'site')
const componentEnabledStates = computed(() => props.config?.attrs?.components || props.config?.components || {})
const componentMap = {
  site: SiteStatsWidget,
  actions: ActionsWidget,
}
const activeComponent = computed(() => componentMap[componentKey.value] || SiteStatsWidget)
function actionComponentEnabled(action) {
  const states = componentEnabledStates.value || {}
  if (!action?.component || !(action.component in states)) return true
  return !!states[action.component]
}
const widgetActions = computed(() => actionItems.map(action => {
  const enabled = actionComponentEnabled(action)
  return {
    ...action,
    disabled: !enabled,
    reason: enabled ? '' : '组件未启用，动作已暂停',
  }
}))

const sitePieColors = [
  { color: 'rgba(88, 204, 118, 0.95)', glow: 'rgba(88, 204, 118, 0.30)' },
  { color: 'rgba(45, 212, 191, 0.92)', glow: 'rgba(45, 212, 191, 0.28)' },
  { color: 'rgba(96, 165, 250, 0.92)', glow: 'rgba(96, 165, 250, 0.28)' },
  { color: 'rgba(251, 191, 36, 0.90)', glow: 'rgba(251, 191, 36, 0.26)' },
  { color: 'rgba(248, 113, 113, 0.88)', glow: 'rgba(248, 113, 113, 0.24)' },
  { color: 'rgba(167, 139, 250, 0.90)', glow: 'rgba(167, 139, 250, 0.25)' },
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
  if (action.disabled) {
    actionOk.value = false
    actionMessage.value = action.reason || '组件未启用，动作已暂停'
    window.setTimeout(() => { actionMessage.value = '' }, 5000)
    return
  }
  actionRunning.value = action.path
  actionMessage.value = ''
  actionOk.value = true
  try {
    const res = await postPluginApi(props.api, action.path)
    const ok = !!res && res.code === 0
    actionOk.value = ok
    actionMessage.value = actionMessageFromResponse(res, action.label)
    if (ok && action.path === 'run_site_stat') await loadSiteChart()
  } catch (err) {
    actionOk.value = false
    actionMessage.value = actionMessageFromResponse({ code: 1, msg: err?.message }, action.label)
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
      :actions="widgetActions"
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
/* Dashboard.vue 是 MP 仪表盘自由组件的外壳：
 * - 外框跟随 MP 官方 v-card token，子 widget 内部再叠 on-surface 透白做液态玻璃层次
 * - 透明主题下直连 --transparent-opacity / --transparent-blur
 */
.aoa-dashboard-widget {
  --aoa-dashboard-radius: var(--app-surface-radius, 12px);
  --aoa-dashboard-border: var(--app-surface-border, 1px solid rgba(var(--v-border-color), var(--v-border-opacity, 0.12)));
  --aoa-dashboard-shadow: var(--app-surface-shadow, none);
  width: 100%;
  height: 100%;
  min-height: 100%;
  border-radius: var(--aoa-dashboard-radius);
  color: rgba(var(--v-theme-on-surface), 0.92);
}

:global(html[data-theme="transparent"]) .aoa-dashboard-widget {
  /* 透明主题下子 widget 自己处理 backdrop-filter，这里只透传 token 给后代 */
  --aoa-dashboard-opacity: var(--transparent-opacity);
  --aoa-dashboard-blur: var(--transparent-blur);
}
</style>
