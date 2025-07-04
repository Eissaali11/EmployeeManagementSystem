/**
 * Service Worker خاص بالتطبيق المحمول
 * نظام إدارة الموظفين - النسخة المحمولة
 */

// اسم وإصدار التخزين المؤقت
const CACHE_NAME = 'employee-management-mobile-v1';

// قائمة الملفات التي سيتم تخزينها مؤقتًا (offline-first)
const filesToCache = [
  '/mobile',
  '/mobile/',
  '/static/mobile/css/mobile-style.css',
  '/static/mobile/js/mobile-script.js',
  '/static/mobile/js/service-worker.js',
  '/static/mobile/images/logo.png',
  '/static/mobile/images/icon-192.png',
  '/static/mobile/images/icon-512.png',
  '/static/mobile/manifest.json',
  '/static/fonts/Tajawal-Regular.ttf',
  '/static/fonts/Tajawal-Bold.ttf',
  '/static/css/fontawesome.min.css',
  '/static/css/solid.min.css',
  'https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css'
];

// تثبيت Service Worker وتخزين الملفات
self.addEventListener('install', event => {
  console.log('تثبيت Service Worker...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('تخزين الملفات في التخزين المؤقت');
        return cache.addAll(filesToCache);
      })
      .then(() => self.skipWaiting())
  );
});

// تنشيط Service Worker وحذف التخزينات القديمة
self.addEventListener('activate', event => {
  console.log('تنشيط Service Worker...');
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('حذف التخزين المؤقت القديم:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// استراتيجية "Network First, with Cache Fallback"
self.addEventListener('fetch', event => {
  // تجاهل الطلبات غير GET
  if (event.request.method !== 'GET') return;
  
  // تجاهل طلبات API والنماذج
  if (event.request.url.includes('/api/') || 
      event.request.url.includes('/login') ||
      event.request.url.includes('/logout')) {
    return;
  }
  
  event.respondWith(
    fetch(event.request)
      .then(response => {
        // نسخ الاستجابة لأننا سنستخدمها مرتين
        const responseToCache = response.clone();
        
        // تخزين الاستجابة الجديدة في التخزين المؤقت
        caches.open(CACHE_NAME)
          .then(cache => {
            cache.put(event.request, responseToCache);
          });
          
        return response;
      })
      .catch(() => {
        // إذا فشل الاتصال بالشبكة، استخدم النسخة المخزنة مسبقًا
        return caches.match(event.request)
          .then(cachedResponse => {
            // إرجاع الاستجابة المخزنة أو صفحة الخطأ
            if (cachedResponse) {
              return cachedResponse;
            }
            
            // إذا كان الطلب لصفحة HTML ولم تكن مخزنة، أعرض صفحة الخطأ المخزنة
            if (event.request.headers.get('accept').includes('text/html')) {
              return caches.match('/mobile/offline.html');
            }
          });
      })
  );
});

// التعامل مع إشعارات التحديث (إذا كان التطبيق يدعم الإشعارات)
self.addEventListener('push', event => {
  if (!event.data) return;
  
  const notification = event.data.json();
  const title = notification.title || 'نظام إدارة الموظفين';
  const options = {
    body: notification.body || 'تم استلام إشعار جديد',
    icon: notification.icon || '/static/mobile/images/icon-192.png',
    badge: '/static/mobile/images/badge.png',
    data: notification.data || {},
    dir: 'rtl'
  };
  
  event.waitUntil(self.registration.showNotification(title, options));
});

// التعامل مع النقر على الإشعار
self.addEventListener('notificationclick', event => {
  event.notification.close();
  
  // فتح النافذة المستهدفة أو الصفحة الرئيسية
  event.waitUntil(
    clients.matchAll({type: 'window'})
      .then(clientList => {
        const url = event.notification.data.url || '/mobile';
        
        // إذا كانت النافذة مفتوحة، قم بالتركيز عليها
        for (const client of clientList) {
          if (client.url === url && 'focus' in client) {
            return client.focus();
          }
        }
        
        // إذا لم تكن النافذة مفتوحة، افتح نافذة جديدة
        if (clients.openWindow) {
          return clients.openWindow(url);
        }
      })
  );
});