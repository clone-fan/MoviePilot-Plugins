<script setup>
import { computed } from 'vue'

const props = defineProps({
  field: { type: Object, required: true },
  modelValue: { type: null, default: null },
})

const emit = defineEmits(['update:modelValue'])

function emitValue(next) {
  let value = next
  if (control.value === 'number') {
    const parsed = Number(next)
    value = Number.isNaN(parsed) ? null : parsed
  }
  emit('update:modelValue', value)
}

const normalizedValue = computed({
  get: () => props.modelValue,
  set: next => emitValue(next),
})

const control = computed(() => props.field.control || 'text')
const selectionCount = computed(() => Array.isArray(normalizedValue.value) ? normalizedValue.value.length : 0)
const selectionSummary = computed(() => (
  selectionCount.value === 0 && props.field.emptySelectionText
    ? props.field.emptySelectionText
    : `已选 ${selectionCount.value} 项`
))
const commonProps = computed(() => ({
  label: undefined,
  hint: '',
  persistentHint: false,
  disabled: !!props.field.disabled,
  density: props.field.density || 'comfortable',
  hideDetails: props.field.hideDetails ?? false,
  errorMessages: props.field.error ? [props.field.error] : [],
  'aria-label': props.field.ariaLabel || props.field.label || props.field.key,
  'aria-describedby': props.field.ariaDescribedby || undefined,
}))

function selectionTitle(item) {
  return item?.raw?.title ?? item?.raw?.label ?? item?.raw?.name ?? item?.title ?? item?.label ?? item?.name ?? item?.props?.title ?? item?.value ?? item?.key ?? item?.id ?? item
}

function selectionValue(item) {
  return item?.raw?.value ?? item?.raw?.key ?? item?.raw?.id ?? item?.value ?? item?.key ?? item?.id ?? item
}
</script>

<template>
  <div
    class="signal-field-control"
    :class="{
      'signal-field-control--switch': control === 'switch',
      'signal-field-control--switch-on': control === 'switch' && !!normalizedValue,
      'signal-field-control--multi': !!(field.multiple || field.chips || control === 'combobox'),
      'signal-field-control--full': !!(field.fullRow || field.multiple || field.chips || control === 'combobox' || control === 'textarea'),
    }"
    data-field-control
    :data-control-kind="control"
    :data-switch-enabled="control === 'switch' ? (!!normalizedValue ? 'true' : 'false') : undefined"
    :data-multi-select="!!(field.multiple || field.chips || control === 'combobox') ? 'true' : undefined"
  >
    <button
      v-if="control === 'switch'"
      type="button"
      class="signal-toggle-switch"
      :class="{
        'signal-toggle-switch--on': !!normalizedValue,
        'signal-toggle-switch--disabled': !!field.disabled,
      }"
      role="switch"
      :aria-checked="!!normalizedValue"
      :aria-label="field.ariaLabel || field.label || field.key"
      :disabled="!!field.disabled"
      data-field-switch
      @click="normalizedValue = !normalizedValue"
    >
      <span class="signal-toggle-switch__thumb" aria-hidden="true" />
    </button>
    <VCronField
      v-else-if="control === 'cron'"
      v-model="normalizedValue"
      v-bind="commonProps"
      :placeholder="field.placeholder || undefined"
    />
    <VSelect
      v-else-if="control === 'select'"
      v-model="normalizedValue"
      v-bind="commonProps"
      :items="field.items || []"
      :item-title="selectionTitle"
      :item-value="selectionValue"
      :loading="!!field.loading"
      :multiple="!!field.multiple"
      :chips="!!field.chips && !field.compactSelection"
      :closable-chips="!!field.closableChips && !field.compactSelection"
      :clearable="field.clearable !== false"
      :prepend-inner-icon="field.icon || undefined"
      :placeholder="field.compactSelection ? selectionSummary : (field.placeholder || undefined)"
    >
      <template v-if="field.compactSelection" #selection="{ index }">
        <span v-if="index === 0" class="signal-field-control__selection-count">{{ selectionSummary }}</span>
      </template>
      <template v-else-if="field.multiple || field.chips" #chip="{ item, props: chipProps }">
        <VChip v-bind="chipProps" class="signal-field-control__chip" variant="tonal">
          {{ selectionTitle(item) }}
        </VChip>
      </template>
    </VSelect>
    <VCombobox
      v-else-if="control === 'combobox'"
      v-model="normalizedValue"
      v-bind="commonProps"
      :items="field.items || []"
      :item-title="selectionTitle"
      :item-value="selectionValue"
      :multiple="!!field.multiple"
      :chips="!!field.chips && !field.compactSelection"
      :closable-chips="!!field.closableChips && !field.compactSelection"
      :clearable="field.clearable !== false"
      :prepend-inner-icon="field.icon || undefined"
      :placeholder="field.compactSelection ? selectionSummary : (field.placeholder || '输入后按回车添加')"
    >
      <template v-if="field.compactSelection" #selection="{ index }">
        <span v-if="index === 0" class="signal-field-control__selection-count">{{ selectionSummary }}</span>
      </template>
      <template v-else #chip="{ item, props: chipProps }">
        <VChip v-bind="chipProps" class="signal-field-control__chip" variant="tonal">
          {{ selectionTitle(item) }}
        </VChip>
      </template>
    </VCombobox>
    <VTextarea
      v-else-if="control === 'textarea'"
      v-model="normalizedValue"
      v-bind="commonProps"
      :placeholder="field.placeholder || undefined"
      :prepend-inner-icon="field.icon || undefined"
      :rows="field.rows || 3"
      auto-grow
    />
    <VTextField
      v-else
      v-model="normalizedValue"
      v-bind="commonProps"
      :type="control === 'number' ? 'number' : (field.sensitive ? 'password' : 'text')"
      :prepend-inner-icon="field.icon || undefined"
      :suffix="field.suffix || undefined"
      :min="field.min ?? undefined"
      :max="field.max ?? undefined"
      :placeholder="field.placeholder || undefined"
    />
  </div>
</template>

<style scoped>
.signal-field-control {
  min-width: 0;
  width: 100%;
}

.signal-field-control :deep(.v-field),
.signal-field-control :deep(.v-input),
.signal-field-control :deep(.v-selection-control) {
  min-width: 0;
  width: 100%;
}

.signal-field-control--switch {
  width: auto;
  display: inline-flex;
  align-items: center;
  justify-content: flex-end;
  min-width: 44px;
  min-height: 44px;
}

.signal-field-control :deep(textarea),
.signal-field-control :deep(input) {
  overflow-wrap: anywhere;
}

.signal-field-control--multi,
.signal-field-control--full {
  width: 100%;
}

.signal-field-control--multi :deep(.v-field__input),
.signal-field-control--full :deep(.v-field__input) {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  align-content: flex-start;
  gap: 4px;
  min-height: 40px;
  height: auto !important;
  overflow: visible;
}

.signal-field-control--multi :deep(.v-field),
.signal-field-control--full :deep(.v-field) {
  height: auto !important;
  min-height: 40px;
}

.signal-field-control--multi :deep(.v-chip),
.signal-field-control__chip {
  max-width: 100%;
  flex: 0 1 auto;
  margin: 0 !important;
}

.signal-field-control__chip {
  max-width: 100%;
  padding-inline: 6px;
}

.signal-field-control__selection-count {
  min-width: 0;
  color: var(--signal-config-text-primary);
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
}

/* Compact replica rows keep the label icon only; suppress empty prepend slots. */
.signal-field-control :deep(.v-field__prepend-inner:empty),
.signal-field-control :deep(.v-field__prepend-inner:not(:has(*))) {
  display: none;
}
</style>
