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

## الخلاصة

هذا API شامل يوفر:

✅ **مصادقة آمنة** باستخدام JWT  
✅ **إدارة الموظفين** الكاملة  
✅ **تسجيل الحضور والانصراف**  
✅ **إدارة المركبات**  
✅ **نظام الرواتب**  
✅ **الوثائق والملفات**  
✅ **إحصائيات متقدمة**  
✅ **بوابة الموظفين المستقلة**  

يمكن استخدامه مع أي تطبيق جوال أو نظام خارجي يدعم HTTP و JSON.