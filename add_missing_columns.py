"""
أداة مساعدة لإضافة الأعمدة المفقودة في قاعدة البيانات
"""
from app import app, db
from sqlalchemy import text

def add_columns():
    """إضافة الأعمدة المفقودة إلى جدول vehicle_handover"""
    print("جارٍ إضافة الأعمدة المفقودة في جدول تسليم/استلام السيارة...")
    
    with app.app_context():
        # التحقق من وجود العمود supervisor_name
        try:
            db.session.execute(text("SELECT supervisor_name FROM vehicle_handover LIMIT 1"))
            print("عمود supervisor_name موجود بالفعل")
        except Exception:
            # إضافة العمود إذا لم يكن موجوداً
            db.session.execute(text("ALTER TABLE vehicle_handover ADD COLUMN supervisor_name VARCHAR(100)"))
            print("تم إضافة عمود supervisor_name بنجاح")
        
        # التحقق من وجود العمود form_link
        try:
            db.session.execute(text("SELECT form_link FROM vehicle_handover LIMIT 1"))
            print("عمود form_link موجود بالفعل")
        except Exception:
            # إضافة العمود إذا لم يكن موجوداً
            db.session.execute(text("ALTER TABLE vehicle_handover ADD COLUMN form_link VARCHAR(255)"))
            print("تم إضافة عمود form_link بنجاح")
        
        # حفظ التغييرات
        db.session.commit()
        print("تم الانتهاء من تحديث قاعدة البيانات بنجاح")

if __name__ == "__main__":
    add_columns()