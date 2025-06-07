# دليل النشر على VPS - نُظم

## متطلبات الخادم

### المواصفات الدنيا
- **المعالج**: 2 CPU cores
- **الذاكرة**: 4GB RAM
- **التخزين**: 20GB SSD
- **نظام التشغيل**: Ubuntu 20.04+ أو CentOS 8+
- **اتصال الشبكة**: 100Mbps

### البرامج المطلوبة
- Python 3.11+
- PostgreSQL 12+
- Nginx
- Git
- Supervisor (اختياري)

## خطوات النشر

### 1. تحضير الخادم

```bash
# تحديث النظام
sudo apt update && sudo apt upgrade -y

# تثبيت المتطلبات الأساسية
sudo apt install -y python3.11 python3.11-venv python3-pip postgresql nginx git curl

# إنشاء مستخدم التطبيق
sudo useradd -r -s /bin/false www-data
```

### 2. رفع الملفات

```bash
# رفع حزمة النشر إلى الخادم
scp nuzum_deployment_*.zip user@your-server:/tmp/

# فك الضغط
sudo mkdir -p /var/www/nuzum
cd /var/www/nuzum
sudo unzip /tmp/nuzum_deployment_*.zip
```

### 3. تشغيل سكريپت التثبيت

```bash
cd /var/www/nuzum
sudo chmod +x deployment/install.sh
sudo bash deployment/install.sh
```

### 4. إعداد قاعدة البيانات

```bash
# الدخول إلى PostgreSQL
sudo -u postgres psql

-- إنشاء قاعدة البيانات والمستخدم
CREATE DATABASE nuzum_db;
CREATE USER nuzum_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE nuzum_db TO nuzum_user;
ALTER USER nuzum_user CREATEDB;
\q
```

### 5. إعداد متغيرات البيئة

```bash
cd /var/www/nuzum
sudo cp deployment/.env.example .env
sudo nano .env
```

محتوى ملف `.env`:
```env
DATABASE_URL=postgresql://nuzum_user:your_secure_password@localhost:5432/nuzum_db
SESSION_SECRET=your-very-long-random-secret-key-here
FLASK_ENV=production
FLASK_DEBUG=False
```

### 6. إعداد Nginx

```bash
# نسخ إعدادات Nginx
sudo cp deployment/nginx.conf /etc/nginx/sites-available/nuzum

# تحديث اسم النطاق
sudo nano /etc/nginx/sites-available/nuzum
# غيّر your-domain.com إلى نطاقك الحقيقي

# تفعيل الموقع
sudo ln -sf /etc/nginx/sites-available/nuzum /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# اختبار الإعدادات
sudo nginx -t
sudo systemctl reload nginx
```

### 7. إعداد خدمة النظام

```bash
# نسخ ملف الخدمة
sudo cp deployment/systemd.service /etc/systemd/system/nuzum.service

# إعادة تحميل systemd
sudo systemctl daemon-reload
sudo systemctl enable nuzum

# إنشاء جداول قاعدة البيانات
cd /var/www/nuzum
source venv/bin/activate
python -c "from app import app, db; app.app_context().push(); db.create_all()"

# بدء الخدمة
sudo systemctl start nuzum
```

### 8. إعداد شهادة SSL (Let's Encrypt)

```bash
# تثبيت Certbot
sudo apt install certbot python3-certbot-nginx

# الحصول على الشهادة
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# اختبار التجديد التلقائي
sudo certbot renew --dry-run
```

## التحقق من التثبيت

### 1. فحص الخدمات

```bash
# فحص حالة الخدمة
sudo systemctl status nuzum
sudo systemctl status nginx
sudo systemctl status postgresql

# مراقبة السجلات
sudo journalctl -u nuzum -f
```

### 2. اختبار الوصول

```bash
# اختبار محلي
curl -I http://localhost:5000

# اختبار عبر Nginx
curl -I http://your-domain.com
```

### 3. إنشاء المستخدم الأول

```bash
cd /var/www/nuzum
source venv/bin/activate
python -c "
from app import app, db
from models import User, UserRole
from werkzeug.security import generate_password_hash

with app.app_context():
    admin = User(
        name='مدير النظام',
        email='admin@yourcompany.com',
        username='admin',
        password_hash=generate_password_hash('admin123'),
        role=UserRole.ADMIN,
        is_active=True
    )
    db.session.add(admin)
    db.session.commit()
    print('تم إنشاء المستخدم الرئيسي')
"
```

## الصيانة والمراقبة

### أوامر مفيدة

```bash
# إعادة تشغيل التطبيق
sudo systemctl restart nuzum

# مراقبة السجلات المباشرة
sudo journalctl -u nuzum -f

# فحص استخدام الموارد
htop
df -h
free -h

# النسخ الاحتياطي لقاعدة البيانات
sudo -u postgres pg_dump nuzum_db > backup_$(date +%Y%m%d_%H%M%S).sql
```

### تحديث التطبيق

```bash
# إيقاف الخدمة
sudo systemctl stop nuzum

# نسخ احتياطية
sudo cp -r /var/www/nuzum /var/backups/nuzum_$(date +%Y%m%d)
sudo -u postgres pg_dump nuzum_db > /var/backups/nuzum_db_$(date +%Y%m%d).sql

# رفع الإصدار الجديد
sudo unzip /tmp/nuzum_new_version.zip -d /var/www/nuzum_new
sudo rsync -av /var/www/nuzum_new/ /var/www/nuzum/

# تحديث المتطلبات
cd /var/www/nuzum
source venv/bin/activate
pip install -r deployment/requirements.txt

# تطبيق تحديثات قاعدة البيانات (إن وجدت)
python -c "from app import app, db; app.app_context().push(); db.create_all()"

# إعادة تشغيل الخدمة
sudo systemctl start nuzum
```

### مراقبة الأداء

```bash
# مراقبة استخدام المعالج والذاكرة
watch -n 1 'ps aux | grep gunicorn'

# مراقبة اتصالات قاعدة البيانات
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity WHERE datname='nuzum_db';"

# فحص مساحة التخزين
du -sh /var/www/nuzum/
du -sh /var/lib/postgresql/
```

## استكشاف الأخطاء

### مشاكل شائعة وحلولها

#### 1. خطأ اتصال قاعدة البيانات
```bash
# فحص حالة PostgreSQL
sudo systemctl status postgresql

# فحص إعدادات الاتصال
sudo -u postgres psql -c "\l"

# إعادة تشغيل PostgreSQL
sudo systemctl restart postgresql
```

#### 2. خطأ صلاحيات الملفات
```bash
# إصلاح صلاحيات المجلد
sudo chown -R www-data:www-data /var/www/nuzum
sudo chmod -R 755 /var/www/nuzum
```

#### 3. خطأ Nginx
```bash
# فحص إعدادات Nginx
sudo nginx -t

# مراجعة سجلات الأخطاء
sudo tail -f /var/log/nginx/error.log
```

#### 4. مشاكل البيئة الافتراضية
```bash
# إعادة إنشاء البيئة الافتراضية
cd /var/www/nuzum
sudo rm -rf venv
python3.11 -m venv venv
source venv/bin/activate
pip install -r deployment/requirements.txt
```

## الأمان

### إعدادات الجدار الناري

```bash
# تفعيل UFW
sudo ufw enable

# السماح بالخدمات الأساسية
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'

# منع الوصول المباشر لتطبيق Flask
sudo ufw deny 5000
```

### تحديثات الأمان

```bash
# تحديث النظام بانتظام
sudo apt update && sudo apt upgrade -y

# مراقبة محاولات الدخول المشبوهة
sudo tail -f /var/log/auth.log

# تغيير كلمات المرور بانتظام
sudo -u postgres psql -c "ALTER USER nuzum_user PASSWORD 'new_secure_password';"
```

### النسخ الاحتياطية التلقائية

إنشاء سكريپت نسخ احتياطي في `/etc/cron.daily/nuzum-backup`:

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/nuzum"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# نسخ احتياطية لقاعدة البيانات
sudo -u postgres pg_dump nuzum_db > $BACKUP_DIR/db_$DATE.sql

# نسخ احتياطية للملفات المرفوعة
tar -czf $BACKUP_DIR/uploads_$DATE.tar.gz /var/www/nuzum/static/uploads/

# حذف النسخ القديمة (أكثر من 30 يوم)
find $BACKUP_DIR -name "*.sql" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

## الدعم الفني

للحصول على المساعدة:
1. راجع ملف DEVELOPER_GUIDE.md
2. تحقق من السجلات: `journalctl -u nuzum -f`
3. تأكد من إعدادات البيئة في ملف .env

النظام جاهز للعمل بكفاءة على خادم الإنتاج.