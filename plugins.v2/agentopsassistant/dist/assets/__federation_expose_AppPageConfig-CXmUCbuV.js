import { importShared } from './__federation_fn_import-JrT3xvdd.js';
import { am as _export_sfc, c7 as mdiChevronDown, bB as mdiCogOutline, bI as mdiClose, c4 as mdiAlertOutline, aX as mdiPlay, bu as mdiDeleteOutline, ao as mdiWeight, aC as mdiSignal, aF as mdiShieldHalfFull, aK as mdiSendOutline, aY as mdiPercent, aZ as mdiPencilOutline, b7 as mdiLayersOutline, c3 as mdiAlphaMBoxOutline, c5 as mdiAlertCircleOutline, ba as mdiHeartPulse, ax as mdiTelevision, bS as mdiCardAccountDetailsOutline, b$ as mdiBackupRestore, b9 as mdiHistory, aS as mdiPuzzleOutline, aU as mdiPuzzle, bs as mdiDownload, bX as mdiBellOutline, b_ as mdiBell, aG as mdiShieldCheckOutline, c8 as mdiEyeOutline, aW as mdiPlusCircleOutline, by as mdiCubeOutline, bC as mdiCodeTags, bv as mdiDatabaseOutline, bD as mdiCloudUploadOutline, aE as mdiShieldOutline, bp as mdiDownloadOutline, aB as mdiSync, bU as mdiBroom, aO as mdiRocketLaunchOutline, bh as mdiFolderOutline, b3 as mdiLockCheckOutline, bA as mdiContentCopy, c6 as mdiAccountOutline, ap as mdiWeb, bH as mdiCloudOutline, b2 as mdiLockOutline, b4 as mdiLinkVariant, az as mdiTagOutline, au as mdiTimerOutline, aL as mdiScaleBalance, bl as mdiFilterOutline, bb as mdiHarddisk, bc as mdiGauge, bQ as mdiChartBar, a$ as mdiMovieOpenOutline, be as mdiFormatListChecks, aJ as mdiServer, bo as mdiEmailOutline, bd as mdiFormatListNumbered, bT as mdiCalendarClock, aV as mdiPowerStandby, as as mdiUpdate, bn as mdiFileDocumentRemoveOutline, c2 as mdiArchiveArrowUpOutline, c0 as mdiAutoFix, aA as mdiTagMultipleOutline, bt as mdiDeleteSweepOutline, bW as mdiBellRingOutline, aw as mdiTelevisionPlay, aQ as mdiPuzzleRemoveOutline, bq as mdiDownloadNetworkOutline, bP as mdiChartLine, b1 as mdiMessageBadgeOutline } from './mdi-CTgwQT0_.js';
import { c as configSchemaFields, n as normalizeCurrentConfig, e as emitConfigSave } from './save-payload-CuYtvZ2o.js';
import { p as postPluginApi, g as getPluginApi, u as useAgentOpsTheme, a as useActionRunner } from './useAgentOpsTheme-CbGFlsGV.js';

const {createElementVNode:_createElementVNode$6,normalizeClass:_normalizeClass$6,openBlock:_openBlock$8,createElementBlock:_createElementBlock$6,createCommentVNode:_createCommentVNode$6,resolveComponent:_resolveComponent$4,mergeProps:_mergeProps$1,createBlock:_createBlock$7,toDisplayString:_toDisplayString$6,createTextVNode:_createTextVNode$2,withCtx:_withCtx$3,createVNode:_createVNode$5,createSlots:_createSlots} = await importShared('vue');


const _hoisted_1$6 = ["data-control-kind", "data-switch-enabled", "data-multi-select"];
const _hoisted_2$6 = ["aria-checked", "aria-label", "disabled"];
const _hoisted_3$6 = {
  key: 0,
  class: "aoa-field-control__selection-count"
};
const _hoisted_4$5 = {
  key: 0,
  class: "aoa-field-control__selection-count"
};

const {computed: computed$6} = await importShared('vue');



const _sfc_main$8 = {
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

const normalizedValue = computed$6({
  get: () => props.modelValue,
  set: next => emitValue(next),
});

const control = computed$6(() => props.field.control || 'text');
const selectionCount = computed$6(() => Array.isArray(normalizedValue.value) ? normalizedValue.value.length : 0);
const selectionSummary = computed$6(() => (
  selectionCount.value === 0 && props.field.emptySelectionText
    ? props.field.emptySelectionText
    : `已选 ${selectionCount.value} 项`
));
const commonProps = computed$6(() => ({
  label: undefined,
  hint: '',
  persistentHint: false,
  disabled: !!props.field.disabled,
  density: props.field.density || 'comfortable',
  hideDetails: props.field.hideDetails ?? false,
  errorMessages: props.field.error ? [props.field.error] : [],
  'aria-label': props.field.ariaLabel || props.field.label || props.field.key,
  'aria-describedby': props.field.ariaDescribedby || undefined,
}));

function selectionTitle(item) {
  return item?.raw?.title ?? item?.raw?.label ?? item?.raw?.name ?? item?.title ?? item?.label ?? item?.name ?? item?.props?.title ?? item?.value ?? item?.key ?? item?.id ?? item
}

function selectionValue(item) {
  return item?.raw?.value ?? item?.raw?.key ?? item?.raw?.id ?? item?.value ?? item?.key ?? item?.id ?? item
}

return (_ctx, _cache) => {
  const _component_VCronField = _resolveComponent$4("VCronField");
  const _component_VChip = _resolveComponent$4("VChip");
  const _component_VSelect = _resolveComponent$4("VSelect");
  const _component_VCombobox = _resolveComponent$4("VCombobox");
  const _component_VTextarea = _resolveComponent$4("VTextarea");
  const _component_VTextField = _resolveComponent$4("VTextField");

  return (_openBlock$8(), _createElementBlock$6("div", {
    class: _normalizeClass$6(["aoa-field-control", {
      'aoa-field-control--switch': control.value === 'switch',
      'aoa-field-control--switch-on': control.value === 'switch' && !!normalizedValue.value,
      'aoa-field-control--multi': !!(__props.field.multiple || __props.field.chips || control.value === 'combobox'),
      'aoa-field-control--full': !!(__props.field.fullRow || __props.field.multiple || __props.field.chips || control.value === 'combobox' || control.value === 'textarea'),
    }]),
    "data-field-control": "",
    "data-control-kind": control.value,
    "data-switch-enabled": control.value === 'switch' ? (!!normalizedValue.value ? 'true' : 'false') : undefined,
    "data-multi-select": !!(__props.field.multiple || __props.field.chips || control.value === 'combobox') ? 'true' : undefined
  }, [
    (control.value === 'switch')
      ? (_openBlock$8(), _createElementBlock$6("button", {
          key: 0,
          type: "button",
          class: _normalizeClass$6(["aoa-toggle-switch", {
        'aoa-toggle-switch--on': !!normalizedValue.value,
        'aoa-toggle-switch--disabled': !!__props.field.disabled,
      }]),
          role: "switch",
          "aria-checked": !!normalizedValue.value,
          "aria-label": __props.field.ariaLabel || __props.field.label || __props.field.key,
          disabled: !!__props.field.disabled,
          "data-field-switch": "",
          onClick: _cache[0] || (_cache[0] = $event => (normalizedValue.value = !normalizedValue.value))
        }, [...(_cache[6] || (_cache[6] = [
          _createElementVNode$6("span", {
            class: "aoa-toggle-switch__thumb",
            "aria-hidden": "true"
          }, null, -1)
        ]))], 10, _hoisted_2$6))
      : (control.value === 'cron')
        ? (_openBlock$8(), _createBlock$7(_component_VCronField, _mergeProps$1({
            key: 1,
            modelValue: normalizedValue.value,
            "onUpdate:modelValue": _cache[1] || (_cache[1] = $event => ((normalizedValue).value = $event))
          }, commonProps.value, {
            placeholder: __props.field.placeholder || undefined
          }), null, 16, ["modelValue", "placeholder"]))
        : (control.value === 'select')
          ? (_openBlock$8(), _createBlock$7(_component_VSelect, _mergeProps$1({
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
              "prepend-inner-icon": __props.field.icon || undefined,
              placeholder: __props.field.compactSelection ? selectionSummary.value : (__props.field.placeholder || undefined)
            }), _createSlots({ _: 2 }, [
              (__props.field.compactSelection)
                ? {
                    name: "selection",
                    fn: _withCtx$3(({ index }) => [
                      (index === 0)
                        ? (_openBlock$8(), _createElementBlock$6("span", _hoisted_3$6, _toDisplayString$6(selectionSummary.value), 1))
                        : _createCommentVNode$6("", true)
                    ]),
                    key: "0"
                  }
                : (__props.field.multiple || __props.field.chips)
                  ? {
                      name: "chip",
                      fn: _withCtx$3(({ item, props: chipProps }) => [
                        _createVNode$5(_component_VChip, _mergeProps$1(chipProps, {
                          class: "aoa-field-control__chip",
                          variant: "tonal"
                        }), {
                          default: _withCtx$3(() => [
                            _createTextVNode$2(_toDisplayString$6(selectionTitle(item)), 1)
                          ]),
                          _: 2
                        }, 1040)
                      ]),
                      key: "1"
                    }
                  : undefined
            ]), 1040, ["modelValue", "items", "loading", "multiple", "chips", "closable-chips", "clearable", "prepend-inner-icon", "placeholder"]))
          : (control.value === 'combobox')
            ? (_openBlock$8(), _createBlock$7(_component_VCombobox, _mergeProps$1({
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
                "prepend-inner-icon": __props.field.icon || undefined,
                placeholder: __props.field.compactSelection ? selectionSummary.value : (__props.field.placeholder || '输入后按回车添加')
              }), _createSlots({ _: 2 }, [
                (__props.field.compactSelection)
                  ? {
                      name: "selection",
                      fn: _withCtx$3(({ index }) => [
                        (index === 0)
                          ? (_openBlock$8(), _createElementBlock$6("span", _hoisted_4$5, _toDisplayString$6(selectionSummary.value), 1))
                          : _createCommentVNode$6("", true)
                      ]),
                      key: "0"
                    }
                  : {
                      name: "chip",
                      fn: _withCtx$3(({ item, props: chipProps }) => [
                        _createVNode$5(_component_VChip, _mergeProps$1(chipProps, {
                          class: "aoa-field-control__chip",
                          variant: "tonal"
                        }), {
                          default: _withCtx$3(() => [
                            _createTextVNode$2(_toDisplayString$6(selectionTitle(item)), 1)
                          ]),
                          _: 2
                        }, 1040)
                      ]),
                      key: "1"
                    }
              ]), 1040, ["modelValue", "items", "multiple", "chips", "closable-chips", "clearable", "prepend-inner-icon", "placeholder"]))
            : (control.value === 'textarea')
              ? (_openBlock$8(), _createBlock$7(_component_VTextarea, _mergeProps$1({
                  key: 4,
                  modelValue: normalizedValue.value,
                  "onUpdate:modelValue": _cache[4] || (_cache[4] = $event => ((normalizedValue).value = $event))
                }, commonProps.value, {
                  placeholder: __props.field.placeholder || undefined,
                  "prepend-inner-icon": __props.field.icon || undefined,
                  rows: __props.field.rows || 3,
                  "auto-grow": ""
                }), null, 16, ["modelValue", "placeholder", "prepend-inner-icon", "rows"]))
              : (_openBlock$8(), _createBlock$7(_component_VTextField, _mergeProps$1({
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
  ], 10, _hoisted_1$6))
}
}

};
const FieldControl = /*#__PURE__*/_export_sfc(_sfc_main$8, [['__scopeId',"data-v-f885ed00"]]);

const {resolveComponent:_resolveComponent$3,openBlock:_openBlock$7,createBlock:_createBlock$6,createCommentVNode:_createCommentVNode$5,toDisplayString:_toDisplayString$5,createTextVNode:_createTextVNode$1,Fragment:_Fragment$5,createElementBlock:_createElementBlock$5,createElementVNode:_createElementVNode$5,createVNode:_createVNode$4,normalizeClass:_normalizeClass$5} = await importShared('vue');


const _hoisted_1$5 = ["data-field-key", "data-field-control", "data-control-kind", "data-switch-row", "data-full-row", "data-multi-select-row", "data-has-control-hint", "aria-disabled"];
const _hoisted_2$5 = { class: "aoa-field-row__label" };
const _hoisted_3$5 = {
  key: 1,
  class: "aoa-field-row__hint"
};
const _hoisted_4$4 = {
  key: 2,
  class: "aoa-field-row__error"
};
const _hoisted_5$4 = { class: "aoa-field-row__control" };
const _hoisted_6$4 = ["id"];

const {computed: computed$5} = await importShared('vue');


const _sfc_main$7 = {
  __name: 'FieldRow',
  props: {
  field: { type: Object, required: true },
  modelValue: { type: null, default: null },
},
  emits: ['update:modelValue'],
  setup(__props) {

const props = __props;



const rowSpan = computed$5(() => props.field.width || props.field.span || 'normal');
const control = computed$5(() => props.field.control || 'text');
const isSwitch = computed$5(() => control.value === 'switch');
const isMulti = computed$5(() => !!(props.field.multiple || props.field.chips || control.value === 'combobox'));
const isCompactMulti = computed$5(() => !!(props.field.compactMulti && isMulti.value));
const isFullRow = computed$5(() => !!(props.field.fullRow || (isMulti.value && !isCompactMulti.value) || control.value === 'textarea'));
const controlHint = computed$5(() => String(props.field.controlHint || '').trim());
const controlHintId = computed$5(() => controlHint.value
  ? `aoa-field-control-hint-${String(props.field.key || 'field').replace(/[^a-zA-Z0-9_-]/g, '-')}`
  : undefined);
const controlField = computed$5(() => ({
  ...props.field,
  icon: undefined,
  label: '',
  hint: '',
  hideDetails: true,
  ariaLabel: props.field.ariaLabel || props.field.label || props.field.key,
  ariaDescribedby: controlHintId.value,
}));
const rowClasses = computed$5(() => ({
  'aoa-field-row--wide': rowSpan.value === 'wide' || rowSpan.value === 6 || rowSpan.value === '6',
  'aoa-field-row--full': rowSpan.value === 'full' || rowSpan.value === 12 || rowSpan.value === '12',
  'aoa-field-row--disabled': !!props.field.disabled,
  'aoa-field-row--error': !!props.field.error,
  'aoa-field-row--switch': isSwitch.value,
  'aoa-field-row--switch-on': isSwitch.value && !!props.modelValue,
  'aoa-field-row--multi': isMulti.value && !isCompactMulti.value,
  'aoa-field-row--compact-multi': isCompactMulti.value,
  'aoa-field-row--control-full': isFullRow.value,
  'aoa-field-row--with-control-hint': !!controlHint.value,
  'aoa-design-field--disabled': !!props.field.disabled,
  'aoa-design-field--switch': isSwitch.value,
  'aoa-design-field--switch-on': isSwitch.value && !!props.modelValue,
  'aoa-design-field--multi': isMulti.value,
  'aoa-design-field--full': isFullRow.value,
}));

return (_ctx, _cache) => {
  const _component_VIcon = _resolveComponent$3("VIcon");

  return (_openBlock$7(), _createElementBlock$5("div", {
    class: _normalizeClass$5(["aoa-field-row aoa-design-field", [`aoa-field-row--${__props.field.control || 'text'}`, rowClasses.value]]),
    "data-field-row": "",
    "data-html-field": "",
    "data-field-key": __props.field.key,
    "data-field-control": __props.field.control || 'text',
    "data-control-kind": __props.field.control || 'text',
    "data-switch-row": isSwitch.value ? 'true' : undefined,
    "data-full-row": isFullRow.value ? 'true' : undefined,
    "data-multi-select-row": isMulti.value ? 'true' : undefined,
    "data-has-control-hint": controlHint.value ? 'true' : undefined,
    "aria-disabled": __props.field.disabled ? 'true' : 'false'
  }, [
    _createElementVNode$5("div", _hoisted_2$5, [
      (__props.field.icon)
        ? (_openBlock$7(), _createBlock$6(_component_VIcon, {
            key: 0,
            class: "aoa-field-row__icon",
            icon: __props.field.icon,
            size: "16",
            "aria-hidden": "true"
          }, null, 8, ["icon"]))
        : _createCommentVNode$5("", true),
      _createElementVNode$5("span", null, [
        _createTextVNode$1(_toDisplayString$5(__props.field.label), 1),
        (__props.field.compactSelection)
          ? (_openBlock$7(), _createElementBlock$5(_Fragment$5, { key: 0 }, [
              _createTextVNode$1("：")
            ], 64))
          : _createCommentVNode$5("", true)
      ]),
      (__props.field.hint)
        ? (_openBlock$7(), _createElementBlock$5("small", _hoisted_3$5, _toDisplayString$5(__props.field.hint), 1))
        : _createCommentVNode$5("", true),
      (__props.field.error)
        ? (_openBlock$7(), _createElementBlock$5("small", _hoisted_4$4, _toDisplayString$5(__props.field.error), 1))
        : _createCommentVNode$5("", true)
    ]),
    _createElementVNode$5("div", _hoisted_5$4, [
      _createVNode$4(FieldControl, {
        field: controlField.value,
        "model-value": __props.modelValue,
        "onUpdate:modelValue": _cache[0] || (_cache[0] = value => _ctx.$emit('update:modelValue', value))
      }, null, 8, ["field", "model-value"]),
      (controlHint.value)
        ? (_openBlock$7(), _createElementBlock$5("small", {
            key: 0,
            id: controlHintId.value,
            class: "aoa-field-row__control-hint",
            "data-field-control-hint": ""
          }, _toDisplayString$5(controlHint.value), 9, _hoisted_6$4))
        : _createCommentVNode$5("", true)
    ])
  ], 10, _hoisted_1$5))
}
}

};
const FieldRow = /*#__PURE__*/_export_sfc(_sfc_main$7, [['__scopeId',"data-v-0c93f851"]]);

const {openBlock:_openBlock$6,createBlock:_createBlock$5} = await importShared('vue');


const _sfc_main$6 = {
  __name: 'ConfigFieldRow',
  props: {
  field: { type: Object, required: true },
  modelValue: { type: null, default: null },
},
  emits: ['update:modelValue'],
  setup(__props) {





return (_ctx, _cache) => {
  return (_openBlock$6(), _createBlock$5(FieldRow, {
    class: "aoa-config-field-row",
    "data-config-field-row": "",
    field: __props.field,
    "model-value": __props.modelValue,
    "onUpdate:modelValue": _cache[0] || (_cache[0] = value => _ctx.$emit('update:modelValue', value))
  }, null, 8, ["field", "model-value"]))
}
}

};
const ConfigFieldRow = /*#__PURE__*/_export_sfc(_sfc_main$6, [['__scopeId',"data-v-dccacf01"]]);

const {resolveComponent:_resolveComponent$2,createVNode:_createVNode$3,createElementVNode:_createElementVNode$4,toDisplayString:_toDisplayString$4,openBlock:_openBlock$5,createElementBlock:_createElementBlock$4,createCommentVNode:_createCommentVNode$4,renderSlot:_renderSlot,renderList:_renderList$4,Fragment:_Fragment$4,createBlock:_createBlock$4,normalizeClass:_normalizeClass$4} = await importShared('vue');


const _hoisted_1$4 = ["data-html-replica-card", "data-flat-config-section", "data-cron-card", "data-schedule-card", "data-notify-card", "data-generic-card", "data-feature-card"];
const _hoisted_2$4 = {
  key: 0,
  class: "aoa-config-card__head"
};
const _hoisted_3$4 = { class: "aoa-config-card__icon" };
const _hoisted_4$3 = { class: "aoa-config-card__copy" };
const _hoisted_5$3 = { key: 0 };
const _hoisted_6$3 = { class: "aoa-config-card__trailing" };
const _hoisted_7$3 = {
  key: 1,
  class: "aoa-config-card__fields"
};


const _sfc_main$5 = {
  __name: 'ConfigCardBase',
  props: {
  title: { type: String, required: true },
  note: { type: String, default: '' },
  icon: { type: String, default: 'mdi-tune-variant' },
  fields: { type: Array, default: () => [] },
  values: { type: Object, required: true },
  cardType: { type: String, default: 'generic' },
  marker: { type: String, default: '' },
  disabled: { type: Boolean, default: false },
  locked: { type: Boolean, default: false },
  embedded: { type: Boolean, default: false },
},
  emits: ['field-update'],
  setup(__props, { emit: __emit }) {

const props = __props;

const emit = __emit;

function updateField(field, value) {
  if (!field?.key) return
  props.values[field.key] = value;
  emit('field-update', { field, value });
}

return (_ctx, _cache) => {
  const _component_VIcon = _resolveComponent$2("VIcon");

  return (_openBlock$5(), _createElementBlock$4("section", {
    class: _normalizeClass$4(["aoa-config-card aoa-design-section-card", [`aoa-config-card--${__props.cardType}`, { 'aoa-config-card--locked': __props.locked, 'aoa-config-card--disabled': __props.disabled, 'aoa-config-card--embedded': __props.embedded }]]),
    "data-html-replica-card": __props.embedded ? null : '',
    "data-flat-config-section": __props.embedded ? '' : null,
    "data-section-tone": "neutral",
    "data-cron-card": __props.marker === 'cron' || __props.marker === 'schedule' ? '' : null,
    "data-schedule-card": __props.marker === 'schedule' ? '' : null,
    "data-notify-card": __props.marker === 'notify' ? '' : null,
    "data-generic-card": __props.marker === 'generic' ? '' : null,
    "data-feature-card": __props.marker === 'feature' ? '' : null
  }, [
    (!__props.embedded)
      ? (_openBlock$5(), _createElementBlock$4("header", _hoisted_2$4, [
          _createElementVNode$4("span", _hoisted_3$4, [
            _createVNode$3(_component_VIcon, {
              icon: __props.icon,
              size: "20"
            }, null, 8, ["icon"])
          ]),
          _createElementVNode$4("div", _hoisted_4$3, [
            _createElementVNode$4("h3", null, _toDisplayString$4(__props.title), 1),
            (__props.note)
              ? (_openBlock$5(), _createElementBlock$4("p", _hoisted_5$3, _toDisplayString$4(__props.note), 1))
              : _createCommentVNode$4("", true)
          ]),
          _createElementVNode$4("span", _hoisted_6$3, [
            _renderSlot(_ctx.$slots, "actions", {}, undefined, true)
          ])
        ]))
      : _createCommentVNode$4("", true),
    (__props.fields.length)
      ? (_openBlock$5(), _createElementBlock$4("div", _hoisted_7$3, [
          (_openBlock$5(true), _createElementBlock$4(_Fragment$4, null, _renderList$4(__props.fields, (field) => {
            return (_openBlock$5(), _createBlock$4(ConfigFieldRow, {
              key: field.key,
              field: { ...field, disabled: __props.disabled || __props.locked || field.disabled },
              "model-value": __props.values[field.key],
              "onUpdate:modelValue": value => updateField(field, value)
            }, null, 8, ["field", "model-value", "onUpdate:modelValue"]))
          }), 128))
        ]))
      : _createCommentVNode$4("", true),
    _renderSlot(_ctx.$slots, "default", {}, undefined, true)
  ], 10, _hoisted_1$4))
}
}

};
const ConfigCardBase = /*#__PURE__*/_export_sfc(_sfc_main$5, [['__scopeId',"data-v-23683d0f"]]);

const {resolveComponent:_resolveComponent$1,createVNode:_createVNode$2,toDisplayString:_toDisplayString$3,createElementVNode:_createElementVNode$3,normalizeClass:_normalizeClass$3,renderList:_renderList$3,Fragment:_Fragment$3,openBlock:_openBlock$4,createElementBlock:_createElementBlock$3,createBlock:_createBlock$3,createCommentVNode:_createCommentVNode$3,withCtx:_withCtx$2} = await importShared('vue');


const _hoisted_1$3 = ["data-schedule-master-key", "data-schedule-key", "data-schedule-enabled"];
const _hoisted_2$3 = {
  key: 0,
  class: "aoa-schedule-card__group",
  "data-schedule-cron": ""
};
const _hoisted_3$3 = { class: "aoa-design-field-grid aoa-design-field-grid--grid-2" };

const {computed: computed$4} = await importShared('vue');


const _sfc_main$4 = {
  __name: 'ScheduleCard',
  props: {
  title: { type: String, required: true },
  note: { type: String, default: '' },
  icon: { type: String, default: 'mdi-calendar-clock' },
  fields: { type: Array, default: () => [] },
  values: { type: Object, required: true },
  disabled: { type: Boolean, default: false },
  locked: { type: Boolean, default: false },
  masterKey: { type: String, default: '' },
  scheduleKey: { type: String, default: '' },
  effectiveState: { type: String, default: '' },
  embedded: { type: Boolean, default: false },
},
  emits: ['field-update'],
  setup(__props, { emit: __emit }) {

const props = __props;

const emit = __emit;

const moduleEnabled = computed$4(() => (
  props.masterKey ? props.values[props.masterKey] !== false : true
));
const scheduleEnabled = computed$4(() => (
  props.scheduleKey ? props.values[props.scheduleKey] !== false : moduleEnabled.value
));
const cronFields = computed$4(() => props.fields.filter(field => (
  field.control === 'cron' || field.key.endsWith('_cron')
)));
const statusLabel = computed$4(() => {
  if (props.effectiveState === 'plugin_disabled') return '已停用'
  if (props.locked) return '计划已接管'
  if (props.disabled) return '当前不可编辑'
  if (!moduleEnabled.value) return '模块未启用'
  if (!scheduleEnabled.value) return '定时未启用'
  return 'Cron 已启用'
});
const statusActive = computed$4(() => (
  props.effectiveState !== 'plugin_disabled' && !props.disabled && !props.locked && moduleEnabled.value && scheduleEnabled.value
));

function withScheduleState(field) {
  return {
    ...field,
    disabled: props.disabled || props.locked || !moduleEnabled.value || !scheduleEnabled.value || field.disabled,
  }
}

function updateField(field, value) {
  if (!field?.key) return
  props.values[field.key] = value;
  emit('field-update', { field, value });
}

return (_ctx, _cache) => {
  const _component_VIcon = _resolveComponent$1("VIcon");

  return (_openBlock$4(), _createBlock$3(ConfigCardBase, {
    title: __props.title,
    note: __props.note,
    icon: __props.icon,
    values: __props.values,
    fields: [],
    disabled: __props.disabled,
    locked: __props.locked,
    "card-type": "schedule",
    marker: "schedule",
    "data-contract-marker": "data-schedule-card",
    "data-effective-state": __props.effectiveState || undefined,
    embedded: __props.embedded
  }, {
    actions: _withCtx$2(() => [
      _createElementVNode$3("span", {
        class: _normalizeClass$3(["aoa-schedule-card__status", { 'aoa-schedule-card__status--off': !statusActive.value }]),
        "data-schedule-status": "",
        role: "status"
      }, [
        _createVNode$2(_component_VIcon, {
          icon: statusActive.value ? 'mdi-check-circle-outline' : 'mdi-alert-outline',
          size: "16"
        }, null, 8, ["icon"]),
        _createElementVNode$3("span", null, _toDisplayString$3(statusLabel.value), 1)
      ], 2)
    ]),
    default: _withCtx$2(() => [
      _createElementVNode$3("div", {
        class: "aoa-schedule-card",
        "data-schedule-card-body": "",
        "data-schedule-master-key": __props.masterKey || undefined,
        "data-schedule-key": __props.scheduleKey || undefined,
        "data-schedule-enabled": scheduleEnabled.value ? 'true' : 'false'
      }, [
        (cronFields.value.length)
          ? (_openBlock$4(), _createElementBlock$3("section", _hoisted_2$3, [
              _createElementVNode$3("div", _hoisted_3$3, [
                (_openBlock$4(true), _createElementBlock$3(_Fragment$3, null, _renderList$3(cronFields.value, (field) => {
                  return (_openBlock$4(), _createBlock$3(ConfigFieldRow, {
                    key: field.key,
                    field: withScheduleState(field),
                    "model-value": __props.values[field.key],
                    "onUpdate:modelValue": value => updateField(field, value)
                  }, null, 8, ["field", "model-value", "onUpdate:modelValue"]))
                }), 128))
              ])
            ]))
          : _createCommentVNode$3("", true)
      ], 8, _hoisted_1$3)
    ]),
    _: 1
  }, 8, ["title", "note", "icon", "values", "disabled", "locked", "data-effective-state", "embedded"]))
}
}

};
const ScheduleCard = /*#__PURE__*/_export_sfc(_sfc_main$4, [['__scopeId',"data-v-59481b8a"]]);

const schemaByKey = new Map(configSchemaFields.map(field => [field.key, field]));

const auditedCompactSelectionFieldKeys = Object.freeze([
  'health_check_database_targets',
  'health_check_directory_targets',
  'health_check_items',
  'health_check_storage_targets',
  'log_clean_selected_ids',
  'market_update_exclude_ids',
  'market_update_install_ids',
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

const compactSelectionEmptyText = Object.freeze({
  seedclean_downloaders: '全部可用',
  dltag_downloaders: '全部可用',
});

const replicaFieldVisibilityDependencies = Object.freeze({
  backup_notify_type: Object.freeze({ key: 'backup_notify', value: true }),
  log_clean_notify_type: Object.freeze({ key: 'log_clean_notify', value: true }),
  seedclean_notify_type: Object.freeze({ key: 'seedclean_notify', value: true }),
  update_notify_type: Object.freeze({ key: 'update_scheduled_notify', value: true }),
  dltag_notify_type: Object.freeze({ key: 'dltag_scheduled_notify', value: true }),
  dltag_source_delete_strategy: Object.freeze({ key: 'dltag_listen_source_file', value: true }),
  market_update_install_ids: Object.freeze({ key: 'market_update_strategy', value: 'install' }),
  market_update_exclude_ids: Object.freeze({ key: 'market_update_strategy', value: 'install' }),
});

function isReplicaFieldVisible(field, values = {}) {
  if (!field || field.hidden) return false
  const dependency = replicaFieldVisibilityDependencies[field.key];
  if (!dependency) return true
  return values[dependency.key] === dependency.value
}

// Hero / subtab masters own the authority switches.  Schedule enable flags stay
// persisted and still inherit from the master toggle, but must not reappear as a
// second visible switch inside notify/schedule cards.
const heroManagedReplicaFieldKeys = Object.freeze({
  fusion: Object.freeze(['fusion_notify_enabled']),
  server: Object.freeze(['msgnotify_enabled']),
  subscribe: Object.freeze(['subscribe_reminder_enabled', 'subscribe_reminder_schedule_enabled']),
  sites: Object.freeze(['site_stat_enabled', 'site_stat_schedule_enabled']),
  hc: Object.freeze(['health_check_enabled', 'health_check_schedule_enabled']),
  seedremove: Object.freeze(['seedclean_enabled', 'seedclean_schedule_enabled']),
  dltagmain: Object.freeze(['dltag_enabled']),
  subfill: Object.freeze(['subfill_enabled']),
  backup: Object.freeze(['backup_enabled']),
  logs: Object.freeze(['log_clean_enabled', 'log_clean_schedule_enabled']),
  updates: Object.freeze([
    'mp_update_enabled',
    'mp_update_schedule_enabled',
    'market_update_enabled',
    'market_update_schedule_enabled',
  ]),
});

const shellManagedReplicaFieldKeys = Object.freeze(['enabled']);
const actionManagedReplicaFieldKeys = Object.freeze([]);

const sharedCardOwnership = Object.freeze({
  fusion: Object.freeze({
    schedule: Object.freeze({ title: '刷新计划', note: '使用 Cron 控制活动卡片的数据刷新频率。', masterKey: 'fusion_notify_enabled' }),
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
    notify: Object.freeze({ title: '站点统计通知', note: '定时统计完成后通过所选 MoviePilot 通知类型发送。', masterKey: 'site_stat_enabled', fusionManaged: true, fusionChannelOnly: true }),
  }),
  hc: Object.freeze({
    schedule: Object.freeze({ title: '健康巡检计划', note: '按 Cron 定时巡查数据库、存储和目录。', masterKey: 'health_check_enabled', scheduleKey: 'health_check_schedule_enabled' }),
    notify: Object.freeze({ title: '巡检异常通知', note: '设置健康巡检异常的投递类型。', masterKey: 'health_check_enabled', fusionManaged: true, fusionChannelOnly: true }),
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
  updates: Object.freeze({
    schedule: Object.freeze({ title: '更新检查计划', note: '分别设置 MoviePilot 系统更新和插件库更新的 Cron。' }),
    notify: Object.freeze({ title: '定时执行通知', note: '系统更新和插件库更新共用一套 Cron 执行结果通知。', resultKey: 'update_scheduled_notify', fusionManaged: true, fusionChannelOnly: true, dependencies: Object.freeze({ update_notify_type: 'update_scheduled_notify' }) }),
  }),
});

function schemaFieldPresentation(field) {
  const isArray = field.type === 'array' || field.dataType === 'array';
  return {
    key: field.key,
    cardType: field.cardType || 'feature',
    icon: field.cardType === 'notify' ? 'mdi-bell-outline' : (field.cardType === 'cron' ? 'mdi-calendar-clock' : 'mdi-cog-outline'),
    label: field.label || field.key,
    sensitive: /(?:password|token|secret)/i.test(field.key),
    multiple: isArray,
    chips: isArray,
    fullRow: isArray,
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
    .flatMap(card => card.fields || [])
    .map(field => field?.key)
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
  // A long option list does not make a single-select control multi-line. Only
  // values that can themselves expand need the full-row layout.
  const fullRow = !!(field.fullRow || isArray || control === 'textarea');
  return {
    ...field,
    cardType: schema.cardType || field.cardType || 'feature',
    control,
    items,
    multiple: isArray,
    chips: isArray,
    closableChips: isArray,
    compactSelection: auditedCompactSelectionFieldKeySet.has(key),
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
    const isSharedScheduleField = field => field.cardType === 'cron' && !field.retainInCard;
    const isSharedNotifyField = field => field.cardType === 'notify' && !field.retainInCard;
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
      const groupedFields = notifyFields.filter(field => {
        const module = schemaByKey.get(field.key)?.module || '';
        const matches = !notifyOwner.module || notifyOwner.module === module;
        if (matches) claimedNotifyKeys.add(field.key);
        return matches
      });
      if (groupedFields.length) composed.push(sharedCard('notify', groupedFields, notifyOwner));
    }
    const unclaimedNotifyFields = notifyFields.filter(field => !claimedNotifyKeys.has(field.key));
    if (unclaimedNotifyFields.length) composed.push(sharedCard('notify', unclaimedNotifyFields, ownership.notify));
    composed.push(...actions);
    return [subtab, composed]
  }))
}

function updateReplicaFieldValue(form, field, value) {
  if (!field?.key) throw new Error('Replica field update requires a backend config key')
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

const {resolveComponent:_resolveComponent,createVNode:_createVNode$1,toDisplayString:_toDisplayString$2,createElementVNode:_createElementVNode$2,normalizeClass:_normalizeClass$2,openBlock:_openBlock$3,createElementBlock:_createElementBlock$2,createCommentVNode:_createCommentVNode$2,renderList:_renderList$2,Fragment:_Fragment$2,createBlock:_createBlock$2,withCtx:_withCtx$1} = await importShared('vue');


const _hoisted_1$2 = ["data-notify-master-key", "data-notify-result-key", "data-notify-result-keys", "data-notify-enabled"];
const _hoisted_2$2 = {
  key: 0,
  class: "aoa-notify-card__lock",
  "data-notify-fusion-lock": "",
  role: "status"
};
const _hoisted_3$2 = {
  key: 1,
  class: "aoa-notify-card__lane aoa-notify-card__lane--master",
  "data-notify-master": ""
};
const _hoisted_4$2 = {
  key: 2,
  class: "aoa-notify-card__lane aoa-notify-card__lane--channel",
  "data-notify-channel": ""
};
const _hoisted_5$2 = {
  key: 3,
  class: "aoa-notify-card__lane aoa-notify-card__lane--mode",
  "data-notify-mode": ""
};
const _hoisted_6$2 = {
  key: 4,
  class: "aoa-notify-card__lane aoa-notify-card__lane--rule",
  "data-notify-rule": ""
};
const _hoisted_7$2 = {
  key: 5,
  class: "aoa-notify-card__lane aoa-notify-card__lane--detail",
  "data-notify-detail": ""
};

const {computed: computed$3} = await importShared('vue');


const _sfc_main$3 = {
  __name: 'NotifyCard',
  props: {
  title: { type: String, required: true },
  note: { type: String, default: '' },
  icon: { type: String, default: 'mdi-bell-outline' },
  fields: { type: Array, default: () => [] },
  values: { type: Object, required: true },
  disabled: { type: Boolean, default: false },
  locked: { type: Boolean, default: false },
  channelOnlyLock: { type: Boolean, default: false },
  masterKey: { type: String, default: '' },
  resultKey: { type: String, default: '' },
  resultKeys: { type: Array, default: () => [] },
  dependencies: { type: Object, default: () => ({}) },
  offValues: { type: Array, default: () => ['none', 'off', ''] },
  effectiveState: { type: String, default: '' },
  embedded: { type: Boolean, default: false },
},
  emits: ['field-update'],
  setup(__props, { emit: __emit }) {

const props = __props;

const emit = __emit;

function isMasterField(field) {
  return field.key.endsWith('_notify') ||
    field.key.endsWith('_enabled') ||
    field.key.endsWith('_poll_enabled')
}

function isChannelField(field) {
  return field.key.endsWith('_notify_type') ||
    field.key.endsWith('_msgtype') ||
    field.key === 'health_check_notify_type' ||
    field.key === 'msgnotify_notify_type' ||
    field.key === 'site_stat_notify_type'
}

function isModeField(field) {
  return false
}

function isRuleField(field) {
  return field.key.endsWith('_columns') ||
    field.key.endsWith('_types') ||
    field.key.endsWith('_servers') ||
    field.key.endsWith('_user_ids') ||
    field.key.endsWith('_max_notices')
}

const visibleFields = computed$3(() => props.fields.filter(field => isReplicaFieldVisible(field, props.values)));
const masterFields = computed$3(() => visibleFields.value.filter(isMasterField));
const channelFields = computed$3(() => visibleFields.value.filter(isChannelField));
const modeFields = computed$3(() => visibleFields.value.filter(isModeField));
const ruleFields = computed$3(() => visibleFields.value.filter(isRuleField));
const detailFields = computed$3(() => visibleFields.value.filter(field => (
  !isMasterField(field) && !isChannelField(field) && true && !isRuleField(field)
)));
const primaryMasterField = computed$3(() => masterFields.value[0] || null);
const notificationLocked = computed$3(() => props.locked);
const notificationResultKeys = computed$3(() => [...new Set([
  props.resultKey,
  ...props.resultKeys,
].filter(Boolean))]);
const moduleEnabled = computed$3(() => (
  props.masterKey ? props.values[props.masterKey] !== false : true
));
const notificationEnabled = computed$3(() => {
  if (props.disabled || (props.locked && !props.channelOnlyLock) || !moduleEnabled.value) return false
  if (
    notificationResultKeys.value.length &&
    notificationResultKeys.value.every(key => props.values[key] === false)
  ) return false
  const primaryMode = modeFields.value[0];
  if (primaryMode) {
    const value = props.values[primaryMode.key];
    if (props.offValues.includes(value == null ? '' : String(value))) return false
  }
  if (notificationResultKeys.value.length) return true
  if (primaryMasterField.value) return props.values[primaryMasterField.value.key] !== false
  const primaryChannel = channelFields.value[0];
  if (!primaryChannel) return true
  const value = props.values[primaryChannel.key];
  return !props.offValues.includes(value == null ? '' : String(value))
});
const statusLabel = computed$3(() => {
  if (props.effectiveState === 'plugin_disabled') return '已停用'
  if (notificationLocked.value && props.channelOnlyLock) return '通知渠道已接管'
  if (notificationLocked.value) return '融合通知已接管'
  if (props.disabled) return '不可编辑'
  if (!moduleEnabled.value) return '模块未启用'
  if (
    notificationResultKeys.value.length > 1 &&
    notificationResultKeys.value.some(key => props.values[key] === false) &&
    notificationResultKeys.value.some(key => props.values[key] !== false)
  ) return '部分通知已启用'
  return notificationEnabled.value ? '通知已启用' : '通知已关闭'
});
const statusIcon = computed$3(() => {
  if (props.effectiveState === 'plugin_disabled') return 'mdi-alert-outline'
  if (notificationLocked.value) return 'mdi-alert-outline'
  return notificationEnabled.value && !props.disabled ? 'mdi-check-circle-outline' : 'mdi-alert-outline'
});

function shouldDisableField(field) {
  if (props.disabled || !moduleEnabled.value || field.disabled) return true
  if (props.locked && (!props.channelOnlyLock || isChannelField(field))) return true
  const dependencyKey = field.dependsOn || props.dependencies[field.key] || (
    notificationResultKeys.value.length === 1 &&
    field.key !== notificationResultKeys.value[0] &&
    isChannelField(field)
      ? notificationResultKeys.value[0]
      : ''
  );
  if (dependencyKey && props.values[dependencyKey] === false) return true
  return false
}

function withNotifyState(field) {
  return {
    ...field,
    disabled: shouldDisableField(field),
  }
}

function updateField(field, value) {
  if (!field?.key) return
  props.values[field.key] = value;
  emit('field-update', { field, value });
}

return (_ctx, _cache) => {
  const _component_VIcon = _resolveComponent("VIcon");

  return (_openBlock$3(), _createBlock$2(ConfigCardBase, {
    title: __props.title,
    note: __props.note,
    icon: __props.icon,
    values: __props.values,
    fields: [],
    disabled: __props.disabled,
    locked: __props.locked,
    "card-type": "notify",
    marker: "notify",
    "data-contract-marker": "data-notify-card",
    "data-effective-state": __props.effectiveState || undefined,
    embedded: __props.embedded
  }, {
    actions: _withCtx$1(() => [
      _createElementVNode$2("span", {
        class: _normalizeClass$2(["aoa-notify-card__status", { 'aoa-notify-card__status--off': __props.effectiveState === 'plugin_disabled' || !notificationEnabled.value || __props.disabled || __props.locked }]),
        "aria-live": "polite"
      }, [
        _createVNode$1(_component_VIcon, {
          icon: statusIcon.value,
          size: "16"
        }, null, 8, ["icon"]),
        _createElementVNode$2("span", null, _toDisplayString$2(statusLabel.value), 1)
      ], 2)
    ]),
    default: _withCtx$1(() => [
      _createElementVNode$2("div", {
        class: "aoa-notify-card",
        "data-notify-card-body": "",
        "data-notify-master-key": __props.masterKey || undefined,
        "data-notify-result-key": notificationResultKeys.value[0] || undefined,
        "data-notify-result-keys": notificationResultKeys.value.join(',') || undefined,
        "data-notify-enabled": notificationEnabled.value ? 'true' : 'false'
      }, [
        (notificationLocked.value && !__props.channelOnlyLock)
          ? (_openBlock$3(), _createElementBlock$2("div", _hoisted_2$2, [
              _createVNode$1(_component_VIcon, {
                icon: "mdi-alert-outline",
                size: "18"
              }),
              _cache[0] || (_cache[0] = _createElementVNode$2("div", null, [
                _createElementVNode$2("strong", null, "融合通知正在接管"),
                _createElementVNode$2("span", null, "当前组件的独立通知配置保持原值，但暂时不可编辑；关闭融合通知后会恢复这些字段。")
              ], -1))
            ]))
          : _createCommentVNode$2("", true),
        (masterFields.value.length)
          ? (_openBlock$3(), _createElementBlock$2("div", _hoisted_3$2, [
              (_openBlock$3(true), _createElementBlock$2(_Fragment$2, null, _renderList$2(masterFields.value, (field) => {
                return (_openBlock$3(), _createBlock$2(ConfigFieldRow, {
                  key: field.key,
                  field: withNotifyState(field),
                  "model-value": __props.values[field.key],
                  "onUpdate:modelValue": value => updateField(field, value)
                }, null, 8, ["field", "model-value", "onUpdate:modelValue"]))
              }), 128))
            ]))
          : _createCommentVNode$2("", true),
        (channelFields.value.length)
          ? (_openBlock$3(), _createElementBlock$2("div", _hoisted_4$2, [
              (_openBlock$3(true), _createElementBlock$2(_Fragment$2, null, _renderList$2(channelFields.value, (field) => {
                return (_openBlock$3(), _createBlock$2(ConfigFieldRow, {
                  key: field.key,
                  field: withNotifyState(field),
                  "model-value": __props.values[field.key],
                  "onUpdate:modelValue": value => updateField(field, value)
                }, null, 8, ["field", "model-value", "onUpdate:modelValue"]))
              }), 128))
            ]))
          : _createCommentVNode$2("", true),
        (modeFields.value.length)
          ? (_openBlock$3(), _createElementBlock$2("div", _hoisted_5$2, [
              (_openBlock$3(true), _createElementBlock$2(_Fragment$2, null, _renderList$2(modeFields.value, (field) => {
                return (_openBlock$3(), _createBlock$2(ConfigFieldRow, {
                  key: field.key,
                  field: withNotifyState(field),
                  "model-value": __props.values[field.key],
                  "onUpdate:modelValue": value => updateField(field, value)
                }, null, 8, ["field", "model-value", "onUpdate:modelValue"]))
              }), 128))
            ]))
          : _createCommentVNode$2("", true),
        (ruleFields.value.length)
          ? (_openBlock$3(), _createElementBlock$2("div", _hoisted_6$2, [
              (_openBlock$3(true), _createElementBlock$2(_Fragment$2, null, _renderList$2(ruleFields.value, (field) => {
                return (_openBlock$3(), _createBlock$2(ConfigFieldRow, {
                  key: field.key,
                  field: withNotifyState(field),
                  "model-value": __props.values[field.key],
                  "onUpdate:modelValue": value => updateField(field, value)
                }, null, 8, ["field", "model-value", "onUpdate:modelValue"]))
              }), 128))
            ]))
          : _createCommentVNode$2("", true),
        (detailFields.value.length)
          ? (_openBlock$3(), _createElementBlock$2("div", _hoisted_7$2, [
              (_openBlock$3(true), _createElementBlock$2(_Fragment$2, null, _renderList$2(detailFields.value, (field) => {
                return (_openBlock$3(), _createBlock$2(ConfigFieldRow, {
                  key: field.key,
                  field: withNotifyState(field),
                  "model-value": __props.values[field.key],
                  "onUpdate:modelValue": value => updateField(field, value)
                }, null, 8, ["field", "model-value", "onUpdate:modelValue"]))
              }), 128))
            ]))
          : _createCommentVNode$2("", true)
      ], 8, _hoisted_1$2)
    ]),
    _: 1
  }, 8, ["title", "note", "icon", "values", "disabled", "locked", "data-effective-state", "embedded"]))
}
}

};
const NotifyCard = /*#__PURE__*/_export_sfc(_sfc_main$3, [['__scopeId',"data-v-93a94e84"]]);

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

function previewSubfillRule(rule = {}) {
  const fields = Array.isArray(rule.fields) ? rule.fields : [];
  if (!fields.length) return '没有可展示的填充字段'
  return fields.map(field => `${field.label}：${field.value || '空值'}`).join('；')
}

const {unref:_unref$1,createElementVNode:_createElementVNode$1,normalizeClass:_normalizeClass$1,vModelText:_vModelText,withDirectives:_withDirectives,toDisplayString:_toDisplayString$1,openBlock:_openBlock$2,createElementBlock:_createElementBlock$1,createCommentVNode:_createCommentVNode$1,createTextVNode:_createTextVNode,mergeProps:_mergeProps,renderList:_renderList$1,Fragment:_Fragment$1} = await importShared('vue');


const _hoisted_1$1 = ["data-subfill-projection-open"];
const _hoisted_2$1 = { class: "aoa-subfill-code__controls" };
const _hoisted_3$1 = ["aria-checked", "disabled"];
const _hoisted_4$1 = { class: "aoa-subfill-code__input" };
const _hoisted_5$1 = ["disabled"];
const _hoisted_6$1 = {
  class: "aoa-subfill-projection-shell",
  "data-subfill-projection-shell": ""
};
const _hoisted_7$1 = ["aria-expanded"];
const _hoisted_8$1 = { class: "aoa-subfill-projection-toggle__label" };
const _hoisted_9$1 = { key: 0 };
const _hoisted_10$1 = ["d"];
const _hoisted_11$1 = {
  key: 0,
  class: "aoa-subfill-projection__empty",
  "data-subfill-code-empty": ""
};
const _hoisted_12$1 = {
  key: 1,
  class: "aoa-subfill-projection__list",
  "data-subfill-code-card-list": ""
};
const _hoisted_13$1 = ["id", "data-subfill-code-line", "data-subfill-code-valid"];
const _hoisted_14$1 = ["id", "aria-expanded", "aria-controls", "title", "onClick"];
const _hoisted_15$1 = { class: "aoa-subfill-code-card__line" };
const _hoisted_16$1 = { class: "aoa-subfill-code-card__title" };
const _hoisted_17$1 = { class: "aoa-subfill-code-card__summary" };
const _hoisted_18$1 = { key: 0 };
const _hoisted_19$1 = ["d"];
const _hoisted_20$1 = ["id", "aria-labelledby"];
const _hoisted_21$1 = {
  key: 0,
  class: "aoa-subfill-code-card__fields"
};
const _hoisted_22$1 = { key: 0 };
const _hoisted_23$1 = {
  key: 1,
  class: "aoa-subfill-code-card__errors",
  role: "alert",
  "data-subfill-code-errors": ""
};
const _hoisted_24$1 = {
  key: 2,
  class: "aoa-subfill-code-card__preview",
  "data-subfill-code-preview": ""
};

const {computed: computed$2,nextTick: nextTick$1,ref: ref$4,useAttrs} = await importShared('vue');


const _sfc_main$2 = /*@__PURE__*/Object.assign({ inheritAttrs: false }, {
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

const projectionOpen = ref$4(false);
const expandedRuleId = ref$4(null);
const projectionPanel = ref$4(null);
const ruleCards = new Map();
const codeText = computed$2({
  get: () => String(props.values.subfill_category_confs ?? ''),
  set: value => { props.values.subfill_category_confs = String(value ?? ''); },
});
const enabled = computed$2({
  get: () => Boolean(props.values.subfill_category_enabled),
  set: value => { props.values.subfill_category_enabled = Boolean(value); },
});
const rules = computed$2(() => parseSubfillRules(codeText.value));
const errorCount = computed$2(() => rules.value.reduce((count, rule) => count + validateSubfillRule(rule).length, 0));

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
  return (_openBlock$2(), _createElementBlock$1(_Fragment$1, null, [
    _createElementVNode$1("section", _mergeProps(_unref$1(attrs), {
      class: ["aoa-subfill-code", { 'aoa-subfill-code--disabled': __props.disabled }],
      "data-subfill-code-editor": "",
      "data-subfill-projection-open": projectionOpen.value ? 'true' : 'false'
    }), [
      _createElementVNode$1("div", _hoisted_2$1, [
        _createElementVNode$1("button", {
          type: "button",
          class: _normalizeClass$1(["aoa-subfill-code__switch", { 'aoa-subfill-code__switch--on': enabled.value }]),
          role: "switch",
          "aria-checked": enabled.value,
          disabled: __props.disabled,
          onClick: _cache[0] || (_cache[0] = $event => (enabled.value = !enabled.value))
        }, [
          _createElementVNode$1("span", {
            class: _normalizeClass$1(["aoa-toggle-switch", { 'aoa-toggle-switch--on': enabled.value }]),
            "aria-hidden": "true"
          }, [...(_cache[2] || (_cache[2] = [
            _createElementVNode$1("span", { class: "aoa-toggle-switch__thumb" }, null, -1)
          ]))], 2),
          _cache[3] || (_cache[3] = _createElementVNode$1("span", null, "启用二级分类填充", -1))
        ], 10, _hoisted_3$1),
        _createElementVNode$1("label", _hoisted_4$1, [
          _cache[4] || (_cache[4] = _createElementVNode$1("span", null, "规则代码", -1)),
          _withDirectives(_createElementVNode$1("textarea", {
            "onUpdate:modelValue": _cache[1] || (_cache[1] = $event => ((codeText).value = $event)),
            rows: "6",
            spellcheck: "false",
            disabled: __props.disabled,
            "data-subfill-code-input": "",
            placeholder: "category:动画/日番#resolution:1080p#include:简体#sites:观众,青蛙"
          }, null, 8, _hoisted_5$1), [
            [_vModelText, codeText.value]
          ])
        ])
      ]),
      _createElementVNode$1("div", _hoisted_6$1, [
        _createElementVNode$1("button", {
          type: "button",
          class: "aoa-subfill-projection-toggle",
          "aria-expanded": projectionOpen.value,
          "aria-controls": "aoa-subfill-projection-panel",
          "data-subfill-projection-toggle": "",
          onClick: toggleProjection
        }, [
          _createElementVNode$1("span", _hoisted_8$1, _toDisplayString$1(projectionOpen.value ? '收起图形化' : '展开图形化'), 1),
          _createElementVNode$1("span", {
            class: _normalizeClass$1(["aoa-subfill-projection-toggle__meta", { 'aoa-subfill-projection-toggle__meta--error': errorCount.value }])
          }, [
            _createTextVNode(_toDisplayString$1(rules.value.length) + " 条", 1),
            (errorCount.value)
              ? (_openBlock$2(), _createElementBlock$1("span", _hoisted_9$1, " · " + _toDisplayString$1(errorCount.value) + " 个错误", 1))
              : _createCommentVNode$1("", true)
          ], 2),
          (_openBlock$2(), _createElementBlock$1("svg", {
            class: _normalizeClass$1(["aoa-subfill-projection-toggle__chevron", { 'aoa-subfill-projection-toggle__chevron--open': projectionOpen.value }]),
            viewBox: "0 0 24 24",
            width: "18",
            height: "18",
            "aria-hidden": "true"
          }, [
            _createElementVNode$1("path", {
              d: _unref$1(mdiChevronDown),
              fill: "currentColor"
            }, null, 8, _hoisted_10$1)
          ], 2))
        ], 8, _hoisted_7$1)
      ])
    ], 16, _hoisted_1$1),
    (projectionOpen.value)
      ? (_openBlock$2(), _createElementBlock$1("section", {
          key: 0,
          ref_key: "projectionPanel",
          ref: projectionPanel,
          id: "aoa-subfill-projection-panel",
          class: "aoa-subfill-projection",
          "data-subfill-code-projection": ""
        }, [
          (!rules.value.length)
            ? (_openBlock$2(), _createElementBlock$1("div", _hoisted_11$1, " 暂无规则 "))
            : (_openBlock$2(), _createElementBlock$1("div", _hoisted_12$1, [
                (_openBlock$2(true), _createElementBlock$1(_Fragment$1, null, _renderList$1(rules.value, (rule) => {
                  return (_openBlock$2(), _createElementBlock$1("article", {
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
                      _createElementVNode$1("span", _hoisted_15$1, "第 " + _toDisplayString$1(rule.lineNumber) + " 行", 1),
                      _createElementVNode$1("span", _hoisted_16$1, _toDisplayString$1(rule.title), 1),
                      _createElementVNode$1("span", _hoisted_17$1, [
                        _createTextVNode(_toDisplayString$1(rule.fields.length) + " 个字段", 1),
                        (rule.errors.length)
                          ? (_openBlock$2(), _createElementBlock$1("span", _hoisted_18$1, " · " + _toDisplayString$1(rule.errors.length) + " 个错误", 1))
                          : _createCommentVNode$1("", true)
                      ]),
                      (_openBlock$2(), _createElementBlock$1("svg", {
                        class: _normalizeClass$1(["aoa-subfill-code-card__chevron", { 'aoa-subfill-code-card__chevron--open': isExpanded(rule.id) }]),
                        viewBox: "0 0 24 24",
                        width: "18",
                        height: "18",
                        "aria-hidden": "true"
                      }, [
                        _createElementVNode$1("path", {
                          d: _unref$1(mdiChevronDown),
                          fill: "currentColor"
                        }, null, 8, _hoisted_19$1)
                      ], 2))
                    ], 8, _hoisted_14$1),
                    (isExpanded(rule.id))
                      ? (_openBlock$2(), _createElementBlock$1("div", {
                          key: 0,
                          id: `subfill-rule-content-${rule.lineNumber}`,
                          class: "aoa-subfill-code-card__content",
                          role: "region",
                          "aria-labelledby": `subfill-rule-toggle-${rule.lineNumber}`,
                          "data-subfill-rule-content": ""
                        }, [
                          (rule.fields.length)
                            ? (_openBlock$2(), _createElementBlock$1("dl", _hoisted_21$1, [
                                (_openBlock$2(true), _createElementBlock$1(_Fragment$1, null, _renderList$1(rule.fields, (field, fieldIndex) => {
                                  return (_openBlock$2(), _createElementBlock$1("div", {
                                    key: `${field.key}-${fieldIndex}`
                                  }, [
                                    _createElementVNode$1("dt", null, [
                                      _createTextVNode(_toDisplayString$1(field.label), 1),
                                      (field.duplicate)
                                        ? (_openBlock$2(), _createElementBlock$1("span", _hoisted_22$1, "（重复）"))
                                        : _createCommentVNode$1("", true)
                                    ]),
                                    _createElementVNode$1("dd", null, _toDisplayString$1(field.value || '空值'), 1)
                                  ]))
                                }), 128))
                              ]))
                            : _createCommentVNode$1("", true),
                          (rule.errors.length)
                            ? (_openBlock$2(), _createElementBlock$1("div", _hoisted_23$1, [
                                (_openBlock$2(true), _createElementBlock$1(_Fragment$1, null, _renderList$1(rule.errors, (error) => {
                                  return (_openBlock$2(), _createElementBlock$1("span", { key: error }, _toDisplayString$1(error), 1))
                                }), 128))
                              ]))
                            : (_openBlock$2(), _createElementBlock$1("p", _hoisted_24$1, _toDisplayString$1(_unref$1(previewSubfillRule)(rule)), 1))
                        ], 8, _hoisted_20$1))
                      : _createCommentVNode$1("", true)
                  ], 10, _hoisted_13$1))
                }), 128))
              ]))
        ], 512))
      : _createCommentVNode$1("", true)
  ], 64))
}
}

});
const SubfillRuleEditor = /*#__PURE__*/_export_sfc(_sfc_main$2, [['__scopeId',"data-v-d2cb563d"]]);

// 插件配置默认值 — 纯数据，无运行时依赖
const DEFAULT_DLTAG_CRON = '0 */6 * * *';

const defaults = {
  enabled: false,
  local_plugin_repo: '',
  fusion_notify_enabled: true,
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
  health_check_notify_type: 'Plugin',
  subscribe_reminder_enabled: true,
  subscribe_reminder_schedule_enabled: true,
  subscribe_reminder_cron: '0 9 * * *',
  subscribe_reminder_subtype: ['movie', 'tv'],
  subscribe_reminder_msgtype: 'Subscribe',
  site_stat_enabled: true,
  site_stat_schedule_enabled: true,
  site_stat_cron: '0 8 * * *',
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
  backup_notify: false,
  backup_notify_type: 'Plugin',
  backup_cron: '0 4 * * 1',
  backup_keep_count: 5,
  backup_path: '/config/plugins/AgentOpsAssistant/Backup',
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
  market_update_strategy: 'check',
  market_update_install_ids: [],
  market_update_exclude_ids: [],
  update_scheduled_notify: false,
  update_notify_type: 'Plugin',
  plugin_uninstall_ids: [],
  plugin_uninstall_remove_plugin: true,
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
  { key: 'maintenance', title: '系统维护', icon: 'mdi-cog-outline', desc: '自动备份、日志清理与更新检查' },
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
    { key: 'updates', title: '更新检查', icon: 'mdi-update' },
  ],
  plugin: [
    { key: 'clean', title: '安全卸载', icon: 'mdi-puzzle-remove-outline' },
  ],
};

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

const siteStatRangeItems = [{ title: '今日数据', value: 'today' }, { title: '汇总数据', value: 'total' }, { title: '所有数据', value: 'all' }];
const marketNotifyItems = notificationTypeItems;
const mpUpdateTypes = ['后端', '前端'].map(v => ({ title: v, value: v }));
const marketUpdateStrategies = [
  { title: '仅检查', value: 'check' },
  { title: '同步插件库', value: 'sync' },
  { title: '同步并更新插件', value: 'install' },
];
const seedActionsItems = [{ title: '暂停', value: 'pause' }, { title: '删除种子', value: 'delete' }, { title: '删除种子和文件', value: 'deletefile' }];
const dltagTaskItems = [
  { title: '自动标签', value: 'tagging' },
  { title: '恢复做种', value: 'seeding' },
  { title: '清理失效任务', value: 'cleanup' },
];
const dltagDeleteStrategyItems = [
  { title: '确认文件已删除后清理', value: 'delayed' },
  { title: '收到事件后立即清理', value: 'early' },
];
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

const {ref: ref$3,reactive: reactive$1,computed: computed$1} = await importShared('vue');

// 备份恢复逻辑 — 本地 + WebDAV 两套独立状态机
// 入参：form(reactive 配置对象), api(MP 插件 API 句柄)
function useBackupRestore(form, api) {
  // --- 本地备份恢复 ---
  const backupArchives = ref$3([]);
  const backupArchivesLoading = ref$3(false);
  const backupRestoreLoading = ref$3(false);
  const backupRestoreResult = ref$3(null);
  const backupRestore = reactive$1({
    archive: '',
    restore_config: true,
    restore_cookies: true,
    restore_database: true,
    confirm: false,
  });

  // --- WebDAV 备份恢复 ---
  const webdavBackupArchives = ref$3([]);
  const webdavBackupArchivesLoading = ref$3(false);
  const webdavBackupRestoreLoading = ref$3(false);
  const webdavBackupRestoreResult = ref$3(null);
  const webdavBackupRestore = reactive$1({
    archive: '',
    restore_config: true,
    restore_cookies: true,
    restore_database: true,
    confirm: false,
  });

  // --- 可用性 computed ---
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
  const webdavBackupRestoreUnavailable = computed$1(() => !form.enabled || !form.backup_enabled || !webdavConfigured.value);
  const webdavBackupRestoreUnavailableMessage = computed$1(() => {
    if (!form.enabled) return '插件总开关未启用，WebDAV 恢复已跳过。'
    if (!form.backup_enabled) return '自动备份组件未启用，WebDAV 恢复已跳过。'
    if (!webdavConfigured.value) return 'WebDAV 地址、账号或密码未完整配置，恢复已跳过。'
    return ''
  });

  // --- 数据加载 ---
  async function loadBackupArchives() {
    backupArchivesLoading.value = true;
    try {
      const res = await getPluginApi(api, 'backup_archives');
      backupArchives.value = Array.isArray(res) ? res : (res?.data || []);
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
      const res = await getPluginApi(api, 'webdav_backup_archives');
      webdavBackupArchives.value = Array.isArray(res) ? res : (res?.data || []);
      if (!webdavBackupRestore.archive && webdavBackupArchives.value.length) {
        webdavBackupRestore.archive = webdavBackupArchives.value[0].name || webdavBackupArchives.value[0].value || '';
      }
    } catch {
      webdavBackupArchives.value = [];
    } finally {
      webdavBackupArchivesLoading.value = false;
    }
  }

  // --- payload 构建 ---
  function backupRestorePayload() {
    return {
      archive: backupRestore.archive,
      restore_config: !!backupRestore.restore_config,
      restore_cookies: !!backupRestore.restore_cookies,
      restore_database: !!backupRestore.restore_database,
      confirm: !!backupRestore.confirm,
    }
  }

  function webdavBackupRestorePayload() {
    return {
      archive: webdavBackupRestore.archive,
      restore_config: !!webdavBackupRestore.restore_config,
      restore_cookies: !!webdavBackupRestore.restore_cookies,
      restore_database: !!webdavBackupRestore.restore_database,
      confirm: !!webdavBackupRestore.confirm,
    }
  }

  // --- 预览 / 执行 ---
  async function previewBackupRestore() {
    if (!backupRestore.archive || backupRestoreLoading.value) return
    if (backupRestoreUnavailable.value) {
      backupRestoreResult.value = { code: 1, msg: backupRestoreUnavailableMessage.value };
      return
    }
    backupRestoreLoading.value = true;
    try {
      backupRestoreResult.value = await postPluginApi(api, 'preview_backup_restore', backupRestorePayload());
    } catch (err) {
      backupRestoreResult.value = { code: 1, msg: err?.message || '备份恢复预览失败' };
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
      webdavBackupRestoreResult.value = await postPluginApi(api, 'preview_webdav_backup_restore', webdavBackupRestorePayload());
    } catch (err) {
      webdavBackupRestoreResult.value = { code: 1, msg: err?.message || 'WebDAV 备份恢复预览失败' };
    } finally {
      webdavBackupRestoreLoading.value = false;
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
      webdavBackupRestoreResult.value = await postPluginApi(api, 'run_webdav_backup_restore', webdavBackupRestorePayload());
      await loadBackupArchives();
    } catch (err) {
      webdavBackupRestoreResult.value = { code: 1, msg: err?.message || 'WebDAV 备份恢复执行失败' };
    } finally {
      webdavBackupRestore.confirm = false;
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
      backupRestoreResult.value = await postPluginApi(api, 'run_backup_restore', backupRestorePayload());
      await loadBackupArchives();
    } catch (err) {
      backupRestoreResult.value = { code: 1, msg: err?.message || '备份恢复执行失败' };
    } finally {
      backupRestore.confirm = false;
      backupRestoreLoading.value = false;
    }
  }

  return {
    backupArchives, backupArchivesLoading, backupRestoreLoading, backupRestoreResult, backupRestore,
    webdavBackupArchives, webdavBackupArchivesLoading, webdavBackupRestoreLoading, webdavBackupRestoreResult, webdavBackupRestore,
    backupRestoreUnavailable, backupRestoreUnavailableMessage,
    webdavBackupRestoreUnavailable, webdavBackupRestoreUnavailableMessage,
    loadBackupArchives, loadWebdavBackupArchives,
    previewBackupRestore, previewWebdavBackupRestore,
    runBackupRestore, runWebdavBackupRestore,
  }
}

const {ref: ref$2} = await importShared('vue');

// 远程数据加载 — 插件列表 / TG 控制台 / 插件市场 / 下载器 / 媒体服务器
// 入参：api(MP 插件 API 句柄)
function useDataLoader(api) {
  // 已安装插件列表（插件卸载用）
  const installedPlugins = ref$2([]);
  const installedLoading = ref$2(false);
  async function loadInstalledPlugins() {
    installedLoading.value = true;
    try {
      const res = await getPluginApi(api, 'installed_plugins');
      installedPlugins.value = Array.isArray(res) ? res : (res?.data || []);
    } catch {
      installedPlugins.value = [];
    } finally {
      installedLoading.value = false;
    }
  }

  // TG 控制台状态
  const tgConsoleStatus = ref$2({});
  const tgConsoleLoading = ref$2(false);
  async function loadTgConsoleStatus() {
    tgConsoleLoading.value = true;
    try {
      const res = await getPluginApi(api, 'tg_console_status');
      tgConsoleStatus.value = res?.data || res || {};
    } catch (err) {
      tgConsoleStatus.value = { last_error: err?.message || '状态读取失败' };
    } finally {
      tgConsoleLoading.value = false;
    }
  }

  // 插件库仓库（更新黑名单用）
  const pluginMarkets = ref$2([]);
  const marketsLoading = ref$2(false);
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
  const downloaderOptions = ref$2([]);
  const downloadersLoading = ref$2(false);
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
  const mediaserverOptions = ref$2([]);
  const mediaserversLoading = ref$2(false);
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

const {unref:_unref,createElementVNode:_createElementVNode,openBlock:_openBlock$1,createElementBlock:_createElementBlock,normalizeClass:_normalizeClass,renderList:_renderList,Fragment:_Fragment,normalizeStyle:_normalizeStyle,toDisplayString:_toDisplayString,createCommentVNode:_createCommentVNode,createBlock:_createBlock$1,withModifiers:_withModifiers,Teleport:_Teleport,Transition:_Transition,withCtx:_withCtx,createVNode:_createVNode} = await importShared('vue');


const _hoisted_1 = ["data-effective-state"];
const _hoisted_2 = {
  class: "aoa-config-top-bar",
  "data-config-top-bar": ""
};
const _hoisted_3 = { class: "aoa-config-top-actions" };
const _hoisted_4 = { class: "aoa-config-master-switch" };
const _hoisted_5 = ["aria-checked"];
const _hoisted_6 = ["aria-selected", "data-config-main-tab", "data-effective-state", "onClick"];
const _hoisted_7 = ["viewBox"];
const _hoisted_8 = ["d"];
const _hoisted_9 = {
  class: "aoa-config-subtab-bar",
  "data-config-subtab-bar": ""
};
const _hoisted_10 = ["aria-label"];
const _hoisted_11 = ["id", "aria-selected", "aria-controls", "data-config-subtab", "data-effective-state", "onClick"];
const _hoisted_12 = ["viewBox"];
const _hoisted_13 = ["d"];
const _hoisted_14 = {
  key: 0,
  class: "aoa-config-subtab-current",
  "aria-live": "polite"
};
const _hoisted_15 = ["id", "aria-labelledby", "data-config-active-sub", "data-effective-state"];
const _hoisted_16 = ["data-effective-state"];
const _hoisted_17 = { class: "aoa-config-hero-left" };
const _hoisted_18 = { class: "aoa-config-hero-icon" };
const _hoisted_19 = ["viewBox"];
const _hoisted_20 = ["d"];
const _hoisted_21 = { class: "aoa-config-hero-info" };
const _hoisted_22 = { class: "aoa-config-hero-kicker" };
const _hoisted_23 = { class: "aoa-config-hero-title" };
const _hoisted_24 = { class: "aoa-config-hero-desc" };
const _hoisted_25 = {
  key: 0,
  class: "aoa-config-hero-right"
};
const _hoisted_26 = ["aria-checked", "aria-label", "data-config-aggregate-state"];
const _hoisted_27 = {
  key: 1,
  class: "aoa-config-hero-right aoa-config-hero-right--danger",
  "data-config-danger-header": ""
};
const _hoisted_28 = {
  key: 0,
  class: "aoa-fusion-takeover-note",
  "data-config-notice-tone": "blue",
  role: "status"
};
const _hoisted_29 = {
  class: "aoa-mdi-icon aoa-fusion-takeover-note__icon",
  viewBox: "0 0 24 24",
  width: "18",
  height: "18",
  "aria-hidden": "true"
};
const _hoisted_30 = ["d"];
const _hoisted_31 = {
  key: 1,
  class: "aoa-fusion-takeover-note aoa-config-risk-note--orange",
  "data-config-notice-tone": "orange",
  "data-config-notice-icon": "warning",
  role: "status"
};
const _hoisted_32 = {
  class: "aoa-mdi-icon aoa-fusion-takeover-note__icon",
  viewBox: "0 0 24 24",
  width: "18",
  height: "18",
  "aria-hidden": "true"
};
const _hoisted_33 = ["d"];
const _hoisted_34 = ["data-subfill-layout-container"];
const _hoisted_35 = ["data-subfill-config-surface", "data-subfill-projection-open", "data-compact-operational-surface", "data-effective-state"];
const _hoisted_36 = {
  class: "aoa-seedclean-confirm-dialog",
  role: "dialog",
  "aria-modal": "true",
  "aria-labelledby": "seedclean-confirm-title"
};
const _hoisted_37 = { class: "aoa-seedclean-confirm-dialog__head" };
const _hoisted_38 = { id: "seedclean-confirm-title" };
const _hoisted_39 = {
  class: "aoa-mdi-icon",
  viewBox: "0 0 24 24",
  width: "18",
  height: "18",
  "aria-hidden": "true"
};
const _hoisted_40 = ["d"];
const _hoisted_41 = {
  class: "aoa-mdi-icon",
  viewBox: "0 0 24 24",
  width: "19",
  height: "19",
  "aria-hidden": "true"
};
const _hoisted_42 = ["d"];
const _hoisted_43 = { class: "aoa-seedclean-confirm-dialog__summary" };
const _hoisted_44 = {
  class: "aoa-seedclean-confirm-dialog__items",
  "data-seedclean-confirm-items": ""
};
const _hoisted_45 = { class: "aoa-seedclean-confirm-dialog__item" };
const _hoisted_46 = { class: "aoa-seedclean-confirm-dialog__actions" };
const _hoisted_47 = {
  class: "aoa-mdi-icon",
  viewBox: "0 0 24 24",
  width: "15",
  height: "15",
  "aria-hidden": "true"
};
const _hoisted_48 = ["d"];
const _hoisted_49 = {
  class: "aoa-seedclean-confirm-dialog",
  role: "dialog",
  "aria-modal": "true",
  "aria-labelledby": "plugin-uninstall-confirm-title"
};
const _hoisted_50 = { class: "aoa-seedclean-confirm-dialog__head" };
const _hoisted_51 = {
  class: "aoa-mdi-icon",
  viewBox: "0 0 24 24",
  width: "18",
  height: "18",
  "aria-hidden": "true"
};
const _hoisted_52 = ["d"];
const _hoisted_53 = { class: "aoa-seedclean-confirm-dialog__warning aoa-seedclean-confirm-dialog__warning--danger" };
const _hoisted_54 = {
  class: "aoa-mdi-icon",
  viewBox: "0 0 24 24",
  width: "19",
  height: "19",
  "aria-hidden": "true"
};
const _hoisted_55 = ["d"];
const _hoisted_56 = { class: "aoa-seedclean-confirm-dialog__summary" };
const _hoisted_57 = {
  class: "aoa-seedclean-confirm-dialog__items",
  "data-plugin-uninstall-confirm-targets": ""
};
const _hoisted_58 = {
  class: "aoa-seedclean-confirm-dialog__items",
  "data-plugin-uninstall-confirm-actions": ""
};
const _hoisted_59 = { class: "aoa-seedclean-confirm-dialog__actions" };
const _hoisted_60 = {
  class: "aoa-mdi-icon",
  viewBox: "0 0 24 24",
  width: "15",
  height: "15",
  "aria-hidden": "true"
};
const _hoisted_61 = ["d"];
const _hoisted_62 = {
  class: "aoa-seedclean-confirm-dialog",
  role: "dialog",
  "aria-modal": "true",
  "aria-labelledby": "downloader-helper-confirm-title"
};
const _hoisted_63 = { class: "aoa-seedclean-confirm-dialog__head" };
const _hoisted_64 = {
  class: "aoa-mdi-icon",
  viewBox: "0 0 24 24",
  width: "18",
  height: "18",
  "aria-hidden": "true"
};
const _hoisted_65 = ["d"];
const _hoisted_66 = { class: "aoa-seedclean-confirm-dialog__warning" };
const _hoisted_67 = {
  class: "aoa-mdi-icon",
  viewBox: "0 0 24 24",
  width: "19",
  height: "19",
  "aria-hidden": "true"
};
const _hoisted_68 = ["d"];
const _hoisted_69 = { class: "aoa-seedclean-confirm-dialog__summary" };
const _hoisted_70 = {
  class: "aoa-seedclean-confirm-dialog__items",
  "data-downloader-helper-confirm-items": ""
};
const _hoisted_71 = { class: "aoa-seedclean-confirm-dialog__actions" };
const _hoisted_72 = {
  class: "aoa-mdi-icon",
  viewBox: "0 0 24 24",
  width: "15",
  height: "15",
  "aria-hidden": "true"
};
const _hoisted_73 = ["d"];
const _hoisted_74 = {
  class: "aoa-config-action-strip",
  "data-config-action-strip": ""
};
const _hoisted_75 = { class: "aoa-config-action-strip-copy" };
const _hoisted_76 = { class: "aoa-config-action-hint" };
const _hoisted_77 = { class: "aoa-config-action-strip-buttons" };

const {reactive,ref: ref$1,computed,watch: watch$1,nextTick,onMounted: onMounted$1,onBeforeUnmount,defineComponent,h} = await importShared('vue');

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
  pluginId: { type: String, default: 'AgentOpsAssistant' },
  configRecordState: {
    type: String,
    default: 'unknown',
    validator: value => ['unknown', 'absent', 'present'].includes(value),
  },
},
  emits: ['save', 'close', 'switch'],
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
const emit = __emit;
const { rootThemeClass } = useAgentOpsTheme();

const form = reactive({});
const subfillRulesValid = computed(() => {
  if (!form.subfill_category_enabled) return true
  const rules = parseSubfillRules(form.subfill_category_confs);
  return rules.length > 0 && rules.every(rule => validateSubfillRule(rule).length === 0)
});
const activeMain = ref$1('notify');
const activeSub = ref$1('fusion');
const subfillProjectionOpen = ref$1(false);
const configRoot = ref$1(null);
const mainNav = ref$1(null);
const subtabList = ref$1(null);
let dialogScrollHost = null;
let dialogSurfaceHost = null;

// Manual action state
// === 运行数据与动作编排 ===
const {
  installedPlugins, loadInstalledPlugins,
  loadTgConsoleStatus,
  loadPluginMarkets,
  downloaderOptions, loadDownloaders,
  mediaserverOptions, loadMediaservers,
} = useDataLoader(props.api);

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
  action, actionDisabledReason, actionComponentDisabledMessage, runAction,
} = useActionRunner(form, props.api, installedPlugins, loadInstalledPlugins);

const {
  loadBackupArchives, loadWebdavBackupArchives} = useBackupRestore(form, props.api);

const currentMain = computed(() => mainTabs.find(item => item.key === activeMain.value) || mainTabs[0]);
const currentSubs = computed(() => subTabs[activeMain.value] || []);
const currentSub = computed(() => currentSubs.value.find(item => item.key === activeSub.value) || currentSubs.value[0] || null);
const currentSubTitle = computed(() => currentSub.value?.title || currentMain.value?.title || '');
const heroMap = {
  fusion: { kicker: '融合通知', on: '已开启，通知统一走卡片', off: '已关闭，各组件自行发送', desc: '开启后所有通知汇入一张 Telegram 卡片，各组件独立渠道将被接管。' },
  server: { kicker: '媒体通知', on: '正在监听媒体事件', off: '未启用', desc: '接收 Emby/Jellyfin/Plex Webhook 事件并转发给用户。' },
  subscribe: { kicker: '订阅追新', on: '每日自动检查更新', off: '未启用', desc: '每日检查订阅更新并按规则推送通知。' },
  sites: { kicker: '站点统计', on: '正在采集站点数据', off: '未启用', desc: '采集每日站点上传/下载增量，供应仪表盘和日报。' },
  hc: { kicker: '健康巡查', on: '定时巡检中', off: '未启用', desc: '检查数据库、存储空间、目录是否正常，异常时告警。' },
  seedremove: { kicker: '自动删种', on: '按条件自动清理', off: '未启用', desc: '按分享率、大小、做种时间等规则自动暂停或删除种子。' },
  dltagmain: { kicker: '下载器助手', on: '自动整理下载任务', off: '未启用', desc: '统一处理标签、恢复做种与失效任务，不替代按规则自动删种。' },
  subfill: { kicker: '规则填充', on: '自动回填规格', off: '未启用', desc: '下载完成后，用实际规格参数回填订阅规则，锁定后续版本。' },
  backup: { kicker: '自动备份', on: '定时备份中', off: '未启用', desc: '按策略备份配置与数据，支持本地和 WebDAV 远端。' },
  logs: { kicker: '日志清理', on: '定时清理中', off: '未启用', desc: '定期裁剪插件运行日志，控制体积。' },
  updates: { kicker: '更新检查', on: '系统与插件库检查均已启用', mixed: '部分启用', off: '系统与插件库检查均未启用', desc: '分别检查 MoviePilot 和插件库更新，共用一套结果通知。' },
  clean: { kicker: '插件卸载', on: '已选目标，待执行', off: '未选择卸载目标', desc: '彻底移除插件并清理配置、数据和源码残留。此操作不可逆。' },
};
const currentHero = computed(() => heroMap[activeSub.value] || heroMap.fusion);
const heroIconPath = computed(() => activeSub.value === 'fusion' ? faIdCardPath : iconPath(currentSub.value?.icon || 'mdi-cog-outline'));
const heroIconViewBox = computed(() => activeSub.value === 'fusion' ? '0 0 576 512' : '0 0 24 24');
const updateMasterState = computed(() => {
  const mpEnabled = Boolean(form.mp_update_enabled);
  const marketEnabled = Boolean(form.market_update_enabled);
  if (mpEnabled && marketEnabled) return 'on'
  if (!mpEnabled && !marketEnabled) return 'off'
  return 'mixed'
});
const heroMixed = computed(() => activeSub.value === 'updates' && updateMasterState.value === 'mixed');
const pluginEnabled = computed(() => form.enabled !== false);
const effectiveStateInputs = {
  fusion: { enabledKey: 'fusion_notify_enabled', scheduleRequired: true, scheduleKey: 'fusion_notify_enabled', cronKeys: ['fusion_card_create_cron', 'fusion_card_refresh_cron'] },
  server: { enabledKey: 'msgnotify_enabled' },
  subscribe: { enabledKey: 'subscribe_reminder_enabled', scheduleRequired: true, scheduleKey: 'subscribe_reminder_schedule_enabled', cronKeys: ['subscribe_reminder_cron'] },
  sites: { enabledKey: 'site_stat_enabled', scheduleRequired: true, scheduleKey: 'site_stat_schedule_enabled', cronKeys: ['site_stat_cron'] },
  hc: { enabledKey: 'health_check_enabled', scheduleRequired: true, scheduleKey: 'health_check_schedule_enabled', cronKeys: ['health_check_cron'] },
  seedremove: { enabledKey: 'seedclean_enabled', scheduleRequired: true, scheduleKey: 'seedclean_schedule_enabled', cronKeys: ['seedclean_cron'], requiredKeys: ['seedclean_downloaders'] },
  dltagmain: { enabledKey: 'dltag_enabled', requiredKeys: ['dltag_tasks'] },
  subfill: { enabledKey: 'subfill_enabled' },
  backup: { enabledKey: 'backup_enabled', scheduleRequired: true, cronKeys: ['backup_cron'] },
  logs: { enabledKey: 'log_clean_enabled', scheduleRequired: true, scheduleKey: 'log_clean_schedule_enabled', cronKeys: ['log_clean_cron'] },
  updates: { enabledKeys: ['mp_update_enabled', 'market_update_enabled'], scheduleRequired: true, scheduleKeys: ['mp_update_schedule_enabled', 'market_update_schedule_enabled'], cronKeys: ['mp_update_cron', 'market_update_cron'] },
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
    : (enabledKeys.length ? enabledKeys.every(key => form[key] !== false) : true);
  const requiredConfigReady = (input.requiredKeys || []).every(key => hasConfiguredValue(form[key]));
  const scheduleEnabled = scheduleKeys.length ? scheduleKeys.every(key => form[key] !== false) : true;
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
  if (key === 'subfill') return Boolean(form.subfill_enabled)
  if (key === 'backup') return Boolean(form.backup_enabled)
  if (key === 'logs') return Boolean(form.log_clean_enabled)
  if (key === 'updates') return updateMasterState.value === 'on'
  if (key === 'clean') return Boolean(form.plugin_uninstall_ids?.length > 0)
  return true
});
const heroEffectivelyEnabled = computed(() => pluginEnabled.value && heroEnabled.value);
const heroEffectivelyMixed = computed(() => pluginEnabled.value && heroMixed.value);
const currentHeroTitle = computed(() => {
  if (currentEffectiveState.value.code === EFFECTIVE_STATE.PLUGIN_DISABLED) return '插件已停用'
  return heroMixed.value ? currentHero.value.mixed : (heroEnabled.value ? currentHero.value.on : currentHero.value.off)
});
const heroStatusText = computed(() => {
  if (currentEffectiveState.value.code === EFFECTIVE_STATE.PLUGIN_DISABLED) return '已停用'
  return heroMixed.value ? '部分启用' : (heroEnabled.value ? '运行中' : '待启用')
});
const heroToggleLabel = computed(() => heroMixed.value
  ? `${currentHero.value.kicker}总开关，当前部分启用，点击后全部启用`
  : `${currentHero.value.kicker}总开关`);

const remoteBackupReady = computed(() => [
  form.backup_webdav_hostname,
  form.backup_webdav_login,
  form.backup_webdav_password,
].every(value => String(value || '').trim().length > 0));

function setHeroEnabled(value) {
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
    case 'subfill': toggle('subfill_enabled'); return
    case 'backup': toggle('backup_enabled'); return
    case 'logs': toggle('log_clean_enabled', 'log_clean_schedule_enabled'); return
    case 'updates':
      toggle('mp_update_enabled', 'mp_update_schedule_enabled');
      toggle('market_update_enabled', 'market_update_schedule_enabled');
      return
  }
}

const compactOperationalSubtabs = new Set(['subscribe', 'sites', 'hc', 'seedremove', 'dltagmain', 'logs']);
const hiddenDownloaderHelperCompatibilityFieldKeys = Object.freeze([
  'dltag_all_tags',
  'dltag_excluded_tags',
]);
const compactNotificationLabels = Object.freeze({
  subscribe_reminder_msgtype: '通知渠道',
  site_stat_notify_type: '通知渠道',
  health_check_notify_type: '通知渠道',
  dltag_notify_type: '通知渠道',
  log_clean_notify_type: '通知渠道',
  backup_notify_type: '通知渠道',
});

function compactOperationalCards(cardsBySubtab, fusionEnabled) {
  const result = { ...cardsBySubtab };
  for (const subtab of compactOperationalSubtabs) {
    const cards = cardsBySubtab[subtab] || [];
    const preserveExpandedFields = subtab === 'seedremove';
    const actions = cards.filter(card => card.type === 'actions');
    const compactCard = card => ({
      ...card,
      fields: (card.fields || []).map(field => {
        const isManagedChannel = Boolean(
          fusionEnabled &&
          card.type === 'notify' &&
          card.fusionManaged &&
          card.fusionChannelOnly &&
          compactNotificationLabels[field.key],
        );
        return {
          ...field,
          label: compactNotificationLabels[field.key] || field.label,
          fullRow: preserveExpandedFields ? Boolean(field.fullRow) : false,
          compactMulti: preserveExpandedFields ? false : Boolean(field.multiple || field.chips),
          compactSelection: Boolean(field.compactSelection),
          disabled: Boolean(field.disabled || isManagedChannel),
        }
      }),
    });
    if (subtab === 'seedremove') {
      result[subtab] = [
        ...cards.filter(card => card.type !== 'actions').map(compactCard),
        ...actions,
      ];
      continue
    }
    if (subtab === 'dltagmain') {
      const advancedCards = cards.filter(card => card.type === 'advanced').map(compactCard);
      const fields = cards
        .filter(card => card.type !== 'actions' && card.type !== 'advanced')
        .flatMap(card => compactCard(card).fields)
        .filter(field => !hiddenDownloaderHelperCompatibilityFieldKeys.includes(field.key));
      result[subtab] = [{
        type: 'section',
        icon: 'mdi-tune-variant',
        title: '配置项',
        grid: 'grid-2',
        fields,
        compactOperational: true,
      }, ...advancedCards, ...actions];
      continue
    }
    const fields = cards
      .filter(card => card.type !== 'actions')
      .flatMap(card => compactCard(card).fields);
    result[subtab] = [{
      type: 'section',
      icon: 'mdi-tune-variant',
      title: '配置项',
      grid: 'grid-2',
      fields,
      compactOperational: true,
    }, ...actions];
  }
  return result
}

const replicaCards = computed(() => {
  const onOff = v => v ? 'ON' : 'OFF';
  const valOr = (v, fb = '未配置') => v || fb;
  const arrCount = (arr, suffix = '个') => Array.isArray(arr) && arr.length ? `${arr.length} ${suffix}` : '未配置';
  const arrNames = (arr) => Array.isArray(arr) && arr.length ? arr.join('、') : '全部';
  const cronVal = v => v || '未设置';
  const dltagTasks = Array.isArray(form.dltag_tasks) ? form.dltag_tasks : [];
  const dltagTaggingActive = dltagTasks.includes('tagging') || Boolean(form.dltag_listen_download);
  const cards = composeSharedReplicaCards(bindReplicaCards(completeReplicaCards({
    fusion: [
      { type: 'section', icon: 'mdi-plus-circle-outline', title: '每日建卡', note: '使用标准 Cron 安排建卡和刷新，修改后保存即可重载计划。', grid: 'grid-2', fields: [
        { key: 'fusion_card_create_cron', icon: 'mdi-plus-circle-outline', label: '建卡时间', value: cronVal(form.fusion_card_create_cron) },
        { key: 'fusion_card_refresh_cron', icon: 'mdi-calendar-clock', label: '刷新时间', value: cronVal(form.fusion_card_refresh_cron) },
      ] },
      { type: 'actions', actions: [{ icon: 'mdi-plus-circle-outline', label: '立即建卡', path: 'create_tg_console_card' }, { icon: 'mdi-sync', label: '立即刷新', path: 'run_daily_report' }] },
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
      { type: 'actions', actions: [{ icon: 'mdi-send-outline', label: '手动推送', path: 'run_subscribe_reminder' }] },
    ],
    sites: [
      { type: 'section', icon: 'mdi-chart-line', title: '采集设置', note: '按 Cron 自动刷新站点数据；定时执行完成后发送结果。', grid: 'grid-2', fields: [
        { key: 'site_stat_cron', icon: 'mdi-calendar-clock', label: '统计时间', value: cronVal(form.site_stat_cron) },
        { key: 'site_stat_dashboard_type', icon: 'mdi-database-outline', label: '数据范围', value: form.site_stat_dashboard_type === 'total' ? '汇总' : '今日' },
      ] },
      { type: 'actions', actions: [{ icon: 'mdi-chart-line', label: '立即统计', path: 'run_site_stat' }] },
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
      { type: 'section', icon: 'mdi-bell-outline', title: '异常通知', note: '发现异常时通知', grid: 'grid-2', fields: [
        { key: 'health_check_notify_type', icon: 'mdi-email-outline', label: '消息类型', value: valOr(form.health_check_notify_type, 'Plugin'), disabled: Boolean(form.fusion_notify_enabled) },
      ] },
      { type: 'actions', actions: [{ icon: 'mdi-heart-pulse-solid', label: '立即巡检', path: 'run_health_check' }] },
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
      { type: 'actions', danger: true, actions: [
        { icon: 'mdi-play', label: '执行自动删种', path: 'run_seed_clean' },
      ] },
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
        { key: 'dltag_tracker_mappings', icon: 'mdi-link-variant', label: '映射规则', placeholder: '每行一条，例如 tracker.example.com => 站点标签；也支持 tracker.example.com = 站点标签', value: form.dltag_tracker_mappings ? '已配置' : '未配置', fullRow: true },
      ] },
      { type: 'actions', actions: [{ icon: 'mdi-play', label: '立即执行下载器助手', path: 'run_downloader_helper' }] },
    ],
    subfill: [
      { type: 'section', subfillScope: 'range', icon: 'mdi-auto-fix', title: '填充范围', note: '下载完成后，自动回填哪些订阅字段。', grid: 'grid-2', fields: [
        { key: 'subfill_details', icon: 'mdi-format-list-checks', label: '填充项', value: arrNames(form.subfill_details) },
      ] },
      { type: 'subfill_rules', icon: 'mdi-layers-outline', title: '二级分类规则', fields: [
        { key: 'subfill_category_enabled', icon: 'mdi-power-standby', label: '启用二级分类填充', value: onOff(form.subfill_category_enabled) },
        { key: 'subfill_category_confs', icon: 'mdi-code-tags', label: '规则配置', value: form.subfill_category_confs ? '已配置' : '未配置' },
      ] },
      { type: 'actions', actions: [
        { icon: 'mdi-history', label: '清理填充历史', path: 'subfill_clear_history' },
        { icon: 'mdi-broom', label: '清理已处理记录', path: 'subfill_clear_handled' },
      ] },
    ],
    backup: [
      { type: 'section', backupScope: 'local', icon: 'mdi-folder-outline', title: '本地备份', note: '本地：按 Cron 将配置与运行数据保存到本地，并自动清理超出保留数量的旧备份。', grid: 'grid-3', fields: [
        { key: 'backup_cron', icon: 'mdi-calendar-clock', label: '备份时间', value: cronVal(form.backup_cron), retainInCard: true },
        { key: 'backup_path', icon: 'mdi-folder-outline', label: '本地路径', value: valOr(form.backup_path, '/config/plugins/AgentOpsAssistant/Backup') },
        { key: 'backup_keep_count', icon: 'mdi-content-copy', label: '本地保留', value: `${form.backup_keep_count || 5} 份` },
        { key: 'backup_notify', icon: 'mdi-bell-outline', label: '定时执行后通知', value: onOff(form.backup_notify) },
        { key: 'backup_notify_type', icon: 'mdi-email-outline', label: '通知渠道', value: valOr(form.backup_notify_type, 'Plugin') },
      ] },
      { type: 'section', backupScope: 'remote', backupReady: remoteBackupReady.value, icon: 'mdi-cloud-outline', title: '远端备份', note: '远端：填写地址|账号|密码自动启用；清空任一必填项停用', grid: 'grid-2', fields: [
        { key: 'backup_webdav_hostname', icon: 'mdi-web', label: 'WebDAV 地址', value: form.backup_webdav_hostname ? '已配置' : '未配置' },
        { key: 'backup_webdav_login', icon: 'mdi-account-outline', label: '账号', value: form.backup_webdav_login ? '已配置' : '未配置' },
        { key: 'backup_webdav_password', icon: 'mdi-lock-outline', label: '密码', value: form.backup_webdav_password ? '已配置' : '未配置' },
        { key: 'backup_webdav_max_count', icon: 'mdi-content-copy', label: '远端保留', value: `${form.backup_webdav_max_count || 5} 份` },
        { key: 'backup_webdav_digest_auth', icon: 'mdi-shield-outline', label: 'Digest 认证', value: onOff(form.backup_webdav_digest_auth) },
        { key: 'backup_webdav_disable_check', icon: 'mdi-lock-check-outline', label: '跳过证书校验', value: onOff(form.backup_webdav_disable_check) },
      ] },
      { type: 'actions', actions: [{ icon: 'mdi-archive-arrow-up-outline', label: '立即备份', path: 'run_backup' }] },
    ],
    logs: [
      { type: 'section', icon: 'mdi-file-document-remove-outline', title: '配置项', grid: 'grid-2', fields: [
        { key: 'log_clean_cron', icon: 'mdi-calendar-clock', label: '清理时间', value: cronVal(form.log_clean_cron) },
        { key: 'log_clean_rows', icon: 'mdi-format-list-numbered', label: '保留行数', value: `${form.log_clean_rows || 300} 行` },
        { key: 'log_clean_selected_ids', icon: 'mdi-puzzle-outline', label: '限定插件', value: form.log_clean_selected_ids?.length ? `${form.log_clean_selected_ids.length} 个` : '全部' },
        { key: 'log_clean_notify', icon: 'mdi-bell-outline', label: '定时执行后通知', value: onOff(form.log_clean_notify) },
        { key: 'log_clean_notify_type', icon: 'mdi-email-outline', label: '通知渠道', value: valOr(form.log_clean_notify_type, 'Plugin') },
      ] },
      { type: 'actions', actions: [{ icon: 'mdi-broom', label: '立即清理', path: 'run_log_clean' }] },
    ],
    updates: [
      { type: 'module', module: 'mp_update', icon: 'mdi-update', title: 'MoviePilot 系统更新', grid: 'grid-2', fields: [
        { key: 'mp_update_cron', icon: 'mdi-calendar-clock', label: '系统检查时间', value: cronVal(form.mp_update_cron) },
        { key: 'mp_update_types', icon: 'mdi-cube-outline', label: '检查范围', value: arrNames(form.mp_update_types) },
      ], actions: [{ icon: 'mdi-update', label: '检查系统更新', path: 'run_mp_update' }] },
      { type: 'module', module: 'market_update', icon: 'mdi-cloud-upload-outline', title: '插件库更新', grid: 'grid-2', fields: [
        { key: 'market_update_cron', icon: 'mdi-calendar-clock', label: '插件库检查时间', value: cronVal(form.market_update_cron) },
        { key: 'market_update_strategy', icon: 'mdi-auto-fix', label: '处理方式', value: valOr(form.market_update_strategy, 'check') },
        { key: 'market_update_install_ids', icon: 'mdi-puzzle-outline', label: '仅更新这些插件', value: arrNames(form.market_update_install_ids), hidden: form.market_update_strategy !== 'install' },
        { key: 'market_update_exclude_ids', icon: 'mdi-shield-outline', label: '排除插件', value: arrNames(form.market_update_exclude_ids), hidden: form.market_update_strategy !== 'install' },
        { key: 'update_scheduled_notify', icon: 'mdi-bell-outline', label: '定时执行后通知', value: onOff(form.update_scheduled_notify) },
        { key: 'update_notify_type', icon: 'mdi-email-outline', label: '通知渠道', value: valOr(form.update_notify_type, 'Plugin') },
      ], actions: [{
        icon: 'mdi-cloud-upload-outline',
        label: form.market_update_strategy === 'install'
          ? '同步并更新插件'
          : form.market_update_strategy === 'sync' ? '同步插件库' : '检查插件库',
        path: 'run_market_update',
      }] },
    ],
    clean: [
      { type: 'section', icon: 'mdi-alert-outline', title: '卸载设置', grid: 'grid-4', fields: [
        { key: 'plugin_uninstall_ids', icon: 'mdi-puzzle-outline', label: '目标插件', value: arrCount(form.plugin_uninstall_ids) },
        { key: 'plugin_uninstall_remove_plugin', icon: 'mdi-delete-outline', label: '卸载插件', value: onOff(form.plugin_uninstall_remove_plugin) },
        { key: 'plugin_uninstall_clear_config', icon: 'mdi-cog-outline', label: '清除配置', value: onOff(form.plugin_uninstall_clear_config) },
        { key: 'plugin_uninstall_clear_data', icon: 'mdi-database-outline', label: '清除数据', value: onOff(form.plugin_uninstall_clear_data) },
        { key: 'plugin_uninstall_delete_source', icon: 'mdi-code-tags', label: '删除源码', value: onOff(form.plugin_uninstall_delete_source) },
      ], danger: true },
      {
        type: 'actions',
        danger: true,
        actions: [{ icon: 'mdi-alert-outline', label: '执行卸载', path: 'run_plugin_uninstall' }],
      },
    ],
  }), replicaItemSources.value));
  return compactOperationalCards(cards, Boolean(form.fusion_notify_enabled))
});
const currentReplicaCards = computed(() => replicaCards.value[activeSub.value] || replicaCards.value.fusion);
const settingCards = computed(() => currentReplicaCards.value.filter(card => card.type !== 'actions'));
const actionCards = computed(() => currentReplicaCards.value.filter(card => card.type === 'actions'));
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
  updates: '系统更新与插件库更新分别执行，共用结果通知',
  clean: '确认后执行不可逆卸载',
};
const currentActionHint = computed(() => configActionHints[activeSub.value] || '');
const fusionTakeoverNoticeBySub = Object.freeze({
  server: '融合通知已接管媒体通知，消息将统一汇入 Telegram 卡片。',
  subscribe: '融合通知仅接管通知渠道；检查时间和订阅类型仍可编辑。',
  sites: '融合通知仅接管通知渠道；统计时间和数据范围仍可编辑。',
  hc: '融合通知仅接管通知渠道；巡查时间、阈值和巡查范围仍可编辑。',
  seedremove: '融合通知仅接管自动删种的通知渠道；执行时间和清理规则仍可编辑。',
  dltagmain: '融合通知已接管下载器助手的通知渠道，任务和清理设置仍由你控制。',
  logs: '融合通知只接管日志清理的通知渠道；Cron、清理范围和定时执行后通知仍由你控制。',
  updates: '融合通知只接管更新检查的通知渠道；Cron、检查范围、处理方式和定时执行后通知仍由你控制。',
});
const fusionTakeoverNotice = computed(() => {
  if (!form.fusion_notify_enabled) return null
  if (activeSub.value === 'dltagmain' && !form.dltag_scheduled_notify) return null
  return fusionTakeoverNoticeBySub[activeSub.value] || null
});
const seedCleanRiskNotice = computed(() => activeSub.value === 'seedremove'
  ? '自动删种会按当前筛选条件暂停或删除任务；执行前请确认动作与范围。'
  : null);

const seedCleanConfirmOpen = ref$1(false);
const downloaderHelperConfirmOpen = ref$1(false);
const pluginUninstallConfirmOpen = ref$1(false);
const seedCleanPortalStyle = ref$1({});
const downloaderHelperPreviewItems = computed(() => action.downloaderHelperPreview?.items || []);
const selectedPluginUninstallItems = computed(() => {
  const selected = Array.isArray(form.plugin_uninstall_ids) ? form.plugin_uninstall_ids : [];
  const installed = installedPlugins.value || [];
  return selected.map(id => {
    const value = String(id);
    const item = installed.find(candidate => String(candidate?.value ?? candidate?.id ?? candidate?.title ?? candidate) === value);
    return { value, title: String(item?.title ?? item?.name ?? value) }
  })
});
const pluginUninstallActionItems = computed(() => [
  { key: 'plugin_uninstall_remove_plugin', label: '卸载插件本体', detail: '移出已安装列表并停止运行实例' },
  { key: 'plugin_uninstall_clear_config', label: '清除插件配置', detail: '删除 MoviePilot 保存的插件配置' },
  { key: 'plugin_uninstall_clear_data', label: '清除插件数据', detail: '删除插件运行数据' },
  { key: 'plugin_uninstall_delete_source', label: '删除本地源码', detail: '删除本地插件源码目录' },
].filter(item => Boolean(form[item.key])));
const seedCleanActionMeta = computed(() => ({
  pause: { label: '暂停种子', confirm: '确认暂停', risk: '所选种子将停止上传和下载，可在下载器中重新开始。' },
  delete: { label: '删除种子', confirm: '确认删除', risk: '所选任务将从下载器移除，但保留已下载文件。' },
  deletefile: { label: '删除种子和文件', confirm: '确认删除种子和文件', risk: '所选任务及其已下载文件将被永久删除，无法恢复。' },
}[String(form.seedclean_action || 'pause')] || { label: '处理种子', confirm: '确认执行', risk: '将按当前动作处理匹配条件的种子。' }));
const seedCleanFilterSummary = computed(() => {
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

function openSeedCleanConfirmation() {
  const message = actionDisabledReason.value || actionComponentDisabledMessage('run_seed_clean');
  if (message) {
    action.ok = false;
    action.message = message;
    return
  }
  if (!Array.isArray(form.seedclean_downloaders) || !form.seedclean_downloaders.length) {
    action.ok = false;
    action.message = '请先选择下载器。';
    return
  }
  if (seedCleanFilterSummary.value === '未设置筛选条件') {
    action.ok = false;
    action.message = '请至少设置一项筛选条件。';
    return
  }
  if (typeof window !== 'undefined' && configRoot.value) {
    const computedStyle = window.getComputedStyle(configRoot.value);
    seedCleanPortalStyle.value = Array.from(computedStyle).reduce((tokens, name) => {
      if (name.startsWith('--aoa-') || name.startsWith('--v-')) tokens[name] = computedStyle.getPropertyValue(name);
      return tokens
    }, {});
  }
  seedCleanConfirmOpen.value = true;
}

function openPluginUninstallConfirmation() {
  const message = actionDisabledReason.value || actionComponentDisabledMessage('run_plugin_uninstall');
  if (message) {
    action.ok = false;
    action.message = message;
    return
  }
  if (!selectedPluginUninstallItems.value.length) {
    action.ok = false;
    action.message = '请先选择要卸载的插件。';
    return
  }
  if (!pluginUninstallActionItems.value.length) {
    action.ok = false;
    action.message = '请至少选择一项卸载或清理操作。';
    return
  }
  if (typeof window !== 'undefined' && configRoot.value) {
    const computedStyle = window.getComputedStyle(configRoot.value);
    seedCleanPortalStyle.value = Array.from(computedStyle).reduce((tokens, name) => {
      if (name.startsWith('--aoa-') || name.startsWith('--v-')) tokens[name] = computedStyle.getPropertyValue(name);
      return tokens
    }, {});
  }
  pluginUninstallConfirmOpen.value = true;
}

async function confirmSeedCleanExecution() {
  seedCleanConfirmOpen.value = false;
  await runAction('run_seed_clean', '执行自动删种');
}

async function confirmDownloaderHelperExecution() {
  downloaderHelperConfirmOpen.value = false;
  await runAction('run_downloader_helper', '执行下载器助手');
}

async function confirmPluginUninstallExecution() {
  pluginUninstallConfirmOpen.value = false;
  await runAction('run_plugin_uninstall', '执行卸载');
}

async function triggerConfigAction(item) {
  if (!item) return
  if (item.path === 'run_seed_clean') {
    openSeedCleanConfirmation();
    return
  }
  if (item.path === 'run_plugin_uninstall') {
    openPluginUninstallConfirmation();
    return
  }
  await runAction(item.path, item.label);
  if (item.path === 'run_downloader_helper' && action.downloaderHelperPreview?.confirm_required) {
    downloaderHelperConfirmOpen.value = true;
  }
}

watch$1(() => [
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
  seedCleanConfirmOpen.value = false;
}, { deep: true });

watch$1(() => [form.dltag_downloaders, form.dltag_tasks], () => {
  action.downloaderHelperPreview = null;
  downloaderHelperConfirmOpen.value = false;
}, { deep: true });

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

const seedCleanStatusDictionaries = Object.freeze([
  {
    key: 'qb',
    title: 'qB 任务状态字典',
    field: 'seedclean_torrentstates',
    entries: [
      { key: 'downloading', label: '正在下载-传输数据' },
      { key: 'stalledDL', label: '正在下载_未建立连接' },
      { key: 'uploading', label: '正在上传-传输数据' },
      { key: 'stalledUP', label: '正在上传-未建立连接' },
      { key: 'error', label: '暂停-发生错误' },
      { key: 'pausedDL', label: '暂停-下载未完成' },
      { key: 'pausedUP', label: '暂停-下载完成' },
      { key: 'missingFiles', label: '暂停-文件丢失' },
      { key: 'checkingDL', label: '检查中-下载未完成' },
      { key: 'checkingUP', label: '检查中-下载完成' },
      { key: 'checkingResumeData', label: '检查中-启动时恢复数据' },
      { key: 'forcedDL', label: '强制下载-忽略队列' },
      { key: 'queuedDL', label: '等待下载-排队' },
      { key: 'forcedUP', label: '强制上传-忽略队列' },
      { key: 'queuedUP', label: '等待上传-排队' },
      { key: 'allocating', label: '分配磁盘空间' },
      { key: 'metaDL', label: '获取元数据' },
      { key: 'moving', label: '移动文件' },
      { key: 'unknown', label: '未知状态' },
    ],
  },
  {
    key: 'tr',
    title: 'TR 任务状态字典',
    field: 'seedclean_trtorrentstates',
    entries: [
      { key: '0 / stopped', label: '停止' },
      { key: '1 / check_pending', label: '校验队列' },
      { key: '2 / checking', label: '校验中' },
      { key: '3 / download_pending', label: '下载队列' },
      { key: '4 / downloading', label: '下载中' },
      { key: '5 / seed_pending', label: '做种队列' },
      { key: '6 / seeding', label: '做种' },
      { key: 'error', label: '错误' },
    ],
  },
]);

const CompactSettingCard = defineComponent({
  name: 'CompactSettingCard',
  props: {
    card: { type: Object, required: true },
    activeSub: { type: String, required: true },
    effectiveState: { type: String, required: true },
    embedded: { type: Boolean, default: false },
  },
  emits: ['run'],
  setup(props, { emit }) {
    const renderDictionary = () => props.card.dictionary === 'seedclean-status'
      ? h('aside', { class: 'aoa-seedclean-status-dictionary', 'data-seedclean-status-dictionary': '' }, [
          ...seedCleanStatusDictionaries.map(dictionary => h('section', {
            key: dictionary.key,
            class: 'aoa-seedclean-status-dictionary__group',
            [`data-seedclean-${dictionary.key}-status-dictionary`]: '',
          }, [
            h('h4', dictionary.title),
            h('ul', dictionary.entries.map((entry, index) => h('li', {
              key: entry.key,
              'data-seedclean-status-entry': '',
              'data-seedclean-status-key': entry.key,
              'data-seedclean-status-index': String(index),
              'data-seedclean-status-field': dictionary.field,
            }, `${entry.key}：${entry.label}`))),
          ])),
        ])
      : null;
    const renderFields = () => {
      const fields = (props.card.fields || []).filter(field => isReplicaFieldVisible(field, form));
      const children = fields.flatMap(field => {
        const groupHeading = field.groupLabel
          ? h('h4', {
              key: `${props.activeSub}-group-${field.layoutGroup}`,
              class: 'aoa-config-field-group',
              'data-field-group-heading': field.layoutGroup,
            }, field.groupLabel)
          : null;
        const fieldRow = h(ConfigFieldRow, {
          key: `${props.activeSub}-${field.key}`,
          'data-field-layout-group': field.layoutGroup || undefined,
          ...createReplicaFieldControlProps(form, {
            ...field,
            hideInlineLabel: true,
            hideDetails: true,
            density: 'compact',
          }),
        });
        return groupHeading ? [groupHeading, fieldRow] : [fieldRow]
      });
      return h('div', { class: ['aoa-design-field-grid', `aoa-design-field-grid--${props.card.grid || 'grid-3'}`] }, children)
    };
    return () => {
      if (props.card.type === 'advanced' && (!props.embedded || props.card.embeddedDrawer)) {
        return h('details', {
          class: ['aoa-design-advanced', { 'aoa-design-advanced--embedded': props.embedded }],
          'data-html-advanced': '',
          'data-seedclean-filter-drawer': props.card.dictionary === 'seedclean-status' ? '' : undefined,
          'data-dltag-tracker-drawer': props.card.drawer === 'dltag-tracker' ? '' : undefined,
          'data-default-open': 'false',
          'data-effective-state': props.effectiveState,
        }, [
          h('summary', [
            h('span', [compactIcon(props.card.icon, 'aoa-mdi-icon'), props.card.title]),
            h('svg', { class: 'aoa-design-advanced__chevron aoa-mdi-icon', viewBox: '0 0 24 24', width: '15', height: '15', 'aria-hidden': 'true' }, [h('path', { d: mdiCogOutline, fill: 'currentColor' })]),
          ]),
          h('div', { class: 'aoa-design-advanced-content' }, [
            props.card.note ? h('div', { class: 'aoa-design-section-note' }, props.card.note) : null,
            renderFields(),
            renderDictionary(),
          ]),
        ])
      }
      const isPeerSection = Boolean(props.card.backupScope || props.card.type === 'module');
      return h('section', {
        class: ['aoa-design-section-card', {
          'aoa-design-section-card--danger': props.card.danger,
          'aoa-update-module-card': props.card.type === 'module',
          'aoa-design-section-card--embedded': props.embedded,
          'aoa-design-section-card--peer': isPeerSection,
        }],
        'data-html-replica-card': props.embedded && !isPeerSection ? undefined : '',
        'data-flat-config-section': props.embedded && !isPeerSection ? '' : undefined,
        'data-backup-card': props.card.backupScope || undefined,
        'data-backup-enabled': props.card.backupScope === 'remote' ? String(!!props.card.backupReady) : undefined,
        'data-seedclean-primary-card': props.card.seedcleanPrimary ? '' : undefined,
        'data-subfill-range-card': props.card.subfillScope === 'range' ? '' : undefined,
        'data-section-tone': props.card.danger ? 'danger' : 'neutral',
        'data-update-module-card': props.card.type === 'module' ? props.card.module : undefined,
        'data-effective-state': props.effectiveState,
      }, [
        isPeerSection
          ? h('div', { class: 'aoa-design-section-title' }, [
              h('span', { class: 'aoa-design-section-title__leading', 'aria-hidden': 'true' }, [
                compactIcon(props.card.icon, 'aoa-mdi-icon aoa-mdi-icon--section'),
              ]),
              h('span', { class: 'aoa-design-section-title__text' }, props.card.title),
              h('span', { class: 'aoa-design-section-title__trailing' }, [
                props.card.backupScope === 'remote'
                  ? h('small', { class: ['aoa-design-section-status', props.card.backupReady ? 'aoa-design-section-status--on' : 'aoa-design-section-status--off'] }, props.card.backupReady ? '已启用' : '未启用')
                  : null,
              ]),
            ])
          : null,
        isPeerSection && props.card.note ? h('div', { class: 'aoa-design-section-note' }, props.card.note) : null,
        renderFields(),
        props.card.actions?.length
          ? h(CompactActionRow, { card: { type: 'actions', actions: props.card.actions }, pluginEnabled: pluginEnabled.value, effectiveState: props.effectiveState, onRun: item => emit('run', item) })
          : null,
      ])
    }
  },
});

const CompactActionRow = defineComponent({
  name: 'CompactActionRow',
  props: { card: { type: Object, required: true }, pluginEnabled: { type: Boolean, default: true }, effectiveState: { type: String, default: '' } },
  emits: ['run'],
  setup(props, { emit }) {
    return () => {
      const actionButtons = (props.card.actions || []).map(actionItem => {
        const disabledBySelection = actionItem.path === 'run_plugin_uninstall'
          && (!Array.isArray(form.plugin_uninstall_ids) || form.plugin_uninstall_ids.length === 0);
        const disabledByPlugin = !props.pluginEnabled;
        const isDisabled = disabledByPlugin || disabledBySelection || action.running === actionItem.path;
        const title = disabledByPlugin
          ? '插件已停用，开启总开关后可执行'
          : disabledBySelection
          ? '请先选择要卸载的插件'
          : '';
        const buttonLabel = action.running === actionItem.path
          ? '正在执行...'
          : actionItem.label;
        return h('button', {
          key: actionItem.label,
          type: 'button',
          class: ['aoa-design-action-btn', {
            'aoa-design-action-btn--danger': props.card.danger,
            'aoa-design-action-btn--disabled': isDisabled,
          }],
          disabled: isDisabled,
          title,
          'data-config-action-path': actionItem.path,
          'data-effective-state': props.effectiveState || undefined,
          onClick: () => {
            if (isDisabled) return
            emit('run', actionItem);
          },
        }, [actionIcon(actionItem.icon), h('span', buttonLabel)])
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

watch$1([() => props.initialConfig, () => props.configRecordState], ([value, configRecordState]) => {
  Object.keys(form).forEach(key => delete form[key]);
  const rawConfig = value || {};
  Object.assign(form, normalizeCurrentConfig(defaults), normalizeCurrentConfig(rawConfig));
  if (!Object.prototype.hasOwnProperty.call(rawConfig, 'dltag_cron')) {
    form.dltag_cron = DEFAULT_DLTAG_CRON;
  }
  const inheritSchedule = (scheduleKey, enabledKey) => {
    if (!Object.prototype.hasOwnProperty.call(rawConfig, scheduleKey)) {
      form[scheduleKey] = !!form[enabledKey];
    }
  };
  inheritSchedule('subscribe_reminder_schedule_enabled', 'subscribe_reminder_enabled');
  inheritSchedule('health_check_schedule_enabled', 'health_check_enabled');
  inheritSchedule('log_clean_schedule_enabled', 'log_clean_enabled');
  inheritSchedule('mp_update_schedule_enabled', 'mp_update_enabled');
  inheritSchedule('market_update_schedule_enabled', 'market_update_enabled');
  inheritSchedule('seedclean_schedule_enabled', 'seedclean_enabled');
  const toArr = v => typeof v === 'string' ? v.split(',').map(s => s.trim()).filter(Boolean) : (Array.isArray(v) ? v : []);
  form.subscribe_reminder_subtype = toArr(form.subscribe_reminder_subtype);
  form.mp_update_types = toArr(form.mp_update_types);
  form.plugin_uninstall_ids = toArr(form.plugin_uninstall_ids);
  form.log_clean_selected_ids = toArr(form.log_clean_selected_ids);
  form.market_update_install_ids = toArr(form.market_update_install_ids);
  form.market_update_exclude_ids = toArr(form.market_update_exclude_ids);
  form.seedclean_downloaders = toArr(form.seedclean_downloaders);
  form.subfill_details = toArr(form.subfill_details);
  form.msgnotify_types = toArr(form.msgnotify_types);
  form.msgnotify_servers = toArr(form.msgnotify_servers);
  form.dltag_downloaders = toArr(form.dltag_downloaders);
  form.dltag_tasks = toArr(form.dltag_tasks);
  form.dltag_all_tags = toArr(form.dltag_all_tags);
  form.dltag_excluded_tags = toArr(form.dltag_excluded_tags);
  form.health_check_items = toArr(form.health_check_items);
  form.health_check_database_targets = toArr(form.health_check_database_targets);
  form.health_check_storage_targets = toArr(form.health_check_storage_targets);
  form.health_check_directory_targets = toArr(form.health_check_directory_targets);
}, { immediate: true, deep: true });

async function saveConfig() {
  if (!subfillRulesValid.value) {
    action.message = '二级分类规则存在错误，请先修正后再保存';
    action.ok = false;
    return
  }
  const payload = emitConfigSave(emit, form);
  if (props.api?.put) {
    await props.api.put(`plugin/${props.pluginId}`, payload);
  } else if (typeof props.api === 'function') {
    await props.api({ method: 'put', url: `plugin/${props.pluginId}`, data: payload });
  }
}

function selectMain(key) {
  if (activeMain.value === key) return
  activeMain.value = key;
  activeSub.value = subTabs[key]?.[0]?.key || '';
}

function revealCategoryItem(target, behavior = 'smooth') {
  const container = target?.closest?.('[data-config-nav-scroll]');
  if (!container) return
  const containerRect = container.getBoundingClientRect();
  const targetRect = target.getBoundingClientRect();
  const inset = 8;
  let nextLeft = container.scrollLeft;
  if (targetRect.left < containerRect.left + inset) {
    nextLeft -= containerRect.left + inset - targetRect.left;
  } else if (targetRect.right > containerRect.right - inset) {
    nextLeft += targetRect.right - containerRect.right + inset;
  }
  if (Math.abs(nextLeft - container.scrollLeft) > 1) {
    container.scrollTo({ left: nextLeft, behavior });
  }
}

function revealActiveCategories(behavior = 'smooth') {
  nextTick(() => {
    revealCategoryItem(mainNav.value?.querySelector('[aria-selected="true"]'), behavior);
    revealCategoryItem(subtabList.value?.querySelector('[aria-selected="true"]'), behavior);
  });
}

watch$1([activeMain, activeSub], () => revealActiveCategories());
watch$1(activeSub, value => {
  if (value !== 'subfill') subfillProjectionOpen.value = false;
});

function switchPluginAppNav(navKey) {
  if (typeof window === 'undefined') return false
  const pluginAppPrefix = `#/plugin-app/${props.pluginId}/`;
  if (!window.location.hash.startsWith(pluginAppPrefix)) return false
  window.location.hash = `${pluginAppPrefix}${navKey}`;
  return true
}

function openDashboard() {
  if (switchPluginAppNav('main')) return
  emit('switch');
}

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

onMounted$1(() => {
  bindDialogScrollHost();
  revealActiveCategories('auto');
  loadInstalledPlugins();
  loadTgConsoleStatus();
  loadBackupArchives();
  loadWebdavBackupArchives();
  loadPluginMarkets();
  loadDownloaders();
  loadMediaservers();
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
    "data-effective-state": currentEffectiveState.value.code
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
        _cache[15] || (_cache[15] = _createElementVNode("span", { class: "aoa-config-brand-copy" }, [
          _createElementVNode("strong", null, "MP 运维助手"),
          _createElementVNode("small", null, "配置中心")
        ], -1))
      ]),
      _createElementVNode("div", _hoisted_3, [
        _createElementVNode("div", _hoisted_4, [
          _cache[17] || (_cache[17] = _createElementVNode("span", { class: "aoa-config-master-switch__label" }, "插件总开关", -1)),
          _createElementVNode("button", {
            type: "button",
            class: _normalizeClass(["aoa-toggle-switch", { 'aoa-toggle-switch--on': form.enabled }]),
            role: "switch",
            "aria-checked": !!form.enabled,
            "aria-label": '插件总开关',
            onClick: _cache[0] || (_cache[0] = $event => (form.enabled = !form.enabled))
          }, [...(_cache[16] || (_cache[16] = [
            _createElementVNode("span", { class: "aoa-toggle-switch__thumb" }, null, -1)
          ]))], 10, _hoisted_5)
        ]),
        _createElementVNode("button", {
          type: "button",
          class: "aoa-config-ghost-btn",
          "data-config-dashboard-button": "",
          title: '仪表盘',
          "aria-label": '仪表盘',
          onClick: openDashboard
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
          _cache[18] || (_cache[18] = _createElementVNode("span", null, "仪表盘", -1))
        ])
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
          class: _normalizeClass(["aoa-config-main-tab", { 'aoa-config-main-tab--active': activeMain.value === item.key }]),
          role: "tab",
          "aria-selected": activeMain.value === item.key,
          "data-config-main-tab": item.key,
          "data-effective-state": mainEffectiveState(item.key),
          onClick: $event => (selectMain(item.key)),
          onFocus: _cache[1] || (_cache[1] = $event => (revealCategoryItem($event.currentTarget, 'auto')))
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
            }, null, 8, _hoisted_8)
          ], 12, _hoisted_7)),
          _createElementVNode("span", null, _toDisplayString(item.title), 1)
        ], 42, _hoisted_6))
      }), 128))
    ], 512),
    _createElementVNode("div", _hoisted_9, [
      _createElementVNode("div", {
        ref_key: "subtabList",
        ref: subtabList,
        class: "aoa-subtab-list",
        "data-config-nav-scroll": "sub",
        role: "tablist",
        "aria-label": `${currentMain.value.title} 二级分类`
      }, [
        (_openBlock$1(true), _createElementBlock(_Fragment, null, _renderList(currentSubs.value, (sub) => {
          return (_openBlock$1(), _createElementBlock("button", {
            key: sub.key,
            type: "button",
            id: `config-tab-${sub.key}`,
            class: _normalizeClass(["aoa-subtab", { 'aoa-subtab--active': activeSub.value === sub.key }]),
            role: "tab",
            "aria-selected": activeSub.value === sub.key,
            "aria-controls": `config-panel-${sub.key}`,
            "data-config-subtab": sub.key,
            "data-effective-state": effectiveStateFor(sub.key).code,
            onClick: $event => (activeSub.value = sub.key),
            onFocus: _cache[2] || (_cache[2] = $event => (revealCategoryItem($event.currentTarget, 'auto')))
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
              }, null, 8, _hoisted_13)
            ], 12, _hoisted_12)),
            _createElementVNode("span", null, _toDisplayString(sub.title), 1)
          ], 42, _hoisted_11))
        }), 128))
      ], 8, _hoisted_10),
      (currentSubTitle.value)
        ? (_openBlock$1(), _createElementBlock("div", _hoisted_14, _toDisplayString(currentSubTitle.value), 1))
        : _createCommentVNode("", true)
    ]),
    _createElementVNode("main", {
      id: `config-panel-${activeSub.value}`,
      class: "aoa-config-scroll",
      "data-config-scroll": "",
      "aria-labelledby": `config-tab-${activeSub.value}`,
      "data-config-active-sub": activeSub.value,
      "data-effective-state": currentEffectiveState.value.code
    }, [
      _createElementVNode("section", {
        class: "aoa-config-hero-card",
        "data-config-active-card": "",
        "aria-live": "polite",
        "data-effective-state": currentEffectiveState.value.code
      }, [
        _createElementVNode("div", _hoisted_17, [
          _createElementVNode("span", _hoisted_18, [
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
              }, null, 8, _hoisted_20)
            ], 8, _hoisted_19))
          ]),
          _createElementVNode("span", _hoisted_21, [
            _createElementVNode("span", _hoisted_22, _toDisplayString(currentHero.value.kicker), 1),
            _createElementVNode("strong", _hoisted_23, _toDisplayString(currentHeroTitle.value), 1),
            _createElementVNode("small", _hoisted_24, _toDisplayString(currentHero.value.desc), 1)
          ])
        ]),
        (activeSub.value !== 'clean')
          ? (_openBlock$1(), _createElementBlock("div", _hoisted_25, [
              _createElementVNode("span", {
                class: _normalizeClass(["aoa-config-status-badge", { 'aoa-config-status-badge--on': heroEffectivelyEnabled.value, 'aoa-config-status-badge--mixed': heroEffectivelyMixed.value }])
              }, _toDisplayString(heroStatusText.value), 3),
              _createElementVNode("button", {
                type: "button",
                class: _normalizeClass(["aoa-toggle-switch aoa-toggle-switch--hero", { 'aoa-toggle-switch--on': heroEffectivelyEnabled.value }]),
                role: "switch",
                "aria-checked": !!heroEnabled.value,
                "aria-label": heroToggleLabel.value,
                "data-config-aggregate-state": activeSub.value === 'updates' ? updateMasterState.value : undefined,
                onClick: _cache[3] || (_cache[3] = $event => (setHeroEnabled(!heroEnabled.value)))
              }, [...(_cache[19] || (_cache[19] = [
                _createElementVNode("span", { class: "aoa-toggle-switch__thumb" }, null, -1)
              ]))], 10, _hoisted_26)
            ]))
          : (_openBlock$1(), _createElementBlock("div", _hoisted_27, [...(_cache[20] || (_cache[20] = [
              _createElementVNode("span", { class: "aoa-config-status-badge" }, "高风险操作", -1)
            ]))]))
      ], 8, _hoisted_16),
      (fusionTakeoverNotice.value)
        ? (_openBlock$1(), _createElementBlock("div", _hoisted_28, [
            (_openBlock$1(), _createElementBlock("svg", _hoisted_29, [
              _createElementVNode("path", {
                d: iconPath('mdi-shield-check-outline'),
                fill: "currentColor"
              }, null, 8, _hoisted_30)
            ])),
            _createElementVNode("span", null, _toDisplayString(fusionTakeoverNotice.value), 1)
          ]))
        : _createCommentVNode("", true),
      (seedCleanRiskNotice.value)
        ? (_openBlock$1(), _createElementBlock("div", _hoisted_31, [
            (_openBlock$1(), _createElementBlock("svg", _hoisted_32, [
              _createElementVNode("path", {
                d: iconPath('mdi-alert-outline'),
                fill: "currentColor"
              }, null, 8, _hoisted_33)
            ])),
            _createElementVNode("span", null, _toDisplayString(seedCleanRiskNotice.value), 1)
          ]))
        : _createCommentVNode("", true),
      _createElementVNode("div", {
        class: "aoa-design-replica-stack",
        "data-html-replica-stack": "",
        "data-subfill-layout-container": activeSub.value === 'subfill' ? '' : undefined
      }, [
        _createElementVNode("section", {
          class: _normalizeClass(["aoa-settings-form-surface", {
              'aoa-settings-form-surface--peer': activeSub.value === 'backup' || activeSub.value === 'updates',
              'aoa-settings-form-surface--compact-operational': _unref(compactOperationalSubtabs).has(activeSub.value),
            }]),
          "data-settings-form-surface": "",
          "data-subfill-config-surface": activeSub.value === 'subfill' ? '' : undefined,
          "data-subfill-projection-open": activeSub.value === 'subfill' ? String(subfillProjectionOpen.value) : undefined,
          "data-compact-operational-surface": _unref(compactOperationalSubtabs).has(activeSub.value) ? activeSub.value : undefined,
          "data-effective-state": currentEffectiveState.value.code
        }, [
          (_openBlock$1(true), _createElementBlock(_Fragment, null, _renderList(settingCards.value, (card, index) => {
            return (_openBlock$1(), _createElementBlock(_Fragment, {
              key: `${activeSub.value}-setting-${index}`
            }, [
              (card.type === 'schedule')
                ? (_openBlock$1(), _createBlock$1(ScheduleCard, {
                    key: 0,
                    title: card.title,
                    note: card.note,
                    icon: card.icon,
                    fields: card.fields,
                    values: form,
                    "master-key": card.masterKey,
                    "schedule-key": card.scheduleKey,
                    "effective-state": currentEffectiveState.value.code,
                    embedded: ""
                  }, null, 8, ["title", "note", "icon", "fields", "values", "master-key", "schedule-key", "effective-state"]))
                : (card.type === 'notify')
                  ? (_openBlock$1(), _createBlock$1(NotifyCard, {
                      key: 1,
                      title: card.title,
                      note: card.note,
                      icon: card.icon,
                      fields: card.fields,
                      values: form,
                      "master-key": card.masterKey,
                      "result-key": card.resultKey,
                      "result-keys": card.resultKeys,
                      dependencies: card.dependencies,
                      "off-values": card.offValues,
                      locked: !!card.fusionManaged && !!form.fusion_notify_enabled,
                      "channel-only-lock": !!card.fusionChannelOnly,
                      "effective-state": currentEffectiveState.value.code,
                      embedded: ""
                    }, null, 8, ["title", "note", "icon", "fields", "values", "master-key", "result-key", "result-keys", "dependencies", "off-values", "locked", "channel-only-lock", "effective-state"]))
                  : (card.type === 'subfill_rules')
                    ? (_openBlock$1(), _createBlock$1(SubfillRuleEditor, {
                        key: 2,
                        values: form,
                        "data-effective-state": currentEffectiveState.value.code,
                        onProjectionChange: _cache[4] || (_cache[4] = $event => (subfillProjectionOpen.value = $event))
                      }, null, 8, ["values", "data-effective-state"]))
                    : (_openBlock$1(), _createBlock$1(_unref(CompactSettingCard), {
                        key: 3,
                        card: card,
                        "active-sub": activeSub.value,
                        "effective-state": currentEffectiveState.value.code,
                        embedded: "",
                        onRun: triggerConfigAction
                      }, null, 8, ["card", "active-sub", "effective-state"]))
            ], 64))
          }), 128))
        ], 10, _hoisted_35),
        (_openBlock$1(true), _createElementBlock(_Fragment, null, _renderList(actionCards.value, (card, index) => {
          return (_openBlock$1(), _createBlock$1(_unref(CompactActionRow), {
            key: `${activeSub.value}-action-${index}`,
            card: card,
            "plugin-enabled": pluginEnabled.value,
            "effective-state": currentEffectiveState.value.code,
            onRun: triggerConfigAction
          }, null, 8, ["card", "plugin-enabled", "effective-state"]))
        }), 128))
      ], 8, _hoisted_34)
    ], 8, _hoisted_15),
    (_openBlock$1(), _createBlock$1(_Teleport, { to: "body" }, [
      (seedCleanConfirmOpen.value)
        ? (_openBlock$1(), _createElementBlock("div", {
            key: 0,
            class: _normalizeClass(["aoa-seedclean-confirm-overlay aoa-root", _unref(rootThemeClass)]),
            style: _normalizeStyle(seedCleanPortalStyle.value),
            "data-seedclean-confirm-dialog": "",
            role: "presentation",
            onClick: _cache[7] || (_cache[7] = _withModifiers($event => (seedCleanConfirmOpen.value = false), ["self"]))
          }, [
            _createElementVNode("section", _hoisted_36, [
              _createElementVNode("header", _hoisted_37, [
                _createElementVNode("div", null, [
                  _cache[21] || (_cache[21] = _createElementVNode("span", { class: "aoa-seedclean-confirm-dialog__kicker" }, "请确认本次处理", -1)),
                  _createElementVNode("h2", _hoisted_38, _toDisplayString(seedCleanActionMeta.value.label), 1)
                ]),
                _createElementVNode("button", {
                  type: "button",
                  class: "aoa-seedclean-confirm-dialog__close",
                  "aria-label": "关闭",
                  title: "关闭",
                  onClick: _cache[5] || (_cache[5] = $event => (seedCleanConfirmOpen.value = false))
                }, [
                  (_openBlock$1(), _createElementBlock("svg", _hoisted_39, [
                    _createElementVNode("path", {
                      d: _unref(mdiClose),
                      fill: "currentColor"
                    }, null, 8, _hoisted_40)
                  ]))
                ])
              ]),
              _createElementVNode("div", {
                class: _normalizeClass(["aoa-seedclean-confirm-dialog__warning", { 'aoa-seedclean-confirm-dialog__warning--danger': form.seedclean_action !== 'pause' }])
              }, [
                (_openBlock$1(), _createElementBlock("svg", _hoisted_41, [
                  _createElementVNode("path", {
                    d: _unref(mdiAlertOutline),
                    fill: "currentColor"
                  }, null, 8, _hoisted_42)
                ])),
                _createElementVNode("span", null, _toDisplayString(seedCleanActionMeta.value.risk), 1)
              ], 2),
              _createElementVNode("div", _hoisted_43, [
                _createElementVNode("strong", null, _toDisplayString(form.seedclean_downloaders?.length || 0) + " 个下载器", 1),
                _cache[22] || (_cache[22] = _createElementVNode("span", null, "按当前条件执行", -1))
              ]),
              _createElementVNode("div", _hoisted_44, [
                _createElementVNode("div", _hoisted_45, [
                  _createElementVNode("strong", null, _toDisplayString(form.seedclean_downloaders?.join('、') || '未选择下载器'), 1),
                  _createElementVNode("span", null, _toDisplayString(seedCleanActionMeta.value.label), 1),
                  _createElementVNode("small", null, _toDisplayString(seedCleanFilterSummary.value), 1)
                ])
              ]),
              _createElementVNode("footer", _hoisted_46, [
                _createElementVNode("button", {
                  type: "button",
                  class: "aoa-config-btn aoa-config-btn--ghost",
                  "data-seedclean-confirm-cancel": "",
                  onClick: _cache[6] || (_cache[6] = $event => (seedCleanConfirmOpen.value = false))
                }, "返回修改"),
                _createElementVNode("button", {
                  type: "button",
                  class: "aoa-config-btn aoa-config-btn--save aoa-seedclean-confirm-dialog__submit",
                  "data-seedclean-confirm-submit": "",
                  onClick: confirmSeedCleanExecution
                }, [
                  (_openBlock$1(), _createElementBlock("svg", _hoisted_47, [
                    _createElementVNode("path", {
                      d: _unref(mdiPlay),
                      fill: "currentColor"
                    }, null, 8, _hoisted_48)
                  ])),
                  _createElementVNode("span", null, _toDisplayString(seedCleanActionMeta.value.confirm), 1)
                ])
              ])
            ])
          ], 6))
        : _createCommentVNode("", true)
    ])),
    (_openBlock$1(), _createBlock$1(_Teleport, { to: "body" }, [
      (pluginUninstallConfirmOpen.value)
        ? (_openBlock$1(), _createElementBlock("div", {
            key: 0,
            class: _normalizeClass(["aoa-seedclean-confirm-overlay aoa-root", _unref(rootThemeClass)]),
            style: _normalizeStyle(seedCleanPortalStyle.value),
            "data-plugin-uninstall-confirm-dialog": "",
            role: "presentation",
            onClick: _cache[10] || (_cache[10] = _withModifiers($event => (pluginUninstallConfirmOpen.value = false), ["self"]))
          }, [
            _createElementVNode("section", _hoisted_49, [
              _createElementVNode("header", _hoisted_50, [
                _cache[23] || (_cache[23] = _createElementVNode("div", null, [
                  _createElementVNode("h2", { id: "plugin-uninstall-confirm-title" }, "确认卸载插件")
                ], -1)),
                _createElementVNode("button", {
                  type: "button",
                  class: "aoa-seedclean-confirm-dialog__close",
                  "aria-label": "关闭",
                  title: "关闭",
                  onClick: _cache[8] || (_cache[8] = $event => (pluginUninstallConfirmOpen.value = false))
                }, [
                  (_openBlock$1(), _createElementBlock("svg", _hoisted_51, [
                    _createElementVNode("path", {
                      d: _unref(mdiClose),
                      fill: "currentColor"
                    }, null, 8, _hoisted_52)
                  ]))
                ])
              ]),
              _createElementVNode("div", _hoisted_53, [
                (_openBlock$1(), _createElementBlock("svg", _hoisted_54, [
                  _createElementVNode("path", {
                    d: _unref(mdiAlertOutline),
                    fill: "currentColor"
                  }, null, 8, _hoisted_55)
                ])),
                _cache[24] || (_cache[24] = _createElementVNode("span", null, "以下操作将立即执行且无法撤销，请核对目标插件和清理范围。", -1))
              ]),
              _createElementVNode("div", _hoisted_56, [
                _createElementVNode("strong", null, _toDisplayString(selectedPluginUninstallItems.value.length) + " 个目标插件", 1),
                _createElementVNode("span", null, _toDisplayString(pluginUninstallActionItems.value.length) + " 项卸载或清理操作", 1)
              ]),
              _createElementVNode("div", _hoisted_57, [
                (_openBlock$1(true), _createElementBlock(_Fragment, null, _renderList(selectedPluginUninstallItems.value, (item) => {
                  return (_openBlock$1(), _createElementBlock("div", {
                    key: item.value,
                    class: "aoa-seedclean-confirm-dialog__item"
                  }, [
                    _createElementVNode("strong", null, _toDisplayString(item.title), 1),
                    _createElementVNode("span", null, _toDisplayString(item.value), 1)
                  ]))
                }), 128))
              ]),
              _createElementVNode("div", _hoisted_58, [
                (_openBlock$1(true), _createElementBlock(_Fragment, null, _renderList(pluginUninstallActionItems.value, (item) => {
                  return (_openBlock$1(), _createElementBlock("div", {
                    key: item.key,
                    class: "aoa-seedclean-confirm-dialog__item"
                  }, [
                    _createElementVNode("strong", null, _toDisplayString(item.label), 1),
                    _createElementVNode("small", null, _toDisplayString(item.detail), 1)
                  ]))
                }), 128))
              ]),
              _createElementVNode("footer", _hoisted_59, [
                _createElementVNode("button", {
                  type: "button",
                  class: "aoa-config-btn aoa-config-btn--ghost",
                  "data-plugin-uninstall-confirm-cancel": "",
                  onClick: _cache[9] || (_cache[9] = $event => (pluginUninstallConfirmOpen.value = false))
                }, "返回修改"),
                _createElementVNode("button", {
                  type: "button",
                  class: "aoa-config-btn aoa-config-btn--save aoa-seedclean-confirm-dialog__submit",
                  "data-plugin-uninstall-confirm-submit": "",
                  onClick: confirmPluginUninstallExecution
                }, [
                  (_openBlock$1(), _createElementBlock("svg", _hoisted_60, [
                    _createElementVNode("path", {
                      d: _unref(mdiDeleteOutline),
                      fill: "currentColor"
                    }, null, 8, _hoisted_61)
                  ])),
                  _cache[25] || (_cache[25] = _createElementVNode("span", null, "确认卸载", -1))
                ])
              ])
            ])
          ], 6))
        : _createCommentVNode("", true)
    ])),
    (_openBlock$1(), _createBlock$1(_Teleport, { to: "body" }, [
      (downloaderHelperConfirmOpen.value)
        ? (_openBlock$1(), _createElementBlock("div", {
            key: 0,
            class: _normalizeClass(["aoa-seedclean-confirm-overlay aoa-root", _unref(rootThemeClass)]),
            style: _normalizeStyle(seedCleanPortalStyle.value),
            "data-downloader-helper-confirm-dialog": "",
            role: "presentation",
            onClick: _cache[13] || (_cache[13] = _withModifiers($event => (downloaderHelperConfirmOpen.value = false), ["self"]))
          }, [
            _createElementVNode("section", _hoisted_62, [
              _createElementVNode("header", _hoisted_63, [
                _cache[26] || (_cache[26] = _createElementVNode("div", null, [
                  _createElementVNode("span", { class: "aoa-seedclean-confirm-dialog__kicker" }, "一次确认"),
                  _createElementVNode("h2", { id: "downloader-helper-confirm-title" }, "清理失效下载任务")
                ], -1)),
                _createElementVNode("button", {
                  type: "button",
                  class: "aoa-seedclean-confirm-dialog__close",
                  "aria-label": "关闭",
                  title: "关闭",
                  onClick: _cache[11] || (_cache[11] = $event => (downloaderHelperConfirmOpen.value = false))
                }, [
                  (_openBlock$1(), _createElementBlock("svg", _hoisted_64, [
                    _createElementVNode("path", {
                      d: _unref(mdiClose),
                      fill: "currentColor"
                    }, null, 8, _hoisted_65)
                  ]))
                ])
              ]),
              _createElementVNode("div", _hoisted_66, [
                (_openBlock$1(), _createElementBlock("svg", _hoisted_67, [
                  _createElementVNode("path", {
                    d: _unref(mdiAlertOutline),
                    fill: "currentColor"
                  }, null, 8, _hoisted_68)
                ])),
                _cache[27] || (_cache[27] = _createElementVNode("span", null, "标签和恢复做种无需确认；以下失效任务将从下载器移除。仅在源文件事件确认数据已删除时才请求清理文件。", -1))
              ]),
              _createElementVNode("div", _hoisted_69, [
                _createElementVNode("strong", null, _toDisplayString(downloaderHelperPreviewItems.value.length) + " 个清理候选", 1),
                _cache[28] || (_cache[28] = _createElementVNode("span", null, "确认后同时执行当前选择的非破坏任务", -1))
              ]),
              _createElementVNode("div", _hoisted_70, [
                (_openBlock$1(true), _createElementBlock(_Fragment, null, _renderList(downloaderHelperPreviewItems.value, (item) => {
                  return (_openBlock$1(), _createElementBlock("div", {
                    key: `${item.downloader}-${item.id}`,
                    class: "aoa-seedclean-confirm-dialog__item"
                  }, [
                    _createElementVNode("strong", null, _toDisplayString(item.name || item.id), 1),
                    _createElementVNode("span", null, _toDisplayString(item.downloader), 1),
                    _createElementVNode("small", null, _toDisplayString(item.reason) + " · " + _toDisplayString(item.delete_file ? '数据已删除' : '不删除数据文件'), 1)
                  ]))
                }), 128))
              ]),
              _createElementVNode("footer", _hoisted_71, [
                _createElementVNode("button", {
                  type: "button",
                  class: "aoa-config-btn aoa-config-btn--ghost",
                  onClick: _cache[12] || (_cache[12] = $event => (downloaderHelperConfirmOpen.value = false))
                }, "取消"),
                _createElementVNode("button", {
                  type: "button",
                  class: "aoa-config-btn aoa-config-btn--save aoa-seedclean-confirm-dialog__submit",
                  "data-downloader-helper-confirm-submit": "",
                  onClick: confirmDownloaderHelperExecution
                }, [
                  (_openBlock$1(), _createElementBlock("svg", _hoisted_72, [
                    _createElementVNode("path", {
                      d: _unref(mdiPlay),
                      fill: "currentColor"
                    }, null, 8, _hoisted_73)
                  ])),
                  _cache[29] || (_cache[29] = _createElementVNode("span", null, "确认并执行", -1))
                ])
              ])
            ])
          ], 6))
        : _createCommentVNode("", true)
    ])),
    _createElementVNode("footer", _hoisted_74, [
      _createElementVNode("div", _hoisted_75, [
        _createElementVNode("span", _hoisted_76, _toDisplayString(currentActionHint.value), 1),
        _createVNode(_Transition, { name: "aoa-fade" }, {
          default: _withCtx(() => [
            (_unref(action).message)
              ? (_openBlock$1(), _createElementBlock("strong", {
                  key: 0,
                  class: _normalizeClass(["aoa-config-action-feedback", { 'aoa-config-action-feedback--ok': _unref(action).ok, 'aoa-config-action-feedback--err': !_unref(action).ok }])
                }, _toDisplayString(_unref(action).message), 3))
              : _createCommentVNode("", true)
          ]),
          _: 1
        })
      ]),
      _createElementVNode("div", _hoisted_77, [
        _createElementVNode("button", {
          type: "button",
          class: "aoa-config-btn aoa-config-btn--ghost",
          onClick: _cache[14] || (_cache[14] = $event => (emit('close')))
        }, "取消"),
        _createElementVNode("button", {
          type: "button",
          class: "aoa-config-btn aoa-config-btn--save",
          "data-config-save-button": "",
          onClick: saveConfig
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
          _cache[30] || (_cache[30] = _createElementVNode("span", null, "保存配置", -1))
        ])
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
  pluginId: { type: String, default: 'AgentOpsAssistant' },
  configRecordState: { type: String, default: null },
},
  emits: ['save', 'close', 'switch'],
  setup(__props, { emit: __emit }) {

const props = __props;

const emit = __emit;
const recordStates = new Set(['unknown', 'absent', 'present']);
const explicitRecordState = value => recordStates.has(value) ? value : null;
const loadedConfig = ref({ ...props.initialConfig });
const recordState = ref(explicitRecordState(props.configRecordState) || 'unknown');

watch(() => props.initialConfig, value => {
  loadedConfig.value = { ...(value || {}) };
}, { deep: true });

watch(() => props.configRecordState, value => {
  recordState.value = explicitRecordState(value) || 'unknown';
});

onMounted(async () => {
  if (!props.api?.get) return
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
      recordState.value = 'absent';
    }
  } catch {
    if (!explicitRecordState(props.configRecordState)) recordState.value = 'unknown';
  }
});


return (_ctx, _cache) => {
  return (_openBlock(), _createBlock(_sfc_main$1, {
    api: __props.api,
    "initial-config": loadedConfig.value,
    "plugin-id": __props.pluginId,
    "config-record-state": recordState.value,
    onSave: _cache[0] || (_cache[0] = value => emit('save', value)),
    onClose: _cache[1] || (_cache[1] = $event => (emit('close'))),
    onSwitch: _cache[2] || (_cache[2] = $event => (emit('switch')))
  }, null, 8, ["api", "initial-config", "plugin-id", "config-record-state"]))
}
}

};

export { _sfc_main as default };
