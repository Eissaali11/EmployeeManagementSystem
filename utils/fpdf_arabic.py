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
        self.add_font('Tajawal', '', os.path.join('static', 'fonts', 'Tajawal-Regular.ttf'), uni=True)
        self.add_font('Tajawal', 'B', os.path.join('static', 'fonts', 'Tajawal-Bold.ttf'), uni=True)
        
        # تحديد الألوان الرئيسية في النظام
        self.primary_color = (29, 161, 142)  # اللون الأخضر من شعار RASSCO
        self.secondary_color = (100, 100, 100)  # لون رمادي
        self.table_header_color = (230, 230, 230)  # لون رمادي فاتح لرؤوس الجداول
        self.table_row_alt_color = (245, 245, 245)  # لون رمادي فاتح جداً للصفوف البديلة
    
    def arabic_text(self, x, y, txt, align='R'):
        """طباعة نص عربي"""
        # تشكيل النص العربي للعرض الصحيح
        reshaped_text = arabic_reshaper.reshape(txt)
        bidi_text = get_display(reshaped_text)
        
        # حفظ الموضع الحالي
        self.set_xy(x, y)
        
        # ضبط المحاذاة
        self.cell(0, 10, bidi_text, 0, 1, align)
    
    def add_company_header(self, title, subtitle=None):
        """إضافة ترويسة الشركة مع الشعار والعنوان"""
        # إضافة الشعار
        logo_path = os.path.join('static', 'images', 'logo.png')
        
        # تحديد موضع العنوان حسب اتجاه الصفحة
        title_x = 200  # القيمة الافتراضية لصفحة عمودية
        if self.page_no() > 0 and getattr(self, 'cur_orientation', 'P') == 'L':
            title_x = 280  # للصفحة الأفقية
        
        if os.path.exists(logo_path):
            # حساب موضع الشعار حسب اتجاه الصفحة
            logo_width = 50
            logo_x = 10
            
            # إضافة الشعار بحجم مناسب
            self.image(logo_path, logo_x, 10, logo_width)
            
            # إضافة خط أفقي أسفل الترويسة
            self.set_draw_color(*self.primary_color)
            self.set_line_width(0.5)
            
            # تحديد طول الخط حسب اتجاه الصفحة
            line_end = 200  # للصفحة العمودية
            if self.page_no() > 0 and getattr(self, 'cur_orientation', 'P') == 'L':
                line_end = 280  # للصفحة الأفقية
                
            self.line(10, 30, line_end, 30)
        
        # إضافة العنوان الرئيسي
        self.set_font('Tajawal', 'B', 18)
        self.set_text_color(*self.primary_color)
        self.arabic_text(title_x, 15, title, 'C')
        
        # إضافة العنوان الفرعي إذا كان موجوداً
        if subtitle:
            self.set_font('Tajawal', '', 14)
            self.set_text_color(*self.secondary_color)
            self.arabic_text(title_x, 25, subtitle, 'C')
        
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
        # إنشاء PDF جديد
        pdf = ArabicPDF()
        pdf.add_page()
        
        # إضافة ترويسة الشركة
        subtitle = f"إشعار راتب - شهر {data.get('month_name', '')} {data.get('year', '')}"
        y_pos = pdf.add_company_header("نظام إدارة الموظفين RASSCO", subtitle)
        
        # إضافة إطار للمستند
        pdf.set_draw_color(*pdf.primary_color)
        pdf.set_line_width(0.3)
        pdf.rect(10, 40, 190, 230)  # إطار خارجي
        
        # معلومات الموظف
        pdf.set_font('Tajawal', 'B', 14)
        pdf.set_text_color(*pdf.primary_color)
        pdf.arabic_text(190, y_pos + 5, "بيانات الموظف", 'R')
        
        # إضافة خط تحت عنوان بيانات الموظف
        pdf.set_draw_color(*pdf.primary_color)
        pdf.line(60, y_pos + 15, 190, y_pos + 15)
        
        # بيانات الموظف
        pdf.set_font('Tajawal', '', 12)
        pdf.set_text_color(0, 0, 0)
        
        # إنشاء جدول لبيانات الموظف (أكثر تنظيماً)
        emp_info_y = y_pos + 20
        pdf.set_xy(20, emp_info_y)
        
        # العمود الأول
        pdf.set_font('Tajawal', 'B', 11)
        pdf.arabic_text(190, emp_info_y, f"الاسم:", 'R')
        pdf.set_font('Tajawal', '', 11)
        pdf.arabic_text(140, emp_info_y, f"{data.get('employee_name', '')}", 'R')
        
        pdf.set_font('Tajawal', 'B', 11)
        pdf.arabic_text(100, emp_info_y, f"الرقم الوظيفي:", 'R')
        pdf.set_font('Tajawal', '', 11)
        pdf.arabic_text(50, emp_info_y, f"{data.get('employee_id', '')}", 'R')
        
        # العمود الثاني
        emp_info_y += 12
        if data.get('department_name'):
            pdf.set_font('Tajawal', 'B', 11)
            pdf.arabic_text(190, emp_info_y, f"القسم:", 'R')
            pdf.set_font('Tajawal', '', 11)
            pdf.arabic_text(140, emp_info_y, f"{data.get('department_name', '')}", 'R')
        
        pdf.set_font('Tajawal', 'B', 11)
        pdf.arabic_text(100, emp_info_y, f"المسمى الوظيفي:", 'R')
        pdf.set_font('Tajawal', '', 11)
        pdf.arabic_text(50, emp_info_y, f"{data.get('job_title', '')}", 'R')
        
        # تفاصيل الراتب
        salary_title_y = emp_info_y + 25
        pdf.set_font('Tajawal', 'B', 14)
        pdf.set_text_color(*pdf.primary_color)
        pdf.arabic_text(190, salary_title_y, "تفاصيل الراتب", 'C')
        
        # خط تحت عنوان تفاصيل الراتب
        pdf.set_draw_color(*pdf.primary_color)
        pdf.line(60, salary_title_y + 10, 140, salary_title_y + 10)
        
        # جدول الراتب
        headers = ["البند", "المبلغ"]
        items = [
            ["الراتب الأساسي", f"{data.get('basic_salary', 0):.2f}"],
            ["البدلات", f"{data.get('allowances', 0):.2f}"],
            ["المكافآت", f"{data.get('bonus', 0):.2f}"],
            ["الخصومات", f"{data.get('deductions', 0):.2f}"],
            ["صافي الراتب", f"{data.get('net_salary', 0):.2f}"]
        ]
        
        # رسم الجدول بتصميم أفضل
        table_y = salary_title_y + 20
        pdf.set_font('Tajawal', 'B', 11)
        pdf.set_text_color(0, 0, 0)
        
        # رأس الجدول
        pdf.set_fill_color(*pdf.primary_color)
        pdf.set_text_color(255, 255, 255)  # لون أبيض للنص
        pdf.set_xy(50, table_y)
        pdf.cell(50, 10, get_display(arabic_reshaper.reshape(headers[1])), 1, 0, 'C', True)
        pdf.cell(70, 10, get_display(arabic_reshaper.reshape(headers[0])), 1, 1, 'C', True)
        
        # بيانات الجدول
        pdf.set_text_color(0, 0, 0)  # إعادة لون النص إلى الأسود
        pdf.set_font('Tajawal', '', 11)
        for i, item in enumerate(items):
            fill = i % 2 == 1  # صفوف بديلة
            
            if i == len(items) - 1:  # صف المجموع
                pdf.set_font('Tajawal', 'B', 11)
                pdf.set_fill_color(*pdf.primary_color)
                pdf.set_text_color(255, 255, 255)  # لون أبيض للنص
                fill = True
            elif fill:
                pdf.set_fill_color(*pdf.table_row_alt_color)
            
            pdf.set_xy(50, pdf.get_y())
            pdf.cell(50, 10, item[1], 1, 0, 'C', fill)
            pdf.cell(70, 10, get_display(arabic_reshaper.reshape(item[0])), 1, 1, 'R', fill)
        
        pdf.set_text_color(0, 0, 0)  # إعادة لون النص إلى الأسود
        
        # إضافة الملاحظات إذا وجدت
        if data.get('notes'):
            notes_y = pdf.get_y() + 10
            pdf.set_font('Tajawal', 'B', 12)
            pdf.set_text_color(*pdf.primary_color)
            pdf.arabic_text(190, notes_y, "ملاحظات:", 'R')
            
            pdf.set_xy(20, notes_y + 5)
            pdf.set_font('Tajawal', '', 10)
            pdf.set_text_color(0, 0, 0)  # لون أسود للنص
            
            # إطار للملاحظات
            notes_text = data.get('notes', '')
            pdf.rect(20, notes_y + 5, 170, 20)
            pdf.set_xy(25, notes_y + 10)
            pdf.multi_cell(160, 5, get_display(arabic_reshaper.reshape(notes_text)), 0, 'R')
        
        # التوقيعات
        signature_y = pdf.get_y() + 30
        if signature_y < 230:  # التأكد من أن التوقيعات ليست قريبة جداً من نهاية الصفحة
            signature_y = 230
        
        pdf.set_xy(20, signature_y)
        pdf.set_font('Tajawal', 'B', 11)
        pdf.set_text_color(*pdf.secondary_color)
        pdf.cell(50, 10, get_display(arabic_reshaper.reshape("توقيع الموظف")), 0, 0, 'C')
        pdf.cell(70, 10, "", 0, 0, 'C')  # فراغ في الوسط
        pdf.cell(50, 10, get_display(arabic_reshaper.reshape("توقيع المدير المالي")), 0, 1, 'C')
        
        pdf.set_xy(20, pdf.get_y())
        pdf.cell(50, 10, "________________", 0, 0, 'C')
        pdf.cell(70, 10, "", 0, 0, 'C')  # فراغ في الوسط
        pdf.cell(50, 10, "________________", 0, 1, 'C')
        
        # التذييل
        pdf.set_xy(10, 270)
        pdf.set_font('Tajawal', '', 8)
        pdf.set_text_color(*pdf.secondary_color)
        current_date = data.get('current_date', datetime.now().strftime('%Y-%m-%d'))
        pdf.arabic_text(200, pdf.get_y(), f"تم إصدار هذا الإشعار بتاريخ {current_date}", 'C')
        pdf.arabic_text(200, pdf.get_y() + 5, "شركة RASSCO - جميع الحقوق محفوظة © " + str(datetime.now().year), 'C')
        
        # حفظ PDF إلى متغير
        pdf_output = pdf.output('', 'S')
        if isinstance(pdf_output, str):
            pdf_bytes = pdf_output.encode('latin1')  # FPDF ترجع سلسلة لاتينية في بعض الإصدارات
        else:
            pdf_bytes = pdf_output  # في الإصدارات الأحدث قد ترجع بيانات ثنائية مباشرة
        return pdf_bytes
        
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
        # إنشاء PDF جديد
        pdf = ArabicPDF('L')  # وضع أفقي
        pdf.add_page()
        
        # إضافة ترويسة الشركة
        subtitle = f"تقرير الرواتب - شهر {month_name} {year}"
        y_pos = pdf.add_company_header("نظام إدارة الموظفين RASSCO", subtitle)
        
        # إضافة إطار للمستند
        pdf.set_draw_color(*pdf.primary_color)
        pdf.set_line_width(0.3)
        pdf.rect(10, 40, 277, 150)  # إطار خارجي للتقرير
        
        # إعداد جدول الرواتب
        headers = ["م", "اسم الموظف", "الرقم الوظيفي", "الراتب الأساسي", "البدلات", "الخصومات", "المكافآت", "صافي الراتب"]
        
        # حساب المجاميع
        total_basic = sum(salary.get('basic_salary', 0) for salary in salaries_data)
        total_allowances = sum(salary.get('allowances', 0) for salary in salaries_data)
        total_deductions = sum(salary.get('deductions', 0) for salary in salaries_data)
        total_bonus = sum(salary.get('bonus', 0) for salary in salaries_data)
        total_net = sum(salary.get('net_salary', 0) for salary in salaries_data)
        
        # ضبط موضع الجدول
        pdf.set_font('Tajawal', 'B', 10)
        y_pos = 50
        
        # عرض الأعمدة
        col_widths = [15, 60, 25, 25, 25, 25, 25, 30]  # مجموع العرض = 230 (مليمتر تقريباً)
        
        # رأس الجدول
        pdf.set_fill_color(*pdf.primary_color)
        pdf.set_text_color(255, 255, 255)  # لون أبيض للنص
        x_pos = 30  # بداية من اليسار
        
        for i, header in reversed(list(enumerate(headers))):
            pdf.set_xy(x_pos, y_pos)
            pdf.cell(col_widths[i], 10, get_display(arabic_reshaper.reshape(header)), 1, 0, 'C', True)
            x_pos += col_widths[i]
        
        # بيانات الجدول
        pdf.set_text_color(0, 0, 0)  # إعادة النص للون الأسود
        pdf.set_font('Tajawal', '', 10)
        for idx, salary in enumerate(salaries_data):
            y_pos += 10
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
            
            x_pos = 30
            for i, cell_data in reversed(list(enumerate(row_data))):
                pdf.set_xy(x_pos, y_pos)
                if i == 1 or i == 2:  # اسم الموظف والرقم الوظيفي
                    text = get_display(arabic_reshaper.reshape(cell_data))
                    align = 'R'
                else:
                    text = cell_data
                    align = 'C'
                pdf.cell(col_widths[i], 10, text, 1, 0, align, fill)
                x_pos += col_widths[i]
        
        # صف المجموع
        y_pos += 10
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
        
        x_pos = 30
        pdf.set_font('Tajawal', 'B', 10)
        for i, cell_data in reversed(list(enumerate(summary_data))):
            pdf.set_xy(x_pos, y_pos)
            if i == 1:  # نص "المجموع"
                text = get_display(arabic_reshaper.reshape(cell_data))
                align = 'R'
            else:
                text = cell_data
                align = 'C'
            pdf.cell(col_widths[i], 10, text, 1, 0, align, True)
            x_pos += col_widths[i]
        
        # ملخص الرواتب
        pdf.set_text_color(*pdf.primary_color)
        pdf.set_font('Tajawal', 'B', 14)
        pdf.arabic_text(280, y_pos + 20, "ملخص الرواتب", 'R')
        
        # إضافة خط تحت عنوان ملخص الرواتب
        pdf.set_draw_color(*pdf.primary_color)
        pdf.line(210, y_pos + 28, 280, y_pos + 28)
        
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
        pdf.set_font('Tajawal', 'B', 10)
        summary_y = y_pos + 35
        
        # رأس جدول الملخص
        pdf.set_fill_color(*pdf.primary_color)
        pdf.set_text_color(255, 255, 255)  # لون أبيض للنص
        pdf.set_xy(210, summary_y)
        pdf.cell(30, 10, get_display(arabic_reshaper.reshape(summary_headers[1])), 1, 0, 'C', True)
        pdf.cell(50, 10, get_display(arabic_reshaper.reshape(summary_headers[0])), 1, 1, 'C', True)
        
        # بيانات جدول الملخص
        pdf.set_text_color(0, 0, 0)  # إعادة النص للون الأسود
        pdf.set_font('Tajawal', '', 10)
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
                pdf.set_font('Tajawal', 'B', 10)
            
            pdf.set_xy(210, pdf.get_y())
            pdf.cell(30, 10, item[1], 1, 0, 'C', fill)
            pdf.cell(50, 10, get_display(arabic_reshaper.reshape(item[0])), 1, 1, 'R', fill)
        
        # معلومات التقرير
        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Tajawal', '', 10)
        pdf.set_xy(20, y_pos + 35)
        pdf.arabic_text(150, y_pos + 35, f"إجمالي عدد الموظفين: {len(salaries_data)}", 'R')
        pdf.arabic_text(150, y_pos + 45, f"متوسط الراتب الأساسي: {total_basic/len(salaries_data):.2f}" if len(salaries_data) > 0 else "متوسط الراتب الأساسي: 0.00", 'R')
        pdf.arabic_text(150, y_pos + 55, f"متوسط صافي الراتب: {total_net/len(salaries_data):.2f}" if len(salaries_data) > 0 else "متوسط صافي الراتب: 0.00", 'R')
        
        # التذييل
        pdf.set_xy(10, 190)  # تقريباً أسفل الصفحة
        pdf.set_font('Tajawal', '', 8)
        pdf.set_text_color(*pdf.secondary_color)
        current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        pdf.arabic_text(280, pdf.get_y(), f"تم إنشاء هذا التقرير في {current_timestamp}", 'C')
        pdf.arabic_text(280, pdf.get_y() + 5, "شركة RASSCO - جميع الحقوق محفوظة © " + str(datetime.now().year), 'C')
        
        # حفظ PDF إلى متغير
        pdf_output = pdf.output('', 'S')
        if isinstance(pdf_output, str):
            pdf_bytes = pdf_output.encode('latin1')  # FPDF ترجع سلسلة لاتينية في بعض الإصدارات
        else:
            pdf_bytes = pdf_output  # في الإصدارات الأحدث قد ترجع بيانات ثنائية مباشرة
        return pdf_bytes
        
    except Exception as e:
        print(f"خطأ في إنشاء تقرير الرواتب PDF: {str(e)}")
        raise e