import asyncio
from datetime import date
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from orm import Employee, Attendance

ASYNC_DATABASE_URL = 'mysql+aiomysql://root:123456@localhost:3306/company_hr_db'
engine = create_async_engine(ASYNC_DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def main():
    async with AsyncSessionLocal() as session:
        # 查现有员工
        result = await session.execute(select(Employee).order_by(Employee.emp_id))
        emps = result.scalars().all()
        emp_ids = [e.emp_id for e in emps]

        # 考勤数据: (emp_id, work_date, work_hours, status)
        attendance_data = [
            # 张三 - 技术部 (1001)
            (1001, date(2024, 7, 10), 8.0, "正常"),
            (1001, date(2024, 7, 11), 7.5, "早退"),
            (1001, date(2024, 7, 12), 8.0, "正常"),
            (1001, date(2024, 7, 13), 8.0, "正常"),
            (1001, date(2024, 7, 14), 0.0, "旷工"),

            # 李四 - 技术部 (1002)
            (1002, date(2024, 7, 10), 8.0, "正常"),
            (1002, date(2024, 7, 11), 8.0, "正常"),
            (1002, date(2024, 7, 12), 8.5, "正常"),
            (1002, date(2024, 7, 13), 8.0, "正常"),
            (1002, date(2024, 7, 14), 7.0, "早退"),

            # 王小明 - 技术部 (1003)
            (1003, date(2024, 7, 10), 8.0, "正常"),
            (1003, date(2024, 7, 11), 8.0, "迟到"),
            (1003, date(2024, 7, 12), 8.0, "正常"),
            (1003, date(2024, 7, 13), 8.0, "正常"),
            (1003, date(2024, 7, 14), 8.0, "正常"),

            # 赵丽 - 市场部 (1004)
            (1004, date(2024, 7, 10), 8.0, "正常"),
            (1004, date(2024, 7, 11), 8.0, "正常"),
            (1004, date(2024, 7, 12), 8.0, "正常"),
            (1004, date(2024, 7, 13), 8.0, "迟到"),
            (1004, date(2024, 7, 14), 8.0, "正常"),

            # 钱枫 - 市场部 (1005)
            (1005, date(2024, 7, 10), 8.0, "正常"),
            (1005, date(2024, 7, 11), 8.0, "正常"),
            (1005, date(2024, 7, 12), 0.0, "旷工"),
            (1005, date(2024, 7, 13), 8.0, "正常"),
            (1005, date(2024, 7, 14), 8.0, "正常"),

            # 孙悦 - 人事部 (1006)
            (1006, date(2024, 7, 10), 8.0, "正常"),
            (1006, date(2024, 7, 11), 8.0, "正常"),
            (1006, date(2024, 7, 12), 8.0, "正常"),
            (1006, date(2024, 7, 13), 6.5, "早退"),
            (1006, date(2024, 7, 14), 8.0, "正常"),

            # 周杰 - 人事部 (1007)
            (1007, date(2024, 7, 10), 8.0, "迟到"),
            (1007, date(2024, 7, 11), 8.0, "正常"),
            (1007, date(2024, 7, 12), 8.0, "正常"),
            (1007, date(2024, 7, 13), 8.0, "正常"),
            (1007, date(2024, 7, 14), 8.0, "正常"),

            # 吴芳 - 财务部 (1008)
            (1008, date(2024, 7, 10), 8.0, "正常"),
            (1008, date(2024, 7, 11), 8.0, "正常"),
            (1008, date(2024, 7, 12), 8.0, "正常"),
            (1008, date(2024, 7, 13), 8.0, "正常"),
            (1008, date(2024, 7, 14), 8.0, "正常"),

            # 郑强 - 运营部 (1009)
            (1009, date(2024, 7, 10), 8.0, "正常"),
            (1009, date(2024, 7, 11), 7.0, "早退"),
            (1009, date(2024, 7, 12), 8.0, "正常"),
            (1009, date(2024, 7, 13), 0.0, "旷工"),
            (1009, date(2024, 7, 14), 8.0, "正常"),

            # 冯雪 - 运营部 (1010)
            (1010, date(2024, 7, 10), 8.0, "正常"),
            (1010, date(2024, 7, 11), 8.0, "正常"),
            (1010, date(2024, 7, 12), 8.0, "迟到"),
            (1010, date(2024, 7, 13), 8.0, "正常"),
            (1010, date(2024, 7, 14), 8.0, "正常"),
        ]

        for (emp_id, work_date, work_hours, status) in attendance_data:
            att = Attendance(
                emp_id=emp_id,
                work_date=work_date,
                work_hours=work_hours,
                status=status,
                employee_id=emp_id,
            )
            session.add(att)

        await session.commit()
        print(f"插入 {len(attendance_data)} 条考勤记录!")

        # 验证
        result = await session.execute(select(func.count()).select_from(Attendance))
        total = result.scalar()
        print(f"考勤记录总数: {total}")

        # 按状态统计
        result = await session.execute(
            select(Attendance.status, func.count())
            .group_by(Attendance.status)
        )
        print("\n状态统计:")
        for row in result.all():
            print(f"  {row[0]}: {row[1]}条")


if __name__ == "__main__":
    asyncio.run(main())
