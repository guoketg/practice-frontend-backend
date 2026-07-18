from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy import Column, Integer, String, Date, DECIMAL, ForeignKey
from sqlalchemy import Enum as SAEnum
from pydantic import BaseModel
from sqlalchemy.orm.events import interfaces
from enum import Enum

class GenderEnum(str,Enum):
    MALE='男'
    FEMALE='女'

class StatusEnum(str,Enum):
    NORMAL='正常'
    LATE='迟到'
    EARLY='早退'
    ABSENT='旷工'

class Base(DeclarativeBase):
    pass

class Department(Base):
    __tablename__ = "department"

    dept_id:Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dept_name:Mapped[str] = mapped_column(String(30), nullable=False)
    dept_manager:Mapped[str] = mapped_column(String(50),nullable=False)
    dept_location:Mapped[str] = mapped_column(String(50),nullable=False)

class Employee(Base):
    __tablename__ = "employee"

    emp_id:Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    emp_name:Mapped[str] = mapped_column(String(50), nullable=False)
    gender:Mapped[GenderEnum] = mapped_column(String(10),nullable=False)
    age:Mapped[int] = mapped_column(Integer,nullable=False)
    department:Mapped[str] = mapped_column(String(30),nullable=False)
    salary:Mapped[float] = mapped_column(DECIMAL(10, 2))
    hire_date:Mapped[Date] = mapped_column(Date)
    password:Mapped[str] = mapped_column(String(50),nullable=False)

    dept_id:Mapped[int] = mapped_column(Integer, ForeignKey("department.dept_id"), nullable=True)

class Attendance(Base):
    __tablename__ = "attendance"

    att_id:Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    emp_id:Mapped[int] = mapped_column(Integer,ForeignKey('employee.emp_id'))
    work_date:Mapped[Date] = mapped_column(Date, nullable=False)
    work_hours:Mapped[float] = mapped_column(DECIMAL(4,1),nullable=False)
    status:Mapped[StatusEnum] = mapped_column(String(10), nullable=False)

    employee_id:Mapped[int] = mapped_column(Integer, ForeignKey("employee.emp_id"), nullable=False)

class DepartmentCreate(BaseModel):
    dept_id:int
    dept_name:str
    dept_manager:str
    dept_location:str

class EmployeeCreate(BaseModel):
    emp_id:int
    emp_name:str
    gender:GenderEnum
    age:int
    department:str
    salary:float
    hire_date:str
    password:str

    dept_id:int

class AttendanceCreate(BaseModel):
    emp_id:int
    work_date:str
    work_hours:float
    status:StatusEnum

class EmployeeUpdate(BaseModel):
    # emp_id:int | None = None
    emp_name:str | None =None
    gender:GenderEnum | None = None
    age:int | None = None
    department:str | None = None
    salary:float | None = None
    hire_date:str   | None = None
    password:str | None = None

    dept_id:int | None = None

class DepartmentUpdate(BaseModel):
    # dept_id:int | None = None
    dept_name:str | None = None
    dept_manager:str | None = None
    dept_location:str | None = None

class AttendanceUpdate(BaseModel):
    # att_id:int | None = None
    # emp_id:int | None = None
    work_date:str | None = None
    work_hours:float | None = None
    status:StatusEnum | None = None

class LoginRequest(BaseModel):
    emp_id:int
    password:str

class RegisterRequest(BaseModel):
    emp_id:int
    emp_name:str
    password:str
    dept_id:int
    gender:GenderEnum
    age:int
    department:str
    salary:float
    hire_date:str



