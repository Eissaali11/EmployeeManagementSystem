"""
وحدة إنشاء ملفات PDF من HTML مع دعم كامل للنصوص العربية
"""
from io import BytesIO
from datetime import datetime
from weasyprint import HTML, CSS
from jinja2 import Template
import os
import base64

def generate_html_pdf(template_str, data, filename=None, landscape=False):
    """
    إنشاء ملف PDF من قالب HTML مع دعم كامل للعربية
    
    Args:
        template_str: قالب HTML كنص
        data: البيانات التي سيتم دمجها مع القالب
        filename: اسم الملف (اختياري، إذا كان None سيتم إرجاع البيانات فقط)
        landscape: هل التقرير بالوضع الأفقي (اختياري)
        
    Returns:
        BytesIO أو None
    """
    try:
        # دمج البيانات مع القالب
        template = Template(template_str)
        html_content = template.render(**data)
        
        # إنشاء ملف PDF
        css_str = """
            @page {
                size: """ + ("landscape A4" if landscape else "A4") + """;
                margin: 2cm;
                @top-center {
                    content: "نظام إدارة الموظفين";
                    font-family: 'Tajawal', sans-serif;
                    font-size: 10px;
                    color: #666;
                }
                @bottom-center {
                    content: "الصفحة " counter(page) " من " counter(pages);
                    font-family: 'Tajawal', sans-serif;
                    font-size: 10px;
                    color: #666;
                }
            }
            body {
                font-family: 'Tajawal', sans-serif;
                direction: rtl;
                text-align: right;
            }
            h1, h2, h3 {
                color: #333;
                text-align: center;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }
            table, th, td {
                border: 1px solid #ddd;
            }
            th {
                background-color: #f2f2f2;
                font-weight: bold;
                padding: 10px;
            }
            td {
                padding: 8px;
            }
            tr:nth-child(even) {
                background-color: #f9f9f9;
            }
            .logo {
                text-align: center;
                margin-bottom: 20px;
            }
            .footer {
                margin-top: 30px;
                text-align: center;
                font-size: 12px;
                color: #666;
            }
            .signature {
                margin-top: 50px;
                display: flex;
                justify-content: space-between;
            }
            .signature div {
                flex: 1;
                text-align: center;
            }
            .signature .line {
                width: 80%;
                margin: 10px auto;
                border-bottom: 1px solid #000;
            }
            .employee-info {
                margin: 20px 0;
                padding: 10px;
                border: 1px solid #ddd;
                background-color: #f9f9f9;
            }
            .employee-info p {
                margin: 5px 0;
            }
            .salary-details {
                font-weight: bold;
            }
            .total-row {
                font-weight: bold;
                background-color: #f2f2f2;
            }
            @font-face {
                font-family: 'Tajawal';
                src: url('static/fonts/Tajawal-Regular.ttf') format('truetype');
                font-weight: normal;
                font-style: normal;
            }
            @font-face {
                font-family: 'ArefRuqaa';
                src: url('static/fonts/ArefRuqaa-Regular.ttf') format('truetype');
                font-weight: normal;
                font-style: normal;
            }
        """
        
        # تحويل HTML إلى PDF
        buffer = BytesIO()
        html = HTML(string=html_content)
        css = CSS(string=css_str)
        html.write_pdf(buffer, stylesheets=[css])
        
        # إذا كان هناك اسم ملف، يتم حفظ البيانات في الملف
        if filename:
            with open(filename, 'wb') as f:
                f.write(buffer.getvalue())
            return None
        
        # إعادة توجيه المؤشر إلى بداية البيانات
        buffer.seek(0)
        return buffer
    except Exception as e:
        print(f"Error creating PDF: {str(e)}")
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