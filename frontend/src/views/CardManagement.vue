<!-- 卡片管理页面 -->
<template>
  <div class="question-management">
    <div class="container">
      <div class="page-header">
        <h1>📚 卡片管理</h1>
        <div class="header-actions">
          <button class="btn btn-primary" @click="showAddModal = true">
            ➕ 添加卡片
          </button>
          <button class="btn btn-secondary" @click="showBatchModal = true">
            📥 批量导入
          </button>
        </div>
      </div>

      <!-- 卡片标记过滤 -->
      <div class="filter-section">
        <div class="filter-tabs">
          <button 
            v-for="tab in filterTabs" 
            :key="tab.value"
            class="filter-tab"
            :class="{ active: currentFilter === tab.value }"
            @click="currentFilter = tab.value"
          >
            {{ tab.label }} ({{ getFilterCount(tab.value) }})
          </button>
        </div>
      </div>

      <!-- 卡片列表 -->
      <QuestionList
        :questions="filteredQuestions"
        :loading="loading"
        :type-filter="currentFilter"
        :empty-title="currentFilter === 'all' ? '还没有卡片' : `暂无${getFilterLabel(currentFilter)}卡片`"
        :empty-message="currentFilter === 'all' ? '创建第一张卡片开始学习吧！' : `暂无${getFilterLabel(currentFilter)}，可以添加或查看其他标签`"
        @select-question="selectQuestion"
        @edit-question="editQuestion"
        @delete-question="deleteQuestion"
        @add-question="showAddModal = true"
      />

      <!-- 添加/编辑卡片模态框 -->
      <div v-if="showAddModal || showEditModal" class="modal-overlay">
        <div class="modal" @click.stop>
          <h2>{{ showEditModal ? '编辑卡片' : '添加卡片' }}</h2>
          
          <QuestionForm
            v-model="questionForm"
            :is-edit="showEditModal"
            :loading="saving"
            :existing-types="existingCardTypes"
            @submit="saveQuestion"
            @cancel="closeModals"
          />
        </div>
      </div>

      <!-- 批量导入模态框 -->
      <div v-if="showBatchModal" class="modal-overlay">
        <div class="modal modal-large" @click.stop>
          <BatchImport
            :loading="importing"
            @import="importBatchQuestions"
            @cancel="closeModals"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useCardStore } from '@/stores'
import { cardAPI } from '@/services/api'
import QuestionList from '@/components/QuestionList.vue'
import QuestionForm from '@/components/QuestionForm.vue'
import BatchImport from '@/components/BatchImport.vue'

// 状态管理
const cardStore = useCardStore()
const { cards, loading } = storeToRefs(cardStore)

// 本地状态
const showAddModal = ref(false)
const showEditModal = ref(false)
const showBatchModal = ref(false)
const selectedQuestion = ref(null)
const saving = ref(false)
const importing = ref(false)
const currentFilter = ref('all')

// 表单数据
const questionForm = ref({
  content: '',
  card_type: '',
  notes: ''
})

// 计算属性
const filteredQuestions = computed(() => {
  if (!cards.value || !Array.isArray(cards.value)) {
    return []
  }
  if (currentFilter.value === 'all') {
    return cards.value
  }
  return cards.value.filter(card => card.card_type === currentFilter.value)
})

// 动态生成过滤选项
const filterTabs = computed(() => {
  if (!cards.value || !Array.isArray(cards.value)) {
    return [{ value: 'all', label: '全部' }]
  }
  
  // 获取所有唯一的卡片类型
  const uniqueTypes = [...new Set(cards.value.map(card => card.card_type))]
    .filter(type => type) // 过滤掉空值
    .sort() // 按字母顺序排序
  
  // 生成过滤标签
  const tabs = [{ value: 'all', label: '全部' }]
  
  uniqueTypes.forEach(type => {
    tabs.push({
      value: type,
      label: type
    })
  })
  
  return tabs
})

// 获取已存在的卡片标记类型
const existingCardTypes = computed(() => {
  if (!cards.value || !Array.isArray(cards.value)) {
    return []
  }
  return [...new Set(cards.value.map(card => card.card_type))]
    .filter(type => type && type.trim())
    .sort()
})

// 生命周期
onMounted(() => {
  loadQuestions()
})

// 监听器
watch(() => showAddModal.value, (newVal) => {
  if (newVal) {
    resetForm()
  }
})

// 监听卡片类型变化，重置过滤器
// 优化递归：只有当前过滤器失效且不是'all'时才赋值，避免死循环
watch(() => filterTabs.value, (newTabs) => {
  if (currentFilter.value !== 'all') {
    const currentExists = newTabs.some(tab => tab.value === currentFilter.value)
    if (!currentExists) {
      currentFilter.value = 'all'
    }
  }
}, { deep: true })

// 方法
async function loadQuestions() {
  try {
    cardStore.setLoading(true)
    const data = await cardAPI.getCards()
    cardStore.setCards(data)
  } catch (err) {
    console.error('加载卡片失败:', err)
  } finally {
    cardStore.setLoading(false)
  }
}

function selectQuestion(question) {
  cardStore.setCurrentCard(question)
}

function editQuestion(question) {
  selectedQuestion.value = question
  questionForm.value = {
    content: question.content,
    card_type: question.card_type,
    notes: question.notes || ''
  }
  showEditModal.value = true
}

async function deleteQuestion(questionId) {
  try {
    await cardAPI.deleteCard(questionId)
    cardStore.deleteCard(questionId)
    console.log('卡片删除成功')
  } catch (err) {
    console.error('删除卡片失败:', err)
  }
}

async function saveQuestion(formData) {
  try {
    saving.value = true
    
    const questionData = {
      content: formData.content.trim(),
      card_type: formData.card_type,
      notes: formData.notes.trim() || null
    }

    if (showEditModal.value && selectedQuestion.value) {
      // 编辑模式
      const updatedQuestion = await cardAPI.updateCard(selectedQuestion.value.id, questionData)
      cardStore.updateCard(updatedQuestion)
      console.log('卡片更新成功')
    } else {
      // 添加模式
      const newQuestion = await cardAPI.createCard(questionData)
      cardStore.addCard(newQuestion)
      console.log('卡片添加成功')
    }
    
    closeModals()
  } catch (err) {
    console.error('保存卡片失败:', err)
  } finally {
    saving.value = false
  }
}

async function importBatchQuestions(questions) {
  try {
    importing.value = true
    
    const questionsData = {
      cards: questions
    }

    const result = await cardAPI.createCards(questionsData)
    
    // 添加到本地状态
    result.forEach(question => {
      cardStore.addCard(question)
    })
    
    console.log(`成功导入 ${result.length} 张卡片`)
    closeModals()
  } catch (err) {
    console.error('批量导入失败:', err)
  } finally {
    importing.value = false
  }
}

function closeModals() {
  showAddModal.value = false
  showEditModal.value = false
  showBatchModal.value = false
  selectedQuestion.value = null
  resetForm()
}

function resetForm() {
  questionForm.value = {
    content: '',
    card_type: '',
    notes: ''
  }
}

function getFilterLabel(filterValue) {
  const tab = filterTabs.value.find(t => t.value === filterValue)
  return tab ? tab.label : filterValue
}

function getFilterCount(filterValue) {
  if (!cards.value || !Array.isArray(cards.value)) {
    return 0
  }
  if (filterValue === 'all') {
    return cards.value.length
  }
  return cards.value.filter(card => card.card_type === filterValue).length
}
</script>

<style scoped>
.question-management {
  padding: var(--spacing-xl) 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-xl);
}

.page-header h1 {
  margin: 0;
  color: var(--text-primary);
}

.header-actions {
  display: flex;
  gap: var(--spacing-md);
}

/* 过滤器样式 */
.filter-section {
  margin-bottom: var(--spacing-xl);
}

.filter-tabs {
  display: flex;
  gap: var(--spacing-sm);
  border-bottom: 2px solid var(--border-color);
}

.filter-tab {
  padding: var(--spacing-md) var(--spacing-lg);
  border: none;
  background: none;
  color: var(--text-secondary);
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.2s ease;
  font-weight: 500;
}

.filter-tab:hover {
  color: var(--text-primary);
  background: var(--bg-secondary);
}

.filter-tab.active {
  color: var(--primary-color);
  border-bottom-color: var(--primary-color);
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl);
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: var(--shadow-xl);
}

.modal-large {
  max-width: 800px;
}

.modal h2 {
  margin: 0 0 var(--spacing-lg) 0;
  color: var(--text-primary);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    gap: var(--spacing-md);
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: center;
  }
  
  .filter-tabs {
    flex-wrap: wrap;
  }
  
  .modal {
    width: 95%;
    margin: var(--spacing-md);
  }
}
</style>
