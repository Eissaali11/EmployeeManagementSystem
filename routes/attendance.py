from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import func
from datetime import datetime, time, timedelta
from app import db
from models import Attendance, Employee, Department, SystemAudit
from utils.date_converter import parse_date, format_date_hijri, format_date_gregorian

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
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
        'stats': result
    })

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
