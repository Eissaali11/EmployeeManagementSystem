<?php
/**
 * التحقق من متغيرات البيئة
 * هذا الملف يساعد في التأكد من إعداد المتغيرات البيئية اللازمة للنظام
 */

// تعريف المتغيرات المطلوبة وأوصافها
$required_variables = [
    'DATABASE_URL' => [
        'name' => 'رابط قاعدة البيانات',
        'description' => 'رابط الاتصال بقاعدة البيانات PostgreSQL بالتنسيق: postgresql://username:password@hostname:port/database',
        'example' => 'postgresql://dbuser:dbpass@localhost:5432/employee_db'
    ],
    'SECRET_KEY' => [
        'name' => 'المفتاح السري',
        'description' => 'مفتاح تشفير مستخدم لحماية الجلسات والبيانات الحساسة',
        'example' => 'a-random-string-of-characters-123456789'
    ],
    'FLASK_ENV' => [
        'name' => 'بيئة التشغيل',
        'description' => 'نوع بيئة التشغيل (development أو production)',
        'example' => 'production',
        'required' => false
    ],
    'TWILIO_ACCOUNT_SID' => [
        'name' => 'معرف حساب Twilio',
        'description' => 'معرف حساب Twilio المستخدم لإرسال الرسائل النصية',
        'example' => 'AC1234567890abcdef1234567890abcdef',
        'required' => false
    ],
    'TWILIO_AUTH_TOKEN' => [
        'name' => 'رمز مصادقة Twilio',
        'description' => 'رمز المصادقة لحساب Twilio',
        'example' => '1234567890abcdef1234567890abcdef',
        'required' => false
    ],
    'TWILIO_PHONE_NUMBER' => [
        'name' => 'رقم هاتف Twilio',
        'description' => 'رقم هاتف Twilio المستخدم لإرسال الرسائل النصية',
        'example' => '+15551234567',
        'required' => false
    ]
];

// وظيفة لعرض حالة المتغير
function displayVariableStatus($name, $var_info) {
    $value = getenv($name);
    $is_set = !empty($value);
    $is_required = isset($var_info['required']) ? $var_info['required'] : true;
    
    $status_class = $is_set ? 'success' : ($is_required ? 'danger' : 'warning');
    $status_icon = $is_set ? 'check-circle-fill' : 'exclamation-triangle-fill';
    $status_text = $is_set ? 'متوفر' : ($is_required ? 'مفقود (مطلوب)' : 'مفقود (اختياري)');
    
    echo "<div class='card mb-3'>\n";
    echo "    <div class='card-header bg-{$status_class} text-white d-flex justify-content-between align-items-center'>\n";
    echo "        <h3 class='h5 mb-0'>{$var_info['name']} ({$name})</h3>\n";
    echo "        <span><i class='bi bi-{$status_icon} me-1'></i>{$status_text}</span>\n";
    echo "    </div>\n";
    echo "    <div class='card-body'>\n";
    echo "        <p>{$var_info['description']}</p>\n";
    
    if ($is_set) {
        echo "        <div class='alert alert-success'>\n";
        echo "            <i class='bi bi-check-circle-fill me-2'></i>تم تعيين هذا المتغير بنجاح.\n";
        echo "        </div>\n";
    } else {
        echo "        <div class='alert alert-" . ($is_required ? 'danger' : 'warning') . "'>\n";
        echo "            <i class='bi bi-" . ($is_required ? 'x-circle-fill' : 'exclamation-triangle-fill') . " me-2'></i>\n";
        echo "            " . ($is_required ? 'هذا المتغير مطلوب ولم يتم تعيينه.' : 'هذا المتغير اختياري ولم يتم تعيينه.') . "\n";
        echo "        </div>\n";
        
        echo "        <div class='mb-3'>\n";
        echo "            <label class='form-label'>مثال:</label>\n";
        echo "            <input type='text' class='form-control' value='{$var_info['example']}' readonly>\n";
        echo "        </div>\n";
        
        if ($name === 'SECRET_KEY') {
            echo "        <button class='btn btn-sm btn-outline-primary' onclick='generateRandomKey()'>توليد مفتاح عشوائي</button>\n";
            echo "        <div id='random-key-output' class='mt-2'></div>\n";
        }
    }
    
    echo "    </div>\n";
    echo "</div>\n";
}

// عنوان الصفحة
echo "<!DOCTYPE html>\n";
echo "<html dir='rtl' lang='ar'>\n";
echo "<head>\n";
echo "    <meta charset='UTF-8'>\n";
echo "    <meta name='viewport' content='width=device-width, initial-scale=1.0'>\n";
echo "    <title>فحص متغيرات البيئة - نظام إدارة الموظفين</title>\n";
echo "    <link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.rtl.min.css'>\n";
echo "    <link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css'>\n";
echo "    <link rel='stylesheet' href='style.css'>\n";
echo "</head>\n";
echo "<body>\n";
echo "<div class='container'>\n";
echo "    <header class='text-center my-5'>\n";
echo "        <h1 class='main-title'>فحص متغيرات البيئة</h1>\n";
echo "        <p class='lead'>التحقق من إعداد المتغيرات البيئية اللازمة لنظام إدارة الموظفين</p>\n";
echo "    </header>\n";

echo "    <div class='row'>\n";
echo "        <div class='col-lg-8 mx-auto'>\n";

// فحص كل متغير وعرض حالته
$missing_required = 0;
foreach ($required_variables as $name => $info) {
    displayVariableStatus($name, $info);
    
    // حساب عدد المتغيرات المطلوبة المفقودة
    $is_required = isset($info['required']) ? $info['required'] : true;
    if ($is_required && empty(getenv($name))) {
        $missing_required++;
    }
}

// عرض الخلاصة والخطوات التالية
echo "        <div class='card shadow mb-4'>\n";
echo "            <div class='card-header bg-primary text-white'>\n";
echo "                <h2 class='h5 mb-0'><i class='bi bi-list-check me-2'></i>الخلاصة</h2>\n";
echo "            </div>\n";
echo "            <div class='card-body'>\n";

if ($missing_required > 0) {
    echo "                <div class='alert alert-danger'>\n";
    echo "                    <h4 class='alert-heading'>انتبه!</h4>\n";
    echo "                    <p>هناك {$missing_required} من المتغيرات المطلوبة غير معرفة. يجب تعريف هذه المتغيرات قبل تشغيل النظام.</p>\n";
    echo "                </div>\n";
    
    echo "                <h5>كيفية تعيين المتغيرات البيئية:</h5>\n";
    echo "                <ol>\n";
    echo "                    <li>قم بإنشاء ملف <code>.env</code> في المجلد الرئيسي للتطبيق</li>\n";
    echo "                    <li>أضف المتغيرات بتنسيق <code>VARIABLE_NAME=value</code> (متغير واحد في كل سطر)</li>\n";
    echo "                    <li>تأكد من عدم وجود مسافات قبل أو بعد علامة '='</li>\n";
    echo "                    <li>أعد تشغيل خادم الويب بعد تعديل الملف</li>\n";
    echo "                </ol>\n";
    
    echo "                <div class='bg-light p-3 rounded'>\n";
    echo "                    <code>DATABASE_URL=postgresql://username:password@hostname:port/database<br>\n";
    echo "SECRET_KEY=your-secure-random-key<br>\n";
    echo "FLASK_ENV=production</code>\n";
    echo "                </div>\n";
} else {
    echo "                <div class='alert alert-success'>\n";
    echo "                    <h4 class='alert-heading'>ممتاز!</h4>\n";
    echo "                    <p>جميع المتغيرات البيئية المطلوبة معرفة بشكل صحيح. يمكنك متابعة إعداد النظام.</p>\n";
    echo "                </div>\n";
}

echo "                <div class='text-center mt-4'>\n";
echo "                    <a href='setup.php' class='btn btn-primary'>\n";
echo "                        <i class='bi bi-arrow-left me-2'></i>العودة إلى إعداد النظام\n";
echo "                    </a>\n";
echo "                    <a href='index.html' class='btn btn-success ms-2'>\n";
echo "                        <i class='bi bi-house-door-fill me-2'></i>الصفحة الرئيسية\n";
echo "                    </a>\n";
echo "                </div>\n";
echo "            </div>\n";
echo "        </div>\n";

echo "        </div>\n";
echo "    </div>\n";

echo "    <footer class='text-center mt-5 mb-4'>\n";
echo "        <p>نظام إدارة الموظفين &copy; " . date('Y') . "</p>\n";
echo "    </footer>\n";
echo "</div>\n";

// JavaScript لتوليد مفتاح عشوائي
echo "<script>\n";
echo "function generateRandomKey() {\n";
echo "    const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*';\n";
echo "    let result = '';\n";
echo "    const charactersLength = characters.length;\n";
echo "    for (let i = 0; i < 32; i++) {\n";
echo "        result += characters.charAt(Math.floor(Math.random() * charactersLength));\n";
echo "    }\n";
echo "    \n";
echo "    const outputDiv = document.getElementById('random-key-output');\n";
echo "    outputDiv.innerHTML = `\n";
echo "        <div class='alert alert-info mt-3'>\n";
echo "            <p class='mb-2'>المفتاح العشوائي:</p>\n";
echo "            <input type='text' class='form-control' value='${result}' readonly onclick='this.select()'>\n";
echo "            <small class='text-muted'>انقر على المفتاح لتحديده، ثم انسخه واستخدمه في ملف .env</small>\n";
echo "        </div>\n";
echo "    `;\n";
echo "}\n";
echo "</script>\n";

echo "</body>\n";
echo "</html>";