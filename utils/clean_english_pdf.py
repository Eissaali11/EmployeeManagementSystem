"""
Clean English Workshop PDF Report Generator
No Arabic text - only English and numbers to avoid black squares
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import inch
from datetime import datetime
import io
import re

def safe_text_filter(text):
    """Filter text to show only ASCII characters - no Arabic to avoid black squares"""
    if not text:
        return "Not specified"
    
    # Convert to string and filter only ASCII characters
    text_str = str(text)
    filtered = re.sub(r'[^\x00-\x7F]+', '', text_str)
    
    return filtered.strip() if filtered.strip() else "Not specified"

def generate_workshop_pdf(vehicle, workshop_records):
    """Generate clean English workshop PDF report without Arabic characters"""
    
    try:
        print("Starting clean English workshop PDF generation...")
        
        # Create PDF buffer
        buffer = io.BytesIO()
        
        # Create canvas
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # Title
        c.setFont("Helvetica-Bold", 18)
        plate_clean = safe_text_filter(vehicle.plate_number)
        title = f"Workshop Records Report - Vehicle: {plate_clean}"
        c.drawString(width/2 - len(title)*4, height - 60, title)
        
        # Vehicle information section
        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, height - 100, "Vehicle Information")
        
        c.setFont("Helvetica", 12)
        y_position = height - 130
        
        # Clean vehicle data
        make_clean = safe_text_filter(vehicle.make)
        model_clean = safe_text_filter(vehicle.model)
        color_clean = safe_text_filter(vehicle.color)
        
        vehicle_info = [
            f"License Plate: {plate_clean}",
            f"Make & Model: {make_clean} {model_clean}",
            f"Year: {vehicle.year}",
            f"Color: {color_clean}",
            f"Current Status: {get_status_english(vehicle.status)}"
        ]
        
        for info in vehicle_info:
            c.drawString(70, y_position, info)
            y_position -= 20
        
        # Separator line
        c.setStrokeColor(colors.blue)
        c.setLineWidth(2)
        c.line(50, y_position - 10, width - 50, y_position - 10)
        
        # Workshop records section
        y_position -= 40
        
        if workshop_records and len(workshop_records) > 0:
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, y_position, f"Workshop Records ({len(workshop_records)} records)")
            
            y_position -= 30
            
            # Create detailed records table
            table_data = []
            table_data.append([
                "Entry Date", "Exit Date", "Reason", "Status", 
                "Cost (SAR)", "Workshop", "Technician", "Days"
            ])
            
            total_cost = 0
            total_days = 0
            
            for record in workshop_records:
                # Entry date
                entry_date = record.entry_date.strftime('%Y-%m-%d') if record.entry_date else "Not specified"
                
                # Exit date
                if record.exit_date:
                    exit_date = record.exit_date.strftime('%Y-%m-%d')
                else:
                    exit_date = "Still in workshop"
                
                # Reason and status
                reason = get_reason_english(record.reason)
                status = get_repair_status_english(record.repair_status)
                
                # Cost
                cost = float(record.cost) if record.cost else 0
                total_cost += cost
                cost_str = f"{cost:,.0f}" if cost > 0 else "0"
                
                # Workshop and technician - clean from Arabic
                workshop_name = safe_text_filter(record.workshop_name) if record.workshop_name else "Not specified"
                technician = safe_text_filter(record.technician_name) if record.technician_name else "Not specified"
                
                # Calculate days
                if record.entry_date:
                    if record.exit_date:
                        days = (record.exit_date - record.entry_date).days
                    else:
                        days = (datetime.now().date() - record.entry_date).days
                    total_days += max(0, days)
                    days_str = str(max(0, days))
                else:
                    days_str = "0"
                
                table_data.append([
                    entry_date, exit_date, reason, status,
                    cost_str, workshop_name, technician, days_str
                ])
            
            # Create and style the table
            if len(table_data) > 1:  # More than just headers
                table = Table(table_data, colWidths=[
                    0.9*inch, 0.9*inch, 1.1*inch, 1.0*inch,
                    0.8*inch, 1.2*inch, 1.0*inch, 0.6*inch
                ])
                
                table.setStyle(TableStyle([
                    # Header row styling
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    
                    # Data rows styling
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    
                    # Alternate row colors
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
                ]))
                
                # Calculate table height and position
                table_height = (len(table_data) * 20) + 20  # Approximate height
                
                if y_position - table_height < 150:  # Not enough space, create new page
                    c.showPage()
                    y_position = height - 80
                
                # Draw the table
                table.wrapOn(c, width - 100, height)
                table.drawOn(c, 50, y_position - table_height)
                
                y_position -= table_height + 40
            
            # Statistics section
            if y_position < 200:  # Create new page for statistics
                c.showPage()
                y_position = height - 80
            
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, y_position, "Summary Statistics")
            
            y_position -= 30
            c.setFont("Helvetica", 12)
            
            # Calculate averages
            record_count = len(workshop_records)
            avg_cost = total_cost / record_count if record_count > 0 else 0
            avg_days = total_days / record_count if record_count > 0 else 0
            
            statistics = [
                f"Total Records: {record_count}",
                f"Total Cost: {total_cost:,.0f} SAR",
                f"Total Repair Days: {total_days} days",
                f"Average Cost per Record: {avg_cost:,.0f} SAR",
                f"Average Repair Duration: {avg_days:.1f} days"
            ]
            
            for stat in statistics:
                c.drawString(70, y_position, stat)
                y_position -= 25
            
            # Workshop performance analysis - only if we have clean data
            if record_count > 0:
                y_position -= 20
                c.setFont("Helvetica-Bold", 12)
                c.drawString(50, y_position, "Performance Analysis")
                
                y_position -= 25
                c.setFont("Helvetica", 10)
                
                # Count by reason
                reason_counts = {}
                status_counts = {}
                workshop_counts = {}
                
                for record in workshop_records:
                    reason = get_reason_english(record.reason)
                    status = get_repair_status_english(record.repair_status)
                    workshop = safe_text_filter(record.workshop_name) if record.workshop_name else "Not specified"
                    
                    reason_counts[reason] = reason_counts.get(reason, 0) + 1
                    status_counts[status] = status_counts.get(status, 0) + 1
                    workshop_counts[workshop] = workshop_counts.get(workshop, 0) + 1
                
                # Most common reason
                if reason_counts:
                    most_common_reason = max(reason_counts.items(), key=lambda x: x[1])
                    c.drawString(70, y_position, f"Most Common Reason: {most_common_reason[0]} ({most_common_reason[1]} times)")
                    y_position -= 15
                
                # Most used workshop - only if we have readable workshop names
                clean_workshops = {k: v for k, v in workshop_counts.items() if k != "Not specified" and len(k) > 2}
                if clean_workshops:
                    most_used_workshop = max(clean_workshops.items(), key=lambda x: x[1])
                    c.drawString(70, y_position, f"Most Used Workshop: {most_used_workshop[0]} ({most_used_workshop[1]} times)")
                    y_position -= 15
                else:
                    c.drawString(70, y_position, "Most Used Workshop: Information contains non-English characters")
                    y_position -= 15
                
                # Completion rate
                completed = status_counts.get('Completed', 0)
                completion_rate = (completed / record_count) * 100
                c.drawString(70, y_position, f"Completion Rate: {completion_rate:.1f}% ({completed}/{record_count})")
        
        else:
            c.setFont("Helvetica", 12)
            c.drawString(70, y_position, "No workshop records available for this vehicle.")
        
        # Footer
        c.setFont("Helvetica", 10)
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
        footer_text = f"Generated by Nuzum Vehicle Management System - {current_time}"
        c.drawString(width/2 - len(footer_text)*3, 50, footer_text)
        
        # Save PDF
        c.save()
        buffer.seek(0)
        
        print("Clean English workshop PDF generated successfully!")
        return buffer.getvalue()
        
    except Exception as e:
        print(f"Error generating clean English workshop PDF: {str(e)}")
        raise e

def get_status_english(status):
    """Translate vehicle status to English"""
    status_map = {
        'available': 'Available',
        'rented': 'Rented',
        'in_workshop': 'In Workshop',
        'accident': 'Accident',
        'in_project': 'In Project'
    }
    return status_map.get(status, status if status else "Unknown")

def get_reason_english(reason):
    """Translate workshop entry reason to English"""
    reason_map = {
        'maintenance': 'Routine Maintenance',
        'breakdown': 'Breakdown',
        'accident': 'Accident Repair',
        'inspection': 'Inspection'
    }
    return reason_map.get(reason, reason if reason else "Not specified")

def get_repair_status_english(status):
    """Translate repair status to English"""
    status_map = {
        'in_progress': 'In Progress',
        'completed': 'Completed',
        'pending_approval': 'Pending Approval',
        'cancelled': 'Cancelled'
    }
    return status_map.get(status, status if status else "Not specified")