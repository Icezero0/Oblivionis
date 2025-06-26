import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { authAPI } from '@/services/api'

// 用户状态管理
export const useUserStore = defineStore('user', () => {
  const currentUser = ref(null)
  const loading = ref(false)
  
  const isAuthenticated = computed(() => !!currentUser.value)

  function setUser(user) {
    currentUser.value = user
  }

  function setLoading(state) {
    loading.value = state
  }

  async function logout() {
    try {
      await authAPI.logout()
      currentUser.value = null
    } catch (error) {
      console.error('登出失败:', error)
      // 即使API调用失败，也清除本地用户状态
      currentUser.value = null
    }
  }

  async function checkAuth() {
    if (!authAPI.isAuthenticated()) {
      return false
    }

    try {
      setLoading(true)
      const user = await authAPI.getCurrentUser()
      setUser(user)
      return true
    } catch (error) {
      console.error('验证用户身份失败:', error)
      currentUser.value = null
      return false
    } finally {
      setLoading(false)
    }
  }

  return {
    currentUser,
    loading,
    isAuthenticated,
    setUser,
    setLoading,
    logout,
    checkAuth
  }
})

// 卡片状态管理
export const useCardStore = defineStore('card', () => {
  const cards = ref([])
  const currentCard = ref(null)
  const loading = ref(false)

  function setCards(newCards) {
    cards.value = newCards
  }

  function addCard(card) {
    cards.value.push(card)
  }

  function updateCard(updatedCard) {
    const index = cards.value.findIndex(card => card.id === updatedCard.id)
    if (index !== -1) {
      cards.value[index] = updatedCard
    }
  }

  function deleteCard(cardId) {
    cards.value = cards.value.filter(card => card.id !== cardId)
  }

  function setCurrentCard(card) {
    currentCard.value = card
  }

  function setLoading(state) {
    loading.value = state
  }

  return {
    cards,
    currentCard,
    loading,
    setCards,
    addCard,
    updateCard,
    deleteCard,
    setCurrentCard,
    setLoading
  }
})

// 练习状态管理
export const usePracticeStore = defineStore('practice', () => {
  const currentSession = ref(null)
  const practiceStats = ref({})
  const settings = ref({
    cardTypes: [],
    difficulty: 'all',
    reviewInterval: 1
  })

  function startSession(sessionData) {
    currentSession.value = sessionData
  }

  function endSession() {
    currentSession.value = null
  }

  function updateStats(stats) {
    practiceStats.value = stats
  }

  function updateSettings(newSettings) {
    settings.value = { ...settings.value, ...newSettings }
  }

  return {
    currentSession,
    practiceStats,
    settings,
    startSession,
    endSession,
    updateStats,
    updateSettings
  }
})
