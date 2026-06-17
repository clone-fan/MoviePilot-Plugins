# 汇报栏目与组件对应关系分析

## 当前已在汇报中的栏目（reportSections）

| 栏目 ID | 栏目名称 | 对应组件 | 配置项 | 说明 |
|--------|--------|--------|--------|------|
| report_version | MoviePilot 版本 | daily_report | report_version | MP 版本信息 |
| report_site_status | 站点状态 | site_center | report_site_status | 各站点状态（馒头\|正常） |
| report_site_increment | 站点增量 | site_center | report_site_increment | 上传/下载/分享率增量 |
| report_today_download | 今日下载 | download_transfer | report_today_download | **去重后的** 下载统计（原"下载器"重复，已去重） |
| report_transfer | 入库整理 | download_transfer | report_transfer | 今日转移成功/失败 |
| report_subscribe | 订阅追新 | subscribe_center | report_subscribe | 订阅提醒追新内容 |
| report_storage | 存储空间 | system_storage | report_storage | 下载/媒体库目录空间占用 |
| report_media_stat | 媒体统计 | library_center | report_media_stat | 入库电影/电视剧统计 |
| report_summary | 今日摘要 | daily_report | report_summary | 前文内容的文字摘要 |

## 仪表盘已有的组件但汇报缺失的栏目

| 组件 | 仪表盘模块 | 缺失的汇报栏目 | 应对方案 |
|-----|---------|-------------|--------|
| 健康巡查 | 健康巡查卡片（成功/异常） | `report_health` | 新增：健康巡查结果（通过/异常） |
| 下载器助手 | 活动种子概览 | （无，下载统计已有 report_today_download） | 可聚合到 report_today_download 中 |
| 媒体通知 | （仪表盘暂无展示） | `report_media_notify` | **暂不推送汇报**，保留 webhook 通知即可 |

## 后续应补充的栏目（目前状态为"规划中"或"待接替"）

| 栏目 | 对应组件 | 现状 | v1.0.0 后的计划 |
|-----|--------|------|----------------|
| 下载器状态 | downloader_status | 规划中 | 后续版本补充 |
| 当前下载 | downloading | 已接入 | 已在 report_today_download 中 |
| 今日完成下载 | download_done | 规划中 | 后续版本补充 |
| 转移失败 | transfer_failed | 规划中 | 后续版本补充 |
| 最近入库 | latest_library | 规划中 | 与 report_media_stat 可聚合 |
| 目录健康 | directory_health | 规划中 | 与 report_health 聚合 |
| 系统基础健康 | system_health | 规划中 | 与 report_health 聚合 |

## 结论与建议

### 现有汇报对组件的覆盖情况
- ✅ **已完整映射**：版本、站点、下载、入库、订阅、存储、媒体统计
- ⚠️ **部分覆盖**：健康巡查（缺配置项）、媒体通知（仅 webhook，无汇报）
- ❌ **未接入**：后续规划功能

### v1.0.0 需要补充的配置项
1. **新增 `report_health`** — 健康巡查结果（通过/异常）
   - 需配置项：`report_health: bool`
   - 需配置项：`health_check_enabled: bool`（健康巡查总开关）
   - 需配置项：`health_check_cron: str`（巡查计划）
   - 需配置项：`health_check_items: list`（检查项选择）

2. **汇报栏目配置补全**
   - 在 Config.vue 的「每日汇报 > 汇报栏目」面板中显示所有栏目的开关
   - 每个栏目前加 Checkbox

### 后续版本（v1.1+）补充的可选栏目
- 下载器状态
- 转移失败提醒
- 系统存储进度（等后续功能完成）
