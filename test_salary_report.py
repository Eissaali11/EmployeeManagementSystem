#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from utils.fpdf_arabic import generate_salary_report_pdf
from datetime import datetime

def test_salary_report():
    # إنشاء بيانات تجريبية
    salaries_data = [
        {
            'employee_name': 'أحمد محمد',
            'employee_id': 'EMP001',
            'basic_salary': 5000,
            'allowances': 1000,
            'bonus': 500,
            'deductions': 200,
            'net_salary': 6300
        },
        {
            'employee_name': 'محمد أحمد',
            'employee_id': 'EMP002',
            'basic_salary': 6000,
            'allowances': 1200,
            'bonus': 600,
            'deductions': 300,
            'net_salary': 7500
        },
        {
            'employee_name': 'فاطمة علي',
            'employee_id': 'EMP003',
            'basic_salary': 4500,
            'allowances': 900,
            'bonus': 400,
            'deductions': 150,
            'net_salary': 5650
        }
    ]
    
    # إنشاء تقرير الرواتب
    pdf_bytes = generate_salary_report_pdf(salaries_data, 'أبريل', '2025')
    
    # حفظ الملف
    with open('test_salary_report.pdf', 'wb') as f:
        f.write(pdf_bytes)
    
    print('تم إنشاء تقرير الرواتب بصيغة PDF بنجاح: test_salary_report.pdf')

if __name__ == '__main__':
    test_salary_report()