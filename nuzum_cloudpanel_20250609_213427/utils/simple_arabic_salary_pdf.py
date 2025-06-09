"""
مولد PDF بسيط وآمن لإشعارات الرواتب
يعمل بدون مشاكل ترميز ومع النصوص العربية الأساسية
"""

from fpdf import FPDF
from datetime import datetime
from io import BytesIO

class SimpleSalaryPDF(FPDF):
    """فئة PDF بسيطة وآمنة للرواتب"""
    
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        
    def safe_text(self, text):
        """تحويل النص إلى نص آمن للـ PDF"""
        if not text:
            return ""
        
        # تحويل النص إلى string أولاً
        text_str = str(text)
        
        # إزالة الأحرف الخاصة التي تسبب مشاكل في الترميز
        # استبدال الأحرف العربية بنسخ بسيطة
        replacements = {
            # أحرف عربية خاصة
            'ً': '', 'ٌ': '', 'ٍ': '', 'َ': '', 'ُ': '', 'ِ': '', 'ّ': '', 'ْ': '',
            'ٓ': '', 'ٔ': '', 'ٕ': '', 'ٖ': '', 'ٗ': '', '٘ ': '', 'ٙ': '', 'ٚ': '',
            'ٛ': '', 'ٜ': '', 'ٝ': '', 'ٞ': '', 'ٟ': '', 'ٰ': '',
            # أحرف اتجاه النص
            '\u200f': '', '\u200e': '', '\u202a': '', '\u202b': '', '\u202c': '', '\u202d': '', '\u202e': '',
            # أحرف أخرى
            '​': '', '‌': '', '‍': '',  # zero width chars
            # استبدال أحرف عربية معقدة بأحرف بسيطة
            'ي': 'ي', 'ى': 'ى', 'ة': 'ة', 'أ': 'ا', 'إ': 'ا', 'آ': 'ا', 'ء': 'ء',
            'ؤ': 'و', 'ئ': 'ي'
        }
        
        # تطبيق الاستبدالات
        for old, new in replacements.items():
            text_str = text_str.replace(old, new)
        
        # فلترة الأحرف المسموحة فقط
        allowed_chars = []
        for char in text_str:
            # أحرف عربية أساسية
            if '\u0600' <= char <= '\u06FF':
                # تحقق من الأحرف الأساسية فقط
                if char in 'ابتثجحخدذرزسشصضطظعغفقكلمنهوي':
                    allowed_chars.append(char)
                else:
                    allowed_chars.append(' ')
            # أحرف إنجليزية وأرقام ورموز أساسية
            elif char.isalnum() or char in ' .-_:()[]{}/@#$%^&*+=<>?!,;':
                allowed_chars.append(char)
            else:
                allowed_chars.append(' ')
        
        result = ''.join(allowed_chars)
        
        # تنظيف المسافات الزائدة
        result = ' '.join(result.split())
        
        return result[:100]  # تحديد الطول لتجنب مشاكل
    
    def safe_cell(self, w, h, txt='', border=0, ln=0, align='', fill=False):
        """خلية آمنة مع معالجة الأخطاء"""
        try:
            safe_txt = self.safe_text(txt)
            self.cell(w, h, safe_txt, border, ln, align, fill)
        except Exception:
            self.cell(w, h, '[TEXT ERROR]', border, ln, align, fill)

def create_simple_arabic_salary_pdf(salary):
    """
    إنشاء إشعار راتب بسيط وآمن
    
    Args:
        salary: كائن Salary يحتوي على بيانات الراتب
        
    Returns:
        bytes: ملف PDF كـ bytes
    """
    try:
        pdf = SimpleSalaryPDF()
        pdf.add_page()
        
        # الرأس
        pdf.set_fill_color(41, 128, 185)  # أزرق
        pdf.rect(0, 0, 210, 30, 'F')
        
        # شعار الشركة (مربع أخضر)
        pdf.set_fill_color(46, 204, 113)
        pdf.rect(15, 8, 15, 15, 'F')
        
        # نص الشعار
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Arial', 'B', 8)
        pdf.set_xy(17, 13)
        pdf.safe_cell(11, 5, 'NUZUM', 0, 0, 'C')
        
        # اسم الشركة
        pdf.set_font('Arial', 'B', 14)
        pdf.set_xy(35, 10)
        pdf.safe_cell(80, 6, 'NUZUM COMPANY LTD', 0, 1, 'L')
        
        pdf.set_font('Arial', '', 10)
        pdf.set_xy(35, 18)
        pdf.safe_cell(80, 6, 'Employee Management System', 0, 1, 'L')
        
        # العنوان الرئيسي
        pdf.set_font('Arial', 'B', 16)
        pdf.set_xy(130, 12)
        pdf.safe_cell(60, 8, 'اشعار راتب للموظف', 0, 1, 'R')
        
        # التاريخ
        pdf.set_font('Arial', '', 10)
        pdf.set_xy(130, 22)
        pdf.safe_cell(60, 6, f'التاريخ: {datetime.now().strftime("%Y-%m-%d")}', 0, 1, 'R')
        
        # استعادة لون النص الأسود
        pdf.set_text_color(0, 0, 0)
        pdf.ln(10)
        
        # معلومات الموظف
        pdf.set_fill_color(240, 248, 255)
        pdf.set_font('Arial', 'B', 12)
        pdf.safe_cell(0, 8, 'معلومات الموظف', 1, 1, 'C', True)
        
        pdf.set_font('Arial', '', 11)
        
        # جدول المعلومات
        info_data = [
            ('اسم الموظف', str(salary.employee.name)),
            ('رقم الموظف', str(salary.employee.employee_id)),
            ('المسمى الوظيفي', str(salary.employee.job_title)),
            ('القسم', str(salary.employee.department.name) if salary.employee.department else 'غير محدد'),
        ]
        
        for i, (label, value) in enumerate(info_data):
            fill_color = (248, 249, 250) if i % 2 == 0 else (255, 255, 255)
            pdf.set_fill_color(*fill_color)
            
            pdf.safe_cell(60, 8, label, 1, 0, 'R', True)
            pdf.safe_cell(130, 8, value, 1, 1, 'L', True)
        
        pdf.ln(10)
        
        # تفاصيل الراتب
        pdf.set_fill_color(52, 152, 219)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Arial', 'B', 12)
        pdf.safe_cell(0, 8, 'تفاصيل الراتب', 1, 1, 'C', True)
        
        # رأس جدول الراتب
        pdf.safe_cell(120, 8, 'البيان', 1, 0, 'C', True)
        pdf.safe_cell(70, 8, 'المبلغ (ريال)', 1, 1, 'C', True)
        
        # استعادة لون النص
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Arial', '', 11)
        
        # بيانات الراتب
        salary_data = [
            ('الراتب الاساسي', float(salary.basic_salary)),
            ('البدلات', float(salary.allowances)),
            ('المكافآت', float(salary.bonus)),
        ]
        
        for i, (item, amount) in enumerate(salary_data):
            fill_color = (248, 249, 250) if i % 2 == 0 else (255, 255, 255)
            pdf.set_fill_color(*fill_color)
            
            pdf.safe_cell(120, 8, item, 1, 0, 'R', True)
            pdf.safe_cell(70, 8, f'{amount:,.2f}', 1, 1, 'C', True)
        
        # إجمالي المستحقات
        total_earnings = float(salary.basic_salary) + float(salary.allowances) + float(salary.bonus)
        pdf.set_fill_color(230, 247, 255)
        pdf.set_font('Arial', 'B', 11)
        pdf.safe_cell(120, 8, 'اجمالي المستحقات', 1, 0, 'R', True)
        pdf.safe_cell(70, 8, f'{total_earnings:,.2f}', 1, 1, 'C', True)
        
        # الخصومات
        pdf.set_fill_color(255, 245, 245)
        pdf.set_font('Arial', '', 11)
        pdf.safe_cell(120, 8, 'الخصومات', 1, 0, 'R', True)
        pdf.safe_cell(70, 8, f'{float(salary.deductions):,.2f}', 1, 1, 'C', True)
        
        # صافي الراتب
        pdf.set_fill_color(46, 204, 113)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Arial', 'B', 14)
        pdf.safe_cell(120, 12, 'صافي الراتب', 1, 0, 'R', True)
        pdf.safe_cell(70, 12, f'{float(salary.net_salary):,.2f}', 1, 1, 'C', True)
        
        # استعادة اللون الأسود
        pdf.set_text_color(0, 0, 0)
        pdf.ln(15)
        
        # الملاحظات
        if salary.notes:
            pdf.set_font('Arial', 'B', 11)
            pdf.safe_cell(0, 6, 'ملاحظات:', 0, 1, 'R')
            pdf.set_font('Arial', '', 10)
            notes = str(salary.notes)[:100] + ('...' if len(str(salary.notes)) > 100 else '')
            pdf.safe_cell(0, 8, notes, 1, 1, 'R')
            pdf.ln(5)
        
        # التذييل
        pdf.set_font('Arial', '', 9)
        pdf.set_text_color(100, 100, 100)
        
        # معلومات الإصدار
        month = int(salary.month) if not isinstance(salary.month, int) else salary.month
        year = str(salary.year)
        notification_id = f'رقم الاشعار: SAL-{salary.id}-{year}-{month:02d}'
        pdf.safe_cell(0, 6, notification_id, 0, 1, 'C')
        
        issue_date = f'تاريخ الاصدار: {datetime.now().strftime("%Y-%m-%d")}'
        pdf.safe_cell(0, 6, issue_date, 0, 1, 'C')
        
        # خط فاصل
        pdf.ln(8)
        pdf.set_draw_color(200, 200, 200)
        pdf.line(20, pdf.get_y(), 190, pdf.get_y())
        
        # إرجاع PDF آمن
        output = BytesIO()
        
        try:
            pdf_content = pdf.output(dest='S')
            
            # معالجة آمنة للبيانات
            if isinstance(pdf_content, bytes):
                output.write(pdf_content)
            else:
                # تحويل آمن لـ bytes
                content_str = str(pdf_content)
                # استبدال الأحرف الخاصة
                safe_content = content_str.encode('latin-1', errors='replace')
                output.write(safe_content)
                
        except Exception as e:
            # في حالة فشل الترميز، إنشاء PDF بسيط جداً
            print(f"خطأ في إنشاء PDF: {str(e)}")
            return create_emergency_pdf(salary)
        
        output.seek(0)
        return output.getvalue()
        
    except Exception as e:
        print(f"خطأ عام في إنشاء PDF: {str(e)}")
        return create_emergency_pdf(salary)

def create_emergency_pdf(salary):
    """PDF طوارئ بسيط جداً"""
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        
        pdf.cell(0, 10, 'SALARY NOTIFICATION', 0, 1, 'C')
        pdf.ln(10)
        
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
        
        output = BytesIO()
        pdf_content = pdf.output(dest='S')
        
        if isinstance(pdf_content, str):
            pdf_content = pdf_content.encode('latin-1', errors='replace')
        output.write(pdf_content)
        output.seek(0)
        
        return output.getvalue()
        
    except Exception:
        # في حالة فشل كل شيء، إرجاع بيانات فارغة
        return b'PDF_CREATION_FAILED'