<script setup>
import { computed } from 'vue'
import ConfigCardBase from './ConfigCardBase.vue'
import ConfigFieldRow from './ConfigFieldRow.vue'

const props = defineProps({
  title: { type: String, required: true },
  note: { type: String, default: '' },
  icon: { type: String, default: 'mdi-calendar-clock' },
  fields: { type: Array, default: () => [] },
  values: { type: Object, required: true },
  disabled: { type: Boolean, default: false },
  locked: { type: Boolean, default: false },
  masterKey: { type: String, default: '' },
  scheduleKey: { type: String, default: '' },
  effectiveState: { type: String, default: '' },
  embedded: { type: Boolean, default: false },
})

const emit = defineEmits(['field-update'])

const moduleEnabled = computed(() => (
  props.masterKey ? props.values[props.masterKey] !== false : true
))
const scheduleEnabled = computed(() => (
  props.scheduleKey ? props.values[props.scheduleKey] !== false : moduleEnabled.value
))
const cronFields = computed(() => props.fields.filter(field => (
  field.control === 'cron' || field.key.endsWith('_cron')
)))
const statusLabel = computed(() => {
  if (props.effectiveState === 'plugin_disabled') return '已停用'
  if (props.locked) return '计划已接管'
  if (props.disabled) return '当前不可编辑'
  if (!moduleEnabled.value) return '模块未启用'
  if (!scheduleEnabled.value) return '定时未启用'
  return 'Cron 已启用'
})
const statusActive = computed(() => (
  props.effectiveState !== 'plugin_disabled' && !props.disabled && !props.locked && moduleEnabled.value && scheduleEnabled.value
))

function withScheduleState(field) {
  return {
    ...field,
    disabled: props.disabled || props.locked || !moduleEnabled.value || !scheduleEnabled.value || field.disabled,
  }
}

function updateField(field, value) {
  if (!field?.key) return
  props.values[field.key] = value
  emit('field-update', { field, value })
}
</script>

<template>
  <ConfigCardBase
    :title="title"
    :note="note"
    :icon="icon"
    :values="values"
    :fields="[]"
    :disabled="disabled"
    :locked="locked"
    card-type="schedule"
    marker="schedule"
    data-contract-marker="data-schedule-card"
    :data-effective-state="effectiveState || undefined"
    :embedded="embedded"
  >
    <template #actions>
      <span
        class="signal-schedule-card__status"
        :class="{ 'signal-schedule-card__status--off': !statusActive }"
        data-schedule-status
        role="status"
      >
        <VIcon :icon="statusActive ? 'mdi-check-circle-outline' : 'mdi-alert-outline'" size="16" />
        <span>{{ statusLabel }}</span>
      </span>
    </template>

    <div
      class="signal-schedule-card"
      data-schedule-card-body
      :data-schedule-master-key="masterKey || undefined"
      :data-schedule-key="scheduleKey || undefined"
      :data-schedule-enabled="scheduleEnabled ? 'true' : 'false'"
    >
      <section v-if="cronFields.length" class="signal-schedule-card__group" data-schedule-cron>
        <div class="signal-design-field-grid signal-design-field-grid--grid-2">
          <ConfigFieldRow
            v-for="field in cronFields"
            :key="field.key"
            :field="withScheduleState(field)"
            :model-value="values[field.key]"
            @update:model-value="value => updateField(field, value)"
          />
        </div>
      </section>

    </div>
  </ConfigCardBase>
</template>

<style scoped>
.signal-schedule-card {
  min-width: 0;
  display: grid;
  gap: 14px;
}

.signal-schedule-card__status {
  min-height: 30px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: rgb(var(--v-theme-success));
  font-size: 12px;
  font-weight: 750;
  white-space: nowrap;
}

.signal-schedule-card__status--off {
  color: rgb(var(--v-theme-warning));
}

.signal-schedule-card__group {
  min-width: 0;
  display: grid;
  gap: 8px;
}

.signal-schedule-card__group-head {
  min-width: 0;
  display: inline-flex;
  align-items: center;
  gap: 7px;
  color: var(--signal-config-text-secondary);
  font-size: 12px;
  font-weight: 760;
}
</style>
