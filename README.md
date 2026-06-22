<div align="center">

# 👔 نُظم — نظام إدارة الموظفين العربي
### Arabic Employee Management System with Full REST API

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![JWT](https://img.shields.io/badge/JWT-000000?style=for-the-badge&logo=jsonwebtokens&logoColor=white)](https://jwt.io/)
[![Firebase](https://img.shields.io/badge/Firebase-FFCA28?style=for-the-badge&logo=firebase&logoColor=black)](https://firebase.google.com/)

![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square)
![Language](https://img.shields.io/badge/Language-Arabic%20RTL-orange?style=flat-square)
![API](https://img.shields.io/badge/API-RESTful%2025%2B%20Endpoints-blue?style=flat-square)

</div>

---

## 📌 نظرة عامة

**نُظم** هو نظام متكامل لإدارة الموظفين مبني بـ **Python Flask** مع **REST API** شاملة تضم أكثر من 25 endpoint. يدعم إدارة دورة حياة الموظف الكاملة، تتبع المركبات، نظام الحضور، إدارة الرواتب، وتقارير متقدمة — كل ذلك بدعم كامل للغة العربية.

```
╔══════════════════════════════════════════════════════════════════╗
║                   👔 نُظم SYSTEM                                 ║
║                                                                  ║
║  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────┐  ║
║  │ 👤 الموظفون │  │ 🚗 المركبات  │  │ ⏰ الحضور والانصراف   │  ║
║  │  إدارة كاملة│  │  تتبع وتسليم │  │  تتبع الوقت والتقارير  │  ║
║  └─────────────┘  └──────────────┘  └────────────────────────┘  ║
║                                                                  ║
║  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────┐  ║
║  │ 💰 الرواتب  │  │ 🏢 الأقسام   │  │  📊 التقارير والإحصاء │  ║
║  │  معالجة كشف │  │  هيكل المنظمة│  │  لوحة تحكم شاملة      │  ║
║  └─────────────┘  └──────────────┘  └────────────────────────┘  ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## ✨ المميزات الرئيسية

| الميزة | الوصف |
|--------|-------|
| 👤 **إدارة الموظفين** | CRUD كامل — إضافة، تعديل، أرشفة، بحث |
| 🚗 **تتبع المركبات** | إدارة الأسطول وتسجيل التسليم والاستلام |
| ⏰ **نظام الحضور** | تتبع الوقت مع حالات متعددة |
| 💰 **إدارة الرواتب** | معالجة كشوف الرواتب والتقارير |
| 🏢 **إدارة الأقسام** | هيكل تنظيمي كامل |
| 🔍 **بحث متقدم** | بحث شامل عبر جميع الأقسام |
| 📊 **لوحة الإحصائيات** | تحليلات مباشرة في الوقت الفعلي |
| 🔔 **الإشعارات** | نظام إشعارات داخلي |
| 🔐 **JWT Auth** | مصادقة آمنة بـ JWT Token |
| 📱 **SMS (Twilio)** | إشعارات عبر الرسائل النصية |
| 🔥 **Firebase** | مصادقة ومزامنة Firebase |

---

## 🛠️ التقنيات المستخدمة

```
┌────────────────────────────────────────────────────┐
│                   TECH STACK                        │
├───────────────────┬────────────────────────────────┤
│  Backend          │  Python Flask 3.1.0             │
│  Database         │  MySQL + SQLAlchemy ORM         │
│  Authentication   │  Flask-Login + JWT + Firebase   │
│  SMS              │  Twilio API                     │
│  API Design       │  RESTful JSON API               │
│  Security         │  bcrypt + Input Validation      │
│  Timezone         │  Asia/Riyadh (توقيت السعودية)  │
└───────────────────┴────────────────────────────────┘
```

---

## 📁 هيكل المشروع

```
EmployeeManagementSystem/
├── 📄 app.py                    ← تطبيق Flask الرئيسي
├── 📄 main.py                   ← نقطة الدخول
├── 📄 models.py                 ← نماذج قاعدة البيانات
├── 📁 routes/
│   └── restful_api.py           ← جميع API Endpoints (25+)
├── 📁 templates/                ← قوالب HTML
├── 📁 static/                   ← ملفات ثابتة
├── 📄 NUZUM_API_Collection.json ← مجموعة Postman
├── 📄 NUZUM_Environment.json    ← متغيرات Postman
├── 📄 API_DOCUMENTATION.md      ← توثيق API كامل
└── 📄 requirements.txt          ← التبعيات
```

---

## ⚙️ إعداد وتشغيل المشروع

### 1️⃣ استنساخ المستودع
```bash
git clone https://github.com/Eissaali11/EmployeeManagementSystem.git
cd EmployeeManagementSystem
```

### 2️⃣ إنشاء بيئة افتراضية
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate   # Windows
```

### 3️⃣ تثبيت التبعيات
```bash
pip install -r requirements.txt
```

### 4️⃣ إعداد ملف .env
```env
DATABASE_URL="mysql://username:password@localhost:3306/nuzum_db"
SECRET_KEY=your_secret_key_here

# Twilio (اختياري)
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=+1234567890

# Firebase (اختياري)
FIREBASE_API_KEY=your_api_key
FIREBASE_PROJECT_ID=your_project_id

# إعدادات التطبيق
FLASK_ENV=development
TZ=Asia/Riyadh
```

### 5️⃣ تهيئة البيانات التجريبية
```bash
python create_test_data.py
```

### 6️⃣ تشغيل المشروع
```bash
python main.py
# يعمل على: http://localhost:5000
```

---

## 🔌 API Endpoints الرئيسية

| Method | Endpoint | الوصف |
|--------|----------|-------|
| `GET` | `/api/v1/health` | فحص صحة النظام |
| `POST` | `/api/v1/auth/login` | تسجيل الدخول |
| `GET` | `/api/v1/employees` | قائمة الموظفين |
| `POST` | `/api/v1/employees` | إضافة موظف |
| `GET` | `/api/v1/vehicles` | قائمة المركبات |
| `GET` | `/api/v1/attendance` | سجلات الحضور |
| `GET` | `/api/v1/salaries` | كشوف الرواتب |
| `GET` | `/api/v1/departments` | الأقسام |
| `GET` | `/api/v1/dashboard/stats` | إحصائيات لوحة التحكم |
| `GET` | `/api/v1/search` | بحث شامل |

---

## 🧪 اختبار API مع Postman

```bash
# 1. افتح Postman
# 2. استورد: NUZUM_API_Collection.postman_collection.json
# 3. استورد البيئة: NUZUM_Environment.postman_environment.json
# 4. ابدأ بـ Health Check: GET /api/v1/health
# 5. سجل الدخول للحصول على Token
```

**بيانات الدخول الافتراضية:**
- Email: admin@nuzum.sa
- Password: admin123

---

## 🔐 الأمان

- ✅ JWT tokens بصلاحية 24 ساعة
- ✅ تشفير كلمات المرور (bcrypt)
- ✅ التحقق من المدخلات وتنقيتها
- ✅ حماية من SQL Injection
- ✅ رسائل خطأ بدون كشف بيانات حساسة

---

## 📜 الترخيص

MIT License — مفتوح المصدر للاستخدام التجاري والشخصي

---

<div align="center">

**نظام إدارة موظفين عربي متكامل — مبني بـ Python Flask 🐍**

[![Python](https://img.shields.io/badge/Built%20with-Python%20Flask-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://github.com/Eissaali11)

</div>
