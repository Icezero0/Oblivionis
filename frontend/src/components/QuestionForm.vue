<!-- 卡片表单组件 -->
<template>
  <form @submit.prevent="handleSubmit" class="question-form">
    <div class="form-group">
      <label for="content">卡片内容 *</label>
      <textarea 
        id="content"
        v-model="form.content" 
        placeholder="请输入卡片内容..."
        rows="4"
        required
        :class="{ 'error': errors.content }"
        @blur="validateField('content')"
      ></textarea>
      <span v-if="errors.content" class="error-message">{{ errors.content }}</span>
    </div>

    <div class="form-group">
      <label for="card_type">卡片标签 *</label>
      <select 
        id="card_type" 
        v-model="form.card_type" 
        required
        :class="{ 'error': errors.card_type }"
        @change="validateField('card_type')"
      >
        <option value="">请选择卡片标签</option>
        <option v-for="type in allAvailableTypes" :key="type" :value="type">
          {{ type }}
        </option>
        <option value="new">新增标签</option>
      </select>
      <span v-if="errors.card_type" class="error-message">{{ errors.card_type }}</span>
      
      <!-- 新增标签输入框 -->
      <div v-if="form.card_type === 'new'" class="custom-type-input">
        <input 
          type="text" 
          v-model="newType"
          placeholder="请输入新的标签 (如: 名词解释题, 简答题等)"
          maxlength="20"
          @blur="applyNewType"
          @keyup.enter="applyNewType"
        />
        <small class="input-hint">输入后按回车或失去焦点确认</small>
      </div>
    </div>

    <div class="form-group">
      <label for="notes">备注说明</label>
      <textarea 
        id="notes"
        v-model="form.notes" 
        placeholder="可选的备注信息..."
        rows="2"
      ></textarea>
    </div>

    <div class="form-actions">
      <button type="button" class="btn btn-secondary" @click="$emit('cancel')">
        取消
      </button>
      <button type="submit" class="btn btn-primary" :disabled="!isValid || loading">
        {{ loading ? '保存中...' : (isEdit ? '更新' : '保存') }}
      </button>
    </div>
  </form>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'

const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({
      content: '',
      card_type: '',
      notes: ''
    })
  },
  isEdit: {
    type: Boolean,
    default: false
  },
  loading: {
    type: Boolean,
    default: false
  },
  existingTypes: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:modelValue', 'submit', 'cancel'])

// 表单数据
const form = ref({ ...props.modelValue })
const newType = ref('')

// 错误状态
const errors = ref({})

// 计算属性
const isValid = computed(() => {
  return form.value.content.trim() && 
         form.value.card_type && 
         form.value.card_type !== 'new' &&
         Object.keys(errors.value).length === 0
})

// 获取已存在的标签类型（去重并排序）
const existingTypes = computed(() => {
  if (!props.existingTypes || !Array.isArray(props.existingTypes)) {
    return []
  }
  return [...new Set(props.existingTypes)]
    .filter(type => type && type.trim())
    .sort()
})

// 获取所有可用的标签选项（包括当前表单中的新标签）
const allAvailableTypes = computed(() => {
  const types = [...existingTypes.value]
  
  // 如果当前选中的标签不在已有列表中，且不是 'new'，则添加到选项中
  if (form.value.card_type && 
      form.value.card_type !== 'new' && 
      !types.includes(form.value.card_type)) {
    types.push(form.value.card_type)
    types.sort()
  }
  
  return types
})

// 监听器
// 防止递归：只有内容不一致时才 emit
watch(form, (newForm) => {
  if (JSON.stringify(newForm) !== JSON.stringify(props.modelValue)) {
    emit('update:modelValue', { ...newForm })
  }
}, { deep: true })

// props 变化时只在内容不一致时赋值
watch(() => props.modelValue, (newValue) => {
  if (JSON.stringify(newValue) !== JSON.stringify(form.value)) {
    form.value = { ...newValue }
    errors.value = {}
  }
}, { deep: true })

// 监听标签选择变化，重置新标签输入
watch(() => form.value.card_type, (selectedType) => {
  if (selectedType !== 'new') {
    newType.value = ''
  }
})

// 验证方法
function validateField(field) {
  switch (field) {
    case 'content':
      if (!form.value.content.trim()) {
        errors.value.content = '卡片内容不能为空'
      } else {
        delete errors.value.content
      }
      break
    case 'card_type':
      if (!form.value.card_type) {
        errors.value.card_type = '请选择卡片标签'
      } else if (form.value.card_type === 'new') {
        errors.value.card_type = '请输入新的标签名称'
      } else {
        delete errors.value.card_type
      }
      break
  }
}

function validateAll() {
  validateField('content')
  validateField('card_type')
}

function handleSubmit() {
  validateAll()
  if (isValid.value) {
    emit('submit', form.value)
  }
}

// 处理新增标签
function applyNewType() {
  if (newType.value.trim()) {
    const trimmedType = newType.value.trim()
    
    // 检查是否已存在
    const exists = allAvailableTypes.value.includes(trimmedType)
    if (exists) {
      alert('该标签已存在，请选择已有标签或使用其他名称')
      return
    }
    
    // 设置表单值
    form.value.card_type = trimmedType
    newType.value = ''
    
    // 重新验证
    validateField('card_type')
  }
}

// 重置表单
function reset() {
  form.value = {
    content: '',
    card_type: '',
    notes: ''
  }
  errors.value = {}
}

// 暴露方法
defineExpose({
  reset,
  validateAll
})
</script>

<style scoped>
.question-form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.form-group label {
  font-weight: 600;
  color: var(--text-primary);
  font-size: var(--text-sm);
}

.form-group input,
.form-group textarea,
.form-group select {
  padding: var(--spacing-md);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  font-size: var(--text-base);
  transition: all 0.2s ease;
  font-family: inherit;
}

.form-group input:focus,
.form-group textarea:focus,
.form-group select:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
}

.form-group textarea {
  resize: vertical;
  min-height: 80px;
  line-height: 1.5;
}

.form-group input.error,
.form-group textarea.error,
.form-group select.error {
  border-color: var(--error-color);
  box-shadow: 0 0 0 2px rgba(239, 68, 68, 0.1);
}

.error-message {
  color: var(--error-color);
  font-size: var(--text-xs);
  margin-top: var(--spacing-xs);
}

.custom-type-input {
  margin-top: var(--spacing-sm);
  padding: var(--spacing-sm);
  background-color: var(--bg-secondary, #f8f9fa);
  border-radius: var(--border-radius);
  border: 1px solid var(--border-color);
}

.custom-type-input input {
  width: 100%;
  padding: var(--spacing-sm);
  border: 1px solid var(--border-color);
  border-radius: var(--border-radius);
  font-size: var(--text-sm);
}

.custom-type-input input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px var(--primary-color-alpha);
}

.input-hint {
  display: block;
  margin-top: var(--spacing-xs);
  font-size: var(--text-xs);
  color: var(--text-secondary);
  font-style: italic;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-md);
  margin-top: var(--spacing-lg);
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--border-color);
}

@media (max-width: 768px) {
  .form-actions {
    flex-direction: column-reverse;
  }
  
  .form-actions .btn {
    width: 100%;
  }
}
</style>
