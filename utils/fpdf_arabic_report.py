"""
وحدة إنشاء تقارير PDF باستخدام FPDF2 مع دعم كامل للغة العربية وتصميم احترافي
"""

import os
import io
from datetime import datetime
from fpdf import FPDF
import arabic_reshaper
from bidi.algorithm import get_display

# تعريف مسار المجلد الحالي
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(CURRENT_DIR)

class ProfessionalArabicPDF(FPDF):
    """فئة PDF احترافية مع دعم كامل للغة العربية والتصميم الحديث"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_auto_page_break(auto=True, margin=20)
        
        # تسجيل الخطوط العربية
        font_path = os.path.join(PROJECT_DIR, 'static', 'fonts')
        
        try:
            # إضافة خط Tajawal (خط عصري للعناوين)
            self.add_font('Tajawal', '', os.path.join(font_path, 'Tajawal-Regular.ttf'), uni=True)
            self.add_font('Tajawal', 'B', os.path.join(font_path, 'Tajawal-Bold.ttf'), uni=True)
            
            # إضافة خط Amiri (خط تقليدي للنصوص)
            self.add_font('Amiri', '', os.path.join(font_path, 'Amiri-Regular.ttf'), uni=True)
            self.add_font('Amiri', 'B', os.path.join(font_path, 'Amiri-Bold.ttf'), uni=True)
            
            self.fonts_available = True
        except Exception as e:
            print(f"خطأ في تحميل الخطوط: {e}")
            self.fonts_available = False
        
        # تعريف الألوان المستخدمة في التصميم
        self.colors = {
            'primary': (41, 128, 185),       # أزرق أساسي
            'secondary': (52, 73, 94),       # رمادي غامق
            'success': (39, 174, 96),        # أخضر
            'warning': (243, 156, 18),       # برتقالي
            'danger': (231, 76, 60),         # أحمر
            'light_gray': (236, 240, 241),   # رمادي فاتح
            'white': (255, 255, 255),        # أبيض
            'black': (0, 0, 0),              # أسود
            'text_dark': (44, 62, 80),       # نص غامق
            'text_light': (127, 140, 141),   # نص فاتح
            'gradient_start': (74, 144, 226), # بداية التدرج
            'gradient_end': (80, 170, 200)   # نهاية التدرج
        }
    
    def arabic_text(self, txt):
        """إعادة تشكيل النص العربي وتحويله ليعرض بشكل صحيح"""
        if txt is None or txt == '':
            return ''
        
        # تحويل إلى نص
        txt_str = str(txt)
        
        # تخطي معالجة الأرقام فقط
        if txt_str.replace('.', '').replace(',', '').replace('-', '').replace(' ', '').isdigit():
            return txt_str
        
        # فحص إذا كان النص يحتوي على أحرف عربية
        has_arabic = any('\u0600' <= c <= '\u06FF' or '\u0750' <= c <= '\u077F' or '\uFB50' <= c <= '\uFDFF' or '\uFE70' <= c <= '\uFEFF' for c in txt_str)
        
        if not has_arabic:
            return txt_str
        
        try:
            # تطبيق reshaper مع إعدادات محسنة
            reshaped_text = arabic_reshaper.reshape(
                txt_str,
                delete_harakat=False,  # الاحتفاظ بالتشكيل
                support_zwj=True,      # دعم الزخارف
                delete_tatweel=False   # الاحتفاظ بالتطويل
            )
            
            # تطبيق خوارزمية الاتجاه الثنائي
            bidi_text = get_display(reshaped_text, base_dir='R')
            
            return bidi_text
        except Exception as e:
            print(f"خطأ في معالجة النص العربي '{txt_str}': {e}")
            return txt_str
    
    def cell(self, w=0, h=0, text='', border=0, ln=0, align='', fill=False, link=''):
        """تجاوز دالة الخلية لدعم النص العربي"""
        arabic_txt = self.arabic_text(text)
        super().cell(w, h, arabic_txt, border, ln, align, fill, link)
    
    def multi_cell(self, w=0, h=0, text='', border=0, align='', fill=False):
        """تجاوز دالة الخلايا المتعددة لدعم النص العربي"""
        arabic_txt = self.arabic_text(text)
        super().multi_cell(w, h, arabic_txt, border, align, fill)
    
    def set_color(self, color_name):
        """تعيين لون من مجموعة الألوان المحددة"""
        if color_name in self.colors:
            r, g, b = self.colors[color_name]
            self.set_text_color(r, g, b)
            return r, g, b
        return 0, 0, 0
    
    def set_fill_color_custom(self, color_name):
        """تعيين لون الخلفية من مجموعة الألوان المحددة"""
        if color_name in self.colors:
            r, g, b = self.colors[color_name]
            self.set_fill_color(r, g, b)
            return r, g, b
        return 255, 255, 255
    
    def draw_header_background(self):
        """رسم خلفية متدرجة لرأس الصفحة"""
        # رسم مستطيل متدرج للخلفية
        self.set_fill_color_custom('primary')
        self.rect(0, 0, 210, 60, 'F')
        
        # إضافة نمط هندسي خفيف
        self.set_draw_color(255, 255, 255)
        self.set_line_width(0.3)
        
        # رسم خطوط قطرية خفيفة بدلاً من الشفافية
        for i in range(0, 220, 30):
            self.line(i, 0, i+15, 60)
            
        # إضافة تأثير بصري بدلاً من الشفافية
        self.set_fill_color(255, 255, 255)
        # رسم مستطيلات صغيرة كنقاط زخرفية
        for x in range(20, 200, 40):
            for y in range(10, 50, 20):
                self.rect(x, y, 2, 2, 'F')
    
    def add_decorative_border(self, x, y, w, h, color='primary'):
        """إضافة حدود زخرفية ملونة"""
        r, g, b = self.set_fill_color_custom(color)
        
        # الحد العلوي
        self.rect(x, y, w, 2, 'F')
        # الحد السفلي
        self.rect(x, y + h - 2, w, 2, 'F')
        # الحد الأيسر
        self.rect(x, y, 2, h, 'F')
        # الحد الأيمن
        self.rect(x + w - 2, y, 2, h, 'F')
    
    def add_section_header(self, title, icon='■'):
        """إضافة رأس قسم مع تصميم احترافي"""
        current_y = self.get_y()
        
        # خلفية القسم
        self.set_fill_color_custom('light_gray')
        self.rect(10, current_y, 190, 12, 'F')
        
        # شريط ملون على اليسار
        self.set_fill_color_custom('primary')
        self.rect(10, current_y, 4, 12, 'F')
        
        # النص
        self.set_xy(20, current_y + 2)
        if self.fonts_available:
            self.set_font('Tajawal', 'B', 14)
        else:
            self.set_font('Arial', 'B', 14)
        
        self.set_color('text_dark')
        self.cell(0, 8, f'{icon} {title}', 0, 1, 'R')
        self.ln(3)


def calculate_days_in_workshop(entry_date, exit_date=None):
    """
    حساب عدد الأيام التي قضتها السيارة في الورشة
    
    Args:
        entry_date: تاريخ دخول الورشة
        exit_date: تاريخ خروج الورشة (إذا كان None، يعني أنها لا تزال في الورشة)
    
    Returns:
        int: عدد الأيام في الورشة
    """
    if not entry_date:
        return 0
    
    # إذا لم يكن هناك تاريخ خروج، نستخدم تاريخ اليوم
    end_date = exit_date if exit_date else datetime.now().date()
    
    # حساب الفرق بين التواريخ
    if isinstance(entry_date, datetime):
        entry_date = entry_date.date()
    if isinstance(end_date, datetime):
        end_date = end_date.date()
    
    # محاولة حساب الفرق
    try:
        days = (end_date - entry_date).days
        return max(0, days)  # لا يمكن أن يكون عدد الأيام سالبًا
    except:
        return 0


def generate_workshop_report_pdf_fpdf(vehicle, workshop_records):
    """
    إنشاء تقرير سجلات الورشة للمركبة باستخدام FPDF مع تصميم احترافي
    
    Args:
        vehicle: كائن المركبة
        workshop_records: قائمة بسجلات الورشة
    
    Returns:
        BytesIO: كائن بايت يحتوي على ملف PDF
    """
    # إنشاء كائن PDF مع دعم اللغة العربية
    pdf = ProfessionalArabicPDF(orientation='P', unit='mm', format='A4')
    pdf.set_title('تقرير سجلات الورشة')
    pdf.set_author('نُظم - نظام إدارة المركبات')
    
    # إضافة صفحة جديدة
    pdf.add_page()
    
    # ===== رأس الصفحة الاحترافي =====
    pdf.draw_header_background()
    
    # إضافة الشعار في رأس الصفحة
    possible_logo_paths = [
        os.path.join(PROJECT_DIR, 'static', 'images', 'logo', 'logo_new.png'),
        os.path.join(PROJECT_DIR, 'static', 'images', 'logo_new.png'),
        os.path.join(PROJECT_DIR, 'static', 'images', 'logo.png')
    ]
    
    # البحث عن أول ملف شعار موجود
    logo_path = None
    for path in possible_logo_paths:
        if os.path.exists(path):
            logo_path = path
            break
    
    # إذا وجدنا شعارًا، قم بإضافته
    if logo_path:
        try:
            pdf.image(logo_path, x=15, y=10, w=40, h=40)
        except:
            # إذا فشل تحميل الشعار، نرسم شعار نصي بديل
            pdf.set_fill_color(255, 255, 255)
            pdf.set_xy(15, 20)
            pdf.rect(15, 20, 40, 20, 'F')
            pdf.set_text_color(41, 128, 185)
            if pdf.fonts_available:
                pdf.set_font('Tajawal', 'B', 16)
            else:
                pdf.set_font('Arial', 'B', 16)
            pdf.set_xy(15, 25)
            pdf.cell(40, 10, 'نُظم', 0, 0, 'C')
    else:
        # شعار نصي بديل
        pdf.set_fill_color(255, 255, 255)
        pdf.rect(15, 15, 40, 30, 'F')
        pdf.set_text_color(41, 128, 185)
        if pdf.fonts_available:
            pdf.set_font('Tajawal', 'B', 20)
        else:
            pdf.set_font('Arial', 'B', 20)
        pdf.set_xy(15, 25)
        pdf.cell(40, 10, 'نُظم', 0, 0, 'C')
    
    # عنوان التقرير
    pdf.set_text_color(255, 255, 255)
    if pdf.fonts_available:
        pdf.set_font('Tajawal', 'B', 24)
    else:
        pdf.set_font('Arial', 'B', 24)
    pdf.set_xy(70, 15)
    pdf.cell(120, 12, 'تقرير سجلات الورشة', 0, 1, 'C')
    
    # معلومات السيارة في الرأس
    if pdf.fonts_available:
        pdf.set_font('Tajawal', 'B', 16)
    else:
        pdf.set_font('Arial', 'B', 16)
    pdf.set_xy(70, 30)
    pdf.cell(120, 10, f'{vehicle.make} {vehicle.model} - {vehicle.plate_number}', 0, 1, 'C')
    
    # تاريخ التقرير
    if pdf.fonts_available:
        pdf.set_font('Amiri', '', 12)
    else:
        pdf.set_font('Arial', '', 12)
    pdf.set_xy(70, 42)
    pdf.cell(120, 8, f'تاريخ التقرير: {datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 1, 'C')
    
    # إعادة تعيين اللون للنص العادي
    pdf.set_text_color(0, 0, 0)
    pdf.set_y(70)
    
    # ===== معلومات المركبة =====
    pdf.add_section_header('معلومات المركبة', '■')
    
    # جدول معلومات المركبة مع تصميم احترافي
    vehicle_info = [
        ['رقم اللوحة:', vehicle.plate_number or 'غير محدد'],
        ['الماركة:', vehicle.make or 'غير محدد'],
        ['الموديل:', vehicle.model or 'غير محدد'],
        ['سنة الصنع:', str(vehicle.year) if hasattr(vehicle, 'year') and vehicle.year else 'غير محدد']
    ]
    
    # إضافة معلومات إضافية إذا كانت متوفرة
    if hasattr(vehicle, 'vin') and vehicle.vin:
        vehicle_info.append(['رقم الهيكل:', vehicle.vin])
    
    if hasattr(vehicle, 'odometer') and vehicle.odometer:
        vehicle_info.append(['قراءة العداد:', f'{vehicle.odometer:,} كم'])
    
    # رسم جدول معلومات المركبة بتصميم حديث
    current_y = pdf.get_y()
    
    # خلفية الجدول
    pdf.set_fill_color_custom('white')
    pdf.rect(15, current_y, 180, len(vehicle_info) * 8 + 4, 'F')
    
    # حدود ملونة للجدول
    pdf.add_decorative_border(15, current_y, 180, len(vehicle_info) * 8 + 4)
    
    pdf.set_y(current_y + 2)
    
    for i, info in enumerate(vehicle_info):
        # تناوب ألوان الصفوف
        if i % 2 == 0:
            pdf.set_fill_color(248, 249, 250)
        else:
            pdf.set_fill_color(255, 255, 255)
        
        pdf.set_x(17)
        
        # العمود الأول (التسمية)
        if pdf.fonts_available:
            pdf.set_font('Tajawal', 'B', 11)
        else:
            pdf.set_font('Arial', 'B', 11)
        pdf.set_color('text_dark')
        pdf.cell(80, 8, info[0], 0, 0, 'R', True)
        
        # العمود الثاني (القيمة)
        if pdf.fonts_available:
            pdf.set_font('Amiri', '', 11)
        else:
            pdf.set_font('Arial', '', 11)
        pdf.set_color('primary')
        pdf.cell(96, 8, info[1], 0, 1, 'R', True)
    
    pdf.ln(10)
    
    # ===== سجلات الورشة =====
    pdf.add_section_header('سجلات الورشة', '■')
    
    # التحقق من وجود سجلات
    if not workshop_records or len(workshop_records) == 0:
        # رسالة عدم وجود سجلات مع تصميم جميل
        pdf.set_fill_color_custom('light_gray')
        pdf.rect(15, pdf.get_y(), 180, 30, 'F')
        
        pdf.add_decorative_border(15, pdf.get_y(), 180, 30, 'warning')
        
        if pdf.fonts_available:
            pdf.set_font('Tajawal', 'B', 14)
        else:
            pdf.set_font('Arial', 'B', 14)
        pdf.set_color('text_light')
        pdf.set_y(pdf.get_y() + 12)
        pdf.cell(0, 6, 'لا توجد سجلات ورشة لهذه المركبة', 0, 1, 'C')
        
        pdf.ln(15)
    else:
        # إحصائيات سريعة
        total_records = len(workshop_records)
        total_cost = sum(float(record.cost) if hasattr(record, 'cost') and record.cost else 0 for record in workshop_records)
        total_days = sum(calculate_days_in_workshop(
            record.entry_date if hasattr(record, 'entry_date') else None,
            record.exit_date if hasattr(record, 'exit_date') else None
        ) for record in workshop_records)
        
        # صندوق الإحصائيات
        stats_y = pdf.get_y()
        
        # خلفية الإحصائيات
        pdf.set_fill_color_custom('primary')
        pdf.rect(15, stats_y, 180, 25, 'F')
        
        pdf.set_text_color(255, 255, 255)
        if pdf.fonts_available:
            pdf.set_font('Tajawal', 'B', 12)
        else:
            pdf.set_font('Arial', 'B', 12)
        
        # توزيع الإحصائيات على ثلاثة أعمدة
        pdf.set_xy(20, stats_y + 5)
        pdf.cell(56, 6, f'عدد السجلات: {total_records}', 0, 0, 'R')
        
        pdf.set_xy(76, stats_y + 5)
        pdf.cell(58, 6, f'إجمالي التكلفة: {total_cost:,.0f} ريال', 0, 0, 'C')
        
        pdf.set_xy(134, stats_y + 5)
        pdf.cell(56, 6, f'إجمالي الأيام: {total_days} يوم', 0, 0, 'L')
        
        # متوسطات
        avg_cost = total_cost / total_records if total_records > 0 else 0
        avg_days = total_days / total_records if total_records > 0 else 0
        
        pdf.set_xy(20, stats_y + 14)
        pdf.cell(80, 6, f'متوسط التكلفة: {avg_cost:,.0f} ريال', 0, 0, 'R')
        
        pdf.set_xy(110, stats_y + 14)
        pdf.cell(70, 6, f'متوسط المدة: {avg_days:.1f} يوم', 0, 0, 'L')
        
        pdf.set_y(stats_y + 30)
        pdf.set_text_color(0, 0, 0)
        
        # جدول السجلات
        pdf.ln(5)
        
        # تحديد عرض الأعمدة المحسن
        col_widths = [25, 20, 20, 15, 22, 30, 25, 23]
        headers = ['سبب الدخول', 'تاريخ الدخول', 'تاريخ الخروج', 'الأيام', 'حالة الإصلاح', 'اسم الورشة', 'الفني المسؤول', 'التكلفة (ريال)']
        
        # رأس الجدول مع تصميم احترافي
        header_y = pdf.get_y()
        
        # خلفية رأس الجدول
        pdf.set_fill_color_custom('secondary')
        pdf.rect(15, header_y, 180, 12, 'F')
        
        pdf.set_text_color(255, 255, 255)
        if pdf.fonts_available:
            pdf.set_font('Tajawal', 'B', 9)
        else:
            pdf.set_font('Arial', 'B', 9)
        
        # عناوين الأعمدة
        x_pos = 15
        pdf.set_y(header_y + 2)
        for i, header in enumerate(headers):
            pdf.set_x(x_pos)
            pdf.cell(col_widths[i], 8, header, 0, 0, 'C')
            x_pos += col_widths[i]
        
        pdf.ln(12)
        
        # بيانات الجدول
        pdf.set_text_color(0, 0, 0)
        
        # ترجمة القيم بدون رموز تعبيرية
        reason_map = {
            'maintenance': 'صيانة دورية', 
            'breakdown': 'عطل', 
            'accident': 'حادث'
        }
        status_map = {
            'in_progress': 'قيد التنفيذ', 
            'completed': 'تم الإصلاح', 
            'pending_approval': 'بانتظار الموافقة'
        }
        
        # تحديد ألوان الصفوف المتناوبة
        row_colors = [(248, 249, 250), (255, 255, 255)]
        
        for i, record in enumerate(workshop_records):
            row_y = pdf.get_y()
            
            # خلفية الصف
            color = row_colors[i % 2]
            pdf.set_fill_color(color[0], color[1], color[2])
            pdf.rect(15, row_y, 180, 10, 'F')
            
            # حدود خفيفة بين الصفوف
            if i > 0:
                pdf.set_draw_color(220, 220, 220)
                pdf.set_line_width(0.2)
                pdf.line(15, row_y, 195, row_y)
            
            if pdf.fonts_available:
                pdf.set_font('Amiri', '', 8)
            else:
                pdf.set_font('Arial', '', 8)
            
            # تحضير البيانات
            reason = reason_map.get(record.reason, record.reason) if hasattr(record, 'reason') and record.reason else 'غير محدد'
            entry_date = record.entry_date.strftime('%Y-%m-%d') if hasattr(record, 'entry_date') and record.entry_date else 'غير محدد'
            exit_date = record.exit_date.strftime('%Y-%m-%d') if hasattr(record, 'exit_date') and record.exit_date else '⏳ قيد الإصلاح'
            
            # حساب عدد الأيام
            days_count = 0
            if hasattr(record, 'entry_date') and record.entry_date:
                days_count = calculate_days_in_workshop(
                    record.entry_date, 
                    record.exit_date if hasattr(record, 'exit_date') and record.exit_date else None
                )
            
            status = status_map.get(record.repair_status, record.repair_status) if hasattr(record, 'repair_status') and record.repair_status else 'غير محدد'
            workshop_name = record.workshop_name if hasattr(record, 'workshop_name') and record.workshop_name else 'غير محدد'
            technician = record.technician_name if hasattr(record, 'technician_name') and record.technician_name else 'غير محدد'
            cost = f'{float(record.cost):,.0f}' if hasattr(record, 'cost') and record.cost else '0'
            
            # بيانات الصف
            row_data = [reason, entry_date, exit_date, str(days_count), status, workshop_name, technician, cost]
            
            # طباعة البيانات
            x_pos = 15
            pdf.set_y(row_y + 1)
            
            for j, data in enumerate(row_data):
                pdf.set_x(x_pos)
                
                # تلوين خاص لبعض الحقول
                if j == 0:  # سبب الدخول
                    if 'عطل' in data:
                        pdf.set_color('danger')
                    elif 'حادث' in data:
                        pdf.set_color('warning')
                    else:
                        pdf.set_color('success')
                elif j == 4:  # حالة الإصلاح
                    if 'تم' in data:
                        pdf.set_color('success')
                    elif 'قيد' in data:
                        pdf.set_color('warning')
                    else:
                        pdf.set_color('text_light')
                elif j == 7:  # التكلفة
                    pdf.set_color('primary')
                else:
                    pdf.set_color('text_dark')
                
                pdf.cell(col_widths[j], 8, data, 0, 0, 'C')
                x_pos += col_widths[j]
            
            pdf.ln(10)
            
            # فحص إذا كنا نحتاج صفحة جديدة
            if pdf.get_y() > 250:
                pdf.add_page()
                
                # إعادة رسم رأس الجدول في الصفحة الجديدة
                header_y = pdf.get_y()
                pdf.set_fill_color_custom('secondary')
                pdf.rect(15, header_y, 180, 12, 'F')
                
                pdf.set_text_color(255, 255, 255)
                if pdf.fonts_available:
                    pdf.set_font('Tajawal', 'B', 9)
                else:
                    pdf.set_font('Arial', 'B', 9)
                
                x_pos = 15
                pdf.set_y(header_y + 2)
                for k, header in enumerate(headers):
                    pdf.set_x(x_pos)
                    pdf.cell(col_widths[k], 8, header, 0, 0, 'C')
                    x_pos += col_widths[k]
                
                pdf.ln(12)
                pdf.set_text_color(0, 0, 0)
    
    # ===== تذييل الصفحة =====
    pdf.set_y(-35)
    
    # خط فاصل
    pdf.set_draw_color(41, 128, 185)  # اللون الأساسي
    pdf.set_line_width(1)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    
    pdf.ln(5)
    
    # معلومات النظام
    if pdf.fonts_available:
        pdf.set_font('Tajawal', 'B', 10)
    else:
        pdf.set_font('Arial', 'B', 10)
    pdf.set_color('primary')
    pdf.cell(0, 6, 'تم إنشاء هذا التقرير بواسطة نُظم - نظام إدارة المركبات والموظفين', 0, 1, 'C')
    
    if pdf.fonts_available:
        pdf.set_font('Amiri', '', 9)
    else:
        pdf.set_font('Arial', '', 9)
    pdf.set_color('text_light')
    pdf.cell(0, 5, f'تاريخ ووقت الإنشاء: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', 0, 1, 'C')
    
    pdf.cell(0, 4, 'نُظم © 2025 - جميع الحقوق محفوظة', 0, 0, 'C')
    
    # حفظ PDF مع معالجة محسنة للأخطاء
    try:
        # حفظ PDF كسلسلة بايتات
        pdf_content = pdf.output(dest='S')
        
        # في FPDF2، نحتاج للتعامل مع أنواع مختلفة من المخرجات
        if isinstance(pdf_content, str):
            # إذا كان نص، نحوله إلى بايتات
            pdf_content = pdf_content.encode('latin-1')
        elif isinstance(pdf_content, bytearray):
            # إذا كان bytearray، نحوله إلى bytes
            pdf_content = bytes(pdf_content)
        elif isinstance(pdf_content, bytes):
            # إذا كان بالفعل bytes، لا نحتاج تحويل
            pass
        else:
            # حالة غير متوقعة - نحاول التحويل إلى bytes
            pdf_content = bytes(pdf_content)
        
        # وضع المحتوى في بفر الذاكرة
        pdf_buffer = io.BytesIO(pdf_content)
        pdf_buffer.seek(0)
        
        import logging
        logging.info(f"تم إنشاء PDF بنجاح بحجم: {len(pdf_content)} بايت")
        
        return pdf_buffer
        
    except Exception as e:
        import logging, traceback
        logging.error(f"خطأ عند إنشاء PDF: {str(e)}")
        logging.error(traceback.format_exc())
        
        # إذا فشلت الطريقة الأولى، نستخدم ملفًا مؤقتًا
        import tempfile
        
        fd, temp_path = tempfile.mkstemp(suffix='.pdf')
        os.close(fd)
        
        try:
            # حفظ إلى ملف مؤقت
            pdf.output(temp_path)
            
            # قراءة المحتوى
            with open(temp_path, 'rb') as f:
                pdf_content = f.read()
            
            pdf_buffer = io.BytesIO(pdf_content)
            pdf_buffer.seek(0)
            
            return pdf_buffer
        
        finally:
            # تأكد من حذف الملف المؤقت حتى في حالة حدوث خطأ
            if os.path.exists(temp_path):
                os.unlink(temp_path)