// 配置页导航 tabs — 纯数据，无运行时依赖
export const mainTabs = [
  { key: 'notify', title: '通知设置', icon: 'mdi-message-badge-outline', desc: '融合通知、媒体通知与订阅追新' },
  { key: 'monitor', title: '数据与监控', icon: 'mdi-chart-line', desc: '站点统计与健康巡查' },
  { key: 'download', title: '下载器管理', icon: 'mdi-download-network-outline', desc: '自动删种、下载器助手与订阅规则填充' },
  { key: 'maintenance', title: '系统维护', icon: 'mdi-cog-outline', desc: '自动备份、日志清理与更新检查' },
  { key: 'plugin', title: '插件卸载', icon: 'mdi-puzzle-remove-outline', desc: '安全卸载插件并清理残留' },
]

export const subTabs = {
  notify: [
    { key: 'fusion', title: '融合通知', icon: 'mdi-message-badge-outline' },
    { key: 'server', title: '媒体通知', icon: 'mdi-television-play' },
    { key: 'subscribe', title: '订阅追新', icon: 'mdi-bell-ring-outline' },
  ],
  monitor: [
    { key: 'sites', title: '站点统计', icon: 'mdi-chart-line' },
    { key: 'hc', title: '健康巡查', icon: 'mdi-heart-pulse' },
  ],
  download: [
    { key: 'seedremove', title: '自动删种', icon: 'mdi-delete-sweep-outline' },
    { key: 'dltagmain', title: '下载器助手', icon: 'mdi-download-network-outline' },
    { key: 'subfill', title: '订阅规则填充', icon: 'mdi-auto-fix' },
  ],
  maintenance: [
    { key: 'backup', title: '自动备份', icon: 'mdi-archive-arrow-up-outline' },
    { key: 'logs', title: '日志清理', icon: 'mdi-file-document-remove-outline' },
    { key: 'updates', title: '更新检查', icon: 'mdi-update' },
  ],
  plugin: [
    { key: 'clean', title: '安全卸载', icon: 'mdi-puzzle-remove-outline' },
  ],
}
