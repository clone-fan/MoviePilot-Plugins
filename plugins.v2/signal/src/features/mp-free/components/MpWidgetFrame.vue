<script setup>
import { computed } from 'vue'

const props = defineProps({
  component: { type: String, default: 'site' },
  frame: { type: Object, default: () => ({}) },
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
  fallbackMessage: { type: String, default: '' },
})

const frameVariant = computed(() => props.frame?.variant || 'mp-native')

const frameStyle = computed(() => {
  const frame = props.frame || {}
  return {
    '--signal-mp-frame-radius': frame.radius || 'var(--app-surface-radius)',
    '--signal-mp-frame-border': frame.border || 'var(--app-surface-border)',
    '--signal-mp-frame-shadow': frame.shadow || 'var(--app-surface-shadow)',
    '--signal-mp-frame-opacity': frame.transparentOpacity || 'var(--transparent-opacity)',
    '--signal-mp-frame-blur': frame.transparentBlur || 'var(--transparent-blur)',
    '--signal-mp-frame-padding': '0px',
    '--signal-mp-frame-gap': frame.density === 'comfortable' ? '8px' : '6px',
  }
})
</script>

<template>
  <section
    class="signal-mp-widget-frame"
    :data-mp-frame-component="component"
    :data-mp-frame-variant="frameVariant"
    :data-mp-frame-density="frame?.density || 'compact'"
    :style="frameStyle"
  >
    <div v-if="fallbackMessage" class="signal-mp-widget-frame__notice" role="status">
      {{ fallbackMessage }}
    </div>
    <div v-if="error" class="signal-mp-widget-frame__notice signal-mp-widget-frame__notice--bad" role="alert">
      {{ error }}
    </div>

    <section class="signal-mp-widget-frame__body">
      <div
        class="signal-mp-free-widget"
        :class="{ 'signal-mp-free-widget--loading': loading }"
        :data-free-widget="component"
      >
        <slot />
      </div>
    </section>
  </section>
</template>

<style scoped>
.signal-mp-widget-frame {
  inline-size: 100%;
  block-size: 100%;
  min-inline-size: 0;
  min-block-size: 0;
  box-sizing: border-box;
  display: grid;
  grid-template-rows: auto auto minmax(0, 1fr);
  gap: var(--signal-mp-frame-gap, 6px);
  padding: var(--signal-mp-frame-padding, 0px);
  border: var(--signal-mp-frame-border, var(--app-surface-border, 1px solid rgba(var(--v-theme-on-surface), var(--v-border-opacity, 0.12))));
  border-radius: var(--signal-mp-frame-radius, var(--app-surface-radius, 12px));
  outline: 1px solid rgba(var(--v-theme-on-surface), var(--v-border-opacity, 0.12));
  outline-offset: -1px;
  background: transparent;
  box-shadow: var(--signal-mp-frame-shadow, var(--app-surface-shadow, none));
  color: rgb(var(--v-theme-on-surface));
  overflow: hidden;
  backdrop-filter: blur(var(--signal-mp-frame-blur, var(--transparent-blur, 0px)));
  -webkit-backdrop-filter: blur(var(--signal-mp-frame-blur, var(--transparent-blur, 0px)));
}

.signal-mp-widget-frame__notice {
  min-block-size: 26px;
  display: flex;
  align-items: center;
  margin: 8px 8px 0;
  padding-inline: 10px;
  border-radius: 999px;
  outline: 1px solid rgba(var(--v-theme-on-surface), 0.10);
  color: rgba(var(--v-theme-on-surface), 0.72);
  background: rgba(var(--v-theme-on-surface), 0.08);
  font-size: 12px;
  line-height: 1.3;
}

.signal-mp-widget-frame__notice--bad {
  color: rgb(var(--v-theme-error));
  background: rgba(var(--v-theme-error), 0.10);
}

.signal-mp-widget-frame__body,
.signal-mp-free-widget {
  min-inline-size: 0;
  min-block-size: 0;
  block-size: 100%;
  display: grid;
  overflow: hidden;
}

.signal-mp-widget-frame__body {
  grid-row: -2 / -1;
}

.signal-mp-free-widget {
  --line: 255, 255, 255;
  --signal-site-column-fr: 2.55fr;
  --signal-runtime-column-min: 340px;
  --signal-runtime-column-fr: 0.82fr;
  --signal-quick-actions-width: min(100%, 540px);
  --signal-quick-action-min: 92px;
  --signal-module-surface-dim: rgba(255, 255, 255, 0.052);
  --signal-module-surface-dim-border: rgba(255, 255, 255, 0.082);
  --signal-action-capsule-surface: rgba(255, 255, 255, 0.038);
  --signal-action-capsule-surface-hover: rgba(255, 255, 255, 0.074);
  inline-size: 100%;
  opacity: 1;
  transition: opacity 160ms ease;
}

.signal-mp-free-widget :deep(.signal-site-panel),
.signal-mp-free-widget :deep(.signal-bottom-row) {
  inline-size: 100%;
  block-size: 100%;
  min-block-size: 0;
  box-sizing: border-box;
}

.signal-mp-free-widget--loading {
  opacity: 0.62;
}
</style>
