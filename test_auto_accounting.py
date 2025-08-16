#!/usr/bin/env python3
"""
اختبار سريع لنظام الربط المحاسبي الذكي
"""
import requests
import json

# إعدادات الاتصال
BASE_URL = 'http://localhost:5000'
LOGIN_DATA = {
    'email': 'admin@admin.com',
    'password': 'admin123'
}

def test_auto_accounting():
    """اختبار شامل لنظام الربط المحاسبي"""
    
    # إنشاء جلسة
    session = requests.Session()
    
    print("🔐 تسجيل الدخول...")
    
    # تسجيل الدخول
    login_response = session.post(f'{BASE_URL}/auth/login', data=LOGIN_DATA)
    if login_response.status_code == 200:
        print("✅ تم تسجيل الدخول بنجاح")
    else:
        print(f"❌ فشل تسجيل الدخول: {login_response.status_code}")
        return
    
    print("\n📊 اختبار حالة النظام...")
    
    # اختبار حالة النظام
    try:
        status_response = session.get(f'{BASE_URL}/integrated/api/sync/status')
        if status_response.status_code == 200:
            print("✅ API حالة النظام يعمل")
            print(f"📝 الاستجابة: {status_response.text[:200]}...")
        else:
            print(f"❌ فشل API حالة النظام: {status_response.status_code}")
    except Exception as e:
        print(f"❌ خطأ في API حالة النظام: {e}")
    
    print("\n💰 اختبار ربط الرواتب...")
    
    # اختبار ربط الرواتب
    try:
        salary_response = session.post(f'{BASE_URL}/integrated/api/sync/salaries')
        if salary_response.status_code == 200:
            print("✅ API ربط الرواتب يعمل")
            print(f"📝 الاستجابة: {salary_response.text[:200]}...")
        else:
            print(f"❌ فشل API ربط الرواتب: {salary_response.status_code}")
    except Exception as e:
        print(f"❌ خطأ في API ربط الرواتب: {e}")
    
    print("\n🚗 اختبار ربط السيارات...")
    
    # اختبار ربط السيارات
    try:
        vehicle_response = session.post(f'{BASE_URL}/integrated/api/sync/vehicles')
        if vehicle_response.status_code == 200:
            print("✅ API ربط السيارات يعمل")
            print(f"📝 الاستجابة: {vehicle_response.text[:200]}...")
        else:
            print(f"❌ فشل API ربط السيارات: {vehicle_response.status_code}")
    except Exception as e:
        print(f"❌ خطأ في API ربط السيارات: {e}")
    
    print("\n🔄 اختبار الربط الشامل...")
    
    # اختبار الربط الشامل
    try:
        full_response = session.post(f'{BASE_URL}/integrated/api/sync/full')
        if full_response.status_code == 200:
            print("✅ API الربط الشامل يعمل")
            print(f"📝 الاستجابة: {full_response.text[:200]}...")
        else:
            print(f"❌ فشل API الربط الشامل: {full_response.status_code}")
    except Exception as e:
        print(f"❌ خطأ في API الربط الشامل: {e}")
    
    print("\n🌐 اختبار صفحة الربط المحاسبي...")
    
    # اختبار صفحة الربط المحاسبي
    try:
        page_response = session.get(f'{BASE_URL}/integrated/auto-accounting')
        if page_response.status_code == 200:
            print("✅ صفحة الربط المحاسبي تعمل")
            if 'الربط المحاسبي الذكي' in page_response.text:
                print("✅ العنوان موجود بالصفحة")
            else:
                print("⚠️ العنوان غير موجود بالصفحة")
        else:
            print(f"❌ فشل تحميل صفحة الربط المحاسبي: {page_response.status_code}")
    except Exception as e:
        print(f"❌ خطأ في صفحة الربط المحاسبي: {e}")
    
    print("\n✨ انتهى الاختبار!")

if __name__ == "__main__":
    test_auto_accounting()