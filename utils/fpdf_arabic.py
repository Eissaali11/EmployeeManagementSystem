"""
وحدة إنشاء ملفات PDF مع دعم للنصوص العربية باستخدام FPDF
"""
from io import BytesIO
import os
from datetime import datetime
import arabic_reshaper
from bidi.algorithm import get_display
from fpdf import FPDF

class ArabicPDF(FPDF):
    """فئة PDF مخصصة لدعم اللغة العربية"""
    
    def __init__(self, orientation='P', unit='mm', format='A4'):
        super().__init__(orientation=orientation, unit=unit, format=format)
        # إضافة الخط العربي
        self.add_font('Arial', '', os.path.join('static', 'fonts', 'arial.ttf'), uni=True)
        self.add_font('Arial', 'B', os.path.join('static', 'fonts', 'arialbd.ttf'), uni=True)
    
    def arabic_text(self, x, y, txt, align='R'):
        """طباعة نص عربي"""
        # تشكيل النص العربي للعرض الصحيح
        reshaped_text = arabic_reshaper.reshape(txt)
        bidi_text = get_display(reshaped_text)
        
        # حفظ الموضع الحالي
        self.set_xy(x, y)
        
        # ضبط المحاذاة
        self.cell(0, 10, bidi_text, 0, 1, align)

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
        
        # ضبط الخط
        pdf.set_font('Arial', '', 14)
        
        # العنوان
        pdf.set_font('Arial', 'B', 18)
        pdf.arabic_text(200, 20, "إشعار راتب", 'C')
        
        # معلومات الموظف
        pdf.set_font('Arial', 'B', 14)
        pdf.arabic_text(200, 40, "بيانات الموظف", 'R')
        
        pdf.set_font('Arial', '', 12)
        pdf.arabic_text(200, 50, f"الاسم: {data.get('employee_name', '')}", 'R')
        pdf.arabic_text(200, 60, f"الرقم الوظيفي: {data.get('employee_id', '')}", 'R')
        
        if data.get('department_name'):
            pdf.arabic_text(200, 70, f"القسم: {data.get('department_name', '')}", 'R')
            y_pos = 80
        else:
            y_pos = 70
            
        pdf.arabic_text(200, y_pos, f"المسمى الوظيفي: {data.get('job_title', '')}", 'R')
        
        # تفاصيل الراتب
        y_pos += 20
        pdf.set_font('Arial', 'B', 14)
        pdf.arabic_text(200, y_pos, f"تفاصيل راتب شهر: {data.get('month_name', '')} {data.get('year', '')}", 'C')
        
        # جدول الراتب
        headers = ["البند", "المبلغ"]
        items = [
            ["الراتب الأساسي", f"{data.get('basic_salary', 0):.2f}"],
            ["البدلات", f"{data.get('allowances', 0):.2f}"],
            ["المكافآت", f"{data.get('bonus', 0):.2f}"],
            ["الخصومات", f"{data.get('deductions', 0):.2f}"],
            ["صافي الراتب", f"{data.get('net_salary', 0):.2f}"]
        ]
        
        # رسم الجدول
        y_pos += 15
        pdf.set_font('Arial', 'B', 12)
        
        # رأس الجدول
        pdf.set_fill_color(200, 200, 200)  # لون رمادي فاتح
        pdf.set_xy(110, y_pos)
        pdf.cell(40, 10, get_display(arabic_reshaper.reshape(headers[1])), 1, 0, 'C', True)
        pdf.cell(60, 10, get_display(arabic_reshaper.reshape(headers[0])), 1, 1, 'C', True)
        
        # بيانات الجدول
        pdf.set_font('Arial', '', 10)
        for i, item in enumerate(items):
            fill = False
            if i == len(items) - 1:  # صف المجموع
                pdf.set_font('Arial', 'B', 10)
                fill = True
            
            pdf.set_xy(110, pdf.get_y())
            pdf.cell(40, 10, item[1], 1, 0, 'C', fill)
            pdf.cell(60, 10, get_display(arabic_reshaper.reshape(item[0])), 1, 1, 'R', fill)
        
        # إضافة الملاحظات إذا وجدت
        if data.get('notes'):
            pdf.set_xy(40, pdf.get_y() + 10)
            pdf.set_font('Arial', 'B', 12)
            pdf.arabic_text(200, pdf.get_y(), "ملاحظات:", 'R')
            
            pdf.set_xy(40, pdf.get_y() + 5)
            pdf.set_font('Arial', '', 10)
            pdf.arabic_text(200, pdf.get_y(), data.get('notes', ''), 'R')
        
        # التوقيعات
        pdf.set_xy(40, pdf.get_y() + 30)
        pdf.set_font('Arial', '', 12)
        pdf.cell(50, 10, get_display(arabic_reshaper.reshape("توقيع الموظف")), 0, 0, 'C')
        pdf.cell(70, 10, "", 0, 0, 'C')  # فراغ في الوسط
        pdf.cell(50, 10, get_display(arabic_reshaper.reshape("توقيع المدير المالي")), 0, 1, 'C')
        
        pdf.set_xy(40, pdf.get_y())
        pdf.cell(50, 10, "________________", 0, 0, 'C')
        pdf.cell(70, 10, "", 0, 0, 'C')  # فراغ في الوسط
        pdf.cell(50, 10, "________________", 0, 1, 'C')
        
        # التذييل
        pdf.set_xy(10, 270)
        pdf.set_font('Arial', '', 8)
        pdf.set_text_color(150, 150, 150)  # لون رمادي
        pdf.arabic_text(200, pdf.get_y(), f"تم إصدار هذا الإشعار بتاريخ {data.get('current_date', datetime.now().strftime('%Y-%m-%d'))}", 'C')
        pdf.arabic_text(200, pdf.get_y() + 5, "نظام إدارة الموظفين - جميع الحقوق محفوظة", 'C')
        
        # حفظ PDF إلى متغير
        pdf_bytes = pdf.output('', 'S').encode('latin1')  # FPDF ترجع سلسلة لاتينية
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
        
        # ضبط الخط
        pdf.set_font('Arial', 'B', 18)
        
        # العنوان
        pdf.arabic_text(280, 20, "تقرير الرواتب", 'C')
        
        # العنوان الفرعي
        pdf.set_font('Arial', 'B', 14)
        pdf.arabic_text(280, 30, f"شهر {month_name} {year}", 'C')
        
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
        y_pos = 50
        
        # عرض الأعمدة
        col_widths = [15, 60, 25, 25, 25, 25, 25, 30]  # مجموع العرض = 230 (مليمتر تقريباً)
        
        # رأس الجدول
        pdf.set_fill_color(200, 200, 200)  # لون رمادي فاتح
        x_pos = 30  # بداية من اليسار
        
        for i, header in reversed(list(enumerate(headers))):
            pdf.set_xy(x_pos, y_pos)
            pdf.cell(col_widths[i], 10, get_display(arabic_reshaper.reshape(header)), 1, 0, 'C', True)
            x_pos += col_widths[i]
        
        # بيانات الجدول
        pdf.set_font('Arial', '', 10)
        for idx, salary in enumerate(salaries_data):
            y_pos += 10
            fill = idx % 2 == 1  # صفوف بديلة
            if fill:
                pdf.set_fill_color(240, 240, 240)  # لون رمادي فاتح جداً
            
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
        pdf.set_fill_color(200, 200, 200)  # لون رمادي فاتح
        
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
        pdf.set_font('Arial', 'B', 10)
        for i, cell_data in reversed(list(enumerate(summary_data))):
            pdf.set_xy(x_pos, y_pos)
            if i == 1:  # نص "المجموع"
                text = get_display(arabic_reshaper.reshape(cell_data))
                align = 'R'
            else:
                text = cell_data
                align = 'C'
            pdf.cell(col_widths[i], 10, text, 1, 0, align, 1)
            x_pos += col_widths[i]
        
        # ملخص الرواتب
        pdf.set_font('Arial', 'B', 14)
        pdf.arabic_text(280, y_pos + 20, "ملخص الرواتب", 'R')
        
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
        summary_y = y_pos + 30
        
        # رأس جدول الملخص
        pdf.set_fill_color(200, 200, 200)  # لون رمادي فاتح
        pdf.set_xy(210, summary_y)
        pdf.cell(30, 10, get_display(arabic_reshaper.reshape(summary_headers[1])), 1, 0, 'C', 1)
        pdf.cell(50, 10, get_display(arabic_reshaper.reshape(summary_headers[0])), 1, 1, 'C', 1)
        
        # بيانات جدول الملخص
        pdf.set_font('Arial', '', 10)
        for i, item in enumerate(summary_items):
            fill = i % 2 == 1  # صفوف بديلة
            if fill:
                pdf.set_fill_color(240, 240, 240)  # لون رمادي فاتح جداً
            
            if i == len(summary_items) - 1:  # الصف الأخير
                pdf.set_fill_color(200, 200, 200)  # لون رمادي فاتح
                fill = True
                pdf.set_font('Arial', 'B', 10)
            
            pdf.set_xy(210, pdf.get_y())
            pdf.cell(30, 10, item[1], 1, 0, 'C', fill)
            pdf.cell(50, 10, get_display(arabic_reshaper.reshape(item[0])), 1, 1, 'R', fill)
        
        # التذييل
        pdf.set_xy(10, 190)  # تقريباً أسفل الصفحة
        pdf.set_font('Arial', '', 8)
        pdf.set_text_color(150, 150, 150)  # لون رمادي
        pdf.arabic_text(280, pdf.get_y(), f"تم إنشاء هذا التقرير في {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 'C')
        pdf.arabic_text(280, pdf.get_y() + 5, "نظام إدارة الموظفين - جميع الحقوق محفوظة", 'C')
        
        # حفظ PDF إلى متغير
        pdf_bytes = pdf.output('', 'S').encode('latin1')  # FPDF ترجع سلسلة لاتينية
        return pdf_bytes
        
    except Exception as e:
        print(f"خطأ في إنشاء تقرير الرواتب PDF: {str(e)}")
        raise e