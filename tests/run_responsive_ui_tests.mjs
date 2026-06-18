#!/usr/bin/env node
import assert from 'node:assert/strict'
import { createRequire } from 'node:module'

const require = createRequire(import.meta.url)
const { chromium } = require('playwright')

const BASE_URL = process.env.MP_WEB_URL || 'http://localhost:3000'
const USERNAME = process.env.MP_USER || 'admin'
const PASSWORD = process.env.MP_PASSWORD || 'codex-mp-2026'
const CHROME_PATH = process.env.CHROME_PATH || 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
const PLUGIN_NAME = 'MP 运维助手'
const GB = 1024 ** 3

const viewports = [
  { name: 'desktop', width: 1440, height: 900 },
  { name: 'tablet', width: 834, height: 1112 },
  { name: 'mobile', width: 390, height: 844 },
  { name: 'narrow', width: 360, height: 740 },
]

const dashboardFixture = {
  enabled: true,
  summary: '',
  task_total: 10,
  task_on: 10,
  task_failed: 2,
  tasks: [
    { key: 'daily_report', name: '每日汇报', enabled: true, next: '2026-06-18 22:00', last_time: '2026-06-18 19:30', state: '成功', color: 'success', icon: 'mdi-newspaper-variant-outline' },
    { key: 'subscribe_reminder', name: '订阅追新', enabled: true, next: '2026-06-19 09:00', last_time: '2026-06-18 09:02', state: '成功', color: 'success', icon: 'mdi-bell-ring-outline' },
    { key: 'health_check', name: '健康巡查', enabled: true, next: '2026-06-19 00:00', last_time: '2026-06-18 20:00', state: '失败', color: 'error', icon: 'mdi-heart-pulse' },
    { key: 'site_stat', name: '站点数据统计', enabled: true, next: '2026-06-18 23:59', last_time: '2026-06-18 20:01', state: '成功', color: 'success', icon: 'mdi-chart-pie' },
    { key: 'log_clean', name: '日志清理', enabled: true, next: '2026-06-24 03:00', last_time: '2026-06-17 03:01', state: '成功', color: 'success', icon: 'mdi-broom' },
    { key: 'backup', name: '配置备份', enabled: true, next: '2026-06-19 04:00', last_time: '2026-06-18 04:00', state: '成功', color: 'success', icon: 'mdi-database-arrow-up-outline' },
    { key: 'mp_update', name: 'MP 更新检查', enabled: true, next: '2026-06-19 09:00', last_time: '2026-06-18 09:00', state: '失败', color: 'error', icon: 'mdi-update' },
    { key: 'market_update', name: '插件库更新', enabled: true, next: '2026-06-19 09:00', last_time: '2026-06-18 10:20', state: '待处理', color: 'warning', icon: 'mdi-puzzle-check-outline' },
    { key: 'downloader_tag', name: '种子标签', enabled: true, next: '手动执行', last_time: '2026-06-18 11:20', state: '成功', color: 'success', icon: 'mdi-tag-plus-outline' },
    { key: 'seedclean', name: '自动删种', enabled: true, next: '2026-06-19 08:00', last_time: '2026-06-18 08:00', state: '成功', color: 'success', icon: 'mdi-delete-sweep-outline' },
  ],
  health: {
    time: '2026-06-18 20:00',
    success: false,
    output: '⚠️ 存储空间：本地 /downloads/moviepilot/library/very/very/long/path 已用 93%，超过阈值 85%；目录权限：/config/plugins/AgentOpsAssistant/Backup 无写入权限；数据库：SQLite 主库连接正常\n✅ 订阅：正常\n⚠️ 下载器：qbittorrent 连接失败，HTTP 401 用户名或密码错误\n✅ 本插件任务：正常',
  },
}

const siteChartFixture = {
  date: '2026-06-18',
  basis: 'today',
  upload_total: 156 * GB,
  download_total: 48 * GB,
  sites: [
    { name: '馒头', upload: 64 * GB, download: 18 * GB },
    { name: '不可说-超长站点名称用于验证排版不会横向炸裂', upload: 40 * GB, download: 12 * GB },
    { name: '红豆饭', upload: 20 * GB, download: 7 * GB },
    { name: '青蛙', upload: 16 * GB, download: 5 * GB },
    { name: '海胆', upload: 8 * GB, download: 4 * GB },
    { name: '朋友', upload: 8 * GB, download: 2 * GB },
  ],
}

const downloaderFixture = {
  downloaders: [
    { name: 'qBittorrent-main', count: 3, dl_speed: 12 * 1024 * 1024, up_speed: 3 * 1024 * 1024 },
    { name: 'Transmission-backup-long-name', count: 2, dl_speed: 2 * 1024 * 1024, up_speed: 1 * 1024 * 1024 },
  ],
}

async function loginIfNeeded(page) {
  await page.goto(`${BASE_URL}/#/plugins`, { waitUntil: 'domcontentloaded' })
  await page.waitForTimeout(1000)
  if (!page.url().includes('/login')) return

  await page.locator('input').nth(0).fill(USERNAME)
  await page.locator('input').nth(1).fill(PASSWORD)
  await page.keyboard.press('Enter')
  await page.waitForTimeout(2500)
  await page.goto(`${BASE_URL}/#/plugins`, { waitUntil: 'domcontentloaded' })
  await page.waitForTimeout(1500)
}

async function mockDashboardApis(page) {
  await page.route('**/api/v1/plugin/AgentOpsAssistant/dashboard', route => {
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ code: 0, data: dashboardFixture }) })
  })
  await page.route('**/api/v1/plugin/AgentOpsAssistant/site_stat_chart', route => {
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ code: 0, data: siteChartFixture }) })
  })
  await page.route('**/api/v1/plugin/AgentOpsAssistant/downloader_overview', route => {
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ code: 0, data: downloaderFixture }) })
  })
  await page.route('**/api/v1/plugin/AgentOpsAssistant/run_seed_clean', route => {
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ code: 1, msg: '自动删种未执行：未选择下载器' }) })
  })
}

async function openPluginDashboard(page) {
  const card = page.locator('.v-card--link').filter({ hasText: PLUGIN_NAME }).first()
  await card.waitFor({ timeout: 15000 })
  await card.click({ position: { x: 40, y: 30 } })
  await page.waitForSelector('.agentops-dashboard', { timeout: 15000 })
  await page.waitForTimeout(800)
}

async function openPluginConfig(page) {
  await page.locator('.agentops-dashboard').getByRole('button', { name: /设置/ }).click()
  await page.waitForSelector('.aoa-config', { timeout: 15000 })
  await page.waitForTimeout(600)
}

async function auditVisibleDashboard(page, scope) {
  const result = await page.evaluate((scope) => {
    const isVisible = (el) => {
      const r = el.getBoundingClientRect()
      const cs = getComputedStyle(el)
      return r.width > 0 && r.height > 0 && cs.display !== 'none' && cs.visibility !== 'hidden'
    }
    const info = (el) => {
      const r = el.getBoundingClientRect()
      const cs = getComputedStyle(el)
      return {
        tag: el.tagName,
        cls: String(el.className || ''),
        text: (el.innerText || '').replace(/\s+/g, ' ').trim().slice(0, 120),
        width: Math.round(r.width),
        height: Math.round(r.height),
        deltaX: el.scrollWidth - el.clientWidth,
        deltaY: el.scrollHeight - el.clientHeight,
        overflowX: cs.overflowX,
        overflowY: cs.overflowY,
      }
    }
    const horizontalOverflow = [
      '.agentops-dashboard',
      '.glass-panel',
      '.site-stat-layout',
      '.site-stat-content',
      '.site-summary',
      '.site-legend',
      '.site-legend-row',
      '.action-panel',
      '.action-scroll',
      '.action-buttons',
      '.task-grid',
      '.task-card',
      '.health-grid',
      '.health-card',
    ]
      .flatMap(sel => [...document.querySelectorAll(sel)].filter(isVisible).map(info))
      .filter(item => item.deltaX > 3)

    const clippedImportantText = [
      '.overview-item strong',
      '.site-summary-item strong',
      '.site-traffic',
      '.action-btn-label',
      '.action-btn-desc',
      '.health-detail-row',
    ]
      .flatMap(sel => [...document.querySelectorAll(sel)].filter(isVisible).map(info))
      .filter(item => item.deltaX > 3 || item.deltaY > 4)

    const clippedCommandLabelStyles = [...document.querySelectorAll('.action-btn-label')]
      .filter(isVisible)
      .map(el => {
        const cs = getComputedStyle(el)
        return {
          ...info(el),
          overflow: cs.overflow,
          textOverflow: cs.textOverflow,
        }
      })
      .filter(item => item.overflow !== 'visible' || item.textOverflow === 'ellipsis')

    const actionScroll = document.querySelector('.action-scroll')
    const actionTotal = document.querySelectorAll('.action-item').length
    const actionVisible = actionScroll ? [...actionScroll.querySelectorAll('.action-item')].filter(isVisible).length : 0
    const actionBox = actionScroll ? info(actionScroll) : null

    const scrollbarIssues = [
      '.agentops-dashboard',
      '.site-legend',
      '.task-grid',
      '.health-grid',
      '.action-scroll',
    ]
      .map(sel => document.querySelector(sel))
      .filter(el => el && isVisible(el))
      .map(el => ({ ...info(el), width: getComputedStyle(el, '::-webkit-scrollbar').width, height: getComputedStyle(el, '::-webkit-scrollbar').height }))
      .filter(item => item.width !== '1px' || item.height !== '1px')

    return { scope, horizontalOverflow, clippedImportantText, clippedCommandLabelStyles, actionTotal, actionVisible, actionBox, scrollbarIssues }
  }, scope)

  assert.deepEqual(result.horizontalOverflow, [], `${scope} dashboard should not have plugin-internal horizontal overflow`)
  assert.deepEqual(result.clippedImportantText, [], `${scope} dashboard should not clip important text`)
  assert.deepEqual(result.clippedCommandLabelStyles, [], `${scope} command button labels should never rely on hidden overflow or ellipsis`)
  assert.equal(result.actionVisible, result.actionTotal, `${scope} dashboard should render every manual action button`)
  assert.equal(result.actionBox?.overflowY, 'visible', `${scope} dashboard action buttons should not rely on an internal scroller`)
  assert.deepEqual(result.scrollbarIssues, [], `${scope} dashboard scrollbars should stay at 1px`)
}

async function auditDashboardActionFailure(page, scope) {
  await page.locator('.action-btn--red').first().click()
  const alert = page.locator('.action-panel .v-alert').filter({ hasText: '未选择下载器' }).first()
  await alert.waitFor({ timeout: 5000 })
  const result = await alert.evaluate(el => {
    const cls = String(el.className || '')
    const color = getComputedStyle(el).color
    return { cls, color, text: (el.innerText || '').trim() }
  })
  assert.match(result.text, /未选择下载器/, `${scope} failed dashboard action should expose backend failure message`)
  assert.match(result.cls, /error/, `${scope} failed dashboard action should render as error alert`)
}

async function auditVisibleConfig(page, scope) {
  const result = await page.evaluate((scope) => {
    const roots = [...document.querySelectorAll('.aoa-config')].filter((el) => {
      const r = el.getBoundingClientRect()
      return r.width > 0 && r.height > 0
    })
    const isVisible = (el) => {
      const r = el.getBoundingClientRect()
      const cs = getComputedStyle(el)
      return r.width > 0 && r.height > 0 && cs.display !== 'none' && cs.visibility !== 'hidden'
    }
    const inConfig = (el) => roots.some(root => root.contains(el))
    const info = (el) => {
      const r = el.getBoundingClientRect()
      return {
        tag: el.tagName,
        cls: String(el.className || ''),
        text: (el.innerText || '').replace(/\s+/g, ' ').trim().slice(0, 120),
        width: Math.round(r.width),
        height: Math.round(r.height),
        deltaX: el.scrollWidth - el.clientWidth,
        deltaY: el.scrollHeight - el.clientHeight,
      }
    }
    const overflowSelectors = [
      '.aoa-window',
      '.aoa-pane',
      '.aoa-columns-form',
      '.aoa-table-wrap',
      '.aoa-report-table-scroll',
      '.aoa-report-table',
    ]
    const horizontalOverflow = overflowSelectors
      .flatMap(sel => [...document.querySelectorAll(sel)].filter(isVisible).map(info))
      .filter(item => item.deltaX > 3)

    const clippedLabels = [...document.querySelectorAll('.aoa-config .v-label.v-field-label')]
      .filter(el => isVisible(el) && inConfig(el))
      .filter(el => (el.innerText || '').trim() && el.scrollWidth > el.clientWidth + 3)
      .map(info)
    const clippedHeaderText = [...document.querySelectorAll('.aoa-config .aoa-header .v-card-title, .aoa-config .aoa-header .v-card-subtitle')]
      .filter(el => isVisible(el) && inConfig(el))
      .filter(el => (el.innerText || '').trim() && (el.scrollWidth > el.clientWidth + 3 || el.scrollHeight > el.clientHeight + 3))
      .map(info)

    const verticalAccessIssues = [...document.querySelectorAll('.aoa-card, .aoa-body, .aoa-content, .aoa-window')]
      .filter(el => isVisible(el) && inConfig(el))
      .filter(el => {
        const cs = getComputedStyle(el)
        return el.scrollHeight > el.clientHeight + 5 && !['auto', 'scroll'].includes(cs.overflowY)
      })
      .map(info)

    return { scope, horizontalOverflow, clippedLabels, clippedHeaderText, verticalAccessIssues }
  }, scope)

  assert.deepEqual(result.horizontalOverflow, [], `${scope} should not have horizontal overflow inside config`)
  assert.deepEqual(result.clippedLabels, [], `${scope} should not clip field labels`)
  assert.deepEqual(result.clippedHeaderText, [], `${scope} should not show clipped header text`)
  assert.deepEqual(result.verticalAccessIssues, [], `${scope} should keep long config content reachable by scrolling`)
}

async function walkConfigTabs(page, viewportName) {
  const navCount = await page.locator('.aoa-nav-item').count()
  for (let i = 0; i < navCount; i += 1) {
    await page.locator('.aoa-nav-item').nth(i).evaluate(el => {
      el.scrollIntoView({ block: 'center', inline: 'nearest' })
      el.click()
    })
    await page.waitForTimeout(100)

    const subCount = await page.locator('.aoa-subtab').count()
    for (let j = 0; j < Math.max(1, subCount); j += 1) {
      const currentSubCount = await page.locator('.aoa-subtab').count()
      if (currentSubCount > j) {
        await page.locator('.aoa-subtab').nth(j).evaluate(el => {
          el.scrollIntoView({ block: 'nearest', inline: 'nearest' })
          el.click()
        })
        await page.waitForTimeout(80)
      }
      const title = await page.evaluate(() => {
        const main = document.querySelector('.aoa-nav-item.v-list-item--active .v-list-item-title')?.innerText || ''
        const sub = document.querySelector('.aoa-subtab--active')?.innerText || ''
        return `${main.trim()} / ${sub.trim()}`
      })
      await auditVisibleConfig(page, `${viewportName}: ${title}`)
    }
  }
}

async function main() {
  const browser = await chromium.launch({ headless: true, executablePath: CHROME_PATH })
  try {
    for (const viewport of viewports) {
      const page = await browser.newPage({
        viewport: { width: viewport.width, height: viewport.height },
        deviceScaleFactor: 1,
        isMobile: viewport.width < 500,
      })
      await loginIfNeeded(page)
      await mockDashboardApis(page)
      await openPluginDashboard(page)
      await auditVisibleDashboard(page, `${viewport.name}: dashboard stress`)
      await auditDashboardActionFailure(page, `${viewport.name}: dashboard action failure`)
      await openPluginConfig(page)
      await walkConfigTabs(page, viewport.name)
      await page.close()
    }
  } finally {
    await browser.close()
  }
}

main().catch(err => {
  console.error(err)
  process.exit(1)
})
