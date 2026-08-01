<script setup>
import { computed, nextTick, ref, useAttrs } from 'vue'
import { mdiChevronDown } from '@mdi/js'
import { parseSubfillRules, previewSubfillRule, validateSubfillRule } from '../model/subfill-rules.js'

const props = defineProps({
  values: { type: Object, required: true },
  disabled: { type: Boolean, default: false },
})
const emit = defineEmits(['projection-change'])
defineOptions({ inheritAttrs: false })
const attrs = useAttrs()

const projectionOpen = ref(false)
const expandedRuleId = ref(null)
const projectionPanel = ref(null)
const ruleCards = new Map()
const codeText = computed({
  get: () => String(props.values.subfill_category_confs ?? ''),
  set: value => { props.values.subfill_category_confs = String(value ?? '') },
})
const enabled = computed({
  get: () => Boolean(props.values.subfill_category_enabled),
  set: value => { props.values.subfill_category_enabled = Boolean(value) },
})
const rules = computed(() => parseSubfillRules(codeText.value))
const errorCount = computed(() => rules.value.reduce((count, rule) => count + validateSubfillRule(rule).length, 0))

function isExpanded(ruleId) {
  return expandedRuleId.value === ruleId
}

function setRuleCardRef(ruleId, element) {
  if (element) ruleCards.set(ruleId, element)
  else ruleCards.delete(ruleId)
}

async function revealWithinNearestScroller(element) {
  await nextTick()
  element.value?.scrollIntoView?.({ block: 'nearest', inline: 'nearest' })
}

async function toggleRule(ruleId) {
  const nextRuleId = expandedRuleId.value === ruleId ? null : ruleId
  expandedRuleId.value = nextRuleId
  if (!nextRuleId) return

  await nextTick()
  const card = ruleCards.get(nextRuleId)
  card?.scrollIntoView?.({ block: 'nearest', inline: 'nearest' })
}

async function toggleProjection() {
  const nextOpen = !projectionOpen.value
  projectionOpen.value = nextOpen
  expandedRuleId.value = null
  emit('projection-change', nextOpen)
  if (nextOpen) await revealWithinNearestScroller(projectionPanel)
}
</script>

<template>
  <section
    v-bind="attrs"
    class="signal-subfill-code"
    :class="{ 'signal-subfill-code--disabled': disabled }"
    data-subfill-code-editor
    :data-subfill-projection-open="projectionOpen ? 'true' : 'false'"
  >
    <div class="signal-subfill-code__controls">
      <button
        type="button"
        class="signal-subfill-code__switch"
        :class="{ 'signal-subfill-code__switch--on': enabled }"
        role="switch"
        :aria-checked="enabled"
        :disabled="disabled"
        @click="enabled = !enabled"
      >
        <span class="signal-toggle-switch" :class="{ 'signal-toggle-switch--on': enabled }" aria-hidden="true"><span class="signal-toggle-switch__thumb" /></span>
        <span>启用二级分类填充</span>
      </button>

      <label class="signal-subfill-code__input">
        <span>规则代码</span>
        <textarea
          v-model="codeText"
          rows="6"
          spellcheck="false"
          :disabled="disabled"
          data-subfill-code-input
          placeholder="category:动画/日番#resolution:1080p#include:简体#sites:观众,青蛙"
        />
      </label>
    </div>

    <div class="signal-subfill-projection-shell" data-subfill-projection-shell>
      <button
        type="button"
        class="signal-subfill-projection-toggle"
        :aria-expanded="projectionOpen"
        aria-controls="signal-subfill-projection-panel"
        data-subfill-projection-toggle
        @click="toggleProjection"
      >
        <span class="signal-subfill-projection-toggle__label">{{ projectionOpen ? '收起图形化' : '展开图形化' }}</span>
        <span class="signal-subfill-projection-toggle__meta" :class="{ 'signal-subfill-projection-toggle__meta--error': errorCount }">
          {{ rules.length }} 条<span v-if="errorCount"> · {{ errorCount }} 个错误</span>
        </span>
        <svg class="signal-subfill-projection-toggle__chevron" :class="{ 'signal-subfill-projection-toggle__chevron--open': projectionOpen }" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path :d="mdiChevronDown" fill="currentColor" /></svg>
      </button>

    </div>
  </section>

  <section
    v-if="projectionOpen"
    ref="projectionPanel"
    id="signal-subfill-projection-panel"
    class="signal-subfill-projection"
    data-subfill-code-projection
  >
    <div v-if="!rules.length" class="signal-subfill-projection__empty" data-subfill-code-empty>
      暂无规则
    </div>

    <div v-else class="signal-subfill-projection__list" data-subfill-code-card-list>
      <article
        v-for="rule in rules"
        :ref="element => setRuleCardRef(rule.id, element)"
        :id="`subfill-rule-panel-${rule.lineNumber}`"
        :key="rule.id"
        class="signal-subfill-code-card"
        :class="{ 'signal-subfill-code-card--error': !rule.valid }"
        :data-subfill-code-line="rule.lineNumber"
        :data-subfill-code-valid="rule.valid"
      >
        <button
          :id="`subfill-rule-toggle-${rule.lineNumber}`"
          type="button"
          class="signal-subfill-code-card__toggle"
          :aria-expanded="isExpanded(rule.id)"
          :aria-controls="`subfill-rule-content-${rule.lineNumber}`"
          :title="isExpanded(rule.id) ? '收起' : '展开'"
          @click="toggleRule(rule.id)"
        >
          <span class="signal-subfill-code-card__line">第 {{ rule.lineNumber }} 行</span>
          <span class="signal-subfill-code-card__title">{{ rule.title }}</span>
          <span class="signal-subfill-code-card__summary">{{ rule.fields.length }} 个字段<span v-if="rule.errors.length"> · {{ rule.errors.length }} 个错误</span></span>
          <svg class="signal-subfill-code-card__chevron" :class="{ 'signal-subfill-code-card__chevron--open': isExpanded(rule.id) }" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path :d="mdiChevronDown" fill="currentColor" /></svg>
        </button>

        <div
          v-if="isExpanded(rule.id)"
          :id="`subfill-rule-content-${rule.lineNumber}`"
          class="signal-subfill-code-card__content"
          role="region"
          :aria-labelledby="`subfill-rule-toggle-${rule.lineNumber}`"
          data-subfill-rule-content
        >
          <dl v-if="rule.fields.length" class="signal-subfill-code-card__fields">
            <div v-for="(field, fieldIndex) in rule.fields" :key="`${field.key}-${fieldIndex}`">
              <dt>{{ field.label }}<span v-if="field.duplicate">（重复）</span></dt>
              <dd>{{ field.value || '空值' }}</dd>
            </div>
          </dl>
          <div v-if="rule.errors.length" class="signal-subfill-code-card__errors" role="alert" data-subfill-code-errors>
            <span v-for="error in rule.errors" :key="error">{{ error }}</span>
          </div>
          <p v-else class="signal-subfill-code-card__preview" data-subfill-code-preview>{{ previewSubfillRule(rule) }}</p>
        </div>
      </article>
    </div>
  </section>
</template>

<style scoped>
.signal-subfill-code {
  min-width: 0;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 12px;
  overflow-x: clip;
}

.signal-subfill-code__controls,
.signal-subfill-code__input,
.signal-subfill-projection-shell,
.signal-subfill-projection,
.signal-subfill-projection__list,
.signal-subfill-code-card,
.signal-subfill-code-card__content,
.signal-subfill-code-card__fields {
  min-width: 0;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 10px;
}

.signal-subfill-code__switch {
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  min-height: 44px;
  display: grid;
  grid-template-columns: 44px minmax(0, 1fr);
  align-items: center;
  gap: 10px;
  padding: 0;
  border: 0;
  color: var(--signal-config-text-primary);
  background: transparent;
  text-align: left;
  font: inherit;
  font-size: 13px;
  font-weight: 750;
  cursor: pointer;
}

.signal-subfill-code__input > span { color: var(--signal-config-text-secondary); font-size: 12px; font-weight: 750; }
.signal-subfill-code__input textarea {
  min-width: 0;
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  min-height: 154px;
  field-sizing: content;
  resize: none;
  overflow: hidden;
  padding: 11px 12px;
  border: 1px solid var(--signal-config-border);
  border-radius: var(--signal-config-field-radius);
  color: var(--signal-config-text-primary);
  background: var(--signal-config-field-surface);
  font: 500 12px/1.6 ui-monospace, SFMono-Regular, Consolas, monospace;
}

.signal-subfill-projection-shell {
  align-content: start;
  gap: 8px;
}

.signal-subfill-projection-toggle {
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  min-height: 42px;
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto 18px;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  border: 1px solid var(--signal-config-border);
  border-radius: var(--signal-config-field-radius);
  color: var(--signal-config-text-primary);
  background: var(--signal-config-field-surface);
  text-align: left;
  font: inherit;
  cursor: pointer;
}

.signal-subfill-projection-toggle__label {
  min-width: 0;
  font-size: 13px;
  font-weight: 750;
}

.signal-subfill-projection-toggle__meta {
  color: var(--signal-config-text-secondary);
  font-size: 12px;
  white-space: nowrap;
}

.signal-subfill-projection-toggle__meta--error {
  color: rgb(var(--v-theme-error));
}

.signal-subfill-projection-toggle__chevron {
  transition: transform .16s ease;
}

.signal-subfill-projection-toggle__chevron--open {
  transform: rotate(180deg);
}

.signal-subfill-projection {
  align-content: start;
  padding: 0;
  border: 0;
  border-radius: 0;
  background: transparent;
}

.signal-subfill-projection__empty {
  min-height: 88px;
  display: grid;
  place-items: center;
  color: var(--signal-config-text-secondary);
  font-size: 12px;
}

.signal-subfill-projection__list {
  max-height: none;
  overflow-x: clip;
  overflow-y: visible;
  align-content: start;
  grid-auto-rows: max-content;
}

.signal-subfill-code-card {
  border-radius: 8px;
  background: var(--signal-config-field-surface);
  border: 1px solid var(--signal-config-border);
  overflow: hidden;
}

.signal-subfill-code-card--error {
  border-color: rgba(var(--v-theme-error), .42);
}

.signal-subfill-code-card__toggle {
  width: 100%;
  max-width: 100%;
  box-sizing: border-box;
  min-height: 46px;
  display: grid;
  grid-template-columns: auto minmax(0, 1fr) auto 18px;
  align-items: center;
  gap: 9px;
  padding: 8px 10px;
  border: 0;
  color: var(--signal-config-text-primary);
  background: transparent;
  text-align: left;
  font: inherit;
  cursor: pointer;
}

.signal-subfill-code-card__line,
.signal-subfill-code-card__summary {
  color: var(--signal-config-text-secondary);
  font-size: 11px;
  white-space: nowrap;
}

.signal-subfill-code-card__title {
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 13px;
  font-weight: 780;
}

.signal-subfill-code-card__chevron {
  transition: transform .16s ease;
}

.signal-subfill-code-card__chevron--open {
  transform: rotate(180deg);
}

.signal-subfill-code-card__content {
  padding: 0 10px 10px;
}

.signal-subfill-code-card__fields {
  grid-template-columns: repeat(2, minmax(0, 1fr));
  margin: 0;
}

.signal-subfill-code-card__fields > div {
  min-width: 0;
  max-width: 100%;
  box-sizing: border-box;
  padding: 8px;
  border-radius: 7px;
  background: var(--signal-config-capsule-surface);
}

.signal-subfill-code-card__fields dt {
  color: var(--signal-config-text-secondary);
  font-size: 11px;
}

.signal-subfill-code-card__fields dd {
  margin: 3px 0 0;
  overflow-wrap: anywhere;
  color: var(--signal-config-text-primary);
  font-size: 12px;
  line-height: 1.45;
}

.signal-subfill-code-card__errors {
  min-width: 0;
  max-width: 100%;
  box-sizing: border-box;
  display: grid;
  gap: 4px;
  padding: 8px;
  border-radius: 7px;
  color: rgb(var(--v-theme-error));
  background: rgba(var(--v-theme-error), .08);
  font-size: 11px;
  line-height: 1.45;
}

.signal-subfill-code-card__preview {
  min-width: 0;
  max-width: 100%;
  margin: 0;
  overflow-wrap: anywhere;
  color: var(--signal-config-text-secondary);
  font-size: 11px;
  line-height: 1.5;
}

.signal-subfill-code button:focus-visible,
.signal-subfill-projection button:focus-visible,
.signal-subfill-code textarea:focus-visible {
  outline: 2px solid rgb(var(--v-theme-primary));
  outline-offset: 2px;
}

.signal-subfill-code button:disabled,
.signal-subfill-code textarea:disabled {
  cursor: not-allowed;
  opacity: .52;
}

.signal-subfill-code--disabled {
  opacity: .72;
}

@media (max-width: 460px) {
  .signal-subfill-projection-toggle {
    grid-template-columns: minmax(0, 1fr) 18px;
  }

  .signal-subfill-projection-toggle__meta {
    grid-column: 1;
    white-space: normal;
  }

  .signal-subfill-projection-toggle__chevron {
    grid-column: 2;
    grid-row: 1 / span 2;
  }

  .signal-subfill-code-card__toggle {
    grid-template-columns: auto minmax(0, 1fr) 18px;
  }

  .signal-subfill-code-card__summary {
    grid-column: 2;
    white-space: normal;
  }

  .signal-subfill-code-card__chevron {
    grid-column: 3;
    grid-row: 1 / span 2;
  }

  .signal-subfill-code-card__fields {
    grid-template-columns: minmax(0, 1fr);
  }
}
</style>
