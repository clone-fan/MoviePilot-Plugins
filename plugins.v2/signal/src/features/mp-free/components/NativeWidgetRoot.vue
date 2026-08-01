<template>
  <section
    class="signal-mp-free-shell"
    :data-free-widget-shell="widget"
    :data-title-mode="titleMode"
  >
    <header class="signal-mp-free-shell__header" data-mp-free-fallback-title>
      <div class="signal-mp-free-shell__title-stack">
        <strong class="signal-mp-free-shell__title">{{ displayTitle }}</strong>
        <span v-if="subtitle" class="signal-mp-free-shell__subtitle">{{ subtitle }}</span>
      </div>
      <span v-if="status" class="signal-mp-free-shell__status">{{ status }}</span>
    </header>

    <div v-if="fallbackMessage" class="signal-mp-free-shell__notice" role="status">
      {{ fallbackMessage }}
    </div>
    <div v-if="error" class="signal-mp-free-shell__notice signal-mp-free-shell__notice--bad" role="alert">
      {{ error }}
    </div>

    <section class="signal-mp-free-widget" :data-free-widget="widget">
      <div class="signal-mp-free-widget__body" :class="{ 'signal-mp-free-widget__body--loading': loading }">
        <slot />
      </div>
    </section>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  widget: { type: String, default: 'site' },
  title: { type: String, default: '' },
  subtitle: { type: String, default: '' },
  status: { type: String, default: '' },
  titleMode: { type: String, default: 'first-party-fallback' },
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
  fallbackMessage: { type: String, default: '' },
})

const displayTitle = computed(() => props.title || {
  site: '站点数据',
  actions: '快捷操作',
}[props.widget] || '仪表盘组件')
</script>

<style scoped>
.signal-mp-free-shell {
  inline-size: 100%;
  block-size: 100%;
  min-inline-size: 0;
  min-block-size: 0;
  box-sizing: border-box;
  display: grid;
  grid-template-rows: auto auto auto minmax(0, 1fr);
  gap: 8px;
  color: rgb(var(--v-theme-on-surface));
  overflow: hidden;
}

.signal-mp-free-shell__header {
  min-inline-size: 0;
  min-block-size: 30px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: start;
  gap: 10px;
}

.signal-mp-free-shell__title-stack {
  min-inline-size: 0;
  display: grid;
  gap: 2px;
}

.signal-mp-free-shell__title {
  min-inline-size: 0;
  overflow: hidden;
  color: rgb(var(--v-theme-on-surface));
  font-size: 15px;
  font-weight: 650;
  line-height: 1.2;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.signal-mp-free-shell__subtitle {
  min-inline-size: 0;
  overflow: hidden;
  color: rgba(var(--v-theme-on-surface), 0.58);
  font-size: 11px;
  line-height: 1.2;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.signal-mp-free-shell__status {
  min-block-size: 22px;
  display: inline-grid;
  place-items: center;
  padding-inline: 9px;
  border-radius: 999px;
  outline: 1px solid rgba(var(--v-theme-on-surface), 0.10);
  color: rgba(var(--v-theme-on-surface), 0.68);
  background: rgba(var(--v-theme-surface), 0.20);
  font-size: 11px;
  line-height: 1;
  white-space: nowrap;
}

.signal-mp-free-widget {
  inline-size: 100%;
  block-size: 100%;
  min-inline-size: 0;
  min-block-size: 0;
  box-sizing: border-box;
  display: grid;
  color: rgb(var(--v-theme-on-surface));
  overflow: hidden;
}

.signal-mp-free-widget__body {
  min-inline-size: 0;
  min-block-size: 0;
  display: grid;
  opacity: 1;
  transition: opacity 160ms ease;
}

.signal-mp-free-widget__body--loading {
  opacity: 0.62;
}

.signal-mp-free-shell__notice {
  min-block-size: 26px;
  display: flex;
  align-items: center;
  padding-inline: 10px;
  border-radius: 999px;
  outline: 1px solid rgba(var(--v-theme-on-surface), 0.10);
  color: rgba(var(--v-theme-on-surface), 0.72);
  background: rgba(var(--v-theme-surface), 0.24);
  font-size: 12px;
  line-height: 1.3;
}

.signal-mp-free-shell__notice--bad {
  color: rgb(var(--v-theme-error));
  background: rgba(var(--v-theme-error), 0.10);
}
</style>
