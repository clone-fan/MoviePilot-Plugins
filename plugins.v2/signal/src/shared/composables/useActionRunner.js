import { reactive, computed, ref } from 'vue'
import { actionMessageFromResponse, postPluginApi } from '../api.js'

function resolveMaybeRef(value) {
  if (typeof value === 'function') return value()
  if (value && typeof value === 'object' && 'value' in value) return value.value
  return value
}

export function usePanelActionRunner(options = {}) {
  const {
    api,
    getDisabledMessage = () => '',
    buildPayload = () => ({}),
    onSuccess = null,
    messageTimeoutMs = 5000,
  } = options
  const actionRunning = ref('')
  const runningActionLabel = ref('')
  const actionMessage = ref('')
  const actionOk = ref(true)
  let clearTimer = 0

  function scheduleClear() {
    if (clearTimer) clearTimeout(clearTimer)
    clearTimer = setTimeout(() => {
      actionMessage.value = ''
      clearTimer = 0
    }, messageTimeoutMs)
  }

  function showMessage(message, ok = false) {
    actionOk.value = ok
    actionMessage.value = message
    scheduleClear()
  }

  async function runAction(action) {
    const apiClient = resolveMaybeRef(api)
    if (!apiClient) return
    if (actionRunning.value) {
      showMessage(`${runningActionLabel.value || '当前动作'}正在执行，请等待完成。`, false)
      return
    }
    const path = action?.path
    if (!path) return
    const disabledMessage = getDisabledMessage(action) || ''
    if (disabledMessage) {
      showMessage(disabledMessage, false)
      return
    }
    actionRunning.value = path
    runningActionLabel.value = action?.label || path
    actionMessage.value = ''
    actionOk.value = true
    try {
      const res = await postPluginApi(apiClient, path, buildPayload(action))
      const ok = !!res && res.code === 0
      actionOk.value = ok
      actionMessage.value = actionMessageFromResponse(res, action.label)
      if (ok && typeof onSuccess === 'function') await onSuccess({ action, res, path })
    } catch (err) {
      actionOk.value = false
      actionMessage.value = actionMessageFromResponse({ code: 1, msg: err?.message }, action.label)
    } finally {
      actionRunning.value = ''
      runningActionLabel.value = ''
      scheduleClear()
    }
  }

  return { actionRunning, runningActionLabel, actionMessage, actionOk, runAction }
}

// Action 执行系统 — 手动动作运行、组件可用性检查、payload 构建
// 入参：form(reactive 配置对象), api(MP 插件 API 句柄), installedPlugins(ref 已安装插件列表), loadInstalledPlugins(函数)
export function useActionRunner(form, api, installedPlugins, loadInstalledPlugins) {
  const action = reactive({ running: '', message: '', ok: true })
  action.downloaderHelperPreview = null

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
  }

  const actionDisabledReason = computed(() => {
    if (!form.enabled) return '插件总开关未启用，手动动作已暂停。'
    return ''
  })

  const notificationLockedByFusion = computed(() => !!form.fusion_notify_enabled)

  function actionComponentEnabled(itemOrPath) {
    const path = typeof itemOrPath === 'string' ? itemOrPath : itemOrPath?.path
    const component = actionComponentMap[path]
    if (!component) return true
    return !!form[`${component}_enabled`]
  }

  function actionComponentDisabledMessage(path) {
    const component = actionComponentMap[path]
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
    const uninstalled = Array.isArray(res?.data?.uninstalled) ? res.data.uninstalled : []
    const removed = new Set(uninstalled
      .filter(item => item && item.success !== false)
      .map(item => String(item.plugin_id || item.id || item.value || ''))
      .filter(Boolean))
    await loadInstalledPlugins()
    const available = installedPluginValues()
    form.plugin_uninstall_ids = (Array.isArray(form.plugin_uninstall_ids) ? form.plugin_uninstall_ids : [])
      .filter(id => !removed.has(String(id)) && available.has(String(id)))
  }

  async function runAction(path, label) {
    if (action.running) return
    const disabledMessage = actionDisabledReason.value || actionComponentDisabledMessage(path) || actionDangerGateMessage(path)
    if (disabledMessage) {
      action.ok = false
      action.message = disabledMessage
      return
    }
    action.running = path
    action.message = ''
    try {
      const res = await postPluginApi(api, path, buildActionPayload(path))
      const ok = !!res && res.code === 0
      if (path === 'run_downloader_helper') {
        action.downloaderHelperPreview = res?.data?.confirm_required ? res.data : null
      }
      if (ok && path === 'run_plugin_uninstall') {
        await refreshAfterPluginUninstall(res)
      }
      action.ok = ok
      action.message = actionMessageFromResponse(res, label)
    } catch (err) {
      action.ok = false
      action.message = actionMessageFromResponse({ code: 1, msg: err?.message }, label)
    } finally {
      action.running = ''
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
