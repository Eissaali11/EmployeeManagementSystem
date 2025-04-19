#!/usr/bin/env python3
"""
سكريبت إعداد نظام إدارة الموظفين
يقوم هذا السكريبت بإنشاء قاعدة البيانات وإعدادها والتأكد من وجود حساب مسؤول افتراضي
"""

import os
import sys
import logging
import hashlib
import random
import string
import datetime
from werkzeug.security import generate_password_hash

# إعداد التسجيل
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'setup.log'))
    ]
)

# إضافة المسار الحالي إلى مسار النظام
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def setup_database():
    """إعداد قاعدة البيانات وإنشاء الجداول"""
    logging.info("بدء إعداد قاعدة البيانات")
    
    try:
        # تحميل المتغيرات البيئية من ملف .env إذا كان موجودًا
        env_path = os.path.join(current_dir, '.env')
        if os.path.exists(env_path):
            logging.info("تحميل المتغيرات البيئية من ملف .env")
            try:
                from dotenv import load_dotenv
                load_dotenv(env_path)
            except ImportError:
                logging.warning("لم يتم العثور على حزمة python-dotenv. سيتم استخدام المتغيرات البيئية الموجودة فقط.")
        
        # التحقق من وجود متغير رابط قاعدة البيانات
        db_url = os.environ.get('DATABASE_URL')
        if not db_url:
            logging.error("لم يتم العثور على متغير DATABASE_URL في ملف .env أو في متغيرات البيئة")
            logging.info("يرجى إضافة متغير DATABASE_URL بتنسيق: postgresql://username:password@hostname:port/database")
            return False
        
        # استيراد كائنات قاعدة البيانات
        logging.info("استيراد كائنات قاعدة البيانات")
        from app import db, app
        from models import User, Department, Employee, Attendance, Salary, Document, Vehicle, VehicleInspection, Fee
        
        # إنشاء جداول قاعدة البيانات
        with app.app_context():
            logging.info("إنشاء جداول قاعدة البيانات")
            db.create_all()
            
            # التحقق من وجود مستخدم مسؤول
            if User.query.filter_by(email='admin@example.com').first() is None:
                logging.info("إنشاء حساب مسؤول افتراضي")
                
                # إنشاء كلمة مرور آمنة للمسؤول (يمكن تغييرها لاحقًا)
                admin_password = 'admin123'  # كلمة مرور افتراضية
                
                # إنشاء حساب المسؤول
                admin = User(
                    name='مدير النظام',
                    username='admin',
                    email='admin@example.com',
                    password_hash=generate_password_hash(admin_password),
                    role='admin',
                    created_at=datetime.datetime.now()
                )
                
                # حفظ المستخدم في قاعدة البيانات
                db.session.add(admin)
                db.session.commit()
                
                logging.info("تم إنشاء حساب المسؤول بنجاح")
                logging.info(f"اسم المستخدم: admin@example.com")
                logging.info(f"كلمة المرور: {admin_password}")
                logging.info("يرجى تغيير كلمة المرور فورًا بعد تسجيل الدخول الأول")
            else:
                logging.info("حساب المسؤول موجود بالفعل")
            
            # إنشاء قسم افتراضي إذا لم يكن موجودًا
            if Department.query.count() == 0:
                logging.info("إنشاء قسم افتراضي")
                default_dept = Department(
                    name='الإدارة العامة',
                    description='القسم الرئيسي للشركة',
                    created_at=datetime.datetime.now()
                )
                db.session.add(default_dept)
                db.session.commit()
            
            logging.info("تم إعداد قاعدة البيانات بنجاح")
            return True
        
    except Exception as e:
        logging.error(f"حدث خطأ أثناء إعداد قاعدة البيانات: {str(e)}")
        import traceback
        logging.error(traceback.format_exc())
        return False

def setup_static_folders():
    """إنشاء المجلدات الثابتة اللازمة إذا لم تكن موجودة"""
    logging.info("إنشاء المجلدات الثابتة اللازمة")
    
    static_folders = [
        os.path.join(current_dir, 'static', 'uploads'),
        os.path.join(current_dir, 'static', 'uploads', 'employees'),
        os.path.join(current_dir, 'static', 'uploads', 'documents'),
        os.path.join(current_dir, 'static', 'uploads', 'vehicles'),
        os.path.join(current_dir, 'static', 'reports'),
        os.path.join(current_dir, 'static', 'error'),
    ]
    
    for folder in static_folders:
        if not os.path.exists(folder):
            try:
                os.makedirs(folder)
                logging.info(f"تم إنشاء المجلد: {folder}")
            except Exception as e:
                logging.warning(f"لم يتم إنشاء المجلد {folder}: {str(e)}")

def setup_error_pages():
    """إنشاء صفحات الخطأ إذا لم تكن موجودة"""
    logging.info("إنشاء صفحات الخطأ")
    
    error_pages = {
        '403.html': """<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>خطأ 403 - الوصول ممنوع</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f8f9fa;
            color: #333;
            margin: 0;
            padding: 20px;
            text-align: center;
        }
        .error-container {
            background-color: #fff;
            border-radius: 5px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin: 40px auto;
            max-width: 600px;
            padding: 20px;
        }
        h1 {
            color: #dc3545;
        }
        p {
            line-height: 1.6;
        }
        .back-link {
            display: inline-block;
            margin-top: 20px;
            padding: 10px 20px;
            background-color: #007bff;
            color: white;
            text-decoration: none;
            border-radius: 4px;
        }
        .back-link:hover {
            background-color: #0056b3;
        }
    </style>
</head>
<body>
    <div class="error-container">
        <h1>خطأ 403 - الوصول ممنوع</h1>
        <p>ليس لديك الصلاحيات اللازمة للوصول إلى هذه الصفحة.</p>
        <p>يرجى التأكد من تسجيل الدخول أو الاتصال بمسؤول النظام إذا كنت تعتقد أنه خطأ.</p>
        <a href="/" class="back-link">العودة إلى الصفحة الرئيسية</a>
    </div>
</body>
</html>""",
        '404.html': """<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>خطأ 404 - الصفحة غير موجودة</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f8f9fa;
            color: #333;
            margin: 0;
            padding: 20px;
            text-align: center;
        }
        .error-container {
            background-color: #fff;
            border-radius: 5px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin: 40px auto;
            max-width: 600px;
            padding: 20px;
        }
        h1 {
            color: #dc3545;
        }
        p {
            line-height: 1.6;
        }
        .back-link {
            display: inline-block;
            margin-top: 20px;
            padding: 10px 20px;
            background-color: #007bff;
            color: white;
            text-decoration: none;
            border-radius: 4px;
        }
        .back-link:hover {
            background-color: #0056b3;
        }
    </style>
</head>
<body>
    <div class="error-container">
        <h1>خطأ 404 - الصفحة غير موجودة</h1>
        <p>عذراً، الصفحة التي تبحث عنها غير موجودة.</p>
        <p>قد تكون الصفحة قد تم نقلها أو حذفها أو قد يكون هناك خطأ في الرابط الذي اتبعته.</p>
        <a href="/" class="back-link">العودة إلى الصفحة الرئيسية</a>
    </div>
</body>
</html>""",
        '500.html': """<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>خطأ 500 - خطأ في الخادم</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f8f9fa;
            color: #333;
            margin: 0;
            padding: 20px;
            text-align: center;
        }
        .error-container {
            background-color: #fff;
            border-radius: 5px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin: 40px auto;
            max-width: 600px;
            padding: 20px;
        }
        h1 {
            color: #dc3545;
        }
        p {
            line-height: 1.6;
        }
        .back-link {
            display: inline-block;
            margin-top: 20px;
            padding: 10px 20px;
            background-color: #007bff;
            color: white;
            text-decoration: none;
            border-radius: 4px;
        }
        .back-link:hover {
            background-color: #0056b3;
        }
    </style>
</head>
<body>
    <div class="error-container">
        <h1>خطأ 500 - خطأ في الخادم</h1>
        <p>عذراً، حدث خطأ غير متوقع في الخادم.</p>
        <p>الرجاء المحاولة مرة أخرى لاحقاً أو الاتصال بمسؤول النظام إذا استمرت المشكلة.</p>
        <a href="/" class="back-link">العودة إلى الصفحة الرئيسية</a>
    </div>
</body>
</html>"""
    }
    
    error_dir = os.path.join(current_dir, 'static', 'error')
    for filename, content in error_pages.items():
        file_path = os.path.join(error_dir, filename)
        if not os.path.exists(file_path):
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logging.info(f"تم إنشاء صفحة الخطأ: {filename}")
            except Exception as e:
                logging.warning(f"لم يتم إنشاء صفحة الخطأ {filename}: {str(e)}")

def print_header(message):
    """طباعة عنوان"""
    print("\n" + "=" * 60)
    print(f" {message}")
    print("=" * 60)

def main():
    """الدالة الرئيسية"""
    print_header("إعداد نظام إدارة الموظفين")
    
    # إنشاء المجلدات الثابتة
    setup_static_folders()
    
    # إنشاء صفحات الخطأ
    setup_error_pages()
    
    # إعداد قاعدة البيانات
    success = setup_database()
    
    if success:
        print("\n✅ تم إعداد النظام بنجاح!")
        print("\nيمكنك الآن الوصول إلى النظام من خلال المتصفح.")
        print("بيانات الدخول الافتراضية للمسؤول:")
        print("البريد الإلكتروني: admin@example.com")
        print("كلمة المرور: admin123")
        print("\n⚠️ يرجى تغيير كلمة المرور الافتراضية فور تسجيل الدخول الأول.")
    else:
        print("\n❌ حدث خطأ أثناء إعداد النظام.")
        print("يرجى مراجعة ملف setup.log للحصول على مزيد من المعلومات.")

if __name__ == "__main__":
    main()