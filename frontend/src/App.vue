<template>
  <div id="app">
    <!-- 导航栏 -->
    <nav v-if="userStore.isAuthenticated" class="navbar">
      <div class="nav-container">
        <router-link to="/" class="nav-brand">
          🧠 Oblivionis
        </router-link>
        
        <div class="nav-links">
          <router-link to="/cards" class="nav-link">题目管理</router-link>
          <router-link to="/practice" class="nav-link">抽题练习</router-link>
          <router-link to="/statistics" class="nav-link">学习统计</router-link>
          <router-link to="/settings" class="nav-link">系统设置</router-link>
        </div>
        
        <div class="nav-user">
          <span class="user-name">{{ userStore.currentUser?.username }}</span>
          <button @click="handleLogout" class="logout-btn">登出</button>
        </div>
      </div>
    </nav>
    
    <!-- 主内容区域 -->
    <main class="main-content" :class="{ 'with-navbar': userStore.isAuthenticated }">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores'

const router = useRouter()
const userStore = useUserStore()

onMounted(async () => {
  // 应用启动时检查用户认证状态
  await userStore.checkAuth()
})

async function handleLogout() {
  await userStore.logout()
  router.push('/login')
}
</script>

<style>
#app {
  min-height: 100vh;
  background-color: var(--bg-secondary);
}

.navbar {
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-color);
  box-shadow: var(--shadow-sm);
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 var(--spacing-lg);
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
}

.nav-brand {
  font-size: var(--text-xl);
  font-weight: 700;
  color: var(--primary-color);
  text-decoration: none;
  transition: color 0.2s ease;
}

.nav-brand:hover {
  color: var(--primary-dark);
}

.nav-brand,
.nav-brand:hover,
.nav-brand.router-link-active {
  text-decoration: none !important;
  border-bottom: none !important;
}

.nav-brand.router-link-active::after {
  content: none !important;
}

.nav-links {
  display: flex;
  gap: var(--spacing-lg);
}

.nav-link {
  color: var(--text-secondary);
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s ease;
  position: relative;
}

.nav-link:hover {
  color: var(--text-primary);
}

.nav-link.router-link-active {
  color: var(--primary-color);
}

.nav-link,
.nav-link:hover,
.nav-link.router-link-active,
.nav-link.router-link-active::after {
  text-decoration: none !important;
  border-bottom: none !important;
}

.nav-link.router-link-active::after {
  content: none !important;
}

.nav-user {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.user-name {
  color: var(--text-secondary);
  font-weight: 500;
}

.logout-btn {
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--bg-secondary);
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: var(--text-sm);
}

.logout-btn:hover {
  background: var(--error-color);
  color: white;
  border-color: var(--error-color);
}

.main-content {
  min-height: 100vh;
}

.main-content.with-navbar {
  min-height: calc(100vh - 60px);
}

@media (max-width: 768px) {
  .nav-container {
    padding: 0 var(--spacing-md);
  }
  
  .nav-links {
    display: none;
  }
  
  .nav-brand {
    font-size: var(--text-lg);
  }
  
  .user-name {
    display: none;
  }
}
</style>
