from app import app, db
from models import VehicleMaintenance

with app.app_context():
    db.create_all()
    print("تم تحديث قاعدة البيانات بنجاح!")