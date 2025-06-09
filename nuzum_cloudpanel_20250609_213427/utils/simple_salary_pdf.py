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
    إنشاء إشعار راتب احترافي يعمل في جميع البيئات
    
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
            1: 'يناير', 2: 'فبراير', 3: 'مارس', 4: 'أبريل',
            5: 'مايو', 6: 'يونيو', 7: 'يوليو', 8: 'أغسطس',
            9: 'سبتمبر', 10: 'أكتوبر', 11: 'نوفمبر', 12: 'ديسمبر'
        }
        
        month = int(salary.month) if not isinstance(salary.month, int) else salary.month
        month_name = month_names.get(month, f'الشهر {month}')
        year = str(salary.year)
        
        # شريط علوي ملون
        pdf.set_fill_color(41, 128, 185)  # أزرق احترافي
        pdf.rect(0, 0, 210, 25, 'F')
        
        # العنوان الرئيسي مع خلفية ملونة
        pdf.set_text_color(255, 255, 255)  # نص أبيض
        pdf.set_font('Arial', 'B', 20)
        pdf.ln(8)
        title_ar = pdf.reshape_arabic(f'إشعار راتب - {month_name} {year}')
        pdf.safe_cell(0, 10, title_ar, 0, 1, 'C')
        
        # استعادة لون النص الأسود
        pdf.set_text_color(0, 0, 0)
        pdf.ln(15)
        
        # صندوق معلومات الموظف
        pdf.set_fill_color(240, 248, 255)  # خلفية زرقاء فاتحة
        pdf.rect(15, pdf.get_y(), 180, 50, 'F')
        
        pdf.set_x(20)
        pdf.set_font('Arial', 'B', 14)
        pdf.safe_cell(0, 10, pdf.reshape_arabic('بيانات الموظف'), 0, 1, 'R')
        pdf.ln(2)
        
        # معلومات الموظف في صندوق
        pdf.set_font('Arial', '', 11)
        
        # الصف الأول - الاسم والرقم
        pdf.set_x(20)
        pdf.safe_cell(85, 8, pdf.reshape_arabic(f'الاسم: {salary.employee.name}'), 0, 0, 'R')
        pdf.safe_cell(85, 8, pdf.reshape_arabic(f'رقم الموظف: {salary.employee.employee_id}'), 0, 1, 'R')
        
        # الصف الثاني - المسمى والقسم
        pdf.set_x(20)
        pdf.safe_cell(85, 8, pdf.reshape_arabic(f'المسمى: {salary.employee.job_title}'), 0, 0, 'R')
        department_name = salary.employee.department.name if salary.employee.department else 'غير محدد'
        pdf.safe_cell(85, 8, pdf.reshape_arabic(f'القسم: {department_name}'), 0, 1, 'R')
        
        pdf.ln(15)
        
        # جدول الراتب الاحترافي
        pdf.set_font('Arial', 'B', 14)
        pdf.safe_cell(0, 10, pdf.reshape_arabic('تفاصيل الراتب'), 0, 1, 'C')
        pdf.ln(5)
        
        # رأس الجدول
        pdf.set_fill_color(52, 152, 219)  # أزرق
        pdf.set_text_color(255, 255, 255)  # نص أبيض
        pdf.set_font('Arial', 'B', 12)
        
        pdf.safe_cell(105, 10, pdf.reshape_arabic('البيان'), 1, 0, 'C', True)
        pdf.safe_cell(75, 10, pdf.reshape_arabic('المبلغ (ريال)'), 1, 1, 'C', True)
        
        # استعادة لون النص
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Arial', '', 11)
        
        # بيانات الجدول
        salary_items = [
            ('الراتب الأساسي', float(salary.basic_salary)),
            ('البدلات', float(salary.allowances)),
            ('المكافآت', float(salary.bonus)),
        ]
        
        # صفوف عادية
        for i, (label, amount) in enumerate(salary_items):
            fill_color = (248, 249, 250) if i % 2 == 0 else (255, 255, 255)
            pdf.set_fill_color(*fill_color)
            
            pdf.safe_cell(105, 8, pdf.reshape_arabic(label), 1, 0, 'R', True)
            pdf.safe_cell(75, 8, f'{amount:,.2f}', 1, 1, 'C', True)
        
        # إجمالي المستحقات
        total_earnings = float(salary.basic_salary) + float(salary.allowances) + float(salary.bonus)
        pdf.set_fill_color(230, 247, 255)
        pdf.set_font('Arial', 'B', 11)
        pdf.safe_cell(105, 8, pdf.reshape_arabic('إجمالي المستحقات'), 1, 0, 'R', True)
        pdf.safe_cell(75, 8, f'{total_earnings:,.2f}', 1, 1, 'C', True)
        
        # الخصومات
        pdf.set_fill_color(255, 245, 245)
        pdf.set_font('Arial', '', 11)
        pdf.safe_cell(105, 8, pdf.reshape_arabic('الخصومات'), 1, 0, 'R', True)
        pdf.safe_cell(75, 8, f'{float(salary.deductions):,.2f}', 1, 1, 'C', True)
        
        # صافي الراتب (مميز)
        pdf.set_fill_color(46, 204, 113)  # أخضر
        pdf.set_text_color(255, 255, 255)  # نص أبيض
        pdf.set_font('Arial', 'B', 14)
        pdf.safe_cell(105, 12, pdf.reshape_arabic('صافي الراتب'), 1, 0, 'R', True)
        pdf.safe_cell(75, 12, f'{float(salary.net_salary):,.2f}', 1, 1, 'C', True)
        
        # استعادة لون النص
        pdf.set_text_color(0, 0, 0)
        pdf.ln(15)
        
        # الملاحظات (إذا وجدت)
        if salary.notes:
            pdf.set_fill_color(255, 252, 240)  # خلفية صفراء فاتحة
            pdf.rect(15, pdf.get_y(), 180, 20, 'F')
            
            pdf.set_x(20)
            pdf.set_font('Arial', 'B', 12)
            pdf.safe_cell(0, 8, pdf.reshape_arabic('ملاحظات:'), 0, 1, 'R')
            
            pdf.set_x(20)
            pdf.set_font('Arial', '', 10)
            notes_text = str(salary.notes)[:150] + ('...' if len(str(salary.notes)) > 150 else '')
            pdf.safe_cell(0, 8, pdf.reshape_arabic(notes_text), 0, 1, 'R')
            pdf.ln(10)
        
        # التذييل
        pdf.ln(10)
        pdf.set_font('Arial', '', 9)
        pdf.set_text_color(100, 100, 100)  # رمادي
        
        # معلومات إضافية
        issue_date = f'تاريخ الإصدار: {datetime.now().strftime("%Y-%m-%d")}'
        pdf.safe_cell(0, 6, pdf.reshape_arabic(issue_date), 0, 1, 'C')
        
        notification_id = f'رقم الإشعار: SAL-{salary.id}-{year}-{month:02d}'
        pdf.safe_cell(0, 6, pdf.reshape_arabic(notification_id), 0, 1, 'C')
        
        # خط فاصل
        pdf.ln(10)
        pdf.set_draw_color(200, 200, 200)
        pdf.line(20, pdf.get_y(), 190, pdf.get_y())
        pdf.ln(10)
        
        # مساحة التوقيع
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Arial', '', 10)
        
        # توقيع على اليسار والتاريخ على اليمين
        y_pos = pdf.get_y()
        pdf.safe_cell(90, 6, pdf.reshape_arabic('التوقيع: ___________________'), 0, 0, 'L')
        pdf.safe_cell(90, 6, pdf.reshape_arabic('التاريخ: ___________________'), 0, 1, 'R')
        
        # إرجاع PDF كـ bytes
        output = BytesIO()
        
        try:
            # محاولة الحصول على PDF كـ bytes مباشرة
            pdf_content = pdf.output(dest='S')
            
            # التعامل مع أنواع البيانات المختلفة
            if isinstance(pdf_content, bytes):
                output.write(pdf_content)
            elif isinstance(pdf_content, bytearray):
                output.write(bytes(pdf_content))
            elif isinstance(pdf_content, str):
                # استخدام ترميز أكثر أماناً للنصوص العربية
                try:
                    pdf_content = pdf_content.encode('utf-8')
                except UnicodeEncodeError:
                    try:
                        pdf_content = pdf_content.encode('latin-1')
                    except UnicodeEncodeError:
                        # في حالة فشل جميع المحاولات، استخدام ترميز آمن
                        pdf_content = pdf_content.encode('utf-8', errors='replace')
                output.write(pdf_content)
            else:
                # تحويل إلى bytes بطريقة آمنة
                output.write(str(pdf_content).encode('utf-8', errors='replace'))
                
        except Exception as e:
            print(f"خطأ في ترميز PDF: {str(e)}")
            # في حالة فشل الترميز، استخدام PDF طوارئ
            return create_emergency_salary_pdf(salary)
        
        output.seek(0)
        return output.getvalue()
        
    except Exception as e:
        print(f"خطأ في إنشاء إشعار الراتب الاحترافي: {str(e)}")
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