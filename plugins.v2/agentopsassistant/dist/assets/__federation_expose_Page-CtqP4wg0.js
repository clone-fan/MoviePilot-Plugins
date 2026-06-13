import { importShared } from './__federation_fn_import-JrT3xvdd.js';
import { _ as _export_sfc, g as getPluginApi } from './_plugin-vue_export-helper-DrmeQDM1.js';

const {resolveComponent:_resolveComponent,createVNode:_createVNode,createElementVNode:_createElementVNode,createTextVNode:_createTextVNode,withCtx:_withCtx,openBlock:_openBlock,createBlock:_createBlock,createCommentVNode:_createCommentVNode,toDisplayString:_toDisplayString,renderList:_renderList,Fragment:_Fragment,createElementBlock:_createElementBlock} = await importShared('vue');


const _hoisted_1 = { class: "agentops-dashboard" };
const _hoisted_2 = { class: "pa-3" };
const _hoisted_3 = { class: "text-h6 font-weight-bold" };
const _hoisted_4 = { class: "text-h6 font-weight-bold" };
const _hoisted_5 = { class: "text-h6 font-weight-bold" };
const _hoisted_6 = { class: "d-flex align-center ga-2" };
const _hoisted_7 = {
  key: 0,
  class: "text-caption text-medium-emphasis mb-2"
};
const _hoisted_8 = {
  key: 1,
  class: "health-output"
};
const _hoisted_9 = {
  key: 2,
  class: "text-medium-emphasis text-body-2"
};

const {ref,reactive,computed,onMounted} = await importShared('vue');


const _sfc_main = {
  __name: 'Page',
  props: { api: { type: [Object, Function], default: null } },
  emits: ['close', 'switch'],
  setup(__props, { emit: __emit }) {

const props = __props;
const emit = __emit;

const loading = ref(true);
const error = ref('');
const data = reactive({
  enabled: false,
  summary: '',
  tasks: [],
  task_total: 0,
  task_on: 0,
  task_failed: 0,
  health: { time: '', success: null, output: '' },
});

const overallColor = computed(() => {
  if (!data.enabled) return 'default'
  if (data.task_failed > 0) return 'error'
  return 'success'
});
const overallText = computed(() => {
  if (!data.enabled) return '未启用'
  if (data.task_failed > 0) return `${data.task_failed} 项异常`
  return '运行正常'
});
const healthColor = computed(() => {
  if (data.health.success === true) return 'success'
  if (data.health.success === false) return 'error'
  return 'grey'
});
const healthText = computed(() => {
  if (data.health.success === true) return '通过'
  if (data.health.success === false) return '存在异常'
  return '尚未巡查'
});

async function loadDashboard() {
  loading.value = true;
  error.value = '';
  try {
    const res = await getPluginApi(props.api, 'dashboard');
    Object.assign(data, res || {});
  } catch (err) {
    error.value = err?.message || '仪表盘数据加载失败';
  } finally {
    loading.value = false;
  }
}

onMounted(loadDashboard);

return (_ctx, _cache) => {
  const _component_VIcon = _resolveComponent("VIcon");
  const _component_VSpacer = _resolveComponent("VSpacer");
  const _component_VBtn = _resolveComponent("VBtn");
  const _component_VToolbar = _resolveComponent("VToolbar");
  const _component_VDivider = _resolveComponent("VDivider");
  const _component_VAlert = _resolveComponent("VAlert");
  const _component_VAvatar = _resolveComponent("VAvatar");
  const _component_VCardText = _resolveComponent("VCardText");
  const _component_VCard = _resolveComponent("VCard");
  const _component_VCol = _resolveComponent("VCol");
  const _component_VRow = _resolveComponent("VRow");
  const _component_VCardTitle = _resolveComponent("VCardTitle");
  const _component_VSkeletonLoader = _resolveComponent("VSkeletonLoader");
  const _component_VListItemTitle = _resolveComponent("VListItemTitle");
  const _component_VListItemSubtitle = _resolveComponent("VListItemSubtitle");
  const _component_VChip = _resolveComponent("VChip");
  const _component_VListItem = _resolveComponent("VListItem");
  const _component_VList = _resolveComponent("VList");

  return (_openBlock(), _createElementBlock("div", _hoisted_1, [
    _createVNode(_component_VToolbar, {
      density: "comfortable",
      class: "agentops-toolbar"
    }, {
      default: _withCtx(() => [
        _createVNode(_component_VIcon, {
          icon: "mdi-view-dashboard-outline",
          class: "ms-3 me-2",
          color: "primary"
        }),
        _cache[4] || (_cache[4] = _createElementVNode("div", { class: "text-h6" }, "MP 运维助手 · 仪表盘", -1)),
        _createVNode(_component_VSpacer),
        _createVNode(_component_VBtn, {
          color: "primary",
          variant: "tonal",
          "prepend-icon": "mdi-refresh",
          class: "text-none me-2",
          loading: loading.value,
          onClick: loadDashboard
        }, {
          default: _withCtx(() => [...(_cache[2] || (_cache[2] = [
            _createTextVNode("刷新", -1)
          ]))]),
          _: 1
        }, 8, ["loading"]),
        _createVNode(_component_VBtn, {
          variant: "text",
          "prepend-icon": "mdi-cog-outline",
          class: "text-none",
          onClick: _cache[0] || (_cache[0] = $event => (emit('switch')))
        }, {
          default: _withCtx(() => [...(_cache[3] || (_cache[3] = [
            _createTextVNode("设置", -1)
          ]))]),
          _: 1
        }),
        _createVNode(_component_VBtn, {
          icon: "mdi-close",
          variant: "text",
          onClick: _cache[1] || (_cache[1] = $event => (emit('close')))
        })
      ]),
      _: 1
    }),
    _createVNode(_component_VDivider),
    _createElementVNode("div", _hoisted_2, [
      (error.value)
        ? (_openBlock(), _createBlock(_component_VAlert, {
            key: 0,
            type: "error",
            variant: "tonal",
            class: "mb-3",
            text: error.value
          }, null, 8, ["text"]))
        : _createCommentVNode("", true),
      _createVNode(_component_VRow, { class: "mb-1" }, {
        default: _withCtx(() => [
          _createVNode(_component_VCol, {
            cols: "12",
            sm: "4"
          }, {
            default: _withCtx(() => [
              _createVNode(_component_VCard, {
                variant: "tonal",
                color: overallColor.value,
                class: "rounded-lg"
              }, {
                default: _withCtx(() => [
                  _createVNode(_component_VCardText, { class: "d-flex align-center" }, {
                    default: _withCtx(() => [
                      _createVNode(_component_VAvatar, {
                        color: overallColor.value,
                        variant: "flat",
                        size: "44",
                        class: "me-3"
                      }, {
                        default: _withCtx(() => [
                          _createVNode(_component_VIcon, {
                            icon: "mdi-shield-check-outline",
                            color: "white"
                          })
                        ]),
                        _: 1
                      }, 8, ["color"]),
                      _createElementVNode("div", null, [
                        _cache[5] || (_cache[5] = _createElementVNode("div", { class: "text-caption text-medium-emphasis" }, "插件状态", -1)),
                        _createElementVNode("div", _hoisted_3, _toDisplayString(overallText.value), 1)
                      ])
                    ]),
                    _: 1
                  })
                ]),
                _: 1
              }, 8, ["color"])
            ]),
            _: 1
          }),
          _createVNode(_component_VCol, {
            cols: "12",
            sm: "4"
          }, {
            default: _withCtx(() => [
              _createVNode(_component_VCard, {
                variant: "tonal",
                color: "primary",
                class: "rounded-lg"
              }, {
                default: _withCtx(() => [
                  _createVNode(_component_VCardText, { class: "d-flex align-center" }, {
                    default: _withCtx(() => [
                      _createVNode(_component_VAvatar, {
                        color: "primary",
                        variant: "flat",
                        size: "44",
                        class: "me-3"
                      }, {
                        default: _withCtx(() => [
                          _createVNode(_component_VIcon, {
                            icon: "mdi-format-list-checks",
                            color: "white"
                          })
                        ]),
                        _: 1
                      }),
                      _createElementVNode("div", null, [
                        _cache[6] || (_cache[6] = _createElementVNode("div", { class: "text-caption text-medium-emphasis" }, "已启用任务", -1)),
                        _createElementVNode("div", _hoisted_4, _toDisplayString(data.task_on) + " / " + _toDisplayString(data.task_total), 1)
                      ])
                    ]),
                    _: 1
                  })
                ]),
                _: 1
              })
            ]),
            _: 1
          }),
          _createVNode(_component_VCol, {
            cols: "12",
            sm: "4"
          }, {
            default: _withCtx(() => [
              _createVNode(_component_VCard, {
                variant: "tonal",
                color: data.task_failed > 0 ? 'error' : 'success',
                class: "rounded-lg"
              }, {
                default: _withCtx(() => [
                  _createVNode(_component_VCardText, { class: "d-flex align-center" }, {
                    default: _withCtx(() => [
                      _createVNode(_component_VAvatar, {
                        color: data.task_failed > 0 ? 'error' : 'success',
                        variant: "flat",
                        size: "44",
                        class: "me-3"
                      }, {
                        default: _withCtx(() => [
                          _createVNode(_component_VIcon, {
                            icon: data.task_failed > 0 ? 'mdi-alert-circle-outline' : 'mdi-check-circle-outline',
                            color: "white"
                          }, null, 8, ["icon"])
                        ]),
                        _: 1
                      }, 8, ["color"]),
                      _createElementVNode("div", null, [
                        _cache[7] || (_cache[7] = _createElementVNode("div", { class: "text-caption text-medium-emphasis" }, "最近执行异常", -1)),
                        _createElementVNode("div", _hoisted_5, _toDisplayString(data.task_failed), 1)
                      ])
                    ]),
                    _: 1
                  })
                ]),
                _: 1
              }, 8, ["color"])
            ]),
            _: 1
          })
        ]),
        _: 1
      }),
      _createVNode(_component_VCard, {
        variant: "outlined",
        class: "rounded-lg mb-3"
      }, {
        default: _withCtx(() => [
          _createVNode(_component_VCardTitle, { class: "text-subtitle-1 d-flex align-center py-3" }, {
            default: _withCtx(() => [
              _createVNode(_component_VIcon, {
                icon: "mdi-timeline-clock-outline",
                color: "primary",
                class: "me-2"
              }),
              _cache[8] || (_cache[8] = _createTextVNode("模块运行概览 ", -1))
            ]),
            _: 1
          }),
          _createVNode(_component_VDivider),
          (loading.value)
            ? (_openBlock(), _createBlock(_component_VSkeletonLoader, {
                key: 0,
                type: "list-item-avatar-three-line@3"
              }))
            : (_openBlock(), _createBlock(_component_VList, {
                key: 1,
                class: "bg-transparent py-0"
              }, {
                default: _withCtx(() => [
                  (_openBlock(true), _createElementBlock(_Fragment, null, _renderList(data.tasks, (task, i) => {
                    return (_openBlock(), _createElementBlock(_Fragment, {
                      key: task.key
                    }, [
                      _createVNode(_component_VListItem, { class: "py-2" }, {
                        prepend: _withCtx(() => [
                          _createVNode(_component_VAvatar, {
                            size: "40",
                            variant: "tonal",
                            color: task.enabled ? task.color : 'default'
                          }, {
                            default: _withCtx(() => [
                              _createVNode(_component_VIcon, {
                                icon: task.icon
                              }, null, 8, ["icon"])
                            ]),
                            _: 2
                          }, 1032, ["color"])
                        ]),
                        append: _withCtx(() => [
                          _createElementVNode("div", _hoisted_6, [
                            _createVNode(_component_VChip, {
                              size: "x-small",
                              variant: "tonal",
                              color: task.enabled ? 'success' : 'default'
                            }, {
                              default: _withCtx(() => [
                                _createTextVNode(_toDisplayString(task.enabled ? 'ON' : 'OFF'), 1)
                              ]),
                              _: 2
                            }, 1032, ["color"]),
                            _createVNode(_component_VChip, {
                              size: "x-small",
                              variant: "tonal",
                              color: task.color
                            }, {
                              default: _withCtx(() => [
                                _createTextVNode(_toDisplayString(task.state), 1)
                              ]),
                              _: 2
                            }, 1032, ["color"])
                          ])
                        ]),
                        default: _withCtx(() => [
                          _createVNode(_component_VListItemTitle, { class: "font-weight-medium" }, {
                            default: _withCtx(() => [
                              _createTextVNode(_toDisplayString(task.name), 1)
                            ]),
                            _: 2
                          }, 1024),
                          _createVNode(_component_VListItemSubtitle, { class: "mt-1" }, {
                            default: _withCtx(() => [
                              _createTextVNode(" 最近 " + _toDisplayString(task.last_time || '—') + "｜下次 " + _toDisplayString(task.next) + "｜" + _toDisplayString(task.last_summary), 1)
                            ]),
                            _: 2
                          }, 1024)
                        ]),
                        _: 2
                      }, 1024),
                      (i < data.tasks.length - 1)
                        ? (_openBlock(), _createBlock(_component_VDivider, { key: 0 }))
                        : _createCommentVNode("", true)
                    ], 64))
                  }), 128))
                ]),
                _: 1
              }))
        ]),
        _: 1
      }),
      _createVNode(_component_VCard, {
        variant: "outlined",
        class: "rounded-lg"
      }, {
        default: _withCtx(() => [
          _createVNode(_component_VCardTitle, { class: "text-subtitle-1 d-flex align-center py-3" }, {
            default: _withCtx(() => [
              _createVNode(_component_VIcon, {
                icon: "mdi-heart-pulse",
                color: "primary",
                class: "me-2"
              }),
              _cache[9] || (_cache[9] = _createTextVNode("最近健康巡查 ", -1)),
              _createVNode(_component_VSpacer),
              _createVNode(_component_VChip, {
                size: "small",
                variant: "tonal",
                color: healthColor.value
              }, {
                default: _withCtx(() => [
                  _createTextVNode(_toDisplayString(healthText.value), 1)
                ]),
                _: 1
              }, 8, ["color"])
            ]),
            _: 1
          }),
          _createVNode(_component_VDivider),
          _createVNode(_component_VCardText, null, {
            default: _withCtx(() => [
              (data.health.time)
                ? (_openBlock(), _createElementBlock("div", _hoisted_7, "巡查时间：" + _toDisplayString(data.health.time), 1))
                : _createCommentVNode("", true),
              (data.health.output)
                ? (_openBlock(), _createElementBlock("pre", _hoisted_8, _toDisplayString(data.health.output), 1))
                : (_openBlock(), _createElementBlock("div", _hoisted_9, "尚无健康巡查记录，可在设置页手动触发或等待每日汇报自动执行。"))
            ]),
            _: 1
          })
        ]),
        _: 1
      })
    ])
  ]))
}
}

};
const Page = /*#__PURE__*/_export_sfc(_sfc_main, [['__scopeId',"data-v-cad48fa5"]]);

export { Page as default };
