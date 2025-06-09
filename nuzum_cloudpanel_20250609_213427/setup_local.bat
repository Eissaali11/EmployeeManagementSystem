@echo off
echo ========================================
echo       إعداد نظام نُظم للتطوير المحلي
echo ========================================

echo إنشاء البيئة الافتراضية...
python -m venv venv

echo تفعيل البيئة الافتراضية...
call venv\Scripts\activate

echo تثبيت المكتبات المطلوبة...
pip install --upgrade pip
pip install -r local_requirements.txt

echo إعداد متغيرات البيئة...
copy .env.local .env

echo إنشاء البيانات التجريبية...
python create_test_data.py

echo ========================================
echo تم الإعداد بنجاح!
echo ========================================
echo لتشغيل النظام:
echo   python run_local.py
echo أو:
echo   python main.py
echo ========================================
pause