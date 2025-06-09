"""
مولد PDF عربي محسن لتسليم المركبات مع معالجة متقدمة للنصوص
"""

import os
from io import BytesIO
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def safe_arabic_text(text):
    """
    تحويل النص العربي إلى نص آمن للعرض في PDF
    """
    if not text:
        return "Not Available"
    
    # قاموس تحويل النصوص العربية الشائعة
    arabic_translations = {
        'وثيقة تسليم واستلام المركبة': 'Vehicle Handover Document',
        'رقم الوثيقة': 'Document ID',
        'تاريخ الإنشاء': 'Creation Date',
        'نوع العملية': 'Operation Type',
        'تسليم': 'Delivery',
        'استلام': 'Return',
        'معلومات المركبة': 'Vehicle Information',
        'رقم اللوحة': 'Plate Number',
        'الصنع': 'Make',
        'الموديل': 'Model',
        'السنة': 'Year',
        'اللون': 'Color',
        'تفاصيل التسليم': 'Handover Details',
        'التاريخ': 'Date',
        'الوقت': 'Time',
        'اسم الشخص': 'Person Name',
        'رقم الهاتف': 'Phone Number',
        'قراءة العداد': 'Odometer Reading',
        'مستوى الوقود': 'Fuel Level',
        'معدات المركبة': 'Vehicle Equipment',
        'الإطار الاحتياطي': 'Spare Tire',
        'طفاية الحريق': 'Fire Extinguisher',
        'حقيبة الإسعافات الأولية': 'First Aid Kit',
        'مثلث التحذير': 'Warning Triangle',
        'عدة الأدوات': 'Tool Kit',
        'ملاحظات إضافية': 'Additional Notes',
        'توقيع المسلم': 'Deliverer Signature',
        'توقيع المستلم': 'Receiver Signature',
        'غير محدد': 'Not Specified',
        'غير متوفرة': 'Not Available'
    }
    
    # البحث عن ترجمة مباشرة
    if str(text) in arabic_translations:
        return arabic_translations[str(text)]
    
    # فحص وجود أحرف عربية
    has_arabic = any('\u0600' <= char <= '\u06FF' for char in str(text))
    
    if has_arabic:
        # ترجمة الأسماء العربية الشائعة
        name_translations = {
            'محمد': 'Mohammed',
            'أحمد': 'Ahmed',
            'علي': 'Ali',
            'عبدالله': 'Abdullah',
            'فاطمة': 'Fatima',
            'عائشة': 'Aisha',
            'خديجة': 'Khadija',
            'سارة': 'Sarah',
            'مريم': 'Mariam',
            'نورا': 'Nora'
        }
        
        if str(text) in name_translations:
            return name_translations[str(text)]
        
        # إزالة الأحرف العربية كحل أخير
        cleaned = ''.join(char for char in str(text) if ord(char) < 128)
        return cleaned.strip() or "Arabic Text"
    
    return str(text)

def create_vehicle_handover_pdf(handover_data):
    """
    إنشاء PDF محسن لتسليم المركبة بنصوص آمنة
    """
    try:
        print("Starting enhanced Arabic handover PDF generation...")
        
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # الألوان الاحترافية
        primary_color = colors.HexColor('#2E86AB')
        secondary_color = colors.HexColor('#A23B72')
        accent_color = colors.HexColor('#F18F01')
        
        # شعار الشركة
        try:
            logo_path = os.path.join(os.path.dirname(__file__), '..', 'attached_assets', 'logo.png')
            if os.path.exists(logo_path):
                c.drawImage(logo_path, 50, height - 80, width=60, height=40, preserveAspectRatio=True)
        except:
            pass
        
        # العنوان الرئيسي
        c.setFont("Helvetica-Bold", 18)
        c.setFillColor(primary_color)
        title = safe_arabic_text("وثيقة تسليم واستلام المركبة")
        title_width = c.stringWidth(title, "Helvetica-Bold", 18)
        c.drawString((width - title_width)/2, height - 60, title)
        
        # صندوق معلومات الوثيقة الموسع
        c.setStrokeColor(primary_color)
        c.setLineWidth(2)
        c.rect(width - 220, height - 150, 170, 110)
        
        # معلومات الوثيقة
        y_position = height - 50
        c.setFont("Helvetica", 10)
        c.setFillColor(colors.black)
        
        # رابط الفورم الإلكتروني
        form_url = f"nuzum-system.replit.app/vehicles/handover/{getattr(handover_data, 'id', 'new')}"
        
        doc_info = [
            f"Document ID: {getattr(handover_data, 'id', 85)}",
            f"Creation Date: {datetime.now().strftime('%Y-%m-%d')}",
            f"Time: {datetime.now().strftime('%H:%M')}",
            f"Operation Type: Return",
            f"Form Link: {form_url}",
            "QR Code: Scan for online access"
        ]
        
        for i, info in enumerate(doc_info):
            c.drawString(width - 215, height - 60 - (i * 12), info)
        
        # خط فاصل
        y_position = height - 170
        c.setStrokeColor(primary_color)
        c.setLineWidth(2)
        c.line(50, y_position, width - 50, y_position)
        
        # معلومات المركبة
        y_position -= 40
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(secondary_color)
        vehicle_title = safe_arabic_text("معلومات المركبة")
        c.drawString(50, y_position, vehicle_title)
        
        # جدول معلومات المركبة المفصل
        vehicle_data = []
        if hasattr(handover_data, 'vehicle_rel') and handover_data.vehicle_rel:
            vehicle = handover_data.vehicle_rel
            vehicle_data = [
                [safe_arabic_text("رقم اللوحة"), safe_arabic_text(str(vehicle.plate_number) if vehicle.plate_number else "Not Specified")],
                [safe_arabic_text("الصنع"), safe_arabic_text(str(vehicle.make) if vehicle.make else "Not Specified")],
                [safe_arabic_text("الموديل"), safe_arabic_text(str(vehicle.model) if vehicle.model else "Not Specified")],
                [safe_arabic_text("السنة"), safe_arabic_text(str(vehicle.year) if hasattr(vehicle, 'year') and vehicle.year else "Not Specified")],
                [safe_arabic_text("اللون"), safe_arabic_text(str(vehicle.color) if hasattr(vehicle, 'color') and vehicle.color else "Not Specified")],
                ["VIN Number", safe_arabic_text(str(vehicle.vin_number) if hasattr(vehicle, 'vin_number') and vehicle.vin_number else "Not Available")],
                ["Engine Number", safe_arabic_text(str(vehicle.engine_number) if hasattr(vehicle, 'engine_number') and vehicle.engine_number else "Not Available")],
                ["Vehicle Status", safe_arabic_text(str(vehicle.status) if hasattr(vehicle, 'status') and vehicle.status else "Active")]
            ]
        else:
            vehicle_data = [[safe_arabic_text("معلومات المركبة"), safe_arabic_text("غير متوفرة")]]
        
        # إنشاء جدول المركبة مع تحسين التخطيط
        vehicle_table = Table(vehicle_data, colWidths=[2.2*inch, 2.8*inch])
        vehicle_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('BACKGROUND', (1, 0), (1, -1), colors.beige),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        table_width, table_height = vehicle_table.wrap(width, height)
        y_position -= 30
        vehicle_table.drawOn(c, 50, y_position - table_height)
        y_position -= table_height + 30
        
        # تفاصيل التسليم
        y_position -= 40
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(secondary_color)
        handover_title = safe_arabic_text("تفاصيل التسليم")
        c.drawString(50, y_position, handover_title)
        
        # جدول تفاصيل التسليم المفصل
        handover_details = [
            [safe_arabic_text("التاريخ"), safe_arabic_text(handover_data.handover_date.strftime('%Y-%m-%d') if handover_data.handover_date else "Not Specified")],
            [safe_arabic_text("الوقت"), safe_arabic_text(handover_data.handover_date.strftime('%H:%M') if handover_data.handover_date else "Not Specified")],
            [safe_arabic_text("اسم الشخص"), safe_arabic_text(str(handover_data.person_name) if handover_data.person_name else "Not Specified")],
            ["Employee ID", safe_arabic_text(str(handover_data.employee_id) if handover_data.employee_id else "Not Assigned")],
            ["Supervisor", safe_arabic_text(str(handover_data.supervisor_name) if handover_data.supervisor_name else "Not Specified")],
            [safe_arabic_text("قراءة العداد"), safe_arabic_text(f"{handover_data.mileage} km" if handover_data.mileage else "Not Specified")],
            [safe_arabic_text("مستوى الوقود"), safe_arabic_text(f"{handover_data.fuel_level}%" if handover_data.fuel_level else "Not Specified")],
            ["Vehicle Condition", safe_arabic_text(str(handover_data.vehicle_condition) if handover_data.vehicle_condition else "Good")]
        ]
        
        handover_table = Table(handover_details, colWidths=[2.2*inch, 2.8*inch])
        handover_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
            ('BACKGROUND', (1, 0), (1, -1), colors.lightcyan),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        table_width, table_height = handover_table.wrap(width, height)
        y_position -= 30
        handover_table.drawOn(c, 50, y_position - table_height)
        y_position -= table_height + 30
        
        # قائمة تحقق المعدات
        y_position -= 50
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(secondary_color)
        equipment_title = safe_arabic_text("معدات المركبة")
        c.drawString(50, y_position, equipment_title)
        
        # المعدات مع حالة الموجودة/غير موجودة
        equipment_items = [
            (safe_arabic_text("الإطار الاحتياطي"), getattr(handover_data, 'has_spare_tire', True)),
            (safe_arabic_text("طفاية الحريق"), getattr(handover_data, 'has_fire_extinguisher', True)),
            (safe_arabic_text("حقيبة الإسعافات الأولية"), getattr(handover_data, 'has_first_aid_kit', True)),
            (safe_arabic_text("مثلث التحذير"), getattr(handover_data, 'has_warning_triangle', True)),
            (safe_arabic_text("عدة الأدوات"), getattr(handover_data, 'has_tools', True))
        ]
        
        y_position -= 30
        c.setFont("Helvetica", 10)
        
        for item, available in equipment_items:
            # رمز الحالة
            status_color = colors.green if available else colors.red
            status_text = "✓" if available else "✗"
            c.setFillColor(status_color)
            c.drawString(50, y_position, status_text)
            
            # نص المعدات
            c.setFillColor(colors.black)
            c.drawString(70, y_position, item)
            y_position -= 20
        
        # قسم الملاحظات
        y_position -= 30
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(secondary_color)
        notes_title = safe_arabic_text("ملاحظات إضافية")
        c.drawString(50, y_position, notes_title)
        
        # مربع الملاحظات
        y_position -= 30
        c.setStrokeColor(colors.grey)
        c.setLineWidth(1)
        c.rect(50, y_position - 80, width - 100, 70)
        
        # نص الملاحظات
        if handover_data.notes:
            c.setFont("Helvetica", 10)
            c.setFillColor(colors.black)
            notes_text = safe_arabic_text(str(handover_data.notes))
            c.drawString(60, y_position - 20, notes_text)
        
        # قسم التوقيعات
        y_position -= 100
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(colors.black)
        
        # جدول التوقيعات
        signature_data = [
            [safe_arabic_text("توقيع المسلم"), safe_arabic_text("توقيع المستلم")],
            ["", ""],
            [safe_arabic_text("التاريخ") + ": ___________", safe_arabic_text("التاريخ") + ": ___________"]
        ]
        
        signature_table = Table(signature_data, colWidths=[2.4*inch, 2.4*inch], rowHeights=[25, 50, 25])
        signature_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        table_width, table_height = signature_table.wrap(width, height)
        y_position -= 30
        signature_table.drawOn(c, 50, y_position - table_height)
        
        # تذييل الصفحة
        c.setFont("Helvetica", 8)
        c.setFillColor(colors.grey)
        footer_text = f"Generated by Nuzum Vehicle Management System - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        footer_width = c.stringWidth(footer_text, "Helvetica", 8)
        c.drawString((width - footer_width)/2, 30, footer_text)
        
        # إطار الصفحة
        c.setStrokeColor(primary_color)
        c.setLineWidth(2)
        c.rect(30, 20, width - 60, height - 40)
        
        c.save()
        buffer.seek(0)
        
        print("Enhanced Arabic handover PDF generated successfully!")
        return buffer
        
    except Exception as e:
        print(f"Error generating enhanced Arabic handover PDF: {str(e)}")
        # في حالة الفشل، استخدم النسخة الإنجليزية
        from utils.professional_handover_pdf import create_vehicle_handover_pdf as create_english_pdf
        return create_english_pdf(handover_data)