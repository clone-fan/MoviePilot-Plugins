// Current-only configuration field contract. Legacy fields are intentionally absent.


const currentConfigSchemaFields = [
{
    "key": "backup_cron",
    "type": "string",
    "dataType": "string",
    "cardType": "cron",
    "module": "backup",
    "subtab": "backup",
    "label": "备份时间",
    "help": "",
    "control": "cron",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": false,
      "remoteConfig": true
    }
  },
{
    "key": "backup_enabled",
    "type": "boolean",
    "dataType": "boolean",
    "cardType": "feature",
    "module": "backup",
    "subtab": "backup",
    "label": "启用开关",
    "help": "",
    "control": "switch",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "backup_keep_count",
    "type": "number",
    "dataType": "number",
    "cardType": "feature",
    "module": "backup",
    "subtab": "backup",
    "label": "保留份数",
    "help": "",
    "control": "number",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "backup_path",
    "type": "string",
    "dataType": "string",
    "cardType": "feature",
    "module": "backup",
    "subtab": "backup",
    "label": "备份目录",
    "help": "",
    "control": "text",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "backup_notify",
    "type": "boolean",
    "dataType": "boolean",
    "cardType": "notify",
    "module": "backup",
    "subtab": "backup",
    "label": "定时执行后通知",
    "help": "只通知 Cron 执行结果，手动备份不发送。",
    "control": "switch",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "backup_notify_type",
    "type": "string",
    "dataType": "string",
    "cardType": "notify",
    "module": "backup",
    "subtab": "backup",
    "label": "通知渠道",
    "help": "融合通知启用时只接管此渠道。",
    "control": "select",
    "itemSource": "notificationTypeItems",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": false,
      "remoteConfig": true
    }
  },
{
    "key": "backup_webdav_digest_auth",
    "type": "boolean",
    "dataType": "boolean",
    "cardType": "feature",
    "module": "backup_webdav",
    "subtab": "backup",
    "label": "摘要认证",
    "help": "",
    "control": "switch",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "backup_webdav_disable_check",
    "type": "boolean",
    "dataType": "boolean",
    "cardType": "feature",
    "module": "backup_webdav",
    "subtab": "backup",
    "label": "跳过连通检查",
    "help": "",
    "control": "switch",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "backup_webdav_hostname",
    "type": "string",
    "dataType": "string",
    "cardType": "feature",
    "module": "backup_webdav",
    "subtab": "backup",
    "label": "服务地址",
    "help": "",
    "control": "text",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "backup_webdav_login",
    "type": "string",
    "dataType": "string",
    "cardType": "feature",
    "module": "backup_webdav",
    "subtab": "backup",
    "label": "登录账号",
    "help": "",
    "control": "text",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "backup_webdav_max_count",
    "type": "number",
    "dataType": "number",
    "cardType": "feature",
    "module": "backup_webdav",
    "subtab": "backup",
    "label": "远端保留份数",
    "help": "",
    "control": "number",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "backup_webdav_password",
    "type": "string",
    "dataType": "string",
    "cardType": "feature",
    "module": "backup_webdav",
    "subtab": "backup",
    "label": "登录密码",
    "help": "",
    "control": "text",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "dltag_downloaders",
    "type": "array",
    "dataType": "array",
    "cardType": "feature",
    "module": "downloader_tag",
    "subtab": "dltagmain",
    "label": "下载器范围",
    "help": "",
    "control": "select",
    "itemSource": "downloaderOptions",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "dltag_enabled",
    "type": "boolean",
    "dataType": "boolean",
    "cardType": "feature",
    "module": "downloader_tag",
    "subtab": "dltagmain",
    "label": "启用开关",
    "help": "",
    "control": "switch",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "dltag_notify_type",
    "type": "string",
    "dataType": "string",
    "cardType": "notify",
    "module": "downloader_tag",
    "subtab": "dltagmain",
    "label": "通知类型",
    "help": "",
    "control": "select",
    "itemSource": "notificationTypeItems",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": false,
      "remoteConfig": true
    }
  },
{
    "key": "dltag_prefix",
    "type": "string",
    "dataType": "string",
    "cardType": "feature",
    "module": "downloader_tag",
    "subtab": "dltagmain",
    "label": "标签前缀",
    "help": "",
    "control": "text",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "enabled",
    "type": "boolean",
    "dataType": "boolean",
    "cardType": "generic",
    "module": "plugin",
    "subtab": "clean",
    "label": "启用开关",
    "help": "",
    "control": "switch",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "fusion_notify_enabled",
    "type": "boolean",
    "dataType": "boolean",
    "cardType": "notify",
    "module": "fusion_notify",
    "subtab": "fusion",
    "label": "启用融合卡",
    "help": "",
    "control": "switch",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "health_check_cron",
    "type": "string",
    "dataType": "string",
    "cardType": "cron",
    "module": "health_check",
    "subtab": "hc",
    "label": "巡查时间",
    "help": "",
    "control": "cron",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": false,
      "remoteConfig": true
    }
  },
{
    "key": "health_check_database_targets",
    "type": "array",
    "dataType": "array",
    "cardType": "feature",
    "module": "health_check",
    "subtab": "hc",
    "label": "数据库项目",
    "help": "",
    "control": "select",
    "itemSource": "healthDatabaseTargets",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "health_check_directory_targets",
    "type": "array",
    "dataType": "array",
    "cardType": "feature",
    "module": "health_check",
    "subtab": "hc",
    "label": "目录项目",
    "help": "",
    "control": "select",
    "itemSource": "healthDirectoryTargets",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "health_check_enabled",
    "type": "boolean",
    "dataType": "boolean",
    "cardType": "feature",
    "module": "health_check",
    "subtab": "hc",
    "label": "启用开关",
    "help": "",
    "control": "switch",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "health_check_items",
    "type": "array",
    "dataType": "array",
    "cardType": "feature",
    "module": "health_check",
    "subtab": "hc",
    "label": "巡查项目",
    "help": "",
    "control": "select",
    "itemSource": "healthCheckItems",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "health_check_notify_type",
    "type": "string",
    "dataType": "string",
    "cardType": "notify",
    "module": "health_check",
    "subtab": "hc",
    "label": "通知类型",
    "help": "",
    "control": "select",
    "itemSource": "notificationTypeItems",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": false,
      "remoteConfig": true
    }
  },
{
    "key": "health_check_schedule_enabled",
    "type": "boolean",
    "dataType": "boolean",
    "cardType": "cron",
    "module": "health_check",
    "subtab": "hc",
    "label": "启用定时任务",
    "help": "",
    "control": "switch",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": false,
      "vueUses": false,
      "remoteConfig": true
    }
  },
{
    "key": "health_check_storage_targets",
    "type": "array",
    "dataType": "array",
    "cardType": "feature",
    "module": "health_check",
    "subtab": "hc",
    "label": "存储项目",
    "help": "",
    "control": "select",
    "itemSource": "healthStorageTargets",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "health_check_storage_threshold",
    "type": "number",
    "dataType": "number",
    "cardType": "feature",
    "module": "health_check",
    "subtab": "hc",
    "label": "存储阈值",
    "help": "",
    "control": "number",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "local_plugin_repo",
    "type": "unknown",
    "dataType": "unknown",
    "cardType": "runtime",
    "module": "plugin",
    "subtab": "clean",
    "label": "本地插件仓库",
    "help": "",
    "control": "text",
    "itemSource": "",
    "defaultSource": "none",
    "defaultSources": [],
    "isDisplayed": false,
    "displayPolicy": "runtime",
    "displayReason": "backend-only source cleanup safety setting; never synthesize in the configuration center",
    "sources": [
      "backend_config_read"
    ],
    "sourceFlags": {
      "frontendDefaults": false,
      "backendDefaults": false,
      "backendReads": true,
      "vueUses": false,
      "remoteConfig": false
    }
  },
{
    "key": "log_clean_cron",
    "type": "string",
    "dataType": "string",
    "cardType": "cron",
    "module": "log_clean",
    "subtab": "logs",
    "label": "清理时间",
    "help": "",
    "control": "cron",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": false,
      "remoteConfig": true
    }
  },
{
    "key": "log_clean_enabled",
    "type": "boolean",
    "dataType": "boolean",
    "cardType": "feature",
    "module": "log_clean",
    "subtab": "logs",
    "label": "启用开关",
    "help": "",
    "control": "switch",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "log_clean_notify",
    "type": "boolean",
    "dataType": "boolean",
    "cardType": "notify",
    "module": "log_clean",
    "subtab": "logs",
    "label": "定时执行后通知",
    "help": "只通知 Cron 执行结果，手动清理不发送。",
    "control": "switch",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "log_clean_notify_type",
    "type": "string",
    "dataType": "string",
    "cardType": "notify",
    "module": "log_clean",
    "subtab": "logs",
    "label": "通知渠道",
    "help": "融合通知启用时只接管此渠道。",
    "control": "select",
    "itemSource": "notificationTypeItems",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": false,
      "remoteConfig": true
    }
  },
{
    "key": "log_clean_rows",
    "type": "number",
    "dataType": "number",
    "cardType": "feature",
    "module": "log_clean",
    "subtab": "logs",
    "label": "保留行数",
    "help": "",
    "control": "number",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "log_clean_schedule_enabled",
    "type": "boolean",
    "dataType": "boolean",
    "cardType": "cron",
    "module": "log_clean",
    "subtab": "logs",
    "label": "启用定时任务",
    "help": "",
    "control": "switch",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": false,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "log_clean_selected_ids",
    "type": "array",
    "dataType": "array",
    "cardType": "feature",
    "module": "log_clean",
    "subtab": "logs",
    "label": "目标日志",
    "help": "",
    "control": "select",
    "itemSource": "installedPlugins",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "market_update_enabled",
    "type": "boolean",
    "dataType": "boolean",
    "cardType": "feature",
    "module": "market_update",
    "subtab": "updates",
    "label": "启用开关",
    "help": "",
    "control": "switch",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "market_update_exclude_ids",
    "type": "array",
    "dataType": "array",
    "cardType": "feature",
    "module": "market_update",
    "subtab": "updates",
    "label": "忽略插件",
    "help": "",
    "control": "select",
    "itemSource": "installedPlugins",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "market_update_install_ids",
    "type": "array",
    "dataType": "array",
    "cardType": "feature",
    "module": "market_update",
    "subtab": "updates",
    "label": "自动安装插件",
    "help": "",
    "control": "select",
    "itemSource": "installedPlugins",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "market_update_schedule_enabled",
    "type": "boolean",
    "dataType": "boolean",
    "cardType": "cron",
    "module": "market_update",
    "subtab": "updates",
    "label": "启用定时任务",
    "help": "",
    "control": "switch",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": false,
      "vueUses": false,
      "remoteConfig": true
    }
  },
{
    "key": "mp_update_cron",
    "type": "string",
    "dataType": "string",
    "cardType": "cron",
    "module": "mp_update",
    "subtab": "updates",
    "label": "系统检查时间",
    "help": "",
    "control": "cron",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": false,
      "remoteConfig": true
    }
  },
{
    "key": "mp_update_enabled",
    "type": "boolean",
    "dataType": "boolean",
    "cardType": "feature",
    "module": "mp_update",
    "subtab": "updates",
    "label": "启用开关",
    "help": "",
    "control": "switch",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "mp_update_schedule_enabled",
    "type": "boolean",
    "dataType": "boolean",
    "cardType": "cron",
    "module": "mp_update",
    "subtab": "updates",
    "label": "启用定时任务",
    "help": "",
    "control": "switch",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": false,
      "vueUses": false,
      "remoteConfig": true
    }
  },
{
    "key": "mp_update_types",
    "type": "array",
    "dataType": "array",
    "cardType": "feature",
    "module": "mp_update",
    "subtab": "updates",
    "label": "检查范围",
    "help": "",
    "control": "select",
    "itemSource": "mpUpdateTypes",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "msgnotify_enabled",
    "type": "boolean",
    "dataType": "boolean",
    "cardType": "notify",
    "module": "media_notify",
    "subtab": "server",
    "label": "启用开关",
    "help": "",
    "control": "switch",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "msgnotify_notify_type",
    "type": "string",
    "dataType": "string",
    "cardType": "notify",
    "module": "media_notify",
    "subtab": "server",
    "label": "通知类型",
    "help": "",
    "control": "select",
    "itemSource": "notificationTypeItems",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": false,
      "remoteConfig": true
    }
  },
{
    "key": "msgnotify_servers",
    "type": "array",
    "dataType": "array",
    "cardType": "notify",
    "module": "media_notify",
    "subtab": "server",
    "label": "通知服务器",
    "help": "",
    "control": "select",
    "itemSource": "mediaserverOptions",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "msgnotify_types",
    "type": "array",
    "dataType": "array",
    "cardType": "notify",
    "module": "media_notify",
    "subtab": "server",
    "label": "通知事件",
    "help": "",
    "control": "select",
    "itemSource": "msgGroupItems",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "plugin_uninstall_clear_config",
    "type": "boolean",
    "dataType": "boolean",
    "cardType": "feature",
    "module": "plugin_uninstall",
    "subtab": "clean",
    "label": "清理配置",
    "help": "",
    "control": "switch",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "plugin_uninstall_clear_data",
    "type": "boolean",
    "dataType": "boolean",
    "cardType": "feature",
    "module": "plugin_uninstall",
    "subtab": "clean",
    "label": "清理数据",
    "help": "",
    "control": "switch",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "plugin_uninstall_delete_source",
    "type": "boolean",
    "dataType": "boolean",
    "cardType": "feature",
    "module": "plugin_uninstall",
    "subtab": "clean",
    "label": "删除源码目录",
    "help": "",
    "control": "switch",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "plugin_uninstall_ids",
    "type": "array",
    "dataType": "array",
    "cardType": "feature",
    "module": "plugin_uninstall",
    "subtab": "clean",
    "label": "目标插件",
    "help": "",
    "control": "select",
    "itemSource": "installedPlugins",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "plugin_uninstall_remove_plugin",
    "type": "boolean",
    "dataType": "boolean",
    "cardType": "feature",
    "module": "plugin_uninstall",
    "subtab": "clean",
    "label": "移除插件本体",
    "help": "",
    "control": "switch",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "seedclean_action",
    "type": "string",
    "dataType": "string",
    "cardType": "feature",
    "module": "seedclean",
    "subtab": "seedremove",
    "label": "处理动作",
    "help": "",
    "control": "select",
    "itemSource": "seedActionsItems",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "seedclean_cron",
    "type": "string",
    "dataType": "string",
    "cardType": "cron",
    "module": "seedclean",
    "subtab": "seedremove",
    "label": "执行时间",
    "help": "",
    "control": "cron",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": false,
      "remoteConfig": true
    }
  },
{
    "key": "seedclean_downloaders",
    "type": "array",
    "dataType": "array",
    "cardType": "feature",
    "module": "seedclean",
    "subtab": "seedremove",
    "label": "下载器范围",
    "help": "",
    "control": "select",
    "itemSource": "downloaderOptions",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "seedclean_enabled",
    "type": "boolean",
    "dataType": "boolean",
    "cardType": "feature",
    "module": "seedclean",
    "subtab": "seedremove",
    "label": "启用开关",
    "help": "",
    "control": "switch",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "seedclean_errorkeywords",
    "type": "string",
    "dataType": "string",
    "cardType": "feature",
    "module": "seedclean",
    "subtab": "seedremove",
    "label": "错误关键词",
    "help": "",
    "control": "text",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "seedclean_labels",
    "type": "string",
    "dataType": "string",
    "cardType": "feature",
    "module": "seedclean",
    "subtab": "seedremove",
    "label": "标签关键词",
    "help": "",
    "control": "text",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "seedclean_mponly",
    "type": "boolean",
    "dataType": "boolean",
    "cardType": "feature",
    "module": "seedclean",
    "subtab": "seedremove",
    "label": "仅处理站内任务",
    "help": "",
    "control": "switch",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "seedclean_notify",
    "type": "boolean",
    "dataType": "boolean",
    "cardType": "notify",
    "module": "seedclean",
    "subtab": "seedremove",
    "label": "结果通知",
    "help": "",
    "control": "switch",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": false,
      "remoteConfig": true
    }
  },
{
    "key": "seedclean_notify_type",
    "type": "string",
    "dataType": "string",
    "cardType": "notify",
    "module": "seedclean",
    "subtab": "seedremove",
    "label": "通知类型",
    "help": "",
    "control": "select",
    "itemSource": "notificationTypeItems",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": false,
      "remoteConfig": true
    }
  },
{
    "key": "seedclean_pathkeywords",
    "type": "string",
    "dataType": "string",
    "cardType": "feature",
    "module": "seedclean",
    "subtab": "seedremove",
    "label": "路径关键词",
    "help": "",
    "control": "text",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "seedclean_ratio",
    "type": "string",
    "dataType": "string",
    "cardType": "feature",
    "module": "seedclean",
    "subtab": "seedremove",
    "label": "分享率阈值",
    "help": "",
    "control": "text",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "seedclean_samedata",
    "type": "boolean",
    "dataType": "boolean",
    "cardType": "feature",
    "module": "seedclean",
    "subtab": "seedremove",
    "label": "同体积判定",
    "help": "",
    "control": "switch",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "seedclean_schedule_enabled",
    "type": "boolean",
    "dataType": "boolean",
    "cardType": "cron",
    "module": "seedclean",
    "subtab": "seedremove",
    "label": "启用定时任务",
    "help": "",
    "control": "switch",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": false,
      "vueUses": false,
      "remoteConfig": true
    }
  },
{
    "key": "seedclean_size",
    "type": "string",
    "dataType": "string",
    "cardType": "feature",
    "module": "seedclean",
    "subtab": "seedremove",
    "label": "体积阈值",
    "help": "",
    "control": "text",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "seedclean_time",
    "type": "string",
    "dataType": "string",
    "cardType": "feature",
    "module": "seedclean",
    "subtab": "seedremove",
    "label": "时间条件",
    "help": "",
    "control": "text",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "seedclean_torrentcategorys",
    "type": "string",
    "dataType": "string",
    "cardType": "feature",
    "module": "seedclean",
    "subtab": "seedremove",
    "label": "种子分类",
    "help": "",
    "control": "text",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "seedclean_torrentstates",
    "type": "string",
    "dataType": "string",
    "cardType": "feature",
    "module": "seedclean",
    "subtab": "seedremove",
    "label": "种子状态",
    "help": "",
    "control": "text",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "seedclean_trtorrentstates",
    "type": "string",
    "dataType": "string",
    "cardType": "feature",
    "module": "seedclean",
    "subtab": "seedremove",
    "label": "任务状态（TR）",
    "help": "Transmission 状态可填数字或英文状态，多个用英文逗号分隔。",
    "control": "text",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "seedclean_trackerkeywords",
    "type": "string",
    "dataType": "string",
    "cardType": "feature",
    "module": "seedclean",
    "subtab": "seedremove",
    "label": "站点来源关键词",
    "help": "",
    "control": "text",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "seedclean_upspeed",
    "type": "string",
    "dataType": "string",
    "cardType": "feature",
    "module": "seedclean",
    "subtab": "seedremove",
    "label": "上传速度阈值",
    "help": "",
    "control": "text",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "site_stat_dashboard_type",
    "type": "string",
    "dataType": "string",
    "cardType": "feature",
    "module": "site_stat",
    "subtab": "sites",
    "label": "仪表盘口径",
    "help": "",
    "control": "select",
    "itemSource": "siteStatRangeItems",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "site_stat_enabled",
    "type": "boolean",
    "dataType": "boolean",
    "cardType": "feature",
    "module": "site_stat",
    "subtab": "sites",
    "label": "启用开关",
    "help": "",
    "control": "switch",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "site_stat_schedule_enabled",
    "type": "boolean",
    "dataType": "boolean",
    "cardType": "cron",
    "module": "site_stat",
    "subtab": "sites",
    "label": "??????",
    "help": "",
    "control": "switch",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": false
    }
  },
{
    "key": "site_stat_cron",
    "type": "string",
    "dataType": "string",
    "cardType": "cron",
    "module": "site_stat",
    "subtab": "sites",
    "label": "统计时间",
    "help": "???????????????????? 08:00?",
    "control": "cron",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": false
    }
  },
{
    "key": "site_stat_notify_type",
    "type": "string",
    "dataType": "string",
    "cardType": "notify",
    "module": "site_stat",
    "subtab": "sites",
    "label": "通知类型",
    "help": "融合通知关闭时，定时统计结果通过此 MoviePilot 通知类型发送。",
    "control": "select",
    "itemSource": "notificationTypeItems",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": false,
      "remoteConfig": true
    }
  },
{
    "key": "subfill_category_confs",
    "type": "string",
    "dataType": "string",
    "cardType": "feature",
    "module": "subfill",
    "subtab": "subfill",
    "label": "规则配置",
    "help": "",
    "control": "text",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "subfill_category_enabled",
    "type": "boolean",
    "dataType": "boolean",
    "cardType": "feature",
    "module": "subfill",
    "subtab": "subfill",
    "label": "启用规则填充",
    "help": "",
    "control": "switch",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "subfill_details",
    "type": "array",
    "dataType": "array",
    "cardType": "feature",
    "module": "subfill",
    "subtab": "subfill",
    "label": "填充明细",
    "help": "",
    "control": "select",
    "itemSource": "subfillDetailItems",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "subfill_enabled",
    "type": "boolean",
    "dataType": "boolean",
    "cardType": "feature",
    "module": "subfill",
    "subtab": "subfill",
    "label": "启用开关",
    "help": "",
    "control": "switch",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "subscribe_reminder_cron",
    "type": "string",
    "dataType": "string",
    "cardType": "cron",
    "module": "subscribe_reminder",
    "subtab": "subscribe",
    "label": "检查时间",
    "help": "",
    "control": "cron",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": false,
      "remoteConfig": true
    }
  },
{
    "key": "subscribe_reminder_enabled",
    "type": "boolean",
    "dataType": "boolean",
    "cardType": "feature",
    "module": "subscribe_reminder",
    "subtab": "subscribe",
    "label": "启用开关",
    "help": "",
    "control": "switch",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "subscribe_reminder_msgtype",
    "type": "string",
    "dataType": "string",
    "cardType": "notify",
    "module": "subscribe_reminder",
    "subtab": "subscribe",
    "label": "消息类型",
    "help": "",
    "control": "select",
    "itemSource": "messageTypeItems",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": false,
      "remoteConfig": true
    }
  },
{
    "key": "subscribe_reminder_schedule_enabled",
    "type": "boolean",
    "dataType": "boolean",
    "cardType": "cron",
    "module": "subscribe_reminder",
    "subtab": "subscribe",
    "label": "启用定时任务",
    "help": "",
    "control": "switch",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": false,
      "vueUses": false,
      "remoteConfig": true
    }
  },
{
    "key": "subscribe_reminder_subtype",
    "type": "array",
    "dataType": "array",
    "cardType": "feature",
    "module": "subscribe_reminder",
    "subtab": "subscribe",
    "label": "订阅类型",
    "help": "",
    "control": "select",
    "itemSource": "subscribeSubtypeItems",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "dltag_all_tags",
    "type": "array",
    "dataType": "array",
    "cardType": "feature",
    "module": "downloader_tag",
    "subtab": "dltagmain",
    "label": "全量标签",
    "help": "这些标签会补到每个未命中排除条件的目标种子。",
    "control": "combobox",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "dltag_excluded_tags",
    "type": "array",
    "dataType": "array",
    "cardType": "feature",
    "module": "downloader_tag",
    "subtab": "dltagmain",
    "label": "排除标签",
    "help": "已有任一排除标签的种子跳过，不会追加站点或全量标签。",
    "control": "combobox",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "dltag_tracker_mappings",
    "type": "string",
    "dataType": "string",
    "cardType": "feature",
    "module": "downloader_tag",
    "subtab": "dltagmain",
    "label": "Tracker 映射",
    "help": "每行一个规则：Tracker 正则或关键字 => 标签。无效行会被忽略。",
    "control": "textarea",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config,remote_mp_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config",
      "remote_mp_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use",
      "remote_mp_config"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": true
    }
  },
{
    "key": "fusion_card_create_cron",
    "type": "string",
    "dataType": "string",
    "cardType": "cron",
    "module": "fusion_notify",
    "subtab": "fusion",
    "label": "建卡时间",
    "help": "按标准五段 Cron 建立或切换融合卡，默认每天 00:05。",
    "control": "cron",
    "inputType": "",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": false
    }
  },
{
    "key": "fusion_card_refresh_cron",
    "type": "string",
    "dataType": "string",
    "cardType": "cron",
    "module": "fusion_notify",
    "subtab": "fusion",
    "label": "刷新时间",
    "help": "按 Cron 周期刷新当前活动卡，默认每小时一次。",
    "control": "cron",
    "inputType": "",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": false
    }
  },
{
    "key": "market_update_cron",
    "type": "string",
    "dataType": "string",
    "cardType": "cron",
    "module": "market_update",
    "subtab": "updates",
    "label": "插件库检查时间",
    "help": "按 Cron 定时检查插件库。",
    "control": "cron",
    "inputType": "",
    "itemSource": "",
    "defaultSource": "frontend_defaults,backend_default_config",
    "defaultSources": [
      "frontend_defaults",
      "backend_default_config"
    ],
    "isDisplayed": true,
    "displayPolicy": "display",
    "displayReason": "",
    "sources": [
      "frontend_defaults",
      "backend_default_config",
      "backend_config_read",
      "vue_form_use"
    ],
    "sourceFlags": {
      "frontendDefaults": true,
      "backendDefaults": true,
      "backendReads": true,
      "vueUses": true,
      "remoteConfig": false
    }
  }
];

const downloaderHelperSchemaFields = [
  { "key": "dltag_enabled", "type": "boolean", "dataType": "boolean", "cardType": "feature", "module": "downloader_tag", "subtab": "dltagmain", "label": "启用下载器助手", "help": "", "control": "switch", "itemSource": "", "isDisplayed": true },
  { "key": "dltag_downloaders", "type": "array", "dataType": "array", "cardType": "feature", "module": "downloader_tag", "subtab": "dltagmain", "label": "下载器", "help": "", "control": "select", "itemSource": "downloaderOptions", "isDisplayed": true },
  { "key": "dltag_tasks", "type": "array", "dataType": "array", "cardType": "feature", "module": "downloader_tag", "subtab": "dltagmain", "label": "执行任务", "help": "", "control": "select", "itemSource": "dltagTaskItems", "isDisplayed": true },
  { "key": "dltag_cron", "type": "string", "dataType": "string", "cardType": "feature", "module": "downloader_tag", "subtab": "dltagmain", "label": "执行时间", "help": "", "control": "cron", "itemSource": "", "retainInCard": true, "isDisplayed": true },
  { "key": "dltag_listen_download", "type": "boolean", "dataType": "boolean", "cardType": "feature", "module": "downloader_tag", "subtab": "dltagmain", "label": "监听新增下载", "help": "新增任务时只执行标签和恢复做种，不会删种。", "control": "switch", "itemSource": "", "isDisplayed": true },
  { "key": "dltag_listen_source_file", "type": "boolean", "dataType": "boolean", "cardType": "feature", "module": "downloader_tag", "subtab": "dltagmain", "label": "监听源文件删除", "help": "源文件被删除后按路径匹配并清理下载任务。", "control": "switch", "itemSource": "", "isDisplayed": true },
  { "key": "dltag_prefix", "type": "string", "dataType": "string", "cardType": "feature", "module": "downloader_tag", "subtab": "dltagmain", "label": "站点标签前缀", "help": "留空表示不添加前缀。", "control": "text", "itemSource": "", "isDisplayed": true },
  { "key": "dltag_all_tags", "type": "array", "dataType": "array", "cardType": "feature", "module": "downloader_tag", "subtab": "dltagmain", "label": "固定标签", "help": "为每个目标任务补充这些标签。", "control": "combobox", "itemSource": "", "isDisplayed": true },
  { "key": "dltag_excluded_tags", "type": "array", "dataType": "array", "cardType": "feature", "module": "downloader_tag", "subtab": "dltagmain", "label": "保护标签", "help": "带有保护标签的任务不会被恢复做种或清理，标签仍会正常修正。", "control": "combobox", "itemSource": "", "isDisplayed": true },
  { "key": "dltag_not_select_all_tag", "type": "string", "dataType": "string", "cardType": "feature", "module": "downloader_tag", "subtab": "dltagmain", "label": "未全选标签", "help": "任务未选择全部文件时使用的标签。", "control": "text", "itemSource": "", "isDisplayed": true },
  { "key": "dltag_tracker_mappings", "type": "string", "dataType": "string", "cardType": "feature", "module": "downloader_tag", "subtab": "dltagmain", "label": "Tracker 映射", "help": "", "control": "textarea", "itemSource": "", "isDisplayed": true },
  { "key": "dltag_source_delete_strategy", "type": "string", "dataType": "string", "cardType": "feature", "module": "downloader_tag", "subtab": "dltagmain", "label": "源文件清理时机", "help": "提前清理只删除下载任务，不删除数据文件。", "control": "select", "itemSource": "dltagDeleteStrategyItems", "isDisplayed": true },
  { "key": "dltag_scheduled_notify", "type": "boolean", "dataType": "boolean", "cardType": "notify", "module": "downloader_tag", "subtab": "dltagmain", "label": "定时执行后通知", "help": "只通知 Cron 执行结果，手动和事件执行不发送。", "control": "switch", "itemSource": "", "isDisplayed": true },
  { "key": "dltag_notify_type", "type": "string", "dataType": "string", "cardType": "notify", "module": "downloader_tag", "subtab": "dltagmain", "label": "通知渠道", "help": "融合通知启用时只接管此渠道。", "control": "select", "itemSource": "notificationTypeItems", "isDisplayed": true },
];

const hiddenBackupConfigKeys = new Set(['backup_webdav_digest_auth', 'backup_webdav_disable_check']);
const updateSchemaFields = [
  { "key": "market_update_strategy", "type": "string", "dataType": "string", "cardType": "feature", "module": "market_update", "subtab": "updates", "label": "自动处理方式", "help": "仅检查不会修改配置；同步插件库会保存最新插件库地址；同步并更新插件还会更新符合范围的已安装插件。", "control": "select", "itemSource": "marketUpdateStrategies", "isDisplayed": true },
  { "key": "update_scheduled_notify", "type": "boolean", "dataType": "boolean", "cardType": "notify", "module": "updates", "subtab": "updates", "label": "定时执行后通知", "help": "只通知 Cron 执行结果，手动执行不发送。", "control": "switch", "itemSource": "", "isDisplayed": true },
  { "key": "update_notify_type", "type": "string", "dataType": "string", "cardType": "notify", "module": "updates", "subtab": "updates", "label": "通知渠道", "help": "系统更新和插件库更新共用此渠道；融合通知启用时只接管此字段。", "control": "select", "itemSource": "notificationTypeItems", "isDisplayed": true },
];

const configSchemaFields = Object.freeze([
  ...currentConfigSchemaFields
    .filter(field => !field.key.startsWith('dltag_'))
    .map(field => hiddenBackupConfigKeys.has(field.key) ? { ...field, isDisplayed: false } : field),
  ...updateSchemaFields,
  ...downloaderHelperSchemaFields,
]);

Object.freeze(
  Object.fromEntries(configSchemaFields.map(field => [field.key, field])),
);

const DEFAULT_FUSION_CARD_REFRESH_CRON = '0 * * * *';
const DEFAULT_FUSION_CARD_CREATE_CRON = '5 0 * * *';
const cronRanges = [[0, 59], [0, 23], [1, 31], [1, 12], [0, 7]];

function validCronPart(part, min, max) {
  const segments = String(part || '').split(',');
  if (!segments.length || segments.some(segment => !segment)) return false
  return segments.every(segment => {
    const pieces = segment.split('/');
    if (pieces.length > 2) return false
    const [base, step] = pieces;
    if (step !== undefined && (!/^\d+$/u.test(step) || Number(step) < 1 || Number(step) > (max - min + 1))) return false
    if (base === '*') return true
    if (/^\d+$/u.test(base)) {
      const value = Number(base);
      return value >= min && value <= max
    }
    const range = base.match(/^(\d+)-(\d+)$/u);
    if (!range) return false
    const start = Number(range[1]);
    const end = Number(range[2]);
    return start >= min && end <= max && start <= end
  })
}

function isValidFusionRefreshCron(value) {
  const parts = String(value || '').trim().split(/\s+/u);
  return parts.length === 5 && parts.every((part, index) => validCronPart(part, ...cronRanges[index]))
}

function normalizeFusionRefreshCron(value, fallback = DEFAULT_FUSION_CARD_REFRESH_CRON) {
  const candidate = String(value || '').trim();
  if (isValidFusionRefreshCron(candidate)) return candidate
  const fallbackValue = String(fallback || '').trim();
  return isValidFusionRefreshCron(fallbackValue) ? fallbackValue : DEFAULT_FUSION_CARD_REFRESH_CRON
}

function normalizeFusionCreateCron(value, fallback = DEFAULT_FUSION_CARD_CREATE_CRON) {
  return normalizeFusionRefreshCron(value, fallback)
}

function normalizeCurrentFusionConfig(config = {}) {
  const source = config && typeof config === 'object' && !Array.isArray(config) ? config : {};
  const normalized = { ...source };
  if (Object.hasOwn(source, 'fusion_notify_enabled')) normalized.fusion_notify_enabled = !!source.fusion_notify_enabled;
  if (Object.hasOwn(source, 'fusion_card_create_cron')) normalized.fusion_card_create_cron = normalizeFusionCreateCron(source.fusion_card_create_cron);
  if (Object.hasOwn(source, 'fusion_card_refresh_cron')) normalized.fusion_card_refresh_cron = normalizeFusionRefreshCron(source.fusion_card_refresh_cron);
  return normalized
}

const DEFAULT_SUBSCRIBE_REMINDER_CRON = '0 9 * * *';
const DEFAULT_MARKET_UPDATE_CRON = '0 9 * * *';
const DEFAULT_SITE_STAT_CRON = '0 8 * * *';
const notificationTypes = new Set(['Plugin', 'Other', 'Manual', 'Subscribe', 'Download', 'Organize', 'SiteMessage', 'MediaServer', 'Agent']);

const currentConfigKeys$1 = new Set(configSchemaFields.map(field => field.key));

function currentValues(config = {}) {
  const source = config && typeof config === 'object' && !Array.isArray(config) ? config : {};
  return Object.fromEntries(Object.entries(source).filter(([key]) => currentConfigKeys$1.has(key)))
}

function normalizeCron(value, fallback) {
  const candidate = String(value || '').trim().replace(/\s+/gu, ' ');
  return isValidFusionRefreshCron(candidate) ? candidate : fallback
}

function normalizeCurrentConfig(config = {}) {
  const normalized = normalizeCurrentFusionConfig(currentValues(config));
  if (Object.hasOwn(normalized, 'subscribe_reminder_cron')) {
    normalized.subscribe_reminder_cron = normalizeCron(normalized.subscribe_reminder_cron, DEFAULT_SUBSCRIBE_REMINDER_CRON);
  }
  if (Object.hasOwn(normalized, 'market_update_cron')) {
    normalized.market_update_cron = normalizeCron(normalized.market_update_cron, DEFAULT_MARKET_UPDATE_CRON);
  }
  if (Object.hasOwn(normalized, 'site_stat_cron')) {
    normalized.site_stat_cron = normalizeCron(normalized.site_stat_cron, DEFAULT_SITE_STAT_CRON);
  }
  if (Object.hasOwn(normalized, 'dltag_cron')) {
    normalized.dltag_cron = normalizeCron(normalized.dltag_cron, '');
  }
  if (Object.hasOwn(normalized, 'dltag_tasks')) {
    const values = Array.isArray(normalized.dltag_tasks) ? normalized.dltag_tasks : String(normalized.dltag_tasks || '').split(',');
    const allowed = new Set(['tagging', 'seeding', 'cleanup']);
    normalized.dltag_tasks = [...new Set(values.map(value => String(value || '').trim()).filter(value => allowed.has(value)))];
  }
  if (Object.hasOwn(normalized, 'dltag_source_delete_strategy')) {
    normalized.dltag_source_delete_strategy = normalized.dltag_source_delete_strategy === 'early' ? 'early' : 'delayed';
  }
  if (Object.hasOwn(normalized, 'site_stat_notify_type')) {
    normalized.site_stat_notify_type = notificationTypes.has(normalized.site_stat_notify_type) ? normalized.site_stat_notify_type : 'Plugin';
  }
  if (Object.hasOwn(normalized, 'plugin_uninstall_ids')) {
    const source = normalized.plugin_uninstall_ids;
    normalized.plugin_uninstall_ids = Array.isArray(source)
      ? [...new Set(source.map(value => String(value || '').trim()).filter(Boolean))]
      : String(source || '').split(',').map(value => value.trim()).filter(Boolean);
  }
  return normalized
}

const currentConfigKeys = Object.freeze(configSchemaFields.map(field => field.key));

function buildConfigSavePayload(form = {}) {
  const normalized = normalizeCurrentConfig(form);
  const payload = {};
  for (const key of currentConfigKeys) {
    if (Object.prototype.hasOwnProperty.call(normalized, key)) payload[key] = normalized[key];
  }
  return payload
}

function emitConfigSave(emit, form = {}) {
  const payload = buildConfigSavePayload(form);
  emit('save', payload);
  return payload
}

function serializeConfigSavePayload(payload = {}) {
  return JSON.stringify(payload ?? {})
}

function reloadConfigSavePayload(serializedPayload = '{}') {
  const reloaded = JSON.parse(serializedPayload || '{}');
  if (!reloaded || typeof reloaded !== 'object' || Array.isArray(reloaded)) return {}
  return reloaded
}

export { configSchemaFields as c, emitConfigSave as e, normalizeCurrentConfig as n, reloadConfigSavePayload as r, serializeConfigSavePayload as s };
