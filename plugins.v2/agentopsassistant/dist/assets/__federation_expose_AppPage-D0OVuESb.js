import { importShared } from './__federation_fn_import-JrT3xvdd.js';
import Page from './__federation_expose_Page-BNbwAGBD.js';

const {openBlock:_openBlock,createBlock:_createBlock} = await importShared('vue');


const _sfc_main = {
  __name: 'AppPage',
  props: {
  api: { type: [Object, Function], default: null },
  pluginId: { type: String, default: 'AgentOpsAssistant' },
  navKey: { type: String, default: 'main' },
},
  setup(__props) {



return (_ctx, _cache) => {
  return (_openBlock(), _createBlock(Page, {
    api: __props.api,
    surface: "sidebar"
  }, null, 8, ["api"]))
}
}

};

export { _sfc_main as default };
