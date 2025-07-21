from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app import db
from models import (OperationRequest, OperationNotification, VehicleHandover, 
                   VehicleWorkshop, ExternalAuthorization, SafetyInspection, 
                   Vehicle, User, UserRole, Employee)
from datetime import datetime
from utils.audit_logger import log_audit

operations_bp = Blueprint('operations', __name__, url_prefix='/operations')

@operations_bp.route('/')
@login_required
def operations_dashboard():
    """لوحة إدارة العمليات الرئيسية"""
    
    # فحص صلاحية المدير
    if current_user.role != UserRole.ADMIN:
        flash('غير مسموح لك بالوصول لهذه الصفحة', 'danger')
        return redirect(url_for('dashboard.index'))
    
    # إحصائيات العمليات
    pending_operations = OperationRequest.query.filter_by(status='pending').count()
    under_review_operations = OperationRequest.query.filter_by(status='under_review').count()
    approved_operations = OperationRequest.query.filter_by(status='approved').count()
    rejected_operations = OperationRequest.query.filter_by(status='rejected').count()
    
    # العمليات المعلقة مرتبة بالأولوية والتاريخ
    pending_requests = OperationRequest.query.filter_by(status='pending').order_by(
        OperationRequest.priority.desc(),
        OperationRequest.requested_at.desc()
    ).limit(10).all()
    
    # الإشعارات غير المقروءة
    unread_notifications = OperationNotification.query.filter_by(
        user_id=current_user.id, 
        is_read=False
    ).count()
    
    stats = {
        'pending': pending_operations,
        'under_review': under_review_operations,
        'approved': approved_operations,
        'rejected': rejected_operations,
        'unread_notifications': unread_notifications
    }
    
    return render_template('operations/dashboard.html', 
                         stats=stats, 
                         pending_requests=pending_requests)

@operations_bp.route('/list')
@login_required
def operations_list():
    """قائمة جميع العمليات مع فلترة"""
    
    if current_user.role != UserRole.ADMIN:
        flash('غير مسموح لك بالوصول لهذه الصفحة', 'danger')
        return redirect(url_for('dashboard.index'))
    
    # فلترة العمليات
    status_filter = request.args.get('status', 'all')
    operation_type_filter = request.args.get('operation_type', 'all')
    priority_filter = request.args.get('priority', 'all')
    
    query = OperationRequest.query
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    if operation_type_filter != 'all':
        query = query.filter_by(operation_type=operation_type_filter)
    
    if priority_filter != 'all':
        query = query.filter_by(priority=priority_filter)
    
    # ترتيب العمليات
    operations = query.order_by(
        OperationRequest.priority.desc(),
        OperationRequest.requested_at.desc()
    ).all()
    
    return render_template('operations/list.html', 
                         operations=operations,
                         status_filter=status_filter,
                         operation_type_filter=operation_type_filter,
                         priority_filter=priority_filter)

@operations_bp.route('/<int:operation_id>')
@login_required
def view_operation(operation_id):
    """عرض تفاصيل العملية"""
    
    if current_user.role != UserRole.ADMIN:
        flash('غير مسموح لك بالوصول لهذه الصفحة', 'danger')
        return redirect(url_for('dashboard.index'))
    
    operation = OperationRequest.query.get_or_404(operation_id)
    related_record = operation.get_related_record()
    
    # جلب بيانات الموظف إذا كانت متاحة
    employee = None
    if related_record:
        # محاولة العثور على الموظف من خلال رقم الهوية أو الاسم
        if hasattr(related_record, 'driver_residency_number') and related_record.driver_residency_number:
            employee = Employee.query.filter_by(national_id=related_record.driver_residency_number).first()
        if not employee and hasattr(related_record, 'person_name') and related_record.person_name:
            employee = Employee.query.filter_by(name=related_record.person_name).first()
        if not employee and hasattr(related_record, 'driver_name') and related_record.driver_name:
            employee = Employee.query.filter_by(name=related_record.driver_name).first()
    
    return render_template('operations/view.html', 
                         operation=operation,
                         related_record=related_record,
                         employee=employee)

@operations_bp.route('/<int:operation_id>/approve', methods=['POST'])
@login_required
def approve_operation(operation_id):
    """الموافقة على العملية"""
    
    if current_user.role != UserRole.ADMIN:
        return jsonify({'success': False, 'message': 'غير مسموح'})
    
    operation = OperationRequest.query.get_or_404(operation_id)
    review_notes = request.form.get('review_notes', '').strip()
    
    try:
        # تحديث حالة العملية
        operation.status = 'approved'
        operation.reviewed_by = current_user.id
        operation.reviewed_at = datetime.utcnow()
        operation.review_notes = review_notes
        
        # إنشاء إشعار للطالب
        create_notification(
            operation_id=operation.id,
            user_id=operation.requested_by,
            notification_type='status_change',
            title=f'تمت الموافقة على العملية: {operation.title}',
            message=f'تمت الموافقة على العملية من قبل {current_user.username}.\n{review_notes if review_notes else ""}'
        )
        
        db.session.commit()
        
        # تسجيل العملية
        log_audit('approve', 'operation_request', operation.id, 
                 f'تمت الموافقة على العملية: {operation.title}')
        
        flash('تمت الموافقة على العملية بنجاح', 'success')
        return jsonify({'success': True, 'message': 'تمت الموافقة بنجاح'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'حدث خطأ: {str(e)}'})

@operations_bp.route('/<int:operation_id>/reject', methods=['POST'])
@login_required
def reject_operation(operation_id):
    """رفض العملية"""
    
    if current_user.role != UserRole.ADMIN:
        return jsonify({'success': False, 'message': 'غير مسموح'})
    
    operation = OperationRequest.query.get_or_404(operation_id)
    review_notes = request.form.get('review_notes', '').strip()
    
    if not review_notes:
        return jsonify({'success': False, 'message': 'يجب إدخال سبب الرفض'})
    
    try:
        # تحديث حالة العملية
        operation.status = 'rejected'
        operation.reviewed_by = current_user.id
        operation.reviewed_at = datetime.utcnow()
        operation.review_notes = review_notes
        
        # إنشاء إشعار للطالب
        create_notification(
            operation_id=operation.id,
            user_id=operation.requested_by,
            notification_type='status_change',
            title=f'تم رفض العملية: {operation.title}',
            message=f'تم رفض العملية من قبل {current_user.username}.\nالسبب: {review_notes}'
        )
        
        db.session.commit()
        
        # تسجيل العملية
        log_audit('reject', 'operation_request', operation.id, 
                 f'تم رفض العملية: {operation.title} - السبب: {review_notes}')
        
        flash('تم رفض العملية', 'warning')
        return jsonify({'success': True, 'message': 'تم رفض العملية'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'حدث خطأ: {str(e)}'})

@operations_bp.route('/<int:operation_id>/under-review', methods=['POST'])
@login_required  
def set_under_review(operation_id):
    """وضع العملية تحت المراجعة"""
    
    if current_user.role != UserRole.ADMIN:
        return jsonify({'success': False, 'message': 'غير مسموح'})
    
    operation = OperationRequest.query.get_or_404(operation_id)
    
    try:
        operation.status = 'under_review'
        operation.reviewed_by = current_user.id
        operation.reviewed_at = datetime.utcnow()
        
        # إنشاء إشعار للطالب
        create_notification(
            operation_id=operation.id,
            user_id=operation.requested_by,
            notification_type='status_change',
            title=f'العملية تحت المراجعة: {operation.title}',
            message=f'العملية قيد المراجعة من قبل {current_user.username}'
        )
        
        db.session.commit()
        
        log_audit('review', 'operation_request', operation.id, 
                 f'العملية تحت المراجعة: {operation.title}')
        
        return jsonify({'success': True, 'message': 'تم وضع العملية تحت المراجعة'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'حدث خطأ: {str(e)}'})

@operations_bp.route('/<int:operation_id>/delete', methods=['POST'])
@login_required
def delete_operation(operation_id):
    """حذف العملية"""
    
    if current_user.role != UserRole.ADMIN:
        return jsonify({'success': False, 'message': 'غير مسموح لك بحذف العمليات'})
    
    operation = OperationRequest.query.get_or_404(operation_id)
    
    try:
        # تسجيل العملية قبل الحذف
        operation_title = operation.title
        operation_type = operation.operation_type
        
        # حذف الإشعارات المرتبطة بالعملية أولاً
        notifications = OperationNotification.query.filter_by(operation_id=operation_id).all()
        for notification in notifications:
            db.session.delete(notification)
        
        # حذف العملية
        db.session.delete(operation)
        db.session.commit()
        
        # تسجيل عملية الحذف
        log_audit('delete', 'operation_request', operation_id, 
                 f'تم حذف العملية: {operation_title} من النوع {operation_type}')
        
        flash('تم حذف العملية بنجاح', 'success')
        return jsonify({'success': True, 'message': 'تم حذف العملية بنجاح'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'حدث خطأ أثناء الحذف: {str(e)}'})

@operations_bp.route('/notifications')
@login_required
def notifications():
    """عرض الإشعارات"""
    
    user_notifications = OperationNotification.query.filter_by(
        user_id=current_user.id
    ).order_by(OperationNotification.created_at.desc()).all()
    
    # تحديد الإشعارات كمقروءة
    OperationNotification.query.filter_by(
        user_id=current_user.id, 
        is_read=False
    ).update({'is_read': True, 'read_at': datetime.utcnow()})
    
    db.session.commit()
    
    return render_template('operations/notifications.html', 
                         notifications=user_notifications)

def create_operation_request(operation_type, related_record_id, vehicle_id, 
                           title, description, requested_by, priority='normal'):
    """إنشاء طلب عملية جديد"""
    
    operation = OperationRequest()
    operation.operation_type = operation_type
    operation.related_record_id = related_record_id
    operation.vehicle_id = vehicle_id
    operation.title = title
    operation.description = description
    operation.requested_by = requested_by
    operation.requested_at = datetime.utcnow()
    operation.priority = priority
    operation.status = 'pending'
    
    try:
        db.session.add(operation)
        db.session.flush()  # للحصول على ID
        
        # إنشاء إشعارات للمديرين
        admins = User.query.filter_by(role=UserRole.ADMIN).all()
        for admin in admins:
            create_notification(
                operation_id=operation.id,
                user_id=admin.id,
                notification_type='new_operation',
                title=f'عملية جديدة تحتاج موافقة: {title}',
                message=f'عملية جديدة من نوع {get_operation_type_name(operation_type)} تحتاج للمراجعة والموافقة.'
            )
        
        # لا نحفظ هنا، الدالة المستدعية مسؤولة عن الحفظ
        return operation
    except Exception as e:
        print(f"خطأ في create_operation_request: {str(e)}")
        import traceback
        traceback.print_exc()
        raise e

def create_notification(operation_id, user_id, notification_type, title, message):
    """إنشاء إشعار جديد"""
    
    notification = OperationNotification()
    notification.operation_request_id = operation_id
    notification.user_id = user_id
    notification.notification_type = notification_type
    notification.title = title
    notification.message = message
    
    db.session.add(notification)
    return notification

def get_operation_type_name(operation_type):
    """الحصول على اسم نوع العملية بالعربية"""
    
    type_names = {
        'handover': 'تسليم/استلام مركبة',
        'workshop': 'عملية ورشة',
        'external_authorization': 'تفويض خارجي',
        'safety_inspection': 'فحص سلامة'
    }
    
    return type_names.get(operation_type, operation_type)

# دالة مساعدة للحصول على عدد العمليات المعلقة للمدير
def get_pending_operations_count():
    """الحصول على عدد العمليات المعلقة"""
    return OperationRequest.query.filter_by(status='pending').count()

# دالة مساعدة للحصول على عدد الإشعارات غير المقروءة
def get_unread_notifications_count(user_id):
    """الحصول على عدد الإشعارات غير المقروءة للمستخدم"""
    return OperationNotification.query.filter_by(
        user_id=user_id, 
        is_read=False
    ).count()

@operations_bp.route('/api/count')
@login_required
def api_operations_count():
    """API للحصول على إحصائيات العمليات"""
    
    if current_user.role != UserRole.ADMIN:
        return jsonify({'error': 'غير مسموح'})
    
    pending_count = OperationRequest.query.filter_by(status='pending').count()
    under_review_count = OperationRequest.query.filter_by(status='under_review').count()
    
    return jsonify({
        'pending': pending_count,
        'under_review': under_review_count,
        'unread_notifications': get_unread_notifications_count(current_user.id)
    })