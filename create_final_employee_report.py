"""
إنشاء تقرير الموظف النهائي بالتصميم المطلوب
"""
import os
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
import sys

def create_employee_report_with_design(employee_data):
    """إنشاء تقرير الموظف بالتصميم المطلوب"""
    try:
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
        title = "تقرير المعلومات الأساسية للموظف"
        text_width = c.stringWidth(title, "Helvetica-Bold", 16)
        c.drawString((width - text_width) / 2, height - 55, title)
        
        y_position = height - 90
        
        # الصورة الشخصية
        c.setFillColor(HexColor('#000000'))
        c.setFont("Helvetica-Bold", 12)
        image_title = "الصورة الشخصية"
        text_width = c.stringWidth(image_title, "Helvetica-Bold", 12)
        c.drawString((width - text_width) / 2, y_position, image_title)
        
        # إطار الصورة الشخصية (دائري)
        image_x = width / 2 - 60
        image_y = y_position - 140
        
        c.setStrokeColor(blue_header)
        c.setLineWidth(3)
        c.circle(image_x + 60, image_y + 60, 55)
        
        # النص داخل الدائرة
        c.setFont("Helvetica", 10)
        c.drawString(image_x + 20, image_y + 55, "صورة شخصية")
        
        y_position = image_y - 40
        
        # صورة الهوية الوطنية
        c.setFillColor(HexColor('#000000'))
        c.setFont("Helvetica-Bold", 12)
        id_title = "صورة الهوية الوطنية"
        text_width = c.stringWidth(id_title, "Helvetica-Bold", 12)
        c.drawString((width - text_width) / 2, y_position, id_title)
        
        # إطار صورة الهوية (مستطيل أخضر)
        id_image_x = width / 2 - 100
        id_image_y = y_position - 100
        
        c.setStrokeColor(green_border)
        c.setLineWidth(3)
        c.rect(id_image_x, id_image_y, 200, 80)
        
        c.setFont("Helvetica", 10)
        c.drawString(id_image_x + 70, id_image_y + 35, "صورة الهوية الوطنية")
        
        y_position = id_image_y - 40
        
        # صورة رخصة القيادة
        c.setFillColor(HexColor('#000000'))
        c.setFont("Helvetica-Bold", 12)
        license_title = "صورة رخصة القيادة"
        text_width = c.stringWidth(license_title, "Helvetica-Bold", 12)
        c.drawString((width - text_width) / 2, y_position, license_title)
        
        # إطار صورة الرخصة (مستطيل أخضر)
        license_image_x = width / 2 - 100
        license_image_y = y_position - 100
        
        c.setStrokeColor(green_border)
        c.setLineWidth(3)
        c.rect(license_image_x, license_image_y, 200, 80)
        
        c.setFont("Helvetica", 10)
        c.drawString(license_image_x + 60, license_image_y + 35, "صورة رخصة القيادة")
        
        y_position = license_image_y - 60
        
        # جدول المعلومات الأساسية
        c.setFillColor(blue_header)
        c.rect(50, y_position, width - 100, 25, fill=True, stroke=False)
        
        c.setFillColor(HexColor('#FFFFFF'))
        c.setFont("Helvetica-Bold", 12)
        basic_info_title = "المعلومات الأساسية"
        text_width = c.stringWidth(basic_info_title, "Helvetica-Bold", 12)
        c.drawString((width - text_width) / 2, y_position + 8, basic_info_title)
        
        y_position -= 35
        
        # بيانات المعلومات الأساسية
        basic_info_data = [
            ["الاسم", employee_data.get('name', 'غير محدد')],
            ["رقم الموظف", employee_data.get('employee_id', 'غير محدد')],
            ["الجوال", employee_data.get('mobile', 'غير محدد')],
            ["رقم الهوية", employee_data.get('national_id', 'غير محدد')],
            ["المسمى الوظيفي", employee_data.get('job_title', 'غير محدد')],
            ["القسم", employee_data.get('department', 'غير محدد')],
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
            c.drawString(200, row_y - 8, str(value))
        
        y_position -= len(basic_info_data) * 25 + 40
        
        # معلومات العمل
        c.setFillColor(blue_header)
        c.rect(50, y_position, width - 100, 25, fill=True, stroke=False)
        
        c.setFillColor(HexColor('#FFFFFF'))
        c.setFont("Helvetica-Bold", 12)
        work_info_title = "معلومات العمل"
        text_width = c.stringWidth(work_info_title, "Helvetica-Bold", 12)
        c.drawString((width - text_width) / 2, y_position + 8, work_info_title)
        
        y_position -= 35
        
        # بيانات معلومات العمل
        work_info_data = [
            ["تاريخ الانضمام", employee_data.get('join_date', 'غير محدد')],
            ["الراتب الأساسي", employee_data.get('basic_salary', 'غير محدد')],
            ["نوع العقد", employee_data.get('contract_type', 'غير محدد')],
            ["الموقع", employee_data.get('location', 'غير محدد')],
            ["المشروع", employee_data.get('project', 'غير محدد')],
            ["الحالة", employee_data.get('status', 'غير محدد')],
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
            c.drawString(200, row_y - 8, str(value))
        
        y_position -= len(work_info_data) * 25 + 40
        
        # سجلات المركبات
        if employee_data.get('vehicle_records'):
            c.setFillColor(blue_header)
            c.rect(50, y_position, width - 100, 25, fill=True, stroke=False)
            
            c.setFillColor(HexColor('#FFFFFF'))
            c.setFont("Helvetica-Bold", 12)
            vehicle_title = "سجلات المركبات (آخر 3 عمليات)"
            text_width = c.stringWidth(vehicle_title, "Helvetica-Bold", 12)
            c.drawString((width - text_width) / 2, y_position + 8, vehicle_title)
            
            y_position -= 35
            
            # عناوين الأعمدة
            headers = ["رقم اللوحة", "نوع العملية", "التاريخ", "المسؤول"]
            
            for i, header in enumerate(headers):
                c.setFillColor(HexColor('#E7E6E6'))
                c.rect(50 + i * 125, y_position - 20, 125, 25, fill=True, stroke=True)
                c.setFillColor(HexColor('#000000'))
                c.setFont("Helvetica-Bold", 9)
                c.drawString(55 + i * 125, y_position - 8, header)
            
            y_position -= 25
            
            # بيانات المركبات
            for j, record in enumerate(employee_data['vehicle_records'][:3]):
                row_data = [
                    record.get('plate_number', 'غير محدد'),
                    record.get('handover_type', 'غير محدد'),
                    record.get('handover_date', 'غير محدد'),
                    record.get('person_name', 'غير محدد')
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
                    c.drawString(55 + i * 125, y_position - 8, str(data)[:15])
                
                y_position -= 25
        
        # تذييل الصفحة
        c.setFont("Helvetica", 8)
        c.setFillColor(HexColor('#666666'))
        c.drawString(50, 30, "تم الإنشاء: 2025-06-14")
        c.drawString(width - 150, 30, "نظام نُظم - Nuzum System")
        
        c.save()
        buffer.seek(0)
        return buffer.getvalue()
        
    except Exception as e:
        print(f"خطأ في إنشاء التقرير: {str(e)}")
        return None

def main():
    """إنشاء تقرير تجريبي"""
    employee_data = {
        'name': 'أحمد محمد علي',
        'employee_id': '178',
        'mobile': '0501234567',
        'national_id': '1234567890',
        'job_title': 'مطور برمجيات',
        'department': 'تقنية المعلومات',
        'join_date': '2023-01-15',
        'basic_salary': '8000.00 ريال',
        'contract_type': 'دائم',
        'location': 'الرياض',
        'project': 'نظام نُظم',
        'status': 'نشط',
        'vehicle_records': [
            {
                'plate_number': 'أ ب ج 123',
                'handover_type': 'تسليم',
                'handover_date': '2024-01-01',
                'person_name': 'أحمد علي'
            },
            {
                'plate_number': 'د هـ و 456',
                'handover_type': 'استلام',
                'handover_date': '2024-02-01',
                'person_name': 'محمد أحمد'
            }
        ]
    }
    
    pdf_data = create_employee_report_with_design(employee_data)
    
    if pdf_data:
        with open('employee_designed_report_final.pdf', 'wb') as f:
            f.write(pdf_data)
        print("✓ تم إنشاء التقرير بالتصميم المطلوب بنجاح!")
        print(f"حجم الملف: {len(pdf_data)} بايت")
        return True
    else:
        print("✗ فشل في إنشاء التقرير")
        return False

if __name__ == "__main__":
    main()