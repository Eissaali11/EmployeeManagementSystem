#!/usr/bin/env python3
import pandas as pd
from io import BytesIO
from utils.excel import parse_employee_excel

# إنشاء ملف Excel اختباري
test_data = {
    'الاسم الكامل': ['محمد أحمد علي', 'فاطمة سالم'],
    'رقم الموظف': ['EMP001', 'EMP002'],
    'رقم الهوية الوطنية': ['1234567890', '0987654321'],
    'رقم الجوال': ['0501234567', '0509876543'],
    'المسمى الوظيفي': ['مطور', 'محاسب']
}

# إنشاء DataFrame
df = pd.DataFrame(test_data)

# إنشاء ملف Excel في الذاكرة
excel_buffer = BytesIO()
with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='الموظفين', index=False)

# محاولة قراءة الملف
excel_buffer.seek(0)
try:
    employees = parse_employee_excel(excel_buffer)
    print(f"Success! Parsed {len(employees)} employees:")
    for emp in employees:
        print(f"  - {emp['name']}: {emp['employee_id']}")
except Exception as e:
    print(f"Error: {e}")