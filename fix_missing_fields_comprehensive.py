#!/usr/bin/env python3
"""
إصلاح شامل لجميع الحقول المفقودة في وظائف التصدير
"""

def fix_missing_fields():
    """إصلاح جميع الحقول المفقودة في routes/vehicles.py"""
    
    # قراءة الملف الحالي
    with open('routes/vehicles.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # الإصلاحات الشاملة بناءً على الحقول الفعلية في قاعدة البيانات
    
    # 1. إصلاح حقول VehiclePeriodicInspection
    content = content.replace("record.certificate_number", "record.inspection_number")
    content = content.replace("'رقم الشهادة':", "'رقم الفحص':")
    content = content.replace("'جهة الفحص':", "'مركز الفحص':")
    content = content.replace("record.cost or 0", "0")  # لا يوجد حقل cost في VehiclePeriodicInspection
    
    # 2. إصلاح حقول VehicleSafetyCheck
    content = content.replace("safety_check.inspector_name", "safety_check.inspector_name")
    content = content.replace("safety_check.certificate_number", "''")  # لا يوجد هذا الحقل
    
    # 3. إصلاح حقول VehicleHandover
    content = content.replace("handover.employee_name", "handover.person_name")
    content = content.replace("handover.odometer_reading", "handover.mileage")
    
    # 4. إصلاح حقول غير موجودة
    content = content.replace("record.department", "''")
    content = content.replace("employee.department.name if employee and employee.department else ''", "''")
    
    # حفظ الملف المُحدث
    with open('routes/vehicles.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ تم إصلاح جميع الحقول المفقودة في وظائف التصدير")

if __name__ == "__main__":
    fix_missing_fields()