<!-- 练习卡片组件 -->
<template>
  <div class="practice-card">
    <!-- 进度信息 -->
    <div class="progress-header">
      <div class="progress-info">
        <span class="current-progress">第 {{ currentIndex + 1 }} 题 / 共 {{ totalCount }} 题</span>
        <div class="progress-bar">
          <div 
            class="progress-fill" 
            :style="{ width: `${progressPercentage}%` }"
          ></div>
        </div>
      </div>
      <div class="practice-actions">
        <button class="btn btn-secondary btn-sm" @click="$emit('end')">
          结束练习
        </button>
      </div>
    </div>

    <!-- 题目卡片 -->
    <div class="card-container">
      <div class="card-header">
        <span class="card-type-badge" :class="`type-${card.card_type}`">
          {{ getCardTypeLabel(card.card_type) }}
        </span>
        <span v-if="card.appear_count > 0" class="appear-count">
          已练习 {{ card.appear_count }} 次
        </span>
      </div>

      <div class="question-section">
        <h2 class="question-text">{{ card.content }}</h2>
      </div>

      <!-- 操作区域 -->
      <div class="answer-section">
        <div class="answer-actions">
          <button 
            class="btn btn-primary"
            @click="showNotes = true"
          >
            查看备注
          </button>
        </div>
        <div class="self-evaluation" style="margin-top: 2rem;">
          <div class="evaluation-options">
            <button 
              v-for="option in evaluationOptions"
              :key="option.value"
              class="evaluation-btn"
              @click="submitEvaluation(option.value)"
            >
              <span class="eval-icon">{{ option.icon }}</span>
              <span class="eval-text">{{ option.label }}</span>
            </button>
          </div>
        </div>
      </div>

      <!-- 备注展示 -->
      <div v-if="showNotes" class="feedback-section">
        <div v-if="card.notes" class="explanation-display">
          <h4>💡 备注：</h4>
          <div class="answer-content">{{ card.notes }}</div>
        </div>
        <div v-else class="explanation-display">
          <h4>💡 备注：</h4>
          <div class="answer-content">无备注</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  card: {
    type: Object,
    required: true
  },
  currentIndex: {
    type: Number,
    required: true
  },
  totalCount: {
    type: Number,
    required: true
  }
})

const emit = defineEmits(['answer', 'skip', 'next', 'end'])

// 状态
const showNotes = ref(false)

// 计算属性
const progressPercentage = computed(() => {
  return ((props.currentIndex + 1) / props.totalCount) * 100
})

// 方法
function getCardTypeLabel(type) {
  const types = {
    'M': 'M题(名词解释)',
    'N': 'N题(简答题)'
  }
  return types[type] || type
}

const evaluationOptions = [
  { value: 'perfect', icon: '🎯', label: '完全正确' },
  { value: 'good', icon: '👍', label: '基本正确' },
  { value: 'partial', icon: '🤔', label: '部分正确' },
  { value: 'wrong', icon: '❌', label: '完全错误' }
]

function submitEvaluation(val) {
  showNotes.value = false
  emit('answer', {
    cardId: props.card.id,
    selfRating: val
  })
  emit('next')
}

// 暴露重置方法
function reset() {
  showNotes.value = false
}
defineExpose({
  reset
})
</script>

<style scoped>
.practice-card {
  max-width: 800px;
  margin: 0 auto;
}

/* 进度头部 */
.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-xl);
  padding: var(--spacing-md);
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
}

.progress-info {
  flex: 1;
}

.current-progress {
  display: block;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: var(--spacing-sm);
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-sm);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
  transition: width 0.3s ease;
}

.practice-actions {
  margin-left: var(--spacing-lg);
}

/* 卡片容器 */
.card-container {
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow-md);
  border: 1px solid var(--border-color);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-xl);
}

.card-type-badge {
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  font-weight: 600;
  color: white;
}

.card-type-badge.type-M {
  background: #667eea;
}

.card-type-badge.type-N {
  background: #f093fb;
}

.appear-count {
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

/* 题目区域 */
.question-section {
  margin-bottom: var(--spacing-2xl);
}

.question-text {
  font-size: var(--text-xl);
  font-weight: 600;
  line-height: 1.5;
  color: var(--text-primary);
  margin: 0 0 var(--spacing-md) 0;
}

/* 操作区域 */
.answer-section {
  border-top: 1px solid var(--border-color);
  padding-top: var(--spacing-xl);
}

.answer-actions {
  display: flex;
  gap: var(--spacing-md);
}

/* 反馈区域 */
.feedback-section {
  border-top: 1px solid var(--border-color);
  padding-top: var(--spacing-xl);
}

.explanation-display {
  margin-bottom: var(--spacing-xl);
}

.explanation-display h4 {
  margin: 0 0 var(--spacing-sm) 0;
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--text-primary);
}

.answer-content {
  padding: var(--spacing-md);
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  border-left: 4px solid var(--primary-color);
  line-height: 1.6;
  white-space: pre-wrap;
}

/* 自评区域 */
.self-evaluation {
  margin-bottom: var(--spacing-xl);
}

.self-evaluation h4 {
  margin: 0 0 var(--spacing-md) 0;
  font-size: var(--text-base);
  font-weight: 600;
  color: var(--text-primary);
}

.evaluation-options {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: var(--spacing-sm);
}

.evaluation-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-xs);
  padding: var(--spacing-md);
  border: 2px solid var(--border-color);
  background: var(--bg-primary);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s ease;
}

.evaluation-btn:hover {
  border-color: var(--primary-color);
  background: rgba(102, 126, 234, 0.05);
}

.evaluation-btn.selected {
  border-color: var(--primary-color);
  background: var(--primary-color);
  color: white;
}

.eval-icon {
  font-size: var(--text-lg);
}

.eval-text {
  font-size: var(--text-sm);
  font-weight: 500;
}

.next-actions {
  text-align: center;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .progress-header {
    flex-direction: column;
    gap: var(--spacing-md);
    align-items: stretch;
  }
  
  .practice-actions {
    margin-left: 0;
  }
  
  .card-container {
    padding: var(--spacing-lg);
  }
  
  .answer-actions {
    flex-direction: column;
  }
  
  .evaluation-options {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .evaluation-options {
    grid-template-columns: 1fr;
  }
}
</style>
