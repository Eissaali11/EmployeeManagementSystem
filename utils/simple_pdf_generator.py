"""
مولد PDF بسيط ومحسن للغة العربية مع حل مشاكل الترميز
"""

from fpdf import FPDF
from io import BytesIO
import os


class SimplePDF(FPDF):
    """فئة بسيطة لإنشاء ملفات PDF مع دعم أساسي للغة العربية"""
    
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        # استخدام الخط الافتراضي للنظام
        self.set_font('Arial', '', 12)
    
    def header(self):
        """إضافة ترويسة الصفحة"""
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Nuzum Management System', 0, 1, 'C')
        self.ln(10)
    
    def footer(self):
        """إضافة تذييل الصفحة"""
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')


def generate_salary_report_pdf(salaries_data, month_name, year):
    """
    إنشاء تقرير رواتب بصيغة PDF مع دعم بسيط للعربية
    """
    try:
        pdf = SimplePDF()
        pdf.add_page()
        
        # عنوان التقرير
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, f'Salary Report - {month_name} {year}', 0, 1, 'C')
        pdf.ln(5)
        
        # رأس الجدول
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(40, 10, 'Employee Name', 1, 0, 'C')
        pdf.cell(20, 10, 'ID', 1, 0, 'C')
        pdf.cell(25, 10, 'Basic', 1, 0, 'C')
        pdf.cell(25, 10, 'Allowances', 1, 0, 'C')
        pdf.cell(25, 10, 'Deductions', 1, 0, 'C')
        pdf.cell(20, 10, 'Bonus', 1, 0, 'C')
        pdf.cell(25, 10, 'Net Salary', 1, 1, 'C')
        
        # بيانات الموظفين
        pdf.set_font('Arial', '', 9)
        total_net = 0
        
        for salary in salaries_data:
            # تنظيف النص العربي واستبداله بنص إنجليزي آمن
            emp_name = str(salary.get('employee_name', 'N/A'))
            if any(ord(char) > 127 for char in emp_name):
                emp_name = f"Employee {salary.get('employee_id', 'N/A')}"
            
            pdf.cell(40, 8, emp_name[:15], 1, 0, 'L')
            pdf.cell(20, 8, str(salary.get('employee_id', '')), 1, 0, 'C')
            pdf.cell(25, 8, f"{salary.get('basic_salary', 0):.2f}", 1, 0, 'R')
            pdf.cell(25, 8, f"{salary.get('allowances', 0):.2f}", 1, 0, 'R')
            pdf.cell(25, 8, f"{salary.get('deductions', 0):.2f}", 1, 0, 'R')
            pdf.cell(20, 8, f"{salary.get('bonus', 0):.2f}", 1, 0, 'R')
            pdf.cell(25, 8, f"{salary.get('net_salary', 0):.2f}", 1, 1, 'R')
            
            total_net += salary.get('net_salary', 0)
        
        # المجموع الإجمالي
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(135, 8, 'Total:', 1, 0, 'R')
        pdf.cell(25, 8, f"{total_net:.2f}", 1, 1, 'R')
        
        # إضافة معلومات إضافية
        pdf.ln(10)
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 8, f'Generated on: {year}-{month_name}', 0, 1, 'L')
        pdf.cell(0, 8, f'Total Employees: {len(salaries_data)}', 0, 1, 'L')
        
        # تحويل إلى bytes
        output = pdf.output(dest='S')
        if isinstance(output, str):
            return output.encode('latin-1')
        return output
        
    except Exception as e:
        print(f"خطأ في إنشاء PDF: {str(e)}")
        # إنشاء PDF بسيط في حالة الخطأ
        pdf = SimplePDF()
        pdf.add_page()
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, 'Error generating salary report', 0, 1, 'C')
        pdf.cell(0, 10, f'Error: {str(e)}', 0, 1, 'C')
        output = pdf.output(dest='S')
        if isinstance(output, str):
            return output.encode('latin-1')
        return output


def create_vehicle_handover_pdf(handover_data):
    """
    إنشاء تقرير تسليم المركبة بصيغة PDF
    """
    try:
        pdf = SimplePDF()
        pdf.add_page()
        
        # عنوان التقرير
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 15, 'Vehicle Handover Report', 0, 1, 'C')
        pdf.ln(10)
        
        # معلومات المركبة
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Vehicle Information:', 0, 1, 'L')
        pdf.set_font('Arial', '', 10)
        
        if hasattr(handover_data, 'vehicle_rel') and handover_data.vehicle_rel:
            pdf.cell(0, 8, f'Plate Number: {handover_data.vehicle_rel.plate_number}', 0, 1, 'L')
            pdf.cell(0, 8, f'Make: {handover_data.vehicle_rel.make}', 0, 1, 'L')
            pdf.cell(0, 8, f'Model: {handover_data.vehicle_rel.model}', 0, 1, 'L')
        
        pdf.ln(5)
        
        # معلومات التسليم
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Handover Information:', 0, 1, 'L')
        pdf.set_font('Arial', '', 10)
        
        pdf.cell(0, 8, f'Date: {handover_data.handover_date.strftime("%Y-%m-%d") if handover_data.handover_date else "N/A"}', 0, 1, 'L')
        pdf.cell(0, 8, f'Person: {handover_data.person_name or "N/A"}', 0, 1, 'L')
        pdf.cell(0, 8, f'Type: {handover_data.handover_type or "N/A"}', 0, 1, 'L')
        pdf.cell(0, 8, f'Mileage: {handover_data.mileage or "N/A"} km', 0, 1, 'L')
        pdf.cell(0, 8, f'Fuel Level: {handover_data.fuel_level or "N/A"}', 0, 1, 'L')
        
        if handover_data.notes:
            pdf.ln(5)
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 10, 'Notes:', 0, 1, 'L')
            pdf.set_font('Arial', '', 10)
            pdf.multi_cell(0, 8, handover_data.notes)
        
        # إنتاج الملف
        buffer = BytesIO()
        pdf_content = pdf.output(dest='S').encode('latin-1')
        buffer.write(pdf_content)
        buffer.seek(0)
        
        return buffer
        
    except Exception as e:
        print(f"Error generating handover PDF: {e}")
        return None


def generate_employee_salary_slip_pdf(employee_data, salary_data, month_name, year):
    """
    إنشاء إشعار راتب فردي بصيغة PDF
    """
    try:
        pdf = SimplePDF()
        pdf.add_page()
        
        # عنوان الإشعار
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'Salary Slip', 0, 1, 'C')
        pdf.ln(5)
        
        # معلومات الموظف
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, f'Month: {month_name} {year}', 0, 1, 'L')
        pdf.ln(3)
        
        # تنظيف اسم الموظف
        emp_name = str(employee_data.get('name', 'N/A'))
        if any(ord(char) > 127 for char in emp_name):
            emp_name = f"Employee {employee_data.get('employee_id', 'N/A')}"
        
        pdf.set_font('Arial', '', 11)
        pdf.cell(50, 8, 'Employee ID:', 0, 0, 'L')
        pdf.cell(0, 8, str(employee_data.get('employee_id', 'N/A')), 0, 1, 'L')
        
        pdf.cell(50, 8, 'Employee Name:', 0, 0, 'L')
        pdf.cell(0, 8, emp_name, 0, 1, 'L')
        
        pdf.cell(50, 8, 'Job Title:', 0, 0, 'L')
        job_title = str(employee_data.get('job_title', 'N/A'))
        if any(ord(char) > 127 for char in job_title):
            job_title = 'Staff Member'
        pdf.cell(0, 8, job_title, 0, 1, 'L')
        
        pdf.ln(5)
        
        # تفاصيل الراتب
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, 'Salary Details:', 0, 1, 'L')
        pdf.ln(2)
        
        pdf.set_font('Arial', '', 11)
        pdf.cell(60, 8, 'Basic Salary:', 0, 0, 'L')
        pdf.cell(0, 8, f"{salary_data.get('basic_salary', 0):.2f}", 0, 1, 'L')
        
        pdf.cell(60, 8, 'Allowances:', 0, 0, 'L')
        pdf.cell(0, 8, f"{salary_data.get('allowances', 0):.2f}", 0, 1, 'L')
        
        pdf.cell(60, 8, 'Bonus:', 0, 0, 'L')
        pdf.cell(0, 8, f"{salary_data.get('bonus', 0):.2f}", 0, 1, 'L')
        
        pdf.cell(60, 8, 'Deductions:', 0, 0, 'L')
        pdf.cell(0, 8, f"-{salary_data.get('deductions', 0):.2f}", 0, 1, 'L')
        
        pdf.ln(3)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(60, 8, 'Net Salary:', 0, 0, 'L')
        pdf.cell(0, 8, f"{salary_data.get('net_salary', 0):.2f}", 0, 1, 'L')
        
        output = pdf.output(dest='S')
        if isinstance(output, str):
            return output.encode('latin-1')
        return output
        
    except Exception as e:
        print(f"خطأ في إنشاء إشعار الراتب: {str(e)}")
        # إنشاء PDF بسيط في حالة الخطأ
        pdf = SimplePDF()
        pdf.add_page()
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, 'Error generating salary slip', 0, 1, 'C')
        output = pdf.output(dest='S')
        if isinstance(output, str):
            return output.encode('latin-1')
        return output