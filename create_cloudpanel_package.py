#!/usr/bin/env python3
"""
إنشاء حزمة نشر CloudPanel لنظام نُظم
"""

import os
import shutil
import tarfile
import zipfile
from datetime import datetime

def create_cloudpanel_package():
    """إنشاء حزمة النشر لـ CloudPanel"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    package_name = f"nuzum_cloudpanel_{timestamp}"
    
    # إنشاء مجلد مؤقت للحزمة
    temp_dir = f"temp_{package_name}"
    os.makedirs(temp_dir, exist_ok=True)
    
    # قائمة الملفات والمجلدات المطلوبة
    files_to_include = [
        'app.py',
        'main.py',
        'models.py',
        'cloudpanel_requirements.txt',
        'cloudpanel_deploy.sh',
        'cloudpanel_env_template.txt',
        'cloudpanel_setup_guide.md',
        '.env.example',
        'Cairo.ttf',
        'local_requirements.txt',
        '.env.local',
        'run_local.py',
        'create_test_data.py',
        'setup_local.bat',
        'setup_local.sh',
        'LOCAL_SETUP_GUIDE.md',
        'QUICK_START.md'
    ]
    
    folders_to_include = [
        'routes',
        'templates',
        'static',
        'forms',
        'utils',
        'core',
        'services',
        'functions'
    ]
    
    print(f"إنشاء حزمة النشر: {package_name}")
    
    # نسخ الملفات
    for file_name in files_to_include:
        if os.path.exists(file_name):
            shutil.copy2(file_name, temp_dir)
            print(f"تم نسخ الملف: {file_name}")
        else:
            print(f"تحذير: الملف غير موجود: {file_name}")
    
    # نسخ المجلدات
    for folder_name in folders_to_include:
        if os.path.exists(folder_name):
            shutil.copytree(folder_name, os.path.join(temp_dir, folder_name))
            print(f"تم نسخ المجلد: {folder_name}")
        else:
            print(f"تحذير: المجلد غير موجود: {folder_name}")
    
    # إنشاء ملف README للنشر
    readme_content = """# نُظم - نظام إدارة الموظفين
# CloudPanel Deployment Package

## محتويات الحزمة:

### للنشر على الخادم (CloudPanel):
1. cloudpanel_requirements.txt - متطلبات Python للخادم
2. cloudpanel_deploy.sh - سكريبت النشر الآلي
3. cloudpanel_env_template.txt - قالب متغيرات البيئة
4. cloudpanel_setup_guide.md - دليل النشر المفصل

### للتطوير المحلي (CURSOR/VS Code):
1. local_requirements.txt - متطلبات Python للتطوير
2. .env.local - متغيرات البيئة المحلية
3. run_local.py - تشغيل النظام محلياً
4. create_test_data.py - إنشاء بيانات تجريبية
5. setup_local.bat/sh - إعداد آلي للتطوير
6. LOCAL_SETUP_GUIDE.md - دليل التطوير المحلي
7. QUICK_START.md - بدء سريع

## بيانات تسجيل الدخول الافتراضية:
- المدير: skrkhtan@gmail.com
- مدير القسم: z.alhamdani@rassaudi.com
- بوابة الموظف: رقم 4298 / هوية 2489682019

## خطوات سريعة للنشر على الخادم:
1. رفع الملفات لمجلد الموقع في CloudPanel
2. تشغيل: chmod +x cloudpanel_deploy.sh && ./cloudpanel_deploy.sh
3. تكوين متغيرات البيئة في ملف .env
4. إنشاء قاعدة البيانات PostgreSQL
5. تشغيل الخدمة

## خطوات سريعة للتطوير المحلي:
### Windows:
setup_local.bat

### macOS/Linux:
chmod +x setup_local.sh && ./setup_local.sh

### يدوياً:
python run_local.py

للمزيد من التفاصيل، راجع الملفات المرفقة.
"""
    
    with open(os.path.join(temp_dir, 'README_DEPLOYMENT.txt'), 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    # إنشاء ملف إعداد سريع
    quick_setup = """#!/bin/bash
# إعداد سريع لـ CloudPanel

echo "=== إعداد سريع لنظام نُظم ==="

# تعيين الصلاحيات
chmod +x cloudpanel_deploy.sh

# نسخ قالب البيئة
cp cloudpanel_env_template.txt .env

echo "تم الإعداد الأولي"
echo "يرجى تعديل ملف .env بالقيم الفعلية"
echo "ثم تشغيل: ./cloudpanel_deploy.sh"
"""
    
    with open(os.path.join(temp_dir, 'quick_setup.sh'), 'w', encoding='utf-8') as f:
        f.write(quick_setup)
    
    os.chmod(os.path.join(temp_dir, 'quick_setup.sh'), 0o755)
    
    # إنشاء أرشيف tar.gz
    tar_filename = f"{package_name}.tar.gz"
    with tarfile.open(tar_filename, "w:gz") as tar:
        tar.add(temp_dir, arcname=package_name)
    
    # إنشاء أرشيف zip
    zip_filename = f"{package_name}.zip"
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, temp_dir)
                zipf.write(file_path, os.path.join(package_name, arc_name))
    
    # حذف المجلد المؤقت
    shutil.rmtree(temp_dir)
    
    print(f"\n=== تم إنشاء حزم النشر بنجاح ===")
    print(f"📦 حزمة tar.gz: {tar_filename}")
    print(f"📦 حزمة zip: {zip_filename}")
    print(f"📄 حجم tar.gz: {os.path.getsize(tar_filename) / 1024 / 1024:.2f} MB")
    print(f"📄 حجم zip: {os.path.getsize(zip_filename) / 1024 / 1024:.2f} MB")
    
    return tar_filename, zip_filename

if __name__ == "__main__":
    create_cloudpanel_package()