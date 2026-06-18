#!/usr/bin/env node
import assert from 'node:assert/strict'

import { getPluginApi, postPluginApi, postPluginApiRaw } from '../plugins.v2/agentopsassistant/src/components/api.js'

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

  const action = await postPluginApi(api, 'run_backup')
  assert.equal(action.code, 1, 'POST helpers must preserve action status code')
  assert.equal(action.msg, '自动备份执行失败', 'POST helpers must preserve action message')
  assert.deepEqual(action.data, { reason: 'disk full' }, 'POST helpers must keep the response payload under data')

  const raw = await postPluginApiRaw(api, 'run_backup')
  assert.deepEqual(raw, action, 'postPluginApiRaw remains compatible with the full action envelope')
}

main().catch(err => {
  console.error(err)
  process.exit(1)
})
