"""
سكريبت لتعديل قيود NOT NULL في جدول الوثائق (documents)
يسمح بإدخال قيم NULL في حقول issue_date و expiry_date
"""

from app import app, db
from sqlalchemy import text

def modify_document_constraints():
    """
    تعديل قيود NOT NULL في جدول الوثائق
    """
    print("بدء تعديل قيود NOT NULL في جدول الوثائق...")
    
    # استخدام raw SQL للتغيير في هيكل الجدول
    with app.app_context():
        try:
            # تغيير حقل issue_date للسماح بقيم NULL
            db.session.execute(text("ALTER TABLE document ALTER COLUMN issue_date DROP NOT NULL;"))
            print("تم تعديل حقل issue_date للسماح بقيم NULL")
            
            # تغيير حقل expiry_date للسماح بقيم NULL
            db.session.execute(text("ALTER TABLE document ALTER COLUMN expiry_date DROP NOT NULL;"))
            print("تم تعديل حقل expiry_date للسماح بقيم NULL")
            
            # تطبيق التغييرات
            db.session.commit()
            print("تم تطبيق التغييرات بنجاح!")
            
        except Exception as e:
            db.session.rollback()
            print(f"حدث خطأ: {str(e)}")

if __name__ == "__main__":
    modify_document_constraints()
    print("تم الانتهاء من تعديل القيود")