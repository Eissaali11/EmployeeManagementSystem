import pandas as pd
from io import BytesIO
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from werkzeug.utils import secure_filename
from sqlalchemy import func
from datetime import datetime
from app import db
from models import Salary, Employee, Department, SystemAudit
from utils.excel import parse_salary_excel, generate_salary_excel
from utils.pdf_generator import generate_salary_report_pdf
from utils.salary_notification import generate_salary_notification_pdf, generate_batch_salary_notifications

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
                        # Check if record already exists
                        existing = Salary.query.filter_by(
                            employee_id=data['employee_id'],
                            month=month,
                            year=year
                        ).first()
                        
                        if existing:
                            # Update existing record
                            existing.basic_salary = data['basic_salary']
                            existing.allowances = data['allowances']
                            existing.deductions = data['deductions']
                            existing.bonus = data['bonus']
                            existing.net_salary = data['net_salary']
                            db.session.commit()
                        else:
                            # Create new record
                            salary = Salary(**data)
                            db.session.add(salary)
                            db.session.commit()
                        
                        success_count += 1
                    except Exception:
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
        
        # تسجيل العملية
        audit = SystemAudit(
            action='generate_notification',
            entity_type='salary',
            entity_id=salary.id,
            details=f'تم إنشاء إشعار راتب للموظف: {salary.employee.name} لشهر {salary.month}/{salary.year}'
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
                # معالجة الإشعارات للقسم المحدد
                processed_employees = generate_batch_salary_notifications(department_id, month, year)
                
                if processed_employees:
                    # تسجيل العملية
                    audit = SystemAudit(
                        action='batch_notifications',
                        entity_type='salary',
                        entity_id=0,
                        details=f'تم إنشاء {len(processed_employees)} إشعار راتب لموظفي قسم {department_name} لشهر {month}/{year}'
                    )
                    db.session.add(audit)
                    db.session.commit()
                    
                    flash(f'تم إنشاء {len(processed_employees)} إشعار راتب لموظفي قسم {department_name}', 'success')
                else:
                    flash(f'لا توجد رواتب مسجلة لموظفي قسم {department_name} في شهر {month}/{year}', 'warning')
            else:
                # معالجة الإشعارات لجميع الموظفين
                processed_employees = generate_batch_salary_notifications(None, month, year)
                
                if processed_employees:
                    # تسجيل العملية
                    audit = SystemAudit(
                        action='batch_notifications',
                        entity_type='salary',
                        entity_id=0,
                        details=f'تم إنشاء {len(processed_employees)} إشعار راتب لجميع الموظفين لشهر {month}/{year}'
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
