from functools import wraps
from flask import flash, redirect, url_for, abort, request
from flask_login import current_user
from models import Module, UserRole

def module_access_required(module):
    """
    مصادقة للتحقق من أن المستخدم لديه الصلاحية للوصول إلى وحدة معينة.
    
    Args:
        module: الوحدة المطلوب التحقق من صلاحية الوصول إليها
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # التحقق من إذا كان المستخدم مسؤول (ADMIN)
            if current_user.role == UserRole.ADMIN:
                return f(*args, **kwargs)
                
            # التحقق من إذا كان للمستخدم صلاحية الوصول إلى الوحدة
            if not current_user.has_module_access(module):
                flash('ليس لديك صلاحية الوصول إلى هذه الصفحة', 'danger')
                return redirect(url_for('auth.login'))
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def permission_required(module, permission):
    """
    مصادقة للتحقق من أن المستخدم لديه صلاحية محددة على وحدة معينة.
    
    Args:
        module: الوحدة المطلوب التحقق من الصلاحية عليها
        permission: الصلاحية المطلوبة
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # التحقق من إذا كان المستخدم مسؤول (ADMIN)
            if current_user.role == UserRole.ADMIN:
                return f(*args, **kwargs)
                
            # التحقق من إذا كان للمستخدم صلاحية محددة على الوحدة
            if not current_user.has_permission(module, permission):
                flash('ليس لديك صلاحية كافية لتنفيذ هذا الإجراء', 'danger')
                return redirect(url_for('auth.login'))
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator