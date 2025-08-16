#!/usr/bin/env python3
"""
سكريبت لإضافة صلاحيات المحاسبة للمستخدمين وضمان ظهورها في القائمة
"""

import os
import sys
from datetime import datetime

# إضافة المجلد الحالي إلى مسار البحث
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, UserRole, Module, UserPermission, Permission

def add_accounting_permissions():
    """إضافة صلاحيات المحاسبة للمستخدمين"""
    
    with app.app_context():
        print("🔄 إضافة صلاحيات المحاسبة...")
        
        try:
            # البحث عن المستخدمين الإداريين
            admin_users = User.query.filter_by(role=UserRole.ADMIN).all()
            
            if not admin_users:
                print("⚠️ لا يوجد مستخدمين إداريين. سأنشئ مستخدم إداري تجريبي...")
                
                # إنشاء مستخدم إداري تجريبي
                admin_user = User(
                    email='admin@nuzum.com',
                    username='admin',
                    name='مدير النظام',
                    role=UserRole.ADMIN,
                    is_active=True,
                    auth_type='local'
                )
                
                # تعيين كلمة مرور
                from werkzeug.security import generate_password_hash
                admin_user.password_hash = generate_password_hash('admin123')
                
                db.session.add(admin_user)
                db.session.commit()
                
                admin_users = [admin_user]
                print("✅ تم إنشاء مستخدم إداري: admin@nuzum.com / admin123")
            
            # إضافة صلاحيات المحاسبة لكل مدير
            for admin_user in admin_users:
                # التحقق من وجود صلاحية المحاسبة
                # استخدم القيمة الصحيحة من قاعدة البيانات
                from models import Module as ModuleEnum
                
                # أنشئ الـ module باستخدام القيمة النصية مباشرة
                try:
                    accounting_module = ModuleEnum('accounting')
                except ValueError:
                    # إذا لم تنجح، استخدم القيمة مباشرة
                    print("⚠️ استخدام القيمة النصية مباشرة...")
                    
                # إنشاء الصلاحية يدوياً في قاعدة البيانات
                from sqlalchemy import text
                result = db.session.execute(text("""
                    SELECT COUNT(*) FROM user_permission 
                    WHERE user_id = :user_id AND module = 'accounting'
                """), {'user_id': admin_user.id})
                
                existing_count = result.scalar()
                
                if existing_count == 0:
                    # إدراج الصلاحية مباشرة
                    db.session.execute(text("""
                        INSERT INTO user_permission (user_id, module, permissions)
                        VALUES (:user_id, 'accounting', :permissions)
                    """), {
                        'user_id': admin_user.id,
                        'permissions': Permission.ADMIN
                    })
                    print(f"✅ تم إضافة صلاحية المحاسبة للمستخدم: {admin_user.email}")
                else:
                    print(f"ℹ️ صلاحية المحاسبة موجودة مسبقاً للمستخدم: {admin_user.email}")
            
            db.session.commit()
            
            # عرض تفاصيل المستخدمين
            print("\n📋 المستخدمين الإداريين:")
            for user in admin_users:
                print(f"   - {user.email} ({user.name}) - {user.role.value}")
                
                # عرض صلاحيات المحاسبة
                accounting_perm = UserPermission.query.filter_by(
                    user_id=user.id,
                    module=Module.ACCOUNTING
                ).first()
                
                if accounting_perm:
                    print(f"     ✅ يملك صلاحيات المحاسبة")
                else:
                    print(f"     ❌ لا يملك صلاحيات المحاسبة")
            
            return True
            
        except Exception as e:
            print(f"❌ خطأ في إضافة صلاحيات المحاسبة: {str(e)}")
            db.session.rollback()
            return False

def verify_accounting_access():
    """التحقق من إمكانية الوصول للمحاسبة"""
    
    with app.app_context():
        print("\n🔍 التحقق من إمكانية الوصول للمحاسبة...")
        
        try:
            # التحقق من وجود وحدة المحاسبة
            if hasattr(Module, 'ACCOUNTING'):
                print("✅ وحدة المحاسبة موجودة في النظام")
            else:
                print("❌ وحدة المحاسبة غير موجودة في النظام")
                return False
            
            # التحقق من توفر طرق المحاسبة
            try:
                from routes.accounting import accounting_bp
                print("✅ طرق المحاسبة متوفرة")
            except ImportError as e:
                print(f"❌ خطأ في استيراد طرق المحاسبة: {str(e)}")
                return False
            
            # التحقق من الجداول المحاسبية
            try:
                from models_accounting import Account, FiscalYear
                accounts_count = Account.query.count()
                fiscal_years_count = FiscalYear.query.count()
                
                print(f"✅ عدد الحسابات المحاسبية: {accounts_count}")
                print(f"✅ عدد السنوات المالية: {fiscal_years_count}")
                
                if accounts_count == 0:
                    print("⚠️ لا توجد حسابات محاسبية. تشغيل setup_accounting.py أولاً")
                
            except Exception as e:
                print(f"❌ خطأ في الوصول للجداول المحاسبية: {str(e)}")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ خطأ في التحقق من النظام المحاسبي: {str(e)}")
            return False

def main():
    """الدالة الرئيسية"""
    print("🚀 إعداد صلاحيات النظام المحاسبي")
    print("="*40)
    
    # إضافة الصلاحيات
    success1 = add_accounting_permissions()
    
    # التحقق من النظام
    success2 = verify_accounting_access()
    
    if success1 and success2:
        print("\n🎉 تم إعداد صلاحيات المحاسبة بنجاح!")
        print("📝 يمكنك الآن:")
        print("   1. تسجيل الدخول بحساب admin@nuzum.com")
        print("   2. كلمة المرور: admin123")
        print("   3. ستجد رابط 'المحاسبة' في القائمة الجانبية")
        print("   4. الوصول المباشر: /accounting")
    else:
        print("\n❌ فشل في إعداد صلاحيات المحاسبة")
        print("🔍 يرجى مراجعة الأخطاء أعلاه")

if __name__ == "__main__":
    main()