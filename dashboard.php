<?php
// لوحة التحكم البسيطة
session_start();

// التحقق من تسجيل دخول المستخدم
if(!isset($_SESSION['user_id'])) {
    header('Location: login.php');
    exit;
}

// الحصول على معلومات المستخدم من الجلسة
$user_id = $_SESSION['user_id'];
$user_name = $_SESSION['user_name'] ?? 'مستخدم';
$user_email = $_SESSION['user_email'] ?? '';
$user_role = $_SESSION['user_role'] ?? 'user';

// تسجيل الخروج
if(isset($_GET['logout'])) {
    // تدمير الجلسة
    session_unset();
    session_destroy();
    
    // توجيه المستخدم إلى صفحة تسجيل الدخول
    header('Location: login.php');
    exit;
}

// استدعاء بيانات النظام
try {
    // الاتصال بقاعدة البيانات
    $host = 'localhost';
    $db   = 'u800258840_eissa';
    $user = 'u800258840_eissa';
    $pass = 'Eisa2012@#';
    
    $conn = new PDO("mysql:host=$host;dbname=$db;charset=utf8mb4", $user, $pass);
    $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    
    // جلب بيانات احصائية (محاكاة)
    $database_connected = true;
    
    // التحقق من وجود الجداول الأساسية
    $tables_info = [];
    $core_tables = ['user', 'department', 'employee', 'attendance', 'document', 'vehicle'];
    
    foreach ($core_tables as $table) {
        $stmt = $conn->query("SHOW TABLES LIKE '$table'");
        $tables_info[$table] = $stmt->rowCount() > 0;
    }
    
    // محاولة استعلام من الجداول الموجودة
    $stats = [
        'employees' => 0,
        'departments' => 0,
        'attendance' => 0,
        'documents' => 0,
        'vehicles' => 0
    ];
    
    if ($tables_info['employee']) {
        $stmt = $conn->query("SELECT COUNT(*) FROM employee");
        $stats['employees'] = $stmt->fetchColumn();
    }
    
    if ($tables_info['department']) {
        $stmt = $conn->query("SELECT COUNT(*) FROM department");
        $stats['departments'] = $stmt->fetchColumn();
    }
    
    if ($tables_info['attendance']) {
        $stmt = $conn->query("SELECT COUNT(*) FROM attendance");
        $stats['attendance'] = $stmt->fetchColumn();
    }
    
    if ($tables_info['document']) {
        $stmt = $conn->query("SELECT COUNT(*) FROM document");
        $stats['documents'] = $stmt->fetchColumn();
    }
    
    if ($tables_info['vehicle']) {
        $stmt = $conn->query("SELECT COUNT(*) FROM vehicle");
        $stats['vehicles'] = $stmt->fetchColumn();
    }
    
} catch(PDOException $e) {
    // خطأ في الاتصال بقاعدة البيانات
    $database_connected = false;
    $db_error = $e->getMessage();
    
    // تعيين بيانات افتراضية للعرض
    $stats = [
        'employees' => '—',
        'departments' => '—',
        'attendance' => '—',
        'documents' => '—',
        'vehicles' => '—'
    ];
}
?>
<!DOCTYPE html>
<html dir="rtl" lang="ar">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>لوحة التحكم - نظام إدارة الموظفين</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f7f9fc;
            margin: 0;
            padding: 0;
            color: #333;
        }
        .dashboard {
            display: flex;
            min-height: 100vh;
        }
        .sidebar {
            width: 250px;
            background-color: #2c3e50;
            color: #ecf0f1;
            padding: 20px 0;
        }
        .main-content {
            flex: 1;
            padding: 20px;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            padding-bottom: 10px;
            border-bottom: 1px solid #eee;
        }
        .user-info {
            display: flex;
            align-items: center;
        }
        .user-avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            background-color: #3498db;
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-left: 10px;
            font-weight: bold;
        }
        .welcome-text small {
            color: #7f8c8d;
        }
        .logo {
            text-align: center;
            padding: 20px 0;
            margin-bottom: 20px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .logo-text {
            font-size: 20px;
            font-weight: bold;
            color: #3498db;
        }
        .nav-menu {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        .nav-item {
            padding: 10px 20px;
            border-right: 3px solid transparent;
            transition: all 0.3s;
        }
        .nav-item:hover, .nav-item.active {
            background-color: rgba(255,255,255,0.1);
            border-right-color: #3498db;
        }
        .nav-item a {
            color: #ecf0f1;
            text-decoration: none;
            display: block;
        }
        .dashboard-title {
            color: #2c3e50;
            margin-bottom: 30px;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background-color: #fff;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            transition: transform 0.3s;
        }
        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .stat-number {
            font-size: 28px;
            font-weight: bold;
            color: #3498db;
            margin: 10px 0;
        }
        .stat-title {
            color: #7f8c8d;
            font-size: 16px;
        }
        .stat-icon {
            font-size: 24px;
            color: #3498db;
        }
        .quick-actions {
            background-color: #fff;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            margin-bottom: 30px;
        }
        .action-buttons {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        .action-btn {
            background-color: #f8f9fa;
            border: none;
            border-radius: 4px;
            padding: 12px;
            text-align: center;
            color: #333;
            text-decoration: none;
            transition: background-color 0.3s;
            font-size: 15px;
        }
        .action-btn:hover {
            background-color: #e9ecef;
        }
        .recent-activities {
            background-color: #fff;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        .activity-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        .activity-item {
            padding: 12px 0;
            border-bottom: 1px solid #f1f1f1;
        }
        .activity-item:last-child {
            border-bottom: none;
        }
        .activity-icon {
            display: inline-block;
            width: 30px;
            height: 30px;
            background-color: #e1f5fe;
            color: #03a9f4;
            border-radius: 50%;
            text-align: center;
            line-height: 30px;
            margin-left: 10px;
        }
        .activity-text {
            display: inline-block;
            vertical-align: middle;
        }
        .activity-time {
            color: #7f8c8d;
            font-size: 14px;
            margin-right: 10px;
        }
        .logout-btn {
            display: block;
            margin-top: 30px;
            text-align: center;
            background-color: rgba(231, 76, 60, 0.1);
            color: #e74c3c;
            padding: 10px;
            border-radius: 4px;
            text-decoration: none;
            transition: background-color 0.3s;
        }
        .logout-btn:hover {
            background-color: rgba(231, 76, 60, 0.2);
        }
        .db-status {
            margin-top: 20px;
            padding: 15px;
            border-radius: 5px;
        }
        .db-status.connected {
            background-color: #d4edda;
            color: #155724;
        }
        .db-status.disconnected {
            background-color: #f8d7da;
            color: #721c24;
        }
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="sidebar">
            <div class="logo">
                <div class="logo-text">نظام إدارة الموظفين</div>
            </div>
            
            <ul class="nav-menu">
                <li class="nav-item active"><a href="dashboard.php">لوحة التحكم</a></li>
                <li class="nav-item"><a href="#">الموظفين</a></li>
                <li class="nav-item"><a href="#">الأقسام</a></li>
                <li class="nav-item"><a href="#">الحضور والانصراف</a></li>
                <li class="nav-item"><a href="#">الرواتب</a></li>
                <li class="nav-item"><a href="#">المستندات</a></li>
                <li class="nav-item"><a href="#">المركبات</a></li>
                <li class="nav-item"><a href="#">التقارير</a></li>
                <li class="nav-item"><a href="#">الإعدادات</a></li>
            </ul>
            
            <a href="dashboard.php?logout=1" class="logout-btn">تسجيل الخروج</a>
        </div>
        
        <div class="main-content">
            <div class="header">
                <div class="user-info">
                    <div class="user-avatar"><?php echo substr($user_name, 0, 1); ?></div>
                    <div class="welcome-text">
                        <div>مرحباً، <?php echo htmlspecialchars($user_name); ?></div>
                        <small><?php echo htmlspecialchars($user_email); ?></small>
                    </div>
                </div>
                
                <div class="date">
                    <?php echo date("Y/m/d"); ?>
                </div>
            </div>
            
            <h1 class="dashboard-title">لوحة التحكم</h1>
            
            <?php if ($database_connected): ?>
                <div class="db-status connected">
                    ✓ قاعدة البيانات متصلة وتعمل بشكل صحيح
                </div>
            <?php else: ?>
                <div class="db-status disconnected">
                    ✗ فشل الاتصال بقاعدة البيانات: <?php echo htmlspecialchars($db_error ?? 'خطأ غير معروف'); ?>
                </div>
            <?php endif; ?>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-icon">👨‍💼</div>
                    <div class="stat-number"><?php echo $stats['employees']; ?></div>
                    <div class="stat-title">الموظفين</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">🏢</div>
                    <div class="stat-number"><?php echo $stats['departments']; ?></div>
                    <div class="stat-title">الأقسام</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">📅</div>
                    <div class="stat-number"><?php echo $stats['attendance']; ?></div>
                    <div class="stat-title">سجلات الحضور</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">📄</div>
                    <div class="stat-number"><?php echo $stats['documents']; ?></div>
                    <div class="stat-title">المستندات</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">🚗</div>
                    <div class="stat-number"><?php echo $stats['vehicles']; ?></div>
                    <div class="stat-title">المركبات</div>
                </div>
            </div>
            
            <div class="quick-actions">
                <h2>إجراءات سريعة</h2>
                <div class="action-buttons">
                    <a href="#" class="action-btn">إضافة موظف جديد</a>
                    <a href="#" class="action-btn">تسجيل حضور</a>
                    <a href="#" class="action-btn">إضافة قسم</a>
                    <a href="#" class="action-btn">صرف راتب</a>
                    <a href="#" class="action-btn">إضافة مستند</a>
                    <a href="#" class="action-btn">إنشاء تقرير</a>
                </div>
            </div>
            
            <div class="recent-activities">
                <h2>النشاطات الأخيرة</h2>
                <ul class="activity-list">
                    <li class="activity-item">
                        <span class="activity-icon">👤</span>
                        <span class="activity-text">تم تسجيل الدخول إلى النظام</span>
                        <span class="activity-time">الآن</span>
                    </li>
                    <li class="activity-item">
                        <span class="activity-icon">📊</span>
                        <span class="activity-text">تم الاطلاع على لوحة التحكم</span>
                        <span class="activity-time">الآن</span>
                    </li>
                    <li class="activity-item">
                        <span class="activity-icon">⚙️</span>
                        <span class="activity-text">بدء تهيئة النظام للعمل مع استضافة Hostinger</span>
                        <span class="activity-time">اليوم <?php echo date("H:i"); ?></span>
                    </li>
                </ul>
            </div>
        </div>
    </div>
</body>
</html>