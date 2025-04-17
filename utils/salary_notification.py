"""
وحدة إنشاء إشعار راتب كملف PDF
"""
from datetime import datetime
from utils.arabic_pdf import reshape_arabic_text, get_arabic_styles, create_rtl_table, create_arabic_pdf
from reportlab.lib import colors
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import cm

def generate_salary_notification_pdf(salary):
    """
    إنشاء إشعار راتب لموظف كملف PDF
    
    Args:
        salary: كائن Salary يحتوي على بيانات الراتب
        
    Returns:
        BytesIO يحتوي على ملف PDF
    """
    try:
        # الحصول على اسم الشهر بالعربية
        month_names = {
            1: 'يناير', 2: 'فبراير', 3: 'مارس', 4: 'أبريل',
            5: 'مايو', 6: 'يونيو', 7: 'يوليو', 8: 'أغسطس',
            9: 'سبتمبر', 10: 'أكتوبر', 11: 'نوفمبر', 12: 'ديسمبر'
        }
        month_name = month_names.get(salary.month, str(salary.month))
        
        # الحصول على أنماط النصوص العربية
        styles = get_arabic_styles()
        
        # بناء محتوى المستند
        elements = []
        
        # العنوان
        elements.append(Paragraph(reshape_arabic_text("إشعار راتب"), styles['title']))
        elements.append(Spacer(1, 20))
        
        # معلومات الموظف
        employee_info = [
            [reshape_arabic_text("بيانات الموظف"), ""],
            [reshape_arabic_text("الاسم:"), reshape_arabic_text(salary.employee.name)],
            [reshape_arabic_text("الرقم الوظيفي:"), reshape_arabic_text(salary.employee.employee_id)]
        ]
        
        # إضافة معلومات القسم إذا كانت متوفرة
        if salary.employee.department:
            employee_info.append([
                reshape_arabic_text("القسم:"), 
                reshape_arabic_text(salary.employee.department.name)
            ])
        
        # إضافة المسمى الوظيفي
        employee_info.append([
            reshape_arabic_text("المسمى الوظيفي:"), 
            reshape_arabic_text(salary.employee.job_title)
        ])
        
        # إنشاء جدول بيانات الموظف
        employee_table = Table(employee_info, colWidths=[4*cm, 10*cm])
        employee_style = TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),
            ('SPAN', (0, 0), (1, 0)),  # دمج خلايا العنوان
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),  # محاذاة العناوين إلى اليمين
            ('ALIGN', (0, 0), (1, 0), 'CENTER'),  # توسيط العنوان
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica'),
            ('FONTSIZE', (0, 0), (1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (1, 0), 8),
            ('GRID', (0, 0), (1, -1), 0.5, colors.grey),
            ('VALIGN', (0, 0), (1, -1), 'MIDDLE'),
        ])
        employee_table.setStyle(employee_style)
        elements.append(employee_table)
        elements.append(Spacer(1, 20))
        
        # معلومات الراتب
        elements.append(Paragraph(reshape_arabic_text(f"تفاصيل راتب شهر: {month_name} {salary.year}"), styles['heading']))
        elements.append(Spacer(1, 10))
        
        # جدول تفاصيل الراتب
        data = [
            [reshape_arabic_text("البند"), reshape_arabic_text("المبلغ")],
            [reshape_arabic_text("الراتب الأساسي"), f"{salary.basic_salary:.2f}"],
            [reshape_arabic_text("البدلات"), f"{salary.allowances:.2f}"],
            [reshape_arabic_text("المكافآت"), f"{salary.bonus:.2f}"],
            [reshape_arabic_text("الخصومات"), f"{salary.deductions:.2f}"],
            [reshape_arabic_text("صافي الراتب"), f"{salary.net_salary:.2f}"]
        ]
        
        # تحديد عرض الأعمدة بوحدات السنتيمتر
        table = Table(data, colWidths=[10*cm, 4*cm])
        
        # تحسين تنسيق الجدول
        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),
            ('TEXTCOLOR', (0, 0), (1, 0), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),  # محاذاة العمود الأول إلى اليمين
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),  # محاذاة العمود الثاني إلى الوسط
            ('FONTNAME', (0, 0), (1, 0), 'Helvetica'),
            ('FONTSIZE', (0, 0), (1, 0), 12),  # حجم خط عناوين الجدول
            ('FONTSIZE', (0, 1), (1, -1), 10),  # حجم خط بيانات الجدول
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, -1), (1, -1), colors.lightgrey),  # لون خلفية صف المجموع
            ('FONTNAME', (0, -1), (1, -1), 'Helvetica'),  # خط أكثر سمكاً لصف المجموع
            ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.black),  # خط أكثر سمكاً تحت العناوين
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # محاذاة رأسية وسط
        ])
        
        # إضافة ألوان متبادلة للصفوف
        for i in range(1, len(data)-1):
            if i % 2 == 0:
                table_style.add('BACKGROUND', (0, i), (1, i), colors.whitesmoke)
        
        table.setStyle(table_style)
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        # ملاحظات
        if salary.notes:
            elements.append(Paragraph(reshape_arabic_text("ملاحظات:"), styles['normal']))
            elements.append(Paragraph(reshape_arabic_text(salary.notes), styles['normal']))
        
        # التوقيع
        elements.append(Spacer(1, 40))
        signature_data = [
            [reshape_arabic_text("توقيع المدير المالي"), "", reshape_arabic_text("توقيع الموظف")],
            ["________________", "", "________________"]
        ]
        signature_table = Table(signature_data, colWidths=[5*cm, 4*cm, 5*cm])
        signature_style = TableStyle([
            ('ALIGN', (0, 0), (2, 1), 'CENTER'),
            ('FONTNAME', (0, 0), (2, 1), 'Helvetica'),
            ('VALIGN', (0, 0), (2, 1), 'MIDDLE'),
            ('FONTSIZE', (0, 1), (2, 1), 10),
        ])
        signature_table.setStyle(signature_style)
        elements.append(signature_table)
        
        # التذييل
        elements.append(Spacer(1, 40))
        
        # إنشاء جدول التذييل
        footer_data = [
            [reshape_arabic_text(f"تم إصدار هذا الإشعار في {datetime.now().strftime('%Y-%m-%d')}")],
            [reshape_arabic_text("نظام إدارة الموظفين - جميع الحقوق محفوظة")]
        ]
        
        footer_table = Table(footer_data, colWidths=[14*cm])
        footer_style = TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (0, -1), 8),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.gray),
            ('BOTTOMPADDING', (0, 0), (0, -1), 5),
        ])
        
        footer_table.setStyle(footer_style)
        elements.append(footer_table)
        
        # إنشاء ملف PDF
        return create_arabic_pdf(elements, title="إشعار راتب")
        
    except Exception as e:
        raise Exception(f"خطأ في إنشاء إشعار الراتب: {str(e)}")


def generate_batch_salary_notifications(department_id=None, month=None, year=None):
    """
    إنشاء إشعارات رواتب مجمعة لموظفي قسم معين أو لكل الموظفين
    
    Args:
        department_id: معرف القسم (اختياري)
        month: رقم الشهر (إلزامي)
        year: السنة (إلزامي)
        
    Returns:
        قائمة بأسماء الموظفين الذين تم إنشاء إشعارات لهم
    """
    from models import Salary, Employee
    
    # بناء الاستعلام
    salary_query = Salary.query.filter_by(month=month, year=year)
    
    # إذا تم تحديد قسم معين
    if department_id:
        employees = Employee.query.filter_by(department_id=department_id).all()
        employee_ids = [emp.id for emp in employees]
        salary_query = salary_query.filter(Salary.employee_id.in_(employee_ids))
        
    # تنفيذ الاستعلام
    salaries = salary_query.all()
    
    # قائمة بأسماء الموظفين الذين تم إنشاء إشعارات لهم
    processed_employees = []
    
    # إنشاء إشعار لكل موظف
    for salary in salaries:
        try:
            # هنا يمكن إضافة المنطق اللازم لتخزين أو إرسال الإشعار
            generate_salary_notification_pdf(salary)
            processed_employees.append(salary.employee.name)
        except Exception as e:
            # تسجيل الخطأ
            print(f"خطأ في إنشاء إشعار للموظف {salary.employee.name}: {str(e)}")
            
    return processed_employees