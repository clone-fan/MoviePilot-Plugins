# AgentOpsAssistant v0.0.8 更新日志

## 版本信息
- **版本号**: 0.0.8
- **发布日期**: 2024-06-14
- **更新内容**: 7项重大修复与功能增强

---

## 🔧 修复项

### 1. 版本显示优化（13.8 vs 13.8-1）
**问题**: 用户反馈前端版本 13.8 与后端版本 13.8-1 显示不一致导致困惑

**解决方案**: 
- 在 `_frontend_backend_version_line()` 方法中添加注释说明
- 前端版本（FRONTEND_VERSION）和后端版本（APP_VERSION）可以有不同的构建号后缀
- 这是 MoviePilot 的正常行为，后端可能有 `-1` 等构建号，前端保持纯版本号

**文件**: `__init__.py` 第 608-615 行

---

### 2. 站点过期状态显示优化
**问题**: "过期" 一词不够清晰，用户不清楚是站点本身过期还是数据过期

**解决方案**:
- 将显示文本从 "过期 X" 改为 "数据过期 X"
- 明确指出是站点快照数据不是今日的，而非站点本身过期

**文件**: `__init__.py` 第 742-768 行

**变更**:
```python
# 修改前
items = [f"⦁ 今日快照：正常 {normal}｜过期 {stale}｜异常 {len(errors)}"]

# 修改后  
items = [f"⦁ 今日快照：正常 {normal}｜数据过期 {stale}｜异常 {len(errors)}"]
```

---

### 3. 存储空间显示重构 ⭐
**问题**: 
- 仅显示硬编码路径 `/downloads`, `/media`, `/config`
- 无法区分存储类型（本地 vs 115 vs rclone vs alipan）
- 不读取 MoviePilot 实际配置的目录

**解决方案**:
- 优先读取 MoviePilot 配置的下载目录和媒体库目录（通过 `DirectoryHelper`）
- 从 `TransferDirectoryConf` 读取 `storage`、`library_storage` 字段
- 通过 `SystemConfigKey.Storages` 获取存储配置，映射存储名称到类型（local/u115/alipan/rclone/alist）
- 对本地存储显示剩余空间和使用百分比
- 对网络存储类型显示"已配置"状态
- 回退机制：如果无配置则检查硬编码路径

**文件**: `__init__.py` 第 806-854 行

**新增方法**:
- `_get_storage_health_locked()`: 主逻辑重构
- `_add_storage_item()`: 添加存储项到列表

**显示示例**:
```
⦁ 下载目录（local）：剩余 500 GB｜已用 45%
⦁ 媒体库（u115）：已配置
⦁ 媒体库（rclone）：已配置
```

---

### 4. 下载器多实例显示 ⭐
**问题**: 
- 当配置多个下载器时，仅聚合显示总任务数和总速度
- 无法区分各下载器的状态

**解决方案**:
- 通过 `DownloaderHelper` 获取所有配置的下载器服务
- 按下载器名称分组统计正在下载的种子
- 每个下载器独立显示任务数和上传/下载速度
- 支持 qBittorrent、Transmission 等多下载器场景

**文件**: `__init__.py` 第 770-804 行

**显示示例**:
```
⦁ qBittorrent：3 个任务｜↓ 5.2 MB/s ↑ 1.8 MB/s
⦁ Transmission：1 个任务｜↓ 1.1 MB/s ↑ 0.5 MB/s
```

---

### 5. WebDAV 远端备份功能实现 ⭐⭐⭐
**问题**: 
- 配置存在但从未实现上传逻辑
- `_create_agentops_backup()` 仅做本地备份

**解决方案**:
- 新增 `_upload_to_webdav()` 方法实现 WebDAV 上传
- 使用 `webdav3-client` 库
- 支持 Basic 和 Digest 认证
- 支持跳过证书校验（自签名证书场景）
- 自动清理远端旧备份（保留 `backup_webdav_max_count` 份）
- 可选的上传结果通知
- 本地备份完成后自动触发 WebDAV 上传

**文件**: `__init__.py` 第 1109-1210 行

**新增方法**:
- `_upload_to_webdav(local_zip_path: str) -> Tuple[bool, str]`

**配置项**:
- `backup_webdav_enabled`: 启用 WebDAV 备份
- `backup_webdav_hostname`: WebDAV 服务器地址
- `backup_webdav_login`: 账号
- `backup_webdav_password`: 密码
- `backup_webdav_max_count`: 远端保留份数
- `backup_webdav_notify`: 上传结果通知
- `backup_webdav_digest_auth`: 使用 Digest 认证
- `backup_webdav_disable_check`: 跳过证书校验

**依赖**: 需要安装 `webdav3-client`
```bash
pip install webdav3-client
```

---

### 6. 仪表盘手动触发按钮 ⭐
**问题**: 
- 仪表盘（Page.vue）仅展示状态，无操作入口
- 用户需要切换到设置页才能手动触发任务

**解决方案**:
- 在仪表盘底部新增"手动触发"卡片
- 提供 4 个快捷操作按钮：
  - 发送每日汇报
  - 健康巡查
  - 立即备份
  - 清理日志
- 按钮带 loading 状态和结果提示
- 操作完成后自动刷新仪表盘数据

**文件**: 
- `src/components/Page.vue` (Script 部分第 1-68 行)
- `src/components/Page.vue` (Template 部分第 147-178 行)

**新增功能**:
- `runAction(path, label)` 方法：调用 API 并显示结果
- `actionRunning`、`actionMessage` 响应式变量：UI 状态管理

---

### 7. 健康巡查修复 ⭐
**问题**: 
- 尝试从 `app.core.downloader` 导入 `Downloader` 类（v2 中不存在）
- 健康巡查结果未保存到 `last_health_check`

**解决方案**:
- 改用 v2 正确的导入：`from app.helper.downloader import DownloaderHelper`
- 使用 `DownloaderHelper().get_services()` 获取下载器列表
- 在 `_build_health_summary()` 中直接保存结果到 `last_health_check`
- 确保仪表盘能正确读取健康巡查数据

**文件**: `__init__.py` 第 1597-1638 行

**检查项**:
1. 订阅数量
2. 站点总数和启用数
3. 下载器在线数
4. 本插件调度任务数

---

## 📦 前端构建

已重新构建 Vue 前端组件：
```bash
npm run build
```

构建产物位于 `dist/assets/` 目录。

---

## 🔍 测试建议

### 手动测试清单

1. **版本显示**
   - 查看每日汇报中的版本行，确认显示格式正确

2. **站点状态**
   - 检查站点快照报告，确认"数据过期"描述清晰

3. **存储空间**
   - 配置多种存储类型（本地、115、rclone）
   - 触发每日汇报，确认存储类型正确标注

4. **多下载器**
   - 配置 2 个以上下载器
   - 添加下载任务到不同下载器
   - 触发每日汇报，确认按下载器分组显示

5. **WebDAV 备份**
   - 配置 WebDAV 参数
   - 启用 WebDAV 备份
   - 手动触发备份，检查本地和远端备份
   - 验证旧备份清理逻辑

6. **仪表盘手动触发**
   - 打开仪表盘（详情页）
   - 点击各手动触发按钮
   - 确认操作成功并显示结果

7. **健康巡查**
   - 手动触发健康巡查
   - 查看仪表盘健康巡查卡片，确认结果显示
   - 检查插件数据文件 `last_health_check`

---

## 📝 已知限制

1. **网络存储空间显示**: 
   - 115/alipan/rclone 等网络存储暂时仅显示"已配置"
   - 未来版本可通过 `StorageChain` 获取实际空间信息

2. **WebDAV 依赖**:
   - 需要手动安装 `webdav3-client`
   - 首次使用前需确保依赖已安装

3. **下载器速度精度**:
   - 依赖 MoviePilot 的 `DownloadingTorrent` 返回的速度字段
   - 不同下载器类型速度字段名可能不同（已兼容 `dlspeed` 和 `upspeed`）

---

## 🚀 升级方式

1. 替换 `__init__.py` 文件
2. 替换 `src/components/Page.vue` 文件
3. 重新构建前端（或直接替换 `dist/assets/` 目录）
4. 重启 MoviePilot
5. 如需 WebDAV 备份，安装依赖：
   ```bash
   pip install webdav3-client
   ```

---

## 💬 反馈

如有问题或建议，请反馈至：
- GitHub Issues: https://github.com/clone-fan/MoviePilot-Plugins/issues
- 作者: wenking

---

**感谢使用 MP 运维助手！**
