#!/usr/bin/env python3
"""
أداة للتحقق من صحة تثبيت نظام إدارة الموظفين
تقوم هذه الأداة بفحص المتطلبات والإعدادات للتأكد من أن النظام سيعمل بشكل صحيح
"""

import os
import sys
import importlib
import platform
import socket
import psycopg2
from urllib.parse import urlparse

def print_header(message):
    """طباعة عنوان"""
    print("\n" + "=" * 60)
    print(f" {message}")
    print("=" * 60)

def print_success(message):
    """طباعة رسالة نجاح"""
    print(f"✅ {message}")

def print_warning(message):
    """طباعة رسالة تحذير"""
    print(f"⚠️ {message}")

def print_error(message):
    """طباعة رسالة خطأ"""
    print(f"❌ {message}")

def check_python_version():
    """التحقق من إصدار Python"""
    print_header("فحص إصدار Python")
    
    python_version = platform.python_version()
    print(f"إصدار Python: {python_version}")
    
    major, minor, _ = map(int, python_version.split('.'))
    
    if major >= 3 and minor >= 9:
        print_success("إصدار Python متوافق")
        return True
    else:
        print_error(f"إصدار Python غير متوافق. مطلوب 3.9 أو أحدث.")
        return False

def check_required_packages():
    """التحقق من حزم Python المطلوبة"""
    print_header("فحص حزم Python المطلوبة")
    
    required_packages = [
        "flask", "flask_login", "flask_sqlalchemy", "flask_wtf",
        "werkzeug", "psycopg2", "sqlalchemy", "twilio", "pandas",
        "gunicorn", "reportlab", "weasyprint", "arabic_reshaper"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package.replace('-', '_'))
            print_success(f"حزمة {package} متوفرة")
        except ImportError:
            print_error(f"حزمة {package} غير متوفرة")
            missing_packages.append(package)
    
    if missing_packages:
        print_warning(f"يرجى تثبيت الحزم المفقودة: {', '.join(missing_packages)}")
        print("يمكنك تثبيتها باستخدام الأمر:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    else:
        print_success("جميع الحزم المطلوبة متوفرة")
        return True

def check_database_connection():
    """التحقق من الاتصال بقاعدة البيانات"""
    print_header("فحص الاتصال بقاعدة البيانات")
    
    database_url = os.environ.get("DATABASE_URL")
    
    if not database_url:
        print_error("متغير DATABASE_URL غير محدد")
        return False
    
    try:
        # تحليل عنوان قاعدة البيانات
        parsed_url = urlparse(database_url)
        
        # استخراج معلومات الاتصال
        dbname = parsed_url.path[1:]  # إزالة الشرطة المائلة الأولى
        user = parsed_url.username
        password = parsed_url.password
        host = parsed_url.hostname
        port = parsed_url.port or 5432
        
        # محاولة الاتصال بقاعدة البيانات
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        
        # إذا وصلنا إلى هنا، فإن الاتصال ناجح
        print_success("تم الاتصال بقاعدة البيانات بنجاح")
        
        # التحقق من وجود الجداول المطلوبة
        cursor = conn.cursor()
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = [table[0] for table in cursor.fetchall()]
        
        expected_tables = ['user', 'employee', 'department', 'attendance', 'salary', 'document', 'vehicle']
        missing_tables = [table for table in expected_tables if table not in tables]
        
        if missing_tables:
            print_warning(f"الجداول التالية غير موجودة: {', '.join(missing_tables)}")
            print_warning("يرجى تشغيل سكريبت setup.py لإنشاء جداول قاعدة البيانات")
        else:
            print_success("جميع الجداول المتوقعة موجودة في قاعدة البيانات")
        
        conn.close()
        return True
    
    except Exception as e:
        print_error(f"فشل الاتصال بقاعدة البيانات: {str(e)}")
        return False

def check_environment_variables():
    """التحقق من المتغيرات البيئية المطلوبة"""
    print_header("فحص المتغيرات البيئية")
    
    required_vars = {
        "DATABASE_URL": "عنوان قاعدة البيانات",
        "SECRET_KEY": "المفتاح السري للتطبيق",
    }
    
    optional_vars = {
        "TWILIO_ACCOUNT_SID": "معرف حساب Twilio",
        "TWILIO_AUTH_TOKEN": "رمز مصادقة Twilio",
        "TWILIO_PHONE_NUMBER": "رقم هاتف Twilio",
        "FLASK_ENV": "بيئة Flask",
        "FLASK_DEBUG": "وضع التصحيح",
    }
    
    # التحقق من المتغيرات المطلوبة
    missing_required = []
    for var, description in required_vars.items():
        if os.environ.get(var):
            print_success(f"{description} ({var}) محدد")
        else:
            print_error(f"{description} ({var}) غير محدد")
            missing_required.append(var)
    
    # التحقق من المتغيرات الاختيارية
    for var, description in optional_vars.items():
        if os.environ.get(var):
            print_success(f"{description} ({var}) محدد")
        else:
            print_warning(f"{description} ({var}) غير محدد")
    
    # التحقق من أن وضع التصحيح معطل في الإنتاج
    if os.environ.get("FLASK_ENV") == "production" and os.environ.get("FLASK_DEBUG") == "True":
        print_warning("وضع التصحيح نشط في بيئة الإنتاج. يرجى تعطيله لأسباب أمنية.")
    
    if missing_required:
        print_error(f"يرجى تعيين المتغيرات البيئية المطلوبة التالية: {', '.join(missing_required)}")
        return False
    else:
        print_success("جميع المتغيرات البيئية المطلوبة محددة")
        return True

def check_web_server():
    """التحقق من خادم الويب"""
    print_header("فحص خادم الويب")
    
    # محاولة اكتشاف خادم الويب
    server_software = os.environ.get("SERVER_SOFTWARE", "")
    
    if "apache" in server_software.lower():
        print_success(f"تم اكتشاف خادم Apache: {server_software}")
        # التحقق من وجود ملف .htaccess
        if os.path.exists(".htaccess"):
            print_success("ملف .htaccess موجود")
        else:
            print_warning("ملف .htaccess غير موجود. قد تكون هناك مشاكل في إعادة توجيه الطلبات.")
    elif "nginx" in server_software.lower():
        print_success(f"تم اكتشاف خادم Nginx: {server_software}")
    elif "gunicorn" in server_software.lower():
        print_success(f"تم اكتشاف خادم Gunicorn: {server_software}")
    else:
        print_warning(f"لم يتم التعرف على خادم الويب. تم اكتشاف: {server_software or 'غير معروف'}")
    
    # التحقق من إمكانية الوصول إلى المنفذ 80 أو 443
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("0.0.0.0", 80))
        print_warning("المنفذ 80 متاح. قد لا يكون خادم الويب قيد التشغيل.")
        s.close()
    except socket.error:
        print_success("المنفذ 80 مستخدم (محتمل أن يكون بواسطة خادم الويب)")
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("0.0.0.0", 443))
        print_warning("المنفذ 443 متاح. قد لا يكون HTTPS مفعلاً.")
        s.close()
    except socket.error:
        print_success("المنفذ 443 مستخدم (محتمل أن يكون بواسطة خادم الويب مع HTTPS)")
    
    return True

def check_files_and_permissions():
    """التحقق من وجود الملفات والأذونات"""
    print_header("فحص الملفات والأذونات")
    
    required_files = {
        "wsgi.py": "ملف WSGI الرئيسي",
        "main.py": "ملف Flask الرئيسي",
        "models.py": "نماذج قاعدة البيانات",
        "requirements.txt": "قائمة الحزم المطلوبة",
    }
    
    folders_to_check = [
        "static", "templates", "routes"
    ]
    
    # التحقق من الملفات المطلوبة
    for filename, description in required_files.items():
        if os.path.exists(filename):
            print_success(f"{description} ({filename}) موجود")
        else:
            print_error(f"{description} ({filename}) غير موجود")
    
    # التحقق من المجلدات المطلوبة
    for folder in folders_to_check:
        if os.path.exists(folder) and os.path.isdir(folder):
            print_success(f"مجلد {folder} موجود")
        else:
            print_error(f"مجلد {folder} غير موجود")
    
    # التحقق من أذونات الملفات والمجلدات
    try:
        current_folder = os.getcwd()
        writable = os.access(current_folder, os.W_OK)
        if writable:
            print_success(f"المجلد الحالي ({current_folder}) قابل للكتابة")
        else:
            print_error(f"المجلد الحالي ({current_folder}) غير قابل للكتابة")
        
        # التحقق من أذونات مجلد static
        if os.path.exists("static") and os.path.isdir("static"):
            writable = os.access("static", os.W_OK)
            if writable:
                print_success("مجلد static قابل للكتابة")
            else:
                print_error("مجلد static غير قابل للكتابة. قد تكون هناك مشاكل في تحميل الملفات.")
    except Exception as e:
        print_error(f"حدث خطأ أثناء التحقق من الأذونات: {str(e)}")
    
    return True

def main():
    """الدالة الرئيسية"""
    print("\n🔍 أداة فحص تثبيت نظام إدارة الموظفين 🔍\n")
    
    print("جاري فحص النظام للتأكد من جاهزيته للعمل...\n")
    
    checks = [
        check_python_version,
        check_required_packages,
        check_environment_variables,
        check_database_connection,
        check_web_server,
        check_files_and_permissions
    ]
    
    results = {}
    
    for check_function in checks:
        results[check_function.__name__] = check_function()
    
    print_header("ملخص نتائج الفحص")
    
    all_passed = True
    for name, result in results.items():
        test_name = name.replace("check_", "").replace("_", " ").capitalize()
        if result:
            print_success(f"{test_name}: نجاح")
        else:
            print_error(f"{test_name}: فشل")
            all_passed = False
    
    if all_passed:
        print("\n🎉 تهانينا! النظام جاهز للعمل. 🎉\n")
    else:
        print("\n⚠️ يرجى معالجة المشاكل المذكورة أعلاه قبل بدء تشغيل النظام. ⚠️\n")

if __name__ == "__main__":
    main()