<script setup>
import { getCurrentInstance, onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: '* * * * *',
  },
})

const emit = defineEmits(['update:modelValue'])

const menu = ref(false)
const currentCron = ref(props.modelValue)
const menuRoot = ref(null)
const instance = getCurrentInstance()
const menuContentClass = `cron-input-menu-${instance?.uid ?? 'default'}`
const menuContentSelector = `.${menuContentClass}`

function isCronMenuTarget(target) {
  if (!(target instanceof Element)) return false

  if (menuRoot.value?.contains(target)) return true

  const menuContent = document.querySelector(menuContentSelector)
  if (menuContent?.contains(target)) return true

  const overlayId = target.closest('.v-overlay')?.getAttribute('id')
  if (!overlayId || !menuContent) return false

  return Array.from(menuContent.querySelectorAll('[aria-owns]')).some(
    activator => activator.getAttribute('aria-owns') === overlayId,
  )
}

function closeOnOutsidePointerDown(event) {
  if (!menu.value || isCronMenuTarget(event.target)) return
  menu.value = false
}

onMounted(() => {
  document.addEventListener('pointerdown', closeOnOutsidePointerDown, true)
})

onBeforeUnmount(() => {
  document.removeEventListener('pointerdown', closeOnOutsidePointerDown, true)
})

watch(currentCron, newVal => {
  emit('update:modelValue', newVal)
})

watch(
  () => props.modelValue,
  value => {
    currentCron.value = value
  },
)
</script>

<template>
  <div ref="menuRoot" class="signal-cron-input" data-cron-input>
    <VMenu
      v-model="menu"
      :close-on-content-click="false"
      :content-class="['cursor-default', menuContentClass]"
      persistent
    >
      <template #activator="{ props: menuProps }">
        <slot name="activator" :menuprops="menuProps" />
      </template>
      <VList>
        <VListItem>
          <VCronVuetify
            v-model="currentCron"
            locale="zh-CN"
            :chip-props="{ color: 'success' }"
            class="mt-1"
          />
        </VListItem>
      </VList>
    </VMenu>
  </div>
</template>