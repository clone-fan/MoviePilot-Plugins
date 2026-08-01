<template>
  <header class="signal-dashboard-toolbar">
    <div>
      <h1 class="signal-dashboard-toolbar__title">MP 运维助手</h1>
      <span class="signal-dashboard-toolbar__subtitle">仪表盘</span>
    </div>
    <div class="signal-dashboard-toolbar__actions">
      <PillButton :icon="signalIcons.refresh" label="刷新" :disabled="loading" @click="$emit('refresh')" />
      <PillButton :icon="signalIcons.cog" icon-only label="设置" @click="$emit('settings')" />
    </div>
  </header>
</template>

<script setup>
import PillButton from '../../../shared/primitives/PillButton.vue'
import { signalIcons } from '../../../shared/icons.js'

defineProps({
  loading: { type: Boolean, default: false },
})

defineEmits(['refresh', 'settings'])
</script>
