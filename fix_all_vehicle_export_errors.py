"""
إصلاح شامل لجميع أخطاء التصدير في ملف routes/vehicles.py
"""
import re

def fix_vehicle_export_errors():
    """إصلاح جميع أخطاء حقول التصدير"""
    
    with open('routes/vehicles.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # إصلاح حقول VehicleProject
    content = content.replace("record.project_description", "record.notes")
    content = content.replace("record.project_location", "record.location")
    content = content.replace("record.project_manager", "record.manager_name")
    
    # إصلاح حقول VehicleHandover المفقودة
    content = content.replace("handover.employee_name", "handover.person_name")
    content = content.replace("handover.odometer_reading", "handover.mileage")
    
    # إصلاح حقول VehiclePeriodicInspection المفقودة
    content = content.replace("inspection.certificate_number", "inspection.inspection_number")
    content = content.replace("inspection.authority", "inspection.inspection_center")
    
    # إصلاح حقول VehicleSafetyCheck المفقودة
    content = content.replace("safety_check.tire_condition", "safety_check.status")
    content = content.replace("safety_check.brake_condition", "safety_check.issues_found")
    content = content.replace("safety_check.checked_by", "safety_check.supervisor_name")
    
    # حفظ الملف المحدث
    with open('routes/vehicles.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("تم إصلاح جميع أخطاء التصدير بنجاح!")

if __name__ == "__main__":
    fix_vehicle_export_errors()