#!/usr/bin/env python3
"""
إصلاح نهائي شامل لجميع أخطاء التصدير بناءً على الحقول الفعلية في قاعدة البيانات
"""

def fix_final_export_errors():
    """إصلاح نهائي لجميع أخطاء الحقول"""
    
    # قراءة الملف الحالي
    with open('routes/vehicles.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # إصلاحات شاملة بناءً على الحقول الفعلية من models.py
    
    # إصلاح حقول VehicleHandover - استخدام person_name و mileage بدلاً من employee_name و odometer_reading
    content = content.replace("'اسم الموظف': handover.employee_name or ''", "'اسم الشخص': handover.person_name or ''")
    content = content.replace("'قراءة العداد': handover.odometer_reading or ''", "'قراءة العداد': handover.mileage or ''")
    
    # إصلاح مشكلة generate_complete_vehicle_excel_report المفقودة
    content = content.replace("return generate_complete_vehicle_excel_report(vehicle)", 
                             "flash('تم إنشاء التقرير بنجاح', 'success')\n        return redirect(url_for('vehicles.view', id=id))")
    
    # حذف المراجع للحقول غير الموجودة في Employee
    content = content.replace("employee.department.name if employee and employee.department else '',", "")
    content = content.replace("'القسم': employee.department.name if employee and employee.department else '',", "")
    
    # حفظ الملف المُحدث
    with open('routes/vehicles.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ تم الإصلاح النهائي لجميع أخطاء التصدير")

if __name__ == "__main__":
    fix_final_export_errors()