<script setup>
defineProps({
  loading: { type: Boolean, default: false },
  error: { type: String, default: '' },
  siteChart: { type: Object, default: () => ({}) },
  siteRows: { type: Array, default: () => [] },
  siteTableRows: { type: Array, default: () => [] },
  siteTrafficTotal: { type: Number, default: 0 },
  siteDateLabel: { type: String, default: '等待统计' },
  siteDateNote: { type: String, default: '等待统计' },
  sitePieStyle: { type: Object, default: () => ({}) },
  hasSiteChart: { type: Boolean, default: false },
  formatBytes: { type: Function, default: value => String(value || 0) },
  sitePercent: { type: Function, default: () => '0%' },
  allowRefresh: { type: Boolean, default: true },
})

const emit = defineEmits(['refresh'])
</script>

<template>
  <section class="mp-site-panel">
    <header class="mp-panel-head">
      <span class="mp-panel-icon"><VIcon icon="mdi-chart-line" size="19" /></span>
      <div>
        <h3>站点数据统计</h3>
        <p>{{ siteDateNote }}</p>
      </div>
      <VBtn
        v-if="allowRefresh"
        icon="mdi-refresh"
        size="small"
        variant="text"
        class="mp-refresh"
        :loading="loading"
        aria-label="刷新站点数据统计"
        @click="emit('refresh')"
      />
    </header>

    <VAlert v-if="error" type="error" density="compact" variant="tonal" :text="error" />
    <div v-else class="mp-site-body" :class="{ 'is-empty': !hasSiteChart }">
      <div class="mp-donut-zone">
        <div class="mp-donut" :class="{ 'mp-donut--empty': !hasSiteChart }" :style="sitePieStyle">
          <div class="mp-donut-core">
            <strong>{{ hasSiteChart ? siteRows.length : 0 }}</strong>
            <span>{{ hasSiteChart ? '站点' : '待刷新' }}</span>
          </div>
        </div>
      </div>

      <div class="mp-site-data">
        <div class="mp-site-stats">
          <div class="mp-site-stat mp-site-stat--upload">
            <span>上传增量</span>
            <strong>{{ formatBytes(siteChart.upload_total) }}</strong>
          </div>
          <div class="mp-site-stat mp-site-stat--download">
            <span>下载增量</span>
            <strong>{{ formatBytes(siteChart.download_total) }}</strong>
          </div>
          <div class="mp-site-stat mp-site-stat--date">
            <span>统计日期</span>
            <strong>{{ siteDateLabel }}</strong>
          </div>
        </div>

        <div v-if="hasSiteChart" class="mp-site-list">
          <article v-for="site in siteTableRows" :key="site.name" class="mp-site-card">
            <div class="mp-site-card-head">
              <i class="mp-dot" :style="{ background: site.color, boxShadow: `0 0 8px ${site.glow}` }"></i>
              <span class="mp-site-name">{{ site.name }}</span>
              <strong class="mp-site-percent">{{ sitePercent(site.value) }}</strong>
            </div>
            <div class="mp-site-card-metrics">
              <span class="mp-site-row-cell mp-site-upload">↑ {{ formatBytes(site.upload) }}</span>
              <span class="mp-site-row-cell mp-site-download">↓ {{ formatBytes(site.download) }}</span>
            </div>
          </article>
        </div>
        <div v-else class="mp-site-list mp-site-list--empty">
          <div class="mp-site-row-cell mp-site-empty-row">
            <VIcon icon="mdi-chart-pie" size="18" />
            <div>
              <strong>暂无站点增量</strong>
              <span>刷新后显示最近可用快照</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.mp-site-panel {
  --mp-widget-panel-source-opacity: var(--mp-widget-surface-opacity, var(--mp-widget-mp-surface-opacity));
  container-type: inline-size;
  display: flex;
  flex-direction: column;
  gap: 16px;
  box-sizing: border-box;
  height: 100%;
  min-height: 100%;
  padding: 18px;
  overflow: hidden;
  border-radius: var(--mp-widget-radius);
  border: 1px solid rgba(var(--v-border-color), var(--mp-widget-panel-line));
  background:
    radial-gradient(circle at 13% 10%, rgba(var(--v-theme-on-surface), 0.046), transparent 36%),
    radial-gradient(circle at 76% 20%, rgba(var(--v-theme-on-surface), 0.032), transparent 34%),
    linear-gradient(180deg, rgba(var(--v-theme-surface), var(--mp-widget-panel-fill-hi)), rgba(var(--v-theme-surface), var(--mp-widget-panel-fill-lo))),
    rgba(var(--v-theme-surface), var(--mp-widget-surface-opacity));
  box-shadow: var(--mp-widget-shadow-panel);
  backdrop-filter: blur(18px) saturate(145%);
  -webkit-backdrop-filter: blur(18px) saturate(145%);
}

.mp-panel-head {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto;
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
  box-shadow: var(--mp-widget-shadow-cell);
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

.mp-refresh {
  color: rgba(var(--v-theme-on-surface), 0.62);
  cursor: pointer;
}

.mp-site-body {
  flex: 1;
  min-height: 0;
  display: grid;
  grid-template-columns: 190px minmax(0, 1fr);
  gap: 16px;
  overflow: hidden;
}

.mp-donut-zone {
  min-height: 210px;
  display: grid;
  place-items: center;
  border-radius: var(--mp-widget-inner-radius);
  border: 1px solid rgba(var(--v-border-color), var(--mp-widget-cell-line));
  background:
    radial-gradient(circle at 50% 44%, rgba(var(--v-theme-on-surface), 0.055), transparent 54%),
    rgba(var(--v-theme-surface), var(--mp-widget-cell-fill)),
    rgba(var(--v-theme-surface), var(--mp-widget-surface-opacity));
  box-shadow: var(--mp-widget-shadow-cell);
}

.mp-donut {
  position: relative;
  width: 142px;
  height: 142px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  box-shadow:
    inset 0 1px 16px rgba(var(--v-theme-on-surface), 0.16),
    inset 0 -12px 22px rgba(0, 0, 0, 0.08),
    0 7px 18px rgba(16, 24, 40, 0.08);
}

.mp-donut--empty {
  filter: saturate(82%);
}

.mp-donut::after {
  content: "";
  position: absolute;
  inset: 30px;
  border-radius: 50%;
  background:
    radial-gradient(circle at 50% 18%, rgba(var(--v-theme-on-surface), 0.10), transparent 48%),
    rgba(var(--v-theme-surface), clamp(0.16, calc(var(--mp-widget-surface-opacity) + 0.24), 0.92));
  box-shadow:
    inset 0 1px 0 rgba(var(--v-theme-on-surface), 0.08),
    0 0 0 1px rgba(var(--v-border-color), 0.12);
}

.mp-donut-core {
  position: relative;
  z-index: 1;
  text-align: center;
}

.mp-donut-core strong {
  display: block;
  font-size: 28px;
  line-height: 1;
  font-weight: 840;
}

.mp-donut-core span {
  display: block;
  margin-top: 7px;
  color: rgba(var(--v-theme-on-surface), 0.58);
  font-size: 12px;
  font-weight: 700;
}

.mp-site-data {
  min-width: 0;
  min-height: 0;
  display: grid;
  grid-template-rows: auto minmax(0, 1fr);
  gap: 9px;
  overflow: hidden;
}

.mp-site-stats {
  min-height: 0;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
  overflow: hidden;
}

.mp-site-stat,
.mp-site-card,
.mp-site-row-cell {
  min-width: 0;
  border-radius: var(--mp-widget-cell-radius);
  border: 1px solid rgba(var(--v-border-color), var(--mp-widget-cell-line));
  background:
    linear-gradient(180deg, rgba(var(--v-theme-on-surface), var(--mp-widget-cell-line-soft)), rgba(var(--v-theme-on-surface), 0.012)),
    rgba(var(--v-theme-surface), var(--mp-widget-cell-fill)),
    rgba(var(--v-theme-surface), var(--mp-widget-surface-opacity));
  box-shadow: var(--mp-widget-shadow-cell);
}

.mp-site-stat {
  min-height: 32px;
  height: 32px;
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  align-items: center;
  gap: 6px;
  padding: 0 10px;
  overflow: hidden;
  contain: layout paint;
}

.mp-site-stat--date {
  grid-column: 1 / -1;
  grid-template-columns: auto minmax(0, 1fr);
  min-height: 30px;
  height: 30px;
}

.mp-site-stat span {
  color: rgba(var(--v-theme-on-surface), 0.58);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 11px;
  line-height: 1;
  font-weight: 700;
}

.mp-site-stat strong {
  display: block;
  margin: 0;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  text-align: right;
  font-size: 14px;
  line-height: 1;
  font-weight: 780;
}

.mp-site-list {
  min-height: 0;
  display: grid;
  gap: 9px;
  align-content: start;
  overflow: auto;
  padding-right: 2px;
  color: rgba(var(--v-theme-on-surface), 0.88);
  font-size: 13px;
  font-weight: 650;
  scrollbar-width: thin;
}

.mp-site-card {
  display: grid;
  grid-template-rows: 18px 30px;
  gap: 8px;
  padding: 10px 11px;
  overflow: hidden;
  contain: layout paint;
}

.mp-site-card-head {
  min-width: 0;
  min-height: 18px;
  display: flex;
  align-items: center;
  gap: 8px;
  overflow: hidden;
  line-height: 1;
}

.mp-site-card-metrics {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
}

.mp-site-row-cell {
  min-height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 9px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1;
}

.mp-site-name {
  flex: 1 1 auto;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.mp-dot {
  width: 8px;
  height: 8px;
  flex: 0 0 auto;
  border-radius: 999px;
}

.mp-site-percent {
  flex: 0 0 auto;
  color: rgba(var(--v-theme-on-surface), 0.88);
  font-size: 13px;
  line-height: 1;
  font-weight: 780;
}

.mp-site-list--empty {
  grid-auto-rows: auto;
}

.mp-site-empty-row {
  grid-column: 1 / -1;
  min-height: 72px;
  justify-content: center;
  gap: 12px;
  color: rgba(var(--v-theme-on-surface), 0.62);
  white-space: normal;
}

.mp-site-empty-row > div {
  min-width: 0;
  display: grid;
  gap: 4px;
}

.mp-site-empty-row strong {
  color: rgba(var(--v-theme-on-surface), 0.90);
  font-size: 13px;
  line-height: 1;
}

.mp-site-empty-row span {
  font-size: 12px;
  line-height: 1;
}

@media (max-width: 760px) {
  .mp-site-panel {
    gap: 10px;
    padding: 14px;
  }

  .mp-site-body {
    grid-template-columns: 1fr;
    gap: 10px;
  }

  .mp-donut-zone {
    min-height: 132px;
  }

  .mp-donut {
    width: 108px;
    height: 108px;
  }

  .mp-donut::after {
    inset: 24px;
  }

  .mp-donut-core strong {
    font-size: 24px;
  }

  .mp-donut-core span {
    margin-top: 5px;
  }

  .mp-site-data {
    grid-template-rows: auto minmax(0, 1fr);
    gap: 8px;
  }

  .mp-site-stats {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 6px;
  }

  .mp-site-stat {
    gap: 4px;
    padding: 0 8px;
    min-height: 30px;
    height: 30px;
  }

  .mp-site-stat--date {
    min-height: 28px;
    height: 28px;
  }

  .mp-site-stat strong {
    font-size: 12px;
    line-height: 1;
  }

  .mp-site-row-cell {
    min-height: 30px;
  }
}

@container (max-width: 560px) {
  .mp-site-panel {
    gap: 10px;
    padding: 14px;
  }

  .mp-panel-head {
    gap: 8px;
  }

  .mp-panel-icon {
    width: 28px;
    height: 28px;
    border-radius: 10px;
  }

  .mp-panel-head h3 {
    font-size: 15px;
  }

  .mp-site-body {
    grid-template-columns: 1fr;
    gap: 10px;
  }

  .mp-donut-zone {
    min-height: 132px;
  }

  .mp-donut {
    width: 108px;
    height: 108px;
  }

  .mp-donut::after {
    inset: 24px;
  }

  .mp-donut-core strong {
    font-size: 24px;
  }

  .mp-donut-core span {
    margin-top: 5px;
  }

  .mp-site-data {
    grid-template-rows: auto minmax(0, 1fr);
    gap: 8px;
  }

  .mp-site-stats {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 6px;
  }

  .mp-site-stat {
    gap: 4px;
    padding: 0 8px;
    min-height: 30px;
    height: 30px;
  }

  .mp-site-stat--date {
    min-height: 28px;
    height: 28px;
  }

  .mp-site-stat span {
    font-size: 11px;
  }

  .mp-site-stat strong {
    font-size: 12px;
    line-height: 1;
  }

  .mp-site-list {
    gap: 8px;
    padding-right: 0;
  }

  .mp-site-row-cell {
    min-height: 30px;
    padding-inline: 9px;
    white-space: nowrap;
    line-height: 1.25;
  }

  .mp-site-upload,
  .mp-site-download {
    justify-content: center;
  }
}
</style>
