from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app import db
from models import User, Department, UserRole, Module, Permission, UserPermission, AuditLog, UserDepartmentAccess
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
    departments = Department.query.all()
    return render_template('users/permissions.html', user=user, modules=modules, departments=departments)

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

@users_bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add():
    """إضافة مستخدم جديد"""
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            role = request.form.get('role', 'user')
            department_id = request.form.get('department_id')
            
            # التحقق من البيانات المطلوبة
            if not name or not email or not password:
                flash('جميع الحقول مطلوبة', 'error')
                return redirect(url_for('users.add'))
            
            # التحقق من عدم وجود مستخدم بنفس البريد الإلكتروني
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash('يوجد مستخدم آخر بنفس البريد الإلكتروني', 'error')
                return redirect(url_for('users.add'))
            
            # إنشاء المستخدم الجديد
            new_user = User(
                name=name,
                email=email,
                role=UserRole(role),
                is_active=True
            )
            new_user.set_password(password)
            
            # تحديد القسم إذا تم اختياره
            if department_id and department_id != '':
                new_user.assigned_department_id = int(department_id)
            
            db.session.add(new_user)
            db.session.commit()
            
            flash(f'تم إضافة المستخدم {name} بنجاح', 'success')
            return redirect(url_for('users.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ: {str(e)}', 'error')
    
    departments = Department.query.all()
    return render_template('users/add.html', departments=departments)

@users_bp.route('/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(user_id):
    """تعديل مستخدم"""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        try:
            user.name = request.form.get('name')
            email = request.form.get('email')
            role = request.form.get('role')
            department_id = request.form.get('department_id')
            password = request.form.get('password')
            
            # التحقق من البيانات المطلوبة
            if not user.name or not email:
                flash('الاسم والبريد الإلكتروني مطلوبان', 'error')
                return redirect(url_for('users.edit', user_id=user_id))
            
            # التحقق من عدم وجود مستخدم آخر بنفس البريد الإلكتروني
            existing_user = User.query.filter_by(email=email).filter(User.id != user_id).first()
            if existing_user:
                flash('يوجد مستخدم آخر بنفس البريد الإلكتروني', 'error')
                return redirect(url_for('users.edit', user_id=user_id))
            
            user.email = email
            user.role = UserRole(role)
            
            # تحديد القسم
            if department_id and department_id != '':
                user.assigned_department_id = int(department_id)
            else:
                user.assigned_department_id = None
            
            # تحديث كلمة المرور إذا تم إدخالها
            if password:
                user.set_password(password)
            
            db.session.commit()
            flash(f'تم تحديث بيانات المستخدم {user.name} بنجاح', 'success')
            return redirect(url_for('users.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ: {str(e)}', 'error')
    
    departments = Department.query.all()
    return render_template('users/edit.html', user=user, departments=departments)

@users_bp.route('/confirm_delete/<int:user_id>')
@login_required
@admin_required
def confirm_delete(user_id):
    """صفحة تأكيد حذف المستخدم"""
    user = User.query.get_or_404(user_id)
    
    # منع المستخدم من حذف نفسه
    if user.id == current_user.id:
        flash('لا يمكنك حذف حسابك الخاص', 'error')
        return redirect(url_for('users.index'))
    
    return render_template('users/confirm_delete.html', user=user)

@users_bp.route('/delete/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete(user_id):
    """حذف مستخدم"""
    user = User.query.get_or_404(user_id)
    
    # منع المستخدم من حذف نفسه
    if user.id == current_user.id:
        flash('لا يمكنك حذف حسابك الخاص', 'error')
        return redirect(url_for('users.index'))
    
    try:
        user_name = user.name
        
        # حذف المستخدم من قاعدة البيانات
        db.session.delete(user)
        db.session.commit()
        
        flash(f'تم حذف المستخدم {user_name} بنجاح', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء حذف المستخدم: {str(e)}', 'error')
    
    return redirect(url_for('users.index'))

@users_bp.route('/update_permissions/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def update_permissions(user_id):
    """تحديث صلاحيات المستخدم التفصيلية"""
    user = User.query.get_or_404(user_id)
    
    # منع تعديل صلاحيات المديرين
    if user.role == UserRole.ADMIN:
        flash('لا يمكن تعديل صلاحيات المديرين', 'error')
        return redirect(url_for('users.user_permissions', user_id=user_id))
    
    try:
        # جلب الصلاحيات المحددة
        selected_permissions = request.form.getlist('permissions')
        
        # تحديث الوصول للأقسام
        department_access = request.form.get('department_access')
        accessible_departments = request.form.getlist('accessible_departments')
        
        # حذف جميع الأقسام المخصصة الحالية
        UserDepartmentAccess.query.filter_by(user_id=user_id).delete()
        
        if department_access == 'all':
            user.assigned_department_id = None
        elif department_access == 'specific' and accessible_departments:
            # إضافة الأقسام المتعددة المحددة
            for dept_id in accessible_departments:
                new_access = UserDepartmentAccess(
                    user_id=user_id,
                    department_id=int(dept_id)
                )
                db.session.add(new_access)
            
            # تعيين أول قسم كقسم رئيسي (للتوافق مع النظام الحالي)
            user.assigned_department_id = int(accessible_departments[0])
        else:
            user.assigned_department_id = None
        
        # حذف جميع صلاحيات المستخدم الحالية
        UserPermission.query.filter_by(user_id=user_id).delete()
        
        # تجميع الصلاحيات حسب الوحدة
        module_permissions = {}
        for permission_str in selected_permissions:
            module_name, permission_value = permission_str.split('_')
            permission_value = int(permission_value)
            
            if module_name not in module_permissions:
                module_permissions[module_name] = 0
            module_permissions[module_name] |= permission_value
        
        # إضافة الصلاحيات الجديدة
        for module_name, combined_permissions in module_permissions.items():
            module = Module[module_name]
            
            new_permission = UserPermission(
                user_id=user_id,
                module=module,
                permissions=combined_permissions
            )
            db.session.add(new_permission)
        
        db.session.commit()
        
        # تسجيل العملية في سجل النشاط
        audit_log = AuditLog(
            user_id=current_user.id,
            action='تحديث الصلاحيات',
            entity_type='مستخدم',
            entity_id=user_id,
            details=f'تم تحديث صلاحيات المستخدم {user.name}'
        )
        db.session.add(audit_log)
        db.session.commit()
        
        flash(f'تم تحديث صلاحيات المستخدم {user.name} بنجاح', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء تحديث الصلاحيات: {str(e)}', 'error')
    
    return redirect(url_for('users.user_permissions', user_id=user_id))