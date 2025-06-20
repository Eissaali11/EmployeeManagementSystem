"""
تقرير شامل للمعلومات الأساسية للموظف مع الصور
"""
import os
from io import BytesIO
from fpdf import FPDF
from PIL import Image
import arabic_reshaper
from bidi.algorithm import get_display
from datetime import datetime

class EmployeeComprehensiveBasicReportPDF(FPDF):
    """فئة إنشاء تقرير المعلومات الأساسية للموظف مع الصور"""
    
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        
    def header(self):
        """رأس الصفحة"""
        try:
            # عنوان النظام
            self.set_font('Arial', 'B', 20)
            self.set_text_color(41, 128, 185)
            self.cell(0, 10, 'NUZUM EMPLOYEE MANAGEMENT SYSTEM', 0, 1, 'C')
            
            # خط فاصل
            self.set_draw_color(41, 128, 185)
            self.line(20, 25, 190, 25)
            
            # عنوان التقرير
            self.set_font('Arial', 'B', 16)
            self.set_text_color(0, 0, 0)
            self.cell(0, 10, 'Employee Basic Information Report', 0, 1, 'C')
            self.ln(5)
        except:
            pass
            
    def footer(self):
        """تذييل الصفحة"""
        try:
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.set_text_color(128, 128, 128)
            self.cell(0, 10, f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M")} - Page {self.page_no()}', 0, 0, 'C')
        except:
            pass
            
    def add_section_title(self, title):
        """إضافة عنوان قسم"""
        try:
            self.ln(5)
            self.set_font('Arial', 'B', 14)
            self.set_fill_color(52, 152, 219)
            self.set_text_color(255, 255, 255)
            self.cell(0, 10, title, 0, 1, 'L', True)
            self.ln(3)
        except:
            pass
            
    def add_info_row(self, label, value, is_header=False):
        """إضافة صف معلومات"""
        try:
            if is_header:
                self.set_font('Arial', 'B', 12)
                self.set_fill_color(231, 246, 255)
            else:
                self.set_font('Arial', '', 10)
                self.set_fill_color(248, 249, 250)
                
            self.set_text_color(0, 0, 0)
            
            # تنظيف النصوص
            label_text = str(label) if label else 'Not specified'
            value_text = str(value) if value else 'Not specified'
            
            # إضافة الصف
            self.cell(60, 8, label_text, 1, 0, 'L', True)
            self.cell(120, 8, value_text, 1, 1, 'L')
        except Exception as e:
            print(f"Error adding info row: {e}")
            
    def add_image_with_title(self, image_path, title, x_position, y_position, width=50, height=60):
        """إضافة صورة مع عنوان"""
        try:
            # إضافة عنوان الصورة
            self.set_xy(x_position, y_position)
            self.set_font('Arial', 'B', 10)
            self.set_text_color(0, 0, 0)
            self.cell(width, 5, title, 0, 1, 'C')
            
            # التحقق من وجود الصورة
            if image_path and os.path.exists(image_path):
                try:
                    # إضافة الصورة
                    self.image(image_path, x_position, y_position + 7, width, height)
                    return True
                except Exception as e:
                    print(f"Error adding image {image_path}: {e}")
                    # إضافة مربع فارغ بدلاً من الصورة
                    self.rect(x_position, y_position + 7, width, height)
                    self.set_xy(x_position, y_position + height/2 + 5)
                    self.set_font('Arial', '', 8)
                    self.cell(width, 5, 'Image not available', 0, 1, 'C')
                    return False
            else:
                # إضافة مربع فارغ
                self.rect(x_position, y_position + 7, width, height)
                self.set_xy(x_position, y_position + height/2 + 5)
                self.set_font('Arial', '', 8)
                self.cell(width, 5, 'No image', 0, 1, 'C')
                return False
        except Exception as e:
            print(f"Error in add_image_with_title: {e}")
            return False


def generate_comprehensive_basic_report(employee_id):
    """إنشاء تقرير شامل للمعلومات الأساسية للموظف"""
    try:
        # استيراد داخلي لتجنب المشاكل الدائرية
        from flask import current_app
        with current_app.app_context():
            from sqlalchemy import text
            from app import db
            
            print(f"Starting comprehensive basic report for employee {employee_id}")
            
            # البحث عن الموظف باستخدام SQL مباشر
            employee_query = text("""
                SELECT e.*, d.name as department_name 
                FROM employees e 
                LEFT JOIN departments d ON e.department_id = d.id 
                WHERE e.id = :employee_id
            """)
            
            result = db.session.execute(employee_query, {'employee_id': employee_id}).fetchone()
            if not result:
                print(f"Employee {employee_id} not found")
                return None, "Employee not found"
            
            # تحويل النتيجة إلى dict
            employee = dict(result._mapping) if hasattr(result, '_mapping') else dict(zip(result.keys(), result))
            print(f"Found employee: {employee.get('name', 'Unknown')}")
        if not employee:
            print(f"Employee {employee_id} not found")
            return None, "Employee not found"
            
        print(f"Found employee: {employee.name}")
        
        # إنشاء PDF
        pdf = EmployeeComprehensiveBasicReportPDF()
        pdf.add_page()
        
        # عنوان التقرير الرئيسي
        pdf.set_font('Arial', 'B', 16)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 10, f'Basic Information Report for: {employee.name}', 0, 1, 'C')
        pdf.ln(10)
        
        # المعلومات الأساسية
        pdf.add_section_title('Basic Personal Information')
        pdf.add_info_row('Employee Name', employee.name, True)
        pdf.add_info_row('Employee ID', employee.employee_id)
        pdf.add_info_row('National ID', employee.national_id)
        pdf.add_info_row('Mobile Phone', employee.mobile)
        pdf.add_info_row('Email Address', employee.email or 'Not specified')
        pdf.add_info_row('Nationality', employee.nationality or 'Not specified')
        pdf.add_info_row('Contract Type', 'Saudi' if employee.contract_type == 'saudi' else 'Foreign' if employee.contract_type == 'foreign' else 'Not specified')
        
        # معلومات العمل
        pdf.add_section_title('Work Information')
        pdf.add_info_row('Job Title', employee.job_title)
        pdf.add_info_row('Department', employee.department.name if employee.department else 'Not assigned')
        pdf.add_info_row('Employment Status', employee.status.title())
        pdf.add_info_row('Join Date', employee.join_date.strftime('%Y-%m-%d') if employee.join_date else 'Not specified')
        pdf.add_info_row('Location', employee.location or 'Not specified')
        pdf.add_info_row('Project', employee.project or 'Not specified')
        pdf.add_info_row('Basic Salary', f"{employee.basic_salary:,.0f} SAR" if employee.basic_salary else 'Not specified')
        pdf.add_info_row('National Balance', 'Available' if employee.has_national_balance else 'Not available')
        
        # قسم الصور
        pdf.add_section_title('Employee Documents and Photos')
        pdf.ln(10)
        
        # تحديد مسارات الصور
        static_path = os.path.join(os.getcwd(), 'static')
        
        profile_image_path = None
        national_id_image_path = None
        license_image_path = None
        
        # البحث عن الصور في المجلد
        try:
            if employee.profile_image:
                if employee.profile_image.startswith('uploads/'):
                    profile_image_path = os.path.join(static_path, employee.profile_image)
                else:
                    profile_image_path = os.path.join(static_path, 'uploads', 'employees', employee.profile_image)
        except:
            pass
            
        try:
            if employee.national_id_image:
                if employee.national_id_image.startswith('uploads/'):
                    national_id_image_path = os.path.join(static_path, employee.national_id_image)
                else:
                    national_id_image_path = os.path.join(static_path, 'uploads', 'employees', employee.national_id_image)
        except:
            pass
            
        try:
            if employee.license_image:
                if employee.license_image.startswith('uploads/'):
                    license_image_path = os.path.join(static_path, employee.license_image)
                else:
                    license_image_path = os.path.join(static_path, 'uploads', 'employees', employee.license_image)
        except:
            pass
        
        # إضافة الصور في صف واحد
        current_y = pdf.get_y()
        
        # الصورة الشخصية
        pdf.add_image_with_title(profile_image_path, 'Profile Photo', 30, current_y, 45, 55)
        
        # صورة الهوية الوطنية
        pdf.add_image_with_title(national_id_image_path, 'National ID', 85, current_y, 45, 55)
        
        # صورة رخصة القيادة
        pdf.add_image_with_title(license_image_path, 'Driving License', 140, current_y, 45, 55)
        
        # الانتقال إلى السطر التالي بعد الصور
        pdf.set_y(current_y + 70)
        
        # معلومات إضافية
        pdf.add_section_title('Additional Information')
        pdf.add_info_row('Created Date', employee.created_at.strftime('%Y-%m-%d') if employee.created_at else 'Not specified')
        pdf.add_info_row('Last Updated', employee.updated_at.strftime('%Y-%m-%d') if employee.updated_at else 'Not specified')
        
        # إحصائيات سريعة
        pdf.add_section_title('Quick Statistics')
        
        # حساب الإحصائيات
        total_documents = len(employee.documents) if employee.documents else 0
        total_attendances = len(employee.attendances) if employee.attendances else 0
        total_salaries = len(employee.salaries) if employee.salaries else 0
        
        # حساب أيام الخدمة
        service_days = 0
        if employee.join_date:
            service_days = (datetime.now().date() - employee.join_date).days
        
        pdf.add_info_row('Documents Count', str(total_documents))
        pdf.add_info_row('Attendance Records', str(total_attendances))
        pdf.add_info_row('Salary Records', str(total_salaries))
        pdf.add_info_row('Service Days', str(service_days))
        
        # إنشاء buffer وإرجاع PDF
        try:
            pdf_buffer = pdf.output(dest='S').encode('latin1')
        except:
            pdf_buffer = bytes(pdf.output(dest='S'))
        print("PDF generated successfully")
        return pdf_buffer, None
        
    except Exception as e:
        import traceback
        error_msg = f"Error generating comprehensive basic report: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        return None, error_msg