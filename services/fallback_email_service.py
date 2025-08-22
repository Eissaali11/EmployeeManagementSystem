"""
خدمة إيميل احتياطية تعمل بدون خدمات خارجية
تحفظ الإيميلات في ملفات محلية ويمكن إرسالها لاحقاً
"""
import os
import json
import base64
from datetime import datetime
from typing import Dict, Any, List, Optional
from flask import current_app


class FallbackEmailService:
    """خدمة إيميل احتياطية تحفظ الإيميلات محلياً"""
    
    def __init__(self):
        self.emails_dir = "emails_queue"
        self._ensure_email_directory()
    
    def _ensure_email_directory(self):
        """إنشاء مجلد الإيميلات إن لم يكن موجوداً"""
        if not os.path.exists(self.emails_dir):
            os.makedirs(self.emails_dir)
    
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        from_email: str = "noreply@eissa.site",
        from_name: str = "نظام نُظم",
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        حفظ الإيميل في مجلد محلي للإرسال لاحقاً
        """
        try:
            # إنشاء معرف فريد للإيميل
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
            email_id = f"email_{timestamp}"
            
            # إعداد بيانات الإيميل
            email_data = {
                'id': email_id,
                'to_email': to_email,
                'from_email': from_email,
                'from_name': from_name,
                'subject': subject,
                'html_content': html_content,
                'created_at': datetime.now().isoformat(),
                'status': 'queued',
                'attachments': []
            }
            
            # معالجة المرفقات
            if attachments:
                for i, attachment in enumerate(attachments):
                    if 'content' in attachment and 'filename' in attachment:
                        # حفظ المرفق في ملف منفصل
                        attachment_filename = f"{email_id}_attachment_{i}_{attachment['filename']}"
                        attachment_path = os.path.join(self.emails_dir, attachment_filename)
                        
                        # كتابة محتوى المرفق
                        if isinstance(attachment['content'], bytes):
                            with open(attachment_path, 'wb') as f:
                                f.write(attachment['content'])
                        else:
                            # إذا كان base64
                            try:
                                content_bytes = base64.b64decode(attachment['content'])
                                with open(attachment_path, 'wb') as f:
                                    f.write(content_bytes)
                            except Exception:
                                # إذا فشل، احفظه كنص
                                with open(attachment_path, 'w', encoding='utf-8') as f:
                                    f.write(str(attachment['content']))
                        
                        email_data['attachments'].append({
                            'filename': attachment['filename'],
                            'content_type': attachment.get('content_type', 'application/octet-stream'),
                            'file_path': attachment_path,
                            'size': os.path.getsize(attachment_path) if os.path.exists(attachment_path) else 0
                        })
            
            # حفظ بيانات الإيميل
            email_file_path = os.path.join(self.emails_dir, f"{email_id}.json")
            with open(email_file_path, 'w', encoding='utf-8') as f:
                json.dump(email_data, f, ensure_ascii=False, indent=2)
            
            # إنشاء ملف HTML للعرض
            html_file_path = os.path.join(self.emails_dir, f"{email_id}.html")
            with open(html_file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            current_app.logger.info(f'تم حفظ الإيميل محلياً - ID: {email_id}')
            
            return {
                'success': True,
                'message_id': email_id,
                'message': f'تم حفظ الإيميل محلياً وسيتم إرساله لاحقاً إلى {to_email}',
                'saved_path': email_file_path
            }
            
        except Exception as e:
            current_app.logger.error(f'خطأ في حفظ الإيميل: {e}')
            return {
                'success': False,
                'error': f'خطأ في حفظ الإيميل: {str(e)}'
            }
    
    def get_queued_emails(self) -> List[Dict[str, Any]]:
        """جلب قائمة الإيميلات المحفوظة"""
        emails = []
        
        if not os.path.exists(self.emails_dir):
            return emails
        
        for filename in os.listdir(self.emails_dir):
            if filename.endswith('.json'):
                try:
                    file_path = os.path.join(self.emails_dir, filename)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        email_data = json.load(f)
                        emails.append(email_data)
                except Exception as e:
                    current_app.logger.error(f'خطأ في قراءة الإيميل {filename}: {e}')
        
        return sorted(emails, key=lambda x: x.get('created_at', ''), reverse=True)
    
    def get_email_details(self, email_id: str) -> Optional[Dict[str, Any]]:
        """جلب تفاصيل إيميل محدد"""
        email_file_path = os.path.join(self.emails_dir, f"{email_id}.json")
        
        if not os.path.exists(email_file_path):
            return None
        
        try:
            with open(email_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            current_app.logger.error(f'خطأ في قراءة تفاصيل الإيميل {email_id}: {e}')
            return None
    
    def delete_email(self, email_id: str) -> bool:
        """حذف إيميل من القائمة"""
        try:
            email_file_path = os.path.join(self.emails_dir, f"{email_id}.json")
            html_file_path = os.path.join(self.emails_dir, f"{email_id}.html")
            
            # حذف الملفات الأساسية
            if os.path.exists(email_file_path):
                os.remove(email_file_path)
            if os.path.exists(html_file_path):
                os.remove(html_file_path)
            
            # حذف المرفقات
            email_data = self.get_email_details(email_id)
            if email_data and 'attachments' in email_data:
                for attachment in email_data['attachments']:
                    if 'file_path' in attachment and os.path.exists(attachment['file_path']):
                        os.remove(attachment['file_path'])
            
            return True
        except Exception as e:
            current_app.logger.error(f'خطأ في حذف الإيميل {email_id}: {e}')
            return False


def create_operation_email_template_simple(
    operation_data: Dict[str, Any],
    vehicle_plate: str,
    driver_name: str
) -> str:
    """إنشاء قالب HTML مبسط للإيميل"""
    
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
    
    operation_type = operation_data.get('operation_type', 'غير محدد')
    operation_type_display = operation_type_names.get(operation_type, operation_type)
    
    status = operation_data.get('status', 'غير محدد')
    status_display = status_names.get(status, status)
    
    html_content = f"""
    <!DOCTYPE html>
    <html dir="rtl" lang="ar">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; direction: rtl; margin: 20px; }}
            .header {{ background: #1e3a5c; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; }}
            .info-box {{ background: #f8f9fa; padding: 15px; margin: 10px 0; border-right: 3px solid #1e3a5c; }}
            .vehicle-info {{ background: #28a745; color: white; padding: 15px; margin: 10px 0; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>شركة رأس السعودية المحدودة</h1>
            <h2>نظام نُظم - إدارة المركبات</h2>
        </div>
        
        <div class="content">
            <h2>تفاصيل العملية</h2>
            
            <div class="info-box">
                <p><strong>عنوان العملية:</strong> {operation_data.get('title', 'غير محدد')}</p>
                <p><strong>نوع العملية:</strong> {operation_type_display}</p>
                <p><strong>الحالة:</strong> {status_display}</p>
                <p><strong>تاريخ الطلب:</strong> {operation_data.get('requested_at', 'غير محدد')}</p>
                <p><strong>طالب العملية:</strong> {operation_data.get('requester', 'غير محدد')}</p>
            </div>
            
            <div class="vehicle-info">
                <h3>معلومات المركبة</h3>
                <p><strong>رقم اللوحة:</strong> {vehicle_plate}</p>
                <p><strong>السائق الحالي:</strong> {driver_name}</p>
            </div>
            
            {f'<div class="info-box"><p><strong>الوصف:</strong> {operation_data.get("description")}</p></div>' if operation_data.get('description') else ''}
            
            <div class="info-box">
                <h3>المرفقات</h3>
                <ul>
                    <li>ملف Excel مع تفاصيل العملية</li>
                    <li>ملف PDF للمستندات (حسب نوع العملية)</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_content