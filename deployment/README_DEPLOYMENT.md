# دليل النشر - نظام نُظم لإدارة الموظفين والمركبات

## متطلبات الخادم

### المتطلبات الأساسية
- **نظام التشغيل**: Ubuntu 20.04 LTS أو أحدث
- **الذاكرة**: 4GB RAM كحد أدنى (8GB مستحسن)
- **التخزين**: 50GB مساحة فارغة كحد أدنى
- **المعالج**: 2 CPU cores كحد أدنى

### البرامج المطلوبة
- Docker Engine 20.10+
- Docker Compose 2.0+
- PostgreSQL 13+
- Nginx 1.18+
- Certbot (للحصول على شهادات SSL)

## خطوات النشر على VPS Hostinger

### 1. إعداد الخادم

```bash
# تحديث النظام
sudo apt update && sudo apt upgrade -y

# تثبيت المتطلبات الأساسية
sudo apt install -y curl wget git unzip

# تثبيت Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# تثبيت Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 2. رفع ملفات المشروع

```bash
# إنشاء مجلد المشروع
mkdir -p /var/www/nuzum
cd /var/www/nuzum

# رفع ملفات المشروع (استخدم Git أو SCP)
git clone <repository-url> .
# أو
scp -r ./project-files/* root@your-server-ip:/var/www/nuzum/
```

### 3. تكوين متغيرات البيئة

```bash
# نسخ ملف البيئة وتخصيصه
cp deployment/production.env .env

# تحرير الملف وتعديل القيم
nano .env
```

**قيم مهمة يجب تخصيصها:**
- `DATABASE_URL`: رابط قاعدة البيانات
- `SESSION_SECRET`: مفتاح آمن للجلسات
- `FIREBASE_*`: بيانات Firebase
- `ALLOWED_HOSTS`: نطاق موقعك

### 4. تشغيل النشر

```bash
# جعل ملف النشر قابل للتنفيذ
chmod +x deployment/deploy.sh

# تشغيل النشر
./deployment/deploy.sh
```

### 5. إعداد النطاق والـ SSL

```bash
# تثبيت Certbot
sudo apt install certbot python3-certbot-nginx

# الحصول على شهادة SSL
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# تجديد تلقائي للشهادة
sudo crontab -e
# إضافة السطر التالي:
0 12 * * * /usr/bin/certbot renew --quiet
```

## إعداد قاعدة البيانات

### PostgreSQL الخارجي (مستحسن للإنتاج)

```bash
# الاتصال بقاعدة البيانات
psql -h your-db-host -U your-db-user -d your-db-name

# إنشاء قاعدة البيانات والمستخدم
CREATE DATABASE nuzum_production;
CREATE USER nuzum_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE nuzum_production TO nuzum_user;
```

## مراقبة النظام

### عرض سجلات النظام
```bash
# سجلات جميع الخدمات
docker-compose logs -f

# سجلات خدمة معينة
docker-compose logs -f web
docker-compose logs -f db
```

### فحص حالة الخدمات
```bash
# حالة الحاويات
docker-compose ps

# استهلاك الموارد
docker stats
```

## النسخ الاحتياطية

### تشغيل النسخ الاحتياطي
```bash
# نسخ احتياطي يدوي
./deployment/backup.sh

# جدولة النسخ الاحتياطي التلقائي
crontab -e
# إضافة السطر التالي للنسخ اليومي في 2:00 صباحاً:
0 2 * * * /var/www/nuzum/deployment/backup.sh
```

## استكشاف الأخطاء

### مشاكل شائعة وحلولها

1. **فشل بناء الحاوية**
   ```bash
   docker-compose build --no-cache
   docker-compose up -d
   ```

2. **مشاكل قاعدة البيانات**
   ```bash
   docker-compose exec db psql -U username -d nuzum_db
   ```

3. **مشاكل الصلاحيات**
   ```bash
   sudo chown -R $USER:$USER /var/www/nuzum
   chmod -R 755 /var/www/nuzum
   ```

4. **مشاكل الذاكرة**
   ```bash
   # زيادة swap
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

## تحديث النظام

```bash
# إيقاف النظام
docker-compose down

# تحديث الكود
git pull origin main

# إعادة بناء وتشغيل
docker-compose up --build -d

# تشغيل migrations إذا لزم الأمر
docker-compose exec web python -c "
from app import app, db
with app.app_context():
    db.create_all()
"
```

## الأمان

### إعدادات الحماية الأساسية

1. **Firewall**
   ```bash
   sudo ufw enable
   sudo ufw allow 22/tcp
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   ```

2. **فشل المحاولات المتكررة**
   ```bash
   sudo apt install fail2ban
   sudo systemctl enable fail2ban
   ```

3. **تحديثات أمنية تلقائية**
   ```bash
   sudo apt install unattended-upgrades
   sudo dpkg-reconfigure unattended-upgrades
   ```

## الدعم

للحصول على المساعدة:
1. راجع سجلات النظام أولاً
2. تأكد من تكوين متغيرات البيئة
3. تحقق من حالة الخدمات
4. راجع هذا الدليل للحلول الشائعة

---

**ملاحظة مهمة**: تأكد من إجراء نسخة احتياطية قبل أي تغييرات كبيرة في النظام.