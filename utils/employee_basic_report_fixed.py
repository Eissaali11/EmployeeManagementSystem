"""
تقرير المعلومات الأساسية للموظف - إصدار محدث وآمن
يحتوي على: المعلومات الأساسية، معلومات العمل، سجلات المركبات، والصور والوثائق
"""

import os
from datetime import datetime
from io import BytesIO
from fpdf import FPDF
from arabic_reshaper import reshape
from bidi.algorithm import get_display
from models import Employee, VehicleHandover, Vehicle
from PIL import Image, ImageDraw

class EmployeeBasicReportPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.arabic_font_loaded = False
        self.setup_fonts()
    
    def setup_fonts(self):
        """إعداد الخطوط العربية مع معالجة الأخطاء"""
        try:
            # محاولة تحميل Cairo.ttf من المجلد الجذر
            if os.path.exists('Cairo.ttf'):
                self.add_font('Arabic', '', 'Cairo.ttf', uni=True)
                self.add_font('Arabic', 'B', 'Cairo.ttf', uni=True)
                self.arabic_font_loaded = True
                print("تم تحميل الخط العربي بنجاح من Cairo.ttf")
                return
            
            # البحث في مجلدات أخرى
            possible_paths = [
                'fonts/Cairo.ttf',
                'static/fonts/Cairo.ttf',
                'fonts/Amiri-Regular.ttf'
            ]
            
            for font_path in possible_paths:
                if os.path.exists(font_path):
                    self.add_font('Arabic', '', font_path, uni=True)
                    self.add_font('Arabic', 'B', font_path, uni=True)
                    self.arabic_font_loaded = True
                    print(f"تم تحميل الخط العربي من {font_path}")
                    return
            
            print("لم يتم العثور على خط عربي، سيتم استخدام Arial")
            
        except Exception as e:
            print(f"خطأ في تحميل الخط العربي: {e}")
            self.arabic_font_loaded = False
    
    def safe_set_font(self, family='Arabic', style='', size=12):
        """تعيين خط آمن مع التحقق من توفر الخط العربي"""
        try:
            if family == 'Arabic' and self.arabic_font_loaded:
                self.set_font('Arabic', style, size)
                return True
            else:
                self.set_font('Arial', style, size)
                return False
        except:
            self.set_font('Arial', style, size)
            return False
    
    def safe_text(self, text, use_arabic=True):
        """معالجة آمنة للنص العربي"""
        if use_arabic and self.arabic_font_loaded:
            try:
                return get_display(reshape(str(text)))
            except:
                return str(text)
        return str(text)

    def header(self):
        """رأس الصفحة"""
        self.safe_set_font('Arabic', 'B', 20)
        title = self.safe_text('تقرير المعلومات الأساسية للموظف')
        if not self.arabic_font_loaded:
            title = 'Employee Basic Report'
        self.cell(0, 15, title, 0, 1, 'C')
        self.ln(5)
        
    def footer(self):
        """تذييل الصفحة"""
        self.set_y(-15)
        self.safe_set_font('Arabic', '', 10)
        
        # رقم الصفحة
        page_text = self.safe_text(f'صفحة {self.page_no()}')
        if not self.arabic_font_loaded:
            page_text = f'Page {self.page_no()}'
        self.cell(0, 10, page_text, 0, 0, 'C')
        
        # تاريخ الطباعة
        current_date = datetime.now().strftime('%Y/%m/%d')
        date_text = self.safe_text(f'تاريخ الطباعة: {current_date}')
        if not self.arabic_font_loaded:
            date_text = f'Print Date: {current_date}'
        self.cell(0, 10, date_text, 0, 0, 'L')
        
    def add_section_title(self, title):
        """إضافة عنوان قسم"""
        self.ln(5)
        self.safe_set_font('Arabic', 'B', 16)
        self.set_fill_color(70, 130, 180)  # لون أزرق فاتح
        self.set_text_color(255, 255, 255)  # نص أبيض
        
        title_text = self.safe_text(title)
        self.cell(0, 12, title_text, 1, 1, 'C', True)
        self.set_text_color(0, 0, 0)  # إعادة النص للأسود
        self.ln(5)
        
    def add_info_row(self, label, value, is_bold=False):
        """إضافة صف معلومات"""
        font_style = 'B' if is_bold else ''
        self.safe_set_font('Arabic', font_style, 12)
        
        # التسمية
        label_text = self.safe_text(f'{label}:')
        if not self.arabic_font_loaded:
            label_text = f'{label}:'
        self.cell(60, 8, label_text, 1, 0, 'R')
        
        # القيمة
        value_str = str(value) if value else 'غير محدد'
        value_text = self.safe_text(value_str)
        if not self.arabic_font_loaded and not value:
            value_text = 'Not specified'
        self.cell(120, 8, value_text, 1, 1, 'R')
        
    def add_vehicle_record(self, record):
        """إضافة سجل مركبة"""
        self.safe_set_font('Arabic', '', 10)
        
        # عرض معلومات المركبة
        vehicle_info = f"رقم اللوحة: {record.vehicle.plate_number if record.vehicle else 'غير محدد'}"
        if record.handover_date:
            vehicle_info += f" - تاريخ الاستلام: {record.handover_date.strftime('%Y-%m-%d')}"
        if record.return_date:
            vehicle_info += f" - تاريخ الإرجاع: {record.return_date.strftime('%Y-%m-%d')}"
            
        vehicle_text = self.safe_text(vehicle_info)
        if not self.arabic_font_loaded:
            vehicle_text = f"Plate: {record.vehicle.plate_number if record.vehicle else 'N/A'}"
            if record.handover_date:
                vehicle_text += f" - Handover: {record.handover_date.strftime('%Y-%m-%d')}"
            if record.return_date:
                vehicle_text += f" - Return: {record.return_date.strftime('%Y-%m-%d')}"
        
        self.cell(0, 8, vehicle_text, 1, 1, 'R')
        
    def add_employee_image(self, image_path, title, max_width=60, max_height=60, is_profile=False):
        """إضافة صورة الموظف إلى التقرير مع تصميم جميل"""
        
        # إضافة عنوان فرعي للصورة
        self.safe_set_font('Arabic', 'B', 14)
        self.set_fill_color(245, 245, 245)  # لون رمادي فاتح جداً
        
        title_text = self.safe_text(title)
        if not self.arabic_font_loaded:
            if 'الشخصية' in title:
                title_text = 'Profile Photo'
            elif 'الهوية' in title:
                title_text = 'ID Document'
            else:
                title_text = title
        
        self.cell(0, 10, title_text, 1, 1, 'C', True)
        self.ln(3)
        
        # التحقق من وجود الصورة
        if not image_path or not os.path.exists(image_path):
            # رسالة عدم التوفر
            try:
                self.safe_set_font('Arabic', '', 11)
                no_image_text = self.safe_text('لا توجد صورة متاحة')
                if not self.arabic_font_loaded:
                    no_image_text = 'No image available'
            except:
                self.set_font('Arial', '', 11)
                no_image_text = 'No image available'
            
            self.set_text_color(128, 128, 128)  # رمادي
            self.cell(0, 8, no_image_text, 0, 1, 'C')
            self.set_text_color(0, 0, 0)  # إعادة النص للأسود
            self.ln(8)
            return False

        try:
            # فتح الصورة وتحسين جودتها
            img = Image.open(image_path)
            
            # تحويل الصورة إلى RGB إذا لزم الأمر
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # تحسين جودة الصورة إذا كانت صغيرة
            original_width, original_height = img.size
            if original_width < 200 or original_height < 200:
                # تكبير الصورة بجودة عالية
                scale_factor = max(200 / original_width, 200 / original_height)
                new_width = int(original_width * scale_factor)
                new_height = int(original_height * scale_factor)
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # حساب أبعاد العرض مع الحفاظ على النسبة
            width, height = img.size
            aspect_ratio = width / height
            
            if width > height:
                display_width = min(max_width, width * 0.3)  # تصغير قليل لتحسين العرض
                display_height = display_width / aspect_ratio
            else:
                display_height = min(max_height, height * 0.3)
                display_width = display_height * aspect_ratio
            
            # حفظ الصورة مؤقتاً بجودة عالية
            temp_image_path = f"temp_image_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            img.save(temp_image_path, "JPEG", quality=95, optimize=True)
            
            # حساب موقع الصورة للتوسيط
            page_width = self.w - 2 * self.l_margin
            x_position = self.l_margin + (page_width - display_width) / 2
            
            # إضافة الصورة
            self.image(temp_image_path, x=x_position, w=display_width, h=display_height)
            
            # حذف الملف المؤقت
            if os.path.exists(temp_image_path):
                os.remove(temp_image_path)
            
            self.ln(display_height + 5)
            return True
            
        except Exception as e:
            print(f"خطأ في معالجة الصورة {image_path}: {e}")
            # رسالة خطأ في تحميل الصورة
            self.safe_set_font('Arabic', '', 11)
            error_text = self.safe_text('خطأ في تحميل الصورة')
            if not self.arabic_font_loaded:
                error_text = 'Error loading image'
                
            self.set_text_color(255, 0, 0)  # أحمر
            self.cell(0, 8, error_text, 0, 1, 'C')
            self.set_text_color(0, 0, 0)  # إعادة النص للأسود
            self.ln(8)
            return False


def generate_employee_basic_pdf(employee_id):
    """إنشاء تقرير المعلومات الأساسية للموظف"""
    try:
        print(f"بدء إنشاء التقرير الأساسي للموظف {employee_id}")
        
        # البحث عن الموظف
        employee = Employee.query.get(employee_id)
        if not employee:
            print(f"لم يتم العثور على الموظف {employee_id}")
            return None
        
        print(f"تم العثور على الموظف: {employee.first_name} {employee.last_name}")
        
        # إنشاء PDF
        pdf = EmployeeBasicReportPDF()
        pdf.add_page()
        
        # المعلومات الأساسية
        pdf.add_section_title('المعلومات الأساسية')
        
        pdf.add_info_row('الاسم الأول', employee.first_name)
        pdf.add_info_row('اسم العائلة', employee.last_name)
        pdf.add_info_row('رقم الهوية', employee.national_id)
        pdf.add_info_row('رقم الهاتف', employee.phone)
        pdf.add_info_row('البريد الإلكتروني', employee.email)
        pdf.add_info_row('تاريخ الميلاد', employee.birth_date.strftime('%Y-%m-%d') if employee.birth_date else 'غير محدد')
        pdf.add_info_row('الجنسية', employee.nationality)
        pdf.add_info_row('العنوان', employee.address)
        
        # معلومات العمل
        pdf.add_section_title('معلومات العمل')
        
        pdf.add_info_row('رقم الموظف', employee.employee_number)
        pdf.add_info_row('المسمى الوظيفي', employee.job_title)
        pdf.add_info_row('القسم', employee.department.name if employee.department else 'غير محدد')
        pdf.add_info_row('تاريخ التوظيف', employee.hire_date.strftime('%Y-%m-%d') if employee.hire_date else 'غير محدد')
        pdf.add_info_row('الراتب الأساسي', f"{employee.basic_salary:,.2f} ريال" if employee.basic_salary else 'غير محدد')
        pdf.add_info_row('حالة الموظف', employee.status)
        
        # إضافة الصورة الشخصية إذا كانت متوفرة
        if employee.profile_image:
            pdf.add_employee_image(employee.profile_image, 'الصورة الشخصية', 80, 80, is_profile=True)
        
        # إضافة صورة الهوية إذا كانت متوفرة
        if employee.id_document:
            pdf.add_employee_image(employee.id_document, 'صورة الهوية', 120, 80)
        
        # سجلات المركبات
        vehicle_handovers = VehicleHandover.query.filter_by(employee_id=employee_id).all()
        if vehicle_handovers:
            pdf.add_section_title('سجلات المركبات')
            
            for handover in vehicle_handovers:
                pdf.add_vehicle_record(handover)
        
        # حفظ PDF
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"employee_basic_report_{employee_id}_{timestamp}.pdf"
        
        pdf_output = pdf.output(dest='S').encode('latin1')
        
        print(f"تم إنشاء التقرير الأساسي بنجاح: {filename}")
        return pdf_output, filename
        
    except Exception as e:
        print(f"خطأ في إنشاء التقرير الأساسي: {e}")
        import traceback
        traceback.print_exc()
        return None, None