<script setup>
import FieldRow from '../fields/FieldRow.vue'

defineProps({
  field: { type: Object, required: true },
  modelValue: { type: null, default: null },
})

defineEmits(['update:modelValue'])
</script>

<template>
  <FieldRow
    class="signal-config-field-row"
    data-config-field-row
    :field="field"
    :model-value="modelValue"
    @update:model-value="value => $emit('update:modelValue', value)"
  />
</template>

<style scoped>
.signal-config-field-row {
  min-width: 0;
  width: 100%;
  align-self: stretch;
}

.signal-config-field-row[data-switch-row="true"] {
  grid-template-columns: minmax(0, 1fr) 44px;
}

.signal-config-field-row :deep(.signal-field-row__label),
.signal-config-field-row :deep(.signal-field-row__control) {
  min-width: 0;
}

.signal-config-field-row[data-switch-row="true"] :deep(.signal-field-row__control),
.signal-config-field-row[data-switch-row="true"] :deep([data-field-control]) {
  width: 44px;
  min-width: 44px;
  max-width: 44px;
}

.signal-config-field-row :deep(.signal-field-row__error) {
  min-height: 16px;
  line-height: 16px;
}
</style>
