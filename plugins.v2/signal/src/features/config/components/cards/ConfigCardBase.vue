<script setup>
import ConfigFieldRow from './ConfigFieldRow.vue'

const props = defineProps({
  title: { type: String, required: true },
  note: { type: String, default: '' },
  icon: { type: String, default: 'mdi-tune-variant' },
  fields: { type: Array, default: () => [] },
  values: { type: Object, required: true },
  cardType: { type: String, default: 'generic' },
  marker: { type: String, default: '' },
  disabled: { type: Boolean, default: false },
  locked: { type: Boolean, default: false },
  embedded: { type: Boolean, default: false },
})

const emit = defineEmits(['field-update'])

function updateField(field, value) {
  if (!field?.key) return
  props.values[field.key] = value
  emit('field-update', { field, value })
}
</script>

<template>
  <section
    class="signal-config-card signal-design-section-card"
    :class="[`signal-config-card--${cardType}`, { 'signal-config-card--locked': locked, 'signal-config-card--disabled': disabled, 'signal-config-card--embedded': embedded }]"
    :data-html-replica-card="embedded ? null : ''"
    :data-flat-config-section="embedded ? '' : null"
    data-section-tone="neutral"
    :data-cron-card="marker === 'cron' || marker === 'schedule' ? '' : null"
    :data-schedule-card="marker === 'schedule' ? '' : null"
    :data-notify-card="marker === 'notify' ? '' : null"
    :data-generic-card="marker === 'generic' ? '' : null"
    :data-feature-card="marker === 'feature' ? '' : null"
  >
    <header v-if="!embedded" class="signal-config-card__head">
      <span class="signal-config-card__icon">
        <VIcon :icon="icon" size="20" />
      </span>
      <div class="signal-config-card__copy">
        <h3>{{ title }}</h3>
        <p v-if="note">{{ note }}</p>
      </div>
      <span class="signal-config-card__trailing">
        <slot name="actions" />
      </span>
    </header>

    <div v-if="fields.length" class="signal-config-card__fields">
      <ConfigFieldRow
        v-for="field in fields"
        :key="field.key"
        :field="{ ...field, disabled: disabled || locked || field.disabled }"
        :model-value="values[field.key]"
        @update:model-value="value => updateField(field, value)"
      />
    </div>
    <slot />
  </section>
</template>

<style scoped>
.signal-config-card {
  display: grid;
  gap: 14px;
  min-width: 0;
}

.signal-config-card__head {
  min-width: 0;
  display: grid;
  grid-template-columns: minmax(64px, 1fr) minmax(0, auto) minmax(64px, 1fr);
  align-items: center;
  gap: 12px;
}

.signal-config-card__icon {
  justify-self: start;
  flex: 0 0 38px;
  width: 38px;
  height: 38px;
  display: grid;
  place-items: center;
  border-radius: var(--signal-field-radius);
  color: rgb(var(--v-theme-primary));
  background: var(--signal-config-capsule-surface);
}

.signal-config-card__copy {
  min-width: 0;
  min-height: 38px;
  display: grid;
  align-content: center;
  text-align: center;
}

.signal-config-card__trailing {
  min-width: 0;
  display: inline-flex;
  align-items: center;
  justify-self: end;
}

.signal-config-card__copy h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 800;
  line-height: 1.35;
}

.signal-config-card__copy p {
  margin: 3px 0 0;
  max-width: 620px;
  font-size: 12px;
  line-height: 1.45;
  color: var(--signal-config-text-secondary);
}

.signal-config-card__fields {
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  gap: var(--signal-grid-gutter-y) var(--signal-grid-gutter-x);
}

.signal-config-card__fields > :deep(*) {
  grid-column: span 4;
}

.signal-config-card--notify .signal-config-card__icon {
  color: rgb(var(--v-theme-info));
}

.signal-config-card--feature .signal-config-card__icon {
  color: rgb(var(--v-theme-success));
}

.signal-config-card--locked,
.signal-config-card--disabled {
  opacity: 0.78;
}

@media (max-width: 960px) {
  .signal-config-card__fields > :deep(*) {
    grid-column: span 6;
  }
}

@media (max-width: 620px) {
  .signal-config-card__head {
    grid-template-columns: minmax(54px, 1fr) minmax(0, auto) minmax(54px, 1fr);
    gap: 6px;
  }

  .signal-config-card__fields {
    grid-template-columns: 1fr;
  }

  .signal-config-card__fields > :deep(*) {
    grid-column: 1;
  }
}
</style>
