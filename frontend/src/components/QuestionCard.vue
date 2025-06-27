<!-- 卡片卡片组件 -->
<template>
  <div 
    class="question-card"
    :class="`view-${viewMode}`"
    @click="$emit('select', question)"
  >
    <div class="question-header">
      <span class="question-type" :class="`type-${question.card_type}`">
        {{ getCardTypeLabel(question.card_type) }}
      </span>
      <div class="question-actions">
        <button @click.stop="$emit('edit', question)" class="action-btn edit-btn" title="编辑">
          <span v-if="viewMode === 'list'">编辑</span>
          <span v-else>✏️</span>
        </button>
        <button @click.stop="confirmDelete" class="action-btn delete-btn" title="删除">
          <span v-if="viewMode === 'list'">删除</span>
          <span v-else>🗑️</span>
        </button>
      </div>
    </div>
    <div class="question-content">
      <h3>{{ question.content }}</h3>
      <p v-if="question.notes" class="question-notes">{{ question.notes }}</p>
      <div class="question-meta">
        <span class="meta-item">
          <span class="meta-label">出现次数:</span>
          <span class="meta-value">{{ question.appear_count || 0 }}</span>
        </span>
        <span class="meta-item">
          <span class="meta-label">创建时间:</span>
          <span class="meta-value">{{ formatDate(question.created_at) }}</span>
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { defineProps, defineEmits } from 'vue'

const props = defineProps({
  question: {
    type: Object,
    required: true
  },
  viewMode: {
    type: String,
    default: 'grid',
    validator: (value) => ['grid', 'list'].includes(value)
  }
})

const emit = defineEmits(['select', 'edit', 'delete'])

function getCardTypeLabel(type) {
  const types = {
    'M': 'M题(名词解释)',
    'N': 'N题(简答题)'
  }
  return types[type] || type
}

function formatDate(dateString) {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

function confirmDelete() {
  if (confirm('确定要删除这张卡片吗？此操作不可撤销。')) {
    emit('delete', props.question.id)
  }
}
</script>

<style scoped>
.question-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: var(--shadow-sm);
}

/* 网格视图样式 */
.question-card.view-grid {
  padding: var(--spacing-lg);
}

.question-card.view-grid:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-lg);
  border-color: var(--primary-color);
}

/* 列表视图样式 */
.question-card.view-list {
  padding: var(--spacing-md);
  border-radius: var(--radius-md);
}

.question-card.view-list:hover {
  background: var(--bg-secondary);
  border-color: var(--primary-color);
}

.question-card.view-list .question-header {
  margin-bottom: var(--spacing-sm);
}

.question-card.view-list .question-content h3 {
  font-size: var(--text-base);
  margin-bottom: var(--spacing-xs);
}

.question-card.view-list .question-meta {
  margin-top: var(--spacing-sm);
  padding-top: var(--spacing-xs);
  font-size: var(--text-xs);
}

.question-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
}

.question-type {
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
  font-weight: 600;
  color: white;
}

.question-type.type-M {
  background: #667eea;
}

.question-type.type-N {
  background: #f093fb;
}

.question-actions {
  display: flex;
  gap: var(--spacing-xs);
}

.action-btn {
  background: none;
  border: none;
  padding: var(--spacing-xs);
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: all 0.2s ease;
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.action-btn:hover {
  background: var(--gray-100);
  color: var(--text-primary);
}

.edit-btn:hover {
  background: rgba(102, 126, 234, 0.1);
  color: var(--primary-color);
}

.delete-btn:hover {
  background: rgba(239, 68, 68, 0.1);
  color: var(--error-color);
}

.question-content h3 {
  margin: 0 0 var(--spacing-sm) 0;
  font-size: var(--text-lg);
  color: var(--text-primary);
  line-height: 1.4;
}

.question-notes {
  color: var(--text-secondary);
  font-size: var(--text-sm);
  margin: var(--spacing-sm) 0;
  font-style: italic;
  line-height: 1.4;
}

.question-meta {
  display: flex;
  justify-content: space-between;
  color: var(--text-secondary);
  font-size: var(--text-xs);
  margin-top: var(--spacing-md);
  padding-top: var(--spacing-sm);
  border-top: 1px solid var(--border-color);
}

.meta-item {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.meta-label {
  font-weight: 500;
}

.meta-value {
  color: var(--text-primary);
  font-weight: 600;
}

@media (max-width: 768px) {
  .question-meta {
    flex-direction: column;
    gap: var(--spacing-xs);
  }
  
  .meta-item {
    flex-direction: row;
    gap: var(--spacing-xs);
  }
  
  .action-btn {
    padding: var(--spacing-sm);
  }
}
</style>
