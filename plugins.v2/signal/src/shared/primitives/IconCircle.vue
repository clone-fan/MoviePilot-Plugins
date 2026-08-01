<template>
  <span class="signal-icon-circle" :class="variantClass">
    <SvgIcon :icon="icon" :size="size" />
  </span>
</template>

<script setup>
import { computed } from 'vue'
import SvgIcon from './SvgIcon.vue'

const props = defineProps({
  icon: { type: String, required: true },
  size: { type: [Number, String], default: 14 },
  tone: { type: String, default: '' },
})

const variantClass = computed(() => props.tone ? `signal-icon-circle--${props.tone}` : '')
</script>
