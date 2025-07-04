import os
from datetime import datetime
from io import BytesIO
from fpdf import FPDF
from arabic_reshaper import reshape
from bidi.algorithm import get_display
from models import Employee, VehicleHandover, Vehicle

class EmployeeBasicReportPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.font_path = self.find_font_path()
        self.arabic_font_available = False
        
    def find_font_path(self):
        """البحث عن مسار الخطوط"""
        possible_paths = [
            'fonts',
            'static/fonts', 
            os.path.join(os.getcwd(), 'fonts'),
            os.path.join(os.getcwd(), 'static', 'fonts'),
            '.'
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return '.'
        
    def setup_fonts(self):
        """إعداد الخطوط العربية"""
        if self.arabic_font_available:
            return True
            
        try:
            # محاولة Cairo.ttf أولاً
            cairo_path = os.path.join(self.font_path, 'Cairo.ttf')
            if os.path.exists(cairo_path):
                self.add_font('Arabic', '', cairo_path, uni=True)
                self.add_font('Arabic', 'B', cairo_path, uni=True)
                self.arabic_font_available = True
                return True
            
            # البحث عن Cairo.ttf في المجلد الجذر
            if os.path.exists('Cairo.ttf'):
                self.add_font('Arabic', '', 'Cairo.ttf', uni=True)
                self.add_font('Arabic', 'B', 'Cairo.ttf', uni=True)
                self.arabic_font_available = True
                return True
                
            # خطوط Amiri
            amiri_regular = os.path.join(self.font_path, 'Amiri-Regular.ttf')
            amiri_bold = os.path.join(self.font_path, 'Amiri-Bold.ttf')
            
            if os.path.exists(amiri_regular) and os.path.exists(amiri_bold):
                self.add_font('Arabic', '', amiri_regular, uni=True)
                self.add_font('Arabic', 'B', amiri_bold, uni=True)
                self.arabic_font_available = True
                return True
                
            return False
        except Exception as e:
            print(f"خطأ في إعداد الخط: {e}")
            return False
        
    def header(self):
        """رأس الصفحة"""
        if not self.setup_fonts():
            self.set_font('Arial', 'B', 20)
            self.cell(0, 15, 'Employee Basic Report', 0, 1, 'C')
        else:
            self.set_font('Arabic', 'B', 20)
            title = get_display(reshape('تقرير المعلومات الأساسية للموظف'))
            self.cell(0, 15, title, 0, 1, 'C')
        self.ln(5)
        
    def footer(self):
        """تذييل الصفحة"""
        self.set_y(-15)
        if self.setup_fonts():
            self.set_font('Arabic', '', 10)
            page_text = get_display(reshape(f'صفحة {self.page_no()}'))
            self.cell(0, 10, page_text, 0, 0, 'C')
            
            current_date = datetime.now().strftime('%Y/%m/%d')
            date_text = get_display(reshape(f'تاريخ الطباعة: {current_date}'))
            self.cell(0, 10, date_text, 0, 0, 'L')
        else:
            self.set_font('Arial', '', 10)
            self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')
            current_date = datetime.now().strftime('%Y/%m/%d')
            self.cell(0, 10, f'Print Date: {current_date}', 0, 0, 'L')
        
    def add_section_title(self, title):
        """إضافة عنوان قسم"""
        self.ln(5)
        if self.setup_fonts():
            self.set_font('Arabic', 'B', 16)
            title_text = get_display(reshape(title))
        else:
            self.set_font('Arial', 'B', 16)
            title_text = title
            
        self.set_fill_color(70, 130, 180)
        self.set_text_color(255, 255, 255)
        self.cell(0, 12, title_text, 1, 1, 'C', True)
        self.set_text_color(0, 0, 0)
        self.ln(3)
        
    def add_info_row(self, label, value, is_name=False):
        """إضافة صف معلومات"""
        if self.setup_fonts():
            if is_name:
                self.set_font('Arabic', 'B', 14)
            else:
                self.set_font('Arabic', '', 12)
            
            label_text = get_display(reshape(label))
            value_text = get_display(reshape(str(value) if value else 'غير محدد'))
        else:
            if is_name:
                self.set_font('Arial', 'B', 14)
            else:
                self.set_font('Arial', '', 12)
            
            label_text = label
            value_text = str(value) if value else 'Not specified'
        
        self.set_fill_color(248, 249, 250)
        self.cell(60, 10, label_text, 1, 0, 'R', True)
        self.cell(120, 10, value_text, 1, 1, 'L')


def generate_employee_basic_pdf(employee_id):
    """إنشاء تقرير المعلومات الأساسية للموظف"""
    try:
        print(f"بدء إنشاء التقرير الأساسي للموظف {employee_id}")
        
        employee = Employee.query.get(employee_id)
        if not employee:
            print(f"لم يتم العثور على الموظف {employee_id}")
            return None
            
        print(f"تم العثور على الموظف: {employee.name}")
        
        pdf = EmployeeBasicReportPDF()
        pdf.add_page()
        
        # المعلومات الأساسية
        pdf.add_section_title('المعلومات الأساسية')
        pdf.add_info_row('اسم الموظف', employee.name, True)
        pdf.add_info_row('رقم الهوية الوطنية', employee.national_id)
        pdf.add_info_row('رقم الموظف', employee.employee_id)
        pdf.add_info_row('رقم الجوال', employee.mobile)
        pdf.add_info_row('البريد الإلكتروني', employee.email or 'غير محدد')
        pdf.add_info_row('الجنسية', employee.nationality or 'غير محددة')
        
        # معلومات العمل
        pdf.add_section_title('معلومات العمل')
        pdf.add_info_row('المسمى الوظيفي', employee.job_title or 'غير محدد')
        pdf.add_info_row('القسم', employee.department.name if employee.department else 'غير محدد')
        pdf.add_info_row('الحالة الوظيفية', employee.status or 'غير محددة')
        pdf.add_info_row('نوع العقد', employee.contract_type or 'غير محدد')
        pdf.add_info_row('تاريخ الالتحاق', employee.join_date.strftime('%Y/%m/%d') if employee.join_date else 'غير محدد')
        pdf.add_info_row('الراتب الأساسي', f'{employee.basic_salary:.2f} ريال' if employee.basic_salary else 'غير محدد')
        pdf.add_info_row('الموقع', employee.location or 'غير محدد')
        pdf.add_info_row('المشروع', employee.project or 'غير محدد')
        
        # حفظ PDF
        output = BytesIO()
        pdf_content = pdf.output(dest='S')
        if isinstance(pdf_content, str):
            pdf_content = pdf_content.encode('latin-1')
        elif isinstance(pdf_content, bytearray):
            pdf_content = bytes(pdf_content)
        
        output.write(pdf_content)
        output.seek(0)
        
        print(f"تم إنشاء ملف PDF بحجم: {len(pdf_content)} بايت")
        return output
        
    except Exception as e:
        print(f"خطأ في إنشاء التقرير الأساسي: {str(e)}")
        import traceback
        traceback.print_exc()
        return None