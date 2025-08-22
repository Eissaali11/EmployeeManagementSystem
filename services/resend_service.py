"""
خدمة إرسال الإيميل باستخدام Resend كبديل لـ SendGrid
"""
import os
import requests
import base64
from flask import current_app
from typing import List, Dict, Any, Optional


def send_email_with_resend(
    to_email: str,
    subject: str,
    html_content: str,
    from_email: str = "noreply@eissa.site",
    from_name: str = "نظام نُظم",
    attachments: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    إرسال إيميل باستخدام Resend API
    
    Args:
        to_email: البريد الإلكتروني للمستقبل
        subject: موضوع الرسالة
        html_content: محتوى HTML للرسالة
        from_email: البريد الإلكتروني للمرسل
        from_name: اسم المرسل
        attachments: قائمة المرفقات
        
    Returns:
        dict: نتيجة الإرسال مع معرف الرسالة أو رسالة الخطأ
    """
    
    # الحصول على مفتاح API
    api_key = os.environ.get('RESEND_API_KEY')
    if not api_key:
        return {
            'success': False,
            'error': 'مفتاح Resend API غير موجود'
        }
    
    # إعداد headers
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # إعداد بيانات الرسالة
    email_data = {
        'from': f'{from_name} <{from_email}>',
        'to': [to_email],
        'subject': subject,
        'html': html_content
    }
    
    # إضافة المرفقات إن وجدت
    if attachments:
        email_data['attachments'] = []
        
        for attachment in attachments:
            if 'content' in attachment and 'filename' in attachment:
                # تحويل المحتوى إلى base64 إذا لم يكن كذلك
                if isinstance(attachment['content'], bytes):
                    content_b64 = base64.b64encode(attachment['content']).decode('utf-8')
                else:
                    content_b64 = attachment['content']
                
                attachment_data = {
                    'filename': attachment['filename'],
                    'content': content_b64
                }
                
                # إضافة نوع الملف إن وجد
                if 'content_type' in attachment:
                    attachment_data['content_type'] = attachment['content_type']
                
                email_data['attachments'].append(attachment_data)
    
    try:
        # إرسال الطلب
        response = requests.post(
            'https://api.resend.com/emails',
            headers=headers,
            json=email_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            current_app.logger.info(f'تم إرسال الإيميل بنجاح - ID: {result.get("id", "unknown")}')
            return {
                'success': True,
                'message_id': result.get('id'),
                'message': 'تم إرسال الإيميل بنجاح'
            }
        else:
            error_detail = response.text
            current_app.logger.error(f'خطأ في إرسال الإيميل عبر Resend: {response.status_code} - {error_detail}')
            return {
                'success': False,
                'error': f'خطأ في الإرسال: {response.status_code}',
                'details': error_detail
            }
            
    except requests.exceptions.Timeout:
        current_app.logger.error('انتهت مهلة الاتصال مع Resend')
        return {
            'success': False,
            'error': 'انتهت مهلة الاتصال مع خدمة الإيميل'
        }
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f'خطأ في الاتصال مع Resend: {e}')
        return {
            'success': False,
            'error': f'خطأ في الاتصال: {str(e)}'
        }
    except Exception as e:
        current_app.logger.error(f'خطأ غير متوقع في إرسال الإيميل: {e}')
        return {
            'success': False,
            'error': f'خطأ غير متوقع: {str(e)}'
        }


def test_resend_connection() -> Dict[str, Any]:
    """
    اختبار الاتصال مع Resend API
    """
    api_key = os.environ.get('RESEND_API_KEY')
    if not api_key:
        return {
            'success': False,
            'error': 'مفتاح Resend API غير موجود'
        }
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        # اختبار بسيط للتحقق من صحة المفتاح
        response = requests.get(
            'https://api.resend.com/domains',
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            return {
                'success': True,
                'message': 'الاتصال مع Resend يعمل بشكل صحيح'
            }
        else:
            return {
                'success': False,
                'error': f'خطأ في الاتصال: {response.status_code}',
                'details': response.text
            }
    except Exception as e:
        return {
            'success': False,
            'error': f'خطأ في الاتصال: {str(e)}'
        }


def create_operation_email_template(
    operation_data: Dict[str, Any],
    vehicle_plate: str,
    driver_name: str
) -> str:
    """
    إنشاء قالب HTML للإيميل الخاص بالعمليات
    """
    
    operation_type_names = {
        'handover': 'تسليم واستلام مركبة',
        'workshop': 'إدخال ورشة',
        'workshop_record': 'سجل ورشة',
        'external_authorization': 'تفويض خارجي',
        'safety_inspection': 'فحص السلامة'
    }
    
    status_names = {
        'pending': 'في انتظار الموافقة',
        'approved': 'مُوافق عليه',
        'rejected': 'مرفوض',
        'under_review': 'قيد المراجعة'
    }
    
    priority_names = {
        'low': 'منخفضة',
        'normal': 'عادية',
        'high': 'عالية',
        'urgent': 'عاجلة'
    }
    
    operation_type = operation_data.get('operation_type', 'غير محدد')
    operation_type_display = operation_type_names.get(operation_type, operation_type)
    
    status = operation_data.get('status', 'غير محدد')
    status_display = status_names.get(status, status)
    
    priority = operation_data.get('priority', 'عادية')
    priority_display = priority_names.get(priority, priority)
    
    html_content = f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>تفاصيل العملية - {operation_data.get('title', 'غير محدد')}</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                background-color: #f8f9fa;
                margin: 0;
                padding: 20px;
                direction: rtl;
            }}
            .email-container {{
                max-width: 600px;
                margin: 0 auto;
                background-color: #ffffff;
                border-radius: 10px;
                box-shadow: 0 0 20px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            .header {{
                background: linear-gradient(135deg, #1e3a5c 0%, #2c5282 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 24px;
                font-weight: bold;
            }}
            .content {{
                padding: 30px;
            }}
            .operation-info {{
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 20px;
                margin: 20px 0;
                border-right: 4px solid #1e3a5c;
            }}
            .info-row {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 8px 0;
                border-bottom: 1px solid #e9ecef;
            }}
            .info-row:last-child {{
                border-bottom: none;
            }}
            .info-label {{
                font-weight: bold;
                color: #1e3a5c;
                min-width: 120px;
            }}
            .info-value {{
                color: #333;
                flex: 1;
                text-align: left;
            }}
            .status-badge {{
                display: inline-block;
                padding: 4px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: bold;
                text-transform: uppercase;
            }}
            .status-pending {{
                background-color: #fff3cd;
                color: #856404;
            }}
            .status-approved {{
                background-color: #d4edda;
                color: #155724;
            }}
            .status-rejected {{
                background-color: #f8d7da;
                color: #721c24;
            }}
            .priority-high {{
                color: #dc3545;
                font-weight: bold;
            }}
            .priority-urgent {{
                color: #dc3545;
                font-weight: bold;
                animation: blink 1s infinite;
            }}
            .vehicle-info {{
                background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                color: white;
                padding: 20px;
                border-radius: 8px;
                margin: 20px 0;
                text-align: center;
            }}
            .attachments {{
                background-color: #e9ecef;
                border-radius: 8px;
                padding: 20px;
                margin: 20px 0;
            }}
            .attachment-list {{
                list-style: none;
                padding: 0;
                margin: 10px 0 0 0;
            }}
            .attachment-item {{
                padding: 8px 0;
                border-bottom: 1px solid #dee2e6;
            }}
            .attachment-item:last-child {{
                border-bottom: none;
            }}
            .footer {{
                background-color: #1e3a5c;
                color: white;
                padding: 20px;
                text-align: center;
                font-size: 14px;
            }}
            .company-logo {{
                font-size: 20px;
                font-weight: bold;
                margin-bottom: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="email-container">
            <div class="header">
                <div class="company-logo">شركة رأس السعودية المحدودة</div>
                <h1>نظام نُظم - إدارة المركبات</h1>
            </div>
            
            <div class="content">
                <h2>تفاصيل العملية</h2>
                
                <div class="operation-info">
                    <div class="info-row">
                        <span class="info-label">عنوان العملية:</span>
                        <span class="info-value">{operation_data.get('title', 'غير محدد')}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">نوع العملية:</span>
                        <span class="info-value">{operation_type_display}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">الحالة:</span>
                        <span class="info-value">
                            <span class="status-badge status-{status}">{status_display}</span>
                        </span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">الأولوية:</span>
                        <span class="info-value priority-{priority}">{priority_display}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">تاريخ الطلب:</span>
                        <span class="info-value">{operation_data.get('requested_at', 'غير محدد')}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">طالب العملية:</span>
                        <span class="info-value">{operation_data.get('requester', 'غير محدد')}</span>
                    </div>
                    <div class="info-row">
                        <span class="info-label">مراجع العملية:</span>
                        <span class="info-value">{operation_data.get('reviewer', 'لم يتم المراجعة بعد')}</span>
                    </div>
                </div>
                
                <div class="vehicle-info">
                    <h3>معلومات المركبة</h3>
                    <p><strong>رقم اللوحة:</strong> {vehicle_plate}</p>
                    <p><strong>السائق الحالي:</strong> {driver_name}</p>
                </div>
                
                {f'<div class="operation-info"><div class="info-row"><span class="info-label">الوصف:</span><span class="info-value">{operation_data.get("description")}</span></div></div>' if operation_data.get('description') else ''}
                
                <div class="attachments">
                    <h3>المرفقات المرسلة</h3>
                    <ul class="attachment-list">
                        <li class="attachment-item">📊 ملف Excel مع تفاصيل العملية الكاملة</li>
                        <li class="attachment-item">📄 ملف PDF للمستندات (حسب نوع العملية)</li>
                    </ul>
                </div>
            </div>
            
            <div class="footer">
                <div class="company-logo">نظام نُظم</div>
                <p>نظام إدارة المركبات والموظفين</p>
                <p>شركة رأس السعودية المحدودة</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_content