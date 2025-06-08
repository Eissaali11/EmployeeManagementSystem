#!/usr/bin/env python3
"""
نص إعداد مستقل لنظام نُظم - يعمل مع أي قاعدة بيانات
يحل مشكلة SQLite ويوفر إعدادات مرنة للنشر
"""

import os
import sys
import subprocess
import sqlite3
from pathlib import Path

def create_directories():
    """إنشاء المجلدات المطلوبة"""
    directories = ['database', 'uploads', 'logs', 'static', 'templates']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("✓ تم إنشاء المجلدات المطلوبة")

def setup_sqlite_database():
    """إعداد قاعدة بيانات SQLite مع الصلاحيات الصحيحة"""
    db_path = Path("database/nuzum.db")
    
    # التأكد من وجود مجلد قاعدة البيانات
    db_path.parent.mkdir(exist_ok=True)
    
    # إنشاء قاعدة البيانات إذا لم تكن موجودة
    if not db_path.exists():
        conn = sqlite3.connect(str(db_path))
        conn.close()
        print(f"✓ تم إنشاء قاعدة البيانات: {db_path}")
    
    # تعيين الصلاحيات المناسبة
    os.chmod(str(db_path), 0o664)
    os.chmod(str(db_path.parent), 0o755)
    
    return f"sqlite:///{db_path.absolute()}"

def create_env_file(database_url):
    """إنشاء ملف .env مع الإعدادات المناسبة"""
    env_content = f"""# إعدادات نظام نُظم
DATABASE_URL={database_url}
SESSION_SECRET=nuzum_session_secret_key_2024_secure
FLASK_ENV=production
FLASK_APP=main.py

# إعدادات اختيارية (يمكن تركها فارغة)
FIREBASE_API_KEY=
FIREBASE_PROJECT_ID=
FIREBASE_APP_ID=
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=
SENDGRID_API_KEY=
"""
    
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    print("✓ تم إنشاء ملف .env")

def install_dependencies():
    """تثبيت المكتبات المطلوبة"""
    print("تثبيت المكتبات المطلوبة...")
    
    requirements = [
        "Flask>=3.1.0",
        "Flask-Login>=0.6.3", 
        "Flask-SQLAlchemy>=3.1.1",
        "Flask-WTF>=1.2.2",
        "WTForms>=3.1.2",
        "SQLAlchemy>=2.0.40",
        "gunicorn>=23.0.0",
        "python-dotenv>=1.1.0",
        "Werkzeug>=3.1.3",
        "MarkupSafe>=3.0.2",
        "email-validator>=2.2.0",
        "Pillow>=11.2.1",
        "reportlab>=4.3.1",
        "openpyxl>=3.1.5",
        "pandas>=2.2.3",
        "numpy>=2.2.4",
        "arabic-reshaper>=3.0.0",
        "python-bidi>=0.6.6",
        "hijri-converter>=2.3.1",
        "fpdf>=1.7.2"
    ]
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + requirements)
        print("✓ تم تثبيت جميع المكتبات بنجاح")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ خطأ في تثبيت المكتبات: {e}")
        return False

def setup_database_and_admin():
    """إعداد قاعدة البيانات وإنشاء المستخدم الإداري"""
    print("إعداد قاعدة البيانات...")
    
    try:
        # استيراد التطبيق والنماذج
        from app import app, db
        from models import User, UserRole
        
        with app.app_context():
            # إنشاء الجداول
            db.create_all()
            print("✓ تم إنشاء جداول قاعدة البيانات")
            
            # إنشاء المستخدم الإداري
            admin = User.query.filter_by(email='admin@nuzum.com').first()
            if not admin:
                admin = User(
                    name='مدير النظام',
                    email='admin@nuzum.com', 
                    role=UserRole.ADMIN,
                    is_active=True,
                    auth_type='local'
                )
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                print("✓ تم إنشاء المستخدم الإداري: admin@nuzum.com / admin123")
            else:
                print("✓ المستخدم الإداري موجود مسبقاً")
                
        return True
    except Exception as e:
        print(f"❌ خطأ في إعداد قاعدة البيانات: {e}")
        return False

def create_run_script():
    """إنشاء نص تشغيل النظام"""
    run_script = """#!/bin/bash
# نص تشغيل نظام نُظم

# تفعيل البيئة الافتراضية إذا كانت موجودة
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✓ تم تفعيل البيئة الافتراضية"
fi

# تحميل متغيرات البيئة
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "✓ تم تحميل متغيرات البيئة"
fi

# التحقق من وجود قاعدة البيانات
if [ ! -f "database/nuzum.db" ]; then
    echo "إنشاء قاعدة البيانات..."
    python3 deployment/standalone_setup.py
fi

echo "تشغيل نظام نُظم..."
echo "الرابط: http://localhost:5000"
echo "تسجيل الدخول: admin@nuzum.com / admin123"
echo "للإيقاف: اضغط Ctrl+C"

# تشغيل النظام
python3 -m gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 --reload main:app
"""
    
    with open('run.sh', 'w') as f:
        f.write(run_script)
    
    # تعيين صلاحيات التنفيذ
    os.chmod('run.sh', 0o755)
    print("✓ تم إنشاء نص التشغيل: run.sh")

def main():
    """الدالة الرئيسية"""
    print("===================================")
    print("إعداد نظام إدارة الموظفين نُظم")
    print("===================================")
    
    # إنشاء المجلدات
    create_directories()
    
    # إعداد قاعدة البيانات SQLite
    database_url = setup_sqlite_database()
    
    # إنشاء ملف البيئة
    create_env_file(database_url)
    
    # تثبيت المكتبات
    if not install_dependencies():
        print("❌ فشل في تثبيت المكتبات")
        return False
    
    # إعداد قاعدة البيانات والمستخدم الإداري
    if not setup_database_and_admin():
        print("❌ فشل في إعداد قاعدة البيانات")
        return False
    
    # إنشاء نص التشغيل
    create_run_script()
    
    print("===================================")
    print("تم إكمال الإعداد بنجاح!")
    print("===================================")
    print("للتشغيل:")
    print("  ./run.sh")
    print("أو:")
    print("  python3 -m gunicorn --bind 0.0.0.0:5000 main:app")
    print("")
    print("رابط النظام: http://localhost:5000")
    print("تسجيل الدخول: admin@nuzum.com / admin123")
    print("===================================")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)