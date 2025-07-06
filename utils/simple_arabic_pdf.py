"""
وحدة إنشاء ملفات PDF للغة العربية بطريقة بسيطة وفعالة
تعتمد على ReportLab مع إضافة دعم كامل للغة العربية
"""

import io
import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
import arabic_reshaper
from bidi.algorithm import get_display

# تسجيل الخطوط العربية
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS_DIR = os.path.join(BASE_DIR, 'static', 'fonts')

# تسجيل خط beIN-Normal والخطوط الاحتياطية
try:
    pdfmetrics.registerFont(TTFont('beIN-Normal', os.path.join(FONTS_DIR, 'beIN-Normal.ttf')))
    pdfmetrics.registerFont(TTFont('Amiri', os.path.join(FONTS_DIR, 'Amiri-Regular.ttf')))
    pdfmetrics.registerFont(TTFont('Amiri-Bold', os.path.join(FONTS_DIR, 'Amiri-Bold.ttf')))
    pdfmetrics.registerFont(TTFont('Tajawal', os.path.join(FONTS_DIR, 'Tajawal-Regular.ttf')))
    pdfmetrics.registerFont(TTFont('Tajawal-Bold', os.path.join(FONTS_DIR, 'Tajawal-Bold.ttf')))
except Exception as e:
    import logging
    logging.error(f"خطأ في تحميل الخطوط: {str(e)}")

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
        # إعادة تشكيل النص العربي وترتيبه بشكل صحيح
        reshaped_text = arabic_reshaper.reshape(str(text))
        bidi_text = get_display(reshaped_text)
        return bidi_text
    except Exception as e:
        import logging
        logging.error(f"خطأ في تحويل النص العربي: {str(e)}")
        return str(text)

def generate_workshop_report_pdf(vehicle, workshop_records):
    """
    إنشاء تقرير سجلات الورشة للمركبة باستخدام ReportLab
    
    Args:
        vehicle: كائن المركبة
        workshop_records: قائمة بسجلات الورشة
    
    Returns:
        BytesIO: كائن بايت يحتوي على ملف PDF
    """
    pdf_buffer = io.BytesIO()
    
    # إنشاء مستند PDF
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        title=get_arabic_text("تقرير سجلات الورشة"),
        author=get_arabic_text("نُظم - نظام إدارة المركبات"),
        topMargin=30,
        bottomMargin=30
    )
    
    # قائمة العناصر للإضافة إلى PDF
    elements = []
    
    # أنماط النصوص
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='RightAlign',
        fontName='beIN-Normal',
        fontSize=14,
        alignment=2  # محاذاة لليمين
    ))
    styles.add(ParagraphStyle(
        name='RightAlignNormal',
        fontName='beIN-Normal',
        fontSize=12,
        alignment=2
    ))
    styles.add(ParagraphStyle(
        name='CenterAlign',
        fontName='beIN-Normal',
        fontSize=16,
        alignment=1
    ))
    styles.add(ParagraphStyle(
        name='Footer',
        fontName='beIN-Normal',
        fontSize=8,
        alignment=1
    ))
    
    # إضافة الشعار إذا كان متاحًا
    logo_path = os.path.join(BASE_DIR, 'static', 'img', 'logo.png')
    if os.path.exists(logo_path):
        img = Image(logo_path, width=100, height=50)
        img.hAlign = 'CENTER'
        elements.append(img)
        elements.append(Spacer(1, 10))
    
    # العنوان
    elements.append(Paragraph(get_arabic_text("تقرير سجلات الورشة"), styles['CenterAlign']))
    elements.append(Spacer(1, 10))
    
    # بيانات المركبة
    vehicle_info = [
        [get_arabic_text("معلومات المركبة"), ""],
        [get_arabic_text("رقم اللوحة:"), get_arabic_text(vehicle.plate_number if hasattr(vehicle, 'plate_number') else "")],
        [get_arabic_text("الماركة:"), get_arabic_text(vehicle.make if hasattr(vehicle, 'make') else "")],
        [get_arabic_text("الموديل:"), get_arabic_text(vehicle.model if hasattr(vehicle, 'model') else "")]
    ]
    
    vehicle_table = Table(vehicle_info, colWidths=[120, 300])
    vehicle_table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'beIN-Normal'),
        ('FONT', (0, 0), (0, 0), 'beIN-Normal'),
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
    
    # جدول سجلات الورشة
    table_data = [
        [
            get_arabic_text("سبب الزيارة"),
            get_arabic_text("تاريخ الدخول"),
            get_arabic_text("تاريخ الخروج"),
            get_arabic_text("عدد الأيام"),
            get_arabic_text("الحالة"),
            get_arabic_text("اسم الورشة"),
            get_arabic_text("الفني المسؤول"),
            get_arabic_text("التكلفة")
        ]
    ]
    
    # ترجمة القيم
    reason_map = {'maintenance': 'صيانة دورية', 'breakdown': 'عطل', 'accident': 'حادث'}
    status_map = {'in_progress': 'قيد التنفيذ', 'completed': 'تم الإصلاح', 'pending_approval': 'بانتظار الموافقة'}
    
    # إضافة البيانات وحساب الإحصائيات
    total_days = 0
    total_cost = 0
    
    for record in workshop_records:
        # حساب عدد الأيام في الورشة
        days_count = "—"
        if hasattr(record, 'entry_date') and record.entry_date:
            from utils.fpdf_arabic_report import calculate_days_in_workshop
            days = calculate_days_in_workshop(
                record.entry_date, 
                record.exit_date if hasattr(record, 'exit_date') and record.exit_date else None
            )
            days_count = str(days) + " يوم" if days > 0 else "—"
            total_days += days
        
        # تجميع إجمالي التكلفة
        if hasattr(record, 'cost') and record.cost:
            total_cost += record.cost
        
        # تحويل البيانات إلى سلاسل نصية
        reason = reason_map.get(record.reason, record.reason) if hasattr(record, 'reason') and record.reason else ''
        entry_date = record.entry_date.strftime('%Y-%m-%d') if hasattr(record, 'entry_date') and record.entry_date else ''
        exit_date = record.exit_date.strftime('%Y-%m-%d') if hasattr(record, 'exit_date') and record.exit_date else 'قيد الإصلاح'
        status = status_map.get(record.repair_status, record.repair_status) if hasattr(record, 'repair_status') and record.repair_status else ''
        workshop_name = record.workshop_name if hasattr(record, 'workshop_name') and record.workshop_name else ''
        technician = record.technician_name if hasattr(record, 'technician_name') and record.technician_name else ''
        cost = f"{record.cost:,.2f}" if hasattr(record, 'cost') and record.cost else ''
        
        row = [
            get_arabic_text(reason),
            get_arabic_text(entry_date),
            get_arabic_text(exit_date),
            get_arabic_text(days_count),
            get_arabic_text(status),
            get_arabic_text(workshop_name),
            get_arabic_text(technician),
            get_arabic_text(cost)
        ]
        table_data.append(row)
    
    # إنشاء الجدول بعرض مناسب
    col_widths = [70, 50, 50, 40, 60, 70, 70, 50]  # عرض الأعمدة
    workshop_table = Table(table_data, colWidths=col_widths)
    
    # أنماط الجدول
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
    for i in range(1, len(table_data)):
        bg_color = row_colors[(i - 1) % 2]
        table_style.append(('BACKGROUND', (0, i), (-1, i), bg_color))
        
        # تلوين السجلات التي في حالة "قيد التنفيذ" باللون الأحمر
        if (hasattr(workshop_records[i-1], 'repair_status') and 
            workshop_records[i-1].repair_status == 'in_progress'):
            table_style.append(('TEXTCOLOR', (0, i), (-1, i), colors.darkred))
    
    workshop_table.setStyle(TableStyle(table_style))
    elements.append(workshop_table)
    elements.append(Spacer(1, 20))
    
    # جدول الإحصائيات
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
    
    # بناء المستند
    try:
        doc.build(
            elements,
            onFirstPage=lambda canvas, doc: add_page_number(canvas, doc),
            onLaterPages=lambda canvas, doc: add_page_number(canvas, doc)
        )
        
        # إعادة المؤشر إلى بداية الملف
        pdf_buffer.seek(0)
        return pdf_buffer
    except Exception as e:
        import logging, traceback
        logging.error(f"خطأ في إنشاء PDF باستخدام ReportLab: {str(e)}")
        logging.error(traceback.format_exc())
        
        # إنشاء PDF بسيط في حالة حدوث خطأ
        return create_simple_error_pdf(str(e))

def add_page_number(canvas, doc):
    """إضافة رقم الصفحة والتاريخ والوقت إلى تذييل الصفحة"""
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
    
    # تاريخ ووقت الإنشاء
    date_text = get_arabic_text(f'تاريخ الإنشاء: {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    canvas.drawCentredString(A4[0] / 2, 20, date_text)
    
    # رقم الصفحة
    page_num = get_arabic_text(f'صفحة {doc.page}')
    canvas.drawRightString(A4[0] - 30, 20, page_num)
    
    canvas.restoreState()

def create_simple_error_pdf(error_message):
    """إنشاء PDF بسيط يحتوي على رسالة خطأ"""
    pdf_buffer = io.BytesIO()
    
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        title="Error Report",
    )
    
    styles = getSampleStyleSheet()
    elements = []
    
    elements.append(Paragraph("حدث خطأ أثناء إنشاء التقرير", styles['Title']))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"نص الخطأ: {error_message}", styles['Normal']))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("يرجى الاتصال بمسؤول النظام", styles['Normal']))
    
    doc.build(elements)
    pdf_buffer.seek(0)
    return pdf_buffer