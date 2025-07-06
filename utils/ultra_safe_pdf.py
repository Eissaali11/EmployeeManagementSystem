"""
مولد PDF آمن تماماً - يعمل مع أي نص عربي بدون مشاكل ترميز
"""

from fpdf import FPDF
from datetime import datetime
from io import BytesIO

class UltraSafePDF(FPDF):
    """PDF آمن تماماً بدون مشاكل ترميز"""
    
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        
    def safe_arabic_text(self, text):
        """تحويل آمن للنصوص العربية إلى نص قابل للعرض"""
        if not text:
            return ""
        
        # تحويل إلى string
        text_str = str(text)
        
        # قاموس تحويل الأحرف العربية إلى أحرف آمنة
        arabic_to_safe = {
            'ا': 'a', 'أ': 'a', 'إ': 'a', 'آ': 'aa',
            'ب': 'b', 'ت': 't', 'ث': 'th', 'ج': 'j',
            'ح': 'h', 'خ': 'kh', 'د': 'd', 'ذ': 'th',
            'ر': 'r', 'ز': 'z', 'س': 's', 'ش': 'sh',
            'ص': 's', 'ض': 'd', 'ط': 't', 'ظ': 'th',
            'ع': 'a', 'غ': 'gh', 'ف': 'f', 'ق': 'q',
            'ك': 'k', 'ل': 'l', 'م': 'm', 'ن': 'n',
            'ه': 'h', 'و': 'w', 'ي': 'y', 'ى': 'a',
            'ة': 'h', 'ء': 'a', 'ؤ': 'w', 'ئ': 'y'
        }
        
        # تحويل النص
        result = ""
        for char in text_str:
            if char in arabic_to_safe:
                result += arabic_to_safe[char]
            elif char.isalnum():
                result += char
            elif char in ' .-_:()[]{}/@#$%^&*+=<>?!,;':
                result += char
            else:
                result += ' '
        
        # تنظيف المسافات
        result = ' '.join(result.split())
        return result[:80]  # تحديد الطول
        
    def ultra_safe_cell(self, w, h, txt='', border=0, ln=0, align='', fill=False):
        """خلية آمنة جداً"""
        try:
            # تحويل النص إلى نص آمن
            safe_txt = self.safe_arabic_text(txt)
            self.cell(w, h, safe_txt, border, ln, align, fill)
        except Exception:
            # في حالة أي خطأ، استخدم نص بديل
            fallback_txt = f'[{len(str(txt))} chars]'
            try:
                self.cell(w, h, fallback_txt, border, ln, align, fill)
            except:
                self.cell(w, h, '[TEXT]', border, ln, align, fill)

def create_ultra_safe_salary_pdf(salary):
    """
    إنشاء PDF آمن تماماً بدون أي مشاكل ترميز
    """
    try:
        pdf = UltraSafePDF()
        pdf.add_page()
        
        # الرأس الآمن
        pdf.set_fill_color(41, 128, 185)  # أزرق
        pdf.rect(0, 0, 210, 35, 'F')
        
        # شعار الشركة
        try:
            # محاولة إضافة صورة الشعار
            logo_path = 'static\images\logo\logo_new.png'
            pdf.image(logo_path, x=15, y=8, w=20, h=20)
        except Exception:
            # في حالة عدم وجود الصورة، استخدام مربع أزرق مع نص
            pdf.set_fill_color(52, 152, 219)  # أزرق
            pdf.rect(15, 8, 20, 20, 'F')
            
            # نص الشعار
            pdf.set_text_color(255, 255, 255)
            pdf.set_font('Arial', 'B', 12)
            pdf.set_xy(18, 15)
            pdf.ultra_safe_cell(14, 6, 'M', 0, 0, 'C')
        
        # # اسم الشركة
        # pdf.set_font('Arial', 'B', 16)
        # pdf.set_xy(40, 12)
        # pdf.ultra_safe_cell(100, 8, 'NUZUM COMPANY LTD', 0, 1, 'L')
        
        # وصف الشركة
        pdf.set_font('Arial', 'B', 12)
        pdf.set_xy(40, 12)
        pdf.ultra_safe_cell(100, 6, 'Employee Management System', 0, 1, 'L')
        
        # عنوان التقرير
        pdf.set_font('Arial', 'B', 18)
        pdf.set_xy(120, 10)
        pdf.ultra_safe_cell(70, 8, 'SALARY NOTIFICATION', 0, 1, 'R')
        
        # التاريخ
        pdf.set_font('Arial', '', 10)
        pdf.set_xy(120, 22)
        date_str = datetime.now().strftime('%Y-%m-%d')
        pdf.ultra_safe_cell(70, 6, f'Date: {date_str}', 0, 1, 'R')
        
        # استعادة اللون الأسود
        pdf.set_text_color(0, 0, 0)
        pdf.ln(15)
        
        # معلومات الموظف
        pdf.set_fill_color(240, 248, 255)  # أزرق فاتح
        pdf.set_font('Arial', 'B', 14)
        pdf.ultra_safe_cell(0, 10, 'EMPLOYEE INFORMATION', 1, 1, 'C', True)
        
        pdf.set_font('Arial', '', 12)
        
        # بيانات الموظف
        employee_data = [
            ('Employee Name', str(salary.employee.name)),
            ('Employee ID', str(salary.employee.employee_id)),
            ('Job Title', str(salary.employee.job_title)),
            ('Department', str(salary.employee.department.name) if salary.employee.department else 'Not Specified'),
            ('Month/Year', f'{salary.month}/{salary.year}'),
        ]
        
        for i, (label, value) in enumerate(employee_data):
            # تناوب الألوان
            if i % 2 == 0:
                pdf.set_fill_color(248, 249, 250)
            else:
                pdf.set_fill_color(255, 255, 255)
                
            pdf.ultra_safe_cell(70, 8, label, 1, 0, 'L', True)
            pdf.ultra_safe_cell(120, 8, value, 1, 1, 'L', True)
        
        pdf.ln(10)
        
        # تفاصيل الراتب
        pdf.set_fill_color(52, 152, 219)  # أزرق
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Arial', 'B', 14)
        pdf.ultra_safe_cell(0, 10, 'SALARY DETAILS', 1, 1, 'C', True)
        
        # رأس الجدول
        pdf.ultra_safe_cell(120, 8, 'ITEM', 1, 0, 'C', True)
        pdf.ultra_safe_cell(70, 8, 'AMOUNT (SAR)', 1, 1, 'C', True)
        
        # استعادة اللون الأسود
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Arial', '', 12)
        
        # تفاصيل الراتب
        salary_items = [
            ('Basic Salary', float(salary.basic_salary)),
            ('Allowances', float(salary.allowances)),
            ('Bonus', float(salary.bonus)),
        ]
        
        total_earnings = 0
        for i, (item, amount) in enumerate(salary_items):
            total_earnings += amount
            
            if i % 2 == 0:
                pdf.set_fill_color(248, 249, 250)
            else:
                pdf.set_fill_color(255, 255, 255)
                
            pdf.ultra_safe_cell(120, 8, item, 1, 0, 'L', True)
            pdf.ultra_safe_cell(70, 8, f'{amount:,.2f}', 1, 1, 'C', True)
        
        # إجمالي المستحقات
        pdf.set_fill_color(230, 247, 255)  # أزرق فاتح جداً
        pdf.set_font('Arial', 'B', 12)
        pdf.ultra_safe_cell(120, 10, 'TOTAL EARNINGS', 1, 0, 'L', True)
        pdf.ultra_safe_cell(70, 10, f'{total_earnings:,.2f}', 1, 1, 'C', True)
        
        # الخصومات
        pdf.set_fill_color(255, 245, 245)  # أحمر فاتح
        pdf.set_font('Arial', '', 12)
        deductions = float(salary.deductions)
        pdf.ultra_safe_cell(120, 8, 'DEDUCTIONS', 1, 0, 'L', True)
        pdf.ultra_safe_cell(70, 8, f'{deductions:,.2f}', 1, 1, 'C', True)
        
        # صافي الراتب
        pdf.set_fill_color(46, 204, 113)  # أخضر
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Arial', 'B', 16)
        net_salary = float(salary.net_salary)
        pdf.ultra_safe_cell(120, 12, 'NET SALARY', 1, 0, 'L', True)
        pdf.ultra_safe_cell(70, 12, f'{net_salary:,.2f}', 1, 1, 'C', True)
        
        # استعادة اللون الأسود
        pdf.set_text_color(0, 0, 0)
        pdf.ln(15)
        
        # الملاحظات (إن وجدت)
        if salary.notes:
            pdf.set_font('Arial', 'B', 12)
            pdf.ultra_safe_cell(0, 8, 'NOTES:', 0, 1, 'L')
            pdf.set_font('Arial', '', 10)
            notes_text = str(salary.notes)[:200]  # تحديد طول الملاحظات
            pdf.ultra_safe_cell(0, 8, notes_text, 1, 1, 'L')
            pdf.ln(5)
        
        # التذييل
        pdf.set_font('Arial', '', 9)
        pdf.set_text_color(100, 100, 100)
        
        # معرف الإشعار
        notification_id = f'Notification ID: SAL-{salary.id}-{salary.year}-{salary.month:02d}'
        pdf.ultra_safe_cell(0, 6, notification_id, 0, 1, 'C')
        
        # تاريخ الإصدار
        issue_date = f'Issue Date: {datetime.now().strftime("%Y-%m-%d %H:%M")}'
        pdf.ultra_safe_cell(0, 6, issue_date, 0, 1, 'C')
        
        # خط فاصل
        pdf.ln(5)
        pdf.set_draw_color(200, 200, 200)
        pdf.line(20, pdf.get_y(), 190, pdf.get_y())
        
        # إنشاء الملف
        output = BytesIO()
        
        try:
            # محاولة إنشاء PDF
            pdf_content = pdf.output(dest='S')
            
            # التعامل مع نوع البيانات
            if isinstance(pdf_content, str):
                # تحويل آمن إلى bytes
                output.write(pdf_content.encode('latin-1', errors='replace'))
            else:
                output.write(pdf_content)
                
        except Exception as e:
            print(f"خطأ في إنشاء PDF: {str(e)}")
            # إنشاء PDF بسيط جداً في حالة الفشل
            return create_emergency_text_pdf(salary)
        
        output.seek(0)
        return output.getvalue()
        
    except Exception as e:
        print(f"خطأ عام في PDF: {str(e)}")
        return create_emergency_text_pdf(salary)

def create_emergency_text_pdf(salary):
    """PDF طوارئ نصي بسيط"""
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        
        # رأس بسيط
        pdf.cell(0, 10, 'NUZUM - SALARY NOTIFICATION', 0, 1, 'C')
        pdf.ln(10)
        
        # بيانات أساسية
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 8, f'Employee: {salary.employee.employee_id}', 0, 1)
        pdf.cell(0, 8, f'Name: [Employee Name]', 0, 1)
        pdf.cell(0, 8, f'Period: {salary.month}/{salary.year}', 0, 1)
        pdf.ln(5)
        
        # تفاصيل الراتب
        pdf.cell(0, 8, f'Basic Salary: {salary.basic_salary} SAR', 0, 1)
        pdf.cell(0, 8, f'Allowances: {salary.allowances} SAR', 0, 1)
        pdf.cell(0, 8, f'Bonus: {salary.bonus} SAR', 0, 1)
        pdf.cell(0, 8, f'Deductions: {salary.deductions} SAR', 0, 1)
        pdf.ln(5)
        
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, f'NET SALARY: {salary.net_salary} SAR', 0, 1)
        
        # إنشاء الملف
        output = BytesIO()
        pdf_content = pdf.output(dest='S')
        
        if isinstance(pdf_content, str):
            output.write(pdf_content.encode('latin-1', errors='replace'))
        else:
            output.write(pdf_content)
            
        output.seek(0)
        return output.getvalue()
        
    except Exception:
        # في حالة فشل كل شيء
        return b'PDF_CREATION_FAILED'