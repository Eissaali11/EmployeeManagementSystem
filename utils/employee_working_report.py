"""
تقرير موظف بسيط وفعال - يعمل بدون أخطاء
"""
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
from models import Employee, VehicleHandover


def generate_working_employee_report(employee_id):
    """إنشاء تقرير موظف باستخدام ReportLab"""
    try:
        # البحث عن الموظف
        employee = Employee.query.get(employee_id)
        if not employee:
            return None, "Employee not found"
            
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter
        
        # عنوان التقرير
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, height - 50, "Employee Basic Report - Nuzum System")
        
        # خط فاصل
        c.line(50, height - 70, width - 50, height - 70)
        
        y_position = height - 100
        
        # دالة تنظيف النص
        def clean_text(text):
            if not text:
                return "Not specified"
            try:
                # إزالة الأحرف غير ASCII
                cleaned = str(text).encode('ascii', 'ignore').decode('ascii').strip()
                return cleaned if cleaned else "Not specified"
            except:
                return "Not specified"
        
        # المعلومات الأساسية
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y_position, "Basic Information:")
        y_position -= 30
        
        c.setFont("Helvetica", 12)
        info_data = [
            ("Name:", clean_text(employee.name)),
            ("Employee ID:", clean_text(employee.employee_id)),
            ("Mobile:", clean_text(employee.mobile)),
            ("Email:", clean_text(employee.email)),
            ("National ID:", clean_text(employee.national_id)),
            ("Job Title:", clean_text(employee.job_title)),
            ("Department:", clean_text(employee.department.name) if employee.department else "Not assigned"),
            ("Status:", clean_text(employee.status)),
            ("Join Date:", employee.join_date.strftime('%Y-%m-%d') if employee.join_date else "Not specified"),
            ("Basic Salary:", f"{employee.basic_salary:,.2f} SAR" if employee.basic_salary else "Not specified"),
        ]
        
        for label, value in info_data:
            c.drawString(50, y_position, f"{label} {value}")
            y_position -= 20
        
        # معلومات إضافية
        y_position -= 20
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y_position, "Additional Information:")
        y_position -= 30
        
        c.setFont("Helvetica", 12)
        additional_data = [
            ("Contract Type:", clean_text(employee.contract_type)),
            ("Location:", clean_text(employee.location)),
            ("Project:", clean_text(employee.project)),
            ("National Balance:", "Yes" if employee.has_national_balance else "No"),
        ]
        
        for label, value in additional_data:
            c.drawString(50, y_position, f"{label} {value}")
            y_position -= 20
        
        # سجلات المركبات
        vehicle_handovers = VehicleHandover.query.filter_by(employee_id=employee_id).all()
        if vehicle_handovers:
            y_position -= 20
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, y_position, "Vehicle Records:")
            y_position -= 30
            
            c.setFont("Helvetica", 10)
            for handover in vehicle_handovers:
                if y_position < 100:  # صفحة جديدة إذا اقترب من النهاية
                    c.showPage()
                    y_position = height - 50
                
                vehicle_info = f"Plate: {clean_text(handover.vehicle.plate_number) if handover.vehicle else 'N/A'}"
                vehicle_info += f" | Type: {clean_text(handover.handover_type)}"
                vehicle_info += f" | Date: {handover.handover_date.strftime('%Y-%m-%d')}"
                vehicle_info += f" | Person: {clean_text(handover.person_name)}"
                if handover.mileage:
                    vehicle_info += f" | Mileage: {handover.mileage} km"
                
                c.drawString(50, y_position, vehicle_info)
                y_position -= 15
        
        # تذييل الصفحة
        c.setFont("Helvetica", 8)
        c.drawString(50, 30, f"Generated on: {employee.created_at.strftime('%Y-%m-%d %H:%M') if employee.created_at else 'Unknown'}")
        c.drawString(width - 150, 30, "Nuzum Management System")
        
        c.save()
        buffer.seek(0)
        return buffer.getvalue(), None
        
    except Exception as e:
        print(f"خطأ في إنشاء التقرير: {str(e)}")
        return None, str(e)