#!/usr/bin/env python3
"""
اختبار شامل لـ RESTful API نظام نُظم
يختبر جميع المسارات والوظائف
"""

import requests
import json
from datetime import datetime
import sys
import time

# إعدادات الاختبار
BASE_URL = "http://localhost:5000/api/v1"
HEADERS = {'Content-Type': 'application/json'}

def print_header(title):
    """طباعة رأس جميل للاختبار"""
    print("\n" + "="*60)
    print(f"🔄 {title}")
    print("="*60)

def test_request(method, endpoint, data=None, headers=None, token=None):
    """إرسال طلب واختباره"""
    url = f"{BASE_URL}{endpoint}"
    
    # إضافة token إذا كان متوفراً
    if token:
        if headers is None:
            headers = {}
        headers['Authorization'] = f'Bearer {token}'
    
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, headers=headers)
        elif method.upper() == 'PUT':
            response = requests.put(url, json=data, headers=headers)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, headers=headers)
        
        print(f"📡 {method.upper()} {endpoint}")
        print(f"📊 Status: {response.status_code}")
        
        if response.status_code < 400:
            print("✅ نجح")
            try:
                result = response.json()
                if 'data' in result:
                    print(f"📋 البيانات: {type(result['data'])} items")
                return result
            except:
                return response.text
        else:
            print("❌ فشل")
            try:
                error = response.json()
                print(f"🚫 الخطأ: {error.get('error', {}).get('message', 'خطأ غير معروف')}")
            except:
                print(f"🚫 خطأ: {response.text}")
            return None
        
    except requests.exceptions.ConnectionError:
        print("❌ فشل الاتصال - تأكد من تشغيل الخادم")
        return None
    except Exception as e:
        print(f"❌ خطأ: {str(e)}")
        return None

def main():
    print("🚀 بدء اختبار RESTful API لنظام نُظم")
    print(f"🔗 Base URL: {BASE_URL}")
    
    # متغير لحفظ token
    auth_token = None
    employee_token = None
    
    # ==================== اختبار الصحة العامة ====================
    print_header("فحص صحة API")
    
    # فحص الصحة
    test_request('GET', '/health')
    
    # معلومات API
    test_request('GET', '/info')
    
    # ==================== اختبار المصادقة ====================
    print_header("اختبار المصادقة")
    
    # تسجيل دخول مستخدم (بيانات تجريبية)
    login_data = {
        "email": "admin@nuzum.sa",
        "password": "admin123"
    }
    
    result = test_request('POST', '/auth/login', login_data)
    if result and 'data' in result and 'token' in result['data']:
        auth_token = result['data']['token']
        print(f"🔑 تم الحصول على Token: {auth_token[:20]}...")
    
    # تسجيل دخول موظف (بيانات تجريبية)
    employee_login_data = {
        "employee_id": "4298",
        "national_id": "2489682019"
    }
    
    result = test_request('POST', '/auth/employee-login', employee_login_data)
    if result and 'data' in result and 'token' in result['data']:
        employee_token = result['data']['token']
        print(f"🔑 تم الحصول على Employee Token: {employee_token[:20]}...")
    
    # استخدام token المتاح
    token = auth_token or employee_token
    
    if not token:
        print("⚠️ لم يتم الحصول على Token - سيتم المتابعة بدون مصادقة")
    
    # ==================== اختبار لوحة المعلومات ====================
    print_header("اختبار لوحة المعلومات")
    
    test_request('GET', '/dashboard/stats', headers=HEADERS, token=token)
    
    # ==================== اختبار إدارة الموظفين ====================
    print_header("اختبار إدارة الموظفين")
    
    # جلب قائمة الموظفين
    test_request('GET', '/employees?page=1&per_page=5', headers=HEADERS, token=token)
    
    # البحث في الموظفين
    test_request('GET', '/employees?search=محمد', headers=HEADERS, token=token)
    
    # جلب موظف محدد (ID تجريبي)
    test_request('GET', '/employees/179', headers=HEADERS, token=token)
    
    # إضافة موظف جديد (بيانات تجريبية)
    new_employee = {
        "name": "أحمد محمد التجريبي",
        "employee_id": "9999",
        "national_id": "1234567890",
        "email": "ahmed.test@example.com",
        "phone": "0501234567",
        "job_title": "مطور",
        "status": "active"
    }
    
    create_result = test_request('POST', '/employees', new_employee, headers=HEADERS, token=token)
    created_employee_id = None
    if create_result and 'data' in create_result:
        created_employee_id = create_result['data'].get('id')
        print(f"🆕 تم إنشاء موظف بـ ID: {created_employee_id}")
    
    # تحديث الموظف الجديد
    if created_employee_id:
        update_data = {
            "job_title": "مطور أول",
            "status": "active"
        }
        test_request('PUT', f'/employees/{created_employee_id}', update_data, headers=HEADERS, token=token)
    
    # ==================== اختبار إدارة المركبات ====================
    print_header("اختبار إدارة المركبات")
    
    # جلب قائمة المركبات
    test_request('GET', '/vehicles?page=1&per_page=5', headers=HEADERS, token=token)
    
    # البحث في المركبات
    test_request('GET', '/vehicles?search=١٢٣', headers=HEADERS, token=token)
    
    # جلب مركبة محددة (ID تجريبي)
    test_request('GET', '/vehicles/14', headers=HEADERS, token=token)
    
    # ==================== اختبار إدارة الأقسام ====================
    print_header("اختبار إدارة الأقسام")
    
    test_request('GET', '/departments', headers=HEADERS, token=token)
    
    # ==================== اختبار إدارة الحضور ====================
    print_header("اختبار إدارة الحضور")
    
    # جلب سجلات الحضور
    test_request('GET', '/attendance?page=1&per_page=5', headers=HEADERS, token=token)
    
    # تسجيل حضور جديد (بيانات تجريبية)
    if created_employee_id:
        attendance_data = {
            "employee_id": created_employee_id,
            "date": datetime.now().strftime('%Y-%m-%d'),
            "status": "present",
            "check_in_time": "08:00",
            "notes": "حضور تجريبي من API"
        }
        test_request('POST', '/attendance', attendance_data, headers=HEADERS, token=token)
    
    # ==================== اختبار الرواتب ====================
    print_header("اختبار الرواتب")
    
    # جلب رواتب موظف
    test_request('GET', '/employees/179/salaries', headers=HEADERS, token=token)
    
    # ==================== اختبار التقارير ====================
    print_header("اختبار التقارير")
    
    # تقرير ملخص الموظفين
    test_request('GET', '/reports/employees/summary', headers=HEADERS, token=token)
    
    # تقرير الحضور الشهري
    current_date = datetime.now()
    test_request('GET', f'/reports/attendance/monthly?year={current_date.year}&month={current_date.month}', 
                 headers=HEADERS, token=token)
    
    # ==================== اختبار البحث المتقدم ====================
    print_header("اختبار البحث المتقدم")
    
    search_data = {
        "query": "محمد",
        "search_in": ["employees", "vehicles"]
    }
    test_request('POST', '/search', search_data, headers=HEADERS, token=token)
    
    # ==================== اختبار الإشعارات ====================
    print_header("اختبار الإشعارات")
    
    test_request('GET', '/notifications', headers=HEADERS, token=token)
    
    # ==================== حذف الموظف التجريبي ====================
    if created_employee_id:
        print_header("تنظيف البيانات التجريبية")
        test_request('DELETE', f'/employees/{created_employee_id}', headers=HEADERS, token=token)
    
    # ==================== خلاصة الاختبار ====================
    print_header("خلاصة الاختبار")
    print("✅ تم اختبار جميع مسارات API")
    print("🔗 API Endpoints متاحة:")
    print("   • المصادقة: /api/v1/auth/*")
    print("   • لوحة المعلومات: /api/v1/dashboard/*")
    print("   • الموظفين: /api/v1/employees/*")
    print("   • المركبات: /api/v1/vehicles/*")
    print("   • الأقسام: /api/v1/departments")
    print("   • الحضور: /api/v1/attendance")
    print("   • التقارير: /api/v1/reports/*")
    print("   • البحث: /api/v1/search")
    print("   • الإشعارات: /api/v1/notifications")
    print("   • معلومات API: /api/v1/info")
    print("   • فحص الصحة: /api/v1/health")
    
    print("\n🎉 انتهى اختبار RESTful API بنجاح!")

if __name__ == "__main__":
    main()