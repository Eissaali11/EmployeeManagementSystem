"""
مولد PDF احترافي للرواتب مع دعم كامل للنصوص العربية
تصميم محسن وعرض صحيح للبيانات
"""

from fpdf import FPDF
from datetime import datetime
import arabic_reshaper
from bidi.algorithm import get_display
import os
from io import BytesIO

class ProfessionalArabicSalaryPDF(FPDF):
    """PDF احترافي مع دعم النصوص العربية"""
    
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=15)
        # محاولة إضافة الخط العربي
        self.add_arabic_font()
        
    def add_arabic_font(self):
        """إضافة الخط العربي - نفس الخط المستخدم في نظام التسليم والاستلام"""
        try:
            # تجربة المسارات المختلفة للخط العربي
            font_paths = [
                os.path.join('static', 'fonts', 'beIN Normal .ttf'),  # نفس الخط المستخدم في نظام التسليم
                os.path.join('static', 'fonts', 'beIN-Normal.ttf'),
                os.path.join('static', 'fonts', 'Tajawal-Regular.ttf'),
                os.path.join('static', 'fonts', 'Cairo.ttf'),
                os.path.join('utils', 'beIN-Normal.ttf'),
                'Cairo.ttf'  # الخط الموجود في المجلد الجذر
            ]
            
            for font_path in font_paths:
                if os.path.exists(font_path):
                    try:
                        self.add_font('Arabic', '', font_path, uni=True)
                        self.arabic_font_available = True
                        self.selected_font_path = font_path
                        print(f"استخدام خط: {font_path}")
                        return
                    except Exception as e:
                        print(f"فشل في تحميل الخط {font_path}: {e}")
                        continue
            
            # إذا لم نجد أي خط، استخدام الخط الافتراضي
            self.arabic_font_available = False
            self.selected_font_path = None
            print("لم يتم العثور على خط عربي، سيتم استخدام الخط الافتراضي")
            
        except Exception as e:
            print(f"خطأ في إضافة الخط العربي: {e}")
            self.arabic_font_available = False
            
    def reshape_arabic(self, text):
        """تحويل النص العربي للعرض الصحيح"""
        try:
            if not text:
                return ""
            text_str = str(text)
            # تحويل النص العربي
            reshaped_text = arabic_reshaper.reshape(text_str)
            bidi_text = get_display(reshaped_text)
            return bidi_text
        except Exception:
            return str(text) if text else ""
    
    def safe_cell(self, w, h, txt='', border=0, ln=0, align='', fill=False):
        """خلية آمنة مع دعم النصوص العربية"""
        try:
            if self.arabic_font_available:
                # استخدام الخط العربي
                arabic_txt = self.reshape_arabic(txt)
                self.cell(w, h, arabic_txt, border, ln, align, fill)
            else:
                # استخدام النص كما هو مع الخط الافتراضي
                self.cell(w, h, str(txt), border, ln, align, fill)
        except Exception:
            # في حالة الخطأ، استخدام نص بديل
            try:
                self.cell(w, h, str(txt)[:50], border, ln, align, fill)
            except:
                self.cell(w, h, '[النص]', border, ln, align, fill)

def create_professional_arabic_salary_pdf(salary):
    """
    إنشاء إشعار راتب احترافي مع دعم كامل للعربية
    """
    try:
        pdf = ProfessionalArabicSalaryPDF()
        pdf.add_page()
        
        # إعداد الخط الأساسي
        if pdf.arabic_font_available:
            pdf.set_font('Arabic', '', 12)
        else:
            pdf.set_font('Arial', '', 12)
        
        # === الرأس الاحترافي ===
        # خلفية الرأس
        pdf.set_fill_color(41, 128, 185)  # أزرق احترافي
        pdf.rect(0, 0, 210, 40, 'F')
        
        # شعار الشركة
        try:
            logo_path = os.path.join('static', 'images', 'logo_new.png')
            if os.path.exists(logo_path):
                pdf.image(logo_path, x=15, y=8, w=25, h=25)
            else:
                # مربع بديل للشعار
                pdf.set_fill_color(52, 152, 219)
                pdf.rect(15, 8, 25, 25, 'F')
                pdf.set_text_color(255, 255, 255)
                pdf.set_font('Arial', 'B', 16)
                pdf.set_xy(18, 18)
                pdf.cell(19, 8, 'نُظم', 0, 0, 'C')
        except Exception:
            # في حالة عدم وجود شعار
            pdf.set_fill_color(52, 152, 219)
            pdf.rect(15, 8, 25, 25, 'F')
        
        # اسم الشركة
        pdf.set_text_color(255, 255, 255)
        if pdf.arabic_font_available:
            pdf.set_font('Arabic', '', 16)
        else:
            pdf.set_font('Arial', 'B', 16)
        pdf.set_xy(45, 12)
        pdf.safe_cell(100, 8, 'نُظم - نظام إدارة متكامل', 0, 1, 'L')
        
        # عنوان المستند
        if pdf.arabic_font_available:
            pdf.set_font('Arabic', '', 18)
        else:
            pdf.set_font('Arial', 'B', 18)
        pdf.set_xy(120, 10)
        pdf.safe_cell(70, 10, 'إشعار راتب', 0, 1, 'R')
        
        # التاريخ
        if pdf.arabic_font_available:
            pdf.set_font('Arabic', '', 10)
        else:
            pdf.set_font('Arial', '', 10)
        pdf.set_xy(120, 25)
        date_str = datetime.now().strftime('%Y/%m/%d')
        pdf.safe_cell(70, 6, f'التاريخ: {date_str}', 0, 1, 'R')
        
        # استعادة اللون الأسود
        pdf.set_text_color(0, 0, 0)
        pdf.ln(15)
        
        # === معلومات الموظف ===
        pdf.set_fill_color(240, 248, 255)  # أزرق فاتح
        if pdf.arabic_font_available:
            pdf.set_font('Arabic', '', 14)
        else:
            pdf.set_font('Arial', 'B', 14)
        pdf.safe_cell(0, 10, 'معلومات الموظف', 1, 1, 'C', True)
        
        # بيانات الموظف في جدول
        if pdf.arabic_font_available:
            pdf.set_font('Arabic', '', 12)
        else:
            pdf.set_font('Arial', '', 12)
        
        # الاسم
        pdf.set_fill_color(250, 250, 250)
        employee_name = salary.employee.name if salary.employee else 'غير محدد'
        pdf.safe_cell(95, 8, employee_name, 1, 0, 'L')
        pdf.safe_cell(95, 8, 'اسم الموظف', 1, 1, 'R', True)
        
        # رقم الموظف
        employee_id = salary.employee.employee_id if salary.employee else 'غير محدد'
        pdf.safe_cell(95, 8, str(employee_id), 1, 0, 'L')
        pdf.safe_cell(95, 8, 'رقم الموظف', 1, 1, 'R', True)
        
        # القسم
        try:
            department_name = salary.employee.departments[0].name if salary.employee and salary.employee.departments else 'غير محدد'
        except:
            department_name = 'غير محدد'
        pdf.safe_cell(95, 8, department_name, 1, 0, 'L')
        pdf.safe_cell(95, 8, 'القسم', 1, 1, 'R', True)
        
        pdf.ln(10)
        
        # === تفاصيل الراتب ===
        pdf.set_fill_color(240, 248, 255)
        if pdf.arabic_font_available:
            pdf.set_font('Arabic', '', 14)
        else:
            pdf.set_font('Arial', 'B', 14)
        pdf.safe_cell(0, 10, 'تفاصيل الراتب', 1, 1, 'C', True)
        
        # الشهر والسنة
        if pdf.arabic_font_available:
            pdf.set_font('Arabic', '', 12)
        else:
            pdf.set_font('Arial', '', 12)
        
        # أسماء الأشهر بالعربية
        month_names = {
            1: 'يناير', 2: 'فبراير', 3: 'مارس', 4: 'أبريل',
            5: 'مايو', 6: 'يونيو', 7: 'يوليو', 8: 'أغسطس',
            9: 'سبتمبر', 10: 'أكتوبر', 11: 'نوفمبر', 12: 'ديسمبر'
        }
        
        month = int(salary.month) if salary.month else 1
        year = int(salary.year) if salary.year else datetime.now().year
        month_name = month_names.get(month, f'الشهر {month}')
        
        pdf.set_fill_color(250, 250, 250)
        pdf.safe_cell(95, 8, f'{month_name} {year}', 1, 0, 'L')
        pdf.safe_cell(95, 8, 'فترة الراتب', 1, 1, 'R', True)
        
        # الراتب الأساسي
        basic_salary = f'{float(salary.basic_salary or 0):,.2f} ريال'
        pdf.safe_cell(95, 8, basic_salary, 1, 0, 'L')
        pdf.safe_cell(95, 8, 'الراتب الأساسي', 1, 1, 'R', True)
        
        # البدلات
        allowances = f'{float(salary.allowances or 0):,.2f} ريال'
        pdf.safe_cell(95, 8, allowances, 1, 0, 'L')
        pdf.safe_cell(95, 8, 'البدلات', 1, 1, 'R', True)
        
        # الخصومات
        deductions = f'{float(salary.deductions or 0):,.2f} ريال'
        pdf.safe_cell(95, 8, deductions, 1, 0, 'L')
        pdf.safe_cell(95, 8, 'الخصومات', 1, 1, 'R', True)
        
        # صافي الراتب (مميز)
        pdf.set_fill_color(76, 175, 80)  # أخضر
        pdf.set_text_color(255, 255, 255)  # أبيض
        if pdf.arabic_font_available:
            pdf.set_font('Arabic', '', 14)
        else:
            pdf.set_font('Arial', 'B', 14)
        net_salary = f'{float(salary.net_salary or 0):,.2f} ريال'
        pdf.safe_cell(95, 10, net_salary, 1, 0, 'L', True)
        pdf.safe_cell(95, 10, 'صافي الراتب', 1, 1, 'R', True)
        
        # استعادة الألوان
        pdf.set_text_color(0, 0, 0)
        pdf.set_fill_color(255, 255, 255)
        
        # === الملاحظات (إن وجدت) ===
        if salary.notes:
            pdf.ln(10)
            pdf.set_fill_color(255, 252, 230)  # أصفر فاتح
            if pdf.arabic_font_available:
                pdf.set_font('Arabic', '', 12)
            else:
                pdf.set_font('Arial', 'B', 12)
            pdf.safe_cell(0, 8, 'ملاحظات', 1, 1, 'R', True)
            
            if pdf.arabic_font_available:
                pdf.set_font('Arabic', '', 10)
            else:
                pdf.set_font('Arial', '', 10)
            pdf.set_fill_color(255, 255, 255)
            notes_text = str(salary.notes)[:200] + ('...' if len(str(salary.notes)) > 200 else '')
            pdf.safe_cell(0, 15, notes_text, 1, 1, 'R')
        
        # === التذييل ===
        pdf.ln(20)
        
        # خط فاصل
        pdf.set_draw_color(200, 200, 200)
        pdf.line(20, pdf.get_y(), 190, pdf.get_y())
        pdf.ln(5)
        
        # معلومات الإصدار
        if pdf.arabic_font_available:
            pdf.set_font('Arabic', '', 9)
        else:
            pdf.set_font('Arial', '', 9)
        pdf.set_text_color(100, 100, 100)
        
        # رقم الإشعار
        notification_id = f'رقم الإشعار: SAL-{salary.id}-{year}-{month:02d}'
        pdf.safe_cell(0, 6, notification_id, 0, 1, 'C')
        
        # تاريخ الإصدار
        issue_date = f'تاريخ الإصدار: {datetime.now().strftime("%d/%m/%Y %H:%M")}'
        pdf.safe_cell(0, 6, issue_date, 0, 1, 'C')
        
        # رسالة أسفل الصفحة
        pdf.ln(5)
        pdf.safe_cell(0, 6, 'هذا المستند مُولد إلكترونياً من نظام نُظم لإدارة الموظفين', 0, 1, 'C')
        
        # معلومات الخط المُستخدم
        if hasattr(pdf, 'selected_font_path') and pdf.selected_font_path:
            pdf.ln(2)
            pdf.set_font('Arial', '', 6)
            pdf.set_text_color(150, 150, 150)
            font_name = os.path.basename(pdf.selected_font_path)
            pdf.cell(0, 4, f'Font: {font_name}', 0, 1, 'C')
        
        # إرجاع PDF كـ bytes
        output = BytesIO()
        pdf_content = pdf.output(dest='S')
        
        # التعامل مع أنواع البيانات المختلفة
        if isinstance(pdf_content, bytes):
            output.write(pdf_content)
        elif isinstance(pdf_content, bytearray):
            output.write(bytes(pdf_content))
        elif isinstance(pdf_content, str):
            output.write(pdf_content.encode('latin1'))
        else:
            # محاولة تحويل إلى bytes
            output.write(bytes(pdf_content))
            
        output.seek(0)
        return output.getvalue()
        
    except Exception as e:
        print(f"خطأ في إنشاء PDF الراتب: {str(e)}")
        # في حالة الفشل، إنشاء PDF بسيط جداً
        return create_emergency_salary_pdf(salary)

def create_emergency_salary_pdf(salary):
    """إنشاء PDF طوارئ بسيط جداً"""
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        
        # عنوان
        pdf.cell(0, 10, 'SALARY NOTIFICATION', 0, 1, 'C')
        pdf.ln(10)
        
        # معلومات أساسية
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 8, f'Employee: {salary.employee.name if salary.employee else "N/A"}', 0, 1)
        pdf.cell(0, 8, f'Month/Year: {salary.month}/{salary.year}', 0, 1)
        pdf.cell(0, 8, f'Basic Salary: {salary.basic_salary or 0:,.2f} SAR', 0, 1)
        pdf.cell(0, 8, f'Allowances: {salary.allowances or 0:,.2f} SAR', 0, 1)
        pdf.cell(0, 8, f'Deductions: {salary.deductions or 0:,.2f} SAR', 0, 1)
        pdf.ln(5)
        
        # صافي الراتب
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, f'Net Salary: {salary.net_salary or 0:,.2f} SAR', 0, 1)
        
        # تاريخ الإصدار
        pdf.ln(10)
        pdf.set_font('Arial', '', 8)
        pdf.cell(0, 5, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 1, 'C')
        
        # إرجاع PDF
        output = BytesIO()
        pdf_content = pdf.output(dest='S')
        
        # التعامل مع أنواع البيانات المختلفة
        if isinstance(pdf_content, bytes):
            output.write(pdf_content)
        elif isinstance(pdf_content, bytearray):
            output.write(bytes(pdf_content))
        elif isinstance(pdf_content, str):
            output.write(pdf_content.encode('latin1'))
        else:
            output.write(bytes(pdf_content))
            
        output.seek(0)
        return output.getvalue()
        
    except Exception as e:
        print(f"حتى PDF الطوارئ فشل: {str(e)}")
        raise Exception("فشل تام في إنشاء PDF")