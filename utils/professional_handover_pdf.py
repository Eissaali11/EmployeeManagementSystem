"""
Professional Vehicle Handover PDF Generator
Comprehensive and organized design for vehicle handover documents
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
import io
import os

def smart_text_display(text):
    """Display text smartly - keep useful parts, indicate Arabic content"""
    if not text:
        return "Not specified"
    
    text_str = str(text).strip()
    
    if not text_str:
        return "Not specified"
    
    # If text is ASCII, return as is
    if text_str.isascii():
        return text_str
    
    # Extract useful characters (numbers, English letters, symbols)
    useful_chars = ""
    for char in text_str:
        if char.isdigit() or char.isascii():
            useful_chars += char
        elif char in "()[]{}،.-_/\\ ":
            useful_chars += char
    
    useful_chars = useful_chars.strip()
    
    if useful_chars and len(useful_chars) > 1:
        return f"{useful_chars} (Arabic)"
    
    return "Arabic name"

def create_vehicle_handover_pdf(handover_data):
    """Generate professional vehicle handover PDF with organized layout"""
    
    try:
        print("Starting professional handover PDF generation...")
        
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # Add company logo if available
        logo_path = "attached_assets/ChatGPT Image Jun 8, 2025, 05_34_10 PM_1749393284624.png"
        if os.path.exists(logo_path):
            try:
                c.drawImage(logo_path, 50, height - 100, width=60, height=60, preserveAspectRatio=True)
            except:
                pass
        
        # Header section
        c.setFont("Helvetica-Bold", 20)
        title = "VEHICLE HANDOVER DOCUMENT"
        title_width = c.stringWidth(title, "Helvetica-Bold", 20)
        c.drawString((width - title_width)/2, height - 50, title)
        
        # Document info box
        c.setStrokeColor(colors.blue)
        c.setLineWidth(1)
        c.rect(400, height - 140, 150, 80)
        
        c.setFont("Helvetica-Bold", 10)
        c.drawString(410, height - 70, "DOCUMENT INFO")
        c.setFont("Helvetica", 9)
        c.drawString(410, height - 85, f"ID: {handover_data.id}")
        c.drawString(410, height - 100, f"Date: {datetime.now().strftime('%Y-%m-%d')}")
        c.drawString(410, height - 115, f"Time: {datetime.now().strftime('%H:%M')}")
        
        handover_type = "DELIVERY" if str(handover_data.handover_type) == "delivery" else "RETURN"
        c.setFont("Helvetica-Bold", 9)
        c.drawString(410, height - 130, f"Type: {handover_type}")
        
        # Main content starts here
        y_position = height - 170
        
        # Vehicle Information Section
        c.setFillColor(colors.lightblue)
        c.rect(50, y_position - 30, width - 100, 25, fill=1)
        c.setFillColor(colors.black)
        
        c.setFont("Helvetica-Bold", 14)
        c.drawString(60, y_position - 20, "VEHICLE INFORMATION")
        
        y_position -= 50
        
        # Vehicle details table
        vehicle_data = []
        if hasattr(handover_data, 'vehicle_rel') and handover_data.vehicle_rel:
            vehicle = handover_data.vehicle_rel
            vehicle_data = [
                ["License Plate", smart_text_display(vehicle.plate_number)],
                ["Make & Model", f"{smart_text_display(vehicle.make)} {smart_text_display(vehicle.model)}"],
                ["Year", str(vehicle.year) if hasattr(vehicle, 'year') and vehicle.year else "Not specified"],
                ["Color", smart_text_display(vehicle.color) if hasattr(vehicle, 'color') else "Not specified"],
                ["Current Status", vehicle.status if hasattr(vehicle, 'status') else "Not specified"]
            ]
        else:
            vehicle_data = [["Vehicle information", "Not available"]]
        
        # Create vehicle info table
        vehicle_table = Table(vehicle_data, colWidths=[2.5*inch, 3.5*inch])
        vehicle_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        table_height = len(vehicle_data) * 25 + 10
        vehicle_table.wrapOn(c, width - 100, height)
        vehicle_table.drawOn(c, 50, y_position - table_height)
        
        y_position -= table_height + 30
        
        # Handover Details Section
        c.setFillColor(colors.lightgreen)
        c.rect(50, y_position - 30, width - 100, 25, fill=1)
        c.setFillColor(colors.black)
        
        c.setFont("Helvetica-Bold", 14)
        c.drawString(60, y_position - 20, "HANDOVER DETAILS")
        
        y_position -= 50
        
        # Handover details table
        handover_details = [
            ["Handover Date", handover_data.handover_date.strftime('%Y-%m-%d') if handover_data.handover_date else "Not specified"],
            ["Person Name", smart_text_display(handover_data.person_name)],
            ["Mobile Number", handover_data.person_mobile if hasattr(handover_data, 'person_mobile') and handover_data.person_mobile else "Not specified"],
            ["Current Mileage", f"{handover_data.mileage:,} km" if handover_data.mileage else "Not specified"],
            ["Fuel Level", f"{handover_data.fuel_level}%" if handover_data.fuel_level else "Not specified"],
            ["Vehicle Condition", handover_data.vehicle_condition if handover_data.vehicle_condition else "Not specified"]
        ]
        
        handover_table = Table(handover_details, colWidths=[2.5*inch, 3.5*inch])
        handover_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        table_height = len(handover_details) * 25 + 10
        handover_table.wrapOn(c, width - 100, height)
        handover_table.drawOn(c, 50, y_position - table_height)
        
        y_position -= table_height + 30
        
        # Vehicle Equipment Checklist
        c.setFillColor(colors.lightyellow)
        c.rect(50, y_position - 30, width - 100, 25, fill=1)
        c.setFillColor(colors.black)
        
        c.setFont("Helvetica-Bold", 14)
        c.drawString(60, y_position - 20, "VEHICLE EQUIPMENT CHECKLIST")
        
        y_position -= 50
        
        # Equipment checklist
        equipment_items = [
            ["Spare Tire", "✓" if getattr(handover_data, 'has_spare_tire', False) else "✗"],
            ["Fire Extinguisher", "✓" if getattr(handover_data, 'has_fire_extinguisher', False) else "✗"],
            ["First Aid Kit", "✓" if getattr(handover_data, 'has_first_aid_kit', False) else "✗"],
            ["Warning Triangle", "✓" if getattr(handover_data, 'has_warning_triangle', False) else "✗"],
            ["Tools", "✓" if getattr(handover_data, 'has_tools', False) else "✗"]
        ]
        
        equipment_table = Table(equipment_items, colWidths=[4*inch, 2*inch])
        equipment_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        # Color code the checkmarks
        for i, item in enumerate(equipment_items):
            if item[1] == "✓":
                equipment_table.setStyle(TableStyle([
                    ('TEXTCOLOR', (1, i), (1, i), colors.green),
                ]))
            else:
                equipment_table.setStyle(TableStyle([
                    ('TEXTCOLOR', (1, i), (1, i), colors.red),
                ]))
        
        table_height = len(equipment_items) * 25 + 10
        equipment_table.wrapOn(c, width - 100, height)
        equipment_table.drawOn(c, 50, y_position - table_height)
        
        y_position -= table_height + 30
        
        # Notes section if there are notes
        if hasattr(handover_data, 'notes') and handover_data.notes:
            if y_position < 150:  # New page if needed
                c.showPage()
                y_position = height - 80
            
            c.setFillColor(colors.lightcyan)
            c.rect(50, y_position - 30, width - 100, 25, fill=1)
            c.setFillColor(colors.black)
            
            c.setFont("Helvetica-Bold", 14)
            c.drawString(60, y_position - 20, "ADDITIONAL NOTES")
            
            y_position -= 50
            
            # Notes box
            c.setStrokeColor(colors.grey)
            c.setLineWidth(1)
            c.rect(50, y_position - 80, width - 100, 70)
            
            # Notes text
            c.setFont("Helvetica", 10)
            notes_text = smart_text_display(handover_data.notes)
            
            # Split notes into lines if too long
            max_width = width - 120
            words = notes_text.split()
            lines = []
            current_line = ""
            
            for word in words:
                test_line = current_line + " " + word if current_line else word
                if c.stringWidth(test_line, "Helvetica", 10) <= max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            
            if current_line:
                lines.append(current_line)
            
            # Draw notes lines
            for i, line in enumerate(lines[:4]):  # Max 4 lines
                c.drawString(60, y_position - 20 - (i * 15), line)
            
            y_position -= 100
        
        # Signature section
        if y_position < 150:  # New page if needed
            c.showPage()
            y_position = height - 80
        
        c.setFillColor(colors.lightpink)
        c.rect(50, y_position - 30, width - 100, 25, fill=1)
        c.setFillColor(colors.black)
        
        c.setFont("Helvetica-Bold", 14)
        c.drawString(60, y_position - 20, "SIGNATURES")
        
        y_position -= 50
        
        # Signature boxes
        signature_data = [
            ["Delivered By", "Received By"],
            ["", ""],
            ["", ""],
            ["Name: ________________", "Name: ________________"],
            ["Date: ________________", "Date: ________________"],
            ["Signature: ____________", "Signature: ____________"]
        ]
        
        signature_table = Table(signature_data, colWidths=[3*inch, 3*inch])
        signature_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ]))
        
        table_height = len(signature_data) * 30 + 10
        signature_table.wrapOn(c, width - 100, height)
        signature_table.drawOn(c, 50, y_position - table_height)
        
        # Footer
        c.setFont("Helvetica", 8)
        footer_text = f"Generated by Nuzum Vehicle Management System - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        footer_width = c.stringWidth(footer_text, "Helvetica", 8)
        c.drawString((width - footer_width)/2, 30, footer_text)
        
        # Page border
        c.setStrokeColor(colors.black)
        c.setLineWidth(2)
        c.rect(30, 20, width - 60, height - 40)
        
        c.save()
        buffer.seek(0)
        
        print("Professional handover PDF generated successfully!")
        return buffer
        
    except Exception as e:
        print(f"Error generating professional handover PDF: {str(e)}")
        raise e