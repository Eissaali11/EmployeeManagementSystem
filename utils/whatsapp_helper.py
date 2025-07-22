def create_simple_whatsapp_url(phone, message):
    """إنشاء رابط واتساب مبسط يتجه مباشرة للمحادثة"""
    # تنظيف رقم الهاتف
    clean_phone = phone.replace('+', '').replace(' ', '').replace('-', '')
    
    # رسالة مبسطة وقصيرة
    simple_message = f"مرحباً {message.get('name', '')} 👋\n\n🚗 بخصوص المركبة: {message.get('plate_number', '')}\n📅 تاريخ: {message.get('date', '')}\n\n📋 رابط PDF: {message.get('pdf_url', '')}\n\n🙏 شكراً لك"
    
    # استخدام wa.me مع ترميز بسيط
    return f"https://wa.me/{clean_phone}?text={simple_message.replace(' ', '%20').replace('\n', '%0A')}"

def create_enhanced_whatsapp_url(phone, vehicle_data):
    """إنشاء رابط واتساب محسن مع جميع التفاصيل"""
    clean_phone = phone.replace('+', '').replace(' ', '').replace('-', '')
    
    message_parts = [
        f"عزيزي السائق {vehicle_data.get('driver_name', '')}،",
        "تم تفويضك بقيادة السيارة، ونتمنى لك قيادة آمنة.",
        "",
        f"📄 نموذج التسليم:",
        f"{vehicle_data.get('pdf_url', '')}",
    ]
    
    if vehicle_data.get('registration_image_url'):
        message_parts.extend([
            "📄 الاستمارة:",
            f"{vehicle_data.get('registration_image_url')}"
        ])
    
    message_parts.extend([
        "",
        "💬 محادثة نجم واتساب:",
        "https://wa.me/966920000560",
        "📞 رقم نجم الموحد: 199033",
        "",
        "📞 أرقام الطوارئ:",
        "🚑 997 | 🚓 993 | 🛣️ 996 | 🚔 999 | 🔥 998",
        "",
        "📌 ملاحظة:",
        "الرجاء المحافظة على السيارة:",
        "• تغيير الزيوت في موعدها",
        "• تفقد السوائل",
        "• التأكد من جاهزية السيارة",
        "",
        "مع الشكر والتقدير، وقيادة آمنة دومًا."
    ])
    
    message = "\n".join(message_parts)
    
    # ترميز بسيط للنص العربي
    encoded_message = message.replace(' ', '%20').replace('\n', '%0A').replace(':', '%3A').replace('/', '%2F')
    
    return f"https://wa.me/{clean_phone}?text={encoded_message}"