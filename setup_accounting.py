#!/usr/bin/env python3
"""
سكريبت إعداد النظام المحاسبي
"""

import os
import sys
from datetime import datetime, date

# إضافة المجلد الحالي إلى مسار البحث
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# استيراد التطبيق والقاعدة
from app import app, db
from models import UserRole
from models_accounting import *
from services.accounting_service import AccountingService

def setup_accounting_system():
    """إعداد النظام المحاسبي بالكامل"""
    
    with app.app_context():
        print("🔄 بدء إعداد النظام المحاسبي...")
        
        try:
            # 1. إنشاء جداول قاعدة البيانات
            print("📊 إنشاء جداول قاعدة البيانات...")
            db.create_all()
            print("✅ تم إنشاء جداول قاعدة البيانات بنجاح")
            
            # 2. إنشاء دليل الحسابات الأساسي
            print("📋 إنشاء دليل الحسابات الأساسي...")
            success, message = AccountingService.initialize_chart_of_accounts()
            print(f"{'✅' if success else '❌'} {message}")
            
            # 3. إنشاء السنة المالية الحالية
            current_year = datetime.now().year
            print(f"📅 إنشاء السنة المالية {current_year}...")
            success, message = AccountingService.create_fiscal_year(current_year)
            print(f"{'✅' if success else '❌'} {message}")
            
            # 4. إنشاء مراكز التكلفة من الأقسام الموجودة
            print("🏢 إنشاء مراكز التكلفة...")
            success, message = AccountingService.create_cost_centers()
            print(f"{'✅' if success else '❌'} {message}")
            
            # 5. إنشاء إعدادات النظام الافتراضية
            print("⚙️ إنشاء إعدادات النظام...")
            existing_settings = AccountingSettings.query.first()
            if not existing_settings:
                settings = AccountingSettings(
                    company_name='شركة نُظم',
                    tax_number='',
                    commercial_register='',
                    address='المملكة العربية السعودية',
                    phone='',
                    email='',
                    base_currency='SAR',
                    decimal_places=2,
                    transaction_prefix='JV',
                    fiscal_year_start_month=1,
                    next_transaction_number=1
                )
                db.session.add(settings)
                db.session.commit()
                print("✅ تم إنشاء إعدادات النظام بنجاح")
            else:
                print("ℹ️ إعدادات النظام موجودة مسبقاً")
            
            # 6. إنشاء بعض الموردين والعملاء الافتراضيين
            print("👥 إنشاء الموردين والعملاء الافتراضيين...")
            create_default_vendors_customers()
            
            # 7. تحديث أرصدة الحسابات
            print("💰 تحديث أرصدة الحسابات...")
            success, message = AccountingService.update_account_balances()
            print(f"{'✅' if success else '❌'} {message}")
            
            print("\n🎉 تم إعداد النظام المحاسبي بنجاح!")
            print("📌 يمكنك الآن الوصول إلى النظام المحاسبي عبر الرابط: /accounting")
            
            # عرض ملخص النظام
            display_system_summary()
            
        except Exception as e:
            print(f"❌ خطأ في إعداد النظام المحاسبي: {str(e)}")
            return False
    
    return True

def create_default_vendors_customers():
    """إنشاء الموردين والعملاء الافتراضيين"""
    try:
        # الموردين الافتراضيين
        default_vendors = [
            {
                'code': 'V001',
                'name': 'محطة وقود أرامكو',
                'phone': '920000001',
                'description': 'محطة وقود رئيسية'
            },
            {
                'code': 'V002', 
                'name': 'ورشة الخليج للصيانة',
                'phone': '920000002',
                'description': 'ورشة صيانة المركبات'
            },
            {
                'code': 'V003',
                'name': 'شركة التأمين الشاملة',
                'phone': '920000003',
                'description': 'شركة تأمين المركبات'
            }
        ]
        
        for vendor_data in default_vendors:
            existing = Vendor.query.filter_by(code=vendor_data['code']).first()
            if not existing:
                vendor = Vendor(
                    code=vendor_data['code'],
                    name=vendor_data['name'],
                    phone=vendor_data['phone'],
                    contact_person='مسؤول المبيعات',
                    payment_terms='نقداً',
                    is_active=True
                )
                db.session.add(vendor)
        
        # العملاء الافتراضيين
        default_customers = [
            {
                'code': 'C001',
                'name': 'عميل تجريبي 1',
                'phone': '920000101'
            },
            {
                'code': 'C002',
                'name': 'عميل تجريبي 2', 
                'phone': '920000102'
            }
        ]
        
        for customer_data in default_customers:
            existing = Customer.query.filter_by(code=customer_data['code']).first()
            if not existing:
                customer = Customer(
                    code=customer_data['code'],
                    name=customer_data['name'],
                    phone=customer_data['phone'],
                    contact_person='مسؤول المشتريات',
                    is_active=True
                )
                db.session.add(customer)
        
        db.session.commit()
        print("✅ تم إنشاء الموردين والعملاء الافتراضيين")
        
    except Exception as e:
        print(f"❌ خطأ في إنشاء الموردين والعملاء: {str(e)}")
        db.session.rollback()

def display_system_summary():
    """عرض ملخص النظام المحاسبي"""
    try:
        print("\n" + "="*50)
        print("📊 ملخص النظام المحاسبي")
        print("="*50)
        
        # عدد الحسابات
        accounts_count = Account.query.count()
        print(f"📋 عدد الحسابات: {accounts_count}")
        
        # عدد السنوات المالية
        fiscal_years_count = FiscalYear.query.count()
        active_fiscal_year = FiscalYear.query.filter_by(is_active=True).first()
        print(f"📅 عدد السنوات المالية: {fiscal_years_count}")
        if active_fiscal_year:
            print(f"📅 السنة المالية النشطة: {active_fiscal_year.name}")
        
        # عدد مراكز التكلفة
        cost_centers_count = CostCenter.query.count()
        print(f"🏢 عدد مراكز التكلفة: {cost_centers_count}")
        
        # عدد الموردين والعملاء
        vendors_count = Vendor.query.count()
        customers_count = Customer.query.count()
        print(f"👥 عدد الموردين: {vendors_count}")
        print(f"👥 عدد العملاء: {customers_count}")
        
        # عدد المعاملات
        transactions_count = Transaction.query.count()
        print(f"📄 عدد المعاملات: {transactions_count}")
        
        print("="*50)
        
    except Exception as e:
        print(f"❌ خطأ في عرض الملخص: {str(e)}")

def add_accounting_to_app():
    """إضافة النظام المحاسبي إلى التطبيق"""
    print("🔧 إضافة النظام المحاسبي إلى التطبيق...")
    
    # قراءة ملف app.py
    with open('app.py', 'r', encoding='utf-8') as f:
        app_content = f.read()
    
    # إضافة استيراد طرق المحاسبة
    if 'from routes.accounting import accounting_bp' not in app_content:
        # البحث عن موقع الإدراج
        lines = app_content.split('\n')
        insert_index = -1
        
        for i, line in enumerate(lines):
            if 'from routes.vehicle_operations import vehicle_operations_bp' in line:
                insert_index = i + 1
                break
        
        if insert_index > -1:
            # إضافة الأسطر الجديدة
            lines.insert(insert_index, "    ")
            lines.insert(insert_index + 1, "    # استيراد طرق النظام المحاسبي")
            lines.insert(insert_index + 2, "    from routes.accounting import accounting_bp")
            lines.insert(insert_index + 3, "    from routes.accounting_extended import accounting_ext_bp")
            
            # البحث عن موقع تسجيل البلوبرينت
            for i, line in enumerate(lines):
                if 'app.register_blueprint(vehicle_operations_bp' in line:
                    lines.insert(i + 1, "    app.register_blueprint(accounting_bp, url_prefix='/accounting')")
                    lines.insert(i + 2, "    app.register_blueprint(accounting_ext_bp, url_prefix='/accounting')")
                    break
            
            # كتابة الملف المحدث
            with open('app.py', 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            
            print("✅ تم إضافة النظام المحاسبي إلى التطبيق")
    else:
        print("ℹ️ النظام المحاسبي مُضاف بالفعل إلى التطبيق")

def main():
    """الدالة الرئيسية"""
    print("🚀 بدء إعداد النظام المحاسبي الشامل لنُظم")
    print("="*60)
    
    # 1. إضافة النظام إلى التطبيق
    add_accounting_to_app()
    
    # 2. إعداد قاعدة البيانات والبيانات الأساسية
    success = setup_accounting_system()
    
    if success:
        print("\n🎉 تم إكمال إعداد النظام المحاسبي بنجاح!")
        print("📝 الخطوات التالية:")
        print("   1. إعادة تشغيل التطبيق")
        print("   2. تسجيل الدخول بحساب المدير")
        print("   3. الانتقال إلى /accounting للبدء")
        print("   4. مراجعة دليل الحسابات وتخصيصه حسب الحاجة")
        print("   5. إنشاء قيود تجريبية للاختبار")
    else:
        print("\n❌ فشل في إعداد النظام المحاسبي")
        print("🔍 يرجى مراجعة الأخطاء أعلاه وإعادة المحاولة")

if __name__ == "__main__":
    main()