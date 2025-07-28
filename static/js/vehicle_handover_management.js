/**
 * إدارة سجلات التسليم والاستلام - نظام الحذف المتعدد
 */

document.addEventListener("DOMContentLoaded", function () {
    console.log("تحميل نظام إدارة سجلات التسليم والاستلام");
    
    // انتظار قليل للتأكد من تحميل جميع العناصر
    setTimeout(initializeHandoverManagement, 500);
});

function initializeHandoverManagement() {
    // البحث عن العناصر المطلوبة
    const selectAllCheckbox = document.getElementById("select-all");
    const handoverCheckboxes = document.querySelectorAll(".handover-checkbox");
    const deleteSelectedBtn = document.getElementById("delete-selected-btn");
    const handoverDeleteForm = document.getElementById("handover-delete-form");

    console.log("عناصر نظام التسليم والاستلام:", {
        selectAllCheckbox: !!selectAllCheckbox,
        handoverCheckboxes: handoverCheckboxes.length,
        deleteSelectedBtn: !!deleteSelectedBtn,
        handoverDeleteForm: !!handoverDeleteForm
    });

    // التحقق من وجود العناصر الأساسية
    if (!selectAllCheckbox || handoverCheckboxes.length === 0 || !deleteSelectedBtn) {
        console.warn("بعض عناصر نظام التسليم والاستلام غير موجودة");
        return;
    }

    // دالة تحديث حالة زر الحذف
    function updateDeleteButtonState() {
        const checkedCount = document.querySelectorAll(".handover-checkbox:checked").length;
        
        // تفعيل/تعطيل الزر بناءً على التحديد
        deleteSelectedBtn.disabled = checkedCount === 0;
        
        // تحديث نص الزر
        if (checkedCount > 0) {
            deleteSelectedBtn.innerHTML = `<i class="fas fa-trash-alt ms-1"></i> حذف المحدد (${checkedCount})`;
            deleteSelectedBtn.classList.remove("btn-secondary");
            deleteSelectedBtn.classList.add("btn-danger");
        } else {
            deleteSelectedBtn.innerHTML = `<i class="fas fa-trash-alt ms-1"></i> حذف المحدد`;
            deleteSelectedBtn.classList.remove("btn-danger");
            deleteSelectedBtn.classList.add("btn-secondary");
        }
        
        console.log(`تم تحديث زر الحذف: ${checkedCount} عنصر محدد`);
    }

    // إعداد خانة "تحديد الكل"
    selectAllCheckbox.addEventListener("change", function () {
        const isChecked = this.checked;
        
        handoverCheckboxes.forEach((checkbox) => {
            checkbox.checked = isChecked;
        });
        
        updateDeleteButtonState();
        console.log(`تم ${isChecked ? 'تحديد' : 'إلغاء تحديد'} جميع السجلات`);
    });

    // إعداد خانات التحديد الفردية
    handoverCheckboxes.forEach((checkbox, index) => {
        checkbox.addEventListener("change", function () {
            // تحديث حالة خانة "تحديد الكل"
            const checkedCount = document.querySelectorAll(".handover-checkbox:checked").length;
            const allChecked = checkedCount === handoverCheckboxes.length;
            
            selectAllCheckbox.checked = allChecked;
            selectAllCheckbox.indeterminate = checkedCount > 0 && !allChecked;
            
            // تحديث زر الحذف
            updateDeleteButtonState();
        });
    });

    // إعداد نموذج الحذف
    if (handoverDeleteForm) {
        handoverDeleteForm.addEventListener("submit", function (e) {
            const checkedBoxes = document.querySelectorAll(".handover-checkbox:checked");
            
            if (checkedBoxes.length === 0) {
                e.preventDefault();
                alert("يرجى تحديد السجلات المراد حذفها");
                return false;
            }

            // رسالة تأكيد
            const confirmMessage = `هل أنت متأكد من حذف ${checkedBoxes.length} سجل من سجلات التسليم والاستلام؟\n\nسيتم توجيهك لصفحة التأكيد النهائية.`;
            
            if (!confirm(confirmMessage)) {
                e.preventDefault();
                return false;
            }
            
            console.log(`تم إرسال طلب حذف ${checkedBoxes.length} سجل`);
        });
    }

    // تحديث الحالة الأولية
    updateDeleteButtonState();
    
    console.log("تم تهيئة نظام إدارة التسليم والاستلام بنجاح");
}

// دالة إضافية لإعادة تهيئة النظام عند الحاجة
window.reinitializeHandoverManagement = initializeHandoverManagement;