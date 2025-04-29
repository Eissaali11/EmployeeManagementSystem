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
    return get_display(reshape(str(text)))

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
    
    # إضافة شعار النظام (إذا وجد)
    logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'images', 'logo_new.png')
    try:
        if os.path.exists(logo_path):
            img = Image(logo_path, width=30*mm, height=30*mm)
            content.append(img)
        else:
            try:
                # محاولة البحث في المسار البديل
                static_folder = current_app.static_folder
                logo_path = os.path.join(static_folder, 'images', 'logo_new.png')
                if os.path.exists(logo_path):
                    img = Image(logo_path, width=30*mm, height=30*mm)
                    content.append(img)
            except Exception as e:
                print(f"لم يتم العثور على الشعار: {str(e)}")
    except Exception as e:
        print(f"خطأ في إضافة الشعار: {str(e)}")
    
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
    handover_info_data = [
        [arabic_text("التاريخ"), arabic_text(handover_data['handover_date'])],
        [arabic_text("الشخص"), arabic_text(handover_data['person_name'])],
    ]
    
    # إضافة معلومات المشرف إذا وجدت
    if handover_data.get('supervisor_name'):
        handover_info_data.append([arabic_text("المشرف"), arabic_text(handover_data['supervisor_name'])])
    
    # إضافة رابط النموذج إذا وجد كرابط قابل للنقر
    if handover_data.get('form_link'):
        from reportlab.lib.colors import blue
        link_style = ParagraphStyle(
            name='LinkStyle',
            parent=styles['Arabic'],
            textColor=blue,
            underline=True
        )
        link_text = Paragraph(f'<link href="{handover_data["form_link"]}">{arabic_text(handover_data["form_link"])}</link>', link_style)
        handover_info_data.append([arabic_text("رابط النموذج"), link_text])
    
    # إضافة مستوى الوقود وعداد المسافة
    handover_info_data.append([arabic_text("مستوى الوقود"), arabic_text(handover_data['fuel_level'])])
    handover_info_data.append([arabic_text("قراءة العداد"), arabic_text(str(handover_data['mileage']))])
    handover_info_data.append([arabic_text("حالة المركبة"), arabic_text(handover_data['vehicle_condition'])])
    
    # جدول معلومات التسليم/الاستلام
    handover_table = Table(handover_info_data, colWidths=[100, 300])
    handover_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # محاذاة رأسية وسطية
        ('FONTNAME', (0, 0), (0, -1), 'Amiri'),  # نستثني العمود الثاني من تعيين الخط لأنه قد يحتوي على نصوص بأنماط مختلفة
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
    
    for item_name, is_checked in items:
        status = "✓" if is_checked else "✗"
        check_data.append([arabic_text(item_name), status])
    
    # جدول الفحص
    check_table = Table(check_data, colWidths=[200, 200])
    check_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Amiri'),
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
    
    return buffer.getvalue()
