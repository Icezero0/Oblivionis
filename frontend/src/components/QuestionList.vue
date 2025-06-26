<!-- 题目列表组件 -->
<template>
  <div class="question-list">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>
    
    <!-- 空状态 -->
    <div v-else-if="questions.length === 0" class="empty-state">
      <div class="empty-icon">📝</div>
      <h3>{{ emptyTitle }}</h3>
      <p>{{ emptyMessage }}</p>
      <button v-if="showAddButton" class="btn btn-primary" @click="$emit('add-question')">
        ➕ 添加第一道题目
      </button>
    </div>
    
    <!-- 题目网格 -->
    <div v-else class="questions-grid">
      <div class="grid-header" v-if="showStats">
        <div class="stats-info">
          <span>共 {{ questions.length }} 道题目</span>
          <span v-if="typeFilter !== 'all'">筛选结果</span>
        </div>
        <div class="view-options">
          <button 
            class="view-toggle"
            :class="{ active: viewMode === 'grid' }"
            @click="setViewMode('grid')"
            title="网格视图"
          >
            ⊞
          </button>
          <button 
            class="view-toggle"
            :class="{ active: viewMode === 'list' }"
            @click="setViewMode('list')"
            title="列表视图"
          >
            ☰
          </button>
        </div>
      </div>
      
      <div class="questions-container" :class="`view-${viewMode}`">
        <QuestionCard
          v-for="question in questions" 
          :key="question.id" 
          :question="question"
          :view-mode="viewMode"
          @select="$emit('select-question', question)"
          @edit="$emit('edit-question', question)"
          @delete="$emit('delete-question', question.id)"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import QuestionCard from './QuestionCard.vue'

const props = defineProps({
  questions: {
    type: Array,
    default: () => []
  },
  loading: {
    type: Boolean,
    default: false
  },
  typeFilter: {
    type: String,
    default: 'all'
  },
  emptyTitle: {
    type: String,
    default: '暂无题目'
  },
  emptyMessage: {
    type: String,
    default: '还没有题目，创建第一道题目开始学习吧！'
  },
  showAddButton: {
    type: Boolean,
    default: true
  },
  showStats: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits([
  'select-question',
  'edit-question', 
  'delete-question',
  'add-question'
])

// 视图模式
const viewMode = ref('grid')

function setViewMode(mode) {
  viewMode.value = mode
}
</script>

<style scoped>
.question-list {
  min-height: 400px;
}

/* 加载状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-2xl);
  color: var(--text-secondary);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--border-color);
  border-top: 4px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: var(--spacing-md);
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-2xl);
  text-align: center;
  color: var(--text-secondary);
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: var(--spacing-lg);
  opacity: 0.6;
}

.empty-state h3 {
  margin: 0 0 var(--spacing-md) 0;
  color: var(--text-primary);
  font-size: var(--text-xl);
}

.empty-state p {
  margin: 0 0 var(--spacing-xl) 0;
  max-width: 400px;
  line-height: 1.6;
}

/* 网格头部 */
.grid-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
  padding-bottom: var(--spacing-md);
  border-bottom: 1px solid var(--border-color);
}

.stats-info {
  display: flex;
  gap: var(--spacing-md);
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

.view-options {
  display: flex;
  gap: var(--spacing-xs);
}

.view-toggle {
  padding: var(--spacing-xs) var(--spacing-sm);
  border: 1px solid var(--border-color);
  background: var(--bg-primary);
  color: var(--text-secondary);
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: all 0.2s ease;
  font-size: var(--text-lg);
}

.view-toggle:hover {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.view-toggle.active {
  background: var(--primary-color);
  color: white;
  border-color: var(--primary-color);
}

/* 网格容器 */
.questions-container.view-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: var(--spacing-lg);
}

.questions-container.view-list {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .questions-container.view-grid {
    grid-template-columns: 1fr;
  }
  
  .grid-header {
    flex-direction: column;
    gap: var(--spacing-md);
    align-items: stretch;
  }
  
  .stats-info {
    justify-content: center;
  }
  
  .view-options {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .empty-state {
    padding: var(--spacing-xl);
  }
  
  .empty-icon {
    font-size: 3rem;
  }
}
</style>
