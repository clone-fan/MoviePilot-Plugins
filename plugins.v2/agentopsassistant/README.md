# MP 运维助手（AgentOpsAssistant）

面向 MoviePilot 的日常运维配置插件。提供模块化仪表盘、每日汇报、TG 融合汇报卡、订阅追新、站点统计、健康巡查、备份恢复、清理、更新、自动删种、种子打标签、媒体通知与插件卸载能力。

## 当前功能

- 每日汇报：设置是否发送、发送时间，并统一勾选要并入日报的栏目。
- 订阅追新：设置独立推送开关、推送时间、媒体类型和通知类型。
- 站点统计：设置是否采集站点数据、统计范围和通知内容。
- 插件日志清理：设置定时清理、保留行数、限定插件 ID 和结果通知。
- 健康巡查：检查数据库、存储空间、目录权限、站点、下载器和本插件任务状态。
- 自动备份：设置备份时间、本地保留数量、保存路径、WebDAV 备份参数，并支持本地/WebDAV 备份恢复。
- 更新检查：设置 MoviePilot 主程序和插件库更新检查；默认只检查和通知，不自动升级。
- 下载器管理：按规则自动删种，或按 tracker 站点为种子批量补标签。
- 媒体通知：接收媒体服务器事件并写入融合汇报卡。
- 插件卸载：多选目标插件，执行 MoviePilot 插件卸载，并按需清理配置、运行数据、日志和本地源码残留。

## 设置提示原则

- 提示只说明这个选项做什么、推荐怎么设置、什么时候需要开启或关闭。
- 不展示内部实现过程、开发计划或与当前配置无关的说明。
- 高影响选项放在对应任务内说明，不再单独拆出额外分类。

## 常用命令

- `/mpops_report`：发送 MP 运维每日汇报。
- `/mpops_subscribe`：立即推送订阅追新。
- `/mpops_report_preview`：预览每日汇报，不发送通知。
- `/mpops_health`：执行健康巡查。
- `/mpops_logs`：预览插件日志清理范围。
- `/mpops_logs_clean`：执行插件日志清理。
- `/mpops_backup`：执行一次自动备份。
- `/mpops_updates`：检查 MoviePilot 后端/前端更新。
- `/mpops_market`：检查插件库更新。
- `/mpops_plugin_preview`：预览插件卸载与残留清理范围。
- `/mpops_plugin_clean`：提示到配置页显式确认后执行插件卸载，远程命令不会直接卸载插件。
- `/mpops_seed_clean`：执行自动删种（按规则暂停或删除种子）。
- `/mpops_downloader_tag`：按站点为种子批量补打标签。

## 致谢

本插件整合了 MoviePilot 社区多位作者优秀插件的能力与思路，在此一并致谢：

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

同时特别感谢 [MoviePilot](https://github.com/jxxghp/MoviePilot)（作者 jxxghp）提供的插件框架与 API。
