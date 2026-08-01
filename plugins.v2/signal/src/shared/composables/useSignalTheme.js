import { computed } from 'vue'
import { useTheme } from 'vuetify'

const supportedThemes = ['transparent', 'dark', 'light', 'purple']

function normalizeThemeName(value) {
  const name = String(value || '').toLowerCase()
  return supportedThemes.find(theme => name.includes(theme)) || 'dark'
}

// Federation roots use this class instead of relying on Vuetify's .v-theme--*
// selectors, which are removed from plugin CSS during the MoviePilot build.
export function useSignalTheme() {
  const vuetifyTheme = useTheme()
  const themeName = computed(() => normalizeThemeName(vuetifyTheme.global.name.value))
  const rootThemeClass = computed(() => `signal-theme--${themeName.value}`)

  return { themeName, rootThemeClass }
}
