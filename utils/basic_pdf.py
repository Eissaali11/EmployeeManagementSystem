"""
دالة أساسية جداً لإنشاء PDF بدون أي نصوص عربية
"""

from fpdf import FPDF
from io import BytesIO
from datetime import datetime


def create_basic_pdf(handover_data):
    """
    إنشاء PDF أساسي جداً بأحرف إنجليزية فقط
    """
    try:
        pdf = FPDF()
        pdf.add_page()
        
        # Header
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'Vehicle Handover Document', 0, 1, 'C')
        pdf.ln(10)
        
        # Basic info
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 8, f'Document ID: {handover_data.id}', 0, 1, 'L')
        pdf.cell(0, 8, f'Date: {datetime.now().strftime("%Y-%m-%d")}', 0, 1, 'L')
        pdf.ln(10)
        
        # Vehicle info section
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 8, 'VEHICLE INFORMATION', 0, 1, 'L')
        pdf.ln(5)
        
        if hasattr(handover_data, 'vehicle_rel') and handover_data.vehicle_rel:
            vehicle = handover_data.vehicle_rel
            
            pdf.set_font('Arial', '', 12)
            
            # Safe text extraction - remove any non-ASCII
            def safe_str(text):
                if not text:
                    return "N/A"
                return ''.join(c for c in str(text) if ord(c) < 128).strip() or "N/A"
            
            pdf.cell(0, 6, f'Plate Number: {safe_str(vehicle.plate_number)}', 0, 1, 'L')
            pdf.cell(0, 6, f'Make: {safe_str(vehicle.make)}', 0, 1, 'L')
            pdf.cell(0, 6, f'Model: {safe_str(vehicle.model)}', 0, 1, 'L')
            
            if hasattr(vehicle, 'year') and vehicle.year:
                pdf.cell(0, 6, f'Year: {vehicle.year}', 0, 1, 'L')
        else:
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 6, 'Vehicle information not available', 0, 1, 'L')
        
        pdf.ln(10)
        
        # Handover details
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 8, 'HANDOVER DETAILS', 0, 1, 'L')
        pdf.ln(5)
        
        pdf.set_font('Arial', '', 12)
        
        if handover_data.handover_date:
            pdf.cell(0, 6, f'Date: {handover_data.handover_date.strftime("%Y-%m-%d")}', 0, 1, 'L')
            pdf.cell(0, 6, f'Time: {handover_data.handover_date.strftime("%H:%M")}', 0, 1, 'L')
        
        handover_type = "DELIVERY" if str(handover_data.handover_type) == "delivery" else "RETURN"
        pdf.cell(0, 6, f'Type: {handover_type}', 0, 1, 'L')
        
        # Person name - completely safe
        person_name = "Person Name"
        if handover_data.person_name:
            clean_name = ''.join(c for c in str(handover_data.person_name) if ord(c) < 128).strip()
            if clean_name:
                person_name = clean_name
        pdf.cell(0, 6, f'Person: {person_name}', 0, 1, 'L')
        
        pdf.ln(10)
        
        # Vehicle condition
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 8, 'VEHICLE CONDITION', 0, 1, 'L')
        pdf.ln(5)
        
        pdf.set_font('Arial', '', 12)
        mileage = str(handover_data.mileage) if handover_data.mileage else "0"
        pdf.cell(0, 6, f'Mileage: {mileage} km', 0, 1, 'L')
        
        # Fuel level - safe extraction
        fuel_level = "Unknown"
        if handover_data.fuel_level:
            clean_fuel = ''.join(c for c in str(handover_data.fuel_level) if ord(c) < 128).strip()
            if clean_fuel:
                fuel_level = clean_fuel
        pdf.cell(0, 6, f'Fuel Level: {fuel_level}', 0, 1, 'L')
        
        pdf.ln(10)
        
        # Equipment status
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 6, 'Equipment Status:', 0, 1, 'L')
        pdf.set_font('Arial', '', 10)
        
        equipment = [
            ('Spare Tire', getattr(handover_data, 'has_spare_tire', False)),
            ('Fire Extinguisher', getattr(handover_data, 'has_fire_extinguisher', False)),
            ('First Aid Kit', getattr(handover_data, 'has_first_aid_kit', False)),
            ('Warning Triangle', getattr(handover_data, 'has_warning_triangle', False)),
            ('Tools', getattr(handover_data, 'has_tools', False))
        ]
        
        for item, available in equipment:
            status = "Available" if available else "Not Available"
            pdf.cell(0, 5, f'- {item}: {status}', 0, 1, 'L')
        
        pdf.ln(10)
        
        # Electronic form link
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 6, 'Electronic Form Access:', 0, 1, 'L')
        pdf.set_font('Arial', '', 10)
        
        if hasattr(handover_data, 'form_link') and handover_data.form_link:
            pdf.cell(0, 5, f'Link: {handover_data.form_link}', 0, 1, 'L')
        else:
            pdf.cell(0, 5, f'Form ID: {handover_data.id}', 0, 1, 'L')
        
        pdf.ln(15)
        
        # Signatures
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 6, 'Signatures:', 0, 1, 'L')
        pdf.ln(10)
        
        pdf.set_font('Arial', '', 10)
        pdf.cell(90, 6, 'Delivered by: ___________________', 0, 0, 'L')
        pdf.cell(90, 6, 'Received by: ___________________', 0, 1, 'L')
        pdf.ln(8)
        pdf.cell(90, 6, 'Date: ___________________', 0, 0, 'L')
        pdf.cell(90, 6, 'Date: ___________________', 0, 1, 'L')
        
        # Footer
        pdf.ln(15)
        pdf.set_font('Arial', 'I', 8)
        pdf.cell(0, 5, 'Generated by Vehicle Management System', 0, 1, 'C')
        
        # Generate file with safe encoding
        buffer = BytesIO()
        pdf_output = pdf.output(dest='S')
        
        # Ensure only ASCII characters
        if isinstance(pdf_output, str):
            # Convert to bytes using only ASCII
            safe_output = pdf_output.encode('ascii', errors='ignore')
            buffer.write(safe_output)
        else:
            buffer.write(pdf_output)
        
        buffer.seek(0)
        return buffer
        
    except Exception as e:
        print(f"Error in basic PDF: {e}")
        # Create minimal fallback PDF
        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font('Arial', 'B', 16)
            pdf.cell(0, 10, 'Vehicle Handover Document', 0, 1, 'C')
            pdf.ln(10)
            pdf.set_font('Arial', '', 12)
            pdf.cell(0, 8, f'Document ID: {handover_data.id}', 0, 1, 'L')
            pdf.cell(0, 8, 'Unable to generate full document', 0, 1, 'L')
            
            buffer = BytesIO()
            buffer.write(pdf.output(dest='S').encode('ascii', errors='ignore'))
            buffer.seek(0)
            return buffer
        except:
            return None