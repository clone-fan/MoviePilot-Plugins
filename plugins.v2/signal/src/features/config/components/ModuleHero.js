import { defineComponent, h, resolveComponent } from 'vue'

// 模块标题区 — 图标 + 标题 + 描述 + 状态/开关
export default defineComponent({
  name: 'ModuleHero',
  props: {
    enabled: { type: Boolean, default: false },
    icon: { type: String, required: true },
    kicker: { type: String, required: true },
    onTitle: { type: String, required: true },
    offTitle: { type: String, default: '' },
    desc: { type: String, required: true },
    countLabel: { type: String, default: '' },
    stateOn: { type: String, default: '运行中' },
    stateOff: { type: String, default: '待启用' },
    switchLabel: { type: String, default: '启用' },
    toggle: { type: Boolean, default: true },
  },
  emits: ['update:enabled'],
  setup(props, { emit }) {
    return () => {
      const VIcon = resolveComponent('VIcon')
      const VChip = resolveComponent('VChip')
      const VSwitch = resolveComponent('VSwitch')
      const descLines = String(props.desc || '').split(/\n|\|/)
      const descChildren = []
      descLines.forEach((line, index) => {
        if (index) descChildren.push(h('br'))
        descChildren.push(line)
      })
      return h('div', { class: ['signal-module-hero', { 'signal-module-hero--off': !props.enabled }] }, [
        h('div', { class: 'signal-module-heading' }, [
          h('div', { class: 'signal-module-emblem' }, [h(VIcon, { icon: props.icon, size: 28 })]),
          h('div', { class: 'signal-module-heading-text' }, [
            h('div', { class: 'signal-module-kicker' }, props.kicker),
            h('div', { class: 'signal-module-title' }, props.enabled ? props.onTitle : (props.offTitle || props.onTitle)),
            h('div', { class: 'signal-module-desc' }, descChildren),
          ]),
        ]),
        h('div', { class: 'signal-module-state' }, [
          h(VChip, { size: 'small', color: props.enabled ? 'success' : 'warning', variant: 'flat' }, () => props.enabled ? props.stateOn : props.stateOff),
          props.countLabel ? h(VChip, { size: 'small', color: 'primary', variant: 'tonal' }, () => props.countLabel) : null,
          props.toggle ? h(VSwitch, {
            modelValue: props.enabled,
            'onUpdate:modelValue': value => emit('update:enabled', value),
            color: 'primary',
            inset: true,
            hideDetails: true,
            label: props.switchLabel,
          }) : null,
        ]),
      ])
    }
  },
})
