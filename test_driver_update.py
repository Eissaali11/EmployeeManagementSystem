"""اختبار تحديث السائق بعد الموافقة على العمليات"""

import os
import sys

# إضافة المجلد الحالي للمسار
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Vehicle, VehicleHandover, OperationRequest, Employee
from utils.vehicle_driver_utils import update_vehicle_driver_approved, get_vehicle_current_employee_id_approved

def test_driver_update():
    with app.app_context():
        print("=== اختبار تحديث السائق بعد الموافقة ===\n")
        
        # اختيار سيارة للاختبار
        vehicle = Vehicle.query.first()
        if not vehicle:
            print("لا توجد سيارات في قاعدة البيانات")
            return
            
        print(f"السيارة المختارة: {vehicle.plate_number}")
        print(f"السائق الحالي في قاعدة البيانات: {vehicle.driver_name}")
        
        # البحث عن عمليات handover معلقة لهذه السيارة
        pending_operations = OperationRequest.query.filter_by(
            vehicle_id=vehicle.id,
            operation_type='handover',
            status='pending'
        ).all()
        
        print(f"\nعدد العمليات المعلقة: {len(pending_operations)}")
        
        # البحث عن عمليات معتمدة
        approved_operations = OperationRequest.query.filter_by(
            vehicle_id=vehicle.id,
            operation_type='handover',
            status='approved'
        ).all()
        
        print(f"عدد العمليات المعتمدة: {len(approved_operations)}")
        
        # عرض جميع سجلات التسليم للسيارة
        handover_records = VehicleHandover.query.filter_by(
            vehicle_id=vehicle.id
        ).order_by(VehicleHandover.handover_date.desc()).all()
        
        print(f"\nجميع سجلات التسليم/الاستلام ({len(handover_records)}):")
        for i, record in enumerate(handover_records):
            print(f"{i+1}. ID: {record.id}, النوع: {record.handover_type}, الاسم: {record.person_name}, التاريخ: {record.handover_date}")
        
        # اختبار الدالة المحسنة
        print(f"\n=== اختبار الدالة المحسنة ===")
        employee_id = get_vehicle_current_employee_id_approved(vehicle.id)
        print(f"معرف الموظف الحالي (دالة محسنة): {employee_id}")
        
        # تحديث السائق
        print(f"\n=== تجربة تحديث السائق ===")
        old_driver = vehicle.driver_name
        update_vehicle_driver_approved(vehicle.id)
        
        # إعادة قراءة السيارة من قاعدة البيانات
        db.session.refresh(vehicle)
        new_driver = vehicle.driver_name
        
        print(f"السائق قبل التحديث: {old_driver}")
        print(f"السائق بعد التحديث: {new_driver}")
        
        if old_driver != new_driver:
            print("✓ تم التحديث بنجاح")
        else:
            print("✗ لم يتم التحديث")

if __name__ == "__main__":
    test_driver_update()