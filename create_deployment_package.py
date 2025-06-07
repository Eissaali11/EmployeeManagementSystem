#!/usr/bin/env python3
"""
إنشاء حزمة نشر مضغوطة لنظام نُظم
"""

import os
import shutil
import tarfile
from datetime import datetime

def create_deployment_package():
    """إنشاء حزمة النشر المضغوطة"""
    
    # اسم المجلد والملف المضغوط
    package_name = f"nuzum_deployment_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    package_dir = f"{package_name}"
    
    # إنشاء مجلد النشر
    os.makedirs(package_dir, exist_ok=True)
    
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
    
    print(f"إنشاء حزمة النشر: {package_name}")
    
    # نسخ الملفات والمجلدات
    for item in files_to_include:
        if os.path.exists(item):
            dest = os.path.join(package_dir, item)
            
            if os.path.isfile(item):
                # نسخ الملف
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.copy2(item, dest)
                print(f"✓ تم نسخ الملف: {item}")
                
            elif os.path.isdir(item):
                # نسخ المجلد
                shutil.copytree(item, dest, dirs_exist_ok=True)
                print(f"✓ تم نسخ المجلد: {item}")
        else:
            print(f"⚠ غير موجود: {item}")
    
    # إنشاء ملف تعليمات النشر
    instructions = """
# تعليمات نشر نظام نُظم

## المحتويات:
- ملفات التطبيق الأساسية
- تكوين Docker و Nginx
- نصوص النشر التلقائي
- دليل النشر المفصل

## خطوات النشر:
1. رفع الملفات للخادم
2. تعديل deployment/production.env
3. تشغيل: chmod +x deployment/deploy.sh
4. تشغيل: ./deployment/deploy.sh

## للمساعدة:
راجع QUICK_DEPLOY.md أو deployment/README_DEPLOYMENT.md
"""
    
    with open(os.path.join(package_dir, 'تعليمات_النشر.txt'), 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    # ضغط المجلد
    tar_filename = f"{package_name}.tar.gz"
    
    with tarfile.open(tar_filename, 'w:gz') as tar:
        tar.add(package_dir, arcname=package_name)
    
    # حذف المجلد المؤقت
    shutil.rmtree(package_dir)
    
    # معلومات الحزمة
    file_size = os.path.getsize(tar_filename)
    size_mb = file_size / (1024 * 1024)
    
    print(f"\n🎉 تم إنشاء حزمة النشر بنجاح!")
    print(f"📦 اسم الملف: {tar_filename}")
    print(f"📏 الحجم: {size_mb:.2f} MB")
    print(f"📍 المسار: {os.path.abspath(tar_filename)}")
    
    return tar_filename

if __name__ == "__main__":
    create_deployment_package()