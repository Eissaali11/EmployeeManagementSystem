"""
تقرير بسيط للموظف - نسخة محسنة بدون أخطاء
"""
import os
from fpdf import FPDF
from models import Employee, VehicleHandover


class SimpleEmployeeReport(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Employee Basic Report - نظم', 0, 1, 'C')
        self.ln(10)
        
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
        
    def add_info_line(self, label, value):
        self.set_font('Arial', 'B', 12)
        self.cell(50, 8, f'{label}:', 0, 0, 'L')
        self.set_font('Arial', '', 12)
        self.cell(0, 8, str(value) if value else 'Not specified', 0, 1, 'L')


def generate_simple_employee_report(employee_id):
    """إنشاء تقرير بسيط للموظف"""
    try:
        # البحث عن الموظف
        employee = Employee.query.get(employee_id)
        if not employee:
            return None, "Employee not found"
            
        pdf = SimpleEmployeeReport()
        pdf.add_page()
        
        # المعلومات الأساسية
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Basic Information', 0, 1, 'L')
        pdf.ln(5)
        
        pdf.add_info_line('Name', employee.name)
        pdf.add_info_line('Employee ID', employee.employee_id)
        pdf.add_info_line('Mobile', employee.mobile)
        pdf.add_info_line('Email', employee.email)
        pdf.add_info_line('National ID', employee.national_id)
        pdf.add_info_line('Job Title', employee.job_title)
        pdf.add_info_line('Department', employee.department.name if employee.department else 'Not assigned')
        pdf.add_info_line('Status', employee.status)
        pdf.add_info_line('Join Date', employee.join_date.strftime('%Y-%m-%d') if employee.join_date else 'Not specified')
        pdf.add_info_line('Basic Salary', f'{employee.basic_salary:,.2f} SAR' if employee.basic_salary else 'Not specified')
        
        # معلومات إضافية
        pdf.ln(10)
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Additional Information', 0, 1, 'L')
        pdf.ln(5)
        
        pdf.add_info_line('Contract Type', employee.contract_type)
        pdf.add_info_line('Location', employee.location)
        pdf.add_info_line('Project', employee.project)
        pdf.add_info_line('National Balance', 'Yes' if employee.has_national_balance else 'No')
        
        # سجلات المركبات
        vehicle_handovers = VehicleHandover.query.filter_by(employee_id=employee_id).all()
        if vehicle_handovers:
            pdf.ln(10)
            pdf.set_font('Arial', 'B', 14)
            pdf.cell(0, 10, 'Vehicle Records', 0, 1, 'L')
            pdf.ln(5)
            
            for handover in vehicle_handovers:
                vehicle_info = f"Plate: {handover.vehicle.plate_number if handover.vehicle else 'N/A'}"
                vehicle_info += f" | Type: {handover.handover_type}"
                vehicle_info += f" | Date: {handover.handover_date.strftime('%Y-%m-%d')}"
                vehicle_info += f" | Person: {handover.person_name}"
                if handover.mileage:
                    vehicle_info += f" | Mileage: {handover.mileage} km"
                
                pdf.set_font('Arial', '', 10)
                pdf.cell(0, 6, vehicle_info, 0, 1, 'L')
        
        # إنشاء PDF
        pdf_output = pdf.output(dest='S')
        return pdf_output, None
        
    except Exception as e:
        print(f"خطأ في إنشاء التقرير البسيط: {str(e)}")
        return None, str(e)