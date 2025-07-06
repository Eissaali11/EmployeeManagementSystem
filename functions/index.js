const functions = require('firebase-functions');
const { exec } = require('child_process');
const express = require('express');
const app = express();

// صفحة بسيطة للتأكد من أن الخادم يعمل
app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', message: 'نظام نُظم يعمل بنجاح' });
});

// توجيه كل الطلبات إلى تطبيق Flask
app.all('*', (req, res) => {
  // تنفيذ طلب HTTP إلى تطبيق Flask المحلي
  const { spawn } = require('child_process');
  const method = req.method;
  const path = req.path;
  const headers = req.headers;
  const body = req.body;
  
  // سجل معلومات الطلب
  console.log(`[${new Date().toISOString()}] ${method} ${path}`);
  
  // هنا نقوم باستدعاء تطبيق Flask
  // هذا الجزء سيحتاج إلى تعديل عندما تنشر فعلياً
  res.redirect(`https://your-flask-backend-url.com${path}`);
});

// تصدير دالة Express كـ Firebase Function
exports.app = functions.https.onRequest(app);

// دالة لبدء تشغيل خادم Gunicorn في الخلفية
exports.startFlaskServer = functions.https.onRequest((req, res) => {
  // ملاحظة: هذه طريقة للتوضيح فقط
  // ستحتاج إلى تعديلها وفقاً لبيئة Cloud Functions
  const server = exec('cd /workspace && gunicorn --bind 0.0.0.0:8080 main:app');
  
  server.stdout.on('data', (data) => {
    console.log(`stdout: ${data}`);
  });
  
  server.stderr.on('data', (data) => {
    console.error(`stderr: ${data}`);
  });
  
  server.on('close', (code) => {
    console.log(`child process exited with code ${code}`);
  });
  
  res.json({ status: 'started', message: 'تم بدء تشغيل خادم Flask' });
});