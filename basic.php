<?php
// صفحة بسيطة جدًا للاختبار
?>
<!DOCTYPE html>
<html dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>نظام Eissa HR - صفحة اختبار</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 50px;
            background-color: #f0f0f0;
        }
        
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        
        h1 {
            color: #2c3e50;
        }
        
        p {
            color: #7f8c8d;
            margin-bottom: 20px;
        }
        
        .success {
            color: green;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>نظام Eissa HR</h1>
        <p class="success">تم تشغيل PHP بنجاح!</p>
        <p>هذه صفحة اختبار بسيطة للتأكد من عمل PHP على استضافتك.</p>
        <p>الوقت الحالي على الخادم: <?php echo date('Y-m-d H:i:s'); ?></p>
        <p>إصدار PHP: <?php echo PHP_VERSION; ?></p>
    </div>
</body>
</html>