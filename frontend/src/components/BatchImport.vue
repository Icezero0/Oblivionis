<!-- 批量导入组件 -->
<template>
  <div class="batch-import">
    <div class="import-header">
      <h3>批量导入题目</h3>
      <p class="import-description">
        快速导入多道题目，支持批量创建不同类型的题目
      </p>
    </div>

    <div class="import-content">
      <!-- 格式说明 -->
      <div class="format-section">
        <h4>📋 导入格式说明</h4>
        <p class="format-hint">请按以下格式输入题目，每行一道题目：</p>
        <div class="format-example">
          <div class="example-item">
            <code>标记|题目内容|备注(可选)</code>
            <span class="example-desc">基本格式</span>
          </div>
          <div class="example-item">
            <code>名词解释|这是一道名词解释题|</code>
            <span class="example-desc">示例：自定义标记</span>
          </div>
        </div>
        <div class="format-tips">
          <p>💡 <strong>说明：</strong></p>
          <ul>
            <li>题目标记可以是任意字符（如：名词解释、简答题、选择题等）</li>
            <li>题目内容为必填项</li>
            <li>备注为可选项，可以留空</li>
            <li>每行代表一道题目</li>
          </ul>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="input-section">
        <label for="batch-content">题目内容</label>
        <textarea 
          id="batch-content"
          v-model="content" 
          rows="8"
          class="batch-textarea"
          @input="validateContent"
        ></textarea>
        <div class="input-stats">
          <span>行数: {{ lineCount }}</span>
          <span>有效题目: {{ validQuestions.length }}</span>
          <span v-if="errors.length > 0" class="error-count">错误: {{ errors.length }}</span>
        </div>
      </div>

      <!-- 错误提示 -->
      <div v-if="errors.length > 0" class="error-section">
        <h4>⚠️ 格式错误</h4>
        <div class="error-list">
          <div v-for="error in errors" :key="error.line" class="error-item">
            <span class="error-line">第 {{ error.line }} 行:</span>
            <span class="error-message">{{ error.message }}</span>
            <code class="error-content">{{ error.content }}</code>
          </div>
        </div>
      </div>

      <!-- 预览区域 -->
      <div v-if="validQuestions.length > 0" class="preview-section">
        <h4>👀 导入预览 ({{ validQuestions.length }} 道题目)</h4>
        <div class="preview-list">
          <div v-for="(question, index) in validQuestions" :key="index" class="preview-item">
            <span class="preview-type" :class="`type-${question.card_type}`">
              {{ getCardTypeLabel(question.card_type) }}
            </span>
            <div class="preview-content">
              <p class="preview-text">{{ question.content }}</p>
              <p v-if="question.notes" class="preview-notes">备注: {{ question.notes }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="import-actions">
      <button class="btn btn-secondary" @click="$emit('cancel')">
        取消
      </button>
      <button 
        class="btn btn-primary" 
        @click="handleImport"
        :disabled="validQuestions.length === 0 || loading"
      >
        {{ loading ? '导入中...' : `导入 ${validQuestions.length} 道题目` }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['import', 'cancel'])

// 数据
const content = ref('')
const errors = ref([])

// 计算属性
const lineCount = computed(() => {
  return content.value.trim() ? content.value.trim().split('\n').length : 0
})

const validQuestions = computed(() => {
  if (!content.value.trim()) return []
  
  const lines = content.value.trim().split('\n')
  const questions = []
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim()
    if (!line) continue
    
    const parts = line.split('|')
    if (parts.length >= 2) {
      const question = {
        card_type: parts[0].trim(),
        content: parts[1].trim(),
        notes: parts[2] ? parts[2].trim() : ''
      }
      
      // 验证题目类型和内容
      if (['M', 'N'].includes(question.card_type) && question.content) {
        questions.push(question)
      }
    }
  }
  
  return questions
})

// 方法
function validateContent() {
  errors.value = []
  
  if (!content.value.trim()) return
  
  const lines = content.value.trim().split('\n')
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].trim()
    if (!line) continue
    
    const lineNumber = i + 1
    const parts = line.split('|')
    
    if (parts.length < 2) {
      errors.value.push({
        line: lineNumber,
        message: '格式错误，至少需要题目类型和内容，用 | 分隔',
        content: line
      })
      continue
    }
    
    const cardType = parts[0].trim()
    const questionContent = parts[1].trim()
    
    if (!['M', 'N'].includes(cardType)) {
      errors.value.push({
        line: lineNumber,
        message: '题目类型错误，只支持 M (名词解释) 或 N (简答题)',
        content: line
      })
      continue
    }
    
    if (!questionContent) {
      errors.value.push({
        line: lineNumber,
        message: '题目内容不能为空',
        content: line
      })
      continue
    }
    
    if (questionContent.length < 3) {
      errors.value.push({
        line: lineNumber,
        message: '题目内容太短，至少需要3个字符',
        content: line
      })
    }
  }
}

function getCardTypeLabel(type) {
  const types = {
    'M': 'M题(名词解释)',
    'N': 'N题(简答题)'
  }
  return types[type] || type
}

function handleImport() {
  if (validQuestions.value.length > 0) {
    emit('import', validQuestions.value)
  }
}

function reset() {
  content.value = ''
  errors.value = []
}

// 监听内容变化
watch(content, validateContent)

// 暴露方法
defineExpose({
  reset
})
</script>

<style scoped>
.batch-import {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
  max-height: 80vh;
  overflow-y: auto;
}

.import-header h3 {
  margin: 0 0 var(--spacing-sm) 0;
  color: var(--text-primary);
}

.import-description {
  margin: 0;
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

.import-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

/* 格式说明 */
.format-section h4 {
  margin: 0 0 var(--spacing-sm) 0;
  color: var(--text-primary);
  font-size: var(--text-base);
}

.format-hint {
  margin: 0 0 var(--spacing-md) 0;
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

.format-example {
  background: var(--bg-secondary);
  padding: var(--spacing-md);
  border-radius: var(--radius-md);
  border-left: 4px solid var(--primary-color);
}

.example-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-sm);
}

.example-item:last-child {
  margin-bottom: 0;
}

.example-item code {
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  background: var(--bg-primary);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--radius-sm);
  flex: 1;
}

.example-desc {
  color: var(--text-secondary);
  font-size: var(--text-xs);
}

.format-tips {
  margin-top: var(--spacing-md);
  padding: var(--spacing-md);
  background: var(--bg-secondary, #f8f9fa);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
}

.format-tips p {
  margin: 0 0 var(--spacing-sm) 0;
  font-weight: 600;
  color: var(--text-primary);
}

.format-tips ul {
  margin: 0;
  padding-left: var(--spacing-lg);
}

.format-tips li {
  margin-bottom: var(--spacing-xs);
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

/* 输入区域 */
.input-section label {
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--spacing-sm);
}

.batch-textarea {
  width: 100%;
  min-height: 150px;
  padding: var(--spacing-md);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  font-family: var(--font-mono);
  font-size: var(--text-sm);
  line-height: 1.5;
  resize: vertical;
  transition: border-color 0.2s ease;
}

.batch-textarea:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
}

.input-stats {
  display: flex;
  gap: var(--spacing-lg);
  margin-top: var(--spacing-sm);
  font-size: var(--text-xs);
  color: var(--text-secondary);
}

.error-count {
  color: var(--error-color);
  font-weight: 600;
}

/* 错误提示 */
.error-section {
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
}

.error-section h4 {
  margin: 0 0 var(--spacing-md) 0;
  color: var(--error-color);
  font-size: var(--text-base);
}

.error-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
  max-height: 150px;
  overflow-y: auto;
}

.error-item {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xs);
  padding: var(--spacing-sm);
  background: white;
  border-radius: var(--radius-sm);
  border-left: 3px solid var(--error-color);
}

.error-line {
  font-weight: 600;
  color: var(--error-color);
  font-size: var(--text-xs);
}

.error-message {
  color: var(--text-primary);
  font-size: var(--text-sm);
}

.error-content {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
  background: #f9fafb;
  padding: var(--spacing-xs);
  border-radius: var(--radius-xs);
  color: var(--text-secondary);
}

/* 预览区域 */
.preview-section h4 {
  margin: 0 0 var(--spacing-md) 0;
  color: var(--text-primary);
  font-size: var(--text-base);
}

.preview-list {
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  background: var(--bg-secondary);
}

.preview-item {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  border-bottom: 1px solid var(--border-color);
  background: var(--bg-primary);
}

.preview-item:last-child {
  border-bottom: none;
}

.preview-type {
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
  font-weight: 600;
  color: white;
  white-space: nowrap;
}

.preview-type.type-M {
  background: #667eea;
}

.preview-type.type-N {
  background: #f093fb;
}

.preview-content {
  flex: 1;
}

.preview-text {
  margin: 0 0 var(--spacing-xs) 0;
  color: var(--text-primary);
  font-size: var(--text-sm);
  line-height: 1.4;
}

.preview-notes {
  margin: 0;
  color: var(--text-secondary);
  font-size: var(--text-xs);
  font-style: italic;
}

/* 操作按钮 */
.import-actions {
  display: flex;
  justify-content: flex-end;
  gap: var(--spacing-md);
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--border-color);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .import-actions {
    flex-direction: column-reverse;
  }
  
  .import-actions .btn {
    width: 100%;
  }
  
  .input-stats {
    flex-direction: column;
    gap: var(--spacing-xs);
  }
  
  .example-item {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-xs);
  }
}
</style>
