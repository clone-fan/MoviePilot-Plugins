<template>
  <div class="signal-fusion-takeover-note" role="status">
    <span class="signal-fusion-takeover-note__state">融合通知已接管</span>
    <span class="signal-fusion-takeover-note__item signal-fusion-takeover-note__item--source">
      当前融合卡使用：{{ configLabel }}
    </span>
    <span class="signal-fusion-takeover-note__item">卡片：{{ cardLabel }}</span>
    <span class="signal-fusion-takeover-note__item">最后更新：{{ updateLabel }}</span>
    <span class="signal-fusion-takeover-note__item">最近错误：{{ errorLabel }}</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: { type: Object, default: () => ({}) },
  loading: { type: Boolean, default: false },
})

const messageId = computed(() => Number(props.status?.message_id || 0))
const cardLabel = computed(() => (messageId.value > 0 ? `#${messageId.value}` : '未创建'))
const updateLabel = computed(() => props.status?.date || props.status?.updated_at || props.status?.last_updated || '--')
const errorLabel = computed(() => props.status?.last_error || '无')
const configLabel = computed(() => {
  if (props.loading) return '读取中'
  return props.status?.config_hint || props.status?.config_source || '未找到可用 Telegram 通知渠道'
})
</script>
