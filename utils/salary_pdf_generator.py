"""
مولد PDF لإشعارات الرواتب
استخدام FPDF مع دعم كامل للنصوص العربية والتنسيق المحترف
"""

from fpdf import FPDF
from datetime import datetime
import arabic_reshaper
from bidi.algorithm import get_display
import os
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
        # شعار أو عنوان الشركة
        self.set_font('Arial', 'B', 20)
        self.cell(0, 15, 'Employee Management System', 0, 1, 'C')
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
        pdf_content = pdf.output(dest='S').encode('latin-1')
        output.write(pdf_content)
        output.seek(0)
        
        return output.getvalue()
        
    except Exception as e:
        print(f"خطأ في إنشاء إشعار الراتب: {str(e)}")
        raise Exception(f"فشل في إنشاء إشعار الراتب: {str(e)}")

def generate_salary_summary_pdf(salaries, department_name=None, month=None, year=None):
    """
    إنشاء تقرير ملخص رواتب كملف PDF
    
    Args:
        salaries: قائمة بكائنات Salary
        department_name: اسم القسم (اختياري)
        month: رقم الشهر
        year: السنة
        
    Returns:
        bytes: ملف PDF كـ bytes
    """
    try:
        pdf = SalaryPDF()
        pdf.add_page()
        
        # تحضير البيانات
        month_names = {
            1: 'يناير', 2: 'فبراير', 3: 'مارس', 4: 'أبريل',
            5: 'مايو', 6: 'يونيو', 7: 'يوليو', 8: 'أغسطس',
            9: 'سبتمبر', 10: 'أكتوبر', 11: 'نوفمبر', 12: 'ديسمبر'
        }
        
        month_name = month_names.get(int(month), str(month)) if month else 'جميع الشهور'
        
        # العنوان
        pdf.set_font('Arial', 'B', 16)
        title = f'تقرير الرواتب - {month_name} {year}'
        if department_name:
            title += f' - {department_name}'
        pdf.cell(0, 15, pdf.reshape_arabic(title), 0, 1, 'C')
        pdf.ln(10)
        
        # جدول الرواتب
        pdf.set_font('Arial', 'B', 10)
        
        # رؤوس الجدول
        pdf.cell(40, 8, pdf.reshape_arabic('اسم الموظف'), 1, 0, 'C')
        pdf.cell(25, 8, pdf.reshape_arabic('الراتب الأساسي'), 1, 0, 'C')
        pdf.cell(20, 8, pdf.reshape_arabic('البدلات'), 1, 0, 'C')
        pdf.cell(20, 8, pdf.reshape_arabic('المكافآت'), 1, 0, 'C')
        pdf.cell(20, 8, pdf.reshape_arabic('الخصومات'), 1, 0, 'C')
        pdf.cell(25, 8, pdf.reshape_arabic('صافي الراتب'), 1, 1, 'C')
        
        # بيانات الموظفين
        pdf.set_font('Arial', '', 9)
        total_basic = total_allowances = total_bonus = total_deductions = total_net = 0
        
        for salary in salaries:
            # التحقق من طول الاسم وتقسيمه إذا لزم الأمر
            name = salary.employee.name[:15] + '...' if len(salary.employee.name) > 15 else salary.employee.name
            
            pdf.cell(40, 6, pdf.reshape_arabic(name), 1, 0, 'R')
            pdf.cell(25, 6, f'{float(salary.basic_salary):,.0f}', 1, 0, 'C')
            pdf.cell(20, 6, f'{float(salary.allowances):,.0f}', 1, 0, 'C')
            pdf.cell(20, 6, f'{float(salary.bonus):,.0f}', 1, 0, 'C')
            pdf.cell(20, 6, f'{float(salary.deductions):,.0f}', 1, 0, 'C')
            pdf.cell(25, 6, f'{float(salary.net_salary):,.0f}', 1, 1, 'C')
            
            # إضافة للمجاميع
            total_basic += float(salary.basic_salary)
            total_allowances += float(salary.allowances)
            total_bonus += float(salary.bonus)
            total_deductions += float(salary.deductions)
            total_net += float(salary.net_salary)
        
        # المجاميع
        pdf.set_font('Arial', 'B', 9)
        pdf.cell(40, 8, pdf.reshape_arabic('المجموع:'), 1, 0, 'R')
        pdf.cell(25, 8, f'{total_basic:,.0f}', 1, 0, 'C')
        pdf.cell(20, 8, f'{total_allowances:,.0f}', 1, 0, 'C')
        pdf.cell(20, 8, f'{total_bonus:,.0f}', 1, 0, 'C')
        pdf.cell(20, 8, f'{total_deductions:,.0f}', 1, 0, 'C')
        pdf.cell(25, 8, f'{total_net:,.0f}', 1, 1, 'C')
        
        # معلومات إضافية
        pdf.ln(10)
        pdf.set_font('Arial', '', 10)
        pdf.cell(0, 6, pdf.reshape_arabic(f'عدد الموظفين: {len(salaries)}'), 0, 1, 'R')
        pdf.cell(0, 6, pdf.reshape_arabic(f'تاريخ التقرير: {datetime.now().strftime("%Y-%m-%d")}'), 0, 1, 'R')
        
        # إرجاع PDF كـ bytes
        output = BytesIO()
        pdf_content = pdf.output(dest='S').encode('latin-1')
        output.write(pdf_content)
        output.seek(0)
        
        return output.getvalue()
        
    except Exception as e:
        print(f"خطأ في إنشاء تقرير الرواتب: {str(e)}")
        raise Exception(f"فشل في إنشاء تقرير الرواتب: {str(e)}")

def generate_batch_salary_notifications(department_id=None, month=None, year=None):
    """
    إنشاء إشعارات رواتب مجمعة
    
    Args:
        department_id: معرف القسم (اختياري)
        month: رقم الشهر
        year: السنة
        
    Returns:
        list: قائمة بأسماء الموظفين المعالجين
    """
    from models import Salary, Employee
    
    try:
        # بناء الاستعلام
        salary_query = Salary.query.filter_by(month=month, year=year)
        
        # تصفية حسب القسم إذا تم تحديده
        if department_id:
            employees = Employee.query.filter_by(department_id=department_id).all()
            employee_ids = [emp.id for emp in employees]
            salary_query = salary_query.filter(Salary.employee_id.in_(employee_ids))
        
        salaries = salary_query.all()
        processed_employees = []
        
        # معالجة كل راتب
        for salary in salaries:
            try:
                generate_salary_notification_pdf(salary)
                processed_employees.append(salary.employee.name)
            except Exception as e:
                print(f"خطأ في معالجة راتب {salary.employee.name}: {str(e)}")
        
        return processed_employees
        
    except Exception as e:
        print(f"خطأ في المعالجة المجمعة: {str(e)}")
        return []