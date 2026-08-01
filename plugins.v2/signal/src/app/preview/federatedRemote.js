import * as Vue from 'vue'

const DEFAULT_REMOTE_ENTRY = '/dist/assets/remoteEntry.js'
const vueVersion = Vue.version || '3.5.13'
const componentCache = new Map()

function createVueShareRecord() {
  return {
    from: 'signal-local-mp-final-preview',
    loaded: true,
    get: () => Promise.resolve(() => Vue),
  }
}

export function ensureFederationSharedVue() {
  globalThis.__federation_shared__ = globalThis.__federation_shared__ || {}
  const defaultScope = globalThis.__federation_shared__.default || {}
  defaultScope.vue = {
    ...(defaultScope.vue || {}),
    [vueVersion]: defaultScope.vue?.[vueVersion] || createVueShareRecord(),
  }
  globalThis.__federation_shared__.default = defaultScope
  return { vue: defaultScope.vue }
}

function normalizeExpose(expose) {
  return expose.startsWith('./') ? expose : `./${expose}`
}

export async function loadSignalRemoteComponent(expose, remoteEntry = DEFAULT_REMOTE_ENTRY) {
  const exposeName = normalizeExpose(expose)
  const cacheKey = `${remoteEntry}::${exposeName}`
  if (componentCache.has(cacheKey)) return componentCache.get(cacheKey)

  const shared = ensureFederationSharedVue()
  const remote = await import(/* @vite-ignore */ remoteEntry)
  remote.init?.(shared)
  const factory = await remote.get(exposeName)
  const module = await factory()
  const component = module?.default || module
  componentCache.set(cacheKey, component)
  return component
}

export async function preloadSignalRemoteComponents(remoteEntry = DEFAULT_REMOTE_ENTRY) {
  return Promise.all([
    loadSignalRemoteComponent('./Dashboard', remoteEntry),
    loadSignalRemoteComponent('./Config', remoteEntry),
  ])
}

export const finalPreviewRemoteEntry = DEFAULT_REMOTE_ENTRY
