#!/usr/bin/env python3
"""
سكريبت لإنشاء ملف مضغوط للنشر على الخادم
يقوم هذا السكريبت بجمع جميع الملفات اللازمة للنشر في ملف واحد مضغوط
"""

import os
import sys
import zipfile
import shutil
from datetime import datetime

def print_header(message):
    """طباعة عنوان"""
    print("\n" + "=" * 60)
    print(f" {message}")
    print("=" * 60)

def print_info(message):
    """طباعة معلومات"""
    print(f"ℹ️ {message}")

def print_success(message):
    """طباعة رسالة نجاح"""
    print(f"✅ {message}")

def print_warning(message):
    """طباعة رسالة تحذير"""
    print(f"⚠️ {message}")

def print_error(message):
    """طباعة رسالة خطأ"""
    print(f"❌ {message}")

def create_deployment_zip():
    """إنشاء ملف مضغوط للنشر"""
    # اسم الملف المضغوط
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"deployment_package_{timestamp}.zip"
    
    # الملفات والمجلدات المطلوب تضمينها
    include_files = [
        # ملفات التكوين الرئيسية
        'wsgi.py',
        'main.py',
        'app.py',
        'models.py',
        'index.php',
        '.htaccess',
        'php.ini',
        'setup.py',
        'requirements_deploy.txt',  # سيتم إعادة تسميته إلى requirements.txt في مرحلة لاحقة
        '.env.example',  # سيتم إعادة تسميته إلى .env في مرحلة لاحقة
        'check_installation.py',
        'deploy_guide.md',
        'domain_deployment.md'
    ]
    
    include_dirs = [
        'static',
        'templates',
        'routes',
        'utils'
    ]
    
    # المجلدات والملفات المستبعدة
    exclude_patterns = [
        '__pycache__',
        '.git',
        '.replit',
        'replit.nix',
        '.upm',
        '.pytest_cache',
        '*.pyc',
        '*.pyo',
        '*.pyd',
        '.DS_Store',
        'Thumbs.db'
    ]
    
    print_header("إنشاء حزمة النشر")
    print_info(f"اسم الملف المضغوط: {zip_filename}")
    
    try:
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # إضافة الملفات الفردية
            for file in include_files:
                if os.path.exists(file):
                    zipf.write(file)
                    print_success(f"تمت إضافة الملف: {file}")
                else:
                    print_warning(f"الملف غير موجود: {file}")
            
            # إضافة المجلدات
            for directory in include_dirs:
                if os.path.exists(directory) and os.path.isdir(directory):
                    for root, dirs, files in os.walk(directory):
                        # استبعاد المجلدات غير المرغوب فيها
                        dirs[:] = [d for d in dirs if not any(pattern in d for pattern in exclude_patterns)]
                        
                        for file in files:
                            # استبعاد الملفات غير المرغوب فيها
                            if not any(pattern in file for pattern in exclude_patterns):
                                file_path = os.path.join(root, file)
                                zipf.write(file_path)
                    print_success(f"تمت إضافة المجلد: {directory}")
                else:
                    print_warning(f"المجلد غير موجود: {directory}")
            
            # إضافة ملف بتعليمات النشر
            readme_content = """# حزمة نشر نظام إدارة الموظفين

هذه الحزمة تحتوي على جميع الملفات اللازمة لنشر نظام إدارة الموظفين على خادم ويب.

## خطوات النشر

1. قم باستخراج جميع الملفات إلى المجلد الرئيسي للموقع على الخادم
2. أعد تسمية الملف `requirements_deploy.txt` إلى `requirements.txt`
3. أعد تسمية الملف `.env.example` إلى `.env` وحدّث القيم حسب إعدادات خادمك
4. قم بضبط أذونات الملفات والمجلدات:
   - 644 للملفات العادية
   - 755 للمجلدات
   - 755 للملفات القابلة للتنفيذ مثل *.py
5. اتبع التعليمات الموجودة في ملف `deploy_guide.md` للإعداد الكامل

## ملاحظات هامة

- تأكد من دعم خادمك لـ Python 3.9 أو أحدث
- تأكد من وجود قاعدة بيانات PostgreSQL
- قم بتعيين المتغيرات البيئية المطلوبة في ملف `.env`

للمزيد من المساعدة، راجع ملفات `deploy_guide.md` و `domain_deployment.md`
"""
            zipf.writestr('README.txt', readme_content)
            print_success("تمت إضافة ملف README.txt")
            
        print_header("تم إنشاء حزمة النشر بنجاح")
        print_info(f"موقع الملف المضغوط: {os.path.abspath(zip_filename)}")
        print_info("يمكنك الآن تنزيل هذا الملف ورفعه إلى خادم الويب الخاص بك.")
        
        print("\nتعليمات إضافية:")
        print("1. بعد استخراج الملفات، أعد تسمية requirements_deploy.txt إلى requirements.txt")
        print("2. أعد تسمية .env.example إلى .env وقم بتحديث القيم حسب بيئتك")
        print("3. اضبط أذونات الملفات والمجلدات كما هو موضح في الدليل")
        
    except Exception as e:
        print_error(f"حدث خطأ أثناء إنشاء الملف المضغوط: {str(e)}")

if __name__ == "__main__":
    create_deployment_zip()