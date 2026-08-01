// Action 配置 SSOT — Dashboard.vue / Page.vue 共享，禁止各 vue 里各写一份
// Page.vue 用全量分组版，Dashboard.vue (MP widget) 用子集

export const fusionCardActionPaths = Object.freeze([
  'create_tg_console_card',
  'run_daily_report',
])

export const quickActionPaths = Object.freeze([
  'run_subscribe_reminder',
  'run_today_transfer',
  'run_site_stat',
  'run_backup',
  'run_log_clean',
  'run_health_check',
  'run_mp_update',
  'run_market_update',
])

// MP widget 适用的 action paths（子集）
const mpWidgetActionPaths = [
  'run_subscribe_reminder',
  'run_today_transfer',
  'run_site_stat',
  'run_health_check',
  'run_backup',
]

// 完整分组 action 配置（插件仪表盘用）
export const actionGroups = [
  {
    group: '汇报与追新',
    icon: 'mdi-newspaper-variant-outline',
    actions: [
      { path: 'run_subscribe_reminder', component: 'subscribe_reminder', label: '订阅追新', desc: '推送今日追新', icon: 'mdi-bell-badge-outline', tone: 'blue' },
      { path: 'run_today_transfer', component: '', label: '今日入库', desc: '刷新今日入库', icon: 'mdi-download-circle-outline', tone: 'blue' },
    ],
  },
  {
    group: '站点与下载器',
    icon: 'mdi-download-network-outline',
    actions: [
      { path: 'run_site_stat', component: 'site_stat', label: '站点统计', desc: '刷新站点增量', icon: 'mdi-chart-pie', tone: 'blue' },
    ],
  },
  {
    group: '系统维护',
    icon: 'mdi-cog-outline',
    actions: [
      { path: 'run_backup', component: 'backup', label: '配置备份', desc: '执行自动备份', icon: 'mdi-database-arrow-up-outline', tone: 'violet' },
      { path: 'run_log_clean', component: 'log_clean', label: '日志清理', desc: '按保留行数截断日志', icon: 'mdi-broom', tone: 'violet' },
      { path: 'run_health_check', component: 'health_check', label: '健康巡查', desc: '检查关键状态', icon: 'mdi-heart-pulse', tone: 'green' },
      { path: 'run_mp_update', component: 'mp_update', label: 'MP 更新', desc: '检查主程序更新', icon: 'mdi-update', tone: 'amber' },
    ],
  },
  {
    group: '插件治理',
    icon: 'mdi-puzzle-check-outline',
    actions: [
      { path: 'run_market_update', component: 'market_update', label: '插件更新', desc: '检查插件库更新', icon: 'mdi-cloud-sync-outline', tone: 'amber' },
    ],
  },
]

export const fusionCardActions = [
  { path: 'create_tg_console_card', component: 'fusion_notify', label: '立即建卡', desc: '创建融合汇报卡', icon: 'mdi-card-plus-outline', tone: 'blue' },
  { path: 'run_daily_report', component: 'daily_report', label: '立即刷新', desc: '刷新融合汇报', icon: 'mdi-refresh', tone: 'blue' },
]

export const quickActionItems = actionGroups.flatMap(group => group.actions)

// 扁平化全部 action items
export const allActionItems = [
  ...quickActionItems,
  ...fusionCardActions,
]

// MP widget 子集（按 path 过滤，保持原始顺序）
export const mpWidgetActions = allActionItems.filter(action => mpWidgetActionPaths.includes(action.path))
