#!/bin/bash
# إعداد سريع لـ CloudPanel

echo "=== إعداد سريع لنظام نُظم ==="

# تعيين الصلاحيات
chmod +x cloudpanel_deploy.sh

# نسخ قالب البيئة
cp cloudpanel_env_template.txt .env

echo "تم الإعداد الأولي"
echo "يرجى تعديل ملف .env بالقيم الفعلية"
echo "ثم تشغيل: ./cloudpanel_deploy.sh"
