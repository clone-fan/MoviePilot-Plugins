import { computed, reactive, ref } from 'vue'
import { getPluginApiEnvelope } from '../../../shared/api.js'
import { usePanelActionRunner } from '../../../shared/composables/useActionRunner.js'
import { useSiteChart } from '../../../shared/composables/useSiteChart.js'
import { formatGB } from '../../../shared/utils/format.js'
import { signalIcons } from '../../../shared/icons.js'

export const mpFreeQuickActions = [
  { key: 'subscribe', label: '订阅追新', icon: signalIcons.rss, path: 'run_subscribe_reminder' },
  { key: 'transfer', label: '今日入库', icon: signalIcons.calendarToday, path: 'run_today_transfer' },
  { key: 'site_stat', label: '站点统计', icon: signalIcons.chartPie, path: 'run_site_stat' },
  { key: 'backup', label: '配置备份', icon: signalIcons.database, path: 'run_backup' },
  { key: 'log_clean', label: '日志清理', icon: signalIcons.broom, path: 'run_log_clean' },
  { key: 'health', label: '健康巡查', icon: signalIcons.heartPulse, path: 'run_health_check' },
  { key: 'mp_update', label: 'MP 更新', icon: signalIcons.refresh, path: 'run_mp_update' },
  { key: 'plugin_update', label: '插件更新', icon: signalIcons.cloudUpload, path: 'run_market_update' },
]

export function useDashboardFreeData(api) {
  const loading = ref(false)
  const error = ref('')
  const dashboard = reactive({
    enabled: true,
    tasks: [],
    task_total: 0,
    task_on: 0,
    task_failed: 0,
    health: { success: true, output: '' },
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
  } = useSiteChart(api)

  const actionRunner = usePanelActionRunner({
    api: () => api,
    onSuccess: async ({ action }) => {
      if (action?.path === 'run_site_stat') await loadSiteChart()
    },
  })

  const trafficSummaryRows = computed(() => [
    { label: '上传增量', value: formatGB(siteChart.upload_total || 0), icon: signalIcons.arrowUp },
    { label: '下载增量', value: formatGB(siteChart.download_total || 0), icon: signalIcons.arrowDown },
    { label: '统计时间', value: siteChart.date || '等待统计', icon: signalIcons.calendarToday },
  ])

  const siteCards = computed(() => {
    const siteIcons = [signalIcons.yinYang, signalIcons.eye, signalIcons.chartPie, signalIcons.leaf, signalIcons.database]
    const siteColors = ['#34C759', '#60A5FA', '#FFB020', '#AF52DE', '#64D2FF']
    return siteRows.value.map((site, index) => {
      const traffic = Number(site.upload || 0) + Number(site.download || 0)
      return {
        name: site.name || `站点 ${index + 1}`,
        icon: siteIcons[index % siteIcons.length],
        iconColor: siteColors[index % siteColors.length],
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
      return {
        key: task?.key || task?.service_id || task?.id || task?.name,
        name: task?.name || '注册任务',
        enabled: dashboard.enabled !== false && task?.effective_enabled === true,
        state: task?.state || '',
        schedule: rawSchedule.startsWith('下次') ? rawSchedule : `下次 ${rawSchedule}`,
      }
    }).filter(task => task.enabled)
  })

  const donutValue = computed(() => String(sitePieSegments.value.length || siteRows.value.length || 0))
  const dateNote = computed(() => siteDateNote.value || '今天 00:00 起')

  async function loadDashboard() {
    if (!api) return
    loading.value = true
    error.value = ''
    try {
      const response = await getPluginApiEnvelope(api, 'dashboard')
      const payload = response?.data || response
      if (payload && typeof payload === 'object') {
        Object.assign(dashboard, {
          enabled: payload.enabled !== false,
          tasks: Array.isArray(payload.tasks) ? payload.tasks : [],
          task_total: Number(payload.task_total || payload.taskTotal || payload.tasks?.length || 0),
          task_on: Number(payload.task_on || payload.taskOn || payload.tasks?.filter?.(task => task?.state !== false)?.length || 0),
          task_failed: Number(payload.task_failed || payload.taskFailed || 0),
          health: payload.health || dashboard.health,
        })
      }
      await loadSiteChart()
    } catch (err) {
      error.value = err?.message || '仪表盘数据加载失败'
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    error,
    dashboard,
    siteChart,
    siteCards,
    sitePieSegments,
    sitePieStyle,
    siteTrafficTotal,
    trafficSummaryRows,
    runtimeTasks,
    donutValue,
    dateNote,
    quickActions: mpFreeQuickActions,
    actionRunner,
    loadDashboard,
  }
}
