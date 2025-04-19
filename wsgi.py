#!/usr/bin/env python3
"""
ملف WSGI للنشر على استضافة مشتركة
هذا الملف يعمل كنقطة اتصال بين خادم الويب وتطبيق Flask
"""

import os
import sys
import logging

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'app.log'))
    ]
)

# إضافة المسار الحالي إلى مسار النظام
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# إضافة مسار الحزم المثبتة محليًا (إذا كانت موجودة)
site_packages = os.path.join(current_dir, 'lib', 'python3.9', 'site-packages')
if os.path.exists(site_packages):
    sys.path.insert(0, site_packages)

try:
    # استيراد تطبيق Flask
    from main import app as application
    
    # تكوين للاستضافة المشتركة
    if __name__ == "__main__":
        # إعداد متغيرات البيئة من ملف .env إذا كان موجودًا
        env_path = os.path.join(current_dir, '.env')
        if os.path.exists(env_path):
            logging.info("تحميل المتغيرات البيئية من ملف .env")
            from dotenv import load_dotenv
            load_dotenv(env_path)
        
        # طباعة المعلومات كاستجابة CGI
        print("Content-Type: text/html\n")
        
        # التحقق من وجود قاعدة البيانات واتصالها
        db_url = os.environ.get('DATABASE_URL')
        if not db_url:
            print('<html dir="rtl" lang="ar"><head><meta charset="UTF-8"><title>خطأ في الإعداد</title>')
            print('<style>body{font-family:Arial,sans-serif;background-color:#f8f9fa;color:#333;margin:0;padding:20px;text-align:center;}')
            print('.error-container{background-color:#fff;border-radius:5px;box-shadow:0 2px 10px rgba(0,0,0,0.1);margin:40px auto;max-width:600px;padding:20px;}')
            print('h1{color:#dc3545;}p{line-height:1.6;}</style></head><body>')
            print('<div class="error-container"><h1>خطأ في إعداد قاعدة البيانات</h1>')
            print('<p>لم يتم العثور على رابط قاعدة البيانات. يرجى التأكد من تكوين ملف .env بشكل صحيح.</p>')
            print('<p>للمساعدة، يرجى مراجعة <a href="deploy_guide.md">دليل النشر</a> أو <a href="دليل_النشر_على_الاستضافة.md">الدليل العربي</a>.</p></div></body></html>')
            sys.exit(1)
        
        # تشغيل ملف setup.py للتأكد من إنشاء جداول قاعدة البيانات
        try:
            logging.info("محاولة إعداد قاعدة البيانات")
            import setup
            logging.info("تم إعداد قاعدة البيانات بنجاح")
        except Exception as e:
            logging.error(f"خطأ في إعداد قاعدة البيانات: {str(e)}")
        
        # عرض رسالة نجاح أو توجيه المتصفح
        print('<html dir="rtl" lang="ar"><head><meta charset="UTF-8"><title>نظام إدارة الموظفين</title>')
        print('<meta http-equiv="refresh" content="0;url=/">')
        print('<style>body{font-family:Arial,sans-serif;background-color:#f8f9fa;color:#333;margin:0;padding:20px;text-align:center;}')
        print('.success-container{background-color:#fff;border-radius:5px;box-shadow:0 2px 10px rgba(0,0,0,0.1);margin:40px auto;max-width:600px;padding:20px;}')
        print('h1{color:#28a745;}p{line-height:1.6;}</style></head><body>')
        print('<div class="success-container"><h1>تم تشغيل النظام بنجاح</h1>')
        print('<p>جاري تحويلك إلى الصفحة الرئيسية...</p>')
        print('<p>إذا لم يتم التحويل تلقائيًا، <a href="/">انقر هنا</a>.</p></div></body></html>')
        
except Exception as e:
    # طباعة رسالة الخطأ كاستجابة CGI
    print("Content-Type: text/html\n")
    print('<html dir="rtl" lang="ar"><head><meta charset="UTF-8"><title>خطأ في النظام</title>')
    print('<style>body{font-family:Arial,sans-serif;background-color:#f8f9fa;color:#333;margin:0;padding:20px;text-align:center;}')
    print('.error-container{background-color:#fff;border-radius:5px;box-shadow:0 2px 10px rgba(0,0,0,0.1);margin:40px auto;max-width:800px;padding:20px;text-align:right;}')
    print('h1{color:#dc3545;}p{line-height:1.6;}pre{background-color:#f8f9fa;border-radius:4px;padding:10px;overflow:auto;text-align:left;direction:ltr;}</style></head><body>')
    print('<div class="error-container"><h1>خطأ في تشغيل النظام</h1>')
    print(f'<p>حدث خطأ أثناء محاولة تشغيل النظام: {str(e)}</p>')
    
    # عرض معلومات النظام للمطورين
    print('<h2>معلومات النظام (للمطورين فقط):</h2>')
    print('<pre>')
    print(f'Python version: {sys.version}')
    print(f'Python path: {sys.path}')
    print(f'Current directory: {current_dir}')
    print('Environment variables:')
    for key, value in os.environ.items():
        if 'SECRET' not in key and 'PASSWORD' not in key and 'TOKEN' not in key:
            print(f'  {key}: {value}')
    print('</pre>')
    
    print('<p>للمساعدة، يرجى مراجعة <a href="deploy_guide.md">دليل النشر</a> أو <a href="دليل_النشر_على_الاستضافة.md">الدليل العربي</a>.</p></div></body></html>')
    sys.exit(1)