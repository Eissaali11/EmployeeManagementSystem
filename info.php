<?php
// ملف استخدامي لمعرفة معلومات PHP والخادم
// تنبيه: ينبغي حذف هذا الملف بعد الاستخدام لأسباب أمنية

echo "<div style='direction:rtl; font-family:Arial; padding:20px;'>";
echo "<h1>معلومات PHP على الخادم</h1>";

// معلومات PHP الأساسية
echo "<h2>معلومات PHP الأساسية</h2>";
echo "<ul>";
echo "<li>إصدار PHP: " . PHP_VERSION . "</li>";
echo "<li>نظام التشغيل: " . PHP_OS . "</li>";
echo "<li>واجهة PHP: " . php_sapi_name() . "</li>";
echo "<li>المجلد المؤقت: " . sys_get_temp_dir() . "</li>";
echo "</ul>";

// الإضافات
echo "<h2>الإضافات المثبتة</h2>";
$extensions = get_loaded_extensions();
sort($extensions);
echo "<ul>";
foreach ($extensions as $extension) {
    echo "<li>$extension</li>";
}
echo "</ul>";

// الموديولات
echo "<h2>وحدات Apache المفعلة</h2>";
if (function_exists('apache_get_modules')) {
    $modules = apache_get_modules();
    sort($modules);
    echo "<ul>";
    foreach ($modules as $module) {
        echo "<li>$module</li>";
    }
    echo "</ul>";
} else {
    echo "<p>لا يمكن الوصول إلى وحدات Apache (قد يكون PHP يعمل كـ CGI)</p>";
}

// إعدادات PHP
echo "<h2>إعدادات PHP</h2>";
echo "<table border='1' cellpadding='5' style='border-collapse:collapse;'>";
echo "<tr><th>الإعداد</th><th>القيمة</th></tr>";

$settings = [
    'display_errors', 'max_execution_time', 'memory_limit', 'post_max_size', 
    'upload_max_filesize', 'max_file_uploads', 'allow_url_fopen', 
    'default_charset', 'date.timezone', 'session.save_path'
];

foreach ($settings as $setting) {
    echo "<tr><td>$setting</td><td>" . ini_get($setting) . "</td></tr>";
}
echo "</table>";

// المتغيرات البيئية
echo "<h2>متغيرات الخادم</h2>";
echo "<table border='1' cellpadding='5' style='border-collapse:collapse;'>";
echo "<tr><th>المتغير</th><th>القيمة</th></tr>";
foreach ($_SERVER as $key => $value) {
    if (!is_array($value)) {
        echo "<tr><td>$key</td><td>" . htmlspecialchars($value) . "</td></tr>";
    }
}
echo "</table>";

// اختبار قواعد البيانات
echo "<h2>دعم قواعد البيانات</h2>";
echo "<ul>";
echo "<li>SQLite: " . (extension_loaded('sqlite3') ? 'مدعوم' : 'غير مدعوم') . "</li>";
echo "<li>MySQL: " . (extension_loaded('mysqli') ? 'مدعوم' : 'غير مدعوم') . "</li>";
echo "<li>PostgreSQL: " . (extension_loaded('pgsql') ? 'مدعوم' : 'غير مدعوم') . "</li>";
echo "<li>PDO: " . (extension_loaded('pdo') ? 'مدعوم' : 'غير مدعوم') . "</li>";
if (extension_loaded('pdo')) {
    echo "<ul>";
    echo "<li>PDO MySQL: " . (extension_loaded('pdo_mysql') ? 'مدعوم' : 'غير مدعوم') . "</li>";
    echo "<li>PDO SQLite: " . (extension_loaded('pdo_sqlite') ? 'مدعوم' : 'غير مدعوم') . "</li>";
    echo "<li>PDO PostgreSQL: " . (extension_loaded('pdo_pgsql') ? 'مدعوم' : 'غير مدعوم') . "</li>";
    echo "</ul>";
}
echo "</ul>";

// اختبار الاتصال بقاعدة البيانات MySQL
echo "<h2>اختبار الاتصال بقاعدة البيانات</h2>";
if (extension_loaded('mysqli') || extension_loaded('pdo_mysql')) {
    try {
        $host = 'localhost';
        $db   = 'u800258840_eissa';
        $user = 'u800258840_eissa';
        $pass = 'Eisa2012@#';
        
        if (extension_loaded('pdo_mysql')) {
            $conn = new PDO("mysql:host=$host;dbname=$db;charset=utf8mb4", $user, $pass);
            $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
            echo "<p style='color:green'>✓ اتصال PDO بقاعدة البيانات MySQL ناجح.</p>";
            
            // استعلام إحصائي
            $stmt = $conn->query("SHOW TABLES");
            $tables = $stmt->fetchAll(PDO::FETCH_COLUMN);
            echo "<p>عدد الجداول: " . count($tables) . "</p>";
            if (count($tables) > 0) {
                echo "<ul>";
                foreach ($tables as $table) {
                    echo "<li>$table</li>";
                }
                echo "</ul>";
            }
        } elseif (extension_loaded('mysqli')) {
            $conn = new mysqli($host, $user, $pass, $db);
            if ($conn->connect_error) {
                throw new Exception("فشل الاتصال: " . $conn->connect_error);
            }
            echo "<p style='color:green'>✓ اتصال MySQLi بقاعدة البيانات ناجح.</p>";
            
            // استعلام إحصائي
            $result = $conn->query("SHOW TABLES");
            $tables = [];
            while ($row = $result->fetch_array()) {
                $tables[] = $row[0];
            }
            echo "<p>عدد الجداول: " . count($tables) . "</p>";
            if (count($tables) > 0) {
                echo "<ul>";
                foreach ($tables as $table) {
                    echo "<li>$table</li>";
                }
                echo "</ul>";
            }
            $conn->close();
        }
    } catch (Exception $e) {
        echo "<p style='color:red'>✗ فشل الاتصال بقاعدة البيانات: " . $e->getMessage() . "</p>";
    }
} else {
    echo "<p style='color:red'>✗ لا يوجد دعم لـ MySQL في PHP على هذا الخادم</p>";
}

// اختبار تنفيذ أوامر النظام
echo "<h2>اختبار تنفيذ أوامر النظام</h2>";
if (function_exists('exec')) {
    echo "<p>✓ دالة exec متوفرة</p>";
    $output = [];
    $return_var = 0;
    exec('uname -a 2>&1', $output, $return_var);
    echo "<p>نتيجة تنفيذ 'uname -a': " . ($return_var === 0 ? 'ناجح' : 'فشل') . "</p>";
    if ($return_var === 0) {
        echo "<pre>" . implode("\n", $output) . "</pre>";
    }
} else {
    echo "<p>✗ دالة exec غير متوفرة أو معطلة</p>";
}

if (function_exists('shell_exec')) {
    echo "<p>✓ دالة shell_exec متوفرة</p>";
    $output = shell_exec('whoami 2>&1');
    echo "<p>نتيجة تنفيذ 'whoami': " . ($output !== null ? 'ناجح' : 'فشل') . "</p>";
    if ($output !== null) {
        echo "<pre>$output</pre>";
    }
} else {
    echo "<p>✗ دالة shell_exec غير متوفرة أو معطلة</p>";
}

// اختبار كتابة الملفات
echo "<h2>اختبار كتابة الملفات</h2>";
$test_dir = './';
$test_file = $test_dir . 'test_write_' . time() . '.txt';
$write_test = file_put_contents($test_file, 'اختبار الكتابة');
if ($write_test !== false) {
    echo "<p style='color:green'>✓ تم إنشاء ملف اختبار الكتابة بنجاح.</p>";
    if (unlink($test_file)) {
        echo "<p style='color:green'>✓ تم حذف ملف الاختبار بنجاح.</p>";
    } else {
        echo "<p style='color:red'>✗ فشل حذف ملف الاختبار.</p>";
    }
} else {
    echo "<p style='color:red'>✗ فشل إنشاء ملف اختبار الكتابة.</p>";
}

echo "<p style='color:red; font-weight:bold; margin-top:30px;'>تنبيه أمني: يرجى حذف ملف info.php بمجرد الانتهاء من استخدامه!</p>";

echo "</div>";

// إظهار معلومات PHP الكاملة بطريقة آمنة
echo "<hr>";
echo "<h2 style='direction:rtl; font-family:Arial; padding:20px;'>معلومات PHP الكاملة (phpinfo)</h2>";
ob_start();
phpinfo();
$phpinfo = ob_get_clean();

// تنظيف مخرجات phpinfo
$phpinfo = preg_replace('%^.*<body>(.*)</body>.*$%ms', '$1', $phpinfo);
$phpinfo = str_replace('<table', '<table class="phpinfo" border="1" cellpadding="5" style="border-collapse:collapse;"', $phpinfo);

echo $phpinfo;
?>