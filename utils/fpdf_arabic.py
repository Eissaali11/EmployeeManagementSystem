"""
وحدة إنشاء ملفات PDF مع دعم للنصوص العربية باستخدام FPDF
يتضمن تنسيق جداول منظمة وإضافة شعار الشركة
"""
from io import BytesIO
import os
from datetime import datetime
import arabic_reshaper
from bidi.algorithm import get_display
from fpdf import FPDF

class ArabicPDF(FPDF):
    """فئة PDF مخصصة لدعم اللغة العربية مع تحسينات التصميم"""
    
    def __init__(self, orientation='P', unit='mm', format='A4'):
        # القيم المقبولة للاتجاه هي 'P' (عمودي) أو 'L' (أفقي)
        o = orientation.upper() if isinstance(orientation, str) else 'P'
        if o not in ['P', 'L']:
            o = 'P'
        
        # تحويل الوحدة إلى قيمة معترف بها
        u = unit.lower() if isinstance(unit, str) else 'mm'
        if u not in ['pt', 'mm', 'cm', 'in']:
            u = 'mm'
        
        # تحويل الصيغة إلى قيمة معترف بها
        f = format.upper() if isinstance(format, str) else 'A4'
        
        # استدعاء المُنشئ الأصلي مع المعاملات الصحيحة
        super().__init__(orientation=o, unit=u, format=f)
        # إضافة الخط العربي
        self.add_font('Arial', '', os.path.join('static', 'fonts', 'arial.ttf'), uni=True)
        self.add_font('Arial', 'B', os.path.join('static', 'fonts', 'arialbd.ttf'), uni=True)
        
        # تحديد الألوان الرئيسية في النظام
        self.primary_color = (29, 161, 142)  # اللون الأخضر من شعار RASSCO
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
        self.set_font('Arial', 'B', 14)  # تقليل حجم الخط قليلاً
        self.set_text_color(*self.primary_color)
        
        # تحسين موضع العنوان بحيث لا يتداخل مع اللوجو أو حافة الصفحة
        if is_landscape:
            self.arabic_text(245, 15, title, 'C')  # ضبط بشكل أفضل
        else:
            self.arabic_text(150, 18, title, 'C')  # ضبط بشكل أفضل
        
        # إضافة العنوان الفرعي إذا كان موجوداً
        if subtitle:
            self.set_font('Arial', '', 11)  # تقليل حجم خط العنوان الفرعي
            self.set_text_color(*self.secondary_color)
            
            # تحسين موضع العنوان الفرعي لمنع التداخل
            if is_landscape:
                self.arabic_text(245, 24, subtitle, 'C')  # زيادة المسافة بين العنوان والعنوان الفرعي
            else:
                self.arabic_text(150, 26, subtitle, 'C')  # زيادة المسافة بين العنوان والعنوان الفرعي
        
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
        department_name = str(data.get('department_name', '')) if data.get('department_name') else None
        month_name = str(data.get('month_name', ''))
        year = str(data.get('year', ''))
        basic_salary = float(data.get('basic_salary', 0))
        allowances = float(data.get('allowances', 0))
        deductions = float(data.get('deductions', 0))
        bonus = float(data.get('bonus', 0))
        net_salary = float(data.get('net_salary', 0))
        notes = str(data.get('notes', '')) if data.get('notes') else None
        current_date = str(data.get('current_date', datetime.now().strftime('%Y-%m-%d')))
        
        # إنشاء PDF جديد
        pdf = ArabicPDF()
        pdf.add_page()
        
        # إضافة ترويسة الشركة
        subtitle = "إشعار راتب - شهر " + month_name + " " + year
        y_pos = pdf.add_company_header("نُظم - نظام إدارة متكامل", subtitle)
        
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
        pdf.line(60.0, float(y_pos) + 15.0, 190.0, float(y_pos) + 15.0)
        
        # بيانات الموظف
        pdf.set_font('Arial', '', 12)
        pdf.set_text_color(0, 0, 0)
        
        # إنشاء جدول لبيانات الموظف (أكثر تنظيماً)
        emp_info_y = float(y_pos) + 20.0
        pdf.set_xy(20.0, float(emp_info_y))
        
        # العمود الأول
        pdf.set_font('Arial', 'B', 11)
        pdf.arabic_text(190.0, float(emp_info_y), "الاسم:", 'R')
        pdf.set_font('Arial', '', 11)
        pdf.arabic_text(140.0, float(emp_info_y), employee_name, 'R')
        
        pdf.set_font('Arial', 'B', 11)
        pdf.arabic_text(100.0, float(emp_info_y), "الرقم الوظيفي:", 'R')
        pdf.set_font('Arial', '', 11)
        pdf.arabic_text(50.0, float(emp_info_y), employee_id, 'R')
        
        # العمود الثاني
        emp_info_y += 12.0
        if department_name:
            pdf.set_font('Arial', 'B', 11)
            pdf.arabic_text(190.0, float(emp_info_y), "القسم:", 'R')
            pdf.set_font('Arial', '', 11)
            pdf.arabic_text(140.0, float(emp_info_y), department_name, 'R')
        
        pdf.set_font('Arial', 'B', 11)
        pdf.arabic_text(100.0, float(emp_info_y), "المسمى الوظيفي:", 'R')
        pdf.set_font('Arial', '', 11)
        pdf.arabic_text(50.0, float(emp_info_y), job_title, 'R')
        
        # تفاصيل الراتب
        salary_title_y = float(emp_info_y) + 25.0
        pdf.set_font('Arial', 'B', 14)
        pdf.set_text_color(*pdf.primary_color)
        pdf.arabic_text(190.0, float(salary_title_y), "تفاصيل الراتب", 'C')
        
        # خط تحت عنوان تفاصيل الراتب
        pdf.set_draw_color(*pdf.primary_color)
        pdf.line(60.0, float(salary_title_y) + 10.0, 140.0, float(salary_title_y) + 10.0)
        
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
        pdf.line(70.0, float(title_y) + 10.0, 140.0, float(title_y) + 10.0)
        
        # نترك مسافة قبل بداية الجدول
        table_y = float(title_y) + 15.0
        
        # تحديد عرض الجدول بشكل يتناسب مع المحتوى
        amount_width = 40.0  # عرض عمود المبلغ
        item_width = 85.0    # عرض عمود البيان
        row_height = 10.0    # ارتفاع الصف
        
        # حساب موقع بداية الجدول في منتصف الصفحة
        table_width = float(amount_width) + float(item_width)
        x_start = float(pdf.page_width - table_width) / 2.0
        
        # إنشاء جدول جديد بتصميم محسن
        pdf.set_xy(float(x_start), float(table_y))
        pdf.set_fill_color(*pdf.primary_color)
        pdf.set_text_color(255, 255, 255)  # لون أبيض للنص
        pdf.set_font('Arial', 'B', 12)
        
        # رسم رأس الجدول - لكن عكس ترتيب الأعمدة ليتناسب مع اللغة العربية
        pdf.cell(float(amount_width), float(row_height), get_display(arabic_reshaper.reshape("المبلغ")), 1, 0, 'C', True)
        pdf.cell(float(item_width), float(row_height), get_display(arabic_reshaper.reshape("البيان")), 1, 1, 'C', True)
        
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
            pdf.set_xy(float(x_start), float(pdf.get_y()))
            pdf.cell(float(amount_width), float(row_height), item[1], 1, 0, 'C', fill)
            pdf.cell(float(item_width), float(row_height), get_display(arabic_reshaper.reshape(item[0])), 1, 1, 'R', fill)
        
        # إعادة ضبط نمط النص
        pdf.set_text_color(0, 0, 0)
        
        # إضافة الملاحظات إذا وجدت
        if notes:
            notes_y = float(pdf.get_y()) + 10.0
            pdf.set_font('Arial', 'B', 12)
            pdf.set_text_color(*pdf.primary_color)
            pdf.arabic_text(190.0, float(notes_y), "ملاحظات:", 'R')
            
            pdf.set_xy(20.0, float(notes_y) + 5.0)
            pdf.set_font('Arial', '', 10)
            pdf.set_text_color(0, 0, 0)  # لون أسود للنص
            
            # إطار للملاحظات
            pdf.rect(20.0, float(notes_y) + 5.0, 170.0, 20.0)
            pdf.set_xy(25.0, float(notes_y) + 10.0)
            pdf.multi_cell(160.0, 5.0, get_display(arabic_reshaper.reshape(notes)), 0, 'R')
        
        # التوقيعات
        signature_y = float(pdf.get_y()) + 30.0
        if signature_y < 230.0:  # التأكد من أن التوقيعات ليست قريبة جداً من نهاية الصفحة
            signature_y = 230.0
        
        pdf.set_xy(20.0, float(signature_y))
        pdf.set_font('Arial', 'B', 11)
        pdf.set_text_color(*pdf.secondary_color)
        pdf.cell(50.0, 10.0, get_display(arabic_reshaper.reshape("توقيع الموظف")), 0, 0, 'C')
        pdf.cell(70.0, 10.0, "", 0, 0, 'C')  # فراغ في الوسط
        pdf.cell(50.0, 10.0, get_display(arabic_reshaper.reshape("توقيع المدير المالي")), 0, 1, 'C')
        
        pdf.set_xy(20.0, float(pdf.get_y()))
        pdf.cell(50.0, 10.0, "________________", 0, 0, 'C')
        pdf.cell(70.0, 10.0, "", 0, 0, 'C')  # فراغ في الوسط
        pdf.cell(50.0, 10.0, "________________", 0, 1, 'C')
        
        # التذييل
        pdf.set_xy(10.0, 270.0)
        pdf.set_font('Arial', '', 8)
        pdf.set_text_color(*pdf.secondary_color)
        
        pdf.arabic_text(200.0, float(pdf.get_y()), "تم إصدار هذا الإشعار بتاريخ " + current_date, 'C')
        current_year_str = str(datetime.now().year)
        pdf.arabic_text(200.0, float(pdf.get_y()) + 5.0, "شركة RASSCO - جميع الحقوق محفوظة © " + current_year_str, 'C')
        
        # إنشاء الملف كبيانات ثنائية
        buffer = BytesIO()
        pdf.output(buffer)
        buffer.seek(0)
        
        return buffer.getvalue()
        
    except Exception as e:
        print(f"خطأ في إنشاء إشعار راتب PDF: {str(e)}")
        raise e


def generate_salary_report_pdf(salaries_data, month_name, year):
    """
    إنشاء تقرير رواتب كملف PDF باستخدام FPDF
    
    Args:
        salaries_data: قائمة بقواميس تحتوي على بيانات الرواتب
        month_name: اسم الشهر
        year: السنة
        
    Returns:
        bytes يحتوي على ملف PDF
    """
    try:
        # تحويل المدخلات إلى النوع المناسب
        month_name = str(month_name)
        year = str(year)
        
        # إنشاء PDF جديد
        pdf = ArabicPDF('L')  # وضع أفقي
        pdf.add_page()
        
        # إضافة ترويسة الشركة
        subtitle = "تقرير الرواتب - شهر " + month_name + " " + year
        y_pos = pdf.add_company_header("نُظم - نظام إدارة متكامل", subtitle)
        
        # إضافة إطار للمستند
        pdf.set_draw_color(*pdf.primary_color)
        pdf.set_line_width(0.3)
        pdf.rect(10.0, 40.0, 277.0, 150.0)  # إطار خارجي للتقرير
        
        # إعداد جدول الرواتب
        headers = ["م", "اسم الموظف", "الرقم الوظيفي", "الراتب الأساسي", "البدلات", "الخصومات", "المكافآت", "صافي الراتب"]
        
        # حساب المجاميع
        total_basic = sum(salary.get('basic_salary', 0) for salary in salaries_data)
        total_allowances = sum(salary.get('allowances', 0) for salary in salaries_data)
        total_deductions = sum(salary.get('deductions', 0) for salary in salaries_data)
        total_bonus = sum(salary.get('bonus', 0) for salary in salaries_data)
        total_net = sum(salary.get('net_salary', 0) for salary in salaries_data)
        
        # ضبط موضع الجدول
        pdf.set_font('Arial', 'B', 10)
        y_pos = 50.0
        
        # عرض الأعمدة
        col_widths = [15.0, 60.0, 25.0, 25.0, 25.0, 25.0, 25.0, 30.0]  # مجموع العرض = 230 (مليمتر تقريباً)
        
        # رأس الجدول
        pdf.set_fill_color(*pdf.primary_color)
        pdf.set_text_color(255, 255, 255)  # لون أبيض للنص
        x_pos = 30.0  # بداية من اليسار (قيمة عائمة)
        
        for i, header in reversed(list(enumerate(headers))):
            pdf.set_xy(float(x_pos), float(y_pos))
            pdf.cell(float(col_widths[i]), 10.0, get_display(arabic_reshaper.reshape(header)), 1, 0, 'C', True)
            x_pos += float(col_widths[i])
        
        # بيانات الجدول
        pdf.set_text_color(0, 0, 0)  # إعادة النص للون الأسود
        pdf.set_font('Arial', '', 10)
        for idx, salary in enumerate(salaries_data):
            y_pos += 10.0
            fill = idx % 2 == 1  # صفوف بديلة
            if fill:
                pdf.set_fill_color(*pdf.table_row_alt_color)
            else:
                pdf.set_fill_color(255, 255, 255)  # خلفية بيضاء للصفوف غير المظللة
            
            # بيانات الصف
            row_data = [
                str(idx + 1),
                salary.get('employee_name', ''),
                salary.get('employee_id', ''),
                f"{salary.get('basic_salary', 0):.2f}",
                f"{salary.get('allowances', 0):.2f}",
                f"{salary.get('deductions', 0):.2f}",
                f"{salary.get('bonus', 0):.2f}",
                f"{salary.get('net_salary', 0):.2f}"
            ]
            
            x_pos = 30.0  # تحويل إلى رقم عائم
            for i, cell_data in reversed(list(enumerate(row_data))):
                pdf.set_xy(float(x_pos), float(y_pos))
                if i == 1 or i == 2:  # اسم الموظف والرقم الوظيفي
                    text = get_display(arabic_reshaper.reshape(str(cell_data)))
                    align = 'R'
                else:
                    text = str(cell_data)  # تحويل إلى نص بغض النظر عن النوع
                    align = 'C'
                pdf.cell(float(col_widths[i]), 10.0, text, 1, 0, align, fill)
                x_pos += float(col_widths[i])
        
        # صف المجموع
        y_pos += 10.0
        pdf.set_fill_color(*pdf.primary_color)
        pdf.set_text_color(255, 255, 255)  # لون أبيض للنص
        
        # بيانات المجموع
        summary_data = [
            "",
            "المجموع",
            "",
            f"{total_basic:.2f}",
            f"{total_allowances:.2f}",
            f"{total_deductions:.2f}",
            f"{total_bonus:.2f}",
            f"{total_net:.2f}"
        ]
        
        x_pos = 30.0  # تحويل إلى رقم عائم
        pdf.set_font('Arial', 'B', 10)
        for i, cell_data in reversed(list(enumerate(summary_data))):
            pdf.set_xy(float(x_pos), float(y_pos))
            if i == 1:  # نص "المجموع"
                text = get_display(arabic_reshaper.reshape(str(cell_data)))
                align = 'R'
            else:
                text = str(cell_data)  # تحويل إلى نص بغض النظر عن النوع
                align = 'C'
            pdf.cell(float(col_widths[i]), 10.0, text, 1, 0, align, True)
            x_pos += float(col_widths[i])
        
        # ملخص الرواتب - إصدار محسن بشكل كبير
        
        # احتساب مكان الجدول بما يتناسب مع عدد الموظفين وحجم الصفحة
        if len(salaries_data) > 5:
            summary_y = 135.0  # إذا كان هناك عدد كبير من الموظفين، نضع الجدول في مكان ثابت
        else:
            summary_y = float(y_pos) + 35.0  # مكان متناسب مع موضع جدول الرواتب
        
        # تقسيم الصفحة إلى عمودين واضحين
        # الجانب الأيمن للملخص (ثلثي عرض الصفحة)
        right_column_width = pdf.content_width * 0.6
        
        # الجانب الأيسر للإحصائيات (ثلث عرض الصفحة)
        left_column_width = pdf.content_width * 0.4
        
        # ================ قسم ملخص الرواتب ================
        # عنوان ملخص الرواتب - مع ضبط موضع أفضل
        summary_title_x = float(pdf.page_width) - 70.0
        summary_title_y = float(summary_y) - 15.0
        
        pdf.set_text_color(*pdf.primary_color)
        pdf.set_font('Arial', 'B', 12)  # تصغير حجم الخط قليلاً
        # استخدام عرض محدد للنص لضمان عدم التداخل
        pdf.arabic_text(summary_title_x, summary_title_y, "ملخص الرواتب", 'R', 100)
        
        # إضافة خط تحت عنوان ملخص الرواتب
        pdf.set_draw_color(*pdf.primary_color)
        pdf.line(float(summary_title_x) - 60.0, float(summary_title_y) + 6.0, float(summary_title_x), float(summary_title_y) + 6.0)
        
        # جدول الملخص
        summary_headers = ["البيان", "المبلغ"]
        summary_items = [
            ["إجمالي الرواتب الأساسية", f"{total_basic:.2f}"],
            ["إجمالي البدلات", f"{total_allowances:.2f}"],
            ["إجمالي الخصومات", f"{total_deductions:.2f}"],
            ["إجمالي المكافآت", f"{total_bonus:.2f}"],
            ["إجمالي صافي الرواتب", f"{total_net:.2f}"]
        ]
        
        # رسم جدول الملخص
        pdf.set_font('Arial', 'B', 10)
        
        # ضبط أبعاد وموضع جدول الملخص بشكل أفضل
        col1_width = 40.0  # عمود المبلغ
        col2_width = 70.0  # عمود البيان
        summary_table_width = float(col1_width) + float(col2_width)
        
        # ضبط موضع X بشكل أفضل لتفادي التداخل مع أي عناصر أخرى
        # احتساب موضع الجدول من اليمين للتوافق مع اللغة العربية
        summary_table_x = float(pdf.page_width) - 80.0 - float(summary_table_width)
        
        pdf.set_fill_color(*pdf.primary_color)
        pdf.set_text_color(255, 255, 255)  # لون أبيض للنص
        pdf.set_xy(float(summary_table_x), float(summary_y))
        pdf.cell(float(col1_width), 10.0, get_display(arabic_reshaper.reshape(summary_headers[1])), 1, 0, 'C', True)
        pdf.cell(float(col2_width), 10.0, get_display(arabic_reshaper.reshape(summary_headers[0])), 1, 1, 'C', True)
        
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
            pdf.set_xy(float(summary_table_x), pdf.get_y())
            pdf.cell(float(col1_width), 10.0, item[1], 1, 0, 'C', fill)
            pdf.cell(float(col2_width), 10.0, get_display(arabic_reshaper.reshape(item[0])), 1, 1, 'R', fill)
        
        # معلومات التقرير - جعلها في عمود منفصل وواضح
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Arial', 'B', 10)
        
        # عنوان المعلومات
        info_x = 30.0
        info_y = float(summary_y)
        pdf.set_xy(float(info_x), float(info_y) - 15.0)
        pdf.set_text_color(*pdf.primary_color)
        pdf.arabic_text(120.0, float(info_y) - 15.0, "معلومات التقرير", 'R')
        
        # إضافة خط تحت عنوان معلومات التقرير
        pdf.set_draw_color(*pdf.primary_color)
        pdf.line(50.0, float(info_y) - 7.0, 120.0, float(info_y) - 7.0)
        
        # إطار للمعلومات
        pdf.set_draw_color(*pdf.secondary_color)
        pdf.rect(float(info_x), float(info_y), 110.0, 45.0)
        
        # معلومات التقرير داخل إطار
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Arial', '', 10)
        pdf.arabic_text(120.0, float(info_y) + 10.0, f"إجمالي عدد الموظفين: {len(salaries_data)}", 'R')
        
        # التأكد من عدم القسمة على صفر
        if len(salaries_data) > 0:
            avg_basic = float(total_basic)/float(len(salaries_data))
            avg_net = float(total_net)/float(len(salaries_data))
        else:
            avg_basic = 0.0
            avg_net = 0.0
            
        pdf.arabic_text(120.0, float(info_y) + 25.0, f"متوسط الراتب الأساسي: {avg_basic:.2f}", 'R')
        pdf.arabic_text(120.0, float(info_y) + 40.0, f"متوسط صافي الراتب: {avg_net:.2f}", 'R')
        
        # التذييل
        pdf.set_xy(10.0, 190.0)  # تقريباً أسفل الصفحة - هذه القيم بالفعل float
        pdf.set_font('Arial', '', 8)
        pdf.set_text_color(*pdf.secondary_color)
        current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        pdf.arabic_text(280.0, float(pdf.get_y()), f"تم إنشاء هذا التقرير في {current_timestamp}", 'C')
        current_year = datetime.now().year
        pdf.arabic_text(280.0, float(pdf.get_y()) + 5.0, f"شركة RASSCO - جميع الحقوق محفوظة © {current_year}", 'C')
        
        # إنشاء الملف كبيانات ثنائية
        buffer = BytesIO()
        pdf.output(buffer)
        buffer.seek(0)
        
        return buffer.getvalue()
        
    except Exception as e:
        print(f"خطأ في إنشاء تقرير الرواتب PDF: {str(e)}")
        raise e