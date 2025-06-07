"""
دالة بسيطة لإنشاء PDF نماذج تسليم/استلام المركبات باللغة الإنجليزية فقط
"""

from fpdf import FPDF
from io import BytesIO
from datetime import datetime


def create_simple_handover_pdf(handover_data):
    """
    إنشاء PDF بسيط لنموذج تسليم/استلام المركبة (إنجليزي فقط)
    """
    try:
        pdf = FPDF('P', 'mm', 'A4')
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        
        # Header
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'Vehicle Handover Document', 0, 1, 'C')
        pdf.ln(10)
        
        # Document info
        pdf.set_font('Arial', '', 10)
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        pdf.cell(0, 8, f'Document ID: {handover_data.id}', 0, 0, 'L')
        pdf.cell(0, 8, f'Generated: {current_time}', 0, 1, 'R')
        pdf.ln(5)
        
        # Line separator
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(8)
        
        # Vehicle Information
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, 'VEHICLE INFORMATION', 0, 1, 'L')
        pdf.ln(2)
        
        if hasattr(handover_data, 'vehicle_rel') and handover_data.vehicle_rel:
            vehicle = handover_data.vehicle_rel
            
            pdf.set_font('Arial', '', 10)
            
            # Clean text function
            def clean_text(text):
                if not text:
                    return "N/A"
                # Remove any non-ASCII characters
                return ''.join(char for char in str(text) if ord(char) < 128) or "N/A"
            
            pdf.cell(40, 6, 'Plate Number:', 0, 0, 'L')
            pdf.cell(0, 6, clean_text(vehicle.plate_number), 0, 1, 'L')
            
            pdf.cell(40, 6, 'Make:', 0, 0, 'L')
            pdf.cell(0, 6, clean_text(vehicle.make), 0, 1, 'L')
            
            pdf.cell(40, 6, 'Model:', 0, 0, 'L')
            pdf.cell(0, 6, clean_text(vehicle.model), 0, 1, 'L')
            
            if hasattr(vehicle, 'year') and vehicle.year:
                pdf.cell(40, 6, 'Year:', 0, 0, 'L')
                pdf.cell(0, 6, str(vehicle.year), 0, 1, 'L')
                
            if hasattr(vehicle, 'color') and vehicle.color:
                pdf.cell(40, 6, 'Color:', 0, 0, 'L')
                pdf.cell(0, 6, clean_text(vehicle.color), 0, 1, 'L')
        else:
            pdf.set_font('Arial', '', 10)
            pdf.cell(0, 6, 'Vehicle information not available', 0, 1, 'L')
        
        pdf.ln(8)
        
        # Handover Details
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, 'HANDOVER DETAILS', 0, 1, 'L')
        pdf.ln(2)
        
        pdf.set_font('Arial', '', 10)
        
        # Date and time
        if handover_data.handover_date:
            date_str = handover_data.handover_date.strftime("%Y-%m-%d")
            time_str = handover_data.handover_date.strftime("%H:%M")
        else:
            date_str = "N/A"
            time_str = "N/A"
            
        pdf.cell(40, 6, 'Date:', 0, 0, 'L')
        pdf.cell(0, 6, date_str, 0, 1, 'L')
        
        pdf.cell(40, 6, 'Time:', 0, 0, 'L')
        pdf.cell(0, 6, time_str, 0, 1, 'L')
        
        # Type
        handover_type = "DELIVERY" if str(handover_data.handover_type) == "delivery" else "RETURN"
        pdf.cell(40, 6, 'Type:', 0, 0, 'L')
        pdf.cell(0, 6, handover_type, 0, 1, 'L')
        
        # Person name (clean)
        def clean_person_name(name):
            if not name:
                return "N/A"
            # Remove Arabic characters
            cleaned = ''.join(char for char in str(name) if ord(char) < 128)
            return cleaned.strip() or "Person Name (Arabic)"
        
        pdf.cell(40, 6, 'Person Name:', 0, 0, 'L')
        pdf.cell(0, 6, clean_person_name(handover_data.person_name), 0, 1, 'L')
        
        # Mobile number
        if hasattr(handover_data, 'person_mobile') and handover_data.person_mobile:
            pdf.cell(40, 6, 'Mobile Number:', 0, 0, 'L')
            pdf.cell(0, 6, str(handover_data.person_mobile), 0, 1, 'L')
        
        pdf.ln(8)
        
        # Vehicle Condition
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, 'VEHICLE CONDITION', 0, 1, 'L')
        pdf.ln(2)
        
        pdf.set_font('Arial', '', 10)
        
        pdf.cell(40, 6, 'Mileage:', 0, 0, 'L')
        mileage = str(handover_data.mileage) if handover_data.mileage else "0"
        pdf.cell(0, 6, f'{mileage} km', 0, 1, 'L')
        
        pdf.cell(40, 6, 'Fuel Level:', 0, 0, 'L')
        fuel_level = str(handover_data.fuel_level) if handover_data.fuel_level else "Unknown"
        # Clean fuel level text
        fuel_clean = ''.join(char for char in fuel_level if ord(char) < 128) or "Unknown"
        pdf.cell(0, 6, fuel_clean, 0, 1, 'L')
        
        pdf.ln(5)
        
        # Equipment Status
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 6, 'EQUIPMENT STATUS:', 0, 1, 'L')
        pdf.set_font('Arial', '', 9)
        
        equipment_items = [
            ('Spare Tire', getattr(handover_data, 'has_spare_tire', False)),
            ('Fire Extinguisher', getattr(handover_data, 'has_fire_extinguisher', False)),
            ('First Aid Kit', getattr(handover_data, 'has_first_aid_kit', False)),
            ('Warning Triangle', getattr(handover_data, 'has_warning_triangle', False)),
            ('Tools', getattr(handover_data, 'has_tools', False))
        ]
        
        for item_name, has_item in equipment_items:
            status = 'Available' if has_item else 'Not Available'
            pdf.cell(0, 5, f'- {item_name}: {status}', 0, 1, 'L')
        
        pdf.ln(8)
        
        # Electronic Form Link
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, 'ELECTRONIC FORM ACCESS', 0, 1, 'L')
        pdf.ln(2)
        
        pdf.set_font('Arial', '', 10)
        if hasattr(handover_data, 'form_link') and handover_data.form_link:
            pdf.cell(0, 6, f'Electronic Form: {handover_data.form_link}', 0, 1, 'L')
        else:
            pdf.cell(0, 6, f'Form ID: {handover_data.id}', 0, 1, 'L')
        
        # Notes (if any, cleaned)
        if handover_data.notes:
            pdf.ln(5)
            pdf.set_font('Arial', 'B', 10)
            pdf.cell(0, 6, 'ADDITIONAL NOTES:', 0, 1, 'L')
            pdf.set_font('Arial', '', 9)
            # Clean notes
            notes_clean = ''.join(char for char in str(handover_data.notes) if ord(char) < 128)
            if notes_clean.strip():
                pdf.multi_cell(0, 5, notes_clean.strip())
            else:
                pdf.cell(0, 5, 'Notes in Arabic language', 0, 1, 'L')
        
        pdf.ln(10)
        
        # Signatures
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 6, 'SIGNATURES:', 0, 1, 'L')
        pdf.ln(8)
        
        pdf.set_font('Arial', '', 9)
        pdf.cell(90, 6, 'Delivered by: ____________________', 0, 0, 'L')
        pdf.cell(90, 6, 'Received by: ____________________', 0, 1, 'L')
        pdf.ln(5)
        pdf.cell(90, 6, 'Date: ____________________', 0, 0, 'L')
        pdf.cell(90, 6, 'Date: ____________________', 0, 1, 'L')
        
        # Footer
        pdf.ln(10)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(5)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0, 6, 'This document was generated automatically by the Vehicle Management System', 0, 1, 'C')
        pdf.cell(0, 6, 'For verification, please access the electronic form using the link above', 0, 1, 'C')
        
        # Generate PDF
        buffer = BytesIO()
        pdf_content = pdf.output(dest='S')
        
        # Safe encoding - only ASCII characters
        if isinstance(pdf_content, str):
            buffer.write(pdf_content.encode('ascii', errors='ignore'))
        else:
            buffer.write(pdf_content)
        
        buffer.seek(0)
        return buffer
        
    except Exception as e:
        print(f"Error creating simple handover PDF: {e}")
        return None