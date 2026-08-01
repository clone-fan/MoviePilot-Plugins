import { reactive, computed } from 'vue'
import { getPluginApiEnvelope } from '../api'
import { sitePercent as fmtSitePercent, sitePieColors } from '../utils/format'

// 站点统计图表状态 — 跨 Dashboard.vue / Page.vue 共享，禁止各 vue 里各写一份
// 入参：api(MP 插件 API 句柄)
export function useSiteChart(api) {
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
    return siteChart.basis === 'latest' ? '最近快照' : '今天 00:00 起'
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
    return fmtSitePercent(value, siteTrafficTotal.value)
  }

  async function loadSiteChart() {
    if (!api) return
    try {
      const res = await getPluginApiEnvelope(api, 'site_stat_chart')
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

  return {
    siteChart,
    siteRows,
    siteTrafficTotal,
    siteDateLabel,
    siteDateNote,
    sitePieSegments,
    sitePieStyle,
    siteTableRows,
    hasSiteChart,
    siteEmptyTitle,
    siteEmptyDesc,
    sitePercent,
    loadSiteChart,
  }
}
