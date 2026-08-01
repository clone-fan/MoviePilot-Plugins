<template>
  <div class="signal-pane">
    <VForm>
      <ModuleHero
        v-model:enabled="form.subscribe_reminder_enabled"
        icon="mdi-bell-ring-outline"
        kicker="MP 订阅管理"
        on-title="订阅追新已启用"
        off-title="订阅追新未启用"
        desc="组件开关控制手动追新|定时推送由下方独立开关控制"
        :count-label="`${form.subscribe_reminder_subtype?.length || 0} 类提醒`"
      />
      <SettingSection title="追新设置" note="订阅类型集中配置">
        <VRow class="signal-setting-grid">
          <VCol cols="12" md="3">
            <VSelect v-model="form.subscribe_reminder_subtype" :items="subscribeSubtypeItems"
              label="提醒类型" multiple chips closable-chips :disabled="!form.subscribe_reminder_enabled" />
          </VCol>
        </VRow>
      </SettingSection>
    </VForm>
  </div>
</template>

<script setup>
import ModuleHero from './ModuleHero'
import SettingSection from './SettingSection'

defineProps({
  form: { type: Object, required: true },
  subscribeSubtypeItems: { type: Array, default: () => [] },
})
</script>
