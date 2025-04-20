"""
سكريبت لتحديث قاعدة البيانات وإعادة إنشاء جدول المستخدمين بعد التغييرات
"""

from app import db
from models import User, UserRole, UserPermission
from werkzeug.security import generate_password_hash
from sqlalchemy import text

def reset_user_table():
    """إعادة إنشاء جدول المستخدمين بعد تغيير نوع الدور"""
    try:
        # حفظ بيانات المستخدمين الحالية
        print("جاري جمع بيانات المستخدمين الحالية...")
        
        existing_users = []
        try:
            # محاولة الوصول إلى بيانات المستخدمين الحالية
            # قد يفشل بسبب مشكلة في عمود الدور الذي تم تغييره
            users = db.session.execute(text("SELECT id, email, name, password_hash, firebase_uid, profile_picture, last_login, is_active, auth_type, employee_id FROM \"user\"")).fetchall()
            for user in users:
                existing_users.append({
                    'id': user[0],
                    'email': user[1],
                    'name': user[2],
                    'password_hash': user[3],
                    'firebase_uid': user[4],
                    'profile_picture': user[5],
                    'last_login': user[6],
                    'is_active': user[7],
                    'auth_type': user[8],
                    'employee_id': user[9]
                })
            print(f"تم استرجاع {len(existing_users)} مستخدم من قاعدة البيانات")
        except Exception as e:
            print(f"تعذر استرجاع بيانات المستخدمين الحالية: {str(e)}")
            
        # حذف جداول الصلاحيات والمستخدمين
        print("جاري حذف جداول الصلاحيات والمستخدمين...")
        db.session.execute(text("DROP TABLE IF EXISTS user_permission CASCADE"))
        db.session.execute(text("DROP TABLE IF EXISTS system_audit CASCADE"))
        db.session.execute(text("DROP TABLE IF EXISTS \"user\" CASCADE"))
        db.session.commit()
        
        # إعادة إنشاء الجداول
        print("جاري إعادة إنشاء الجداول...")
        db.create_all()
        db.session.commit()
        
        # إعادة إنشاء مستخدم المدير إذا لم يكن هناك مستخدمين
        if not existing_users:
            print("إنشاء مستخدم المدير الافتراضي...")
            admin = User(
                email="admin@example.com",
                name="مدير النظام",
                role=UserRole.ADMIN,
                is_active=True
            )
            admin.password_hash = generate_password_hash("adminpass")
            db.session.add(admin)
            db.session.commit()
            print("تم إنشاء مستخدم المدير بنجاح")
        else:
            # إعادة إنشاء المستخدمين الموجودين
            print("إعادة إنشاء المستخدمين الموجودين...")
            for user_data in existing_users:
                try:
                    user = User(
                        id=user_data['id'],
                        email=user_data['email'],
                        name=user_data['name'],
                        password_hash=user_data['password_hash'],
                        firebase_uid=user_data['firebase_uid'],
                        profile_picture=user_data['profile_picture'],
                        role=UserRole.ADMIN if user_data['email'] == 'admin@example.com' else UserRole.USER,
                        last_login=user_data['last_login'],
                        is_active=user_data['is_active'],
                        auth_type=user_data['auth_type'],
                        employee_id=user_data['employee_id']
                    )
                    db.session.add(user)
                except Exception as e:
                    print(f"خطأ في إعادة إنشاء المستخدم {user_data['email']}: {str(e)}")
                    
            db.session.commit()
            print("تم إعادة إنشاء المستخدمين بنجاح")
        
        print("تم تحديث قاعدة البيانات بنجاح")
        return True
    
    except Exception as e:
        db.session.rollback()
        print(f"حدث خطأ أثناء تحديث قاعدة البيانات: {str(e)}")
        return False

# تنفيذ التحديث عند استدعاء السكريبت مباشرة
if __name__ == "__main__":
    from flask import Flask
    import app as flask_app
    
    app = flask_app.app
    with app.app_context():
        reset_user_table()