<script setup>
import { onMounted, ref, watch } from 'vue'
import Config from '../features/config/Config.vue'

const props = defineProps({
  api: { type: [Object, Function], default: null },
  initialConfig: { type: Object, default: () => ({}) },
  pluginId: { type: String, default: 'Signal' },
  configRecordState: { type: String, default: null },
})

const emit = defineEmits(['save', 'close', 'switch'])
const recordStates = new Set(['unknown', 'absent', 'present'])
const explicitRecordState = value => recordStates.has(value) ? value : null
const loadedConfig = ref({ ...props.initialConfig })
const recordState = ref(explicitRecordState(props.configRecordState) || 'unknown')

watch(() => props.initialConfig, value => {
  loadedConfig.value = { ...(value || {}) }
}, { deep: true })

watch(() => props.configRecordState, value => {
  recordState.value = explicitRecordState(value) || 'unknown'
})

onMounted(async () => {
  if (!props.api?.get) return
  if (!explicitRecordState(props.configRecordState)) recordState.value = 'unknown'
  try {
    const result = await props.api.get(`plugin/form/${props.pluginId}`)
    const model = result?.model ?? result?.data?.model
    const hasConfigRecord = model !== null && typeof model === 'object' && !Array.isArray(model)
    const forcedState = explicitRecordState(props.configRecordState)
    if (hasConfigRecord) {
      loadedConfig.value = { ...model }
      if (!forcedState) recordState.value = 'present'
    } else if (!forcedState) {
      recordState.value = 'absent'
    }
  } catch {
    if (!explicitRecordState(props.configRecordState)) recordState.value = 'unknown'
  }
})

</script>

<template>
  <Config
    :api="api"
    :initial-config="loadedConfig"
    :plugin-id="pluginId"
    :config-record-state="recordState"
    @save="value => emit('save', value)"
    @close="emit('close')"
    @switch="emit('switch')"
  />
</template>
