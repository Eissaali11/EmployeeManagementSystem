#!/usr/bin/env python3
import pandas as pd
from io import BytesIO

# إنشاء ملف Excel اختباري للموظفين
test_data = {
    'الاسم الكامل': ['محمد أحمد علي', 'فاطمة سالم محمد', 'عبدالله العبدالرحمن'],
    'رقم الموظف': ['EMP001', 'EMP002', 'EMP003'],
    'رقم الهوية الوطنية': ['1234567890', '0987654321', '5555555555'],
    'رقم الجوال': ['0501234567', '0509876543', '0551234567'],
    'المسمى الوظيفي': ['مطور برمجيات', 'محاسب', 'مهندس'],
    'الحالة الوظيفية': ['active', 'active', 'active'],
    'الموقع': ['الرياض', 'جدة', 'الدمام'],
    'المشروع': ['مشروع الرياض', 'مشروع جدة', 'مشروع الدمام'],
    'البريد الإلكتروني': ['mohamed@test.com', 'fatima@test.com', 'abdullah@test.com'],
    'الأقسام': ['تقنية المعلومات', 'المحاسبة', 'الهندسة'],
    'الجنسية': ['سعودي', 'سعودي', 'سعودي'],
    'ملاحظات': ['موظف متميز', 'موظف جديد', 'موظف مخضرم']
}

# إنشاء DataFrame
df = pd.DataFrame(test_data)

# حفظ الملف
with pd.ExcelWriter('test_employees.xlsx', engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='الموظفين', index=False)

print("تم إنشاء ملف test_employees.xlsx بنجاح!")
print(f"الملف يحتوي على {len(df)} موظف")
print("الأعمدة الموجودة:", df.columns.tolist())