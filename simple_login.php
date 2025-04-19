<?php
// صفحة تسجيل دخول بسيطة للغاية
session_start();

// التحقق مما إذا كان المستخدم قد قام بالفعل بتسجيل الدخول
if(isset($_SESSION['user_id'])) {
    header('Location: dashboard.php');
    exit;
}

$error_message = '';

// التحقق مما إذا كان النموذج قد تم إرساله
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $email = $_POST['email'] ?? '';
    $password = $_POST['password'] ?? '';
    
    if ($email === 'admin@example.com' && $password === 'admin123') {
        $_SESSION['user_id'] = 1;
        $_SESSION['user_name'] = 'مدير النظام';
        header('Location: dashboard.php');
        exit;
    } else {
        $error_message = 'البريد الإلكتروني أو كلمة المرور غير صحيحة';
    }
}
?>
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <title>تسجيل الدخول - نظام Eissa HR</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #1e2a38;
            margin: 0;
            padding: 20px;
            display: flex;
            height: 100vh;
        }
        
        .container {
            display: flex;
            width: 900px;
            margin: auto;
            background: #fff;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 0 20px rgba(0,0,0,0.2);
        }
        
        .info-section {
            flex: 1;
            background: linear-gradient(135deg, #1e3c72, #2a5298);
            color: white;
            padding: 40px;
        }
        
        .login-section {
            width: 350px;
            padding: 40px;
            background: #f9f9f9;
        }
        
        h1 {
            color: #3498db;
            margin-top: 0;
            margin-bottom: 30px;
        }
        
        h2 {
            color: white;
            margin-top: 0;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
        }
        
        input {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }
        
        button {
            width: 100%;
            padding: 12px;
            background: #3498db;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }
        
        button:hover {
            background: #2980b9;
        }
        
        .error {
            color: #e74c3c;
            margin-bottom: 15px;
        }
        
        .feature {
            margin-bottom: 20px;
            display: flex;
            align-items: center;
        }
        
        .feature-icon {
            margin-left: 15px;
            font-size: 24px;
        }
        
        .login-info {
            margin-top: 20px;
            background: #f0f0f0;
            padding: 10px;
            border-radius: 4px;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="info-section">
            <h2>نظام Eissa HR</h2>
            <p>نظام متكامل لإدارة الموارد البشرية مصمم خصيصًا للشركات السعودية</p>
            
            <div class="feature">
                <div class="feature-icon">👥</div>
                <div>
                    <h3>إدارة شاملة للموظفين</h3>
                    <p>سجلات كاملة للموظفين مع معلومات شخصية ومهنية</p>
                </div>
            </div>
            
            <div class="feature">
                <div class="feature-icon">📊</div>
                <div>
                    <h3>تقارير تحليلية</h3>
                    <p>رؤى دقيقة عن أداء الموظفين وتكاليف الموارد البشرية</p>
                </div>
            </div>
            
            <div class="feature">
                <div class="feature-icon">🚗</div>
                <div>
                    <h3>إدارة المركبات</h3>
                    <p>متابعة حالة مركبات الشركة والصيانة والمصاريف</p>
                </div>
            </div>
            
            <div class="feature">
                <div class="feature-icon">💵</div>
                <div>
                    <h3>إدارة الرواتب</h3>
                    <p>نظام متكامل لحساب الرواتب والبدلات</p>
                </div>
            </div>
        </div>
        
        <div class="login-section">
            <h1>تسجيل الدخول</h1>
            
            <?php if(!empty($error_message)): ?>
                <div class="error"><?php echo $error_message; ?></div>
            <?php endif; ?>
            
            <form method="post">
                <div class="form-group">
                    <label for="email">البريد الإلكتروني</label>
                    <input type="email" id="email" name="email" required>
                </div>
                
                <div class="form-group">
                    <label for="password">كلمة المرور</label>
                    <input type="password" id="password" name="password" required>
                </div>
                
                <button type="submit">تسجيل الدخول</button>
            </form>
            
            <div class="login-info">
                <strong>بيانات الدخول التجريبية:</strong><br>
                البريد الإلكتروني: admin@example.com<br>
                كلمة المرور: admin123
            </div>
        </div>
    </div>
</body>
</html>