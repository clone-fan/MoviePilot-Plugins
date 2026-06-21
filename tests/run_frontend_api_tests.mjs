#!/usr/bin/env node
import assert from 'node:assert/strict'
import fs from 'node:fs'

import { getPluginApi, getPluginApiRaw, postPluginApi, postPluginApiRaw } from '../plugins.v2/agentopsassistant/src/components/api.js'

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

  const unwrappedFailureApi = {
    async post(path) {
      if (path.endsWith('/run_backup')) {
        return { enabled: false, back_path: '/config/plugins/AgentOpsAssistant/Backup' }
      }
      throw new Error(`unexpected POST ${path}`)
    },
  }
  const unwrappedAction = await postPluginApi(unwrappedFailureApi, 'run_backup')
  assert.equal(unwrappedAction.code, undefined, 'fixture should simulate MoviePilot returning an unwrapped action payload')

  const raw = await postPluginApiRaw(api, 'run_backup')
  assert.deepEqual(raw, action, 'postPluginApiRaw remains compatible with the full action envelope')

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
    [{ path: 'plugin/AgentOpsAssistant/run_plugin_uninstall', payload: { plugin_uninstall_ids: ['AutoBackup'] } }],
    'POST helpers should forward action payloads without unwrapping or dropping fields',
  )

  const config = fs.readFileSync('plugins.v2/agentopsassistant/src/components/Config.vue', 'utf8')
  const pageSource = fs.readFileSync('plugins.v2/agentopsassistant/src/components/Page.vue', 'utf8')
  const dashboardSource = fs.readFileSync('plugins.v2/agentopsassistant/src/components/Dashboard.vue', 'utf8')
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
  ]) {
    assert.ok(config.includes(fragment), `Config.vue should expose WebDAV backup restore UI/API fragment: ${fragment}`)
  }
}

main().catch(err => {
  console.error(err)
  process.exit(1)
})
