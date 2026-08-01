export const subfillRuleFields = Object.freeze([
  Object.freeze({ key: 'category', label: '二级分类', required: true }),
  Object.freeze({ key: 'resolution', label: '分辨率' }),
  Object.freeze({ key: 'quality', label: '资源质量' }),
  Object.freeze({ key: 'effect', label: '特效' }),
  Object.freeze({ key: 'include', label: '包含规则' }),
  Object.freeze({ key: 'exclude', label: '排除规则' }),
  Object.freeze({ key: 'sites', label: '站点名称' }),
  Object.freeze({ key: 'filter_groups', label: '过滤规则组' }),
  Object.freeze({ key: 'savepath', label: '保存路径' }),
])

const fieldByKey = new Map(subfillRuleFields.map(field => [field.key, field]))
const fillKeys = new Set(subfillRuleFields.map(field => field.key).filter(key => key !== 'category'))

function splitRuleTokens(line) {
  const tokens = []
  let token = ''
  for (let index = 0; index < line.length; index += 1) {
    const character = line[index]
    if (character === '\\' && line[index + 1] === '#') {
      token += '#'
      index += 1
    } else if (character === '#') {
      tokens.push(token)
      token = ''
    } else {
      token += character
    }
  }
  tokens.push(token)
  return tokens
}

function lineError(lineNumber, message) {
  return `第 ${lineNumber} 行：${message}`
}

export function parseSubfillRuleLine(rawLine = '', lineNumber = 1) {
  const values = Object.fromEntries(subfillRuleFields.map(field => [field.key, '']))
  const fields = []
  const errors = []
  const seen = new Set()

  for (const rawToken of splitRuleTokens(String(rawLine))) {
    const token = rawToken.trim()
    if (!token) {
      errors.push(lineError(lineNumber, '存在空字段'))
      continue
    }
    const separator = token.indexOf(':')
    if (separator <= 0) {
      errors.push(lineError(lineNumber, `“${token}”缺少 字段:值`))
      continue
    }
    const key = token.slice(0, separator).trim()
    const value = token.slice(separator + 1).trim()
    const definition = fieldByKey.get(key)
    if (!definition) {
      errors.push(lineError(lineNumber, `不支持字段“${key || token}”`))
      continue
    }
    if (!value) errors.push(lineError(lineNumber, `字段“${key}”不能为空`))
    if (seen.has(key)) errors.push(lineError(lineNumber, `字段“${key}”重复出现`))
    seen.add(key)
    values[key] = value
    fields.push(Object.freeze({ key, label: definition.label, value, duplicate: fields.some(field => field.key === key) }))
  }

  if (!values.category) errors.push(lineError(lineNumber, '缺少二级分类 category'))
  if (!fields.some(field => fillKeys.has(field.key) && field.value)) {
    errors.push(lineError(lineNumber, '至少需要一个填充字段'))
  }

  const uniqueErrors = [...new Set(errors)]
  const detailFields = fields.filter(field => field.key !== 'category')
  return Object.freeze({
    id: `subfill-line-${lineNumber}`,
    lineNumber,
    rawLine: String(rawLine),
    category: values.category,
    title: values.category || `第 ${lineNumber} 行`,
    values: Object.freeze(values),
    fields: Object.freeze(detailFields),
    errors: Object.freeze(uniqueErrors),
    valid: uniqueErrors.length === 0,
  })
}

export function parseSubfillRules(text = '') {
  return String(text ?? '')
    .split(/\r?\n/u)
    .map((line, index) => ({ line, lineNumber: index + 1 }))
    .filter(({ line }) => line.trim())
    .map(({ line, lineNumber }) => parseSubfillRuleLine(line, lineNumber))
}

export function validateSubfillRule(rule = {}) {
  return [...(rule.errors || [])]
}

export function previewSubfillRule(rule = {}) {
  const fields = Array.isArray(rule.fields) ? rule.fields : []
  if (!fields.length) return '没有可展示的填充字段'
  return fields.map(field => `${field.label}：${field.value || '空值'}`).join('；')
}
