#!/bin/bash

# نص إعداد VPS لنظام نُظم
# يدعم SQLite، PostgreSQL، وMySQL

echo "====================================="
echo "إعداد VPS لنظام إدارة الموظفين نُظم"
echo "====================================="

# تحديد نوع قاعدة البيانات
DB_TYPE=${1:-sqlite}  # sqlite, postgresql, mysql

echo "نوع قاعدة البيانات المختار: $DB_TYPE"

# تحديث النظام
echo "تحديث النظام..."
apt update && apt upgrade -y

# تثبيت Python والمتطلبات الأساسية
echo "تثبيت Python والمتطلبات..."
apt install -y python3 python3-pip python3-venv git curl

# إنشاء بيئة Python الافتراضية
echo "إنشاء بيئة Python..."
python3 -m venv venv
source venv/bin/activate

# تثبيت المكتبات الأساسية
echo "تثبيت المكتبات الأساسية..."
pip install --upgrade pip
pip install Flask>=3.1.0 Flask-Login>=0.6.3 Flask-SQLAlchemy>=3.1.1 Flask-WTF>=1.2.2
pip install gunicorn>=23.0.0 python-dotenv>=1.1.0 Werkzeug>=3.1.3
pip install email-validator>=2.2.0 Pillow>=11.2.1 reportlab>=4.3.1
pip install openpyxl>=3.1.5 pandas>=2.2.3 numpy>=2.2.4
pip install arabic-reshaper>=3.0.0 python-bidi>=0.6.6 hijri-converter>=2.3.1

# تثبيت قاعدة البيانات حسب النوع المختار
case $DB_TYPE in
    postgresql)
        echo "تثبيت PostgreSQL..."
        apt install -y postgresql postgresql-contrib
        pip install psycopg2-binary>=2.9.10
        
        # إعداد قاعدة البيانات
        sudo -u postgres psql -c "CREATE USER nuzum_user WITH PASSWORD 'nuzum_secure_pass_2024';"
        sudo -u postgres psql -c "CREATE DATABASE nuzum_db OWNER nuzum_user;"
        sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE nuzum_db TO nuzum_user;"
        
        # إعداد متغير البيئة
        export DATABASE_URL="postgresql://nuzum_user:nuzum_secure_pass_2024@localhost:5432/nuzum_db"
        echo "DATABASE_URL=$DATABASE_URL" > .env
        ;;
        
    mysql)
        echo "تثبيت MySQL..."
        apt install -y mysql-server
        pip install PyMySQL>=1.1.1
        
        # إعداد قاعدة البيانات
        mysql -e "CREATE DATABASE nuzum_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
        mysql -e "CREATE USER 'nuzum_user'@'localhost' IDENTIFIED BY 'nuzum_secure_pass_2024';"
        mysql -e "GRANT ALL PRIVILEGES ON nuzum_db.* TO 'nuzum_user'@'localhost';"
        mysql -e "FLUSH PRIVILEGES;"
        
        # إعداد متغير البيئة
        export DATABASE_URL="mysql://nuzum_user:nuzum_secure_pass_2024@localhost:3306/nuzum_db"
        echo "DATABASE_URL=$DATABASE_URL" > .env
        ;;
        
    sqlite|*)
        echo "استخدام SQLite (افتراضي)..."
        # إنشاء مجلد قاعدة البيانات
        mkdir -p database
        
        # متغير البيئة اختياري لـ SQLite (سيستخدم النظام الافتراضي)
        echo "# SQLite يستخدم تلقائياً: database/nuzum.db" > .env
        ;;
esac

# إعداد متغيرات البيئة الإضافية
echo "SESSION_SECRET=nuzum_session_secret_key_2024_secure" >> .env
echo "FLASK_ENV=production" >> .env
echo "FLASK_APP=main.py" >> .env

# إنشاء مجلدات المشروع
echo "إنشاء مجلدات المشروع..."
mkdir -p uploads logs static templates

# إعداد خدمة systemd
echo "إعداد خدمة النظام..."
cat > /etc/systemd/system/nuzum.service << EOF
[Unit]
Description=نظام إدارة الموظفين نُظم
After=network.target

[Service]
User=root
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 main:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# تفعيل وتشغيل الخدمة
systemctl daemon-reload
systemctl enable nuzum
systemctl start nuzum

# إعداد Nginx (اختياري)
if command -v nginx >/dev/null 2>&1 || [ "$2" = "nginx" ]; then
    echo "إعداد Nginx..."
    apt install -y nginx
    
    cat > /etc/nginx/sites-available/nuzum << 'EOF'
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias $(pwd)/static/;
        expires 30d;
    }
    
    location /uploads/ {
        alias $(pwd)/uploads/;
        expires 7d;
    }
}
EOF
    
    ln -sf /etc/nginx/sites-available/nuzum /etc/nginx/sites-enabled/
    nginx -t && systemctl restart nginx
fi

# إنشاء المستخدم الإداري
echo "إنشاء المستخدم الإداري..."
python3 -c "
from app import app, db
from models import User, UserRole

with app.app_context():
    db.create_all()
    
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
        print('تم إنشاء مستخدم الإدارة: admin@nuzum.com / admin123')
    else:
        print('مستخدم الإدارة موجود مسبقاً')
"

# عرض معلومات النظام
echo "====================================="
echo "تم إكمال الإعداد بنجاح!"
echo "====================================="
echo "نوع قاعدة البيانات: $DB_TYPE"
echo "رابط النظام: http://$(curl -s ipinfo.io/ip)"
echo "رابط محلي: http://localhost"
echo ""
echo "بيانات تسجيل الدخول:"
echo "البريد الإلكتروني: admin@nuzum.com"
echo "كلمة المرور: admin123"
echo ""
echo "إدارة الخدمة:"
echo "حالة النظام: systemctl status nuzum"
echo "إعادة التشغيل: systemctl restart nuzum"
echo "مراقبة السجلات: journalctl -u nuzum -f"
echo "====================================="