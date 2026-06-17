# AgentOpsAssistant 系统性改进方案 v1.0.0

## 概述

根据用户需求，对 AgentOpsAssistant 进行 8 个维度的系统性改进，目标是：
1. **汇报栏目与组件深度绑定** — 栏目对应组件，组件配置与栏目开关一一对应
2. **仪表盘补强** — 手动触发按钮清晰分组、文案明确、有说明
3. **组件独立化** — 健康巡查成为完整的组件（配置+触发+汇报）
4. **说明易发现** — 每个功能的说明在配置内容顶部醒目显示
5. **通知渠道统一** — 检查现有通知是否都走了 MP 插件通知渠道（媒体库除外）
6. **插件设计统一** — 每个功能的启用、定时、触发、说明遵循统一模式
7. **下载器助手配置** — 参考自动删种的结构进行配置设计
8. **媒体库通知配置** — 参考自动删种的结构进行配置设计

---

## 方案详述

### 1. 汇报栏目补强 — 新增 `report_health` 与深度绑定

#### 现状问题
- 汇报栏目与其对应的组件关系不清晰
- 健康巡查在仪表盘有展示，但汇报中无对应栏目
- 栏目开关与组件配置分离，用户改组件配置后还要单独调整汇报栏目开关

#### 改进方案

**后端配置项补充：**
```python
# 新增：健康巡查相关配置（在 init_plugin 中初始化）
_health_check_enabled: bool = True              # 健康巡查总启用
_health_check_cron: str = "0 */6 * * *"         # 健康巡查计划（默认每 6 小时）
_health_check_items: List[str] = []             # 选择检查项：['db', 'storage', 'directory', ...]
_report_health: bool = True                     # 健康巡查结果是否并入汇报

# 修改：report_today_download 增强（避免与其他下载相关栏目重复）
_report_downloading: bool = True                # 当前下载任务（已有，确保存在）
```

**前端配置（Config.vue - defaults）：**
```javascript
// 在 defaults 中新增
health_check_enabled: true,
health_check_cron: '0 */6 * * *',
health_check_items: [],
report_health: true,
```

**前端配置页面（Config.vue - 「每日汇报」> 「汇报栏目」）：**
- 改为一个表格/列表，展示所有可用的 report_* 配置项
- 每行显示：
  - ☐ 栏目开关（Checkbox）
  - 栏目名称（label）
  - 对应的组件（信息提示）
  - 可选：该栏目特定的参数配置（如 report_site_status 的显示格式）

示例 UI：
```
汇报栏目配置
┌─ 勾选启用的栏目，以下栏目将聚合进每日汇报

☐ MoviePilot 版本              [系统] 显示 MP 后端/前端版本
☑ 站点状态                    [站点] 显示各站点连接状态（正常/异常）
☑ 站点增量                    [站点] 显示上传/下载增量
☑ 今日下载                    [下载] 显示今日下载数量与体积
☑ 入库整理                    [媒体] 显示今日转移成功/失败
☑ 订阅追新                    [订阅] 显示今日追新电影/电视剧
☑ 存储空间                    [系统] 显示下载/媒体库目录占用
☑ 媒体统计                    [媒体] 显示库内电影/电视剧总数
☑ 系统健康                    [系统] 显示健康巡查结果（通过/异常）
☐ 今日摘要                    [系统] 前述栏目的文字摘要
```

#### 配置与组件的对应关系表

| 栏目 ID | 栏目名称 | 对应组件 | 组件配置项 | 栏目开关 | 说明 |
|--------|--------|--------|----------|--------|------|
| report_version | MoviePilot 版本 | daily_report | — | report_version | — |
| report_site_status | 站点状态 | site_center | — | report_site_status | — |
| report_site_increment | 站点增量 | site_center | site_stat_enabled | report_site_increment | 需启用「站点数据统计」 |
| report_today_download | 今日下载 | download_transfer | — | report_today_download | — |
| report_transfer | 入库整理 | download_transfer | — | report_transfer | — |
| report_subscribe | 订阅追新 | subscribe_center | subscribe_reminder_enabled | report_subscribe | 需启用「订阅提醒」 |
| report_storage | 存储空间 | system_storage | — | report_storage | — |
| report_media_stat | 媒体统计 | library_center | — | report_media_stat | — |
| report_health | 系统健康 | system_storage | health_check_enabled | report_health | 需启用「健康巡查」 |
| report_summary | 今日摘要 | daily_report | — | report_summary | — |

**关键规则：**
- 如果 `report_site_increment` 启用，需 `site_stat_enabled = true`（依赖关系）
- 如果 `report_subscribe` 启用，需 `subscribe_reminder_enabled = true`（依赖关系）
- 如果 `report_health` 启用，需 `health_check_enabled = true`（依赖关系）
- 在前端切换栏目开关时，若其依赖组件未启用，应给予提示："需先启用「站点数据统计」"

---

### 2. 仪表盘补强 — 手动触发重组织

#### 现状问题
- 手动触发按钮无分组，堆放在一起
- 按钮名字不清晰（如"立即运行一次日报"可能不清楚是什么意思）
- 没有功能说明

#### 改进方案

**Page.vue - 手动触发卡片重组织：**

将现有的随意按钮改为**分组结构**（参考 Config.vue 的左侧导航风格）：

```javascript
// Page.vue - script 部分

const actionGroups = [
  {
    group: '汇报中心',
    icon: 'mdi-newspaper-variant-outline',
    actions: [
      { path: 'run_daily_report', label: '立即推送每日汇报', desc: '手动发送一份汇报到通知渠道' },
    ]
  },
  {
    group: '订阅与站点',
    icon: 'mdi-bell-ring-outline',
    actions: [
      { path: 'run_subscribe_reminder', label: '推送订阅提醒', desc: '手动推送一次订阅追新提醒' },
      { path: 'run_site_stat', label: '更新站点数据', desc: '重新采集站点上传/下载数据' },
    ]
  },
  {
    group: '下载与媒体',
    icon: 'mdi-download-network-outline',
    actions: [
      { path: 'run_downloader_overview', label: '刷新活动种子', desc: '重新加载下载器中的活动种子概览' },
      // { path: 'run_media_notify', label: '检查媒体通知', desc: '手动检查是否有待推送的媒体通知' },
    ]
  },
  {
    group: '系统维护',
    icon: 'mdi-cog-outline',
    actions: [
      { path: 'run_backup', label: '执行备份', desc: '立即执行一次配置备份' },
      { path: 'run_log_clean', label: '清理日志', desc: '立即清理插件日志（按保留行数）' },
      { path: 'run_mp_update', label: '检查 MP 更新', desc: '检查 MoviePilot 后端/前端更新' },
      { path: 'run_market_update', label: '检查插件库更新', desc: '检查插件库及已安装插件更新' },
      { path: 'run_health_check', label: '执行健康巡查', desc: '手动执行一次系统健康巡查' },
    ]
  }
]
```

**Page.vue - template 部分：**
```vue
<!-- 手动触发卡片改为分组显示 -->
<VCard class="mb-3">
  <VCardTitle class="d-flex align-center">
    <VIcon icon="mdi-play-circle-outline" class="mr-2" color="primary" />
    手动触发
  </VCardTitle>
  <VCardText>
    <div v-for="group in actionGroups" :key="group.group" class="mb-4">
      <!-- 分组标题 -->
      <div class="d-flex align-center mb-2">
        <VIcon :icon="group.icon" size="20" class="mr-2" color="primary" />
        <span class="text-subtitle2 font-weight-medium">{{ group.group }}</span>
      </div>
      <!-- 该分组下的按钮 -->
      <div class="ml-4">
        <div v-for="action in group.actions" :key="action.path" class="mb-2">
          <VBtn
            size="small"
            variant="outlined"
            color="primary"
            :loading="actionRunning === action.path"
            @click="runAction(action.path, action.label)"
            class="text-none"
          >
            {{ action.label }}
          </VBtn>
          <div class="text-caption text-grey mt-1">{{ action.desc }}</div>
        </div>
      </div>
    </div>
    <VAlert v-if="actionMessage" type="info" variant="tonal" class="mt-3" :text="actionMessage" />
  </VCardText>
</VCard>
```

#### API 端点检查
确保以下 API 在后端都有实现：
- `POST /api/plugins/agentopsassistant/run_daily_report` → `run_daily_report()`
- `POST /api/plugins/agentopsassistant/run_subscribe_reminder` → `run_subscribe_reminder()`
- `POST /api/plugins/agentopsassistant/run_site_stat` → `run_site_stat()`
- `POST /api/plugins/agentopsassistant/run_downloader_overview` → `run_downloader_overview()`（获取数据，仪表盘刷新）
- `POST /api/plugins/agentopsassistant/run_backup` → `run_backup()`
- `POST /api/plugins/agentopsassistant/run_log_clean` → `run_log_clean()`
- `POST /api/plugins/agentopsassistant/run_mp_update` → `run_mp_update()`
- `POST /api/plugins/agentopsassistant/run_market_update` → `run_market_update()`
- `POST /api/plugins/agentopsassistant/run_health_check` → `run_health_check()`

---

### 3. 组件补强 — 健康巡查成为独立组件

#### 现状问题
- 健康巡查在 Page.vue 中硬编码显示，不是独立的配置模块
- 配置页无「健康巡查」一级分类，用户无法配置巡查计划和选择巡查项

#### 改进方案

**后端新增 HealthCheck 类：**
```python
# 在 __init__.py 中新增

class HealthCheck:
    """系统健康巡查组件：检查数据库、存储、目录等."""
    
    def __init__(self, plugin):
        self.plugin = plugin
    
    def check_all(self, items: List[str] = None) -> Dict[str, Any]:
        """执行所有勾选的健康检查.
        
        Args:
            items: 检查项列表，如 ['db', 'storage', 'directory']
                   为空时检查所有可用项
        
        Returns:
            {
              'success': bool,  # 所有检查是否通过
              'checks': [
                {'name': '数据库', 'status': 'success', 'message': '...'},
                {'name': '存储空间', 'status': 'error', 'message': '...'},
              ]
            }
        """
        pass
    
    def check_db(self) -> Tuple[bool, str]:
        """检查数据库连接."""
        pass
    
    def check_storage(self) -> Tuple[bool, str]:
        """检查存储空间."""
        pass
    
    def check_directory(self) -> Tuple[bool, str]:
        """检查配置目录."""
        pass

```

**前端配置页面（Config.vue）：**
- 在「系统维护」分组中新增「健康巡查」一级分类
- 配置面板包含：
  - 启用开关 + 说明
  - Cron 定时设置
  - 检查项多选（数据库、存储、目录等）
  - 通知选项
  - 手动触发按钮

示例配置项：
```javascript
defaults = {
  health_check_enabled: true,
  health_check_cron: '0 */6 * * *',
  health_check_items: ['db', 'storage'],  // 用户选择要检查的项
  health_check_notify: true,
  health_check_onlyonce: false,
}
```

---

### 4. 组件说明补强 — 说明在分类内容顶部

#### 现状问题
- Config.vue 顶部显示的 `currentMain.desc`，用户容易忽略

#### 改进方案

**Config.vue - template 改进：**
```vue
<!-- 在 aoa-subtabs 下方、content 内容上方添加说明 -->
<section class="aoa-content">
  <div class="aoa-subtabs">
    <!-- 现有的二级标签 -->
  </div>
  <VDivider />
  
  <!-- ↓ 新增：说明卡片（每切换一级分类就显示对应说明） -->
  <VAlert 
    v-if="currentMain.desc" 
    type="info" 
    variant="tonal" 
    class="ma-3"
    :text="currentMain.desc"
  >
    <template #prepend>
      <VIcon icon="mdi-information-outline" />
    </template>
  </VAlert>
  
  <!-- 现有的内容窗口 -->
  <div class="aoa-window">
    <!-- ... 各个配置面板 ... -->
  </div>
</section>
```

效果：用户每切换一个一级分类（如从「汇报中心」切到「订阅提醒」），说明卡片会自动更新。

---

### 5. 通知渠道检查 — 查找 bug

#### 任务清单

**后端通知函数扫描：**
- [ ] grep 搜索所有 `notify()` 调用，检查是否都使用了 `self.eventmanager.send('plugin_notify', ...)`
- [ ] grep 搜索所有 `send()` 调用，确认目标是 `plugin_notify` 事件或特定事件（如 webhook）
- [ ] 检查媒体库通知是否正确发送到 webhook（不走 MP 通知渠道）
- [ ] 检查是否有直接 `print()`、文件写入或其他通知渠道

**特别检查的功能：**
1. 每日汇报推送 — 应走 `plugin_notify`
2. 订阅提醒推送 — 应走 `plugin_notify`
3. 媒体库通知 — 应走 webhook（`msgnotify_servers`），不改
4. 备份完成 — 应走 `plugin_notify`
5. 日志清理 — 应走 `plugin_notify`
6. 更新检查 — 应走 `plugin_notify`
7. 健康巡查 — 应走 `plugin_notify`

**目标：** 确保所有通知都走了正确的渠道，没有遗漏或走错的。

---

### 6. 插件设计统一 — 每个功能的标准模式

#### 统一的配置结构

**每个一级分类（功能模块）都应遵循这个顺序：**

1. **启用开关 + 说明**
   ```vue
   <VSwitch v-model="form.feature_enabled" label="启用 [功能名]" />
   <VAlert type="info" variant="tonal" text="[功能说明]" class="mt-2" />
   ```

2. **定时计划**（如果该功能有定时触发）
   ```vue
   <VCronField v-model="form.feature_cron" label="执行时间 (Cron)" :disabled="!form.feature_enabled" />
   ```

3. **功能特定的配置**
   ```vue
   <!-- 如选择项、参数等 -->
   ```

4. **通知选项**
   ```vue
   <VSwitch v-model="form.feature_notify" label="执行完成后发送通知" />
   ```

5. **保存后立即运行**（可选）
   ```vue
   <VSwitch v-model="form.feature_onlyonce" label="保存后立即运行一次" />
   ```

#### 统一的仪表盘手动触发文案

- 「立即 [功能名]」— 一次性执行
  - 如：「立即推送汇报」「立即执行备份」
- 「更新 [数据源]」— 获取数据并刷新展示
  - 如：「更新站点数据」

---

### 7. 下载器助手配置统一

**参考对象：** 自动删种（seedclean）配置面板

**改进方案（dltag）：**

```
下载器助手配置
├─ 启用开关
│  ☑ 启用下载器助手
│  说明：为下载器中的种子按站点批量补打标签...
├─ 下载器选择
│  ☑ qBittorrent
│  ☑ Transmission
├─ 标签规则
│  标签前缀：[输入框] mp_
│  标签格式：按站点名
├─ 通知
│  ☑ 操作完成后发送通知
```

配置项对标 seedclean 的结构。

---

### 8. 媒体库服务器通知配置统一

**参考对象：** 自动删种（seedclean）配置面板

**改进方案（msgnotify）：**

```
媒体库通知配置
├─ 启用开关
│  ☑ 启用媒体库通知
│  说明：监听 Emby/Jellyfin/Plex 的 webhook 事件并推送通知...
├─ 服务器选择
│  ☑ Emby
│  ☑ Jellyfin
│  ☐ Plex
├─ 事件类型
│  ☑ 新入库
│  ☑ 开始播放
│  ☑ 停止播放
│  ☑ 登录成功
│  ☑ 登录失败
│  ☑ 标记
├─ 通知
│  ☑ 事件触发时发送通知
```

配置项对标 seedclean 的结构。

**重要：** 媒体库通知的推送目标是各服务器的 webhook，而不是 MP 的插件通知渠道。此处不改。

---

## 实现优先级

| 优先级 | 条目 | 预计工作量 |
|--------|------|---------|
| **P0** | 5. 通知渠道 bug 检查 | 1-2 小时（grep + 验证） |
| **P1** | 2. 仪表盘重组织 | 2-3 小时（前端） |
| **P1** | 4. 说明卡片 | 0.5 小时（前端） |
| **P2** | 1. 汇报栏目补强 | 3-4 小时（前后端 + 配置表） |
| **P2** | 3. 健康巡查组件化 | 4-5 小时（后端 + 前端） |
| **P2** | 6. 设计统一 | 1-2 小时（规范文档 + 代码调整） |
| **P3** | 7. 下载器助手统一 | 2-3 小时（前端调整） |
| **P3** | 8. 媒体库通知统一 | 2-3 小时（前端调整） |

**总计：** 约 16-23 小时（假设单人）

---

## 测试检查清单

- [ ] 所有 report_* 配置项在 init_plugin 中正确初始化
- [ ] 汇报栏目表在配置页正确渲染，开关生效
- [ ] 仪表盘手动触发分组正确渲染，按钮可点击
- [ ] 每个手动触发按钮对应的 API 都能调用成功
- [ ] 说明卡片在每个一级分类中正确显示
- [ ] 健康巡查配置页正确渲染，定时计划生效
- [ ] 健康巡查手动触发成功执行
- [ ] 所有通知都走了正确的渠道（检查日志）
- [ ] 下载器助手配置页参考 seedclean 风格
- [ ] 媒体库通知配置页参考 seedclean 风格
- [ ] 单测全绿（90+项）
- [ ] npm build 成功
- [ ] pyflakes 无错

