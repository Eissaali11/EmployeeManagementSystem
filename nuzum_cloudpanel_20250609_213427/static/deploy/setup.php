<?php
/**
 * سكريبت تثبيت نظام إدارة الموظفين
 * يستخدم هذا الملف لتهيئة البيئة عند استضافة النظام
 */

// تعريف متغيرات التكوين
$config = [
    'app_name' => 'نظام إدارة الموظفين',
    'version' => '1.0.0',
    'min_php_version' => '7.4.0',
    'required_extensions' => ['pdo', 'pdo_pgsql', 'json', 'mbstring', 'zip']
];

// تخزين نتائج الفحص
$results = [];

/**
 * عرض الرأس
 */
function displayHeader() {
    global $config;
    echo "<!DOCTYPE html>\n";
    echo "<html dir='rtl' lang='ar'>\n";
    echo "<head>\n";
    echo "    <meta charset='UTF-8'>\n";
    echo "    <meta name='viewport' content='width=device-width, initial-scale=1.0'>\n";
    echo "    <title>{$config['app_name']} - تثبيت النظام</title>\n";
    echo "    <link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css'>\n";
    echo "    <link rel='stylesheet' href='style.css'>\n";
    echo "</head>\n";
    echo "<body>\n";
    echo "<div class='container'>\n";
    echo "    <header class='text-center my-5'>\n";
    echo "        <h1 class='main-title'>{$config['app_name']}</h1>\n";
    echo "        <p class='lead'>أداة تثبيت النظام - الإصدار {$config['version']}</p>\n";
    echo "    </header>\n";
}

/**
 * عرض التذييل
 */
function displayFooter() {
    echo "    <footer class='text-center mt-5 mb-4'>\n";
    echo "        <p>نظام إدارة الموظفين &copy; " . date('Y') . "</p>\n";
    echo "    </footer>\n";
    echo "</div>\n";
    echo "<script src='https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js'></script>\n";
    echo "</body>\n";
    echo "</html>\n";
}

/**
 * عرض رسالة
 */
function displayMessage($message, $type = 'info') {
    echo "<div class='alert alert-{$type}' role='alert'>{$message}</div>";
}

/**
 * فحص إصدار PHP
 */
function checkPhpVersion() {
    global $config;
    $current_version = phpversion();
    $min_version = $config['min_php_version'];
    
    if (version_compare($current_version, $min_version, '>=')) {
        return [
            'status' => true,
            'message' => "إصدار PHP ({$current_version}) يلبي الحد الأدنى المطلوب ({$min_version})"
        ];
    } else {
        return [
            'status' => false,
            'message' => "إصدار PHP ({$current_version}) أقل من الحد الأدنى المطلوب ({$min_version})"
        ];
    }
}

/**
 * فحص امتدادات PHP المطلوبة
 */
function checkExtensions() {
    global $config;
    $missing = [];
    $loaded = [];
    
    foreach ($config['required_extensions'] as $ext) {
        if (!extension_loaded($ext)) {
            $missing[] = $ext;
        } else {
            $loaded[] = $ext;
        }
    }
    
    if (empty($missing)) {
        return [
            'status' => true,
            'message' => "جميع الامتدادات المطلوبة متوفرة: " . implode(', ', $loaded)
        ];
    } else {
        return [
            'status' => false,
            'message' => "بعض الامتدادات المطلوبة غير متوفرة: " . implode(', ', $missing)
        ];
    }
}

/**
 * فحص أذونات الملفات
 */
function checkPermissions() {
    $dirs_to_check = [
        '.' => 'المجلد الرئيسي',
        './static' => 'مجلد الملفات الثابتة',
        './templates' => 'مجلد القوالب'
    ];
    
    $issues = [];
    
    foreach ($dirs_to_check as $dir => $name) {
        if (!file_exists($dir)) {
            $issues[] = "المجلد {$name} ({$dir}) غير موجود";
        } elseif (!is_writable($dir)) {
            $issues[] = "المجلد {$name} ({$dir}) غير قابل للكتابة";
        }
    }
    
    if (empty($issues)) {
        return [
            'status' => true,
            'message' => "جميع المجلدات موجودة وقابلة للكتابة"
        ];
    } else {
        return [
            'status' => false,
            'message' => "مشاكل في الأذونات:<br>" . implode('<br>', $issues)
        ];
    }
}

/**
 * محاولة الاتصال بقاعدة البيانات
 */
function checkDatabase() {
    // التحقق من توفر متغيرات البيئة
    $db_host = getenv('PGHOST') ?: '';
    $db_name = getenv('PGDATABASE') ?: '';
    $db_user = getenv('PGUSER') ?: '';
    $db_pass = getenv('PGPASSWORD') ?: '';
    $db_port = getenv('PGPORT') ?: 5432;
    
    // التحقق من وجود جميع المعلومات المطلوبة
    if (empty($db_host) || empty($db_name) || empty($db_user)) {
        return [
            'status' => false,
            'message' => "معلومات الاتصال بقاعدة البيانات غير مكتملة"
        ];
    }
    
    // محاولة الاتصال
    try {
        $dsn = "pgsql:host={$db_host};port={$db_port};dbname={$db_name}";
        $conn = new PDO($dsn, $db_user, $db_pass);
        $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
        
        return [
            'status' => true,
            'message' => "تم الاتصال بقاعدة البيانات بنجاح"
        ];
    } catch (PDOException $e) {
        return [
            'status' => false,
            'message' => "فشل الاتصال بقاعدة البيانات: " . $e->getMessage()
        ];
    }
}

/**
 * التحقق من متغيرات البيئة
 */
function checkEnvironment() {
    $required_vars = [
        'DATABASE_URL' => 'رابط قاعدة البيانات',
        'SECRET_KEY' => 'المفتاح السري'
    ];
    
    $missing = [];
    
    foreach ($required_vars as $var => $desc) {
        if (empty(getenv($var))) {
            $missing[] = "{$desc} ({$var})";
        }
    }
    
    if (empty($missing)) {
        return [
            'status' => true,
            'message' => "جميع متغيرات البيئة المطلوبة متوفرة"
        ];
    } else {
        return [
            'status' => false,
            'message' => "بعض متغيرات البيئة المطلوبة غير متوفرة: " . implode(', ', $missing)
        ];
    }
}

/**
 * عرض نتائج الفحص
 */
function displayResults($results) {
    echo "<div class='card shadow mb-4'>\n";
    echo "    <div class='card-header bg-primary text-white'>\n";
    echo "        <h2 class='h5 mb-0'>نتائج فحص النظام</h2>\n";
    echo "    </div>\n";
    echo "    <div class='card-body'>\n";
    
    $all_passed = true;
    
    foreach ($results as $test => $result) {
        $status_class = $result['status'] ? 'success' : 'danger';
        $status_icon = $result['status'] ? 'check-circle-fill' : 'x-circle-fill';
        $all_passed = $all_passed && $result['status'];
        
        echo "<div class='alert alert-{$status_class} mb-3'>\n";
        echo "    <i class='bi bi-{$status_icon} me-2'></i>";
        echo "    <strong>{$test}:</strong> {$result['message']}\n";
        echo "</div>\n";
    }
    
    if ($all_passed) {
        echo "<div class='alert alert-success'>\n";
        echo "    <h4 class='alert-heading'>تهانينا!</h4>\n";
        echo "    <p>النظام جاهز للتثبيت. يمكنك المتابعة بالضغط على زر \"تثبيت النظام\" أدناه.</p>\n";
        echo "</div>\n";
        echo "<div class='text-center'>\n";
        echo "    <a href='index.html' class='btn btn-success btn-lg'>\n";
        echo "        <i class='bi bi-arrow-right-circle-fill me-2'></i>متابعة التثبيت\n";
        echo "    </a>\n";
        echo "</div>\n";
    } else {
        echo "<div class='alert alert-warning'>\n";
        echo "    <h4 class='alert-heading'>انتبه!</h4>\n";
        echo "    <p>هناك بعض المشاكل التي تحتاج إلى معالجة قبل متابعة التثبيت.</p>\n";
        echo "</div>\n";
        echo "<div class='text-center'>\n";
        echo "    <a href='setup.php' class='btn btn-primary'>\n";
        echo "        <i class='bi bi-arrow-clockwise me-2'></i>إعادة الفحص\n";
        echo "    </a>\n";
        echo "</div>\n";
    }
    
    echo "    </div>\n";
    echo "</div>\n";
}

// تنفيذ الفحوصات
$results['فحص إصدار PHP'] = checkPhpVersion();
$results['فحص امتدادات PHP'] = checkExtensions();
$results['فحص أذونات الملفات'] = checkPermissions();
$results['فحص الاتصال بقاعدة البيانات'] = checkDatabase();
$results['فحص متغيرات البيئة'] = checkEnvironment();

// عرض الصفحة
displayHeader();
displayResults($results);
displayFooter();