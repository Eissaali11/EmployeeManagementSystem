<?php
// صفحة بسيطة للترحيب بالمستخدمين
?>
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>نظام إدارة الموظفين</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f7f9fc;
            margin: 0;
            padding: 0;
            color: #333;
            line-height: 1.6;
        }
        .container {
            max-width: 1000px;
            margin: 50px auto;
            padding: 30px;
            background-color: #fff;
            border-radius: 8px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        header {
            text-align: center;
            margin-bottom: 30px;
        }
        .logo {
            max-width: 150px;
            margin-bottom: 20px;
        }
        h1 {
            color: #2c3e50;
            font-size: 32px;
            margin-bottom: 10px;
        }
        .subtitle {
            color: #7f8c8d;
            font-size: 18px;
            margin-bottom: 30px;
        }
        .features {
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            margin: 40px 0;
        }
        .feature {
            flex-basis: 30%;
            background: #f8f9fa;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 6px;
            border-right: 4px solid #3498db;
            transition: transform 0.3s ease;
        }
        .feature:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .feature h3 {
            color: #3498db;
            margin-top: 0;
        }
        .btn {
            display: inline-block;
            background-color: #3498db;
            color: white;
            padding: 12px 25px;
            text-decoration: none;
            border-radius: 5px;
            font-weight: bold;
            transition: background-color 0.3s ease;
        }
        .btn:hover {
            background-color: #2980b9;
        }
        .database-status {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
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
        footer {
            text-align: center;
            margin-top: 50px;
            color: #7f8c8d;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <?php if (file_exists('static/img/logo.png')): ?>
                <img src="static/img/logo.png" alt="شعار الشركة" class="logo">
            <?php else: ?>
                <div style="font-size: 50px; color: #3498db; margin-bottom: 20px;">🏢</div>
            <?php endif; ?>
            <h1>نظام إدارة الموظفين</h1>
            <p class="subtitle">إدارة شؤون الموظفين والحضور والمركبات والمستندات</p>
        </header>
        
        <div class="features">
            <div class="feature">
                <h3>إدارة الموظفين</h3>
                <p>تسجيل بيانات الموظفين وإدارة شؤونهم بكفاءة وسهولة</p>
            </div>
            <div class="feature">
                <h3>الحضور والانصراف</h3>
                <p>سجلات الحضور والانصراف وإدارة الإجازات والغياب</p>
            </div>
            <div class="feature">
                <h3>إدارة المركبات</h3>
                <p>متابعة حالة المركبات والصيانة والفحوصات الدورية</p>
            </div>
            <div class="feature">
                <h3>المستندات</h3>
                <p>إدارة وثائق الموظفين والتنبيهات بمواعيد التجديد</p>
            </div>
            <div class="feature">
                <h3>الرواتب</h3>
                <p>حساب الرواتب وإصدار كشوفها بصيغة PDF</p>
            </div>
            <div class="feature">
                <h3>التقارير</h3>
                <p>تقارير متنوعة وإحصائيات لاتخاذ القرارات المناسبة</p>
            </div>
        </div>
        
        <div style="text-align: center; margin: 40px 0;">
            <a href="login.php" class="btn">تسجيل الدخول</a>
        </div>
        
        <div class="database-status">
            <h3>حالة قاعدة البيانات:</h3>
            <?php
            // اختبار الاتصال بقاعدة البيانات
            try {
                $host = 'localhost';
                $db   = 'u800258840_eissa';
                $user = 'u800258840_eissa';
                $pass = 'Eisa2012@#';
                
                $conn = new PDO("mysql:host=$host;dbname=$db;charset=utf8mb4", $user, $pass);
                $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
                echo "<p class='success'>✓ تم الاتصال بقاعدة البيانات بنجاح.</p>";
                
                // التحقق من وجود الجداول
                $stmt = $conn->query("SHOW TABLES");
                $tables = $stmt->fetchAll(PDO::FETCH_COLUMN);
                
                if (count($tables) > 0) {
                    echo "<p><strong>الجداول الموجودة:</strong> " . count($tables) . " جدول</p>";
                    echo "<ul>";
                    foreach (array_slice($tables, 0, 5) as $table) {
                        echo "<li>" . htmlspecialchars($table) . "</li>";
                    }
                    if (count($tables) > 5) {
                        echo "<li>... والمزيد</li>";
                    }
                    echo "</ul>";
                } else {
                    echo "<p class='warning'>⚠️ لا توجد جداول في قاعدة البيانات حتى الآن.</p>";
                }
                
            } catch(PDOException $e) {
                echo "<p class='error'>✗ فشل الاتصال بقاعدة البيانات: " . htmlspecialchars($e->getMessage()) . "</p>";
            }
            ?>
        </div>
        
        <div style="margin-top: 30px; background-color: #f5f5f5; padding: 15px; border-radius: 5px;">
            <h3>حالة النظام:</h3>
            <p>الإصدار الحالي: 1.0</p>
            <p>تاريخ التثبيت: <?php echo date("Y-m-d"); ?></p>
            <p>معلومات الخادم: <?php echo PHP_OS . ' / PHP ' . PHP_VERSION; ?></p>
        </div>
        
        <footer>
            <p>نظام إدارة الموظفين &copy; <?php echo date("Y"); ?> شركة التقنية المتطورة - جميع الحقوق محفوظة</p>
        </footer>
    </div>
</body>
</html>