// ملف JavaScript منفصل لنموذج الاستلام السريع
document.addEventListener('DOMContentLoaded', function() {
    setupReturnChecklistButton();
});

function setupReturnChecklistButton() {
    const returnChecklistBtn = document.getElementById('show-return-checklist-btn');
    
    if (returnChecklistBtn) {
        returnChecklistBtn.onclick = function() {
            const vehicleSelect = document.getElementById('vehicle_id');
            const vehicleId = vehicleSelect.value;
            
            if (!vehicleId) {
                alert('يرجى اختيار السيارة أولاً');
                return;
            }
            
            console.log('عرض نموذج الاستلام للسيارة:', vehicleId);
            
            // إخفاء التحذير
            document.getElementById('vehicle-status-alert-avaliable').classList.add('d-none');
            
            // جلب بيانات السائق الحالي وملء النموذج
            fetch(`/mobile/get_vehicle_driver_info/${vehicleId}`)
                .then(response => response.json())
                .then(data => {
                    console.log('استجابة من الخادم:', data);
                    if (data.success) {
                        // ملء بيانات السائق في النموذج
                        fillReturnFormWithDriverData(data.driver_info, data.vehicle_info);
                        
                        // إظهار النموذج والتمرير إليه
                        const formContainer = document.querySelector('form[method="post"]');
                        if (formContainer) {
                            formContainer.scrollIntoView({ behavior: 'smooth' });
                        }
                    } else {
                        alert('خطأ في جلب بيانات السائق: ' + data.error);
                    }
                })
                .catch(error => {
                    console.error('خطأ:', error);
                    alert('حدث خطأ في الاتصال بالخادم');
                });
        };
    }
}

function fillReturnFormWithDriverData(driverInfo, vehicleInfo) {
    console.log('ملء النموذج ببيانات السائق:', driverInfo);
    
    // تحديد نوع العملية إلى استلام
    const handoverTypeSelect = document.getElementById('handover_type');
    if (handoverTypeSelect) {
        handoverTypeSelect.value = 'return';
        
        // إخفاء الاختيارات الأخرى وترك فقط استلام
        Array.from(handoverTypeSelect.options).forEach(option => {
            if (option.value !== 'return') {
                option.style.display = 'none';
            }
        });
        
        // إضافة لون مميز لخيار الاستلام
        handoverTypeSelect.style.backgroundColor = '#fff3cd';
        handoverTypeSelect.style.border = '2px solid #ffc107';
    }
    
    // ملء بيانات السائق
    if (driverInfo.name) {
        const personNameInput = document.getElementById('person_name');
        if (personNameInput) {
            personNameInput.value = driverInfo.name;
            personNameInput.style.backgroundColor = '#d1ecf1';
        }
    }
    
    if (driverInfo.phone) {
        const personPhoneInput = document.getElementById('person_phone');
        if (personPhoneInput) {
            personPhoneInput.value = driverInfo.phone;
            personPhoneInput.style.backgroundColor = '#d1ecf1';
        }
    }
    
    if (driverInfo.national_id) {
        const personNationalIdInput = document.getElementById('person_national_id');
        if (personNationalIdInput) {
            personNationalIdInput.value = driverInfo.national_id;
            personNationalIdInput.style.backgroundColor = '#d1ecf1';
        }
    }
    
    if (driverInfo.employee_id) {
        const employeeIdInput = document.getElementById('employee_id');
        if (employeeIdInput) {
            employeeIdInput.value = driverInfo.employee_id;
            employeeIdInput.style.backgroundColor = '#d1ecf1';
        }
    }
    
    // تعبئة التاريخ والوقت الحاليين
    const now = new Date();
    const today = now.toISOString().split('T')[0];
    const currentTime = now.toTimeString().split(' ')[0].substring(0,5);
    
    const handoverDateInput = document.getElementById('handover_date');
    if (handoverDateInput) {
        handoverDateInput.value = today;
        handoverDateInput.style.backgroundColor = '#d4edda';
    }
    
    const handoverTimeInput = document.getElementById('handover_time');
    if (handoverTimeInput) {
        handoverTimeInput.value = currentTime;
        handoverTimeInput.style.backgroundColor = '#d4edda';
    }
    
    // إضافة ملاحظة في حقل الملاحظات
    const notesInput = document.getElementById('notes');
    if (notesInput) {
        notesInput.value = `استلام سريع من السائق الحالي: ${driverInfo.name} - ${driverInfo.phone}`;
        notesInput.style.backgroundColor = '#f8f9fa';
    }
    
    // إضافة رسالة نجاح
    showSuccessMessage('تم ملء النموذج ببيانات السائق الحالي. يرجى مراجعة البيانات واستكمال النموذج.');
    
    console.log('تم ملء النموذج بنجاح');
}

function showSuccessMessage(message) {
    // إنشاء رسالة نجاح مؤقتة
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-success alert-dismissible fade show mt-3';
    alertDiv.innerHTML = `
        <i class="fas fa-check-circle"></i>
        <strong>تم بنجاح:</strong> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // إضافة الرسالة أعلى النموذج
    const form = document.querySelector('form[method="post"]');
    if (form) {
        form.insertBefore(alertDiv, form.firstChild);
        
        // إزالة الرسالة تلقائياً بعد 5 ثواني
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }
}