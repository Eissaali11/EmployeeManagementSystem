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
        f"مرحباً {vehicle_data.get('driver_name', '')} 👋",
        "",
        f"🚗 بخصوص المركبة رقم: {vehicle_data.get('plate_number', '')}",
        f"📅 تاريخ {vehicle_data.get('handover_type', '')}: {vehicle_data.get('date', '')}",
        "",
        "🚗 عزيزي السائق، نتمنى لك قيادة آمنة",
        "",
        "⚠️ تنبيهات مهمة:",
        "🔧 تأكد من تغيير زيت السيارة في موعده",
        "🛡️ حافظ على السيارة فهي أمانة ومسؤوليتك", 
        "⛽ تفقد مستوى الوقود والماء بانتظام",
        "🚦 التزم بقوانين المرور وحدود السرعة",
        "",
        "📞 أرقام الطوارئ المهمة:",
        "🚗 نجم: 920000560",
        "🚔 المرور: 993", 
        "🚑 الهلال الأحمر: 997",
        "👮 الشرطة: 999",
        "🛡️ أمن الطرق: 996",
        "",
        "📄 المستندات:",
        f"📋 ملف PDF: {vehicle_data.get('pdf_url', '')}",
    ]
    
    if vehicle_data.get('registration_image_url'):
        message_parts.append(f"📝 صورة الاستمارة: {vehicle_data.get('registration_image_url')}")
    
    message_parts.extend(["", "🙏 شكراً لك والسلامة في الطريق"])
    
    message = "\n".join(message_parts)
    
    # ترميز بسيط للنص العربي
    encoded_message = message.replace(' ', '%20').replace('\n', '%0A').replace(':', '%3A').replace('/', '%2F')
    
    return f"https://wa.me/{clean_phone}?text={encoded_message}"