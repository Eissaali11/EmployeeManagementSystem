"""
وحدة مخصصة لإنشاء تقارير الورشة بصيغة PDF
"""

from flask import Blueprint, request, send_file, flash, redirect, url_for
from flask_login import login_required
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

from app import db
from models import Vehicle, VehicleWorkshop

# إنشاء Blueprint
workshop_reports_bp = Blueprint('workshop_reports', __name__)

# تسجيل الخطوط العربية
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS_DIR = os.path.join(BASE_DIR, 'static', 'fonts')

# تسجيل خطوط Amiri و Tajawal
try:
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

@workshop_reports_bp.route('/vehicle/<int:id>/workshop/pdf')
@login_required
def vehicle_workshop_pdf(id):
    """تصدير تقرير سجلات الورشة للمركبة كملف PDF"""
    try:
        # جلب بيانات المركبة
        vehicle = Vehicle.query.get_or_404(id)
        
        # جلب سجلات دخول الورشة
        workshop_records = VehicleWorkshop.query.filter_by(vehicle_id=id).order_by(
            VehicleWorkshop.entry_date.desc()
        ).all()
        
        # التحقق من وجود سجلات
        if not workshop_records:
            flash('لا توجد سجلات ورشة لهذه المركبة!', 'warning')
            return redirect(url_for('vehicles.view', id=id))
        
        # إنشاء كائن PDF جديد
        pdf_buffer = create_workshop_pdf(vehicle, workshop_records)
        
        # اسم الملف
        filename = f"workshop_report_{vehicle.plate_number}.pdf"
        
        # إرسال الملف
        return send_file(
            pdf_buffer,
            download_name=filename,
            as_attachment=True,
            mimetype='application/pdf'
        )
    
    except Exception as e:
        # تسجيل الخطأ بالتفصيل
        import logging
        import traceback
        logging.error(f"خطأ في إنشاء تقرير الورشة: {str(e)}")
        logging.error(traceback.format_exc())
        
        flash(f'حدث خطأ أثناء إنشاء التقرير: {str(e)}', 'error')
        return redirect(url_for('vehicles.view', id=id))

def create_workshop_pdf(vehicle, workshop_records):
    """
    إنشاء ملف PDF يحتوي على تقرير سجلات الورشة
    
    Args:
        vehicle: بيانات المركبة
        workshop_records: سجلات الورشة
        
    Returns:
        BytesIO: كائن بايت يحتوي على ملف PDF
    """
    # إنشاء كائن بايت IO
    pdf_buffer = io.BytesIO()
    
    # إنشاء مستند بحجم A4
    doc = SimpleDocTemplate(
        pdf_buffer, 
        pagesize=A4,
        title=get_arabic_text("تقرير سجلات الورشة"),
        author=get_arabic_text("نُظم - نظام إدارة المركبات")
    )
    
    # عناصر المستند
    elements = []
    
    # تعريف الأنماط
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name='RightAlign',
        fontName='Tajawal-Bold',
        fontSize=14,
        alignment=2  # محاذاة لليمين
    ))
    styles.add(ParagraphStyle(
        name='CenterAlign',
        fontName='Tajawal-Bold',
        fontSize=16,
        alignment=1  # توسيط
    ))
    
    # إضافة الشعار إن وجد
    logo_path = os.path.join(BASE_DIR, 'static', 'img', 'logo.png')
    if os.path.exists(logo_path):
        img = Image(logo_path, width=100, height=50)
        img.hAlign = 'CENTER'
        elements.append(img)
        elements.append(Spacer(1, 10))
    
    # عنوان التقرير
    elements.append(Paragraph(get_arabic_text("تقرير سجلات الورشة"), styles['CenterAlign']))
    elements.append(Spacer(1, 10))
    
    # معلومات المركبة
    vehicle_info = [
        [get_arabic_text("معلومات المركبة"), ""],
        [get_arabic_text("رقم اللوحة:"), get_arabic_text(vehicle.plate_number)],
        [get_arabic_text("الماركة:"), get_arabic_text(vehicle.make)],
        [get_arabic_text("الموديل:"), get_arabic_text(vehicle.model)]
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
    
    # جدول سجلات الورشة
    table_data = [
        [
            get_arabic_text("سبب الزيارة"),
            get_arabic_text("تاريخ الدخول"),
            get_arabic_text("تاريخ الخروج"),
            get_arabic_text("عدد الأيام"),
            get_arabic_text("الحالة"),
            get_arabic_text("اسم الورشة"),
            get_arabic_text("الفني"),
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
    
    # إنشاء المستند
    doc.build(
        elements,
        onFirstPage=lambda canvas, doc: add_page_number(canvas, doc),
        onLaterPages=lambda canvas, doc: add_page_number(canvas, doc)
    )
    
    # رجوع إلى بداية الذاكرة المؤقتة
    pdf_buffer.seek(0)
    return pdf_buffer

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