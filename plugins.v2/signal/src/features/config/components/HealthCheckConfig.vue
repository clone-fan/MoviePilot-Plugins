<template>
  <div class="signal-pane">
    <VForm class="signal-health-form">
      <ModuleHero
        v-model:enabled="form.health_check_enabled"
        icon="mdi-heart-pulse"
        kicker="MP 健康巡检"
        on-title="健康巡检已启用"
        off-title="健康巡检未启用"
        desc="定时检查站点、数据库、存储与目录|异常会在仪表盘和通知中展示"
        :count-label="`${healthSelectedCount} 项`"
      />

      <HealthScheduleSection
        :form="form"
        :notification-type-items="notificationTypeItems"
        :notification-locked-by-fusion="notificationLockedByFusion"
      />
      <HealthTargetsSection
        :form="form"
        :health-check-items="healthCheckItems"
        :health-database-targets="healthDatabaseTargets"
        :health-storage-targets="healthStorageTargets"
        :health-directory-targets="healthDirectoryTargets"
        :selection-title="selectionTitle"
      />
    </VForm>
  </div>
</template>

<script setup>
import ModuleHero from './ModuleHero'
import HealthScheduleSection from './HealthScheduleSection.vue'
import HealthTargetsSection from './HealthTargetsSection.vue'

defineProps({
  form: { type: Object, required: true },
  healthSelectedCount: { type: Number, default: 0 },
  healthCheckItems: { type: Array, default: () => [] },
  healthDatabaseTargets: { type: Array, default: () => [] },
  healthStorageTargets: { type: Array, default: () => [] },
  healthDirectoryTargets: { type: Array, default: () => [] },
  notificationTypeItems: { type: Array, default: () => [] },
  notificationLockedByFusion: { type: Boolean, default: false },
  selectionTitle: { type: Function, default: (v) => v?.title ?? v },
})
</script>
