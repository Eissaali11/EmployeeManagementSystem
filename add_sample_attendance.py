#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import app, db
from models import Employee, Attendance
from datetime import datetime, date, time

def add_sample_attendance():
    with app.app_context():
        # الحصول على أول موظف
        employee = Employee.query.first()
        if not employee:
            print("لا يوجد موظفين في قاعدة البيانات")
            return
        
        print(f'وجدنا الموظف: {employee.name} (الرقم: {employee.id})')
        
        # إضافة سجل حضور لليوم الحالي
        today = date.today()
        attendance = Attendance(
            employee_id=employee.id,
            date=today,
            check_in=time(8, 0),
            check_out=time(17, 0),
            status='present'
        )
        
        # حفظ السجل
        db.session.add(attendance)
        db.session.commit()
        
        print(f'تمت إضافة سجل الحضور: {attendance.id} للتاريخ {attendance.date}')
        
        # طباعة جميع سجلات حضور الموظف
        attendances = Attendance.query.filter_by(employee_id=employee.id).all()
        print(f"عدد سجلات الحضور للموظف {employee.name}: {len(attendances)}")
        
        for a in attendances:
            print(f"السجل {a.id}: التاريخ {a.date}, الحالة: {a.status}")

if __name__ == "__main__":
    add_sample_attendance()