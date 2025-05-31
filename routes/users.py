from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app import db
from models import User, Department, UserRole, Module, Permission, AuditLog
from functools import wraps

users_bp = Blueprint('users', __name__, url_prefix='/users')

def admin_required(f):
    """Decorator to require admin access"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != UserRole.ADMIN:
            flash('ليس لديك صلاحية للوصول إلى هذه الصفحة', 'error')
            return redirect(url_for('attendance.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@users_bp.route('/')
@login_required
@admin_required
def index():
    """قائمة المستخدمين"""
    users = User.query.all()
    departments = Department.query.all()
    return render_template('users/index.html', users=users, departments=departments)

@users_bp.route('/assign_department/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def assign_department(user_id):
    """تحديد قسم للمستخدم"""
    user = User.query.get_or_404(user_id)
    department_id = request.form.get('department_id')
    
    if department_id and department_id != '':
        department_id = int(department_id)
        department = Department.query.get(department_id)
        if not department:
            flash('القسم غير موجود', 'error')
            return redirect(url_for('users.index'))
        
        user.assigned_department_id = department_id
        flash(f'تم تحديد قسم "{department.name}" للمستخدم {user.name}', 'success')
    else:
        user.assigned_department_id = None
        flash(f'تم إلغاء تحديد القسم للمستخدم {user.name}', 'info')
    
    db.session.commit()
    return redirect(url_for('users.index'))

@users_bp.route('/edit_role/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def edit_role(user_id):
    """تحديث دور المستخدم"""
    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role')
    
    if new_role in [role.value for role in UserRole]:
        user.role = UserRole(new_role)
        db.session.commit()
        flash(f'تم تحديث دور المستخدم {user.name} إلى {new_role}', 'success')
    else:
        flash('الدور المحدد غير صالح', 'error')
    
    return redirect(url_for('users.index'))

@users_bp.route('/permissions/<int:user_id>')
@login_required
@admin_required
def user_permissions(user_id):
    """إدارة صلاحيات المستخدم التفصيلية"""
    user = User.query.get_or_404(user_id)
    modules = list(Module)
    return render_template('users/permissions.html', user=user, modules=modules)

@users_bp.route('/toggle_active/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def toggle_active(user_id):
    """تفعيل/إلغاء تفعيل المستخدم"""
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    
    status = "تفعيل" if user.is_active else "إلغاء تفعيل"
    flash(f'تم {status} المستخدم {user.name}', 'success')
    return redirect(url_for('users.index'))

@users_bp.route('/department_users/<int:department_id>')
@login_required
@admin_required
def department_users(department_id):
    """عرض جميع المستخدمين المخصصين لقسم معين"""
    department = Department.query.get_or_404(department_id)
    users = User.query.filter_by(assigned_department_id=department_id).all()
    return jsonify({
        'department': department.name,
        'users': [{'id': u.id, 'name': u.name, 'email': u.email, 'role': u.role.value} for u in users]
    })

@users_bp.route('/view/<int:id>')
@login_required
@admin_required
def view(id):
    """عرض تفاصيل مستخدم"""
    user = User.query.get_or_404(id)
    
    # جلب آخر 10 أنشطة للمستخدم
    recent_activities = AuditLog.query.filter_by(user_id=id).order_by(AuditLog.timestamp.desc()).limit(10).all()
    
    return render_template('users/view.html', user=user, recent_activities=recent_activities)

@users_bp.route('/activity_logs')
@login_required
@admin_required
def activity_logs():
    """عرض قائمة المستخدمين لاختيار سجل النشاط"""
    users = User.query.all()
    return render_template('users/activity_logs.html', users=users)

@users_bp.route('/activity_log/<int:id>')
@login_required
@admin_required
def activity_log(id):
    """عرض سجل النشاط الكامل للمستخدم"""
    user = User.query.get_or_404(id)
    
    # معاملات التصفية
    action_filter = request.args.get('action', '')
    entity_filter = request.args.get('entity_type', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    # بناء الاستعلام
    query = AuditLog.query.filter_by(user_id=id)
    
    # تشخيص: طباعة عدد السجلات للمستخدم
    total_logs = query.count()
    print(f"إجمالي سجلات النشاط للمستخدم {id}: {total_logs}")
    
    if action_filter:
        query = query.filter(AuditLog.action == action_filter)
    
    if entity_filter:
        query = query.filter(AuditLog.entity_type == entity_filter)
    
    if date_from:
        try:
            from datetime import datetime
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(AuditLog.timestamp >= date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            from datetime import datetime
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
            query = query.filter(AuditLog.timestamp <= date_to_obj)
        except ValueError:
            pass
    
    # ترتيب وتقسيم الصفحات
    activities = query.order_by(AuditLog.timestamp.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # تشخيص: طباعة عدد السجلات في الصفحة الحالية
    print(f"عدد السجلات في الصفحة الحالية: {len(activities.items)}")
    if activities.items:
        print(f"أول سجل: {activities.items[0].action} - {activities.items[0].details}")
    
    # جلب قائمة الإجراءات والكيانات الفريدة للفلتر
    actions = db.session.query(AuditLog.action).filter_by(user_id=id).distinct().all()
    entity_types = db.session.query(AuditLog.entity_type).filter_by(user_id=id).distinct().all()
    
    return render_template('users/activity_log.html', 
                         user=user, 
                         activities=activities,
                         actions=[a[0] for a in actions],
                         entity_types=[e[0] for e in entity_types],
                         current_filters={
                             'action': action_filter,
                             'entity_type': entity_filter,
                             'date_from': date_from,
                             'date_to': date_to
                         })