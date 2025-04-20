"""
وحدة لإنشاء تقارير الورشة بالتصميم الجديد
"""

import os
import io
from datetime import datetime
from flask import current_app
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from arabic_reshaper import reshape
from bidi.algorithm import get_display

def register_fonts():
    """تسجيل الخطوط العربية"""
    font_path = os.path.join(current_app.static_folder, 'fonts')
    
    # التحقق من وجود الخطوط وتسجيلها
    amiri_path = os.path.join(font_path, 'Amiri-Regular.ttf')
    amiri_bold_path = os.path.join(font_path, 'Amiri-Bold.ttf')
    
    if not os.path.exists(font_path):
        os.makedirs(font_path)
    
    if os.path.exists(amiri_path) and os.path.exists(amiri_bold_path):
        pdfmetrics.registerFont(TTFont('Amiri', amiri_path))
        pdfmetrics.registerFont(TTFont('Amiri-Bold', amiri_bold_path))
        print("تم تسجيل خط Amiri للنصوص العربية بنجاح")
    else:
        # استخدام خط افتراضي إذا لم تكن الخطوط العربية متوفرة
        pdfmetrics.registerFont(TTFont('Amiri', 'Helvetica'))
        pdfmetrics.registerFont(TTFont('Amiri-Bold', 'Helvetica-Bold'))

def arabic_text(text):
    """معالجة النص العربي للعرض الصحيح في ملفات PDF"""
    if text is None:
        return ""
    return get_display(reshape(str(text)))

def generate_workshop_report_pdf(vehicle, workshop_records):
    """
    إنشاء تقرير سجلات الورشة للمركبة بالتصميم الجديد
    
    Args:
        vehicle: كائن المركبة
        workshop_records: قائمة بسجلات الورشة
    
    Returns:
        BytesIO: كائن بايت يحتوي على ملف PDF
    """
    register_fonts()
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    styles = getSampleStyleSheet()
    
    # إنشاء نمط للنص العربي
    styles.add(ParagraphStyle(name='Arabic', fontName='Amiri', fontSize=12, alignment=1))
    styles.add(ParagraphStyle(name='ArabicTitle', fontName='Amiri-Bold', fontSize=16, alignment=1))
    styles.add(ParagraphStyle(name='ArabicHeading', fontName='Amiri-Bold', fontSize=14, alignment=1))
    
    # تحضير المحتوى
    content = []
    
    # إضافة شعار الشركة الجديد بشكل دائري
    from reportlab.lib.utils import ImageReader
    from reportlab.lib.colors import blue, white
    from reportlab.pdfgen import canvas
    
    # تحديد مسار الشعار
    logo_path = os.path.join(current_app.static_folder, 'images', 'workshop_logo.png')
    if not os.path.exists(logo_path):
        # استخدام الشعار الأساسي للنظام كبديل
        logo_path = os.path.join(current_app.static_folder, 'images', 'logo_new.png')
    
    if os.path.exists(logo_path):
        # إنشاء دائرة باستخدام Flowable مخصص
        class CircularImage:
            def __init__(self, path, size=120):
                self.path = path
                self.size = size
                
            def wrap(self, width, height):
                return (self.size, self.size)
                
            def drawOn(self, canv, x, y, _sW=0):
                # حساب موضع مركز الدائرة
                center_x = x + self.size / 2
                center_y = y
                radius = self.size / 2
                
                # رسم دائرة زرقاء كخلفية
                canv.setFillColor(blue)
                canv.circle(center_x, center_y, radius, fill=1)
                
                # وضع الصورة داخل الدائرة
                img = ImageReader(self.path)
                canv.drawImage(img, x+5, y-radius+5, width=self.size-10, height=self.size-10, mask='auto')
                
        # إضافة الشعار الدائري
        circular_logo = CircularImage(logo_path, 120)
        content.append(circular_logo)
        content.append(Spacer(1, 20))
    
    # عنوان التقرير
    title = Paragraph(arabic_text(f"تقرير سجلات الورشة للسيارة: {vehicle.plate_number}"), styles['ArabicTitle'])
    content.append(title)
    content.append(Spacer(1, 10))
    
    # معلومات السيارة الأساسية
    vehicle_info = Paragraph(
        arabic_text(f"السيارة: {vehicle.make} {vehicle.model} {vehicle.year}"),
        styles['Arabic']
    )
    content.append(vehicle_info)
    content.append(Spacer(1, 20))
    
    # سجلات الورشة
    content.append(Paragraph(arabic_text("سجلات الورشة"), styles['ArabicHeading']))
    content.append(Spacer(1, 10))
    
    if workshop_records and len(workshop_records) > 0:
        # تحضير بيانات سجلات الورشة
        workshop_data = [
            [
                arabic_text("الفني المسؤول"),
                arabic_text("اسم الورشة"),
                arabic_text("التكلفة (ريال)"),
                arabic_text("حالة الإصلاح"),
                arabic_text("تاريخ الخروج"),
                arabic_text("تاريخ الدخول"),
                arabic_text("سبب الدخول")
            ]
        ]
        
        for record in workshop_records:
            reason_map = {'maintenance': 'صيانة دورية', 'breakdown': 'عطل', 'accident': 'حادث'}
            status_map = {'in_progress': 'قيد التنفيذ', 'completed': 'تم الإصلاح', 'pending_approval': 'بانتظار الموافقة'}
            
            # استخراج البيانات بشكل آمن
            entry_date = record.entry_date.strftime('%Y-%m-%d') if hasattr(record, 'entry_date') and record.entry_date else ""
            exit_date = record.exit_date.strftime('%Y-%m-%d') if hasattr(record, 'exit_date') and record.exit_date else "ما زالت في الورشة"
            
            entry_reason = reason_map.get(record.entry_reason, record.entry_reason) if hasattr(record, 'entry_reason') else ""
            repair_status = status_map.get(record.repair_status, record.repair_status) if hasattr(record, 'repair_status') else ""
            
            cost = f"{record.cost:,.2f}" if hasattr(record, 'cost') and record.cost is not None else "0.00"
            workshop_name = record.workshop_name if hasattr(record, 'workshop_name') else ""
            technician = record.technician if hasattr(record, 'technician') else ""
            
            workshop_data.append([
                arabic_text(technician),
                arabic_text(workshop_name),
                arabic_text(cost),
                arabic_text(repair_status),
                arabic_text(exit_date),
                arabic_text(entry_date),
                arabic_text(entry_reason)
            ])
        
        t = Table(workshop_data, colWidths=[doc.width/7] * 7)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('ALIGN', (2, 1), (2, -1), 'LEFT'),  # محاذاة أرقام التكلفة إلى اليسار
            ('FONTNAME', (0, 0), (-1, -1), 'Amiri'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        content.append(t)
        content.append(Spacer(1, 20))
        
        # إجمالي تكاليف الصيانة
        total_cost = sum(record.cost or 0 for record in workshop_records)
        cost_text = Paragraph(arabic_text(f"إجمالي تكاليف الصيانة: {total_cost:,.2f} ريال"), styles['Arabic'])
        content.append(cost_text)
        
        # إجمالي عدد أيام الورشة
        days_in_workshop = sum(
            (record.exit_date - record.entry_date).days + 1 if hasattr(record, 'exit_date') and record.exit_date else 
            (datetime.now().date() - record.entry_date).days + 1 if hasattr(record, 'entry_date') else 0
            for record in workshop_records
        )
        days_text = Paragraph(arabic_text(f"إجمالي عدد أيام الورشة: {days_in_workshop} يوم"), styles['Arabic'])
        content.append(days_text)
    else:
        content.append(Paragraph(arabic_text("لا توجد سجلات ورشة لهذه السيارة"), styles['Arabic']))
    
    content.append(Spacer(1, 20))
    
    # بيانات التوقيع والطباعة
    footer_text = Paragraph(
        arabic_text(f"تم إنشاء هذا التقرير بواسطة نظام نُظم في {datetime.now().strftime('%Y-%m-%d %H:%M')}"),
        styles['Arabic']
    )
    content.append(footer_text)
    
    # بناء الوثيقة
    doc.build(content)
    buffer.seek(0)
    return buffer