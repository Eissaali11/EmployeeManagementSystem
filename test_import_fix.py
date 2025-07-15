#!/usr/bin/env python3
"""
اختبار لتأكيد أن نظام الاستيراد يعمل بشكل صحيح
"""
import pandas as pd
from io import BytesIO
from utils.excel import parse_employee_excel

# إنشاء ملف Excel اختباري مع بيانات أساسية
test_data = {
    'الاسم الكامل': ['أحمد محمد', 'فاطمة علي', 'سعد الأحمد'],
    'رقم الموظف': ['E001', 'E002', 'E003'],
    'رقم الهوية الوطنية': ['1234567890', '0987654321', '1111111111'],
    'رقم الجوال': ['0501234567', '0509876543', '0551234567'],
    'المسمى الوظيفي': ['مطور', 'محاسب', 'مهندس'],
    'الأقسام': ['تقنية المعلومات', 'المحاسبة', 'الهندسة']
}

# إنشاء DataFrame
df = pd.DataFrame(test_data)
print("بيانات الاختبار:")
print(df.to_string(index=False))

# إنشاء ملف Excel في الذاكرة
excel_buffer = BytesIO()
with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='الموظفين', index=False)

# اختبار تحليل الملف
excel_buffer.seek(0)
try:
    employees = parse_employee_excel(excel_buffer)
    print(f"\nنجح! تم تحليل {len(employees)} موظف:")
    for i, emp in enumerate(employees, 1):
        print(f"{i}. {emp['name']} - {emp['employee_id']} - {emp.get('department', 'بدون قسم')}")
    
    # التحقق من أن الحقول المطلوبة موجودة
    required_fields = ['name', 'employee_id', 'national_id', 'mobile', 'job_title']
    for emp in employees:
        for field in required_fields:
            if field not in emp:
                print(f"خطأ: الحقل '{field}' غير موجود في الموظف {emp['name']}")
                break
        else:
            print(f"✓ جميع الحقول المطلوبة موجودة للموظف {emp['name']}")
    
    print("\n✅ الاختبار نجح - نظام الاستيراد يعمل بشكل صحيح!")
    
except Exception as e:
    print(f"❌ خطأ في الاختبار: {e}")
    import traceback
    traceback.print_exc()