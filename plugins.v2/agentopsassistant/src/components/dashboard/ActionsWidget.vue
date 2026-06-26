<script setup>
defineProps({
  actions: { type: Array, default: () => [] },
  actionRunning: { type: String, default: '' },
  actionMessage: { type: String, default: '' },
  actionOk: { type: Boolean, default: true },
  allowRefresh: { type: Boolean, default: true },
})

const emit = defineEmits(['runAction'])
</script>

<template>
  <section class="mp-actions-panel">
    <header class="mp-panel-head">
      <span class="mp-panel-icon"><VIcon icon="mdi-lightning-bolt-outline" size="19" /></span>
      <div>
        <h3>手动操作</h3>
        <p>{{ actions.length }} 个常用动作</p>
      </div>
    </header>

    <div class="mp-action-list">
      <VBtn
        v-for="action in actions"
        :key="action.path"
        variant="text"
        class="mp-action-btn text-none"
        :loading="actionRunning === action.path"
        :disabled="action.disabled || (!!actionRunning && actionRunning !== action.path)"
        :title="action.reason || action.desc"
        @click="emit('runAction', action)"
      >
        <span class="mp-action-icon"><VIcon :icon="action.icon" size="19" /></span>
        <span class="mp-action-copy">
          <strong>{{ action.label }}</strong>
          <small>{{ action.desc }}</small>
        </span>
        <VIcon icon="mdi-chevron-right" size="17" class="mp-action-arrow" />
      </VBtn>
    </div>

    <VAlert
      v-if="actionMessage"
      variant="tonal"
      density="compact"
      class="mp-action-message"
      :icon="false"
      :text="actionMessage"
    />
  </section>
</template>

<style scoped>
.mp-actions-panel {
  --mp-widget-panel-source-opacity: var(--mp-widget-surface-opacity, var(--mp-widget-mp-surface-opacity));
  container-type: inline-size;
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-height: 100%;
  padding: 18px;
  border-radius: var(--mp-widget-radius);
  border: 1px solid rgba(var(--v-border-color), var(--mp-widget-panel-line));
  background:
    radial-gradient(circle at 14% 0%, rgba(var(--v-theme-on-surface), 0.048), transparent 34%),
    radial-gradient(circle at 92% 12%, rgba(var(--v-theme-on-surface), 0.034), transparent 32%),
    linear-gradient(180deg, rgba(var(--v-theme-surface), var(--mp-widget-panel-fill-hi)), rgba(var(--v-theme-surface), var(--mp-widget-panel-fill-lo))),
    rgba(var(--v-theme-surface), var(--mp-widget-surface-opacity));
  box-shadow: var(--mp-widget-shadow-panel);
  backdrop-filter: blur(18px) saturate(145%);
  -webkit-backdrop-filter: blur(18px) saturate(145%);
}

.mp-panel-head {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  align-items: center;
  gap: 10px;
}

.mp-panel-icon {
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  border-radius: 12px;
  color: rgba(var(--v-theme-on-surface), 0.76);
  background: rgba(var(--v-theme-on-surface), 0.075);
  box-shadow: var(--mp-widget-shadow-cell) !important;
}

.mp-panel-head h3 {
  margin: 0;
  font-size: 16px;
  line-height: 1.2;
  font-weight: 760;
}

.mp-panel-head p {
  margin: 3px 0 0;
  color: rgba(var(--v-theme-on-surface), 0.58);
  font-size: 12px;
  line-height: 1.15;
}

.mp-action-list {
  min-height: 0;
  display: grid;
  gap: 12px;
}

.mp-action-btn {
  min-width: 0;
  min-height: 60px;
  justify-content: stretch;
  border-radius: var(--mp-widget-cell-radius);
  border: 1px solid rgba(var(--v-border-color), var(--mp-widget-cell-line));
  color: rgba(var(--v-theme-on-surface), 0.90);
  background:
    linear-gradient(180deg, rgba(var(--v-theme-on-surface), var(--mp-widget-cell-line-soft)), rgba(var(--v-theme-on-surface), 0.012)),
    rgba(var(--v-theme-surface), var(--mp-widget-cell-fill)),
    rgba(var(--v-theme-surface), var(--mp-widget-surface-opacity));
  box-shadow: var(--mp-widget-shadow-cell) !important;
  filter: drop-shadow(0 6px 14px rgba(0, 0, 0, 0.055));
  cursor: pointer;
  transition: border-color 180ms ease, background 180ms ease, box-shadow 180ms ease, filter 180ms ease;
}

.mp-action-btn.v-btn,
:deep(.mp-action-btn.v-btn) {
  box-shadow: var(--mp-widget-shadow-cell) !important;
}

.mp-action-btn:hover {
  border-color: rgba(var(--v-theme-on-surface), 0.18);
  background:
    linear-gradient(180deg, rgba(var(--v-theme-on-surface), 0.065), rgba(var(--v-theme-on-surface), 0.020)),
    rgba(var(--v-theme-surface), var(--mp-widget-cell-fill-strong)),
    rgba(var(--v-theme-surface), var(--mp-widget-surface-opacity));
  filter: drop-shadow(0 8px 18px rgba(0, 0, 0, 0.07));
}

.mp-action-btn:focus-visible {
  outline: 2px solid rgba(var(--v-theme-on-surface), 0.38);
  outline-offset: 2px;
}

.mp-action-btn :deep(.v-btn__content) {
  width: 100%;
  min-width: 0;
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
  gap: 11px;
}

.mp-action-icon {
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  border-radius: 12px;
  color: rgba(var(--v-theme-on-surface), 0.78);
  background: rgba(var(--v-theme-on-surface), 0.075);
  box-shadow: var(--mp-widget-shadow-cell);
}

.mp-action-copy {
  min-width: 0;
  display: grid;
  gap: 4px;
  text-align: left;
}

.mp-action-copy strong,
.mp-action-copy small {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.mp-action-copy strong {
  color: rgba(var(--v-theme-on-surface), 0.90);
  font-size: 13px;
  line-height: 1.05;
  font-weight: 760;
}

.mp-action-copy small {
  color: rgba(var(--v-theme-on-surface), 0.56);
  font-size: 12px;
  line-height: 1.05;
  font-weight: 520;
}

.mp-action-arrow {
  color: rgba(var(--v-theme-on-surface), 0.36);
}

.mp-action-message {
  margin-top: auto;
  color: rgba(var(--v-theme-on-surface), 0.74);
  background: rgba(var(--v-theme-on-surface), 0.055);
}

@container (max-width: 420px) {
  .mp-actions-panel {
    gap: 12px;
    padding: 14px;
  }

  .mp-panel-icon,
  .mp-action-icon {
    width: 30px;
    height: 30px;
    border-radius: 11px;
  }

  .mp-panel-head h3 {
    font-size: 14px;
  }

  .mp-panel-head p {
    display: none;
  }

  .mp-action-copy small {
    display: none;
  }

  .mp-action-arrow {
    display: none;
  }

  .mp-action-list {
    gap: 9px;
  }

  .mp-action-btn {
    min-height: 48px;
  }

  .mp-action-btn :deep(.v-btn__content) {
    grid-template-columns: auto minmax(0, 1fr);
    gap: 9px;
  }

  .mp-action-copy strong {
    font-size: 13px;
    white-space: normal;
    line-height: 1.2;
  }
}
</style>
