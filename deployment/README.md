# دليل نشر نظام نُظم

## متطلبات النشر

### المتطلبات الأساسية
- Docker و Docker Compose
- نظام تشغيل Linux (Ubuntu 20.04+ مُوصى به)
- ذاكرة وصول عشوائي: 2GB كحد أدنى، 4GB مُوصى به
- مساحة تخزين: 10GB كحد أدنى

### قواعد البيانات المدعومة
- PostgreSQL 15+ (افتراضي ومُوصى به)
- MySQL 8.0+ (دعم إضافي)

## خطوات النشر

### 1. تحضير الخادم
```bash
# تحديث النظام
sudo apt update && sudo apt upgrade -y

# تثبيت Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# تثبيت Docker Compose
sudo apt install docker-compose -y

# إضافة المستخدم إلى مجموعة docker
sudo usermod -aG docker $USER
```

### 2. رفع ملفات النظام
```bash
# فك ضغط حزمة النشر
tar -xzf nuzum_deployment.tar.gz
cd nuzum_deployment

# تعيين الصلاحيات
chmod +x deployment/deploy.sh
```

### 3. تشغيل النظام
```bash
# تشغيل نص النشر
./deployment/deploy.sh
```

## إعدادات قاعدة البيانات

### PostgreSQL (افتراضي)
```
المستخدم: nuzum_user
كلمة المرور: nuzum_secure_pass_2024
قاعدة البيانات: nuzum_db
المنفذ: 5432
```

### متغيرات البيئة
```
DATABASE_URL=postgresql://nuzum_user:nuzum_secure_pass_2024@db:5432/nuzum_db
SESSION_SECRET=nuzum_session_secret_key_2024_secure
```

## بيانات تسجيل الدخول الافتراضية

```
البريد الإلكتروني: admin@nuzum.com
كلمة المرور: admin123
```

## الخدمات الخارجية (اختيارية)

### Firebase للمصادقة
```bash
# تعيين متغيرات Firebase
export FIREBASE_API_KEY="your_api_key"
export FIREBASE_PROJECT_ID="your_project_id" 
export FIREBASE_APP_ID="your_app_id"
```

### Twilio للرسائل النصية
```bash
export TWILIO_ACCOUNT_SID="your_account_sid"
export TWILIO_AUTH_TOKEN="your_auth_token"
export TWILIO_PHONE_NUMBER="your_phone_number"
```

## أوامر الإدارة

```bash
# مراقبة السجلات
docker-compose logs -f

# إعادة تشغيل الخدمات
docker-compose restart

# إيقاف النظام
docker-compose down

# تشغيل النظام
docker-compose up -d

# تحديث النظام
docker-compose pull
docker-compose up -d --build
```

## استكشاف الأخطاء

### مشاكل قاعدة البيانات
```bash
# فحص حالة قاعدة البيانات
docker-compose exec db psql -U nuzum_user -d nuzum_db -c "\dt"

# إعادة إنشاء قاعدة البيانات
docker-compose down -v
docker-compose up -d
```

### مشاكل الشبكة
```bash
# فحص المنافذ
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :5000

# فحص جدار الحماية
sudo ufw status
```

## الأمان

### تحديث كلمات المرور
يُنصح بتغيير كلمات المرور الافتراضية:

1. كلمة مرور قاعدة البيانات في `docker-compose.yml`
2. SESSION_SECRET في متغيرات البيئة
3. كلمة مرور المدير من لوحة التحكم

### جدار الحماية
```bash
sudo ufw enable
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp  
sudo ufw allow 443/tcp
```

## النسخ الاحتياطي

```bash
# نسخ احتياطي لقاعدة البيانات
docker-compose exec db pg_dump -U nuzum_user nuzum_db > backup_$(date +%Y%m%d).sql

# نسخ احتياطي للملفات المرفوعة
tar -czf uploads_backup_$(date +%Y%m%d).tar.gz uploads/
```

## الدعم الفني

في حالة وجود مشاكل، يرجى التحقق من:
1. سجلات النظام: `docker-compose logs`
2. حالة الخدمات: `docker-compose ps`
3. مساحة التخزين: `df -h`
4. الذاكرة المتاحة: `free -m`