#!/usr/bin/env node
import assert from 'node:assert/strict'
import fs from 'node:fs'

import { actionMessageFromResponse, getPluginApi, getPluginApiRaw, postPluginApi, postPluginApiRaw } from '../plugins.v2/signal/src/shared/api.js'

async function main() {
  const api = {
    async get(path) {
      if (path.endsWith('/dashboard')) {
        return { data: { code: 0, data: { enabled: true, tasks: [] } } }
      }
      throw new Error(`unexpected GET ${path}`)
    },
    async post(path) {
      if (path.endsWith('/run_backup')) {
        return { data: { code: 1, msg: '自动备份执行失败', data: { reason: 'disk full' } } }
      }
      throw new Error(`unexpected POST ${path}`)
    },
  }

  const dashboard = await getPluginApi(api, 'dashboard')
  assert.deepEqual(dashboard, { enabled: true, tasks: [] }, 'GET helpers should unwrap data payloads for views')
  const dashboardRaw = await getPluginApiRaw(api, 'dashboard')
  assert.deepEqual(
    dashboardRaw,
    { code: 0, data: { enabled: true, tasks: [] } },
    'GET raw helper should preserve the full response envelope for skipped-state messages',
  )

  const action = await postPluginApi(api, 'run_backup')
  assert.equal(action.code, 1, 'POST helpers must preserve action status code')
  assert.equal(action.msg, '自动备份执行失败', 'POST helpers must preserve action message')
  assert.deepEqual(action.data, { reason: 'disk full' }, 'POST helpers must keep the response payload under data')

  const directEnvelopeApi = {
    async post(path) {
      if (path.endsWith('/create_tg_console_card')) {
        return { code: 0, msg: '融合通知卡已创建 #38834', data: { enabled: true, message_id: 38834, last_error: '' } }
      }
      throw new Error(`unexpected POST ${path}`)
    },
  }
  const directEnvelopeAction = await postPluginApi(directEnvelopeApi, 'create_tg_console_card')
  assert.equal(directEnvelopeAction.code, 0, 'POST helpers must preserve top-level MoviePilot action envelopes')
  assert.equal(directEnvelopeAction.msg, '融合通知卡已创建 #38834', 'POST helpers must not unwrap successful action envelopes into status data')

  const unwrappedFailureApi = {
    async post(path) {
      if (path.endsWith('/run_backup')) {
        return { enabled: false, back_path: '/config/plugins/Signal/Backup' }
      }
      throw new Error(`unexpected POST ${path}`)
    },
  }
  const unwrappedAction = await postPluginApi(unwrappedFailureApi, 'run_backup')
  assert.equal(unwrappedAction.code, undefined, 'fixture should simulate MoviePilot returning an unwrapped action payload')

  const raw = await postPluginApiRaw(api, 'run_backup')
  assert.deepEqual(raw, action, 'postPluginApiRaw remains compatible with the full action envelope')
  const directEnvelopeRaw = await postPluginApiRaw(directEnvelopeApi, 'create_tg_console_card')
  assert.deepEqual(directEnvelopeRaw, directEnvelopeAction, 'postPluginApiRaw must also preserve top-level action envelopes')
  const unwrappedCardStatusApi = {
    async post(path) {
      if (path.endsWith('/create_tg_console_card')) {
        return { enabled: true, chat_configured: true, message_id: 38843, last_error: '' }
      }
      throw new Error(`unexpected POST ${path}`)
    },
  }
  const unwrappedCardStatus = await postPluginApi(unwrappedCardStatusApi, 'create_tg_console_card')
  assert.equal(unwrappedCardStatus.code, 0, 'create card should infer success from an unwrapped healthy status payload')
  assert.equal(unwrappedCardStatus.msg, '融合通知卡已创建 #38843', 'create card should show a useful success message when MoviePilot unwraps data')
  assert.deepEqual(
    unwrappedCardStatus.data,
    { enabled: true, chat_configured: true, message_id: 38843, last_error: '' },
    'create card should preserve unwrapped status payload under data',
  )
  const unwrappedCardErrorApi = {
    async post(path) {
      if (path.endsWith('/create_tg_console_card')) {
        return { enabled: true, chat_configured: true, message_id: 0, last_error: 'Telegram sendRichMessage 返回失败：Bad Request' }
      }
      throw new Error(`unexpected POST ${path}`)
    },
  }
  const unwrappedCardError = await postPluginApi(unwrappedCardErrorApi, 'create_tg_console_card')
  assert.equal(unwrappedCardError.code, 1, 'create card should infer failure from an unwrapped status payload with last_error')
  assert.equal(
    actionMessageFromResponse(unwrappedCardError, '立即建卡'),
    'Telegram sendRichMessage 返回失败：Bad Request',
    'create card should surface last_error instead of the generic failed toast when MoviePilot unwraps data',
  )
  assert.equal(
    actionMessageFromResponse(
      { code: 1, msg: '', data: { last_error: 'Telegram sendRichMessage 返回失败：Bad Request: rich_message html is invalid' } },
      '立即建卡',
    ),
    'Telegram sendRichMessage 返回失败：Bad Request: rich_message html is invalid',
    'manual action messages should surface backend data.last_error when msg is empty',
  )
  assert.equal(
    actionMessageFromResponse(
      { code: 1, msg: '融合通知卡创建失败', data: { last_error: 'Telegram sendRichMessage 返回失败：Bad Request: rich_message html is invalid' } },
      '立即建卡',
    ),
    'Telegram sendRichMessage 返回失败：Bad Request: rich_message html is invalid',
    'manual action messages should prefer backend data.last_error over generic failure messages',
  )
  assert.equal(
    actionMessageFromResponse(
      { enabled: true, last_error: 'Telegram sendRichMessage 返回失败：Bad Request: rich_message html is invalid' },
      '立即建卡',
    ),
    'Telegram sendRichMessage 返回失败：Bad Request: rich_message html is invalid',
    'manual action messages should surface top-level last_error when MoviePilot returns an unwrapped status payload',
  )
  assert.equal(
    actionMessageFromResponse(
      { data: { code: 0, msg: '融合通知卡已创建 #38831', data: { message_id: 38831, last_error: '' } } },
      '立即建卡',
    ),
    '融合通知卡已创建 #38831',
    'manual action messages should unwrap MoviePilot response.data action envelopes before deciding success',
  )
  assert.equal(
    actionMessageFromResponse(
      {
        data: {
          code: 1,
          msg: '融合通知卡创建失败',
          data: { last_error: 'Telegram sendRichMessage 返回失败：Bad Request: rich_message html is invalid' },
        },
      },
      '立即建卡',
    ),
    'Telegram sendRichMessage 返回失败：Bad Request: rich_message html is invalid',
    'manual action messages should unwrap MoviePilot response.data failure envelopes before showing details',
  )
  assert.equal(
    actionMessageFromResponse({ code: 1, msg: '', data: { message: '后端任务返回了详细失败原因' } }, '立即执行'),
    '后端任务返回了详细失败原因',
    'manual action messages should surface backend data.message when msg is empty',
  )
  assert.equal(
    actionMessageFromResponse({ code: 1, msg: '', text: '纯文本失败原因' }, '立即执行'),
    '纯文本失败原因',
    'manual action messages should surface backend text when msg and data detail are empty',
  )

  const slowApi = {
    async post(path) {
      if (path.endsWith('/run_backup')) {
        return new Promise(resolve => {
          setTimeout(() => resolve({ data: { code: 0, msg: 'late', data: {} } }), 90)
        })
      }
      throw new Error(`unexpected POST ${path}`)
    },
  }
  await assert.rejects(
    () => postPluginApi(slowApi, 'run_backup', {}, 20),
    /timeout|超时/i,
    'POST action helpers should reject slow manual actions with a timeout',
  )
  await assert.rejects(
    () => postPluginApiRaw(slowApi, 'run_backup', {}, 20),
    /timeout|超时/i,
    'POST raw action helpers should reject slow manual actions with a timeout',
  )

  const posted = []
  const payloadApi = {
    async post(path, payload) {
      posted.push({ path, payload })
      return { data: { code: 0, msg: 'ok', data: {} } }
    },
  }
  await postPluginApi(payloadApi, 'run_plugin_uninstall', { plugin_uninstall_ids: ['AutoBackup'] })
  assert.deepEqual(
    posted,
    [{ path: 'plugin/Signal/run_plugin_uninstall', payload: { plugin_uninstall_ids: ['AutoBackup'] } }],
    'POST helpers should forward action payloads without unwrapping or dropping fields',
  )

  const config = fs.readFileSync('plugins.v2/signal/src/app/Config.vue', 'utf8')
  const pageSource = fs.readFileSync('plugins.v2/signal/src/app/Page.vue', 'utf8')
  const dashboardSource = fs.readFileSync('plugins.v2/signal/src/app/Dashboard.vue', 'utf8')
  assert.ok(
    pageSource.includes('res && res.code === 0') && !pageSource.includes('res.code === undefined'),
    'Page.vue manual actions must not treat a missing status code as success',
  )
  assert.ok(
    dashboardSource.includes('res && res.code === 0') && !dashboardSource.includes('res.code === undefined'),
    'Dashboard.vue manual actions must not treat a missing status code as success',
  )
  assert.ok(
    config.includes('res && res.code === 0') && !config.includes('res.code === undefined'),
    'Config.vue manual actions must not treat a missing status code as success',
  )
  assert.match(config, /function\s+buildActionPayload\s*\(\s*path\s*\)/, 'Config.vue should build per-action payloads')
  assert.match(
    config,
    /postPluginApi\(\s*props\.api\s*,\s*path\s*,\s*buildActionPayload\(path\)\s*\)/,
    'Config.vue runAction should send the current form payload for manual actions',
  )
  assert.ok(
    config.includes('actionMessageFromResponse') &&
      pageSource.includes('actionMessageFromResponse') &&
      dashboardSource.includes('actionMessageFromResponse'),
    'Config/Page/Dashboard manual actions should use the shared response message helper',
  )
  for (const field of [
    'plugin_uninstall_ids',
    'plugin_uninstall_remove_plugin',
    'plugin_uninstall_clear_config',
    'plugin_uninstall_clear_data',
    'plugin_uninstall_delete_source',
    'plugin_uninstall_notify',
    'plugin_uninstall_notify_type',
  ]) {
    assert.ok(config.includes(field), `plugin uninstall action payload should include ${field}`)
  }

  for (const fragment of [
    'backupArchives',
    'backupRestore',
    'loadBackupArchives',
    'previewBackupRestore',
    'runBackupRestore',
    'backup_archives',
    'preview_backup_restore',
    'run_backup_restore',
    'backupRestoreUnavailable',
    'backupRestoreUnavailableMessage',
    'restore_config',
    'restore_cookies',
    'restore_database',
    '确认覆盖当前配置',
    ':disabled="backupRestoreUnavailable || !backupRestore.archive"',
    'confirm: !!backupRestore.confirm',
  ]) {
    assert.ok(config.includes(fragment), `Config.vue should expose backup restore UI/API fragment: ${fragment}`)
  }

  for (const fragment of [
    'webdavBackupArchives',
    'webdavBackupRestore',
    'loadWebdavBackupArchives',
    'previewWebdavBackupRestore',
    'runWebdavBackupRestore',
    'webdav_backup_archives',
    'preview_webdav_backup_restore',
    'run_webdav_backup_restore',
    'webdavBackupRestoreUnavailable',
    'webdavBackupRestoreUnavailableMessage',
    'confirm: !!webdavBackupRestore.confirm',
  ]) {
    assert.ok(config.includes(fragment), `Config.vue should expose WebDAV backup restore UI/API fragment: ${fragment}`)
  }
}

main().catch(err => {
  console.error(err)
  process.exit(1)
})
