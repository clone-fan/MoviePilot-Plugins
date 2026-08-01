<template>
  <div class="signal-traffic-summary">
    <div v-for="row in rows" :key="row.label" class="signal-traffic-summary__pill">
      <span v-if="row.icon" class="signal-traffic-summary__icon" aria-hidden="true">
        <SvgIcon :icon="row.icon" size="12" />
      </span>
      <span class="signal-traffic-summary__text">
        <span class="signal-traffic-summary__label">
          {{ row.label }}
        </span>
        <strong class="signal-traffic-summary__value">{{ row.value }}</strong>
      </span>
    </div>
  </div>
</template>

<script setup>
import SvgIcon from './primitives/SvgIcon.vue'

defineProps({
  rows: { type: Array, default: () => [] },
})
</script>
