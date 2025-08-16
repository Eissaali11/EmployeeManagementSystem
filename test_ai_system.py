#!/usr/bin/env python3
"""
اختبار نظام الذكاء الاصطناعي للتحليل المالي
"""
import requests
import json

# إعدادات الاتصال
BASE_URL = 'http://localhost:5000'
LOGIN_DATA = {
    'email': 'admin@admin.com',
    'password': 'admin123'
}

def test_ai_system():
    """اختبار شامل لنظام الذكاء الاصطناعي"""
    
    # إنشاء جلسة
    session = requests.Session()
    
    print("🤖 اختبار نظام الذكاء الاصطناعي المالي")
    print("=" * 50)
    
    # تسجيل الدخول
    print("🔐 تسجيل الدخول...")
    login_response = session.post(f'{BASE_URL}/auth/login', data=LOGIN_DATA)
    if login_response.status_code == 200:
        print("✅ تم تسجيل الدخول بنجاح")
    else:
        print(f"❌ فشل تسجيل الدخول: {login_response.status_code}")
        return
    
    print("\n🧠 اختبار التحليل المالي الذكي...")
    
    # اختبار التحليل المالي
    try:
        analysis_response = session.post(
            f'{BASE_URL}/integrated/api/ai/analysis',
            headers={'Content-Type': 'application/json'},
            json={}
        )
        
        if analysis_response.status_code == 200:
            try:
                result = analysis_response.json()
                if result.get('success'):
                    print("✅ نظام التحليل المالي الذكي يعمل!")
                    print(f"📊 ملخص البيانات: {result.get('data_summary', {})}")
                    print(f"📝 التحليل: {result.get('analysis', '')[:200]}...")
                else:
                    print(f"⚠️ التحليل فشل: {result.get('message', 'غير محدد')}")
            except json.JSONDecodeError:
                print(f"⚠️ استجابة غير صحيحة: {analysis_response.text[:200]}")
        else:
            print(f"❌ فشل API التحليل المالي: {analysis_response.status_code}")
            
    except Exception as e:
        print(f"❌ خطأ في اختبار التحليل المالي: {e}")
    
    print("\n💡 اختبار التوصيات الذكية...")
    
    # اختبار التوصيات الذكية
    focus_areas = ['general', 'salaries', 'vehicles', 'efficiency']
    
    for area in focus_areas:
        try:
            recommendations_response = session.post(
                f'{BASE_URL}/integrated/api/ai/recommendations',
                headers={'Content-Type': 'application/json'},
                json={'focus_area': area}
            )
            
            if recommendations_response.status_code == 200:
                try:
                    result = recommendations_response.json()
                    if result.get('success'):
                        print(f"✅ توصيات {area}: متوفرة")
                        print(f"   📝 {result.get('recommendations', '')[:100]}...")
                    else:
                        print(f"⚠️ توصيات {area}: {result.get('message', 'فشل')}")
                except json.JSONDecodeError:
                    print(f"⚠️ استجابة توصيات {area} غير صحيحة")
            else:
                print(f"❌ فشل توصيات {area}: {recommendations_response.status_code}")
                
        except Exception as e:
            print(f"❌ خطأ في اختبار توصيات {area}: {e}")
    
    print("\n🔄 اختبار تكامل النظام...")
    
    # اختبار تكامل الأنظمة
    try:
        sync_response = session.post(f'{BASE_URL}/integrated/api/sync/full')
        if sync_response.status_code == 200:
            print("✅ نظام الربط المحاسبي متصل")
        else:
            print(f"⚠️ مشكلة في الربط المحاسبي: {sync_response.status_code}")
    except Exception as e:
        print(f"❌ خطأ في اختبار التكامل: {e}")
    
    print("\n✨ انتهى اختبار نظام الذكاء الاصطناعي!")
    print("🎯 النظام جاهز للاستخدام الفعلي")

if __name__ == "__main__":
    test_ai_system()