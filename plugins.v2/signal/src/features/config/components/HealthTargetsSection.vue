<template>
  <SettingSection title="巡检目标" note="选择需要检查的项目、目标和日报存储展示范围">
    <div class="signal-health-scope-grid">
      <VSelect
        v-model="form.health_check_items"
        :items="healthCheckItems"
        class="signal-health-field-full signal-health-select"
        label="巡检项目"
        multiple
        chips
        closable-chips
        clearable
        hint="选择需要执行的健康检查项，留空或清空表示全部巡检"
        persistent-hint
        :disabled="!form.health_check_enabled"
      >
        <template #chip="{ item, props }">
          <VChip v-bind="props" class="signal-health-selection-chip" variant="tonal">
            {{ selectionTitle(item) }}
          </VChip>
        </template>
      </VSelect>
      <VSelect
        v-model="form.health_check_database_targets"
        :items="healthDatabaseTargets"
        class="signal-health-field-full signal-health-select"
        label="数据库"
        multiple
        chips
        closable-chips
        clearable
        :disabled="!form.health_check_enabled"
      >
        <template #chip="{ item, props }">
          <VChip v-bind="props" class="signal-health-selection-chip" variant="tonal">
            {{ selectionTitle(item) }}
          </VChip>
        </template>
      </VSelect>
      <VSelect
        v-model="form.health_check_storage_targets"
        :items="healthStorageTargets"
        class="signal-health-field-full signal-health-select"
        label="存储空间"
        multiple
        chips
        closable-chips
        clearable
        :disabled="!form.health_check_enabled"
      >
        <template #chip="{ item, props }">
          <VChip v-bind="props" class="signal-health-selection-chip" variant="tonal">
            {{ selectionTitle(item) }}
          </VChip>
        </template>
      </VSelect>
      <VSelect
        v-model="form.health_check_directory_targets"
        :items="healthDirectoryTargets"
        class="signal-health-field-full signal-health-select"
        label="目录权限"
        multiple
        chips
        closable-chips
        clearable
        :disabled="!form.health_check_enabled"
      >
        <template #chip="{ item, props }">
          <VChip v-bind="props" class="signal-health-selection-chip" variant="tonal">
            {{ selectionTitle(item) }}
          </VChip>
        </template>
      </VSelect>
    </div>
  </SettingSection>
</template>

<script setup>
import SettingSection from './SettingSection'

defineProps({
  form: { type: Object, required: true },
  healthCheckItems: { type: Array, default: () => [] },
  healthDatabaseTargets: { type: Array, default: () => [] },
  healthStorageTargets: { type: Array, default: () => [] },
  healthDirectoryTargets: { type: Array, default: () => [] },
  selectionTitle: { type: Function, default: (v) => v?.title ?? v },
})
</script>
