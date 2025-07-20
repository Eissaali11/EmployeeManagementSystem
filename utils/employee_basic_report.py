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
        # Use beIN-Normal.ttf from static/fonts/
        self.font_path = os.path.join('static', 'fonts')
        self.bein_font = os.path.join(self.font_path, 'beIN-Normal.ttf')
        if not os.path.exists(self.bein_font):
            raise FileNotFoundError('beIN-Normal.ttf not found in static/fonts/')
        self.add_font('Arabic', '', self.bein_font, uni=True)
        self.add_font('Arabic', 'B', self.bein_font, uni=True)
        
    def _ensure_str(self, text):
        return text.decode('utf-8') if isinstance(text, bytes) else text
        
    def header(self):
        """رأس الصفحة مع شعار المشروع (الصفحة الأولى فقط)"""
        try:
            self.set_font('Arabic', 'B', 20)
        except Exception as e:
            print(f"خطأ في تحميل الخط: {e}")
            self.set_font('Arial', 'B', 20)
            return
        # إضافة الشعار في الأعلى (فقط الصفحة الأولى)
        if self.page_no() == 1:
            logo_path = os.path.join('static', 'images', 'logo_new.png')
            if os.path.exists(logo_path):
                self.image(logo_path, x=10, y=8, w=30, h=30)
        # العنوان الرئيسي
        title = self._ensure_str(get_display(reshape('تقرير المعلومات الأساسية للموظف')))
        self.set_xy(0, 12)
        self.set_text_color(40, 70, 120)
        self.cell(0, 20, title, 0, 1, 'C')
        self.ln(5)
        self.set_text_color(0, 0, 0)
        
    def footer(self):
        """تذييل الصفحة"""
        self.set_y(-15)
        self.set_font('Arabic', '', 10)
        page_text = self._ensure_str(get_display(reshape(f'صفحة {self.page_no()}')))
        self.cell(0, 10, page_text, 0, 0, 'C')
        
        # تاريخ الطباعة
        current_date = datetime.now().strftime('%Y/%m/%d')
        date_text = self._ensure_str(get_display(reshape(f'تاريخ الطباعة: {current_date}')))
        self.cell(0, 10, date_text, 0, 0, 'L')
        
    def add_section_title(self, title):
        """إضافة عنوان قسم"""
        self.ln(8)
        self.set_font('Arabic', 'B', 18)
        self.set_fill_color(70, 130, 180)
        self.set_text_color(255, 255, 255)
        title_text = self._ensure_str(get_display(reshape(title)))
        # إضافة ظل خفيف خلف العنوان
        y = self.get_y()
        self.set_fill_color(220, 230, 245)
        self.rect(10, y, self.w - 20, 18, 'F')
        self.set_fill_color(70, 130, 180)
        self.set_xy(10, y)
        self.cell(self.w - 20, 18, title_text, 0, 1, 'C', True)
        self.set_text_color(0, 0, 0)
        self.ln(4)
        
    def add_info_row(self, label, value, is_bold=False):
        """إضافة صف معلومات"""
        font_style = 'B' if is_bold else ''
        self.set_font('Arabic', font_style, 13)
        
        # التسمية
        label_text = self._ensure_str(get_display(reshape(f'{label}:')))
        
        # القيمة
        value_text = self._ensure_str(get_display(reshape(str(value) if value else 'غير محدد')))
        
        # Modern table row with subtle background and padding
        self.set_fill_color(245, 248, 255)
        self.set_draw_color(180, 200, 230)
        self.set_line_width(0.5)
        self.cell(120, 12, value_text, 1, 0, 'R', True)
        self.cell(60, 12, label_text, 1, 1, 'R', True)
        self.set_line_width(0.2)
        
    def add_vehicle_record(self, record):
        """إضافة سجل مركبة"""
        self.set_font('Arabic', '', 11)
        
        # رقم اللوحة
        plate_text = self._ensure_str(get_display(reshape(record.vehicle.plate_number if record.vehicle else 'غير محدد')))
        
        # نوع العملية
        operation_map = {'delivery': 'تسليم', 'return': 'استلام'}
        operation_text = self._ensure_str(get_display(reshape(operation_map.get(record.handover_type, record.handover_type))))
        
        # التاريخ
        date_text = record.handover_date.strftime('%Y/%m/%d') if record.handover_date else 'غير محدد'
        
        # الملاحظات
        notes_text = self._ensure_str(get_display(reshape(record.notes[:50] + '...' if record.notes and len(record.notes) > 50 else record.notes or 'لا توجد')))
        
        # Draw in RTL order: notes, date, operation, plate
        self.set_fill_color(255, 255, 255)
        self.set_draw_color(200, 220, 240)
        self.set_line_width(0.4)
        self.cell(70, 10, notes_text, 1, 0, 'R', True)
        self.cell(40, 10, date_text, 1, 0, 'C', True)
        self.cell(30, 10, operation_text, 1, 0, 'C', True)
        self.cell(40, 10, plate_text, 1, 1, 'C', True)
        self.set_line_width(0.2)
        
    def add_employee_image(self, image_path, title, max_width=70, max_height=70, is_profile=False):
        """إضافة صورة الموظف إلى التقرير مع تصميم جميل"""
        if image_path:
            try:
                # بناء المسار الصحيح للصورة
                full_path = os.path.join('static', image_path) if not image_path.startswith('static') else image_path
                if os.path.exists(full_path):
                    # إضافة عنوان الصورة مع تصميم جميل
                    self.set_font('Arabic', 'B', 14)
                    title_text = self._ensure_str(get_display(reshape(title)))
                    
                    # إطار للعنوان
                    self.set_fill_color(240, 248, 255)
                    self.set_draw_color(180, 200, 230)
                    self.set_line_width(0.8)
                    self.cell(0, 12, title_text, 0, 1, 'C', True)
                    self.ln(3)
                    
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
                        self.set_line_width(2)
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
                        self.set_line_width(1.2)
                        self.set_draw_color(34, 139, 34)  # لون أخضر
                        
                        # إطار خارجي مزدوج
                        self.rect(x-4, y-4, max_width+8, max_height+8)
                        self.set_line_width(0.7)
                        self.set_draw_color(220, 220, 220)  # رمادي فاتح
                        self.rect(x-2, y-2, max_width+4, max_height+4)
                        
                        # إضافة زخرفة في الزوايا
                        corner_size = 8
                        self.set_draw_color(34, 139, 34)
                        self.set_line_width(1)
                        
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
                    
                    self.ln(max_height + 15)
                    
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
            title_text = self._ensure_str(get_display(reshape(title)))
            
            # إطار للعنوان
            self.set_fill_color(255, 240, 240)  # لون وردي فاتح
            self.cell(0, 10, title_text, 1, 1, 'C', True)
            self.ln(3)
            
            # رسالة عدم التوفر
            self.set_font('Arabic', '', 11)
            self.set_text_color(128, 128, 128)  # رمادي
            no_image_text = self._ensure_str(get_display(reshape('غير متوفرة')))
            self.cell(0, 8, no_image_text, 0, 1, 'C')
            self.set_text_color(0, 0, 0)  # إعادة النص للأسود
            self.ln(8)
            return False

    def add_documents_row(self, employee):
        """إضافة صور الوثائق في صف واحد مع تنسيق احترافي"""
        # إضافة عنوان للوثائق
        self.set_font('Arabic', 'B', 14)
        docs_title = self._ensure_str(get_display(reshape('وثائق الموظف')))
        self.set_fill_color(230, 240, 250)
        self.set_draw_color(180, 200, 230)
        self.set_line_width(0.7)
        self.cell(0, 10, docs_title, 0, 1, 'C', True)
        self.ln(6)
        # تقليل حجم الصور والإطارات
        doc_width = 45
        doc_height = 32
        spacing = 12
        total_width = 3 * doc_width + 2 * spacing
        start_x = (self.w - total_width) / 2
        current_y = self.get_y()
        documents = [
            (employee.national_id_image, 'الهوية الوطنية'),
            (employee.license_image, 'رخصة القيادة'),
            (employee.profile_image, 'صورة إضافية')
        ]
        for i, (image_path, title) in enumerate(documents):
            x_pos = start_x + i * (doc_width + spacing)
            self.set_draw_color(70, 130, 180)
            self.set_line_width(1)
            self.rect(x_pos - 2, current_y - 2, doc_width + 4, doc_height + 4)
            self.set_draw_color(200, 220, 240)
            self.set_line_width(0.5)
            self.rect(x_pos - 1, current_y - 1, doc_width + 2, doc_height + 2)
            self.set_xy(x_pos, current_y + doc_height + 4)
            self.set_font('Arabic', 'B', 10)
            self.set_text_color(70, 130, 180)
            title_text = self._ensure_str(get_display(reshape(title)))
            self.cell(doc_width, 6, title_text, 0, 0, 'C')
            if image_path:
                try:
                    full_path = os.path.join('static', image_path) if not image_path.startswith('static') else image_path
                    if os.path.exists(full_path):
                        margin = 3
                        self.image(full_path, x=x_pos + margin, y=current_y + margin, w=doc_width - 2*margin, h=doc_height - 2*margin)
                    else:
                        self.set_xy(x_pos + 5, current_y + doc_height/2 - 3)
                        self.set_font('Arabic', '', 9)
                        self.set_text_color(150, 150, 150)
                        error_text = self._ensure_str(get_display(reshape('غير متوفرة')))
                        self.cell(doc_width - 10, 6, error_text, 0, 0, 'C')
                        self.set_draw_color(200, 200, 200)
                        self.set_line_width(2)
                        center_x = x_pos + doc_width/2
                        center_y = current_y + doc_height/2
                        self.line(center_x - 8, center_y - 8, center_x + 8, center_y + 8)
                        self.line(center_x - 8, center_y + 8, center_x + 8, center_y - 8)
                except Exception as e:
                    print(f"خطأ في عرض الصورة {image_path}: {str(e)}")
            else:
                self.set_xy(x_pos + 5, current_y + doc_height/2 - 3)
                self.set_font('Arabic', '', 9)
                self.set_text_color(150, 150, 150)
                no_img_text = self._ensure_str(get_display(reshape('غير متوفرة')))
                self.cell(doc_width - 10, 6, no_img_text, 0, 0, 'C')
        self.set_text_color(0, 0, 0)
        self.set_draw_color(0, 0, 0)
        self.set_line_width(0.2)
        self.set_y(current_y + doc_height + 18)


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
            # RTL order: notes, date, operation, plate
            pdf.cell(70, 10, pdf._ensure_str(get_display(reshape('الملاحظات'))), 1, 0, 'C')
            pdf.cell(40, 10, pdf._ensure_str(get_display(reshape('التاريخ'))), 1, 0, 'C')
            pdf.cell(30, 10, pdf._ensure_str(get_display(reshape('نوع العملية'))), 1, 0, 'C')
            pdf.cell(40, 10, pdf._ensure_str(get_display(reshape('رقم اللوحة'))), 1, 1, 'C')
            
            # البيانات
            for record in vehicle_records:
                pdf.add_vehicle_record(record)
        else:
            pdf.add_section_title('سجلات تسليم/استلام المركبات')
            pdf.set_font('Arabic', '', 12)
            no_records_text = pdf._ensure_str(get_display(reshape('لا توجد سجلات لتسليم أو استلام المركبات')))
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