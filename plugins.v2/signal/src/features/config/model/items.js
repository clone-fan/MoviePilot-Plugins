// 配置页选项列表 — 纯数据，无运行时依赖

export const subscribeSubtypeItems = [{ title: '电影', value: 'movie' }, { title: '电视剧', value: 'tv' }]

export const notificationTypeItems = [
  { title: '插件', value: 'Plugin' },
  { title: '其他', value: 'Other' },
  { title: '手动处理', value: 'Manual' },
  { title: '订阅', value: 'Subscribe' },
  { title: '资源下载', value: 'Download' },
  { title: '整理入库', value: 'Organize' },
  { title: '站点', value: 'SiteMessage' },
  { title: '媒体服务器', value: 'MediaServer' },
  { title: '智能体', value: 'Agent' },
]

export const messageTypeItems = [
  { title: '订阅', value: 'Subscribe' },
  { title: '插件', value: 'Plugin' },
  { title: '其他', value: 'Other' },
  { title: '手动处理', value: 'Manual' },
  { title: '资源下载', value: 'Download' },
  { title: '整理入库', value: 'Organize' },
  { title: '站点', value: 'SiteMessage' },
  { title: '媒体服务器', value: 'MediaServer' },
  { title: '智能体', value: 'Agent' },
]

export const siteStatRangeItems = [{ title: '今日数据', value: 'today' }, { title: '汇总数据', value: 'total' }, { title: '所有数据', value: 'all' }]
export const marketNotifyItems = notificationTypeItems
export const mpUpdateTypes = ['后端', '前端'].map(v => ({ title: v, value: v }))
export const marketUpdateStrategies = [
  { title: '仅检查', value: 'check' },
  { title: '同步插件库', value: 'sync' },
  { title: '同步并更新插件', value: 'install' },
]
export const keepCountPresets = [3, 5, 7, 10, 15].map(v => ({ title: `保留 ${v} 份`, value: v }))
export const logRowsPresets = [100, 300, 500, 1000, 2000].map(v => ({ title: `保留 ${v} 行`, value: v }))
export const intervalPresets = [3600, 21600, 43200, 86400, 604800].map(v => ({ title: v < 86400 ? `${v / 3600} 小时` : `${v / 86400} 天`, value: v }))
export const seedActionsItems = [{ title: '暂停', value: 'pause' }, { title: '删除种子', value: 'delete' }, { title: '删除种子和文件', value: 'deletefile' }]
export const dltagTaskItems = [
  { title: '自动标签', value: 'tagging' },
  { title: '恢复做种', value: 'seeding' },
  { title: '清理失效任务', value: 'cleanup' },
]
export const dltagDeleteStrategyItems = [
  { title: '确认文件已删除后清理', value: 'delayed' },
  { title: '收到事件后立即清理', value: 'early' },
]
export const subfillDetailItems = ['分辨率', '资源质量', '特效', '制作组', '站点'].map(v => ({ title: v, value: v }))
export const msgGroupItems = ['新入库', '开始播放', '停止播放', '登录成功', '登录失败', '标记'].map(v => ({ title: v, value: v }))

export const healthCheckItems = [
  { title: '数据库', value: '数据库', icon: 'mdi-database-check-outline', desc: '连接与基础读写状态' },
  { title: '存储空间', value: '存储空间', icon: 'mdi-harddisk', desc: '下载与媒体库容量余量' },
  { title: '目录权限', value: '目录权限', icon: 'mdi-folder-key-outline', desc: '关键路径可访问性' },
]

export const healthDatabaseTargets = [
  { title: '当前主库', value: 'current' },
  { title: 'SQLite 配置库', value: 'sqlite' },
  { title: 'PostgreSQL 主库', value: 'postgresql' },
]

export const healthStorageTargets = [
  { title: 'MoviePilot 存储配置', value: 'storages' },
  { title: '配置目录', value: 'config' },
  { title: '下载目录', value: 'download' },
  { title: '媒体库目录', value: 'library' },
]

export const healthDirectoryTargets = [
  { title: '配置目录', value: 'config' },
  { title: '插件目录', value: 'plugin' },
  { title: '下载目录', value: 'download' },
  { title: '媒体库目录', value: 'library' },
]

export const healthChipLabels = {
  数据库: '数据库',
  存储空间: '存储',
  目录权限: '目录',
  current: '当前主库',
  sqlite: 'SQLite',
  postgresql: 'PG 主库',
  storages: '存储配置',
  config: '配置目录',
  plugin: '插件目录',
  download: '下载目录',
  library: '媒体库',
}
