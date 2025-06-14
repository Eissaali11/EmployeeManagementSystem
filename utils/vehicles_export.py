"""
وحدة للتصدير والمشاركة في نظام إدارة المركبات
تتضمن وظائف لتصدير بيانات المركبات وسجلات الورشة إلى PDF وExcel
"""

import os
import io
import tempfile
from datetime import datetime
from flask import url_for
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from arabic_reshaper import reshape
from bidi.algorithm import get_display
import pandas as pd

# تسجيل الخطوط العربية
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
    else:
        # استخدام خط افتراضي إذا لم تكن الخطوط العربية متوفرة
        pdfmetrics.registerFont(TTFont('Amiri', 'Helvetica'))
        pdfmetrics.registerFont(TTFont('Amiri-Bold', 'Helvetica-Bold'))


def arabic_text(text):
    """معالجة النص العربي للعرض الصحيح في ملفات PDF"""
    if text is None:
        return ""
    return get_display(reshape(str(text)))


def export_vehicle_pdf(vehicle, workshop_records=None, rental_records=None):
    """
    تصدير بيانات السيارة إلى ملف PDF
    
    Args:
        vehicle: كائن السيارة
        workshop_records: سجلات الورشة (اختياري)
        rental_records: سجلات الإيجار (اختياري)
    
    Returns:
        BytesIO: كائن بايت يحتوي على ملف PDF
    """
    register_fonts()
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
    styles = getSampleStyleSheet()
    
    # إنشاء نمط للنص العربي
    styles.add(ParagraphStyle(name='Arabic', fontName='Amiri', fontSize=12, alignment=1))  # alignment=1 للتوسيط
    styles.add(ParagraphStyle(name='ArabicTitle', fontName='Amiri-Bold', fontSize=16, alignment=1))
    styles.add(ParagraphStyle(name='ArabicHeading', fontName='Amiri-Bold', fontSize=14, alignment=1))
    
    # تحضير المحتوى
    content = []
    
    # إضافة شعار الشركة إذا كان متوفراً
    logo_path = os.path.join(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static"), 'img/logo.png')
    if os.path.exists(logo_path):
        img = Image(logo_path, width=120, height=60)
        content.append(img)
        content.append(Spacer(1, 10))
    
    # عنوان التقرير
    title = Paragraph(arabic_text(f"تقرير بيانات السيارة: {vehicle.plate_number}"), styles['ArabicTitle'])
    content.append(title)
    content.append(Spacer(1, 20))
    
    # معلومات السيارة الأساسية
    content.append(Paragraph(arabic_text("معلومات السيارة الأساسية"), styles['ArabicHeading']))
    content.append(Spacer(1, 10))
    
    # جدول المعلومات الأساسية
    basic_data = [
        [arabic_text("رقم اللوحة"), arabic_text(vehicle.plate_number)],
        [arabic_text("النوع"), arabic_text(f"{vehicle.make} {vehicle.model}")],
        [arabic_text("سنة الصنع"), arabic_text(str(vehicle.year))],
        [arabic_text("اللون"), arabic_text(vehicle.color)],
        [arabic_text("السائق الحالي"), arabic_text(vehicle.driver_name or "غير محدد")],
        [arabic_text("القسم/المالك"), arabic_text(vehicle.department or "غير محدد")],
        [arabic_text("الحالة"), arabic_text({
            'available': 'متاحة',
            'rented': 'مؤجرة',
            'in_workshop': 'في الورشة',
            'in_project': 'في المشروع',
            'accident': 'حادث',
            'sold': 'مباعة'
        }.get(vehicle.status, vehicle.status))],
        [arabic_text("تاريخ انتهاء التأمين"), arabic_text(vehicle.insurance_expiry.strftime("%Y-%m-%d") if vehicle.insurance_expiry else "غير محدد")],
        [arabic_text("تاريخ انتهاء الفحص"), arabic_text(vehicle.inspection_expiry.strftime("%Y-%m-%d") if vehicle.inspection_expiry else "غير محدد")],
    ]
    
    t = Table(basic_data, colWidths=[doc.width/3, 2*doc.width/3])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Amiri'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ]))
    content.append(t)
    content.append(Spacer(1, 20))
    
    # سجلات الورشة إذا كانت متوفرة
    if workshop_records and len(workshop_records) > 0:
        content.append(Paragraph(arabic_text("سجلات الورشة"), styles['ArabicHeading']))
        content.append(Spacer(1, 10))
        
        # تحضير بيانات سجلات الورشة
        workshop_data = [
            [
                arabic_text("سبب الدخول"),
                arabic_text("تاريخ الدخول"),
                arabic_text("تاريخ الخروج"),
                arabic_text("حالة الإصلاح"),
                arabic_text("التكلفة (ريال)"),
                arabic_text("اسم الورشة")
            ]
        ]
        
        for record in workshop_records:
            reason_map = {'maintenance': 'صيانة دورية', 'breakdown': 'عطل', 'accident': 'حادث'}
            status_map = {'in_progress': 'قيد التنفيذ', 'completed': 'تم الإصلاح', 'pending_approval': 'بانتظار الموافقة'}
            
            workshop_data.append([
                arabic_text(reason_map.get(record.reason, record.reason)),
                arabic_text(record.entry_date.strftime("%Y-%m-%d")),
                arabic_text(record.exit_date.strftime("%Y-%m-%d") if record.exit_date else "ما زالت في الورشة"),
                arabic_text(status_map.get(record.repair_status, record.repair_status)),
                arabic_text(f"{record.cost:,.2f}"),
                arabic_text(record.workshop_name or "غير محدد")
            ])
        
        t = Table(workshop_data, colWidths=[doc.width/6] * 6)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('ALIGN', (4, 1), (4, -1), 'LEFT'),  # محاذاة أرقام التكلفة إلى اليسار
            ('FONTNAME', (0, 0), (-1, -1), 'Amiri'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        content.append(t)
        content.append(Spacer(1, 10))
        
        # إجمالي تكاليف الصيانة
        total_cost = sum(record.cost for record in workshop_records)
        cost_text = Paragraph(arabic_text(f"إجمالي تكاليف الصيانة: {total_cost:,.2f} ريال"), styles['Arabic'])
        content.append(cost_text)
        content.append(Spacer(1, 20))
    
    # سجلات الإيجار إذا كانت متوفرة
    if rental_records and len(rental_records) > 0:
        content.append(Paragraph(arabic_text("سجلات الإيجار"), styles['ArabicHeading']))
        content.append(Spacer(1, 10))
        
        # تحضير بيانات سجلات الإيجار
        rental_data = [
            [
                arabic_text("المستأجر"),
                arabic_text("تاريخ البداية"),
                arabic_text("تاريخ النهاية"),
                arabic_text("التكلفة (ريال)"),
                arabic_text("الحالة")
            ]
        ]
        
        for record in rental_records:
            rental_data.append([
                arabic_text(record.renter_name),
                arabic_text(record.start_date.strftime("%Y-%m-%d")),
                arabic_text(record.end_date.strftime("%Y-%m-%d") if record.end_date else "مستمر"),
                arabic_text(f"{record.cost:,.2f}"),
                arabic_text("نشط" if record.is_active else "منتهي")
            ])
        
        t = Table(rental_data, colWidths=[doc.width/5] * 5)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('ALIGN', (3, 1), (3, -1), 'LEFT'),  # محاذاة أرقام التكلفة إلى اليسار
            ('FONTNAME', (0, 0), (-1, -1), 'Amiri'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOX', (0, 0), (-1, -1), 1, colors.black),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
        ]))
        content.append(t)
        content.append(Spacer(1, 20))
    
    # بيانات التوقيع والطباعة
    footer_text = Paragraph(
        arabic_text(f"تم إنشاء هذا التقرير بواسطة نُظم - نظام إدارة متكامل في {datetime.now().strftime('%Y-%m-%d %H:%M')}"),
        styles['Arabic']
    )
    content.append(footer_text)
    
    # بناء الوثيقة
    doc.build(content)
    buffer.seek(0)
    return buffer


def export_workshop_records_pdf(vehicle, workshop_records):
    """
    تصدير سجلات الورشة لسيارة معينة إلى ملف PDF
    
    Args:
        vehicle: كائن السيارة
        workshop_records: سجلات الورشة
    
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
    
    # إضافة شعار الشركة إذا كان متوفراً
    logo_path = os.path.join(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static"), 'img/logo.png')
    if os.path.exists(logo_path):
        img = Image(logo_path, width=120, height=60)
        content.append(img)
        content.append(Spacer(1, 10))
    
    # عنوان التقرير
    title = Paragraph(arabic_text(f"تقرير سجلات الورشة للسيارة: {vehicle.plate_number}"), styles['ArabicTitle'])
    content.append(title)
    content.append(Spacer(1, 10))
    
    # معلومات السيارة الأساسية
    vehicle_info = Paragraph(
        arabic_text(f"السيارة: {vehicle.make} {vehicle.model} {vehicle.year} - {vehicle.color}"),
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
                arabic_text("سبب الدخول"),
                arabic_text("تاريخ الدخول"),
                arabic_text("تاريخ الخروج"),
                arabic_text("حالة الإصلاح"),
                arabic_text("التكلفة (ريال)"),
                arabic_text("اسم الورشة"),
                arabic_text("الفني المسؤول")
            ]
        ]
        
        for record in workshop_records:
            reason_map = {'maintenance': 'صيانة دورية', 'breakdown': 'عطل', 'accident': 'حادث'}
            status_map = {'in_progress': 'قيد التنفيذ', 'completed': 'تم الإصلاح', 'pending_approval': 'بانتظار الموافقة'}
            
            workshop_data.append([
                arabic_text(reason_map.get(record.reason, record.reason)),
                arabic_text(record.entry_date.strftime("%Y-%m-%d")),
                arabic_text(record.exit_date.strftime("%Y-%m-%d") if record.exit_date else "ما زالت في الورشة"),
                arabic_text(status_map.get(record.repair_status, record.repair_status)),
                arabic_text(f"{record.cost:,.2f}"),
                arabic_text(record.workshop_name or "غير محدد"),
                arabic_text(record.technician_name or "غير محدد")
            ])
        
        t = Table(workshop_data, colWidths=[doc.width/7] * 7)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('ALIGN', (4, 1), (4, -1), 'LEFT'),  # محاذاة أرقام التكلفة إلى اليسار
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
        total_cost = sum(record.cost for record in workshop_records)
        cost_text = Paragraph(arabic_text(f"إجمالي تكاليف الصيانة: {total_cost:,.2f} ريال"), styles['Arabic'])
        content.append(cost_text)
        
        # إجمالي عدد أيام الورشة
        days_in_workshop = sum(
            (record.exit_date - record.entry_date).days + 1 if record.exit_date else 
            (datetime.now().date() - record.entry_date).days + 1
            for record in workshop_records
        )
        days_text = Paragraph(arabic_text(f"إجمالي عدد أيام الورشة: {days_in_workshop} يوم"), styles['Arabic'])
        content.append(days_text)
    else:
        content.append(Paragraph(arabic_text("لا توجد سجلات ورشة لهذه السيارة"), styles['Arabic']))
    
    content.append(Spacer(1, 20))
    
    # بيانات التوقيع والطباعة
    footer_text = Paragraph(
        arabic_text(f"تم إنشاء هذا التقرير بواسطة نُظم - نظام إدارة متكامل في {datetime.now().strftime('%Y-%m-%d %H:%M')}"),
        styles['Arabic']
    )
    content.append(footer_text)
    
    # بناء الوثيقة
    doc.build(content)
    buffer.seek(0)
    return buffer


def export_vehicle_excel(vehicle, workshop_records=None, rental_records=None):
    """
    تصدير بيانات السيارة إلى ملف Excel
    
    Args:
        vehicle: كائن السيارة
        workshop_records: سجلات الورشة (اختياري)
        rental_records: سجلات الإيجار (اختياري)
    
    Returns:
        BytesIO: كائن بايت يحتوي على ملف Excel
    """
    buffer = io.BytesIO()
    
    try:
        # إنشاء مصنف Excel مع عدة أوراق عمل
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            
            # ورقة المعلومات الأساسية
            basic_data = {
                'البيان': [
                    'رقم اللوحة', 'النوع', 'سنة الصنع', 'اللون', 'السائق الحالي',
                    'الحالة', 'تاريخ انتهاء الفحص الدوري', 'تاريخ انتهاء الاستمارة', 'الملاحظات'
                ],
                'القيمة': [
                    vehicle.plate_number or '',
                    f"{vehicle.make or ''} {vehicle.model or ''}".strip(),
                    str(vehicle.year) if vehicle.year else '',
                    vehicle.color or '',
                    vehicle.driver_name or "غير محدد",
                    {
                        'available': 'متاحة',
                        'rented': 'مؤجرة', 
                        'in_workshop': 'في الورشة',
                        'in_project': 'في المشروع',
                        'accident': 'حادث',
                        'sold': 'مباعة'
                    }.get(vehicle.status, vehicle.status or ''),
                    vehicle.inspection_expiry_date.strftime("%Y-%m-%d") if vehicle.inspection_expiry_date else "غير محدد",
                    vehicle.registration_expiry_date.strftime("%Y-%m-%d") if vehicle.registration_expiry_date else "غير محدد",
                    vehicle.notes or "لا توجد ملاحظات"
                ]
            }
            
            # إنشاء DataFrame وكتابته إلى ورقة العمل
            df_basic = pd.DataFrame(basic_data)
            df_basic.to_excel(writer, sheet_name='معلومات السيارة', index=False)
            
            # إذا كانت سجلات الورشة متوفرة
            if workshop_records and len(workshop_records) > 0:
                # تحويل سجلات الورشة إلى DataFrame
                workshop_data = []
                
                for record in workshop_records:
                    reason_map = {'maintenance': 'صيانة دورية', 'breakdown': 'عطل', 'accident': 'حادث'}
                    status_map = {'in_progress': 'قيد التنفيذ', 'completed': 'تم الإصلاح', 'pending_approval': 'بانتظار الموافقة'}
                    
                    workshop_data.append({
                        'سبب الدخول': reason_map.get(record.reason, record.reason or "غير محدد"),
                        'تاريخ الدخول': record.entry_date.strftime("%Y-%m-%d") if record.entry_date else "غير محدد",
                        'تاريخ الخروج': record.exit_date.strftime("%Y-%m-%d") if record.exit_date else "ما زالت في الورشة",
                        'حالة الإصلاح': status_map.get(record.repair_status, record.repair_status or "غير محدد"),
                        'التكلفة (ريال)': record.cost or 0,
                        'اسم الورشة': record.workshop_name or "غير محدد",
                        'الفني المسؤول': record.technician_name or "غير محدد",
                        'الوصف': record.description or "",
                        'ملاحظات': record.notes or ""
                    })
                
                df_workshop = pd.DataFrame(workshop_data)
                df_workshop.to_excel(writer, sheet_name='سجلات الورشة', index=False)
            
            # إذا كانت سجلات الإيجار متوفرة
            if rental_records and len(rental_records) > 0:
                # تحويل سجلات الإيجار إلى DataFrame
                rental_data = []
                
                for record in rental_records:
                    rental_data.append({
                        'المستأجر': record.lessor_name or "غير محدد",
                        'تاريخ البداية': record.start_date.strftime("%Y-%m-%d") if record.start_date else "غير محدد",
                        'تاريخ النهاية': record.end_date.strftime("%Y-%m-%d") if record.end_date else "مستمر",
                        'التكلفة الشهرية (ريال)': record.monthly_cost or 0,
                        'الحالة': "نشط" if record.is_active else "منتهي",
                        'جهة الاتصال': record.lessor_contact or "",
                        'رقم العقد': record.contract_number or "",
                        'المدينة': record.city or "",
                        'ملاحظات': record.notes or ""
                    })
                
                df_rental = pd.DataFrame(rental_data)
                df_rental.to_excel(writer, sheet_name='سجلات الإيجار', index=False)
        
        buffer.seek(0)
        return buffer
        
    except Exception as e:
        print(f"خطأ في تصدير بيانات السيارة: {str(e)}")
        # إنشاء ملف Excel بسيط في حالة الخطأ
        simple_data = {
            'البيان': ['رقم اللوحة', 'النوع', 'سنة الصنع', 'اللون', 'السائق الحالي', 'الحالة'],
            'القيمة': [
                vehicle.plate_number or '',
                f"{vehicle.make or ''} {vehicle.model or ''}".strip(),
                str(vehicle.year) if vehicle.year else '',
                vehicle.color or '',
                vehicle.driver_name or "غير محدد",
                vehicle.status or ''
            ]
        }
        
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_simple = pd.DataFrame(simple_data)
            df_simple.to_excel(writer, sheet_name='معلومات السيارة', index=False)
        
        buffer.seek(0)
        return buffer


def export_workshop_records_excel(vehicle, workshop_records):
    """
    تصدير سجلات الورشة لسيارة معينة إلى ملف Excel
    
    Args:
        vehicle: كائن السيارة
        workshop_records: سجلات الورشة
    
    Returns:
        BytesIO: كائن بايت يحتوي على ملف Excel
    """
    buffer = io.BytesIO()
    
    try:
        # إنشاء مصنف Excel
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            # معلومات السيارة
            vehicle_info = {
                'البيان': ['رقم اللوحة', 'النوع', 'سنة الصنع', 'اللون'],
                'القيمة': [
                    vehicle.plate_number or '',
                    f"{vehicle.make or ''} {vehicle.model or ''}".strip(),
                    str(vehicle.year) if vehicle.year else '',
                    vehicle.color or ''
                ]
            }
            
            # إنشاء ورقة معلومات السيارة
            df_vehicle = pd.DataFrame(vehicle_info)
            df_vehicle.to_excel(writer, sheet_name='معلومات السيارة', index=False)
            
            # إنشاء ورقة سجلات الورشة
            if workshop_records:
                workshop_data = []
                for record in workshop_records:
                    workshop_data.append({
                        'تاريخ الدخول': record.entry_date.strftime("%Y-%m-%d") if record.entry_date else "غير محدد",
                        'تاريخ الخروج': record.exit_date.strftime("%Y-%m-%d") if record.exit_date else "ما زالت في الورشة",
                        'سبب الدخول': record.reason or "غير محدد",
                        'الوصف': record.description or "",
                        'التكلفة': record.cost or 0,
                        'ملاحظات': record.notes or ""
                    })
                
                df_workshop = pd.DataFrame(workshop_data)
                df_workshop.to_excel(writer, sheet_name='سجلات الورشة', index=False)
        
        buffer.seek(0)
        return buffer
        
    except Exception as e:
        print(f"خطأ في تصدير سجلات الورشة: {str(e)}")
        # إنشاء ملف بسيط في حالة الخطأ
        simple_data = {
            'البيان': ['رقم اللوحة', 'النوع'],
            'القيمة': [vehicle.plate_number or '', f"{vehicle.make or ''} {vehicle.model or ''}".strip()]
        }
        
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_simple = pd.DataFrame(simple_data)
            df_simple.to_excel(writer, sheet_name='معلومات السيارة', index=False)
        
        buffer.seek(0)
        return buffer


def export_all_vehicles_to_excel():
    """
    تصدير جميع بيانات المركبات إلى ملف Excel شامل
    
    Returns:
        Flask Response: استجابة Flask مع ملف Excel
    """
    from flask import make_response, flash, redirect, url_for
    from models import Vehicle, VehicleWorkshop
    import openpyxl
    from openpyxl.styles import Font, Alignment, PatternFill
    
    try:
        # الحصول على جميع المركبات
        vehicles = Vehicle.query.order_by(Vehicle.plate_number).all()
        
        if not vehicles:
            flash("لا توجد مركبات للتصدير!", "warning")
            return redirect(url_for("vehicles.index"))
        
        # إنشاء مصنف Excel جديد
        wb = openpyxl.Workbook()
        
        # إزالة الورقة الافتراضية
        wb.remove(wb.active)
        
        # إنشاء ورقة المركبات الأساسية
        vehicles_ws = wb.create_sheet("المركبات")
        
        # إعداد التنسيق
        header_font = Font(bold=True, color="FFFFFF")
        header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
        center_alignment = Alignment(horizontal="center", vertical="center")
        
        # عناوين الأعمدة للمركبات
        vehicle_headers = [
            "رقم اللوحة", "الماركة", "الموديل", "سنة الصنع", "اللون",
            "اسم السائق", "الحالة", "تاريخ انتهاء الفحص الدوري",
            "تاريخ انتهاء الاستمارة", "تاريخ انتهاء التفويض",
            "ملاحظات", "تاريخ الإضافة"
        ]
        
        # إضافة العناوين
        for col, header in enumerate(vehicle_headers, 1):
            cell = vehicles_ws.cell(row=1, column=col, value=header)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = center_alignment
        
        # إضافة بيانات المركبات
        for row, vehicle in enumerate(vehicles, 2):
            vehicles_ws.cell(row=row, column=1, value=vehicle.plate_number or "")
            vehicles_ws.cell(row=row, column=2, value=vehicle.make or "")
            vehicles_ws.cell(row=row, column=3, value=vehicle.model or "")
            vehicles_ws.cell(row=row, column=4, value=vehicle.year or "")
            vehicles_ws.cell(row=row, column=5, value=vehicle.color or "")
            vehicles_ws.cell(row=row, column=6, value=vehicle.driver_name or "")
            
            # ترجمة حالة المركبة
            status_map = {
                "available": "متاحة",
                "rented": "مؤجرة",
                "in_use": "في الاستخدام",
                "maintenance": "في الصيانة",
                "in_workshop": "في الورشة",
                "in_project": "في المشروع",
                "accident": "حادث",
                "sold": "مباعة"
            }
            vehicles_ws.cell(row=row, column=7, value=status_map.get(vehicle.status, vehicle.status or ""))
            
            # تواريخ انتهاء الوثائق
            vehicles_ws.cell(row=row, column=8, value=vehicle.inspection_expiry_date.strftime("%Y-%m-%d") if vehicle.inspection_expiry_date else "")
            vehicles_ws.cell(row=row, column=9, value=vehicle.registration_expiry_date.strftime("%Y-%m-%d") if vehicle.registration_expiry_date else "")
            vehicles_ws.cell(row=row, column=10, value=vehicle.authorization_expiry_date.strftime("%Y-%m-%d") if vehicle.authorization_expiry_date else "")
            vehicles_ws.cell(row=row, column=11, value=vehicle.notes or "")
            vehicles_ws.cell(row=row, column=12, value=vehicle.created_at.strftime("%Y-%m-%d") if vehicle.created_at else "")
        
        # تعديل عرض الأعمدة
        for col in range(1, len(vehicle_headers) + 1):
            vehicles_ws.column_dimensions[openpyxl.utils.get_column_letter(col)].width = 15
        
        # حفظ الملف في الذاكرة
        buffer = io.BytesIO()
        wb.save(buffer)
        buffer.seek(0)
        
        # إنشاء الاستجابة
        response = make_response(buffer.getvalue())
        response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        response.headers["Content-Disposition"] = f"attachment; filename=vehicles_export_{timestamp}.xlsx"
        
        return response
        
    except Exception as e:
        flash(f"خطأ في تصدير البيانات: {str(e)}", "danger")
        return redirect(url_for("vehicles.index"))
