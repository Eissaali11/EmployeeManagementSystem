#!/usr/bin/env python3
"""
اختبار شامل لوظيفة تصدير Excel لنظام عمليات السيارة
"""

import requests
import os
from datetime import datetime

def test_export_functionality():
    """اختبار جميع أنواع التصدير مع الفلاتر المختلفة"""
    
    base_url = "http://localhost:5000/vehicle-operations/export"
    
    test_cases = [
        {
            'name': 'تصدير جميع العمليات',
            'params': {},
            'expected_file': 'all_operations.xlsx'
        },
        {
            'name': 'تصدير حسب السيارة (3220)',
            'params': {'vehicle_filter': '3220'},
            'expected_file': 'vehicle_3220.xlsx'
        },
        {
            'name': 'تصدير عمليات التسليم والاستلام فقط',
            'params': {'operation_type': 'handover'},
            'expected_file': 'handover_only.xlsx'
        },
        {
            'name': 'تصدير عمليات الورشة فقط',
            'params': {'operation_type': 'workshop'},
            'expected_file': 'workshop_only.xlsx'
        },
        {
            'name': 'تصدير فحوصات السلامة فقط',
            'params': {'operation_type': 'safety_check'},
            'expected_file': 'safety_only.xlsx'
        },
        {
            'name': 'تصدير حسب التاريخ (2025)',
            'params': {'date_from': '2025-01-01', 'date_to': '2025-12-31'},
            'expected_file': 'date_filtered_2025.xlsx'
        },
        {
            'name': 'تصدير مركب (السيارة والنوع)',
            'params': {'vehicle_filter': '3220', 'operation_type': 'handover'},
            'expected_file': 'combined_filter.xlsx'
        }
    ]
    
    print("🚗 بدء اختبار وظيفة تصدير Excel لنظام عمليات السيارة")
    print("=" * 60)
    
    results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 الاختبار {i}: {test_case['name']}")
        
        try:
            # إرسال الطلب
            response = requests.get(base_url, params=test_case['params'])
            
            # فحص النتيجة
            if response.status_code == 200:
                # تحقق من نوع المحتوى
                content_type = response.headers.get('Content-Type', '')
                if 'spreadsheet' in content_type or 'excel' in content_type:
                    file_size = len(response.content)
                    print(f"   ✅ نجح التصدير - حجم الملف: {file_size} بايت")
                    
                    # حفظ الملف للفحص
                    filename = f"test_{test_case['expected_file']}"
                    with open(filename, 'wb') as f:
                        f.write(response.content)
                    
                    results.append({
                        'test': test_case['name'],
                        'status': 'نجح',
                        'size': file_size,
                        'params': test_case['params']
                    })
                else:
                    print(f"   ❌ فشل - المحتوى ليس Excel: {content_type}")
                    results.append({
                        'test': test_case['name'],
                        'status': 'فشل - نوع محتوى خاطئ',
                        'content_type': content_type,
                        'params': test_case['params']
                    })
            else:
                print(f"   ❌ فشل HTTP - كود الاستجابة: {response.status_code}")
                results.append({
                    'test': test_case['name'],
                    'status': f'فشل HTTP {response.status_code}',
                    'params': test_case['params']
                })
                
        except Exception as e:
            print(f"   ❌ خطأ في الطلب: {str(e)}")
            results.append({
                'test': test_case['name'],
                'status': f'خطأ: {str(e)}',
                'params': test_case['params']
            })
    
    # تلخيص النتائج
    print("\n" + "=" * 60)
    print("📊 ملخص نتائج الاختبار:")
    print("=" * 60)
    
    successful_tests = [r for r in results if r['status'] == 'نجح']
    failed_tests = [r for r in results if r['status'] != 'نجح']
    
    print(f"✅ الاختبارات الناجحة: {len(successful_tests)}/{len(results)}")
    print(f"❌ الاختبارات الفاشلة: {len(failed_tests)}/{len(results)}")
    
    if successful_tests:
        print("\n🎉 الاختبارات الناجحة:")
        total_size = 0
        for result in successful_tests:
            size_kb = result['size'] / 1024
            total_size += result['size']
            print(f"   • {result['test']}: {size_kb:.1f} KB")
        
        print(f"\n📈 إجمالي حجم الملفات المُصدرة: {total_size/1024:.1f} KB")
    
    if failed_tests:
        print("\n⚠️ الاختبارات الفاشلة:")
        for result in failed_tests:
            print(f"   • {result['test']}: {result['status']}")
    
    # توصيات
    print("\n" + "=" * 60)
    print("💡 التوصيات:")
    if len(successful_tests) == len(results):
        print("🌟 ممتاز! جميع اختبارات التصدير نجحت بشكل كامل")
        print("✨ النظام جاهز للاستخدام في الإنتاج")
    elif len(successful_tests) > len(failed_tests):
        print("👍 معظم الاختبارات نجحت - قم بمراجعة الاختبارات الفاشلة")
    else:
        print("⚠️ عدد كبير من الاختبارات فشل - يحتاج مراجعة شاملة")
    
    return results

if __name__ == "__main__":
    test_export_functionality()