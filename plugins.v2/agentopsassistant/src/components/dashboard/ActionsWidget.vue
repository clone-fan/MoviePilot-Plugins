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
        :class="[`mp-action-btn--${action.tone}`]"
        :loading="actionRunning === action.path"
        :disabled="!!actionRunning && actionRunning !== action.path"
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
      :type="actionOk ? 'success' : 'error'"
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
  display: flex;
  flex-direction: column;
  gap: 14px;
  min-height: 100%;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid rgba(var(--v-border-color), 0.14);
  background:
    radial-gradient(circle at 14% 0%, rgba(var(--v-theme-primary), 0.10), transparent 34%),
    linear-gradient(180deg, rgba(var(--v-theme-surface), 0.86), rgba(var(--v-theme-surface), 0.64));
  box-shadow: 0 10px 28px rgba(16, 24, 40, 0.06);
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
  border-radius: 8px;
  color: rgb(var(--v-theme-primary));
  background: rgba(var(--v-theme-primary), 0.10);
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
  gap: 10px;
}

.mp-action-btn {
  min-width: 0;
  min-height: 58px;
  justify-content: stretch;
  border-radius: 8px;
  border: 1px solid rgba(var(--v-border-color), 0.12);
  color: rgba(var(--v-theme-on-surface), 0.90);
  background:
    linear-gradient(180deg, rgba(var(--v-theme-on-surface), 0.045), rgba(var(--v-theme-on-surface), 0.014)),
    rgba(var(--v-theme-surface), 0.58);
  cursor: pointer;
  transition: border-color 180ms ease, background 180ms ease, transform 180ms ease;
}

.mp-action-btn:hover {
  border-color: rgba(var(--v-theme-primary), 0.24);
  background:
    linear-gradient(180deg, rgba(var(--v-theme-on-surface), 0.065), rgba(var(--v-theme-on-surface), 0.020)),
    rgba(var(--v-theme-surface), 0.76);
}

.mp-action-btn:focus-visible {
  outline: 2px solid rgba(var(--v-theme-primary), 0.62);
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
  border-radius: 8px;
  color: rgb(var(--v-theme-primary));
  background: rgba(var(--v-theme-primary), 0.10);
}

.mp-action-btn--green .mp-action-icon {
  color: rgb(var(--v-theme-success));
  background: rgba(var(--v-theme-success), 0.10);
}

.mp-action-btn--cyan .mp-action-icon,
.mp-action-btn--blue .mp-action-icon {
  color: rgb(var(--v-theme-info));
  background: rgba(var(--v-theme-info), 0.10);
}

.mp-action-btn--violet .mp-action-icon {
  color: rgb(var(--v-theme-primary));
  background: rgba(var(--v-theme-primary), 0.10);
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
}
</style>
