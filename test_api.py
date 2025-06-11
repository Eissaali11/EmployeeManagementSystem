#!/usr/bin/env python3
"""
اختبار شامل لـ API نظام نُظم
"""

import requests
import json
from datetime import datetime

# عنوان الخادم
BASE_URL = "http://localhost:5000/api/v1"

def test_employee_login():
    """اختبار تسجيل دخول الموظف"""
    print("🔑 اختبار تسجيل دخول الموظف...")
    
    url = f"{BASE_URL}/auth/employee-login"
    data = {
        "employee_id": "4298",
        "national_id": "2489682019"
    }
    
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ نجح تسجيل الدخول للموظف: {result['employee']['name']}")
        return result['token']
    else:
        print(f"❌ فشل تسجيل الدخول: {response.text}")
        return None

def test_user_login():
    """اختبار تسجيل دخول المستخدم العادي"""
    print("\n🔑 اختبار تسجيل دخول المستخدم...")
    
    url = f"{BASE_URL}/auth/login"
    data = {
        "email": "z.alhamdani@rassaudi.com",
        "password": "123456"
    }
    
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ نجح تسجيل الدخول للمستخدم: {result['user']['name']}")
        return result['token']
    else:
        print(f"❌ فشل تسجيل الدخول: {response.text}")
        return None

def test_get_employees(token):
    """اختبار جلب قائمة الموظفين"""
    print("\n👥 اختبار جلب قائمة الموظفين...")
    
    url = f"{BASE_URL}/employees"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ تم جلب {len(result['employees'])} موظف")
        print(f"📊 إجمالي الموظفين: {result['pagination']['total']}")
        
        if result['employees']:
            first_employee = result['employees'][0]
            print(f"📝 أول موظف: {first_employee['name']} (ID: {first_employee['employee_id']})")
            return first_employee['id']
    else:
        print(f"❌ فشل جلب الموظفين: {response.text}")
        return None

def test_get_employee_details(token, employee_id):
    """اختبار جلب تفاصيل موظف محدد"""
    print(f"\n📋 اختبار جلب تفاصيل الموظف {employee_id}...")
    
    url = f"{BASE_URL}/employees/{employee_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        employee = response.json()
        print(f"✅ تم جلب بيانات الموظف: {employee['name']}")
        print(f"   🏢 القسم: {employee.get('department', 'غير محدد')}")
        print(f"   💼 المسمى الوظيفي: {employee.get('job_title', 'غير محدد')}")
        print(f"   📱 الجوال: {employee.get('mobile', 'غير محدد')}")
    else:
        print(f"❌ فشل جلب بيانات الموظف: {response.text}")

def test_get_attendance(token):
    """اختبار جلب سجلات الحضور"""
    print("\n⏰ اختبار جلب سجلات الحضور...")
    
    url = f"{BASE_URL}/attendance"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ تم جلب {len(result['attendance'])} سجل حضور")
        
        if result['attendance']:
            latest = result['attendance'][0]
            print(f"📅 آخر سجل: {latest['employee_name']} - {latest['date']}")
            print(f"   🕐 الحضور: {latest['check_in'] or 'لم يسجل'}")
            print(f"   🕔 الانصراف: {latest['check_out'] or 'لم يسجل'}")
    else:
        print(f"❌ فشل جلب سجلات الحضور: {response.text}")

def test_check_in(employee_token):
    """اختبار تسجيل الحضور"""
    if not employee_token:
        print("\n❌ لا يوجد token للموظف لاختبار تسجيل الحضور")
        return
        
    print("\n✅ اختبار تسجيل الحضور...")
    
    url = f"{BASE_URL}/attendance/check-in"
    headers = {"Authorization": f"Bearer {employee_token}"}
    
    response = requests.post(url, json={}, headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ تم تسجيل الحضور بنجاح")
    else:
        result = response.json()
        print(f"ℹ️ رسالة: {result.get('error', 'غير معروف')}")

def test_get_vehicles(token):
    """اختبار جلب قائمة المركبات"""
    print("\n🚗 اختبار جلب قائمة المركبات...")
    
    url = f"{BASE_URL}/vehicles"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ تم جلب {len(result['vehicles'])} مركبة")
        
        if result['vehicles']:
            first_vehicle = result['vehicles'][0]
            print(f"🚗 أول مركبة: {first_vehicle['plate_number']} - {first_vehicle['model']}")
            print(f"   📊 الحالة: {first_vehicle['status']}")
    else:
        print(f"❌ فشل جلب المركبات: {response.text}")

def test_get_departments(token):
    """اختبار جلب قائمة الأقسام"""
    print("\n🏢 اختبار جلب قائمة الأقسام...")
    
    url = f"{BASE_URL}/departments"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ تم جلب {len(result['departments'])} قسم")
        
        for dept in result['departments']:
            print(f"   🏢 {dept['name']} - عدد الموظفين: {dept['employees_count']}")
    else:
        print(f"❌ فشل جلب الأقسام: {response.text}")

def test_dashboard_stats(token):
    """اختبار إحصائيات لوحة التحكم"""
    print("\n📊 اختبار إحصائيات لوحة التحكم...")
    
    url = f"{BASE_URL}/dashboard/stats"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        stats = response.json()
        print("✅ إحصائيات النظام:")
        print(f"   👥 إجمالي الموظفين: {stats['total_employees']}")
        print(f"   🏢 إجمالي الأقسام: {stats['total_departments']}")
        print(f"   🚗 إجمالي المركبات: {stats['total_vehicles']}")
        print(f"   ✅ حاضرين اليوم: {stats['present_today']}")
        print(f"   ❌ غائبين اليوم: {stats['absent_today']}")
    else:
        print(f"❌ فشل جلب الإحصائيات: {response.text}")

def test_employee_profile(employee_token):
    """اختبار الملف الشخصي للموظف"""
    if not employee_token:
        print("\n❌ لا يوجد token للموظف لاختبار الملف الشخصي")
        return
        
    print("\n👤 اختبار الملف الشخصي للموظف...")
    
    url = f"{BASE_URL}/employee/profile"
    headers = {"Authorization": f"Bearer {employee_token}"}
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        profile = response.json()
        print(f"✅ الملف الشخصي: {profile['name']}")
        print(f"   🆔 رقم الموظف: {profile['employee_id']}")
        print(f"   🏢 القسم: {profile.get('department', 'غير محدد')}")
        print(f"   💼 المسمى الوظيفي: {profile.get('job_title', 'غير محدد')}")
    else:
        print(f"❌ فشل جلب الملف الشخصي: {response.text}")

def main():
    """تشغيل جميع الاختبارات"""
    print("🚀 بدء اختبار API نظام نُظم\n")
    print("=" * 50)
    
    # اختبار تسجيل دخول المستخدم العادي
    user_token = test_user_login()
    
    # اختبار تسجيل دخول الموظف
    employee_token = test_employee_login()
    
    if user_token:
        # اختبارات تتطلب صلاحيات المستخدم العادي
        employee_id = test_get_employees(user_token)
        
        if employee_id:
            test_get_employee_details(user_token, employee_id)
        
        test_get_attendance(user_token)
        test_get_vehicles(user_token)
        test_get_departments(user_token)
        test_dashboard_stats(user_token)
    
    if employee_token:
        # اختبارات خاصة بالموظفين
        test_employee_profile(employee_token)
        test_check_in(employee_token)
    
    print("\n" + "=" * 50)
    print("✅ انتهاء اختبار API")

if __name__ == "__main__":
    main()