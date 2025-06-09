"""
وحدة إنشاء ملفات PDF باستخدام ReportLab مع دعم للغة العربية
"""
import os
from io import BytesIO
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm
import arabic_reshaper
from bidi.algorithm import get_display

# تسجيل الخطوط المستخدمة
def register_fonts():
    """تسجيل الخطوط المستخدمة في التقارير"""
    # نستخدم الخط الافتراضي في ReportLab وهو Helvetica
    # لا نحتاج لتسجيل خط خاص
    pass

# إنشاء الأنماط للتقارير
def get_styles():
    """الحصول على أنماط النصوص للتقارير"""
    styles = getSampleStyleSheet()
    
    # إنشاء نمط للنص العربي
    arabic_style = ParagraphStyle(
        name='ArabicStyle',
        parent=styles['Normal'],
        fontName='Helvetica',  # استخدام الخط الافتراضي
        fontSize=10,
        alignment=2,  # يمين (RTL)
        textColor=colors.black
    )
    
    # إنشاء نمط للعناوين
    title_style = ParagraphStyle(
        name='ArabicTitle',
        parent=styles['Title'],
        fontName='Helvetica-Bold',  # استخدام الخط الافتراضي مع نمط عريض
        fontSize=16,
        alignment=1,  # وسط
        textColor=colors.black
    )
    
    # إنشاء نمط للعناوين الفرعية
    subtitle_style = ParagraphStyle(
        name='ArabicSubtitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',  # استخدام الخط الافتراضي مع نمط عريض
        fontSize=14,
        alignment=2,  # يمين (RTL)
        textColor=colors.blue
    )
    
    return {
        'arabic': arabic_style,
        'title': title_style,
        'subtitle': subtitle_style
    }

# تجهيز النص العربي للعرض في PDF
def arabic_text(text):
    """
    تحويل النص العربي ليعرض بشكل صحيح في PDF
    
    Args:
        text: النص العربي المراد عرضه
        
    Returns:
        النص بعد المعالجة
    """
    if not text:
        return ""
    
    reshaped_text = arabic_reshaper.reshape(str(text))
    bidi_text = get_display(reshaped_text)
    return bidi_text

# إنشاء ملف PDF
def create_pdf(elements, landscape_mode=False):
    """
    إنشاء ملف PDF يحتوي على العناصر المحددة
    
    Args:
        elements: قائمة بالعناصر المراد إضافتها للتقرير
        landscape_mode: هل التقرير بالوضع الأفقي (Landscape)
        
    Returns:
        BytesIO يحتوي على ملف PDF
    """
    # تسجيل الخطوط
    register_fonts()
    
    # إنشاء وثيقة جديدة
    buffer = BytesIO()
    pagesize = landscape(A4) if landscape_mode else A4
    
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=pagesize,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # بناء المستند
    doc.build(elements)
    
    # إعادة المؤشر إلى بداية البايت
    buffer.seek(0)
    
    return buffer

# إنشاء جدول بيانات متعدد الأعمدة
def create_data_table(headers, data, col_widths=None):
    """
    إنشاء جدول بيانات متعدد الأعمدة
    
    Args:
        headers: قائمة بعناوين الأعمدة
        data: قائمة الصفوف (كل صف عبارة عن قائمة من القيم)
        col_widths: عرض الأعمدة (اختياري)
        
    Returns:
        كائن Table
    """
    # تجهيز عناوين الأعمدة بالعربية
    headers_display = [arabic_text(h) for h in headers]
    
    # إنشاء الجدول
    all_data = [headers_display]
    all_data.extend(data)
    
    # إنشاء الجدول مع تحديد عرض الأعمدة
    if col_widths:
        table = Table(all_data, colWidths=col_widths)
    else:
        table = Table(all_data)
    
    # تنسيق الجدول
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ])
    
    # تطبيق التناوب في ألوان الصفوف
    for i in range(1, len(all_data)):
        if i % 2 == 0:
            table_style.add('BACKGROUND', (0, i), (-1, i), colors.whitesmoke)
    
    table.setStyle(table_style)
    return table