# تشغيل سريع لنظام نُظم في CURSOR

## الطريقة السريعة (Windows)
```cmd
setup_local.bat
```

## الطريقة السريعة (macOS/Linux)
```bash
chmod +x setup_local.sh
./setup_local.sh
```

## الطريقة اليدوية

### 1. إنشاء البيئة
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux  
source venv/bin/activate
```

### 2. تثبيت المكتبات
```bash
pip install flask flask-sqlalchemy flask-login flask-wtf werkzeug wtforms python-dotenv pillow reportlab arabic-reshaper python-bidi
```

### 3. إعداد البيئة
```bash
# نسخ ملف البيئة
cp .env.local .env
```

### 4. تشغيل النظام
```bash
python run_local.py
```

## الوصول للنظام
- الرابط: http://localhost:5000
- المستخدم: admin
- كلمة المرور: admin123

## اختبار بوابة الموظف
- رقم الموظف: EMP001
- رقم الهوية: 1234567890

## المشاكل الشائعة

### خطأ: No module named 'flask'
```bash
# تأكد من تفعيل البيئة الافتراضية
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# إعادة تثبيت
pip install -r local_requirements.txt
```

### خطأ: Port 5000 is already in use
```bash
# تغيير المنفذ
python -c "import os; os.environ['PORT']='5001'; exec(open('run_local.py').read())"
```

### قاعدة البيانات فارغة
```bash
python create_test_data.py
```