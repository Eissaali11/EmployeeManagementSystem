"""
تقرير موظف بسيط ومضمون العمل
"""
import os
from flask import Response
from models import Employee, VehicleHandover


def generate_minimal_employee_report(employee_id):
    """إنشاء تقرير نصي بسيط للموظف"""
    try:
        # البحث عن الموظف
        employee = Employee.query.get(employee_id)
        if not employee:
            return None, "Employee not found"
        
        # دالة تنظيف النص
        def clean_text(text):
            if not text:
                return "Not specified"
            try:
                cleaned = str(text).encode('ascii', 'ignore').decode('ascii').strip()
                return cleaned if cleaned else "Not specified"
            except:
                return "Not specified"
        
        # إنشاء محتوى التقرير النصي
        report_content = f"""
EMPLOYEE BASIC REPORT - NUZUM SYSTEM
=====================================

BASIC INFORMATION:
------------------
Name: {clean_text(employee.name)}
Employee ID: {clean_text(employee.employee_id)}
Mobile: {clean_text(employee.mobile)}
Email: {clean_text(employee.email)}
National ID: {clean_text(employee.national_id)}
Job Title: {clean_text(employee.job_title)}
Department: {clean_text(employee.department.name) if employee.department else 'Not assigned'}
Status: {clean_text(employee.status)}
Join Date: {employee.join_date.strftime('%Y-%m-%d') if employee.join_date else 'Not specified'}
Basic Salary: {f'{employee.basic_salary:,.2f} SAR' if employee.basic_salary else 'Not specified'}

ADDITIONAL INFORMATION:
-----------------------
Contract Type: {clean_text(employee.contract_type)}
Location: {clean_text(employee.location)}
Project: {clean_text(employee.project)}
National Balance: {'Yes' if employee.has_national_balance else 'No'}

VEHICLE RECORDS:
----------------
"""
        
        # إضافة سجلات المركبات
        vehicle_handovers = VehicleHandover.query.filter_by(employee_id=employee_id).all()
        if vehicle_handovers:
            for handover in vehicle_handovers:
                vehicle_info = f"Plate: {clean_text(handover.vehicle.plate_number) if handover.vehicle else 'N/A'}"
                vehicle_info += f" | Type: {clean_text(handover.handover_type)}"
                vehicle_info += f" | Date: {handover.handover_date.strftime('%Y-%m-%d')}"
                vehicle_info += f" | Person: {clean_text(handover.person_name)}"
                if handover.mileage:
                    vehicle_info += f" | Mileage: {handover.mileage} km"
                
                report_content += f"{vehicle_info}\n"
        else:
            report_content += "No vehicle records found.\n"
        
        report_content += f"""
=====================================
Generated: {employee.created_at.strftime('%Y-%m-%d %H:%M') if employee.created_at else 'Unknown'}
System: Nuzum Management System
=====================================
"""
        
        return report_content.encode('utf-8'), None
        
    except Exception as e:
        print(f"خطأ في إنشاء التقرير النصي: {str(e)}")
        return None, str(e)