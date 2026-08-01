<template>
  <div class="signal-donut" :class="{ 'signal-donut--empty': !normalizedSegments.length }" :style="ringStyle" :aria-label="ariaLabel">
    <div class="signal-donut__inner">
      <span>
        <strong class="signal-donut__value">{{ value }}</strong>
        <small class="signal-donut__label">{{ label }}</small>
      </span>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  value: { type: [String, Number], default: '2' },
  label: { type: String, default: '个站点' },
  segments: { type: Array, default: () => [] },
  pieStyle: { type: Object, default: () => ({}) },
})

const normalizedSegments = computed(() => Array.isArray(props.segments) ? props.segments : [])
const ringStyle = computed(() => {
  if (props.pieStyle && typeof props.pieStyle === 'object' && Object.keys(props.pieStyle).length) {
    return props.pieStyle
  }
  return {
    background: 'conic-gradient(rgba(var(--line), 0.16) 0 82deg, rgba(var(--line), 0.055) 82deg 360deg)',
  }
})
const ariaLabel = computed(() => {
  if (!normalizedSegments.value.length) return `${props.value} ${props.label}，暂无站点流量分段`
  const names = normalizedSegments.value.map(item => item?.name).filter(Boolean).slice(0, 4).join('、')
  return `${props.value} ${props.label}，按 PT 站点${names ? ` ${names}` : ''} 流量分段`
})
</script>

<style>
.signal-donut {
  inline-size: min(140px, 100%);
  block-size: auto;
  aspect-ratio: 1;
  border-radius: 50%;
  flex: 0 0 auto;
  align-self: center;
  display: grid;
  place-items: center;
  background: conic-gradient(rgba(var(--line), 0.16) 0 82deg, rgba(var(--line), 0.055) 82deg 360deg);
}

.signal-donut--empty {
  opacity: 0.82;
}

.signal-donut__inner {
  inline-size: min(100px, 71.428571%);
  block-size: auto;
  aspect-ratio: 1;
  border-radius: 50%;
  display: grid;
  place-items: center;
  background:
    linear-gradient(145deg, rgba(255, 255, 255, 0.16), rgba(255, 255, 255, 0.055)),
    rgba(28, 28, 30, 0.48);
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow: inset 0 1px 14px rgba(255, 255, 255, 0.045), inset 0 -10px 22px rgba(0, 0, 0, 0.22);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.signal-donut__value {
  display: block;
  font-size: 28px;
  line-height: 1;
  font-weight: 780;
  color: #f2f2f7;
  text-align: center;
}

.signal-donut__label {
  display: block;
  margin-block-start: 5px;
  font-size: 12px;
  line-height: 1;
  color: rgba(242, 242, 247, 0.72);
  text-align: center;
}
</style>
