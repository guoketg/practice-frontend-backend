# 登录功能前后端对接指导

## 一、后端现状

### 当前代码（`backend/main.py` 第 116-135 行）

```python
@app.post('/login', response_model=ApiResponse)
async def login(body: LoginRequest):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Employee).where(Employee.emp_id == body.emp_id))
        employee = result.scalar_one_or_none()

        if not employee:
            return ApiResponse(success=False, message='员工不存在')

        if employee.password != body.password:          # ← ⚠️ 明文对比
            return ApiResponse(success=False, message='密码错误')

        token = create_access_token(employee.emp_id)
        return ApiResponse(success=True, message='登录成功', data={
            'emp_id': employee.emp_id,
            'emp_name': employee.emp_name,
            'token': token
        })
```

### ⚠️ 存在一个 Bug：密码明文对比

**问题**：第 127 行 `employee.password != body.password` 是用明文对比。

注册时已经用 `hash_password()` 哈希存储了密码，所以数据库中 `password` 字段存的是 bcrypt 哈希值（如 `$2b$12$...`），而前端传的是明文 `"123456"`。**明文对比永远匹配不上**。

### 🔧 修复

**编辑文件 `backend/main.py` 第 127 行**：

```python
# 修改前
        if employee.password != body.password:

# 修改后
        if not verify_password(body.password, employee.password):
```

`verify_password` 已从 `auth.py` 导入（第 11 行），无需额外 import。

---

## 二、后端接口规格

### 请求

```
POST /login
Content-Type: application/json
```

```json
{
    "emp_id": 1001,
    "password": "123456"
}
```

### 成功响应

```json
{
    "success": true,
    "message": "登录成功",
    "data": {
        "emp_id": 1001,
        "emp_name": "张三",
        "token": "eyJhbGciOiJIUzI1NiIs..."
    }
}
```

`token` 是 JWT，有效期 60 分钟。

### 失败响应

```json
{ "success": false, "message": "员工不存在", "data": null }
{ "success": false, "message": "密码错误", "data": null }
```

---

## 三、前端代码

### 文件：`vue-frontend/src/views/Login.vue`

```vue
<template>
  <div class="form-page">
    <h2>员工登录</h2>
    <form @submit.prevent="handleLogin">
      <label>员工 ID</label>
      <input v-model="form.emp_id" type="number" required />

      <label>密码</label>
      <input v-model="form.password" type="password" required />

      <button type="submit" :disabled="loading">
        {{ loading ? '登录中...' : '登录' }}
      </button>

      <p v-if="error" class="error">{{ error }}</p>
    </form>
    <p class="switch">
      还没有账号？<router-link to="/register">去注册</router-link>
    </p>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { login } from '../api'

const router = useRouter()
const form = reactive({ emp_id: '', password: '' })
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  loading.value = true
  error.value = ''

  const res = await login({
    emp_id: Number(form.emp_id),
    password: form.password,
  })

  loading.value = false

  if (res.success) {
    // 登录成功：存储 token + 用户名到 localStorage
    localStorage.setItem('token', res.data.token)
    localStorage.setItem('userName', res.data.emp_name)
    // 跳转到员工管理页
    router.push('/employees')
  } else {
    error.value = res.message
  }
}
</script>
```

---

## 四、前后端数据流对接

```
┌──────────────────┐         ┌──────────────────┐
│  Login.vue       │         │  FastAPI         │
│                  │         │  backend/main.py  │
├──────────────────┤         ├──────────────────┤
│ 1. 用户输入       │         │                  │
│    emp_id + pwd  │         │                  │
│                  │         │                  │
│ 2. handleLogin   │  POST   │                  │
│    ↓             │──────→ │ /login            │
│ 3. login(body)   │ /api/   │                  │
│    (api/index.js)│ (proxy) │                  │
│                  │         │                  │
│                  │         │ 4. SELECT WHERE   │
│                  │         │    emp_id = ?     │
│                  │         │    ↓              │
│                  │         │ 5. 员工不存在      │
│                  │         │    → false 响应    │
│                  │         │    ↓              │
│                  │         │ 6. verify_password│
│                  │         │    ↓              │
│    ←─────────────│         │ 7. 密码错误        │
│ 10. 解析 JSON    │         │    → false 响应    │
│    ↓             │         │    ↓              │
│ 11. res.success? │         │ 8. create_access_ │
│   T → 存 token   │         │    token(emp_id)  │
│       跳转员工页  │         │    ↓              │
│   F → 显示错误   │         │ 9. return succ +  │
│                  │         │    token          │
└──────────────────┘         └──────────────────┘
```

### 关键对接点

| 步骤 | 位置 | 说明 |
|------|------|------|
| **Token 存储** | `handleLogin()` | `localStorage.setItem('token', ...)` — 后续所有需认证的请求都会读取此值 |
| **Token 使用** | `src/api/index.js` `request()` | `Authorization: Bearer ${token}` 自动注入请求头 |
| **路由跳转** | `handleLogin()` | `router.push('/employees')` 登录后进入员工管理页 |
| **路由守卫** | `src/router/index.js` `beforeEach` | 没有 token 无法访问 `/employees`，自动跳回 `/login` |
| **Token 过期** | `src/api/index.js` | HTTP 401 → 清除 token → 跳转登录页 |
| **密码验证** | 后端 `verify_password()` | bcrypt 对比，前端只传明文即可 |

---

## 五、JWT Token 串起整个认证流程

```
注册                          登录                         后续操作
─────                        ─────                       ────────
POST /register               POST /login                 PUT /employee/1001
  │                            │                          │
  ├── hash_password(pwd)       ├── verify_password()      ├── Depends(get_current_emp)
  ├── INSERT INTO employee     ├── create_access_token()  │   │
  └── 返回 emp_id              └── 返回 token             │   ├── 从 Header 取 Bearer token
                                   │                      │   ├── jwt.decode() 解析
              前端存储 token ←────────┘                    │   ├── 验证签名 + 过期时间
              到 localStorage                              │   └── 返回 emp_id → 继续业务
                                    │                      │
                                    后续请求自动带 token ────┘
```

---

## ⚠️ 注意事项

1. **必须先修复密码对比 Bug**：不修复则登录永远失败。
2. **注册时已 hash 存储**：如果是旧数据（明文存储的密码），需重新注册或用 SQL 更新密码为 hash 值。
3. **Token 60 分钟过期**：过期后前端自动 401 跳转登录页。
4. **logout**：清除 `localStorage` 中的 token 和 userName 即可。
