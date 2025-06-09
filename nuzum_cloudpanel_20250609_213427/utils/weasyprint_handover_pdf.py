"""
مولد تقارير تسليم/استلام المركبات باستخدام WeasyPrint
مع دعم كامل للنصوص العربية والاتجاه من اليمين لليسار
"""

import io
import os
from datetime import datetime
from io import BytesIO
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

def generate_handover_report_pdf(vehicle, handover_record):
    """
    إنشاء تقرير تسليم/استلام المركبة باستخدام WeasyPrint
    مع دعم كامل للنصوص العربية
    """
    
    # تحديد نوع العملية
    operation_type = "تسليم" if handover_record.handover_type == "delivery" else "استلام"
    
    # إنشاء محتوى HTML للتقرير
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>وثيقة تسليم واستلام المركبة</title>
    </head>
    <body>
        <div class="header">
            <div class="logo">
                <div class="logo-circle">نُظم</div>
            </div>
            <h1>وثيقة تسليم واستلام المركبة</h1>
            <p class="subtitle">المركبة: {vehicle.plate_number}</p>
            <p class="date">{datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </div>

        <div class="document-info">
            <div class="info-row">
                <span class="label">رقم الوثيقة:</span>
                <span class="value">#{handover_record.id}</span>
            </div>
            <div class="info-row">
                <span class="label">نوع العملية:</span>
                <span class="value operation-{handover_record.handover_type}">{operation_type}</span>
            </div>
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
                <tr>
                    <td class="label">اللون:</td>
                    <td class="value">{vehicle.color or 'غير محدد'}</td>
                </tr>
            </table>
        </div>

        <div class="handover-details">
            <h2>تفاصيل العملية</h2>
            <table class="details-table">
                <tr>
                    <td class="label">التاريخ:</td>
                    <td class="value">{handover_record.handover_date.strftime('%Y-%m-%d') if handover_record.handover_date else 'غير محدد'}</td>
                </tr>
                <tr>
                    <td class="label">الوقت:</td>
                    <td class="value">{getattr(handover_record, 'handover_time', None) and handover_record.handover_time.strftime('%H:%M') or 'غير محدد'}</td>
                </tr>
                <tr>
                    <td class="label">اسم الشخص:</td>
                    <td class="value">{getattr(handover_record, 'person_name', None) or 'غير محدد'}</td>
                </tr>
                <tr>
                    <td class="label">رقم الهاتف:</td>
                    <td class="value">{getattr(handover_record, 'phone_number', None) or 'غير محدد'}</td>
                </tr>
                <tr>
                    <td class="label">قراءة العداد:</td>
                    <td class="value">{getattr(handover_record, 'mileage', None) or 'غير محدد'} كم</td>
                </tr>
                <tr>
                    <td class="label">مستوى الوقود:</td>
                    <td class="value">{getattr(handover_record, 'fuel_level', None) or 'غير محدد'}%</td>
                </tr>
            </table>
        </div>

        <div class="equipment-section">
            <h2>معدات المركبة</h2>
            <div class="equipment-grid">
    """
    
    # إضافة معدات المركبة
    equipment_items = [
        ('has_spare_tire', 'الإطار الاحتياطي'),
        ('has_fire_extinguisher', 'طفاية الحريق'),
        ('has_first_aid_kit', 'حقيبة الإسعافات الأولية'),
        ('has_warning_triangle', 'مثلث التحذير'),
        ('has_tools', 'عدة الأدوات')
    ]
    
    for field, label in equipment_items:
        status = getattr(handover_record, field, None)
        status_class = "available" if status == 1 else "unavailable"
        status_text = "متوفر" if status == 1 else "غير متوفر"
        
        html_content += f"""
                <div class="equipment-item {status_class}">
                    <div class="equipment-label">{label}</div>
                    <div class="equipment-status">{status_text}</div>
                </div>
        """
    
    # إضافة الملاحظات والتوقيعات
    html_content += f"""
            </div>
        </div>

        <div class="notes-section">
            <h2>ملاحظات إضافية</h2>
            <div class="notes-content">
                {getattr(handover_record, 'notes', None) or 'لا توجد ملاحظات إضافية'}
            </div>
        </div>

        <div class="signatures">
            <div class="signature-section">
                <h3>المُسلِّم</h3>
                <div class="signature-line"></div>
                <p>الاسم: ___________________</p>
                <p>التوقيع: _________________</p>
                <p>التاريخ: _________________</p>
            </div>
            <div class="signature-section">
                <h3>المُستلِم</h3>
                <div class="signature-line"></div>
                <p>الاسم: ___________________</p>
                <p>التوقيع: _________________</p>
                <p>التاريخ: _________________</p>
            </div>
        </div>

        <div class="footer">
            <p>نُظم - نظام إدارة المركبات المتقدم</p>
            <p>تم إنشاء هذه الوثيقة تلقائياً في {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <div class="electronic-form-link">
                <p><strong>رابط النموذج الإلكتروني:</strong></p>
                <p class="link-description">{('تسليم' if handover_record.handover_type == 'delivery' else 'استلام')} السيارة {handover_record.vehicle.plate_number if handover_record.vehicle else 'غير محدد'} {'من' if handover_record.handover_type == 'delivery' else 'إلى'} {getattr(handover_record, 'person_name', 'غير محدد')}</p>
                <p class="link-text">{getattr(handover_record, 'form_link', f'https://d72f2aef-918c-4148-9723-15870f8c7cf6-00-2c1ygyxvqoldk.riker.replit.dev/vehicles/handover/{handover_record.id}/view/public')}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # CSS للتصميم العربي المحسن
    css_content = """
    @import url('https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&family=Cairo:wght@400;600;700&display=swap');
    
    * {
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }
    
    body {
        font-family: 'Cairo', 'Amiri', Arial, sans-serif;
        direction: rtl;
        text-align: right;
        line-height: 1.6;
        color: #2c3e50;
        background-color: #ffffff;
        font-size: 14px;
    }
    
    .header {
        text-align: center;
        margin-bottom: 30px;
        border-bottom: 3px solid #3498db;
        padding-bottom: 20px;
    }
    
    .logo {
        margin-bottom: 15px;
    }
    
    .logo-circle {
        display: inline-block;
        width: 80px;
        height: 80px;
        background: linear-gradient(135deg, #3498db, #2980b9);
        color: white;
        border-radius: 50%;
        line-height: 80px;
        text-align: center;
        font-size: 24px;
        font-weight: bold;
        box-shadow: 0 4px 15px rgba(52, 152, 219, 0.3);
    }
    
    h1 {
        color: #2c3e50;
        font-size: 26px;
        font-weight: bold;
        margin: 15px 0;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    
    .subtitle {
        font-size: 18px;
        color: #34495e;
        font-weight: 600;
        margin: 5px 0;
    }
    
    .date {
        font-size: 14px;
        color: #7f8c8d;
        margin: 5px 0;
    }
    
    .document-info {
        background: linear-gradient(135deg, #ecf0f1, #bdc3c7);
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 25px;
        border: 1px solid #bdc3c7;
    }
    
    .info-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin: 8px 0;
        padding: 5px 0;
    }
    
    .label {
        font-weight: bold;
        color: #2c3e50;
        min-width: 120px;
    }
    
    .value {
        color: #34495e;
        font-weight: 500;
    }
    
    .operation-delivery {
        background-color: #27ae60;
        color: white;
        padding: 4px 12px;
        border-radius: 15px;
        font-size: 12px;
    }
    
    .operation-return {
        background-color: #e74c3c;
        color: white;
        padding: 4px 12px;
        border-radius: 15px;
        font-size: 12px;
    }
    
    .vehicle-info, .handover-details, .equipment-section, .notes-section {
        margin-bottom: 25px;
        background: white;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border: 1px solid #ecf0f1;
    }
    
    h2 {
        color: #2c3e50;
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 15px;
        border-bottom: 2px solid #3498db;
        padding-bottom: 8px;
    }
    
    .info-table, .details-table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 10px;
    }
    
    .info-table td, .details-table td {
        padding: 12px;
        border: 1px solid #ecf0f1;
        vertical-align: middle;
    }
    
    .info-table .label, .details-table .label {
        background-color: #f8f9fa;
        font-weight: bold;
        width: 30%;
        color: #2c3e50;
    }
    
    .info-table .value, .details-table .value {
        background-color: white;
        color: #34495e;
    }
    
    .equipment-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 15px;
        margin-top: 15px;
    }
    
    .equipment-item {
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        border: 2px solid;
        transition: all 0.3s ease;
    }
    
    .equipment-item.available {
        background-color: #d5f4e6;
        border-color: #27ae60;
        color: #27ae60;
    }
    
    .equipment-item.unavailable {
        background-color: #fadbd8;
        border-color: #e74c3c;
        color: #e74c3c;
    }
    
    .equipment-label {
        font-weight: bold;
        margin-bottom: 8px;
        font-size: 14px;
    }
    
    .equipment-status {
        font-size: 12px;
        font-weight: 500;
    }
    
    .notes-section h2 {
        color: #8e44ad;
        border-color: #8e44ad;
    }
    
    .notes-content {
        background-color: #fdf2e9;
        padding: 15px;
        border-radius: 6px;
        border-left: 4px solid #f39c12;
        color: #2c3e50;
        line-height: 1.8;
        min-height: 60px;
    }
    
    .signatures {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 30px;
        margin: 30px 0;
        page-break-inside: avoid;
    }
    
    .signature-section {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        text-align: center;
    }
    
    .signature-section h3 {
        color: #2c3e50;
        font-size: 16px;
        margin-bottom: 15px;
        border-bottom: 1px solid #dee2e6;
        padding-bottom: 8px;
    }
    
    .signature-line {
        height: 60px;
        border-bottom: 2px solid #adb5bd;
        margin: 15px 0;
    }
    
    .signature-section p {
        margin: 8px 0;
        color: #6c757d;
        font-size: 12px;
    }
    
    .footer {
        text-align: center;
        margin-top: 30px;
        padding: 20px;
        background-color: #2c3e50;
        color: white;
        border-radius: 8px;
        font-size: 12px;
    }
    
    .footer p {
        margin: 5px 0;
    }
    
    .electronic-form-link {
        background-color: #34495e;
        border-radius: 6px;
        padding: 15px;
        margin-top: 15px;
        border: 1px solid #4a5f7a;
    }
    
    .electronic-form-link p {
        margin: 8px 0;
        font-size: 11px;
    }
    
    .link-description {
        background-color: #27ae60;
        color: white;
        padding: 8px 12px;
        border-radius: 4px;
        font-weight: bold;
        text-align: center;
        margin: 8px 0;
        font-size: 12px;
    }
    
    .link-text {
        background-color: #ecf0f1;
        color: #2c3e50;
        padding: 8px 12px;
        border-radius: 4px;
        font-family: 'Courier New', monospace;
        word-break: break-all;
        font-size: 10px;
        margin-top: 8px;
    }
    
    @page {
        margin: 2cm;
        @bottom-center {
            content: "صفحة " counter(page) " من " counter(pages);
            font-family: 'Cairo', Arial, sans-serif;
            font-size: 10px;
            color: #7f8c8d;
        }
    }
    
    @media print {
        body {
            print-color-adjust: exact;
        }
        
        .signatures {
            page-break-inside: avoid;
        }
    }
    """
    
    # إنشاء ملف PDF
    try:
        pdf_buffer = BytesIO()
        HTML(string=html_content).write_pdf(
            pdf_buffer,
            stylesheets=[CSS(string=css_content)],
            font_config=FontConfiguration()
        )
        pdf_buffer.seek(0)
        return pdf_buffer
    
    except Exception as e:
        import logging
        logging.error(f"خطأ في إنشاء تقرير تسليم/استلام المركبة: {str(e)}")
        raise