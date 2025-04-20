"""
اختبار تقرير الورشة بالتصميم الجديد
"""

import os
import io
from datetime import datetime, timedelta
from flask import Flask, current_app
from app import db
from models import Vehicle, VehicleWorkshop

# إنشاء تطبيق Flask للاختبار
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# استيراد وظيفة تقرير الورشة
from utils.workshop_report import generate_workshop_report_pdf

def test_workshop_report():
    """اختبار إنشاء تقرير ورشة"""
    with app.app_context():
        # البحث عن سيارة للاختبار
        vehicle = Vehicle.query.first()
        
        if not vehicle:
            print("لا توجد سيارات في قاعدة البيانات")
            return
        
        # البحث عن سجلات الورشة للسيارة
        workshop_records = VehicleWorkshop.query.filter_by(vehicle_id=vehicle.id).all()
        
        if not workshop_records:
            print(f"لا توجد سجلات ورشة للسيارة {vehicle.plate_number}")
            # إنشاء سجل ورشة وهمي للاختبار
            entry_date = datetime.now().date() - timedelta(days=7)
            exit_date = datetime.now().date() - timedelta(days=2)
            
            workshop_record = VehicleWorkshop(
                vehicle_id=vehicle.id,
                entry_date=entry_date,
                exit_date=exit_date,
                reason='maintenance',
                description='صيانة دورية للسيارة',
                repair_status='completed',
                cost=500.0,
                workshop_name='ورشة تجريبية',
                technician_name='فني تجريبي',
                notes='ملاحظات للاختبار'
            )
            
            db.session.add(workshop_record)
            db.session.commit()
            
            workshop_records = [workshop_record]
            print(f"تم إنشاء سجل ورشة تجريبي للسيارة {vehicle.plate_number}")
        
        # إنشاء التقرير
        pdf_buffer = generate_workshop_report_pdf(vehicle, workshop_records)
        
        # حفظ التقرير في ملف للفحص
        output_path = os.path.join(os.getcwd(), f'test_workshop_report_{vehicle.plate_number}.pdf')
        with open(output_path, 'wb') as f:
            f.write(pdf_buffer.read())
        
        print(f"تم إنشاء تقرير الورشة بنجاح: {output_path}")
        
if __name__ == '__main__':
    test_workshop_report()