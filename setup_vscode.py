#!/usr/bin/env python3
"""
نص إعداد VS Code لنظام نُظم
تثبيت جميع المكتبات والإعدادات المطلوبة للتطوير المحلي
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def create_virtual_environment():
    """إنشاء بيئة Python افتراضية"""
    print("إنشاء البيئة الافتراضية...")
    try:
        subprocess.check_call([sys.executable, "-m", "venv", "venv"])
        print("✓ تم إنشاء البيئة الافتراضية: venv/")
        
        # تحديد مسار Python في البيئة الافتراضية
        if sys.platform == "win32":
            python_path = "venv\\Scripts\\python.exe"
            pip_path = "venv\\Scripts\\pip.exe"
        else:
            python_path = "venv/bin/python"
            pip_path = "venv/bin/pip"
            
        return python_path, pip_path
    except subprocess.CalledProcessError as e:
        print(f"❌ خطأ في إنشاء البيئة الافتراضية: {e}")
        return None, None

def install_requirements(pip_path):
    """تثبيت المكتبات من ملف requirements"""
    print("تثبيت المكتبات المطلوبة...")
    
    requirements = [
        "Flask==3.1.0",
        "Flask-Login==0.6.3", 
        "Flask-SQLAlchemy==3.1.1",
        "Flask-WTF==1.2.2",
        "WTForms==3.1.2",
        "SQLAlchemy==2.0.40",
        "psycopg2-binary==2.9.10",
        "PyMySQL==1.1.1",
        "gunicorn==23.0.0",
        "Werkzeug==3.1.3",
        "MarkupSafe==3.0.2",
        "email-validator==2.2.0",
        "Pillow==11.2.1",
        "openpyxl==3.1.5",
        "xlrd==2.0.1",
        "xlsxwriter==3.2.2",
        "pandas==2.2.3",
        "numpy==2.2.4",
        "reportlab==4.3.1",
        "weasyprint==65.1",
        "fpdf==1.7.2",
        "arabic-reshaper==3.0.0",
        "python-bidi==0.6.6",
        "hijri-converter==2.3.1",
        "python-dotenv==1.1.0",
        "twilio==9.5.2",
        "sendgrid==6.11.0",
        "requests==2.31.0",
        "pytest==7.4.3",
        "pytest-flask==1.3.0",
        "coverage==7.3.2",
        "flake8==6.1.0"
    ]
    
    try:
        # تحديث pip
        subprocess.check_call([pip_path, "install", "--upgrade", "pip"])
        
        # تثبيت المكتبات
        subprocess.check_call([pip_path, "install"] + requirements)
        print("✓ تم تثبيت جميع المكتبات بنجاح")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ خطأ في تثبيت المكتبات: {e}")
        return False

def create_vscode_settings():
    """إنشاء إعدادات VS Code للمشروع"""
    print("إنشاء إعدادات VS Code...")
    
    # إنشاء مجلد .vscode
    vscode_dir = Path(".vscode")
    vscode_dir.mkdir(exist_ok=True)
    
    # إعدادات VS Code
    settings = {
        "python.defaultInterpreterPath": "./venv/bin/python" if sys.platform != "win32" else ".\\venv\\Scripts\\python.exe",
        "python.linting.enabled": True,
        "python.linting.flake8Enabled": True,
        "python.linting.pylintEnabled": False,
        "python.formatting.provider": "black",
        "python.testing.pytestEnabled": True,
        "python.testing.unittestEnabled": False,
        "python.testing.pytestArgs": ["tests"],
        "files.associations": {
            "*.html": "html",
            "*.js": "javascript",
            "*.css": "css"
        },
        "emmet.includeLanguages": {
            "jinja-html": "html"
        },
        "files.exclude": {
            "**/__pycache__": True,
            "**/*.pyc": True,
            "**/venv": True,
            "**/.pytest_cache": True,
            "**/database/*.db": False
        },
        "editor.tabSize": 4,
        "editor.insertSpaces": True,
        "editor.detectIndentation": True,
        "python.envFile": "${workspaceFolder}/.env",
        "terminal.integrated.env.windows": {
            "PYTHONPATH": "${workspaceFolder}"
        },
        "terminal.integrated.env.linux": {
            "PYTHONPATH": "${workspaceFolder}"
        },
        "terminal.integrated.env.osx": {
            "PYTHONPATH": "${workspaceFolder}"
        }
    }
    
    # كتابة ملف الإعدادات
    with open(vscode_dir / "settings.json", "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)
    
    # إعدادات التشغيل والتصحيح
    launch_config = {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Flask App",
                "type": "python",
                "request": "launch",
                "program": "${workspaceFolder}/main.py",
                "env": {
                    "FLASK_ENV": "development",
                    "FLASK_APP": "main.py"
                },
                "args": [],
                "jinja": True,
                "console": "integratedTerminal"
            },
            {
                "name": "Gunicorn Server",
                "type": "python",
                "request": "launch",
                "module": "gunicorn",
                "env": {
                    "FLASK_ENV": "development"
                },
                "args": [
                    "--bind", "0.0.0.0:5000",
                    "--reload",
                    "main:app"
                ],
                "console": "integratedTerminal"
            }
        ]
    }
    
    with open(vscode_dir / "launch.json", "w", encoding="utf-8") as f:
        json.dump(launch_config, f, indent=4)
    
    # إعدادات المهام
    tasks_config = {
        "version": "2.0.0",
        "tasks": [
            {
                "label": "Run Flask Development Server",
                "type": "shell",
                "command": "${workspaceFolder}/venv/bin/python" if sys.platform != "win32" else "${workspaceFolder}\\venv\\Scripts\\python.exe",
                "args": ["main.py"],
                "group": {
                    "kind": "build",
                    "isDefault": True
                },
                "presentation": {
                    "echo": True,
                    "reveal": "always",
                    "focus": False,
                    "panel": "shared"
                },
                "problemMatcher": []
            },
            {
                "label": "Run Tests",
                "type": "shell",
                "command": "${workspaceFolder}/venv/bin/python" if sys.platform != "win32" else "${workspaceFolder}\\venv\\Scripts\\python.exe",
                "args": ["-m", "pytest", "tests/"],
                "group": "test",
                "presentation": {
                    "echo": True,
                    "reveal": "always",
                    "focus": False,
                    "panel": "shared"
                }
            },
            {
                "label": "Install Requirements",
                "type": "shell",
                "command": "${workspaceFolder}/venv/bin/pip" if sys.platform != "win32" else "${workspaceFolder}\\venv\\Scripts\\pip.exe",
                "args": ["install", "-r", "requirements_vscode.txt"],
                "group": "build"
            }
        ]
    }
    
    with open(vscode_dir / "tasks.json", "w", encoding="utf-8") as f:
        json.dump(tasks_config, f, indent=4)
    
    print("✓ تم إنشاء إعدادات VS Code")

def create_env_file():
    """إنشاء ملف .env للتطوير المحلي"""
    env_content = """# إعدادات التطوير المحلي
DATABASE_URL=sqlite:///database/nuzum.db
SESSION_SECRET=dev_secret_key_change_in_production
FLASK_ENV=development
FLASK_APP=main.py
FLASK_DEBUG=1

# إعدادات اختيارية (اتركها فارغة إذا لم تكن متوفرة)
FIREBASE_API_KEY=
FIREBASE_PROJECT_ID=
FIREBASE_APP_ID=
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=
SENDGRID_API_KEY=
"""
    
    if not Path(".env").exists():
        with open(".env", "w", encoding="utf-8") as f:
            f.write(env_content)
        print("✓ تم إنشاء ملف .env")
    else:
        print("✓ ملف .env موجود مسبقاً")

def create_project_structure():
    """إنشاء هيكل المشروع"""
    directories = [
        "database",
        "uploads", 
        "logs",
        "tests",
        "static/css",
        "static/js", 
        "static/images",
        "templates"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✓ تم إنشاء هيكل المشروع")

def create_run_scripts():
    """إنشاء نصوص التشغيل"""
    
    # نص تشغيل التطوير - Windows
    run_dev_bat = """@echo off
echo تفعيل البيئة الافتراضية...
call venv\\Scripts\\activate.bat

echo تحميل متغيرات البيئة...
set FLASK_ENV=development
set FLASK_APP=main.py
set FLASK_DEBUG=1

echo تشغيل خادم التطوير...
echo الرابط: http://localhost:5000
echo البريد: admin@nuzum.com
echo كلمة المرور: admin123
echo للإيقاف: اضغط Ctrl+C

python main.py
pause
"""
    
    # نص تشغيل التطوير - Linux/Mac
    run_dev_sh = """#!/bin/bash
echo "تفعيل البيئة الافتراضية..."
source venv/bin/activate

echo "تحميل متغيرات البيئة..."
export FLASK_ENV=development
export FLASK_APP=main.py
export FLASK_DEBUG=1

echo "تشغيل خادم التطوير..."
echo "الرابط: http://localhost:5000"
echo "البريد: admin@nuzum.com"
echo "كلمة المرور: admin123"
echo "للإيقاف: اضغط Ctrl+C"

python main.py
"""
    
    with open("run_dev.bat", "w", encoding="utf-8") as f:
        f.write(run_dev_bat)
    
    with open("run_dev.sh", "w", encoding="utf-8") as f:
        f.write(run_dev_sh)
    
    # تعيين صلاحيات التنفيذ لنظام Linux/Mac
    if sys.platform != "win32":
        os.chmod("run_dev.sh", 0o755)
    
    print("✓ تم إنشاء نصوص التشغيل")

def setup_database():
    """إعداد قاعدة البيانات المحلية"""
    print("إعداد قاعدة البيانات...")
    
    try:
        # استيراد التطبيق مع معالجة المسار
        sys.path.insert(0, os.getcwd())
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
                print("✓ تم إنشاء المستخدم الإداري")
            else:
                print("✓ المستخدم الإداري موجود مسبقاً")
                
        return True
    except Exception as e:
        print(f"❌ خطأ في إعداد قاعدة البيانات: {e}")
        return False

def create_readme():
    """إنشاء ملف README للمطورين"""
    readme_content = """# نظام إدارة الموظفين نُظم

## إعداد بيئة التطوير

### 1. المتطلبات
- Python 3.8+
- VS Code
- Git

### 2. إعداد المشروع
```bash
# تشغيل نص الإعداد
python setup_vscode.py

# أو تفعيل البيئة الافتراضية يدوياً
# Windows:
venv\\Scripts\\activate
# Linux/Mac:
source venv/bin/activate

# تثبيت المكتبات
pip install -r requirements_vscode.txt
```

### 3. تشغيل النظام
```bash
# Windows:
run_dev.bat

# Linux/Mac:
./run_dev.sh

# أو مباشرة:
python main.py
```

### 4. الوصول للنظام
- الرابط: http://localhost:5000
- البريد: admin@nuzum.com
- كلمة المرور: admin123

### 5. أوامر VS Code المفيدة
- `Ctrl+Shift+P` ثم `Python: Select Interpreter` لاختيار البيئة الافتراضية
- `F5` لتشغيل النظام مع التصحيح
- `Ctrl+Shift+` لفتح Terminal مع البيئة الافتراضية

### 6. هيكل المشروع
```
nuzum/
├── app.py              # التطبيق الرئيسي
├── main.py             # نقطة الدخول
├── models.py           # نماذج قاعدة البيانات
├── routes/             # مسارات التطبيق
├── templates/          # قوالب HTML
├── static/             # ملفات CSS/JS/Images
├── database/           # قاعدة البيانات SQLite
├── uploads/            # الملفات المرفوعة
├── tests/              # اختبارات الوحدة
├── .vscode/            # إعدادات VS Code
└── venv/               # البيئة الافتراضية
```

### 7. الاختبار
```bash
# تشغيل الاختبارات
python -m pytest tests/

# تشغيل مع التغطية
python -m pytest --cov=app tests/
```

### 8. استكشاف الأخطاء
- تحقق من ملف `.env`
- تأكد من تشغيل البيئة الافتراضية
- راجع سجلات الأخطاء في VS Code Terminal
"""
    
    with open("README_DEV.md", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("✓ تم إنشاء دليل المطورين")

def main():
    """الدالة الرئيسية"""
    print("=" * 50)
    print("إعداد بيئة التطوير لنظام نُظم في VS Code")
    print("=" * 50)
    
    # إنشاء هيكل المشروع
    create_project_structure()
    
    # إنشاء البيئة الافتراضية
    python_path, pip_path = create_virtual_environment()
    if not python_path:
        return False
    
    # تثبيت المكتبات
    if not install_requirements(pip_path):
        return False
    
    # إنشاء إعدادات VS Code
    create_vscode_settings()
    
    # إنشاء ملف البيئة
    create_env_file()
    
    # إنشاء نصوص التشغيل
    create_run_scripts()
    
    # إعداد قاعدة البيانات
    if not setup_database():
        print("تحذير: قد تحتاج لإعداد قاعدة البيانات يدوياً")
    
    # إنشاء دليل المطورين
    create_readme()
    
    print("=" * 50)
    print("تم إكمال الإعداد بنجاح!")
    print("=" * 50)
    print("خطوات البدء:")
    print("1. افتح VS Code في هذا المجلد")
    print("2. اختر البيئة الافتراضية Python Interpreter")
    print("3. شغل المشروع بالضغط على F5")
    print("4. أو استخدم: python main.py")
    print("")
    print("الرابط: http://localhost:5000")
    print("تسجيل الدخول: admin@nuzum.com / admin123")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)