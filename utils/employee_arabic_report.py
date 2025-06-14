"""
تقرير الموظف باللغة العربية مع الصور والمعلومات الأساسية
"""
import os
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PIL import Image
from models import Employee, VehicleHandover


def generate_arabic_employee_report(employee_id):
    """إنشاء تقرير الموظف باللغة العربية مع الصور"""
    try:
        # البحث عن الموظف
        employee = Employee.query.get(employee_id)
        if not employee:
            return None, "الموظف غير موجود"
        
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        
        # محاولة تحميل الخط العربي
        arabic_font_available = False
        try:
            font_path = os.path.join(os.path.dirname(__file__), '..', 'Cairo.ttf')
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('Cairo', font_path))
                arabic_font_available = True
        except:
            pass
        
        # إعداد الخط
        if arabic_font_available:
            c.setFont("Cairo", 16)
        else:
            c.setFont("Helvetica-Bold", 16)
        
        # عنوان التقرير
        title = "تقرير معلومات الموظف - نظام نُظم" if arabic_font_available else "Employee Report - Nuzum System"
        text_width = c.stringWidth(title, "Cairo" if arabic_font_available else "Helvetica-Bold", 16)
        c.drawString((width - text_width) / 2, height - 50, title)
        
        # خط فاصل
        c.line(50, height - 70, width - 50, height - 70)
        
        y_position = height - 100
        
        # دالة آمنة لعرض النص
        def safe_text(text, arabic_label="", english_label=""):
            if not text:
                return "غير محدد" if arabic_font_available else "Not specified"
            return str(text)
        
        # دالة لإضافة صف معلومات
        def add_info_row(arabic_label, english_label, value, y_pos):
            if arabic_font_available:
                c.setFont("Cairo", 12)
                label = arabic_label
            else:
                c.setFont("Helvetica-Bold", 12)
                label = english_label
            
            c.drawString(50, y_pos, f"{label}: {safe_text(value)}")
            return y_pos - 25
        
        # دالة لإضافة عنوان قسم
        def add_section_title(arabic_title, english_title, y_pos):
            if arabic_font_available:
                c.setFont("Cairo", 14)
                title = arabic_title
            else:
                c.setFont("Helvetica-Bold", 14)
                title = english_title
            
            c.drawString(50, y_pos, title)
            return y_pos - 30
        
        # المعلومات الأساسية
        y_position = add_section_title("المعلومات الأساسية", "Basic Information", y_position)
        
        y_position = add_info_row("الاسم", "Name", employee.name, y_position)
        y_position = add_info_row("رقم الموظف", "Employee ID", employee.employee_id, y_position)
        y_position = add_info_row("الجوال", "Mobile", employee.mobile, y_position)
        y_position = add_info_row("البريد الإلكتروني", "Email", employee.email, y_position)
        y_position = add_info_row("رقم الهوية الوطنية", "National ID", employee.national_id, y_position)
        y_position = add_info_row("المسمى الوظيفي", "Job Title", employee.job_title, y_position)
        y_position = add_info_row("القسم", "Department", 
                                 employee.department.name if employee.department else None, y_position)
        y_position = add_info_row("الحالة", "Status", employee.status, y_position)
        y_position = add_info_row("تاريخ الانضمام", "Join Date", 
                                 employee.join_date.strftime('%Y-%m-%d') if employee.join_date else None, y_position)
        y_position = add_info_row("الراتب الأساسي", "Basic Salary", 
                                 f"{employee.basic_salary:,.2f} ريال" if employee.basic_salary else None, y_position)
        
        # معلومات إضافية
        y_position -= 20
        y_position = add_section_title("معلومات إضافية", "Additional Information", y_position)
        
        y_position = add_info_row("نوع العقد", "Contract Type", employee.contract_type, y_position)
        y_position = add_info_row("الموقع", "Location", employee.location, y_position)
        y_position = add_info_row("المشروع", "Project", employee.project, y_position)
        y_position = add_info_row("الرصيد الوطني", "National Balance", 
                                 "نعم" if employee.has_national_balance else "لا", y_position)
        
        # إضافة الصور إذا كانت متوفرة
        image_y_start = y_position - 50
        image_x_positions = [50, 200, 350]  # مواضع الصور على المحور السيني
        
        images_info = [
            (employee.profile_image, "الصورة الشخصية", "Profile Photo"),
            (employee.national_id_image, "صورة الهوية الوطنية", "National ID"),
            (employee.license_image, "صورة رخصة القيادة", "License Photo")
        ]
        
        # دالة لإضافة صورة
        def add_image(image_path, title_ar, title_en, x_pos, y_pos):
            if image_path and os.path.exists(f"static/{image_path}"):
                try:
                    # إضافة عنوان الصورة
                    if arabic_font_available:
                        c.setFont("Cairo", 10)
                        c.drawString(x_pos, y_pos + 10, title_ar)
                    else:
                        c.setFont("Helvetica", 10)
                        c.drawString(x_pos, y_pos + 10, title_en)
                    
                    # إضافة الصورة
                    c.drawImage(f"static/{image_path}", x_pos, y_pos - 80, width=120, height=80, preserveAspectRatio=True)
                    return True
                except Exception as e:
                    print(f"خطأ في إضافة الصورة {image_path}: {e}")
            return False
        
        # إضافة الصور
        for i, (image_path, title_ar, title_en) in enumerate(images_info):
            if i < len(image_x_positions):
                add_image(image_path, title_ar, title_en, image_x_positions[i], image_y_start)
        
        # سجلات المركبات
        vehicle_handovers = VehicleHandover.query.filter_by(employee_id=employee_id).all()
        if vehicle_handovers:
            y_position = image_y_start - 120
            y_position = add_section_title("سجلات المركبات", "Vehicle Records", y_position)
            
            for handover in vehicle_handovers:
                if y_position < 100:  # صفحة جديدة إذا اقترب من النهاية
                    c.showPage()
                    y_position = height - 50
                
                vehicle_info = f"اللوحة: {handover.vehicle.plate_number if handover.vehicle else 'غير محدد'}"
                vehicle_info += f" | النوع: {handover.handover_type}"
                vehicle_info += f" | التاريخ: {handover.handover_date.strftime('%Y-%m-%d')}"
                vehicle_info += f" | الشخص: {handover.person_name}"
                if handover.mileage:
                    vehicle_info += f" | المسافة: {handover.mileage} كم"
                
                if not arabic_font_available:
                    vehicle_info = f"Plate: {handover.vehicle.plate_number if handover.vehicle else 'N/A'}"
                    vehicle_info += f" | Type: {handover.handover_type}"
                    vehicle_info += f" | Date: {handover.handover_date.strftime('%Y-%m-%d')}"
                    vehicle_info += f" | Person: {handover.person_name}"
                    if handover.mileage:
                        vehicle_info += f" | Mileage: {handover.mileage} km"
                
                c.setFont("Cairo" if arabic_font_available else "Helvetica", 10)
                c.drawString(50, y_position, vehicle_info)
                y_position -= 20
        
        # تذييل الصفحة
        c.setFont("Helvetica", 8)
        footer_text = f"تم الإنشاء: {employee.created_at.strftime('%Y-%m-%d %H:%M') if employee.created_at else 'غير معروف'}"
        if not arabic_font_available:
            footer_text = f"Generated: {employee.created_at.strftime('%Y-%m-%d %H:%M') if employee.created_at else 'Unknown'}"
        
        c.drawString(50, 30, footer_text)
        c.drawString(width - 150, 30, "نظام نُظم - Nuzum System")
        
        c.save()
        buffer.seek(0)
        return buffer.getvalue(), None
        
    except Exception as e:
        print(f"خطأ في إنشاء التقرير العربي: {str(e)}")
        return None, str(e)