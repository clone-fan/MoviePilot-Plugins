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
  --mp-widget-radius: var(--v-card-border-radius, var(--app-surface-radius, 12px));
  --mp-widget-surface-opacity: var(--v-card-opacity, var(--transparent-opacity, 1));
  --mp-widget-mp-surface-opacity: var(--v-card-opacity, var(--transparent-opacity, 1));
  --aoa-outer-surface: rgb(var(--v-theme-surface));
  --aoa-inner-surface-alpha-hi: 0.56;
  --aoa-inner-surface-alpha-lo: 0.42;
  --aoa-inner-surface-tint: 0.10;
  --aoa-inner-strong-alpha-hi: 0.66;
  --aoa-inner-strong-alpha-lo: 0.50;
  --aoa-inner-strong-tint: 0.14;
  --aoa-inner-muted-alpha-hi: 0.48;
  --aoa-inner-muted-alpha-lo: 0.34;
  --aoa-inner-muted-tint: 0.09;
  --aoa-inner-surface:
    linear-gradient(180deg, rgba(var(--v-theme-surface), var(--aoa-inner-surface-alpha-hi)), rgba(var(--v-theme-surface), var(--aoa-inner-surface-alpha-lo))),
    rgba(var(--v-theme-on-surface), var(--aoa-inner-surface-tint));
  --aoa-inner-surface-strong:
    linear-gradient(180deg, rgba(var(--v-theme-surface), var(--aoa-inner-strong-alpha-hi)), rgba(var(--v-theme-surface), var(--aoa-inner-strong-alpha-lo))),
    rgba(var(--v-theme-on-surface), var(--aoa-inner-strong-tint));
  --aoa-inner-surface-muted:
    linear-gradient(180deg, rgba(var(--v-theme-surface), var(--aoa-inner-muted-alpha-hi)), rgba(var(--v-theme-surface), var(--aoa-inner-muted-alpha-lo))),
    rgba(var(--v-theme-on-surface), var(--aoa-inner-muted-tint));
  --aoa-inner-border: 1px solid rgba(var(--v-border-color), 0.18);
  --aoa-inner-shadow:
    inset 0 1px 0 rgba(var(--v-theme-on-surface), 0.10),
    inset 0 -1px 0 rgba(0, 0, 0, 0.10),
    0 10px 26px rgba(0, 0, 0, 0.14);
  --aoa-inner-blur: 12px;
  --mp-widget-panel-fill-hi: var(--aoa-outer-surface);
  --mp-widget-cell-fill: linear-gradient(
    180deg,
    rgba(var(--v-theme-surface), var(--mp-widget-surface-opacity)),
    rgba(var(--v-theme-on-surface), 0.045)
  ), var(--aoa-inner-surface-strong);
  --mp-widget-shadow-panel: var(--app-surface-shadow, none);
  --mp-widget-shadow-cell: var(--aoa-inner-shadow);
  --mp-widget-blur: var(--aoa-inner-blur);
  --mp-panel-radius: var(--mp-widget-radius);
  --mp-panel-border: var(--app-surface-border, 1px solid rgba(var(--v-border-color), var(--v-border-opacity, 0.12)));
  --mp-panel-shadow: var(--mp-widget-shadow-panel);
  --mp-panel-surface: var(--mp-widget-panel-fill-hi);
  /* 内框：on-surface 透白叠在外框上，做液态玻璃层次 */
  --mp-cell-radius: var(--app-field-radius, 10px);
  --mp-cell-border: var(--aoa-inner-border);
  --mp-cell-surface: var(--mp-widget-cell-fill);
  --mp-cell-hover-surface: var(--aoa-inner-surface-strong);
  --mp-cell-muted-surface: var(--aoa-inner-surface-muted);
  --mp-cell-shadow: var(--mp-widget-shadow-cell);
  --mp-cell-hover-shadow: var(--app-surface-hover-shadow, none);
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
  backdrop-filter: blur(var(--mp-widget-blur));
  -webkit-backdrop-filter: blur(var(--mp-widget-blur));
}

:global(html[data-theme="transparent"]) .mp-actions-panel {
  --aoa-outer-surface: rgba(var(--v-theme-surface), var(--transparent-opacity, 1));
  --aoa-inner-surface-alpha-hi: var(--transparent-opacity-heavy, 0.58);
  --aoa-inner-surface-alpha-lo: var(--transparent-opacity, 0.42);
  --aoa-inner-surface-tint: 0.13;
  --aoa-inner-strong-alpha-hi: var(--transparent-opacity-heavy, 0.66);
  --aoa-inner-strong-alpha-lo: var(--transparent-opacity, 0.48);
  --aoa-inner-strong-tint: 0.17;
  --aoa-inner-muted-alpha-hi: var(--transparent-opacity, 0.48);
  --aoa-inner-muted-alpha-lo: var(--transparent-opacity-light, 0.34);
  --aoa-inner-muted-tint: 0.12;
  --aoa-inner-border: 1px solid rgba(var(--v-border-color), 0.22);
  --aoa-inner-blur: var(--transparent-blur, 12px);
  --mp-panel-surface: var(--mp-widget-panel-fill-hi);
  --mp-cell-surface: var(--mp-widget-cell-fill);
  --mp-cell-hover-surface: var(--aoa-inner-surface-strong);
  --mp-cell-muted-surface: var(--aoa-inner-surface-muted);
  --mp-cell-border: var(--aoa-inner-border);
  --mp-widget-blur: var(--aoa-inner-blur);
}

.mp-actions-panel::-webkit-scrollbar,
.mp-action-list::-webkit-scrollbar {
  width: 1px !important;
  height: 1px !important;
  background: transparent !important;
}

.mp-actions-panel::-webkit-scrollbar-track,
.mp-action-list::-webkit-scrollbar-track,
.mp-actions-panel::-webkit-scrollbar-track-piece,
.mp-action-list::-webkit-scrollbar-track-piece {
  background: transparent !important;
}

.mp-actions-panel::-webkit-scrollbar-thumb,
.mp-action-list::-webkit-scrollbar-thumb {
  border: 0 !important;
  border-radius: 999px !important;
  background: rgba(var(--v-theme-on-surface), 0.08) !important;
}

.mp-actions-panel::-webkit-scrollbar-button,
.mp-action-list::-webkit-scrollbar-button,
.mp-actions-panel::-webkit-scrollbar-corner,
.mp-action-list::-webkit-scrollbar-corner {
  display: none !important;
  width: 0 !important;
  height: 0 !important;
  appearance: none !important;
  background: transparent !important;
  opacity: 0 !important;
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
  box-shadow: var(--mp-widget-shadow-cell) !important;
  filter: drop-shadow(0 6px 14px rgba(var(--v-theme-on-surface), 0.06));
}

.mp-action-btn:hover {
  border-color: rgba(var(--v-theme-on-surface), 0.18);
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
