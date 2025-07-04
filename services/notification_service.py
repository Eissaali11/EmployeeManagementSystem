"""
خدمة الإشعارات والرسائل
"""
import os
from twilio.rest import Client
from utils.audit_logger import log_activity
from flask_login import current_user

class NotificationService:
    """خدمة إدارة الإشعارات والرسائل"""
    
    def __init__(self):
        self.twilio_account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        self.twilio_auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        self.twilio_phone_number = os.environ.get('TWILIO_PHONE_NUMBER')
        
        if all([self.twilio_account_sid, self.twilio_auth_token, self.twilio_phone_number]):
            self.twilio_client = Client(self.twilio_account_sid, self.twilio_auth_token)
        else:
            self.twilio_client = None
    
    def send_sms(self, to_phone_number, message):
        """إرسال رسالة نصية عبر Twilio"""
        if not self.twilio_client:
            log_activity(
                user_id=current_user.id if current_user.is_authenticated else None,
                action='sms_send_failed',
                details='فشل إرسال الرسالة: إعدادات Twilio غير مكتملة'
            )
            return False, "إعدادات Twilio غير مكتملة"
        
        try:
            message_obj = self.twilio_client.messages.create(
                body=message,
                from_=self.twilio_phone_number,
                to=to_phone_number
            )
            
            log_activity(
                user_id=current_user.id if current_user.is_authenticated else None,
                action='sms_sent',
                details=f'تم إرسال رسالة نصية إلى {to_phone_number}: {message[:50]}...'
            )
            
            return True, message_obj.sid
            
        except Exception as e:
            log_activity(
                user_id=current_user.id if current_user.is_authenticated else None,
                action='sms_send_failed',
                details=f'فشل إرسال الرسالة إلى {to_phone_number}: {str(e)}'
            )
            return False, str(e)
    
    def send_document_expiry_notification(self, employee, document):
        """إرسال إشعار انتهاء صلاحية وثيقة"""
        if not employee.mobile:
            return False, "رقم الهاتف غير متوفر"
        
        message = f"""
تنبيه: انتهاء صلاحية وثيقة

الموظف: {employee.name}
نوع الوثيقة: {document.document_type}
رقم الوثيقة: {document.document_number}
تاريخ الانتهاء: {document.expiry_date.strftime('%Y-%m-%d') if document.expiry_date else 'غير محدد'}

يرجى تجديد الوثيقة في أقرب وقت ممكن.
        """.strip()
        
        return self.send_sms(employee.mobile, message)
    
    def send_salary_notification(self, employee, salary):
        """إرسال إشعار الراتب"""
        if not employee.mobile:
            return False, "رقم الهاتف غير متوفر"
        
        message = f"""
إشعار الراتب

الموظف: {employee.name}
الشهر: {salary.month}/{salary.year}
الراتب الصافي: {salary.net_salary} ريال

تم إعداد راتبك الشهري.
        """.strip()
        
        return self.send_sms(employee.mobile, message)
    
    def send_attendance_reminder(self, employee):
        """إرسال تذكير الحضور"""
        if not employee.mobile:
            return False, "رقم الهاتف غير متوفر"
        
        message = f"""
تذكير الحضور

السيد/ة: {employee.name}
القسم: {employee.department.name if employee.department else 'غير محدد'}

لم يتم تسجيل حضورك اليوم. يرجى تسجيل الحضور.
        """.strip()
        
        return self.send_sms(employee.mobile, message)
    
    def send_vehicle_maintenance_reminder(self, vehicle):
        """إرسال تذكير صيانة المركبة"""
        # البحث عن المسؤول عن المركبة
        from models import VehicleHandover
        handover = VehicleHandover.query.filter_by(
            vehicle_id=vehicle.id,
            status='active'
        ).first()
        
        if not handover or not handover.employee_rel or not handover.employee_rel.mobile:
            return False, "لا يوجد مسؤول عن المركبة أو رقم هاتف"
        
        employee = handover.employee_rel
        message = f"""
تذكير صيانة المركبة

المسؤول: {employee.name}
المركبة: {vehicle.license_plate}
النوع: {vehicle.vehicle_type}

حان موعد صيانة المركبة. يرجى ترتيب الصيانة اللازمة.
        """.strip()
        
        return self.send_sms(employee.mobile, message)