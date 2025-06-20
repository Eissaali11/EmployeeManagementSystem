"""
تقرير المعلومات الأساسية للموظف باللغة العربية مع الصور
"""
import os
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import arabic_reshaper
from bidi.algorithm import get_display
from datetime import datetime

def setup_arabic_font():
    """إعداد الخط العربي"""
    try:
        # محاولة تسجيل الخط العربي
        font_path = os.path.join(os.getcwd(), 'fonts', 'NotoSansArabic-Regular.ttf')
        if not os.path.exists(font_path):
            # إذا لم يوجد الخط، استخدم خط بديل
            font_path = os.path.join(os.getcwd(), 'Cairo.ttf')
        
        if os.path.exists(font_path):
            pdfmetrics.registerFont(TTFont('Arabic', font_path))
            return True
        else:
            print("Arabic font not found, using default font")
            return False
    except Exception as e:
        print(f"Error setting up Arabic font: {e}")
        return False

def reshape_arabic_text(text):
    """إعادة تشكيل النص العربي"""
    try:
        if text and any('\u0600' <= char <= '\u06FF' for char in str(text)):
            reshaped_text = arabic_reshaper.reshape(str(text))
            return get_display(reshaped_text)
        return str(text) if text else ""
    except Exception as e:
        print(f"Error reshaping Arabic text: {e}")
        return str(text) if text else ""

def generate_arabic_basic_report(employee_id):
    """إنشاء تقرير أساسي للموظف باللغة العربية"""
    try:
        # استيراد داخلي لتجنب المشاكل الدائرية
        from flask import current_app
        with current_app.app_context():
            from sqlalchemy import text
            from app import db
            
            print(f"بدء إنشاء التقرير العربي للموظف {employee_id}")
            
            # البحث عن الموظف
            employee_query = text("""
                SELECT e.*, d.name as department_name 
                FROM employee e 
                LEFT JOIN department d ON e.department_id = d.id 
                WHERE e.id = :employee_id
            """)
            
            result = db.session.execute(employee_query, {'employee_id': employee_id}).fetchone()
            if not result:
                print(f"لم يتم العثور على الموظف {employee_id}")
                return None, "Employee not found"
            
            # تحويل النتيجة إلى dict
            employee = dict(result._mapping) if hasattr(result, '_mapping') else dict(zip(result.keys(), result))
            print(f"تم العثور على الموظف: {employee.get('name', 'غير معروف')}")
            
            # إعداد الخط العربي
            has_arabic_font = setup_arabic_font()
            
            # إنشاء buffer للPDF
            buffer = BytesIO()
            
            # إنشاء PDF
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
            
            # قائمة العناصر للPDF
            story = []
            
            # إعداد الأنماط
            if has_arabic_font:
                title_style = ParagraphStyle(
                    'ArabicTitle',
                    fontName='Arabic',
                    fontSize=20,
                    alignment=TA_CENTER,
                    textColor=colors.blue,
                    spaceAfter=20
                )
                
                header_style = ParagraphStyle(
                    'ArabicHeader',
                    fontName='Arabic',
                    fontSize=14,
                    alignment=TA_RIGHT,
                    textColor=colors.blue,
                    spaceAfter=10,
                    spaceBefore=15
                )
                
                normal_style = ParagraphStyle(
                    'ArabicNormal',
                    fontName='Arabic',
                    fontSize=11,
                    alignment=TA_RIGHT,
                    spaceAfter=5
                )
            else:
                # استخدام الأنماط الافتراضية
                styles = getSampleStyleSheet()
                title_style = styles['Title']
                header_style = styles['Heading2']
                normal_style = styles['Normal']
            
            # عنوان التقرير
            title_text = "نظام نُظم - تقرير المعلومات الأساسية للموظف"
            if has_arabic_font:
                title_text = reshape_arabic_text(title_text)
            story.append(Paragraph(title_text, title_style))
            story.append(Spacer(1, 20))
            
            # اسم الموظف
            employee_name = employee.get('name', 'غير محدد')
            if has_arabic_font:
                employee_name = reshape_arabic_text(f"تقرير الموظف: {employee_name}")
            else:
                employee_name = f"Employee Report: {employee_name}"
            story.append(Paragraph(employee_name, header_style))
            story.append(Spacer(1, 15))
            
            # المعلومات الأساسية
            basic_info_title = "المعلومات الشخصية الأساسية"
            if has_arabic_font:
                basic_info_title = reshape_arabic_text(basic_info_title)
            else:
                basic_info_title = "Basic Personal Information"
            story.append(Paragraph(basic_info_title, header_style))
            
            # جدول المعلومات الأساسية
            basic_data = []
            
            def add_info_row(label, value):
                if has_arabic_font:
                    label = reshape_arabic_text(label)
                    value = reshape_arabic_text(str(value) if value else 'غير محدد')
                else:
                    # تحويل العربي للإنجليزي
                    label_mapping = {
                        'اسم الموظف': 'Employee Name',
                        'رقم الموظف': 'Employee ID',
                        'رقم الهوية الوطنية': 'National ID',
                        'رقم الهاتف المحمول': 'Mobile Phone',
                        'البريد الإلكتروني': 'Email Address',
                        'الجنسية': 'Nationality',
                        'نوع العقد': 'Contract Type'
                    }
                    label = label_mapping.get(label, label)
                    value = str(value) if value else 'Not specified'
                
                return [label, value]
            
            basic_data.append(add_info_row('اسم الموظف', employee.get('name')))
            basic_data.append(add_info_row('رقم الموظف', employee.get('employee_id')))
            basic_data.append(add_info_row('رقم الهوية الوطنية', employee.get('national_id')))
            basic_data.append(add_info_row('رقم الهاتف المحمول', employee.get('mobile')))
            basic_data.append(add_info_row('البريد الإلكتروني', employee.get('email')))
            basic_data.append(add_info_row('الجنسية', employee.get('nationality')))
            
            contract_type = employee.get('contract_type', '')
            contract_display = 'سعودي' if contract_type == 'saudi' else 'وافد' if contract_type == 'foreign' else 'غير محدد'
            basic_data.append(add_info_row('نوع العقد', contract_display))
            
            # إنشاء جدول المعلومات الأساسية
            basic_table = Table(basic_data, colWidths=[5*cm, 10*cm])
            basic_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT' if has_arabic_font else 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Arabic' if has_arabic_font else 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(basic_table)
            story.append(Spacer(1, 20))
            
            # معلومات العمل
            work_info_title = "معلومات العمل"
            if has_arabic_font:
                work_info_title = reshape_arabic_text(work_info_title)
            else:
                work_info_title = "Work Information"
            story.append(Paragraph(work_info_title, header_style))
            
            # جدول معلومات العمل
            work_data = []
            
            def add_work_info_row(label, value):
                if has_arabic_font:
                    label = reshape_arabic_text(label)
                    value = reshape_arabic_text(str(value) if value else 'غير محدد')
                else:
                    label_mapping = {
                        'المسمى الوظيفي': 'Job Title',
                        'القسم': 'Department',
                        'حالة التوظيف': 'Employment Status',
                        'تاريخ الانضمام': 'Join Date',
                        'الموقع': 'Location',
                        'المشروع': 'Project',
                        'الراتب الأساسي': 'Basic Salary'
                    }
                    label = label_mapping.get(label, label)
                    value = str(value) if value else 'Not specified'
                
                return [label, value]
            
            work_data.append(add_work_info_row('المسمى الوظيفي', employee.get('job_title')))
            work_data.append(add_work_info_row('القسم', employee.get('department_name')))
            
            status = employee.get('status', 'unknown')
            status_display = 'نشط' if status == 'active' else 'غير نشط' if status == 'inactive' else 'في إجازة' if status == 'on_leave' else 'غير محدد'
            work_data.append(add_work_info_row('حالة التوظيف', status_display))
            
            join_date = employee.get('join_date')
            join_date_str = join_date.strftime('%Y-%m-%d') if join_date else 'غير محدد'
            work_data.append(add_work_info_row('تاريخ الانضمام', join_date_str))
            
            work_data.append(add_work_info_row('الموقع', employee.get('location')))
            work_data.append(add_work_info_row('المشروع', employee.get('project')))
            
            basic_salary = employee.get('basic_salary')
            salary_str = f"{basic_salary:,.0f} ريال سعودي" if basic_salary else 'غير محدد'
            work_data.append(add_work_info_row('الراتب الأساسي', salary_str))
            
            # إنشاء جدول معلومات العمل
            work_table = Table(work_data, colWidths=[5*cm, 10*cm])
            work_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgreen),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT' if has_arabic_font else 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Arabic' if has_arabic_font else 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(work_table)
            story.append(Spacer(1, 20))
            
            # قسم الصور
            images_title = "وثائق وصور الموظف"
            if has_arabic_font:
                images_title = reshape_arabic_text(images_title)
            else:
                images_title = "Employee Documents and Photos"
            story.append(Paragraph(images_title, header_style))
            
            # تحديد مسارات الصور
            static_path = os.path.join(os.getcwd(), 'static')
            images_data = []
            
            # الصورة الشخصية
            profile_image = employee.get('profile_image')
            if profile_image:
                if profile_image.startswith('uploads/'):
                    profile_path = os.path.join(static_path, profile_image)
                else:
                    profile_path = os.path.join(static_path, 'uploads', 'employees', profile_image)
                
                if os.path.exists(profile_path):
                    try:
                        img = Image(profile_path, width=4*cm, height=5*cm)
                        if has_arabic_font:
                            label = reshape_arabic_text("الصورة الشخصية")
                        else:
                            label = "Profile Photo"
                        images_data.append([label, img])
                    except Exception as e:
                        print(f"Error loading profile image: {e}")
            
            # صورة الهوية
            national_id_image = employee.get('national_id_image')
            if national_id_image:
                if national_id_image.startswith('uploads/'):
                    id_path = os.path.join(static_path, national_id_image)
                else:
                    id_path = os.path.join(static_path, 'uploads', 'employees', national_id_image)
                
                if os.path.exists(id_path):
                    try:
                        img = Image(id_path, width=4*cm, height=5*cm)
                        if has_arabic_font:
                            label = reshape_arabic_text("صورة الهوية الوطنية")
                        else:
                            label = "National ID Photo"
                        images_data.append([label, img])
                    except Exception as e:
                        print(f"Error loading national ID image: {e}")
            
            # صورة الرخصة
            license_image = employee.get('license_image')
            if license_image:
                if license_image.startswith('uploads/'):
                    license_path = os.path.join(static_path, license_image)
                else:
                    license_path = os.path.join(static_path, 'uploads', 'employees', license_image)
                
                if os.path.exists(license_path):
                    try:
                        img = Image(license_path, width=4*cm, height=5*cm)
                        if has_arabic_font:
                            label = reshape_arabic_text("صورة رخصة القيادة")
                        else:
                            label = "Driving License Photo"
                        images_data.append([label, img])
                    except Exception as e:
                        print(f"Error loading license image: {e}")
            
            # إضافة جدول الصور إذا وجدت
            if images_data:
                images_table = Table(images_data, colWidths=[5*cm, 6*cm])
                images_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('FONTNAME', (0, 0), (0, -1), 'Arabic' if has_arabic_font else 'Helvetica'),
                    ('FONTSIZE', (0, 0), (0, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('BACKGROUND', (0, 0), (0, -1), colors.lightcyan)
                ]))
                story.append(images_table)
            else:
                no_images_text = "لا توجد صور متاحة"
                if has_arabic_font:
                    no_images_text = reshape_arabic_text(no_images_text)
                else:
                    no_images_text = "No images available"
                story.append(Paragraph(no_images_text, normal_style))
            
            story.append(Spacer(1, 20))
            
            # تاريخ إنتاج التقرير
            generation_date = datetime.now().strftime('%Y-%m-%d %H:%M')
            date_text = f"تم إنتاج هذا التقرير في: {generation_date}"
            if has_arabic_font:
                date_text = reshape_arabic_text(date_text)
            else:
                date_text = f"Report generated on: {generation_date}"
            
            date_style = ParagraphStyle(
                'DateStyle',
                fontName='Arabic' if has_arabic_font else 'Helvetica',
                fontSize=9,
                alignment=TA_CENTER,
                textColor=colors.grey
            )
            story.append(Paragraph(date_text, date_style))
            
            # بناء PDF
            doc.build(story)
            
            # إرجاع البيانات
            pdf_data = buffer.getvalue()
            buffer.close()
            
            print("تم إنتاج التقرير العربي بنجاح")
            return pdf_data, None
            
    except Exception as e:
        import traceback
        error_msg = f"خطأ في إنتاج التقرير العربي: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        return None, error_msg