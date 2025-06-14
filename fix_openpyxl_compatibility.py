#!/usr/bin/env python3
"""
إصلاح توافق openpyxl بإزالة جميع استخدامات xlsxwriter
"""

def fix_openpyxl_compatibility():
    """إزالة جميع استخدامات xlsxwriter والتنسيق المتقدم"""
    
    with open('routes/vehicles.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # إزالة جميع مراجع التنسيق xlsxwriter
    content = content.replace("header_format", "None")
    content = content.replace("data_format", "None")
    
    # إزالة جميع استخدامات worksheet.write و worksheet.set_column
    lines = content.split('\n')
    new_lines = []
    
    for line in lines:
        # تخطي السطور التي تحتوي على worksheet.write أو worksheet.set_column
        if ('worksheet.write(' in line or 
            'worksheet.set_column(' in line or
            'for col_num, value in enumerate(' in line or
            'for row in range(1, len(' in line or
            'for col in range(len(' in line):
            continue
        # تخطي السطور التي تحتوي على تعليقات التنسيق
        if ('# تطبيق التنسيق' in line):
            continue
        new_lines.append(line)
    
    content = '\n'.join(new_lines)
    
    # حفظ الملف المُحدث
    with open('routes/vehicles.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ تم إصلاح توافق openpyxl")

if __name__ == "__main__":
    fix_openpyxl_compatibility()