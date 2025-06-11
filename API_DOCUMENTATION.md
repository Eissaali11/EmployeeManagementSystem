# نظام نُظم - دليل API الشامل

## نظرة عامة
يوفر نظام نُظم API متكامل لتطبيقات الجوال والتطوير الخارجي باستخدام JSON و JWT للمصادقة.

### عنوان الخادم
```
https://your-domain.com/api/v1
```

### المصادقة
جميع الطلبات (عدا تسجيل الدخول) تتطلب JWT token في header:
```
Authorization: Bearer YOUR_JWT_TOKEN
```

---

## المصادقة (Authentication)

### 1. تسجيل دخول المستخدمين العاديين
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "admin@example.com",
  "password": "password123"
}
```

**الرد:**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "name": "أحمد محمد",
    "email": "admin@example.com",
    "role": "admin",
    "department_id": 1,
    "permissions": 255
  }
}
```

### 2. تسجيل دخول الموظفين
```http
POST /api/v1/auth/employee-login
Content-Type: application/json

{
  "employee_id": "4298",
  "work_number": "2489682019"
}
```

**الرد:**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "employee": {
    "id": 179,
    "name": "عمر عبدالوهاب",
    "employee_id": "4298",
    "department": "قسم التشغيل",
    "job_title": "مشغل معدات",
    "profile_image": "/static/uploads/employees/4298_profile.jpg"
  }
}
```

### 3. التحقق من صحة Token
```http
GET /api/v1/auth/verify
Authorization: Bearer YOUR_JWT_TOKEN
```

---

## الموظفين (Employees)

### 1. جلب قائمة الموظفين
```http
GET /api/v1/employees?page=1&per_page=20&search=أحمد&department_id=1
Authorization: Bearer YOUR_JWT_TOKEN
```

**المعاملات:**
- `page`: رقم الصفحة (افتراضي: 1)
- `per_page`: عدد العناصر لكل صفحة (افتراضي: 20)
- `search`: البحث في الأسماء
- `department_id`: تصفية حسب القسم

**الرد:**
```json
{
  "employees": [
    {
      "id": 169,
      "name": "صالح ناصر يسلم بعانس",
      "employee_id": "50799",
      "national_id": "1234567890",
      "mobile": "+966501234567",
      "email": "saleh@company.com",
      "job_title": "مهندس",
      "department": "الهندسة",
      "status": "نشط",
      "join_date": "2023-01-15",
      "basic_salary": 8000.00,
      "is_active": true,
      "profile_image": "/static/uploads/employees/50799_profile.jpg"
    }
  ],
  "pagination": {
    "page": 1,
    "pages": 5,
    "per_page": 20,
    "total": 95,
    "has_next": true,
    "has_prev": false
  }
}
```

### 2. جلب بيانات موظف محدد
```http
GET /api/v1/employees/169
Authorization: Bearer YOUR_JWT_TOKEN
```

### 3. إنشاء موظف جديد
```http
POST /api/v1/employees
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json

{
  "name": "محمد أحمد علي",
  "employee_id": "50900",
  "national_id": "1234567891",
  "mobile": "+966501234568",
  "email": "mohammed@company.com",
  "job_title": "محاسب",
  "department_id": 2,
  "join_date": "2024-01-01",
  "basic_salary": 7000.00
}
```

---

## الحضور والانصراف (Attendance)

### 1. جلب سجلات الحضور
```http
GET /api/v1/attendance?employee_id=169&date_from=2024-01-01&date_to=2024-01-31
Authorization: Bearer YOUR_JWT_TOKEN
```

**الرد:**
```json
{
  "attendance": [
    {
      "id": 1250,
      "employee_id": 169,
      "employee_name": "صالح ناصر يسلم",
      "date": "2024-01-15",
      "check_in": "2024-01-15T07:30:00",
      "check_out": "2024-01-15T16:00:00",
      "status": "حاضر",
      "notes": null,
      "overtime_hours": 0.0,
      "late_minutes": 0
    }
  ],
  "pagination": {
    "page": 1,
    "pages": 3,
    "total": 45
  }
}
```

### 2. تسجيل الحضور (للموظفين فقط)
```http
POST /api/v1/attendance/check-in
Authorization: Bearer EMPLOYEE_JWT_TOKEN
Content-Type: application/json

{}
```

### 3. تسجيل الانصراف (للموظفين فقط)
```http
POST /api/v1/attendance/check-out
Authorization: Bearer EMPLOYEE_JWT_TOKEN
Content-Type: application/json

{}
```

---

## المركبات (Vehicles)

### 1. جلب قائمة المركبات
```http
GET /api/v1/vehicles?status=متاح&search=ABC
Authorization: Bearer YOUR_JWT_TOKEN
```

**الرد:**
```json
{
  "vehicles": [
    {
      "id": 25,
      "plate_number": "ABC-1234",
      "model": "تويوتا كامري",
      "year": 2022,
      "color": "أبيض",
      "type": "سيارة",
      "status": "متاح",
      "driver_id": null,
      "driver_name": null,
      "insurance_expiry": "2024-12-31",
      "license_expiry": "2024-12-31",
      "maintenance_due": "2024-06-15"
    }
  ]
}
```

### 2. جلب مركبات موظف محدد
```http
GET /api/v1/employees/169/vehicles
Authorization: Bearer YOUR_JWT_TOKEN
```

---

## الرواتب (Salaries)

### جلب رواتب موظف محدد
```http
GET /api/v1/employees/169/salaries?page=1
Authorization: Bearer YOUR_JWT_TOKEN
```

**الرد:**
```json
{
  "salaries": [
    {
      "id": 45,
      "month": 12,
      "year": 2023,
      "basic_salary": 8000.00,
      "allowances": 1000.00,
      "overtime": 500.00,
      "deductions": 200.00,
      "net_salary": 9300.00,
      "status": "مدفوع",
      "payment_date": "2023-12-30"
    }
  ]
}
```

---

## الأقسام (Departments)

### جلب قائمة الأقسام
```http
GET /api/v1/departments
Authorization: Bearer YOUR_JWT_TOKEN
```

**الرد:**
```json
{
  "departments": [
    {
      "id": 1,
      "name": "قسم التشغيل",
      "description": "مسؤول عن تشغيل المعدات",
      "manager_id": 5,
      "manager_name": "أحمد المدير",
      "employees_count": 25
    }
  ]
}
```

---

## الوثائق (Documents)

### جلب وثائق موظف محدد
```http
GET /api/v1/employees/169/documents
Authorization: Bearer YOUR_JWT_TOKEN
```

**الرد:**
```json
{
  "documents": [
    {
      "id": 78,
      "title": "عقد العمل",
      "type": "contract",
      "file_path": "/static/uploads/documents/contract_169.pdf",
      "upload_date": "2023-01-15T10:30:00",
      "file_size": 2048576,
      "description": "عقد العمل الأصلي"
    }
  ]
}
```

---

## إحصائيات لوحة التحكم

### جلب الإحصائيات العامة
```http
GET /api/v1/dashboard/stats
Authorization: Bearer YOUR_JWT_TOKEN
```

**الرد:**
```json
{
  "total_employees": 95,
  "total_departments": 8,
  "total_vehicles": 45,
  "today_attendance": 78,
  "present_today": 72,
  "absent_today": 6,
  "vehicles_in_use": 32,
  "vehicles_available": 13
}
```

---

## بوابة الموظفين (Employee Portal)

### 1. الملف الشخصي للموظف
```http
GET /api/v1/employee/profile
Authorization: Bearer EMPLOYEE_JWT_TOKEN
```

### 2. ملخص حضور الموظف
```http
GET /api/v1/employee/attendance/summary
Authorization: Bearer EMPLOYEE_JWT_TOKEN
```

**الرد:**
```json
{
  "monthly_summary": {
    "present_days": 20,
    "absent_days": 2,
    "late_days": 3,
    "total_days": 22
  },
  "today_status": {
    "checked_in": true,
    "checked_out": false,
    "check_in_time": "2024-01-15T07:45:00",
    "check_out_time": null
  }
}
```

---

## رموز الحالة والأخطاء

### رموز النجاح
- `200 OK`: تم بنجاح
- `201 Created`: تم الإنشاء بنجاح

### رموز الخطأ
- `400 Bad Request`: طلب غير صحيح
- `401 Unauthorized`: غير مصرح
- `403 Forbidden`: ممنوع
- `404 Not Found`: غير موجود
- `500 Internal Server Error`: خطأ داخلي

### أمثلة على رسائل الخطأ
```json
{
  "error": "Token مطلوب"
}
```

```json
{
  "error": "بيانات تسجيل الدخول غير صحيحة"
}
```

---

## أمثلة على تطبيقات الجوال

### React Native / Flutter
```javascript
// تسجيل الدخول
const login = async (email, password) => {
  const response = await fetch('https://your-domain.com/api/v1/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ email, password }),
  });
  
  const data = await response.json();
  
  if (response.ok) {
    // حفظ التوكن
    await AsyncStorage.setItem('token', data.token);
    return data;
  } else {
    throw new Error(data.error);
  }
};

// جلب الموظفين
const getEmployees = async () => {
  const token = await AsyncStorage.getItem('token');
  
  const response = await fetch('https://your-domain.com/api/v1/employees', {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  
  return await response.json();
};

// تسجيل الحضور
const checkIn = async () => {
  const token = await AsyncStorage.getItem('token');
  
  const response = await fetch('https://your-domain.com/api/v1/attendance/check-in', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({}),
  });
  
  return await response.json();
};
```

### Dart/Flutter
```dart
import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  static const String baseUrl = 'https://your-domain.com/api/v1';
  
  static Future<Map<String, dynamic>> login(String email, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email, 'password': password}),
    );
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Login failed');
    }
  }
  
  static Future<List<dynamic>> getEmployees(String token) async {
    final response = await http.get(
      Uri.parse('$baseUrl/employees'),
      headers: {'Authorization': 'Bearer $token'},
    );
    
    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return data['employees'];
    } else {
      throw Exception('Failed to load employees');
    }
  }
}
```

---

---

## إدارة المستخدمين (Users Management)

### جلب قائمة المستخدمين
```http
GET /api/v1/users?page=1&per_page=20
Authorization: Bearer YOUR_JWT_TOKEN
```

### إنشاء مستخدم جديد
```http
POST /api/v1/users
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json

{
  "name": "أحمد محمد",
  "email": "ahmed@company.com",
  "password": "secure_password",
  "role": "manager",
  "department_id": 1,
  "permissions": 127,
  "is_active": true
}
```

---

## التقارير والتحليلات (Reports & Analytics)

### تقرير ملخص الموظفين
```http
GET /api/v1/reports/employees/summary?department_id=1
Authorization: Bearer YOUR_JWT_TOKEN
```

**الرد:**
```json
{
  "total_employees": 45,
  "status_breakdown": {
    "active": 42,
    "inactive": 3
  },
  "department_breakdown": {
    "قسم التشغيل": 25,
    "قسم الصيانة": 20
  },
  "nationality_breakdown": {
    "سعودي": 30,
    "مصري": 10,
    "باكستاني": 5
  },
  "average_salary": 7500.00
}
```

### تقرير الحضور الشهري
```http
GET /api/v1/reports/attendance/monthly?year=2024&month=6&department_id=1
Authorization: Bearer YOUR_JWT_TOKEN
```

### تقرير حالة المركبات
```http
GET /api/v1/reports/vehicles/status
Authorization: Bearer YOUR_JWT_TOKEN
```

**الرد:**
```json
{
  "total_vehicles": 20,
  "status_breakdown": {
    "متاح": 8,
    "قيد الاستخدام": 12
  },
  "type_breakdown": {
    "سيارة": 15,
    "شاحنة": 5
  },
  "expiring_insurance": [
    {
      "id": 5,
      "plate_number": "ABC-123",
      "insurance_expiry": "2024-07-15",
      "days_remaining": 25
    }
  ]
}
```

### تقرير ملخص الرواتب
```http
GET /api/v1/reports/salaries/summary?year=2024&month=6
Authorization: Bearer YOUR_JWT_TOKEN
```

---

## إدارة تسليم واستلام المركبات

### جلب سجلات التسليم والاستلام
```http
GET /api/v1/vehicle-handovers?vehicle_id=5&handover_type=تسليم
Authorization: Bearer YOUR_JWT_TOKEN
```

### إنشاء سجل تسليم/استلام
```http
POST /api/v1/vehicle-handovers
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json

{
  "vehicle_id": 5,
  "employee_id": 169,
  "handover_type": "تسليم",
  "handover_date": "2024-06-11T14:30:00",
  "notes": "تسليم مركبة في حالة جيدة"
}
```

---

## البحث المتقدم

### البحث في جميع البيانات
```http
POST /api/v1/search
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json

{
  "query": "أحمد",
  "filters": {
    "department_id": 1
  }
}
```

**الرد:**
```json
{
  "employees": [
    {
      "id": 169,
      "name": "أحمد محمد علي",
      "employee_id": "50799",
      "department": "قسم التشغيل",
      "job_title": "مهندس",
      "mobile": "+966501234567"
    }
  ],
  "vehicles": [
    {
      "id": 3,
      "plate_number": "أحمد-123",
      "model": "تويوتا كامري",
      "status": "متاح"
    }
  ],
  "departments": []
}
```

---

## تحليلات الأداء المتقدمة

### تحليل أداء الموظفين
```http
GET /api/v1/analytics/employee-performance?year=2024&month=6&department_id=1
Authorization: Bearer YOUR_JWT_TOKEN
```

**الرد:**
```json
{
  "period": "2024-06",
  "total_employees_analyzed": 25,
  "performance_data": [
    {
      "employee_id": 169,
      "employee_name": "أحمد محمد",
      "attendance_rate": 96.67,
      "punctuality_rate": 93.33,
      "total_days": 30,
      "present_days": 29,
      "absent_days": 1,
      "late_days": 2,
      "overtime_hours": 8.5
    }
  ],
  "summary": {
    "avg_attendance_rate": 94.2,
    "avg_punctuality_rate": 91.8,
    "total_overtime_hours": 156.5
  }
}
```

---

## التقارير المالية

### تقرير كشف الرواتب المالي
```http
GET /api/v1/reports/financial/payroll?year=2024&month=6
Authorization: Bearer YOUR_JWT_TOKEN
```

**الرد:**
```json
{
  "period": "2024-06",
  "payroll_summary": {
    "total_employees": 45,
    "total_gross_salary": 350000.00,
    "total_deductions": 15000.00,
    "total_net_salary": 335000.00,
    "average_salary": 7444.44
  },
  "payroll_details": [
    {
      "employee_id": "50799",
      "employee_name": "أحمد محمد",
      "department": "قسم التشغيل",
      "basic_salary": 8000.00,
      "allowances": 1000.00,
      "bonus": 500.00,
      "gross_salary": 9500.00,
      "deductions": 200.00,
      "net_salary": 9300.00,
      "payment_status": "مدفوع"
    }
  ]
}
```

---

## الخط الزمني للموظف

### جلب تاريخ أنشطة الموظف
```http
GET /api/v1/employees/169/timeline
Authorization: Bearer YOUR_JWT_TOKEN
```

**الرد:**
```json
{
  "employee": {
    "id": 169,
    "name": "أحمد محمد",
    "employee_id": "50799"
  },
  "timeline": [
    {
      "date": "2024-06-11",
      "type": "attendance",
      "title": "حضور - حاضر",
      "description": "حضور: 08:00, انصراف: 16:30",
      "icon": "clock"
    },
    {
      "date": "2024-06-10",
      "type": "vehicle",
      "title": "تسليم مركبة",
      "description": "تسليم مركبة ABC-123",
      "icon": "truck"
    },
    {
      "date": "2024-01-15",
      "type": "join",
      "title": "التحق بالعمل",
      "description": "انضم أحمد محمد للشركة",
      "icon": "user-plus"
    }
  ]
}
```

---

## العمليات الجماعية

### تسجيل حضور جماعي
```http
POST /api/v1/bulk/attendance
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json

{
  "operation": "mark_present",
  "employee_ids": [169, 171, 172],
  "date": "2024-06-11"
}
```

**الرد:**
```json
{
  "message": "تم تنفيذ العملية بنجاح. نجح: 3, فشل: 0",
  "results": {
    "success": 3,
    "failed": 0,
    "errors": []
  }
}
```

---

## الإشعارات

### جلب إشعارات النظام
```http
GET /api/v1/notifications
Authorization: Bearer YOUR_JWT_TOKEN
```

**الرد:**
```json
{
  "notifications": [
    {
      "type": "warning",
      "title": "انتهاء صلاحية التأمين",
      "message": "تأمين المركبة ABC-123 ينتهي خلال 15 يوم",
      "entity_type": "vehicle",
      "entity_id": 5,
      "created_at": "2024-06-11T14:30:00"
    },
    {
      "type": "info",
      "title": "موظف جديد",
      "message": "انضم الموظف محمد أحمد للنظام",
      "entity_type": "employee",
      "entity_id": 175,
      "created_at": "2024-06-10T09:15:00"
    }
  ],
  "unread_count": 5
}
```

---

## إعدادات النظام

### جلب إعدادات النظام
```http
GET /api/v1/settings
Authorization: Bearer YOUR_JWT_TOKEN
```

**الرد:**
```json
{
  "system_name": "نظام نُظم",
  "version": "2.0.0",
  "attendance_settings": {
    "work_start_time": "08:00",
    "work_end_time": "16:00",
    "late_threshold_minutes": 15,
    "overtime_threshold_hours": 8
  },
  "salary_settings": {
    "currency": "ريال سعودي",
    "default_allowances": 500.0,
    "overtime_rate_multiplier": 1.5
  },
  "vehicle_settings": {
    "insurance_warning_days": 30,
    "maintenance_warning_days": 15
  }
}
```

---

## سجلات النظام والتدقيق

### جلب سجلات العمليات
```http
GET /api/v1/audit-logs?action=login&user_id=1&date_from=2024-06-01
Authorization: Bearer YOUR_JWT_TOKEN
```

---

## رفع الوثائق

### رفع وثيقة للموظف
```http
POST /api/v1/documents/upload
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: multipart/form-data

employee_id: 169
document_type: contract
description: عقد العمل الأصلي
file: [FILE_UPLOAD]
```

---

## الخلاصة

هذا API شامل ومتكامل يغطي جميع جوانب نظام نُظم:

✅ **مصادقة آمنة** باستخدام JWT للمستخدمين والموظفين  
✅ **إدارة المستخدمين** مع الأدوار والصلاحيات  
✅ **إدارة الموظفين** الكاملة مع الملفات الشخصية  
✅ **نظام الحضور والانصراف** المتطور  
✅ **إدارة المركبات** وتسليم/استلام المركبات  
✅ **نظام الرواتب** والتقارير المالية  
✅ **إدارة الوثائق** ورفع الملفات  
✅ **التقارير والتحليلات** المتقدمة  
✅ **تحليلات الأداء** للموظفين والأقسام  
✅ **البحث المتقدم** في جميع البيانات  
✅ **العمليات الجماعية** لتوفير الوقت  
✅ **نظام الإشعارات** الذكي  
✅ **الخط الزمني** لأنشطة الموظفين  
✅ **سجلات التدقيق** والعمليات  
✅ **إعدادات النظام** القابلة للتخصيص  
✅ **بوابة الموظفين** المستقلة  

يمكن استخدام هذا API مع أي تطبيق جوال أو نظام خارجي يدعم HTTP و JSON، مما يوفر حلاً متكاملاً لإدارة الموارد البشرية والمركبات.