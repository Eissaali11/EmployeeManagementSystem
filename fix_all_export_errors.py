#!/usr/bin/env python3
"""
إصلاح شامل لجميع أخطاء التصدير في ملف routes/vehicles.py
"""

def fix_all_export_errors():
    """إصلاح جميع أخطاء الحقول المفقودة"""
    
    # قراءة الملف الحالي
    with open('routes/vehicles.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # إصلاحات شاملة للحقول المفقودة
    
    # 1. إصلاح حقول VehicleRental
    content = content.replace("'اسم المستأجر': rental.renter_name or ''", "'اسم المؤجر': rental.lessor_name or ''")
    content = content.replace("'رقم الهاتف': rental.phone_number or ''", "'معلومات الاتصال': rental.lessor_contact or ''")
    content = content.replace("'القيمة الشهرية': rental.monthly_rate or 0", "'التكلفة الشهرية': rental.monthly_cost or 0")
    content = content.replace("'جهة الاتصال': rental.contact_number or ''", "'معلومات الاتصال': rental.lessor_contact or ''")
    
    # 2. إصلاح حقول VehicleWorkshop
    content = content.replace("'الإجراءات المتخذة': workshop.actions_taken or ''", "'الوصف': workshop.description or ''")
    content = content.replace("'وصف المشكلة': workshop.issue_description or ''", "'الوصف': workshop.description or ''")
    
    # 3. إزالة الحقول غير الموجودة في Employee
    content = content.replace("'القسم': employee.department.name if employee and employee.department else '',\n", "")
    
    # 4. إزالة مراجع للحقول غير الموجودة في Vehicle
    content = content.replace("vehicle.vin", "vehicle.plate_number")
    content = content.replace("vehicle.department", "''")
    content = content.replace("vehicle.insurance_expiry", "vehicle.inspection_expiry_date")
    
    # 5. إصلاح مراجع cost في VehicleRental
    content = content.replace("VehicleRental.cost", "VehicleRental.monthly_cost")
    
    # حفظ الملف المُحدث
    with open('routes/vehicles.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ تم إصلاح جميع أخطاء الحقول المفقودة في وظائف التصدير")

if __name__ == "__main__":
    fix_all_export_errors()