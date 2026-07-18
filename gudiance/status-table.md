# 项目状态维护表

## 后端状态表

| 功能模块 | 接口路径 | HTTP方法 | 完成状态 | 负责文件 | 待办事项 |
|---|---|---|---|---|---|
| 健康检查 | `/` | GET | ✅ 已完成 | [main.py](file:///f:/code/MyPython/tiny-frontend/backend/main.py#L35-L37) | - |
| 部门创建 | `/departments` | POST | ✅ 已完成 | [main.py](file:///f:/code/MyPython/tiny-frontend/backend/main.py#L43-L51) | - |
| 部门查询 | `/departments` | GET | ✅ 已完成 | [main.py](file:///f:/code/MyPython/tiny-frontend/backend/main.py#L53-L64) | - |
| 员工创建 | `/employee` | POST | ✅ 已完成 | [main.py](file:///f:/code/MyPython/tiny-frontend/backend/main.py#L66-L73) | - |
| 员工查询 | `/employee` | GET | ✅ 已完成 | [main.py](file:///f:/code/MyPython/tiny-frontend/backend/main.py#L75-L89) | - |
| 考勤创建 | `/attendance` | POST | ✅ 已完成 | [main.py](file:///f:/code/MyPython/tiny-frontend/backend/main.py#L91-L98) | - |
| 考勤查询 | `/attendance` | GET | ✅ 已完成 | [main.py](file:///f:/code/MyPython/tiny-frontend/backend/main.py#L100-L112) | - |
| 用户登录 | `/login` | POST | ✅ 已完成 | [main.py](file:///f:/code/MyPython/tiny-frontend/backend/main.py#L114-L127) | - |
| 用户注册 | `/register` | POST | ❌ 待实现 | [main.py](file:///f:/code/MyPython/tiny-frontend/backend/main.py) | 添加注册接口 |
| 密码加密 | - | - | ❌ 待实现 | [orm.py](file:///f:/code/MyPython/tiny-frontend/backend/orm.py) | 使用 bcrypt 加密密码 |
| ORM模型 | Employee/Department/Attendance | - | ✅ 已完成 | [orm.py](file:///f:/code/MyPython/tiny-frontend/backend/orm.py) | 修复 ForeignKey 引用问题 |
| ORM模型 | RegisterRequest | - | ❌ 待实现 | [orm.py](file:///f:/code/MyPython/tiny-frontend/backend/orm.py) | 添加注册请求模型 |
| CORS配置 | - | - | ✅ 已完成 | [main.py](file:///f:/code/MyPython/tiny-frontend/backend/main.py#L27-L33) | - |

### 后端已知问题

| 问题描述 | 位置 | 严重程度 | 状态 |
|---|---|---|---|
| `LoginResponse` 中 `suceess` 拼写错误，应为 `success` | [orm.py](file:///f:/code/MyPython/tiny-frontend/backend/orm.py#L76) | 中 | ❌ 待修复 |
| `ForeignKey("department.id")` 引用错误，应为 `department.dept_id` | [orm.py](file:///f:/code/MyPython/tiny-frontend/backend/orm.py#L32) | 高 | ❌ 待修复 |
| `ForeignKey("employee.id")` 引用错误，应为 `employee.emp_id` | [orm.py](file:///f:/code/MyPython/tiny-frontend/backend/orm.py#L38) | 高 | ❌ 待修复 |
| `EmployeeCreate.dept_id` 类型为 `str`，但模型中为 `Integer` | [orm.py](file:///f:/code/MyPython/tiny-frontend/backend/orm.py#L62) | 中 | ❌ 待修复 |
| 密码以明文存储 | [orm.py](file:///f:/code/MyPython/tiny-frontend/backend/orm.py#L30) | 高 | ❌ 待修复 |

---

## 前端状态表

| 功能模块 | 页面/组件 | 完成状态 | 负责文件 | 待办事项 |
|---|---|---|---|---|
| 登录页面 | Login | ❌ 待实现 | [src/](file:///f:/code/MyPython/tiny-frontend/temp-react/src) | 创建登录组件 |
| 注册页面 | Register | ❌ 待实现 | [src/](file:///f:/code/MyPython/tiny-frontend/temp-react/src) | 创建注册组件 |
| 用户信息页 | UserProfile | ✅ 已完成 | [UserProfile.jsx](file:///f:/code/MyPython/tiny-frontend/temp-react/src/UserProfile.jsx) | - |
| 主应用 | App | ✅ 已完成 | [App.jsx](file:///f:/code/MyPython/tiny-frontend/temp-react/src/App.jsx) | - |
| 路由配置 | Router | ❌ 待实现 | [src/](file:///f:/code/MyPython/tiny-frontend/temp-react/src) | 添加路由配置 |
| 全局状态 | Auth Store | ❌ 待实现 | [src/](file:///f:/code/MyPython/tiny-frontend/temp-react/src) | 创建登录态管理 |
| API请求封装 | API Service | ❌ 待实现 | [src/](file:///f:/code/MyPython/tiny-frontend/temp-react/src) | 封装 fetch/axios 请求 |
| 部门列表页 | Department List | ❌ 待实现 | [src/](file:///f:/code/MyPython/tiny-frontend/temp-react/src) | 创建部门列表组件 |
| 员工列表页 | Employee List | ❌ 待实现 | [src/](file:///f:/code/MyPython/tiny-frontend/temp-react/src) | 创建员工列表组件 |
| 考勤管理页 | Attendance | ❌ 待实现 | [src/](file:///f:/code/MyPython/tiny-frontend/temp-react/src) | 创建考勤管理组件 |

### 前端技术栈

| 技术 | 版本 | 状态 | 说明 |
|---|---|---|---|
| React | - | ✅ 已配置 | 使用 Vite + React 模板 |
| Vite | - | ✅ 已配置 | 构建工具 |
| 路由 | - | ❌ 待安装 | 建议使用 react-router-dom |
| 状态管理 | - | ❌ 待选择 | 可使用 Context API 或 Zustand |
| UI样式 | CSS | ✅ 已配置 | [index.css](file:///f:/code/MyPython/tiny-frontend/temp-react/src/index.css)、[App.css](file:///f:/code/MyPython/tiny-frontend/temp-react/src/App.css) |

---

## 接口对接状态

| 前端页面 | 后端接口 | 对接状态 | 备注 |
|---|---|---|---|
| 登录页 | `/login` | ❌ 待对接 | 前端页面未创建 |
| 注册页 | `/register` | ❌ 待对接 | 前后端均未完成 |
| 用户信息页 | `/employee` | ❌ 待对接 | 需根据登录态获取员工信息 |
| 部门列表页 | `/departments` | ❌ 待对接 | 前端页面未创建 |
| 员工列表页 | `/employee` | ❌ 待对接 | 前端页面未创建 |
| 考勤管理页 | `/attendance` | ❌ 待对接 | 前端页面未创建 |

---

## 开发进度统计

### 后端完成度

- **已完成**: 8 / 11 个接口/模块 (72.7%)
- **待实现**: 3 / 11 个接口/模块 (27.3%)
- **已知问题**: 5 个待修复

### 前端完成度

- **已完成**: 2 / 11 个页面/模块 (18.2%)
- **待实现**: 9 / 11 个页面/模块 (81.8%)

### 整体完成度

- **后端**: 🟢 73%
- **前端**: 🔴 18%
- **接口对接**: 🔴 0%