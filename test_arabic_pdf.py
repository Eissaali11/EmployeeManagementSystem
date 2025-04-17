#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from utils.fpdf_arabic import generate_salary_notification_pdf
from datetime import datetime

def test_salary_notification():
    # إنشاء بيانات تجريبية
    data = {
        'employee_name': 'أحمد محمد',
        'employee_id': 'EMP001',
        'job_title': 'مدير تقني',
        'department_name': 'قسم تكنولوجيا المعلومات',
        'month_name': 'أبريل',
        'year': '2025',
        'basic_salary': 5000,
        'allowances': 1000,
        'bonus': 500,
        'deductions': 200,
        'net_salary': 6300,
        'notes': 'ملاحظة: هذا نموذج تجريبي فقط',
        'current_date': datetime.now().strftime('%Y-%m-%d')
    }
    
    # إنشاء إشعار الراتب
    pdf_bytes = generate_salary_notification_pdf(data)
    
    # حفظ الملف
    with open('test_arabic_salary.pdf', 'wb') as f:
        f.write(pdf_bytes)
    
    print('تم إنشاء ملف PDF بنجاح: test_arabic_salary.pdf')

if __name__ == '__main__':
    test_salary_notification()