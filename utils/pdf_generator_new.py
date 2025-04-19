"""
مكتبة جديدة لإنشاء ملفات PDF بدعم كامل للغة العربية
تستخدم FPDF مع معالجة صحيحة للنصوص العربية وأنواع البيانات
"""
from io import BytesIO
import os
from datetime import datetime
import arabic_reshaper
from bidi.algorithm import get_display
from fpdf import FPDF

# تعريف فئة PDF العربية
class ArabicPDF(FPDF):
    """فئة PDF مخصصة لدعم اللغة العربية مع تحسينات التصميم"""
    
    def __init__(self, orientation='P', unit='mm', format='A4'):
        # استدعاء المُنشئ الأصلي
        super().__init__(orientation=orientation, unit=unit, format=format)
        
        # إضافة الخطوط العربية المتوفرة
        # خط Amiri (أميري) يعمل بشكل جيد جداً مع النصوص العربية
        amiri_regular = os.path.join('static', 'fonts', 'Amiri-Regular.ttf')
        amiri_bold = os.path.join('static', 'fonts', 'Amiri-Bold.ttf')
        
        try:
            # تسجيل الخط أميري (Amiri) للعربية
            if os.path.exists(amiri_regular) and os.path.exists(amiri_bold):
                self.add_font('Amiri', '', amiri_regular, uni=True)
                self.add_font('Amiri', 'B', amiri_bold, uni=True)
                # استخدام خط Amiri كخط افتراضي للتطبيق
                self.add_font('Arial', '', amiri_regular, uni=True)
                self.add_font('Arial', 'B', amiri_bold, uni=True)
                print("تم تسجيل خط Amiri للنصوص العربية بنجاح")
            else:
                # محاولة استخدام خط Tajawal كبديل
                tajawal_regular = os.path.join('static', 'fonts', 'Tajawal-Regular.ttf')
                tajawal_bold = os.path.join('static', 'fonts', 'Tajawal-Bold.ttf')
                
                if os.path.exists(tajawal_regular) and os.path.exists(tajawal_bold):
                    self.add_font('Tajawal', '', tajawal_regular, uni=True)
                    self.add_font('Tajawal', 'B', tajawal_bold, uni=True)
                    self.add_font('Arial', '', tajawal_regular, uni=True)
                    self.add_font('Arial', 'B', tajawal_bold, uni=True)
                    print("تم تسجيل خط Tajawal للنصوص العربية بنجاح")
                else:
                    # استخدام خط Arial كملاذ أخير
                    self.add_font('Arial', '', os.path.join('static', 'fonts', 'arial.ttf'), uni=True)
                    self.add_font('Arial', 'B', os.path.join('static', 'fonts', 'arialbd.ttf'), uni=True)
                    print("تم استخدام خط Arial القياسي")
        except Exception as e:
            print(f"خطأ في تحميل الخطوط: {str(e)}")
            # في حالة حدوث خطأ، استخدم الخط الافتراضي
            self.set_font('Arial', '', 12)
        
        # تحديد الألوان الرئيسية في النظام
        self.primary_color = (29, 161, 142)  # اللون الأخضر من شعار RASSCO
        self.primary_color_light = (164, 225, 217)  # نسخة فاتحة من اللون الأخضر
        self.secondary_color = (100, 100, 100)  # لون رمادي
        self.table_header_color = (230, 230, 230)  # لون رمادي فاتح لرؤوس الجداول
        self.table_row_alt_color = (245, 245, 245)  # لون رمادي فاتح جداً للصفوف البديلة
        
        # تحديد أبعاد الصفحة للمساعدة في تنسيق المحتوى
        if orientation in ['P', 'p']:
            self.page_width = 210  # A4 portrait width in mm
            self.page_height = 297  # A4 portrait height in mm
        else:
            self.page_width = 297  # A4 landscape width in mm
            self.page_height = 210  # A4 landscape height in mm
            
        # مساحة العمل المتاحة (مع مراعاة الهوامش)
        self.content_width = self.page_width - 20  # 10 mm margin on each side
    
    def arabic_text(self, x, y, txt, align='R', max_width=None):
        """
        طباعة نص عربي مع دعم أفضل للمحاذاة وعرض النص مع تحسين ظهور الأحرف العربية
        
        Args:
            x: موضع X للنص
            y: موضع Y للنص
            txt: النص العربي المراد طباعته
            align: المحاذاة ('R', 'L', 'C')
            max_width: العرض الأقصى للنص (اختياري)
        """
        # تشكيل النص العربي للعرض الصحيح - إصلاح مشكلة الأحرف العربية الناقصة
        try:
            # التأكد من أن كل المكونات من نوع str
            # يجب تحويل x, y, txt إلى نصوص في حالة كانت أرقام
            x = float(x) if not isinstance(x, (int, float)) else x
            y = float(y) if not isinstance(y, (int, float)) else y
            
            # تحويل النص إلى سلسلة نصية للتأكد من أنه ليس رقم
            txt_str = str(txt)
            
            # استخدام arabic_reshaper لتحويل النص العربي
            reshaped_text = arabic_reshaper.reshape(txt_str)
            # استخدام get_display لعكس اتجاه النص ليظهر بشكل صحيح
            bidi_text = get_display(reshaped_text)
        except Exception as e:
            # في حالة حدوث أي خطأ في التحويل، استخدم النص الأصلي
            print(f"خطأ في تحويل النص العربي: {e}")
            bidi_text = str(txt)
        
        # ضبط العرض الأقصى اعتماداً على اتجاه الصفحة إذا لم يتم تحديده
        if max_width is None:
            # استخدام العرض الحالي للصفحة مع مراعاة الهوامش
            max_width = self.content_width
        
        # حفظ الموضع الحالي
        if align == 'R':
            self.set_xy(x - max_width, y)
        elif align == 'C':
            self.set_xy(x - (max_width/2), y)
        else:
            self.set_xy(x, y)
        
        # زيادة ارتفاع الخلية لضمان عدم حدوث تداخل
        cell_height = 8
        
        # ضبط المحاذاة وطباعة النص مع تحديد العرض
        self.cell(max_width, cell_height, bidi_text, 0, 1, align)
    
    def add_company_header(self, title, subtitle=None):
        """إضافة ترويسة الشركة مع الشعار والعنوان"""
        # إضافة الشعار
        logo_path = os.path.join('static', 'images', 'logo.png')
        
        # تحديد الموضع والأبعاد بشكل مناسب حسب اتجاه الصفحة
        is_landscape = self.page_no() > 0 and getattr(self, 'cur_orientation', 'P') == 'L'
        
        if is_landscape:
            title_x = 150  # موضع العنوان للصفحة الأفقية (وسط الصفحة)
            line_end = 270  # طول الخط الأفقي
            logo_width = 40
            logo_x = 15
            logo_y = 8
        else:
            title_x = 110  # موضع العنوان للصفحة العمودية (وسط الصفحة)
            line_end = 190  # طول الخط الأفقي
            logo_width = 35
            logo_x = 10
            logo_y = 8
        
        if os.path.exists(logo_path):
            # إضافة الشعار بحجم مناسب
            self.image(logo_path, logo_x, logo_y, logo_width)
            
            # إضافة خط أفقي أسفل الترويسة
            self.set_draw_color(*self.primary_color)
            self.set_line_width(0.5)
            self.line(10, 30, line_end, 30)
        
        # إضافة العنوان الرئيسي - ضبط أفضل للموضع والحجم
        self.set_font('Arial', 'B', 14)
        self.set_text_color(*self.primary_color)
        
        # تحسين موضع العنوان بحيث لا يتداخل مع اللوجو أو حافة الصفحة
        if is_landscape:
            self.arabic_text(245, 15, title, 'C')
        else:
            self.arabic_text(150, 18, title, 'C')
        
        # إضافة العنوان الفرعي إذا كان موجوداً
        if subtitle:
            self.set_font('Arial', '', 11)
            self.set_text_color(*self.secondary_color)
            
            # تحسين موضع العنوان الفرعي لمنع التداخل
            if is_landscape:
                self.arabic_text(245, 24, subtitle, 'C')
            else:
                self.arabic_text(150, 26, subtitle, 'C')
        
        # إعادة لون النص إلى الأسود
        self.set_text_color(0, 0, 0)
        
        # إرجاع الموضع Y بعد الترويسة
        return 40

def generate_salary_notification_pdf(data):
    """
    إنشاء إشعار راتب كملف PDF باستخدام FPDF - تصميم مطابق تماماً للنموذج المرسل
    مع تنسيق محسن للخط والمحاذاة داخل الخلايا
    
    Args:
        data: قاموس يحتوي على بيانات الراتب
        
    Returns:
        bytes يحتوي على ملف PDF
    """
    try:
        # التأكد من أن جميع البيانات من النوع الصحيح
        employee_name = str(data.get('employee_name', ''))
        employee_id = str(data.get('employee_id', ''))
        job_title = str(data.get('job_title', ''))
        department_name = str(data.get('department_name', '')) if data.get('department_name') else ''
        month_name = str(data.get('month_name', ''))
        year = str(data.get('year', ''))
        basic_salary = float(data.get('basic_salary', 0))
        allowances = float(data.get('allowances', 0))
        deductions = float(data.get('deductions', 0))
        bonus = float(data.get('bonus', 0))
        net_salary = float(data.get('net_salary', 0))
        notes = str(data.get('notes', '')) if data.get('notes') else ''
        current_date = str(data.get('current_date', datetime.now().strftime('%Y-%m-%d')))
        
        # ------ تهيئة المستند ------
        pdf = ArabicPDF()
        pdf.add_page()
        
        # ------ إضافة الشعار ------
        logo_path = os.path.join('static', 'images', 'logo.png')
        if os.path.exists(logo_path):
            pdf.image(logo_path, 10, 8, 30)
        else:
            # يمكن استخدام صورة بديلة للشعار من المجلد static
            alt_logo_path = os.path.join('static', 'img', 'logo.png')
            if os.path.exists(alt_logo_path):
                pdf.image(alt_logo_path, 10, 8, 30)
        
        # ------ العنوان الرئيسي ------
        # استخدام خط Amiri للنصوص العربية لأنه يتعامل مع العربية بشكل أفضل
        pdf.set_font('Amiri', 'B', 16)
        pdf.set_text_color(29, 161, 142)  # اللون الأخضر التركوازي
        title = "نظام إدارة الموظفين - شركة التقنية المتطورة"
        # استخدام طريقة arabic_text بدلاً من cell
        pdf.arabic_text(105, 15, title, 'C')
        
        # ------ العنوان الفرعي ------
        pdf.set_font('Amiri', '', 13)
        pdf.set_text_color(100, 100, 100)  # لون رمادي
        subtitle = f"إشعار راتب - شهر {month_name} {year}"
        pdf.arabic_text(105, 25, subtitle, 'C')
        
        # ------ خط فاصل أخضر ------
        pdf.set_draw_color(29, 161, 142)
        pdf.set_line_width(0.5)
        pdf.line(10, 35, 200, 35)
        
        # ------ قسم بيانات الموظف ------
        # عنوان القسم
        pdf.set_font('Amiri', 'B', 14)
        pdf.set_text_color(29, 161, 142)
        pdf.arabic_text(105, 45, "بيانات الموظف", 'C')
        
        # خط تحت العنوان
        pdf.line(120, 55, 90, 55)
        
        # بيانات الموظف
        pdf.set_font('Amiri', 'B', 12)
        pdf.set_text_color(0, 0, 0)
        pdf.set_xy(160, 65)
        pdf.arabic_text(170, 65, "الاسم:", 'R')
        
        pdf.set_font('Amiri', '', 12)
        pdf.arabic_text(120, 65, employee_name, 'R')
        
        # ------ قسم تفاصيل الراتب ------
        pdf.set_font('Amiri', 'B', 14)
        pdf.set_text_color(29, 161, 142)
        pdf.arabic_text(105, 85, "تفاصيل الراتب", 'C')
        
        # خط تحت عنوان تفاصيل الراتب
        pdf.line(130, 95, 80, 95)
        
        # ------ قسم ملخص الراتب ------
        pdf.set_font('Amiri', 'B', 14)
        pdf.set_text_color(29, 161, 142)
        pdf.arabic_text(105, 115, "ملخص الراتب", 'C')
        
        # خط تحت عنوان ملخص الراتب
        pdf.line(145, 125, 65, 125)
        
        # ------ جدول ملخص الراتب - تصميم مطابق للصورة المرسلة ------
        # يحتاج إلى تمركز في الصفحة مع عرض 140 وحدة
        table_width = 140
        col1_width = 50   # عرض عمود المبلغ
        col2_width = 90   # عرض عمود البيان
        table_x = (210 - table_width) / 2  # النقطة X في وسط الصفحة
        table_y = 135
        row_height = 10
        
        # رأس الجدول - لون أخضر وخط أبيض
        pdf.set_xy(table_x, table_y)
        pdf.set_fill_color(29, 161, 142)  # اللون الأخضر للخلفية
        pdf.set_text_color(255, 255, 255)  # لون أبيض للنص
        pdf.set_font('Amiri', 'B', 14)
        
        # استخدام دالة arabic_text بدلاً من cell للنصوص العربية
        # عرض رأس الجدول
        header_title_y = table_y + row_height/2
        # نحتاج إلى عرض المبلغ (الخلية اليسرى) والبيان (الخلية اليمنى) بشكل منفصل لمحاذاة صحيحة
        # لرسم خلفية الخلايا
        pdf.set_fill_color(29, 161, 142)
        pdf.rect(table_x, table_y, col1_width, row_height, 'F')  # خلفية خلية المبلغ
        pdf.rect(table_x + col1_width, table_y, col2_width, row_height, 'F')  # خلفية خلية البيان
        
        # رسم حدود الخلايا
        pdf.set_draw_color(0, 0, 0)  # لون أسود للإطارات
        pdf.rect(table_x, table_y, col1_width, row_height)  # إطار خلية المبلغ
        pdf.rect(table_x + col1_width, table_y, col2_width, row_height)  # إطار خلية البيان
        
        # نص الخلايا
        pdf.arabic_text(table_x + col1_width/2, header_title_y, "المبلغ", 'C')
        pdf.arabic_text(table_x + col1_width + col2_width/2, header_title_y, "البيان", 'C')
        
        # تنسيق صيغة الأرقام المالية بدقة رقمين بعد الفاصلة
        basic_salary_str = f"{basic_salary:.2f}"
        allowances_str = f"{allowances:.2f}"
        deductions_str = f"{deductions:.2f}"
        bonus_str = f"{bonus:.2f}"
        net_salary_str = f"{net_salary:.2f}"
        
        # بيانات الجدول مع المحاذاة الدقيقة
        salary_items = [
            ["إجمالي الراتب الأساسي", basic_salary_str],
            ["إجمالي البدلات", allowances_str],
            ["إجمالي الخصومات", deductions_str],
            ["إجمالي المكافآت", bonus_str],
            ["إجمالي صافي الراتب", net_salary_str]
        ]
        
        # نبدأ من سطر جديد بعد العنوان
        current_y = table_y + row_height
        
        # رسم صفوف الجدول
        for i, item in enumerate(salary_items):
            # تنسيق الصف الأخير (إجمالي صافي الراتب) بشكل مميز
            if i == len(salary_items) - 1:
                pdf.set_fill_color(29, 161, 142)  # خلفية خضراء للصف الأخير
                pdf.set_text_color(255, 255, 255)  # لون أبيض للنص
                pdf.set_font('Amiri', 'B', 12)
                use_fill = True
            else:
                pdf.set_fill_color(255, 255, 255)  # خلفية بيضاء للصفوف العادية
                pdf.set_text_color(0, 0, 0)  # لون أسود للنص
                pdf.set_font('Amiri', '', 12)
                use_fill = False
            
            # رسم خلفية الصف
            if use_fill:
                pdf.set_fill_color(29, 161, 142)
                pdf.rect(table_x, current_y, col1_width + col2_width, row_height, 'F')
            
            # رسم حدود الخلايا
            pdf.set_draw_color(0, 0, 0)
            pdf.rect(table_x, current_y, col1_width, row_height)  # إطار خلية المبلغ
            pdf.rect(table_x + col1_width, current_y, col2_width, row_height)  # إطار خلية البيان
            
            # نص الخلايا
            cell_middle_y = current_y + row_height/2
            pdf.arabic_text(table_x + col1_width/2, cell_middle_y, item[1], 'C')
            pdf.arabic_text(table_x + col1_width + col2_width/2, cell_middle_y, item[0], 'C')
            
            # الانتقال للسطر التالي
            current_y += row_height
        
        # ------ قسم التوقيعات ------
        signature_y = 200
        
        # توقيع الموظف (يسار)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Amiri', 'B', 11)
        pdf.arabic_text(50, signature_y, "توقيع الموظف", 'C')
        
        # توقيع المدير المالي (يمين)
        pdf.arabic_text(160, signature_y, "توقيع المدير المالي", 'C')
        
        # خطوط التوقيع
        pdf.set_xy(30, signature_y + 10)
        pdf.cell(40, 10, "______________", 0, 0, 'C')
        
        pdf.set_xy(140, signature_y + 10)
        pdf.cell(40, 10, "______________", 0, 0, 'C')
        
        # ------ التذييل ------
        footer_y = 270
        pdf.set_font('Amiri', '', 8)
        pdf.set_text_color(100, 100, 100)
        
        # تاريخ الإصدار
        footer_text = f"تم إصدار هذا الإشعار بتاريخ {current_date}"
        pdf.arabic_text(105, footer_y, footer_text, 'C')
        
        # حقوق النشر
        copyright_text = f"شركة التقنية المتطورة - جميع الحقوق محفوظة © {datetime.now().year}"
        pdf.arabic_text(105, footer_y + 5, copyright_text, 'C')
        
        # إرجاع المستند كبيانات ثنائية
        pdf_content = pdf.output(dest='S').encode('latin1')
        return pdf_content
        
    except Exception as e:
        print(f"خطأ في إنشاء إشعار راتب PDF: {str(e)}")
        # للمساعدة في تشخيص المشكلات المتعلقة بالبيانات
        print(f"بيانات المدخلات: {str(data)}")
        raise e


def generate_salary_report_pdf(salaries_data, month_name, year):
    """
    إنشاء تقرير رواتب كملف PDF باستخدام FPDF
    
    Args:
        salaries_data: قائمة بكائنات Salary
        month_name: رقم الشهر أو اسم الشهر
        year: السنة
        
    Returns:
        bytes يحتوي على ملف PDF
    """
    try:
        # تحويل المدخلات إلى النوع المناسب
        month_name = str(month_name)
        year = str(year)
        
        # تحويل رقم الشهر إلى اسم الشهر
        month_names = [
            'يناير', 'فبراير', 'مارس', 'أبريل',
            'مايو', 'يونيو', 'يوليو', 'أغسطس',
            'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'
        ]
        
        # إذا كان month_name عددًا، فسيتم استخدامه كفهرس في القائمة
        if month_name.isdigit() and 1 <= int(month_name) <= 12:
            month_name = month_names[int(month_name) - 1]
        
        # إنشاء PDF جديد في الوضع الأفقي
        pdf = ArabicPDF('L')
        pdf.add_page()
        
        # إضافة ترويسة الشركة
        subtitle = "تقرير الرواتب - شهر " + month_name + " " + year
        y_pos = pdf.add_company_header("نظام إدارة الموظفين - شركة التقنية المتطورة", subtitle)
        
        # إنشاء جدول الرواتب
        headers = ["م", "اسم الموظف", "الرقم الوظيفي", "القسم", "الراتب الأساسي", "البدلات", "المكافآت", "الخصومات", "صافي الراتب"]
        
        # تعيين عرض كل عمود (مجموع العروض = 270)
        col_widths = [10, 50, 25, 35, 30, 30, 30, 30, 30]
        
        # بداية جدول الرواتب
        y_start = y_pos + 10
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
        pdf.set_font('Arial', '', 9)
        
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
            
            # الحصول على بيانات الموظف والراتب بشكل آمن
            try:
                # التعامل مع كائن Salary
                employee_name = salary.employee.name if hasattr(salary, 'employee') else ''
                employee_id = salary.employee.employee_id if hasattr(salary, 'employee') else ''
                department_name = salary.employee.department.name if hasattr(salary, 'employee') and hasattr(salary.employee, 'department') and salary.employee.department else ''
                basic_salary = salary.basic_salary if hasattr(salary, 'basic_salary') else 0
                allowances = salary.allowances if hasattr(salary, 'allowances') else 0
                bonus = salary.bonus if hasattr(salary, 'bonus') else 0
                deductions = salary.deductions if hasattr(salary, 'deductions') else 0
                net_salary = salary.net_salary if hasattr(salary, 'net_salary') else 0
                
                row_data = [
                    str(idx + 1),
                    employee_name,
                    employee_id,
                    department_name,
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
            except Exception as e:
                print(f"خطأ في معالجة بيانات الراتب: {e}")
                row_data = [str(idx + 1), "خطأ في البيانات", "", "", "", "", "", "", ""]
            
            # كتابة كل خلية
            for i, cell_data in enumerate(row_data):
                align = 'R' if i >= 4 else 'C'  # محاذاة المبالغ إلى اليمين
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
                pdf.set_font('Arial', '', 9)
        
        # رسم صف المجموع
        pdf.set_fill_color(*pdf.primary_color_light)
        pdf.rect(10, y_pos, 277, 10, style='F')
        
        # كتابة بيانات المجموع
        pdf.set_font('Arial', 'B', 10)
        
        # كتابة كلمة "المجموع" في العمود الثاني
        x_pos = 10
        pdf.arabic_text(x_pos + col_widths[0]/2, y_pos + 5, "", 'C')
        x_pos += col_widths[0]
        
        pdf.arabic_text(x_pos + col_widths[1]/2, y_pos + 5, "المجموع", 'C')
        x_pos += col_widths[1]
        
        # تخطي العمود الثالث والرابع
        pdf.arabic_text(x_pos + col_widths[2]/2, y_pos + 5, "", 'C')
        x_pos += col_widths[2]
        
        pdf.arabic_text(x_pos + col_widths[3]/2, y_pos + 5, "", 'C')
        x_pos += col_widths[3]
        
        # كتابة مجاميع المبالغ
        totals = [
            "{:,.2f}".format(total_basic),
            "{:,.2f}".format(total_allowances),
            "{:,.2f}".format(total_bonus),
            "{:,.2f}".format(total_deductions),
            "{:,.2f}".format(total_net)
        ]
        
        for i, total in enumerate(totals):
            pdf.arabic_text(x_pos + col_widths[i+4]/2, y_pos + 5, total, 'R')
            x_pos += col_widths[i+4]
        
        # إضافة معلومات إحصائية
        y_pos += 15
        pdf.set_font('Arial', 'B', 10)
        pdf.set_text_color(*pdf.secondary_color)
        pdf.arabic_text(20, y_pos, f"إجمالي عدد الموظفين: {len(salaries_data)}", 'R')
        pdf.arabic_text(100, y_pos, f"إجمالي الرواتب: {total_net:,.2f}", 'R')
        pdf.arabic_text(190, y_pos, f"متوسط الراتب: {total_net/len(salaries_data) if len(salaries_data) > 0 else 0:,.2f}", 'R')
        
        # التذييل
        pdf.set_xy(10.0, 190.0)
        pdf.set_font('Arial', '', 8)
        pdf.set_text_color(*pdf.secondary_color)
        current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        pdf.arabic_text(280.0, pdf.get_y(), "تم إنشاء هذا التقرير في " + current_timestamp, 'C')
        current_year = str(datetime.now().year)
        pdf.arabic_text(280.0, pdf.get_y() + 5.0, "شركة التقنية المتطورة - جميع الحقوق محفوظة © " + current_year, 'C')
        
        # إنشاء الملف كبيانات ثنائية - تحديث للإصدار الجديد من FPDF
        # استخدام dest='S' لإرجاع المحتوى كسلسلة نصية ثم تحويله إلى بايت
        pdf_content = pdf.output(dest='S').encode('latin1')
        return pdf_content
        
    except Exception as e:
        print(f"خطأ في إنشاء تقرير الرواتب PDF الجديد: {str(e)}")
        raise e

def generate_workshop_receipts_pdf(delivery_data, pickup_data, vehicle):
    """
    إنشاء إشعار تسليم/استلام من الورشة كملف PDF
    
    Args:
        delivery_data: بيانات تسليم المركبة للورشة
        pickup_data: بيانات استلام المركبة من الورشة
        vehicle: بيانات المركبة
        
    Returns:
        bytes يحتوي على ملف PDF
    """
    try:
        # إنشاء PDF جديد
        pdf = ArabicPDF()
        pdf.add_page()
        
        # إضافة ترويسة الشركة
        y_pos = pdf.add_company_header("نظام إدارة المركبات - شركة التقنية المتطورة", "إشعار تسليم واستلام من الورشة")
        
        # إضافة إطار للمستند
        pdf.set_draw_color(*pdf.primary_color)
        pdf.set_line_width(0.3)
        pdf.rect(10.0, 40.0, 190.0, 230.0)  # إطار خارجي
        
        # بيانات المركبة
        pdf.set_font('Arial', 'B', 14)
        pdf.set_text_color(*pdf.primary_color)
        pdf.arabic_text(190, y_pos + 5, "بيانات المركبة", 'R')
        
        # إضافة خط تحت عنوان بيانات المركبة
        pdf.set_draw_color(*pdf.primary_color)
        pdf.line(60.0, y_pos + 15.0, 190.0, y_pos + 15.0)
        
        # تحضير بيانات المركبة
        vehicle_make = vehicle.get('make', '')
        vehicle_model = vehicle.get('model', '')
        vehicle_year = vehicle.get('year', '')
        vehicle_plate = vehicle.get('plate_number', '')
        vehicle_type = vehicle.get('vehicle_type', '')
        
        # بيانات المركبة
        pdf.set_font('Arial', '', 12)
        pdf.set_text_color(0, 0, 0)
        
        # إنشاء جدول لبيانات المركبة
        veh_info_y = y_pos + 20.0
        pdf.set_xy(20.0, veh_info_y)
        
        # الصف الأول
        pdf.set_font('Arial', 'B', 11)
        pdf.arabic_text(190.0, veh_info_y, "نوع المركبة:", 'R')
        pdf.set_font('Arial', '', 11)
        pdf.arabic_text(140.0, veh_info_y, vehicle_make + " " + vehicle_model, 'R')
        
        pdf.set_font('Arial', 'B', 11)
        pdf.arabic_text(100.0, veh_info_y, "رقم اللوحة:", 'R')
        pdf.set_font('Arial', '', 11)
        pdf.arabic_text(50.0, veh_info_y, vehicle_plate, 'R')
        
        # الصف الثاني
        veh_info_y += 12.0
        pdf.set_font('Arial', 'B', 11)
        pdf.arabic_text(190.0, veh_info_y, "سنة الصنع:", 'R')
        pdf.set_font('Arial', '', 11)
        pdf.arabic_text(140.0, veh_info_y, vehicle_year, 'R')
        
        pdf.set_font('Arial', 'B', 11)
        pdf.arabic_text(100.0, veh_info_y, "فئة المركبة:", 'R')
        pdf.set_font('Arial', '', 11)
        pdf.arabic_text(50.0, veh_info_y, vehicle_type, 'R')
        
        # قسم تسليم المركبة للورشة
        delivery_y = veh_info_y + 25.0
        pdf.set_font('Arial', 'B', 14)
        pdf.set_text_color(*pdf.primary_color)
        pdf.arabic_text(190.0, delivery_y, "تسليم المركبة للورشة", 'R')
        
        # إضافة خط تحت العنوان
        pdf.set_draw_color(*pdf.primary_color)
        pdf.line(60.0, delivery_y + 10.0, 190.0, delivery_y + 10.0)
        
        # تحضير بيانات التسليم
        delivery_date = delivery_data.get('delivery_date', '')
        delivery_odometer = delivery_data.get('delivery_odometer', '')
        delivery_condition = delivery_data.get('delivery_condition', '')
        delivery_notes = delivery_data.get('delivery_notes', '')
        workshop_name = delivery_data.get('workshop_name', '')
        estimated_completion = delivery_data.get('estimated_completion', '')
        
        # بيانات التسليم
        pdf.set_font('Arial', '', 11)
        pdf.set_text_color(0, 0, 0)
        
        # إنشاء جدول لبيانات التسليم
        del_info_y = delivery_y + 15.0
        
        # الصف الأول
        pdf.set_font('Arial', 'B', 10)
        pdf.arabic_text(190.0, del_info_y, "تاريخ التسليم:", 'R')
        pdf.set_font('Arial', '', 10)
        pdf.arabic_text(140.0, del_info_y, delivery_date, 'R')
        
        pdf.set_font('Arial', 'B', 10)
        pdf.arabic_text(100.0, del_info_y, "اسم الورشة:", 'R')
        pdf.set_font('Arial', '', 10)
        pdf.arabic_text(50.0, del_info_y, workshop_name, 'R')
        
        # الصف الثاني
        del_info_y += 10.0
        pdf.set_font('Arial', 'B', 10)
        pdf.arabic_text(190.0, del_info_y, "قراءة العداد:", 'R')
        pdf.set_font('Arial', '', 10)
        pdf.arabic_text(140.0, del_info_y, str(delivery_odometer) + " كم", 'R')
        
        pdf.set_font('Arial', 'B', 10)
        pdf.arabic_text(100.0, del_info_y, "التاريخ المتوقع للإنجاز:", 'R')
        pdf.set_font('Arial', '', 10)
        pdf.arabic_text(50.0, del_info_y, estimated_completion, 'R')
        
        # الصف الثالث - حالة المركبة عند التسليم
        del_info_y += 10.0
        pdf.set_font('Arial', 'B', 10)
        pdf.arabic_text(190.0, del_info_y, "حالة المركبة عند التسليم:", 'R')
        pdf.set_font('Arial', '', 10)
        # استخدام مساحة أوسع لوصف الحالة
        pdf.set_xy(20.0, del_info_y + 5.0)
        pdf.rect(20.0, del_info_y + 5.0, 170.0, 15.0)
        pdf.set_xy(25.0, del_info_y + 8.0)
        pdf.multi_cell(160.0, 5.0, get_display(arabic_reshaper.reshape(delivery_condition)), 0, 'R')
        
        # ملاحظات التسليم
        del_info_y += 25.0
        pdf.set_font('Arial', 'B', 10)
        pdf.arabic_text(190.0, del_info_y, "ملاحظات:", 'R')
        pdf.set_font('Arial', '', 10)
        pdf.set_xy(20.0, del_info_y + 5.0)
        pdf.rect(20.0, del_info_y + 5.0, 170.0, 15.0)
        pdf.set_xy(25.0, del_info_y + 8.0)
        pdf.multi_cell(160.0, 5.0, get_display(arabic_reshaper.reshape(delivery_notes)), 0, 'R')
        
        # قسم استلام المركبة من الورشة
        pickup_y = del_info_y + 30.0
        pdf.set_font('Arial', 'B', 14)
        pdf.set_text_color(*pdf.primary_color)
        pdf.arabic_text(190.0, pickup_y, "استلام المركبة من الورشة", 'R')
        
        # إضافة خط تحت العنوان
        pdf.set_draw_color(*pdf.primary_color)
        pdf.line(60.0, pickup_y + 10.0, 190.0, pickup_y + 10.0)
        
        # تحضير بيانات الاستلام
        pickup_date = pickup_data.get('pickup_date', '')
        pickup_odometer = pickup_data.get('pickup_odometer', '')
        maintenance_cost = pickup_data.get('maintenance_cost', '')
        maintenance_details = pickup_data.get('maintenance_details', '')
        pickup_notes = pickup_data.get('pickup_notes', '')
        
        # بيانات الاستلام
        pdf.set_font('Arial', '', 11)
        pdf.set_text_color(0, 0, 0)
        
        # إنشاء جدول لبيانات الاستلام
        pickup_info_y = pickup_y + 15.0
        
        # الصف الأول
        pdf.set_font('Arial', 'B', 10)
        pdf.arabic_text(190.0, pickup_info_y, "تاريخ الاستلام:", 'R')
        pdf.set_font('Arial', '', 10)
        pdf.arabic_text(140.0, pickup_info_y, pickup_date, 'R')
        
        pdf.set_font('Arial', 'B', 10)
        pdf.arabic_text(100.0, pickup_info_y, "قراءة العداد:", 'R')
        pdf.set_font('Arial', '', 10)
        pdf.arabic_text(50.0, pickup_info_y, str(pickup_odometer) + " كم", 'R')
        
        # الصف الثاني
        pickup_info_y += 10.0
        pdf.set_font('Arial', 'B', 10)
        pdf.arabic_text(190.0, pickup_info_y, "تكلفة الصيانة:", 'R')
        pdf.set_font('Arial', '', 10)
        pdf.arabic_text(140.0, pickup_info_y, maintenance_cost + " ريال", 'R')
        
        # تفاصيل الصيانة
        pickup_info_y += 10.0
        pdf.set_font('Arial', 'B', 10)
        pdf.arabic_text(190.0, pickup_info_y, "تفاصيل الصيانة:", 'R')
        pdf.set_font('Arial', '', 10)
        pdf.set_xy(20.0, pickup_info_y + 5.0)
        pdf.rect(20.0, pickup_info_y + 5.0, 170.0, 15.0)
        pdf.set_xy(25.0, pickup_info_y + 8.0)
        pdf.multi_cell(160.0, 5.0, get_display(arabic_reshaper.reshape(maintenance_details)), 0, 'R')
        
        # ملاحظات الاستلام
        pickup_info_y += 25.0
        pdf.set_font('Arial', 'B', 10)
        pdf.arabic_text(190.0, pickup_info_y, "ملاحظات:", 'R')
        pdf.set_font('Arial', '', 10)
        pdf.set_xy(20.0, pickup_info_y + 5.0)
        pdf.rect(20.0, pickup_info_y + 5.0, 170.0, 15.0)
        pdf.set_xy(25.0, pickup_info_y + 8.0)
        pdf.multi_cell(160.0, 5.0, get_display(arabic_reshaper.reshape(pickup_notes)), 0, 'R')
        
        # التذييل
        pdf.set_xy(10.0, 270.0)
        pdf.set_font('Arial', '', 8)
        pdf.set_text_color(*pdf.secondary_color)
        current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        pdf.arabic_text(200.0, pdf.get_y(), "تم إنشاء هذا المستند في " + current_timestamp, 'C')
        current_year = str(datetime.now().year)
        pdf.arabic_text(200.0, pdf.get_y() + 5.0, "شركة التقنية المتطورة - جميع الحقوق محفوظة © " + current_year, 'C')
        
        # إنشاء الملف كبيانات ثنائية - تحديث للإصدار الجديد من FPDF
        # استخدام dest='S' لإرجاع المحتوى كسلسلة نصية ثم تحويله إلى بايت
        pdf_content = pdf.output(dest='S').encode('latin1')
        return pdf_content
        
    except Exception as e:
        print(f"خطأ في إنشاء نموذج تسليم/استلام PDF: {str(e)}")
        raise e
