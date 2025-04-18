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
        
        # إنشاء الملف كبيانات ثنائية
        # استخدام dest='S' لإرجاع المحتوى كسلسلة نصية ثم تحويله إلى بايت
        pdf_bytes = pdf.output(dest='S').encode('latin1')
        
        return pdf_bytes
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
    from utils.pdf_generator_new import ArabicPDF
    
    try:
        # تحويل المدخلات إلى النوع المناسب
        month_str = str(month)
        year_str = str(year)
        
        # إنشاء PDF جديد في الوضع الأفقي
        pdf = ArabicPDF('L')
        pdf.add_page()
        
        # إضافة ترويسة الشركة
        subtitle = "تقرير الرواتب - شهر " + str(month_str) + " " + str(year_str)
        y_pos = pdf.add_company_header("نظام إدارة الموظفين - شركة التقنية المتطورة", subtitle)
        
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
        pdf.set_font('Arial', 'B', 10)  # استخدام خط Arial بدلاً من Amiri
        pdf.set_text_color(255, 255, 255)  # لون النص أبيض
        
        # كتابة رأس الجدول
        x_pos = 10
        for i, header in enumerate(headers):
            pdf.arabic_text(x_pos + col_widths[i]/2, y_start + 5, header, 'C')
            x_pos += col_widths[i]
        
        # بداية صفوف البيانات
        y_pos = y_start + 10
        pdf.set_text_color(0, 0, 0)  # لون النص أسود
        pdf.set_font('Amiri', '', 10)
        
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
            row_data = [
                str(idx + 1),
                salary.get('employee_name', ''),
                salary.get('employee_id', ''),
                "{:,.2f}".format(float(salary.get('basic_salary', 0))),
                "{:,.2f}".format(float(salary.get('allowances', 0))),
                "{:,.2f}".format(float(salary.get('bonus', 0))),
                "{:,.2f}".format(float(salary.get('deductions', 0))),
                "{:,.2f}".format(float(salary.get('net_salary', 0)))
            ]
            
            # تجميع المبالغ
            total_basic += float(salary.get('basic_salary', 0))
            total_allowances += float(salary.get('allowances', 0))
            total_bonus += float(salary.get('bonus', 0))
            total_deductions += float(salary.get('deductions', 0))
            total_net += float(salary.get('net_salary', 0))
            
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
                pdf.set_font('Amiri', '', 10)
        
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
        pdf.arabic_text(280.0, pdf.get_y() + 5.0, "شركة التقنية المتطورة - جميع الحقوق محفوظة © " + current_year, 'C')
        
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