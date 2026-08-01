<script setup>
import { computed } from 'vue'
import SiteDataPanel from '../../../shared/SiteDataPanel.vue'

const props = defineProps({
  data: { type: Object, required: true },
  frame: { type: Object, default: () => ({}) },
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
})

const dateNote = computed(() => props.data.dateNote?.value || '今天 00:00 起')
const donutValue = computed(() => props.data.donutValue?.value || '0')
const sitePieSegments = computed(() => props.data.sitePieSegments?.value || [])
const sitePieStyle = computed(() => props.data.sitePieStyle?.value || {})
const dashboardDonutStyle = computed(() => {
  const style = sitePieStyle.value
  const background = typeof style?.background === 'string' ? style.background : ''
  if (!background) return style

  const dashboardPalette = {
    '--line': '255, 255, 255',
    '--green': '91, 204, 155',
    '--cyan': '124, 194, 224',
    '--blue': '142, 169, 222',
    '--amber': '218, 179, 93',
    '--red': '232, 104, 124',
    '--violet': '162, 151, 211',
  }

  return {
    ...style,
    background: Object.entries(dashboardPalette).reduce(
      (value, [token, color]) => value.replaceAll(`var(${token})`, color),
      background,
    ),
  }
})
const trafficSummaryRows = computed(() => props.data.trafficSummaryRows?.value || [])
const siteCards = computed(() => props.data.siteCards?.value || [])
const frameVariant = computed(() => props.frame?.variant || 'mp-native')
const frameDensity = computed(() => props.frame?.density || 'comfortable')
</script>

<template>
  <VCard
    class="signal-mp-free-widget signal-mp-native-card dashboard-summary-card dashboard-grid-fill"
    elevation="0"
    rounded="lg"
    data-free-widget="site"
    data-mp-frame-component="site"
    data-module-root-is-frame="true"
    :data-mp-frame-variant="frameVariant"
    :data-mp-frame-density="frameDensity"
    :data-loading="loading ? 'true' : 'false'"
    :data-error="error ? 'true' : 'false'"
  >
    <SiteDataPanel
      class="signal-finalized-site-content"
      :date-note="dateNote"
      :donut-value="donutValue"
      donut-label="个站点"
      :donut-segments="sitePieSegments"
      :donut-style="dashboardDonutStyle"
      :summary-rows="trafficSummaryRows"
      :sites="siteCards"
    />
  </VCard>
</template>

<style scoped>
.signal-mp-native-card {
  display: flex;
  inline-size: 100%;
  block-size: 100%;
  min-inline-size: 0;
  min-block-size: 0;
  box-sizing: border-box;
  flex-direction: column;
  overflow: hidden;
}

.signal-finalized-site-content {
  inline-size: 100%;
  block-size: 100%;
  min-block-size: 0;
  box-sizing: border-box;
  padding-inline: 8px;
  container-name: signal-site-data;
  container-type: inline-size;
  border: 0;
  border-radius: 0;
  background: transparent;
  box-shadow: none;
  overflow: hidden;
  backdrop-filter: none;
  -webkit-backdrop-filter: none;
}

.signal-finalized-site-content :deep(:is(
  .signal-card-heading,
  .signal-traffic-summary__value
)) {
  color: rgba(var(--v-theme-on-surface, 58, 53, 65), 0.94);
}

.signal-finalized-site-content :deep(.signal-site-traffic-card__name) {
  color: rgba(var(--v-theme-on-surface, 58, 53, 65), 0.84);
}

.signal-finalized-site-content :deep(:is(
  .signal-card-heading small,
  .signal-card-note,
  .signal-traffic-summary__label,
  .signal-traffic-summary__icon,
  .signal-site-traffic-card__percent,
  .signal-site-traffic-card__metric-pill
)) {
  color: rgba(var(--v-theme-on-surface, 58, 53, 65), 0.62);
}

.signal-finalized-site-content :deep(.signal-card-header) {
  border-block-end-color: rgba(var(--v-border-color, 58, 53, 65), 0.12);
}

.signal-finalized-site-content :deep(.signal-traffic-summary__pill),
.signal-finalized-site-content :deep(.signal-site-traffic-card) {
  background: rgba(var(--v-theme-on-surface, 58, 53, 65), 0.052);
  border-color: rgba(var(--v-border-color, 58, 53, 65), 0.12);
}

.signal-finalized-site-content :deep(.signal-traffic-summary__icon),
.signal-finalized-site-content :deep(.signal-site-traffic-card__percent) {
  background: rgba(var(--v-theme-on-surface, 58, 53, 65), 0.055);
}

.signal-finalized-site-content :deep(.signal-site-traffic-card__metric-pill) {
  background: rgba(var(--v-theme-on-surface, 58, 53, 65), 0.032);
  border-color: rgba(var(--v-border-color, 58, 53, 65), 0.12);
}

.signal-finalized-site-content :deep(.signal-card-header) {
  min-inline-size: 0;
  flex-wrap: wrap;
}

.signal-finalized-site-content :deep(.signal-card-heading),
.signal-finalized-site-content :deep(.signal-card-note) {
  min-inline-size: 0;
  max-inline-size: 100%;
  overflow-wrap: anywhere;
}

.signal-finalized-site-content :deep(.signal-site-panel__body) {
  flex: 1 1 0;
  min-block-size: 0;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 14px;
  padding-block-start: 0;
  overflow: hidden;
}

.signal-finalized-site-content :deep(.signal-site-panel__content) {
  flex: 1 1 0;
  min-inline-size: 0;
  min-block-size: 0;
  display: flex;
  flex-direction: column;
  gap: 14px;
  overflow: hidden;
}

.signal-finalized-site-content :deep(.signal-traffic-summary) {
  flex: 0 0 auto;
  grid-template-columns: minmax(0, 1fr);
}

.signal-finalized-site-content :deep(.signal-traffic-summary__pill) {
  min-inline-size: 0;
  border-radius: 18px;
}

.signal-finalized-site-content :deep(.signal-traffic-summary__label),
.signal-finalized-site-content :deep(.signal-traffic-summary__value) {
  white-space: normal;
  overflow-wrap: anywhere;
}

.signal-finalized-site-content :deep(.signal-site-card-list) {
  flex: 1 1 0;
  min-inline-size: 0;
  min-block-size: 0;
  max-block-size: none;
  align-content: start;
  grid-auto-rows: max-content;
  overflow: hidden auto;
}

.signal-finalized-site-content :deep(.signal-site-traffic-card) {
  min-inline-size: 0;
  block-size: 60px;
  min-block-size: 60px;
  max-block-size: 60px;
  grid-template-columns: minmax(0, 1fr);
  align-items: stretch;
  align-self: start;
  overflow: hidden;
}

.signal-finalized-site-content :deep(.signal-site-traffic-card__metrics) {
  justify-content: flex-start;
  flex-wrap: wrap;
}

.signal-finalized-site-content :deep(.signal-site-traffic-card__percent) {
  justify-self: start;
}

@container signal-site-data (max-width: 419.98px) {
  .signal-finalized-site-content :deep(.signal-card-header) {
    gap: 6px;
  }

  .signal-finalized-site-content :deep(.signal-card-heading) {
    flex-wrap: wrap;
    gap: 4px;
    font-size: 12px;
  }

  .signal-finalized-site-content :deep(.signal-card-note) {
    flex: 1 1 100%;
  }

  .signal-finalized-site-content :deep(.signal-site-panel__body),
  .signal-finalized-site-content :deep(.signal-traffic-summary),
  .signal-finalized-site-content :deep(.signal-site-card-list) {
    gap: 6px;
  }

  .signal-finalized-site-content :deep(.signal-site-panel__body),
  .signal-finalized-site-content :deep(.signal-site-panel__content) {
    gap: 8px;
  }

  .signal-finalized-site-content :deep(.signal-traffic-summary__pill) {
    min-block-size: 36px;
    grid-template-columns: 20px minmax(0, 1fr);
    gap: 4px;
    padding: 4px 6px;
  }

  .signal-finalized-site-content :deep(.signal-traffic-summary__icon) {
    inline-size: 20px;
    block-size: 20px;
  }

  .signal-finalized-site-content :deep(.signal-site-traffic-card) {
    grid-template-columns: minmax(0, 1fr) auto;
    grid-template-areas:
      "identity percent"
      "metrics metrics";
    align-items: center;
    padding: 4px 6px;
    column-gap: 6px;
    row-gap: 4px;
  }

  .signal-finalized-site-content :deep(.signal-site-traffic-card__identity) {
    grid-area: identity;
    min-inline-size: 0;
    gap: 4px;
  }

  .signal-finalized-site-content :deep(.signal-site-traffic-card__metrics) {
    grid-area: metrics;
    min-inline-size: 0;
    inline-size: 100%;
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 4px;
  }

  .signal-finalized-site-content :deep(.signal-site-traffic-card__metric-pill) {
    min-inline-size: 0;
    min-block-size: 22px;
    max-inline-size: none;
    inline-size: 100%;
    overflow: hidden;
    padding: 2px 4px;
    gap: 3px;
    white-space: nowrap;
  }

  .signal-finalized-site-content :deep(.signal-site-traffic-card__percent) {
    grid-area: percent;
    justify-self: end;
    min-inline-size: 0;
    max-inline-size: 100%;
    padding-inline: 4px;
    white-space: nowrap;
  }
}

@container signal-site-data (min-width: 420px) {
  .signal-finalized-site-content :deep(.signal-traffic-summary) {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .signal-finalized-site-content :deep(.signal-site-traffic-card) {
    grid-template-columns: minmax(120px, 1fr) auto auto;
    align-items: center;
  }

  .signal-finalized-site-content :deep(.signal-site-traffic-card__metrics) {
    flex-wrap: nowrap;
  }

  .signal-finalized-site-content :deep(.signal-site-traffic-card__percent) {
    justify-self: end;
  }
}

@container signal-site-data (min-width: 608px) {
  .signal-finalized-site-content :deep(.signal-site-panel__body) {
    flex-direction: row;
    column-gap: 30px;
  }

  .signal-finalized-site-content :deep(.signal-donut) {
    align-self: center;
  }

  .signal-finalized-site-content :deep(.signal-site-panel__content) {
    align-self: stretch;
  }
}
</style>
