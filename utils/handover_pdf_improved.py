"""
تحسين إنشاء PDF لنماذج تسليم/استلام المركبات مع دعم كامل للنصوص العربية
"""

from fpdf import FPDF
from io import BytesIO
from datetime import datetime
import re


class HandoverPDF(FPDF):
    """فئة محسنة لإنشاء PDF نماذج التسليم/الاستلام"""
    
    def __init__(self):
        super().__init__('P', 'mm', 'A4')
        self.set_auto_page_break(auto=True, margin=15)
        
    def safe_text(self, text, fallback="N/A"):
        """تحويل النص بأمان وإزالة الأحرف غير المدعومة"""
        if not text:
            return fallback
        
        text = str(text)
        # إزالة الأحرف العربية والخاصة
        text = re.sub(r'[^\x00-\x7F]+', '', text)
        return text.strip() or fallback
    
    def header(self):
        """رأس الصفحة"""
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Vehicle Handover Document', 0, 1, 'C')
        self.ln(5)
        
    def footer(self):
        """تذييل الصفحة"""
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')


def create_handover_pdf_improved(handover_data):
    """
    إنشاء PDF محسن لنموذج تسليم/استلام المركبة
    """
    try:
        pdf = HandoverPDF()
        pdf.add_page()
        
        # معلومات الوثيقة
        pdf.set_font('Arial', '', 10)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        pdf.cell(0, 8, f'Document ID: {handover_data.id}', 0, 0, 'L')
        pdf.cell(0, 8, f'Generated: {current_time}', 0, 1, 'R')
        pdf.ln(5)
        
        # خط فاصل
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(10)
        
        # معلومات المركبة
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'VEHICLE INFORMATION', 0, 1, 'L')
        
        if hasattr(handover_data, 'vehicle_rel') and handover_data.vehicle_rel:
            vehicle = handover_data.vehicle_rel
            
            pdf.set_font('Arial', '', 11)
            pdf.cell(50, 8, 'Plate Number:', 0, 0, 'L')
            pdf.set_font('Arial', 'B', 11)
            pdf.cell(0, 8, pdf.safe_text(vehicle.plate_number), 0, 1, 'L')
            
            pdf.set_font('Arial', '', 11)
            pdf.cell(50, 8, 'Make & Model:', 0, 0, 'L')
            pdf.set_font('Arial', 'B', 11)
            make = pdf.safe_text(vehicle.make)
            model = pdf.safe_text(vehicle.model)
            pdf.cell(0, 8, f'{make} {model}', 0, 1, 'L')
            
            if hasattr(vehicle, 'year') and vehicle.year:
                pdf.set_font('Arial', '', 11)
                pdf.cell(50, 8, 'Year:', 0, 0, 'L')
                pdf.set_font('Arial', 'B', 11)
                pdf.cell(0, 8, str(vehicle.year), 0, 1, 'L')
                
            if hasattr(vehicle, 'color') and vehicle.color:
                pdf.set_font('Arial', '', 11)
                pdf.cell(50, 8, 'Color:', 0, 0, 'L')
                pdf.set_font('Arial', 'B', 11)
                pdf.cell(0, 8, pdf.safe_text(vehicle.color), 0, 1, 'L')
        
        pdf.ln(5)
        
        # تفاصيل التسليم/الاستلام
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'HANDOVER DETAILS', 0, 1, 'L')
        
        pdf.set_font('Arial', '', 11)
        
        # التاريخ والوقت
        if handover_data.handover_date:
            date_str = handover_data.handover_date.strftime("%Y-%m-%d")
            time_str = handover_data.handover_date.strftime("%H:%M")
        else:
            date_str = "N/A"
            time_str = "N/A"
            
        pdf.cell(50, 8, 'Date:', 0, 0, 'L')
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 8, date_str, 0, 1, 'L')
        
        pdf.set_font('Arial', '', 11)
        pdf.cell(50, 8, 'Time:', 0, 0, 'L')
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 8, time_str, 0, 1, 'L')
        
        # نوع العملية
        handover_type = "DELIVERY" if str(handover_data.handover_type) == "delivery" else "RETURN"
        pdf.set_font('Arial', '', 11)
        pdf.cell(50, 8, 'Type:', 0, 0, 'L')
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 8, handover_type, 0, 1, 'L')
        
        # اسم الشخص
        person_name = pdf.safe_text(handover_data.person_name, "Person Name")
        pdf.set_font('Arial', '', 11)
        pdf.cell(50, 8, 'Person Name:', 0, 0, 'L')
        pdf.set_font('Arial', 'B', 11)
        pdf.cell(0, 8, person_name, 0, 1, 'L')
        
        # رقم الجوال
        if hasattr(handover_data, 'person_mobile') and handover_data.person_mobile:
            pdf.set_font('Arial', '', 11)
            pdf.cell(50, 8, 'Mobile Number:', 0, 0, 'L')
            pdf.set_font('Arial', 'B', 11)
            pdf.cell(0, 8, str(handover_data.person_mobile), 0, 1, 'L')
        
        pdf.ln(5)
        
        # حالة المركبة
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'VEHICLE CONDITION', 0, 1, 'L')
        
        pdf.set_font('Arial', '', 11)
        pdf.cell(50, 8, 'Mileage:', 0, 0, 'L')
        pdf.set_font('Arial', 'B', 11)
        mileage = str(handover_data.mileage) if handover_data.mileage else "0"
        pdf.cell(0, 8, f'{mileage} km', 0, 1, 'L')
        
        pdf.set_font('Arial', '', 11)
        pdf.cell(50, 8, 'Fuel Level:', 0, 0, 'L')
        pdf.set_font('Arial', 'B', 11)
        fuel_level = pdf.safe_text(handover_data.fuel_level, "Unknown")
        pdf.cell(0, 8, fuel_level, 0, 1, 'L')
        
        # المعدات
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, 'EQUIPMENT STATUS:', 0, 1, 'L')
        pdf.set_font('Arial', '', 10)
        
        equipment_items = [
            ('Spare Tire', getattr(handover_data, 'has_spare_tire', False)),
            ('Fire Extinguisher', getattr(handover_data, 'has_fire_extinguisher', False)),
            ('First Aid Kit', getattr(handover_data, 'has_first_aid_kit', False)),
            ('Warning Triangle', getattr(handover_data, 'has_warning_triangle', False)),
            ('Tools', getattr(handover_data, 'has_tools', False))
        ]
        
        for item_name, has_item in equipment_items:
            status = 'Available' if has_item else 'Not Available'
            pdf.cell(0, 6, f'- {item_name}: {status}', 0, 1, 'L')
        
        # رابط النموذج الإلكتروني
        pdf.ln(5)
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'ELECTRONIC FORM ACCESS', 0, 1, 'L')
        pdf.set_font('Arial', '', 10)
        
        if hasattr(handover_data, 'form_link') and handover_data.form_link:
            pdf.cell(0, 8, f'Electronic Form: {handover_data.form_link}', 0, 1, 'L')
        else:
            pdf.cell(0, 8, f'Form ID: {handover_data.id}', 0, 1, 'L')
        
        # الملاحظات
        if handover_data.notes:
            pdf.ln(5)
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, 'ADDITIONAL NOTES:', 0, 1, 'L')
            pdf.set_font('Arial', '', 10)
            notes_clean = pdf.safe_text(handover_data.notes, "Notes in Arabic")
            pdf.multi_cell(0, 6, notes_clean)
        
        # التوقيعات
        pdf.ln(10)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, 'SIGNATURES:', 0, 1, 'L')
        pdf.ln(10)
        
        pdf.set_font('Arial', '', 10)
        pdf.cell(90, 8, 'Delivered by: ____________________', 0, 0, 'L')
        pdf.cell(90, 8, 'Received by: ____________________', 0, 1, 'L')
        pdf.ln(5)
        pdf.cell(90, 8, 'Date: ____________________', 0, 0, 'L')
        pdf.cell(90, 8, 'Date: ____________________', 0, 1, 'L')
        
        # تذييل
        pdf.ln(10)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0, 8, 'This document was generated automatically by the Vehicle Management System', 0, 1, 'C')
        pdf.cell(0, 8, 'For verification, please access the electronic form using the link above', 0, 1, 'C')
        
        # إنتاج الملف
        buffer = BytesIO()
        pdf_output = pdf.output(dest='S').encode('latin-1', errors='replace')
        buffer.write(pdf_output)
        buffer.seek(0)
        return buffer
        
    except Exception as e:
        print(f"Error creating improved handover PDF: {e}")
        return None