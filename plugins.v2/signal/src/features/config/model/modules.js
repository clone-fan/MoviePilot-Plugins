import { allActionItems } from '../../../shared/actions.js'

export const moduleHosts = Object.freeze({
  FULL_DASHBOARD: 'full-dashboard',
  MP_WIDGET: 'mp-widget',
  CONFIG: 'config',
})

const actionByPath = new Map(allActionItems.map(action => [action.path, action]))

function actionsFor(paths) {
  return paths.map(path => actionByPath.get(path)).filter(Boolean)
}

const full = moduleHosts.FULL_DASHBOARD
const widget = moduleHosts.MP_WIDGET
const config = moduleHosts.CONFIG
const suppressedFullDashboardModuleIds = new Set(['downloader_activity'])

export const dashboardModules = Object.freeze([
  {
    id: 'ops_status',
    title: '',
    navLabel: '状态',
    category: 'control',
    categoryLabel: '控制台',
    order: 5,
    description: '将告警中心与运维总览压缩为同一条顶部状态带，用更直接的图标、数值和重点项呈现当前运行面。',
    icon: 'mdi-view-dashboard-outline',
    card: { subtitle: '', border: false, refresh: 30 },
    component: 'OpsStatusModule',
    hosts: [full],
    dataSources: ['dashboard', 'dashboard.health'],
    actions: [],
    layout: {
      [full]: { area: 'ops-status', density: 'compact-strip', minWidth: 640, minHeight: 128, colSpan: 12, rowSpan: 1, gridColumn: '1 / -1', gridRow: '1' },
    },
  },
  {
    id: 'health_status',
    title: '告警中心',
    navLabel: '告警',
    category: 'control',
    categoryLabel: '控制台',
    order: 10,
    description: '优先展示健康巡查异常、失败任务和处理线索，第一时间告诉用户“现在哪里有问题”。',
    icon: 'mdi-heart-pulse',
    card: { subtitle: '最新异常与处置线索', border: true, refresh: 0 },
    component: 'AlertCenterModule',
    hosts: [widget],
    dataSources: ['dashboard.health'],
    actions: actionsFor(['run_health_check']),
    layout: {
      [widget]: { area: 'health', density: 'widget', minWidth: 280, minHeight: 160, colSpan: 2, rowSpan: 1 },
    },
  },
  {
    id: 'metrics_overview',
    title: '运维总览',
    navLabel: '总览',
    category: 'control',
    categoryLabel: '控制台',
    order: 20,
    description: '用一屏摘要收口插件启用状态、组件覆盖率、异常规模和站点总流量。',
    icon: 'mdi-view-dashboard-outline',
    card: { subtitle: '状态摘要与关键指标', border: true, refresh: 30 },
    component: 'OverviewModule',
    hosts: [widget],
    dataSources: ['dashboard'],
    actions: [],
    layout: {
      [widget]: { area: 'overview', density: 'widget-summary', minWidth: 280, minHeight: 160, colSpan: 2, rowSpan: 1 },
    },
  },
  {
    id: 'quick_actions',
    title: '快捷操作',
    navLabel: '快捷操作',
    category: 'operations',
    categoryLabel: '执行与汇报',
    order: 30,
    description: '把追新、站点、下载器和系统维护收在统一快捷区，降低常用动作路径。',
    icon: 'mdi-refresh',
    card: { subtitle: '横向触发常用运维动作', border: true, refresh: 0 },
    component: 'OperationsActionModule',
    renderers: {
      [full]: 'ActionsWidget',
      [widget]: 'ActionsWidget',
    },
    hosts: [full, widget],
    dataSources: ['dashboard'],
    actions: actionsFor([
      'run_subscribe_reminder',
      'run_today_transfer',
      'run_site_stat',
      'run_backup',
      'run_log_clean',
      'run_health_check',
      'run_mp_update',
      'run_market_update',
    ]),
    layout: {
      [full]: { area: 'commands', density: 'compact', minWidth: 320, minHeight: 132, colSpan: 8, rowSpan: 1, gridColumn: '1 / 3', gridRow: '4' },
      [widget]: { area: 'actions', density: 'widget', minWidth: 280, minHeight: 220, colSpan: 2, rowSpan: 2 },
    },
  },
  {
    id: 'fusion_card',
    title: '融合卡状态',
    navLabel: '融合卡',
    category: 'operations',
    categoryLabel: '执行与汇报',
    order: 35,
    description: '展示 TG 融合卡状态，并集中放置建卡与刷新动作。',
    icon: 'mdi-message-badge-outline',
    card: { subtitle: 'TG 融合通知卡', border: true, refresh: 0 },
    component: 'FusionCardModule',
    hosts: [full],
    dataSources: ['dashboard.tg_console'],
    actions: actionsFor([
      'create_tg_console_card',
      'run_daily_report',
    ]),
    layout: {
      [full]: { area: 'fusion', density: 'compact', minWidth: 280, minHeight: 132, colSpan: 4, rowSpan: 1, gridColumn: '3', gridRow: '4' },
    },
  },
  {
    id: 'site_stats',
    title: '站点数据',
    navLabel: '站点数据',
    category: 'site',
    categoryLabel: '站点与下载',
    order: 40,
    description: '聚合站点上传、下载、占比与快照状态，用更直接的站点数据视角回答“今天跑得怎么样”。',
    icon: 'mdi-chart-pie',
    card: { subtitle: '上传 / 下载 / 占比', border: true, refresh: 0 },
    component: 'SiteOpsModule',
    renderers: {
      [widget]: 'SiteStatsWidget',
    },
    hosts: [full, widget],
    dataSources: ['site_stat_chart'],
    actions: actionsFor(['run_site_stat']),
    layout: {
      [full]: { area: 'site', density: 'comfortable', minWidth: 320, minHeight: 252, colSpan: 8, rowSpan: 2, gridColumn: '1 / 3', gridRow: '2 / 4' },
      [widget]: { area: 'site', density: 'widget', minWidth: 280, minHeight: 220, colSpan: 2, rowSpan: 2 },
    },
  },
  {
    id: 'downloader_activity',
    title: '下载器态势',
    navLabel: '下载器',
    category: 'site',
    categoryLabel: '站点与下载',
    order: 50,
    description: '展示实时任务、上下行速度和跳过语义，避免把“未连接”误读成错误。',
    icon: 'mdi-download-network-outline',
    card: { subtitle: '实时任务与带宽状态', border: true, refresh: 10 },
    component: 'DownloaderOpsModule',
    hosts: [full],
    dataSources: ['downloader_overview'],
    actions: actionsFor(['run_seed_clean']),
    layout: {
      [full]: { area: 'downloaders', density: 'compact', minWidth: 300, minHeight: 156, colSpan: 4, rowSpan: 1, gridColumn: '3', gridRow: '2' },
    },
  },
  {
    id: 'runtime_status',
    title: '任务运行',
    navLabel: '任务',
    category: 'operations',
    categoryLabel: '执行与汇报',
    order: 60,
    description: '按启用状态、最近执行结果和异常优先级组织任务列表，回答“哪些任务需要盯”。',
    icon: 'mdi-puzzle-check-outline',
    card: { subtitle: '组件任务运行队列', border: true, refresh: 0 },
    component: 'TaskRuntimeModule',
    hosts: [full],
    dataSources: ['dashboard.tasks'],
    actions: [],
    layout: {
      [full]: { area: 'runtime', density: 'compact', minWidth: 300, minHeight: 108, colSpan: 4, rowSpan: 1, gridColumn: '3', gridRow: '3' },
    },
  },
  {
    id: 'config_summary',
    title: '配置概览',
    navLabel: '概览',
    category: 'config',
    categoryLabel: '配置中心',
    order: 10,
    description: '为配置页的 Hero、状态摘要和说明区提供统一模块入口，避免再造一套展示语言。',
    icon: 'mdi-tune-variant',
    card: { subtitle: '配置摘要与状态', border: true, refresh: 0 },
    component: 'ModuleHero',
    hosts: [config],
    dataSources: ['config.form', 'dashboard.tasks'],
    actions: [],
    layout: {
      [config]: { area: 'module-hero', density: 'form', minWidth: 320, minHeight: 120, colSpan: 12, rowSpan: 1 },
    },
  },
])

export const moduleRegistry = Object.freeze(
  Object.fromEntries(dashboardModules.map(moduleItem => [moduleItem.id, moduleItem])),
)

export function getDashboardModuleById(id) {
  return moduleRegistry[id] || null
}

export function getDashboardModulesForHost(host) {
  return dashboardModules.filter(moduleItem => {
    if (!moduleItem.hosts.includes(host)) return false
    if (host === full && suppressedFullDashboardModuleIds.has(moduleItem.id)) return false
    return true
  })
}

export function getModuleRenderer(moduleItem, host) {
  if (!moduleItem || !moduleItem.hosts?.includes(host)) return ''
  return moduleItem.renderers?.[host] || moduleItem.component
}

export function getModuleCardAttrs(moduleItem) {
  if (!moduleItem) return { title: '', subtitle: '', border: true, refresh: 0 }
  const card = moduleItem.card || {}
  return {
    title: moduleItem.title || '',
    subtitle: card.subtitle || '',
    border: card.border !== false,
    refresh: Number.isFinite(card.refresh) ? card.refresh : 0,
  }
}

