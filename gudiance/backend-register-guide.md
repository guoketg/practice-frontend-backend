# 后端注册功能实现指导

## 需求分析

目前后端已有 `/login` 登录接口，但缺少 `/register` 注册接口。注册接口需要：

1. 用户通过姓名、密码、性别、年龄、部门等信息进行注册
2. 注册前需检查用户名是否已存在（避免重复注册）
3. 返回与登录接口一致格式的响应（success, message, emp_id, emp_name）
4. 注意：emp_id 由数据库自动生成，不应要求用户输入

需要修改两个文件：

- [orm.py](file:///f:/code/MyPython/tiny-frontend/backend/orm.py)
- [main.py](file:///f:/code/MyPython/tiny-frontend/backend/main.py)

***

## 前置修复

在实现注册接口之前，需要先修复 [orm.py](file:///f:/code/MyPython/tiny-frontend/backend/orm.py) 中已存在的几个问题，否则可能导致运行时错误：

### 问题一：ForeignKey 引用错误

**位置**: [orm.py](file:///f:/code/MyPython/tiny-frontend/backend/orm.py#L32) 第 32 行

```python
# 修改前
dept_id:Mapped[int] = mapped_column(Integer, ForeignKey("department.id"), nullable=True)

# 修改后
dept_id:Mapped[int] = mapped_column(Integer, ForeignKey("department.dept_id"), nullable=True)
```

**原因**: `department` 表的主键列名是 `dept_id`，不是 `id`。

---

**位置**: [orm.py](file:///f:/code/MyPython/tiny-frontend/backend/orm.py#L38) 第 38 行

```python
# 修改前
emp_id:Mapped[int] = mapped_column(Integer,ForeignKey('employee.id'))

# 修改后
emp_id:Mapped[int] = mapped_column(Integer,ForeignKey('employee.emp_id'))
```

**原因**: `employee` 表的主键列名是 `emp_id`，不是 `id`。

---

**位置**: [orm.py](file:///f:/code/MyPython/tiny-frontend/backend/orm.py#L43) 第 43 行

```python
# 修改前
employee_id:Mapped[int] = mapped_column(Integer, ForeignKey("employee.id"), nullable=False)

# 修改后
employee_id:Mapped[int] = mapped_column(Integer, ForeignKey("employee.emp_id"), nullable=False)
```

---

### 问题二：LoginResponse 拼写错误

**位置**: [orm.py](file:///f:/code/MyPython/tiny-frontend/backend/orm.py#L76) 第 76 行

```python
# 修改前
suceess:bool

# 修改后
success:bool
```

---

### 问题三：EmployeeCreate.dept_id 类型不一致

**位置**: [orm.py](file:///f:/code/MyPython/tiny-frontend/backend/orm.py#L62) 第 62 行

```python
# 修改前
dept_id:str

# 修改后
dept_id:int | None = None
```

**原因**: `Employee` 模型中 `dept_id` 是 `Integer` 类型，应保持一致。

***

## 修改步骤

### 步骤一：修改 orm.py - 添加 RegisterRequest 模型

**文件**: [orm.py](file:///f:/code/MyPython/tiny-frontend/backend/orm.py)

#### 1. 创建注册请求的 Pydantic 模型

在文件末尾（第 80 行 `LoginResponse` 之后）添加 `RegisterRequest` 模型：

```python
class RegisterRequest(BaseModel):
    emp_name: str
    password: str
    gender: str
    age: int
    department: str
    salary: float = 0.0
    hire_date: str | None = None
```

**说明**:
- `emp_name` 和 `password` 为必填字段
- `gender`、`age`、`department` 为员工基本信息必填字段
- `salary` 设置默认值 0.0，可选填
- `hire_date` 设置为可选字段，允许为 None
- **不包含 emp_id**，因为主键由数据库自动生成

***

### 步骤二：修改 main.py - 添加注册接口

**文件**: [main.py](file:///f:/code/MyPython/tiny-frontend/backend/main.py)

#### 1. 导入 RegisterRequest 模型

找到第 7 行的导入语句，添加 `RegisterRequest`：

```python
from orm import Base, DepartmentCreate, Department, EmployeeCreate, Employee, Attendance, AttendanceCreate, LoginRequest, RegisterRequest
```

#### 2. 添加注册接口

在 `/login` 接口（第 114-127 行）之后添加 `/register` POST 接口：

```python
@app.post('/register')
async def register(body: RegisterRequest):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Employee).where(Employee.emp_name == body.emp_name)
        )
        existing_employee = result.scalar_one_or_none()
        
        if existing_employee:
            return {'success': False, 'message': '该员工姓名已存在'}
        
        employee_data = body.model_dump()
        employee = Employee(**employee_data)
        session.add(employee)
        await session.commit()
        await session.refresh(employee)
        
        return {
            'success': True,
            'message': '注册成功',
            'emp_id': employee.emp_id,
            'emp_name': employee.emp_name
        }
```

**逻辑说明**:

1. **查重检查**: 先查询数据库中是否已存在同名员工
2. **返回重复错误**: 如果存在，返回 `success: False, message: '该员工姓名已存在'`
3. **创建新员工**: 如果不存在，将请求数据转换为 Employee 对象并保存
4. **返回成功信息**: 返回 `success: True` 及新员工的 emp_id 和 emp_name

***

## 修改后的完整代码示例

### orm.py 新增部分

```python
class RegisterRequest(BaseModel):
    emp_name: str
    password: str
    gender: str
    age: int
    department: str
    salary: float = 0.0
    hire_date: str | None = None
```

### main.py 新增部分

```python
from orm import ..., RegisterRequest

# ... 其他接口不变

@app.post('/register')
async def register(body: RegisterRequest):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Employee).where(Employee.emp_name == body.emp_name)
        )
        existing_employee = result.scalar_one_or_none()
        
        if existing_employee:
            return {'success': False, 'message': '该员工姓名已存在'}
        
        employee_data = body.model_dump()
        employee = Employee(**employee_data)
        session.add(employee)
        await session.commit()
        await session.refresh(employee)
        
        return {
            'success': True,
            'message': '注册成功',
            'emp_id': employee.emp_id,
            'emp_name': employee.emp_name
        }
```

***

## 测试注册接口

启动后端后，可以用以下方式测试：

**方法一：使用 curl**

```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{
    "emp_name": "张三",
    "password": "123456",
    "gender": "男",
    "age": 28,
    "department": "技术部",
    "salary": 8000.00
  }'
```

**方法二：使用 FastAPI 自动文档**

访问 `http://localhost:8000/docs`，可以在 Swagger UI 中直接测试注册接口。

***

## 接口响应格式

> **重要**：前端开发者需要根据以下响应格式来解析接口返回的数据、处理不同业务状态。实际开发中，响应体（Response Body）和请求体（Request Body）同样重要，缺一不可。

### 注册成功响应

**HTTP 状态码**: `200 OK`

```json
{
    "success": true,
    "message": "注册成功",
    "emp_id": 5,
    "emp_name": "张三"
}
```

| 字段 | 类型 | 说明 |
|---|---|---|
| `success` | `bool` | 业务是否成功，`true` 表示注册成功 |
| `message` | `str` | 提示信息："注册成功" |
| `emp_id` | `int` | 数据库自动生成的新员工编号 |
| `emp_name` | `str` | 注册时填写的员工姓名 |

### 注册失败响应 — 员工姓名已存在

**HTTP 状态码**: `200 OK`

```json
{
    "success": false,
    "message": "该员工姓名已存在"
}
```

| 字段 | 类型 | 说明 |
|---|---|---|
| `success` | `bool` | `false` 表示注册失败 |
| `message` | `str` | 错误原因："该员工姓名已存在" |

### 注册失败响应 — 员工编号已存在（如有此校验）

**HTTP 状态码**: `200 OK`

```json
{
    "success": false,
    "message": "该员工编号已被注册"
}
```

### 前端处理建议

前端应根据 `success` 字段判断注册结果：

```javascript
const response = await fetch('http://localhost:8000/register', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        emp_name: '张三',
        password: '123456',
        gender: '男',
        age: 28,
        department: '技术部',
        salary: 8000.00
    })
});
const data = await response.json();

if (data.success) {
    // 注册成功 → 跳转到登录页，提示用户去登录
    alert(`注册成功！您的员工编号是: ${data.emp_id}`);
} else {
    // 注册失败 → 显示 data.message 错误提示
    alert(data.message);
}
```

### 当前方案的说明

> **为什么能跑**：当前注册接口**没有使用 `response_model`**，FastAPI 原样 JSON 序列化返回的字典。成功时返回 4 个字段（含 `emp_id`、`emp_name`），失败时返回 2 个字段（`success`、`message`），前端通过 `success` 字段区分。与登录接口保持一致的约定。

### 进阶：用 ApiResponse 统一所有接口的响应格式

如果希望所有接口（登录、注册、部门CRUD 等）的响应格式完全统一，推荐创建共用响应体模型：

**步骤 1：新建文件 `backend/schemas.py`**，写入以下代码：

```python
from pydantic import BaseModel

class ApiResponse(BaseModel):
    """所有接口的统一响应格式"""
    success: bool
    message: str
    data: dict | None = None
```

**步骤 2：编辑文件 `backend/main.py` 第 142-164 行**，重构注册接口：

```python
# 编辑文件 backend/main.py 第 7 行 — 导入 ApiResponse
# 修改前
from orm import Base, DepartmentCreate, Department, EmployeeCreate, Employee, Attendance, AttendanceCreate, LoginResponse, LoginRequest, RegisterRequest

# 修改后
from orm import Base, DepartmentCreate, Department, EmployeeCreate, Employee, Attendance, AttendanceCreate, LoginRequest, RegisterRequest
from schemas import ApiResponse
```

```python
# 编辑文件 backend/main.py 第 142-164 行 — 重构注册接口
# 修改前
@app.post('/register')
async def register(body: RegisterRequest):
    # ... 查重、创建 ...
    if existing_employee:
        return {'success': False, 'message': '该员工姓名已存在'}
    # ...
    return {'success': True, 'message': '注册成功', 'emp_id': employee.emp_id, 'emp_name': employee.emp_name}

# 修改后
@app.post('/register', response_model=ApiResponse)
async def register(body: RegisterRequest):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Employee).where(Employee.emp_name == body.emp_name)
        )
        existing_employee = result.scalar_one_or_none()

        if existing_employee:
            return ApiResponse(success=False, message='该员工姓名已存在')

        employee_data = body.model_dump()
        employee = Employee(**employee_data)
        session.add(employee)
        await session.commit()
        await session.refresh(employee)

        return ApiResponse(
            success=True,
            message='注册成功',
            data={'emp_id': employee.emp_id, 'emp_name': employee.emp_name}
        )
```

**重构后的响应格式（与登录接口完全一致）：**

```json
// 注册成功 — data 中放业务字段
{
    "success": true,
    "message": "注册成功",
    "data": { "emp_id": 5, "emp_name": "张三" }
}

// 注册失败 — data 为 null
{
    "success": false,
    "message": "该员工姓名已存在",
    "data": null
}
```

> **关键点**：`emp_id`、`emp_name` 等业务数据必须放入 `data` 嵌套对象中，不能平铺在顶层。如果平铺，Pydantic 会因 `response_model=ApiResponse` 而丢弃它们。

***

## 注意事项

1. **密码安全性**: 当前密码以明文存储，生产环境应使用 `bcrypt` 或 `passlib` 进行哈希加密
2. **字段验证**: 当前接口依赖 Pydantic 的基本验证，如需更严格的验证（如密码长度、格式等），可添加 Pydantic 验证器
3. **错误处理**: 当前返回简单的字符串错误信息，可扩展为更详细的错误码
4. **数据一致性**: 注册时 department 字段应与 department 表中的部门名称保持一致（可后续添加部门验证逻辑）