function openWhatsAppChat(phone, driverName, plateNumber, handoverType, date, pdfUrl, registrationImageUrl) {
    // تنظيف رقم الهاتف
    const cleanPhone = phone.replace(/[+\s-]/g, '');
    
    // بناء قسم صورة الاستمارة
    let registrationSection = '';
    if (registrationImageUrl && registrationImageUrl !== 'None' && registrationImageUrl !== '') {
        registrationSection = `\n📄 صورة الاستمارة:\n${registrationImageUrl}\n`;
    }
    
    // إنشاء رسالة مفصلة بالتنسيق المطلوب
    const message = `عزيزي السائق ${driverName}،
تم تفويضك بقيادة السيارة، ونتمنى لك قيادة آمنة.

يرجى الاطلاع على الروابط التالية:

📄 نموذج التسليم:
${pdfUrl}${registrationSection}
💬 محادثة نجم عبر واتساب (للبلاغات):
https://wa.me/966920000560

📞 أرقام الطوارئ المهمة:
📍 نجم (الاتصال الموحد): 199033
🚑 الإسعاف: 997
🚔 الشرطة: 999
🚓 المرور: 993
🛣️ أمن الطرق: 996
🔥 الدفاع المدني: 998

📌 ملاحظة مهمة:
يرجى المحافظة على السيارة من خلال:
✔️ الالتزام بمواعيد تغيير الزيوت.
✔️ تفقد السوائل بشكل دوري.
✔️ التأكد من جاهزية السيارة وسلامتها.

شاكرين لك حرصك والتزامك، ونتمنى لك السلامة دائمًا.`;
    
    // محاولة استخدام deeplink مباشر للواتساب
    const whatsappDeepLink = `whatsapp://send?phone=${cleanPhone}&text=${encodeURIComponent(message)}`;
    const whatsappWebUrl = `https://wa.me/${cleanPhone}?text=${encodeURIComponent(message)}`;
    
    // تجربة فتح التطبيق مباشرة أولاً
    const isMobile = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
    
    if (isMobile) {
        // على الهاتف: تجربة فتح التطبيق مباشرة
        window.location.href = whatsappDeepLink;
        
        // fallback للويب بعد ثانية واحدة إذا لم يفتح التطبيق
        setTimeout(() => {
            window.open(whatsappWebUrl, '_blank');
        }, 1000);
    } else {
        // على سطح المكتب: فتح واتساب ويب مباشرة
        window.open(whatsappWebUrl, '_blank');
    }
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