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
    """تسجيل الخطوط للتقارير"""
    # استخدام الخطوط الافتراضية المدمجة في reportlab بدلاً من الخطوط العربية المخصصة
    try:
        # نستخدم الخطوط الافتراضية المضمنة في reportlab
        styles = getSampleStyleSheet()
        
        # تعريف أنماط الفقرات للتقرير
        global basic_style, title_style, heading_style, normal_style
        
        # نمط العنوان الرئيسي
        title_style = ParagraphStyle(
            name='ReportTitle',
            fontName='Helvetica-Bold',
            fontSize=16,
            leading=20,
            alignment=1,  # وسط
            spaceAfter=12
        )
        
        # نمط العناوين الفرعية
        heading_style = ParagraphStyle(
            name='Heading',
            fontName='Helvetica-Bold',
            fontSize=14,
            leading=18,
            alignment=1,  # وسط
            spaceAfter=10
        )
        
        # نمط النص العادي
        normal_style = ParagraphStyle(
            name='Normal',
            fontName='Helvetica',
            fontSize=12,
            leading=14,
            alignment=2,  # يمين (للعربية)
            firstLineIndent=0
        )
        
        # نمط أساسي للجداول
        basic_style = ParagraphStyle(
            name='BasicStyle',
            fontName='Helvetica',
            fontSize=12
        )
        
        print("تم تجهيز أنماط التقرير بنجاح")
    except Exception as e:
        print(f"خطأ في تجهيز أنماط التقرير: {str(e)}")
        # استخدام أنماط احتياطية في حالة الفشل
        styles = getSampleStyleSheet()
        title_style = styles['Title']
        heading_style = styles['Heading1']
        normal_style = styles['Normal']
        basic_style = styles['Normal']

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
    
    # إنشاء كائن BytesIO لتخزين البيانات
    buffer = io.BytesIO()
    
    # إنشاء الوثيقة
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=60, bottomMargin=18)
    styles = getSampleStyleSheet()
    
    # إعداد الصفحة والأنماط
    styles.add(ParagraphStyle(name='Arabic', fontName='Amiri', fontSize=12, alignment=1))
    styles.add(ParagraphStyle(name='ArabicTitle', fontName='Amiri-Bold', fontSize=16, alignment=1))
    styles.add(ParagraphStyle(name='ArabicHeading', fontName='Amiri-Bold', fontSize=14, alignment=1))
    
    # إنشاء دالة للرسم في رأس الصفحة
    def add_header_footer(canvas, doc):
        canvas.saveState()
        
        # تم حذف كل شيء من رأس الصفحة بناءً على طلب المستخدم
        
        # إضافة معلومات في التذييل فقط
        canvas.setFont('Amiri', 8)
        canvas.setFillColor(colors.gray) # رمادي
        footer_text = arabic_text(f"تم إنشاء هذا التقرير بواسطة نُظم - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        canvas.drawString(A4[0]/2 - canvas.stringWidth(footer_text, 'Amiri', 8)/2, 30, footer_text)
        
        canvas.restoreState()
    
    # تحضير المحتوى
    content = []
    
    # إضافة شعار الشركة الجديد بشكل دائري في رأس الصفحة
    from reportlab.lib.utils import ImageReader
    from reportlab.lib.colors import blue, white, Color
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import mm
    
    # إنشاء Flowable مخصص لرأس الصفحة (بدون شعار)
    from reportlab.platypus.flowables import Flowable
    
    class PageHeader(Flowable):
        def __init__(self, width, height=25*mm):
            Flowable.__init__(self)
            self.width = width
            self.height = height
            
        def wrap(self, width, height):
            return (self.width, self.height)
            
        def drawOn(self, canv, x, y, _sW=0):
            # إضافة الشعار في وسط رأس الصفحة
            try:
                logo_size = 40*mm  # حجم الشعار كبير
                logo_path = 'static/images/logo/logo_new.png'  # مسار الشعار
                logo_img = ImageReader(logo_path)
                
                # موضع الشعار في وسط الصفحة
                logo_x = x + self.width/2  # الوسط الأفقي للصفحة
                logo_y = y + self.height + 5*mm  # موضع الشعار في أعلى الصفحة بهامش صغير
                
                # رسم الشعار مع مراعاة مركز الشعار
                canv.drawImage(logo_img, logo_x - logo_size/2, logo_y - logo_size/2, width=logo_size, height=logo_size, mask='auto')
                
            except Exception as e:
                print(f"خطأ في تحميل الشعار في PageHeader: {e}")
                # في حالة الخطأ، لا نرسم شيئاً

        # دوال مطلوبة للتوافق مع Flowable
        def getKeepWithNext(self):
            return 0
            
        def setKeepWithNext(self, value):
            pass
            
        def getKeepTogether(self):
            return 0
            
        def split(self, availWidth, availHeight):
            if availHeight < self.height:
                return []
            return [self]
    
    # إضافة الشعار ورأس الصفحة
    header = PageHeader(doc.width)
    content.append(header)
    content.append(Spacer(1, 30*mm))
    
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
            
            # استخدام حقل reason بدلاً من entry_reason للتوافق مع نموذج البيانات
            entry_reason = reason_map.get(record.reason, record.reason) if hasattr(record, 'reason') and record.reason else ""
            repair_status = status_map.get(record.repair_status, record.repair_status) if hasattr(record, 'repair_status') else ""
            
            cost = f"{record.cost:,.2f}" if hasattr(record, 'cost') and record.cost is not None else "0.00"
            workshop_name = record.workshop_name if hasattr(record, 'workshop_name') else ""
            # استخدام حقل technician_name بدلاً من technician للتوافق مع نموذج البيانات
            technician = record.technician_name if hasattr(record, 'technician_name') and record.technician_name else ""
            
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
        arabic_text(f"تم إنشاء هذا التقرير بواسطة نُظم في {datetime.now().strftime('%Y-%m-%d %H:%M')}"),
        styles['Arabic']
    )
    copyright_text = Paragraph(
        arabic_text("نُظم - جميع الحقوق محفوظة © " + str(datetime.now().year)),
        styles['Arabic']
    )
    content.append(footer_text)
    content.append(Spacer(1, 10))
    content.append(copyright_text)
    
    # بناء الوثيقة مع استخدام دالة رأس وتذييل الصفحة
    doc.build(content, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
    buffer.seek(0)
    return buffer