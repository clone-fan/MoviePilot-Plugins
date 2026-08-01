<template>
  <div class="signal-pane">
    <VForm>
      <ModuleHero
        v-model:enabled="form.site_stat_enabled"
        icon="mdi-chart-line"
        kicker="MP 站点统计"
        on-title="站点数据采集已启用"
        off-title="站点数据采集未启用"
        desc="为仪表盘和日报提供站点状态|统计上传下载增量与趋势"
        :count-label="form.site_stat_dashboard_type === 'today' ? '今日数据' : '统计数据'"
      />
      <SettingSection title="统计设置" note="控制仪表盘站点数据口径">
        <VRow class="signal-setting-grid">
          <VCol cols="12" md="12">
            <VSelect v-model="form.site_stat_dashboard_type" :items="siteStatRangeItems"
              label="统计数据范围" :disabled="!form.site_stat_enabled" />
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
  siteStatRangeItems: { type: Array, default: () => [] },
})
</script>
