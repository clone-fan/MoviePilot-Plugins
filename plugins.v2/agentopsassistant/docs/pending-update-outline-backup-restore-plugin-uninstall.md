# MP 运维助手待更新大纲：备份恢复与插件卸载交互修复

> 面向后续实现者：本文件是项目内待更新大纲和实现计划。实施时必须先按 TDD 增加失败用例，再改后端和前端，最后构建 `dist/` 并同步 `package.v2.json` 与 `plugin_version`。

## 目标

1. 自动备份支持一键恢复，至少覆盖本插件生成的本地备份包。
2. 插件卸载支持“选择目标后直接执行”，不再要求用户先保存配置。
3. 插件卸载成功后，配置页目标选择框自动移除已卸载插件，不残留英文 ID chip。
4. 抓虫：插件内部相关组件未开启时，禁止走对应插件/链路获取数据；所有数据采集以 AgentOpsAssistant 自身组件开关为主。
5. 需求：本插件运行时必须实时获取当前数据，不允许通过读取旧版文档、历史说明、旧缓存或上次结果来冒充实时数据；用户关闭相关组件时必须断掉对应数据路径。
6. 抓虫：插件总开关必须发挥最高优先级效果；总开关关闭后停止一切业务链路，不能通过分开关、手动按钮、定时任务、远程命令或 API 继续运行。
7. 终验要求：完成上述待更新任务后，必须进行全插件抓虫、清理屎山代码/技术债、清除屎山 bug、完成全面复盘，并通过本机实机验收后才能结束任务。

## 当前依据

- 自动备份入口：`plugins.v2/agentopsassistant/__init__.py` 中 `api_run_backup()`、`run_backup()`、`_build_backup_status()`、`_create_agentops_backup()`。
- 备份包内容：`category.yaml`、`app.env`、`cookies/`、SQLite 的 `user.db*` 或 PostgreSQL 的 `postgresql_backup.sql`，并带 `manifest.json`。
- 插件卸载入口：`api_run_plugin_uninstall()` 只读取后端已初始化配置中的 `_plugin_uninstall_ids`。
- 配置页动作入口：`Config.vue` 的 `runAction()` 当前调用 `postPluginApi(props.api, path)`，没有把当前表单传给后端。
- 目标选择框：`Config.vue` 的 `VSelect v-model="form.plugin_uninstall_ids"` 使用 `installedPlugins`，但执行后没有刷新列表并裁剪已选值。
- 组件状态入口：`_component_status()`、`api_dashboard()`、日报/仪表盘构建函数和各 `run_*` 入口需要统一遵守组件开关。若 `subscribe_reminder_enabled`、`site_stat_enabled`、`health_check_enabled`、`backup_enabled`、`market_update_enabled`、`seedclean_enabled`、`dltag_enabled`、`msgnotify_enabled`、`subfill_enabled` 等关闭，不应继续访问相应 MoviePilot 链路、第三方插件能力或重型数据源。
- 实时数据约束：README、CHANGELOG、history、旧版文档、wiki 缓存、上次任务结果、旧快照只能作为配置说明或历史展示，不能作为仪表盘/日报/状态 API 的当前数据来源。若实时链路不可用，应返回“未启用/已跳过/实时获取失败”，不要回退成旧时数据。
- 总开关约束：`enabled` / `_enabled` 是最高优先级。`init_plugin()`、`get_service()`、`handle_command()`、所有 `api_run_*`、`run_*`、onlyonce、仪表盘主动刷新、日报预览和前端手动动作都必须先判断总开关；总开关关闭时，只允许返回静态关闭状态和配置页保存能力，不允许继续执行组件业务。
- 终验约束：不能在单点修复后直接宣布完成。必须用 PUA 技能进行自我施压式蓝军自检，最大化穷举潜在 bug，再执行全插件回归、技术债清理、复盘和本机实机验收。

## 推荐方案

采用“动作 payload 优先，保存配置兜底”的方案。

- 插件卸载执行时，前端把当前表单里的 `plugin_uninstall_ids`、清理范围、通知类型等字段作为 payload 传给 `/run_plugin_uninstall`。
- 后端对 payload 做一次临时覆盖，只影响本次动作，不写入持久配置。
- 卸载成功后前端重新拉取 `installed_plugins`，并把已不在列表中的 ID 从 `form.plugin_uninstall_ids` 中移除。
- 自动备份恢复新增独立 API 和 UI，不复用“保存后立即运行一次”开关。

备选方案是“点击执行前自动保存配置再执行”，实现较少，但会把一次性危险操作写进持久配置，且仍可能受插件重载时序影响，因此不推荐。

## 实现计划

### 任务 1：为插件卸载直接执行补失败测试

文件：
- 修改：`tests/run_local_tests.py`
- 修改：`tests/run_frontend_api_tests.mjs`

步骤：
1. 在后端测试中新增用例：`api_run_plugin_uninstall({"plugin_uninstall_ids": ["AutoBackup"]})` 应能执行，即使插件实例初始化时 `plugin_uninstall_ids=[]`。
2. 断言本次 payload 不会污染实例原有 `_plugin_uninstall_ids`。
3. 在前端 API 测试中断言点击 `run_plugin_uninstall` 时会 POST 当前选择的插件 ID 和清理开关。
4. 先运行新增测试并确认失败，失败原因应是接口忽略 payload 或前端未传 payload。

### 任务 2：后端支持本次动作临时配置

文件：
- 修改：`plugins.v2/agentopsassistant/__init__.py`

步骤：
1. 新增小函数，例如 `_plugin_uninstall_config_from_payload(payload)`，只提取允许字段：
   - `plugin_uninstall_ids`
   - `plugin_uninstall_remove_plugin`
   - `plugin_uninstall_clear_config`
   - `plugin_uninstall_clear_data`
   - `plugin_uninstall_delete_source`
   - `plugin_uninstall_notify`
   - `plugin_uninstall_notify_type`
2. 调整 `_build_plugin_uninstall_status(clean=False, override=None)`，读取 override 优先于实例字段。
3. 调整 `run_plugin_uninstall_clean(override=None)` 和 `api_run_plugin_uninstall(payload=None)`。
4. 保持远程命令 `/mpops_plugin_clean` 继续只读取已保存配置。
5. 复跑任务 1 的后端测试，确认绿灯。

### 任务 3：前端执行时携带当前表单并清理残留选择

文件：
- 修改：`plugins.v2/agentopsassistant/src/components/Config.vue`
- 如有必要修改：`plugins.v2/agentopsassistant/src/components/api.js`

步骤：
1. 新增 `buildActionPayload(path)`：
   - 对 `run_plugin_uninstall` 返回插件卸载相关表单字段。
   - 其他动作返回 `{}`。
2. 修改 `runAction(path, label)`，调用 `postPluginApi(props.api, path, buildActionPayload(path))`。
3. 当 `run_plugin_uninstall` 返回成功后：
   - 调用 `loadInstalledPlugins()`。
   - 用新列表裁剪 `form.plugin_uninstall_ids`。
   - 如果后端返回 `data.uninstalled`，优先移除成功卸载的 ID。
4. 保持按钮禁用逻辑与当前表单绑定，避免未选择目标时执行。
5. 增加或更新静态测试，覆盖“执行后选择框不显示已卸载 ID”。

### 任务 4：为备份恢复补后端失败测试

文件：
- 修改：`tests/run_local_tests.py`

步骤：
1. 用临时目录构造合法备份目录和 `bk_YYYYmmddHHMMSS.zip`。
2. 测试 `_list_backup_archives()` 只列出备份目录内的 `bk_*.zip`。
3. 测试非法路径、路径穿越、缺少 `manifest.json` 的包会被拒绝。
4. 测试恢复前会创建 emergency backup，并按用户选择恢复 `category.yaml`、`app.env`、`cookies/`。
5. SQLite 场景测试 `user.db*` 恢复路径；PostgreSQL 场景先测试“缺少 psql 时返回可读失败，不破坏现有配置”。
6. 先运行新增测试并确认失败。

### 任务 5：实现本地备份一键恢复后端能力

文件：
- 修改：`plugins.v2/agentopsassistant/__init__.py`

新增 API：
- `GET /backup_archives`：列出可恢复备份包。
- `POST /preview_backup_restore`：预览恢复内容和风险。
- `POST /run_backup_restore`：执行恢复。

核心规则：
- 只允许恢复 `_backup_path` 下的 `bk_*.zip`。
- 解压必须进入临时目录，逐项校验路径，禁止 zip slip。
- 执行恢复前强制创建 emergency backup。
- 支持恢复项：
  - 配置文件：`category.yaml`、`app.env`
  - cookies 目录
  - SQLite：`user.db*`
  - PostgreSQL：仅当备份内有 `postgresql_backup.sql` 且容器内存在 `psql` 时执行；否则返回可读失败。
- 恢复结果写入任务记录并按配置发送通知。

### 任务 6：增加配置页一键恢复 UI

文件：
- 修改：`plugins.v2/agentopsassistant/src/components/Config.vue`

建议 UI 放在“自动备份”页本地备份卡片下方：
- 备份包选择框：来源 `backup_archives`。
- 恢复范围复选项：配置文件、cookies、数据库。
- 预览按钮：调用 `preview_backup_restore`，展示备份时间、包含内容、将覆盖的路径。
- 一键恢复按钮：需要先开启确认开关或输入确认文本。
- 执行成功后提示用户重启 MoviePilot 或按实际返回信息展示后续动作。

交互要求：
- 不要求保存配置即可恢复。
- 没有备份包时显示空状态，恢复按钮禁用。
- PostgreSQL 无法自动恢复时，预览中明确提示原因。

### 任务 7：组件关闭时禁止访问相关链路抓虫

文件：
- 修改：`tests/run_local_tests.py`
- 修改：`plugins.v2/agentopsassistant/__init__.py`
- 必要时修改：`plugins.v2/agentopsassistant/src/components/Page.vue`

步骤：
1. 先补失败测试：构造插件实例并关闭目标组件开关，替换对应链路函数为会抛错的哨兵函数，调用仪表盘、日报预览或相关构建函数时应不触发哨兵。
2. 至少覆盖这些开关与链路：
   - `enabled=False` 时，即使所有分开关均为 True，也不注册定时服务、不执行 onlyonce、不响应手动业务动作、不访问任何外部链路。
   - `site_stat_enabled=False` 时，不采集站点增量/站点统计图数据。
   - `subscribe_reminder_enabled=False` 且日报订阅栏目关闭或依赖未满足时，不查询订阅追新链路。
   - `health_check_enabled=False` 时，不执行健康巡查采集，只展示关闭状态或最近缓存。
   - `backup_enabled=False` 时，仪表盘只读备份状态，不触发备份创建、WebDAV 或数据库导出。
   - `market_update_enabled=False` 时，不抓取插件市场更新数据。
   - `seedclean_enabled=False`、`dltag_enabled=False` 时，不访问下载器种子列表。
   - `msgnotify_enabled=False`、`subfill_enabled=False` 时，不访问媒体服务器通知或订阅填充链路。
3. 穷举总开关关闭矩阵并补测试：
   - 总开关关 + 分开关全开：所有 `get_service()` 业务服务为空或不含本插件业务服务。
   - 总开关关 + `*_onlyonce=True`：初始化后不得触发一次性任务；可以安全复位开关，但不能跑业务。
   - 总开关关 + 前端按钮/`api_run_*`：返回“插件未启用，已跳过”，不得调用 `run_*` 业务链路。
   - 总开关关 + 远程命令 `handle_command()`：不执行业务，只返回/通知未启用。
   - 总开关关 + 仪表盘/日报预览：仅展示插件关闭状态，不访问站点、订阅、下载器、健康巡查、更新检查、备份、媒体服务器等链路。
   - 总开关关 + 分开关保存为开启：配置可以保存，但业务仍保持停止，直到总开关重新开启。
4. 在后端增加统一守卫，例如 `_plugin_active()` + `_component_enabled(key)`；所有业务入口先判总开关，再判组件开关。默认只允许读取轻量关闭状态，不允许访问外部链路或可能触发慢查询的 MoviePilot chain/helper。
5. 若日报栏目依赖组件开关，按“总开关优先、组件开关其次”：总开关关闭时整份业务日报跳过；组件关闭时对应栏目返回“未启用/已跳过”，不要为了生成日报临时访问数据。
6. 手动按钮 `run_*` 不能绕过总开关；总开关关闭时所有业务动作返回可读提示。总开关开启但组件关闭时，高风险/依赖型动作返回“组件未启用，已跳过”，并提示先启用对应组件。
7. 增加实时数据防回退测试：关闭总开关、关闭组件或让实时链路抛错时，返回值必须是“未启用/已跳过/实时获取失败”，不得读取 README、CHANGELOG、package history、旧版文档、`last_*` 任务结果或历史快照来填充当前数据。
8. 允许读取历史数据的场景必须显式命名为历史展示，例如“最近一次执行结果”“上次备份列表”；这些字段不得标成当前实时状态。
9. 复跑本任务新增测试，确认所有总开关关闭态和组件关闭态均不访问对应链路，也不读取旧文档/旧缓存伪造实时数据。

### 任务 8：全插件抓虫、技术债清理与 PUA 终验

文件：
- 修改：`tests/run_local_tests.py`
- 修改：`tests/run_frontend_api_tests.mjs`
- 修改：`tests/run_page_static_tests.mjs`
- 按发现的问题修改：`plugins.v2/agentopsassistant/__init__.py`
- 按发现的问题修改：`plugins.v2/agentopsassistant/src/components/*.vue`
- 按发现的问题修改：`plugins.v2/agentopsassistant/src/components/api.js`

步骤：
1. 在前面所有待更新任务完成后，进入全插件抓虫，不允许只验证本次改动涉及的点。
2. 使用 PUA 技能进行自我施压式穷举，自检至少覆盖：
   - 总开关、组件开关、onlyonce、定时服务、手动按钮、远程命令、API 入口是否一致。
   - 仪表盘、配置页、日报预览、通知、健康巡查、备份恢复、插件卸载、插件更新、下载器、媒体服务器、订阅填充、站点统计是否存在关闭态仍跑链路的问题。
   - 实时数据、历史展示、缓存、旧文档、上次任务结果是否被混用。
   - 危险操作是否有预览、保护名单、备份、路径边界校验和用户确认。
   - 前端是否存在按钮误判成功、payload 丢失、保存/执行状态不同步、卸载后 chip 残留、滚动/布局遮挡。
3. 清理屎山代码/技术债：删除死开关、重复分支、不可达逻辑、过期兼容入口、无用 helper、重复状态字段；保留必要兼容时必须写明原因并有测试覆盖。
4. 清除屎山 bug：每发现一个模式级 bug，先补失败测试，再修同类入口，不能只修单点。
5. 完成全面复盘，至少包含：
   - 本轮修复了哪些根因。
   - 哪些同类问题已扫完。
   - 哪些风险仍需用户真机观察。
   - 后续如何防止同类回归。
6. 通过本机实机验收后才允许进入最终交付口径。本机实机验收至少包含：
   - 本地/真机 MoviePilot 加载插件页面。
   - 配置页保存、总开关关闭、分开关组合、手动按钮、仪表盘刷新、日报预览。
   - 备份恢复预览、插件卸载预览/执行的安全路径。
   - 浏览器或接口证据截图/日志/返回值。
7. 没有本机实机验收证据时，最终状态只能写“候选完成，等待实机验收”，不能写完成。

### 任务 9：版本、构建与验收

文件：
- 修改：`plugins.v2/agentopsassistant/__init__.py`
- 修改：`package.v2.json`
- 修改：`plugins.v2/agentopsassistant/dist/`

步骤：
1. 版本号递增，并在 `package.v2.json` history 顶部写清：
   - 新增自动备份一键恢复。
   - 修复插件卸载未保存配置时执行无效。
   - 修复卸载后目标选择框残留已卸载 ID。
   - 修复组件关闭时仍访问对应插件/链路获取数据的问题，组件开关优先。
   - 强化实时数据约束：当前状态不再回退读取旧版文档、旧缓存或上次结果。
   - 修复插件总开关关闭后分开关、定时、手动动作、远程命令或 API 仍可运行的问题。
   - 完成全插件抓虫、技术债清理、复盘和本机实机验收。
2. 运行：
   - `python -m py_compile plugins.v2/agentopsassistant/__init__.py`
   - `python tests/run_local_tests.py`
   - `node tests/run_frontend_api_tests.mjs`
   - `node tests/run_page_static_tests.mjs`
   - `cd plugins.v2/agentopsassistant && npm run build`
   - `python -c "import json;json.load(open('package.v2.json',encoding='utf-8'))"`
3. 核对 `dist/index.html` 和 `dist/assets/remoteEntry.js` 引用的文件真实存在。
4. 在真实 MoviePilot 页面验收：
   - 选择插件后不保存，直接执行卸载能生效。
   - 卸载成功后选择框不再显示被卸载插件 ID。
   - 选择备份包后可预览并执行恢复，失败场景有明确提示。
   - 关闭任一组件后刷新仪表盘/日报预览，不访问对应外部链路，页面显示已停用或跳过。
   - 断开实时链路时，页面/API 明确显示实时获取失败或已跳过，不展示旧版文档/旧缓存中的旧时数据。
   - 关闭插件总开关后，即使分开关仍显示开启，也不注册定时、不执行 onlyonce、不响应业务按钮/远程命令/API，不采集任何业务数据。
   - 完成全插件抓虫清单，提供 PUA 自检问题列表、修复证据、复盘结论和本机实机验收证据。

## 验收标准

- 用户不需要保存配置，也能直接执行插件卸载。
- 已卸载插件不会继续作为已选 chip 留在目标选择框。
- 备份列表只展示合法备份包，一键恢复具备预览、确认、执行结果和 emergency backup。
- 组件未开启时，相关数据链路被明确跳过；手动动作也按组件开关返回可读提示，不偷偷访问数据。
- 当前数据必须来自实时链路；旧版文档、历史说明、旧缓存、上次结果不得作为当前数据兜底。用户关闭组件时，对应路径必须断开。
- 插件总开关关闭时停止一切业务：分开关开启不能绕过总开关，定时、onlyonce、手动按钮、远程命令、状态 API 和数据采集链路都必须跳过。
- 完成上述任务后，必须进行全插件抓虫、清理屎山代码/技术债、清除屎山 bug、PUA 穷举自检、全面复盘和本机实机验收；缺任一项都不能结束任务。
- 所有新增行为都有失败测试先行记录，最终本地测试和前端构建通过。
