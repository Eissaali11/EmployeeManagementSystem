from datetime import datetime
import pandas as pd
import io

def generate_complete_vehicle_excel_report(vehicle, rental=None, workshop_records=None, documents=None, handovers=None, inspections=None):
    """إنشاء تقرير شامل للسيارة بصيغة Excel يتضمن جميع البيانات المتاحة مع لوحة معلومات"""
    
    # إنشاء كاتب اكسل
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        
        # إنشاء تنسيقات مختلفة للتقرير
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1
        })
        
        subheader_format = workbook.add_format({
            'bold': True,
            'font_size': 12,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#8EA9DB',
            'font_color': 'white',
            'border': 1
        })
        
        cell_format = workbook.add_format({
            'font_size': 11,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1
        })
        
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 16,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#203764',
            'font_color': 'white'
        })
        
        date_format = workbook.add_format({
            'font_size': 11,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'num_format': 'yyyy-mm-dd'
        })
        
        number_format = workbook.add_format({
            'font_size': 11,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'num_format': '#,##0.00'
        })
        
        percent_format = workbook.add_format({
            'font_size': 11,
            'align': 'center',
            'valign': 'vcenter',
            'border': 1,
            'num_format': '0.00%'
        })
        
        # إنشاء ورقة لوحة المعلومات (داشبورد)
        dashboard_sheet = workbook.add_worksheet('لوحة المعلومات')
        dashboard_sheet.right_to_left()
        dashboard_sheet.set_column('A:A', 25)
        dashboard_sheet.set_column('B:B', 30)
        dashboard_sheet.set_column('C:C', 30)
        dashboard_sheet.set_column('D:D', 25)
        dashboard_sheet.set_row(0, 30)
        
        # عنوان لوحة المعلومات
        dashboard_sheet.merge_range('A1:D1', f'تقرير شامل للسيارة: {vehicle.plate_number}', title_format)
        dashboard_sheet.merge_range('A2:D2', f'{vehicle.make} {vehicle.model} {vehicle.year}', subheader_format)
        
        # إضافة معلومات السيارة الرئيسية
        dashboard_sheet.merge_range('A4:D4', 'معلومات السيارة الأساسية', header_format)
        
        vehicle_data = [
            ['رقم اللوحة', vehicle.plate_number or ''],
            ['الشركة المصنعة', vehicle.make or ''],
            ['الطراز', vehicle.model or ''],
            ['سنة الصنع', vehicle.year or ''],
            ['اللون', vehicle.color or ''],
            ['الحالة', vehicle.status or ''],
            ['اسم السائق', vehicle.driver_name or 'غير محدد'],
            ['تاريخ انتهاء التفويض', vehicle.authorization_expiry_date.strftime('%Y-%m-%d') if vehicle.authorization_expiry_date else 'غير محدد'],
            ['تاريخ انتهاء الاستمارة', vehicle.registration_expiry_date.strftime('%Y-%m-%d') if vehicle.registration_expiry_date else 'غير محدد'],
            ['تاريخ انتهاء الفحص الدوري', vehicle.inspection_expiry_date.strftime('%Y-%m-%d') if vehicle.inspection_expiry_date else 'غير محدد'],
            ['رابط Google Drive', vehicle.drive_folder_link or 'غير محدد'],
            ['ملاحظات', vehicle.notes or 'لا توجد ملاحظات'],
            ['تاريخ الإضافة', vehicle.created_at.strftime('%Y-%m-%d %H:%M') if vehicle.created_at else ''],
            ['تاريخ آخر تحديث', vehicle.updated_at.strftime('%Y-%m-%d %H:%M') if vehicle.updated_at else ''],
        ]
        
        for i, (label, value) in enumerate(vehicle_data):
            dashboard_sheet.write(i+5, 0, label, subheader_format)
            dashboard_sheet.write(i+5, 1, value, cell_format)
        
        # إضافة معلومات الإيجار (إذا كانت متوفرة)
        if rental:
            dashboard_sheet.merge_range('C4:D4', 'معلومات الإيجار', header_format)
            
            rental_data = [
                ['تاريخ البداية', rental.start_date.strftime('%Y-%m-%d') if rental.start_date else ''],
                ['تاريخ النهاية', rental.end_date.strftime('%Y-%m-%d') if rental.end_date else 'مستمر'],
                ['قيمة الإيجار الشهري', float(rental.monthly_cost) if rental.monthly_cost else 0],
                ['حالة الإيجار', 'نشط' if rental.is_active else 'منتهي'],
                ['المؤجر', rental.lessor_name or ''],
                ['رقم العقد', rental.contract_number or ''],
                ['معلومات الاتصال', rental.lessor_contact or ''],
            ]
            
            for i, (label, value) in enumerate(rental_data):
                dashboard_sheet.write(i+5, 2, label, subheader_format)
                if label == 'قيمة الإيجار الشهري':
                    dashboard_sheet.write(i+5, 3, value, number_format)
                else:
                    dashboard_sheet.write(i+5, 3, value, cell_format)
        
        # إضافة الملخص الإحصائي في لوحة المعلومات
        row_pos = 13  # موقع الصف الجديد
        dashboard_sheet.merge_range(f'A{row_pos}:D{row_pos}', 'ملخص البيانات', header_format)
        row_pos += 1
        
        # إحصائيات سجلات الصيانة
        workshop_count = len(workshop_records) if workshop_records else 0
        total_workshop_cost = sum(float(r.cost) if r.cost else 0 for r in workshop_records) if workshop_records else 0
        
        # إحصائيات سجلات الفحص
        inspection_count = len(inspections) if inspections else 0
        
        # إحصائيات سجلات التسليم والاستلام
        handover_count = len(handovers) if handovers else 0
        delivery_count = sum(1 for h in handovers if h.handover_type == 'delivery') if handovers else 0
        receipt_count = sum(1 for h in handovers if h.handover_type == 'receipt') if handovers else 0
        
        # إضافة الملخص الإحصائي إلى لوحة المعلومات
        summary_data = [
            ['عدد سجلات الصيانة', workshop_count],
            ['إجمالي تكاليف الصيانة', total_workshop_cost],
            ['عدد سجلات الفحص', inspection_count],
            ['عدد سجلات التسليم/الاستلام', handover_count],
            ['عدد عمليات التسليم', delivery_count],
            ['عدد عمليات الاستلام', receipt_count],
        ]
        
        dashboard_sheet.write(row_pos, 0, 'المؤشر', subheader_format)
        dashboard_sheet.write(row_pos, 1, 'القيمة', subheader_format)
        dashboard_sheet.write(row_pos, 2, 'الملاحظات', subheader_format)
        row_pos += 1
        
        for i, (label, value) in enumerate(summary_data):
            dashboard_sheet.write(row_pos + i, 0, label, cell_format)
            if label == 'إجمالي تكاليف الصيانة':
                dashboard_sheet.write(row_pos + i, 1, value, number_format)
                comment = 'إجمالي المبالغ المدفوعة على صيانة السيارة'
            else:
                dashboard_sheet.write(row_pos + i, 1, value, cell_format)
                comment = ''
            
            if comment:
                dashboard_sheet.write(row_pos + i, 2, comment, cell_format)
        
        # ------------------ إنشاء صفحات التقرير التفصيلية ------------------
        
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
        worksheet.set_column('A:Z', 18)
        
        # تنسيق العناوين
        for col_num, value in enumerate(vehicle_df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
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
            worksheet.set_column('A:Z', 18)
            
            # تنسيق العناوين
            for col_num, value in enumerate(rental_df.columns.values):
                worksheet.write(0, col_num, value, header_format)
        
        # إذا كانت سجلات الورشة متوفرة - نسخة محسنة وشاملة
        if workshop_records:
            workshop_data = []
            for record in workshop_records:
                # حساب مدة البقاء في الورشة
                if record.exit_date and record.entry_date:
                    duration_days = (record.exit_date - record.entry_date).days
                    duration_text = f'{duration_days} يوم'
                elif record.entry_date:
                    current_duration = (datetime.now().date() - record.entry_date).days
                    duration_text = f'{current_duration} يوم (مازال في الورشة)'
                else:
                    duration_text = 'غير محدد'
                
                # تحديد حالة العملية
                if record.exit_date:
                    operation_status = 'مكتملة'
                else:
                    operation_status = 'جارية'
                
                # ترجمة حالة الإصلاح للعربية
                repair_status_ar = {
                    'in_progress': 'قيد التنفيذ',
                    'completed': 'تم الإصلاح',
                    'pending_approval': 'بانتظار الموافقة',
                    'waiting_parts': 'بانتظار قطع الغيار',
                    'on_hold': 'متوقف مؤقتاً'
                }.get(record.repair_status, record.repair_status or 'غير محدد')
                
                workshop_data.append({
                    'رقم العملية': record.id,
                    'تاريخ الدخول': record.entry_date.strftime('%Y-%m-%d') if record.entry_date else 'غير محدد',
                    'تاريخ الخروج': record.exit_date.strftime('%Y-%m-%d') if record.exit_date else 'لا يزال في الورشة',
                    'مدة البقاء': duration_text,
                    'حالة العملية': operation_status,
                    'اسم الورشة': record.workshop_name or 'غير محدد',
                    'الفني المسؤول': record.technician_name or 'غير محدد',
                    'سبب الدخول': record.reason or 'غير محدد',
                    'وصف العطل/الصيانة': record.description or 'غير محدد',
                    'حالة الإصلاح': repair_status_ar,
                    'التكلفة (ريال)': float(record.cost) if record.cost else 0,
                    'رابط تسليم الورشة': record.delivery_link or 'غير متوفر',
                    'رابط استلام من الورشة': record.reception_link or 'غير متوفر',
                    'ملاحظات إضافية': record.notes or 'لا توجد ملاحظات',
                    'تاريخ الإنشاء': record.created_at.strftime('%Y-%m-%d %H:%M') if record.created_at else '',
                    'آخر تحديث': record.updated_at.strftime('%Y-%m-%d %H:%M') if record.updated_at else ''
                })
            
            if workshop_data:
                workshop_df = pd.DataFrame(workshop_data)
                workshop_df.to_excel(writer, sheet_name='عمليات الورش', index=False)
                
                # تنسيق ورقة عمليات الورش
                worksheet = writer.sheets['عمليات الورش']
                worksheet.right_to_left()
                
                # تحديد عرض الأعمدة حسب المحتوى
                column_widths = {
                    'A': 12,  # رقم العملية
                    'B': 15,  # تاريخ الدخول
                    'C': 15,  # تاريخ الخروج
                    'D': 18,  # مدة البقاء
                    'E': 12,  # حالة العملية
                    'F': 20,  # اسم الورشة
                    'G': 18,  # الفني المسؤول
                    'H': 15,  # سبب الدخول
                    'I': 30,  # وصف العطل
                    'J': 15,  # حالة الإصلاح
                    'K': 12,  # التكلفة
                    'L': 25,  # رابط تسليم
                    'M': 25,  # رابط استلام
                    'N': 25,  # ملاحظات
                    'O': 18,  # تاريخ الإنشاء
                    'P': 18   # آخر تحديث
                }
                
                for col, width in column_widths.items():
                    worksheet.set_column(f'{col}:{col}', width)
                
                # تنسيق العناوين
                for col_num, value in enumerate(workshop_df.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                
                # تنسيق صفوف البيانات مع ألوان حسب الحالة
                for row_num in range(1, len(workshop_data) + 1):
                    # تحديد لون الصف حسب حالة العملية
                    operation_status = workshop_data[row_num-1]['حالة العملية']
                    repair_status = workshop_data[row_num-1]['حالة الإصلاح']
                    
                    if operation_status == 'مكتملة' and repair_status == 'تم الإصلاح':
                        bg_color = '#C6E0B4'  # أخضر فاتح للمكتملة بنجاح
                    elif operation_status == 'مكتملة':
                        bg_color = '#FFE4B5'  # أصفر فاتح للمكتملة مع مشاكل
                    else:
                        bg_color = '#FFCCCB'  # أحمر فاتح للجارية
                    
                    for col_num in range(len(workshop_df.columns)):
                        # تنسيق خاص لعمود التكلفة
                        if col_num == 10:  # عمود التكلفة
                            cost_format = workbook.add_format({
                                'bg_color': bg_color, 
                                'border': 1, 
                                'align': 'center', 
                                'num_format': '#,##0.00'
                            })
                            worksheet.write(row_num, col_num, workshop_df.iloc[row_num-1, col_num], cost_format)
                        else:
                            row_format = workbook.add_format({
                                'bg_color': bg_color, 
                                'border': 1, 
                                'align': 'center',
                                'valign': 'vcenter',
                                'text_wrap': True
                            })
                            worksheet.write(row_num, col_num, workshop_df.iloc[row_num-1, col_num], row_format)
        
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
                    'اسم المشرف': getattr(handover, 'supervisor_name', 'غير محدد'),
                    'قراءة العداد': handover.mileage or 0,
                    'مستوى الوقود': getattr(handover, 'fuel_level', 'غير محدد'),
                    'حالة المركبة': getattr(handover, 'vehicle_condition', 'غير محدد'),
                    'إطار احتياطي': 'نعم' if getattr(handover, 'has_spare_tire', False) else 'لا',
                    'طفاية حريق': 'نعم' if getattr(handover, 'has_fire_extinguisher', False) else 'لا',
                    'حقيبة إسعافات': 'نعم' if getattr(handover, 'has_first_aid_kit', False) else 'لا',
                    'مثلث تحذير': 'نعم' if getattr(handover, 'has_warning_triangle', False) else 'لا',
                    'أدوات': 'نعم' if getattr(handover, 'has_tools', False) else 'لا',
                    'ملاحظات': handover.notes or '',
                    'رابط النموذج': getattr(handover, 'form_link', 'غير متوفر'),
                    'رقم الهاتف': getattr(handover, 'driver_phone_number', 'غير محدد'),
                    'رقم الإقامة': getattr(handover, 'driver_residency_number', 'غير محدد'),
                    'المشروع': getattr(handover, 'project_name', 'غير محدد'),
                    'المدينة': getattr(handover, 'city', 'غير محدد')
                })
            
            if handover_data:
                handover_df = pd.DataFrame(handover_data)
                handover_df.to_excel(writer, sheet_name='سجلات التسليم والاستلام', index=False)
                
                # تنسيق ورقة التسليم والاستلام
                worksheet = writer.sheets['سجلات التسليم والاستلام']
                worksheet.right_to_left()
                worksheet.set_column('A:Z', 18)
                
                # تنسيق العناوين
                for col_num, value in enumerate(handover_df.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                
                # تطبيق ألوان مختلفة بناءً على نوع العملية
                for row_num in range(1, len(handover_data) + 1):
                    operation_type = handover_df.iloc[row_num-1, 1]  # نوع العملية
                    
                    # إضافة خلفية مناسبة لنوع العملية
                    row_format = workbook.add_format({
                        'font_size': 11,
                        'align': 'center',
                        'valign': 'vcenter',
                        'border': 1,
                        'bg_color': '#C6E0B4' if operation_type == 'تسليم' else '#D9E1F2'  # أخضر للتسليم، أزرق للاستلام
                    })
                    
                    for col_num in range(len(handover_df.columns)):
                        # نحتفظ بتنسيق الأرقام للعمود الخامس
                        if col_num == 4:  # قراءة العداد
                            value = handover_df.iloc[row_num-1, col_num]
                            num_format = workbook.add_format({
                                'font_size': 11,
                                'align': 'center',
                                'valign': 'vcenter',
                                'border': 1,
                                'num_format': '#,##0',
                                'bg_color': '#C6E0B4' if operation_type == 'تسليم' else '#D9E1F2'
                            })
                            worksheet.write(row_num, col_num, value, num_format)
                        else:
                            worksheet.write(row_num, col_num, handover_df.iloc[row_num-1, col_num], row_format)
        
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
                worksheet.set_column('A:Z', 18)
                
                # تنسيق العناوين
                for col_num, value in enumerate(inspection_df.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                
                # تنسيق صفوف البيانات
                for row_num in range(1, len(inspection_data) + 1):
                    # تنسيق عمود التكلفة
                    cost_idx = 6  # index of cost column
                    if cost_idx < len(inspection_df.columns):
                        worksheet.write(row_num, cost_idx, inspection_df.iloc[row_num-1, cost_idx], number_format)
        
        # إضافة بيانات الوثائق (استخدام البيانات المخزنة في السيارة مباشرة)
        documents_data = []
        # إضافة وثائق السيارة الأساسية من البيانات المخزنة
        if vehicle.authorization_expiry_date:
            days_left = (vehicle.authorization_expiry_date - datetime.now().date()).days if vehicle.authorization_expiry_date else 0
            status = 'سارية' if days_left > 30 else 'تنتهي قريباً' if days_left > 0 else 'منتهية'
            documents_data.append({
                'نوع الوثيقة': 'تفويض السيارة',
                'تاريخ الانتهاء': vehicle.authorization_expiry_date.strftime('%Y-%m-%d'),
                'الأيام المتبقية': days_left,
                'الحالة': status,
                'ملاحظات': f'{"تحتاج تجديد" if days_left <= 30 else "سارية"}'
            })
        
        if vehicle.registration_expiry_date:
            days_left = (vehicle.registration_expiry_date - datetime.now().date()).days if vehicle.registration_expiry_date else 0
            status = 'سارية' if days_left > 30 else 'تنتهي قريباً' if days_left > 0 else 'منتهية'
            documents_data.append({
                'نوع الوثيقة': 'استمارة السيارة',
                'تاريخ الانتهاء': vehicle.registration_expiry_date.strftime('%Y-%m-%d'),
                'الأيام المتبقية': days_left,
                'الحالة': status,
                'ملاحظات': f'{"تحتاج تجديد" if days_left <= 30 else "سارية"}'
            })
        
        if vehicle.inspection_expiry_date:
            days_left = (vehicle.inspection_expiry_date - datetime.now().date()).days if vehicle.inspection_expiry_date else 0
            status = 'سارية' if days_left > 30 else 'تنتهي قريباً' if days_left > 0 else 'منتهية'
            documents_data.append({
                'نوع الوثيقة': 'الفحص الدوري',
                'تاريخ الانتهاء': vehicle.inspection_expiry_date.strftime('%Y-%m-%d'),
                'الأيام المتبقية': days_left,
                'الحالة': status,
                'ملاحظات': f'{"تحتاج تجديد" if days_left <= 30 else "سارية"}'
            })
        
        # إضافة الوثائق الخارجية إذا كانت متوفرة
        if documents:
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
            worksheet.set_column('A:Z', 18)
            
            # تنسيق العناوين
            for col_num, value in enumerate(documents_df.columns.values):
                worksheet.write(0, col_num, value, header_format)
            
            # تنسيق صفوف البيانات مع ألوان حسب الحالة
            for row_num in range(1, len(documents_data) + 1):
                for col_num in range(len(documents_df.columns)):
                    if col_num < len(documents_df.columns):
                        # تلوين الصفوف حسب حالة الوثيقة
                        if 'الحالة' in documents_df.columns:
                            status_col = documents_df.columns.get_loc('الحالة')
                            status = documents_df.iloc[row_num-1, status_col]
                            if status == 'منتهية':
                                row_format = workbook.add_format({'bg_color': '#FFCCCB', 'border': 1})
                            elif status == 'تنتهي قريباً':
                                row_format = workbook.add_format({'bg_color': '#FFE4B5', 'border': 1})
                            else:
                                row_format = workbook.add_format({'bg_color': '#98FB98', 'border': 1})
                            worksheet.write(row_num, col_num, documents_df.iloc[row_num-1, col_num], row_format)
                        else:
                            worksheet.write(row_num, col_num, documents_df.iloc[row_num-1, col_num], cell_format)
        
        # إضافة ملخص شامل للسيارة في ورقة منفصلة
        summary_data = []
        summary_data.append(['معلومات السيارة الأساسية', ''])
        summary_data.append(['رقم اللوحة', vehicle.plate_number or ''])
        summary_data.append(['الشركة المصنعة والطراز', f'{vehicle.make} {vehicle.model}'])
        summary_data.append(['سنة الصنع واللون', f'{vehicle.year} - {vehicle.color}'])
        summary_data.append(['الحالة الحالية', vehicle.status or ''])
        summary_data.append(['السائق المسؤول', vehicle.driver_name or 'غير محدد'])
        summary_data.append(['', ''])  # فاصل
        
        summary_data.append(['حالة الوثائق', ''])
        if vehicle.authorization_expiry_date:
            days_left = (vehicle.authorization_expiry_date - datetime.now().date()).days
            summary_data.append(['تفويض السيارة', f'{vehicle.authorization_expiry_date.strftime("%Y-%m-%d")} ({days_left} يوم متبقي)'])
        if vehicle.registration_expiry_date:
            days_left = (vehicle.registration_expiry_date - datetime.now().date()).days
            summary_data.append(['استمارة السيارة', f'{vehicle.registration_expiry_date.strftime("%Y-%m-%d")} ({days_left} يوم متبقي)'])
        if vehicle.inspection_expiry_date:
            days_left = (vehicle.inspection_expiry_date - datetime.now().date()).days
            summary_data.append(['الفحص الدوري', f'{vehicle.inspection_expiry_date.strftime("%Y-%m-%d")} ({days_left} يوم متبقي)'])
        summary_data.append(['', ''])  # فاصل
        
        summary_data.append(['الإحصائيات', ''])
        summary_data.append(['عدد عمليات الورش', workshop_count])
        summary_data.append(['إجمالي تكاليف الورش', f'{total_workshop_cost:.2f} ريال'])
        
        # إضافة إحصائيات تفصيلية للورش
        if workshop_records:
            completed_count = sum(1 for r in workshop_records if r.exit_date)
            ongoing_count = workshop_count - completed_count
            summary_data.append(['العمليات المكتملة', completed_count])
            summary_data.append(['العمليات الجارية', ongoing_count])
            
            # متوسط مدة البقاء في الورشة
            total_days = 0
            completed_operations = 0
            for record in workshop_records:
                if record.exit_date and record.entry_date:
                    total_days += (record.exit_date - record.entry_date).days
                    completed_operations += 1
            
            if completed_operations > 0:
                avg_duration = total_days / completed_operations
                summary_data.append(['متوسط مدة البقاء في الورشة', f'{avg_duration:.1f} يوم'])
            
            # أكثر الورش استخداماً
            workshop_usage = {}
            for record in workshop_records:
                workshop_name = record.workshop_name or 'غير محدد'
                workshop_usage[workshop_name] = workshop_usage.get(workshop_name, 0) + 1
            
            if workshop_usage:
                most_used_workshop = max(workshop_usage, key=workshop_usage.get)
                summary_data.append(['أكثر الورش استخداماً', f'{most_used_workshop} ({workshop_usage[most_used_workshop]} مرة)'])
        summary_data.append(['عدد سجلات التسليم/الاستلام', handover_count])
        summary_data.append(['عدد سجلات الفحص', inspection_count])
        summary_data.append(['', ''])  # فاصل
        
        summary_data.append(['معلومات النظام', ''])
        summary_data.append(['رابط Google Drive', vehicle.drive_folder_link or 'غير محدد'])
        summary_data.append(['الملاحظات', vehicle.notes or 'لا توجد ملاحظات'])
        summary_data.append(['تاريخ الإضافة', vehicle.created_at.strftime('%Y-%m-%d') if vehicle.created_at else ''])
        summary_data.append(['آخر تحديث', vehicle.updated_at.strftime('%Y-%m-%d') if vehicle.updated_at else ''])
        
        summary_df = pd.DataFrame(summary_data, columns=['البيان', 'القيمة'])
        summary_df.to_excel(writer, sheet_name='الملخص الشامل', index=False)
        
        # تنسيق ورقة الملخص
        worksheet = writer.sheets['الملخص الشامل']
        worksheet.right_to_left()
        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:B', 40)
        
        # تنسيق العناوين
        for col_num, value in enumerate(summary_df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # تنسيق صفوف البيانات
        for row_num in range(1, len(summary_data) + 1):
            for col_num in range(len(summary_df.columns)):
                if summary_data[row_num-1][0] in ['معلومات السيارة الأساسية', 'حالة الوثائق', 'الإحصائيات', 'معلومات النظام']:
                    # عناوين الأقسام
                    worksheet.write(row_num, col_num, summary_df.iloc[row_num-1, col_num], subheader_format)
                elif summary_data[row_num-1][0] == '':
                    # الفواصل
                    worksheet.write(row_num, col_num, '', cell_format)
                else:
                    # البيانات العادية
                    worksheet.write(row_num, col_num, summary_df.iloc[row_num-1, col_num], cell_format)
        
        # إضافة معلومات التقرير
        info_data = []
        info_data.append(['معلومات التقرير', ''])
        info_data.append(['تاريخ إنشاء التقرير', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
        info_data.append(['اسم النظام', 'نُظم - نظام إدارة المركبات المتكامل'])
        info_data.append(['نوع التقرير', 'تقرير شامل للسيارة'])
        info_data.append(['عدد الأوراق', f'{len(writer.sheets)} أوراق'])
        
        info_df = pd.DataFrame(info_data, columns=['البيان', 'القيمة'])
        info_df.to_excel(writer, sheet_name='معلومات التقرير', index=False)
        
        # تنسيق ورقة المعلومات
        worksheet = writer.sheets['معلومات التقرير']
        worksheet.right_to_left()
        worksheet.set_column('A:A', 25)
        worksheet.set_column('B:B', 35)
        
        # تنسيق العناوين
        for col_num, value in enumerate(info_df.columns.values):
            worksheet.write(0, col_num, value, header_format)
        
        # تنسيق صفوف البيانات
        for row_num in range(1, len(info_data) + 1):
            for col_num in range(len(info_df.columns)):
                if info_data[row_num-1][0] == 'معلومات التقرير':
                    worksheet.write(row_num, col_num, info_df.iloc[row_num-1, col_num], subheader_format)
                else:
                    worksheet.write(row_num, col_num, info_df.iloc[row_num-1, col_num], cell_format)
    
    # إرجاع محتوى الملف
    return output.getvalue()
