# Vue 员工列表页详解（面向后端开发者）

> **前提**：你熟悉 Python/FastAPI/SQLAlchemy，但对前端 Vue 不熟。本文用后端类比的方
> 式，逐行讲解 `Employees.vue` 中的前端代码。

---

## 一、Vue 单文件组件的基本结构

一个 `.vue` 文件相当于一个**自包含的页面/组件**，分三个区域：

```vue
<template>   ← 相当于 Jinja2 模板（HTML + 逻辑指令）
</template>

<script setup>  ← 相当于你的 Python 路由函数，写 JS 逻辑
</script>

<style>    ← 相当于 CSS 文件
</style>
```

对比后端：
- `<template>` ≈ Jinja2 的 `return templates.TemplateResponse("xxx.html", {...})`
- `<script setup>` ≈ `@app.get("/employees")` 里面的 Python 代码
- `<style>` ≈ 静态 CSS 文件

> **`<script setup>`** 是 Vue 3 的语法糖，比传统写法更简洁。setup 的意思是「初始化阶段就会执行」。

---

## 二、逐区域讲解

### 2.1 `<template>` 区域 —— 渲染逻辑

```vue
<template>
  <div class="employees-page">
    <h2>员工管理</h2>
```

Vue 模板要求**所有内容必须包裹在一个根元素**内。这里用 `<div class="employees-page">` 作为根。

#### 2.1.1 `v-if` / `v-else-if` / `v-else` —— 条件渲染

```vue
    <div v-if="loading" class="loading">加载中...</div>
```

| Vue 指令 | 类比 Python | 含义 |
|----------|------------|------|
| `v-if="loading"` | `if loading:` | 条件为真时才渲染这个元素 |
| `v-else-if="employees.length > 0"` | `elif len(employees) > 0:` | 第二个条件 |
| `v-else` | `else:` | 以上都不满足 |

对应后端逻辑：

```python
# 等价于在 Jinja2 模板中：
{% if loading %}
    <div class="loading">加载中...</div>
{% elif employees %}
    <table>...</table>
{% else %}
    <p>暂无员工数据</p>
{% endif %}
```

**关键区别**：Vue 的 `v-if` 是**响应式**的。当 `loading` 变量的值改变时，页面自动重新渲染，不需要手动刷新。

#### 2.1.2 `v-for` —— 列表渲染

```vue
        <tr v-for="emp in employees" :key="emp.emp_id">
          <td>{{ emp.emp_id }}</td>
          <td>{{ emp.emp_name }}</td>
          ...
```

| Vue 指令 | 类比 Python | 含义 |
|----------|------------|------|
| `v-for="emp in employees"` | `for emp in employees:` | 遍历数组，每项生成一个 `<tr>` |
| `:key="emp.emp_id"` | 数据库主键 | Vue 用它追踪每行，**必须有唯一值** |

对应后端逻辑：

```python
# 等价于：
for emp in employees:
    # 渲染一行 <tr>
    # emp.emp_id, emp.emp_name, ...
```

`:key` 的作用类似数据库的主键索引 —— Vue 用 `emp_id` 来区分每一行，当数据变化时知道哪些行要更新、删除或新增。

#### 2.1.3 `{{ }}` —— 插值表达式

```vue
          <td>{{ emp.emp_id }}</td>
```

| Vue 语法 | 类比后端 | 含义 |
|----------|---------|------|
| `{{ variable }}` | Jinja2 的 `{{ variable }}` | 在 HTML 中输出变量的值 |

**注意**：`{{ }}` 只能用在**标签的内容区域**（开始标签和结束标签之间），不能用在标签属性上。

#### 2.1.4 `@click` —— 事件绑定

```vue
            <button class="btn-sm" @click="openEdit(emp)">编辑</button>
            <button class="btn-sm btn-danger" @click="handleDelete(emp.emp_id)">删除</button>
```

| Vue 指令 | 类比后端 | 含义 |
|----------|---------|------|
| `@click="openEdit(emp)"` | 点击事件 → 调用函数 | 点击按钮时执行 `openEdit(emp)` |
| `@click="handleDelete(emp.emp_id)"` | 同上 | 点击按钮时执行 `handleDelete(emp.emp_id)` |

`@click` 是 `v-on:click` 的简写。相当于 HTML 的 `onclick`，但 Vue 的事件处理更强大。

#### 2.1.5 `v-model` —— 双向绑定

```vue
          <input v-model="editForm.emp_name" />
          <select v-model="editForm.gender">
            <option value="男">男</option>
            <option value="女">女</option>
          </select>
          <input v-model.number="editForm.age" type="number" />
```

| Vue 指令 | 类比后端 | 含义 |
|----------|---------|------|
| `v-model="editForm.emp_name"` | Pydantic 模型字段 | 输入框的值 ↔ JS 变量，双向同步 |
| `v-model.number="editForm.age"` | `int()` 类型转换 | 自动把输入转为数字类型 |

**双向绑定**的含义：当用户修改输入框 → `editForm.emp_name` 自动更新；当代码修改 `editForm.emp_name` → 输入框自动更新。

对应后端类比：

```python
# v-model 相当于自动做了这件事：
class EditForm:
    emp_name: str   # ← 和输入框实时同步

# 用户输入 "张三" → form.emp_name 自动变成 "张三"
# 代码 form.emp_name = "李四" → 输入框自动显示 "李四"
```

#### 2.1.6 `@submit.prevent` —— 阻止表单默认行为

```vue
        <form @submit.prevent="handleUpdate">
```

| Vue 语法 | 含义 |
|----------|------|
| `@submit` | 监听表单提交事件 |
| `.prevent` | 阻止浏览器默认刷新页面（等价于 `event.preventDefault()`） |
| `="handleUpdate"` | 提交时调用 `handleUpdate()` |

这和后端无关，是前端特有的 —— 浏览器默认提交表单会刷新页面，`.prevent` 阻止它。

#### 2.1.7 `:disabled` —— 动态属性绑定

```vue
            <button type="submit" :disabled="saving">
              {{ saving ? '保存中...' : '保存' }}
            </button>
```

| Vue 语法 | 含义 |
|----------|------|
| `:disabled="saving"` | 当 `saving` 为 `true`，按钮禁用 |
| `{{ saving ? '保存中...' : '保存' }}` | 三元表达式：`"保存中..." if saving else "保存"` |

`:` 前缀是 `v-bind:` 的简写，表示属性值是 JS 变量而非纯字符串。

#### 2.1.8 `@click.self` —— 修饰符

```vue
    <div v-if="showEdit" class="modal-overlay" @click.self="closeEdit">
```

| Vue 语法 | 含义 |
|----------|------|
| `@click.self` | 只有点击**这个 div 本身**（不是它的子元素）才触发 |
| `="closeEdit"` | 触发时关闭弹窗 |

这样实现了「点击遮罩层关闭弹窗，点击弹窗内部不关闭」。

---

### 2.2 `<script setup>` 区域 —— 逻辑代码

```javascript
import { ref, onMounted } from 'vue'
import { getEmployees, updateEmployee, deleteEmployee } from '../api'
```

| JS 语法 | 类比 Python | 含义 |
|---------|------------|------|
| `import { ref, onMounted } from 'vue'` | `from vue import ref, onMounted` | 从 Vue 库导入函数 |
| `import { getEmployees, ... } from '../api'` | `from ..api import get_employees` | 导入自己写的 API 函数 |

#### 2.2.1 `ref()` —— 响应式变量（⭐ 核心概念）

```javascript
const employees = ref([])
const loading = ref(true)
const showEdit = ref(false)
const saving = ref(false)
const editError = ref('')
const editForm = ref({})
```

**这是 Vue 最重要的概念**。`ref()` 创建一个**响应式引用**，当它的值改变时，所有用到它的模板位置自动更新。

类比后端：

```python
# 普通 Python 变量：改了值，HTML 不会自动更新
employees = []
employees = [emp1, emp2]  # ← Jinja2 模板不会知道这个变化

# Vue ref()：改了值，HTML 自动重新渲染
const employees = ref([])     # ← 创建响应式引用
employees.value = [emp1, emp2]  # ← 页面自动刷新！
```

**关键点**：
- 在 `<script>` 中读写 ref 变量，必须用 `.value`：`employees.value = [...]`
- 在 `<template>` 中读写 ref 变量，**不用**.value：`{{ employees }}`（Vue 自动解包）

对比表：

| 位置 | 读取 | 写入 |
|------|------|------|
| `<script>` 中 | `employees.value` | `employees.value = [...]` |
| `<template>` 中 | `{{ employees }}` | `v-model="..."` 自动处理 |

#### 2.2.2 `onMounted()` —— 生命周期钩子

```javascript
onMounted(fetchEmployees)
```

| Vue 概念 | 类比 FastAPI | 含义 |
|----------|-------------|------|
| `onMounted(fn)` | `@app.on_event("startup")` | 组件挂载到 DOM 后自动执行 |

`onMounted` 是 Vue 的**生命周期钩子**之一。当一个组件首次渲染到页面上，会触发 mounted 事件。

FastAPI 类比：

```python
# FastAPI 启动时执行
@app.on_event("startup")
async def startup():
    # 初始化数据库连接等

# Vue 组件挂载时执行
onMounted(() => {
    fetchEmployees()  // 页面加载时自动拉取数据
})
```

**常见生命周期对比**：

| Vue 生命周期 | FastAPI 类比 | 触发时机 |
|-------------|-------------|---------|
| `setup()` | 类 `__init__` | 组件初始化（`<script setup>` 本身就是） |
| `onMounted()` | `startup` 事件 | DOM 渲染完成后 |
| `onUnmounted()` | `shutdown` 事件 | 组件销毁前 |

#### 2.2.3 `fetchEmployees()` —— 加载数据

```javascript
async function fetchEmployees() {
  loading.value = true
  const res = await getEmployees()
  if (Array.isArray(res)) {
    employees.value = res
  }
  loading.value = false
}
```

逐行对应的后端类比：

```python
async def fetch_employees():
    loading = True                      # 1. 设置加载状态
    res = await get_employees()         # 2. httpx.get("http://.../employee")
    if isinstance(res, list):           # 3. 判断返回类型
        employees = res                 # 4. 赋值
    loading = False                     # 5. 清除加载状态
```

**特别注意**：`getEmployees()` 来自 `../api/index.js`，它封装了 `fetch()` 调用，等价于 Python 的 `httpx.get()` 或 `requests.get()`。

#### 2.2.4 `openEdit(emp)` —— 打开编辑弹窗

```javascript
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
```

关键点：
- **`??` 空值合并运算符**：`a ?? b` 表示「如果 a 是 `null` 或 `undefined`，则用 b」。等价于 Python 的 `a if a is not None else b`。
- **浅拷贝**：把员工数据拷贝一份到 `editForm`，这样编辑不会直接修改原始数据。

#### 2.2.5 `handleUpdate()` —— 提交编辑

```javascript
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
```

逐行对应的 Python 类比：

```python
async def handle_update():
    saving = True                               # 1. 设置保存中
    edit_error = ""                             # 2. 清空错误

    emp_id = edit_form["emp_id"]                # 3. 取 ID
    body = {}                                   # 4. 构造请求体
    for key in ["emp_name", "gender", "age", ...]:
        val = edit_form.get(key)
        if val not in ("", None):
            if key in ("dept_id", "age"):
                body[key] = int(val)
            elif key == "salary":
                body[key] = float(val)
            else:
                body[key] = val

    res = await update_employee(emp_id, body)   # 5. HTTP PUT
    saving = False                              # 6. 解除保存中

    if res.success:
        close_edit()                            # 7a. 关闭弹窗
        await fetch_employees()                 # 7b. 刷新列表
    else:
        edit_error = res.message                # 8. 显示错误
```

**类型转换的必要性**：HTML `<input>` 的值始终是字符串。即使写了 `type="number"`，`v-model` 也需要 `.number` 修饰符才能转成数字。这里是手动用 `Number()` 做双重保险。

#### 2.2.6 `handleDelete(empId)` —— 删除员工

```javascript
async function handleDelete(empId) {
  if (!confirm(`确定删除员工 #${empId} 吗？此操作不可撤销。`)) return

  const res = await deleteEmployee(empId)
  if (res.success) {
    await fetchEmployees()
  } else {
    alert('删除失败：' + res.message)
  }
}
```

Python 类比：

```python
async def handle_delete(emp_id: int):
    if not confirm(f"确定删除员工 #{emp_id} 吗？"):
        return

    res = await delete_employee(emp_id)
    if res.success:
        await fetch_employees()
    else:
        alert(f"删除失败：{res.message}")
```

---

## 三、Vue 核心概念速查表

| Vue 概念 | 类比 Python/后端 | 一句话解释 |
|----------|-----------------|-----------|
| `ref()` | `variable = value`（但带自动渲染） | 值变了，页面自动更新 |
| `.value` | 直接变量名 | 在 script 中读写 ref 必须用 `.value` |
| `v-if` | `if:` | 条件为真才渲染 |
| `v-for` | `for x in list:` | 遍历数组生成重复元素 |
| `:key` | 数据库主键 | 给 v-for 每项一个唯一标识 |
| `v-model` | Pydantic 字段 | 表单输入和 JS 变量双向同步 |
| `@click` | `onclick` 回调 | 点击时调用函数 |
| `@submit.prevent` | 阻止表单默认提交 | 防止页面刷新 |
| `onMounted()` | `startup` 事件 | 组件渲染完后自动执行 |
| `{{ }}` | Jinja2 `{{ }}` | 在 HTML 中输出变量 |
| `:disabled` | HTML disabled 属性 | 动态控制按钮禁用 |
| `??` | `x if x is not None else y` | 空值合并 |
| `Number()` | `int()` / `float()` | 字符串转数字 |

---

## 四、数据流动全景图

```
用户打开页面
    │
    ▼
onMounted() 触发
    │
    ▼
fetchEmployees() 执行
    │
    ├─ loading.value = true       → v-if="loading" 展示「加载中」
    │
    ├─ await getEmployees()       → GET /employee
    │     │
    │     └─ 后端返回 JSON 数组
    │
    ├─ employees.value = res      → v-for="emp in employees" 渲染表格
    │
    └─ loading.value = false      → 隐藏「加载中」

用户点击「编辑」
    │
    ▼
openEdit(emp)
    ├─ editForm.value = {...emp}  → v-model 填充表单
    └─ showEdit.value = true      → v-if="showEdit" 显示弹窗

用户修改表单 → v-model 自动同步到 editForm.value

用户点击「保存」
    │
    ▼
handleUpdate()
    ├─ saving.value = true        → :disabled="saving" 禁用按钮
    ├─ await updateEmployee(id, body) → PUT /employee/{id}
    └─ closeEdit() + fetchEmployees() → 刷新列表

用户点击「删除」
    │
    ▼
handleDelete(empId)
    ├─ confirm() 二次确认
    └─ await deleteEmployee(id)  → DELETE /employee/{id}
         └─ fetchEmployees()     → 刷新列表
```
