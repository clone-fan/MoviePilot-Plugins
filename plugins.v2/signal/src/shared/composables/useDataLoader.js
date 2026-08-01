import { ref } from 'vue'
import { getPluginApi } from '../api'

// 远程数据加载 — 插件列表 / TG 控制台 / 插件市场 / 下载器 / 媒体服务器
// 入参：api(MP 插件 API 句柄)
export function useDataLoader(api) {
  // 已安装插件列表（插件卸载用）
  const installedPlugins = ref([])
  const installedLoading = ref(false)
  async function loadInstalledPlugins() {
    installedLoading.value = true
    try {
      const res = await getPluginApi(api, 'installed_plugins')
      installedPlugins.value = Array.isArray(res) ? res : (res?.data || [])
    } catch {
      installedPlugins.value = []
    } finally {
      installedLoading.value = false
    }
  }

  // TG 控制台状态
  const tgConsoleStatus = ref({})
  const tgConsoleLoading = ref(false)
  async function loadTgConsoleStatus() {
    tgConsoleLoading.value = true
    try {
      const res = await getPluginApi(api, 'tg_console_status')
      tgConsoleStatus.value = res?.data || res || {}
    } catch (err) {
      tgConsoleStatus.value = { last_error: err?.message || '状态读取失败' }
    } finally {
      tgConsoleLoading.value = false
    }
  }

  // 插件库仓库（更新黑名单用）
  const pluginMarkets = ref([])
  const marketsLoading = ref(false)
  async function loadPluginMarkets() {
    marketsLoading.value = true
    try {
      const res = await getPluginApi(api, 'plugin_markets')
      pluginMarkets.value = Array.isArray(res) ? res : (res?.data || [])
    } catch {
      pluginMarkets.value = []
    } finally {
      marketsLoading.value = false
    }
  }

  // 下载器列表（自动删种用）
  const downloaderOptions = ref([])
  const downloadersLoading = ref(false)
  async function loadDownloaders() {
    downloadersLoading.value = true
    try {
      const res = await getPluginApi(api, 'downloaders')
      downloaderOptions.value = Array.isArray(res) ? res : (res?.data || [])
    } catch {
      downloaderOptions.value = []
    } finally {
      downloadersLoading.value = false
    }
  }

  // 媒体服务器列表（媒体库通知按服务器过滤用）
  const mediaserverOptions = ref([])
  const mediaserversLoading = ref(false)
  async function loadMediaservers() {
    mediaserversLoading.value = true
    try {
      const res = await getPluginApi(api, 'mediaservers')
      mediaserverOptions.value = Array.isArray(res) ? res : (res?.data || [])
    } catch {
      mediaserverOptions.value = []
    } finally {
      mediaserversLoading.value = false
    }
  }

  // 一键加载全部
  function loadAll() {
    return Promise.allSettled([
      loadInstalledPlugins(),
      loadTgConsoleStatus(),
      loadPluginMarkets(),
      loadDownloaders(),
      loadMediaservers(),
    ])
  }

  return {
    installedPlugins, installedLoading, loadInstalledPlugins,
    tgConsoleStatus, tgConsoleLoading, loadTgConsoleStatus,
    pluginMarkets, marketsLoading, loadPluginMarkets,
    downloaderOptions, downloadersLoading, loadDownloaders,
    mediaserverOptions, mediaserversLoading, loadMediaservers,
    loadAll,
  }
}
