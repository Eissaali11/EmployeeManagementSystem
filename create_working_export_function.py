#!/usr/bin/env python3
"""
إنشاء وظيفة تصدير Excel تعمل بالحقول الصحيحة
"""

# الوظيفة الجديدة المحدثة
new_export_function = '''
@vehicles_bp.route('/export_all_excel')
@login_required
def export_all_vehicles_excel():
    """تصدير جميع بيانات المركبات إلى ملف Excel شامل - إصدار محدث يعمل"""
    try:
        import io
        import pandas as pd
        from datetime import datetime
        
        # الحصول على جميع المركبات
        vehicles = Vehicle.query.order_by(Vehicle.plate_number).all()
        
        if not vehicles:
            flash('لا توجد مركبات للتصدير!', 'warning')
            return redirect(url_for('vehicles.index'))
        
        # إنشاء buffer لملف Excel
        buffer = io.BytesIO()
        
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            
            # ===== الورقة الأولى: بيانات المركبات الأساسية =====
            vehicles_data = []
            for vehicle in vehicles:
                vehicles_data.append({
                    'رقم اللوحة': vehicle.plate_number or '',
                    'الماركة': vehicle.make or '',
                    'الموديل': vehicle.model or '',
                    'سنة الصنع': vehicle.year or '',
                    'اللون': vehicle.color or '',
                    'اسم السائق': vehicle.driver_name or '',
                    'الحالة': {
                        'available': 'متاحة',
                        'rented': 'مؤجرة', 
                        'in_use': 'في الاستخدام',
                        'maintenance': 'في الصيانة',
                        'in_workshop': 'في الورشة',
                        'in_project': 'في المشروع',
                        'accident': 'حادث',
                        'sold': 'مباعة'
                    }.get(vehicle.status, vehicle.status or ''),
                    'تاريخ انتهاء الفحص الدوري': vehicle.inspection_expiry_date.strftime('%Y-%m-%d') if vehicle.inspection_expiry_date else '',
                    'تاريخ انتهاء الاستمارة': vehicle.registration_expiry_date.strftime('%Y-%m-%d') if vehicle.registration_expiry_date else '',
                    'تاريخ انتهاء التفويض': vehicle.authorization_expiry_date.strftime('%Y-%m-%d') if vehicle.authorization_expiry_date else '',
                    'ملاحظات': vehicle.notes or '',
                    'تاريخ الإضافة': vehicle.created_at.strftime('%Y-%m-%d') if vehicle.created_at else ''
                })
            
            df_vehicles = pd.DataFrame(vehicles_data)
            df_vehicles.to_excel(writer, sheet_name='المركبات', index=False)
            
            # ===== الورقة الثانية: سجلات الورشة =====
            workshop_data = []
            for vehicle in vehicles:
                workshops = VehicleWorkshop.query.filter_by(vehicle_id=vehicle.id).all()
                for workshop in workshops:
                    workshop_data.append({
                        'رقم اللوحة': vehicle.plate_number or '',
                        'تاريخ الدخول': workshop.entry_date.strftime('%Y-%m-%d') if workshop.entry_date else '',
                        'تاريخ الخروج': workshop.exit_date.strftime('%Y-%m-%d') if workshop.exit_date else 'لا يزال في الورشة',
                        'السبب': workshop.reason or '',
                        'الوصف': workshop.description or '',
                        'حالة الإصلاح': workshop.repair_status or '',
                        'التكلفة': workshop.cost or 0,
                        'اسم الورشة': workshop.workshop_name or '',
                        'اسم الفني': workshop.technician_name or '',
                        'ملاحظات': workshop.notes or ''
                    })
            
            if workshop_data:
                df_workshop = pd.DataFrame(workshop_data)
                df_workshop.to_excel(writer, sheet_name='سجلات الورشة', index=False)
            
            # ===== الورقة الثالثة: سجلات الإيجار =====
            rental_data = []
            for vehicle in vehicles:
                rentals = VehicleRental.query.filter_by(vehicle_id=vehicle.id).all()
                for rental in rentals:
                    rental_data.append({
                        'رقم اللوحة': vehicle.plate_number or '',
                        'اسم المؤجر': rental.lessor_name or '',
                        'معلومات الاتصال': rental.lessor_contact or '',
                        'تاريخ البداية': rental.start_date.strftime('%Y-%m-%d') if rental.start_date else '',
                        'تاريخ النهاية': rental.end_date.strftime('%Y-%m-%d') if rental.end_date else 'مستمر',
                        'التكلفة الشهرية': rental.monthly_cost or 0,
                        'رقم العقد': rental.contract_number or '',
                        'المدينة': rental.city or '',
                        'الحالة': 'نشط' if rental.is_active else 'منتهي',
                        'ملاحظات': rental.notes or ''
                    })
            
            if rental_data:
                df_rental = pd.DataFrame(rental_data)
                df_rental.to_excel(writer, sheet_name='سجلات الإيجار', index=False)
            
            # ===== الورقة الرابعة: سجلات المشاريع =====
            project_data = []
            for vehicle in vehicles:
                projects = VehicleProject.query.filter_by(vehicle_id=vehicle.id).all()
                for project in projects:
                    project_data.append({
                        'رقم اللوحة': vehicle.plate_number or '',
                        'اسم المشروع': project.project_name or '',
                        'تاريخ البداية': project.start_date.strftime('%Y-%m-%d') if project.start_date else '',
                        'تاريخ النهاية': project.end_date.strftime('%Y-%m-%d') if project.end_date else '',
                        'ملاحظات': project.notes or ''
                    })
            
            if project_data:
                df_project = pd.DataFrame(project_data)
                df_project.to_excel(writer, sheet_name='سجلات المشاريع', index=False)
            
            # ===== الورقة الخامسة: سجلات التسليم والاستلام =====
            handover_data = []
            for vehicle in vehicles:
                handovers = VehicleHandover.query.filter_by(vehicle_id=vehicle.id).all()
                for handover in handovers:
                    handover_data.append({
                        'رقم اللوحة': vehicle.plate_number or '',
                        'نوع العملية': {
                            'delivery': 'تسليم',
                            'return': 'استلام'
                        }.get(handover.handover_type, handover.handover_type or ''),
                        'اسم الشخص': handover.person_name or '',
                        'التاريخ': handover.handover_date.strftime('%Y-%m-%d') if handover.handover_date else '',
                        'قراءة العداد': handover.mileage or '',
                        'مستوى الوقود': handover.fuel_level or '',
                        'ملاحظات': handover.notes or ''
                    })
            
            if handover_data:
                df_handover = pd.DataFrame(handover_data)
                df_handover.to_excel(writer, sheet_name='سجلات التسليم', index=False)
        
        buffer.seek(0)
        
        # إنشاء اسم الملف مع التاريخ
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'جميع_بيانات_المركبات_{timestamp}.xlsx'
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        flash(f'خطأ في تصدير البيانات: {str(e)}', 'danger')
        return redirect(url_for('vehicles.index'))
'''

print("تم إنشاء وظيفة التصدير المحدثة والتي تعمل بالحقول الصحيحة")