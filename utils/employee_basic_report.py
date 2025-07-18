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
        # مسار الخطوط يتكيف مع البيئة
        possible_font_paths = [
            'fonts',  # للبيئة المحلية والخادم
            'static/fonts',  # مسار بديل
            '/home/runner/workspace/static/fonts',  # للـ Replit
            os.path.join(os.getcwd(), 'fonts'),  # مسار نسبي
            os.path.join(os.getcwd(), 'static', 'fonts')  # مسار نسبي آخر
        ]
        
        self.font_path = None
        for path in possible_font_paths:
            if os.path.exists(path):
                self.font_path = path
                break
        
        # إذا لم نجد الخطوط، استخدم Cairo.ttf من المجلد الجذر
        if not self.font_path:
            if os.path.exists('Cairo.ttf'):
                self.font_path = '.'
            else:
                self.font_path = 'fonts'  # مسار افتراضي
        
    def header(self):
        """رأس الصفحة"""
        # إضافة الخط العربي
        try:
            if self.font_path:
                # محاولة استخدام خطوط Amiri أولاً
                amiri_regular = os.path.join(self.font_path, 'Amiri-Regular.ttf')
                amiri_bold = os.path.join(self.font_path, 'Amiri-Bold.ttf')
                
                if os.path.exists(amiri_regular) and os.path.exists(amiri_bold):
                    self.add_font('Arabic', '', amiri_regular, uni=True)
                    self.add_font('Arabic', 'B', amiri_bold, uni=True)
                else:
                    # استخدام Cairo.ttf كبديل
                    cairo_font = os.path.join(self.font_path, 'Cairo.ttf')
                    if os.path.exists(cairo_font):
                        self.add_font('Arabic', '', cairo_font, uni=True)
                        self.add_font('Arabic', 'B', cairo_font, uni=True)
                    elif os.path.exists('Cairo.ttf'):
                        self.add_font('Arabic', '', 'Cairo.ttf', uni=True)
                        self.add_font('Arabic', 'B', 'Cairo.ttf', uni=True)
                    else:
                        # محاولة العثور على خط عربي في النظام
                        self.set_font('Arial', 'B', 20)
                        return
        except Exception as e:
            print(f"خطأ في تحميل الخط: {e}")
            self.set_font('Arial', 'B', 20)
            return
        
        self.set_font('Arabic', 'B', 20)
        # العنوان الرئيسي
        title = get_display(reshape('تقرير المعلومات الأساسية للموظف'))
        self.cell(0, 15, title, 0, 1, 'C')
        self.ln(5)
        
    def footer(self):
        """تذييل الصفحة"""
        self.set_y(-15)
        self.set_font('Arabic', '', 10)
        page_text = get_display(reshape(f'صفحة {self.page_no()}'))
        self.cell(0, 10, page_text, 0, 0, 'C')
        
        # تاريخ الطباعة
        current_date = datetime.now().strftime('%Y/%m/%d')
        date_text = get_display(reshape(f'تاريخ الطباعة: {current_date}'))
        self.cell(0, 10, date_text, 0, 0, 'L')
        
    def add_section_title(self, title):
        """إضافة عنوان قسم"""
        self.ln(5)
        self.set_font('Arabic', 'B', 16)
        self.set_fill_color(70, 130, 180)  # لون أزرق فاتح
        self.set_text_color(255, 255, 255)  # نص أبيض
        
        title_text = get_display(reshape(title))
        self.cell(0, 12, title_text, 1, 1, 'C', True)
        self.set_text_color(0, 0, 0)  # إعادة النص للأسود
        self.ln(5)
        
    def add_info_row(self, label, value, is_bold=False):
        """إضافة صف معلومات"""
        font_style = 'B' if is_bold else ''
        self.set_font('Arabic', font_style, 12)
        
        # التسمية
        label_text = get_display(reshape(f'{label}:'))
        self.cell(60, 8, label_text, 1, 0, 'R')
        
        # القيمة
        value_text = get_display(reshape(str(value) if value else 'غير محدد'))
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
            self.set_font('Arabic', 'B', 12)
            title_text = get_display(reshape(title))
            
            # إطار للعنوان
            self.set_fill_color(255, 240, 240)  # لون وردي فاتح
            self.cell(0, 10, title_text, 1, 1, 'C', True)
            self.ln(3)
            
            # رسالة عدم التوفر
            self.set_font('Arabic', '', 11)
            self.set_text_color(128, 128, 128)  # رمادي
            no_image_text = get_display(reshape('غير متوفرة'))
            self.cell(0, 8, no_image_text, 0, 1, 'C')
            self.set_text_color(0, 0, 0)  # إعادة النص للأسود
            self.ln(8)
            return False

    def add_documents_row(self, employee):
        """إضافة صور الوثائق في صف واحد مع تنسيق احترافي"""
        # إضافة عنوان للوثائق
        self.set_font('Arabic', 'B', 14)
        docs_title = get_display(reshape('وثائق الموظف'))
        self.set_fill_color(230, 240, 250)
        self.cell(0, 10, docs_title, 1, 1, 'C', True)
        self.ln(8)
        
        # تحديد أبعاد الصور
        doc_width = 55
        doc_height = 40
        spacing = 15
        
        # حساب المواضع للصور الثلاث
        total_width = 3 * doc_width + 2 * spacing
        start_x = (self.w - total_width) / 2
        
        current_y = self.get_y()
        
        # الوثائق المطلوب عرضها
        documents = [
            (employee.national_id_image, 'الهوية الوطنية'),
            (employee.license_image, 'رخصة القيادة'),
            (employee.profile_image, 'صورة إضافية')
        ]
        
        # عرض الصور والعناوين
        for i, (image_path, title) in enumerate(documents):
            x_pos = start_x + i * (doc_width + spacing)
            
            # رسم إطار للصورة مع تدرج لوني
            self.set_draw_color(70, 130, 180)
            self.set_line_width(1.5)
            
            # إطار خارجي
            self.rect(x_pos - 2, current_y - 2, doc_width + 4, doc_height + 4)
            
            # إطار داخلي
            self.set_draw_color(200, 220, 240)
            self.set_line_width(0.5)
            self.rect(x_pos - 1, current_y - 1, doc_width + 2, doc_height + 2)
            
            # إضافة العنوان أسفل الإطار
            self.set_xy(x_pos, current_y + doc_height + 5)
            self.set_font('Arabic', 'B', 10)
            self.set_text_color(70, 130, 180)
            title_text = get_display(reshape(title))
            self.cell(doc_width, 6, title_text, 0, 0, 'C')
            
            # إضافة الصورة إذا كانت متوفرة
            if image_path:
                try:
                    full_path = os.path.join('/home/runner/workspace/static', image_path)
                    if os.path.exists(full_path):
                        # إضافة الصورة مع هوامش داخلية
                        margin = 3
                        self.image(full_path, x=x_pos + margin, y=current_y + margin, 
                                 w=doc_width - 2*margin, h=doc_height - 2*margin)
                    else:
                        # إضافة نص "غير متوفرة" مع تصميم أنيق
                        self.set_xy(x_pos + 5, current_y + doc_height/2 - 3)
                        self.set_font('Arabic', '', 9)
                        self.set_text_color(150, 150, 150)
                        error_text = get_display(reshape('غير متوفرة'))
                        self.cell(doc_width - 10, 6, error_text, 0, 0, 'C')
                        
                        # إضافة أيقونة بديلة
                        self.set_draw_color(200, 200, 200)
                        self.set_line_width(2)
                        center_x = x_pos + doc_width/2
                        center_y = current_y + doc_height/2
                        # رسم X بسيط
                        self.line(center_x - 8, center_y - 8, center_x + 8, center_y + 8)
                        self.line(center_x - 8, center_y + 8, center_x + 8, center_y - 8)
                        
                except Exception as e:
                    print(f"خطأ في عرض الصورة {image_path}: {str(e)}")
            else:
                # إضافة نص "غير متوفرة" مع أيقونة
                self.set_xy(x_pos + 5, current_y + doc_height/2 - 3)
                self.set_font('Arabic', '', 9)
                self.set_text_color(150, 150, 150)
                no_img_text = get_display(reshape('غير متوفرة'))
                self.cell(doc_width - 10, 6, no_img_text, 0, 0, 'C')
        
        # إعادة تعيين الألوان والخط
        self.set_text_color(0, 0, 0)
        self.set_draw_color(0, 0, 0)
        self.set_line_width(0.2)
        
        # الانتقال لأسفل قسم الوثائق
        self.set_y(current_y + doc_height + 25)


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
        
        # قسم الصور بتخطيط محسن
        pdf.add_section_title('الصور الشخصية والوثائق')
        
        # الصورة الشخصية في المنتصف (دائرية وأكبر)
        pdf.add_employee_image(employee.profile_image, 'الصورة الشخصية', 90, 90, is_profile=True)
        
        # صور الوثائق في صف واحد جنباً إلى جنب
        pdf.add_documents_row(employee)
        
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
        # الحصول على أسماء الأقسام (many-to-many relationship)
        department_names = ', '.join([dept.name for dept in employee.departments]) if employee.departments else 'غير محدد'
        pdf.add_info_row('القسم', department_names)
        pdf.add_info_row('الحالة الوظيفية', employee.status)
        pdf.add_info_row('نوع العقد', employee.contract_type)
        pdf.add_info_row('تاريخ الالتحاق', employee.join_date.strftime('%Y/%m/%d') if employee.join_date else 'غير محدد')
        pdf.add_info_row('الراتب الأساسي', f'{employee.basic_salary:.2f} ريال' if employee.basic_salary else 'غير محدد')
        pdf.add_info_row('الموقع', employee.location)
        pdf.add_info_row('المشروع', employee.project)
        
        # معلومات الكفالة
        pdf.add_section_title('معلومات الكفالة')
        sponsorship_status_text = 'على الكفالة' if employee.sponsorship_status != 'outside' else 'خارج الكفالة'
        pdf.add_info_row('حالة الكفالة', sponsorship_status_text)
        
        if employee.sponsorship_status != 'outside' and employee.current_sponsor_name:
            pdf.add_info_row('اسم الكفيل الحالي', employee.current_sponsor_name)
        elif employee.sponsorship_status != 'outside':
            pdf.add_info_row('اسم الكفيل الحالي', 'غير محدد')
        
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
        pdf_content = pdf.output(dest='S')
        output.write(pdf_content)
        output.seek(0)
        
        print(f"تم إنشاء ملف PDF بحجم: {len(pdf_content)} بايت")
        return output
        
    except Exception as e:
        print(f"خطأ في إنشاء التقرير الأساسي: {str(e)}")
        import traceback
        traceback.print_exc()
        return None