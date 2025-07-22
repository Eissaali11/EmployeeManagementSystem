"""
مولد تقارير تسليم/استلام المركبات باستخدام ReportLab مع خط beIN-Normal
"""

import os
import io
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import arabic_reshaper
from bidi.algorithm import get_display

def register_arabic_fonts():
    """تسجيل الخطوط العربية مع التركيز على خط beIN-Normal"""
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        fonts_dir = os.path.join(base_dir, 'static', 'fonts')
        
        # تسجيل خط beIN-Normal
        bein_font_path = os.path.join(fonts_dir, 'beIN-Normal.ttf')
        if os.path.exists(bein_font_path):
            pdfmetrics.registerFont(TTFont('beIN-Normal', bein_font_path))
            print("تم تسجيل خط beIN-Normal بنجاح")
            return True
        else:
            print(f"خط beIN-Normal غير موجود في المسار: {bein_font_path}")
            return False
    except Exception as e:
        print(f"خطأ في تسجيل الخطوط: {e}")
        return False

def format_arabic_text(text):
    """تنسيق النص العربي للعرض الصحيح في PDF"""
    if not text:
        return ""
    try:
        reshaped_text = arabic_reshaper.reshape(str(text))
        return get_display(reshaped_text)
    except:
        return str(text)

def generate_handover_pdf_with_bein(handover_data):
    """
    إنشاء تقرير تسليم/استلام باستخدام خط beIN-Normal
    
    Args:
        handover_data: بيانات التسليم/الاستلام
    
    Returns:
        BytesIO: ملف PDF
    """
    # تسجيل الخطوط
    font_registered = register_arabic_fonts()
    if not font_registered:
        raise Exception("فشل في تسجيل خط beIN-Normal")
    
    # إنشاء buffer لـ PDF
    buffer = io.BytesIO()
    
    # إنشاء المستند
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=60,
        bottomMargin=30
    )
    
    # إعداد الأنماط
    styles = getSampleStyleSheet()
    
    # إضافة أنماط عربية جديدة
    styles.add(ParagraphStyle(
        name='ArabicTitle',
        fontName='beIN-Normal',
        fontSize=18,
        alignment=1,  # وسط
        spaceAfter=20
    ))
    
    styles.add(ParagraphStyle(
        name='ArabicSubtitle',
        fontName='beIN-Normal',
        fontSize=14,
        alignment=1,
        spaceAfter=15
    ))
    
    styles.add(ParagraphStyle(
        name='ArabicNormal',
        fontName='beIN-Normal',
        fontSize=12,
        alignment=2,  # يمين
        spaceAfter=10
    ))
    
    # محتوى PDF
    content = []
    
    # العنوان الرئيسي
    title = handover_data.get('handover_type', 'تسليم')
    content.append(Paragraph(format_arabic_text(f"نموذج {title} مركبة"), styles['ArabicTitle']))
    content.append(Spacer(1, 20))
    
    # معلومات الشركة والعمل
    company_info = [
        [format_arabic_text("رقم الشركة"), format_arabic_text(handover_data.get('work_order_number', ''))],
        [format_arabic_text("حالة المركبة"), format_arabic_text(handover_data.get('vehicle', {}).get('vehicle_status', 'متاحة'))],
        [format_arabic_text("تاريخ العملية"), format_arabic_text(handover_data.get('handover_date', ''))]
    ]
    
    company_table = Table(company_info, colWidths=[2*inch, 3*inch])
    company_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('FONTNAME', (0, 0), (-1, -1), 'beIN-Normal'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    
    content.append(Paragraph(format_arabic_text("معلومات الشركة"), styles['ArabicSubtitle']))
    content.append(company_table)
    content.append(Spacer(1, 15))

    # معلومات المركبة
    vehicle = handover_data.get('vehicle', {})
    vehicle_info = [
        [format_arabic_text("رقم اللوحة"), format_arabic_text(vehicle.get('plate_number', ''))],
        [format_arabic_text("الماركة"), format_arabic_text(vehicle.get('make', ''))],
        [format_arabic_text("الموديل"), format_arabic_text(vehicle.get('model', ''))],
        [format_arabic_text("السنة"), str(vehicle.get('year', ''))],
        [format_arabic_text("اللون"), format_arabic_text(vehicle.get('color', ''))]
    ]
    
    vehicle_table = Table(vehicle_info, colWidths=[100, 200])
    vehicle_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 0), (-1, -1), 'beIN-Normal'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    content.append(Paragraph(format_arabic_text("معلومات المركبة"), styles['ArabicSubtitle']))
    content.append(vehicle_table)
    content.append(Spacer(1, 20))
    
    # معلومات التسليم/الاستلام
    handover_info = [
        [format_arabic_text("التاريخ"), format_arabic_text(handover_data.get('handover_date', ''))],
        [format_arabic_text("النوع"), format_arabic_text(handover_data.get('handover_type', ''))],
        [format_arabic_text("اسم الشخص"), format_arabic_text(handover_data.get('person_name', ''))],
        [format_arabic_text("اسم الموظف"), format_arabic_text(handover_data.get('employee_name', ''))],
        [format_arabic_text("رقم الموظف"), format_arabic_text(handover_data.get('emp_id', ''))],
        [format_arabic_text("عداد الكيلومترات"), str(handover_data.get('mileage', ''))],
        [format_arabic_text("مستوى الوقود"), format_arabic_text(handover_data.get('fuel_level', ''))]
    ]
    
    handover_table = Table(handover_info, colWidths=[100, 200])
    handover_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 0), (-1, -1), 'beIN-Normal'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    
    content.append(Paragraph(format_arabic_text(f"بيانات {title}"), styles['ArabicSubtitle']))
    content.append(handover_table)
    content.append(Spacer(1, 20))
    
    # الملاحظات
    notes = handover_data.get('notes', '')
    if notes:
        content.append(Paragraph(format_arabic_text("ملاحظات"), styles['ArabicSubtitle']))
        content.append(Paragraph(format_arabic_text(notes), styles['ArabicNormal']))
        content.append(Spacer(1, 20))
    
    # التوقيعات
    signatures_data = [
        [format_arabic_text("توقيع المُسلم"), format_arabic_text("توقيع المُستلم")],
        ["", ""],
        ["", ""],
        [format_arabic_text("التاريخ: ___________"), format_arabic_text("التاريخ: ___________")]
    ]
    
    signatures_table = Table(signatures_data, colWidths=[150, 150])
    signatures_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ('FONTNAME', (0, 0), (-1, -1), 'beIN-Normal'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0, 0), (-1, 0), [colors.lightgrey]),
        ('TOPPADDING', (0, 0), (-1, -1), 15),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
    ]))
    
    content.append(Paragraph(format_arabic_text("التوقيعات"), styles['ArabicSubtitle']))
    content.append(signatures_table)
    
    # بناء PDF
    doc.build(content)
    
    # إرجاع buffer
    buffer.seek(0)
    return buffer

def handover_pdf_public(handover_id):
    """دالة عامة لإنشاء PDF لتسليم/استلام مركبة"""
    try:
        # استيراد محلي لتجنب الاستيراد الدائري
        import sys
        sys.path.append('/home/runner/workspace')
        
        from sqlalchemy import text
        from app import db
        
        # جلب بيانات التسليم/الاستلام باستخدام SQL مباشر مع جميع البيانات المطلوبة
        result = db.session.execute(text("""
            SELECT vh.*, v.plate_number, v.make, v.model, v.year, v.color, v.vehicle_status,
                   e.name as employee_name, e.employee_id as emp_id
            FROM vehicle_handover vh
            LEFT JOIN vehicle v ON vh.vehicle_id = v.id
            LEFT JOIN employee e ON vh.employee_id = e.id
            WHERE vh.id = :handover_id
        """), {'handover_id': handover_id}).fetchone()
        
        if not result:
            print(f"سجل التسليم/الاستلام برقم {handover_id} غير موجود")
            return None
        
        # تحضير البيانات من النتيجة
        handover_data = {
            'handover_type': result.handover_type_ar or 'تسليم',
            'handover_date': result.handover_date.strftime('%Y-%m-%d') if result.handover_date else '',
            'person_name': result.person_name or '',
            'employee_name': result.employee_name or '',
            'emp_id': result.emp_id or '',
            'mileage': result.mileage or 0,
            'fuel_level': result.fuel_level or '',
            'notes': result.notes or '',
            'work_order_number': f"W{handover_id:06d}",  # رقم العمل
            'vehicle': {
                'plate_number': result.plate_number or '',
                'make': result.make or '',
                'model': result.model or '',
                'year': result.year or '',
                'color': result.color or '',
                'vehicle_status': result.vehicle_status or 'متاحة'  # حالة المركبة
            }
        }
        
        # إنشاء PDF
        return generate_handover_pdf_with_bein(handover_data)
        
    except Exception as e:
        print(f"خطأ في إنشاء PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return None