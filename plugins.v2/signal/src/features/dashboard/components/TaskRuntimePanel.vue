<template>
  <GlassCard class-name="signal-task-panel">
    <div class="signal-card-header">
      <div class="signal-card-heading">
        <SvgIcon :icon="signalIcons.calendarCheck" color="#60A5FA" size="18" />
        <span>任务运行</span>
        <small>当前实时任务</small>
      </div>
      <StatusChip label="异常优先" />
    </div>
    <div v-if="tasks.length" class="signal-task-grid">
      <TaskTile v-for="task in tasks" :key="task.key || task.name" :task="task" />
    </div>
    <div v-else class="signal-task-empty">当前没有正在运行的任务</div>
  </GlassCard>
</template>

<script setup>
import GlassCard from '../../../shared/primitives/GlassCard.vue'
import StatusChip from '../../../shared/primitives/StatusChip.vue'
import SvgIcon from '../../../shared/primitives/SvgIcon.vue'
import TaskTile from './TaskTile.vue'
import { signalIcons } from '../../../shared/icons.js'

defineProps({
  tasks: { type: Array, default: () => [] },
})
</script>
