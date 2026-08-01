<script setup>
import { computed } from 'vue'
import Dashboard from '../features/dashboard/components/Dashboard.vue'
import MpFreeDashboardRenderer from '../features/mp-free/components/MpFreeDashboardRenderer.vue'

const props = defineProps({
  api: { type: [Object, Function], default: null },
  config: { type: Object, default: () => ({}) },
  allowRefresh: { type: Boolean, default: true },
  surface: { type: String, default: 'dialog' },
  pluginId: { type: String, default: 'Signal' },
})

const emit = defineEmits(['update:refreshStatus', 'loaded', 'close', 'switch'])

const effectiveSurface = computed(() => {
  const surface = props.config?.attrs?.surface ?? props.config?.surface ?? props.surface
  return String(surface || 'dialog').trim().toLowerCase()
})

const isMpFreeWidget = computed(() => effectiveSurface.value === 'mp-widget')
</script>

<template>
  <MpFreeDashboardRenderer
    v-if="isMpFreeWidget"
    :api="api"
    :config="config"
    :allow-refresh="allowRefresh"
    surface="mp-widget"
    :plugin-id="pluginId"
    @update:refresh-status="value => emit('update:refreshStatus', value)"
    @loaded="emit('loaded')"
  />
  <Dashboard
    v-else
    :api="api"
    :config="config"
    :allow-refresh="allowRefresh"
    :surface="effectiveSurface"
    :plugin-id="pluginId"
    @update:refresh-status="value => emit('update:refreshStatus', value)"
    @loaded="emit('loaded')"
    @close="emit('close')"
    @switch="emit('switch')"
  />
</template>
