# 前后端数据流对接详解（面向后端开发者）

> **前提**：你熟悉 FastAPI + SQLAlchemy 后端，想理解前端如何与后端 API 对接。
> 本文以员工 CRUD 为例，用后端思维拆解前端的数据请求全链路。
>
> **代码规范**：本文所有「文件代码块」均为**完整、可直接保存运行**的版本（不是片段）。
> 拷贝到一个文件即可使用；被引用但未在本文件展开的文件，会注明其完整出处。

---

## 一、整体架构：Vue ↔ API 封装 ↔ FastAPI ↔ 数据库

```
vue-frontend/                         backend/
─────────────                         ────────

Employees.vue
  │
  ├─ fetchEmployees()
  │    └─ getEmployees()  ←─────────── src/api/index.js
  │                                      │
  │                              fetch('/api/employee')
  │                                      │
  │                              vite proxy: /api → http://127.0.0.1:8001
  │                                      │
  │         ─ ─ ─ HTTP ─ ─ ─ ─ ─ ─ ─ ─ ┘
  │                                      │
  │                              GET /employee  ← backend/main.py
  │                                      │
  │                              SELECT * FROM employee  ← SQLAlchemy
  │                                      │
  │         ←── JSON 数组 ──────────────┘
  │
  └─ employees.value = [...]
```

### 代理机制

在 `vue-frontend/vite.config.js` 中配置了 proxy。**以下是完整文件，可直接保存为
`vue-frontend/vite.config.js`：**

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

**效果**：

| 前端请求 | 经过代理后实际请求 | 命中的后端路由 |
|----------|-------------------|---------------|
| `fetch('/api/login')` | `http://127.0.0.1:8001/login` | `@app.post('/login')` |
| `fetch('/api/register')` | `http://127.0.0.1:8001/register` | `@app.post('/register')` |
| `fetch('/api/employee')` | `http://127.0.0.1:8001/employee` | `@app.get('/employee')` |
| `fetch('/api/employee/1001')` | `http://127.0.0.1:8001/employee/1001` | `@app.put('/employee/{emp_id}')` |

**为什么需要代理？** 前端跑在 `localhost:5173`，后端跑在 `localhost:8001`，属于**跨域**（不同端口）。浏览器默认禁止跨域请求。代理让你在开发环境下绕过跨域限制——前端以为在请求同源的 `/api/xxx`，实际被 vite 转发到后端。

> 类比：相当于 Nginx 的 `proxy_pass` 或 FastAPI 的 `Middleware`。

---

## 二、API 封装层详解

文件：`vue-frontend/src/api/index.js`

### 这个文件在前端的作用

`src/api/index.js` 是前端所有 HTTP 请求的**统一出口**。Vue 组件（如 `Employees.vue`）
不直接调用浏览器原生的 `fetch()`，而是调用这里封装好的 `getEmployees()`、
`updateEmployee()`、`deleteEmployee()` 等函数。

它的作用相当于后端的一个「HTTP 工具模块」：

| 职责 | 说明 | 后端类比 |
|------|------|---------|
| 统一前缀 | 所有请求自动加 `/api` | `BASE_URL = "http://..."` |
| 自动带 token | 有登录态就自动加 `Authorization` 头 | `requests` 的 `auth=` / 中间件 |
| 统一 401 处理 | token 失效自动清登录态并跳登录页 | FastAPI `Depends` 抛 401 后的处理 |
| 统一解析 | 统一 `res.json()` | `response.json()` |

### 完整代码（可直接保存运行）

```javascript
// vue-frontend/src/api/index.js
const BASE = '/api'

async function request(url, options = {}) {
  const token = localStorage.getItem('token')
  const headers = {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  }

  const res = await fetch(`${BASE}${url}`, { ...options, headers })
  const data = await res.json()

  if (res.status === 401) {
    localStorage.removeItem('token')
    localStorage.removeItem('userName')
    window.location.href = '/login'
  }

  return data
}

export function login(body) {
  return request('/login', { method: 'POST', body: JSON.stringify(body) })
}

export function register(body) {
  return request('/register', { method: 'POST', body: JSON.stringify(body) })
}

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

### 代码讲解（request 函数）

1. **取 token**：从 `localStorage` 读取登录时存的 `token`，没有则为 `null`。
2. **构造请求头**：有 token 就加 `Authorization: Bearer <token>`，没有就不加（如登录接口本身不需要）。`...options.headers` 允许单个请求额外追加头。
3. **发请求并解析**：`fetch(BASE + url)` 发送请求，`await res.json()` 解析 JSON 响应体。
4. **401 处理**：若后端返回 401（token 无效/过期），清除 `token` 和 `userName`，并跳回登录页。组件拿到的是已解析的 `data`，无需关心这些细节。

### 各 API 函数说明

| 函数 | 请求 | 对应后端路由 | 是否需要 token |
|------|------|-------------|---------------|
| `login(body)` | `POST /api/login` | `@app.post('/login')` | 否 |
| `register(body)` | `POST /api/register` | `@app.post('/register')` | 否 |
| `getEmployees()` | `GET /api/employee` | `@app.get('/employee')` | 否 |
| `updateEmployee(id, body)` | `PUT /api/employee/{id}` | `@app.put('/employee/{emp_id}')` | 是（自动带） |
| `deleteEmployee(id)` | `DELETE /api/employee/{id}` | `@app.delete('/employee/{emp_id}')` | 是（自动带） |

### `fetch()` ↔ Python HTTP 请求对比

| JS fetch | Python httpx | 说明 |
|----------|-------------|------|
| `fetch(url)` | `httpx.get(url)` | GET 请求 |
| `fetch(url, {method: 'POST', body: ...})` | `httpx.post(url, json=...)` | POST 请求 |
| `fetch(url, {method: 'PUT', body: ...})` | `httpx.put(url, json=...)` | PUT 请求 |
| `fetch(url, {method: 'DELETE'})` | `httpx.delete(url)` | DELETE 请求 |
| `await res.json()` | `response.json()` | 解析 JSON |

### Token 存储 ↔ Python session 对比

| 前端方案 | 后端类比 | 说明 |
|----------|---------|------|
| `localStorage.setItem('token', val)` | `session['token'] = val` | 存储登录凭证 |
| `localStorage.getItem('token')` | `session.get('token')` | 读取登录凭证 |
| `localStorage.removeItem('token')` | `session.pop('token')` | 删除登录凭证 |

`localStorage` 是浏览器提供的**持久化键值存储**（关闭浏览器也不丢失），相当于一个永不过期的简单 KV 数据库。

### 各 API 函数的 Python 等价写法（仅供对照理解）

```python
async def login(body: dict):
    return await request("/login", method="POST", json=body)

async def register(body: dict):
    return await request("/register", method="POST", json=body)

async def get_employees():
    return await request("/employee", method="GET")

async def update_employee(emp_id: int, body: dict):
    return await request(f"/employee/{emp_id}", method="PUT", json=body)

async def delete_employee(emp_id: int):
    return await request(f"/employee/{emp_id}", method="DELETE")
```

---

## 三、三大数据流详解

### 3.1 列表加载流程

```
用户打开 /employees 页面
    │
    ▼
onMounted(fetchEmployees)  ← 页面渲染完成后自动触发
    │
    ▼
fetchEmployees()
    ├─ loading.value = true          → 模板渲染「加载中...」
    │
    ├─ await getEmployees()          → JS fetch → GET /api/employee
    │                                      │
    │                              Vite Proxy 去掉 /api 前缀
    │                                      │
    │                              GET http://127.0.0.1:8001/employee
    │                                      │
    │                              @app.get('/employee')   ← main.py
    │                              async def get_employee():
    │                                async with AsyncSessionLocal() as session:
    │                                  result = await session.execute(select(Employee))
    │                                  employees = result.scalars().all()
    │                                  return [ {...}, ... ]   ← 裸数组！
    │                                      │
    │         ←── JSON 数组 ←─────────────┘
    │         [{"emp_id":1001,"emp_name":"张三",...}, ...]
    │
    ├─ if (Array.isArray(res))       → 判断是数组（不是 ApiResponse）
    │    employees.value = res       → 赋值给响应式变量
    │                                      │
    │                              v-for="emp in employees"  → 渲染每行
    │
    └─ loading.value = false         → 隐藏「加载中...」
```

**注意**：`GET /employee` 返回的是**裸数组**，不是 `{success, message, data}` 格式。这是因为 `response_model` 没有指定 Schema，直接返回了 list。所以前端用 `Array.isArray(res)` 判断。

### 3.2 编辑流程

```
用户点击「编辑」按钮
    │
    ▼
openEdit(emp)                       ← @click 触发
    ├─ editForm.value = {...emp}    → 浅拷贝员工数据
    │   (dept_id ?? '' 处理 NULL)
    ├─ showEdit.value = true        → v-if="showEdit" 显示弹窗
    └─ editError.value = ''         → 清空旧错误

用户修改表单字段
    │
    ▼
v-model 双向绑定 → editForm.value 实时更新

用户点击「保存」
    │
    ▼
handleUpdate()
    │
    ├─ saving.value = true          → :disabled="saving" 禁用按钮
    ├─ 构造 body = {emp_name, age, ...}
    │   ├─ 跳过空值（!== "" && !== undefined）
    │   └─ 类型转换：dept_id/age → Number, salary → Number
    │
    ├─ await updateEmployee(empId, body) → fetch → PUT /api/employee/{id}
    │                                      │
    │                              Authorization: Bearer <token>  ← 自动附带
    │                                      │
    │                              @app.put('/employee/{emp_id}')  ← main.py
    │                              async def update_employee(
    │                                  body: EmployeeUpdate,
    │                                  current_emp_id: int = Depends(get_current_emp)
    │                              ):
    │                                # current_emp_id = 当前登录用户（来自 token）
    │                                # SELECT * WHERE emp_id = ?  (路径里的 emp_id)
    │                                # setattr 逐字段更新（仅更新传来的字段）
    │                                # session.commit()
    │                                return ApiResponse(success=True, ...)
    │                                      │
    │         ←── {success: true, ...} ───┘
    │
    ├─ saving.value = false         → 解除按钮禁用
    │
    ├─ if (res.success)
    │    closeEdit()                → showEdit.value = false  关闭弹窗
    │    await fetchEmployees()     → 重新加载列表
    │
    └─ else
         editError.value = res.message  → 显示错误信息
```

**编辑请求体的构造逻辑**（以下片段属于 `Employees.vue` 的 `handleUpdate()` 函数，
完整文件见 `vue-employee-crud.md` 第四部分）：

```javascript
const body = {}
for (const key of ['emp_name', 'gender', 'age', 'department', 'dept_id', 'salary', 'hire_date']) {
  if (editForm.value[key] !== '' && editForm.value[key] !== undefined) {
    body[key] = key === 'dept_id' || key === 'age'
      ? Number(editForm.value[key])     // → int
      : key === 'salary'
        ? Number(editForm.value[key])   // → float
        : editForm.value[key]           // → string 原样
  }
}
```

**为什么这样做？** 对应后端的 `EmployeeUpdate` 模型（`backend/orm.py` 中定义）配合
`exclude_unset=True` 实现「只更新传来的字段」：

```python
# backend/orm.py  （完整可运行，与 ORM 模型同文件）
from pydantic import BaseModel
from enum import Enum

class GenderEnum(str, Enum):
    MALE = '男'
    FEMALE = '女'

class EmployeeUpdate(BaseModel):
    emp_name: str | None = None
    gender: GenderEnum | None = None
    age: int | None = None
    department: str | None = None
    salary: float | None = None
    hire_date: str | None = None
    password: str | None = None
    dept_id: int | None = None

# backend/main.py 中的更新接口
# update_data 只包含前端实际传来的字段
update_data = body.model_dump(exclude_unset=True)
for key, value in update_data.items():
    setattr(employee, key, value)
```

前端跳过空值 → 只传有值的字段 → 后端 `exclude_unset=True` 只更新这些字段 → 完美对接。

> 注意：`EmployeeUpdate` **定义在 `backend/orm.py`**，不是 `schemas.py`；
> `main.py` 通过 `from orm import EmployeeUpdate` 导入它。

### 3.3 删除流程

```
用户点击「删除」按钮
    │
    ▼
handleDelete(empId)
    │
    ├─ confirm("确定删除员工 #1001 吗？")
    │    └─ 用户点「取消」→ 直接 return，不执行后续
    │
    ├─ await deleteEmployee(empId) → fetch → DELETE /api/employee/{id}
    │                                      │
    │                              Authorization: Bearer <token>
    │                                      │
    │                              @app.delete('/employee/{emp_id}')  ← main.py
    │                              async def delete_employee(
    │                                  emp_id: int,
    │                                  _: int = Depends(get_current_emp)
    │                              ):
    │                                # SELECT * WHERE emp_id = ?
    │                                # session.delete(employee)
    │                                # session.commit()
    │                                return ApiResponse(success=True, ...)
    │                                      │
    │         ←── {success: true, ...} ───┘
    │
    ├─ if (res.success)
    │    await fetchEmployees()     → 重新加载列表（该行消失）
    │
    └─ else
         alert('删除失败：' + res.message)  → 浏览器弹窗提示
```

> ⚠️ **后端已知问题**：`main.py` 第 229 行当前写的是 `@app.delete('employee/{emp_id}')`
> （**缺少前导斜杠**），应改为 `@app.delete('/employee/{emp_id}')`。前端按 `/api/employee/{id}`
> 请求，代理后会变成 `/employee/{id}`，请在后端修正该路由定义。

---

## 四、Token 认证全链路

```
登录成功后
    │
    ▼
localStorage.setItem('token', res.data.token)
localStorage.setItem('userName', res.data.emp_name)   // ← 同时存用户名
    │
    ▼
后续所有需要认证的请求（PUT/DELETE）
    │
    ▼
api/index.js → request()
    ├─ const token = localStorage.getItem('token')
    └─ headers: { Authorization: `Bearer ${token}` }
        │
        ▼
HTTP Request → backend/main.py
    │
    ▼
Depends(get_current_emp) → auth.py
    ├─ 解析 Authorization header（HTTPBearer 提取 token）
    ├─ jwt.decode(token) → 验证签名和过期时间
    ├─ SELECT * FROM employee WHERE emp_id = ?
    ├─ 如果 token 无效或过期 → raise HTTPException(401)
    └─ return emp_id  ← 注入到路由参数
        │
        ▼
路由函数执行（已认证身份）
    │
    ▼
如果返回 401：
    ├─ localStorage.removeItem('token')  → 清除登录状态
    ├─ localStorage.removeItem('userName')
    └─ window.location.href = '/login'   → 跳转登录页
```

**对比 FastAPI 后端的 OAuth2 流程**（以下是 `backend/auth.py` 中可运行的核心片段）：

```python
# backend/auth.py  （可运行核心片段）
import os
from datetime import datetime, timedelta
from jose import jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, HTTPException

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = 'HS256'

security = HTTPBearer()

def verify_token(token: str):
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    return int(payload.get('sub'))

async def get_current_emp(credentials: HTTPAuthorizationCredentials = Depends(security)):
    emp_id = verify_token(credentials.credentials)
    if emp_id is None:
        raise HTTPException(status_code=401, detail='无效或者过期的 token')
    return emp_id
```

前端只需要做两件事：
1. 登录成功时把 `token`（以及 `userName`）存到 `localStorage`
2. 每次请求时从 `localStorage` 取出 `token` 放到 `Authorization` 头

---

## 五、路由守卫（认证拦截）

文件：`vue-frontend/src/router/index.js`

**以下是完整可运行文件**，可直接保存为 `vue-frontend/src/router/index.js`。
它依赖 `views/Login.vue`、`views/Register.vue`、`views/Employees.vue` 三个组件
（这三个组件分别见 `vue-login-guide.md` / `vue-register-guide.md` / `vue-employee-crud.md`）：

```javascript
// vue-frontend/src/router/index.js  —— 完整可运行文件
import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Employees from '../views/Employees.vue'

const routes = [
  { path: '/', redirect: '/employees' },
  { path: '/login', component: Login },
  { path: '/register', component: Register },
  { path: '/employees', component: Employees, meta: { requiresAuth: true } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) {
    next('/login')    // 未登录 → 强制跳转登录页
  } else {
    next()            // 放行
  }
})

export default router
```

> 注意：路由文件写好后，还需在 `src/main.js` 中挂载它：
> `import router from './router'` 并 `createApp(App).use(router).mount('#app')`，
> 否则 `beforeEach` 守卫不会生效。

**Python 类比**：

```python
# 相当于 FastAPI 中间件
@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    if request.url.path == "/employees" and "token" not in request.cookies:
        return RedirectResponse("/login")
    return await call_next(request)
```

| 前端方案 | 后端方案 | 说明 |
|----------|---------|------|
| `router.beforeEach` | Middleware / Depends | 拦截路由访问 |
| `to.meta.requiresAuth` | 路由上的 Depends 标记 | 标记需要认证的路由 |
| `next('/login')` | `RedirectResponse` | 重定向到登录页 |
| `localStorage.getItem('token')` | 检查 Cookie/Session | 判断登录状态 |

---

## 六、关键对接点总结

| # | 对接点 | 前端位置 | 后端位置 | 注意事项 |
|---|--------|---------|---------|---------|
| 1 | 列表加载 | `onMounted` → `fetchEmployees()` | `@app.get('/employee')` | 返回裸数组，不是 ApiResponse |
| 2 | Token 注入 | `api/index.js` → `request()` | `Depends(get_current_emp)` | PUT/DELETE 自动带 Authorization |
| 3 | 编辑只发有值字段 | `handleUpdate()` 构造 body | `exclude_unset=True` | 前端跳过空值，后端只更新传了的字段 |
| 4 | 类型转换 | `handleUpdate()` `Number()` | Pydantic 自动转换 | age/dept_id→int, salary→float |
| 5 | 删除确认 | `handleDelete()` `confirm()` | 无 | 前端二次确认，防止误删 |
| 6 | 列表刷新 | `fetchEmployees()` | 无 | 编辑/删除成功后重新加载 |
| 7 | 401 处理 | `api/index.js` `res.status === 401` | `HTTPException(401)` | token 过期自动跳转登录 |
| 8 | 路由守卫 | `router.beforeEach` | `Depends` | 未登录拦截 |
| 9 | NULL 处理 | `dept_id ?? ''` | 数据库 NULL | 防止 input 显示 null 字样 |

---

## 七、常见踩坑点

### 1. GET /employee 返回裸数组

```python
# backend/main.py
@app.get('/employee')
async def get_employee():
    return [ {...}, ... ]  # ← 直接 return list，不是 ApiResponse
```

**前端必须特殊处理**：

```javascript
if (Array.isArray(res)) {   // ← 不能用 res.success
    employees.value = res
}
```

### 2. 响应式变量的 .value

```javascript
// ❌ 错误：在 script 中忘记 .value
employees = res          // 不会触发页面更新！
loading = false          // 不会触发页面更新！

// ✅ 正确
employees.value = res    // 触发页面更新
loading.value = false    // 触发页面更新
```

### 3. HTML input 值始终是字符串

```javascript
// 用户输入 "28" → editForm.age = "28" (字符串，不是数字)
// 需要手动转换：
body[key] = Number(editForm.value[key])  // → 28 (数字)
```

### 4. async/await 必须配套

```javascript
// ❌ 忘记 await
const res = getEmployees()    // res 是 Promise 对象，不是数据
employees.value = res         // 拿到的是 Promise，不是数组

// ✅ 正确
const res = await getEmployees()
if (Array.isArray(res)) {
    employees.value = res
}
```

这和 Python 的 async/await 完全一样：不 await 拿到的是 coroutine，不是返回值。
