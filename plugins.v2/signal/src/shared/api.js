export function unwrapResponse(response) {
  const data = response?.data ?? response
  if (data && typeof data === 'object' && 'data' in data) return data.data
  return data
}

export const DEFAULT_PLUGIN_API_TIMEOUT_MS = 60000

export function sanitizeActionMessage(value) {
  return String(value ?? '')
    .replace(/bot\d{5,}:[A-Za-z0-9_-]{20,}/g, 'bot***')
    .replace(/\d{5,}:[A-Za-z0-9_-]{20,}/g, '***TOKEN***')
}

function normalizeActionResponse(res) {
  if (
    res &&
    typeof res === 'object' &&
    ('code' in res || 'msg' in res)
  ) {
    return res
  }
  const inner = res?.data
  if (
    inner &&
    typeof inner === 'object' &&
    ('code' in inner || 'msg' in inner || 'last_error' in inner || 'error' in inner || 'message' in inner)
  ) {
    return inner
  }
  return res
}

function isActionEnvelope(value) {
  return !!(
    value &&
    typeof value === 'object' &&
    ('code' in value || 'msg' in value || 'last_error' in value || 'error' in value || 'message' in value)
  )
}

function normalizePostActionResponse(path, response) {
  const payload = response?.data ?? response
  if (
    path === 'create_tg_console_card' &&
    payload &&
    typeof payload === 'object' &&
    !('code' in payload) &&
    !('msg' in payload) &&
    ('message_id' in payload || 'chat_configured' in payload || 'last_error' in payload)
  ) {
    const detail = String(payload.last_error || payload.error || payload.message || '').trim()
    if (detail) {
      return { code: 1, msg: '融合通知卡创建失败', data: payload }
    }
    const messageId = Number(payload.message_id || 0)
    if (messageId > 0) {
      return { code: 0, msg: `融合通知卡已创建 #${messageId}`, data: payload }
    }
  }
  if (isActionEnvelope(response)) return response
  if (isActionEnvelope(payload)) return payload
  return payload
}

export function actionMessageFromResponse(res, label = '操作') {
  const payload = normalizeActionResponse(res)
  const ok = !!payload && payload.code === 0
  const msg = String(payload?.msg ?? '').trim()
  const detailCandidates = [
    payload?.data?.last_error,
    payload?.data?.message,
    payload?.data?.error,
    payload?.last_error,
    payload?.message,
    payload?.error,
    payload?.text,
  ]
  const detail = detailCandidates.find(item => String(item ?? '').trim())
  if (ok && msg) return sanitizeActionMessage(msg)
  if (!ok && detail) return sanitizeActionMessage(detail)
  if (msg) return sanitizeActionMessage(msg)
  return sanitizeActionMessage(detail || `${label}已${ok ? '完成' : '失败'}`)
}

export async function withTimeout(promise, path, timeoutMs = DEFAULT_PLUGIN_API_TIMEOUT_MS) {
  if (!Number.isFinite(timeoutMs) || timeoutMs <= 0) return promise

  let timer
  try {
    return await Promise.race([
      promise,
      new Promise((_, reject) => {
        timer = setTimeout(() => {
          reject(new Error(`MoviePilot plugin API timeout/超时: ${path}`))
        }, timeoutMs)
      }),
    ])
  } finally {
    clearTimeout(timer)
  }
}

export async function postPluginApi(api, path, payload = {}, timeoutMs = DEFAULT_PLUGIN_API_TIMEOUT_MS) {
  if (!api?.post) throw new Error('MoviePilot 插件 API 未就绪')
  const response = await withTimeout(api.post(`plugin/Signal/${path}`, payload), path, timeoutMs)
  return normalizePostActionResponse(path, response)
}

// 返回完整响应信封 {code, msg, data, text}，用于需要 text 预览正文的场景
export async function postPluginApiRaw(api, path, payload = {}, timeoutMs = DEFAULT_PLUGIN_API_TIMEOUT_MS) {
  if (!api?.post) throw new Error('MoviePilot 插件 API 未就绪')
  const response = await withTimeout(api.post(`plugin/Signal/${path}`, payload), path, timeoutMs)
  return normalizePostActionResponse(path, response)
}

export async function getPluginApi(api, path) {
  if (!api?.get) throw new Error('MoviePilot 插件 API 未就绪')
  const response = await api.get(`plugin/Signal/${path}`)
  return unwrapResponse(response)
}

export async function getPluginApiEnvelope(api, path) {
  if (!api?.get) throw new Error('MoviePilot 插件 API 未就绪')
  const response = await api.get(`plugin/Signal/${path}`)
  return response?.data ?? response
}

export async function getPluginApiRaw(api, path) {
  return getPluginApiEnvelope(api, path)
}
