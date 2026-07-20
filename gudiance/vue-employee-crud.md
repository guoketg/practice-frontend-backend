# 员工管理（列表/编辑/删除）前后端对接指导

## 一、后端现状

### 已有接口

| 方法 | 路径 | 认证 | 功能 | 行号 |
|------|------|------|------|------|
| GET | `/employee` | 无需 | 获取所有员工列表 | 77-91 |
| PUT | `/employee/{emp_id}` | ✅ 需要 | 更新员工信息 | 161-180 |

### ⚠️ 缺少 DELETE 接口

后端目前没有删除员工的接口，需要在 `backend/main.py` 中添加。

---

## 二、需要修复/新增的后端代码

### 新增 1：DELETE 接口

**新增代码** `backend/main.py`：在 `if __name__` 之前（第 228 行之前）插入：

```python
@app.delete('/employee/{emp_id}', response_model=ApiResponse)
async def delete_employee(emp_id: int, _: int = Depends(get_current_emp)):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Employee).where(Employee.emp_id == emp_id)
        )
        employee = result.scalar_one_or_none()

        if not employee:
            return ApiResponse(success=False, message='员工不存在')

        await session.delete(employee)
        await session.commit()

        return ApiResponse(success=True, message='删除成功', data={
            'emp_id': emp_id
        })
```

### 修复 2：编辑接口的自编辑权限问题

当前代码（第 161-180 行）的逻辑是：

```python
@app.put('/employee/{emp_id}', response_model=ApiResponse)
async def update_employee(body: EmployeeUpdate, emp_id: int = Depends(get_current_emp)):
    # ...
    result = await session.execute(select(Employee).where(Employee.emp_id == emp_id))
    # emp_id 来自 Depends(get_current_emp)，即登录者自己的 ID
```

**问题**：`emp_id` 同时作为路径参数和 `Depends` 的参数，FastAPI 会用路径参数覆盖 `Depends` 的返回值。这意味着**任何登录用户都能编辑任何员工**（因为路径中的 `emp_id` 会覆盖 token 中的身份）。

如果需要限制为「只能编辑自己」，应改为如下逻辑（可选修复）：

```python
@app.put('/employee/{emp_id}', response_model=ApiResponse)
async def update_employee(
    emp_id: int,                          # 路径参数：要编辑的员工 id
    body: EmployeeUpdate,
    current_emp: int = Depends(get_current_emp)   # Token 身份
):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Employee).where(Employee.emp_id == emp_id)
        )
        employee = result.scalar_one_or_none()

        if not employee:
            return ApiResponse(success=False, message='员工不存在')

        # 可选：限制只能编辑自己
        # if emp_id != current_emp:
        #     return ApiResponse(success=False, message='只能编辑自己的信息')

        update_data = body.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(employee, key, value)

        await session.commit()
        await session.refresh(employee)

        return ApiResponse(success=True, message='更新成功', data={
            'emp_id': employee.emp_id, 'emp_name': employee.emp_name
        })
```

> 当前项目为学习用途，暂不强制限制。上面代码给出了可选约束注释。

---

## 三、后端接口规格

### 获取员工列表

```
GET /employee
无需 Token
```

返回：

```json
[
    {
        "emp_id": 1001,
        "emp_name": "张三",
        "gender": "男",
        "age": 28,
        "department": "技术部",
        "salary": 8000.00,
        "hire_date": "2024-07-01"
    }
]
```

**注意**：这个接口返回的是**裸数组**，不是 `ApiResponse` 格式。前端需要特殊处理。

### 更新员工

```
PUT /employee/{emp_id}
Authorization: Bearer <token>
Content-Type: application/json
```

请求体（所有字段可选，只传要更新的字段）：

```json
{
    "emp_name": "张三三",
    "salary": 9000.00
}
```

成功响应：

```json
{
    "success": true,
    "message": "更新成功",
    "data": { "emp_id": 1001, "emp_name": "张三三" }
}
```

### 删除员工

```
DELETE /employee/{emp_id}
Authorization: Bearer <token>
```

成功响应：

```json
{
    "success": true,
    "message": "删除成功",
    "data": { "emp_id": 1001 }
}
```

---

## 四、前端代码

> 📘 逐行讲解见专题文档 **[vue-employee-list-explained.md](./vue-employee-list-explained.md)**——
> 用后端类比的方式解释每个 Vue 概念（`ref()`、`v-for`、`v-if`、`v-model`、`@click`、`onMounted` 等）。

### 文件：`vue-frontend/src/views/Employees.vue`

```vue
<template>
  <div class="employees-page">
    <h2>员工管理</h2>

    <div v-if="loading" class="loading">加载中...</div>

    <table v-else-if="employees.length > 0">
      <thead>
        <tr>
          <th>ID</th>
          <th>姓名</th>
          <th>性别</th>
          <th>年龄</th>
          <th>部门</th>
          <th>薪资</th>
          <th>入职日期</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="emp in employees" :key="emp.emp_id">
          <td>{{ emp.emp_id }}</td>
          <td>{{ emp.emp_name }}</td>
          <td>{{ emp.gender }}</td>
          <td>{{ emp.age }}</td>
          <td>{{ emp.department }}</td>
          <td>{{ emp.salary }}</td>
          <td>{{ emp.hire_date }}</td>
          <td class="actions">
            <button class="btn-sm" @click="openEdit(emp)">编辑</button>
            <button class="btn-sm btn-danger" @click="handleDelete(emp.emp_id)">删除</button>
          </td>
        </tr>
      </tbody>
    </table>

    <p v-else>暂无员工数据</p>

    <!-- ====== 编辑弹窗 ====== -->
    <div v-if="showEdit" class="modal-overlay" @click.self="closeEdit">
      <div class="modal">
        <h3>编辑员工 #{{ editForm.emp_id }}</h3>
        <form @submit.prevent="handleUpdate">
          <label>姓名</label>
          <input v-model="editForm.emp_name" />

          <label>性别</label>
          <select v-model="editForm.gender">
            <option value="男">男</option>
            <option value="女">女</option>
          </select>

          <label>年龄</label>
          <input v-model.number="editForm.age" type="number" />

          <label>部门名称</label>
          <input v-model="editForm.department" />

          <label>部门 ID</label>
          <input v-model.number="editForm.dept_id" type="number" />

          <label>薪资</label>
          <input v-model.number="editForm.salary" type="number" step="0.01" />

          <label>入职日期</label>
          <input v-model="editForm.hire_date" type="date" />

          <div class="modal-btns">
            <button type="submit" :disabled="saving">
              {{ saving ? '保存中...' : '保存' }}
            </button>
            <button type="button" class="btn-cancel" @click="closeEdit">取消</button>
          </div>
          <p v-if="editError" class="error">{{ editError }}</p>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getEmployees, updateEmployee, deleteEmployee } from '../api'

const employees = ref([])
const loading = ref(true)

// ====== 加载列表 ======
async function fetchEmployees() {
  loading.value = true
  const res = await getEmployees()
  if (Array.isArray(res)) {
    employees.value = res
  }
  loading.value = false
}

onMounted(fetchEmployees)

// ====== 编辑 ======
const showEdit = ref(false)
const saving = ref(false)
const editError = ref('')
const editForm = ref({})

function openEdit(emp) {
  editForm.value = {
    emp_id: emp.emp_id,
    emp_name: emp.emp_name,
    gender: emp.gender,
    age: emp.age,
    department: emp.department,
    dept_id: emp.dept_id ?? '',
    salary: emp.salary,
    hire_date: emp.hire_date,
  }
  showEdit.value = true
  editError.value = ''
}

function closeEdit() {
  showEdit.value = false
}

async function handleUpdate() {
  saving.value = true
  editError.value = ''

  const empId = editForm.value.emp_id
  const body = {}
  for (const key of ['emp_name', 'gender', 'age', 'department', 'dept_id', 'salary', 'hire_date']) {
    if (editForm.value[key] !== '' && editForm.value[key] !== undefined) {
      body[key] = key === 'dept_id' || key === 'age'
        ? Number(editForm.value[key])
        : key === 'salary'
          ? Number(editForm.value[key])
          : editForm.value[key]
    }
  }

  const res = await updateEmployee(empId, body)
  saving.value = false

  if (res.success) {
    closeEdit()
    await fetchEmployees()
  } else {
    editError.value = res.message
  }
}

// ====== 删除 ======
async function handleDelete(empId) {
  if (!confirm(`确定删除员工 #${empId} 吗？此操作不可撤销。`)) return

  const res = await deleteEmployee(empId)
  if (res.success) {
    await fetchEmployees()
  } else {
    alert('删除失败：' + res.message)
  }
}
</script>
```

---

## 五、前后端数据流对接

> 📘 全链路详解（API 封装、Token 认证、路由守卫、Vite 代理、踩坑点）见专题文档
> **[vue-employee-dataflow-explained.md](./vue-employee-dataflow-explained.md)**。

### 列表加载流程

```
Employees.vue                  FastAPI
───────────                   ───────
onMounted()
  │
  ├─ fetchEmployees()
  │    │
  │    └─ getEmployees() ────→ GET /employee (无需 token)
  │                                │
  │                                └─ SELECT * FROM employee
  │                                     │
  │    ←───── JSON 数组 ←───────────────┘
  │    [
  │      {emp_id:1001, emp_name:"张三", ...},
  │      {emp_id:1002, emp_name:"李四", ...}
  │    ]
  │
  └─ employees.value = res
     渲染 table
```

### 编辑流程

```
Employees.vue                          FastAPI
───────────                            ───────
openEdit(emp)
  │ 显示弹窗，填充表单
  │
handleUpdate()
  │
  ├─ 构造 body = {emp_name, age, ...}
  │  (只包含有值的字段)
  │
  └─ updateEmployee(id, body) ────→ PUT /employee/{id}
                                       Authorization: Bearer <token>
                                       │
                                       ├─ Depends(get_current_emp) 验证 token
                                       ├─ SELECT ... WHERE emp_id = ?
                                       ├─ setattr 逐字段更新
                                       ├─ session.commit()
                                       └─ return ApiResponse(success=true, ...)

  ←───── {success:true, data:{emp_id, emp_name}} ────

  closeEdit()
  fetchEmployees()  ← 刷新列表
```

### 删除流程

```
Employees.vue                          FastAPI
───────────                            ───────
handleDelete(empId)
  │
  ├─ confirm("确定删除？")
  │
  └─ deleteEmployee(id) ─────────→ DELETE /employee/{id}
                                       Authorization: Bearer <token>
                                       │
                                       ├─ Depends(get_current_emp) 验证 token
                                       ├─ SELECT ... WHERE emp_id = ?
                                       ├─ session.delete(employee)
                                       ├─ session.commit()
                                       └─ return ApiResponse(success=true, ...)

  ←───── {success:true, data:{emp_id}} ────

  fetchEmployees()  ← 刷新列表
```

### 关键对接点

| 步骤 | 位置 | 说明 |
|------|------|------|
| 列表加载 | `onMounted` → `fetchEmployees()` | 页面挂载时自动加载 |
| Token 注入 | `src/api/index.js` `request()` | PUT/DELETE 自动带 `Authorization: Bearer` |
| 编辑只发有值字段 | `handleUpdate()` | 对应后端 `exclude_unset=True` |
| 类型转换 | `handleUpdate()` | age/dept_id→Number, salary→Number |
| 删除确认 | `handleDelete()` | `confirm()` 二次确认防止误删 |
| 列表刷新 | `fetchEmployees()` | 编辑/删除成功后重新加载 |
| GET 返回数组 | `fetchEmployees()` | 注意不是 `ApiResponse` 格式，用 `Array.isArray()` 判断 |

---

## ⚠️ 注意事项

1. **必须先添加 DELETE 接口**：后端没有删除接口则前端删除按钮无法工作。
2. **GET /employee 返回裸数组**：不是 `{success, message, data}` 格式，前端需特殊判断（`Array.isArray(res)`）。
3. **编辑的 dept_id**：如果数据库中该字段为 `NULL`，`emp.dept_id` 会是 `null`，前端用 `?? ''` 兜底。
4. **token 过期处理**：`api/index.js` 中 401 自动清除 token 并跳转登录页，编辑和删除都会触发。
5. **删除关联数据**：如果 `attendance` 表中有该员工的考勤记录，删除员工可能因外键约束失败。可先删除考勤再删员工，或在数据库中设置级联删除。
