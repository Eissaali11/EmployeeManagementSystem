#!/bin/bash

echo "========================================"
echo "       إعداد نظام نُظم للتطوير المحلي"
echo "========================================"

# فحص Python
if ! command -v python3 &> /dev/null; then
    echo "خطأ: Python 3 غير مثبت"
    exit 1
fi

echo "إنشاء البيئة الافتراضية..."
python3 -m venv venv

echo "تفعيل البيئة الافتراضية..."
source venv/bin/activate

echo "تثبيت المكتبات المطلوبة..."
pip install --upgrade pip
pip install -r local_requirements.txt

echo "إعداد متغيرات البيئة..."
cp .env.local .env

echo "إنشاء البيانات التجريبية..."
python create_test_data.py

echo "========================================"
echo "تم الإعداد بنجاح!"
echo "========================================"
echo "لتشغيل النظام:"
echo "  source venv/bin/activate"
echo "  python run_local.py"
echo "========================================"