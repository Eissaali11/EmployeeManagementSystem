"""
سكريبت لتحديث هيكل جدول صور التسليم VehicleHandoverImage
لدعم ملفات PDF بالإضافة إلى الصور
"""

from datetime import datetime
from app import app, db
from models import VehicleHandoverImage
from sqlalchemy import text

def update_handover_images_table():
    """
    تحديث هيكل جدول صور التسليم لدعم ملفات PDF
    - إضافة أعمدة جديدة: file_type, file_path, file_description
    - نسخ البيانات من الأعمدة القديمة (image_path, image_description) إلى الأعمدة الجديدة
    """
    
    with app.app_context():
        # استخدام المحرك الخام للوصول المباشر إلى قاعدة البيانات
        connection = db.engine.connect()
        transaction = connection.begin()
        
        try:
            # التحقق مما إذا كانت الأعمدة الجديدة موجودة بالفعل
            columns_check = connection.execute(
                text("SELECT column_name FROM information_schema.columns WHERE table_name = 'vehicle_handover_image' AND column_name = 'file_path'")
            ).fetchone()
            
            if not columns_check:
                print("إضافة الأعمدة الجديدة للجدول...")
                
                # إضافة الأعمدة الجديدة
                connection.execute(text("ALTER TABLE vehicle_handover_image ADD COLUMN IF NOT EXISTS file_path VARCHAR(255)"))
                connection.execute(text("ALTER TABLE vehicle_handover_image ADD COLUMN IF NOT EXISTS file_type VARCHAR(20) DEFAULT 'image'"))
                connection.execute(text("ALTER TABLE vehicle_handover_image ADD COLUMN IF NOT EXISTS file_description VARCHAR(200)"))
                
                # نسخ البيانات من الأعمدة القديمة إلى الأعمدة الجديدة
                connection.execute(text("UPDATE vehicle_handover_image SET file_path = image_path WHERE file_path IS NULL"))
                connection.execute(text("UPDATE vehicle_handover_image SET file_description = image_description WHERE file_description IS NULL"))
                
                print("تم تحديث هيكل الجدول بنجاح!")
            else:
                print("الأعمدة الجديدة موجودة بالفعل، لا داعي للتحديث.")
            
            transaction.commit()
            return True
        except Exception as e:
            transaction.rollback()
            print(f"حدث خطأ أثناء تحديث هيكل الجدول: {e}")
            return False
        finally:
            connection.close()

if __name__ == "__main__":
    update_handover_images_table()