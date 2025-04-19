<?php
// صفحة بسيطة تعمل على أي استضافة بدون أي متطلبات خاصة
?>
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>نظام إدارة الموظفين - صفحة اختبار</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f8f9fa;
            color: #333;
            text-align: center;
        }
        .container {
            max-width: 800px;
            margin: 40px auto;
            background-color: #fff;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: right;
        }
        h1 {
            color: #3498db;
            border-bottom: 2px solid #f1f1f1;
            padding-bottom: 10px;
            margin-bottom: 30px;
        }
        .info-box {
            background-color: #e8f4fd;
            border-right: 4px solid #3498db;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 4px;
        }
        .success {
            color: #28a745;
            font-weight: bold;
        }
        .info {
            margin-top: 30px;
            background-color: #f1f1f1;
            padding: 15px;
            border-radius: 4px;
        }
        .link-btn {
            display: inline-block;
            background-color: #3498db;
            color: white;
            padding: 10px 20px;
            margin: 10px;
            text-decoration: none;
            border-radius: 4px;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>نظام إدارة الموظفين</h1>
        
        <div class="info-box">
            <p class="success">✓ نجح عرض هذه الصفحة على استضافة Hostinger!</p>
            <p>هذه صفحة بسيطة لاختبار عمل PHP على استضافتك.</p>
        </div>
        
        <h2>روابط الوصول إلى النظام</h2>
        <div>
            <a href="home.html" class="link-btn">الصفحة الرئيسية</a>
            <a href="welcome.php" class="link-btn">صفحة الترحيب</a>
            <a href="login.php" class="link-btn">تسجيل الدخول</a>
        </div>
        
        <div class="info">
            <h3>معلومات النظام:</h3>
            <p>إصدار PHP: <?php echo PHP_VERSION; ?></p>
            <p>نظام التشغيل: <?php echo PHP_OS; ?></p>
            <p>الوقت الحالي على الخادم: <?php echo date('Y-m-d H:i:s'); ?></p>
        </div>
    </div>
</body>
</html>