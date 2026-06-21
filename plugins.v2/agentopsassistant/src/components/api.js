export function unwrapResponse(response) {
  const data = response?.data ?? response
  if (data && typeof data === 'object' && 'data' in data) return data.data
  return data
}

export const DEFAULT_PLUGIN_API_TIMEOUT_MS = 60000

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
  const response = await withTimeout(api.post(`plugin/AgentOpsAssistant/${path}`, payload), path, timeoutMs)
  return response?.data ?? response
}

// 返回完整响应信封 {code, msg, data, text}，用于需要 text 预览正文的场景
export async function postPluginApiRaw(api, path, payload = {}, timeoutMs = DEFAULT_PLUGIN_API_TIMEOUT_MS) {
  if (!api?.post) throw new Error('MoviePilot 插件 API 未就绪')
  const response = await withTimeout(api.post(`plugin/AgentOpsAssistant/${path}`, payload), path, timeoutMs)
  return response?.data ?? response
}

export async function getPluginApi(api, path) {
  if (!api?.get) throw new Error('MoviePilot 插件 API 未就绪')
  const response = await api.get(`plugin/AgentOpsAssistant/${path}`)
  return unwrapResponse(response)
}

export async function getPluginApiRaw(api, path) {
  if (!api?.get) throw new Error('MoviePilot 插件 API 未就绪')
  const response = await api.get(`plugin/AgentOpsAssistant/${path}`)
  return response?.data ?? response
}
