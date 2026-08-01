import { importShared } from './__federation_fn_import-JrT3xvdd.js';
import { a1 as useTheme } from './mdi-CTgwQT0_.js';

function unwrapResponse(response) {
  const data = response?.data ?? response;
  if (data && typeof data === 'object' && 'data' in data) return data.data
  return data
}

const DEFAULT_PLUGIN_API_TIMEOUT_MS = 60000;

function sanitizeActionMessage(value) {
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
  const inner = res?.data;
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
  const payload = response?.data ?? response;
  if (
    path === 'create_tg_console_card' &&
    payload &&
    typeof payload === 'object' &&
    !('code' in payload) &&
    !('msg' in payload) &&
    ('message_id' in payload || 'chat_configured' in payload || 'last_error' in payload)
  ) {
    const detail = String(payload.last_error || payload.error || payload.message || '').trim();
    if (detail) {
      return { code: 1, msg: '融合通知卡创建失败', data: payload }
    }
    const messageId = Number(payload.message_id || 0);
    if (messageId > 0) {
      return { code: 0, msg: `融合通知卡已创建 #${messageId}`, data: payload }
    }
  }
  if (isActionEnvelope(response)) return response
  if (isActionEnvelope(payload)) return payload
  return payload
}

function actionMessageFromResponse(res, label = '操作') {
  const payload = normalizeActionResponse(res);
  const ok = !!payload && payload.code === 0;
  const msg = String(payload?.msg ?? '').trim();
  const detailCandidates = [
    payload?.data?.last_error,
    payload?.data?.message,
    payload?.data?.error,
    payload?.last_error,
    payload?.message,
    payload?.error,
    payload?.text,
  ];
  const detail = detailCandidates.find(item => String(item ?? '').trim());
  if (ok && msg) return sanitizeActionMessage(msg)
  if (!ok && detail) return sanitizeActionMessage(detail)
  if (msg) return sanitizeActionMessage(msg)
  return sanitizeActionMessage(detail || `${label}已${ok ? '完成' : '失败'}`)
}

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
  return normalizePostActionResponse(path, response)
}

async function getPluginApi(api, path) {
  if (!api?.get) throw new Error('MoviePilot 插件 API 未就绪')
  const response = await api.get(`plugin/AgentOpsAssistant/${path}`);
  return unwrapResponse(response)
}

async function getPluginApiEnvelope(api, path) {
  if (!api?.get) throw new Error('MoviePilot 插件 API 未就绪')
  const response = await api.get(`plugin/AgentOpsAssistant/${path}`);
  return response?.data ?? response
}

const {reactive,computed: computed$1,ref} = await importShared('vue');

function resolveMaybeRef(value) {
  if (typeof value === 'function') return value()
  if (value && typeof value === 'object' && 'value' in value) return value.value
  return value
}

function usePanelActionRunner(options = {}) {
  const {
    api,
    getDisabledMessage = () => '',
    buildPayload = () => ({}),
    onSuccess = null,
    messageTimeoutMs = 5000,
  } = options;
  const actionRunning = ref('');
  const runningActionLabel = ref('');
  const actionMessage = ref('');
  const actionOk = ref(true);
  let clearTimer = 0;

  function scheduleClear() {
    if (clearTimer) clearTimeout(clearTimer);
    clearTimer = setTimeout(() => {
      actionMessage.value = '';
      clearTimer = 0;
    }, messageTimeoutMs);
  }

  function showMessage(message, ok = false) {
    actionOk.value = ok;
    actionMessage.value = message;
    scheduleClear();
  }

  async function runAction(action) {
    const apiClient = resolveMaybeRef(api);
    if (!apiClient) return
    if (actionRunning.value) {
      showMessage(`${runningActionLabel.value || '当前动作'}正在执行，请等待完成。`, false);
      return
    }
    const path = action?.path;
    if (!path) return
    const disabledMessage = getDisabledMessage(action) || '';
    if (disabledMessage) {
      showMessage(disabledMessage, false);
      return
    }
    actionRunning.value = path;
    runningActionLabel.value = action?.label || path;
    actionMessage.value = '';
    actionOk.value = true;
    try {
      const res = await postPluginApi(apiClient, path, buildPayload(action));
      const ok = !!res && res.code === 0;
      actionOk.value = ok;
      actionMessage.value = actionMessageFromResponse(res, action.label);
      if (ok && typeof onSuccess === 'function') await onSuccess({ action, res, path });
    } catch (err) {
      actionOk.value = false;
      actionMessage.value = actionMessageFromResponse({ code: 1, msg: err?.message }, action.label);
    } finally {
      actionRunning.value = '';
      runningActionLabel.value = '';
      scheduleClear();
    }
  }

  return { actionRunning, runningActionLabel, actionMessage, actionOk, runAction }
}

// Action 执行系统 — 手动动作运行、组件可用性检查、payload 构建
// 入参：form(reactive 配置对象), api(MP 插件 API 句柄), installedPlugins(ref 已安装插件列表), loadInstalledPlugins(函数)
function useActionRunner(form, api, installedPlugins, loadInstalledPlugins) {
  const action = reactive({ running: '', message: '', ok: true });
  action.downloaderHelperPreview = null;

  // action path → config key 前缀映射
  const actionComponentMap = {
    create_tg_console_card: 'fusion_notify',
    run_daily_report: 'fusion_notify',

    run_subscribe_reminder: 'subscribe_reminder',
    run_site_stat: 'site_stat',
    run_health_check: 'health_check',
    subfill_clear_history: 'subfill',
    subfill_clear_handled: 'subfill',
    run_backup: 'backup',
    preview_backup_restore: 'backup',
    run_backup_restore: 'backup',
    run_log_clean: 'log_clean',
    preview_log_clean: 'log_clean',
    run_mp_update: 'mp_update',
    run_market_update: 'market_update',
    run_seed_clean: 'seedclean',
    preview_downloader_helper: 'dltag',
    run_downloader_helper: 'dltag',
  };

  const actionDisabledReason = computed$1(() => {
    if (!form.enabled) return '插件总开关未启用，手动动作已暂停。'
    return ''
  });

  const notificationLockedByFusion = computed$1(() => !!form.fusion_notify_enabled);

  function actionComponentEnabled(itemOrPath) {
    const path = typeof itemOrPath === 'string' ? itemOrPath : itemOrPath?.path;
    const component = actionComponentMap[path];
    if (!component) return true
    return !!form[`${component}_enabled`]
  }

  function actionComponentDisabledMessage(path) {
    const component = actionComponentMap[path];
    if (!component || actionComponentEnabled(path)) return ''
    return '当前组件未启用，手动动作已暂停。'
  }

  function actionDangerGateMessage(path) {
    if (path !== 'run_plugin_uninstall') return ''
    if (!Array.isArray(form.plugin_uninstall_ids) || form.plugin_uninstall_ids.length === 0) {
      return '请先选择要卸载的插件。'
    }
    return ''
  }

  function buildActionPayload(path) {
    if (path === 'run_downloader_helper' && action.downloaderHelperPreview?.scope_token) {
      return {
        dltag_confirm: true,
        dltag_preview_token: action.downloaderHelperPreview.scope_token,
      }
    }
    if (path === 'run_seed_clean') {
      return {
        seedclean_confirm: true,
      }
    }
    if (path !== 'run_plugin_uninstall') return {}
    return {
      plugin_uninstall_ids: Array.isArray(form.plugin_uninstall_ids) ? [...form.plugin_uninstall_ids] : [],
      plugin_uninstall_remove_plugin: !!form.plugin_uninstall_remove_plugin,
      plugin_uninstall_clear_config: !!form.plugin_uninstall_clear_config,
      plugin_uninstall_clear_data: !!form.plugin_uninstall_clear_data,
      plugin_uninstall_delete_source: !!form.plugin_uninstall_delete_source,
      plugin_uninstall_confirm: true,
    }
  }

  function installedPluginValues() {
    return new Set((installedPlugins.value || []).map(item => String(item?.value ?? item?.id ?? item?.title ?? item ?? '')))
  }

  async function refreshAfterPluginUninstall(res) {
    const uninstalled = Array.isArray(res?.data?.uninstalled) ? res.data.uninstalled : [];
    const removed = new Set(uninstalled
      .filter(item => item && item.success !== false)
      .map(item => String(item.plugin_id || item.id || item.value || ''))
      .filter(Boolean));
    await loadInstalledPlugins();
    const available = installedPluginValues();
    form.plugin_uninstall_ids = (Array.isArray(form.plugin_uninstall_ids) ? form.plugin_uninstall_ids : [])
      .filter(id => !removed.has(String(id)) && available.has(String(id)));
  }

  async function runAction(path, label) {
    if (action.running) return
    const disabledMessage = actionDisabledReason.value || actionComponentDisabledMessage(path) || actionDangerGateMessage(path);
    if (disabledMessage) {
      action.ok = false;
      action.message = disabledMessage;
      return
    }
    action.running = path;
    action.message = '';
    try {
      const res = await postPluginApi(api, path, buildActionPayload(path));
      const ok = !!res && res.code === 0;
      if (path === 'run_downloader_helper') {
        action.downloaderHelperPreview = res?.data?.confirm_required ? res.data : null;
      }
      if (ok && path === 'run_plugin_uninstall') {
        await refreshAfterPluginUninstall(res);
      }
      action.ok = ok;
      action.message = actionMessageFromResponse(res, label);
    } catch (err) {
      action.ok = false;
      action.message = actionMessageFromResponse({ code: 1, msg: err?.message }, label);
    } finally {
      action.running = '';
    }
  }

  return {
    action,
    actionComponentMap,
    actionDisabledReason,
    notificationLockedByFusion,
    actionComponentEnabled,
    actionComponentDisabledMessage,
    actionDangerGateMessage,
    buildActionPayload,
    runAction,
  }
}

const {computed} = await importShared('vue');

const supportedThemes = ['transparent', 'dark', 'light', 'purple'];

function normalizeThemeName(value) {
  const name = String(value || '').toLowerCase();
  return supportedThemes.find(theme => name.includes(theme)) || 'dark'
}

// Federation roots use this class instead of relying on Vuetify's .v-theme--*
// selectors, which are removed from plugin CSS during the MoviePilot build.
function useAgentOpsTheme() {
  const vuetifyTheme = useTheme();
  const themeName = computed(() => normalizeThemeName(vuetifyTheme.global.name.value));
  const rootThemeClass = computed(() => `agentops-theme--${themeName.value}`);

  return { themeName, rootThemeClass }
}

export { useActionRunner as a, getPluginApiEnvelope as b, usePanelActionRunner as c, getPluginApi as g, postPluginApi as p, useAgentOpsTheme as u };
