#!/usr/bin/env python3
"""
اختبار شامل لـ API نظام نُظم
يختبر جميع endpoints والوحدات المتاحة
"""

import requests
import json
import sys
from datetime import datetime

BASE_URL = "http://localhost:5000/api/v1"

def test_api():
    print("🔄 اختبار شامل لـ API نظام نُظم")
    print("=" * 50)
    
    # تسجيل دخول الموظف والحصول على token
    print("1. تسجيل دخول الموظف...")
    login_data = {
        "employee_id": "4298",
        "national_id": "2489682019"
    }
    
    response = requests.post(f"{BASE_URL}/auth/employee-login", json=login_data)
    if response.status_code != 200:
        print(f"❌ فشل تسجيل الدخول: {response.text}")
        return
    
    token = response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ تم تسجيل الدخول بنجاح")
    
    # اختبار الوحدات المختلفة
    tests = [
        # الإحصائيات العامة
        {
            "name": "الإحصائيات العامة",
            "method": "GET",
            "endpoint": "/dashboard/stats"
        },
        
        # إدارة الموظفين
        {
            "name": "قائمة الموظفين",
            "method": "GET", 
            "endpoint": "/employees?page=1&per_page=5"
        },
        {
            "name": "بيانات موظف محدد",
            "method": "GET",
            "endpoint": "/employees/179"
        },
        
        # إدارة الأقسام
        {
            "name": "قائمة الأقسام",
            "method": "GET",
            "endpoint": "/departments"
        },
        
        # إدارة المركبات
        {
            "name": "قائمة المركبات",
            "method": "GET",
            "endpoint": "/vehicles?page=1&per_page=5"
        },
        
        # سجلات الحضور
        {
            "name": "سجلات الحضور",
            "method": "GET",
            "endpoint": "/attendance?page=1&per_page=5"
        },
        
        # الرواتب
        {
            "name": "سجلات الرواتب",
            "method": "GET",
            "endpoint": "/employees/179/salaries"
        },
        
        # الوثائق
        {
            "name": "وثائق الموظف",
            "method": "GET", 
            "endpoint": "/employees/179/documents"
        },
        
        # التقارير والتحليلات
        {
            "name": "تقرير ملخص الموظفين",
            "method": "GET",
            "endpoint": "/reports/employees/summary"
        },
        {
            "name": "تقرير الحضور الشهري",
            "method": "GET",
            "endpoint": f"/reports/attendance/monthly?year={datetime.now().year}&month={datetime.now().month}"
        },
        {
            "name": "تقرير حالة المركبات", 
            "method": "GET",
            "endpoint": "/reports/vehicles/status"
        },
        {
            "name": "تقرير ملخص الرواتب",
            "method": "GET", 
            "endpoint": f"/reports/salaries/summary?year={datetime.now().year}&month={datetime.now().month}"
        },
        
        # التحليلات المتقدمة
        {
            "name": "تحليلات أداء الموظفين",
            "method": "GET",
            "endpoint": f"/analytics/employee-performance?year={datetime.now().year}"
        },
        {
            "name": "التقرير المالي للرواتب",
            "method": "GET",
            "endpoint": f"/reports/financial/payroll?year={datetime.now().year}&month={datetime.now().month}"
        },
        
        # الإشعارات والإعدادات
        {
            "name": "الإشعارات",
            "method": "GET",
            "endpoint": "/notifications"
        },
        {
            "name": "إعدادات النظام",
            "method": "GET",
            "endpoint": "/settings"
        },
        
        # الخط الزمني
        {
            "name": "الخط الزمني للموظف",
            "method": "GET",
            "endpoint": "/employees/179/timeline"
        },
        
        # سجلات التدقيق
        {
            "name": "سجلات التدقيق",
            "method": "GET",
            "endpoint": "/audit-logs"
        },
        
        # البحث المتقدم
        {
            "name": "البحث المتقدم",
            "method": "POST",
            "endpoint": "/search",
            "data": {"query": "محمد", "filters": {}}
        },
        
        # بوابة الموظف
        {
            "name": "ملف الموظف الشخصي",
            "method": "GET",
            "endpoint": "/employee/profile"
        },
        {
            "name": "ملخص حضور الموظف",
            "method": "GET",
            "endpoint": "/employee/attendance-summary"
        }
    ]
    
    print(f"\n2. اختبار {len(tests)} وحدة في الـ API:")
    print("-" * 50)
    
    success_count = 0
    
    for i, test in enumerate(tests, 1):
        try:
            print(f"{i:2d}. {test['name']}...", end=" ")
            
            if test['method'] == 'GET':
                response = requests.get(f"{BASE_URL}{test['endpoint']}", headers=headers)
            elif test['method'] == 'POST':
                response = requests.post(f"{BASE_URL}{test['endpoint']}", 
                                       headers={**headers, "Content-Type": "application/json"},
                                       json=test.get('data', {}))
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and 'error' not in data:
                    print("✅")
                    success_count += 1
                else:
                    print(f"⚠️  {data.get('error', 'خطأ غير معروف')}")
            else:
                print(f"❌ {response.status_code}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
    
    print("-" * 50)
    print(f"📊 النتائج: {success_count}/{len(tests)} وحدة تعمل بنجاح")
    print(f"📈 معدل النجاح: {(success_count/len(tests)*100):.1f}%")
    
    # اختبار إضافي: تسجيل حضور
    print("\n3. اختبار تسجيل الحضور...")
    try:
        checkin_response = requests.post(f"{BASE_URL}/attendance/checkin", headers=headers)
        if checkin_response.status_code == 200:
            print("✅ تم تسجيل الحضور بنجاح")
        else:
            print(f"⚠️  {checkin_response.json().get('message', 'تم تسجيل الحضور مسبقاً')}")
    except Exception as e:
        print(f"❌ خطأ في تسجيل الحضور: {str(e)}")
    
    print("\n🎉 اكتمل الاختبار الشامل للـ API")
    
    return success_count >= len(tests) * 0.8  # 80% success rate

if __name__ == "__main__":
    success = test_api()
    sys.exit(0 if success else 1)