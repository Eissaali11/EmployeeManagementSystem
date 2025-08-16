"""
مصنع التطبيق لإنشاء تطبيق Flask
"""
import os
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from config import config
from .extensions import init_extensions

def create_app(config_name=None):
    """إنشاء تطبيق Flask مع جميع الإعدادات والملحقات"""
    
    # تحديد بيئة التشغيل
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # إنشاء تطبيق Flask
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    
    # تحميل الإعدادات
    app.config.from_object(config[config_name])
    config[config_name].init_app(app) if hasattr(config[config_name], 'init_app') else None
    
    # إعداد ProxyFix للعمل مع الخوادم الوكيلة
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # تهيئة الملحقات
    init_extensions(app)
    
    # تسجيل المسارات (Blueprints)
    register_blueprints(app)
    
    # تسجيل معالجات الأخطاء
    register_error_handlers(app)
    
    # تسجيل المرشحات المخصصة
    register_template_filters(app)
    
    # تسجيل المتغيرات العامة للقوالب
    register_template_globals(app)
    
    return app

def register_blueprints(app):
    """تسجيل جميع المسارات (Blueprints)"""
    
    # استيراد المسارات
    from routes.auth import auth_bp
    from routes.attendance import attendance_bp
    from routes.departments import departments_bp
    from routes.employees import employees_bp
    from routes.salaries import salaries_bp
    from routes.documents import documents_bp
    from routes.vehicles import vehicles_bp
    from routes.users import users_bp
    from routes.reports import reports_bp
    from routes.fees_costs import fees_costs_bp
    from routes.accounting import accounting_bp
    from routes.accounting_extended import accounting_ext_bp
    
    # استيراد blueprint التحليل المالي
    try:
        from routes.analytics_direct import analytics_direct_bp
        analytics_available = True
    except ImportError as e:
        print(f"خطأ في استيراد التحليل المالي: {e}")
        analytics_available = False
    
    # تسجيل المسارات
    app.register_blueprint(auth_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(departments_bp)
    app.register_blueprint(employees_bp)
    app.register_blueprint(salaries_bp)
    app.register_blueprint(documents_bp)
    app.register_blueprint(vehicles_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(fees_costs_bp)
    app.register_blueprint(accounting_bp)
    app.register_blueprint(accounting_ext_bp)
    
    # تسجيل blueprint التحليل المالي إذا كان متاحاً
    if analytics_available:
        app.register_blueprint(analytics_direct_bp)
        print("تم تسجيل blueprint التحليل المالي بنجاح")
    else:
        print("لم يتم تسجيل blueprint التحليل المالي")

def register_error_handlers(app):
    """تسجيل معالجات الأخطاء"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        from flask import render_template
        return render_template('error.html', 
                             error_code=404,
                             error_message='الصفحة المطلوبة غير موجودة'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        from .extensions import db
        db.session.rollback()
        return render_template('error.html',
                             error_code=500,
                             error_message='خطأ داخلي في الخادم'), 500
    
    @app.errorhandler(403)
    def forbidden_error(error):
        from flask import render_template
        return render_template('error.html',
                             error_code=403,
                             error_message='ليس لديك صلاحية للوصول إلى هذه الصفحة'), 403

def register_template_filters(app):
    """تسجيل المرشحات المخصصة للقوالب"""
    
    @app.template_filter('nl2br')
    def nl2br_filter(s):
        """تحويل أسطر النصوص الجديدة إلى <br>"""
        if s is None:
            return ''
        return s.replace('\n', '<br>')
    
    @app.template_filter('format_date')
    def format_date_filter(date, format='%Y-%m-%d'):
        """تنسيق التواريخ"""
        if date is None:
            return ''
        try:
            return date.strftime(format)
        except:
            return str(date)
    
    @app.template_filter('display_date')
    def display_date_filter(date, format='%Y-%m-%d', default="غير محدد"):
        """عرض التاريخ مع نص بديل"""
        if date is None:
            return default
        try:
            return date.strftime(format)
        except:
            return default
    
    @app.template_filter('days_remaining')
    def days_remaining_filter(date, from_date=None):
        """حساب الأيام المتبقية"""
        if date is None:
            return None
        try:
            from datetime import datetime, date as date_class
            if isinstance(date, str):
                date = datetime.strptime(date, '%Y-%m-%d').date()
            if from_date is None:
                from_date = datetime.now().date()
            elif isinstance(from_date, str):
                from_date = datetime.strptime(from_date, '%Y-%m-%d').date()
            
            delta = date - from_date
            return delta.days
        except:
            return None

def register_template_globals(app):
    """تسجيل المتغيرات العامة للقوالب"""
    
    @app.context_processor
    def inject_now():
        from datetime import datetime
        return {'now': datetime.utcnow()}
    
    @app.context_processor
    def inject_csrf_token():
        def get_csrf_token():
            from flask_wtf.csrf import generate_csrf
            return generate_csrf()
        return dict(csrf_token=get_csrf_token)
    
    @app.context_processor
    def inject_global_template_vars():
        from flask_login import current_user
        from models import Module, Permission
        
        def bitwise_and_filter(value1, value2):
            """تنفيذ عملية bitwise AND"""
            try:
                return int(value1) & int(value2)
            except:
                return 0
        
        def check_module_access_filter(user, module, permission=None):
            """التحقق من صلاحيات الوصول للوحدة"""
            if not user or not user.is_authenticated:
                return False
            return user.can_access_module(module, permission)
        
        return dict(
            current_user=current_user,
            Module=Module,
            Permission=Permission,
            bitwise_and=bitwise_and_filter,
            check_module_access=check_module_access_filter
        )