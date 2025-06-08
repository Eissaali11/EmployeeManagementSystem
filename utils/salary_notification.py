"""
وحدة إنشاء إشعار راتب كملف PDF محسنة
استخدام FPDF مع دعم كامل للنصوص العربية والتنسيق المحترف
"""

from fpdf import FPDF
from datetime import datetime
import arabic_reshaper
from bidi.algorithm import get_display
from io import BytesIO

class SalaryPDF(FPDF):
    """فئة PDF مخصصة لإشعارات الرواتب"""
    
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        
    def reshape_arabic(self, text):
        """تنسيق النص العربي للعرض الصحيح"""
        if not text:
            return ""
        try:
            reshaped_text = arabic_reshaper.reshape(str(text))
            return get_display(reshaped_text)
        except:
            return str(text)
    
    def header(self):
        """رأس الصفحة"""
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, self.reshape_arabic('نظام إدارة الموظفين - نُظم'), 0, 1, 'C')
        self.ln(5)
        
    def footer(self):
        """تذييل الصفحة"""
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        page_text = f'Page {self.page_no()}'
        self.cell(0, 10, page_text, 0, 0, 'C')

def generate_salary_notification_pdf(salary):
    """
    إنشاء إشعار راتب محترف كملف PDF
    
    Args:
        salary: كائن Salary يحتوي على بيانات الراتب
        
    Returns:
        bytes: ملف PDF كـ bytes
    """
    try:
        # إنشاء كائن PDF
        pdf = SalaryPDF()
        pdf.add_page()
        
        # تحضير البيانات
        month_names = {
            1: 'يناير', 2: 'فبراير', 3: 'مارس', 4: 'أبريل',
            5: 'مايو', 6: 'يونيو', 7: 'يوليو', 8: 'أغسطس',
            9: 'سبتمبر', 10: 'أكتوبر', 11: 'نوفمبر', 12: 'ديسمبر'
        }
        
        month = int(salary.month) if not isinstance(salary.month, int) else salary.month
        month_name = month_names.get(month, str(month))
        year = str(salary.year)
        
        # العنوان الرئيسي
        pdf.set_font('Arial', 'B', 18)
        title = pdf.reshape_arabic(f'إشعار راتب - {month_name} {year}')
        pdf.cell(0, 15, title, 0, 1, 'C')
        pdf.ln(10)
        
        # معلومات الموظف
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, pdf.reshape_arabic('بيانات الموظف'), 0, 1, 'R')
        pdf.ln(5)
        
        # جدول معلومات الموظف
        pdf.set_font('Arial', '', 12)
        
        # اسم الموظف
        pdf.cell(50, 8, pdf.reshape_arabic('اسم الموظف:'), 1, 0, 'R')
        pdf.cell(0, 8, pdf.reshape_arabic(salary.employee.name), 1, 1, 'R')
        
        # رقم الموظف
        pdf.cell(50, 8, pdf.reshape_arabic('رقم الموظف:'), 1, 0, 'R')
        pdf.cell(0, 8, str(salary.employee.employee_id), 1, 1, 'R')
        
        # المسمى الوظيفي
        pdf.cell(50, 8, pdf.reshape_arabic('المسمى الوظيفي:'), 1, 0, 'R')
        pdf.cell(0, 8, pdf.reshape_arabic(salary.employee.job_title), 1, 1, 'R')
        
        # القسم
        department_name = salary.employee.department.name if salary.employee.department else 'غير محدد'
        pdf.cell(50, 8, pdf.reshape_arabic('القسم:'), 1, 0, 'R')
        pdf.cell(0, 8, pdf.reshape_arabic(department_name), 1, 1, 'R')
        
        pdf.ln(10)
        
        # تفاصيل الراتب
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, pdf.reshape_arabic('تفاصيل الراتب'), 0, 1, 'R')
        pdf.ln(5)
        
        # جدول الراتب
        pdf.set_font('Arial', '', 12)
        
        # الراتب الأساسي
        pdf.cell(50, 8, pdf.reshape_arabic('الراتب الأساسي:'), 1, 0, 'R')
        pdf.cell(0, 8, f'{float(salary.basic_salary):,.2f} ريال', 1, 1, 'R')
        
        # البدلات
        pdf.cell(50, 8, pdf.reshape_arabic('البدلات:'), 1, 0, 'R')
        pdf.cell(0, 8, f'{float(salary.allowances):,.2f} ريال', 1, 1, 'R')
        
        # المكافآت
        pdf.cell(50, 8, pdf.reshape_arabic('المكافآت:'), 1, 0, 'R')
        pdf.cell(0, 8, f'{float(salary.bonus):,.2f} ريال', 1, 1, 'R')
        
        # إجمالي المستحقات
        total_earnings = float(salary.basic_salary) + float(salary.allowances) + float(salary.bonus)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(50, 8, pdf.reshape_arabic('إجمالي المستحقات:'), 1, 0, 'R')
        pdf.cell(0, 8, f'{total_earnings:,.2f} ريال', 1, 1, 'R')
        
        # الخصومات
        pdf.set_font('Arial', '', 12)
        pdf.cell(50, 8, pdf.reshape_arabic('الخصومات:'), 1, 0, 'R')
        pdf.cell(0, 8, f'{float(salary.deductions):,.2f} ريال', 1, 1, 'R')
        
        # صافي الراتب
        pdf.set_font('Arial', 'B', 14)
        pdf.set_fill_color(230, 230, 230)
        pdf.cell(50, 10, pdf.reshape_arabic('صافي الراتب:'), 1, 0, 'R', True)
        pdf.cell(0, 10, f'{float(salary.net_salary):,.2f} ريال', 1, 1, 'R', True)
        
        pdf.ln(10)
        
        # الملاحظات
        if salary.notes:
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, pdf.reshape_arabic('ملاحظات:'), 0, 1, 'R')
            pdf.set_font('Arial', '', 10)
            pdf.multi_cell(0, 6, pdf.reshape_arabic(salary.notes), 1, 'R')
            pdf.ln(5)
        
        # معلومات إضافية
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 6, pdf.reshape_arabic(f'تاريخ الإصدار: {datetime.now().strftime("%Y-%m-%d")}'), 0, 1, 'R')
        pdf.cell(0, 6, pdf.reshape_arabic(f'رقم الإشعار: SAL-{salary.id}-{year}-{month:02d}'), 0, 1, 'R')
        
        # توقيع
        pdf.ln(15)
        pdf.cell(0, 6, pdf.reshape_arabic('التوقيع: ___________________'), 0, 1, 'L')
        pdf.cell(0, 6, pdf.reshape_arabic('التاريخ: ___________________'), 0, 1, 'L')
        
        # إرجاع PDF كـ bytes
        output = BytesIO()
        pdf_content = pdf.output(dest='S')
        if isinstance(pdf_content, str):
            pdf_content = pdf_content.encode('latin-1')
        output.write(pdf_content)
        output.seek(0)
        
        return output.getvalue()
        
    except Exception as e:
        print(f"خطأ في إنشاء إشعار الراتب: {str(e)}")
        raise Exception(f"فشل في إنشاء إشعار الراتب: {str(e)}")


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
    
    # التأكد من تحويل البيانات إلى النوع المناسب
    month = int(month) if month is not None and not isinstance(month, int) else month
    year = int(year) if year is not None and not isinstance(year, int) else year
    department_id = int(department_id) if department_id is not None and not isinstance(department_id, int) else department_id
    
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
            # إنشاء إشعار وإضافة اسم الموظف إلى القائمة
            generate_salary_notification_pdf(salary)
            processed_employees.append(salary.employee.name)
        except Exception as e:
            # تسجيل الخطأ
            print(f"خطأ في إنشاء إشعار للموظف {salary.employee.name}: {str(e)}")
            
    return processed_employees