<template>
  <article class="signal-glass-card-light signal-task-tile">
    <div class="signal-task-tile__top">
      <span class="signal-task-tile__name">{{ task.name }}</span>
      <StatusChip :label="task.state || '运行中'" :tone="task.state === '失败' ? 'danger' : 'plain-green'" />
    </div>
    <span class="signal-task-tile__schedule">{{ task.schedule }}</span>
  </article>
</template>

<script setup>
import StatusChip from '../../../shared/primitives/StatusChip.vue'

defineProps({
  task: { type: Object, required: true },
})
</script>
