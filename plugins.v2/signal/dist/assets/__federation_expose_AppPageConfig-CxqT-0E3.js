import { importShared } from './__federation_fn_import-JrT3xvdd.js';
import { aG as mdiShieldCheckOutline, bl as mdiFilterOutline, bB as mdiCogOutline, b4 as mdiLinkVariant, c7 as mdiChevronDown, aX as mdiPlay, bu as mdiDeleteOutline, ao as mdiWeight, aC as mdiSignal, aF as mdiShieldHalfFull, aK as mdiSendOutline, aY as mdiPercent, aZ as mdiPencilOutline, b7 as mdiLayersOutline, c3 as mdiAlphaMBoxOutline, c5 as mdiAlertCircleOutline, ba as mdiHeartPulse, ax as mdiTelevision, bS as mdiCardAccountDetailsOutline, b$ as mdiBackupRestore, b9 as mdiHistory, aS as mdiPuzzleOutline, aU as mdiPuzzle, bs as mdiDownload, bX as mdiBellOutline, b_ as mdiBell, c8 as mdiEyeOutline, aW as mdiPlusCircleOutline, by as mdiCubeOutline, bC as mdiCodeTags, bv as mdiDatabaseOutline, c4 as mdiAlertOutline, bD as mdiCloudUploadOutline, aE as mdiShieldOutline, bp as mdiDownloadOutline, aB as mdiSync, bU as mdiBroom, aO as mdiRocketLaunchOutline, bh as mdiFolderOutline, b3 as mdiLockCheckOutline, bA as mdiContentCopy, c6 as mdiAccountOutline, ap as mdiWeb, bH as mdiCloudOutline, b2 as mdiLockOutline, az as mdiTagOutline, au as mdiTimerOutline, aL as mdiScaleBalance, bb as mdiHarddisk, bc as mdiGauge, bQ as mdiChartBar, a$ as mdiMovieOpenOutline, be as mdiFormatListChecks, aJ as mdiServer, bo as mdiEmailOutline, bd as mdiFormatListNumbered, bT as mdiCalendarClock, aV as mdiPowerStandby, as as mdiUpdate, bn as mdiFileDocumentRemoveOutline, c2 as mdiArchiveArrowUpOutline, c0 as mdiAutoFix, aA as mdiTagMultipleOutline, bt as mdiDeleteSweepOutline, bW as mdiBellRingOutline, aw as mdiTelevisionPlay, aQ as mdiPuzzleRemoveOutline, bq as mdiDownloadNetworkOutline, bP as mdiChartLine, b1 as mdiMessageBadgeOutline } from './mdi-DNDHBjvE.js';
import { c as configSchemaFields, i as isConfigFieldVisible, n as normalizeConfigOption, d as defaults, p as pluginAutoInstallScopeValues, b as buildConfigSavePayload, e as emitConfigSave, a as normalizeCurrentConfig, D as DEFAULT_DLTAG_CRON, f as dltagDeleteStrategyItems, g as dltagTaskItems, h as subscribeSubtypeItems, j as subfillDetailItems, k as siteStatRangeItems, l as seedActionsItems, m as notificationTypeItems, o as msgGroupItems, q as pluginAutoInstallScopeItems, t as marketUpdateStrategies, u as mpUpdateTypes, v as messageTypeItems, w as marketNotifyItems, x as healthStorageTargets, y as healthDirectoryTargets, z as healthDatabaseTargets, A as healthCheckItems, B as keepCountPresets } from './save-payload-BE6FIqnc.js';
import { g as getPluginApi, r as resolvePluginApi, a as getActionForSurface, A as ACTION_OPERATION_MODE, c as createPluginWorkflowClient, u as useAgentOpsTheme, b as useConfigActionRunner, d as getActionsForSurface, e as ActionOperationPanel } from './ActionOperationPanel-BhsDOXcn.js';

const {resolveComponent:_resolveComponent$4,createVNode:_createVNode$l,createElementVNode:_createElementVNode$c,toDisplayString:_toDisplayString$c,openBlock:_openBlock$s,createElementBlock:_createElementBlock$p,createCommentVNode:_createCommentVNode$c,renderSlot:_renderSlot$d,normalizeClass:_normalizeClass$8} = await importShared('vue');


const _hoisted_1$p = ["data-html-replica-card", "data-flat-config-section", "data-cron-card", "data-schedule-card", "data-notify-card"];
const _hoisted_2$h = {
  key: 0,
  class: "aoa-config-card__head aoa-design-section-title"
};
const _hoisted_3$c = { class: "aoa-config-card__icon aoa-design-section-title__leading" };
const _hoisted_4$b = { class: "aoa-config-card__copy aoa-design-section-title__text" };
const _hoisted_5$9 = { key: 0 };
const _hoisted_6$9 = { class: "aoa-config-card__trailing aoa-design-section-title__trailing" };


const _sfc_main$s = {
  __name: 'ConfigCardBase',
  props: {
  title: { type: String, required: true },
  note: { type: String, default: '' },
  icon: { type: String, default: 'mdi-tune-variant' },
  cardType: { type: String, required: true },
  marker: { type: String, default: '' },
  disabled: { type: Boolean, default: false },
  locked: { type: Boolean, default: false },
  embedded: { type: Boolean, default: false },
},
  setup(__props) {

return (_ctx, _cache) => {
  const _component_VIcon = _resolveComponent$4("VIcon");

  return (_openBlock$s(), _createElementBlock$p("section", {
    class: _normalizeClass$8(["aoa-config-card aoa-design-section-card", [`aoa-config-card--${__props.cardType}`, { 'aoa-surface-card': !__props.embedded, 'aoa-surface-section': !__props.embedded, 'aoa-config-card--locked': __props.locked, 'aoa-config-card--disabled': __props.disabled, 'aoa-config-card--embedded': __props.embedded }]]),
    "data-html-replica-card": __props.embedded ? null : '',
    "data-flat-config-section": __props.embedded ? '' : null,
    "data-section-tone": "neutral",
    "data-cron-card": __props.marker === 'schedule' ? '' : null,
    "data-schedule-card": __props.marker === 'schedule' ? '' : null,
    "data-notify-card": __props.marker === 'notify' ? '' : null
  }, [
    (!__props.embedded)
      ? (_openBlock$s(), _createElementBlock$p("header", _hoisted_2$h, [
          _createElementVNode$c("span", _hoisted_3$c, [
            _createVNode$l(_component_VIcon, {
              icon: __props.icon,
              size: "20"
            }, null, 8, ["icon"])
          ]),
          _createElementVNode$c("div", _hoisted_4$b, [
            _createElementVNode$c("h3", null, _toDisplayString$c(__props.title), 1),
            (__props.note)
              ? (_openBlock$s(), _createElementBlock$p("p", _hoisted_5$9, _toDisplayString$c(__props.note), 1))
              : _createCommentVNode$c("", true)
          ]),
          _createElementVNode$c("span", _hoisted_6$9, [
            _renderSlot$d(_ctx.$slots, "actions")
          ])
        ]))
      : _createCommentVNode$c("", true),
    _renderSlot$d(_ctx.$slots, "default")
  ], 10, _hoisted_1$p))
}
}

};

const {renderSlot:_renderSlot$c,normalizeClass:_normalizeClass$7,withCtx:_withCtx$7,openBlock:_openBlock$r,createBlock:_createBlock$9} = await importShared('vue');


const {computed: computed$m} = await importShared('vue');


const _sfc_main$r = {
  __name: 'ConfigSectionCard',
  props: {
  card: { type: Object, required: true },
  effectiveState: { type: String, default: '' },
  disabled: { type: Boolean, default: false },
  locked: { type: Boolean, default: false },
},
  setup(__props) {

const props = __props;

const cardType = computed$m(() => props.card?.type === 'advanced' ? 'advanced' : 'section');
const tone = computed$m(() => props.card?.danger ? 'danger' : 'neutral');

return (_ctx, _cache) => {
  return (_openBlock$r(), _createBlock$9(_sfc_main$s, {
    class: _normalizeClass$7(["aoa-config-section-card", { 'aoa-design-section-card--danger': tone.value === 'danger' }]),
    title: __props.card.title || '配置项',
    note: __props.card.note || '',
    icon: __props.card.icon || 'mdi-tune-variant',
    "card-type": cardType.value,
    disabled: __props.disabled,
    locked: __props.locked,
    "data-config-section-card": __props.card.type || 'section',
    "data-section-tone": tone.value,
    "data-effective-state": __props.effectiveState || undefined
  }, {
    actions: _withCtx$7(() => [
      _renderSlot$c(_ctx.$slots, "actions")
    ]),
    default: _withCtx$7(() => [
      _renderSlot$c(_ctx.$slots, "default")
    ]),
    _: 3
  }, 8, ["class", "title", "note", "icon", "card-type", "disabled", "locked", "data-config-section-card", "data-section-tone", "data-effective-state"]))
}
}

};

const CONFIG_PAGE_LAYOUT_MODES = Object.freeze({
  SINGLE: 'single',
  CATEGORIZED: 'categorized',
});

const category = (id, title) => Object.freeze({ id, title });
const single = id => Object.freeze({
  id,
  mode: CONFIG_PAGE_LAYOUT_MODES.SINGLE,
  categories: Object.freeze([]),
});
const categorized = (id, categories) => Object.freeze({
  id,
  mode: CONFIG_PAGE_LAYOUT_MODES.CATEGORIZED,
  categories: Object.freeze(categories),
});

const CONFIG_PAGE_LAYOUTS = Object.freeze({
  fusion: single('fusion'),
  server: single('server'),
  subscribe: single('subscribe'),
  sites: single('sites'),
  hc: single('hc'),
  seedremove: single('seedremove'),
  dltagmain: single('dltagmain'),
  logs: single('logs'),
  clean: single('clean'),
  subfill: categorized('subfill', [
    category('subfill_download', '下载完成'),
    category('subfill_category', '二级分类'),
  ]),
  backup: categorized('backup', [
    category('backup', '本地备份'),
    category('backup_webdav', 'WebDAV'),
  ]),
  updates: categorized('updates', [
    category('mp_update', 'MoviePilot'),
    category('plugin_update_reminder', '插件'),
    category('market_update', '插件库'),
  ]),
});

function getConfigPageLayout(pageId) {
  const id = String(pageId || '').trim();
  return CONFIG_PAGE_LAYOUTS[id] || single(id || 'unknown')
}

const {renderSlot:_renderSlot$b,openBlock:_openBlock$q,createElementBlock:_createElementBlock$o,createCommentVNode:_createCommentVNode$b,createElementVNode:_createElementVNode$b,normalizeClass:_normalizeClass$6} = await importShared('vue');


const _hoisted_1$o = ["data-config-page", "data-config-page-mode", "data-config-category-count", "data-config-active-category", "data-effective-state"];
const _hoisted_2$g = {
  key: 0,
  class: "aoa-config-page-surface__categories",
  "data-config-page-categories": "",
  "aria-label": "页面分类"
};
const _hoisted_3$b = {
  class: "aoa-config-page-surface__content",
  "data-config-page-content": ""
};

const {computed: computed$l,useSlots} = await importShared('vue');


const _sfc_main$q = {
  __name: 'ConfigPageSurface',
  props: {
  layout: { type: Object, required: true },
  activeCategory: { type: String, default: '' },
  effectiveState: { type: String, default: '' },
},
  setup(__props) {

const props = __props;

const slots = useSlots();
const categorized = computed$l(() => props.layout?.mode === CONFIG_PAGE_LAYOUT_MODES.CATEGORIZED);
const categories = computed$l(() => Array.isArray(props.layout?.categories) ? props.layout.categories : []);
const hasCategorySlot = computed$l(() => categorized.value && Boolean(slots.categories));

return (_ctx, _cache) => {
  return (_openBlock$q(), _createElementBlock$o("section", {
    class: _normalizeClass$6(["aoa-config-page-surface", `aoa-config-page-surface--${__props.layout.mode}`]),
    "data-config-page-surface": "",
    "data-config-page": __props.layout.id,
    "data-config-page-mode": __props.layout.mode,
    "data-config-category-count": String(categories.value.length),
    "data-config-active-category": categorized.value ? __props.activeCategory : undefined,
    "data-effective-state": __props.effectiveState || undefined
  }, [
    (hasCategorySlot.value)
      ? (_openBlock$q(), _createElementBlock$o("nav", _hoisted_2$g, [
          _renderSlot$b(_ctx.$slots, "categories", {
            categories: categories.value,
            activeCategory: __props.activeCategory
          })
        ]))
      : _createCommentVNode$b("", true),
    _createElementVNode$b("div", _hoisted_3$b, [
      _renderSlot$b(_ctx.$slots, "default")
    ])
  ], 10, _hoisted_1$o))
}
}

};

const {createElementVNode:_createElementVNode$a,normalizeClass:_normalizeClass$5,openBlock:_openBlock$p,createElementBlock:_createElementBlock$n,createCommentVNode:_createCommentVNode$a,resolveComponent:_resolveComponent$3,mergeProps:_mergeProps$5,createBlock:_createBlock$8,toDisplayString:_toDisplayString$b,createTextVNode:_createTextVNode$5,withCtx:_withCtx$6,createVNode:_createVNode$k,createSlots:_createSlots} = await importShared('vue');


const _hoisted_1$n = ["data-control-kind", "data-switch-enabled", "data-multi-select", "data-disabled", "data-invalid", "data-control-state"];
const _hoisted_2$f = ["aria-checked", "aria-label", "aria-describedby", "aria-required", "aria-invalid", "disabled"];
const _hoisted_3$a = { class: "aoa-field-control__selection-count" };
const _hoisted_4$a = {
  key: 0,
  class: "aoa-field-control__selection-count"
};
const _hoisted_5$8 = { class: "aoa-field-control__selection-count" };
const _hoisted_6$8 = {
  key: 0,
  class: "aoa-field-control__selection-count"
};

const {computed: computed$k} = await importShared('vue');



const _sfc_main$p = {
  __name: 'FieldControl',
  props: {
  field: { type: Object, required: true },
  modelValue: { type: null, default: null },
},
  emits: ['update:modelValue'],
  setup(__props, { emit: __emit }) {

const props = __props;

const emit = __emit;

function emitValue(next) {
  let value = next;
  if (control.value === 'number') {
    const parsed = Number(next);
    value = Number.isNaN(parsed) ? null : parsed;
  }
  emit('update:modelValue', value);
}

const normalizedValue = computed$k({
  get: () => props.modelValue,
  set: next => emitValue(next),
});

const control = computed$k(() => props.field.control || 'text');
const isSwitchControl = computed$k(() => control.value === 'switch');
const isMultiControl = computed$k(() => !!(props.field.multiple || props.field.chips || control.value === 'combobox'));
const isFullControl = computed$k(() => !!(props.field.fullRow || isMultiControl.value || control.value === 'textarea'));
const controlState = computed$k(() => {
  if (props.field.error) return 'invalid'
  if (props.field.disabled) return 'disabled'
  if (isSwitchControl.value && normalizedValue.value) return 'active'
  return 'idle'
});
const selectionCount = computed$k(() => Array.isArray(normalizedValue.value) ? normalizedValue.value.length : 0);
const selectionSummary = computed$k(() => (
  selectionCount.value === 0 && props.field.emptySelectionText
    ? props.field.emptySelectionText
    : `已选 ${selectionCount.value} 项`
));
const commonProps = computed$k(() => ({
  label: undefined,
  hint: '',
  persistentHint: false,
  disabled: !!props.field.disabled,
  density: props.field.density || 'comfortable',
  hideDetails: props.field.hideDetails ?? false,
  errorMessages: props.field.error ? [props.field.error] : [],
  'aria-label': props.field.ariaLabel || props.field.label || props.field.key,
  'aria-describedby': props.field.ariaDescribedby || undefined,
  'aria-required': props.field.required ? 'true' : undefined,
  'aria-invalid': props.field.error ? 'true' : undefined,
}));

function selectionTitle(item) {
  return item?.raw?.title ?? item?.raw?.label ?? item?.raw?.name ?? item?.title ?? item?.label ?? item?.name ?? item?.props?.title ?? item?.value ?? item?.key ?? item?.id ?? item
}

function selectionValue(item) {
  return item?.raw?.value ?? item?.raw?.key ?? item?.raw?.id ?? item?.value ?? item?.key ?? item?.id ?? item
}

return (_ctx, _cache) => {
  const _component_VCronField = _resolveComponent$3("VCronField");
  const _component_VChip = _resolveComponent$3("VChip");
  const _component_VSelect = _resolveComponent$3("VSelect");
  const _component_VCombobox = _resolveComponent$3("VCombobox");
  const _component_VTextarea = _resolveComponent$3("VTextarea");
  const _component_VTextField = _resolveComponent$3("VTextField");

  return (_openBlock$p(), _createElementBlock$n("div", {
    class: _normalizeClass$5(["aoa-field-control", {
      'aoa-field-control--switch': isSwitchControl.value,
      'aoa-field-control--switch-on': isSwitchControl.value && !!normalizedValue.value,
      'aoa-field-control--multi': isMultiControl.value,
      'aoa-field-control--full': isFullControl.value,
      'aoa-field-control--disabled': !!__props.field.disabled,
      'aoa-field-control--error': !!__props.field.error,
    }]),
    "data-field-control": "",
    "data-control-kind": control.value,
    "data-switch-enabled": isSwitchControl.value ? (!!normalizedValue.value ? 'true' : 'false') : undefined,
    "data-multi-select": isMultiControl.value ? 'true' : undefined,
    "data-disabled": __props.field.disabled ? 'true' : undefined,
    "data-invalid": __props.field.error ? 'true' : undefined,
    "data-control-state": controlState.value
  }, [
    (control.value === 'switch')
      ? (_openBlock$p(), _createElementBlock$n("button", {
          key: 0,
          type: "button",
          class: _normalizeClass$5(["aoa-toggle-switch", {
        'aoa-toggle-switch--on': !!normalizedValue.value,
        'aoa-toggle-switch--disabled': !!__props.field.disabled,
        'aoa-toggle-switch--invalid': !!__props.field.error,
      }]),
          role: "switch",
          "aria-checked": !!normalizedValue.value,
          "aria-label": __props.field.ariaLabel || __props.field.label || __props.field.key,
          "aria-describedby": __props.field.ariaDescribedby || undefined,
          "aria-required": __props.field.required ? 'true' : undefined,
          "aria-invalid": __props.field.error ? 'true' : undefined,
          disabled: !!__props.field.disabled,
          "data-field-switch": "",
          onClick: _cache[0] || (_cache[0] = $event => (normalizedValue.value = !normalizedValue.value))
        }, [...(_cache[6] || (_cache[6] = [
          _createElementVNode$a("span", {
            class: "aoa-toggle-switch__thumb",
            "aria-hidden": "true"
          }, null, -1)
        ]))], 10, _hoisted_2$f))
      : (control.value === 'cron')
        ? (_openBlock$p(), _createBlock$8(_component_VCronField, _mergeProps$5({
            key: 1,
            modelValue: normalizedValue.value,
            "onUpdate:modelValue": _cache[1] || (_cache[1] = $event => ((normalizedValue).value = $event))
          }, commonProps.value, {
            placeholder: __props.field.placeholder || undefined
          }), null, 16, ["modelValue", "placeholder"]))
        : (control.value === 'select')
          ? (_openBlock$p(), _createBlock$8(_component_VSelect, _mergeProps$5({
              key: 2,
              modelValue: normalizedValue.value,
              "onUpdate:modelValue": _cache[2] || (_cache[2] = $event => ((normalizedValue).value = $event))
            }, commonProps.value, {
              items: __props.field.items || [],
              "item-title": selectionTitle,
              "item-value": selectionValue,
              loading: !!__props.field.loading,
              multiple: !!__props.field.multiple,
              chips: !!__props.field.chips && !__props.field.compactSelection,
              "closable-chips": !!__props.field.closableChips && !__props.field.compactSelection,
              clearable: __props.field.clearable !== false,
              "prepend-inner-icon": __props.field.compactSelection ? undefined : (__props.field.icon || undefined),
              placeholder: __props.field.compactSelection ? undefined : (__props.field.placeholder || undefined)
            }), _createSlots({ _: 2 }, [
              (__props.field.compactSelection && selectionCount.value === 0)
                ? {
                    name: "prepend-inner",
                    fn: _withCtx$6(() => [
                      _createElementVNode$a("span", _hoisted_3$a, _toDisplayString$b(selectionSummary.value), 1)
                    ]),
                    key: "0"
                  }
                : undefined,
              (__props.field.compactSelection)
                ? {
                    name: "selection",
                    fn: _withCtx$6(({ index }) => [
                      (index === 0)
                        ? (_openBlock$p(), _createElementBlock$n("span", _hoisted_4$a, _toDisplayString$b(selectionSummary.value), 1))
                        : _createCommentVNode$a("", true)
                    ]),
                    key: "1"
                  }
                : (__props.field.multiple || __props.field.chips)
                  ? {
                      name: "chip",
                      fn: _withCtx$6(({ item, props: chipProps }) => [
                        _createVNode$k(_component_VChip, _mergeProps$5(chipProps, {
                          class: "aoa-field-control__chip",
                          variant: "tonal"
                        }), {
                          default: _withCtx$6(() => [
                            _createTextVNode$5(_toDisplayString$b(selectionTitle(item)), 1)
                          ]),
                          _: 2
                        }, 1040)
                      ]),
                      key: "2"
                    }
                  : undefined
            ]), 1040, ["modelValue", "items", "loading", "multiple", "chips", "closable-chips", "clearable", "prepend-inner-icon", "placeholder"]))
          : (control.value === 'combobox')
            ? (_openBlock$p(), _createBlock$8(_component_VCombobox, _mergeProps$5({
                key: 3,
                modelValue: normalizedValue.value,
                "onUpdate:modelValue": _cache[3] || (_cache[3] = $event => ((normalizedValue).value = $event))
              }, commonProps.value, {
                items: __props.field.items || [],
                "item-title": selectionTitle,
                "item-value": selectionValue,
                multiple: !!__props.field.multiple,
                chips: !!__props.field.chips && !__props.field.compactSelection,
                "closable-chips": !!__props.field.closableChips && !__props.field.compactSelection,
                clearable: __props.field.clearable !== false,
                "prepend-inner-icon": __props.field.compactSelection ? undefined : (__props.field.icon || undefined),
                placeholder: __props.field.compactSelection ? undefined : (__props.field.placeholder || '输入后按回车添加')
              }), _createSlots({ _: 2 }, [
                (__props.field.compactSelection && selectionCount.value === 0)
                  ? {
                      name: "prepend-inner",
                      fn: _withCtx$6(() => [
                        _createElementVNode$a("span", _hoisted_5$8, _toDisplayString$b(selectionSummary.value), 1)
                      ]),
                      key: "0"
                    }
                  : undefined,
                (__props.field.compactSelection)
                  ? {
                      name: "selection",
                      fn: _withCtx$6(({ index }) => [
                        (index === 0)
                          ? (_openBlock$p(), _createElementBlock$n("span", _hoisted_6$8, _toDisplayString$b(selectionSummary.value), 1))
                          : _createCommentVNode$a("", true)
                      ]),
                      key: "1"
                    }
                  : {
                      name: "chip",
                      fn: _withCtx$6(({ item, props: chipProps }) => [
                        _createVNode$k(_component_VChip, _mergeProps$5(chipProps, {
                          class: "aoa-field-control__chip",
                          variant: "tonal"
                        }), {
                          default: _withCtx$6(() => [
                            _createTextVNode$5(_toDisplayString$b(selectionTitle(item)), 1)
                          ]),
                          _: 2
                        }, 1040)
                      ]),
                      key: "2"
                    }
              ]), 1040, ["modelValue", "items", "multiple", "chips", "closable-chips", "clearable", "prepend-inner-icon", "placeholder"]))
            : (control.value === 'textarea')
              ? (_openBlock$p(), _createBlock$8(_component_VTextarea, _mergeProps$5({
                  key: 4,
                  modelValue: normalizedValue.value,
                  "onUpdate:modelValue": _cache[4] || (_cache[4] = $event => ((normalizedValue).value = $event))
                }, commonProps.value, {
                  placeholder: __props.field.placeholder || undefined,
                  "prepend-inner-icon": __props.field.icon || undefined,
                  rows: __props.field.rows || 3,
                  "auto-grow": ""
                }), null, 16, ["modelValue", "placeholder", "prepend-inner-icon", "rows"]))
              : (_openBlock$p(), _createBlock$8(_component_VTextField, _mergeProps$5({
                  key: 5,
                  modelValue: normalizedValue.value,
                  "onUpdate:modelValue": _cache[5] || (_cache[5] = $event => ((normalizedValue).value = $event))
                }, commonProps.value, {
                  type: control.value === 'number' ? 'number' : (__props.field.sensitive ? 'password' : 'text'),
                  "prepend-inner-icon": __props.field.icon || undefined,
                  suffix: __props.field.suffix || undefined,
                  min: __props.field.min ?? undefined,
                  max: __props.field.max ?? undefined,
                  placeholder: __props.field.placeholder || undefined
                }), null, 16, ["modelValue", "type", "prepend-inner-icon", "suffix", "min", "max", "placeholder"]))
  ], 10, _hoisted_1$n))
}
}

};

const schemaByKey = new Map(configSchemaFields.map(field => [field.key, field]));

const auditedCompactSelectionFieldKeys = Object.freeze([
  'health_check_database_targets',
  'health_check_directory_targets',
  'health_check_items',
  'health_check_storage_targets',
  'log_clean_selected_ids',
  'market_update_exclude_ids',
  'market_update_install_ids',
  'plugin_auto_install_exclude_ids',
  'plugin_auto_install_install_ids',
  'mp_update_types',
  'msgnotify_servers',
  'msgnotify_types',
  'plugin_uninstall_ids',
  'seedclean_downloaders',
  'subfill_details',
  'subscribe_reminder_subtype',
  'dltag_downloaders',
  'dltag_tasks',
]);

const auditedCompactSelectionFieldKeySet = new Set(auditedCompactSelectionFieldKeys);

const fullRowReplicaFieldKeys = Object.freeze([
  'plugin_uninstall_ids',
]);

const fullRowReplicaFieldKeySet = new Set(fullRowReplicaFieldKeys);

function isReplicaFullRowField(fieldOrKey) {
  const key = typeof fieldOrKey === 'string' ? fieldOrKey : fieldOrKey?.key;
  return fullRowReplicaFieldKeySet.has(key)
}

const compactSelectionEmptyText = Object.freeze({
  seedclean_downloaders: '全部可用',
  dltag_downloaders: '全部可用',
});

function isReplicaFieldVisible(field, values = {}) {
  return isConfigFieldVisible(field, values)
}

/**
 * Resolve the renderable field list in the only supported order:
 * visibility first, disabled state second. Hidden fields are omitted from the
 * DOM only; their values stay in the shared form and therefore remain part of
 * the existing save payload contract.
 */
function resolveReplicaFields(fields = [], values = {}, resolveDisabled = null) {
  return (Array.isArray(fields) ? fields : []).flatMap((field) => {
    if (!isReplicaFieldVisible(field, values)) return []
    const resolvedDisabled = typeof resolveDisabled === 'function'
      ? resolveDisabled(field, values)
      : field?.disabled;
    return [{
      ...field,
      disabled: Boolean(field?.disabled || resolvedDisabled),
    }]
  })
}

// Hero / subtab masters own the authority switches.  Update entry cards own
// the two main switches; legacy schedule flags remain persisted only for
// migration and must not reappear as a second visible switch.
const heroManagedReplicaFieldKeys = Object.freeze({
  fusion: Object.freeze(['fusion_notify_enabled']),
  server: Object.freeze(['msgnotify_enabled']),
  subscribe: Object.freeze(['subscribe_reminder_enabled', 'subscribe_reminder_schedule_enabled']),
  sites: Object.freeze(['site_stat_enabled', 'site_stat_schedule_enabled']),
  hc: Object.freeze(['health_check_enabled', 'health_check_schedule_enabled']),
  seedremove: Object.freeze(['seedclean_enabled', 'seedclean_schedule_enabled']),
  dltagmain: Object.freeze(['dltag_enabled']),
  subfill: Object.freeze([]),
  backup: Object.freeze(['backup_enabled', 'backup_webdav_enabled']),
  logs: Object.freeze(['log_clean_enabled', 'log_clean_schedule_enabled']),
  updates: Object.freeze([
    'mp_update_enabled',
    'plugin_update_reminder_enabled',
    'market_update_enabled',
  ]),
});

const shellManagedReplicaFieldKeys = Object.freeze(['enabled']);
const actionManagedReplicaFieldKeys = Object.freeze([]);

const sharedCardOwnership = Object.freeze({
  fusion: Object.freeze({
    schedule: Object.freeze({ title: '刷新计划', note: '使用 Cron 控制活动卡片的数据刷新频率。', masterKey: 'fusion_notify_enabled', fusionDailyCard: true }),
    notify: Object.freeze({ title: '融合通知渠道', note: '统一卡片通过 MoviePilot 通知渠道发送。', masterKey: 'fusion_notify_enabled' }),
  }),
  server: Object.freeze({
    notify: Object.freeze({ title: '媒体通知', note: '选择事件、媒体服务器与投递消息类型。', masterKey: 'msgnotify_enabled', fusionManaged: true, fusionChannelOnly: true }),
  }),
  subscribe: Object.freeze({
    schedule: Object.freeze({ title: '订阅检查计划', note: '按 Cron 检查订阅更新并生成提醒。', masterKey: 'subscribe_reminder_enabled', scheduleKey: 'subscribe_reminder_schedule_enabled' }),
    notify: Object.freeze({ title: '订阅提醒通知', note: '设置订阅检查结果的投递类型。', masterKey: 'subscribe_reminder_enabled', fusionManaged: true, fusionChannelOnly: true }),
  }),
  sites: Object.freeze({
    schedule: Object.freeze({ title: '站点统计计划', note: '按 Cron 自动刷新站点上传与下载统计。', masterKey: 'site_stat_enabled', scheduleKey: 'site_stat_schedule_enabled' }),
    notify: Object.freeze({ title: '站点统计通知', note: '只通知定时统计结果；手动统计不发送。', masterKey: 'site_stat_enabled', resultKey: 'site_stat_schedule_notify_enabled', fusionManaged: true, fusionChannelOnly: true }),
  }),
  hc: Object.freeze({
    schedule: Object.freeze({ title: '健康巡检计划', note: '按 Cron 定时巡查数据库、存储和目录。', masterKey: 'health_check_enabled', scheduleKey: 'health_check_schedule_enabled' }),
    notify: Object.freeze({ title: '健康巡检通知', note: '异常通知与正常完成通知分开控制；一次巡检最多发送一份结果。', masterKey: 'health_check_enabled', resultKeys: Object.freeze(['health_check_notify', 'health_check_completion_notify_enabled']), preserveFieldOrder: true, fusionManaged: true, fusionChannelOnly: true }),
  }),
  seedremove: Object.freeze({
    schedule: Object.freeze({ title: '自动删种计划', note: '按 Cron 定时检查并处理匹配的下载任务。', masterKey: 'seedclean_enabled', scheduleKey: 'seedclean_schedule_enabled' }),
  }),
  dltagmain: Object.freeze({
    notify: Object.freeze({ title: '定时执行通知', note: '只设置 Cron 执行结果的通知方式。', masterKey: 'dltag_enabled', resultKey: 'dltag_scheduled_notify', fusionManaged: true, fusionChannelOnly: true }),
  }),
  backup: Object.freeze({
    notify: Object.freeze({ title: '定时执行通知', note: '只设置 Cron 执行后的通知方式。', masterKey: 'backup_enabled', resultKey: 'backup_notify', fusionManaged: true, fusionChannelOnly: true }),
  }),
  logs: Object.freeze({
    schedule: Object.freeze({ title: '日志清理计划', note: '按 Cron 定时裁剪插件日志。', masterKey: 'log_clean_enabled', scheduleKey: 'log_clean_schedule_enabled' }),
    notify: Object.freeze({ title: '定时执行通知', note: '只设置 Cron 执行后的通知方式。', masterKey: 'log_clean_enabled', resultKey: 'log_clean_notify', fusionManaged: true, fusionChannelOnly: true }),
  }),
  updates: Object.freeze({}),
  subfill: Object.freeze({
    notify: Object.freeze({ title: '填充完成通知', note: '只有实际发生字段变更时通知，沿用插件默认通知类型。', resultKey: 'subfill_completion_notify_enabled', fusionManaged: true, fusionChannelOnly: true }),
  }),
});

function schemaFieldPresentation(field) {
  const isArray = field.type === 'array' || field.dataType === 'array';
  const compactMulti = isArray && auditedCompactSelectionFieldKeySet.has(field.key);
  return {
    key: field.key,
    cardType: field.cardType || 'feature',
    icon: field.cardType === 'notify' ? 'mdi-bell-outline' : (field.cardType === 'cron' ? 'mdi-calendar-clock' : 'mdi-cog-outline'),
    label: field.label || field.key,
    sensitive: /(?:password|token|secret)/i.test(field.key),
    multiple: isArray,
    chips: isArray,
    compactSelection: compactMulti,
    compactMulti,
    fullRow: isReplicaFullRowField(field),
    retainInCard: field.key === 'backup_cron' || field.retainInCard === true,
  }
}

function isSettingsCard(card) {
  return !!card && card.type !== 'actions'
}

function cardMatchesType(card, cardType) {
  const title = card?.title || '';
  const keys = (card?.fields || []).map(field => field?.key || '');
  if (cardType === 'advanced') return card?.type === 'advanced'
  if (cardType === 'cron') {
    return /定时|计划|执行|巡检|备份|清理|更新|生命周期|规则/.test(title)
      || keys.some(key => /(?:cron|schedule|time)$/i.test(key) || /_(?:cron|schedule|time)\b/i.test(key))
  }
  if (cardType === 'notify') {
    return /通知|消息|渠道/.test(title)
      || keys.some(key => /notify|msgtype|msg_type/i.test(key))
  }
  return card?.type === 'section' || card?.type === 'advanced'
}

function pickPrimaryCard(cards, cardType) {
  const settings = (cards || []).filter(isSettingsCard);
  if (!settings.length) return null
  return settings.find(card => cardMatchesType(card, cardType))
    || settings.find(card => card.type === 'section')
    || settings.find(card => card.type === 'advanced')
    || settings[0]
}

/**
 * 将尚未在手工卡片中出现的可见 schema 字段并入既有主卡。
 *
 * schema 保持字段覆盖唯一真源；不再创建「…补充/…补全」独立卡片岛。
 */
function completeReplicaCards(cardsBySubtab) {
  const completed = Object.fromEntries(Object.entries(cardsBySubtab).map(([subtab, cards]) => [
    subtab,
    (cards || []).map(card => ({ ...card, fields: Array.isArray(card.fields) ? [...card.fields] : card.fields })),
  ]));
  const existingKeys = new Set(Object.values(completed)
    .flatMap(cards => cards || [])
    .flatMap(card => [
      ...(card.fields || []).map(field => field?.key),
      card.masterKey,
    ])
    .filter(Boolean));

  for (const field of configSchemaFields) {
    const isHeroManaged = heroManagedReplicaFieldKeys[field.subtab]?.includes(field.key);
    const isShellManaged = shellManagedReplicaFieldKeys.includes(field.key);
    const isActionManaged = actionManagedReplicaFieldKeys.includes(field.key);
    if (field.isDisplayed === false || isHeroManaged || isShellManaged || isActionManaged || existingKeys.has(field.key)) continue
    if (!completed[field.subtab]) completed[field.subtab] = [];
    const cards = completed[field.subtab];
    const moduleCards = field.module ? cards.filter(card => card.module === field.module) : [];
    let target = pickPrimaryCard(moduleCards.length ? moduleCards : cards, field.cardType);
    if (!target) {
      // Fallback only when a subtab has no settings card yet; keep a neutral title
      // so schema coverage never revives independent supplemental islands.
      target = {
        type: field.cardType === 'advanced' ? 'advanced' : 'section',
        icon: field.cardType === 'notify' ? 'mdi-bell-outline' : (field.cardType === 'cron' ? 'mdi-calendar-clock' : 'mdi-cog-outline'),
        title: '配置项',
        note: '插件持久化配置。',
        grid: field.cardType === 'advanced' ? 'grid-2' : 'grid-3',
        fields: [],
      };
      cards.push(target);
    }
    if (!Array.isArray(target.fields)) target.fields = [];
    target.fields.push(schemaFieldPresentation(field));
    existingKeys.add(field.key);
  }
  return completed
}

function bindField(field, subtab, itemSources) {
  const key = field?.key;
  if (!key) throw new Error(`Replica field is missing a backend config key in subtab: ${subtab}`)
  const schema = schemaByKey.get(key);
  if (!schema) throw new Error(`Replica field key is missing from config schema: ${key}`)
  if (schema.subtab !== subtab) {
    throw new Error(`Replica field subtab mismatch for ${key}: visual ${subtab}, schema ${schema.subtab}`)
  }
  const itemSource = schema.itemSource || '';
  if (itemSource && !Object.prototype.hasOwnProperty.call(itemSources, itemSource)) {
    throw new Error(`Replica field item source is not registered for ${key}: ${itemSource}`)
  }
  const items = itemSource ? itemSources[itemSource] : (schema.items || []);
  const isArray = field.multiple || field.chips || schema.type === 'array' || schema.dataType === 'array';
  const control = itemSource ? 'select' : (isArray ? 'combobox' : (schema.control || 'text'));
  const compactMulti = Boolean(isArray && (
    auditedCompactSelectionFieldKeySet.has(key)
    || field.compactMulti
    || field.compactSelection
  ));
  // Full-row presentation is a deliberately tiny product contract. Field
  // type, option count and local component hints must not silently widen a
  // setting; the plugin uninstall target selector is the sole exception.
  const fullRow = isReplicaFullRowField(key);
  return {
    ...field,
    cardType: schema.cardType || field.cardType || 'feature',
    control,
    items,
    multiple: isArray,
    chips: isArray,
    closableChips: isArray,
    compactSelection: compactMulti,
    compactMulti,
    emptySelectionText: compactSelectionEmptyText[key] || '',
    clearable: true,
    fullRow,
  }
}

function bindReplicaCards(cardsBySubtab, itemSources = {}) {
  return Object.fromEntries(Object.entries(cardsBySubtab).map(([subtab, cards]) => {
    const boundCards = (cards || []).map(card => {
      if (!Array.isArray(card.fields)) return card
      const fields = card.fields.map(field => bindField(field, subtab, itemSources));
      return { ...card, fields }
    });
    return [subtab, boundCards]
  }))
}

function uniqueFields(fields) {
  const keys = new Set();
  return fields.filter((field) => {
    if (!field?.key || keys.has(field.key)) return false
    keys.add(field.key);
    return true
  })
}

function sharedCard(type, fields, ownership = {}) {
  return {
    type,
    icon: type === 'schedule' ? 'mdi-calendar-clock' : 'mdi-bell-outline',
    title: ownership.title || (type === 'schedule' ? '执行计划' : '结果通知'),
    note: ownership.note || '',
    fields,
    ...ownership,
  }
}

function composeSharedReplicaCards(cardsBySubtab) {
  return Object.fromEntries(Object.entries(cardsBySubtab).map(([subtab, cards]) => {
    // Update management deliberately keeps its selector cards and one in-flow
    // detail card; the generic shared-card composer would drop selector cards
    // because they have no fields of their own.
    // Automatic backup follows the same selector/detail composition. Remote
    // WebDAV is a dependent destination with its own switch, not a second Cron.
    // Subscription fill also keeps its selector/detail composition. The same
    // persisted completion switch is rendered inside whichever task detail is
    // active, so it must not be extracted into a standalone notification card.
    if (subtab === 'updates' || subtab === 'backup' || subtab === 'subfill') {
      const settings = (cards || []).filter(card => card.type !== 'actions');
      const actions = (cards || []).filter(card => card.type === 'actions');
      return [subtab, [...settings, ...actions]]
    }
    const isSharedScheduleField = field => subtab !== 'updates' && field.cardType === 'cron' && !field.retainInCard;
    const isSharedNotifyField = field => subtab !== 'updates' && field.cardType === 'notify' && !field.retainInCard;
    const actions = (cards || []).filter(card => card.type === 'actions');
    const settings = (cards || []).filter(card => card.type !== 'actions');
    const sourceModuleCards = settings.filter(card => card.type === 'module');
    const moduleNotifyFields = sourceModuleCards.flatMap(card => (
      card.fields || []
    ).filter(isSharedNotifyField));
    const moduleCards = sourceModuleCards
      .map(card => ({
        ...card,
        fields: (card.fields || []).filter(field => !isSharedNotifyField(field)),
      }))
      .filter(card => card.fields.length > 0 || (card.actions || []).length > 0);
    const sharedSettings = settings.filter(card => card.type !== 'module');
    const allFields = sharedSettings.flatMap(card => card.fields || []);
    const scheduleFields = uniqueFields(allFields.filter(isSharedScheduleField));
    const notifyFields = uniqueFields([
      ...allFields.filter(isSharedNotifyField),
      ...moduleNotifyFields,
    ]);
    // Fusion's message type belongs to the same daily-card workflow as the
    // create/refresh times. Keep it in that card so its vertical spacing is
    // controlled locally instead of creating a second notification card.
    const fusionDailyNotifyFields = subtab === 'fusion'
      ? notifyFields.filter(field => field.key === 'fusion_notify_msgtype')
      : [];
    const remainingNotifyFields = notifyFields.filter(field => !fusionDailyNotifyFields.includes(field));
    scheduleFields.push(...fusionDailyNotifyFields);
    const remainingCards = sharedSettings
      .map(card => ({
        ...card,
        fields: (card.fields || []).filter(field => !isSharedScheduleField(field) && !isSharedNotifyField(field)),
      }))
      .filter(card => card.fields.length > 0 || card.previewKey || (card.actions || []).length > 0);
    const ownership = sharedCardOwnership[subtab] || {};
    const composed = [...moduleCards];
    if (scheduleFields.length) composed.push(sharedCard('schedule', scheduleFields, ownership.schedule));
    composed.push(...remainingCards);
    const notifyGroups = ownership.notifyGroups || (ownership.notify ? [ownership.notify] : []);
    const claimedNotifyKeys = new Set();
    for (const notifyOwner of notifyGroups) {
      const groupedFields = remainingNotifyFields.filter(field => {
        const module = schemaByKey.get(field.key)?.module || '';
        const matches = !notifyOwner.module || notifyOwner.module === module;
        if (matches) claimedNotifyKeys.add(field.key);
        return matches
      });
      const resultKeys = new Set([
        notifyOwner.resultKey,
        ...(notifyOwner.resultKeys || []),
      ].filter(Boolean));
      const orderedFields = notifyOwner.preserveFieldOrder
        ? groupedFields
        : resultKeys.size
        ? [
            ...groupedFields.filter(field => resultKeys.has(field.key)),
            ...groupedFields.filter(field => !resultKeys.has(field.key)),
          ]
        : groupedFields;
      if (orderedFields.length) composed.push(sharedCard('notify', orderedFields, notifyOwner));
    }
    const unclaimedNotifyFields = remainingNotifyFields.filter(field => !claimedNotifyKeys.has(field.key));
    if (unclaimedNotifyFields.length) composed.push(sharedCard('notify', unclaimedNotifyFields, ownership.notify));
    composed.push(...actions);
    return [subtab, composed]
  }))
}

function updateReplicaFieldValue(form, field, value) {
  if (!field?.key) throw new Error('Replica field update requires a backend config key')
  if (field.key === 'plugin_auto_install_scope_mode') {
    const mode = normalizeConfigOption(
      String(value || '').toLowerCase(),
      pluginAutoInstallScopeValues,
      defaults.plugin_auto_install_scope_mode,
    );
    form[field.key] = mode;
    return mode
  }
  form[field.key] = value;
  return value
}

function createReplicaFieldControlProps(form, field) {
  if (!field?.key) throw new Error('Replica field control props require a backend config key')
  return {
    field,
    modelValue: form[field.key],
    'onUpdate:modelValue': value => updateReplicaFieldValue(form, field, value),
  }
}

const {resolveComponent:_resolveComponent$2,openBlock:_openBlock$o,createBlock:_createBlock$7,createCommentVNode:_createCommentVNode$9,toDisplayString:_toDisplayString$a,createTextVNode:_createTextVNode$4,Fragment:_Fragment$5,createElementBlock:_createElementBlock$m,createElementVNode:_createElementVNode$9,normalizeClass:_normalizeClass$4,createVNode:_createVNode$j} = await importShared('vue');


const _hoisted_1$m = ["data-field-key", "data-field-control", "data-control-kind", "data-switch-row", "data-full-row", "data-multi-select-row", "data-has-control-hint", "data-required", "data-invalid", "data-disabled", "data-field-state", "aria-disabled"];
const _hoisted_2$e = { class: "aoa-field-row__label-text" };
const _hoisted_3$9 = {
  key: 1,
  class: "aoa-field-row__required",
  "aria-hidden": "true"
};
const _hoisted_4$9 = ["id"];
const _hoisted_5$7 = ["id"];
const _hoisted_6$7 = { class: "aoa-field-row__control" };
const _hoisted_7$5 = ["id"];

const {computed: computed$j} = await importShared('vue');


const _sfc_main$o = {
  __name: 'FieldRow',
  props: {
  field: { type: Object, required: true },
  modelValue: { type: null, default: null },
},
  emits: ['update:modelValue'],
  setup(__props) {

const props = __props;



const control = computed$j(() => props.field.control || 'text');
const isSwitch = computed$j(() => control.value === 'switch');
const isMulti = computed$j(() => !!(props.field.multiple || props.field.chips || control.value === 'combobox'));
const isCompactMulti = computed$j(() => !!(props.field.compactMulti && isMulti.value));
const isFullRow = computed$j(() => isReplicaFullRowField(props.field));
const fieldState = computed$j(() => {
  if (props.field.error) return 'invalid'
  if (props.field.disabled) return 'disabled'
  if (isSwitch.value && props.modelValue) return 'active'
  return 'idle'
});
const fieldId = computed$j(() => String(props.field.key || 'field').replace(/[^a-zA-Z0-9_-]/g, '-'));
const hintId = computed$j(() => props.field.hint ? `aoa-field-hint-${fieldId.value}` : undefined);
const errorId = computed$j(() => props.field.error ? `aoa-field-error-${fieldId.value}` : undefined);
const controlHint = computed$j(() => String(props.field.controlHint || '').trim());
const controlHintId = computed$j(() => controlHint.value
  ? `aoa-field-control-hint-${fieldId.value}`
  : undefined);
const describedBy = computed$j(() => [
  props.field.ariaDescribedby,
  hintId.value,
  errorId.value,
  controlHintId.value,
].filter(Boolean).join(' ') || undefined);
const controlField = computed$j(() => ({
  ...props.field,
  icon: undefined,
  label: '',
  hint: '',
  hideDetails: true,
  ariaLabel: props.field.ariaLabel || props.field.label || props.field.key,
  ariaDescribedby: describedBy.value,
}));
const rowClasses = computed$j(() => ({
  'aoa-field-row--disabled': !!props.field.disabled,
  'aoa-field-row--error': !!props.field.error,
  'aoa-field-row--switch': isSwitch.value,
  'aoa-field-row--switch-on': isSwitch.value && !!props.modelValue,
  'aoa-field-row--multi': isMulti.value && !isCompactMulti.value,
  'aoa-field-row--compact-multi': isCompactMulti.value,
  'aoa-field-row--control-full': isFullRow.value,
  'aoa-field-row--with-control-hint': !!controlHint.value,
  'aoa-field-row--required': !!props.field.required,
}));

return (_ctx, _cache) => {
  const _component_VIcon = _resolveComponent$2("VIcon");

  return (_openBlock$o(), _createElementBlock$m("div", {
    class: _normalizeClass$4(["aoa-field-row", [`aoa-field-row--${__props.field.control || 'text'}`, rowClasses.value]]),
    "data-field-row": "",
    "data-html-field": "",
    "data-field-key": __props.field.key,
    "data-field-control": __props.field.control || 'text',
    "data-control-kind": __props.field.control || 'text',
    "data-switch-row": isSwitch.value ? 'true' : undefined,
    "data-full-row": isFullRow.value ? 'true' : undefined,
    "data-multi-select-row": isMulti.value ? 'true' : undefined,
    "data-has-control-hint": controlHint.value ? 'true' : undefined,
    "data-required": __props.field.required ? 'true' : undefined,
    "data-invalid": __props.field.error ? 'true' : undefined,
    "data-disabled": __props.field.disabled ? 'true' : undefined,
    "data-field-state": fieldState.value,
    "aria-disabled": __props.field.disabled ? 'true' : 'false'
  }, [
    _createElementVNode$9("div", {
      class: _normalizeClass$4(["aoa-field-row__label", { 'aoa-field-row__label--with-icon': !!__props.field.icon }])
    }, [
      (__props.field.icon)
        ? (_openBlock$o(), _createBlock$7(_component_VIcon, {
            key: 0,
            class: "aoa-field-row__icon",
            icon: __props.field.icon,
            size: "16",
            "aria-hidden": "true"
          }, null, 8, ["icon"]))
        : _createCommentVNode$9("", true),
      _createElementVNode$9("span", _hoisted_2$e, [
        _createTextVNode$4(_toDisplayString$a(__props.field.label), 1),
        (__props.field.compactSelection)
          ? (_openBlock$o(), _createElementBlock$m(_Fragment$5, { key: 0 }, [
              _createTextVNode$4("：")
            ], 64))
          : _createCommentVNode$9("", true),
        (__props.field.required)
          ? (_openBlock$o(), _createElementBlock$m("span", _hoisted_3$9, "*"))
          : _createCommentVNode$9("", true)
      ]),
      (__props.field.hint)
        ? (_openBlock$o(), _createElementBlock$m("small", {
            key: 1,
            id: hintId.value,
            class: "aoa-field-row__hint"
          }, _toDisplayString$a(__props.field.hint), 9, _hoisted_4$9))
        : _createCommentVNode$9("", true),
      (__props.field.error)
        ? (_openBlock$o(), _createElementBlock$m("small", {
            key: 2,
            id: errorId.value,
            class: "aoa-field-row__error",
            role: "alert",
            "aria-live": "polite"
          }, _toDisplayString$a(__props.field.error), 9, _hoisted_5$7))
        : _createCommentVNode$9("", true)
    ], 2),
    _createElementVNode$9("div", _hoisted_6$7, [
      _createVNode$j(_sfc_main$p, {
        field: controlField.value,
        "model-value": __props.modelValue,
        "onUpdate:modelValue": _cache[0] || (_cache[0] = value => _ctx.$emit('update:modelValue', value))
      }, null, 8, ["field", "model-value"]),
      (controlHint.value)
        ? (_openBlock$o(), _createElementBlock$m("small", {
            key: 0,
            id: controlHintId.value,
            class: "aoa-field-row__control-hint",
            "data-field-control-hint": ""
          }, _toDisplayString$a(controlHint.value), 9, _hoisted_7$5))
        : _createCommentVNode$9("", true)
    ])
  ], 10, _hoisted_1$m))
}
}

};

const {mergeProps:_mergeProps$4,openBlock:_openBlock$n,createBlock:_createBlock$6} = await importShared('vue');


const _sfc_main$n = /*@__PURE__*/Object.assign({
  inheritAttrs: false,
}, {
  __name: 'ConfigFieldRow',
  props: {
  field: { type: Object, required: true },
  modelValue: { type: null, default: null },
},
  emits: ['update:modelValue'],
  setup(__props) {







return (_ctx, _cache) => {
  return (_openBlock$n(), _createBlock$6(_sfc_main$o, _mergeProps$4(_ctx.$attrs, {
    class: "aoa-config-field-row",
    "data-config-field-row": "",
    field: __props.field,
    "model-value": __props.modelValue,
    "onUpdate:modelValue": _cache[0] || (_cache[0] = value => _ctx.$emit('update:modelValue', value))
  }), null, 16, ["field", "model-value"]))
}
}

});

const {renderList:_renderList$4,Fragment:_Fragment$4,openBlock:_openBlock$m,createElementBlock:_createElementBlock$l,toDisplayString:_toDisplayString$9,createCommentVNode:_createCommentVNode$8,mergeProps:_mergeProps$3,createVNode:_createVNode$i,normalizeClass:_normalizeClass$3} = await importShared('vue');


const _hoisted_1$l = ["data-config-visible-field-count"];
const _hoisted_2$d = ["data-field-group-heading"];

const {computed: computed$i} = await importShared('vue');


const _sfc_main$m = {
  __name: 'ConfigFieldGrid',
  props: {
  fields: { type: Array, default: () => [] },
  form: { type: Object, required: true },
  grid: { type: String, default: 'grid-2' },
  activeSub: { type: String, default: '' },
  fieldDefaults: { type: Object, default: () => ({}) },
  resolveDisabled: { type: Function, default: null },
  rowAttrs: { type: Function, default: null },
},
  setup(__props) {

const props = __props;

const visibleFields = computed$i(() => resolveReplicaFields(
  props.fields.map(field => ({ ...props.fieldDefaults, ...field })),
  props.form,
  props.resolveDisabled,
));

function fieldProps(field) {
  return createReplicaFieldControlProps(props.form, field)
}

function fieldRowAttrs(field, index) {
  return props.rowAttrs?.(field, index) || {}
}

return (_ctx, _cache) => {
  return (_openBlock$m(), _createElementBlock$l("div", {
    class: _normalizeClass$3(["aoa-config-field-grid aoa-design-field-grid", `aoa-design-field-grid--${__props.grid}`]),
    "data-config-field-grid": "",
    "data-config-visible-field-count": String(visibleFields.value.length)
  }, [
    (_openBlock$m(true), _createElementBlock$l(_Fragment$4, null, _renderList$4(visibleFields.value, (field, index) => {
      return (_openBlock$m(), _createElementBlock$l(_Fragment$4, {
        key: field.key
      }, [
        (field.groupLabel)
          ? (_openBlock$m(), _createElementBlock$l("h4", {
              key: 0,
              class: "aoa-config-field-group",
              "data-field-group-heading": field.layoutGroup || field.key
            }, _toDisplayString$9(field.groupLabel), 9, _hoisted_2$d))
          : _createCommentVNode$8("", true),
        _createVNode$i(_sfc_main$n, _mergeProps$3({ ref_for: true }, { ...fieldProps(field), ...fieldRowAttrs(field, index) }, {
          "data-field-layout-group": field.layoutGroup || undefined,
          "data-field-layout-group-start": field.layoutGroupStart ? 'true' : undefined,
          "data-notify-channel": field.key?.endsWith('_notify_type') || field.key === 'subscribe_reminder_msgtype' ? '' : undefined,
          "data-subfill-inline-notify": __props.activeSub === 'subfill' && field.key === 'subfill_completion_notify_enabled' ? '' : undefined
        }), null, 16, ["data-field-layout-group", "data-field-layout-group-start", "data-notify-channel", "data-subfill-inline-notify"])
      ], 64))
    }), 128))
  ], 10, _hoisted_1$l))
}
}

};

const {createVNode:_createVNode$h,openBlock:_openBlock$l,createElementBlock:_createElementBlock$k} = await importShared('vue');


const _hoisted_1$k = ["data-effective-state"];

const {computed: computed$h} = await importShared('vue');


const _sfc_main$l = {
  __name: 'FusionScheduleSection',
  props: {
  form: { type: Object, required: true },
  fields: { type: Array, default: () => [] },
  notificationTypeItems: { type: Array, default: () => [] },
  effectiveState: { type: String, default: '' },
},
  setup(__props) {

const props = __props;

const fieldsByKey = computed$h(() => new Map(props.fields.map(field => [field.key, field])));
const fieldFor = (key, fallback) => fieldsByKey.value.get(key) || fallback;
const fusionFields = computed$h(() => [
  fieldFor('fusion_card_create_cron', {
    key: 'fusion_card_create_cron',
    control: 'cron',
    icon: 'mdi-plus-circle-outline',
    label: '建卡时间',
  }),
  fieldFor('fusion_card_refresh_cron', {
    key: 'fusion_card_refresh_cron',
    control: 'cron',
    icon: 'mdi-calendar-clock',
    label: '刷新时间',
  }),
  fieldFor('fusion_notify_msgtype', {
    key: 'fusion_notify_msgtype',
    control: 'select',
    icon: 'mdi-email-outline',
    label: '消息类型',
    items: props.notificationTypeItems,
  }),
].map(field => ({
  ...field,
  items: field.key === 'fusion_notify_msgtype'
    ? (field.items?.length ? field.items : props.notificationTypeItems)
    : field.items,
})));

function resolveDisabled(field) {
  return Boolean(
    field.disabled
    || !props.form.fusion_notify_enabled
    || props.effectiveState === 'plugin_disabled'
  )
}

return (_ctx, _cache) => {
  return (_openBlock$l(), _createElementBlock$k("div", {
    class: "aoa-fusion-schedule-grid",
    "data-fusion-schedule-section": "",
    "data-effective-state": __props.effectiveState || undefined,
    role: "group",
    "aria-label": "融合卡片调度与通知渠道"
  }, [
    _createVNode$h(_sfc_main$m, {
      fields: fusionFields.value,
      form: __props.form,
      grid: "grid-2",
      "resolve-disabled": resolveDisabled
    }, null, 8, ["fields", "form"])
  ], 8, _hoisted_1$k))
}
}

};

const {createVNode:_createVNode$g,toDisplayString:_toDisplayString$8,createElementVNode:_createElementVNode$8,openBlock:_openBlock$k,createElementBlock:_createElementBlock$j,createCommentVNode:_createCommentVNode$7,renderSlot:_renderSlot$a} = await importShared('vue');


const _hoisted_1$j = ["data-fusion-enabled", "data-effective-state"];
const _hoisted_2$c = {
  class: "aoa-fusion-operation-block",
  "data-fusion-operation-block": ""
};
const _hoisted_3$8 = {
  class: "aoa-fusion-operation-status",
  "data-fusion-operation-status": "",
  role: "status",
  "aria-live": "polite"
};
const _hoisted_4$8 = { "data-fusion-card-status": "" };
const _hoisted_5$6 = {
  key: 0,
  "data-fusion-card-updated": ""
};
const _hoisted_6$6 = {
  key: 1,
  class: "aoa-fusion-operation-status__error",
  "data-fusion-card-error": ""
};

const {computed: computed$g} = await importShared('vue');


const _sfc_main$k = {
  __name: 'FusionColumnConfig',
  props: {
  form: { type: Object, required: true },
  fields: { type: Array, default: () => [] },
  notificationTypeItems: { type: Array, default: () => [] },
  status: { type: Object, default: () => ({}) },
  loading: { type: Boolean, default: false },
  effectiveState: { type: String, default: '' },
},
  setup(__props) {

const props = __props;

const messageId = computed$g(() => Number(props.status?.message_id || 0));
const updatedAt = computed$g(() => props.status?.date || props.status?.updated_at || props.status?.last_updated || '');
const lastError = computed$g(() => String(props.status?.last_error || '').trim());
const cardStatus = computed$g(() => {
  if (props.loading) return '正在读取融合卡片状态'
  if (messageId.value > 0) return `当前卡片 #${messageId.value}`
  return '尚未创建融合卡片'
});

return (_ctx, _cache) => {
  return (_openBlock$k(), _createElementBlock$j("div", {
    class: "aoa-config-content-stack aoa-fusion-column-config",
    "data-flat-config-section": "",
    "data-fusion-column-config-surface": "",
    "data-fusion-enabled": __props.form.fusion_notify_enabled ? 'true' : 'false',
    "data-effective-state": __props.effectiveState || undefined,
    role: "group",
    "aria-label": "融合通知配置"
  }, [
    _createVNode$g(_sfc_main$l, {
      form: __props.form,
      fields: __props.fields,
      "notification-type-items": __props.notificationTypeItems,
      "effective-state": __props.effectiveState
    }, null, 8, ["form", "fields", "notification-type-items", "effective-state"]),
    _createElementVNode$8("div", _hoisted_2$c, [
      _createElementVNode$8("div", _hoisted_3$8, [
        _createElementVNode$8("strong", _hoisted_4$8, _toDisplayString$8(cardStatus.value), 1),
        (updatedAt.value)
          ? (_openBlock$k(), _createElementBlock$j("span", _hoisted_5$6, "最近刷新：" + _toDisplayString$8(updatedAt.value), 1))
          : _createCommentVNode$7("", true),
        (lastError.value)
          ? (_openBlock$k(), _createElementBlock$j("span", _hoisted_6$6, " 最近错误：" + _toDisplayString$8(lastError.value), 1))
          : _createCommentVNode$7("", true)
      ]),
      _renderSlot$a(_ctx.$slots, "operations")
    ])
  ], 8, _hoisted_1$j))
}
}

};

const {unref:_unref$5,createElementVNode:_createElementVNode$7,openBlock:_openBlock$j,createElementBlock:_createElementBlock$i,toDisplayString:_toDisplayString$7} = await importShared('vue');


const _hoisted_1$i = {
  class: "aoa-fusion-takeover-note",
  "data-fusion-takeover-note": "",
  "data-config-notice-tone": "blue",
  role: "status",
  "aria-live": "polite"
};
const _hoisted_2$b = {
  class: "aoa-mdi-icon aoa-fusion-takeover-note__icon",
  viewBox: "0 0 24 24",
  width: "18",
  height: "18",
  "aria-hidden": "true"
};
const _hoisted_3$7 = ["d"];
const _hoisted_4$7 = {
  class: "aoa-fusion-takeover-note__copy",
  "data-fusion-takeover-copy": ""
};


const _sfc_main$j = {
  __name: 'FusionTakeoverNote',
  props: {
  message: { type: String, required: true },
},
  setup(__props) {



return (_ctx, _cache) => {
  return (_openBlock$j(), _createElementBlock$i("div", _hoisted_1$i, [
    (_openBlock$j(), _createElementBlock$i("svg", _hoisted_2$b, [
      _createElementVNode$7("path", {
        d: _unref$5(mdiShieldCheckOutline),
        fill: "currentColor"
      }, null, 8, _hoisted_3$7)
    ])),
    _createElementVNode$7("span", _hoisted_4$7, _toDisplayString$7(__props.message), 1)
  ]))
}
}

};

const {createVNode:_createVNode$f,renderSlot:_renderSlot$9,openBlock:_openBlock$i,createElementBlock:_createElementBlock$h} = await importShared('vue');


const _hoisted_1$h = ["data-health-selected-count", "data-health-notification-locked", "data-effective-state"];

const {computed: computed$f} = await importShared('vue');


const _sfc_main$i = {
  __name: 'HealthCheckConfig',
  props: {
  form: { type: Object, required: true },
  fields: { type: Array, default: () => [] },
  healthSelectedCount: { type: Number, default: 0 },
  healthCheckItems: { type: Array, default: () => [] },
  healthDatabaseTargets: { type: Array, default: () => [] },
  healthStorageTargets: { type: Array, default: () => [] },
  healthDirectoryTargets: { type: Array, default: () => [] },
  notificationTypeItems: { type: Array, default: () => [] },
  notificationLockedByFusion: { type: Boolean, default: false },
  effectiveState: { type: String, default: '' },
},
  setup(__props) {

const props = __props;

const fieldsByKey = computed$f(() => new Map(props.fields.map(field => [field.key, field])));
const fieldFor = (key, fallback) => fieldsByKey.value.get(key) || fallback;
const fieldItemSources = computed$f(() => ({
  health_check_items: props.healthCheckItems,
  health_check_database_targets: props.healthDatabaseTargets,
  health_check_storage_targets: props.healthStorageTargets,
  health_check_directory_targets: props.healthDirectoryTargets,
  health_check_notify_type: props.notificationTypeItems,
  health_check_completion_notify_type: props.notificationTypeItems,
}));
const optionalField = key => fieldsByKey.value.get(key) || null;
const healthFields = computed$f(() => [
  fieldFor('health_check_cron', { key: 'health_check_cron', control: 'cron', icon: 'mdi-calendar-clock', label: '巡查时间' }),
  fieldFor('health_check_storage_threshold', { key: 'health_check_storage_threshold', control: 'number', icon: 'mdi-gauge', label: '容量阈值', min: 1, max: 99, suffix: '%' }),
  fieldFor('health_check_items', { key: 'health_check_items', control: 'select', icon: 'mdi-format-list-checks', label: '巡查项目', items: props.healthCheckItems, multiple: true, chips: true, closableChips: true, compactSelection: true, clearable: true }),
  fieldFor('health_check_database_targets', { key: 'health_check_database_targets', control: 'select', icon: 'mdi-database-outline', label: '数据库', items: props.healthDatabaseTargets, multiple: true, chips: true, closableChips: true, compactSelection: true, clearable: true }),
  fieldFor('health_check_storage_targets', { key: 'health_check_storage_targets', control: 'select', icon: 'mdi-harddisk', label: '存储空间', items: props.healthStorageTargets, multiple: true, chips: true, closableChips: true, compactSelection: true, clearable: true }),
  fieldFor('health_check_directory_targets', { key: 'health_check_directory_targets', control: 'select', icon: 'mdi-folder-outline', label: '目录权限', items: props.healthDirectoryTargets, multiple: true, chips: true, closableChips: true, compactSelection: true, clearable: true }),
  fieldFor('health_check_notify', { key: 'health_check_notify', control: 'switch', icon: 'mdi-bell-outline', label: '异常通知' }),
  optionalField('health_check_notify_type'),
  fieldFor('health_check_completion_notify_enabled', { key: 'health_check_completion_notify_enabled', control: 'switch', icon: 'mdi-check-circle-outline', label: '巡检完成通知' }),
  optionalField('health_check_completion_notify_type'),
].filter(Boolean).map((field) => {
  const fallbackItems = fieldItemSources.value[field.key];
  return {
    ...field,
    min: field.key === 'health_check_storage_threshold' ? (field.min ?? 1) : field.min,
    max: field.key === 'health_check_storage_threshold' ? (field.max ?? 99) : field.max,
    suffix: field.key === 'health_check_storage_threshold' ? (field.suffix || '%') : field.suffix,
    items: field.items?.length ? field.items : (fallbackItems?.length ? fallbackItems : field.items),
    label: field.label,
  }
}));

function resolveDisabled(field) {
  return Boolean(
    field.disabled
    || (['health_check_notify_type', 'health_check_completion_notify_type'].includes(field.key)
      && props.notificationLockedByFusion)
  )
}

return (_ctx, _cache) => {
  return (_openBlock$i(), _createElementBlock$h("div", {
    class: "aoa-config-content-stack aoa-health-config",
    "data-flat-config-section": "",
    "data-health-config-surface": "",
    "data-health-selected-count": String(__props.healthSelectedCount),
    "data-health-notification-locked": __props.notificationLockedByFusion ? 'true' : 'false',
    "data-effective-state": __props.effectiveState || undefined,
    role: "group",
    "aria-label": "健康巡检配置"
  }, [
    _createVNode$f(_sfc_main$m, {
      form: __props.form,
      fields: healthFields.value,
      grid: "grid-2",
      "resolve-disabled": resolveDisabled,
      "data-health-fields": ""
    }, null, 8, ["form", "fields"]),
    _renderSlot$9(_ctx.$slots, "operations")
  ], 8, _hoisted_1$h))
}
}

};

const {createVNode:_createVNode$e,renderSlot:_renderSlot$8,openBlock:_openBlock$h,createElementBlock:_createElementBlock$g} = await importShared('vue');


const _hoisted_1$g = ["data-site-stat-notification-locked", "data-effective-state"];

const {computed: computed$e} = await importShared('vue');


const _sfc_main$h = {
  __name: 'SiteStatConfig',
  props: {
  form: { type: Object, required: true },
  fields: { type: Array, default: () => [] },
  siteStatRangeItems: { type: Array, default: () => [] },
  notificationTypeItems: { type: Array, default: () => [] },
  notificationLockedByFusion: { type: Boolean, default: false },
  effectiveState: { type: String, default: '' },
},
  setup(__props) {

const props = __props;

const fieldsByKey = computed$e(() => new Map(props.fields.map(field => [field.key, field])));
const fieldFor = (key, fallback) => fieldsByKey.value.get(key) || fallback;
const siteFields = computed$e(() => [
  fieldFor('site_stat_cron', { key: 'site_stat_cron', control: 'cron', icon: 'mdi-calendar-clock', label: '统计时间' }),
  fieldFor('site_stat_dashboard_type', { key: 'site_stat_dashboard_type', control: 'select', icon: 'mdi-database-outline', label: '数据范围', items: props.siteStatRangeItems }),
  fieldFor('site_stat_schedule_notify_enabled', { key: 'site_stat_schedule_notify_enabled', control: 'switch', icon: 'mdi-bell-outline', label: '定时执行后通知' }),
  fieldFor('site_stat_notify_type', { key: 'site_stat_notify_type', control: 'select', icon: 'mdi-email-outline', label: '通知渠道', items: props.notificationTypeItems }),
].map(field => ({
  ...field,
  items: field.key === 'site_stat_dashboard_type'
    ? (field.items?.length ? field.items : props.siteStatRangeItems)
    : field.key === 'site_stat_notify_type'
      ? (field.items?.length ? field.items : props.notificationTypeItems)
      : field.items,
  label: field.key === 'site_stat_notify_type' ? '通知渠道' : field.label,
})));

function resolveDisabled(field) {
  return Boolean(
    field.disabled
    || (field.key === 'site_stat_notify_type' && props.notificationLockedByFusion)
  )
}

return (_ctx, _cache) => {
  return (_openBlock$h(), _createElementBlock$g("div", {
    class: "aoa-config-content-stack aoa-site-stat-config",
    "data-flat-config-section": "",
    "data-site-stat-config-surface": "",
    "data-site-stat-notification-locked": __props.notificationLockedByFusion ? 'true' : 'false',
    "data-effective-state": __props.effectiveState || undefined,
    role: "group",
    "aria-label": "站点统计配置"
  }, [
    _createVNode$e(_sfc_main$m, {
      form: __props.form,
      fields: siteFields.value,
      grid: "grid-2",
      "resolve-disabled": resolveDisabled,
      "data-site-stat-fields": ""
    }, null, 8, ["form", "fields"]),
    _renderSlot$8(_ctx.$slots, "operations")
  ], 8, _hoisted_1$g))
}
}

};

const {createVNode:_createVNode$d,openBlock:_openBlock$g,createElementBlock:_createElementBlock$f} = await importShared('vue');


const _hoisted_1$f = ["data-media-notification-locked", "data-effective-state"];

const {computed: computed$d} = await importShared('vue');


const _sfc_main$g = {
  __name: 'MediaNotifyConfig',
  props: {
  form: { type: Object, required: true },
  fields: { type: Array, default: () => [] },
  msgGroupItems: { type: Array, default: () => [] },
  mediaserverOptions: { type: Array, default: () => [] },
  notificationTypeItems: { type: Array, default: () => [] },
  notificationLockedByFusion: { type: Boolean, default: false },
  effectiveState: { type: String, default: '' },
},
  setup(__props) {

const props = __props;

const fieldsByKey = computed$d(() => new Map(props.fields.map(field => [field.key, field])));
const fieldFor = (key, fallback) => fieldsByKey.value.get(key) || fallback;
const mediaFields = computed$d(() => [
  fieldFor('msgnotify_types', {
    key: 'msgnotify_types',
    control: 'select',
    icon: 'mdi-format-list-checks',
    label: '通知事件',
    items: props.msgGroupItems,
    multiple: true,
    chips: true,
    closableChips: true,
    compactSelection: true,
    clearable: true,
  }),
  fieldFor('msgnotify_servers', {
    key: 'msgnotify_servers',
    control: 'select',
    icon: 'mdi-server',
    label: '通知服务器',
    items: props.mediaserverOptions,
    multiple: true,
    chips: true,
    closableChips: true,
    compactSelection: true,
    clearable: true,
  }),
  fieldFor('msgnotify_notify_type', {
    key: 'msgnotify_notify_type',
    control: 'select',
    icon: 'mdi-email-outline',
    label: '通知渠道',
    items: props.notificationTypeItems,
  }),
].map(field => ({
  ...field,
  items: field.key === 'msgnotify_types'
    ? (field.items?.length ? field.items : props.msgGroupItems)
    : field.key === 'msgnotify_servers'
      ? (field.items?.length ? field.items : props.mediaserverOptions)
      : field.key === 'msgnotify_notify_type'
        ? (field.items?.length ? field.items : props.notificationTypeItems)
        : field.items,
  label: field.key === 'msgnotify_notify_type' ? '通知渠道' : field.label,
})));

function resolveDisabled(field) {
  return Boolean(
    field.disabled
    || (field.key === 'msgnotify_notify_type' && props.notificationLockedByFusion)
  )
}

return (_ctx, _cache) => {
  return (_openBlock$g(), _createElementBlock$f("div", {
    class: "aoa-config-content-stack aoa-media-notify-config",
    "data-flat-config-section": "",
    "data-media-notify-config-surface": "",
    "data-media-notification-locked": __props.notificationLockedByFusion ? 'true' : 'false',
    "data-effective-state": __props.effectiveState || undefined,
    role: "group",
    "aria-label": "媒体通知配置"
  }, [
    _createVNode$d(_sfc_main$m, {
      form: __props.form,
      fields: mediaFields.value,
      grid: "grid-2",
      "resolve-disabled": resolveDisabled
    }, null, 8, ["form", "fields"])
  ], 8, _hoisted_1$f))
}
}

};

const {createVNode:_createVNode$c,renderSlot:_renderSlot$7,openBlock:_openBlock$f,createElementBlock:_createElementBlock$e} = await importShared('vue');


const _hoisted_1$e = ["data-subscribe-notification-locked", "data-effective-state"];

const {computed: computed$c} = await importShared('vue');


const _sfc_main$f = {
  __name: 'SubscribeNotifyConfig',
  props: {
  form: { type: Object, required: true },
  fields: { type: Array, default: () => [] },
  subscribeSubtypeItems: { type: Array, default: () => [] },
  messageTypeItems: { type: Array, default: () => [] },
  notificationLockedByFusion: { type: Boolean, default: false },
  effectiveState: { type: String, default: '' },
},
  setup(__props) {

const props = __props;

const fieldsByKey = computed$c(() => new Map(props.fields.map(field => [field.key, field])));
const fieldFor = (key, fallback) => fieldsByKey.value.get(key) || fallback;
const subscribeFields = computed$c(() => [
  fieldFor('subscribe_reminder_cron', {
    key: 'subscribe_reminder_cron',
    control: 'cron',
    icon: 'mdi-calendar-clock',
    label: '检查时间',
  }),
  fieldFor('subscribe_reminder_subtype', {
    key: 'subscribe_reminder_subtype',
    control: 'select',
    icon: 'mdi-movie-open-outline',
    label: '订阅类型',
    items: props.subscribeSubtypeItems,
    multiple: true,
    chips: true,
    closableChips: true,
    compactSelection: true,
    clearable: true,
  }),
  fieldFor('subscribe_reminder_msgtype', {
    key: 'subscribe_reminder_msgtype',
    control: 'select',
    icon: 'mdi-email-outline',
    label: '通知渠道',
    items: props.messageTypeItems,
  }),
].map(field => ({
  ...field,
  items: field.key === 'subscribe_reminder_subtype'
    ? (field.items?.length ? field.items : props.subscribeSubtypeItems)
    : field.key === 'subscribe_reminder_msgtype'
      ? (field.items?.length ? field.items : props.messageTypeItems)
      : field.items,
  label: field.key === 'subscribe_reminder_msgtype' ? '通知渠道' : field.label,
})));

function resolveDisabled(field) {
  return Boolean(
    field.disabled
    || (field.key === 'subscribe_reminder_msgtype' && props.notificationLockedByFusion)
  )
}

return (_ctx, _cache) => {
  return (_openBlock$f(), _createElementBlock$e("div", {
    class: "aoa-config-content-stack aoa-subscribe-notify-config",
    "data-flat-config-section": "",
    "data-subscribe-notify-config-surface": "",
    "data-subscribe-notification-locked": __props.notificationLockedByFusion ? 'true' : 'false',
    "data-effective-state": __props.effectiveState || undefined,
    role: "group",
    "aria-label": "订阅提醒配置"
  }, [
    _createVNode$c(_sfc_main$m, {
      form: __props.form,
      fields: subscribeFields.value,
      grid: "grid-2",
      "resolve-disabled": resolveDisabled
    }, null, 8, ["form", "fields"]),
    _renderSlot$7(_ctx.$slots, "operations")
  ], 8, _hoisted_1$e))
}
}

};

const {createVNode:_createVNode$b,renderSlot:_renderSlot$6,openBlock:_openBlock$e,createElementBlock:_createElementBlock$d} = await importShared('vue');


const _hoisted_1$d = ["data-log-clean-notification-locked", "data-effective-state"];


const _sfc_main$e = {
  __name: 'LogCleanConfig',
  props: {
  form: { type: Object, required: true },
  fields: { type: Array, default: () => [] },
  notificationLockedByFusion: { type: Boolean, default: false },
  effectiveState: { type: String, default: '' },
},
  setup(__props) {

const props = __props;

function resolveDisabled(field) {
  return Boolean(
    field.disabled
    || (field.key === 'log_clean_notify_type' && props.notificationLockedByFusion)
  )
}

return (_ctx, _cache) => {
  return (_openBlock$e(), _createElementBlock$d("div", {
    class: "aoa-config-content-stack aoa-log-clean-config",
    "data-flat-config-section": "",
    "data-log-clean-config-surface": "",
    "data-log-clean-notification-locked": __props.notificationLockedByFusion ? 'true' : 'false',
    "data-effective-state": __props.effectiveState || undefined,
    role: "group",
    "aria-label": "日志清理配置"
  }, [
    _createVNode$b(_sfc_main$m, {
      form: __props.form,
      fields: __props.fields,
      grid: "grid-2",
      "resolve-disabled": resolveDisabled,
      class: "aoa-log-clean-field-grid",
      "data-log-clean-fields": ""
    }, null, 8, ["form", "fields"]),
    _renderSlot$6(_ctx.$slots, "operations")
  ], 8, _hoisted_1$d))
}
}

};

const {createVNode:_createVNode$a,unref:_unref$4,createElementVNode:_createElementVNode$6,openBlock:_openBlock$d,createElementBlock:_createElementBlock$c,createTextVNode:_createTextVNode$3,renderList:_renderList$3,Fragment:_Fragment$3,toDisplayString:_toDisplayString$6,renderSlot:_renderSlot$5} = await importShared('vue');


const _hoisted_1$c = ["data-seed-clean-notification-locked", "data-effective-state"];
const _hoisted_2$a = ["data-effective-state"];
const _hoisted_3$6 = {
  class: "aoa-mdi-icon",
  viewBox: "0 0 24 24",
  width: "18",
  height: "18",
  "aria-hidden": "true"
};
const _hoisted_4$6 = ["d"];
const _hoisted_5$5 = {
  class: "aoa-design-advanced__chevron aoa-mdi-icon",
  viewBox: "0 0 24 24",
  width: "15",
  height: "15",
  "aria-hidden": "true"
};
const _hoisted_6$5 = ["d"];
const _hoisted_7$4 = { class: "aoa-design-advanced-content" };
const _hoisted_8$4 = {
  class: "aoa-seedclean-status-dictionary",
  "data-seedclean-status-dictionary": ""
};
const _hoisted_9$4 = ["data-seedclean-qb-status-dictionary", "data-seedclean-tr-status-dictionary"];
const _hoisted_10$4 = ["data-seedclean-status-key", "data-seedclean-status-index", "data-seedclean-status-field"];


const _sfc_main$d = {
  __name: 'SeedCleanConfig',
  props: {
  form: { type: Object, required: true },
  primaryFields: { type: Array, default: () => [] },
  filterFields: { type: Array, default: () => [] },
  notificationLockedByFusion: { type: Boolean, default: false },
  effectiveState: { type: String, default: '' },
},
  setup(__props) {

const props = __props;
const statusDictionaries = Object.freeze([
  {
    key: 'qb',
    title: 'qB 任务状态字典',
    field: 'seedclean_torrentstates',
    entries: [
      ['downloading', '正在下载-传输数据'],
      ['stalledDL', '正在下载_未建立连接'],
      ['uploading', '正在上传-传输数据'],
      ['stalledUP', '正在上传-未建立连接'],
      ['error', '暂停-发生错误'],
      ['pausedDL', '暂停-下载未完成'],
      ['pausedUP', '暂停-下载完成'],
      ['missingFiles', '暂停-文件丢失'],
      ['checkingDL', '检查中-下载未完成'],
      ['checkingUP', '检查中-下载完成'],
      ['checkingResumeData', '检查中-启动时恢复数据'],
      ['forcedDL', '强制下载-忽略队列'],
      ['queuedDL', '等待下载-排队'],
      ['forcedUP', '强制上传-忽略队列'],
      ['queuedUP', '等待上传-排队'],
      ['allocating', '分配磁盘空间'],
      ['metaDL', '获取元数据'],
      ['moving', '移动文件'],
      ['unknown', '未知状态'],
    ],
  },
  {
    key: 'tr',
    title: 'TR 任务状态字典',
    field: 'seedclean_trtorrentstates',
    entries: [
      ['0 / stopped', '停止'],
      ['1 / check_pending', '校验队列'],
      ['2 / checking', '校验中'],
      ['3 / download_pending', '下载队列'],
      ['4 / downloading', '下载中'],
      ['5 / seed_pending', '做种队列'],
      ['6 / seeding', '做种'],
      ['error', '错误'],
    ],
  },
]);

function resolveDisabled(field) {
  return Boolean(
    field.disabled
    || (field.key === 'seedclean_notify_type' && props.notificationLockedByFusion)
  )
}

return (_ctx, _cache) => {
  return (_openBlock$d(), _createElementBlock$c("div", {
    class: "aoa-config-content-stack aoa-seed-clean-config",
    "data-flat-config-section": "",
    "data-seed-clean-config-surface": "",
    "data-seed-clean-notification-locked": __props.notificationLockedByFusion ? 'true' : 'false',
    "data-effective-state": __props.effectiveState || undefined,
    role: "group",
    "aria-label": "自动删种配置"
  }, [
    _createVNode$a(_sfc_main$m, {
      form: __props.form,
      fields: __props.primaryFields,
      grid: "grid-2",
      "resolve-disabled": resolveDisabled,
      "data-seedclean-primary-card": "",
      "data-seedclean-primary-fields": ""
    }, null, 8, ["form", "fields"]),
    _createElementVNode$6("details", {
      class: "aoa-design-advanced aoa-design-advanced--embedded",
      "data-html-advanced": "",
      "data-seedclean-filter-drawer": "",
      "data-default-open": "false",
      "data-effective-state": __props.effectiveState || undefined
    }, [
      _createElementVNode$6("summary", null, [
        _createElementVNode$6("span", null, [
          (_openBlock$d(), _createElementBlock$c("svg", _hoisted_3$6, [
            _createElementVNode$6("path", {
              d: _unref$4(mdiFilterOutline),
              fill: "currentColor"
            }, null, 8, _hoisted_4$6)
          ])),
          _cache[0] || (_cache[0] = _createTextVNode$3(" 筛选条件 ", -1))
        ]),
        (_openBlock$d(), _createElementBlock$c("svg", _hoisted_5$5, [
          _createElementVNode$6("path", {
            d: _unref$4(mdiCogOutline),
            fill: "currentColor"
          }, null, 8, _hoisted_6$5)
        ]))
      ]),
      _createElementVNode$6("div", _hoisted_7$4, [
        _createVNode$a(_sfc_main$m, {
          form: __props.form,
          fields: __props.filterFields,
          grid: "grid-2",
          "resolve-disabled": resolveDisabled,
          "data-seedclean-filter-fields": ""
        }, null, 8, ["form", "fields"]),
        _createElementVNode$6("aside", _hoisted_8$4, [
          (_openBlock$d(true), _createElementBlock$c(_Fragment$3, null, _renderList$3(_unref$4(statusDictionaries), (dictionary) => {
            return (_openBlock$d(), _createElementBlock$c("section", {
              key: dictionary.key,
              class: "aoa-seedclean-status-dictionary__group",
              "data-seedclean-qb-status-dictionary": dictionary.key === 'qb' ? '' : undefined,
              "data-seedclean-tr-status-dictionary": dictionary.key === 'tr' ? '' : undefined
            }, [
              _createElementVNode$6("h4", null, _toDisplayString$6(dictionary.title), 1),
              _createElementVNode$6("ul", null, [
                (_openBlock$d(true), _createElementBlock$c(_Fragment$3, null, _renderList$3(dictionary.entries, (entry, index) => {
                  return (_openBlock$d(), _createElementBlock$c("li", {
                    key: entry[0],
                    "data-seedclean-status-entry": "",
                    "data-seedclean-status-key": entry[0],
                    "data-seedclean-status-index": String(index),
                    "data-seedclean-status-field": dictionary.field
                  }, _toDisplayString$6(entry[0]) + "：" + _toDisplayString$6(entry[1]), 9, _hoisted_10$4))
                }), 128))
              ])
            ], 8, _hoisted_9$4))
          }), 128))
        ])
      ])
    ], 8, _hoisted_2$a),
    _renderSlot$5(_ctx.$slots, "operations")
  ], 8, _hoisted_1$c))
}
}

};

const {createElementVNode:_createElementVNode$5,toDisplayString:_toDisplayString$5,vModelText:_vModelText$1,withDirectives:_withDirectives$1,normalizeClass:_normalizeClass$2,openBlock:_openBlock$c,createElementBlock:_createElementBlock$b} = await importShared('vue');


const _hoisted_1$b = ["data-disabled"];
const _hoisted_2$9 = { class: "aoa-subfill-code__controls" };
const _hoisted_3$5 = { class: "aoa-subfill-code__input" };
const _hoisted_4$5 = { class: "aoa-subfill-code__heading" };
const _hoisted_5$4 = { "data-tone": "neutral" };
const _hoisted_6$4 = ["rows", "disabled", "placeholder"];

const {computed: computed$b} = await importShared('vue');



const _sfc_main$c = {
  __name: 'TrackerMappingEditor',
  props: {
  values: { type: Object, required: true },
  field: { type: Object, default: () => ({}) },
  disabled: { type: Boolean, default: false },
},
  setup(__props) {

const props = __props;

const mappingText = computed$b({
  get: () => String(props.values.dltag_tracker_mappings ?? ''),
  set: value => { props.values.dltag_tracker_mappings = String(value ?? ''); },
});
const mappingCount = computed$b(() => mappingText.value
  .split(/\r?\n/u)
  .map(line => line.trim())
  .filter(line => line && !line.startsWith('#'))
  .length);
const mappingSummary = computed$b(() => mappingCount.value
  ? `${mappingCount.value} 条映射`
  : '尚未配置映射');

return (_ctx, _cache) => {
  return (_openBlock$c(), _createElementBlock$b("div", {
    class: "aoa-subfill-editor-container aoa-tracker-mapping-editor",
    "data-tracker-mapping-editor": "",
    "data-field-key": "dltag_tracker_mappings",
    "data-field-control": "textarea",
    "data-disabled": __props.disabled ? 'true' : undefined
  }, [
    _createElementVNode$5("section", {
      class: _normalizeClass$2(["aoa-subfill-code aoa-tracker-mapping-code", { 'aoa-subfill-code--disabled': __props.disabled }]),
      "data-tracker-mapping-code-editor": ""
    }, [
      _createElementVNode$5("div", _hoisted_2$9, [
        _createElementVNode$5("label", _hoisted_3$5, [
          _createElementVNode$5("span", _hoisted_4$5, [
            _cache[1] || (_cache[1] = _createElementVNode$5("strong", null, "映射规则", -1)),
            _createElementVNode$5("small", _hoisted_5$4, _toDisplayString$5(mappingSummary.value), 1)
          ]),
          _withDirectives$1(_createElementVNode$5("textarea", {
            "onUpdate:modelValue": _cache[0] || (_cache[0] = $event => ((mappingText).value = $event)),
            rows: __props.field.rows || 6,
            spellcheck: "false",
            disabled: __props.disabled,
            "aria-describedby": "aoa-tracker-mapping-help",
            "data-tracker-mapping-input": "",
            placeholder: __props.field.placeholder || '每行一条，例如 tracker.example.com => 站点标签'
          }, null, 8, _hoisted_6$4), [
            [_vModelText$1, mappingText.value]
          ]),
          _cache[2] || (_cache[2] = _createElementVNode$5("small", {
            id: "aoa-tracker-mapping-help",
            class: "aoa-subfill-code__help"
          }, " 每行一条映射；支持 tracker.example.com => 站点标签，也支持 tracker.example.com = 站点标签。 ", -1))
        ])
      ])
    ], 2)
  ], 8, _hoisted_1$b))
}
}

};

const {createElementVNode:_createElementVNode$4,createVNode:_createVNode$9,unref:_unref$3,openBlock:_openBlock$b,createElementBlock:_createElementBlock$a,createTextVNode:_createTextVNode$2,toDisplayString:_toDisplayString$4,renderSlot:_renderSlot$4} = await importShared('vue');


const _hoisted_1$a = ["data-downloader-helper-notification-locked", "data-effective-state"];
const _hoisted_2$8 = ["data-effective-state"];
const _hoisted_3$4 = { class: "aoa-tracker-mapping-drawer__title" };
const _hoisted_4$4 = {
  class: "aoa-mdi-icon",
  viewBox: "0 0 24 24",
  width: "18",
  height: "18",
  "aria-hidden": "true"
};
const _hoisted_5$3 = ["d"];
const _hoisted_6$3 = { class: "aoa-tracker-mapping-drawer__state" };
const _hoisted_7$3 = { "data-tracker-mapping-summary": "" };
const _hoisted_8$3 = {
  class: "aoa-design-advanced__chevron aoa-tracker-mapping-drawer__chevron aoa-mdi-icon",
  viewBox: "0 0 24 24",
  width: "18",
  height: "18",
  "aria-hidden": "true"
};
const _hoisted_9$3 = ["d"];
const _hoisted_10$3 = { class: "aoa-design-advanced-content" };

const {computed: computed$a} = await importShared('vue');


const _sfc_main$b = {
  __name: 'DownloaderHelperConfig',
  props: {
  form: { type: Object, required: true },
  fields: { type: Array, default: () => [] },
  trackerFields: { type: Array, default: () => [] },
  notificationLockedByFusion: { type: Boolean, default: false },
  effectiveState: { type: String, default: '' },
},
  setup(__props) {

const props = __props;

function resolveDisabled(field) {
  return Boolean(
    field.disabled
    || (field.key === 'dltag_notify_type' && props.notificationLockedByFusion)
  )
}

const trackerField = computed$a(() => props.trackerFields[0] || {});
const trackerMappingCount = computed$a(() => String(props.form.dltag_tracker_mappings ?? '')
  .split(/\r?\n/u)
  .map(line => line.trim())
  .filter(line => line && !line.startsWith('#'))
  .length);
const trackerSummary = computed$a(() => trackerMappingCount.value
  ? `${trackerMappingCount.value} 条映射`
  : '尚未配置');

return (_ctx, _cache) => {
  return (_openBlock$b(), _createElementBlock$a("div", {
    class: "aoa-config-content-stack aoa-downloader-helper-config",
    "data-flat-config-section": "",
    "data-downloader-helper-config-surface": "",
    "data-downloader-helper-notification-locked": __props.notificationLockedByFusion ? 'true' : 'false',
    "data-effective-state": __props.effectiveState || undefined,
    role: "group",
    "aria-label": "下载器助手配置"
  }, [
    _cache[1] || (_cache[1] = _createElementVNode$4("p", {
      class: "aoa-downloader-helper-boundary",
      "data-downloader-helper-boundary-note": ""
    }, " 下载器助手负责标签、恢复做种与失效任务；按用户规则自动清理仍由“自动删种”页面负责。 ", -1)),
    _createVNode$9(_sfc_main$m, {
      form: __props.form,
      fields: __props.fields,
      grid: "grid-2",
      "resolve-disabled": resolveDisabled,
      "data-downloader-helper-fields": ""
    }, null, 8, ["form", "fields"]),
    _createElementVNode$4("details", {
      class: "aoa-design-advanced aoa-design-advanced--embedded aoa-tracker-mapping-drawer",
      "data-html-advanced": "",
      "data-dltag-tracker-drawer": "",
      "data-default-open": "false",
      "data-effective-state": __props.effectiveState || undefined
    }, [
      _createElementVNode$4("summary", null, [
        _createElementVNode$4("span", _hoisted_3$4, [
          (_openBlock$b(), _createElementBlock$a("svg", _hoisted_4$4, [
            _createElementVNode$4("path", {
              d: _unref$3(mdiLinkVariant),
              fill: "currentColor"
            }, null, 8, _hoisted_5$3)
          ])),
          _cache[0] || (_cache[0] = _createTextVNode$2(" Tracker 映射 ", -1))
        ]),
        _createElementVNode$4("span", _hoisted_6$3, [
          _createElementVNode$4("small", _hoisted_7$3, _toDisplayString$4(trackerSummary.value), 1),
          (_openBlock$b(), _createElementBlock$a("svg", _hoisted_8$3, [
            _createElementVNode$4("path", {
              d: _unref$3(mdiChevronDown),
              fill: "currentColor"
            }, null, 8, _hoisted_9$3)
          ]))
        ])
      ]),
      _createElementVNode$4("div", _hoisted_10$3, [
        _createVNode$9(_sfc_main$c, {
          values: __props.form,
          field: trackerField.value,
          disabled: resolveDisabled(trackerField.value)
        }, null, 8, ["values", "field", "disabled"])
      ])
    ], 8, _hoisted_2$8),
    _renderSlot$4(_ctx.$slots, "operations")
  ], 8, _hoisted_1$a))
}
}

};

const {renderList:_renderList$2,Fragment:_Fragment$2,openBlock:_openBlock$a,createElementBlock:_createElementBlock$9,resolveComponent:_resolveComponent$1,createVNode:_createVNode$8,createElementVNode:_createElementVNode$3,toDisplayString:_toDisplayString$3,mergeProps:_mergeProps$2} = await importShared('vue');


const _hoisted_1$9 = ["data-config-category-domain", "aria-label"];
const _hoisted_2$7 = ["data-config-category-card", "aria-selected", "onClick", "onKeydown"];
const _hoisted_3$3 = {
  class: "aoa-config-category-selector__icon",
  "aria-hidden": "true"
};
const _hoisted_4$3 = ["aria-checked", "aria-label", "onClick"];


const _sfc_main$a = {
  __name: 'ConfigCategorySelector',
  props: {
  form: { type: Object, required: true },
  selectors: { type: Array, default: () => [] },
  activeModule: { type: String, default: '' },
  domain: { type: String, required: true },
},
  emits: ['selectModule'],
  setup(__props, { emit: __emit }) {

const props = __props;

const emit = __emit;

function selectorAttrs(card) {
  const active = props.activeModule === card.module;
  return {
    [`data-${props.domain}-selector-card`]: card.module,
    [`data-${props.domain}-selector-active`]: active ? 'true' : 'false',
  }
}

function toggleAttrs(card) {
  return { [`data-${props.domain}-selector-toggle`]: card.module }
}

function selectModule(card, event) {
  if (event?.target?.closest?.('[data-config-category-toggle]')) return
  emit('selectModule', card.module);
}

function selectModuleWithKeyboard(card, event) {
  if (event.key !== 'Enter' && event.key !== ' ') return
  event.preventDefault();
  emit('selectModule', card.module);
}

function toggleModule(card, event) {
  event.preventDefault();
  event.stopPropagation();
  if (!card.masterKey) return
  const enabled = !Boolean(props.form[card.masterKey]);
  props.form[card.masterKey] = enabled;
  const scheduleKey = card.scheduleKey || `${card.module}_schedule_enabled`;
  if (Object.prototype.hasOwnProperty.call(props.form, scheduleKey)) props.form[scheduleKey] = enabled;
}

return (_ctx, _cache) => {
  const _component_VIcon = _resolveComponent$1("VIcon");

  return (_openBlock$a(), _createElementBlock$9("div", {
    class: "aoa-config-category-selector",
    "data-config-category-selector": "",
    "data-config-category-domain": __props.domain,
    role: "tablist",
    "aria-label": `${__props.domain} 分类`
  }, [
    (_openBlock$a(true), _createElementBlock$9(_Fragment$2, null, _renderList$2(__props.selectors, (card) => {
      return (_openBlock$a(), _createElementBlock$9("article", _mergeProps$2({
        key: card.module
      }, { ref_for: true }, selectorAttrs(card), {
        class: ["aoa-config-category-selector__item", { 'aoa-config-category-selector__item--active': __props.activeModule === card.module }],
        "data-config-category-card": card.module,
        "aria-selected": __props.activeModule === card.module ? 'true' : 'false',
        role: "tab",
        tabindex: "0",
        onClick: $event => (selectModule(card, $event)),
        onKeydown: $event => (selectModuleWithKeyboard(card, $event))
      }), [
        _createElementVNode$3("span", _hoisted_3$3, [
          _createVNode$8(_component_VIcon, {
            icon: card.icon || 'mdi-tune-variant',
            size: "18"
          }, null, 8, ["icon"])
        ]),
        _createElementVNode$3("strong", null, _toDisplayString$3(card.title), 1),
        _createElementVNode$3("button", _mergeProps$2({ type: "button" }, { ref_for: true }, toggleAttrs(card), {
          class: ["aoa-toggle-switch aoa-config-category-selector__toggle", { 'aoa-toggle-switch--on': Boolean(__props.form[card.masterKey]) }],
          role: "switch",
          "aria-checked": Boolean(__props.form[card.masterKey]),
          "aria-label": `${card.title}开关`,
          "data-config-category-toggle": "",
          onClick: $event => (toggleModule(card, $event))
        }), [...(_cache[0] || (_cache[0] = [
          _createElementVNode$3("span", {
            class: "aoa-toggle-switch__thumb",
            "aria-hidden": "true"
          }, null, -1)
        ]))], 16, _hoisted_4$3)
      ], 16, _hoisted_2$7))
    }), 128))
  ], 8, _hoisted_1$9))
}
}

};

const {resolveComponent:_resolveComponent,createVNode:_createVNode$7,toDisplayString:_toDisplayString$2,createElementVNode:_createElementVNode$2,unref:_unref$2,openBlock:_openBlock$9,createElementBlock:_createElementBlock$8,createTextVNode:_createTextVNode$1,withCtx:_withCtx$5,createBlock:_createBlock$5,createCommentVNode:_createCommentVNode$6} = await importShared('vue');


const _hoisted_1$8 = ["data-backup-restore-panel", "data-backup-restore-drawer", "aria-labelledby"];
const _hoisted_2$6 = { class: "aoa-backup-restore-drawer__title" };
const _hoisted_3$2 = ["id"];
const _hoisted_4$2 = { class: "aoa-backup-restore-drawer__state" };
const _hoisted_5$2 = { "data-backup-restore-status": "" };
const _hoisted_6$2 = {
  class: "aoa-design-advanced__chevron aoa-backup-restore-drawer__chevron aoa-mdi-icon",
  viewBox: "0 0 24 24",
  width: "18",
  height: "18",
  "aria-hidden": "true"
};
const _hoisted_7$2 = ["d"];
const _hoisted_8$2 = { class: "aoa-design-advanced-content aoa-backup-restore-drawer__content" };
const _hoisted_9$2 = {
  class: "aoa-design-actions aoa-backup-restore-actions",
  "data-backup-restore-actions": ""
};
const _hoisted_10$2 = ["disabled"];
const _hoisted_11$2 = ["disabled"];
const _hoisted_12$2 = ["disabled"];

const {computed: computed$9} = await importShared('vue');


const _sfc_main$9 = {
  __name: 'BackupRestorePanel',
  props: {
  channel: { type: String, default: 'local' },
  title: { type: String, required: true },
  note: { type: String, default: '' },
  restore: { type: Object, required: true },
  archives: { type: Array, default: () => [] },
  archivesLoading: { type: Boolean, default: false },
  restoreLoading: { type: Boolean, default: false },
  result: { type: Object, default: null },
  unavailable: { type: Boolean, default: false },
  unavailableMessage: { type: String, default: '' },
  archiveLabel: { type: String, default: '选择备份包' },
  archiveIcon: { type: String, default: 'mdi-archive-search-outline' },
  noDataText: { type: String, default: '暂无可恢复备份包' },
  refreshLabel: { type: String, default: '刷新列表' },
  refreshIcon: { type: String, default: 'mdi-refresh' },
  confirmLabel: { type: String, default: '确认覆盖当前配置' },
  previewLabel: { type: String, default: '预览恢复' },
  runLabel: { type: String, default: '一键恢复' },
  runIcon: { type: String, default: 'mdi-backup-restore' },
  fallbackResultText: { type: String, default: '备份恢复已返回结果' },
},
  emits: ['refresh', 'preview', 'run'],
  setup(__props, { emit: __emit }) {

const props = __props;

const emit = __emit;
const titleId = computed$9(() => `aoa-backup-restore-${String(props.channel || 'local').replace(/[^a-zA-Z0-9_-]/g, '-')}`);
const archiveItems = computed$9(() => props.archives.map(archive => ({
  title: archive?.name || String(archive || ''),
  value: archive?.name || String(archive || ''),
})));
const restoreFields = computed$9(() => [
  {
    key: 'archive',
    control: 'select',
    icon: props.archiveIcon,
    label: props.archiveLabel,
    items: archiveItems.value,
    loading: props.archivesLoading,
    disabled: props.unavailable || props.archivesLoading,
    placeholder: props.noDataText,
  },
  { key: 'restore_config', control: 'switch', icon: 'mdi-file-cog-outline', label: '恢复配置文件', disabled: props.unavailable },
  { key: 'restore_cookies', control: 'switch', icon: 'mdi-cookie-outline', label: '恢复 Cookies', disabled: props.unavailable },
  { key: 'restore_database', control: 'switch', icon: 'mdi-database-refresh-outline', label: '恢复数据库', disabled: props.unavailable },
  { key: 'confirm', control: 'switch', icon: 'mdi-alert-outline', label: props.confirmLabel, disabled: props.unavailable },
]);

function restoreRowAttrs(field) {
  return {
    'data-backup-restore-field': field.key,
    class: field.key === 'archive' ? 'aoa-backup-restore-field--archive' : undefined,
  }
}

return (_ctx, _cache) => {
  const _component_VIcon = _resolveComponent("VIcon");
  const _component_VAlert = _resolveComponent("VAlert");

  return (_openBlock$9(), _createElementBlock$8("details", {
    class: "aoa-design-advanced aoa-design-advanced--embedded aoa-backup-restore-panel",
    "data-backup-restore-panel": __props.channel,
    "data-backup-restore-drawer": __props.channel,
    "data-default-open": "false",
    "aria-labelledby": titleId.value
  }, [
    _createElementVNode$2("summary", null, [
      _createElementVNode$2("span", _hoisted_2$6, [
        _createVNode$7(_component_VIcon, {
          icon: __props.archiveIcon,
          size: "18"
        }, null, 8, ["icon"]),
        _createElementVNode$2("strong", { id: titleId.value }, _toDisplayString$2(__props.title), 9, _hoisted_3$2)
      ]),
      _createElementVNode$2("span", _hoisted_4$2, [
        _createElementVNode$2("small", _hoisted_5$2, _toDisplayString$2(__props.unavailable ? '暂不可用' : `${__props.archives.length} 份可用`), 1),
        (_openBlock$9(), _createElementBlock$8("svg", _hoisted_6$2, [
          _createElementVNode$2("path", {
            d: _unref$2(mdiChevronDown),
            fill: "currentColor"
          }, null, 8, _hoisted_7$2)
        ]))
      ])
    ]),
    _createElementVNode$2("div", _hoisted_8$2, [
      (__props.unavailable)
        ? (_openBlock$9(), _createBlock$5(_component_VAlert, {
            key: 0,
            type: "warning",
            variant: "tonal",
            density: "comfortable",
            "data-backup-restore-unavailable": ""
          }, {
            default: _withCtx$5(() => [
              _createTextVNode$1(_toDisplayString$2(__props.unavailableMessage), 1)
            ]),
            _: 1
          }))
        : _createCommentVNode$6("", true),
      _createVNode$7(_sfc_main$m, {
        fields: restoreFields.value,
        form: __props.restore,
        grid: "grid-2",
        "field-defaults": { hideInlineLabel: true, hideDetails: true, density: 'compact' },
        "row-attrs": restoreRowAttrs,
        "data-backup-restore-fields": ""
      }, null, 8, ["fields", "form"]),
      _createElementVNode$2("div", _hoisted_9$2, [
        _createElementVNode$2("button", {
          type: "button",
          class: "aoa-design-action-btn",
          disabled: __props.unavailable || __props.archivesLoading,
          "data-backup-restore-refresh": "",
          onClick: _cache[0] || (_cache[0] = $event => (emit('refresh')))
        }, [
          _createVNode$7(_component_VIcon, {
            icon: __props.refreshIcon,
            size: "18",
            "aria-hidden": "true"
          }, null, 8, ["icon"]),
          _createElementVNode$2("span", null, _toDisplayString$2(__props.archivesLoading ? '正在刷新...' : __props.refreshLabel), 1)
        ], 8, _hoisted_10$2),
        _createElementVNode$2("button", {
          type: "button",
          class: "aoa-design-action-btn",
          disabled: __props.unavailable || !__props.restore.archive || __props.restoreLoading,
          "data-backup-restore-preview": "",
          onClick: _cache[1] || (_cache[1] = $event => (emit('preview')))
        }, [
          _createVNode$7(_component_VIcon, {
            icon: "mdi-file-eye-outline",
            size: "18",
            "aria-hidden": "true"
          }),
          _createElementVNode$2("span", null, _toDisplayString$2(__props.restoreLoading ? '正在处理...' : __props.previewLabel), 1)
        ], 8, _hoisted_11$2),
        _createElementVNode$2("button", {
          type: "button",
          class: "aoa-design-action-btn aoa-design-action-btn--danger",
          disabled: __props.unavailable || !__props.restore.archive || !__props.restore.confirm || __props.restoreLoading,
          "data-backup-restore-run": "",
          onClick: _cache[2] || (_cache[2] = $event => (emit('run')))
        }, [
          _createVNode$7(_component_VIcon, {
            icon: __props.runIcon,
            size: "18",
            "aria-hidden": "true"
          }, null, 8, ["icon"]),
          _createElementVNode$2("span", null, _toDisplayString$2(__props.restoreLoading ? '正在恢复...' : __props.runLabel), 1)
        ], 8, _hoisted_12$2)
      ]),
      (__props.result)
        ? (_openBlock$9(), _createBlock$5(_component_VAlert, {
            key: 1,
            type: __props.result.code === 0 ? 'success' : 'error',
            variant: "tonal",
            density: "comfortable",
            "data-backup-restore-feedback": "",
            role: __props.result.code === 0 ? 'status' : 'alert',
            "aria-live": __props.result.code === 0 ? 'polite' : 'assertive'
          }, {
            default: _withCtx$5(() => [
              _createTextVNode$1(_toDisplayString$2(__props.result.msg || __props.result.text || __props.fallbackResultText), 1)
            ]),
            _: 1
          }, 8, ["type", "role", "aria-live"]))
        : _createCommentVNode$6("", true)
    ])
  ], 8, _hoisted_1$8))
}
}

};

const {createVNode:_createVNode$6,openBlock:_openBlock$8,createElementBlock:_createElementBlock$7} = await importShared('vue');


const _hoisted_1$7 = ["data-backup-config-disabled"];

const {computed: computed$8} = await importShared('vue');


const _sfc_main$8 = {
  __name: 'BackupLocalConfig',
  props: {
  form: { type: Object, required: true },
  fields: { type: Array, default: () => [] },
  backupRestoreUnavailable: { type: Boolean, default: false },
  backupRestoreUnavailableMessage: { type: String, default: '' },
  backupArchives: { type: Array, default: () => [] },
  backupArchivesLoading: { type: Boolean, default: false },
  backupRestoreLoading: { type: Boolean, default: false },
  backupRestoreResult: { type: Object, default: null },
  backupRestore: { type: Object, required: true },
},
  emits: ['loadBackupArchives', 'previewBackupRestore', 'runBackupRestore'],
  setup(__props, { emit: __emit }) {

const props = __props;

const emit = __emit;

const fallbackFields = Object.freeze([
  { key: 'backup_path', control: 'text', icon: 'mdi-folder-outline', label: '本地备份路径' },
  { key: 'backup_keep_count', control: 'number', icon: 'mdi-content-copy', label: '本地保留份数', min: 1, max: 30 },
]);
const configDisabled = computed$8(() => !props.form.enabled || !props.form.backup_enabled);
const localFields = computed$8(() => (props.fields.length ? props.fields : fallbackFields).map(field => ({
  ...field,
  min: field.key === 'backup_keep_count' ? (field.min ?? 1) : field.min,
  max: field.key === 'backup_keep_count' ? (field.max ?? 30) : field.max,
  disabled: configDisabled.value || Boolean(field.disabled),
})));

return (_ctx, _cache) => {
  return (_openBlock$8(), _createElementBlock$7("div", {
    class: "aoa-backup-config-panel",
    "data-backup-config-panel": "local",
    "data-backup-config-disabled": configDisabled.value ? 'true' : 'false'
  }, [
    _createVNode$6(_sfc_main$m, {
      class: "aoa-backup-config-fields",
      "data-backup-config-fields": "local",
      fields: localFields.value,
      form: __props.form,
      grid: "grid-2",
      "active-sub": "backup",
      "field-defaults": { hideInlineLabel: true, hideDetails: true, density: 'compact' }
    }, null, 8, ["fields", "form"]),
    _createVNode$6(_sfc_main$9, {
      channel: "local",
      title: "恢复本地备份",
      note: "从本插件生成的本地备份包恢复配置、Cookies 或数据库",
      restore: __props.backupRestore,
      archives: __props.backupArchives,
      "archives-loading": __props.backupArchivesLoading,
      "restore-loading": __props.backupRestoreLoading,
      result: __props.backupRestoreResult,
      unavailable: __props.backupRestoreUnavailable,
      "unavailable-message": __props.backupRestoreUnavailableMessage,
      "archive-label": "选择备份包",
      "archive-icon": "mdi-archive-search-outline",
      "no-data-text": "暂无可恢复备份包",
      "refresh-label": "刷新列表",
      "refresh-icon": "mdi-refresh",
      "confirm-label": "确认覆盖当前配置",
      "preview-label": "预览恢复",
      "run-label": "一键恢复",
      "run-icon": "mdi-backup-restore",
      "fallback-result-text": "备份恢复已返回结果",
      onRefresh: _cache[0] || (_cache[0] = $event => (emit('loadBackupArchives'))),
      onPreview: _cache[1] || (_cache[1] = $event => (emit('previewBackupRestore'))),
      onRun: _cache[2] || (_cache[2] = $event => (emit('runBackupRestore')))
    }, null, 8, ["restore", "archives", "archives-loading", "restore-loading", "result", "unavailable", "unavailable-message"])
  ], 8, _hoisted_1$7))
}
}

};

const {createVNode:_createVNode$5,openBlock:_openBlock$7,createElementBlock:_createElementBlock$6} = await importShared('vue');


const _hoisted_1$6 = ["data-backup-configured", "data-backup-config-disabled"];

const {computed: computed$7} = await importShared('vue');


const _sfc_main$7 = {
  __name: 'BackupWebdavConfig',
  props: {
  form: { type: Object, required: true },
  fields: { type: Array, default: () => [] },
  keepCountPresets: { type: Array, default: () => [] },
  webdavBackupRestoreUnavailable: { type: Boolean, default: false },
  webdavBackupRestoreUnavailableMessage: { type: String, default: '' },
  webdavBackupArchives: { type: Array, default: () => [] },
  webdavBackupArchivesLoading: { type: Boolean, default: false },
  webdavBackupRestoreLoading: { type: Boolean, default: false },
  webdavBackupRestoreResult: { type: Object, default: null },
  webdavBackupRestore: { type: Object, required: true },
},
  emits: ['loadWebdavBackupArchives', 'previewWebdavBackupRestore', 'runWebdavBackupRestore'],
  setup(__props, { emit: __emit }) {

const props = __props;

const emit = __emit;

const webdavConfigured = computed$7(() => Boolean(props.form.backup_webdav_enabled) && [
  props.form.backup_webdav_hostname,
  props.form.backup_webdav_login,
  props.form.backup_webdav_password,
].every(value => String(value || '').trim().length > 0));
const configDisabled = computed$7(() => !props.form.enabled || !props.form.backup_webdav_enabled);
const fallbackFields = computed$7(() => [
  { key: 'backup_webdav_hostname', control: 'text', icon: 'mdi-web', label: 'WebDAV 地址', placeholder: 'https://dav.example.com/backup' },
  { key: 'backup_webdav_login', control: 'text', icon: 'mdi-account-outline', label: '账号' },
  { key: 'backup_webdav_password', control: 'text', icon: 'mdi-lock-outline', label: '密码', sensitive: true },
  {
    key: 'backup_webdav_max_count',
    control: props.keepCountPresets.length ? 'select' : 'number',
    icon: 'mdi-content-copy',
    label: '远端保留份数',
    items: props.keepCountPresets,
    min: 1,
    max: 30,
  },
  { key: 'backup_webdav_digest_auth', control: 'switch', icon: 'mdi-shield-outline', label: '使用 Digest 认证' },
  { key: 'backup_webdav_disable_check', control: 'switch', icon: 'mdi-lock-check-outline', label: '跳过证书校验（自签名时启用）' },
]);
const webdavFields = computed$7(() => (props.fields.length ? props.fields : fallbackFields.value).map(field => ({
  ...field,
  min: field.key === 'backup_webdav_max_count' ? (field.min ?? 1) : field.min,
  max: field.key === 'backup_webdav_max_count' ? (field.max ?? 30) : field.max,
  disabled: configDisabled.value || Boolean(field.disabled),
})));

return (_ctx, _cache) => {
  return (_openBlock$7(), _createElementBlock$6("div", {
    class: "aoa-backup-config-panel",
    "data-backup-config-panel": "webdav",
    "data-backup-configured": webdavConfigured.value ? 'true' : 'false',
    "data-backup-config-disabled": configDisabled.value ? 'true' : 'false'
  }, [
    _createVNode$5(_sfc_main$m, {
      class: "aoa-backup-config-fields",
      "data-backup-config-fields": "webdav",
      fields: webdavFields.value,
      form: __props.form,
      grid: "grid-2",
      "active-sub": "backup",
      "field-defaults": { hideInlineLabel: true, hideDetails: true, density: 'compact' }
    }, null, 8, ["fields", "form"]),
    _createVNode$5(_sfc_main$9, {
      channel: "webdav",
      title: "恢复远端备份",
      note: "从远端备份包下载到本地后恢复配置、Cookies 或数据库",
      restore: __props.webdavBackupRestore,
      archives: __props.webdavBackupArchives,
      "archives-loading": __props.webdavBackupArchivesLoading,
      "restore-loading": __props.webdavBackupRestoreLoading,
      result: __props.webdavBackupRestoreResult,
      unavailable: __props.webdavBackupRestoreUnavailable,
      "unavailable-message": __props.webdavBackupRestoreUnavailableMessage,
      "archive-label": "选择远端备份包",
      "archive-icon": "mdi-cloud-search-outline",
      "no-data-text": "暂无远端可恢复备份包",
      "refresh-label": "刷新远端",
      "refresh-icon": "mdi-cloud-sync-outline",
      "confirm-label": "确认下载并覆盖当前配置",
      "preview-label": "预览远端恢复",
      "run-label": "恢复远端备份",
      "run-icon": "mdi-cloud-refresh-outline",
      "fallback-result-text": "WebDAV 备份恢复已返回结果",
      onRefresh: _cache[0] || (_cache[0] = $event => (emit('loadWebdavBackupArchives'))),
      onPreview: _cache[1] || (_cache[1] = $event => (emit('previewWebdavBackupRestore'))),
      onRun: _cache[2] || (_cache[2] = $event => (emit('runWebdavBackupRestore')))
    }, null, 8, ["restore", "archives", "archives-loading", "restore-loading", "result", "unavailable", "unavailable-message"])
  ], 8, _hoisted_1$6))
}
}

};

const {createVNode:_createVNode$4,openBlock:_openBlock$6,createBlock:_createBlock$4,createCommentVNode:_createCommentVNode$5,renderSlot:_renderSlot$3,createElementBlock:_createElementBlock$5,withCtx:_withCtx$4} = await importShared('vue');


const _hoisted_1$5 = ["data-backup-active-module"];
const _hoisted_2$5 = {
  key: 2,
  class: "aoa-config-category-actions",
  "data-backup-detail-actions": ""
};


const _sfc_main$6 = {
  __name: 'BackupManagementConfig',
  props: {
  form: { type: Object, required: true },
  selectors: { type: Array, default: () => [] },
  detail: { type: Object, default: null },
  actions: { type: Array, default: () => [] },
  activeModule: { type: String, default: '' },
  effectiveState: { type: String, default: '' },
  keepCountPresets: { type: Array, default: () => [] },
  backupRestoreUnavailable: { type: Boolean, default: false },
  backupRestoreUnavailableMessage: { type: String, default: '' },
  backupArchives: { type: Array, default: () => [] },
  backupArchivesLoading: { type: Boolean, default: false },
  backupRestoreLoading: { type: Boolean, default: false },
  backupRestoreResult: { type: Object, default: null },
  backupRestore: { type: Object, required: true },
  webdavBackupRestoreUnavailable: { type: Boolean, default: false },
  webdavBackupRestoreUnavailableMessage: { type: String, default: '' },
  webdavBackupArchives: { type: Array, default: () => [] },
  webdavBackupArchivesLoading: { type: Boolean, default: false },
  webdavBackupRestoreLoading: { type: Boolean, default: false },
  webdavBackupRestoreResult: { type: Object, default: null },
  webdavBackupRestore: { type: Object, required: true },
},
  emits: [
  'selectModule',
  'loadBackupArchives',
  'previewBackupRestore',
  'runBackupRestore',
  'loadWebdavBackupArchives',
  'previewWebdavBackupRestore',
  'runWebdavBackupRestore',
],
  setup(__props, { emit: __emit }) {



const emit = __emit;

return (_ctx, _cache) => {
  return (_openBlock$6(), _createElementBlock$5("div", {
    class: "aoa-config-category-management aoa-backup-management-config",
    "data-backup-management-surface": "",
    "data-backup-active-module": __props.activeModule || undefined
  }, [
    _createVNode$4(_sfc_main$a, {
      form: __props.form,
      selectors: __props.selectors,
      "active-module": __props.activeModule,
      domain: "backup",
      onSelectModule: _cache[0] || (_cache[0] = $event => (emit('selectModule', $event)))
    }, null, 8, ["form", "selectors", "active-module"]),
    (__props.detail)
      ? (_openBlock$6(), _createBlock$4(_sfc_main$r, {
          key: 0,
          card: __props.detail,
          "effective-state": __props.effectiveState,
          class: "aoa-config-category-detail",
          "data-backup-detail-card": __props.detail.module,
          "data-task-detail-card": __props.detail.module
        }, {
          default: _withCtx$4(() => [
            (__props.detail.module === 'backup_webdav')
              ? (_openBlock$6(), _createBlock$4(_sfc_main$7, {
                  key: 0,
                  form: __props.form,
                  fields: __props.detail.fields,
                  "keep-count-presets": __props.keepCountPresets,
                  "webdav-backup-restore-unavailable": __props.webdavBackupRestoreUnavailable,
                  "webdav-backup-restore-unavailable-message": __props.webdavBackupRestoreUnavailableMessage,
                  "webdav-backup-archives": __props.webdavBackupArchives,
                  "webdav-backup-archives-loading": __props.webdavBackupArchivesLoading,
                  "webdav-backup-restore-loading": __props.webdavBackupRestoreLoading,
                  "webdav-backup-restore-result": __props.webdavBackupRestoreResult,
                  "webdav-backup-restore": __props.webdavBackupRestore,
                  onLoadWebdavBackupArchives: _cache[1] || (_cache[1] = $event => (emit('loadWebdavBackupArchives'))),
                  onPreviewWebdavBackupRestore: _cache[2] || (_cache[2] = $event => (emit('previewWebdavBackupRestore'))),
                  onRunWebdavBackupRestore: _cache[3] || (_cache[3] = $event => (emit('runWebdavBackupRestore')))
                }, null, 8, ["form", "fields", "keep-count-presets", "webdav-backup-restore-unavailable", "webdav-backup-restore-unavailable-message", "webdav-backup-archives", "webdav-backup-archives-loading", "webdav-backup-restore-loading", "webdav-backup-restore-result", "webdav-backup-restore"]))
              : (_openBlock$6(), _createBlock$4(_sfc_main$8, {
                  key: 1,
                  form: __props.form,
                  fields: __props.detail.fields,
                  "backup-restore-unavailable": __props.backupRestoreUnavailable,
                  "backup-restore-unavailable-message": __props.backupRestoreUnavailableMessage,
                  "backup-archives": __props.backupArchives,
                  "backup-archives-loading": __props.backupArchivesLoading,
                  "backup-restore-loading": __props.backupRestoreLoading,
                  "backup-restore-result": __props.backupRestoreResult,
                  "backup-restore": __props.backupRestore,
                  onLoadBackupArchives: _cache[4] || (_cache[4] = $event => (emit('loadBackupArchives'))),
                  onPreviewBackupRestore: _cache[5] || (_cache[5] = $event => (emit('previewBackupRestore'))),
                  onRunBackupRestore: _cache[6] || (_cache[6] = $event => (emit('runBackupRestore')))
                }, null, 8, ["form", "fields", "backup-restore-unavailable", "backup-restore-unavailable-message", "backup-archives", "backup-archives-loading", "backup-restore-loading", "backup-restore-result", "backup-restore"])),
            (__props.actions.length)
              ? (_openBlock$6(), _createElementBlock$5("div", _hoisted_2$5, [
                  _renderSlot$3(_ctx.$slots, "actions", { actions: __props.actions })
                ]))
              : _createCommentVNode$5("", true)
          ]),
          _: 3
        }, 8, ["card", "effective-state", "data-backup-detail-card", "data-task-detail-card"]))
      : _createCommentVNode$5("", true)
  ], 8, _hoisted_1$5))
}
}

};

const subfillRuleFields = Object.freeze([
  Object.freeze({ key: 'category', label: '二级分类', required: true }),
  Object.freeze({ key: 'resolution', label: '分辨率' }),
  Object.freeze({ key: 'quality', label: '资源质量' }),
  Object.freeze({ key: 'effect', label: '特效' }),
  Object.freeze({ key: 'include', label: '包含规则' }),
  Object.freeze({ key: 'exclude', label: '排除规则' }),
  Object.freeze({ key: 'sites', label: '站点名称' }),
  Object.freeze({ key: 'filter_groups', label: '过滤规则组' }),
  Object.freeze({ key: 'savepath', label: '保存路径' }),
]);

const fieldByKey = new Map(subfillRuleFields.map(field => [field.key, field]));
const fillKeys = new Set(subfillRuleFields.map(field => field.key).filter(key => key !== 'category'));

function splitRuleTokens(line) {
  const tokens = [];
  let token = '';
  for (let index = 0; index < line.length; index += 1) {
    const character = line[index];
    if (character === '\\' && line[index + 1] === '#') {
      token += '#';
      index += 1;
    } else if (character === '#') {
      tokens.push(token);
      token = '';
    } else {
      token += character;
    }
  }
  tokens.push(token);
  return tokens
}

function lineError(lineNumber, message) {
  return `第 ${lineNumber} 行：${message}`
}

function parseSubfillRuleLine(rawLine = '', lineNumber = 1) {
  const values = Object.fromEntries(subfillRuleFields.map(field => [field.key, '']));
  const fields = [];
  const errors = [];
  const seen = new Set();

  for (const rawToken of splitRuleTokens(String(rawLine))) {
    const token = rawToken.trim();
    if (!token) {
      errors.push(lineError(lineNumber, '存在空字段'));
      continue
    }
    const separator = token.indexOf(':');
    if (separator <= 0) {
      errors.push(lineError(lineNumber, `“${token}”缺少 字段:值`));
      continue
    }
    const key = token.slice(0, separator).trim();
    const value = token.slice(separator + 1).trim();
    const definition = fieldByKey.get(key);
    if (!definition) {
      errors.push(lineError(lineNumber, `不支持字段“${key || token}”`));
      continue
    }
    if (!value) errors.push(lineError(lineNumber, `字段“${key}”不能为空`));
    if (seen.has(key)) errors.push(lineError(lineNumber, `字段“${key}”重复出现`));
    seen.add(key);
    values[key] = value;
    fields.push(Object.freeze({ key, label: definition.label, value, duplicate: fields.some(field => field.key === key) }));
  }

  if (!values.category) errors.push(lineError(lineNumber, '缺少二级分类 category'));
  if (!fields.some(field => fillKeys.has(field.key) && field.value)) {
    errors.push(lineError(lineNumber, '至少需要一个填充字段'));
  }

  const uniqueErrors = [...new Set(errors)];
  const detailFields = fields.filter(field => field.key !== 'category');
  return Object.freeze({
    id: `subfill-line-${lineNumber}`,
    lineNumber,
    rawLine: String(rawLine),
    category: values.category,
    title: values.category || `第 ${lineNumber} 行`,
    values: Object.freeze(values),
    fields: Object.freeze(detailFields),
    errors: Object.freeze(uniqueErrors),
    valid: uniqueErrors.length === 0,
  })
}

function parseSubfillRules(text = '') {
  return String(text ?? '')
    .split(/\r?\n/u)
    .map((line, index) => ({ line, lineNumber: index + 1 }))
    .filter(({ line }) => line.trim())
    .map(({ line, lineNumber }) => parseSubfillRuleLine(line, lineNumber))
}

function validateSubfillRule(rule = {}) {
  return [...(rule.errors || [])]
}

const {unref:_unref$1,createElementVNode:_createElementVNode$1,toDisplayString:_toDisplayString$1,vModelText:_vModelText,withDirectives:_withDirectives,openBlock:_openBlock$5,createElementBlock:_createElementBlock$4,createCommentVNode:_createCommentVNode$4,createTextVNode:_createTextVNode,normalizeClass:_normalizeClass$1,renderList:_renderList$1,Fragment:_Fragment$1,mergeProps:_mergeProps$1} = await importShared('vue');


const _hoisted_1$4 = ["data-subfill-rule-state"];
const _hoisted_2$4 = ["data-subfill-projection-open"];
const _hoisted_3$1 = ["data-subfill-projection-open"];
const _hoisted_4$1 = { class: "aoa-subfill-code__controls" };
const _hoisted_5$1 = { class: "aoa-subfill-code__input" };
const _hoisted_6$1 = { class: "aoa-subfill-code__heading" };
const _hoisted_7$1 = ["data-tone"];
const _hoisted_8$1 = ["disabled", "aria-invalid"];
const _hoisted_9$1 = {
  class: "aoa-subfill-projection-shell",
  "data-subfill-projection-shell": ""
};
const _hoisted_10$1 = ["aria-expanded"];
const _hoisted_11$1 = { class: "aoa-subfill-projection-toggle__label" };
const _hoisted_12$1 = { key: 0 };
const _hoisted_13$1 = ["d"];
const _hoisted_14$1 = {
  key: 0,
  class: "aoa-subfill-projection__empty",
  "data-subfill-code-empty": ""
};
const _hoisted_15$1 = {
  key: 1,
  class: "aoa-subfill-projection__list",
  "data-subfill-code-card-list": ""
};
const _hoisted_16$1 = ["id", "data-subfill-code-line", "data-subfill-code-valid"];
const _hoisted_17$1 = ["id", "aria-expanded", "aria-controls", "title", "onClick"];
const _hoisted_18$1 = { class: "aoa-subfill-code-card__line" };
const _hoisted_19$1 = { class: "aoa-subfill-code-card__title" };
const _hoisted_20$1 = { class: "aoa-subfill-code-card__summary" };
const _hoisted_21$1 = { key: 0 };
const _hoisted_22$1 = ["d"];
const _hoisted_23$1 = ["id", "aria-labelledby"];
const _hoisted_24$1 = {
  key: 0,
  class: "aoa-subfill-code-card__fields"
};
const _hoisted_25$1 = { key: 0 };
const _hoisted_26$1 = {
  key: 1,
  class: "aoa-subfill-code-card__errors",
  role: "alert",
  "data-subfill-code-errors": ""
};

const {computed: computed$6,nextTick: nextTick$1,ref: ref$7,useAttrs} = await importShared('vue');


const _sfc_main$5 = /*@__PURE__*/Object.assign({ inheritAttrs: false }, {
  __name: 'SubfillRuleEditor',
  props: {
  values: { type: Object, required: true },
  disabled: { type: Boolean, default: false },
},
  emits: ['projection-change'],
  setup(__props, { emit: __emit }) {

const props = __props;
const emit = __emit;

const attrs = useAttrs();

const projectionOpen = ref$7(false);
const expandedRuleId = ref$7(null);
const projectionPanel = ref$7(null);
const ruleCards = new Map();
const codeText = computed$6({
  get: () => String(props.values.subfill_category_confs ?? ''),
  set: value => { props.values.subfill_category_confs = String(value ?? ''); },
});
const rules = computed$6(() => parseSubfillRules(codeText.value));
const errorCount = computed$6(() => rules.value.reduce((count, rule) => count + validateSubfillRule(rule).length, 0));
const ruleState = computed$6(() => {
  if (!codeText.value.trim()) return 'empty'
  return errorCount.value > 0 ? 'invalid' : 'valid'
});
const ruleSummary = computed$6(() => {
  if (ruleState.value === 'empty') return '尚未配置规则'
  if (ruleState.value === 'invalid') return `${rules.value.length} 条规则，${errorCount.value} 个错误`
  return `${rules.value.length} 条规则，校验通过`
});

function isExpanded(ruleId) {
  return expandedRuleId.value === ruleId
}

function setRuleCardRef(ruleId, element) {
  if (element) ruleCards.set(ruleId, element);
  else ruleCards.delete(ruleId);
}

async function revealWithinNearestScroller(element) {
  await nextTick$1();
  element.value?.scrollIntoView?.({ block: 'nearest', inline: 'nearest' });
}

async function toggleRule(ruleId) {
  const nextRuleId = expandedRuleId.value === ruleId ? null : ruleId;
  expandedRuleId.value = nextRuleId;
  if (!nextRuleId) return

  await nextTick$1();
  const card = ruleCards.get(nextRuleId);
  card?.scrollIntoView?.({ block: 'nearest', inline: 'nearest' });
}

async function toggleProjection() {
  const nextOpen = !projectionOpen.value;
  projectionOpen.value = nextOpen;
  expandedRuleId.value = null;
  emit('projection-change', nextOpen);
  if (nextOpen) await revealWithinNearestScroller(projectionPanel);
}

return (_ctx, _cache) => {
  return (_openBlock$5(), _createElementBlock$4("div", _mergeProps$1(_unref$1(attrs), {
    class: "aoa-subfill-editor-container",
    "data-subfill-editor-container": "",
    "data-subfill-rule-state": ruleState.value
  }), [
    _createElementVNode$1("div", {
      class: "aoa-subfill-editor-layout",
      "data-subfill-projection-open": projectionOpen.value ? 'true' : 'false',
      "data-subfill-editor-layout": ""
    }, [
      _createElementVNode$1("section", {
        class: _normalizeClass$1(["aoa-subfill-code", { 'aoa-subfill-code--disabled': __props.disabled }]),
        "data-subfill-code-editor": "",
        "data-subfill-projection-open": projectionOpen.value ? 'true' : 'false'
      }, [
        _createElementVNode$1("div", _hoisted_4$1, [
          _createElementVNode$1("label", _hoisted_5$1, [
            _createElementVNode$1("span", _hoisted_6$1, [
              _cache[1] || (_cache[1] = _createElementVNode$1("strong", null, "规则代码", -1)),
              _createElementVNode$1("small", {
                "data-tone": ruleState.value === 'invalid' ? 'error' : 'neutral'
              }, _toDisplayString$1(ruleSummary.value), 9, _hoisted_7$1)
            ]),
            _withDirectives(_createElementVNode$1("textarea", {
              "onUpdate:modelValue": _cache[0] || (_cache[0] = $event => ((codeText).value = $event)),
              rows: "6",
              spellcheck: "false",
              disabled: __props.disabled,
              "aria-invalid": ruleState.value === 'invalid',
              "aria-describedby": "aoa-subfill-code-help",
              "data-subfill-code-input": "",
              placeholder: "category:动画/日番#resolution:1080p#include:简体#sites:观众,青蛙"
            }, null, 8, _hoisted_8$1), [
              [_vModelText, codeText.value]
            ]),
            _cache[2] || (_cache[2] = _createElementVNode$1("small", {
              id: "aoa-subfill-code-help",
              class: "aoa-subfill-code__help"
            }, " 每行一条规则；展开图形化后可逐项核对字段与错误，投影不会改写规则代码。 ", -1))
          ])
        ]),
        _createElementVNode$1("div", _hoisted_9$1, [
          _createElementVNode$1("button", {
            type: "button",
            class: "aoa-subfill-projection-toggle",
            "aria-expanded": projectionOpen.value,
            "aria-controls": "aoa-subfill-projection-panel",
            "data-subfill-projection-toggle": "",
            onClick: toggleProjection
          }, [
            _createElementVNode$1("span", _hoisted_11$1, _toDisplayString$1(projectionOpen.value ? '收起图形化' : '展开图形化'), 1),
            _createElementVNode$1("span", {
              class: _normalizeClass$1(["aoa-subfill-projection-toggle__meta", { 'aoa-subfill-projection-toggle__meta--error': errorCount.value }])
            }, [
              _createTextVNode(_toDisplayString$1(rules.value.length) + " 条", 1),
              (errorCount.value)
                ? (_openBlock$5(), _createElementBlock$4("span", _hoisted_12$1, " · " + _toDisplayString$1(errorCount.value) + " 个错误", 1))
                : _createCommentVNode$4("", true)
            ], 2),
            (_openBlock$5(), _createElementBlock$4("svg", {
              class: _normalizeClass$1(["aoa-subfill-projection-toggle__chevron", { 'aoa-subfill-projection-toggle__chevron--open': projectionOpen.value }]),
              viewBox: "0 0 24 24",
              width: "18",
              height: "18",
              "aria-hidden": "true"
            }, [
              _createElementVNode$1("path", {
                d: _unref$1(mdiChevronDown),
                fill: "currentColor"
              }, null, 8, _hoisted_13$1)
            ], 2))
          ], 8, _hoisted_10$1)
        ])
      ], 10, _hoisted_3$1),
      (projectionOpen.value)
        ? (_openBlock$5(), _createElementBlock$4("section", {
            key: 0,
            ref_key: "projectionPanel",
            ref: projectionPanel,
            id: "aoa-subfill-projection-panel",
            class: "aoa-subfill-projection",
            "data-subfill-code-projection": ""
          }, [
            (!rules.value.length)
              ? (_openBlock$5(), _createElementBlock$4("div", _hoisted_14$1, " 暂无规则 "))
              : (_openBlock$5(), _createElementBlock$4("div", _hoisted_15$1, [
                  (_openBlock$5(true), _createElementBlock$4(_Fragment$1, null, _renderList$1(rules.value, (rule) => {
                    return (_openBlock$5(), _createElementBlock$4("article", {
                      ref_for: true,
                      ref: element => setRuleCardRef(rule.id, element),
                      id: `subfill-rule-panel-${rule.lineNumber}`,
                      key: rule.id,
                      class: _normalizeClass$1(["aoa-subfill-code-card", { 'aoa-subfill-code-card--error': !rule.valid }]),
                      "data-subfill-code-line": rule.lineNumber,
                      "data-subfill-code-valid": rule.valid
                    }, [
                      _createElementVNode$1("button", {
                        id: `subfill-rule-toggle-${rule.lineNumber}`,
                        type: "button",
                        class: "aoa-subfill-code-card__toggle",
                        "aria-expanded": isExpanded(rule.id),
                        "aria-controls": `subfill-rule-content-${rule.lineNumber}`,
                        title: isExpanded(rule.id) ? '收起' : '展开',
                        onClick: $event => (toggleRule(rule.id))
                      }, [
                        _createElementVNode$1("span", _hoisted_18$1, "第 " + _toDisplayString$1(rule.lineNumber) + " 行", 1),
                        _createElementVNode$1("span", _hoisted_19$1, _toDisplayString$1(rule.title), 1),
                        _createElementVNode$1("span", _hoisted_20$1, [
                          _createTextVNode(_toDisplayString$1(rule.fields.length) + " 个字段", 1),
                          (rule.errors.length)
                            ? (_openBlock$5(), _createElementBlock$4("span", _hoisted_21$1, " · " + _toDisplayString$1(rule.errors.length) + " 个错误", 1))
                            : _createCommentVNode$4("", true)
                        ]),
                        (_openBlock$5(), _createElementBlock$4("svg", {
                          class: _normalizeClass$1(["aoa-subfill-code-card__chevron", { 'aoa-subfill-code-card__chevron--open': isExpanded(rule.id) }]),
                          viewBox: "0 0 24 24",
                          width: "18",
                          height: "18",
                          "aria-hidden": "true"
                        }, [
                          _createElementVNode$1("path", {
                            d: _unref$1(mdiChevronDown),
                            fill: "currentColor"
                          }, null, 8, _hoisted_22$1)
                        ], 2))
                      ], 8, _hoisted_17$1),
                      (isExpanded(rule.id))
                        ? (_openBlock$5(), _createElementBlock$4("div", {
                            key: 0,
                            id: `subfill-rule-content-${rule.lineNumber}`,
                            class: "aoa-subfill-code-card__content",
                            role: "region",
                            "aria-labelledby": `subfill-rule-toggle-${rule.lineNumber}`,
                            "data-subfill-rule-content": ""
                          }, [
                            (rule.fields.length)
                              ? (_openBlock$5(), _createElementBlock$4("dl", _hoisted_24$1, [
                                  (_openBlock$5(true), _createElementBlock$4(_Fragment$1, null, _renderList$1(rule.fields, (field, fieldIndex) => {
                                    return (_openBlock$5(), _createElementBlock$4("div", {
                                      key: `${field.key}-${fieldIndex}`
                                    }, [
                                      _createElementVNode$1("dt", null, [
                                        _createTextVNode(_toDisplayString$1(field.label), 1),
                                        (field.duplicate)
                                          ? (_openBlock$5(), _createElementBlock$4("span", _hoisted_25$1, "（重复）"))
                                          : _createCommentVNode$4("", true)
                                      ]),
                                      _createElementVNode$1("dd", null, _toDisplayString$1(field.value || '空值'), 1)
                                    ]))
                                  }), 128))
                                ]))
                              : _createCommentVNode$4("", true),
                            (rule.errors.length)
                              ? (_openBlock$5(), _createElementBlock$4("div", _hoisted_26$1, [
                                  (_openBlock$5(true), _createElementBlock$4(_Fragment$1, null, _renderList$1(rule.errors, (error) => {
                                    return (_openBlock$5(), _createElementBlock$4("span", { key: error }, _toDisplayString$1(error), 1))
                                  }), 128))
                                ]))
                              : _createCommentVNode$4("", true)
                          ], 8, _hoisted_23$1))
                        : _createCommentVNode$4("", true)
                    ], 10, _hoisted_16$1))
                  }), 128))
                ]))
          ], 512))
        : _createCommentVNode$4("", true)
    ], 8, _hoisted_2$4)
  ], 16, _hoisted_1$4))
}
}

});

const {createVNode:_createVNode$3,openBlock:_openBlock$4,createBlock:_createBlock$3,createCommentVNode:_createCommentVNode$3,renderSlot:_renderSlot$2,createElementBlock:_createElementBlock$3,withCtx:_withCtx$3} = await importShared('vue');


const _hoisted_1$3 = ["data-subfill-active-module"];
const _hoisted_2$3 = {
  key: 1,
  class: "aoa-config-category-actions",
  "data-subfill-detail-actions": ""
};


const _sfc_main$4 = {
  __name: 'SubscriptionFillConfig',
  props: {
  form: { type: Object, required: true },
  selectors: { type: Array, default: () => [] },
  detail: { type: Object, default: null },
  actions: { type: Array, default: () => [] },
  activeModule: { type: String, default: '' },
  effectiveState: { type: String, default: '' },
},
  emits: ['selectModule', 'projectionChange'],
  setup(__props, { emit: __emit }) {



const emit = __emit;

return (_ctx, _cache) => {
  return (_openBlock$4(), _createElementBlock$3("div", {
    class: "aoa-config-category-management aoa-subfill-management-config",
    "data-subfill-management-surface": "",
    "data-subfill-layout-container": "",
    "data-subfill-active-module": __props.activeModule || undefined
  }, [
    _createVNode$3(_sfc_main$a, {
      form: __props.form,
      selectors: __props.selectors,
      "active-module": __props.activeModule,
      domain: "subfill",
      onSelectModule: _cache[0] || (_cache[0] = $event => (emit('selectModule', $event)))
    }, null, 8, ["form", "selectors", "active-module"]),
    (__props.detail)
      ? (_openBlock$4(), _createBlock$3(_sfc_main$r, {
          key: 0,
          card: __props.detail,
          "effective-state": __props.effectiveState,
          class: "aoa-config-category-detail",
          "data-subfill-detail-card": __props.detail.module,
          "data-subfill-module-card": __props.detail.module,
          "data-task-detail-card": __props.detail.module
        }, {
          default: _withCtx$3(() => [
            (__props.detail.module === 'subfill_category')
              ? (_openBlock$4(), _createBlock$3(_sfc_main$5, {
                  key: 0,
                  values: __props.form,
                  "data-effective-state": __props.effectiveState || undefined,
                  onProjectionChange: _cache[1] || (_cache[1] = $event => (emit('projectionChange', $event)))
                }, null, 8, ["values", "data-effective-state"]))
              : _createCommentVNode$3("", true),
            _createVNode$3(_sfc_main$m, {
              fields: __props.detail.fields || [],
              form: __props.form,
              grid: __props.detail.grid || 'grid-2',
              "active-sub": "subfill",
              "field-defaults": { hideInlineLabel: true, hideDetails: true, density: 'compact' },
              "data-subfill-detail-fields": ""
            }, null, 8, ["fields", "form", "grid"]),
            (__props.actions.length)
              ? (_openBlock$4(), _createElementBlock$3("div", _hoisted_2$3, [
                  _renderSlot$2(_ctx.$slots, "actions", { actions: __props.actions })
                ]))
              : _createCommentVNode$3("", true)
          ]),
          _: 3
        }, 8, ["card", "effective-state", "data-subfill-detail-card", "data-subfill-module-card", "data-task-detail-card"]))
      : _createCommentVNode$3("", true)
  ], 8, _hoisted_1$3))
}
}

};

const {createVNode:_createVNode$2,renderSlot:_renderSlot$1,openBlock:_openBlock$3,createElementBlock:_createElementBlock$2,createCommentVNode:_createCommentVNode$2,withCtx:_withCtx$2,createBlock:_createBlock$2} = await importShared('vue');


const _hoisted_1$2 = ["data-update-active-module", "data-effective-state"];
const _hoisted_2$2 = ["data-update-detail-actions"];


const _sfc_main$3 = {
  __name: 'UpdateManagementConfig',
  props: {
  form: { type: Object, required: true },
  selectors: { type: Array, default: () => [] },
  detail: { type: Object, default: null },
  activeModule: { type: String, default: '' },
  effectiveState: { type: String, default: '' },
},
  emits: ['selectModule'],
  setup(__props, { emit: __emit }) {



const emit = __emit;

return (_ctx, _cache) => {
  return (_openBlock$3(), _createElementBlock$2("div", {
    class: "aoa-config-category-management aoa-update-management-config",
    "data-update-management-surface": "",
    "data-update-active-module": __props.activeModule || undefined,
    "data-effective-state": __props.effectiveState || undefined,
    role: "group",
    "aria-label": "更新管理配置"
  }, [
    _createVNode$2(_sfc_main$a, {
      form: __props.form,
      selectors: __props.selectors,
      "active-module": __props.activeModule,
      domain: "update",
      onSelectModule: _cache[0] || (_cache[0] = $event => (emit('selectModule', $event)))
    }, null, 8, ["form", "selectors", "active-module"]),
    (__props.detail)
      ? (_openBlock$3(), _createBlock$2(_sfc_main$r, {
          key: 0,
          card: __props.detail,
          "effective-state": __props.effectiveState,
          class: "aoa-config-category-detail",
          "data-update-detail-card": __props.detail.module,
          "data-update-module-card": __props.detail.module,
          "data-task-detail-card": __props.detail.module
        }, {
          default: _withCtx$2(() => [
            _createVNode$2(_sfc_main$m, {
              fields: __props.detail.fields || [],
              form: __props.form,
              grid: __props.detail.grid || 'grid-2',
              "active-sub": "updates",
              "field-defaults": { hideInlineLabel: true, hideDetails: true, density: 'compact' },
              "data-update-detail-fields": ""
            }, null, 8, ["fields", "form", "grid"]),
            (__props.detail.actions?.length)
              ? (_openBlock$3(), _createElementBlock$2("div", {
                  key: 0,
                  class: "aoa-config-category-actions",
                  "data-update-detail-actions": __props.detail.module
                }, [
                  _renderSlot$1(_ctx.$slots, "actions", {
                    actions: __props.detail.actions
                  })
                ], 8, _hoisted_2$2))
              : _createCommentVNode$2("", true)
          ]),
          _: 3
        }, 8, ["card", "effective-state", "data-update-detail-card", "data-update-module-card", "data-task-detail-card"]))
      : _createCommentVNode$2("", true)
  ], 8, _hoisted_1$2))
}
}

};

const {createVNode:_createVNode$1,renderSlot:_renderSlot,openBlock:_openBlock$2,createElementBlock:_createElementBlock$1,createCommentVNode:_createCommentVNode$1,withCtx:_withCtx$1} = await importShared('vue');


const _hoisted_1$1 = ["data-effective-state"];
const _hoisted_2$1 = {
  key: 0,
  class: "aoa-plugin-uninstall-actions",
  "data-plugin-uninstall-actions": ""
};

const {computed: computed$5} = await importShared('vue');


const _sfc_main$2 = {
  __name: 'PluginUninstallConfig',
  props: {
  form: { type: Object, required: true },
  card: { type: Object, required: true },
  actions: { type: Array, default: () => [] },
  effectiveState: { type: String, default: '' },
},
  setup(__props) {

const props = __props;

const uninstallCard = computed$5(() => ({
  ...props.card,
  danger: true,
}));

function uninstallFieldAttrs(field, index) {
  return {
    'data-plugin-uninstall-field': field.key,
    'data-plugin-uninstall-field-index': String(index),
  }
}

return (_ctx, _cache) => {
  return (_openBlock$2(), _createElementBlock$1("div", {
    class: "aoa-plugin-uninstall-config aoa-design-replica-stack",
    "data-plugin-uninstall-config-surface": "",
    "data-effective-state": __props.effectiveState || undefined,
    role: "group",
    "aria-label": "插件卸载配置"
  }, [
    _createVNode$1(_sfc_main$r, {
      card: uninstallCard.value,
      "effective-state": __props.effectiveState,
      "data-plugin-uninstall-fields-surface": "",
      "data-plugin-uninstall-fields-card": ""
    }, {
      default: _withCtx$1(() => [
        _createVNode$1(_sfc_main$m, {
          fields: __props.card.fields || [],
          form: __props.form,
          grid: __props.card.grid || 'grid-4',
          "active-sub": "clean",
          "field-defaults": { hideInlineLabel: true, hideDetails: true, density: 'compact' },
          "row-attrs": uninstallFieldAttrs,
          "data-plugin-uninstall-fields": ""
        }, null, 8, ["fields", "form", "grid"]),
        (__props.actions.length)
          ? (_openBlock$2(), _createElementBlock$1("div", _hoisted_2$1, [
              _renderSlot(_ctx.$slots, "actions", { actions: __props.actions })
            ]))
          : _createCommentVNode$1("", true)
      ]),
      _: 3
    }, 8, ["card", "effective-state"])
  ], 8, _hoisted_1$1))
}
}

};

const EFFECTIVE_STATE = Object.freeze({
  ACTIVE: 'active',
  PLUGIN_DISABLED: 'plugin_disabled',
  COMPONENT_DISABLED: 'component_disabled',
  CONFIGURATION_MISSING: 'configuration_missing',
  SCHEDULE_DISABLED: 'schedule_disabled',
  CRON_MISSING: 'cron_missing',
});

function deriveEffectiveState({
  pluginEnabled = false,
  componentEnabled = false,
  requiredConfigReady = true,
  scheduleRequired = false,
  scheduleEnabled = true,
  cron = '',
  fusionNotificationManaged = false,
} = {}) {
  let code = EFFECTIVE_STATE.ACTIVE;
  if (!pluginEnabled) code = EFFECTIVE_STATE.PLUGIN_DISABLED;
  else if (!componentEnabled) code = EFFECTIVE_STATE.COMPONENT_DISABLED;
  else if (!requiredConfigReady) code = EFFECTIVE_STATE.CONFIGURATION_MISSING;
  else if (scheduleRequired && !scheduleEnabled) code = EFFECTIVE_STATE.SCHEDULE_DISABLED;
  else if (scheduleRequired && !String(cron || '').trim()) code = EFFECTIVE_STATE.CRON_MISSING;

  return Object.freeze({
    code,
    active: code === EFFECTIVE_STATE.ACTIVE,
    pluginEnabled: Boolean(pluginEnabled),
    componentEnabled: Boolean(componentEnabled),
    notificationManagedByFusion: Boolean(fusionNotificationManaged),
  })
}

// 配置页导航 tabs — 纯数据，无运行时依赖
const mainTabs = [
  { key: 'notify', title: '通知设置', icon: 'mdi-message-badge-outline', desc: '融合通知、媒体通知与订阅追新' },
  { key: 'monitor', title: '数据与监控', icon: 'mdi-chart-line', desc: '站点统计与健康巡查' },
  { key: 'download', title: '下载器管理', icon: 'mdi-download-network-outline', desc: '自动删种、下载器助手与订阅规则填充' },
  { key: 'maintenance', title: '系统维护', icon: 'mdi-cog-outline', desc: '自动备份、日志清理与更新管理' },
  { key: 'plugin', title: '插件卸载', icon: 'mdi-puzzle-remove-outline', desc: '安全卸载插件并清理残留' },
];

const subTabs = {
  notify: [
    { key: 'fusion', title: '融合通知', icon: 'mdi-message-badge-outline' },
    { key: 'server', title: '媒体通知', icon: 'mdi-television-play' },
    { key: 'subscribe', title: '订阅追新', icon: 'mdi-bell-ring-outline' },
  ],
  monitor: [
    { key: 'sites', title: '站点统计', icon: 'mdi-chart-line' },
    { key: 'hc', title: '健康巡查', icon: 'mdi-heart-pulse' },
  ],
  download: [
    { key: 'seedremove', title: '自动删种', icon: 'mdi-delete-sweep-outline' },
    { key: 'dltagmain', title: '下载器助手', icon: 'mdi-download-network-outline' },
    { key: 'subfill', title: '订阅规则填充', icon: 'mdi-auto-fix' },
  ],
  maintenance: [
    { key: 'backup', title: '自动备份', icon: 'mdi-archive-arrow-up-outline' },
    { key: 'logs', title: '日志清理', icon: 'mdi-file-document-remove-outline' },
    { key: 'updates', title: '更新管理', icon: 'mdi-update' },
  ],
  plugin: [
    { key: 'clean', title: '安全卸载', icon: 'mdi-puzzle-remove-outline' },
  ],
};

const {ref: ref$6} = await importShared('vue');

// 远程数据加载 — 插件列表 / TG 控制台 / 插件市场 / 下载器 / 媒体服务器
// 入参：api(MP 插件 API 句柄)
function useDataLoader(api) {
  // 已安装插件列表（插件卸载用）
  const installedPlugins = ref$6([]);
  const installedLoading = ref$6(false);
  async function loadInstalledPlugins({ throwOnError = false } = {}) {
    installedLoading.value = true;
    try {
      const res = await getPluginApi(api, 'installed_plugins');
      installedPlugins.value = Array.isArray(res) ? res : (res?.data || []);
      return { ok: true, data: installedPlugins.value }
    } catch (error) {
      installedPlugins.value = [];
      if (throwOnError) throw error
      return { ok: false, error }
    } finally {
      installedLoading.value = false;
    }
  }

  // TG 控制台状态
  const tgConsoleStatus = ref$6({});
  const tgConsoleLoading = ref$6(false);
  async function loadTgConsoleStatus() {
    tgConsoleLoading.value = true;
    try {
      const res = await getPluginApi(api, 'tg_console_status');
      const status = res?.data || res || {};
      tgConsoleStatus.value = status && typeof status === 'object' ? { ...status } : {};
    } catch (err) {
      tgConsoleStatus.value = { last_error: err?.message || '状态读取失败' };
    } finally {
      tgConsoleLoading.value = false;
    }
  }

  // 插件库仓库（更新黑名单用）
  const pluginMarkets = ref$6([]);
  const marketsLoading = ref$6(false);
  async function loadPluginMarkets() {
    marketsLoading.value = true;
    try {
      const res = await getPluginApi(api, 'plugin_markets');
      pluginMarkets.value = Array.isArray(res) ? res : (res?.data || []);
    } catch {
      pluginMarkets.value = [];
    } finally {
      marketsLoading.value = false;
    }
  }

  // 下载器列表（自动删种用）
  const downloaderOptions = ref$6([]);
  const downloadersLoading = ref$6(false);
  async function loadDownloaders() {
    downloadersLoading.value = true;
    try {
      const res = await getPluginApi(api, 'downloaders');
      downloaderOptions.value = Array.isArray(res) ? res : (res?.data || []);
    } catch {
      downloaderOptions.value = [];
    } finally {
      downloadersLoading.value = false;
    }
  }

  // 媒体服务器列表（媒体库通知按服务器过滤用）
  const mediaserverOptions = ref$6([]);
  const mediaserversLoading = ref$6(false);
  async function loadMediaservers() {
    mediaserversLoading.value = true;
    try {
      const res = await getPluginApi(api, 'mediaservers');
      mediaserverOptions.value = Array.isArray(res) ? res : (res?.data || []);
    } catch {
      mediaserverOptions.value = [];
    } finally {
      mediaserversLoading.value = false;
    }
  }

  // 一键加载全部
  function loadAll() {
    return Promise.allSettled([
      loadInstalledPlugins(),
      loadTgConsoleStatus(),
      loadPluginMarkets(),
      loadDownloaders(),
      loadMediaservers(),
    ])
  }

  return {
    installedPlugins, installedLoading, loadInstalledPlugins,
    tgConsoleStatus, tgConsoleLoading, loadTgConsoleStatus,
    pluginMarkets, marketsLoading, loadPluginMarkets,
    downloaderOptions, downloadersLoading, loadDownloaders,
    mediaserverOptions, mediaserversLoading, loadMediaservers,
    loadAll,
  }
}

const {computed: computed$4,reactive: reactive$2,watch: watch$4} = await importShared('vue');

const own = (source, key) => Object.prototype.hasOwnProperty.call(source, key);

function configBool(value, fallback = false) {
  if (typeof value === 'string') return !['', '0', 'false', 'no', 'off'].includes(value.trim().toLowerCase())
  return value == null ? Boolean(fallback) : Boolean(value)
}

const toArr = value => typeof value === 'string'
  ? value.split(',').map(item => item.trim()).filter(Boolean)
  : (Array.isArray(value) ? value : []);

const arrayKeys = [
  'subscribe_reminder_subtype', 'mp_update_types', 'plugin_uninstall_ids',
  'log_clean_selected_ids', 'market_update_install_ids', 'market_update_exclude_ids',
  'plugin_auto_install_install_ids', 'plugin_auto_install_exclude_ids', 'seedclean_downloaders',
  'subfill_details', 'msgnotify_types', 'msgnotify_servers', 'dltag_downloaders', 'dltag_tasks',
  'dltag_all_tags', 'dltag_excluded_tags', 'health_check_items', 'health_check_database_targets',
  'health_check_storage_targets', 'health_check_directory_targets',
];

/** Merge defaults, migrate legacy config keys, and normalize form-only values once. */
function hydrateConfigForm(rawConfig = {}) {
  const source = rawConfig && typeof rawConfig === 'object' && !Array.isArray(rawConfig) ? rawConfig : {};
  const form = {
    ...normalizeCurrentConfig(defaults),
    ...normalizeCurrentConfig(source),
  };

  if (!own(source, 'dltag_cron')) form.dltag_cron = DEFAULT_DLTAG_CRON;
  const inheritSchedule = (scheduleKey, enabledKey) => {
    if (!own(source, scheduleKey)) form[scheduleKey] = !!form[enabledKey];
  };
  inheritSchedule('subscribe_reminder_schedule_enabled', 'subscribe_reminder_enabled');
  inheritSchedule('health_check_schedule_enabled', 'health_check_enabled');
  inheritSchedule('log_clean_schedule_enabled', 'log_clean_enabled');
  inheritSchedule('mp_update_schedule_enabled', 'mp_update_enabled');
  inheritSchedule('market_update_schedule_enabled', 'market_update_enabled');
  inheritSchedule('seedclean_schedule_enabled', 'seedclean_enabled');

  if (!own(source, 'backup_webdav_enabled')) {
    form.backup_webdav_enabled = [source.backup_webdav_hostname, source.backup_webdav_login, source.backup_webdav_password]
      .every(value => String(value || '').trim().length > 0);
  } else {
    form.backup_webdav_enabled = configBool(source.backup_webdav_enabled);
  }

  const legacyMarketEnabled = configBool(source.market_update_enabled);
  const legacyMarketScheduleEnabled = own(source, 'market_update_schedule_enabled')
    ? configBool(source.market_update_schedule_enabled)
    : legacyMarketEnabled;
  const legacyMarketEffective = legacyMarketEnabled && legacyMarketScheduleEnabled;
  const hasCurrentPluginUpdateConfig = ['plugin_update_reminder_enabled', 'plugin_auto_install_enabled', 'plugin_auto_install_scope_mode']
    .some(key => own(source, key));
  const legacyStrategy = String(source.market_update_strategy || '').trim().toLowerCase();
  if (own(source, 'market_update_enabled') && !hasCurrentPluginUpdateConfig) form.market_update_enabled = legacyMarketEffective;
  if (!own(source, 'plugin_update_reminder_enabled')) form.plugin_update_reminder_enabled = legacyMarketEffective;
  if (!own(source, 'plugin_update_reminder_schedule_enabled')) form.plugin_update_reminder_schedule_enabled = legacyMarketScheduleEnabled;
  if (!own(source, 'plugin_update_reminder_cron') && own(source, 'market_update_cron')) form.plugin_update_reminder_cron = form.market_update_cron;
  if (!own(source, 'plugin_auto_install_enabled')) form.plugin_auto_install_enabled = legacyStrategy === 'install';
  if (!own(source, 'plugin_auto_install_schedule_enabled')) form.plugin_auto_install_schedule_enabled = legacyStrategy === 'install' && legacyMarketScheduleEnabled;
  if (!own(source, 'plugin_auto_install_cron') && own(source, 'market_update_cron')) form.plugin_auto_install_cron = form.market_update_cron;
  if (!own(source, 'plugin_auto_install_install_ids') && own(source, 'market_update_install_ids')) form.plugin_auto_install_install_ids = source.market_update_install_ids;
  if (!own(source, 'plugin_auto_install_exclude_ids') && own(source, 'market_update_exclude_ids')) form.plugin_auto_install_exclude_ids = source.market_update_exclude_ids;
  if (!own(source, 'plugin_auto_install_scope_mode')) {
    const legacyInstallIds = toArr(form.plugin_auto_install_install_ids);
    const legacyExcludeIds = toArr(form.plugin_auto_install_exclude_ids);
    if (legacyInstallIds.length && legacyExcludeIds.length) {
      const excluded = new Set(legacyExcludeIds);
      form.plugin_auto_install_install_ids = legacyInstallIds.filter(pluginId => !excluded.has(pluginId));
      form.plugin_auto_install_exclude_ids = [];
      form.plugin_auto_install_scope_mode = 'include';
    } else if (legacyInstallIds.length) {
      form.plugin_auto_install_scope_mode = 'include';
    } else if (legacyExcludeIds.length) {
      form.plugin_auto_install_scope_mode = 'exclude';
    } else {
      form.plugin_auto_install_scope_mode = 'all';
    }
  }

  for (const key of arrayKeys) form[key] = toArr(form[key]);
  return form
}

const snapshot = value => JSON.parse(JSON.stringify(value || {}));

function useConfigLifecycle({ initialConfig, configRecordState, api, pluginId, emit, validateSave, onValidationError }) {
  const form = reactive$2({});
  const savedSnapshot = reactive$2({});

  function applyHydratedConfig(rawConfig) {
    const hydrated = hydrateConfigForm(rawConfig);
    Object.keys(form).forEach(key => delete form[key]);
    Object.assign(form, hydrated);
    Object.keys(savedSnapshot).forEach(key => delete savedSnapshot[key]);
    Object.assign(savedSnapshot, snapshot(hydrated));
  }

  watch$4([initialConfig, configRecordState], ([value]) => applyHydratedConfig(value), { immediate: true, deep: true });

  const isDirty = computed$4(() => JSON.stringify(buildConfigSavePayload(form)) !== JSON.stringify(buildConfigSavePayload(savedSnapshot)));

  async function saveConfig() {
    if (validateSave && !validateSave()) {
      onValidationError?.('二级分类规则存在错误，请先修正后再保存');
      return { ok: false, reason: 'validation' }
    }
    const payload = emitConfigSave(emit, form);
    const apiClient = resolvePluginApi(api);
    if (apiClient?.put) await apiClient.put(`plugin/${pluginId}`, payload);
    else if (typeof apiClient === 'function') await apiClient({ method: 'put', url: `plugin/${pluginId}`, data: payload });
    Object.keys(savedSnapshot).forEach(key => delete savedSnapshot[key]);
    Object.assign(savedSnapshot, snapshot(payload));
    return { ok: true, payload }
  }

  return { form, isDirty, saveConfig, hydrateConfigForm: applyHydratedConfig }
}

const {ref: ref$5} = await importShared('vue');


const CARD_TYPE_TO_MODULE = Object.freeze({
  update: 'update',
  'update-selector': 'update',
  'update-detail': 'update',
  backup: 'backup',
  'backup-selector': 'backup',
  'backup-detail': 'backup',
  subfill: 'subfill',
  'subfill-selector': 'subfill',
  'subfill-detail': 'subfill',
});

/** Owns the detail-card selection and transient page state below the main config tabs. */
function useConfigPageSession() {
  const activeUpdateModule = ref$5('mp_update');
  const activeBackupModule = ref$5('backup');
  const activeSubfillModule = ref$5('subfill_download');
  const subfillProjectionOpen = ref$5(false);

  const moduleRefs = {
    update: activeUpdateModule,
    backup: activeBackupModule,
    subfill: activeSubfillModule,
  };

  function moduleKind(cardType) {
    return CARD_TYPE_TO_MODULE[cardType] || ''
  }

  function activeModuleFor(cardType) {
    const kind = moduleKind(cardType);
    return kind ? moduleRefs[kind] : null
  }

  function selectModule(cardType, module) {
    const target = activeModuleFor(cardType);
    const nextModule = String(module ?? '').trim();
    if (!target || !nextModule) return false
    target.value = nextModule;
    return true
  }

  function setSubfillProjectionOpen(value) {
    subfillProjectionOpen.value = Boolean(value);
    return subfillProjectionOpen.value
  }

  function resetSubfillProjection() {
    return setSubfillProjectionOpen(false)
  }

  return {
    activeUpdateModule,
    activeBackupModule,
    activeSubfillModule,
    subfillProjectionOpen,
    moduleKind,
    activeModuleFor,
    selectModule,
    setSubfillProjectionOpen,
    resetSubfillProjection,
  }
}

const {computed: computed$3,nextTick,reactive: reactive$1,ref: ref$4,watch: watch$3} = await importShared('vue');

const firstSubFor = mainKey => subTabs[mainKey]?.[0]?.key || '';

/** Owns config page navigation, sub-page session state and horizontal tab reveal. */
function useConfigNavigation({ pluginId = 'Signal', emit, saveConfig, onSubChange, root = null, pageSession = useConfigPageSession() } = {}) {
  const activeMain = ref$4(mainTabs[0]?.key || 'notify');
  const activeSub = ref$4(firstSubFor(activeMain.value));
  const {
    activeUpdateModule,
    activeBackupModule,
    activeSubfillModule,
    subfillProjectionOpen,
    activeModuleFor,
    selectModule,
    setSubfillProjectionOpen,
    resetSubfillProjection,
  } = pageSession;
  const saving = ref$4(false);
  const saveFeedback = reactive$1({ message: '', ok: true });
  const mainNav = ref$4(null);
  const subtabList = ref$4(null);

  const currentMain = computed$3(() => mainTabs.find(item => item.key === activeMain.value) || mainTabs[0]);
  const currentSubs = computed$3(() => subTabs[activeMain.value] || []);
  const currentSub = computed$3(() => currentSubs.value.find(item => item.key === activeSub.value) || currentSubs.value[0] || null);
  const currentSubTitle = computed$3(() => currentSub.value?.title || currentMain.value?.title || '');

  function selectMain(key) {
    if (!subTabs[key] || activeMain.value === key) return
    activeMain.value = key;
    selectSub(firstSubFor(key));
  }

  function selectSub(key) {
    const nextKey = currentSubs.value.some(item => item.key === key) ? key : firstSubFor(activeMain.value);
    if (!nextKey || activeSub.value === nextKey) return
    activeSub.value = nextKey;
  }

  function revealCategoryItem(target, behavior = 'smooth') {
    const container = target?.closest?.('[data-config-nav-scroll]');
    if (!container) return
    const containerRect = container.getBoundingClientRect();
    const targetRect = target.getBoundingClientRect();
    const inset = 8;
    let nextLeft = container.scrollLeft;
    if (targetRect.left < containerRect.left + inset) nextLeft -= containerRect.left + inset - targetRect.left;
    else if (targetRect.right > containerRect.right - inset) nextLeft += targetRect.right - containerRect.right + inset;
    if (Math.abs(nextLeft - container.scrollLeft) > 1) container.scrollTo({ left: nextLeft, behavior });
  }

  function revealActiveCategories(behavior = 'smooth') {
    nextTick(() => {
      revealCategoryItem(mainNav.value?.querySelector('[aria-selected="true"]'), behavior);
      revealCategoryItem(subtabList.value?.querySelector('[aria-selected="true"]'), behavior);
    });
  }

  watch$3([activeMain, activeSub], () => revealActiveCategories());
  watch$3(activeSub, value => {
    if (value !== 'subfill') resetSubfillProjection();
    onSubChange?.(value);
  });

  function switchPluginAppNav(navKey) {
    if (typeof window === 'undefined') return false
    const rootElement = typeof root === 'function' ? root() : root?.value ?? root;
    if (rootElement?.closest?.('[role="dialog"], .v-dialog, .v-overlay')) return false
    const prefix = `#/plugin-app/${pluginId}/`;
    if (!window.location.hash.startsWith(prefix)) return false
    window.location.hash = `${prefix}${navKey}`;
    return true
  }

  function openDashboard() {
    if (switchPluginAppNav('main')) return true
    emit?.('switch');
    return false
  }

  async function savePage() {
    if (saving.value || typeof saveConfig !== 'function') return { ok: false, reason: 'unavailable' }
    saving.value = true;
    saveFeedback.message = '';
    try {
      const result = await saveConfig();
      if (result?.ok === false) return result
      saveFeedback.ok = true;
      saveFeedback.message = '配置已保存';
      return result
    } catch (error) {
      saveFeedback.ok = false;
      saveFeedback.message = error?.message || '配置保存失败，请稍后重试';
      return { ok: false, reason: 'request', error }
    } finally {
      saving.value = false;
    }
  }

  return {
    activeMain, activeSub, activeUpdateModule, activeBackupModule, activeSubfillModule,
    subfillProjectionOpen, mainNav, subtabList,
    saving, saveFeedback,
    currentMain, currentSubs, currentSub, currentSubTitle,
    selectMain, selectSub, revealCategoryItem, revealActiveCategories,
    switchPluginAppNav, openDashboard, savePage,
    pageSession,
    activeModuleFor, selectModule, setSubfillProjectionOpen, resetSubfillProjection,
  }
}

const {computed: computed$2,ref: ref$3,watch: watch$2} = await importShared('vue');

const actionId = action => String(action?.id || action?.path || action?.apiPath || '');

function resolveList(value) {
  const resolved = value && typeof value === 'object' && Object.prototype.hasOwnProperty.call(value, 'value')
    ? value.value
    : value;
  return Array.isArray(resolved) ? resolved : []
}

/** Owns Config-specific action panel specs, lifecycle and operation-mode routing. */
function useConfigActionOperation(options = {}) {
  const {
    configRoot,
    form = {},
    action = {},
    installedPlugins = [],
    actionDisabledMessage = () => '',
    isActionRunning = () => false,
    runAction = async () => null,
  } = options;

  const activeActionOperationId = ref$3('');
  const actionOperationPortalStyle = ref$3({});
  const actionOperationSubmitting = ref$3(false);

  const downloaderHelperPreviewItems = computed$2(() => action.downloaderHelperPreview?.items || []);
  const selectedPluginUninstallItems = computed$2(() => {
    const selected = Array.isArray(form.plugin_uninstall_ids) ? form.plugin_uninstall_ids : [];
    const installed = resolveList(installedPlugins);
    return selected.map(id => {
      const value = String(id);
      const item = installed.find(candidate => String(candidate?.value ?? candidate?.id ?? candidate?.title ?? candidate) === value);
      return { value, title: String(item?.title ?? item?.name ?? value) }
    })
  });
  const pluginUninstallActionItems = computed$2(() => [
    { key: 'uninstall_plugin', label: '卸载插件本体', detail: '始终移出已安装列表、停止运行实例并删除运行目录' },
    ...[
      { key: 'plugin_uninstall_clear_config', label: '清除插件配置', detail: '删除 MoviePilot 保存的插件配置' },
      { key: 'plugin_uninstall_clear_data', label: '清除插件数据', detail: '删除插件运行数据' },
      { key: 'plugin_uninstall_delete_source', label: '删除源码', detail: '删除 MoviePilot 运行源码、本地插件源码目录及历史源码残留' },
    ].filter(item => Boolean(form[item.key])),
  ]);
  const seedCleanActionMeta = computed$2(() => ({
    pause: { label: '暂停种子', confirm: '确认暂停', risk: '所选种子将停止上传和下载，可在下载器中重新开始。' },
    delete: { label: '删除种子', confirm: '确认删除', risk: '所选任务将从下载器移除，但保留已下载文件。' },
    deletefile: { label: '删除种子和文件', confirm: '确认删除种子和文件', risk: '所选任务及其已下载文件将被永久删除，无法恢复。' },
  }[String(form.seedclean_action || 'pause')] || { label: '处理种子', confirm: '确认执行', risk: '将按当前动作处理匹配条件的种子。' }));
  const seedCleanFilterSummary = computed$2(() => {
    const rows = [
      ['大小', form.seedclean_size && `${form.seedclean_size} GB`],
      ['分享率', form.seedclean_ratio],
      ['做种时长', form.seedclean_time && `${form.seedclean_time} 小时`],
      ['上传上限', form.seedclean_upspeed && `${form.seedclean_upspeed} KB/s`],
      ['标签', form.seedclean_labels],
      ['路径正则', form.seedclean_pathkeywords],
      ['Tracker 正则', form.seedclean_trackerkeywords],
      ['qB 状态', form.seedclean_torrentstates],
      ['qB 分类', form.seedclean_torrentcategorys],
      ['TR 状态', form.seedclean_trtorrentstates],
      ['TR 错误', form.seedclean_errorkeywords],
    ].filter(([, value]) => String(value || '').trim());
    return rows.length ? rows.map(([label, value]) => `${label}：${value}`).join('；') : '未设置筛选条件'
  });

  const activeActionOperation = computed$2(() => activeActionOperationId.value
    ? getActionForSurface(activeActionOperationId.value, 'config')
    : null);

  const actionOperationSpec = computed$2(() => {
    const current = activeActionOperation.value;
    if (!current) return null
    if (current.id === 'run_seed_clean') {
      return {
        action: current,
        kicker: '请确认本次处理',
        title: seedCleanActionMeta.value.label,
        warning: seedCleanActionMeta.value.risk,
        danger: form.seedclean_action !== 'pause',
        summaryPrimary: `${form.seedclean_downloaders?.length || 0} 个下载器`,
        summarySecondary: '按当前条件执行',
        sections: [{
          key: 'seed-clean-scope',
          attrs: { 'data-seedclean-confirm-items': '' },
          items: [{
            key: 'seed-clean-current-scope',
            title: form.seedclean_downloaders?.join('、') || '未选择下载器',
            meta: seedCleanActionMeta.value.label,
            detail: seedCleanFilterSummary.value,
          }],
        }],
        confirmLabel: seedCleanActionMeta.value.confirm,
        cancelLabel: '返回修改',
        confirmIconPath: mdiPlay,
        returnFocusSelector: `[data-config-action-path="${current.path}"]`,
        rootAttrs: { 'data-seedclean-confirm-dialog': '' },
        confirmAttrs: { 'data-seedclean-confirm-submit': '' },
        cancelAttrs: { 'data-seedclean-confirm-cancel': '' },
      }
    }
    if (current.id === 'run_plugin_uninstall') {
      return {
        action: current,
        title: '确认卸载插件',
        warning: '以下操作将立即执行且无法撤销，请核对目标插件和清理范围。',
        danger: true,
        summaryPrimary: `${selectedPluginUninstallItems.value.length} 个目标插件`,
        summarySecondary: `${pluginUninstallActionItems.value.length} 项卸载或清理操作`,
        sections: [
          {
            key: 'plugin-uninstall-targets',
            label: '目标插件',
            attrs: { 'data-plugin-uninstall-confirm-targets': '' },
            items: selectedPluginUninstallItems.value.map(item => ({
              key: item.value,
              title: item.title,
              meta: item.value,
            })),
          },
          {
            key: 'plugin-uninstall-actions',
            label: '卸载与清理范围',
            attrs: { 'data-plugin-uninstall-confirm-actions': '' },
            items: pluginUninstallActionItems.value.map(item => ({
              key: item.key,
              title: item.label,
              detail: item.detail,
            })),
          },
        ],
        confirmLabel: '确认卸载',
        cancelLabel: '返回修改',
        confirmIconPath: mdiDeleteOutline,
        returnFocusSelector: `[data-config-action-path="${current.path}"]`,
        rootAttrs: { 'data-plugin-uninstall-confirm-dialog': '' },
        confirmAttrs: { 'data-plugin-uninstall-confirm-submit': '' },
        cancelAttrs: { 'data-plugin-uninstall-confirm-cancel': '' },
      }
    }
    if (current.id === 'run_downloader_helper') {
      return {
        action: current,
        kicker: '一次确认',
        title: '清理失效下载任务',
        warning: '标签和恢复做种无需确认；以下失效任务将从下载器移除。仅在源文件事件确认数据已删除时才请求清理文件。',
        danger: true,
        summaryPrimary: `${downloaderHelperPreviewItems.value.length} 个清理候选`,
        summarySecondary: '确认后同时执行当前选择的非破坏任务',
        sections: [{
          key: 'downloader-helper-preview',
          label: '清理预览',
          attrs: { 'data-downloader-helper-confirm-items': '' },
          items: downloaderHelperPreviewItems.value.map(item => ({
            key: `${item.downloader}-${item.id}`,
            title: item.name || item.id,
            meta: item.downloader,
            detail: `${item.reason} · ${item.delete_file ? '数据已删除' : '不删除数据文件'}`,
          })),
        }],
        confirmLabel: '确认并执行',
        cancelLabel: '取消',
        confirmIconPath: mdiPlay,
        returnFocusSelector: `[data-config-action-path="${current.path}"]`,
        rootAttrs: { 'data-downloader-helper-confirm-dialog': '' },
        confirmAttrs: { 'data-downloader-helper-confirm-submit': '' },
        cancelAttrs: { 'data-downloader-helper-confirm-cancel': '' },
      }
    }
    return null
  });

  const actionOperationBusy = computed$2(() => actionOperationSubmitting.value || isActionRunning(activeActionOperation.value));

  function setActionMessage(message, ok = false) {
    action.ok = Boolean(ok);
    action.message = message;
  }

  function captureActionOperationPortalStyle() {
    const root = configRoot?.value;
    if (typeof window === 'undefined' || !root) return
    const computedStyle = window.getComputedStyle(root);
    actionOperationPortalStyle.value = Array.from(computedStyle).reduce((tokens, name) => {
      if (name.startsWith('--aoa-') || name.startsWith('--v-')) tokens[name] = computedStyle.getPropertyValue(name);
      return tokens
    }, {});
  }

  function openActionOperationPanel(itemOrPath) {
    const current = typeof itemOrPath === 'string'
      ? getActionForSurface(itemOrPath, 'config')
      : itemOrPath;
    const currentId = actionId(current);
    if (!current || !currentId) return false
    const message = actionDisabledMessage(current);
    if (message) {
      setActionMessage(message);
      return false
    }
    if (currentId === 'run_seed_clean' && (!Array.isArray(form.seedclean_downloaders) || !form.seedclean_downloaders.length)) {
      setActionMessage('请先选择下载器。');
      return false
    }
    if (currentId === 'run_seed_clean' && seedCleanFilterSummary.value === '未设置筛选条件') {
      setActionMessage('请至少设置一项筛选条件。');
      return false
    }
    if (currentId === 'run_plugin_uninstall' && !pluginUninstallActionItems.value.length) {
      setActionMessage('请至少选择一项卸载或清理操作。');
      return false
    }
    captureActionOperationPortalStyle();
    activeActionOperationId.value = currentId;
    return true
  }

  function closeActionOperationPanel({ clearDownloaderPreview = true } = {}) {
    const closingActionId = activeActionOperationId.value;
    activeActionOperationId.value = '';
    if (clearDownloaderPreview && closingActionId === 'run_downloader_helper') {
      action.downloaderHelperPreview = null;
    }
    return closingActionId
  }

  function cancelActionOperationPanel() {
    return closeActionOperationPanel()
  }

  async function confirmActionOperationPanel() {
    if (actionOperationSubmitting.value) return null
    const current = activeActionOperation.value;
    if (!current) return null
    actionOperationSubmitting.value = true;
    closeActionOperationPanel({ clearDownloaderPreview: false });
    try {
      return await runAction(current)
    } finally {
      if (current.id === 'run_downloader_helper') action.downloaderHelperPreview = null;
      actionOperationSubmitting.value = false;
    }
  }

  async function triggerConfigAction(item) {
    if (!item) return null
    const operationMode = item.operation?.mode || ACTION_OPERATION_MODE.direct;
    if (operationMode === ACTION_OPERATION_MODE.confirm) {
      return { started: false, panelOpened: openActionOperationPanel(item), action: item }
    }
    if (operationMode === ACTION_OPERATION_MODE.previewConfirm) {
      if (item.path === 'run_downloader_helper') action.downloaderHelperPreview = null;
      const result = await runAction(item);
      const panelOpened = item.path === 'run_downloader_helper' && action.downloaderHelperPreview?.confirm_required
        ? openActionOperationPanel(item)
        : false;
      return { ...result, panelOpened }
    }
    if (item.parameters?.length) {
      setActionMessage('该动作缺少共享操作面板配置，已阻止直接执行。');
      return { started: false, ok: false, reason: 'panel-required', action: item }
    }
    return await runAction(item)
  }

  watch$2(() => [
    form.seedclean_action,
    form.seedclean_downloaders,
    form.seedclean_size,
    form.seedclean_ratio,
    form.seedclean_time,
    form.seedclean_upspeed,
    form.seedclean_labels,
    form.seedclean_pathkeywords,
    form.seedclean_trackerkeywords,
    form.seedclean_errorkeywords,
    form.seedclean_torrentstates,
    form.seedclean_trtorrentstates,
    form.seedclean_torrentcategorys,
    form.seedclean_samedata,
    form.seedclean_mponly,
  ], () => {
    if (activeActionOperationId.value === 'run_seed_clean') closeActionOperationPanel();
  }, { deep: true });

  watch$2(() => [form.dltag_downloaders, form.dltag_tasks], () => {
    action.downloaderHelperPreview = null;
    if (activeActionOperationId.value === 'run_downloader_helper') closeActionOperationPanel();
  }, { deep: true });

  return {
    activeActionOperationId,
    activeActionOperation,
    actionOperationPortalStyle,
    actionOperationSubmitting,
    actionOperationSpec,
    actionOperationBusy,
    openActionOperationPanel,
    closeActionOperationPanel,
    cancelActionOperationPanel,
    confirmActionOperationPanel,
    triggerConfigAction,
  }
}

const {computed: computed$1,reactive,ref: ref$2} = await importShared('vue');

// 本地与 WebDAV 恢复保留两套独立状态和原有一键恢复协议。
function useBackupRestore(form, api) {
  const client = createPluginWorkflowClient(api);
  const backupArchives = ref$2([]);
  const backupArchivesLoading = ref$2(false);
  const backupRestoreLoading = ref$2(false);
  const backupRestoreResult = ref$2(null);
  const backupRestore = reactive({
    archive: '',
    restore_config: true,
    restore_cookies: true,
    restore_database: true,
    confirm: false,
  });

  const webdavBackupArchives = ref$2([]);
  const webdavBackupArchivesLoading = ref$2(false);
  const webdavBackupRestoreLoading = ref$2(false);
  const webdavBackupRestoreResult = ref$2(null);
  const webdavBackupRestore = reactive({
    archive: '',
    restore_config: true,
    restore_cookies: true,
    restore_database: true,
    confirm: false,
  });

  const backupRestoreUnavailable = computed$1(() => !form.enabled || !form.backup_enabled);
  const backupRestoreUnavailableMessage = computed$1(() => {
    if (!form.enabled) return '插件总开关未启用，备份恢复已跳过。'
    if (!form.backup_enabled) return '自动备份组件未启用，备份恢复已跳过。'
    return ''
  });
  const webdavConfigured = computed$1(() => [
    form.backup_webdav_hostname,
    form.backup_webdav_login,
    form.backup_webdav_password,
  ].every(value => String(value || '').trim().length > 0));
  const webdavBackupRestoreUnavailable = computed$1(() => (
    !form.enabled || !form.backup_webdav_enabled || !webdavConfigured.value
  ));
  const webdavBackupRestoreUnavailableMessage = computed$1(() => {
    if (!form.enabled) return '插件总开关未启用，WebDAV 恢复已跳过。'
    if (!form.backup_webdav_enabled) return '远端备份未启用，WebDAV 恢复已跳过。'
    if (!webdavConfigured.value) return 'WebDAV 地址、账号或密码未完整配置，恢复已跳过。'
    return ''
  });

  async function loadBackupArchives() {
    backupArchivesLoading.value = true;
    try {
      const response = await client.load('backup_archives');
      backupArchives.value = Array.isArray(response) ? response : (response?.data || []);
      if (!backupRestore.archive && backupArchives.value.length) {
        backupRestore.archive = backupArchives.value[0].name || backupArchives.value[0].value || '';
      }
    } catch {
      backupArchives.value = [];
    } finally {
      backupArchivesLoading.value = false;
    }
  }

  async function loadWebdavBackupArchives() {
    if (webdavBackupRestoreUnavailable.value) {
      webdavBackupArchives.value = [];
      return
    }
    webdavBackupArchivesLoading.value = true;
    try {
      const response = await client.load('webdav_backup_archives');
      webdavBackupArchives.value = Array.isArray(response) ? response : (response?.data || []);
      if (!webdavBackupRestore.archive && webdavBackupArchives.value.length) {
        webdavBackupRestore.archive = webdavBackupArchives.value[0].name || webdavBackupArchives.value[0].value || '';
      }
    } catch {
      webdavBackupArchives.value = [];
    } finally {
      webdavBackupArchivesLoading.value = false;
    }
  }

  function backupRestorePayload() {
    return {
      archive: backupRestore.archive,
      restore_config: Boolean(backupRestore.restore_config),
      restore_cookies: Boolean(backupRestore.restore_cookies),
      restore_database: Boolean(backupRestore.restore_database),
      confirm: Boolean(backupRestore.confirm),
    }
  }

  function webdavBackupRestorePayload() {
    return {
      archive: webdavBackupRestore.archive,
      restore_config: Boolean(webdavBackupRestore.restore_config),
      restore_cookies: Boolean(webdavBackupRestore.restore_cookies),
      restore_database: Boolean(webdavBackupRestore.restore_database),
      confirm: Boolean(webdavBackupRestore.confirm),
    }
  }

  async function previewBackupRestore() {
    if (!backupRestore.archive || backupRestoreLoading.value) return
    if (backupRestoreUnavailable.value) {
      backupRestoreResult.value = { code: 1, msg: backupRestoreUnavailableMessage.value };
      return
    }
    backupRestoreLoading.value = true;
    try {
      backupRestoreResult.value = await client.execute('preview_backup_restore', backupRestorePayload());
    } catch (error) {
      backupRestoreResult.value = { code: 1, msg: error?.message || '备份恢复预览失败' };
    } finally {
      backupRestoreLoading.value = false;
    }
  }

  async function previewWebdavBackupRestore() {
    if (!webdavBackupRestore.archive || webdavBackupRestoreLoading.value) return
    if (webdavBackupRestoreUnavailable.value) {
      webdavBackupRestoreResult.value = { code: 1, msg: webdavBackupRestoreUnavailableMessage.value };
      return
    }
    webdavBackupRestoreLoading.value = true;
    try {
      webdavBackupRestoreResult.value = await client.execute('preview_webdav_backup_restore', webdavBackupRestorePayload());
    } catch (error) {
      webdavBackupRestoreResult.value = { code: 1, msg: error?.message || 'WebDAV 备份恢复预览失败' };
    } finally {
      webdavBackupRestoreLoading.value = false;
    }
  }

  async function runBackupRestore() {
    if (!backupRestore.archive || !backupRestore.confirm || backupRestoreLoading.value) return
    if (backupRestoreUnavailable.value) {
      backupRestoreResult.value = { code: 1, msg: backupRestoreUnavailableMessage.value };
      return
    }
    backupRestoreLoading.value = true;
    try {
      backupRestoreResult.value = await client.execute('run_backup_restore', backupRestorePayload());
      await loadBackupArchives();
    } catch (error) {
      backupRestoreResult.value = { code: 1, msg: error?.message || '备份恢复执行失败' };
    } finally {
      backupRestore.confirm = false;
      backupRestoreLoading.value = false;
    }
  }

  async function runWebdavBackupRestore() {
    if (!webdavBackupRestore.archive || !webdavBackupRestore.confirm || webdavBackupRestoreLoading.value) return
    if (webdavBackupRestoreUnavailable.value) {
      webdavBackupRestoreResult.value = { code: 1, msg: webdavBackupRestoreUnavailableMessage.value };
      return
    }
    webdavBackupRestoreLoading.value = true;
    try {
      webdavBackupRestoreResult.value = await client.execute('run_webdav_backup_restore', webdavBackupRestorePayload());
      await loadWebdavBackupArchives();
    } catch (error) {
      webdavBackupRestoreResult.value = { code: 1, msg: error?.message || 'WebDAV 备份恢复执行失败' };
    } finally {
      webdavBackupRestore.confirm = false;
      webdavBackupRestoreLoading.value = false;
    }
  }

  return {
    backupArchives,
    backupArchivesLoading,
    backupRestoreLoading,
    backupRestoreResult,
    backupRestore,
    webdavBackupArchives,
    webdavBackupArchivesLoading,
    webdavBackupRestoreLoading,
    webdavBackupRestoreResult,
    webdavBackupRestore,
    backupRestoreUnavailable,
    backupRestoreUnavailableMessage,
    webdavBackupRestoreUnavailable,
    webdavBackupRestoreUnavailableMessage,
    loadBackupArchives,
    loadWebdavBackupArchives,
    previewBackupRestore,
    previewWebdavBackupRestore,
    runBackupRestore,
    runWebdavBackupRestore,
  }
}

const {unref:_unref,createElementVNode:_createElementVNode,openBlock:_openBlock$1,createElementBlock:_createElementBlock,normalizeClass:_normalizeClass,renderList:_renderList,Fragment:_Fragment,normalizeStyle:_normalizeStyle,toDisplayString:_toDisplayString,createCommentVNode:_createCommentVNode,createBlock:_createBlock$1,createVNode:_createVNode,withCtx:_withCtx,mergeProps:_mergeProps,Transition:_Transition} = await importShared('vue');


const _hoisted_1 = ["data-config-dirty", "data-config-record-state", "data-config-load-state", "data-effective-state", "aria-busy"];
const _hoisted_2 = {
  class: "aoa-config-top-bar",
  "data-config-top-bar": ""
};
const _hoisted_3 = { class: "aoa-config-top-actions" };
const _hoisted_4 = { class: "aoa-config-master-switch" };
const _hoisted_5 = ["aria-checked", "disabled"];
const _hoisted_6 = ["disabled"];
const _hoisted_7 = ["aria-selected", "data-config-main-tab", "data-effective-state", "disabled", "onClick"];
const _hoisted_8 = ["viewBox"];
const _hoisted_9 = ["d"];
const _hoisted_10 = {
  class: "aoa-config-subtab-bar",
  "data-config-subtab-bar": ""
};
const _hoisted_11 = ["aria-label"];
const _hoisted_12 = ["id", "aria-selected", "aria-controls", "data-config-subtab", "data-effective-state", "disabled", "onClick"];
const _hoisted_13 = ["viewBox"];
const _hoisted_14 = ["d"];
const _hoisted_15 = {
  key: 0,
  class: "aoa-config-subtab-current",
  "aria-live": "polite"
};
const _hoisted_16 = ["id", "aria-labelledby", "data-config-active-sub", "data-effective-state"];
const _hoisted_17 = ["data-config-load-panel", "role"];
const _hoisted_18 = {
  class: "aoa-config-load-state__indicator",
  "aria-hidden": "true"
};
const _hoisted_19 = {
  key: 0,
  class: "aoa-config-load-state__spinner"
};
const _hoisted_20 = {
  key: 1,
  class: "aoa-mdi-icon",
  viewBox: "0 0 24 24",
  width: "24",
  height: "24"
};
const _hoisted_21 = ["d"];
const _hoisted_22 = { class: "aoa-config-load-state__copy" };
const _hoisted_23 = { key: 0 };
const _hoisted_24 = ["data-config-hero-tone", "aria-label", "data-effective-state"];
const _hoisted_25 = { class: "aoa-config-hero-left" };
const _hoisted_26 = { class: "aoa-config-hero-icon" };
const _hoisted_27 = ["viewBox"];
const _hoisted_28 = ["d"];
const _hoisted_29 = { class: "aoa-config-hero-info" };
const _hoisted_30 = { class: "aoa-config-hero-kicker" };
const _hoisted_31 = { class: "aoa-config-hero-title" };
const _hoisted_32 = {
  key: 0,
  class: "aoa-config-hero-desc"
};
const _hoisted_33 = ["data-config-danger-header"];
const _hoisted_34 = ["aria-checked", "aria-label"];
const _hoisted_35 = {
  key: 1,
  class: "aoa-fusion-takeover-note aoa-config-risk-note--orange",
  "data-config-notice-tone": "orange",
  "data-config-notice-icon": "warning",
  role: "status"
};
const _hoisted_36 = {
  class: "aoa-mdi-icon aoa-fusion-takeover-note__icon",
  viewBox: "0 0 24 24",
  width: "18",
  height: "18",
  "aria-hidden": "true"
};
const _hoisted_37 = ["d"];
const _hoisted_38 = {
  class: "aoa-design-replica-stack",
  "data-html-replica-stack": ""
};
const _hoisted_39 = {
  class: "aoa-config-action-strip",
  "data-config-action-strip": ""
};
const _hoisted_40 = { class: "aoa-config-action-strip-copy" };
const _hoisted_41 = {
  key: 0,
  class: "aoa-config-action-hint"
};
const _hoisted_42 = ["data-tone"];
const _hoisted_43 = { class: "aoa-config-action-strip-buttons" };
const _hoisted_44 = ["data-dirty", "disabled", "aria-busy"];

const {ref: ref$1,computed,onMounted: onMounted$1,onBeforeUnmount,defineComponent,h,watch: watch$1,toRef} = await importShared('vue');

const faShieldHalvedPath = 'M256 0c4.6 0 9.2 1 13.4 2.9L457.7 82.8c22 9.3 38.4 31 38.3 57.2c-.5 99.2-41.3 280.7-213.6 363.2c-16.7 8-36.1 8-52.8 0C57.3 420.7 16.5 239.2 16 140c-.1-26.2 16.3-47.9 38.3-57.2L242.7 2.9C246.8 1 251.4 0 256 0zm0 66.8V444.8C394 378 431.1 230.1 432 141.4L256 66.8l0 0z';
const faGaugePath = 'M0 256a256 256 0 1 1 512 0A256 256 0 1 1 0 256zm320 96c0-26.9-16.5-49.9-40-59.3V88c0-13.3-10.7-24-24-24s-24 10.7-24 24V292.7c-23.5 9.5-40 32.5-40 59.3c0 35.3 28.7 64 64 64s64-28.7 64-64zM144 176a32 32 0 1 0 0-64 32 32 0 1 0 0 64zm-16 80a32 32 0 1 0 -64 0 32 32 0 1 0 64 0zm288 32a32 32 0 1 0 0-64 32 32 0 1 0 0 64zM400 144a32 32 0 1 0 -64 0 32 32 0 1 0 64 0z';
const faIdCardPath = 'M0 96l576 0c0-35.3-28.7-64-64-64H64C28.7 32 0 60.7 0 96zm0 32V416c0 35.3 28.7 64 64 64H512c35.3 0 64-28.7 64-64V128H0zM64 405.3c0-29.5 23.9-53.3 53.3-53.3H234.7c29.5 0 53.3 23.9 53.3 53.3c0 5.9-4.8 10.7-10.7 10.7H74.7c-5.9 0-10.7-4.8-10.7-10.7zM176 192a64 64 0 1 1 0 128 64 64 0 1 1 0-128zm176 16c0-8.8 7.2-16 16-16H496c8.8 0 16 7.2 16 16s-7.2 16-16 16H368c-8.8 0-16-7.2-16-16zm0 64c0-8.8 7.2-16 16-16H496c8.8 0 16 7.2 16 16s-7.2 16-16 16H368c-8.8 0-16-7.2-16-16zm0 64c0-8.8 7.2-16 16-16H496c8.8 0 16 7.2 16 16s-7.2 16-16 16H368c-8.8 0-16-7.2-16-16z';
const faBellPath = 'M224 0c-17.7 0-32 14.3-32 32V51.2C119 66 64 130.6 64 208v18.8c0 47-17.3 92.4-48.5 127.6l-7.4 8.3c-8.4 9.4-10.4 22.9-5.3 34.4S19.4 416 32 416H416c12.6 0 24-7.4 29.2-18.9s3.1-25-5.3-34.4l-7.4-8.3C401.3 319.2 384 273.9 384 226.8V208c0-77.4-55-142-128-156.8V32c0-17.7-14.3-32-32-32zm45.3 493.3c12-12 18.7-28.3 18.7-45.3H224 160c0 17 6.7 33.3 18.7 45.3s28.3 18.7 45.3 18.7s33.3-6.7 45.3-18.7z';
const faChartLinePath = 'M64 64c0-17.7-14.3-32-32-32S0 46.3 0 64V400c0 44.2 35.8 80 80 80H480c17.7 0 32-14.3 32-32s-14.3-32-32-32H80c-8.8 0-16-7.2-16-16V64zm406.6 86.6c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L320 210.7l-57.4-57.4c-12.5-12.5-32.8-12.5-45.3 0l-112 112c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L240 221.3l57.4 57.4c12.5 12.5 32.8 12.5 45.3 0l128-128z';
const faDownloadPath = 'M288 32c0-17.7-14.3-32-32-32s-32 14.3-32 32V274.7l-73.4-73.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3l128 128c12.5 12.5 32.8 12.5 45.3 0l128-128c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L288 274.7V32zM64 352c-35.3 0-64 28.7-64 64v32c0 35.3 28.7 64 64 64H448c35.3 0 64-28.7 64-64V416c0-35.3-28.7-64-64-64H346.5l-45.3 45.3c-25 25-65.5 25-90.5 0L165.5 352H64zm368 56a24 24 0 1 1 0 48 24 24 0 1 1 0-48z';
const faHeartPulsePath = 'M228.3 469.1L47.6 300.4c-4.2-3.9-8.2-8.1-11.9-12.4h87c22.6 0 43-13.6 51.7-34.5l10.5-25.2 49.3 109.5c3.8 8.5 12.1 14 21.4 14.1s17.8-5 22-13.3L320 253.7l1.7 3.4c9.5 19 28.9 31 50.1 31H476.3c-3.7 4.3-7.7 8.5-11.9 12.4L283.7 469.1c-7.5 7-17.4 10.9-27.7 10.9s-20.2-3.9-27.7-10.9zM503.7 240h-132c-3 0-5.8-1.7-7.2-4.4l-23.2-46.3c-4.1-8.1-12.4-13.3-21.5-13.3s-17.4 5.1-21.5 13.3l-41.4 82.8L205.9 158.2c-3.9-8.7-12.7-14.3-22.2-14.1s-18.1 5.9-21.8 14.8l-31.8 76.3c-1.2 3-4.2 4.9-7.4 4.9H16c-2.6 0-5 .4-7.3 1.1C3 225.2 0 208.2 0 190.9v-5.8c0-69.9 50.5-129.5 119.4-141C165 36.5 211.4 51.4 244 84l12 12 12-12c32.6-32.6 79-47.5 124.6-39.9C461.5 55.6 512 115.2 512 185.1v5.8c0 16.9-2.8 33.5-8.3 49.1z';
const faPuzzlePiecePath = 'M192 104.8c0-9.2-5.8-17.3-13.2-22.8C167.2 73.3 160 61.3 160 48c0-26.5 28.7-48 64-48s64 21.5 64 48c0 13.3-7.2 25.3-18.8 34c-7.4 5.5-13.2 13.6-13.2 22.8v0c0 12.8 10.4 23.2 23.2 23.2H336c26.5 0 48 21.5 48 48v56.8c0 12.8 10.4 23.2 23.2 23.2v0c9.2 0 17.3-5.8 22.8-13.2c8.7-11.6 20.7-18.8 34-18.8c26.5 0 48 28.7 48 64s-21.5 64-48 64c-13.3 0-25.3-7.2-34-18.8c-5.5-7.4-13.6-13.2-22.8-13.2v0c-12.8 0-23.2 10.4-23.2 23.2V464c0 26.5-21.5 48-48 48H279.2c-12.8 0-23.2-10.4-23.2-23.2v0c0-9.2 5.8-17.3 13.2-22.8c11.6-8.7 18.8-20.7 18.8-34c0-26.5-28.7-48-64-48s-64 21.5-64 48c0 13.3 7.2 25.3 18.8 34c7.4 5.5 13.2 13.6 13.2 22.8v0c0 12.8-10.4 23.2-23.2 23.2H48c-26.5 0-48-21.5-48-48V343.2C0 330.4 10.4 320 23.2 320v0c9.2 0 17.3 5.8 22.8 13.2C54.7 344.8 66.7 352 80 352c26.5 0 48-28.7 48-64s-21.5-64-48-64c-13.3 0-25.3 7.2-34 18.8C40.5 250.2 32.4 256 23.2 256v0C10.4 256 0 245.6 0 232.8V176c0-26.5 21.5-48 48-48H168.8c12.8 0 23.2-10.4 23.2-23.2v0z';
const faTvPath = 'M64 64V352H576V64H64zM0 64C0 28.7 28.7 0 64 0H576c35.3 0 64 28.7 64 64V352c0 35.3-28.7 64-64 64H64c-35.3 0-64-28.7-64-64V64zM128 448H512c17.7 0 32 14.3 32 32s-14.3 32-32 32H128c-17.7 0-32-14.3-32-32s14.3-32 32-32z';
const faCirclePlusPath = 'M256 512A256 256 0 1 0 256 0a256 256 0 1 0 0 512zM232 344V280H168c-13.3 0-24-10.7-24-24s10.7-24 24-24h64V168c0-13.3 10.7-24 24-24s24 10.7 24 24v64h64c13.3 0 24 10.7 24 24s-10.7 24-24 24H280v64c0 13.3-10.7 24-24 24s-24-10.7-24-24z';
const faArrowsRotatePath = 'M105.1 202.6c7.7-21.8 20.2-42.3 37.8-59.8c62.5-62.5 163.8-62.5 226.3 0L386.3 160H336c-17.7 0-32 14.3-32 32s14.3 32 32 32H463.5c0 0 0 0 0 0h.4c17.7 0 32-14.3 32-32V64c0-17.7-14.3-32-32-32s-32 14.3-32 32v51.2L414.4 97.6c-87.5-87.5-229.3-87.5-316.8 0C73.2 122 55.6 150.7 44.8 181.4c-5.9 16.7 2.9 34.9 19.5 40.8s34.9-2.9 40.8-19.5zM39 289.3c-5 1.5-9.8 4.2-13.7 8.2c-4 4-6.7 8.8-8.1 14c-.3 1.2-.6 2.5-.8 3.8c-.3 1.7-.4 3.4-.4 5.1V448c0 17.7 14.3 32 32 32s32-14.3 32-32V396.9l17.6 17.5l0 0c87.5 87.4 229.3 87.4 316.7 0c24.4-24.4 42.1-53.1 52.9-83.7c5.9-16.7-2.9-34.9-19.5-40.8s-34.9 2.9-40.8 19.5c-7.7 21.8-20.2 42.3-37.8 59.8c-62.5 62.5-163.8 62.5-226.3 0l-.1-.1L125.6 352H176c17.7 0 32-14.3 32-32s-14.3-32-32-32H48.4c-1.6 0-3.2 .1-4.8 .3s-3.1 .5-4.6 1z';
const faFloppyDiskPath = 'M64 32C28.7 32 0 60.7 0 96V416c0 35.3 28.7 64 64 64H384c35.3 0 64-28.7 64-64V173.3c0-17-6.7-33.3-18.7-45.3L352 50.7C340 38.7 323.7 32 306.7 32H64zm0 96c0-17.7 14.3-32 32-32H288c17.7 0 32 14.3 32 32v64c0 17.7-14.3 32-32 32H96c-17.7 0-32-14.3-32-32V128zM224 288a64 64 0 1 1 0 128 64 64 0 1 1 0-128z';
const faPowerOffPath = 'M288 32c0-17.7-14.3-32-32-32s-32 14.3-32 32V256c0 17.7 14.3 32 32 32s32-14.3 32-32V32zM143.5 120.6c13.6-11.3 15.4-31.5 4.1-45.1s-31.5-15.4-45.1-4.1C49.7 115.4 16 181.8 16 256c0 132.5 107.5 240 240 240s240-107.5 240-240c0-74.2-33.8-140.6-86.6-184.6c-13.6-11.3-33.8-9.4-45.1 4.1s-9.4 33.8 4.1 45.1c38.9 32.3 63.5 81 63.5 135.4c0 97.2-78.8 176-176 176s-176-78.8-176-176c0-54.4 24.7-103.1 63.5-135.4z';
const faCalendarPath = 'M96 32V64H48C21.5 64 0 85.5 0 112v48H448V112c0-26.5-21.5-48-48-48H352V32c0-17.7-14.3-32-32-32s-32 14.3-32 32V64H160V32c0-17.7-14.3-32-32-32S96 14.3 96 32zM448 192H0V464c0 26.5 21.5 48 48 48H400c26.5 0 48-21.5 48-48V192z';
const faClockPath = 'M256 0a256 256 0 1 1 0 512A256 256 0 1 1 256 0zM232 120V256c0 8 4 15.5 10.7 20l96 64c11 7.4 25.9 4.4 33.3-6.7s4.4-25.9-6.7-33.3L280 243.2V120c0-13.3-10.7-24-24-24s-24 10.7-24 24z';
const faListOlPath = 'M24 56c0-13.3 10.7-24 24-24H80c13.3 0 24 10.7 24 24V176h16c13.3 0 24 10.7 24 24s-10.7 24-24 24H40c-13.3 0-24-10.7-24-24s10.7-24 24-24H56V80H48C34.7 80 24 69.3 24 56zM86.7 341.2c-6.5-7.4-18.3-6.9-24 1.2L51.5 357.9c-7.7 10.8-22.7 13.3-33.5 5.6s-13.3-22.7-5.6-33.5l11.1-15.6c23.7-33.2 72.3-35.6 99.2-4.9c21.3 24.4 20.8 60.9-1.1 84.7L86.8 432H120c13.3 0 24 10.7 24 24s-10.7 24-24 24H32c-9.5 0-18.2-5.6-22-14.4s-2.1-18.9 4.3-25.9l72-78c5.3-5.8 5.4-14.6 .3-20.5zM224 64H480c17.7 0 32 14.3 32 32s-14.3 32-32 32H224c-17.7 0-32-14.3-32-32s14.3-32 32-32zm0 160H480c17.7 0 32 14.3 32 32s-14.3 32-32 32H224c-17.7 0-32-14.3-32-32s14.3-32 32-32zm0 160H480c17.7 0 32 14.3 32 32s-14.3 32-32 32H224c-17.7 0-32-14.3-32-32s14.3-32 32-32z';

const _sfc_main$1 = {
  __name: 'Config',
  props: {
  api: { type: [Object, Function], default: null },
  initialConfig: { type: Object, default: () => ({}) },
  pluginId: { type: String, default: 'Signal' },
  configRecordState: {
    type: String,
    default: 'unknown',
    validator: value => ['unknown', 'absent', 'present'].includes(value),
  },
  configLoadState: {
    type: String,
    default: 'ready',
    validator: value => ['loading', 'ready', 'error'].includes(value),
  },
  configLoadError: { type: String, default: '' },
},
  emits: ['save', 'close', 'switch', 'retry-load'],
  setup(__props, { emit: __emit }) {

const iconPaths = {
  'mdi-cog-outline': mdiCogOutline,
  'mdi-message-badge-outline': mdiMessageBadgeOutline,
  'mdi-chart-line': mdiChartLine,
  'mdi-download-network-outline': mdiDownloadNetworkOutline,
  'mdi-puzzle-remove-outline': mdiPuzzleRemoveOutline,
  'mdi-television-play': mdiTelevisionPlay,
  'mdi-bell-ring-outline': mdiBellRingOutline,
  'mdi-heart-pulse': mdiHeartPulse,
  'mdi-delete-sweep-outline': mdiDeleteSweepOutline,
  'mdi-tag-multiple-outline': mdiTagMultipleOutline,
  'mdi-auto-fix': mdiAutoFix,
  'mdi-archive-arrow-up-outline': mdiArchiveArrowUpOutline,
  'mdi-file-document-remove-outline': mdiFileDocumentRemoveOutline,
  'mdi-update': mdiUpdate,
  'mdi-power-standby': mdiPowerStandby,
  'mdi-calendar-clock': mdiCalendarClock,
  'mdi-format-list-numbered': mdiFormatListNumbered,
  'mdi-email-outline': mdiEmailOutline,
  'mdi-server': mdiServer,
  'mdi-format-list-checks': mdiFormatListChecks,
  'mdi-movie-open-outline': mdiMovieOpenOutline,
  'mdi-chart-bar': mdiChartBar,
  'mdi-gauge': mdiGauge,
  'mdi-harddisk': mdiHarddisk,
  'mdi-filter-outline': mdiFilterOutline,
  'mdi-scale-balance': mdiScaleBalance,
  'mdi-timer-outline': mdiTimerOutline,
  'mdi-tag-outline': mdiTagOutline,
  'mdi-delete-outline': mdiDeleteOutline,
  'mdi-link-variant': mdiLinkVariant,
  'mdi-lock-outline': mdiLockOutline,
  'mdi-cloud-outline': mdiCloudOutline,
  'mdi-web': mdiWeb,
  'mdi-account-outline': mdiAccountOutline,
  'mdi-content-copy': mdiContentCopy,
  'mdi-lock-check-outline': mdiLockCheckOutline,
  'mdi-folder-outline': mdiFolderOutline,
  'mdi-rocket-launch-outline': mdiRocketLaunchOutline,
  'mdi-broom': mdiBroom,
  'mdi-sync': mdiSync,
  'mdi-download-outline': mdiDownloadOutline,
  'mdi-shield-outline': mdiShieldOutline,
  'mdi-cloud-upload-outline': mdiCloudUploadOutline,
  'mdi-alert-outline': mdiAlertOutline,
  'mdi-database-outline': mdiDatabaseOutline,
  'mdi-code-tags': mdiCodeTags,
  'mdi-cube-outline': mdiCubeOutline,
  'mdi-plus-circle-outline': mdiPlusCircleOutline,
  'mdi-eye-outline': mdiEyeOutline,
  'mdi-shield-check-outline': mdiShieldCheckOutline,
  'mdi-bell': mdiBell,
  'mdi-bell-outline': mdiBellOutline,
  'mdi-download': mdiDownload,
  'mdi-puzzle': mdiPuzzle,
  'mdi-puzzle-outline': mdiPuzzleOutline,
  'mdi-history': mdiHistory,
  'mdi-backup-restore': mdiBackupRestore,
  'mdi-card-account-details-outline': mdiCardAccountDetailsOutline,
  'mdi-television': mdiTelevision,
  'mdi-heart-pulse-solid': mdiHeartPulse,
  'mdi-alert-circle-outline': mdiAlertCircleOutline,
  'mdi-alpha-m-box-outline': mdiAlphaMBoxOutline,
  'mdi-layers-outline': mdiLayersOutline,
  'mdi-pencil-outline': mdiPencilOutline,
  'mdi-percent': mdiPercent,
  'mdi-play': mdiPlay,
  'mdi-send-outline': mdiSendOutline,
  'mdi-shield-half-full': mdiShieldHalfFull,
  'mdi-signal': mdiSignal,
  'mdi-weight': mdiWeight,
};
function iconPath(name) {
  return iconPaths[name] || mdiCogOutline
}

const replicaFieldFaIcons = {
  'mdi-power-standby': { path: faPowerOffPath, viewBox: '0 0 512 512' },
  'mdi-calendar-clock': { path: faCalendarPath, viewBox: '0 0 448 512' },
  'mdi-format-list-numbered': { path: faListOlPath, viewBox: '0 0 512 512' },
};
const props = __props;
const apiHandle = toRef(props, 'api');
const emit = __emit;
const { rootThemeClass } = useAgentOpsTheme();
const configLoadReady = computed(() => props.configLoadState === 'ready');
const configLoadBusy = computed(() => props.configLoadState === 'loading');
const configReadLocked = computed(() => !configLoadReady.value);
const configLoadErrorDetail = computed(() => String(props.configLoadError || '').trim());

const lifecycle = useConfigLifecycle({
  initialConfig: () => props.initialConfig,
  configRecordState: () => props.configRecordState,
  api: apiHandle,
  pluginId: props.pluginId,
  emit,
  validateSave: () => subfillRulesValid.value,
  onValidationError: message => {
    action.ok = false;
    action.message = message;
  },
});
const { form, isDirty, saveConfig } = lifecycle;
const {
  backupArchives,
  backupArchivesLoading,
  backupRestoreLoading,
  backupRestoreResult,
  backupRestore,
  webdavBackupArchives,
  webdavBackupArchivesLoading,
  webdavBackupRestoreLoading,
  webdavBackupRestoreResult,
  webdavBackupRestore,
  backupRestoreUnavailable,
  backupRestoreUnavailableMessage,
  webdavBackupRestoreUnavailable,
  webdavBackupRestoreUnavailableMessage,
  loadBackupArchives,
  loadWebdavBackupArchives,
  previewBackupRestore,
  previewWebdavBackupRestore,
  runBackupRestore,
  runWebdavBackupRestore,
} = useBackupRestore(form, apiHandle);
const subfillRulesValid = computed(() => {
  if (!form.subfill_category_enabled) return true
  const rules = parseSubfillRules(form.subfill_category_confs);
  return rules.length > 0 && rules.every(rule => validateSubfillRule(rule).length === 0)
});
const configRoot = ref$1(null);
const pageSession = useConfigPageSession();
const navigation = useConfigNavigation({ pluginId: props.pluginId, emit, saveConfig, root: configRoot, pageSession });
const {
  activeMain, activeSub, activeUpdateModule, activeBackupModule, activeSubfillModule,
  mainNav, subtabList, saving, saveFeedback,
  currentMain, currentSubs, currentSub, currentSubTitle,
  selectMain, selectSub, revealCategoryItem, revealActiveCategories, openDashboard,
  savePage,
} = navigation;
function saveCurrentPage() {
  if (configReadLocked.value) return
  return savePage()
}
let dialogScrollHost = null;
let dialogSurfaceHost = null;

// Manual action state
// === 运行数据与动作编排 ===
const {
  installedPlugins, loadInstalledPlugins,
  tgConsoleStatus, tgConsoleLoading, loadTgConsoleStatus,
  downloaderOptions, loadDownloaders,
  mediaserverOptions, loadMediaservers,
} = useDataLoader(apiHandle);

const replicaItemSources = computed(() => ({
  downloaderOptions: downloaderOptions.value,
  healthCheckItems,
  healthDatabaseTargets,
  healthDirectoryTargets,
  healthStorageTargets,
  installedPlugins: installedPlugins.value,
  marketNotifyItems,
  mediaserverOptions: mediaserverOptions.value,
  messageTypeItems,
  mpUpdateTypes,
  marketUpdateStrategies,
  pluginAutoInstallScopeItems,
  msgGroupItems,
  notificationTypeItems,
  seedActionsItems,
  siteStatRangeItems,
  subfillDetailItems,
  subscribeSubtypeItems,
  dltagTaskItems,
  dltagDeleteStrategyItems,
}));

const {
  action, notificationLockedByFusion,
  getActionAvailability, actionDisabledMessage, isActionRunning, runAction,
} = useConfigActionRunner(form, apiHandle, installedPlugins, loadInstalledPlugins);
const {
  actionOperationPortalStyle,
  actionOperationSpec,
  actionOperationBusy,
  triggerConfigAction,
  cancelActionOperationPanel,
  confirmActionOperationPanel,
} = useConfigActionOperation({
  configRoot,
  form,
  action,
  installedPlugins,
  actionDisabledMessage,
  isActionRunning,
  runAction,
});

const fusionActionIds = new Set(['create_tg_console_card', 'run_daily_report']);
async function triggerConfigActionWithRefresh(item) {
  if (configReadLocked.value) return { ok: false, reason: 'config-not-ready' }
  const result = await triggerConfigAction(item);
  const actionId = String(item?.id || item?.path || item?.apiPath || '');
  if (fusionActionIds.has(actionId) && result?.ok) await loadTgConsoleStatus();
  return result
}

const heroMap = {
  fusion: { kicker: '融合通知', on: '已开启，通知统一走卡片', off: '已关闭，各组件自行发送', desc: '开启后所有通知汇入一张 Telegram 卡片，各组件独立渠道将被接管。' },
  server: { kicker: '媒体通知', on: '正在监听媒体事件', off: '未启用', desc: '接收 Emby/Jellyfin/Plex Webhook 事件并转发给用户。' },
  subscribe: { kicker: '订阅追新', on: '每日自动检查更新', off: '未启用', desc: '每日检查订阅更新并按规则推送通知。' },
  sites: { kicker: '站点统计', on: '正在采集站点数据', off: '未启用', desc: '采集每日站点上传/下载增量，供应仪表盘和日报。' },
  hc: { kicker: '健康巡查', on: '定时巡检中', off: '未启用', desc: '检查数据库、存储空间、目录是否正常，异常时告警。' },
  seedremove: { kicker: '自动删种', on: '按条件自动清理', off: '未启用', desc: '按分享率、大小、做种时间等规则自动暂停或删除种子。' },
  dltagmain: { kicker: '下载器助手', on: '自动整理下载任务', off: '未启用', desc: '统一处理标签、恢复做种与失效任务，不替代按规则自动删种。' },
  subfill: { kicker: '订阅规则填充', on: '订阅规则填充已启用', mixed: '部分订阅填充已启用', off: '未启用', desc: '' },
  backup: { kicker: '自动备份', on: '定时备份中', off: '未启用', desc: '按策略备份配置与数据，支持本地和 WebDAV 远端。' },
  logs: { kicker: '日志清理', on: '定时清理中', off: '未启用', desc: '定期裁剪插件运行日志，控制体积。' },
  updates: { kicker: '更新管理', on: '更新管理已启用', mixed: '部分更新已启用', off: '更新管理未启用', desc: '' },
  clean: { kicker: '插件卸载', on: '已选目标，待执行', off: '未选择卸载目标', desc: '彻底移除插件并清理配置、数据和源码残留。此操作不可逆。' },
};
const currentHero = computed(() => heroMap[activeSub.value] || heroMap.fusion);
const heroIconPath = computed(() => activeSub.value === 'fusion' ? faIdCardPath : iconPath(currentSub.value?.icon || 'mdi-cog-outline'));
const heroIconViewBox = computed(() => activeSub.value === 'fusion' ? '0 0 576 512' : '0 0 24 24');
const updateTaskKeys = Object.freeze(['mp_update_enabled', 'plugin_update_reminder_enabled', 'market_update_enabled']);
const updateMasterState = computed(() => {
  const enabledCount = updateTaskKeys.filter(key => Boolean(form[key])).length;
  if (enabledCount === updateTaskKeys.length) return 'on'
  if (enabledCount === 0) return 'off'
  return 'mixed'
});
const updateEnabledCount = computed(() => updateTaskKeys.filter(key => Boolean(form[key])).length);
const subfillEnabledCount = computed(() => ['subfill_enabled', 'subfill_category_enabled']
  .filter(key => Boolean(form[key])).length);
const heroMixed = computed(() => (
  (activeSub.value === 'updates' && updateMasterState.value === 'mixed')
  || (activeSub.value === 'subfill' && subfillEnabledCount.value === 1)
));
const pluginEnabled = computed(() => form.enabled !== false);
const effectiveStateInputs = {
  fusion: { enabledKey: 'fusion_notify_enabled', scheduleRequired: true, scheduleKey: 'fusion_notify_enabled', cronKeys: ['fusion_card_create_cron', 'fusion_card_refresh_cron'] },
  server: { enabledKey: 'msgnotify_enabled' },
  subscribe: { enabledKey: 'subscribe_reminder_enabled', scheduleRequired: true, scheduleKey: 'subscribe_reminder_schedule_enabled', cronKeys: ['subscribe_reminder_cron'] },
  sites: { enabledKey: 'site_stat_enabled', scheduleRequired: true, scheduleKey: 'site_stat_schedule_enabled', cronKeys: ['site_stat_cron'] },
  hc: { enabledKey: 'health_check_enabled', scheduleRequired: true, scheduleKey: 'health_check_schedule_enabled', cronKeys: ['health_check_cron'] },
  seedremove: { enabledKey: 'seedclean_enabled', scheduleRequired: true, scheduleKey: 'seedclean_schedule_enabled', cronKeys: ['seedclean_cron'], requiredKeys: ['seedclean_downloaders'] },
  dltagmain: { enabledKey: 'dltag_enabled', requiredKeys: ['dltag_tasks'] },
  subfill: { enabledKeys: ['subfill_enabled', 'subfill_category_enabled'], enabledMode: 'any' },
  backup: { enabledKey: 'backup_enabled', scheduleRequired: true, cronKeys: ['backup_cron'] },
  logs: { enabledKey: 'log_clean_enabled', scheduleRequired: true, scheduleKey: 'log_clean_schedule_enabled', cronKeys: ['log_clean_cron'] },
  updates: { enabledKeys: updateTaskKeys, enabledMode: 'any', scheduleRequired: true, cronKeys: ['mp_update_cron', 'plugin_update_reminder_cron', 'market_update_cron'] },
  clean: { selectionKey: 'plugin_uninstall_ids' },
};
function hasConfiguredValue(value) {
  if (Array.isArray(value)) return value.length > 0
  return String(value ?? '').trim().length > 0
}
function effectiveStateFor(subKey) {
  const input = effectiveStateInputs[subKey] || {};
  const enabledKeys = input.enabledKeys || (input.enabledKey ? [input.enabledKey] : []);
  const scheduleKeys = input.scheduleKeys || (input.scheduleKey ? [input.scheduleKey] : []);
  const cronKeys = input.cronKeys || [];
  const componentEnabled = input.selectionKey
    ? hasConfiguredValue(form[input.selectionKey])
    : (enabledKeys.length
        ? (input.enabledMode === 'any' || subKey === 'updates'
            ? enabledKeys.some(key => form[key] !== false)
            : enabledKeys.every(key => form[key] !== false))
        : true);
  const requiredConfigReady = (input.requiredKeys || []).every(key => hasConfiguredValue(form[key]));
  const scheduleEnabled = scheduleKeys.length ? (subKey === 'updates' ? scheduleKeys.some(key => form[key] !== false) : scheduleKeys.every(key => form[key] !== false)) : true;
  const allCronReady = cronKeys.every(key => hasConfiguredValue(form[key]));
  return deriveEffectiveState({
    pluginEnabled: pluginEnabled.value,
    componentEnabled,
    requiredConfigReady,
    scheduleRequired: Boolean(input.scheduleRequired),
    scheduleEnabled,
    cron: allCronReady ? 'configured' : '',
    fusionNotificationManaged: subKey !== 'fusion' && Boolean(form.fusion_notify_enabled),
  })
}
const currentEffectiveState = computed(() => effectiveStateFor(activeSub.value));
const mainEffectiveState = (mainKey) => {
  if (!pluginEnabled.value) return EFFECTIVE_STATE.PLUGIN_DISABLED
  const states = (subTabs[mainKey] || []).map(item => effectiveStateFor(item.key).code);
  return states.includes(EFFECTIVE_STATE.ACTIVE) ? EFFECTIVE_STATE.ACTIVE : (states[0] || EFFECTIVE_STATE.COMPONENT_DISABLED)
};
const heroEnabled = computed(() => {
  const key = activeSub.value;
  if (key === 'fusion') return Boolean(form.fusion_notify_enabled)
  if (key === 'server') return Boolean(form.msgnotify_enabled)
  if (key === 'subscribe') return Boolean(form.subscribe_reminder_enabled)
  if (key === 'sites') return Boolean(form.site_stat_enabled)
  if (key === 'hc') return Boolean(form.health_check_enabled)
  if (key === 'seedremove') return Boolean(form.seedclean_enabled)
  if (key === 'dltagmain') return Boolean(form.dltag_enabled)
  if (key === 'subfill') return subfillEnabledCount.value > 0
  if (key === 'backup') return Boolean(form.backup_enabled)
  if (key === 'logs') return Boolean(form.log_clean_enabled)
  if (key === 'updates') return updateEnabledCount.value > 0
  if (key === 'clean') return Boolean(form.plugin_uninstall_ids?.length > 0)
  return true
});
const heroEffectivelyEnabled = computed(() => pluginEnabled.value && heroEnabled.value);
const heroEffectivelyMixed = computed(() => pluginEnabled.value && heroMixed.value);
const currentHeroTitle = computed(() => {
  if (currentEffectiveState.value.code === EFFECTIVE_STATE.PLUGIN_DISABLED) return '插件已停用'
  if (activeSub.value === 'updates') return `已启用 ${updateEnabledCount.value}/${updateTaskKeys.length} 项更新任务`
  return heroMixed.value ? currentHero.value.mixed : (heroEnabled.value ? currentHero.value.on : currentHero.value.off)
});
const heroStatusText = computed(() => {
  if (currentEffectiveState.value.code === EFFECTIVE_STATE.PLUGIN_DISABLED) return '已停用'
  if (activeSub.value === 'updates') return `已启用 ${updateEnabledCount.value}/${updateTaskKeys.length} 项`
  return heroMixed.value ? '部分启用' : (heroEnabled.value ? '运行中' : '待启用')
});
const heroToggleLabel = computed(() => heroMixed.value
  ? `${currentHero.value.kicker}总开关，当前部分启用，点击后全部启用`
  : `${currentHero.value.kicker}总开关`);

function setHeroEnabled(value) {
  if (configReadLocked.value) return
  const key = activeSub.value;
  const toggle = (enabledKey, scheduleKey) => {
    form[enabledKey] = value;
    if (scheduleKey) form[scheduleKey] = value;
  };
  switch (key) {
    case 'fusion': toggle('fusion_notify_enabled'); return
    case 'server': toggle('msgnotify_enabled'); return
    case 'subscribe': toggle('subscribe_reminder_enabled', 'subscribe_reminder_schedule_enabled'); return
    case 'sites': toggle('site_stat_enabled', 'site_stat_schedule_enabled'); return
    case 'hc': toggle('health_check_enabled', 'health_check_schedule_enabled'); return
    case 'seedremove': toggle('seedclean_enabled', 'seedclean_schedule_enabled'); return
    case 'dltagmain': toggle('dltag_enabled'); return
    case 'backup': toggle('backup_enabled'); return
    case 'logs': toggle('log_clean_enabled', 'log_clean_schedule_enabled'); return
    case 'updates':
      return
  }
}

const hiddenDownloaderHelperCompatibilityFieldKeys = Object.freeze([
  'dltag_all_tags',
  'dltag_excluded_tags',
]);

const replicaCards = computed(() => {
  const onOff = v => v ? 'ON' : 'OFF';
  const valOr = (v, fb = '未配置') => v || fb;
  const arrCount = (arr, suffix = '个') => Array.isArray(arr) && arr.length ? `${arr.length} ${suffix}` : '未配置';
  const arrNames = (arr) => Array.isArray(arr) && arr.length ? arr.join('、') : '全部';
  const cronVal = v => v || '未设置';
  const subfillCompletionNotifyFields = () => ([
    {
      key: 'subfill_completion_notify_enabled',
      icon: 'mdi-bell-outline',
      label: '填充完成通知',
      value: onOff(form.subfill_completion_notify_enabled),
    },
    {
      key: 'subfill_completion_notify_type',
      icon: 'mdi-email-outline',
      label: '填充通知渠道',
      value: valOr(form.subfill_completion_notify_type, 'Plugin'),
      disabled: Boolean(form.fusion_notify_enabled),
    },
  ]);
  const dltagTasks = Array.isArray(form.dltag_tasks) ? form.dltag_tasks : [];
  const dltagTaggingActive = dltagTasks.includes('tagging') || Boolean(form.dltag_listen_download);
  const cards = composeSharedReplicaCards(bindReplicaCards(completeReplicaCards({
    fusion: [
      { type: 'section', icon: 'mdi-plus-circle-outline', title: '每日建卡', note: '使用标准 Cron 安排建卡和刷新，修改后保存即可重载计划。', grid: 'grid-2', fusionDailyCard: true, fields: [
        { key: 'fusion_card_create_cron', icon: 'mdi-plus-circle-outline', label: '建卡时间', value: cronVal(form.fusion_card_create_cron) },
        { key: 'fusion_card_refresh_cron', icon: 'mdi-calendar-clock', label: '刷新时间', value: cronVal(form.fusion_card_refresh_cron) },
        { key: 'fusion_notify_msgtype', icon: 'mdi-email-outline', label: '消息类型', value: valOr(form.fusion_notify_msgtype, 'Plugin') },
      ] },
      { type: 'actions', actions: getActionsForSurface(['create_tg_console_card', 'run_daily_report'], 'config') },
    ],
    server: [
      { type: 'section', icon: 'mdi-cog-outline', title: '通知范围', note: '选择哪些事件要通知', grid: 'grid-3', fields: [
        { key: 'msgnotify_types', icon: 'mdi-format-list-checks', label: '通知事件', value: arrCount(form.msgnotify_types) },
        { key: 'msgnotify_servers', icon: 'mdi-server', label: '通知服务器', value: arrCount(form.msgnotify_servers) },
        { key: 'msgnotify_notify_type', icon: 'mdi-email-outline', label: '消息类型', value: valOr(form.msgnotify_notify_type, 'MediaServer'), disabled: Boolean(form.fusion_notify_enabled) },
      ] },
    ],
    subscribe: [
      { type: 'section', icon: 'mdi-movie-open-outline', title: '订阅范围', note: '选择需要检查并推送的订阅类型', grid: 'grid-2', fields: [
        { key: 'subscribe_reminder_cron', icon: 'mdi-calendar-clock', label: '检查时间', value: cronVal(form.subscribe_reminder_cron) },
        { key: 'subscribe_reminder_subtype', icon: 'mdi-movie-open-outline', label: '订阅类型', value: arrNames(form.subscribe_reminder_subtype) },
      ] },
      { type: 'section', icon: 'mdi-bell-outline', title: '通知渠道', note: '推送通知给用户', grid: 'grid-3', fields: [
        { key: 'subscribe_reminder_msgtype', icon: 'mdi-email-outline', label: '消息类型', value: valOr(form.subscribe_reminder_msgtype, 'Subscribe'), disabled: Boolean(form.fusion_notify_enabled) },
      ] },
      { type: 'actions', actions: getActionsForSurface(['run_subscribe_reminder'], 'config') },
    ],
    sites: [
      { type: 'section', icon: 'mdi-chart-line', title: '采集设置', note: '按 Cron 自动刷新站点数据；定时执行完成后发送结果。', grid: 'grid-2', fields: [
        { key: 'site_stat_cron', icon: 'mdi-calendar-clock', label: '统计时间', value: cronVal(form.site_stat_cron) },
        { key: 'site_stat_dashboard_type', icon: 'mdi-database-outline', label: '数据范围', value: form.site_stat_dashboard_type === 'total' ? '汇总' : '今日' },
      ] },
      { type: 'actions', actions: getActionsForSurface(['run_site_stat'], 'config') },
    ],
    hc: [
      { type: 'section', icon: 'mdi-gauge', title: '巡检阈值', note: '设置健康巡检的容量告警阈值', grid: 'grid-2', fields: [
        { key: 'health_check_cron', icon: 'mdi-calendar-clock', label: '巡查时间', value: cronVal(form.health_check_cron) },
        { key: 'health_check_storage_threshold', icon: 'mdi-gauge', label: '容量阈值', value: `${form.health_check_storage_threshold || 85}%` },
      ] },
      { type: 'section', icon: 'mdi-cog-outline', title: '巡查范围', note: '选择巡查项目', grid: 'grid-3', fields: [
        { key: 'health_check_database_targets', icon: 'mdi-database-outline', label: '数据库', value: arrCount(form.health_check_database_targets) },
        { key: 'health_check_storage_targets', icon: 'mdi-harddisk', label: '存储空间', value: arrCount(form.health_check_storage_targets) },
        { key: 'health_check_directory_targets', icon: 'mdi-folder-outline', label: '目录权限', value: arrCount(form.health_check_directory_targets) },
      ] },
      { type: 'section', icon: 'mdi-bell-outline', title: '巡检通知', note: '异常结果与正常完成结果分别控制通知渠道。', grid: 'grid-2', fields: [
        { key: 'health_check_notify', icon: 'mdi-alert-circle-outline', label: '异常通知', value: onOff(form.health_check_notify) },
        { key: 'health_check_notify_type', icon: 'mdi-email-outline', label: '异常通知渠道', value: valOr(form.health_check_notify_type, 'Plugin'), disabled: Boolean(form.fusion_notify_enabled) },
        { key: 'health_check_completion_notify_enabled', icon: 'mdi-check-circle-outline', label: '巡检完成通知', value: onOff(form.health_check_completion_notify_enabled) },
        { key: 'health_check_completion_notify_type', icon: 'mdi-email-check-outline', label: '完成通知渠道', value: valOr(form.health_check_completion_notify_type, 'Plugin'), disabled: Boolean(form.fusion_notify_enabled) },
      ] },
      { type: 'actions', actions: getActionsForSurface(['run_health_check'], 'config') },
    ],
    seedremove: [
      { type: 'section', icon: 'mdi-download-network-outline', title: '执行与保护', grid: 'grid-2', seedcleanPrimary: true, fields: [
        { key: 'seedclean_downloaders', icon: 'mdi-download-network-outline', label: '下载器', value: arrCount(form.seedclean_downloaders), compactSelection: true },
        { key: 'seedclean_cron', icon: 'mdi-calendar-clock', label: '执行时间', value: cronVal(form.seedclean_cron), retainInCard: true },
        { key: 'seedclean_action', icon: 'mdi-play', label: '处理方式', value: form.seedclean_action === 'delete' ? '删除种子' : form.seedclean_action === 'deletefile' ? '删除种子和文件' : '暂停' },
        { key: 'seedclean_samedata', icon: 'mdi-layers-outline', label: '同时处理辅种', value: onOff(form.seedclean_samedata) },
        { key: 'seedclean_mponly', icon: 'mdi-alpha-m-box-outline', label: '仅处理 MP 任务', value: onOff(form.seedclean_mponly) },
        { key: 'seedclean_notify', icon: 'mdi-bell-outline', label: '定时执行后通知', value: onOff(form.seedclean_notify), retainInCard: true },
        { key: 'seedclean_notify_type', icon: 'mdi-email-outline', label: '通知渠道', value: valOr(form.seedclean_notify_type, 'Plugin'), disabled: Boolean(form.fusion_notify_enabled), retainInCard: true },
      ] },
      { type: 'advanced', icon: 'mdi-filter-outline', title: '筛选条件', grid: 'grid-2', embeddedDrawer: true, dictionary: 'seedclean-status', fields: [
        { key: 'seedclean_size', icon: 'mdi-weight', label: '大小（GB）', placeholder: '例如：1-50', value: valOr(form.seedclean_size, '不限') },
        { key: 'seedclean_ratio', icon: 'mdi-percent', label: '分享率', placeholder: '例如：2.0', value: valOr(form.seedclean_ratio, '不限') },
        { key: 'seedclean_time', icon: 'mdi-timer-outline', label: '做种时长（小时）', placeholder: '例如：72', value: valOr(form.seedclean_time, '不限') },
        { key: 'seedclean_upspeed', icon: 'mdi-gauge', label: '平均上传上限（KB/s）', placeholder: '例如：50', value: valOr(form.seedclean_upspeed, '不限') },
        { key: 'seedclean_labels', icon: 'mdi-tag-outline', label: '下载器标签', placeholder: '例如：保留,MoviePilot', value: valOr(form.seedclean_labels, '不限') },
        { key: 'seedclean_torrentstates', icon: 'mdi-signal', label: 'qB 任务状态', placeholder: '例如：pausedUP,stalledUP', value: valOr(form.seedclean_torrentstates, '不限') },
        { key: 'seedclean_torrentcategorys', icon: 'mdi-tag-multiple-outline', label: 'qB 分类', placeholder: '例如：电影,剧集', value: valOr(form.seedclean_torrentcategorys, '不限') },
        { key: 'seedclean_trtorrentstates', icon: 'mdi-signal', label: 'TR 任务状态', placeholder: '例如：6,error', value: valOr(form.seedclean_trtorrentstates, '不限') },
        { key: 'seedclean_errorkeywords', icon: 'mdi-alert-circle-outline', label: 'TR 错误关键词', placeholder: '例如：timeout|permission', value: valOr(form.seedclean_errorkeywords, '不限') },
        { key: 'seedclean_pathkeywords', icon: 'mdi-folder-outline', label: '保存路径', placeholder: '例如：^/downloads/movie', value: valOr(form.seedclean_pathkeywords, '不限') },
        { key: 'seedclean_trackerkeywords', icon: 'mdi-link-variant', label: 'Tracker 关键词', placeholder: '例如：tracker\\.example\\.com', value: valOr(form.seedclean_trackerkeywords, '不限') },
      ] },
      { type: 'actions', danger: true, actions: getActionsForSurface(['run_seed_clean'], 'config') },
    ],
    dltagmain: [
      { type: 'section', icon: 'mdi-download-network-outline', title: '下载器助手设置', grid: 'grid-2', fields: [
        { key: 'dltag_downloaders', icon: 'mdi-download-network-outline', label: '下载器', value: Array.isArray(form.dltag_downloaders) && form.dltag_downloaders.length ? `已选 ${form.dltag_downloaders.length} 项` : '全部可用', layoutGroup: 'scope-tasks' },
        { key: 'dltag_tasks', icon: 'mdi-format-list-checks', label: '执行任务', value: `已选 ${Array.isArray(form.dltag_tasks) ? form.dltag_tasks.length : 0} 项`, layoutGroup: 'scope-tasks' },
        { key: 'dltag_listen_download', icon: 'mdi-download-outline', label: '监听新增下载（标签/辅种）', value: onOff(form.dltag_listen_download), layoutGroup: 'automatic-tagging' },
        { key: 'dltag_prefix', icon: 'mdi-pencil-outline', label: '站点标签前缀', placeholder: '例如 站点-', value: valOr(form.dltag_prefix, '无'), layoutGroup: 'automatic-tagging', hidden: !dltagTaggingActive },
        { key: 'dltag_not_select_all_tag', icon: 'mdi-checkbox-multiple-outline', label: '未全选标签', placeholder: '例如 非全', value: valOr(form.dltag_not_select_all_tag, '非全'), layoutGroup: 'automatic-tagging', hidden: !dltagTaggingActive },
        { key: 'dltag_listen_source_file', icon: 'mdi-file-remove-outline', label: '监听源文件删除', value: onOff(form.dltag_listen_source_file), layoutGroup: 'cleanup-source' },
        { key: 'dltag_source_delete_strategy', icon: 'mdi-timer-outline', label: '源文件清理时机', value: valOr(form.dltag_source_delete_strategy, 'delayed'), layoutGroup: 'cleanup-source', hidden: !form.dltag_listen_source_file },
        { key: 'dltag_cron', icon: 'mdi-calendar-clock', label: '执行时间', placeholder: '例如 0 */6 * * *（每 6 小时）', value: cronVal(form.dltag_cron), retainInCard: true, layoutGroup: 'schedule-notification' },
        { key: 'dltag_scheduled_notify', icon: 'mdi-bell-outline', label: '定时执行后通知', value: onOff(form.dltag_scheduled_notify), layoutGroup: 'schedule-notification' },
        { key: 'dltag_notify_type', icon: 'mdi-email-outline', label: '通知渠道', value: valOr(form.dltag_notify_type, 'Plugin'), disabled: Boolean(form.fusion_notify_enabled), layoutGroup: 'schedule-notification', hidden: !form.dltag_scheduled_notify },
      ] },
      { type: 'advanced', icon: 'mdi-link-variant', title: 'Tracker 映射', grid: 'grid-2', embeddedDrawer: true, drawer: 'dltag-tracker', fields: [
        { key: 'dltag_tracker_mappings', icon: 'mdi-link-variant', label: '映射规则', rows: 6, placeholder: '每行一条，例如 tracker.example.com => 站点标签；也支持 tracker.example.com = 站点标签', value: form.dltag_tracker_mappings ? '已配置' : '未配置' },
      ] },
      { type: 'actions', actions: getActionsForSurface(['run_downloader_helper'], 'config') },
    ],
    subfill: [
      { type: 'subfill-selector', module: 'subfill_download', masterKey: 'subfill_enabled', icon: 'mdi-auto-fix', title: '下载完成订阅填充' },
      { type: 'subfill-selector', module: 'subfill_category', masterKey: 'subfill_category_enabled', icon: 'mdi-layers-outline', title: '二级分类订阅填充' },
      { type: 'subfill-detail', module: 'subfill_download', icon: 'mdi-auto-fix', title: '下载完成订阅填充', grid: 'grid-2', fields: [
        { key: 'subfill_details', icon: 'mdi-format-list-checks', label: '填充项', value: arrNames(form.subfill_details) },
        ...subfillCompletionNotifyFields(),
      ] },
      { type: 'subfill-detail', module: 'subfill_category', icon: 'mdi-layers-outline', title: '二级分类订阅填充', grid: 'grid-2', fields: [
        { key: 'subfill_category_confs', icon: 'mdi-code-tags', label: '规则配置', value: form.subfill_category_confs ? '已配置' : '未配置', hidden: true },
        ...subfillCompletionNotifyFields(),
      ] },
      { type: 'actions', actions: getActionsForSurface(['subfill_clear_history', 'subfill_clear_handled'], 'config') },
    ],
    backup: [
      { type: 'backup-selector', module: 'backup', masterKey: 'backup_enabled', icon: 'mdi-archive-arrow-up-outline', title: '自动备份' },
      { type: 'backup-selector', module: 'backup_webdav', masterKey: 'backup_webdav_enabled', icon: 'mdi-cloud-outline', title: '远端备份' },
      { type: 'backup-detail', module: 'backup', icon: 'mdi-archive-arrow-up-outline', title: '自动备份', grid: 'grid-2', fields: [
        { key: 'backup_cron', icon: 'mdi-calendar-clock', label: '备份时间', value: cronVal(form.backup_cron), retainInCard: true },
        { key: 'backup_path', icon: 'mdi-folder-outline', label: '本地路径', value: valOr(form.backup_path, '/config/plugins/Signal/Backup') },
        { key: 'backup_keep_count', icon: 'mdi-content-copy', label: '本地保留', value: `${form.backup_keep_count || 5} 份` },
        { key: 'backup_notify', icon: 'mdi-bell-outline', label: '定时执行后通知', value: onOff(form.backup_notify) },
        { key: 'backup_notify_type', icon: 'mdi-email-outline', label: '通知渠道', value: valOr(form.backup_notify_type, 'Plugin'), disabled: Boolean(form.fusion_notify_enabled) },
      ] },
      { type: 'backup-detail', module: 'backup_webdav', icon: 'mdi-cloud-outline', title: '远端备份', grid: 'grid-2', fields: [
        { key: 'backup_webdav_hostname', icon: 'mdi-web', label: 'WebDAV 地址', value: form.backup_webdav_hostname ? '已配置' : '未配置' },
        { key: 'backup_webdav_login', icon: 'mdi-account-outline', label: '账号', value: form.backup_webdav_login ? '已配置' : '未配置' },
        { key: 'backup_webdav_password', icon: 'mdi-lock-outline', label: '密码', value: form.backup_webdav_password ? '已配置' : '未配置' },
        { key: 'backup_webdav_max_count', icon: 'mdi-content-copy', label: '远端保留', value: `${form.backup_webdav_max_count || 5} 份` },
        { key: 'backup_webdav_digest_auth', icon: 'mdi-shield-outline', label: 'Digest 认证', value: onOff(form.backup_webdav_digest_auth) },
        { key: 'backup_webdav_disable_check', icon: 'mdi-lock-check-outline', label: '跳过证书校验', value: onOff(form.backup_webdav_disable_check) },
      ] },
      { type: 'actions', actions: getActionsForSurface(['run_backup'], 'config') },
    ],
    logs: [
      { type: 'section', icon: 'mdi-file-document-remove-outline', title: '配置项', grid: 'grid-2', fields: [
        { key: 'log_clean_cron', icon: 'mdi-calendar-clock', label: '清理时间', value: cronVal(form.log_clean_cron) },
        { key: 'log_clean_rows', icon: 'mdi-format-list-numbered', label: '保留行数', value: `${form.log_clean_rows || 300} 行` },
        { key: 'log_clean_selected_ids', icon: 'mdi-puzzle-outline', label: '限定插件', value: form.log_clean_selected_ids?.length ? `${form.log_clean_selected_ids.length} 个` : '全部' },
        { key: 'log_clean_notify', icon: 'mdi-bell-outline', label: '定时执行后通知', value: onOff(form.log_clean_notify) },
        { key: 'log_clean_notify_type', icon: 'mdi-email-outline', label: '通知渠道', value: valOr(form.log_clean_notify_type, 'Plugin') },
      ] },
      { type: 'actions', actions: getActionsForSurface(['run_log_clean'], 'config') },
    ],
    updates: [
      { type: 'update-selector', module: 'mp_update', masterKey: 'mp_update_enabled', icon: 'mdi-update', title: 'MoviePilot' },
      { type: 'update-selector', module: 'plugin_update_reminder', masterKey: 'plugin_update_reminder_enabled', icon: 'mdi-puzzle-outline', title: '插件' },
      { type: 'update-selector', module: 'market_update', masterKey: 'market_update_enabled', icon: 'mdi-database-sync-outline', title: '插件库' },
      { type: 'update-detail', module: 'mp_update', icon: 'mdi-update', title: 'MoviePilot 更新', grid: 'grid-2', fields: [
        { key: 'mp_update_cron', icon: 'mdi-calendar-clock', label: '检查时间', value: cronVal(form.mp_update_cron), retainInCard: true },
        { key: 'mp_update_types', icon: 'mdi-cube-outline', label: '检查范围', value: arrNames(form.mp_update_types) },
        { key: 'mp_update_scheduled_notify', icon: 'mdi-bell-outline', label: '更新结果通知', value: onOff(form.mp_update_scheduled_notify) },
        { key: 'mp_update_notify_type', icon: 'mdi-email-outline', label: '通知渠道', value: valOr(form.mp_update_notify_type, 'Plugin'), disabled: Boolean(form.fusion_notify_enabled) },
      ], actions: getActionsForSurface(['run_mp_update'], 'config') },
      { type: 'update-detail', module: 'plugin_update_reminder', icon: 'mdi-puzzle-outline', title: '插件更新', grid: 'grid-2', fields: [
        { key: 'plugin_update_reminder_cron', icon: 'mdi-calendar-clock', label: '检查时间', value: cronVal(form.plugin_update_reminder_cron), retainInCard: true, layoutGroup: 'plugin-update-check' },
        { key: 'plugin_update_reminder_scheduled_notify', icon: 'mdi-bell-outline', label: '更新结果通知', value: onOff(form.plugin_update_reminder_scheduled_notify), layoutGroup: 'plugin-update-check' },
        { key: 'plugin_update_reminder_notify_type', icon: 'mdi-email-outline', label: '通知渠道', value: valOr(form.plugin_update_reminder_notify_type, 'Plugin'), disabled: Boolean(form.fusion_notify_enabled), layoutGroup: 'plugin-update-check' },
        { key: 'plugin_auto_install_enabled', icon: 'mdi-package-down', label: '自动安装', value: onOff(form.plugin_auto_install_enabled), layoutGroupStart: true, layoutGroup: 'plugin-auto-install' },
        { key: 'plugin_auto_install_scheduled_notify', icon: 'mdi-bell-outline', label: '安装后通知', value: onOff(form.plugin_auto_install_scheduled_notify), layoutGroup: 'plugin-auto-install' },
        { key: 'plugin_auto_install_notify_type', icon: 'mdi-email-check-outline', label: '安装通知渠道', value: valOr(form.plugin_auto_install_notify_type, 'Plugin'), disabled: Boolean(form.fusion_notify_enabled), layoutGroup: 'plugin-auto-install' },
        { key: 'plugin_auto_install_scope_mode', icon: 'mdi-format-list-bulleted', label: '安装范围', value: form.plugin_auto_install_scope_mode || 'all', layoutGroup: 'plugin-auto-install' },
        { key: 'plugin_auto_install_install_ids', icon: 'mdi-puzzle-outline', label: '指定插件', value: arrNames(form.plugin_auto_install_install_ids), layoutGroup: 'plugin-auto-install' },
        { key: 'plugin_auto_install_exclude_ids', icon: 'mdi-shield-outline', label: '排除插件', value: arrNames(form.plugin_auto_install_exclude_ids), layoutGroup: 'plugin-auto-install' },
      ], actions: getActionsForSurface(['run_plugin_update_reminder'], 'config') },
      { type: 'update-detail', module: 'market_update', icon: 'mdi-database-sync-outline', title: '插件库同步', grid: 'grid-2', fields: [
        { key: 'market_update_cron', icon: 'mdi-calendar-clock', label: '同步时间', value: cronVal(form.market_update_cron), retainInCard: true, layoutGroup: 'market-sync' },
        { key: 'market_update_scheduled_notify', icon: 'mdi-bell-outline', label: '同步结果通知', value: onOff(form.market_update_scheduled_notify), layoutGroup: 'market-sync' },
        { key: 'market_update_notify_type', icon: 'mdi-email-outline', label: '通知渠道', value: valOr(form.market_update_notify_type, 'Plugin'), disabled: Boolean(form.fusion_notify_enabled), layoutGroup: 'market-sync' },
      ], actions: getActionsForSurface(['run_market_update'], 'config') },
    ],
    clean: [
      { type: 'section', icon: 'mdi-alert-outline', title: '卸载设置', grid: 'grid-4', fields: [
        { key: 'plugin_uninstall_ids', icon: 'mdi-puzzle-outline', label: '目标插件', value: arrCount(form.plugin_uninstall_ids) },
        { key: 'plugin_uninstall_clear_config', icon: 'mdi-cog-outline', label: '清除配置', value: onOff(form.plugin_uninstall_clear_config) },
        { key: 'plugin_uninstall_clear_data', icon: 'mdi-database-outline', label: '清除数据', value: onOff(form.plugin_uninstall_clear_data) },
        { key: 'plugin_uninstall_delete_source', icon: 'mdi-code-tags', label: '删除源码', value: onOff(form.plugin_uninstall_delete_source) },
      ], danger: true },
      {
        type: 'actions',
        danger: true,
        actions: getActionsForSurface(['run_plugin_uninstall'], 'config'),
      },
    ],
  }), replicaItemSources.value));
  return cards
});
const currentPageLayout = computed(() => getConfigPageLayout(activeSub.value));
const currentPageActiveCategory = computed(() => ({
  updates: activeUpdateModule.value,
  backup: activeBackupModule.value,
  subfill: activeSubfillModule.value,
})[activeSub.value] || '');
const currentReplicaCards = computed(() => (
  replicaCards.value[activeSub.value] || replicaCards.value.fusion
).map(card => Array.isArray(card.fields)
  ? { ...card, fields: resolveReplicaFields(card.fields, form) }
  : card));
const settingCards = computed(() => currentReplicaCards.value.filter(card => card.type !== 'actions'));
const updateSelectorCards = computed(() => settingCards.value.filter(card => card.type === 'update-selector'));
const activeUpdateDetailCard = computed(() => settingCards.value.find(card => card.type === 'update-detail' && card.module === activeUpdateModule.value) || null);
const backupSelectorCards = computed(() => settingCards.value.filter(card => card.type === 'backup-selector'));
const activeBackupDetailCard = computed(() => settingCards.value.find(card => card.type === 'backup-detail' && card.module === activeBackupModule.value) || null);
const subfillSelectorCards = computed(() => settingCards.value.filter(card => card.type === 'subfill-selector'));
const activeSubfillDetailCard = computed(() => settingCards.value.find(card => card.type === 'subfill-detail' && card.module === activeSubfillModule.value) || null);
const seedCleanPrimaryCard = computed(() => settingCards.value.find(card => card.seedcleanPrimary) || null);
const seedCleanFilterCard = computed(() => settingCards.value.find(card => card.dictionary === 'seedclean-status') || null);
const downloaderTrackerCard = computed(() => settingCards.value.find(card => card.drawer === 'dltag-tracker') || null);
function uniqueCardFields(cards) {
  const keys = new Set();
  return cards.flatMap(card => card.fields || []).filter((field) => {
    if (!field?.key || keys.has(field.key)) return false
    keys.add(field.key);
    return true
  })
}
const currentSinglePageFields = computed(() => currentPageLayout.value.mode === 'single'
  ? uniqueCardFields(settingCards.value)
  : []);
const downloaderHelperFields = computed(() => uniqueCardFields(
  settingCards.value.filter(card => card.drawer !== 'dltag-tracker'),
)
  .filter(field => !hiddenDownloaderHelperCompatibilityFieldKeys.includes(field.key)));
const logCleanFields = computed(() => currentSinglePageFields.value);
const singlePageCard = computed(() => ({
  type: 'section',
  icon: currentSub.value?.icon || 'mdi-tune-variant',
  title: '配置项',
  grid: 'grid-2',
}));
const actionCards = computed(() => currentReplicaCards.value.filter(card => card.type === 'actions'));
const singlePageActionCard = computed(() => actionCards.value[0] || null);
const backupActionCard = computed(() => actionCards.value.find(card => card.actions?.some(item => item.path === 'run_backup')) || null);
const subfillActionCard = computed(() => actionCards.value.find(card => card.actions?.some(item => item.path === 'subfill_clear_history')) || null);
const pluginUninstallCard = computed(() => activeSub.value === 'clean'
  ? settingCards.value.find(card => card.fields?.some(field => field.key === 'plugin_uninstall_ids')) || null
  : null);
const pluginUninstallActionCard = computed(() => activeSub.value === 'clean'
  ? actionCards.value.find(card => card.actions?.some(item => item.path === 'run_plugin_uninstall')) || null
  : null);
const configActionHints = {
  fusion: '管理卡片状态，可建卡或刷新数据',
  server: '配置完成后即时生效',
  subscribe: '手动推送今日订阅更新',
  sites: '立即刷新站点统计面板',
  hc: '手动执行一次完整巡检',
  seedremove: '确认后按当前下载器和筛选条件执行',
  dltagmain: '执行标签、做种与失效任务检查',
  subfill: '清理记录可触发重新填充',
  backup: '按当前设置立即备份一次',
  logs: '按保留行数裁剪日志文件',
  updates: '检查系统、插件和插件库更新，并按当前策略处理',
  clean: '确认后执行不可逆卸载',
};
const currentActionHint = computed(() => configActionHints[activeSub.value] || '');
const fusionTakeoverNoticeBySub = Object.freeze({
  fusion: 'Fusion 统一管理各业务通知渠道；业务范围、调度和手动动作保持可编辑。',
  server: '融合通知仅接管通知渠道；通知事件和媒体服务器仍可编辑。',
  subscribe: '融合通知仅接管通知渠道；检查时间和订阅类型仍可编辑。',
  sites: '融合通知仅接管通知渠道；统计时间和数据范围仍可编辑。',
  hc: '融合通知仅接管通知渠道；巡查时间、阈值和巡查范围仍可编辑。',
  seedremove: '融合通知仅接管自动删种的通知渠道；执行时间和清理规则仍可编辑。',
  dltagmain: '融合通知已接管下载器助手的通知渠道，任务和清理设置仍由你控制。',
  backup: '融合通知仅接管通知渠道；备份时间、路径和保留策略仍可编辑。',
  logs: '融合通知只接管日志清理的通知渠道；Cron、清理范围和定时执行后通知仍由你控制。',
  subfill: '融合通知已接管订阅填充的通知渠道；下载完成填充和二级分类填充仍可分别控制。',
  updates: '融合通知已接管系统更新、插件更新和插件库同步的通知渠道；各任务通知开关、Cron、检查范围和处理方式仍可编辑。',
});
const fusionTakeoverNotice = computed(() => {
  if (!form.fusion_notify_enabled) return null
  if (activeSub.value === 'dltagmain' && !form.dltag_scheduled_notify) return null
  return fusionTakeoverNoticeBySub[activeSub.value] || null
});
const seedCleanRiskNotice = computed(() => activeSub.value === 'seedremove'
  ? '自动删种会按当前筛选条件暂停或删除任务；执行前请确认动作与范围。'
  : null);

function compactIcon(name, className = 'aoa-mdi-icon') {
  const isSectionIcon = className.includes('aoa-mdi-icon--section');
  const fieldFaIcon = className.includes('aoa-mdi-icon--field') ? replicaFieldFaIcons[name] : null;
  const sectionFaIcon = isSectionIcon && name === 'mdi-calendar-clock'
    ? { path: faClockPath, viewBox: '0 0 512 512' }
    : null;
  const faIcon = fieldFaIcon || sectionFaIcon;
  return h('svg', { class: className, viewBox: faIcon?.viewBox || '0 0 24 24', width: isSectionIcon ? '15' : '18', height: isSectionIcon ? '15' : '13', 'aria-hidden': 'true' }, [
    h('path', { d: faIcon?.path || iconPath(name), fill: 'currentColor' }),
  ])
}
function actionIcon(name) {
  const faActionIcons = {
    'mdi-plus-circle-outline': faCirclePlusPath,
    'mdi-sync': faArrowsRotatePath,
  };
  if (faActionIcons[name]) {
    return h('svg', { class: 'aoa-mdi-icon aoa-mdi-icon--action', viewBox: '0 0 512 512', width: '14', height: '14', 'aria-hidden': 'true' }, [
      h('path', { d: faActionIcons[name], fill: 'currentColor' }),
    ])
  }
  return compactIcon(name, 'aoa-mdi-icon aoa-mdi-icon--action')
}
function navIconMeta(item) {
  const meta = {
    notify: { path: faBellPath, viewBox: '0 0 448 512' },
    monitor: { path: faChartLinePath, viewBox: '0 0 512 512' },
    download: { path: faDownloadPath, viewBox: '0 0 512 512' },
    maintenance: { path: faHeartPulsePath, viewBox: '0 0 512 512' },
    plugin: { path: faPuzzlePiecePath, viewBox: '0 0 512 512' },
    fusion: { path: faIdCardPath, viewBox: '0 0 576 512' },
    server: { path: faTvPath, viewBox: '0 0 640 512' },
    subscribe: { path: faBellPath, viewBox: '0 0 448 512' },
  }[item?.key];
  return meta || { path: iconPath(item?.icon || 'mdi-cog-outline'), viewBox: '0 0 24 24' }
}
function navIconStyle(item, height = 14) {
  const [, , width, viewHeight] = navIconMeta(item).viewBox.split(/\s+/).map(Number);
  const naturalWidth = width && viewHeight ? (width / viewHeight) * height : height;
  return {
    width: `${naturalWidth.toFixed(3)}px`,
    height: `${height}px`,
    lineHeight: `${height}px`,
  }
}

const CompactActionRow = defineComponent({
  name: 'CompactActionRow',
  props: { card: { type: Object, required: true }, effectiveState: { type: String, default: '' } },
  emits: ['run'],
  setup(props, { emit }) {
    return () => {
      const actionButtons = (props.card.actions || []).flatMap(actionItem => {
        const availability = getActionAvailability(actionItem);
        if (!availability.visible) return []
        const isDisabled = availability.disabled;
        const title = availability.disabledReason;
        const buttonLabel = isActionRunning(actionItem)
          ? '正在执行...'
          : actionItem.label;
        return [h('button', {
          key: actionItem.label,
          type: 'button',
          class: ['aoa-design-action-btn', {
            'aoa-design-action-btn--danger': props.card.danger,
            'aoa-design-action-btn--disabled': isDisabled,
          }],
          disabled: isDisabled,
          title,
          'aria-label': title ? `${actionItem.label}，${title}` : actionItem.label,
          'data-disabled-reason': title || undefined,
          'data-config-action-path': actionItem.path,
          'data-effective-state': props.effectiveState || undefined,
          onClick: () => {
            if (isDisabled) return
            emit('run', actionItem);
          },
        }, [actionIcon(actionItem.icon), h('span', buttonLabel)])]
      });

      return h('div', {
        class: ['aoa-design-actions', {
          'aoa-design-actions--danger': props.card.danger,
          'aoa-design-actions--single': (props.card.actions || []).length === 1,
        }],
        'data-html-action-row': '',
      }, actionButtons)
    }
  },
});

function bindDialogScrollHost() {
  const host = configRoot.value?.closest?.('.v-card-text.pa-0');
  if (!host || host === dialogScrollHost) return
  dialogScrollHost?.classList.remove('aoa-config-scroll-host');
  dialogSurfaceHost?.classList.remove('aoa-config-single-surface-host');
  dialogScrollHost = host;
  dialogScrollHost.classList.add('aoa-config-scroll-host');
  dialogSurfaceHost = host.closest?.('.v-card') || null;
  dialogSurfaceHost?.classList.add('aoa-config-single-surface-host');
}

async function loadRemoteData() {
  if (!apiHandle.value?.get) return
  await Promise.allSettled([
    loadInstalledPlugins(),
    loadTgConsoleStatus(),
    loadDownloaders(),
    loadMediaservers(),
  ]);
  if (apiHandle.value?.get) await loadBackupArchives();
}

onMounted$1(() => {
  bindDialogScrollHost();
  revealActiveCategories('auto');
  loadRemoteData();
});

watch$1(apiHandle, (api, previousApi) => {
  if (api && api !== previousApi) loadRemoteData();
});

watch$1(activeBackupModule, module => {
  if (!apiHandle.value?.get) return
  if (module === 'backup_webdav') loadWebdavBackupArchives();
  else if (module === 'backup' && !backupArchives.value.length) loadBackupArchives();
});

onBeforeUnmount(() => {
  dialogScrollHost?.classList.remove('aoa-config-scroll-host');
  dialogSurfaceHost?.classList.remove('aoa-config-single-surface-host');
  dialogScrollHost = null;
  dialogSurfaceHost = null;
});

return (_ctx, _cache) => {
  return (_openBlock$1(), _createElementBlock("div", {
    ref_key: "configRoot",
    ref: configRoot,
    class: _normalizeClass(["aoa-config aoa-root aoa-plugin-shell", _unref(rootThemeClass)]),
    "data-config-shell": "",
    "data-config-dirty": String(_unref(isDirty)),
    "data-config-record-state": __props.configRecordState,
    "data-config-load-state": __props.configLoadState,
    "data-effective-state": configLoadReady.value ? currentEffectiveState.value.code : 'unknown',
    "aria-busy": configLoadBusy.value
  }, [
    _createElementVNode("header", _hoisted_2, [
      _createElementVNode("div", { class: "aoa-config-brand" }, [
        _createElementVNode("span", { class: "aoa-config-brand-icon" }, [
          _createElementVNode("svg", {
            class: "aoa-mdi-icon aoa-mdi-icon--brand",
            viewBox: "0 0 512 512",
            width: "20",
            height: "20",
            "aria-hidden": "true"
          }, [
            _createElementVNode("path", {
              d: faShieldHalvedPath,
              fill: "currentColor"
            })
          ])
        ]),
        _cache[11] || (_cache[11] = _createElementVNode("span", { class: "aoa-config-brand-copy" }, [
          _createElementVNode("strong", null, "配置中心")
        ], -1))
      ]),
      _createElementVNode("div", _hoisted_3, [
        _createElementVNode("div", _hoisted_4, [
          _cache[13] || (_cache[13] = _createElementVNode("span", { class: "aoa-config-master-switch__label" }, "插件总开关", -1)),
          _createElementVNode("button", {
            type: "button",
            class: _normalizeClass(["aoa-toggle-switch", { 'aoa-toggle-switch--on': configLoadReady.value && _unref(form).enabled }]),
            role: "switch",
            "aria-checked": configLoadReady.value && !!_unref(form).enabled,
            "aria-label": '插件总开关',
            disabled: configReadLocked.value,
            onClick: _cache[0] || (_cache[0] = $event => (_unref(form).enabled = !_unref(form).enabled))
          }, [...(_cache[12] || (_cache[12] = [
            _createElementVNode("span", { class: "aoa-toggle-switch__thumb" }, null, -1)
          ]))], 10, _hoisted_5)
        ]),
        _createElementVNode("button", {
          type: "button",
          class: "aoa-config-ghost-btn",
          "data-config-dashboard-button": "",
          title: '仪表盘',
          "aria-label": '仪表盘',
          disabled: configReadLocked.value,
          onClick: _cache[1] || (_cache[1] = (...args) => (_unref(openDashboard) && _unref(openDashboard)(...args)))
        }, [
          _createElementVNode("svg", {
            class: "aoa-mdi-icon aoa-mdi-icon--ghost",
            viewBox: "0 0 512 512",
            width: "12",
            height: "12",
            "aria-hidden": "true"
          }, [
            _createElementVNode("path", {
              d: faGaugePath,
              fill: "currentColor"
            })
          ]),
          _cache[14] || (_cache[14] = _createElementVNode("span", null, "仪表盘", -1))
        ], 8, _hoisted_6)
      ])
    ]),
    _createElementVNode("nav", {
      ref_key: "mainNav",
      ref: mainNav,
      class: "aoa-config-main-nav",
      "data-config-main-nav": "",
      "data-config-nav-scroll": "main",
      "aria-label": "配置分类",
      role: "tablist"
    }, [
      (_openBlock$1(true), _createElementBlock(_Fragment, null, _renderList(_unref(mainTabs), (item) => {
        return (_openBlock$1(), _createElementBlock("button", {
          key: item.key,
          type: "button",
          class: _normalizeClass(["aoa-config-main-tab", { 'aoa-config-main-tab--active': _unref(activeMain) === item.key }]),
          role: "tab",
          "aria-selected": _unref(activeMain) === item.key,
          "data-config-main-tab": item.key,
          "data-effective-state": configLoadReady.value ? mainEffectiveState(item.key) : 'unknown',
          disabled: configReadLocked.value,
          onClick: $event => (_unref(selectMain)(item.key)),
          onFocus: _cache[2] || (_cache[2] = $event => (_unref(revealCategoryItem)($event.currentTarget, 'auto')))
        }, [
          (_openBlock$1(), _createElementBlock("svg", {
            class: "aoa-mdi-icon aoa-mdi-icon--nav",
            viewBox: navIconMeta(item).viewBox,
            style: _normalizeStyle(navIconStyle(item, 14)),
            "aria-hidden": "true"
          }, [
            _createElementVNode("path", {
              d: navIconMeta(item).path,
              fill: "currentColor"
            }, null, 8, _hoisted_9)
          ], 12, _hoisted_8)),
          _createElementVNode("span", null, _toDisplayString(item.title), 1)
        ], 42, _hoisted_7))
      }), 128))
    ], 512),
    _createElementVNode("div", _hoisted_10, [
      _createElementVNode("div", {
        ref_key: "subtabList",
        ref: subtabList,
        class: "aoa-subtab-list",
        "data-config-nav-scroll": "sub",
        role: "tablist",
        "aria-label": `${_unref(currentMain).title} 二级分类`
      }, [
        (_openBlock$1(true), _createElementBlock(_Fragment, null, _renderList(_unref(currentSubs), (sub) => {
          return (_openBlock$1(), _createElementBlock("button", {
            key: sub.key,
            type: "button",
            id: `config-tab-${sub.key}`,
            class: _normalizeClass(["aoa-subtab", { 'aoa-subtab--active': _unref(activeSub) === sub.key }]),
            role: "tab",
            "aria-selected": _unref(activeSub) === sub.key,
            "aria-controls": `config-panel-${sub.key}`,
            "data-config-subtab": sub.key,
            "data-effective-state": configLoadReady.value ? effectiveStateFor(sub.key).code : 'unknown',
            disabled: configReadLocked.value,
            onClick: $event => (_unref(selectSub)(sub.key)),
            onFocus: _cache[3] || (_cache[3] = $event => (_unref(revealCategoryItem)($event.currentTarget, 'auto')))
          }, [
            (_openBlock$1(), _createElementBlock("svg", {
              class: "aoa-mdi-icon aoa-mdi-icon--subtab",
              viewBox: navIconMeta(sub).viewBox,
              style: _normalizeStyle(navIconStyle(sub, 13)),
              "aria-hidden": "true"
            }, [
              _createElementVNode("path", {
                d: navIconMeta(sub).path,
                fill: "currentColor"
              }, null, 8, _hoisted_14)
            ], 12, _hoisted_13)),
            _createElementVNode("span", null, _toDisplayString(sub.title), 1)
          ], 42, _hoisted_12))
        }), 128))
      ], 8, _hoisted_11),
      (_unref(currentSubTitle))
        ? (_openBlock$1(), _createElementBlock("div", _hoisted_15, _toDisplayString(_unref(currentSubTitle)), 1))
        : _createCommentVNode("", true)
    ]),
    _createElementVNode("main", {
      id: `config-panel-${_unref(activeSub)}`,
      class: "aoa-config-scroll",
      "data-config-scroll": "",
      "aria-labelledby": `config-tab-${_unref(activeSub)}`,
      "data-config-active-sub": _unref(activeSub),
      "data-effective-state": configLoadReady.value ? currentEffectiveState.value.code : 'unknown'
    }, [
      (!configLoadReady.value)
        ? (_openBlock$1(), _createElementBlock("section", {
            key: 0,
            class: _normalizeClass(["aoa-config-load-state", `aoa-config-load-state--${__props.configLoadState}`]),
            "data-config-load-panel": __props.configLoadState,
            role: __props.configLoadState === 'error' ? 'alert' : 'status',
            "aria-live": "polite",
            "aria-atomic": "true"
          }, [
            _createElementVNode("span", _hoisted_18, [
              (configLoadBusy.value)
                ? (_openBlock$1(), _createElementBlock("span", _hoisted_19))
                : (_openBlock$1(), _createElementBlock("svg", _hoisted_20, [
                    _createElementVNode("path", {
                      d: iconPath('mdi-alert-outline'),
                      fill: "currentColor"
                    }, null, 8, _hoisted_21)
                  ]))
            ]),
            _createElementVNode("span", _hoisted_22, [
              _cache[15] || (_cache[15] = _createElementVNode("span", { class: "aoa-config-load-state__eyebrow" }, "配置读取", -1)),
              _createElementVNode("strong", null, _toDisplayString(configLoadBusy.value ? '正在读取当前配置' : '当前配置读取失败'), 1),
              _createElementVNode("span", null, _toDisplayString(configLoadBusy.value
                ? '请稍候，读取完成前不会展示或保存未确认的默认值。'
                : '为避免覆盖已有设置，编辑、动作和保存已锁定。请重新读取后继续。'), 1),
              (__props.configLoadState === 'error' && configLoadErrorDetail.value)
                ? (_openBlock$1(), _createElementBlock("small", _hoisted_23, _toDisplayString(configLoadErrorDetail.value), 1))
                : _createCommentVNode("", true)
            ]),
            (__props.configLoadState === 'error')
              ? (_openBlock$1(), _createElementBlock("button", {
                  key: 0,
                  type: "button",
                  class: "aoa-config-btn aoa-config-load-state__retry",
                  "data-config-retry-load": "",
                  onClick: _cache[4] || (_cache[4] = $event => (emit('retry-load')))
                }, " 重新读取 "))
              : _createCommentVNode("", true)
          ], 10, _hoisted_17))
        : (_openBlock$1(), _createElementBlock(_Fragment, { key: 1 }, [
            _createElementVNode("section", {
              class: "aoa-config-hero-card",
              "data-config-active-card": "",
              "data-config-hero-tone": _unref(activeSub) === 'clean' ? 'danger' : 'neutral',
              tabindex: "0",
              "aria-label": `${currentHero.value.kicker}：${currentHeroTitle.value}`,
              "aria-live": "polite",
              "data-effective-state": currentEffectiveState.value.code
            }, [
              _createElementVNode("div", _hoisted_25, [
                _createElementVNode("span", _hoisted_26, [
                  (_openBlock$1(), _createElementBlock("svg", {
                    class: "aoa-mdi-icon aoa-mdi-icon--hero",
                    viewBox: heroIconViewBox.value,
                    width: "25",
                    height: "22",
                    "aria-hidden": "true"
                  }, [
                    _createElementVNode("path", {
                      d: heroIconPath.value,
                      fill: "currentColor"
                    }, null, 8, _hoisted_28)
                  ], 8, _hoisted_27))
                ]),
                _createElementVNode("span", _hoisted_29, [
                  _createElementVNode("span", _hoisted_30, _toDisplayString(currentHero.value.kicker), 1),
                  _createElementVNode("strong", _hoisted_31, _toDisplayString(currentHeroTitle.value), 1),
                  (currentHero.value.desc)
                    ? (_openBlock$1(), _createElementBlock("small", _hoisted_32, _toDisplayString(currentHero.value.desc), 1))
                    : _createCommentVNode("", true)
                ])
              ]),
              _createElementVNode("div", {
                class: "aoa-config-hero-right",
                "data-config-danger-header": _unref(activeSub) === 'clean' ? '' : undefined
              }, [
                _createElementVNode("span", {
                  class: _normalizeClass(["aoa-config-status-badge", { 'aoa-config-status-badge--on': _unref(activeSub) !== 'clean' && heroEffectivelyEnabled.value, 'aoa-config-status-badge--mixed': _unref(activeSub) !== 'clean' && heroEffectivelyMixed.value }])
                }, _toDisplayString(_unref(activeSub) === 'clean' ? '高风险操作' : heroStatusText.value), 3),
                (_unref(activeSub) !== 'updates' && _unref(activeSub) !== 'backup' && _unref(activeSub) !== 'subfill' && _unref(activeSub) !== 'clean')
                  ? (_openBlock$1(), _createElementBlock("button", {
                      key: 0,
                      type: "button",
                      class: _normalizeClass(["aoa-toggle-switch aoa-toggle-switch--hero", { 'aoa-toggle-switch--on': heroEffectivelyEnabled.value }]),
                      role: "switch",
                      "aria-checked": !!heroEnabled.value,
                      "aria-label": heroToggleLabel.value,
                      onClick: _cache[5] || (_cache[5] = $event => (setHeroEnabled(!heroEnabled.value)))
                    }, [...(_cache[16] || (_cache[16] = [
                      _createElementVNode("span", { class: "aoa-toggle-switch__thumb" }, null, -1)
                    ]))], 10, _hoisted_34))
                  : _createCommentVNode("", true)
              ], 8, _hoisted_33)
            ], 8, _hoisted_24),
            (fusionTakeoverNotice.value)
              ? (_openBlock$1(), _createBlock$1(_sfc_main$j, {
                  key: 0,
                  message: fusionTakeoverNotice.value
                }, null, 8, ["message"]))
              : _createCommentVNode("", true),
            (seedCleanRiskNotice.value)
              ? (_openBlock$1(), _createElementBlock("div", _hoisted_35, [
                  (_openBlock$1(), _createElementBlock("svg", _hoisted_36, [
                    _createElementVNode("path", {
                      d: iconPath('mdi-alert-outline'),
                      fill: "currentColor"
                    }, null, 8, _hoisted_37)
                  ])),
                  _createElementVNode("span", null, _toDisplayString(seedCleanRiskNotice.value), 1)
                ]))
              : _createCommentVNode("", true),
            _createElementVNode("div", _hoisted_38, [
              _createVNode(_sfc_main$q, {
                layout: currentPageLayout.value,
                "active-category": currentPageActiveCategory.value,
                "effective-state": currentEffectiveState.value.code
              }, {
                default: _withCtx(() => [
                  (_unref(activeSub) === 'clean')
                    ? (_openBlock$1(), _createBlock$1(_sfc_main$2, {
                        key: 0,
                        form: _unref(form),
                        card: pluginUninstallCard.value,
                        actions: pluginUninstallActionCard.value?.actions || [],
                        "effective-state": currentEffectiveState.value.code
                      }, {
                        actions: _withCtx(({ actions }) => [
                          _createVNode(_unref(CompactActionRow), {
                            card: { type: 'actions', danger: true, actions },
                            "effective-state": currentEffectiveState.value.code,
                            onRun: triggerConfigActionWithRefresh
                          }, null, 8, ["card", "effective-state"])
                        ]),
                        _: 1
                      }, 8, ["form", "card", "actions", "effective-state"]))
                    : (_unref(activeSub) === 'backup')
                      ? (_openBlock$1(), _createBlock$1(_sfc_main$6, {
                          key: 1,
                          form: _unref(form),
                          selectors: backupSelectorCards.value,
                          detail: activeBackupDetailCard.value,
                          actions: backupActionCard.value?.actions || [],
                          "active-module": _unref(activeBackupModule),
                          "effective-state": currentEffectiveState.value.code,
                          "keep-count-presets": _unref(keepCountPresets),
                          "backup-restore-unavailable": _unref(backupRestoreUnavailable),
                          "backup-restore-unavailable-message": _unref(backupRestoreUnavailableMessage),
                          "backup-archives": _unref(backupArchives),
                          "backup-archives-loading": _unref(backupArchivesLoading),
                          "backup-restore-loading": _unref(backupRestoreLoading),
                          "backup-restore-result": _unref(backupRestoreResult),
                          "backup-restore": _unref(backupRestore),
                          "webdav-backup-restore-unavailable": _unref(webdavBackupRestoreUnavailable),
                          "webdav-backup-restore-unavailable-message": _unref(webdavBackupRestoreUnavailableMessage),
                          "webdav-backup-archives": _unref(webdavBackupArchives),
                          "webdav-backup-archives-loading": _unref(webdavBackupArchivesLoading),
                          "webdav-backup-restore-loading": _unref(webdavBackupRestoreLoading),
                          "webdav-backup-restore-result": _unref(webdavBackupRestoreResult),
                          "webdav-backup-restore": _unref(webdavBackupRestore),
                          onSelectModule: _cache[6] || (_cache[6] = $event => (_unref(pageSession).selectModule('backup-selector', $event))),
                          onLoadBackupArchives: _unref(loadBackupArchives),
                          onPreviewBackupRestore: _unref(previewBackupRestore),
                          onRunBackupRestore: _unref(runBackupRestore),
                          onLoadWebdavBackupArchives: _unref(loadWebdavBackupArchives),
                          onPreviewWebdavBackupRestore: _unref(previewWebdavBackupRestore),
                          onRunWebdavBackupRestore: _unref(runWebdavBackupRestore)
                        }, {
                          actions: _withCtx(({ actions }) => [
                            _createVNode(_unref(CompactActionRow), {
                              card: { type: 'actions', actions },
                              "effective-state": currentEffectiveState.value.code,
                              onRun: triggerConfigActionWithRefresh
                            }, null, 8, ["card", "effective-state"])
                          ]),
                          _: 1
                        }, 8, ["form", "selectors", "detail", "actions", "active-module", "effective-state", "keep-count-presets", "backup-restore-unavailable", "backup-restore-unavailable-message", "backup-archives", "backup-archives-loading", "backup-restore-loading", "backup-restore-result", "backup-restore", "webdav-backup-restore-unavailable", "webdav-backup-restore-unavailable-message", "webdav-backup-archives", "webdav-backup-archives-loading", "webdav-backup-restore-loading", "webdav-backup-restore-result", "webdav-backup-restore", "onLoadBackupArchives", "onPreviewBackupRestore", "onRunBackupRestore", "onLoadWebdavBackupArchives", "onPreviewWebdavBackupRestore", "onRunWebdavBackupRestore"]))
                      : (_unref(activeSub) === 'subfill')
                        ? (_openBlock$1(), _createBlock$1(_sfc_main$4, {
                            key: 2,
                            form: _unref(form),
                            selectors: subfillSelectorCards.value,
                            detail: activeSubfillDetailCard.value,
                            actions: subfillActionCard.value?.actions || [],
                            "active-module": _unref(activeSubfillModule),
                            "effective-state": currentEffectiveState.value.code,
                            onSelectModule: _cache[7] || (_cache[7] = $event => (_unref(pageSession).selectModule('subfill-selector', $event))),
                            onProjectionChange: _cache[8] || (_cache[8] = $event => (_unref(pageSession).setSubfillProjectionOpen($event)))
                          }, {
                            actions: _withCtx(({ actions }) => [
                              _createVNode(_unref(CompactActionRow), {
                                card: { type: 'actions', actions },
                                "effective-state": currentEffectiveState.value.code,
                                onRun: triggerConfigActionWithRefresh
                              }, null, 8, ["card", "effective-state"])
                            ]),
                            _: 1
                          }, 8, ["form", "selectors", "detail", "actions", "active-module", "effective-state"]))
                        : (_unref(activeSub) === 'updates')
                          ? (_openBlock$1(), _createBlock$1(_sfc_main$3, {
                              key: 3,
                              form: _unref(form),
                              selectors: updateSelectorCards.value,
                              detail: activeUpdateDetailCard.value,
                              "active-module": _unref(activeUpdateModule),
                              "effective-state": currentEffectiveState.value.code,
                              onSelectModule: _cache[9] || (_cache[9] = $event => (_unref(pageSession).selectModule('update-selector', $event)))
                            }, {
                              actions: _withCtx(({ actions }) => [
                                _createVNode(_unref(CompactActionRow), {
                                  card: { type: 'actions', actions },
                                  "effective-state": currentEffectiveState.value.code,
                                  onRun: triggerConfigActionWithRefresh
                                }, null, 8, ["card", "effective-state"])
                              ]),
                              _: 1
                            }, 8, ["form", "selectors", "detail", "active-module", "effective-state"]))
                          : (_unref(activeSub) === 'fusion')
                            ? (_openBlock$1(), _createBlock$1(_sfc_main$r, {
                                key: 4,
                                card: singlePageCard.value,
                                "effective-state": currentEffectiveState.value.code
                              }, {
                                default: _withCtx(() => [
                                  _createVNode(_sfc_main$k, {
                                    form: _unref(form),
                                    fields: currentSinglePageFields.value,
                                    "notification-type-items": _unref(notificationTypeItems),
                                    status: _unref(tgConsoleStatus),
                                    loading: _unref(tgConsoleLoading),
                                    "effective-state": currentEffectiveState.value.code
                                  }, {
                                    operations: _withCtx(() => [
                                      (singlePageActionCard.value)
                                        ? (_openBlock$1(), _createBlock$1(_unref(CompactActionRow), {
                                            key: 0,
                                            card: singlePageActionCard.value,
                                            "effective-state": currentEffectiveState.value.code,
                                            onRun: triggerConfigActionWithRefresh
                                          }, null, 8, ["card", "effective-state"]))
                                        : _createCommentVNode("", true)
                                    ]),
                                    _: 1
                                  }, 8, ["form", "fields", "notification-type-items", "status", "loading", "effective-state"])
                                ]),
                                _: 1
                              }, 8, ["card", "effective-state"]))
                            : (_unref(activeSub) === 'server')
                              ? (_openBlock$1(), _createBlock$1(_sfc_main$r, {
                                  key: 5,
                                  card: singlePageCard.value,
                                  "effective-state": currentEffectiveState.value.code
                                }, {
                                  default: _withCtx(() => [
                                    _createVNode(_sfc_main$g, {
                                      form: _unref(form),
                                      fields: currentSinglePageFields.value,
                                      "msg-group-items": _unref(msgGroupItems),
                                      "mediaserver-options": _unref(mediaserverOptions),
                                      "notification-type-items": _unref(notificationTypeItems),
                                      "notification-locked-by-fusion": _unref(notificationLockedByFusion),
                                      "effective-state": currentEffectiveState.value.code
                                    }, null, 8, ["form", "fields", "msg-group-items", "mediaserver-options", "notification-type-items", "notification-locked-by-fusion", "effective-state"])
                                  ]),
                                  _: 1
                                }, 8, ["card", "effective-state"]))
                              : (_unref(activeSub) === 'subscribe')
                                ? (_openBlock$1(), _createBlock$1(_sfc_main$r, {
                                    key: 6,
                                    card: singlePageCard.value,
                                    "effective-state": currentEffectiveState.value.code
                                  }, {
                                    default: _withCtx(() => [
                                      _createVNode(_sfc_main$f, {
                                        form: _unref(form),
                                        fields: currentSinglePageFields.value,
                                        "subscribe-subtype-items": _unref(subscribeSubtypeItems),
                                        "message-type-items": _unref(messageTypeItems),
                                        "notification-locked-by-fusion": _unref(notificationLockedByFusion),
                                        "effective-state": currentEffectiveState.value.code
                                      }, {
                                        operations: _withCtx(() => [
                                          (singlePageActionCard.value)
                                            ? (_openBlock$1(), _createBlock$1(_unref(CompactActionRow), {
                                                key: 0,
                                                card: singlePageActionCard.value,
                                                "effective-state": currentEffectiveState.value.code,
                                                onRun: triggerConfigActionWithRefresh
                                              }, null, 8, ["card", "effective-state"]))
                                            : _createCommentVNode("", true)
                                        ]),
                                        _: 1
                                      }, 8, ["form", "fields", "subscribe-subtype-items", "message-type-items", "notification-locked-by-fusion", "effective-state"])
                                    ]),
                                    _: 1
                                  }, 8, ["card", "effective-state"]))
                                : (_unref(activeSub) === 'sites')
                                  ? (_openBlock$1(), _createBlock$1(_sfc_main$r, {
                                      key: 7,
                                      card: singlePageCard.value,
                                      "effective-state": currentEffectiveState.value.code
                                    }, {
                                      default: _withCtx(() => [
                                        _createVNode(_sfc_main$h, {
                                          form: _unref(form),
                                          fields: currentSinglePageFields.value,
                                          "site-stat-range-items": _unref(siteStatRangeItems),
                                          "notification-type-items": _unref(notificationTypeItems),
                                          "notification-locked-by-fusion": _unref(notificationLockedByFusion),
                                          "effective-state": currentEffectiveState.value.code
                                        }, {
                                          operations: _withCtx(() => [
                                            (singlePageActionCard.value)
                                              ? (_openBlock$1(), _createBlock$1(_unref(CompactActionRow), {
                                                  key: 0,
                                                  card: singlePageActionCard.value,
                                                  "effective-state": currentEffectiveState.value.code,
                                                  onRun: triggerConfigActionWithRefresh
                                                }, null, 8, ["card", "effective-state"]))
                                              : _createCommentVNode("", true)
                                          ]),
                                          _: 1
                                        }, 8, ["form", "fields", "site-stat-range-items", "notification-type-items", "notification-locked-by-fusion", "effective-state"])
                                      ]),
                                      _: 1
                                    }, 8, ["card", "effective-state"]))
                                  : (_unref(activeSub) === 'hc')
                                    ? (_openBlock$1(), _createBlock$1(_sfc_main$r, {
                                        key: 8,
                                        card: singlePageCard.value,
                                        "effective-state": currentEffectiveState.value.code
                                      }, {
                                        default: _withCtx(() => [
                                          _createVNode(_sfc_main$i, {
                                            form: _unref(form),
                                            fields: currentSinglePageFields.value,
                                            "health-selected-count": [
                  _unref(form).health_check_items,
                  _unref(form).health_check_database_targets,
                  _unref(form).health_check_storage_targets,
                  _unref(form).health_check_directory_targets,
                ].reduce((sum, value) => sum + (Array.isArray(value) ? value.length : 0), 0),
                                            "health-check-items": _unref(healthCheckItems),
                                            "health-database-targets": _unref(healthDatabaseTargets),
                                            "health-storage-targets": _unref(healthStorageTargets),
                                            "health-directory-targets": _unref(healthDirectoryTargets),
                                            "notification-type-items": _unref(notificationTypeItems),
                                            "notification-locked-by-fusion": _unref(notificationLockedByFusion),
                                            "effective-state": currentEffectiveState.value.code
                                          }, {
                                            operations: _withCtx(() => [
                                              (singlePageActionCard.value)
                                                ? (_openBlock$1(), _createBlock$1(_unref(CompactActionRow), {
                                                    key: 0,
                                                    card: singlePageActionCard.value,
                                                    "effective-state": currentEffectiveState.value.code,
                                                    onRun: triggerConfigActionWithRefresh
                                                  }, null, 8, ["card", "effective-state"]))
                                                : _createCommentVNode("", true)
                                            ]),
                                            _: 1
                                          }, 8, ["form", "fields", "health-selected-count", "health-check-items", "health-database-targets", "health-storage-targets", "health-directory-targets", "notification-type-items", "notification-locked-by-fusion", "effective-state"])
                                        ]),
                                        _: 1
                                      }, 8, ["card", "effective-state"]))
                                    : (_unref(activeSub) === 'seedremove')
                                      ? (_openBlock$1(), _createBlock$1(_sfc_main$r, {
                                          key: 9,
                                          card: singlePageCard.value,
                                          "effective-state": currentEffectiveState.value.code
                                        }, {
                                          default: _withCtx(() => [
                                            _createVNode(_sfc_main$d, {
                                              form: _unref(form),
                                              "primary-fields": seedCleanPrimaryCard.value?.fields || [],
                                              "filter-fields": seedCleanFilterCard.value?.fields || [],
                                              "notification-locked-by-fusion": _unref(notificationLockedByFusion),
                                              "effective-state": currentEffectiveState.value.code
                                            }, {
                                              operations: _withCtx(() => [
                                                (singlePageActionCard.value)
                                                  ? (_openBlock$1(), _createBlock$1(_unref(CompactActionRow), {
                                                      key: 0,
                                                      card: singlePageActionCard.value,
                                                      "effective-state": currentEffectiveState.value.code,
                                                      onRun: triggerConfigActionWithRefresh
                                                    }, null, 8, ["card", "effective-state"]))
                                                  : _createCommentVNode("", true)
                                              ]),
                                              _: 1
                                            }, 8, ["form", "primary-fields", "filter-fields", "notification-locked-by-fusion", "effective-state"])
                                          ]),
                                          _: 1
                                        }, 8, ["card", "effective-state"]))
                                      : (_unref(activeSub) === 'dltagmain')
                                        ? (_openBlock$1(), _createBlock$1(_sfc_main$r, {
                                            key: 10,
                                            card: singlePageCard.value,
                                            "effective-state": currentEffectiveState.value.code
                                          }, {
                                            default: _withCtx(() => [
                                              _createVNode(_sfc_main$b, {
                                                form: _unref(form),
                                                fields: downloaderHelperFields.value,
                                                "tracker-fields": downloaderTrackerCard.value?.fields || [],
                                                "notification-locked-by-fusion": _unref(notificationLockedByFusion),
                                                "effective-state": currentEffectiveState.value.code
                                              }, {
                                                operations: _withCtx(() => [
                                                  (singlePageActionCard.value)
                                                    ? (_openBlock$1(), _createBlock$1(_unref(CompactActionRow), {
                                                        key: 0,
                                                        card: singlePageActionCard.value,
                                                        "effective-state": currentEffectiveState.value.code,
                                                        onRun: triggerConfigActionWithRefresh
                                                      }, null, 8, ["card", "effective-state"]))
                                                    : _createCommentVNode("", true)
                                                ]),
                                                _: 1
                                              }, 8, ["form", "fields", "tracker-fields", "notification-locked-by-fusion", "effective-state"])
                                            ]),
                                            _: 1
                                          }, 8, ["card", "effective-state"]))
                                        : (_unref(activeSub) === 'logs')
                                          ? (_openBlock$1(), _createBlock$1(_sfc_main$r, {
                                              key: 11,
                                              card: singlePageCard.value,
                                              "effective-state": currentEffectiveState.value.code
                                            }, {
                                              default: _withCtx(() => [
                                                _createVNode(_sfc_main$e, {
                                                  form: _unref(form),
                                                  fields: logCleanFields.value,
                                                  "notification-locked-by-fusion": _unref(notificationLockedByFusion),
                                                  "effective-state": currentEffectiveState.value.code
                                                }, {
                                                  operations: _withCtx(() => [
                                                    (singlePageActionCard.value)
                                                      ? (_openBlock$1(), _createBlock$1(_unref(CompactActionRow), {
                                                          key: 0,
                                                          card: singlePageActionCard.value,
                                                          "effective-state": currentEffectiveState.value.code,
                                                          onRun: triggerConfigActionWithRefresh
                                                        }, null, 8, ["card", "effective-state"]))
                                                      : _createCommentVNode("", true)
                                                  ]),
                                                  _: 1
                                                }, 8, ["form", "fields", "notification-locked-by-fusion", "effective-state"])
                                              ]),
                                              _: 1
                                            }, 8, ["card", "effective-state"]))
                                          : _createCommentVNode("", true)
                ]),
                _: 1
              }, 8, ["layout", "active-category", "effective-state"])
            ])
          ], 64))
    ], 8, _hoisted_16),
    (configLoadReady.value && _unref(actionOperationSpec))
      ? (_openBlock$1(), _createBlock$1(ActionOperationPanel, _mergeProps({ key: 0 }, _unref(actionOperationSpec), {
          open: "",
          "theme-class": _unref(rootThemeClass),
          "portal-style": _unref(actionOperationPortalStyle),
          busy: _unref(actionOperationBusy),
          onCancel: _unref(cancelActionOperationPanel),
          onConfirm: _unref(confirmActionOperationPanel)
        }), null, 16, ["theme-class", "portal-style", "busy", "onCancel", "onConfirm"]))
      : _createCommentVNode("", true),
    _createElementVNode("footer", _hoisted_39, [
      _createElementVNode("div", _hoisted_40, [
        (configLoadReady.value && currentActionHint.value)
          ? (_openBlock$1(), _createElementBlock("span", _hoisted_41, _toDisplayString(currentActionHint.value), 1))
          : _createCommentVNode("", true),
        _createVNode(_Transition, { name: "aoa-fade" }, {
          default: _withCtx(() => [
            (_unref(saveFeedback).message || _unref(action).message)
              ? (_openBlock$1(), _createElementBlock("strong", {
                  key: 0,
                  class: _normalizeClass(["aoa-config-action-feedback aoa-feedback", {
                'aoa-config-action-feedback--ok': _unref(saveFeedback).message ? _unref(saveFeedback).ok : _unref(action).ok,
                'aoa-config-action-feedback--err': _unref(saveFeedback).message ? !_unref(saveFeedback).ok : !_unref(action).ok,
              }]),
                  "data-tone": (_unref(saveFeedback).message ? _unref(saveFeedback).ok : _unref(action).ok) ? 'success' : 'error',
                  role: "status",
                  "aria-live": "polite",
                  "aria-atomic": "true"
                }, _toDisplayString(_unref(saveFeedback).message || _unref(action).message), 11, _hoisted_42))
              : _createCommentVNode("", true)
          ]),
          _: 1
        })
      ]),
      _createElementVNode("div", _hoisted_43, [
        _createElementVNode("button", {
          type: "button",
          class: "aoa-config-btn aoa-config-btn--ghost",
          "data-config-cancel-button": "",
          onClick: _cache[10] || (_cache[10] = $event => (emit('close')))
        }, "取消"),
        _createElementVNode("button", {
          type: "button",
          class: "aoa-config-btn aoa-config-btn--save",
          "data-config-save-button": "",
          "data-dirty": String(_unref(isDirty)),
          disabled: _unref(saving) || configReadLocked.value,
          "aria-busy": _unref(saving) || configLoadBusy.value,
          onClick: saveCurrentPage
        }, [
          _createElementVNode("svg", {
            class: "aoa-mdi-icon aoa-mdi-icon--save",
            viewBox: "0 0 448 512",
            width: "11.375",
            height: "13",
            "aria-hidden": "true"
          }, [
            _createElementVNode("path", {
              d: faFloppyDiskPath,
              fill: "currentColor"
            })
          ]),
          _cache[17] || (_cache[17] = _createElementVNode("span", null, "保存配置", -1))
        ], 8, _hoisted_44)
      ])
    ])
  ], 10, _hoisted_1))
}
}

};

const {openBlock:_openBlock,createBlock:_createBlock} = await importShared('vue');


const {onMounted,ref,watch} = await importShared('vue');


const _sfc_main = {
  __name: 'AppPageConfig',
  props: {
  api: { type: [Object, Function], default: null },
  initialConfig: { type: Object, default: () => ({}) },
  pluginId: { type: String, default: 'Signal' },
  configRecordState: { type: String, default: null },
},
  emits: ['save', 'close', 'switch'],
  setup(__props, { emit: __emit }) {

const props = __props;

const emit = __emit;
const recordStates = new Set(['unknown', 'absent', 'present']);
const explicitRecordState = value => recordStates.has(value) ? value : null;
const canLoadConfig = () => typeof props.api?.get === 'function';
const loadedConfig = ref({ ...props.initialConfig });
const recordState = ref(explicitRecordState(props.configRecordState) || 'unknown');
const loadState = ref(canLoadConfig() ? 'loading' : 'ready');
const loadError = ref('');

watch(() => props.initialConfig, value => {
  loadedConfig.value = { ...(value || {}) };
}, { deep: true });

watch(() => props.configRecordState, value => {
  recordState.value = explicitRecordState(value) || 'unknown';
});

watch(() => props.api, api => {
  if (typeof api?.get === 'function') loadConfig();
});

async function loadConfig() {
  if (!canLoadConfig()) {
    loadError.value = '';
    loadState.value = 'ready';
    return
  }

  loadState.value = 'loading';
  loadError.value = '';
  if (!explicitRecordState(props.configRecordState)) recordState.value = 'unknown';
  try {
    const result = await props.api.get(`plugin/form/${props.pluginId}`);
    const model = result?.model ?? result?.data?.model;
    const hasConfigRecord = model !== null && typeof model === 'object' && !Array.isArray(model);
    const forcedState = explicitRecordState(props.configRecordState);
    if (hasConfigRecord) {
      loadedConfig.value = { ...model };
      if (!forcedState) recordState.value = 'present';
    } else if (!forcedState) {
      loadedConfig.value = {};
      recordState.value = 'absent';
    }
    loadState.value = 'ready';
  } catch (error) {
    if (!explicitRecordState(props.configRecordState)) recordState.value = 'unknown';
    loadError.value = String(error?.message || '').trim();
    loadState.value = 'error';
  }
}

onMounted(loadConfig);


return (_ctx, _cache) => {
  return (_openBlock(), _createBlock(_sfc_main$1, {
    api: __props.api,
    "initial-config": loadedConfig.value,
    "plugin-id": __props.pluginId,
    "config-record-state": recordState.value,
    "config-load-state": loadState.value,
    "config-load-error": loadError.value,
    onSave: _cache[0] || (_cache[0] = value => emit('save', value)),
    onClose: _cache[1] || (_cache[1] = $event => (emit('close'))),
    onSwitch: _cache[2] || (_cache[2] = $event => (emit('switch'))),
    onRetryLoad: loadConfig
  }, null, 8, ["api", "initial-config", "plugin-id", "config-record-state", "config-load-state", "config-load-error"]))
}
}

};

export { _sfc_main as default };
