<script setup>
import ScheduleCard from './ScheduleCard.vue'

defineOptions({ inheritAttrs: false })
</script>

<template>
  <ScheduleCard v-bind="$attrs" />
</template>
