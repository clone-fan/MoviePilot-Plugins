import { ref, reactive, computed } from 'vue'
import { getPluginApi, postPluginApi } from '../../../shared/api'

// 备份恢复逻辑 — 本地 + WebDAV 两套独立状态机
// 入参：form(reactive 配置对象), api(MP 插件 API 句柄)
export function useBackupRestore(form, api) {
  // --- 本地备份恢复 ---
  const backupArchives = ref([])
  const backupArchivesLoading = ref(false)
  const backupRestoreLoading = ref(false)
  const backupRestoreResult = ref(null)
  const backupRestore = reactive({
    archive: '',
    restore_config: true,
    restore_cookies: true,
    restore_database: true,
    confirm: false,
  })

  // --- WebDAV 备份恢复 ---
  const webdavBackupArchives = ref([])
  const webdavBackupArchivesLoading = ref(false)
  const webdavBackupRestoreLoading = ref(false)
  const webdavBackupRestoreResult = ref(null)
  const webdavBackupRestore = reactive({
    archive: '',
    restore_config: true,
    restore_cookies: true,
    restore_database: true,
    confirm: false,
  })

  // --- 可用性 computed ---
  const backupRestoreUnavailable = computed(() => !form.enabled || !form.backup_enabled)
  const backupRestoreUnavailableMessage = computed(() => {
    if (!form.enabled) return '插件总开关未启用，备份恢复已跳过。'
    if (!form.backup_enabled) return '自动备份组件未启用，备份恢复已跳过。'
    return ''
  })
  const webdavConfigured = computed(() => [
    form.backup_webdav_hostname,
    form.backup_webdav_login,
    form.backup_webdav_password,
  ].every(value => String(value || '').trim().length > 0))
  const webdavBackupRestoreUnavailable = computed(() => !form.enabled || !form.backup_enabled || !webdavConfigured.value)
  const webdavBackupRestoreUnavailableMessage = computed(() => {
    if (!form.enabled) return '插件总开关未启用，WebDAV 恢复已跳过。'
    if (!form.backup_enabled) return '自动备份组件未启用，WebDAV 恢复已跳过。'
    if (!webdavConfigured.value) return 'WebDAV 地址、账号或密码未完整配置，恢复已跳过。'
    return ''
  })

  // --- 数据加载 ---
  async function loadBackupArchives() {
    backupArchivesLoading.value = true
    try {
      const res = await getPluginApi(api, 'backup_archives')
      backupArchives.value = Array.isArray(res) ? res : (res?.data || [])
      if (!backupRestore.archive && backupArchives.value.length) {
        backupRestore.archive = backupArchives.value[0].name || backupArchives.value[0].value || ''
      }
    } catch {
      backupArchives.value = []
    } finally {
      backupArchivesLoading.value = false
    }
  }

  async function loadWebdavBackupArchives() {
    if (webdavBackupRestoreUnavailable.value) {
      webdavBackupArchives.value = []
      return
    }
    webdavBackupArchivesLoading.value = true
    try {
      const res = await getPluginApi(api, 'webdav_backup_archives')
      webdavBackupArchives.value = Array.isArray(res) ? res : (res?.data || [])
      if (!webdavBackupRestore.archive && webdavBackupArchives.value.length) {
        webdavBackupRestore.archive = webdavBackupArchives.value[0].name || webdavBackupArchives.value[0].value || ''
      }
    } catch {
      webdavBackupArchives.value = []
    } finally {
      webdavBackupArchivesLoading.value = false
    }
  }

  // --- payload 构建 ---
  function backupRestorePayload() {
    return {
      archive: backupRestore.archive,
      restore_config: !!backupRestore.restore_config,
      restore_cookies: !!backupRestore.restore_cookies,
      restore_database: !!backupRestore.restore_database,
      confirm: !!backupRestore.confirm,
    }
  }

  function webdavBackupRestorePayload() {
    return {
      archive: webdavBackupRestore.archive,
      restore_config: !!webdavBackupRestore.restore_config,
      restore_cookies: !!webdavBackupRestore.restore_cookies,
      restore_database: !!webdavBackupRestore.restore_database,
      confirm: !!webdavBackupRestore.confirm,
    }
  }

  // --- 预览 / 执行 ---
  async function previewBackupRestore() {
    if (!backupRestore.archive || backupRestoreLoading.value) return
    if (backupRestoreUnavailable.value) {
      backupRestoreResult.value = { code: 1, msg: backupRestoreUnavailableMessage.value }
      return
    }
    backupRestoreLoading.value = true
    try {
      backupRestoreResult.value = await postPluginApi(api, 'preview_backup_restore', backupRestorePayload())
    } catch (err) {
      backupRestoreResult.value = { code: 1, msg: err?.message || '备份恢复预览失败' }
    } finally {
      backupRestoreLoading.value = false
    }
  }

  async function previewWebdavBackupRestore() {
    if (!webdavBackupRestore.archive || webdavBackupRestoreLoading.value) return
    if (webdavBackupRestoreUnavailable.value) {
      webdavBackupRestoreResult.value = { code: 1, msg: webdavBackupRestoreUnavailableMessage.value }
      return
    }
    webdavBackupRestoreLoading.value = true
    try {
      webdavBackupRestoreResult.value = await postPluginApi(api, 'preview_webdav_backup_restore', webdavBackupRestorePayload())
    } catch (err) {
      webdavBackupRestoreResult.value = { code: 1, msg: err?.message || 'WebDAV 备份恢复预览失败' }
    } finally {
      webdavBackupRestoreLoading.value = false
    }
  }

  async function runWebdavBackupRestore() {
    if (!webdavBackupRestore.archive || !webdavBackupRestore.confirm || webdavBackupRestoreLoading.value) return
    if (webdavBackupRestoreUnavailable.value) {
      webdavBackupRestoreResult.value = { code: 1, msg: webdavBackupRestoreUnavailableMessage.value }
      return
    }
    webdavBackupRestoreLoading.value = true
    try {
      webdavBackupRestoreResult.value = await postPluginApi(api, 'run_webdav_backup_restore', webdavBackupRestorePayload())
      await loadBackupArchives()
    } catch (err) {
      webdavBackupRestoreResult.value = { code: 1, msg: err?.message || 'WebDAV 备份恢复执行失败' }
    } finally {
      webdavBackupRestore.confirm = false
      webdavBackupRestoreLoading.value = false
    }
  }

  async function runBackupRestore() {
    if (!backupRestore.archive || !backupRestore.confirm || backupRestoreLoading.value) return
    if (backupRestoreUnavailable.value) {
      backupRestoreResult.value = { code: 1, msg: backupRestoreUnavailableMessage.value }
      return
    }
    backupRestoreLoading.value = true
    try {
      backupRestoreResult.value = await postPluginApi(api, 'run_backup_restore', backupRestorePayload())
      await loadBackupArchives()
    } catch (err) {
      backupRestoreResult.value = { code: 1, msg: err?.message || '备份恢复执行失败' }
    } finally {
      backupRestore.confirm = false
      backupRestoreLoading.value = false
    }
  }

  return {
    backupArchives, backupArchivesLoading, backupRestoreLoading, backupRestoreResult, backupRestore,
    webdavBackupArchives, webdavBackupArchivesLoading, webdavBackupRestoreLoading, webdavBackupRestoreResult, webdavBackupRestore,
    backupRestoreUnavailable, backupRestoreUnavailableMessage,
    webdavBackupRestoreUnavailable, webdavBackupRestoreUnavailableMessage,
    loadBackupArchives, loadWebdavBackupArchives,
    previewBackupRestore, previewWebdavBackupRestore,
    runBackupRestore, runWebdavBackupRestore,
  }
}
