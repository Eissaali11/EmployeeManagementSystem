# دليل تحميل ملفات نُظم

## الملفات الأساسية المتاحة للتحميل:

### 1. الملفات الأساسية:
- `app.py` - التطبيق الرئيسي
- `main.py` - نقطة الدخول
- `models.py` - نماذج قاعدة البيانات

### 2. واجهة برمجة التطبيقات:
- `routes/restful_api.py` - RESTful API كامل
- `NUZUM_API_Collection.postman_collection.json` - مجموعة Postman
- `NUZUM_Environment.postman_environment.json` - بيئة Postman
- `API_DOCUMENTATION.md` - توثيق كامل للAPI

### 3. القوالب:
- `templates/base.html`
- `templates/dashboard.html` 
- `templates/login.html`
- `templates/index.html`
- `templates/errors/404.html`
- `templates/errors/500.html`

### 4. التوثيق:
- `README.md` - دليل المشروع
- `replit.md` - تاريخ وتفاصيل المشروع
- `POSTMAN_TESTING_GUIDE.md` - دليل الاختبار

## طرق الحصول على الملفات:

### 1. من Replit:
- انقر على Files في الشريط الجانبي
- انقر بزر الماوس الأيمن على أي ملف
- اختر "Download"

### 2. من Git Repository:
```bash
git clone <repository-url>
```

### 3. باستخدام Replit Export:
- اذهب إلى Settings
- اختر "Export as ZIP"

## معلومات النظام:
- البيانات: 59 موظف، 20 مركبة، 6 أقسام
- API: 25+ مسار
- المصادقة: admin@nuzum.sa / admin123
- قاعدة البيانات: PostgreSQL

## ملاحظات مهمة:
- ملف `.env` يحتوي على متغيرات البيئة المطلوبة
- تأكد من إعداد قاعدة البيانات عند النقل
- استخدم `requirements.txt` أو `pyproject.toml` للاعتماديات