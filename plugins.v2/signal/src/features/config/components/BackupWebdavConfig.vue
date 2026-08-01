<template>
  <div class="signal-pane">
    <VForm>
      <ModuleHero
        :enabled="webdavConfigured"
        icon="mdi-cloud-upload-outline"
        kicker="MP 自动备份"
        on-title="WebDAV 远端备份已启用"
        off-title="WebDAV 远端备份未启用"
        desc="本地备份完成后同步上传远端|按策略保留历史版本"
        :count-label="`${form.backup_webdav_max_count} 份保留`"
      />
      <SettingSection title="远端连接" note="WebDAV 地址、账号和密码">
        <VRow class="signal-setting-grid">
          <VCol cols="12" md="6">
            <VTextField v-model="form.backup_webdav_hostname" label="WebDAV 地址"
              placeholder="https://dav.example.com/backup" prepend-inner-icon="mdi-web"
              :disabled="!form.backup_enabled" />
          </VCol>
          <VCol cols="12" md="3">
            <VTextField v-model="form.backup_webdav_login" label="账号"
              :disabled="!form.backup_enabled" />
          </VCol>
          <VCol cols="12" md="3">
            <VTextField v-model="form.backup_webdav_password" label="密码"
              type="password" :disabled="!form.backup_enabled" />
          </VCol>
        </VRow>
      </SettingSection>
      <SettingSection title="远端策略" note="保留份数和连接校验">
        <VRow class="signal-setting-grid">
          <VCol cols="12" md="4">
            <VSelect v-model="form.backup_webdav_max_count" :items="keepCountPresets"
              label="远端保留份数" :disabled="!form.backup_enabled" />
          </VCol>
          <VCol cols="12" md="4">
            <VSwitch v-model="form.backup_webdav_digest_auth" color="primary" inset hide-details
              label="使用 Digest 认证" :disabled="!form.backup_enabled" />
          </VCol>
          <VCol cols="12" md="8">
            <VSwitch v-model="form.backup_webdav_disable_check" color="warning" inset hide-details
              label="跳过证书校验（自签名时启用）" :disabled="!form.backup_enabled" />
          </VCol>
        </VRow>
      </SettingSection>
      <BackupRestorePanel
        title="WebDAV 一键恢复"
        note="从远端备份包下载到本地后恢复配置、Cookies 或数据库"
        :restore="webdavBackupRestore"
        :archives="webdavBackupArchives"
        :archives-loading="webdavBackupArchivesLoading"
        :restore-loading="webdavBackupRestoreLoading"
        :result="webdavBackupRestoreResult"
        :unavailable="webdavBackupRestoreUnavailable"
        :unavailable-message="webdavBackupRestoreUnavailableMessage"
        archive-label="选择远端备份包"
        archive-icon="mdi-cloud-search-outline"
        no-data-text="暂无远端可恢复备份包"
        refresh-label="刷新远端"
        refresh-icon="mdi-cloud-sync-outline"
        confirm-label="确认下载并覆盖当前配置"
        preview-label="预览远端恢复"
        run-label="恢复远端备份"
        run-icon="mdi-cloud-refresh-outline"
        fallback-result-text="WebDAV 备份恢复已返回结果"
        @refresh="emit('loadWebdavBackupArchives')"
        @preview="emit('previewWebdavBackupRestore')"
        @run="emit('runWebdavBackupRestore')"
      />
    </VForm>
  </div>
</template>

<script setup>
import { computed } from "vue"
import ModuleHero from "./ModuleHero"
import SettingSection from "./SettingSection"
import BackupRestorePanel from "./BackupRestorePanel.vue"

const props = defineProps({
  form: { type: Object, required: true },
  keepCountPresets: { type: Array, default: () => [] },
  webdavBackupRestoreUnavailable: { type: Boolean, default: false },
  webdavBackupRestoreUnavailableMessage: { type: String, default: "" },
  webdavBackupArchives: { type: Array, default: () => [] },
  webdavBackupArchivesLoading: { type: Boolean, default: false },
  webdavBackupRestoreLoading: { type: Boolean, default: false },
  webdavBackupRestoreResult: { type: Object, default: null },
  webdavBackupRestore: { type: Object, required: true },
})

const webdavConfigured = computed(() => [
  props.form.backup_webdav_hostname,
  props.form.backup_webdav_login,
  props.form.backup_webdav_password,
].every(value => String(value || "").trim().length > 0))

const emit = defineEmits(["loadWebdavBackupArchives", "previewWebdavBackupRestore", "runWebdavBackupRestore"])
</script>
