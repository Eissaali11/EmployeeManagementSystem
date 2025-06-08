"""
مولد PDF بسيط لإشعارات الرواتب يعمل بدون خطوط خارجية
يستخدم FPDF مع الخطوط الافتراضية المدمجة فقط
"""

from fpdf import FPDF
from datetime import datetime
import arabic_reshaper
from bidi.algorithm import get_display
from io import BytesIO

class SimpleSalaryPDF(FPDF):
    """فئة PDF بسيطة للرواتب تعمل بدون خطوط خارجية"""
    
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        
    def reshape_arabic(self, text):
        """تنسيق النص العربي للعرض الصحيح"""
        if not text:
            return ""
        try:
            # تجربة تشكيل النص العربي
            reshaped_text = arabic_reshaper.reshape(str(text))
            return get_display(reshaped_text)
        except:
            # في حالة فشل التشكيل، إرجاع النص كما هو
            return str(text)
    
    def safe_cell(self, w, h, txt='', border=0, ln=0, align='', fill=False):
        """دالة آمنة لإضافة خلية مع معالجة الأخطاء"""
        try:
            # تحويل النص لسلسلة نصية آمنة
            safe_txt = str(txt) if txt is not None else ''
            self.cell(w, h, safe_txt, border, ln, align, fill)
        except Exception as e:
            # في حالة فشل الخلية، استخدام نص بديل
            fallback_txt = f'[Error: {str(e)[:20]}]'
            self.cell(w, h, fallback_txt, border, ln, align, fill)
    
    def header(self):
        """رأس الصفحة"""
        try:
            self.set_font('Arial', 'B', 16)
            header_text = self.reshape_arabic('نظام إدارة الموظفين - نُظم')
            self.safe_cell(0, 10, header_text, 0, 1, 'C')
            self.ln(5)
        except:
            # رأس بديل في حالة الخطأ
            self.set_font('Arial', 'B', 16)
            self.safe_cell(0, 10, 'Employee Management System - Nuzum', 0, 1, 'C')
            self.ln(5)
        
    def footer(self):
        """تذييل الصفحة"""
        try:
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
            page_text = f'Page {self.page_no()}'
            self.safe_cell(0, 10, page_text, 0, 0, 'C')
        except:
            pass

def create_simple_salary_pdf(salary):
    """
    إنشاء إشعار راتب بسيط يعمل في جميع البيئات
    
    Args:
        salary: كائن Salary يحتوي على بيانات الراتب
        
    Returns:
        bytes: ملف PDF كـ bytes
    """
    try:
        # إنشاء كائن PDF
        pdf = SimpleSalaryPDF()
        pdf.add_page()
        
        # تحضير البيانات الأساسية
        month_names = {
            1: 'January - يناير', 2: 'February - فبراير', 3: 'March - مارس', 4: 'April - أبريل',
            5: 'May - مايو', 6: 'June - يونيو', 7: 'July - يوليو', 8: 'August - أغسطس',
            9: 'September - سبتمبر', 10: 'October - أكتوبر', 11: 'November - نوفمبر', 12: 'December - ديسمبر'
        }
        
        month = int(salary.month) if not isinstance(salary.month, int) else salary.month
        month_name = month_names.get(month, f'Month {month}')
        year = str(salary.year)
        
        # العنوان الرئيسي
        pdf.set_font('Arial', 'B', 18)
        title = f'Salary Notification - {month_name} {year}'
        pdf.safe_cell(0, 15, title, 0, 1, 'C')
        pdf.ln(10)
        
        # معلومات الموظف
        pdf.set_font('Arial', 'B', 14)
        pdf.safe_cell(0, 10, 'Employee Information / بيانات الموظف', 0, 1, 'L')
        pdf.ln(5)
        
        # جدول معلومات الموظف
        pdf.set_font('Arial', '', 12)
        
        # اسم الموظف
        pdf.safe_cell(50, 8, 'Name / الاسم:', 1, 0, 'L')
        employee_name = str(salary.employee.name) if salary.employee.name else 'N/A'
        pdf.safe_cell(0, 8, employee_name, 1, 1, 'L')
        
        # رقم الموظف
        pdf.safe_cell(50, 8, 'ID / الرقم:', 1, 0, 'L')
        employee_id = str(salary.employee.employee_id) if salary.employee.employee_id else 'N/A'
        pdf.safe_cell(0, 8, employee_id, 1, 1, 'L')
        
        # المسمى الوظيفي
        pdf.safe_cell(50, 8, 'Position / المسمى:', 1, 0, 'L')
        job_title = str(salary.employee.job_title) if salary.employee.job_title else 'N/A'
        pdf.safe_cell(0, 8, job_title, 1, 1, 'L')
        
        # القسم
        pdf.safe_cell(50, 8, 'Department / القسم:', 1, 0, 'L')
        department_name = str(salary.employee.department.name) if salary.employee.department else 'N/A'
        pdf.safe_cell(0, 8, department_name, 1, 1, 'L')
        
        pdf.ln(10)
        
        # تفاصيل الراتب
        pdf.set_font('Arial', 'B', 14)
        pdf.safe_cell(0, 10, 'Salary Details / تفاصيل الراتب', 0, 1, 'L')
        pdf.ln(5)
        
        # جدول الراتب
        pdf.set_font('Arial', '', 12)
        
        # الراتب الأساسي
        pdf.safe_cell(70, 8, 'Basic Salary / الراتب الأساسي:', 1, 0, 'L')
        basic_amount = f'{float(salary.basic_salary):,.2f} SAR'
        pdf.safe_cell(0, 8, basic_amount, 1, 1, 'R')
        
        # البدلات
        pdf.safe_cell(70, 8, 'Allowances / البدلات:', 1, 0, 'L')
        allowances_amount = f'{float(salary.allowances):,.2f} SAR'
        pdf.safe_cell(0, 8, allowances_amount, 1, 1, 'R')
        
        # المكافآت
        pdf.safe_cell(70, 8, 'Bonus / المكافآت:', 1, 0, 'L')
        bonus_amount = f'{float(salary.bonus):,.2f} SAR'
        pdf.safe_cell(0, 8, bonus_amount, 1, 1, 'R')
        
        # إجمالي المستحقات
        total_earnings = float(salary.basic_salary) + float(salary.allowances) + float(salary.bonus)
        pdf.set_font('Arial', 'B', 12)
        pdf.safe_cell(70, 8, 'Total Earnings / المستحقات:', 1, 0, 'L')
        total_amount = f'{total_earnings:,.2f} SAR'
        pdf.safe_cell(0, 8, total_amount, 1, 1, 'R')
        
        # الخصومات
        pdf.set_font('Arial', '', 12)
        pdf.safe_cell(70, 8, 'Deductions / الخصومات:', 1, 0, 'L')
        deductions_amount = f'{float(salary.deductions):,.2f} SAR'
        pdf.safe_cell(0, 8, deductions_amount, 1, 1, 'R')
        
        # صافي الراتب
        pdf.set_font('Arial', 'B', 14)
        pdf.set_fill_color(230, 230, 230)
        pdf.safe_cell(70, 10, 'Net Salary / صافي الراتب:', 1, 0, 'L', True)
        net_amount = f'{float(salary.net_salary):,.2f} SAR'
        pdf.safe_cell(0, 10, net_amount, 1, 1, 'R', True)
        
        pdf.ln(10)
        
        # الملاحظات
        if salary.notes:
            pdf.set_font('Arial', 'B', 12)
            pdf.safe_cell(0, 8, 'Notes / ملاحظات:', 0, 1, 'L')
            pdf.set_font('Arial', '', 10)
            # تقسيم الملاحظات لعدة أسطر إذا لزم الأمر
            notes_text = str(salary.notes)[:200] + ('...' if len(str(salary.notes)) > 200 else '')
            pdf.safe_cell(0, 6, notes_text, 1, 1, 'L')
            pdf.ln(5)
        
        # معلومات إضافية
        pdf.set_font('Arial', '', 10)
        issue_date = f'Issue Date / تاريخ الإصدار: {datetime.now().strftime("%Y-%m-%d")}'
        pdf.safe_cell(0, 6, issue_date, 0, 1, 'L')
        
        notification_id = f'Notification ID / رقم الإشعار: SAL-{salary.id}-{year}-{month:02d}'
        pdf.safe_cell(0, 6, notification_id, 0, 1, 'L')
        
        # توقيع
        pdf.ln(15)
        pdf.safe_cell(0, 6, 'Signature / التوقيع: ___________________', 0, 1, 'L')
        pdf.safe_cell(0, 6, 'Date / التاريخ: ___________________', 0, 1, 'L')
        
        # إرجاع PDF كـ bytes
        output = BytesIO()
        pdf_content = pdf.output(dest='S')
        
        # معالجة نوع البيانات المُرجعة
        if isinstance(pdf_content, str):
            pdf_content = pdf_content.encode('latin-1')
        elif hasattr(pdf_content, 'encode'):
            pdf_content = str(pdf_content).encode('latin-1')
        
        output.write(pdf_content)
        output.seek(0)
        
        return output.getvalue()
        
    except Exception as e:
        print(f"خطأ في إنشاء إشعار الراتب البسيط: {str(e)}")
        # إرجاع PDF بسيط جداً في حالة الفشل
        return create_emergency_salary_pdf(salary)

def create_emergency_salary_pdf(salary):
    """
    إنشاء PDF طوارئ بسيط جداً في حالة فشل النظام الرئيسي
    """
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        
        # عنوان بسيط
        pdf.cell(0, 10, 'SALARY NOTIFICATION', 0, 1, 'C')
        pdf.ln(10)
        
        # بيانات أساسية
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 8, f'Employee: {salary.employee.name}', 0, 1)
        pdf.cell(0, 8, f'ID: {salary.employee.employee_id}', 0, 1)
        pdf.cell(0, 8, f'Month: {salary.month}/{salary.year}', 0, 1)
        pdf.ln(5)
        
        pdf.cell(0, 8, f'Basic Salary: {salary.basic_salary} SAR', 0, 1)
        pdf.cell(0, 8, f'Allowances: {salary.allowances} SAR', 0, 1)
        pdf.cell(0, 8, f'Bonus: {salary.bonus} SAR', 0, 1)
        pdf.cell(0, 8, f'Deductions: {salary.deductions} SAR', 0, 1)
        pdf.ln(5)
        
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, f'NET SALARY: {salary.net_salary} SAR', 0, 1)
        
        # إرجاع النتيجة
        output = BytesIO()
        pdf_content = pdf.output(dest='S')
        if isinstance(pdf_content, str):
            pdf_content = pdf_content.encode('latin-1')
        output.write(pdf_content)
        output.seek(0)
        
        return output.getvalue()
        
    except Exception as e:
        print(f"حتى PDF الطوارئ فشل: {str(e)}")
        return b'PDF_GENERATION_FAILED'