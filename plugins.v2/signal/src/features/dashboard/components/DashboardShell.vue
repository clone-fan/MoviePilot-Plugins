<template>
  <section class="dashboard-plugin-vue-renderer signal-dashboard-shell signal-root signal-plugin-shell" :class="shellClass">
    <div class="signal-dashboard-canvas">
      <slot />
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  surface: { type: String, default: 'dialog' },
  themeClass: { type: String, default: '' },
})

const shellClass = computed(() => [
  `signal-dashboard-shell--${props.surface || 'dialog'}`,
  props.themeClass,
])
</script>
