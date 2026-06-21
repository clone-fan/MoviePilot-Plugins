#!/usr/bin/env node
import assert from 'node:assert/strict'
import fs from 'node:fs'

const page = fs.readFileSync('plugins.v2/agentopsassistant/src/components/Page.vue', 'utf8')
const appPagePath = 'plugins.v2/agentopsassistant/src/components/AppPage.vue'
const dashboardPath = 'plugins.v2/agentopsassistant/src/components/Dashboard.vue'
const dashboardSitePath = 'plugins.v2/agentopsassistant/src/components/dashboard/SiteStatsWidget.vue'
const dashboardActionsPath = 'plugins.v2/agentopsassistant/src/components/dashboard/ActionsWidget.vue'
const configPath = 'plugins.v2/agentopsassistant/src/components/Config.vue'
const distAssetsPath = 'plugins.v2/agentopsassistant/dist/assets'
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
]

for (const fragment of requiredFragments) {
  assert.ok(page.includes(fragment), `Page.vue should contain static-draft fragment: ${fragment}`)
}

assert.ok(
  /const actionGroups = \[[\s\S]*group: '汇报与追新'[\s\S]*group: '站点与下载器'[\s\S]*group: '系统维护'[\s\S]*group: '插件治理'/m.test(page),
  'Page.vue should keep the command panel grouped like the final static draft',
)

assert.ok(
  !page.includes('run_plugin_uninstall') && !page.includes("label: '插件卸载'"),
  'Page.vue dashboard command panel should not expose destructive plugin uninstall quick actions',
)

assert.ok(
  /const metricCards = computed\(\(\) => \[/m.test(page),
  'Page.vue should expose the four metric cards as computed real data',
)

assert.ok(
  page.includes('getPluginApiRaw') && page.includes("payload?.message || res?.msg || ''"),
  'Page.vue should keep the downloader overview skipped message from the full backend envelope',
)

assert.ok(
  page.includes("下载器活动已跳过") && page.includes('v-if="!downloaderOverviewMessage"'),
  'Page.vue should show skipped downloader overview state without the realtime connection ghost card',
)

assert.ok(
  page.includes('isPluginDisabled') &&
    page.includes("return '插件已停用'") &&
    page.includes('alert-panel--idle') &&
    page.includes("'停用'"),
  'Page.vue should render disabled plugin state as neutral idle, not as an exception',
)

assert.ok(
  page.includes('const actionsDisabled = computed') &&
    page.includes('插件总开关未启用，手动命令已暂停') &&
    page.includes(':disabled="actionsDisabled || (!!actionRunning && actionRunning !== action.path)"'),
  'Page.vue should disable dashboard command buttons and short-circuit manual actions when the plugin main switch is off',
)

assert.ok(
  page.includes('function isTaskOn(task)') &&
    page.includes('return !!data.enabled && !!task?.enabled') &&
    page.includes("value: `${data.enabled ? data.task_on : 0} / ${data.task_total}`") &&
    page.includes("{{ isTaskBad(task) ? '失败' : isTaskOn(task) ? 'ON' : 'OFF' }}"),
  'Page.vue should treat component switches as effectively off when the plugin main switch is off',
)

assert.ok(fs.existsSync(appPagePath), 'sidebar AppPage.vue should exist')
const appPage = fs.readFileSync(appPagePath, 'utf8')
const config = fs.readFileSync(configPath, 'utf8')

assert.ok(
  !page.includes('.site-row-cell:nth-of-type(4n + 1)'),
  'Page.vue mobile site table should not hide the site name column through positional selectors',
)
for (const fragment of [
  'site-row-cell site-upload',
  'site-row-cell site-download',
  'site-row-cell site-percent',
]) {
  assert.ok(page.includes(fragment), `Page.vue should use explicit site table cell class: ${fragment}`)
}

assert.match(
  config,
  /<VTextField[^>]*v-model="form\.market_update_wiki_xpath"[\s\S]*?label=/,
  'Config.vue should expose the market_update_wiki_xpath setting in the update checker UI',
)

const healthItemsSelect = config.match(/<VSelect[^>]*v-model="form\.health_check_items"[\s\S]*?<\/VSelect>/)?.[0] || ''
assert.ok(
  healthItemsSelect.includes('hint=') &&
    healthItemsSelect.includes('persistent-hint') &&
    /留空|清空|全部/.test(healthItemsSelect),
  'Config.vue health check item selector should explain that empty selection means checking all items',
)

assert.ok(
  config.includes('plugin_uninstall_confirm: false') &&
    config.includes('form.plugin_uninstall_confirm') &&
    /run_plugin_uninstall[\s\S]*!form\.plugin_uninstall_confirm/.test(config),
  'Config.vue plugin uninstall should require an explicit confirmation control before enabling the destructive action',
)
assert.ok(
  /watch\(\(\) => props\.initialConfig[\s\S]*form\.plugin_uninstall_confirm\s*=\s*false/.test(config) &&
    /function\s+saveConfig\s*\(\)\s*\{[\s\S]*plugin_uninstall_confirm:\s*false/.test(config),
  'Config.vue plugin uninstall confirmation should be reset on load and never be persisted by saveConfig',
)

assert.ok(
    config.includes('const actionDisabledReason = computed') &&
    config.includes('actionComponentEnabled') &&
    config.includes('插件总开关未启用，手动动作已暂停。') &&
    config.includes(':disabled="!!actionDisabledReason || item.disabled || !actionComponentEnabled(item)"'),
  'Config.vue should disable manual action buttons and short-circuit actions when the main switch or component switch is off',
)

const cleanActionBlock = config.match(/clean:\s*\[[\s\S]*?\],\s*seedremove:/)?.[0] || ''
assert.ok(
  !cleanActionBlock.includes('run_plugin_uninstall'),
  'Config.vue should not render plugin uninstall through the bottom action dock',
)

assert.ok(
  config.includes('class="aoa-inline-action aoa-plugin-uninstall-action"') &&
    config.includes("@click=\"runAction('run_plugin_uninstall', '执行卸载')\""),
  'Config.vue should render plugin uninstall action inline beside the target plugin selector',
)

assert.ok(
  config.includes('WebDAV 一键恢复') &&
    config.includes('run_webdav_backup_restore') &&
    config.includes('preview_webdav_backup_restore'),
  'Config.vue should expose WebDAV backup restore controls in the WebDAV tab',
)

assert.ok(
  config.includes('aoa-seed-protect-row') &&
    config.includes('aoa-seed-option-label') &&
    /\.aoa-seed-option-label[\s\S]*white-space:\s*nowrap/m.test(config) &&
    /font-size:\s*12px/.test(config) &&
    /min-width:\s*max-content/.test(config),
  'Config.vue should keep short seed protection labels on one line with a smaller font',
)

const configDistCss = fs
  .readdirSync(distAssetsPath)
  .filter((name) => /^__federation_expose_Config-.*\.css$/.test(name))
  .map((name) => fs.readFileSync(`${distAssetsPath}/${name}`, 'utf8'))
  .join('\n')

assert.ok(
  /\.aoa-seed-options[\s\S]*display:\s*flex/m.test(configDistCss) &&
    /\.aoa-seed-option-label[\s\S]*white-space:\s*nowrap/m.test(configDistCss) &&
    /font-size:\s*12px/.test(configDistCss) &&
    /min-width:\s*max-content/.test(configDistCss),
  'dist Config CSS should be rebuilt with one-line seed protection labels',
)

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
assert.ok(fs.existsSync(dashboardSitePath), 'MP dashboard site widget should exist')
assert.ok(fs.existsSync(dashboardActionsPath), 'MP dashboard actions widget should exist')
const dashboardSite = fs.readFileSync(dashboardSitePath, 'utf8')
const dashboardActions = fs.readFileSync(dashboardActionsPath, 'utf8')

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
  dashboard.includes('componentEnabledStates') &&
    dashboard.includes('actionComponentEnabled') &&
    dashboard.includes('widgetActions') &&
    dashboard.includes('组件未启用，动作已暂停') &&
    dashboard.includes('if (action.disabled)'),
  'Dashboard.vue should pass component switch states to MP dashboard manual actions and short-circuit disabled actions',
)

assert.ok(
  dashboardActions.includes(':disabled="action.disabled || (!!actionRunning && actionRunning !== action.path)"') &&
    dashboardActions.includes(':title="action.reason || action.desc"'),
  'ActionsWidget.vue should render disabled MP dashboard action buttons with a readable reason',
)

assert.ok(
  /\.mp-action-btn\.v-btn[\s\S]*box-shadow:\s*var\(--mp-widget-shadow-cell\)\s*!important/m.test(dashboardActions),
  'ActionsWidget.vue action buttons should keep MP widget shadows above Vuetify button defaults',
)
assert.ok(
  /filter:\s*drop-shadow\(/.test(dashboardActions),
  'ActionsWidget.vue action buttons should use a drop-shadow visual fallback for cross-theme depth',
)

for (const fragment of [
  '--mp-widget-panel-fill-hi',
  '--mp-widget-cell-fill',
  '--mp-widget-shadow-panel',
  '--mp-widget-shadow-cell',
]) {
  assert.ok(dashboard.includes(fragment), `Dashboard.vue should expose shared MP dashboard visual token: ${fragment}`)
  assert.ok(dashboardSite.includes(fragment), `SiteStatsWidget.vue should consume shared MP dashboard visual token: ${fragment}`)
  assert.ok(dashboardActions.includes(fragment), `ActionsWidget.vue should consume shared MP dashboard visual token: ${fragment}`)
}

for (const source of [
  ['SiteStatsWidget.vue', dashboardSite],
  ['ActionsWidget.vue', dashboardActions],
]) {
  const [name, content] = source
  assert.ok(
    content.includes('var(--mp-widget-radius)'),
    `${name} should use the latest plugin dashboard radius token instead of the old compact 8px shell`,
  )
  assert.ok(
    content.includes('backdrop-filter: blur('),
    `${name} should keep the latest translucent glass depth used by the plugin dashboard`,
  )
  assert.ok(
    !/border-radius:\s*8px;/.test(content),
    `${name} should not keep the old cramped MP widget 8px radius`,
  )
  assert.ok(
    !/rgba\(var\(--v-theme-surface\),\s*0\.(?:86|64|58)\)/.test(content),
    `${name} should avoid hard-coded one-theme surface opacity and rely on shared tokens`,
  )
}

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

assert.ok(
  page.includes('--aoa-dashboard-radius: var(--v-card-border-radius'),
  'Page.vue outer dashboard radius should be controlled by MP/Vuetify theme variables',
)

assert.ok(
  /\.dashboard-shell\s*\{[\s\S]*border-radius:\s*var\(--aoa-dashboard-radius\)/m.test(page),
  'Page.vue dashboard shell should not hard-code its outer radius',
)

const dashboardShellRule = page.match(/\.dashboard-shell\s*\{[\s\S]*?\n\}/m)?.[0] || ''
assert.ok(
  /padding:\s*(?:24|26|28|30|32)px\s+(?:36|38|40|42|44)px\s+(?:32|34|36|38|40)px;/.test(dashboardShellRule),
  'Page.vue dashboard shell should keep generous MP dialog breathing room around the content',
)
assert.ok(
  dashboardShellRule.includes('border: 0;'),
  'Page.vue dashboard shell should not draw an extra outer border around the MP frame',
)
assert.ok(
  /background:\s*transparent;/.test(dashboardShellRule),
  'Page.vue dashboard shell should be transparent so the MP frame is the outer visual layer',
)
assert.ok(
  /box-shadow:\s*none;/.test(dashboardShellRule),
  'Page.vue dashboard shell should not add an extra outer shadow',
)
assert.ok(
  /backdrop-filter:\s*none(?:\s*!important)?;/.test(dashboardShellRule),
  'Page.vue dashboard shell should not blur as a separate outer layer',
)

assert.ok(
  /^\.agentops-frame\s*\{[\s\S]*border-radius:\s*var\(--aoa-dashboard-radius\)/m.test(page),
  'Page.vue dashboard frame should not hard-code its outer radius',
)

const agentopsFrameRule = page.match(/^\.agentops-frame\s*\{[\s\S]*?\n\}/m)?.[0] || ''
assert.ok(
  agentopsFrameRule.includes('border: 0;'),
  'Page.vue dashboard frame should not draw a second outer border inside the MP dialog',
)
assert.ok(
  /background:\s*transparent;/.test(agentopsFrameRule),
  'Page.vue dashboard frame should be transparent so only inner cards create visual layers',
)
assert.ok(
  /box-shadow:\s*none;/.test(agentopsFrameRule),
  'Page.vue dashboard frame should not add an extra outer shadow',
)
assert.ok(
  /backdrop-filter:\s*none(?:\s*!important)?;/.test(agentopsFrameRule),
  'Page.vue dashboard frame should not blur as a separate outer layer',
)
assert.ok(
  /-webkit-backdrop-filter:\s*none(?:\s*!important)?;/.test(agentopsFrameRule),
  'Page.vue dashboard frame should override WebKit backdrop blur as well',
)

const toolbarRule = page.match(/^\.agentops-toolbar\s*\{[\s\S]*?\n\}/m)?.[0] || ''
assert.ok(
  /margin-bottom:\s*(?:12|14|16|18)px;/.test(toolbarRule),
  'Page.vue toolbar should leave visible breathing room before dashboard content',
)
assert.ok(
  toolbarRule.includes('border-bottom: 0;'),
  'Page.vue toolbar should not draw a full-width top separator frame',
)
assert.ok(
  /background:\s*transparent;/.test(toolbarRule),
  'Page.vue toolbar should not render a separate top background panel',
)
assert.ok(
  /padding:\s*0\s+(?:18|20|22|24)px;/.test(toolbarRule),
  'Page.vue toolbar should keep safe horizontal spacing without relying on a boxed bar',
)

const canvasRule = page.match(/^\.dashboard-canvas\s*\{[\s\S]*?\n\}/m)?.[0] || ''
assert.ok(
  /padding:\s*(?:16|18|20)px;/.test(canvasRule),
  'Page.vue dashboard canvas should increase inner padding around panels',
)
assert.ok(
  /gap:\s*(?:14|16|18)px;/.test(canvasRule),
  'Page.vue dashboard canvas should increase panel gaps for a less cramped layout',
)

assert.ok(
  page.includes('.v-overlay:has(.agentops-dashboard) .v-overlay__scrim'),
  'Page.vue should dim the underlying MP page while the dashboard dialog is open',
)

const mobileRule = page.match(/@media \(max-width:\s*760px\)\s*\{[\s\S]*?\n\}/m)?.[0] || ''
for (const fragment of ['height: auto;', 'grid-template-rows: auto;', 'overflow: visible;']) {
  assert.ok(mobileRule.includes(fragment), `Mobile dashboard should avoid fixed-height compressed rows: ${fragment}`)
}
for (const fragment of ['.alert-panel', '.site-panel', '.download-panel', '.runtime-panel']) {
  assert.ok(mobileRule.includes(fragment), `Mobile dashboard should explicitly size primary panel: ${fragment}`)
}

for (const fragment of ['border-radius: 30px', 'border-radius: 22px']) {
  assert.ok(!page.includes(fragment), `Page.vue should not hard-code MP-controlled outer radius: ${fragment}`)
}

assert.ok(
  /\.site-body\s*\{[\s\S]*gap:\s*18px;[\s\S]*padding:\s*14px 18px 18px;/m.test(page),
  'Page.vue site statistics body should have more breathing room between the panel and inner content',
)

for (const fragment of ['--site-cell-line-alpha', '--site-cell-fill-alpha', '--site-cell-shadow']) {
  assert.ok(page.includes(fragment), `Page.vue should expose cross-theme site cell token: ${fragment}`)
}

assert.ok(
  /\.site-stat\s*\{[\s\S]*rgba\(var\(--line\), var\(--site-cell-line-alpha\)\)[\s\S]*rgba\(var\(--panel\), var\(--site-cell-fill-alpha\)\)[\s\S]*box-shadow:\s*var\(--site-cell-shadow\)/m.test(page),
  'Page.vue site stat cards should use shared translucent tokens and shadow',
)

assert.ok(
  /\.site-row-cell\s*\{[\s\S]*rgba\(var\(--line\), var\(--site-cell-line-alpha\)\)[\s\S]*box-shadow:\s*var\(--site-cell-shadow\)/m.test(page),
  'Page.vue site table cells should use shared translucent tokens and shadow',
)

assert.ok(
  /\.cmd-grid\s*\{[\s\S]*grid-template-columns:\s*repeat\(2,\s*minmax\(0,\s*1fr\)\)/m.test(page),
  'Page.vue command button grid should not use fixed minimum column widths that overflow MP dialogs',
)

const transparentThemeRule = page.match(/\.agentops-dashboard\.agentops-theme--transparent\s*\{[\s\S]*?\n\}/m)?.[0] || ''
for (const fragment of ['--site-cell-line-alpha', '--site-cell-fill-alpha', '--site-cell-shadow']) {
  assert.ok(transparentThemeRule.includes(fragment), `Transparent theme should tune site cell token: ${fragment}`)
}
