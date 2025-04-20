import logging
from datetime import datetime, timedelta
from typing import Dict, Optional

# Flask imports
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from sqlalchemy import desc

# Project imports
from app import db
from werkzeug.security import generate_password_hash
from models import User, UserRole, Module, Permission, UserPermission, Employee, SystemAudit
from forms.user_forms import CreateUserForm, EditUserForm, UserSearchForm, UserPermissionsForm
from utils.user_helpers import (
    get_role_display_name, get_module_display_name, format_permissions,
    create_user, update_user, delete_user, create_default_permissions,
    update_user_permissions, get_available_employees, require_module_access
)
from utils.audit_helpers import log_create, log_update, log_delete

# إعداد التسجيل
logger = logging.getLogger(__name__)

# إنشاء blueprint للمستخدمين
users_bp = Blueprint('users', __name__)

@users_bp.context_processor
def inject_user_helpers():
    """إضافة دوال المساعدة إلى جميع القوالب"""
    return {
        'get_role_display_name': get_role_display_name,
        'get_module_display_name': get_module_display_name,
        'format_permissions': format_permissions,
        'UserRole': UserRole,
        'Module': Module,
        'Permission': Permission
    }

@users_bp.route('/')
@login_required
@require_module_access(Module.USERS, Permission.VIEW)
def index():
    """عرض قائمة المستخدمين"""
    form = UserSearchForm(request.args, meta={'csrf': False})
    
    # البحث عن المستخدمين
    query = User.query
    
    # تطبيق مرشحات البحث
    if form.query.data:
        search_term = f"%{form.query.data}%"
        query = query.filter(
            (User.name.ilike(search_term)) |
            (User.email.ilike(search_term))
        )
    
    if form.role.data:
        query = query.filter(User.role == form.role.data)
    
    if form.status.data:
        is_active = form.status.data == 'active'
        query = query.filter(User.is_active == is_active)
    
    # الحصول على المستخدمين
    users = query.order_by(User.name).all()
    
    # عرض قالب قائمة المستخدمين
    return render_template('users/index.html', users=users, form=form)

@users_bp.route('/create', methods=['GET', 'POST'])
@login_required
@require_module_access(Module.USERS, Permission.CREATE)
def create():
    """إضافة مستخدم جديد"""
    form = CreateUserForm()
    
    # تحديث خيارات الموظفين في النموذج
    employees = get_available_employees()
    form.employee_id.choices = [(-1, 'لا يوجد')] + employees
    
    if form.validate_on_submit():
        try:
            # إنشاء المستخدم الجديد
            user = create_user(
                name=form.name.data,
                email=form.email.data,
                role=form.role.data,
                password=form.password.data,
                is_active=form.is_active.data,
                employee_id=form.employee_id.data if form.employee_id.data != -1 else None,
                auth_type='local'
            )
            
            flash('تم إضافة المستخدم بنجاح', 'success')
            log_create('user', user, 'تم إنشاء مستخدم جديد')
            return redirect(url_for('users.view', id=user.id))
            
        except Exception as e:
            flash(f'حدث خطأ أثناء إضافة المستخدم: {str(e)}', 'danger')
            logger.error(f"Error creating user: {str(e)}")
    
    return render_template('users/create.html', form=form)

@users_bp.route('/view/<int:id>')
@login_required
@require_module_access(Module.USERS, Permission.VIEW)
def view(id):
    """عرض تفاصيل المستخدم"""
    user = User.query.get_or_404(id)
    return render_template('users/view.html', user=user)

@users_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@require_module_access(Module.USERS, Permission.EDIT)
def edit(id):
    """تعديل معلومات المستخدم"""
    user = User.query.get_or_404(id)
    form = EditUserForm(obj=user, user_id=id)
    
    # تحديث خيارات الموظفين في النموذج
    employees = get_available_employees()
    form.employee_id.choices = [(-1, 'لا يوجد')] + employees
    
    if form.validate_on_submit():
        try:
            # تحديث معلومات المستخدم
            update_user(
                user_id=id,
                name=form.name.data,
                email=form.email.data,
                role=form.role.data,
                password=form.password.data if form.password.data else None,
                is_active=form.is_active.data,
                employee_id=form.employee_id.data,
                update_permissions=True
            )
            
            flash('تم تحديث معلومات المستخدم بنجاح', 'success')
            log_update('user', user, None, 'تم تحديث بيانات المستخدم')
            return redirect(url_for('users.view', id=id))
            
        except Exception as e:
            flash(f'حدث خطأ أثناء تحديث المستخدم: {str(e)}', 'danger')
            logger.error(f"Error updating user: {str(e)}")
    
    # ضبط القيم الافتراضية للنموذج
    if request.method == 'GET':
        form.employee_id.data = user.employee_id if user.employee_id else -1
    
    return render_template('users/edit.html', form=form, user=user)

@users_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
@require_module_access(Module.USERS, Permission.DELETE)
def delete(id):
    """حذف مستخدم"""
    # لا يمكن حذف المستخدم الحالي
    if current_user.id == id:
        flash('لا يمكنك حذف حسابك الشخصي', 'danger')
        return redirect(url_for('users.index'))
    
    # التحقق من وجود المستخدم
    user = User.query.get_or_404(id)
    
    try:
        # حذف المستخدم
        delete_user(id)
        flash('تم حذف المستخدم بنجاح', 'success')
        return redirect(url_for('users.index'))
        
    except Exception as e:
        flash(f'حدث خطأ أثناء حذف المستخدم: {str(e)}', 'danger')
        logger.error(f"Error deleting user: {str(e)}")
        return redirect(url_for('users.view', id=id))

@users_bp.route('/permissions/<int:id>', methods=['GET', 'POST'])
@login_required
@require_module_access(Module.USERS, Permission.EDIT)
def permissions(id):
    """تعديل صلاحيات المستخدم"""
    user = User.query.get_or_404(id)
    
    # لا يمكن تعديل صلاحيات المدير
    if user.role == UserRole.ADMIN:
        flash('لا يمكن تعديل صلاحيات مدير النظام', 'warning')
        return redirect(url_for('users.view', id=id))
    
    # تحويل الصلاحيات الحالية إلى قاموس
    current_permissions = {}
    for p in user.permissions:
        current_permissions[p.module.value] = p.permissions
    
    if request.method == 'POST':
        # جمع الصلاحيات من النموذج
        new_permissions = {}
        for module in Module:
            # تجاهل وحدة إدارة المستخدمين للمستخدمين العاديين
            if module == Module.USERS and user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
                continue
                
            module_key = f"module_{module.value}"
            if module_key in request.form:
                permission_value = 0
                
                # جمع الصلاحيات المختارة
                for permission in [Permission.VIEW, Permission.CREATE, Permission.EDIT, Permission.DELETE]:
                    perm_key = f"{module.value}_{permission}"
                    if perm_key in request.form:
                        permission_value |= permission
                
                # التحقق من صلاحية "إدارة"
                manage_key = f"{module.value}_{Permission.MANAGE}"
                if manage_key in request.form:
                    permission_value |= Permission.MANAGE
                
                # إضافة الصلاحيات إلى القاموس
                if permission_value > 0:
                    new_permissions[module.value] = permission_value
        
        try:
            # تحديث صلاحيات المستخدم
            update_user_permissions(id, new_permissions)
            flash('تم تحديث صلاحيات المستخدم بنجاح', 'success')
            log_update('user_permissions', user, None, 'تم تحديث صلاحيات المستخدم')
            return redirect(url_for('users.view', id=id))
            
        except Exception as e:
            flash(f'حدث خطأ أثناء تحديث الصلاحيات: {str(e)}', 'danger')
            logger.error(f"Error updating permissions: {str(e)}")
    
    return render_template(
        'users/permissions.html',
        user=user,
        modules=Module,
        permissions=[Permission.VIEW, Permission.CREATE, Permission.EDIT, Permission.DELETE, Permission.MANAGE],
        current_permissions=current_permissions
    )

@users_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """عرض وتعديل الملف الشخصي للمستخدم الحالي"""
    form = EditUserForm(obj=current_user, user_id=current_user.id)
    
    # إخفاء حقول معينة في الملف الشخصي
    delattr(form, 'role')
    delattr(form, 'is_active')
    delattr(form, 'employee_id')
    
    if form.validate_on_submit():
        try:
            # تحديث معلومات المستخدم
            update_user(
                user_id=current_user.id,
                name=form.name.data,
                email=form.email.data,
                password=form.password.data if form.password.data else None
            )
            
            flash('تم تحديث الملف الشخصي بنجاح', 'success')
            log_update('user', current_user, None, 'تم تحديث الملف الشخصي')
            return redirect(url_for('users.profile'))
            
        except Exception as e:
            flash(f'حدث خطأ أثناء تحديث الملف الشخصي: {str(e)}', 'danger')
            logger.error(f"Error updating profile: {str(e)}")
    
    return render_template('users/profile.html', form=form, user=current_user)

@users_bp.route('/api/check-email', methods=['POST'])
@login_required
def check_email():
    """التحقق من توفر البريد الإلكتروني (AJAX)"""
    email = request.json.get('email')
    user_id = request.json.get('user_id')
    
    if not email:
        return jsonify({'valid': False, 'message': 'البريد الإلكتروني مطلوب'})
    
    # البحث عن المستخدم بالبريد الإلكتروني
    query = User.query.filter(User.email == email)
    
    # استثناء المستخدم الحالي عند التعديل
    if user_id:
        query = query.filter(User.id != int(user_id))
    
    user = query.first()
    
    if user:
        return jsonify({'valid': False, 'message': 'البريد الإلكتروني مستخدم بالفعل'})
    
    return jsonify({'valid': True})

@users_bp.route('/activity/<int:id>')
@login_required
@require_module_access(Module.USERS, Permission.VIEW)
def activity_log(id):
    """عرض سجل نشاط المستخدم"""
    # التحقق من وجود المستخدم
    user = User.query.get_or_404(id)
    
    # الحصول على عدد الأيام للعرض (افتراضي: آخر 30 يوم)
    days = request.args.get('days', 30, type=int)
    
    # حساب تاريخ البداية
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # البحث عن سجلات النشاط للمستخدم
    activities = SystemAudit.query.filter(
        SystemAudit.user_id == id,
        SystemAudit.timestamp >= start_date
    ).order_by(desc(SystemAudit.timestamp)).all()
    
    # عرض صفحة سجل النشاط
    return render_template(
        'users/activity_log.html',
        user=user,
        activities=activities,
        days=days
    )

@users_bp.route('/api/reset-permissions/<int:id>', methods=['POST'])
@login_required
@require_module_access(Module.USERS, Permission.EDIT)
def reset_permissions(id):
    """إعادة تعيين صلاحيات المستخدم إلى الإعدادات الافتراضية"""
    user = User.query.get_or_404(id)
    
    # لا يمكن إعادة تعيين صلاحيات المدير
    if user.role == UserRole.ADMIN:
        return jsonify({'success': False, 'message': 'لا يمكن إعادة تعيين صلاحيات مدير النظام'})
    
    try:
        # حذف الصلاحيات الحالية
        UserPermission.query.filter_by(user_id=id).delete()
        db.session.commit()
        
        # إنشاء الصلاحيات الافتراضية
        create_default_permissions(user)
        
        return jsonify({
            'success': True,
            'message': 'تم إعادة تعيين الصلاحيات بنجاح'
        })
        
    except Exception as e:
        logger.error(f"Error resetting permissions: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'حدث خطأ: {str(e)}'
        })