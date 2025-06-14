#!/usr/bin/env python3
"""
سكريبت لإصلاح جميع الحقول المفقودة في وظائف تصدير Excel
"""

import re

def fix_export_functions():
    """إصلاح جميع وظائف التصدير"""
    
    # قراءة الملف
    with open('routes/vehicles.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # إصلاح حقول VehicleRental
    content = re.sub(
        r"'المستأجر': record\.renter_name or ''",
        "'اسم المؤجر': record.lessor_name or ''",
        content
    )
    
    content = re.sub(
        r"'جهة الاتصال': record\.contact_number or ''",
        "'معلومات الاتصال': record.lessor_contact or ''",
        content
    )
    
    content = re.sub(
        r"'التكلفة \(ريال\)': record\.cost or 0",
        "'التكلفة الشهرية (ريال)': record.monthly_cost or 0",
        content
    )
    
    # إصلاح حقول VehicleWorkshop
    content = re.sub(
        r"'الإجراءات المتخذة': workshop\.actions_taken or ''",
        "'وصف المشكلة': workshop.description or ''",
        content
    )
    
    content = re.sub(
        r"'وصف المشكلة': workshop\.issue_description or ''",
        "'وصف الإصلاح': workshop.description or ''",
        content
    )
    
    # إزالة الحقول غير الموجودة
    content = re.sub(
        r"'القسم': employee\.department\.name if employee and employee\.department else '',\n",
        "",
        content
    )
    
    # حفظ الملف المُحدث
    with open('routes/vehicles.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("تم إصلاح جميع الحقول المفقودة في وظائف التصدير")

if __name__ == "__main__":
    fix_export_functions()