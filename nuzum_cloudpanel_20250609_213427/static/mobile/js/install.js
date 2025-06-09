// متغيرات عالمية
let deferredPrompt;
const installButton = document.getElementById('install-app-button');

// إخفاء زر التثبيت في البداية
if (installButton) {
  installButton.style.display = 'none';
}

// مراقبة حدث beforeinstallprompt
window.addEventListener('beforeinstallprompt', (e) => {
  // منع ظهور الرسالة تلقائياً
  e.preventDefault();
  
  // تخزين الحدث لاستخدامه لاحقاً
  deferredPrompt = e;
  
  // إظهار زر التثبيت
  if (installButton) {
    installButton.style.display = 'block';
  }
  
  // إضافة تفاعل للزر
  if (installButton) {
    installButton.addEventListener('click', async () => {
      if (!deferredPrompt) {
        return;
      }
      
      // إظهار مربع حوار التثبيت
      deferredPrompt.prompt();
      
      // انتظار اختيار المستخدم
      const { outcome } = await deferredPrompt.userChoice;
      console.log(`اختيار المستخدم: ${outcome}`);
      
      // تفريغ المتغير
      deferredPrompt = null;
      
      // إخفاء الزر
      installButton.style.display = 'none';
    });
  }
});

// التحقق إذا كان التطبيق مثبتاً بالفعل
window.addEventListener('appinstalled', (e) => {
  console.log('تم تثبيت التطبيق بنجاح');
  
  // إخفاء زر التثبيت
  if (installButton) {
    installButton.style.display = 'none';
  }
  
  // تفريغ المتغير
  deferredPrompt = null;
});