"""
ملحقات Flask المشتركة
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

# تهيئة الملحقات
db = SQLAlchemy(model_class=Base)
login_manager = LoginManager()

def init_extensions(app):
    """تهيئة جميع الملحقات مع التطبيق"""
    
    # قاعدة البيانات
    db.init_app(app)
    
    # إدارة تسجيل الدخول
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'يرجى تسجيل الدخول للوصول إلى هذه الصفحة'
    login_manager.login_message_category = 'info'
    
    # تحديد دالة تحميل المستخدم
    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User.query.get(int(user_id))
    
    # التعامل مع المستخدمين غير المصرح لهم
    @login_manager.unauthorized_handler
    def unauthorized_handler():
        from flask import flash, redirect, url_for
        flash('يجب تسجيل الدخول أولاً', 'warning')
        return redirect(url_for('auth.login'))