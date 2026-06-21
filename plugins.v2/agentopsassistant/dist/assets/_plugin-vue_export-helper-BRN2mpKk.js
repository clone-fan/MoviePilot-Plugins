function unwrapResponse(response) {
  const data = response?.data ?? response;
  if (data && typeof data === 'object' && 'data' in data) return data.data
  return data
}

const DEFAULT_PLUGIN_API_TIMEOUT_MS = 60000;

async function withTimeout(promise, path, timeoutMs = DEFAULT_PLUGIN_API_TIMEOUT_MS) {
  if (!Number.isFinite(timeoutMs) || timeoutMs <= 0) return promise

  let timer;
  try {
    return await Promise.race([
      promise,
      new Promise((_, reject) => {
        timer = setTimeout(() => {
          reject(new Error(`MoviePilot plugin API timeout/超时: ${path}`));
        }, timeoutMs);
      }),
    ])
  } finally {
    clearTimeout(timer);
  }
}

async function postPluginApi(api, path, payload = {}, timeoutMs = DEFAULT_PLUGIN_API_TIMEOUT_MS) {
  if (!api?.post) throw new Error('MoviePilot 插件 API 未就绪')
  const response = await withTimeout(api.post(`plugin/AgentOpsAssistant/${path}`, payload), path, timeoutMs);
  return response?.data ?? response
}

async function getPluginApi(api, path) {
  if (!api?.get) throw new Error('MoviePilot 插件 API 未就绪')
  const response = await api.get(`plugin/AgentOpsAssistant/${path}`);
  return unwrapResponse(response)
}

async function getPluginApiRaw(api, path) {
  if (!api?.get) throw new Error('MoviePilot 插件 API 未就绪')
  const response = await api.get(`plugin/AgentOpsAssistant/${path}`);
  return response?.data ?? response
}

const _export_sfc = (sfc, props) => {
  const target = sfc.__vccOpts || sfc;
  for (const [key, val] of props) {
    target[key] = val;
  }
  return target;
};

export { _export_sfc as _, getPluginApiRaw as a, getPluginApi as g, postPluginApi as p };
