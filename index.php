<?php
/**
 * ملف مدخل بسيط لموقع Flask على استضافة Hostinger
 */

// تسجيل الأخطاء لمساعدة في استكشاف المشكلات
ini_set('display_errors', 1);
ini_set('log_errors', 1);
ini_set('error_log', dirname(__FILE__) . '/php_errors.log');

// رؤوس الصفحة
header('Content-Type: text/html; charset=utf-8');

// الإحاطة بالكود في كتلة try-catch لإدارة الأخطاء
try {
    // التحقق من وجود ملف WSGI
    if (!file_exists('wsgi.py')) {
        throw new Exception('ملف wsgi.py غير موجود في المجلد ' . dirname(__FILE__));
    }
    
    // التحقق من وجود ملف .env
    if (!file_exists('.env')) {
        throw new Exception('ملف .env غير موجود. يرجى إنشاء ملف .env من ملف .env.example');
    }
    
    // تحديد مسار Python - قد تحتاج لتعديله حسب إعدادات الخادم الخاص بك
    $python_paths = [
        '/usr/bin/python3',      // المسار الشائع في استضافة Hostinger
        '/usr/local/bin/python3', // مسار آخر محتمل
        '/opt/alt/python39/bin/python3', // مسار بديل في بعض الاستضافات
        'python3',               // استخدام Python من متغير PATH
        'python'                 // محاولة أخيرة باستخدام الأمر العام
    ];
    
    $python_found = false;
    $python_path = '';
    
    // البحث عن أول مسار Python متاح
    foreach ($python_paths as $path) {
        $test_command = "$path --version 2>&1";
        $test_output = [];
        $test_return = -1;
        
        exec($test_command, $test_output, $test_return);
        
        if ($test_return === 0) {
            $python_path = $path;
            $python_found = true;
            break;
        }
    }
    
    if (!$python_found) {
        throw new Exception('لم يتم العثور على Python في المسارات المتوقعة. يرجى التواصل مع الدعم الفني لاستضافة Hostinger.');
    }
    
    // تنفيذ سكريبت WSGI
    $command = escapeshellcmd("$python_path wsgi.py");
    $output = [];
    $return_var = -1;
    
    // تنفيذ الأمر مع تسجيل الخطأ
    exec($command . ' 2>&1', $output, $return_var);
    
    // إذا فشل التنفيذ، عرض رسالة خطأ تفصيلية
    if ($return_var !== 0) {
        echo '<html dir="rtl" lang="ar"><head><meta charset="UTF-8">';
        echo '<title>خطأ في تشغيل التطبيق</title>';
        echo '<style>body{font-family:Arial,sans-serif;background:#f5f5f5;color:#333;margin:0;padding:20px;} ';
        echo '.container{background:#fff;border-radius:5px;box-shadow:0 2px 10px rgba(0,0,0,0.1);margin:40px auto;max-width:800px;padding:20px;} ';
        echo 'h1{color:#e74c3c;}h2{color:#3498db;}pre{background:#f8f9fa;padding:10px;overflow:auto;border-radius:4px;}</style>';
        echo '</head><body><div class="container">';
        echo '<h1>حدث خطأ أثناء تشغيل التطبيق</h1>';
        echo '<p>لم يتمكن النظام من تشغيل تطبيق Python بنجاح.</p>';
        
        echo '<h2>معلومات النظام:</h2>';
        echo '<ul>';
        echo '<li>نظام التشغيل: ' . PHP_OS . '</li>';
        echo '<li>إصدار PHP: ' . PHP_VERSION . '</li>';
        echo '<li>مسار Python المستخدم: ' . $python_path . '</li>';
        echo '<li>المجلد الحالي: ' . dirname(__FILE__) . '</li>';
        echo '</ul>';
        
        echo '<h2>مخرجات تنفيذ Python:</h2>';
        echo '<pre>' . implode("\n", $output) . '</pre>';
        
        echo '<h2>الخطوات المقترحة للإصلاح:</h2>';
        echo '<ol>';
        echo '<li>تأكد من تثبيت Python 3.9 أو أحدث على الخادم</li>';
        echo '<li>تحقق من تثبيت جميع حزم Python المطلوبة (requirements.txt)</li>';
        echo '<li>تأكد من أن ملف .env يحتوي على جميع المتغيرات البيئية المطلوبة</li>';
        echo '<li>تأكد من الاتصال بقاعدة البيانات باستخدام بيانات صحيحة</li>';
        echo '<li>راجع سجلات الخطأ في لوحة تحكم Hostinger</li>';
        echo '</ol>';
        
        echo '</div></body></html>';
        exit;
    }
    
    // عرض مخرجات Python (إذا كانت هناك)
    if (!empty($output)) {
        echo implode("\n", $output);
    } else {
        // إذا لم تكن هناك مخرجات، عرض صفحة افتراضية
        echo '<html dir="rtl" lang="ar">';
        echo '<head><meta charset="UTF-8"><title>نظام إدارة الموظفين</title>';
        echo '<meta http-equiv="refresh" content="0;url=/">';
        echo '</head><body style="font-family:Arial,sans-serif;text-align:center;margin-top:100px;">';
        echo '<h1>جاري تحميل النظام...</h1>';
        echo '<p>إذا لم يتم التحويل تلقائياً، <a href="/">انقر هنا</a></p>';
        echo '</body></html>';
    }
} catch (Exception $e) {
    // عرض رسالة الخطأ بتنسيق منسق
    echo '<html dir="rtl" lang="ar"><head><meta charset="UTF-8">';
    echo '<title>خطأ في تشغيل النظام</title>';
    echo '<style>body{font-family:Arial,sans-serif;background:#f5f5f5;color:#333;margin:0;padding:20px;} ';
    echo '.container{background:#fff;border-radius:5px;box-shadow:0 2px 10px rgba(0,0,0,0.1);margin:40px auto;max-width:800px;padding:20px;} ';
    echo 'h1{color:#e74c3c;}pre{background:#f8f9fa;padding:10px;overflow:auto;border-radius:4px;}</style>';
    echo '</head><body><div class="container">';
    echo '<h1>حدث خطأ أثناء بدء تشغيل النظام</h1>';
    echo '<p>رسالة الخطأ: ' . $e->getMessage() . '</p>';
    
    // عرض معلومات الخطأ المفصلة للمطورين
    echo '<h2>معلومات تفصيلية (للمطورين فقط):</h2>';
    echo '<pre>';
    echo 'PHP Version: ' . PHP_VERSION . "\n";
    echo 'Current Directory: ' . getcwd() . "\n";
    echo 'Script Path: ' . __FILE__ . "\n";
    echo 'Error Time: ' . date('Y-m-d H:i:s') . "\n\n";
    echo 'Stack Trace:' . "\n" . $e->getTraceAsString();
    echo '</pre>';
    
    echo '</div></body></html>';
    
    // تسجيل الخطأ في ملف السجل أيضًا
    error_log('نظام إدارة الموظفين - خطأ: ' . $e->getMessage() . ' في ' . $e->getFile() . ' على السطر ' . $e->getLine());
}
?>