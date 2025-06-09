"""
مولد PDF بالعربية باستخدام WeasyPrint - حل نهائي للنصوص العربية
"""

from weasyprint import HTML, CSS
from datetime import datetime
import tempfile
import os

def generate_workshop_pdf(vehicle, workshop_records):
    """إنشاء PDF للورشة بالعربية باستخدام WeasyPrint"""
    
    try:
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
        html_content = f"""
        <!DOCTYPE html>
        <html dir="rtl" lang="ar">
        <head>
            <meta charset="UTF-8">
            <title>تقرير سجلات الورشة - {vehicle.plate_number}</title>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
                
                * {{
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                }}
                
                body {{
                    font-family: 'Cairo', 'Arial Unicode MS', Arial, sans-serif;
                    direction: rtl;
                    text-align: right;
                    line-height: 1.8;
                    color: #2c3e50;
                    background: white;
                }}
                
                .page {{
                    width: 210mm;
                    min-height: 297mm;
                    padding: 20mm;
                    margin: 0 auto;
                    background: white;
                }}
                
                .header {{
                    text-align: center;
                    margin-bottom: 30px;
                    border-bottom: 4px solid #3498db;
                    padding-bottom: 20px;
                }}
                
                .title {{
                    font-size: 24px;
                    font-weight: 700;
                    color: #2c3e50;
                    margin-bottom: 10px;
                }}
                
                .subtitle {{
                    font-size: 16px;
                    color: #7f8c8d;
                    margin-bottom: 8px;
                }}
                
                .section {{
                    margin: 25px 0;
                    page-break-inside: avoid;
                }}
                
                .section-title {{
                    font-size: 18px;
                    font-weight: 700;
                    color: #2c3e50;
                    margin-bottom: 15px;
                    padding: 8px 15px;
                    background: #ecf0f1;
                    border-right: 4px solid #3498db;
                }}
                
                .info-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 25px;
                    border: 1px solid #bdc3c7;
                }}
                
                .info-table th {{
                    background: #34495e;
                    color: white;
                    font-weight: 700;
                    padding: 12px;
                    text-align: center;
                    border: 1px solid #2c3e50;
                }}
                
                .info-table td {{
                    padding: 10px 12px;
                    border: 1px solid #bdc3c7;
                    text-align: center;
                    background: #ffffff;
                }}
                
                .records-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 25px;
                    font-size: 12px;
                    border: 1px solid #bdc3c7;
                }}
                
                .records-table th {{
                    background: #3498db;
                    color: white;
                    font-weight: 700;
                    padding: 8px 6px;
                    text-align: center;
                    border: 1px solid #2980b9;
                }}
                
                .records-table td {{
                    padding: 8px 6px;
                    text-align: center;
                    border: 1px solid #bdc3c7;
                    background: #ffffff;
                }}
                
                .records-table tr:nth-child(even) td {{
                    background: #f8f9fa;
                }}
                
                .stats-table {{
                    width: 70%;
                    margin: 0 auto;
                    border-collapse: collapse;
                    border: 1px solid #bdc3c7;
                }}
                
                .stats-table th {{
                    background: #e8f4fd;
                    color: #2c3e50;
                    font-weight: 700;
                    padding: 12px;
                    text-align: center;
                    border: 1px solid #3498db;
                }}
                
                .stats-table td {{
                    padding: 10px 12px;
                    text-align: center;
                    border: 1px solid #bdc3c7;
                    background: #ffffff;
                    font-weight: 600;
                }}
                
                .footer {{
                    margin-top: 40px;
                    text-align: center;
                    font-size: 12px;
                    color: #7f8c8d;
                    border-top: 1px solid #bdc3c7;
                    padding-top: 15px;
                }}
                
                .no-records {{
                    text-align: center;
                    font-size: 16px;
                    color: #7f8c8d;
                    padding: 40px;
                    background: #f8f9fa;
                    border: 2px dashed #bdc3c7;
                    border-radius: 8px;
                }}
                
                @page {{
                    size: A4;
                    margin: 2cm;
                }}
            </style>
        </head>
        <body>
            <div class="page">
                <div class="header">
                    <div class="title">تقرير سجلات الورشة للمركبة: {vehicle.plate_number}</div>
                    <div class="subtitle">{vehicle.make} {vehicle.model} - سنة {vehicle.year}</div>
                    <div class="subtitle">اللون: {vehicle.color} | الحالة: {get_status_arabic(vehicle.status)}</div>
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
            html_content += f"""
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
                
                html_content += f"""
                            <tr>
                                <td>{entry_date}</td>
                                <td>{exit_date}</td>
                                <td>{reason}</td>
                                <td>{status}</td>
                                <td>{cost:,.0f}</td>
                                <td>{workshop_name}</td>
                                <td>{technician}</td>
                            </tr>
                """
            
            html_content += """
                        </tbody>
                    </table>
                </div>
            """
            
            # الإحصائيات
            avg_cost = total_cost / len(workshop_records) if len(workshop_records) > 0 else 0
            avg_days = total_days / len(workshop_records) if len(workshop_records) > 0 else 0
            
            html_content += f"""
                <div class="section">
                    <div class="section-title">ملخص الإحصائيات</div>
                    <table class="stats-table">
                        <tr>
                            <th>عدد السجلات</th>
                            <td>{len(workshop_records)}</td>
                        </tr>
                        <tr>
                            <th>إجمالي التكلفة</th>
                            <td>{total_cost:,.0f} ريال</td>
                        </tr>
                        <tr>
                            <th>إجمالي أيام الإصلاح</th>
                            <td>{total_days} يوم</td>
                        </tr>
                        <tr>
                            <th>متوسط التكلفة لكل سجل</th>
                            <td>{avg_cost:,.0f} ريال</td>
                        </tr>
                        <tr>
                            <th>متوسط مدة الإصلاح</th>
                            <td>{avg_days:.1f} يوم</td>
                        </tr>
                    </table>
                </div>
            """
        else:
            html_content += """
                <div class="section">
                    <div class="no-records">لا توجد سجلات ورشة متاحة لهذه المركبة</div>
                </div>
            """
        
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
        html_content += f"""
                <div class="footer">
                    تم إنشاء هذا التقرير بواسطة نظام نُظم لإدارة المركبات<br>
                    التاريخ والوقت: {current_time}
                </div>
            </div>
        </body>
        </html>
        """
        
        # إنشاء PDF باستخدام WeasyPrint
        html_doc = HTML(string=html_content, base_url='.')
        pdf_bytes = html_doc.write_pdf()
        
        print("تم إنشاء PDF بالعربية باستخدام WeasyPrint بنجاح!")
        return pdf_bytes
        
    except Exception as e:
        print(f"خطأ في إنشاء PDF بـ WeasyPrint: {str(e)}")
        # العودة لمولد HTML كبديل
        from utils.simple_html_pdf import generate_workshop_pdf as html_fallback
        return html_fallback(vehicle, workshop_records)

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