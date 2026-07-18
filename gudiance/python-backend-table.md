# 关系数据库表格 — 代码编写教程

本教程教你如何使用 **SQLAlchemy ORM** 在 `orm.py` 中定义数据库表，并在 `main.py` 中完成数据库连接与 CRUD 操作。

## 数据库实测结构

以下是从你的 MySQL 实际查询到的三张表结构：

### `department` 部门表

| 列名 | 类型 | 允许空 | 键 | 额外 |
|---|---|---|---|---|
| `dept_id` | int | NO | **PRI** | auto_increment |
| `dept_name` | varchar(30) | NO | | |
| `dept_manager` | varchar(50) | NO | | |
| `dept_location` | varchar(50) | NO | | |

### `employee` 员工表

| 列名 | 类型 | 允许空 | 键 | 额外 |
|---|---|---|---|---|
| `emp_id` | int | NO | **PRI** | auto_increment |
| `emp_name` | varchar(50) | NO | | |
| `gender` | enum('男','女') | NO | | |
| `age` | int | NO | | |
| `department` | varchar(30) | NO | | |
| `salary` | decimal(10,2) | NO | | |
| `hire_date` | date | NO | | |

> ⚠️ `department` 列是 **普通 varchar**，不是外键！

### `attendance` 考勤表

| 列名 | 类型 | 允许空 | 键 | 额外 |
|---|---|---|---|---|
| `att_id` | int | NO | **PRI** | auto_increment |
| `emp_id` | int | NO | **MUL**（外键） | |
| `work_date` | date | NO | | |
| `work_hours` | decimal(4,1) | NO | | |
| `status` | enum('正常','迟到','早退','旷工') | NO | | |

### 外键关系

| 子表.列 | → | 父表.列 | 约束名 |
|---|---|---|---|
| `attendance.emp_id` | → | `employee.emp_id` | attendance_ibfk_1 |

> ⚠️ `employee.department` 是 varchar，**不是**外键 → `department.dept_id`。

---

## Step 1：在 `orm.py` 中定义三张表的模型

### 1.1 基础导入 & 基类

| 代码 | 解释 |
|---|---|
| `from sqlalchemy.orm import DeclarativeBase` | 导入 SQLAlchemy 2.0 声明式基类 |
| `from sqlalchemy import Column, Integer, String, Date, DECIMAL, Enum, ForeignKey` | Column 定义列；Integer/String/Date/DECIMAL 是字段类型；**Enum** 用于 MySQL 枚举列；**ForeignKey** 声明外键 |
| `class Base(DeclarativeBase): pass` | 创建基类，所有 ORM 模型都继承它 |

### 1.2 部门表 `department`

| 代码 | 解释 |
|---|---|
| `class Department(Base):` | ORM 模型类名 `Department` |
| `__tablename__ = "department"` | 对应 MySQL 表名 `department` |
| `dept_id = Column(Integer, primary_key=True, autoincrement=True)` | 主键 `dept_id`，自增 |
| `dept_name = Column(String(30), nullable=False)` | 部门名称，varchar(30) |
| `dept_manager = Column(String(50), nullable=False)` | 部门经理，varchar(50) |
| `dept_location = Column(String(50), nullable=False)` | 部门位置，varchar(50) |

### 1.3 员工表 `employee`

| 代码 | 解释 |
|---|---|
| `class Employee(Base):` | ORM 模型类名 `Employee` |
| `__tablename__ = "employee"` | 对应 MySQL 表名 `employee` |
| `emp_id = Column(Integer, primary_key=True, autoincrement=True)` | 主键 `emp_id`，自增 |
| `emp_name = Column(String(50), nullable=False)` | 姓名，varchar(50) |
| `gender = Column(Enum('男', '女'), nullable=False)` | **枚举**：男/女 |
| `age = Column(Integer, nullable=False)` | 年龄，整数 |
| `department = Column(String(30), nullable=False)` | 部门名，**普通字符串**，非外键 |
| `salary = Column(DECIMAL(10, 2), nullable=False)` | 薪资，10 位 + 2 位小数 |
| `hire_date = Column(Date, nullable=False)` | 入职日期 |

### 1.4 考勤表 `attendance`

| 代码 | 解释 |
|---|---|
| `class Attendance(Base):` | ORM 模型类名 `Attendance` |
| `__tablename__ = "attendance"` | 对应 MySQL 表名 `attendance` |
| `att_id = Column(Integer, primary_key=True, autoincrement=True)` | 主键 `att_id`，自增 |
| `emp_id = Column(Integer, ForeignKey("employee.emp_id"), nullable=False)` | **外键** → `employee.emp_id` |
| `work_date = Column(Date, nullable=False)` | 考勤日期 |
| `work_hours = Column(DECIMAL(4, 1), nullable=False)` | 工时，4 位数字 + 1 位小数（如 `8.0`） |
| `status = Column(Enum('正常', '迟到', '早退', '旷工'), nullable=False)` | 考勤状态枚举 |

### 完整代码 → 写入 `orm.py`

```python
# orm.py
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, Date, DECIMAL, Enum, ForeignKey


class Base(DeclarativeBase):
    pass


class Department(Base):
    __tablename__ = "department"

    dept_id = Column(Integer, primary_key=True, autoincrement=True)
    dept_name = Column(String(30), nullable=False)
    dept_manager = Column(String(50), nullable=False)
    dept_location = Column(String(50), nullable=False)


class Employee(Base):
    __tablename__ = "employee"

    emp_id = Column(Integer, primary_key=True, autoincrement=True)
    emp_name = Column(String(50), nullable=False)
    gender = Column(Enum('男', '女'), nullable=False)
    age = Column(Integer, nullable=False)
    department = Column(String(30), nullable=False)
    salary = Column(DECIMAL(10, 2), nullable=False)
    hire_date = Column(Date, nullable=False)


class Attendance(Base):
    __tablename__ = "attendance"

    att_id = Column(Integer, primary_key=True, autoincrement=True)
    emp_id = Column(Integer, ForeignKey("employee.emp_id"), nullable=False)
    work_date = Column(Date, nullable=False)
    work_hours = Column(DECIMAL(4, 1), nullable=False)
    status = Column(Enum('正常', '迟到', '早退', '旷工'), nullable=False)
```

---

## Step 2：在 `main.py` 中连接数据库并建表

### 2.1 创建异步引擎 & 会话工厂

| 代码 | 解释 |
|---|---|
| `from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker` | `create_async_engine` 创建异步连接池；`async_sessionmaker` 生成会话工厂 |
| `from orm import Base` | 导入 `orm.py` 中的 `Base`，用于自动建表 |
| `engine = create_async_engine(ASYNC_DATABASE_URL, echo=True)` | 创建异步引擎，`echo=True` 在控制台打印 SQL（调试用） |
| `AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)` | 创建会话工厂，`expire_on_commit=False` 避免提交后属性过期 |

### 2.2 在应用启动时自动建表

| 代码 | 解释 |
|---|---|
| `from contextlib import asynccontextmanager` | Python 内置的异步上下文管理器 |
| `@asynccontextmanager` | 装饰器，使函数可用于 `async with` |
| `async def lifespan(app):` | FastAPI 生命周期函数 |
| `async with engine.begin() as conn:` | 开启事务连接 |
| `await conn.run_sync(Base.metadata.create_all)` | **自动建表**：扫描所有 `Base` 子类并建表 |
| `yield` | 应用正常运行阶段 |

### 完整代码 → 修改 `main.py`

```python
# main.py
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from orm import Base

ASYNC_DATABASE_URL = 'mysql+aiomysql://root:123456@localhost:3306/company_hr_db'

engine = create_async_engine(ASYNC_DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)


@app.get('/')
async def root():
    return {'message': 'hello world'}


@app.get(path='/hello/{name}')
async def hello(name: str):
    return {'message': f'hello {name}'}
```

---

## Step 3：为三张表添加 CRUD 路由

### 3.1 核心语法速查

| 操作 | 代码 | 解释 |
|---|---|---|
| 新增 | `session.add(obj)` + `await session.commit()` | 添加对象 → 提交事务 |
| 查询全部 | `await session.execute(select(Model))` + `.scalars().all()` | 执行 SELECT → 提取对象列表 |
| 按 ID 查 | `await session.get(Model, pk_value)` | 主键查找，最快 |
| 更新 | `obj.列名 = 新值` + `await session.commit()` | 修改属性 → 提交 |
| 删除 | `await session.delete(obj)` + `await session.commit()` | 标记删除 → 提交 |

### 3.2 Pydantic 请求体定义

> 注意列名要与 ORM 模型完全一致（`emp_name` 而非 `name`）。

```python
from pydantic import BaseModel


class DepartmentCreate(BaseModel):
    dept_name: str
    dept_manager: str
    dept_location: str


class EmployeeCreate(BaseModel):
    emp_name: str
    gender: str          # '男' 或 '女'
    age: int
    department: str
    salary: float
    hire_date: str       # 'YYYY-MM-DD'


class AttendanceCreate(BaseModel):
    emp_id: int
    work_date: str       # 'YYYY-MM-DD'
    work_hours: float    # 如 8.0
    status: str           # '正常'/'迟到'/'早退'/'旷工'
```

### 3.3 路由代码

```python
from sqlalchemy import select
from orm import Department, Employee, Attendance


# ========== Department ==========

@app.post('/departments/')
async def create_department(body: DepartmentCreate):
    async with AsyncSessionLocal() as session:
        dept = Department(**body.model_dump())
        session.add(dept)
        await session.commit()
        await session.refresh(dept)
        return {'dept_id': dept.dept_id, 'dept_name': dept.dept_name}


@app.get('/departments/')
async def list_departments():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Department))
        depts = result.scalars().all()
        return [
            {'dept_id': d.dept_id, 'dept_name': d.dept_name, 'dept_manager': d.dept_manager}
            for d in depts
        ]


# ========== Employee ==========

@app.post('/employees/')
async def create_employee(body: EmployeeCreate):
    async with AsyncSessionLocal() as session:
        emp = Employee(**body.model_dump())
        session.add(emp)
        await session.commit()
        await session.refresh(emp)
        return {'emp_id': emp.emp_id, 'emp_name': emp.emp_name}


@app.get('/employees/')
async def list_employees():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Employee))
        emps = result.scalars().all()
        return [
            {'emp_id': e.emp_id, 'emp_name': e.emp_name, 'gender': e.gender,
             'age': e.age, 'department': e.department, 'salary': float(e.salary)}
            for e in emps
        ]


# ========== Attendance ==========

@app.post('/attendances/')
async def create_attendance(body: AttendanceCreate):
    async with AsyncSessionLocal() as session:
        att = Attendance(**body.model_dump())
        session.add(att)
        await session.commit()
        await session.refresh(att)
        return {'att_id': att.att_id, 'emp_id': att.emp_id, 'status': att.status}


@app.get('/attendances/')
async def list_attendances():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Attendance))
        atts = result.scalars().all()
        return [
            {'att_id': a.att_id, 'emp_id': a.emp_id,
             'work_date': str(a.work_date), 'work_hours': float(a.work_hours),
             'status': a.status}
            for a in atts
        ]
```

---

## 最终文件结构

| 文件 | 职责 |
|---|---|
| `orm.py` | 定义 `Base` + 三张表的 ORM 模型 |
| `main.py` | FastAPI 应用 + 引擎/会话 + 生命周期建表 + CRUD 路由 |

## 表关系总结

| 表 | 主键 | 外键 | 关系 |
|---|---|---|---|
| `department` | `dept_id` | — | 独立表，无外键 |
| `employee` | `emp_id` | — | `department` 列是普通 varchar，**不是外键** |
| `attendance` | `att_id` | `emp_id` → `employee.emp_id` | 每个考勤记录属于一个员工 (N:1) |

## 运行前检查清单

| 步骤 | 操作 |
|---|---|
| 安装依赖 | `pip install fastapi sqlalchemy aiomysql uvicorn pydantic` |
| 确保 MySQL 已启动 | 本地 3306，库 `company_hr_db` 已存在 |
| 启动服务 | `uvicorn main:app --reload` |
| 测试 | 访问 `http://localhost:8000/docs` 查看 Swagger 文档 |
