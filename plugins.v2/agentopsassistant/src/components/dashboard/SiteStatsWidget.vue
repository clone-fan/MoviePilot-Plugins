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
          <div class="mp-site-stat">
            <span>上传增量</span>
            <strong>{{ formatBytes(siteChart.upload_total) }}</strong>
          </div>
          <div class="mp-site-stat">
            <span>下载增量</span>
            <strong>{{ formatBytes(siteChart.download_total) }}</strong>
          </div>
          <div class="mp-site-stat">
            <span>统计日期</span>
            <strong>{{ siteDateLabel }}</strong>
          </div>
        </div>

        <div v-if="hasSiteChart" class="mp-site-table">
          <div class="th">站点</div><div class="th">上传</div><div class="th">下载</div><div class="th">占比</div>
          <template v-for="site in siteTableRows" :key="site.name">
            <div class="mp-site-row-cell mp-site-name">
              <i class="mp-dot" :style="{ background: site.color, boxShadow: `0 0 8px ${site.glow}` }"></i>
              <span>{{ site.name }}</span>
            </div>
            <div class="mp-site-row-cell">↑ {{ formatBytes(site.upload) }}</div>
            <div class="mp-site-row-cell">↓ {{ formatBytes(site.download) }}</div>
            <div class="mp-site-row-cell">{{ sitePercent(site.value) }}</div>
          </template>
        </div>
        <div v-else class="mp-site-table mp-site-table--empty">
          <div class="th">站点</div><div class="th">上传</div><div class="th">下载</div><div class="th">占比</div>
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
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-height: 100%;
  padding: 18px;
  border-radius: var(--mp-widget-radius);
  border: 1px solid rgba(var(--v-border-color), var(--mp-widget-panel-line));
  background:
    radial-gradient(circle at 13% 10%, rgba(var(--v-theme-info), 0.10), transparent 36%),
    radial-gradient(circle at 76% 20%, rgba(var(--v-theme-primary), 0.075), transparent 34%),
    linear-gradient(180deg, rgba(var(--v-theme-surface), var(--mp-widget-panel-fill-hi)), rgba(var(--v-theme-surface), var(--mp-widget-panel-fill-lo)));
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
  color: rgb(var(--v-theme-info));
  background: rgba(var(--v-theme-info), 0.12);
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
  cursor: pointer;
}

.mp-site-body {
  flex: 1;
  min-height: 0;
  display: grid;
  grid-template-columns: 190px minmax(0, 1fr);
  gap: 16px;
}

.mp-donut-zone {
  min-height: 210px;
  display: grid;
  place-items: center;
  border-radius: var(--mp-widget-inner-radius);
  border: 1px solid rgba(var(--v-border-color), var(--mp-widget-cell-line));
  background:
    radial-gradient(circle at 50% 44%, rgba(var(--v-theme-on-surface), 0.055), transparent 54%),
    rgba(var(--v-theme-surface), var(--mp-widget-cell-fill));
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
    rgba(var(--v-theme-surface), 0.92);
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
  display: grid;
  grid-template-rows: 70px minmax(0, 1fr);
  gap: 13px;
}

.mp-site-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.mp-site-stat,
.mp-site-row-cell {
  min-width: 0;
  border-radius: var(--mp-widget-cell-radius);
  border: 1px solid rgba(var(--v-border-color), var(--mp-widget-cell-line));
  background:
    linear-gradient(180deg, rgba(var(--v-theme-on-surface), var(--mp-widget-cell-line-soft)), rgba(var(--v-theme-on-surface), 0.012)),
    rgba(var(--v-theme-surface), var(--mp-widget-cell-fill));
  box-shadow: var(--mp-widget-shadow-cell);
}

.mp-site-stat {
  padding: 12px 13px;
}

.mp-site-stat span,
.mp-site-table .th {
  color: rgba(var(--v-theme-on-surface), 0.58);
  font-size: 12px;
  font-weight: 700;
}

.mp-site-stat strong {
  display: block;
  margin-top: 7px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 17px;
  line-height: 1;
  font-weight: 780;
}

.mp-site-table {
  min-height: 0;
  display: grid;
  grid-template-columns: 1.05fr 1fr 1fr 0.72fr;
  gap: 9px 10px;
  align-content: start;
  overflow: auto;
  padding-right: 2px;
  color: rgba(var(--v-theme-on-surface), 0.88);
  font-size: 13px;
  font-weight: 650;
  scrollbar-width: thin;
}

.mp-site-row-cell {
  min-height: 34px;
  display: flex;
  align-items: center;
  padding: 0 10px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.mp-site-name {
  gap: 8px;
}

.mp-site-name span {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
}

.mp-dot {
  width: 8px;
  height: 8px;
  flex: 0 0 auto;
  border-radius: 999px;
}

.mp-site-table--empty {
  grid-auto-rows: 31px;
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
  .mp-site-body {
    grid-template-columns: 1fr;
  }

  .mp-donut-zone {
    min-height: 172px;
  }

  .mp-site-data {
    grid-template-rows: auto minmax(0, 1fr);
  }

  .mp-site-stats {
    grid-template-columns: 1fr;
  }

  .mp-site-table {
    grid-template-columns: 1.1fr 1fr 1fr;
  }

  .mp-site-table .th:nth-child(4),
  .mp-site-row-cell:nth-of-type(4n) {
    display: none;
  }
}
</style>
