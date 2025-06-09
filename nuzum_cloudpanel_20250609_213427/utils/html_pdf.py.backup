"""
وحدة إنشاء ملفات PDF من قوالب Jinja مع دعم كامل للنصوص العربية
تستخدم FPDF بدلاً من weasyprint لتجنب الاعتماد على wkhtmltopdf
"""
from io import BytesIO
from datetime import datetime
from jinja2 import Template
import os
import base64
import arabic_reshaper
from bidi.algorithm import get_display
from fpdf import FPDF
import re

# استيراد وحدة FPDF المخصصة للعربية
from utils.fpdf_arabic import ArabicPDF, generate_salary_notification_pdf, generate_salary_report_pdf

def strip_html_tags(text):
    """
    إزالة وسوم HTML من النص
    
    Args:
        text: النص المراد معالجته
        
    Returns:
        النص بدون وسوم HTML
    """
    return re.sub(r'<.*?>', '', text) if text else ''

def process_html_table_to_data(html_table):
    """
    تحويل جدول HTML إلى بيانات مناسبة لـ FPDF
    
    Args:
        html_table: نص HTML يحتوي على جدول
        
    Returns:
        قائمة ببيانات الجدول
    """
    # تنفيذ منطق بسيط لاستخراج بيانات الجدول
    # هذه نسخة مبسطة جداً، يجب تطويرها حسب احتياجات المشروع
    rows = []
    # استخراج الصفوف بين <tr> و </tr>
    tr_pattern = r'<tr.*?>(.*?)</tr>'
    for tr_match in re.finditer(tr_pattern, html_table, re.DOTALL):
        row = []
        # استخراج الخلايا بين <td> و </td> أو <th> و </th>
        cell_pattern = r'<(?:td|th).*?>(.*?)</(?:td|th)>'
        for cell_match in re.finditer(cell_pattern, tr_match.group(1), re.DOTALL):
            cell_content = strip_html_tags(cell_match.group(1).strip())
            row.append(cell_content)
        if row:  # تجنب الصفوف الفارغة
            rows.append(row)
    return rows

def generate_html_pdf(template_str, data, filename=None, landscape=False):
    """
    إنشاء ملف PDF من قالب HTML مع دعم كامل للعربية
    باستخدام FPDF بدلاً من weasyprint لتجنب الاعتماد على wkhtmltopdf
    
    Args:
        template_str: قالب HTML كنص
        data: البيانات التي سيتم دمجها مع القالب
        filename: اسم الملف (اختياري، إذا كان None سيتم إرجاع البيانات فقط)
        landscape: هل التقرير بالوضع الأفقي (اختياري)
        
    Returns:
        BytesIO أو None
    """
    try:
        # تحديد نوع البيانات استناداً إلى محتوى data
        # نقوم بتحليل البيانات لنعرف ما إذا كان إشعار راتب أو تقرير رواتب
        if 'employee_name' in data and 'basic_salary' in data:
            # هذا إشعار راتب فردي - استخدام الدالة المخصصة
            pdf_bytes = generate_salary_notification_pdf(data)
        elif 'salaries' in data and 'month_name' in data and 'year' in data:
            # هذا تقرير رواتب - استخدام الدالة المخصصة
            pdf_bytes = generate_salary_report_pdf(data['salaries'], data['month_name'], data['year'])
        else:
            # في حالة أخرى، ننشئ PDF عام
            # هذا مجرد تنفيذ أساسي، يمكن توسيعه لأنواع أخرى من التقارير
            pdf = ArabicPDF('L' if landscape else 'P')
            pdf.add_page()
            
            # إضافة ترويسة
            title = data.get('title', 'تقرير النظام')
            subtitle = data.get('subtitle', '')
            pdf.add_company_header(title, subtitle)
            
            # إضافة المحتوى بطريقة مبسطة
            # هذه نسخة أولية، يمكن تحسينها لدعم المزيد من ميزات HTML
            pdf.set_font('Tajawal', '', 12)
            pdf.set_text_color(0, 0, 0)
            
            # إضافة نص المحتوى الرئيسي
            content = data.get('content', '')
            if content:
                pdf.set_xy(20, 50)
                pdf.multi_cell(pdf.content_width - 40, 10, get_display(arabic_reshaper.reshape(content)), 0, 'R')
            
            # التذييل
            pdf.set_xy(10, pdf.page_height - 20)
            pdf.set_font('Tajawal', '', 8)
            pdf.set_text_color(*pdf.secondary_color)
            current_date = datetime.now().strftime('%Y-%m-%d')
            pdf.arabic_text(pdf.page_width / 2, pdf.get_y(), f"تم إنشاء هذا التقرير بتاريخ {current_date}", 'C')
            pdf.arabic_text(pdf.page_width / 2, pdf.get_y() + 5, "نظام إدارة الموظفين - جميع الحقوق محفوظة", 'C')
            
            # إنتاج البيانات الثنائية
            pdf_output = pdf.output('', 'S')
            if isinstance(pdf_output, str):
                pdf_bytes = pdf_output.encode('latin1')
            else:
                pdf_bytes = pdf_output
        
        # معالجة البيانات الناتجة
        if filename:
            with open(filename, 'wb') as f:
                f.write(pdf_bytes)
            return None
        
        # إرجاع البيانات في buffer
        buffer = BytesIO(pdf_bytes)
        buffer.seek(0)
        return buffer
    
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        raise e

def get_salary_notification_template():
    """
    الحصول على قالب HTML لإشعار الراتب
    
    Returns:
        نص قالب HTML
    """
    return """
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>إشعار راتب</title>
        <style>
            @font-face {
                font-family: 'Tajawal';
                src: url('static/fonts/Tajawal-Regular.ttf') format('truetype');
            }
            body {
                font-family: 'Tajawal', sans-serif;
                direction: rtl;
                line-height: 1.6;
            }
        </style>
    </head>
    <body>
        <div class="logo">
            <h1>نظام إدارة الموظفين</h1>
        </div>
        
        <h2>إشعار راتب</h2>
        
        <div class="employee-info">
            <h3>معلومات الموظف</h3>
            <p><strong>الاسم:</strong> {{ employee_name }}</p>
            <p><strong>الرقم الوظيفي:</strong> {{ employee_id }}</p>
            {% if department_name %}
            <p><strong>القسم:</strong> {{ department_name }}</p>
            {% endif %}
            <p><strong>المسمى الوظيفي:</strong> {{ job_title }}</p>
        </div>
        
        <h3>تفاصيل الراتب لشهر {{ month_name }} {{ year }}</h3>
        
        <table>
            <tr>
                <th>البند</th>
                <th>المبلغ</th>
            </tr>
            <tr>
                <td>الراتب الأساسي</td>
                <td>{{ basic_salary|float|round(2) }}</td>
            </tr>
            <tr>
                <td>البدلات</td>
                <td>{{ allowances|float|round(2) }}</td>
            </tr>
            <tr>
                <td>المكافآت</td>
                <td>{{ bonus|float|round(2) }}</td>
            </tr>
            <tr>
                <td>الخصومات</td>
                <td>{{ deductions|float|round(2) }}</td>
            </tr>
            <tr class="total-row">
                <td>صافي الراتب</td>
                <td>{{ net_salary|float|round(2) }}</td>
            </tr>
        </table>
        
        {% if notes %}
        <div class="notes">
            <h3>ملاحظات</h3>
            <p>{{ notes }}</p>
        </div>
        {% endif %}
        
        <div class="signature">
            <div>
                <p>توقيع المدير المالي</p>
                <div class="line"></div>
            </div>
            <div>
                <p>توقيع الموظف</p>
                <div class="line"></div>
            </div>
        </div>
        
        <div class="footer">
            <p>تم إصدار هذا الإشعار بتاريخ {{ current_date }}</p>
            <p>نظام إدارة الموظفين - جميع الحقوق محفوظة</p>
        </div>
    </body>
    </html>
    """

def get_salary_report_template():
    """
    الحصول على قالب HTML لتقرير الرواتب
    
    Returns:
        نص قالب HTML
    """
    return """
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <title>تقرير الرواتب</title>
        <style>
            @font-face {
                font-family: 'Tajawal';
                src: url('static/fonts/Tajawal-Regular.ttf') format('truetype');
            }
            body {
                font-family: 'Tajawal', sans-serif;
                direction: rtl;
                line-height: 1.6;
            }
        </style>
    </head>
    <body>
        <div class="logo">
            <h1>نظام إدارة الموظفين</h1>
        </div>
        
        <h2>تقرير الرواتب</h2>
        <h3>شهر {{ month_name }} {{ year }}</h3>
        
        <table>
            <tr>
                <th>م</th>
                <th>اسم الموظف</th>
                <th>الرقم الوظيفي</th>
                <th>الراتب الأساسي</th>
                <th>البدلات</th>
                <th>الخصومات</th>
                <th>المكافآت</th>
                <th>صافي الراتب</th>
            </tr>
            {% for salary in salaries %}
            <tr>
                <td>{{ loop.index }}</td>
                <td>{{ salary.employee_name }}</td>
                <td>{{ salary.employee_id }}</td>
                <td>{{ salary.basic_salary|float|round(2) }}</td>
                <td>{{ salary.allowances|float|round(2) }}</td>
                <td>{{ salary.deductions|float|round(2) }}</td>
                <td>{{ salary.bonus|float|round(2) }}</td>
                <td>{{ salary.net_salary|float|round(2) }}</td>
            </tr>
            {% endfor %}
            <tr class="total-row">
                <td colspan="3">المجموع</td>
                <td>{{ total_basic|float|round(2) }}</td>
                <td>{{ total_allowances|float|round(2) }}</td>
                <td>{{ total_deductions|float|round(2) }}</td>
                <td>{{ total_bonus|float|round(2) }}</td>
                <td>{{ total_net|float|round(2) }}</td>
            </tr>
        </table>
        
        <h3>ملخص الرواتب</h3>
        
        <table>
            <tr>
                <th>البيان</th>
                <th>المبلغ</th>
            </tr>
            <tr>
                <td>إجمالي الرواتب الأساسية</td>
                <td>{{ total_basic|float|round(2) }}</td>
            </tr>
            <tr>
                <td>إجمالي البدلات</td>
                <td>{{ total_allowances|float|round(2) }}</td>
            </tr>
            <tr>
                <td>إجمالي الخصومات</td>
                <td>{{ total_deductions|float|round(2) }}</td>
            </tr>
            <tr>
                <td>إجمالي المكافآت</td>
                <td>{{ total_bonus|float|round(2) }}</td>
            </tr>
            <tr class="total-row">
                <td>إجمالي صافي الرواتب</td>
                <td>{{ total_net|float|round(2) }}</td>
            </tr>
        </table>
        
        <div class="footer">
            <p>تم إنشاء هذا التقرير بتاريخ {{ current_date }}</p>
            <p>نظام إدارة الموظفين - جميع الحقوق محفوظة</p>
        </div>
    </body>
    </html>
    """