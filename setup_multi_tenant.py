#!/usr/bin/env python3
"""
Multi-Tenant System Setup Script
================================

This script initializes the نُظم system with multi-tenant capabilities:
1. Creates the first system owner (System Admin)
2. Sets up sample companies with trial subscriptions
3. Configures subscription plans and limits
4. Initializes the multi-tenant database structure

Usage:
    python setup_multi_tenant.py
"""

import os
import sys
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import (
    User, UserType, Company, CompanySubscription, 
    SubscriptionNotification, Module
)
from services.subscription_service import SubscriptionService

def create_system_admin():
    """إنشاء مالك النظام (System Owner)"""
    
    print("🔧 إنشاء مالك النظام...")
    
    # التحقق من وجود مالك النظام
    existing_admin = User.query.filter_by(user_type=UserType.SYSTEM_ADMIN).first()
    if existing_admin:
        print(f"✅ يوجد مالك نظام بالفعل: {existing_admin.email}")
        return existing_admin
    
    # إنشاء مالك النظام الجديد
    system_admin = User(
        email="admin@nuzum.sa",
        name="مالك النظام",
        user_type=UserType.SYSTEM_ADMIN,
        company_id=None,  # مالك النظام لا ينتمي لشركة محددة
        is_active=True,
        auth_type='local',
        created_at=datetime.utcnow()
    )
    
    # تعيين كلمة مرور افتراضية
    system_admin.set_password("admin123")
    
    db.session.add(system_admin)
    db.session.commit()
    
    print(f"✅ تم إنشاء مالك النظام: {system_admin.email}")
    print(f"🔑 كلمة المرور: admin123")
    return system_admin

def create_sample_companies():
    """إنشاء شركات تجريبية للاختبار"""
    
    print("\n🏢 إنشاء شركات تجريبية...")
    
    sample_companies = [
        {
            "name": "شركة النجاح للتجارة",
            "contact_email": "info@najah.sa",
            "contact_phone": "+966501234567",
            "address": "الرياض، السعودية",
            "plan_type": "trial"
        },
        {
            "name": "مؤسسة التقدم للخدمات",
            "contact_email": "contact@taqadum.sa", 
            "contact_phone": "+966502345678",
            "address": "جدة، السعودية",
            "plan_type": "basic"
        },
        {
            "name": "شركة الرؤية للتطوير",
            "contact_email": "admin@roya.sa",
            "contact_phone": "+966503456789", 
            "address": "الدمام، السعودية",
            "plan_type": "premium"
        }
    ]
    
    created_companies = []
    
    for company_data in sample_companies:
        # التحقق من وجود الشركة
        existing_company = Company.query.filter_by(name=company_data["name"]).first()
        if existing_company:
            print(f"⚠️  الشركة موجودة بالفعل: {company_data['name']}")
            created_companies.append(existing_company)
            continue
        
        # إنشاء الشركة
        company = Company(
            name=company_data["name"],
            contact_email=company_data["contact_email"],
            contact_phone=company_data["contact_phone"],
            address=company_data["address"],
            status="active",
            created_at=datetime.utcnow()
        )
        
        db.session.add(company)
        db.session.flush()  # للحصول على معرف الشركة
        
        # إنشاء اشتراك الشركة
        subscription = SubscriptionService.create_subscription(
            company_id=company.id,
            plan_type=company_data["plan_type"]
        )
        
        # إنشاء مدير الشركة
        company_admin = User(
            email=f"admin@{company_data['contact_email'].split('@')[1]}",
            name=f"مدير {company_data['name']}",
            user_type=UserType.COMPANY_ADMIN,
            company_id=company.id,
            is_active=True,
            auth_type='local',
            created_at=datetime.utcnow()
        )
        company_admin.set_password("admin123")
        
        db.session.add(company_admin)
        created_companies.append(company)
        
        print(f"✅ تم إنشاء الشركة: {company.name}")
        print(f"   📧 مدير الشركة: {company_admin.email}")
        print(f"   📋 نوع الاشتراك: {company_data['plan_type']}")
    
    db.session.commit()
    return created_companies

def setup_subscription_notifications():
    """إعداد إشعارات الاشتراك"""
    
    print("\n🔔 إعداد إشعارات الاشتراك...")
    
    # جلب جميع الشركات
    companies = Company.query.all()
    
    for company in companies:
        if company.subscription and company.subscription.is_trial():
            # إشعار للشركات في فترة التجربة
            notification = SubscriptionNotification(
                company_id=company.id,
                notification_type="trial_ending",
                title="انتهاء الفترة التجريبية قريباً",
                message=f"تنتهي فترتكم التجريبية في {company.subscription.days_remaining} يوم. قوموا بترقية اشتراككم للاستمرار في استخدام النظام.",
                is_read=False,
                is_urgent=company.subscription.days_remaining <= 7,
                sent_date=datetime.utcnow()
            )
            db.session.add(notification)
    
    db.session.commit()
    print("✅ تم إعداد إشعارات الاشتراك")

def verify_multi_tenant_setup():
    """التحقق من إعداد النظام متعدد المستأجرين"""
    
    print("\n🔍 التحقق من إعداد النظام...")
    
    # إحصائيات النظام
    total_companies = Company.query.count()
    total_users = User.query.count()
    system_admins = User.query.filter_by(user_type=UserType.SYSTEM_ADMIN).count()
    company_admins = User.query.filter_by(user_type=UserType.COMPANY_ADMIN).count()
    
    print(f"📊 إحصائيات النظام:")
    print(f"   🏢 إجمالي الشركات: {total_companies}")
    print(f"   👥 إجمالي المستخدمين: {total_users}")
    print(f"   👑 مالكو النظام: {system_admins}")
    print(f"   🏢 مديرو الشركات: {company_admins}")
    
    # التحقق من الاشتراكات
    active_subscriptions = CompanySubscription.query.filter_by(is_active=True).count()
    trial_subscriptions = CompanySubscription.query.filter_by(plan_type='trial').count()
    
    print(f"   💳 الاشتراكات النشطة: {active_subscriptions}")
    print(f"   🆓 الاشتراكات التجريبية: {trial_subscriptions}")
    
    return True

def main():
    """تشغيل إعداد النظام متعدد المستأجرين"""
    
    print("🚀 بدء إعداد النظام متعدد المستأجرين - نُظم")
    print("=" * 50)
    
    try:
        with app.app_context():
            # إنشاء الجداول إذا لم تكن موجودة
            print("📋 إنشاء جداول قاعدة البيانات...")
            db.create_all()
            print("✅ تم إنشاء جداول قاعدة البيانات")
            
            # إنشاء مالك النظام
            system_admin = create_system_admin()
            
            # إنشاء الشركات التجريبية
            companies = create_sample_companies()
            
            # إعداد إشعارات الاشتراك
            setup_subscription_notifications()
            
            # التحقق من الإعداد
            verify_multi_tenant_setup()
            
            print("\n" + "=" * 50)
            print("🎉 تم إعداد النظام متعدد المستأجرين بنجاح!")
            print("\n📝 معلومات تسجيل الدخول:")
            print("   مالك النظام:")
            print(f"   📧 البريد الإلكتروني: {system_admin.email}")
            print("   🔑 كلمة المرور: admin123")
            print("\n   مديرو الشركات:")
            for company in companies:
                admin = User.query.filter_by(
                    company_id=company.id,
                    user_type=UserType.COMPANY_ADMIN
                ).first()
                if admin:
                    print(f"   📧 {company.name}: {admin.email}")
            print("   🔑 كلمة المرور للجميع: admin123")
            
            print("\n🌐 يمكنكم الآن الوصول للنظام عبر:")
            print("   - /login (تسجيل الدخول)")
            print("   - /system-admin/dashboard (لوحة مالك النظام)")
            print("   - /company-admin/dashboard (لوحة مدير الشركة)")
            
    except Exception as e:
        print(f"❌ خطأ في إعداد النظام: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)