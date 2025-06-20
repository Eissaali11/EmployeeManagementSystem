"""
خدمة إدارة الاشتراكات والحدود للنظام Multi-Tenant
"""
from datetime import datetime, timedelta
from models import Company, CompanySubscription, SubscriptionNotification
from app import db
import logging

logger = logging.getLogger(__name__)

class SubscriptionService:
    """خدمة إدارة الاشتراكات"""
    
    @staticmethod
    def create_trial_subscription(company_id, plan_type='basic'):
        """
        إنشاء اشتراك تجريبي جديد لمدة 30 يوم
        """
        try:
            # التحقق من عدم وجود اشتراك فعال
            existing_subscription = CompanySubscription.query.filter_by(
                company_id=company_id,
                is_active=True
            ).first()
            
            if existing_subscription:
                return False, "يوجد اشتراك فعال بالفعل"
            
            # إنشاء الاشتراك التجريبي
            trial_start = datetime.utcnow()
            trial_end = trial_start + timedelta(days=30)
            
            subscription = CompanySubscription(
                company_id=company_id,
                plan_type=plan_type,
                is_trial=True,
                trial_start_date=trial_start,
                trial_end_date=trial_end,
                start_date=trial_start,
                end_date=trial_end,
                is_active=True,
                auto_renew=False
            )
            
            db.session.add(subscription)
            db.session.commit()
            
            logger.info(f"تم إنشاء اشتراك تجريبي للشركة {company_id}")
            return True, "تم إنشاء الاشتراك التجريبي بنجاح"
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"خطأ في إنشاء الاشتراك التجريبي: {str(e)}")
            return False, "حدث خطأ في إنشاء الاشتراك"
    
    @staticmethod
    def upgrade_to_paid_subscription(company_id, plan_type, duration_months=12):
        """
        ترقية من التجريبي إلى الاشتراك المدفوع
        """
        try:
            company = Company.query.get(company_id)
            if not company:
                return False, "الشركة غير موجودة"
            
            # إلغاء الاشتراك الحالي
            current_subscription = company.subscription
            if current_subscription:
                current_subscription.is_active = False
                current_subscription.updated_at = datetime.utcnow()
            
            # إنشاء الاشتراك المدفوع
            start_date = datetime.utcnow()
            end_date = start_date + timedelta(days=duration_months * 30)
            
            new_subscription = CompanySubscription(
                company_id=company_id,
                plan_type=plan_type,
                is_trial=False,
                start_date=start_date,
                end_date=end_date,
                is_active=True,
                auto_renew=True
            )
            
            db.session.add(new_subscription)
            db.session.commit()
            
            logger.info(f"تم ترقية الاشتراك للشركة {company_id} إلى {plan_type}")
            return True, "تم ترقية الاشتراك بنجاح"
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"خطأ في ترقية الاشتراك: {str(e)}")
            return False, "حدث خطأ في ترقية الاشتراك"
    
    @staticmethod
    def check_subscription_limits(company_id, check_type):
        """
        التحقق من حدود الاشتراك
        check_type: 'employees', 'vehicles', 'users'
        """
        from models import Employee, Vehicle, User
        
        try:
            company = Company.query.get(company_id)
            if not company or not company.subscription:
                return False, "لا يوجد اشتراك فعال"
            
            subscription = company.subscription
            
            # التحقق من انتهاء الفترة التجريبية والاشتراك
            if subscription.is_trial_expired and subscription.is_expired:
                return False, "انتهت الفترة التجريبية والاشتراك"
            
            # جلب العدد الحالي والحد الأقصى
            current_count = 0
            limit = 0
            
            if check_type == 'employees':
                current_count = Employee.query.filter_by(company_id=company_id).count()
                limit = subscription.max_employees
            elif check_type == 'vehicles':
                current_count = Vehicle.query.filter_by(company_id=company_id).count()
                limit = subscription.max_vehicles
            elif check_type == 'users':
                current_count = User.query.filter_by(company_id=company_id).count()
                limit = subscription.max_users
            
            if current_count >= limit:
                return False, f"تم الوصول للحد الأقصى من {check_type} ({limit})"
            
            return True, f"متاح {limit - current_count} من {limit}"
            
        except Exception as e:
            logger.error(f"خطأ في التحقق من حدود الاشتراك: {str(e)}")
            return False, "حدث خطأ في التحقق من الحدود"
    
    @staticmethod
    def upgrade_subscription(company_id, new_plan_type):
        """
        ترقية اشتراك الشركة إلى خطة جديدة
        """
        try:
            subscription = CompanySubscription.query.filter_by(
                company_id=company_id,
                is_active=True
            ).first()
            
            if not subscription:
                # إنشاء اشتراك جديد
                start_date = datetime.utcnow()
                end_date = start_date + timedelta(days=365)  # سنة واحدة
                
                new_subscription = CompanySubscription(
                    company_id=company_id,
                    plan_type=new_plan_type,
                    is_trial=False,
                    start_date=start_date,
                    end_date=end_date,
                    is_active=True,
                    auto_renew=True
                )
                
                db.session.add(new_subscription)
            else:
                # ترقية الاشتراك الحالي
                subscription.plan_type = new_plan_type
                subscription.is_trial = False
                subscription.updated_at = datetime.utcnow()
            
            db.session.commit()
            logger.info(f"تم ترقية اشتراك الشركة {company_id} إلى {new_plan_type}")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"خطأ في ترقية الاشتراك: {str(e)}")
            return False
    
    @staticmethod
    def extend_subscription(company_id, extend_days):
        """
        تمديد اشتراك الشركة
        """
        try:
            subscription = CompanySubscription.query.filter_by(
                company_id=company_id,
                is_active=True
            ).first()
            
            if not subscription:
                return False
            
            # تمديد تاريخ الانتهاء
            if subscription.end_date:
                subscription.end_date = subscription.end_date + timedelta(days=extend_days)
            else:
                subscription.end_date = datetime.utcnow() + timedelta(days=extend_days)
            
            subscription.updated_at = datetime.utcnow()
            
            db.session.commit()
            logger.info(f"تم تمديد اشتراك الشركة {company_id} لـ {extend_days} يوم")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"خطأ في تمديد الاشتراك: {str(e)}")
            return False
    
    @staticmethod
    def get_subscription_status(company_id):
        """
        جلب حالة الاشتراك التفصيلية
        """
        try:
            company = Company.query.get(company_id)
            if not company:
                return None
            
            subscription = company.subscription
            if not subscription:
                return {
                    'status': 'no_subscription',
                    'message': 'لا يوجد اشتراك',
                    'can_create_trial': True
                }
            
            status = {
                'subscription_id': subscription.id,
                'plan_type': subscription.plan_type,
                'is_trial': subscription.is_trial,
                'is_active': subscription.is_active,
                'start_date': subscription.start_date,
                'end_date': subscription.end_date,
                'days_remaining': subscription.days_remaining,
                'is_expired': subscription.is_expired,
                'is_trial_expired': subscription.is_trial_expired,
                'max_employees': subscription.max_employees,
                'max_vehicles': subscription.max_vehicles,
                'max_users': subscription.max_users,
                'features': subscription.features
            }
            
            # تحديد الحالة
            if subscription.is_trial_expired and subscription.is_expired:
                status['status'] = 'expired'
                status['message'] = 'انتهت الفترة التجريبية والاشتراك'
                status['action_required'] = 'upgrade'
            elif subscription.is_trial and subscription.days_remaining <= 7:
                status['status'] = 'trial_expiring'
                status['message'] = f'تنتهي الفترة التجريبية خلال {subscription.days_remaining} أيام'
                status['action_required'] = 'upgrade'
            elif subscription.is_trial:
                status['status'] = 'trial_active'
                status['message'] = f'فترة تجريبية - {subscription.days_remaining} يوم متبقي'
            elif subscription.days_remaining <= 7:
                status['status'] = 'expiring'
                status['message'] = f'ينتهي الاشتراك خلال {subscription.days_remaining} أيام'
                status['action_required'] = 'renew'
            else:
                status['status'] = 'active'
                status['message'] = f'اشتراك فعال - {subscription.days_remaining} يوم متبقي'
            
            return status
            
        except Exception as e:
            logger.error(f"خطأ في جلب حالة الاشتراك: {str(e)}")
            return None
    
    @staticmethod
    def send_expiry_notifications():
        """
        إرسال تنبيهات انتهاء الاشتراكات
        """
        try:
            # جلب الاشتراكات المنتهية الصلاحية قريباً
            upcoming_expiry = datetime.utcnow() + timedelta(days=7)
            
            expiring_subscriptions = CompanySubscription.query.filter(
                CompanySubscription.is_active == True,
                CompanySubscription.end_date <= upcoming_expiry,
                CompanySubscription.end_date > datetime.utcnow()
            ).all()
            
            notifications_sent = 0
            
            for subscription in expiring_subscriptions:
                # التحقق من عدم إرسال تنبيه مؤخراً
                last_notification = SubscriptionNotification.query.filter_by(
                    company_id=subscription.company_id,
                    notification_type='expiry_warning'
                ).order_by(SubscriptionNotification.created_at.desc()).first()
                
                # إرسال تنبيه إذا لم يتم إرساله خلال آخر 24 ساعة
                if not last_notification or \
                   (datetime.utcnow() - last_notification.created_at).days >= 1:
                    
                    notification = SubscriptionNotification(
                        company_id=subscription.company_id,
                        notification_type='expiry_warning',
                        title='تنبيه انتهاء الاشتراك',
                        message=f'ينتهي اشتراكك خلال {subscription.days_remaining} أيام. يرجى التجديد لتجنب انقطاع الخدمة.',
                        is_read=False
                    )
                    
                    db.session.add(notification)
                    notifications_sent += 1
            
            db.session.commit()
            logger.info(f"تم إرسال {notifications_sent} تنبيه انتهاء اشتراك")
            return notifications_sent
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"خطأ في إرسال تنبيهات الانتهاء: {str(e)}")
            return 0
    
    @staticmethod
    def get_plan_features(plan_type):
        """
        جلب ميزات خطة الاشتراك
        """
        plans = {
            'basic': {
                'name': 'الخطة الأساسية',
                'max_employees': 50,
                'max_vehicles': 20,
                'max_users': 5,
                'features': [
                    'إدارة الموظفين الأساسية',
                    'إدارة المركبات',
                    'تقارير أساسية',
                    'نظام الحضور والانصراف'
                ],
                'price_monthly': 199,
                'price_yearly': 1990
            },
            'premium': {
                'name': 'الخطة المتقدمة',
                'max_employees': 200,
                'max_vehicles': 100,
                'max_users': 20,
                'features': [
                    'جميع ميزات الخطة الأساسية',
                    'تقارير متقدمة',
                    'إدارة الرواتب',
                    'نظام الإشعارات المتقدم',
                    'تكامل API'
                ],
                'price_monthly': 499,
                'price_yearly': 4990
            },
            'enterprise': {
                'name': 'خطة المؤسسات',
                'max_employees': 1000,
                'max_vehicles': 500,
                'max_users': 100,
                'features': [
                    'جميع ميزات الخطة المتقدمة',
                    'دعم متعدد الشركات',
                    'نسخ احتياطية متقدمة',
                    'دعم فني مخصص',
                    'تخصيص كامل',
                    'تدريب فريق العمل'
                ],
                'price_monthly': 999,
                'price_yearly': 9990
            }
        }
        
        return plans.get(plan_type, plans['basic'])
    
    @staticmethod
    def can_access_feature(company_id, feature_name):
        """
        التحقق من إمكانية الوصول لميزة معينة
        """
        try:
            company = Company.query.get(company_id)
            if not company or not company.subscription:
                return False
            
            subscription = company.subscription
            if subscription.is_trial_expired and subscription.is_expired:
                return False
            
            # جلب ميزات الخطة
            plan_features = SubscriptionService.get_plan_features(subscription.plan_type)
            
            # التحقق من وجود الميزة
            feature_mapping = {
                'advanced_reports': ['premium', 'enterprise'],
                'salary_management': ['premium', 'enterprise'],
                'api_integration': ['premium', 'enterprise'],
                'multi_company': ['enterprise'],
                'custom_branding': ['enterprise']
            }
            
            allowed_plans = feature_mapping.get(feature_name, ['basic', 'premium', 'enterprise'])
            return subscription.plan_type in allowed_plans
            
        except Exception as e:
            logger.error(f"خطأ في التحقق من الميزة {feature_name}: {str(e)}")
            return False