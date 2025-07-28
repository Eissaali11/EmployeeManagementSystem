/**
 * تهيئة وتحسين Select2 لحقل اختيار الموظفين
 * مع دعم البحث المتقدم وعرض المعلومات التفصيلية
 */

$(document).ready(function() {
    // تهيئة Select2 لحقل اختيار الموظف مع تحسينات متقدمة
    $('#employee_id').select2({
        theme: 'bootstrap-5',
        placeholder: 'ابحث واختر الموظف...',
        allowClear: true,
        dir: 'rtl',
        language: 'ar',
        width: '100%',
        minimumInputLength: 0,
        maximumSelectionLength: 1,
        tags: false,
        dropdownAutoWidth: true,
        
        // تخصيص عرض النتائج في القائمة المنسدلة
        templateResult: function(option) {
            if (!option.id) return option.text;
            
            // استخراج البيانات من data attributes
            var $option = $(option.element);
            var deptNames = $option.data('department-names') || '';
            var employeeId = $option.data('employee-id') || '';
            var nationalId = $option.data('national-id') || '';
            
            // إنشاء HTML مخصص لعرض معلومات الموظف
            var employeeName = option.text.split(' (')[0];
            var html = '<div class="select2-employee-option p-2">' +
                '<div class="fw-bold text-primary mb-1">' + employeeName + '</div>' +
                '<div class="d-flex flex-wrap gap-2">';
                
            if (employeeId) {
                html += '<small class="badge bg-secondary">رقم الموظف: ' + employeeId + '</small>';
            }
            
            if (deptNames) {
                html += '<small class="badge bg-info text-dark">القسم: ' + deptNames + '</small>';
            }
            
            if (nationalId) {
                html += '<small class="badge bg-success">رقم الهوية: ' + nationalId + '</small>';
            }
            
            html += '</div></div>';
            
            return $(html);
        },
        
        // تخصيص عرض الخيار المحدد
        templateSelection: function(option) {
            if (!option.id) return option.text;
            return option.text;
        },
        
        // تحسين البحث
        matcher: function(params, data) {
            // إذا لم يتم إدخال نص بحث، اعرض جميع الخيارات
            if ($.trim(params.term) === '') {
                return data;
            }
            
            // تحويل نص البحث لحروف صغيرة للمقارنة
            var term = params.term.toLowerCase();
            var text = data.text.toLowerCase();
            
            // البحث في اسم الموظف
            if (text.indexOf(term) > -1) {
                return data;
            }
            
            // البحث في رقم الموظف
            var $option = $(data.element);
            var employeeId = ($option.data('employee-id') || '').toString().toLowerCase();
            if (employeeId.indexOf(term) > -1) {
                return data;
            }
            
            // البحث في اسم القسم 
            var deptNames = ($option.data('department-names') || '').toString().toLowerCase();
            if (deptNames.indexOf(term) > -1) {
                return data;
            }
            
            // البحث في رقم الهوية الوطنية
            var nationalId = ($option.data('national-id') || '').toString().toLowerCase();
            if (nationalId.indexOf(term) > -1) {
                return data;
            }
            
            // إذا لم يتطابق مع أي من المعايير، لا تعرض الخيار
            return null;
        }
    });
    
    // تهيئة Select2 لفلتر الأقسام
    $('#filter_department').select2({
        theme: 'bootstrap-5',
        placeholder: 'جميع الأقسام',
        allowClear: true,
        dir: 'rtl',
        language: 'ar',
        width: '100%'
    });
    
    // تهيئة Select2 لحقل اختيار القسم (في حالة إضافة لقسم كامل)
    $('#department_id').select2({
        theme: 'bootstrap-5',
        placeholder: 'اختر القسم',
        allowClear: true,
        dir: 'rtl',
        language: 'ar',
        width: '100%'
    });
    
    // تهيئة Select2 لأنواع الوثائق
    $('#document_type').select2({
        theme: 'bootstrap-5',
        placeholder: 'اختر نوع الوثيقة',
        allowClear: true,
        dir: 'rtl',
        language: 'ar',
        width: '100%'
    });
    
    // إضافة CSS مخصص لتحسين مظهر Select2
    $('<style>')
        .prop('type', 'text/css')
        .html(`
            .select2-employee-option {
                border-radius: 5px;
                margin: 2px 0;
            }
            
            .select2-employee-option:hover {
                background-color: var(--bs-primary-bg-subtle) !important;
            }
            
            .select2-container--bootstrap-5 .select2-dropdown {
                border-radius: 8px;
                box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
            }
            
            .select2-container--bootstrap-5 .select2-results__option[data-selected=true] {
                background-color: var(--bs-primary) !important;
                color: white !important;
            }
        `)
        .appendTo('head');
        
    console.log('✅ تم تفعيل Select2 المحسن لحقل اختيار الموظفين بنجاح');
});