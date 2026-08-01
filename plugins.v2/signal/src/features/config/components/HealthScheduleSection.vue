<template>
  <SettingSection title="巡检调度" note="配置定时开关、巡检周期、存储阈值和通知渠道">
    <div class="signal-health-scope-grid">
      <VTextField
        v-model.number="form.health_check_storage_threshold"
        label="存储阈值"
        type="number"
        class="signal-health-field-third"
        min="1"
        max="99"
        suffix="%"
        :disabled="!form.health_check_enabled"
      />
    </div>
  </SettingSection>
</template>

<script setup>
import SettingSection from './SettingSection'

defineProps({
  form: { type: Object, required: true },
})
</script>
