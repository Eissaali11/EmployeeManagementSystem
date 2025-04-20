"""
سكريبت لترحيل بيانات المستخدمين من النظام القديم (أدوار نصية) إلى النظام الجديد (أدوار enum)
"""

from app import db
from models import User, UserRole

def migrate_user_roles():
    """
    ترحيل أدوار المستخدمين من النظام القديم إلى النظام الجديد
    """
    print("بدء ترحيل أدوار المستخدمين...")
    
    try:
        # الحصول على جميع المستخدمين
        users = User.query.all()
        updated_count = 0
        
        for user in users:
            # التحويل من النص إلى الـ enum
            if hasattr(user, 'role') and isinstance(user.role, str):
                old_role = user.role
                new_role = None
                
                # تحويل الأدوار النصية إلى كائنات enum
                if old_role == 'admin':
                    new_role = UserRole.ADMIN
                elif old_role == 'manager':
                    new_role = UserRole.MANAGER
                elif old_role == 'hr':
                    new_role = UserRole.HR
                elif old_role == 'finance':
                    new_role = UserRole.FINANCE
                elif old_role == 'fleet':
                    new_role = UserRole.FLEET
                else:
                    new_role = UserRole.USER
                
                # تحديث الدور
                try:
                    # استخدام استعلام مباشر لتجنب مشكلة تحويل النوع
                    db.session.execute(
                        "UPDATE \"user\" SET role = :new_role WHERE id = :user_id",
                        {"new_role": new_role.value, "user_id": user.id}
                    )
                    updated_count += 1
                except Exception as ex:
                    print(f"خطأ في تحديث المستخدم {user.email}: {str(ex)}")
        
        # حفظ التغييرات
        db.session.commit()
        print(f"تم ترحيل {updated_count} مستخدم بنجاح")
        return True
    
    except Exception as e:
        db.session.rollback()
        print(f"خطأ في ترحيل أدوار المستخدمين: {str(e)}")
        return False

# تنفيذ الترحيل عند استدعاء السكريبت مباشرة
if __name__ == "__main__":
    from flask import Flask
    from app import create_app
    
    app = create_app()
    with app.app_context():
        migrate_user_roles()