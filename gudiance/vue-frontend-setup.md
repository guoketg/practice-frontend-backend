# Vue 前端项目搭建指导

## 前置条件

- Node.js ≥ 18
- 后端 FastAPI 项目已能正常运行（`backend/main.py` 端口 8001）

---

## 步骤一：创建 Vue 项目

在项目根目录 `f:/code/MyPython/tiny-frontend/` 下执行：

```powershell
npm create vite@latest vue-frontend -- --template vue
cd vue-frontend
npm install
npm install vue-router@4
```

创建后目录结构：

```
vue-frontend/
├── index.html
├── package.json
├── vite.config.js
├── src/
│   ├── main.js
│   ├── App.vue
│   ├── style.css
│   ├── api/
│   │   └── index.js          ← 新建
│   ├── router/
│   │   └── index.js          ← 新建
│   └── views/
│       ├── Login.vue          ← 新建
│       ├── Register.vue       ← 新建
│       └── Employees.vue      ← 新建
```

---

## 步骤二：修改 `vite.config.js` — 配置代理

```js
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})
```

**作用**：前端请求 `/api/login` → Vite 自动转发到 `http://127.0.0.1:8001/login`，避免跨域和 CORS 问题。

---

## 步骤三：修改 `src/main.js` — 挂载路由

```js
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import './style.css'

createApp(App).use(router).mount('#app')
```

---

## 步骤四：新建 `src/router/index.js` — 路由配置

```js
import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Employees from '../views/Employees.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', name: 'Login', component: Login },
  { path: '/register', name: 'Register', component: Register },
  { path: '/employees', name: 'Employees', component: Employees, meta: { requiresAuth: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 路由守卫：未登录自动跳转登录页
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router
```

---

## 步骤五：新建 `src/api/index.js` — 所有后端 API 调用封装

```js
const BASE = '/api'

// 通用请求函数
async function request(url, options = {}) {
  const token = localStorage.getItem('token')
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  }

  const res = await fetch(`${BASE}${url}`, { ...options, headers })
  const data = await res.json()

  // 如果后端返回 401（token 过期），清除登录状态并跳转
  if (res.status === 401) {
    localStorage.removeItem('token')
    localStorage.removeItem('userName')
    window.location.href = '/login'
    return null
  }

  return data
}

// ========== 注册 / 登录 ==========
export function register(body) {
  return request('/register', { method: 'POST', body: JSON.stringify(body) })
}

export function login(body) {
  return request('/login', { method: 'POST', body: JSON.stringify(body) })
}

// ========== 员工 CRUD ==========
export function getEmployees() {
  return request('/employee', { method: 'GET' })
}

export function updateEmployee(empId, body) {
  return request(`/employee/${empId}`, { method: 'PUT', body: JSON.stringify(body) })
}

export function deleteEmployee(empId) {
  return request(`/employee/${empId}`, { method: 'DELETE' })
}
```

**设计要点**：
- 统一请求前缀 `/api`（由 Vite proxy 转发到后端）
- 自动注入 `Authorization: Bearer <token>` 头
- 401 自动清理登录态并跳转
- 所有 API 函数签名简洁，组件调用时只需传业务参数

---

## 步骤六：替换 `src/App.vue` — 根组件

```vue
<template>
  <div id="app-container">
    <header v-if="isLoggedIn" class="top-bar">
      <span>欢迎，{{ userName }}</span>
      <button class="btn-sm" @click="logout">退出登录</button>
    </header>
    <main>
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()
const isLoggedIn = ref(!!localStorage.getItem('token'))
const userName = ref(localStorage.getItem('userName') || '')

watch(
  () => route.path,
  () => {
    isLoggedIn.value = !!localStorage.getItem('token')
    userName.value = localStorage.getItem('userName') || ''
  }
)

function logout() {
  localStorage.removeItem('token')
  localStorage.removeItem('userName')
  isLoggedIn.value = false
  router.push('/login')
}
</script>
```

---

## 步骤七：替换 `src/style.css` — 全局样式

```css
:root {
  --primary: #4f46e5;
  --danger: #dc2626;
  --text: #1f2937;
  --text-light: #6b7280;
  --bg: #f9fafb;
  --card-bg: #fff;
  --border: #e5e7eb;
  --radius: 8px;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: system-ui, -apple-system, sans-serif;
  background: var(--bg);
  color: var(--text);
}

#app-container { min-height: 100vh; }

/* 顶部栏 */
.top-bar {
  display: flex; justify-content: flex-end; align-items: center; gap: 16px;
  padding: 12px 24px; background: var(--card-bg);
  border-bottom: 1px solid var(--border); font-size: 14px;
}

/* 表单页面（登录/注册共用） */
.form-page {
  max-width: 420px; margin: 80px auto 0; padding: 32px;
  background: var(--card-bg); border-radius: var(--radius);
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}
.form-page h2 { margin-bottom: 24px; text-align: center; }
.form-page label { display: block; margin-top: 12px; margin-bottom: 4px; font-size: 14px; font-weight: 500; }
.form-page input, .form-page select {
  width: 100%; padding: 10px 12px; border: 1px solid var(--border);
  border-radius: 6px; font-size: 14px; outline: none; transition: border-color 0.2s;
}
.form-page input:focus, .form-page select:focus { border-color: var(--primary); }
.form-page button {
  width: 100%; margin-top: 20px; padding: 10px;
  background: var(--primary); color: #fff; border: none;
  border-radius: 6px; font-size: 15px; cursor: pointer;
}
.form-page button:disabled { opacity: 0.6; cursor: not-allowed; }
.form-page button:hover:not(:disabled) { opacity: 0.9; }
.error { color: var(--danger); font-size: 14px; margin-top: 12px; }
.success { color: #16a34a; font-size: 14px; margin-top: 12px; }
.switch { text-align: center; margin-top: 16px; font-size: 14px; color: var(--text-light); }
.switch a { color: var(--primary); text-decoration: none; }

/* 员工列表页 */
.employees-page { max-width: 1100px; margin: 40px auto; padding: 0 24px; }
.employees-page h2 { margin-bottom: 20px; }
.loading { text-align: center; color: var(--text-light); padding: 40px; }

table {
  width: 100%; border-collapse: collapse; background: var(--card-bg);
  border-radius: var(--radius); overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.08);
}
th, td { padding: 12px 16px; text-align: left; font-size: 14px; border-bottom: 1px solid var(--border); }
th { background: #f3f4f6; font-weight: 600; }
.actions { display: flex; gap: 8px; }

button { cursor: pointer; }
.btn-sm {
  padding: 4px 12px; font-size: 13px; border: 1px solid var(--border);
  border-radius: 4px; background: var(--card-bg); color: var(--text);
}
.btn-sm:hover { background: #f3f4f6; }
.btn-danger { color: var(--danger); border-color: var(--danger); }
.btn-danger:hover { background: #fef2f2; }
.btn-cancel { padding: 8px 16px; border: 1px solid var(--border); border-radius: 6px; background: #fff; font-size: 14px; }

/* 编辑弹窗 */
.modal-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,0.4);
  display: flex; justify-content: center; align-items: center; z-index: 100;
}
.modal {
  background: var(--card-bg); border-radius: var(--radius); padding: 28px;
  width: 460px; max-height: 90vh; overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0,0,0,0.15);
}
.modal h3 { margin-bottom: 16px; }
.modal label { display: block; margin-top: 10px; margin-bottom: 4px; font-size: 13px; font-weight: 500; }
.modal input, .modal select {
  width: 100%; padding: 8px 10px; border: 1px solid var(--border);
  border-radius: 5px; font-size: 14px; outline: none;
}
.modal input:focus, .modal select:focus { border-color: var(--primary); }
.modal-btns { display: flex; gap: 10px; margin-top: 18px; }
.modal-btns button[type='submit'] {
  flex: 1; padding: 8px; background: var(--primary); color: #fff;
  border: none; border-radius: 6px; font-size: 14px;
}
.modal-btns button[type='submit']:disabled { opacity: 0.6; }
```

---

## 数据流架构总览

```
┌─────────────────────────────────────────────────────────┐
│  Vue 前端 (localhost:5173)                               │
│                                                         │
│  src/api/index.js          ← 统一 fetch 封装            │
│  ├── register(body)        → POST /api/register         │
│  ├── login(body)           → POST /api/login            │
│  ├── getEmployees()        → GET  /api/employee         │
│  ├── updateEmployee(id,b)  → PUT  /api/employee/{id}    │
│  └── deleteEmployee(id)    → DELETE /api/employee/{id}  │
│                                                         │
│  Vite Proxy: /api → http://127.0.0.1:8001              │
└─────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│  FastAPI 后端 (localhost:8001)                          │
│                                                         │
│  auth.py: JWT + bcrypt 密码加密                         │
│  ├── hash_password()                                    │
│  ├── verify_password()                                  │
│  ├── create_access_token()                              │
│  └── get_current_emp()  ← Depends 依赖注入              │
│                                                         │
│  main.py: 路由接口                                      │
│  ├── POST /login      → ApiResponse + token             │
│  ├── POST /register   → ApiResponse                     │
│  ├── GET  /employee   → 数组（无需 token）               │
│  ├── PUT  /employee/{id} → ApiResponse（需 token）       │
│  └── DELETE /employee/{id} → ApiResponse（需 token）     │
└─────────────────────────────────────────────────────────┘
```

---

## 启动方式

```powershell
# 终端1：启动后端（端口 8001）
cd backend
python main.py

# 终端2：启动前端（端口 5173）
cd vue-frontend
npm run dev
```

浏览器打开 `http://localhost:5173`，自动跳转到登录页。
