<!-- 设置页面 -->
<template>
  <div class="settings-page">
    <div class="container container-sm">
      <div class="page-header">
        <h1>⚙️ 系统设置</h1>
        <p>配置你的个人信息</p>
      </div>

      <!-- 用户信息设置 -->
      <div class="settings-section card">
        <h3>👤 个人信息</h3>
        <div class="form-group">
          <label class="label">用户名</label>
          <input 
            v-model="userSettings.username" 
            type="text" 
            class="form-input"
            placeholder="请输入用户名"
          >
        </div>
        
        <div class="form-group">
          <label class="label">邮箱</label>
          <input 
            v-model="userSettings.email" 
            type="email" 
            class="form-input"
            placeholder="请输入邮箱地址"
          >
        </div>

        <div class="form-actions">
          <button class="btn btn-primary" @click="saveUserSettings">
            保存个人信息
          </button>
        </div>
      </div>

      <!-- 关于信息 -->
      <div class="settings-section card">
        <h3>ℹ️ 关于</h3>
        <div class="about-content">
          <div class="app-info">
            <h4>Oblivionis</h4>
            <p>记忆卡片学习系统</p>
            <p>版本: 1.0.0</p>
          </div>
          
          <div class="credits">
            <p>基于Vue 3 + FastAPI构建</p>
            <p>© 2025 Oblivionis项目</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { authAPI } from '@/services/api'

// 响应式数据
const userSettings = ref({
  username: '',
  email: ''
})

// 生命周期
onMounted(() => {
  loadSettings()
})

// 方法
async function loadSettings() {
  try {
    // 加载用户信息
    const user = await authAPI.getCurrentUser()
    if (user) {
      userSettings.value = {
        username: user.username || '',
        email: user.email || ''
      }
    }
  } catch (error) {
    console.error('加载设置失败:', error)
  }
}

async function saveUserSettings() {
  try {
    // 注意：后端目前没有提供用户信息更新API
    // 用户信息更新应该通过专门的用户管理流程处理
    console.log('用户信息更新功能暂未实现')
    alert('用户信息更新功能暂未实现，请联系管理员')
  } catch (error) {
    console.error('保存个人信息失败:', error)
    alert('保存失败，请重试')
  }
}
</script>

<style scoped>
.settings-page {
  padding: var(--spacing-xl) 0;
}

.page-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.page-header h1 {
  margin: 0 0 var(--spacing-sm) 0;
  color: var(--text-primary);
}

.page-header p {
  margin: 0;
  color: var(--text-secondary);
}

.settings-section {
  margin-bottom: var(--spacing-xl);
  padding: var(--spacing-xl);
}

.settings-section h3 {
  margin: 0 0 var(--spacing-lg) 0;
  color: var(--text-primary);
  border-bottom: 1px solid var(--border-color);
  padding-bottom: var(--spacing-md);
}

.form-group {
  margin-bottom: var(--spacing-lg);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
}

.about-content {
  text-align: center;
}

.app-info {
  margin-bottom: var(--spacing-lg);
}

.app-info h4 {
  margin: 0 0 var(--spacing-sm) 0;
  color: var(--primary-color);
  font-size: var(--text-xl);
}

.app-info p {
  margin: var(--spacing-xs) 0;
  color: var(--text-secondary);
}

.credits p {
  margin: var(--spacing-xs) 0;
  color: var(--text-tertiary);
  font-size: var(--text-sm);
}
</style>
