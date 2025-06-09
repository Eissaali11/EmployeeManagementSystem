"""
مولد تقارير HTML بسيط للورشة - حل فوري للمشكلة
يعرض التقرير كصفحة HTML قابلة للطباعة كـ PDF
"""

from datetime import datetime

def generate_workshop_pdf(vehicle, workshop_records):
    """إنشاء تقرير HTML للورشة"""
    
    try:
        print("إنشاء تقرير HTML بسيط...")
        
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
                @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@400;700&display=swap');
                
                body {{
                    font-family: 'Noto Sans Arabic', Arial, sans-serif;
                    direction: rtl;
                    text-align: right;
                    margin: 40px;
                    line-height: 1.6;
                    color: #333;
                }}
                
                .header {{
                    text-align: center;
                    margin-bottom: 40px;
                    border-bottom: 3px solid #2c5aa0;
                    padding-bottom: 20px;
                }}
                
                .title {{
                    font-size: 28px;
                    font-weight: bold;
                    color: #2c5aa0;
                    margin-bottom: 10px;
                }}
                
                .subtitle {{
                    font-size: 18px;
                    color: #666;
                    margin-bottom: 5px;
                }}
                
                .section {{
                    margin: 30px 0;
                    page-break-inside: avoid;
                }}
                
                .section-title {{
                    font-size: 20px;
                    font-weight: bold;
                    color: #2c5aa0;
                    margin-bottom: 15px;
                    border-bottom: 2px solid #e0e0e0;
                    padding-bottom: 8px;
                }}
                
                .info-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 30px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                
                .info-table th {{
                    background-color: #f8f9fa;
                    font-weight: bold;
                    padding: 15px;
                    border: 1px solid #ddd;
                    text-align: center;
                    font-size: 16px;
                }}
                
                .info-table td {{
                    padding: 12px 15px;
                    border: 1px solid #ddd;
                    text-align: center;
                    font-size: 15px;
                }}
                
                .records-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 30px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                
                .records-table th {{
                    background-color: #2c5aa0;
                    color: white;
                    font-weight: bold;
                    padding: 12px 8px;
                    border: 1px solid #1a4080;
                    text-align: center;
                    font-size: 14px;
                }}
                
                .records-table td {{
                    padding: 10px 8px;
                    border: 1px solid #ddd;
                    text-align: center;
                    font-size: 13px;
                }}
                
                .records-table tr:nth-child(even) {{
                    background-color: #f9f9f9;
                }}
                
                .records-table tr:hover {{
                    background-color: #e3f2fd;
                }}
                
                .stats-table {{
                    width: 80%;
                    margin: 0 auto;
                    border-collapse: collapse;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                
                .stats-table th {{
                    background-color: #e3f2fd;
                    font-weight: bold;
                    padding: 15px;
                    border: 1px solid #90caf9;
                    text-align: center;
                    font-size: 16px;
                }}
                
                .stats-table td {{
                    padding: 12px 15px;
                    border: 1px solid #90caf9;
                    text-align: center;
                    font-size: 15px;
                    font-weight: 500;
                }}
                
                .footer {{
                    margin-top: 50px;
                    text-align: center;
                    font-size: 14px;
                    color: #666;
                    border-top: 1px solid #e0e0e0;
                    padding-top: 20px;
                }}
                
                .no-records {{
                    text-align: center;
                    font-size: 18px;
                    color: #666;
                    padding: 50px;
                    background-color: #f5f5f5;
                    border-radius: 8px;
                    border: 2px dashed #ddd;
                }}
                
                @media print {{
                    body {{ margin: 20px; }}
                    .section {{ page-break-inside: avoid; }}
                    @page {{ margin: 2cm; }}
                }}
            </style>
        </head>
        <body>
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
        </body>
        </html>
        """
        
        print("تم إنشاء تقرير HTML بنجاح!")
        return html_content.encode('utf-8')
        
    except Exception as e:
        print(f"خطأ في إنشاء تقرير HTML: {str(e)}")
        return "<html><body><h1>خطأ في إنشاء التقرير</h1></body></html>".encode('utf-8')

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