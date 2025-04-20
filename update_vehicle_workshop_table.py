"""
سكريبت لتحديث جدول vehicle_workshop بإضافة حقول جديدة
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, MetaData, Table, Column, String, text
from sqlalchemy.ext.declarative import declarative_base
import os

# الحصول على رابط قاعدة البيانات من المتغيرات البيئية
DATABASE_URL = os.environ.get("DATABASE_URL")

# إعداد المحرك واتصال قاعدة البيانات
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# إنشاء الاتصال بقاعدة البيانات
conn = engine.connect()

# تحديث جدول vehicle_workshop لإضافة الحقول الجديدة
try:
    # التحقق من وجود العمود الأول
    conn.execute(text("SELECT delivery_link FROM vehicle_workshop LIMIT 1"))
    print("العمود delivery_link موجود بالفعل.")
except Exception:
    # إضافة العمود إذا لم يكن موجوداً
    conn.execute(text("ALTER TABLE vehicle_workshop ADD COLUMN delivery_link VARCHAR(255)"))
    conn.commit()
    print("تمت إضافة العمود delivery_link بنجاح.")

try:
    # التحقق من وجود العمود الثاني
    conn.execute(text("SELECT reception_link FROM vehicle_workshop LIMIT 1"))
    print("العمود reception_link موجود بالفعل.")
except Exception:
    # إضافة العمود إذا لم يكن موجوداً
    conn.execute(text("ALTER TABLE vehicle_workshop ADD COLUMN reception_link VARCHAR(255)"))
    conn.commit()
    print("تمت إضافة العمود reception_link بنجاح.")

# إغلاق الاتصال
conn.close()
print("تم الانتهاء من تحديث جدول vehicle_workshop.")