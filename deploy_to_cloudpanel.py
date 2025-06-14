#!/usr/bin/env python3
"""
أداة النشر المباشر لنظام نُظم على CloudPanel VPS
"""

import os
import shutil
import subprocess
import zipfile
import datetime
from pathlib import Path

def create_cloudpanel_deployment():
    """إنشاء حزمة النشر المباشر لـ CloudPanel"""
    
    print("🚀 بدء إنشاء حزمة النشر لـ CloudPanel...")
    
    # اسم الحزمة مع التاريخ
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    package_name = f"nuzum_cloudpanel_deploy_{timestamp}"
    
    # إنشاء مجلد مؤقت
    temp_dir = Path(package_name)
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()
    
    # قائمة الملفات والمجلدات المطلوبة
    required_files = [
        'app.py',
        'main.py', 
        'models.py',
        'cloudpanel_requirements.txt',
        'cloudpanel_deploy.sh',
        'cloudpanel_env_template.txt',
        'cloudpanel_setup_guide.md',
        'routes/',
        'templates/',
        'static/',
        'forms/',
        'utils/',
        'services/',
        'core/',
        'fonts/',
        'config/',
        'functions/',
        'database/',
        'public/',
        'nginx.conf'
    ]
    
    # نسخ الملفات
    print("📁 نسخ ملفات المشروع...")
    for item in required_files:
        src = Path(item)
        if src.exists():
            dst = temp_dir / item
            if src.is_dir():
                shutil.copytree(src, dst, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.git'))
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
        else:
            print(f"⚠️  تحذير: {item} غير موجود")
    
    # إنشاء ملف النشر السريع
    quick_deploy = temp_dir / "quick_deploy.sh"
    with open(quick_deploy, 'w', encoding='utf-8') as f:
        f.write("""#!/bin/bash
# نشر سريع لنظام نُظم على CloudPanel

echo "🚀 بدء النشر السريع لنظام نُظم..."

# تحديد المسار
DOMAIN_PATH="/home/cloudpanel/htdocs/$(basename $(pwd))"
cd "$DOMAIN_PATH"

# جعل السكريبت قابل للتنفيذ
chmod +x cloudpanel_deploy.sh

# تشغيل النشر
./cloudpanel_deploy.sh

echo "✅ تم النشر بنجاح!"
echo "📝 لا تنس:"
echo "   1. تحديث ملف .env بمعلومات قاعدة البيانات"
echo "   2. إنشاء قاعدة البيانات PostgreSQL"
echo "   3. تشغيل: python -c 'from app import app, db; app.app_context().push(); db.create_all()'"
""")
    
    # جعل الملف قابل للتنفيذ
    os.chmod(quick_deploy, 0o755)
    
    # إنشاء ملف README للنشر
    readme = temp_dir / "DEPLOY_README.md"
    with open(readme, 'w', encoding='utf-8') as f:
        f.write("""# دليل النشر السريع - نظام نُظم

## خطوات النشر على CloudPanel VPS

### 1. رفع الملفات
```bash
# رفع جميع الملفات إلى مجلد الدومين في CloudPanel
scp -r nuzum_cloudpanel_deploy_* user@your-server:/home/cloudpanel/htdocs/yourdomain.com/
```

### 2. النشر السريع
```bash
ssh user@your-server
cd /home/cloudpanel/htdocs/yourdomain.com
./quick_deploy.sh
```

### 3. تكوين قاعدة البيانات
```bash
# إنشاء قاعدة بيانات PostgreSQL
sudo -u postgres createdb nuzum_db
sudo -u postgres createuser nuzum_user
sudo -u postgres psql -c "ALTER USER nuzum_user PASSWORD 'your_strong_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE nuzum_db TO nuzum_user;"
```

### 4. تحديث متغيرات البيئة
```bash
# نسخ وتعديل ملف البيئة
cp cloudpanel_env_template.txt .env
nano .env
# تحديث DATABASE_URL و FLASK_SECRET_KEY
```

### 5. إنشاء الجداول
```bash
source venv/bin/activate
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### 6. التحقق من الخدمة
```bash
sudo systemctl status nuzum
sudo systemctl restart nuzum
```

## متطلبات النظام
- Ubuntu 20.04+
- CloudPanel مثبت
- PostgreSQL 12+
- Python 3.11
- Nginx

## الدعم والمساعدة
في حالة وجود مشاكل، تحقق من:
- سجلات النظام: `sudo journalctl -u nuzum -f`
- سجلات Nginx: `sudo tail -f /var/log/nginx/error.log`
- حالة الخدمة: `sudo systemctl status nuzum`
""")
    
    # إنشاء ملف ZIP
    zip_name = f"{package_name}.zip"
    print(f"📦 إنشاء حزمة مضغوطة: {zip_name}")
    
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = Path(root) / file
                arcname = file_path.relative_to(temp_dir)
                zipf.write(file_path, arcname)
    
    # تنظيف المجلد المؤقت
    shutil.rmtree(temp_dir)
    
    print(f"✅ تم إنشاء حزمة النشر: {zip_name}")
    print(f"📏 حجم الحزمة: {os.path.getsize(zip_name) / 1024 / 1024:.2f} MB")
    
    print("\n🚀 خطوات النشر:")
    print("1. رفع الحزمة إلى الخادم وفك الضغط")
    print("2. تشغيل: ./quick_deploy.sh")
    print("3. تكوين قاعدة البيانات")
    print("4. تحديث ملف .env")
    print("5. إنشاء الجداول")
    
    return zip_name

if __name__ == "__main__":
    create_cloudpanel_deployment()