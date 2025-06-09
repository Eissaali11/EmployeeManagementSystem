"""
وحدة إنشاء ملفات PDF باستخدام ReportLab Canvas مباشرة
مع دعم للنصوص العربية
"""
import os
from io import BytesIO
import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
from reportlab.lib.units import cm
from reportlab.lib import colors
from datetime import datetime

# تسجيل الخطوط العربية
ARABIC_FONT = 'Helvetica'  # الخط الافتراضي

try:
    # قائمة بالخطوط العربية المتاحة
    arabic_fonts = [
        {'name': 'ArefRuqaa', 'path': os.path.join('static', 'fonts', 'ArefRuqaa-Regular.ttf')},
        {'name': 'Tajawal', 'path': os.path.join('static', 'fonts', 'Tajawal-Regular.ttf')}
    ]
    
    # محاولة تسجيل الخطوط العربية
    for font in arabic_fonts:
        if os.path.exists(font['path']):
            pdfmetrics.registerFont(TTFont(font['name'], font['path']))
            ARABIC_FONT = font['name']
            print(f"Registered Arabic font for Canvas PDF: {font['name']}")
            break
    
    # إذا لم يتم العثور على أي خط عربي
    if ARABIC_FONT == 'Helvetica':
        print("Warning: No Arabic fonts found, using default font")
        
except Exception as e:
    print(f"Error registering fonts: {str(e)}")


def reshape_arabic_text(text):
    """
    تشكيل النص العربي بشكل صحيح للعرض في ملفات PDF
    
    Args:
        text: النص العربي المراد تشكيله
        
    Returns:
        النص بعد التشكيل
    """
    if not text:
        return ""
    try:
        # تشكيل النص العربي
        reshaped_text = arabic_reshaper.reshape(str(text))
        # عكس النص لدعم اللغة العربية (من اليمين إلى اليسار)
        bidi_text = get_display(reshaped_text)
        return bidi_text
    except Exception as e:
        print(f"Error reshaping text: {str(e)}")
        return str(text)  # إرجاع النص الأصلي في حالة الخطأ


def generate_salary_notification_pdf(data):
    """
    إنشاء إشعار راتب كملف PDF باستخدام Canvas
    
    Args:
        data: قاموس يحتوي على بيانات الراتب
        
    Returns:
        BytesIO يحتوي على ملف PDF
    """
    try:
        # إنشاء كائن BytesIO لاحتواء البيانات
        buffer = BytesIO()
        
        # إنشاء كائن الرسم
        c = canvas.Canvas(buffer, pagesize=A4)
        c.setTitle(reshape_arabic_text("إشعار راتب"))
        
        # تعيين الخط العربي
        c.setFont(ARABIC_FONT, 18)
        
        # موقع العنوان (في وسط الصفحة)
        page_width, page_height = A4
        title_text = reshape_arabic_text("إشعار راتب")
        c.drawCentredString(page_width/2, page_height - 2*cm, title_text)
        
        # معلومات الموظف
        c.setFont(ARABIC_FONT, 12)
        y_position = page_height - 4*cm
        
        # رسم مستطيل لمعلومات الموظف
        c.setFillColorRGB(0.95, 0.95, 0.95)  # لون رمادي فاتح
        c.rect(2*cm, y_position - 3*cm, page_width - 4*cm, 3*cm, fill=1, stroke=1)
        c.setFillColorRGB(0, 0, 0)  # إعادة اللون إلى الأسود
        
        # عنوان بيانات الموظف
        c.setFont(ARABIC_FONT, 14)
        c.drawRightString(page_width - 2*cm, y_position, reshape_arabic_text("بيانات الموظف"))
        c.setFont(ARABIC_FONT, 12)
        
        # إنشاء النصوص
        y_position -= 0.7*cm
        employee_name = data.get('employee_name', '')
        c.drawRightString(page_width - 2*cm, y_position, reshape_arabic_text(f"الاسم: {employee_name}"))
        
        y_position -= 0.7*cm
        employee_id = data.get('employee_id', '')
        c.drawRightString(page_width - 2*cm, y_position, reshape_arabic_text(f"الرقم الوظيفي: {employee_id}"))
        
        y_position -= 0.7*cm
        if data.get('department_name'):
            c.drawRightString(page_width - 2*cm, y_position, reshape_arabic_text(f"القسم: {data.get('department_name')}"))
            y_position -= 0.7*cm
            
        job_title = data.get('job_title', '')
        c.drawRightString(page_width - 2*cm, y_position, reshape_arabic_text(f"المسمى الوظيفي: {job_title}"))
        
        # معلومات الراتب
        y_position -= 1.5*cm
        c.setFont(ARABIC_FONT, 14)
        month_name = data.get('month_name', '')
        year = data.get('year', '')
        c.drawCentredString(page_width/2, y_position, reshape_arabic_text(f"تفاصيل راتب شهر: {month_name} {year}"))
        
        # رسم جدول تفاصيل الراتب
        y_position -= 1*cm
        
        # رسم الإطار الخارجي للجدول
        table_width = page_width - 4*cm
        table_height = 4*cm
        c.rect(2*cm, y_position - table_height, table_width, table_height)
        
        # رسم الصفوف
        for i in range(6):  # 6 صفوف: العنوان و5 بنود
            row_y = y_position - (i * table_height/6)
            c.line(2*cm, row_y, 2*cm + table_width, row_y)
        
        # رسم الأعمدة
        column_width = table_width * 0.7
        c.line(2*cm + column_width, y_position, 2*cm + column_width, y_position - table_height)
        
        # رسم العناوين
        c.setFillColorRGB(0.9, 0.9, 0.9)  # لون رمادي فاتح للعناوين
        c.rect(2*cm, y_position, table_width, table_height/6, fill=1, stroke=0)
        c.setFillColorRGB(0, 0, 0)  # إعادة اللون إلى الأسود
        
        c.setFont(ARABIC_FONT, 12)
        c.drawRightString(2*cm + table_width - 0.5*cm, y_position - table_height/12, reshape_arabic_text("البند"))
        c.drawCentredString(2*cm + column_width + (table_width - column_width)/2, y_position - table_height/12, reshape_arabic_text("المبلغ"))
        
        # بيانات الجدول
        c.setFont(ARABIC_FONT, 10)
        
        # الراتب الأساسي
        basic_salary = data.get('basic_salary', 0)
        row_y = y_position - table_height/6
        c.drawRightString(2*cm + table_width - 0.5*cm, row_y - table_height/12, reshape_arabic_text("الراتب الأساسي"))
        c.drawCentredString(2*cm + column_width + (table_width - column_width)/2, row_y - table_height/12, f"{basic_salary:.2f}")
        
        # البدلات
        allowances = data.get('allowances', 0)
        row_y -= table_height/6
        c.drawRightString(2*cm + table_width - 0.5*cm, row_y - table_height/12, reshape_arabic_text("البدلات"))
        c.drawCentredString(2*cm + column_width + (table_width - column_width)/2, row_y - table_height/12, f"{allowances:.2f}")
        
        # المكافآت
        bonus = data.get('bonus', 0)
        row_y -= table_height/6
        c.drawRightString(2*cm + table_width - 0.5*cm, row_y - table_height/12, reshape_arabic_text("المكافآت"))
        c.drawCentredString(2*cm + column_width + (table_width - column_width)/2, row_y - table_height/12, f"{bonus:.2f}")
        
        # الخصومات
        deductions = data.get('deductions', 0)
        row_y -= table_height/6
        c.drawRightString(2*cm + table_width - 0.5*cm, row_y - table_height/12, reshape_arabic_text("الخصومات"))
        c.drawCentredString(2*cm + column_width + (table_width - column_width)/2, row_y - table_height/12, f"{deductions:.2f}")
        
        # صافي الراتب
        net_salary = data.get('net_salary', 0)
        row_y -= table_height/6
        
        # لون خلفية لصافي الراتب
        c.setFillColorRGB(0.9, 0.9, 0.9)  # لون رمادي فاتح
        c.rect(2*cm, row_y, table_width, table_height/6, fill=1, stroke=0)
        c.setFillColorRGB(0, 0, 0)  # إعادة اللون إلى الأسود
        
        c.drawRightString(2*cm + table_width - 0.5*cm, row_y - table_height/12, reshape_arabic_text("صافي الراتب"))
        c.drawCentredString(2*cm + column_width + (table_width - column_width)/2, row_y - table_height/12, f"{net_salary:.2f}")
        
        # ملاحظات
        if data.get('notes'):
            y_position = y_position - table_height - 1*cm
            c.setFont(ARABIC_FONT, 12)
            c.drawRightString(page_width - 2*cm, y_position, reshape_arabic_text("ملاحظات:"))
            
            y_position -= 0.7*cm
            c.setFont(ARABIC_FONT, 10)
            notes = data.get('notes', '')
            c.drawRightString(page_width - 2*cm, y_position, reshape_arabic_text(notes))
        
        # التوقيعات
        y_position = 5*cm
        c.setFont(ARABIC_FONT, 12)
        
        # توقيع المدير المالي
        c.drawCentredString(page_width/4, y_position, reshape_arabic_text("توقيع المدير المالي"))
        c.line(page_width/4 - 2*cm, y_position - 1*cm, page_width/4 + 2*cm, y_position - 1*cm)
        
        # توقيع الموظف
        c.drawCentredString(3*page_width/4, y_position, reshape_arabic_text("توقيع الموظف"))
        c.line(3*page_width/4 - 2*cm, y_position - 1*cm, 3*page_width/4 + 2*cm, y_position - 1*cm)
        
        # التذييل
        c.setFont(ARABIC_FONT, 8)
        c.setFillColorRGB(0.5, 0.5, 0.5)  # لون رمادي
        c.drawCentredString(page_width/2, 2*cm, reshape_arabic_text(f"تم إصدار هذا الإشعار في {data.get('current_date', datetime.now().strftime('%Y-%m-%d'))}"))
        c.drawCentredString(page_width/2, 1.5*cm, reshape_arabic_text("نُظم - جميع الحقوق محفوظة"))
        
        # إتمام الصفحة
        c.save()
        
        # إعادة توجيه المؤشر إلى بداية البيانات
        buffer.seek(0)
        return buffer.getvalue()
        
    except Exception as e:
        print(f"Error creating salary notification PDF: {str(e)}")
        raise e


def generate_salary_report_pdf(salaries_data, month_name, year):
    """
    إنشاء تقرير رواتب كملف PDF باستخدام Canvas
    
    Args:
        salaries_data: قائمة بقواميس تحتوي على بيانات الرواتب
        month_name: اسم الشهر
        year: السنة
        
    Returns:
        BytesIO يحتوي على ملف PDF
    """
    try:
        # إنشاء كائن BytesIO لاحتواء البيانات
        buffer = BytesIO()
        
        # إنشاء كائن الرسم بوضع أفقي (landscape)
        page_width, page_height = landscape(A4)
        c = canvas.Canvas(buffer, pagesize=landscape(A4))
        c.setTitle(reshape_arabic_text("تقرير الرواتب"))
        
        # تعيين الخط العربي
        c.setFont(ARABIC_FONT, 18)
        
        # موقع العنوان (في وسط الصفحة)
        c.drawCentredString(page_width/2, page_height - 2*cm, reshape_arabic_text("تقرير الرواتب"))
        
        # عنوان فرعي
        c.setFont(ARABIC_FONT, 14)
        c.drawCentredString(page_width/2, page_height - 3*cm, reshape_arabic_text(f"شهر {month_name} {year}"))
        
        # رسم جدول الرواتب
        c.setFont(ARABIC_FONT, 10)
        
        # حساب أبعاد الجدول
        margin = 2*cm
        table_width = page_width - 2*margin
        header_height = 1*cm
        row_height = 0.7*cm
        
        # عدد الصفوف يعتمد على عدد الرواتب + صف العنوان + صف المجموع
        rows_count = len(salaries_data) + 2
        table_height = header_height + (rows_count - 1) * row_height
        
        # تحديد موقع الجدول
        table_y = page_height - 4*cm - table_height
        
        # رسم الإطار الخارجي للجدول
        c.rect(margin, table_y, table_width, table_height)
        
        # عرض الأعمدة
        columns = 8  # عدد الأعمدة
        column_widths = [
            table_width * 0.05,  # م
            table_width * 0.23,  # اسم الموظف
            table_width * 0.12,  # الرقم الوظيفي
            table_width * 0.12,  # الراتب الأساسي
            table_width * 0.12,  # البدلات
            table_width * 0.12,  # الخصومات
            table_width * 0.12,  # المكافآت
            table_width * 0.12,  # صافي الراتب
        ]
        
        # رسم الأعمدة الرأسية
        x_pos = margin
        for width in column_widths[:-1]:  # لا نرسم الخط بعد العمود الأخير
            x_pos += width
            c.line(x_pos, table_y, x_pos, table_y + table_height)
        
        # رسم صف العنوان
        c.setFillColorRGB(0.9, 0.9, 0.9)  # لون رمادي فاتح للعناوين
        c.rect(margin, table_y + table_height - header_height, table_width, header_height, fill=1, stroke=0)
        c.setFillColorRGB(0, 0, 0)  # إعادة اللون إلى الأسود
        
        # عناوين الأعمدة
        column_titles = ["م", "اسم الموظف", "الرقم الوظيفي", "الراتب الأساسي", "البدلات", "الخصومات", "المكافآت", "صافي الراتب"]
        x_pos = margin
        for i, title in enumerate(column_titles):
            # وسط العمود
            column_center = x_pos + column_widths[i]/2
            c.drawCentredString(column_center, table_y + table_height - header_height/2, reshape_arabic_text(title))
            x_pos += column_widths[i]
        
        # رسم الصفوف الأفقية
        for i in range(rows_count):
            row_y = table_y + table_height - header_height - i * row_height
            c.line(margin, row_y, margin + table_width, row_y)
        
        # حساب المجاميع
        total_basic = sum(salary.get('basic_salary', 0) for salary in salaries_data)
        total_allowances = sum(salary.get('allowances', 0) for salary in salaries_data)
        total_deductions = sum(salary.get('deductions', 0) for salary in salaries_data)
        total_bonus = sum(salary.get('bonus', 0) for salary in salaries_data)
        total_net = sum(salary.get('net_salary', 0) for salary in salaries_data)
        
        # بيانات الرواتب
        for i, salary in enumerate(salaries_data):
            row_y = table_y + table_height - header_height - (i + 0.5) * row_height
            
            # رقم الصف
            column_center = margin + column_widths[0]/2
            c.drawCentredString(column_center, row_y, str(i+1))
            
            # اسم الموظف
            column_center = margin + column_widths[0] + column_widths[1]/2
            c.drawCentredString(column_center, row_y, reshape_arabic_text(salary.get('employee_name', '')))
            
            # الرقم الوظيفي
            column_center = margin + column_widths[0] + column_widths[1] + column_widths[2]/2
            c.drawCentredString(column_center, row_y, reshape_arabic_text(salary.get('employee_id', '')))
            
            # الراتب الأساسي
            column_center = margin + sum(column_widths[:3]) + column_widths[3]/2
            c.drawCentredString(column_center, row_y, f"{salary.get('basic_salary', 0):.2f}")
            
            # البدلات
            column_center = margin + sum(column_widths[:4]) + column_widths[4]/2
            c.drawCentredString(column_center, row_y, f"{salary.get('allowances', 0):.2f}")
            
            # الخصومات
            column_center = margin + sum(column_widths[:5]) + column_widths[5]/2
            c.drawCentredString(column_center, row_y, f"{salary.get('deductions', 0):.2f}")
            
            # المكافآت
            column_center = margin + sum(column_widths[:6]) + column_widths[6]/2
            c.drawCentredString(column_center, row_y, f"{salary.get('bonus', 0):.2f}")
            
            # صافي الراتب
            column_center = margin + sum(column_widths[:7]) + column_widths[7]/2
            c.drawCentredString(column_center, row_y, f"{salary.get('net_salary', 0):.2f}")
            
            # تلوين الصفوف بالتناوب
            if i % 2 == 1:
                # لون فاتح للصفوف الزوجية
                c.setFillColorRGB(0.95, 0.95, 0.95)
                c.rect(margin, table_y + table_height - header_height - (i+1) * row_height, 
                      table_width, row_height, fill=1, stroke=0)
                c.setFillColorRGB(0, 0, 0)  # إعادة اللون إلى الأسود
        
        # صف المجموع
        summary_row_y = table_y + row_height/2
        
        # لون خلفية لصف المجموع
        c.setFillColorRGB(0.9, 0.9, 0.9)
        c.rect(margin, table_y, table_width, row_height, fill=1, stroke=0)
        c.setFillColorRGB(0, 0, 0)
        
        # نص المجموع
        column_center = margin + column_widths[0] + column_widths[1]/2
        c.drawCentredString(column_center, summary_row_y, reshape_arabic_text("المجموع"))
        
        # مجموع الراتب الأساسي
        column_center = margin + sum(column_widths[:3]) + column_widths[3]/2
        c.drawCentredString(column_center, summary_row_y, f"{total_basic:.2f}")
        
        # مجموع البدلات
        column_center = margin + sum(column_widths[:4]) + column_widths[4]/2
        c.drawCentredString(column_center, summary_row_y, f"{total_allowances:.2f}")
        
        # مجموع الخصومات
        column_center = margin + sum(column_widths[:5]) + column_widths[5]/2
        c.drawCentredString(column_center, summary_row_y, f"{total_deductions:.2f}")
        
        # مجموع المكافآت
        column_center = margin + sum(column_widths[:6]) + column_widths[6]/2
        c.drawCentredString(column_center, summary_row_y, f"{total_bonus:.2f}")
        
        # مجموع صافي الراتب
        column_center = margin + sum(column_widths[:7]) + column_widths[7]/2
        c.drawCentredString(column_center, summary_row_y, f"{total_net:.2f}")
        
        # ملخص البيانات
        summary_y = table_y - 2*cm
        c.setFont(ARABIC_FONT, 14)
        c.drawRightString(page_width - margin, summary_y, reshape_arabic_text("ملخص الرواتب"))
        
        # جدول الملخص
        summary_table_width = page_width * 0.4
        summary_table_x = page_width - margin - summary_table_width
        summary_rows = 6
        summary_row_height = 0.7*cm
        summary_table_height = summary_rows * summary_row_height
        
        # رسم الإطار الخارجي لجدول الملخص
        c.rect(summary_table_x, summary_y - summary_table_height - 0.5*cm, summary_table_width, summary_table_height)
        
        # رسم الصفوف الأفقية
        for i in range(summary_rows):
            row_y = summary_y - 0.5*cm - i * summary_row_height
            c.line(summary_table_x, row_y, summary_table_x + summary_table_width, row_y)
        
        # رسم العمود الرأسي
        column_width = summary_table_width * 0.7
        c.line(summary_table_x + column_width, summary_y - 0.5*cm, 
              summary_table_x + column_width, summary_y - 0.5*cm - summary_table_height)
        
        # عناوين جدول الملخص
        c.setFont(ARABIC_FONT, 10)
        c.setFillColorRGB(0.9, 0.9, 0.9)
        c.rect(summary_table_x, summary_y - 0.5*cm - summary_row_height, 
              summary_table_width, summary_row_height, fill=1, stroke=0)
        c.setFillColorRGB(0, 0, 0)
        
        # العناوين
        column_center_title = summary_table_x + column_width/2
        column_center_value = summary_table_x + column_width + (summary_table_width - column_width)/2
        row_y = summary_y - 0.5*cm - summary_row_height/2
        c.drawRightString(summary_table_x + column_width - 0.5*cm, row_y, reshape_arabic_text("البيان"))
        c.drawCentredString(column_center_value, row_y, reshape_arabic_text("المبلغ"))
        
        # بيانات الملخص
        c.setFont(ARABIC_FONT, 9)
        summary_items = [
            {"title": "إجمالي الرواتب الأساسية", "value": total_basic},
            {"title": "إجمالي البدلات", "value": total_allowances},
            {"title": "إجمالي الخصومات", "value": total_deductions},
            {"title": "إجمالي المكافآت", "value": total_bonus},
            {"title": "إجمالي صافي الرواتب", "value": total_net}
        ]
        
        for i, item in enumerate(summary_items):
            row_y = summary_y - 0.5*cm - summary_row_height - (i + 0.5) * summary_row_height
            c.drawRightString(summary_table_x + column_width - 0.5*cm, row_y, reshape_arabic_text(item["title"]))
            c.drawCentredString(column_center_value, row_y, f"{item['value']:.2f}")
            
            # تلوين الصفوف بالتناوب
            if i % 2 == 1:
                # لون فاتح للصفوف الزوجية
                c.setFillColorRGB(0.95, 0.95, 0.95)
                c.rect(summary_table_x, summary_y - 0.5*cm - summary_row_height - (i+1) * summary_row_height, 
                      summary_table_width, summary_row_height, fill=1, stroke=0)
                c.setFillColorRGB(0, 0, 0)
        
        # تلوين خلفية الصف الأخير
        c.setFillColorRGB(0.9, 0.9, 0.9)
        c.rect(summary_table_x, summary_y - 0.5*cm - summary_table_height, 
              summary_table_width, summary_row_height, fill=1, stroke=0)
        c.setFillColorRGB(0, 0, 0)
        
        # التذييل
        c.setFont(ARABIC_FONT, 8)
        c.setFillColorRGB(0.5, 0.5, 0.5)  # لون رمادي
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        c.drawCentredString(page_width/2, 1.5*cm, reshape_arabic_text(f"تم إنشاء هذا التقرير في {current_date}"))
        c.drawCentredString(page_width/2, 1*cm, reshape_arabic_text("نُظم - جميع الحقوق محفوظة"))
        
        # إتمام الصفحة
        c.save()
        
        # إعادة توجيه المؤشر إلى بداية البيانات
        buffer.seek(0)
        return buffer.getvalue()
        
    except Exception as e:
        print(f"Error creating salary report PDF: {str(e)}")
        raise e