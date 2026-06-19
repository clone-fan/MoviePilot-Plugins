<script setup>
import Page from './Page.vue'

defineProps({
  api: { type: [Object, Function], default: null },
  pluginId: { type: String, default: 'AgentOpsAssistant' },
  navKey: { type: String, default: 'main' },
})
</script>

<template>
  <Page :api="api" surface="sidebar" />
</template>
