<script setup>
import Dashboard from './Dashboard.vue'

defineProps({
  api: { type: [Object, Function], default: null },
  surface: { type: String, default: 'dialog' },
  pluginId: { type: String, default: 'Signal' },
})

const emit = defineEmits(['close', 'switch'])
</script>

<template>
  <Dashboard
    :api="api"
    :surface="surface"
    :plugin-id="pluginId"
    @close="emit('close')"
    @switch="emit('switch')"
  />
</template>
