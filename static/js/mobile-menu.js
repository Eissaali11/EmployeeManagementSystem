/**
 * JavaScript للتحكم في القائمة الجانبية على الجوال
 * Mobile Sidebar Menu Controller
 */

document.addEventListener('DOMContentLoaded', function() {
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const sidebar = document.querySelector('.sidebar');
    const overlay = document.getElementById('sidebarOverlay');
    
    // التحقق من وجود العناصر المطلوبة
    if (!mobileMenuBtn || !sidebar || !overlay) {
        console.log('بعض عناصر القائمة الجانبية غير موجودة');
        return;
    }
    
    console.log('تم تحميل نظام التحكم في القائمة الجانبية للجوال');
    
    /**
     * فتح القائمة الجانبية
     */
    function openSidebar() {
        sidebar.classList.add('show');
        overlay.classList.add('show');
        document.body.style.overflow = 'hidden'; // منع التمرير
        mobileMenuBtn.setAttribute('aria-expanded', 'true');
    }
    
    /**
     * إغلاق القائمة الجانبية
     */
    function closeSidebar() {
        sidebar.classList.remove('show');
        overlay.classList.remove('show');
        document.body.style.overflow = 'auto'; // السماح بالتمرير مرة أخرى
        mobileMenuBtn.setAttribute('aria-expanded', 'false');
    }
    
    /**
     * تبديل حالة القائمة الجانبية
     */
    function toggleSidebar() {
        if (sidebar.classList.contains('show')) {
            closeSidebar();
        } else {
            openSidebar();
        }
    }
    
    // ربط الأحداث
    
    // فتح/إغلاق القائمة عند الضغط على زر القائمة
    mobileMenuBtn.addEventListener('click', toggleSidebar);
    
    // إغلاق القائمة عند الضغط على الـ overlay
    overlay.addEventListener('click', closeSidebar);
    
    // إغلاق القائمة عند تغيير حجم الشاشة إلى كبير
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            closeSidebar();
        }
    });
    
    // إغلاق القائمة عند الضغط على أي رابط في القائمة (للجوال فقط)
    const sidebarLinks = sidebar.querySelectorAll('a');
    sidebarLinks.forEach(link => {
        link.addEventListener('click', function() {
            // تأخير بسيط للسماح للصفحة بالتحميل
            setTimeout(() => {
                if (window.innerWidth <= 768) {
                    closeSidebar();
                }
            }, 100);
        });
    });
    
    // إغلاق القائمة عند الضغط على مفتاح Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && sidebar.classList.contains('show')) {
            closeSidebar();
        }
    });
    
    // منع انتشار النقر داخل القائمة الجانبية
    sidebar.addEventListener('click', function(e) {
        e.stopPropagation();
    });
    
    // إضافة accessibility attributes
    mobileMenuBtn.setAttribute('aria-label', 'فتح القائمة الجانبية');
    mobileMenuBtn.setAttribute('aria-expanded', 'false');
    overlay.setAttribute('aria-hidden', 'true');
});