# نشر سريع - نظام نُظم

## ملخص سريع للنشر على VPS Hostinger

### 1. متطلبات الخادم
- Ubuntu 20.04+ مع 4GB RAM و 50GB تخزين
- Docker & Docker Compose
- نطاق مؤشر إلى IP الخادم

### 2. خطوات النشر السريع

```bash
# 1. رفع المشروع للخادم
scp -r ./* root@your-server-ip:/var/www/nuzum/
cd /var/www/nuzum

# 2. تخصيص متغيرات البيئة
cp deployment/production.env .env
nano .env  # تعديل القيم المطلوبة

# 3. تشغيل النشر التلقائي
chmod +x deployment/deploy.sh
./deployment/deploy.sh

# 4. إعداد SSL (اختياري)
sudo certbot --nginx -d yourdomain.com
```

### 3. المتغيرات المطلوبة في .env

```env
# قاعدة البيانات - يجب تغييرها
DATABASE_URL=postgresql://user:password@localhost:5432/nuzum_db
SESSION_SECRET=your-unique-secret-key-here

# Firebase - احصل عليها من Firebase Console
FIREBASE_API_KEY=your-api-key
FIREBASE_PROJECT_ID=your-project-id  
FIREBASE_APP_ID=your-app-id

# Twilio للرسائل (اختياري)
TWILIO_ACCOUNT_SID=your-sid
TWILIO_AUTH_TOKEN=your-token
TWILIO_PHONE_NUMBER=your-number
```

### 4. الوصول للنظام

بعد النشر:
- **HTTP**: `http://your-server-ip`
- **HTTPS**: `https://your-domain.com` (بعد إعداد SSL)
- **بيانات الدخول الافتراضية**: admin / admin123

### 5. أوامر الإدارة

```bash
# مراقبة السجلات
docker-compose logs -f

# إعادة تشغيل
docker-compose restart

# إيقاف النظام
docker-compose down

# نسخة احتياطية
./deployment/backup.sh

# تحديث النظام
git pull && docker-compose up --build -d
```

### 6. استكشاف الأخطاء

**مشكلة الذاكرة:**
```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

**مشاكل الصلاحيات:**
```bash
sudo chown -R $USER:$USER /var/www/nuzum
```

**إعادة بناء الحاويات:**
```bash
docker-compose down
docker-compose up --build -d
```

### 7. الأمان الأساسي

```bash
# Firewall
sudo ufw enable
sudo ufw allow 22,80,443/tcp

# Fail2ban
sudo apt install fail2ban
sudo systemctl enable fail2ban
```

---

## ملفات النشر المُنشأة:

✅ `docker-compose.yml` - تكوين الحاويات الرئيسي
✅ `nginx.conf` - إعدادات Nginx مع SSL
✅ `deployment/deploy.sh` - نص النشر التلقائي  
✅ `deployment/production.env` - متغيرات البيئة للإنتاج
✅ `deployment/backup.sh` - نص النسخ الاحتياطي
✅ `deployment/README_DEPLOYMENT.md` - دليل النشر المفصل

**النظام جاهز للنشر على أي VPS يدعم Docker!**