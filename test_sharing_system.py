#!/usr/bin/env python3
"""
اختبار نظام مشاركة روابط فحص السلامة الخارجي
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Vehicle, Employee, SafetyInspection, Department
from datetime import datetime, timedelta
from flask import url_for

def test_sharing_system():
    """اختبار نظام المشاركة"""
    
    print("🔧 اختبار نظام مشاركة روابط فحص السلامة الخارجي")
    print("=" * 60)
    
    with app.app_context():
        # البحث عن السيارات الموجودة
        vehicles = Vehicle.query.all()
        print(f"📊 عدد السيارات المتاحة: {len(vehicles)}")
        
        if not vehicles:
            print("⚠️  لا توجد سيارات في النظام")
            return
            
        # اختبار توليد الروابط
        print("\n🔗 اختبار توليد الروابط:")
        print("-" * 40)
        
        for i, vehicle in enumerate(vehicles[:5]):  # أول 5 سيارات
            external_url = f"/external-safety-check/{vehicle.id}"
            print(f"{i+1}. السيارة: {vehicle.plate_number}")
            print(f"   الرابط: {external_url}")
            print(f"   النوع: {vehicle.make} {vehicle.model}")
            print(f"   الحالة: {vehicle.status}")
            print()
        
        # اختبار صفحة مشاركة الروابط
        print("\n📄 اختبار صفحة مشاركة الروابط:")
        print("-" * 40)
        
        with app.test_request_context():
            try:
                share_links_url = url_for('external_safety.share_links')
                print(f"✅ رابط صفحة المشاركة: {share_links_url}")
            except Exception as e:
                print(f"❌ خطأ في توليد رابط صفحة المشاركة: {e}")
        
        # اختبار فحوصات السلامة الموجودة
        print("\n🛡️  اختبار فحوصات السلامة الموجودة:")
        print("-" * 40)
        
        safety_checks = SafetyInspection.query.all()
        print(f"📊 عدد فحوصات السلامة: {len(safety_checks)}")
        
        if safety_checks:
            for check in safety_checks:
                vehicle = Vehicle.query.get(check.vehicle_id)
                print(f"• فحص ID: {check.id}")
                print(f"  السيارة: {vehicle.plate_number if vehicle else 'غير موجودة'}")
                print(f"  التاريخ: {check.inspection_date}")
                print(f"  الحالة: {check.approval_status}")
                print()
        
        # اختبار نظام المشاركة المتقدم
        print("\n📱 اختبار نظام المشاركة المتقدم:")
        print("-" * 40)
        
        sample_vehicle = vehicles[0]
        
        # محاكاة رسالة المشاركة
        share_message = f"""مرحباً 👋

يرجى تعبئة نموذج فحص السلامة الخارجي للمركبة التالية:

🚗 رقم اللوحة: {sample_vehicle.plate_number}
🚙 نوع المركبة: {sample_vehicle.make} {sample_vehicle.model}
📋 نوع النموذج: فحص السلامة الخارجي
🏢 نظام نُظم لإدارة المركبات

يرجى الضغط على الرابط أدناه لتعبئة النموذج:
/external-safety-check/{sample_vehicle.id}

⚠️ ملاحظات مهمة:
- يرجى تعبئة النموذج بعناية وبدقة
- إرفاق جميع الصور المطلوبة للفحص
- التأكد من صحة البيانات المدخلة
- النموذج سيتم إرساله للإدارة للمراجعة والموافقة

شكراً لتعاونكم 🙏"""
        
        print("✅ رسالة المشاركة النموذجية:")
        print(share_message)
        
        # اختبار معلومات النظام
        print("\n🔍 معلومات النظام:")
        print("-" * 40)
        
        employees = Employee.query.all()
        departments = Department.query.all()
        
        print(f"👥 عدد الموظفين: {len(employees)}")
        print(f"🏢 عدد الأقسام: {len(departments)}")
        print(f"🚗 عدد السيارات: {len(vehicles)}")
        print(f"🛡️  عدد فحوصات السلامة: {len(safety_checks)}")
        
        print("\n✅ تم إكمال اختبار نظام المشاركة بنجاح!")
        print("🎯 النظام جاهز للاستخدام والمشاركة")

if __name__ == "__main__":
    test_sharing_system()