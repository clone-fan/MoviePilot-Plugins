# 媒体融合 Signal

> **通知汇报、数据监控、下载管理、系统维护、插件卸载,你要的全在里面。**

一个 MoviePilot 插件,把散落的社区能力装进一个面板,让运维从"开十个插件"变成"开一个 Signal"。

## 它复刻了什么

这个插件不是从零造轮子,而是把社区里验证过的优秀能力**融合**进一个统一界面。致谢以下作者和仓库,没有他们就没有 Signal:

| 能力 | 来源插件 | 作者 | 仓库 |
|------|---------|------|------|
| 每日汇报 / TG 融合卡 | MoviePilot-Plugins | jxxghp | https://github.com/jxxghp/MoviePilot-Plugins |
| 订阅追新 + 规则填充 | SubscribeGroup | thsrite | https://github.com/thsrite/MoviePilot-Plugins |
| 站点数据统计 | SiteStatistic | jxxghp | https://github.com/jxxghp/MoviePilot-Plugins |
| 自动删种 | TorrentRemover | jxxghp | https://github.com/jxxghp/MoviePilot-Plugins |
| 下载器助手(打标签/概览) | DownloaderHelper | hotlcc | https://github.com/hotlcc/MoviePilot-Plugins |
| 自动备份恢复 | PluginAutoBackup | thsrite | https://github.com/thsrite/MoviePilot-Plugins |
| 日志清理 | LogClean | madrays | https://github.com/madrays/MoviePilot-Plugins |
| 历史记录清理 | HistoryClean | InfinityPacer | https://github.com/InfinityPacer/MoviePilot-Plugins |
| MP 更新推送 | MoviePilotUpdate | jxxghp | https://github.com/jxxghp/MoviePilot-Plugins |
| 插件库更新 | PluginAutoUpdate | Aqr-K / thsrite | https://github.com/Aqr-K/MoviePilot-Plugins |
| 插件卸载 | PluginUninstall | thsrite | https://github.com/thsrite/MoviePilot-Plugins |
| 媒体服务器通知 | MediaServerMsg | jxxghp | https://github.com/jxxghp/MoviePilot-Plugins |

> 每个功能的 UI 和交互都按 Signal 自己的设计语言重做,不是简单套壳。

## 它能做什么

### 汇报
每天一张 Telegram 融合汇报卡,把日报、订阅追新、站点统计、健康巡查、媒体动态装进同一张卡,点击展开看明细。支持流式更新,数据变了卡片自动刷新。

### 监控
站点在线状态、上传下载增量、存储空间、下载器活动种子、媒体服务器播放动态,全部在 MP 仪表盘实时可见。

### 管理
- 自动删种:按大小/分享率/做种时间/标签等条件定时清理
- 批量打标签:按 tracker 所属站点给种子补标签
- 订阅规则填充:下载后自动回填分辨率/质量/站点等规则
- 插件库更新:检测已装插件新版,可自动安装+重载

### 维护
- 自动备份:本地 + WebDAV 双通道,一键恢复
- 日志清理:按插件/按天数清理
- 插件卸载:走 MP 官方卸载流程,可选清理配置/数据/日志

### 快捷操作
仪表盘一键触发:发送日报、立即建卡、健康巡查、备份、清理、检查更新。

## 怎么用

1. MoviePilot 设置 → 插件 → 插件仓库,添加:
   ```
   https://github.com/clone-fan/MoviePilot-Plugins
   ```
2. 插件市场搜索"媒体融合 Signal",安装
3. 进入插件配置页,按需开启组件(默认全关,按需启用)

> 系统要求:MoviePilot ≥ v2.12.0

## 界面预览

*待补截图*

## 仓库结构

```
MoviePilot-Plugins/
├── package.v2.json          # V2 插件市场索引
├── icons/                   # 插件图标
└── plugins.v2/              # V2 插件源码
    └── agentopsassistant/
        ├── __init__.py      # 插件主类
        ├── README.md        # 插件说明
        ├── src/             # Vue 联邦组件源码
        └── dist/assets/     # 前端构建产物
```

## 开发说明

修改前端 `src/` 后需重新构建:

```bash
cd plugins.v2/agentopsassistant
npm install
npm run build
```

后端 `__init__.py` 修改后在 MoviePilot 插件页重载即生效。

## 协议

MIT