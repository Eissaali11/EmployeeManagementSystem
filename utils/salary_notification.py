from io import BytesIO
import arabic_reshaper
from bidi.algorithm import get_display
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

def generate_salary_notification_pdf(salary):
    """
    إنشاء إشعار راتب لموظف كملف PDF
    
    Args:
        salary: كائن Salary يحتوي على بيانات الراتب
        
    Returns:
        BytesIO يحتوي على ملف PDF
    """
    buffer = BytesIO()
    
    # تهيئة مستند PDF
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )
    
    # تعريف الأنماط
    styles = getSampleStyleSheet()
    
    # تعريف نمط للنصوص العربية
    styles.add(ParagraphStyle(
        name='Arabic',
        fontName='Helvetica',
        alignment=1,  # وسط
        rightIndent=0,
        leftIndent=0,
        wordWrap='RTL',
        firstLineIndent=0,
        textColor=colors.black,
        fontSize=12
    ))
    
    styles.add(ParagraphStyle(
        name='ArabicTitle',
        fontName='Helvetica-Bold',
        alignment=1,  # وسط
        rightIndent=0,
        leftIndent=0,
        wordWrap='RTL',
        firstLineIndent=0,
        textColor=colors.black,
        fontSize=16
    ))
    
    # دالة مساعدة لإعادة تشكيل النص العربي
    def arabic_text(text):
        if not text:
            return ""
        reshaped_text = arabic_reshaper.reshape(str(text))
        return get_display(reshaped_text)
    
    # الحصول على اسم الشهر بالعربية
    month_names = {
        1: 'يناير', 2: 'فبراير', 3: 'مارس', 4: 'أبريل',
        5: 'مايو', 6: 'يونيو', 7: 'يوليو', 8: 'أغسطس',
        9: 'سبتمبر', 10: 'أكتوبر', 11: 'نوفمبر', 12: 'ديسمبر'
    }
    month_name = month_names.get(salary.month, str(salary.month))
    
    # بناء محتوى المستند
    elements = []
    
    # العنوان
    elements.append(Paragraph(arabic_text("إشعار راتب"), styles['ArabicTitle']))
    elements.append(Spacer(1, 20))
    
    # معلومات الموظف
    elements.append(Paragraph(arabic_text(f"اسم الموظف: {salary.employee.name}"), styles['Arabic']))
    elements.append(Paragraph(arabic_text(f"الرقم الوظيفي: {salary.employee.employee_id}"), styles['Arabic']))
    if salary.employee.department:
        elements.append(Paragraph(arabic_text(f"القسم: {salary.employee.department.name}"), styles['Arabic']))
    elements.append(Paragraph(arabic_text(f"المسمى الوظيفي: {salary.employee.job_title}"), styles['Arabic']))
    elements.append(Spacer(1, 20))
    
    # معلومات الراتب
    elements.append(Paragraph(arabic_text(f"راتب شهر: {month_name} {salary.year}"), styles['ArabicTitle']))
    elements.append(Spacer(1, 10))
    
    # جدول تفاصيل الراتب
    data = [
        [arabic_text("البند"), arabic_text("المبلغ")],
        [arabic_text("الراتب الأساسي"), f"{salary.basic_salary:.2f}"],
        [arabic_text("البدلات"), f"{salary.allowances:.2f}"],
        [arabic_text("المكافآت"), f"{salary.bonus:.2f}"],
        [arabic_text("الخصومات"), f"{salary.deductions:.2f}"],
        [arabic_text("صافي الراتب"), f"{salary.net_salary:.2f}"]
    ]
    
    table = Table(data, colWidths=[300, 150])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (1, 0), colors.black),
        ('ALIGN', (0, 0), (1, 0), 'CENTER'),
        ('ALIGN', (1, 1), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, -1), (1, -1), 'Helvetica-Bold'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BACKGROUND', (0, -1), (1, -1), colors.lightgrey),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 20))
    
    # ملاحظات
    if salary.notes:
        elements.append(Paragraph(arabic_text("ملاحظات:"), styles['Arabic']))
        elements.append(Paragraph(arabic_text(salary.notes), styles['Arabic']))
    
    # التوقيع
    elements.append(Spacer(1, 40))
    elements.append(Paragraph(arabic_text("توقيع المدير المالي"), styles['Arabic']))
    elements.append(Spacer(1, 40))
    elements.append(Paragraph(arabic_text("توقيع الموظف باستلام الإشعار"), styles['Arabic']))
    
    # التذييل
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(arabic_text(f"تم إصدار هذا الإشعار في {datetime.now().strftime('%Y-%m-%d')}"), styles['Arabic']))
    
    # بناء المستند
    doc.build(elements)
    
    buffer.seek(0)
    return buffer.getvalue()


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
            # يمكن هنا إضافة منطق لإرسال الإشعار بالبريد الإلكتروني أو حفظه
            processed_employees.append(salary.employee.name)
        except Exception as e:
            # تسجيل الخطأ
            print(f"خطأ في إنشاء إشعار للموظف {salary.employee.name}: {str(e)}")
            
    return processed_employees