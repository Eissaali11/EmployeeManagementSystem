"""
نظام توليد رسائل الواتساب المحسنة للسائقين مع رسائل السلامة وأرقام الطوارئ
"""

import urllib.parse
from flask import url_for


def generate_enhanced_whatsapp_message(driver_name, vehicle_plate, handover_date, handover_type_ar, handover_id, registration_form_image=None):
    """
    توليد رسالة واتساب محسنة مع رسائل السلامة وأرقام الطوارئ
    
    Args:
        driver_name: اسم السائق
        vehicle_plate: رقم لوحة السيارة
        handover_date: تاريخ التسليم
        handover_type_ar: نوع العملية (تسليم/استلام)
        handover_id: معرف عملية التسليم
        registration_form_image: رابط صورة الاستمارة (اختياري)
    
    Returns:
        str: رسالة واتساب منسقة مع جميع المعلومات المطلوبة
    """
    
    # أرقام الطوارئ في السعودية
    emergency_numbers = {
        'najm': '920000560',  # نجم للتأمين والمساعدة على الطريق
        'traffic': '993',      # المرور
        'red_crescent': '997', # الهلال الأحمر
        'police': '999',       # الشرطة
        'road_security': '996' # أمن الطرق
    }
    
    # بناء الرسالة
    message_parts = []
    
    # التحية والمعلومات الأساسية
    message_parts.append(f"مرحباً {driver_name}")
    message_parts.append("")
    message_parts.append(f"بخصوص المركبة رقم: {vehicle_plate}")
    message_parts.append(f"تاريخ {handover_type_ar}: {handover_date}")
    message_parts.append("")
    
    # رسالة السلامة والتنبيهات
    safety_message = [
        "🚗 عزيزي السائق، نتمنى لك قيادة آمنة",
        "",
        "⚠️ تنبيهات مهمة:",
        "• تأكد من تغيير زيت السيارة في موعده",
        "• حافظ على السيارة فهي أمانة ومسؤوليتك",
        "• تفقد مستوى الوقود والماء بانتظام",
        "• التزم بقوانين المرور وحدود السرعة",
        ""
    ]
    message_parts.extend(safety_message)
    
    # أرقام الطوارئ
    emergency_section = [
        "📞 أرقام الطوارئ المهمة:",
        f"• نجم (المساعدة على الطريق): {emergency_numbers['najm']}",
        f"• المرور: {emergency_numbers['traffic']}",
        f"• الهلال الأحمر: {emergency_numbers['red_crescent']}",
        f"• الشرطة: {emergency_numbers['police']}",
        f"• أمن الطرق: {emergency_numbers['road_security']}",
        ""
    ]
    message_parts.extend(emergency_section)
    
    # روابط المستندات
    documents_section = [
        "📄 المستندات والروابط:",
    ]
    
    # رابط PDF التسليم/الاستلام
    pdf_url = url_for('vehicles.handover_pdf_public', id=handover_id, _external=True)
    documents_section.append(f"• ملف PDF للتسليم/الاستلام:")
    documents_section.append(pdf_url)
    
    # رابط صورة الاستمارة إذا كان متوفراً
    if registration_form_image:
        documents_section.append("")
        documents_section.append("• صورة الاستمارة:")
        # إنشاء رابط لصورة الاستمارة
        if registration_form_image.startswith('static/'):
            # إزالة static/ من بداية المسار لأن url_for سيضيفها
            image_path = registration_form_image[7:]
            registration_url = url_for('static', filename=image_path, _external=True)
        else:
            registration_url = url_for('static', filename=f'uploads/{registration_form_image}', _external=True)
        documents_section.append(registration_url)
    
    message_parts.extend(documents_section)
    message_parts.append("")
    
    # الختام
    message_parts.extend([
        "🙏 شكراً لك والسلامة في الطريق"
    ])
    
    # دمج جميع أجزاء الرسالة
    full_message = "\n".join(message_parts)
    
    return full_message


def generate_whatsapp_url(phone_number, driver_name, vehicle_plate, handover_date, handover_type_ar, handover_id, registration_form_image=None):
    """
    توليد رابط واتساب كامل مع الرسالة المحسنة
    
    Args:
        phone_number: رقم الهاتف
        driver_name: اسم السائق
        vehicle_plate: رقم لوحة السيارة
        handover_date: تاريخ التسليم
        handover_type_ar: نوع العملية (تسليم/استلام)
        handover_id: معرف عملية التسليم
        registration_form_image: رابط صورة الاستمارة (اختياري)
    
    Returns:
        str: رابط واتساب كامل مع الرسالة المرمزة
    """
    
    # تنظيف رقم الهاتف
    clean_phone = phone_number.replace('+', '').replace(' ', '').replace('-', '')
    
    # توليد الرسالة المحسنة
    message = generate_enhanced_whatsapp_message(
        driver_name, vehicle_plate, handover_date, 
        handover_type_ar, handover_id, registration_form_image
    )
    
    # ترميز الرسالة للـ URL
    encoded_message = urllib.parse.quote(message)
    
    # إنشاء رابط الواتساب
    whatsapp_url = f"https://wa.me/{clean_phone}?text={encoded_message}"
    
    return whatsapp_url


def get_emergency_numbers():
    """
    إرجاع قاموس بأرقام الطوارئ في السعودية
    
    Returns:
        dict: قاموس بأرقام الطوارئ
    """
    return {
        'najm': '920000560',  # نجم للتأمين والمساعدة على الطريق
        'traffic': '993',      # المرور
        'red_crescent': '997', # الهلال الأحمر
        'police': '999',       # الشرطة
        'road_security': '996' # أمن الطرق
    }