# FastAPI 员工登录接口完整逐行讲解
## 一、整体功能概述
这是一段 **FastAPI + SQLAlchemy 异步** 实现的员工登录 POST 接口，核心逻辑：
1. 接收前端提交的员工账号（emp_id）、密码；
2. 异步查询数据库匹配员工；
3. 三层判断：员工不存在 / 密码错误 / 登录成功；
4. 返回统一 JSON 格式结果。

## 二、逐段拆解说明
### 1. 接口路由装饰器
```python
@app.post('/login')
```
- `@app.post()`：声明这是 **POST 请求接口**，路径为 `/login`；
- 登录、提交数据类操作规范使用 POST，避免账号密码暴露在 URL。

### 2. 异步接口函数定义
```python
async def login(body: LoginRequest):
```
- `async def`：异步函数，配合 SQLAlchemy 异步数据库，不阻塞服务；
- `body: LoginRequest`：
  - `LoginRequest` 是自定义 Pydantic 请求模型；
  - FastAPI 会自动解析前端 JSON 请求体，校验字段类型并封装到 `body` 对象；
  - 前端必须传 `emp_id`、`password` 两个字段，少传/类型错误会直接返回 422 校验报错。

### 3. 异步数据库会话上下文
```python
async with AsyncSessionLocal() as session:
```
- `AsyncSessionLocal`：SQLAlchemy 异步数据库会话工厂，用于和数据库交互；
- `async with` 异步上下文管理器：
  1. 自动创建数据库连接会话 `session`；
  2. 代码块结束后**自动关闭会话、释放数据库连接**，不用手动 `await session.close()`，防止连接泄漏。

### 4. 异步执行 SQL 查询
```python
result = await session.execute(
    select(Employee).where(Employee.emp_id == body.emp_id)
)
```
- `select(Employee)`：SQLAlchemy ORM 语法，等价 SQL：`SELECT * FROM employee`；
- `.where(Employee.emp_id == body.emp_id)`：查询条件，匹配前端传入的员工编号；
- `await session.execute()`：异步执行 SQL，必须加 `await`，否则会报错；
- `result`：查询结果集对象，不能直接拿实体。

### 5. 取出单条查询结果
```python
employee = result.scalar_one_or_none()
```
- `scalar_one_or_none()` 核心作用：
  1. 只取 ORM 模型对象（丢弃元数据，直接得到 Employee 实例）；
  2. 数据库**匹配到 1 条数据** → 返回员工对象；
  3. 数据库**无匹配数据** → 返回 `None`；
- 对比其他方法：
  - `scalar_one()`：无数据会直接抛异常，登录场景不适用；
  - `scalars().all()`：返回列表，适合多条查询。

### 6. 第一层判断：员工是否存在
```python
if employee:
    # 员工存在逻辑
else:
    return {
        'success': False,
        'message': '员工不存在'
    }
```
`employee` 不为 None 代表数据库有该员工；反之直接返回登录失败，提示员工不存在。

### 7. 第二层判断：密码校验
```python
if employee.password == body.password:
    # 登录成功
else:
    return {
        'success': False,
        'message': '密码错误'
    }
```
直接对比数据库存储的密码和前端传的明文密码，匹配成功则登录通过。

### 8. 登录成功返回数据
```python
return {
    'success': True,
    'message': '登录成功',
    'emp_id': employee.emp_id,
    'emp_name': employee.emp_name
}
```
返回结构化 JSON：
- `success`：布尔标识业务是否成功，前端方便统一判断；
- `message`：提示文案，展示给用户；
- 附带员工编号、姓名，供前端页面展示/存储用户信息。

## 三、代码存在的明显缺陷（生产环境必须优化）
1. **明文存储密码，极度危险**
   数据库直接存原始密码，泄露后所有账号完全暴露，应使用 bcrypt/Argon2 哈希加密存储，登录时对比哈希值。
2. **无登录凭证（无 Token）**
   当前只返回员工信息，没有 JWT / Session，前端下次请求无法证明登录状态，后续接口会全部需要重新登录。
3. **错误信息区分过细，存在信息泄露**
   分开提示「员工不存在」「密码错误」，黑客可暴力遍历判断系统内有效员工账号，安全规范建议统一返回「账号或密码错误」。
4. **没有请求限流**
   无防暴力破解，攻击者可无限循环请求猜密码。
5. **没有统一响应格式、没有 HTTP 状态码控制**
   全部返回 200 状态码，靠 success 区分业务失败，规范项目会封装统一响应类。
6. **缺少异常捕获**
   数据库断连、查询异常会直接抛出 500 报错，没有 try-except 捕获处理。

## 四、补充配套依赖与模型示例（方便完整运行）
### 1. LoginRequest 请求模型（Pydantic）
```python
from pydantic import BaseModel

class LoginRequest(BaseModel):
    emp_id: str
    password: str
```
### 2. Employee 数据库模型（SQLAlchemy 异步）
```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Employee(Base):
    __tablename__ = "employee"
    emp_id: Mapped[str] = mapped_column(primary_key=True)
    emp_name: Mapped[str]
    password: Mapped[str]
```
### 3. 异步会话工厂
```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

async_engine = create_async_engine("mysql+asyncmy://user:pass@localhost/dbname")
AsyncSessionLocal = async_sessionmaker(bind=async_engine)
```

## 五、接口调用示例（前端请求）
请求地址：`POST http://127.0.0.1:8000/login`
请求体 JSON：
```json
{
    "emp_id": "E001",
    "password": "123456"
}
```
成功返回：
```json
{
    "success": true,
    "message": "登录成功",
    "emp_id": "E001",
    "emp_name": "张三"
}
```
密码错误返回：
```json
{
    "success": false,
    "message": "密码错误"
}
```
员工不存在返回：
```json
{
    "success": false,
    "message": "员工不存在"
}