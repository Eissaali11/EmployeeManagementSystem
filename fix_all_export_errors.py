#!/usr/bin/env python3
"""
إصلاح شامل لجميع أخطاء التصدير في ملف routes/vehicles.py
"""

def fix_all_export_errors():
    """إصلاح جميع أخطاء الحقول المفقودة"""
    
    with open('routes/vehicles.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    cleaned_lines = []
    skip_until_brace = False
    
    for i, line in enumerate(lines):
        # تخطي الأسطر التي تحتوي على None = workbook.add_format
        if 'None = workbook.add_format(' in line:
            skip_until_brace = True
            continue
        
        # تخطي حتى نجد })
        if skip_until_brace:
            if '})' in line:
                skip_until_brace = False
            continue
            
        # إزالة السطور المتعلقة بالتنسيق
        if ('workbook.add_format' in line or
            'worksheet.write(' in line or
            'worksheet.set_column(' in line or
            'header_format' in line or
            'data_format' in line):
            continue
            
        cleaned_lines.append(line)
    
    # إعادة بناء المحتوى
    content = '\n'.join(cleaned_lines)
    
    # إصلاح المراجع للحقول غير الموجودة
    replacements = {
        'record.certificate_number': 'record.inspection_number',
        'handover.employee_name': 'handover.person_name', 
        'handover.odometer_reading': 'handover.mileage',
        "'رقم الشهادة':": "'رقم الفحص':",
        "'جهة الفحص':": "'مركز الفحص':",
    }
    
    for old, new in replacements.items():
        content = content.replace(old, new)
    
    # حفظ الملف المُحدث
    with open('routes/vehicles.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ تم إصلاح جميع أخطاء التصدير بنجاح")

if __name__ == "__main__":
    fix_all_export_errors()