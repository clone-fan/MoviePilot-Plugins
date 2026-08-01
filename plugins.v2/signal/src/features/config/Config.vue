<script setup>
import { reactive, ref, computed, watch, nextTick, onMounted, onBeforeUnmount, defineComponent, h } from 'vue'
import '../../shared/styles/index.css'
import {
  mdiCogOutline, mdiMessageBadgeOutline, mdiChartLine, mdiDownloadNetworkOutline,
  mdiPuzzleRemoveOutline, mdiTelevisionPlay, mdiBellRingOutline, mdiHeartPulse,
  mdiDeleteSweepOutline, mdiTagMultipleOutline, mdiAutoFix, mdiArchiveArrowUpOutline,
  mdiFileDocumentRemoveOutline, mdiUpdate, mdiViewDashboardOutline, mdiClose,
  mdiShieldHalfFull, mdiPowerStandby, mdiCalendarClock,
  mdiFormatListNumbered, mdiEmailOutline, mdiServer, mdiFormatListChecks,
  mdiMovieOpenOutline, mdiChartBar, mdiGauge, mdiHarddisk, mdiFilterOutline,
  mdiScaleBalance, mdiTimerOutline, mdiTagOutline, mdiDeleteOutline, mdiLinkVariant,
  mdiLockOutline, mdiCloudOutline, mdiWeb, mdiAccountOutline, mdiContentCopy,
  mdiLockCheckOutline, mdiFolderOutline, mdiRocketLaunchOutline, mdiBroom,
  mdiSync, mdiDownloadOutline, mdiShieldOutline, mdiCloudUploadOutline,
  mdiAlertOutline, mdiDatabaseOutline, mdiCodeTags, mdiCubeOutline, mdiPlusCircleOutline, mdiEyeOutline,
  mdiShieldCheckOutline, mdiBell, mdiDownload, mdiPuzzle, mdiCardAccountDetailsOutline, mdiTelevision, mdiBellOutline, mdiPuzzleOutline, mdiHistory, mdiBackupRestore, mdiAlertCircleOutline, mdiAlphaMBoxOutline, mdiLayersOutline, mdiPencilOutline, mdiPercent, mdiPlay, mdiSendOutline, mdiSignal, mdiWeight,
} from '@mdi/js'
import ConfigFieldRow from './components/cards/ConfigFieldRow.vue'
import ScheduleCard from './components/cards/ScheduleCard.vue'
import NotifyCard from './components/cards/NotifyCard.vue'
import SubfillRuleEditor from './components/SubfillRuleEditor.vue'
import { bindReplicaCards, completeReplicaCards, composeSharedReplicaCards, createReplicaFieldControlProps, isReplicaFieldVisible } from './model/replica-field-bindings.js'
// Map mdi icon names from tabs.js to SVG path data for native rendering
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
}
function iconPath(name) {
  return iconPaths[name] || mdiCogOutline
}

const faShieldHalvedPath = 'M256 0c4.6 0 9.2 1 13.4 2.9L457.7 82.8c22 9.3 38.4 31 38.3 57.2c-.5 99.2-41.3 280.7-213.6 363.2c-16.7 8-36.1 8-52.8 0C57.3 420.7 16.5 239.2 16 140c-.1-26.2 16.3-47.9 38.3-57.2L242.7 2.9C246.8 1 251.4 0 256 0zm0 66.8V444.8C394 378 431.1 230.1 432 141.4L256 66.8l0 0z'
const faGaugePath = 'M0 256a256 256 0 1 1 512 0A256 256 0 1 1 0 256zm320 96c0-26.9-16.5-49.9-40-59.3V88c0-13.3-10.7-24-24-24s-24 10.7-24 24V292.7c-23.5 9.5-40 32.5-40 59.3c0 35.3 28.7 64 64 64s64-28.7 64-64zM144 176a32 32 0 1 0 0-64 32 32 0 1 0 0 64zm-16 80a32 32 0 1 0 -64 0 32 32 0 1 0 64 0zm288 32a32 32 0 1 0 0-64 32 32 0 1 0 0 64zM400 144a32 32 0 1 0 -64 0 32 32 0 1 0 64 0z'
const faIdCardPath = 'M0 96l576 0c0-35.3-28.7-64-64-64H64C28.7 32 0 60.7 0 96zm0 32V416c0 35.3 28.7 64 64 64H512c35.3 0 64-28.7 64-64V128H0zM64 405.3c0-29.5 23.9-53.3 53.3-53.3H234.7c29.5 0 53.3 23.9 53.3 53.3c0 5.9-4.8 10.7-10.7 10.7H74.7c-5.9 0-10.7-4.8-10.7-10.7zM176 192a64 64 0 1 1 0 128 64 64 0 1 1 0-128zm176 16c0-8.8 7.2-16 16-16H496c8.8 0 16 7.2 16 16s-7.2 16-16 16H368c-8.8 0-16-7.2-16-16zm0 64c0-8.8 7.2-16 16-16H496c8.8 0 16 7.2 16 16s-7.2 16-16 16H368c-8.8 0-16-7.2-16-16zm0 64c0-8.8 7.2-16 16-16H496c8.8 0 16 7.2 16 16s-7.2 16-16 16H368c-8.8 0-16-7.2-16-16z'
const faBellPath = 'M224 0c-17.7 0-32 14.3-32 32V51.2C119 66 64 130.6 64 208v18.8c0 47-17.3 92.4-48.5 127.6l-7.4 8.3c-8.4 9.4-10.4 22.9-5.3 34.4S19.4 416 32 416H416c12.6 0 24-7.4 29.2-18.9s3.1-25-5.3-34.4l-7.4-8.3C401.3 319.2 384 273.9 384 226.8V208c0-77.4-55-142-128-156.8V32c0-17.7-14.3-32-32-32zm45.3 493.3c12-12 18.7-28.3 18.7-45.3H224 160c0 17 6.7 33.3 18.7 45.3s28.3 18.7 45.3 18.7s33.3-6.7 45.3-18.7z'
const faChartLinePath = 'M64 64c0-17.7-14.3-32-32-32S0 46.3 0 64V400c0 44.2 35.8 80 80 80H480c17.7 0 32-14.3 32-32s-14.3-32-32-32H80c-8.8 0-16-7.2-16-16V64zm406.6 86.6c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L320 210.7l-57.4-57.4c-12.5-12.5-32.8-12.5-45.3 0l-112 112c-12.5 12.5-12.5 32.8 0 45.3s32.8 12.5 45.3 0L240 221.3l57.4 57.4c12.5 12.5 32.8 12.5 45.3 0l128-128z'
const faDownloadPath = 'M288 32c0-17.7-14.3-32-32-32s-32 14.3-32 32V274.7l-73.4-73.4c-12.5-12.5-32.8-12.5-45.3 0s-12.5 32.8 0 45.3l128 128c12.5 12.5 32.8 12.5 45.3 0l128-128c12.5-12.5 12.5-32.8 0-45.3s-32.8-12.5-45.3 0L288 274.7V32zM64 352c-35.3 0-64 28.7-64 64v32c0 35.3 28.7 64 64 64H448c35.3 0 64-28.7 64-64V416c0-35.3-28.7-64-64-64H346.5l-45.3 45.3c-25 25-65.5 25-90.5 0L165.5 352H64zm368 56a24 24 0 1 1 0 48 24 24 0 1 1 0-48z'
const faHeartPulsePath = 'M228.3 469.1L47.6 300.4c-4.2-3.9-8.2-8.1-11.9-12.4h87c22.6 0 43-13.6 51.7-34.5l10.5-25.2 49.3 109.5c3.8 8.5 12.1 14 21.4 14.1s17.8-5 22-13.3L320 253.7l1.7 3.4c9.5 19 28.9 31 50.1 31H476.3c-3.7 4.3-7.7 8.5-11.9 12.4L283.7 469.1c-7.5 7-17.4 10.9-27.7 10.9s-20.2-3.9-27.7-10.9zM503.7 240h-132c-3 0-5.8-1.7-7.2-4.4l-23.2-46.3c-4.1-8.1-12.4-13.3-21.5-13.3s-17.4 5.1-21.5 13.3l-41.4 82.8L205.9 158.2c-3.9-8.7-12.7-14.3-22.2-14.1s-18.1 5.9-21.8 14.8l-31.8 76.3c-1.2 3-4.2 4.9-7.4 4.9H16c-2.6 0-5 .4-7.3 1.1C3 225.2 0 208.2 0 190.9v-5.8c0-69.9 50.5-129.5 119.4-141C165 36.5 211.4 51.4 244 84l12 12 12-12c32.6-32.6 79-47.5 124.6-39.9C461.5 55.6 512 115.2 512 185.1v5.8c0 16.9-2.8 33.5-8.3 49.1z'
const faPuzzlePiecePath = 'M192 104.8c0-9.2-5.8-17.3-13.2-22.8C167.2 73.3 160 61.3 160 48c0-26.5 28.7-48 64-48s64 21.5 64 48c0 13.3-7.2 25.3-18.8 34c-7.4 5.5-13.2 13.6-13.2 22.8v0c0 12.8 10.4 23.2 23.2 23.2H336c26.5 0 48 21.5 48 48v56.8c0 12.8 10.4 23.2 23.2 23.2v0c9.2 0 17.3-5.8 22.8-13.2c8.7-11.6 20.7-18.8 34-18.8c26.5 0 48 28.7 48 64s-21.5 64-48 64c-13.3 0-25.3-7.2-34-18.8c-5.5-7.4-13.6-13.2-22.8-13.2v0c-12.8 0-23.2 10.4-23.2 23.2V464c0 26.5-21.5 48-48 48H279.2c-12.8 0-23.2-10.4-23.2-23.2v0c0-9.2 5.8-17.3 13.2-22.8c11.6-8.7 18.8-20.7 18.8-34c0-26.5-28.7-48-64-48s-64 21.5-64 48c0 13.3 7.2 25.3 18.8 34c7.4 5.5 13.2 13.6 13.2 22.8v0c0 12.8-10.4 23.2-23.2 23.2H48c-26.5 0-48-21.5-48-48V343.2C0 330.4 10.4 320 23.2 320v0c9.2 0 17.3 5.8 22.8 13.2C54.7 344.8 66.7 352 80 352c26.5 0 48-28.7 48-64s-21.5-64-48-64c-13.3 0-25.3 7.2-34 18.8C40.5 250.2 32.4 256 23.2 256v0C10.4 256 0 245.6 0 232.8V176c0-26.5 21.5-48 48-48H168.8c12.8 0 23.2-10.4 23.2-23.2v0z'
const faTvPath = 'M64 64V352H576V64H64zM0 64C0 28.7 28.7 0 64 0H576c35.3 0 64 28.7 64 64V352c0 35.3-28.7 64-64 64H64c-35.3 0-64-28.7-64-64V64zM128 448H512c17.7 0 32 14.3 32 32s-14.3 32-32 32H128c-17.7 0-32-14.3-32-32s14.3-32 32-32z'
const faCirclePlusPath = 'M256 512A256 256 0 1 0 256 0a256 256 0 1 0 0 512zM232 344V280H168c-13.3 0-24-10.7-24-24s10.7-24 24-24h64V168c0-13.3 10.7-24 24-24s24 10.7 24 24v64h64c13.3 0 24 10.7 24 24s-10.7 24-24 24H280v64c0 13.3-10.7 24-24 24s-24-10.7-24-24z'
const faArrowsRotatePath = 'M105.1 202.6c7.7-21.8 20.2-42.3 37.8-59.8c62.5-62.5 163.8-62.5 226.3 0L386.3 160H336c-17.7 0-32 14.3-32 32s14.3 32 32 32H463.5c0 0 0 0 0 0h.4c17.7 0 32-14.3 32-32V64c0-17.7-14.3-32-32-32s-32 14.3-32 32v51.2L414.4 97.6c-87.5-87.5-229.3-87.5-316.8 0C73.2 122 55.6 150.7 44.8 181.4c-5.9 16.7 2.9 34.9 19.5 40.8s34.9-2.9 40.8-19.5zM39 289.3c-5 1.5-9.8 4.2-13.7 8.2c-4 4-6.7 8.8-8.1 14c-.3 1.2-.6 2.5-.8 3.8c-.3 1.7-.4 3.4-.4 5.1V448c0 17.7 14.3 32 32 32s32-14.3 32-32V396.9l17.6 17.5l0 0c87.5 87.4 229.3 87.4 316.7 0c24.4-24.4 42.1-53.1 52.9-83.7c5.9-16.7-2.9-34.9-19.5-40.8s-34.9 2.9-40.8 19.5c-7.7 21.8-20.2 42.3-37.8 59.8c-62.5 62.5-163.8 62.5-226.3 0l-.1-.1L125.6 352H176c17.7 0 32-14.3 32-32s-14.3-32-32-32H48.4c-1.6 0-3.2 .1-4.8 .3s-3.1 .5-4.6 1z'
const faFloppyDiskPath = 'M64 32C28.7 32 0 60.7 0 96V416c0 35.3 28.7 64 64 64H384c35.3 0 64-28.7 64-64V173.3c0-17-6.7-33.3-18.7-45.3L352 50.7C340 38.7 323.7 32 306.7 32H64zm0 96c0-17.7 14.3-32 32-32H288c17.7 0 32 14.3 32 32v64c0 17.7-14.3 32-32 32H96c-17.7 0-32-14.3-32-32V128zM224 288a64 64 0 1 1 0 128 64 64 0 1 1 0-128z'
const faPowerOffPath = 'M288 32c0-17.7-14.3-32-32-32s-32 14.3-32 32V256c0 17.7 14.3 32 32 32s32-14.3 32-32V32zM143.5 120.6c13.6-11.3 15.4-31.5 4.1-45.1s-31.5-15.4-45.1-4.1C49.7 115.4 16 181.8 16 256c0 132.5 107.5 240 240 240s240-107.5 240-240c0-74.2-33.8-140.6-86.6-184.6c-13.6-11.3-33.8-9.4-45.1 4.1s-9.4 33.8 4.1 45.1c38.9 32.3 63.5 81 63.5 135.4c0 97.2-78.8 176-176 176s-176-78.8-176-176c0-54.4 24.7-103.1 63.5-135.4z'
const faCalendarPath = 'M96 32V64H48C21.5 64 0 85.5 0 112v48H448V112c0-26.5-21.5-48-48-48H352V32c0-17.7-14.3-32-32-32s-32 14.3-32 32V64H160V32c0-17.7-14.3-32-32-32S96 14.3 96 32zM448 192H0V464c0 26.5 21.5 48 48 48H400c26.5 0 48-21.5 48-48V192z'
const faClockPath = 'M256 0a256 256 0 1 1 0 512A256 256 0 1 1 256 0zM232 120V256c0 8 4 15.5 10.7 20l96 64c11 7.4 25.9 4.4 33.3-6.7s4.4-25.9-6.7-33.3L280 243.2V120c0-13.3-10.7-24-24-24s-24 10.7-24 24z'
const faListOlPath = 'M24 56c0-13.3 10.7-24 24-24H80c13.3 0 24 10.7 24 24V176h16c13.3 0 24 10.7 24 24s-10.7 24-24 24H40c-13.3 0-24-10.7-24-24s10.7-24 24-24H56V80H48C34.7 80 24 69.3 24 56zM86.7 341.2c-6.5-7.4-18.3-6.9-24 1.2L51.5 357.9c-7.7 10.8-22.7 13.3-33.5 5.6s-13.3-22.7-5.6-33.5l11.1-15.6c23.7-33.2 72.3-35.6 99.2-4.9c21.3 24.4 20.8 60.9-1.1 84.7L86.8 432H120c13.3 0 24 10.7 24 24s-10.7 24-24 24H32c-9.5 0-18.2-5.6-22-14.4s-2.1-18.9 4.3-25.9l72-78c5.3-5.8 5.4-14.6 .3-20.5zM224 64H480c17.7 0 32 14.3 32 32s-14.3 32-32 32H224c-17.7 0-32-14.3-32-32s14.3-32 32-32zm0 160H480c17.7 0 32 14.3 32 32s-14.3 32-32 32H224c-17.7 0-32-14.3-32-32s14.3-32 32-32zm0 160H480c17.7 0 32 14.3 32 32s-14.3 32-32 32H224c-17.7 0-32-14.3-32-32s14.3-32 32-32z'
const replicaFieldFaIcons = {
  'mdi-power-standby': { path: faPowerOffPath, viewBox: '0 0 512 512' },
  'mdi-calendar-clock': { path: faCalendarPath, viewBox: '0 0 448 512' },
  'mdi-format-list-numbered': { path: faListOlPath, viewBox: '0 0 512 512' },
}
import { DEFAULT_DLTAG_CRON, defaults } from './model/defaults'
import { emitConfigSave } from './model/save-payload'
import { normalizeCurrentConfig } from './model/config-normalization.js'
import { deriveEffectiveState, EFFECTIVE_STATE } from './model/effective-state.js'
import { parseSubfillRules, validateSubfillRule } from './model/subfill-rules.js'
import { mainTabs, subTabs } from './model/tabs'
import {
  subscribeSubtypeItems, notificationTypeItems, messageTypeItems,
  siteStatRangeItems, marketNotifyItems, mpUpdateTypes, marketUpdateStrategies,
  keepCountPresets, logRowsPresets, seedActionsItems,
  dltagTaskItems, dltagDeleteStrategyItems,
  subfillDetailItems, msgGroupItems, healthCheckItems, healthDatabaseTargets,
  healthStorageTargets, healthDirectoryTargets, healthChipLabels,
} from './model/items'
import { useBackupRestore } from './composables/useBackupRestore'
import { useDataLoader } from '../../shared/composables/useDataLoader'
import { useActionRunner } from '../../shared/composables/useActionRunner'
import { useSignalTheme } from '../../shared/composables/useSignalTheme.js'

const props = defineProps({
  api: { type: [Object, Function], default: null },
  initialConfig: { type: Object, default: () => ({}) },
  pluginId: { type: String, default: 'Signal' },
  configRecordState: {
    type: String,
    default: 'unknown',
    validator: value => ['unknown', 'absent', 'present'].includes(value),
  },
})
const emit = defineEmits(['save', 'close', 'switch'])
const { rootThemeClass } = useSignalTheme()

const form = reactive({})
const subfillRulesValid = computed(() => {
  if (!form.subfill_category_enabled) return true
  const rules = parseSubfillRules(form.subfill_category_confs)
  return rules.length > 0 && rules.every(rule => validateSubfillRule(rule).length === 0)
})
const activeMain = ref('notify')
const activeSub = ref('fusion')
const subfillProjectionOpen = ref(false)
const configRoot = ref(null)
const mainNav = ref(null)
const subtabList = ref(null)
let dialogScrollHost = null
let dialogSurfaceHost = null

// Manual action state
// === 运行数据与动作编排 ===
const {
  installedPlugins, installedLoading, loadInstalledPlugins,
  tgConsoleStatus, tgConsoleLoading, loadTgConsoleStatus,
  pluginMarkets, marketsLoading, loadPluginMarkets,
  downloaderOptions, downloadersLoading, loadDownloaders,
  mediaserverOptions, mediaserversLoading, loadMediaservers,
} = useDataLoader(props.api)

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
}))

const {
  action, actionDisabledReason, notificationLockedByFusion,
  actionComponentDisabledMessage, runAction,
} = useActionRunner(form, props.api, installedPlugins, loadInstalledPlugins)

const {
  backupArchives, backupArchivesLoading, backupRestoreLoading, backupRestoreResult, backupRestore,
  webdavBackupArchives, webdavBackupArchivesLoading, webdavBackupRestoreLoading, webdavBackupRestoreResult, webdavBackupRestore,
  backupRestoreUnavailable, backupRestoreUnavailableMessage,
  webdavBackupRestoreUnavailable, webdavBackupRestoreUnavailableMessage,
  loadBackupArchives, loadWebdavBackupArchives,
  previewBackupRestore, previewWebdavBackupRestore,
  runBackupRestore, runWebdavBackupRestore,
} = useBackupRestore(form, props.api)

const currentMain = computed(() => mainTabs.find(item => item.key === activeMain.value) || mainTabs[0])
const currentSubs = computed(() => subTabs[activeMain.value] || [])
const currentSub = computed(() => currentSubs.value.find(item => item.key === activeSub.value) || currentSubs.value[0] || null)
const currentSubTitle = computed(() => currentSub.value?.title || currentMain.value?.title || '')
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
}
const currentHero = computed(() => heroMap[activeSub.value] || heroMap.fusion)
const heroIconPath = computed(() => activeSub.value === 'fusion' ? faIdCardPath : iconPath(currentSub.value?.icon || 'mdi-cog-outline'))
const heroIconViewBox = computed(() => activeSub.value === 'fusion' ? '0 0 576 512' : '0 0 24 24')
const updateMasterState = computed(() => {
  const mpEnabled = Boolean(form.mp_update_enabled)
  const marketEnabled = Boolean(form.market_update_enabled)
  if (mpEnabled && marketEnabled) return 'on'
  if (!mpEnabled && !marketEnabled) return 'off'
  return 'mixed'
})
const heroMixed = computed(() => activeSub.value === 'updates' && updateMasterState.value === 'mixed')
const pluginEnabled = computed(() => form.enabled !== false)
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
}
function hasConfiguredValue(value) {
  if (Array.isArray(value)) return value.length > 0
  return String(value ?? '').trim().length > 0
}
function effectiveStateFor(subKey) {
  const input = effectiveStateInputs[subKey] || {}
  const enabledKeys = input.enabledKeys || (input.enabledKey ? [input.enabledKey] : [])
  const scheduleKeys = input.scheduleKeys || (input.scheduleKey ? [input.scheduleKey] : [])
  const cronKeys = input.cronKeys || []
  const componentEnabled = input.selectionKey
    ? hasConfiguredValue(form[input.selectionKey])
    : (enabledKeys.length ? enabledKeys.every(key => form[key] !== false) : true)
  const requiredConfigReady = (input.requiredKeys || []).every(key => hasConfiguredValue(form[key]))
  const scheduleEnabled = scheduleKeys.length ? scheduleKeys.every(key => form[key] !== false) : true
  const allCronReady = cronKeys.every(key => hasConfiguredValue(form[key]))
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
const currentEffectiveState = computed(() => effectiveStateFor(activeSub.value))
const mainEffectiveState = (mainKey) => {
  if (!pluginEnabled.value) return EFFECTIVE_STATE.PLUGIN_DISABLED
  const states = (subTabs[mainKey] || []).map(item => effectiveStateFor(item.key).code)
  return states.includes(EFFECTIVE_STATE.ACTIVE) ? EFFECTIVE_STATE.ACTIVE : (states[0] || EFFECTIVE_STATE.COMPONENT_DISABLED)
}
const heroEnabled = computed(() => {
  const key = activeSub.value
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
})
const heroEffectivelyEnabled = computed(() => pluginEnabled.value && heroEnabled.value)
const heroEffectivelyMixed = computed(() => pluginEnabled.value && heroMixed.value)
const currentHeroTitle = computed(() => {
  if (currentEffectiveState.value.code === EFFECTIVE_STATE.PLUGIN_DISABLED) return '插件已停用'
  return heroMixed.value ? currentHero.value.mixed : (heroEnabled.value ? currentHero.value.on : currentHero.value.off)
})
const heroStatusText = computed(() => {
  if (currentEffectiveState.value.code === EFFECTIVE_STATE.PLUGIN_DISABLED) return '已停用'
  return heroMixed.value ? '部分启用' : (heroEnabled.value ? '运行中' : '待启用')
})
const heroToggleLabel = computed(() => heroMixed.value
  ? `${currentHero.value.kicker}总开关，当前部分启用，点击后全部启用`
  : `${currentHero.value.kicker}总开关`)

const remoteBackupReady = computed(() => [
  form.backup_webdav_hostname,
  form.backup_webdav_login,
  form.backup_webdav_password,
].every(value => String(value || '').trim().length > 0))

function setHeroEnabled(value) {
  const key = activeSub.value
  const toggle = (enabledKey, scheduleKey) => {
    form[enabledKey] = value
    if (scheduleKey) form[scheduleKey] = value
  }
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
      toggle('mp_update_enabled', 'mp_update_schedule_enabled')
      toggle('market_update_enabled', 'market_update_schedule_enabled')
      return
  }
}

const compactOperationalSubtabs = new Set(['subscribe', 'sites', 'hc', 'seedremove', 'dltagmain', 'logs'])
const hiddenDownloaderHelperCompatibilityFieldKeys = Object.freeze([
  'dltag_all_tags',
  'dltag_excluded_tags',
])
const compactNotificationLabels = Object.freeze({
  subscribe_reminder_msgtype: '通知渠道',
  site_stat_notify_type: '通知渠道',
  health_check_notify_type: '通知渠道',
  dltag_notify_type: '通知渠道',
  log_clean_notify_type: '通知渠道',
  backup_notify_type: '通知渠道',
})

function compactOperationalCards(cardsBySubtab, fusionEnabled) {
  const result = { ...cardsBySubtab }
  for (const subtab of compactOperationalSubtabs) {
    const cards = cardsBySubtab[subtab] || []
    const preserveExpandedFields = subtab === 'seedremove'
    const actions = cards.filter(card => card.type === 'actions')
    const compactCard = card => ({
      ...card,
      fields: (card.fields || []).map(field => {
        const isManagedChannel = Boolean(
          fusionEnabled &&
          card.type === 'notify' &&
          card.fusionManaged &&
          card.fusionChannelOnly &&
          compactNotificationLabels[field.key],
        )
        return {
          ...field,
          label: compactNotificationLabels[field.key] || field.label,
          fullRow: preserveExpandedFields ? Boolean(field.fullRow) : false,
          compactMulti: preserveExpandedFields ? false : Boolean(field.multiple || field.chips),
          compactSelection: Boolean(field.compactSelection),
          disabled: Boolean(field.disabled || isManagedChannel),
        }
      }),
    })
    if (subtab === 'seedremove') {
      result[subtab] = [
        ...cards.filter(card => card.type !== 'actions').map(compactCard),
        ...actions,
      ]
      continue
    }
    if (subtab === 'dltagmain') {
      const advancedCards = cards.filter(card => card.type === 'advanced').map(compactCard)
      const fields = cards
        .filter(card => card.type !== 'actions' && card.type !== 'advanced')
        .flatMap(card => compactCard(card).fields)
        .filter(field => !hiddenDownloaderHelperCompatibilityFieldKeys.includes(field.key))
      result[subtab] = [{
        type: 'section',
        icon: 'mdi-tune-variant',
        title: '配置项',
        grid: 'grid-2',
        fields,
        compactOperational: true,
      }, ...advancedCards, ...actions]
      continue
    }
    const fields = cards
      .filter(card => card.type !== 'actions')
      .flatMap(card => compactCard(card).fields)
    result[subtab] = [{
      type: 'section',
      icon: 'mdi-tune-variant',
      title: '配置项',
      grid: 'grid-2',
      fields,
      compactOperational: true,
    }, ...actions]
  }
  return result
}

const replicaCards = computed(() => {
  const onOff = v => v ? 'ON' : 'OFF'
  const valOr = (v, fb = '未配置') => v || fb
  const arrCount = (arr, suffix = '个') => Array.isArray(arr) && arr.length ? `${arr.length} ${suffix}` : '未配置'
  const arrNames = (arr) => Array.isArray(arr) && arr.length ? arr.join('、') : '全部'
  const cronVal = v => v || '未设置'
  const dltagTasks = Array.isArray(form.dltag_tasks) ? form.dltag_tasks : []
  const dltagTaggingActive = dltagTasks.includes('tagging') || Boolean(form.dltag_listen_download)
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
        { key: 'backup_path', icon: 'mdi-folder-outline', label: '本地路径', value: valOr(form.backup_path, '/config/plugins/Signal/Backup') },
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
  }), replicaItemSources.value))
  return compactOperationalCards(cards, Boolean(form.fusion_notify_enabled))
})
const currentReplicaCards = computed(() => replicaCards.value[activeSub.value] || replicaCards.value.fusion)
const settingCards = computed(() => currentReplicaCards.value.filter(card => card.type !== 'actions'))
const actionCards = computed(() => currentReplicaCards.value.filter(card => card.type === 'actions'))
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
}
const currentActionHint = computed(() => configActionHints[activeSub.value] || '')
const fusionTakeoverNoticeBySub = Object.freeze({
  server: '融合通知已接管媒体通知，消息将统一汇入 Telegram 卡片。',
  subscribe: '融合通知仅接管通知渠道；检查时间和订阅类型仍可编辑。',
  sites: '融合通知仅接管通知渠道；统计时间和数据范围仍可编辑。',
  hc: '融合通知仅接管通知渠道；巡查时间、阈值和巡查范围仍可编辑。',
  seedremove: '融合通知仅接管自动删种的通知渠道；执行时间和清理规则仍可编辑。',
  dltagmain: '融合通知已接管下载器助手的通知渠道，任务和清理设置仍由你控制。',
  logs: '融合通知只接管日志清理的通知渠道；Cron、清理范围和定时执行后通知仍由你控制。',
  updates: '融合通知只接管更新检查的通知渠道；Cron、检查范围、处理方式和定时执行后通知仍由你控制。',
})
const fusionTakeoverNotice = computed(() => {
  if (!form.fusion_notify_enabled) return null
  if (activeSub.value === 'dltagmain' && !form.dltag_scheduled_notify) return null
  return fusionTakeoverNoticeBySub[activeSub.value] || null
})
const seedCleanRiskNotice = computed(() => activeSub.value === 'seedremove'
  ? '自动删种会按当前筛选条件暂停或删除任务；执行前请确认动作与范围。'
  : null)

const seedCleanConfirmOpen = ref(false)
const downloaderHelperConfirmOpen = ref(false)
const pluginUninstallConfirmOpen = ref(false)
const seedCleanPortalStyle = ref({})
const downloaderHelperPreviewItems = computed(() => action.downloaderHelperPreview?.items || [])
const selectedPluginUninstallItems = computed(() => {
  const selected = Array.isArray(form.plugin_uninstall_ids) ? form.plugin_uninstall_ids : []
  const installed = installedPlugins.value || []
  return selected.map(id => {
    const value = String(id)
    const item = installed.find(candidate => String(candidate?.value ?? candidate?.id ?? candidate?.title ?? candidate) === value)
    return { value, title: String(item?.title ?? item?.name ?? value) }
  })
})
const pluginUninstallActionItems = computed(() => [
  { key: 'plugin_uninstall_remove_plugin', label: '卸载插件本体', detail: '移出已安装列表并停止运行实例' },
  { key: 'plugin_uninstall_clear_config', label: '清除插件配置', detail: '删除 MoviePilot 保存的插件配置' },
  { key: 'plugin_uninstall_clear_data', label: '清除插件数据', detail: '删除插件运行数据' },
  { key: 'plugin_uninstall_delete_source', label: '删除本地源码', detail: '删除本地插件源码目录' },
].filter(item => Boolean(form[item.key])))
const seedCleanActionMeta = computed(() => ({
  pause: { label: '暂停种子', confirm: '确认暂停', risk: '所选种子将停止上传和下载，可在下载器中重新开始。' },
  delete: { label: '删除种子', confirm: '确认删除', risk: '所选任务将从下载器移除，但保留已下载文件。' },
  deletefile: { label: '删除种子和文件', confirm: '确认删除种子和文件', risk: '所选任务及其已下载文件将被永久删除，无法恢复。' },
}[String(form.seedclean_action || 'pause')] || { label: '处理种子', confirm: '确认执行', risk: '将按当前动作处理匹配条件的种子。' }))
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
  ].filter(([, value]) => String(value || '').trim())
  return rows.length ? rows.map(([label, value]) => `${label}：${value}`).join('；') : '未设置筛选条件'
})

function openSeedCleanConfirmation() {
  const message = actionDisabledReason.value || actionComponentDisabledMessage('run_seed_clean')
  if (message) {
    action.ok = false
    action.message = message
    return
  }
  if (!Array.isArray(form.seedclean_downloaders) || !form.seedclean_downloaders.length) {
    action.ok = false
    action.message = '请先选择下载器。'
    return
  }
  if (seedCleanFilterSummary.value === '未设置筛选条件') {
    action.ok = false
    action.message = '请至少设置一项筛选条件。'
    return
  }
  if (typeof window !== 'undefined' && configRoot.value) {
    const computedStyle = window.getComputedStyle(configRoot.value)
    seedCleanPortalStyle.value = Array.from(computedStyle).reduce((tokens, name) => {
      if (name.startsWith('--signal-') || name.startsWith('--v-')) tokens[name] = computedStyle.getPropertyValue(name)
      return tokens
    }, {})
  }
  seedCleanConfirmOpen.value = true
}

function openPluginUninstallConfirmation() {
  const message = actionDisabledReason.value || actionComponentDisabledMessage('run_plugin_uninstall')
  if (message) {
    action.ok = false
    action.message = message
    return
  }
  if (!selectedPluginUninstallItems.value.length) {
    action.ok = false
    action.message = '请先选择要卸载的插件。'
    return
  }
  if (!pluginUninstallActionItems.value.length) {
    action.ok = false
    action.message = '请至少选择一项卸载或清理操作。'
    return
  }
  if (typeof window !== 'undefined' && configRoot.value) {
    const computedStyle = window.getComputedStyle(configRoot.value)
    seedCleanPortalStyle.value = Array.from(computedStyle).reduce((tokens, name) => {
      if (name.startsWith('--signal-') || name.startsWith('--v-')) tokens[name] = computedStyle.getPropertyValue(name)
      return tokens
    }, {})
  }
  pluginUninstallConfirmOpen.value = true
}

async function confirmSeedCleanExecution() {
  seedCleanConfirmOpen.value = false
  await runAction('run_seed_clean', '执行自动删种')
}

async function confirmDownloaderHelperExecution() {
  downloaderHelperConfirmOpen.value = false
  await runAction('run_downloader_helper', '执行下载器助手')
}

async function confirmPluginUninstallExecution() {
  pluginUninstallConfirmOpen.value = false
  await runAction('run_plugin_uninstall', '执行卸载')
}

async function triggerConfigAction(item) {
  if (!item) return
  if (item.path === 'run_seed_clean') {
    openSeedCleanConfirmation()
    return
  }
  if (item.path === 'run_plugin_uninstall') {
    openPluginUninstallConfirmation()
    return
  }
  await runAction(item.path, item.label)
  if (item.path === 'run_downloader_helper' && action.downloaderHelperPreview?.confirm_required) {
    downloaderHelperConfirmOpen.value = true
  }
}

watch(() => [
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
  seedCleanConfirmOpen.value = false
}, { deep: true })

watch(() => [form.dltag_downloaders, form.dltag_tasks], () => {
  action.downloaderHelperPreview = null
  downloaderHelperConfirmOpen.value = false
}, { deep: true })

function compactIcon(name, className = 'signal-mdi-icon') {
  const isSectionIcon = className.includes('signal-mdi-icon--section')
  const fieldFaIcon = className.includes('signal-mdi-icon--field') ? replicaFieldFaIcons[name] : null
  const sectionFaIcon = isSectionIcon && name === 'mdi-calendar-clock'
    ? { path: faClockPath, viewBox: '0 0 512 512' }
    : null
  const faIcon = fieldFaIcon || sectionFaIcon
  return h('svg', { class: className, viewBox: faIcon?.viewBox || '0 0 24 24', width: isSectionIcon ? '15' : '18', height: isSectionIcon ? '15' : '13', 'aria-hidden': 'true' }, [
    h('path', { d: faIcon?.path || iconPath(name), fill: 'currentColor' }),
  ])
}
function actionIcon(name) {
  const faActionIcons = {
    'mdi-plus-circle-outline': faCirclePlusPath,
    'mdi-sync': faArrowsRotatePath,
  }
  if (faActionIcons[name]) {
    return h('svg', { class: 'signal-mdi-icon signal-mdi-icon--action', viewBox: '0 0 512 512', width: '14', height: '14', 'aria-hidden': 'true' }, [
      h('path', { d: faActionIcons[name], fill: 'currentColor' }),
    ])
  }
  return compactIcon(name, 'signal-mdi-icon signal-mdi-icon--action')
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
  }[item?.key]
  return meta || { path: iconPath(item?.icon || 'mdi-cog-outline'), viewBox: '0 0 24 24' }
}
function navIconStyle(item, height = 14) {
  const [, , width, viewHeight] = navIconMeta(item).viewBox.split(/\s+/).map(Number)
  const naturalWidth = width && viewHeight ? (width / viewHeight) * height : height
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
])

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
      ? h('aside', { class: 'signal-seedclean-status-dictionary', 'data-seedclean-status-dictionary': '' }, [
          ...seedCleanStatusDictionaries.map(dictionary => h('section', {
            key: dictionary.key,
            class: 'signal-seedclean-status-dictionary__group',
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
      : null
    const renderFields = () => {
      const fields = (props.card.fields || []).filter(field => isReplicaFieldVisible(field, form))
      const children = fields.flatMap(field => {
        const groupHeading = field.groupLabel
          ? h('h4', {
              key: `${props.activeSub}-group-${field.layoutGroup}`,
              class: 'signal-config-field-group',
              'data-field-group-heading': field.layoutGroup,
            }, field.groupLabel)
          : null
        const fieldRow = h(ConfigFieldRow, {
          key: `${props.activeSub}-${field.key}`,
          'data-field-layout-group': field.layoutGroup || undefined,
          ...createReplicaFieldControlProps(form, {
            ...field,
            hideInlineLabel: true,
            hideDetails: true,
            density: 'compact',
          }),
        })
        return groupHeading ? [groupHeading, fieldRow] : [fieldRow]
      })
      return h('div', { class: ['signal-design-field-grid', `signal-design-field-grid--${props.card.grid || 'grid-3'}`] }, children)
    }
    return () => {
      if (props.card.type === 'advanced' && (!props.embedded || props.card.embeddedDrawer)) {
        return h('details', {
          class: ['signal-design-advanced', { 'signal-design-advanced--embedded': props.embedded }],
          'data-html-advanced': '',
          'data-seedclean-filter-drawer': props.card.dictionary === 'seedclean-status' ? '' : undefined,
          'data-dltag-tracker-drawer': props.card.drawer === 'dltag-tracker' ? '' : undefined,
          'data-default-open': 'false',
          'data-effective-state': props.effectiveState,
        }, [
          h('summary', [
            h('span', [compactIcon(props.card.icon, 'signal-mdi-icon'), props.card.title]),
            h('svg', { class: 'signal-design-advanced__chevron signal-mdi-icon', viewBox: '0 0 24 24', width: '15', height: '15', 'aria-hidden': 'true' }, [h('path', { d: mdiCogOutline, fill: 'currentColor' })]),
          ]),
          h('div', { class: 'signal-design-advanced-content' }, [
            props.card.note ? h('div', { class: 'signal-design-section-note' }, props.card.note) : null,
            renderFields(),
            renderDictionary(),
          ]),
        ])
      }
      const isPeerSection = Boolean(props.card.backupScope || props.card.type === 'module')
      return h('section', {
        class: ['signal-design-section-card', {
          'signal-design-section-card--danger': props.card.danger,
          'signal-update-module-card': props.card.type === 'module',
          'signal-design-section-card--embedded': props.embedded,
          'signal-design-section-card--peer': isPeerSection,
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
          ? h('div', { class: 'signal-design-section-title' }, [
              h('span', { class: 'signal-design-section-title__leading', 'aria-hidden': 'true' }, [
                compactIcon(props.card.icon, 'signal-mdi-icon signal-mdi-icon--section'),
              ]),
              h('span', { class: 'signal-design-section-title__text' }, props.card.title),
              h('span', { class: 'signal-design-section-title__trailing' }, [
                props.card.backupScope === 'remote'
                  ? h('small', { class: ['signal-design-section-status', props.card.backupReady ? 'signal-design-section-status--on' : 'signal-design-section-status--off'] }, props.card.backupReady ? '已启用' : '未启用')
                  : null,
              ]),
            ])
          : null,
        isPeerSection && props.card.note ? h('div', { class: 'signal-design-section-note' }, props.card.note) : null,
        renderFields(),
        props.card.actions?.length
          ? h(CompactActionRow, { card: { type: 'actions', actions: props.card.actions }, pluginEnabled: pluginEnabled.value, effectiveState: props.effectiveState, onRun: item => emit('run', item) })
          : null,
      ])
    }
  },
})

const CompactActionRow = defineComponent({
  name: 'CompactActionRow',
  props: { card: { type: Object, required: true }, pluginEnabled: { type: Boolean, default: true }, effectiveState: { type: String, default: '' } },
  emits: ['run'],
  setup(props, { emit }) {
    return () => {
      const actionButtons = (props.card.actions || []).map(actionItem => {
        const disabledBySelection = actionItem.path === 'run_plugin_uninstall'
          && (!Array.isArray(form.plugin_uninstall_ids) || form.plugin_uninstall_ids.length === 0)
        const disabledByPlugin = !props.pluginEnabled
        const isDisabled = disabledByPlugin || disabledBySelection || action.running === actionItem.path
        const title = disabledByPlugin
          ? '插件已停用，开启总开关后可执行'
          : disabledBySelection
          ? '请先选择要卸载的插件'
          : ''
        const buttonLabel = action.running === actionItem.path
          ? '正在执行...'
          : actionItem.label
        return h('button', {
          key: actionItem.label,
          type: 'button',
          class: ['signal-design-action-btn', {
            'signal-design-action-btn--danger': props.card.danger,
            'signal-design-action-btn--disabled': isDisabled,
          }],
          disabled: isDisabled,
          title,
          'data-config-action-path': actionItem.path,
          'data-effective-state': props.effectiveState || undefined,
          onClick: () => {
            if (isDisabled) return
            emit('run', actionItem)
          },
        }, [actionIcon(actionItem.icon), h('span', buttonLabel)])
      })

      return h('div', {
        class: ['signal-design-actions', {
          'signal-design-actions--danger': props.card.danger,
          'signal-design-actions--single': (props.card.actions || []).length === 1,
        }],
        'data-html-action-row': '',
      }, actionButtons)
    }
  },
})

watch([() => props.initialConfig, () => props.configRecordState], ([value, configRecordState]) => {
  Object.keys(form).forEach(key => delete form[key])
  const rawConfig = value || {}
  Object.assign(form, normalizeCurrentConfig(defaults), normalizeCurrentConfig(rawConfig))
  if (!Object.prototype.hasOwnProperty.call(rawConfig, 'dltag_cron')) {
    form.dltag_cron = DEFAULT_DLTAG_CRON
  }
  const inheritSchedule = (scheduleKey, enabledKey) => {
    if (!Object.prototype.hasOwnProperty.call(rawConfig, scheduleKey)) {
      form[scheduleKey] = !!form[enabledKey]
    }
  }
  inheritSchedule('subscribe_reminder_schedule_enabled', 'subscribe_reminder_enabled')
  inheritSchedule('health_check_schedule_enabled', 'health_check_enabled')
  inheritSchedule('log_clean_schedule_enabled', 'log_clean_enabled')
  inheritSchedule('mp_update_schedule_enabled', 'mp_update_enabled')
  inheritSchedule('market_update_schedule_enabled', 'market_update_enabled')
  inheritSchedule('seedclean_schedule_enabled', 'seedclean_enabled')
  const toArr = v => typeof v === 'string' ? v.split(',').map(s => s.trim()).filter(Boolean) : (Array.isArray(v) ? v : [])
  form.subscribe_reminder_subtype = toArr(form.subscribe_reminder_subtype)
  form.mp_update_types = toArr(form.mp_update_types)
  form.plugin_uninstall_ids = toArr(form.plugin_uninstall_ids)
  form.log_clean_selected_ids = toArr(form.log_clean_selected_ids)
  form.market_update_install_ids = toArr(form.market_update_install_ids)
  form.market_update_exclude_ids = toArr(form.market_update_exclude_ids)
  form.seedclean_downloaders = toArr(form.seedclean_downloaders)
  form.subfill_details = toArr(form.subfill_details)
  form.msgnotify_types = toArr(form.msgnotify_types)
  form.msgnotify_servers = toArr(form.msgnotify_servers)
  form.dltag_downloaders = toArr(form.dltag_downloaders)
  form.dltag_tasks = toArr(form.dltag_tasks)
  form.dltag_all_tags = toArr(form.dltag_all_tags)
  form.dltag_excluded_tags = toArr(form.dltag_excluded_tags)
  form.health_check_items = toArr(form.health_check_items)
  form.health_check_database_targets = toArr(form.health_check_database_targets)
  form.health_check_storage_targets = toArr(form.health_check_storage_targets)
  form.health_check_directory_targets = toArr(form.health_check_directory_targets)
}, { immediate: true, deep: true })

async function saveConfig() {
  if (!subfillRulesValid.value) {
    action.message = '二级分类规则存在错误，请先修正后再保存'
    action.ok = false
    return
  }
  const payload = emitConfigSave(emit, form)
  if (props.api?.put) {
    await props.api.put(`plugin/${props.pluginId}`, payload)
  } else if (typeof props.api === 'function') {
    await props.api({ method: 'put', url: `plugin/${props.pluginId}`, data: payload })
  }
}

function selectMain(key) {
  if (activeMain.value === key) return
  activeMain.value = key
  activeSub.value = subTabs[key]?.[0]?.key || ''
}

function revealCategoryItem(target, behavior = 'smooth') {
  const container = target?.closest?.('[data-config-nav-scroll]')
  if (!container) return
  const containerRect = container.getBoundingClientRect()
  const targetRect = target.getBoundingClientRect()
  const inset = 8
  let nextLeft = container.scrollLeft
  if (targetRect.left < containerRect.left + inset) {
    nextLeft -= containerRect.left + inset - targetRect.left
  } else if (targetRect.right > containerRect.right - inset) {
    nextLeft += targetRect.right - containerRect.right + inset
  }
  if (Math.abs(nextLeft - container.scrollLeft) > 1) {
    container.scrollTo({ left: nextLeft, behavior })
  }
}

function revealActiveCategories(behavior = 'smooth') {
  nextTick(() => {
    revealCategoryItem(mainNav.value?.querySelector('[aria-selected="true"]'), behavior)
    revealCategoryItem(subtabList.value?.querySelector('[aria-selected="true"]'), behavior)
  })
}

watch([activeMain, activeSub], () => revealActiveCategories())
watch(activeSub, value => {
  if (value !== 'subfill') subfillProjectionOpen.value = false
})

function switchPluginAppNav(navKey) {
  if (typeof window === 'undefined') return false
  const pluginAppPrefix = `#/plugin-app/${props.pluginId}/`
  if (!window.location.hash.startsWith(pluginAppPrefix)) return false
  window.location.hash = `${pluginAppPrefix}${navKey}`
  return true
}

function openDashboard() {
  if (switchPluginAppNav('main')) return
  emit('switch')
}

function bindDialogScrollHost() {
  const host = configRoot.value?.closest?.('.v-card-text.pa-0')
  if (!host || host === dialogScrollHost) return
  dialogScrollHost?.classList.remove('signal-config-scroll-host')
  dialogSurfaceHost?.classList.remove('signal-config-single-surface-host')
  dialogScrollHost = host
  dialogScrollHost.classList.add('signal-config-scroll-host')
  dialogSurfaceHost = host.closest?.('.v-card') || null
  dialogSurfaceHost?.classList.add('signal-config-single-surface-host')
}

onMounted(() => {
  bindDialogScrollHost()
  revealActiveCategories('auto')
  loadInstalledPlugins()
  loadTgConsoleStatus()
  loadBackupArchives()
  loadWebdavBackupArchives()
  loadPluginMarkets()
  loadDownloaders()
  loadMediaservers()
})

onBeforeUnmount(() => {
  dialogScrollHost?.classList.remove('signal-config-scroll-host')
  dialogSurfaceHost?.classList.remove('signal-config-single-surface-host')
  dialogScrollHost = null
  dialogSurfaceHost = null
})
</script>
<template>
  <div ref="configRoot" class="signal-config signal-root signal-plugin-shell" :class="rootThemeClass" data-config-shell :data-effective-state="currentEffectiveState.code">
      <header class="signal-config-top-bar" data-config-top-bar>
        <div class="signal-config-brand">
          <span class="signal-config-brand-icon">
            <svg class="signal-mdi-icon signal-mdi-icon--brand" viewBox="0 0 512 512" width="20" height="20" aria-hidden="true"><path :d="faShieldHalvedPath" fill="currentColor"/></svg>
          </span>
          <span class="signal-config-brand-copy">
            <strong>MP 运维助手</strong>
            <small>配置中心</small>
          </span>
        </div>
        <div class="signal-config-top-actions">
          <div class="signal-config-master-switch">
            <span class="signal-config-master-switch__label">插件总开关</span>
            <button
              type="button"
              class="signal-toggle-switch"
              :class="{ 'signal-toggle-switch--on': form.enabled }"
              role="switch"
              :aria-checked="!!form.enabled"
              :aria-label="'插件总开关'"
              @click="form.enabled = !form.enabled"
            ><span class="signal-toggle-switch__thumb"></span></button>
          </div>
          <button
            type="button"
            class="signal-config-ghost-btn"
            data-config-dashboard-button
            :title="'仪表盘'"
            :aria-label="'仪表盘'"
            @click="openDashboard"
          ><svg class="signal-mdi-icon signal-mdi-icon--ghost" viewBox="0 0 512 512" width="12" height="12" aria-hidden="true"><path :d="faGaugePath" fill="currentColor"/></svg><span>仪表盘</span></button>
        </div>
      </header>
      <nav ref="mainNav" class="signal-config-main-nav" data-config-main-nav data-config-nav-scroll="main" aria-label="配置分类" role="tablist">
        <button
          v-for="item in mainTabs"
          :key="item.key"
          type="button"
          class="signal-config-main-tab"
          :class="{ 'signal-config-main-tab--active': activeMain === item.key }"
          role="tab"
          :aria-selected="activeMain === item.key"
           :data-config-main-tab="item.key"
           :data-effective-state="mainEffectiveState(item.key)"
          @click="selectMain(item.key)"
          @focus="revealCategoryItem($event.currentTarget, 'auto')"
        >
          <svg class="signal-mdi-icon signal-mdi-icon--nav" :viewBox="navIconMeta(item).viewBox" :style="navIconStyle(item, 14)" aria-hidden="true"><path :d="navIconMeta(item).path" fill="currentColor"/></svg>
          <span>{{ item.title }}</span>
        </button>
      </nav>

      <div class="signal-config-subtab-bar" data-config-subtab-bar>
        <div ref="subtabList" class="signal-subtab-list" data-config-nav-scroll="sub" role="tablist" :aria-label="`${currentMain.title} 二级分类`">
          <button
            v-for="sub in currentSubs"
            :key="sub.key"
            type="button"
            :id="`config-tab-${sub.key}`"
            class="signal-subtab"
            :class="{ 'signal-subtab--active': activeSub === sub.key }"
            role="tab"
            :aria-selected="activeSub === sub.key"
            :aria-controls="`config-panel-${sub.key}`"
             :data-config-subtab="sub.key"
             :data-effective-state="effectiveStateFor(sub.key).code"
            @click="activeSub = sub.key"
            @focus="revealCategoryItem($event.currentTarget, 'auto')"
          >
            <svg class="signal-mdi-icon signal-mdi-icon--subtab" :viewBox="navIconMeta(sub).viewBox" :style="navIconStyle(sub, 13)" aria-hidden="true"><path :d="navIconMeta(sub).path" fill="currentColor"/></svg>
            <span>{{ sub.title }}</span>
          </button>
        </div>
        <div v-if="currentSubTitle" class="signal-config-subtab-current" aria-live="polite">
          {{ currentSubTitle }}
        </div>
      </div>

      <main
        :id="`config-panel-${activeSub}`"
        class="signal-config-scroll"
        data-config-scroll
        :aria-labelledby="`config-tab-${activeSub}`"
        :data-config-active-sub="activeSub"
        :data-effective-state="currentEffectiveState.code"
      >
        <section class="signal-config-hero-card" data-config-active-card aria-live="polite" :data-effective-state="currentEffectiveState.code">
          <div class="signal-config-hero-left">
            <span class="signal-config-hero-icon">
                    <svg class="signal-mdi-icon signal-mdi-icon--hero" :viewBox="heroIconViewBox" width="25" height="22" aria-hidden="true"><path :d="heroIconPath" fill="currentColor"/></svg>
            </span>
            <span class="signal-config-hero-info">
              <span class="signal-config-hero-kicker">{{ currentHero.kicker }}</span>
              <strong class="signal-config-hero-title">{{ currentHeroTitle }}</strong>
              <small class="signal-config-hero-desc">{{ currentHero.desc }}</small>
            </span>
          </div>
          <div v-if="activeSub !== 'clean'" class="signal-config-hero-right">
            <span class="signal-config-status-badge" :class="{ 'signal-config-status-badge--on': heroEffectivelyEnabled, 'signal-config-status-badge--mixed': heroEffectivelyMixed }">{{ heroStatusText }}</span>
            <button
              type="button"
              class="signal-toggle-switch signal-toggle-switch--hero"
              :class="{ 'signal-toggle-switch--on': heroEffectivelyEnabled }"
              role="switch"
              :aria-checked="!!heroEnabled"
              :aria-label="heroToggleLabel"
              :data-config-aggregate-state="activeSub === 'updates' ? updateMasterState : undefined"
              @click="setHeroEnabled(!heroEnabled)"
            >
              <span class="signal-toggle-switch__thumb" />
            </button>
          </div>
          <div v-else class="signal-config-hero-right signal-config-hero-right--danger" data-config-danger-header>
            <span class="signal-config-status-badge">高风险操作</span>
          </div>
        </section>

        <div
          v-if="fusionTakeoverNotice"
          class="signal-fusion-takeover-note"
          data-config-notice-tone="blue"
          role="status"
        >
          <svg class="signal-mdi-icon signal-fusion-takeover-note__icon" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path :d="iconPath('mdi-shield-check-outline')" fill="currentColor"/></svg>
          <span>{{ fusionTakeoverNotice }}</span>
        </div>
        <div
          v-if="seedCleanRiskNotice"
          class="signal-fusion-takeover-note signal-config-risk-note--orange"
          data-config-notice-tone="orange"
          data-config-notice-icon="warning"
          role="status"
        >
          <svg class="signal-mdi-icon signal-fusion-takeover-note__icon" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path :d="iconPath('mdi-alert-outline')" fill="currentColor"/></svg>
          <span>{{ seedCleanRiskNotice }}</span>
        </div>
        <div
          class="signal-design-replica-stack"
          data-html-replica-stack
          :data-subfill-layout-container="activeSub === 'subfill' ? '' : undefined"
        >
          <section
            class="signal-settings-form-surface"
            :class="{
              'signal-settings-form-surface--peer': activeSub === 'backup' || activeSub === 'updates',
              'signal-settings-form-surface--compact-operational': compactOperationalSubtabs.has(activeSub),
            }"
            data-settings-form-surface
            :data-subfill-config-surface="activeSub === 'subfill' ? '' : undefined"
            :data-subfill-projection-open="activeSub === 'subfill' ? String(subfillProjectionOpen) : undefined"
            :data-compact-operational-surface="compactOperationalSubtabs.has(activeSub) ? activeSub : undefined"
            :data-effective-state="currentEffectiveState.code"
          >
            <template v-for="(card, index) in settingCards" :key="`${activeSub}-setting-${index}`">
              <ScheduleCard
                v-if="card.type === 'schedule'"
                :title="card.title"
                :note="card.note"
                :icon="card.icon"
                :fields="card.fields"
                :values="form"
                :master-key="card.masterKey"
                :schedule-key="card.scheduleKey"
                :effective-state="currentEffectiveState.code"
                embedded
              />
              <NotifyCard
                v-else-if="card.type === 'notify'"
                :title="card.title"
                :note="card.note"
                :icon="card.icon"
                :fields="card.fields"
                :values="form"
                :master-key="card.masterKey"
                :result-key="card.resultKey"
                :result-keys="card.resultKeys"
                :dependencies="card.dependencies"
                :off-values="card.offValues"
                :locked="!!card.fusionManaged && !!form.fusion_notify_enabled"
                :channel-only-lock="!!card.fusionChannelOnly"
                :effective-state="currentEffectiveState.code"
                embedded
              />
              <SubfillRuleEditor
                v-else-if="card.type === 'subfill_rules'"
                :values="form"
                :data-effective-state="currentEffectiveState.code"
                @projection-change="subfillProjectionOpen = $event"
              />
              <CompactSettingCard v-else :card="card" :active-sub="activeSub" :effective-state="currentEffectiveState.code" embedded @run="triggerConfigAction" />
            </template>
          </section>
          <template v-for="(card, index) in actionCards" :key="`${activeSub}-action-${index}`">
            <CompactActionRow :card="card" :plugin-enabled="pluginEnabled" :effective-state="currentEffectiveState.code" @run="triggerConfigAction" />
          </template>
        </div>
      </main>

      <Teleport to="body">
        <div
          v-if="seedCleanConfirmOpen"
          class="signal-seedclean-confirm-overlay signal-root"
          :class="rootThemeClass"
          :style="seedCleanPortalStyle"
          data-seedclean-confirm-dialog
          role="presentation"
          @click.self="seedCleanConfirmOpen = false"
        >
        <section class="signal-seedclean-confirm-dialog" role="dialog" aria-modal="true" aria-labelledby="seedclean-confirm-title">
          <header class="signal-seedclean-confirm-dialog__head">
            <div>
              <span class="signal-seedclean-confirm-dialog__kicker">请确认本次处理</span>
              <h2 id="seedclean-confirm-title">{{ seedCleanActionMeta.label }}</h2>
            </div>
            <button type="button" class="signal-seedclean-confirm-dialog__close" aria-label="关闭" title="关闭" @click="seedCleanConfirmOpen = false">
              <svg class="signal-mdi-icon" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path :d="mdiClose" fill="currentColor" /></svg>
            </button>
          </header>
          <div class="signal-seedclean-confirm-dialog__warning" :class="{ 'signal-seedclean-confirm-dialog__warning--danger': form.seedclean_action !== 'pause' }">
            <svg class="signal-mdi-icon" viewBox="0 0 24 24" width="19" height="19" aria-hidden="true"><path :d="mdiAlertOutline" fill="currentColor" /></svg>
            <span>{{ seedCleanActionMeta.risk }}</span>
          </div>
          <div class="signal-seedclean-confirm-dialog__summary">
            <strong>{{ form.seedclean_downloaders?.length || 0 }} 个下载器</strong>
            <span>按当前条件执行</span>
          </div>
          <div class="signal-seedclean-confirm-dialog__items" data-seedclean-confirm-items>
            <div class="signal-seedclean-confirm-dialog__item">
              <strong>{{ form.seedclean_downloaders?.join('、') || '未选择下载器' }}</strong>
              <span>{{ seedCleanActionMeta.label }}</span>
              <small>{{ seedCleanFilterSummary }}</small>
            </div>
          </div>
          <footer class="signal-seedclean-confirm-dialog__actions">
            <button type="button" class="signal-config-btn signal-config-btn--ghost" data-seedclean-confirm-cancel @click="seedCleanConfirmOpen = false">返回修改</button>
            <button type="button" class="signal-config-btn signal-config-btn--save signal-seedclean-confirm-dialog__submit" data-seedclean-confirm-submit @click="confirmSeedCleanExecution">
              <svg class="signal-mdi-icon" viewBox="0 0 24 24" width="15" height="15" aria-hidden="true"><path :d="mdiPlay" fill="currentColor" /></svg>
              <span>{{ seedCleanActionMeta.confirm }}</span>
            </button>
          </footer>
          </section>
        </div>
      </Teleport>

      <Teleport to="body">
        <div
          v-if="pluginUninstallConfirmOpen"
          class="signal-seedclean-confirm-overlay signal-root"
          :class="rootThemeClass"
          :style="seedCleanPortalStyle"
          data-plugin-uninstall-confirm-dialog
          role="presentation"
          @click.self="pluginUninstallConfirmOpen = false"
        >
          <section class="signal-seedclean-confirm-dialog" role="dialog" aria-modal="true" aria-labelledby="plugin-uninstall-confirm-title">
            <header class="signal-seedclean-confirm-dialog__head">
              <div>
                <h2 id="plugin-uninstall-confirm-title">确认卸载插件</h2>
              </div>
              <button type="button" class="signal-seedclean-confirm-dialog__close" aria-label="关闭" title="关闭" @click="pluginUninstallConfirmOpen = false">
                <svg class="signal-mdi-icon" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path :d="mdiClose" fill="currentColor" /></svg>
              </button>
            </header>
            <div class="signal-seedclean-confirm-dialog__warning signal-seedclean-confirm-dialog__warning--danger">
              <svg class="signal-mdi-icon" viewBox="0 0 24 24" width="19" height="19" aria-hidden="true"><path :d="mdiAlertOutline" fill="currentColor" /></svg>
              <span>以下操作将立即执行且无法撤销，请核对目标插件和清理范围。</span>
            </div>
            <div class="signal-seedclean-confirm-dialog__summary">
              <strong>{{ selectedPluginUninstallItems.length }} 个目标插件</strong>
              <span>{{ pluginUninstallActionItems.length }} 项卸载或清理操作</span>
            </div>
            <div class="signal-seedclean-confirm-dialog__items" data-plugin-uninstall-confirm-targets>
              <div v-for="item in selectedPluginUninstallItems" :key="item.value" class="signal-seedclean-confirm-dialog__item">
                <strong>{{ item.title }}</strong>
                <span>{{ item.value }}</span>
              </div>
            </div>
            <div class="signal-seedclean-confirm-dialog__items" data-plugin-uninstall-confirm-actions>
              <div v-for="item in pluginUninstallActionItems" :key="item.key" class="signal-seedclean-confirm-dialog__item">
                <strong>{{ item.label }}</strong>
                <small>{{ item.detail }}</small>
              </div>
            </div>
            <footer class="signal-seedclean-confirm-dialog__actions">
              <button type="button" class="signal-config-btn signal-config-btn--ghost" data-plugin-uninstall-confirm-cancel @click="pluginUninstallConfirmOpen = false">返回修改</button>
              <button type="button" class="signal-config-btn signal-config-btn--save signal-seedclean-confirm-dialog__submit" data-plugin-uninstall-confirm-submit @click="confirmPluginUninstallExecution">
                <svg class="signal-mdi-icon" viewBox="0 0 24 24" width="15" height="15" aria-hidden="true"><path :d="mdiDeleteOutline" fill="currentColor" /></svg>
                <span>确认卸载</span>
              </button>
            </footer>
          </section>
        </div>
      </Teleport>

      <Teleport to="body">
        <div
          v-if="downloaderHelperConfirmOpen"
          class="signal-seedclean-confirm-overlay signal-root"
          :class="rootThemeClass"
          :style="seedCleanPortalStyle"
          data-downloader-helper-confirm-dialog
          role="presentation"
          @click.self="downloaderHelperConfirmOpen = false"
        >
          <section class="signal-seedclean-confirm-dialog" role="dialog" aria-modal="true" aria-labelledby="downloader-helper-confirm-title">
            <header class="signal-seedclean-confirm-dialog__head">
              <div>
                <span class="signal-seedclean-confirm-dialog__kicker">一次确认</span>
                <h2 id="downloader-helper-confirm-title">清理失效下载任务</h2>
              </div>
              <button type="button" class="signal-seedclean-confirm-dialog__close" aria-label="关闭" title="关闭" @click="downloaderHelperConfirmOpen = false">
                <svg class="signal-mdi-icon" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path :d="mdiClose" fill="currentColor" /></svg>
              </button>
            </header>
            <div class="signal-seedclean-confirm-dialog__warning">
              <svg class="signal-mdi-icon" viewBox="0 0 24 24" width="19" height="19" aria-hidden="true"><path :d="mdiAlertOutline" fill="currentColor" /></svg>
              <span>标签和恢复做种无需确认；以下失效任务将从下载器移除。仅在源文件事件确认数据已删除时才请求清理文件。</span>
            </div>
            <div class="signal-seedclean-confirm-dialog__summary">
              <strong>{{ downloaderHelperPreviewItems.length }} 个清理候选</strong>
              <span>确认后同时执行当前选择的非破坏任务</span>
            </div>
            <div class="signal-seedclean-confirm-dialog__items" data-downloader-helper-confirm-items>
              <div v-for="item in downloaderHelperPreviewItems" :key="`${item.downloader}-${item.id}`" class="signal-seedclean-confirm-dialog__item">
                <strong>{{ item.name || item.id }}</strong>
                <span>{{ item.downloader }}</span>
                <small>{{ item.reason }} · {{ item.delete_file ? '数据已删除' : '不删除数据文件' }}</small>
              </div>
            </div>
            <footer class="signal-seedclean-confirm-dialog__actions">
              <button type="button" class="signal-config-btn signal-config-btn--ghost" @click="downloaderHelperConfirmOpen = false">取消</button>
              <button type="button" class="signal-config-btn signal-config-btn--save signal-seedclean-confirm-dialog__submit" data-downloader-helper-confirm-submit @click="confirmDownloaderHelperExecution">
                <svg class="signal-mdi-icon" viewBox="0 0 24 24" width="15" height="15" aria-hidden="true"><path :d="mdiPlay" fill="currentColor" /></svg>
                <span>确认并执行</span>
              </button>
            </footer>
          </section>
        </div>
      </Teleport>

      <footer class="signal-config-action-strip" data-config-action-strip>
        <div class="signal-config-action-strip-copy">
          <span class="signal-config-action-hint">{{ currentActionHint }}</span>
          <Transition name="signal-fade">
            <strong
              v-if="action.message"
              class="signal-config-action-feedback"
              :class="{ 'signal-config-action-feedback--ok': action.ok, 'signal-config-action-feedback--err': !action.ok }"
            >
              {{ action.message }}
            </strong>
          </Transition>
        </div>
        <div class="signal-config-action-strip-buttons">
          <button type="button" class="signal-config-btn signal-config-btn--ghost" @click="emit('close')">取消</button>
          <button type="button" class="signal-config-btn signal-config-btn--save" data-config-save-button @click="saveConfig">
            <svg class="signal-mdi-icon signal-mdi-icon--save" viewBox="0 0 448 512" width="11.375" height="13" aria-hidden="true"><path :d="faFloppyDiskPath" fill="currentColor"/></svg>
            <span>保存配置</span>
          </button>
        </div>
      </footer>
  </div>
</template>
<style>@import "./styles/config-theme.css";</style>
