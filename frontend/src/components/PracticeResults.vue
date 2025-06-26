<!-- 练习结果组件 -->
<template>
  <div class="practice-results">
    <div class="results-container">
      <!-- 完成庆祝 -->
      <div class="completion-header">
        <div class="completion-icon">🎉</div>
        <h1>练习完成！</h1>
      </div>

      <!-- 统计概览 -->
      <div class="stats-overview">
        <div class="stat-card">
          <div class="stat-number">{{ results.answered }}</div>
          <div class="stat-label">总题数</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ results.correct }}</div>
          <div class="stat-label">正确</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ accuracyPercentage }}%</div>
          <div class="stat-label">正确率</div>
        </div>
        <div class="stat-card">
          <div class="stat-number">{{ formatTime(results.practiceTime) }}</div>
          <div class="stat-label">用时</div>
        </div>
      </div>

      <!-- 详细分析 -->
      <div class="detailed-analysis">
        <h3>📊 详细分析</h3>
        
        <!-- 题型分析 -->
        <div class="analysis-section">
          <h4>题型表现</h4>
          <div class="type-stats">
            <div 
              v-for="typeStat in typeStats" 
              :key="typeStat.type"
              class="type-stat-item"
            >
              <div class="type-header">
                <span class="type-badge" :class="`type-${typeStat.type}`">
                  {{ getCardTypeLabel(typeStat.type) }}
                </span>
                <span class="type-accuracy">
                  {{ Math.round((typeStat.correct / typeStat.total) * 100) }}%
                </span>
              </div>
              <div class="type-progress">
                <div 
                  class="type-progress-fill"
                  :style="{ width: `${(typeStat.correct / typeStat.total) * 100}%` }"
                ></div>
              </div>
              <div class="type-details">
                {{ typeStat.correct }} / {{ typeStat.total }} 题正确
              </div>
            </div>
          </div>
        </div>

        <!-- 评价分布 -->
        <div class="analysis-section">
          <h4>自评分布</h4>
          <div class="evaluation-chart">
            <div 
              v-for="evalStat in evaluationStats"
              :key="evalStat.evaluation"
              class="eval-bar"
            >
              <div class="eval-label">
                <span class="eval-icon">{{ getEvaluationIcon(evalStat.evaluation) }}</span>
                <span class="eval-text">{{ getEvaluationLabel(evalStat.evaluation) }}</span>
              </div>
              <div class="eval-progress">
                <div 
                  class="eval-progress-fill"
                  :class="`eval-${evalStat.evaluation}`"
                  :style="{ width: `${evalStat.percentage}%` }"
                ></div>
              </div>
              <div class="eval-count">{{ evalStat.count }}</div>
            </div>
          </div>
        </div>

        <!-- 需要复习的题目 -->
        <div v-if="reviewCards.length > 0" class="analysis-section">
          <h4>建议复习 ({{ reviewCards.length }} 道题)</h4>
          <div class="review-cards">
            <div 
              v-for="card in reviewCards" 
              :key="card.id"
              class="review-card-item"
            >
              <div class="review-card-content">
                <span class="review-card-type" :class="`type-${card.card_type}`">
                  {{ getCardTypeLabel(card.card_type) }}
                </span>
                <span class="review-card-text">{{ truncateText(card.content, 50) }}</span>
              </div>
              <span class="review-card-reason">
                {{ getReviewReason(card.evaluation) }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- 操作按钮 -->
      <div class="action-buttons">
        <button class="btn btn-primary" @click="$emit('restart')">
          🔄 再次练习
        </button>
        <button class="btn btn-tertiary" @click="$emit('view-stats')">
          📈 查看统计
        </button>
      </div>

      <!-- 学习建议 -->
      <div class="learning-suggestions">
        <h3>💡 学习建议</h3>
        <div class="suggestions-list">
          <div v-for="suggestion in suggestions" :key="suggestion.type" class="suggestion-item">
            <span class="suggestion-icon">{{ suggestion.icon }}</span>
            <div class="suggestion-content">
              <h5>{{ suggestion.title }}</h5>
              <p>{{ suggestion.content }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  results: {
    type: Object,
    required: true
  }
})

defineEmits(['restart', 'new-practice', 'view-stats'])

// 计算属性
const accuracyPercentage = computed(() => {
  if (props.results.answered === 0) return 0
  return Math.round((props.results.correct / props.results.answered) * 100)
})

const typeStats = computed(() => {
  return Object.entries(props.results.cardTypeStats || {}).map(([type, stats]) => ({
    type,
    total: stats.total,
    correct: stats.correct
  }))
})

const evaluationStats = computed(() => {
  const stats = { perfect: 0, good: 0, partial: 0, wrong: 0 }
  props.results.selfRatings.forEach(rating => {
    if (stats.hasOwnProperty(rating)) {
      stats[rating]++
    }
  })
  
  const total = props.results.selfRatings.length
  return Object.entries(stats).map(([evaluation, count]) => ({
    evaluation,
    count,
    percentage: total > 0 ? (count / total) * 100 : 0
  }))
})

const reviewCards = computed(() => {
  // 这里我们暂时返回空数组，因为需要更复杂的数据结构来支持
  // 在后续版本中可以增加题目详细信息的存储
  return []
})

const suggestions = computed(() => {
  const suggestions = []
  const accuracy = accuracyPercentage.value
  
  if (accuracy >= 90) {
    suggestions.push({
      type: 'excellent',
      icon: '🏆',
      title: '表现优秀',
      content: '你的掌握程度很好！可以尝试更有挑战性的题目或增加练习难度。'
    })
  } else if (accuracy >= 70) {
    suggestions.push({
      type: 'good',
      icon: '👍',
      title: '进步明显',
      content: '继续保持这种学习节奏，重点复习错误的题目以提高准确率。'
    })
  } else {
    suggestions.push({
      type: 'needs-improvement',
      icon: '📚',
      title: '需要加强',
      content: '建议复习基础知识，多进行练习，循序渐进地提高掌握程度。'
    })
  }
  
  if (reviewCards.value.length > 0) {
    suggestions.push({
      type: 'review',
      icon: '🔄',
      title: '重点复习',
      content: `建议重点复习 ${reviewCards.value.length} 道掌握不够好的题目，加强记忆。`
    })
  }
  
  suggestions.push({
    type: 'consistency',
    icon: '⏰',
    title: '保持规律',
    content: '建议每天坚持练习，利用间隔重复的方法巩固记忆效果。'
  })
  
  return suggestions
})

// 方法
function getCardTypeLabel(type) {
  const types = {
    'M': 'M题(名词解释)',
    'N': 'N题(简答题)'
  }
  return types[type] || type
}

function getEvaluationIcon(evaluation) {
  const icons = {
    perfect: '🎯',
    good: '👍',
    partial: '🤔',
    wrong: '❌'
  }
  return icons[evaluation] || '❓'
}

function getEvaluationLabel(evaluation) {
  const labels = {
    perfect: '完全正确',
    good: '基本正确',
    partial: '部分正确',
    wrong: '完全错误'
  }
  return labels[evaluation] || evaluation
}

function getReviewReason(evaluation) {
  const reasons = {
    partial: '部分掌握',
    wrong: '需要重学'
  }
  return reasons[evaluation] || '需要复习'
}

function formatTime(seconds) {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

function truncateText(text, maxLength) {
  if (text.length <= maxLength) return text
  return text.substring(0, maxLength) + '...'
}
</script>

<style scoped>
.practice-results {
  max-width: 800px;
  margin: 0 auto;
  padding: var(--spacing-xl) 0;
}

.results-container {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2xl);
}

/* 完成头部 */
.completion-header {
  text-align: center;
  padding: var(--spacing-2xl);
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(243, 139, 168, 0.1));
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
}

.completion-icon {
  font-size: 4rem;
  margin-bottom: var(--spacing-lg);
}

.completion-header h1 {
  margin: 0 0 var(--spacing-md) 0;
  color: var(--text-primary);
  font-size: var(--text-2xl);
}

.completion-header p {
  margin: 0;
  color: var(--text-secondary);
  font-size: var(--text-base);
}

/* 统计概览 */
.stats-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: var(--spacing-lg);
}

.stat-card {
  background: var(--bg-primary);
  padding: var(--spacing-xl);
  border-radius: var(--radius-lg);
  text-align: center;
  border: 1px solid var(--border-color);
  transition: transform 0.2s ease;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.stat-number {
  font-size: var(--text-3xl);
  font-weight: 700;
  color: var(--primary-color);
  margin-bottom: var(--spacing-sm);
}

.stat-label {
  color: var(--text-secondary);
  font-size: var(--text-sm);
  font-weight: 500;
}

/* 详细分析 */
.detailed-analysis {
  background: var(--bg-primary);
  padding: var(--spacing-xl);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
}

.detailed-analysis h3 {
  margin: 0 0 var(--spacing-xl) 0;
  color: var(--text-primary);
  font-size: var(--text-xl);
}

.analysis-section {
  margin-bottom: var(--spacing-2xl);
}

.analysis-section:last-child {
  margin-bottom: 0;
}

.analysis-section h4 {
  margin: 0 0 var(--spacing-lg) 0;
  color: var(--text-primary);
  font-size: var(--text-lg);
  font-weight: 600;
}

/* 题型统计 */
.type-stats {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.type-stat-item {
  padding: var(--spacing-lg);
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
}

.type-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-sm);
}

.type-badge {
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
  font-weight: 600;
  color: #222;
  background: #fff;
}

.type-accuracy {
  font-weight: 600;
  color: var(--primary-color);
}

.type-progress {
  height: 8px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-sm);
  overflow: hidden;
  margin-bottom: var(--spacing-sm);
}

.type-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--primary-color), var(--secondary-color));
  transition: width 0.3s ease;
}

.type-details {
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

/* 评价分布 */
.evaluation-chart {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.eval-bar {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
  padding: var(--spacing-md);
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
}

.eval-label {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  min-width: 120px;
}

.eval-icon {
  font-size: var(--text-lg);
}

.eval-text {
  font-weight: 500;
  color: var(--text-primary);
}

.eval-progress {
  flex: 1;
  height: 8px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-sm);
  overflow: hidden;
}

.eval-progress-fill {
  height: 100%;
  transition: width 0.3s ease;
}

.eval-progress-fill.eval-perfect {
  background: var(--success-color);
}

.eval-progress-fill.eval-good {
  background: #10b981;
}

.eval-progress-fill.eval-partial {
  background: #f59e0b;
}

.eval-progress-fill.eval-wrong {
  background: var(--error-color);
}

.eval-count {
  min-width: 30px;
  text-align: right;
  font-weight: 600;
  color: var(--text-primary);
}

/* 复习卡片 */
.review-cards {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.review-card-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-md);
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
}

.review-card-content {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  flex: 1;
}

.review-card-type {
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--radius-sm);
  font-size: var(--text-xs);
  font-weight: 600;
  color: white;
}

.review-card-text {
  color: var(--text-primary);
}

.review-card-reason {
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

/* 操作按钮 */
.action-buttons {
  display: flex;
  gap: var(--spacing-md);
  justify-content: center;
  flex-wrap: wrap;
}

/* 学习建议 */
.learning-suggestions {
  background: var(--bg-primary);
  padding: var(--spacing-xl);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-color);
}

.learning-suggestions h3 {
  margin: 0 0 var(--spacing-xl) 0;
  color: var(--text-primary);
  font-size: var(--text-xl);
}

.suggestions-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.suggestion-item {
  display: flex;
  gap: var(--spacing-md);
  padding: var(--spacing-lg);
  background: var(--bg-secondary);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
}

.suggestion-icon {
  font-size: var(--text-xl);
  flex-shrink: 0;
}

.suggestion-content h5 {
  margin: 0 0 var(--spacing-sm) 0;
  color: var(--text-primary);
  font-size: var(--text-base);
  font-weight: 600;
}

.suggestion-content p {
  margin: 0;
  color: var(--text-secondary);
  line-height: 1.5;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .stats-overview {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .action-buttons {
    flex-direction: column;
  }
  
  .eval-bar {
    flex-direction: column;
    align-items: stretch;
    gap: var(--spacing-sm);
  }
  
  .eval-label {
    min-width: auto;
  }
  
  .review-card-item {
    flex-direction: column;
    align-items: stretch;
    gap: var(--spacing-sm);
  }
  
  .suggestion-item {
    flex-direction: column;
    gap: var(--spacing-sm);
  }
}

@media (max-width: 480px) {
  .stats-overview {
    grid-template-columns: 1fr;
  }
}
</style>
