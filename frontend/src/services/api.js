/**
 * 前端API服务 - 与后端FastAPI完全对应
 * 
 * 后端API路由对应：
 * - /api/users (users.py)
 * - /api/cards (cards.py) 
 * - /api/draw (draw.py)
 * - /api/settings (settings.py)
 * - /api/stats (stats.py)
 */

// API 基础配置
let API_BASE_URL = import.meta.env.VITE_API_BASE_URL
if (!API_BASE_URL) {
  if (import.meta.env.DEV) {
    // 开发环境，使用Vite代理
    API_BASE_URL = '/api'
  } else {
    // 生产环境，自动适配当前域名+8000端口
    const { protocol, hostname } = window.location
    API_BASE_URL = `${protocol}//${hostname}:8000`
  }
}

// 获取存储的token
function getAuthToken() {
  return localStorage.getItem('auth_token')
}

// 设置认证token
function setAuthToken(token) {
  localStorage.setItem('auth_token', token)
}

// 清除认证token
function clearAuthToken() {
  localStorage.removeItem('auth_token')
}

// 基础 API 请求函数
async function apiRequest(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`
  const token = getAuthToken()
  
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
    ...options,
  }

  try {
    const response = await fetch(url, config)
    let data
    try {
      data = await response.clone().json()
    } catch (e) {
      data = null
    }
    if (!response.ok) {
      if (response.status === 401) {
        clearAuthToken()
        window.location.href = '/login'
        throw new Error('认证失败，请重新登录')
      }
      // 输出后端返回的详细错误信息
      console.log('API 400/错误响应:', {
        url,
        status: response.status,
        data
      })
      // 抛出包含后端错误信息的异常
      const error = new Error(`HTTP error! status: ${response.status}`)
      error.response = response
      error.data = data
      throw error
    }
    return data
  } catch (error) {
    console.error('API request failed:', error)
    throw error
  }
}

// 认证相关 API - 对应 backend/app/routers/users.py
export const authAPI = {
  // 用户注册 - POST /api/users/register
  register: (userData) => apiRequest('/api/users/register', {
    method: 'POST',
    body: JSON.stringify(userData),
  }).then(response => {
    // 注册成功后自动保存token
    if (response.access_token) {
      setAuthToken(response.access_token)
    }
    return response
  }),
  
  // 用户登录 - POST /api/users/login
  login: (credentials) => apiRequest('/api/users/login', {
    method: 'POST',
    body: JSON.stringify(credentials),
  }).then(response => {
    // 登录成功后保存token
    if (response.access_token) {
      setAuthToken(response.access_token)
    }
    return response
  }),
  
  // 用户登出
  logout: () => {
    clearAuthToken()
    return Promise.resolve()
  },
  
  // 获取当前用户信息 - GET /api/users/me
  getCurrentUser: () => apiRequest('/api/users/me'),
  
  // 检查是否已登录
  isAuthenticated: () => !!getAuthToken(),
}

// 用户相关 API - 对应 backend/app/routers/users.py
export const userAPI = {
  // 获取所有用户 - GET /api/users
  getUsers: (skip = 0, limit = 100) => apiRequest(`/api/users/?skip=${skip}&limit=${limit}`),
  
  // 获取单个用户 - GET /api/users/{user_id}
  getUser: (userId) => apiRequest(`/api/users/${userId}`),
}

// 卡片相关 API - 对应 backend/app/routers/cards.py
export const cardAPI = {
  // 获取所有卡片 - GET /api/cards/
  getCards: (cardType = null, skip = 0, limit = 100) => {
    let url = `/api/cards/?skip=${skip}&limit=${limit}`
    if (cardType) url += `&card_type=${cardType}`
    return apiRequest(url)
  },
  
  // 获取单个卡片 - GET /api/cards/{card_id}
  getCard: (cardId) => apiRequest(`/api/cards/${cardId}`),
  
  // 创建卡片 - POST /api/cards
  createCard: (cardData) => apiRequest(`/api/cards/`, {
    method: 'POST',
    body: JSON.stringify({
      content: cardData.content,
      card_type: cardData.card_type,
      notes: cardData.notes
    }),
  }),
  
  // 批量创建卡片 - POST /api/cards/batch
  createCards: (cardsData) => apiRequest(`/api/cards/batch`, {
    method: 'POST',
    body: JSON.stringify(cardsData),
  }),
  
  // 更新卡片 - PUT /api/cards/{card_id}
  updateCard: (cardId, cardData) => apiRequest(`/api/cards/${cardId}`, {
    method: 'PUT',
    body: JSON.stringify({
      content: cardData.content,
      card_type: cardData.card_type,
      notes: cardData.notes
    }),
  }),
  
  // 删除卡片 - DELETE /api/cards/{card_id}
  deleteCard: (cardId) => apiRequest(`/api/cards/${cardId}`, {
    method: 'DELETE',
  }),
}

// 抽题相关 API - 对应 backend/app/routers/draw.py
export const drawAPI = {
  // 抽取卡片 - POST /api/draw
  drawCards: (userId, drawData) => apiRequest(`/api/draw/?user_id=${userId}`, {
    method: 'POST',
    body: JSON.stringify(drawData),
  }),
  
  // 获取抽题统计 - GET /api/draw/statistics/{user_id}
  getDrawStatistics: (userId) => apiRequest(`/api/draw/statistics/${userId}`),
  
  // 获取用户会话历史 - GET /api/draw/sessions/{user_id}
  getUserSessions: (userId, skip = 0, limit = 50) => 
    apiRequest(`/api/draw/sessions/${userId}?skip=${skip}&limit=${limit}`),
  
  // 获取会话详情 - GET /api/draw/sessions/detail/{session_id}
  getSessionDetail: (sessionId) => apiRequest(`/api/draw/sessions/detail/${sessionId}`),
  
  // 删除会话 - DELETE /api/draw/sessions/{session_id}
  deleteSession: (sessionId) => apiRequest(`/api/draw/sessions/${sessionId}`, {
    method: 'DELETE',
  }),
  
  // 导出会话数据 - GET /api/draw/sessions/{user_id}/export
  exportSessions: (userId) => apiRequest(`/api/draw/sessions/${userId}/export`),
}

// 用户设置相关 API - 对应 backend/app/routers/settings.py
export const settingsAPI = {
  // 创建或更新设置 - POST /api/settings
  createOrUpdateSettings: (userId, settingsData) => apiRequest(`/api/settings/?user_id=${userId}`, {
    method: 'POST',
    body: JSON.stringify(settingsData),
  }),
  
  // 获取用户设置 - GET /api/settings/{user_id}
  getUserSettings: (userId) => apiRequest(`/api/settings/${userId}`),
  
  // 更新用户设置 - PUT /api/settings/{user_id}
  updateUserSettings: (userId, settingsData) => apiRequest(`/api/settings/${userId}`, {
    method: 'PUT',
    body: JSON.stringify(settingsData),
  }),
  
  // 删除用户设置 - DELETE /api/settings/{user_id}
  deleteUserSettings: (userId) => apiRequest(`/api/settings/${userId}`, {
    method: 'DELETE',
  }),
}

// 统计相关 API - 对应 backend/app/routers/stats.py
export const statsAPI = {
  // 获取用户总览 - GET /api/stats/overview/{user_id}
  getUserOverview: (userId) => apiRequest(`/api/stats/overview/${userId}`),
  
  // 获取卡片统计 - GET /api/stats/cards/{user_id}
  getCardStatistics: (userId, cardType = null) => {
    const url = cardType 
      ? `/api/stats/cards/${userId}?card_type=${cardType}` 
      : `/api/stats/cards/${userId}`
    return apiRequest(url)
  },
  
  // 获取会话分析 - GET /api/stats/sessions/{user_id}
  getSessionAnalytics: (userId, days = 30) => apiRequest(`/api/stats/sessions/${userId}?days=${days}`),
  
  // 获取学习进度 - GET /api/stats/progress/{user_id}
  getLearningProgress: (userId) => apiRequest(`/api/stats/progress/${userId}`),
  
  // 获取推荐信息 - GET /api/stats/recommendations/{user_id}
  getRecommendations: (userId) => apiRequest(`/api/stats/recommendations/${userId}`),
  
  // 获取仪表板数据 - GET /api/stats/dashboard/{user_id}
  getDashboardData: (userId) => apiRequest(`/api/stats/dashboard/${userId}`),
}

// 为了向后兼容，保留原有的练习API别名
export const practiceAPI = {
  // 抽取卡片（别名）
  drawCards: (drawData) => {
    // 假设使用用户ID 1，实际应该从用户状态获取
    const userId = 1
    return drawAPI.drawCards(userId, drawData)
  },
  
  // 获取用户设置（别名）
  getSettings: (userId) => settingsAPI.getUserSettings(userId),
  
  // 更新用户设置（别名）
  updateSettings: (userId, settingsData) => settingsAPI.updateUserSettings(userId, settingsData),
}

// 导出默认 API 对象
export default {
  auth: authAPI,
  user: userAPI,
  card: cardAPI,
  draw: drawAPI,
  settings: settingsAPI,
  stats: statsAPI,
  practice: practiceAPI, // 向后兼容
}

// 导出认证相关的工具函数
export { getAuthToken, setAuthToken, clearAuthToken }
