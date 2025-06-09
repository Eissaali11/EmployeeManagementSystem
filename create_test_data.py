#!/usr/bin/env python3
"""
إنشاء بيانات تجريبية لنظام نُظم للتطوير المحلي
"""

import os
from datetime import datetime, date
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv('.env.local')
os.environ.setdefault('DATABASE_URL', 'sqlite:///nuzum_local.db')

from app import app, db
from models import User, Department, Employee

def create_test_data():
    """إنشاء بيانات تجريبية"""
    
    with app.app_context():
        # حذف البيانات الموجودة
        db.drop_all()
        db.create_all()
        
        print("إنشاء البيانات التجريبية...")
        
        # إنشاء قسم تجريبي
        dept = Department(
            name="قسم تقنية المعلومات",
            description="قسم مختص بتقنية المعلومات والبرمجة"
        )
        db.session.add(dept)
        db.session.flush()
        
        # إنشاء مستخدم إداري
        admin_user = User(
            username="admin",
            email="admin@nuzum.com",
            first_name="المدير",
            last_name="العام",
            role="admin",
            is_active=True
        )
        admin_user.set_password("admin123")
        db.session.add(admin_user)
        
        # إنشاء موظف تجريبي
        employee = Employee(
            employee_id="EMP001",
            national_id="1234567890",
            name="أحمد محمد علي",
            mobile="0501234567",
            email="ahmed@nuzum.com",
            job_title="مطور برمجيات",
            status="active",
            department_id=dept.id,
            join_date=date(2024, 1, 15),
            nationality="سعودي",
            contract_type="saudi",
            basic_salary=8000.0
        )
        db.session.add(employee)
        
        # إنشاء موظف آخر للاختبار
        employee2 = Employee(
            employee_id="EMP002",
            national_id="0987654321",
            name="فاطمة أحمد السالم",
            mobile="0509876543",
            email="fatima@nuzum.com",
            job_title="محللة أنظمة",
            status="active",
            department_id=dept.id,
            join_date=date(2024, 2, 1),
            nationality="سعودية",
            contract_type="saudi",
            basic_salary=7500.0
        )
        db.session.add(employee2)
        
        # حفظ البيانات
        db.session.commit()
        
        print("✓ تم إنشاء البيانات التجريبية بنجاح")
        print("📋 بيانات تسجيل الدخول:")
        print("   المستخدم: admin")
        print("   كلمة المرور: admin123")
        print("📋 بيانات الموظفين للاختبار:")
        print("   الموظف 1: EMP001 / 1234567890")
        print("   الموظف 2: EMP002 / 0987654321")

if __name__ == "__main__":
    create_test_data()