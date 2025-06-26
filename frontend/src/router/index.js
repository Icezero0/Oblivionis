import { createRouter, createWebHistory } from 'vue-router'
import { authAPI } from '@/services/api'
import HomeView from '../views/HomeView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/AuthView.vue'),
      meta: { requiresGuest: true }
    },
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { requiresAuth: true }
    },
    {
      path: '/cards',
      name: 'cards',
      component: () => import('../views/CardManagement.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/practice',
      name: 'practice',
      component: () => import('../views/PracticeView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/statistics',
      name: 'statistics', 
      component: () => import('../views/StatisticsView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('../views/SettingsView.vue'),
      meta: { requiresAuth: true }
    },
  ],
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const isAuthenticated = authAPI.isAuthenticated()
  
  if (to.meta.requiresAuth && !isAuthenticated) {
    // 需要认证但未登录，跳转到登录页
    next({ name: 'login' })
  } else if (to.meta.requiresGuest && isAuthenticated) {
    // 需要游客身份但已登录，跳转到首页
    next({ name: 'home' })
  } else {
    next()
  }
})

export default router
