<template>
  <div class="signal-pane">
    <VForm>
      <ModuleHero
        v-model:enabled="form.backup_enabled"
        icon="mdi-folder-arrow-up-outline"
        kicker="MP 自动备份"
        on-title="备份组件已启用"
        off-title="备份组件未启用"
        desc="组件开关控制手动备份|定时备份由下方独立开关控制"
        :count-label="`${form.backup_keep_count} 份保留`"
      />
      <SettingSection title="本地策略" note="备份时间、路径和保留份数集中配置">
        <VRow class="signal-setting-grid">
          <VCol cols="12" md="4">
            <VTextField v-model="form.backup_path" label="本地备份路径"
              prepend-inner-icon="mdi-folder-outline" :disabled="!form.backup_enabled" />
          </VCol>
          <VCol cols="12">
            <div class="d-flex align-center justify-space-between mb-1">
              <span class="text-body-2">本地保留份数</span>
              <VChip size="small" color="primary" variant="tonal">{{ form.backup_keep_count }} 份</VChip>
            </div>
            <VSlider v-model="form.backup_keep_count" :min="1" :max="30" :step="1"
              color="primary" thumb-label hide-details :disabled="!form.backup_enabled" />
          </VCol>
        </VRow>
      </SettingSection>
      <BackupRestorePanel
        title="一键恢复"
        note="从本插件生成的本地备份包恢复配置、Cookies 或数据库"
        :restore="backupRestore"
        :archives="backupArchives"
        :archives-loading="backupArchivesLoading"
        :restore-loading="backupRestoreLoading"
        :result="backupRestoreResult"
        :unavailable="backupRestoreUnavailable"
        :unavailable-message="backupRestoreUnavailableMessage"
        archive-label="选择备份包"
        archive-icon="mdi-archive-search-outline"
        no-data-text="暂无可恢复备份包"
        refresh-label="刷新列表"
        refresh-icon="mdi-refresh"
        confirm-label="确认覆盖当前配置"
        preview-label="预览恢复"
        run-label="一键恢复"
        run-icon="mdi-backup-restore"
        fallback-result-text="备份恢复已返回结果"
        @refresh="emit('loadBackupArchives')"
        @preview="emit('previewBackupRestore')"
        @run="emit('runBackupRestore')"
      />
    </VForm>
  </div>
</template>

<script setup>
import ModuleHero from "./ModuleHero"
import SettingSection from "./SettingSection"
import BackupRestorePanel from "./BackupRestorePanel.vue"

defineProps({
  form: { type: Object, required: true },
  backupRestoreUnavailable: { type: Boolean, default: false },
  backupRestoreUnavailableMessage: { type: String, default: "" },
  backupArchives: { type: Array, default: () => [] },
  backupArchivesLoading: { type: Boolean, default: false },
  backupRestoreLoading: { type: Boolean, default: false },
  backupRestoreResult: { type: Object, default: null },
  backupRestore: { type: Object, required: true },
})

const emit = defineEmits(["loadBackupArchives", "previewBackupRestore", "runBackupRestore"])
</script>
