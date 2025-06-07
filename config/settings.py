"""
إعدادات النظام المركزية
"""
import os
from datetime import timedelta

class Config:
    """إعدادات النظام الأساسية"""
    
    # إعدادات قاعدة البيانات
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # إعدادات الأمان
    SECRET_KEY = os.environ.get('SESSION_SECRET') or 'dev-secret-key-please-change'
    WTF_CSRF_ENABLED = True
    
    # إعدادات الجلسة
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # إعدادات الملفات
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'xlsx', 'xls'}
    
    # إعدادات التوطين
    LANGUAGES = ['ar', 'en']
    DEFAULT_LANGUAGE = 'ar'
    
    # إعدادات النظام
    SYSTEM_NAME = 'نُظم - نظام إدارة الموظفين والمركبات'
    SYSTEM_VERSION = '2.0.0'
    COMPANY_NAME = 'شركة المملكة العربية السعودية'
    
    # إعدادات البريد الإلكتروني
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # إعدادات Twilio
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')
    
    # إعدادات Firebase
    FIREBASE_API_KEY = os.environ.get('FIREBASE_API_KEY')
    FIREBASE_PROJECT_ID = os.environ.get('FIREBASE_PROJECT_ID')
    FIREBASE_APP_ID = os.environ.get('FIREBASE_APP_ID')

class DevelopmentConfig(Config):
    """إعدادات بيئة التطوير"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """إعدادات بيئة الإنتاج"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """إعدادات بيئة الاختبار"""
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False

# تحديد الإعدادات حسب البيئة
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}