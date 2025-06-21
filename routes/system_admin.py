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
        
        return render_template('system_admin/futuristic_dashboard.html',
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
        
        return render_template('system_admin/futuristic_companies.html',
                             companies=companies.items,
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
            # جمع البيانات من النموذج
            name = request.form.get('name', '').strip()
            contact_email = request.form.get('contact_email', '').strip()
            contact_phone = request.form.get('contact_phone', '').strip()
            address = request.form.get('address', '').strip()
            
            # التحقق من البيانات المطلوبة
            if not name:
                flash('اسم الشركة مطلوب', 'error')
                return render_template('system_admin/futuristic_create_company.html')
            
            if not contact_email:
                flash('البريد الإلكتروني مطلوب', 'error')
                return render_template('system_admin/futuristic_create_company.html')
            
            # التحقق من عدم تكرار الإيميل
            existing_company = Company.query.filter_by(contact_email=contact_email).first()
            if existing_company:
                flash('يوجد شركة مسجلة بنفس البريد الإلكتروني', 'error')
                return render_template('system_admin/futuristic_create_company.html')
            
            # إنشاء الشركة الجديدة
            new_company = Company()
            new_company.name = name
            new_company.contact_email = contact_email
            new_company.contact_phone = contact_phone
            new_company.address = address
            new_company.status = 'active'
            
            db.session.add(new_company)
            db.session.flush()  # للحصول على معرف الشركة
            
            # إنشاء اشتراك تجريبي افتراضي
            from datetime import date, timedelta
            subscription = CompanySubscription()
            subscription.company_id = new_company.id
            subscription.plan_type = 'trial'
            subscription.is_trial = True
            subscription.start_date = date.today()
            subscription.end_date = date.today() + timedelta(days=30)
            subscription.is_active = True
            
            db.session.add(subscription)
            db.session.commit()
            
            logger.info(f"تم إنشاء شركة جديدة: {new_company.name} بواسطة {current_user.id}")
            flash('تم إنشاء الشركة بنجاح', 'success')
            return redirect(url_for('system_admin.companies_list'))
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"خطأ في إنشاء الشركة: {str(e)}")
            flash('حدث خطأ في إنشاء الشركة', 'error')
    
    return render_template('system_admin/futuristic_create_company.html')

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
        
        return render_template('system_admin/futuristic_company_details.html',
                             company=company,
                             employees_count=total_employees,
                             vehicles_count=total_vehicles,
                             users_count=total_users,
                             subscription_status=subscription_status,
                             recent_activities=recent_users)
                             
    except Exception as e:
        logger.error(f"خطأ في تفاصيل الشركة {company_id}: {str(e)}")
        flash('حدث خطأ في تحميل تفاصيل الشركة', 'error')
        return redirect(url_for('system_admin.companies_list'))

@system_admin_bp.route('/companies/<int:company_id>/subscription', methods=['GET', 'POST'])
@system_admin_alt_bp.route('/companies/<int:company_id>/subscription', methods=['GET', 'POST'])
@login_required
@system_owner_required
def manage_subscription(company_id):
    """إدارة اشتراك الشركة"""
    try:
        company = Company.query.get_or_404(company_id)
        
        if request.method == 'POST':
            # معالجة تحديث الاشتراك
            plan_type = request.form.get('plan_type')
            action = request.form.get('action')
            
            if action == 'upgrade':
                # ترقية الاشتراك
                result = SubscriptionService.upgrade_subscription(company_id, plan_type)
                if result:
                    flash('تم ترقية الاشتراك بنجاح', 'success')
                else:
                    flash('حدث خطأ في ترقية الاشتراك', 'error')
            
            elif action == 'extend':
                # تمديد الاشتراك
                extend_days = int(request.form.get('extend_days', 30))
                result = SubscriptionService.extend_subscription(company_id, extend_days)
                if result:
                    flash(f'تم تمديد الاشتراك لـ {extend_days} يوم', 'success')
                else:
                    flash('حدث خطأ في تمديد الاشتراك', 'error')
            
            elif action == 'suspend':
                # إيقاف الاشتراك
                subscription = CompanySubscription.query.filter_by(company_id=company_id).first()
                if subscription:
                    subscription.is_active = False
                    db.session.commit()
                    flash('تم إيقاف الاشتراك', 'success')
            
            elif action == 'activate':
                # تفعيل الاشتراك
                subscription = CompanySubscription.query.filter_by(company_id=company_id).first()
                if subscription:
                    subscription.is_active = True
                    db.session.commit()
                    flash('تم تفعيل الاشتراك', 'success')
            
            return redirect(url_for('system_admin.manage_subscription', company_id=company_id))
        
        # عرض الصفحة
        subscription_status = SubscriptionService.get_subscription_status(company_id)
        
        # جلب جميع خطط الاشتراك المتاحة
        available_plans = {}
        for plan_type in ['basic', 'premium', 'enterprise']:
            available_plans[plan_type] = SubscriptionService.get_plan_features(plan_type)
        
        return render_template('system_admin/futuristic_manage_subscription.html',
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
def subscriptions_list():
    """إدارة الاشتراكات"""
    try:
        page = request.args.get('page', 1, type=int)
        search = request.args.get('search', '')
        status_filter = request.args.get('status', 'all')
        
        query = CompanySubscription.query.join(Company)
        
        # البحث
        if search:
            query = query.filter(Company.name.contains(search))
        
        # تصفية حسب الحالة
        if status_filter == 'active':
            query = query.filter(CompanySubscription.is_active == True)
        elif status_filter == 'trial':
            query = query.filter(CompanySubscription.is_trial == True)
        elif status_filter == 'expired':
            query = query.filter(CompanySubscription.is_active == False)
        
        subscriptions = query.order_by(CompanySubscription.created_at.desc()).paginate(
            page=page, per_page=20, error_out=False
        )
        
        # إحصائيات
        total_subscriptions = CompanySubscription.query.count()
        active_subscriptions = CompanySubscription.query.filter_by(is_active=True).count()
        trial_subscriptions = CompanySubscription.query.filter_by(is_trial=True, is_active=True).count()
        expired_subscriptions = CompanySubscription.query.filter_by(is_active=False).count()
        
        return render_template('system_admin/futuristic_subscriptions.html',
                             subscriptions=subscriptions.items,
                             search=search,
                             status_filter=status_filter,
                             total_subscriptions=total_subscriptions,
                             active_subscriptions=active_subscriptions,
                             trial_subscriptions=trial_subscriptions,
                             expired_subscriptions=expired_subscriptions)
                             
    except Exception as e:
        logger.error(f"خطأ في قائمة الاشتراكات: {str(e)}")
        flash('حدث خطأ في تحميل قائمة الاشتراكات', 'error')
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
        
        # جلب إحصائيات إضافية للتصميم الجديد
        active_subscriptions = CompanySubscription.query.filter_by(is_active=True).count()
        todays_registrations = Company.query.filter(
            Company.created_at >= datetime.utcnow().date()
        ).count() if Company.query.first() and Company.query.first().created_at else 0
        
        # جلب الشركات المسجلة حديثاً
        recent_companies = Company.query.order_by(Company.created_at.desc()).limit(5).all()
        
        # بيانات النمو الشهري (مثال)
        companies_growth = [2, 5, 8, 12, 15, total_companies]
        subscription_distribution = [
            active_subscriptions * 0.4,  # أساسي
            active_subscriptions * 0.35, # مميز
            active_subscriptions * 0.25  # مؤسسات
        ]
        
        return render_template('system_admin/futuristic_reports.html',
                             total_companies=total_companies,
                             total_employees=total_employees,
                             total_vehicles=total_vehicles,
                             active_subscriptions=active_subscriptions,
                             todays_registrations=todays_registrations,
                             monthly_revenue=active_subscriptions * 150,  # تقدير إيرادات شهرية
                             recent_companies=recent_companies,
                             companies_growth=companies_growth,
                             subscription_distribution=subscription_distribution)
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
        # تغيير الحالة بين active و inactive
        company.status = 'inactive' if company.status == 'active' else 'active'
        company.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        status = 'تم تفعيل' if company.status == 'active' else 'تم إلغاء تفعيل'
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

@system_admin_bp.route('/companies/<int:company_id>/edit', methods=['GET', 'POST'])
@system_admin_alt_bp.route('/companies/<int:company_id>/edit', methods=['GET', 'POST'])
@login_required
@system_owner_required
def edit_company(company_id):
    """تعديل بيانات الشركة"""
    try:
        company = Company.query.get_or_404(company_id)
        
        if request.method == 'POST':
            # جمع البيانات من النموذج
            name = request.form.get('name', '').strip()
            contact_email = request.form.get('contact_email', '').strip()
            contact_phone = request.form.get('contact_phone', '').strip()
            address = request.form.get('address', '').strip()
            
            # التحقق من البيانات المطلوبة
            if not name:
                flash('اسم الشركة مطلوب', 'error')
                return render_template('system_admin/futuristic_edit_company.html', company=company)
            
            if not contact_email:
                flash('البريد الإلكتروني مطلوب', 'error')
                return render_template('system_admin/futuristic_edit_company.html', company=company)
            
            # التحقق من عدم تكرار الإيميل (إلا للشركة الحالية)
            existing_company = Company.query.filter(
                Company.contact_email == contact_email,
                Company.id != company_id
            ).first()
            
            if existing_company:
                flash('يوجد شركة أخرى مسجلة بنفس البريد الإلكتروني', 'error')
                return render_template('system_admin/futuristic_edit_company.html', company=company)
            
            # تحديث بيانات الشركة
            company.name = name
            company.contact_email = contact_email
            company.contact_phone = contact_phone
            company.address = address
            
            db.session.commit()
            
            logger.info(f"تم تعديل بيانات الشركة {company_id} بواسطة {current_user.id}")
            flash('تم تحديث بيانات الشركة بنجاح', 'success')
            return redirect(url_for('system_admin.companies_list'))
        
        return render_template('system_admin/futuristic_edit_company.html', company=company)
        
    except Exception as e:
        logger.error(f"خطأ في تعديل الشركة {company_id}: {str(e)}")
        flash('حدث خطأ في تعديل بيانات الشركة', 'error')
        return redirect(url_for('system_admin.companies_list'))

@system_admin_bp.route('/companies/<int:company_id>/delete', methods=['POST'])
@system_admin_alt_bp.route('/companies/<int:company_id>/delete', methods=['POST'])
@login_required
@system_owner_required
def delete_company(company_id):
    """حذف الشركة"""
    try:
        company = Company.query.get_or_404(company_id)
        company_name = company.name
        
        # التحقق من وجود بيانات مرتبطة
        employees_count = Employee.query.filter_by(company_id=company_id).count()
        vehicles_count = Vehicle.query.filter_by(company_id=company_id).count()
        users_count = User.query.filter_by(company_id=company_id).count()
        
        if employees_count > 0 or vehicles_count > 0 or users_count > 0:
            flash(f'لا يمكن حذف الشركة لوجود بيانات مرتبطة ({employees_count} موظف، {vehicles_count} مركبة، {users_count} مستخدم)', 'error')
            return redirect(url_for('system_admin.companies_list'))
        
        # حذف الاشتراك المرتبط
        subscription = CompanySubscription.query.filter_by(company_id=company_id).first()
        if subscription:
            db.session.delete(subscription)
        
        # حذف الشركة
        db.session.delete(company)
        db.session.commit()
        
        logger.info(f"تم حذف الشركة {company_name} (ID: {company_id}) بواسطة {current_user.id}")
        flash(f'تم حذف شركة "{company_name}" بنجاح', 'success')
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"خطأ في حذف الشركة {company_id}: {str(e)}")
        flash('حدث خطأ في حذف الشركة', 'error')
    
    return redirect(url_for('system_admin.companies_list'))