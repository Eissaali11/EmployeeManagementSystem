"""
وحدة إنشاء ملفات PDF للغة العربية باستخدام ReportLab
تتعامل مع إعادة تشكيل النص العربي وعرضه بشكل صحيح من اليمين إلى اليسار
"""
import io
import os
from datetime import datetime

import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib.units import mm

def get_arabic_text(text):
    """
    تحويل النص العربي ليعرض بشكل صحيح في PDF
    
    Args:
        text: النص الذي سيتم تحويله
        
    Returns:
        النص المحول للعرض الصحيح في PDF
    """
    if text is None:
        return ""
    
    try:
        # تحويل أي نوع بيانات إلى نص
        text = str(text)
        # إعادة تشكيل النص العربي
        reshaped_text = arabic_reshaper.reshape(text)
        # تطبيق خوارزمية BiDi للعرض من اليمين إلى اليسار
        bidi_text = get_display(reshaped_text)
        return bidi_text
    except Exception as e:
        import logging
        logging.error(f"خطأ في معالجة النص العربي: {str(e)}")
        return str(text)

def register_arabic_fonts():
    """
    تسجيل الخطوط العربية المطلوبة للاستخدام في ReportLab
    """
    try:
        import os
        
        # استخدام المسار المطلق بدون Flask
        fonts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'fonts')
        
        # تسجيل الخطوط
        pdfmetrics.registerFont(TTFont('Amiri', os.path.join(fonts_dir, 'Amiri-Regular.ttf')))
        pdfmetrics.registerFont(TTFont('Amiri-Bold', os.path.join(fonts_dir, 'Amiri-Bold.ttf')))
        pdfmetrics.registerFont(TTFont('Tajawal', os.path.join(fonts_dir, 'Tajawal-Regular.ttf')))
        pdfmetrics.registerFont(TTFont('Tajawal-Bold', os.path.join(fonts_dir, 'Tajawal-Bold.ttf')))
    except Exception as e:
        import logging
        logging.error(f"خطأ في تسجيل الخطوط العربية: {str(e)}")
        # طباعة مسار الخطوط للمساعدة في تصحيح الأخطاء
        import os
        fonts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'fonts')
        logging.error(f"مسار الخطوط: {fonts_dir}")
        logging.error(f"قائمة الملفات: {os.listdir(fonts_dir) if os.path.exists(fonts_dir) else 'المسار غير موجود'}")
        raise

def create_styles():
    """
    إنشاء أنماط النصوص للاستخدام في المستند
    
    Returns:
        قاموس يحتوي على أنماط النصوص
    """
    styles = getSampleStyleSheet()
    
    # إضافة نمط للنصوص المحاذاة لليمين
    styles.add(ParagraphStyle(
        name='RightAlign',
        fontName='Amiri',
        fontSize=11,
        alignment=2,  # محاذاة لليمين
        leading=14
    ))
    
    # إضافة نمط للعناوين المحاذاة للوسط
    styles.add(ParagraphStyle(
        name='CenterAlign',
        fontName='Tajawal-Bold',
        fontSize=16,
        alignment=1,  # توسيط
        spaceAfter=10,
        leading=20
    ))
    
    # إضافة نمط للعناوين الفرعية
    styles.add(ParagraphStyle(
        name='SubHeading',
        fontName='Tajawal-Bold',
        fontSize=12,
        alignment=2,  # محاذاة لليمين
        textColor=colors.darkblue,
        leading=16
    ))
    
    # إضافة نمط للنص العادي
    styles.add(ParagraphStyle(
        name='ArabicNormal',
        fontName='Amiri',
        fontSize=10,
        alignment=2,  # محاذاة لليمين
        leading=14
    ))
    
    return styles

def add_page_footer(canvas, doc):
    """
    إضافة معلومات في تذييل الصفحة
    
    Args:
        canvas: كائن الرسم
        doc: المستند
    """
    canvas.saveState()
    canvas.setFont('Amiri', 8)
    canvas.setFillColor(colors.grey)
    
    # خط فاصل
    canvas.setStrokeColor(colors.darkblue)
    canvas.setLineWidth(0.5)
    canvas.line(30, 40, A4[0] - 30, 40)
    
    # معلومات التذييل
    footer_text = get_arabic_text(f'تم إنشاء هذا التقرير بواسطة نُظم - نظام إدارة المركبات والموظفين')
    canvas.drawCentredString(A4[0] / 2, 30, footer_text)
    
    # التاريخ
    date_text = get_arabic_text(f'تاريخ الإنشاء: {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    canvas.drawCentredString(A4[0] / 2, 20, date_text)
    
    # رقم الصفحة
    page_num = get_arabic_text(f'صفحة {doc.page}')
    canvas.drawRightString(A4[0] - 30, 20, page_num)
    
    canvas.restoreState()

def add_page_header(canvas, doc, title):
    """
    إضافة معلومات في رأس الصفحة
    
    Args:
        canvas: كائن الرسم
        doc: المستند
        title: عنوان المستند
    """
    canvas.saveState()
    
    # شعار النظام (إذا وجد)
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(base_dir, 'static', 'images', 'logo.png')
        if os.path.exists(logo_path):
            canvas.drawImage(logo_path, 30, A4[1] - 80, width=50, height=50)
    except:
        pass
    
    # عنوان التطبيق
    canvas.setFont('Tajawal-Bold', 16)
    canvas.setFillColor(colors.darkblue)
    app_title = get_arabic_text('نُظم - نظام إدارة المركبات والموظفين')
    canvas.drawCentredString(A4[0] / 2, A4[1] - 50, app_title)
    
    # عنوان المستند
    canvas.setFont('Tajawal-Bold', 14)
    canvas.setFillColor(colors.black)
    doc_title = get_arabic_text(title)
    canvas.drawCentredString(A4[0] / 2, A4[1] - 70, doc_title)
    
    # خط فاصل
    canvas.setStrokeColor(colors.darkblue)
    canvas.setLineWidth(1)
    canvas.line(30, A4[1] - 85, A4[0] - 30, A4[1] - 85)
    
    canvas.restoreState()

def calculate_days(start_date, end_date=None):
    """
    حساب عدد الأيام بين تاريخين
    
    Args:
        start_date: تاريخ البداية
        end_date: تاريخ النهاية (إذا كان None، يستخدم تاريخ اليوم)
        
    Returns:
        عدد الأيام
    """
    if not start_date:
        return 0
    
    end = end_date if end_date else datetime.now().date()
    
    if isinstance(start_date, datetime):
        start_date = start_date.date()
    if isinstance(end, datetime):
        end = end.date()
    
    try:
        days = (end - start_date).days
        return max(0, days)
    except:
        return 0

def generate_workshop_report_pdf(vehicle, workshop_records):
    """
    إنشاء تقرير سجلات الورشة بصيغة PDF
    
    Args:
        vehicle: كائن المركبة
        workshop_records: قائمة بسجلات الورشة
        
    Returns:
        BytesIO: كائن يحتوي على ملف PDF
    """
    # إنشاء بفر الذاكرة لحفظ الملف
    pdf_buffer = io.BytesIO()
    
    # تسجيل الخطوط العربية
    register_arabic_fonts()
    
    # إنشاء المستند
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        title="تقرير سجلات الورشة",
        author="نُظم"
    )
    
    # إنشاء أنماط النصوص
    styles = create_styles()
    
    # إنشاء عناصر المستند
    elements = []
    
    # إضافة مسافة في بداية المستند
    elements.append(Spacer(1, 20))
    
    # معلومات المركبة
    vehicle_info = [
        [get_arabic_text("معلومات المركبة"), ""],
        [get_arabic_text("رقم اللوحة:"), get_arabic_text(vehicle.plate_number)],
        [get_arabic_text("الماركة:"), get_arabic_text(vehicle.make)],
        [get_arabic_text("الموديل:"), get_arabic_text(vehicle.model)],
        [get_arabic_text("سنة الصنع:"), str(vehicle.year) if vehicle.year else ""]
    ]
    
    vehicle_table = Table(vehicle_info, colWidths=[120, 300])
    vehicle_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Amiri'),
        ('FONT', (0, 0), (0, 0), 'Tajawal-Bold'),
        ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.darkblue),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.grey),
        ('SPAN', (0, 0), (1, 0)),  # دمج خلايا العنوان
    ]))
    elements.append(vehicle_table)
    elements.append(Spacer(1, 20))
    
    # ترجمة حالات المركبة
    reason_map = {'maintenance': 'صيانة دورية', 'breakdown': 'عطل', 'accident': 'حادث'}
    status_map = {'in_progress': 'قيد التنفيذ', 'completed': 'تم الإصلاح', 'pending_approval': 'بانتظار الموافقة'}
    
    # عنوان جدول سجلات الورشة
    elements.append(Paragraph(get_arabic_text("سجلات دخول الورشة"), styles['SubHeading']))
    elements.append(Spacer(1, 10))
    
    # جدول سجلات الورشة
    workshop_data = [
        [
            get_arabic_text("سبب الزيارة"),
            get_arabic_text("تاريخ الدخول"),
            get_arabic_text("تاريخ الخروج"),
            get_arabic_text("عدد الأيام"),
            get_arabic_text("الحالة"),
            get_arabic_text("الورشة"),
            get_arabic_text("التكلفة")
        ]
    ]
    
    # إحصائيات
    total_days = 0
    total_cost = 0
    
    # ملء جدول الورشة
    for record in workshop_records:
        # حساب عدد الأيام
        days_count = "—"
        if hasattr(record, 'entry_date') and record.entry_date:
            days = calculate_days(
                record.entry_date, 
                record.exit_date if hasattr(record, 'exit_date') and record.exit_date else None
            )
            days_count = str(days) + " يوم" if days > 0 else "—"
            total_days += days
        
        # إجمالي التكلفة
        if hasattr(record, 'cost') and record.cost:
            total_cost += record.cost
        
        # تجهيز البيانات للعرض
        reason = reason_map.get(record.reason, record.reason) if hasattr(record, 'reason') and record.reason else ''
        entry_date = record.entry_date.strftime('%Y-%m-%d') if hasattr(record, 'entry_date') and record.entry_date else ''
        exit_date = record.exit_date.strftime('%Y-%m-%d') if hasattr(record, 'exit_date') and record.exit_date else 'قيد الإصلاح'
        status = status_map.get(record.repair_status, record.repair_status) if hasattr(record, 'repair_status') and record.repair_status else ''
        workshop_name = record.workshop_name if hasattr(record, 'workshop_name') and record.workshop_name else ''
        cost = f"{record.cost:,.2f}" if hasattr(record, 'cost') and record.cost else ''
        
        row = [
            get_arabic_text(reason),
            get_arabic_text(entry_date),
            get_arabic_text(exit_date),
            get_arabic_text(days_count),
            get_arabic_text(status),
            get_arabic_text(workshop_name),
            get_arabic_text(cost)
        ]
        workshop_data.append(row)
    
    # تعديل عرض الأعمدة
    col_widths = [70, 60, 60, 50, 70, 90, 60]
    workshop_table = Table(workshop_data, colWidths=col_widths)
    
    # تنسيق الجدول
    row_colors = [(0.94, 0.94, 0.94), (1, 1, 1)]  # رمادي فاتح وأبيض
    table_style = [
        ('FONT', (0, 0), (-1, -1), 'Amiri'),
        ('FONT', (0, 0), (-1, 0), 'Tajawal-Bold'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.darkblue)
    ]
    
    # إضافة ألوان الصفوف المتناوبة
    for i in range(1, len(workshop_data)):
        bg_color = row_colors[(i - 1) % 2]
        table_style.append(('BACKGROUND', (0, i), (-1, i), bg_color))
        
        # تمييز السجلات "قيد التنفيذ" باللون الأحمر
        if (hasattr(workshop_records[i-1], 'repair_status') and 
            workshop_records[i-1].repair_status == 'in_progress'):
            table_style.append(('TEXTCOLOR', (0, i), (-1, i), colors.darkred))
    
    workshop_table.setStyle(TableStyle(table_style))
    elements.append(workshop_table)
    elements.append(Spacer(1, 20))
    
    # ملخص الإحصائيات
    stats_data = [
        [get_arabic_text("الإحصائيات"), ""],
        [get_arabic_text("عدد مرات دخول الورشة:"), get_arabic_text(f"{len(workshop_records)}")],
        [get_arabic_text("إجمالي الأيام في الورشة:"), get_arabic_text(f"{total_days} يوم")],
        [get_arabic_text("متوسط المدة لكل زيارة:"), 
         get_arabic_text(f"{total_days/len(workshop_records):.1f} يوم" if len(workshop_records) > 0 else "0 يوم")],
        [get_arabic_text("التكلفة الإجمالية:"), get_arabic_text(f"{total_cost:,.2f} ريال")],
        [get_arabic_text("متوسط التكلفة لكل زيارة:"), 
         get_arabic_text(f"{total_cost/len(workshop_records):,.2f} ريال" if len(workshop_records) > 0 else "0 ريال")]
    ]
    
    stats_table = Table(stats_data, colWidths=[150, 270])
    stats_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Amiri'),
        ('FONT', (0, 0), (0, 0), 'Tajawal-Bold'),
        ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.darkblue),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.grey),
        ('SPAN', (0, 0), (1, 0)),  # دمج خلايا العنوان
    ]))
    elements.append(stats_table)
    
    # إنشاء دالة مخصصة للصفحة الأولى
    def first_page(canvas, doc):
        add_page_header(canvas, doc, "تقرير سجلات الورشة")
        add_page_footer(canvas, doc)
    
    # إنشاء دالة للصفحات التالية
    def later_pages(canvas, doc):
        add_page_header(canvas, doc, "تقرير سجلات الورشة")
        add_page_footer(canvas, doc)
    
    # بناء المستند
    doc.build(
        elements,
        onFirstPage=first_page,
        onLaterPages=later_pages
    )
    
    # العودة إلى بداية البفر وإرجاعه
    pdf_buffer.seek(0)
    return pdf_buffer