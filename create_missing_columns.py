"""
سكريبت لتحديث هيكل قاعدة البيانات وإضافة الأعمدة المفقودة
"""

from app import app, db
import models

# إعادة إنشاء الجداول المفقودة أو الأعمدة المفقودة
with app.app_context():
    # الطريقة 1: تحديث قواعد البيانات دون حذف البيانات الموجودة
    db.reflect()
    db.session.commit()
    
    # تنفيذ SQL محدد مباشرة
    try:
        db.session.execute(db.text("ALTER TABLE vehicle_workshop ADD COLUMN IF NOT EXISTS delivery_link VARCHAR(255)"))
        print("تمت إضافة العمود delivery_link بنجاح (أو كان موجودًا بالفعل)")
    except Exception as e:
        print(f"خطأ في إضافة العمود delivery_link: {str(e)}")
    
    try:
        db.session.execute(db.text("ALTER TABLE vehicle_workshop ADD COLUMN IF NOT EXISTS reception_link VARCHAR(255)"))
        print("تمت إضافة العمود reception_link بنجاح (أو كان موجودًا بالفعل)")
    except Exception as e:
        print(f"خطأ في إضافة العمود reception_link: {str(e)}")
    
    db.session.commit()
    print("تم الانتهاء من التحديث")