const longPath = '/volume1/media/downloads/very/long/path/that/should/wrap/instead/of-pushing-the-card-out-of-the-dashboard'

const dashboard = {
  enabled: true,
  summary: 'Local preview data',
  task_total: 7,
  task_on: 6,
  task_failed: 1,
  health: {
    time: '2026-07-02 09:42:00',
    success: false,
    output: [
      'Subscribe: OK',
      'Sites: OK',
      'Downloader: OK',
      `Directory permission: ${longPath} is not writable. Check mount and ACL settings.`,
      'Storage: OK',
    ].join('\n'),
  },
  tg_console: {
    enabled: true,
    chat_configured: true,
    message_id: 24518,
    notice_count: 18,
    pending_count: 2,
    date: '2026-07-02',
    notices: [{ time: '09:40' }],
    last_error: '',
  },
  tasks: [
    { key: 'fusion_notify', service_id: 'Signal.FusionNotify', name: '融合通知刷新', enabled: true, registered: true, state: '成功', color: 'success', schedule: '0 * * * *', last_time: '2026-07-02 09:40:00' },
    { key: 'health_check', service_id: 'Signal.HealthCheck', name: '健康巡查', enabled: true, registered: true, state: '失败', color: 'error', schedule: '0 */6 * * *', last_time: '2026-07-02 09:42:00' },
    { key: 'log_clean', service_id: 'Signal.LogClean', name: '插件日志清理', enabled: true, registered: true, state: '成功', color: 'success', schedule: '0 3 * * 1', last_time: '2026-07-01 03:00:00' },
    { key: 'backup', service_id: 'Signal.Backup', name: '自动备份', enabled: true, registered: true, state: '成功', color: 'success', schedule: '0 4 * * 1', last_time: '2026-07-01 04:00:00' },
    { key: 'mp_update', service_id: 'Signal.MPUpdate', name: 'MoviePilot更新检查', enabled: true, registered: true, state: '成功', color: 'success', schedule: '0 9 * * *', last_time: '2026-07-02 08:00:00' },
    { key: 'market_update', service_id: 'Signal.MarketUpdate', name: '插件库更新检查', enabled: false, registered: false, state: '已停用', color: 'default', schedule: '每 24 小时', last_time: '2026-07-02 08:10:00' },
    { key: 'seed_clean', service_id: 'Signal.SeedClean', name: '自动删种', enabled: true, registered: true, state: '无记录', color: 'default', schedule: '0 */12 * * *', last_time: '' },
  ],
}

const siteStatChart = {
  date: '2026-07-02',
  basis: 'today',
  data_valid: true,
  upload_total: 9134217728,
  download_total: 5211424768,
  sites: [
    { name: 'MTeam', upload: 3565158400, download: 1101004800 },
    { name: 'Site Alpha', upload: 2197815296, download: 1845493760 },
    { name: 'Site Beta', upload: 1321205760, download: 681574400 },
    { name: 'HDSky', upload: 1048576000, download: 943718400 },
    { name: 'Audiences', upload: 1001462272, download: 639631360 },
  ],
}

const downloaderOverview = {
  downloaders: [
    { name: 'qBittorrent - nas-main', connected: true, count: 8, active: 3, dl_speed: 7340032, up_speed: 1835008 },
    { name: 'Transmission - archive-node', connected: true, count: 2, active: 1, dl_speed: 1048576, up_speed: 419430 },
  ],
  message: '',
}

const listPayloads = {
  installed_plugins: [
    { id: 'Signal', plugin_name: 'Signal', plugin_version: '2.1.0', state: true },
    { id: 'TorrentRemover', plugin_name: 'Torrent remover', plugin_version: '1.2.0', state: true },
  ],
  tg_console_status: dashboard.tg_console,
  plugin_markets: [
    { name: 'MoviePilot-Plugins', url: 'local://MoviePilot-Plugins', enabled: true },
  ],
  downloaders: [
    { title: 'qBittorrent - nas-main', value: 'qb-main' },
    { title: 'Transmission - archive-node', value: 'tr-archive' },
  ],
  mediaservers: [
    { title: 'Emby', value: 'emby' },
    { title: 'Jellyfin', value: 'jellyfin' },
  ],
  backup_archives: [
    { title: 'signal-20260702-0900.zip', value: 'signal-20260702-0900.zip' },
  ],
  webdav_backup_archives: [],
}

for (const task of dashboard.tasks) task.effective_enabled = task.enabled !== false

export const previewApiCalls = []
const previewFailures = new Map()
const previewConfigScenarios = new Set(['baseline', 'new', 'empty', 'value', 'missing', 'error'])
let activePreviewConfigScenario = 'baseline'
let activePreviewConfigRecord = null
let activePreviewConfigGetError = false

function clonePreviewConfig(value) {
  if (value === null || value === undefined) return value
  return JSON.parse(JSON.stringify(value))
}

function isPluginConfigFormRequest(path) {
  return String(path || '')
    .replace(/^\/+|\/+$/g, '')
    .endsWith('plugin/form/Signal')
}

export function resetPreviewApiCalls() {
  previewApiCalls.splice(0, previewApiCalls.length)
  previewFailures.clear()
}

export function failNextPreviewApi(path, message = 'Local preview forced failure') {
  previewFailures.set(apiKey(path), message)
}

function apiKey(path) {
  return String(path || '').split('/').filter(Boolean).pop()
}

export const mockApi = {
  async get(path) {
    const key = apiKey(path)
    previewApiCalls.push({ method: 'GET', path: key })
    const failure = previewFailures.get(key)
    if (failure) {
      previewFailures.delete(key)
      throw new Error(failure)
    }
    if (isPluginConfigFormRequest(path)) {
      if (activePreviewConfigGetError) throw new Error('Local preview config GET failure')
      return { data: { model: clonePreviewConfig(activePreviewConfigRecord) } }
    }
    const payload = {
      dashboard,
      site_stat_chart: siteStatChart,
      downloader_overview: downloaderOverview,
      ...listPayloads,
    }[key]
    return { data: payload ?? { code: 0, msg: 'Local preview mock response', data: {} } }
  },

  async put(path, payload = {}) {
    const key = apiKey(path)
    previewApiCalls.push({ method: 'PUT', path: key, payload })
    return {
      data: {
        code: 0,
        msg: `Local preview accepted: ${key}`,
        data: { path: key, payload },
      },
    }
  },

  async post(path, payload = {}) {
    const key = apiKey(path)
    previewApiCalls.push({ method: 'POST', path: key, payload })
    if (['run_daily_report', 'run_downloader_helper'].includes(key)) await new Promise(resolve => setTimeout(resolve, 120))
    const failure = previewFailures.get(key)
    if (failure) {
      previewFailures.delete(key)
      return { data: { code: 1, msg: failure, data: { path: key } } }
    }
    if (key === 'run_daily_report') {
      dashboard.tg_console.message_id = Number(dashboard.tg_console.message_id || 24518) + 1
      dashboard.tg_console.date = '2026-07-02 10:00'
    }
    if (key === 'run_downloader_helper' && payload?.dltag_confirm !== true) {
      return {
        data: {
          code: 0,
          msg: '发现失效任务，请确认本次清理范围',
          data: {
            confirm_required: true,
            scope_token: 'local-downloader-helper-token',
            total: 2,
            items: [
              { downloader: 'qb-main', id: 'missing-qb', name: '失效电影', reason: '失效下载任务', delete_file: false },
              { downloader: 'tr-main', id: 'missing-tr', name: '失效剧集', reason: '失效下载任务', delete_file: false },
            ],
          },
        },
      }
    }
    return {
      data: {
        code: 0,
        msg: `Local preview accepted: ${key}`,
        data: { path: key, payload, message_id: 24518, chat_configured: true },
      },
    }
  },
  resetCalls: resetPreviewApiCalls,
  failNext: failNextPreviewApi,
}

export const previewConfig = {
  enabled: true,
  fusion_notify_enabled: true,
  health_check_enabled: true,
  site_stat_enabled: true,
  health_check_items: ['数据库', '存储空间', '目录权限'],
  health_check_storage_targets: ['storages', 'config', 'download', 'library'],
  health_check_directory_targets: ['config', 'plugin', 'download', 'library'],
  backup_enabled: true,
  backup_path: '/config/plugins/Signal/Backup',
  backup_keep_count: 5,
  mp_update_enabled: true,
  mp_update_schedule_enabled: true,
  market_update_enabled: false,
  market_update_schedule_enabled: false,
  plugin_uninstall_ids: ['Signal'],
  seedclean_enabled: true,
  seedclean_downloaders: ['qb-main'],
  seedclean_pathkeywords: longPath,
  dltag_enabled: true,
  dltag_downloaders: ['qb-main', 'tr-main'],
  dltag_tasks: ['tagging', 'seeding', 'cleanup'],
  dltag_cron: '0 */6 * * *',
  dltag_listen_download: true,
  dltag_listen_source_file: false,
  dltag_prefix: '站点-',
  dltag_all_tags: ['signal-managed'],
  dltag_excluded_tags: ['保留'],
  dltag_not_select_all_tag: '非全',
  dltag_tracker_mappings: 'tracker.example => 示例站点',
  dltag_source_delete_strategy: 'delayed',
  dltag_scheduled_notify: false,
  dltag_notify_type: 'Plugin',
  subfill_enabled: true,
  subfill_details: ['分辨率', '资源质量', '站点'],
  subfill_category_enabled: true,
  subfill_category_confs: [
    'category:动画/日番#resolution:1080p|x1080#include:.*CR(.*(简繁|简繁英))?.*(ADWeb|HHWEB|FROGWeb|CMCTV)#sites:观众,青蛙',
    'category:剧集/国产剧#resolution:4K|2160p|x2160#quality:WEB-?DL|WEB-?RIP#sites:憨憨,观众,青蛙#exclude:(?i)\\b(?:DV|HQ|IQ|60FPS|50FPS|120FPS)\\b',
  ].join('\n'),
}

export function configurePreviewConfigScenario(value = 'baseline') {
  const scenario = previewConfigScenarios.has(value) ? value : 'baseline'
  const baseConfig = clonePreviewConfig(previewConfig)
  activePreviewConfigScenario = scenario
  activePreviewConfigGetError = scenario === 'error'

  if (scenario === 'new' || scenario === 'error') {
    activePreviewConfigRecord = null
  } else if (scenario === 'empty') {
    activePreviewConfigRecord = { ...baseConfig, dltag_cron: '' }
  } else if (scenario === 'value') {
    activePreviewConfigRecord = { ...baseConfig, dltag_cron: '17 3 * * 2' }
  } else if (scenario === 'missing') {
    const { dltag_cron: _ignoredCron, ...configWithoutCron } = baseConfig
    activePreviewConfigRecord = configWithoutCron
  } else {
    activePreviewConfigRecord = baseConfig
  }

  return getPreviewConfigScenarioState()
}

export function getPreviewConfigScenarioState() {
  return {
    scenario: activePreviewConfigScenario,
    recordState: activePreviewConfigGetError
      ? 'unknown'
      : (activePreviewConfigRecord === null ? 'absent' : 'present'),
    initialConfig: clonePreviewConfig(activePreviewConfigRecord) || {},
  }
}

export function setPreviewConfigRecord(value) {
  activePreviewConfigRecord = clonePreviewConfig(value || {})
  activePreviewConfigGetError = false
  return getPreviewConfigScenarioState()
}

export function setPreviewMasterEnabled(value) {
  const enabled = value !== false
  dashboard.enabled = enabled
  dashboard.task_on = enabled ? dashboard.tasks.filter(task => task.enabled !== false).length : 0
  for (const task of dashboard.tasks) task.effective_enabled = enabled && task.enabled !== false
  previewConfig.enabled = enabled
}
