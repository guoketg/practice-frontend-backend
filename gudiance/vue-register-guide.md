# 注册功能前后端对接指导

## 一、后端现状

### 当前代码（`backend/main.py` 第 137-158 行）

```python
@app.post('/register', response_model=ApiResponse)
async def register(body: RegisterRequest):

    async with AsyncSessionLocal() as session:
        result_emp_id = await session.execute(
            select(Employee).where(body.emp_id == Employee.emp_id)
        )
        emp_id = result_emp_id.scalar_one_or_none()

        if emp_id:
            return ApiResponse(success=False, message='id已存在')

        employee_dict = body.model_dump()
        employee_dict['password'] = hash_password(employee_dict['password'])
        employee = Employee(**employee_dict)

        session.add(employee)
        try:
            await session.commit()
        except Exception:
            await session.rollback()
            return ApiResponse(success=False, message='注册失败，请检查参数，如dept_id等')

        return ApiResponse(success=True, message='注册成功', data={
            'emp_name': employee.emp_name, 'emp_id': employee.emp_id
        })
```

### ✅ 已正确的部分

| 项目 | 说明 |
|------|------|
| 密码哈希 | `hash_password()` 已调用 |
| ApiResponse 格式 | 已使用统一响应 |
| 重复 ID 检查 | 按 `emp_id` 查重 |
| 异常回滚 | `try/except/rollback` 已处理 |

### ⚠️ 无需修改

之前的版本中注册接口有 `Depends(get_current_emp)` 导致「必须先登录才能注册」，当前版本已修复，无需改动。

---

## 二、后端接口规格

### 请求

```
POST /register
Content-Type: application/json
```

```json
{
    "emp_id": 1001,
    "emp_name": "张三",
    "password": "123456",
    "gender": "男",
    "age": 28,
    "department": "技术部",
    "dept_id": 1,
    "salary": 8000.00,
    "hire_date": "2024-07-01"
}
```

| 字段 | 类型 | 必须 | 说明 |
|------|------|------|------|
| emp_id | int | ✅ | 员工编号（手动指定） |
| emp_name | str | ✅ | 员工姓名 |
| password | str | ✅ | 登录密码 |
| gender | str | ✅ | 性别，值必须为 `"男"` 或 `"女"` |
| age | int | ✅ | 年龄 |
| department | str | ✅ | 部门名称 |
| dept_id | int | ✅ | 外键，必须存在于 department 表 |
| salary | float | ✅ | 薪资 |
| hire_date | str | ✅ | 入职日期，格式 `YYYY-MM-DD` |

### 成功响应

```json
{
    "success": true,
    "message": "注册成功",
    "data": {
        "emp_id": 1001,
        "emp_name": "张三"
    }
}
```

### 失败响应

```json
// ID 已存在
{ "success": false, "message": "id已存在", "data": null }

// 参数错误（如 dept_id 不存在）
{ "success": false, "message": "注册失败，请检查参数，如dept_id等", "data": null }
```

---

## 三、前端代码

### 文件：`vue-frontend/src/views/Register.vue`

**这个文件在前端的作用**：`Register.vue` 是注册页面，负责收集新员工的所有字段，调用 `register()` 发送注册请求；成功后显示提示。它对应后端 `@app.post('/register')` 的前端入口。

```vue
<template>
  <div class="form-page">
    <h2>员工注册</h2>
    <form @submit.prevent="handleRegister">
      <label>员工 ID</label>
      <input v-model="form.emp_id" type="number" required />

      <label>姓名</label>
      <input v-model="form.emp_name" required />

      <label>密码</label>
      <input v-model="form.password" type="password" required />

      <label>性别</label>
      <select v-model="form.gender" required>
        <option value="">请选择</option>
        <option value="男">男</option>
        <option value="女">女</option>
      </select>

      <label>年龄</label>
      <input v-model="form.age" type="number" required />

      <label>部门名称</label>
      <input v-model="form.department" required />

      <label>部门 ID</label>
      <input v-model="form.dept_id" type="number" required />

      <label>薪资</label>
      <input v-model="form.salary" type="number" step="0.01" required />

      <label>入职日期</label>
      <input v-model="form.hire_date" type="date" required />

      <button type="submit" :disabled="loading">
        {{ loading ? '注册中...' : '注册' }}
      </button>

      <p v-if="error" class="error">{{ error }}</p>
      <p v-if="success" class="success">{{ success }}</p>
    </form>
    <p class="switch">
      已有账号？<router-link to="/login">去登录</router-link>
    </p>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { register } from '../api'

const form = reactive({
  emp_id: '',
  emp_name: '',
  password: '',
  gender: '',
  age: '',
  department: '',
  dept_id: '',
  salary: '',
  hire_date: '',
})

const loading = ref(false)
const error = ref('')
const success = ref('')

async function handleRegister() {
  loading.value = true
  error.value = ''
  success.value = ''

  const body = {
    emp_id: Number(form.emp_id),
    emp_name: form.emp_name,
    password: form.password,
    gender: form.gender,
    age: Number(form.age),
    department: form.department,
    dept_id: Number(form.dept_id),
    salary: Number(form.salary),
    hire_date: form.hire_date,
  }

  const res = await register(body)
  loading.value = false

  if (res.success) {
    success.value = `注册成功！员工 ${res.data.emp_name} (ID: ${res.data.emp_id})`
    Object.keys(form).forEach((k) => (form[k] = ''))
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
│  Register.vue    │         │  FastAPI         │
│                  │         │  backend/main.py  │
├──────────────────┤         ├──────────────────┤
│ 1. 用户填表      │         │                  │
│                  │         │                  │
│ 2. handleRegister│  POST   │                  │
│    ↓             │──────→ │ /register        │
│ 3. register(body)│ /api/   │                  │
│    (api/index.js)│ (proxy) │                  │
│                  │         │                  │
│ 4. 自动加头:     │         │ 5. 接收 body     │
│    Content-Type  │         │    ↓             │
│    (注册无需      │         │ 6. 查重 emp_id   │
│     token)       │         │    ↓             │
│                  │         │ 7. hash_password │
│    ←─────────────│         │    ↓             │
│ 9. 解析 JSON     │         │ 8. 插入数据库    │
│    ↓             │         │                  │
│ 10. res.success? │         │ return ApiResponse│
│     T→ 显示成功  │         │                  │
│     F→ 显示错误  │         │                  │
└──────────────────┘         └──────────────────┘
```

### 关键对接点

| 步骤 | 位置 | 说明 |
|------|------|------|
| 表单 v-model | `Register.vue` template | 双向绑定，收集用户输入 |
| 类型转换 | `handleRegister()` 第 423-433 行 | `emp_id`、`age`、`dept_id`、`salary` 从字符串转数字 |
| API 调用 | `src/api/index.js` `register()` | `POST /api/register` → proxy → `POST /register` |
| 响应解析 | `handleRegister()` 第 438 行 | `res.success` 判断：true → 显示成功 / false → 显示错误 |
| 密码处理 | 后端 `main.py` 第 148 行 | `hash_password()` 自动哈希，前端无需处理 |

---

## ⚠️ 注意事项

1. **dept_id 必须存在**：注册前确保 `department` 表已有数据。可先调用 `POST /departments` 创建部门。
2. **密码不返回**：后端响应不包含密码字段（安全）。
3. **注册不返回 token**：注册后需手动跳转到登录页使用刚注册的账号登录。
4. **emp_id 手动指定**：当前 emp_id 由用户输入，生产环境建议 autoincrement。
