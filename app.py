import os
import logging
from datetime import datetime

from flask import Flask, session, redirect, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager, current_user, login_required
from flask_wtf.csrf import CSRFProtect

# استيراد مكتبة dotenv لقراءة ملف .env
from dotenv import load_dotenv
load_dotenv()  # تحميل المتغيرات البيئية من ملف .env

# استيراد مكتبة SQLAlchemy للتعامل مع MySQL
import pymysql
pymysql.install_as_MySQLdb()  # استخدام PyMySQL كبديل لـ MySQLdb

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Base class for SQLAlchemy models
class Base(DeclarativeBase):
    pass

# Initialize SQLAlchemy
db = SQLAlchemy(model_class=Base)

# Initialize Flask-Login
login_manager = LoginManager()

# Initialize CSRF Protection
csrf = CSRFProtect()

# Create the Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "employee_management_secret")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# إعفاء بعض المسارات من حماية CSRF
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_CHECK_DEFAULT'] = False  # تعطيل التحقق التلقائي من CSRF

# Configure database connection using environment variables
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Provide default values for uploads and other configurations
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # Limit uploads to 16MB
app.config["UPLOAD_FOLDER"] = "uploads"

# Initialize SQLAlchemy with the app
db.init_app(app)

# Initialize Flask-Login
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'الرجاء تسجيل الدخول للوصول إلى هذه الصفحة'
login_manager.login_message_category = 'warning'

# Initialize CSRF Protection
csrf.init_app(app)

# إعداد Firebase
app.config['FIREBASE_API_KEY'] = os.environ.get('FIREBASE_API_KEY')
app.config['FIREBASE_PROJECT_ID'] = os.environ.get('FIREBASE_PROJECT_ID')
app.config['FIREBASE_APP_ID'] = os.environ.get('FIREBASE_APP_ID')

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# إضافة فلتر nl2br لتحويل السطور الجديدة إلى وسوم HTML <br>
from markupsafe import Markup

@app.template_filter('nl2br')
def nl2br_filter(s):
    if s:
        return Markup(s.replace('\n', '<br>'))
    return s

# Context processor to add variables to all templates
@app.context_processor
def inject_now():
    return {
        'now': datetime.now(),
        'firebase_api_key': app.config['FIREBASE_API_KEY'],
        'firebase_project_id': app.config['FIREBASE_PROJECT_ID'],
        'firebase_app_id': app.config['FIREBASE_APP_ID']
    }

# تصحيح مشكلة CSRF token في القوالب
@app.context_processor
def inject_csrf_token():
    """إضافة csrf_token إلى جميع القوالب"""
    def get_csrf_token():
        return csrf._get_csrf_token()
    
    return {'csrf_token': get_csrf_token}

# مسار الجذر الرئيسي للتطبيق مع توجيه تلقائي حسب نوع الجهاز
@app.route('/')
def root():
    from flask import request
    from models import Module, UserRole
    
    user_agent = request.headers.get('User-Agent', '').lower()
    mobile_devices = ['android', 'iphone', 'ipad', 'mobile']
    
    # التحقق مما إذا كان الطلب يتضمن معلمة m=1 للوصول المباشر إلى نسخة الجوال
    mobile_param = request.args.get('m', '0')
    
    # إذا كان المستخدم يستخدم جهازاً محمولاً أو طلب نسخة الجوال صراحةً
    if any(device in user_agent for device in mobile_devices) or mobile_param == '1':
        if current_user.is_authenticated:
            return redirect(url_for('mobile.index'))
        else:
            return redirect(url_for('mobile.login'))
    
    # إذا كان المستخدم يستخدم جهاز كمبيوتر
    if current_user.is_authenticated:
        # التحقق من صلاحيات المستخدم للوصول إلى لوحة التحكم
        if current_user.role == UserRole.ADMIN or current_user.has_module_access(Module.DASHBOARD):
            return redirect(url_for('dashboard.index'))
        else:
            return render_template('restricted.html')
    else:
        return redirect(url_for('auth.login'))

# Register blueprints for different modules
with app.app_context():
    # Import models before creating tables
    import models  # noqa: F401
    
    # Import and register route blueprints
    from routes.dashboard import dashboard_bp
    from routes.employees import employees_bp
    from routes.departments import departments_bp
    from routes.attendance import attendance_bp
    from routes.salaries import salaries_bp
    from routes.documents import documents_bp
    from routes.reports import reports_bp
    from routes.auth import auth_bp
    from routes.vehicles import vehicles_bp
    from routes.fees_costs import fees_costs_bp
    from routes.api import api_bp
    from routes.enhanced_reports import enhanced_reports_bp
    from routes.mobile import mobile_bp
    from routes.users import users_bp
    
    # تعطيل حماية CSRF لطرق معينة
    csrf.exempt(auth_bp)
    
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(employees_bp, url_prefix='/employees')
    app.register_blueprint(departments_bp, url_prefix='/departments')
    app.register_blueprint(attendance_bp, url_prefix='/attendance')
    app.register_blueprint(salaries_bp, url_prefix='/salaries')
    app.register_blueprint(enhanced_reports_bp, url_prefix='/enhanced_reports')
    app.register_blueprint(documents_bp, url_prefix='/documents')
    app.register_blueprint(vehicles_bp, url_prefix='/vehicles')
    app.register_blueprint(fees_costs_bp, url_prefix='/fees-costs')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    app.register_blueprint(api_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(mobile_bp, url_prefix='/mobile')
    app.register_blueprint(users_bp, url_prefix='/users')
    
    # إضافة دوال مساعدة لقوالب Jinja
    from utils.user_helpers import get_role_display_name, get_module_display_name, format_permissions, check_module_access
    
    # إضافة مرشح bitwise_and لاستخدامه في قوالب Jinja2
    @app.template_filter('bitwise_and')
    def bitwise_and_filter(value1, value2):
        """تنفيذ عملية bitwise AND بين قيمتين"""
        return value1 & value2
    
    # إضافة مرشح للتحقق من صلاحيات المستخدم
    @app.template_filter('check_module_access')
    def check_module_access_filter(user, module, permission=None):
        """
        مرشح للتحقق من صلاحيات المستخدم للوصول إلى وحدة معينة
        
        :param user: كائن المستخدم
        :param module: الوحدة المطلوب التحقق منها
        :param permission: الصلاحية المطلوبة (اختياري)
        :return: True إذا كان المستخدم لديه الصلاحية، False غير ذلك
        """
        from models import Permission
        return check_module_access(user, module, permission or Permission.VIEW)
        
    @app.context_processor
    def inject_global_template_vars():
        from models import Module, UserRole, Permission
        return {
            'get_role_display_name': get_role_display_name,
            'get_module_display_name': get_module_display_name,
            'format_permissions': format_permissions,
            'Module': Module,
            'UserRole': UserRole,
            'Permission': Permission
        }
    
    # ملاحظة: تم دمج هذا الكود مع مسار الجذر الرئيسي
    
    # Create database tables if they don't exist
    logger.info("Creating database tables...")
    db.create_all()
    logger.info("Database tables created successfully.")
