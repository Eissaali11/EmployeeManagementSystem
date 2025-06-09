# دليل نشر نظام نُظم على CloudPanel

## متطلبات النظام
- Ubuntu 20.04 أو أحدث
- CloudPanel مثبت ومُكوّن
- PostgreSQL 12 أو أحدث
- Python 3.11
- Nginx

## خطوات النشر

### 1. رفع الملفات
```bash
# رفع جميع ملفات المشروع إلى مجلد الموقع
cd /home/cloudpanel/htdocs/yourdomain.com
# رفع الملفات هنا
```

### 2. تثبيت التبعيات
```bash
chmod +x cloudpanel_deploy.sh
./cloudpanel_deploy.sh
```

### 3. تكوين قاعدة البيانات
```bash
# إنشاء قاعدة بيانات PostgreSQL
sudo -u postgres createdb nuzum_db
sudo -u postgres createuser nuzum_user
sudo -u postgres psql -c "ALTER USER nuzum_user PASSWORD 'your_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE nuzum_db TO nuzum_user;"
```

### 4. تكوين متغيرات البيئة
```bash
# نسخ قالب متغيرات البيئة
cp cloudpanel_env_template.txt .env
# تعديل المتغيرات بالقيم الفعلية
nano .env
```

### 5. إنشاء الجداول
```bash
source venv/bin/activate
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### 6. تشغيل النظام
```bash
sudo systemctl start nuzum
sudo systemctl enable nuzum
sudo systemctl status nuzum
```

## تكوين الدومين في CloudPanel

1. إضافة موقع جديد في CloudPanel
2. تحديد المجلد الجذر: `/home/cloudpanel/htdocs/yourdomain.com`
3. تفعيل SSL من Let's Encrypt
4. تكوين DNS للدومين

## الصيانة والمراقبة

### فحص حالة الخدمة
```bash
sudo systemctl status nuzum
sudo journalctl -u nuzum -f
```

### تحديث النظام
```bash
git pull origin main
source venv/bin/activate
pip install -r cloudpanel_requirements.txt
sudo systemctl restart nuzum
```

### النسخ الاحتياطي
```bash
# نسخ احتياطي لقاعدة البيانات
pg_dump -U nuzum_user -h localhost nuzum_db > backup_$(date +%Y%m%d_%H%M%S).sql

# نسخ احتياطي للملفات
tar -czf files_backup_$(date +%Y%m%d_%H%M%S).tar.gz static/uploads/
```

## استكشاف الأخطاء

### مشاكل شائعة:
1. **خطأ في الاتصال بقاعدة البيانات**: تحقق من متغيرات البيئة
2. **مشاكل الصلاحيات**: تأكد من صلاحيات www-data
3. **خطأ في الحزم**: تأكد من تثبيت جميع التبعيات النظام

### ملفات السجلات:
- سجلات التطبيق: `journalctl -u nuzum`
- سجلات Nginx: `/var/log/nginx/error.log`
- سجلات قاعدة البيانات: `/var/log/postgresql/`