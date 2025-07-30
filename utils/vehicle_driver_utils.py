"""وظائف مساعدة لإدارة السائقين المحسنة"""

from models import VehicleHandover, OperationRequest, Vehicle, Employee
from app import db


def get_vehicle_current_employee_id_approved(vehicle_id):
    """الحصول على معرف الموظف الحالي للسيارة باستخدام السجلات المعتمدة"""
    try:
        # استخدام نفس منطق الفلترة المستخدم في view
        approved_handover_ids = []
        approved_operations = OperationRequest.query.filter_by(
            vehicle_id=vehicle_id, 
            operation_type='handover',
            status='approved'
        ).all()
        
        for operation in approved_operations:
            approved_handover_ids.append(operation.related_record_id)
        
        all_handover_operations = OperationRequest.query.filter_by(
            vehicle_id=vehicle_id, 
            operation_type='handover'
        ).all()
        all_handover_operation_ids = [op.related_record_id for op in all_handover_operations]
        
        # جلب آخر سجل تسليم معتمد
        latest_delivery = VehicleHandover.query.filter(
            VehicleHandover.vehicle_id == vehicle_id,
            VehicleHandover.handover_type.in_(['delivery', 'تسليم', 'handover']),
            # إما أن يكون السجل معتمد، أو لا يوجد له operation request (سجل قديم)
            (VehicleHandover.id.in_(approved_handover_ids)) | 
            (~VehicleHandover.id.in_(all_handover_operation_ids))
        ).order_by(VehicleHandover.handover_date.desc()).first()

        if latest_delivery and latest_delivery.employee_id:
            return latest_delivery.employee_id
        return None
        
    except Exception as e:
        print(f"خطأ في الحصول على معرف الموظف الحالي: {e}")
        return None


def update_vehicle_driver_approved(vehicle_id):
    """تحديث اسم السائق في جدول السيارات بناءً على آخر سجل تسليم معتمد"""
    try:
        # جلب السجلات المعتمدة فقط مثلما نفعل في دالة view  
        
        # جلب operation IDs المعتمدة للتسليم والاستلام
        approved_handover_ids = []
        approved_operations = OperationRequest.query.filter_by(
            vehicle_id=vehicle_id, 
            operation_type='handover',
            status='approved'
        ).all()
        
        for operation in approved_operations:
            approved_handover_ids.append(operation.related_record_id)
        
        # جلب جميع operation requests للمركبة من نوع handover
        all_handover_operations = OperationRequest.query.filter_by(
            vehicle_id=vehicle_id, 
            operation_type='handover'
        ).all()
        all_handover_operation_ids = [op.related_record_id for op in all_handover_operations]
        
        # جلب سجلات التسليم المعتمدة فقط
        delivery_records = VehicleHandover.query.filter(
            VehicleHandover.vehicle_id == vehicle_id,
            VehicleHandover.handover_type.in_(['delivery', 'تسليم', 'handover']),
            # إما أن يكون السجل معتمد، أو لا يوجد له operation request (سجل قديم)
            (VehicleHandover.id.in_(approved_handover_ids)) | 
            (~VehicleHandover.id.in_(all_handover_operation_ids))
        ).order_by(VehicleHandover.handover_date.desc()).all()

        if delivery_records:
            # أخذ أحدث سجل تسليم (delivery) معتمد
            latest_delivery = delivery_records[0]

            # تحديد اسم السائق (إما من جدول الموظفين أو من اسم الشخص المدخل يدوياً)
            driver_name = None
            if latest_delivery.employee_id:
                employee = Employee.query.get(latest_delivery.employee_id)
                if employee:
                    driver_name = employee.name

            # إذا لم يكن هناك موظف معين، استخدم اسم الشخص المدخل يدوياً
            if not driver_name and latest_delivery.person_name:
                driver_name = latest_delivery.person_name

            # تحديث اسم السائق في جدول السيارات
            vehicle = Vehicle.query.get(vehicle_id)
            if vehicle:
                vehicle.driver_name = driver_name
                db.session.commit()
                print(f"تم تحديث السائق للسيارة {vehicle_id} إلى: {driver_name}")
        else:
            # إذا لم يكن هناك سجلات تسليم معتمدة، امسح اسم السائق
            vehicle = Vehicle.query.get(vehicle_id)
            if vehicle:
                vehicle.driver_name = None
                db.session.commit()
                print(f"تم مسح السائق للسيارة {vehicle_id}")

    except Exception as e:
        print(f"خطأ في تحديث اسم السائق: {e}")
        # لا نريد أن يؤثر هذا الخطأ على العملية الأساسية
        pass