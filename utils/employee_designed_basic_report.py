"""
تقرير المعلومات الأساسية للموظف بالتصميم المطلوب
"""
import os
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
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

def generate_designed_basic_report(employee_id):
    """إنشاء تقرير أساسي للموظف بالتصميم المطلوب"""
    try:
        # استيراد داخلي لتجنب المشاكل الدائرية
        from flask import current_app
        with current_app.app_context():
            from sqlalchemy import text
            from app import db
            
            print(f"بدء إنشاء التقرير المصمم للموظف {employee_id}")
            
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
                rightMargin=1.5*cm,
                leftMargin=1.5*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
            
            # قائمة العناصر للPDF
            story = []
            
            # عنوان التقرير الرئيسي
            title_style = ParagraphStyle(
                'Title',
                fontName='Arabic' if has_arabic_font else 'Helvetica-Bold',
                fontSize=18,
                alignment=TA_CENTER,
                spaceAfter=30,
                textColor=colors.black
            )
            
            title_text = "تقرير المعلومات الأساسية للموظف"
            if has_arabic_font:
                title_text = reshape_arabic_text(title_text)
            
            story.append(Paragraph(title_text, title_style))
            
            # قسم الصور الثلاث في الأعلى
            static_path = os.path.join(os.getcwd(), 'static')
            
            # تحديد مسارات الصور
            profile_image_path = None
            national_id_image_path = None
            license_image_path = None
            
            # الصورة الشخصية
            profile_image = employee.get('profile_image')
            if profile_image:
                if profile_image.startswith('uploads/'):
                    profile_image_path = os.path.join(static_path, profile_image)
                else:
                    profile_image_path = os.path.join(static_path, 'uploads', 'employees', profile_image)
            
            # صورة الهوية
            national_id_image = employee.get('national_id_image')
            if national_id_image:
                if national_id_image.startswith('uploads/'):
                    national_id_image_path = os.path.join(static_path, national_id_image)
                else:
                    national_id_image_path = os.path.join(static_path, 'uploads', 'employees', national_id_image)
            
            # صورة الرخصة
            license_image = employee.get('license_image')
            if license_image:
                if license_image.startswith('uploads/'):
                    license_image_path = os.path.join(static_path, license_image)
                else:
                    license_image_path = os.path.join(static_path, 'uploads', 'employees', license_image)
            
            # إنشاء جدول الصور الثلاث
            images_data = []
            image_titles = []
            image_objects = []
            
            # عناوين الصور
            if has_arabic_font:
                image_titles = [
                    reshape_arabic_text("الصورة الشخصية"),
                    reshape_arabic_text("صورة الهوية الوطنية"),
                    reshape_arabic_text("صورة رخصة القيادة")
                ]
            else:
                image_titles = ["Personal Photo", "National ID Photo", "Driving License Photo"]
            
            # إضافة الصور
            for i, (path, title) in enumerate(zip([profile_image_path, national_id_image_path, license_image_path], image_titles)):
                if path and os.path.exists(path):
                    try:
                        img = Image(path, width=4*cm, height=5*cm)
                        image_objects.append(img)
                    except Exception as e:
                        print(f"Error loading image {i+1}: {e}")
                        # إضافة مربع فارغ
                        empty_text = "لا توجد صورة" if has_arabic_font else "No Image"
                        if has_arabic_font:
                            empty_text = reshape_arabic_text(empty_text)
                        image_objects.append(Paragraph(empty_text, ParagraphStyle('Empty', fontSize=8, alignment=TA_CENTER)))
                else:
                    # إضافة مربع فارغ
                    empty_text = "لا توجد صورة" if has_arabic_font else "No Image"
                    if has_arabic_font:
                        empty_text = reshape_arabic_text(empty_text)
                    image_objects.append(Paragraph(empty_text, ParagraphStyle('Empty', fontSize=8, alignment=TA_CENTER)))
            
            # جدول الصور مع العناوين
            images_table_data = [
                image_titles,
                image_objects
            ]
            
            images_table = Table(images_table_data, colWidths=[5*cm, 5*cm, 5*cm])
            images_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, 0), 'Arabic' if has_arabic_font else 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                ('TOPPADDING', (0, 1), (-1, 1), 10),
                ('BOX', (0, 0), (-1, -1), 1, colors.lightgrey),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey)
            ]))
            
            story.append(images_table)
            story.append(Spacer(1, 30))
            
            # قسم المعلومات الأساسية
            section_style = ParagraphStyle(
                'SectionHeader',
                fontName='Arabic' if has_arabic_font else 'Helvetica-Bold',
                fontSize=14,
                alignment=TA_CENTER,
                textColor=colors.white,
                spaceAfter=10
            )
            
            basic_info_title = "المعلومات الأساسية"
            if has_arabic_font:
                basic_info_title = reshape_arabic_text(basic_info_title)
            else:
                basic_info_title = "Basic Information"
            
            # إنشاء جدول عنوان القسم
            header_table = Table([[basic_info_title]], colWidths=[15*cm])
            header_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.Color(0.2, 0.4, 0.6)),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Arabic' if has_arabic_font else 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 14),
                ('PADDING', (0, 0), (-1, -1), 8)
            ]))
            
            story.append(header_table)
            
            # جدول المعلومات الأساسية
            basic_data = []
            
            def format_field(label, value):
                if has_arabic_font:
                    formatted_label = reshape_arabic_text(label)
                    formatted_value = reshape_arabic_text(str(value) if value else 'غير محدد')
                else:
                    label_mapping = {
                        'اسم الموظف': 'Employee Name',
                        'رقم الهوية الوطنية': 'National ID',
                        'رقم الهاتف': 'Phone Number',
                        'الجوال': 'Mobile',
                        'البريد الإلكتروني': 'Email',
                        'الجنسية': 'Nationality'
                    }
                    formatted_label = label_mapping.get(label, label)
                    formatted_value = str(value) if value else 'Not specified'
                
                return [formatted_label, formatted_value]
            
            basic_data.append(format_field('اسم الموظف', employee.get('name')))
            basic_data.append(format_field('رقم الهوية الوطنية', employee.get('national_id')))
            basic_data.append(format_field('رقم الهاتف', employee.get('mobile')))
            basic_data.append(format_field('الجوال', employee.get('mobile')))
            basic_data.append(format_field('البريد الإلكتروني', employee.get('email')))
            basic_data.append(format_field('الجنسية', employee.get('nationality')))
            
            basic_table = Table(basic_data, colWidths=[7*cm, 8*cm])
            basic_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT' if has_arabic_font else 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Arabic' if has_arabic_font else 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.lightgrey]),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('PADDING', (0, 0), (-1, -1), 8)
            ]))
            
            story.append(basic_table)
            story.append(Spacer(1, 20))
            
            # قسم معلومات العمل
            work_info_title = "معلومات العمل"
            if has_arabic_font:
                work_info_title = reshape_arabic_text(work_info_title)
            else:
                work_info_title = "Work Information"
            
            work_header_table = Table([[work_info_title]], colWidths=[15*cm])
            work_header_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.Color(0.2, 0.4, 0.6)),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Arabic' if has_arabic_font else 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 14),
                ('PADDING', (0, 0), (-1, -1), 8)
            ]))
            
            story.append(work_header_table)
            
            # جدول معلومات العمل
            work_data = []
            
            def format_work_field(label, value):
                if has_arabic_font:
                    formatted_label = reshape_arabic_text(label)
                    formatted_value = reshape_arabic_text(str(value) if value else 'غير محدد')
                else:
                    label_mapping = {
                        'الوظيفة الحالية': 'Current Position',
                        'القسم': 'Department',
                        'رقم الموظف': 'Employee Number',
                        'التخصص': 'Specialization',
                        'تاريخ التعيين': 'Appointment Date',
                        'الراتب': 'Salary',
                        'أيام الإجازة المتبقية': 'Remaining Leave Days'
                    }
                    formatted_label = label_mapping.get(label, label)
                    formatted_value = str(value) if value else 'Not specified'
                
                return [formatted_label, formatted_value]
            
            work_data.append(format_work_field('الوظيفة الحالية', employee.get('job_title')))
            work_data.append(format_work_field('القسم', employee.get('department_name')))
            work_data.append(format_work_field('رقم الموظف', employee.get('employee_id')))
            work_data.append(format_work_field('التخصص', employee.get('job_title')))
            
            join_date = employee.get('join_date')
            join_date_str = join_date.strftime('%Y/%m/%d') if join_date else 'غير محدد'
            work_data.append(format_work_field('تاريخ التعيين', join_date_str))
            
            basic_salary = employee.get('basic_salary')
            salary_str = f"{basic_salary:,.0f} ريال" if basic_salary else 'غير محدد'
            work_data.append(format_work_field('الراتب', salary_str))
            
            work_data.append(format_work_field('أيام الإجازة المتبقية', 'غير محدد'))
            
            work_table = Table(work_data, colWidths=[7*cm, 8*cm])
            work_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT' if has_arabic_font else 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Arabic' if has_arabic_font else 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.lightgrey]),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('PADDING', (0, 0), (-1, -1), 8)
            ]))
            
            story.append(work_table)
            story.append(Spacer(1, 30))
            
            # قسم سجلات أداء الموظف - جدول فارغ
            performance_title = "سجلات أداء الموظف (آخر 10 سجلات)"
            if has_arabic_font:
                performance_title = reshape_arabic_text(performance_title)
            else:
                performance_title = "Employee Performance Records (Last 10 Records)"
            
            performance_header_table = Table([[performance_title]], colWidths=[15*cm])
            performance_header_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.Color(0.2, 0.4, 0.6)),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Arabic' if has_arabic_font else 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 14),
                ('PADDING', (0, 0), (-1, -1), 8)
            ]))
            
            story.append(performance_header_table)
            
            # جدول الأداء الفارغ
            if has_arabic_font:
                performance_headers = [
                    reshape_arabic_text("ملاحظات"),
                    reshape_arabic_text("نوع السجل"),
                    reshape_arabic_text("التاريخ"),
                    reshape_arabic_text("رقم السجل")
                ]
            else:
                performance_headers = ["Notes", "Record Type", "Date", "Record Number"]
            
            performance_data = [performance_headers]
            # إضافة صف فارغ
            empty_row_text = "لا توجد سجلات" if has_arabic_font else "No records"
            if has_arabic_font:
                empty_row_text = reshape_arabic_text(empty_row_text)
            performance_data.append([empty_row_text, "", "", ""])
            
            performance_table = Table(performance_data, colWidths=[4*cm, 3*cm, 3*cm, 2*cm])
            performance_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.Color(0.2, 0.4, 0.6)),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Arabic' if has_arabic_font else 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('PADDING', (0, 0), (-1, -1), 6),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white)
            ]))
            
            story.append(performance_table)
            story.append(Spacer(1, 20))
            
            # قسم الراتب الحالي
            salary_title = "الراتب الحالي"
            if has_arabic_font:
                salary_title = reshape_arabic_text(salary_title)
            else:
                salary_title = "Current Salary"
            
            salary_header_table = Table([[salary_title]], colWidths=[15*cm])
            salary_header_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), colors.Color(0.2, 0.4, 0.6)),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, -1), 'Arabic' if has_arabic_font else 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 14),
                ('PADDING', (0, 0), (-1, -1), 8)
            ]))
            
            story.append(salary_header_table)
            
            # جدول الراتب
            basic_salary = employee.get('basic_salary', 0)
            salary_amount = f"{basic_salary:,.0f}" if basic_salary else "غير محدد"
            
            if has_arabic_font:
                salary_data = [
                    [reshape_arabic_text("إجمالي الراتب"), reshape_arabic_text(salary_amount)]
                ]
            else:
                salary_data = [["Total Salary", str(salary_amount)]]
            
            salary_table = Table(salary_data, colWidths=[7*cm, 8*cm])
            salary_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'RIGHT' if has_arabic_font else 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Arabic' if has_arabic_font else 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('BOX', (0, 0), (-1, -1), 1, colors.black),
                ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.black),
                ('PADDING', (0, 0), (-1, -1), 8),
                ('BACKGROUND', (0, 0), (-1, -1), colors.white)
            ]))
            
            story.append(salary_table)
            
            # بناء PDF
            doc.build(story)
            
            # إرجاع البيانات
            pdf_data = buffer.getvalue()
            buffer.close()
            
            print("تم إنتاج التقرير المصمم بنجاح")
            return pdf_data, None
            
    except Exception as e:
        import traceback
        error_msg = f"خطأ في إنتاج التقرير المصمم: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        return None, error_msg