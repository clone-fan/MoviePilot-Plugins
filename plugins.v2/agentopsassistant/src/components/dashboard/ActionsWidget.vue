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
  /* 外框：贴 MP 官方 surface（跟 v-card 一致） */
  --mp-panel-radius: var(--app-surface-radius, 12px);
  --mp-panel-border: var(--app-surface-border, 1px solid rgba(var(--v-border-color), var(--v-border-opacity, 0.12)));
  --mp-panel-shadow: var(--app-surface-shadow, none);
  --mp-panel-surface: rgb(var(--v-theme-surface));
  /* 内框：on-surface 透白叠在外框上，做液态玻璃层次 */
  --mp-cell-radius: var(--app-field-radius, 10px);
  --mp-cell-border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity, 0.10));
  --mp-cell-surface: rgba(var(--v-theme-on-surface), 0.04);
  --mp-cell-hover-surface: rgba(var(--v-theme-on-surface), 0.08);
  --mp-cell-muted-surface: rgba(var(--v-theme-on-surface), 0.045);
  --mp-cell-shadow: none;
  --mp-cell-hover-shadow: var(--app-surface-hover-shadow, none);
  --mp-blur: none;
  container-type: inline-size;
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-height: 100%;
  padding: 18px;
  border-radius: var(--mp-panel-radius);
  border: var(--mp-panel-border);
  background: var(--mp-panel-surface);
  box-shadow: var(--mp-panel-shadow);
  backdrop-filter: var(--mp-blur);
  -webkit-backdrop-filter: var(--mp-blur);
}

:global(html[data-theme="transparent"]) .mp-actions-panel {
  --mp-panel-surface: rgba(var(--v-theme-surface), var(--transparent-opacity));
  --mp-cell-surface: rgba(var(--v-theme-surface), var(--transparent-opacity-light));
  --mp-cell-hover-surface: rgba(var(--v-theme-surface), var(--transparent-opacity-heavy));
  --mp-blur: blur(var(--transparent-blur));
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
  background: var(--mp-cell-muted-surface);
  box-shadow: var(--mp-cell-shadow) !important;
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
  border-radius: var(--mp-cell-radius);
  border: var(--mp-cell-border);
  color: rgba(var(--v-theme-on-surface), 0.90);
  background: var(--mp-cell-surface);
  box-shadow: var(--mp-cell-shadow) !important;
  cursor: pointer;
  transition: border-color 180ms ease, background-color 180ms ease, box-shadow 180ms ease;
}

.mp-action-btn.v-btn,
:deep(.mp-action-btn.v-btn) {
  box-shadow: var(--mp-cell-shadow) !important;
}

.mp-action-btn:hover {
  border-color: rgba(var(--v-theme-primary), 0.28);
  background: var(--mp-cell-hover-surface);
  box-shadow: var(--mp-cell-hover-shadow) !important;
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
  background: var(--mp-cell-muted-surface);
  box-shadow: var(--mp-cell-shadow);
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
  background: var(--mp-cell-surface);
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
