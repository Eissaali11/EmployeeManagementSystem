#!/usr/bin/env python3
"""
اختبار سريع لإنشاء بيانات تجريبية لفحص السلامة
"""

from app import app, db
from models import Vehicle, SafetyInspection, Employee
from datetime import datetime, timedelta
import json

def create_test_safety_checks():
    """إنشاء بيانات تجريبية لفحص السلامة"""
    with app.app_context():
        # البحث عن أول سيارة في قاعدة البيانات
        vehicle = Vehicle.query.first()
        if not vehicle:
            print("لا توجد سيارات في قاعدة البيانات")
            return
        
        # البحث عن أول موظف
        employee = Employee.query.first()
        if not employee:
            print("لا توجد موظفين في قاعدة البيانات")
            return
        
        # إنشاء فحص سلامة تجريبي
        safety_check = SafetyInspection(
            vehicle_id=vehicle.id,
            employee_id=employee.employee_id,
            driver_name=employee.name,
            inspection_date=datetime.now(),
            issues_found="تم فحص السيارة بنجاح",
            recommendations="صيانة دورية كل 6 أشهر",
            approval_status='pending'
        )
        
        try:
            db.session.add(safety_check)
            db.session.commit()
            print(f"تم إنشاء فحص السلامة بنجاح - ID: {safety_check.id}")
            print(f"السيارة: {vehicle.plate_number}")
            print(f"الفاحص: {employee.name}")
            print(f"تاريخ الفحص: {safety_check.inspection_date}")
            print(f"المشاكل المكتشفة: {safety_check.issues_found}")
            print(f"التوصيات: {safety_check.recommendations}")
            print(f"حالة الموافقة: {safety_check.approval_status}")
            
        except Exception as e:
            print(f"خطأ في إنشاء البيانات: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    create_test_safety_checks()