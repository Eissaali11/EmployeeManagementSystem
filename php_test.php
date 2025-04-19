<?php
/**
 * ملف اختبار لتشخيص مشاكل التنفيذ على استضافة Hostinger
 */

// تمكين عرض الأخطاء لأغراض التشخيص
ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

echo "<!DOCTYPE html>
<html dir='rtl' lang='ar'>
<head>
    <meta charset='UTF-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <title>اختبار تكوين PHP</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            border-bottom: 2px solid #eee;
            padding-bottom: 10px;
        }
        h2 {
            color: #3498db;
            margin-top: 30px;
        }
        .success {
            color: #27ae60;
            font-weight: bold;
        }
        .error {
            color: #e74c3c;
            font-weight: bold;
        }
        .warning {
            color: #f39c12;
            font-weight: bold;
        }
        pre {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 4px;
            overflow-x: auto;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        table th, table td {
            padding: 10px;
            border: 1px solid #ddd;
            text-align: right;
        }
        table th {
            background-color: #f2f2f2;
        }
    </style>
</head>
<body>
    <div class='container'>
        <h1>اختبار تكوين PHP على استضافة Hostinger</h1>";

// ====== معلومات النظام الأساسية ======
echo "<h2>معلومات النظام</h2>";
echo "<table>
        <tr><th>معلومة</th><th>القيمة</th></tr>
        <tr><td>إصدار PHP</td><td>" . PHP_VERSION . "</td></tr>
        <tr><td>نظام التشغيل</td><td>" . PHP_OS . "</td></tr>
        <tr><td>واجهة السيرفر</td><td>" . $_SERVER['SERVER_SOFTWARE'] . "</td></tr>
        <tr><td>مجلد PHP الحالي</td><td>" . getcwd() . "</td></tr>
        <tr><td>المسار النسبي للملف</td><td>" . __FILE__ . "</td></tr>
        <tr><td>العنوان الكامل</td><td>" . (isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] === 'on' ? "https" : "http") . "://$_SERVER[HTTP_HOST]$_SERVER[REQUEST_URI]" . "</td></tr>
      </table>";

// ====== التحقق من وجود الملفات الرئيسية ======
echo "<h2>التحقق من الملفات الرئيسية</h2>";
echo "<ul>";
$required_files = [
    '.htaccess' => 'ملف تكوين Apache',
    'index.php' => 'صفحة البداية',
    'wsgi.py' => 'سكريبت WSGI',
    '.env' => 'متغيرات البيئة',
    'app.py' => 'تطبيق Flask',
    'main.py' => 'المدخل الرئيسي للتطبيق',
    'models.py' => 'نماذج قاعدة البيانات',
    'requirements.txt' => 'متطلبات Python'
];

foreach ($required_files as $file => $description) {
    if (file_exists($file)) {
        echo "<li><span class='success'>✓</span> {$description} (<code>{$file}</code>) موجود</li>";
    } else {
        echo "<li><span class='error'>✗</span> {$description} (<code>{$file}</code>) غير موجود</li>";
    }
}
echo "</ul>";

// ====== التحقق من أذونات الملفات ======
echo "<h2>أذونات الملفات</h2>";
echo "<ul>";
$permissions_check = [
    '.' => 'المجلد الرئيسي',
    '.htaccess' => 'ملف تكوين Apache',
    'index.php' => 'صفحة البداية',
    'wsgi.py' => 'سكريبت WSGI',
    '.env' => 'متغيرات البيئة',
    'app.py' => 'تطبيق Flask',
    'static' => 'مجلد الملفات الثابتة',
    'templates' => 'مجلد القوالب'
];

foreach ($permissions_check as $file => $description) {
    if (file_exists($file)) {
        $perms = fileperms($file);
        $perms_text = substr(sprintf('%o', $perms), -4);
        $is_dir = is_dir($file);
        $expected = $is_dir ? '0755' : '0644';
        $expected_exec = '0755';
        
        $perms_ok = false;
        if ($is_dir && $perms_text == $expected) {
            $perms_ok = true;
        } elseif (!$is_dir && ($perms_text == $expected || $perms_text == $expected_exec)) {
            $perms_ok = true;
        }
        
        if ($perms_ok) {
            echo "<li><span class='success'>✓</span> {$description} (<code>{$file}</code>) الأذونات: {$perms_text}</li>";
        } else {
            echo "<li><span class='warning'>⚠</span> {$description} (<code>{$file}</code>) الأذونات: {$perms_text}, الأذونات المتوقعة: " . ($is_dir ? "0755" : "0644 أو 0755 للملفات التنفيذية") . "</li>";
        }
    } else {
        echo "<li><span class='error'>✗</span> {$description} (<code>{$file}</code>) غير موجود</li>";
    }
}
echo "</ul>";

// ====== التحقق من قاعدة البيانات ======
echo "<h2>التحقق من إعدادات قاعدة البيانات</h2>";
if (file_exists('.env')) {
    echo "<p><span class='success'>✓</span> تم العثور على ملف .env</p>";
    
    // قراءة الملف ومحاولة استخراج URL قاعدة البيانات (مع إخفاء التفاصيل الحساسة)
    $env_content = file_get_contents('.env');
    $db_url_match = [];
    if (preg_match('/DATABASE_URL\s*=\s*([^\r\n]+)/', $env_content, $db_url_match)) {
        $db_url = $db_url_match[1];
        
        // تحليل URL قاعدة البيانات بأمان
        $safe_db_url = preg_replace('/(:)[^:@]+(@)/', '$1*****$2', $db_url);
        echo "<p>تم العثور على رابط قاعدة البيانات: <code>{$safe_db_url}</code></p>";
        
        // التحقق من نوع قاعدة البيانات
        if (strpos($db_url, 'mysql://') === 0) {
            echo "<p><span class='success'>✓</span> نوع قاعدة البيانات: MySQL</p>";
        } elseif (strpos($db_url, 'postgresql://') === 0) {
            echo "<p><span class='warning'>⚠</span> نوع قاعدة البيانات: PostgreSQL (تأكد من أن الاستضافة تدعم PostgreSQL)</p>";
        } else {
            echo "<p><span class='error'>✗</span> نوع قاعدة البيانات غير معروف</p>";
        }
    } else {
        echo "<p><span class='error'>✗</span> لم يتم العثور على رابط قاعدة البيانات في ملف .env</p>";
    }
} else {
    echo "<p><span class='error'>✗</span> ملف .env غير موجود</p>";
}

// ====== اختبار تنفيذ Python ======
echo "<h2>اختبار تنفيذ Python</h2>";

$python_paths = [
    '/usr/bin/python3',
    '/usr/local/bin/python3',
    '/opt/alt/python39/bin/python3',
    'python3',
    'python'
];

$python_found = false;
$python_version = "";
$python_path = "";

foreach ($python_paths as $path) {
    $command = "$path --version 2>&1";
    $output = [];
    $return_var = -1;
    
    exec($command, $output, $return_var);
    
    if ($return_var === 0) {
        $python_found = true;
        $python_version = implode("\n", $output);
        $python_path = $path;
        break;
    }
}

if ($python_found) {
    echo "<p><span class='success'>✓</span> تم العثور على Python: <code>{$python_path}</code></p>";
    echo "<p>الإصدار: <code>{$python_version}</code></p>";
    
    // اختبار تنفيذ كود Python بسيط
    $test_command = "$python_path -c \"import sys; print('Python is working! Version: ' + sys.version)\" 2>&1";
    $test_output = [];
    $test_result = -1;
    
    exec($test_command, $test_output, $test_result);
    
    if ($test_result === 0) {
        echo "<p><span class='success'>✓</span> يمكن تنفيذ كود Python:</p>";
        echo "<pre>" . implode("\n", $test_output) . "</pre>";
        
        // فحص تثبيت المكتبات الأساسية
        $libraries = ['flask', 'sqlalchemy', 'pymysql', 'dotenv'];
        echo "<p>التحقق من تثبيت المكتبات الأساسية:</p>";
        echo "<ul>";
        
        foreach ($libraries as $lib) {
            $lib_command = "$python_path -c \"import $lib; print('$lib version: ' + str(getattr($lib, '__version__', 'unknown')))\" 2>&1";
            $lib_output = [];
            $lib_result = -1;
            
            exec($lib_command, $lib_output, $lib_result);
            
            if ($lib_result === 0) {
                echo "<li><span class='success'>✓</span> مكتبة $lib: مثبتة - " . implode("\n", $lib_output) . "</li>";
            } else {
                echo "<li><span class='error'>✗</span> مكتبة $lib: غير مثبتة</li>";
            }
        }
        
        echo "</ul>";
    } else {
        echo "<p><span class='error'>✗</span> فشل تنفيذ كود Python:</p>";
        echo "<pre>" . implode("\n", $test_output) . "</pre>";
    }
} else {
    echo "<p><span class='error'>✗</span> لم يتم العثور على Python في المسارات المتوقعة</p>";
}

// ====== اختبار تنفيذ ملف wsgi.py ======
if (file_exists('wsgi.py') && $python_found) {
    echo "<h2>اختبار تنفيذ ملف wsgi.py</h2>";
    
    // التأكد أولاً من أن الملف قابل للتنفيذ
    if (!is_executable('wsgi.py')) {
        echo "<p><span class='warning'>⚠</span> ملف wsgi.py غير قابل للتنفيذ. محاولة تغيير الأذونات...</p>";
        if (@chmod('wsgi.py', 0755)) {
            echo "<p><span class='success'>✓</span> تم تغيير أذونات wsgi.py بنجاح إلى 0755</p>";
        } else {
            echo "<p><span class='error'>✗</span> فشل تغيير أذونات wsgi.py. يرجى تغييرها يدوياً إلى 0755</p>";
        }
    }
    
    // تنفيذ ملف wsgi.py
    $wsgi_command = "$python_path wsgi.py 2>&1";
    $wsgi_output = [];
    $wsgi_result = -1;
    
    exec($wsgi_command, $wsgi_output, $wsgi_result);
    
    echo "<p>نتيجة تنفيذ wsgi.py: " . ($wsgi_result === 0 ? "<span class='success'>ناجح</span>" : "<span class='error'>فشل (كود: $wsgi_result)</span>") . "</p>";
    echo "<p>مخرجات التنفيذ:</p>";
    echo "<pre>" . implode("\n", $wsgi_output) . "</pre>";
}

// ====== اختبار دوال PHP المطلوبة ======
echo "<h2>اختبار دوال PHP المطلوبة</h2>";
$required_functions = [
    'exec' => 'تنفيذ أوامر نظام التشغيل',
    'shell_exec' => 'تنفيذ أوامر نظام التشغيل وإرجاع المخرجات',
    'system' => 'تنفيذ أوامر نظام التشغيل وعرض المخرجات',
    'passthru' => 'تنفيذ أوامر نظام التشغيل وتمرير المخرجات',
    'escapeshellcmd' => 'تأمين أوامر نظام التشغيل',
    'file_get_contents' => 'قراءة محتوى الملفات',
    'file_put_contents' => 'كتابة محتوى الملفات'
];

echo "<ul>";
foreach ($required_functions as $func => $desc) {
    if (function_exists($func)) {
        echo "<li><span class='success'>✓</span> دالة $func متاحة ($desc)</li>";
    } else {
        echo "<li><span class='error'>✗</span> دالة $func غير متاحة ($desc) - قد تكون معطلة في تكوين PHP</li>";
    }
}
echo "</ul>";

// ====== معلومات إضافية ======
echo "<h2>معلومات إضافية</h2>";

// التحقق من mod_rewrite
echo "<p>التحقق من mod_rewrite (مطلوب لعمل روابط SEO):</p>";
if (function_exists('apache_get_modules')) {
    $modules = apache_get_modules();
    if (in_array('mod_rewrite', $modules)) {
        echo "<p><span class='success'>✓</span> mod_rewrite مفعل</p>";
    } else {
        echo "<p><span class='error'>✗</span> mod_rewrite غير مفعل</p>";
    }
} else {
    echo "<p><span class='warning'>⚠</span> لا يمكن التحقق من mod_rewrite (غالباً لأن PHP يعمل كـ CGI/FastCGI)</p>";
}

// إظهار المتغيرات البيئية
echo "<h2>المتغيرات البيئية</h2>";
echo "<pre>";
$env_vars = getenv();
foreach ($env_vars as $key => $value) {
    // تجنب عرض معلومات حساسة
    if (!in_array(strtolower($key), ['password', 'secret', 'token', 'key', 'pwd'])) {
        echo htmlspecialchars("$key = $value") . "\n";
    }
}
echo "</pre>";

echo "<h2>الخلاصة والخطوات التالية</h2>";
echo "<ol>
    <li>تأكد من وجود جميع الملفات الرئيسية (.htaccess, index.php, wsgi.py, .env)</li>
    <li>تأكد من أن أذونات المجلدات هي 755 وأذونات الملفات العادية هي 644</li>
    <li>تأكد من أن أذونات الملفات التنفيذية (wsgi.py, setup.py) هي 755</li>
    <li>تأكد من صحة بيانات الاتصال بقاعدة البيانات في ملف .env</li>
    <li>تأكد من تثبيت Python وجميع المكتبات المطلوبة</li>
    <li>تأكد من أن Hostinger يدعم تنفيذ أوامر نظام التشغيل</li>
</ol>";

echo "</div>
</body>
</html>";
?>