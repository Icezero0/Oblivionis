<template>
  <div class="auth-page">
    <div class="auth-container">
      <div class="auth-card">
        <div class="auth-header">
          <h1>🧠 Oblivionis</h1>
          <p>{{ isLogin ? '欢迎回来' : '创建新账户' }}</p>
        </div>

        <div class="auth-tabs">
          <button 
            class="auth-tab" 
            :class="{ active: isLogin }"
            @click="isLogin = true"
          >
            登录
          </button>
          <button 
            class="auth-tab" 
            :class="{ active: !isLogin }"
            @click="isLogin = false"
          >
            注册
          </button>
        </div>

        <form @submit.prevent="handleSubmit" class="auth-form">
          <div v-if="!isLogin" class="form-group">
            <label for="email">邮箱地址</label>
            <input 
              id="email"
              v-model="formData.email" 
              type="email" 
              required
              placeholder="请输入邮箱地址"
            >
          </div>

          <div class="form-group">
            <label for="username">用户名</label>
            <input 
              id="username"
              v-model="formData.username" 
              type="text" 
              required
              placeholder="请输入用户名"
            >
          </div>

          <div class="form-group">
            <label for="password">密码</label>
            <input 
              id="password"
              v-model="formData.password" 
              type="password" 
              required
              placeholder="请输入密码"
            >
          </div>

          <div v-if="!isLogin" class="form-group">
            <label for="confirmPassword">确认密码</label>
            <input 
              id="confirmPassword"
              v-model="formData.confirmPassword" 
              type="password" 
              required
              placeholder="请再次输入密码"
            >
          </div>

          <button 
            type="submit" 
            class="auth-button"
            :disabled="loading"
          >
            {{ loading ? '处理中...' : (isLogin ? '登录' : '注册') }}
          </button>
        </form>

        <div v-if="error" class="error-message">
          {{ error }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores'
import { authAPI } from '@/services/api'

const router = useRouter()
const userStore = useUserStore()

const isLogin = ref(true)
const loading = ref(false)
const error = ref('')

const formData = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

async function handleSubmit() {
  error.value = ''
  
  // 表单验证
  if (!isLogin.value) {
    if (formData.password !== formData.confirmPassword) {
      error.value = '两次输入的密码不一致'
      return
    }
    
    if (formData.password.length < 6) {
      error.value = '密码长度至少6位'
      return
    }
  }

  try {
    loading.value = true
    
    if (isLogin.value) {
      // 登录
      const response = await authAPI.login({
        username: formData.username,
        password: formData.password
      })
      
      userStore.setUser(response.user)
      router.push('/')
    } else {
      // 注册
      const response = await authAPI.register({
        username: formData.username,
        email: formData.email,
        password: formData.password
      })
      
      userStore.setUser(response.user)
      router.push('/')
    }
  } catch (err) {
    console.error('认证失败:', err)
    error.value = err.message || '操作失败，请重试'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-lg);
}

.auth-container {
  width: 100%;
  max-width: 400px;
}

.auth-card {
  background: var(--bg-primary);
  border-radius: var(--radius-xl);
  padding: var(--spacing-2xl);
  box-shadow: var(--shadow-xl);
}

.auth-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.auth-header h1 {
  font-size: var(--text-3xl);
  color: var(--text-primary);
  margin-bottom: var(--spacing-sm);
}

.auth-header p {
  color: var(--text-secondary);
  font-size: var(--text-lg);
}

.auth-tabs {
  display: flex;
  margin-bottom: var(--spacing-xl);
  border-bottom: 1px solid var(--border-color);
}

.auth-tab {
  flex: 1;
  padding: var(--spacing-md);
  border: none;
  background: none;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: var(--text-base);
  font-weight: 500;
  border-bottom: 2px solid transparent;
  transition: all 0.2s ease;
}

.auth-tab:hover {
  color: var(--text-primary);
}

.auth-tab.active {
  color: var(--primary-color);
  border-bottom-color: var(--primary-color);
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.form-group label {
  font-weight: 600;
  color: var(--text-primary);
}

.form-group input {
  padding: var(--spacing-md);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  font-size: var(--text-base);
  transition: border-color 0.2s ease;
}

.form-group input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1);
}

.auth-button {
  padding: var(--spacing-md) var(--spacing-lg);
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--text-base);
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-top: var(--spacing-md);
}

.auth-button:hover:not(:disabled) {
  background: var(--primary-dark);
  transform: translateY(-1px);
}

.auth-button:disabled {
  background: var(--gray-300);
  cursor: not-allowed;
  transform: none;
}

.error-message {
  margin-top: var(--spacing-lg);
  padding: var(--spacing-md);
  background: #fef2f2;
  color: var(--error-color);
  border: 1px solid #fecaca;
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  text-align: center;
}

@media (max-width: 480px) {
  .auth-page {
    padding: var(--spacing-md);
  }
  
  .auth-card {
    padding: var(--spacing-xl);
  }
}
</style>
