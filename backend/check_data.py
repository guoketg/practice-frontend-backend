import asyncio
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from orm import Employee, Attendance, Department

ASYNC_DATABASE_URL = 'mysql+aiomysql://root:123456@localhost:3306/company_hr_db'
engine = create_async_engine(ASYNC_DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def main():
    async with AsyncSessionLocal() as session:
        # employee
        result = await session.execute(select(func.count()).select_from(Employee))
        print(f"员工总数: {result.scalar()}")

        result = await session.execute(select(Employee).order_by(Employee.emp_id))
        for e in result.scalars().all():
            print(f"  {e.emp_id} | {e.emp_name} | {e.department}")

        # attendance
        result = await session.execute(select(func.count()).select_from(Attendance))
        print(f"\n考勤记录总数: {result.scalar()}")

        result = await session.execute(select(Attendance).order_by(Attendance.att_id))
        for a in result.scalars().all():
            print(f"  {a.att_id} | emp_id={a.emp_id} | {a.work_date} | {a.status} | {a.work_hours}h")


if __name__ == "__main__":
    asyncio.run(main())
