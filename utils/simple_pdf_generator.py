"""
مولد PDF بسيط باستخدام reportlab لتجنب مشاكل الترميز
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from io import BytesIO
from datetime import datetime


def create_vehicle_handover_pdf(handover_data):
    """
    إنشاء PDF بسيط لتسليم/استلام المركبة باستخدام reportlab
    """
    try:
        buffer = BytesIO()
        
        # إنشاء PDF باستخدام reportlab
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # دالة تنظيف النصوص
        def clean_text(text):
            if not text:
                return "N/A"
            # إزالة الأحرف غير الأساسية
            cleaned = ''.join(char for char in str(text) if ord(char) < 128)
            return cleaned.strip() or "N/A"
        
        # العنوان الرئيسي
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredText(width/2, height-50, "Vehicle Handover Document")
        
        # معلومات الوثيقة
        y_position = height - 100
        c.setFont("Helvetica", 12)
        c.drawString(50, y_position, f"Document ID: {handover_data.id}")
        y_position -= 20
        c.drawString(50, y_position, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        # خط فاصل
        y_position -= 30
        c.line(50, y_position, width-50, y_position)
        y_position -= 30
        
        # معلومات المركبة
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y_position, "VEHICLE INFORMATION")
        y_position -= 25
        
        if hasattr(handover_data, 'vehicle_rel') and handover_data.vehicle_rel:
            vehicle = handover_data.vehicle_rel
            c.setFont("Helvetica", 11)
            
            c.drawString(50, y_position, f"Plate Number: {clean_text(vehicle.plate_number)}")
            y_position -= 18
            c.drawString(50, y_position, f"Make: {clean_text(vehicle.make)}")
            y_position -= 18
            c.drawString(50, y_position, f"Model: {clean_text(vehicle.model)}")
            y_position -= 18
            
            if hasattr(vehicle, 'year') and vehicle.year:
                c.drawString(50, y_position, f"Year: {vehicle.year}")
                y_position -= 18
                
            if hasattr(vehicle, 'color') and vehicle.color:
                c.drawString(50, y_position, f"Color: {clean_text(vehicle.color)}")
                y_position -= 18
        else:
            c.setFont("Helvetica", 11)
            c.drawString(50, y_position, "Vehicle information not available")
            y_position -= 18
        
        # تفاصيل التسليم
        y_position -= 20
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y_position, "HANDOVER DETAILS")
        y_position -= 25
        
        c.setFont("Helvetica", 11)
        
        if handover_data.handover_date:
            c.drawString(50, y_position, f"Date: {handover_data.handover_date.strftime('%Y-%m-%d')}")
            y_position -= 18
            c.drawString(50, y_position, f"Time: {handover_data.handover_date.strftime('%H:%M')}")
            y_position -= 18
        
        handover_type = "DELIVERY" if str(handover_data.handover_type) == "delivery" else "RETURN"
        c.drawString(50, y_position, f"Type: {handover_type}")
        y_position -= 18
        
        person_name = clean_text(handover_data.person_name) if handover_data.person_name else "Person Name"
        c.drawString(50, y_position, f"Person: {person_name}")
        y_position -= 18
        
        if hasattr(handover_data, 'person_mobile') and handover_data.person_mobile:
            c.drawString(50, y_position, f"Mobile: {handover_data.person_mobile}")
            y_position -= 18
        
        # حالة المركبة
        y_position -= 20
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, y_position, "VEHICLE CONDITION")
        y_position -= 25
        
        c.setFont("Helvetica", 11)
        mileage = str(handover_data.mileage) if handover_data.mileage else "0"
        c.drawString(50, y_position, f"Mileage: {mileage} km")
        y_position -= 18
        
        fuel_level = clean_text(handover_data.fuel_level) if handover_data.fuel_level else "Unknown"
        c.drawString(50, y_position, f"Fuel Level: {fuel_level}")
        y_position -= 18
        
        # المعدات
        y_position -= 20
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_position, "EQUIPMENT STATUS:")
        y_position -= 20
        
        c.setFont("Helvetica", 10)
        equipment_items = [
            ('Spare Tire', getattr(handover_data, 'has_spare_tire', False)),
            ('Fire Extinguisher', getattr(handover_data, 'has_fire_extinguisher', False)),
            ('First Aid Kit', getattr(handover_data, 'has_first_aid_kit', False)),
            ('Warning Triangle', getattr(handover_data, 'has_warning_triangle', False)),
            ('Tools', getattr(handover_data, 'has_tools', False))
        ]
        
        for item_name, has_item in equipment_items:
            status = 'Available' if has_item else 'Not Available'
            c.drawString(50, y_position, f"- {item_name}: {status}")
            y_position -= 15
        
        # رابط النموذج الإلكتروني
        y_position -= 20
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y_position, "ELECTRONIC FORM ACCESS")
        y_position -= 20
        
        c.setFont("Helvetica", 10)
        if hasattr(handover_data, 'form_link') and handover_data.form_link:
            c.drawString(50, y_position, f"Form Link: {handover_data.form_link}")
        else:
            c.drawString(50, y_position, f"Form ID: {handover_data.id}")
        y_position -= 20
        
        # الملاحظات
        if handover_data.notes:
            y_position -= 10
            c.setFont("Helvetica-Bold", 10)
            c.drawString(50, y_position, "NOTES:")
            y_position -= 15
            c.setFont("Helvetica", 9)
            notes_clean = clean_text(handover_data.notes)
            if notes_clean and notes_clean != "N/A":
                c.drawString(50, y_position, notes_clean[:100])  # أول 100 حرف فقط
            else:
                c.drawString(50, y_position, "Notes in Arabic language")
            y_position -= 20
        
        # التوقيعات
        y_position -= 20
        c.setFont("Helvetica-Bold", 10)
        c.drawString(50, y_position, "SIGNATURES:")
        y_position -= 30
        
        c.setFont("Helvetica", 9)
        c.drawString(50, y_position, "Delivered by: ____________________")
        c.drawString(300, y_position, "Received by: ____________________")
        y_position -= 20
        c.drawString(50, y_position, "Date: ____________________")
        c.drawString(300, y_position, "Date: ____________________")
        
        # تذييل
        y_position -= 40
        c.line(50, y_position, width-50, y_position)
        y_position -= 15
        c.setFont("Helvetica-Oblique", 8)
        c.drawCentredText(width/2, y_position, "Generated by Vehicle Management System")
        c.drawCentredText(width/2, y_position-12, "For verification, access the electronic form using the ID above")
        
        # حفظ PDF
        c.save()
        buffer.seek(0)
        return buffer
        
    except Exception as e:
        print(f"Error creating PDF with reportlab: {e}")
        
        # نظام احتياطي بسيط جداً
        try:
            buffer = BytesIO()
            c = canvas.Canvas(buffer, pagesize=A4)
            width, height = A4
            
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredText(width/2, height-50, "Vehicle Handover Document")
            c.setFont("Helvetica", 12)
            c.drawString(50, height-100, f"Document ID: {handover_data.id}")
            c.drawString(50, height-120, f"Date: {datetime.now().strftime('%Y-%m-%d')}")
            c.drawString(50, height-140, "Full document could not be generated")
            c.drawString(50, height-160, "Please contact system administrator")
            
            c.save()
            buffer.seek(0)
            return buffer
            
        except Exception as backup_error:
            print(f"Backup PDF creation failed: {backup_error}")
            return None