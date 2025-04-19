<?php
/**
 * ملف مدخل تطبيق Flask على استضافة مشتركة
 * هذا الملف يعمل كنقطة دخول للتطبيق ويوجه الطلبات إلى wsgi.py
 */

// تعيين رأس الاستجابة لمنع التخزين المؤقت
header("Cache-Control: no-store, no-cache, must-revalidate, max-age=0");
header("Cache-Control: post-check=0, pre-check=0", false);
header("Pragma: no-cache");
header("X-Powered-By: Python/Flask");

// تعيين الترميز للدعم العربي
header('Content-Type: text/html; charset=utf-8');

// تحديد مسار Python وملف WSGI
// ملاحظة: قد تحتاج إلى تعديل هذه المسارات حسب إعدادات الخادم الخاص بك
$python_path = '/usr/bin/python3'; // المسار الافتراضي لـ Python 3
$wsgi_script = __DIR__ . '/wsgi.py'; // مسار ملف wsgi.py

// تحقق من وجود ملف WSGI
if (!file_exists($wsgi_script)) {
    header("HTTP/1.1 500 Internal Server Error");
    echo '<html dir="rtl" lang="ar"><head><meta charset="UTF-8"><title>خطأ في التكوين</title>';
    echo '<style>body{font-family:Arial,sans-serif;background-color:#f8f9fa;color:#333;margin:0;padding:20px;text-align:center;} ';
    echo '.error-container{background-color:#fff;border-radius:5px;box-shadow:0 2px 10px rgba(0,0,0,0.1);margin:40px auto;max-width:600px;padding:20px;} ';
    echo 'h1{color:#dc3545;}p{line-height:1.6;}</style></head><body>';
    echo '<div class="error-container"><h1>خطأ في تكوين النظام</h1>';
    echo '<p>لم يتم العثور على ملف WSGI المطلوب. يرجى التأكد من وجود ملف wsgi.py في المجلد الرئيسي للموقع.</p>';
    echo '<p>المسار المتوقع: ' . $wsgi_script . '</p>';
    echo '<p>للمساعدة، يرجى مراجعة <a href="deploy_guide.md">دليل النشر</a>.</p></div></body></html>';
    exit;
}

// الإعداد للاستخدام مع FastCGI/CGI على Hostinger
// تعديل الأذونات لضمان إمكانية تنفيذ ملف wsgi.py
@chmod($wsgi_script, 0755);

try {
    // جرب تشغيل ملف WSGI باستخدام Python
    $command = escapeshellcmd($python_path . ' ' . $wsgi_script);
    $output = [];
    $return_var = 0;
    
    // تنفيذ الأمر وحفظ المخرجات
    exec($command . ' 2>&1', $output, $return_var);
    
    // التحقق من نجاح التنفيذ
    if ($return_var !== 0) {
        header("HTTP/1.1 500 Internal Server Error");
        echo '<html dir="rtl" lang="ar"><head><meta charset="UTF-8"><title>خطأ في تشغيل التطبيق</title>';
        echo '<style>body{font-family:Arial,sans-serif;background-color:#f8f9fa;color:#333;margin:0;padding:20px;text-align:center;} ';
        echo '.error-container{background-color:#fff;border-radius:5px;box-shadow:0 2px 10px rgba(0,0,0,0.1);margin:40px auto;max-width:800px;padding:20px;text-align:right;} ';
        echo 'h1{color:#dc3545;}p{line-height:1.6;}pre{background-color:#f8f9fa;border-radius:4px;padding:10px;overflow:auto;text-align:left;direction:ltr;}</style></head><body>';
        echo '<div class="error-container"><h1>خطأ في تشغيل التطبيق</h1>';
        echo '<p>حدث خطأ أثناء محاولة تشغيل تطبيق Flask. يرجى التحقق من تكوين الخادم والتأكد من تثبيت جميع المتطلبات.</p>';
        echo '<p>رمز الخطأ: ' . $return_var . '</p>';
        
        // عرض الخطأ للمطورين (يمكن إزالته في الإنتاج)
        echo '<h2>تفاصيل الخطأ (للمطورين فقط):</h2>';
        echo '<pre>' . implode("\n", $output) . '</pre>';
        
        echo '<p>للمساعدة، يرجى مراجعة <a href="deploy_guide.md">دليل النشر</a> أو <a href="دليل_النشر_على_الاستضافة.md">الدليل العربي</a>.</p></div></body></html>';
        exit;
    }
    
    // إذا كان هناك مخرجات، اعرضها
    if (!empty($output)) {
        echo implode("\n", $output);
    } else {
        // إذا لم تكن هناك مخرجات، فقد يكون هناك مشكلة
        include 'static/error/500.html';
    }
    
} catch (Exception $e) {
    // التعامل مع الخطأ
    header("HTTP/1.1 500 Internal Server Error");
    echo '<html dir="rtl" lang="ar"><head><meta charset="UTF-8"><title>خطأ في النظام</title>';
    echo '<style>body{font-family:Arial,sans-serif;background-color:#f8f9fa;color:#333;margin:0;padding:20px;text-align:center;} ';
    echo '.error-container{background-color:#fff;border-radius:5px;box-shadow:0 2px 10px rgba(0,0,0,0.1);margin:40px auto;max-width:600px;padding:20px;text-align:right;} ';
    echo 'h1{color:#dc3545;}p{line-height:1.6;}</style></head><body>';
    echo '<div class="error-container"><h1>خطأ في النظام</h1>';
    echo '<p>حدث خطأ غير متوقع أثناء محاولة تشغيل التطبيق.</p>';
    echo '<p>رسالة الخطأ: ' . $e->getMessage() . '</p>';
    echo '<p>للمساعدة، يرجى مراجعة <a href="deploy_guide.md">دليل النشر</a>.</p></div></body></html>';
    exit;
}
?>