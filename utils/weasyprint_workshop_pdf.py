"""
مولد تقارير الورشة باستخدام WeasyPrint
مع دعم كامل للنصوص العربية والاتجاه من اليمين لليسار
"""

import io
import os
from datetime import datetime
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

def generate_workshop_report_pdf(vehicle, workshop_records):
    print("ميزة توليد PDF غير متوفرة مؤقتًا على ويندوز بسبب مشكلة التبعيات.")
    return None

def generate_workshop_report_pdf(vehicle, workshop_records):
    """
    إنشاء تقرير سجلات الورشة باستخدام WeasyPrint
    مع دعم كامل للنصوص العربية
    """
    
    # إنشاء محتوى HTML للتقرير
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>تقرير سجلات الورشة</title>
    </head>
    <body>
        <div class="header">
            <div class="logo">
                <div class="logo-circle">نُظم</div>
            </div>
            <h1>تقرير سجلات الورشة</h1>
            <p class="subtitle">المركبة: {vehicle.plate_number}</p>
            <p class="date">{datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </div>

        <div class="vehicle-info">
            <h2>معلومات المركبة</h2>
            <table class="info-table">
                <tr>
                    <td class="label">رقم اللوحة:</td>
                    <td class="value">{vehicle.plate_number}</td>
                </tr>
                <tr>
                    <td class="label">الماركة:</td>
                    <td class="value">{vehicle.make or 'غير محدد'}</td>
                </tr>
                <tr>
                    <td class="label">الموديل:</td>
                    <td class="value">{vehicle.model or 'غير محدد'}</td>
                </tr>
                <tr>
                    <td class="label">السنة:</td>
                    <td class="value">{vehicle.year or 'غير محدد'}</td>
                </tr>
            </table>
        </div>

        <div class="workshop-records">
            <h2>سجلات الورشة</h2>
            <table class="records-table">
                <thead>
                    <tr>
                        <th>الفني المسؤول</th>
                        <th>اسم الورشة</th>
                        <th>التكلفة (ريال)</th>
                        <th>حالة الإصلاح</th>
                        <th>تاريخ الخروج</th>
                        <th>تاريخ الدخول</th>
                        <th>سبب الدخول</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    # إضافة سجلات الورشة
    total_cost = 0
    total_days = 0
    
    for record in workshop_records:
        # حساب التكلفة
        cost = float(record.cost) if record.cost else 0
        total_cost += cost
        
        # حساب عدد الأيام
        if record.entry_date and record.exit_date:
            days = (record.exit_date - record.entry_date).days
            total_days += max(days, 0)
        
        # تنسيق التواريخ
        entry_date = record.entry_date.strftime('%Y-%m-%d') if record.entry_date else 'غير محدد'
        exit_date = record.exit_date.strftime('%Y-%m-%d') if record.exit_date else 'غير محدد'
        
        html_content += f"""
                    <tr>
                        <td>{getattr(record, 'technician_name', None) or 'غير محدد'}</td>
                        <td>{getattr(record, 'workshop_name', None) or 'غير محدد'}</td>
                        <td>{cost:.2f}</td>
                        <td>{record.repair_status or 'غير محدد'}</td>
                        <td>{exit_date}</td>
                        <td>{entry_date}</td>
                        <td>{record.reason or 'غير محدد'}</td>
                    </tr>
        """
    
    # إضافة الإحصائيات
    html_content += f"""
                </tbody>
            </table>
        </div>

        <div class="statistics">
            <h2>إحصائيات التقرير</h2>
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-label">إجمالي عدد السجلات:</div>
                    <div class="stat-value">{len(workshop_records)}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">إجمالي التكلفة (ريال):</div>
                    <div class="stat-value">{total_cost:.2f}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">إجمالي أيام الورشة:</div>
                    <div class="stat-value">{total_days}</div>
                </div>
            </div>
        </div>

        <div class="footer">
            <p>تم إنشاء هذا التقرير في {datetime.now().strftime('%Y-%m-%d %H:%M')} بواسطة نظام نُظم</p>
            <p>© 2025 جميع الحقوق محفوظة - نظام نُظم</p>
        </div>
    </body>
    </html>
    """
    
    # تعريف CSS للتنسيق
    css_content = """
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&display=swap');
    
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        font-family: 'Amiri', 'Arial', sans-serif;
        direction: rtl;
        text-align: right;
        line-height: 1.6;
        color: #333;
        background: #fff;
    }
    
    .header {
        text-align: center;
        margin-bottom: 30px;
        padding: 20px;
        border-bottom: 2px solid #1e3a8a;
    }
    
    .logo-circle {
        width: 80px;
        height: 80px;
        background: #1e3a8a;
        color: white;
        border-radius: 50%;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 15px;
    }
    
    h1 {
        color: #1e3a8a;
        font-size: 28px;
        margin-bottom: 10px;
        font-weight: 700;
    }
    
    h2 {
        color: #1e3a8a;
        font-size: 20px;
        margin-bottom: 15px;
        font-weight: 700;
        border-bottom: 1px solid #e5e7eb;
        padding-bottom: 5px;
    }
    
    .subtitle {
        font-size: 18px;
        color: #374151;
        margin-bottom: 5px;
    }
    
    .date {
        font-size: 14px;
        color: #6b7280;
    }
    
    .vehicle-info {
        margin-bottom: 30px;
        padding: 20px;
        background: #f9fafb;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
    }
    
    .info-table {
        width: 100%;
        border-collapse: collapse;
    }
    
    .info-table td {
        padding: 10px;
        border-bottom: 1px solid #e5e7eb;
    }
    
    .info-table .label {
        font-weight: bold;
        color: #374151;
        width: 30%;
    }
    
    .info-table .value {
        color: #111827;
    }
    
    .workshop-records {
        margin-bottom: 30px;
    }
    
    .records-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 15px;
        background: white;
        border: 1px solid #d1d5db;
    }
    
    .records-table th,
    .records-table td {
        padding: 12px 8px;
        text-align: center;
        border: 1px solid #d1d5db;
    }
    
    .records-table th {
        background: #1e3a8a;
        color: white;
        font-weight: bold;
        font-size: 14px;
    }
    
    .records-table tbody tr:nth-child(even) {
        background: #f9fafb;
    }
    
    .records-table tbody tr:hover {
        background: #f3f4f6;
    }
    
    .statistics {
        margin-bottom: 30px;
        padding: 20px;
        background: #fef3c7;
        border-radius: 8px;
        border: 1px solid #f59e0b;
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 20px;
        margin-top: 15px;
    }
    
    .stat-item {
        text-align: center;
        padding: 15px;
        background: white;
        border-radius: 6px;
        border: 1px solid #d97706;
    }
    
    .stat-label {
        font-size: 14px;
        color: #92400e;
        margin-bottom: 5px;
    }
    
    .stat-value {
        font-size: 20px;
        font-weight: bold;
        color: #92400e;
    }
    
    .footer {
        text-align: center;
        margin-top: 40px;
        padding: 20px;
        border-top: 1px solid #e5e7eb;
        color: #6b7280;
        font-size: 12px;
    }
    
    @page {
        size: A4;
        margin: 1cm;
    }
    """
    
    # إنشاء ملف PDF
    try:
        font_config = FontConfiguration()
        html_doc = HTML(string=html_content)
        css_doc = CSS(string=css_content, font_config=font_config)
        
        # إنشاء PDF في الذاكرة
        pdf_buffer = io.BytesIO()
        html_doc.write_pdf(pdf_buffer, stylesheets=[css_doc], font_config=font_config)
        pdf_buffer.seek(0)
        
        return pdf_buffer
        
    except Exception as e:
        print(f"خطأ في إنشاء PDF: {str(e)}")
        raise e