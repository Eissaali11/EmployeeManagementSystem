function openWhatsAppChat(phone, driverName, plateNumber, handoverType, date, pdfUrl, registrationImageUrl) {
    // تنظيف رقم الهاتف
    const cleanPhone = phone.replace(/[+\s-]/g, '');
    
    // بناء قسم صورة الاستمارة
    let registrationSection = '';
    if (registrationImageUrl && registrationImageUrl !== 'None' && registrationImageUrl !== '') {
        registrationSection = `\n📄 صورة الاستمارة:\n${registrationImageUrl}\n`;
    }
    
    // إنشاء رسالة مختصرة للسائق
    const message = `عزيزي السائق ${driverName}،
تم تفويضك بقيادة السيارة، ونتمنى لك قيادة آمنة.

📄 نموذج التسليم:
${pdfUrl}${registrationSection}
💬 محادثة نجم واتساب:
https://wa.me/966920000560
📞 رقم نجم الموحد: 199033

📞 أرقام الطوارئ:
🚑 997 | 🚓 993 | 🛣️ 996 | 🚔 999 | 🔥 998

📌 ملاحظة:
الرجاء المحافظة على السيارة:
• تغيير الزيوت في موعدها
• تفقد السوائل
• التأكد من جاهزية السيارة

مع الشكر والتقدير، وقيادة آمنة دومًا.`;
    
    // استخدام window.location.href للتوجيه المباشر لتجنب مشاكل api.whatsapp.com
    const whatsappUrl = `https://wa.me/${cleanPhone}?text=${encodeURIComponent(message)}`;
    
    console.log('Redirecting to WhatsApp:', whatsappUrl);
    
    // استخدام window.location.href للتوجيه المباشر
    window.location.href = whatsappUrl;
}

function openSimpleWhatsAppChat(phone, driverName, plateNumber) {
    // تنظيف رقم الهاتف
    const cleanPhone = phone.replace(/[+\s-]/g, '');
    
    // رسالة بسيطة جداً
    const message = `مرحبا ${driverName} - بخصوص المركبة ${plateNumber} - شكرا لك`;
    
    // إنشاء رابط wa.me مباشر
    const whatsappUrl = `https://wa.me/${cleanPhone}?text=${encodeURIComponent(message)}`;
    
    // فتح الرابط في نافذة جديدة
    window.open(whatsappUrl, '_blank');
}