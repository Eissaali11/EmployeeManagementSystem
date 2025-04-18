"""
تصحيح أخطاء ضبط أعمدة Excel في ملفات التقارير
"""

import re
import os

def fix_excel_adjustment():
    """تصحيح جميع أخطاء ضبط عرض الأعمدة في ملف routes/reports.py"""
    
    # قراءة محتوى ملف التقارير
    with open('routes/reports.py', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # النمط الذي سنبحث عنه لاستبداله
    pattern = r"""    # ضبط عرض الأعمدة
    for col in sheet\.columns:
        max_length = 0
        column = col\[0\]\.column_letter  # الحصول على حرف العمود
        for cell in col:
            try:
                if len\(str\(cell\.value\)\) > max_length:
                    max_length = len\(str\(cell\.value\)\)
            except:
                pass
        adjusted_width = \(max_length \+ 2\) \* 1\.2
        sheet\.column_dimensions\[column\]\.width = adjusted_width"""
    
    # الكود الجديد للاستبدال
    replacement = """    # ضبط عرض الأعمدة باستخدام الدالة المساعدة
    from utils.excel_utils import adjust_column_width
    adjust_column_width(sheet)"""
    
    # استبدال جميع الحالات
    new_content = re.sub(pattern, replacement, content)
    
    # كتابة المحتوى الجديد إلى الملف
    with open('routes/reports.py', 'w', encoding='utf-8') as file:
        file.write(new_content)
    
    print("تم إصلاح جميع أماكن ضبط عرض الأعمدة في ملف routes/reports.py")

if __name__ == "__main__":
    # تنفيذ الإصلاح
    fix_excel_adjustment()