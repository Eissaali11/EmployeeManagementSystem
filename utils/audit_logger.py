"""
نظام تسجيل العمليات والنشاطات في النظام
"""

from flask import request
from flask_login import current_user
from app import db
from models import AuditLog
import json
from datetime import datetime


def log_activity(action, entity_type, entity_id=None, details=None, previous_data=None, new_data=None):
    """
    تسجيل نشاط في سجل المراجعة
    
    :param action: نوع العملية (create, update, delete, view)
    :param entity_type: نوع الكيان (Employee, Department, Attendance, etc.)
    :param entity_id: معرف الكيان
    :param details: تفاصيل العملية
    :param previous_data: البيانات السابقة (للتحديث والحذف)
    :param new_data: البيانات الجديدة (للإنشاء والتحديث)
    """
    try:
        # التحقق من وجود current_user والتأكد من أنه مسجل دخول أو النماذج الخارجية
        user_id = None
        if hasattr(current_user, 'is_authenticated') and current_user.is_authenticated and hasattr(current_user, 'id') and current_user.id:
            user_id = current_user.id
        elif 'external' in action or 'External' in entity_type:
            # للنماذج الخارجية، استخدم user_id خاص للعمليات الخارجية
            user_id = -1  # معرف خاص للعمليات الخارجية
        
        if user_id:
            print(f"تسجيل عملية: {action} - {entity_type} - {details}")  # للتشخيص
            
            # تحويل البيانات إلى JSON إذا كانت قاموس
            if isinstance(previous_data, dict):
                previous_data = json.dumps(previous_data, ensure_ascii=False)
            if isinstance(new_data, dict):
                new_data = json.dumps(new_data, ensure_ascii=False)
            
            audit_log = AuditLog()
            audit_log.user_id = user_id
            audit_log.action = action
            audit_log.entity_type = entity_type
            audit_log.entity_id = entity_id
            audit_log.details = details
            
            # التعامل الآمن مع request
            try:
                audit_log.ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'Unknown'))
                audit_log.user_agent = request.environ.get('HTTP_USER_AGENT', 'Unknown')
            except:
                audit_log.ip_address = 'Unknown'
                audit_log.user_agent = 'Unknown'
            
            audit_log.previous_data = previous_data
            audit_log.new_data = new_data
            audit_log.timestamp = datetime.utcnow()
            
            db.session.add(audit_log)
            db.session.commit()
            print(f"تم تسجيل العملية بنجاح: {audit_log.id}")  # للتشخيص
            
        else:
            print(f"لا يوجد مستخدم مسجل دخول - لم يتم تسجيل العملية: {action}")  # للتشخيص
            
    except Exception as e:
        print(f"خطأ في تسجيل النشاط: {e}")
        import traceback
        traceback.print_exc()  # طباعة التفاصيل الكاملة للخطأ
        # لا نريد أن يؤثر خطأ في التسجيل على العملية الأساسية
        try:
            db.session.rollback()
        except:
            pass


def log_attendance_activity(action, attendance_data, employee_name=None):
    """
    تسجيل نشاط الحضور
    """
    if action == 'create':
        details = f"تم تسجيل حضور الموظف: {employee_name}"
    elif action == 'update':
        details = f"تم تعديل حضور الموظف: {employee_name}"
    elif action == 'bulk_create':
        details = f"تم تسجيل حضور جماعي"
    else:
        details = f"عملية حضور: {action}"
    
    log_activity(
        action=action,
        entity_type='Attendance',
        entity_id=attendance_data.get('id'),
        details=details,
        new_data=attendance_data
    )


def log_employee_activity(action, employee_data, employee_name=None):
    """
    تسجيل نشاط الموظفين
    """
    if action == 'create':
        details = f"تم إضافة موظف جديد: {employee_name}"
    elif action == 'update':
        details = f"تم تعديل بيانات الموظف: {employee_name}"
    elif action == 'delete':
        details = f"تم حذف الموظف: {employee_name}"
    else:
        details = f"عملية موظف: {action}"
    
    log_activity(
        action=action,
        entity_type='Employee',
        entity_id=employee_data.get('id'),
        details=details,
        new_data=employee_data if action in ['create', 'update'] else None,
        previous_data=employee_data if action == 'delete' else None
    )


def log_department_activity(action, department_data, department_name=None):
    """
    تسجيل نشاط الأقسام
    """
    if action == 'create':
        details = f"تم إضافة قسم جديد: {department_name}"
    elif action == 'update':
        details = f"تم تعديل القسم: {department_name}"
    elif action == 'delete':
        details = f"تم حذف القسم: {department_name}"
    else:
        details = f"عملية قسم: {action}"
    
    log_activity(
        action=action,
        entity_type='Department',
        entity_id=department_data.get('id'),
        details=details,
        new_data=department_data if action in ['create', 'update'] else None,
        previous_data=department_data if action == 'delete' else None
    )


def log_user_activity(action, user_data, user_name=None):
    """
    تسجيل نشاط المستخدمين
    """
    if action == 'create':
        details = f"تم إضافة مستخدم جديد: {user_name}"
    elif action == 'update':
        details = f"تم تعديل المستخدم: {user_name}"
    elif action == 'login':
        details = f"تسجيل دخول المستخدم: {user_name}"
    elif action == 'logout':
        details = f"تسجيل خروج المستخدم: {user_name}"
    else:
        details = f"عملية مستخدم: {action}"
    
    log_activity(
        action=action,
        entity_type='User',
        entity_id=user_data.get('id'),
        details=details,
        new_data=user_data if action in ['create', 'update'] else None
    )


def log_document_activity(action, document_data, document_name=None):
    """
    تسجيل نشاط الوثائق
    """
    if action == 'create':
        details = f"تم إضافة وثيقة جديدة: {document_name}"
    elif action == 'update':
        details = f"تم تعديل الوثيقة: {document_name}"
    elif action == 'delete':
        details = f"تم حذف الوثيقة: {document_name}"
    else:
        details = f"عملية وثيقة: {action}"
    
    log_activity(
        action=action,
        entity_type='Document',
        entity_id=document_data.get('id'),
        details=details,
        new_data=document_data if action in ['create', 'update'] else None,
        previous_data=document_data if action == 'delete' else None
    )


def log_system_activity(action, details):
    """
    تسجيل نشاط النظام العام
    """
    log_activity(
        action=action,
        entity_type='System',
        details=details
    )


def log_audit(user_id, action, entity_type, entity_id=None, details=None, previous_data=None, new_data=None):
    """
    دالة تسجيل المراجعة العامة
    
    :param user_id: معرف المستخدم
    :param action: نوع العملية (create, update, delete, etc.)
    :param entity_type: نوع الكيان
    :param entity_id: معرف الكيان
    :param details: تفاصيل العملية
    :param previous_data: البيانات السابقة
    :param new_data: البيانات الجديدة
    """
    try:
        # تحويل البيانات إلى JSON إذا كانت قاموس
        if isinstance(previous_data, dict):
            previous_data = json.dumps(previous_data, ensure_ascii=False)
        if isinstance(new_data, dict):
            new_data = json.dumps(new_data, ensure_ascii=False)
        
        audit_log = AuditLog()
        audit_log.user_id = user_id
        audit_log.action = action
        audit_log.entity_type = entity_type
        audit_log.entity_id = entity_id
        audit_log.details = details
        
        # التعامل الآمن مع request
        try:
            audit_log.ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR', 'Unknown'))
            audit_log.user_agent = request.environ.get('HTTP_USER_AGENT', 'Unknown')
        except:
            audit_log.ip_address = 'Unknown'
            audit_log.user_agent = 'Unknown'
        
        audit_log.previous_data = previous_data
        audit_log.new_data = new_data
        audit_log.timestamp = datetime.utcnow()
        
        db.session.add(audit_log)
        db.session.commit()
        print(f"تم تسجيل العملية بنجاح: {audit_log.id}")
        
    except Exception as e:
        print(f"خطأ في تسجيل المراجعة: {e}")
        import traceback
        traceback.print_exc()
        try:
            db.session.rollback()
        except:
            pass