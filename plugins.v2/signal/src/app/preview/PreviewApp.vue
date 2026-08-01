<script setup>
import { computed, defineAsyncComponent, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useTheme } from 'vuetify'
import { reloadConfigSavePayload, serializeConfigSavePayload } from '../../features/config/model/save-payload'
import { finalPreviewRemoteEntry, loadSignalRemoteComponent } from './federatedRemote'
import {
  configurePreviewConfigScenario,
  mockApi,
  previewApiCalls,
  setPreviewConfigRecord,
  setPreviewMasterEnabled,
} from './mockApi'

const params = new URLSearchParams(window.location.search)
if (params.get('masterEnabled') === 'false') setPreviewMasterEnabled(false)
else if (params.get('masterEnabled') === 'true') setPreviewMasterEnabled(true)
const previewConfigScenario = configurePreviewConfigScenario(params.get('configScenario') || 'baseline')
const initialView = params.get('view') || 'dashboard'
const initialSurface = params.get('surface') || 'dialog'
const initialTheme = params.get('theme') || 'transparent'
const themeCarrier = params.get('themeCarrier') === 'class-only' ? 'class-only' : 'data'
const initialWidget = ['site', 'actions'].includes(params.get('widget') || '') ? params.get('widget') : 'site'
const initialLoader = ['dist', 'source'].includes(params.get('loader') || '') ? params.get('loader') : 'dist'
const previewBuildId = params.get('previewBuild') || String(Date.now())
const view = ref(initialView)
const surface = ref(initialSurface)
const widget = ref(initialWidget)
const loaderMode = ref(initialLoader)
const previewConfigState = ref({ ...previewConfigScenario.initialConfig })
const previewConfigRecordState = ref(previewConfigScenario.recordState)
const previewConfigComponentKey = ref(0)
const previewSaveCount = ref(0)
const previewSaveRoundTrip = ref(false)
const previewCronValue = ref('')
const configHost = ref(null)
let configHostObserver = null
const themeOptions = ['transparent', 'dark', 'light', 'purple', 'system']
const normalizedInitialTheme = themeOptions.includes(initialTheme) ? initialTheme : 'transparent'
const systemDarkMedia = window.matchMedia('(prefers-color-scheme: dark)')
const systemPrefersDark = ref(systemDarkMedia.matches)
const themePreference = ref(normalizedInitialTheme)
const theme = useTheme()
const resolvedTheme = computed(() => (
  themePreference.value === 'system'
    ? (systemPrefersDark.value ? 'dark' : 'light')
    : themePreference.value
))
theme.global.name.value = resolvedTheme.value
const activeTheme = computed(() => theme.global.name.value)
const isTransparent = computed(() => activeTheme.value === 'transparent')
const remoteEntryUrl = `${finalPreviewRemoteEntry}?signalPreviewBuild=${encodeURIComponent(previewBuildId)}`

const title = computed(() => {
  if (view.value === 'config') return 'Config'
  if (view.value === 'dashboard' && surface.value === 'mp-widget') return 'Dashboard Widget'
  return 'Dashboard'
})

const DashboardComponent = defineAsyncComponent(() => (
  loaderMode.value === 'source'
    ? import('../Dashboard.vue').then(module => module.default)
    : loadSignalRemoteComponent('./Dashboard', remoteEntryUrl)
))

const ConfigComponent = defineAsyncComponent(() => (
  loaderMode.value === 'source'
    ? import('../Config.vue').then(module => module.default)
    : loadSignalRemoteComponent('./Config', remoteEntryUrl)
))
const modeTitle = computed(() => {
  if (view.value === 'config') return '插件设置'
  if (view.value === 'dashboard' && surface.value === 'mp-widget') return '仪表盘组件'
  return '插件详情'
})
const modeSubtitle = computed(() => {
  if (view.value === 'config') return '设定 / 插件 / MP 运维助手'
  if (view.value === 'dashboard' && surface.value === 'mp-widget') return '首页 / 仪表盘组件'
  return '插件 / MP 运维助手'
})
const transparencyOptions = ['low', 'medium', 'high']

function setTheme(name) {
  if (themeOptions.includes(name)) themePreference.value = name
}

function openDashboard(nextSurface = 'dialog', nextWidget = widget.value) {
  view.value = 'dashboard'
  surface.value = nextSurface
  widget.value = nextWidget
}

function openConfig() {
  view.value = 'config'
  surface.value = 'dialog'
}

async function handleConfigSave(payload) {
  previewSaveRoundTrip.value = false
  const serializedPayload = serializeConfigSavePayload(payload)
  const reloadedConfig = reloadConfigSavePayload(serializedPayload)
  setPreviewConfigRecord(reloadedConfig)
  previewConfigState.value = reloadedConfig
  previewConfigRecordState.value = 'present'
  previewConfigComponentKey.value += 1
  previewSaveCount.value += 1
  await nextTick()
  const remountedConfig = previewConfigState.value
  const sensitiveKeys = new Set([
    'backup_webdav_password',
  ])
  previewSaveRoundTrip.value = Object.entries(payload || {})
    .filter(([key]) => !sensitiveKeys.has(key))
    .every(([key, value]) => JSON.stringify(remountedConfig[key]) === JSON.stringify(value))
}

function syncPreviewCronValue() {
  const input = configHost.value?.querySelector('[data-field-key="dltag_cron"] input')
  if (input) previewCronValue.value = input.value
}

function handleConfigHostInput(event) {
  if (event.target?.closest?.('[data-field-key="dltag_cron"]')) syncPreviewCronValue()
}

// Transparency settings: mirrors official MP useTransparencySettings.ts
const transparencyPresets = {
  low: { opacity: 0.1, blur: 5 },
  medium: { opacity: 0.3, blur: 10 },
  high: { opacity: 0.6, blur: 15 },
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value))
}

function applyTransparencySettings(settings) {
  const normalized = {
    opacity: Number.isFinite(settings.opacity) ? clamp(settings.opacity, 0, 1) : 0.3,
    blur: Number.isFinite(settings.blur) ? clamp(settings.blur, 0, 30) : 10,
    backgroundPosterOpacity: Number.isFinite(settings.backgroundPosterOpacity)
      ? clamp(settings.backgroundPosterOpacity, 0, 1)
      : 0,
    backgroundBlur: Number.isFinite(settings.backgroundBlur) ? clamp(settings.backgroundBlur, 0, 30) : 16,
    level: settings.level,
  }
  const root = document.documentElement
  root.style.setProperty('--transparent-opacity', normalized.opacity.toString())
  root.style.setProperty('--transparent-opacity-light', (normalized.opacity * 0.67).toString())
  root.style.setProperty('--transparent-opacity-heavy', (normalized.opacity * 1.67).toString())
  root.style.setProperty('--transparent-blur', normalized.blur + 'px')
  root.style.setProperty('--transparent-blur-light', normalized.blur * 0.6 + 'px')
  root.style.setProperty('--transparent-blur-heavy', normalized.blur * 1.6 + 'px')
  root.style.setProperty('--transparent-background-poster-opacity', (1 - normalized.backgroundPosterOpacity).toString())
  root.style.setProperty('--transparent-background-blur', normalized.backgroundBlur + 'px')

  localStorage.setItem('transparency-opacity', normalized.opacity.toString())
  localStorage.setItem('transparency-blur', normalized.blur.toString())
  localStorage.setItem('transparency-background-poster-opacity', normalized.backgroundPosterOpacity.toString())
  localStorage.setItem('transparency-background-blur', normalized.backgroundBlur.toString())
  localStorage.setItem('transparency-level', normalized.level)
  return normalized
}

const transparencyLevel = ref(localStorage.getItem('transparency-level') || 'medium')
const transparencyOpacity = ref(parseFloat(localStorage.getItem('transparency-opacity') || '0.3'))
const transparencyBlur = ref(parseFloat(localStorage.getItem('transparency-blur') || '10'))

function adjustTransparency(level) {
  transparencyLevel.value = level
  const preset = transparencyPresets[level]
  if (preset) {
    transparencyOpacity.value = preset.opacity
    transparencyBlur.value = preset.blur
  }
  applyTransparencySettings({
    opacity: transparencyOpacity.value,
    blur: transparencyBlur.value,
    backgroundPosterOpacity: 0,
    backgroundBlur: 16,
    level,
  })
}

function applyMoviePilotThemeChrome(name, preference = themePreference.value) {
  const normalized = name || 'transparent'
  if (themeCarrier === 'data') {
    document.documentElement.setAttribute('data-theme', normalized)
    document.documentElement.setAttribute('data-theme-preference', preference)
    document.body.setAttribute('data-theme', normalized)
    document.body.setAttribute('data-theme-preference', preference)
  } else {
    document.documentElement.removeAttribute('data-theme')
    document.documentElement.removeAttribute('data-theme-preference')
    document.body.removeAttribute('data-theme')
    document.body.removeAttribute('data-theme-preference')
  }
  document.documentElement.setAttribute('data-signal-preview-theme-carrier', themeCarrier)
  document.documentElement.setAttribute('data-signal-preview-loader', loaderMode.value)
  document.documentElement.setAttribute('data-signal-preview-remote-entry', remoteEntryUrl)
  document.body.setAttribute('data-signal-preview-theme-carrier', themeCarrier)
  document.body.setAttribute('data-signal-preview-loader', loaderMode.value)
  const stored = {
    opacity: parseFloat(localStorage.getItem('transparency-opacity') || '0.3'),
    blur: parseFloat(localStorage.getItem('transparency-blur') || '10'),
    backgroundPosterOpacity: parseFloat(localStorage.getItem('transparency-background-poster-opacity') || '0'),
    backgroundBlur: parseFloat(localStorage.getItem('transparency-background-blur') || '16'),
    level: localStorage.getItem('transparency-level') || 'medium',
  }
  applyTransparencySettings(stored)
  const root = document.documentElement
  root.style.setProperty('--app-surface-radius', '18px')
  root.style.setProperty('--app-surface-radius-lg', '24px')
  root.style.setProperty('--app-surface-radius-md', '18px')
  root.style.setProperty('--app-control-radius', '12px')
  root.style.setProperty('--app-field-radius', '12px')
  root.style.setProperty('--app-surface-border', '1px solid rgba(var(--v-border-color), var(--v-border-opacity, 0.12))')
  root.style.setProperty('--app-surface-shadow', normalized === 'transparent'
    ? '0 18px 48px rgba(0, 0, 0, 0.18)'
    : '0 12px 36px rgba(0, 0, 0, 0.14)')
  root.style.setProperty('--app-surface-hover-shadow', '0 16px 42px rgba(0, 0, 0, 0.18)')
  root.style.setProperty('--v-card-border-radius', '18px')
  root.style.setProperty('--v-card-opacity', normalized === 'transparent' ? stored.opacity.toString() : '1')
}

function handleSystemThemeChange(event) {
  systemPrefersDark.value = event.matches
}

watch([resolvedTheme, themePreference], ([name, preference]) => {
  theme.global.name.value = name
  applyMoviePilotThemeChrome(name, preference)
}, { immediate: true })
onMounted(() => {
  systemDarkMedia.addEventListener('change', handleSystemThemeChange)
  applyMoviePilotThemeChrome(activeTheme.value, themePreference.value)
  window.__SIGNAL_PREVIEW_API__ = mockApi
  window.__SIGNAL_PREVIEW_API_CALLS__ = previewApiCalls
  configHostObserver = new MutationObserver(syncPreviewCronValue)
  if (configHost.value) configHostObserver.observe(configHost.value, { childList: true, subtree: true })
  nextTick(syncPreviewCronValue)
})
onBeforeUnmount(() => {
  systemDarkMedia.removeEventListener('change', handleSystemThemeChange)
  configHostObserver?.disconnect()
})
</script>

<template>
  <v-app :theme="activeTheme">
    <div class="signal-local-mp-shell" :class="['signal-local-mp-shell--' + activeTheme]">
      <aside class="signal-local-mp-sidebar">
        <div class="signal-local-mp-brand">
          <span class="signal-local-mp-brand__mark">MP</span>
          <span class="signal-local-mp-brand__text">MoviePilot</span>
        </div>
        <nav class="signal-local-mp-nav" aria-label="MoviePilot preview navigation">
          <button
            type="button"
            class="signal-local-mp-nav__item"
            :class="{ active: view === 'dashboard' && surface === 'dialog' }"
            @click="openDashboard('dialog')"
          >
            <VIcon icon="mdi-view-dashboard-outline" size="18" />
            <span>插件详情</span>
          </button>
          <button
            type="button"
            class="signal-local-mp-nav__item"
            :class="{ active: view === 'dashboard' && surface === 'mp-widget' }"
            @click="openDashboard('mp-widget')"
          >
            <VIcon icon="mdi-view-grid-outline" size="18" />
            <span>首页组件</span>
          </button>
          <button
            type="button"
            class="signal-local-mp-nav__item"
            :class="{ active: view === 'config' }"
            @click="openConfig"
          >
            <VIcon icon="mdi-cog-outline" size="18" />
            <span>插件设置</span>
          </button>
        </nav>
      </aside>

      <section class="signal-local-mp-frame">
        <header class="signal-local-mp-topbar">
          <div class="signal-local-mp-heading">
            <span>{{ modeSubtitle }}</span>
            <strong>{{ modeTitle }}</strong>
          </div>
          <div class="signal-local-mp-actions">
            <div class="signal-local-mp-segment" aria-label="Theme">
              <button
                v-for="name in themeOptions"
                :key="name"
                type="button"
                :class="{ active: themePreference === name }"
                :data-theme-option="name"
                @click="setTheme(name)"
              >
                {{ name }}
              </button>
            </div>
            <div v-if="isTransparent" class="signal-local-mp-segment" aria-label="Transparency">
              <button
                v-for="level in transparencyOptions"
                :key="level"
                type="button"
                :class="{ active: transparencyLevel === level }"
                @click="adjustTransparency(level)"
              >
                {{ level }}
              </button>
            </div>
          </div>
        </header>

        <main class="signal-local-mp-content">
          <div class="signal-local-mp-plugin-surface">
            <v-main class="preview-stage" :class="['preview-stage--' + view, 'preview-stage--' + surface]">
              <div v-if="view === 'dashboard' && surface === 'mp-widget'" class="mp-widget-host">
                <div class="dashboard-plugin-vue-renderer">
                  <component
                    :is="DashboardComponent"
                    :api="mockApi"
                    surface="mp-widget"
                    :allow-refresh="true"
                    :config="{ id: 'Signal', render_mode: 'vue', attrs: { component: widget, components: { [widget]: true } } }"
                  />
                </div>
              </div>
              <div v-else-if="view === 'dashboard'" class="plugin-app-page mp-app-page-host">
                <component
                  :is="DashboardComponent"
                  :api="mockApi"
                  :surface="surface"
                  :allow-refresh="true"
                />
              </div>
              <div
                v-else
                ref="configHost"
                class="mp-config-host"
                :data-config-scenario="previewConfigScenario.scenario"
                :data-config-record-state="previewConfigRecordState"
                :data-config-cron-value="previewCronValue"
                :data-config-save-round-trip="String(previewSaveRoundTrip)"
                :data-config-save-count="previewSaveCount"
                :data-config-mp-update-enabled="String(!!previewConfigState.mp_update_enabled)"
                :data-config-mp-update-schedule-enabled="String(!!previewConfigState.mp_update_schedule_enabled)"
                :data-config-market-update-enabled="String(!!previewConfigState.market_update_enabled)"
                :data-config-market-update-schedule-enabled="String(!!previewConfigState.market_update_schedule_enabled)"
                @input.capture="handleConfigHostInput"
              >
                <VCard class="mp-config-dialog-card">
                  <VCardText class="v-card-text pa-0 signal-config-scroll-host">
                    <component
                      :is="ConfigComponent"
                      :key="previewConfigComponentKey"
                      :api="mockApi"
                      :initial-config="previewConfigState"
                      :config-record-state="previewConfigRecordState"
                      @save="handleConfigSave"
                    />
                  </VCardText>
                </VCard>
              </div>
            </v-main>
          </div>
        </main>
      </section>
    </div>
  </v-app>
</template>

<style scoped>
:global(html),
:global(body),
:global(#app) {
  min-width: 0;
  min-height: 100%;
  margin: 0;
}

:global(body) {
  overflow: hidden;
  background: rgb(var(--v-theme-background));
}

:global(.v-application__wrap) {
  min-width: 0;
  min-height: 100vh;
  display: block;
}

:global(.v-btn) {
  min-width: 64px;
  min-height: 36px;
  padding-inline: 16px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border-radius: var(--app-control-radius, 12px);
  line-height: 1;
}

:global(.v-btn--variant-text) {
  min-width: auto;
  background: transparent;
}

:global(.v-btn__content),
:global(.v-btn__prepend),
:global(.v-btn__append) {
  min-width: 0;
  display: inline-flex;
  align-items: center;
}

:global(.v-btn__prepend) {
  margin-inline-end: 4px;
}

:global(.v-icon) {
  width: 1em;
  height: 1em;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 auto;
  font-size: 20px;
  line-height: 1;
}

:global(.v-icon__svg) {
  width: 1em;
  height: 1em;
  display: block;
}

.signal-local-mp-shell {
  --signal-local-nav-width: 248px;
  --signal-local-topbar-height: 66px;
  --signal-local-shell-surface: rgba(var(--v-theme-surface), var(--transparent-opacity, 0.3));
  --signal-local-panel-surface: rgba(var(--v-theme-surface), calc(var(--transparent-opacity, 0.3) * 0.74));
  --signal-local-line: rgba(var(--v-border-color), var(--v-border-opacity, 0.12));
  width: 100vw;
  height: 100vh;
  min-width: 0;
  display: grid;
  grid-template-columns: var(--signal-local-nav-width) minmax(0, 1fr);
  overflow: hidden;
  color: rgb(var(--v-theme-on-surface));
  background:
    linear-gradient(180deg, rgba(var(--v-theme-background), 0.96), rgba(var(--v-theme-background), 0.86)),
    rgb(var(--v-theme-background));
}

.signal-local-mp-shell--light {
  --signal-local-shell-surface: rgba(var(--v-theme-surface), 0.94);
  --signal-local-panel-surface: rgba(var(--v-theme-surface), 0.88);
}

.signal-local-mp-shell--dark,
.signal-local-mp-shell--purple {
  --signal-local-shell-surface: rgba(var(--v-theme-surface), 0.98);
  --signal-local-panel-surface: rgba(var(--v-theme-surface), 0.92);
}

.signal-local-mp-sidebar {
  min-width: 0;
  height: 100vh;
  padding: 18px 14px;
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
  gap: 18px;
  border-right: 1px solid var(--signal-local-line);
  background: var(--signal-local-shell-surface);
  backdrop-filter: blur(var(--transparent-blur, 10px));
  -webkit-backdrop-filter: blur(var(--transparent-blur, 10px));
}

.signal-local-mp-brand {
  min-width: 0;
  min-height: 42px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding-inline: 6px;
}

.signal-local-mp-brand__mark {
  width: 34px;
  height: 34px;
  display: inline-grid;
  place-items: center;
  flex: 0 0 auto;
  border-radius: 10px;
  color: rgb(var(--v-theme-on-primary));
  background: rgb(var(--v-theme-primary));
  font-size: 13px;
  font-weight: 700;
}

.signal-local-mp-brand__text {
  min-width: 0;
  color: rgb(var(--v-theme-on-surface));
  font-size: 15px;
  font-weight: 650;
}

.signal-local-mp-nav {
  min-width: 0;
  min-height: 0;
  display: grid;
  align-content: start;
  gap: 6px;
}

.signal-local-mp-nav__item {
  width: 100%;
  min-width: 0;
  min-height: 40px;
  padding: 0 12px;
  display: grid;
  grid-template-columns: 20px minmax(0, 1fr);
  align-items: center;
  gap: 10px;
  border: 0;
  border-radius: 10px;
  color: rgba(var(--v-theme-on-surface), 0.68);
  background: transparent;
  font: inherit;
  text-align: left;
  cursor: pointer;
}

.signal-local-mp-nav__item span {
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.signal-local-mp-nav__item.active,
.signal-local-mp-nav__item:hover {
  color: rgb(var(--v-theme-on-surface));
  background: rgba(var(--v-theme-primary), 0.14);
}

.signal-local-mp-frame {
  min-width: 0;
  min-height: 0;
  display: grid;
  grid-template-rows: var(--signal-local-topbar-height) minmax(0, 1fr);
}

.signal-local-mp-topbar {
  min-width: 0;
  min-height: var(--signal-local-topbar-height);
  padding: 0 22px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: center;
  gap: 18px;
  border-bottom: 1px solid var(--signal-local-line);
  background: var(--signal-local-panel-surface);
  backdrop-filter: blur(var(--transparent-blur, 10px));
  -webkit-backdrop-filter: blur(var(--transparent-blur, 10px));
}

.signal-local-mp-heading {
  min-width: 0;
  display: grid;
  gap: 2px;
}

.signal-local-mp-heading span {
  overflow: hidden;
  color: rgba(var(--v-theme-on-surface), 0.56);
  font-size: 12px;
  line-height: 1.25;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.signal-local-mp-heading strong {
  overflow: hidden;
  color: rgb(var(--v-theme-on-surface));
  font-size: 17px;
  font-weight: 650;
  line-height: 1.25;
  white-space: nowrap;
  text-overflow: ellipsis;
}

.signal-local-mp-actions {
  min-width: 0;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 8px;
}

.signal-local-mp-segment {
  min-width: 0;
  min-height: 34px;
  padding: 3px;
  display: flex;
  align-items: center;
  gap: 3px;
  border: 1px solid var(--signal-local-line);
  border-radius: 12px;
  background: rgba(var(--v-theme-surface), calc(var(--transparent-opacity, 0.3) * 0.62));
}

.signal-local-mp-segment button {
  min-width: 0;
  min-height: 26px;
  padding: 0 10px;
  border: 0;
  border-radius: 9px;
  color: rgba(var(--v-theme-on-surface), 0.66);
  background: transparent;
  font: inherit;
  font-size: 12px;
  cursor: pointer;
}

.signal-local-mp-segment button.active,
.signal-local-mp-segment button:hover {
  color: rgb(var(--v-theme-on-surface));
  background: rgba(var(--v-theme-primary), 0.18);
}

.signal-local-mp-content {
  min-width: 0;
  min-height: 0;
  padding: 22px;
  overflow: auto;
}

.signal-local-mp-plugin-surface {
  min-width: 0;
  min-height: 100%;
}

.preview-stage {
  min-width: 0;
  min-height: 0;
  padding: 0;
  overflow: visible;
}

.preview-stage--dialog {
  min-height: calc(100vh - var(--signal-local-topbar-height) - 44px);
}

.preview-stage--mp-widget {
  display: grid;
  place-items: start center;
  min-height: calc(100vh - var(--signal-local-topbar-height) - 44px);
}

.mp-widget-host {
  width: min(920px, 100%);
  height: 420px;
  border-radius: var(--app-surface-radius, 18px);
}

.dashboard-plugin-vue-renderer {
  display: flex;
  flex-direction: column;
  inline-size: 100%;
  block-size: 100%;
  min-block-size: 0;
}

.mp-app-page-host {
  min-width: 0;
  min-height: calc(100vh - var(--signal-local-topbar-height) - 44px);
}

.mp-config-host {
  max-width: 64rem;
  margin: 0 auto;
}

.mp-config-dialog-card {
  display: flex;
  flex-direction: column;
  height: clamp(640px, calc(100dvh - var(--signal-local-topbar-height) - 44px), 912px);
  max-height: calc(100dvh - var(--signal-local-topbar-height) - 44px);
  overflow: hidden;
  border: var(--app-surface-border, 1px solid rgba(var(--v-border-color), var(--v-border-opacity, 0.12)));
  border-radius: var(--app-surface-radius, 18px);
  background: rgba(var(--v-theme-surface), var(--transparent-opacity, 0.3));
  box-shadow: var(--app-surface-shadow, none);
  backdrop-filter: blur(var(--transparent-blur, 10px));
  -webkit-backdrop-filter: blur(var(--transparent-blur, 10px));
}

.mp-config-dialog-card :deep(.v-card-text.pa-0) {
  flex: 1 1 auto;
  height: 100%;
  min-height: 0;
  max-height: 100%;
  overflow: hidden;
}

@media (max-width: 760px) {
  .signal-local-mp-shell {
    width: 100vw;
    height: 100vh;
    grid-template-columns: 1fr;
    grid-template-rows: auto minmax(0, 1fr);
  }

  .signal-local-mp-sidebar {
    height: auto;
    min-height: 58px;
    padding: 10px;
    display: grid;
    grid-template-columns: auto minmax(0, 1fr);
    grid-template-rows: auto;
    align-items: center;
    gap: 10px;
    border-right: 0;
    border-bottom: 1px solid var(--signal-local-line);
  }

  .signal-local-mp-brand__text {
    display: none;
  }

  .signal-local-mp-nav {
    display: flex;
    align-items: center;
    gap: 6px;
    overflow-x: auto;
    scrollbar-width: none;
  }

  .signal-local-mp-nav::-webkit-scrollbar {
    width: 0;
    height: 0;
  }

  .signal-local-mp-nav__item {
    width: auto;
    min-width: 42px;
    grid-template-columns: 18px;
    justify-content: center;
    padding: 0 10px;
  }

  .signal-local-mp-nav__item span {
    display: none;
  }

  .signal-local-mp-frame {
    grid-template-rows: auto minmax(0, 1fr);
  }

  .signal-local-mp-topbar {
    min-height: auto;
    padding: 10px 12px;
    grid-template-columns: minmax(0, 1fr);
    gap: 10px;
  }

  .signal-local-mp-actions {
    justify-content: flex-start;
  }

  .signal-local-mp-segment {
    max-width: 100%;
    overflow-x: auto;
  }

  .signal-local-mp-content {
    padding: 12px;
  }

  .preview-stage {
    min-height: auto;
  }

  .mp-widget-host {
    height: 520px;
  }

  .mp-config-dialog-card :deep(.v-card-text.pa-0) {
    height: 100%;
    max-height: 100%;
  }

  .mp-config-dialog-card {
    height: calc(100dvh - 148px);
    max-height: calc(100dvh - 148px);
  }
}
</style>
