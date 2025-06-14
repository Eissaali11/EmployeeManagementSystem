#!/usr/bin/env python3
"""
إنشاء وظيفة تصدير Excel تعمل بالحقول الصحيحة
"""

def create_working_export():
    """إنشاء وظيفة تصدير تعمل"""
    
    # قراءة الملف الحالي
    with open('routes/vehicles.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # البحث عن بداية ونهاية دالة export_expired_documents_excel
    start_marker = 'def export_expired_documents_excel():'
    end_marker = 'def index():'
    
    start_pos = content.find(start_marker)
    end_pos = content.find(end_marker)
    
    if start_pos != -1 and end_pos != -1:
        # استبدال الدالة بنسخة مبسطة تعمل
        new_function = '''def export_expired_documents_excel():
    """تصدير بيانات الوثائق المنتهية للمركبات إلى ملف Excel منسق"""
    try:
        from io import BytesIO
        import pandas as pd
        from flask import make_response
        
        # جمع بيانات الاستمارات المنتهية
        vehicles = Vehicle.query.all()
        reg_data = []
        
        for vehicle in vehicles:
            if vehicle.istmara_expiry_date:
                days_until_expiry = (vehicle.istmara_expiry_date - datetime.now().date()).days
                
                reg_data.append({
                    'رقم اللوحة': vehicle.plate_number or '',
                    'ماركة السيارة': vehicle.make or '',
                    'موديل السيارة': vehicle.model or '',
                    'تاريخ انتهاء الاستمارة': vehicle.istmara_expiry_date.strftime('%Y-%m-%d') if vehicle.istmara_expiry_date else '',
                    'عدد أيام الانتهاء': days_until_expiry,
                    'الحالة': 'منتهية' if days_until_expiry < 0 else 'ستنتهي قريباً' if days_until_expiry <= 30 else 'سارية'
                })
        
        # جمع بيانات الفحص الدوري المنتهي
        inspection_data = []
        for vehicle in vehicles:
            inspections = VehiclePeriodicInspection.query.filter_by(vehicle_id=vehicle.id).all()
            for inspection in inspections:
                if inspection.expiry_date:
                    days_until_expiry = (inspection.expiry_date - datetime.now().date()).days
                    
                    inspection_data.append({
                        'رقم اللوحة': vehicle.plate_number or '',
                        'ماركة السيارة': vehicle.make or '',
                        'موديل السيارة': vehicle.model or '',
                        'تاريخ الفحص': inspection.inspection_date.strftime('%Y-%m-%d') if inspection.inspection_date else '',
                        'تاريخ الانتهاء': inspection.expiry_date.strftime('%Y-%m-%d') if inspection.expiry_date else '',
                        'مركز الفحص': inspection.inspection_center or '',
                        'رقم الفحص': inspection.inspection_number or '',
                        'نتيجة الفحص': inspection.result or '',
                        'عدد أيام الانتهاء': days_until_expiry,
                        'الحالة': 'منتهية' if days_until_expiry < 0 else 'ستنتهي قريباً' if days_until_expiry <= 30 else 'سارية'
                    })
        
        # إنشاء ملف Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # ورقة الاستمارات
            if reg_data:
                reg_df = pd.DataFrame(reg_data)
                reg_df.to_excel(writer, sheet_name='استمارات منتهية', index=False)
            
            # ورقة الفحص الدوري
            if inspection_data:
                insp_df = pd.DataFrame(inspection_data)
                insp_df.to_excel(writer, sheet_name='فحص دوري منتهي', index=False)
        
        output.seek(0)
        
        # إنشاء الاستجابة
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f'attachment; filename=expired_documents_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        
        return response
        
    except Exception as e:
        flash(f'خطأ في تصدير البيانات: {str(e)}', 'error')
        return redirect(url_for('vehicles.expired_documents'))

'''
        
        # استبدال الدالة
        before_function = content[:start_pos]
        after_function = content[end_pos:]
        
        new_content = before_function + new_function + after_function
        
        # حفظ الملف
        with open('routes/vehicles.py', 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("✅ تم إنشاء وظيفة تصدير تعمل بشكل صحيح")
    else:
        print("❌ لم يتم العثور على الدالة")

if __name__ == "__main__":
    create_working_export()