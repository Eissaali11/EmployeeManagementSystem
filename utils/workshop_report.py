"""
وحدة لإنشاء تقارير الورشة بالتصميم الجديد
مع دعم كامل للنصوص العربية
"""

import os
import io
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.lib.units import mm
from arabic_reshaper import reshape
from bidi.algorithm import get_display

def register_fonts():
    """تسجيل الخطوط العربية للتقارير بطريقة صحيحة"""
    try:
        # تحديد مسار ملفات الخطوط
        font_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'fonts')
        
        # تحديد مسارات خط Amiri (العادي والغامق)
        amiri_path = os.path.join(font_path, 'Amiri-Regular.ttf')
        amiri_bold_path = os.path.join(font_path, 'Amiri-Bold.ttf')
        
        # تسجيل الخطوط العربية إذا لم تكن مسجلة بالفعل
        if os.path.exists(amiri_path) and 'Amiri' not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont('Amiri', amiri_path))
            print("تم تسجيل خط Amiri للنصوص العربية بنجاح")
        
        if os.path.exists(amiri_bold_path) and 'Amiri-Bold' not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont('Amiri-Bold', amiri_bold_path))
            print("تم تسجيل خط Amiri-Bold للنصوص العربية بنجاح")
        
        # تحديد الخطوط التي سيتم استخدامها 
        if 'Amiri' in pdfmetrics.getRegisteredFontNames():
            font_name = 'Amiri'
            font_name_bold = 'Amiri-Bold' if 'Amiri-Bold' in pdfmetrics.getRegisteredFontNames() else 'Amiri'
        else:
            # استخدام الخطوط الافتراضية إذا لم يكن Amiri متاحًا
            print("خط Amiri غير متاح، استخدام الخطوط الافتراضية")
            font_name = 'Helvetica'
            font_name_bold = 'Helvetica-Bold'
        
        # تعريف أنماط الفقرات للتقرير
        global basic_style, title_style, heading_style, normal_style, arabic_style
        
        # نمط العنوان الرئيسي (وسط)
        title_style = ParagraphStyle(
            name='ReportTitle',
            fontName=font_name_bold,
            fontSize=16,
            leading=20,
            alignment=TA_CENTER,  # وسط
            spaceAfter=12
        )
        
        # نمط العناوين الفرعية (وسط)
        heading_style = ParagraphStyle(
            name='Heading',
            fontName=font_name_bold,
            fontSize=14,
            leading=18,
            alignment=TA_CENTER,  # وسط
            spaceAfter=10
        )
        
        # نمط النص العادي (يمين للعربية)
        normal_style = ParagraphStyle(
            name='Normal',
            fontName=font_name,
            fontSize=12,
            leading=14,
            alignment=TA_RIGHT,  # يمين (للعربية)
            firstLineIndent=0
        )
        
        # نمط نص عربي محدد (للجداول والنصوص قصيرة)
        arabic_style = ParagraphStyle(
            name='Arabic',
            fontName=font_name,
            fontSize=10,
            leading=12,
            alignment=TA_RIGHT,  # يمين (للعربية)
            firstLineIndent=0
        )
        
        # نمط أساسي للجداول
        basic_style = ParagraphStyle(
            name='BasicStyle',
            fontName=font_name,
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
        arabic_style = styles['Normal']

def arabic_text(text):
    """
    معالجة النص العربي بشكل صحيح ليظهر في ملفات PDF
    
    تستخدم هذه الدالة arabic_reshaper فقط لإعادة تشكيل النص العربي دون تغيير الترتيب
    """
    if text is None or text == "":
        return ""
    
    try:
        # تحويل إلى نص
        text_str = str(text)
        
        # حالات خاصة - الأرقام والتواريخ
        if text_str.replace('.', '', 1).replace(',', '', 1).isdigit():
            return text_str
            
        # حالة التواريخ وأي نص يحتوي على أرقام وحروف خاصة فقط
        if ('-' in text_str or '/' in text_str) and all(not ('\u0600' <= c <= '\u06FF') for c in text_str):
            return text_str
        
        # نستخدم فقط إعادة تشكيل النص دون تغيير ترتيب الأحرف
        # لأن المشكلة تظهر من استخدام get_display الذي يعكس النص
        reshaped_text = reshape(text_str)
        
        # طريقة بديلة - قائمة مصطلحات شائعة في السياق
        common_terms = {
            'تقرير سجلات الورشة': 'Workshop Records Report',
            'المركبة': 'Vehicle',
            'سجلات الورشة': 'Workshop Records',
            'الفني المسؤول': 'Technician',
            'اسم الورشة': 'Workshop',
            'التكلفة (ريال)': 'Cost (SAR)',
            'حالة الإصلاح': 'Repair Status',
            'تاريخ الخروج': 'Exit Date',
            'تاريخ الدخول': 'Entry Date',
            'سبب الدخول': 'Entry Reason',
            'صيانة دورية': 'Regular Maintenance',
            'عطل': 'Breakdown',
            'حادث': 'Accident'
        }
        
        # تحقق إذا كان النص موجودًا في القائمة
        if text_str in common_terms:
            return common_terms[text_str]
            
        # سجل للتصحيح
        print(f"النص الأصلي: {text_str}")
        print(f"النص بعد إعادة التشكيل فقط: {reshaped_text}")
        
        # نعيد النص الأصلي كما هو بدلاً من إجراء أي معالجة
        # هذا سيسمح لنا بالتحقق مما إذا كانت المشكلة في reportlab نفسها
        return text_str
        
    except Exception as e:
        print(f"خطأ في معالجة النص العربي: {str(e)}")
        # إذا فشلت المعالجة، نعيد النص الأصلي
        return str(text)

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
    
    # إعداد الصفحة والأنماط - استخدام الخطوط الافتراضية فقط
    styles.add(ParagraphStyle(name='Arabic', fontName='Helvetica', fontSize=12, alignment=1))
    styles.add(ParagraphStyle(name='ArabicTitle', fontName='Helvetica-Bold', fontSize=16, alignment=1))
    styles.add(ParagraphStyle(name='ArabicHeading', fontName='Helvetica-Bold', fontSize=14, alignment=1))
    
    # إنشاء دالة للرسم في رأس الصفحة
    def add_header_footer(canvas, doc):
        canvas.saveState()
        
        # تم حذف كل شيء من رأس الصفحة بناءً على طلب المستخدم
        
        # إضافة معلومات في التذييل فقط - استخدام خط Helvetica بدل Amiri
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.gray) # رمادي
        footer_text = f"تم إنشاء هذا التقرير بواسطة نُظم - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        canvas.drawString(A4[0]/2 - canvas.stringWidth(footer_text, 'Helvetica', 8)/2, 30, footer_text)
        
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
    
    # عنوان التقرير - استخدم نص بسيط
    title = "تقرير سجلات الورشة للسيارة: " + vehicle.plate_number
    content.append(Paragraph(title, title_style))
    content.append(Spacer(1, 10))
    
    # معلومات السيارة الأساسية - استخدم نص بسيط
    vehicle_info = "السيارة: " + vehicle.make + " " + vehicle.model + " " + str(vehicle.year)
    content.append(Paragraph(vehicle_info, normal_style))
    content.append(Spacer(1, 20))
    
    # سجلات الورشة - استخدم نص بسيط
    content.append(Paragraph("سجلات الورشة", heading_style))
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
        
        # استخدام خط Helvetica الافتراضي للجدول
        font_name = 'Helvetica'
        
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('ALIGN', (2, 1), (2, -1), 'LEFT'),  # محاذاة أرقام التكلفة إلى اليسار
            ('FONTNAME', (0, 0), (-1, -1), font_name),  # استخدام الخط العربي المسجل
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
        cost_text = Paragraph(f"إجمالي تكاليف الصيانة: {total_cost:,.2f} ريال", normal_style)
        content.append(cost_text)
        
        # إجمالي عدد أيام الورشة
        days_in_workshop = sum(
            (record.exit_date - record.entry_date).days + 1 if hasattr(record, 'exit_date') and record.exit_date else 
            (datetime.now().date() - record.entry_date).days + 1 if hasattr(record, 'entry_date') else 0
            for record in workshop_records
        )
        days_text = Paragraph(f"إجمالي عدد أيام الورشة: {days_in_workshop} يوم", normal_style)
        content.append(days_text)
    else:
        content.append(Paragraph("لا توجد سجلات ورشة لهذه السيارة", normal_style))
    
    content.append(Spacer(1, 20))
    
    # بيانات التوقيع والطباعة
    footer_text = Paragraph(
        f"تم إنشاء هذا التقرير بواسطة نُظم في {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        normal_style
    )
    copyright_text = Paragraph(
        "نُظم - جميع الحقوق محفوظة © " + str(datetime.now().year),
        normal_style
    )
    content.append(footer_text)
    content.append(Spacer(1, 10))
    content.append(copyright_text)
    
    # بناء الوثيقة مع استخدام دالة رأس وتذييل الصفحة
    doc.build(content, onFirstPage=add_header_footer, onLaterPages=add_header_footer)
    buffer.seek(0)
    return buffer