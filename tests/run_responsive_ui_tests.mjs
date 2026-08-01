#!/usr/bin/env node
import assert from 'node:assert/strict'
import { createRequire } from 'node:module'

const require = createRequire(import.meta.url)
const { chromium } = require('playwright')

const BASE_URL = process.env.MP_WEB_URL || 'http://localhost:3000'
const USERNAME = process.env.MP_USER || 'admin'
const PASSWORD = process.env.MP_PASSWORD || 'codex-mp-2026'
const CHROME_PATH = process.env.CHROME_PATH || ''
const PLUGIN_NAME = 'MP 运维助手'
const GB = 1024 ** 3

const viewports = [
  { name: 'desktop', width: 1440, height: 900 },
  { name: 'short-desktop', width: 1240, height: 760 },
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
    output: '⚠️ 存储空间：本地 /downloads/moviepilot/library/very/very/long/path 已用 93%，超过阈值 85%；目录权限：/config/plugins/Signal/Backup 无写入权限；数据库：SQLite 主库连接正常\n✅ 订阅：正常\n⚠️ 下载器：qbittorrent 连接失败，HTTP 401 用户名或密码错误\n✅ 本插件任务：正常',
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

function isLoginUrl(url) {
  return url.includes('#/login') || url.includes('/login')
}

async function waitForLoginDecision(page) {
  await page.waitForFunction(() => {
    const onLogin = location.hash.startsWith('#/login') || location.pathname.includes('/login')
    return !onLogin || document.querySelectorAll('input').length >= 2
  }, { timeout: 8000 }).catch(() => {})
}

async function gotoPlugins(page) {
  await page.goto(`${BASE_URL}/#/plugins`, { waitUntil: 'domcontentloaded' })
  await page.waitForLoadState('networkidle', { timeout: 5000 }).catch(() => {})
  await waitForLoginDecision(page)
}

async function loginIfNeeded(page) {
  await gotoPlugins(page)
  if (isLoginUrl(page.url())) {
    const inputs = page.locator('input')
    const inputCount = await inputs.count()
    if (inputCount < 2) {
      throw new Error(`Login page did not render credential inputs: url=${page.url()} inputs=${inputCount}`)
    }

    await inputs.nth(0).fill(USERNAME)
    await inputs.nth(1).fill(PASSWORD)
    await page.keyboard.press('Enter')
    await page.waitForFunction(() => {
      return !(location.hash.startsWith('#/login') || location.pathname.includes('/login'))
    }, { timeout: 15000 })
  }

  await gotoPlugins(page)
  if (isLoginUrl(page.url())) {
    throw new Error(`Still on login page after authentication flow: ${page.url()}`)
  }
  await page.waitForTimeout(1500)
}

async function mockDashboardApis(page) {
  await page.route('**/api/v1/plugin/Signal/dashboard', route => {
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ code: 0, data: dashboardFixture }) })
  })
  await page.route('**/api/v1/plugin/Signal/site_stat_chart', route => {
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ code: 0, data: siteChartFixture }) })
  })
  await page.route('**/api/v1/plugin/Signal/downloader_overview', route => {
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ code: 0, data: downloaderFixture }) })
  })
  await page.route('**/api/v1/plugin/Signal/run_seed_clean', route => {
    route.fulfill({ status: 200, contentType: 'application/json', body: JSON.stringify({ code: 1, msg: '自动删种未执行：未选择下载器' }) })
  })
}

async function openPluginDashboard(page) {
  const card = page.locator('.v-card--link').filter({ hasText: PLUGIN_NAME }).first()
  await card.waitFor({ timeout: 15000 })
  await card.click({ position: { x: 40, y: 30 } })
  await page.waitForSelector('.signal-dashboard', { timeout: 15000 })
  await page.waitForTimeout(800)
}

async function openSidebarDashboard(page) {
  await page.goto(`${BASE_URL}/#/plugin-app/Signal/main`, { waitUntil: 'domcontentloaded' })
  await page.waitForLoadState('networkidle', { timeout: 5000 }).catch(() => {})
  await page.waitForSelector('.dashboard-shell--sidebar .dashboard-canvas', { timeout: 15000 })
  await page.waitForTimeout(800)
}

async function openPluginConfig(page) {
  await page.locator('.signal-dashboard').getByRole('button', { name: /设置/ }).click()
  await page.waitForSelector('.signal-config', { timeout: 15000 })
  await page.waitForTimeout(600)
}

async function auditVisibleSidebarDashboard(page, scope) {
  await auditVisibleDashboard(page, scope)
  const shellResult = await page.evaluate((scope) => {
    const shell = document.querySelector('.dashboard-shell--sidebar')
    const canvas = document.querySelector('.dashboard-shell--sidebar .dashboard-canvas')
    const hiddenCompact = [...document.querySelectorAll('.sidebar-dashboard')].filter(el => {
      const r = el.getBoundingClientRect()
      const cs = getComputedStyle(el)
      return r.width > 0 && r.height > 0 && cs.display !== 'none' && cs.visibility !== 'hidden'
    }).length
    const shellBox = shell?.getBoundingClientRect()
    const canvasBox = canvas?.getBoundingClientRect()
    const clipped = [...document.querySelectorAll('.dashboard-shell--sidebar .metric-copy strong, .dashboard-shell--sidebar .action-btn-label')]
      .filter(el => {
        const r = el.getBoundingClientRect()
        return r.width > 0 && r.height > 0
      })
      .filter(el => el.scrollWidth > el.clientWidth + 3 || el.scrollHeight > el.clientHeight + 3)
      .map(el => ({
        text: (el.innerText || '').trim(),
        width: Math.round(el.getBoundingClientRect().width),
        scrollWidth: el.scrollWidth,
        clientWidth: el.clientWidth,
      }))
    const horizontalOverflow = [
      '.dashboard-shell--sidebar',
      '.dashboard-shell--sidebar .signal-frame',
      '.dashboard-shell--sidebar .dashboard-canvas',
      '.dashboard-shell--sidebar .metrics-panel',
      '.dashboard-shell--sidebar .site-panel',
      '.dashboard-shell--sidebar .command-panel',
      '.dashboard-shell--sidebar .download-panel',
      '.dashboard-shell--sidebar .runtime-panel',
    ]
      .flatMap(sel => [...document.querySelectorAll(sel)]
        .filter(el => {
          const r = el.getBoundingClientRect()
          const cs = getComputedStyle(el)
          return r.width > 0 && r.height > 0 && cs.display !== 'none' && cs.visibility !== 'hidden'
        })
        .map(el => ({
          selector: sel,
          deltaX: el.scrollWidth - el.clientWidth,
          width: Math.round(el.getBoundingClientRect().width),
        })))
      .filter(item => item.deltaX > 3)
    const outerFrameChrome = [
      '.dashboard-shell--sidebar',
      '.dashboard-shell--sidebar .signal-frame',
    ]
      .flatMap(sel => [...document.querySelectorAll(sel)]
        .filter(el => {
          const r = el.getBoundingClientRect()
          const cs = getComputedStyle(el)
          return r.width > 0 && r.height > 0 && cs.display !== 'none' && cs.visibility !== 'hidden'
        })
        .map(el => {
          const cs = getComputedStyle(el)
          return {
            selector: sel,
            borderTopWidth: Number.parseFloat(cs.borderTopWidth) || 0,
            borderRadius: Number.parseFloat(cs.borderTopLeftRadius) || 0,
            backgroundImage: cs.backgroundImage,
            backgroundColor: cs.backgroundColor,
            boxShadow: cs.boxShadow,
          }
        }))
      .filter(item => {
        const transparent = item.backgroundColor === 'rgba(0, 0, 0, 0)' || item.backgroundColor === 'transparent'
        return item.borderTopWidth > 0 || item.borderRadius > 0 || item.backgroundImage !== 'none' || !transparent || item.boxShadow !== 'none'
      })
    return {
      scope,
      shellWidth: shellBox ? Math.round(shellBox.width) : 0,
      viewportWidth: window.innerWidth,
      canvasWidth: canvasBox ? Math.round(canvasBox.width) : 0,
      hiddenCompact,
      clipped,
      horizontalOverflow,
      outerFrameChrome,
    }
  }, scope)
  assert.equal(shellResult.hiddenCompact, 0, `${scope} should render the full dashboard shell instead of the compact sidebar draft`)
  assert.ok(shellResult.shellWidth >= shellResult.viewportWidth * 0.68, `${scope} sidebar dashboard should occupy the MP content area with native breathing room`)
  assert.ok(shellResult.canvasWidth >= shellResult.shellWidth - 60, `${scope} dashboard canvas should fill the padded shell`)
  assert.deepEqual(shellResult.clipped, [], `${scope} sidebar-adapted dashboard should not clip key values or action labels`)
  assert.deepEqual(shellResult.horizontalOverflow, [], `${scope} sidebar-adapted dashboard should not keep hidden horizontal overflow`)
  assert.deepEqual(shellResult.outerFrameChrome, [], `${scope} sidebar dashboard should not render an extra outer card frame`)
  return

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
        left: Math.round(r.left),
        right: Math.round(r.right),
        width: Math.round(r.width),
        height: Math.round(r.height),
        deltaX: el.scrollWidth - el.clientWidth,
        deltaY: el.scrollHeight - el.clientHeight,
        overflowX: cs.overflowX,
        overflowY: cs.overflowY,
      }
    }
    const requiredSelectors = [
      '.sidebar-dashboard',
      '.sidebar-flow',
      '.sidebar-hero',
      '.sidebar-quick-grid',
      '.sidebar-section--site',
      '.sidebar-section--actions',
      '.sidebar-section--runtime',
    ]
    const missing = requiredSelectors.filter(sel => !document.querySelector(sel) || !isVisible(document.querySelector(sel)))

    const overflowSelectors = [
      '.sidebar-dashboard',
      '.sidebar-flow',
      '.sidebar-top',
      '.sidebar-hero',
      '.sidebar-quick-grid',
      '.sidebar-section',
      '.sidebar-site-summary',
      '.sidebar-site-list',
      '.sidebar-site-row',
      '.sidebar-action-groups',
      '.sidebar-action-group',
      '.sidebar-actions',
      '.sidebar-action',
      '.sidebar-download-list',
      '.sidebar-download-row',
      '.sidebar-runtime-list',
      '.sidebar-task',
    ]
    const horizontalOverflow = overflowSelectors
      .flatMap(sel => [...document.querySelectorAll(sel)].filter(isVisible).map(info))
      .filter(item => item.deltaX > 3)

    const offscreen = ['.sidebar-flow', '.sidebar-top', '.sidebar-section', '.sidebar-hero', '.sidebar-metric']
      .flatMap(sel => [...document.querySelectorAll(sel)].filter(isVisible).map(info))
      .filter(item => item.left < -2 || item.right > window.innerWidth + 2)

    const clippedActionLabels = [...document.querySelectorAll('.sidebar-action .action-btn-label')]
      .filter(isVisible)
      .filter(el => el.scrollWidth > el.clientWidth + 3 || el.scrollHeight > el.clientHeight + 3)
      .map(info)
    const clippedCompactValues = [...document.querySelectorAll('.sidebar-metric strong, .sidebar-site-summary strong')]
      .filter(isVisible)
      .filter(el => el.scrollWidth > el.clientWidth + 3 || el.scrollHeight > el.clientHeight + 3)
      .map(info)

    const actionGroups = [...document.querySelectorAll('.sidebar-action-group')].filter(isVisible).length
    const actionTotal = [...document.querySelectorAll('.sidebar-action')].filter(isVisible).length
    const actionBox = document.querySelector('.sidebar-action-groups')
    const actionBoxInfo = actionBox ? info(actionBox) : null
    const siteRows = [...document.querySelectorAll('.sidebar-site-row')].filter(isVisible).length
    const taskRows = [...document.querySelectorAll('.sidebar-task')].filter(isVisible).length

    return {
      scope,
      missing,
      horizontalOverflow,
      offscreen,
      clippedActionLabels,
      clippedCompactValues,
      actionGroups,
      actionTotal,
      actionBox: actionBoxInfo,
      siteRows,
      taskRows,
    }
  }, scope)

  assert.deepEqual(result.missing, [], `${scope} sidebar dashboard should render all primary sections`)
  assert.deepEqual(result.horizontalOverflow, [], `${scope} sidebar dashboard should not have internal horizontal overflow`)
  assert.deepEqual(result.offscreen, [], `${scope} sidebar dashboard sections should stay inside the viewport`)
  assert.deepEqual(result.clippedActionLabels, [], `${scope} sidebar manual action labels should fit their buttons`)
  assert.deepEqual(result.clippedCompactValues, [], `${scope} sidebar compact metrics should not clip key values`)
  assert.equal(result.actionGroups, 4, `${scope} sidebar dashboard should group manual actions`)
  assert.ok(result.actionTotal >= 10, `${scope} sidebar dashboard should expose all manual action buttons`)
  assert.equal(result.actionBox?.overflowY, 'visible', `${scope} sidebar action panel should not depend on an internal scroller`)
  assert.ok(result.siteRows >= 4, `${scope} sidebar site panel should keep useful rows visible`)
  assert.ok(result.taskRows >= 6, `${scope} sidebar runtime panel should keep useful rows visible`)
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
      '.signal-dashboard',
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
    const viewportHeight = window.innerHeight
    const viewportWidth = window.innerWidth
    const dashboard = document.querySelector('.signal-dashboard')
    const dashboardBox = dashboard ? dashboard.getBoundingClientRect() : null
    const dashboardStyle = dashboard ? getComputedStyle(dashboard) : null
    const isSidebarDashboard = dashboard?.classList.contains('dashboard-shell--sidebar')
    const clippedPanels = ['.alert-panel', '.site-panel', '.command-panel', '.download-panel', '.runtime-panel']
      .map(sel => document.querySelector(sel))
      .filter(el => el && isVisible(el))
      .map(el => ({ ...info(el), bottom: Math.round(el.getBoundingClientRect().bottom) }))
      .filter(item => {
        if (viewportWidth <= 760 || isSidebarDashboard) return false
        const dashboardCanScroll = dashboard && dashboard.scrollHeight > dashboard.clientHeight + 3 && /auto|scroll/.test(dashboardStyle.overflowY)
        return item.bottom > viewportHeight + 3 && !dashboardCanScroll
      })
    const collapsedPanels = ['.download-panel', '.runtime-panel']
      .map(sel => document.querySelector(sel))
      .filter(el => el && isVisible(el))
      .map(info)
      .filter(item => viewportWidth > 760 && item.height < 128)
    const dashboardViewport = dashboard ? {
      width: Math.round(dashboardBox.width),
      height: Math.round(dashboardBox.height),
      scrollHeight: dashboard.scrollHeight,
      clientHeight: dashboard.clientHeight,
      overflowY: dashboardStyle.overflowY,
      viewportHeight,
    } : null

    const scrollbarIssues = [
      '.signal-dashboard',
      '.site-legend',
      '.task-grid',
      '.health-grid',
      '.action-scroll',
    ]
      .map(sel => document.querySelector(sel))
      .filter(el => el && isVisible(el))
      .map(el => ({ ...info(el), width: getComputedStyle(el, '::-webkit-scrollbar').width, height: getComputedStyle(el, '::-webkit-scrollbar').height }))
      .filter(item => item.width !== '1px' || item.height !== '1px')

    return { scope, horizontalOverflow, clippedImportantText, clippedCommandLabelStyles, actionTotal, actionVisible, actionBox, clippedPanels, collapsedPanels, dashboardViewport, scrollbarIssues }
  }, scope)

  assert.deepEqual(result.horizontalOverflow, [], `${scope} dashboard should not have plugin-internal horizontal overflow`)
  assert.deepEqual(result.clippedImportantText, [], `${scope} dashboard should not clip important text`)
  assert.deepEqual(result.clippedCommandLabelStyles, [], `${scope} command button labels should never rely on hidden overflow or ellipsis`)
  assert.equal(result.actionVisible, result.actionTotal, `${scope} dashboard should render every manual action button`)
  assert.equal(result.actionBox?.overflowY, 'visible', `${scope} dashboard action buttons should not rely on an internal scroller`)
  assert.deepEqual(result.clippedPanels, [], `${scope} dashboard panels should not be clipped by short desktop viewports without a dashboard scroll container`)
  assert.deepEqual(result.collapsedPanels, [], `${scope} dashboard bottom panels should not collapse into title-only bars`)
  if (result.dashboardViewport && result.dashboardViewport.scrollHeight > result.dashboardViewport.clientHeight + 3) {
    assert.match(result.dashboardViewport.overflowY, /auto|scroll/, `${scope} dashboard overflow should stay reachable when content is taller than the viewport`)
  }
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
    const roots = [...document.querySelectorAll('.signal-config')].filter((el) => {
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
      '.signal-window',
      '.signal-pane',
      '.signal-columns-form',
      '.signal-table-wrap',
      '.signal-report-table-scroll',
      '.signal-report-table',
    ]
    const horizontalOverflow = overflowSelectors
      .flatMap(sel => [...document.querySelectorAll(sel)].filter(isVisible).map(info))
      .filter(item => item.deltaX > 3)

    const clippedLabels = [...document.querySelectorAll('.signal-config .v-label.v-field-label')]
      .filter(el => isVisible(el) && inConfig(el))
      .filter(el => (el.innerText || '').trim() && el.scrollWidth > el.clientWidth + 3)
      .map(info)
    const clippedHeaderText = [...document.querySelectorAll('.signal-config .signal-header .v-card-title, .signal-config .signal-header .v-card-subtitle')]
      .filter(el => isVisible(el) && inConfig(el))
      .filter(el => (el.innerText || '').trim() && (el.scrollWidth > el.clientWidth + 3 || el.scrollHeight > el.clientHeight + 3))
      .map(info)

    const verticalAccessIssues = [...document.querySelectorAll('.signal-card, .signal-body, .signal-content, .signal-window')]
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
  const navCount = await page.locator('.signal-nav-item').count()
  for (let i = 0; i < navCount; i += 1) {
    await page.locator('.signal-nav-item').nth(i).evaluate(el => {
      el.scrollIntoView({ block: 'center', inline: 'nearest' })
      el.click()
    })
    await page.waitForTimeout(100)

    const subCount = await page.locator('.signal-subtab').count()
    for (let j = 0; j < Math.max(1, subCount); j += 1) {
      const currentSubCount = await page.locator('.signal-subtab').count()
      if (currentSubCount > j) {
        await page.locator('.signal-subtab').nth(j).evaluate(el => {
          el.scrollIntoView({ block: 'nearest', inline: 'nearest' })
          el.click()
        })
        await page.waitForTimeout(80)
      }
      const title = await page.evaluate(() => {
        const main = document.querySelector('.signal-nav-item.v-list-item--active .v-list-item-title')?.innerText || ''
        const sub = document.querySelector('.signal-subtab--active')?.innerText || ''
        return `${main.trim()} / ${sub.trim()}`
      })
      await auditVisibleConfig(page, `${viewportName}: ${title}`)
    }
  }
}

async function main() {
  const launchOptions = { headless: true }
  if (CHROME_PATH) launchOptions.executablePath = CHROME_PATH
  const browser = await chromium.launch(launchOptions)
  try {
    for (const viewport of viewports) {
      const page = await browser.newPage({
        viewport: { width: viewport.width, height: viewport.height },
        deviceScaleFactor: 1,
        isMobile: viewport.width < 500,
      })
      await loginIfNeeded(page)
      await mockDashboardApis(page)
      await openSidebarDashboard(page)
      await auditVisibleSidebarDashboard(page, `${viewport.name}: sidebar dashboard`)
      await gotoPlugins(page)
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
