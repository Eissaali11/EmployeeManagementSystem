"""
مولد PDF باللغة العربية لتقارير سجلات الورشة
يستخدم arabic-reshaper و python-bidi لعرض صحيح للنصوص العربية
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.pdfgen import canvas
import io
import os
from datetime import datetime

# مكتبات دعم العربية
import arabic_reshaper
from bidi.algorithm import get_display

def format_arabic_text(text):
    """تنسيق النص العربي للعرض الصحيح في PDF"""
    if not text:
        return ""
    
    text_str = str(text)
    
    try:
        # إعادة تشكيل النص العربي
        reshaped_text = arabic_reshaper.reshape(text_str)
        # تطبيق خوارزمية الاتجاه الثنائي
        bidi_text = get_display(reshaped_text)
        return bidi_text
    except Exception as e:
        print(f"خطأ في معالجة النص العربي: {e}")
        return text_str

def generate_workshop_pdf(vehicle, workshop_records):
    """
    إنشاء تقرير ورشة باللغة العربية
    """
    try:
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
        
        # قائمة المحتوى
        content = []
        
        # الأنماط
        styles = getSampleStyleSheet()
        
        # نمط العنوان العربي
        arabic_title_style = ParagraphStyle(
            'ArabicTitle',
            parent=styles['Title'],
            fontSize=18,
            spaceAfter=20,
            alignment=1,  # وسط
            fontName='Helvetica-Bold'
        )
        
        # نمط النص العربي
        arabic_style = ParagraphStyle(
            'Arabic',
            parent=styles['Normal'],
            fontSize=12,
            alignment=2,  # يمين
            fontName='Helvetica'
        )
        
        # نمط العناوين الفرعية
        arabic_heading_style = ParagraphStyle(
            'ArabicHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=10,
            alignment=1,  # وسط
            fontName='Helvetica-Bold'
        )
        
        # شعار وعنوان التقرير
        try:
            # إضافة الشعار إذا كان متوفراً
            logo_path = 'attached_assets/ChatGPT Image Jun 8, 2025, 05_34_10 PM_1749393284624.png'
            if os.path.exists(logo_path):
                logo = Image(logo_path, width=60, height=60)
                logo.hAlign = 'CENTER'
                content.append(logo)
                content.append(Spacer(1, 10))
        except:
            pass
        
        # عنوان التقرير
        title_text = format_arabic_text(f"تقرير سجلات الورشة للمركبة: {vehicle.plate_number}")
        title = Paragraph(title_text, arabic_title_style)
        content.append(title)
        content.append(Spacer(1, 20))
        
        # معلومات المركبة
        vehicle_info_title = Paragraph(format_arabic_text("معلومات المركبة"), arabic_heading_style)
        content.append(vehicle_info_title)
        
        vehicle_data = [
            [format_arabic_text("رقم اللوحة"), format_arabic_text(str(vehicle.plate_number))],
            [format_arabic_text("الصنع والموديل"), format_arabic_text(f"{vehicle.make} {vehicle.model}")],
            [format_arabic_text("سنة الصنع"), format_arabic_text(str(vehicle.year))],
            [format_arabic_text("اللون"), format_arabic_text(str(vehicle.color))],
            [format_arabic_text("الحالة الحالية"), format_arabic_text(str(vehicle.status))]
        ]
        
        vehicle_table = Table(vehicle_data, colWidths=[150, 200])
        vehicle_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        content.append(vehicle_table)
        content.append(Spacer(1, 20))
        
        # سجلات الورشة
        if workshop_records:
            records_title = Paragraph(
                format_arabic_text(f"سجلات الورشة ({len(workshop_records)} سجل)"), 
                arabic_heading_style
            )
            content.append(records_title)
            content.append(Spacer(1, 10))
            
            # رأس جدول السجلات
            headers = [
                format_arabic_text("تاريخ الدخول"),
                format_arabic_text("تاريخ الخروج"),
                format_arabic_text("سبب الدخول"),
                format_arabic_text("حالة الإصلاح"),
                format_arabic_text("التكلفة (ريال)"),
                format_arabic_text("اسم الورشة"),
                format_arabic_text("الفني المسؤول")
            ]
            
            workshop_data = [headers]
            
            # إضافة البيانات
            total_cost = 0
            total_days = 0
            
            for record in workshop_records:
                entry_date = record.entry_date.strftime('%Y-%m-%d') if record.entry_date else format_arabic_text("غير محدد")
                exit_date = record.exit_date.strftime('%Y-%m-%d') if record.exit_date else format_arabic_text("ما زالت في الورشة")
                
                # ترجمة سبب الدخول
                reason_map = {
                    'maintenance': 'صيانة دورية',
                    'breakdown': 'عطل',
                    'accident': 'حادث'
                }
                reason = format_arabic_text(reason_map.get(record.reason, record.reason if record.reason else "غير محدد"))
                
                # ترجمة حالة الإصلاح
                status_map = {
                    'in_progress': 'قيد التنفيذ',
                    'completed': 'تم الإصلاح',
                    'pending_approval': 'بانتظار الموافقة'
                }
                status = format_arabic_text(status_map.get(record.repair_status, record.repair_status if record.repair_status else "غير محدد"))
                
                cost = float(record.cost) if record.cost else 0
                total_cost += cost
                
                # حساب الأيام
                if record.entry_date:
                    if record.exit_date:
                        days = (record.exit_date - record.entry_date).days
                    else:
                        days = (datetime.now().date() - record.entry_date).days
                    total_days += max(0, days)
                
                workshop_name = format_arabic_text(record.workshop_name if record.workshop_name else "غير محدد")
                technician = format_arabic_text(record.technician_name if record.technician_name else "غير محدد")
                
                row = [
                    entry_date,
                    exit_date,
                    reason,
                    status,
                    f"{cost:,.2f}",
                    workshop_name,
                    technician
                ]
                workshop_data.append(row)
            
            # إنشاء جدول السجلات
            col_widths = [70, 70, 80, 80, 60, 80, 80]
            workshop_table = Table(workshop_data, colWidths=col_widths)
            
            # تنسيق الجدول
            workshop_table.setStyle(TableStyle([
                # رأس الجدول
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                
                # الحدود
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                
                # تلوين الصفوف بالتناوب
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
            ]))
            
            content.append(workshop_table)
            content.append(Spacer(1, 20))
            
            # الإحصائيات
            stats_title = Paragraph(format_arabic_text("ملخص الإحصائيات"), arabic_heading_style)
            content.append(stats_title)
            
            stats_data = [
                [format_arabic_text("عدد السجلات"), str(len(workshop_records))],
                [format_arabic_text("إجمالي التكلفة"), f"{total_cost:,.2f} ريال"],
                [format_arabic_text("إجمالي أيام الإصلاح"), f"{total_days} يوم"]
            ]
            
            if len(workshop_records) > 0:
                avg_cost = total_cost / len(workshop_records)
                avg_days = total_days / len(workshop_records)
                stats_data.extend([
                    [format_arabic_text("متوسط التكلفة لكل سجل"), f"{avg_cost:,.2f} ريال"],
                    [format_arabic_text("متوسط مدة الإصلاح"), f"{avg_days:.1f} يوم"]
                ])
            
            stats_table = Table(stats_data, colWidths=[200, 150])
            stats_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            content.append(stats_table)
        
        else:
            # لا توجد سجلات
            no_records = Paragraph(
                format_arabic_text("لا توجد سجلات ورشة متاحة لهذه المركبة"),
                arabic_style
            )
            content.append(no_records)
        
        # التذييل
        content.append(Spacer(1, 30))
        footer_text = format_arabic_text(
            f"تم إنشاء هذا التقرير بواسطة نظام نُظم لإدارة المركبات - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        footer = Paragraph(footer_text, arabic_style)
        content.append(footer)
        
        # بناء المستند
        doc.build(content)
        buffer.seek(0)
        
        return buffer.getvalue()
        
    except Exception as e:
        print(f"خطأ في إنشاء PDF العربي: {str(e)}")
        # العودة إلى المولد الآمن في حالة الفشل
        from utils.safe_workshop_pdf import generate_workshop_pdf as safe_generate
        return safe_generate(vehicle, workshop_records)