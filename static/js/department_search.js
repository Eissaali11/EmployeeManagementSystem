/**
 * وظائف البحث المتقدم في القسم
 * هذا الملف يحتوي على وظائف لتنفيذ البحث في قائمة الموظفين داخل القسم
 */

$(document).ready(function() {
    // عناصر البحث
    const searchInput = $('#employeeSearch');
    const searchButton = $('#searchButton');
    const employeeRows = $('tr[data-employee-id]');
    const employeeCount = $('#employeeCount');
    const searchResults = $('#searchResultsInfo');
    
    // وظيفة البحث الرئيسية
    function performSearch() {
        const searchTerm = searchInput.val().trim().toLowerCase();
        let foundCount = 0;
        
        // إعادة تعيين التنسيقات السابقة
        employeeRows.removeClass('search-highlight');
        employeeRows.find('.text-primary, .fw-bold').each(function() {
            if (!$(this).hasClass('original-primary')) {
                $(this).removeClass('text-primary fw-bold');
            }
        });
        
        // إذا كان البحث فارغًا، أظهر جميع الصفوف
        if (searchTerm === '') {
            employeeRows.show();
            searchResults.hide();
            return;
        }
        
        // البحث في كل صف
        employeeRows.each(function() {
            const row = $(this);
            
            // استخراج بيانات الموظف
            const employeeName = row.find('h6').text().toLowerCase();
            const employeeId = row.find('.badge.bg-secondary').text().toLowerCase();
            const jobTitle = row.find('p.mb-0').text().toLowerCase();
            const status = row.find('button[data-bs-toggle="dropdown"]').text().toLowerCase();
            const hireDate = row.find('td:nth-child(4)').text().toLowerCase();
            
            // جمع كل البيانات للبحث الشامل
            const allText = employeeName + ' ' + employeeId + ' ' + jobTitle + ' ' + status + ' ' + hireDate;
            
            // البحث عن الكلمات المنفصلة
            const searchWords = searchTerm.split(/\s+/).filter(word => word.length > 0);
            const matchesAllWords = searchWords.every(word => allText.includes(word));
            
            if (matchesAllWords) {
                row.show();
                row.addClass('search-highlight');
                
                // تمييز النص المطابق
                highlightMatches(row, searchWords);
                
                foundCount++;
            } else {
                row.hide();
            }
        });
        
        // عرض نتائج البحث
        searchResults.show();
        
        // تحديث عدد النتائج
        if (employeeCount.length) {
            employeeCount.text(foundCount);
        }
        
        // عرض رسالة بالنتائج
        if (foundCount > 0) {
            showAlert('تم العثور على ' + foundCount + ' موظف يطابق "' + searchTerm + '"', 'success');
        } else {
            showAlert('لا توجد نتائج مطابقة للبحث عن "' + searchTerm + '"', 'warning');
        }
    }
    
    // تمييز النص المطابق
    function highlightMatches(row, searchWords) {
        const elements = row.find('h6, p, span.badge, td');
        
        elements.each(function() {
            const el = $(this);
            const text = el.text().toLowerCase();
            
            // التحقق من وجود أي من كلمات البحث
            for (const word of searchWords) {
                if (word && text.includes(word)) {
                    el.addClass('text-primary fw-bold');
                    break;
                }
            }
        });
    }
    
    // عرض تنبيه
    function showAlert(message, type) {
        // إزالة التنبيهات السابقة
        $('#searchAlert').remove();
        
        // إنشاء تنبيه جديد
        const alertHtml = `
            <div id="searchAlert" class="alert alert-${type} alert-dismissible fade show mb-3" role="alert">
                <i class="${type === 'success' ? 'fas fa-check-circle' : 'fas fa-exclamation-triangle'} me-2"></i>
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="إغلاق"></button>
            </div>
        `;
        
        // إضافة التنبيه إلى الصفحة
        searchResults.before(alertHtml);
        
        // إخفاء التنبيه تلقائيًا بعد 5 ثوانٍ
        setTimeout(function() {
            $('#searchAlert').fadeOut(500, function() {
                $(this).remove();
            });
        }, 5000);
    }
    
    // ربط وظيفة البحث بحدث النقر على زر البحث
    searchButton.on('click', function() {
        performSearch();
    });
    
    // ربط وظيفة البحث بحدث الضغط على Enter
    searchInput.on('keypress', function(e) {
        if (e.which === 13) { // رمز مفتاح Enter
            e.preventDefault();
            performSearch();
        }
    });
    
    // بحث تلقائي عند الكتابة
    searchInput.on('input', function() {
        // بحث تلقائي فقط إذا كان طول النص 3 أحرف أو أكثر، أو إذا كان فارغًا
        if ($(this).val().length >= 3 || $(this).val().length === 0) {
            performSearch();
        }
    });
});