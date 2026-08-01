<script setup>
import { computed } from 'vue'
import ConfigCardBase from './ConfigCardBase.vue'
import ConfigFieldRow from './ConfigFieldRow.vue'

const props = defineProps({
  title: { type: String, required: true },
  note: { type: String, default: '' },
  icon: { type: String, default: 'mdi-form-textbox' },
  fields: { type: Array, default: () => [] },
  values: { type: Object, required: true },
  disabled: { type: Boolean, default: false },
  locked: { type: Boolean, default: false },
})

const emit = defineEmits(['field-update'])

const activeFields = computed(() => props.fields.map(field => ({
  ...field,
  disabled: props.disabled || props.locked || field.disabled,
  hideInlineLabel: field.hideInlineLabel ?? true,
})))

const genericFieldGroups = computed(() => {
  const groups = []
  for (const field of activeFields.value) {
    const groupKey = field.group || field.section || 'basic'
    let group = groups.find(item => item.key === groupKey)
    if (!group) {
      group = {
        key: groupKey,
        title: field.groupTitle || field.sectionTitle || '',
        fields: [],
      }
      groups.push(group)
    }
    group.fields.push(field)
  }
  return groups
})

const statusText = computed(() => {
  if (props.locked) return '已由上游接管'
  if (props.disabled) return '当前不可编辑'
  return `${props.fields.length} 项基础参数`
})

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
    :fields="[]"
    :values="values"
    card-type="generic"
    marker="generic"
    data-contract-marker="data-generic-card"
    :disabled="disabled"
    :locked="locked"
  >
    <template #actions>
      <span class="signal-generic-card__status" data-generic-status>{{ statusText }}</span>
    </template>

    <div class="signal-generic-card" :class="{ 'signal-generic-card--locked': locked }">
      <div
        v-for="group in genericFieldGroups"
        :key="group.key"
        class="signal-generic-card__group"
      >
        <h4 v-if="group.title" class="signal-generic-card__group-title">{{ group.title }}</h4>
        <div class="signal-generic-card__fields" data-generic-field-grid>
          <ConfigFieldRow
            v-for="field in group.fields"
            :key="field.key"
            :field="field"
            :model-value="values[field.key]"
            @update:model-value="value => updateField(field, value)"
          />
        </div>
      </div>
    </div>
  </ConfigCardBase>
</template>

<style scoped>
.signal-generic-card {
  display: grid;
  gap: 12px;
  min-width: 0;
}

.signal-generic-card__status {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 10px;
  border: var(--signal-config-field-border);
  border-radius: var(--signal-config-capsule-radius);
  color: var(--signal-config-text-secondary);
  background: var(--signal-config-capsule-surface);
  font-size: 12px;
  font-weight: 700;
  white-space: nowrap;
}

.signal-generic-card__group {
  display: grid;
  gap: 10px;
  min-width: 0;
}

.signal-generic-card__group-title {
  margin: 0;
  color: var(--signal-config-text-secondary);
  font-size: 12px;
  font-weight: 800;
  line-height: 1.35;
}

.signal-generic-card__fields {
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  gap: var(--signal-grid-gutter-y) var(--signal-grid-gutter-x);
  min-width: 0;
}

@media (max-width: 620px) {
  .signal-generic-card__fields {
    grid-template-columns: 1fr;
  }
}
</style>
