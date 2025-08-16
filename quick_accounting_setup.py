#!/usr/bin/env python3
"""
سكريبت سريع لإعداد النظام المحاسبي وإنشاء البيانات الأساسية
"""

import os
import sys
from datetime import datetime, date

# إضافة المجلد الحالي إلى مسار البحث
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# استيراد التطبيق والقاعدة
from app import app, db

def create_accounting_tables():
    """إنشاء جداول النظام المحاسبي"""
    with app.app_context():
        print("🔄 إنشاء جداول النظام المحاسبي...")
        try:
            db.create_all()
            print("✅ تم إنشاء جداول قاعدة البيانات بنجاح")
            
            # تحقق من إنشاء الجداول المحاسبية
            from models_accounting import Account, FiscalYear, Transaction, CostCenter
            
            # إنشاء حسابات أساسية بسيطة
            accounts = [
                {'code': '1000', 'name': 'الأصول', 'account_type': 'assets', 'level': 0},
                {'code': '1100', 'name': 'الأصول المتداولة', 'account_type': 'assets', 'level': 1},
                {'code': '1110', 'name': 'النقدية والبنوك', 'account_type': 'assets', 'level': 2},
                {'code': '2000', 'name': 'الخصوم', 'account_type': 'liabilities', 'level': 0},
                {'code': '3000', 'name': 'حقوق الملكية', 'account_type': 'equity', 'level': 0},
                {'code': '4000', 'name': 'الإيرادات', 'account_type': 'revenue', 'level': 0},
                {'code': '5000', 'name': 'المصروفات', 'account_type': 'expenses', 'level': 0},
                {'code': '5100', 'name': 'مصروفات الموظفين', 'account_type': 'expenses', 'level': 1},
                {'code': '5200', 'name': 'مصروفات المركبات', 'account_type': 'expenses', 'level': 1},
            ]
            
            from models_accounting import AccountType
            
            for acc_data in accounts:
                existing = Account.query.filter_by(code=acc_data['code']).first()
                if not existing:
                    account = Account(
                        code=acc_data['code'],
                        name=acc_data['name'],
                        account_type=getattr(AccountType, acc_data['account_type'].upper()),
                        level=acc_data['level'],
                        is_active=True,
                        balance=0
                    )
                    db.session.add(account)
            
            # إنشاء السنة المالية الحالية
            current_year = datetime.now().year
            existing_fy = FiscalYear.query.filter_by(year=current_year).first()
            if not existing_fy:
                fy = FiscalYear(
                    name=f"السنة المالية {current_year}",
                    year=current_year,
                    start_date=date(current_year, 1, 1),
                    end_date=date(current_year, 12, 31),
                    is_active=True,
                    is_closed=False
                )
                db.session.add(fy)
            
            # إنشاء مراكز التكلفة من الأقسام
            from models import Department
            departments = Department.query.all()
            for dept in departments:
                existing_cc = CostCenter.query.filter_by(code=f"CC{dept.id:03d}").first()
                if not existing_cc:
                    cost_center = CostCenter(
                        code=f"CC{dept.id:03d}",
                        name=dept.name,
                        description=f"مركز تكلفة قسم {dept.name}",
                        is_active=True
                    )
                    db.session.add(cost_center)
            
            db.session.commit()
            print("✅ تم إنشاء البيانات الأساسية للنظام المحاسبي")
            
            return True
            
        except Exception as e:
            print(f"❌ خطأ في إعداد النظام المحاسبي: {str(e)}")
            db.session.rollback()
            return False

def main():
    """الدالة الرئيسية"""
    print("🚀 بدء إعداد النظام المحاسبي السريع لنُظم")
    print("="*50)
    
    success = create_accounting_tables()
    
    if success:
        print("\n🎉 تم إكمال إعداد النظام المحاسبي بنجاح!")
        print("📝 يمكنك الآن:")
        print("   1. الدخول إلى /accounting لاستكشاف النظام")
        print("   2. إضافة المزيد من الحسابات")
        print("   3. إنشاء قيود محاسبية")
        print("   4. إنتاج التقارير المالية")
    else:
        print("\n❌ فشل في إعداد النظام المحاسبي")

if __name__ == "__main__":
    main()