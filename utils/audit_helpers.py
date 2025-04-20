"""
أدوات المراقبة ومتابعة الإجراءات
توفر هذه الوحدة دوال مساعدة لتسجيل إجراءات المستخدمين والمراقبة
"""

import json
from datetime import datetime
from flask import request, current_app, g
from app import db
from models import SystemAudit

def log_activity(action, entity_type, entity_id, entity_name=None, 
                previous_data=None, new_data=None, details=None):
    """
    تسجيل نشاط في سجل المراقبة
    
    المعلمات:
        action (str): نوع الإجراء (إضافة، تعديل، حذف)
        entity_type (str): نوع الكيان (موظف، قسم، راتب، الخ)
        entity_id (int): معرف الكيان
        entity_name (str, اختياري): اسم الكيان للعرض
        previous_data (dict, اختياري): البيانات قبل التعديل
        new_data (dict, اختياري): البيانات بعد التعديل
        details (str, اختياري): تفاصيل إضافية
    """
    try:
        # إنشاء كائن سجل مراقبة جديد
        audit = SystemAudit(
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            entity_name=entity_name,
            details=details,
            ip_address=request.remote_addr
        )
        
        # إضافة بيانات المستخدم إذا كان متوفراً
        if hasattr(g, 'user') and g.user:
            audit.user_id = g.user.id
        
        # تحويل البيانات إلى JSON إذا كانت متوفرة
        if previous_data:
            audit.previous_data = json.dumps(previous_data, ensure_ascii=False)
        
        if new_data:
            audit.new_data = json.dumps(new_data, ensure_ascii=False)
        
        # حفظ السجل في قاعدة البيانات
        db.session.add(audit)
        db.session.commit()
        
        return True
    except Exception as e:
        current_app.logger.error(f"خطأ في تسجيل النشاط: {str(e)}")
        db.session.rollback()
        return False

def log_create(entity_type, entity, entity_name_field='name', details=None):
    """
    تسجيل عملية إنشاء كيان جديد
    
    المعلمات:
        entity_type (str): نوع الكيان
        entity (object): كائن الكيان الذي تم إنشاؤه
        entity_name_field (str): اسم الحقل الذي يحتوي على اسم الكيان
        details (str, اختياري): تفاصيل إضافية
    """
    entity_name = getattr(entity, entity_name_field, str(entity.id)) if entity else None
    entity_data = entity_to_dict(entity) if entity else {}
    
    return log_activity(
        action="إنشاء",
        entity_type=entity_type,
        entity_id=entity.id,
        entity_name=entity_name,
        new_data=entity_data,
        details=details
    )

def log_update(entity_type, entity, old_data, entity_name_field='name', details=None):
    """
    تسجيل عملية تحديث كيان
    
    المعلمات:
        entity_type (str): نوع الكيان
        entity (object): كائن الكيان الذي تم تحديثه
        old_data (dict): البيانات القديمة قبل التحديث
        entity_name_field (str): اسم الحقل الذي يحتوي على اسم الكيان
        details (str, اختياري): تفاصيل إضافية
    """
    entity_name = getattr(entity, entity_name_field, str(entity.id)) if entity else None
    new_data = entity_to_dict(entity) if entity else {}
    
    return log_activity(
        action="تعديل",
        entity_type=entity_type,
        entity_id=entity.id,
        entity_name=entity_name,
        previous_data=old_data,
        new_data=new_data,
        details=details
    )

def log_delete(entity_type, entity_id, old_data, entity_name=None, details=None):
    """
    تسجيل عملية حذف كيان
    
    المعلمات:
        entity_type (str): نوع الكيان
        entity_id (int): معرف الكيان
        old_data (dict): بيانات الكيان قبل الحذف
        entity_name (str, اختياري): اسم الكيان
        details (str, اختياري): تفاصيل إضافية
    """
    return log_activity(
        action="حذف",
        entity_type=entity_type,
        entity_id=entity_id,
        entity_name=entity_name,
        previous_data=old_data,
        details=details
    )

def entity_to_dict(entity):
    """
    تحويل كائن قاعدة البيانات إلى قاموس
    
    المعلمات:
        entity (object): كائن قاعدة البيانات
        
    العائد:
        dict: قاموس يحتوي على بيانات الكائن
    """
    if not entity:
        return {}
        
    # الحصول على قاموس من كائن SQLAlchemy
    result = {}
    for column in entity.__table__.columns:
        # استثناء الحقول الخاصة
        if column.name not in ['password_hash', 'firebase_uid']:
            value = getattr(entity, column.name)
            
            # معالجة التاريخ والوقت
            if isinstance(value, datetime):
                value = value.isoformat()
                
            result[column.name] = value
            
    return result