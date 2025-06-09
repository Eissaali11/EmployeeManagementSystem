# دليل التشغيل المحلي لنظام نُظم في CURSOR

## المتطلبات الأساسية
- Python 3.11 أو أحدث
- CURSOR أو VS Code
- Git

## خطوات الإعداد

### 1. إنشاء البيئة الافتراضية
```bash
# في terminal داخل CURSOR
python -m venv venv

# تفعيل البيئة الافتراضية
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 2. تثبيت المكتبات
```bash
pip install -r local_requirements.txt
```

### 3. إعداد متغيرات البيئة
```bash
# نسخ ملف البيئة المحلية
cp .env.local .env
```

### 4. إنشاء قاعدة البيانات
```bash
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('Database created successfully')"
```

### 5. تشغيل النظام
```bash
python main.py
```

## إعداد CURSOR

### في settings.json أضف:
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.terminal.activateEnvironment": true,
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        "venv/": true
    }
}
```

## استكشاف الأخطاء الشائعة

### خطأ: Module not found
```bash
# تأكد من تفعيل البيئة الافتراضية
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# إعادة تثبيت المكتبات
pip install -r local_requirements.txt
```

### خطأ: Database error
```bash
# حذف قاعدة البيانات وإعادة إنشائها
rm nuzum_local.db
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### خطأ: Port already in use
```bash
# تغيير المنفذ في main.py أو إيقاف العملية
python main.py --port 5001
```

## البيانات التجريبية
```bash
# إنشاء مستخدم تجريبي
python create_test_data.py
```

## أوامر مفيدة
```bash
# فحص المكتبات المثبتة
pip list

# تحديث المكتبات
pip install --upgrade -r local_requirements.txt

# تشغيل مع debug
export FLASK_DEBUG=1 && python main.py

# فحص قاعدة البيانات
python -c "from app import app, db; from models import *; app.app_context().push(); print('Tables:', db.engine.table_names())"
```