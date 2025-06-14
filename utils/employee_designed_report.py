"""
تقرير الموظف بالتصميم المطلوب - نظام نُظم
"""
import os
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.colors import Color, HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Table, TableStyle
from models import Employee, VehicleHandover


def generate_designed_employee_report(employee_id):
    """إنشاء تقرير الموظف بالتصميم المطلوب"""
    try:
        # البحث عن الموظف
        employee = Employee.query.get(employee_id)
        if not employee:
            return None, "الموظف غير موجود"
        
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # إعداد الخط العربي
        arabic_font_available = False
        try:
            font_path = os.path.join(os.path.dirname(__file__), '..', 'Cairo.ttf')
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('Cairo', font_path))
                arabic_font_available = True
        except:
            pass
        
        # الألوان
        blue_header = HexColor('#4472C4')
        green_border = HexColor('#70AD47')
        
        # العنوان الرئيسي
        c.setFillColor(blue_header)
        c.rect(50, height - 70, width - 100, 40, fill=True, stroke=False)
        
        c.setFillColor(HexColor('#FFFFFF'))
        if arabic_font_available:
            c.setFont("Cairo", 16)
            title = "تقرير المعلومات الأساسية للموظف"
        else:
            c.setFont("Helvetica-Bold", 16)
            title = "Employee Basic Information Report"
        
        text_width = c.stringWidth(title, "Cairo" if arabic_font_available else "Helvetica-Bold", 16)
        c.drawString((width - text_width) / 2, height - 55, title)
        
        y_position = height - 90
        
        # الصورة الشخصية
        c.setFillColor(HexColor('#000000'))
        if arabic_font_available:
            c.setFont("Cairo", 12)
            image_title = "الصورة الشخصية"
        else:
            c.setFont("Helvetica-Bold", 12)
            image_title = "Personal Photo"
        
        text_width = c.stringWidth(image_title, "Cairo" if arabic_font_available else "Helvetica-Bold", 12)
        c.drawString((width - text_width) / 2, y_position, image_title)
        
        # إطار الصورة الشخصية (دائري)
        image_x = width / 2 - 60
        image_y = y_position - 140
        
        if employee.profile_image and os.path.exists(f"static/{employee.profile_image}"):
            try:
                # رسم دائرة للصورة الشخصية
                c.setStrokeColor(blue_header)
                c.setLineWidth(3)
                c.circle(image_x + 60, image_y + 60, 55)
                c.drawImage(f"static/{employee.profile_image}", image_x + 5, image_y + 5, width=110, height=110, mask='auto')
            except:
                # رسم دائرة فارغة إذا فشل تحميل الصورة
                c.setStrokeColor(blue_header)
                c.setLineWidth(3)
                c.circle(image_x + 60, image_y + 60, 55)
                c.setFont("Helvetica", 10)
                c.drawString(image_x + 35, image_y + 55, "No Image")
        else:
            # دائرة فارغة
            c.setStrokeColor(blue_header)
            c.setLineWidth(3)
            c.circle(image_x + 60, image_y + 60, 55)
            c.setFont("Helvetica", 10)
            c.drawString(image_x + 35, image_y + 55, "No Image")
        
        y_position = image_y - 40
        
        # صورة الهوية الوطنية
        c.setFillColor(HexColor('#000000'))
        if arabic_font_available:
            c.setFont("Cairo", 12)
            id_title = "صورة الهوية الوطنية"
        else:
            c.setFont("Helvetica-Bold", 12)
            id_title = "National ID"
        
        text_width = c.stringWidth(id_title, "Cairo" if arabic_font_available else "Helvetica-Bold", 12)
        c.drawString((width - text_width) / 2, y_position, id_title)
        
        # إطار صورة الهوية (مستطيل أخضر)
        id_image_x = width / 2 - 100
        id_image_y = y_position - 100
        
        c.setStrokeColor(green_border)
        c.setLineWidth(3)
        c.rect(id_image_x, id_image_y, 200, 80)
        
        if employee.national_id_image and os.path.exists(f"static/{employee.national_id_image}"):
            try:
                c.drawImage(f"static/{employee.national_id_image}", id_image_x + 5, id_image_y + 5, width=190, height=70)
            except:
                c.setFont("Helvetica", 10)
                c.drawString(id_image_x + 85, id_image_y + 35, "No Image")
        else:
            c.setFont("Helvetica", 10)
            c.drawString(id_image_x + 85, id_image_y + 35, "No Image")
        
        y_position = id_image_y - 40
        
        # صورة رخصة القيادة
        c.setFillColor(HexColor('#000000'))
        if arabic_font_available:
            c.setFont("Cairo", 12)
            license_title = "صورة رخصة القيادة"
        else:
            c.setFont("Helvetica-Bold", 12)
            license_title = "Driving License"
        
        text_width = c.stringWidth(license_title, "Cairo" if arabic_font_available else "Helvetica-Bold", 12)
        c.drawString((width - text_width) / 2, y_position, license_title)
        
        # إطار صورة الرخصة (مستطيل أخضر)
        license_image_x = width / 2 - 100
        license_image_y = y_position - 100
        
        c.setStrokeColor(green_border)
        c.setLineWidth(3)
        c.rect(license_image_x, license_image_y, 200, 80)
        
        if employee.license_image and os.path.exists(f"static/{employee.license_image}"):
            try:
                c.drawImage(f"static/{employee.license_image}", license_image_x + 5, license_image_y + 5, width=190, height=70)
            except:
                c.setFont("Helvetica", 10)
                c.drawString(license_image_x + 85, license_image_y + 35, "No Image")
        else:
            c.setFont("Helvetica", 10)
            c.drawString(license_image_x + 85, license_image_y + 35, "No Image")
        
        y_position = license_image_y - 60
        
        # جدول المعلومات الأساسية
        c.setFillColor(blue_header)
        c.rect(50, y_position, width - 100, 25, fill=True, stroke=False)
        
        c.setFillColor(HexColor('#FFFFFF'))
        if arabic_font_available:
            c.setFont("Cairo", 12)
            basic_info_title = "المعلومات الأساسية"
        else:
            c.setFont("Helvetica-Bold", 12)
            basic_info_title = "Basic Information"
        
        text_width = c.stringWidth(basic_info_title, "Cairo" if arabic_font_available else "Helvetica-Bold", 12)
        c.drawString((width - text_width) / 2, y_position + 8, basic_info_title)
        
        y_position -= 35
        
        # بيانات المعلومات الأساسية
        basic_info_data = [
            ["الاسم" if arabic_font_available else "Name", employee.name or "غير محدد"],
            ["رقم الموظف" if arabic_font_available else "Employee ID", employee.employee_id or "غير محدد"],
            ["الجوال" if arabic_font_available else "Mobile", employee.mobile or "غير محدد"],
            ["رقم الهوية" if arabic_font_available else "National ID", employee.national_id or "غير محدد"],
            ["المسمى الوظيفي" if arabic_font_available else "Job Title", employee.job_title or "غير محدد"],
            ["القسم" if arabic_font_available else "Department", employee.department.name if employee.department else "غير محدد"],
        ]
        
        # رسم الجدول
        for i, (label, value) in enumerate(basic_info_data):
            row_y = y_position - (i * 25)
            
            # خلفية الصف
            if i % 2 == 0:
                c.setFillColor(HexColor('#F2F2F2'))
                c.rect(50, row_y - 20, width - 100, 25, fill=True, stroke=False)
            
            # النص
            c.setFillColor(HexColor('#000000'))
            c.setFont("Cairo" if arabic_font_available else "Helvetica-Bold", 10)
            c.drawString(60, row_y - 8, label)
            c.setFont("Cairo" if arabic_font_available else "Helvetica", 10)
            c.drawString(200, row_y - 8, str(value))
        
        y_position -= len(basic_info_data) * 25 + 40
        
        # معلومات العمل
        c.setFillColor(blue_header)
        c.rect(50, y_position, width - 100, 25, fill=True, stroke=False)
        
        c.setFillColor(HexColor('#FFFFFF'))
        if arabic_font_available:
            c.setFont("Cairo", 12)
            work_info_title = "معلومات العمل"
        else:
            c.setFont("Helvetica-Bold", 12)
            work_info_title = "Work Information"
        
        text_width = c.stringWidth(work_info_title, "Cairo" if arabic_font_available else "Helvetica-Bold", 12)
        c.drawString((width - text_width) / 2, y_position + 8, work_info_title)
        
        y_position -= 35
        
        # بيانات معلومات العمل
        work_info_data = [
            ["تاريخ الانضمام" if arabic_font_available else "Join Date", 
             employee.join_date.strftime('%Y-%m-%d') if employee.join_date else "غير محدد"],
            ["الراتب الأساسي" if arabic_font_available else "Basic Salary", 
             f"{employee.basic_salary:,.2f} ريال" if employee.basic_salary else "غير محدد"],
            ["نوع العقد" if arabic_font_available else "Contract Type", employee.contract_type or "غير محدد"],
            ["الموقع" if arabic_font_available else "Location", employee.location or "غير محدد"],
            ["المشروع" if arabic_font_available else "Project", employee.project or "غير محدد"],
            ["الحالة" if arabic_font_available else "Status", employee.status or "غير محدد"],
        ]
        
        # رسم جدول معلومات العمل
        for i, (label, value) in enumerate(work_info_data):
            row_y = y_position - (i * 25)
            
            # خلفية الصف
            if i % 2 == 0:
                c.setFillColor(HexColor('#F2F2F2'))
                c.rect(50, row_y - 20, width - 100, 25, fill=True, stroke=False)
            
            # النص
            c.setFillColor(HexColor('#000000'))
            c.setFont("Cairo" if arabic_font_available else "Helvetica-Bold", 10)
            c.drawString(60, row_y - 8, label)
            c.setFont("Cairo" if arabic_font_available else "Helvetica", 10)
            c.drawString(200, row_y - 8, str(value))
        
        y_position -= len(work_info_data) * 25 + 40
        
        # سجلات المركبات (إذا كان هناك مساحة)
        vehicle_handovers = VehicleHandover.query.filter_by(employee_id=employee_id).limit(3).all()
        if vehicle_handovers and y_position > 150:
            c.setFillColor(blue_header)
            c.rect(50, y_position, width - 100, 25, fill=True, stroke=False)
            
            c.setFillColor(HexColor('#FFFFFF'))
            if arabic_font_available:
                c.setFont("Cairo", 12)
                vehicle_title = f"سجلات المركبات (آخر {len(vehicle_handovers)} عمليات)"
            else:
                c.setFont("Helvetica-Bold", 12)
                vehicle_title = f"Vehicle Records (Last {len(vehicle_handovers)} operations)"
            
            text_width = c.stringWidth(vehicle_title, "Cairo" if arabic_font_available else "Helvetica-Bold", 12)
            c.drawString((width - text_width) / 2, y_position + 8, vehicle_title)
            
            y_position -= 35
            
            # عناوين الأعمدة
            headers = ["رقم اللوحة", "نوع العملية", "التاريخ", "المسؤول"] if arabic_font_available else ["Plate", "Type", "Date", "Person"]
            
            for i, header in enumerate(headers):
                c.setFillColor(HexColor('#E7E6E6'))
                c.rect(50 + i * 125, y_position - 20, 125, 25, fill=True, stroke=True)
                c.setFillColor(HexColor('#000000'))
                c.setFont("Cairo" if arabic_font_available else "Helvetica-Bold", 9)
                c.drawString(55 + i * 125, y_position - 8, header)
            
            y_position -= 25
            
            # بيانات المركبات
            for j, handover in enumerate(vehicle_handovers):
                row_data = [
                    handover.vehicle.plate_number if handover.vehicle else "غير محدد",
                    handover.handover_type or "غير محدد",
                    handover.handover_date.strftime('%Y-%m-%d') if handover.handover_date else "غير محدد",
                    handover.person_name or "غير محدد"
                ]
                
                for i, data in enumerate(row_data):
                    if j % 2 == 0:
                        c.setFillColor(HexColor('#F2F2F2'))
                        c.rect(50 + i * 125, y_position - 20, 125, 25, fill=True, stroke=True)
                    else:
                        c.setStrokeColor(HexColor('#000000'))
                        c.rect(50 + i * 125, y_position - 20, 125, 25, fill=False, stroke=True)
                    
                    c.setFillColor(HexColor('#000000'))
                    c.setFont("Cairo" if arabic_font_available else "Helvetica", 8)
                    c.drawString(55 + i * 125, y_position - 8, str(data)[:15])
                
                y_position -= 25
        
        # تذييل الصفحة
        c.setFont("Helvetica", 8)
        c.setFillColor(HexColor('#666666'))
        footer_text = f"تم الإنشاء: {employee.created_at.strftime('%Y-%m-%d %H:%M') if employee.created_at else 'غير معروف'}"
        if not arabic_font_available:
            footer_text = f"Generated: {employee.created_at.strftime('%Y-%m-%d %H:%M') if employee.created_at else 'Unknown'}"
        
        c.drawString(50, 30, footer_text)
        c.drawString(width - 150, 30, "نظام نُظم - Nuzum System")
        
        c.save()
        buffer.seek(0)
        return buffer.getvalue(), None
        
    except Exception as e:
        print(f"خطأ في إنشاء التقرير المصمم: {str(e)}")
        return None, str(e)