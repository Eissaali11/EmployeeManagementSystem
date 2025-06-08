"""
مولد PDF احترافي لإشعارات الرواتب بتصميم شبيه بتقرير راس كو
يتضمن شعار الشركة ورأس صفحة وجدول منظم
"""

from fpdf import FPDF
from datetime import datetime
import arabic_reshaper
from bidi.algorithm import get_display
from io import BytesIO
import os

class ProfessionalSalaryPDF(FPDF):
    """فئة PDF احترافية لإشعارات الرواتب"""
    
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
    
    def safe_cell(self, w, h, txt='', border=0, ln=0, align='', fill=False):
        """دالة آمنة لإضافة خلية مع معالجة الأخطاء"""
        try:
            safe_txt = str(txt) if txt is not None else ''
            self.cell(w, h, safe_txt, border, ln, align, fill)
        except Exception as e:
            fallback_txt = f'[Error: {str(e)[:20]}]'
            self.cell(w, h, fallback_txt, border, ln, align, fill)
    
    def add_company_header(self, company_name="نُظم", title="إشعار راتب"):
        """إضافة رأس الشركة مع الشعار"""
        
        # منطقة الشعار (مربع أخضر بدلاً من دائرة)
        self.set_fill_color(46, 204, 113)  # أخضر
        self.rect(15, 15, 20, 20, 'F')
        
        # نص الشعار
        self.set_text_color(255, 255, 255)
        self.set_font('Arial', 'B', 10)
        self.set_xy(18, 22)
        self.safe_cell(14, 6, company_name, 0, 0, 'C')
        
        # اسم الشركة باللغة الإنجليزية
        self.set_text_color(0, 0, 0)
        self.set_font('Arial', 'B', 12)
        self.set_xy(45, 18)
        self.safe_cell(60, 5, 'NUZUM COMPANY LTD', 0, 1, 'L')
        
        # وصف الشركة
        self.set_font('Arial', '', 9)
        self.set_xy(45, 25)
        self.safe_cell(60, 5, 'Employee Management System', 0, 1, 'L')
        
        # العنوان الرئيسي
        self.set_font('Arial', 'B', 16)
        self.set_xy(110, 22)
        title_simple = f"اشعار راتب للموظف"  # نص مبسط بدون تشكيل
        self.safe_cell(80, 8, title_simple, 0, 1, 'R')
        
        # تاريخ التقرير
        self.set_font('Arial', '', 10)
        self.set_xy(110, 32)
        date_text = f"تاريخ التقرير: {datetime.now().strftime('%d-%m-%Y')}"
        self.safe_cell(80, 5, date_text, 0, 1, 'R')
        
        # خط فاصل
        self.set_draw_color(0, 0, 0)
        self.line(10, 45, 200, 45)
        
        self.ln(20)

def create_professional_salary_pdf(salary):
    """
    إنشاء إشعار راتب احترافي مشابه لتقرير راس كو
    
    Args:
        salary: كائن Salary يحتوي على بيانات الراتب
        
    Returns:
        bytes: ملف PDF كـ bytes
    """
    try:
        # إنشاء كائن PDF
        pdf = ProfessionalSalaryPDF()
        pdf.add_page()
        
        # تحضير البيانات
        month_names = {
            1: 'يناير', 2: 'فبراير', 3: 'مارس', 4: 'أبريل',
            5: 'مايو', 6: 'يونيو', 7: 'يوليو', 8: 'أغسطس',
            9: 'سبتمبر', 10: 'أكتوبر', 11: 'نوفمبر', 12: 'ديسمبر'
        }
        
        month = int(salary.month) if not isinstance(salary.month, int) else salary.month
        month_name = month_names.get(month, f'الشهر {month}')
        year = str(salary.year)
        
        # إضافة رأس الشركة
        pdf.add_company_header("نُظم", f"إشعار راتب للموظف - {month_name} {year}")
        
        # عنوان قسم المعلومات الأساسية
        pdf.set_fill_color(220, 220, 220)  # رمادي فاتح
        pdf.set_font('Arial', 'B', 12)
        basic_info_title = "المعلومات الاساسية"  # نص مبسط
        pdf.safe_cell(0, 8, basic_info_title, 1, 1, 'R', True)
        
        # جدول المعلومات الأساسية
        pdf.set_font('Arial', '', 11)
        
        # صف 1: اسم الموظف
        pdf.set_fill_color(245, 245, 245)
        employee_name = str(salary.employee.name) if salary.employee.name else 'غير محدد'
        pdf.safe_cell(95, 8, employee_name, 1, 0, 'L', True)
        pdf.safe_cell(95, 8, pdf.reshape_arabic('اسم الموظف'), 1, 1, 'R', True)
        
        # صف 2: الرقم الوظيفي
        pdf.set_fill_color(255, 255, 255)
        employee_id = str(salary.employee.employee_id) if salary.employee.employee_id else 'غير محدد'
        pdf.safe_cell(95, 8, employee_id, 1, 0, 'L', True)
        pdf.safe_cell(95, 8, pdf.reshape_arabic('الرقم الوظيفي'), 1, 1, 'R', True)
        
        # صف 3: رقم الهوية
        pdf.set_fill_color(245, 245, 245)
        national_id = getattr(salary.employee, 'national_id', 'غير محدد')
        pdf.safe_cell(95, 8, str(national_id), 1, 0, 'L', True)
        pdf.safe_cell(95, 8, pdf.reshape_arabic('رقم الهوية'), 1, 1, 'R', True)
        
        # صف 4: تاريخ الالتحاق
        pdf.set_fill_color(255, 255, 255)
        hire_date = getattr(salary.employee, 'hire_date', 'غير محدد')
        if hire_date and hasattr(hire_date, 'strftime'):
            hire_date = hire_date.strftime('%d-%m-%Y')
        pdf.safe_cell(95, 8, str(hire_date), 1, 0, 'L', True)
        pdf.safe_cell(95, 8, pdf.reshape_arabic('تاريخ الالتحاق'), 1, 1, 'R', True)
        
        # صف 5: الجنسية
        pdf.set_fill_color(245, 245, 245)
        nationality = getattr(salary.employee, 'nationality', 'غير محدد')
        pdf.safe_cell(95, 8, str(nationality), 1, 0, 'L', True)
        pdf.safe_cell(95, 8, pdf.reshape_arabic('الجنسية'), 1, 1, 'R', True)
        
        # صف 6: القسم
        pdf.set_fill_color(255, 255, 255)
        department_name = salary.employee.department.name if salary.employee.department else 'غير محدد'
        pdf.safe_cell(95, 8, str(department_name), 1, 0, 'L', True)
        pdf.safe_cell(95, 8, pdf.reshape_arabic('القسم'), 1, 1, 'R', True)
        
        # صف 7: المشروع
        pdf.set_fill_color(245, 245, 245)
        project = getattr(salary.employee, 'project', salary.employee.job_title)
        pdf.safe_cell(95, 8, str(project), 1, 0, 'L', True)
        pdf.safe_cell(95, 8, pdf.reshape_arabic('المشروع'), 1, 1, 'R', True)
        
        # صف 8: الموقع
        pdf.set_fill_color(255, 255, 255)
        location = getattr(salary.employee, 'location', 'غير محدد')
        pdf.safe_cell(95, 8, str(location), 1, 0, 'L', True)
        pdf.safe_cell(95, 8, pdf.reshape_arabic('الموقع'), 1, 1, 'R', True)
        
        # صف 9: البريد الإلكتروني
        pdf.set_fill_color(245, 245, 245)
        email = getattr(salary.employee, 'email', 'غير محدد')
        pdf.safe_cell(95, 8, str(email), 1, 0, 'L', True)
        pdf.safe_cell(95, 8, pdf.reshape_arabic('البريد الإلكتروني'), 1, 1, 'R', True)
        
        # صف 10: رقم الجوال
        pdf.set_fill_color(255, 255, 255)
        phone = getattr(salary.employee, 'phone', getattr(salary.employee, 'mobile', 'غير محدد'))
        pdf.safe_cell(95, 8, str(phone), 1, 0, 'L', True)
        pdf.safe_cell(95, 8, pdf.reshape_arabic('رقم الجوال'), 1, 1, 'R', True)
        
        pdf.ln(10)
        
        # عنوان قسم تفاصيل الراتب
        pdf.set_fill_color(220, 220, 220)
        pdf.set_font('Arial', 'B', 12)
        salary_details_title = pdf.reshape_arabic('تفاصيل الراتب')
        pdf.safe_cell(0, 8, salary_details_title, 1, 1, 'R', True)
        
        # جدول تفاصيل الراتب
        pdf.set_font('Arial', '', 11)
        
        # الراتب الأساسي
        pdf.set_fill_color(245, 245, 245)
        basic_amount = f'{float(salary.basic_salary):,.2f}'
        pdf.safe_cell(95, 8, basic_amount, 1, 0, 'L', True)
        pdf.safe_cell(95, 8, pdf.reshape_arabic('الراتب الأساسي'), 1, 1, 'R', True)
        
        # البدلات
        pdf.set_fill_color(255, 255, 255)
        allowances_amount = f'{float(salary.allowances):,.2f}'
        pdf.safe_cell(95, 8, allowances_amount, 1, 0, 'L', True)
        pdf.safe_cell(95, 8, pdf.reshape_arabic('البدلات'), 1, 1, 'R', True)
        
        # المكافآت
        pdf.set_fill_color(245, 245, 245)
        bonus_amount = f'{float(salary.bonus):,.2f}'
        pdf.safe_cell(95, 8, bonus_amount, 1, 0, 'L', True)
        pdf.safe_cell(95, 8, pdf.reshape_arabic('المكافآت'), 1, 1, 'R', True)
        
        # إجمالي المستحقات
        total_earnings = float(salary.basic_salary) + float(salary.allowances) + float(salary.bonus)
        pdf.set_fill_color(230, 247, 255)
        pdf.set_font('Arial', 'B', 11)
        total_amount = f'{total_earnings:,.2f}'
        pdf.safe_cell(95, 8, total_amount, 1, 0, 'L', True)
        pdf.safe_cell(95, 8, pdf.reshape_arabic('إجمالي المستحقات'), 1, 1, 'R', True)
        
        # الخصومات
        pdf.set_fill_color(255, 240, 240)
        pdf.set_font('Arial', '', 11)
        deductions_amount = f'{float(salary.deductions):,.2f}'
        pdf.safe_cell(95, 8, deductions_amount, 1, 0, 'L', True)
        pdf.safe_cell(95, 8, pdf.reshape_arabic('الخصومات'), 1, 1, 'R', True)
        
        # صافي الراتب
        pdf.set_fill_color(46, 204, 113)  # أخضر
        pdf.set_text_color(255, 255, 255)  # نص أبيض
        pdf.set_font('Arial', 'B', 12)
        net_amount = f'{float(salary.net_salary):,.2f}'
        pdf.safe_cell(95, 10, net_amount, 1, 0, 'L', True)
        pdf.safe_cell(95, 10, pdf.reshape_arabic('صافي الراتب'), 1, 1, 'R', True)
        
        # استعادة لون النص الأسود
        pdf.set_text_color(0, 0, 0)
        
        # الملاحظات إن وجدت
        if salary.notes:
            pdf.ln(10)
            pdf.set_font('Arial', 'B', 12)
            pdf.set_fill_color(255, 252, 230)
            notes_title = pdf.reshape_arabic('ملاحظات')
            pdf.safe_cell(0, 8, notes_title, 1, 1, 'R', True)
            
            pdf.set_font('Arial', '', 10)
            pdf.set_fill_color(255, 255, 255)
            notes_text = str(salary.notes)[:200] + ('...' if len(str(salary.notes)) > 200 else '')
            pdf.safe_cell(0, 15, pdf.reshape_arabic(notes_text), 1, 1, 'R', True)
        
        # التذييل
        pdf.ln(15)
        pdf.set_font('Arial', '', 9)
        pdf.set_text_color(100, 100, 100)
        
        # معلومات الإصدار
        notification_id = f'رقم الإشعار: SAL-{salary.id}-{year}-{month:02d}'
        pdf.safe_cell(0, 6, pdf.reshape_arabic(notification_id), 0, 1, 'C')
        
        issue_date = f'تاريخ الإصدار: {datetime.now().strftime("%d-%m-%Y")}'
        pdf.safe_cell(0, 6, pdf.reshape_arabic(issue_date), 0, 1, 'C')
        
        # خط فاصل نهائي
        pdf.ln(10)
        pdf.set_draw_color(200, 200, 200)
        pdf.line(20, pdf.get_y(), 190, pdf.get_y())
        
        # إرجاع PDF كـ bytes
        output = BytesIO()
        
        try:
            pdf_content = pdf.output(dest='S')
            
            if isinstance(pdf_content, bytes):
                output.write(pdf_content)
            elif isinstance(pdf_content, bytearray):
                output.write(bytes(pdf_content))
            elif isinstance(pdf_content, str):
                try:
                    pdf_content = pdf_content.encode('latin-1')
                except UnicodeEncodeError:
                    pdf_content = pdf_content.encode('utf-8', errors='replace')
                output.write(pdf_content)
            else:
                output.write(str(pdf_content).encode('utf-8', errors='replace'))
                
        except Exception as e:
            print(f"خطأ في ترميز PDF الاحترافي: {str(e)}")
            # في حالة فشل الترميز، استخدام PDF بسيط
            from utils.simple_salary_pdf import create_emergency_salary_pdf
            return create_emergency_salary_pdf(salary)
        
        output.seek(0)
        return output.getvalue()
        
    except Exception as e:
        print(f"خطأ في إنشاء إشعار الراتب الاحترافي: {str(e)}")
        # في حالة الفشل، استخدام المولد البسيط
        from utils.simple_salary_pdf import create_simple_salary_pdf
        return create_simple_salary_pdf(salary)