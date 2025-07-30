/**
 * نصوص JavaScript لصفحة إنشاء الوثائق
 */

$(document).ready(function() {
    // التحقق من توفر jQuery و Select2
    if (typeof $ === 'undefined' || !$.fn.select2) {
        console.error('jQuery أو Select2 غير متوفر');
        return;
    }

    // تهيئة Select2 لحقل اختيار الموظف
    if ($('#employee_id').length) {
        $('#employee_id').select2({
            theme: 'bootstrap-5',
            placeholder: 'ابحث واختر الموظف...',
            allowClear: true,
            dir: 'rtl',
            language: 'ar',
            width: '100%',
            templateResult: function(option) {
                if (!option.id) return option.text;
                
                var $option = $(option.element);
                var deptNames = $option.data('department-names') || '';
                var employeeId = $option.data('employee-id') || '';
                var nationalId = $option.data('national-id') || '';
                
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
            templateSelection: function(option) {
                return option.text;
            },
            matcher: function(params, data) {
                if ($.trim(params.term) === '') {
                    return data;
                }
                
                var term = params.term.toLowerCase();
                var text = data.text.toLowerCase();
                
                if (text.indexOf(term) > -1) {
                    return data;
                }
                
                var $option = $(data.element);
                var employeeId = ($option.data('employee-id') || '').toString().toLowerCase();
                if (employeeId.indexOf(term) > -1) {
                    return data;
                }
                
                var deptNames = ($option.data('department-names') || '').toString().toLowerCase();
                if (deptNames.indexOf(term) > -1) {
                    return data;
                }
                
                var nationalId = ($option.data('national-id') || '').toString().toLowerCase();
                if (nationalId.indexOf(term) > -1) {
                    return data;
                }
                
                return null;
            }
        });
        
        console.log('✅ تم تهيئة Select2 لحقل الموظف');
    }

    // تهيئة باقي Select2 elements
    $('#filter_department, #department_id, #document_type').select2({
        theme: 'bootstrap-5',
        allowClear: true,
        dir: 'rtl',
        language: 'ar',
        width: '100%'
    });

    // إضافة CSS مخصص
    $('<style>').prop('type', 'text/css').html(`
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
    `).appendTo('head');
});