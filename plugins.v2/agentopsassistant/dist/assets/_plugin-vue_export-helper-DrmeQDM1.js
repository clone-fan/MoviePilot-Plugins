function unwrapResponse(response) {
  const data = response?.data ?? response;
  if (data && typeof data === 'object' && 'data' in data) return data.data
  return data
}

async function postPluginApi(api, path, payload = {}) {
  if (!api?.post) throw new Error('MoviePilot 插件 API 未就绪')
  const response = await api.post(`plugin/AgentOpsAssistant/${path}`, payload);
  return unwrapResponse(response)
}

// 返回完整响应信封 {code, msg, data, text}，用于需要 text 预览正文的场景
async function postPluginApiRaw(api, path, payload = {}) {
  if (!api?.post) throw new Error('MoviePilot 插件 API 未就绪')
  const response = await api.post(`plugin/AgentOpsAssistant/${path}`, payload);
  return response?.data ?? response
}

async function getPluginApi(api, path) {
  if (!api?.get) throw new Error('MoviePilot 插件 API 未就绪')
  const response = await api.get(`plugin/AgentOpsAssistant/${path}`);
  return unwrapResponse(response)
}

const _export_sfc = (sfc, props) => {
  const target = sfc.__vccOpts || sfc;
  for (const [key, val] of props) {
    target[key] = val;
  }
  return target;
};

export { _export_sfc as _, postPluginApiRaw as a, getPluginApi as g, postPluginApi as p };
