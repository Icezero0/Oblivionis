<!-- 统计页面 -->
<template>
  <div class="statistics-page">
    <div class="container">
      <div class="page-header">
        <h1>📊 学习统计</h1>
      </div>

      <!-- 总览统计 -->
      <div class="stats-overview">
        <div class="grid grid-cols-4">
          <div class="stat-card card">
            <div class="stat-icon">📚</div>
            <div class="stat-content">
              <div class="stat-number">{{ overview.total_cards || 0 }}</div>
              <div class="stat-label">总卡片数</div>
            </div>
          </div>
          <div class="stat-card card">
            <div class="stat-icon">🃏</div>
            <div class="stat-content">
              <div class="stat-number">{{ overview.drawn_cards || 0 }}</div>
              <div class="stat-label">已练习卡片</div>
            </div>
          </div>
          <div class="stat-card card">
            <div class="stat-icon">💡</div>
            <div class="stat-content">
              <div class="stat-number">{{ overview.never_drawn || 0 }}</div>
              <div class="stat-label">未练习卡片</div>
            </div>
          </div>
          <div class="stat-card card">
            <div class="stat-icon">🎯</div>
            <div class="stat-content">
              <div class="stat-number">{{ overview.total_sessions || 0 }}</div>
              <div class="stat-label">练习次数</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 卡片类型分布 -->
      <div class="card-type-distribution card">
        <h3>📦 卡片类型分布</h3>
        <div v-if="Object.keys(overview.cards_by_type || {}).length === 0" class="empty-state">暂无数据</div>
        <div v-else class="type-list">
          <div v-for="(count, type) in overview.cards_by_type" :key="type" class="type-item">
            <span class="type-badge">{{ getCardTypeLabel(type) }}</span>
            <span class="type-count">{{ count }} 张</span>
          </div>
        </div>
      </div>

      <!-- 学习进度分析 -->
      <div class="progress-section card">
        <h3>📈 学习进度</h3>
        <div v-if="Object.keys(progress.progress_by_type || {}).length === 0" class="empty-state">暂无进度数据</div>
        <div v-else class="progress-list">
          <div v-for="(item, type) in progress.progress_by_type" :key="type" class="progress-item">
            <span class="type-badge">{{ getCardTypeLabel(type) }}</span>
            <span class="progress-bar">
              <span class="progress-fill" :style="{ width: item.progress_rate + '%' }"></span>
            </span>
            <span class="progress-label">{{ item.practiced }}/{{ item.total }} ({{ item.progress_rate }}%)</span>
          </div>
        </div>
        <div class="proficiency-summary">
          <span>未练习: {{ progress.proficiency_levels?.beginner || 0 }}</span>
          <span>练习中: {{ progress.proficiency_levels?.practicing || 0 }}</span>
          <span>熟悉: {{ progress.proficiency_levels?.familiar || 0 }}</span>
          <span>精通: {{ progress.proficiency_levels?.mastered || 0 }}</span>
        </div>
      </div>

      <!-- 会话分析 -->
      <div class="session-section card">
        <h3>📅 练习会话分析</h3>
        <div v-if="session.total_sessions === 0" class="empty-state">暂无会话数据</div>
        <div v-else>
          <div class="session-stats">
            <span>总会话数：{{ session.total_sessions }}</span>
            <span>平均每次练习卡片数：{{ session.avg_cards_per_session }}</span>
          </div>
          <div class="session-timeline">
            <div v-for="item in session.session_timeline" :key="item.session_number" class="session-item">
              <span class="session-date">{{ item.date }}</span>
              <span class="session-info">会话#{{ item.session_number }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 卡片详细统计 -->
      <div class="card-stats-section card">
        <h3>🃏 卡片详细统计</h3>
        <div v-if="cardStats.total_cards === 0" class="empty-state">暂无卡片统计</div>
        <div v-else>
          <div>总出现次数：{{ cardStats.total_appears }}</div>
          <div>平均出现次数：{{ cardStats.avg_appears }}</div>
          <div>最大出现次数：{{ cardStats.max_appears }}</div>
          <div>最小出现次数：{{ cardStats.min_appears }}</div>
          <div class="most-drawn-list">
            <div v-for="card in cardStats.most_drawn_cards" :key="card.id" class="most-drawn-item">
              <span class="card-content">{{ card.content }}</span>
              <span class="appear-count">出现 {{ card.appear_count }} 次</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 智能建议 -->
      <div class="recommendations-section card">
        <h3>💡 智能建议</h3>
        <div v-if="recommendations.length === 0" class="empty-state">暂无建议</div>
        <div v-else class="recommendations-list">
          <div v-for="(rec, index) in recommendations" :key="index" class="recommendation-item">
            <span class="recommendation-message">{{ rec.message }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { statsAPI } from '@/services/api'

const overview = ref({})
const progress = ref({})
const session = ref({})
const cardStats = ref({})
const recommendations = ref([])

onMounted(() => {
  loadStatistics()
})

async function loadStatistics() {
  try {
    const [overviewData, progressData, sessionData, cardStatsData, recData] = await Promise.all([
      statsAPI.getUserOverview(1),
      statsAPI.getLearningProgress(1).catch(e => {
        if (e.message && e.message.includes('400')) {
          // 400错误时输出详细信息
          console.log('学习进度API 400错误:', e);
        }
        throw e;
      }),
      statsAPI.getSessionAnalytics(1),
      statsAPI.getCardStatistics(1),
      statsAPI.getRecommendations(1)
    ])
    overview.value = overviewData || {}
    progress.value = progressData || {}
    session.value = sessionData || {}
    cardStats.value = cardStatsData || {}
    recommendations.value = recData.recommendations || []
  } catch (e) {
    console.error('加载统计数据失败', e)
  }
}

function getCardTypeLabel(type) {
  const types = {
    'M': '名词解释',
    'N': '简答题',
    'single_choice': '单选',
    'multiple_choice': '多选',
    'fill_blank': '填空',
    'qa': '问答'
  }
  return types[type] || type
}
</script>

<style scoped>
.statistics-page {
  padding: var(--spacing-xl) 0;
}

.page-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.page-header h1 {
  margin: 0 0 var(--spacing-sm) 0;
  color: var(--text-primary);
}

.page-header p {
  margin: 0;
  color: var(--text-secondary);
}

.stats-overview {
  margin-bottom: var(--spacing-xl);
}

.stat-card {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-lg);
}

.stat-icon {
  font-size: 2rem;
}

.stat-content .stat-number {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--primary-color);
  margin-bottom: var(--spacing-xs);
}

.stat-content .stat-label {
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

.card-type-distribution {
  margin-bottom: var(--spacing-xl);
}

.type-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.type-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-md);
  border-radius: var(--radius-md);
  background: var(--gray-50);
}

.type-badge {
  font-weight: 500;
  color: var(--text-primary);
}

.progress-section {
  margin-bottom: var(--spacing-xl);
}

.progress-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.progress-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-md);
  border-radius: var(--radius-md);
  background: var(--gray-50);
}

.progress-bar {
  flex: 1;
  height: 8px;
  border-radius: var(--radius-sm);
  background: var(--gray-200);
  margin: 0 var(--spacing-md);
}

.progress-fill {
  display: block;
  height: 100%;
  border-radius: var(--radius-sm);
  background: var(--primary-color);
}

.proficiency-summary {
  display: flex;
  justify-content: space-between;
  margin-top: var(--spacing-md);
  padding: var(--spacing-md) 0;
  border-top: 1px solid var(--border-color);
  border-bottom: 1px solid var(--border-color);
}

.session-section {
  margin-bottom: var(--spacing-xl);
}

.session-stats {
  display: flex;
  justify-content: space-between;
  margin-bottom: var(--spacing-md);
}

.session-timeline {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.session-item {
  display: flex;
  justify-content: space-between;
  padding: var(--spacing-md);
  border-radius: var(--radius-md);
  background: var(--gray-50);
}

.card-stats-section {
  margin-bottom: var(--spacing-xl);
}

.most-drawn-list {
  margin-top: var(--spacing-md);
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--border-color);
}

.most-drawn-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-md) 0;
  border-bottom: 1px solid var(--border-color);
}

.most-drawn-item:last-child {
  border-bottom: none;
}

.card-content {
  flex: 1;
  font-weight: 500;
  color: var(--text-primary);
}

.appear-count {
  font-size: var(--text-sm);
  color: var(--text-secondary);
}

.recommendations-section {
  margin-bottom: var(--spacing-xl);
}

.recommendations-section h3 {
  margin: 0 0 var(--spacing-lg) 0;
  color: var(--text-primary);
}

.recommendations-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

.recommendation-item {
  display: flex;
  align-items: flex-start;
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  border-radius: var(--radius-md);
  border-left: 4px solid var(--border-color);
}

.recommendation-item.priority-high {
  border-left-color: var(--error-color);
  background: rgba(239, 68, 68, 0.05);
}

.recommendation-item.priority-medium {
  border-left-color: var(--warning-color);
  background: rgba(245, 158, 11, 0.05);
}

.recommendation-item.priority-low {
  border-left-color: var(--info-color);
  background: rgba(59, 130, 246, 0.05);
}

.recommendation-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.recommendation-content h4 {
  margin: 0 0 var(--spacing-xs) 0;
  color: var(--text-primary);
}

.recommendation-content p {
  margin: 0;
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

.empty-state {
  text-align: center;
  color: var(--text-secondary);
  padding: var(--spacing-xl);
}

@media (max-width: 768px) {
  .grid-cols-4 {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .grid-cols-2 {
    grid-template-columns: 1fr;
  }
  
  .stat-card {
    flex-direction: column;
    text-align: center;
  }
}

@media (max-width: 480px) {
  .grid-cols-4 {
    grid-template-columns: 1fr;
  }
}
</style>
