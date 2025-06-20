"""
Multi-Tenant Decorators للتحكم في الوصول وعزل البيانات بين الشركات
"""
from functools import wraps
from flask import abort, g, current_app
from flask_login import current_user
from models import Company, User, UserType
import logging

logger = logging.getLogger(__name__)

def system_owner_required(f):
    """
    يتطلب أن يكون المستخدم مالك النظام
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        
        # التحقق من نوع المستخدم بأمان
        user_type = getattr(current_user, 'user_type', None)
        if not user_type or (user_type != UserType.SYSTEM_ADMIN and str(user_type) != 'SYSTEM_ADMIN'):
            logger.warning(f"غير مصرح - المستخدم {current_user.id} ليس مالك نظام، النوع: {user_type}")
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function

def company_admin_required(f):
    """
    يتطلب أن يكون المستخدم مدير شركة أو مالك النظام
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        
        user_type = getattr(current_user, 'user_type', None)
        allowed_types = [UserType.SYSTEM_ADMIN, UserType.COMPANY_ADMIN, 'SYSTEM_ADMIN', 'COMPANY_ADMIN']
        if not user_type or (user_type not in allowed_types and str(user_type) not in allowed_types):
            logger.warning(f"غير مصرح - المستخدم {current_user.id} حاول الوصول لوظيفة مدير الشركة، النوع: {user_type}")
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function

def employee_access_required(f):
    """
    يسمح للموظفين ومديري الشركات ومالك النظام
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        
        return f(*args, **kwargs)
    return decorated_function

def set_company_context(f):
    """
    يضع سياق الشركة في g.company_id للاستعلامات
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        
        # مالك النظام يمكنه الوصول لجميع الشركات
        user_type = getattr(current_user, 'user_type', None)
        if (user_type and (str(user_type) == 'SYSTEM_ADMIN' or user_type == UserType.SYSTEM_ADMIN)):
            # يمكن تمرير company_id في المعاملات للوصول لشركة محددة
            company_id = kwargs.get('company_id') or args[0] if args else None
            # إذا لم يحدد شركة معينة، استخدم الشركة الرئيسية
            g.company_id = company_id or current_user.company_id or 1
            g.user_type = UserType.SYSTEM_ADMIN
        else:
            # المستخدمون الآخرون مقيدون بشركتهم
            g.company_id = current_user.company_id
            g.user_type = current_user.user_type
        
        return f(*args, **kwargs)
    return decorated_function

def validate_company_access(company_id):
    """
    التحقق من صحة الوصول للشركة
    """
    if not current_user.is_authenticated:
        return False
    
    # مالك النظام يمكنه الوصول لجميع الشركات
    user_type = getattr(current_user, 'user_type', None)
    if (user_type and (str(user_type) == 'SYSTEM_ADMIN' or user_type == UserType.SYSTEM_ADMIN)):
        return True
    
    # المستخدمون الآخرون مقيدون بشركتهم
    return current_user.company_id == company_id

def filter_by_company(query, model_class):
    """
    تصفية الاستعلام حسب الشركة
    """
    # مالك النظام يمكنه رؤية جميع البيانات
    if (hasattr(g, 'user_type') and 
        g.user_type and 
        (str(g.user_type) == 'SYSTEM_ADMIN' or g.user_type == UserType.SYSTEM_ADMIN)):
        return query
    
    # إذا لم يحدد company_id، استخدم الشركة الرئيسية للتوافق
    if not hasattr(g, 'company_id') or g.company_id is None:
        g.company_id = 1
    
    if hasattr(model_class, 'company_id'):
        return query.filter(model_class.company_id == g.company_id)
    
    return query

def check_subscription_limits(company_id, check_type):
    """
    التحقق من حدود الاشتراك
    check_type: 'employees', 'vehicles', 'users'
    """
    from models import Company, Employee, Vehicle, User
    from app import db
    
    company = Company.query.get(company_id)
    if not company:
        return False, "الشركة غير موجودة"
    
    subscription = company.subscription
    if not subscription:
        return False, "لا يوجد اشتراك فعال"
    
    # التحقق من انتهاء الفترة التجريبية
    if subscription.is_trial_expired:
        return False, "انتهت الفترة التجريبية. يرجى الترقية للاشتراك المدفوع"
    
    # التحقق من انتهاء الاشتراك
    if subscription.is_expired:
        return False, "انتهى الاشتراك. يرجى تجديد الاشتراك"
    
    current_count = 0
    limit = 0
    
    if check_type == 'employees':
        current_count = Employee.query.filter_by(company_id=company_id).count()
        limit = subscription.max_employees
    elif check_type == 'vehicles':
        current_count = Vehicle.query.filter_by(company_id=company_id).count()
        limit = subscription.max_vehicles
    elif check_type == 'users':
        current_count = User.query.filter_by(company_id=company_id).count()
        limit = subscription.max_users
    
    if current_count >= limit:
        return False, f"تم الوصول للحد الأقصى من {check_type} ({limit})"
    
    return True, "مسموح"

def subscription_limit_required(check_type):
    """
    Decorator للتحقق من حدود الاشتراك قبل إنشاء عناصر جديدة
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            
            # مالك النظام غير مقيد بحدود الاشتراك
            if current_user.user_type == UserType.SYSTEM_ADMIN:
                return f(*args, **kwargs)
            
            # التحقق من حدود الاشتراك
            allowed, message = check_subscription_limits(current_user.company_id, check_type)
            if not allowed:
                logger.warning(f"تجاوز حدود الاشتراك - {current_user.company_id}: {message}")
                abort(403, description=message)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def trial_access_required(f):
    """
    التحقق من صحة الوصول للفترة التجريبية
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        
        # مالك النظام لديه وصول كامل
        if current_user.user_type == UserType.SYSTEM_ADMIN:
            return f(*args, **kwargs)
        
        company = Company.query.get(current_user.company_id)
        if not company or not company.subscription:
            abort(403, description="لا يوجد اشتراك فعال")
        
        subscription = company.subscription
        
        # التحقق من انتهاء الفترة التجريبية والاشتراك
        if subscription.is_trial_expired and subscription.is_expired:
            abort(403, description="انتهت الفترة التجريبية والاشتراك. يرجى الترقية")
        
        return f(*args, **kwargs)
    return decorated_function

def get_user_accessible_companies():
    """
    جلب الشركات التي يمكن للمستخدم الوصول إليها
    """
    if not current_user.is_authenticated:
        return []
    
    if current_user.user_type == UserType.SYSTEM_ADMIN:
        return Company.query.all()
    else:
        return [Company.query.get(current_user.company_id)] if current_user.company_id else []

def require_company_context(f):
    """
    يتطلب وجود سياق شركة صالح
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        
        # مالك النظام يحتاج لتحديد الشركة
        if current_user.user_type == UserType.SYSTEM_ADMIN:
            company_id = kwargs.get('company_id')
            if not company_id:
                abort(400, description="يجب تحديد معرف الشركة")
            
            company = Company.query.get(company_id)
            if not company:
                abort(404, description="الشركة غير موجودة")
            
            g.current_company = company
        else:
            # المستخدمون الآخرون مقيدون بشركتهم
            if not current_user.company_id:
                abort(403, description="المستخدم غير مرتبط بشركة")
            
            company = Company.query.get(current_user.company_id)
            if not company:
                abort(404, description="شركة المستخدم غير موجودة")
            
            g.current_company = company
        
        return f(*args, **kwargs)
    return decorated_function