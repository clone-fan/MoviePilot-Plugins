<template>
  <article class="signal-glass-card signal-fusion-mini">
    <span class="signal-fusion-mini__updated">{{ enabled ? `更新于 ${updatedAt || '--'}` : '插件已停用' }}</span>
    <IconCircle :icon="signalIcons.cardAccount" tone="blue" class="signal-fusion-mini__icon" />
    <div class="signal-fusion-mini__identity">
      <strong class="signal-fusion-mini__name">融合卡 <template v-if="enabled && cardId">#{{ cardId }}</template><template v-else-if="enabled">未建卡</template></strong>
      <div class="signal-fusion-mini__status">
        <span>状态</span>
        <StatusChip :label="enabled ? (isBuilt ? '已建立' : '未建立') : '已停用'" :tone="enabled && isBuilt ? 'green' : ''" :icon="enabled && isBuilt ? signalIcons.checkCircle : ''" />
      </div>
    </div>
    <div class="signal-fusion-mini__buttons">
      <button type="button" class="signal-pill-button signal-pill-button--compact" :class="{ 'signal-status-chip--green': enabled }" :disabled="!enabled || building || refreshing" :aria-busy="building ? 'true' : 'false'" title="创建或更新融合卡" @click="$emit('build')">
        <SvgIcon :icon="signalIcons.cardPlus" size="11" />
        建卡
      </button>
      <button type="button" class="signal-pill-button signal-pill-button--compact" :disabled="!enabled || building || refreshing" :aria-busy="refreshing ? 'true' : 'false'" :title="refreshing ? '融合卡刷新中' : '立即刷新融合卡'" data-fusion-refresh-button @click="$emit('refresh')">
        <SvgIcon :icon="signalIcons.refresh" size="11" />
        {{ refreshing ? '刷新中' : '刷新' }}
      </button>
    </div>
  </article>
</template>

<script setup>
import IconCircle from '../../../shared/primitives/IconCircle.vue'
import StatusChip from '../../../shared/primitives/StatusChip.vue'
import SvgIcon from '../../../shared/primitives/SvgIcon.vue'
import { signalIcons } from '../../../shared/icons.js'

defineProps({
  cardId: { type: [String, Number], default: '' },
  updatedAt: { type: String, default: '' },
  isBuilt: { type: Boolean, default: false },
  enabled: { type: Boolean, default: true },
  refreshing: { type: Boolean, default: false },
  building: { type: Boolean, default: false },
})

defineEmits(['build', 'refresh'])
</script>
