import { importShared } from './__federation_fn_import-JrT3xvdd.js';
import _sfc_main$1 from './__federation_expose_Dashboard-Cr0Fl9n_.js';

const {openBlock:_openBlock,createBlock:_createBlock} = await importShared('vue');


const _sfc_main = {
  __name: 'Page',
  props: {
  api: { type: [Object, Function], default: null },
  surface: { type: String, default: 'dialog' },
  pluginId: { type: String, default: 'Signal' },
},
  emits: ['close', 'switch'],
  setup(__props, { emit: __emit }) {



const emit = __emit;

return (_ctx, _cache) => {
  return (_openBlock(), _createBlock(_sfc_main$1, {
    api: __props.api,
    surface: __props.surface,
    "plugin-id": __props.pluginId,
    onClose: _cache[0] || (_cache[0] = $event => (emit('close'))),
    onSwitch: _cache[1] || (_cache[1] = $event => (emit('switch')))
  }, null, 8, ["api", "surface", "plugin-id"]))
}
}

};

export { _sfc_main as default };
