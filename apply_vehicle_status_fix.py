#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تطبيق إصلاح تحديث حالة السيارة التلقائي
Apply Automatic Vehicle Status Update Fix
"""

import re

def apply_fix():
    """تطبيق إصلاح تحديث حالة السيارة في ملف routes/mobile.py"""
    
    print("🔧 تطبيق إصلاح تحديث حالة السيارة التلقائي...")
    
    # قراءة الملف الحالي
    with open('routes/mobile.py', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # البحث عن موقع الإضافة المطلوب
    pattern = r'(\s+db\.session\.add\(handover\))\n(\s+db\.session\.commit\(\))'
    
    # الكود المطلوب إضافته
    fix_code = '''
            
            # تحديث حالة السيارة تلقائياً إلى "متاحة" بعد عملية الاستلام
            if handover_type == 'return':
                vehicle.status = 'available'
                vehicle.updated_at = datetime.utcnow()
                log_audit('update', 'vehicle_status', vehicle.id, 
                         f'تم تحديث حالة السيارة {vehicle.plate_number} إلى "متاحة" بعد عملية الاستلام')
            '''
    
    # تطبيق التعديل فقط على أول ظهور
    def replace_first(match):
        return match.group(1) + fix_code + '\n' + match.group(2)
    
    # تطبيق التعديل
    new_content, count = re.subn(pattern, replace_first, content, count=1)
    
    if count > 0:
        # كتابة الملف المحدث
        with open('routes/mobile.py', 'w', encoding='utf-8') as file:
            file.write(new_content)
        
        print("✅ تم تطبيق الإصلاح بنجاح!")
        print("🔄 الآن عند إجراء عملية استلام، ستتحديث حالة السيارة تلقائياً إلى 'متاحة'")
        return True
    else:
        print("⚠️ لم يتم العثور على المكان المحدد للتعديل أو تم تطبيق الإصلاح مسبقاً")
        return False

if __name__ == '__main__':
    apply_fix()