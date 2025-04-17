"""
وحدة إنشاء ملفات PDF باستخدام ReportLab مع معالجة خاصة للنصوص العربية
"""
from io import BytesIO
import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm

def reshape_arabic_text(text):
    """
    تشكيل النص العربي بشكل صحيح للعرض في ملفات PDF
    
    Args:
        text: النص العربي المراد تشكيله
        
    Returns:
        النص بعد التشكيل
    """
    if not text:
        return ""
    # تشكيل النص العربي
    reshaped_text = arabic_reshaper.reshape(str(text))
    # عكس النص لدعم اللغة العربية (من اليمين إلى اليسار)
    bidi_text = get_display(reshaped_text)
    return bidi_text

def get_arabic_styles():
    """
    الحصول على أنماط النصوص العربية للاستخدام في PDF
    
    Returns:
        قاموس بالأنماط المختلفة للنصوص العربية
    """
    styles = getSampleStyleSheet()
    
    # نمط العنوان
    title_style = ParagraphStyle(
        'Arabic_Title',
        parent=styles['Title'],
        alignment=1,  # وسط
        fontName='Helvetica',
        fontSize=16,
        spaceAfter=14,
        leading=20
    )
    
    # نمط العنوان الفرعي
    heading_style = ParagraphStyle(
        'Arabic_Heading',
        parent=styles['Heading2'],
        alignment=1,  # وسط
        fontName='Helvetica',
        fontSize=14,
        spaceAfter=12,
        leading=18
    )
    
    # نمط النص الأساسي
    normal_style = ParagraphStyle(
        'Arabic_Normal',
        parent=styles['Normal'],
        alignment=2,  # يمين
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        spaceAfter=10
    )
    
    return {
        'title': title_style,
        'heading': heading_style,
        'normal': normal_style
    }

def create_rtl_table(data, col_widths=None, style=None):
    """
    إنشاء جدول يدعم النصوص العربية من اليمين إلى اليسار
    
    Args:
        data: بيانات الجدول (مصفوفة ثنائية)
        col_widths: عرض الأعمدة (اختياري)
        style: نمط الجدول (اختياري)
        
    Returns:
        كائن Table
    """
    # إنشاء الجدول
    table = Table(data, colWidths=col_widths)
    
    # تطبيق النمط الافتراضي إذا لم يتم تحديد نمط
    if not style:
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ])
    
    table.setStyle(style)
    return table

def create_arabic_pdf(elements, title="تقرير", filename=None, landscape_mode=False):
    """
    إنشاء ملف PDF يحتوي على نصوص عربية
    
    Args:
        elements: قائمة بالعناصر المراد إضافتها للتقرير
        title: عنوان الملف (اختياري)
        filename: اسم الملف (اختياري، إذا كان None سيتم إرجاع البيانات فقط)
        landscape_mode: هل التقرير بالوضع الأفقي (اختياري)
        
    Returns:
        BytesIO أو None
    """
    # تحديد حجم الصفحة
    pagesize = landscape(A4) if landscape_mode else A4
    
    # إنشاء كائن BytesIO لاحتواء البيانات
    buffer = BytesIO()
    
    # إنشاء مستند PDF
    doc = SimpleDocTemplate(
        filename or buffer,
        title=reshape_arabic_text(title),
        pagesize=pagesize,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm
    )
    
    # بناء المستند
    doc.build(elements)
    
    # إذا كان هناك اسم ملف، فلن نحتاج لإرجاع البيانات
    if filename:
        return None
    
    # إعادة توجيه المؤشر إلى بداية البيانات
    buffer.seek(0)
    return buffer.getvalue()