from datetime import datetime
import pandas as pd
import io

def generate_complete_vehicle_excel_report(vehicle, rental=None, workshop_records=None, documents=None, handovers=None, inspections=None):
    """إنشاء تقرير شامل للسيارة بصيغة Excel يتضمن جميع البيانات المتاحة"""
    
    # إنشاء كاتب اكسل
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # معلومات السيارة الأساسية
        vehicle_data = {
            'رقم اللوحة': [vehicle.plate_number],
            'الشركة المصنعة': [vehicle.make],
            'الطراز': [vehicle.model],
            'سنة الصنع': [vehicle.year],
            'اللون': [vehicle.color],
            'الحالة': [vehicle.status],
            'تاريخ الإضافة': [vehicle.created_at.strftime('%Y-%m-%d') if vehicle.created_at else ''],
            'آخر تحديث': [vehicle.updated_at.strftime('%Y-%m-%d') if vehicle.updated_at else ''],
            'ملاحظات': [vehicle.notes or ''],
        }
        
        # إنشاء ورقة معلومات السيارة
        vehicle_df = pd.DataFrame(vehicle_data)
        vehicle_df.to_excel(writer, sheet_name='معلومات السيارة', index=False)
        
        # تنسيق الورقة
        worksheet = writer.sheets['معلومات السيارة']
        worksheet.right_to_left()
        
        # إذا كانت بيانات الإيجار متوفرة
        if rental:
            rental_data = {
                'تاريخ البداية': [rental.start_date.strftime('%Y-%m-%d') if rental.start_date else ''],
                'تاريخ النهاية': [rental.end_date.strftime('%Y-%m-%d') if rental.end_date else 'مستمر'],
                'قيمة الإيجار الشهري': [float(rental.monthly_cost) if rental.monthly_cost else 0],
                'حالة الإيجار': ['نشط' if rental.is_active else 'منتهي'],
                'المؤجر': [rental.lessor_name or ''],
                'معلومات الاتصال': [rental.lessor_contact or ''],
                'رقم العقد': [rental.contract_number or ''],
                'ملاحظات': [rental.notes or '']
            }
            rental_df = pd.DataFrame(rental_data)
            rental_df.to_excel(writer, sheet_name='معلومات الإيجار', index=False)
            
            # تنسيق ورقة الإيجار
            worksheet = writer.sheets['معلومات الإيجار']
            worksheet.right_to_left()
        
        # إذا كانت سجلات الورشة متوفرة
        if workshop_records:
            workshop_data = []
            for record in workshop_records:
                workshop_data.append({
                    'تاريخ الدخول': record.entry_date.strftime('%Y-%m-%d') if record.entry_date else '',
                    'تاريخ الخروج': record.exit_date.strftime('%Y-%m-%d') if record.exit_date else 'لا يزال في الورشة',
                    'اسم الورشة': record.workshop_name or '',
                    'سبب الصيانة': record.reason or '',
                    'التكلفة': float(record.cost) if record.cost else 0,
                    'القراءة قبل الصيانة': record.mileage_before or 0,
                    'القراءة بعد الصيانة': record.mileage_after or 0,
                    'الملاحظات': record.notes or ''
                })
            
            if workshop_data:
                workshop_df = pd.DataFrame(workshop_data)
                workshop_df.to_excel(writer, sheet_name='سجلات الصيانة', index=False)
                
                # تنسيق ورقة الصيانة
                worksheet = writer.sheets['سجلات الصيانة']
                worksheet.right_to_left()
        
        # الحصول على سجلات التسليم/الاستلام
        if handovers is None:
            from models import VehicleHandover
            # جلب السجلات إذا لم يتم توفيرها
            handovers = VehicleHandover.query.filter_by(vehicle_id=vehicle.id).order_by(
                VehicleHandover.handover_date.desc()
            ).all()
        
        # إضافة سجلات التسليم/الاستلام
        if handovers:
            handover_data = []
            for handover in handovers:
                handover_data.append({
                    'التاريخ': handover.handover_date.strftime('%Y-%m-%d') if handover.handover_date else '',
                    'نوع العملية': 'تسليم' if handover.handover_type == 'delivery' else 'استلام',
                    'اسم الشخص': handover.person_name or '',
                    'اسم المشرف': handover.supervisor_name if hasattr(handover, 'supervisor_name') else '',
                    'قراءة العداد': handover.mileage or 0,
                    'مستوى الوقود': handover.fuel_level or '',
                    'حالة المركبة': handover.vehicle_condition or '',
                    'إطار احتياطي': 'نعم' if handover.has_spare_tire else 'لا',
                    'طفاية حريق': 'نعم' if handover.has_fire_extinguisher else 'لا',
                    'حقيبة إسعافات': 'نعم' if handover.has_first_aid_kit else 'لا',
                    'مثلث تحذير': 'نعم' if handover.has_warning_triangle else 'لا',
                    'أدوات': 'نعم' if handover.has_tools else 'لا',
                    'ملاحظات': handover.notes or '',
                    'رابط النموذج': handover.form_link or ''
                })
            
            if handover_data:
                handover_df = pd.DataFrame(handover_data)
                handover_df.to_excel(writer, sheet_name='سجلات التسليم والاستلام', index=False)
                
                # تنسيق ورقة التسليم والاستلام
                worksheet = writer.sheets['سجلات التسليم والاستلام']
                worksheet.right_to_left()
        
        # الحصول على سجلات الفحص
        if inspections is None:
            from models import VehiclePeriodicInspection
            # جلب السجلات إذا لم يتم توفيرها
            inspections = VehiclePeriodicInspection.query.filter_by(vehicle_id=vehicle.id).order_by(
                VehiclePeriodicInspection.inspection_date.desc()
            ).all()
        
        # إضافة سجلات الفحص
        if inspections:
            inspection_data = []
            for inspection in inspections:
                inspection_data.append({
                    'رقم الفحص': inspection.inspection_number if hasattr(inspection, 'inspection_number') else '',
                    'تاريخ الفحص': inspection.inspection_date.strftime('%Y-%m-%d') if inspection.inspection_date else '',
                    'تاريخ الانتهاء': inspection.expiry_date.strftime('%Y-%m-%d') if inspection.expiry_date else '',
                    'نوع الفحص': getattr(inspection, 'inspection_type', ''),
                    'مركز الفحص': inspection.inspection_center if hasattr(inspection, 'inspection_center') else '',
                    'النتيجة': inspection.result if hasattr(inspection, 'result') else '',
                    'التكلفة': float(inspection.cost) if hasattr(inspection, 'cost') and inspection.cost else 0,
                    'ملاحظات': inspection.notes or ''
                })
            
            if inspection_data:
                inspection_df = pd.DataFrame(inspection_data)
                inspection_df.to_excel(writer, sheet_name='سجلات الفحص', index=False)
                
                # تنسيق ورقة الفحص
                worksheet = writer.sheets['سجلات الفحص']
                worksheet.right_to_left()
        
        # إضافة بيانات الوثائق إذا كانت متوفرة
        if documents:
            documents_data = []
            for doc in documents:
                documents_data.append({
                    'نوع الوثيقة': doc.document_type or '',
                    'رقم الوثيقة': doc.document_number or '',
                    'تاريخ الإصدار': doc.issue_date.strftime('%Y-%m-%d') if hasattr(doc, 'issue_date') and doc.issue_date else '',
                    'تاريخ الانتهاء': doc.expiry_date.strftime('%Y-%m-%d') if hasattr(doc, 'expiry_date') and doc.expiry_date else '',
                    'الحالة': doc.status or '',
                    'ملاحظات': doc.notes or ''
                })
            
            if documents_data:
                documents_df = pd.DataFrame(documents_data)
                documents_df.to_excel(writer, sheet_name='وثائق السيارة', index=False)
                
                # تنسيق ورقة الوثائق
                worksheet = writer.sheets['وثائق السيارة']
                worksheet.right_to_left()
        
        # إضافة معلومات التقرير
        info_data = {
            'معلومات التقرير': [''],
            'تاريخ إنشاء التقرير': [datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            'اسم النظام': ['نُظم - نظام إدارة متكامل'],
        }
        info_df = pd.DataFrame(info_data)
        info_df.to_excel(writer, sheet_name='معلومات التقرير', index=False)
        
        # تنسيق ورقة المعلومات
        worksheet = writer.sheets['معلومات التقرير']
        worksheet.right_to_left()
    
    # إرجاع محتوى الملف
    return output.getvalue()
