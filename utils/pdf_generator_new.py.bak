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
        
        # إضافة الخط العربي (Tajawal)
        tajawal_regular = os.path.join('static', 'fonts', 'Tajawal-Regular.ttf')
        tajawal_bold = os.path.join('static', 'fonts', 'Tajawal-Bold.ttf')
        
        # التأكد من وجود ملفات الخط
        if os.path.exists(tajawal_regular) and os.path.exists(tajawal_bold):
            # تسجيل الخط باسمه الأصلي
            self.add_font('Tajawal', '', tajawal_regular, uni=True)
            self.add_font('Tajawal', 'B', tajawal_bold, uni=True)
            # تسجيل نفس الخط باسم Arial للحفاظ على توافق الكود الحالي
            self.add_font('Arial', '', tajawal_regular, uni=True)
            self.add_font('Arial', 'B', tajawal_bold, uni=True)
            print("تم تسجيل خط Tajawal للنصوص العربية بنجاح")
        else:
            # استخدام خط Arial كبديل
            self.add_font('Arial', '', os.path.join('static', 'fonts', 'arial.ttf'), uni=True)
            self.add_font('Arial', 'B', os.path.join('static', 'fonts', 'arialbd.ttf'), uni=True)
            print("تعذر العثور على خط Tajawal، تم استخدام Arial بدلاً منه")
        
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
    إنشاء إشعار راتب كملف PDF باستخدام FPDF
    
    Args:
        data: قاموس يحتوي على بيانات الراتب
        
    Returns:
        bytes يحتوي على ملف PDF
    """
    try:
        # التأكد من أن جميع البيانات من النوع النصي
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
        
        # إنشاء PDF جديد
        pdf = ArabicPDF()
        pdf.add_page()
        
        # إضافة ترويسة الشركة
        subtitle = "إشعار راتب - شهر " + str(month_name) + " " + str(year)
        y_pos = pdf.add_company_header("نظام إدارة الموظفين - شركة التقنية المتطورة", subtitle)
        
        # إضافة إطار للمستند
        pdf.set_draw_color(*pdf.primary_color)
        pdf.set_line_width(0.3)
        pdf.rect(10.0, 40.0, 190.0, 230.0)  # إطار خارجي
        
        # معلومات الموظف
        pdf.set_font('Arial', 'B', 14)
        pdf.set_text_color(*pdf.primary_color)
        pdf.arabic_text(190, y_pos + 5, "بيانات الموظف", 'R')
        
        # إضافة خط تحت عنوان بيانات الموظف
        pdf.set_draw_color(*pdf.primary_color)
        pdf.line(60.0, y_pos + 15.0, 190.0, y_pos + 15.0)
        
        # بيانات الموظف
        pdf.set_font('Arial', '', 12)
        pdf.set_text_color(0, 0, 0)
        
        # إنشاء جدول لبيانات الموظف (أكثر تنظيماً)
        emp_info_y = y_pos + 20.0
        pdf.set_xy(20.0, emp_info_y)
        
        # العمود الأول
        pdf.set_font('Arial', 'B', 11)
        pdf.arabic_text(190.0, emp_info_y, "الاسم:", 'R')
        pdf.set_font('Arial', '', 11)
        pdf.arabic_text(140.0, emp_info_y, employee_name, 'R')
        
        pdf.set_font('Arial', 'B', 11)
        pdf.arabic_text(100.0, emp_info_y, "الرقم الوظيفي:", 'R')
        pdf.set_font('Arial', '', 11)
        pdf.arabic_text(50.0, emp_info_y, employee_id, 'R')
        
        # العمود الثاني
        emp_info_y += 12.0
        if department_name:
            pdf.set_font('Arial', 'B', 11)
            pdf.arabic_text(190.0, emp_info_y, "القسم:", 'R')
            pdf.set_font('Arial', '', 11)
            pdf.arabic_text(140.0, emp_info_y, department_name, 'R')
        
        pdf.set_font('Arial', 'B', 11)
        pdf.arabic_text(100.0, emp_info_y, "المسمى الوظيفي:", 'R')
        pdf.set_font('Arial', '', 11)
        pdf.arabic_text(50.0, emp_info_y, job_title, 'R')
        
        # تفاصيل الراتب
        salary_title_y = emp_info_y + 25.0
        pdf.set_font('Arial', 'B', 14)
        pdf.set_text_color(*pdf.primary_color)
        pdf.arabic_text(190.0, salary_title_y, "تفاصيل الراتب", 'C')
        
        # خط تحت عنوان تفاصيل الراتب
        pdf.set_draw_color(*pdf.primary_color)
        pdf.line(60.0, salary_title_y + 10.0, 140.0, salary_title_y + 10.0)
        
        # ========== إعادة تصميم كاملة وصحيحة لقسم ملخص الراتب ==========
        
        # نبدأ بعنوان منفصل وواضح تماماً
        pdf.ln(15)  # مسافة إضافية بعد قسم تفاصيل الراتب
        pdf.set_font('Arial', 'B', 16)
        pdf.set_text_color(*pdf.primary_color)

        # إضافة عنوان محاذى للوسط
        title_y = pdf.get_y()
        # استخدام get_display لضمان عرض النص العربي بشكل صحيح
        pdf.cell(0, 10, get_display(arabic_reshaper.reshape("ملخص الراتب")), 0, 1, 'C')
        
        # خط أفقي تحت العنوان عبر الصفحة
        pdf.set_draw_color(*pdf.primary_color)
        pdf.line(70.0, title_y + 10.0, 140.0, title_y + 10.0)
        
        # نترك مسافة قبل بداية الجدول
        table_y = title_y + 15.0
        
        # تحديد عرض الجدول بشكل يتناسب مع المحتوى
        amount_width = 40.0  # عرض عمود المبلغ
        item_width = 85.0    # عرض عمود البيان
        row_height = 10.0    # ارتفاع الصف
        
        # حساب موقع بداية الجدول في منتصف الصفحة
        table_width = amount_width + item_width
        x_start = (pdf.page_width - table_width) / 2.0
        
        # إنشاء جدول جديد بتصميم محسن
        pdf.set_xy(x_start, table_y)
        pdf.set_fill_color(*pdf.primary_color)
        pdf.set_text_color(255, 255, 255)  # لون أبيض للنص
        pdf.set_font('Arial', 'B', 12)
        
        # رسم رأس الجدول - لكن عكس ترتيب الأعمدة ليتناسب مع اللغة العربية
        pdf.cell(amount_width, row_height, get_display(arabic_reshaper.reshape("المبلغ")), 1, 0, 'C', True)
        pdf.cell(item_width, row_height, get_display(arabic_reshaper.reshape("البيان")), 1, 1, 'C', True)
        
        # تنسيق الأرقام
        basic_salary_str = f"{basic_salary:.2f}"
        allowances_str = f"{allowances:.2f}"
        deductions_str = f"{deductions:.2f}"
        bonus_str = f"{bonus:.2f}"
        net_salary_str = f"{net_salary:.2f}"
        
        # إعداد مصفوفة بيانات ملخص الراتب
        salary_items = [
            ["إجمالي الراتب الأساسي", basic_salary_str],
            ["إجمالي البدلات", allowances_str],
            ["إجمالي الخصومات", deductions_str],
            ["إجمالي المكافآت", bonus_str],
            ["إجمالي صافي الراتب", net_salary_str]
        ]
        
        # طباعة بيانات الجدول
        pdf.set_text_color(0, 0, 0)  # لون أسود للنص
        
        for i, item in enumerate(salary_items):
            # تطبيق تنسيق خاص للصف الأخير (إجمالي صافي الراتب)
            if i == len(salary_items) - 1:
                pdf.set_font('Arial', 'B', 12)
                pdf.set_fill_color(*pdf.primary_color)
                pdf.set_text_color(255, 255, 255)  # لون أبيض للنص
                fill = True
            else:
                # تناوب ألوان الصفوف
                pdf.set_font('Arial', '', 11)
                fill = i % 2 == 1
                if fill:
                    pdf.set_fill_color(*pdf.table_row_alt_color)
                else:
                    pdf.set_fill_color(255, 255, 255)
            
            # رسم الصف بشكل صحيح - ضبط كامل للمحاذاة
            pdf.set_xy(x_start, pdf.get_y())
            pdf.cell(amount_width, row_height, item[1], 1, 0, 'C', fill)
            pdf.cell(item_width, row_height, get_display(arabic_reshaper.reshape(item[0])), 1, 1, 'R', fill)
        
        # إعادة ضبط نمط النص
        pdf.set_text_color(0, 0, 0)
        
        # إضافة الملاحظات إذا وجدت
        if notes:
            notes_y = pdf.get_y() + 10.0
            pdf.set_font('Arial', 'B', 12)
            pdf.set_text_color(*pdf.primary_color)
            pdf.arabic_text(190.0, notes_y, "ملاحظات:", 'R')
            
            pdf.set_xy(20.0, notes_y + 5.0)
            pdf.set_font('Arial', '', 10)
            pdf.set_text_color(0, 0, 0)  # لون أسود للنص
            
            # إطار للملاحظات
            pdf.rect(20.0, notes_y + 5.0, 170.0, 20.0)
            pdf.set_xy(25.0, notes_y + 10.0)
            pdf.multi_cell(160.0, 5.0, get_display(arabic_reshaper.reshape(notes)), 0, 'R')
        
        # التوقيعات
        signature_y = pdf.get_y() + 30.0
        if signature_y < 230.0:  # التأكد من أن التوقيعات ليست قريبة جداً من نهاية الصفحة
            signature_y = 230.0
        
        pdf.set_xy(20.0, signature_y)
        pdf.set_font('Arial', 'B', 11)
        pdf.set_text_color(*pdf.secondary_color)
        pdf.cell(50.0, 10.0, get_display(arabic_reshaper.reshape("توقيع الموظف")), 0, 0, 'C')
        pdf.cell(70.0, 10.0, "", 0, 0, 'C')  # فراغ في الوسط
        pdf.cell(50.0, 10.0, get_display(arabic_reshaper.reshape("توقيع المدير المالي")), 0, 1, 'C')
        
        pdf.set_xy(20.0, pdf.get_y())
        pdf.cell(50.0, 10.0, "________________", 0, 0, 'C')
        pdf.cell(70.0, 10.0, "", 0, 0, 'C')  # فراغ في الوسط
        pdf.cell(50.0, 10.0, "________________", 0, 1, 'C')
        
        # التذييل
        pdf.set_xy(10.0, 270.0)
        pdf.set_font('Arial', '', 8)
        pdf.set_text_color(*pdf.secondary_color)
        
        pdf.arabic_text(200.0, pdf.get_y(), "تم إصدار هذا الإشعار بتاريخ " + current_date, 'C')
        current_year_str = str(datetime.now().year)
        pdf.arabic_text(200.0, pdf.get_y() + 5.0, "شركة التقنية المتطورة - جميع الحقوق محفوظة © " + current_year_str, 'C')
        
        # إنشاء الملف كبيانات ثنائية
        buffer = BytesIO()
        pdf.output(buffer)
        buffer.seek(0)
        
        return buffer.getvalue()
        
    except Exception as e:
        print(f"خطأ في إنشاء إشعار راتب PDF الجديد: {str(e)}")
        raise e


def generate_salary_report_pdf(salaries_data, month_name, year):
    """
    إنشاء تقرير رواتب كملف PDF باستخدام FPDF
    
    Args:
        salaries_data: قائمة بكائنات Salary
        month_name: رقم الشهر
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
            'يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو',
            'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'
        ]
        # التأكد من أن month_name رقم صحيح بين 1 و 12
        try:
            month_int = int(month_name)
            if 1 <= month_int <= 12:
                month_display = month_names[month_int - 1]
            else:
                month_display = month_name
        except (ValueError, TypeError):
            month_display = month_name
        
        # إنشاء PDF جديد في الوضع الأفقي
        pdf = ArabicPDF('L')
        pdf.add_page()
        
        # إضافة ترويسة الشركة
        subtitle = "تقرير الرواتب - شهر " + str(month_display) + " " + str(year)
        y_pos = pdf.add_company_header("نظام إدارة الموظفين - شركة التقنية المتطورة", subtitle)
        
        # إضافة إطار للمستند
        pdf.set_draw_color(*pdf.primary_color)
        pdf.set_line_width(0.3)
        pdf.rect(10.0, 40.0, 277.0, 150.0)  # إطار خارجي للتقرير
        
        # إعداد جدول الرواتب
        headers = ["م", "اسم الموظف", "الرقم الوظيفي", "الراتب الأساسي", "البدلات", "الخصومات", "المكافآت", "صافي الراتب"]
        
        # تحويل البيانات إلى نوع مناسب
        clean_salaries_data = []
        for salary in salaries_data:
            # التعامل مع كائنات Salary
            if hasattr(salary, 'employee'):
                clean_salary = {
                    'employee_name': str(salary.employee.name) if salary.employee else '',
                    'employee_id': str(salary.employee.employee_id) if salary.employee else '',
                    'basic_salary': float(salary.basic_salary),
                    'allowances': float(salary.allowances),
                    'deductions': float(salary.deductions),
                    'bonus': float(salary.bonus),
                    'net_salary': float(salary.net_salary)
                }
            # التعامل مع القواميس
            else:
                clean_salary = {
                    'employee_name': str(salary.get('employee_name', '')),
                    'employee_id': str(salary.get('employee_id', '')),
                    'basic_salary': float(salary.get('basic_salary', 0)),
                    'allowances': float(salary.get('allowances', 0)),
                    'deductions': float(salary.get('deductions', 0)),
                    'bonus': float(salary.get('bonus', 0)),
                    'net_salary': float(salary.get('net_salary', 0))
                }
            clean_salaries_data.append(clean_salary)
        
        # حساب المجاميع
        total_basic = sum(salary['basic_salary'] for salary in clean_salaries_data)
        total_allowances = sum(salary['allowances'] for salary in clean_salaries_data)
        total_deductions = sum(salary['deductions'] for salary in clean_salaries_data)
        total_bonus = sum(salary['bonus'] for salary in clean_salaries_data)
        total_net = sum(salary['net_salary'] for salary in clean_salaries_data)
        
        # ضبط موضع الجدول
        pdf.set_font('Arial', 'B', 10)
        y_pos = 50.0
        
        # عرض الأعمدة
        col_widths = [15.0, 60.0, 25.0, 25.0, 25.0, 25.0, 25.0, 30.0]  # مجموع العرض = 230 (مليمتر تقريباً)
        
        # رأس الجدول
        pdf.set_fill_color(*pdf.primary_color)
        pdf.set_text_color(255, 255, 255)  # لون أبيض للنص
        x_pos = 30.0  # بداية من اليسار
        
        for i, header in reversed(list(enumerate(headers))):
            pdf.set_xy(x_pos, y_pos)
            pdf.cell(col_widths[i], 10.0, get_display(arabic_reshaper.reshape(header)), 1, 0, 'C', True)
            x_pos += col_widths[i]
        
        # بيانات الجدول
        pdf.set_text_color(0, 0, 0)  # إعادة النص للون الأسود
        pdf.set_font('Arial', '', 10)
        for idx, salary in enumerate(clean_salaries_data):
            y_pos += 10.0
            fill = idx % 2 == 1  # صفوف بديلة
            if fill:
                pdf.set_fill_color(*pdf.table_row_alt_color)
            else:
                pdf.set_fill_color(255, 255, 255)  # خلفية بيضاء للصفوف غير المظللة
            
            # تنسيق القيم المالية
            basic_salary_str = f"{salary['basic_salary']:.2f}"
            allowances_str = f"{salary['allowances']:.2f}"
            deductions_str = f"{salary['deductions']:.2f}"
            bonus_str = f"{salary['bonus']:.2f}"
            net_salary_str = f"{salary['net_salary']:.2f}"
            
            # بيانات الصف
            row_data = [
                str(idx + 1),
                salary['employee_name'],
                salary['employee_id'],
                basic_salary_str,
                allowances_str,
                deductions_str,
                bonus_str,
                net_salary_str
            ]
            
            x_pos = 30.0
            for i, cell_data in reversed(list(enumerate(row_data))):
                pdf.set_xy(x_pos, y_pos)
                if i == 1 or i == 2:  # اسم الموظف والرقم الوظيفي
                    text = get_display(arabic_reshaper.reshape(str(cell_data)))
                    align = 'R'
                else:
                    text = str(cell_data)  # تحويل إلى نص بغض النظر عن النوع
                    align = 'C'
                pdf.cell(col_widths[i], 10.0, text, 1, 0, align, fill)
                x_pos += col_widths[i]
        
        # صف المجموع
        y_pos += 10.0
        pdf.set_fill_color(*pdf.primary_color)
        pdf.set_text_color(255, 255, 255)  # لون أبيض للنص
        
        # تنسيق المجاميع
        total_basic_str = f"{total_basic:.2f}"
        total_allowances_str = f"{total_allowances:.2f}"
        total_deductions_str = f"{total_deductions:.2f}"
        total_bonus_str = f"{total_bonus:.2f}"
        total_net_str = f"{total_net:.2f}"
        
        # بيانات المجموع
        summary_data = [
            "",
            "المجموع",
            "",
            total_basic_str,
            total_allowances_str,
            total_deductions_str,
            total_bonus_str,
            total_net_str
        ]
        
        x_pos = 30.0
        pdf.set_font('Arial', 'B', 10)
        for i, cell_data in reversed(list(enumerate(summary_data))):
            pdf.set_xy(x_pos, y_pos)
            if i == 1:  # نص "المجموع"
                text = get_display(arabic_reshaper.reshape(str(cell_data)))
                align = 'R'
            else:
                text = str(cell_data)  # تحويل إلى نص بغض النظر عن النوع
                align = 'C'
            pdf.cell(col_widths[i], 10.0, text, 1, 0, align, True)
            x_pos += col_widths[i]
        
        # ملخص الرواتب
        if len(clean_salaries_data) > 5:
            summary_y = 135.0  # إذا كان هناك عدد كبير من الموظفين، نضع الجدول في مكان ثابت
        else:
            summary_y = y_pos + 35.0  # مكان متناسب مع موضع جدول الرواتب
        
        # عنوان ملخص الرواتب
        summary_title_x = pdf.page_width - 70.0
        summary_title_y = summary_y - 15.0
        
        pdf.set_text_color(*pdf.primary_color)
        pdf.set_font('Arial', 'B', 12)
        pdf.arabic_text(summary_title_x, summary_title_y, "ملخص الرواتب", 'R', 100)
        
        # إضافة خط تحت عنوان ملخص الرواتب
        pdf.set_draw_color(*pdf.primary_color)
        pdf.line(summary_title_x - 60.0, summary_title_y + 6.0, summary_title_x, summary_title_y + 6.0)
        
        # جدول الملخص
        summary_headers = ["البيان", "المبلغ"]
        summary_items = [
            ["إجمالي الرواتب الأساسية", total_basic_str],
            ["إجمالي البدلات", total_allowances_str],
            ["إجمالي الخصومات", total_deductions_str],
            ["إجمالي المكافآت", total_bonus_str],
            ["إجمالي صافي الرواتب", total_net_str]
        ]
        
        # رسم جدول الملخص
        pdf.set_font('Arial', 'B', 10)
        
        # ضبط أبعاد وموضع جدول الملخص بشكل أفضل
        col1_width = 40.0  # عمود المبلغ
        col2_width = 70.0  # عمود البيان
        summary_table_width = col1_width + col2_width
        
        # ضبط موضع X بشكل أفضل
        summary_table_x = pdf.page_width - 80.0 - summary_table_width
        
        pdf.set_fill_color(*pdf.primary_color)
        pdf.set_text_color(255, 255, 255)  # لون أبيض للنص
        pdf.set_xy(summary_table_x, summary_y)
        pdf.cell(col1_width, 10.0, get_display(arabic_reshaper.reshape(summary_headers[1])), 1, 0, 'C', True)
        pdf.cell(col2_width, 10.0, get_display(arabic_reshaper.reshape(summary_headers[0])), 1, 1, 'C', True)
        
        # بيانات جدول الملخص
        pdf.set_text_color(0, 0, 0)  # إعادة النص للون الأسود
        pdf.set_font('Arial', '', 10)
        for i, item in enumerate(summary_items):
            fill = i % 2 == 1  # صفوف بديلة
            if fill:
                pdf.set_fill_color(*pdf.table_row_alt_color)
            else:
                pdf.set_fill_color(255, 255, 255)  # خلفية بيضاء للصفوف غير المظللة
            
            if i == len(summary_items) - 1:  # الصف الأخير
                pdf.set_fill_color(*pdf.primary_color)
                pdf.set_text_color(255, 255, 255)  # لون أبيض للنص
                fill = True
                pdf.set_font('Arial', 'B', 10)
            
            # استخدام summary_table_x الذي تم تعريفه للجدول
            pdf.set_xy(summary_table_x, pdf.get_y())
            pdf.cell(col1_width, 10.0, item[1], 1, 0, 'C', fill)
            pdf.cell(col2_width, 10.0, get_display(arabic_reshaper.reshape(item[0])), 1, 1, 'R', fill)
        
        # معلومات التقرير
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Arial', 'B', 10)
        
        # عنوان المعلومات
        info_x = 30.0
        info_y = summary_y
        pdf.set_xy(info_x, info_y - 15.0)
        pdf.set_text_color(*pdf.primary_color)
        pdf.arabic_text(120.0, info_y - 15.0, "معلومات التقرير", 'R')
        
        # إضافة خط تحت عنوان معلومات التقرير
        pdf.set_draw_color(*pdf.primary_color)
        pdf.line(50.0, info_y - 7.0, 120.0, info_y - 7.0)
        
        # إطار للمعلومات
        pdf.set_draw_color(*pdf.secondary_color)
        pdf.rect(info_x, info_y, 110.0, 45.0)
        
        # معلومات التقرير داخل إطار
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Arial', '', 10)
        pdf.arabic_text(120.0, info_y + 10.0, "إجمالي عدد الموظفين: " + str(len(clean_salaries_data)), 'R')
        
        # التأكد من عدم القسمة على صفر
        if len(clean_salaries_data) > 0:
            avg_basic = total_basic / len(clean_salaries_data)
            avg_net = total_net / len(clean_salaries_data)
        else:
            avg_basic = 0.0
            avg_net = 0.0
        
        # تنسيق القيم وتحويلها إلى نصوص    
        avg_basic_str = f"{avg_basic:.2f}"
        avg_net_str = f"{avg_net:.2f}"
            
        pdf.arabic_text(120.0, info_y + 25.0, "متوسط الراتب الأساسي: " + avg_basic_str, 'R')
        pdf.arabic_text(120.0, info_y + 40.0, "متوسط صافي الراتب: " + avg_net_str, 'R')
        
        # التذييل
        pdf.set_xy(10.0, 190.0)
        pdf.set_font('Arial', '', 8)
        pdf.set_text_color(*pdf.secondary_color)
        current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        pdf.arabic_text(280.0, pdf.get_y(), "تم إنشاء هذا التقرير في " + current_timestamp, 'C')
        current_year = str(datetime.now().year)
        pdf.arabic_text(280.0, pdf.get_y() + 5.0, "شركة التقنية المتطورة - جميع الحقوق محفوظة © " + current_year, 'C')
        
        # إنشاء الملف كبيانات ثنائية
        buffer = BytesIO()
        pdf.output(buffer)
        buffer.seek(0)
        
        return buffer.getvalue()
        
    except Exception as e:
        print(f"خطأ في إنشاء تقرير الرواتب PDF الجديد: {str(e)}")
        raise e


def generate_vehicle_handover_pdf(handover_data):
    """
    إنشاء نموذج تسليم/استلام سيارة كملف PDF
    
    Args:
        handover_data: قاموس يحتوي على بيانات التسليم/الاستلام
        
    Returns:
        bytes يحتوي على ملف PDF
    """
    try:
        # التأكد من أن جميع البيانات من النوع النصي
        vehicle_data = {
            'plate_number': str(handover_data.get('vehicle', {}).get('plate_number', '')),
            'make': str(handover_data.get('vehicle', {}).get('make', '')),
            'model': str(handover_data.get('vehicle', {}).get('model', '')),
            'year': str(handover_data.get('vehicle', {}).get('year', '')),
            'color': str(handover_data.get('vehicle', {}).get('color', ''))
        }
        
        handover_type = str(handover_data.get('handover_type', ''))
        handover_date = str(handover_data.get('handover_date', ''))
        person_name = str(handover_data.get('person_name', ''))
        vehicle_condition = str(handover_data.get('vehicle_condition', ''))
        fuel_level = str(handover_data.get('fuel_level', ''))
        mileage = str(handover_data.get('mileage', ''))
        
        # تحويل القيم المنطقية إلى نص
        has_spare_tire = "نعم" if handover_data.get('has_spare_tire') else "لا"
        has_fire_extinguisher = "نعم" if handover_data.get('has_fire_extinguisher') else "لا"
        has_first_aid_kit = "نعم" if handover_data.get('has_first_aid_kit') else "لا"
        has_warning_triangle = "نعم" if handover_data.get('has_warning_triangle') else "لا"
        has_tools = "نعم" if handover_data.get('has_tools') else "لا"
        
        notes = str(handover_data.get('notes', ''))
        form_link = str(handover_data.get('form_link', ''))
        
        # تحديد عنوان المستند بناءً على نوع التسليم
        if handover_type == 'استلام':
            doc_title = "نموذج استلام سيارة"
        else:
            doc_title = "نموذج تسليم سيارة"
        
        # إنشاء PDF جديد
        pdf = ArabicPDF()
        pdf.add_page()
        
        # إضافة ترويسة الشركة
        y_pos = pdf.add_company_header("نظام إدارة المركبات - شركة التقنية المتطورة", doc_title)
        
        # إضافة إطار للمستند
        pdf.set_draw_color(*pdf.primary_color)
        pdf.set_line_width(0.3)
        pdf.rect(10.0, 40.0, 190.0, 230.0)  # إطار خارجي
        
        # معلومات السيارة
        pdf.set_font('Arial', 'B', 14)
        pdf.set_text_color(*pdf.primary_color)
        pdf.arabic_text(190, y_pos + 5, "بيانات السيارة", 'R')
        
        # إضافة خط تحت عنوان بيانات السيارة
        pdf.set_draw_color(*pdf.primary_color)
        pdf.line(60.0, y_pos + 15.0, 190.0, y_pos + 15.0)
        
        # بيانات السيارة
        pdf.set_font('Arial', '', 12)
        pdf.set_text_color(0, 0, 0)
        
        # إنشاء جدول لبيانات السيارة
        vehicle_info_y = y_pos + 20.0
        
        # الصف الأول - رقم اللوحة والشركة المصنعة
        pdf.set_font('Arial', 'B', 11)
        pdf.arabic_text(190.0, vehicle_info_y, "رقم اللوحة:", 'R')
        pdf.set_font('Arial', '', 11)
        pdf.arabic_text(140.0, vehicle_info_y, vehicle_data['plate_number'], 'R')
        
        pdf.set_font('Arial', 'B', 11)
        pdf.arabic_text(100.0, vehicle_info_y, "الشركة المصنعة:", 'R')
        pdf.set_font('Arial', '', 11)
        pdf.arabic_text(50.0, vehicle_info_y, vehicle_data['make'], 'R')
        
        # الصف الثاني - الموديل والسنة
        vehicle_info_y += 12.0
        pdf.set_font('Arial', 'B', 11)
        pdf.arabic_text(190.0, vehicle_info_y, "الموديل:", 'R')
        pdf.set_font('Arial', '', 11)
        pdf.arabic_text(140.0, vehicle_info_y, vehicle_data['model'], 'R')
        
        pdf.set_font('Arial', 'B', 11)
        pdf.arabic_text(100.0, vehicle_info_y, "سنة الصنع:", 'R')
        pdf.set_font('Arial', '', 11)
        pdf.arabic_text(50.0, vehicle_info_y, vehicle_data['year'], 'R')
        
        # الصف الثالث - اللون
        vehicle_info_y += 12.0
        pdf.set_font('Arial', 'B', 11)
        pdf.arabic_text(190.0, vehicle_info_y, "اللون:", 'R')
        pdf.set_font('Arial', '', 11)
        pdf.arabic_text(140.0, vehicle_info_y, vehicle_data['color'], 'R')
        
        # معلومات التسليم/الاستلام
        handover_title_y = vehicle_info_y + 25.0
        pdf.set_font('Arial', 'B', 14)
        pdf.set_text_color(*pdf.primary_color)
        
        if handover_type == 'استلام':
            pdf.arabic_text(190.0, handover_title_y, "بيانات الاستلام", 'R')
        else:
            pdf.arabic_text(190.0, handover_title_y, "بيانات التسليم", 'R')
        
        # إضافة خط تحت العنوان
        pdf.set_draw_color(*pdf.primary_color)
        pdf.line(60.0, handover_title_y + 10.0, 190.0, handover_title_y + 10.0)
        
        # بيانات التسليم/الاستلام
        pdf.set_font('Arial', '', 12)
        pdf.set_text_color(0, 0, 0)
        
        # إنشاء جدول لبيانات التسليم/الاستلام
        handover_info_y = handover_title_y + 20.0
        
        # الصف الأول - تاريخ التسليم/الاستلام واسم الشخص
        pdf.set_font('Arial', 'B', 11)
        
        if handover_type == 'استلام':
            pdf.arabic_text(190.0, handover_info_y, "تاريخ الاستلام:", 'R')
        else:
            pdf.arabic_text(190.0, handover_info_y, "تاريخ التسليم:", 'R')
            
        pdf.set_font('Arial', '', 11)
        pdf.arabic_text(140.0, handover_info_y, handover_date, 'R')
        
        pdf.set_font('Arial', 'B', 11)
        pdf.arabic_text(100.0, handover_info_y, "اسم الشخص:", 'R')
        pdf.set_font('Arial', '', 11)
        pdf.arabic_text(50.0, handover_info_y, person_name, 'R')
        
        # الصف الثاني - عداد الكيلومترات ومستوى الوقود
        handover_info_y += 12.0
        pdf.set_font('Arial', 'B', 11)
        pdf.arabic_text(190.0, handover_info_y, "عداد الكيلومترات:", 'R')
        pdf.set_font('Arial', '', 11)
        pdf.arabic_text(140.0, handover_info_y, mileage, 'R')
        
        pdf.set_font('Arial', 'B', 11)
        pdf.arabic_text(100.0, handover_info_y, "مستوى الوقود:", 'R')
        pdf.set_font('Arial', '', 11)
        pdf.arabic_text(50.0, handover_info_y, fuel_level, 'R')
        
        # قسم المحتويات والملحقات
        accessories_title_y = handover_info_y + 25.0
        pdf.set_font('Arial', 'B', 14)
        pdf.set_text_color(*pdf.primary_color)
        pdf.arabic_text(190.0, accessories_title_y, "المحتويات والملحقات", 'R')
        
        # إضافة خط تحت العنوان
        pdf.set_draw_color(*pdf.primary_color)
        pdf.line(60.0, accessories_title_y + 10.0, 190.0, accessories_title_y + 10.0)
        
        # بيانات المحتويات والملحقات
        accessories_info_y = accessories_title_y + 20.0
        pdf.set_font('Arial', 'B', 11)
        pdf.set_text_color(0, 0, 0)
        
        # جدول المحتويات
        accessory_items = [
            ["إطار احتياطي", has_spare_tire],
            ["طفاية حريق", has_fire_extinguisher],
            ["حقيبة إسعافات أولية", has_first_aid_kit],
            ["مثلث تحذيري", has_warning_triangle],
            ["عدة أدوات", has_tools]
        ]
        
        # تحديد عرض الجدول
        col1_width = 30.0  # عمود الحالة
        col2_width = 60.0  # عمود البيان
        
        # رسم جدول المحتويات
        pdf.set_fill_color(*pdf.primary_color)
        pdf.set_text_color(255, 255, 255)  # لون أبيض للنص
        pdf.set_xy(80.0, accessories_info_y)
        pdf.cell(col1_width, 10.0, get_display(arabic_reshaper.reshape("الحالة")), 1, 0, 'C', True)
        pdf.cell(col2_width, 10.0, get_display(arabic_reshaper.reshape("البيان")), 1, 1, 'C', True)
        
        # بيانات جدول المحتويات
        pdf.set_text_color(0, 0, 0)  # إعادة النص للون الأسود
        for i, item in enumerate(accessory_items):
            fill = i % 2 == 1  # صفوف بديلة
            if fill:
                pdf.set_fill_color(*pdf.table_row_alt_color)
            else:
                pdf.set_fill_color(255, 255, 255)  # خلفية بيضاء للصفوف غير المظللة
            
            pdf.set_xy(80.0, pdf.get_y())
            pdf.cell(col1_width, 10.0, get_display(arabic_reshaper.reshape(item[1])), 1, 0, 'C', fill)
            pdf.cell(col2_width, 10.0, get_display(arabic_reshaper.reshape(item[0])), 1, 1, 'R', fill)
        
        # قسم حالة السيارة
        condition_title_y = pdf.get_y() + 15.0
        pdf.set_font('Arial', 'B', 14)
        pdf.set_text_color(*pdf.primary_color)
        pdf.arabic_text(190.0, condition_title_y, "حالة السيارة", 'R')
        
        # إضافة خط تحت العنوان
        pdf.set_draw_color(*pdf.primary_color)
        pdf.line(60.0, condition_title_y + 10.0, 190.0, condition_title_y + 10.0)
        
        # حالة السيارة
        pdf.set_xy(20.0, condition_title_y + 15.0)
        pdf.set_font('Arial', '', 11)
        pdf.set_text_color(0, 0, 0)
        
        # إطار لوصف حالة السيارة
        pdf.rect(20.0, condition_title_y + 15.0, 170.0, 25.0)
        pdf.set_xy(25.0, condition_title_y + 20.0)
        pdf.multi_cell(160.0, 5.0, get_display(arabic_reshaper.reshape(vehicle_condition)), 0, 'R')
        
        # الملاحظات
        notes_y = condition_title_y + 50.0
        if notes:
            pdf.set_font('Arial', 'B', 12)
            pdf.set_text_color(*pdf.primary_color)
            pdf.arabic_text(190.0, notes_y, "ملاحظات:", 'R')
            
            pdf.set_xy(20.0, notes_y + 5.0)
            pdf.set_font('Arial', '', 10)
            pdf.set_text_color(0, 0, 0)
            
            # إطار للملاحظات
            pdf.rect(20.0, notes_y + 5.0, 170.0, 20.0)
            pdf.set_xy(25.0, notes_y + 10.0)
            pdf.multi_cell(160.0, 5.0, get_display(arabic_reshaper.reshape(notes)), 0, 'R')
        
        # رابط النموذج الإلكتروني
        if form_link:
            form_link_y = notes_y + 35.0 if notes else notes_y + 10.0
            pdf.set_font('Arial', 'B', 11)
            pdf.set_text_color(*pdf.primary_color)
            pdf.arabic_text(190.0, form_link_y, "رابط النموذج الإلكتروني:", 'R')
            
            pdf.set_font('Arial', '', 10)
            pdf.set_text_color(0, 0, 255)  # لون أزرق للرابط
            pdf.arabic_text(100.0, form_link_y, form_link, 'R')
        
        # التوقيعات
        signature_y = pdf.get_y() + 20.0
        pdf.set_font('Arial', 'B', 11)
        pdf.set_text_color(*pdf.secondary_color)
        
        if handover_type == 'استلام':
            pdf.arabic_text(170.0, signature_y, "توقيع المستلم", 'C')
            pdf.arabic_text(40.0, signature_y, "توقيع مسؤول السيارات", 'C')
        else:
            pdf.arabic_text(170.0, signature_y, "توقيع المسلم", 'C')
            pdf.arabic_text(40.0, signature_y, "توقيع مسؤول السيارات", 'C')
        
        # خطوط التوقيع
        pdf.set_xy(20.0, signature_y + 10.0)
        pdf.cell(60.0, 10.0, "__________________", 0, 0, 'C')
        pdf.cell(50.0, 10.0, "", 0, 0, 'C')  # فراغ في الوسط
        pdf.cell(60.0, 10.0, "__________________", 0, 1, 'C')
        
        # التذييل
        pdf.set_xy(10.0, 270.0)
        pdf.set_font('Arial', '', 8)
        pdf.set_text_color(*pdf.secondary_color)
        current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        pdf.arabic_text(200.0, pdf.get_y(), "تم إنشاء هذا المستند في " + current_timestamp, 'C')
        current_year = str(datetime.now().year)
        pdf.arabic_text(200.0, pdf.get_y() + 5.0, "شركة التقنية المتطورة - جميع الحقوق محفوظة © " + current_year, 'C')
        
        # إنشاء الملف كبيانات ثنائية
        buffer = BytesIO()
        pdf.output(buffer)
        buffer.seek(0)
        
        return buffer.getvalue()
        
    except Exception as e:
        print(f"خطأ في إنشاء نموذج تسليم/استلام PDF: {str(e)}")
        raise e