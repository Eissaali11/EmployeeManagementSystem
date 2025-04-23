from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from sqlalchemy import func
from datetime import datetime, time, timedelta
from app import db
from models import Attendance, Employee, Department, SystemAudit
from utils.date_converter import parse_date, format_date_hijri, format_date_gregorian
from utils.excel import export_attendance_by_department

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/')
def index():
    """List attendance records with filtering options"""
    # Get filter parameters
    date_str = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
    department_id = request.args.get('department_id', '')
    status = request.args.get('status', '')
    
    # Parse date
    try:
        date = parse_date(date_str)
    except ValueError:
        date = datetime.now().date()
    
    # Build query
    query = Attendance.query.filter(Attendance.date == date)
    
    # Apply filters
    if department_id and department_id != '':
        query = query.join(Employee).filter(Employee.department_id == department_id)
    
    if status and status != '':
        query = query.filter(Attendance.status == status)
    
    # Execute query
    attendances = query.all()
    
    # Get departments for filter dropdown
    departments = Department.query.all()
    
    # Format date for display in both calendars
    hijri_date = format_date_hijri(date)
    gregorian_date = format_date_gregorian(date)
    
    return render_template('attendance/index.html', 
                          attendances=attendances,
                          departments=departments,
                          date=date,
                          hijri_date=hijri_date,
                          gregorian_date=gregorian_date,
                          selected_department=department_id,
                          selected_status=status)

@attendance_bp.route('/record', methods=['GET', 'POST'])
def record():
    """Record attendance for individual employees"""
    if request.method == 'POST':
        try:
            employee_id = request.form['employee_id']
            date_str = request.form['date']
            status = request.form['status']
            
            # Parse date
            date = parse_date(date_str)
            
            # Check if attendance record already exists
            existing = Attendance.query.filter_by(
                employee_id=employee_id,
                date=date
            ).first()
            
            if existing:
                # Update existing record
                existing.status = status
                existing.notes = request.form.get('notes', '')
                
                # Process check-in and check-out times if present
                if status == 'present':
                    check_in_str = request.form.get('check_in', '')
                    check_out_str = request.form.get('check_out', '')
                    
                    if check_in_str:
                        hours, minutes = map(int, check_in_str.split(':'))
                        existing.check_in = time(hours, minutes)
                    
                    if check_out_str:
                        hours, minutes = map(int, check_out_str.split(':'))
                        existing.check_out = time(hours, minutes)
                else:
                    existing.check_in = None
                    existing.check_out = None
                
                db.session.commit()
                flash('تم تحديث سجل الحضور بنجاح', 'success')
            else:
                # Create new attendance record
                new_attendance = Attendance(
                    employee_id=employee_id,
                    date=date,
                    status=status,
                    notes=request.form.get('notes', '')
                )
                
                # Process check-in and check-out times if present and status is 'present'
                if status == 'present':
                    check_in_str = request.form.get('check_in', '')
                    check_out_str = request.form.get('check_out', '')
                    
                    if check_in_str:
                        hours, minutes = map(int, check_in_str.split(':'))
                        new_attendance.check_in = time(hours, minutes)
                    
                    if check_out_str:
                        hours, minutes = map(int, check_out_str.split(':'))
                        new_attendance.check_out = time(hours, minutes)
                
                db.session.add(new_attendance)
                db.session.commit()
                
                # Log the action
                employee = Employee.query.get(employee_id)
                audit = SystemAudit(
                    action='create',
                    entity_type='attendance',
                    entity_id=new_attendance.id,
                    details=f'تم تسجيل حضور للموظف: {employee.name} بتاريخ {date}'
                )
                db.session.add(audit)
                db.session.commit()
                
                flash('تم تسجيل الحضور بنجاح', 'success')
            
            return redirect(url_for('attendance.index', date=date_str))
        
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ: {str(e)}', 'danger')
    
    # Get all active employees for dropdown
    employees = Employee.query.filter_by(status='active').all()
    
    # Default to today's date
    today = datetime.now().date()
    hijri_date = format_date_hijri(today)
    gregorian_date = format_date_gregorian(today)
    
    return render_template('attendance/record.html', 
                          employees=employees, 
                          today=today,
                          hijri_date=hijri_date,
                          gregorian_date=gregorian_date)

@attendance_bp.route('/department', methods=['GET', 'POST'])
def department_attendance():
    """Record attendance for an entire department at once"""
    if request.method == 'POST':
        try:
            department_id = request.form['department_id']
            date_str = request.form['date']
            status = request.form['status']
            
            # Parse date
            date = parse_date(date_str)
            
            # Get all employees in the department
            employees = Employee.query.filter_by(
                department_id=department_id,
                status='active'
            ).all()
            
            count = 0
            for employee in employees:
                # Check if attendance record already exists
                existing = Attendance.query.filter_by(
                    employee_id=employee.id,
                    date=date
                ).first()
                
                if existing:
                    # Update existing record
                    existing.status = status
                    if status != 'present':
                        existing.check_in = None
                        existing.check_out = None
                else:
                    # Create new attendance record
                    new_attendance = Attendance(
                        employee_id=employee.id,
                        date=date,
                        status=status
                    )
                    db.session.add(new_attendance)
                
                count += 1
            
            # Log the action
            department = Department.query.get(department_id)
            audit = SystemAudit(
                action='mass_update',
                entity_type='attendance',
                entity_id=0,
                details=f'تم تسجيل حضور لقسم {department.name} بتاريخ {date} لعدد {count} موظف'
            )
            db.session.add(audit)
            db.session.commit()
            
            flash(f'تم تسجيل الحضور لـ {count} موظف بنجاح', 'success')
            return redirect(url_for('attendance.index', date=date_str))
        
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ: {str(e)}', 'danger')
    
    # Get all departments
    departments = Department.query.all()
    
    # Default to today's date
    today = datetime.now().date()
    hijri_date = format_date_hijri(today)
    gregorian_date = format_date_gregorian(today)
    
    return render_template('attendance/department.html', 
                          departments=departments,
                          today=today,
                          hijri_date=hijri_date,
                          gregorian_date=gregorian_date)

@attendance_bp.route('/multi-day-department', methods=['GET', 'POST'])
def multi_day_department_attendance():
    """تسجيل حضور لقسم بالكامل لفترة زمنية محددة"""
    if request.method == 'POST':
        try:
            department_id = request.form['department_id']
            start_date_str = request.form['start_date']
            end_date_str = request.form['end_date']
            status = request.form['status']
            
            # تحليل التواريخ
            try:
                start_date = parse_date(start_date_str)
                end_date = parse_date(end_date_str)
                
                if not start_date or not end_date:
                    raise ValueError("تاريخ غير صالح")
                
                # التحقق من صحة النطاق
                if end_date < start_date:
                    flash('تاريخ النهاية يجب أن يكون بعد تاريخ البداية أو مساوياً له.', 'danger')
                    return redirect(url_for('attendance.multi_day_department_attendance'))
            except (ValueError, TypeError) as e:
                flash(f'خطأ في تنسيق التاريخ: {str(e)}', 'danger')
                return redirect(url_for('attendance.multi_day_department_attendance'))
                
            # الحصول على جميع الموظفين في القسم
            employees = Employee.query.filter_by(
                department_id=department_id,
                status='active'
            ).all()
            
            # حساب عدد الأيام
            delta = end_date - start_date
            days_count = delta.days + 1  # لتضمين اليوم الأخير
            
            # التحضير لكل يوم في النطاق المحدد
            total_count = 0
            current_date = start_date
            
            while current_date <= end_date:
                day_count = 0
                
                for employee in employees:
                    # التحقق من وجود سجل حضور مسبق
                    existing = Attendance.query.filter_by(
                        employee_id=employee.id,
                        date=current_date
                    ).first()
                    
                    if existing:
                        # تحديث السجل الموجود
                        existing.status = status
                        if status != 'present':
                            existing.check_in = None
                            existing.check_out = None
                    else:
                        # إنشاء سجل حضور جديد
                        new_attendance = Attendance(
                            employee_id=employee.id,
                            date=current_date,
                            status=status
                        )
                        db.session.add(new_attendance)
                    
                    day_count += 1
                
                total_count += day_count
                current_date += timedelta(days=1)
            
            # تسجيل الإجراء
            department = Department.query.get(department_id)
            audit = SystemAudit(
                action='mass_update_range',
                entity_type='attendance',
                entity_id=0,
                entity_name=department.name,
                details=f'تم تسجيل حضور لقسم {department.name} للفترة من {start_date} إلى {end_date} لعدد {len(employees)} موظف'
            )
            db.session.add(audit)
            db.session.commit()
            
            flash(f'تم تسجيل الحضور لـ {len(employees)} موظف خلال {days_count} يوم بنجاح', 'success')
            return redirect(url_for('attendance.index'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ: {str(e)}', 'danger')
    
    # الحصول على جميع الأقسام
    departments = Department.query.all()
    
    # التاريخ الافتراضي (اليوم)
    today = datetime.now().date()
    hijri_date = format_date_hijri(today)
    gregorian_date = format_date_gregorian(today)
    
    return render_template('attendance/multi_day_department.html', 
                          departments=departments,
                          today=today,
                          hijri_date=hijri_date,
                          gregorian_date=gregorian_date)

@attendance_bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    """Delete an attendance record"""
    attendance = Attendance.query.get_or_404(id)
    date = attendance.date
    employee_name = attendance.employee.name
    
    try:
        db.session.delete(attendance)
        
        # Log the action
        audit = SystemAudit(
            action='delete',
            entity_type='attendance',
            entity_id=id,
            details=f'تم حذف سجل حضور للموظف: {employee_name} بتاريخ {date}'
        )
        db.session.add(audit)
        db.session.commit()
        
        flash('تم حذف سجل الحضور بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء حذف سجل الحضور: {str(e)}', 'danger')
    
    return redirect(url_for('attendance.index', date=date))

@attendance_bp.route('/stats')
def stats():
    """Get attendance statistics for a date range"""
    # Get date range
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    try:
        start_date = parse_date(start_date_str) if start_date_str else (datetime.now().date() - timedelta(days=30))
        end_date = parse_date(end_date_str) if end_date_str else datetime.now().date()
    except ValueError:
        start_date = datetime.now().date() - timedelta(days=30)
        end_date = datetime.now().date()
    
    # Calculate statistics
    stats = db.session.query(
        Attendance.status,
        func.count(Attendance.id).label('count')
    ).filter(
        Attendance.date.between(start_date, end_date)
    ).group_by(Attendance.status).all()
    
    # Format for response
    result = {}
    for status, count in stats:
        result[status] = count
    
    return jsonify({
        'start_date': start_date.isoformat() if start_date else None,
        'end_date': end_date.isoformat() if end_date else None,
        'stats': result
    })

@attendance_bp.route('/export_excel')
def export_excel():
    """تصدير بيانات الحضور إلى ملف Excel"""
    try:
        # الحصول على معايير التصفية
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        department_id = request.args.get('department_id', '')
        
        # معالجة التواريخ
        try:
            start_date = parse_date(start_date_str) if start_date_str else datetime.now().date()
            end_date = parse_date(end_date_str) if end_date_str else start_date
        except ValueError:
            start_date = datetime.now().date()
            end_date = start_date
        
        # الحصول على جميع الموظفين النشطين
        employees_query = Employee.query.filter_by(status='active')
        
        # تطبيق فلتر القسم إذا تم تحديده
        if department_id and department_id != '':
            employees_query = employees_query.filter(Employee.department_id == department_id)
        
        employees = employees_query.all()
        
        # الحصول على سجلات الحضور للفترة المحددة
        attendance_query = Attendance.query.filter(
            Attendance.date.between(start_date, end_date)
        )
        
        # تطبيق فلتر القسم إذا تم تحديده
        if department_id and department_id != '':
            attendance_query = attendance_query.join(Employee).filter(Employee.department_id == department_id)
        
        attendances = attendance_query.all()
        
        # تصدير البيانات إلى ملف إكسل
        output = export_attendance_by_department(employees, attendances, start_date, end_date)
        
        # تحديد اسم الملف
        if start_date is not None and end_date is not None:
            if start_date == end_date:
                filename = f"سجل_الحضور_{start_date.strftime('%Y-%m-%d')}.xlsx"
            else:
                filename = f"سجل_الحضور_{start_date.strftime('%Y-%m-%d')}_إلى_{end_date.strftime('%Y-%m-%d')}.xlsx"
        else:
            # حالة احتياطية
            today = datetime.now().date()
            filename = f"سجل_الحضور_{today.strftime('%Y-%m-%d')}.xlsx"
        
        # إرسال الملف للتنزيل
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    
    except Exception as e:
        flash(f'حدث خطأ أثناء تصدير البيانات: {str(e)}', 'danger')
        return redirect(url_for('attendance.index'))

# صفحة تصدير بيانات الحضور
@attendance_bp.route('/export')
def export_page():
    """صفحة تصدير بيانات الحضور إلى ملف Excel"""
    # الحصول على جميع الأقسام
    departments = Department.query.order_by(Department.name).all()
    
    # إعداد القيم الافتراضية
    today = datetime.now().date()
    default_start_date = today.strftime('%Y-%m-%d')
    
    return render_template('attendance/export.html', 
                          departments=departments,
                          default_start_date=default_start_date)

@attendance_bp.route('/api/departments/<int:department_id>/employees')
def get_department_employees(department_id):
    """API endpoint to get all employees in a department"""
    try:
        # Get the department
        department = Department.query.get_or_404(department_id)
        
        # Get all active employees in the department
        employees = Employee.query.filter_by(
            department_id=department_id,
            status='active'  # Only return active employees
        ).all()
        
        # Format employee data
        employee_data = []
        for employee in employees:
            employee_data.append({
                'id': employee.id,
                'name': employee.name,
                'employee_id': employee.employee_id,
                'job_title': employee.job_title,
                'status': employee.status
            })
        
        return jsonify(employee_data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
        
@attendance_bp.route('/employee/<int:employee_id>')
def employee_attendance(employee_id):
    """عرض سجلات الحضور التفصيلية للموظف مرتبة حسب الشهر والسنة"""
    
    # الحصول على بيانات الموظف
    employee = Employee.query.get_or_404(employee_id)
    
    # الحصول على سنة وشهر محددين من معاملات الاستعلام (إذا وجدت)
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', datetime.now().month, type=int)
    
    # الحصول على قائمة السنوات والشهور التي يوجد بها سجلات حضور للموظف
    years_months = db.session.query(
        func.extract('year', Attendance.date).label('year'),
        func.extract('month', Attendance.date).label('month')
    ).filter(
        Attendance.employee_id == employee_id
    ).distinct().order_by('year', 'month').all()
    
    # تنظيم السنوات والشهور
    attendance_periods = {}
    for year_month in years_months:
        y = int(year_month.year)
        m = int(year_month.month)
        if y not in attendance_periods:
            attendance_periods[y] = []
        attendance_periods[y].append(m)
    
    # الحصول على سجلات الحضور للشهر والسنة المحددين
    attendances = Attendance.query.filter(
        Attendance.employee_id == employee_id,
        func.extract('year', Attendance.date) == year,
        func.extract('month', Attendance.date) == month
    ).order_by(Attendance.date.desc()).all()
    
    # تنظيم سجلات الحضور حسب اليوم
    attendance_by_day = {}
    for attendance in attendances:
        day = attendance.date.day
        attendance_by_day[day] = attendance
    
    # تحديد أيام الشهر
    from calendar import monthrange
    days_in_month = monthrange(year, month)[1]
    
    # حساب ال weekday لليوم الأول من الشهر
    first_day = datetime(year, month, 1)
    first_day_weekday = first_day.weekday()
    
    return render_template('attendance/employee_attendance.html',
                          employee=employee,
                          attendances=attendances,
                          attendance_by_day=attendance_by_day,
                          attendance_periods=attendance_periods,
                          year=year,
                          month=month,
                          days_in_month=days_in_month,
                          selected_year=year,
                          selected_month=month,
                          first_day_weekday=first_day_weekday)
