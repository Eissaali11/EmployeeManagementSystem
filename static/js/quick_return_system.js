/**
 * نظام الإرجاع السريع للسيارات
 * Quick Return System for Vehicles
 */

// دالة لتحميل بيانات السائق الحالي تلقائياً
async function loadDriverInfoForReturn(vehicleId) {
    if (!vehicleId) {
        console.warn('معرف السيارة مطلوب');
        return;
    }

    try {
        console.log(`🔍 جاري تحميل بيانات السائق للسيارة: ${vehicleId}`);
        
        const response = await fetch(`/mobile/get_vehicle_driver_info/${vehicleId}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        const data = await response.json();
        
        if (data.success) {
            console.log('✅ تم تحميل بيانات السائق بنجاح:', data);
            
            // تعبئة حقول النموذج تلقائياً
            fillReturnFormFields(data.driver_info);
            
            // إظهار رسالة نجاح
            showSuccessMessage('تم تحميل بيانات السائق الحالي بنجاح');
            
            return data;
        } else {
            console.warn('⚠️ لم يتم العثور على بيانات السائق:', data.error);
            showWarningMessage(data.error || 'لم يتم العثور على بيانات السائق الحالي');
            return null;
        }
    } catch (error) {
        console.error('❌ خطأ في تحميل بيانات السائق:', error);
        showErrorMessage('حدث خطأ في تحميل بيانات السائق');
        return null;
    }
}

// دالة لتعبئة حقول النموذج بناءً على بيانات السائق
function fillReturnFormFields(driverInfo) {
    if (!driverInfo) {
        console.warn('بيانات السائق غير متوفرة');
        return;
    }

    // تعبئة حقول النموذج
    const fields = {
        'person_name': driverInfo.name,
        'person_phone': driverInfo.phone,
        'person_national_id': driverInfo.national_id,
        'employee_id': driverInfo.employee_id
    };

    Object.keys(fields).forEach(fieldName => {
        const field = document.querySelector(`[name="${fieldName}"], #${fieldName}`);
        if (field && fields[fieldName]) {
            field.value = fields[fieldName];
            
            // إضافة تأثير بصري لإظهار أن الحقل تم تعبئته تلقائياً
            field.classList.add('auto-filled');
            field.style.backgroundColor = '#e8f5e8';
            
            console.log(`📝 تم تعبئة حقل ${fieldName}: ${fields[fieldName]}`);
        }
    });

    // تغيير نوع العملية إلى استلام
    const handoverTypeField = document.querySelector('[name="handover_type"], #handover_type');
    if (handoverTypeField) {
        handoverTypeField.value = 'return';
        handoverTypeField.style.backgroundColor = '#fff3cd';
        console.log('🔄 تم تغيير نوع العملية إلى: استلام');
    }
}

// دالة لإظهار رسائل النجاح
function showSuccessMessage(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-success alert-dismissible fade show';
    alert.innerHTML = `
        <i class="fas fa-check-circle me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // إضافة الرسالة في أعلى النموذج
    const form = document.querySelector('form');
    if (form) {
        form.insertBefore(alert, form.firstChild);
        
        // إخفاء الرسالة تلقائياً بعد 5 ثوان
        setTimeout(() => {
            alert.remove();
        }, 5000);
    }
}

// دالة لإظهار رسائل التحذير
function showWarningMessage(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-warning alert-dismissible fade show';
    alert.innerHTML = `
        <i class="fas fa-exclamation-triangle me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const form = document.querySelector('form');
    if (form) {
        form.insertBefore(alert, form.firstChild);
        setTimeout(() => alert.remove(), 7000);
    }
}

// دالة لإظهار رسائل الخطأ
function showErrorMessage(message) {
    const alert = document.createElement('div');
    alert.className = 'alert alert-danger alert-dismissible fade show';
    alert.innerHTML = `
        <i class="fas fa-times-circle me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const form = document.querySelector('form');
    if (form) {
        form.insertBefore(alert, form.firstChild);
        setTimeout(() => alert.remove(), 10000);
    }
}

// دالة لإضافة زر الإرجاع السريع
function addQuickReturnButton(vehicleId) {
    if (!vehicleId) return;

    const container = document.querySelector('.quick-actions, .form-actions, .d-flex');
    if (!container) return;

    const quickReturnBtn = document.createElement('button');
    quickReturnBtn.type = 'button';
    quickReturnBtn.className = 'btn btn-warning me-2';
    quickReturnBtn.innerHTML = `
        <i class="fas fa-undo me-2"></i>
        إرجاع سريع
    `;
    
    quickReturnBtn.addEventListener('click', async () => {
        quickReturnBtn.disabled = true;
        quickReturnBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>جاري التحميل...';
        
        await loadDriverInfoForReturn(vehicleId);
        
        quickReturnBtn.disabled = false;
        quickReturnBtn.innerHTML = '<i class="fas fa-undo me-2"></i>إرجاع سريع';
    });

    container.insertBefore(quickReturnBtn, container.firstChild);
    console.log('✅ تم إضافة زر الإرجاع السريع');
}

// تهيئة النظام عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 تم تحميل نظام الإرجاع السريع');
    
    // البحث عن معرف السيارة في الصفحة
    const vehicleIdField = document.querySelector('[name="vehicle_id"], #vehicle_id');
    if (vehicleIdField) {
        const vehicleId = vehicleIdField.value;
        if (vehicleId) {
            console.log(`🚗 تم اكتشاف السيارة: ${vehicleId}`);
            
            // إضافة زر الإرجاع السريع
            addQuickReturnButton(vehicleId);
            
            // إضافة مستمع للتغييرات في حقل السيارة
            vehicleIdField.addEventListener('change', function() {
                if (this.value) {
                    loadDriverInfoForReturn(this.value);
                }
            });
        }
    }
    
    // إضافة أنماط CSS للحقول المُعبأة تلقائياً
    const style = document.createElement('style');
    style.textContent = `
        .auto-filled {
            border-left: 4px solid #28a745 !important;
            transition: background-color 0.3s ease;
        }
        
        .auto-filled:focus {
            box-shadow: 0 0 0 0.2rem rgba(40, 167, 69, 0.25) !important;
        }
        
        .quick-return-indicator {
            position: relative;
        }
        
        .quick-return-indicator::after {
            content: "🔄";
            position: absolute;
            right: 10px;
            top: 50%;
            transform: translateY(-50%);
        }
    `;
    document.head.appendChild(style);
});

// تصدير الوظائف للاستخدام الخارجي
window.QuickReturnSystem = {
    loadDriverInfoForReturn,
    fillReturnFormFields,
    addQuickReturnButton,
    showSuccessMessage,
    showWarningMessage,
    showErrorMessage
};