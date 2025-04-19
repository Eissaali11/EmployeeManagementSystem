import os
import sys
from werkzeug.security import generate_password_hash

# إضافة المسار الحالي إلى مسارات النظام
current_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_path)

# استيراد app و db بعد إضافة المسار
try:
    from main import app, db
    from models import User
except ImportError as e:
    print(f"حدث خطأ أثناء استيراد الوحدات: {e}")
    sys.exit(1)

def create_default_admin():
    """إنشاء مستخدم مسؤول افتراضي إذا لم يكن موجوداً"""
    print("جاري محاولة إنشاء مستخدم مسؤول افتراضي...")
    
    try:
        with app.app_context():
            # التحقق مما إذا كان يوجد مستخدمين في النظام
            user_count = User.query.count()
            
            if user_count == 0:
                # إنشاء مستخدم جديد إذا لم يكن هناك مستخدمين
                default_admin = User(
                    username="admin",
                    email="admin@example.com",
                    password_hash=generate_password_hash("admin123")
                )
                
                db.session.add(default_admin)
                db.session.commit()
                print("تم إنشاء مستخدم المسؤول الافتراضي بنجاح.")
                print("اسم المستخدم: admin")
                print("البريد الإلكتروني: admin@example.com")
                print("كلمة المرور: admin123")
                print("يرجى تغيير كلمة المرور فور تسجيل الدخول!")
            else:
                print("يوجد مستخدمين بالفعل في قاعدة البيانات. لم يتم إنشاء مستخدم جديد.")
    except Exception as e:
        print(f"حدث خطأ أثناء إنشاء المستخدم الافتراضي: {e}")
        return False
    
    return True

def initialize_database():
    """تهيئة قاعدة البيانات وإنشاء الجداول"""
    print("جاري تهيئة قاعدة البيانات...")
    
    try:
        with app.app_context():
            # إنشاء جميع الجداول
            db.create_all()
            print("تم إنشاء جداول قاعدة البيانات بنجاح.")
    except Exception as e:
        print(f"حدث خطأ أثناء تهيئة قاعدة البيانات: {e}")
        return False
    
    return True

def check_environment():
    """التحقق من وجود المتغيرات البيئية المطلوبة"""
    required_vars = ['DATABASE_URL', 'SECRET_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.environ.get(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("تحذير: بعض المتغيرات البيئية المطلوبة غير محددة:")
        for var in missing_vars:
            print(f"- {var}")
        
        print("\nيرجى التأكد من تعيين هذه المتغيرات في ملف .env أو في إعدادات خادم الويب.")
        return False
    
    return True

def main():
    """الدالة الرئيسية لإعداد النظام"""
    print("=== بدء إعداد نظام إدارة الموظفين ===")
    
    # التحقق من المتغيرات البيئية
    if not check_environment():
        print("تحذير: بعض المتغيرات البيئية غير مكتملة. سيتم المتابعة مع إمكانية حدوث أخطاء.")
    
    # تهيئة قاعدة البيانات
    if not initialize_database():
        print("فشل تهيئة قاعدة البيانات. يرجى التحقق من إعدادات الاتصال.")
        sys.exit(1)
    
    # إنشاء مستخدم المسؤول الافتراضي
    if not create_default_admin():
        print("فشل إنشاء مستخدم المسؤول الافتراضي.")
    
    print("\n=== تم إكمال إعداد النظام بنجاح ===")
    print("يمكنك الآن تشغيل التطبيق باستخدام Gunicorn أو نظام WSGI آخر.")

if __name__ == "__main__":
    main()