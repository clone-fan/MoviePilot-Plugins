<template>
  <span class="signal-status-chip" :class="toneClass">
    <SvgIcon v-if="icon" :icon="icon" size="10" />
    <slot>{{ label }}</slot>
  </span>
</template>

<script setup>
import { computed } from 'vue'
import SvgIcon from './SvgIcon.vue'

const props = defineProps({
  label: { type: String, default: '' },
  tone: { type: String, default: '' },
  icon: { type: String, default: '' },
})

const toneClass = computed(() => props.tone ? `signal-status-chip--${props.tone}` : '')
</script>
