// دالة محسنة لفتح واتساب مباشرة دون إعادة توجيه
function openWhatsAppDirectly(phone, driverName, plateNumber, handoverType, date, pdfUrl, registrationImageUrl) {
    // تنظيف رقم الهاتف
    const cleanPhone = phone.replace(/[+\s-]/g, '');
    
    // بناء قسم صورة الاستمارة
    let registrationSection = '';
    if (registrationImageUrl && registrationImageUrl !== 'None' && registrationImageUrl !== '') {
        registrationSection = `\n📄 الاستمارة:\n${registrationImageUrl}`;
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

تغيير الزيوت في موعدها

تفقد السوائل

التأكد من جاهزية السيارة

مع الشكر والتقدير، وقيادة آمنة دومًا.`;

    // تشفير الرسالة يدوياً لتجنب مشاكل encodeURIComponent
    const encodedMessage = message
        .replace(/\n/g, '%0A')
        .replace(/\s/g, '+')
        .replace(/،/g, '%D8%8C')
        .replace(/:/g, '%3A')
        .replace(/\./g, '%2E')
        .replace(/\(/g, '%28')
        .replace(/\)/g, '%29')
        .replace(/'/g, '%27')
        .replace(/"/g, '%22')
        .replace(/\//g, '%2F')
        .replace(/\?/g, '%3F')
        .replace(/&/g, '%26')
        .replace(/#/g, '%23')
        .replace(/\[/g, '%5B')
        .replace(/\]/g, '%5D')
        .replace(/@/g, '%40')
        .replace(/!/g, '%21')
        .replace(/\$/g, '%24')
        .replace(/\^/g, '%5E')
        .replace(/`/g, '%60')
        .replace(/\{/g, '%7B')
        .replace(/\}/g, '%7D')
        .replace(/\|/g, '%7C')
        .replace(/\\/g, '%5C')
        .replace(/~/g, '%7E')
        .replace(/;/g, '%3B')
        .replace(/=/g, '%3D')
        .replace(/</g, '%3C')
        .replace(/>/g, '%3E')
        .replace(/\+/g, '%2B');
    
    // إنشاء رابط wa.me بدون استخدام encodeURIComponent
    const directUrl = `https://wa.me/${cleanPhone}?text=${encodedMessage}`;
    
    console.log('Opening WhatsApp with URL:', directUrl);
    
    // فتح الرابط مباشرة
    window.open(directUrl, '_blank');
}

// دالة بديلة باستخدام window.location.href
function redirectToWhatsApp(phone, driverName, plateNumber, handoverType, date, pdfUrl, registrationImageUrl) {
    // تنظيف رقم الهاتف
    const cleanPhone = phone.replace(/[+\s-]/g, '');
    
    // بناء قسم صورة الاستمارة
    let registrationSection = '';
    if (registrationImageUrl && registrationImageUrl !== 'None' && registrationImageUrl !== '') {
        registrationSection = `\n📄 الاستمارة:\n${registrationImageUrl}`;
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

تغيير الزيوت في موعدها

تفقد السوائل

التأكد من جاهزية السيارة

مع الشكر والتقدير، وقيادة آمنة دومًا.`;
    
    // استخدام window.location.href للتوجيه المباشر لتجنب مشاكل api.whatsapp.com
    const whatsappUrl = `https://wa.me/${cleanPhone}?text=${encodeURIComponent(message)}`;
    
    console.log('Redirecting to WhatsApp:', whatsappUrl);
    
    // استخدام window.location.href للتوجيه المباشر
    window.location.href = whatsappUrl;
}