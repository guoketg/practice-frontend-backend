from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine,async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy import Column,Integer,String,Date,DECIMAL,select
from contextlib import asynccontextmanager
from schemas import ApiResponse
from orm import Base,DepartmentCreate,Department,EmployeeCreate,Employee,Attendance,AttendanceCreate,LoginRequest,RegisterRequest,EmployeeUpdate,DepartmentUpdate,AttendanceUpdate
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Depends
from auth import hash_password,verify_password,create_access_token,get_current_emp
from sqlalchemy.orm.query import attributes

class base(DeclarativeBase):
    pass


ASYNC_DATABASE_URL='mysql+aiomysql://root:123456@localhost:3306/company_hr_db'
async_engine=create_async_engine(ASYNC_DATABASE_URL,echo=True)
AsyncSessionLocal=async_sessionmaker(async_engine,expire_on_commit=False)

@asynccontextmanager
async def lifespan(app):
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    
app=FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

@app.get('/')
async def root():
    return {'message':'hello world'}

@app.get(path='/hello/{name}')
async def hello(name:str):
    return {'message':f'hello {name}'}

@app.post('/departments')
async def create_department(body:DepartmentCreate):
    async with AsyncSessionLocal() as session:
        dept=Department(**body.model_dump())
        session.add(dept)
        await session.commit()
        await session.refresh(dept)
        return {'dept_id':dept.dept_id,'dept_name':dept.dept_name,'dept_manager':dept.dept_manager,'dept_location':dept.dept_location}

@app.get(path='/departments')
async def get_departments():
    async with AsyncSessionLocal() as session:
        result=await session.execute(select(Department))
        depts=result.scalars().all()
        return [{
            'dept_id':dept.dept_id,
            'dept_name':dept.dept_name,
            'dept_manager':dept.dept_manager,
            'dept_location':dept.dept_location
            } 
            for dept in depts]

# 只有登录的员工可以创建账号
@app.post(path='/employee')
async def create_employee(body:EmployeeCreate,emp_id:int=Depends(get_current_emp)):
    async with AsyncSessionLocal() as session:
        emp=Employee(**body.model_dump())
        session.add(emp)
        result=await session.commit()
        await session.refresh(emp)
        return {'emp_id':emp.emp_id,'emp_name':emp.emp_name,'gender':emp.gender,'age':emp.age,'department':emp.department,'salary':emp.salary,'hire_date':emp.hire_date}

@app.get(path='/employee')
async def get_employee():
    async with AsyncSessionLocal() as session:
        result=await session.execute(select(Employee))
        emps=result.scalars().all()
        return [{
            'emp_id':emp.emp_id,
            'emp_name':emp.emp_name,
            'gender':emp.gender,
            'age':emp.age,
            'department':emp.department,
            'salary':emp.salary,
            'hire_date':emp.hire_date
            } 
            for emp in emps]

@app.post(path='/attendance')
async def create_attendance(body:AttendanceCreate):
    async with AsyncSessionLocal() as session:
        atten=Attendance(**body.model_dump())
        session.add(atten)
        await session.commit()
        await session.refresh(atten)
        return {'attendance_id':atten.att_id,'emp_id':atten.emp_id,'attendance_date':atten.work_date,'attendance_status':atten.status}

@app.get(path='/attendance')
async def get_attendance():
    async with AsyncSessionLocal() as session:
        result=await session.execute(select(Attendance))
        attens=result.scalars().all()

        return [{
            'attendance_id':att.att_id,
            'emp_id':att.emp_id,
            'attendance_date':att.work_date,
            'attendance_status':att.status
            } 
            for att in attens]

@app.post('/login',response_model=ApiResponse)
async def login(body:LoginRequest):
    async with AsyncSessionLocal() as session:
        #拿到orm对象
        result=await session.execute(select(Employee).where(Employee.emp_id==body.emp_id))
        #拿到数据
        employee=result.scalar_one_or_none()

        if not employee:
            return ApiResponse(success=False,message='员工不存在')
        
        if employee.password!=body.password:
            return ApiResponse(success=False,message='密码错误')
        
        token =create_access_token(employee.emp_id)
        return ApiResponse(success=True,message='登录成功',data={
            'emp_id':employee.emp_id,
            'emp_name':employee.emp_name,
            'token':token
        })

@app.post('/register',response_model=ApiResponse)
async def register(body:RegisterRequest):

    async with AsyncSessionLocal() as session:
        result_emp_id=await session.execute(select(Employee).where(body.emp_id==Employee.emp_id))
        emp_id=result_emp_id.scalar_one_or_none()

        if emp_id:
            return ApiResponse(success=False,message='id已存在')
        
        employee_dict=body.model_dump()
        employee_dict['password']=hash_password(employee_dict['password'])
        employee=Employee(**employee_dict)
        
        session.add(employee)
        try:
            await session.commit()
        except Exception:
            await session.rollback()
            return ApiResponse(success=False,message='注册失败，请检查参数，如dept_id等')

        return ApiResponse(success=True,message='注册成功',data={'emp_name':employee.emp_name,'emp_id':employee.emp_id})

#防止员工信息被修改
@app.put(path='/employee/{emp_id}',response_model=ApiResponse)
async def update_employee(body:EmployeeUpdate,emp_id: int=Depends(get_current_emp)):
    async with AsyncSessionLocal() as session:
        result=await session.execute(select(Employee).where(Employee.emp_id==emp_id))
        employee=result.scalar_one_or_none()

        if not employee:
            return ApiResponse(success=False,message='emp_id不存在')
        
        update_data=body.model_dump(exclude_unset=True)

        # 选择性更新
        for key,value in update_data.items():
            setattr(employee,key,value)
        
        await session.commit()
        await session.refresh(employee)

        return ApiResponse(success=True,message='更新成功',data={
            'emp_id':employee.emp_id,'emp_name':employee.emp_name})

@app.put(path='/department/{dept_id}')
async def update_department(dept_id:int,body:DepartmentUpdate):
    async with AsyncSessionLocal() as session:
        result= await session.execute(select(Department).where(dept_id==Department.dept_id))
        department=result.scalar_one_or_none()

        if not department:
            return ApiResponse(success=False,message='id不存在')
        
        update_data=body.model_dump(exclude_unset=True)
        for key,value in update_data.items():
            setattr(department,key,value)
        
        await session.commit()
        await session.refresh(department)

        return ApiResponse(success=True,message='更新成功',data={
            'dept_id':department.dept_id,
            'dept_name':department.dept_name,
            'dept_manager':department.dept_manager,
            'dept_location':department.dept_location
        })

@app.put(path='/attendance/{att_id}')
async def update_attendance(att_id:int,body:AttendanceUpdate):
    async with AsyncSessionLocal() as session:
        result=await session.execute(select(Attendance).where(att_id==Attendance.att_id))
        attendance=result.scalar_one_or_none()

        if not attendance:
            return ApiResponse(success=False,message='att_id不存在')
        
        update_data=body.model_dump(exclude_unset=True)
        for key,value in update_data.items():
            setattr(attendance,key,value)
        
        await session.commit()
        await session.refresh(attendance)

        return ApiResponse(success=True,message='Attendance更新成功',data={
            'att_id':attendance.att_id,
            'emp_id':attendance.emp_id,
            'work_date':attendance.work_date,
            'work_hours':attendance.work_hours,
            'status':attendance.status
        })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8001, reload=True)