import os
from twilio.rest import Client
from datetime import datetime

# الحصول على بيانات الاعتماد من متغيرات البيئة
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER")
# معرف قالب الرسالة
WHATSAPP_TEMPLATE_SID = "HXb5b62575e6e4ff6129ad7c8efe1f983e"

def send_salary_notification_whatsapp(employee, salary):
    """
    إرسال إشعار راتب للموظف عبر WhatsApp باستخدام Twilio
    
    Args:
        employee: كائن Employee يحتوي على بيانات الموظف
        salary: كائن Salary يحتوي على بيانات الراتب
        
    Returns:
        Boolean: True إذا تم الإرسال بنجاح، False إذا فشل الإرسال
    """
    try:
        # التحقق من وجود رقم هاتف للموظف
        if not employee.mobile:
            return False, "لا يوجد رقم هاتف مسجل للموظف"
            
        # التحقق من وجود بيانات اعتماد Twilio
        if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN or not TWILIO_PHONE_NUMBER:
            return False, "لم يتم تكوين بيانات اعتماد Twilio"
            
        # إعداد عميل Twilio
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # تنسيق رقم الهاتف (إضافة رمز الدولة +966 إذا لم يكن موجودًا)
        to_phone = employee.mobile
        if not to_phone.startswith('+'):
            # إذا كان الرقم يبدأ بـ 0، نحذفه ونضيف رمز الدولة
            if to_phone.startswith('0'):
                to_phone = "+966" + to_phone[1:]
            else:
                to_phone = "+966" + to_phone
                
        # تحضير بيانات الرسالة
        # استخدام النموذج الذي قمت بتوفيره
        
        # الحصول على اسم الشهر بالعربية
        month_names = {
            1: 'يناير', 2: 'فبراير', 3: 'مارس', 4: 'أبريل',
            5: 'مايو', 6: 'يونيو', 7: 'يوليو', 8: 'أغسطس',
            9: 'سبتمبر', 10: 'أكتوبر', 11: 'نوفمبر', 12: 'ديسمبر'
        }
        month_name = month_names.get(salary.month, str(salary.month))
        
        # تنسيق التاريخ والوقت
        date_string = f"{month_name}/{salary.year}"
        time_string = datetime.now().strftime("%I:%M%p")
        
        # إرسال الرسالة باستخدام واجهة برمجة تطبيقات Twilio
        message = client.messages.create(
            to=f'whatsapp:{to_phone}',
            from_=f'whatsapp:{TWILIO_PHONE_NUMBER}',
            content_sid=WHATSAPP_TEMPLATE_SID,
            content_variables=f'{{"1":"{date_string}","2":"{time_string}"}}'
        )
        
        return True, f"تم إرسال الإشعار بنجاح. SID: {message.sid}"
        
    except Exception as e:
        return False, f"حدث خطأ أثناء إرسال الإشعار: {str(e)}"


def send_salary_deduction_notification_whatsapp(employee, salary, deduction_reason=""):
    """
    إرسال إشعار خصم على الراتب للموظف عبر WhatsApp
    
    Args:
        employee: كائن Employee يحتوي على بيانات الموظف
        salary: كائن Salary يحتوي على بيانات الراتب
        deduction_reason: سبب الخصم (اختياري)
        
    Returns:
        Boolean: True إذا تم الإرسال بنجاح، False إذا فشل الإرسال
    """
    try:
        # التحقق من وجود رقم هاتف للموظف
        if not employee.mobile:
            return False, "لا يوجد رقم هاتف مسجل للموظف"
            
        # التحقق من وجود بيانات اعتماد Twilio
        if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN or not TWILIO_PHONE_NUMBER:
            return False, "لم يتم تكوين بيانات اعتماد Twilio"
            
        # التحقق من وجود خصم على الراتب
        if salary.deductions <= 0:
            return False, "لا يوجد خصم على هذا الراتب"
            
        # إعداد عميل Twilio
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # تنسيق رقم الهاتف (إضافة رمز الدولة +966 إذا لم يكن موجودًا)
        to_phone = employee.mobile
        if not to_phone.startswith('+'):
            # إذا كان الرقم يبدأ بـ 0، نحذفه ونضيف رمز الدولة
            if to_phone.startswith('0'):
                to_phone = "+966" + to_phone[1:]
            else:
                to_phone = "+966" + to_phone
                
        # الحصول على اسم الشهر بالعربية
        month_names = {
            1: 'يناير', 2: 'فبراير', 3: 'مارس', 4: 'أبريل',
            5: 'مايو', 6: 'يونيو', 7: 'يوليو', 8: 'أغسطس',
            9: 'سبتمبر', 10: 'أكتوبر', 11: 'نوفمبر', 12: 'ديسمبر'
        }
        month_name = month_names.get(salary.month, str(salary.month))
        
        # تنسيق التاريخ والوقت
        date_string = f"{month_name}/{salary.year}"
        
        # استخدام نفس النموذج ولكن مع متغيرات مختلفة
        # هنا نفترض أن النموذج المستخدم يمكن استخدامه للخصومات أيضًا
        
        message = client.messages.create(
            to=f'whatsapp:{to_phone}',
            from_=f'whatsapp:{TWILIO_PHONE_NUMBER}',
            content_sid=WHATSAPP_TEMPLATE_SID,
            content_variables=f'{{"1":"{date_string}","2":"{salary.deductions:.2f}"}}'
        )
        
        return True, f"تم إرسال إشعار الخصم بنجاح. SID: {message.sid}"
        
    except Exception as e:
        return False, f"حدث خطأ أثناء إرسال إشعار الخصم: {str(e)}"


def send_batch_salary_notifications_whatsapp(department_id=None, month=None, year=None):
    """
    إرسال إشعارات رواتب مجمعة لموظفي قسم معين أو لكل الموظفين عبر WhatsApp
    
    Args:
        department_id: معرف القسم (اختياري)
        month: رقم الشهر (إلزامي)
        year: السنة (إلزامي)
        
    Returns:
        tuple: (عدد الإشعارات الناجحة، عدد الإشعارات الفاشلة، قائمة برسائل الأخطاء)
    """
    from models import Salary, Employee
    
    success_count = 0
    failure_count = 0
    error_messages = []
    
    try:
        # بناء الاستعلام
        salary_query = Salary.query.filter_by(month=month, year=year)
        
        # إذا تم تحديد قسم معين
        if department_id:
            employees = Employee.query.filter_by(department_id=department_id).all()
            employee_ids = [emp.id for emp in employees]
            salary_query = salary_query.filter(Salary.employee_id.in_(employee_ids))
            
        # تنفيذ الاستعلام
        salaries = salary_query.all()
        
        # إرسال إشعار لكل موظف
        for salary in salaries:
            employee = salary.employee
            success, message = send_salary_notification_whatsapp(employee, salary)
            
            if success:
                success_count += 1
            else:
                failure_count += 1
                error_messages.append(f"فشل إرسال إشعار للموظف {employee.name}: {message}")
        
        return success_count, failure_count, error_messages
            
    except Exception as e:
        return 0, 0, [f"حدث خطأ عام أثناء إرسال الإشعارات: {str(e)}"]


def send_batch_deduction_notifications_whatsapp(department_id=None, month=None, year=None):
    """
    إرسال إشعارات خصومات مجمعة لموظفي قسم معين أو لكل الموظفين عبر WhatsApp
    
    Args:
        department_id: معرف القسم (اختياري)
        month: رقم الشهر (إلزامي)
        year: السنة (إلزامي)
        
    Returns:
        tuple: (عدد الإشعارات الناجحة، عدد الإشعارات الفاشلة، قائمة برسائل الأخطاء)
    """
    from models import Salary, Employee
    
    success_count = 0
    failure_count = 0
    error_messages = []
    
    try:
        # بناء الاستعلام - الرواتب التي تحتوي على خصومات
        salary_query = Salary.query.filter_by(month=month, year=year).filter(Salary.deductions > 0)
        
        # إذا تم تحديد قسم معين
        if department_id:
            employees = Employee.query.filter_by(department_id=department_id).all()
            employee_ids = [emp.id for emp in employees]
            salary_query = salary_query.filter(Salary.employee_id.in_(employee_ids))
            
        # تنفيذ الاستعلام
        salaries = salary_query.all()
        
        # إرسال إشعار لكل موظف
        for salary in salaries:
            employee = salary.employee
            success, message = send_salary_deduction_notification_whatsapp(employee, salary)
            
            if success:
                success_count += 1
            else:
                failure_count += 1
                error_messages.append(f"فشل إرسال إشعار الخصم للموظف {employee.name}: {message}")
        
        return success_count, failure_count, error_messages
            
    except Exception as e:
        return 0, 0, [f"حدث خطأ عام أثناء إرسال إشعارات الخصم: {str(e)}"]


def send_vehicle_handover_whatsapp(handover, recipient_phone, message_text=None):
    """
    إرسال إشعار تسليم/استلام مركبة عبر WhatsApp
    
    Args:
        handover: كائن VehicleHandover يحتوي على بيانات التسليم
        recipient_phone: رقم هاتف المستلم
        message_text: نص الرسالة المخصص (اختياري)
        
    Returns:
        Boolean: True إذا تم الإرسال بنجاح، False إذا فشل الإرسال
    """
    try:
        # التحقق من وجود بيانات اعتماد Twilio
        if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN or not TWILIO_PHONE_NUMBER:
            return False, "لم يتم تكوين بيانات اعتماد Twilio"
            
        # إعداد عميل Twilio
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        # تنسيق رقم الهاتف (إضافة رمز الدولة +966 إذا لم يكن موجودًا)
        to_phone = recipient_phone
        if not to_phone.startswith('+'):
            # إذا كان الرقم يبدأ بـ 0، نحذفه ونضيف رمز الدولة
            if to_phone.startswith('0'):
                to_phone = "+966" + to_phone[1:]
            else:
                to_phone = "+966" + to_phone
        
        # إنشاء رابط PDF المفتوح بدون تسجيل دخول
        from flask import url_for, request
        pdf_url = url_for('vehicles.handover_pdf_public', id=handover.id, _external=True)
        
        # إعداد نص الرسالة
        if not message_text:
            handover_type = "تسليم" if handover.handover_type == "delivery" else "استلام"
            vehicle_info = f"{handover.vehicle_rel.plate_number} - {handover.vehicle_rel.make} {handover.vehicle_rel.model}"
            handover_date = handover.handover_date.strftime('%d %B %Y') if handover.handover_date else "غير محدد"
            
            message_text = f"""مرحباً {handover.person_name}

بخصوص المركبة رقم: {handover.vehicle_rel.plate_number}
تاريخ {handover_type}: {handover_date}

رابط ملف PDF لبيانات التسليم/الاستلام:
{pdf_url}

شكراً لك"""
        
        # إرسال الرسالة
        message = client.messages.create(
            to=f'whatsapp:{to_phone}',
            from_=f'whatsapp:{TWILIO_PHONE_NUMBER}',
            body=message_text
        )
        
        return True, f"تم إرسال الإشعار بنجاح. SID: {message.sid}"
        
    except Exception as e:
        return False, f"حدث خطأ أثناء إرسال الإشعار: {str(e)}"