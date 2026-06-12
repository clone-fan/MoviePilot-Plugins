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
| MP 运维助手（AgentOpsAssistant） | 每日汇报、订阅提醒、站点统计、插件日志清理、自动备份、更新检查与插件残留清理，离线自包含。 | 1.6.3 |

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
