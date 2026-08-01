<template>
  <section class="signal-quick-actions">
    <div class="signal-quick-actions__header">
      <h2 class="signal-quick-actions__title">快捷操作</h2>
      <div
        v-if="feedbackMessage"
        class="signal-action-feedback"
        :class="{ 'signal-action-feedback--bad': !feedbackOk }"
        role="status"
        aria-live="polite"
      >
        {{ feedbackMessage }}
      </div>
    </div>
    <div class="signal-quick-actions__grid">
      <button
        v-for="action in actions"
        :key="action.key"
        type="button"
        class="signal-quick-action"
        :class="{ 'signal-quick-action--running': isActionRunning(action) }"
        :disabled="isActionRunning(action)"
        :aria-busy="isActionRunning(action) ? 'true' : 'false'"
        :aria-label="`${action.label}，点击后执行`"
        :title="isActionRunning(action) ? `${action.label}执行中` : `执行${action.label}`"
        @click="$emit('action', action)"
      >
        <span class="signal-quick-action__icon">
          <SvgIcon :icon="action.icon" size="13" />
        </span>
        <span class="signal-quick-action__label">{{ action.label }}</span>
      </button>
    </div>
  </section>
</template>

<script setup>
import SvgIcon from './primitives/SvgIcon.vue'

const props = defineProps({
  actions: { type: Array, default: () => [] },
  runningKey: { type: String, default: '' },
  feedbackMessage: { type: String, default: '' },
  feedbackOk: { type: Boolean, default: true },
})

defineEmits(['action'])

function isActionRunning(action) {
  return !!props.runningKey && (props.runningKey === action?.key || props.runningKey === action?.path)
}
</script>
