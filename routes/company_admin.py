"""
نظام إدارة مديري الشركات - إدارة المستخدمين والصلاحيات داخل الشركة
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from utils.multi_tenant_decorators import (
    company_admin_required, set_company_context, trial_access_required,
    subscription_limit_required, require_company_context
)
from services.subscription_service import SubscriptionService
from models import User, Employee, Vehicle, Department, UserType, CompanyPermission, Module
from app import db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

company_admin_bp = Blueprint('company_admin', __name__, url_prefix='/company')

@company_admin_bp.route('/dashboard')
@login_required
@company_admin_required
@trial_access_required
@set_company_context
def dashboard():
    """لوحة تحكم مدير الشركة"""
    try:
        company_id = current_user.company_id
        
        # إحصائيات الشركة
        total_employees = Employee.query.filter_by(company_id=company_id).count()
        total_vehicles = Vehicle.query.filter_by(company_id=company_id).count()
        total_users = User.query.filter_by(company_id=company_id).count()
        total_departments = Department.query.filter_by(company_id=company_id).count()
        
        # حالة الاشتراك
        subscription_status = SubscriptionService.get_subscription_status(company_id)
        
        # الموظفون الجدد هذا الشهر
        current_month = datetime.utcnow().replace(day=1)
        new_employees_this_month = Employee.query.filter(
            Employee.company_id == company_id,
            Employee.created_at >= current_month
        ).count()
        
        # المركبات المتاحة
        available_vehicles = Vehicle.query.filter_by(
            company_id=company_id,
            status='available'
        ).count()
        
        return render_template('company_admin/dashboard.html',
                             total_employees=total_employees,
                             total_vehicles=total_vehicles,
                             total_users=total_users,
                             total_departments=total_departments,
                             new_employees_this_month=new_employees_this_month,
                             available_vehicles=available_vehicles,
                             subscription_status=subscription_status)
                             
    except Exception as e:
        logger.error(f"خطأ في لوحة تحكم مدير الشركة: {str(e)}")
        flash('حدث خطأ في تحميل لوحة التحكم', 'error')
        return redirect(url_for('multi_tenant_home'))

@company_admin_bp.route('/users')
@login_required
@company_admin_required
@trial_access_required
@set_company_context
def users_list():
    """قائمة مستخدمي الشركة"""
    try:
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '')
        
        query = User.query.filter_by(company_id=current_user.company_id)
        
        # البحث
        if search:
            query = query.filter(
                User.name.contains(search) | 
                User.email.contains(search)
            )
        
        users = query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=20, error_out=False
        )
        
        return render_template('company_admin/users_list.html',
                             users=users,
                             search=search)
                             
    except Exception as e:
        logger.error(f"خطأ في قائمة المستخدمين: {str(e)}")
        flash('حدث خطأ في تحميل قائمة المستخدمين', 'error')
        return redirect(url_for('company_admin.dashboard'))

@company_admin_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@company_admin_required
@trial_access_required
@subscription_limit_required('users')
@set_company_context
def create_user():
    """إنشاء مستخدم جديد"""
    if request.method == 'POST':
        try:
            user_data = {
                'email': request.form.get('email'),
                'name': request.form.get('name'),
                'user_type': UserType.EMPLOYEE,
                'company_id': current_user.company_id,
                'created_by': current_user.id,
                'is_active': True
            }
            
            # التحقق من البيانات المطلوبة
            required_fields = ['email', 'name']
            for field in required_fields:
                if not user_data.get(field):
                    flash(f'حقل {field} مطلوب', 'error')
                    return render_template('company_admin/create_user.html')
            
            # التحقق من عدم تكرار الإيميل داخل الشركة
            existing_user = User.query.filter_by(
                company_id=current_user.company_id,
                email=user_data['email']
            ).first()
            if existing_user:
                flash('هذا البريد الإلكتروني مستخدم بالفعل في الشركة', 'error')
                return render_template('company_admin/create_user.html')
            
            # تعيين كلمة المرور
            password = request.form.get('password')
            if password:
                from werkzeug.security import generate_password_hash
                user_data['password_hash'] = generate_password_hash(password)
            
            # ربط بموظف إذا تم تحديده
            employee_id = request.form.get('employee_id')
            if employee_id:
                employee = Employee.query.filter_by(
                    id=employee_id,
                    company_id=current_user.company_id
                ).first()
                if employee:
                    user_data['employee_id'] = employee_id
            
            # إنشاء المستخدم
            new_user = User(**user_data)
            db.session.add(new_user)
            db.session.flush()
            
            # إضافة الصلاحيات الأساسية
            basic_permissions = request.form.getlist('permissions')
            for module_name in basic_permissions:
                try:
                    module = Module[module_name.upper()]
                    permission = CompanyPermission(
                        user_id=new_user.id,
                        module=module,
                        can_view=True,
                        can_create=request.form.get(f'{module_name}_create') == 'on',
                        can_edit=request.form.get(f'{module_name}_edit') == 'on',
                        can_delete=request.form.get(f'{module_name}_delete') == 'on'
                    )
                    db.session.add(permission)
                except (KeyError, ValueError):
                    continue
            
            db.session.commit()
            
            logger.info(f"تم إنشاء مستخدم جديد: {new_user.email} في الشركة {current_user.company_id}")
            flash('تم إنشاء المستخدم بنجاح', 'success')
            return redirect(url_for('company_admin.users_list'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"خطأ في إنشاء المستخدم: {str(e)}")
            flash('حدث خطأ في إنشاء المستخدم', 'error')
    
    # جلب الموظفين غير المرتبطين بمستخدمين
    available_employees = Employee.query.filter_by(
        company_id=current_user.company_id
    ).filter(
        ~Employee.id.in_(
            db.session.query(User.employee_id).filter(
                User.employee_id.isnot(None),
                User.company_id == current_user.company_id
            )
        )
    ).all()
    
    return render_template('company_admin/create_user.html',
                         available_employees=available_employees)

@company_admin_bp.route('/users/<int:user_id>/permissions')
@login_required
@company_admin_required
@trial_access_required
@set_company_context
def manage_user_permissions(user_id):
    """إدارة صلاحيات المستخدم"""
    try:
        user = User.query.filter_by(
            id=user_id,
            company_id=current_user.company_id
        ).first_or_404()
        
        # جلب الصلاحيات الحالية
        current_permissions = {}
        for permission in user.company_permissions:
            current_permissions[permission.module] = permission
        
        # جلب جميع الوحدات المتاحة
        available_modules = list(Module)
        
        return render_template('company_admin/manage_permissions.html',
                             user=user,
                             current_permissions=current_permissions,
                             available_modules=available_modules)
                             
    except Exception as e:
        logger.error(f"خطأ في إدارة صلاحيات المستخدم {user_id}: {str(e)}")
        flash('حدث خطأ في تحميل صلاحيات المستخدم', 'error')
        return redirect(url_for('company_admin.users_list'))

@company_admin_bp.route('/users/<int:user_id>/permissions', methods=['POST'])
@login_required
@company_admin_required
@trial_access_required
@set_company_context
def update_user_permissions(user_id):
    """تحديث صلاحيات المستخدم"""
    try:
        user = User.query.filter_by(
            id=user_id,
            company_id=current_user.company_id
        ).first_or_404()
        
        # حذف الصلاحيات الحالية
        CompanyPermission.query.filter_by(user_id=user_id).delete()
        
        # إضافة الصلاحيات الجديدة
        for module in Module:
            module_name = module.value.lower()
            
            if request.form.get(f'{module_name}_view'):
                permission = CompanyPermission(
                    user_id=user_id,
                    module=module,
                    can_view=True,
                    can_create=request.form.get(f'{module_name}_create') == 'on',
                    can_edit=request.form.get(f'{module_name}_edit') == 'on',
                    can_delete=request.form.get(f'{module_name}_delete') == 'on'
                )
                db.session.add(permission)
        
        db.session.commit()
        
        logger.info(f"تم تحديث صلاحيات المستخدم {user_id} في الشركة {current_user.company_id}")
        flash('تم تحديث صلاحيات المستخدم بنجاح', 'success')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"خطأ في تحديث صلاحيات المستخدم {user_id}: {str(e)}")
        flash('حدث خطأ في تحديث الصلاحيات', 'error')
    
    return redirect(url_for('company_admin.users_list'))

@company_admin_bp.route('/subscription')
@login_required
@company_admin_required
@set_company_context
def subscription_status():
    """عرض حالة الاشتراك وخيارات الترقية"""
    try:
        subscription_status = SubscriptionService.get_subscription_status(current_user.company_id)
        
        # جلب خطط الاشتراك المتاحة
        available_plans = {}
        for plan_type in ['basic', 'premium', 'enterprise']:
            available_plans[plan_type] = SubscriptionService.get_plan_features(plan_type)
        
        # إحصائيات الاستخدام الحالي
        usage_stats = {
            'employees': Employee.query.filter_by(company_id=current_user.company_id).count(),
            'vehicles': Vehicle.query.filter_by(company_id=current_user.company_id).count(),
            'users': User.query.filter_by(company_id=current_user.company_id).count()
        }
        
        return render_template('company_admin/subscription.html',
                             subscription_status=subscription_status,
                             available_plans=available_plans,
                             usage_stats=usage_stats)
                             
    except Exception as e:
        logger.error(f"خطأ في عرض حالة الاشتراك: {str(e)}")
        flash('حدث خطأ في تحميل معلومات الاشتراك', 'error')
        return redirect(url_for('company_admin.dashboard'))

@company_admin_bp.route('/settings')
@login_required
@company_admin_required
@trial_access_required
@set_company_context
def company_settings():
    """إعدادات الشركة"""
    try:
        company = current_user.company
        return render_template('company_admin/settings.html', company=company)
        
    except Exception as e:
        logger.error(f"خطأ في إعدادات الشركة: {str(e)}")
        flash('حدث خطأ في تحميل إعدادات الشركة', 'error')
        return redirect(url_for('company_admin.dashboard'))

@company_admin_bp.route('/settings', methods=['POST'])
@login_required
@company_admin_required
@trial_access_required
@set_company_context
def update_company_settings():
    """تحديث إعدادات الشركة"""
    try:
        company = current_user.company
        
        # تحديث البيانات الأساسية
        company.name = request.form.get('name', company.name)
        company.name_en = request.form.get('name_en', company.name_en)
        company.contact_phone = request.form.get('contact_phone', company.contact_phone)
        company.address = request.form.get('address', company.address)
        company.city = request.form.get('city', company.city)
        company.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        logger.info(f"تم تحديث إعدادات الشركة {company.id}")
        flash('تم تحديث إعدادات الشركة بنجاح', 'success')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"خطأ في تحديث إعدادات الشركة: {str(e)}")
        flash('حدث خطأ في تحديث الإعدادات', 'error')
    
    return redirect(url_for('company_admin.company_settings'))

@company_admin_bp.route('/api/usage-stats')
@login_required
@company_admin_required
@trial_access_required
@set_company_context
def api_usage_stats():
    """API للحصول على إحصائيات الاستخدام"""
    try:
        company_id = current_user.company_id
        subscription_status = SubscriptionService.get_subscription_status(company_id)
        
        stats = {
            'employees': {
                'current': Employee.query.filter_by(company_id=company_id).count(),
                'limit': subscription_status['max_employees'] if subscription_status else 0
            },
            'vehicles': {
                'current': Vehicle.query.filter_by(company_id=company_id).count(),
                'limit': subscription_status['max_vehicles'] if subscription_status else 0
            },
            'users': {
                'current': User.query.filter_by(company_id=company_id).count(),
                'limit': subscription_status['max_users'] if subscription_status else 0
            }
        }
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"خطأ في API إحصائيات الاستخدام: {str(e)}")
        return jsonify({'error': 'حدث خطأ في جلب الإحصائيات'}), 500