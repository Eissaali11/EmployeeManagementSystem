"""
مسارات بوابة الموظفين - تسجيل دخول بالهوية ورقم العمل
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func, or_, and_, extract
from models import Employee, Vehicle, VehicleRental, VehicleProject, Salary, Attendance, Department, User
from app import db
# from functions.date_functions import format_date_arabic
# from utils.audit_log import log_audit

def log_audit(action, entity_type, entity_id, description):
    """دالة مؤقتة لتسجيل الأحداث"""
    print(f"AUDIT: {action} - {entity_type} - {entity_id} - {description}")

employee_portal_bp = Blueprint('employee_portal', __name__, url_prefix='/employee')

@employee_portal_bp.route('/login', methods=['GET', 'POST'])
def employee_login():
    """تسجيل دخول الموظف باستخدام رقم الهوية ورقم العمل"""
    if request.method == 'POST':
        national_id = request.form.get('national_id', '').strip()
        employee_number = request.form.get('employee_number', '').strip()
        
        if not national_id or not employee_number:
            flash('يرجى إدخال رقم الهوية ورقم العمل', 'error')
            return render_template('employee_portal/login.html')
        
        # البحث عن الموظف (مع التعامل مع الأرقام العشرية)
        try:
            # تحويل المدخلات لأرقام للمقارنة
            national_id_float = float(national_id)
            employee_number_float = float(employee_number)
            
            # البحث بالأرقام العشرية أو النصوص
            employee = Employee.query.filter(
                or_(
                    and_(Employee.national_id == national_id, Employee.employee_id == employee_number),
                    and_(Employee.national_id == str(national_id_float), Employee.employee_id == str(employee_number_float)),
                    and_(Employee.national_id == national_id_float, Employee.employee_id == employee_number_float)
                )
            ).first()
        except ValueError:
            # في حالة عدم إمكانية تحويل المدخلات لأرقام
            employee = Employee.query.filter_by(
                national_id=national_id,
                employee_id=employee_number
            ).first()
        
        if not employee:
            flash('بيانات تسجيل الدخول غير صحيحة', 'error')
            log_audit('failed_login', 'employee', None, f'محاولة دخول فاشلة - هوية: {national_id}, رقم عمل: {employee_number}')
            return render_template('employee_portal/login.html')
        
        # فحص حالة الحساب
        if employee.status != 'active':
            if employee.status == 'inactive':
                flash('حسابك غير نشط. يرجى مراجعة إدارة الموارد البشرية', 'error')
            elif employee.status == 'on_leave':
                flash('أنت في إجازة حالياً. لا يمكن الوصول للبوابة', 'error')
            else:
                flash('حالة حسابك لا تسمح بالوصول للبوابة', 'error')
            log_audit('failed_login', 'employee', employee.id, f'محاولة دخول لحساب غير نشط - {employee.name} - الحالة: {employee.status}')
            return render_template('employee_portal/login.html')
        
        # تسجيل الدخول في الجلسة
        session['employee_id'] = employee.id
        session['employee_name'] = employee.name
        session['employee_number'] = employee.employee_number
        session['employee_login_time'] = datetime.now().isoformat()
        
        # تسجيل عملية الدخول
        log_audit('employee_login', 'employee', employee.id, f'تسجيل دخول الموظف: {employee.name}')
        
        flash(f'مرحباً {employee.name}', 'success')
        return redirect(url_for('employee_portal.dashboard'))
    
    return render_template('employee_portal/login.html')

@employee_portal_bp.route('/logout')
def employee_logout():
    """تسجيل خروج الموظف"""
    employee_id = session.get('employee_id')
    employee_name = session.get('employee_name')
    
    if employee_id:
        log_audit('employee_logout', 'employee', employee_id, f'تسجيل خروج الموظف: {employee_name}')
    
    # مسح جلسة الموظف
    session.pop('employee_id', None)
    session.pop('employee_name', None)
    session.pop('employee_number', None)
    session.pop('employee_login_time', None)
    
    flash('تم تسجيل الخروج بنجاح', 'info')
    return redirect(url_for('employee_portal.employee_login'))

def employee_login_required(f):
    """ديكوريتر للتحقق من تسجيل دخول الموظف وحالة الحساب"""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'employee_id' not in session:
            flash('يرجى تسجيل الدخول أولاً', 'warning')
            return redirect(url_for('employee_portal.employee_login'))
        
        # التحقق من حالة الحساب في كل طلب
        employee_id = session.get('employee_id')
        employee = Employee.query.get(employee_id)
        
        if not employee or employee.status != 'active':
            # مسح الجلسة إذا كان الحساب غير نشط
            session.clear()
            if employee and employee.status == 'inactive':
                flash('تم إيقاف حسابك. يرجى مراجعة إدارة الموارد البشرية', 'error')
            elif employee and employee.status == 'on_leave':
                flash('حسابك في حالة إجازة. لا يمكن الوصول للبوابة', 'error')
            else:
                flash('حالة حسابك تغيرت. يرجى تسجيل الدخول مرة أخرى', 'warning')
            return redirect(url_for('employee_portal.employee_login'))
        
        return f(*args, **kwargs)
    return decorated_function

@employee_portal_bp.route('/dashboard')
@employee_login_required
def dashboard():
    """لوحة معلومات الموظف"""
    employee_id = session.get('employee_id')
    employee = Employee.query.get_or_404(employee_id)
    
    # احصائيات سريعة
    stats = {}
    
    # السيارات المخصصة للموظف
    assigned_vehicles = Vehicle.query.filter(
        or_(
            Vehicle.current_driver_id == employee_id,
            VehicleRental.query.filter_by(
                employee_id=employee_id,
                is_active=True
            ).exists(),
            VehicleProject.query.filter_by(
                employee_id=employee_id,
                is_active=True
            ).exists()
        )
    ).all()
    
    stats['assigned_vehicles_count'] = len(assigned_vehicles)
    
    # آخر راتب
    latest_salary = Salary.query.filter_by(employee_id=employee_id).order_by(Salary.salary_date.desc()).first()
    stats['latest_salary'] = latest_salary
    
    # حضور هذا الشهر
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    monthly_attendance = Attendance.query.filter(
        Attendance.employee_id == employee_id,
        extract('month', Attendance.date) == current_month,
        extract('year', Attendance.date) == current_year
    ).all()
    
    stats['monthly_attendance_days'] = len([a for a in monthly_attendance if a.status == 'present'])
    stats['monthly_absence_days'] = len([a for a in monthly_attendance if a.status == 'absent'])
    
    # الإجازات المتبقية
    stats['remaining_vacation_days'] = employee.annual_vacation_days or 0
    
    return render_template('employee_portal/dashboard.html', 
                         employee=employee, 
                         stats=stats,
                         assigned_vehicles=assigned_vehicles)

@employee_portal_bp.route('/vehicles')
@employee_login_required
def my_vehicles():
    """السيارات المخصصة للموظف"""
    employee_id = session.get('employee_id')
    employee = Employee.query.get_or_404(employee_id)
    
    # السيارات المخصصة كسائق حالي
    current_driver_vehicles = Vehicle.query.filter_by(current_driver_id=employee_id).all()
    
    # السيارات المؤجرة للموظف
    rented_vehicles = db.session.query(Vehicle, VehicleRental).join(
        VehicleRental, Vehicle.id == VehicleRental.vehicle_id
    ).filter(
        VehicleRental.employee_id == employee_id,
        VehicleRental.is_active == True
    ).all()
    
    # السيارات في مشاريع للموظف
    project_vehicles = db.session.query(Vehicle, VehicleProject).join(
        VehicleProject, Vehicle.id == VehicleProject.vehicle_id
    ).filter(
        VehicleProject.employee_id == employee_id,
        VehicleProject.is_active == True
    ).all()
    
    return render_template('employee_portal/vehicles.html',
                         employee=employee,
                         current_driver_vehicles=current_driver_vehicles,
                         rented_vehicles=rented_vehicles,
                         project_vehicles=project_vehicles)

@employee_portal_bp.route('/salaries')
@employee_login_required
def my_salaries():
    """رواتب الموظف"""
    employee_id = session.get('employee_id')
    employee = Employee.query.get_or_404(employee_id)
    
    # جلب جميع الرواتب
    salaries = Salary.query.filter_by(employee_id=employee_id).order_by(Salary.salary_date.desc()).all()
    
    # تنسيق التواريخ
    for salary in salaries:
        if salary.salary_date:
            salary.formatted_salary_date = salary.salary_date.strftime('%Y-%m-%d')
        else:
            salary.formatted_salary_date = 'غير محدد'
    
    # احصائيات الرواتب
    total_salaries = len(salaries)
    total_amount = sum(s.net_salary for s in salaries if s.net_salary)
    avg_salary = total_amount / total_salaries if total_salaries > 0 else 0
    
    salary_stats = {
        'total_count': total_salaries,
        'total_amount': total_amount,
        'average_salary': avg_salary,
        'latest_salary': salaries[0] if salaries else None
    }
    
    return render_template('employee_portal/salaries.html',
                         employee=employee,
                         salaries=salaries,
                         salary_stats=salary_stats)

@employee_portal_bp.route('/attendance')
@employee_login_required
def my_attendance():
    """حضور الموظف"""
    employee_id = session.get('employee_id')
    employee = Employee.query.get_or_404(employee_id)
    
    # فلترة بالشهر والسنة
    month = request.args.get('month', datetime.now().month, type=int)
    year = request.args.get('year', datetime.now().year, type=int)
    
    # جلب سجل الحضور للشهر المحدد
    attendance_records = Attendance.query.filter(
        Attendance.employee_id == employee_id,
        extract('month', Attendance.date) == month,
        extract('year', Attendance.date) == year
    ).order_by(Attendance.date.desc()).all()
    
    # تنسيق التواريخ
    for record in attendance_records:
        if record.date:
            record.formatted_date = record.date.strftime('%Y-%m-%d')
        else:
            record.formatted_date = 'غير محدد'
    
    # احصائيات الحضور
    present_days = len([r for r in attendance_records if r.status == 'present'])
    absent_days = len([r for r in attendance_records if r.status == 'absent'])
    late_days = len([r for r in attendance_records if r.status == 'late'])
    vacation_days = len([r for r in attendance_records if r.status == 'vacation'])
    
    attendance_stats = {
        'present_days': present_days,
        'absent_days': absent_days,
        'late_days': late_days,
        'vacation_days': vacation_days,
        'total_days': len(attendance_records),
        'attendance_rate': (present_days / len(attendance_records) * 100) if attendance_records else 0
    }
    
    # قائمة الأشهر والسنوات للفلترة
    months = [
        (1, 'يناير'), (2, 'فبراير'), (3, 'مارس'), (4, 'أبريل'),
        (5, 'مايو'), (6, 'يونيو'), (7, 'يوليو'), (8, 'أغسطس'),
        (9, 'سبتمبر'), (10, 'أكتوبر'), (11, 'نوفمبر'), (12, 'ديسمبر')
    ]
    
    years = list(range(datetime.now().year - 5, datetime.now().year + 1))
    
    return render_template('employee_portal/attendance.html',
                         employee=employee,
                         attendance_records=attendance_records,
                         attendance_stats=attendance_stats,
                         current_month=month,
                         current_year=year,
                         months=months,
                         years=years)

@employee_portal_bp.route('/profile')
@employee_login_required
def my_profile():
    """الملف الشخصي للموظف"""
    employee_id = session.get('employee_id')
    employee = Employee.query.get_or_404(employee_id)
    
    # معلومات القسم
    department = Department.query.get(employee.department_id) if employee.department_id else None
    
    # تنسيق التواريخ
    employee.formatted_hire_date = employee.hire_date.strftime('%Y-%m-%d') if employee.hire_date else 'غير محدد'
    employee.formatted_birth_date = employee.birth_date.strftime('%Y-%m-%d') if employee.birth_date else 'غير محدد'
    
    return render_template('employee_portal/profile.html',
                         employee=employee,
                         department=department)

@employee_portal_bp.route('/api/attendance_chart/<int:year>')
@employee_login_required
def attendance_chart_data(year):
    """بيانات مخطط الحضور السنوي"""
    employee_id = session.get('employee_id')
    
    monthly_data = []
    months = ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو',
              'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر']
    
    for month in range(1, 13):
        attendance_count = Attendance.query.filter(
            Attendance.employee_id == employee_id,
            extract('month', Attendance.date) == month,
            extract('year', Attendance.date) == year,
            Attendance.status == 'present'
        ).count()
        
        absent_count = Attendance.query.filter(
            Attendance.employee_id == employee_id,
            extract('month', Attendance.date) == month,
            extract('year', Attendance.date) == year,
            Attendance.status == 'absent'
        ).count()
        
        monthly_data.append({
            'month': months[month-1],
            'present': attendance_count,
            'absent': absent_count
        })
    
    return jsonify(monthly_data)