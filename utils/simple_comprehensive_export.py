from datetime import date, datetime
from io import BytesIO
import pandas as pd

def generate_comprehensive_employee_excel(employees):
    """إنشاء ملف Excel شامل لبيانات الموظفين مع جميع التفاصيل - نسخة مبسطة"""
    try:
        # قائمة البيانات الشاملة
        comprehensive_data = []
        
        for employee in employees:
            try:
                # البيانات الأساسية - مع حماية من الأخطاء
                row_data = {}
                
                # معلومات أساسية آمنة
                row_data['رقم الموظف'] = getattr(employee, 'employee_id', '') or ''
                row_data['الاسم'] = getattr(employee, 'name', '') or ''
                row_data['رقم الهوية'] = getattr(employee, 'national_id', '') or ''
                row_data['رقم الجوال الأول'] = getattr(employee, 'mobile', '') or ''
                row_data['رقم الجوال الثاني'] = getattr(employee, 'mobile2', '') or ''
                row_data['الإيميل'] = getattr(employee, 'email', '') or ''
                row_data['المنصب'] = getattr(employee, 'position', '') or ''
                row_data['الحالة الوظيفية'] = getattr(employee, 'status', '') or ''
                row_data['الموقع'] = getattr(employee, 'location', '') or ''
                row_data['المشروع'] = getattr(employee, 'project', '') or ''
                row_data['الجنسية'] = getattr(employee, 'nationality', '') or ''
                row_data['نوع العقد'] = 'سعودي' if getattr(employee, 'contract_type', '') == 'saudi' else 'وافد'
                row_data['الراتب الأساسي'] = getattr(employee, 'basic_salary', 0) or 0
                row_data['حالة العقد'] = getattr(employee, 'contract_status', '') or ''
                row_data['حالة الرخصة'] = getattr(employee, 'license_status', '') or ''
                row_data['ملاحظات'] = getattr(employee, 'notes', '') or ''
                
                # التواريخ مع حماية
                join_date = getattr(employee, 'join_date', None)
                row_data['تاريخ الانضمام'] = join_date.strftime('%Y-%m-%d') if join_date else ''
                
                birth_date = getattr(employee, 'birth_date', None)
                row_data['تاريخ الميلاد'] = birth_date.strftime('%Y-%m-%d') if birth_date else ''
                
                created_at = getattr(employee, 'created_at', None)
                row_data['تاريخ الإنشاء'] = created_at.strftime('%Y-%m-%d %H:%M') if created_at else ''
                
                updated_at = getattr(employee, 'updated_at', None)
                row_data['تاريخ آخر تحديث'] = updated_at.strftime('%Y-%m-%d %H:%M') if updated_at else ''
                
                # معلومات الأقسام - مع حماية من الأخطاء
                departments_list = []
                try:
                    if hasattr(employee, 'departments') and employee.departments:
                        for dept in employee.departments:
                            dept_name = getattr(dept, 'name', 'غير محدد')
                            if dept_name:
                                departments_list.append(str(dept_name))
                except:
                    pass
                
                row_data['الأقسام'] = ' | '.join(departments_list) if departments_list else 'بدون قسم'
                row_data['عدد الأقسام'] = len(departments_list)
                
                # معلومات الجنسية المفصلة - مع حماية
                try:
                    if hasattr(employee, 'nationality_rel') and employee.nationality_rel:
                        nationality_name = getattr(employee.nationality_rel, 'name_ar', '')
                        nationality_code = getattr(employee.nationality_rel, 'code', '')
                        row_data['الجنسية التفصيلية'] = nationality_name or ''
                        row_data['رمز الجنسية'] = nationality_code or ''
                    else:
                        row_data['الجنسية التفصيلية'] = ''
                        row_data['رمز الجنسية'] = ''
                except:
                    row_data['الجنسية التفصيلية'] = ''
                    row_data['رمز الجنسية'] = ''
                
                # معلومات نوع الموظف والعُهد
                row_data['نوع الموظف'] = 'سائق' if getattr(employee, 'employee_type', '') == 'driver' else 'عادي'
                row_data['لديه عهدة جوال'] = 'نعم' if getattr(employee, 'has_mobile_custody', False) else 'لا'
                row_data['نوع الجوال'] = getattr(employee, 'mobile_type', '') or ''
                row_data['رقم IMEI'] = getattr(employee, 'mobile_imei', '') or ''
                
                # معلومات الكفالة
                sponsorship_status = getattr(employee, 'sponsorship_status', '')
                row_data['حالة الكفالة'] = 'على الكفالة' if sponsorship_status == 'inside' else 'خارج الكفالة'
                row_data['اسم الكفيل الحالي'] = getattr(employee, 'current_sponsor_name', '') or ''
                
                # المعلومات البنكية
                row_data['رقم الإيبان'] = getattr(employee, 'bank_iban', '') or ''
                row_data['لديه صورة إيبان'] = 'نعم' if getattr(employee, 'bank_iban_image', '') else 'لا'
                
                # معلومات الصور
                row_data['لديه صورة شخصية'] = 'نعم' if getattr(employee, 'profile_image', '') else 'لا'
                row_data['لديه صورة هوية'] = 'نعم' if getattr(employee, 'national_id_image', '') else 'لا'
                row_data['لديه صورة رخصة'] = 'نعم' if getattr(employee, 'license_image', '') else 'لا'
                
                # إحصائيات الوثائق - مع حماية
                documents_count = 0
                expired_docs = 0
                valid_docs = 0
                doc_types_list = []
                
                try:
                    if hasattr(employee, 'documents') and employee.documents:
                        documents_count = len(employee.documents)
                        for doc in employee.documents:
                            doc_type = getattr(doc, 'document_type', '')
                            if doc_type:
                                doc_types_list.append(str(doc_type))
                            
                            expiry_date = getattr(doc, 'expiry_date', None)
                            if expiry_date:
                                if expiry_date < date.today():
                                    expired_docs += 1
                                else:
                                    valid_docs += 1
                except:
                    pass
                
                row_data['عدد الوثائق'] = documents_count
                row_data['أنواع الوثائق'] = ' | '.join(set(doc_types_list)) if doc_types_list else ''
                row_data['الوثائق المنتهية'] = expired_docs
                row_data['الوثائق السارية'] = valid_docs
                
                # إحصائيات الرواتب - مع حماية
                salary_count = 0
                total_salaries = 0
                max_salary = 0
                min_salary = 0
                avg_salary = 0
                
                try:
                    if hasattr(employee, 'salaries') and employee.salaries:
                        salary_amounts = []
                        for salary in employee.salaries:
                            total_salary = getattr(salary, 'total_salary', 0)
                            if total_salary and total_salary > 0:
                                salary_amounts.append(float(total_salary))
                        
                        if salary_amounts:
                            salary_count = len(salary_amounts)
                            total_salaries = sum(salary_amounts)
                            max_salary = max(salary_amounts)
                            min_salary = min(salary_amounts)
                            avg_salary = round(total_salaries / salary_count, 2)
                except:
                    pass
                
                row_data['عدد سجلات الراتب'] = salary_count
                row_data['متوسط الراتب'] = avg_salary
                row_data['أعلى راتب'] = max_salary
                row_data['أدنى راتب'] = min_salary
                
                # إحصائيات الحضور - مع حماية
                attendance_count = 0
                present_days = 0
                absent_days = 0
                attendance_percentage = 0
                
                try:
                    if hasattr(employee, 'attendances') and employee.attendances:
                        attendance_count = len(employee.attendances)
                        for attendance in employee.attendances:
                            status = getattr(attendance, 'status', '')
                            if status == 'present':
                                present_days += 1
                            elif status == 'absent':
                                absent_days += 1
                        
                        if attendance_count > 0:
                            attendance_percentage = round((present_days / attendance_count) * 100, 2)
                except:
                    pass
                
                row_data['عدد سجلات الحضور'] = attendance_count
                row_data['أيام الحضور'] = present_days
                row_data['أيام الغياب'] = absent_days
                row_data['نسبة الحضور'] = attendance_percentage
                
                comprehensive_data.append(row_data)
                
            except Exception as e:
                # تسجيل الخطأ وتجاهل هذا الموظف
                print(f"خطأ في معالجة بيانات موظف: {str(e)}")
                continue
        
        # تحويل البيانات إلى DataFrame
        if not comprehensive_data:
            # إنشاء DataFrame فارغ
            df = pd.DataFrame([{'رسالة': 'لا توجد بيانات متاحة للتصدير'}])
        else:
            df = pd.DataFrame(comprehensive_data)
        
        # إنشاء ملف Excel في الذاكرة
        output = BytesIO()
        
        # استخدام pandas ExcelWriter
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # كتابة البيانات الشاملة
            df.to_excel(writer, sheet_name='البيانات الشاملة', index=False)
            
            # إنشاء ورقة الإحصائيات العامة إذا كان هناك بيانات
            if comprehensive_data:
                stats_data = calculate_general_statistics(employees)
                stats_df = pd.DataFrame(list(stats_data.items()), columns=['البيان', 'القيمة'])
                stats_df.to_excel(writer, sheet_name='الإحصائيات العامة', index=False)
        
        output.seek(0)
        return output
        
    except Exception as e:
        print(f"خطأ في إنشاء ملف Excel: {str(e)}")
        raise Exception(f"Error generating Excel file: {str(e)}")

def calculate_general_statistics(employees):
    """حساب الإحصائيات العامة للموظفين"""
    total_employees = len(employees)
    if total_employees == 0:
        return {'إجمالي الموظفين': 0}
    
    try:
        # إحصائيات أساسية
        active_employees = len([e for e in employees if getattr(e, 'status', '') == 'active'])
        inactive_employees = total_employees - active_employees
        
        # إحصائيات العُهد
        mobile_custody_count = len([e for e in employees if getattr(e, 'has_mobile_custody', False)])
        
        # إحصائيات الكفالة  
        inside_sponsorship = len([e for e in employees if getattr(e, 'sponsorship_status', '') == 'inside'])
        outside_sponsorship = len([e for e in employees if getattr(e, 'sponsorship_status', '') == 'outside'])
        
        # إحصائيات الجنسية
        saudi_count = len([e for e in employees if getattr(e, 'contract_type', '') == 'saudi'])
        foreign_count = len([e for e in employees if getattr(e, 'contract_type', '') == 'foreign'])
        
        # إحصائيات نوع الموظف
        driver_count = len([e for e in employees if getattr(e, 'employee_type', '') == 'driver'])
        regular_count = len([e for e in employees if getattr(e, 'employee_type', '') == 'regular'])
        
        # إحصائيات الصور
        with_profile_image = len([e for e in employees if getattr(e, 'profile_image', '')])
        with_id_image = len([e for e in employees if getattr(e, 'national_id_image', '')])
        with_license_image = len([e for e in employees if getattr(e, 'license_image', '')])
        with_iban_image = len([e for e in employees if getattr(e, 'bank_iban_image', '')])
        with_iban = len([e for e in employees if getattr(e, 'bank_iban', '')])
        
        return {
            'إجمالي الموظفين': total_employees,
            'الموظفون النشطون': active_employees,
            'الموظفون غير النشطين': inactive_employees,
            'نسبة النشطين %': round((active_employees / total_employees) * 100, 2),
            'الموظفون السعوديون': saudi_count,
            'الموظفون الوافدون': foreign_count,
            'نسبة السعوديين %': round((saudi_count / total_employees) * 100, 2),
            'السائقون': driver_count,
            'الموظفون العاديون': regular_count,
            'نسبة السائقين %': round((driver_count / total_employees) * 100, 2),
            'لديهم عهدة جوال': mobile_custody_count,
            'نسبة العُهد %': round((mobile_custody_count / total_employees) * 100, 2),
            'على الكفالة': inside_sponsorship,
            'خارج الكفالة': outside_sponsorship,
            'نسبة على الكفالة %': round((inside_sponsorship / total_employees) * 100, 2),
            'لديهم صورة شخصية': with_profile_image,
            'لديهم صورة هوية': with_id_image,
            'لديهم صورة رخصة': with_license_image,
            'لديهم صورة إيبان': with_iban_image,
            'لديهم رقم إيبان': with_iban,
            'نسبة اكتمال الصور الشخصية %': round((with_profile_image / total_employees) * 100, 2),
            'نسبة اكتمال صور الهوية %': round((with_id_image / total_employees) * 100, 2),
            'نسبة اكتمال المعلومات البنكية %': round((with_iban / total_employees) * 100, 2),
            'تاريخ التصدير': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    except Exception as e:
        print(f"خطأ في حساب الإحصائيات: {str(e)}")
        return {
            'إجمالي الموظفين': total_employees,
            'حالة': f'خطأ في حساب الإحصائيات: {str(e)}',
            'تاريخ التصدير': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }