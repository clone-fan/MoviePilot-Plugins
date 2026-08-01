<template>
  <article class="signal-glass-card-light signal-site-traffic-card">
    <div class="signal-site-traffic-card__identity">
      <span class="signal-site-traffic-card__icon">
        <SvgIcon :icon="icon" :color="iconColor" size="14" />
      </span>
      <span class="signal-site-traffic-card__name">
        {{ name }}
      </span>
    </div>
    <div class="signal-site-traffic-card__metrics">
      <span class="signal-site-traffic-card__metric-pill signal-site-traffic-card__metric-pill--upload">
        <SvgIcon :icon="signalIcons.arrowUp" size="10" />
        {{ upload }}
      </span>
      <span class="signal-site-traffic-card__metric-pill signal-site-traffic-card__metric-pill--download">
        <SvgIcon :icon="signalIcons.arrowDown" size="10" />
        {{ download }}
      </span>
    </div>
    <span class="signal-site-traffic-card__percent">
      <span class="signal-site-traffic-card__percent-icon">
        <SvgIcon :icon="signalIcons.chartPie" size="9" />
      </span>
      {{ percent }}
    </span>
  </article>
</template>

<script setup>
import { signalIcons } from './icons.js'
import SvgIcon from './primitives/SvgIcon.vue'

defineProps({
  name: { type: String, default: '馒头' },
  icon: { type: String, default: signalIcons.yinYang },
  iconColor: { type: String, default: '#34C759' },
  percent: { type: String, default: '100%' },
  upload: { type: String, default: '64.45 GB' },
  download: { type: String, default: '58.00 GB' },
})
</script>
