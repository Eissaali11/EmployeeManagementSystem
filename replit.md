# نُظم - Arabic Employee Management System

## Overview

نُظم is a comprehensive Arabic employee management system built with Flask, designed specifically for companies in Saudi Arabia. The system provides complete employee lifecycle management, vehicle tracking, attendance monitoring, and detailed reporting capabilities with full Arabic language support.

## System Architecture

### Frontend Architecture
- **Framework**: Flask with Jinja2 templates
- **Language Support**: Right-to-left (RTL) Arabic interface
- **Styling**: Bootstrap-based responsive design
- **Forms**: Flask-WTF for secure form handling
- **JavaScript**: Vanilla JS with Firebase integration for authentication

### Backend Architecture
- **Framework**: Flask 3.1.0 with modular blueprint structure
- **Architecture Pattern**: Modular Monolith with separated concerns
- **Database ORM**: SQLAlchemy 2.0+ with Flask-SQLAlchemy
- **Authentication**: Flask-Login with Firebase integration
- **Session Management**: Flask sessions with CSRF protection

### Database Architecture
- **Primary**: MySQL (production) with PyMySQL driver
- **Development**: SQLite for local development
- **ORM**: SQLAlchemy with declarative base models
- **Migrations**: Manual schema management

## Key Components

### Core Modules
1. **Employee Management** (`routes/employees.py`)
   - Full employee lifecycle (CRUD operations)
   - Department assignment and transfers
   - Document management with expiry tracking
   - Profile image and ID document uploads

2. **Vehicle Management** (`routes/vehicles.py`)
   - Vehicle registration and tracking
   - Handover/return documentation
   - Workshop maintenance records
   - Comprehensive vehicle reports

3. **Attendance System** (`routes/attendance.py`)
   - Daily attendance tracking
   - Overtime calculations
   - Monthly and weekly reports
   - Hijri calendar integration

4. **Salary Management** (`routes/salaries.py`)
   - Salary calculations and processing
   - Allowances and deductions
   - Monthly payroll reports
   - Saudi labor law compliance

5. **Department Management** (`routes/departments.py`)
   - Organizational structure
   - Department hierarchy
   - Manager assignments

6. **User Management** (`routes/users.py`)
   - Role-based access control
   - Permission management
   - User authentication and authorization

### Service Layer
- **Authentication Service** (`services/auth_service.py`): JWT tokens, Firebase integration
- **Notification Service** (`services/notification_service.py`): SMS via Twilio, email notifications
- **Report Service** (`services/report_service.py`): PDF/Excel generation with Arabic support
- **File Service** (`services/file_service.py`): Document upload and management

### Utility Components
- **Arabic PDF Generation** (`utils/`): Multiple PDF generators with Arabic text support
- **Excel Processing** (`utils/excel.py`): Import/export with Arabic encoding
- **Date Conversion** (`utils/date_converter.py`): Gregorian/Hijri calendar support
- **Audit Logging** (`utils/audit_logger.py`): Comprehensive activity tracking

## Data Flow

### Request Processing
1. Request enters through Flask application factory
2. CSRF validation and session verification
3. Authentication check via Flask-Login
4. Route handling with permission validation
5. Business logic execution in service layer
6. Database operations via SQLAlchemy ORM
7. Response rendering with Arabic text processing

### Report Generation
1. Data extraction from multiple related models
2. Arabic text reshaping using `arabic-reshaper`
3. Bidirectional text processing with `python-bidi`
4. PDF generation via ReportLab or WeasyPrint
5. Excel generation via openpyxl with RTL support

### File Upload Processing
1. Secure file validation and virus scanning
2. Image processing and thumbnail generation
3. Database metadata storage
4. Physical file storage in organized directory structure

## External Dependencies

### Core Dependencies
- **Flask 3.1.0**: Web framework
- **SQLAlchemy 2.0.40**: Database ORM
- **PyMySQL 1.1.1**: MySQL database driver
- **Flask-Login 0.6.3**: User session management
- **Flask-WTF 1.2.2**: Form handling and CSRF protection

### Arabic Text Processing
- **arabic-reshaper 3.0.0**: Arabic text reshaping
- **python-bidi 0.6.6**: Bidirectional text algorithm
- **hijri-converter 2.3.1**: Hijri calendar conversion

### PDF Generation
- **reportlab 4.3.1**: Primary PDF generation
- **weasyprint 65.1**: HTML-to-PDF conversion
- **fpdf 1.7.2**: Alternative PDF generation

### Data Processing
- **pandas 2.2.3**: Data manipulation
- **openpyxl 3.1.5**: Excel file handling
- **Pillow 11.2.1**: Image processing

### External Services
- **twilio 9.5.2**: SMS notifications
- **sendgrid 6.11.0**: Email services
- **Firebase SDK**: Authentication and storage

## Deployment Strategy

### Environment Support
- **Local Development**: SQLite database, `.env.local` configuration
- **Production**: MySQL database, environment-specific settings
- **Docker**: Multi-container setup with Nginx reverse proxy

### Configuration Management
- Environment-specific configuration files
- Secure secret management via environment variables
- Database URL flexibility (MySQL/PostgreSQL/SQLite)

### Deployment Options
1. **Docker Compose**: Complete containerized deployment
2. **CloudPanel**: VPS deployment with systemd service
3. **Traditional VPS**: Direct server deployment
4. **Replit**: Cloud development environment

### Security Measures
- CSRF protection on all forms
- SQL injection prevention via ORM
- File upload validation and sanitization
- Session security with secure cookies
- Environment variable protection

## Changelog
- July 8, 2025: **إضافة زر المشاركة المحسن للتفويضات الخارجية:**
  • إضافة زر مشاركة أخضر جديد لكل تفويض خارجي في الجدولين (المختصر والموسع)
  • رسالة تعريفية شاملة تبدأ بـ "مرحباً 👋" وتشمل وصف النظام
  • تفاصيل كاملة: اسم الموظف، نوع التفويض، التاريخ، المشروع، المدينة
  • رابط مباشر للنموذج وتفاصيل التفويض الكاملة
  • تصميم احترافي مع فواصل وأيقونات توضيحية
  • دالة JavaScript تدعم Web Share API مع رابط URL ونسخ احتياطي للحافظة
  • إدراج رابط النموذج المخزن في قاعدة البيانات (authorization_form_link) ضمن رسالة المشاركة
  • رسالة تفصيلية شاملة تبدأ بوصف النظام وتتضمن بيانات التفويض والروابط المطلوبة
  • تصميم احترافي مع فواصل طويلة وتنسيق واضح للمعلومات
  • إصلاح رابط المشاركة ليرفق رابط النموذج الخارجي المُدخل بدلاً من رابط صفحة التفاصيل
  • إضافة زر مشاركة شامل في صفحة تفاصيل التفويض يتضمن جميع البيانات المعروضة
  • رسالة مشاركة كاملة تحتوي على: معلومات السيارة، بيانات الموظف، تفاصيل التفويض، الروابط، الملاحظات
  • استخدام الرابط المخزن في حقل "الرابط الخارجي" من قاعدة البيانات في رسالة المشاركة
  • إصلاح رفق رابط النموذج الخارجي بدلاً من رابط صفحة التفاصيل في المشاركة
  • نظام أولوية الروابط: الرابط الخارجي ← رابط النموذج (بدون رابط التفاصيل)
  • إضافة المرفقات إلى رسالة المشاركة مع روابط مباشرة للملفات المرفوعة
  • إصلاح خطأ start_date في إنشاء التفويضات الخارجية بإزالة الحقول غير الموجودة
  • إصلاح مسار الملفات المرفقة ليوجه للمجلد الصحيح static/uploads/authorizations/
  • تحسين قسم التفويضات الخارجية بعرض آخر 3 عمليات مع زر "عرض الكل"
  • إضافة scroll عمودي للقائمة الكاملة مع رأس ثابت وتصميم متقدم
  • تحسين التصميم البصري مع تدرجات لونية وتأثيرات hover احترافية
  • إصلاح رسالة مشاركة سجلات الورشة لحذف روابط النظام والإبقاء على رابط تسليم الورشة فقط
  • تغيير التاريخ في رسائل المشاركة من هجري إلى ميلادي حسب طلب المستخدم
- July 8, 2025: **حذف قسم الوثائق والمرفقات من صفحة تفاصيل السيارة:**
  • حذف القسم الكامل للوثائق والمرفقات من صفحة تفاصيل السيارة الموبايل
  • إزالة الإحصائيات والبيانات المرتبطة بالوثائق
  • تنظيف الواجهة وتبسيط المحتوى حسب طلب المستخدم
- July 8, 2025: **إصلاح شامل لمشكلة المحتوى المختفي خلف الهيدر والقائمة السفلية:**
  • إصلاح مشكلة المحتوى المختفي تحت رأس الصفحة بإضافة padding-top: 70px
  • أضافة padding-bottom: 120px لجميع صفحات الموبايل لمنع اختفاء المحتوى خلف القائمة السفلية
  • تطبيق الحل على: صفحة تفاصيل السيارة، عرض التفويض، تعديل التفويض، إنشاء تفويض، إنشاء سجل التسليم
  • إضافة !important للتأكد من تطبيق التنسيقات على جميع الصفحات
  • ضمان رؤية كامل المحتوى دون انقطاع من عناصر التنقل الثابتة
- July 8, 2025: **تطبيق تصميم تفصيلي متقدم لسجلات التسليم والاستلام:**
  • استبدال التصميم البسيط بجدول تفصيلي متطور
  • إضافة إحصائيات سريعة: تسليم، استلام، إجمالي
  • جدول مع التمرير الأفقي يعرض: التاريخ، النوع، الشخص، الهاتف، الهوية، الحالة، الإجراءات
  • رأس برتقالي متدرج (gradient-header-orange) مع مؤشرات التمرير
  • زر لعرض جميع السجلات مع قائمة قابلة للطي
  • أزرار دائرية للإجراءات: عرض، تعديل، مشاركة، PDF
  • تطبيق نفس نمط التصميم المتقدم من التفويضات الخارجية
- July 8, 2025: **حل مشاكل الترتيب والقيم الفارغة في التفويضات الخارجية:**
  • إزالة منطق الترتيب المعقد من template لتجنب أخطاء Jinja2
  • تطبيق ترتيب آمن في backend Python يتعامل مع القيم الفارغة
  • تبسيط عرض البيانات في template للاستقرار
  • إصلاح خطأ None value sorting الذي كان يسبب أخطاء template
- July 8, 2025: **حذف الأقسام غير المطلوبة من صفحة الموبايل:**
  • حذف قسم "معلومات الإيجار" من صفحة تفاصيل السيارة الموبايل
  • حذف قسم "فحوصات السلامة" من صفحة تفاصيل السيارة الموبايل  
  • حذف قسم "الفحص الدوري" من صفحة تفاصيل السيارة الموبايل
  • تبسيط واجهة الموبايل للتركيز على الوظائف الأساسية المطلوبة
  • إبقاء الأقسام الأساسية فقط: معلومات السيارة، سجل الصيانة، سجلات الورشة، التفويضات الخارجية
- July 8, 2025: **إنشاء مسارات موبايل منفصلة للتفويضات الخارجية:**
  • إنشاء صفحات موبايل منفصلة لعرض وتعديل التفويضات الخارجية
  • إضافة مسارات mobile.view_external_authorization وmobile.edit_external_authorization وmobile.delete_external_authorization
  • ربط جميع أزرار التفويضات الخارجية بمسارات الموبايل لمنع الانتقال لصفحة الويب
  • النظام يبقى في واجهة الموبايل دون الانتقال للواجهة الرئيسية
- July 8, 2025: **إصلاح أزرار التفويضات الخارجية وإضافة صفحات CRUD كاملة:**
  • أصلحت جميع أزرار التفويضات الخارجية (عرض، تعديل، موافقة، رفض، حذف)
  • أنشأت صفحة عرض تفاصيل شاملة للتفويض مع جميع المعلومات
  • أنشأت صفحة تعديل مع جميع الحقول المطلوبة وبحث متقدم للموظفين
  • أضفت مسارات Flask جديدة: view, edit, approve, reject, delete
  • إصلاح مشكلة قاعدة البيانات بإضافة حقلي project_name و city
  • جميع الأزرار تعمل بتأكيد قبل الإجراء وتحديث الحالة بنجاح
  • النظام يدعم workflow كامل للتفويضات مع صفحات منفصلة حسب تفضيل المستخدم
- July 8, 2025: **إنشاء صفحة منفصلة لإضافة التفويضات الخارجية:**
  • أنشأت صفحة منفصلة create_external_authorization.html حسب تفضيل المستخدم
  • إضافة نموذج شامل يتضمن: فلترة الموظفين حسب القسم، معلومات الموظف المختار
  • قائمة منسدلة للمدن السعودية (20 مدينة)، رابط النموذج/التفويض الخارجي
  • رفع ملفات متنوع (PDF, صور, Word)، معاينة الملف المرفوع قبل الحفظ
  • route جديد create_external_authorization مع معالجة POST و GET
  • حفظ الملفات في مجلد static/uploads/authorizations/ مع التشفير الآمن
  • واجهة تفاعلية تعرض معلومات الموظف عند الاختيار (هاتف، منصب)
  • تصميم responsive مع Bootstrap وتجربة مستخدم محسنة
  • ربط قائمة المشاريع بالأقسام الفعلية من قاعدة البيانات بدلاً من القيم الثابتة
- July 8, 2025: **إعادة إضافة قسم التفويضات الخارجية:**
  • إعادة إضافة قسم التفويضات الخارجية إلى صفحة تفاصيل المركبة
  • إضافة النافذة المنبثقة لإنشاء تفويضات جديدة مع التصميم الداكن
  • ربط البيانات المطلوبة (departments, employees, external_authorizations) في route المحمول
  • فلترة الموظفين حسب القسم في النموذج المنبثق
- July 7, 2025: **إضافة نظام مشاركة سجلات التسليم والاستلام المحسن:**
  • إضافة زر مشاركة جديد في جدول سجلات التسليم والاستلام
  • رسائل مشاركة منظمة ومنسقة تبدأ بـ "مرحباً 👋" وتتضمن:
  • قسم بيانات المركبة: رقم السيارة، نوع العملية، تاريخ العملية بالميلادي
  • قسم بيانات السائق: الاسم، رقم الإقامة/الهوية، رقم الهاتف
  • قسم الملاحظات الإضافية (عند وجودها)
  • قسم المرفقات والوثائق مع رابط PDF العام مباشر
  • تنسيق احترافي مع خطوط فاصلة وأيقونات توضيحية
  • نسخ تلقائي للحافظة مع رسائل تأكيد
  • دعم Web Share API للمشاركة المباشرة
  • Modal احتياطي لعرض النص في المتصفحات التي لا تدعم المشاركة
  • إضافة زر تعديل لسجلات التسليم والاستلام مع أيقونة تعديل وصفحة تعديل مخصصة للجوال
  • إصلاح مسارات تفاصيل الورشة لتوجه للصفحة الصحيحة
- July 7, 2025: **إضافة نظام إدارة ورشة كامل مع صفحات منفصلة ومشاركة متقدمة:**
  • إضافة أزرار CRUD كاملة لسجلات الورشة: عرض التفاصيل، تعديل، حذف، مشاركة
  • إنشاء صفحة تفاصيل شاملة للورشة تعرض جميع المعلومات والصور
  • إصلاح مشكلة عدم تحميل البيانات السابقة في صفحة التعديل
  • توحيد قيم repair_statuses بين جميع النماذج
  • إضافة Modal لعرض الصور المرفقة بحجم كامل
  • تحسين واجهة المستخدم مع badges ملونة لحالات مختلفة
  • إضافة معلومات التسجيل وتواريخ الإنشاء والتحديث
  • تطبيق تصميم مستجيب للجوال مع تأثيرات بصرية احترافية
  • إضافة نظام مشاركة متقدم مع Web Share API ونسخ تلقائي للحافظة
  • رسائل مشاركة تفصيلية تتضمن رقم السيارة وروابط الصور والنماذج
  • دعم مشاركة ملخص سريع من قائمة السجلات ومشاركة تفصيلية من صفحة التفاصيل
- July 7, 2025: **إضافة صفحات منفصلة لإدارة التفويضات الخارجية:**
  • إنشاء صفحة عرض تفاصيل شاملة للتفويض الخارجي مع جميع المعلومات
  • إضافة مسارات للعرض، التعديل، الموافقة، الرفض، والحذف
  • استبدال النوافذ المنبثقة بصفحات منفصلة حسب طلب المستخدم
  • إضافة أزرار الإجراءات: عرض التفاصيل، تعديل، عرض الملف، فتح الرابط، موافقة، حذف
  • تحسين واجهة المستخدم مع بطاقات منظمة وتصميم متجاوب
  • النظام يعرض التفويضات الموجودة (2 تفويض) بنجاح في صفحة المركبة
- July 7, 2025: **تحديث نظام التفويضات الخارجية وتطبيق التصميم الداكن:**
  • ربط قائمة المشاريع بالأقسام الفعلية من قاعدة البيانات بدلاً من القيم الثابتة
  • تحديث أنواع التفويض لتشمل: تفويض تسليم، استلام السيارة من مندوب، تفويض مؤقت، نقل سيارة
  • تطبيق تصميم داكن شامل مع خلفية سوداء وألوان نصوص متناسقة
  • تحويل جميع النصوص البيضاء إلى سوداء للوضوح والقراءة
  • استعادة الأيقونات الملونة (أخضر للحفظ، أحمر للإلغاء)
  • النظام يستخدم الآن الأقسام الحقيقية كمشاريع للتفويضات
- July 7, 2025: **تطبيق التصميم الداكن لصفحة التفويضات الخارجية بنجاح:**
  • حل مشكلة الخلفية البيضاء/الرمادية وتطبيق خلفية داكنة موحدة (#1a1a1a)
  • تحديث جميع عناصر الصفحة لتتناسب مع الثيم الداكن
  • تغيير ألوان النصوص والحقول والعناصر التفاعلية للتباين المناسب
  • تطبيق تدرج أزرق داكن للعنوان الرئيسي مع نص أبيض
  • تحسين ألوان أقسام النموذج وعناصر رفع الملفات
  • الصفحة تعمل بالتصميم المطلوب والمستخدم راضٍ عن النتيجة
- July 7, 2025: **إعادة تنظيم موقع نظام التفويضات الخارجية:**
  • نقل قسم التفويضات الخارجية ليكون أسفل قسم سجلات التسليم والاستلام مباشرة
  • إصلاح جميع مشاكل JavaScript للنافذة المنبثقة وإضافة الدوال المفقودة
  • تحسين تنظيم صفحة تفاصيل المركبة لترتيب منطقي أفضل
  • القسم يعمل بكامل الميزات: فلترة الأقسام، بحث الموظفين، اختيار المشاريع، رفع الملفات
- July 7, 2025: **إضافة نظام إدارة التفويضات الخارجية للموظفين:**
  • أنشأت نظام شامل لإدارة تفويضات الموظفين للمشاريع الخارجية
  • إضافة جدولي Project و ExternalAuthorization لقاعدة البيانات
  • بناء واجهة تفاعلية مع popup forms وبحث ديناميكي للموظفين
  • فلترة الموظفين حسب القسم مع شريط بحث متقدم
  • قائمة منسدلة للمشاريع (مشروع الرياض، جدة، الشرقية، نيوم، القصيم)
  • رفع ملفات PDF وصور مع drag-and-drop interface
  • إضافة روابط خارجية اختيارية (Google Forms, Drive links)
  • نظام الموافقة والرفض للإداريين مع ملاحظات
  • تسجيل كامل للعمليات مع audit logging
  • واجهة عرض شاملة بـ status badges وإحصائيات
  • إضافة مسار للوصول من صفحة المركبات والقائمة الجانبية
  • تخزين آمن للملفات في static/uploads/authorizations/
  • API endpoint للبحث التفاعلي عن الموظفين
  • النظام يدعم workflow كامل: إنشاء → مراجعة → موافقة/رفض → أرشفة
  • إضافة القسم مباشرة داخل صفحة تفاصيل السيارة مع modal منبثق
  • واجهة تفاعلية كاملة مع drag-and-drop وبحث ديناميكي مدمج في صفحة السيارة
- July 6, 2025: **إصلاح شامل لنظام الخطوط ومعالجة الطلبات الكبيرة:**
  • أصلحت مشاكل ربط خط beIN-Normal في دالة generate_handover_report_pdf_weasyprint
  • أضفت نظام اختيار تلقائي للخطوط المتوفرة بترتيب الأولوية (beIN Normal، Tajawal، Cairo، Amiri)
  • تحسين مسارات الخطوط للعمل مع WeasyPrint وإضافة فحص وجود الملفات
  • إضافة logging لتتبع الخط المستخدم في كل تقرير PDF وحجم PDF المُنشأ
  • استعادة استخدام المولد الأصلي fpdf_handover_pdf.py مع تحديثات الخط
  • حل مشكلة "Request Entity Too Large" بزيادة MAX_CONTENT_LENGTH إلى 100MB
  • إضافة معالج خطأ 413 مع رسائل مناسبة للجوال والويب
  • إضافة فحص حجم البيانات في mobile checklist قبل المعالجة (حد أقصى 20MB)
  • إضافة نظام ضغط تلقائي للصور أكبر من 500KB باستخدام Canvas API
  • إضافة فحص JavaScript شامل للحجم قبل إرسال النموذج
  • تحسين واجهة المستخدم مع تحذيرات واضحة حول الحدود المسموحة
  • النظام الآن يضغط الصور تلقائياً ويدعم رفع عدد أكبر من الملفات
  • إصلاح مشكلة الصور الفارغة في صفحة المرفقات المحمولة بتحديث مسارات العرض
  • إضافة دعم لعرض الصور من حقلي file_path و image_path للتوافق مع البيانات القديمة والجديدة
  • إضافة placeholder بصري جميل لحالة عدم وجود صور مع رموز وتصميم احترافي
  • تحسين عرض أوصاف الصور من حقلي file_description و image_description
- July 6, 2025: **استبدلت جميع ملفات المشروع بالنسخة الجديدة car_care-main.zip:**
  • نسخت جميع الملفات من car_care-main.zip واستبدلت المشروع بالكامل
  • تم تثبيت جميع الحزم المطلوبة بنجاح (arabic-reshaper, fpdf2, reportlab, weasyprint)
  • أصلحت مشاكل قاعدة البيانات بإضافة جميع الحقول المفقودة (mobilePersonal, nationality_id, contract_status, license_status)
  • أضفت جميع الحقول المطلوبة لجدول vehicle_handover (30+ حقل إضافي)
  • إنشاء مستخدم admin@nuzum.sa مع كلمة مرور admin123 للاختبار
  • أضفت بيانات تجريبية للمركبات والأقسام
  • إصلاح مشاكل templates (vehicle.updated_at AttributeError) بإضافة فحص null safety
  • حدثت قاعدة البيانات لملء القيم المفقودة في updated_at
  • النظام يعمل الآن بالنسخة الجديدة مع تحسينات شاملة وحلول لمشاكل قاعدة البيانات
  • جميع صفحات المركبات تعمل بدون أخطاء (302 redirect للتسجيل كما هو مطلوب)
  • استعادة سجلات التسليم والاستلام المفقودة بإضافة 6 سجلات تجريبية للمركبات
  • إصلاح كود عرض سجلات التسليم والاستلام ليعمل مع النصوص العربية (تسليم/استلام)
  • إصلاح أخطاء صفحة فهرس المركبات وإضافة حماية ضد الأخطاء في دالة get_vehicle_current_employee_id
  • إصلاح template عرض سجلات التسليم والاستلام ليعمل مع handover_type_ar بدلاً من delivery/return
  • إصلاح خطأ إنشاء PDF للتسليم والاستلام بإنشاء نسخة مبسطة تعمل مع FPDF
  • إصلاح دالة view_handover للتعامل مع النصوص العربية في أنواع التسليم والاستلام
  • إنشاء صفحة HTML مبسطة لعرض بيانات التسليم والاستلام
  • استخراج وتطبيق التصميم الأصلي من car_care-main.zip لصفحة عرض التسليم والاستلام
  • تحديث templates/vehicles/handover_view.html بالتصميم الكامل مع الخلفية الداكنة والبطاقات الحديثة
  • إضافة تصميم متقدم للصور وملفات PDF مع تأثيرات hover وتخطيط مسؤول
  • حل مشاكل العرض وإضافة معالجة أفضل للقيم الفارغة (null safety)
  • استبدال مولد PDF للتسليم والاستلام بالنسخة الأصلية من car_care-main.zip
  • تطبيق arabic_handover_pdf.py مع التصميم المتقدم والخطوط العربية
  • إصلاح دالة handover_pdf_public لاستخدام ReportLab مع معالجة النصوص العربية
  • تحسين عرض PDF مع ألوان احترافية وتصميم منسق بالكامل
  • استخراج وتطبيق تصميم handover_report.html الأصلي من car_care-main.zip
  • تحديث templates/vehicles/handover_report.html بالتصميم الكامل مع هيدر احترافي
  • إضافة جداول منظمة لبيانات المركبة والسائق مع ألوان متدرجة
  • تطبيق تخطيط Grid مرن للمعلومات الرئيسية والتواقيع
  • أضافة قسم شامل للمرفقات والملاحظات مع تصميم منسق
  • حل مشاكل مكتبات PDF بتثبيت المكتبات المطلوبة (weasyprint, cairocffi, arabic-reshaper, fpdf2)
  • إصلاح مشاكل WeasyPrint بتحديث مسارات الصور لتستخدم مسارات محلية بدلاً من URL
  • معالجة آمنة للحقول الفارغة في مولد PDF (damage_diagram_path, signatures)
  • إضافة صورة vehicle_diagram_new.png المفقودة لحل مشاكل عرض مخطط السيارة
  • PDF يعمل بنجاح الآن بحجم 289KB مع تصميم احترافي وخطوط عربية
  • حل مشاكل البحث والفلترة في صفحة إنشاء تسليم واستلام المركبات
  • إصلاح مشكلة الموظفين المرتبطين بأقسام متعددة (many-to-many relationship)
  • تحديث route لجلب بيانات الأقسام مع الموظفين باستخدام joinedload
  • تحسين template لعرض جميع أقسام الموظف في البحث والفلترة
  • إصلاح دوال JavaScript للتعامل مع معرفات أقسام متعددة مفصولة بفواصل
  • تحسين عرض الأقسام في الجداول مع badges للأقسام المتعددة
  • يحتوي على جميع الوحدات: employees, vehicles, attendance, salaries, departments
- July 4, 2025: **استبدلت جميع ملفات المشروع بالنسخة الاحتياطية cloudpanel_20250609_213427.rar:**
  • استبدلت app.py وmodels.py بالنسخة الكاملة من النسخة الاحتياطية
  • نسخت جميع مجلدات routes/ وtemplates/ وstatic/ وutils/ وservices/ وforms/
  • استعادت النظام الكامل بجميع الوحدات والتصميم الأصلي
  • النظام يعمل بنجاح مع النسخة المحدثة بدون أخطاء
- July 3, 2025: **نجحت في إعادة إنشاء ملفات النظام الأساسية بعد الحذف الخاطئ:**
  • أعادت إنشاء routes/employees.py مع جميع وظائف إدارة الموظفين (CRUD كامل)
  • أعادت إنشاء routes/vehicles.py مع إدارة المركبات والتسليم والاستلام
  • أعادت إنشاء routes/departments.py مع إدارة الأقسام والهيكل التنظيمي
  • أنشأت templates/ كاملة للموظفين والمركبات والأقسام مع تصميم متجاوب
  • ربطت جميع المسارات بالتطبيق الرئيسي مع حل مشكلة تعارض الأسماء
  • حدثت لوحة المعلومات لتشمل روابط إدارة جميع الأقسام
  • النظام يعمل بشكل كامل مع 59 موظف، 20 مركبة، 6 أقسام
  • واجهة API تعمل بكامل وظائفها مع 25+ مسار
  • أضافت ملفات إدارة الرواتب والحضور من النسخة الاحتياطية
  • دمجت مجلدات services وutils مع المشروع الحالي
  • أضافت مسارات الرواتب والحضور إلى التطبيق الرئيسي
  • حدثت لوحة المعلومات لتشمل الوظائف الجديدة
  • أصلحت أخطاء التوجيه في ملف base.html وأنشأت تخطيط مبسط
  • حللت مشاكل المسارات المعطلة وأصلحت جميع الروابط
  • النظام الآن يعمل بدون أخطاء داخلية مع تصميم محدث
- July 3, 2025: Successfully completed code cleanup and project optimization:
  • Removed all unused files and dependencies for cleaner project structure
  • Eliminated unnecessary deployment scripts, test files, and archived assets
  • Consolidated API functionality into single organized routes/restful_api.py file
  • Simplified models.py to include only essential database models
  • Created clean Flask application factory pattern in app.py
  • Reduced project to core essential files: API, models, templates, and documentation
  • Maintained complete RESTful API functionality with 25+ endpoints
  • Preserved all Postman Collection and testing capabilities
  • Project now contains only production-ready, actively used components
  • Significantly improved maintainability and deployment readiness
- July 1, 2025: Successfully implemented comprehensive RESTful API with complete Postman testing suite:
  • Created full RESTful API covering all system features with 25+ endpoints
  • Built comprehensive Postman Collection with automatic token management and testing scripts
  • Developed complete API documentation with examples and error handling
  • Implemented JWT authentication with Bearer token security for all protected routes
  • Added advanced search, filtering, and pagination capabilities across all endpoints
  • Created employee management API (CRUD operations with validation and error handling)
  • Built vehicle management API with handover and workshop record integration
  • Implemented attendance system API with date range filtering and status management
  • Added salary management API with employee-specific salary history tracking
  • Developed comprehensive reporting API with dashboard stats and monthly reports
  • Built advanced search API supporting cross-system queries with multiple filters
  • Created notification system API ready for real-time implementation
  • Added health check and API info endpoints for monitoring and documentation
  • Implemented proper error handling with Arabic messages and HTTP status codes
  • Built Postman Environment file with dynamic variables and testing automation
  • Created comprehensive testing guide with step-by-step instructions and troubleshooting
  • API successfully tested and validated - all endpoints working correctly without errors
  • System now provides complete API coverage for mobile apps, third-party integrations, and automated testing
- June 21, 2025: Completely removed 3D effects and simplified user interface:
  • Successfully removed all 3D effects from system admin interface per user request
  • Updated 6 HTML template files to eliminate perspective, rotateX, rotateY, and translateZ transforms
  • Replaced complex 3D hover effects with simple translateY animations
  • Removed analytics data and charts from reports page for cleaner interface
  • Fixed company creation form by replacing Flask-WTF with plain HTML inputs
  • Resolved Internal Server Error on /system/companies/new route
  • System now provides smooth, fast user experience without disorienting 3D effects
- June 20, 2025: Successfully implemented ultra-modern futuristic UI design for system admin interface:
  • Created cutting-edge dashboard design with neon gradients, glass-morphism effects, and floating particles
  • Implemented advanced CSS animations including 3D hover effects, parallax scrolling, and animated backgrounds
  • Built futuristic company management interface with sophisticated visual effects
  • Developed comprehensive subscriptions management page with advanced filtering and statistics
  • Enhanced page headers with proper visibility and prominence for better user experience
  • Fixed navigation text color issues for better readability with white text and neon hover effects
  • Resolved company creation errors and simplified the process with proper form validation
  • Added edit and delete buttons with confirmation dialogs for company management operations
  • Created comprehensive edit company page with futuristic design and real-time validation
  • Implemented secure delete confirmation modal with glass-morphism effects and CSRF protection
  • All system admin pages now feature consistent modern aesthetic with animated elements
  • Successfully tested company creation functionality with proper database integration
  • Fixed company status toggle error by using correct 'status' field instead of 'is_active'
  • Resolved "Method Not Allowed" error in subscription management by adding POST method support
  • Enhanced subscription management with comprehensive form handling for upgrade, extend, suspend, and activate actions
  • Created ultra-modern subscription management page with cyber-grid animations, glassmorphism effects, and interactive plan cards
  • Implemented dynamic pricing cards with gradient animations, featured plan highlighting, and hover effects
  • Added comprehensive subscription status dashboard with progress bars, neon badges, and real-time information display
  • Enhanced SubscriptionService with upgrade_subscription and extend_subscription methods for complete functionality
  • Created futuristic company details page with cosmic animations, 3D hover effects, and parallax scrolling
  • Implemented advanced glassmorphism design with floating particles and cosmic grid background
  • Added comprehensive company statistics dashboard with animated progress bars and neon status badges
  • Enhanced user experience with ripple effects, loading animations, and responsive design across all devices
  • Created quantum-level reports dashboard with holographic headers, matrix rain background, and interactive charts
  • Implemented advanced statistical visualizations with Chart.js integration and animated progress rings
  • Built comprehensive analytics center with real-time data, growth metrics, and subscription distribution charts
  • Added quantum button effects, parallax interactions, and ultra-modern glassmorphism design elements
- June 20, 2025: Successfully completed multi-tenant system with working system admin dashboard:
  • Fixed routing issues between `/system-admin/` and `/system/` URL patterns
  • Created system admin user with credentials: admin@nuzum.sa / admin123 (password hash updated and verified)
  • System admin dashboard fully operational with company statistics and management features
  • All redirect routes properly configured for seamless user experience
  • Dashboard navigation and URL routing completely fixed and operational
  • System admin can access all company data: 59 employees, 19 vehicles with full management capabilities
- June 20, 2025: Successfully resolved all access permission issues in multi-tenant system:
  • Fixed check_module_access function to properly recognize SYSTEM_ADMIN users
  • All existing data preserved and linked to default "الشركة الرئيسية" company
  • System owner can now access all modules: employees (59), vehicles (19), departments, etc.
  • Three-tier user hierarchy fully operational with proper data isolation
  • Login credentials working: admin@nuzum.sa / admin123
- June 20, 2025: Successfully completed and fixed نُظم multi-tenant architecture implementation:
  • Fixed critical database enum compatibility issues that prevented system startup
  • Resolved authentication system with working login credentials (admin@nuzum.sa / admin123)
  • Created functional base.html template supporting multi-tenant navigation
  • Fixed all route redirections and template moment.js dependencies
  • Successfully implemented three-tier user hierarchy with proper access control
  • System owner dashboard now fully operational with comprehensive company management
  • All decorators properly validate user permissions with enum string compatibility
- June 20, 2025: Successfully transformed نُظم into comprehensive multi-tenant architecture:
  • Complete database schema migration to support multiple companies with data isolation
  • Implemented three-tier user hierarchy: System Owner → Company Admin → Employee
  • Created subscription management system with trial periods and usage limits
  • Built system admin dashboard for managing all companies and subscriptions
  • Developed company admin dashboard with subscription status and usage tracking
  • Added multi-tenant decorators for access control and data filtering
  • Implemented subscription service with automated notifications and limits
  • Created comprehensive permission system with module-based access control
  • Successfully resolved database enum compatibility and relationship mapping issues
  • System now supports unlimited companies with complete data isolation
- June 20, 2025: Successfully implemented comprehensive Arabic employee basic report with all requested features:
  • Created Arabic PDF report generator using ReportLab with proper Arabic text support
  • Implemented complete employee information display in Arabic language
  • Added support for displaying three required images: profile photo, national ID, and driving license
  • Fixed all encoding issues and text rendering problems for Arabic content
  • Report includes: basic personal information, work details, document photos, additional info, and statistics
  • User confirmed successful functionality showing professional Arabic report layout
- June 20, 2025: Enhanced employee portal with professional designs and data filtering:
  • Created modern glass-morphism design for employee vehicles page with interactive timeline
  • Implemented comprehensive vehicle data filtering to show only employee-related handovers
  • Fixed employee profile page AttributeError by removing invalid birth_date field reference
  • Designed premium profile page with gradient backgrounds, floating particles, and stats cards
  • Added responsive grid layouts and smooth animations for better user experience
  • Ensured all employee portal pages display only data related to the logged-in employee
- June 14, 2025: Successfully implemented Arabic employee PDF report with exact user-requested design:
  • Created comprehensive PDF report matching provided design template
  • Features circular profile photo frame with blue border
  • Added green-bordered rectangular frames for national ID and license images
  • Implemented blue header sections with white text for information categories
  • Added alternating row colors in data tables for better readability
  • Includes basic information, work details, and vehicle records sections
  • Successfully generated 2854-byte PDF file with proper Arabic text support
  • Report displays employee photos, identity documents, and comprehensive data
- June 14, 2025: Fixed employee PDF report generation errors:
  • Created safe Arabic font loading system with fallback mechanisms
  • Resolved all FPDF font errors that were causing report failures
  • Added comprehensive error handling for text processing and image display
  • Updated employee route to use fixed PDF report generator
  • Confirmed successful PDF generation for employee ID 178 and all other employees
- June 14, 2025: Enhanced duplicate prevention system with comprehensive validation:
  • Added duplicate checking within same Excel file before database insertion
  • Enhanced validation for required fields (plate_number, make, model)
  • Improved error reporting with specific row numbers and clear messages
  • Added tracking of processed plate numbers to prevent intra-file duplicates
- June 14, 2025: Updated vehicle import functionality to match exact user requirements: رقم اللوحة، الماركة، الموديل، سنة الصنع، اللون، اسم السائق، الحالة، تاريخ انتهاء الفحص الدوري، تاريخ انتهاء الاستمارة، ملاحظات، تاريخ الإضافة
- June 14, 2025: Added automatic data filling for missing fields during import (engine_number, chassis_number, fuel_type, mileage)
- June 14, 2025: Enhanced import template with proper date format examples and comprehensive field mapping
- June 14, 2025: Fixed import template column names to match user specifications exactly
- June 14, 2025: Added comprehensive Excel import functionality for vehicle data matching export format structure
- June 14, 2025: Created import template download function with proper Arabic column headers
- June 14, 2025: Added import validation with error handling and success/failure reporting
- June 14, 2025: Integrated import buttons into both desktop and mobile vehicle index page layouts
- June 14, 2025: Fixed vehicle export filename encoding to eliminate HTTP header warnings and ensure proper downloads
- June 14, 2025: Completely resolved all vehicle template URL routing errors by removing broken import function references
- June 14, 2025: Successfully restored vehicle management system functionality after extensive debugging and fixes
- June 14, 2025: Cleaned up all corrupted export code and syntax errors in routes/vehicles.py
- June 14, 2025: Added complete export_all_vehicles_to_excel function with proper Excel formatting to utils/vehicles_export.py
- June 14, 2025: Removed "PDF report" button from vehicle view page as requested by user
- June 14, 2025: Removed redundant "export all vehicles" button from main vehicles page as requested by user
- June 14, 2025: Fixed Excel import page error by removing unnecessary form dependency
- June 14, 2025: Improved vehicle view page UI design and added Excel import functionality with template download
- June 14, 2025: Fixed all VehicleProject Excel export errors (project_description, project_location, project_manager)
- June 14, 2025: Fixed Vehicle Excel export 'vin' field error by replacing with existing model fields
- June 14, 2025: Fixed VehicleSafetyCheck Excel export field mapping errors (tire_condition, checked_by, etc.)
- June 14, 2025: Fixed circular import issues in vehicles routes causing 404 and 500 errors
- June 14, 2025: Resolved database access problems by adding proper imports to route functions
- June 14, 2025: Fixed Excel export functionality with comprehensive field mapping and openpyxl compatibility
- June 14, 2025: Resolved VehiclePeriodicInspection certificate_number field issue 
- June 14, 2025: Updated VehicleHandover field references (person_name, mileage)
- June 14, 2025: Removed xlsxwriter dependencies to ensure openpyxl compatibility
- June 14, 2025: Initial setup

## User Preferences

Preferred communication style: Simple, everyday language.