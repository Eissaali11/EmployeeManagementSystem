"""
وحدة إنشاء تقارير PDF باستخدام FPDF2 مع دعم كامل للغة العربية
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

class ArabicPDF(FPDF):
    """فئة PDF معدلة لدعم اللغة العربية"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_auto_page_break(auto=True, margin=15)
        # تسجيل الخطوط العربية
        font_path = os.path.join(PROJECT_DIR, 'static', 'fonts')
        
        # إضافة خط Tajawal (خط عصري للعناوين)
        self.add_font('Tajawal', '', os.path.join(font_path, 'Tajawal-Regular.ttf'), uni=True)
        self.add_font('Tajawal', 'B', os.path.join(font_path, 'Tajawal-Bold.ttf'), uni=True)
        
        # إضافة خط Amiri (خط تقليدي للنصوص)
        self.add_font('Amiri', '', os.path.join(font_path, 'Amiri-Regular.ttf'), uni=True)
        self.add_font('Amiri', 'B', os.path.join(font_path, 'Amiri-Bold.ttf'), uni=True)
    
    def arabic_text(self, txt):
        """إعادة تشكيل النص العربي وتحويله ليعرض بشكل صحيح"""
        if txt is None or txt == '':
            return ''
        
        # تخطي المعالجة لغير النصوص
        if not isinstance(txt, str):
            return str(txt)
        
        # تخطي معالجة الأرقام والتواريخ
        if txt.replace('.', '', 1).replace(',', '', 1).isdigit() or all(c.isdigit() or c in '/-:' for c in txt):
            return txt
        
        # إعادة تشكيل النص العربي وتحويله إلى النمط المناسب للعرض
        reshaped_text = arabic_reshaper.reshape(txt)
        bidi_text = get_display(reshaped_text)
        return bidi_text
    
    def cell(self, w=0, h=0, txt='', border=0, ln=0, align='', fill=False, link=''):
        """تجاوز دالة الخلية لدعم النص العربي"""
        # نحول النص العربي ونستخدم الواجهة القديمة للمكتبة
        arabic_txt = self.arabic_text(txt)
        super().cell(w, h, arabic_txt, border, ln, align, fill, link)
    
    def multi_cell(self, w=0, h=0, txt='', border=0, align='', fill=False):
        """تجاوز دالة الخلايا المتعددة لدعم النص العربي"""
        # نحول النص العربي ونستخدم الواجهة القديمة للمكتبة
        arabic_txt = self.arabic_text(txt)
        super().multi_cell(w, h, arabic_txt, border, align, fill)


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
    إنشاء تقرير سجلات الورشة للمركبة باستخدام FPDF
    
    Args:
        vehicle: كائن المركبة
        workshop_records: قائمة بسجلات الورشة
    
    Returns:
        BytesIO: كائن بايت يحتوي على ملف PDF
    """
    # إنشاء كائن PDF مع دعم اللغة العربية
    pdf = ArabicPDF(orientation='P', unit='mm', format='A4')
    pdf.set_title('تقرير سجلات الورشة')
    pdf.set_author('نُظم - نظام إدارة المركبات')
    
    # إضافة صفحة جديدة
    pdf.add_page()
    
    # إضافة الشعار في رأس الصفحة (البحث في عدة مواقع محتملة)
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
        # إضافة الشعار في أعلى الصفحة
        pdf.image(logo_path, x=10, y=10, w=30)
    else:
        # إذا لم نجد شعارًا، نرسم شعار نصي بديل
        pdf.set_fill_color(30, 60, 114)  # لون أزرق غامق
        pdf.set_xy(10, 10)
        pdf.cell(30, 30, '', 0, 0, 'C', True)  # رسم دائرة زرقاء
        pdf.set_text_color(255, 255, 255)  # لون أبيض للنص
        pdf.set_font('Amiri', 'B', 16)
        pdf.set_xy(10, 20)
        pdf.cell(30, 10, 'نُظم', 0, 0, 'C')
    
    # إعداد الخط الافتراضي - استخدام Tajawal للعناوين
    pdf.set_font('Tajawal', 'B', 18)
    
    # عنوان التقرير (مع تعديل الموضع إذا كان هناك شعار)
    pdf.set_y(20)
    pdf.cell(0, 10, 'تقرير سجلات الورشة', 0, 1, 'C')
    
    # معلومات السيارة
    pdf.set_font('Tajawal', 'B', 14)
    pdf.cell(0, 10, f'{vehicle.make} {vehicle.model} - {vehicle.plate_number}', 0, 1, 'C')
    
    # تاريخ التقرير
    pdf.set_font('Amiri', '', 10)  # استخدام Amiri للنصوص العادية
    pdf.cell(0, 5, f'تاريخ التقرير: {datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 1, 'C')
    pdf.ln(5)
    
    # معلومات المركبة
    pdf.set_font('Tajawal', 'B', 14)  # استخدام Tajawal للعناوين الفرعية
    pdf.cell(0, 10, 'معلومات المركبة', 0, 1, 'R')
    
    pdf.set_font('Amiri', '', 12)
    # جدول معلومات المركبة
    vehicle_info = [
        ['رقم اللوحة:', vehicle.plate_number],
        ['الماركة:', vehicle.make],
        ['الموديل:', vehicle.model],
        ['سنة الصنع:', str(vehicle.year) if hasattr(vehicle, 'year') and vehicle.year else '']
    ]
    
    # إضافة معلومات إضافية إذا كانت متوفرة
    if hasattr(vehicle, 'vin') and vehicle.vin:
        vehicle_info.append(['رقم الهيكل:', vehicle.vin])
    
    if hasattr(vehicle, 'odometer') and vehicle.odometer:
        vehicle_info.append(['قراءة العداد:', f'{vehicle.odometer} كم'])
    
    # رسم جدول معلومات المركبة
    for info in vehicle_info:
        pdf.set_font('Amiri', 'B', 12)
        pdf.cell(150, 8, '', 0, 0)
        pdf.cell(25, 8, info[0], 0, 0, 'R')
        pdf.set_font('Amiri', '', 12)
        pdf.cell(15, 8, info[1], 0, 1, 'R')
    
    pdf.ln(5)
    
    # سجلات الورشة
    pdf.set_font('Amiri', 'B', 14)
    pdf.cell(0, 10, 'سجلات الورشة', 0, 1, 'R')
    
    # التحقق من وجود سجلات
    if not workshop_records or len(workshop_records) == 0:
        pdf.set_font('Amiri', '', 12)
        pdf.cell(0, 10, 'لا توجد سجلات ورشة لهذه المركبة', 0, 1, 'C')
    else:
        # عنوان جدول سجلات الورشة
        pdf.set_font('Tajawal', 'B', 14)
        pdf.cell(0, 10, 'سجلات الورشة', 0, 1, 'R')
        pdf.ln(2)
        
        # إنشاء جدول سجلات الورشة - استخدام Tajawal للعناوين
        pdf.set_font('Tajawal', 'B', 10)
        
        # تحديد عرض الأعمدة (إضافة عمود لعدد الأيام)
        col_width = [30, 20, 20, 15, 20, 20, 25, 20]
        
        # عناوين الأعمدة (إضافة عمود لعدد الأيام)
        headers = ['سبب الدخول', 'تاريخ الدخول', 'تاريخ الخروج', 'عدد الأيام', 'حالة الإصلاح', 'اسم الورشة', 'الفني المسؤول', 'التكلفة (ريال)']
        
        # تنسيق رأس الجدول بألوان جذابة
        pdf.set_fill_color(30, 60, 114)  # لون أزرق غامق للخلفية
        pdf.set_text_color(255, 255, 255)  # نص أبيض
        
        # الصف الأول (الرأس)
        for i, header in enumerate(headers):
            pdf.cell(col_width[i], 10, header, 1, 0, 'C', True)
        pdf.ln()
        
        # إعادة لون النص إلى الأسود للبيانات
        pdf.set_text_color(0, 0, 0)
        
        # ترجمة القيم
        reason_map = {'maintenance': 'صيانة دورية', 'breakdown': 'عطل', 'accident': 'حادث'}
        status_map = {'in_progress': 'قيد التنفيذ', 'completed': 'تم الإصلاح', 'pending_approval': 'بانتظار الموافقة'}
        
        # بيانات الجدول
        pdf.set_font('Amiri', '', 10)
        
        # تحديد ألوان الصفوف المتناوبة للجدول
        row_colors = [(240, 240, 240), (255, 255, 255)]  # رمادي فاتح وأبيض
        
        for i, record in enumerate(workshop_records):
            # تطبيق لون خلفية متناوب للصفوف
            row_color = row_colors[i % 2]
            pdf.set_fill_color(row_color[0], row_color[1], row_color[2])
            
            # تحويل البيانات إلى سلاسل نصية وتطبيق الخريطة عند الحاجة
            reason = reason_map.get(record.reason, record.reason) if hasattr(record, 'reason') and record.reason else ''
            entry_date = record.entry_date.strftime('%Y-%m-%d') if hasattr(record, 'entry_date') and record.entry_date else ''
            exit_date = record.exit_date.strftime('%Y-%m-%d') if hasattr(record, 'exit_date') and record.exit_date else 'قيد الإصلاح'
            
            # حساب عدد الأيام في الورشة
            days_count = "—"
            if hasattr(record, 'entry_date') and record.entry_date:
                days = calculate_days_in_workshop(
                    record.entry_date, 
                    record.exit_date if hasattr(record, 'exit_date') and record.exit_date else None
                )
                days_count = str(days) + " يوم" if days > 0 else "—"
            
            status = status_map.get(record.repair_status, record.repair_status) if hasattr(record, 'repair_status') and record.repair_status else ''
            workshop_name = record.workshop_name if hasattr(record, 'workshop_name') and record.workshop_name else ''
            technician = record.technician_name if hasattr(record, 'technician_name') and record.technician_name else ''
            cost = f"{record.cost:,.2f}" if hasattr(record, 'cost') and record.cost else ''
            
            # تمييز حالة السجلات المفتوحة (قيد الإصلاح) بلون مختلف للنص
            if hasattr(record, 'repair_status') and record.repair_status == 'in_progress':
                pdf.set_text_color(180, 40, 40)  # لون أحمر داكن للسجلات المفتوحة
            else:
                pdf.set_text_color(0, 0, 0)  # إعادة لون النص إلى الأسود للبيانات الأخرى
            
            # رسم الخلايا (إضافة خلية لعدد الأيام)
            pdf.cell(col_width[0], 8, reason, 1, 0, 'C', True)
            pdf.cell(col_width[1], 8, entry_date, 1, 0, 'C', True)
            pdf.cell(col_width[2], 8, exit_date, 1, 0, 'C', True)
            pdf.cell(col_width[3], 8, days_count, 1, 0, 'C', True)
            pdf.cell(col_width[4], 8, status, 1, 0, 'C', True)
            pdf.cell(col_width[5], 8, workshop_name, 1, 0, 'C', True)
            pdf.cell(col_width[6], 8, technician, 1, 0, 'C', True)
            pdf.cell(col_width[7], 8, cost, 1, 0, 'C', True)
            pdf.ln()
            
        # إعادة لون النص إلى الأسود بعد الانتهاء من الجدول
        pdf.set_text_color(0, 0, 0)
        
        # إحصائيات
        pdf.ln(10)
        
        # استخدام خط Tajawal للعناوين
        pdf.set_font('Tajawal', 'B', 14)
        pdf.cell(0, 10, 'ملخص التكاليف والمدة', 0, 1, 'R')
        
        # حساب الإحصائيات
        total_cost = sum(record.cost or 0 for record in workshop_records)
        # حساب إجمالي الأيام في الورشة لجميع السجلات
        total_days = sum(calculate_days_in_workshop(
            record.entry_date, 
            record.exit_date if hasattr(record, 'exit_date') and record.exit_date else None
        ) for record in workshop_records if hasattr(record, 'entry_date') and record.entry_date)
        
        # عرض الإحصائيات في جدول
        pdf.set_font('Amiri', '', 12)
        stats_info = [
            ['عدد مرات دخول الورشة:', f'{len(workshop_records)}'],
            ['إجمالي الأيام في الورشة:', f'{total_days} يوم'],
            ['متوسط المدة لكل زيارة:', f'{total_days/len(workshop_records):.1f} يوم' if len(workshop_records) > 0 else '0 يوم'],
            ['التكلفة الإجمالية:', f'{total_cost:,.2f} ريال'],
            ['متوسط التكلفة لكل زيارة:', f'{total_cost/len(workshop_records):,.2f} ريال' if len(workshop_records) > 0 else '0 ريال']
        ]
        
        # رسم جدول الإحصائيات
        for info in stats_info:
            pdf.set_font('Tajawal', 'B', 12)
            pdf.cell(40, 8, info[0], 0, 0, 'R')
            pdf.set_font('Amiri', '', 12)
            pdf.cell(0, 8, info[1], 0, 1, 'R')
    
    # تذييل الصفحة مع تصميم محسن
    pdf.set_y(-25)
    pdf.set_draw_color(30, 60, 114)  # لون أزرق غامق
    pdf.set_line_width(0.5)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    
    pdf.set_font('Tajawal', 'B', 8)
    pdf.set_y(-20)
    pdf.cell(0, 10, f'تم إنشاء هذا التقرير بواسطة نُظم - نظام إدارة المركبات والموظفين', 0, 1, 'C')
    
    pdf.set_font('Amiri', '', 8)
    pdf.cell(0, 5, f'تاريخ الإنشاء: {datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 0, 'C')
    
    # تعديل طريقة حفظ الملف لاستخدام الطريقة القياسية من FPDF
    try:
        # حفظ PDF كسلسلة بايتات
        pdf_content = pdf.output(dest='S')
        
        # في FPDF2، يجب تحويل المخرجات إلى بايتات
        if not isinstance(pdf_content, bytes):
            pdf_content = pdf_content.encode('latin-1')
        
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