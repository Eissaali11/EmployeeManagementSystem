#!/usr/bin/env python3
"""
إزالة جميع التأثيرات ثلاثية الأبعاد من ملفات النظام
"""

import os
import re

def remove_3d_effects_from_file(file_path):
    """إزالة التأثيرات ثلاثية الأبعاد من ملف واحد"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # إزالة التأثيرات ثلاثية الأبعاد من CSS
        content = re.sub(r'transform-style:\s*preserve-3d;?', '', content)
        content = re.sub(r'perspective\([^)]*\)', '', content)
        
        # إزالة كود JavaScript للتأثيرات ثلاثية الأبعاد
        content = re.sub(r'const rotateX[^;]*;', '', content)
        content = re.sub(r'const rotateY[^;]*;', '', content)
        content = re.sub(r'rotateX\([^)]*\)', '', content)
        content = re.sub(r'rotateY\([^)]*\)', '', content)
        content = re.sub(r'translateZ\([^)]*\)', '', content)
        
        # إزالة تأثيرات hover ثلاثية الأبعاد
        content = re.sub(r'card\.style\.transform\s*=\s*`perspective\([^`]*`[^;]*;', 
                        "card.style.transform = 'translateY(-5px)';", content)
        
        # إزالة تعليقات التأثيرات ثلاثية الأبعاد
        content = re.sub(r'//.*3D.*\n', '', content)
        content = re.sub(r'/\*.*3D.*\*/', '', content, flags=re.DOTALL)
        
        # تنظيف الفراغات الزائدة
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        
        # كتابة المحتوى المحدث فقط إذا تغير
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"تم تحديث: {file_path}")
        
    except Exception as e:
        print(f"خطأ في معالجة {file_path}: {e}")

def main():
    """إزالة جميع التأثيرات ثلاثية الأبعاد من النظام"""
    templates_dir = 'templates/system_admin'
    
    if not os.path.exists(templates_dir):
        print(f"المجلد غير موجود: {templates_dir}")
        return
    
    html_files = []
    for root, dirs, files in os.walk(templates_dir):
        for file in files:
            if file.endswith('.html'):
                html_files.append(os.path.join(root, file))
    
    print(f"تم العثور على {len(html_files)} ملف HTML")
    
    for file_path in html_files:
        remove_3d_effects_from_file(file_path)
    
    print("تم الانتهاء من إزالة جميع التأثيرات ثلاثية الأبعاد")

if __name__ == "__main__":
    main()