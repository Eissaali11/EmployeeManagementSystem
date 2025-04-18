// تعريف اسم التخزين المؤقت
const CACHE_NAME = 'employee-system-cache-v1';

// قائمة الملفات للتخزين المؤقت
const urlsToCache = [
  '/mobile',
  '/mobile/login',
  '/static/mobile/css/mobile-theme.css',
  '/static/mobile/img/logo.png',
  'https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800&display=swap',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css',
  'https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css',
  'https://code.jquery.com/jquery-3.6.0.min.js'
];

// تثبيت خادم الويب
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('فتح ذاكرة التخزين المؤقت');
        return cache.addAll(urlsToCache);
      })
  );
});

// تفعيل خادم الويب
self.addEventListener('activate', event => {
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// استراتيجية التخزين المؤقت - الشبكة أولاً مع التخزين المؤقت كاحتياطي
self.addEventListener('fetch', event => {
  event.respondWith(
    fetch(event.request)
      .then(response => {
        // إذا كان الطلب ناجحاً، قم بنسخه وتخزينه
        if (event.request.method === 'GET' && response.status === 200) {
          let responseToCache = response.clone();
          caches.open(CACHE_NAME)
            .then(cache => {
              cache.put(event.request, responseToCache);
            });
        }
        return response;
      })
      .catch(() => {
        // إذا فشل الطلب، حاول تقديم النسخة المخزنة مؤقتاً
        return caches.match(event.request);
      })
  );
});