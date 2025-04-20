"""
مسارات إدارة المستخدمين والصلاحيات
توفر هذه الوحدة المسارات اللازمة لإدارة المستخدمين وأدوارهم وصلاحياتهم
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, g
from flask_login import login_required, current_user
from app import db
from models import User, UserPermission, UserRole, Module, Permission
from utils.user_helpers import create_default_permissions, get_role_display_name, get_module_display_name, format_permissions, requires_permission
from utils.audit_helpers import log_create, log_update, log_delete
from werkzeug.security import generate_password_hash

# إنشاء مخطط للمسارات
users_bp = Blueprint('users', __name__, url_prefix='/users')

@users_bp.route('/')
@login_required
@requires_permission(Module.USERS, Permission.VIEW)
def index():
    """صفحة قائمة المستخدمين"""
    users = User.query.all()
    return render_template('users/index.html', users=users, get_role_display_name=get_role_display_name)

@users_bp.route('/view/<int:id>')
@login_required
@requires_permission(Module.USERS, Permission.VIEW)
def view(id):
    """عرض تفاصيل المستخدم"""
    user = User.query.get_or_404(id)
    return render_template('users/view.html', user=user, 
                          get_role_display_name=get_role_display_name,
                          get_module_display_name=get_module_display_name,
                          format_permissions=format_permissions)

@users_bp.route('/create', methods=['GET', 'POST'])
@login_required
@requires_permission(Module.USERS, Permission.CREATE)
def create():
    """إنشاء مستخدم جديد"""
    from forms.user_forms import UserForm
    
    form = UserForm()
    
    if form.validate_on_submit():
        # التحقق من عدم وجود مستخدم بنفس البريد الإلكتروني
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('البريد الإلكتروني مستخدم بالفعل', 'danger')
            return render_template('users/create.html', form=form)
        
        # إنشاء المستخدم الجديد
        user = User(
            email=form.email.data,
            name=form.name.data,
            role=form.role.data,
            is_active=form.is_active.data
        )
        
        # تعيين كلمة المرور إذا تم تقديمها
        if form.password.data:
            user.set_password(form.password.data)
            
        db.session.add(user)
        db.session.commit()
        
        # إنشاء الصلاحيات الافتراضية للمستخدم
        create_default_permissions(user)
        
        # تسجيل العملية
        log_create('user', user, 'email', 'تم إنشاء مستخدم جديد')
        
        flash('تم إنشاء المستخدم بنجاح', 'success')
        return redirect(url_for('users.index'))
    
    return render_template('users/create.html', form=form)

@users_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@requires_permission(Module.USERS, Permission.EDIT)
def edit(id):
    """تعديل بيانات المستخدم"""
    from forms.user_forms import UserForm
    
    user = User.query.get_or_404(id)
    
    # حفظ نسخة من البيانات القديمة للمراقبة
    old_data = {
        'email': user.email,
        'name': user.name,
        'role': user.role.value if user.role else None,
        'is_active': user.is_active
    }
    
    form = UserForm(obj=user)
    
    if form.validate_on_submit():
        # التحقق من عدم وجود مستخدم آخر بنفس البريد الإلكتروني
        existing_user = User.query.filter(User.email == form.email.data, User.id != id).first()
        if existing_user:
            flash('البريد الإلكتروني مستخدم بالفعل', 'danger')
            return render_template('users/edit.html', form=form, user=user)
        
        # تحديث بيانات المستخدم
        user.email = form.email.data
        user.name = form.name.data
        
        # تحديث كلمة المرور فقط إذا تم تقديمها
        if form.password.data:
            user.set_password(form.password.data)
        
        # إذا تغير الدور، نحذف الصلاحيات القديمة ونضيف الصلاحيات الجديدة
        if user.role != form.role.data:
            user.role = form.role.data
            
            # حذف الصلاحيات القديمة
            UserPermission.query.filter_by(user_id=user.id).delete()
            db.session.commit()
            
            # إضافة الصلاحيات الجديدة
            create_default_permissions(user)
        else:
            user.role = form.role.data
            
        user.is_active = form.is_active.data
        
        db.session.commit()
        
        # تسجيل العملية
        log_update('user', user, old_data, 'email', 'تم تحديث بيانات المستخدم')
        
        flash('تم تحديث بيانات المستخدم بنجاح', 'success')
        return redirect(url_for('users.view', id=user.id))
    
    return render_template('users/edit.html', form=form, user=user)

@users_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
@requires_permission(Module.USERS, Permission.DELETE)
def delete(id):
    """حذف مستخدم"""
    user = User.query.get_or_404(id)
    
    # لا يمكن حذف المستخدم الحالي
    if user.id == current_user.id:
        flash('لا يمكن حذف المستخدم الحالي', 'danger')
        return redirect(url_for('users.index'))
    
    # حفظ بيانات المستخدم قبل الحذف للمراقبة
    old_data = {
        'id': user.id,
        'email': user.email,
        'name': user.name,
        'role': user.role.value if user.role else None
    }
    
    # حذف المستخدم وجميع صلاحياته
    db.session.delete(user)
    db.session.commit()
    
    # تسجيل العملية
    log_delete('user', old_data['id'], old_data, old_data['email'], 'تم حذف المستخدم')
    
    flash('تم حذف المستخدم بنجاح', 'success')
    return redirect(url_for('users.index'))

@users_bp.route('/permissions/<int:id>', methods=['GET', 'POST'])
@login_required
@requires_permission(Module.USERS, Permission.MANAGE)
def permissions(id):
    """إدارة صلاحيات المستخدم"""
    user = User.query.get_or_404(id)
    
    if request.method == 'POST':
        # حذف جميع الصلاحيات الحالية
        UserPermission.query.filter_by(user_id=user.id).delete()
        
        # الحصول على الصلاحيات المحددة من النموذج
        for module in Module:
            module_permissions = 0
            
            if f'view_{module.value}' in request.form:
                module_permissions |= Permission.VIEW
                
            if f'create_{module.value}' in request.form:
                module_permissions |= Permission.CREATE
                
            if f'edit_{module.value}' in request.form:
                module_permissions |= Permission.EDIT
                
            if f'delete_{module.value}' in request.form:
                module_permissions |= Permission.DELETE
                
            if f'manage_{module.value}' in request.form:
                module_permissions |= Permission.MANAGE
            
            # إضافة الصلاحيات فقط إذا كانت موجودة
            if module_permissions > 0:
                permission = UserPermission(
                    user_id=user.id,
                    module=module,
                    permissions=module_permissions
                )
                db.session.add(permission)
        
        db.session.commit()
        
        # تسجيل العملية
        log_update('user_permissions', user, None, 'email', 'تم تحديث صلاحيات المستخدم')
        
        flash('تم تحديث صلاحيات المستخدم بنجاح', 'success')
        return redirect(url_for('users.view', id=user.id))
    
    # قائمة بالصلاحيات الحالية
    user_permissions = {}
    for permission in user.permissions:
        user_permissions[permission.module.value] = permission.permissions
    
    return render_template('users/permissions.html', 
                          user=user, 
                          modules=Module, 
                          user_permissions=user_permissions,
                          Permission=Permission,
                          get_module_display_name=get_module_display_name)

@users_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """الملف الشخصي للمستخدم الحالي"""
    from forms.user_forms import ProfileForm
    
    form = ProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        # حفظ البيانات القديمة للمراقبة
        old_data = {
            'name': current_user.name,
            'email': current_user.email
        }
        
        # تحديث البيانات
        current_user.name = form.name.data
        
        # تحديث كلمة المرور فقط إذا تم تقديمها
        if form.password.data:
            current_user.set_password(form.password.data)
        
        db.session.commit()
        
        # تسجيل العملية
        log_update('user', current_user, old_data, 'email', 'تم تحديث الملف الشخصي')
        
        flash('تم تحديث الملف الشخصي بنجاح', 'success')
        return redirect(url_for('users.profile'))
    
    return render_template('users/profile.html', form=form, user=current_user)