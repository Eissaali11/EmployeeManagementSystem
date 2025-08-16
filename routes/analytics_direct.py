"""
مسار مباشر للتحليل المالي
"""
from flask import Blueprint, render_template_string

analytics_direct_bp = Blueprint('analytics_direct', __name__, url_prefix='/accounting/analytics')

@analytics_direct_bp.route('/')
def dashboard():
    """لوحة التحليل المالي"""
    
    # قالب HTML مباشر
    template = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>التحليل المالي الذكي</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        .card { box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }
        .bg-gradient-primary { background: linear-gradient(45deg, #007bff, #6610f2); }
        .bg-gradient-success { background: linear-gradient(45deg, #28a745, #20c997); }
        .bg-gradient-danger { background: linear-gradient(45deg, #dc3545, #fd7e14); }
        .bg-gradient-info { background: linear-gradient(45deg, #17a2b8, #6f42c1); }
    </style>
</head>
<body>
    <div class="container-fluid mt-4">
        <div class="row">
            <div class="col-12">
                <div class="card shadow-sm mb-4">
                    <div class="card-header bg-gradient-primary text-white">
                        <h4 class="mb-0">
                            <i class="fas fa-chart-line me-2"></i>
                            التحليل المالي الذكي
                        </h4>
                    </div>
                    <div class="card-body">
                        <!-- المؤشرات الرئيسية -->
                        <div class="row mb-4">
                            <div class="col-md-3">
                                <div class="card bg-gradient-success text-white">
                                    <div class="card-body text-center">
                                        <h5>إجمالي الإيرادات</h5>
                                        <h2>450,000 ريال</h2>
                                        <small>هذا العام</small>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="card bg-gradient-danger text-white">
                                    <div class="card-body text-center">
                                        <h5>إجمالي المصروفات</h5>
                                        <h2>380,000 ريال</h2>
                                        <small>هذا العام</small>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="card bg-gradient-info text-white">
                                    <div class="card-body text-center">
                                        <h5>صافي الربح</h5>
                                        <h2>70,000 ريال</h2>
                                        <small>هذا العام</small>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-3">
                                <div class="card bg-gradient-primary text-white">
                                    <div class="card-body text-center">
                                        <h5>معدل الربحية</h5>
                                        <h2>15.6%</h2>
                                        <small>من الإيرادات</small>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- الرسوم البيانية -->
                        <div class="row">
                            <div class="col-md-8">
                                <div class="card">
                                    <div class="card-header">
                                        <h6 class="mb-0">الإيرادات والمصروفات الشهرية</h6>
                                    </div>
                                    <div class="card-body">
                                        <canvas id="revenueChart" width="400" height="200"></canvas>
                                    </div>
                                </div>
                            </div>
                            <div class="col-md-4">
                                <div class="card">
                                    <div class="card-header">
                                        <h6 class="mb-0">توزيع المصروفات</h6>
                                    </div>
                                    <div class="card-body">
                                        <canvas id="expenseChart" width="200" height="200"></canvas>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- تحليل الأقسام -->
                        <div class="row mt-4">
                            <div class="col-12">
                                <div class="card">
                                    <div class="card-header">
                                        <h6 class="mb-0">أداء الأقسام</h6>
                                    </div>
                                    <div class="card-body">
                                        <div class="table-responsive">
                                            <table class="table table-striped">
                                                <thead class="table-dark">
                                                    <tr>
                                                        <th>القسم</th>
                                                        <th>الإيرادات</th>
                                                        <th>المصروفات</th>
                                                        <th>صافي الربح</th>
                                                        <th>معدل الربحية</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    <tr>
                                                        <td>المبيعات</td>
                                                        <td>180,000 ريال</td>
                                                        <td>120,000 ريال</td>
                                                        <td class="text-success">60,000 ريال</td>
                                                        <td class="text-success">33.3%</td>
                                                    </tr>
                                                    <tr>
                                                        <td>التسويق</td>
                                                        <td>120,000 ريال</td>
                                                        <td>95,000 ريال</td>
                                                        <td class="text-success">25,000 ريال</td>
                                                        <td class="text-success">20.8%</td>
                                                    </tr>
                                                    <tr>
                                                        <td>الإدارة</td>
                                                        <td>80,000 ريال</td>
                                                        <td>85,000 ريال</td>
                                                        <td class="text-danger">-5,000 ريال</td>
                                                        <td class="text-danger">-6.3%</td>
                                                    </tr>
                                                    <tr>
                                                        <td>المحاسبة</td>
                                                        <td>70,000 ريال</td>
                                                        <td>80,000 ريال</td>
                                                        <td class="text-danger">-10,000 ريال</td>
                                                        <td class="text-danger">-14.3%</td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- التنبؤات -->
                        <div class="row mt-4">
                            <div class="col-12">
                                <div class="card">
                                    <div class="card-header">
                                        <h6 class="mb-0">
                                            <i class="fas fa-brain me-2"></i>
                                            التنبؤات المالية الذكية
                                        </h6>
                                    </div>
                                    <div class="card-body">
                                        <div class="row">
                                            <div class="col-md-4">
                                                <div class="alert alert-info">
                                                    <h6>التنبؤ للشهر القادم</h6>
                                                    <p><strong>الإيرادات المتوقعة:</strong> 48,000 ريال</p>
                                                    <p><strong>المصروفات المتوقعة:</strong> 39,000 ريال</p>
                                                    <p><strong>الربح المتوقع:</strong> 9,000 ريال</p>
                                                </div>
                                            </div>
                                            <div class="col-md-8">
                                                <canvas id="predictionChart" width="600" height="200"></canvas>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- مكتبات الرسوم البيانية -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
        // الإيرادات والمصروفات الشهرية
        const revenueCtx = document.getElementById('revenueChart').getContext('2d');
        new Chart(revenueCtx, {
            type: 'line',
            data: {
                labels: ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو'],
                datasets: [{
                    label: 'الإيرادات',
                    data: [35000, 42000, 38000, 45000, 41000, 47000],
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    tension: 0.4
                }, {
                    label: 'المصروفات',
                    data: [28000, 32000, 30000, 35000, 33000, 37000],
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'الأداء المالي الشهري'
                    }
                }
            }
        });

        // توزيع المصروفات
        const expenseCtx = document.getElementById('expenseChart').getContext('2d');
        new Chart(expenseCtx, {
            type: 'pie',
            data: {
                labels: ['رواتب', 'مركبات', 'تشغيل', 'أخرى'],
                datasets: [{
                    data: [150000, 120000, 80000, 30000],
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.8)',
                        'rgba(54, 162, 235, 0.8)',
                        'rgba(255, 205, 86, 0.8)',
                        'rgba(75, 192, 192, 0.8)'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });

        // التنبؤات
        const predictionCtx = document.getElementById('predictionChart').getContext('2d');
        new Chart(predictionCtx, {
            type: 'line',
            data: {
                labels: ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو', 'يوليو (متوقع)', 'أغسطس (متوقع)'],
                datasets: [{
                    label: 'البيانات الفعلية',
                    data: [35000, 42000, 38000, 45000, 41000, 47000, null, null],
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)'
                }, {
                    label: 'التنبؤات',
                    data: [null, null, null, null, null, 47000, 48000, 49500],
                    borderColor: 'rgb(255, 159, 64)',
                    backgroundColor: 'rgba(255, 159, 64, 0.2)',
                    borderDash: [5, 5]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: 'التنبؤات المالية للأشهر القادمة'
                    }
                }
            }
        });
    </script>
</body>
</html>
    """
    
    return render_template_string(template)