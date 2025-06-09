#!/usr/bin/env python3
"""
اختبار إنشاء تقرير تسليم/استلام PDF للتأكد من عمل التحسينات
"""

import sys
import os
sys.path.append('.')

from app import app, db
from models import VehicleHandover, Vehicle
from utils.weasyprint_handover_pdf import generate_enhanced_handover_pdf

def test_handover_pdf():
    """اختبار إنشاء تقرير تسليم/استلام PDF"""
    with app.app_context():
        # البحث عن سجل تسليم/استلام موجود
        handover = db.session.query(VehicleHandover).filter_by(id=89).first()
        
        if not handover:
            print("❌ لم يتم العثور على سجل تسليم/استلام #89")
            return False
            
        print(f"✓ تم العثور على سجل تسليم/استلام #89")
        print(f"  - المركبة: {handover.vehicle.plate_number if handover.vehicle else 'غير محدد'}")
        print(f"  - الشخص: {getattr(handover, 'person_name', 'غير محدد')}")
        print(f"  - التاريخ: {handover.handover_date}")
        print(f"  - النوع: {handover.handover_type}")
        
        try:
            # إنشاء ملف PDF
            pdf_content = generate_enhanced_handover_pdf(handover)
            
            # حفظ الملف للاختبار
            with open('test_handover_89.pdf', 'wb') as f:
                f.write(pdf_content)
                
            print(f"✓ تم إنشاء ملف PDF بنجاح: test_handover_89.pdf")
            print(f"  - حجم الملف: {len(pdf_content)} بايت")
            
            return True
            
        except Exception as e:
            print(f"❌ خطأ في إنشاء PDF: {str(e)}")
            return False

if __name__ == "__main__":
    print("🧪 اختبار إنشاء تقرير تسليم/استلام PDF...")
    success = test_handover_pdf()
    if success:
        print("🎉 الاختبار نجح!")
    else:
        print("💥 فشل الاختبار!")