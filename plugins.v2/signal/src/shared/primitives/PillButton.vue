<template>
  <button type="button" class="signal-glass-card signal-pill-button" :class="{ 'signal-pill-button--icon': iconOnly }" :disabled="disabled">
    <SvgIcon v-if="icon" :icon="icon" size="14" />
    <span v-if="!iconOnly"><slot>{{ label }}</slot></span>
  </button>
</template>

<script setup>
import SvgIcon from './SvgIcon.vue'

defineProps({
  icon: { type: String, default: '' },
  label: { type: String, default: '' },
  iconOnly: { type: Boolean, default: false },
  disabled: { type: Boolean, default: false },
})
</script>
