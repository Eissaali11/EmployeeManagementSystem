"""   
مكتبة لإنشاء تقارير تسليم/استلام المركبات باستخدام ReportLab
لحل مشكلة الترميز مع النصوص العربية
"""

import os
import io
from datetime import datetime
from flask import current_app
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.platypus.flowables import Flowable
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from arabic_reshaper import reshape
from bidi.algorithm import get_display
from reportlab.lib.units import mm

def register_fonts():
    """تسجيل الخطوط العربية"""
    font_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'fonts')
    
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
        # محاولة البحث عن المسارات البديلة
        try:
            static_folder = current_app.static_folder
            amiri_path = os.path.join(static_folder, 'fonts', 'Amiri-Regular.ttf')
            amiri_bold_path = os.path.join(static_folder, 'fonts', 'Amiri-Bold.ttf')
            
            if os.path.exists(amiri_path) and os.path.exists(amiri_bold_path):
                pdfmetrics.registerFont(TTFont('Amiri', amiri_path))
                pdfmetrics.registerFont(TTFont('Amiri-Bold', amiri_bold_path))
                print("تم تسجيل خط Amiri للنصوص العربية من المسار البديل بنجاح")
            else:
                print("لم يتم العثور على ملفات الخط العربي، سيتم استخدام الخط الافتراضي")
                # استخدام خط افتراضي إذا لم تكن الخطوط العربية متوفرة
                pdfmetrics.registerFont(TTFont('Amiri', 'Helvetica'))
                pdfmetrics.registerFont(TTFont('Amiri-Bold', 'Helvetica-Bold'))
        except Exception as e:
            print(f"خطأ في تسجيل الخطوط: {str(e)}")
            # استخدام خط افتراضي إذا لم تكن الخطوط العربية متوفرة
            pdfmetrics.registerFont(TTFont('Amiri', 'Helvetica'))
            pdfmetrics.registerFont(TTFont('Amiri-Bold', 'Helvetica-Bold'))

def arabic_text(text):
    """معالجة النص العربي للعرض الصحيح في ملفات PDF"""
    if text is None:
        return ""
    # إضافة معالجة إضافية للنصوص العربية
    try:
        # تحويل النص إلى سلسلة أحرف
        text_str = str(text)
        # إعادة تشكيل النص باستخدام arabic_reshaper
        reshaped_text = reshape(text_str)
        # تطبيق خوارزمية BIDI لدعم اتجاه الكتابة من اليمين إلى اليسار
        bidi_text = get_display(reshaped_text)
        return bidi_text
    except Exception as e:
        print(f"خطأ في معالجة النص العربي: {str(e)}")
        # إذا فشلت المعالجة، أعد النص الأصلي
        return str(text)

def generate_vehicle_handover_pdf(handover_data):
    """
    إنشاء تقرير تسليم/استلام المركبة باستخدام ReportLab
    
    Args:
        handover_data: بيانات التسليم/الاستلام
    
    Returns:
        BytesIO: كائن بايت يحتوي على ملف PDF
    """
    # تسجيل الخطوط
    register_fonts()
    
    # إنشاء كائن BytesIO لتخزين البيانات
    buffer = io.BytesIO()
    
    # إنشاء الوثيقة
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    styles = getSampleStyleSheet()
    
    # إنشاء أنماط للنص العربي
    styles.add(ParagraphStyle(name='Arabic', fontName='Amiri', fontSize=12, alignment=1))  # للنص العربي
    styles.add(ParagraphStyle(name='ArabicTitle', fontName='Amiri-Bold', fontSize=16, alignment=1))  # للعناوين
    styles.add(ParagraphStyle(name='ArabicSubtitle', fontName='Amiri-Bold', fontSize=14, alignment=1))  # للعناوين الفرعية
    styles.add(ParagraphStyle(name='ArabicSmall', fontName='Amiri', fontSize=10, alignment=1))  # للنص الصغير
    
    # تحضير المحتوى
    content = []
    
    # إضافة شعار النظام بشكل دائري
    try:
        # محاولة البحث في مسار الأصول الثابتة
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'images', 'logo_new.png')
        if not os.path.exists(logo_path):
            try:
                # محاولة البحث في المسار البديل
                static_folder = current_app.static_folder
                logo_path = os.path.join(static_folder, 'images', 'logo_new.png')
            except Exception as e:
                print(f"لم يتم العثور على الشعار: {str(e)}")
                logo_path = None
        
        if logo_path and os.path.exists(logo_path):
            # إنشاء خلفية دائرية زرقاء للشعار
            from reportlab.lib.colors import Color
            from reportlab.platypus.flowables import Flowable

            class CircularLogoImage(Flowable):
                def __init__(self, path, size=30*mm):
                    Flowable.__init__(self)
                    self.path = path
                    self.size = size
                    
                def wrap(self, width, height):
                    return (self.size, self.size)
                    
                def drawOn(self, canv, x, y, _sW=0):
                    # تحديد اللون الأزرق للخلفية (لون مطابق للشعار)
                    navy_blue = Color(0.13, 0.24, 0.49)
                    
                    # رسم دائرة زرقاء
                    canv.setFillColor(navy_blue)
                    center_x = x + self.size/2
                    center_y = y - self.size/2
                    radius = self.size/2
                    canv.circle(center_x, center_y, radius, fill=1)
                    
                    # إضافة الشعار فوق الدائرة
                    canv.drawImage(self.path, x, y-self.size, width=self.size, height=self.size, mask='auto')
            
            # إضافة الشعار الدائري إلى المحتوى
            circular_logo = CircularLogoImage(logo_path, 30*mm)
            content.append(circular_logo)
    except Exception as e:
        print(f"خطأ في إضافة الشعار: {str(e)}")
        # إذا فشل إضافة الشعار الدائري، نضيف عنوان بديل
        system_title = Paragraph(arabic_text("نُظم"), styles['ArabicTitle'])
        content.append(system_title)
    
    # إضافة مسافة
    content.append(Spacer(1, 10))
    
    # عنوان التقرير
    title_text = f"نموذج {handover_data['handover_type']} مركبة"
    title = Paragraph(arabic_text(title_text), styles['ArabicTitle'])
    content.append(title)
    content.append(Spacer(1, 20))
    
    # معلومات المركبة
    content.append(Paragraph(arabic_text("بيانات المركبة"), styles['ArabicSubtitle']))
    content.append(Spacer(1, 10))
    
    # جدول معلومات المركبة
    vehicle_data = [
        [arabic_text("رقم اللوحة"), arabic_text(handover_data['vehicle']['plate_number'])],
        [arabic_text("النوع والموديل"), arabic_text(f"{handover_data['vehicle']['make']} {handover_data['vehicle']['model']}")],
        [arabic_text("سنة الصنع"), arabic_text(str(handover_data['vehicle']['year']))],
        [arabic_text("اللون"), arabic_text(handover_data['vehicle']['color'])]
    ]
    
    vehicle_table = Table(vehicle_data, colWidths=[100, 300])
    vehicle_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Amiri'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    content.append(vehicle_table)
    content.append(Spacer(1, 20))
    
    # معلومات التسليم/الاستلام
    content.append(Paragraph(arabic_text(f"معلومات {handover_data['handover_type']}"), styles['ArabicSubtitle']))
    content.append(Spacer(1, 10))
    
    # تجهيز بيانات التسليم/الاستلام
    # استخدام Paragraph لضمان التعامل السليم مع النصوص العربية
    date_text = Paragraph(arabic_text(handover_data['handover_date']), styles['Arabic'])
    person_text = Paragraph(arabic_text(handover_data['person_name']), styles['Arabic'])
    
    handover_info_data = [
        [arabic_text("التاريخ"), date_text],
        [arabic_text("الشخص"), person_text],
    ]
    
    # إضافة معلومات المشرف إذا وجدت
    if handover_data.get('supervisor_name'):
        supervisor_text = Paragraph(arabic_text(handover_data['supervisor_name']), styles['Arabic'])
        handover_info_data.append([arabic_text("المشرف"), supervisor_text])
    
    # إضافة رابط النموذج إذا وجد كرابط قابل للنقر
    if handover_data.get('form_link'):
        from reportlab.lib.colors import blue
        # إنشاء نمط مخصص للرابط
        link_style = ParagraphStyle(
            name='LinkStyle',
            parent=styles['Arabic'],
            textColor=blue,
            underline=True
        )
        # استخدام نهج مختلف للروابط
        from reportlab.platypus.flowables import HRFlowable
        
        # إنشاء نص الرابط وإضافة أيقونة مناسبة
        link_value = handover_data['form_link']
        
        # إنشاء نص توجيهي
        link_desc = Paragraph(arabic_text("انقر هنا لفتح النموذج"), styles['Arabic'])
        
        # استخدام صورة "هنا هنا" كرابط
        # الحصول على مسار الصورة
        icon_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'static', 'images', 'icons', 'click_here.svg'
        )
        
        # بدلاً من استخدام الرسومات، سنستخدم Paragraph مع خلفية ملونة
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER
        from reportlab.lib import colors

        # إنشاء نمط للزر
        button_style = ParagraphStyle(
            name='ButtonStyle',
            parent=styles['Arabic'],
            alignment=TA_CENTER,
            fontSize=12,
            textColor=colors.white,
            backColor=colors.Color(0.10, 0.16, 0.35),
            borderWidth=0,
            padding=8
        )
        
        # إنشاء نص الزر
        button = Paragraph(
            arabic_text("مشاهدة سجل التسليم «"), 
            button_style
        )
        
        # استخدام الصورة كما هي بدون روابط قابلة للنقر
        # في ملفات PDF لن يكون هناك روابط قابلة للنقر
        link_icon = button

        # إنشاء جدول داخلي للنص والأيقونة
        link_table = Table([[link_desc], [link_icon]], colWidths=[300])
        link_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # توسيط كل محتويات الجدول
            ('VALIGN', (0, 0), (0, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (0, 0), 4),
            ('TOPPADDING', (0, 0), (0, 0), 4),
            ('BOTTOMPADDING', (0, 1), (0, 1), 4),
            ('TOPPADDING', (0, 1), (0, 1), 4),
        ]))
        handover_info_data.append([arabic_text("رابط النموذج"), link_table])
    
    # إضافة مستوى الوقود وعداد المسافة
    # نقوم بإنشاء Paragraph لكل نص لضمان التعامل السليم مع النصوص العربية
    fuel_text = Paragraph(arabic_text(handover_data['fuel_level']), styles['Arabic'])
    mileage_text = Paragraph(arabic_text(str(handover_data['mileage'])), styles['Arabic'])
    condition_text = Paragraph(arabic_text(handover_data['vehicle_condition']), styles['Arabic'])
    
    handover_info_data.append([arabic_text("مستوى الوقود"), fuel_text])
    handover_info_data.append([arabic_text("قراءة العداد"), mileage_text])
    handover_info_data.append([arabic_text("حالة المركبة"), condition_text])
    
    # جدول معلومات التسليم/الاستلام
    handover_table = Table(handover_info_data, colWidths=[100, 300])
    handover_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # محاذاة رأسية وسطية
        # تطبيق خط Amiri على جميع الخلايا ما عدا التي تحتوي على جداول داخلية أو نصوص خاصة
        # تطبيق الخط على كل صف على حدة
        ('FONTNAME', (0, 0), (0, -1), 'Amiri'),  # عناوين الصفوف
        ('FONTNAME', (1, 0), (1, 0), 'Amiri'),    # التاريخ
        ('FONTNAME', (1, 1), (1, 1), 'Amiri'),    # اسم الشخص
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    content.append(handover_table)
    content.append(Spacer(1, 20))
    
    # معلومات فحص المركبة
    content.append(Paragraph(arabic_text("قائمة الفحص"), styles['ArabicSubtitle']))
    content.append(Spacer(1, 10))
    
    # تحضير بيانات الفحص
    items = [
        ("إطار احتياطي", handover_data['has_spare_tire']),
        ("طفاية حريق", handover_data['has_fire_extinguisher']),
        ("حقيبة إسعافات أولية", handover_data['has_first_aid_kit']),
        ("مثلث تحذيري", handover_data['has_warning_triangle']),
        ("أدوات", handover_data['has_tools'])
    ]
    
    # تحويل قيم البوليان إلى نص
    check_data = [
        [arabic_text("العنصر"), arabic_text("الحالة")]
    ]
    
    # إنشاء أنماط خاصة لعلامات الفحص
    check_style = ParagraphStyle(
        name='CheckStyle', 
        fontName='Helvetica',  # استخدام خط مناسب يدعم الرموز الخاصة
        fontSize=14,
        alignment=1,  # توسيط
        textColor=colors.green  # لون أخضر للعلامات الموجبة
    )
    
    unchecked_style = ParagraphStyle(
        name='UncheckedStyle', 
        fontName='Helvetica',
        fontSize=14,
        alignment=1,  # توسيط
        textColor=colors.red  # لون أحمر للعلامات السالبة
    )
    
    for item_name, is_checked in items:
        if is_checked:
            check_mark = Paragraph('<b>&#10004;</b>', check_style)  # علامة صح باللون الأخضر
        else:
            check_mark = Paragraph('<b>&#10008;</b>', unchecked_style)  # علامة خطأ باللون الأحمر
        check_data.append([arabic_text(item_name), check_mark])
    
    # جدول الفحص
    check_table = Table(check_data, colWidths=[200, 200])
    check_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),  # توسيط عنوان العمود الثاني فقط
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # محاذاة رأسية وسطية للجميع
        ('FONTNAME', (0, 0), (0, -1), 'Amiri'),  # تطبيق خط Amiri على العمود الأول فقط
        ('FONTNAME', (0, 0), (1, 0), 'Amiri'),  # تطبيق خط Amiri على العناوين
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    
    content.append(check_table)
    content.append(Spacer(1, 20))
    
    # إضافة قسم الملاحظات
    if handover_data.get('notes'):
        content.append(Paragraph(arabic_text("ملاحظات"), styles['ArabicSubtitle']))
        content.append(Spacer(1, 5))
        notes = Paragraph(arabic_text(handover_data['notes']), styles['Arabic'])
        content.append(notes)
        content.append(Spacer(1, 20))
    
    # إضافة تذييل للصفحة
    footer_text = f"تم إنشاء هذا التقرير بواسطة نُظم - نظام إدارة متكامل في {datetime.now().strftime('%Y-%m-%d')}"  
    footer = Paragraph(arabic_text(footer_text), styles['ArabicSmall'])
    content.append(footer)
    
    # بناء المستند
    doc.build(content)
    
    # إعادة ضبط مؤشر الكائن BytesIO للقراءة
    buffer.seek(0)
    
    # إرجاع كائن BytesIO لاستخدامه في send_file
    return buffer
