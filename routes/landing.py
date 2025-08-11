from flask import Blueprint, render_template
from models import Employee, Vehicle, Department, User, Salary

landing_bp = Blueprint('landing', __name__)

@landing_bp.route('/nuzum')
def index():
    """صفحة هبوط نظام نُظم - عرض المواصفات والإمكانيات"""
    
    # إحصائيات النظام
    stats = {
        'employees': Employee.query.count(),
        'vehicles': Vehicle.query.count(), 
        'departments': Department.query.count(),
        'users': User.query.count(),
        'salary_records': Salary.query.count()
    }
    
    # ميزات النظام
    features = [
        {
            'title': 'إدارة الموظفين',
            'description': 'نظام شامل لإدارة بيانات الموظفين مع تتبع المستندات وانتهاء الصلاحيات',
            'icon': 'fas fa-users',
            'capabilities': [
                'إضافة وتعديل بيانات الموظفين الشخصية والوظيفية',
                'إدارة المستندات مع تنبيهات انتهاء الصلاحية',
                'رفع صور الهوية والملف الشخصي',
                'استيراد وتصدير البيانات من/إلى Excel',
                'نظام بحث متقدم وفلترة',
                'تتبع تاريخ التوظيف والعقود'
            ]
        },
        {
            'title': 'إدارة المركبات',
            'description': 'نظام متكامل لإدارة أسطول المركبات وتتبع العمليات',
            'icon': 'fas fa-car',
            'capabilities': [
                'تسجيل وإدارة بيانات المركبات',
                'نظام تسليم واستقبال المركبات',
                'تتبع مستندات المركبة (رخصة، تأمين، استمارة)',
                'إدارة ورش الصيانة والإصلاحات',
                'فحوصات السلامة الخارجية مع الصور',
                'تقارير تفصيلية للمركبات والعمليات'
            ]
        },
        {
            'title': 'نظام الحضور والانصراف',
            'description': 'تتبع دقيق لحضور الموظفين مع حساب الإضافي والخصم',
            'icon': 'fas fa-clock',
            'capabilities': [
                'تسجيل الحضور والانصراف اليومي',
                'حساب ساعات العمل الإضافية',
                'تقارير شهرية وأسبوعية مفصلة',
                'دعم التقويم الهجري والميلادي',
                'تتبع الغياب والإجازات',
                'إحصائيات متقدمة للأداء'
            ]
        },
        {
            'title': 'إدارة الرواتب',
            'description': 'نظام محاسبي متكامل لحساب ومعالجة رواتب الموظفين',
            'icon': 'fas fa-money-bill-wave',
            'capabilities': [
                'حساب الراتب الأساسي والبدلات',
                'إدارة الخصومات والاستقطاعات',
                'معالجة دفعية للرواتب',
                'تقارير شهرية مفصلة',
                'تصدير كشوف الرواتب PDF',
                'تتبع تاريخ الدفع والمستحقات'
            ]
        },
        {
            'title': 'إدارة الأقسام',
            'description': 'تنظيم هيكلي للإدارات والأقسام المختلفة',
            'icon': 'fas fa-sitemap',
            'capabilities': [
                'إنشاء وإدارة الأقسام والإدارات',
                'تحديد المديرين والمسؤولين',
                'ربط الموظفين بالأقسام',
                'هيكل تنظيمي واضح',
                'تقارير على مستوى القسم',
                'إحصائيات الأداء الإداري'
            ]
        },
        {
            'title': 'إدارة المستخدمين والصلاحيات',
            'description': 'نظام أمان متقدم لإدارة المستخدمين والصلاحيات',
            'icon': 'fas fa-shield-alt',
            'capabilities': [
                'إنشاء حسابات مستخدمين متعددة',
                'نظام أدوار وصلاحيات مرن',
                'تسجيل نشاط المستخدمين',
                'تشفير كلمات المرور',
                'جلسات آمنة ومحمية',
                'تدقيق العمليات والتغييرات'
            ]
        },
        {
            'title': 'التقارير والإحصائيات',
            'description': 'تقارير شاملة ومرئيات بيانية للمساعدة في اتخاذ القرارات',
            'icon': 'fas fa-chart-bar',
            'capabilities': [
                'تقارير PDF احترافية',
                'تصدير Excel للبيانات',
                'رسوم بيانية تفاعلية',
                'تقارير مخصصة حسب الفترة',
                'إحصائيات الأداء الشاملة',
                'تحليل البيانات المتقدم'
            ]
        },
        {
            'title': 'إدارة الأجهزة المحمولة',
            'description': 'تتبع وإدارة الأجهزة المحمولة المخصصة للموظفين',
            'icon': 'fas fa-mobile-alt',
            'capabilities': [
                'تسجيل تفاصيل الأجهزة والـ IMEI',
                'ربط الأجهزة بالموظفين',
                'تتبع حالة الجهاز والصيانة',
                'إدارة أرقام الهواتف',
                'تقارير استخدام الأجهزة',
                'نظام بحث متقدم للأجهزة'
            ]
        }
    ]
    
    # المزايا التنافسية
    advantages = [
        {
            'title': 'واجهة عربية كاملة',
            'description': 'تصميم يدعم الكتابة من اليمين لليسار مع خطوط عربية واضحة',
            'icon': 'fas fa-language'
        },
        {
            'title': 'نظام أمان متقدم',
            'description': 'حماية البيانات بأعلى معايير الأمان مع تشفير المعلومات الحساسة',
            'icon': 'fas fa-lock'
        },
        {
            'title': 'تقارير احترافية',
            'description': 'تقارير PDF وExcel بتصميم احترافي يدعم الخطوط العربية',
            'icon': 'fas fa-file-pdf'
        },
        {
            'title': 'سهولة الاستخدام',
            'description': 'واجهة بديهية وسهلة التعلم لجميع مستويات المستخدمين',
            'icon': 'fas fa-mouse-pointer'
        },
        {
            'title': 'مرونة في التخصيص',
            'description': 'إمكانية تخصيص النظام حسب احتياجات كل مؤسسة',
            'icon': 'fas fa-cogs'
        },
        {
            'title': 'دعم فني مستمر',
            'description': 'فريق دعم فني متخصص لضمان استمرارية العمل',
            'icon': 'fas fa-headset'
        }
    ]
    
    return render_template('landing/index.html', 
                         stats=stats,
                         features=features, 
                         advantages=advantages)

@landing_bp.route('/nuzum/features')
def features():
    """صفحة تفصيلية للميزات"""
    return render_template('landing/features.html')

@landing_bp.route('/nuzum/pricing') 
def pricing():
    """صفحة الأسعار والباقات"""
    return render_template('landing/pricing.html')

@landing_bp.route('/nuzum/contact')
def contact():
    """صفحة التواصل"""
    return render_template('landing/contact.html')

@landing_bp.route('/nuzum/demo')
def demo():
    """صفحة عرض توضيحي"""
    return render_template('landing/demo.html')