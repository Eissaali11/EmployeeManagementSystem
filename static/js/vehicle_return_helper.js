/**
 * مساعد إرجاع السيارات - تحسين تجربة المستخدم
 * Vehicle Return Helper - Enhanced User Experience
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 تم تحميل مساعد إرجاع السيارات');
    
    // إضافة منطق تحسين عرض الاستلام للسيارات غير المتاحة
    const vehicleSelect = document.querySelector('#vehicle_id, [name="vehicle_id"]');
    const handoverTypeSelect = document.querySelector('#handover_type, [name="handover_type"]');
    
    if (vehicleSelect && handoverTypeSelect) {
        // عند تغيير السيارة المحددة
        vehicleSelect.addEventListener('change', function() {
            const selectedOption = this.options[this.selectedIndex];
            const vehicleStatus = selectedOption.getAttribute('data-status');
            
            if (vehicleStatus && vehicleStatus !== 'available') {
                // السيارة غير متاحة - عرض رسالة واضحة مع خيار الاستلام
                showUnavailableVehicleOptions(selectedOption, vehicleStatus);
                
                // تغيير نوع العملية تلقائياً إلى استلام
                handoverTypeSelect.value = 'return';
                handoverTypeSelect.style.backgroundColor = '#fff3cd';
                
                // إضافة زر إرجاع سريع
                addQuickReturnButton(this.value);
            } else {
                // السيارة متاحة - إخفاء الرسائل الخاصة
                hideUnavailableVehicleOptions();
            }
        });
        
        // عند تغيير نوع العملية
        handoverTypeSelect.addEventListener('change', function() {
            const vehicleStatus = getSelectedVehicleStatus();
            
            if (vehicleStatus !== 'available' && this.value !== 'return') {
                // منع التسليم للسيارات غير المتاحة
                showWarning('لا يمكن تسليم هذه السيارة لأنها غير متاحة. يمكن فقط إجراء عملية استلام.');
                this.value = 'return';
            }
        });
    }
    
    function showUnavailableVehicleOptions(selectedOption, vehicleStatus) {
        // إزالة أي رسائل سابقة
        hideUnavailableVehicleOptions();
        
        const plateNumber = selectedOption.textContent;
        const statusText = getStatusText(vehicleStatus);
        
        // إنشاء رسالة توضيحية
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-info mt-3 unavailable-vehicle-alert';
        alertDiv.innerHTML = `
            <div class="d-flex align-items-center mb-2">
                <i class="fas fa-info-circle me-2"></i>
                <strong>السيارة ${plateNumber} - ${statusText}</strong>
            </div>
            <p class="mb-2">هذه السيارة غير متاحة حالياً. يمكنك:</p>
            <div class="d-grid gap-2">
                <button type="button" class="btn btn-warning btn-sm quick-return-btn" data-vehicle-id="${selectedOption.value}">
                    <i class="fas fa-undo me-2"></i>
                    استلام سريع - تحميل بيانات السائق الحالي
                </button>
                <button type="button" class="btn btn-outline-secondary btn-sm manual-return-btn">
                    <i class="fas fa-edit me-2"></i>
                    استلام يدوي - إدخال البيانات يدوياً
                </button>
            </div>
        `;
        
        // إضافة الرسالة بعد حقل اختيار السيارة
        const vehicleSelect = document.querySelector('#vehicle_id, [name="vehicle_id"]');
        vehicleSelect.parentNode.insertBefore(alertDiv, vehicleSelect.nextSibling);
        
        // إضافة مستمعي الأحداث للأزرار
        alertDiv.querySelector('.quick-return-btn').addEventListener('click', handleQuickReturn);
        alertDiv.querySelector('.manual-return-btn').addEventListener('click', handleManualReturn);
    }
    
    function hideUnavailableVehicleOptions() {
        const existingAlert = document.querySelector('.unavailable-vehicle-alert');
        if (existingAlert) {
            existingAlert.remove();
        }
    }
    
    function getSelectedVehicleStatus() {
        const vehicleSelect = document.querySelector('#vehicle_id, [name="vehicle_id"]');
        if (!vehicleSelect || !vehicleSelect.selectedOptions.length) return 'available';
        
        return vehicleSelect.selectedOptions[0].getAttribute('data-status') || 'available';
    }
    
    function getStatusText(status) {
        const statusMap = {
            'in_use': 'قيد الاستخدام',
            'maintenance': 'في الصيانة',
            'rented': 'مؤجرة',
            'in_project': 'في مشروع',
            'available': 'متاحة'
        };
        return statusMap[status] || status;
    }
    
    async function handleQuickReturn(event) {
        const vehicleId = event.target.getAttribute('data-vehicle-id');
        const button = event.target;
        
        // تعطيل الزر وإظهار مؤشر التحميل
        button.disabled = true;
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>جاري تحميل البيانات...';
        
        try {
            // استدعاء API لجلب بيانات السائق
            const response = await fetch(`/mobile/get_vehicle_driver_info/${vehicleId}`);
            const data = await response.json();
            
            if (data.success && data.driver_info) {
                // تعبئة الحقول تلقائياً
                fillDriverFields(data.driver_info);
                showSuccess('تم تحميل بيانات السائق الحالي بنجاح');
                
                // تغيير نوع العملية إلى استلام
                const handoverTypeSelect = document.querySelector('#handover_type, [name="handover_type"]');
                if (handoverTypeSelect) {
                    handoverTypeSelect.value = 'return';
                    handoverTypeSelect.style.backgroundColor = '#d1ecf1';
                }
                
                // التمرير إلى قسم بيانات السائق
                const driverSection = document.querySelector('#driver-info-section, .card:nth-child(2)');
                if (driverSection) {
                    driverSection.scrollIntoView({ behavior: 'smooth' });
                }
            } else {
                showWarning(data.error || 'لم يتم العثور على بيانات السائق الحالي');
            }
        } catch (error) {
            showError('حدث خطأ في تحميل بيانات السائق: ' + error.message);
        } finally {
            // إعادة تفعيل الزر
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-undo me-2"></i>استلام سريع - تحميل بيانات السائق الحالي';
        }
    }
    
    function handleManualReturn(event) {
        // تغيير نوع العملية إلى استلام
        const handoverTypeSelect = document.querySelector('#handover_type, [name="handover_type"]');
        if (handoverTypeSelect) {
            handoverTypeSelect.value = 'return';
            handoverTypeSelect.style.backgroundColor = '#d1ecf1';
        }
        
        // التمرير إلى قسم بيانات السائق
        const driverSection = document.querySelector('#driver-info-section, .card:nth-child(2)');
        if (driverSection) {
            driverSection.scrollIntoView({ behavior: 'smooth' });
        }
        
        showInfo('يرجى تعبئة بيانات السائق يدوياً لإجراء عملية الاستلام');
    }
    
    function fillDriverFields(driverInfo) {
        const fields = [
            { name: 'person_name', value: driverInfo.name },
            { name: 'person_phone', value: driverInfo.phone },
            { name: 'person_national_id', value: driverInfo.national_id },
            { name: 'employee_id', value: driverInfo.employee_id }
        ];
        
        fields.forEach(field => {
            const element = document.querySelector(`[name="${field.name}"], #${field.name}`);
            if (element && field.value) {
                element.value = field.value;
                element.style.backgroundColor = '#d4edda';
                element.classList.add('auto-filled');
                
                // إضافة أيقونة تأكيد
                addSuccessIcon(element);
            }
        });
    }
    
    function addSuccessIcon(element) {
        // إزالة أي أيقونة موجودة
        const existingIcon = element.parentNode.querySelector('.auto-fill-icon');
        if (existingIcon) existingIcon.remove();
        
        // إضافة أيقونة جديدة
        const icon = document.createElement('i');
        icon.className = 'fas fa-check-circle text-success auto-fill-icon';
        icon.style.position = 'absolute';
        icon.style.left = '10px';
        icon.style.top = '50%';
        icon.style.transform = 'translateY(-50%)';
        icon.style.zIndex = '10';
        
        element.parentNode.style.position = 'relative';
        element.parentNode.appendChild(icon);
    }
    
    function addQuickReturnButton(vehicleId) {
        // التحقق من وجود الزر مسبقاً
        if (document.querySelector('.main-quick-return-btn')) return;
        
        const actionsContainer = document.querySelector('.form-actions, .d-flex.gap-2');
        if (!actionsContainer) return;
        
        const quickReturnBtn = document.createElement('button');
        quickReturnBtn.type = 'button';
        quickReturnBtn.className = 'btn btn-warning main-quick-return-btn';
        quickReturnBtn.innerHTML = '<i class="fas fa-undo me-2"></i>إرجاع سريع';
        quickReturnBtn.setAttribute('data-vehicle-id', vehicleId);
        
        quickReturnBtn.addEventListener('click', handleQuickReturn);
        actionsContainer.insertBefore(quickReturnBtn, actionsContainer.firstChild);
    }
    
    // دوال الرسائل
    function showSuccess(message) {
        showMessage(message, 'success', 'fas fa-check-circle');
    }
    
    function showInfo(message) {
        showMessage(message, 'info', 'fas fa-info-circle');
    }
    
    function showWarning(message) {
        showMessage(message, 'warning', 'fas fa-exclamation-triangle');
    }
    
    function showError(message) {
        showMessage(message, 'danger', 'fas fa-times-circle');
    }
    
    function showMessage(message, type, icon) {
        // إزالة أي رسائل سابقة
        const existingToast = document.querySelector('.vehicle-return-toast');
        if (existingToast) existingToast.remove();
        
        const toast = document.createElement('div');
        toast.className = `alert alert-${type} alert-dismissible fade show vehicle-return-toast`;
        toast.style.position = 'fixed';
        toast.style.top = '20px';
        toast.style.right = '20px';
        toast.style.zIndex = '9999';
        toast.style.maxWidth = '300px';
        
        toast.innerHTML = `
            <i class="${icon} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(toast);
        
        // إزالة تلقائية بعد 5 ثوان
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 5000);
    }
});