<script setup>
import { computed } from 'vue'
import FieldControl from './FieldControl.vue'

const props = defineProps({
  field: { type: Object, required: true },
  modelValue: { type: null, default: null },
})

defineEmits(['update:modelValue'])

const rowSpan = computed(() => props.field.width || props.field.span || 'normal')
const control = computed(() => props.field.control || 'text')
const isSwitch = computed(() => control.value === 'switch')
const isMulti = computed(() => !!(props.field.multiple || props.field.chips || control.value === 'combobox'))
const isCompactMulti = computed(() => !!(props.field.compactMulti && isMulti.value))
const isFullRow = computed(() => !!(props.field.fullRow || (isMulti.value && !isCompactMulti.value) || control.value === 'textarea'))
const controlHint = computed(() => String(props.field.controlHint || '').trim())
const controlHintId = computed(() => controlHint.value
  ? `signal-field-control-hint-${String(props.field.key || 'field').replace(/[^a-zA-Z0-9_-]/g, '-')}`
  : undefined)
const controlField = computed(() => ({
  ...props.field,
  icon: undefined,
  label: '',
  hint: '',
  hideDetails: true,
  ariaLabel: props.field.ariaLabel || props.field.label || props.field.key,
  ariaDescribedby: controlHintId.value,
}))
const rowClasses = computed(() => ({
  'signal-field-row--wide': rowSpan.value === 'wide' || rowSpan.value === 6 || rowSpan.value === '6',
  'signal-field-row--full': rowSpan.value === 'full' || rowSpan.value === 12 || rowSpan.value === '12',
  'signal-field-row--disabled': !!props.field.disabled,
  'signal-field-row--error': !!props.field.error,
  'signal-field-row--switch': isSwitch.value,
  'signal-field-row--switch-on': isSwitch.value && !!props.modelValue,
  'signal-field-row--multi': isMulti.value && !isCompactMulti.value,
  'signal-field-row--compact-multi': isCompactMulti.value,
  'signal-field-row--control-full': isFullRow.value,
  'signal-field-row--with-control-hint': !!controlHint.value,
  'signal-design-field--disabled': !!props.field.disabled,
  'signal-design-field--switch': isSwitch.value,
  'signal-design-field--switch-on': isSwitch.value && !!props.modelValue,
  'signal-design-field--multi': isMulti.value,
  'signal-design-field--full': isFullRow.value,
}))
</script>

<template>
  <div
    class="signal-field-row signal-design-field"
    :class="[`signal-field-row--${field.control || 'text'}`, rowClasses]"
    data-field-row
    data-html-field
    :data-field-key="field.key"
    :data-field-control="field.control || 'text'"
    :data-control-kind="field.control || 'text'"
    :data-switch-row="isSwitch ? 'true' : undefined"
    :data-full-row="isFullRow ? 'true' : undefined"
    :data-multi-select-row="isMulti ? 'true' : undefined"
    :data-has-control-hint="controlHint ? 'true' : undefined"
    :aria-disabled="field.disabled ? 'true' : 'false'"
  >
    <div class="signal-field-row__label">
      <VIcon v-if="field.icon" class="signal-field-row__icon" :icon="field.icon" size="16" aria-hidden="true" />
      <span>{{ field.label }}<template v-if="field.compactSelection">：</template></span>
      <small v-if="field.hint" class="signal-field-row__hint">{{ field.hint }}</small>
      <small v-if="field.error" class="signal-field-row__error">{{ field.error }}</small>
    </div>
    <div class="signal-field-row__control">
      <FieldControl
        :field="controlField"
        :model-value="modelValue"
        @update:model-value="value => $emit('update:modelValue', value)"
      />
      <small
        v-if="controlHint"
        :id="controlHintId"
        class="signal-field-row__control-hint"
        data-field-control-hint
      >{{ controlHint }}</small>
    </div>
  </div>
</template>

<style scoped>
.signal-field-row {
  --signal-design-field-label-track: minmax(132px, 1fr);
  --signal-design-field-control-track: minmax(120px, 1.25fr);
  min-width: 0;
  min-height: 54px;
  display: grid;
  grid-template-columns: var(--signal-design-field-label-track) var(--signal-design-field-control-track);
  align-items: center;
  column-gap: 12px;
  row-gap: 6px;
}

.signal-field-row--wide {
  grid-column: span 6;
}

.signal-field-row--full {
  grid-column: 1 / -1;
}

.signal-field-row--switch {
  grid-template-columns: minmax(0, 1fr) 44px;
}

.signal-field-row--multi,
.signal-field-row--control-full {
  grid-column: 1 / -1;
  grid-template-columns: minmax(96px, 0.42fr) minmax(0, 2.4fr);
  align-items: start;
}

.signal-field-row--compact-multi {
  grid-template-columns: minmax(88px, 0.42fr) minmax(0, 1.8fr);
  align-items: center;
}

.signal-field-row--disabled {
  opacity: 0.72;
}

.signal-field-row__label,
.signal-field-row__control {
  min-width: 0;
}

.signal-field-row__label {
  width: 100%;
}

.signal-field-row__control {
  width: auto;
  max-width: 100%;
}

.signal-field-row__label {
  display: grid;
  grid-template-columns: 16px minmax(0, 1fr);
  gap: 3px;
  color: var(--signal-config-text-primary);
  font-size: 12px;
  font-weight: 800;
  line-height: 1.35;
  overflow-wrap: anywhere;
}

.signal-field-row__label > span,
.signal-field-row__hint,
.signal-field-row__error {
  grid-column: 2;
  min-width: 0;
  white-space: normal;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.signal-field-row__icon {
  grid-column: 1;
  grid-row: 1;
  color: var(--signal-config-text-muted);
}

.signal-field-row__hint,
.signal-field-row__error {
  color: var(--signal-config-text-secondary);
  font-size: 11px;
  font-weight: 500;
  line-height: 1.45;
}

.signal-field-row__error {
  color: rgb(var(--v-theme-error));
}

.signal-field-row :deep(.v-selection-control) {
  min-height: 44px;
}

.signal-field-row :deep(.v-field) {
  min-width: 0;
  width: 100%;
}

.signal-field-row__control {
  display: flex;
  align-items: center;
  justify-content: stretch;
}

.signal-field-row--with-control-hint {
  align-items: start;
}

.signal-field-row--with-control-hint .signal-field-row__control {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  align-content: start;
  gap: 4px;
}

.signal-field-row__control-hint {
  display: block;
  width: 100%;
  min-width: 0;
  color: var(--signal-config-text-secondary);
  font-size: 11px;
  font-weight: 500;
  line-height: 1.45;
  white-space: normal;
  overflow: visible;
  overflow-wrap: anywhere;
  word-break: break-word;
  text-overflow: clip;
  -webkit-line-clamp: unset;
}

.signal-field-row--switch .signal-field-row__control {
  width: 44px;
  min-width: 44px;
  min-height: 44px;
  justify-self: end;
  justify-content: flex-end;
}

@media (max-width: 960px) {
  .signal-field-row,
  .signal-field-row--wide {
    grid-column: span 6;
  }
}

@media (max-width: 620px) {
  .signal-field-row,
  .signal-field-row--wide,
  .signal-field-row--full {
    grid-column: 1;
  }

  .signal-field-row:not(.signal-field-row--switch) {
    grid-template-columns: minmax(0, 1fr);
    row-gap: 3px;
    padding: 5px 8px;
  }

  .signal-field-row:not(.signal-field-row--switch) .signal-field-row__control {
    grid-column: 1;
  }
}
</style>
