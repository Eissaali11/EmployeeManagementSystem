"""
مولد PDF مثالي للنصوص العربية باستخدام الخطوط المحملة
يستخدم ReportLab مع خط Noto Sans Arabic الحقيقي
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import arabic_reshaper
from bidi.algorithm import get_display
from datetime import datetime
import os
import io

def register_arabic_font():
    """تسجيل الخط العربي في ReportLab"""
    try:
        # محاولة تسجيل خط Noto Sans Arabic
        noto_path = 'static/fonts/NotoSansArabic-Regular.ttf'
        if os.path.exists(noto_path):
            pdfmetrics.registerFont(TTFont('ArabicFont', noto_path))
            print("تم تسجيل خط Noto Sans Arabic بنجاح")
            return True
        
        # محاولة تسجيل خط Amiri كبديل
        amiri_path = 'static/fonts/Amiri-Regular.ttf'
        if os.path.exists(amiri_path):
            pdfmetrics.registerFont(TTFont('ArabicFont', amiri_path))
            print("تم تسجيل خط Amiri بنجاح")
            return True
            
        print("لم يتم العثور على الخطوط العربية")
        return False
        
    except Exception as e:
        print(f"خطأ في تسجيل الخط العربي: {e}")
        return False

def format_arabic_text(text):
    """تنسيق النص العربي للعرض الصحيح في PDF"""
    if not text:
        return ""
    
    try:
        text_str = str(text)
        # إعادة تشكيل النص العربي للعرض الصحيح
        reshaped_text = arabic_reshaper.reshape(text_str)
        # تطبيق خوارزمية الاتجاه الثنائي
        bidi_text = get_display(reshaped_text)
        return bidi_text
    except Exception as e:
        print(f"خطأ في تنسيق النص العربي: {e}")
        return str(text)

def create_arabic_styles():
    """إنشاء أنماط النصوص العربية"""
    styles = {}
    
    # نمط العنوان الرئيسي
    styles['title'] = ParagraphStyle(
        'ArabicTitle',
        fontName='ArabicFont',
        fontSize=20,
        alignment=1,  # محاذاة وسط
        textColor=colors.darkblue,
        spaceAfter=20,
        leading=24
    )
    
    # نمط العناوين الفرعية
    styles['heading'] = ParagraphStyle(
        'ArabicHeading',
        fontName='ArabicFont',
        fontSize=16,
        alignment=1,  # محاذاة وسط
        textColor=colors.darkblue,
        spaceAfter=12,
        leading=20
    )
    
    # نمط النص العادي
    styles['normal'] = ParagraphStyle(
        'ArabicNormal',
        fontName='ArabicFont',
        fontSize=12,
        alignment=2,  # محاذاة يمين
        leading=16,
        spaceAfter=6
    )
    
    # نمط النص في الجداول
    styles['table'] = ParagraphStyle(
        'ArabicTable',
        fontName='ArabicFont',
        fontSize=10,
        alignment=1,  # محاذاة وسط
        leading=12
    )
    
    return styles

def generate_workshop_pdf(vehicle, workshop_records):
    """إنشاء تقرير ورشة مثالي بالنصوص العربية"""
    
    try:
        print("بدء إنشاء تقرير PDF مع الخطوط العربية المحملة...")
        
        # تسجيل الخط العربي
        font_registered = register_arabic_font()
        if not font_registered:
            print("فشل في تسجيل الخط العربي، استخدام البديل...")
            return create_english_fallback(vehicle, workshop_records)
        
        # إنشاء buffer للـ PDF
        buffer = io.BytesIO()
        
        # إنشاء المستند
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=30,
            leftMargin=30,
            topMargin=50,
            bottomMargin=30
        )
        
        # الحصول على الأنماط العربية
        arabic_styles = create_arabic_styles()
        
        # قائمة المحتوى
        content = []
        
        # إضافة الشعار
        try:
            logo_path = 'attached_assets/ChatGPT Image Jun 8, 2025, 05_34_10 PM_1749393284624.png'
            if os.path.exists(logo_path):
                logo = Image(logo_path, width=80, height=50)
                logo.hAlign = 'CENTER'
                content.append(logo)
                content.append(Spacer(1, 15))
        except Exception as e:
            print(f"تعذر إضافة الشعار: {e}")
        
        # عنوان التقرير
        title_text = format_arabic_text(f"تقرير سجلات الورشة للمركبة: {vehicle.plate_number}")
        title = Paragraph(title_text, arabic_styles['title'])
        content.append(title)
        
        # معلومات المركبة الفرعية
        vehicle_subtitle = format_arabic_text(f"{vehicle.make} {vehicle.model} - سنة {vehicle.year}")
        subtitle = Paragraph(vehicle_subtitle, arabic_styles['normal'])
        content.append(subtitle)
        content.append(Spacer(1, 25))
        
        # قسم معلومات المركبة
        vehicle_heading = format_arabic_text("معلومات المركبة")
        content.append(Paragraph(vehicle_heading, arabic_styles['heading']))
        content.append(Spacer(1, 10))
        
        # جدول معلومات المركبة
        vehicle_data = []
        vehicle_info = [
            ("رقم اللوحة", str(vehicle.plate_number)),
            ("الصنع والموديل", f"{vehicle.make} {vehicle.model}"),
            ("سنة الصنع", str(vehicle.year)),
            ("اللون", str(vehicle.color)),
            ("الحالة الحالية", get_status_arabic(vehicle.status))
        ]
        
        for label, value in vehicle_info:
            formatted_label = format_arabic_text(label)
            formatted_value = format_arabic_text(value)
            vehicle_data.append([
                Paragraph(formatted_label, arabic_styles['table']),
                Paragraph(formatted_value, arabic_styles['table'])
            ])
        
        vehicle_table = Table(vehicle_data, colWidths=[4*inch, 3*inch])
        vehicle_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('BACKGROUND', (1, 0), (1, -1), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'ArabicFont'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('LINEBELOW', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        
        content.append(vehicle_table)
        content.append(Spacer(1, 25))
        
        # قسم سجلات الورشة
        if workshop_records and len(workshop_records) > 0:
            records_heading = format_arabic_text(f"سجلات الورشة ({len(workshop_records)} سجل)")
            content.append(Paragraph(records_heading, arabic_styles['heading']))
            content.append(Spacer(1, 15))
            
            # رأس جدول السجلات
            headers = [
                format_arabic_text("تاريخ الدخول"),
                format_arabic_text("تاريخ الخروج"),
                format_arabic_text("سبب الدخول"),
                format_arabic_text("حالة الإصلاح"),
                format_arabic_text("التكلفة (ريال)"),
                format_arabic_text("اسم الورشة")
            ]
            
            header_row = []
            for header in headers:
                header_row.append(Paragraph(header, arabic_styles['table']))
            
            workshop_data = [header_row]
            
            # بيانات السجلات
            total_cost = 0
            total_days = 0
            
            for record in workshop_records:
                # تاريخ الدخول
                entry_date = record.entry_date.strftime('%Y-%m-%d') if record.entry_date else "غير محدد"
                
                # تاريخ الخروج
                if record.exit_date:
                    exit_date = record.exit_date.strftime('%Y-%m-%d')
                else:
                    exit_date = "ما زالت في الورشة"
                
                # سبب الدخول
                reason = get_reason_arabic(record.reason)
                
                # حالة الإصلاح
                status = get_repair_status_arabic(record.repair_status)
                
                # التكلفة
                cost = float(record.cost) if record.cost else 0
                total_cost += cost
                
                # اسم الورشة
                workshop_name = record.workshop_name if record.workshop_name else "غير محدد"
                
                # حساب الأيام
                if record.entry_date:
                    if record.exit_date:
                        days = (record.exit_date - record.entry_date).days
                    else:
                        days = (datetime.now().date() - record.entry_date).days
                    total_days += max(0, days)
                
                # إضافة الصف
                row = [
                    Paragraph(str(entry_date), arabic_styles['table']),
                    Paragraph(format_arabic_text(exit_date), arabic_styles['table']),
                    Paragraph(format_arabic_text(reason), arabic_styles['table']),
                    Paragraph(format_arabic_text(status), arabic_styles['table']),
                    Paragraph(f"{cost:,.0f}", arabic_styles['table']),
                    Paragraph(format_arabic_text(workshop_name), arabic_styles['table'])
                ]
                workshop_data.append(row)
            
            # إنشاء جدول السجلات
            col_widths = [1.2*inch, 1.2*inch, 1.3*inch, 1.3*inch, 0.8*inch, 1.2*inch]
            workshop_table = Table(workshop_data, colWidths=col_widths)
            
            # تنسيق جدول السجلات
            workshop_table.setStyle(TableStyle([
                # رأس الجدول
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, -1), 'ArabicFont'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                
                # الحدود والخطوط
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('LINEBELOW', (0, 0), (-1, 0), 2, colors.darkblue),
                
                # تلوين الصفوف بالتناوب
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.beige])
            ]))
            
            content.append(workshop_table)
            content.append(Spacer(1, 25))
            
            # قسم الإحصائيات
            stats_heading = format_arabic_text("ملخص الإحصائيات")
            content.append(Paragraph(stats_heading, arabic_styles['heading']))
            content.append(Spacer(1, 15))
            
            # حساب المتوسطات
            avg_cost = total_cost / len(workshop_records) if len(workshop_records) > 0 else 0
            avg_days = total_days / len(workshop_records) if len(workshop_records) > 0 else 0
            
            stats_data = [
                [
                    Paragraph(format_arabic_text("عدد السجلات"), arabic_styles['table']),
                    Paragraph(str(len(workshop_records)), arabic_styles['table'])
                ],
                [
                    Paragraph(format_arabic_text("إجمالي التكلفة"), arabic_styles['table']),
                    Paragraph(f"{total_cost:,.0f} " + format_arabic_text("ريال"), arabic_styles['table'])
                ],
                [
                    Paragraph(format_arabic_text("إجمالي أيام الإصلاح"), arabic_styles['table']),
                    Paragraph(f"{total_days} " + format_arabic_text("يوم"), arabic_styles['table'])
                ],
                [
                    Paragraph(format_arabic_text("متوسط التكلفة لكل سجل"), arabic_styles['table']),
                    Paragraph(f"{avg_cost:,.0f} " + format_arabic_text("ريال"), arabic_styles['table'])
                ],
                [
                    Paragraph(format_arabic_text("متوسط مدة الإصلاح"), arabic_styles['table']),
                    Paragraph(f"{avg_days:.1f} " + format_arabic_text("يوم"), arabic_styles['table'])
                ]
            ]
            
            stats_table = Table(stats_data, colWidths=[3*inch, 2.5*inch])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
                ('BACKGROUND', (1, 0), (1, -1), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, -1), 'ArabicFont'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ('TOPPADDING', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('LINEBELOW', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            
            content.append(stats_table)
        
        else:
            # لا توجد سجلات
            no_records_text = format_arabic_text("لا توجد سجلات ورشة متاحة لهذه المركبة")
            no_records = Paragraph(no_records_text, arabic_styles['normal'])
            content.append(no_records)
        
        # التذييل
        content.append(Spacer(1, 35))
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
        footer_text = format_arabic_text(f"تم إنشاء هذا التقرير بواسطة نظام نُظم لإدارة المركبات - {current_time}")
        
        footer_style = ParagraphStyle(
            'Footer',
            fontName='ArabicFont',
            fontSize=9,
            alignment=1,  # محاذاة وسط
            textColor=colors.grey
        )
        
        footer = Paragraph(footer_text, footer_style)
        content.append(footer)
        
        # بناء المستند
        doc.build(content)
        buffer.seek(0)
        
        print("تم إنشاء تقرير PDF مثالي بالخطوط العربية!")
        return buffer.getvalue()
        
    except Exception as e:
        print(f"خطأ في إنشاء PDF العربي المثالي: {str(e)}")
        return create_english_fallback(vehicle, workshop_records)

def create_english_fallback(vehicle, workshop_records):
    """إنشاء تقرير بديل بالإنجليزية"""
    try:
        print("إنشاء تقرير بديل بالإنجليزية...")
        from utils.final_arabic_pdf import generate_workshop_pdf as fallback_generate
        return fallback_generate(vehicle, workshop_records)
    except Exception as e:
        print(f"خطأ في التقرير البديل: {e}")
        return b"PDF Generation Error"

def get_status_arabic(status):
    """ترجمة حالة المركبة للعربية"""
    status_map = {
        'available': 'متاح',
        'rented': 'مؤجر',
        'in_workshop': 'في الورشة',
        'accident': 'حادث'
    }
    return status_map.get(status, status)

def get_reason_arabic(reason):
    """ترجمة سبب دخول الورشة للعربية"""
    reason_map = {
        'maintenance': 'صيانة دورية',
        'breakdown': 'عطل',
        'accident': 'حادث'
    }
    return reason_map.get(reason, reason if reason else "غير محدد")

def get_repair_status_arabic(status):
    """ترجمة حالة الإصلاح للعربية"""
    status_map = {
        'in_progress': 'قيد التنفيذ',
        'completed': 'تم الإصلاح',
        'pending_approval': 'بانتظار الموافقة'
    }
    return status_map.get(status, status if status else "غير محدد")