# MoviePilot-Plugins

面向 [MoviePilot](https://github.com/jxxghp/MoviePilot) 的第三方插件库，遵循官方[第三方插件仓库规范](https://github.com/jxxghp/MoviePilot-Plugins/blob/main/docs/Repository_Guide.md)组织。

## 如何使用

在 MoviePilot 的「设定 → 插件 → 插件仓库」中添加本仓库地址：

```
https://github.com/clone-fan/MoviePilot-Plugins
```

保存后即可在插件市场中看到下列插件并安装。

## 插件列表

| 插件 | 说明 | 版本 |
| --- | --- | --- |
| MP 运维助手（AgentOpsAssistant） | 每日汇报、订阅追新、站点统计、插件日志清理、自动备份、更新检查与插件卸载清理，离线自包含。 | 1.0.20 |

## 仓库结构

```
MoviePilot-Plugins/
├── package.v2.json          # V2 插件市场索引
├── icons/                   # 插件图标
└── plugins.v2/              # V2 插件源码（目录名为插件类名小写）
    └── agentopsassistant/
        ├── __init__.py      # 插件主类
        ├── README.md        # 插件说明
        ├── src/             # Vue 联邦组件源码
        └── dist/assets/     # 前端构建产物
```

## 开发与构建

各插件为 Vue 联邦渲染模式。修改前端 `src/` 后需重新构建产物到 `dist/assets/`：

```bash
cd plugins.v2/agentopsassistant
npm install
npm run build
```

后端 `__init__.py` 修改后在 MoviePilot 插件页重载插件即可生效。

## 致谢

本仓库的「MP 运维助手」整合了 MoviePilot 社区多位作者优秀插件的能力与思路，在此一并致谢：

| 功能 | 参考来源 | 作者 |
|------|----------|------|
| 历史记录清理 | https://github.com/InfinityPacer/MoviePilot-Plugins | InfinityPacer |
| 自动备份 | https://github.com/thsrite/MoviePilot-Plugins | thsrite |
| 插件彻底卸载 | https://github.com/thsrite/MoviePilot-Plugins | thsrite |
| 订阅追新 | https://github.com/thsrite/MoviePilot-Plugins | thsrite |
| MoviePilot 更新推送 | https://github.com/jxxghp/MoviePilot-Plugins | jxxghp |
| 站点数据统计 | https://github.com/jxxghp/MoviePilot-Plugins | jxxghp |
| 插件库更新推送 | https://github.com/Aqr-K/MoviePilot-Plugins | Aqr-K |
| 日志清理（Vue） | https://github.com/madrays/MoviePilot-Plugins | madrays |
| 自动删种 | https://github.com/jxxghp/MoviePilot-Plugins | jxxghp |
| 插件自动更新 | https://github.com/thsrite/MoviePilot-Plugins | thsrite |
| 订阅规则自动填充 | https://github.com/thsrite/MoviePilot-Plugins | thsrite |
| 媒体库服务器通知 | https://github.com/jxxghp/MoviePilot-Plugins | jxxghp |
| 下载器助手 | https://github.com/hotlcc/MoviePilot-Plugins-Third | hotlcc |

同时特别感谢 [MoviePilot](https://github.com/jxxghp/MoviePilot)（作者 jxxghp）提供的插件框架与 API。
