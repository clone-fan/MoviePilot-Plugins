<script setup>
import { computed } from 'vue'
import QuickActionsBand from '../../../shared/QuickActionsBand.vue'

const props = defineProps({
  data: { type: Object, required: true },
  frame: { type: Object, default: () => ({}) },
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
})

const quickActions = computed(() => props.data.quickActions || [])
const actionRunner = computed(() => props.data.actionRunner || {})
const actionRunning = computed(() => actionRunner.value.actionRunning?.value || '')
const actionMessage = computed(() => actionRunner.value.actionMessage?.value || '')
const actionOk = computed(() => actionRunner.value.actionOk?.value !== false)
const frameVariant = computed(() => props.frame?.variant || 'mp-native')
const frameDensity = computed(() => props.frame?.density || 'compact')

function runAction(action) {
  actionRunner.value.runAction?.(action)
}
</script>

<template>
  <VCard
    class="signal-mp-free-widget signal-mp-native-card dashboard-summary-card dashboard-grid-fill"
    elevation="0"
    rounded="lg"
    data-free-widget="actions"
    data-mp-frame-component="actions"
    data-module-root-is-frame="true"
    :data-mp-frame-variant="frameVariant"
    :data-mp-frame-density="frameDensity"
    :data-loading="loading ? 'true' : 'false'"
    :data-error="error ? 'true' : 'false'"
  >
    <QuickActionsBand
      class="signal-finalized-actions-content"
      :actions="quickActions"
      :running-key="actionRunning"
      :feedback-message="actionMessage"
      :feedback-ok="actionOk"
      @action="runAction"
    />
  </VCard>
</template>

<style scoped>
.signal-mp-native-card {
  display: flex;
  inline-size: 100%;
  block-size: 100%;
  min-inline-size: 0;
  min-block-size: 0;
  box-sizing: border-box;
  flex-direction: column;
  overflow: hidden;
}

.signal-finalized-actions-content {
  position: relative;
  flex: 1 1 auto;
  inline-size: 100%;
  max-inline-size: 100%;
  block-size: 100%;
  min-block-size: 0;
  box-sizing: border-box;
  justify-content: safe center;
  padding-block: clamp(4px, 2%, 16px);
  padding-inline: clamp(4px, 4%, 24px);
  container-name: signal-quick-actions;
  container-type: inline-size;
  overflow-x: hidden;
  overflow-y: auto;
  overscroll-behavior: contain;
}

.signal-finalized-actions-content :deep(.signal-quick-actions__header),
.signal-finalized-actions-content :deep(.signal-quick-actions__grid) {
  flex: 0 0 auto;
}

.signal-finalized-actions-content :deep(.signal-quick-actions__grid) {
  grid-template-columns: repeat(auto-fit, minmax(min(100%, var(--signal-quick-action-min, 92px)), 1fr));
}

.signal-finalized-actions-content :deep(.signal-quick-action) {
  appearance: none;
  inline-size: 100%;
  min-inline-size: 0;
  min-block-size: 40px;
  border: 1px solid transparent;
  border-radius: 999px;
  padding: 4px 6px 4px 4px;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: var(--signal-action-capsule-surface, rgba(255, 255, 255, 0.038));
  color: rgba(242, 242, 247, 0.78);
  font: inherit;
  font-size: 12.5px;
  line-height: 1.12;
  cursor: pointer;
  transition: background 160ms ease, border-color 160ms ease, box-shadow 160ms ease, color 160ms ease, opacity 160ms ease, transform 160ms ease;
}

.signal-finalized-actions-content :deep(.signal-quick-action:hover) {
  background: var(--signal-action-capsule-surface-hover, rgba(255, 255, 255, 0.074));
  border-color: rgba(255, 255, 255, 0.105);
  color: #fff;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.055);
  transform: translateY(-1px);
}

.signal-finalized-actions-content :deep(.signal-quick-action:disabled) {
  cursor: progress;
  opacity: 0.72;
}

.signal-finalized-actions-content :deep(.signal-quick-action--running) {
  background: rgba(52, 199, 89, 0.105);
  border-color: rgba(52, 199, 89, 0.24);
  color: #fff;
}

.signal-finalized-actions-content :deep(.signal-quick-action__icon) {
  flex: 0 0 22px;
  inline-size: 22px;
  block-size: 22px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  display: grid;
  place-items: center;
  font-size: 9px;
  color: rgba(242, 242, 247, 0.78);
}

.signal-finalized-actions-content :deep(.signal-quick-action--running .signal-quick-action__icon) {
  border-color: rgba(52, 199, 89, 0.32);
  background: rgba(52, 199, 89, 0.15);
  color: #34C759;
}

.signal-finalized-actions-content :deep(.signal-quick-action__label) {
  flex: 1 1 auto;
  min-inline-size: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.signal-finalized-actions-content :deep(.signal-quick-actions__title) {
  color: rgba(var(--v-theme-on-surface, 58, 53, 65), 0.94);
}

@container signal-quick-actions (max-width: 96px) {
  .signal-finalized-actions-content :deep(.signal-quick-actions__header) {
    min-block-size: 18px;
    gap: 4px;
  }

  .signal-finalized-actions-content :deep(.signal-quick-actions__title) {
    min-inline-size: 0;
    font-size: 11px;
    white-space: nowrap;
  }

  .signal-finalized-actions-content :deep(.signal-quick-actions__grid) {
    grid-template-columns: minmax(0, 1fr);
    column-gap: 4px;
    row-gap: 4px;
  }

}
</style>
