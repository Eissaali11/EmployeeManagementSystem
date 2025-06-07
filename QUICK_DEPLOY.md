# النشر السريع على VPS - نُظم

## الملفات المطلوبة للنقل

### 1. حزمة النشر الرئيسية
- **الملف**: `nuzum_deployment_20250607_184309.zip` (13.49 MB)
- **المحتوى**: جميع ملفات التطبيق، القوالب، الملفات الثابتة، وأدوات النشر

### 2. الأوامر السريعة للنشر

```bash
# 1. رفع الحزمة إلى الخادم
scp nuzum_deployment_20250607_184309.zip root@your-server-ip:/tmp/

# 2. تسجيل الدخول للخادم
ssh root@your-server-ip

# 3. فك الضغط وبدء التثبيت
cd /var/www
mkdir -p nuzum
cd nuzum
unzip /tmp/nuzum_deployment_20250607_184309.zip
chmod +x deployment/install.sh
./deployment/install.sh

# 4. تحديث إعدادات قاعدة البيانات
nano .env
# غيّر DATABASE_URL إلى الإعدادات الصحيحة

# 5. تحديث اسم النطاق
nano /etc/nginx/sites-available/nuzum
# غيّر your-domain.com إلى نطاقك

# 6. إعادة تشغيل الخدمات
systemctl restart nuzum nginx
```

## بيانات الدخول الافتراضية

بعد التثبيت، قم بإنشاء المستخدم الأول:

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
        email='admin@company.com',
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

**بيانات الدخول:**
- البريد الإلكتروني: `admin@company.com`
- كلمة المرور: `admin123`

⚠️ **هام**: غيّر كلمة المرور فور تسجيل الدخول الأول

## الملفات المهمة

### إعدادات قاعدة البيانات (.env)
```env
DATABASE_URL=postgresql://nuzum_user:your_password@localhost:5432/nuzum_db
SESSION_SECRET=your-random-secret-key
FLASK_ENV=production
```

### إعدادات Nginx
- الملف: `/etc/nginx/sites-available/nuzum`
- غيّر `your-domain.com` إلى نطاقك الحقيقي

### خدمة النظام
- الملف: `/etc/systemd/system/nuzum.service`
- الأوامر: `systemctl start/stop/restart nuzum`

## التحقق من التثبيت

```bash
# فحص حالة الخدمات
systemctl status nuzum nginx postgresql

# اختبار الوصول
curl -I http://localhost:5000
curl -I http://your-domain.com

# مراقبة السجلات
journalctl -u nuzum -f
```

## المجلدات المهمة

- **التطبيق**: `/var/www/nuzum`
- **السجلات**: `/var/log/nuzum/`
- **رفع الملفات**: `/var/www/nuzum/static/uploads/`
- **النسخ الاحتياطية**: `/var/backups/nuzum/`

## الدعم الفني

في حالة المشاكل، راجع:
1. `deployment/DEPLOYMENT_GUIDE.md` - دليل النشر التفصيلي
2. `DEVELOPER_GUIDE.md` - دليل المطور
3. السجلات: `journalctl -u nuzum -f`

النظام جاهز للعمل فور إكمال هذه الخطوات.