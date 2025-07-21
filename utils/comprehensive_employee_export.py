import pandas as pd
from io import BytesIO
from datetime import datetime, date
import os

def export_comprehensive_employee_data(employees):
    """
    تصدير شامل لبيانات الموظفين مع جميع التفاصيل
    يشمل: البيانات الأساسية، المعلومات البنكية، العُهد، الوثائق، الرواتب، الحضور
    """
    
    # قائمة لحفظ بيانات الموظفين
    employees_data = []
    
    for employee in employees:
        # البيانات الأساسية
        base_data = {
            'رقم الموظف': employee.employee_id or '',
            'الاسم': employee.name or '',
            'الرقم الوطني/الإقامة': employee.national_id or '',
            'رقم الهاتف': employee.phone or '',
            'رقم الهاتف الثاني': getattr(employee, 'mobilePersonal', '') or '',
            'البريد الإلكتروني': employee.email or '',
            'المنصب/الوظيفة': employee.job_title or '',
            'الحالة الوظيفية': employee.status or '',
            'الموقع': employee.location or '',
            'المشروع': employee.project or '',
            'تاريخ الانضمام': employee.join_date.strftime('%Y-%m-%d') if employee.join_date else '',
            'تاريخ الميلاد': employee.birth_date.strftime('%Y-%m-%d') if employee.birth_date else '',
            'الجنسية': employee.nationality or '',
            'نوع العقد': 'سعودي' if employee.contract_type == 'saudi' else 'وافد',
            'الراتب الأساسي': employee.basic_salary or 0,
            'حالة العقد': employee.contract_status or '',
            'حالة الرخصة': employee.license_status or '',
            'ملاحظات': employee.notes or '',
            'تاريخ الإنشاء': employee.created_at.strftime('%Y-%m-%d %H:%M') if employee.created_at else '',
            'تاريخ آخر تحديث': employee.updated_at.strftime('%Y-%m-%d %H:%M') if employee.updated_at else '',
        }
        
        # معلومات الأقسام
        departments_list = []
        if employee.departments:
            departments_list = [dept.name for dept in employee.departments]
        base_data['الأقسام'] = ' | '.join(departments_list) if departments_list else 'بدون قسم'
        base_data['عدد الأقسام'] = len(departments_list)
        
        # معلومات الجنسية المفصلة
        if employee.nationality_rel:
            base_data['الجنسية التفصيلية'] = employee.nationality_rel.name_ar
            base_data['رمز الجنسية'] = employee.nationality_rel.code
        
        # معلومات نوع الموظف والعُهد
        base_data['نوع الموظف'] = 'سائق' if employee.employee_type == 'driver' else 'عادي'
        base_data['لديه عهدة جوال'] = 'نعم' if employee.has_mobile_custody else 'لا'
        base_data['نوع الجوال'] = employee.mobile_type or ''
        base_data['رقم IMEI'] = employee.mobile_imei or ''
        
        # معلومات الكفالة
        base_data['حالة الكفالة'] = 'على الكفالة' if employee.sponsorship_status == 'inside' else 'خارج الكفالة'
        base_data['اسم الكفيل الحالي'] = employee.current_sponsor_name or ''
        
        # المعلومات البنكية
        base_data['رقم الإيبان'] = employee.bank_iban or ''
        base_data['لديه صورة إيبان'] = 'نعم' if employee.bank_iban_image else 'لا'
        
        # معلومات الصور
        base_data['لديه صورة شخصية'] = 'نعم' if employee.profile_image else 'لا'
        base_data['لديه صورة هوية'] = 'نعم' if employee.national_id_image else 'لا'
        base_data['لديه صورة رخصة'] = 'نعم' if employee.license_image else 'لا'
        
        # إحصائيات الوثائق
        documents_count = len(employee.documents) if employee.documents else 0
        base_data['عدد الوثائق'] = documents_count
        
        # تفاصيل الوثائق
        if employee.documents:
            doc_types = []
            expired_docs = 0
            valid_docs = 0
            
            for doc in employee.documents:
                doc_types.append(doc.document_type)
                if doc.expiry_date:
                    if doc.expiry_date < date.today():
                        expired_docs += 1
                    else:
                        valid_docs += 1
            
            base_data['أنواع الوثائق'] = ' | '.join(set(doc_types))
            base_data['الوثائق المنتهية'] = expired_docs
            base_data['الوثائق السارية'] = valid_docs
        else:
            base_data['أنواع الوثائق'] = ''
            base_data['الوثائق المنتهية'] = 0
            base_data['الوثائق السارية'] = 0
        
        # إحصائيات الرواتب
        salaries_count = len(employee.salaries) if employee.salaries else 0
        base_data['عدد الرواتب المسجلة'] = salaries_count
        
        if employee.salaries:
            # حساب متوسط الراتب
            total_basic = sum(s.basic_salary for s in employee.salaries if s.basic_salary)
            total_net = sum(s.net_salary for s in employee.salaries if s.net_salary)
            total_allowances = sum(s.allowances for s in employee.salaries if s.allowances)
            total_deductions = sum(s.deductions for s in employee.salaries if s.deductions)
            
            base_data['متوسط الراتب الأساسي'] = round(total_basic / salaries_count, 2) if salaries_count > 0 else 0
            base_data['متوسط صافي الراتب'] = round(total_net / salaries_count, 2) if salaries_count > 0 else 0
            base_data['متوسط البدلات'] = round(total_allowances / salaries_count, 2) if salaries_count > 0 else 0
            base_data['متوسط الخصومات'] = round(total_deductions / salaries_count, 2) if salaries_count > 0 else 0
            
            # آخر راتب
            latest_salary = max(employee.salaries, key=lambda s: (s.year, s.month))
            base_data['آخر راتب - الشهر'] = latest_salary.month
            base_data['آخر راتب - السنة'] = latest_salary.year
            base_data['آخر راتب - الأساسي'] = latest_salary.basic_salary or 0
            base_data['آخر راتب - صافي'] = latest_salary.net_salary or 0
            base_data['آخر راتب - البدلات'] = latest_salary.allowances or 0
            base_data['آخر راتب - الخصومات'] = latest_salary.deductions or 0
            base_data['آخر راتب - مدفوع'] = 'نعم' if latest_salary.is_paid else 'لا'
            
            # أعلى وأدنى راتب
            max_salary = max(s.net_salary for s in employee.salaries if s.net_salary)
            min_salary = min(s.net_salary for s in employee.salaries if s.net_salary)
            base_data['أعلى راتب'] = max_salary
            base_data['أدنى راتب'] = min_salary
        else:
            # قيم افتراضية للرواتب
            base_data.update({
                'متوسط الراتب الأساسي': 0,
                'متوسط صافي الراتب': 0,
                'متوسط البدلات': 0,
                'متوسط الخصومات': 0,
                'آخر راتب - الشهر': '',
                'آخر راتب - السنة': '',
                'آخر راتب - الأساسي': 0,
                'آخر راتب - صافي': 0,
                'آخر راتب - البدلات': 0,
                'آخر راتب - الخصومات': 0,
                'آخر راتب - مدفوع': '',
                'أعلى راتب': 0,
                'أدنى راتب': 0
            })
        
        # إحصائيات الحضور
        attendances_count = len(employee.attendances) if employee.attendances else 0
        base_data['عدد سجلات الحضور'] = attendances_count
        
        if employee.attendances:
            present_count = len([a for a in employee.attendances if a.status == 'present'])
            absent_count = len([a for a in employee.attendances if a.status == 'absent'])
            leave_count = len([a for a in employee.attendances if a.status == 'leave'])
            
            base_data['أيام الحضور'] = present_count
            base_data['أيام الغياب'] = absent_count
            base_data['أيام الإجازة'] = leave_count
            base_data['نسبة الحضور %'] = round((present_count / attendances_count) * 100, 2) if attendances_count > 0 else 0
        else:
            base_data.update({
                'أيام الحضور': 0,
                'أيام الغياب': 0,
                'أيام الإجازة': 0,
                'نسبة الحضور %': 0
            })
        
        # إضافة البيانات للقائمة
        employees_data.append(base_data)
    
    # إنشاء DataFrame
    df = pd.DataFrame(employees_data)
    
    # ترتيب الأعمدة بشكل منطقي
    column_order = [
        'رقم الموظف', 'الاسم', 'الرقم الوطني/الإقامة', 'رقم الهاتف', 'رقم الهاتف الثاني',
        'البريد الإلكتروني', 'المنصب/الوظيفة', 'الحالة الوظيفية', 'الأقسام', 'عدد الأقسام',
        'الموقع', 'المشروع', 'تاريخ الانضمام', 'تاريخ الميلاد', 'الجنسية', 'الجنسية التفصيلية',
        'رمز الجنسية', 'نوع العقد', 'الراتب الأساسي', 'حالة العقد', 'حالة الرخصة',
        'نوع الموظف', 'لديه عهدة جوال', 'نوع الجوال', 'رقم IMEI',
        'حالة الكفالة', 'اسم الكفيل الحالي', 'رقم الإيبان', 'لديه صورة إيبان',
        'لديه صورة شخصية', 'لديه صورة هوية', 'لديه صورة رخصة',
        'عدد الوثائق', 'أنواع الوثائق', 'الوثائق السارية', 'الوثائق المنتهية',
        'عدد الرواتب المسجلة', 'متوسط الراتب الأساسي', 'متوسط صافي الراتب', 
        'متوسط البدلات', 'متوسط الخصومات', 'أعلى راتب', 'أدنى راتب',
        'آخر راتب - الشهر', 'آخر راتب - السنة', 'آخر راتب - الأساسي', 
        'آخر راتب - صافي', 'آخر راتب - البدلات', 'آخر راتب - الخصومات', 'آخر راتب - مدفوع',
        'عدد سجلات الحضور', 'أيام الحضور', 'أيام الغياب', 'أيام الإجازة', 'نسبة الحضور %',
        'ملاحظات', 'تاريخ الإنشاء', 'تاريخ آخر تحديث'
    ]
    
    # إعادة ترتيب الأعمدة
    available_columns = [col for col in column_order if col in df.columns]
    df = df[available_columns]
    
    return df

def generate_comprehensive_employee_excel(employees):
    """إنشاء ملف Excel شامل لبيانات الموظفين"""
    
    # الحصول على البيانات الشاملة
    df = export_comprehensive_employee_data(employees)
    
    # إنشاء BytesIO للإخراج
    output = BytesIO()
    
    # إنشاء ملف Excel مع تنسيقات
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # كتابة البيانات الأساسية
        df.to_excel(writer, sheet_name='البيانات الشاملة', index=False, engine='openpyxl')
        
        # الحصول على الورقة لتطبيق التنسيقات
        worksheet = writer.sheets['البيانات الشاملة']
        
        # تطبيق عرض تلقائي للأعمدة
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)  # حد أقصى 50 حرف
            worksheet.column_dimensions[column_letter].width = adjusted_width
        
        # تجميد الصف الأول
        worksheet.freeze_panes = 'A2'
        
        # إضافة ورقة إحصائيات موجزة
        summary_data = generate_summary_statistics(employees)
        summary_df = pd.DataFrame(list(summary_data.items()), columns=['المقياس', 'القيمة'])
        summary_df.to_excel(writer, sheet_name='الإحصائيات', index=False)
    
    output.seek(0)
    return output

def generate_summary_statistics(employees):
    """إنشاء إحصائيات موجزة للموظفين"""
    
    total_employees = len(employees)
    active_employees = len([e for e in employees if e.status == 'active'])
    inactive_employees = len([e for e in employees if e.status == 'inactive'])
    
    # إحصائيات العُهد
    mobile_custody_count = len([e for e in employees if e.has_mobile_custody])
    
    # إحصائيات الكفالة
    inside_sponsorship = len([e for e in employees if e.sponsorship_status == 'inside'])
    outside_sponsorship = len([e for e in employees if e.sponsorship_status == 'outside'])
    
    # إحصائيات الجنسية
    saudi_count = len([e for e in employees if e.contract_type == 'saudi'])
    foreign_count = len([e for e in employees if e.contract_type == 'foreign'])
    
    # إحصائيات نوع الموظف
    driver_count = len([e for e in employees if e.employee_type == 'driver'])
    regular_count = len([e for e in employees if e.employee_type == 'regular'])
    
    # إحصائيات الصور
    with_profile_image = len([e for e in employees if e.profile_image])
    with_id_image = len([e for e in employees if e.national_id_image])
    with_license_image = len([e for e in employees if e.license_image])
    with_iban_image = len([e for e in employees if e.bank_iban_image])
    
    # إحصائيات المعلومات البنكية
    with_iban = len([e for e in employees if e.bank_iban])
    
    return {
        'إجمالي الموظفين': total_employees,
        'الموظفون النشطون': active_employees,
        'الموظفون غير النشطين': inactive_employees,
        'نسبة النشطين %': round((active_employees / total_employees) * 100, 2) if total_employees > 0 else 0,
        '',
        'الموظفون السعوديون': saudi_count,
        'الموظفون الوافدون': foreign_count,
        'نسبة السعوديين %': round((saudi_count / total_employees) * 100, 2) if total_employees > 0 else 0,
        ' ',
        'السائقون': driver_count,
        'الموظفون العاديون': regular_count,
        'نسبة السائقين %': round((driver_count / total_employees) * 100, 2) if total_employees > 0 else 0,
        '  ',
        'لديهم عهدة جوال': mobile_custody_count,
        'نسبة العُهد %': round((mobile_custody_count / total_employees) * 100, 2) if total_employees > 0 else 0,
        '   ',
        'على الكفالة': inside_sponsorship,
        'خارج الكفالة': outside_sponsorship,
        'نسبة على الكفالة %': round((inside_sponsorship / total_employees) * 100, 2) if total_employees > 0 else 0,
        '    ',
        'لديهم صورة شخصية': with_profile_image,
        'لديهم صورة هوية': with_id_image,
        'لديهم صورة رخصة': with_license_image,
        'لديهم صورة إيبان': with_iban_image,
        'لديهم رقم إيبان': with_iban,
        '     ',
        'نسبة اكتمال الصور الشخصية %': round((with_profile_image / total_employees) * 100, 2) if total_employees > 0 else 0,
        'نسبة اكتمال صور الهوية %': round((with_id_image / total_employees) * 100, 2) if total_employees > 0 else 0,
        'نسبة اكتمال المعلومات البنكية %': round((with_iban / total_employees) * 100, 2) if total_employees > 0 else 0,
        'تاريخ التصدير': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }