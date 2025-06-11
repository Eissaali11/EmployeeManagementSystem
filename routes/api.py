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
        'total_employees': Employee.query.filter_by(is_active=True).count(),
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

# Error Handlers
@api_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'المورد غير موجود'}), 404

@api_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'خطأ داخلي في الخادم'}), 500