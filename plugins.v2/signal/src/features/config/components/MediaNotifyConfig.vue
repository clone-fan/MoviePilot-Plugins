<template>
  <div class="signal-pane signal-media-pane">
    <VForm class="signal-media-form">
      <ModuleHero
        :enabled="!!form.msgnotify_enabled"
        icon="mdi-television-play"
        kicker="媒体通知"
        on-title="媒体通知已启用"
        off-title="媒体通知未启用"
        desc="接收 Emby/Jellyfin/Plex 事件|按事件类型与服务器过滤通知"
        :count-label="`${form.msgnotify_types?.length || 0} 个事件`"
        :toggle="false"
      />
    </VForm>
  </div>
</template>

<script setup>
import ModuleHero from './ModuleHero'

defineProps({
  form: { type: Object, required: true },
})
</script>
