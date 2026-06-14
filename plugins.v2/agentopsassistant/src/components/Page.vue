<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { getPluginApi, postPluginApi } from './api'

const props = defineProps({ api: { type: [Object, Function], default: null } })
const emit = defineEmits(['close', 'switch'])

const loading = ref(true)
const error = ref('')
const actionRunning = ref('')
const actionMessage = ref('')
const data = reactive({
  enabled: false,
  summary: '',
  tasks: [],
  task_total: 0,
  task_on: 0,
  task_failed: 0,
  health: { time: '', success: null, output: '' },
})

const overallColor = computed(() => {
  if (!data.enabled) return 'default'
  if (data.task_failed > 0) return 'error'
  return 'success'
})
const overallText = computed(() => {
  if (!data.enabled) return '未启用'
  if (data.task_failed > 0) return `${data.task_failed} 项异常`
  return '运行正常'
})
const healthColor = computed(() => {
  if (data.health.success === true) return 'success'
  if (data.health.success === false) return 'error'
  return 'grey'
})
const healthText = computed(() => {
  if (data.health.success === true) return '通过'
  if (data.health.success === false) return '存在异常'
  return '尚未巡查'
})

async function loadDashboard() {
  loading.value = true
  error.value = ''
  try {
    const res = await getPluginApi(props.api, 'dashboard')
    Object.assign(data, res || {})
  } catch (err) {
    error.value = err?.message || '仪表盘数据加载失败'
  } finally {
    loading.value = false
  }
}

async function runAction(path, label) {
  if (actionRunning.value) return
  actionRunning.value = path
  actionMessage.value = ''
  try {
    const res = await postPluginApi(props.api, path)
    const ok = !res || res.code === 0 || res.code === undefined
    actionMessage.value = (res && res.msg) || `${label}已${ok ? '完成' : '失败'}`
    setTimeout(() => { actionMessage.value = '' }, 5000)
    if (ok) loadDashboard()
  } catch (err) {
    actionMessage.value = err?.message || `${label}失败`
    setTimeout(() => { actionMessage.value = '' }, 5000)
  } finally {
    actionRunning.value = ''
  }
}

onMounted(loadDashboard)
</script>

<template>
  <div class="agentops-dashboard">
    <VToolbar density="comfortable" class="agentops-toolbar">
      <VIcon icon="mdi-view-dashboard-outline" class="ms-3 me-2" color="primary" />
      <div class="text-h6">MP 运维助手 · 仪表盘</div>
      <VSpacer />
      <VBtn color="primary" variant="tonal" prepend-icon="mdi-refresh" class="text-none me-2" :loading="loading" @click="loadDashboard">刷新</VBtn>
      <VBtn variant="text" prepend-icon="mdi-cog-outline" class="text-none" @click="emit('switch')">设置</VBtn>
      <VBtn icon="mdi-close" variant="text" @click="emit('close')" />
    </VToolbar>
    <VDivider />

    <div class="pa-3">
      <VAlert v-if="error" type="error" variant="tonal" class="mb-3" :text="error" />

      <!-- 状态总览 -->
      <VRow class="mb-1">
        <VCol cols="12" sm="4">
          <VCard variant="tonal" :color="overallColor" class="rounded-lg">
            <VCardText class="d-flex align-center">
              <VAvatar :color="overallColor" variant="flat" size="44" class="me-3">
                <VIcon icon="mdi-shield-check-outline" color="white" />
              </VAvatar>
              <div>
                <div class="text-caption text-medium-emphasis">插件状态</div>
                <div class="text-h6 font-weight-bold">{{ overallText }}</div>
              </div>
            </VCardText>
          </VCard>
        </VCol>
        <VCol cols="12" sm="4">
          <VCard variant="tonal" color="primary" class="rounded-lg">
            <VCardText class="d-flex align-center">
              <VAvatar color="primary" variant="flat" size="44" class="me-3">
                <VIcon icon="mdi-format-list-checks" color="white" />
              </VAvatar>
              <div>
                <div class="text-caption text-medium-emphasis">已启用任务</div>
                <div class="text-h6 font-weight-bold">{{ data.task_on }} / {{ data.task_total }}</div>
              </div>
            </VCardText>
          </VCard>
        </VCol>
        <VCol cols="12" sm="4">
          <VCard variant="tonal" :color="data.task_failed > 0 ? 'error' : 'success'" class="rounded-lg">
            <VCardText class="d-flex align-center">
              <VAvatar :color="data.task_failed > 0 ? 'error' : 'success'" variant="flat" size="44" class="me-3">
                <VIcon :icon="data.task_failed > 0 ? 'mdi-alert-circle-outline' : 'mdi-check-circle-outline'" color="white" />
              </VAvatar>
              <div>
                <div class="text-caption text-medium-emphasis">最近执行异常</div>
                <div class="text-h6 font-weight-bold">{{ data.task_failed }}</div>
              </div>
            </VCardText>
          </VCard>
        </VCol>
      </VRow>

      <!-- 模块任务列表 -->
      <VCard variant="outlined" class="rounded-lg mb-3">
        <VCardTitle class="text-subtitle-1 d-flex align-center py-3">
          <VIcon icon="mdi-timeline-clock-outline" color="primary" class="me-2" />模块运行概览
        </VCardTitle>
        <VDivider />
        <VSkeletonLoader v-if="loading" type="list-item-avatar-three-line@3" />
        <VList v-else class="bg-transparent py-0">
          <template v-for="(task, i) in data.tasks" :key="task.key">
            <VListItem class="py-2">
              <template #prepend>
                <VAvatar size="40" variant="tonal" :color="task.enabled ? task.color : 'default'">
                  <VIcon :icon="task.icon" />
                </VAvatar>
              </template>
              <VListItemTitle class="font-weight-medium">{{ task.name }}</VListItemTitle>
              <VListItemSubtitle class="mt-1">
                最近 {{ task.last_time || '—' }}｜下次 {{ task.next }}｜{{ task.last_summary }}
              </VListItemSubtitle>
              <template #append>
                <div class="d-flex align-center ga-2">
                  <VChip size="x-small" variant="tonal" :color="task.enabled ? 'success' : 'default'">{{ task.enabled ? 'ON' : 'OFF' }}</VChip>
                  <VChip size="x-small" variant="tonal" :color="task.color">{{ task.state }}</VChip>
                </div>
              </template>
            </VListItem>
            <VDivider v-if="i < data.tasks.length - 1" />
          </template>
        </VList>
      </VCard>

      <!-- 健康巡查 -->
      <VCard variant="outlined" class="rounded-lg mb-3">
        <VCardTitle class="text-subtitle-1 d-flex align-center py-3">
          <VIcon icon="mdi-heart-pulse" color="primary" class="me-2" />最近健康巡查
          <VSpacer />
          <VChip size="small" variant="tonal" :color="healthColor">{{ healthText }}</VChip>
        </VCardTitle>
        <VDivider />
        <VCardText>
          <div v-if="data.health.time" class="text-caption text-medium-emphasis mb-2">巡查时间：{{ data.health.time }}</div>
          <pre v-if="data.health.output" class="health-output">{{ data.health.output }}</pre>
          <div v-else class="text-medium-emphasis text-body-2">尚无健康巡查记录，可在设置页手动触发或等待每日汇报自动执行。</div>
        </VCardText>
      </VCard>

      <!-- 手动触发操作 -->
      <VCard variant="outlined" class="rounded-lg">
        <VCardTitle class="text-subtitle-1 d-flex align-center py-3">
          <VIcon icon="mdi-play-circle-outline" color="primary" class="me-2" />手动触发
        </VCardTitle>
        <VDivider />
        <VCardText>
          <div class="d-flex flex-wrap ga-2">
            <VBtn
              color="primary"
              variant="tonal"
              prepend-icon="mdi-send-outline"
              size="small"
              :loading="actionRunning === 'run_daily_report'"
              @click="runAction('run_daily_report', '每日汇报')"
            >
              发送每日汇报
            </VBtn>
            <VBtn
              color="primary"
              variant="tonal"
              prepend-icon="mdi-heart-pulse"
              size="small"
              :loading="actionRunning === 'run_health_check'"
              @click="runAction('run_health_check', '健康巡查')"
            >
              健康巡查
            </VBtn>
            <VBtn
              color="primary"
              variant="tonal"
              prepend-icon="mdi-archive-arrow-up-outline"
              size="small"
              :loading="actionRunning === 'run_backup'"
              @click="runAction('run_backup', '立即备份')"
            >
              立即备份
            </VBtn>
            <VBtn
              color="primary"
              variant="tonal"
              prepend-icon="mdi-broom"
              size="small"
              :loading="actionRunning === 'run_log_clean'"
              @click="runAction('run_log_clean', '日志清理')"
            >
              清理日志
            </VBtn>
          </div>
          <VAlert v-if="actionMessage" type="info" variant="tonal" density="compact" class="mt-3" :text="actionMessage" />
        </VCardText>
      </VCard>
    </div>
  </div>
</template>

<style scoped>
.agentops-toolbar { position: sticky; top: 0; z-index: 10; background: rgb(var(--v-theme-surface)); }
.agentops-dashboard :deep(.v-card) { border-radius: 12px; }
.health-output {
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 12px;
  line-height: 1.6;
  margin: 0;
  font-family: 'JetBrains Mono', Consolas, Menlo, monospace;
  color: rgb(var(--v-theme-on-surface));
  opacity: .85;
}
</style>
