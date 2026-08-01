<script setup>
import { computed, ref, useAttrs, watch } from 'vue'
import CronInput from './CronInput.vue'

defineOptions({
  inheritAttrs: false,
})

const attrs = useAttrs()

const props = defineProps({
  modelValue: {
    type: String,
    default: '* * * * *',
  },
})

const emit = defineEmits(['update:modelValue'])

const innerValue = ref(props.modelValue)

watch(
  () => props.modelValue,
  value => {
    innerValue.value = value
  },
)

const propsWithoutModelValue = computed(() => {
  const { modelValue, ...rest } = props
  return { ...rest, ...attrs }
})

function updateModelValue(value) {
  innerValue.value = value
  emit('update:modelValue', value)
}
</script>

<template>
  <div class="signal-cron-field" data-cron-field data-official-cron="true">
    <CronInput
      v-model="innerValue"
      data-cron-field-input
      @update:modelValue="updateModelValue"
    >
      <template #activator="{ menuprops }">
        <VTextField
          :modelValue="innerValue"
          clearable
          v-bind="{ ...menuprops, ...propsWithoutModelValue }"
          @update:modelValue="updateModelValue"
        />
      </template>
    </CronInput>
  </div>
</template>