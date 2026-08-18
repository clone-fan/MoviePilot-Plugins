const backupConfigBool = (value, fallback = false) => {
  if (typeof value === 'string') return !['', '0', 'false', 'no', 'off'].includes(value.trim().toLowerCase())
  return value == null ? Boolean(fallback) : Boolean(value)
};

function resolveBackupDatabaseEnabled(source = {}) {
  if (Object.prototype.hasOwnProperty.call(source, 'backup_database_enabled')) {
    return backupConfigBool(source.backup_database_enabled, false)
  }
  return backupConfigBool(source.backup_enabled, false)
}

const backupSchemaFieldDescriptors = Object.freeze([
  {
    "key": "backup_cron",
    "type": "string",
    "cardType": "cron",
    "module": "backup",
    "subtab": "backup",
    "label": "备份时间",
    "control": "cron",
    "sourceProfile": "remote-read"
  },
  {
    "key": "backup_enabled",
    "type": "boolean",
    "cardType": "feature",
    "module": "backup",
    "subtab": "backup",
    "label": "启用开关",
    "control": "switch",
    "sourceProfile": "remote-form"
  },
  {
    "key": "backup_database_enabled",
    "type": "boolean",
    "cardType": "feature",
    "module": "backup",
    "subtab": "backup",
    "label": "备份SQL数据库",
    "control": "switch",
    "sourceProfile": "remote-form"
  },
  {
    "key": "backup_webdav_enabled",
    "type": "boolean",
    "cardType": "feature",
    "module": "backup_webdav",
    "subtab": "backup",
    "label": "启用远端备份",
    "control": "switch",
    "sourceProfile": "remote-form"
  },
  {
    "key": "backup_keep_count",
    "type": "number",
    "cardType": "feature",
    "module": "backup",
    "subtab": "backup",
    "label": "保留份数",
    "control": "number",
    "sourceProfile": "remote-form"
  },
  {
    "key": "backup_path",
    "type": "string",
    "cardType": "feature",
    "module": "backup",
    "subtab": "backup",
    "label": "备份目录",
    "control": "text",
    "sourceProfile": "remote-form"
  },
  {
    "key": "backup_notify",
    "type": "boolean",
    "cardType": "notify",
    "module": "backup",
    "subtab": "backup",
    "label": "定时执行后通知",
    "help": "只通知 Cron 执行结果，手动备份不发送。",
    "control": "switch",
    "sourceProfile": "remote-form"
  },
  {
    "key": "backup_notify_type",
    "type": "string",
    "cardType": "notify",
    "module": "backup",
    "subtab": "backup",
    "label": "通知渠道",
    "help": "融合通知启用时只接管此渠道。",
    "control": "select",
    "itemSource": "notificationTypeItems",
    "sourceProfile": "remote-read"
  },
  {
    "key": "backup_webdav_digest_auth",
    "type": "boolean",
    "cardType": "feature",
    "module": "backup_webdav",
    "subtab": "backup",
    "label": "摘要认证",
    "control": "switch",
    "isDisplayed": false,
    "sourceProfile": "remote-form"
  },
  {
    "key": "backup_webdav_disable_check",
    "type": "boolean",
    "cardType": "feature",
    "module": "backup_webdav",
    "subtab": "backup",
    "label": "跳过连通检查",
    "control": "switch",
    "isDisplayed": false,
    "sourceProfile": "remote-form"
  },
  {
    "key": "backup_webdav_hostname",
    "type": "string",
    "cardType": "feature",
    "module": "backup_webdav",
    "subtab": "backup",
    "label": "服务地址",
    "control": "text",
    "sourceProfile": "remote-form"
  },
  {
    "key": "backup_webdav_login",
    "type": "string",
    "cardType": "feature",
    "module": "backup_webdav",
    "subtab": "backup",
    "label": "登录账号",
    "control": "text",
    "sourceProfile": "remote-form"
  },
  {
    "key": "backup_webdav_max_count",
    "type": "number",
    "cardType": "feature",
    "module": "backup_webdav",
    "subtab": "backup",
    "label": "远端保留份数",
    "control": "number",
    "sourceProfile": "remote-form"
  },
  {
    "key": "backup_webdav_password",
    "type": "string",
    "cardType": "feature",
    "module": "backup_webdav",
    "subtab": "backup",
    "label": "登录密码",
    "control": "text",
    "sourceProfile": "remote-form"
  },
]);

const sourceProfile = (defaultSources, sources, sourceFlags, overrides = {}) => Object.freeze({
  defaultSource: defaultSources.join(','),
  defaultSources: Object.freeze([...defaultSources]),
  displayPolicy: 'display',
  displayReason: '',
  sources: Object.freeze([...sources]),
  sourceFlags: Object.freeze({ ...sourceFlags }),
  ...overrides,
});

const CONFIG_FIELD_SOURCE_PROFILES = Object.freeze({
  COMPACT: 'compact',
  REMOTE_READ: 'remote-read',
  REMOTE_FORM: 'remote-form',
  REMOTE_PERSISTED: 'remote-persisted',
  REMOTE_FORM_ONLY: 'remote-form-only',
  LOCAL_DECLARED: 'local-declared',
  LOCAL_FORM: 'local-form',
  BACKEND_RUNTIME: 'backend-runtime',
});

const sourceProfiles = Object.freeze({
  [CONFIG_FIELD_SOURCE_PROFILES.REMOTE_READ]: sourceProfile(
    ['frontend_defaults', 'backend_default_config', 'remote_mp_config'],
    ['frontend_defaults', 'backend_default_config', 'backend_config_read', 'remote_mp_config'],
    { frontendDefaults: true, backendDefaults: true, backendReads: true, vueUses: false, remoteConfig: true },
  ),
  [CONFIG_FIELD_SOURCE_PROFILES.REMOTE_FORM]: sourceProfile(
    ['frontend_defaults', 'backend_default_config', 'remote_mp_config'],
    ['frontend_defaults', 'backend_default_config', 'backend_config_read', 'vue_form_use', 'remote_mp_config'],
    { frontendDefaults: true, backendDefaults: true, backendReads: true, vueUses: true, remoteConfig: true },
  ),
  [CONFIG_FIELD_SOURCE_PROFILES.REMOTE_PERSISTED]: sourceProfile(
    ['frontend_defaults', 'backend_default_config', 'remote_mp_config'],
    ['frontend_defaults', 'backend_default_config', 'remote_mp_config'],
    { frontendDefaults: true, backendDefaults: true, backendReads: false, vueUses: false, remoteConfig: true },
  ),
  [CONFIG_FIELD_SOURCE_PROFILES.REMOTE_FORM_ONLY]: sourceProfile(
    ['frontend_defaults', 'backend_default_config', 'remote_mp_config'],
    ['frontend_defaults', 'backend_default_config', 'vue_form_use', 'remote_mp_config'],
    { frontendDefaults: true, backendDefaults: true, backendReads: false, vueUses: true, remoteConfig: true },
  ),
  [CONFIG_FIELD_SOURCE_PROFILES.LOCAL_DECLARED]: sourceProfile(
    ['frontend_defaults', 'backend_default_config'],
    ['frontend_defaults', 'backend_default_config'],
    { frontendDefaults: true, backendDefaults: true, backendReads: true, vueUses: true, remoteConfig: false },
  ),
  [CONFIG_FIELD_SOURCE_PROFILES.LOCAL_FORM]: sourceProfile(
    ['frontend_defaults', 'backend_default_config'],
    ['frontend_defaults', 'backend_default_config', 'backend_config_read', 'vue_form_use'],
    { frontendDefaults: true, backendDefaults: true, backendReads: true, vueUses: true, remoteConfig: false },
  ),
  [CONFIG_FIELD_SOURCE_PROFILES.BACKEND_RUNTIME]: sourceProfile(
    [],
    ['backend_config_read'],
    { frontendDefaults: false, backendDefaults: false, backendReads: true, vueUses: false, remoteConfig: false },
    {
      defaultSource: 'none',
      displayPolicy: 'runtime',
      displayReason: 'backend-only source cleanup safety setting; never synthesize in the configuration center',
    },
  ),
});

function defineConfigField(descriptor = {}) {
  const type = descriptor.type || 'unknown';
  const selectedProfile = descriptor.sourceProfile || CONFIG_FIELD_SOURCE_PROFILES.COMPACT;
  const profile = selectedProfile === CONFIG_FIELD_SOURCE_PROFILES.COMPACT ? null : sourceProfiles[selectedProfile];
  if (selectedProfile !== CONFIG_FIELD_SOURCE_PROFILES.COMPACT && !profile) {
    throw new Error(`Unknown config field source profile: ${selectedProfile}`)
  }
  if (!descriptor.key || !descriptor.control) {
    throw new Error(`Config field descriptor requires key and control: ${descriptor.key || '<missing>'}`)
  }

  const field = {
    key: descriptor.key,
    type,
    dataType: type,
    cardType: descriptor.cardType,
    module: descriptor.module,
    subtab: descriptor.subtab,
    label: descriptor.label,
    help: descriptor.help || '',
    control: descriptor.control,
  };
  if (Object.hasOwn(descriptor, 'inputType')) field.inputType = descriptor.inputType;
  field.itemSource = descriptor.itemSource || '';
  if (profile) {
    field.defaultSource = profile.defaultSource;
    field.defaultSources = [...profile.defaultSources];
  }
  if (descriptor.retainInCard === true) field.retainInCard = true;
  field.isDisplayed = descriptor.isDisplayed !== false;
  if (profile) {
    field.displayPolicy = profile.displayPolicy;
    field.displayReason = profile.displayReason;
    field.sources = [...profile.sources];
    field.sourceFlags = { ...profile.sourceFlags };
  }
  return field
}

function defineConfigFields(descriptors = []) {
  const fields = descriptors.map(defineConfigField);
  const keys = fields.map(field => field.key);
  const duplicates = keys.filter((key, index) => keys.indexOf(key) !== index);
  if (duplicates.length) throw new Error(`Duplicate config field keys: ${[...new Set(duplicates)].join(', ')}`)
  return fields
}

function defineConfigDefaults(values = {}) {
  if (!values || typeof values !== 'object' || Array.isArray(values)) {
    throw new Error('Config defaults must be a plain object')
  }
  if (Object.entries(values).some(([, value]) => value === undefined)) {
    throw new Error('Config defaults cannot contain undefined values')
  }
  return values
}

function assertConfigFieldDefaults(fields = [], defaults = {}) {
  const fieldKeys = fields.map(field => field.key);
  const defaultKeys = Object.keys(defaults);
  const missingDefaults = fieldKeys.filter(key => !Object.hasOwn(defaults, key));
  const extraDefaults = defaultKeys.filter(key => !fieldKeys.includes(key));
  if (missingDefaults.length || extraDefaults.length) {
    throw new Error(`Config schema/default mismatch: missing=${missingDefaults.join(',')} extra=${extraDefaults.join(',')}`)
  }
}

function configOptionValues(items = []) {
  return Object.freeze([...new Set(items
    .filter(item => item && Object.hasOwn(item, 'value'))
    .map(item => item.value))])
}

const allowedValueSet = allowedValues => allowedValues instanceof Set ? allowedValues : new Set(allowedValues || []);

function normalizeConfigOption(value, allowedValues, fallback) {
  return allowedValueSet(allowedValues).has(value) ? value : fallback
}

function normalizeConfigOptionList(value, allowedValues) {
  const values = Array.isArray(value) ? value : String(value || '').split(',');
  const allowed = allowedValueSet(allowedValues);
  return [...new Set(values
    .map(item => String(item || '').trim())
    .filter(item => allowed.has(item)))]
}

const cronRanges = Object.freeze([[0, 59], [0, 23], [1, 31], [1, 12], [0, 7]]);

function validCronPart(part, min, max) {
  const segments = String(part || '').split(',');
  if (!segments.length || segments.some(segment => !segment)) return false
  return segments.every((segment) => {
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

function isValidConfigCron(value) {
  const parts = String(value || '').trim().split(/\s+/u);
  return parts.length === 5 && parts.every((part, index) => validCronPart(part, ...cronRanges[index]))
}

function normalizeConfigCron(value, fallback = '', { collapseWhitespace = false } = {}) {
  let candidate = String(value || '').trim();
  if (collapseWhitespace) candidate = candidate.replace(/\s+/gu, ' ');
  return isValidConfigCron(candidate) ? candidate : fallback
}

const visibilityConditions = (...conditions) => Object.freeze(conditions.map(condition => Object.freeze({ ...condition })));

const CONFIG_FIELD_VISIBILITY_RULES = Object.freeze({
  subfill_details: visibilityConditions({ key: 'subfill_enabled', value: true }),
  health_check_notify_type: visibilityConditions({ key: 'health_check_notify', value: true }),
  health_check_completion_notify_type: visibilityConditions({ key: 'health_check_completion_notify_enabled', value: true }),
  subfill_completion_notify_type: visibilityConditions({ key: 'subfill_completion_notify_enabled', value: true }),
  backup_notify_type: visibilityConditions({ key: 'backup_notify', value: true }),
  log_clean_notify_type: visibilityConditions({ key: 'log_clean_notify', value: true }),
  seedclean_notify_type: visibilityConditions({ key: 'seedclean_notify', value: true }),
  mp_update_notify_type: visibilityConditions({ key: 'mp_update_scheduled_notify', value: true }),
  market_update_scheduled_notify: visibilityConditions({ key: 'market_update_enabled', value: true }),
  market_update_notify_type: visibilityConditions(
    { key: 'market_update_enabled', value: true },
    { key: 'market_update_scheduled_notify', value: true },
  ),
  market_update_cron: visibilityConditions({ key: 'market_update_enabled', value: true }),
  plugin_update_reminder_notify_type: visibilityConditions({ key: 'plugin_update_reminder_scheduled_notify', value: true }),
  plugin_auto_install_notify_type: visibilityConditions(
    { key: 'plugin_auto_install_enabled', value: true },
    { key: 'plugin_auto_install_scheduled_notify', value: true },
  ),
  plugin_auto_install_scheduled_notify: visibilityConditions({ key: 'plugin_auto_install_enabled', value: true }),
  plugin_auto_install_scope_mode: visibilityConditions({ key: 'plugin_auto_install_enabled', value: true }),
  dltag_notify_type: visibilityConditions({ key: 'dltag_scheduled_notify', value: true }),
  dltag_source_delete_strategy: visibilityConditions({ key: 'dltag_listen_source_file', value: true }),
  plugin_auto_install_install_ids: visibilityConditions(
    { key: 'plugin_auto_install_enabled', value: true },
    { key: 'plugin_auto_install_scope_mode', value: 'include' },
  ),
  plugin_auto_install_exclude_ids: visibilityConditions(
    { key: 'plugin_auto_install_enabled', value: true },
    { key: 'plugin_auto_install_scope_mode', value: 'exclude' },
  ),
});

Object.freeze(Object.fromEntries(
  Object.entries(CONFIG_FIELD_VISIBILITY_RULES)
    .filter(([, conditions]) => conditions.length === 1)
    .map(([key, [condition]]) => [key, condition]),
));

function isConfigFieldVisible(field, values = {}) {
  if (!field || field.hidden) return false
  const conditions = CONFIG_FIELD_VISIBILITY_RULES[field.key];
  return !conditions || conditions.every(condition => values[condition.key] === condition.value)
}

// 插件配置默认值 — 纯数据，无运行时依赖
const DEFAULT_DLTAG_CRON = '0 */6 * * *';

const defaults = defineConfigDefaults({
  enabled: false,
  local_plugin_repo: '',
  fusion_notify_enabled: true,
  fusion_notify_msgtype: 'Plugin',
  fusion_card_create_cron: '5 0 * * *',
  fusion_card_refresh_cron: '0 * * * *',
  health_check_enabled: true,
  health_check_schedule_enabled: true,
  health_check_cron: '0 */6 * * *',
  health_check_items: [],
  health_check_database_targets: ['current'],
  health_check_storage_targets: ['storages', 'config', 'download', 'library'],
  health_check_directory_targets: ['config', 'plugin', 'download', 'library'],
  health_check_storage_threshold: 85,
  health_check_notify: true,
  health_check_completion_notify_enabled: false,
  health_check_notify_type: 'Plugin',
  health_check_completion_notify_type: 'Plugin',
  subscribe_reminder_enabled: true,
  subscribe_reminder_schedule_enabled: true,
  subscribe_reminder_cron: '0 9 * * *',
  subscribe_reminder_subtype: ['movie', 'tv'],
  subscribe_reminder_msgtype: 'Subscribe',
  site_stat_enabled: true,
  site_stat_schedule_enabled: true,
  site_stat_cron: '0 8 * * *',
  site_stat_schedule_notify_enabled: true,
  site_stat_dashboard_type: 'today',
  site_stat_notify_type: 'Plugin',
  log_clean_enabled: false,
  log_clean_schedule_enabled: false,
  log_clean_cron: '0 3 * * 1',
  log_clean_rows: 300,
  log_clean_selected_ids: [],
  log_clean_notify: true,
  log_clean_notify_type: 'Plugin',
  backup_enabled: false,
  backup_database_enabled: false,
  backup_notify: false,
  backup_notify_type: 'Plugin',
  backup_cron: '0 4 * * 1',
  backup_keep_count: 5,
  backup_path: '/config/plugins/Signal/Backup',
  backup_webdav_enabled: false,
  backup_webdav_digest_auth: false,
  backup_webdav_disable_check: false,
  backup_webdav_hostname: '',
  backup_webdav_login: '',
  backup_webdav_password: '',
  backup_webdav_max_count: 5,
  mp_update_enabled: false,
  mp_update_schedule_enabled: false,
  mp_update_cron: '0 9 * * *',
  mp_update_types: ['后端', '前端'],
  market_update_enabled: false,
  market_update_schedule_enabled: false,
  market_update_cron: '0 9 * * *',
  market_update_install_ids: [],
  market_update_exclude_ids: [],
  plugin_update_reminder_enabled: false,
  plugin_update_reminder_schedule_enabled: false,
  plugin_update_reminder_cron: '0 9 * * *',
  mp_update_scheduled_notify: false,
  mp_update_notify_type: 'Plugin',
  market_update_scheduled_notify: false,
  market_update_notify_type: 'Plugin',
  plugin_update_reminder_scheduled_notify: false,
  plugin_update_reminder_notify_type: 'Plugin',
  plugin_auto_install_enabled: false,
  plugin_auto_install_schedule_enabled: false,
  plugin_auto_install_cron: '0 9 * * *',
  plugin_auto_install_scheduled_notify: false,
  plugin_auto_install_notify_type: 'Plugin',
  plugin_auto_install_scope_mode: 'all',
  plugin_auto_install_install_ids: [],
  plugin_auto_install_exclude_ids: [],
  update_scheduled_notify: false,
  update_notify_type: 'Plugin',
  plugin_uninstall_ids: [],
  plugin_uninstall_clear_config: true,
  plugin_uninstall_clear_data: true,
  plugin_uninstall_delete_source: false,
  seedclean_enabled: false,
  seedclean_schedule_enabled: false,
  seedclean_cron: '0 */12 * * *',
  seedclean_action: 'pause',
  seedclean_downloaders: [],
  seedclean_size: '',
  seedclean_ratio: '',
  seedclean_time: '',
  seedclean_upspeed: '',
  seedclean_labels: '',
  seedclean_pathkeywords: '',
  seedclean_trackerkeywords: '',
  seedclean_errorkeywords: '',
  seedclean_torrentstates: '',
  seedclean_trtorrentstates: '',
  seedclean_torrentcategorys: '',
  seedclean_samedata: false,
  seedclean_mponly: false,
  seedclean_notify: true,
  seedclean_notify_type: 'Plugin',
  subfill_enabled: false,
  subfill_details: [],
  subfill_category_enabled: false,
  subfill_category_confs: '',
  subfill_completion_notify_enabled: false,
  subfill_completion_notify_type: 'Plugin',
  msgnotify_enabled: false,
  msgnotify_types: [],
  msgnotify_servers: [],
  msgnotify_notify_type: 'MediaServer',
  dltag_enabled: false,
  dltag_downloaders: [],
  dltag_tasks: ['tagging', 'seeding', 'cleanup'],
  dltag_cron: DEFAULT_DLTAG_CRON,
  dltag_listen_download: true,
  dltag_listen_source_file: false,
  dltag_prefix: '',
  dltag_all_tags: [],
  dltag_excluded_tags: [],
  dltag_not_select_all_tag: '非全',
  dltag_tracker_mappings: '',
  dltag_source_delete_strategy: 'delayed',
  dltag_scheduled_notify: false,
  dltag_notify_type: 'Plugin',
});

const fusionNotificationSchemaFieldDescriptors = Object.freeze([
  {
    "key": "fusion_notify_enabled",
    "type": "boolean",
    "cardType": "notify",
    "module": "fusion_notify",
    "subtab": "fusion",
    "label": "启用融合卡",
    "control": "switch",
    "sourceProfile": "remote-form"
  },
  {
    "key": "fusion_notify_msgtype",
    "type": "string",
    "cardType": "notify",
    "module": "fusion_notify",
    "subtab": "fusion",
    "label": "消息类型",
    "help": "融合卡片通过 MoviePilot 对应消息类型发送。",
    "control": "select",
    "itemSource": "notificationTypeItems",
    "sourceProfile": "remote-form"
  },
]);

const fusionScheduleSchemaFieldDescriptors = Object.freeze([
  {
    "key": "fusion_card_create_cron",
    "type": "string",
    "cardType": "cron",
    "module": "fusion_notify",
    "subtab": "fusion",
    "label": "建卡时间",
    "help": "按标准五段 Cron 建立或切换融合卡，默认每天 00:05。",
    "control": "cron",
    "inputType": "",
    "sourceProfile": "local-form"
  },
  {
    "key": "fusion_card_refresh_cron",
    "type": "string",
    "cardType": "cron",
    "module": "fusion_notify",
    "subtab": "fusion",
    "label": "刷新时间",
    "help": "按 Cron 周期刷新当前活动卡，默认每小时一次。",
    "control": "cron",
    "inputType": "",
    "sourceProfile": "local-form"
  },
]);

const healthCheckCoreSchemaFieldDescriptors = Object.freeze([
  {
    "key": "health_check_cron",
    "type": "string",
    "cardType": "cron",
    "module": "health_check",
    "subtab": "hc",
    "label": "巡查时间",
    "control": "cron",
    "sourceProfile": "remote-read"
  },
  {
    "key": "health_check_database_targets",
    "type": "array",
    "cardType": "feature",
    "module": "health_check",
    "subtab": "hc",
    "label": "数据库项目",
    "control": "select",
    "itemSource": "healthDatabaseTargets",
    "sourceProfile": "remote-form"
  },
  {
    "key": "health_check_directory_targets",
    "type": "array",
    "cardType": "feature",
    "module": "health_check",
    "subtab": "hc",
    "label": "目录项目",
    "control": "select",
    "itemSource": "healthDirectoryTargets",
    "sourceProfile": "remote-form"
  },
  {
    "key": "health_check_enabled",
    "type": "boolean",
    "cardType": "feature",
    "module": "health_check",
    "subtab": "hc",
    "label": "启用开关",
    "control": "switch",
    "sourceProfile": "remote-form"
  },
  {
    "key": "health_check_items",
    "type": "array",
    "cardType": "feature",
    "module": "health_check",
    "subtab": "hc",
    "label": "巡查项目",
    "control": "select",
    "itemSource": "healthCheckItems",
    "sourceProfile": "remote-form"
  },
  {
    "key": "health_check_notify_type",
    "type": "string",
    "cardType": "notify",
    "module": "health_check",
    "subtab": "hc",
    "label": "异常通知渠道",
    "control": "select",
    "itemSource": "notificationTypeItems",
    "sourceProfile": "remote-read"
  },
  {
    "key": "health_check_schedule_enabled",
    "type": "boolean",
    "cardType": "cron",
    "module": "health_check",
    "subtab": "hc",
    "label": "启用定时任务",
    "control": "switch",
    "sourceProfile": "remote-persisted"
  },
  {
    "key": "health_check_storage_targets",
    "type": "array",
    "cardType": "feature",
    "module": "health_check",
    "subtab": "hc",
    "label": "存储项目",
    "control": "select",
    "itemSource": "healthStorageTargets",
    "sourceProfile": "remote-form"
  },
  {
    "key": "health_check_storage_threshold",
    "type": "number",
    "cardType": "feature",
    "module": "health_check",
    "subtab": "hc",
    "label": "存储阈值",
    "control": "number",
    "sourceProfile": "remote-form"
  },
]);

const healthCheckNotificationSchemaFieldDescriptors = Object.freeze([
  {
    "key": "health_check_notify",
    "type": "boolean",
    "cardType": "notify",
    "module": "health_check",
    "subtab": "hc",
    "label": "异常通知",
    "help": "发现巡检异常时发送；异常结果不会同时重复发送完成通知。",
    "control": "switch"
  },
  {
    "key": "health_check_completion_notify_enabled",
    "type": "boolean",
    "cardType": "notify",
    "module": "health_check",
    "subtab": "hc",
    "label": "巡检完成通知",
    "help": "仅在本次巡检全部正常时发送，发现异常时只发送异常通知。",
    "control": "switch"
  },
  {
    "key": "health_check_completion_notify_type",
    "type": "string",
    "cardType": "notify",
    "module": "health_check",
    "subtab": "hc",
    "label": "完成通知渠道",
    "control": "select",
    "itemSource": "notificationTypeItems"
  },
]);

const logCleanSchemaFieldDescriptors = Object.freeze([
  { "key": "log_clean_cron", "type": "string", "cardType": "cron", "module": "log_clean", "subtab": "logs", "label": "清理时间", "control": "cron", "sourceProfile": "remote-read" },
  { "key": "log_clean_enabled", "type": "boolean", "cardType": "feature", "module": "log_clean", "subtab": "logs", "label": "启用开关", "control": "switch", "sourceProfile": "remote-form" },
  { "key": "log_clean_notify", "type": "boolean", "cardType": "notify", "module": "log_clean", "subtab": "logs", "label": "定时执行后通知", "help": "只通知 Cron 执行结果，手动清理不发送。", "control": "switch", "sourceProfile": "remote-form" },
  { "key": "log_clean_notify_type", "type": "string", "cardType": "notify", "module": "log_clean", "subtab": "logs", "label": "通知渠道", "help": "融合通知启用时只接管此渠道。", "control": "select", "itemSource": "notificationTypeItems", "sourceProfile": "remote-read" },
  { "key": "log_clean_rows", "type": "number", "cardType": "feature", "module": "log_clean", "subtab": "logs", "label": "保留行数", "control": "number", "sourceProfile": "remote-form" },
  { "key": "log_clean_schedule_enabled", "type": "boolean", "cardType": "cron", "module": "log_clean", "subtab": "logs", "label": "启用定时任务", "control": "switch", "sourceProfile": "remote-form-only" },
  { "key": "log_clean_selected_ids", "type": "array", "cardType": "feature", "module": "log_clean", "subtab": "logs", "label": "目标日志", "control": "select", "itemSource": "installedPlugins", "sourceProfile": "remote-form" },
]);

const seedCleanSchemaFieldDescriptors = Object.freeze([
  { "key": "seedclean_action", "type": "string", "cardType": "feature", "module": "seedclean", "subtab": "seedremove", "label": "处理动作", "control": "select", "itemSource": "seedActionsItems", "sourceProfile": "remote-form" },
  { "key": "seedclean_cron", "type": "string", "cardType": "cron", "module": "seedclean", "subtab": "seedremove", "label": "执行时间", "control": "cron", "sourceProfile": "remote-read" },
  { "key": "seedclean_downloaders", "type": "array", "cardType": "feature", "module": "seedclean", "subtab": "seedremove", "label": "下载器范围", "control": "select", "itemSource": "downloaderOptions", "sourceProfile": "remote-form" },
  { "key": "seedclean_enabled", "type": "boolean", "cardType": "feature", "module": "seedclean", "subtab": "seedremove", "label": "启用开关", "control": "switch", "sourceProfile": "remote-form" },
  { "key": "seedclean_errorkeywords", "type": "string", "cardType": "feature", "module": "seedclean", "subtab": "seedremove", "label": "错误关键词", "control": "text", "sourceProfile": "remote-form" },
  { "key": "seedclean_labels", "type": "string", "cardType": "feature", "module": "seedclean", "subtab": "seedremove", "label": "标签关键词", "control": "text", "sourceProfile": "remote-form" },
  { "key": "seedclean_mponly", "type": "boolean", "cardType": "feature", "module": "seedclean", "subtab": "seedremove", "label": "仅处理站内任务", "control": "switch", "sourceProfile": "remote-form" },
  { "key": "seedclean_notify", "type": "boolean", "cardType": "notify", "module": "seedclean", "subtab": "seedremove", "label": "结果通知", "control": "switch", "sourceProfile": "remote-read" },
  { "key": "seedclean_notify_type", "type": "string", "cardType": "notify", "module": "seedclean", "subtab": "seedremove", "label": "通知类型", "control": "select", "itemSource": "notificationTypeItems", "sourceProfile": "remote-read" },
  { "key": "seedclean_pathkeywords", "type": "string", "cardType": "feature", "module": "seedclean", "subtab": "seedremove", "label": "路径关键词", "control": "text", "sourceProfile": "remote-form" },
  { "key": "seedclean_ratio", "type": "string", "cardType": "feature", "module": "seedclean", "subtab": "seedremove", "label": "分享率阈值", "control": "text", "sourceProfile": "remote-form" },
  { "key": "seedclean_samedata", "type": "boolean", "cardType": "feature", "module": "seedclean", "subtab": "seedremove", "label": "同体积判定", "control": "switch", "sourceProfile": "remote-form" },
  { "key": "seedclean_schedule_enabled", "type": "boolean", "cardType": "cron", "module": "seedclean", "subtab": "seedremove", "label": "启用定时任务", "control": "switch", "sourceProfile": "remote-persisted" },
  { "key": "seedclean_size", "type": "string", "cardType": "feature", "module": "seedclean", "subtab": "seedremove", "label": "体积阈值", "control": "text", "sourceProfile": "remote-form" },
  { "key": "seedclean_time", "type": "string", "cardType": "feature", "module": "seedclean", "subtab": "seedremove", "label": "时间条件", "control": "text", "sourceProfile": "remote-form" },
  { "key": "seedclean_torrentcategorys", "type": "string", "cardType": "feature", "module": "seedclean", "subtab": "seedremove", "label": "种子分类", "control": "text", "sourceProfile": "remote-form" },
  { "key": "seedclean_torrentstates", "type": "string", "cardType": "feature", "module": "seedclean", "subtab": "seedremove", "label": "种子状态", "control": "text", "sourceProfile": "remote-form" },
  { "key": "seedclean_trtorrentstates", "type": "string", "cardType": "feature", "module": "seedclean", "subtab": "seedremove", "label": "任务状态（TR）", "help": "Transmission 状态可填数字或英文状态，多个用英文逗号分隔。", "control": "text", "sourceProfile": "remote-form" },
  { "key": "seedclean_trackerkeywords", "type": "string", "cardType": "feature", "module": "seedclean", "subtab": "seedremove", "label": "站点来源关键词", "control": "text", "sourceProfile": "remote-form" },
  { "key": "seedclean_upspeed", "type": "string", "cardType": "feature", "module": "seedclean", "subtab": "seedremove", "label": "上传速度阈值", "control": "text", "sourceProfile": "remote-form" },
]);

const downloaderHelperSchemaFieldDescriptors = Object.freeze([
  { "key": "dltag_enabled", "type": "boolean", "cardType": "feature", "module": "downloader_tag", "subtab": "dltagmain", "label": "启用下载器助手", "control": "switch" },
  { "key": "dltag_downloaders", "type": "array", "cardType": "feature", "module": "downloader_tag", "subtab": "dltagmain", "label": "下载器", "control": "select", "itemSource": "downloaderOptions" },
  { "key": "dltag_tasks", "type": "array", "cardType": "feature", "module": "downloader_tag", "subtab": "dltagmain", "label": "执行任务", "control": "select", "itemSource": "dltagTaskItems" },
  { "key": "dltag_cron", "type": "string", "cardType": "feature", "module": "downloader_tag", "subtab": "dltagmain", "label": "执行时间", "control": "cron", "retainInCard": true },
  { "key": "dltag_listen_download", "type": "boolean", "cardType": "feature", "module": "downloader_tag", "subtab": "dltagmain", "label": "监听新增下载", "help": "新增任务时只执行标签和恢复做种，不会删种。", "control": "switch" },
  { "key": "dltag_listen_source_file", "type": "boolean", "cardType": "feature", "module": "downloader_tag", "subtab": "dltagmain", "label": "监听源文件删除", "help": "源文件被删除后按路径匹配并清理下载任务。", "control": "switch" },
  { "key": "dltag_prefix", "type": "string", "cardType": "feature", "module": "downloader_tag", "subtab": "dltagmain", "label": "站点标签前缀", "help": "留空表示不添加前缀。", "control": "text" },
  { "key": "dltag_all_tags", "type": "array", "cardType": "feature", "module": "downloader_tag", "subtab": "dltagmain", "label": "固定标签", "help": "为每个目标任务补充这些标签。", "control": "combobox" },
  { "key": "dltag_excluded_tags", "type": "array", "cardType": "feature", "module": "downloader_tag", "subtab": "dltagmain", "label": "保护标签", "help": "带有保护标签的任务不会被恢复做种或清理，标签仍会正常修正。", "control": "combobox" },
  { "key": "dltag_not_select_all_tag", "type": "string", "cardType": "feature", "module": "downloader_tag", "subtab": "dltagmain", "label": "未全选标签", "help": "任务未选择全部文件时使用的标签。", "control": "text" },
  { "key": "dltag_tracker_mappings", "type": "string", "cardType": "feature", "module": "downloader_tag", "subtab": "dltagmain", "label": "Tracker 映射", "control": "textarea" },
  { "key": "dltag_source_delete_strategy", "type": "string", "cardType": "feature", "module": "downloader_tag", "subtab": "dltagmain", "label": "源文件清理时机", "help": "提前清理只删除下载任务，不删除数据文件。", "control": "select", "itemSource": "dltagDeleteStrategyItems" },
  { "key": "dltag_scheduled_notify", "type": "boolean", "cardType": "notify", "module": "downloader_tag", "subtab": "dltagmain", "label": "定时执行后通知", "help": "只通知 Cron 执行结果，手动和事件执行不发送。", "control": "switch" },
  { "key": "dltag_notify_type", "type": "string", "cardType": "notify", "module": "downloader_tag", "subtab": "dltagmain", "label": "通知渠道", "help": "融合通知启用时只接管此渠道。", "control": "select", "itemSource": "notificationTypeItems" },
]);

const mediaNotifySchemaFieldDescriptors = Object.freeze([
  {
    "key": "msgnotify_enabled",
    "type": "boolean",
    "cardType": "notify",
    "module": "media_notify",
    "subtab": "server",
    "label": "启用开关",
    "control": "switch",
    "sourceProfile": "remote-form"
  },
  {
    "key": "msgnotify_notify_type",
    "type": "string",
    "cardType": "notify",
    "module": "media_notify",
    "subtab": "server",
    "label": "通知类型",
    "control": "select",
    "itemSource": "notificationTypeItems",
    "sourceProfile": "remote-read"
  },
  {
    "key": "msgnotify_servers",
    "type": "array",
    "cardType": "notify",
    "module": "media_notify",
    "subtab": "server",
    "label": "通知服务器",
    "control": "select",
    "itemSource": "mediaserverOptions",
    "sourceProfile": "remote-form"
  },
  {
    "key": "msgnotify_types",
    "type": "array",
    "cardType": "notify",
    "module": "media_notify",
    "subtab": "server",
    "label": "通知事件",
    "control": "select",
    "itemSource": "msgGroupItems",
    "sourceProfile": "remote-form"
  },
]);

const subscribeReminderSchemaFieldDescriptors = Object.freeze([
  {
    "key": "subscribe_reminder_cron",
    "type": "string",
    "cardType": "cron",
    "module": "subscribe_reminder",
    "subtab": "subscribe",
    "label": "检查时间",
    "control": "cron",
    "sourceProfile": "remote-read"
  },
  {
    "key": "subscribe_reminder_enabled",
    "type": "boolean",
    "cardType": "feature",
    "module": "subscribe_reminder",
    "subtab": "subscribe",
    "label": "启用开关",
    "control": "switch",
    "sourceProfile": "remote-form"
  },
  {
    "key": "subscribe_reminder_msgtype",
    "type": "string",
    "cardType": "notify",
    "module": "subscribe_reminder",
    "subtab": "subscribe",
    "label": "消息类型",
    "control": "select",
    "itemSource": "messageTypeItems",
    "sourceProfile": "remote-read"
  },
  {
    "key": "subscribe_reminder_schedule_enabled",
    "type": "boolean",
    "cardType": "cron",
    "module": "subscribe_reminder",
    "subtab": "subscribe",
    "label": "启用定时任务",
    "control": "switch",
    "sourceProfile": "remote-persisted"
  },
  {
    "key": "subscribe_reminder_subtype",
    "type": "array",
    "cardType": "feature",
    "module": "subscribe_reminder",
    "subtab": "subscribe",
    "label": "订阅类型",
    "control": "select",
    "itemSource": "subscribeSubtypeItems",
    "sourceProfile": "remote-form"
  },
]);

const pluginShellSchemaFieldDescriptors = Object.freeze([
  { "key": "enabled", "type": "boolean", "cardType": "generic", "module": "plugin", "subtab": "clean", "label": "启用开关", "control": "switch", "sourceProfile": "remote-form" },
]);

const pluginRuntimeSchemaFieldDescriptors = Object.freeze([
  { "key": "local_plugin_repo", "type": "unknown", "cardType": "runtime", "module": "plugin", "subtab": "clean", "label": "本地插件仓库", "control": "text", "isDisplayed": false, "sourceProfile": "backend-runtime" },
]);

const pluginUninstallSchemaFieldDescriptors = Object.freeze([
  { "key": "plugin_uninstall_clear_config", "type": "boolean", "cardType": "feature", "module": "plugin_uninstall", "subtab": "clean", "label": "清理配置", "control": "switch", "sourceProfile": "remote-form" },
  { "key": "plugin_uninstall_clear_data", "type": "boolean", "cardType": "feature", "module": "plugin_uninstall", "subtab": "clean", "label": "清理数据", "control": "switch", "sourceProfile": "remote-form" },
  { "key": "plugin_uninstall_delete_source", "type": "boolean", "cardType": "feature", "module": "plugin_uninstall", "subtab": "clean", "label": "删除源码目录", "control": "switch", "sourceProfile": "remote-form" },
  { "key": "plugin_uninstall_ids", "type": "array", "cardType": "feature", "module": "plugin_uninstall", "subtab": "clean", "label": "目标插件", "control": "select", "itemSource": "installedPlugins", "sourceProfile": "remote-form" },
]);

const siteStatCoreSchemaFieldDescriptors = Object.freeze([
  {
    "key": "site_stat_dashboard_type",
    "type": "string",
    "cardType": "feature",
    "module": "site_stat",
    "subtab": "sites",
    "label": "仪表盘口径",
    "control": "select",
    "itemSource": "siteStatRangeItems",
    "sourceProfile": "remote-form"
  },
  {
    "key": "site_stat_enabled",
    "type": "boolean",
    "cardType": "feature",
    "module": "site_stat",
    "subtab": "sites",
    "label": "启用开关",
    "control": "switch",
    "sourceProfile": "remote-form"
  },
  {
    "key": "site_stat_schedule_enabled",
    "type": "boolean",
    "cardType": "cron",
    "module": "site_stat",
    "subtab": "sites",
    "label": "??????",
    "control": "switch",
    "sourceProfile": "local-declared"
  },
  {
    "key": "site_stat_cron",
    "type": "string",
    "cardType": "cron",
    "module": "site_stat",
    "subtab": "sites",
    "label": "统计时间",
    "help": "???????????????????? 08:00?",
    "control": "cron",
    "sourceProfile": "local-form"
  },
  {
    "key": "site_stat_notify_type",
    "type": "string",
    "cardType": "notify",
    "module": "site_stat",
    "subtab": "sites",
    "label": "通知类型",
    "help": "融合通知关闭时，定时统计结果通过此 MoviePilot 通知类型发送。",
    "control": "select",
    "itemSource": "notificationTypeItems",
    "sourceProfile": "remote-read"
  },
]);

const siteStatNotificationSchemaFieldDescriptors = Object.freeze([
  {
    "key": "site_stat_schedule_notify_enabled",
    "type": "boolean",
    "cardType": "notify",
    "module": "site_stat",
    "subtab": "sites",
    "label": "定时执行后通知",
    "help": "只通知 Cron 执行结果，手动统计不发送。",
    "control": "switch"
  },
]);

const subscriptionFillCoreSchemaFieldDescriptors = Object.freeze([
  {
    "key": "subfill_category_confs",
    "type": "string",
    "cardType": "feature",
    "module": "subfill",
    "subtab": "subfill",
    "label": "规则配置",
    "control": "text",
    "sourceProfile": "remote-form"
  },
  {
    "key": "subfill_category_enabled",
    "type": "boolean",
    "cardType": "feature",
    "module": "subfill",
    "subtab": "subfill",
    "label": "二级分类订阅填充",
    "control": "switch",
    "sourceProfile": "remote-form"
  },
  {
    "key": "subfill_details",
    "type": "array",
    "cardType": "feature",
    "module": "subfill",
    "subtab": "subfill",
    "label": "填充项",
    "control": "select",
    "itemSource": "subfillDetailItems",
    "sourceProfile": "remote-form"
  },
  {
    "key": "subfill_enabled",
    "type": "boolean",
    "cardType": "feature",
    "module": "subfill",
    "subtab": "subfill",
    "label": "下载完成订阅填充",
    "control": "switch",
    "sourceProfile": "remote-form"
  },
]);

const subscriptionFillNotificationSchemaFieldDescriptors = Object.freeze([
  {
    "key": "subfill_completion_notify_enabled",
    "type": "boolean",
    "cardType": "notify",
    "module": "subfill",
    "subtab": "subfill",
    "label": "填充完成通知",
    "help": "下载完成填充或新增订阅二级分类填充发生实际变更时通知；无变化不发送。",
    "control": "switch"
  },
  {
    "key": "subfill_completion_notify_type",
    "type": "string",
    "cardType": "notify",
    "module": "subfill",
    "subtab": "subfill",
    "label": "填充通知渠道",
    "help": "下载完成填充和二级分类填充共用此通知渠道。",
    "control": "select",
    "itemSource": "notificationTypeItems"
  },
]);

const marketUpdateCoreSchemaFieldDescriptors = Object.freeze([
  { "key": "market_update_enabled", "type": "boolean", "cardType": "feature", "module": "market_update", "subtab": "updates", "label": "启用开关", "control": "switch", "sourceProfile": "remote-form" },
  { "key": "market_update_exclude_ids", "type": "array", "cardType": "feature", "module": "market_update", "subtab": "updates", "label": "忽略插件", "control": "select", "itemSource": "installedPlugins", "isDisplayed": false, "sourceProfile": "remote-form" },
  { "key": "market_update_install_ids", "type": "array", "cardType": "feature", "module": "market_update", "subtab": "updates", "label": "自动安装插件", "control": "select", "itemSource": "installedPlugins", "isDisplayed": false, "sourceProfile": "remote-form" },
  { "key": "market_update_schedule_enabled", "type": "boolean", "cardType": "cron", "module": "market_update", "subtab": "updates", "label": "启用定时任务", "control": "switch", "isDisplayed": false, "sourceProfile": "remote-persisted" },
]);

const moviePilotUpdateCoreSchemaFieldDescriptors = Object.freeze([
  { "key": "mp_update_cron", "type": "string", "cardType": "cron", "module": "mp_update", "subtab": "updates", "label": "系统检查时间", "control": "cron", "sourceProfile": "remote-read" },
  { "key": "mp_update_enabled", "type": "boolean", "cardType": "feature", "module": "mp_update", "subtab": "updates", "label": "启用开关", "control": "switch", "sourceProfile": "remote-form" },
  { "key": "mp_update_schedule_enabled", "type": "boolean", "cardType": "cron", "module": "mp_update", "subtab": "updates", "label": "启用定时任务", "control": "switch", "isDisplayed": false, "sourceProfile": "remote-persisted" },
  { "key": "mp_update_types", "type": "array", "cardType": "feature", "module": "mp_update", "subtab": "updates", "label": "检查范围", "control": "select", "itemSource": "mpUpdateTypes", "sourceProfile": "remote-form" },
]);

const marketUpdateScheduleSchemaFieldDescriptors = Object.freeze([
  { "key": "market_update_cron", "type": "string", "cardType": "cron", "module": "market_update", "subtab": "updates", "label": "插件库同步时间", "help": "按 Cron 定时同步插件库。", "control": "cron", "inputType": "", "sourceProfile": "local-form" },
]);

const updateGovernanceDetailSchemaFieldDescriptors = Object.freeze([
  { "key": "plugin_update_reminder_enabled", "type": "boolean", "cardType": "feature", "module": "plugin_update_reminder", "subtab": "updates", "label": "启用插件更新", "help": "控制插件更新检查；自动安装是否执行由内部开关决定。", "control": "switch" },
  { "key": "plugin_update_reminder_cron", "type": "string", "cardType": "cron", "module": "plugin_update_reminder", "subtab": "updates", "label": "插件更新时间", "help": "按 Cron 定时检查插件更新。", "control": "cron" },
  { "key": "mp_update_scheduled_notify", "type": "boolean", "cardType": "notify", "module": "mp_update", "subtab": "updates", "label": "定时执行后通知", "help": "只通知 Cron 执行结果，手动执行不发送。", "control": "switch" },
  { "key": "mp_update_notify_type", "type": "string", "cardType": "notify", "module": "mp_update", "subtab": "updates", "label": "通知渠道", "help": "系统更新结果使用的通知渠道。", "control": "select", "itemSource": "notificationTypeItems" },
  { "key": "market_update_scheduled_notify", "type": "boolean", "cardType": "notify", "module": "market_update", "subtab": "updates", "label": "定时执行后通知", "help": "只通知 Cron 执行结果，手动执行不发送。", "control": "switch" },
  { "key": "market_update_notify_type", "type": "string", "cardType": "notify", "module": "market_update", "subtab": "updates", "label": "通知渠道", "help": "插件库同步结果使用的通知渠道。", "control": "select", "itemSource": "notificationTypeItems" },
  { "key": "plugin_update_reminder_scheduled_notify", "type": "boolean", "cardType": "notify", "module": "plugin_update_reminder", "subtab": "updates", "label": "定时执行后通知", "help": "只通知 Cron 执行结果，手动执行不发送。", "control": "switch" },
  { "key": "plugin_update_reminder_notify_type", "type": "string", "cardType": "notify", "module": "plugin_update_reminder", "subtab": "updates", "label": "通知渠道", "help": "插件更新结果使用的通知渠道。", "control": "select", "itemSource": "notificationTypeItems" },
  { "key": "plugin_auto_install_enabled", "type": "boolean", "cardType": "feature", "module": "plugin_auto_install", "subtab": "updates", "label": "启用自动安装", "help": "独立控制插件更新安装；默认关闭。", "control": "switch" },
  { "key": "plugin_auto_install_scheduled_notify", "type": "boolean", "cardType": "notify", "module": "plugin_auto_install", "subtab": "updates", "label": "安装后通知", "help": "插件更新检查实际安装插件后发送结果。", "control": "switch" },
  { "key": "plugin_auto_install_scope_mode", "type": "string", "cardType": "feature", "module": "plugin_auto_install", "subtab": "updates", "label": "安装范围", "help": "三选一；切换只改变当前生效范围，保留各名单中的已选值。", "control": "select", "itemSource": "pluginAutoInstallScopeItems" },
  { "key": "plugin_auto_install_install_ids", "type": "array", "cardType": "feature", "module": "plugin_auto_install", "subtab": "updates", "label": "指定插件", "help": "仅安装这份名单中的插件；空名单表示不安装任何插件。", "control": "select", "itemSource": "installedPlugins" },
  { "key": "plugin_auto_install_exclude_ids", "type": "array", "cardType": "feature", "module": "plugin_auto_install", "subtab": "updates", "label": "排除插件", "help": "这份名单中的插件不会自动安装更新。", "control": "select", "itemSource": "installedPlugins" },
  { "key": "plugin_auto_install_cron", "type": "string", "cardType": "cron", "module": "plugin_auto_install", "subtab": "updates", "label": "自动安装时间", "help": "兼容旧配置；自动安装跟随插件更新检查执行，不再单独调度。", "control": "cron", "isDisplayed": false },
  { "key": "plugin_auto_install_notify_type", "type": "string", "cardType": "notify", "module": "plugin_auto_install", "subtab": "updates", "label": "安装通知渠道", "help": "插件自动安装结果使用的独立通知渠道。", "control": "select", "itemSource": "notificationTypeItems" },
  { "key": "plugin_update_reminder_schedule_enabled", "type": "boolean", "cardType": "cron", "module": "plugin_update_reminder", "subtab": "updates", "label": "启用定时任务", "help": "兼容旧配置，定时是否运行现在由任务开关和 Cron 决定。", "control": "switch", "isDisplayed": false },
  { "key": "plugin_auto_install_schedule_enabled", "type": "boolean", "cardType": "cron", "module": "plugin_auto_install", "subtab": "updates", "label": "启用自动安装定时任务", "help": "兼容旧配置，定时是否运行现在由自动安装开关和 Cron 决定。", "control": "switch", "isDisplayed": false },
  { "key": "update_scheduled_notify", "type": "boolean", "cardType": "notify", "module": "updates", "subtab": "updates", "label": "定时执行后通知", "help": "兼容旧配置，迁移到各更新任务自己的通知开关。", "control": "switch", "isDisplayed": false },
  { "key": "update_notify_type", "type": "string", "cardType": "notify", "module": "updates", "subtab": "updates", "label": "通知渠道", "help": "兼容旧配置，迁移到各更新任务自己的通知渠道。", "control": "select", "itemSource": "notificationTypeItems", "isDisplayed": false },
]);

// Current-only configuration field contract. Legacy fields are intentionally absent.

const configSchemaFields = Object.freeze(defineConfigFields([
  ...backupSchemaFieldDescriptors,
  ...pluginShellSchemaFieldDescriptors,
  ...fusionNotificationSchemaFieldDescriptors,
  ...healthCheckCoreSchemaFieldDescriptors,
  ...pluginRuntimeSchemaFieldDescriptors,
  ...logCleanSchemaFieldDescriptors,
  ...marketUpdateCoreSchemaFieldDescriptors,
  ...moviePilotUpdateCoreSchemaFieldDescriptors,
  ...mediaNotifySchemaFieldDescriptors,
  ...pluginUninstallSchemaFieldDescriptors,
  ...seedCleanSchemaFieldDescriptors,
  ...siteStatCoreSchemaFieldDescriptors,
  ...subscriptionFillCoreSchemaFieldDescriptors,
  ...subscribeReminderSchemaFieldDescriptors,
  ...fusionScheduleSchemaFieldDescriptors,
  ...marketUpdateScheduleSchemaFieldDescriptors,
  ...healthCheckNotificationSchemaFieldDescriptors,
  ...siteStatNotificationSchemaFieldDescriptors,
  ...subscriptionFillNotificationSchemaFieldDescriptors,
  ...updateGovernanceDetailSchemaFieldDescriptors,
  ...downloaderHelperSchemaFieldDescriptors,
]));

assertConfigFieldDefaults(configSchemaFields, defaults);

Object.freeze(
  Object.fromEntries(configSchemaFields.map(field => [field.key, field])),
);

// 配置页选项列表 — 纯数据，无运行时依赖

const subscribeSubtypeItems = [{ title: '电影', value: 'movie' }, { title: '电视剧', value: 'tv' }];

const notificationTypeItems = [
  { title: '插件', value: 'Plugin' },
  { title: '其他', value: 'Other' },
  { title: '手动处理', value: 'Manual' },
  { title: '订阅', value: 'Subscribe' },
  { title: '资源下载', value: 'Download' },
  { title: '整理入库', value: 'Organize' },
  { title: '站点', value: 'SiteMessage' },
  { title: '媒体服务器', value: 'MediaServer' },
  { title: '智能体', value: 'Agent' },
];
const notificationTypeValues = configOptionValues(notificationTypeItems);

const messageTypeItems = [
  { title: '订阅', value: 'Subscribe' },
  { title: '插件', value: 'Plugin' },
  { title: '其他', value: 'Other' },
  { title: '手动处理', value: 'Manual' },
  { title: '资源下载', value: 'Download' },
  { title: '整理入库', value: 'Organize' },
  { title: '站点', value: 'SiteMessage' },
  { title: '媒体服务器', value: 'MediaServer' },
  { title: '智能体', value: 'Agent' },
];
configOptionValues(messageTypeItems);

const siteStatRangeItems = [{ title: '今日数据', value: 'today' }, { title: '汇总数据', value: 'total' }, { title: '所有数据', value: 'all' }];
const marketNotifyItems = notificationTypeItems;
const mpUpdateTypes = ['后端', '前端'].map(v => ({ title: v, value: v }));
const pluginAutoInstallScopeItems = [
  { title: '全部插件', value: 'all' },
  { title: '仅安装指定插件', value: 'include' },
  { title: '排除指定插件', value: 'exclude' },
];
const pluginAutoInstallScopeValues = configOptionValues(pluginAutoInstallScopeItems);
const marketUpdateStrategies = [
  { title: '仅检查', value: 'check' },
  { title: '同步插件库', value: 'sync' },
  { title: '同步并更新插件', value: 'install' },
];
const keepCountPresets = [3, 5, 7, 10, 15].map(v => ({ title: `保留 ${v} 份`, value: v }));
const seedActionsItems = [{ title: '暂停', value: 'pause' }, { title: '删除种子', value: 'delete' }, { title: '删除种子和文件', value: 'deletefile' }];
const dltagTaskItems = [
  { title: '自动标签', value: 'tagging' },
  { title: '恢复做种', value: 'seeding' },
  { title: '清理失效任务', value: 'cleanup' },
];
const dltagTaskValues = configOptionValues(dltagTaskItems);
const dltagDeleteStrategyItems = [
  { title: '确认文件已删除后清理', value: 'delayed' },
  { title: '收到事件后立即清理', value: 'early' },
];
const dltagDeleteStrategyValues = configOptionValues(dltagDeleteStrategyItems);
const subfillDetailItems = ['分辨率', '资源质量', '特效', '制作组', '站点'].map(v => ({ title: v, value: v }));
const msgGroupItems = ['新入库', '开始播放', '停止播放', '登录成功', '登录失败', '标记'].map(v => ({ title: v, value: v }));

const healthCheckItems = [
  { title: '数据库', value: '数据库', icon: 'mdi-database-check-outline', desc: '连接与基础读写状态' },
  { title: '存储空间', value: '存储空间', icon: 'mdi-harddisk', desc: '下载与媒体库容量余量' },
  { title: '目录权限', value: '目录权限', icon: 'mdi-folder-key-outline', desc: '关键路径可访问性' },
];

const healthDatabaseTargets = [
  { title: '当前主库', value: 'current' },
  { title: 'SQLite 配置库', value: 'sqlite' },
  { title: 'PostgreSQL 主库', value: 'postgresql' },
];

const healthStorageTargets = [
  { title: 'MoviePilot 存储配置', value: 'storages' },
  { title: '配置目录', value: 'config' },
  { title: '下载目录', value: 'download' },
  { title: '媒体库目录', value: 'library' },
];

const healthDirectoryTargets = [
  { title: '配置目录', value: 'config' },
  { title: '插件目录', value: 'plugin' },
  { title: '下载目录', value: 'download' },
  { title: '媒体库目录', value: 'library' },
];

function normalizeFusionRefreshCron(value, fallback = defaults.fusion_card_refresh_cron) {
  const fallbackValue = String(fallback || '').trim();
  const safeFallback = isValidConfigCron(fallbackValue) ? fallbackValue : defaults.fusion_card_refresh_cron;
  return normalizeConfigCron(value, safeFallback)
}

function normalizeFusionCreateCron(value, fallback = defaults.fusion_card_create_cron) {
  return normalizeFusionRefreshCron(value, fallback)
}

function normalizeFusionNotifyMsgtype(value) {
  return normalizeConfigOption(value, notificationTypeValues, defaults.fusion_notify_msgtype)
}

function normalizeCurrentFusionConfig(config = {}) {
  const source = config && typeof config === 'object' && !Array.isArray(config) ? config : {};
  const normalized = { ...source };
  if (Object.hasOwn(source, 'fusion_notify_enabled')) normalized.fusion_notify_enabled = !!source.fusion_notify_enabled;
  if (Object.hasOwn(source, 'fusion_notify_msgtype')) normalized.fusion_notify_msgtype = normalizeFusionNotifyMsgtype(source.fusion_notify_msgtype);
  if (Object.hasOwn(source, 'fusion_card_create_cron')) normalized.fusion_card_create_cron = normalizeFusionCreateCron(source.fusion_card_create_cron);
  if (Object.hasOwn(source, 'fusion_card_refresh_cron')) normalized.fusion_card_refresh_cron = normalizeFusionRefreshCron(source.fusion_card_refresh_cron);
  return normalized
}

const currentConfigKeys$1 = new Set(configSchemaFields.map(field => field.key));

function currentValues(config = {}) {
  const source = config && typeof config === 'object' && !Array.isArray(config) ? config : {};
  return Object.fromEntries(Object.entries(source).filter(([key]) => currentConfigKeys$1.has(key)))
}

function normalizeCron(value, fallback) {
  return normalizeConfigCron(value, fallback, { collapseWhitespace: true })
}

function normalizeCurrentConfig(config = {}) {
  const normalized = normalizeCurrentFusionConfig(currentValues(config));
  if (Object.hasOwn(normalized, 'subscribe_reminder_cron')) {
    normalized.subscribe_reminder_cron = normalizeCron(normalized.subscribe_reminder_cron, defaults.subscribe_reminder_cron);
  }
  if (Object.hasOwn(normalized, 'market_update_cron')) {
    normalized.market_update_cron = normalizeCron(normalized.market_update_cron, defaults.market_update_cron);
  }
  for (const key of ['plugin_update_reminder_cron', 'plugin_auto_install_cron']) {
    if (Object.hasOwn(normalized, key)) normalized[key] = normalizeCron(normalized[key], defaults[key]);
  }
  if (Object.hasOwn(normalized, 'site_stat_cron')) {
    normalized.site_stat_cron = normalizeCron(normalized.site_stat_cron, defaults.site_stat_cron);
  }
  if (Object.hasOwn(normalized, 'dltag_cron')) {
    normalized.dltag_cron = normalizeCron(normalized.dltag_cron, '');
  }
  if (Object.hasOwn(normalized, 'dltag_tasks')) {
    normalized.dltag_tasks = normalizeConfigOptionList(normalized.dltag_tasks, dltagTaskValues);
  }
  if (Object.hasOwn(normalized, 'dltag_source_delete_strategy')) {
    normalized.dltag_source_delete_strategy = normalizeConfigOption(
      normalized.dltag_source_delete_strategy,
      dltagDeleteStrategyValues,
      defaults.dltag_source_delete_strategy,
    );
  }
  if (Object.hasOwn(normalized, 'site_stat_notify_type')) {
    normalized.site_stat_notify_type = normalizeConfigOption(
      normalized.site_stat_notify_type,
      notificationTypeValues,
      defaults.site_stat_notify_type,
    );
  }
  for (const key of [
    'health_check_completion_notify_type',
    'subfill_completion_notify_type',
    'mp_update_notify_type',
    'market_update_notify_type',
    'plugin_update_reminder_notify_type',
    'plugin_auto_install_notify_type',
  ]) {
    if (Object.hasOwn(normalized, key)) {
      normalized[key] = normalizeConfigOption(normalized[key], notificationTypeValues, defaults[key]);
    }
  }
  if (Object.hasOwn(normalized, 'plugin_uninstall_ids')) {
    const source = normalized.plugin_uninstall_ids;
    normalized.plugin_uninstall_ids = Array.isArray(source)
      ? [...new Set(source.map(value => String(value || '').trim()).filter(Boolean))]
      : String(source || '').split(',').map(value => value.trim()).filter(Boolean);
  }
  for (const key of ['plugin_auto_install_install_ids', 'plugin_auto_install_exclude_ids']) {
    if (!Object.hasOwn(normalized, key)) continue
    const source = normalized[key];
    normalized[key] = Array.isArray(source)
      ? [...new Set(source.map(value => String(value || '').trim()).filter(Boolean))]
      : String(source || '').split(',').map(value => value.trim()).filter(Boolean);
  }
  if (Object.hasOwn(normalized, 'plugin_auto_install_scope_mode')) {
    const mode = String(normalized.plugin_auto_install_scope_mode || '').trim().toLowerCase();
    normalized.plugin_auto_install_scope_mode = normalizeConfigOption(
      mode,
      pluginAutoInstallScopeValues,
      defaults.plugin_auto_install_scope_mode,
    );
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

export { healthDatabaseTargets as A, healthCheckItems as B, keepCountPresets as C, DEFAULT_DLTAG_CRON as D, normalizeCurrentConfig as a, buildConfigSavePayload as b, configSchemaFields as c, defaults as d, emitConfigSave as e, resolveBackupDatabaseEnabled as f, dltagDeleteStrategyItems as g, dltagTaskItems as h, isConfigFieldVisible as i, subscribeSubtypeItems as j, subfillDetailItems as k, siteStatRangeItems as l, seedActionsItems as m, normalizeConfigOption as n, notificationTypeItems as o, pluginAutoInstallScopeValues as p, msgGroupItems as q, reloadConfigSavePayload as r, serializeConfigSavePayload as s, pluginAutoInstallScopeItems as t, marketUpdateStrategies as u, mpUpdateTypes as v, messageTypeItems as w, marketNotifyItems as x, healthStorageTargets as y, healthDirectoryTargets as z };
