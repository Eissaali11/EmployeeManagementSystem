"""
سكريبت لإضافة أعمدة تواريخ الوثائق إلى جدول المركبات
"""

from app import db, app
from sqlalchemy import Column, Date, text
from models import Vehicle

print("بدء إضافة أعمدة تواريخ الوثائق إلى جدول المركبات...")

with app.app_context():
    # استخدام DDL مباشرة لإضافة الأعمدة الجديدة
    # إضافة عمود تاريخ انتهاء التفويض
    db.session.execute(text("""
        ALTER TABLE vehicle 
        ADD COLUMN IF NOT EXISTS authorization_expiry_date DATE DEFAULT NULL;
    """))
    
    # إضافة عمود تاريخ انتهاء استمارة السيارة
    db.session.execute(text("""
        ALTER TABLE vehicle 
        ADD COLUMN IF NOT EXISTS registration_expiry_date DATE DEFAULT NULL;
    """))
    
    # إضافة عمود تاريخ انتهاء الفحص الدوري
    db.session.execute(text("""
        ALTER TABLE vehicle 
        ADD COLUMN IF NOT EXISTS inspection_expiry_date DATE DEFAULT NULL;
    """))
    
    # تطبيق التغييرات
    db.session.commit()
    
    print("تم إضافة أعمدة تواريخ الوثائق بنجاح!")