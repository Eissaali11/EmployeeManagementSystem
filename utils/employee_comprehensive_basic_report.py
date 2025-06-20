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
            self.cell(0, 10, 'نظام نُظم لإدارة الموظفين', 0, 1, 'C')
            
            # خط فاصل
            self.set_draw_color(41, 128, 185)
            self.line(20, 25, 190, 25)
            
            # عنوان التقرير
            self.set_font('Arial', 'B', 16)
            self.set_text_color(0, 0, 0)
            self.cell(0, 10, 'تقرير المعلومات الأساسية للموظف', 0, 1, 'C')
            self.ln(5)
        except:
            pass
            
    def footer(self):
        """تذييل الصفحة"""
        try:
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            self.set_text_color(128, 128, 128)
            self.cell(0, 10, f'تم الإنتاج في: {datetime.now().strftime("%Y-%m-%d %H:%M")} - صفحة {self.page_no()}', 0, 0, 'C')
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
            
            # تنظيف النصوص وتحويلها للإنجليزية إذا لزم الأمر
            def clean_text(text):
                if not text:
                    return 'Not specified'
                try:
                    # محاولة تشفير النص بـ latin-1
                    str(text).encode('latin-1')
                    return str(text)
                except UnicodeEncodeError:
                    # إذا فشل التشفير، استخدم النص الإنجليزي المكافئ
                    arabic_to_english = {
                        'اسم الموظف': 'Employee Name',
                        'رقم الموظف': 'Employee ID',
                        'رقم الهوية الوطنية': 'National ID',
                        'رقم الهاتف المحمول': 'Mobile Phone',
                        'عنوان البريد الإلكتروني': 'Email Address',
                        'الجنسية': 'Nationality',
                        'نوع العقد': 'Contract Type',
                        'المسمى الوظيفي': 'Job Title',
                        'القسم': 'Department',
                        'حالة التوظيف': 'Employment Status',
                        'تاريخ الانضمام': 'Join Date',
                        'الموقع': 'Location',
                        'المشروع': 'Project',
                        'الراتب الأساسي': 'Basic Salary',
                        'الرصيد الوطني': 'National Balance',
                        'تاريخ الإنشاء': 'Created Date',
                        'آخر تحديث': 'Last Updated',
                        'عدد الوثائق': 'Documents Count',
                        'سجلات الحضور': 'Attendance Records',
                        'سجلات الراتب': 'Salary Records',
                        'أيام الخدمة': 'Service Days',
                        'غير محدد': 'Not specified',
                        'غير محددة': 'Not specified',
                        'سعودي': 'Saudi',
                        'وافد': 'Foreign',
                        'نشط': 'Active',
                        'غير نشط': 'Inactive',
                        'في إجازة': 'On Leave',
                        'متوفر': 'Available',
                        'غير متوفر': 'Not available'
                    }
                    return arabic_to_english.get(str(text), str(text).encode('ascii', 'ignore').decode('ascii'))
            
            label_text = clean_text(label)
            value_text = clean_text(value)
            
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
                FROM employee e 
                LEFT JOIN department d ON e.department_id = d.id 
                WHERE e.id = :employee_id
            """)
            
            result = db.session.execute(employee_query, {'employee_id': employee_id}).fetchone()
            if not result:
                print(f"Employee {employee_id} not found")
                return None, "Employee not found"
            
            # تحويل النتيجة إلى dict
            employee = dict(result._mapping) if hasattr(result, '_mapping') else dict(zip(result.keys(), result))
            print(f"Found employee: {employee.get('name', 'Unknown')}")
            
            # إنشاء PDF
            pdf = EmployeeComprehensiveBasicReportPDF()
            pdf.add_page()
            
            # عنوان التقرير الرئيسي
            pdf.set_font('Arial', 'B', 16)
            pdf.set_text_color(0, 0, 0)
            pdf.cell(0, 10, f'تقرير المعلومات الأساسية للموظف: {employee.get("name", "غير محدد")}', 0, 1, 'C')
            pdf.ln(10)
            
            # المعلومات الأساسية
            pdf.add_section_title('المعلومات الشخصية الأساسية')
            pdf.add_info_row('اسم الموظف', employee.get('name', 'غير محدد'), True)
            pdf.add_info_row('رقم الموظف', employee.get('employee_id', 'غير محدد'))
            pdf.add_info_row('رقم الهوية الوطنية', employee.get('national_id', 'غير محدد'))
            pdf.add_info_row('رقم الهاتف المحمول', employee.get('mobile', 'غير محدد'))
            pdf.add_info_row('عنوان البريد الإلكتروني', employee.get('email', 'غير محدد'))
            pdf.add_info_row('الجنسية', employee.get('nationality', 'غير محددة'))
            contract_type = employee.get('contract_type', '')
            contract_display = 'سعودي' if contract_type == 'saudi' else 'وافد' if contract_type == 'foreign' else 'غير محدد'
            pdf.add_info_row('نوع العقد', contract_display)
            
            # معلومات العمل
            pdf.add_section_title('معلومات العمل')
            pdf.add_info_row('المسمى الوظيفي', employee.get('job_title', 'غير محدد'))
            pdf.add_info_row('القسم', employee.get('department_name', 'غير محدد'))
            status = employee.get('status', 'unknown')
            status_display = 'نشط' if status == 'active' else 'غير نشط' if status == 'inactive' else 'في إجازة' if status == 'on_leave' else 'غير محدد'
            pdf.add_info_row('حالة التوظيف', status_display)
            
            join_date = employee.get('join_date')
            join_date_str = join_date.strftime('%Y-%m-%d') if join_date else 'غير محدد'
            pdf.add_info_row('تاريخ الانضمام', join_date_str)
            
            pdf.add_info_row('الموقع', employee.get('location', 'غير محدد'))
            pdf.add_info_row('المشروع', employee.get('project', 'غير محدد'))
            
            basic_salary = employee.get('basic_salary')
            salary_str = f"{basic_salary:,.0f} ريال سعودي" if basic_salary else 'غير محدد'
            pdf.add_info_row('الراتب الأساسي', salary_str)
            
            has_balance = employee.get('has_national_balance', False)
            pdf.add_info_row('الرصيد الوطني', 'متوفر' if has_balance else 'غير متوفر')
        
            # قسم الصور
            pdf.add_section_title('وثائق وصور الموظف')
            pdf.ln(10)
            
            # تحديد مسارات الصور
            static_path = os.path.join(os.getcwd(), 'static')
            
            profile_image_path = None
            national_id_image_path = None
            license_image_path = None
            
            # البحث عن الصور في المجلد
            try:
                profile_image = employee.get('profile_image')
                if profile_image:
                    if profile_image.startswith('uploads/'):
                        profile_image_path = os.path.join(static_path, profile_image)
                    else:
                        profile_image_path = os.path.join(static_path, 'uploads', 'employees', profile_image)
            except:
                pass
                
            try:
                national_id_image = employee.get('national_id_image')
                if national_id_image:
                    if national_id_image.startswith('uploads/'):
                        national_id_image_path = os.path.join(static_path, national_id_image)
                    else:
                        national_id_image_path = os.path.join(static_path, 'uploads', 'employees', national_id_image)
            except:
                pass
                
            try:
                license_image = employee.get('license_image')
                if license_image:
                    if license_image.startswith('uploads/'):
                        license_image_path = os.path.join(static_path, license_image)
                    else:
                        license_image_path = os.path.join(static_path, 'uploads', 'employees', license_image)
            except:
                pass
            
            # إضافة الصور في صف واحد
            current_y = pdf.get_y()
            
            # الصورة الشخصية
            pdf.add_image_with_title(profile_image_path, 'الصورة الشخصية', 30, current_y, 45, 55)
            
            # صورة الهوية الوطنية
            pdf.add_image_with_title(national_id_image_path, 'صورة الهوية الوطنية', 85, current_y, 45, 55)
            
            # صورة رخصة القيادة
            pdf.add_image_with_title(license_image_path, 'صورة رخصة القيادة', 140, current_y, 45, 55)
            
            # الانتقال إلى السطر التالي بعد الصور
            pdf.set_y(current_y + 70)
            
            # معلومات إضافية
            pdf.add_section_title('معلومات إضافية')
            
            created_at = employee.get('created_at')
            created_str = created_at.strftime('%Y-%m-%d') if created_at else 'غير محدد'
            pdf.add_info_row('تاريخ الإنشاء', created_str)
            
            updated_at = employee.get('updated_at')
            updated_str = updated_at.strftime('%Y-%m-%d') if updated_at else 'غير محدد'
            pdf.add_info_row('آخر تحديث', updated_str)
            
            # إحصائيات سريعة - سنستخدم استعلامات منفصلة
            pdf.add_section_title('إحصائيات سريعة')
            
            # حساب الإحصائيات من قاعدة البيانات
            try:
                # حساب عدد الوثائق
                documents_query = text("SELECT COUNT(*) as count FROM document WHERE employee_id = :emp_id")
                docs_result = db.session.execute(documents_query, {'emp_id': employee_id}).fetchone()
                total_documents = docs_result[0] if docs_result else 0
                
                # حساب عدد سجلات الحضور
                attendance_query = text("SELECT COUNT(*) as count FROM attendance WHERE employee_id = :emp_id")
                att_result = db.session.execute(attendance_query, {'emp_id': employee_id}).fetchone()
                total_attendances = att_result[0] if att_result else 0
                
                # حساب عدد سجلات الراتب
                salary_query = text("SELECT COUNT(*) as count FROM salary WHERE employee_id = :emp_id")
                sal_result = db.session.execute(salary_query, {'emp_id': employee_id}).fetchone()
                total_salaries = sal_result[0] if sal_result else 0
            except:
                total_documents = 0
                total_attendances = 0
                total_salaries = 0
            
            # حساب أيام الخدمة
            service_days = 0
            join_date = employee.get('join_date')
            if join_date:
                service_days = (datetime.now().date() - join_date).days
            
            pdf.add_info_row('عدد الوثائق', str(total_documents))
            pdf.add_info_row('سجلات الحضور', str(total_attendances))
            pdf.add_info_row('سجلات الراتب', str(total_salaries))
            pdf.add_info_row('أيام الخدمة', str(service_days))
            
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