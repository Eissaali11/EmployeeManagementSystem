#!/usr/bin/env python3
"""
اختبار نظام التصدير الجديد للسيارات مع التبويبات المنفصلة
"""

import sys
import os
sys.path.append('.')

from app import app, db
from models import Vehicle, VehicleWorkshop, VehicleRental, VehicleProject, VehicleHandover
from utils.vehicle_tabbed_export import create_vehicle_excel_with_tabs

def test_vehicle_export():
    """اختبار تصدير بيانات السيارة"""
    with app.app_context():
        try:
            # البحث عن سيارة للاختبار
            vehicle = Vehicle.query.first()
            if not vehicle:
                print("لا توجد سيارات في قاعدة البيانات")
                return
            
            print(f"اختبار تصدير السيارة: {vehicle.plate_number}")
            
            # جلب جميع البيانات المتعلقة بالسيارة
            workshop_records = VehicleWorkshop.query.filter_by(vehicle_id=vehicle.id).all()
            rental_records = VehicleRental.query.filter_by(vehicle_id=vehicle.id).all()
            project_records = VehicleProject.query.filter_by(vehicle_id=vehicle.id).all()
            handover_records = VehicleHandover.query.filter_by(vehicle_id=vehicle.id).all()
            
            print(f"سجلات الورشة: {len(workshop_records)}")
            print(f"سجلات الإيجار: {len(rental_records)}")
            print(f"سجلات المشاريع: {len(project_records)}")
            print(f"سجلات التسليم: {len(handover_records)}")
            
            # إنشاء ملف التصدير
            excel_buffer = create_vehicle_excel_with_tabs(
                vehicle,
                workshop_records=workshop_records,
                rental_records=rental_records,
                project_records=project_records,
                handover_records=handover_records
            )
            
            if excel_buffer:
                # حفظ الملف للاختبار
                test_file = 'test_vehicle_tabbed_export.xlsx'
                with open(test_file, 'wb') as f:
                    f.write(excel_buffer.getvalue())
                
                file_size = os.path.getsize(test_file)
                print(f"تم إنشاء الملف بنجاح: {test_file}")
                print(f"حجم الملف: {file_size} بايت")
                
                # التحقق من محتوى الملف
                import openpyxl
                wb = openpyxl.load_workbook(test_file)
                print(f"عدد التبويبات: {len(wb.worksheets)}")
                for sheet in wb.worksheets:
                    print(f"- تبويب: {sheet.title}")
                
                return True
            else:
                print("فشل في إنشاء ملف التصدير")
                return False
                
        except Exception as e:
            print(f"خطأ في الاختبار: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = test_vehicle_export()
    if success:
        print("✓ اختبار التصدير نجح")
    else:
        print("✗ اختبار التصدير فشل")