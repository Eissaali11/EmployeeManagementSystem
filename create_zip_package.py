#!/usr/bin/env python3
"""
إنشاء حزمة نشر مضغوطة ZIP لنظام نُظم
"""

import os
import shutil
import zipfile
from datetime import datetime

def create_zip_package():
    """إنشاء حزمة النشر المضغوطة بصيغة ZIP"""
    
    # اسم المجلد والملف المضغوط
    package_name = f"nuzum_deployment_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    zip_filename = f"{package_name}.zip"
    
    # قائمة الملفات والمجلدات المطلوبة للنشر
    files_to_include = [
        # الملفات الأساسية
        'app.py',
        'main.py', 
        'models.py',
        'pyproject.toml',
        'Dockerfile',
        'docker-compose.yml',
        'nginx.conf',
        'QUICK_DEPLOY.md',
        'README.md',
        
        # مجلدات التطبيق
        'routes/',
        'templates/',
        'static/',
        'services/',
        'utils/',
        'forms/',
        'core/',
        'config/',
        
        # مجلد النشر
        'deployment/',
        
        # ملفات Firebase
        'firebase.json',
        'functions/',
        'public/',
        
        # الأصول
        'attached_assets/',
    ]
    
    print(f"إنشاء حزمة ZIP: {zip_filename}")
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        
        # إضافة ملف تعليمات النشر
        instructions = """
# تعليمات نشر نظام نُظم

## المحتويات:
- ملفات التطبيق الأساسية
- تكوين Docker و Nginx  
- نصوص النشر التلقائي
- دليل النشر المفصل

## خطوات النشر:
1. فك الضغط في مجلد على الخادم
2. تعديل deployment/production.env بالقيم الصحيحة
3. تشغيل: chmod +x deployment/deploy.sh
4. تشغيل: ./deployment/deploy.sh

## للمساعدة:
راجع QUICK_DEPLOY.md أو deployment/README_DEPLOYMENT.md

تاريخ الإنشاء: {}
""".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
        zipf.writestr(f"{package_name}/تعليمات_النشر.txt", instructions.encode('utf-8'))
        
        # نسخ الملفات والمجلدات
        for item in files_to_include:
            if os.path.exists(item):
                if os.path.isfile(item):
                    # إضافة الملف للـ ZIP
                    zipf.write(item, f"{package_name}/{item}")
                    print(f"✓ تم إضافة الملف: {item}")
                    
                elif os.path.isdir(item):
                    # إضافة المجلد وجميع محتوياته للـ ZIP
                    for root, dirs, files in os.walk(item):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arc_path = f"{package_name}/{file_path}"
                            zipf.write(file_path, arc_path)
                    print(f"✓ تم إضافة المجلد: {item}")
            else:
                print(f"⚠ غير موجود: {item}")
    
    # معلومات الحزمة
    file_size = os.path.getsize(zip_filename)
    size_mb = file_size / (1024 * 1024)
    
    print(f"\n🎉 تم إنشاء حزمة ZIP بنجاح!")
    print(f"📦 اسم الملف: {zip_filename}")
    print(f"📏 الحجم: {size_mb:.2f} MB")
    print(f"📍 المسار: {os.path.abspath(zip_filename)}")
    
    return zip_filename

if __name__ == "__main__":
    create_zip_package()