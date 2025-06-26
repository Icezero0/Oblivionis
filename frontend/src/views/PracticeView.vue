<!-- 练习页面 -->
<template>
  <div class="practice-page">
    <div class="container">
      <div v-if="noCardToast" class="no-card-toast">未找到符合条件的卡片</div>
      <!-- 练习设置阶段 -->
      <div v-if="currentStage === 'setup'" class="setup-stage">
        <PracticeSettings
          v-model="practiceSettings"
          :loading="loading"
          @start="startPractice"
        />
      </div>

      <!-- 练习进行阶段 -->
      <div v-else-if="currentStage === 'practicing'" class="practice-stage">
        <PracticeCard
          :card="currentCard"
          :current-index="currentCardIndex"
          :total-count="totalCards"
          @answer="handleAnswer"
          @skip="handleSkip"
          @next="handleNext"
          @end="endPractice"
        />
      </div>

      <!-- 练习结果阶段 -->
      <div v-else-if="currentStage === 'results'" class="results-stage">
        <PracticeResults
          :results="practiceResults"
          @restart="restartPractice"
          @new-practice="newPractice"
          @view-stats="viewStats"
        />
      </div>

      <!-- 加载阶段 -->
      <div v-else class="loading-stage">
        <div class="loading-container">
          <div class="loading-spinner"></div>
          <p>正在准备练习...</p>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { drawAPI, statsAPI, settingsAPI } from '@/services/api'
import PracticeSettings from '@/components/PracticeSettings.vue'
import PracticeCard from '@/components/PracticeCard.vue'
import PracticeResults from '@/components/PracticeResults.vue'

// 路由
const router = useRouter()

// 练习阶段控制
const currentStage = ref('setup') // setup, practicing, results, loading
const loading = ref(false)

// 练习设置
const practiceSettings = ref({
  cardTypes: ['M'],
  quantity: 10,
  customQuantity: 10,
  strategy: 'random',
  reviewInterval: 1
})

// 练习状态
const drawnCards = ref([])
const currentCardIndex = ref(0)
const currentCard = ref(null)
const totalCards = ref(0)
const practiceResults = ref({
  totalCards: 0,
  answered: 0,
  correct: 0,
  skipped: 0,
  selfRatings: [],
  practiceTime: 0,
  cardTypeStats: {},
  accuracy: 0,
  startTime: null,
  endTime: null
})

// 计算属性
const hasCards = computed(() => drawnCards.value.length > 0)

// 生命周期
onMounted(() => {
  // 初始化
})

// 获取实际练习数量
function getActualQuantity() {
  if (practiceSettings.value.quantity === 'all') {
    return 999 // 使用一个大数字表示全部
  } else if (practiceSettings.value.quantity === 'custom') {
    return practiceSettings.value.customQuantity || 10
  } else {
    return practiceSettings.value.quantity
  }
}

// 开始练习
async function startPractice() {
  loading.value = true
  currentStage.value = 'loading'
  await saveDrawSettings()
  try {
    // 调用抽题接口 - 传递userId参数
    const userId = 1 // 实际应该从用户状态获取
    const response = await drawAPI.drawCards(userId, {
      type_counts: practiceSettings.value.items.reduce((acc, item) => {
        if (item.tag && item.quantity > 0) {
          acc[item.tag] = item.quantity
        }
        return acc
      }, {}),
      interval_count: practiceSettings.value.reviewInterval
    })
    
    // 合并所有类型的卡片为一个数组
    const allCards = Object.values(response.cards_by_type || {}).flat();

    if (allCards.length > 0) {
      drawnCards.value = allCards;
      totalCards.value = allCards.length;
      currentCardIndex.value = 0;
      currentCard.value = allCards[0];
      // 初始化练习结果
      practiceResults.value = {
        totalCards: allCards.length,
        answered: 0,
        correct: 0,
        skipped: 0,
        selfRatings: [],
        practiceTime: 0,
        cardTypeStats: {},
        accuracy: 0,
        startTime: new Date(),
        endTime: null
      };
      currentStage.value = 'practicing';
      console.log('练习开始！');
    } else {
      // 输出调试信息
      console.log('【未找到符合条件的卡片】API返回：', response);
      console.log('【当前抽题设置】', JSON.stringify({
        type_counts: practiceSettings.value.items.reduce((acc, item) => {
          if (item.tag && item.quantity > 0) acc[item.tag] = item.quantity;
          return acc;
        }, {}),
        interval_count: practiceSettings.value.reviewInterval
      }, null, 2));
      showNoCardToast();
      currentStage.value = 'setup';
    }
  } catch (error) {
    console.error('开始练习失败:', error)
    currentStage.value = 'setup'
  } finally {
    loading.value = false
  }
}

// 处理答题
function handleAnswer(answerData) {
  // 更新练习结果
  practiceResults.value.answered++
  
  // 这里可以添加更复杂的正确性判断逻辑
  // 目前基于自评分数简单判断
  const isCorrect = answerData.selfRating === 'perfect' || answerData.selfRating === 'good'
  if (isCorrect) {
    practiceResults.value.correct++
  }
  
  // 记录自评
  if (answerData.selfRating) {
    practiceResults.value.selfRatings.push(answerData.selfRating)
  }
  
  // 更新题型统计
  updateCardTypeStats(answerData, isCorrect)
  
  // 更新整体准确率
  updateOverallAccuracy()
}

// 更新题型统计
function updateCardTypeStats(answerData, isCorrect) {
  const cardType = currentCard.value.card_type
  if (!practiceResults.value.cardTypeStats[cardType]) {
    practiceResults.value.cardTypeStats[cardType] = {
      total: 0,
      correct: 0,
      accuracy: 0
    }
  }
  practiceResults.value.cardTypeStats[cardType].total++
  if (isCorrect) {
    practiceResults.value.cardTypeStats[cardType].correct++
  }
  practiceResults.value.cardTypeStats[cardType].accuracy = 
    (practiceResults.value.cardTypeStats[cardType].correct / 
     practiceResults.value.cardTypeStats[cardType].total) * 100
}

// 更新整体准确率
function updateOverallAccuracy() {
  if (practiceResults.value.answered > 0) {
    practiceResults.value.accuracy = 
      (practiceResults.value.correct / practiceResults.value.answered) * 100
  }
}

// 处理跳过
function handleSkip() {
  practiceResults.value.skipped++
}

// 下一题
function handleNext() {
  if (currentCardIndex.value < drawnCards.value.length - 1) {
    currentCardIndex.value++
    currentCard.value = drawnCards.value[currentCardIndex.value]
  } else {
    endPractice()
  }
}

// 结束练习
function endPractice() {
  practiceResults.value.endTime = new Date()
  practiceResults.value.practiceTime = Math.round(
    (practiceResults.value.endTime - practiceResults.value.startTime) / 1000
  )
  
  currentStage.value = 'results'
  console.log('练习完成！')
}

// 重新开始练习
function restartPractice() {
  currentStage.value = 'setup'
  // 重置状态
  drawnCards.value = []
  currentCardIndex.value = 0
  currentCard.value = null
  totalCards.value = 0
}

// 新练习
function newPractice() {
  restartPractice()
}

// 查看统计
function viewStats() {
  router.push('/statistics')
}

// 保存抽卡设置到后端（可选，建议在设置变更或开始练习时调用）
async function saveDrawSettings() {
  const userId = 1; // 实际应从用户状态获取
  const type_counts = practiceSettings.value.items.reduce((acc, item) => {
    if (item.tag && item.quantity > 0) acc[item.tag] = item.quantity;
    return acc;
  }, {});
  const interval_count = practiceSettings.value.reviewInterval;
  try {
    await settingsAPI.createOrUpdateSettings(userId, {
      type_counts,
      interval_count
    });
    console.log('抽卡设置已保存到后端');
  } catch (e) {
    console.error('保存抽卡设置失败', e);
  }
}

// 浮起提示逻辑
const noCardToast = ref(false)
function showNoCardToast() {
  noCardToast.value = true
  nextTick(() => {
    setTimeout(() => {
      noCardToast.value = false
    }, 2000)
  })
}
</script>
<style scoped>
.practice-page {
  padding: var(--spacing-xl) 0;
  min-height: 100vh;
}

.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 var(--spacing-md);
}

.setup-stage,
.practice-stage,
.results-stage {
  width: 100%;
}

.loading-stage {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 50vh;
}

.loading-container {
  text-align: center;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  margin: 0 auto var(--spacing-md);
  border: 4px solid var(--border-color);
  border-top: 4px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading-container p {
  color: var(--text-secondary);
  margin: 0;
}

.no-card-toast {
  position: fixed;
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0,0,0,0.85);
  color: #fff;
  padding: 1rem 2rem;
  border-radius: 1.5rem;
  font-size: 1.1rem;
  z-index: 9999;
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
  animation: fadeInOut 2s;
}

@keyframes fadeInOut {
  0% { opacity: 0; }
  10% { opacity: 1; }
  90% { opacity: 1; }
  100% { opacity: 0; }
}

@media (max-width: 768px) {
  .container {
    padding: 0 var(--spacing-sm);
  }
}
</style>
