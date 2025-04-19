# دليل نشر نظام إدارة الموظفين على استضافة Hostinger

هذا الدليل يوضح خطوات نشر نظام إدارة الموظفين المبني بإطار Flask على استضافة Hostinger.

## المتطلبات الأساسية

- حساب استضافة على Hostinger يدعم Python (خطة VPS أو Cloud)
- خادم ويب Apache أو Nginx
- دعم Python 3.9 أو أحدث
- قاعدة بيانات PostgreSQL

## الخطوة 1: إعداد قاعدة البيانات

1. قم بتسجيل الدخول إلى لوحة تحكم Hostinger
2. انتقل إلى قسم "قواعد البيانات" وأنشئ قاعدة بيانات PostgreSQL جديدة
3. لاحظ معلومات الاتصال التالية:
   - اسم قاعدة البيانات
   - اسم المستخدم
   - كلمة المرور
   - المضيف (غالباً "localhost")
   - المنفذ (غالباً 5432)

## الخطوة 2: رفع ملفات المشروع

1. قم بتحميل جميع ملفات المشروع باستثناء:
   - `__pycache__/`
   - `.git/`
   - أي ملفات إعدادات محلية أخرى
   
2. تأكد من رفع الملفات التالية الإضافية التي تم إنشاؤها:
   - `wsgi.py`
   - `requirements_deploy.txt` (يجب إعادة تسميته إلى `requirements.txt` بعد الرفع)
   - `.htaccess`
   - `setup.py`
   
3. يمكن استخدام FTP أو Git أو لوحة تحكم الملفات في Hostinger لرفع الملفات

## الخطوة 3: إعداد البيئة الافتراضية وتثبيت الحزم

1. اتصل بالخادم عبر SSH (إذا كان مدعوماً)
2. أنشئ بيئة افتراضية في مجلد المشروع:
   ```bash
   cd /path/to/your/project
   python3 -m venv venv
   source venv/bin/activate
   ```

3. قم بتثبيت الحزم المطلوبة:
   ```bash
   pip install -r requirements.txt
   ```

## الخطوة 4: إعداد المتغيرات البيئية

1. أنشئ ملف `.env` جديد بناءً على ملف `.env.example`:
   ```
   # قم بنسخ محتويات ملف .env.example وتعديل القيم حسب إعدادات الخادم
   DATABASE_URL=postgresql://username:password@localhost:5432/database_name
   SECRET_KEY=your_secure_random_key
   TWILIO_ACCOUNT_SID=your_twilio_sid
   TWILIO_AUTH_TOKEN=your_twilio_token
   TWILIO_PHONE_NUMBER=your_twilio_phone_number
   ```

2. إذا كانت استضافة Hostinger لا تدعم ملف `.env`، يمكنك تعيين المتغيرات البيئية في ملف تكوين Apache أو PHP:
   - لـ Apache: استخدم `SetEnv` في ملف `.htaccess`
   - لـ PHP: استخدم `putenv()` في ملف PHP يتم تحميله قبل التطبيق

## الخطوة 5: تهيئة قاعدة البيانات

1. قم بتشغيل سكريبت الإعداد:
   ```bash
   python setup.py
   ```

2. سيقوم هذا السكريبت بإنشاء جداول قاعدة البيانات وإنشاء مستخدم مسؤول افتراضي

## الخطوة 6: تكوين خادم الويب

### لـ Apache (ملف `.htaccess` موجود بالفعل)

تأكد من أن وحدة mod_wsgi مثبتة ومفعلة:
```
sudo apt-get install libapache2-mod-wsgi-py3
sudo a2enmod wsgi
```

### لـ Nginx

أنشئ ملف تكوين في `/etc/nginx/sites-available/your_domain`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        include proxy_params;
        proxy_pass http://unix:/path/to/your/project/app.sock;
    }
}
```

## الخطوة 7: إعداد Gunicorn

1. قم بتثبيت Gunicorn (مُضمّن في ملف requirements.txt)
2. أنشئ ملف خدمة systemd لتشغيل التطبيق:

```
[Unit]
Description=Gunicorn instance for Employee Management System
After=network.target

[Service]
User=your_user
Group=www-data
WorkingDirectory=/path/to/your/project
Environment="PATH=/path/to/your/project/venv/bin"
ExecStart=/path/to/your/project/venv/bin/gunicorn --workers 3 --bind unix:app.sock -m 007 wsgi:app

[Install]
WantedBy=multi-user.target
```

3. تفعيل وتشغيل الخدمة:
```bash
sudo systemctl enable your_service
sudo systemctl start your_service
```

## الخطوة 8: اختبار النظام

1. افتح متصفح ويب وانتقل إلى عنوان موقعك
2. قم بتسجيل الدخول باستخدام بيانات المستخدم الافتراضي:
   - البريد الإلكتروني: admin@example.com
   - كلمة المرور: admin123
3. بعد تسجيل الدخول، قم بتغيير كلمة المرور الافتراضية فوراً

## حل المشكلات الشائعة

### مشكلة 1: خطأ في الاتصال بقاعدة البيانات
- تحقق من صحة معلومات الاتصال في متغير `DATABASE_URL`
- تأكد من أن مستخدم قاعدة البيانات لديه صلاحيات كافية
- تحقق من أن خدمة PostgreSQL تعمل

### مشكلة 2: خطأ في تحميل الصفحات
- تحقق من سجلات الخطأ في Apache أو Nginx
- تأكد من أن ملف `.htaccess` تم رفعه بشكل صحيح
- تأكد من أن وحدة mod_wsgi مثبتة ومفعلة

### مشكلة 3: مشاكل في العرض أو الخطوط العربية
- تأكد من أن الترميز UTF-8 مفعل في خادم الويب
- تحقق من وجود الخطوط العربية في المجلد المناسب
- تأكد من تعيين المنطقة الزمنية الصحيحة

## ملاحظات هامة

- قم بتغيير كلمة مرور المستخدم الافتراضي فور تسجيل الدخول
- قم بتعطيل وضع التصحيح في الإنتاج عن طريق تعيين `FLASK_DEBUG=False`
- قم بإجراء نسخ احتياطي لقاعدة البيانات بانتظام
- تحقق من تحديثات الأمان لحزم Python المستخدمة
- استخدم HTTPS لتأمين نقل البيانات بين المستخدم والخادم

## المزيد من الموارد

- [توثيق Flask الرسمي](https://flask.palletsprojects.com/)
- [توثيق Gunicorn](https://docs.gunicorn.org/)
- [مركز مساعدة Hostinger](https://www.hostinger.com/tutorials/)