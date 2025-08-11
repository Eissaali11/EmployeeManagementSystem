"""
مسارات بوابة الموظفين - تسجيل دخول بالهوية ورقم العمل
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func, or_, and_, extract
from models import Employee, Vehicle, VehicleRental, VehicleProject, VehicleHandover, Salary, Attendance, Department, User, VehicleSafetyCheck
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
        
        # البحث عن الموظف بطريقة مرنة
        from sqlalchemy import text
        
        try:
            # البحث باستخدام تحويل جميع القيم إلى نصوص للمقارنة
            result = db.session.execute(text("""
                SELECT id FROM employee 
                WHERE national_id::text = :national_id 
                AND employee_id::text = :employee_id
                LIMIT 1
            """), {
                'national_id': national_id,
                'employee_id': employee_number
            }).fetchone()
            
            employee = Employee.query.get(result[0]) if result else None
            
        except Exception as e:
            print(f"Database error: {e}")
            employee = None
        
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
        session['employee_number'] = employee.employee_id
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
    
    # السيارات المخصصة للموظف من خلال سجلات التسليم الأخيرة
    latest_handovers = db.session.query(
        VehicleHandover.vehicle_id,
        func.max(VehicleHandover.handover_date).label('latest_date')
    ).filter(
        VehicleHandover.employee_id == employee_id,
        VehicleHandover.handover_type == 'delivery'
    ).group_by(VehicleHandover.vehicle_id).subquery()
    
    assigned_vehicles = db.session.query(Vehicle).join(
        VehicleHandover, Vehicle.id == VehicleHandover.vehicle_id
    ).join(
        latest_handovers, 
        and_(
            VehicleHandover.vehicle_id == latest_handovers.c.vehicle_id,
            VehicleHandover.handover_date == latest_handovers.c.latest_date
        )
    ).filter(
        VehicleHandover.employee_id == employee_id,
        VehicleHandover.handover_type == 'delivery'
    ).all()
    
    stats['assigned_vehicles_count'] = len(assigned_vehicles)
    
    # آخر راتب
    latest_salary = Salary.query.filter_by(employee_id=employee_id).order_by(Salary.created_at.desc()).first()
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
    
    # الإجازات المتبقية (حقل مؤقت)
    stats['remaining_vacation_days'] = 30  # قيمة افتراضية مؤقتة
    
    return render_template('employee_portal/dashboard.html', 
                         employee=employee, 
                         stats=stats,
                         assigned_vehicles=assigned_vehicles)

@employee_portal_bp.route('/vehicles')
@employee_login_required
def my_vehicles():
    """عرض السيارات المخصصة للموظف مع العمليات والفحوصات"""
    employee_id = session.get('employee_id')
    employee = Employee.query.get_or_404(employee_id)
    
    # استيراد النماذج المطلوبة
    from models import OperationRequest, VehicleSafetyCheck, VehiclePeriodicInspection, VehicleWorkshop
    
    # السيارات المخصصة للموظف من خلال سجلات التسليم الأخيرة
    latest_handovers = db.session.query(
        VehicleHandover.vehicle_id,
        func.max(VehicleHandover.handover_date).label('latest_date')
    ).filter(
        VehicleHandover.employee_id == employee_id,
        VehicleHandover.handover_type == 'delivery'
    ).group_by(VehicleHandover.vehicle_id).subquery()
    
    current_driver_vehicles_base = db.session.query(Vehicle).join(
        VehicleHandover, Vehicle.id == VehicleHandover.vehicle_id
    ).join(
        latest_handovers, 
        and_(
            VehicleHandover.vehicle_id == latest_handovers.c.vehicle_id,
            VehicleHandover.handover_date == latest_handovers.c.latest_date
        )
    ).filter(
        VehicleHandover.employee_id == employee_id,
        VehicleHandover.handover_type == 'delivery'
    ).all()
    
    # إضافة معلومات شاملة لكل سيارة
    current_driver_vehicles = []
    for vehicle in current_driver_vehicles_base:
        # جميع نماذج التسليم والاستلام لهذه السيارة والموظف
        vehicle_handovers = VehicleHandover.query.filter_by(
            vehicle_id=vehicle.id,
            employee_id=employee_id
        ).order_by(VehicleHandover.handover_date.desc()).all()
        
        # العمليات المرتبطة بالموظف (لا يوجد حقل employee_id في OperationRequest)
        # سيتم عرض العمليات العامة المرتبطة بالسيارة
        employee_operations = []
        
        # فحوصات السلامة للسيارة
        safety_checks = VehicleSafetyCheck.query.filter_by(
            vehicle_id=vehicle.id
        ).order_by(VehicleSafetyCheck.check_date.desc()).limit(3).all()
        
        # فحوصات السيارة الدورية
        inspections = VehiclePeriodicInspection.query.filter_by(
            vehicle_id=vehicle.id
        ).order_by(VehiclePeriodicInspection.inspection_date.desc()).limit(3).all()
        
        # سجلات الورشة للسيارة
        workshop_records = VehicleWorkshop.query.filter_by(
            vehicle_id=vehicle.id
        ).order_by(VehicleWorkshop.entry_date.desc()).limit(3).all()
        
        vehicle.handovers = vehicle_handovers
        vehicle.employee_operations = employee_operations
        vehicle.safety_checks = safety_checks
        vehicle.inspections = inspections
        vehicle.workshop_records = workshop_records
        current_driver_vehicles.append(vehicle)
    
    # السيارات المؤجرة النشطة (عرض عام)
    rented_vehicles_base = db.session.query(Vehicle, VehicleRental).join(
        VehicleRental, Vehicle.id == VehicleRental.vehicle_id
    ).filter(
        VehicleRental.is_active == True
    ).limit(10).all()
    
    # إضافة معلومات النماذج للسيارات المؤجرة
    rented_vehicles = []
    for vehicle, rental in rented_vehicles_base:
        # البحث عن نماذج التسليم والاستلام لهذه السيارة
        vehicle_handovers = VehicleHandover.query.filter_by(
            vehicle_id=vehicle.id
        ).order_by(VehicleHandover.handover_date.desc()).limit(5).all()
        
        # فحوصات السلامة للسيارة
        safety_checks = VehicleSafetyCheck.query.filter_by(
            vehicle_id=vehicle.id
        ).order_by(VehicleSafetyCheck.check_date.desc()).limit(3).all()
        
        vehicle.handovers = vehicle_handovers
        vehicle.safety_checks = safety_checks
        rented_vehicles.append((vehicle, rental))
    
    # السيارات في مشاريع نشطة (عرض عام)
    project_vehicles_base = db.session.query(Vehicle, VehicleProject).join(
        VehicleProject, Vehicle.id == VehicleProject.vehicle_id
    ).filter(
        VehicleProject.is_active == True
    ).limit(10).all()
    
    # إضافة معلومات النماذج للسيارات في المشاريع
    project_vehicles = []
    for vehicle, project in project_vehicles_base:
        # البحث عن نماذج التسليم والاستلام لهذه السيارة
        vehicle_handovers = VehicleHandover.query.filter_by(
            vehicle_id=vehicle.id
        ).order_by(VehicleHandover.handover_date.desc()).limit(5).all()
        
        # فحوصات السلامة للسيارة
        safety_checks = VehicleSafetyCheck.query.filter_by(
            vehicle_id=vehicle.id
        ).order_by(VehicleSafetyCheck.check_date.desc()).limit(3).all()
        
        vehicle.handovers = vehicle_handovers
        vehicle.safety_checks = safety_checks
        project_vehicles.append((vehicle, project))
    
    # إحصائيات شاملة للموظف
    total_operations = VehicleHandover.query.filter_by(employee_id=employee_id).count()
    
    # عدد فحوصات السلامة للسيارات المخصصة للموظف
    if current_driver_vehicles:
        vehicle_ids = [v.id for v in current_driver_vehicles]
        total_safety_checks = VehicleSafetyCheck.query.filter(
            VehicleSafetyCheck.vehicle_id.in_(vehicle_ids)
        ).count()
    else:
        total_safety_checks = 0
        
    pending_operations = OperationRequest.query.filter_by(status='pending').count()
    approved_operations = OperationRequest.query.filter_by(status='approved').count()
    
    stats = {
        'total_operations': total_operations,
        'total_safety_checks': total_safety_checks,
        'pending_operations': pending_operations,
        'approved_operations': approved_operations
    }
    
    return render_template('employee_portal/vehicles_enhanced.html',
                         employee=employee,
                         current_driver_vehicles=current_driver_vehicles,
                         rented_vehicles=rented_vehicles,
                         project_vehicles=project_vehicles,
                         stats=stats)

@employee_portal_bp.route('/salaries')
@employee_login_required
def my_salaries():
    """رواتب الموظف"""
    employee_id = session.get('employee_id')
    employee = Employee.query.get_or_404(employee_id)
    
    # جلب جميع الرواتب
    salaries = Salary.query.filter_by(employee_id=employee_id).order_by(Salary.year.desc(), Salary.month.desc()).all()
    
    # تنسيق التواريخ
    for salary in salaries:
        if salary.month and salary.year:
            salary.formatted_salary_date = f"{salary.year}-{salary.month:02d}"
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
    """حضور الموظف مع عرض البيانات الشهرية"""
    employee_id = session.get('employee_id')
    employee = Employee.query.get_or_404(employee_id)
    
    # السنة الحالية أو المحددة
    current_year = request.args.get('year', datetime.now().year, type=int)
    
    # جلب جميع سجلات الحضور للسنة
    attendance_records = Attendance.query.filter(
        Attendance.employee_id == employee_id,
        extract('year', Attendance.date) == current_year
    ).all()
    
    # تنظيم البيانات حسب الشهر
    monthly_data = {}
    month_names = {
        1: 'يناير', 2: 'فبراير', 3: 'مارس', 4: 'أبريل',
        5: 'مايو', 6: 'يونيو', 7: 'يوليو', 8: 'أغسطس',
        9: 'سبتمبر', 10: 'أكتوبر', 11: 'نوفمبر', 12: 'ديسمبر'
    }
    
    # تهيئة البيانات الشهرية
    for month in range(1, 13):
        monthly_data[month] = {
            'month': month,
            'month_name': month_names[month],
            'year': current_year,
            'present_days': 0,
            'absent_days': 0,
            'late_days': 0,
            'overtime_hours': 0,
            'attendance_percentage': 0,
            'details': []
        }
    
    # معالجة سجلات الحضور
    for record in attendance_records:
        if record.date:
            month = record.date.month
            
            # تحديد حالة الحضور
            if hasattr(record, 'is_present') and record.is_present:
                monthly_data[month]['present_days'] += 1
                
                # فحص التأخير
                if hasattr(record, 'late_minutes') and record.late_minutes and record.late_minutes > 0:
                    monthly_data[month]['late_days'] += 1
            else:
                # إذا لم يكن موجوداً أو غائب
                if hasattr(record, 'status'):
                    if record.status == 'absent':
                        monthly_data[month]['absent_days'] += 1
                    elif record.status == 'present':
                        monthly_data[month]['present_days'] += 1
                        if hasattr(record, 'late_minutes') and record.late_minutes and record.late_minutes > 0:
                            monthly_data[month]['late_days'] += 1
                else:
                    # إذا لم يكن هناك حقل status، تحديد بناءً على is_present
                    if hasattr(record, 'is_present'):
                        if record.is_present:
                            monthly_data[month]['present_days'] += 1
                        else:
                            monthly_data[month]['absent_days'] += 1
                    else:
                        # افتراضي: حاضر
                        monthly_data[month]['present_days'] += 1
            
            # إضافة الساعات الإضافية
            if hasattr(record, 'overtime_hours') and record.overtime_hours:
                monthly_data[month]['overtime_hours'] += record.overtime_hours
            
            # إضافة التفاصيل
            monthly_data[month]['details'].append(record)
    
    # حساب نسب الحضور
    for month_info in monthly_data.values():
        total_days = month_info['present_days'] + month_info['absent_days']
        if total_days > 0:
            month_info['attendance_percentage'] = (month_info['present_days'] / total_days) * 100
        else:
            month_info['attendance_percentage'] = 0
    
    # تجهيز البيانات للعرض (الأشهر التي تحتوي على بيانات فقط)
    monthly_attendance = []
    for month_info in monthly_data.values():
        if month_info['present_days'] > 0 or month_info['absent_days'] > 0:
            monthly_attendance.append(month_info)
    
    # ترتيب الأشهر
    monthly_attendance.sort(key=lambda x: x['month'])
    
    # حساب الإحصائيات الإجمالية
    total_present_days = sum(month['present_days'] for month in monthly_attendance)
    total_absent_days = sum(month['absent_days'] for month in monthly_attendance)
    total_late_days = sum(month['late_days'] for month in monthly_attendance)
    total_overtime_hours = sum(month['overtime_hours'] for month in monthly_attendance)
    
    return render_template('employee_portal/attendance_enhanced.html',
                         employee=employee,
                         monthly_attendance=monthly_attendance,
                         current_year=current_year,
                         total_present_days=total_present_days,
                         total_absent_days=total_absent_days,
                         total_late_days=total_late_days,
                         total_overtime_hours=total_overtime_hours)

@employee_portal_bp.route('/profile')
@employee_login_required
def my_profile():
    """الملف الشخصي المحسن للموظف مع جميع البيانات"""
    employee_id = session.get('employee_id')
    employee = Employee.query.get_or_404(employee_id)
    
    # معلومات القسم
    department = Department.query.get(employee.department_id) if employee.department_id else None
    
    # السيارات المخصصة للموظف
    latest_handovers = db.session.query(
        VehicleHandover.vehicle_id,
        func.max(VehicleHandover.handover_date).label('latest_date')
    ).filter(
        VehicleHandover.employee_id == employee_id,
        VehicleHandover.handover_type == 'delivery'
    ).group_by(VehicleHandover.vehicle_id).subquery()
    
    assigned_vehicles = db.session.query(Vehicle).join(
        VehicleHandover, Vehicle.id == VehicleHandover.vehicle_id
    ).join(
        latest_handovers, 
        and_(
            VehicleHandover.vehicle_id == latest_handovers.c.vehicle_id,
            VehicleHandover.handover_date == latest_handovers.c.latest_date
        )
    ).filter(
        VehicleHandover.employee_id == employee_id,
        VehicleHandover.handover_type == 'delivery'
    ).all()
    
    # آخر 5 أيام حضور
    recent_attendance = Attendance.query.filter_by(
        employee_id=employee_id
    ).order_by(Attendance.date.desc()).limit(5).all()
    
    # آخر 3 رواتب
    salary_history = Salary.query.filter_by(
        employee_id=employee_id
    ).order_by(Salary.created_at.desc()).limit(3).all()
    
    # حالة الوثائق (فحص انتهاء الصلاحية)
    from datetime import datetime, timedelta
    warning_days = 30  # تحذير قبل 30 يوم
    
    documents_status = {
        'id_expiry_warning': False,
        'license_expiry_warning': False,
        'passport_expiry_warning': False,
        'id_expired': False,
        'license_expired': False,
        'passport_expired': False
    }
    
    today = datetime.now().date()
    warning_date = today + timedelta(days=warning_days)
    
    # فحص الحقول المتوفرة فقط
    if hasattr(employee, 'id_expiry_date') and employee.id_expiry_date:
        if employee.id_expiry_date < today:
            documents_status['id_expired'] = True
        elif employee.id_expiry_date < warning_date:
            documents_status['id_expiry_warning'] = True
            
    if hasattr(employee, 'license_expiry_date') and employee.license_expiry_date:
        if employee.license_expiry_date < today:
            documents_status['license_expired'] = True
        elif employee.license_expiry_date < warning_date:
            documents_status['license_expiry_warning'] = True
            
    if hasattr(employee, 'passport_expiry_date') and employee.passport_expiry_date:
        if employee.passport_expiry_date < today:
            documents_status['passport_expired'] = True
        elif employee.passport_expiry_date < warning_date:
            documents_status['passport_expiry_warning'] = True
    
    # إحصائيات شاملة
    stats = {
        'total_vehicles': len(assigned_vehicles),
        'total_handovers': VehicleHandover.query.filter_by(employee_id=employee_id).count(),
        'present_days_recent': len([a for a in recent_attendance if a.status == 'present']),
        'total_salary_payments': len(salary_history),
        'years_of_service': 0,
        'mobile_devices': 0
    }
    
    # حساب سنوات الخدمة
    if employee.join_date:
        years_of_service = (datetime.now().date() - employee.join_date).days / 365.25
        stats['years_of_service'] = round(years_of_service, 1)
    
    # عد الأجهزة المحمولة المخصصة
    from models import MobileDevice
    mobile_devices_count = MobileDevice.query.filter_by(employee_id=employee_id).count()
    stats['mobile_devices'] = mobile_devices_count
    
    # تنسيق التواريخ
    formatted_dates = {
        'hire_date': employee.join_date.strftime('%Y-%m-%d') if employee.join_date else 'غير محدد',
        'birth_date': employee.birth_date.strftime('%Y-%m-%d') if employee.birth_date else 'غير محدد',
        'id_expiry': getattr(employee, 'id_expiry_date', None).strftime('%Y-%m-%d') if getattr(employee, 'id_expiry_date', None) else 'غير محدد',
        'license_expiry': getattr(employee, 'license_expiry_date', None).strftime('%Y-%m-%d') if getattr(employee, 'license_expiry_date', None) else 'غير محدد',
        'passport_expiry': getattr(employee, 'passport_expiry_date', None).strftime('%Y-%m-%d') if getattr(employee, 'passport_expiry_date', None) else 'غير محدد'
    }
    
    return render_template('employee_portal/profile_enhanced.html',
                         employee=employee,
                         department=department,
                         assigned_vehicles=assigned_vehicles,
                         recent_attendance=recent_attendance,
                         salary_history=salary_history,
                         documents_status=documents_status,
                         stats=stats,
                         formatted_dates=formatted_dates)

@employee_portal_bp.route('/safety-check/<int:safety_check_id>')
@employee_login_required
def view_safety_check(safety_check_id):
    """عرض فحص السلامة للموظف بتصميم الموبايل"""
    employee_id = session.get('employee_id')
    employee = Employee.query.get_or_404(employee_id)
    
    # جلب فحص السلامة
    safety_check = VehicleSafetyCheck.query.get_or_404(safety_check_id)
    
    # التحقق من أن الموظف مخول لعرض هذا الفحص
    # يمكن للموظف عرض فحوصات السيارات المخصصة له
    latest_handovers = db.session.query(
        VehicleHandover.vehicle_id,
        func.max(VehicleHandover.handover_date).label('latest_date')
    ).filter(
        VehicleHandover.employee_id == employee_id,
        VehicleHandover.handover_type == 'delivery'
    ).group_by(VehicleHandover.vehicle_id).subquery()
    
    assigned_vehicle_ids = db.session.query(VehicleHandover.vehicle_id).join(
        latest_handovers, 
        and_(
            VehicleHandover.vehicle_id == latest_handovers.c.vehicle_id,
            VehicleHandover.handover_date == latest_handovers.c.latest_date
        )
    ).filter(
        VehicleHandover.employee_id == employee_id,
        VehicleHandover.handover_type == 'delivery'
    ).all()
    
    assigned_vehicle_ids = [v[0] for v in assigned_vehicle_ids]
    
    if safety_check.vehicle_id not in assigned_vehicle_ids:
        flash('غير مصرح لك بعرض هذا الفحص', 'error')
        return redirect(url_for('employee_portal.my_vehicles'))
    
    # جلب معلومات السيارة
    vehicle = Vehicle.query.get_or_404(safety_check.vehicle_id)
    
    return render_template('employee_portal/safety_check_view.html',
                         employee=employee,
                         safety_check=safety_check,
                         vehicle=vehicle)

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

@employee_portal_bp.route('/handover/<int:handover_id>')
def view_handover(handover_id):
    """عرض النموذج الإلكتروني - متاح للعرض العام"""
    handover = VehicleHandover.query.get_or_404(handover_id)
    vehicle = Vehicle.query.get_or_404(handover.vehicle_id)
    
    return render_template('employee_portal/handover_view.html', 
                         handover=handover, 
                         vehicle=vehicle)