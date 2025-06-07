#!/bin/bash

# سكريبت تثبيت نُظم على VPS
# يجب تشغيله بصلاحيات المدير (sudo)

set -e

echo "=== بدء تثبيت نُظم - نظام إدارة الموظفين والمركبات ==="

# متغيرات الإعداد
APP_NAME="nuzum"
APP_DIR="/var/www/$APP_NAME"
APP_USER="www-data"
DB_NAME="nuzum_db"
PYTHON_VERSION="3.11"

# التحقق من صلاحيات المدير
if [[ $EUID -ne 0 ]]; then
   echo "خطأ: يجب تشغيل هذا السكريبت بصلاحيات المدير (sudo)"
   exit 1
fi

echo "1. تحديث النظام..."
apt update && apt upgrade -y

echo "2. تثبيت المتطلبات الأساسية..."
apt install -y \
    python3.$PYTHON_VERSION \
    python3.$PYTHON_VERSION-venv \
    python3-pip \
    postgresql \
    postgresql-contrib \
    nginx \
    git \
    curl \
    supervisor \
    build-essential \
    libpq-dev \
    python3-dev \
    libffi-dev \
    libssl-dev \
    pkg-config \
    libcairo2-dev \
    libpango1.0-dev \
    libgdk-pixbuf2.0-dev \
    libffi-dev \
    shared-mime-info

echo "3. إنشاء مستخدم التطبيق إذا لم يكن موجوداً..."
if ! id "$APP_USER" &>/dev/null; then
    useradd -r -s /bin/false $APP_USER
fi

echo "4. إنشاء مجلدات التطبيق..."
mkdir -p $APP_DIR
mkdir -p /var/log/$APP_NAME
mkdir -p $APP_DIR/static/uploads

echo "5. إعداد قاعدة البيانات PostgreSQL..."
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME;" 2>/dev/null || echo "قاعدة البيانات موجودة مسبقاً"
sudo -u postgres psql -c "CREATE USER ${APP_NAME}_user WITH PASSWORD 'secure_password_123';" 2>/dev/null || echo "المستخدم موجود مسبقاً"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO ${APP_NAME}_user;"
sudo -u postgres psql -c "ALTER USER ${APP_NAME}_user CREATEDB;"

echo "6. نسخ ملفات التطبيق..."
# ملاحظة: يجب رفع ملفات التطبيق إلى $APP_DIR يدوياً أو عبر git
# cp -r /path/to/app/* $APP_DIR/

echo "7. إنشاء البيئة الافتراضية..."
cd $APP_DIR
python3.$PYTHON_VERSION -m venv venv
source venv/bin/activate

echo "8. تثبيت متطلبات Python..."
pip install --upgrade pip
pip install -r deployment/requirements.txt

echo "9. إعداد متغيرات البيئة..."
if [ ! -f "$APP_DIR/.env" ]; then
    cp deployment/.env.example .env
    echo "تم إنشاء ملف .env - يرجى تحديث المتغيرات"
fi

echo "10. إعداد صلاحيات الملفات..."
chown -R $APP_USER:$APP_USER $APP_DIR
chown -R $APP_USER:$APP_USER /var/log/$APP_NAME
chmod -R 755 $APP_DIR
chmod -R 755 /var/log/$APP_NAME

echo "11. إعداد Nginx..."
cp deployment/nginx.conf /etc/nginx/sites-available/$APP_NAME
ln -sf /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

echo "12. إعداد خدمة Systemd..."
cp deployment/systemd.service /etc/systemd/system/$APP_NAME.service
systemctl daemon-reload
systemctl enable $APP_NAME

echo "13. تشغيل قاعدة البيانات..."
cd $APP_DIR
source venv/bin/activate
python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('تم إنشاء جداول قاعدة البيانات')
"

echo "14. بدء الخدمات..."
systemctl start $APP_NAME
systemctl start nginx
systemctl enable nginx

echo "15. التحقق من حالة الخدمات..."
systemctl status $APP_NAME --no-pager
systemctl status nginx --no-pager

echo "=== تم الانتهاء من التثبيت ==="
echo ""
echo "خطوات ما بعد التثبيت:"
echo "1. قم بتحديث ملف .env بالإعدادات الصحيحة"
echo "2. قم بتحديث اسم النطاق في /etc/nginx/sites-available/$APP_NAME"
echo "3. قم بتثبيت شهادة SSL (Let's Encrypt موصى به)"
echo "4. أعد تشغيل الخدمات: systemctl restart $APP_NAME nginx"
echo ""
echo "أوامر مفيدة:"
echo "- مراقبة السجلات: journalctl -u $APP_NAME -f"
echo "- إعادة التشغيل: systemctl restart $APP_NAME"
echo "- التحقق من الحالة: systemctl status $APP_NAME"
echo ""
echo "التطبيق متاح الآن على: http://your-domain.com"