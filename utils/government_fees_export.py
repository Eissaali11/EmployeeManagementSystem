import os
import io
import xlsxwriter
from datetime import datetime
from flask import send_file
from models import GovernmentFee, Employee, Department, Document
from sqlalchemy import func, extract
from app import db

def export_government_fees_data(fee_type=None, payment_status=None, department_id=None, year=None, month=None):
    """
    تصدير بيانات الرسوم الحكومية إلى ملف Excel
    
    Args:
        fee_type (str): نوع الرسوم للتصفية
        payment_status (str): حالة السداد للتصفية
        department_id (int): معرف القسم للتصفية
        year (int): السنة للتصفية
        month (int): الشهر للتصفية
        
    Returns:
        io.BytesIO: تيار بايت يحتوي على ملف Excel
    """
    # إنشاء استعلام قاعدة البيانات
    query = GovernmentFee.query.join(Employee)
    
    # تطبيق عوامل التصفية
    if fee_type:
        query = query.filter(GovernmentFee.fee_type == fee_type)
    
    if payment_status:
        query = query.filter(GovernmentFee.payment_status == payment_status)
    
    if department_id:
        query = query.filter(Employee.department_id == department_id)
    
    if year:
        query = query.filter(extract('year', GovernmentFee.fee_date) == year)
    
    if month:
        query = query.filter(extract('month', GovernmentFee.fee_date) == month)
    
    # الحصول على البيانات
    fees = query.order_by(GovernmentFee.fee_date.desc()).all()
    
    # إنشاء ملف Excel في الذاكرة
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet('الرسوم الحكومية')
    
    # تعريف الأنماط
    header_format = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'center',
        'valign': 'vcenter',
        'bg_color': '#0d6efd',
        'color': 'white',
        'border': 1
    })
    
    cell_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
        'border': 1
    })
    
    money_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
        'border': 1,
        'num_format': '#,##0.00 ريال'
    })
    
    date_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
        'border': 1,
        'num_format': 'yyyy-mm-dd'
    })
    
    # تعيين عرض الأعمدة
    worksheet.set_column('A:A', 5)  # رقم متسلسل
    worksheet.set_column('B:B', 25)  # اسم الموظف
    worksheet.set_column('C:C', 15)  # الرقم الوظيفي
    worksheet.set_column('D:D', 20)  # القسم
    worksheet.set_column('E:E', 15)  # نوع العقد
    worksheet.set_column('F:F', 15)  # نوع الرسوم
    worksheet.set_column('G:G', 15)  # تاريخ الاستحقاق
    worksheet.set_column('H:H', 15)  # تاريخ انتهاء المهلة
    worksheet.set_column('I:I', 15)  # المبلغ
    worksheet.set_column('J:J', 15)  # حالة السداد
    worksheet.set_column('K:K', 15)  # تاريخ السداد
    worksheet.set_column('L:L', 25)  # ملاحظات
    
    # إضافة عنوان
    title_format = workbook.add_format({
        'bold': True,
        'font_size': 18,
        'align': 'center',
        'valign': 'vcenter'
    })
    worksheet.merge_range('A1:L1', 'تقرير الرسوم الحكومية', title_format)
    
    # إضافة تاريخ التقرير
    date_title_format = workbook.add_format({
        'italic': True,
        'align': 'center',
        'valign': 'vcenter'
    })
    worksheet.merge_range('A2:L2', f'تاريخ التقرير: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', date_title_format)
    
    # عناوين الأعمدة
    headers = [
        '#',
        'اسم الموظف',
        'الرقم الوظيفي',
        'القسم',
        'نوع العقد',
        'نوع الرسوم',
        'تاريخ الاستحقاق',
        'تاريخ انتهاء المهلة',
        'المبلغ',
        'حالة السداد',
        'تاريخ السداد',
        'ملاحظات'
    ]
    
    # كتابة عناوين الأعمدة
    for col, header in enumerate(headers):
        worksheet.write(3, col, header, header_format)
    
    # قواميس لتحويل القيم
    fee_types = {
        'passport': 'الجوازات',
        'labor_office': 'مكتب العمل',
        'insurance': 'التأمين الطبي',
        'social_insurance': 'التأمينات الاجتماعية',
        'transfer_sponsorship': 'نقل كفالة',
        'other': 'رسوم أخرى'
    }
    
    payment_statuses = {
        'pending': 'قيد الانتظار',
        'paid': 'مدفوع',
        'overdue': 'متأخر'
    }
    
    contract_types = {
        'saudi': 'سعودي',
        'foreign': 'وافد'
    }
    
    # كتابة بيانات الرسوم
    total_amount = 0
    for i, fee in enumerate(fees):
        row = i + 4  # البدء من الصف 4 (بعد العناوين)
        
        # الحصول على معلومات الموظف والقسم
        employee = fee.employee
        department_name = employee.department.name if employee.department else 'غير محدد'
        contract_type = contract_types.get(employee.contract_type, 'غير محدد')
        
        # حساب إجمالي المبلغ
        total_amount += fee.amount
        
        # كتابة بيانات الصف
        worksheet.write(row, 0, i + 1, cell_format)  # رقم متسلسل
        worksheet.write(row, 1, employee.name, cell_format)  # اسم الموظف
        worksheet.write(row, 2, employee.employee_id, cell_format)  # الرقم الوظيفي
        worksheet.write(row, 3, department_name, cell_format)  # القسم
        worksheet.write(row, 4, contract_type, cell_format)  # نوع العقد
        worksheet.write(row, 5, fee_types.get(fee.fee_type, fee.fee_type), cell_format)  # نوع الرسوم
        worksheet.write(row, 6, fee.fee_date, date_format)  # تاريخ الاستحقاق
        worksheet.write(row, 7, fee.due_date, date_format)  # تاريخ انتهاء المهلة
        worksheet.write(row, 8, fee.amount, money_format)  # المبلغ
        worksheet.write(row, 9, payment_statuses.get(fee.payment_status, fee.payment_status), cell_format)  # حالة السداد
        worksheet.write(row, 10, fee.payment_date or '', date_format)  # تاريخ السداد
        worksheet.write(row, 11, fee.notes or '', cell_format)  # ملاحظات
    
    # إضافة صف للإجمالي
    total_row = len(fees) + 4
    total_format = workbook.add_format({
        'bold': True,
        'align': 'center',
        'valign': 'vcenter',
        'bg_color': '#f8f9fa',
        'border': 1
    })
    
    total_money_format = workbook.add_format({
        'bold': True,
        'align': 'center',
        'valign': 'vcenter',
        'bg_color': '#f8f9fa',
        'border': 1,
        'num_format': '#,##0.00 ريال'
    })
    
    worksheet.merge_range(f'A{total_row}:H{total_row}', 'الإجمالي', total_format)
    worksheet.write(total_row - 1, 8, total_amount, total_money_format)
    worksheet.merge_range(f'J{total_row}:L{total_row}', '', total_format)
    
    # إضافة صفحة ثانية لملخص الرسوم حسب النوع
    summary_sheet = workbook.add_worksheet('ملخص الرسوم')
    
    # عنوان الصفحة
    summary_sheet.merge_range('A1:D1', 'ملخص الرسوم الحكومية حسب النوع', title_format)
    summary_sheet.merge_range('A2:D2', f'تاريخ التقرير: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', date_title_format)
    
    # عناوين الأعمدة
    summary_headers = ['نوع الرسوم', 'عدد الرسوم', 'إجمالي المبلغ', 'النسبة المئوية']
    for col, header in enumerate(summary_headers):
        summary_sheet.write(3, col, header, header_format)
    
    # تعيين عرض الأعمدة
    summary_sheet.set_column('A:A', 25)
    summary_sheet.set_column('B:B', 15)
    summary_sheet.set_column('C:C', 20)
    summary_sheet.set_column('D:D', 15)
    
    # استخراج إحصائيات الرسوم حسب النوع
    fee_stats = db.session.query(
        GovernmentFee.fee_type,
        func.count(GovernmentFee.id).label('count'),
        func.sum(GovernmentFee.amount).label('total')
    ).group_by(GovernmentFee.fee_type).all()
    
    # كتابة بيانات الملخص
    total_all = sum(stat[2] for stat in fee_stats) if fee_stats else 0
    
    for i, (fee_type, count, fee_total) in enumerate(fee_stats):
        row = i + 4
        percentage = (fee_total / total_all) * 100 if total_all > 0 else 0
        
        summary_sheet.write(row, 0, fee_types.get(fee_type, fee_type), cell_format)
        summary_sheet.write(row, 1, count, cell_format)
        summary_sheet.write(row, 2, fee_total, money_format)
        summary_sheet.write(row, 3, f'{percentage:.2f}%', cell_format)
    
    # إضافة صف للإجمالي
    summary_total_row = len(fee_stats) + 4
    summary_sheet.write(summary_total_row, 0, 'الإجمالي', total_format)
    summary_sheet.write(summary_total_row, 1, sum(stat[1] for stat in fee_stats), total_format)
    summary_sheet.write(summary_total_row, 2, total_all, total_money_format)
    summary_sheet.write(summary_total_row, 3, '100.00%', total_format)
    
    # إغلاق الملف وإرجاع البيانات
    workbook.close()
    output.seek(0)
    
    # إنشاء اسم الملف بناء على المعايير المستخدمة
    filename_parts = ['government_fees']
    if fee_type:
        filename_parts.append(fee_type)
    if payment_status:
        filename_parts.append(payment_status)
    if department_id:
        department = Department.query.get(department_id)
        if department:
            filename_parts.append(department.name)
    if year:
        filename_parts.append(str(year))
    if month:
        filename_parts.append(str(month))
    
    filename = '_'.join(filename_parts) + '.xlsx'
    
    return output, filename

def generate_monthly_report(year, month):
    """
    إنشاء تقرير شهري للرسوم الحكومية
    
    Args:
        year (int): السنة
        month (int): الشهر
        
    Returns:
        io.BytesIO: تيار بايت يحتوي على ملف Excel
    """
    return export_government_fees_data(year=year, month=month)

def generate_employee_report(employee_id):
    """
    إنشاء تقرير للرسوم الحكومية لموظف محدد
    
    Args:
        employee_id (int): معرف الموظف
        
    Returns:
        io.BytesIO: تيار بايت يحتوي على ملف Excel
    """
    # إنشاء استعلام قاعدة البيانات
    query = GovernmentFee.query.filter(GovernmentFee.employee_id == employee_id)
    
    # الحصول على البيانات
    fees = query.order_by(GovernmentFee.fee_date.desc()).all()
    employee = Employee.query.get(employee_id)
    
    if not employee:
        return None, "employee_not_found"
    
    # إنشاء ملف Excel في الذاكرة
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet('الرسوم الحكومية')
    
    # تعريف الأنماط
    header_format = workbook.add_format({
        'bold': True,
        'font_size': 14,
        'align': 'center',
        'valign': 'vcenter',
        'bg_color': '#0d6efd',
        'color': 'white',
        'border': 1
    })
    
    cell_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
        'border': 1
    })
    
    money_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
        'border': 1,
        'num_format': '#,##0.00 ريال'
    })
    
    date_format = workbook.add_format({
        'align': 'center',
        'valign': 'vcenter',
        'border': 1,
        'num_format': 'yyyy-mm-dd'
    })
    
    # تعيين عرض الأعمدة
    worksheet.set_column('A:A', 5)
    worksheet.set_column('B:B', 25)
    worksheet.set_column('C:C', 15)
    worksheet.set_column('D:D', 15)
    worksheet.set_column('E:E', 15)
    worksheet.set_column('F:F', 15)
    
    # إضافة عنوان
    title_format = workbook.add_format({
        'bold': True,
        'font_size': 18,
        'align': 'center',
        'valign': 'vcenter'
    })
    
    worksheet.merge_range('A1:F1', f'تقرير الرسوم الحكومية للموظف: {employee.name}', title_format)
    worksheet.merge_range('A2:F2', f'الرقم الوظيفي: {employee.employee_id}', title_format)
    
    # معلومات الموظف
    info_format = workbook.add_format({
        'bold': True,
        'align': 'right',
        'valign': 'vcenter',
    })
    
    worksheet.write(3, 0, 'القسم:', info_format)
    worksheet.write(3, 1, employee.department.name if employee.department else 'غير محدد')
    worksheet.write(3, 2, 'نوع العقد:', info_format)
    worksheet.write(3, 3, 'سعودي' if employee.contract_type == 'saudi' else 'وافد')
    
    worksheet.write(4, 0, 'تاريخ المباشرة:', info_format)
    worksheet.write(4, 1, employee.join_date.strftime('%Y-%m-%d') if employee.join_date else '')
    worksheet.write(4, 2, 'الراتب الأساسي:', info_format)
    
    salary_format = workbook.add_format({
        'num_format': '#,##0.00 ريال'
    })
    worksheet.write(4, 3, employee.basic_salary or 0, salary_format)
    
    # عناوين الأعمدة
    headers = [
        '#',
        'نوع الرسوم',
        'تاريخ الاستحقاق',
        'المبلغ',
        'حالة السداد',
        'تاريخ السداد'
    ]
    
    # كتابة عناوين الأعمدة
    for col, header in enumerate(headers):
        worksheet.write(6, col, header, header_format)
    
    # قاموس لتحويل القيم
    fee_types = {
        'passport': 'الجوازات',
        'labor_office': 'مكتب العمل',
        'insurance': 'التأمين الطبي',
        'social_insurance': 'التأمينات الاجتماعية',
        'transfer_sponsorship': 'نقل كفالة',
        'other': 'رسوم أخرى'
    }
    
    payment_statuses = {
        'pending': 'قيد الانتظار',
        'paid': 'مدفوع',
        'overdue': 'متأخر'
    }
    
    # كتابة بيانات الرسوم
    total_amount = 0
    for i, fee in enumerate(fees):
        row = i + 7  # البدء من الصف 7 (بعد العناوين)
        
        # حساب إجمالي المبلغ
        total_amount += fee.amount
        
        # كتابة بيانات الصف
        worksheet.write(row, 0, i + 1, cell_format)
        worksheet.write(row, 1, fee_types.get(fee.fee_type, fee.fee_type), cell_format)
        worksheet.write(row, 2, fee.fee_date, date_format)
        worksheet.write(row, 3, fee.amount, money_format)
        worksheet.write(row, 4, payment_statuses.get(fee.payment_status, fee.payment_status), cell_format)
        worksheet.write(row, 5, fee.payment_date or '', date_format)
    
    # إضافة صف للإجمالي
    total_row = len(fees) + 7
    total_format = workbook.add_format({
        'bold': True,
        'align': 'center',
        'valign': 'vcenter',
        'bg_color': '#f8f9fa',
        'border': 1
    })
    
    total_money_format = workbook.add_format({
        'bold': True,
        'align': 'center',
        'valign': 'vcenter',
        'bg_color': '#f8f9fa',
        'border': 1,
        'num_format': '#,##0.00 ريال'
    })
    
    worksheet.merge_range(f'A{total_row}:C{total_row}', 'الإجمالي', total_format)
    worksheet.write(total_row - 1, 3, total_amount, total_money_format)
    worksheet.merge_range(f'E{total_row}:F{total_row}', '', total_format)
    
    # إغلاق الملف وإرجاع البيانات
    workbook.close()
    output.seek(0)
    
    filename = f'employee_government_fees_{employee.employee_id}.xlsx'
    
    return output, filename