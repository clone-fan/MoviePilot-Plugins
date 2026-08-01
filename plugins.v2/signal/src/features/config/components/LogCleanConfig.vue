<script setup>
import { computed } from 'vue'
import ModuleHero from './ModuleHero'
import CronCard from './cards/CronCard.vue'
import NotifyCard from './cards/NotifyCard.vue'
import GenericConfigCard from './cards/GenericConfigCard.vue'
import FeatureConfigCard from './cards/FeatureConfigCard.vue'

const props = defineProps({
  form: { type: Object, required: true },
  logRowsPresets: { type: Array, default: () => [] },
  notificationTypeItems: { type: Array, default: () => [] },
  notificationLockedByFusion: { type: Boolean, default: false },
  installedPlugins: { type: Array, default: () => [] },
  installedLoading: { type: Boolean, default: false },
})

const featureFields = computed(() => [
  {
    key: 'log_clean_enabled',
    label: '启用日志清理',
    control: 'switch',
    hint: '关闭后手动和定时日志清理都会停止。',
  },
])

const cronFields = computed(() => [
  {
    key: 'log_clean_schedule_enabled',
    label: '启用定时清理',
    control: 'switch',
    disabled: !props.form.log_clean_enabled,
  },
  {
    key: 'log_clean_cron',
    label: '清理周期 (Cron)',
    control: 'cron',
    disabled: !props.form.log_clean_enabled || !props.form.log_clean_schedule_enabled,
  },
])

const genericFields = computed(() => [
  {
    key: 'log_clean_rows',
    label: '保留行数',
    control: 'select',
    items: props.logRowsPresets,
    disabled: !props.form.log_clean_enabled,
  },
  {
    key: 'log_clean_selected_ids',
    label: '目标插件',
    control: 'select',
    items: props.installedPlugins,
    loading: props.installedLoading,
    multiple: true,
    chips: true,
    closableChips: true,
    icon: 'mdi-puzzle-outline',
    hint: '为空时处理全部插件日志。',
    disabled: !props.form.log_clean_enabled,
  },
])

const notifyFields = computed(() => [
  {
    key: 'log_clean_notify',
    label: '清理通知',
    control: 'switch',
    disabled: !props.form.log_clean_enabled || props.notificationLockedByFusion,
  },
  {
    key: 'log_clean_notify_type',
    label: '消息类型',
    control: 'select',
    items: props.notificationTypeItems,
    disabled: !props.form.log_clean_enabled || !props.form.log_clean_notify || props.notificationLockedByFusion,
  },
])
</script>

<template>
  <div class="signal-pane">
    <VForm class="signal-standard-card-demo">
      <ModuleHero
        v-model:enabled="form.log_clean_enabled"
        icon="mdi-file-document-remove-outline"
        kicker="MP 日志清理"
        on-title="日志清理已启用"
        off-title="日志清理未启用"
        desc="定期压缩插件运行日志|保留关键记录并控制日志体积"
        :count-label="`保留 ${form.log_clean_rows} 行`"
      />
      <FeatureConfigCard
        title="组件状态"
        note="控制日志清理组件是否允许运行，是所有清理动作的总开关。"
        icon="mdi-file-document-remove-outline"
        :values="form"
        :fields="featureFields"
      />
      <CronCard
        title="定时策略"
        note="所有周期、一次性启动动作统一使用 CronCard 交互。"
        :values="form"
        :fields="cronFields"
      />
      <GenericConfigCard
        title="基础参数"
        note="通用数值和多选项通过 GenericConfigCard 渲染。"
        icon="mdi-format-list-bulleted"
        :values="form"
        :fields="genericFields"
      />
      <NotifyCard
        title="通知设置"
        note="日志清理完成后的消息渠道与融合通知锁定状态保持一致。"
        :values="form"
        :fields="notifyFields"
        :locked="notificationLockedByFusion"
      />
    </VForm>
  </div>
</template>
