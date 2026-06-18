#!/usr/bin/env node
import assert from 'node:assert/strict'
import fs from 'node:fs'

const page = fs.readFileSync('plugins.v2/agentopsassistant/src/components/Page.vue', 'utf8')

const requiredFragments = [
  'dashboard-shell',
  'dashboard-canvas',
  'alert-panel',
  'metrics-panel',
  'site-panel',
  'command-panel',
  'download-panel',
  'runtime-panel',
  '--shadow-panel',
  '--shadow-block',
  '--shadow-button',
  'grid-template-columns: minmax(300px, 410px) minmax(300px, 410px) minmax(280px, 1fr)',
  '命令面板',
  '站点数据统计',
  '下载器活动',
  '组件运行状况',
  'run_plugin_uninstall',
]

for (const fragment of requiredFragments) {
  assert.ok(page.includes(fragment), `Page.vue should contain static-draft fragment: ${fragment}`)
}

assert.ok(
  /const actionGroups = \[[\s\S]*group: '汇报与追新'[\s\S]*group: '站点与下载器'[\s\S]*group: '系统维护'[\s\S]*group: '插件治理'/m.test(page),
  'Page.vue should keep the command panel grouped like the final static draft',
)

assert.ok(
  /const metricCards = computed\(\(\) => \[/m.test(page),
  'Page.vue should expose the four metric cards as computed real data',
)
