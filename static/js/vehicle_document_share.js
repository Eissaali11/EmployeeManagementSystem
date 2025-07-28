/**
 * نصوص JavaScript لمشاركة وثائق السيارة عبر الواتساب
 */

function shareVehicleDocuments() {
    // الحصول على معلومات السيارة من الصفحة
    const plateNumber = document.querySelector('[data-plate-number]')?.dataset.plateNumber || '';
    const make = document.querySelector('[data-make]')?.dataset.make || '';
    const model = document.querySelector('[data-model]')?.dataset.model || '';
    const year = document.querySelector('[data-year]')?.dataset.year || '';
    
    // معلومات السائق الحالي
    const currentDriver = document.querySelector('[data-current-driver]')?.dataset.currentDriver || 'غير محدد';
    const driverPhone = document.querySelector('[data-driver-phone]')?.dataset.driverPhone || '';
    
    // الروابط للوثائق
    const registrationFormLink = document.querySelector('[data-registration-form]')?.dataset.registrationForm || null;
    const insuranceFileLink = document.querySelector('[data-insurance-file]')?.dataset.insuranceFile || null;
    
    // إعداد رسالة مفصلة منظمة
    let message = `🚗 *تفاصيل مركبة - نُظم*\n\n`;
    message += `━━━━━━━━━━━━━━━━━━━━━━\n\n`;
    
    // معلومات المركبة
    message += `📋 *معلومات المركبة:*\n`;
    message += `🔹 رقم اللوحة: ${plateNumber}\n`;
    if (make) message += `🔹 الماركة: ${make}\n`;
    if (model) message += `🔹 الموديل: ${model}\n`;
    if (year) message += `🔹 السنة: ${year}\n`;
    message += `\n`;
    
    // معلومات السائق الحالي
    if (currentDriver && currentDriver !== 'غير محدد') {
        message += `👨‍💼 *السائق الحالي:*\n`;
        message += `🔹 الاسم: ${currentDriver}\n`;
        if (driverPhone) {
            message += `🔹 الهاتف: ${driverPhone}\n`;
        }
        message += `\n`;
    }
    
    // قسم الوثائق
    message += `📄 *الوثائق المرفقة:*\n\n`;
    
    if (registrationFormLink) {
        message += `📝 *صورة الاستمارة:*\n`;
        message += `${registrationFormLink}\n\n`;
    }
    
    if (insuranceFileLink) {
        message += `🛡️ *ملف التأمين:*\n`;
        message += `${insuranceFileLink}\n\n`;
    }
    
    if (!registrationFormLink && !insuranceFileLink) {
        message += `⚠️ لا توجد وثائق مرفوعة حالياً\n\n`;
    }
    
    message += `━━━━━━━━━━━━━━━━━━━━━━\n`;
    message += `📅 تاريخ المشاركة: ${new Date().toLocaleDateString('ar-SA')}\n`;
    message += `🏢 نُظم - نظام إدارة المركبات`;
    
    // استخدام Web Share API أو النسخ للحافظة
    if (navigator.share) {
        navigator.share({
            title: `وثائق المركبة ${plateNumber}`,
            text: message
        }).then(() => {
            showAlert('تم مشاركة الوثائق بنجاح!', 'success');
        }).catch((error) => {
            console.log('خطأ في المشاركة:', error);
            copyToClipboard(message);
        });
    } else {
        copyToClipboard(message);
    }
}

function copyToClipboard(text) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text).then(() => {
            showAlert('تم نسخ تفاصيل الوثائق للحافظة!', 'success');
        }).catch(() => {
            fallbackCopyToClipboard(text);
        });
    } else {
        fallbackCopyToClipboard(text);
    }
}

function fallbackCopyToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        const successful = document.execCommand('copy');
        if (successful) {
            showAlert('تم نسخ تفاصيل الوثائق للحافظة!', 'success');
        } else {
            showDocumentShareModal(text);
        }
    } catch (err) {
        showDocumentShareModal(text);
    }
    
    document.body.removeChild(textArea);
}

function showDocumentShareModal(text) {
    // إنشاء نافذة منبثقة لعرض النص
    const modal = document.createElement('div');
    modal.innerHTML = `
        <div class="modal fade" id="shareDocumentsModal" tabindex="-1">
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header bg-success text-white">
                        <h5 class="modal-title">
                            <i class="fab fa-whatsapp me-2"></i>
                            مشاركة وثائق المركبة
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p class="mb-3">انسخ النص التالي وشاركه عبر الواتساب:</p>
                        <div class="form-group">
                            <textarea class="form-control" rows="15" readonly style="font-family: 'Courier New', monospace; font-size: 12px;">${text}</textarea>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">إغلاق</button>
                        <button type="button" class="btn btn-success" onclick="selectTextarea()">
                            <i class="fas fa-copy me-1"></i>تحديد الكل
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    const bootstrapModal = new bootstrap.Modal(document.getElementById('shareDocumentsModal'));
    bootstrapModal.show();
    
    // حذف النافذة عند إغلاقها
    document.getElementById('shareDocumentsModal').addEventListener('hidden.bs.modal', function () {
        modal.remove();
    });
}

function selectTextarea() {
    const textarea = document.querySelector('#shareDocumentsModal textarea');
    textarea.select();
    textarea.setSelectionRange(0, 99999); // للجوال
    
    try {
        document.execCommand('copy');
        showAlert('تم نسخ النص بنجاح!', 'success');
    } catch (err) {
        console.log('خطأ في النسخ');
    }
}

function showAlert(message, type) {
    // إنشاء تنبيه مؤقت
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        <i class="fas fa-check-circle me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // إزالة التنبيه بعد 4 ثوان
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 4000);
}