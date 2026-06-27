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
    <div v-else-if="hasSiteChart" class="mp-site-body">
      <div class="mp-donut-zone">
        <div class="mp-donut" :class="{ 'mp-donut--empty': !hasSiteChart }" :style="sitePieStyle">
          <div class="mp-donut-core">
            <strong>{{ siteRows.length }}</strong>
            <span>站点</span>
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

        <div class="mp-site-list">
          <div class="mp-site-table">
            <div class="mp-site-table-head">
              <span>站点</span>
              <span>上传</span>
              <span>下载</span>
              <span>占比</span>
            </div>
            <div v-for="site in siteTableRows" :key="site.name" class="mp-site-table-row">
              <span class="mp-site-table-name">
                <i class="mp-dot" :style="{ background: site.color, boxShadow: `0 0 8px ${site.glow}` }"></i>
                <span class="mp-site-name">{{ site.name }}</span>
              </span>
              <span class="mp-site-table-number mp-site-upload">↑ {{ formatBytes(site.upload) }}</span>
              <span class="mp-site-table-number mp-site-download">↓ {{ formatBytes(site.download) }}</span>
              <strong class="mp-site-table-percent">{{ sitePercent(site.value) }}</strong>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div v-else class="mp-site-empty-state">
      <div class="mp-empty-main">
        <span class="mp-empty-icon"><VIcon icon="mdi-chart-pie" size="19" /></span>
        <div>
          <strong>暂无站点增量</strong>
          <span>刷新后显示最近可用快照</span>
        </div>
      </div>
      <div class="mp-empty-stats">
        <div class="mp-site-stat mp-site-stat--upload">
          <span>上传增量</span>
          <strong>0.0 MB</strong>
        </div>
        <div class="mp-site-stat mp-site-stat--download">
          <span>下载增量</span>
          <strong>0.0 MB</strong>
        </div>
        <div class="mp-site-stat mp-site-stat--date">
          <span>统计日期</span>
          <strong>{{ siteDateLabel }}</strong>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.mp-site-panel {
  /* 外框：贴 MP 官方 surface */
  --mp-panel-radius: var(--app-surface-radius, 12px);
  --mp-panel-border: var(--app-surface-border, 1px solid rgba(var(--v-border-color), var(--v-border-opacity, 0.12)));
  --mp-panel-shadow: var(--app-surface-shadow, none);
  --mp-panel-surface: rgb(var(--v-theme-surface));
  /* 内框：on-surface 透白做层次 */
  --mp-cell-radius: var(--app-field-radius, 10px);
  --mp-cell-border: 1px solid rgba(var(--v-border-color), var(--v-border-opacity, 0.10));
  --mp-cell-surface: rgba(var(--v-theme-on-surface), 0.04);
  --mp-cell-hover-surface: rgba(var(--v-theme-on-surface), 0.08);
  --mp-cell-muted-surface: rgba(var(--v-theme-on-surface), 0.045);
  --mp-cell-shadow: none;
  --mp-blur: none;
  --mp-empty-min: 132px;
  container-type: inline-size;
  display: flex;
  flex-direction: column;
  gap: 14px;
  box-sizing: border-box;
  height: 100%;
  min-height: 100%;
  padding: 18px;
  overflow: hidden;
  border-radius: var(--mp-panel-radius);
  border: var(--mp-panel-border);
  background: var(--mp-panel-surface);
  box-shadow: var(--mp-panel-shadow);
  backdrop-filter: var(--mp-blur);
  -webkit-backdrop-filter: var(--mp-blur);
}

:global(html[data-theme="transparent"]) .mp-site-panel {
  --mp-panel-surface: rgba(var(--v-theme-surface), var(--transparent-opacity));
  --mp-cell-surface: rgba(var(--v-theme-surface), var(--transparent-opacity-light));
  --mp-cell-hover-surface: rgba(var(--v-theme-surface), var(--transparent-opacity-heavy));
  --mp-blur: blur(var(--transparent-blur));
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
  background: var(--mp-cell-muted-surface);
  box-shadow: var(--mp-cell-shadow);
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
  grid-template-columns: clamp(150px, 24%, 190px) minmax(0, 1fr);
  gap: clamp(10px, 1.4vw, 16px);
  overflow: hidden;
}

.mp-donut-zone {
  min-height: clamp(136px, 100%, 190px);
  display: grid;
  place-items: center;
  border-radius: var(--mp-cell-radius);
  border: var(--mp-cell-border);
  background: var(--mp-cell-surface);
  box-shadow: var(--mp-cell-shadow);
}

.mp-donut {
  position: relative;
  width: clamp(112px, 10.4vw, 142px);
  height: clamp(112px, 10.4vw, 142px);
  display: grid;
  place-items: center;
  border-radius: 50%;
  box-shadow: inset 0 0 0 1px rgba(var(--v-border-color), var(--v-border-opacity, 0.12));
}

.mp-donut--empty {
  opacity: 0.72;
}

.mp-donut::after {
  content: "";
  position: absolute;
  inset: 30px;
  border-radius: 50%;
  background: var(--mp-panel-surface);
  box-shadow: inset 0 0 0 1px rgba(var(--v-border-color), var(--v-border-opacity, 0.12));
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
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
  overflow: hidden;
}

.mp-site-stat,
.mp-site-row-cell {
  min-width: 0;
  border-radius: var(--mp-cell-radius);
  border: var(--mp-cell-border);
  background: var(--mp-cell-surface);
  box-shadow: var(--mp-cell-shadow);
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
  gap: 0;
  align-content: start;
  overflow: auto;
  padding-right: 2px;
  color: rgba(var(--v-theme-on-surface), 0.88);
  font-size: 13px;
  font-weight: 650;
  scrollbar-width: thin;
}

.mp-site-table {
  min-width: 0;
  display: grid;
  gap: 6px;
  padding: 8px;
  border-radius: var(--mp-cell-radius);
  border: var(--mp-cell-border);
  background: var(--mp-cell-surface);
  overflow: hidden;
  contain: layout paint;
}

.mp-site-table-head,
.mp-site-table-row {
  min-width: 0;
  display: grid;
  grid-template-columns: minmax(0, 1.35fr) minmax(72px, 0.82fr) minmax(72px, 0.82fr) minmax(46px, 0.46fr);
  align-items: center;
  gap: 7px;
  overflow: hidden;
  line-height: 1;
}

.mp-site-table-head {
  min-height: 24px;
  padding: 0 8px;
  color: rgba(var(--v-theme-on-surface), 0.58);
  font-size: 11px;
  font-weight: 760;
}

.mp-site-table-head span:nth-child(n+2) {
  text-align: right;
}

.mp-site-table-row {
  min-height: 33px;
  border-radius: calc(var(--mp-cell-radius) - 2px);
  border: var(--mp-cell-border);
  padding: 0 8px;
  background: var(--mp-panel-surface);
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

.mp-site-table-name {
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  overflow: hidden;
}

.mp-site-table-number,
.mp-site-table-percent {
  min-width: 0;
  display: block;
  text-align: right;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.mp-dot {
  width: 8px;
  height: 8px;
  flex: 0 0 auto;
  border-radius: 999px;
}

.mp-site-table-percent {
  color: rgba(var(--v-theme-on-surface), 0.88);
  font-size: 13px;
  line-height: 1;
  font-weight: 780;
}

.mp-site-list--empty {
  grid-auto-rows: auto;
}

.mp-site-empty-state {
  min-height: var(--mp-empty-min);
  display: grid;
  grid-template-columns: minmax(180px, 0.72fr) minmax(0, 1fr);
  align-items: stretch;
  gap: 10px;
  overflow: hidden;
}

.mp-empty-main,
.mp-empty-stats {
  min-width: 0;
  border-radius: var(--mp-cell-radius);
  border: var(--mp-cell-border);
  background: var(--mp-cell-surface);
  box-shadow: var(--mp-cell-shadow);
}

.mp-empty-main {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  color: rgba(var(--v-theme-on-surface), 0.62);
}

.mp-empty-icon {
  width: 36px;
  height: 36px;
  flex: 0 0 auto;
  display: grid;
  place-items: center;
  border-radius: var(--mp-cell-radius);
  color: rgba(var(--v-theme-on-surface), 0.72);
  background: var(--mp-cell-muted-surface);
}

.mp-empty-main > div {
  min-width: 0;
  display: grid;
  gap: 4px;
}

.mp-empty-main strong {
  color: rgba(var(--v-theme-on-surface), 0.90);
  font-size: 13px;
  line-height: 1.15;
}

.mp-empty-main span {
  font-size: 12px;
  line-height: 1.2;
}

.mp-empty-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  align-content: center;
  gap: 8px;
  padding: 10px;
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

  .mp-site-empty-state {
    grid-template-columns: 1fr;
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
    grid-template-columns: repeat(3, minmax(0, 1fr));
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

  .mp-site-table {
    padding: 7px;
  }

  .mp-site-table-head,
  .mp-site-table-row {
    grid-template-columns: minmax(0, 1.2fr) minmax(70px, 0.8fr) minmax(70px, 0.8fr) 46px;
    gap: 6px;
    padding-inline: 7px;
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

  .mp-site-empty-state {
    grid-template-columns: 1fr;
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
    grid-template-columns: repeat(3, minmax(0, 1fr));
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
    padding-right: 0;
  }

  .mp-site-table {
    padding: 7px;
  }

  .mp-site-table-head,
  .mp-site-table-row {
    grid-template-columns: minmax(0, 1.2fr) minmax(70px, 0.8fr) minmax(70px, 0.8fr) 46px;
    gap: 6px;
    padding-inline: 7px;
  }

  .mp-site-upload,
  .mp-site-download {
    text-align: right;
  }
}

@container (max-width: 390px) {
  .mp-site-stats {
    grid-template-columns: 1fr;
  }

  .mp-empty-stats {
    grid-template-columns: 1fr;
  }

  .mp-site-table-head,
  .mp-site-table-row {
    grid-template-columns: minmax(0, 1fr) minmax(64px, 0.72fr) minmax(64px, 0.72fr) 42px;
    gap: 5px;
    padding-inline: 6px;
  }

  .mp-site-table-head {
    font-size: 10px;
  }

  .mp-site-table-number,
  .mp-site-table-percent {
    font-size: 11px;
  }
}
</style>
