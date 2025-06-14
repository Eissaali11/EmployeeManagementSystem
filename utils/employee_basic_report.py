"""
تقرير المعلومات الأساسية للموظف
يحتوي على: المعلومات الأساسية، معلومات العمل، سجلات المركبات، والصور والوثائق
"""
import os
import math
import tempfile
from io import BytesIO
from datetime import datetime
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
        """إعداد الخطوط العربية"""
        try:
            # محاولة تحميل Cairo.ttf من المجلد الجذر
            if os.path.exists('Cairo.ttf'):
                self.add_font('Arabic', '', 'Cairo.ttf', uni=True)
                self.add_font('Arabic', 'B', 'Cairo.ttf', uni=True)
                self.arabic_font_loaded = True
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
                    return
            
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
                return get_display(reshape(text))
            except:
                return text
        return text

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
        self.set_font('Arabic', '', 10)
        
        # رقم اللوحة
        plate_text = get_display(reshape(record.vehicle.plate_number if record.vehicle else 'غير محدد'))
        self.cell(40, 8, plate_text, 1, 0, 'C')
        
        # نوع العملية
        operation_map = {'delivery': 'تسليم', 'return': 'استلام'}
        operation_text = get_display(reshape(operation_map.get(record.handover_type, record.handover_type)))
        self.cell(30, 8, operation_text, 1, 0, 'C')
        
        # التاريخ
        date_text = record.handover_date.strftime('%Y/%m/%d') if record.handover_date else 'غير محدد'
        self.cell(40, 8, date_text, 1, 0, 'C')
        
        # الملاحظات
        notes_text = get_display(reshape(record.notes[:50] + '...' if record.notes and len(record.notes) > 50 else record.notes or 'لا توجد'))
        self.cell(70, 8, notes_text, 1, 1, 'R')
        
    def add_employee_image(self, image_path, title, max_width=60, max_height=60, is_profile=False):
        """إضافة صورة الموظف إلى التقرير مع تصميم جميل"""
        if image_path:
            try:
                # التحقق من وجود الملف
                full_path = os.path.join('/home/runner/workspace/static', image_path)
                if os.path.exists(full_path):
                    # إضافة عنوان الصورة مع تصميم جميل
                    self.set_font('Arabic', 'B', 14)
                    title_text = get_display(reshape(title))
                    
                    # إطار للعنوان
                    self.set_fill_color(240, 248, 255)  # لون أزرق فاتح جداً
                    self.cell(0, 10, title_text, 1, 1, 'C', True)
                    self.ln(5)
                    
                    # حساب موضع الصورة في المنتصف
                    x = (self.w - max_width) / 2
                    y = self.get_y()
                    
                    if is_profile:
                        # للصورة الشخصية - تطبيق قناع دائري
                        # فتح الصورة الأصلية
                        img = Image.open(full_path)
                        
                        # تحويل إلى RGB إذا لزم الأمر
                        if img.mode != 'RGB':
                            img = img.convert('RGB')
                        
                        # تغيير حجم الصورة لتكون مربعة
                        size = min(img.size)
                        img = img.resize((size, size), Image.Resampling.LANCZOS)
                        
                        # إنشاء قناع دائري
                        mask = Image.new('L', (size, size), 0)
                        draw = ImageDraw.Draw(mask)
                        draw.ellipse((0, 0, size, size), fill=255)
                        
                        # تطبيق القناع
                        img.putalpha(mask)
                        
                        # حفظ الصورة المدورة مؤقتاً
                        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
                            img.save(temp_file.name, 'PNG')
                            temp_path = temp_file.name
                        
                        # رسم إطار دائري أزرق
                        self.set_line_width(3)
                        self.set_draw_color(70, 130, 180)  # لون أزرق
                        center_x = x + max_width/2
                        center_y = y + max_height/2
                        radius = max_width/2 + 2
                        
                        # رسم الدائرة
                        segments = 60
                        for i in range(segments):
                            angle1 = 2 * math.pi * i / segments
                            angle2 = 2 * math.pi * (i + 1) / segments
                            x1 = center_x + radius * math.cos(angle1)
                            y1 = center_y + radius * math.sin(angle1)
                            x2 = center_x + radius * math.cos(angle2)
                            y2 = center_y + radius * math.sin(angle2)
                            self.line(x1, y1, x2, y2)
                        
                        # إضافة الصورة الدائرية
                        self.image(temp_path, x=x, y=y, w=max_width, h=max_height)
                        
                        # حذف الملف المؤقت
                        os.unlink(temp_path)
                        
                    else:
                        # للوثائق - إطار مستطيل مزخرف
                        self.set_line_width(2)
                        self.set_draw_color(34, 139, 34)  # لون أخضر
                        
                        # إطار خارجي مزدوج
                        self.rect(x-4, y-4, max_width+8, max_height+8)
                        self.set_line_width(1)
                        self.set_draw_color(220, 220, 220)  # رمادي فاتح
                        self.rect(x-2, y-2, max_width+4, max_height+4)
                        
                        # إضافة زخرفة في الزوايا
                        corner_size = 8
                        self.set_draw_color(34, 139, 34)
                        self.set_line_width(1.5)
                        
                        # الزاوية العلوية اليسرى
                        self.line(x-4, y-4+corner_size, x-4, y-4)
                        self.line(x-4, y-4, x-4+corner_size, y-4)
                        
                        # الزاوية العلوية اليمنى
                        self.line(x+max_width+4-corner_size, y-4, x+max_width+4, y-4)
                        self.line(x+max_width+4, y-4, x+max_width+4, y-4+corner_size)
                        
                        # الزاوية السفلية اليسرى
                        self.line(x-4, y+max_height+4-corner_size, x-4, y+max_height+4)
                        self.line(x-4, y+max_height+4, x-4+corner_size, y+max_height+4)
                        
                        # الزاوية السفلية اليمنى
                        self.line(x+max_width+4-corner_size, y+max_height+4, x+max_width+4, y+max_height+4)
                        self.line(x+max_width+4, y+max_height+4, x+max_width+4, y+max_height+4-corner_size)
                        
                        # إضافة الصورة
                        self.image(full_path, x=x, y=y, w=max_width, h=max_height)
                    
                    # إضافة ظل خفيف أسفل الصورة
                    self.set_fill_color(200, 200, 200)  # رمادي فاتح للظل
                    shadow_offset = 3
                    self.rect(x + shadow_offset, y + max_height + shadow_offset, max_width, 2, 'F')
                    
                    self.ln(max_height + 20)
                    
                    # إعادة تعيين إعدادات الرسم
                    self.set_line_width(0.2)
                    self.set_draw_color(0, 0, 0)
                    return True
                else:
                    print(f"ملف الصورة غير موجود: {full_path}")
                    return False
            except Exception as e:
                print(f"خطأ في إضافة الصورة {image_path}: {str(e)}")
                return False
        else:
            # عرض رسالة عدم وجود صورة مع تصميم جميل
            try:
                self.set_font('Arabic', 'B', 12)
                title_text = get_display(reshape(title))
            except:
                self.set_font('Arial', 'B', 12)
                title_text = title
            
            # إطار للعنوان
            self.set_fill_color(255, 240, 240)  # لون وردي فاتح
            self.cell(0, 10, title_text, 1, 1, 'C', True)
            self.ln(3)
            
            # رسالة عدم التوفر
            try:
                self.set_font('Arabic', '', 11)
                no_image_text = get_display(reshape('لا توجد صورة متاحة'))
            except:
                self.set_font('Arial', '', 11)
                no_image_text = 'No image available'
            
            self.set_text_color(128, 128, 128)  # رمادي
            self.cell(0, 8, no_image_text, 0, 1, 'C')
            self.set_text_color(0, 0, 0)  # إعادة النص للأسود
            self.ln(8)
            return False


def generate_employee_basic_pdf(employee_id):
    """إنشاء تقرير المعلومات الأساسية للموظف"""
    try:
        print(f"بدء إنشاء التقرير الأساسي للموظف {employee_id}")
        
        # جلب بيانات الموظف
        employee = Employee.query.get(employee_id)
        if not employee:
            print(f"لم يتم العثور على الموظف {employee_id}")
            return None
            
        print(f"تم العثور على الموظف: {employee.name}")
        
        # إنشاء PDF
        pdf = EmployeeBasicReportPDF()
        pdf.add_page()
        
        # عرض الصور في البداية
        # الصورة الشخصية في الرأس (دائرية)
        pdf.add_employee_image(employee.profile_image, 'الصورة الشخصية', 80, 80, is_profile=True)
        
        # صورة الهوية الوطنية (مستطيلة مع إطار)
        pdf.add_employee_image(employee.national_id_image, 'صورة الهوية الوطنية', 70, 50, is_profile=False)
        
        # صورة رخصة القيادة (مستطيلة مع إطار)
        pdf.add_employee_image(employee.license_image, 'صورة رخصة القيادة', 70, 50, is_profile=False)
        
        # المعلومات الأساسية
        pdf.add_section_title('المعلومات الأساسية')
        pdf.add_info_row('اسم الموظف', employee.name, True)
        pdf.add_info_row('رقم الهوية الوطنية', employee.national_id)
        pdf.add_info_row('رقم الموظف', employee.employee_id)
        pdf.add_info_row('رقم الجوال', employee.mobile)
        pdf.add_info_row('البريد الإلكتروني', employee.email)
        pdf.add_info_row('الجنسية', employee.nationality)
        
        # معلومات العمل
        pdf.add_section_title('معلومات العمل')
        pdf.add_info_row('المسمى الوظيفي', employee.job_title)
        pdf.add_info_row('القسم', employee.department.name if employee.department else 'غير محدد')
        pdf.add_info_row('الحالة الوظيفية', employee.status)
        pdf.add_info_row('نوع العقد', employee.contract_type)
        pdf.add_info_row('تاريخ الالتحاق', employee.join_date.strftime('%Y/%m/%d') if employee.join_date else 'غير محدد')
        pdf.add_info_row('الراتب الأساسي', f'{employee.basic_salary:.2f} ريال' if employee.basic_salary else 'غير محدد')
        pdf.add_info_row('الموقع', employee.location)
        pdf.add_info_row('المشروع', employee.project)
        
        # سجلات تسليم/استلام المركبات
        vehicle_records = VehicleHandover.query.filter_by(employee_id=employee.id).order_by(VehicleHandover.handover_date.desc()).limit(10).all()
        
        if vehicle_records:
            pdf.add_section_title('سجلات تسليم/استلام المركبات (آخر 10 سجلات)')
            
            # رؤوس الجدول
            pdf.set_font('Arabic', 'B', 10)
            pdf.cell(40, 10, get_display(reshape('رقم اللوحة')), 1, 0, 'C')
            pdf.cell(30, 10, get_display(reshape('نوع العملية')), 1, 0, 'C')
            pdf.cell(40, 10, get_display(reshape('التاريخ')), 1, 0, 'C')
            pdf.cell(70, 10, get_display(reshape('الملاحظات')), 1, 1, 'C')
            
            # البيانات
            for record in vehicle_records:
                pdf.add_vehicle_record(record)
        else:
            pdf.add_section_title('سجلات تسليم/استلام المركبات')
            pdf.set_font('Arabic', '', 12)
            no_records_text = get_display(reshape('لا توجد سجلات لتسليم أو استلام المركبات'))
            pdf.cell(0, 10, no_records_text, 0, 1, 'C')
        
        # إحصائيات الوثائق المرفقة
        pdf.add_section_title('الوثائق المرفقة')
        documents_count = len(employee.documents) if employee.documents else 0
        pdf.add_info_row('عدد الوثائق المرفقة', documents_count)
        
        # حفظ PDF في الذاكرة
        output = BytesIO()
        pdf_content = pdf.output(dest='S').encode('latin-1')
        output.write(pdf_content)
        output.seek(0)
        
        print(f"تم إنشاء ملف PDF بحجم: {len(pdf_content)} بايت")
        return output
        
    except Exception as e:
        print(f"خطأ في إنشاء التقرير الأساسي: {str(e)}")
        import traceback
        traceback.print_exc()
        return None