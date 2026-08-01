<template>
  <SettingSection :title="title" :note="note">
    <VRow class="signal-setting-grid">
      <VCol v-if="unavailable" cols="12">
        <VAlert type="warning" variant="tonal" density="comfortable">
          {{ unavailableMessage }}
        </VAlert>
      </VCol>
      <VCol cols="12" md="8">
        <VSelect v-model="restore.archive" :items="archives"
          item-title="name" item-value="name" :label="archiveLabel"
          :prepend-inner-icon="archiveIcon"
          :loading="archivesLoading" :disabled="unavailable || archivesLoading"
          :no-data-text="noDataText" />
      </VCol>
      <VCol cols="12" md="4" class="d-flex align-center">
        <VBtn variant="tonal" color="primary" block
          :prepend-icon="refreshIcon"
          :loading="archivesLoading"
          :disabled="unavailable"
          @click="emit('refresh')">
          {{ refreshLabel }}
        </VBtn>
      </VCol>
      <VCol cols="12" md="4">
        <VCheckbox v-model="restore.restore_config" hide-details
          label="恢复配置文件" :disabled="unavailable" />
      </VCol>
      <VCol cols="12" md="4">
        <VCheckbox v-model="restore.restore_cookies" hide-details
          label="恢复 Cookies" :disabled="unavailable" />
      </VCol>
      <VCol cols="12" md="4">
        <VCheckbox v-model="restore.restore_database" hide-details
          label="恢复数据库" :disabled="unavailable" />
      </VCol>
      <VCol cols="12">
        <VSwitch v-model="restore.confirm" color="error" inset hide-details
          :label="confirmLabel" :disabled="unavailable" />
      </VCol>
      <VCol cols="12" md="6">
        <VBtn variant="tonal" color="primary" block
          prepend-icon="mdi-file-eye-outline"
          :loading="restoreLoading"
          :disabled="unavailable || !restore.archive"
          @click="emit('preview')">
          {{ previewLabel }}
        </VBtn>
      </VCol>
      <VCol cols="12" md="6">
        <VBtn variant="flat" color="error" block
          :prepend-icon="runIcon"
          :loading="restoreLoading"
          :disabled="unavailable || !restore.archive || !restore.confirm"
          @click="emit('run')">
          {{ runLabel }}
        </VBtn>
      </VCol>
      <VCol v-if="result" cols="12">
        <VAlert :type="result.code === 0 ? 'success' : 'error'"
          variant="tonal" density="comfortable">
          {{ result.msg || result.text || fallbackResultText }}
        </VAlert>
      </VCol>
    </VRow>
  </SettingSection>
</template>

<script setup>
import SettingSection from "./SettingSection"

defineProps({
  title: { type: String, required: true },
  note: { type: String, default: "" },
  restore: { type: Object, required: true },
  archives: { type: Array, default: () => [] },
  archivesLoading: { type: Boolean, default: false },
  restoreLoading: { type: Boolean, default: false },
  result: { type: Object, default: null },
  unavailable: { type: Boolean, default: false },
  unavailableMessage: { type: String, default: "" },
  archiveLabel: { type: String, default: "选择备份包" },
  archiveIcon: { type: String, default: "mdi-archive-search-outline" },
  noDataText: { type: String, default: "暂无可恢复备份包" },
  refreshLabel: { type: String, default: "刷新列表" },
  refreshIcon: { type: String, default: "mdi-refresh" },
  confirmLabel: { type: String, default: "确认覆盖当前配置" },
  previewLabel: { type: String, default: "预览恢复" },
  runLabel: { type: String, default: "一键恢复" },
  runIcon: { type: String, default: "mdi-backup-restore" },
  fallbackResultText: { type: String, default: "备份恢复已返回结果" },
})

const emit = defineEmits(["refresh", "preview", "run"])
</script>