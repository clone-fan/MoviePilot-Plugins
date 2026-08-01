<template>
  <GlassCard class-name="signal-site-panel">
    <div class="signal-card-header">
      <h2 class="signal-card-heading">
        <SvgIcon :icon="signalIcons.leaf" color="#34C759" size="18" />
        站点数据
      </h2>
      <span class="signal-card-note">{{ dateNote }}</span>
    </div>
    <div class="signal-site-panel__body">
      <DonutRing
        :value="donutValue"
        :label="donutLabel"
        :segments="donutSegments"
        :pie-style="donutStyle"
      />
      <div class="signal-site-panel__content">
        <TrafficSummary :rows="summaryRows" />
        <div class="signal-site-card-list">
          <SiteTrafficCard
            v-for="site in sites"
            :key="site.name"
            :name="site.name"
            :icon="site.icon"
            :icon-color="site.iconColor"
            :percent="site.percent"
            :upload="site.upload"
            :download="site.download"
          />
        </div>
      </div>
    </div>
  </GlassCard>
</template>

<script setup>
import GlassCard from './primitives/GlassCard.vue'
import DonutRing from './DonutRing.vue'
import TrafficSummary from './TrafficSummary.vue'
import SiteTrafficCard from './SiteTrafficCard.vue'
import SvgIcon from './primitives/SvgIcon.vue'
import { signalIcons } from './icons.js'

defineProps({
  dateNote: { type: String, default: '今天 00:00 起' },
  donutValue: { type: [String, Number], default: '2' },
  donutLabel: { type: String, default: '个站点' },
  donutSegments: { type: Array, default: () => [] },
  donutStyle: { type: Object, default: () => ({}) },
  summaryRows: { type: Array, default: () => [] },
  sites: { type: Array, default: () => [] },
})
</script>
