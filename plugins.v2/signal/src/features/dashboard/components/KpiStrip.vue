<template>
  <div class="signal-kpi-strip" aria-label="仪表盘指标">
    <KpiCard v-for="item in items" :key="item.key" :item="item" />
  </div>
</template>

<script setup>
import KpiCard from './KpiCard.vue'

defineProps({
  items: { type: Array, default: () => [] },
})
</script>
