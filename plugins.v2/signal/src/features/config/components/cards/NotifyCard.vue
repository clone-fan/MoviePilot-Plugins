<script setup>
import { computed } from 'vue'
import ConfigCardBase from './ConfigCardBase.vue'
import ConfigFieldRow from './ConfigFieldRow.vue'
import { isReplicaFieldVisible } from '../../model/replica-field-bindings.js'

const props = defineProps({
  title: { type: String, required: true },
  note: { type: String, default: '' },
  icon: { type: String, default: 'mdi-bell-outline' },
  fields: { type: Array, default: () => [] },
  values: { type: Object, required: true },
  disabled: { type: Boolean, default: false },
  locked: { type: Boolean, default: false },
  channelOnlyLock: { type: Boolean, default: false },
  masterKey: { type: String, default: '' },
  resultKey: { type: String, default: '' },
  resultKeys: { type: Array, default: () => [] },
  dependencies: { type: Object, default: () => ({}) },
  offValues: { type: Array, default: () => ['none', 'off', ''] },
  effectiveState: { type: String, default: '' },
  embedded: { type: Boolean, default: false },
})

const emit = defineEmits(['field-update'])

function isMasterField(field) {
  return field.key.endsWith('_notify') ||
    field.key.endsWith('_enabled') ||
    field.key.endsWith('_poll_enabled')
}

function isChannelField(field) {
  if (isModeField(field)) return false
  return field.key.endsWith('_notify_type') ||
    field.key.endsWith('_msgtype') ||
    field.key === 'health_check_notify_type' ||
    field.key === 'msgnotify_notify_type' ||
    field.key === 'site_stat_notify_type'
}

function isModeField(field) {
  return false
}

function isRuleField(field) {
  return field.key.endsWith('_columns') ||
    field.key.endsWith('_types') ||
    field.key.endsWith('_servers') ||
    field.key.endsWith('_user_ids') ||
    field.key.endsWith('_max_notices')
}

const visibleFields = computed(() => props.fields.filter(field => isReplicaFieldVisible(field, props.values)))
const masterFields = computed(() => visibleFields.value.filter(isMasterField))
const channelFields = computed(() => visibleFields.value.filter(isChannelField))
const modeFields = computed(() => visibleFields.value.filter(isModeField))
const ruleFields = computed(() => visibleFields.value.filter(isRuleField))
const detailFields = computed(() => visibleFields.value.filter(field => (
  !isMasterField(field) && !isChannelField(field) && !isModeField(field) && !isRuleField(field)
)))
const primaryMasterField = computed(() => masterFields.value[0] || null)
const notificationLocked = computed(() => props.locked)
const notificationResultKeys = computed(() => [...new Set([
  props.resultKey,
  ...props.resultKeys,
].filter(Boolean))])
const moduleEnabled = computed(() => (
  props.masterKey ? props.values[props.masterKey] !== false : true
))
const notificationEnabled = computed(() => {
  if (props.disabled || (props.locked && !props.channelOnlyLock) || !moduleEnabled.value) return false
  if (
    notificationResultKeys.value.length &&
    notificationResultKeys.value.every(key => props.values[key] === false)
  ) return false
  const primaryMode = modeFields.value[0]
  if (primaryMode) {
    const value = props.values[primaryMode.key]
    if (props.offValues.includes(value == null ? '' : String(value))) return false
  }
  if (notificationResultKeys.value.length) return true
  if (primaryMasterField.value) return props.values[primaryMasterField.value.key] !== false
  const primaryChannel = channelFields.value[0]
  if (!primaryChannel) return true
  const value = props.values[primaryChannel.key]
  return !props.offValues.includes(value == null ? '' : String(value))
})
const statusLabel = computed(() => {
  if (props.effectiveState === 'plugin_disabled') return '已停用'
  if (notificationLocked.value && props.channelOnlyLock) return '通知渠道已接管'
  if (notificationLocked.value) return '融合通知已接管'
  if (props.disabled) return '不可编辑'
  if (!moduleEnabled.value) return '模块未启用'
  if (
    notificationResultKeys.value.length > 1 &&
    notificationResultKeys.value.some(key => props.values[key] === false) &&
    notificationResultKeys.value.some(key => props.values[key] !== false)
  ) return '部分通知已启用'
  return notificationEnabled.value ? '通知已启用' : '通知已关闭'
})
const statusIcon = computed(() => {
  if (props.effectiveState === 'plugin_disabled') return 'mdi-alert-outline'
  if (notificationLocked.value) return 'mdi-alert-outline'
  return notificationEnabled.value && !props.disabled ? 'mdi-check-circle-outline' : 'mdi-alert-outline'
})

function shouldDisableField(field) {
  if (props.disabled || !moduleEnabled.value || field.disabled) return true
  if (props.locked && (!props.channelOnlyLock || isChannelField(field))) return true
  const dependencyKey = field.dependsOn || props.dependencies[field.key] || (
    notificationResultKeys.value.length === 1 &&
    field.key !== notificationResultKeys.value[0] &&
    isChannelField(field)
      ? notificationResultKeys.value[0]
      : ''
  )
  if (dependencyKey && props.values[dependencyKey] === false) return true
  return false
}

function withNotifyState(field) {
  return {
    ...field,
    disabled: shouldDisableField(field),
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
    card-type="notify"
    marker="notify"
    data-contract-marker="data-notify-card"
    :data-effective-state="effectiveState || undefined"
    :embedded="embedded"
  >
    <template #actions>
      <span
        class="signal-notify-card__status"
        :class="{ 'signal-notify-card__status--off': effectiveState === 'plugin_disabled' || !notificationEnabled || disabled || locked }"
        aria-live="polite"
      >
        <VIcon :icon="statusIcon" size="16" />
        <span>{{ statusLabel }}</span>
      </span>
    </template>

    <div
      class="signal-notify-card"
      data-notify-card-body
      :data-notify-master-key="masterKey || undefined"
      :data-notify-result-key="notificationResultKeys[0] || undefined"
      :data-notify-result-keys="notificationResultKeys.join(',') || undefined"
      :data-notify-enabled="notificationEnabled ? 'true' : 'false'"
    >
      <div
        v-if="notificationLocked && !channelOnlyLock"
        class="signal-notify-card__lock"
        data-notify-fusion-lock
        role="status"
      >
        <VIcon icon="mdi-alert-outline" size="18" />
        <div>
          <strong>融合通知正在接管</strong>
          <span>当前组件的独立通知配置保持原值，但暂时不可编辑；关闭融合通知后会恢复这些字段。</span>
        </div>
      </div>

      <div v-if="masterFields.length" class="signal-notify-card__lane signal-notify-card__lane--master" data-notify-master>
        <ConfigFieldRow
          v-for="field in masterFields"
          :key="field.key"
          :field="withNotifyState(field)"
          :model-value="values[field.key]"
          @update:model-value="value => updateField(field, value)"
        />
      </div>

      <div v-if="channelFields.length" class="signal-notify-card__lane signal-notify-card__lane--channel" data-notify-channel>
        <ConfigFieldRow
          v-for="field in channelFields"
          :key="field.key"
          :field="withNotifyState(field)"
          :model-value="values[field.key]"
          @update:model-value="value => updateField(field, value)"
        />
      </div>

      <div v-if="modeFields.length" class="signal-notify-card__lane signal-notify-card__lane--mode" data-notify-mode>
        <ConfigFieldRow
          v-for="field in modeFields"
          :key="field.key"
          :field="withNotifyState(field)"
          :model-value="values[field.key]"
          @update:model-value="value => updateField(field, value)"
        />
      </div>

      <div v-if="ruleFields.length" class="signal-notify-card__lane signal-notify-card__lane--rule" data-notify-rule>
        <ConfigFieldRow
          v-for="field in ruleFields"
          :key="field.key"
          :field="withNotifyState(field)"
          :model-value="values[field.key]"
          @update:model-value="value => updateField(field, value)"
        />
      </div>

      <div v-if="detailFields.length" class="signal-notify-card__lane signal-notify-card__lane--detail" data-notify-detail>
        <ConfigFieldRow
          v-for="field in detailFields"
          :key="field.key"
          :field="withNotifyState(field)"
          :model-value="values[field.key]"
          @update:model-value="value => updateField(field, value)"
        />
      </div>
    </div>
  </ConfigCardBase>
</template>

<style scoped>
.signal-notify-card {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(260px, 100%), 1fr));
  gap: var(--signal-grid-gutter-y) var(--signal-grid-gutter-x);
}

.signal-notify-card__status {
  min-height: 30px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: rgb(var(--v-theme-info));
  font-size: 12px;
  font-weight: 750;
  white-space: nowrap;
}

.signal-notify-card__status--off {
  color: rgb(var(--v-theme-warning));
}

.signal-notify-card__lock {
  grid-column: 1 / -1;
  min-width: 0;
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  gap: 10px;
  align-items: start;
  padding: 12px;
  border-radius: var(--signal-config-field-radius);
  color: var(--signal-config-text-secondary);
  background: rgba(var(--v-theme-warning), 0.10);
  box-shadow: inset 0 0 0 1px rgba(var(--v-theme-warning), 0.20);
}

.signal-notify-card__lock strong,
.signal-notify-card__lock span {
  display: block;
}

.signal-notify-card__lock strong {
  color: var(--signal-config-text-primary);
  font-size: 12px;
  line-height: 1.4;
}

.signal-notify-card__lock span {
  margin-top: 2px;
  font-size: 12px;
  line-height: 1.45;
}

.signal-notify-card__lane {
  min-width: 0;
  display: grid;
  align-content: start;
  gap: 8px;
}

.signal-notify-card__lane--master {
  grid-column: auto;
}

.signal-notify-card__lane--channel,
.signal-notify-card__lane--mode,
.signal-notify-card__lane--rule,
.signal-notify-card__lane--detail {
  grid-column: auto;
}

.signal-notify-card__lane-head {
  min-width: 0;
  display: inline-flex;
  align-items: center;
  gap: 7px;
  color: var(--signal-config-text-secondary);
  font-size: 12px;
  font-weight: 760;
}

.signal-notify-card__lane :deep(.signal-config-field-row) {
  min-width: 0;
}

@media (max-width: 900px) {
  .signal-notify-card {
    grid-template-columns: minmax(0, 1fr);
  }

  .signal-notify-card__lane--master,
  .signal-notify-card__lane--channel,
  .signal-notify-card__lane--mode,
  .signal-notify-card__lane--rule,
  .signal-notify-card__lane--detail {
    grid-column: 1 / -1;
  }
}
</style>
