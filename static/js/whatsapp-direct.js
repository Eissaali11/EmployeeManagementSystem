// دالة محسنة لفتح واتساب مباشرة دون إعادة توجيه
function openWhatsAppDirectly(phone, driverName, plateNumber, handoverType, date, pdfUrl, registrationImageUrl) {
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
    
    // رسالة مبسطة لتجنب مشاكل التشفير
    const simpleMessage = `مرحبا ${driverName} - بخصوص المركبة ${plateNumber} - رابط PDF: ${pdfUrl} - شكرا لك`;
    
    // استخدام window.location.href للتوجيه المباشر
    window.location.href = `https://wa.me/${cleanPhone}?text=${encodeURIComponent(simpleMessage)}`;
}