"""
تقرير الموظف المبسط مع التصميم المطلوب - نظام نُظم
"""
import os
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
from models import Employee, VehicleHandover


def generate_simple_designed_employee_report(employee_id):
    """إنشاء تقرير الموظف المبسط بالتصميم المطلوب"""
    try:
        # البحث عن الموظف
        employee = Employee.query.get(employee_id)
        if not employee:
            return None, "الموظف غير موجود"
        
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # الألوان
        blue_header = HexColor('#4472C4')
        green_border = HexColor('#70AD47')
        light_gray = HexColor('#F2F2F2')
        
        # العنوان الرئيسي
        c.setFillColor(blue_header)
        c.rect(50, height - 70, width - 100, 40, fill=True, stroke=False)
        
        c.setFillColor(HexColor('#FFFFFF'))
        c.setFont("Helvetica-Bold", 16)
        title = "Employee Basic Information Report"
        text_width = c.stringWidth(title, "Helvetica-Bold", 16)
        c.drawString((width - text_width) / 2, height - 55, title)
        
        y_position = height - 90
        
        # الصورة الشخصية
        c.setFillColor(HexColor('#000000'))
        c.setFont("Helvetica-Bold", 12)
        image_title = "Personal Photo"
        text_width = c.stringWidth(image_title, "Helvetica-Bold", 12)
        c.drawString((width - text_width) / 2, y_position, image_title)
        
        # إطار الصورة الشخصية (دائري)
        image_x = width / 2 - 60
        image_y = y_position - 140
        
        c.setStrokeColor(blue_header)
        c.setLineWidth(3)
        c.circle(image_x + 60, image_y + 60, 55)
        
        if employee.profile_image and os.path.exists(f"static/{employee.profile_image}"):
            try:
                c.drawImage(f"static/{employee.profile_image}", image_x + 5, image_y + 5, 
                           width=110, height=110, preserveAspectRatio=True, mask='auto')
            except:
                c.setFont("Helvetica", 10)
                c.drawString(image_x + 35, image_y + 55, "Image Available")
        else:
            c.setFont("Helvetica", 10)
            c.drawString(image_x + 35, image_y + 55, "No Image")
        
        y_position = image_y - 40
        
        # صورة الهوية الوطنية
        c.setFillColor(HexColor('#000000'))
        c.setFont("Helvetica-Bold", 12)
        id_title = "National ID Photo"
        text_width = c.stringWidth(id_title, "Helvetica-Bold", 12)
        c.drawString((width - text_width) / 2, y_position, id_title)
        
        # إطار صورة الهوية (مستطيل أخضر)
        id_image_x = width / 2 - 100
        id_image_y = y_position - 100
        
        c.setStrokeColor(green_border)
        c.setLineWidth(3)
        c.rect(id_image_x, id_image_y, 200, 80)
        
        if employee.national_id_image and os.path.exists(f"static/{employee.national_id_image}"):
            try:
                c.drawImage(f"static/{employee.national_id_image}", id_image_x + 5, id_image_y + 5, 
                           width=190, height=70, preserveAspectRatio=True)
            except:
                c.setFont("Helvetica", 8)
                c.drawString(id_image_x + 75, id_image_y + 35, "ID Image Available")
        else:
            c.setFont("Helvetica", 8)
            c.drawString(id_image_x + 85, id_image_y + 35, "No ID Image")
        
        y_position = id_image_y - 40
        
        # صورة رخصة القيادة
        c.setFillColor(HexColor('#000000'))
        c.setFont("Helvetica-Bold", 12)
        license_title = "Driving License Photo"
        text_width = c.stringWidth(license_title, "Helvetica-Bold", 12)
        c.drawString((width - text_width) / 2, y_position, license_title)
        
        # إطار صورة الرخصة (مستطيل أخضر)
        license_image_x = width / 2 - 100
        license_image_y = y_position - 100
        
        c.setStrokeColor(green_border)
        c.setLineWidth(3)
        c.rect(license_image_x, license_image_y, 200, 80)
        
        if employee.license_image and os.path.exists(f"static/{employee.license_image}"):
            try:
                c.drawImage(f"static/{employee.license_image}", license_image_x + 5, license_image_y + 5, 
                           width=190, height=70, preserveAspectRatio=True)
            except:
                c.setFont("Helvetica", 8)
                c.drawString(license_image_x + 70, license_image_y + 35, "License Image Available")
        else:
            c.setFont("Helvetica", 8)
            c.drawString(license_image_x + 80, license_image_y + 35, "No License Image")
        
        y_position = license_image_y - 60
        
        # جدول المعلومات الأساسية
        c.setFillColor(blue_header)
        c.rect(50, y_position, width - 100, 25, fill=True, stroke=False)
        
        c.setFillColor(HexColor('#FFFFFF'))
        c.setFont("Helvetica-Bold", 12)
        basic_info_title = "Basic Information"
        text_width = c.stringWidth(basic_info_title, "Helvetica-Bold", 12)
        c.drawString((width - text_width) / 2, y_position + 8, basic_info_title)
        
        y_position -= 35
        
        # بيانات المعلومات الأساسية
        basic_info_data = [
            ["Name", str(employee.name or "Not specified")],
            ["Employee ID", str(employee.employee_id or "Not specified")],
            ["Mobile", str(employee.mobile or "Not specified")],
            ["National ID", str(employee.national_id or "Not specified")],
            ["Job Title", str(employee.job_title or "Not specified")],
            ["Department", str(employee.department.name if employee.department else "Not specified")],
        ]
        
        # رسم الجدول
        for i, (label, value) in enumerate(basic_info_data):
            row_y = y_position - (i * 25)
            
            # خلفية الصف
            if i % 2 == 0:
                c.setFillColor(light_gray)
                c.rect(50, row_y - 20, width - 100, 25, fill=True, stroke=False)
            
            # النص
            c.setFillColor(HexColor('#000000'))
            c.setFont("Helvetica-Bold", 10)
            c.drawString(60, row_y - 8, label)
            c.setFont("Helvetica", 10)
            c.drawString(200, row_y - 8, value[:50])  # تحديد طول النص
        
        y_position -= len(basic_info_data) * 25 + 40
        
        # معلومات العمل
        c.setFillColor(blue_header)
        c.rect(50, y_position, width - 100, 25, fill=True, stroke=False)
        
        c.setFillColor(HexColor('#FFFFFF'))
        c.setFont("Helvetica-Bold", 12)
        work_info_title = "Work Information"
        text_width = c.stringWidth(work_info_title, "Helvetica-Bold", 12)
        c.drawString((width - text_width) / 2, y_position + 8, work_info_title)
        
        y_position -= 35
        
        # بيانات معلومات العمل
        work_info_data = [
            ["Join Date", employee.join_date.strftime('%Y-%m-%d') if employee.join_date else "Not specified"],
            ["Basic Salary", f"{employee.basic_salary:,.2f} SAR" if employee.basic_salary else "Not specified"],
            ["Contract Type", str(employee.contract_type or "Not specified")],
            ["Location", str(employee.location or "Not specified")],
            ["Project", str(employee.project or "Not specified")],
            ["Status", str(employee.status or "Not specified")],
        ]
        
        # رسم جدول معلومات العمل
        for i, (label, value) in enumerate(work_info_data):
            row_y = y_position - (i * 25)
            
            # خلفية الصف
            if i % 2 == 0:
                c.setFillColor(light_gray)
                c.rect(50, row_y - 20, width - 100, 25, fill=True, stroke=False)
            
            # النص
            c.setFillColor(HexColor('#000000'))
            c.setFont("Helvetica-Bold", 10)
            c.drawString(60, row_y - 8, label)
            c.setFont("Helvetica", 10)
            c.drawString(200, row_y - 8, str(value)[:50])
        
        y_position -= len(work_info_data) * 25 + 40
        
        # سجلات المركبات (إذا كان هناك مساحة)
        vehicle_handovers = VehicleHandover.query.filter_by(employee_id=employee_id).limit(3).all()
        if vehicle_handovers and y_position > 150:
            c.setFillColor(blue_header)
            c.rect(50, y_position, width - 100, 25, fill=True, stroke=False)
            
            c.setFillColor(HexColor('#FFFFFF'))
            c.setFont("Helvetica-Bold", 12)
            vehicle_title = f"Vehicle Records (Last {len(vehicle_handovers)} operations)"
            text_width = c.stringWidth(vehicle_title, "Helvetica-Bold", 12)
            c.drawString((width - text_width) / 2, y_position + 8, vehicle_title)
            
            y_position -= 35
            
            # عناوين الأعمدة
            headers = ["Plate Number", "Operation Type", "Date", "Person"]
            
            for i, header in enumerate(headers):
                c.setFillColor(HexColor('#E7E6E6'))
                c.rect(50 + i * 125, y_position - 20, 125, 25, fill=True, stroke=True)
                c.setFillColor(HexColor('#000000'))
                c.setFont("Helvetica-Bold", 9)
                c.drawString(55 + i * 125, y_position - 8, header)
            
            y_position -= 25
            
            # بيانات المركبات
            for j, handover in enumerate(vehicle_handovers):
                row_data = [
                    str(handover.vehicle.plate_number if handover.vehicle else "N/A"),
                    str(handover.handover_type or "N/A"),
                    handover.handover_date.strftime('%Y-%m-%d') if handover.handover_date else "N/A",
                    str(handover.person_name or "N/A")
                ]
                
                for i, data in enumerate(row_data):
                    if j % 2 == 0:
                        c.setFillColor(light_gray)
                        c.rect(50 + i * 125, y_position - 20, 125, 25, fill=True, stroke=True)
                    else:
                        c.setStrokeColor(HexColor('#000000'))
                        c.rect(50 + i * 125, y_position - 20, 125, 25, fill=False, stroke=True)
                    
                    c.setFillColor(HexColor('#000000'))
                    c.setFont("Helvetica", 8)
                    c.drawString(55 + i * 125, y_position - 8, data[:15])
                
                y_position -= 25
        
        # تذييل الصفحة
        c.setFont("Helvetica", 8)
        c.setFillColor(HexColor('#666666'))
        footer_text = f"Generated: {employee.created_at.strftime('%Y-%m-%d %H:%M') if employee.created_at else 'Unknown'}"
        c.drawString(50, 30, footer_text)
        c.drawString(width - 150, 30, "Nuzum Management System")
        
        c.save()
        buffer.seek(0)
        return buffer.getvalue(), None
        
    except Exception as e:
        print(f"خطأ في إنشاء التقرير المبسط: {str(e)}")
        return None, str(e)