<script setup>
import { computed, onMounted, watch } from 'vue'
import { useDashboardFreeData } from '../composables/useDashboardFreeData.js'
import MpSiteDataWidget from './MpSiteDataWidget.vue'
import MpQuickActionsWidget from './MpQuickActionsWidget.vue'

// SIGNAL-HOST-CONSTRAINT: MoviePilot free-widget hosts own the visible outer frame.
// This adapter selects one content module and passes the host frame through unchanged.
const props = defineProps({
  api: { type: [Object, Function], default: null },
  config: { type: Object, default: () => ({}) },
  allowRefresh: { type: Boolean, default: true },
  surface: { type: String, default: 'mp-widget' },
  pluginId: { type: String, default: 'Signal' },
})

const emit = defineEmits(['update:refreshStatus', 'loaded'])

const freeData = useDashboardFreeData(props.api)

const requestedWidget = computed(() => {
  const attrs = props.config?.attrs || {}
  const explicit = attrs.component || props.config?.component
  if (explicit) return String(explicit)
  const components = attrs.components || props.config?.components || {}
  const firstEnabled = Object.entries(components).find(([, enabled]) => enabled)
  return firstEnabled?.[0] || 'site'
})

const widget = computed(() => {
  if (['site', 'actions'].includes(requestedWidget.value)) return requestedWidget.value
  return 'site'
})

const widgetFrame = computed(() => {
  const attrs = props.config?.attrs || {}
  return attrs.frame || {
    variant: 'mp-native',
    surface: 'dashboard-widget',
    density: widget.value === 'site' ? 'comfortable' : 'compact',
    radius: 'var(--app-surface-radius)',
    border: 'var(--app-surface-border)',
    shadow: 'var(--app-surface-shadow)',
    transparentOpacity: 'var(--transparent-opacity)',
    transparentBlur: 'var(--transparent-blur)',
  }
})

const fallbackMessage = computed(() => (
  requestedWidget.value === widget.value ? '' : `未知组件 ${requestedWidget.value}，已显示站点数据。`
))

const currentComponent = computed(() => ({
  site: MpSiteDataWidget,
  actions: MpQuickActionsWidget,
}[widget.value] || MpSiteDataWidget))

watch(() => freeData.loading.value, value => emit('update:refreshStatus', value ? 'loading' : 'success'))
watch(() => freeData.error.value, value => {
  if (value) emit('update:refreshStatus', 'error')
})

onMounted(async () => {
  await freeData.loadDashboard()
  emit('loaded')
})
</script>

<template>
  <component
    :is="currentComponent"
    :data="freeData"
    :frame="widgetFrame"
    :loading="freeData.loading.value"
    :error="freeData.error.value || fallbackMessage"
    :allow-refresh="allowRefresh"
    @refresh="freeData.loadDashboard"
  />
</template>
