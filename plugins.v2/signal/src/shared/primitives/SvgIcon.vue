<template>
  <i class="signal-svg-icon" :style="iconStyle" aria-hidden="true">
    <svg
      class="signal-svg-icon__svg"
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 24 24"
      :width="normalizedSize"
      :height="normalizedSize"
      focusable="false"
      role="img"
    >
      <path :d="icon" fill="currentColor" />
    </svg>
  </i>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  icon: { type: String, required: true },
  size: { type: [Number, String], default: 14 },
  color: { type: String, default: '' },
})

const normalizedSize = computed(() => {
  const rawSize = String(props.size).trim()
  return /^\d+(\.\d+)?$/.test(rawSize) ? `${rawSize}px` : rawSize
})

const iconStyle = computed(() => ({
  '--signal-icon-size': normalizedSize.value,
  inlineSize: normalizedSize.value,
  blockSize: normalizedSize.value,
  color: props.color || undefined,
}))
</script>
