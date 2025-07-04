"""
وحدة بسيطة لإنشاء ملفات PDF لتقارير الورشة باللغة العربية
"""
import io
import os
from datetime import datetime


from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image

# استيراد المكتبات اللازمة للغة العربية
import arabic_reshaper
from bidi.algorithm import get_display

def arabic_text(text):
    """تحويل النص العربي ليعرض بشكل صحيح في PDF"""
    if text is None:
        return ""
    text = str(text)
    try:
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)
        return bidi_text
    except Exception as e:
        import logging
        logging.error(f"خطأ في معالجة النص العربي: {str(e)}")
        return text

def generate_workshop_pdf(vehicle, workshop_records):
    """
    إنشاء تقرير ورشة بصيغة PDF
    
    Args:
        vehicle: كائن المركبة
        workshop_records: سجلات الورشة
        
    Returns:
        BytesIO: كائن ذاكرة يحتوي على ملف PDF
    """
    import logging
    import os
    from datetime import datetime
    
    logging.info(f"بدء إنشاء تقرير PDF للمركبة {vehicle.plate_number}")
    
    # تجهيز المخرجات
    buffer = io.BytesIO()
    
    try:
        # إنشاء PDF بدون خطوط خارجية لتجنب مشاكل النشر
        logging.info("إنشاء PDF باستخدام الخطوط الافتراضية")
        
        # إنشاء المستند
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4,
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=30,
            title=arabic_text("تقرير سجلات الورشة")
        )
        
        # تحضير أنماط النصوص بدون خطوط خارجية
        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(
            name='Arabic',
            fontName='Helvetica',
            fontSize=12,
            alignment=1,  # وسط
            leading=16
        ))
        
        styles.add(ParagraphStyle(
            name='ArabicTitle',
            fontName='Helvetica-Bold',
            fontSize=16,
            alignment=1,  # وسط
            leading=22,
            spaceAfter=10
        ))
        
        styles.add(ParagraphStyle(
            name='ArabicHeading',
            fontName='Helvetica-Bold',
            fontSize=14,
            alignment=1,  # وسط
            leading=20,
            spaceAfter=8
        ))
        
        # تجهيز المحتوى
        content = []
        
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
            
            # حساب الإحصائيات
            total_cost = 0
            total_days = 0
            
            # ترجمة القيم المختصرة إلى نصوص مفهومة
            reason_map = {'maintenance': 'صيانة دورية', 'breakdown': 'عطل', 'accident': 'حادث'}
            status_map = {'in_progress': 'قيد التنفيذ', 'completed': 'تم الإصلاح', 'pending_approval': 'بانتظار الموافقة'}
            
            for record in workshop_records:
                # حساب عدد أيام الإصلاح
                days = 0
                if record.entry_date:
                    if record.exit_date:
                        days = (record.exit_date - record.entry_date).days
                    else:
                        days = (datetime.now().date() - record.entry_date).days
                    total_days += max(0, days)
                
                # إجمالي التكلفة
                if record.cost:
                    total_cost += record.cost
                
                # تجهيز بيانات الصف
                workshop_data.append([
                    arabic_text(reason_map.get(record.reason, record.reason) if record.reason else "غير محدد"),
                    arabic_text(record.entry_date.strftime("%Y-%m-%d") if record.entry_date else ""),
                    arabic_text(record.exit_date.strftime("%Y-%m-%d") if record.exit_date else "ما زالت في الورشة"),
                    arabic_text(status_map.get(record.repair_status, record.repair_status) if record.repair_status else ""),
                    arabic_text(f"{record.cost:,.2f}" if record.cost else "0.00"),
                    arabic_text(record.workshop_name or "غير محدد"),
                    arabic_text(record.technician_name or "غير محدد")
                ])
            
            # إنشاء جدول سجلات الورشة
            col_widths = [65, 55, 55, 65, 55, 60, 60]
            table = Table(workshop_data, colWidths=col_widths)
            
            # تنسيق الجدول
            table_style = TableStyle([
                # تنسيق الرأس
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('TOPPADDING', (0, 0), (-1, 0), 6),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                
                # تنسيق الخلايا
                ('FONT', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                
                # الحدود
                ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
                ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.gray),
                
                # تلوين الصفوف بالتناوب
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.white])
            ])
            
            # دمج تنسيق الجدول
            table.setStyle(table_style)
            content.append(table)
            
            # إضافة ملخص الإحصائيات
            content.append(Spacer(1, 20))
            content.append(Paragraph(arabic_text("ملخص الإحصائيات"), styles['ArabicHeading']))
            content.append(Spacer(1, 10))
            
            stats_data = [
                [arabic_text("عدد السجلات"), arabic_text(str(len(workshop_records)))],
                [arabic_text("إجمالي التكلفة"), arabic_text(f"{total_cost:,.2f} ريال")],
                [arabic_text("إجمالي أيام الإصلاح"), arabic_text(f"{total_days} يوم")]
            ]
            
            # Avoid division by zero
            if len(workshop_records) > 0:
                stats_data.append([
                    arabic_text("متوسط التكلفة لكل سجل"), 
                    arabic_text(f"{total_cost/len(workshop_records):,.2f} ريال")
                ])
                stats_data.append([
                    arabic_text("متوسط مدة الإصلاح"), 
                    arabic_text(f"{total_days/len(workshop_records):.1f} يوم")
                ])
            
            stats_table = Table(stats_data, colWidths=[100, 150])
            stats_table.setStyle(TableStyle([
                ('FONT', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONT', (1, 0), (1, -1), 'Helvetica'),
                ('ALIGN', (0, 0), (0, -1), 'LEFT'),
                ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('BOX', (0, 0), (1, -1), 0.5, colors.black),
                ('INNERGRID', (0, 0), (1, -1), 0.25, colors.grey),
            ]))
            content.append(stats_table)
        else:
            # عرض رسالة في حالة عدم وجود سجلات
            no_records = Paragraph(arabic_text("لا توجد سجلات ورشة متاحة لهذه المركبة"), styles['Arabic'])
            content.append(no_records)
        
        # بيانات التذييل
        content.append(Spacer(1, 30))
        footer = Paragraph(
            arabic_text(f"تم إنشاء هذا التقرير بواسطة نظام نُظم لإدارة المركبات - {datetime.now().strftime('%Y-%m-%d %H:%M')}"),
            styles['Arabic']
        )
        content.append(footer)
        
        # إنشاء المستند
        doc.build(content)
        buffer.seek(0)
        logging.info("تم إنشاء ملف PDF بنجاح")
        
    except Exception as e:
        logging.error(f"حدث خطأ أثناء إنشاء ملف PDF: {str(e)}")
    
    return buffer