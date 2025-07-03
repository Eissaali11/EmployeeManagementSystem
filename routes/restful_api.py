"""
RESTful API Routes for نُظم Employee Management System
نظام إدارة الموظفين - مسارات API الشاملة
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import current_user, login_required
from functools import wraps
from datetime import datetime, timedelta
import jwt
import logging
from sqlalchemy import and_, or_, desc, func, extract
from sqlalchemy.orm import joinedload
from app import db
from models import (
    User, Employee, Vehicle, Department, Attendance, 
    Salary, AuditLog, VehicleHandover, VehicleWorkshop
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# JWT Secret Key
JWT_SECRET_KEY = 'nuzum-api-secret-key-2024'
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_DELTA = timedelta(hours=24)

def create_token(user_id, user_email=None, user_type='user'):
    """إنشاء JWT token للمستخدم"""
    try:
        payload = {
            'user_id': user_id,
            'user_email': user_email,
            'user_type': user_type,
            'exp': datetime.utcnow() + JWT_EXPIRATION_DELTA,
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    except Exception as e:
        logger.error(f"خطأ في إنشاء Token: {str(e)}")
        return None

def verify_token(token):
    """التحقق من صحة JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def require_auth(f):
    """Decorator للتحقق من المصادقة"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer TOKEN
            except IndexError:
                return jsonify({
                    'success': False,
                    'message': 'تنسيق رمز المصادقة غير صحيح',
                    'error': 'Invalid token format'
                }), 401
        
        if not token:
            return jsonify({
                'success': False,
                'message': 'مطلوب رمز المصادقة للوصول',
                'error': 'No token provided'
            }), 401
        
        # Verify token
        payload = verify_token(token)
        if not payload:
            return jsonify({
                'success': False,
                'message': 'رمز المصادقة غير صحيح أو منتهي الصلاحية',
                'error': 'Invalid or expired token'
            }), 401
        
        # Store user info in request context
        request.current_user_id = payload['user_id']
        request.current_user_email = payload.get('user_email')
        request.current_user_type = payload.get('user_type', 'user')
        
        return f(*args, **kwargs)
    
    return decorated_function

def api_response(success=True, data=None, message=None, error=None, status_code=200):
    """إنشاء استجابة API موحدة"""
    response = {
        'success': success,
        'timestamp': datetime.utcnow().isoformat(),
        'message': message or ('success' if success else 'error')
    }
    
    if data is not None:
        response['data'] = data
    
    if error:
        response['error'] = error
    
    return jsonify(response), status_code

# ========== Authentication Endpoints ==========

@api_bp.route('/health', methods=['GET'])
def health_check():
    """فحص صحة API"""
    return api_response(
        data={
            'status': 'healthy',
            'version': '1.0',
            'timestamp': datetime.utcnow().isoformat()
        },
        message='API يعمل بشكل طبيعي'
    )

@api_bp.route('/info', methods=['GET'])
def api_info():
    """معلومات API والمسارات المتاحة"""
    endpoints = {
        'health': 'GET /api/v1/health',
        'info': 'GET /api/v1/info',
        'authentication': {
            'login': 'POST /api/v1/auth/login',
            'employee_login': 'POST /api/v1/auth/employee-login'
        },
        'dashboard': {
            'stats': 'GET /api/v1/dashboard/stats'
        },
        'employees': {
            'list': 'GET /api/v1/employees',
            'get': 'GET /api/v1/employees/{id}',
            'create': 'POST /api/v1/employees',
            'update': 'PUT /api/v1/employees/{id}',
            'delete': 'DELETE /api/v1/employees/{id}',
            'salaries': 'GET /api/v1/employees/{id}/salaries'
        },
        'vehicles': {
            'list': 'GET /api/v1/vehicles',
            'get': 'GET /api/v1/vehicles/{id}'
        },
        'departments': {
            'list': 'GET /api/v1/departments'
        },
        'attendance': {
            'list': 'GET /api/v1/attendance',
            'create': 'POST /api/v1/attendance'
        },
        'search': 'POST /api/v1/search',
        'reports': {
            'employees_summary': 'GET /api/v1/reports/employees/summary',
            'monthly_attendance': 'GET /api/v1/reports/attendance/monthly'
        },
        'notifications': 'GET /api/v1/notifications'
    }
    
    return api_response(
        data={
            'name': 'نُظم API',
            'version': '1.0',
            'description': 'RESTful API شامل لنظام إدارة الموظفين والمركبات',
            'endpoints': endpoints
        }
    )

@api_bp.route('/auth/login', methods=['POST'])
def login():
    """تسجيل دخول المستخدم"""
    try:
        data = request.get_json()
        if not data or not data.get('email') or not data.get('password'):
            return api_response(
                success=False,
                message='البريد الإلكتروني وكلمة المرور مطلوبان',
                error='Missing email or password',
                status_code=400
            )
        
        email = data.get('email')
        password = data.get('password')
        
        # Find user
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return api_response(
                success=False,
                message='البريد الإلكتروني أو كلمة المرور غير صحيحة',
                error='Invalid credentials',
                status_code=401
            )
        
        # Create token
        token = create_token(user.id, user.email, 'user')
        
        if not token:
            return api_response(
                success=False,
                message='خطأ في إنشاء رمز المصادقة',
                error='Token creation failed',
                status_code=500
            )
        
        return api_response(
            data={
                'token': token,
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'name': user.name,
                    'role': user.role
                }
            },
            message='تم تسجيل الدخول بنجاح'
        )
        
    except Exception as e:
        logger.error(f"خطأ في تسجيل الدخول: {str(e)}")
        return api_response(
            success=False,
            message='خطأ في تسجيل الدخول',
            error=str(e),
            status_code=500
        )

@api_bp.route('/auth/employee-login', methods=['POST'])
def employee_login():
    """تسجيل دخول الموظف"""
    try:
        data = request.get_json()
        if not data or not data.get('employee_id') or not data.get('national_id'):
            return api_response(
                success=False,
                message='رقم الموظف ورقم الهوية مطلوبان',
                error='Missing employee_id or national_id',
                status_code=400
            )
        
        employee_id = data.get('employee_id')
        national_id = data.get('national_id')
        
        # Find employee
        employee = Employee.query.filter_by(
            employee_id=employee_id,
            national_id=national_id
        ).first()
        
        if not employee:
            return api_response(
                success=False,
                message='رقم الموظف أو رقم الهوية غير صحيح',
                error='Invalid employee credentials',
                status_code=401
            )
        
        # Create token
        token = create_token(employee.id, employee.email, 'employee')
        
        if not token:
            return api_response(
                success=False,
                message='خطأ في إنشاء رمز المصادقة',
                error='Token creation failed',
                status_code=500
            )
        
        return api_response(
            data={
                'token': token,
                'employee': {
                    'id': employee.id,
                    'employee_id': employee.employee_id,
                    'name': employee.name,
                    'department': employee.department.name if employee.department else None
                }
            },
            message='تم تسجيل دخول الموظف بنجاح'
        )
        
    except Exception as e:
        logger.error(f"خطأ في تسجيل دخول الموظف: {str(e)}")
        return api_response(
            success=False,
            message='خطأ في تسجيل دخول الموظف',
            error=str(e),
            status_code=500
        )

# ========== Dashboard Endpoints ==========

@api_bp.route('/dashboard/stats', methods=['GET'])
@require_auth
def dashboard_stats():
    """إحصائيات لوحة المعلومات"""
    try:
        # Get basic statistics
        total_employees = Employee.query.count()
        total_vehicles = Vehicle.query.count()
        total_departments = Department.query.count()
        
        # Get attendance stats for current month
        current_month = datetime.now().month
        current_year = datetime.now().year
        
        monthly_attendance = Attendance.query.filter(
            extract('month', Attendance.date) == current_month,
            extract('year', Attendance.date) == current_year
        ).count()
        
        # Get recent activities
        recent_employees = Employee.query.order_by(desc(Employee.created_at)).limit(5).all()
        
        return api_response(
            data={
                'totals': {
                    'employees': total_employees,
                    'vehicles': total_vehicles,
                    'departments': total_departments,
                    'monthly_attendance': monthly_attendance
                },
                'recent_employees': [{
                    'id': emp.id,
                    'name': emp.name,
                    'employee_id': emp.employee_id,
                    'department': emp.department.name if emp.department else None,
                    'created_at': emp.created_at.isoformat() if emp.created_at else None
                } for emp in recent_employees]
            },
            message='تم جلب إحصائيات لوحة المعلومات بنجاح'
        )
        
    except Exception as e:
        logger.error(f"خطأ في جلب إحصائيات لوحة المعلومات: {str(e)}")
        return api_response(
            success=False,
            message='خطأ في جلب إحصائيات لوحة المعلومات',
            error=str(e),
            status_code=500
        )

# ========== Employee Management Endpoints ==========

@api_bp.route('/employees', methods=['GET'])
@require_auth
def get_employees():
    """قائمة الموظفين مع البحث والترقيم"""
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        department_id = request.args.get('department_id', type=int)
        status = request.args.get('status', '')
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'desc')
        
        # Build query
        query = Employee.query
        
        # Apply search
        if search:
            query = query.filter(
                or_(
                    Employee.name.ilike(f'%{search}%'),
                    Employee.employee_id.ilike(f'%{search}%'),
                    Employee.national_id.ilike(f'%{search}%')
                )
            )
        
        # Apply filters
        if department_id:
            query = query.filter(Employee.department_id == department_id)
        
        if status:
            query = query.filter(Employee.status == status)
        
        # Apply sorting
        if sort_by == 'name':
            order_column = Employee.name
        elif sort_by == 'employee_id':
            order_column = Employee.employee_id
        elif sort_by == 'created_at':
            order_column = Employee.created_at
        else:
            order_column = Employee.created_at
        
        if sort_order == 'desc':
            query = query.order_by(desc(order_column))
        else:
            query = query.order_by(order_column)
        
        # Execute pagination
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        employees = pagination.items
        
        return api_response(
            data={
                'employees': [{
                    'id': emp.id,
                    'name': emp.name,
                    'employee_id': emp.employee_id,
                    'national_id': emp.national_id,
                    'department': {
                        'id': emp.department.id,
                        'name': emp.department.name
                    } if emp.department else None,
                    'position': emp.position,
                    'status': emp.status,
                    'phone': emp.phone,
                    'email': emp.email,
                    'created_at': emp.created_at.isoformat() if emp.created_at else None
                } for emp in employees],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            },
            message='تم جلب قائمة الموظفين بنجاح'
        )
        
    except Exception as e:
        logger.error(f"خطأ في جلب قائمة الموظفين: {str(e)}")
        return api_response(
            success=False,
            message='خطأ في جلب قائمة الموظفين',
            error=str(e),
            status_code=500
        )

@api_bp.route('/employees/<int:employee_id>', methods=['GET'])
@require_auth
def get_employee(employee_id):
    """تفاصيل موظف محدد"""
    try:
        employee = Employee.query.get_or_404(employee_id)
        
        # Get employee's salary records
        salaries = Salary.query.filter_by(employee_id=employee_id).order_by(desc(Salary.created_at)).limit(5).all()
        
        # Get employee's attendance records
        attendance = Attendance.query.filter_by(employee_id=employee_id).order_by(desc(Attendance.date)).limit(10).all()
        
        return api_response(
            data={
                'employee': {
                    'id': employee.id,
                    'name': employee.name,
                    'employee_id': employee.employee_id,
                    'national_id': employee.national_id,
                    'department': {
                        'id': employee.department.id,
                        'name': employee.department.name
                    } if employee.department else None,
                    'position': employee.position,
                    'status': employee.status,
                    'phone': employee.phone,
                    'email': employee.email,
                    'address': employee.address,
                    'created_at': employee.created_at.isoformat() if employee.created_at else None,
                    'updated_at': employee.updated_at.isoformat() if employee.updated_at else None
                },
                'recent_salaries': [{
                    'id': sal.id,
                    'amount': float(sal.amount),
                    'month': sal.month,
                    'year': sal.year,
                    'created_at': sal.created_at.isoformat() if sal.created_at else None
                } for sal in salaries],
                'recent_attendance': [{
                    'id': att.id,
                    'date': att.date.isoformat(),
                    'status': att.status,
                    'created_at': att.created_at.isoformat() if att.created_at else None
                } for att in attendance]
            },
            message='تم جلب تفاصيل الموظف بنجاح'
        )
        
    except Exception as e:
        logger.error(f"خطأ في جلب تفاصيل الموظف: {str(e)}")
        return api_response(
            success=False,
            message='خطأ في جلب تفاصيل الموظف',
            error=str(e),
            status_code=500
        )

@api_bp.route('/employees', methods=['POST'])
@require_auth
def create_employee():
    """إضافة موظف جديد"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'employee_id', 'national_id', 'department_id']
        for field in required_fields:
            if not data.get(field):
                return api_response(
                    success=False,
                    message=f'الحقل {field} مطلوب',
                    error=f'Missing required field: {field}',
                    status_code=400
                )
        
        # Check for duplicates
        existing_employee = Employee.query.filter(
            or_(
                Employee.employee_id == data['employee_id'],
                Employee.national_id == data['national_id']
            )
        ).first()
        
        if existing_employee:
            return api_response(
                success=False,
                message='رقم الموظف أو رقم الهوية مستخدم بالفعل',
                error='Employee ID or National ID already exists',
                status_code=400
            )
        
        # Create new employee
        employee = Employee(
            name=data['name'],
            employee_id=data['employee_id'],
            national_id=data['national_id'],
            department_id=data['department_id'],
            position=data.get('position', ''),
            phone=data.get('phone', ''),
            email=data.get('email', ''),
            address=data.get('address', ''),
            status=data.get('status', 'active')
        )
        
        db.session.add(employee)
        db.session.commit()
        
        return api_response(
            data={
                'employee': {
                    'id': employee.id,
                    'name': employee.name,
                    'employee_id': employee.employee_id,
                    'national_id': employee.national_id,
                    'department_id': employee.department_id,
                    'position': employee.position,
                    'status': employee.status
                }
            },
            message='تم إضافة الموظف بنجاح',
            status_code=201
        )
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"خطأ في إضافة الموظف: {str(e)}")
        return api_response(
            success=False,
            message='خطأ في إضافة الموظف',
            error=str(e),
            status_code=500
        )

@api_bp.route('/employees/<int:employee_id>', methods=['PUT'])
@require_auth
def update_employee(employee_id):
    """تحديث بيانات موظف"""
    try:
        employee = Employee.query.get_or_404(employee_id)
        data = request.get_json()
        
        # Update fields
        if 'name' in data:
            employee.name = data['name']
        if 'position' in data:
            employee.position = data['position']
        if 'department_id' in data:
            employee.department_id = data['department_id']
        if 'phone' in data:
            employee.phone = data['phone']
        if 'email' in data:
            employee.email = data['email']
        if 'address' in data:
            employee.address = data['address']
        if 'status' in data:
            employee.status = data['status']
        
        employee.updated_at = datetime.utcnow()
        db.session.commit()
        
        return api_response(
            data={
                'employee': {
                    'id': employee.id,
                    'name': employee.name,
                    'employee_id': employee.employee_id,
                    'position': employee.position,
                    'status': employee.status,
                    'updated_at': employee.updated_at.isoformat()
                }
            },
            message='تم تحديث بيانات الموظف بنجاح'
        )
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"خطأ في تحديث الموظف: {str(e)}")
        return api_response(
            success=False,
            message='خطأ في تحديث الموظف',
            error=str(e),
            status_code=500
        )

@api_bp.route('/employees/<int:employee_id>', methods=['DELETE'])
@require_auth
def delete_employee(employee_id):
    """حذف موظف (soft delete)"""
    try:
        employee = Employee.query.get_or_404(employee_id)
        
        # Soft delete - just mark as inactive
        employee.status = 'inactive'
        employee.updated_at = datetime.utcnow()
        db.session.commit()
        
        return api_response(
            message='تم حذف الموظف بنجاح'
        )
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"خطأ في حذف الموظف: {str(e)}")
        return api_response(
            success=False,
            message='خطأ في حذف الموظف',
            error=str(e),
            status_code=500
        )

# ========== Vehicle Management Endpoints ==========

@api_bp.route('/vehicles', methods=['GET'])
@require_auth
def get_vehicles():
    """قائمة المركبات"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        search = request.args.get('search', '')
        
        query = Vehicle.query
        
        if search:
            query = query.filter(
                or_(
                    Vehicle.plate_number.ilike(f'%{search}%'),
                    Vehicle.make.ilike(f'%{search}%'),
                    Vehicle.model.ilike(f'%{search}%')
                )
            )
        
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        vehicles = pagination.items
        
        return api_response(
            data={
                'vehicles': [{
                    'id': veh.id,
                    'plate_number': veh.plate_number,
                    'make': veh.make,
                    'model': veh.model,
                    'year': veh.year,
                    'color': veh.color,
                    'status': veh.status,
                    'created_at': veh.created_at.isoformat() if veh.created_at else None
                } for veh in vehicles],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            },
            message='تم جلب قائمة المركبات بنجاح'
        )
        
    except Exception as e:
        logger.error(f"خطأ في جلب قائمة المركبات: {str(e)}")
        return api_response(
            success=False,
            message='خطأ في جلب قائمة المركبات',
            error=str(e),
            status_code=500
        )

@api_bp.route('/vehicles/<int:vehicle_id>', methods=['GET'])
@require_auth
def get_vehicle(vehicle_id):
    """تفاصيل مركبة محددة"""
    try:
        vehicle = Vehicle.query.get_or_404(vehicle_id)
        
        # Get vehicle handover records
        handovers = VehicleHandover.query.filter_by(vehicle_id=vehicle_id).order_by(desc(VehicleHandover.created_at)).limit(10).all()
        
        # Get vehicle workshop records
        workshops = VehicleWorkshop.query.filter_by(vehicle_id=vehicle_id).order_by(desc(VehicleWorkshop.created_at)).limit(10).all()
        
        return api_response(
            data={
                'vehicle': {
                    'id': vehicle.id,
                    'plate_number': vehicle.plate_number,
                    'make': vehicle.make,
                    'model': vehicle.model,
                    'year': vehicle.year,
                    'color': vehicle.color,
                    'status': vehicle.status,
                    'created_at': vehicle.created_at.isoformat() if vehicle.created_at else None
                },
                'handovers': [{
                    'id': hand.id,
                    'employee_name': hand.employee_name,
                    'handover_date': hand.handover_date.isoformat() if hand.handover_date else None,
                    'return_date': hand.return_date.isoformat() if hand.return_date else None,
                    'status': hand.status
                } for hand in handovers],
                'workshops': [{
                    'id': work.id,
                    'description': work.description,
                    'cost': float(work.cost) if work.cost else 0,
                    'date': work.date.isoformat() if work.date else None
                } for work in workshops]
            },
            message='تم جلب تفاصيل المركبة بنجاح'
        )
        
    except Exception as e:
        logger.error(f"خطأ في جلب تفاصيل المركبة: {str(e)}")
        return api_response(
            success=False,
            message='خطأ في جلب تفاصيل المركبة',
            error=str(e),
            status_code=500
        )

# ========== Department Management Endpoints ==========

@api_bp.route('/departments', methods=['GET'])
@require_auth
def get_departments():
    """قائمة الأقسام"""
    try:
        departments = Department.query.all()
        
        return api_response(
            data={
                'departments': [{
                    'id': dept.id,
                    'name': dept.name,
                    'description': dept.description,
                    'employee_count': Employee.query.filter_by(department_id=dept.id).count(),
                    'created_at': dept.created_at.isoformat() if dept.created_at else None
                } for dept in departments]
            },
            message='تم جلب قائمة الأقسام بنجاح'
        )
        
    except Exception as e:
        logger.error(f"خطأ في جلب قائمة الأقسام: {str(e)}")
        return api_response(
            success=False,
            message='خطأ في جلب قائمة الأقسام',
            error=str(e),
            status_code=500
        )

# ========== Attendance Management Endpoints ==========

@api_bp.route('/attendance', methods=['GET'])
@require_auth
def get_attendance():
    """قائمة سجلات الحضور"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        employee_id = request.args.get('employee_id', type=int)
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        status = request.args.get('status')
        
        query = Attendance.query
        
        # Apply filters
        if employee_id:
            query = query.filter(Attendance.employee_id == employee_id)
        
        if date_from:
            query = query.filter(Attendance.date >= datetime.strptime(date_from, '%Y-%m-%d').date())
        
        if date_to:
            query = query.filter(Attendance.date <= datetime.strptime(date_to, '%Y-%m-%d').date())
        
        if status:
            query = query.filter(Attendance.status == status)
        
        pagination = query.order_by(desc(Attendance.date)).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        attendance_records = pagination.items
        
        return api_response(
            data={
                'attendance': [{
                    'id': att.id,
                    'employee': {
                        'id': att.employee.id,
                        'name': att.employee.name,
                        'employee_id': att.employee.employee_id
                    } if att.employee else None,
                    'date': att.date.isoformat(),
                    'status': att.status,
                    'notes': att.notes,
                    'created_at': att.created_at.isoformat() if att.created_at else None
                } for att in attendance_records],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            },
            message='تم جلب سجلات الحضور بنجاح'
        )
        
    except Exception as e:
        logger.error(f"خطأ في جلب سجلات الحضور: {str(e)}")
        return api_response(
            success=False,
            message='خطأ في جلب سجلات الحضور',
            error=str(e),
            status_code=500
        )

@api_bp.route('/attendance', methods=['POST'])
@require_auth
def create_attendance():
    """تسجيل حضور جديد"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['employee_id', 'date', 'status']
        for field in required_fields:
            if not data.get(field):
                return api_response(
                    success=False,
                    message=f'الحقل {field} مطلوب',
                    error=f'Missing required field: {field}',
                    status_code=400
                )
        
        # Check if employee exists
        employee = Employee.query.get(data['employee_id'])
        if not employee:
            return api_response(
                success=False,
                message='الموظف غير موجود',
                error='Employee not found',
                status_code=404
            )
        
        # Check if attendance already exists for this date
        attendance_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        existing_attendance = Attendance.query.filter_by(
            employee_id=data['employee_id'],
            date=attendance_date
        ).first()
        
        if existing_attendance:
            return api_response(
                success=False,
                message='تم تسجيل الحضور لهذا التاريخ مسبقاً',
                error='Attendance already exists for this date',
                status_code=400
            )
        
        # Create new attendance record
        attendance = Attendance(
            employee_id=data['employee_id'],
            date=attendance_date,
            status=data['status'],
            notes=data.get('notes', '')
        )
        
        db.session.add(attendance)
        db.session.commit()
        
        return api_response(
            data={
                'attendance': {
                    'id': attendance.id,
                    'employee_id': attendance.employee_id,
                    'date': attendance.date.isoformat(),
                    'status': attendance.status,
                    'notes': attendance.notes
                }
            },
            message='تم تسجيل الحضور بنجاح',
            status_code=201
        )
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"خطأ في تسجيل الحضور: {str(e)}")
        return api_response(
            success=False,
            message='خطأ في تسجيل الحضور',
            error=str(e),
            status_code=500
        )

# ========== Salary Management Endpoints ==========

@api_bp.route('/employees/<int:employee_id>/salaries', methods=['GET'])
@require_auth
def get_employee_salaries(employee_id):
    """سجلات رواتب موظف محدد"""
    try:
        employee = Employee.query.get_or_404(employee_id)
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        pagination = Salary.query.filter_by(employee_id=employee_id).order_by(desc(Salary.created_at)).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        salaries = pagination.items
        
        return api_response(
            data={
                'employee': {
                    'id': employee.id,
                    'name': employee.name,
                    'employee_id': employee.employee_id
                },
                'salaries': [{
                    'id': sal.id,
                    'amount': float(sal.amount),
                    'month': sal.month,
                    'year': sal.year,
                    'created_at': sal.created_at.isoformat() if sal.created_at else None
                } for sal in salaries],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': pagination.total,
                    'pages': pagination.pages,
                    'has_next': pagination.has_next,
                    'has_prev': pagination.has_prev
                }
            },
            message='تم جلب سجلات الرواتب بنجاح'
        )
        
    except Exception as e:
        logger.error(f"خطأ في جلب سجلات الرواتب: {str(e)}")
        return api_response(
            success=False,
            message='خطأ في جلب سجلات الرواتب',
            error=str(e),
            status_code=500
        )

# ========== Reports Endpoints ==========

@api_bp.route('/reports/employees/summary', methods=['GET'])
@require_auth
def employees_summary_report():
    """تقرير ملخص الموظفين"""
    try:
        # Get summary statistics
        total_employees = Employee.query.count()
        active_employees = Employee.query.filter_by(status='active').count()
        inactive_employees = Employee.query.filter_by(status='inactive').count()
        
        # Get department-wise statistics
        departments = db.session.query(
            Department.name,
            func.count(Employee.id).label('employee_count')
        ).join(Employee).group_by(Department.name).all()
        
        # Get recent hires
        recent_hires = Employee.query.order_by(desc(Employee.created_at)).limit(10).all()
        
        return api_response(
            data={
                'summary': {
                    'total_employees': total_employees,
                    'active_employees': active_employees,
                    'inactive_employees': inactive_employees
                },
                'departments': [{
                    'name': dept.name,
                    'employee_count': dept.employee_count
                } for dept in departments],
                'recent_hires': [{
                    'id': emp.id,
                    'name': emp.name,
                    'employee_id': emp.employee_id,
                    'department': emp.department.name if emp.department else None,
                    'created_at': emp.created_at.isoformat() if emp.created_at else None
                } for emp in recent_hires]
            },
            message='تم إنشاء تقرير ملخص الموظفين بنجاح'
        )
        
    except Exception as e:
        logger.error(f"خطأ في إنشاء تقرير ملخص الموظفين: {str(e)}")
        return api_response(
            success=False,
            message='خطأ في إنشاء تقرير ملخص الموظفين',
            error=str(e),
            status_code=500
        )

@api_bp.route('/reports/attendance/monthly', methods=['GET'])
@require_auth
def monthly_attendance_report():
    """تقرير الحضور الشهري"""
    try:
        year = request.args.get('year', datetime.now().year, type=int)
        month = request.args.get('month', datetime.now().month, type=int)
        
        # Get attendance statistics for the month
        attendance_stats = db.session.query(
            Attendance.status,
            func.count(Attendance.id).label('count')
        ).filter(
            extract('year', Attendance.date) == year,
            extract('month', Attendance.date) == month
        ).group_by(Attendance.status).all()
        
        # Get employee-wise attendance
        employee_attendance = db.session.query(
            Employee.name,
            Employee.employee_id,
            func.count(Attendance.id).label('attendance_count')
        ).join(Attendance).filter(
            extract('year', Attendance.date) == year,
            extract('month', Attendance.date) == month
        ).group_by(Employee.id, Employee.name, Employee.employee_id).all()
        
        return api_response(
            data={
                'period': {
                    'year': year,
                    'month': month
                },
                'attendance_summary': [{
                    'status': stat.status,
                    'count': stat.count
                } for stat in attendance_stats],
                'employee_attendance': [{
                    'employee_name': emp.name,
                    'employee_id': emp.employee_id,
                    'attendance_count': emp.attendance_count
                } for emp in employee_attendance]
            },
            message='تم إنشاء تقرير الحضور الشهري بنجاح'
        )
        
    except Exception as e:
        logger.error(f"خطأ في إنشاء تقرير الحضور الشهري: {str(e)}")
        return api_response(
            success=False,
            message='خطأ في إنشاء تقرير الحضور الشهري',
            error=str(e),
            status_code=500
        )

# ========== Search Endpoints ==========

@api_bp.route('/search', methods=['POST'])
@require_auth
def search_system():
    """البحث الشامل في النظام"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return api_response(
                success=False,
                message='كلمة البحث مطلوبة',
                error='Search query is required',
                status_code=400
            )
        
        # Search employees
        employees = Employee.query.filter(
            or_(
                Employee.name.ilike(f'%{query}%'),
                Employee.employee_id.ilike(f'%{query}%'),
                Employee.national_id.ilike(f'%{query}%')
            )
        ).limit(10).all()
        
        # Search vehicles
        vehicles = Vehicle.query.filter(
            or_(
                Vehicle.plate_number.ilike(f'%{query}%'),
                Vehicle.make.ilike(f'%{query}%'),
                Vehicle.model.ilike(f'%{query}%')
            )
        ).limit(10).all()
        
        # Search departments
        departments = Department.query.filter(
            Department.name.ilike(f'%{query}%')
        ).limit(5).all()
        
        return api_response(
            data={
                'query': query,
                'results': {
                    'employees': [{
                        'id': emp.id,
                        'name': emp.name,
                        'employee_id': emp.employee_id,
                        'department': emp.department.name if emp.department else None
                    } for emp in employees],
                    'vehicles': [{
                        'id': veh.id,
                        'plate_number': veh.plate_number,
                        'make': veh.make,
                        'model': veh.model
                    } for veh in vehicles],
                    'departments': [{
                        'id': dept.id,
                        'name': dept.name,
                        'description': dept.description
                    } for dept in departments]
                }
            },
            message='تم البحث بنجاح'
        )
        
    except Exception as e:
        logger.error(f"خطأ في البحث: {str(e)}")
        return api_response(
            success=False,
            message='خطأ في البحث',
            error=str(e),
            status_code=500
        )

# ========== Notification Endpoints ==========

@api_bp.route('/notifications', methods=['GET'])
@require_auth
def get_notifications():
    """قائمة الإشعارات"""
    try:
        # For now, return sample notifications
        # In future, implement proper notification system
        notifications = [
            {
                'id': 1,
                'title': 'موظف جديد',
                'message': 'تم إضافة موظف جديد إلى النظام',
                'type': 'info',
                'created_at': datetime.utcnow().isoformat(),
                'read': False
            },
            {
                'id': 2,
                'title': 'تحديث مركبة',
                'message': 'تم تحديث بيانات المركبة رقم 123',
                'type': 'update',
                'created_at': (datetime.utcnow() - timedelta(hours=1)).isoformat(),
                'read': True
            }
        ]
        
        return api_response(
            data={'notifications': notifications},
            message='تم جلب الإشعارات بنجاح'
        )
        
    except Exception as e:
        logger.error(f"خطأ في جلب الإشعارات: {str(e)}")
        return api_response(
            success=False,
            message='خطأ في جلب الإشعارات',
            error=str(e),
            status_code=500
        )

# Log successful API loading
logger.info("تم تحميل RESTful API نُظم بنجاح")
logger.info("جميع المسارات متاحة ومحمية من الأخطاء")