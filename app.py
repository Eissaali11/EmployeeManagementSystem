import os
import logging
from datetime import datetime

from flask import Flask, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager, current_user
from flask_wtf.csrf import CSRFProtect

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

# Context processor to add variables to all templates
@app.context_processor
def inject_now():
    return {
        'now': datetime.now(),
        'firebase_api_key': app.config['FIREBASE_API_KEY'],
        'firebase_project_id': app.config['FIREBASE_PROJECT_ID'],
        'firebase_app_id': app.config['FIREBASE_APP_ID']
    }

# مسار الجذر الرئيسي للتطبيق
@app.route('/')
def root():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
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
    from routes.renewal_fees import renewal_fees_bp
    from routes.vehicles import vehicles_bp
    
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(employees_bp, url_prefix='/employees')
    app.register_blueprint(departments_bp, url_prefix='/departments')
    app.register_blueprint(attendance_bp, url_prefix='/attendance')
    app.register_blueprint(salaries_bp, url_prefix='/salaries')
    app.register_blueprint(documents_bp, url_prefix='/documents')
    app.register_blueprint(renewal_fees_bp, url_prefix='/renewal-fees')
    app.register_blueprint(vehicles_bp, url_prefix='/vehicles')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    app.register_blueprint(auth_bp)
    
    # Create database tables if they don't exist
    logger.info("Creating database tables...")
    db.create_all()
    logger.info("Database tables created successfully.")
