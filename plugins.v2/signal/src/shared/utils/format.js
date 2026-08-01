// 共享格式化工具 — 跨组件复用，禁止在各 vue 里各写一份
/** 将字节数格式化为人类可读的 GB/MB 字符串 */
export function formatGB(bytes) {
  const n = Number(bytes) || 0
  const gb = n / (1024 ** 3)
  if (gb >= 1) return gb.toFixed(2) + ' GB'
  return (n / (1024 ** 2)).toFixed(1) + ' MB'
}

/** formatBytes = formatGB 别名（消除命名歧义） */
export const formatBytes = formatGB

/** 计算站点流量占比百分比字符串 */
export function sitePercent(value, total) {
  const t = Number(total) || 0
  if (!t) return '0%'
  return `${Math.round(((Number(value) || 0) / t) * 100)}%`
}

/** 站点饼图配色（CSS 变量版，自动适配 MP 主题） */
export const sitePieColors = [
  { color: 'rgba(var(--green), 0.94)', glow: 'rgba(var(--green), 0.28)' },
  { color: 'rgba(var(--cyan), 0.90)', glow: 'rgba(var(--cyan), 0.26)' },
  { color: 'rgba(var(--amber), 0.88)', glow: 'rgba(var(--amber), 0.24)' },
  { color: 'rgba(var(--blue), 0.88)', glow: 'rgba(var(--blue), 0.24)' },
  { color: 'rgba(var(--red), 0.84)', glow: 'rgba(var(--red), 0.22)' },
  { color: 'rgba(var(--violet), 0.86)', glow: 'rgba(var(--violet), 0.23)' },
  { color: 'color-mix(in srgb, rgb(var(--green)) 62%, rgb(var(--blue)))', glow: 'rgba(var(--green), 0.20)' },
  { color: 'color-mix(in srgb, rgb(var(--amber)) 68%, rgb(var(--cyan)))', glow: 'rgba(var(--amber), 0.20)' },
]
