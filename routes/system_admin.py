"""
نظام إدارة مالك النظام - إدارة الشركات والاشتراكات
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from utils.multi_tenant_decorators import system_owner_required, set_company_context
from services.subscription_service import SubscriptionService
from models import Company, User, CompanySubscription, Employee, Vehicle, UserType, SubscriptionNotification
from app import db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

system_admin_bp = Blueprint('system_admin', __name__, url_prefix='/system')
# إضافة blueprint آخر لدعم مسار system-admin
system_admin_alt_bp = Blueprint('system_admin_alt', __name__, url_prefix='/system-admin')

# إضافة نفس المسارات للبلوبرينت البديل
@system_admin_bp.route('/dashboard')
@system_admin_alt_bp.route('/dashboard')
@login_required
@system_owner_required
def dashboard():
    """لوحة تحكم مالك النظام"""
    try:
        # إحصائيات عامة
        total_companies = Company.query.count()
        active_companies = Company.query.filter_by(status='active').count()
        total_subscriptions = CompanySubscription.query.count()
        active_subscriptions = CompanySubscription.query.filter_by(is_active=True).count()
        
        # إحصائيات النظام
        total_employees = Employee.query.count()
        total_vehicles = Vehicle.query.count()
        total_revenue = 0  # يمكن حسابه من الاشتراكات لاحقاً
        
        # النشاط الأخير - محاكاة بسيطة للعرض
        recent_activities = [
            {
                'description': f'النظام يحتوي على {total_companies} شركة مسجلة',
                'icon': 'fa-building',
                'created_at': datetime.utcnow()
            },
            {
                'description': f'إجمالي {total_employees} موظف في النظام',
                'icon': 'fa-users',
                'created_at': datetime.utcnow()
            },
            {
                'description': f'إجمالي {total_vehicles} مركبة مسجلة',
                'icon': 'fa-car',
                'created_at': datetime.utcnow()
            }
        ]
        
        return render_template('system_admin/dashboard.html',
                             total_companies=total_companies,
                             active_companies=active_companies,
                             total_subscriptions=total_subscriptions,
                             active_subscriptions=active_subscriptions,
                             total_employees=total_employees,
                             total_vehicles=total_vehicles,
                             total_revenue=total_revenue,
                             recent_activities=recent_activities,
                             now=datetime.utcnow())
                             
    except Exception as e:
        logger.error(f"خطأ في لوحة تحكم مالك النظام: {str(e)}")
        flash('حدث خطأ في تحميل لوحة التحكم', 'error')
        return redirect(url_for('multi_tenant_home'))

@system_admin_bp.route('/companies')
@system_admin_alt_bp.route('/companies')
@login_required
@system_owner_required
def companies_list():
    """قائمة جميع الشركات"""
    try:
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '')
        status_filter = request.args.get('status', 'all')
        
        query = Company.query
        
        # البحث
        if search:
            query = query.filter(
                Company.name.contains(search) | 
                Company.contact_email.contains(search)
            )
        
        # تصفية حسب الحالة
        if status_filter == 'active':
            query = query.filter(Company.status == 'active')
        elif status_filter == 'inactive':
            query = query.filter(Company.status == 'inactive')
        elif status_filter == 'trial':
            query = query.join(CompanySubscription).filter(
                CompanySubscription.is_trial == True,
                CompanySubscription.is_active == True
            )
        
        companies = query.order_by(Company.created_at.desc()).paginate(
            page=page, per_page=20, error_out=False
        )
        
        return render_template('system_admin/companies_list.html',
                             companies=companies,
                             search=search,
                             status_filter=status_filter)
                             
    except Exception as e:
        logger.error(f"خطأ في قائمة الشركات: {str(e)}")
        flash('حدث خطأ في تحميل قائمة الشركات', 'error')
        return redirect(url_for('system_admin.dashboard'))

@system_admin_bp.route('/companies/new', methods=['GET', 'POST'])
@system_admin_alt_bp.route('/companies/new', methods=['GET', 'POST'])
@login_required
@system_owner_required
def create_new_company():
    """إنشاء شركة جديدة"""
    if request.method == 'POST':
        try:
            company_data = {
                'name': request.form.get('name'),
                'name_en': request.form.get('name_en'),
                'commercial_register': request.form.get('commercial_register'),
                'tax_number': request.form.get('tax_number'),
                'contact_email': request.form.get('contact_email'),
                'contact_phone': request.form.get('contact_phone'),
                'address': request.form.get('address'),
                'city': request.form.get('city'),
                'country': request.form.get('country', 'السعودية'),
                'is_active': True,
                'created_by_user_id': current_user.id
            }
            
            # التحقق من البيانات المطلوبة
            required_fields = ['name', 'contact_email']
            for field in required_fields:
                if not company_data.get(field):
                    flash(f'حقل {field} مطلوب', 'error')
                    return render_template('system_admin/create_company.html')
            
            # التحقق من عدم تكرار الإيميل
            existing_company = Company.query.filter_by(
                contact_email=company_data['contact_email']
            ).first()
            if existing_company:
                flash('هذا البريد الإلكتروني مستخدم بالفعل', 'error')
                return render_template('system_admin/create_company.html')
            
            # إنشاء الشركة
            new_company = Company(**company_data)
            db.session.add(new_company)
            db.session.flush()  # للحصول على ID الشركة
            
            # إنشاء اشتراك تجريبي
            plan_type = request.form.get('plan_type', 'basic')
            success, message = SubscriptionService.create_trial_subscription(
                new_company.id, plan_type
            )
            
            if not success:
                db.session.rollback()
                flash(f'فشل في إنشاء الاشتراك: {message}', 'error')
                return render_template('system_admin/create_company.html')
            
            # إنشاء مدير الشركة
            admin_email = request.form.get('admin_email')
            admin_name = request.form.get('admin_name')
            admin_password = request.form.get('admin_password')
            
            if admin_email and admin_name and admin_password:
                from werkzeug.security import generate_password_hash
                
                company_admin = User(
                    email=admin_email,
                    name=admin_name,
                    password_hash=generate_password_hash(admin_password),
                    company_id=new_company.id,
                    user_type=UserType.COMPANY_ADMIN,
                    created_by=current_user.id,
                    is_active=True
                )
                db.session.add(company_admin)
            
            db.session.commit()
            
            logger.info(f"تم إنشاء شركة جديدة: {new_company.name} بواسطة {current_user.id}")
            flash('تم إنشاء الشركة بنجاح', 'success')
            return redirect(url_for('system_admin.company_details', company_id=new_company.id))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"خطأ في إنشاء الشركة: {str(e)}")
            flash('حدث خطأ في إنشاء الشركة', 'error')
    
    return render_template('system_admin/create_company.html')

@system_admin_bp.route('/companies/<int:company_id>')
@login_required
@system_owner_required
def company_details(company_id):
    """تفاصيل شركة محددة"""
    try:
        company = Company.query.get_or_404(company_id)
        
        # إحصائيات الشركة
        total_employees = Employee.query.filter_by(company_id=company_id).count()
        total_vehicles = Vehicle.query.filter_by(company_id=company_id).count()
        total_users = User.query.filter_by(company_id=company_id).count()
        
        # حالة الاشتراك
        subscription_status = SubscriptionService.get_subscription_status(company_id)
        
        # آخر المستخدمين
        recent_users = User.query.filter_by(company_id=company_id)\
                                .order_by(User.created_at.desc())\
                                .limit(5).all()
        
        return render_template('system_admin/company_details.html',
                             company=company,
                             total_employees=total_employees,
                             total_vehicles=total_vehicles,
                             total_users=total_users,
                             subscription_status=subscription_status,
                             recent_users=recent_users)
                             
    except Exception as e:
        logger.error(f"خطأ في تفاصيل الشركة {company_id}: {str(e)}")
        flash('حدث خطأ في تحميل تفاصيل الشركة', 'error')
        return redirect(url_for('system_admin.companies_list'))

@system_admin_bp.route('/companies/<int:company_id>/subscription')
@login_required
@system_owner_required
def manage_subscription(company_id):
    """إدارة اشتراك الشركة"""
    try:
        company = Company.query.get_or_404(company_id)
        subscription_status = SubscriptionService.get_subscription_status(company_id)
        
        # جلب جميع خطط الاشتراك المتاحة
        available_plans = {}
        for plan_type in ['basic', 'premium', 'enterprise']:
            available_plans[plan_type] = SubscriptionService.get_plan_features(plan_type)
        
        return render_template('system_admin/manage_subscription.html',
                             company=company,
                             subscription_status=subscription_status,
                             available_plans=available_plans)
                             
    except Exception as e:
        logger.error(f"خطأ في إدارة اشتراك الشركة {company_id}: {str(e)}")
        flash('حدث خطأ في تحميل إدارة الاشتراك', 'error')
        return redirect(url_for('system_admin.company_details', company_id=company_id))

@system_admin_bp.route('/subscriptions')
@system_admin_alt_bp.route('/subscriptions')
@login_required
@system_owner_required
def subscriptions():
    """إدارة الاشتراكات"""
    try:
        subscriptions = CompanySubscription.query.all()
        return render_template('system_admin/subscriptions.html',
                             subscriptions=subscriptions)
    except Exception as e:
        logger.error(f"خطأ في عرض الاشتراكات: {str(e)}")
        flash('حدث خطأ في تحميل الاشتراكات', 'error')
        return redirect(url_for('system_admin.dashboard'))

@system_admin_bp.route('/reports')
@login_required
@system_owner_required
def reports():
    """التقارير والإحصائيات"""
    try:
        # إحصائيات شاملة للنظام
        total_companies = Company.query.count()
        total_employees = Employee.query.count()
        total_vehicles = Vehicle.query.count()
        
        return render_template('system_admin/reports.html',
                             total_companies=total_companies,
                             total_employees=total_employees,
                             total_vehicles=total_vehicles)
    except Exception as e:
        logger.error(f"خطأ في عرض التقارير: {str(e)}")
        flash('حدث خطأ في تحميل التقارير', 'error')
        return redirect(url_for('system_admin.dashboard'))



@system_admin_bp.route('/companies/<int:company_id>/upgrade', methods=['POST'])
@login_required
@system_owner_required
def upgrade_subscription(company_id):
    """ترقية اشتراك الشركة"""
    try:
        plan_type = request.form.get('plan_type')
        duration_months = int(request.form.get('duration_months', 12))
        
        if not plan_type or plan_type not in ['basic', 'premium', 'enterprise']:
            flash('نوع الخطة غير صحيح', 'error')
            return redirect(url_for('system_admin.manage_subscription', company_id=company_id))
        
        success, message = SubscriptionService.upgrade_to_paid_subscription(
            company_id, plan_type, duration_months
        )
        
        if success:
            flash('تم ترقية الاشتراك بنجاح', 'success')
            logger.info(f"تم ترقية اشتراك الشركة {company_id} إلى {plan_type}")
        else:
            flash(f'فشل في ترقية الاشتراك: {message}', 'error')
        
        return redirect(url_for('system_admin.manage_subscription', company_id=company_id))
        
    except Exception as e:
        logger.error(f"خطأ في ترقية اشتراك الشركة {company_id}: {str(e)}")
        flash('حدث خطأ في ترقية الاشتراك', 'error')
        return redirect(url_for('system_admin.manage_subscription', company_id=company_id))

@system_admin_bp.route('/companies/<int:company_id>/toggle-status', methods=['POST'])
@login_required
@system_owner_required
def toggle_company_status(company_id):
    """تفعيل/إلغاء تفعيل الشركة"""
    try:
        company = Company.query.get_or_404(company_id)
        company.is_active = not company.is_active
        company.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        status = 'تم تفعيل' if company.is_active else 'تم إلغاء تفعيل'
        flash(f'{status} الشركة بنجاح', 'success')
        logger.info(f"{status} الشركة {company_id} بواسطة {current_user.id}")
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"خطأ في تغيير حالة الشركة {company_id}: {str(e)}")
        flash('حدث خطأ في تغيير حالة الشركة', 'error')
    
    return redirect(url_for('system_admin.company_details', company_id=company_id))

@system_admin_bp.route('/notifications')
@login_required
@system_owner_required
def notifications():
    """إدارة إشعارات النظام"""
    try:
        # إرسال تنبيهات انتهاء الاشتراكات
        notifications_sent = SubscriptionService.send_expiry_notifications()
        
        # جلب الاشتراكات المنتهية قريباً
        from models import SubscriptionNotification
        recent_notifications = SubscriptionNotification.query\
                                .order_by(SubscriptionNotification.created_at.desc())\
                                .limit(50).all()
        
        return render_template('system_admin/notifications.html',
                             notifications_sent=notifications_sent,
                             recent_notifications=recent_notifications)
                             
    except Exception as e:
        logger.error(f"خطأ في إدارة الإشعارات: {str(e)}")
        flash('حدث خطأ في تحميل الإشعارات', 'error')
        return redirect(url_for('system_admin.dashboard'))

@system_admin_bp.route('/api/stats')
@login_required
@system_owner_required
def api_stats():
    """API للإحصائيات المباشرة"""
    try:
        # إحصائيات مباشرة للوحة التحكم
        stats = {
            'total_companies': Company.query.count(),
            'active_companies': Company.query.filter_by(is_active=True).count(),
            'trial_companies': CompanySubscription.query.filter_by(
                is_trial=True, is_active=True
            ).count(),
            'paid_companies': CompanySubscription.query.filter_by(
                is_trial=False, is_active=True
            ).count(),
            'total_users': User.query.count(),
            'total_employees': Employee.query.count(),
            'total_vehicles': Vehicle.query.count()
        }
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"خطأ في API الإحصائيات: {str(e)}")
        return jsonify({'error': 'حدث خطأ في جلب الإحصائيات'}), 500