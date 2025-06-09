#!/bin/bash

# CloudPanel Deployment Script for نُظم Employee Management System
echo "=== بدء نشر نظام نُظم على CloudPanel ==="

# Update system packages
echo "تحديث حزم النظام..."
sudo apt update && sudo apt upgrade -y

# Install Python 3.11 and pip if not available
echo "تثبيت Python 3.11..."
sudo apt install python3.11 python3.11-pip python3.11-venv -y

# Install system dependencies for WeasyPrint and image processing
echo "تثبيت التبعيات النظام..."
sudo apt install -y \
    libpango-1.0-0 \
    libharfbuzz0b \
    libpangoft2-1.0-0 \
    libfontconfig1 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info \
    libpq-dev \
    gcc \
    g++ \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    tcl8.6-dev \
    tk8.6-dev \
    python3-tk

# Create virtual environment
echo "إنشاء البيئة الافتراضية..."
python3.11 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "تحديث pip..."
pip install --upgrade pip

# Install Python packages
echo "تثبيت حزم Python..."
pip install -r cloudpanel_requirements.txt

# Create systemd service file
echo "إنشاء خدمة systemd..."
sudo tee /etc/systemd/system/nuzum.service > /dev/null <<EOF
[Unit]
Description=Nuzum Employee Management System
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/home/cloudpanel/htdocs/nuzum.yourdomain.com
Environment=PATH=/home/cloudpanel/htdocs/nuzum.yourdomain.com/venv/bin
ExecStart=/home/cloudpanel/htdocs/nuzum.yourdomain.com/venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 3 --timeout 120 main:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Create nginx configuration
echo "إنشاء تكوين Nginx..."
sudo tee /etc/nginx/sites-available/nuzum > /dev/null <<EOF
server {
    listen 80;
    server_name nuzum.yourdomain.com www.nuzum.yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
    
    location /static {
        alias /home/cloudpanel/htdocs/nuzum.yourdomain.com/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    client_max_body_size 50M;
}
EOF

# Enable nginx site
sudo ln -sf /etc/nginx/sites-available/nuzum /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# Set proper permissions
echo "تعيين الصلاحيات..."
sudo chown -R www-data:www-data /home/cloudpanel/htdocs/nuzum.yourdomain.com
sudo chmod -R 755 /home/cloudpanel/htdocs/nuzum.yourdomain.com

# Create uploads directory
mkdir -p static/uploads/employees
sudo chown -R www-data:www-data static/uploads
sudo chmod -R 755 static/uploads

# Enable and start service
echo "تشغيل الخدمة..."
sudo systemctl daemon-reload
sudo systemctl enable nuzum
sudo systemctl start nuzum

echo "=== تم النشر بنجاح ==="
echo "يرجى تحديث متغيرات البيئة في ملف .env"
echo "وتكوين قاعدة البيانات PostgreSQL"
EOF