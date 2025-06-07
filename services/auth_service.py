"""
خدمة المصادقة والتفويض
"""
from flask import flash, redirect, url_for
from flask_login import login_user, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from models import User, UserRole
from core.extensions import db
from utils.audit_logger import log_activity

class AuthService:
    """خدمة إدارة المصادقة والتفويض"""
    
    @staticmethod
    def authenticate_user(email, password, remember_me=False):
        """مصادقة المستخدم"""
        user = User.query.filter_by(email=email).first()
        
        if user and user.is_active and check_password_hash(user.password_hash, password):
            login_user(user, remember=remember_me)
            log_activity(
                user_id=user.id,
                action='login',
                details=f'تم تسجيل دخول المستخدم {user.name}'
            )
            return True, user
        
        log_activity(
            action='failed_login',
            details=f'محاولة تسجيل دخول فاشلة للبريد الإلكتروني: {email}'
        )
        return False, None
    
    @staticmethod
    def logout_user_session():
        """تسجيل خروج المستخدم"""
        if current_user.is_authenticated:
            log_activity(
                user_id=current_user.id,
                action='logout',
                details=f'تم تسجيل خروج المستخدم {current_user.name}'
            )
        logout_user()
    
    @staticmethod
    def create_user(name, email, username, password, role=UserRole.EMPLOYEE):
        """إنشاء مستخدم جديد"""
        try:
            # التحقق من عدم وجود المستخدم مسبقاً
            existing_user = User.query.filter(
                (User.email == email) | (User.username == username)
            ).first()
            
            if existing_user:
                return False, "المستخدم موجود مسبقاً"
            
            # إنشاء المستخدم الجديد
            user = User(
                name=name,
                email=email,
                username=username,
                password_hash=generate_password_hash(password),
                role=role,
                is_active=True
            )
            
            db.session.add(user)
            db.session.commit()
            
            log_activity(
                user_id=current_user.id if current_user.is_authenticated else None,
                action='create_user',
                details=f'تم إنشاء مستخدم جديد: {name} ({email})'
            )
            
            return True, user
            
        except Exception as e:
            db.session.rollback()
            return False, str(e)
    
    @staticmethod
    def update_user_password(user, new_password):
        """تحديث كلمة مرور المستخدم"""
        try:
            user.password_hash = generate_password_hash(new_password)
            db.session.commit()
            
            log_activity(
                user_id=current_user.id if current_user.is_authenticated else None,
                action='update_password',
                details=f'تم تحديث كلمة مرور المستخدم: {user.name}'
            )
            
            return True
        except Exception as e:
            db.session.rollback()
            return False
    
    @staticmethod
    def check_permission(user, module, permission=None):
        """التحقق من صلاحيات المستخدم"""
        if not user or not user.is_authenticated:
            return False
        
        # المديرون لديهم جميع الصلاحيات
        if user.role == UserRole.ADMIN:
            return True
        
        return user.can_access_module(module, permission)
    
    @staticmethod
    def get_user_accessible_departments(user):
        """جلب الأقسام التي يمكن للمستخدم الوصول إليها"""
        if not user or not user.is_authenticated:
            return []
        
        return user.get_accessible_departments()