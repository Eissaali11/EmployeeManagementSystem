import pandas as pd
from io import BytesIO
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from werkzeug.utils import secure_filename
from sqlalchemy import func
from datetime import datetime
from app import db
from models import Salary, Employee, Department, SystemAudit
from utils.excel import parse_salary_excel, generate_salary_excel
from utils.pdf_generator_fixed import generate_salary_report_pdf
from utils.salary_notification import generate_salary_notification_pdf, generate_batch_salary_notifications
from utils.whatsapp_notification import (
    send_salary_notification_whatsapp, 
    send_salary_deduction_notification_whatsapp,
    send_batch_salary_notifications_whatsapp,
    send_batch_deduction_notifications_whatsapp
)

salaries_bp = Blueprint('salaries', __name__)

@salaries_bp.route('/')
def index():
    """List salary records with filtering options"""
    # Get filter parameters
    month = request.args.get('month', str(datetime.now().month))
    year = request.args.get('year', str(datetime.now().year))
    employee_id = request.args.get('employee_id', '')
    
    # Build query
    query = Salary.query
    
    # Apply filters
    if month and month.isdigit():
        query = query.filter(Salary.month == int(month))
    
    if year and year.isdigit():
        query = query.filter(Salary.year == int(year))
    
    if employee_id and employee_id.isdigit():
        query = query.filter(Salary.employee_id == int(employee_id))
    
    # Execute query
    salaries = query.all()
    
    # Get summary statistics
    if salaries:
        total_basic = sum(s.basic_salary for s in salaries)
        total_allowances = sum(s.allowances for s in salaries)
        total_deductions = sum(s.deductions for s in salaries)
        total_bonus = sum(s.bonus for s in salaries)
        total_net = sum(s.net_salary for s in salaries)
    else:
        total_basic = total_allowances = total_deductions = total_bonus = total_net = 0
    
    # Get all employees for filter dropdown
    employees = Employee.query.filter_by(status='active').all()
    
    # Get available months and years for dropdown
    available_months = db.session.query(Salary.month).distinct().order_by(Salary.month).all()
    available_years = db.session.query(Salary.year).distinct().order_by(Salary.year.desc()).all()
    
    return render_template('salaries/index.html',
                          salaries=salaries,
                          employees=employees,
                          available_months=available_months,
                          available_years=available_years,
                          selected_month=month,
                          selected_year=year,
                          selected_employee=employee_id,
                          total_basic=total_basic,
                          total_allowances=total_allowances,
                          total_deductions=total_deductions,
                          total_bonus=total_bonus,
                          total_net=total_net)

@salaries_bp.route('/create', methods=['GET', 'POST'])
def create():
    """Create a new salary record"""
    if request.method == 'POST':
        try:
            employee_id = request.form['employee_id']
            month = int(request.form['month'])
            year = int(request.form['year'])
            basic_salary = float(request.form['basic_salary'])
            allowances = float(request.form.get('allowances', 0))
            deductions = float(request.form.get('deductions', 0))
            bonus = float(request.form.get('bonus', 0))
            
            # Calculate net salary
            net_salary = basic_salary + allowances + bonus - deductions
            
            # Check if salary record already exists for this employee/month/year
            existing = Salary.query.filter_by(
                employee_id=employee_id,
                month=month,
                year=year
            ).first()
            
            if existing:
                flash('يوجد سجل راتب لهذا الموظف في نفس الشهر والسنة', 'danger')
                return redirect(url_for('salaries.create'))
            
            # Create new salary record
            salary = Salary(
                employee_id=employee_id,
                month=month,
                year=year,
                basic_salary=basic_salary,
                allowances=allowances,
                deductions=deductions,
                bonus=bonus,
                net_salary=net_salary,
                notes=request.form.get('notes', '')
            )
            
            db.session.add(salary)
            
            # Log the action
            employee = Employee.query.get(employee_id)
            audit = SystemAudit(
                action='create',
                entity_type='salary',
                entity_id=employee_id,
                details=f'تم إنشاء سجل راتب للموظف: {employee.name} لشهر {month}/{year}'
            )
            db.session.add(audit)
            db.session.commit()
            
            flash('تم إنشاء سجل الراتب بنجاح', 'success')
            return redirect(url_for('salaries.index', month=month, year=year))
        
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ: {str(e)}', 'danger')
    
    # Get all active employees for dropdown
    employees = Employee.query.filter_by(status='active').all()
    
    # Default to current month and year
    now = datetime.now()
    
    return render_template('salaries/create.html',
                          employees=employees,
                          current_month=now.month,
                          current_year=now.year)

@salaries_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    """تعديل سجل راتب"""
    # الحصول على سجل الراتب
    salary = Salary.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # تحديث بيانات الراتب
            salary.basic_salary = float(request.form['basic_salary'])
            salary.allowances = float(request.form.get('allowances', 0))
            salary.deductions = float(request.form.get('deductions', 0))
            salary.bonus = float(request.form.get('bonus', 0))
            salary.notes = request.form.get('notes', '')
            
            # إعادة حساب صافي الراتب
            salary.net_salary = salary.basic_salary + salary.allowances + salary.bonus - salary.deductions
            
            # تسجيل العملية
            audit = SystemAudit(
                action='update',
                entity_type='salary',
                entity_id=salary.id,
                details=f'تم تعديل سجل راتب للموظف: {salary.employee.name} لشهر {salary.month}/{salary.year}'
            )
            db.session.add(audit)
            
            db.session.commit()
            
            flash('تم تعديل سجل الراتب بنجاح', 'success')
            return redirect(url_for('salaries.index', month=salary.month, year=salary.year))
            
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء تعديل سجل الراتب: {str(e)}', 'danger')
    
    # الحصول على قائمة الموظفين للاختيار من القائمة المنسدلة
    employees = Employee.query.order_by(Employee.name).all()
    
    return render_template('salaries/edit.html',
                          salary=salary,
                          employees=employees)


@salaries_bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    """Delete a salary record"""
    salary = Salary.query.get_or_404(id)
    employee_name = salary.employee.name
    month = salary.month
    year = salary.year
    
    try:
        db.session.delete(salary)
        
        # Log the action
        audit = SystemAudit(
            action='delete',
            entity_type='salary',
            entity_id=id,
            details=f'تم حذف سجل راتب للموظف: {employee_name} لشهر {month}/{year}'
        )
        db.session.add(audit)
        db.session.commit()
        
        flash('تم حذف سجل الراتب بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء حذف سجل الراتب: {str(e)}', 'danger')
    
    return redirect(url_for('salaries.index', month=month, year=year))

@salaries_bp.route('/import', methods=['GET', 'POST'])
def import_excel():
    """Import salary records from Excel file"""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('لم يتم اختيار ملف', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('لم يتم اختيار ملف', 'danger')
            return redirect(request.url)
        
        month = int(request.form['month'])
        year = int(request.form['year'])
        
        if file and file.filename.endswith(('.xlsx', '.xls')):
            try:
                # Parse Excel file
                salaries_data = parse_salary_excel(file, month, year)
                success_count = 0
                error_count = 0
                
                for data in salaries_data:
                    try:
                        # تنظيف رقم الموظف المستورد (إزالة الأصفار الزائدة والمسافات)
                        employee_id_str = str(data['employee_id']).strip()
                        
                        # محاولة البحث عن الموظف بأكثر من طريقة
                        # 1. البحث المباشر
                        employee = Employee.query.filter_by(employee_id=employee_id_str).first()
                        
                        # 2. البحث بعد إزالة الأصفار من البداية
                        if not employee:
                            clean_id = employee_id_str.lstrip('0')
                            employee = Employee.query.filter_by(employee_id=clean_id).first()
                            
                        # 3. البحث بإضافة أصفار للبداية (حتى 6 أرقام إجمالاً)
                        if not employee:
                            padded_id = employee_id_str.zfill(6)
                            employee = Employee.query.filter_by(employee_id=padded_id).first()
                            
                        # 4. البحث باستخدام like للعثور على تطابق جزئي
                        if not employee:
                            employee = Employee.query.filter(
                                Employee.employee_id.like(f"%{employee_id_str}%")
                            ).first()
                            
                        if not employee:
                            print(f"لم يتم العثور على موظف برقم: {data['employee_id']} بعد محاولة البحث بعدة طرق")
                            raise ValueError(f"لم يتم العثور على موظف برقم: {data['employee_id']}")
                            
                        # التحقق من وجود سجل راتب لهذا الموظف في نفس الشهر والسنة
                        existing = Salary.query.filter_by(
                            employee_id=employee.id,  # استخدام معرف الموظف في قاعدة البيانات
                            month=month,
                            year=year
                        ).first()
                        
                        # تحضير بيانات الراتب
                        salary_data = {
                            'employee_id': employee.id,  # معرف الموظف في قاعدة البيانات وليس رقم الموظف
                            'month': month,
                            'year': year,
                            'basic_salary': data['basic_salary'],
                            'allowances': data['allowances'],
                            'deductions': data['deductions'],
                            'bonus': data['bonus'],
                            'net_salary': data['net_salary']
                        }
                        
                        if 'notes' in data:
                            salary_data['notes'] = data['notes']
                        
                        if existing:
                            # تحديث السجل الموجود
                            existing.basic_salary = data['basic_salary']
                            existing.allowances = data['allowances']
                            existing.deductions = data['deductions']
                            existing.bonus = data['bonus']
                            existing.net_salary = data['net_salary']
                            if 'notes' in data:
                                existing.notes = data['notes']
                            db.session.commit()
                        else:
                            # إنشاء سجل جديد
                            salary = Salary(**salary_data)
                            db.session.add(salary)
                            db.session.commit()
                        
                        success_count += 1
                    except Exception as e:
                        # طباعة رسالة الخطأ للسجل
                        print(f"Error importing salary: {str(e)}")
                        db.session.rollback()
                        error_count += 1
                
                # Log the import
                audit = SystemAudit(
                    action='import',
                    entity_type='salary',
                    entity_id=0,
                    details=f'تم استيراد {success_count} سجل راتب لشهر {month}/{year} بنجاح و {error_count} فشل'
                )
                db.session.add(audit)
                db.session.commit()
                
                if error_count > 0:
                    flash(f'تم استيراد {success_count} سجل راتب بنجاح و {error_count} فشل', 'warning')
                else:
                    flash(f'تم استيراد {success_count} سجل راتب بنجاح', 'success')
                return redirect(url_for('salaries.index', month=month, year=year))
            except Exception as e:
                flash(f'حدث خطأ أثناء استيراد الملف: {str(e)}', 'danger')
        else:
            flash('الملف يجب أن يكون بصيغة Excel (.xlsx, .xls)', 'danger')
    
    # Default to current month and year
    now = datetime.now()
    
    return render_template('salaries/import.html',
                          current_month=now.month,
                          current_year=now.year)

@salaries_bp.route('/export')
def export_excel():
    """Export salary records to Excel file"""
    try:
        # Get filter parameters
        month = request.args.get('month')
        year = request.args.get('year')
        
        # Build query
        query = Salary.query
        
        # Apply filters
        if month and month.isdigit():
            query = query.filter(Salary.month == int(month))
            filename_part = f"month_{month}"
        else:
            filename_part = "all_months"
        
        if year and year.isdigit():
            query = query.filter(Salary.year == int(year))
            filename_part += f"_year_{year}"
        else:
            filename_part += "_all_years"
        
        # Execute query
        salaries = query.all()
        
        # Generate Excel file
        output = generate_salary_excel(salaries)
        
        # Log the export
        audit = SystemAudit(
            action='export',
            entity_type='salary',
            entity_id=0,
            details=f'تم تصدير {len(salaries)} سجل راتب إلى ملف Excel'
        )
        db.session.add(audit)
        db.session.commit()
        
        return send_file(
            BytesIO(output.getvalue()),
            download_name=f'salaries_{filename_part}.xlsx',
            as_attachment=True,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        flash(f'حدث خطأ أثناء تصدير البيانات: {str(e)}', 'danger')
        return redirect(url_for('salaries.index'))

@salaries_bp.route('/report')
def report():
    """Generate a salary report for a specific month and year"""
    # Get filter parameters
    month = request.args.get('month', str(datetime.now().month))
    year = request.args.get('year', str(datetime.now().year))
    
    # Validate parameters
    if not month.isdigit() or not year.isdigit():
        flash('يرجى اختيار شهر وسنة صالحين', 'danger')
        return redirect(url_for('salaries.index'))
    
    month = int(month)
    year = int(year)
    
    # Get salary records for the selected month and year
    salaries = Salary.query.filter_by(month=month, year=year).all()
    
    if not salaries:
        flash('لا توجد سجلات رواتب للشهر والسنة المحددين', 'warning')
        return redirect(url_for('salaries.index'))
    
    # Get summary statistics
    total_basic = sum(s.basic_salary for s in salaries)
    total_allowances = sum(s.allowances for s in salaries)
    total_deductions = sum(s.deductions for s in salaries)
    total_bonus = sum(s.bonus for s in salaries)
    total_net = sum(s.net_salary for s in salaries)
    
    return render_template('salaries/report.html',
                          salaries=salaries,
                          month=month,
                          year=year,
                          total_basic=total_basic,
                          total_allowances=total_allowances,
                          total_deductions=total_deductions,
                          total_bonus=total_bonus,
                          total_net=total_net)

@salaries_bp.route('/report/pdf')
def report_pdf():
    """Generate a PDF salary report for a specific month and year"""
    try:
        # Get filter parameters
        month = request.args.get('month')
        year = request.args.get('year')
        
        if not month or not month.isdigit() or not year or not year.isdigit():
            flash('يرجى اختيار شهر وسنة صالحين', 'danger')
            return redirect(url_for('salaries.index'))
        
        month = int(month)
        year = int(year)
        
        # Get salary records for the selected month and year
        salaries = Salary.query.filter_by(month=month, year=year).all()
        
        if not salaries:
            flash('لا توجد سجلات رواتب للشهر والسنة المحددين', 'warning')
            return redirect(url_for('salaries.index'))
        
        # Generate PDF report
        pdf_bytes = generate_salary_report_pdf(salaries, month, year)
        
        # Log the export
        audit = SystemAudit(
            action='export_pdf',
            entity_type='salary',
            entity_id=0,
            details=f'تم تصدير تقرير رواتب لشهر {month}/{year} بصيغة PDF'
        )
        db.session.add(audit)
        db.session.commit()
        
        return send_file(
            BytesIO(pdf_bytes),
            download_name=f'salary_report_{month}_{year}.pdf',
            as_attachment=True,
            mimetype='application/pdf'
        )
    except Exception as e:
        flash(f'حدث خطأ أثناء إنشاء تقرير PDF: {str(e)}', 'danger')
        return redirect(url_for('salaries.index'))

@salaries_bp.route('/notification/<int:id>/pdf')
def salary_notification_pdf(id):
    """إنشاء إشعار راتب لموظف بصيغة PDF"""
    try:
        # الحصول على سجل الراتب
        salary = Salary.query.get_or_404(id)
        
        # إنشاء ملف PDF
        pdf_bytes = generate_salary_notification_pdf(salary)
        
        # تسجيل العملية - بدون تحديد user_id
        audit = SystemAudit(
            action='generate_notification',
            entity_type='salary',
            entity_id=salary.id,
            details=f'تم إنشاء إشعار راتب للموظف: {salary.employee.name} لشهر {salary.month}/{salary.year}',
            user_id=None  # تحديد القيمة بشكل واضح كقيمة فارغة
        )
        db.session.add(audit)
        db.session.commit()
        
        return send_file(
            BytesIO(pdf_bytes),
            download_name=f'salary_notification_{salary.employee.employee_id}_{salary.month}_{salary.year}.pdf',
            as_attachment=True,
            mimetype='application/pdf'
        )
    except Exception as e:
        flash(f'حدث خطأ أثناء إنشاء إشعار الراتب: {str(e)}', 'danger')
        return redirect(url_for('salaries.index'))

@salaries_bp.route('/notification/<int:id>/share_whatsapp')
def share_salary_via_whatsapp(id):
    """مشاركة إشعار راتب عبر الواتس اب باستخدام رابط المشاركة المباشر"""
    try:
        # الحصول على سجل الراتب
        salary = Salary.query.get_or_404(id)
        employee = salary.employee
        
        # الحصول على اسم الشهر بالعربية
        month_names = {
            1: 'يناير', 2: 'فبراير', 3: 'مارس', 4: 'أبريل',
            5: 'مايو', 6: 'يونيو', 7: 'يوليو', 8: 'أغسطس',
            9: 'سبتمبر', 10: 'أكتوبر', 11: 'نوفمبر', 12: 'ديسمبر'
        }
        month_name = month_names.get(salary.month, str(salary.month))
        
        # إنشاء رابط لتحميل ملف PDF
        pdf_url = url_for('salaries.salary_notification_pdf', id=salary.id, _external=True)
        
        # إعداد نص الرسالة مع رابط التحميل
        message_text = f"""
*إشعار راتب - نُظم*

السلام عليكم ورحمة الله وبركاته،

تحية طيبة،

نود إشعاركم بإيداع راتب شهر {month_name} {salary.year}.

الموظف: {employee.name}
الشهر: {month_name} {salary.year}

صافي الراتب: *{salary.net_salary:.2f}*

للاطلاع على تفاصيل الراتب، يمكنكم تحميل نسخة الإشعار من الرابط التالي:
{pdf_url}

مع تحيات إدارة الموارد البشرية
نُظم - نظام إدارة متكامل
"""
        
        # تسجيل العملية
        audit = SystemAudit(
            action='share_whatsapp_link',
            entity_type='salary',
            entity_id=salary.id,
            details=f'تم مشاركة إشعار راتب عبر رابط واتس اب للموظف: {employee.name} لشهر {salary.month}/{salary.year}',
            user_id=None
        )
        db.session.add(audit)
        db.session.commit()
        
        # إنشاء رابط الواتس اب مع نص الرسالة
        from urllib.parse import quote
        
        # التحقق مما إذا كان رقم الهاتف متوفر للموظف
        if employee.mobile:
            # تنسيق رقم الهاتف (إضافة رمز الدولة +966 إذا لم يكن موجودًا)
            to_phone = employee.mobile
            if not to_phone.startswith('+'):
                # إذا كان الرقم يبدأ بـ 0، نحذفه ونضيف رمز الدولة
                if to_phone.startswith('0'):
                    to_phone = "+966" + to_phone[1:]
                else:
                    to_phone = "+966" + to_phone
            
            # إنشاء رابط مباشر للموظف
            whatsapp_url = f"https://wa.me/{to_phone}?text={quote(message_text)}"
        else:
            # إذا لم يكن هناك رقم هاتف، استخدم الطريقة العادية
            whatsapp_url = f"https://wa.me/?text={quote(message_text)}"
        
        # إعادة توجيه المستخدم إلى رابط الواتس اب
        return redirect(whatsapp_url)
        
    except Exception as e:
        flash(f'حدث خطأ أثناء مشاركة إشعار الراتب عبر الواتس اب: {str(e)}', 'danger')
        return redirect(url_for('salaries.index'))


@salaries_bp.route('/notification/<int:id>/share_deduction_whatsapp')
def share_deduction_via_whatsapp(id):
    """مشاركة إشعار خصم راتب عبر الواتس اب باستخدام رابط المشاركة المباشر"""
    try:
        # الحصول على سجل الراتب
        salary = Salary.query.get_or_404(id)
        employee = salary.employee
        
        # التحقق من وجود خصم على الراتب
        if salary.deductions <= 0:
            flash('لا يوجد خصم على هذا الراتب', 'warning')
            return redirect(url_for('salaries.index'))
        
        # الحصول على اسم الشهر بالعربية
        month_names = {
            1: 'يناير', 2: 'فبراير', 3: 'مارس', 4: 'أبريل',
            5: 'مايو', 6: 'يونيو', 7: 'يوليو', 8: 'أغسطس',
            9: 'سبتمبر', 10: 'أكتوبر', 11: 'نوفمبر', 12: 'ديسمبر'
        }
        month_name = month_names.get(salary.month, str(salary.month))
        
        # إنشاء رابط لتحميل ملف PDF
        pdf_url = url_for('salaries.salary_notification_pdf', id=salary.id, _external=True)
        
        # إعداد نص الرسالة مع رابط التحميل
        message_text = f"""
*إشعار خصم على الراتب - نُظم*

السلام عليكم ورحمة الله وبركاته،

تحية طيبة،

نود إبلاغكم عن وجود خصم على راتب شهر {month_name} {salary.year}.

الموظف: {employee.name}
الشهر: {month_name} {salary.year}

مبلغ الخصم: *{salary.deductions:.2f}*

الراتب بعد الخصم: {salary.net_salary:.2f}

للاطلاع على تفاصيل الراتب والخصم، يمكنكم تحميل نسخة الإشعار من الرابط التالي:
{pdf_url}

مع تحيات إدارة الموارد البشرية
نُظم - نظام إدارة متكامل
"""
        
        # تسجيل العملية
        audit = SystemAudit(
            action='share_deduction_whatsapp_link',
            entity_type='salary',
            entity_id=salary.id,
            details=f'تم مشاركة إشعار خصم عبر رابط واتس اب للموظف: {employee.name} لشهر {salary.month}/{salary.year}',
            user_id=None
        )
        db.session.add(audit)
        db.session.commit()
        
        # إنشاء رابط الواتس اب مع نص الرسالة
        from urllib.parse import quote
        
        # التحقق مما إذا كان رقم الهاتف متوفر للموظف
        if employee.mobile:
            # تنسيق رقم الهاتف (إضافة رمز الدولة +966 إذا لم يكن موجودًا)
            to_phone = employee.mobile
            if not to_phone.startswith('+'):
                # إذا كان الرقم يبدأ بـ 0، نحذفه ونضيف رمز الدولة
                if to_phone.startswith('0'):
                    to_phone = "+966" + to_phone[1:]
                else:
                    to_phone = "+966" + to_phone
            
            # إنشاء رابط مباشر للموظف
            whatsapp_url = f"https://wa.me/{to_phone}?text={quote(message_text)}"
        else:
            # إذا لم يكن هناك رقم هاتف، استخدم الطريقة العادية
            whatsapp_url = f"https://wa.me/?text={quote(message_text)}"
        
        # إعادة توجيه المستخدم إلى رابط الواتس اب
        return redirect(whatsapp_url)
        
    except Exception as e:
        flash(f'حدث خطأ أثناء مشاركة إشعار الخصم عبر الواتس اب: {str(e)}', 'danger')
        return redirect(url_for('salaries.index'))


@salaries_bp.route('/notification/<int:id>/whatsapp', methods=['GET'])
def salary_notification_whatsapp(id):
    """إرسال إشعار راتب لموظف عبر WhatsApp"""
    try:
        # الحصول على سجل الراتب
        salary = Salary.query.get_or_404(id)
        employee = salary.employee
        
        # إرسال الإشعار عبر WhatsApp
        success, message = send_salary_notification_whatsapp(employee, salary)
        
        if success:
            # تسجيل العملية
            audit = SystemAudit(
                action='send_whatsapp_notification',
                entity_type='salary',
                entity_id=salary.id,
                details=f'تم إرسال إشعار راتب عبر WhatsApp للموظف: {employee.name} لشهر {salary.month}/{salary.year}',
                user_id=None
            )
            db.session.add(audit)
            db.session.commit()
            
            flash(f'تم إرسال إشعار الراتب عبر WhatsApp بنجاح للموظف {employee.name}', 'success')
        else:
            flash(f'فشل إرسال إشعار الراتب عبر WhatsApp: {message}', 'danger')
        
        return redirect(url_for('salaries.index'))
    except Exception as e:
        flash(f'حدث خطأ أثناء إرسال إشعار الراتب عبر WhatsApp: {str(e)}', 'danger')
        return redirect(url_for('salaries.index'))


@salaries_bp.route('/notification/<int:id>/deduction/whatsapp', methods=['GET'])
def salary_deduction_notification_whatsapp(id):
    """إرسال إشعار خصم على الراتب لموظف عبر WhatsApp"""
    try:
        # الحصول على سجل الراتب
        salary = Salary.query.get_or_404(id)
        employee = salary.employee
        
        # التحقق من وجود خصم على الراتب
        if salary.deductions <= 0:
            flash('لا يوجد خصم على هذا الراتب', 'warning')
            return redirect(url_for('salaries.index'))
        
        # إرسال الإشعار عبر WhatsApp
        success, message = send_salary_deduction_notification_whatsapp(employee, salary)
        
        if success:
            # تسجيل العملية
            audit = SystemAudit(
                action='send_whatsapp_deduction_notification',
                entity_type='salary',
                entity_id=salary.id,
                details=f'تم إرسال إشعار خصم على الراتب عبر WhatsApp للموظف: {employee.name} لشهر {salary.month}/{salary.year}',
                user_id=None
            )
            db.session.add(audit)
            db.session.commit()
            
            flash(f'تم إرسال إشعار الخصم عبر WhatsApp بنجاح للموظف {employee.name}', 'success')
        else:
            flash(f'فشل إرسال إشعار الخصم عبر WhatsApp: {message}', 'danger')
        
        return redirect(url_for('salaries.index'))
    except Exception as e:
        flash(f'حدث خطأ أثناء إرسال إشعار الخصم عبر WhatsApp: {str(e)}', 'danger')
        return redirect(url_for('salaries.index'))


@salaries_bp.route('/notifications/deduction/batch', methods=['GET', 'POST'])
def batch_deduction_notifications():
    """إرسال إشعارات خصومات مجمعة للموظفين عبر WhatsApp"""
    # الحصول على الأقسام للاختيار
    departments = Department.query.all()
    
    if request.method == 'POST':
        try:
            # الحصول على المعلمات
            department_id = request.form.get('department_id')
            month = request.form.get('month')
            year = request.form.get('year')
            
            if not month or not month.isdigit() or not year or not year.isdigit():
                flash('يرجى اختيار شهر وسنة صالحين', 'danger')
                return redirect(url_for('salaries.batch_deduction_notifications'))
                
            month = int(month)
            year = int(year)
            
            # إذا تم تحديد قسم
            if department_id and department_id != 'all':
                department_id = int(department_id)
                department = Department.query.get(department_id)
                department_name = department.name if department else "غير معروف"
                
                # إرسال إشعارات الخصم عبر WhatsApp
                success_count, failure_count, error_messages = send_batch_deduction_notifications_whatsapp(department_id, month, year)
                
                if success_count > 0:
                    # تسجيل العملية
                    audit = SystemAudit(
                        action='batch_whatsapp_deduction_notifications',
                        entity_type='salary',
                        entity_id=0,
                        details=f'تم إرسال {success_count} إشعار خصم عبر WhatsApp لموظفي قسم {department_name} لشهر {month}/{year}',
                        user_id=None
                    )
                    db.session.add(audit)
                    db.session.commit()
                    
                    # عرض رسالة نجاح مع تفاصيل النجاح/الفشل
                    if failure_count > 0:
                        flash(f'تم إرسال {success_count} إشعار خصم بنجاح و {failure_count} فشل', 'warning')
                        for error in error_messages[:5]:  # عرض أول 5 أخطاء فقط
                            flash(error, 'danger')
                        if len(error_messages) > 5:
                            flash(f'... و {len(error_messages) - 5} أخطاء أخرى', 'danger')
                    else:
                        flash(f'تم إرسال {success_count} إشعار خصم عبر WhatsApp بنجاح', 'success')
                else:
                    flash(f'لم يتم إرسال أي إشعارات خصم. {error_messages[0] if error_messages else "لا توجد خصومات مسجلة لموظفي قسم " + department_name + " في شهر " + str(month) + "/" + str(year)}', 'warning')
            else:
                # إرسال إشعارات الخصم لجميع الموظفين
                success_count, failure_count, error_messages = send_batch_deduction_notifications_whatsapp(None, month, year)
                
                if success_count > 0:
                    # تسجيل العملية
                    audit = SystemAudit(
                        action='batch_whatsapp_deduction_notifications',
                        entity_type='salary',
                        entity_id=0,
                        details=f'تم إرسال {success_count} إشعار خصم عبر WhatsApp لجميع الموظفين لشهر {month}/{year}',
                        user_id=None
                    )
                    db.session.add(audit)
                    db.session.commit()
                    
                    # عرض رسالة نجاح مع تفاصيل النجاح/الفشل
                    if failure_count > 0:
                        flash(f'تم إرسال {success_count} إشعار خصم بنجاح و {failure_count} فشل', 'warning')
                        for error in error_messages[:5]:  # عرض أول 5 أخطاء فقط
                            flash(error, 'danger')
                        if len(error_messages) > 5:
                            flash(f'... و {len(error_messages) - 5} أخطاء أخرى', 'danger')
                    else:
                        flash(f'تم إرسال {success_count} إشعار خصم عبر WhatsApp بنجاح', 'success')
                else:
                    flash(f'لم يتم إرسال أي إشعارات خصم. {error_messages[0] if error_messages else "لا توجد خصومات مسجلة لشهر " + str(month) + "/" + str(year)}', 'warning')
                
            return redirect(url_for('salaries.index', month=month, year=year))
                
        except Exception as e:
            flash(f'حدث خطأ أثناء إرسال إشعارات الخصم: {str(e)}', 'danger')
    
    # Default to current month and year
    now = datetime.now()
    
    return render_template('salaries/batch_deduction_notifications.html',
                          departments=departments,
                          current_month=now.month,
                          current_year=now.year)

@salaries_bp.route('/notifications/batch', methods=['GET', 'POST'])
def batch_salary_notifications():
    """إنشاء إشعارات رواتب مجمعة للموظفين حسب القسم"""
    # الحصول على الأقسام للاختيار
    departments = Department.query.all()
    
    if request.method == 'POST':
        try:
            # الحصول على المعلمات
            department_id = request.form.get('department_id')
            month = request.form.get('month')
            year = request.form.get('year')
            notification_type = request.form.get('notification_type', 'pdf')  # نوع الإشعار (pdf أو whatsapp)
            
            if not month or not month.isdigit() or not year or not year.isdigit():
                flash('يرجى اختيار شهر وسنة صالحين', 'danger')
                return redirect(url_for('salaries.batch_salary_notifications'))
                
            month = int(month)
            year = int(year)
            
            # إذا تم تحديد قسم
            if department_id and department_id != 'all':
                department_id = int(department_id)
                department = Department.query.get(department_id)
                department_name = department.name if department else "غير معروف"
                
                if notification_type == 'whatsapp':
                    # إرسال الإشعارات عبر WhatsApp
                    success_count, failure_count, error_messages = send_batch_salary_notifications_whatsapp(department_id, month, year)
                    
                    if success_count > 0:
                        # تسجيل العملية
                        audit = SystemAudit(
                            action='batch_whatsapp_notifications',
                            entity_type='salary',
                            entity_id=0,
                            details=f'تم إرسال {success_count} إشعار راتب عبر WhatsApp لموظفي قسم {department_name} لشهر {month}/{year}',
                            user_id=None
                        )
                        db.session.add(audit)
                        db.session.commit()
                        
                        # عرض رسالة نجاح مع تفاصيل النجاح/الفشل
                        if failure_count > 0:
                            flash(f'تم إرسال {success_count} إشعار راتب بنجاح و {failure_count} فشل', 'warning')
                            for error in error_messages[:5]:  # عرض أول 5 أخطاء فقط
                                flash(error, 'danger')
                            if len(error_messages) > 5:
                                flash(f'... و {len(error_messages) - 5} أخطاء أخرى', 'danger')
                        else:
                            flash(f'تم إرسال {success_count} إشعار راتب عبر WhatsApp بنجاح', 'success')
                    else:
                        flash(f'لم يتم إرسال أي إشعارات. {error_messages[0] if error_messages else "لا توجد رواتب مسجلة لموظفي قسم " + department_name + " في شهر " + str(month) + "/" + str(year)}', 'warning')
                else:
                    # إنشاء ملفات PDF (السلوك الافتراضي)
                    processed_employees = generate_batch_salary_notifications(department_id, month, year)
                    
                    if processed_employees:
                        # تسجيل العملية
                        audit = SystemAudit(
                            action='batch_notifications',
                            entity_type='salary',
                            entity_id=0,
                            details=f'تم إنشاء {len(processed_employees)} إشعار راتب لموظفي قسم {department_name} لشهر {month}/{year}',
                            user_id=None
                        )
                        db.session.add(audit)
                        db.session.commit()
                        
                        flash(f'تم إنشاء {len(processed_employees)} إشعار راتب لموظفي قسم {department_name}', 'success')
                    else:
                        flash(f'لا توجد رواتب مسجلة لموظفي قسم {department_name} في شهر {month}/{year}', 'warning')
            else:
                # معالجة الإشعارات لجميع الموظفين
                if notification_type == 'whatsapp':
                    # إرسال الإشعارات عبر WhatsApp
                    success_count, failure_count, error_messages = send_batch_salary_notifications_whatsapp(None, month, year)
                    
                    if success_count > 0:
                        # تسجيل العملية
                        audit = SystemAudit(
                            action='batch_whatsapp_notifications',
                            entity_type='salary',
                            entity_id=0,
                            details=f'تم إرسال {success_count} إشعار راتب عبر WhatsApp لجميع الموظفين لشهر {month}/{year}',
                            user_id=None
                        )
                        db.session.add(audit)
                        db.session.commit()
                        
                        # عرض رسالة نجاح مع تفاصيل النجاح/الفشل
                        if failure_count > 0:
                            flash(f'تم إرسال {success_count} إشعار راتب بنجاح و {failure_count} فشل', 'warning')
                            for error in error_messages[:5]:  # عرض أول 5 أخطاء فقط
                                flash(error, 'danger')
                            if len(error_messages) > 5:
                                flash(f'... و {len(error_messages) - 5} أخطاء أخرى', 'danger')
                        else:
                            flash(f'تم إرسال {success_count} إشعار راتب عبر WhatsApp بنجاح', 'success')
                    else:
                        flash(f'لم يتم إرسال أي إشعارات. {error_messages[0] if error_messages else "لا توجد رواتب مسجلة لشهر " + str(month) + "/" + str(year)}', 'warning')
                else:
                    # إنشاء ملفات PDF (السلوك الافتراضي)
                    processed_employees = generate_batch_salary_notifications(None, month, year)
                    
                    if processed_employees:
                        # تسجيل العملية
                        audit = SystemAudit(
                            action='batch_notifications',
                            entity_type='salary',
                            entity_id=0,
                            details=f'تم إنشاء {len(processed_employees)} إشعار راتب لجميع الموظفين لشهر {month}/{year}',
                            user_id=None
                        )
                        db.session.add(audit)
                        db.session.commit()
                        
                        flash(f'تم إنشاء {len(processed_employees)} إشعار راتب لجميع الموظفين', 'success')
                    else:
                        flash(f'لا توجد رواتب مسجلة لشهر {month}/{year}', 'warning')
                    
            return redirect(url_for('salaries.index', month=month, year=year))
                
        except Exception as e:
            flash(f'حدث خطأ أثناء إنشاء إشعارات الرواتب: {str(e)}', 'danger')
    
    # Default to current month and year
    now = datetime.now()
    
    return render_template('salaries/batch_notifications.html',
                          departments=departments,
                          current_month=now.month,
                          current_year=now.year)
