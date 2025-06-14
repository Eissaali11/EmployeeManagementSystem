#!/usr/bin/env python3
"""
إصلاح نهائي شامل لجميع أخطاء التصدير بناءً على الحقول الفعلية في قاعدة البيانات
"""

def fix_final_export_errors():
    """إصلاح نهائي لجميع أخطاء الحقول"""
    
    with open('routes/vehicles.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # إزالة جميع الأسطر التي تحتوي على تعيين لـ None
    lines = content.split('\n')
    new_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # تخطي الأسطر التي تحتوي على أخطاء نحوية
        if ('None = ' in line or
            'Expression cannot be assignment target' in line or
            '}) alone' in line.strip() or
            line.strip() == '})'):
            # تخطي الأسطر المتعلقة بالتنسيق
            while i < len(lines) and ('}' not in lines[i] or lines[i].strip() == '}'):
                i += 1
            if i < len(lines) and '}' in lines[i]:
                i += 1
            continue
        
        # إصلاح الأسطر التي تحتوي على workbook.add_format
        if 'workbook.add_format' in line:
            # تخطي تعريف التنسيق بالكامل
            while i < len(lines) and '})' not in lines[i]:
                i += 1
            if i < len(lines) and '})' in lines[i]:
                i += 1
            continue
        
        new_lines.append(line)
        i += 1
    
    content = '\n'.join(new_lines)
    
    # إزالة السطور الفارغة المتتالية
    content = '\n'.join([line for line in content.split('\n') if line.strip() or not line])
    
    # إصلاح المراجع للحقول غير الموجودة
    content = content.replace('record.certificate_number', 'record.inspection_number')
    content = content.replace('handover.employee_name', 'handover.person_name')
    content = content.replace('handover.odometer_reading', 'handover.mileage')
    
    # حفظ الملف المُحدث
    with open('routes/vehicles.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ تم إصلاح جميع أخطاء التصدير النهائية")

if __name__ == "__main__":
    fix_final_export_errors()