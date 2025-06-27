<template>
  <div class="home">
    <div class="container">
      <div class="header">
        <h1>🧠 Oblivionis</h1>
      </div>
      
      <div class="actions-grid">
        <router-link to="/cards" class="action-card primary">
          <div class="card-icon">📚</div>
          <h3>卡片管理</h3>
          <p>添加、编辑和管理你的学习卡片</p>
          <div class="card-stats">
            <span>{{ questionStats.total || 0 }} 张卡片</span>
          </div>
        </router-link>
        
        <router-link to="/practice" class="action-card secondary">
          <div class="card-icon">🎯</div>
          <h3>抽卡练习</h3>
          <p>从你所添加的学习卡片中抽卡练习</p>
          <div class="card-stats">
            <template v-if="questionStats.realTypes && questionStats.realTypes.length > 0">
              <template v-for="(type, idx) in questionStats.realTypes" :key="type">
                <span>
                  {{ getCardTypeLabel(type) }}: {{ questionStats.typeCountMap[type] || 0 }}<span v-if="idx < questionStats.realTypes.length - 1"> | </span>
                </span>
              </template>
            </template>
            <span v-else>无题型</span>
          </div>
        </router-link>
        
        <router-link to="/statistics" class="action-card accent">
          <div class="card-icon">📊</div>
          <h3>学习统计</h3>
          <p>查看学习进度和数据分析</p>
          <div class="card-stats">
            <span>{{ sessionStats.total || 0 }} 次练习</span>
          </div>
        </router-link>
        
        <router-link to="/settings" class="action-card neutral">
          <div class="card-icon">⚙️</div>
          <h3>系统设置</h3>
          <p>配置个人设置</p>
          <div class="card-stats">
            <span>个性化配置</span>
          </div>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { cardAPI, statsAPI } from '@/services/api'

const router = useRouter()

// 统计数据
const questionStats = ref({
  total: 0,
  typeCountMap: {},
  realTypes: []
})

const sessionStats = ref({
  total: 0
})

// 实际题型及数量
const realTypes = ref([])
const typeCountMap = ref({})

// 生命周期
onMounted(() => {
  loadStats()
})

// 方法
async function loadStats() {
  try {
    // 获取卡片统计
    const cards = await cardAPI.getCards()
    // 统计题型及数量
    const typeCountMap = {}
    cards.forEach(c => {
      if (c.card_type) {
        typeCountMap[c.card_type] = (typeCountMap[c.card_type] || 0) + 1
      }
    })
    questionStats.value = {
      total: cards.length,
      typeCountMap,
      realTypes: Object.keys(typeCountMap)
    }
  } catch (error) {
    console.error('获取卡片统计失败:', error)
    questionStats.value = {
      total: 0,
      typeCountMap: {},
      realTypes: []
    }
  }

  // 获取会话统计
  try {
    // 假设用户ID为1，实际应该从用户状态获取
    const userId = 1
    const sessions = await statsAPI.getSessionAnalytics(userId)
    sessionStats.value = {
      total: sessions.total_sessions || 0
    }
  } catch (error) {
    console.warn('获取会话统计失败:', error)
    sessionStats.value = {
      total: 0
    }
  }
}

async function quickDraw() {
  if (questionStats.value.total === 0) {
    alert('请先添加一些卡片再开始练习')
    return
  }
  router.push('/practice')
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
.home {
  min-height: calc(100vh - 60px);
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
  position: relative;
}

.home::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
}

.container {
  position: relative;
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--spacing-2xl);
}

.header {
  text-align: center;
  margin-bottom: var(--spacing-2xl);
  color: white;
}

.header h1 {
  font-size: var(--text-4xl);
  font-weight: 700;
  margin-bottom: var(--spacing-md);
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.subtitle {
  font-size: var(--text-xl);
  margin-bottom: var(--spacing-sm);
  opacity: 0.9;
}

.description {
  font-size: var(--text-base);
  opacity: 0.8;
  max-width: 500px;
  margin: 0 auto;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: var(--spacing-xl);
  margin-bottom: var(--spacing-2xl);
}

.action-card {
  background: var(--bg-primary);
  padding: var(--spacing-xl);
  border-radius: var(--radius-xl);
  text-decoration: none;
  color: var(--text-primary);
  transition: all 0.3s ease;
  box-shadow: var(--shadow-lg);
  position: relative;
  overflow: hidden;
}

.action-card,
.action-card:hover,
.action-card:focus {
  text-decoration: none !important;
}

.action-card h3,
.action-card p,
.action-card .card-stats,
.action-card span {
  text-decoration: none !important;
}

.action-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  transition: all 0.3s ease;
}

.action-card.primary::before {
  background: var(--primary-color);
}

.action-card.secondary::before {
  background: var(--secondary-color);
}

.action-card.accent::before {
  background: var(--accent-color);
}

.action-card.neutral::before {
  background: var(--gray-400);
}

.action-card:hover {
  transform: translateY(-8px);
  box-shadow: var(--shadow-xl);
}

.action-card:hover::before {
  height: 6px;
}

.card-icon {
  font-size: 2.5rem;
  margin-bottom: var(--spacing-md);
}

.action-card h3 {
  font-size: var(--text-xl);
  margin-bottom: var(--spacing-md);
  color: var(--text-primary);
}

.action-card p {
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: var(--spacing-lg);
}

.card-stats {
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--border-color);
  font-size: var(--text-sm);
  color: var(--text-tertiary);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .container {
    padding: var(--spacing-lg);
  }
  
  .header h1 {
    font-size: var(--text-3xl);
  }
  
  .actions-grid {
    grid-template-columns: 1fr;
    gap: var(--spacing-lg);
  }
}
</style>
