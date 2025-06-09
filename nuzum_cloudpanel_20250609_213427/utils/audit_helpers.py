import json
import datetime
from typing import Any, Dict, Optional, Union
import ipaddress
import logging

from app import db
from flask import request, g
from models import SystemAudit, User

# إعداد التسجيل
logger = logging.getLogger(__name__)

def json_serial(obj):
    """
    دالة مساعدة لتحويل كائنات التاريخ والوقت إلى نص في JSON
    """
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def serialize_sqlalchemy_obj(obj):
    """
    تحويل كائن SQLAlchemy إلى قاموس (لتسجيل الأنشطة)
    """
    if obj is None:
        return None
        
    # استبعاد العلاقات والحقول المستثناة
    excluded_keys = ['_sa_instance_state', 'query', 'query_class']
    
    # استخدام حقل __dict__ للحصول على جميع الخصائص
    data = {}
    for key, value in obj.__dict__.items():
        if key not in excluded_keys:
            try:
                # محاولة تحويل القيمة إلى JSON
                json.dumps(value, default=json_serial)
                data[key] = value
            except TypeError:
                # إذا كانت القيمة غير قابلة للتحويل إلى JSON، حولها إلى نص
                data[key] = str(value)
    
    return data

def extract_entity_name(entity_obj: Any, entity_type: str) -> str:
    """
    استخراج اسم الكيان لعرضه في سجل النشاط
    """
    if entity_obj is None:
        return "Unknown"
        
    if hasattr(entity_obj, 'name'):
        return entity_obj.name
    elif hasattr(entity_obj, 'title'):
        return entity_obj.title
    elif hasattr(entity_obj, 'email'):
        return entity_obj.email
    elif entity_type == 'user' and hasattr(entity_obj, 'email'):
        return entity_obj.email
    elif entity_type == 'employee' and hasattr(entity_obj, 'name'):
        return entity_obj.name
    elif entity_type == 'vehicle' and hasattr(entity_obj, 'plate_number'):
        return entity_obj.plate_number
    
    # إذا لم يكن هناك اسم معروف، استخدم معرف الكيان
    if hasattr(entity_obj, 'id'):
        return f"{entity_type} #{entity_obj.id}"
    
    return "Unknown"

def get_client_ip() -> str:
    """
    الحصول على عنوان IP الخاص بالمستخدم
    """
    if not request:
        return "127.0.0.1"  # تعيين قيمة افتراضية إذا لم يكن هناك طلب
        
    # محاولة الحصول على عنوان IP من ترويسات الطلب
    x_forwarded_for = request.headers.get('X-Forwarded-For')
    
    if x_forwarded_for:
        # استخدام أول عنوان IP في حالة وجود عدة عناوين
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.remote_addr or "127.0.0.1"
    
    # التحقق من صحة عنوان IP
    try:
        ipaddress.ip_address(ip)
        return ip
    except ValueError:
        return "127.0.0.1"  # إرجاع قيمة افتراضية إذا كان العنوان غير صالح

def get_current_user_id() -> Optional[int]:
    """
    الحصول على معرف المستخدم الحالي
    """
    # محاولة الحصول على المستخدم من الجلسة الحالية
    if hasattr(g, 'user') and g.user and hasattr(g.user, 'id'):
        return g.user.id
    
    # محاولة الحصول على المستخدم من معرف تسجيل الدخول
    if hasattr(g, 'user_id') and g.user_id:
        return g.user_id
        
    return None

def log_activity(
    action: str,
    entity_type: str,
    entity_id: int,
    entity_obj: Any = None,
    previous_data: Dict[str, Any] = None,
    new_data: Dict[str, Any] = None,
    details: str = None,
    user_id: Optional[int] = None
) -> None:
    """
    تسجيل نشاط في سجل عمليات النظام
    
    :param action: نوع الإجراء (إضافة، تعديل، حذف، الخ)
    :param entity_type: نوع الكيان (موظف، قسم، الخ)
    :param entity_id: معرف الكيان
    :param entity_obj: كائن الكيان (اختياري)
    :param previous_data: البيانات السابقة (للتعديل)
    :param new_data: البيانات الجديدة (للتعديل أو الإضافة)
    :param details: تفاصيل إضافية
    :param user_id: معرف المستخدم الذي قام بالإجراء (اختياري)
    """
    try:
        # الحصول على معرف المستخدم إذا لم يتم تمريره
        if user_id is None:
            user_id = get_current_user_id()
        
        # استخراج اسم الكيان
        entity_name = extract_entity_name(entity_obj, entity_type)
        
        # تحويل البيانات إلى JSON
        previous_data_json = None
        if previous_data:
            previous_data_json = json.dumps(previous_data, default=json_serial, ensure_ascii=False)
            
        new_data_json = None
        if new_data:
            new_data_json = json.dumps(new_data, default=json_serial, ensure_ascii=False)
        
        # إنشاء كائن SystemAudit
        audit = SystemAudit(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            entity_name=entity_name,
            previous_data=previous_data_json,
            new_data=new_data_json,
            details=details,
            ip_address=get_client_ip(),
            user_id=user_id,
            timestamp=datetime.datetime.utcnow()
        )
        
        # حفظ السجل في قاعدة البيانات
        db.session.add(audit)
        db.session.commit()
        
        # تسجيل معلومات
        logger.info(f"Activity logged: {action} on {entity_type} #{entity_id} by user #{user_id}")
        
    except Exception as e:
        # تسجيل الخطأ ولكن لا ترفع استثناء
        logger.error(f"Error logging activity: {str(e)}")
        # إلغاء العملية إذا كانت هناك مشكلة
        db.session.rollback()

def log_create(entity_type: str, entity: Any, details: str = None, user_id: Optional[int] = None) -> None:
    """
    تسجيل إضافة كيان جديد
    """
    entity_data = serialize_sqlalchemy_obj(entity)
    
    log_activity(
        action="create",
        entity_type=entity_type,
        entity_id=entity.id,
        entity_obj=entity,
        new_data=entity_data,
        details=details,
        user_id=user_id
    )

def log_update(entity_type: str, entity: Any, previous_data: Dict[str, Any], details: str = None, user_id: Optional[int] = None) -> None:
    """
    تسجيل تعديل كيان
    """
    new_data = serialize_sqlalchemy_obj(entity)
    
    log_activity(
        action="update",
        entity_type=entity_type,
        entity_id=entity.id,
        entity_obj=entity,
        previous_data=previous_data,
        new_data=new_data,
        details=details,
        user_id=user_id
    )

def log_delete(entity_type: str, entity: Any, details: str = None, user_id: Optional[int] = None) -> None:
    """
    تسجيل حذف كيان
    """
    entity_data = serialize_sqlalchemy_obj(entity)
    
    log_activity(
        action="delete",
        entity_type=entity_type,
        entity_id=entity.id,
        entity_obj=entity,
        previous_data=entity_data,
        details=details,
        user_id=user_id
    )

def log_login(user: User, details: str = None) -> None:
    """
    تسجيل تسجيل دخول مستخدم
    """
    log_activity(
        action="login",
        entity_type="user",
        entity_id=user.id,
        entity_obj=user,
        details=details,
        user_id=user.id
    )

def log_logout(user: User, details: str = None) -> None:
    """
    تسجيل تسجيل خروج مستخدم
    """
    log_activity(
        action="logout",
        entity_type="user",
        entity_id=user.id,
        entity_obj=user,
        details=details,
        user_id=user.id
    )

def log_access_denied(entity_type: str, entity_id: int, details: str = None, user_id: Optional[int] = None) -> None:
    """
    تسجيل محاولة وصول مرفوضة
    """
    log_activity(
        action="access_denied",
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
        user_id=user_id
    )