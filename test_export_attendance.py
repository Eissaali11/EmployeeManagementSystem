#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import app, db
from models import Employee
from utils.excel import export_employee_attendance_to_excel
from datetime import datetime

def test_export_attendance():
    with app.app_context():
        # الحصول على أول موظف
        employee = Employee.query.filter_by(id=166).first()
        if not employee:
            print("لا يوجد موظف بهذا الرقم")
            return
        
        print(f'تصدير بيانات الحضور للموظف: {employee.name} (الرقم: {employee.id})')
        
        # الشهر والسنة الحاليين
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        print(f"تصدير البيانات للشهر {current_month} من سنة {current_year}")
        
        # تصدير البيانات
        try:
            output = export_employee_attendance_to_excel(employee, current_month, current_year)
            print("تم تصدير البيانات بنجاح")
            
            # طباعة معلومات المخرجات
            print(f"حجم الملف: {output.getbuffer().nbytes} بايت")
        except Exception as e:
            print(f"حدث خطأ أثناء تصدير البيانات: {str(e)}")
            import traceback
            print(traceback.format_exc())

if __name__ == "__main__":
    test_export_attendance()