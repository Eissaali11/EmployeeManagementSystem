<?php
/**
 * ملف المدخل الرئيسي لنظام إدارة الموظفين
 * يقوم هذا الملف بتوجيه الطلبات إلى تطبيق Flask
 */

// التحقق من أن Python متاح
$python_path = '/usr/bin/python3';
if (!file_exists($python_path)) {
    $python_path = '/usr/bin/python';
    if (!file_exists($python_path)) {
        die('لم يتم العثور على Python على الخادم. يرجى الاتصال بمزود الاستضافة.');
    }
}

// تعيين المتغيرات البيئية
$env_file = '.env';
if (file_exists($env_file)) {
    $lines = file($env_file, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    foreach ($lines as $line) {
        if (strpos($line, '=') !== false && strpos($line, '#') !== 0) {
            list($key, $value) = explode('=', $line, 2);
            $key = trim($key);
            $value = trim($value);
            putenv("$key=$value");
        }
    }
}

// تخزين URL الطلب الحالي لاستخدامه في wsgi.py
putenv('REQUEST_URI=' . $_SERVER['REQUEST_URI']);

// محاولة تنفيذ تطبيق Flask
try {
    // طريقة 1: تشغيل التطبيق مباشرة عبر wsgi.py
    if (file_exists('wsgi.py')) {
        $command = escapeshellcmd("$python_path wsgi.py");
        $output = shell_exec($command);
        if ($output) {
            echo $output;
        } else {
            // إذا فشل التنفيذ، انتقل إلى صفحة التثبيت
            header('Location: /static/deploy/');
            exit;
        }
    } 
    // طريقة 2: توجيه المستخدم إلى صفحة التثبيت
    else {
        header('Location: /static/deploy/');
        exit;
    }
} catch (Exception $e) {
    // عرض رسالة خطأ
    header('HTTP/1.1 500 Internal Server Error');
    echo '<html dir="rtl"><head><meta charset="UTF-8"><title>خطأ في التنفيذ</title>';
    echo '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css">';
    echo '</head><body><div class="container mt-5">';
    echo '<div class="alert alert-danger"><h4>خطأ في تشغيل التطبيق</h4>';
    echo '<p>' . $e->getMessage() . '</p>';
    echo '<p>يرجى التحقق من إعدادات الخادم أو الاتصال بمزود الاستضافة.</p>';
    echo '</div>';
    echo '<a href="/static/deploy/" class="btn btn-primary">الذهاب إلى صفحة التثبيت</a>';
    echo '</div></body></html>';
}
?>