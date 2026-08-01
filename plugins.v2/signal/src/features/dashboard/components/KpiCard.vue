<template>
  <GlassCard class-name="signal-kpi-card">
    <span class="signal-kpi-card__icon">
      <SvgIcon v-if="item.icon" :icon="item.icon" :color="item.iconColor || undefined" size="20" />
      <span v-if="item.dot" class="signal-status-dot" :class="{ 'signal-status-dot--pulse': item.pulse }" />
    </span>
    <div class="signal-kpi-card__content">
      <span class="signal-kpi-card__label">{{ item.label }}</span>
      <div class="signal-kpi-card__value-row">
        <span class="signal-kpi-card__value" :class="{ 'signal-kpi-card__value--large': item.large }">{{ item.value }}</span>
        <span v-if="item.total" class="signal-kpi-card__total">/ {{ item.total }}</span>
        <span v-if="item.unit" class="signal-kpi-card__unit">{{ item.unit }}</span>
      </div>
      <span class="signal-kpi-card__detail">{{ item.detail }}</span>
    </div>
  </GlassCard>
</template>

<script setup>
import GlassCard from '../../../shared/primitives/GlassCard.vue'
import SvgIcon from '../../../shared/primitives/SvgIcon.vue'

defineProps({
  item: { type: Object, required: true },
})
</script>
