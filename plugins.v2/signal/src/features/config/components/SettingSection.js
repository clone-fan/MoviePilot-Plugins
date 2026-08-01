import { defineComponent, h } from 'vue'

// 配置区块容器 — 标题 + 描述 + slot 内容
export default defineComponent({
  name: 'SettingSection',
  props: {
    title: { type: String, required: true },
    note: { type: String, default: '' },
  },
  setup(props, { slots }) {
    return () => h('section', { class: 'signal-setting-section' }, [
      h('div', { class: 'signal-setting-section-head' }, [
        h('div', [
          h('div', { class: 'signal-setting-section-title' }, props.title),
          props.note ? h('div', { class: 'signal-setting-section-note' }, props.note) : null,
        ]),
      ]),
      h('div', { class: 'signal-setting-section-body' }, slots.default?.()),
    ])
  },
})
