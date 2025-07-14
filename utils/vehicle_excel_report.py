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
            ['رقم اللوحة', vehicle.plate_number],
            ['الشركة المصنعة', vehicle.make],
            ['الطراز', vehicle.model],
            ['سنة الصنع', vehicle.year],
            ['اللون', vehicle.color],
            ['الحالة', vehicle.status],
            ['تاريخ الإضافة', vehicle.created_at.strftime('%Y-%m-%d') if vehicle.created_at else ''],
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
                    'حالة الإصلاح': record.repair_status or '',
                    'الملاحظات': record.notes or ''
                })
            
            if workshop_data:
                workshop_df = pd.DataFrame(workshop_data)
                workshop_df.to_excel(writer, sheet_name='سجلات الصيانة', index=False)
                
                # تنسيق ورقة الصيانة
                worksheet = writer.sheets['سجلات الصيانة']
                worksheet.right_to_left()
                worksheet.set_column('A:Z', 18)
                
                # تنسيق العناوين
                for col_num, value in enumerate(workshop_df.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                
                # تطبيق تنسيق على الأعمدة المناسبة
                for row_num in range(1, len(workshop_data) + 1):
                    # تنسيق عمود التكلفة
                    worksheet.write(row_num, 4, workshop_df.iloc[row_num-1, 4], number_format)  # التكلفة
        
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
                worksheet.set_column('A:Z', 18)
                
                # تنسيق العناوين
                for col_num, value in enumerate(documents_df.columns.values):
                    worksheet.write(0, col_num, value, header_format)
        
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
        worksheet.set_column('A:Z', 18)
        
        # تنسيق العناوين
        for col_num, value in enumerate(info_df.columns.values):
            worksheet.write(0, col_num, value, header_format)
    
    # إرجاع محتوى الملف
    return output.getvalue()
