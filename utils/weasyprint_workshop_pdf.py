"""
مولد PDF للورشة باستخدام WeasyPrint مع دعم كامل للغة العربية
"""

from weasyprint import HTML, CSS
from datetime import datetime
import tempfile
import os

def generate_workshop_pdf(vehicle, workshop_records):
    """
    إنشاء تقرير ورشة باللغة العربية باستخدام WeasyPrint
    """
    try:
        # إنشاء HTML للتقرير
        html_content = create_workshop_html(vehicle, workshop_records)
        
        # CSS للتنسيق والخطوط العربية
        css_content = """
        @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@400;700&display=swap');
        
        body {
            font-family: 'Noto Sans Arabic', Arial, sans-serif;
            direction: rtl;
            text-align: right;
            line-height: 1.6;
            margin: 20px;
            color: #333;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 3px solid #2c5aa0;
            padding-bottom: 20px;
        }
        
        .logo {
            width: 80px;
            height: 80px;
            margin: 0 auto 15px;
        }
        
        .title {
            font-size: 24px;
            font-weight: bold;
            color: #2c5aa0;
            margin-bottom: 10px;
        }
        
        .vehicle-info {
            font-size: 16px;
            color: #666;
        }
        
        .section {
            margin: 25px 0;
        }
        
        .section-title {
            font-size: 18px;
            font-weight: bold;
            color: #2c5aa0;
            margin-bottom: 15px;
            border-bottom: 2px solid #e0e0e0;
            padding-bottom: 5px;
        }
        
        .info-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
            font-size: 14px;
        }
        
        .info-table th {
            background-color: #f5f5f5;
            font-weight: bold;
            padding: 12px;
            border: 1px solid #ddd;
            text-align: center;
        }
        
        .info-table td {
            padding: 10px;
            border: 1px solid #ddd;
            text-align: center;
        }
        
        .records-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
            font-size: 12px;
        }
        
        .records-table th {
            background-color: #2c5aa0;
            color: white;
            font-weight: bold;
            padding: 10px 8px;
            border: 1px solid #1a4080;
            text-align: center;
        }
        
        .records-table td {
            padding: 8px;
            border: 1px solid #ddd;
            text-align: center;
        }
        
        .records-table tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        
        .stats-table {
            width: 70%;
            margin: 0 auto;
            border-collapse: collapse;
            font-size: 14px;
        }
        
        .stats-table th {
            background-color: #e3f2fd;
            font-weight: bold;
            padding: 12px;
            border: 1px solid #90caf9;
            text-align: center;
        }
        
        .stats-table td {
            padding: 10px;
            border: 1px solid #90caf9;
            text-align: center;
        }
        
        .footer {
            margin-top: 40px;
            text-align: center;
            font-size: 12px;
            color: #666;
            border-top: 1px solid #e0e0e0;
            padding-top: 15px;
        }
        
        .no-records {
            text-align: center;
            font-size: 16px;
            color: #666;
            padding: 30px;
            background-color: #f5f5f5;
            border-radius: 5px;
        }
        
        @page {
            margin: 2cm;
            @top-center {
                content: "تقرير سجلات الورشة - نظام نُظم";
                font-family: 'Noto Sans Arabic', Arial, sans-serif;
                font-size: 10px;
                color: #666;
            }
        }
        """
        
        # إنشاء ملف مؤقت للـ HTML
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as html_file:
            html_file.write(html_content)
            html_file_path = html_file.name
        
        try:
            # إنشاء PDF باستخدام WeasyPrint
            html_doc = HTML(filename=html_file_path)
            css_doc = CSS(string=css_content)
            
            pdf_bytes = html_doc.write_pdf(stylesheets=[css_doc])
            
            return pdf_bytes
            
        finally:
            # حذف الملف المؤقت
            if os.path.exists(html_file_path):
                os.unlink(html_file_path)
                
    except Exception as e:
        print(f"خطأ في إنشاء PDF بـ WeasyPrint: {str(e)}")
        # العودة للمولد الآمن في حالة الفشل
        from utils.safe_workshop_pdf import generate_workshop_pdf as safe_generate
        return safe_generate(vehicle, workshop_records)

def create_workshop_html(vehicle, workshop_records):
    """إنشاء محتوى HTML للتقرير"""
    
    # حساب الإحصائيات
    total_cost = 0
    total_days = 0
    
    if workshop_records:
        for record in workshop_records:
            cost = float(record.cost) if record.cost else 0
            total_cost += cost
            
            if record.entry_date:
                if record.exit_date:
                    days = (record.exit_date - record.entry_date).days
                else:
                    days = (datetime.now().date() - record.entry_date).days
                total_days += max(0, days)
    
    # إنشاء HTML
    html = f"""
    <!DOCTYPE html>
    <html lang="ar">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>تقرير سجلات الورشة - {vehicle.plate_number}</title>
    </head>
    <body>
        <div class="header">
            <div class="title">تقرير سجلات الورشة للمركبة: {vehicle.plate_number}</div>
            <div class="vehicle-info">{vehicle.make} {vehicle.model} - {vehicle.year}</div>
            <div class="vehicle-info">اللون: {vehicle.color} | الحالة: {get_status_arabic(vehicle.status)}</div>
        </div>
        
        <div class="section">
            <div class="section-title">معلومات المركبة</div>
            <table class="info-table">
                <tr>
                    <th>رقم اللوحة</th>
                    <td>{vehicle.plate_number}</td>
                </tr>
                <tr>
                    <th>الصنع والموديل</th>
                    <td>{vehicle.make} {vehicle.model}</td>
                </tr>
                <tr>
                    <th>سنة الصنع</th>
                    <td>{vehicle.year}</td>
                </tr>
                <tr>
                    <th>اللون</th>
                    <td>{vehicle.color}</td>
                </tr>
                <tr>
                    <th>الحالة الحالية</th>
                    <td>{get_status_arabic(vehicle.status)}</td>
                </tr>
            </table>
        </div>
    """
    
    if workshop_records and len(workshop_records) > 0:
        html += f"""
        <div class="section">
            <div class="section-title">سجلات الورشة ({len(workshop_records)} سجل)</div>
            <table class="records-table">
                <thead>
                    <tr>
                        <th>تاريخ الدخول</th>
                        <th>تاريخ الخروج</th>
                        <th>سبب الدخول</th>
                        <th>حالة الإصلاح</th>
                        <th>التكلفة (ريال)</th>
                        <th>اسم الورشة</th>
                        <th>الفني المسؤول</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for record in workshop_records:
            entry_date = record.entry_date.strftime('%Y-%m-%d') if record.entry_date else "غير محدد"
            exit_date = record.exit_date.strftime('%Y-%m-%d') if record.exit_date else "ما زالت في الورشة"
            reason = get_reason_arabic(record.reason)
            status = get_repair_status_arabic(record.repair_status)
            cost = float(record.cost) if record.cost else 0
            workshop_name = record.workshop_name if record.workshop_name else "غير محدد"
            technician = record.technician_name if record.technician_name else "غير محدد"
            
            html += f"""
                    <tr>
                        <td>{entry_date}</td>
                        <td>{exit_date}</td>
                        <td>{reason}</td>
                        <td>{status}</td>
                        <td>{cost:,.2f}</td>
                        <td>{workshop_name}</td>
                        <td>{technician}</td>
                    </tr>
            """
        
        html += """
                </tbody>
            </table>
        </div>
        """
        
        # الإحصائيات
        avg_cost = total_cost / len(workshop_records) if len(workshop_records) > 0 else 0
        avg_days = total_days / len(workshop_records) if len(workshop_records) > 0 else 0
        
        html += f"""
        <div class="section">
            <div class="section-title">ملخص الإحصائيات</div>
            <table class="stats-table">
                <tr>
                    <th>عدد السجلات</th>
                    <td>{len(workshop_records)}</td>
                </tr>
                <tr>
                    <th>إجمالي التكلفة</th>
                    <td>{total_cost:,.2f} ريال</td>
                </tr>
                <tr>
                    <th>إجمالي أيام الإصلاح</th>
                    <td>{total_days} يوم</td>
                </tr>
                <tr>
                    <th>متوسط التكلفة لكل سجل</th>
                    <td>{avg_cost:,.2f} ريال</td>
                </tr>
                <tr>
                    <th>متوسط مدة الإصلاح</th>
                    <td>{avg_days:.1f} يوم</td>
                </tr>
            </table>
        </div>
        """
    else:
        html += """
        <div class="section">
            <div class="no-records">لا توجد سجلات ورشة متاحة لهذه المركبة</div>
        </div>
        """
    
    html += f"""
        <div class="footer">
            تم إنشاء هذا التقرير بواسطة نظام نُظم لإدارة المركبات<br>
            التاريخ والوقت: {datetime.now().strftime('%Y-%m-%d %H:%M')}
        </div>
    </body>
    </html>
    """
    
    return html

def get_status_arabic(status):
    """ترجمة حالة المركبة للعربية"""
    status_map = {
        'available': 'متاح',
        'rented': 'مؤجر',
        'in_workshop': 'في الورشة',
        'accident': 'حادث'
    }
    return status_map.get(status, status)

def get_reason_arabic(reason):
    """ترجمة سبب دخول الورشة للعربية"""
    reason_map = {
        'maintenance': 'صيانة دورية',
        'breakdown': 'عطل',
        'accident': 'حادث'
    }
    return reason_map.get(reason, reason if reason else "غير محدد")

def get_repair_status_arabic(status):
    """ترجمة حالة الإصلاح للعربية"""
    status_map = {
        'in_progress': 'قيد التنفيذ',
        'completed': 'تم الإصلاح',
        'pending_approval': 'بانتظار الموافقة'
    }
    return status_map.get(status, status if status else "غير محدد")