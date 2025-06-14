"""
وظائف تصدير شاملة ومحسّنة للمركبات - Excel و PDF
"""

import io
import pandas as pd
from datetime import datetime
from flask import make_response

def export_all_vehicles_to_excel(vehicles):
    """
    تصدير جميع بيانات المركبات إلى ملف Excel بتنسيق محسّن
    
    Args:
        vehicles: قائمة كائنات المركبات
    
    Returns:
        Response object with Excel file
    """
    try:
        # إعداد البيانات
        vehicles_data = []
        
        for vehicle in vehicles:
            vehicle_dict = {
                'رقم اللوحة': vehicle.plate_number or '',
                'الماركة': vehicle.make or '',
                'الموديل': vehicle.model or '',
                'سنة الصنع': vehicle.year if vehicle.year else '',
                'اللون': vehicle.color or '',
                'اسم السائق': vehicle.current_driver or '',
                'الحالة': {
                    'available': 'متاحة',
                    'rented': 'مؤجرة',
                    'in_workshop': 'في الورشة',
                    'in_project': 'في المشروع',
                    'accident': 'حادث',
                    'sold': 'مباعة'
                }.get(vehicle.status, vehicle.status or 'غير محدد'),
                'تاريخ انتهاء الفحص الدوري': vehicle.periodic_inspection_expiry.strftime('%Y-%m-%d') if vehicle.periodic_inspection_expiry else '',
                'تاريخ انتهاء الاستمارة': vehicle.form_expiry.strftime('%Y-%m-%d') if vehicle.form_expiry else '',
                'ملاحظات': vehicle.notes or '',
                'تاريخ الإضافة': vehicle.created_at.strftime('%Y-%m-%d') if vehicle.created_at else ''
            }
            vehicles_data.append(vehicle_dict)
        
        # إنشاء DataFrame
        df = pd.DataFrame(vehicles_data)
        
        # إنشاء ملف Excel في الذاكرة
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='المركبات', index=False)
            
            # الحصول على ورقة العمل لتنسيقها
            worksheet = writer.sheets['المركبات']
            
            # تعديل عرض الأعمدة
            for column in worksheet.columns:
                max_length = 0
                column_letter = column[0].column_letter
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(str(cell.value))
                    except:
                        pass
                adjusted_width = min(max_length + 2, 50)
                worksheet.column_dimensions[column_letter].width = adjusted_width
        
        output.seek(0)
        
        # إنشاء الاستجابة
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"vehicles_export_{timestamp}.xlsx"
        
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f'attachment; filename*=UTF-8\'\'{filename}'
        
        return response
        
    except Exception as e:
        print(f"خطأ في تصدير Excel: {str(e)}")
        return None


def export_vehicle_details_excel(vehicle):
    """
    تصدير تفاصيل مركبة واحدة إلى Excel
    
    Args:
        vehicle: كائن المركبة
    
    Returns:
        Response object with Excel file
    """
    try:
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # بيانات المركبة الأساسية
            basic_data = {
                'البيان': [
                    'رقم اللوحة',
                    'الماركة', 
                    'الموديل',
                    'سنة الصنع',
                    'اللون',
                    'السائق الحالي',
                    'الحالة',
                    'رقم المحرك',
                    'رقم الهيكل',
                    'نوع الوقود',
                    'المسافة المقطوعة',
                    'تاريخ انتهاء الفحص الدوري',
                    'تاريخ انتهاء الاستمارة',
                    'الملاحظات',
                    'تاريخ الإضافة'
                ],
                'القيمة': [
                    vehicle.plate_number or '',
                    vehicle.make or '',
                    vehicle.model or '',
                    str(vehicle.year) if vehicle.year else '',
                    vehicle.color or '',
                    vehicle.current_driver or '',
                    {
                        'available': 'متاحة',
                        'rented': 'مؤجرة',
                        'in_workshop': 'في الورشة',
                        'in_project': 'في المشروع',
                        'accident': 'حادث',
                        'sold': 'مباعة'
                    }.get(vehicle.status, vehicle.status or ''),
                    vehicle.engine_number or '',
                    vehicle.chassis_number or '',
                    vehicle.fuel_type or '',
                    str(vehicle.mileage) if vehicle.mileage else '0',
                    vehicle.periodic_inspection_expiry.strftime('%Y-%m-%d') if vehicle.periodic_inspection_expiry else '',
                    vehicle.form_expiry.strftime('%Y-%m-%d') if vehicle.form_expiry else '',
                    vehicle.notes or '',
                    vehicle.created_at.strftime('%Y-%m-%d') if vehicle.created_at else ''
                ]
            }
            
            df_basic = pd.DataFrame(basic_data)
            df_basic.to_excel(writer, sheet_name='بيانات المركبة', index=False)
            
            # تنسيق ورقة البيانات الأساسية
            worksheet = writer.sheets['بيانات المركبة']
            worksheet.column_dimensions['A'].width = 25
            worksheet.column_dimensions['B'].width = 35
        
        output.seek(0)
        
        # إنشاء اسم الملف
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"vehicle_{vehicle.plate_number}_{timestamp}.xlsx"
        filename = filename.replace('/', '_').replace('\\', '_')  # تنظيف اسم الملف
        
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        response.headers['Content-Disposition'] = f'attachment; filename*=UTF-8\'\'{filename}'
        
        return response
        
    except Exception as e:
        print(f"خطأ في تصدير تفاصيل المركبة: {str(e)}")
        return None