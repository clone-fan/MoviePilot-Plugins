import { configSchemaFields } from './config-schema.js'
import { normalizeCurrentConfig } from './config-normalization.js'

const currentConfigKeys = Object.freeze(configSchemaFields.map(field => field.key))

export function buildConfigSavePayload(form = {}) {
  const normalized = normalizeCurrentConfig(form)
  const payload = {}
  for (const key of currentConfigKeys) {
    if (Object.prototype.hasOwnProperty.call(normalized, key)) payload[key] = normalized[key]
  }
  return payload
}

export function emitConfigSave(emit, form = {}) {
  const payload = buildConfigSavePayload(form)
  emit('save', payload)
  return payload
}

export function serializeConfigSavePayload(payload = {}) {
  return JSON.stringify(payload ?? {})
}

export function reloadConfigSavePayload(serializedPayload = '{}') {
  const reloaded = JSON.parse(serializedPayload || '{}')
  if (!reloaded || typeof reloaded !== 'object' || Array.isArray(reloaded)) return {}
  return reloaded
}

export function applyConfigSavePayload(target = {}, payload = {}) {
  const reloaded = reloadConfigSavePayload(serializeConfigSavePayload(payload))
  Object.keys(target).forEach(key => delete target[key])
  Object.assign(target, reloaded)
  return target
}
