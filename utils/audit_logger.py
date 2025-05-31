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
        if current_user.is_authenticated:
            # تحويل البيانات إلى JSON إذا كانت قاموس
            if isinstance(previous_data, dict):
                previous_data = json.dumps(previous_data, ensure_ascii=False)
            if isinstance(new_data, dict):
                new_data = json.dumps(new_data, ensure_ascii=False)
            
            audit_log = AuditLog()
            audit_log.user_id = current_user.id
            audit_log.action = action
            audit_log.entity_type = entity_type
            audit_log.entity_id = entity_id
            audit_log.details = details
            audit_log.ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
            audit_log.user_agent = request.environ.get('HTTP_USER_AGENT')
            audit_log.previous_data = previous_data
            audit_log.new_data = new_data
            audit_log.timestamp = datetime.utcnow()
            
            db.session.add(audit_log)
            db.session.commit()
            
    except Exception as e:
        print(f"خطأ في تسجيل النشاط: {e}")
        # لا نريد أن يؤثر خطأ في التسجيل على العملية الأساسية
        db.session.rollback()


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