from app import app, db

with app.app_context():
    # إعادة إنشاء جميع الجداول
    db.drop_all()
    db.create_all()
    
    print("تم إعادة إنشاء قاعدة البيانات بنجاح!")