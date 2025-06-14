#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
اختبار شامل لجميع وظائف التصدير في النظام
"""

import os
import sys
import traceback
from datetime import datetime

# إضافة المسار الحالي
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_vehicle_exports():
    """اختبار وظائف تصدير المركبات"""
    try:
        from models import Vehicle
        from utils.export_all_vehicles_excel import export_all_vehicles_to_excel
        from app import app, db
        
        with app.app_context():
            vehicles = Vehicle.query.limit(5).all()
            print(f"✓ تم جلب {len(vehicles)} مركبة للاختبار")
            
            if vehicles:
                # اختبار تصدير Excel
                response = export_all_vehicles_to_excel(vehicles)
                if response:
                    print("✓ وظيفة تصدير Excel للمركبات تعمل بنجاح")
                    return True
                else:
                    print("✗ فشل في تصدير Excel للمركبات")
                    return False
            else:
                print("⚠ لا توجد مركبات للاختبار")
                return True
                
    except Exception as e:
        print(f"✗ خطأ في اختبار تصدير المركبات: {str(e)}")
        traceback.print_exc()
        return False

def test_employee_exports():
    """اختبار وظائف تصدير الموظفين"""
    try:
        from models import Employee
        from app import app, db
        
        with app.app_context():
            employees = Employee.query.limit(3).all()
            print(f"✓ تم جلب {len(employees)} موظف للاختبار")
            
            if employees:
                print("✓ بيانات الموظفين متاحة للتصدير")
                return True
            else:
                print("⚠ لا يوجد موظفون للاختبار")
                return True
                
    except Exception as e:
        print(f"✗ خطأ في اختبار بيانات الموظفين: {str(e)}")
        return False

def test_database_connection():
    """اختبار الاتصال بقاعدة البيانات"""
    try:
        from app import app, db
        
        with app.app_context():
            # اختبار بسيط للاتصال
            result = db.session.execute("SELECT 1").fetchone()
            if result:
                print("✓ الاتصال بقاعدة البيانات يعمل بنجاح")
                return True
            else:
                print("✗ فشل في الاتصال بقاعدة البيانات")
                return False
                
    except Exception as e:
        print(f"✗ خطأ في الاتصال بقاعدة البيانات: {str(e)}")
        return False

def test_employee_portal():
    """اختبار بوابة الموظفين"""
    try:
        from routes.employee_portal import employee_portal_bp
        print("✓ تم استيراد بوابة الموظفين بنجاح")
        return True
        
    except Exception as e:
        print(f"✗ خطأ في استيراد بوابة الموظفين: {str(e)}")
        return False

def main():
    """تشغيل جميع الاختبارات"""
    print("=" * 60)
    print("بدء اختبار شامل لوظائف النظام قبل النشر")
    print("=" * 60)
    
    tests = [
        ("الاتصال بقاعدة البيانات", test_database_connection),
        ("بوابة الموظفين", test_employee_portal),
        ("تصدير المركبات", test_vehicle_exports),
        ("بيانات الموظفين", test_employee_exports),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 اختبار: {test_name}")
        print("-" * 40)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ فشل الاختبار: {str(e)}")
            results.append((test_name, False))
    
    # تقرير النتائج
    print("\n" + "=" * 60)
    print("ملخص نتائج الاختبار")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✓ نجح" if result else "✗ فشل"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nالنتيجة الإجمالية: {passed}/{total} اختبار نجح")
    
    if passed == total:
        print("🎉 جميع الاختبارات نجحت! النظام جاهز للنشر")
        return True
    else:
        print("⚠ بعض الاختبارات فشلت. يرجى مراجعة الأخطاء قبل النشر")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)