#!/bin/bash

# نص تشغيل نشر المشروع على VPS Hostinger
echo "===== بدء عملية نشر نظام نُظم ====="

# التأكد من وجود Docker و Docker Compose
if ! command -v docker &> /dev/null; then
    echo "تثبيت Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    sudo usermod -aG docker $USER
fi

if ! command -v docker-compose &> /dev/null; then
    echo "تثبيت Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# إنشاء المجلدات المطلوبة
echo "إنشاء المجلدات المطلوبة..."
mkdir -p uploads logs backup ssl

# تعيين الصلاحيات
sudo chown -R $USER:$USER .
chmod +x deployment/deploy.sh

# إنشاء شهادة SSL ذاتية التوقيع (للاختبار)
if [ ! -f ssl/cert.pem ]; then
    echo "إنشاء شهادة SSL للاختبار..."
    openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes \
        -subj "/C=SA/ST=Riyadh/L=Riyadh/O=Nuzum/CN=localhost"
fi

# إيقاف الحاويات السابقة إن وجدت
echo "إيقاف الحاويات السابقة..."
docker-compose down

# بناء وتشغيل الحاويات
echo "بناء وتشغيل النظام..."
docker-compose up --build -d

# انتظار تشغيل قاعدة البيانات
echo "انتظار تشغيل قاعدة البيانات..."
sleep 30

# تشغيل migration للجداول
echo "إنشاء جداول قاعدة البيانات..."
docker-compose exec web python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('تم إنشاء جداول قاعدة البيانات بنجاح')
"

# إنشاء مستخدم إدارة افتراضي
echo "إنشاء مستخدم إدارة افتراضي..."
docker-compose exec web python -c "
from app import app, db
from models import User, UserRole

with app.app_context():
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
        print('تم إنشاء مستخدم الإدارة: admin / admin123')
    else:
        print('مستخدم الإدارة موجود مسبقاً')
"

echo "===== تم إكمال النشر بنجاح ====="
echo "الموقع متاح على:"
echo "HTTP: http://your-server-ip"
echo "HTTPS: https://your-server-ip"
echo ""
echo "بيانات الدخول الافتراضية:"
echo "اسم المستخدم: admin"
echo "كلمة المرور: admin123"
echo ""
echo "لمراقبة السجلات: docker-compose logs -f"
echo "لإيقاف النظام: docker-compose down"