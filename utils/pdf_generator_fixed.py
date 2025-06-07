"""
مكتبة جديدة لإنشاء ملفات PDF بدعم كامل للغة العربية
تستخدم FPDF مع معالجة صحيحة للنصوص العربية وإصلاح مشكلة BytesIO
"""

import os
from datetime import datetime
import arabic_reshaper
from bidi.algorithm import get_display
from fpdf import FPDF
from io import BytesIO

# تعريف فئة PDF العربية المحسنة
class ArabicPDF(FPDF):
    """فئة محسنة لإنشاء ملفات PDF باللغة العربية"""
    
    def __init__(self, orientation='P', unit='mm', format='A4'):
        """إنشاء كائن FPDF جديد بدعم كامل للغة العربية"""
        super().__init__(orientation=orientation, unit=unit, format=format)
        # إضافة الخط العربي (العادي والعريض)
        try:
            # مسار الخط العادي
            font_regular_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'fonts', 'Amiri-Regular.ttf')
            # مسار الخط العريض
            font_bold_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', 'fonts', 'Amiri-Bold.ttf')
            
            # التحقق من وجود الملفات
            if os.path.exists(font_regular_path) and os.path.exists(font_bold_path):
                # إضافة الخط العادي والعريض
                self.add_font('Arabic', '', font_regular_path, uni=True)
                self.add_font('Arabic', 'B', font_bold_path, uni=True)
                print("تم تحميل الخط العربي (العادي والعريض) بنجاح")
                self.set_font('Arabic', '', 14)
            else:
                # المسارات البديلة للخطوط
                font_regular_path = os.path.join('static', 'fonts', 'Amiri-Regular.ttf')
                font_bold_path = os.path.join('static', 'fonts', 'Amiri-Bold.ttf')
                
                if os.path.exists(font_regular_path) and os.path.exists(font_bold_path):
                    self.add_font('Arabic', '', font_regular_path, uni=True)
                    self.add_font('Arabic', 'B', font_bold_path, uni=True)
                    print("تم تحميل الخط العربي من المسار البديل بنجاح")
                    self.set_font('Arabic', '', 14)
                else:
                    # استخدام خط Tajawal كبديل إذا كان متاحًا
                    tajawal_regular = os.path.join('static', 'fonts', 'Tajawal-Regular.ttf')
                    tajawal_bold = os.path.join('static', 'fonts', 'Tajawal-Bold.ttf')
                    
                    if os.path.exists(tajawal_regular) and os.path.exists(tajawal_bold):
                        self.add_font('Arabic', '', tajawal_regular, uni=True)
                        self.add_font('Arabic', 'B', tajawal_bold, uni=True)
                        print("تم تحميل خط Tajawal كبديل")
                        self.set_font('Arabic', '', 14)
                    else:
                        # استخدام خط Arial كحل أخير
                        print("لم يتم العثور على الخطوط العربية، سيتم استخدام Arial")
                        self.set_font('Arial', '', 14)
        except Exception as e:
            print(f"تعذر تحميل الخط العربي: {str(e)}")
            # محاولة استخدام Arial مع تعطيل الخطوط الثقيلة
            self.set_font('Arial', '', 14)
        
        # تعيين الألوان الافتراضية
        self.primary_color = (29, 161, 142)  # اللون الأخضر للترويسة
        self.primary_color_light = (200, 230, 225)  # اللون الأخضر الفاتح
        self.secondary_color = (66, 66, 66)  # رمادي داكن للنص
        self.border_color = (200, 200, 200)  # لون رمادي فاتح للحدود
        self.background_color = (240, 240, 240)  # رمادي فاتح جدًا للخلفية
    
    def arabic_text(self, x, y, txt, align='L'):
        """طباعة نص عربي في الموضع المحدد مع دعم مناسب للغة العربية"""
        # معالجة النص العربي
        reshaped_text = arabic_reshaper.reshape(str(txt))
        bidi_text = get_display(reshaped_text)
        
        # تعيين موضع الطباعة
        self.set_xy(x, y)
        
        # طباعة النص مع المحاذاة المناسبة
        if align == 'R':  # محاذاة لليمين
            self.cell(0, 0, bidi_text, ln=0, align='L')
        elif align == 'C':  # توسيط
            self.cell(0, 0, bidi_text, ln=0, align='C')
        else:  # محاذاة لليسار (الافتراضي)
            self.cell(0, 0, bidi_text, ln=0, align='R')
    
    def add_page_with_header(self, title, logo_path=None):
        """إضافة صفحة جديدة مع ترويسة موحدة"""
        self.add_page()
        
        # إضافة شعار دائري للنظام
        center_x = 20
        center_y = 15
        radius = 10
        
        # رسم الدائرة الخارجية
        self.set_fill_color(30, 60, 114)  # اللون الأزرق الداكن
        self.ellipse(center_x, center_y, radius, radius, 'F')
        
        # إضافة نص نُظم في الدائرة
        self.set_font('Arabic', 'B', 14)
        self.set_text_color(255, 255, 255)  # لون أبيض للنص
        self.arabic_text(center_x - 4, center_y - 3, "نُظم")
        
        # إضافة عنوان التقرير
        self.set_font('Arabic', 'B', 16)
        self.set_text_color(*self.primary_color)
        self.arabic_text(105, 20, title, 'C')
        
        # إضافة خط أفقي أسفل الترويسة
        self.set_draw_color(*self.primary_color)
        self.set_line_width(0.5)
        self.line(10, 30, 200, 30)
        
        # إعادة ضبط الخط والألوان
        self.set_font('Arabic', '', 12)
        self.set_text_color(*self.secondary_color)
        self.set_draw_color(0, 0, 0)
    
    def rounded_rect(self, x, y, w, h, r, style='', border_color=None, fill_color=None):
        """رسم مستطيل بحواف مستديرة"""
        if border_color:
            self.set_draw_color(*border_color)
        if fill_color:
            self.set_fill_color(*fill_color)
        
        self.rounded_corner_rect(x, y, w, h, r, style)
        
        # إعادة تعيين الألوان الافتراضية
        self.set_draw_color(0)
        self.set_fill_color(255)
    
    def rounded_corner_rect(self, x, y, w, h, r, style=''):
        """رسم مستطيل بزوايا مستديرة"""
        # تحديد أسلوب الرسم
        draw = 'D' in style.upper()
        fill = 'F' in style.upper()
        
        # رسم الشكل
        k = self.k
        hp = self.h
        
        # تحويل مليمترات إلى نقاط
        x *= k
        y = (hp - y) * k
        w *= k
        h *= k
        r *= k
        
        # بدء مسار الرسم
        op = 'n' if not draw and not fill else 'S' if draw and not fill else 'f' if not draw and fill else 'B'
        my_path = f'{x + r:.2f} {y:.2f} m'
        
        # الحواف المستديرة - الزاوية اليمنى العليا
        x_plus_w = x + w
        y_minus_h = y - h
        my_path += f' {x_plus_w - r:.2f} {y:.2f} l'
        my_path += f' {x_plus_w:.2f} {y - r:.2f} l'
        
        # الجانب الأيمن
        my_path += f' {x_plus_w:.2f} {y_minus_h + r:.2f} l'
        
        # الزاوية اليمنى السفلية
        my_path += f' {x_plus_w - r:.2f} {y_minus_h:.2f} l'
        
        # الجانب السفلي
        my_path += f' {x + r:.2f} {y_minus_h:.2f} l'
        
        # الزاوية اليسرى السفلية
        my_path += f' {x:.2f} {y_minus_h + r:.2f} l'
        
        # الجانب الأيسر
        my_path += f' {x:.2f} {y - r:.2f} l'
        
        # الزاوية اليسرى العليا
        my_path += f' {x + r:.2f} {y:.2f} l'
        
        # تنفيذ عملية الرسم
        self._out(f'{my_path} {op}')
    
    def add_page_number(self):
        """إضافة رقم الصفحة في تذييل الصفحة"""
        self.set_y(-15)
        self.set_font('Arabic', '', 8)
        self.set_text_color(128)
        page_number = f"صفحة {self.page_no()}"
        self.arabic_text(105, self.get_y(), page_number, 'C')
        
    def add_company_header(self, title, subtitle=None):
        """إضافة ترويسة الشركة"""
        # استخدام شعار نُظم الدائري
        logo_path = os.path.join(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static").static, 'images', 'logo_new.png')
        if os.path.exists(logo_path):
            # إضافة صورة الشعار
            try:
                self.image(logo_path, x=20, y=10, w=20, h=20)
            except Exception as e:
                print(f"خطأ في إضافة الشعار: {str(e)}")
                # إضافة شعار دائري بديل للنظام
                center_x = 20
                center_y = 20
                radius = 10
                
                # رسم الدائرة الخارجية
                self.set_fill_color(30, 60, 114)  # اللون الأزرق الداكن
                self.ellipse(center_x, center_y, radius, radius, 'F')
                
                # إضافة نص نُظم في الدائرة
                self.set_font('Arabic', 'B', 14)
                self.set_text_color(255, 255, 255)  # لون أبيض للنص
                self.arabic_text(center_x - 4, center_y - 3, "نُظم")
        else:
            # إضافة شعار دائري بديل للنظام
            center_x = 20
            center_y = 20
            radius = 10
            
            # رسم الدائرة الخارجية
            self.set_fill_color(30, 60, 114)  # اللون الأزرق الداكن
            self.ellipse(center_x, center_y, radius, radius, 'F')
            
            # إضافة نص نُظم في الدائرة
            self.set_font('Arabic', 'B', 14)
            self.set_text_color(255, 255, 255)  # لون أبيض للنص
            self.arabic_text(center_x - 4, center_y - 3, "نُظم")
        
        # عنوان التقرير
        self.set_font('Arabic', 'B', 18)
        self.set_text_color(*self.primary_color)
        self.arabic_text(140, 20, "نُظم - نظام إدارة متكامل", 'C')
        
        # العنوان الفرعي
        if subtitle:
            self.set_font('Arabic', 'B', 14)
            self.set_text_color(*self.secondary_color)
            self.arabic_text(140, 30, subtitle, 'C')
            
        # خط فاصل
        self.set_draw_color(*self.primary_color)
        self.set_line_width(0.5)
        self.line(10, 35, 287, 35)
        
        return 35  # إرجاع موضع Y الجديد بعد الترويسة


# تحديث طريقة إنشاء PDF ليكون متوافقًا مع الإصدارات الحديثة من FPDF
def create_pdf_bytes(pdf_function, *args, **kwargs):
    """
    دالة مساعدة لإنشاء ملف PDF وإرجاعه كبيانات ثنائية
    
    Args:
        pdf_function: دالة إنشاء ملف PDF
        *args, **kwargs: المعاملات التي ستمرر إلى الدالة
        
    Returns:
        bytes يحتوي على ملف PDF
    """
    try:
        # استدعاء دالة إنشاء PDF مع المعاملات المناسبة
        pdf = pdf_function(*args, **kwargs)
        
        # تأكد من أن ما تم إرجاعه هو كائن FPDF
        if not isinstance(pdf, FPDF):
            print("خطأ: لم يتم إرجاع كائن FPDF من دالة إنشاء PDF")
            return None
        
        # الطريقة المحسنة للتعامل مع ملفات PDF مع النصوص العربية
        # استخدام طريقة output_to_bytes الجديدة من مكتبة FPDF التي تدعم UTF-8
        from io import BytesIO
        buffer = BytesIO()
        # حفظ الملف كـ binary مباشرة لتجنب مشاكل الترميز
        dest_file = "temp_pdf.pdf"
        pdf.output(dest_file)
        # قراءة الملف المؤقت كبيانات ثنائية
        import os
        with open(dest_file, 'rb') as f:
            binary_data = f.read()
        # حذف الملف المؤقت
        os.remove(dest_file)
        return binary_data
    except Exception as e:
        print(f"خطأ في إنشاء ملف PDF: {str(e)}")
        raise e


# دالة مساعدة لإنشاء تقرير راتب واحد
def create_salary_report_pdf(salaries_data, month, year):
    """
    إنشاء تقرير رواتب كملف PDF
    
    Args:
        salaries_data: قائمة بكائنات Salary
        month: رقم الشهر أو اسم الشهر
        year: السنة
        
    Returns:
        كائن FPDF
    """
    try:
        # تحويل المدخلات إلى النوع المناسب
        month_str = str(month)
        year_str = str(year)
        
        # إنشاء PDF جديد في الوضع الأفقي
        pdf = ArabicPDF('L')
        pdf.add_page()
        
        # إضافة ترويسة الشركة
        subtitle = "تقرير الرواتب - شهر " + str(month_str) + " " + str(year_str)
        pdf.add_company_header("نُظم", subtitle)
        
        # إضافة إطار للمستند
        pdf.set_draw_color(*pdf.primary_color)
        pdf.set_line_width(0.3)
        pdf.rect(10.0, 40.0, 277.0, 150.0)  # إطار خارجي للتقرير
        
        # إنشاء جدول الرواتب
        # تعيين عناوين الأعمدة
        headers = ["م", "اسم الموظف", "الرقم الوظيفي", "الراتب الأساسي", "البدلات", "المكافآت", "الخصومات", "صافي الراتب"]
        
        # تعيين عرض كل عمود (مجموع العروض = 277)
        col_widths = [10, 65, 25, 35, 35, 35, 35, 37]
        
        # بداية جدول الرواتب
        y_start = 50
        pdf.set_y(y_start)
        
        # رسم خلفية رأس الجدول
        pdf.set_fill_color(*pdf.primary_color)
        pdf.rect(10, y_start, 277, 10, style='F')
        
        # كتابة عناوين الأعمدة
        pdf.set_font('Arial', 'B', 10)
        pdf.set_text_color(255, 255, 255)  # لون النص أبيض
        
        # كتابة رأس الجدول
        x_pos = 10
        for i, header in enumerate(headers):
            pdf.arabic_text(x_pos + col_widths[i]/2, y_start + 5, header, 'C')
            x_pos += col_widths[i]
        
        # بداية صفوف البيانات
        y_pos = y_start + 10
        pdf.set_text_color(0, 0, 0)  # لون النص أسود
        pdf.set_font('Arial', '', 10)
        
        # حساب المجاميع
        total_basic = 0
        total_allowances = 0
        total_bonus = 0
        total_deductions = 0
        total_net = 0
        
        # إضافة صفوف البيانات
        for idx, salary in enumerate(salaries_data):
            # تناوب لون الخلفية
            if idx % 2 == 0:
                pdf.set_fill_color(240, 240, 240)
                pdf.rect(10, y_pos, 277, 8, style='F')
            
            # كتابة بيانات الصف
            x_pos = 10
            
            # التعامل مع كائن Salary بطريقة صحيحة (الوصول المباشر للخصائص)
            employee_name = salary.employee.name if hasattr(salary, 'employee') else ''
            employee_id = salary.employee.employee_id if hasattr(salary, 'employee') else ''
            basic_salary = salary.basic_salary if hasattr(salary, 'basic_salary') else 0
            allowances = salary.allowances if hasattr(salary, 'allowances') else 0
            bonus = salary.bonus if hasattr(salary, 'bonus') else 0
            deductions = salary.deductions if hasattr(salary, 'deductions') else 0
            net_salary = salary.net_salary if hasattr(salary, 'net_salary') else 0
            
            row_data = [
                str(idx + 1),
                employee_name,
                employee_id,
                "{:,.2f}".format(float(basic_salary)),
                "{:,.2f}".format(float(allowances)),
                "{:,.2f}".format(float(bonus)),
                "{:,.2f}".format(float(deductions)),
                "{:,.2f}".format(float(net_salary))
            ]
            
            # تجميع المبالغ
            total_basic += float(basic_salary)
            total_allowances += float(allowances)
            total_bonus += float(bonus)
            total_deductions += float(deductions)
            total_net += float(net_salary)
            
            # كتابة كل خلية
            for i, cell_data in enumerate(row_data):
                align = 'R' if i >= 3 else 'C'  # محاذاة المبالغ إلى اليمين
                pdf.arabic_text(x_pos + col_widths[i]/2, y_pos + 4, cell_data, align)
                x_pos += col_widths[i]
            
            # الانتقال للصف التالي
            y_pos += 8
            
            # إذا وصلنا إلى نهاية الصفحة، نضيف صفحة جديدة
            if y_pos > 180:
                pdf.add_page()
                
                # نعيد رسم رأس الجدول
                y_pos = 40
                pdf.set_fill_color(*pdf.primary_color)
                pdf.rect(10, y_pos, 277, 10, style='F')
                
                # كتابة عناوين الأعمدة
                pdf.set_font('Arial', 'B', 10)
                pdf.set_text_color(255, 255, 255)
                
                x_pos = 10
                for i, header in enumerate(headers):
                    pdf.arabic_text(x_pos + col_widths[i]/2, y_pos + 5, header, 'C')
                    x_pos += col_widths[i]
                
                # إعادة تعيين نمط النص
                y_pos += 10
                pdf.set_text_color(0, 0, 0)
                pdf.set_font('Arial', '', 10)
        
        # رسم صف المجموع
        pdf.set_fill_color(*pdf.primary_color_light)
        pdf.rect(10, y_pos, 277, 10, style='F')
        
        # كتابة بيانات المجموع
        pdf.set_font('Arial', 'B', 10)
        pdf.arabic_text(10 + col_widths[0]/2, y_pos + 5, "", 'C')
        pdf.arabic_text(10 + col_widths[0] + col_widths[1]/2, y_pos + 5, "المجموع", 'C')
        pdf.arabic_text(10 + col_widths[0] + col_widths[1] + col_widths[2]/2, y_pos + 5, "", 'C')
        
        # كتابة مجاميع المبالغ
        x_pos = 10 + col_widths[0] + col_widths[1] + col_widths[2]
        totals = [
            "{:,.2f}".format(total_basic),
            "{:,.2f}".format(total_allowances),
            "{:,.2f}".format(total_bonus),
            "{:,.2f}".format(total_deductions),
            "{:,.2f}".format(total_net)
        ]
        
        for i, total in enumerate(totals):
            pdf.arabic_text(x_pos + col_widths[i+3]/2, y_pos + 5, total, 'R')
            x_pos += col_widths[i+3]
        
        # إضافة معلومات إحصائية
        y_pos += 15
        pdf.set_font('Arial', 'B', 10)
        pdf.set_text_color(*pdf.secondary_color)
        pdf.arabic_text(20, y_pos, f"إجمالي عدد الموظفين: {len(salaries_data)}", 'R')
        pdf.arabic_text(100, y_pos, f"إجمالي الرواتب: {total_net:,.2f}", 'R')
        pdf.arabic_text(180, y_pos, f"متوسط الراتب: {total_net/len(salaries_data) if len(salaries_data) > 0 else 0:,.2f}", 'R')
        
        # التذييل
        pdf.set_xy(10.0, 190.0)
        pdf.set_font('Arial', '', 8)
        pdf.set_text_color(*pdf.secondary_color)
        current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        pdf.arabic_text(280.0, pdf.get_y(), "تم إنشاء هذا التقرير في " + current_timestamp, 'C')
        current_year = str(datetime.now().year)
        pdf.arabic_text(280.0, pdf.get_y() + 5.0, "نُظم - جميع الحقوق محفوظة © " + current_year, 'C')
        
        # إرجاع كائن FPDF
        return pdf
    except Exception as e:
        print(f"خطأ في إنشاء تقرير الرواتب PDF المحسن: {str(e)}")
        raise e


# دالة واجهة رئيسية تستدعي دالة الإنشاء ثم تحول النتيجة إلى بايت
def generate_salary_report_pdf(salaries_data, month, year):
    """
    إنشاء تقرير رواتب كملف PDF باستخدام FPDF
    
    Args:
        salaries_data: قائمة بكائنات Salary
        month: رقم الشهر
        year: السنة
        
    Returns:
        bytes يحتوي على ملف PDF
    """
    try:
        return create_pdf_bytes(create_salary_report_pdf, salaries_data, month, year)
    except Exception as e:
        print(f"خطأ في إنشاء تقرير الرواتب PDF الجديد: {str(e)}")
        raise e


# نموذج تسليم واستلام المركبات

def create_vehicle_handover_pdf(handover_data):
    """
    إنشاء نموذج تسليم/استلام المركبة كملف PDF باستخدام FPDF
    
    Args:
        handover_data: بيانات التسليم/الاستلام
        
    Returns:
        FPDF: كائن FPDF محتوي على التقرير
    """
    try:
        # إنشاء كائن FPDF جديد
        pdf = ArabicPDF(orientation='P', unit='mm', format='A4')
        pdf.add_page()
        
        # إعداد الألوان الأساسية
        pdf.primary_color = (13, 71, 161)  # أزرق داكن
        pdf.secondary_color = (66, 66, 66)  # رمادي داكن
        pdf.accent_color = (1, 135, 134)  # أزرق مخضر
        pdf.background_color = (240, 240, 240)  # رمادي فاتح
        
        # إضافة العنوان
        pdf.set_font('Arial', 'B', 18)
        pdf.set_text_color(*pdf.primary_color)
        title = "نموذج " + handover_data['handover_type'] + " مركبة"
        pdf.arabic_text(105, 20, title, 'C')
        
        # إضافة معلومات المركبة
        pdf.rounded_rect(10, 30, 190, 40, 3, 'DF', None, pdf.background_color)
        
        pdf.set_font('Arial', 'B', 13)
        pdf.set_text_color(*pdf.primary_color)
        pdf.arabic_text(190, 40, "بيانات المركبة:", 'R')
        
        pdf.set_font('Arial', '', 11)
        pdf.set_text_color(*pdf.secondary_color)
        pdf.arabic_text(190, 50, f"رقم اللوحة: {handover_data['vehicle']['plate_number']}", 'R')
        pdf.arabic_text(190, 58, f"النوع: {handover_data['vehicle']['make']} {handover_data['vehicle']['model']}", 'R')
        pdf.arabic_text(190, 66, f"سنة الصنع: {handover_data['vehicle']['year']} - اللون: {handover_data['vehicle']['color']}", 'R')
        
        # إضافة معلومات التسليم/الاستلام
        pdf.rounded_rect(10, 80, 190, 30, 3, 'DF', None, pdf.background_color)
        
        pdf.set_font('Arial', 'B', 13)
        pdf.set_text_color(*pdf.primary_color)
        pdf.arabic_text(190, 90, "معلومات " + handover_data['handover_type'] + ":", 'R')
        
        pdf.set_font('Arial', '', 11)
        pdf.set_text_color(*pdf.secondary_color)
        pdf.arabic_text(190, 98, f"التاريخ: {handover_data['handover_date']}", 'R')
        pdf.arabic_text(190, 106, f"الشخص: {handover_data['person_name']}", 'R')
        
        # إضافة معلومات المشرف إذا وجدت
        if handover_data.get('supervisor_name'):
            pdf.arabic_text(100, 106, f"المشرف: {handover_data['supervisor_name']}", 'R')
            
        # إضافة رابط نموذج التسليم/الاستلام إذا وجد
        if handover_data.get('form_link'):
            pdf.set_font('Arial', 'B', 10)
            pdf.set_text_color(*pdf.accent_color)
            pdf.arabic_text(190, 114, "رابط النموذج: " + handover_data['form_link'], 'R')
        
        # جدول فحص المركبة
        pdf.set_font('Arial', 'B', 13)
        pdf.set_text_color(*pdf.primary_color)
        pdf.arabic_text(105, 125, "حالة المركبة", 'C')
        
        # إعداد جدول الفحص
        items = [
            {"name": "إطار احتياطي", "checked": handover_data['has_spare_tire']},
            {"name": "طفاية حريق", "checked": handover_data['has_fire_extinguisher']},
            {"name": "حقيبة إسعافات أولية", "checked": handover_data['has_first_aid_kit']},
            {"name": "مثلث تحذيري", "checked": handover_data['has_warning_triangle']},
            {"name": "أدوات", "checked": handover_data['has_tools']}
        ]
        
        # رسم جدول الفحص
        col_width = 40
        row_height = 10
        pdf.set_fill_color(*pdf.background_color)
        
        y_position = 130
        for i, item in enumerate(items):
            x_position = 115 + (i % 2) * 45
            if i % 2 == 0 and i > 0:
                y_position += row_height
            
            pdf.set_font('Arial', '', 10)
            pdf.arabic_text(x_position + 35, y_position + 5, item["name"], 'R')
            
            # مربع الاختيار
            pdf.rect(x_position, y_position, 5, 5, 'D')
            if item["checked"]:
                pdf.set_font('ZapfDingbats', '', 10)
                pdf.text(x_position + 1, y_position + 4, '4')  # علامة صح
        
        # معلومات إضافية
        y_position = 165
        pdf.set_font('Arial', 'B', 12)
        pdf.set_text_color(*pdf.primary_color)
        pdf.arabic_text(190, y_position, "مستوى الوقود:", 'R')
        
        # رسم خزان الوقود
        pdf.rounded_rect(100, y_position - 5, 70, 10, 2, 'D')
        
        # تلوين الجزء المملوء من خزان الوقود
        fuel_levels = {"فارغ": 0, "ربع": 0.25, "نصف": 0.5, "ثلاثة أرباع": 0.75, "ممتلئ": 1}
        fuel_level = fuel_levels.get(handover_data['fuel_level'], 0)
        if fuel_level > 0:
            pdf.set_fill_color(*pdf.accent_color)
            pdf.rounded_rect(100, y_position - 5, 70 * fuel_level, 10, 2, 'F')
        
        pdf.set_font('Arial', '', 10)
        pdf.set_text_color(*pdf.secondary_color)
        pdf.arabic_text(90, y_position, handover_data['fuel_level'], 'R')
        
        # قراءة العداد
        y_position += 15
        pdf.set_font('Arial', 'B', 12)
        pdf.set_text_color(*pdf.primary_color)
        pdf.arabic_text(190, y_position, "قراءة العداد:", 'R')
        
        pdf.set_font('Arial', '', 10)
        pdf.set_text_color(*pdf.secondary_color)
        pdf.arabic_text(100, y_position, f"{handover_data['mileage']} كم", 'R')
        
        # حالة المركبة
        y_position += 10
        pdf.set_font('Arial', 'B', 12)
        pdf.set_text_color(*pdf.primary_color)
        pdf.arabic_text(190, y_position, "حالة المركبة:", 'R')
        
        # مربع لوصف حالة المركبة
        pdf.rounded_rect(10, y_position + 5, 190, 25, 3, 'D')
        
        pdf.set_font('Arial', '', 10)
        pdf.set_text_color(*pdf.secondary_color)
        pdf.arabic_text(185, y_position + 15, handover_data['vehicle_condition'], 'R')
        
        # ملاحظات إضافية
        if handover_data['notes']:
            y_position += 40
            pdf.set_font('Arial', 'B', 12)
            pdf.set_text_color(*pdf.primary_color)
            pdf.arabic_text(190, y_position, "ملاحظات إضافية:", 'R')
            
            # مربع للملاحظات
            pdf.rounded_rect(10, y_position + 5, 190, 20, 3, 'D')
            
            pdf.set_font('Arial', '', 10)
            pdf.set_text_color(*pdf.secondary_color)
            pdf.arabic_text(185, y_position + 15, handover_data['notes'], 'R')
        
        # التوقيعات
        y_position = 240
        pdf.line(10, y_position - 5, 200, y_position - 5)
        
        pdf.set_font('Arial', 'B', 12)
        pdf.set_text_color(*pdf.primary_color)
        pdf.arabic_text(180, y_position, "التوقيعات", 'R')
        
        pdf.set_font('Arial', '', 10)
        pdf.set_text_color(*pdf.secondary_color)
        
        # توقيع المستلم/المسلم
        pdf.arabic_text(160, y_position + 10, "توقيع " + ("المستلم" if handover_data['handover_type'] == "تسليم" else "المسلم") + ":", 'R')
        pdf.line(80, y_position + 10, 150, y_position + 10)
        
        # توقيع المشرف (إذا وُجد)
        if handover_data.get('supervisor_name'):
            pdf.arabic_text(160, y_position + 25, "توقيع المشرف:", 'R')
            pdf.line(80, y_position + 25, 150, y_position + 25)
        
        # توقيع مدير المرآب
        pdf.arabic_text(60, y_position + 10, "توقيع مدير المرآب:", 'R')
        pdf.line(10, y_position + 10, 50, y_position + 10)
        
        # التذييل
        pdf.set_xy(10.0, 270.0)
        pdf.set_font('Arial', '', 8)
        pdf.set_text_color(*pdf.secondary_color)
        current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        pdf.arabic_text(105.0, pdf.get_y(), "تم إنشاء هذا النموذج في " + current_timestamp, 'C')
        current_year = str(datetime.now().year)
        pdf.arabic_text(105.0, pdf.get_y() + 5.0, "نُظم - جميع الحقوق محفوظة © " + current_year, 'C')
        
        return pdf
    except Exception as e:
        print(f"خطأ في إنشاء نموذج التسليم/الاستلام PDF: {str(e)}")
        raise e


def generate_vehicle_handover_pdf(handover_data):
    """
    دالة واجهة رئيسية لإنشاء نموذج تسليم/استلام المركبة وتحويله إلى بايت
    
    Args:
        handover_data: بيانات التسليم/الاستلام
        
    Returns:
        bytes: بيانات ثنائية للملف
    """
    try:
        return create_pdf_bytes(create_vehicle_handover_pdf, handover_data)
    except Exception as e:
        print(f"خطأ في إنشاء نموذج التسليم/الاستلام PDF: {str(e)}")
        raise e