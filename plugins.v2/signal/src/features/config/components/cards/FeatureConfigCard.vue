<script setup>
import { computed, useSlots } from 'vue'
import ConfigCardBase from './ConfigCardBase.vue'
import ConfigFieldRow from './ConfigFieldRow.vue'

const props = defineProps({
  title: { type: String, required: true },
  note: { type: String, default: '' },
  icon: { type: String, default: 'mdi-puzzle-check-outline' },
  fields: { type: Array, default: () => [] },
  values: { type: Object, required: true },
  disabled: { type: Boolean, default: false },
  locked: { type: Boolean, default: false },
})

const emit = defineEmits(['field-update'])
const slots = useSlots()

const activeFields = computed(() => props.fields.map(field => ({
  ...field,
  disabled: props.disabled || props.locked || field.disabled,
  hideInlineLabel: field.hideInlineLabel ?? true,
})))

const featureFieldGroups = computed(() => {
  const groups = []
  for (const field of activeFields.value) {
    const groupKey = field.group || field.section || 'feature'
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

const hasFeatureSlot = computed(() => !!slots.default || !!slots.feature)
const statusText = computed(() => {
  if (props.locked) return '已锁定'
  if (props.disabled) return '当前不可编辑'
  if (hasFeatureSlot.value && props.fields.length) return `${props.fields.length} 项参数 + 专用操作`
  if (hasFeatureSlot.value) return '专用操作'
  return `${props.fields.length} 项组件参数`
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
    card-type="feature"
    marker="feature"
    data-contract-marker="data-feature-card"
    :disabled="disabled"
    :locked="locked"
  >
    <template #actions>
      <span class="signal-feature-card__status" data-feature-status>{{ statusText }}</span>
    </template>

    <div class="signal-feature-card" data-feature-body>
      <div
        v-for="group in featureFieldGroups"
        :key="group.key"
        class="signal-feature-card__group"
      >
        <h4 v-if="group.title" class="signal-feature-card__group-title">{{ group.title }}</h4>
        <div class="signal-feature-card__fields" data-feature-field-grid>
          <ConfigFieldRow
            v-for="field in group.fields"
            :key="field.key"
            :field="field"
            :model-value="values[field.key]"
            @update:model-value="value => updateField(field, value)"
          />
        </div>
      </div>

      <div v-if="hasFeatureSlot" class="signal-feature-card__slot" data-feature-slot data-feature-slot-surface>
        <slot name="feature" />
        <slot />
      </div>
    </div>
  </ConfigCardBase>
</template>

<style scoped>
.signal-feature-card {
  display: grid;
  gap: 14px;
  min-width: 0;
}

.signal-feature-card__status {
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

.signal-feature-card__group,
.signal-feature-card__slot {
  display: grid;
  gap: 10px;
  min-width: 0;
}

.signal-feature-card__group-title {
  margin: 0;
  color: var(--signal-config-text-secondary);
  font-size: 12px;
  font-weight: 800;
  line-height: 1.35;
}

.signal-feature-card__fields {
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  gap: var(--signal-grid-gutter-y) var(--signal-grid-gutter-x);
  min-width: 0;
}

.signal-feature-card__slot {
  padding: 12px;
  border: var(--signal-config-field-border);
  border-radius: var(--signal-config-field-radius);
  background: var(--signal-config-field-surface);
  overflow: hidden;
}

.signal-feature-card__slot :deep(*) {
  min-width: 0;
}

@media (max-width: 620px) {
  .signal-feature-card__fields {
    grid-template-columns: 1fr;
  }
}
</style>
