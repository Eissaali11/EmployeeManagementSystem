# وثائق RESTful API - نظام نُظم

## نظرة عامة

نظام نُظم يوفر RESTful API شامل لجميع وظائف النظام بما في ذلك إدارة الموظفين، المركبات، الأقسام، الحضور، الرواتب، والتقارير.

**Base URL:** `http://your-domain.com/api/v1`

## المصادقة

يستخدم النظام JWT tokens للمصادقة. يجب إرسال Token في header كالتالي:

```
Authorization: Bearer <your-token>
```

## استجابة API موحدة

جميع استجابات API تتبع النمط التالي:

### النجاح
```json
{
  "success": true,
  "message": "رسالة النجاح",
  "timestamp": "2024-01-01T00:00:00.000Z",
  "data": { /* البيانات */ },
  "meta": { /* معلومات إضافية مثل pagination */ }
}
```

### الخطأ
```json
{
  "success": false,
  "error": {
    "message": "رسالة الخطأ",
    "code": 400,
    "timestamp": "2024-01-01T00:00:00.000Z",
    "details": ["تفاصيل إضافية"]
  }
}
```

## 🔐 المصادقة والترخيص

### تسجيل دخول المستخدم
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

**الاستجابة:**
```json
{
  "success": true,
  "message": "تم تسجيل الدخول بنجاح",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 1,
      "email": "user@example.com",
      "name": "أحمد محمد",
      "company_id": 1,
      "role": "admin"
    }
  }
}
```

### تسجيل دخول الموظف
```http
POST /api/v1/auth/employee-login
Content-Type: application/json

{
  "employee_id": "4298",
  "national_id": "2489682019"
}
```

## 📊 لوحة المعلومات

### إحصائيات لوحة المعلومات
```http
GET /api/v1/dashboard/stats
Authorization: Bearer <token>
```

**الاستجابة:**
```json
{
  "success": true,
  "data": {
    "statistics": {
      "employees": {
        "total": 150,
        "active": 145,
        "new_this_month": 5
      },
      "vehicles": {
        "total": 50,
        "active": 48,
        "in_workshop": 2
      },
      "departments": {
        "total": 8,
        "with_managers": 6
      },
      "attendance": {
        "present_today": 140,
        "absent_today": 5
      }
    }
  }
}
```

## 👥 إدارة الموظفين

### جلب قائمة الموظفين
```http
GET /api/v1/employees?page=1&per_page=20&search=محمد&department_id=1&status=active&sort_by=name&sort_order=asc
Authorization: Bearer <token>
```

**المعاملات:**
- `page`: رقم الصفحة (افتراضي: 1)
- `per_page`: عدد العناصر في الصفحة (افتراضي: 20، الحد الأقصى: 100)
- `search`: البحث في الاسم، رقم الموظف، أو البريد الإلكتروني
- `department_id`: تصفية حسب القسم
- `status`: تصفية حسب الحالة (active, inactive)
- `sort_by`: الترتيب حسب (name, employee_id, created_at)
- `sort_order`: اتجاه الترتيب (asc, desc)

### جلب موظف محدد
```http
GET /api/v1/employees/{employee_id}
Authorization: Bearer <token>
```

### إضافة موظف جديد
```http
POST /api/v1/employees
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "أحمد محمد علي",
  "employee_id": "4299",
  "national_id": "1234567890",
  "email": "ahmed@example.com",
  "phone": "0501234567",
  "department_id": 1,
  "job_title": "مطور",
  "basic_salary": 8000,
  "hire_date": "2024-01-01",
  "status": "active"
}
```

**الحقول المطلوبة:**
- `name`: اسم الموظف
- `employee_id`: رقم الموظف (فريد)
- `national_id`: رقم الهوية الوطنية (فريد)

### تحديث موظف
```http
PUT /api/v1/employees/{employee_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "أحمد محمد علي المحدث",
  "email": "ahmed.updated@example.com",
  "job_title": "مطور أول",
  "basic_salary": 9000
}
```

### حذف موظف
```http
DELETE /api/v1/employees/{employee_id}
Authorization: Bearer <token>
```

## 🚗 إدارة المركبات

### جلب قائمة المركبات
```http
GET /api/v1/vehicles?page=1&per_page=20&search=123&status=active
Authorization: Bearer <token>
```

### جلب مركبة محددة
```http
GET /api/v1/vehicles/{vehicle_id}
Authorization: Bearer <token>
```

**الاستجابة تتضمن:**
- بيانات المركبة الأساسية
- سجلات التسليم (آخر 10 سجلات)
- سجلات الورشة (آخر 5 سجلات)

## 🏢 إدارة الأقسام

### جلب قائمة الأقسام
```http
GET /api/v1/departments
Authorization: Bearer <token>
```

**الاستجابة:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "قسم تقنية المعلومات",
      "description": "قسم البرمجة والتطوير",
      "employees_count": 15,
      "manager": {
        "id": 5,
        "name": "محمد أحمد",
        "employee_id": "4200"
      }
    }
  ]
}
```

## ⏰ إدارة الحضور

### جلب سجلات الحضور
```http
GET /api/v1/attendance?page=1&per_page=20&employee_id=179&date_from=2024-01-01&date_to=2024-01-31
Authorization: Bearer <token>
```

### تسجيل حضور
```http
POST /api/v1/attendance
Authorization: Bearer <token>
Content-Type: application/json

{
  "employee_id": 179,
  "date": "2024-01-15",
  "status": "present",
  "check_in_time": "08:00",
  "check_out_time": "17:00",
  "notes": "حضور عادي"
}
```

**الحالات المتاحة:**
- `present`: حاضر
- `absent`: غائب
- `late`: متأخر
- `vacation`: إجازة
- `sick`: إجازة مرضية

## 💰 إدارة الرواتب

### جلب رواتب موظف
```http
GET /api/v1/employees/{employee_id}/salaries?page=1&per_page=12
Authorization: Bearer <token>
```

## 📊 التقارير

### تقرير ملخص الموظفين
```http
GET /api/v1/reports/employees/summary
Authorization: Bearer <token>
```

### تقرير الحضور الشهري
```http
GET /api/v1/reports/attendance/monthly?year=2024&month=1
Authorization: Bearer <token>
```

## 🔍 البحث المتقدم

### البحث في النظام
```http
POST /api/v1/search
Authorization: Bearer <token>
Content-Type: application/json

{
  "query": "محمد",
  "search_in": ["employees", "vehicles"]
}
```

**خيارات البحث:**
- `employees`: البحث في الموظفين
- `vehicles`: البحث في المركبات

## 🔔 الإشعارات

### جلب الإشعارات
```http
GET /api/v1/notifications
Authorization: Bearer <token>
```

## 🛠️ خدمات مساعدة

### فحص صحة API
```http
GET /api/v1/health
```

### معلومات API
```http
GET /api/v1/info
```

## أكواد الحالة HTTP

- `200`: نجح الطلب
- `201`: تم إنشاء المورد بنجاح
- `400`: خطأ في البيانات المرسلة
- `401`: غير مصرح - يتطلب تسجيل دخول
- `403`: ممنوع - ليس لديك صلاحية
- `404`: المورد غير موجود
- `409`: تعارض - مثل تكرار البيانات
- `500`: خطأ داخلي في الخادم

## أمثلة عملية

### مثال 1: إضافة موظف جديد مع تسجيل حضوره

```bash
# 1. تسجيل الدخول
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@nuzum.sa","password":"admin123"}'

# 2. إضافة موظف (استخدم Token من الخطوة السابقة)
curl -X POST http://localhost:5000/api/v1/employees \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "name": "سالم أحمد محمد",
    "employee_id": "5001",
    "national_id": "1234567890",
    "email": "salem@example.com",
    "department_id": 1,
    "job_title": "محاسب"
  }'

# 3. تسجيل حضور الموظف
curl -X POST http://localhost:5000/api/v1/attendance \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "employee_id": EMPLOYEE_ID_FROM_STEP_2,
    "date": "2024-01-15",
    "status": "present",
    "check_in_time": "08:00"
  }'
```

### مثال 2: إنشاء تقرير شامل

```bash
# الحصول على إحصائيات الشركة
curl -X GET http://localhost:5000/api/v1/dashboard/stats \
  -H "Authorization: Bearer YOUR_TOKEN"

# تقرير ملخص الموظفين
curl -X GET http://localhost:5000/api/v1/reports/employees/summary \
  -H "Authorization: Bearer YOUR_TOKEN"

# تقرير الحضور لشهر معين
curl -X GET "http://localhost:5000/api/v1/reports/attendance/monthly?year=2024&month=1" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## معالجة الأخطاء

API يوفر رسائل خطأ واضحة باللغة العربية:

```json
{
  "success": false,
  "error": {
    "message": "بيانات مطلوبة مفقودة",
    "code": 400,
    "timestamp": "2024-01-15T10:30:00.000Z",
    "details": [
      "الحقل 'name' مطلوب",
      "الحقل 'employee_id' مطلوب"
    ]
  }
}
```

## Pagination

جميع القوائم تدعم Pagination مع المعلومات التالية:

```json
{
  "data": [...],
  "meta": {
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 150,
      "pages": 8,
      "has_next": true,
      "has_prev": false,
      "next_page": 2,
      "prev_page": null
    }
  }
}
```

## أمان API

- جميع المسارات محمية بـ CSRF protection
- JWT tokens مع انتهاء صلاحية 24 ساعة
- تشفير كلمات المرور
- فلترة البيانات الحساسة (مثل أرقام الهوية)
- معالجة شاملة للأخطاء
- التحقق من صحة البيانات المدخلة

## دعم فني

للحصول على مساعدة أو الإبلاغ عن مشاكل:
- استخدم مسار `/api/v1/health` للتحقق من حالة النظام
- راجع رسائل الخطأ في الاستجابات
- تأكد من صحة JWT token المستخدم