from flask import Blueprint, request, jsonify, current_app
from flask_cors import cross_origin
from werkzeug.security import check_password_hash
import jwt
from datetime import datetime, timedelta
from functools import wraps
from models import (
    User, Employee, Department, Attendance, Salary, 
    Vehicle, VehicleHandover, Document, db
)
# من أجل التوافق مع النظام الحالي

api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# JWT Helper Functions
def generate_token(user_id, employee_id=None):
    """إنشاء JWT token"""
    payload = {
        'user_id': user_id,
        'employee_id': employee_id,
        'exp': datetime.utcnow() + timedelta(hours=24),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    """التحقق من JWT token"""
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def require_auth(f):
    """Decorator للتحقق من المصادقة"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token مطلوب'}), 401
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Token غير صالح أو منتهي الصلاحية'}), 401
        
        request.current_user_id = payload['user_id']
        request.current_employee_id = payload.get('employee_id')
        return f(*args, **kwargs)
    
    return decorated

# Authentication Endpoints
@api_bp.route('/auth/login', methods=['POST'])
@cross_origin()
def login():
    """تسجيل دخول المستخدمين العاديين"""
    data = request.get_json()
    
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'البريد الإلكتروني وكلمة المرور مطلوبان'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'error': 'بيانات تسجيل الدخول غير صحيحة'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'الحساب غير مفعل'}), 401
    
    token = generate_token(user.id)
    
    return jsonify({
        'token': token,
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'role': user.role,
            'department_id': user.department_id,
            'permissions': user.permissions
        }
    })

@api_bp.route('/auth/employee-login', methods=['POST'])
@cross_origin()
def employee_login():
    """تسجيل دخول الموظفين"""
    data = request.get_json()
    
    if not data or not data.get('employee_id') or not data.get('national_id'):
        return jsonify({'error': 'رقم الموظف والهوية الوطنية مطلوبان'}), 400
    
    employee = Employee.query.filter_by(
        employee_id=data['employee_id'],
        national_id=data['national_id']
    ).first()
    
    if not employee:
        return jsonify({'error': 'بيانات تسجيل الدخول غير صحيحة'}), 401
    
    if employee.status != 'active':
        return jsonify({'error': 'حساب الموظف غير مفعل'}), 401
    
    token = generate_token(None, employee.id)
    
    return jsonify({
        'token': token,
        'employee': {
            'id': employee.id,
            'name': employee.name,
            'employee_id': employee.employee_id,
            'department': employee.department.name if employee.department else None,
            'job_title': employee.job_title,
            'profile_image': employee.profile_image
        }
    })

@api_bp.route('/auth/verify', methods=['GET'])
@require_auth
@cross_origin()
def verify_token_endpoint():
    """التحقق من صحة Token"""
    if request.current_user_id:
        user = User.query.get(request.current_user_id)
        return jsonify({
            'valid': True,
            'user_type': 'user',
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'role': user.role
            }
        })
    elif request.current_employee_id:
        employee = Employee.query.get(request.current_employee_id)
        return jsonify({
            'valid': True,
            'user_type': 'employee',
            'employee': {
                'id': employee.id,
                'name': employee.name,
                'employee_id': employee.employee_id,
                'department': employee.department.name if employee.department else None
            }
        })

# Employee Endpoints
@api_bp.route('/employees', methods=['GET'])
@require_auth
@cross_origin()
def get_employees():
    """جلب قائمة الموظفين"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    department_id = request.args.get('department_id', type=int)
    
    query = Employee.query
    
    if search:
        query = query.filter(Employee.name.contains(search))
    
    if department_id:
        query = query.filter(Employee.department_id == department_id)
    
    employees = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'employees': [{
            'id': emp.id,
            'name': emp.name,
            'employee_id': emp.employee_id,
            'national_id': emp.national_id,
            'mobile': emp.mobile,
            'email': emp.email,
            'job_title': emp.job_title,
            'department': emp.department.name if emp.department else None,
            'status': emp.status,
            'join_date': emp.join_date.isoformat() if emp.join_date else None,
            'basic_salary': float(emp.basic_salary) if emp.basic_salary else None,
            'is_active': emp.status == 'active',
            'profile_image': emp.profile_image
        } for emp in employees.items],
        'pagination': {
            'page': employees.page,
            'pages': employees.pages,
            'per_page': employees.per_page,
            'total': employees.total,
            'has_next': employees.has_next,
            'has_prev': employees.has_prev
        }
    })

@api_bp.route('/employees/<int:employee_id>', methods=['GET'])
@require_auth
@cross_origin()
def get_employee(employee_id):
    """جلب بيانات موظف محدد"""
    employee = Employee.query.get_or_404(employee_id)
    
    return jsonify({
        'id': employee.id,
        'name': employee.name,
        'employee_id': employee.employee_id,
        'national_id': employee.national_id,
        'mobile': employee.mobile,
        'email': employee.email,
        'nationality': employee.nationality,
        'job_title': employee.job_title,
        'department': employee.department.name if employee.department else None,
        'department_id': employee.department_id,
        'status': employee.status,
        'contract_type': employee.contract_type,
        'join_date': employee.join_date.isoformat() if employee.join_date else None,
        'basic_salary': float(employee.basic_salary) if employee.basic_salary else None,
        'location': employee.location,
        'project': employee.project,
        'is_active': employee.status == 'active',
        'profile_image': employee.profile_image,
        'national_id_image': employee.national_id_image,
        'license_image': employee.license_image,
        'national_id': employee.national_id
    })

@api_bp.route('/employees', methods=['POST'])
@require_auth
@cross_origin()
def create_employee():
    """إنشاء موظف جديد"""
    data = request.get_json()
    
    if not data or not data.get('name') or not data.get('employee_id'):
        return jsonify({'error': 'الاسم ورقم الموظف مطلوبان'}), 400
    
    # التحقق من عدم تكرار رقم الموظف
    existing = Employee.query.filter_by(employee_id=data['employee_id']).first()
    if existing:
        return jsonify({'error': 'رقم الموظف موجود بالفعل'}), 400
    
    employee = Employee(
        name=data['name'],
        employee_id=data['employee_id'],
        national_id=data.get('national_id'),
        mobile=data.get('mobile'),
        email=data.get('email'),
        nationality=data.get('nationality'),
        job_title=data.get('job_title'),
        department_id=data.get('department_id'),
        status=data.get('status', 'نشط'),
        contract_type=data.get('contract_type'),
        join_date=datetime.fromisoformat(data['join_date']) if data.get('join_date') else None,
        basic_salary=data.get('basic_salary'),
        location=data.get('location'),
        project=data.get('project'),
        work_number=data.get('work_number'),
        is_active=data.get('is_active', True)
    )
    
    db.session.add(employee)
    db.session.commit()
    
    return jsonify({'message': 'تم إنشاء الموظف بنجاح', 'employee_id': employee.id}), 201

# Attendance Endpoints
@api_bp.route('/attendance', methods=['GET'])
@require_auth
@cross_origin()
def get_attendance():
    """جلب سجلات الحضور"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    employee_id = request.args.get('employee_id', type=int)
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    query = Attendance.query
    
    if employee_id:
        query = query.filter(Attendance.employee_id == employee_id)
    
    if date_from:
        query = query.filter(Attendance.date >= datetime.fromisoformat(date_from).date())
    
    if date_to:
        query = query.filter(Attendance.date <= datetime.fromisoformat(date_to).date())
    
    attendance_records = query.order_by(Attendance.date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'attendance': [{
            'id': att.id,
            'employee_id': att.employee_id,
            'employee_name': att.employee.name,
            'date': att.date.isoformat(),
            'check_in': att.check_in.isoformat() if att.check_in else None,
            'check_out': att.check_out.isoformat() if att.check_out else None,
            'status': att.status,
            'notes': att.notes,
            'overtime_hours': float(att.overtime_hours) if att.overtime_hours else 0,
            'late_minutes': att.late_minutes or 0
        } for att in attendance_records.items],
        'pagination': {
            'page': attendance_records.page,
            'pages': attendance_records.pages,
            'per_page': attendance_records.per_page,
            'total': attendance_records.total
        }
    })

@api_bp.route('/attendance/check-in', methods=['POST'])
@require_auth
@cross_origin()
def check_in():
    """تسجيل الحضور"""
    if not request.current_employee_id:
        return jsonify({'error': 'هذه الخدمة متاحة للموظفين فقط'}), 403
    
    data = request.get_json()
    today = datetime.now().date()
    
    # التحقق من عدم وجود تسجيل حضور لنفس اليوم
    existing = Attendance.query.filter_by(
        employee_id=request.current_employee_id,
        date=today
    ).first()
    
    if existing and existing.check_in:
        return jsonify({'error': 'تم تسجيل الحضور لهذا اليوم بالفعل'}), 400
    
    if existing:
        existing.check_in = datetime.now()
        existing.status = 'حاضر'
    else:
        attendance = Attendance(
            employee_id=request.current_employee_id,
            date=today,
            check_in=datetime.now(),
            status='حاضر'
        )
        db.session.add(attendance)
    
    db.session.commit()
    
    return jsonify({'message': 'تم تسجيل الحضور بنجاح'})

@api_bp.route('/attendance/check-out', methods=['POST'])
@require_auth
@cross_origin()
def check_out():
    """تسجيل الانصراف"""
    if not request.current_employee_id:
        return jsonify({'error': 'هذه الخدمة متاحة للموظفين فقط'}), 403
    
    today = datetime.now().date()
    
    attendance = Attendance.query.filter_by(
        employee_id=request.current_employee_id,
        date=today
    ).first()
    
    if not attendance or not attendance.check_in:
        return jsonify({'error': 'يجب تسجيل الحضور أولاً'}), 400
    
    if attendance.check_out:
        return jsonify({'error': 'تم تسجيل الانصراف لهذا اليوم بالفعل'}), 400
    
    attendance.check_out = datetime.now()
    db.session.commit()
    
    return jsonify({'message': 'تم تسجيل الانصراف بنجاح'})

# Vehicles Endpoints
@api_bp.route('/vehicles', methods=['GET'])
@require_auth
@cross_origin()
def get_vehicles():
    """جلب قائمة المركبات"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    status = request.args.get('status')
    
    query = Vehicle.query
    
    if search:
        query = query.filter(Vehicle.plate_number.contains(search))
    
    if status:
        query = query.filter(Vehicle.status == status)
    
    vehicles = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'vehicles': [{
            'id': veh.id,
            'plate_number': veh.plate_number,
            'model': veh.model,
            'year': veh.year,
            'color': veh.color,
            'type': veh.type,
            'status': veh.status,
            'driver_id': veh.driver_id,
            'driver_name': veh.driver.name if veh.driver else None,
            'insurance_expiry': veh.insurance_expiry.isoformat() if veh.insurance_expiry else None,
            'license_expiry': veh.license_expiry.isoformat() if veh.license_expiry else None,
            'maintenance_due': veh.maintenance_due.isoformat() if veh.maintenance_due else None
        } for veh in vehicles.items],
        'pagination': {
            'page': vehicles.page,
            'pages': vehicles.pages,
            'per_page': vehicles.per_page,
            'total': vehicles.total
        }
    })

@api_bp.route('/employees/<int:employee_id>/vehicles', methods=['GET'])
@require_auth
@cross_origin()
def get_employee_vehicles(employee_id):
    """جلب مركبات موظف محدد"""
    # التحقق من الصلاحية - الموظف يمكنه رؤية مركباته فقط
    if request.current_employee_id and request.current_employee_id != employee_id:
        return jsonify({'error': 'غير مصرح لك بالوصول لهذه البيانات'}), 403
    
    handovers = VehicleHandover.query.filter_by(
        employee_id=employee_id,
        handover_type='تسليم'
    ).all()
    
    vehicles = []
    for handover in handovers:
        # التحقق من عدم وجود استلام لاحق
        return_handover = VehicleHandover.query.filter(
            VehicleHandover.vehicle_id == handover.vehicle_id,
            VehicleHandover.employee_id == employee_id,
            VehicleHandover.handover_type == 'استلام',
            VehicleHandover.handover_date > handover.handover_date
        ).first()
        
        if not return_handover and handover.vehicle:
            vehicles.append({
                'id': handover.vehicle.id,
                'plate_number': handover.vehicle.plate_number,
                'model': handover.vehicle.model,
                'year': handover.vehicle.year,
                'color': handover.vehicle.color,
                'type': handover.vehicle.type,
                'handover_date': handover.handover_date.isoformat(),
                'handover_notes': handover.notes
            })
    
    return jsonify({'vehicles': vehicles})

# Salary Endpoints
@api_bp.route('/employees/<int:employee_id>/salaries', methods=['GET'])
@require_auth
@cross_origin()
def get_employee_salaries(employee_id):
    """جلب رواتب موظف محدد"""
    # التحقق من الصلاحية
    if request.current_employee_id and request.current_employee_id != employee_id:
        return jsonify({'error': 'غير مصرح لك بالوصول لهذه البيانات'}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    
    salaries = Salary.query.filter_by(employee_id=employee_id).order_by(
        Salary.year.desc(), Salary.month.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'salaries': [{
            'id': sal.id,
            'month': sal.month,
            'year': sal.year,
            'basic_salary': float(sal.basic_salary) if sal.basic_salary else 0,
            'allowances': float(sal.allowances) if sal.allowances else 0,
            'overtime': float(sal.overtime) if sal.overtime else 0,
            'deductions': float(sal.deductions) if sal.deductions else 0,
            'net_salary': float(sal.net_salary) if sal.net_salary else 0,
            'status': sal.status,
            'payment_date': sal.payment_date.isoformat() if sal.payment_date else None
        } for sal in salaries.items],
        'pagination': {
            'page': salaries.page,
            'pages': salaries.pages,
            'total': salaries.total
        }
    })

# Departments Endpoints
@api_bp.route('/departments', methods=['GET'])
@require_auth
@cross_origin()
def get_departments():
    """جلب قائمة الأقسام"""
    departments = Department.query.all()
    
    return jsonify({
        'departments': [{
            'id': dept.id,
            'name': dept.name,
            'description': dept.description,
            'manager_id': dept.manager_id,
            'manager_name': dept.manager.name if dept.manager else None,
            'employees_count': len(dept.employees)
        } for dept in departments]
    })

# Documents Endpoints
@api_bp.route('/employees/<int:employee_id>/documents', methods=['GET'])
@require_auth
@cross_origin()
def get_employee_documents(employee_id):
    """جلب وثائق موظف محدد"""
    # التحقق من الصلاحية
    if request.current_employee_id and request.current_employee_id != employee_id:
        return jsonify({'error': 'غير مصرح لك بالوصول لهذه البيانات'}), 403
    
    documents = Document.query.filter_by(employee_id=employee_id).all()
    
    return jsonify({
        'documents': [{
            'id': doc.id,
            'title': doc.title,
            'type': doc.type,
            'file_path': doc.file_path,
            'upload_date': doc.upload_date.isoformat(),
            'file_size': doc.file_size,
            'description': doc.description
        } for doc in documents]
    })

# Statistics Endpoints
@api_bp.route('/dashboard/stats', methods=['GET'])
@require_auth
@cross_origin()
def get_dashboard_stats():
    """إحصائيات لوحة التحكم"""
    today = datetime.now().date()
    
    stats = {
        'total_employees': Employee.query.filter_by(status='active').count(),
        'total_departments': Department.query.count(),
        'total_vehicles': Vehicle.query.count(),
        'today_attendance': Attendance.query.filter_by(date=today).count(),
        'present_today': Attendance.query.filter_by(date=today, status='حاضر').count(),
        'absent_today': Attendance.query.filter_by(date=today, status='غائب').count(),
        'vehicles_in_use': Vehicle.query.filter_by(status='قيد الاستخدام').count(),
        'vehicles_available': Vehicle.query.filter_by(status='متاح').count()
    }
    
    return jsonify(stats)

# Employee Portal Specific Endpoints
@api_bp.route('/employee/profile', methods=['GET'])
@require_auth
@cross_origin()
def get_employee_profile():
    """ملف الموظف الشخصي"""
    if not request.current_employee_id:
        return jsonify({'error': 'هذه الخدمة متاحة للموظفين فقط'}), 403
    
    employee = Employee.query.get_or_404(request.current_employee_id)
    
    return jsonify({
        'id': employee.id,
        'name': employee.name,
        'employee_id': employee.employee_id,
        'national_id': employee.national_id,
        'mobile': employee.mobile,
        'email': employee.email,
        'job_title': employee.job_title,
        'department': employee.department.name if employee.department else None,
        'join_date': employee.join_date.isoformat() if employee.join_date else None,
        'profile_image': employee.profile_image,
        'national_id_image': employee.national_id_image,
        'license_image': employee.license_image
    })

@api_bp.route('/employee/attendance/summary', methods=['GET'])
@require_auth
@cross_origin()
def get_employee_attendance_summary():
    """ملخص حضور الموظف"""
    if not request.current_employee_id:
        return jsonify({'error': 'هذه الخدمة متاحة للموظفين فقط'}), 403
    
    # إحصائيات الشهر الحالي
    now = datetime.now()
    first_day = now.replace(day=1).date()
    
    monthly_attendance = Attendance.query.filter(
        Attendance.employee_id == request.current_employee_id,
        Attendance.date >= first_day
    ).all()
    
    present_days = len([att for att in monthly_attendance if att.status == 'حاضر'])
    absent_days = len([att for att in monthly_attendance if att.status == 'غائب'])
    late_days = len([att for att in monthly_attendance if att.late_minutes and att.late_minutes > 0])
    
    # حضور اليوم
    today = datetime.now().date()
    today_attendance = Attendance.query.filter_by(
        employee_id=request.current_employee_id,
        date=today
    ).first()
    
    return jsonify({
        'monthly_summary': {
            'present_days': present_days,
            'absent_days': absent_days,
            'late_days': late_days,
            'total_days': len(monthly_attendance)
        },
        'today_status': {
            'checked_in': bool(today_attendance and today_attendance.check_in),
            'checked_out': bool(today_attendance and today_attendance.check_out),
            'check_in_time': today_attendance.check_in.isoformat() if today_attendance and today_attendance.check_in else None,
            'check_out_time': today_attendance.check_out.isoformat() if today_attendance and today_attendance.check_out else None
        }
    })

# Users Management Endpoints
@api_bp.route('/users', methods=['GET'])
@require_auth
@cross_origin()
def get_users():
    """جلب قائمة المستخدمين"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    users = User.query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'users': [{
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'role': user.role,
            'department_id': user.department_id,
            'department_name': user.department.name if user.department else None,
            'is_active': user.is_active,
            'permissions': user.permissions,
            'created_at': user.created_at.isoformat() if user.created_at else None
        } for user in users.items],
        'pagination': {
            'page': users.page,
            'pages': users.pages,
            'per_page': users.per_page,
            'total': users.total
        }
    })

@api_bp.route('/users/<int:user_id>', methods=['GET'])
@require_auth
@cross_origin()
def get_user(user_id):
    """جلب بيانات مستخدم محدد"""
    user = User.query.get_or_404(user_id)
    
    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'role': user.role,
        'department_id': user.department_id,
        'department_name': user.department.name if user.department else None,
        'is_active': user.is_active,
        'permissions': user.permissions,
        'created_at': user.created_at.isoformat() if user.created_at else None
    })

@api_bp.route('/users', methods=['POST'])
@require_auth
@cross_origin()
def create_user():
    """إنشاء مستخدم جديد"""
    data = request.get_json()
    
    if not data or not data.get('name') or not data.get('email'):
        return jsonify({'error': 'الاسم والبريد الإلكتروني مطلوبان'}), 400
    
    # التحقق من عدم تكرار البريد الإلكتروني
    existing = User.query.filter_by(email=data['email']).first()
    if existing:
        return jsonify({'error': 'البريد الإلكتروني موجود بالفعل'}), 400
    
    from werkzeug.security import generate_password_hash
    
    user = User(
        name=data['name'],
        email=data['email'],
        password_hash=generate_password_hash(data.get('password', '123456')),
        role=data.get('role', 'user'),
        department_id=data.get('department_id'),
        permissions=data.get('permissions', 0),
        is_active=data.get('is_active', True)
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({'message': 'تم إنشاء المستخدم بنجاح', 'user_id': user.id}), 201

# Reports and Analytics Endpoints
@api_bp.route('/reports/employees/summary', methods=['GET'])
@require_auth
@cross_origin()
def employees_summary_report():
    """تقرير ملخص الموظفين"""
    department_id = request.args.get('department_id', type=int)
    
    query = Employee.query
    if department_id:
        query = query.filter(Employee.department_id == department_id)
    
    employees = query.all()
    
    # إحصائيات حسب الحالة
    status_stats = {}
    for emp in employees:
        status = emp.status or 'غير محدد'
        status_stats[status] = status_stats.get(status, 0) + 1
    
    # إحصائيات حسب القسم
    department_stats = {}
    for emp in employees:
        dept_name = emp.department.name if emp.department else 'بدون قسم'
        department_stats[dept_name] = department_stats.get(dept_name, 0) + 1
    
    # إحصائيات حسب الجنسية
    nationality_stats = {}
    for emp in employees:
        nationality = emp.nationality or 'غير محدد'
        nationality_stats[nationality] = nationality_stats.get(nationality, 0) + 1
    
    return jsonify({
        'total_employees': len(employees),
        'status_breakdown': status_stats,
        'department_breakdown': department_stats,
        'nationality_breakdown': nationality_stats,
        'average_salary': sum(emp.basic_salary or 0 for emp in employees) / len(employees) if employees else 0
    })

@api_bp.route('/reports/attendance/monthly', methods=['GET'])
@require_auth
@cross_origin()
def monthly_attendance_report():
    """تقرير الحضور الشهري"""
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', datetime.now().month, type=int)
    department_id = request.args.get('department_id', type=int)
    
    from calendar import monthrange
    start_date = datetime(year, month, 1).date()
    end_date = datetime(year, month, monthrange(year, month)[1]).date()
    
    query = Attendance.query.filter(
        Attendance.date >= start_date,
        Attendance.date <= end_date
    )
    
    if department_id:
        query = query.join(Employee).filter(Employee.department_id == department_id)
    
    attendances = query.all()
    
    # إحصائيات الحضور
    total_records = len(attendances)
    present_count = len([att for att in attendances if att.status == 'حاضر'])
    absent_count = len([att for att in attendances if att.status == 'غائب'])
    late_count = len([att for att in attendances if att.late_minutes and att.late_minutes > 0])
    
    # إحصائيات يومية
    daily_stats = {}
    for att in attendances:
        date_str = att.date.isoformat()
        if date_str not in daily_stats:
            daily_stats[date_str] = {'present': 0, 'absent': 0, 'late': 0}
        
        daily_stats[date_str][att.status] = daily_stats[date_str].get(att.status, 0) + 1
        if att.late_minutes and att.late_minutes > 0:
            daily_stats[date_str]['late'] += 1
    
    return jsonify({
        'period': f'{year}-{month:02d}',
        'total_records': total_records,
        'present_count': present_count,
        'absent_count': absent_count,
        'late_count': late_count,
        'attendance_rate': (present_count / total_records * 100) if total_records > 0 else 0,
        'daily_breakdown': daily_stats
    })

@api_bp.route('/reports/vehicles/status', methods=['GET'])
@require_auth
@cross_origin()
def vehicles_status_report():
    """تقرير حالة المركبات"""
    vehicles = Vehicle.query.all()
    
    # إحصائيات حسب الحالة
    status_stats = {}
    for vehicle in vehicles:
        status = vehicle.status or 'غير محدد'
        status_stats[status] = status_stats.get(status, 0) + 1
    
    # إحصائيات حسب النوع
    type_stats = {}
    for vehicle in vehicles:
        vehicle_type = vehicle.type or 'غير محدد'
        type_stats[vehicle_type] = type_stats.get(vehicle_type, 0) + 1
    
    # المركبات المنتهية الصلاحية أو قريبة من الانتهاء
    from datetime import timedelta
    today = datetime.now().date()
    warning_date = today + timedelta(days=30)
    
    expiring_insurance = [v for v in vehicles if v.insurance_expiry and v.insurance_expiry <= warning_date]
    expiring_license = [v for v in vehicles if v.license_expiry and v.license_expiry <= warning_date]
    
    return jsonify({
        'total_vehicles': len(vehicles),
        'status_breakdown': status_stats,
        'type_breakdown': type_stats,
        'expiring_insurance': [{
            'id': v.id,
            'plate_number': v.plate_number,
            'insurance_expiry': v.insurance_expiry.isoformat(),
            'days_remaining': (v.insurance_expiry - today).days
        } for v in expiring_insurance],
        'expiring_license': [{
            'id': v.id,
            'plate_number': v.plate_number,
            'license_expiry': v.license_expiry.isoformat(),
            'days_remaining': (v.license_expiry - today).days
        } for v in expiring_license]
    })

@api_bp.route('/reports/salaries/summary', methods=['GET'])
@require_auth
@cross_origin()
def salaries_summary_report():
    """تقرير ملخص الرواتب"""
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', datetime.now().month, type=int)
    department_id = request.args.get('department_id', type=int)
    
    query = Salary.query.filter(Salary.year == year, Salary.month == month)
    
    if department_id:
        query = query.join(Employee).filter(Employee.department_id == department_id)
    
    salaries = query.all()
    
    if not salaries:
        return jsonify({
            'period': f'{year}-{month:02d}',
            'total_employees': 0,
            'total_basic_salary': 0,
            'total_allowances': 0,
            'total_deductions': 0,
            'total_net_salary': 0,
            'average_salary': 0,
            'payment_status': {}
        })
    
    total_basic = sum(sal.basic_salary or 0 for sal in salaries)
    total_allowances = sum(sal.allowances or 0 for sal in salaries)
    total_deductions = sum(sal.deductions or 0 for sal in salaries)
    total_net = sum(sal.net_salary or 0 for sal in salaries)
    
    # إحصائيات حالة الدفع
    payment_stats = {}
    for sal in salaries:
        status = sal.status or 'غير محدد'
        payment_stats[status] = payment_stats.get(status, 0) + 1
    
    return jsonify({
        'period': f'{year}-{month:02d}',
        'total_employees': len(salaries),
        'total_basic_salary': total_basic,
        'total_allowances': total_allowances,
        'total_deductions': total_deductions,
        'total_net_salary': total_net,
        'average_salary': total_net / len(salaries),
        'payment_status': payment_stats
    })

# Advanced Search and Filtering
@api_bp.route('/search', methods=['POST'])
@require_auth
@cross_origin()
def advanced_search():
    """البحث المتقدم في جميع البيانات"""
    data = request.get_json()
    query = data.get('query', '').strip()
    filters = data.get('filters', {})
    
    if not query:
        return jsonify({'error': 'نص البحث مطلوب'}), 400
    
    results = {
        'employees': [],
        'vehicles': [],
        'departments': []
    }
    
    # البحث في الموظفين
    employee_query = Employee.query.filter(
        Employee.name.contains(query) |
        Employee.employee_id.contains(query) |
        Employee.national_id.contains(query) |
        Employee.mobile.contains(query)
    )
    
    if filters.get('department_id'):
        employee_query = employee_query.filter(Employee.department_id == filters['department_id'])
    
    employees = employee_query.limit(10).all()
    results['employees'] = [{
        'id': emp.id,
        'name': emp.name,
        'employee_id': emp.employee_id,
        'department': emp.department.name if emp.department else None,
        'job_title': emp.job_title,
        'mobile': emp.mobile
    } for emp in employees]
    
    # البحث في المركبات
    vehicle_query = Vehicle.query.filter(
        Vehicle.plate_number.contains(query) |
        Vehicle.model.contains(query)
    )
    
    vehicles = vehicle_query.limit(10).all()
    results['vehicles'] = [{
        'id': veh.id,
        'plate_number': veh.plate_number,
        'model': veh.model,
        'year': veh.year,
        'status': veh.status,
        'driver_name': veh.driver.name if veh.driver else None
    } for veh in vehicles]
    
    # البحث في الأقسام
    departments = Department.query.filter(Department.name.contains(query)).limit(5).all()
    results['departments'] = [{
        'id': dept.id,
        'name': dept.name,
        'description': dept.description,
        'employees_count': len(dept.employees)
    } for dept in departments]
    
    return jsonify(results)

# Notifications and System Messages
@api_bp.route('/notifications', methods=['GET'])
@require_auth
@cross_origin()
def get_notifications():
    """جلب الإشعارات"""
    # إنشاء إشعارات ديناميكية بناءً على حالة النظام
    notifications = []
    
    # إشعارات انتهاء صلاحية التأمين
    from datetime import timedelta
    today = datetime.now().date()
    warning_date = today + timedelta(days=30)
    
    expiring_vehicles = Vehicle.query.filter(
        Vehicle.insurance_expiry <= warning_date,
        Vehicle.insurance_expiry >= today
    ).all()
    
    for vehicle in expiring_vehicles:
        days_remaining = (vehicle.insurance_expiry - today).days
        notifications.append({
            'type': 'warning',
            'title': 'انتهاء صلاحية التأمين',
            'message': f'تأمين المركبة {vehicle.plate_number} ينتهي خلال {days_remaining} يوم',
            'entity_type': 'vehicle',
            'entity_id': vehicle.id,
            'created_at': datetime.now().isoformat()
        })
    
    # إشعارات الموظفين الجدد
    new_employees = Employee.query.filter(
        Employee.created_at >= datetime.now() - timedelta(days=7)
    ).all()
    
    for emp in new_employees:
        notifications.append({
            'type': 'info',
            'title': 'موظف جديد',
            'message': f'انضم الموظف {emp.name} للنظام',
            'entity_type': 'employee',
            'entity_id': emp.id,
            'created_at': emp.created_at.isoformat()
        })
    
    # ترتيب الإشعارات حسب التاريخ
    notifications.sort(key=lambda x: x['created_at'], reverse=True)
    
    return jsonify({
        'notifications': notifications[:20],  # آخر 20 إشعار
        'unread_count': len(notifications)
    })

# System Settings and Configuration
@api_bp.route('/settings', methods=['GET'])
@require_auth
@cross_origin()
def get_system_settings():
    """جلب إعدادات النظام"""
    settings = {
        'system_name': 'نظام نُظم',
        'version': '2.0.0',
        'attendance_settings': {
            'work_start_time': '08:00',
            'work_end_time': '16:00',
            'late_threshold_minutes': 15,
            'overtime_threshold_hours': 8
        },
        'salary_settings': {
            'currency': 'ريال سعودي',
            'default_allowances': 500.0,
            'overtime_rate_multiplier': 1.5
        },
        'vehicle_settings': {
            'insurance_warning_days': 30,
            'maintenance_warning_days': 15
        }
    }
    
    return jsonify(settings)

# Bulk Operations
@api_bp.route('/bulk/attendance', methods=['POST'])
@require_auth
@cross_origin()
def bulk_attendance_operation():
    """عمليات جماعية للحضور"""
    data = request.get_json()
    operation = data.get('operation')
    employee_ids = data.get('employee_ids', [])
    date = data.get('date', datetime.now().date().isoformat())
    
    if not operation or not employee_ids:
        return jsonify({'error': 'نوع العملية وقائمة الموظفين مطلوبة'}), 400
    
    target_date = datetime.fromisoformat(date).date()
    results = {'success': 0, 'failed': 0, 'errors': []}
    
    if operation == 'mark_present':
        for emp_id in employee_ids:
            try:
                # التحقق من عدم وجود سجل حضور
                existing = Attendance.query.filter_by(
                    employee_id=emp_id,
                    date=target_date
                ).first()
                
                if existing:
                    existing.status = 'حاضر'
                    existing.check_in = datetime.combine(target_date, datetime.strptime('08:00', '%H:%M').time())
                else:
                    attendance = Attendance(
                        employee_id=emp_id,
                        date=target_date,
                        status='حاضر',
                        check_in=datetime.combine(target_date, datetime.strptime('08:00', '%H:%M').time())
                    )
                    db.session.add(attendance)
                
                results['success'] += 1
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f'Employee {emp_id}: {str(e)}')
    
    elif operation == 'mark_absent':
        for emp_id in employee_ids:
            try:
                existing = Attendance.query.filter_by(
                    employee_id=emp_id,
                    date=target_date
                ).first()
                
                if existing:
                    existing.status = 'غائب'
                    existing.check_in = None
                    existing.check_out = None
                else:
                    attendance = Attendance(
                        employee_id=emp_id,
                        date=target_date,
                        status='غائب'
                    )
                    db.session.add(attendance)
                
                results['success'] += 1
            except Exception as e:
                results['failed'] += 1
                results['errors'].append(f'Employee {emp_id}: {str(e)}')
    
    db.session.commit()
    
    return jsonify({
        'message': f'تم تنفيذ العملية بنجاح. نجح: {results["success"]}, فشل: {results["failed"]}',
        'results': results
    })

# Document Management
@api_bp.route('/documents/upload', methods=['POST'])
@require_auth
@cross_origin()
def upload_document():
    """رفع وثيقة جديدة"""
    if 'file' not in request.files:
        return jsonify({'error': 'لم يتم اختيار ملف'}), 400
    
    file = request.files['file']
    employee_id = request.form.get('employee_id', type=int)
    document_type = request.form.get('document_type', 'other')
    description = request.form.get('description', '')
    
    if not employee_id:
        return jsonify({'error': 'معرف الموظف مطلوب'}), 400
    
    if file.filename == '':
        return jsonify({'error': 'لم يتم اختيار ملف'}), 400
    
    # التحقق من وجود الموظف
    employee = Employee.query.get(employee_id)
    if not employee:
        return jsonify({'error': 'الموظف غير موجود'}), 404
    
    # حفظ الملف (يتطلب تنفيذ دالة حفظ الملفات)
    # file_path = save_uploaded_file(file, employee_id, document_type)
    
    # إنشاء سجل الوثيقة
    document = Document(
        employee_id=employee_id,
        title=file.filename,
        type=document_type,
        file_path=f'/uploads/documents/{employee_id}/{file.filename}',
        file_size=len(file.read()),
        description=description
    )
    
    db.session.add(document)
    db.session.commit()
    
    return jsonify({
        'message': 'تم رفع الوثيقة بنجاح',
        'document_id': document.id
    }), 201

# Vehicle Handover Management
@api_bp.route('/vehicle-handovers', methods=['GET'])
@require_auth
@cross_origin()
def get_vehicle_handovers():
    """جلب سجلات تسليم واستلام المركبات"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    vehicle_id = request.args.get('vehicle_id', type=int)
    employee_id = request.args.get('employee_id', type=int)
    handover_type = request.args.get('handover_type')
    
    query = VehicleHandover.query
    
    if vehicle_id:
        query = query.filter(VehicleHandover.vehicle_id == vehicle_id)
    
    if employee_id:
        query = query.filter(VehicleHandover.employee_id == employee_id)
    
    if handover_type:
        query = query.filter(VehicleHandover.handover_type == handover_type)
    
    handovers = query.order_by(VehicleHandover.handover_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return jsonify({
        'handovers': [{
            'id': handover.id,
            'vehicle_id': handover.vehicle_id,
            'vehicle_plate': handover.vehicle.plate_number if handover.vehicle else None,
            'employee_id': handover.employee_id,
            'employee_name': handover.employee_rel.name if handover.employee_rel else None,
            'handover_type': handover.handover_type,
            'handover_date': handover.handover_date.isoformat(),
            'notes': handover.notes,
            'created_at': handover.created_at.isoformat() if handover.created_at else None
        } for handover in handovers.items],
        'pagination': {
            'page': handovers.page,
            'pages': handovers.pages,
            'per_page': handovers.per_page,
            'total': handovers.total
        }
    })

@api_bp.route('/vehicle-handovers', methods=['POST'])
@require_auth
@cross_origin()
def create_vehicle_handover():
    """إنشاء سجل تسليم/استلام مركبة"""
    data = request.get_json()
    
    required_fields = ['vehicle_id', 'employee_id', 'handover_type', 'handover_date']
    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} مطلوب'}), 400
    
    # التحقق من وجود المركبة والموظف
    vehicle = Vehicle.query.get(data['vehicle_id'])
    employee = Employee.query.get(data['employee_id'])
    
    if not vehicle:
        return jsonify({'error': 'المركبة غير موجودة'}), 404
    
    if not employee:
        return jsonify({'error': 'الموظف غير موجود'}), 404
    
    handover = VehicleHandover(
        vehicle_id=data['vehicle_id'],
        employee_id=data['employee_id'],
        handover_type=data['handover_type'],
        handover_date=datetime.fromisoformat(data['handover_date']),
        notes=data.get('notes', '')
    )
    
    # تحديث حالة المركبة حسب نوع العملية
    if data['handover_type'] == 'تسليم':
        vehicle.status = 'قيد الاستخدام'
        vehicle.driver_id = data['employee_id']
    elif data['handover_type'] == 'استلام':
        vehicle.status = 'متاح'
        vehicle.driver_id = None
    
    db.session.add(handover)
    db.session.commit()
    
    return jsonify({'message': 'تم تسجيل العملية بنجاح', 'handover_id': handover.id}), 201

# System Audit and Logs
@api_bp.route('/audit-logs', methods=['GET'])
@require_auth
@cross_origin()
def get_audit_logs():
    """جلب سجلات العمليات والتدقيق"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    action = request.args.get('action')
    entity_type = request.args.get('entity_type')
    user_id = request.args.get('user_id', type=int)
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    # نموذج بسيط للعمليات المحفوظة
    logs = []
    
    # يمكن إضافة جدول SystemAudit لاحقاً
    # هنا نعرض العمليات الأخيرة من جلسة المستخدم الحالية
    recent_operations = [
        {
            'id': 1,
            'user_id': request.current_user_id if hasattr(request, 'current_user_id') else None,
            'action': 'login',
            'entity_type': 'user',
            'entity_id': None,
            'details': 'تسجيل دخول بنجاح',
            'timestamp': datetime.now().isoformat(),
            'ip_address': request.remote_addr
        }
    ]
    
    return jsonify({
        'logs': recent_operations,
        'pagination': {
            'page': 1,
            'pages': 1,
            'per_page': per_page,
            'total': len(recent_operations)
        }
    })

# Advanced Analytics
@api_bp.route('/analytics/employee-performance', methods=['GET'])
@require_auth
@cross_origin()
def employee_performance_analytics():
    """تحليلات أداء الموظفين"""
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', type=int)
    department_id = request.args.get('department_id', type=int)
    
    # استعلام بيانات الحضور
    query = Attendance.query.filter(Attendance.date >= datetime(year, 1, 1).date())
    
    if month:
        query = query.filter(
            Attendance.date >= datetime(year, month, 1).date(),
            Attendance.date < datetime(year, month + 1, 1).date() if month < 12 else datetime(year + 1, 1, 1).date()
        )
    
    if department_id:
        query = query.join(Employee).filter(Employee.department_id == department_id)
    
    attendances = query.all()
    
    # تحليل البيانات
    employee_stats = {}
    for att in attendances:
        emp_id = att.employee_id
        if emp_id not in employee_stats:
            employee_stats[emp_id] = {
                'employee_name': att.employee.name,
                'total_days': 0,
                'present_days': 0,
                'absent_days': 0,
                'late_days': 0,
                'overtime_hours': 0
            }
        
        employee_stats[emp_id]['total_days'] += 1
        
        if att.status == 'حاضر':
            employee_stats[emp_id]['present_days'] += 1
        elif att.status == 'غائب':
            employee_stats[emp_id]['absent_days'] += 1
        
        if att.late_minutes and att.late_minutes > 0:
            employee_stats[emp_id]['late_days'] += 1
        
        if att.overtime_hours:
            employee_stats[emp_id]['overtime_hours'] += att.overtime_hours
    
    # حساب معدلات الأداء
    performance_data = []
    for emp_id, stats in employee_stats.items():
        if stats['total_days'] > 0:
            attendance_rate = (stats['present_days'] / stats['total_days']) * 100
            punctuality_rate = ((stats['total_days'] - stats['late_days']) / stats['total_days']) * 100
            
            performance_data.append({
                'employee_id': emp_id,
                'employee_name': stats['employee_name'],
                'attendance_rate': round(attendance_rate, 2),
                'punctuality_rate': round(punctuality_rate, 2),
                'total_days': stats['total_days'],
                'present_days': stats['present_days'],
                'absent_days': stats['absent_days'],
                'late_days': stats['late_days'],
                'overtime_hours': round(stats['overtime_hours'], 2)
            })
    
    # ترتيب حسب معدل الحضور
    performance_data.sort(key=lambda x: x['attendance_rate'], reverse=True)
    
    return jsonify({
        'period': f'{year}' + (f'-{month:02d}' if month else ''),
        'total_employees_analyzed': len(performance_data),
        'performance_data': performance_data,
        'summary': {
            'avg_attendance_rate': sum(p['attendance_rate'] for p in performance_data) / len(performance_data) if performance_data else 0,
            'avg_punctuality_rate': sum(p['punctuality_rate'] for p in performance_data) / len(performance_data) if performance_data else 0,
            'total_overtime_hours': sum(p['overtime_hours'] for p in performance_data)
        }
    })

# Financial Reports
@api_bp.route('/reports/financial/payroll', methods=['GET'])
@require_auth
@cross_origin()
def payroll_financial_report():
    """تقرير كشف الرواتب المالي"""
    year = request.args.get('year', datetime.now().year, type=int)
    month = request.args.get('month', datetime.now().month, type=int)
    department_id = request.args.get('department_id', type=int)
    
    query = Salary.query.filter(Salary.year == year, Salary.month == month)
    
    if department_id:
        query = query.join(Employee).filter(Employee.department_id == department_id)
    
    salaries = query.all()
    
    # تجميع البيانات المالية
    payroll_data = []
    total_gross = 0
    total_deductions = 0
    total_net = 0
    
    for salary in salaries:
        gross_salary = (salary.basic_salary or 0) + (salary.allowances or 0) + (salary.bonus or 0)
        deductions = salary.deductions or 0
        net_salary = gross_salary - deductions
        
        total_gross += gross_salary
        total_deductions += deductions
        total_net += net_salary
        
        payroll_data.append({
            'employee_id': salary.employee.employee_id,
            'employee_name': salary.employee.name,
            'department': salary.employee.department.name if salary.employee.department else 'غير محدد',
            'basic_salary': salary.basic_salary or 0,
            'allowances': salary.allowances or 0,
            'bonus': salary.bonus or 0,
            'gross_salary': gross_salary,
            'deductions': deductions,
            'net_salary': net_salary,
            'payment_status': salary.status or 'غير محدد',
            'payment_date': salary.payment_date.isoformat() if salary.payment_date else None
        })
    
    return jsonify({
        'period': f'{year}-{month:02d}',
        'payroll_summary': {
            'total_employees': len(payroll_data),
            'total_gross_salary': total_gross,
            'total_deductions': total_deductions,
            'total_net_salary': total_net,
            'average_salary': total_net / len(payroll_data) if payroll_data else 0
        },
        'payroll_details': payroll_data,
        'department_breakdown': self._get_payroll_by_department(salaries) if salaries else {}
    })

def _get_payroll_by_department(salaries):
    """تجميع الرواتب حسب القسم"""
    dept_totals = {}
    for salary in salaries:
        dept_name = salary.employee.department.name if salary.employee.department else 'غير محدد'
        if dept_name not in dept_totals:
            dept_totals[dept_name] = {'employees': 0, 'total_net': 0}
        
        dept_totals[dept_name]['employees'] += 1
        dept_totals[dept_name]['total_net'] += salary.net_salary or 0
    
    return dept_totals

# Employee Timeline
@api_bp.route('/employees/<int:employee_id>/timeline', methods=['GET'])
@require_auth
@cross_origin()
def get_employee_timeline(employee_id):
    """جلب الخط الزمني لأنشطة الموظف"""
    employee = Employee.query.get_or_404(employee_id)
    
    timeline_events = []
    
    # إضافة تاريخ الالتحاق
    if employee.join_date:
        timeline_events.append({
            'date': employee.join_date.isoformat(),
            'type': 'join',
            'title': 'التحق بالعمل',
            'description': f'انضم {employee.name} للشركة',
            'icon': 'user-plus'
        })
    
    # إضافة آخر سجلات الحضور
    recent_attendance = Attendance.query.filter_by(employee_id=employee_id).order_by(
        Attendance.date.desc()
    ).limit(10).all()
    
    for att in recent_attendance:
        timeline_events.append({
            'date': att.date.isoformat(),
            'type': 'attendance',
            'title': f'حضور - {att.status}',
            'description': f'حضور: {att.check_in.strftime("%H:%M") if att.check_in else "لم يسجل"}, انصراف: {att.check_out.strftime("%H:%M") if att.check_out else "لم يسجل"}',
            'icon': 'clock'
        })
    
    # إضافة سجلات تسليم المركبات
    vehicle_handovers = VehicleHandover.query.filter_by(employee_id=employee_id).order_by(
        VehicleHandover.handover_date.desc()
    ).limit(5).all()
    
    for handover in vehicle_handovers:
        timeline_events.append({
            'date': handover.handover_date.isoformat(),
            'type': 'vehicle',
            'title': f'{handover.handover_type} مركبة',
            'description': f'{handover.handover_type} مركبة {handover.vehicle.plate_number if handover.vehicle else "غير محدد"}',
            'icon': 'truck'
        })
    
    # ترتيب الأحداث حسب التاريخ
    timeline_events.sort(key=lambda x: x['date'], reverse=True)
    
    return jsonify({
        'employee': {
            'id': employee.id,
            'name': employee.name,
            'employee_id': employee.employee_id
        },
        'timeline': timeline_events[:20]  # آخر 20 حدث
    })

# Error Handlers
@api_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'المورد غير موجود'}), 404

@api_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'خطأ داخلي في الخادم'}), 500