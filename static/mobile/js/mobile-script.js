/**
 * سكربت جافاسكربت خاص بالواجهة المحمولة
 * نظام إدارة الموظفين - النسخة المحمولة
 */

// تهيئة التطبيق عند تحميل الصفحة
document.addEventListener('DOMContentLoaded', function() {
    initMobileApp();
});

/**
 * تهيئة التطبيق المحمول
 */
function initMobileApp() {
    // تهيئة القائمة الجانبية
    initSidebar();
    
    // تهيئة الأحداث والتفاعلات
    setupEventListeners();
    
    // تسجيل Service Worker للـ PWA
    registerServiceWorker();
}

/**
 * تهيئة القائمة الجانبية
 */
function initSidebar() {
    // زر فتح القائمة الجانبية
    const menuButton = document.querySelector('.mobile-menu-button');
    // زر إغلاق القائمة الجانبية
    const closeButton = document.querySelector('.close-sidebar');
    // العنصر الرئيسي للقائمة الجانبية
    const sidebar = document.querySelector('.mobile-sidebar');
    // خلفية قاتمة للإغلاق
    const overlay = document.getElementById('sidebar-overlay');
    
    if (menuButton) {
        menuButton.addEventListener('click', function() {
            sidebar.classList.add('active');
            if (overlay) overlay.classList.add('active');
            document.body.style.overflow = 'hidden'; // منع التمرير في الخلفية
        });
    }
    
    if (closeButton) {
        closeButton.addEventListener('click', closeSidebar);
    }
    
    if (overlay) {
        overlay.addEventListener('click', closeSidebar);
    }
    
    // إغلاق القائمة الجانبية عند النقر على أي رابط فيها
    const sidebarLinks = document.querySelectorAll('.sidebar-menu a');
    sidebarLinks.forEach(link => {
        link.addEventListener('click', closeSidebar);
    });
    
    /**
     * إغلاق القائمة الجانبية
     */
    function closeSidebar() {
        sidebar.classList.remove('active');
        if (overlay) overlay.classList.remove('active');
        document.body.style.overflow = ''; // إعادة تمكين التمرير
    }
}

/**
 * تهيئة مستمعي الأحداث
 */
function setupEventListeners() {
    // مستمعي أحداث النماذج
    setupFormValidation();
    
    // مستمعي أحداث للتبديل بين علامات التبويب (إذا وجدت)
    setupTabSwitching();
    
    // إعداد زر العودة للأعلى (إذا وجد)
    setupScrollToTop();
}

/**
 * التحقق من صحة النماذج
 */
function setupFormValidation() {
    const forms = document.querySelectorAll('.mobile-form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!validateForm(form)) {
                event.preventDefault();
            }
        });
    });
    
    /**
     * التحقق من صحة النموذج
     * @param {HTMLFormElement} form النموذج المراد التحقق منه
     * @returns {boolean} نتيجة التحقق
     */
    function validateForm(form) {
        let isValid = true;
        const requiredFields = form.querySelectorAll('[required]');
        
        requiredFields.forEach(field => {
            if (!field.value.trim()) {
                isValid = false;
                field.classList.add('is-invalid');
                
                // إنشاء رسالة خطأ إذا لم تكن موجودة
                let errorMsg = field.nextElementSibling;
                if (!errorMsg || !errorMsg.classList.contains('error-message')) {
                    errorMsg = document.createElement('div');
                    errorMsg.className = 'error-message';
                    errorMsg.textContent = 'هذا الحقل مطلوب';
                    field.parentNode.insertBefore(errorMsg, field.nextSibling);
                }
            } else {
                field.classList.remove('is-invalid');
                
                // إزالة رسالة الخطأ إذا وجدت
                const errorMsg = field.nextElementSibling;
                if (errorMsg && errorMsg.classList.contains('error-message')) {
                    errorMsg.remove();
                }
            }
        });
        
        return isValid;
    }
}

/**
 * إعداد التبديل بين علامات التبويب
 */
function setupTabSwitching() {
    const tabButtons = document.querySelectorAll('.mobile-tab-button');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            
            // إزالة الفئة النشطة من جميع الأزرار
            tabButtons.forEach(btn => btn.classList.remove('active'));
            
            // إضافة الفئة النشطة للزر الحالي
            this.classList.add('active');
            
            // إخفاء جميع محتويات التبويب
            const tabContents = document.querySelectorAll('.mobile-tab-content');
            tabContents.forEach(content => content.style.display = 'none');
            
            // إظهار المحتوى المستهدف
            const targetContent = document.getElementById(targetId);
            if (targetContent) {
                targetContent.style.display = 'block';
            }
        });
    });
    
    // تفعيل علامة التبويب الأولى افتراضياً
    const firstTab = document.querySelector('.mobile-tab-button');
    if (firstTab) {
        firstTab.click();
    }
}

/**
 * إعداد زر العودة للأعلى
 */
function setupScrollToTop() {
    const scrollButton = document.querySelector('.mobile-scroll-top');
    
    if (scrollButton) {
        // إظهار أو إخفاء الزر بناءً على موضع التمرير
        window.addEventListener('scroll', function() {
            if (window.scrollY > 300) {
                scrollButton.classList.add('visible');
            } else {
                scrollButton.classList.remove('visible');
            }
        });
        
        // التمرير للأعلى عند النقر على الزر
        scrollButton.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
}

/**
 * تسجيل Service Worker للـ PWA
 */
function registerServiceWorker() {
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', function() {
            navigator.serviceWorker.register('/static/mobile/js/service-worker.js').then(function(registration) {
                console.log('ServiceWorker تم التسجيل بنجاح مع النطاق: ', registration.scope);
            }, function(err) {
                console.log('ServiceWorker فشل التسجيل: ', err);
            });
        });
    }
}

/**
 * عرض شاشة التحميل
 */
function showLoader() {
    const loader = document.querySelector('.mobile-loader');
    if (loader) {
        loader.classList.add('active');
    }
}

/**
 * إخفاء شاشة التحميل
 */
function hideLoader() {
    const loader = document.querySelector('.mobile-loader');
    if (loader) {
        loader.classList.remove('active');
    }
}

/**
 * عرض إشعار
 * @param {string} message نص الإشعار
 * @param {string} type نوع الإشعار (success, warning, danger)
 * @param {number} duration مدة ظهور الإشعار بالمللي ثانية
 */
function showNotification(message, type = 'success', duration = 3000) {
    // إزالة الإشعارات السابقة
    const existingNotifications = document.querySelectorAll('.mobile-notification');
    existingNotifications.forEach(notification => {
        notification.remove();
    });
    
    // إنشاء عنصر الإشعار
    const notification = document.createElement('div');
    notification.className = `mobile-notification mobile-notification-${type}`;
    notification.textContent = message;
    
    // إضافة الإشعار للصفحة
    document.body.appendChild(notification);
    
    // إزالة الإشعار بعد المدة المحددة
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, duration);
}

/**
 * إرسال طلب AJAX
 * @param {string} url عنوان URL للطلب
 * @param {string} method طريقة الطلب (GET, POST)
 * @param {Object} data البيانات المرسلة مع الطلب
 * @param {Function} successCallback دالة تنفذ عند نجاح الطلب
 * @param {Function} errorCallback دالة تنفذ عند فشل الطلب
 */
function sendAjaxRequest(url, method, data, successCallback, errorCallback) {
    // عرض شاشة التحميل
    showLoader();
    
    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCsrfToken()
        },
        body: method !== 'GET' ? JSON.stringify(data) : null
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('حدث خطأ في الاستجابة');
        }
        return response.json();
    })
    .then(data => {
        hideLoader();
        if (successCallback) {
            successCallback(data);
        }
    })
    .catch(error => {
        hideLoader();
        if (errorCallback) {
            errorCallback(error);
        } else {
            showNotification('حدث خطأ أثناء تنفيذ الطلب', 'danger');
            console.error(error);
        }
    });
}

/**
 * الحصول على رمز CSRF من الكوكيز
 * @returns {string} رمز CSRF
 */
function getCsrfToken() {
    const name = 'csrf_token=';
    const decodedCookie = decodeURIComponent(document.cookie);
    const cookieArray = decodedCookie.split(';');
    
    for (let i = 0; i < cookieArray.length; i++) {
        let cookie = cookieArray[i].trim();
        if (cookie.indexOf(name) === 0) {
            return cookie.substring(name.length, cookie.length);
        }
    }
    
    // البحث عن الرمز في عنصر الإدخال المخفي
    const csrfInput = document.querySelector('input[name="csrf_token"]');
    if (csrfInput) {
        return csrfInput.value;
    }
    
    return '';
}