function openWhatsAppChat(phone, driverName, plateNumber, handoverType, date, pdfUrl) {
    // تنظيف رقم الهاتف
    const cleanPhone = phone.replace(/[+\s-]/g, '');
    
    // إنشاء رسالة بسيطة
    const message = `مرحبا ${driverName} - بخصوص المركبة ${plateNumber} - تاريخ ${handoverType} ${date} - رابط PDF ${pdfUrl} - شكرا لك`;
    
    // إنشاء رابط wa.me مباشر
    const whatsappUrl = `https://wa.me/${cleanPhone}?text=${encodeURIComponent(message)}`;
    
    // فتح الرابط في نافذة جديدة
    window.open(whatsappUrl, '_blank');
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