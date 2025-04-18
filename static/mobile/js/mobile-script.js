/**
 * الملف الرئيسي للجافاسكربت للنسخة المحمولة
 * يحتوي على كافة الوظائف والتفاعلات للتطبيق
 */

document.addEventListener('DOMContentLoaded', function() {
    // ===============================
    // تهيئة العناصر المتغيرة
    // ===============================
    const sidebar = document.getElementById('mobile-sidebar');
    const sidebarOverlay = document.getElementById('sidebar-overlay');
    const menuBtn = document.querySelector('.mobile-header .fa-bars').parentElement;
    const closeBtn = document.querySelector('.close-sidebar');
    const scrollTopBtn = document.querySelector('.mobile-scroll-top');
    const loader = document.querySelector('.mobile-loader');
    
    // ===============================
    // تهيئة القائمة الجانبية
    // ===============================
    if (menuBtn && sidebar && sidebarOverlay) {
        // فتح القائمة الجانبية
        menuBtn.addEventListener('click', function() {
            sidebar.classList.add('active');
            sidebarOverlay.classList.add('active');
            document.body.style.overflow = 'hidden'; // منع التمرير
        });
        
        // إغلاق القائمة الجانبية
        function closeSidebar() {
            sidebar.classList.remove('active');
            sidebarOverlay.classList.remove('active');
            document.body.style.overflow = ''; // السماح بالتمرير مرة أخرى
        }
        
        // إغلاق عند النقر على زر الإغلاق
        if (closeBtn) {
            closeBtn.addEventListener('click', closeSidebar);
        }
        
        // إغلاق عند النقر على الخلفية الضبابية
        sidebarOverlay.addEventListener('click', closeSidebar);
        
        // إغلاق عند النقر على أي رابط في القائمة
        const sidebarLinks = document.querySelectorAll('.sidebar-menu a');
        sidebarLinks.forEach(link => {
            link.addEventListener('click', function() {
                showLoader(); // إظهار التحميل
                closeSidebar();
            });
        });
    }
    
    // ===============================
    // تهيئة زر العودة للأعلى
    // ===============================
    if (scrollTopBtn) {
        // إظهار/إخفاء زر العودة للأعلى
        window.addEventListener('scroll', function() {
            if (window.scrollY > 300) {
                scrollTopBtn.classList.add('visible');
            } else {
                scrollTopBtn.classList.remove('visible');
            }
        });
        
        // التمرير للأعلى عند النقر
        scrollTopBtn.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
    
    // ===============================
    // تهيئة حقول التاريخ والوقت
    // ===============================
    // تحويل الحقول ذات الخاصية data-hijri إلى حقول تاريخ هجري
    const hijriDateInputs = document.querySelectorAll('[data-hijri]');
    if (hijriDateInputs.length > 0) {
        initializeHijriDatePicker();
    }
    
    // ===============================
    // تأثيرات الأزرار والروابط
    // ===============================
    // إضافة تأثير الضغط على الأزرار
    const buttons = document.querySelectorAll('.mobile-btn, .footer-item, .mobile-menu-button');
    buttons.forEach(button => {
        button.addEventListener('touchstart', function() {
            this.classList.add('pressed');
        });
        
        button.addEventListener('touchend', function() {
            this.classList.remove('pressed');
        });
    });
    
    // تتبع الضغط على روابط القائمة السفلية لتحميل الصفحات
    const footerLinks = document.querySelectorAll('.mobile-footer a');
    footerLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // عدم تنفيذ إذا كان الرابط نشطًا بالفعل
            if (this.classList.contains('active')) {
                e.preventDefault();
                return;
            }
            
            // إظهار شاشة التحميل
            showLoader();
        });
    });
    
    // ===============================
    // دعم PWA
    // ===============================
    // تثبيت التطبيق
    let deferredPrompt;
    const installButton = document.getElementById('install-app');
    
    window.addEventListener('beforeinstallprompt', (e) => {
        // منع ظهور رسالة التثبيت التلقائية للمتصفح
        e.preventDefault();
        // تخزين الحدث للاستخدام لاحقًا
        deferredPrompt = e;
        // إظهار زر التثبيت إذا كان موجودًا
        if (installButton) {
            installButton.style.display = 'block';
            
            installButton.addEventListener('click', async () => {
                // إخفاء زر التثبيت
                installButton.style.display = 'none';
                // إظهار واجهة التثبيت
                deferredPrompt.prompt();
                // انتظار خيار المستخدم
                const { outcome } = await deferredPrompt.userChoice;
                // تفريغ المتغير
                deferredPrompt = null;
            });
        }
    });
    
    // ===============================
    // التحقق من الاتصال بالإنترنت
    // ===============================
    function updateOnlineStatus() {
        const statusElement = document.getElementById('connection-status');
        if (statusElement) {
            if (navigator.onLine) {
                statusElement.textContent = 'متصل';
                statusElement.classList.remove('offline');
                statusElement.classList.add('online');
            } else {
                statusElement.textContent = 'غير متصل';
                statusElement.classList.remove('online');
                statusElement.classList.add('offline');
                
                // إظهار إشعار
                showToast('أنت غير متصل بالإنترنت', 'warning');
            }
        }
    }
    
    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);
    updateOnlineStatus();
    
    // ===============================
    // التأكد من حالة الاتصال بالخادم
    // ===============================
    function checkServerConnection() {
        fetch('/mobile/api/check-connection')
            .then(response => {
                if (!response.ok) {
                    throw new Error('فشل الاتصال بالخادم');
                }
                return response.json();
            })
            .then(data => {
                console.log('متصل بالخادم:', data);
            })
            .catch(error => {
                console.error('خطأ في الاتصال بالخادم:', error);
                showToast('لا يمكن الاتصال بالخادم', 'error');
            });
    }
    
    // التحقق من الاتصال بالخادم كل دقيقة
    setInterval(checkServerConnection, 60000);
    
    // ===============================
    // وظائف مساعدة
    // ===============================
    // إظهار شاشة التحميل
    function showLoader() {
        if (loader) {
            loader.classList.add('active');
            setTimeout(() => {
                loader.classList.remove('active');
            }, 800); // إخفاء بعد 800 مللي ثانية
        }
    }
    
    // إظهار رسالة toast
    function showToast(message, type = 'info') {
        // التحقق من وجود حاوية التوست
        let toastContainer = document.querySelector('.toast-container');
        
        // إنشاء حاوية إذا لم تكن موجودة
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container';
            document.body.appendChild(toastContainer);
        }
        
        // إنشاء عنصر التوست
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        
        // إضافة زر إغلاق
        const closeBtn = document.createElement('button');
        closeBtn.className = 'toast-close';
        closeBtn.innerHTML = '&times;';
        closeBtn.onclick = function() {
            toast.remove();
        };
        
        toast.appendChild(closeBtn);
        toastContainer.appendChild(toast);
        
        // إظهار التوست
        setTimeout(() => {
            toast.classList.add('show');
        }, 10);
        
        // إخفاء التوست تلقائيًا بعد 5 ثواني
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                toast.remove();
            }, 300);
        }, 5000);
    }
    
    // تهيئة منتقي التاريخ الهجري
    function initializeHijriDatePicker() {
        // يتم تنفيذ هذه الوظيفة فقط إذا كانت مكتبة التقويم الهجري متاحة
        if (typeof HijriDatePicker === 'undefined') {
            console.warn('مكتبة التقويم الهجري غير متاحة');
            return;
        }
        
        const hijriDateInputs = document.querySelectorAll('[data-hijri]');
        hijriDateInputs.forEach(input => {
            const options = {
                inputSelector: input,
                showHijriDate: true,
                showGregDate: true,
                selectedDate: input.value || new Date().toISOString().split('T')[0],
                hijriFormat: 'iYYYY/iMM/iDD',
                gregorianFormat: 'YYYY-MM-DD'
            };
            
            new HijriDatePicker(options);
        });
    }
    
    // إخفاء شاشة التحميل الأولية
    hideInitialLoader();
    
    // ===============================
    // إضافة تفاعلات للمكونات المخصصة
    // ===============================
    // مخططات الإحصائيات
    initCharts();
    
    // تفعيل لوحات التبديل (tabs)
    const tabButtons = document.querySelectorAll('.mobile-tabs-btn');
    tabButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const tabId = this.getAttribute('data-tab');
            
            // إزالة التفعيل من جميع الأزرار وإخفاء جميع المحتويات
            document.querySelectorAll('.mobile-tabs-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.mobile-tab-content').forEach(c => c.classList.remove('active'));
            
            // تفعيل الزر والمحتوى المختار
            this.classList.add('active');
            document.getElementById(tabId).classList.add('active');
        });
    });
    
    // تفعيل القوائم المنسدلة
    const dropdownToggles = document.querySelectorAll('.mobile-dropdown-toggle');
    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            const dropdown = this.nextElementSibling;
            
            // إغلاق جميع القوائم المنسدلة المفتوحة الأخرى
            document.querySelectorAll('.mobile-dropdown-menu.show').forEach(menu => {
                if (menu !== dropdown) {
                    menu.classList.remove('show');
                }
            });
            
            // تبديل حالة القائمة المنسدلة الحالية
            dropdown.classList.toggle('show');
        });
    });
    
    // إغلاق القوائم المنسدلة عند النقر خارجها
    document.addEventListener('click', function(e) {
        if (!e.target.matches('.mobile-dropdown-toggle') && !e.target.closest('.mobile-dropdown-menu')) {
            document.querySelectorAll('.mobile-dropdown-menu.show').forEach(menu => {
                menu.classList.remove('show');
            });
        }
    });
});

// إخفاء شاشة التحميل الأولية
function hideInitialLoader() {
    const initialLoader = document.querySelector('.mobile-loader');
    if (initialLoader) {
        initialLoader.classList.remove('active');
    }
}

// تهيئة المخططات
function initCharts() {
    // تنفذ هذه الوظيفة فقط إذا كانت مكتبة Chart.js متاحة وكانت هناك مخططات للتهيئة
    if (typeof Chart === 'undefined' || !document.querySelector('[data-chart]')) {
        return;
    }
    
    // تهيئة المخططات
    const chartElements = document.querySelectorAll('[data-chart]');
    chartElements.forEach(element => {
        const chartType = element.getAttribute('data-chart');
        const chartData = JSON.parse(element.getAttribute('data-chart-data') || '{}');
        const chartOptions = JSON.parse(element.getAttribute('data-chart-options') || '{}');
        
        new Chart(element, {
            type: chartType,
            data: chartData,
            options: chartOptions
        });
    });
}

// وظيفة لتسجيل Service Worker
function registerServiceWorker() {
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/static/mobile/sw.js')
            .then(registration => {
                console.log('Service Worker registered with scope:', registration.scope);
            })
            .catch(error => {
                console.error('Service Worker registration failed:', error);
            });
    }
}

// تسجيل Service Worker عند تحميل الصفحة
window.addEventListener('load', () => {
    registerServiceWorker();
});