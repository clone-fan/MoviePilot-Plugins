#!/usr/bin/env node
import assert from 'node:assert/strict'
import fs from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const repoRoot = process.env.MOVIEPILOT_PLUGINS_REPO_ROOT
  ? path.resolve(process.env.MOVIEPILOT_PLUGINS_REPO_ROOT)
  : path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const fromRoot = (...segments) => path.join(repoRoot, ...segments)

const page = fs.readFileSync(fromRoot('plugins.v2/agentopsassistant/src/components/Page.vue'), 'utf8')
const appPagePath = fromRoot('plugins.v2/agentopsassistant/src/components/AppPage.vue')
const dashboardPath = fromRoot('plugins.v2/agentopsassistant/src/components/Dashboard.vue')
const dashboardSitePath = fromRoot('plugins.v2/agentopsassistant/src/components/dashboard/SiteStatsWidget.vue')
const dashboardActionsPath = fromRoot('plugins.v2/agentopsassistant/src/components/dashboard/ActionsWidget.vue')
const configPath = fromRoot('plugins.v2/agentopsassistant/src/components/Config.vue')
const distAssetsPath = fromRoot('plugins.v2/agentopsassistant/dist/assets')
const vite = fs.readFileSync(fromRoot('plugins.v2/agentopsassistant/vite.config.js'), 'utf8')

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
  'grid-template-columns: minmax(320px, 1.08fr) minmax(320px, 1.08fr) minmax(300px, 0.92fr)',
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
    page.includes(':disabled="actionsDisabled || !actionComponentEnabled(action) || (!!actionRunning && actionRunning !== action.path)"'),
  'Page.vue should disable dashboard command buttons and short-circuit manual actions when the plugin main switch is off',
)

assert.ok(
  page.includes('quickActions') &&
    page.includes('command-quick-card') &&
    page.includes('{{ actionItems.length }} 项') &&
    page.includes(':title="quick.label"') &&
    !page.includes('quick-action-panel') &&
    !/actionGroups[\s\S]*create_tg_console_card[\s\S]*run_daily_report/m.test(page),
  'Page.vue should render create/refresh inside the command panel quick module, matching the git UI placement',
)

assert.ok(
  page.includes('siteEmptyTitle') &&
    page.includes('siteEmptyDesc') &&
    page.includes('data_valid') &&
    page.includes('basis') &&
    page.includes('last_error'),
  'Page.vue should distinguish site statistic empty, skipped and error states from the backend envelope',
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
const fusionPane = config.slice(
  config.indexOf("v-show=\"activeSub === 'fusion'\""),
  config.indexOf("v-show=\"activeSub === 'hc'\""),
)
const healthPane = config.slice(
  config.indexOf("v-show=\"activeSub === 'hc'\""),
  config.indexOf("v-show=\"activeSub === 'subfill'\""),
)

for (const fragment of [
  'fusion_notify_enabled: true',
  'fusion_notify_schedule_enabled: true',
  "fusion_notify_cron: '0 * * * *'",
  'fusion_notify_columns: fusionColumnKeys',
  "report_storage_targets: ['config', 'download', 'library', 'storages']",
  'v-model:enabled="form.fusion_notify_enabled"',
  'form.fusion_notify_schedule_enabled',
  'form.fusion_notify_cron',
  'form.report_storage_targets',
  'fusionColumnEnabled(s.key)',
  'setFusionColumnEnabled(s.key, $event)',
]) {
  assert.ok(config.includes(fragment), `Config.vue should expose fusion notification setting: ${fragment}`)
}
for (const fragment of [
  'daily_report_schedule_enabled',
  'subscribe_reminder_schedule_enabled',
  'health_check_schedule_enabled',
  'backup_schedule_enabled',
  'log_clean_schedule_enabled',
  'mp_update_schedule_enabled',
  'market_update_schedule_enabled',
  'seedclean_schedule_enabled',
]) {
  assert.ok(config.includes(fragment), `Config.vue should expose independent schedule switch: ${fragment}`)
}
assert.ok(
  !config.includes('aoa-quick-card-actions') &&
    !config.includes('quickCardActions') &&
    /report:\s*\[\s*\{\s*key:\s*'fusion',\s*title:\s*'融合通知'/m.test(config) &&
    !config.includes("title: '定时刷新'") &&
    !config.includes("title: '组件栏目'") &&
    config.includes('currentSubs.length > 1'),
  'Config.vue should merge fusion notification into one common-template sub tab and hide the subtab strip when only one item exists',
)
assert.ok(
  config.includes("title: '融合通知'") &&
    !config.includes("title: 'Telegram 日报卡'") &&
    !config.includes('kicker="Telegram 日报卡"'),
  'Config.vue should replace the primary Telegram daily-card wording with fusion notification wording',
)
assert.ok(
  !config.includes('下载器管理 > 下载入库') &&
    !config.includes('健康巡查 > 存储空间') &&
    config.includes('融合通知已接管') &&
    !config.includes('关闭融合通知后恢复本组件自身设置') &&
    config.includes('数据范围'),
  'Config.vue should remove second-level component breadcrumbs and explain unified fusion takeover for component notification settings',
)

const themeEntrySources = {
  'Page.vue': page,
  'Config.vue': config,
  'Dashboard.vue': fs.readFileSync(dashboardPath, 'utf8'),
  'SiteStatsWidget.vue': fs.readFileSync(dashboardSitePath, 'utf8'),
  'ActionsWidget.vue': fs.readFileSync(dashboardActionsPath, 'utf8'),
}

for (const [name, content] of Object.entries(themeEntrySources)) {
  assert.ok(
    content.includes('var(--app-surface-radius') &&
      content.includes('var(--app-surface-border') &&
      content.includes('var(--app-surface-shadow'),
    `${name} should keep every public MP surface aligned to official MoviePilot tokens`,
  )
  assert.ok(
    content.includes('--transparent-opacity') && content.includes('--transparent-blur'),
    `${name} should keep transparent theme tied to MoviePilot transparent tokens`,
  )
  assert.ok(
    !/background(?:-color)?:\s*(?:#000|black|rgb\(0,\s*0,\s*0\))/i.test(content),
    `${name} should not hard-code black backgrounds instead of MoviePilot theme variables`,
  )
}

for (const [name, content] of Object.entries({
  'Page.vue': page,
  'Config.vue': config,
  'Dashboard.vue': themeEntrySources['Dashboard.vue'],
  'SiteStatsWidget.vue': themeEntrySources['SiteStatsWidget.vue'],
  'ActionsWidget.vue': themeEntrySources['ActionsWidget.vue'],
})) {
  assert.ok(
    content.includes('--aoa-inner-surface') &&
      content.includes('--aoa-inner-surface-strong') &&
      content.includes('--aoa-inner-border') &&
      content.includes('--aoa-inner-shadow') &&
      content.includes('--aoa-inner-blur'),
    `${name} should expose the shared stronger inner glass surface contract`,
  )
  assert.ok(
    !/--(?:mp-cell|aoa-native-field)-surface:\s*rgba\(var\(--v-theme-on-surface\),\s*0\.0[4-7]\)/.test(content),
    `${name} should not keep ultra-low-opacity inner cards that disappear on transparent MP themes`,
  )
}

assert.ok(
  /--aoa-scrollbar-alpha:\s*0\.0[6-9]/.test(config) &&
    /--aoa-scrollbar-hover-alpha:\s*0\.1[0-6]/.test(config),
  'Config.vue scrollbar feedback should be nearly hidden, not a visible thick line',
)

for (const [name, content] of Object.entries({
  'SiteStatsWidget.vue': themeEntrySources['SiteStatsWidget.vue'],
  'ActionsWidget.vue': themeEntrySources['ActionsWidget.vue'],
})) {
  assert.ok(
    /::-webkit-scrollbar[\s\S]*width:\s*1px\s*!important[\s\S]*height:\s*1px\s*!important/.test(content) &&
      /::-webkit-scrollbar-track[\s\S]*background:\s*transparent\s*!important/.test(content) &&
      /::-webkit-scrollbar-button[\s\S]*display:\s*none\s*!important/.test(content),
    `${name} should hide WebKit scrollbar tracks/buttons with the same low-visibility rule as the main dashboard`,
  )
}
assert.ok(
  config.includes('fusionColumnGroups') &&
    config.includes('activeFusionGroup') &&
    config.includes('activeFusionColumnGroup') &&
    config.includes("group: '订阅与站点'") &&
    config.includes("group: '下载与媒体'") &&
    config.includes("group: '系统维护'") &&
    config.includes('aoa-fusion-category-tabs') &&
    config.includes('aoa-fusion-subcategory-list') &&
    !config.includes('aoa-report-group-row'),
  'Config.vue fusion columns should use clickable large categories with focused subcategory content',
)
assert.ok(
  /\.aoa-fusion-category-tabs\s*\{[\s\S]*grid-template-columns:\s*repeat\(4,\s*minmax\(132px,\s*1fr\)\)/m.test(config) &&
    /@media\s*\(max-width:\s*960px\)\s*\{[\s\S]*\.aoa-fusion-category-tabs\s*\{[\s\S]*grid-template-columns:\s*repeat\(2,\s*minmax\(128px,\s*1fr\)\)/m.test(config) &&
    /@media\s*\(max-width:\s*720px\)\s*\{[\s\S]*\.aoa-fusion-category-tabs\s*\{[\s\S]*grid-template-columns:\s*1fr/m.test(config) &&
    !/\.aoa-fusion-category-title\s*\{[\s\S]*white-space:\s*nowrap/m.test(config),
  'Config.vue fusion category tabs should adapt as 4/2/1 columns and keep titles readable instead of truncating',
)
assert.ok(
  !config.includes('MP 全局 Telegram 通知渠道') &&
    !config.includes('Bot Token 和 Chat ID 复用') &&
    !config.includes('TG 按钮交互') &&
    !config.includes('启用消息轮询') &&
    !config.includes('轮询间隔') &&
    !config.includes('授权用户 ID') &&
    config.includes("class: 'aoa-fusion-takeover-note'") &&
    /h\('span',\s*\{\s*class:\s*'aoa-fusion-takeover-note'/.test(config) &&
    /\.aoa-fusion-takeover-note\s*\{[\s\S]*position:\s*absolute/m.test(config) &&
    !/name:\s*'FusionTakeoverAlert'[\s\S]*resolveComponent\('VAlert'\)/.test(config),
  'Config.vue should remove the TG button interaction settings from the UI and keep takeover as a compact non-flow note',
)
assert.ok(
  !fusionPane.includes('form.report_storage_targets') &&
    healthPane.includes('form.report_storage_targets') &&
    healthPane.includes('存储空间展示目标'),
  'Config.vue should move storage display targets from fusion notification into health check settings',
)
assert.ok(
  config.includes('aoa-health-schedule-cell') &&
    /\.aoa-health-scope-grid\s*\{[\s\S]*grid-template-columns:\s*repeat\(12,\s*minmax\(0,\s*1fr\)\)/m.test(config) &&
    /\.aoa-health-field-third\s*\{[\s\S]*grid-column:\s*span\s+3/m.test(config),
  'Config.vue health check schedule, cron, threshold and notification channel should fit in one horizontal row on desktop',
)
assert.ok(
  page.includes('command-quick-card') &&
    page.includes('mdi-card-plus-outline') &&
    page.includes('mdi-refresh') &&
    page.includes('grid-template-rows: auto minmax(0, 1fr) auto'),
  'Page.vue command panel should keep quick card on top while letting the command body scroll without clipping the 9 actions',
)

assert.ok(
  /\.command-panel\s*\{[\s\S]*?container-type:\s*inline-size/m.test(page) &&
    /\.command-quick-card\s*\{[\s\S]*?display:\s*grid[\s\S]*?grid-template-columns:\s*minmax\(112px,\s*0\.72fr\)\s+minmax\(220px,\s*1\.28fr\)/m.test(page) &&
    /\.command-quick-buttons\s*\{[\s\S]*?width:\s*100%[\s\S]*?grid-template-columns:\s*repeat\(2,\s*minmax\(0,\s*1fr\)\)/m.test(page) &&
    page.includes('class="command-quick-label"') &&
    /@container \(max-width:\s*360px\)\s*\{[\s\S]*?\.command-quick-card[\s\S]*?grid-template-columns:\s*1fr[\s\S]*?\.command-quick-buttons[\s\S]*?width:\s*100%/m.test(page) &&
    /@container \(max-width:\s*300px\)\s*\{[\s\S]*?\.command-quick-buttons[\s\S]*?grid-template-columns:\s*1fr/m.test(page),
  'Page.vue command quick card should adapt to the command panel width, not only the viewport width',
)

assert.ok(
  /\.command-body\s*\{[\s\S]*padding:\s*0\s+4px\s+10px\s+0/m.test(page) &&
    /\.command-panel\s*\{[\s\S]*gap:\s*12px/m.test(page) &&
    /\.command-group\s*\{[\s\S]*padding:\s*14px\s+14px/m.test(page),
  'Page.vue command panel should use consistent group spacing with a visible bottom breathing gap',
)

assert.ok(
  !page.includes('.site-row-cell:nth-of-type(4n + 1)'),
  'Page.vue mobile site table should not hide the site name column through positional selectors',
)

assert.ok(
  page.includes('class="site-list site-legend"') &&
    page.includes('class="site-card"') &&
    page.includes('class="site-card-head"') &&
    page.includes('class="site-card-metrics"') &&
    page.includes('class="site-percent"') &&
    page.includes('site-row-cell site-upload') &&
    page.includes('site-row-cell site-download') &&
    !page.includes('class="site-table site-legend"') &&
    !page.includes('<div class="th">站点</div>'),
  'Page.vue should render site rows as indivisible cards instead of split grid cells that overlap in narrow MP layouts',
)

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
  '--mp-widget-surface-opacity',
  '--mp-widget-mp-surface-opacity',
  '--mp-widget-shadow-panel',
  '--mp-widget-shadow-cell',
]) {
  assert.ok(dashboard.includes(fragment), `Dashboard.vue should expose shared MP dashboard visual token: ${fragment}`)
  assert.ok(dashboardSite.includes(fragment), `SiteStatsWidget.vue should consume shared MP dashboard visual token: ${fragment}`)
  assert.ok(dashboardActions.includes(fragment), `ActionsWidget.vue should consume shared MP dashboard visual token: ${fragment}`)
}

assert.ok(
  dashboard.includes('var(--mp-widget-mp-surface-opacity)') &&
    dashboard.includes('--mp-widget-mp-surface-opacity: var(--v-card-opacity') &&
    !dashboard.includes('var(--v-medium-emphasis-opacity, 0.68)'),
  'Dashboard.vue should derive widget opacity from MP/Vuetify card opacity instead of text emphasis opacity',
)

const dashboardPiePalette = dashboard.slice(
  dashboard.indexOf('const sitePieColors = ['),
  dashboard.indexOf('const siteRows = computed'),
)
assert.ok(
  dashboardPiePalette.includes('rgba(88, 204, 118, 0.95)') &&
    dashboardPiePalette.includes('rgba(45, 212, 191, 0.92)') &&
    dashboardPiePalette.includes('rgba(96, 165, 250, 0.92)') &&
    !dashboardPiePalette.includes('v-theme-on-surface'),
  'Dashboard.vue MP site pie should use readable colored segments instead of an all-grey on-surface palette',
)

assert.ok(
  !dashboardActions.includes('action.tone') &&
    !/mp-action-btn--(?:blue|cyan|green|red|error|success|info)/.test(dashboardActions) &&
    !/v-theme-(?:error|info|success|primary)/.test(dashboardActions),
  'ActionsWidget.vue should render default manual actions with neutral MP theme colors instead of red/blue/green/primary accents',
)

assert.ok(
  !/v-theme-(?:error|info|success|primary)/.test(dashboardSite),
  'SiteStatsWidget.vue should render default site statistics with neutral MP theme colors instead of red/blue/green/primary accents',
)

assert.ok(
  dashboardSite.includes('container-type: inline-size') &&
    dashboardSite.includes('class="mp-site-card"') &&
    dashboardSite.includes('class="mp-site-card-head"') &&
    dashboardSite.includes('class="mp-site-card-metrics"') &&
    !dashboardSite.includes('class="th mp-site-th-name"'),
  'SiteStatsWidget.vue should render each site as an indivisible card instead of split grid cells that can overlap',
)

assert.ok(
  /\.mp-site-panel\s*\{[\s\S]*?height:\s*100%[\s\S]*?overflow:\s*hidden/m.test(dashboardSite) &&
    /\.mp-site-body\s*\{[\s\S]*?overflow:\s*hidden/m.test(dashboardSite) &&
    /\.mp-site-data\s*\{[\s\S]*?min-height:\s*0[\s\S]*?overflow:\s*hidden/m.test(dashboardSite),
  'SiteStatsWidget.vue should constrain itself to the MP dashboard card height instead of overflowing into the next widget',
)

assert.ok(
  /@container \(max-width:\s*560px\)\s*\{[\s\S]*?\.mp-donut-zone[\s\S]*?min-height:\s*132px[\s\S]*?\.mp-donut[\s\S]*?width:\s*108px[\s\S]*?height:\s*108px/m.test(dashboardSite) &&
    /@container \(max-width:\s*560px\)\s*\{[\s\S]*?\.mp-site-data[\s\S]*?grid-template-rows:\s*auto\s+minmax\(0,\s*1fr\)[\s\S]*?\.mp-site-stats[\s\S]*?grid-template-columns:\s*repeat\(2,\s*minmax\(0,\s*1fr\)\)/m.test(dashboardSite) &&
    /@media \(max-width:\s*760px\)\s*\{[\s\S]*?\.mp-donut-zone[\s\S]*?min-height:\s*132px[\s\S]*?\.mp-site-data[\s\S]*?grid-template-rows:\s*auto\s+minmax\(0,\s*1fr\)[\s\S]*?\.mp-site-stats[\s\S]*?grid-template-columns:\s*repeat\(2,\s*minmax\(0,\s*1fr\)\)/m.test(dashboardSite) &&
    /\.mp-site-card-metrics\s*\{[\s\S]*?grid-template-columns:\s*repeat\(2,\s*minmax\(0,\s*1fr\)\)/m.test(dashboardSite),
  'SiteStatsWidget.vue should compress chart, stats and site rows in the fixed-height MP dashboard widget',
)

assert.ok(
  /\.mp-site-data\s*\{[\s\S]*?grid-template-rows:\s*auto\s+minmax\(0,\s*1fr\)[\s\S]*?overflow:\s*hidden/m.test(dashboardSite) &&
    /\.mp-site-stat\s*\{[\s\S]*?height:\s*32px[\s\S]*?grid-template-columns:\s*auto\s+minmax\(0,\s*1fr\)[\s\S]*?overflow:\s*hidden[\s\S]*?contain:\s*layout paint/m.test(dashboardSite) &&
    /\.mp-site-stat--date\s*\{[\s\S]*?grid-column:\s*1\s*\/\s*-1[\s\S]*?height:\s*30px/m.test(dashboardSite) &&
    /\.mp-site-card\s*\{[\s\S]*?grid-template-rows:\s*18px\s+30px[\s\S]*?overflow:\s*hidden[\s\S]*?contain:\s*layout paint/m.test(dashboardSite),
  'SiteStatsWidget.vue should reserve real stat rows and keep the date full-width so labels cannot paint over site cards',
)

assert.ok(
  dashboardSite.includes('mp-site-upload') &&
    dashboardSite.includes('mp-site-download') &&
    dashboardSite.includes('mp-site-percent') &&
    dashboardSite.includes('mp-site-stat--date') &&
    !dashboardSite.includes('nth-of-type'),
  'SiteStatsWidget.vue mobile table should use explicit cell classes instead of positional selectors',
)

assert.ok(
  dashboardActions.includes('container-type: inline-size') &&
    /@container \(max-width:\s*420px\)\s*\{[\s\S]*?\.mp-action-copy small[\s\S]*?display:\s*none[\s\S]*?\.mp-action-arrow[\s\S]*?display:\s*none/m.test(dashboardActions),
  'ActionsWidget.vue should compress action rows by widget container width on narrow MP dashboard cards',
)

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
  assert.ok(
    content.includes('rgba(var(--v-theme-surface), var(--mp-widget-surface-opacity))'),
    `${name} should layer the MP global surface opacity token under widget glass backgrounds`,
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
  /padding:\s*(?:24|26|28|30|32)px\s+(?:(?:36|38|40|42|44)px|clamp\(18px,\s*3vw,\s*40px\))\s+(?:32|34|36|38|40)px;/.test(dashboardShellRule),
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

for (const [name, content] of Object.entries({
  'Page.vue': page,
  'Dashboard.vue': dashboard,
})) {
  assert.ok(
    !/:global\([^)]*\.v-overlay__scrim[^)]*\)\s*\{[\s\S]*?background:/m.test(content) &&
      !/\.agentops-dashboard::(?:before|after)\s*\{[\s\S]*?inset:\s*0\s*;/m.test(content) &&
      !/\.dashboard-shell::(?:before|after)\s*\{[\s\S]*?inset:\s*0\s*;/m.test(content) &&
      !/\.agentops-frame::(?:before|after)\s*\{[\s\S]*?inset:\s*0\s*;/m.test(content) &&
      !/\.aoa-dashboard-widget::(?:before|after)\s*\{[\s\S]*?inset:\s*0\s*;/m.test(content),
    `${name} should not add a root-level transparent overlay over the MP page or dashboard shell`,
  )
}

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
  /\.site-data\s*\{[\s\S]*?grid-template-rows:\s*auto\s+minmax\(0,\s*1fr\)[\s\S]*?overflow:\s*hidden/m.test(page) &&
    /\.site-stat\s*\{[\s\S]*?height:\s*32px[\s\S]*?grid-template-columns:\s*auto\s+minmax\(0,\s*1fr\)[\s\S]*?overflow:\s*hidden[\s\S]*?contain:\s*layout paint/m.test(page) &&
    /\.site-stat:nth-child\(3\)\s*\{[\s\S]*?grid-column:\s*1\s*\/\s*-1[\s\S]*?height:\s*30px/m.test(page) &&
    /\.site-card\s*\{[\s\S]*?grid-template-rows:\s*18px\s+30px[\s\S]*?overflow:\s*hidden[\s\S]*?contain:\s*layout paint/m.test(page),
  'Page.vue site statistics should reserve stat rows and keep the date full-width above stable site cards',
)

assert.ok(
  /\.site-row-cell\s*\{[\s\S]*rgba\(var\(--line\), var\(--site-cell-line-alpha\)\)[\s\S]*box-shadow:\s*var\(--site-cell-shadow\)/m.test(page),
  'Page.vue site table cells should use shared translucent tokens and shadow',
)

assert.ok(
  /\.cmd-grid\s*\{[\s\S]*grid-template-columns:\s*repeat\(2,\s*minmax\(0,\s*1fr\)\)/m.test(page),
  'Page.vue command button grid should not use fixed minimum column widths that overflow MP dialogs',
)

assert.ok(
  /@media \(max-width:\s*520px\)\s*\{[\s\S]*?\.dashboard-canvas[\s\S]*?padding:\s*8px;[\s\S]*?\.cmd-grid[\s\S]*?grid-template-columns:\s*1fr/m.test(page),
  'Page.vue should include an extra-phone breakpoint so dense dashboard controls do not overflow below 520px',
)

assert.ok(
  /@media \(max-width:\s*380px\)\s*\{[\s\S]*?\.agentops-toolbar[\s\S]*?\.command-quick-card[\s\S]*?\.alert-line/m.test(page),
  'Page.vue should include an ultra-narrow breakpoint for 320-380px MP dialogs',
)

assert.ok(
  /@media \(max-width:\s*520px\)\s*\{[\s\S]*?\.aoa-header-controls[\s\S]*?flex-wrap:\s*wrap[\s\S]*?\.aoa-actions[\s\S]*?flex-wrap:\s*wrap/m.test(config),
  'Config.vue should let header controls and bottom actions wrap on phone-sized dialogs',
)

assert.ok(
  /@media \(max-height:\s*640px\)\s+and\s+\(max-width:\s*760px\)\s*\{[\s\S]*?\.aoa-nav[\s\S]*?height:\s*128px/m.test(config),
  'Config.vue should shorten the mobile navigation rail on low-height screens',
)

const transparentThemeRule = page.match(/\.agentops-dashboard\.agentops-theme--transparent\s*\{[\s\S]*?\n\}/m)?.[0] || ''
for (const fragment of ['--site-cell-line-alpha', '--site-cell-fill-alpha', '--site-cell-shadow']) {
  assert.ok(transparentThemeRule.includes(fragment), `Transparent theme should tune site cell token: ${fragment}`)
}

const remoteEntry = fs.readFileSync(`${distAssetsPath}/remoteEntry.js`, 'utf8')
const exposedCssFiles = [...remoteEntry.matchAll(/dynamicLoadingCss\(\["([^"]+\.css)"\][\s\S]*?__federation_import\('\.\/([^']+\.js)'\)/g)]
assert.ok(exposedCssFiles.length > 0, 'remoteEntry.js should expose CSS/JS pairs for federation modules')

for (const [, cssFile, jsFile] of exposedCssFiles) {
  const js = fs.readFileSync(`${distAssetsPath}/${jsFile}`, 'utf8')
  const css = fs.readFileSync(`${distAssetsPath}/${cssFile}`, 'utf8')
  const jsScopeIds = [...js.matchAll(/['"]__scopeId['"]\s*,\s*["']([^"']+)["']/g)].map((match) => match[1])
  const cssScopeIds = new Set([...css.matchAll(/\[(data-v-[^\]]+)\]/g)].map((match) => match[1]))

  for (const scopeId of jsScopeIds) {
    assert.ok(
      cssScopeIds.has(scopeId),
      `${cssFile} should contain scoped CSS selectors for ${jsFile} scopeId ${scopeId}`,
    )
  }
}
