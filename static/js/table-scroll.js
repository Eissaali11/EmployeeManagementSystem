/**
 * أدوات مساعدة للجداول ذات التمرير الأفقي
 * تساعد في تحسين تجربة المستخدم عند التعامل مع جداول البيانات الكبيرة
 */

document.addEventListener('DOMContentLoaded', function() {
    // إضافة مؤشرات التمرير إلى جميع الجداول ذات الفئة table-horizontal-scroll
    initHorizontalScrollIndicators();
    
    // إضافة وظيفة السحب للجداول
    initDraggableScroll();
    
    // إضافة الفئات لتحسين عرض أعمدة الجدول
    enhanceTableColumns();
});

/**
 * إضافة مؤشرات التمرير إلى الجداول للإشارة إلى إمكانية التمرير أفقيًا
 */
function initHorizontalScrollIndicators() {
    const scrollContainers = document.querySelectorAll('.table-horizontal-scroll');
    
    scrollContainers.forEach(container => {
        // إضافة فئة للإشارة إلى وجود تمرير أفقي
        container.classList.add('has-horizontal-scroll');
        
        // إنشاء مؤشر التمرير
        const scrollIndicator = document.createElement('div');
        scrollIndicator.className = 'scroll-indicator';
        scrollIndicator.innerHTML = '<i class="fas fa-arrows-alt-h"></i>';
        
        // إضافة المؤشر إلى الحاوية
        container.appendChild(scrollIndicator);
        
        // إخفاء المؤشر عند التمرير
        container.addEventListener('scroll', function() {
            scrollIndicator.style.opacity = '0';
            setTimeout(() => {
                if (container.scrollLeft < 10) {
                    scrollIndicator.style.opacity = '1';
                }
            }, 1000);
        });
        
        // التحقق من الحاجة للتمرير
        setTimeout(() => {
            if (container.scrollWidth <= container.clientWidth) {
                scrollIndicator.style.display = 'none';
            }
        }, 500);
    });
}

/**
 * تمكين خاصية السحب للتمرير في الجداول
 */
function initDraggableScroll() {
    const scrollContainers = document.querySelectorAll('.table-horizontal-scroll');
    
    scrollContainers.forEach(container => {
        let isDown = false;
        let startX;
        let scrollLeft;
        
        container.addEventListener('mousedown', (e) => {
            isDown = true;
            container.style.cursor = 'grabbing';
            startX = e.pageX - container.offsetLeft;
            scrollLeft = container.scrollLeft;
        });
        
        container.addEventListener('mouseleave', () => {
            isDown = false;
            container.style.cursor = 'grab';
        });
        
        container.addEventListener('mouseup', () => {
            isDown = false;
            container.style.cursor = 'grab';
        });
        
        container.addEventListener('mousemove', (e) => {
            if (!isDown) return;
            e.preventDefault();
            const x = e.pageX - container.offsetLeft;
            const walk = (x - startX) * 1.5; // سرعة التمرير
            container.scrollLeft = scrollLeft - walk;
        });
        
        // دعم الأجهزة اللمسية
        container.addEventListener('touchstart', (e) => {
            isDown = true;
            startX = e.touches[0].pageX - container.offsetLeft;
            scrollLeft = container.scrollLeft;
        }, { passive: true });
        
        container.addEventListener('touchend', () => {
            isDown = false;
        }, { passive: true });
        
        container.addEventListener('touchmove', (e) => {
            if (!isDown) return;
            const x = e.touches[0].pageX - container.offsetLeft;
            const walk = (x - startX) * 1.5;
            container.scrollLeft = scrollLeft - walk;
        }, { passive: true });
    });
}

/**
 * تحسين أعمدة الجدول بإضافة فئات خاصة لتحسين طريقة العرض
 */
function enhanceTableColumns() {
    const tables = document.querySelectorAll('.table-horizontal-scroll table');
    
    tables.forEach(table => {
        // العثور على فهارس الأعمدة المهمة
        const headerCells = table.querySelectorAll('thead th');
        const nameIndex = findColumnIndex(headerCells, ['الاسم', 'name']);
        const idIndex = findColumnIndex(headerCells, ['الرقم الوظيفي', 'employee_id', 'employee id', 'id']);
        const actionsIndex = findColumnIndex(headerCells, ['الإجراءات', 'actions']);
        
        // إضافة فئات للعناوين
        if (nameIndex !== -1) {
            headerCells[nameIndex].classList.add('th-name');
        }
        
        if (idIndex !== -1) {
            headerCells[idIndex].classList.add('th-id');
        }
        
        if (actionsIndex !== -1) {
            headerCells[actionsIndex].classList.add('th-actions');
        }
        
        // إضافة فئات للخلايا
        const rows = table.querySelectorAll('tbody tr');
        rows.forEach(row => {
            const cells = row.querySelectorAll('td');
            
            if (nameIndex !== -1 && cells.length > nameIndex) {
                cells[nameIndex].classList.add('td-name');
            }
            
            if (idIndex !== -1 && cells.length > idIndex) {
                cells[idIndex].classList.add('td-id');
            }
            
            if (actionsIndex !== -1 && cells.length > actionsIndex) {
                cells[actionsIndex].classList.add('td-actions');
            }
        });
    });
}

/**
 * البحث عن فهرس العمود بناءً على محتوى النص
 */
function findColumnIndex(headerCells, possibleNames) {
    for (let i = 0; i < headerCells.length; i++) {
        const cellText = headerCells[i].textContent.trim().toLowerCase();
        for (let name of possibleNames) {
            if (cellText.includes(name.toLowerCase())) {
                return i;
            }
        }
    }
    return -1;
}

/**
 * التحقق من عرض محتوى الجدول وضبط الحد الأدنى للعرض إذا لزم الأمر
 */
window.adjustTableWidth = function() {
    const tables = document.querySelectorAll('.table-horizontal-scroll table');
    
    tables.forEach(table => {
        const container = table.closest('.table-horizontal-scroll');
        const tableWidth = table.scrollWidth;
        const containerWidth = container.clientWidth;
        
        if (tableWidth < containerWidth) {
            // إذا كان الجدول أصغر من الحاوية، نضبط الحد الأدنى للعرض
            table.style.minWidth = '100%';
        } else {
            // ضمان أن الجدول يملأ العرض المطلوب للسماح بالتمرير
            if (table.offsetWidth < tableWidth) {
                table.style.minWidth = tableWidth + 'px';
            }
        }
    });
};

// الاستدعاء مبدئيًا وعند تغيير حجم النافذة
window.addEventListener('load', window.adjustTableWidth);
window.addEventListener('resize', window.adjustTableWidth);