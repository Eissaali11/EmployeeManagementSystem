#!/usr/bin/env python3
"""
إنشاء ملف Excel تجريبي لاختبار استيراد أرقام الهواتف
"""

import pandas as pd

# إنشاء بيانات تجريبية
phone_data = {
    'phone_number': [
        '966501234567',
        '966522334455',
        '966533445566',
        '966544556677',
        '966555667788',
        '966566778899',
        '966577889900',
        '966588990011',
        '966599001122',
        '966500112233'
    ],
    'description': [
        'أحمد محمد',
        'فاطمة علي',
        'خالد السالم',
        'نورا أحمد',
        'محمد عبدالله',
        'سارة محمد',
        'عبدالرحمن خالد',
        'مريم يوسف',
        'عمر الحسن',
        'هند عبدالعزيز'
    ]
}

# إنشاء DataFrame
df = pd.DataFrame(phone_data)

# حفظ إلى ملف Excel
df.to_excel('test_phone_numbers.xlsx', index=False, sheet_name='أرقام الهواتف')

print("تم إنشاء ملف test_phone_numbers.xlsx بنجاح!")
print(f"عدد الأرقام: {len(df)}")
print("\nالأرقام المُنشأة:")
for idx, row in df.iterrows():
    print(f"- {row['phone_number']} ({row['description']})")