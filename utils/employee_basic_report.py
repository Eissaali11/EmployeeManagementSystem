"""
تقرير المعلومات الأساسية للموظف
يحتوي على: المعلومات الأساسية، معلومات العمل، سجلات المركبات، والصور والوثائق
"""
import os
from io import BytesIO
from datetime import datetime
from fpdf import FPDF
from arabic_reshaper import reshape
from bidi.algorithm import get_display
from models import Employee, VehicleHandover, Vehicle

class EmployeeBasicReportPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.font_path = '/home/runner/workspace/static/fonts'
        
    def header(self):
        """رأس الصفحة"""
        # إضافة الخط العربي
        self.add_font('Arabic', '', os.path.join(self.font_path, 'Amiri-Regular.ttf'), uni=True)
        self.add_font('Arabic', 'B', os.path.join(self.font_path, 'Amiri-Bold.ttf'), uni=True)
        
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
                    
                    # إضافة إطار مزخرف للصورة
                    if is_profile:
                        # إطار دائري للصورة الشخصية
                        self.set_line_width(2)
                        self.set_draw_color(70, 130, 180)  # لون أزرق
                        # رسم دائرة حول الصورة
                        center_x = x + max_width/2
                        center_y = y + max_height/2
                        radius = max(max_width, max_height)/2 + 3
                        
                        # رسم دائرة باستخدام خطوط منحنية
                        import math
                        segments = 36
                        for i in range(segments + 1):
                            angle = 2 * math.pi * i / segments
                            px = center_x + radius * math.cos(angle)
                            py = center_y + radius * math.sin(angle)
                            if i == 0:
                                self.set_xy(px, py)
                            else:
                                prev_angle = 2 * math.pi * (i-1) / segments
                                prev_px = center_x + radius * math.cos(prev_angle)
                                prev_py = center_y + radius * math.sin(prev_angle)
                                self.line(prev_px, prev_py, px, py)
                    else:
                        # إطار مستطيل مزخرف للوثائق
                        self.set_line_width(1.5)
                        self.set_draw_color(34, 139, 34)  # لون أخضر
                        # إطار خارجي
                        self.rect(x-3, y-3, max_width+6, max_height+6)
                        # إطار داخلي
                        self.set_draw_color(220, 220, 220)  # رمادي فاتح
                        self.rect(x-1, y-1, max_width+2, max_height+2)
                    
                    # إضافة الصورة
                    self.image(full_path, x=x, y=y, w=max_width, h=max_height)
                    
                    # إضافة ظل خفيف أسفل الصورة
                    self.set_fill_color(200, 200, 200)  # رمادي فاتح للظل
                    shadow_offset = 2
                    self.rect(x + shadow_offset, y + max_height + shadow_offset, max_width, 1, 'F')
                    
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