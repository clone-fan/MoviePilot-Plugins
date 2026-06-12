<script setup>
import { computed, reactive, watch } from 'vue'

const props = defineProps({ initialConfig: { type: Object, default: () => ({}) } })
const emit = defineEmits(['save', 'close'])

const form = reactive({})
const activeMain = reactive({ value: 'report' })
const activeSub = reactive({
  report: 'basic',
  notices: 'subscribe',
  backup: 'local',
  cleanup: 'logs',
  updates: 'mp',
  plugin: 'target',
})

const defaults = {
  enabled: false,
  daily_report_enabled: true,
  daily_report_cron: '0 22 * * *',
  health_in_report: true,
  subscribe_in_report: true,
  site_stat_in_report: true,
  subscribe_reminder_enabled: true,
  subscribe_reminder_onlyonce: false,
  subscribe_reminder_time: '9',
  subscribe_reminder_subtype: ['movie', 'tv'],
  subscribe_reminder_msgtype: 'Subscribe',
  site_stat_enabled: true,
  site_stat_onlyonce: false,
  site_stat_dashboard_type: 'today',
  site_stat_notify_type: 'inc',
  log_clean_enabled: false,
  log_clean_cron: '0 3 * * 1',
  log_clean_rows: 300,
  log_clean_selected_ids: '',
  log_clean_notify: true,
  log_clean_onlyonce: false,
  backup_enabled: false,
  backup_onlyonce: false,
  backup_cron: '0 4 * * 1',
  backup_keep_count: 5,
  backup_path: '/config/plugins/AgentOpsAssistant/Backup',
  backup_notify: true,
  backup_webdav_enabled: false,
  backup_webdav_notify: false,
  backup_webdav_digest_auth: false,
  backup_webdav_disable_check: false,
  backup_webdav_hostname: '',
  backup_webdav_login: '',
  backup_webdav_password: '',
  backup_webdav_max_count: 5,
  mp_update_enabled: false,
  mp_update_cron: '0 9 * * *',
  mp_update_notify: true,
  mp_update_restart_confirm: false,
  mp_update_types: ['后端', '前端'],
  market_update_enabled: false,
  market_update_onlyonce: false,
  market_update_interval: 86400,
  market_update_notify: true,
  market_update_write_notify: false,
  market_update_notify_type: 'Plugin',
  market_update_write_settings: false,
  market_update_write_env: false,
  market_update_blacklist_enabled: false,
  market_update_blacklist: '',
  market_update_auto_get: false,
  market_update_proxy: true,
  market_update_timeout: 5,
  market_update_wiki_url: 'https://wiki.movie-pilot.org/zh/plugin',
  market_update_wiki_xpath: '//pre[@class="prismjs line-numbers" and @v-pre="true"]/code/text()',
  plugin_uninstall_id: '',
  plugin_uninstall_ids: [],
  plugin_uninstall_clear_config: true,
  plugin_uninstall_clear_data: true,
  plugin_uninstall_delete_source: false,
  plugin_uninstall_notify: true,
}

const mainTabs = [
  { key: 'report', title: '每日汇报', icon: 'mdi-newspaper-variant-outline', color: 'primary', desc: '设置每日汇报是否发送、发送时间和栏目内容。' },
  { key: 'notices', title: '订阅与站点', icon: 'mdi-bell-cog-outline', color: 'cyan', desc: '设置订阅提醒和站点统计是否写入汇报或单独通知。' },
  { key: 'backup', title: '自动备份', icon: 'mdi-archive-arrow-up-outline', color: 'success', desc: '设置本地备份、保留数量和 WebDAV 远端备份。' },
  { key: 'cleanup', title: '日志清理', icon: 'mdi-file-document-remove-outline', color: 'warning', desc: '设置插件日志保留行数、清理时间和结果通知。' },
  { key: 'updates', title: '更新检查', icon: 'mdi-update', color: 'info', desc: '设置 MoviePilot 和插件库更新检查，不在这里直接升级。' },
  { key: 'plugin', title: '插件残留清理', icon: 'mdi-puzzle-remove-outline', color: 'deep-orange', desc: '检查并清理已卸载插件留下的配置、数据、日志或本地源码残留。' },
]

const subTabs = {
  report: [
    { key: 'basic', title: '基础设置', icon: 'mdi-tune-variant' },
    { key: 'columns', title: '汇报栏目', icon: 'mdi-view-list-outline' },
  ],
  notices: [
    { key: 'subscribe', title: '订阅提醒', icon: 'mdi-bell-ring-outline' },
    { key: 'sites', title: '站点统计', icon: 'mdi-chart-line' },
  ],
  backup: [
    { key: 'local', title: '本地备份', icon: 'mdi-folder-arrow-up-outline' },
    { key: 'webdav', title: 'WebDAV', icon: 'mdi-cloud-upload-outline' },
  ],
  cleanup: [
    { key: 'logs', title: '插件日志', icon: 'mdi-file-document-remove-outline' },
  ],
  updates: [
    { key: 'mp', title: '主程序', icon: 'mdi-movie-open-cog-outline' },
    { key: 'market', title: '插件库', icon: 'mdi-puzzle-plus-outline' },
  ],
  plugin: [
    { key: 'target', title: '目标插件', icon: 'mdi-crosshairs-gps' },
    { key: 'scope', title: '清理范围', icon: 'mdi-folder-remove-outline' },
  ],
}

const cronPresets = [
  { title: '每天 22:00', value: '0 22 * * *' },
  { title: '每天 09:00', value: '0 9 * * *' },
  { title: '每周一 03:00', value: '0 3 * * 1' },
  { title: '每周一 04:00', value: '0 4 * * 1' },
]
const subscribeSubtypeItems = [{ title: '电影', value: 'movie' }, { title: '电视剧', value: 'tv' }]
const messageTypeItems = [{ title: '订阅', value: 'Subscribe' }, { title: '插件', value: 'Plugin' }, { title: '手动处理', value: 'Manual' }]
const siteStatRangeItems = [{ title: '今日数据', value: 'today' }, { title: '汇总数据', value: 'total' }, { title: '所有数据', value: 'all' }]
const siteNotifyItems = [{ title: '增量变化', value: 'inc' }, { title: '全部数据', value: 'all' }, { title: '不通知', value: 'none' }]
const marketNotifyItems = [{ title: '插件通知', value: 'Plugin' }, { title: '手动处理', value: 'Manual' }]
const mpUpdateTypes = ['后端', '前端'].map(v => ({ title: v, value: v }))
const keepCountPresets = [3, 5, 7, 10, 15].map(v => ({ title: `保留 ${v} 份`, value: v }))
const logRowsPresets = [100, 300, 500, 1000, 2000].map(v => ({ title: `保留 ${v} 行`, value: v }))
const intervalPresets = [3600, 21600, 43200, 86400, 604800].map(v => ({ title: v < 86400 ? `${v / 3600} 小时` : `${v / 86400} 天`, value: v }))

const currentMain = computed(() => mainTabs.find(item => item.key === activeMain.value) || mainTabs[0])

watch(() => props.initialConfig, value => {
  Object.keys(form).forEach(key => delete form[key])
  Object.assign(form, defaults, value || {})
  if (typeof form.subscribe_reminder_subtype === 'string') form.subscribe_reminder_subtype = form.subscribe_reminder_subtype.split(',').map(v => v.trim()).filter(Boolean)
  if (typeof form.mp_update_types === 'string') form.mp_update_types = form.mp_update_types.split(',').map(v => v.trim()).filter(Boolean)
  if (typeof form.plugin_uninstall_ids === 'string') form.plugin_uninstall_ids = form.plugin_uninstall_ids.split(',').map(v => v.trim()).filter(Boolean)
}, { immediate: true, deep: true })

function saveConfig() {
  emit('save', { ...form })
}

function selectMain(key) {
  activeMain.value = key
  if (!activeSub[key]) activeSub[key] = subTabs[key]?.[0]?.key || 'basic'
}
</script>

<template>
  <div class="agentops-config">
    <VToolbar density="comfortable" class="agentops-toolbar">
      <div class="text-h6 ms-3">MP 运维助手配置</div>
      <VSpacer />
      <VBtn color="primary" variant="tonal" prepend-icon="mdi-content-save" class="text-none" @click="saveConfig">保存配置</VBtn>
      <VBtn icon="mdi-close" variant="text" @click="emit('close')" />
    </VToolbar>
    <VDivider />

    <div class="pa-3">
      <VCard flat class="rounded border mpops-shell">
        <VCardText class="pb-0">
          <div class="d-flex flex-wrap ga-2">
            <VBtn v-for="tab in mainTabs" :key="tab.key" :color="activeMain.value === tab.key ? tab.color : undefined" :variant="activeMain.value === tab.key ? 'tonal' : 'text'" class="text-none" :prepend-icon="tab.icon" @click="selectMain(tab.key)">{{ tab.title }}</VBtn>
          </div>
        </VCardText>
        <VDivider class="mt-3" />

        <VCardItem>
          <template #prepend><VAvatar :color="currentMain.color" variant="tonal" size="40"><VIcon :icon="currentMain.icon" /></VAvatar></template>
          <VCardTitle>{{ currentMain.title }}</VCardTitle>
          <VCardSubtitle>{{ currentMain.desc }}</VCardSubtitle>
        </VCardItem>

        <VCardText>
          <VTabs v-model="activeSub[activeMain.value]" :color="currentMain.color" density="comfortable" show-arrows class="mpops-subtabs">
            <VTab v-for="tab in subTabs[activeMain.value]" :key="tab.key" :value="tab.key" class="text-none"><VIcon :icon="tab.icon" size="small" start />{{ tab.title }}</VTab>
          </VTabs>
          <VDivider />

          <VWindow v-model="activeSub[activeMain.value]" :touch="false">
            <template v-if="activeMain.value === 'report'">
              <VWindowItem value="basic" class="pa-3">
                <VRow>
                  <VCol cols="12" md="6"><VSwitch v-model="form.enabled" label="启用插件" color="primary" hint="关闭后不注册本插件的定时任务，也不会自动发送汇报。" persistent-hint /></VCol>
                  <VCol cols="12" md="6"><VSwitch v-model="form.daily_report_enabled" label="启用每日汇报" color="primary" hint="开启后按下方时间自动发送 MP 运维汇报。" persistent-hint /></VCol>
                  <VCol cols="12" md="6"><VSelect v-model="form.daily_report_cron" :items="cronPresets" label="每日汇报时间" variant="outlined" density="comfortable" hint="推荐选择每天 22:00；也可以手动输入 Cron。" persistent-hint /></VCol>
                  <VCol cols="12" md="6"><VSwitch v-model="form.health_in_report" label="加入健康巡查摘要" color="primary" hint="在汇报中显示下载器、站点、入库和存储等状态摘要。" persistent-hint /></VCol>
                </VRow>
              </VWindowItem>
              <VWindowItem value="columns" class="pa-3">
                <VRow>
                  <VCol cols="12" md="6"><VSwitch v-model="form.subscribe_in_report" label="显示订阅追新" color="primary" hint="开启后每日汇报会包含今日订阅更新；不需要订阅栏目时关闭。" persistent-hint /></VCol>
                  <VCol cols="12" md="6"><VSwitch v-model="form.site_stat_in_report" label="显示站点统计" color="primary" hint="开启后每日汇报会包含站点状态和增量数据。" persistent-hint /></VCol>
                </VRow>
              </VWindowItem>
            </template>

            <template v-if="activeMain.value === 'notices'">
              <VWindowItem value="subscribe" class="pa-3">
                <VRow>
                  <VCol cols="12" md="4"><VSwitch v-model="form.subscribe_reminder_enabled" label="启用订阅提醒" color="cyan" hint="开启后订阅追新数据会参与提醒和汇报。" persistent-hint /></VCol>
                  <VCol cols="12" md="4"><VSwitch v-model="form.subscribe_reminder_onlyonce" label="保存后立即运行一次" color="cyan" hint="只适合手动测试；运行后建议关闭。" persistent-hint /></VCol>
                  <VCol cols="12" md="4"><VTextField v-model="form.subscribe_reminder_time" label="提醒小时" variant="outlined" density="comfortable" hint="填写 0-23 的小时，例如 9 表示上午 9 点提醒。" persistent-hint /></VCol>
                  <VCol cols="12" md="6"><VSelect v-model="form.subscribe_reminder_subtype" :items="subscribeSubtypeItems" label="提醒媒体类型" variant="outlined" density="comfortable" multiple chips closable-chips hint="选择需要统计和提醒的订阅类型。" persistent-hint /></VCol>
                  <VCol cols="12" md="6"><VSelect v-model="form.subscribe_reminder_msgtype" :items="messageTypeItems" label="通知类型" variant="outlined" density="comfortable" hint="不确定时保持“订阅”。" persistent-hint /></VCol>
                </VRow>
              </VWindowItem>
              <VWindowItem value="sites" class="pa-3">
                <VRow>
                  <VCol cols="12" md="4"><VSwitch v-model="form.site_stat_enabled" label="启用站点统计" color="cyan" hint="开启后采集站点状态，用于汇报和通知。" persistent-hint /></VCol>
                  <VCol cols="12" md="4"><VSwitch v-model="form.site_stat_onlyonce" label="保存后立即刷新一次" color="cyan" hint="用于手动更新站点数据；运行后建议关闭。" persistent-hint /></VCol>
                  <VCol cols="12" md="4"><VSelect v-model="form.site_stat_dashboard_type" :items="siteStatRangeItems" label="统计范围" variant="outlined" density="comfortable" hint="今日数据适合日报；汇总/所有数据适合排查趋势。" persistent-hint /></VCol>
                  <VCol cols="12" md="6"><VSelect v-model="form.site_stat_notify_type" :items="siteNotifyItems" label="通知内容" variant="outlined" density="comfortable" hint="选择站点数据变化时发送哪类通知。" persistent-hint /></VCol>
                </VRow>
              </VWindowItem>
            </template>

            <template v-if="activeMain.value === 'backup'">
              <VWindowItem value="local" class="pa-3">
                <VRow>
                  <VCol cols="12" md="4"><VSwitch v-model="form.backup_enabled" label="启用自动备份" color="success" hint="开启后按备份时间自动打包配置和关键数据。" persistent-hint /></VCol>
                  <VCol cols="12" md="4"><VSwitch v-model="form.backup_onlyonce" label="保存后立即备份一次" color="success" hint="用于手动生成一次备份；运行后建议关闭。" persistent-hint /></VCol>
                  <VCol cols="12" md="4"><VSwitch v-model="form.backup_notify" label="备份后通知" color="success" hint="备份成功或失败后发送通知。" persistent-hint /></VCol>
                  <VCol cols="12" md="4"><VSelect v-model="form.backup_cron" :items="cronPresets" label="备份时间" variant="outlined" density="comfortable" hint="推荐每周低峰期执行。" persistent-hint /></VCol>
                  <VCol cols="12" md="4"><VSelect v-model="form.backup_keep_count" :items="keepCountPresets" label="本地保留数量" variant="outlined" density="comfortable" hint="超过数量后会清理最旧备份。" persistent-hint /></VCol>
                  <VCol cols="12" md="4"><VTextField v-model="form.backup_path" label="备份保存路径" variant="outlined" density="comfortable" hint="默认路径即可；如修改，请填写容器内可写目录。" persistent-hint /></VCol>
                </VRow>
              </VWindowItem>
              <VWindowItem value="webdav" class="pa-3">
                <VRow>
                  <VCol cols="12" md="4"><VSwitch v-model="form.backup_webdav_enabled" label="启用 WebDAV 备份" color="success" hint="开启后会把备份同步到 WebDAV。" persistent-hint /></VCol>
                  <VCol cols="12" md="4"><VSwitch v-model="form.backup_webdav_notify" label="WebDAV 结果通知" color="success" hint="上传成功或失败后发送通知。" persistent-hint /></VCol>
                  <VCol cols="12" md="4"><VSwitch v-model="form.backup_webdav_digest_auth" label="使用 Digest 认证" color="success" hint="服务端要求 Digest 时开启；普通账号密码认证保持关闭。" persistent-hint /></VCol>
                  <VCol cols="12" md="4"><VSwitch v-model="form.backup_webdav_disable_check" label="跳过连通检查" color="warning" hint="只有服务端检查异常但实际可上传时才开启。" persistent-hint /></VCol>
                  <VCol cols="12" md="8"><VTextField v-model="form.backup_webdav_hostname" label="WebDAV 地址" variant="outlined" density="comfortable" hint="填写完整地址，例如 https://example.com/dav。" persistent-hint /></VCol>
                  <VCol cols="12" md="4"><VTextField v-model="form.backup_webdav_login" label="WebDAV 用户名" variant="outlined" density="comfortable" /></VCol>
                  <VCol cols="12" md="4"><VTextField v-model="form.backup_webdav_password" label="WebDAV 密码" type="password" variant="outlined" density="comfortable" /></VCol>
                  <VCol cols="12" md="4"><VSelect v-model="form.backup_webdav_max_count" :items="keepCountPresets" label="远端保留数量" variant="outlined" density="comfortable" hint="超过数量后会清理远端旧备份。" persistent-hint /></VCol>
                </VRow>
              </VWindowItem>
            </template>

            <template v-if="activeMain.value === 'cleanup'">
              <VWindowItem value="logs" class="pa-3">
                <VRow>
                  <VCol cols="12" md="4"><VSwitch v-model="form.log_clean_enabled" label="启用插件日志定时清理" color="warning" hint="开启后按设定时间截断插件日志。" persistent-hint /></VCol>
                  <VCol cols="12" md="4"><VSwitch v-model="form.log_clean_onlyonce" label="保存后立即清理一次" color="warning" hint="用于手动清理；运行后建议关闭。" persistent-hint /></VCol>
                  <VCol cols="12" md="4"><VSwitch v-model="form.log_clean_notify" label="清理后通知" color="warning" hint="清理完成后发送处理结果。" persistent-hint /></VCol>
                  <VCol cols="12" md="4"><VSelect v-model="form.log_clean_cron" :items="cronPresets" label="日志清理时间" variant="outlined" density="comfortable" hint="推荐每周低峰期执行。" persistent-hint /></VCol>
                  <VCol cols="12" md="4"><VSelect v-model="form.log_clean_rows" :items="logRowsPresets" label="每个日志保留行数" variant="outlined" density="comfortable" hint="保留越少占用越低；排障频繁时可保留 1000 行。" persistent-hint /></VCol>
                  <VCol cols="12" md="4"><VTextField v-model="form.log_clean_selected_ids" label="限定插件 ID" variant="outlined" density="comfortable" hint="留空表示全部插件；多个 ID 用英文逗号分隔。" persistent-hint /></VCol>
                </VRow>
              </VWindowItem>
            </template>

            <template v-if="activeMain.value === 'updates'">
              <VWindowItem value="mp" class="pa-3">
                <VRow>
                  <VCol cols="12" md="4"><VSwitch v-model="form.mp_update_enabled" label="启用主程序更新检查" color="info" hint="只检查并通知，不会自动升级。" persistent-hint /></VCol>
                  <VCol cols="12" md="4"><VSelect v-model="form.mp_update_cron" :items="cronPresets" label="检查时间" variant="outlined" density="comfortable" hint="推荐每天 09:00。" persistent-hint /></VCol>
                  <VCol cols="12" md="4"><VSwitch v-model="form.mp_update_notify" label="检查后通知" color="info" hint="有无更新都会按插件逻辑发送结果。" persistent-hint /></VCol>
                  <VCol cols="12" md="6"><VSelect v-model="form.mp_update_types" :items="mpUpdateTypes" label="检查对象" variant="outlined" density="comfortable" multiple chips closable-chips hint="一般同时选择后端和前端。" persistent-hint /></VCol>
                  <VCol cols="12" md="6"><VSwitch v-model="form.mp_update_restart_confirm" label="允许更新后重启" color="error" hint="开启后更新流程可在需要时重启 MoviePilot；不想自动重启就关闭。" persistent-hint /></VCol>
                </VRow>
              </VWindowItem>
              <VWindowItem value="market" class="pa-3">
                <VRow>
                  <VCol cols="12" md="4"><VSwitch v-model="form.market_update_enabled" label="启用插件库更新检查" color="info" hint="定期检查插件库地址是否变化。" persistent-hint /></VCol>
                  <VCol cols="12" md="4"><VSwitch v-model="form.market_update_onlyonce" label="保存后立即检查一次" color="info" hint="用于手动测试；运行后建议关闭。" persistent-hint /></VCol>
                  <VCol cols="12" md="4"><VSelect v-model="form.market_update_interval" :items="intervalPresets" label="检查间隔" variant="outlined" density="comfortable" hint="推荐 1 天。" persistent-hint /></VCol>
                  <VCol cols="12" md="4"><VSwitch v-model="form.market_update_notify" label="变化时通知" color="info" hint="发现插件库地址变化时发送通知。" persistent-hint /></VCol>
                  <VCol cols="12" md="4"><VSwitch v-model="form.market_update_write_notify" label="写入后通知" color="info" hint="启用写入时，写入完成后发送通知。" persistent-hint /></VCol>
                  <VCol cols="12" md="4"><VSelect v-model="form.market_update_notify_type" :items="marketNotifyItems" label="通知类型" variant="outlined" density="comfortable" hint="不确定时保持插件通知。" persistent-hint /></VCol>
                  <VCol cols="12" md="4"><VSwitch v-model="form.market_update_write_settings" label="允许写入当前配置" color="error" hint="开启后允许把检测到的插件库地址写入当前配置；不确定就关闭。" persistent-hint /></VCol>
                  <VCol cols="12" md="4"><VSwitch v-model="form.market_update_write_env" label="允许写入 app.env" color="error" hint="开启后允许写入 app.env；通常保持关闭。" persistent-hint /></VCol>
                  <VCol cols="12" md="4"><VSwitch v-model="form.market_update_blacklist_enabled" label="启用写入黑名单" color="info" hint="开启后，黑名单中的插件库地址不会被写入。" persistent-hint /></VCol>
                  <VCol cols="12" md="4"><VSwitch v-model="form.market_update_auto_get" label="自动获取插件库地址" color="info" hint="从 Wiki 页面自动解析插件库地址。" persistent-hint /></VCol>
                  <VCol cols="12" md="4"><VSwitch v-model="form.market_update_proxy" label="使用代理访问 Wiki" color="info" hint="访问 Wiki 慢或失败时开启。" persistent-hint /></VCol>
                  <VCol cols="12" md="4"><VTextField v-model="form.market_update_timeout" type="number" label="请求超时（秒）" variant="outlined" density="comfortable" hint="网络慢时可调大，例如 10。" persistent-hint /></VCol>
                  <VCol cols="12" md="6"><VTextField v-model="form.market_update_wiki_url" label="插件库 Wiki 地址" variant="outlined" density="comfortable" hint="用于自动获取插件库地址，通常保持默认。" persistent-hint /></VCol>
                  <VCol cols="12" md="6"><VTextField v-model="form.market_update_wiki_xpath" label="Wiki XPath" variant="outlined" density="comfortable" hint="用于定位页面中的插件库地址，不懂 XPath 就保持默认。" persistent-hint /></VCol>
                  <VCol cols="12"><VTextField v-model="form.market_update_blacklist" label="插件库黑名单" variant="outlined" density="comfortable" hint="多个插件 ID 用英文逗号分隔。" persistent-hint /></VCol>
                </VRow>
              </VWindowItem>
            </template>

            <template v-if="activeMain.value === 'plugin'">
              <VWindowItem value="target" class="pa-3">
                <VRow>
                  <VCol cols="12" md="6"><VTextField v-model="form.plugin_uninstall_id" label="目标插件 ID" variant="outlined" density="comfortable" hint="填写要检查残留的插件 ID；不要填写 AgentOpsAssistant。" persistent-hint /></VCol>
                  <VCol cols="12" md="6"><VCombobox v-model="form.plugin_uninstall_ids" label="批量目标插件 ID" variant="outlined" density="comfortable" multiple chips closable-chips hint="多个插件一起检查时填写；为空时使用左侧单个 ID。" persistent-hint /></VCol>
                </VRow>
              </VWindowItem>
              <VWindowItem value="scope" class="pa-3">
                <VRow>
                  <VCol cols="12" md="6"><VSwitch v-model="form.plugin_uninstall_clear_config" label="清理插件配置" color="deep-orange" hint="清理目标插件保存的配置项。" persistent-hint /></VCol>
                  <VCol cols="12" md="6"><VSwitch v-model="form.plugin_uninstall_clear_data" label="清理插件数据" color="deep-orange" hint="删除目标插件保存的运行数据；不确定时先关闭。" persistent-hint /></VCol>
                  <VCol cols="12" md="6"><VSwitch v-model="form.plugin_uninstall_delete_source" label="清理本地源码残留" color="deep-orange" hint="删除本地插件仓库中同名源码目录；只在确认源码不再需要时开启。" persistent-hint /></VCol>
                  <VCol cols="12" md="6"><VSwitch v-model="form.plugin_uninstall_notify" label="清理后通知" color="deep-orange" hint="处理完成后发送结果通知。" persistent-hint /></VCol>
                </VRow>
              </VWindowItem>
            </template>

          </VWindow>
        </VCardText>
      </VCard>
    </div>
  </div>
</template>

<style scoped>
.agentops-toolbar { position: sticky; top: 0; z-index: 10; background: rgb(var(--v-theme-surface)); }
.mpops-shell { background: rgba(var(--v-theme-surface), .92); }
.mpops-subtabs { border-radius: 12px 12px 0 0; }
.agentops-config :deep(.v-field) { border-radius: 12px; }
.agentops-config :deep(.v-alert) { border-radius: 12px; }
</style>
