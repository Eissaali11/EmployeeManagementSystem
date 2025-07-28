/**
 * JavaScript لتعبئة حقل رقم الوثيقة تلقائياً بالهوية الوطنية عند اختيار الموظف
 * في صفحة إنشاء الوثائق الجديدة
 */

$(document).ready(function() {
    // التعبئة التلقائية لرقم الهوية الوطنية عند اختيار الموظف
    function setupAutoFillNationalId() {
        console.log('تم تهيئة نظام التعبئة التلقائية لرقم الهوية الوطنية');
        
        // إزالة أي event handlers سابقة
        $('#employee_id').off('change.autofill');
        
        // ربط event handler جديد
        $('#employee_id').on('change.autofill', function() {
            const selectedOption = $(this).find('option:selected');
            const nationalId = selectedOption.data('national-id');
            const documentNumberField = $('#document_number');
            const employeeName = selectedOption.text();
            
            console.log('تم اختيار موظف:', employeeName, 'رقم الهوية:', nationalId);
            
            if (selectedOption.val() && nationalId) {
                // تعبئة حقل رقم الوثيقة برقم الهوية الوطنية
                documentNumberField.val(nationalId);
                
                // إظهار رسالة تأكيد
                showAutoFillNotification('تم تعبئة رقم الهوية تلقائياً: ' + nationalId, 'success');
                
                console.log('تم تعبئة رقم الهوية تلقائياً:', nationalId);
            } else if (selectedOption.val() && !nationalId) {
                // مسح الحقل وإظهار تحذير
                documentNumberField.val('');
                showAutoFillNotification('لا يوجد رقم هوية وطنية مسجل لهذا الموظف: ' + employeeName, 'warning');
            } else {
                // مسح الحقل إذا لم يتم اختيار موظف
                documentNumberField.val('');
                $('.auto-fill-notification').remove();
            }
        });
        
        // ربط مع select2 أيضاً في حال كان مفعلاً
        $('#employee_id').on('select2:select.autofill', function (e) {
            setTimeout(function() {
                $('#employee_id').trigger('change.autofill');
            }, 100);
        });
    }
    
    // دالة لإظهار رسائل التعبئة التلقائية
    function showAutoFillNotification(message, type = 'success') {
        // إزالة أي رسائل سابقة
        $('.auto-fill-notification').remove();
        
        const alertClass = type === 'warning' ? 'alert-warning' : 'alert-success';
        const iconClass = type === 'warning' ? 'fa-exclamation-triangle' : 'fa-magic';
        
        const notification = $(`
            <div class="alert ${alertClass} alert-dismissible fade show mt-2 auto-fill-notification" role="alert" style="font-size: 14px; border-radius: 8px;">
                <i class="fas ${iconClass} me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="إغلاق"></button>
            </div>
        `);
        
        // إضافة الرسالة بعد حقل رقم الوثيقة
        if ($('#document_number_container').length > 0) {
            $('#document_number_container').append(notification);
        } else {
            // بديل في حال عدم وجود الحاوية
            $('#document_number').after(notification);
        }
        
        // إزالة الرسالة تلقائياً بعد 5 ثوان
        setTimeout(function() {
            notification.fadeOut(500, function() {
                $(this).remove();
            });
        }, 5000);
    }
    
    // تطبيق التعبئة التلقائية عند تحميل الصفحة
    setupAutoFillNationalId();
    
    // إعادة ربط التعبئة التلقائية بعد إعادة بناء قائمة الموظفين (عند الفلترة)
    $(document).on('change', '#filter_department', function() {
        console.log('تم تغيير فلتر القسم، إعادة تهيئة التعبئة التلقائية');
        // الانتظار حتى تكتمل إعادة بناء القائمة
        setTimeout(function() {
            setupAutoFillNationalId();
        }, 500);
    });
    
    // إعادة تطبيق عند إعادة تهيئة select2
    $(document).on('select2:ready', '#employee_id', function() {
        console.log('تم إعادة تهيئة select2، إعادة ربط التعبئة التلقائية');
        setupAutoFillNationalId();
    });
    
    console.log('تم تحميل ملف التعبئة التلقائية بنجاح');
});