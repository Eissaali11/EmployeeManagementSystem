#!/usr/bin/env python3
"""
سكريپت إنشاء حزمة النشر لنُظم
يقوم بإنشاء ملف مضغوط يحتوي على جميع الملفات المطلوبة للنشر على VPS
"""

import os
import zipfile
import shutil
from datetime import datetime
import sys

def create_deployment_package():
    """إنشاء حزمة النشر"""
    
    # اسم الحزمة مع التاريخ والوقت
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    package_name = f"nuzum_deployment_{timestamp}.zip"
    
    print("بدء إنشاء حزمة النشر...")
    
    # الملفات والمجلدات المطلوبة
    required_items = [
        # الملفات الأساسية
        'app.py',
        'main.py', 
        'models.py',
        
        # المجلدات الأساسية
        'routes/',
        'templates/',
        'static/',
        'utils/',
        'forms/',
        'config/',
        'core/',
        'services/',
        'deployment/',
        
        # ملفات الإعداد
        '.env.example',
        'README.md',
        'ARCHITECTURE.md',
        'DEVELOPER_GUIDE.md',
        'SYSTEM_MAP.md',
        
        # ملفات Firebase
        'firebase.json',
        '.firebaserc',
        'package.json',
        'package-lock.json',
    ]
    
    # الملفات المستثناة
    excluded_patterns = [
        '__pycache__/',
        '.git/',
        '.env',
        '*.pyc',
        '.DS_Store',
        'node_modules/',
        'temp_fonts/',
        'downloads/',
        'attached_assets/',
        'public/',
        'functions/',
        '.replit',
        'replit.nix',
        'pyproject.toml',
        'uv.lock',
    ]
    
    try:
        with zipfile.ZipFile(package_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            
            for item in required_items:
                if os.path.exists(item):
                    if os.path.isfile(item):
                        print(f"إضافة ملف: {item}")
                        zipf.write(item, item)
                    elif os.path.isdir(item):
                        print(f"إضافة مجلد: {item}")
                        for root, dirs, files in os.walk(item):
                            # تخطي المجلدات المستثناة
                            dirs[:] = [d for d in dirs if not any(pattern.rstrip('/') in d for pattern in excluded_patterns)]
                            
                            for file in files:
                                # تخطي الملفات المستثناة
                                if not any(pattern.rstrip('*') in file for pattern in excluded_patterns):
                                    file_path = os.path.join(root, file)
                                    arcname = file_path
                                    zipf.write(file_path, arcname)
                else:
                    print(f"تحذير: العنصر غير موجود: {item}")
            
            # إضافة ملف معلومات الحزمة
            package_info = f"""حزمة نشر نُظم
تاريخ الإنشاء: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
الإصدار: 2.0.0

محتويات الحزمة:
- التطبيق الأساسي (Flask)
- جميع القوالب والملفات الثابتة
- ملفات الإعداد والنشر
- الوثائق الفنية
- سكريپتات التثبيت

خطوات النشر:
1. فك ضغط الحزمة إلى /var/www/nuzum
2. تشغيل سكريپت التثبيت: sudo bash deployment/install.sh
3. تحديث ملف .env بالإعدادات الصحيحة
4. إعادة تشغيل الخدمات

للدعم الفني: راجع ملف DEVELOPER_GUIDE.md
"""
            zipf.writestr('PACKAGE_INFO.txt', package_info)
        
        print(f"\n✅ تم إنشاء حزمة النشر بنجاح: {package_name}")
        print(f"📦 حجم الحزمة: {os.path.getsize(package_name) / (1024*1024):.2f} ميجابايت")
        
        return package_name
        
    except Exception as e:
        print(f"❌ خطأ في إنشاء الحزمة: {str(e)}")
        return None

def verify_package(package_name):
    """التحقق من محتويات الحزمة"""
    print(f"\nالتحقق من محتويات الحزمة: {package_name}")
    
    try:
        with zipfile.ZipFile(package_name, 'r') as zipf:
            files = zipf.namelist()
            print(f"عدد الملفات: {len(files)}")
            
            # التحقق من الملفات الأساسية
            essential_files = ['app.py', 'main.py', 'models.py', 'deployment/install.sh']
            missing_files = [f for f in essential_files if f not in files]
            
            if missing_files:
                print(f"⚠️  ملفات مفقودة: {missing_files}")
            else:
                print("✅ جميع الملفات الأساسية موجودة")
                
    except Exception as e:
        print(f"❌ خطأ في التحقق من الحزمة: {str(e)}")

if __name__ == "__main__":
    print("=== إنشاء حزمة نشر نُظم ===")
    
    # التحقق من وجود الملفات الأساسية
    if not os.path.exists('app.py'):
        print("❌ خطأ: ملف app.py غير موجود. تأكد من تشغيل السكريپت من المجلد الصحيح.")
        sys.exit(1)
    
    # إنشاء الحزمة
    package_name = create_deployment_package()
    
    if package_name:
        verify_package(package_name)
        print(f"\n🚀 جاهز للنشر!")
        print(f"📋 قم برفع الملف {package_name} إلى الخادم وفك ضغطه")
    else:
        print("❌ فشل في إنشاء الحزمة")
        sys.exit(1)