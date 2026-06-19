#!/usr/bin/env node
import assert from 'node:assert/strict'
import fs from 'node:fs'

const page = fs.readFileSync('plugins.v2/agentopsassistant/src/components/Page.vue', 'utf8')
const appPagePath = 'plugins.v2/agentopsassistant/src/components/AppPage.vue'
const dashboardPath = 'plugins.v2/agentopsassistant/src/components/Dashboard.vue'
const configPath = 'plugins.v2/agentopsassistant/src/components/Config.vue'
const vite = fs.readFileSync('plugins.v2/agentopsassistant/vite.config.js', 'utf8')

const requiredFragments = [
  'dashboard-shell',
  'dashboard-canvas',
  'alert-panel',
  'metrics-panel',
  'site-panel',
  'command-panel',
  'download-panel',
  'runtime-panel',
  '--shadow-panel',
  '--shadow-block',
  '--shadow-button',
  'grid-template-columns: minmax(300px, 410px) minmax(300px, 410px) minmax(280px, 1fr)',
  '命令面板',
  '站点数据统计',
  '下载器活动',
  '组件运行状况',
  'run_plugin_uninstall',
]

for (const fragment of requiredFragments) {
  assert.ok(page.includes(fragment), `Page.vue should contain static-draft fragment: ${fragment}`)
}

assert.ok(
  /const actionGroups = \[[\s\S]*group: '汇报与追新'[\s\S]*group: '站点与下载器'[\s\S]*group: '系统维护'[\s\S]*group: '插件治理'/m.test(page),
  'Page.vue should keep the command panel grouped like the final static draft',
)

assert.ok(
  /const metricCards = computed\(\(\) => \[/m.test(page),
  'Page.vue should expose the four metric cards as computed real data',
)

assert.ok(fs.existsSync(appPagePath), 'sidebar AppPage.vue should exist')
const appPage = fs.readFileSync(appPagePath, 'utf8')
const config = fs.readFileSync(configPath, 'utf8')

assert.ok(
  !config.includes('接入 MP 首页仪表盘') && !config.includes('mp_dashboard_enabled'),
  'Config.vue should not show the MP dashboard switch inside site statistic settings',
)

assert.ok(
  config.includes('sidebar_nav_enabled') && config.includes('侧边栏入口'),
  'Config.vue should expose a top-level sidebar entry switch',
)

assert.ok(
  vite.includes("'./AppPage': './src/components/AppPage.vue'"),
  'vite federation should expose AppPage for MP sidebar routes',
)

assert.ok(fs.existsSync(dashboardPath), 'MP dashboard Dashboard.vue should exist')
const dashboard = fs.readFileSync(dashboardPath, 'utf8')

assert.ok(
  vite.includes("'./Dashboard': './src/components/Dashboard.vue'"),
  'vite federation should expose Dashboard for MP dashboard widgets',
)

for (const fragment of ['SiteStatsWidget', 'ActionsWidget']) {
  assert.ok(dashboard.includes(fragment), `Dashboard.vue should route to ${fragment}`)
}

for (const fragment of ['StatusWidget', 'RuntimeWidget']) {
  assert.ok(!dashboard.includes(fragment), `Dashboard.vue should not route unnecessary ${fragment}`)
}

assert.ok(
  dashboard.includes('run_site_stat') && dashboard.includes('run_health_check'),
  'Dashboard.vue should expose redesigned manual action buttons',
)

assert.ok(
  appPage.includes('surface="sidebar"'),
  'AppPage.vue should render Page in sidebar surface mode',
)

for (const fragment of ['dashboard-shell--sidebar', ':class="[dashboardThemeClass, { \'dashboard-shell--sidebar\': isSidebarSurface }]"']) {
  assert.ok(page.includes(fragment), `Page.vue should adapt the existing dashboard shell for MP sidebar: ${fragment}`)
}

for (const fragment of ['.dashboard-shell--sidebar .dashboard-canvas', '.dashboard-shell--sidebar .metric-card', '.dashboard-shell--sidebar .command-panel']) {
  assert.ok(page.includes(fragment), `Page.vue should keep the full dashboard layout adapted to sidebar space: ${fragment}`)
}
