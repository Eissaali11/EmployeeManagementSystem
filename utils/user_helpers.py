"""
أدوات مساعدة لإدارة المستخدمين والصلاحيات
توفر هذه الوحدة دوال مساعدة للتعامل مع المستخدمين والصلاحيات
"""

from flask import current_app, g
from app import db
from models import User, UserPermission, UserRole, Module, Permission

def create_default_permissions(user):
    """
    إنشاء الصلاحيات الافتراضية للمستخدم بناءً على دوره
    
    المعلمات:
        user (User): كائن المستخدم
    """
    # تحديد الصلاحيات بناءً على دور المستخدم
    if user.role == UserRole.ADMIN:
        # مدير النظام - كل الصلاحيات في جميع الوحدات
        permissions = []
        for module in Module:
            permissions.append(UserPermission(
                user_id=user.id,
                module=module,
                permissions=Permission.ADMIN
            ))
        
    elif user.role == UserRole.MANAGER:
        # مدير - كل الصلاحيات ما عدا إدارة المستخدمين
        permissions = []
        for module in Module:
            if module != Module.USERS:
                permissions.append(UserPermission(
                    user_id=user.id,
                    module=module,
                    permissions=Permission.VIEW | Permission.CREATE | Permission.EDIT | Permission.DELETE | Permission.MANAGE
                ))
            else:
                permissions.append(UserPermission(
                    user_id=user.id,
                    module=module,
                    permissions=Permission.VIEW
                ))
    
    elif user.role == UserRole.HR:
        # موارد بشرية - إدارة الموظفين والمستندات والأقسام
        permissions = [
            UserPermission(user_id=user.id, module=Module.EMPLOYEES, 
                         permissions=Permission.VIEW | Permission.CREATE | Permission.EDIT | Permission.MANAGE),
            UserPermission(user_id=user.id, module=Module.ATTENDANCE, 
                         permissions=Permission.VIEW | Permission.CREATE | Permission.EDIT),
            UserPermission(user_id=user.id, module=Module.DEPARTMENTS, 
                         permissions=Permission.VIEW | Permission.CREATE | Permission.EDIT),
            UserPermission(user_id=user.id, module=Module.DOCUMENTS, 
                         permissions=Permission.VIEW | Permission.CREATE | Permission.EDIT | Permission.MANAGE),
            UserPermission(user_id=user.id, module=Module.REPORTS, 
                         permissions=Permission.VIEW),
            UserPermission(user_id=user.id, module=Module.FEES, 
                         permissions=Permission.VIEW | Permission.CREATE | Permission.EDIT),
        ]
        
    elif user.role == UserRole.FINANCE:
        # مالية - إدارة الرواتب والتكاليف
        permissions = [
            UserPermission(user_id=user.id, module=Module.EMPLOYEES, 
                         permissions=Permission.VIEW),
            UserPermission(user_id=user.id, module=Module.SALARIES, 
                         permissions=Permission.VIEW | Permission.CREATE | Permission.EDIT | Permission.MANAGE),
            UserPermission(user_id=user.id, module=Module.FEES, 
                         permissions=Permission.VIEW | Permission.CREATE | Permission.EDIT | Permission.MANAGE),
            UserPermission(user_id=user.id, module=Module.REPORTS, 
                         permissions=Permission.VIEW),
        ]
        
    elif user.role == UserRole.FLEET:
        # أسطول - إدارة السيارات
        permissions = [
            UserPermission(user_id=user.id, module=Module.VEHICLES, 
                         permissions=Permission.VIEW | Permission.CREATE | Permission.EDIT | Permission.MANAGE),
            UserPermission(user_id=user.id, module=Module.REPORTS, 
                         permissions=Permission.VIEW),
        ]
        
    else:  # UserRole.USER
        # مستخدم عادي - عرض فقط
        permissions = []
        for module in Module:
            permissions.append(UserPermission(
                user_id=user.id,
                module=module,
                permissions=Permission.VIEW
            ))
    
    # حفظ الصلاحيات في قاعدة البيانات
    for permission in permissions:
        db.session.add(permission)
    
    try:
        db.session.commit()
        return True
    except Exception as e:
        current_app.logger.error(f"خطأ في إنشاء الصلاحيات الافتراضية: {str(e)}")
        db.session.rollback()
        return False

def get_role_display_name(role):
    """
    الحصول على اسم العرض لدور المستخدم
    
    المعلمات:
        role (UserRole): دور المستخدم
        
    العائد:
        str: اسم العرض للدور
    """
    role_names = {
        UserRole.ADMIN: "مدير النظام",
        UserRole.MANAGER: "مدير",
        UserRole.HR: "موارد بشرية",
        UserRole.FINANCE: "مالية",
        UserRole.FLEET: "مسؤول أسطول",
        UserRole.USER: "مستخدم عادي"
    }
    
    return role_names.get(role, "مستخدم")

def get_module_display_name(module):
    """
    الحصول على اسم العرض للوحدة
    
    المعلمات:
        module (Module): الوحدة
        
    العائد:
        str: اسم العرض للوحدة
    """
    module_names = {
        Module.EMPLOYEES: "الموظفين",
        Module.ATTENDANCE: "الحضور والغياب",
        Module.DEPARTMENTS: "الأقسام",
        Module.SALARIES: "الرواتب",
        Module.DOCUMENTS: "المستندات",
        Module.VEHICLES: "السيارات",
        Module.USERS: "المستخدمين",
        Module.REPORTS: "التقارير",
        Module.FEES: "الرسوم والتكاليف"
    }
    
    return module_names.get(module, "وحدة غير معروفة")

def format_permissions(permissions_value):
    """
    تنسيق قيمة الصلاحيات إلى قائمة أسماء الصلاحيات
    
    المعلمات:
        permissions_value (int): قيمة الصلاحيات
        
    العائد:
        list: قائمة بأسماء الصلاحيات
    """
    permissions_list = []
    
    if permissions_value & Permission.VIEW:
        permissions_list.append("عرض")
    
    if permissions_value & Permission.CREATE:
        permissions_list.append("إنشاء")
    
    if permissions_value & Permission.EDIT:
        permissions_list.append("تعديل")
    
    if permissions_value & Permission.DELETE:
        permissions_list.append("حذف")
    
    if permissions_value & Permission.MANAGE:
        permissions_list.append("إدارة")
    
    return permissions_list

def requires_permission(module, permission):
    """
    مزخرف للتحقق من صلاحيات المستخدم للوصول إلى طرق المراقبة
    
    المعلمات:
        module (Module): الوحدة المطلوبة
        permission (Permission): الصلاحية المطلوبة
        
    الاستخدام:
        @requires_permission(Module.EMPLOYEES, Permission.EDIT)
        def edit_employee(id):
            # ...
    """
    from functools import wraps
    from flask import flash, redirect, url_for
    from flask_login import current_user
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
                
            if not current_user.has_permission(module, permission):
                flash('ليس لديك الصلاحية للقيام بهذا الإجراء', 'danger')
                return redirect(url_for('home.index'))
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator