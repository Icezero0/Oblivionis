<!-- 练习设置组件 -->
<template>
  <div class="practice-settings">
    <div class="settings-header">
      <h2>🎯 练习设置</h2>
    </div>

    <form @submit.prevent="handleStart" class="settings-form">
      <!-- 抽题配置 -->
      <div class="setting-group">
        <h3>📚 抽题配置</h3>
        <div v-for="(item, index) in localSettings.items" :key="index" class="config-item">
          <div class="config-controls">
            <!-- 标记选择框（单选下拉，已选类型不可再选） -->
            <div class="type-selector">
              <select v-model="item.tag" required class="form-select">
                <option value="" disabled>请选择题目标记</option>
                <option v-for="tag in availableTypeOptions(index)" :key="tag" :value="tag">{{ tag }}</option>
              </select>
            </div>

            <!-- 数量输入框 -->
            <div class="quantity-input">
              <input 
                type="number" 
                v-model.number="item.quantity"
                min="1" 
                :max="getMaxQuantity(item.tag)"
                placeholder="数量"
                class="input-number"
              >
            </div>

            <!-- 删除按钮 -->
            <button 
              v-if="localSettings.items.length > 1" 
              @click.prevent="removeConfig(index)"
              class="btn-remove"
              title="删除此配置"
            >
              &times;
            </button>
          </div>

          <!-- 错误提示 -->
          <p v-if="!item.tag" class="error-hint">
            请至少选择一个标记
          </p>
          <p v-if="item.quantity < 1" class="error-hint">
            数量必须大于0
          </p>
        </div>

        <!-- 添加配置按钮 -->
        <button 
          @click.prevent="addConfig"
          class="btn-add-config"
        >
          + 添加题目配置
        </button>
      </div>

      <!-- 抽题间隔设置（紧凑样式） -->
      <div class="setting-group compact-group">
        <label for="interval-input" class="compact-label">抽题间隔</label>
        <input id="interval-input" type="number" v-model.number="localSettings.reviewInterval" min="1" max="30" class="input-number compact-input" placeholder="间隔" />
        <small class="input-hint">每道题至少间隔多少次练习后才能再次被抽到</small>
      </div>

      <!-- 开始按钮 -->
      <div class="start-section">
        <button 
          type="submit"
          class="btn btn-primary btn-large"
          :disabled="!canStart"
        >
          <span v-if="loading">⏳ 准备中...</span>
          <span v-else>🚀 开始练习</span>
        </button>
        
        <p v-if="!canStart && localSettings.items.some(item => !item.tag)" class="hint">
          请选择每个配置的题目标记
        </p>
        <p v-else-if="!canStart && localSettings.items.some(item => item.quantity < 1)" class="hint">
          每个配置的题目数量必须大于0
        </p>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { statsAPI, settingsAPI } from '@/services/api'

const props = defineProps({
  modelValue: {
    type: Object,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'start'])

// 本地设置
const localSettings = ref({ 
  strategy: 'smart',
  reviewInterval: '1',
  items: [{ tag: '', quantity: 10 }]
})

// 卡片统计数据
const cardStats = ref([])

// 可用题目标记
const availableTags = computed(() => {
  return cardStats.value.map(stat => stat.tag)
})

// 数量选项
const quantityOptions = computed(() => [
  { value: 10, label: '快速练习 (10题)' },
  { value: 20, label: '标准练习 (20题)' },
  { value: 50, label: '深度练习 (50题)' },
  { value: 'all', label: '全部题目' }
])

// 计算属性
const availableCardsCount = computed(() => {
  return localSettings.value.items
    .flatMap(item => item.tag)
    .reduce((sum, tag) => {
      const count = cardStats.value.find(stat => stat.tag === tag)?.count || 0
      return sum + count
    }, 0)
})

const allAvailableTypes = computed(() => cardStats.value.map(stat => stat.tag))

// 每条配置可选类型（去除其他配置已选的）
function availableTypeOptions(currentIndex) {
  const selected = localSettings.value.items.map((item, idx) => idx !== currentIndex ? item.tag : null).filter(Boolean)
  return allAvailableTypes.value.filter(tag => !selected.includes(tag))
}

const canStart = computed(() => {
  return localSettings.value.items.every(item => item.tag && item.quantity > 0) && localSettings.value.items.length > 0
})

// 方法
function getMaxQuantity(tag) {
  const stat = cardStats.value.find(stat => stat.tag === tag)
  return stat ? Math.min(stat.count, 100) : 1
}

async function loadCardStats() {
  try {
    // 假设用户ID为1，实际应该从用户状态获取
    const userId = 1
    const overview = await statsAPI.getUserOverview(userId)
    cardStats.value = Object.entries(overview.cards_by_type).map(([tag, count]) => ({
      tag,
      count
    }))
  } catch (error) {
    console.error('加载题目统计失败:', error)
    cardStats.value = []
  }
}

// 加载用户已保存的抽题设置
async function loadUserDrawSettings() {
  const userId = 1; // 实际应从用户状态获取
  try {
    const settings = await settingsAPI.getUserSettings(userId);
    if (settings && settings.type_counts) {
      // 转换为本地 items 结构
      localSettings.value.items = Object.entries(settings.type_counts).map(([tag, quantity]) => ({ tag, quantity }))
      if (settings.interval_count) {
        localSettings.value.reviewInterval = settings.interval_count.toString()
      }
    }
  } catch (e) {
    console.warn('加载用户抽题设置失败', e)
  }
}

function handleStart() {
  if (canStart.value) {
    emit('start', { ...localSettings.value })
  }
}

function addConfig() {
  localSettings.value.items.push({ tag: '', quantity: 10 })
}

function removeConfig(index) {
  if (localSettings.value.items.length > 1) {
    localSettings.value.items.splice(index, 1)
  }
}

// 监听器
watch(() => props.modelValue, (newValue) => {
  if (JSON.stringify(newValue) !== JSON.stringify(localSettings.value)) {
    localSettings.value = JSON.parse(JSON.stringify(newValue))
  }
}, { deep: true })

watch(localSettings, (newSettings) => {
  if (JSON.stringify(newSettings) !== JSON.stringify(props.modelValue)) {
    emit('update:modelValue', JSON.parse(JSON.stringify(newSettings)))
  }
}, { deep: true })

// 生命周期
onMounted(() => {
  loadCardStats()
  loadUserDrawSettings()
})

// 调试：输出API返回内容到浏览器控制台
watch(cardStats, (val) => {
  console.log('【练习设置下拉框类型选项API返回】', val)
}, { immediate: true })
</script>

<style scoped>
.practice-settings {
  max-width: 600px;
  margin: 0 auto;
}

.settings-header {
  text-align: center;
  margin-bottom: var(--spacing-2xl);
}

.settings-header h2 {
  margin: 0 0 var(--spacing-sm) 0;
  color: var(--text-primary);
  font-size: var(--text-2xl);
}

.settings-header p {
  color: var(--text-secondary);
  font-size: var(--text-base);
  margin: 0;
}

.settings-form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-2xl);
}

.setting-group h3 {
  margin: 0 0 var(--spacing-lg) 0;
  color: var(--text-primary);
  font-size: var(--text-lg);
  font-weight: 600;
}

/* 抽题配置 */
.config-item {
  background: var(--bg-secondary);
  padding: var(--spacing-md);
  border-radius: var(--radius-md);
  border: 1px solid var(--border-color);
  margin-bottom: var(--spacing-md);
}

.config-controls {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.type-selector {
  flex: 1;
}

/* 数量输入框 */
.quantity-input {
  max-width: 100px;
  flex-shrink: 0;
}

.input-number {
  width: 100%;
  padding: var(--spacing-xs) var(--spacing-sm);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-sm);
  font-size: var(--text-sm);
  text-align: center;
}

/* 删除按钮 */
.btn-remove {
  background: transparent;
  border: none;
  color: var(--error-color);
  cursor: pointer;
  font-size: var(--text-lg);
}

/* 添加配置按钮 */
.btn-add-config {
  align-self: flex-start;
  padding: var(--spacing-sm) var(--spacing-md);
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--primary-color);
  background: var(--bg-primary);
  border: 1px solid var(--primary-color);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-add-config:hover {
  background: var(--primary-color);
  color: #fff;
}

/* 表单选择器 */
.form-select {
  width: 100%;
  padding: var(--spacing-md);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  font-size: var(--text-base);
  background: var(--bg-primary);
  transition: border-color 0.2s ease;
}

.form-select:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
}

/* 开始按钮区域 */
.start-section {
  text-align: center;
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--border-color);
}

.btn-large {
  padding: var(--spacing-lg) var(--spacing-2xl);
  font-size: var(--text-lg);
  font-weight: 600;
}

.error-hint,
.hint {
  color: var(--text-secondary);
  font-size: var(--text-sm);
  margin-top: var(--spacing-sm);
}

.error-hint {
  color: var(--error-color);
}

/* 紧凑样式 */
.compact-group {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin-bottom: var(--spacing-md);
}
.compact-label {
  min-width: 80px;
  font-weight: 500;
  color: var(--text-primary);
}
.compact-input {
  max-width: 100px;
  flex-shrink: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .tag-selector {
    flex-direction: column;
  }
  
  .custom-quantity {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .custom-input {
    margin-left: 0;
    margin-top: var(--spacing-xs);
  }
}
</style>
