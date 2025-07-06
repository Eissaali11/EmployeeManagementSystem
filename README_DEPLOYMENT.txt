# نُظم - نظام إدارة الموظفين
# CloudPanel Deployment Package

## محتويات الحزمة:

### للنشر على الخادم (CloudPanel):
1. cloudpanel_requirements.txt - متطلبات Python للخادم
2. cloudpanel_deploy.sh - سكريبت النشر الآلي
3. cloudpanel_env_template.txt - قالب متغيرات البيئة
4. cloudpanel_setup_guide.md - دليل النشر المفصل

### للتطوير المحلي (CURSOR/VS Code):
1. local_requirements.txt - متطلبات Python للتطوير
2. .env.local - متغيرات البيئة المحلية
3. run_local.py - تشغيل النظام محلياً
4. create_test_data.py - إنشاء بيانات تجريبية
5. setup_local.bat/sh - إعداد آلي للتطوير
6. LOCAL_SETUP_GUIDE.md - دليل التطوير المحلي
7. QUICK_START.md - بدء سريع

## بيانات تسجيل الدخول الافتراضية:
- المدير: skrkhtan@gmail.com
- مدير القسم: z.alhamdani@rassaudi.com
- بوابة الموظف: رقم 4298 / هوية 2489682019

## خطوات سريعة للنشر على الخادم:
1. رفع الملفات لمجلد الموقع في CloudPanel
2. تشغيل: chmod +x cloudpanel_deploy.sh && ./cloudpanel_deploy.sh
3. تكوين متغيرات البيئة في ملف .env
4. إنشاء قاعدة البيانات PostgreSQL
5. تشغيل الخدمة

## خطوات سريعة للتطوير المحلي:
### Windows:
setup_local.bat

### macOS/Linux:
chmod +x setup_local.sh && ./setup_local.sh

### يدوياً:
python run_local.py

للمزيد من التفاصيل، راجع الملفات المرفقة.
