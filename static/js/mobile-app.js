// تطبيق نُظم المحمول - JavaScript الرئيسي
(function() {
    'use strict';
    
    // متغيرات عامة
    window.mobileApp = window.mobileApp || {};
    
    // تحديث الوقت في شريط الحالة
    function updateTime() {
        const now = new Date();
        const timeString = now.toLocaleTimeString('ar-SA', { 
            hour: '2-digit', 
            minute: '2-digit',
            hour12: false 
        });
        const timeElement = document.querySelector('.status-time');
        if (timeElement) {
            timeElement.textContent = timeString;
        }
    }

    // التنقل إلى صفحة جديدة
    window.navigateTo = function(url) {
        console.log('Navigating to:', url);
        closeSidebar();
        
        // إضافة تأثير بصري للعنصر المنقور عليه
        try {
            if (window.event) {
                const clickedElement = window.event.target.closest('.nav-item') || window.event.target.closest('.menu-item');
                if (clickedElement) {
                    clickedElement.style.transform = 'scale(0.95)';
                    setTimeout(() => {
                        clickedElement.style.transform = 'scale(1)';
                    }, 150);
                }
            }
        } catch(e) {
            console.log('Visual effect error:', e.message);
        }
        
        // التنقل بعد تأخير بسيط
        setTimeout(() => {
            window.location.href = url;
        }, 200);
    };

    // إغلاق القائمة الجانبية
    window.closeSidebar = function() {
        const sidebar = document.getElementById('sidebar');
        const sidebarOverlay = document.getElementById('sidebar-overlay');
        if (sidebar && sidebarOverlay) {
            sidebar.classList.remove('active');
            sidebarOverlay.classList.remove('active');
            document.body.style.overflow = 'auto';
        }
    };

    // البحث
    window.toggleSearch = function() {
        console.log('Search toggle (mobile version)');
        const searchInput = document.querySelector('#search-input') || 
                           document.querySelector('input[type="search"]') || 
                           document.querySelector('input[name="search"]');
        if (searchInput) {
            searchInput.focus();
            searchInput.style.backgroundColor = '#f0f4ff';
            setTimeout(() => {
                searchInput.style.backgroundColor = '';
            }, 500);
        }
    };

    // تسجيل الخروج
    window.logout = function() {
        if (confirm('هل أنت متأكد من تسجيل الخروج؟')) {
            window.location.href = '/mobile/logout';
        }
    };

    // تحديد الصفحة النشطة
    function setActivePage() {
        const currentPath = window.location.pathname;
        console.log('Current path:', currentPath);
        
        // تحديد عنصر القائمة النشط
        const navItems = document.querySelectorAll('.nav-item');
        navItems.forEach(item => {
            item.classList.remove('active');
            const navType = item.getAttribute('data-nav');
            
            if (navType && currentPath.includes(navType)) {
                item.classList.add('active');
                console.log('Active page set:', navType);
            }
        });
        
        // تحديد عنصر القائمة الجانبية النشط
        const sidebarItems = document.querySelectorAll('.menu-item');
        sidebarItems.forEach(item => {
            const href = item.getAttribute('onclick') || item.getAttribute('href');
            if (href && currentPath.includes(href.replace(/['"()navigateTo]/g, ''))) {
                item.classList.add('active');
            }
        });
    }

    // تهيئة مستمعات الأحداث
    function initializeEventListeners() {
        const menuToggle = document.getElementById('menu-toggle');
        const sidebar = document.getElementById('sidebar');
        const sidebarOverlay = document.getElementById('sidebar-overlay');
        
        if (menuToggle && sidebar && sidebarOverlay) {
            // فتح القائمة الجانبية
            menuToggle.addEventListener('click', function() {
                sidebar.classList.add('active');
                sidebarOverlay.classList.add('active');
                document.body.style.overflow = 'hidden';
            });
            
            // إغلاق القائمة الجانبية عند النقر على الخلفية
            sidebarOverlay.addEventListener('click', function() {
                window.closeSidebar();
            });
        }
        
        // تهيئة أيقونات الرأس
        document.querySelectorAll('.header-icon').forEach(icon => {
            if (icon.id !== 'menu-toggle') {
                icon.addEventListener('click', function() {
                    this.style.transform = 'scale(0.9)';
                    setTimeout(() => {
                        this.style.transform = 'scale(1)';
                    }, 150);
                });
            }
        });
    }

    // تهيئة التطبيق عند تحميل الصفحة
    document.addEventListener('DOMContentLoaded', function() {
        console.log('Mobile App: DOM loaded, initializing...');
        
        try {
            // تحديث الوقت
            updateTime();
            setInterval(updateTime, 60000);
            
            // تهيئة الأحداث
            initializeEventListeners();
            setActivePage();
            
            console.log('Mobile App: Initialized successfully');
            console.log('Available functions:', {
                navigateTo: typeof window.navigateTo,
                toggleSearch: typeof window.toggleSearch,
                logout: typeof window.logout,
                closeSidebar: typeof window.closeSidebar
            });
            
        } catch (error) {
            console.error('Mobile App: Error during initialization:', error);
        }
    });

    // معالج الأخطاء العام
    window.addEventListener('error', function(e) {
        console.log('Mobile App: JavaScript Error handled:', e.message);
        e.preventDefault();
        return true;
    });

})();

// دوال عامة للتوافق مع الكود الحالي
function navigateTo(url) { window.navigateTo(url); }
function closeSidebar() { window.closeSidebar(); }
function toggleSearch() { window.toggleSearch(); }
function logout() { window.logout(); }

// دالة تهيئة الرسوم البيانية (للتوافق)
function initializeDepartmentCharts() {
    console.log('Department charts initialized (mobile fallback)');
}