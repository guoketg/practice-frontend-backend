# 后端登录功能实现指导

## 需求分析

当前后端存在两个问题：

1. `Employee` 模型缺少 `password` 字段
2. 缺少 `/login` POST 登录接口

需要完成两个文件的修改：

- [orm.py](file:///f:/code/MyPython/tiny-frontend/backend/orm.py)
- [main.py](file:///f:/code/MyPython/tiny-frontend/backend/main.py)


### 前端处理建议

前端应根据 `success` 字段判断登录结果：

```javascript
const response = await fetch('http://localhost:8000/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ emp_id: 1, password: '123456' })
});
const data = await response.json();

if (data.success) {
    // 登录成功 → 跳转到主页，存储 emp_id 和 emp_name
    console.log(`欢迎, ${data.emp_name}!`);
} else {
    // 登录失败 → 显示 data.message 错误提示
    alert(data.message);
}
```

### 当前方案的说明

> **为什么能跑**：当前登录接口**没有使用 `response_model`**（装饰器只写了 `@app.post('/login')`），FastAPI 会原样 JSON 序列化你返回的字典。成功时返回 4 个字段，失败时返回 2 个字段，前端通过 `success` 字段区分。
>
> **局限性**：
> 1. 不同接口的返回字段不一致（有的有 `emp_id`，有的没有），前端针对不同接口要写不同的解析逻辑
> 2. Swagger 文档无法自动生成响应体字段说明
> 3. 响应格式没有 Pydantic 校验，写错字段名不会报错

### 进阶：用 ApiResponse 统一所有接口的响应格式

如果你的项目有多个接口（登录、注册、部门CRUD 等），推荐创建一个**统一的响应体模型**，把所有业务数据统一放进 `data` 字段：

**步骤 1：新建文件 `backend/schemas.py`**，写入以下代码：

```python
from pydantic import BaseModel

class ApiResponse(BaseModel):
    """所有接口的统一响应格式"""
    success: bool
    message: str
    data: dict | None = None
```

| 字段 | 类型 | 说明 |
|---|---|---|
| `success` | `bool` | 所有接口都有，表示业务是否成功 |
| `message` | `str` | 所有接口都有，提示文案 |
| `data` | `dict \| None` | 成功时放业务数据（`emp_id`、`emp_name` 等都在这里面），失败时为 `null` |

**步骤 2：编辑文件 `backend/main.py` 第 94 行和第 7 行**，修改登录接口：

```python
# 编辑文件 backend/main.py 第 7 行 — 导入 ApiResponse
# 修改前
from orm import Base, DepartmentCreate, Department, EmployeeCreate, Employee, Attendance, AttendanceCreate, LoginRequest

# 修改后
from orm import Base, DepartmentCreate, Department, EmployeeCreate, Employee, Attendance, AttendanceCreate, LoginRequest
from schemas import ApiResponse
```

```python
# 编辑文件 backend/main.py 第 94-119 行 — 重构登录接口
# 修改前
@app.post('/login')
async def login(body: LoginRequest):
    # ... 查询逻辑 ...
    if employee and employee.password == body.password:
        return {'success': True, 'message': '登录成功', 'emp_id': employee.emp_id, 'emp_name': employee.emp_name}
    elif employee:
        return {'success': False, 'message': '密码错误'}
    else:
        return {'success': False, 'message': '员工不存在'}

# 修改后
@app.post('/login', response_model=ApiResponse)
async def login(body: LoginRequest):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Employee).where(Employee.emp_id == body.emp_id)
        )
        employee = result.scalar_one_or_none()

        if not employee:
            return ApiResponse(success=False, message='员工不存在')

        if employee.password != body.password:
            return ApiResponse(success=False, message='密码错误')

        return ApiResponse(
            success=True,
            message='登录成功',
            data={'emp_id': employee.emp_id, 'emp_name': employee.emp_name}
        )
```

**重构后的响应格式（所有接口统一）：**

```json
// 登录成功
{
    "success": true,
    "message": "登录成功",
    "data": { "emp_id": 1, "emp_name": "张三" }
}

// 登录失败
{
    "success": false,
    "message": "密码错误",
    "data": null
}
```

**前端解析（一套代码处理所有接口）：**

```javascript
const response = await fetch('http://localhost:8000/login', { /* ... */ });
const json = await response.json();

// 所有接口统一：先判断 success，再从 data 中取业务数据
if (json.success) {
    console.log(`欢迎, ${json.data.emp_name}!`);  // 业务数据在 data 里
} else {
    alert(json.message);
}
```

> **核心变化**：`emp_id`、`emp_name` 从顶层移到了 `data` 嵌套对象中，`data` 始终存在（失败时为 `null`），所有接口的响应结构完全一致。

***

## 测试登录接口

启动后端后，可以用以下方式测试：

**方法一：使用 curl**

```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{"emp_id": 1, "password": "123456"}'
```

**方法二：使用 FastAPI 自动文档**

访问 `http://localhost:8000/docs`，可以在 Swagger UI 中直接测试登录接口。

***

## 后续步骤

完成后端修改后，下一步需要：

1. 在数据库中为员工添加密码（可以通过创建员工接口传入 password）
2. 创建前端项目，实现登录页面调用此接口并处理响应体

