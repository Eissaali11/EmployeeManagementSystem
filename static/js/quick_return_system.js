/**
 * نظام الإرجاع السريع للسيارات
 * Quick Return System for Vehicles
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 تم تحميل نظام الإرجاع السريع للسيارات');
    
    // ربط الأحداث بالأزرار
    setupQuickReturnButtons();
    
    function setupQuickReturnButtons() {
        const quickReturnBtn = document.getElementById('quick-return-btn');
        
        if (quickReturnBtn) {
            quickReturnBtn.addEventListener('click', handleQuickReturn);
        }
        
        // مراقبة تغيير السيارة لإضافة بيانات الحالة
        const vehicleSelect = document.getElementById('vehicle_id');
        if (vehicleSelect) {
            vehicleSelect.addEventListener('change', handleVehicleChange);
        }
    }
    
    async function handleQuickReturn() {
        const vehicleSelect = document.getElementById('vehicle_id');
        const selectedVehicleId = vehicleSelect.value;
        
        if (!selectedVehicleId) {
            showMessage('يرجى اختيار سيارة أولاً', 'warning');
            return;
        }
        
        const button = document.getElementById('quick-return-btn');
        
        // تعطيل الزر وإظهار مؤشر التحميل
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>جاري تحميل البيانات...';
        
        try {
            const response = await fetch(`/mobile/get_vehicle_driver_info/${selectedVehicleId}`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.success && data.driver_info) {
                // تعبئة بيانات السائق
                fillDriverData(data.driver_info);
                
                // تغيير نوع العملية إلى استلام
                setOperationType('return');
                
                // إظهار النموذج
                showHandoverForm();
                
                // إظهار رسالة نجاح
                showMessage('تم تحميل بيانات السائق الحالي بنجاح ✓', 'success');
                
                // التمرير إلى النموذج
                scrollToForm();
                
            } else {
                showMessage(data.message || 'لم يتم العثور على بيانات السائق الحالي', 'warning');
            }
            
        } catch (error) {
            console.error('خطأ في تحميل بيانات السائق:', error);
            showMessage('حدث خطأ في تحميل البيانات. يرجى المحاولة مرة أخرى.', 'error');
        } finally {
            // إعادة تفعيل الزر
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-undo me-2"></i> استلام سريع - تحميل بيانات السائق';
        }
    }
    
    function fillDriverData(driverInfo) {
        const fields = [
            { id: 'person_name', value: driverInfo.name },
            { id: 'employee_id', value: driverInfo.employee_id },
            { name: 'person_phone', value: driverInfo.phone },
            { name: 'person_national_id', value: driverInfo.national_id }
        ];
        
        fields.forEach(field => {
            let element = null;
            
            if (field.id) {
                element = document.getElementById(field.id);
            } else if (field.name) {
                element = document.querySelector(`[name="${field.name}"]`);
            }
            
            if (element && field.value) {
                element.value = field.value;
                element.style.backgroundColor = '#d4edda'; // خلفية خضراء فاتحة
                element.style.border = '2px solid #28a745';
                
                // إضافة علامة تأكيد
                addCheckIcon(element);
            }
        });
    }
    
    function setOperationType(type) {
        const handoverTypeSelect = document.getElementById('handover_type');
        if (handoverTypeSelect) {
            handoverTypeSelect.value = type;
            handoverTypeSelect.style.backgroundColor = '#cce5ff';
            handoverTypeSelect.style.border = '2px solid #007bff';
        }
    }
    
    function showHandoverForm() {
        const formContainer = document.getElementById('handover-form-container');
        if (formContainer) {
            formContainer.classList.remove('d-none');
            
            // إضافة تأثير انتقالي
            formContainer.style.opacity = '0';
            formContainer.style.transform = 'translateY(20px)';
            
            setTimeout(() => {
                formContainer.style.transition = 'all 0.5s ease';
                formContainer.style.opacity = '1';
                formContainer.style.transform = 'translateY(0)';
            }, 100);
        }
    }
    
    function scrollToForm() {
        const formContainer = document.getElementById('handover-form-container');
        if (formContainer) {
            setTimeout(() => {
                formContainer.scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'start' 
                });
            }, 600);
        }
    }
    
    function addCheckIcon(element) {
        // إزالة أي أيقونة موجودة مسبقاً
        const existingIcon = element.parentNode.querySelector('.check-icon');
        if (existingIcon) {
            existingIcon.remove();
        }
        
        // إنشاء أيقونة تأكيد
        const checkIcon = document.createElement('i');
        checkIcon.className = 'fas fa-check-circle text-success check-icon';
        checkIcon.style.position = 'absolute';
        checkIcon.style.left = '10px';
        checkIcon.style.top = '50%';
        checkIcon.style.transform = 'translateY(-50%)';
        checkIcon.style.zIndex = '10';
        checkIcon.style.fontSize = '1.2em';
        
        // التأكد من أن الحاوي له position relative
        element.parentNode.style.position = 'relative';
        element.parentNode.appendChild(checkIcon);
    }
    
    function handleVehicleChange() {
        const vehicleSelect = document.getElementById('vehicle_id');
        const selectedOption = vehicleSelect.options[vehicleSelect.selectedIndex];
        const vehicleStatus = selectedOption.getAttribute('data-status');
        
        // إخفاء/إظهار رسائل التنبيه حسب حالة السيارة
        const alertAvailable = document.getElementById('vehicle-status-alert-avaliable');
        const alertOutOfService = document.getElementById('vehicle-status-alert');
        
        if (vehicleStatus === 'out_of_service') {
            // السيارة خارج الخدمة
            if (alertOutOfService) alertOutOfService.classList.remove('d-none');
            if (alertAvailable) alertAvailable.classList.add('d-none');
        } else if (vehicleStatus !== 'available') {
            // السيارة غير متاحة (قيد الاستخدام، صيانة، إلخ)
            if (alertAvailable) alertAvailable.classList.remove('d-none');
            if (alertOutOfService) alertOutOfService.classList.add('d-none');
        } else {
            // السيارة متاحة
            if (alertAvailable) alertAvailable.classList.add('d-none');
            if (alertOutOfService) alertOutOfService.classList.add('d-none');
        }
    }
    
    function showMessage(message, type) {
        const toast = document.createElement('div');
        toast.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show position-fixed`;
        toast.style.top = '20px';
        toast.style.right = '20px';
        toast.style.zIndex = '9999';
        toast.style.maxWidth = '350px';
        toast.style.boxShadow = '0 4px 12px rgba(0,0,0,0.2)';
        
        const iconMap = {
            success: 'fa-check-circle',
            warning: 'fa-exclamation-triangle',
            error: 'fa-times-circle',
            info: 'fa-info-circle'
        };
        
        const icon = iconMap[type] || 'fa-info-circle';
        
        toast.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="fas ${icon} me-2"></i>
                <span>${message}</span>
            </div>
            <button type="button" class="btn-close" onclick="this.parentElement.remove()"></button>
        `;
        
        document.body.appendChild(toast);
        
        // إزالة تلقائية بعد 5 ثوان
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 5000);
    }
    
    // إضافة أنماط CSS ديناميكية
    const style = document.createElement('style');
    style.textContent = `
        .check-icon {
            animation: bounceIn 0.6s ease;
        }
        
        @keyframes bounceIn {
            0% { transform: translateY(-50%) scale(0); }
            50% { transform: translateY(-50%) scale(1.2); }
            100% { transform: translateY(-50%) scale(1); }
        }
        
        .auto-filled-field {
            background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
            border: 2px solid #28a745 !important;
        }
    `;
    document.head.appendChild(style);
});

// تصدير الوظائف للاستخدام العام
window.QuickReturnSystem = {
    init: function() {
        console.log('تم تهيئة نظام الإرجاع السريع');
    }
};