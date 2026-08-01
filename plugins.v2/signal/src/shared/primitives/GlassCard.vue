<template>
  <component :is="tag" :class="cardClass">
    <slot />
  </component>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  tag: { type: String, default: 'section' },
  light: { type: Boolean, default: false },
  className: { type: [String, Array, Object], default: '' },
})

const cardClass = computed(() => [
  props.light ? 'signal-glass-card-light' : 'signal-glass-card',
  props.className,
])
</script>
