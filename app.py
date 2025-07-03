"""
نُظم - تطبيق إدارة الموظفين والمركبات
Clean Flask Application Factory
"""

import os
import logging
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, session, request, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========== Database Setup ==========

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

# ========== Application Factory ==========

def create_app():
    """إنشاء تطبيق Flask"""
    app = Flask(__name__)
    
    # Configuration
    app.secret_key = os.environ.get("SESSION_SECRET", "nuzum-secret-key-2024")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    # Middleware
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'يرجى تسجيل الدخول للوصول إلى هذه الصفحة'
    
    # Import models
    from models import User, Employee, Vehicle, Department, Attendance, Salary
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register API Blueprint
    from routes.restful_api import api_bp
    app.register_blueprint(api_bp)
    
    # Template filters
    @app.template_filter('nl2br')
    def nl2br_filter(s):
        """تحويل أسطر جديدة إلى <br>"""
        if s is None:
            return ''
        return s.replace('\n', '<br>')
    
    @app.template_filter('format_date')
    def format_date_filter(date, format='%Y-%m-%d'):
        """تنسيق التاريخ"""
        if date is None:
            return 'غير محدد'
        if isinstance(date, str):
            return date
        try:
            return date.strftime(format)
        except:
            return str(date)
    
    # Context processors
    @app.context_processor
    def inject_now():
        """إضافة التاريخ والوقت الحالي للقوالب"""
        return {'now': datetime.utcnow()}
    
    # Routes
    @app.route('/')
    def index():
        """الصفحة الرئيسية"""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return render_template('index.html')
    
    @app.route('/dashboard')
    def dashboard():
        """لوحة المعلومات"""
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        
        # Get basic statistics
        total_employees = Employee.query.count()
        total_vehicles = Vehicle.query.count()
        total_departments = Department.query.count()
        
        return render_template('dashboard.html',
                             total_employees=total_employees,
                             total_vehicles=total_vehicles,
                             total_departments=total_departments)
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """تسجيل الدخول"""
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            
            user = User.query.filter_by(email=email).first()
            
            if user and user.check_password(password):
                from flask_login import login_user
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                return render_template('login.html', error='البريد الإلكتروني أو كلمة المرور غير صحيحة')
        
        return render_template('login.html')
    
    @app.route('/logout')
    def logout():
        """تسجيل الخروج"""
        from flask_login import logout_user
        logout_user()
        return redirect(url_for('index'))
    
    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
    
    # Database initialization
    with app.app_context():
        logger.info(f"Using database: {app.config['SQLALCHEMY_DATABASE_URI'][:50]}***")
        logger.info("Creating database tables...")
        db.create_all()
        
        # Initialize basic data
        from models import User
        if not User.query.filter_by(email='admin@nuzum.sa').first():
            admin_user = User(
                name='مدير النظام',
                email='admin@nuzum.sa',
                role='admin'
            )
            admin_user.set_password('admin123')
            db.session.add(admin_user)
            db.session.commit()
        
        logger.info("Database tables created successfully.")
    
    return app

# Create the application
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)