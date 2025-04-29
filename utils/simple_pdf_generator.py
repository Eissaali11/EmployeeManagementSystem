"""   
مكتبة مبسطة لإنشاء تقارير PDF مع دعم للنصوص العربية
تستخدم هذه المكتبة ReportLab لإنشاء ملفات PDF بشكل بسيط ومباشر
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

# محاولة استيراد مكتبات النصوص العربية
try:
    from arabic_reshaper import reshape
    from bidi.algorithm import get_display
    ARABIC_SUPPORT = True
except ImportError:
    ARABIC_SUPPORT = False
    print("تحذير: مكتبات دعم النصوص العربية غير متوفرة")

# تسجيل خط Amiri العربي
def register_arabic_fonts():
    """تسجيل الخطوط العربية لمكتبة ReportLab"""
    try:
        # البحث عن مسار الخطوط
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        font_path = os.path.join(base_path, 'static', 'fonts')
        
        amiri_regular = os.path.join(font_path, 'Amiri-Regular.ttf')
        amiri_bold = os.path.join(font_path, 'Amiri-Bold.ttf')
        
        if os.path.exists(amiri_regular) and os.path.exists(amiri_bold):
            pdfmetrics.registerFont(TTFont('Amiri', amiri_regular))
            pdfmetrics.registerFont(TTFont('Amiri-Bold', amiri_bold))
            return True
    except Exception as e:
        print(f"خطأ في تسجيل الخطوط العربية: {e}")
    
    return False

# دالة مساعدة لمعالجة النصوص العربية
def arabic_text(text):
    """معالجة النصوص العربية للعرض الصحيح في PDF"""
    if not text:
        return ''
    
    # تحويل النص إلى سلسلة نصية إذا لم يكن كذلك بالفعل
    text = str(text)
    
    # إذا كان هناك دعم للنصوص العربية
    if ARABIC_SUPPORT:
        try:
            reshaped_text = reshape(text)
            bidi_text = get_display(reshaped_text)
            return bidi_text
        except Exception as e:
            print(f"خطأ في معالجة النص العربي: {e}")
    
    # إرجاع النص كما هو إذا لم يكن هناك دعم للعربية أو حدث خطأ
    return text

def create_vehicle_handover_pdf(handover_data):
    """
    إنشاء ملف PDF لتسليم/استلام المركبة
    
    Args:
        handover_data (dict): بيانات التسليم/الاستلام
        
    Returns:
        BytesIO: كائن BytesIO يحتوي على ملف PDF
    """
    # تسجيل الخطوط العربية
    fonts_registered = register_arabic_fonts()
    
    # إنشاء مستند PDF
    buffer = io.BytesIO()
    from reportlab.lib.units import mm
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )
    
    # الأنماط المستخدمة في المستند
    styles = getSampleStyleSheet()
    
    # إضافة أنماط عربية مخصصة
    styles.add(
        ParagraphStyle(
            name='ArabicTitle',
            fontName='Amiri-Bold' if fonts_registered else 'Helvetica-Bold',
            fontSize=16,
            leading=20,
            alignment=TA_CENTER,
        )
    )
    
    styles.add(
        ParagraphStyle(
            name='ArabicSubtitle',
            fontName='Amiri-Bold' if fonts_registered else 'Helvetica-Bold',
            fontSize=14,
            leading=18,
            alignment=TA_RIGHT,
        )
    )
    
    styles.add(
        ParagraphStyle(
            name='Arabic',
            fontName='Amiri' if fonts_registered else 'Helvetica',
            fontSize=12,
            leading=16,
            alignment=TA_RIGHT,
        )
    )
    
    styles.add(
        ParagraphStyle(
            name='ArabicSmall',
            fontName='Amiri' if fonts_registered else 'Helvetica',
            fontSize=10,
            leading=12,
            alignment=TA_CENTER,
        )
    )
    
    styles.add(
        ParagraphStyle(
            name='ButtonStyle',
            fontName='Amiri' if fonts_registered else 'Helvetica',
            fontSize=12,
            leading=16,
            alignment=TA_CENTER,
            textColor=colors.white,
            backColor=colors.Color(0.10, 0.16, 0.35),  # لون أزرق داكن
            borderWidth=0,
            spaceAfter=6,
            spaceBefore=6,
            borderRadius=3,
            borderColor=colors.Color(0.10, 0.16, 0.35),
        )
    )
    
    # قائمة لتخزين محتويات المستند
    content = []
    
    # إضافة عنوان المستند
    handover_type = "نموذج تسليم مركبة" if handover_data.get('handover_type') == 'تسليم' else "نموذج استلام مركبة"
    title = Paragraph(arabic_text(handover_type), styles['ArabicTitle'])
    content.append(title)
    content.append(Spacer(1, 10))
    
    # معلومات المركبة
    content.append(Paragraph(arabic_text("بيانات المركبة"), styles['ArabicSubtitle']))
    content.append(Spacer(1, 5))
    
    # إنشاء جدول بيانات المركبة
    if 'vehicle' in handover_data:
        vehicle_data = [
            [arabic_text("رقم اللوحة"), Paragraph(arabic_text(handover_data['vehicle'].get('plate_number', '')), styles['Arabic'])],
            [arabic_text("الشركة المصنعة"), Paragraph(arabic_text(handover_data['vehicle'].get('make', '')), styles['Arabic'])],
            [arabic_text("الطراز"), Paragraph(arabic_text(handover_data['vehicle'].get('model', '')), styles['Arabic'])],
            [arabic_text("سنة الصنع"), Paragraph(arabic_text(str(handover_data['vehicle'].get('year', ''))), styles['Arabic'])],
            [arabic_text("اللون"), Paragraph(arabic_text(handover_data['vehicle'].get('color', '')), styles['Arabic'])],
        ]
        
        vehicle_table = Table(vehicle_data, colWidths=[100, 300])
        vehicle_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (0, -1), 'Amiri' if fonts_registered else 'Helvetica'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))
        
        content.append(vehicle_table)
        content.append(Spacer(1, 15))
    
    # معلومات التسليم/الاستلام
    content.append(Paragraph(arabic_text("بيانات ال" + handover_data.get('handover_type', 'تسليم/استلام')), styles['ArabicSubtitle']))
    content.append(Spacer(1, 5))
    
    # إنشاء جدول معلومات التسليم/الاستلام
    handover_info_data = [
        [arabic_text("التاريخ"), Paragraph(arabic_text(handover_data.get('handover_date', '')), styles['Arabic'])],
        [arabic_text("الشخص"), Paragraph(arabic_text(handover_data.get('person_name', '')), styles['Arabic'])],
    ]
    
    # إضافة اسم المشرف إذا وجد
    if 'supervisor_name' in handover_data and handover_data['supervisor_name']:
        handover_info_data.append(
            [arabic_text("المشرف"), Paragraph(arabic_text(handover_data['supervisor_name']), styles['Arabic'])]
        )
    
    # إضافة رابط النموذج إذا وجد
    if 'form_link' in handover_data and handover_data['form_link']:
        # إنشاء زر للرابط
        button_text = Paragraph(arabic_text("مشاهدة سجل التسليم"), styles['ButtonStyle'])
        
        # إضافة الزر إلى الجدول
        handover_info_data.append(
            [arabic_text("رابط النموذج"), button_text]
        )
    
    # إضافة بقية معلومات التسليم/الاستلام
    handover_info_data.extend([
        [arabic_text("مستوى الوقود"), Paragraph(arabic_text(handover_data.get('fuel_level', '')), styles['Arabic'])],
        [arabic_text("قراءة العداد"), Paragraph(arabic_text(str(handover_data.get('mileage', ''))), styles['Arabic'])],
        [arabic_text("حالة المركبة"), Paragraph(arabic_text(handover_data.get('vehicle_condition', '')), styles['Arabic'])],
    ])
    
    # إنشاء جدول معلومات التسليم/الاستلام
    handover_table = Table(handover_info_data, colWidths=[100, 300])
    handover_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (0, -1), 'Amiri' if fonts_registered else 'Helvetica'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    content.append(handover_table)
    content.append(Spacer(1, 15))
    
    # معلومات فحص المركبة
    content.append(Paragraph(arabic_text("قائمة الفحص"), styles['ArabicSubtitle']))
    content.append(Spacer(1, 5))
    
    # تحضير بيانات الفحص
    check_items = [
        ("إطار احتياطي", handover_data.get('has_spare_tire', False)),
        ("طفاية حريق", handover_data.get('has_fire_extinguisher', False)),
        ("حقيبة إسعافات أولية", handover_data.get('has_first_aid_kit', False)),
        ("مثلث تحذيري", handover_data.get('has_warning_triangle', False)),
        ("أدوات", handover_data.get('has_tools', False))
    ]
    
    # تنسيق جدول الفحص
    check_data = []
    check_data.append([arabic_text("العنصر"), arabic_text("الحالة")])
    
    # إنشاء أنماط للعلامات
    for item_name, is_checked in check_items:
        check_status = "✔" if is_checked else "✖"  # علامة صح أو خطأ
        status_color = colors.green if is_checked else colors.red
        
        # إنشاء نمط تنسيق للعلامة
        status_style = ParagraphStyle(
            name='StatusStyle',
            parent=styles['Arabic'],
            alignment=TA_CENTER,
            textColor=status_color,
            fontSize=14,
            fontName='Helvetica-Bold'  # استخدام خط يدعم الرموز
        )
        
        # إنشاء فقرة للرمز
        status_paragraph = Paragraph(check_status, status_style)
        
        # إضافة البيانات إلى الجدول
        check_data.append([arabic_text(item_name), status_paragraph])
    
    # إنشاء جدول الفحص
    check_table = Table(check_data, colWidths=[200, 200])
    check_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (0, -1), 'Amiri' if fonts_registered else 'Helvetica'),
        ('FONTNAME', (0, 0), (-1, 0), 'Amiri-Bold' if fonts_registered else 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    content.append(check_table)
    content.append(Spacer(1, 15))
    
    # إضافة قسم الملاحظات إذا وجد
    if 'notes' in handover_data and handover_data['notes']:
        content.append(Paragraph(arabic_text("ملاحظات"), styles['ArabicSubtitle']))
        content.append(Spacer(1, 5))
        content.append(Paragraph(arabic_text(handover_data['notes']), styles['Arabic']))
        content.append(Spacer(1, 15))
    
    # إضافة تذييل للصفحة
    footer_text = f"تم إنشاء هذا التقرير بواسطة نُظم - نظام إدارة متكامل في {datetime.now().strftime('%Y-%m-%d')}"
    content.append(Paragraph(arabic_text(footer_text), styles['ArabicSmall']))
    
    # بناء المستند
    doc.build(content)
    
    # إعادة ضبط مؤشر الكائن BytesIO للقراءة
    buffer.seek(0)
    
    # إرجاع مهاندل الملف ليتم استخدامه مع send_file
    return buffer
