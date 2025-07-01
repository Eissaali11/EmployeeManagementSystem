"""
RESTful API شامل لنظام نُظم
API كامل لجميع خصائص النظام مع معالجة الأخطاء
"""

from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from datetime import datetime, date, timedelta
from sqlalchemy import func, desc, asc, and_, or_
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import logging
import traceback
import json
import jwt
import os
from werkzeug.security import check_password_hash

# استيراد النماذج المتوفرة
from models import (
    User, Employee, Vehicle, Department, Attendance, 
    Salary, Company, CompanySubscription, VehicleHandover,
    VehicleWorkshop, VehiclePeriodicInspection, VehicleSafetyCheck,
    AuditLog
)
from app import db

# إعداد Blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# إعداد الـ Logger
logger = logging.getLogger(__name__)

# ==================== مساعدات API ====================

def api_response(data=None, message="success", status_code=200, meta=None):
    """إنشاء استجابة API موحدة"""
    response = {
        "success": status_code < 400,
        "message": message,
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    if data is not None:
        response["data"] = data
    
    if meta is not None:
        response["meta"] = meta
        
    return jsonify(response), status_code

def api_error(message="خطأ في الخادم", status_code=500, details=None):
    """إنشاء استجابة خطأ API"""
    response = {
        "success": False,
        "error": {
            "message": message,
            "code": status_code,
            "timestamp": datetime.utcnow().isoformat()
        }
    }
    
    if details:
        response["error"]["details"] = details
        
    logger.error(f"API Error {status_code}: {message}")
    if details:
        logger.error(f"Details: {details}")
        
    return jsonify(response), status_code

def paginate_query(query, page=1, per_page=20, max_per_page=100):
    """تطبيق Pagination على الاستعلام"""
    page = max(1, int(page))
    per_page = min(max_per_page, max(1, int(per_page)))
    
    try:
        paginated = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return {
            "items": paginated.items,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": paginated.total,
                "pages": paginated.pages,
                "has_next": paginated.has_next,
                "has_prev": paginated.has_prev,
                "next_page": paginated.next_num if paginated.has_next else None,
                "prev_page": paginated.prev_num if paginated.has_prev else None
            }
        }
    except Exception as e:
        # إذا فشل pagination، نرجع البيانات كقائمة عادية
        items = query.limit(per_page).offset((page - 1) * per_page).all()
        total = query.count()
        
        return {
            "items": items,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "pages": (total + per_page - 1) // per_page,
                "has_next": page * per_page < total,
                "has_prev": page > 1,
                "next_page": page + 1 if page * per_page < total else None,
                "prev_page": page - 1 if page > 1 else None
            }
        }

def serialize_model(model, fields=None, exclude=None):
    """تحويل النموذج إلى dictionary"""
    if model is None:
        return None
        
    data = {}
    
    # جلب جميع الحقول من النموذج
    for column in model.__table__.columns:
        try:
            value = getattr(model, column.name)
            
            # تحويل التواريخ والأوقات إلى string
            if isinstance(value, (datetime, date)):
                value = value.isoformat()
            elif isinstance(value, timedelta):
                value = str(value)
                
            data[column.name] = value
        except AttributeError:
            # تجاهل الحقول غير الموجودة
            continue
    
    # تطبيق فلتر الحقول المطلوبة
    if fields:
        data = {k: v for k, v in data.items() if k in fields}
    
    # استبعاد الحقول غير المرغوبة
    if exclude:
        data = {k: v for k, v in data.items() if k not in exclude}
    
    return data

def validate_required_fields(data, required_fields):
    """التحقق من وجود الحقول المطلوبة"""
    errors = []
    for field in required_fields:
        if field not in data or data[field] is None or str(data[field]).strip() == '':
            errors.append(f"الحقل '{field}' مطلوب")
    return errors

def validate_email(email):
    """التحقق من صحة البريد الإلكتروني"""
    import re
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def generate_token(user_id, company_id):
    """إنشاء JWT Token"""
    try:
        secret_key = os.environ.get('SESSION_SECRET', 'default-secret-key')
        payload = {
            'user_id': user_id,
            'company_id': company_id,
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow()
        }
        
        return jwt.encode(payload, secret_key, algorithm='HS256')
        
    except Exception as e:
        raise Exception(f"خطأ في إنشاء Token: {str(e)}")

# ==================== المصادقة والترخيص ====================

@api_bp.route('/auth/login', methods=['POST'])
def login():
    """تسجيل دخول المستخدم"""
    try:
        data = request.get_json()
        
        if not data:
            return api_error("البيانات مطلوبة", 400)
        
        # التحقق من البيانات المطلوبة
        required_fields = ['email', 'password']
        validation_errors = validate_required_fields(data, required_fields)
        if validation_errors:
            return api_error("بيانات مطلوبة مفقودة", 400, validation_errors)
        
        # التحقق من صحة البريد الإلكتروني
        if not validate_email(data['email']):
            return api_error("صيغة البريد الإلكتروني غير صحيحة", 400)
        
        # البحث عن المستخدم
        user = User.query.filter_by(email=data['email']).first()
        
        if not user:
            return api_error("بيانات غير صحيحة", 401)
        
        if not check_password_hash(user.password_hash, data['password']):
            return api_error("كلمة المرور غير صحيحة", 401)
        
        # إنشاء Token
        token = generate_token(user.id, user.company_id)
        
        return api_response({
            "token": token,
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "company_id": user.company_id,
                "role": getattr(user, 'role', 'user')
            }
        }, "تم تسجيل الدخول بنجاح")
        
    except Exception as e:
        logger.error(f"خطأ في تسجيل الدخول: {str(e)}")
        return api_error("خطأ في تسجيل الدخول")

@api_bp.route('/auth/employee-login', methods=['POST'])
def employee_login():
    """تسجيل دخول الموظف بالرقم الوظيفي والهوية"""
    try:
        data = request.get_json()
        
        if not data:
            return api_error("البيانات مطلوبة", 400)
        
        required_fields = ['employee_id', 'national_id']
        validation_errors = validate_required_fields(data, required_fields)
        if validation_errors:
            return api_error("بيانات مطلوبة مفقودة", 400, validation_errors)
        
        # البحث عن الموظف
        employee = Employee.query.filter_by(
            employee_id=data['employee_id'],
            national_id=data['national_id']
        ).first()
        
        if not employee:
            return api_error("بيانات غير صحيحة", 401)
        
        # إنشاء Token للموظف
        secret_key = os.environ.get('SESSION_SECRET', 'default-secret-key')
        payload = {
            'employee_id': employee.id,
            'company_id': employee.company_id,
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(payload, secret_key, algorithm='HS256')
        
        return api_response({
            "token": token,
            "employee": serialize_model(employee, exclude=['national_id'])
        }, "تم تسجيل الدخول بنجاح")
        
    except Exception as e:
        logger.error(f"خطأ في تسجيل دخول الموظف: {str(e)}")
        return api_error("خطأ في تسجيل الدخول")

# ==================== لوحة المعلومات والإحصائيات ====================

@api_bp.route('/dashboard/stats', methods=['GET'])
@login_required
def dashboard_stats():
    """إحصائيات لوحة المعلومات"""
    try:
        company_id = current_user.company_id
        
        # الإحصائيات الأساسية
        stats = {
            "employees": {
                "total": Employee.query.filter_by(company_id=company_id).count(),
                "active": Employee.query.filter_by(company_id=company_id, status='active').count(),
                "new_this_month": 0  # سيتم حسابها إذا كان هناك حقل hire_date
            },
            "vehicles": {
                "total": Vehicle.query.filter_by(company_id=company_id).count(),
                "active": Vehicle.query.filter_by(company_id=company_id, status='active').count(),
                "in_workshop": Vehicle.query.filter_by(company_id=company_id, status='workshop').count()
            },
            "departments": {
                "total": Department.query.filter_by(company_id=company_id).count(),
                "with_managers": 0  # سيتم حسابها إذا كان هناك حقل manager_id
            },
            "attendance": {
                "present_today": 0,  # سيتم حسابها إذا كان هناك سجلات حضور
                "absent_today": 0
            }
        }
        
        # محاولة حساب الموظفين الجدد هذا الشهر
        try:
            month_start = date.today().replace(day=1)
            new_employees = Employee.query.filter(
                Employee.company_id == company_id,
                Employee.hire_date >= month_start
            ).count()
            stats["employees"]["new_this_month"] = new_employees
        except:
            pass
        
        # محاولة حساب الأقسام مع المديرين
        try:
            with_managers = Department.query.filter(
                Department.company_id == company_id,
                Department.manager_id.isnot(None)
            ).count()
            stats["departments"]["with_managers"] = with_managers
        except:
            pass
        
        # محاولة حساب الحضور اليوم
        try:
            present_today = Attendance.query.filter(
                Attendance.company_id == company_id,
                Attendance.date == date.today(),
                Attendance.status == 'present'
            ).count()
            
            absent_today = Attendance.query.filter(
                Attendance.company_id == company_id,
                Attendance.date == date.today(),
                Attendance.status == 'absent'
            ).count()
            
            stats["attendance"]["present_today"] = present_today
            stats["attendance"]["absent_today"] = absent_today
        except:
            pass
        
        return api_response({"statistics": stats})
        
    except Exception as e:
        logger.error(f"خطأ في إحصائيات لوحة المعلومات: {str(e)}")
        return api_error("خطأ في جلب الإحصائيات")

# ==================== إدارة الموظفين ====================

@api_bp.route('/employees', methods=['GET'])
@login_required
def get_employees():
    """جلب قائمة الموظفين مع البحث والتصفية"""
    try:
        company_id = current_user.company_id
        
        # المعاملات
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        department_id = request.args.get('department_id', type=int)
        status = request.args.get('status', '')
        sort_by = request.args.get('sort_by', 'id')
        sort_order = request.args.get('sort_order', 'desc')
        
        # بناء الاستعلام
        query = Employee.query.filter_by(company_id=company_id)
        
        # البحث
        if search:
            query = query.filter(
                or_(
                    Employee.name.contains(search),
                    Employee.employee_id.contains(search),
                    Employee.email.contains(search) if hasattr(Employee, 'email') else False
                )
            )
        
        # التصفية حسب القسم
        if department_id:
            query = query.filter_by(department_id=department_id)
        
        # التصفية حسب الحالة
        if status:
            query = query.filter_by(status=status)
        
        # الترتيب
        if hasattr(Employee, sort_by):
            if sort_order == 'desc':
                query = query.order_by(desc(getattr(Employee, sort_by)))
            else:
                query = query.order_by(asc(getattr(Employee, sort_by)))
        
        # التصفح
        result = paginate_query(query, page, per_page)
        
        # تسلسل البيانات
        employees = [serialize_model(emp, exclude=['national_id']) for emp in result['items']]
        
        return api_response(employees, meta=result['pagination'])
        
    except Exception as e:
        logger.error(f"خطأ في جلب الموظفين: {str(e)}")
        return api_error("خطأ في جلب قائمة الموظفين")

@api_bp.route('/employees/<int:employee_id>', methods=['GET'])
@login_required
def get_employee(employee_id):
    """جلب بيانات موظف محدد"""
    try:
        employee = Employee.query.filter_by(
            id=employee_id,
            company_id=current_user.company_id
        ).first()
        
        if not employee:
            return api_error("الموظف غير موجود", 404)
        
        # جلب البيانات المرتبطة
        employee_data = serialize_model(employee, exclude=['national_id'])
        
        # إضافة بيانات القسم
        try:
            if employee.department:
                employee_data['department'] = serialize_model(employee.department)
        except:
            pass
        
        return api_response(employee_data)
        
    except Exception as e:
        logger.error(f"خطأ في جلب بيانات الموظف {employee_id}: {str(e)}")
        return api_error("خطأ في جلب بيانات الموظف")

@api_bp.route('/employees', methods=['POST'])
@login_required
def create_employee():
    """إضافة موظف جديد"""
    try:
        data = request.get_json()
        
        if not data:
            return api_error("البيانات مطلوبة", 400)
        
        # التحقق من البيانات المطلوبة
        required_fields = ['name', 'employee_id', 'national_id']
        validation_errors = validate_required_fields(data, required_fields)
        if validation_errors:
            return api_error("بيانات مطلوبة مفقودة", 400, validation_errors)
        
        # التحقق من عدم تكرار رقم الموظف أو الهوية
        existing = Employee.query.filter(
            Employee.company_id == current_user.company_id,
            or_(
                Employee.employee_id == data['employee_id'],
                Employee.national_id == data['national_id']
            )
        ).first()
        
        if existing:
            return api_error("رقم الموظف أو الهوية الوطنية مستخدم بالفعل", 409)
        
        # إنشاء الموظف الجديد
        employee_data = {
            'company_id': current_user.company_id,
            'name': data['name'],
            'employee_id': data['employee_id'],
            'national_id': data['national_id']
        }
        
        # إضافة الحقول الاختيارية إذا كانت موجودة
        optional_fields = ['email', 'phone', 'department_id', 'job_title', 'basic_salary', 'status']
        for field in optional_fields:
            if field in data and hasattr(Employee, field):
                employee_data[field] = data[field]
        
        # تعيين الحالة الافتراضية
        if 'status' not in employee_data:
            employee_data['status'] = 'active'
        
        # محاولة تعيين تاريخ التوظيف
        if 'hire_date' in data and hasattr(Employee, 'hire_date'):
            try:
                employee_data['hire_date'] = datetime.strptime(data['hire_date'], '%Y-%m-%d').date()
            except:
                employee_data['hire_date'] = date.today()
        elif hasattr(Employee, 'hire_date'):
            employee_data['hire_date'] = date.today()
        
        employee = Employee(**employee_data)
        
        db.session.add(employee)
        db.session.commit()
        
        return api_response(
            serialize_model(employee, exclude=['national_id']),
            "تم إضافة الموظف بنجاح",
            201
        )
        
    except IntegrityError as e:
        db.session.rollback()
        logger.error(f"خطأ في قاعدة البيانات عند إضافة موظف: {str(e)}")
        return api_error("خطأ في البيانات المدخلة", 400)
    except Exception as e:
        db.session.rollback()
        logger.error(f"خطأ في إضافة موظف: {str(e)}")
        return api_error("خطأ في إضافة الموظف")

@api_bp.route('/employees/<int:employee_id>', methods=['PUT'])
@login_required
def update_employee(employee_id):
    """تحديث بيانات موظف"""
    try:
        employee = Employee.query.filter_by(
            id=employee_id,
            company_id=current_user.company_id
        ).first()
        
        if not employee:
            return api_error("الموظف غير موجود", 404)
        
        data = request.get_json()
        
        if not data:
            return api_error("البيانات مطلوبة", 400)
        
        # تحديث البيانات
        updateable_fields = [
            'name', 'email', 'phone', 'department_id', 'basic_salary', 
            'status', 'job_title'
        ]
        
        for field in updateable_fields:
            if field in data and hasattr(employee, field):
                setattr(employee, field, data[field])
        
        # تحديث تاريخ التوظيف إذا كان موجوداً
        if 'hire_date' in data and hasattr(employee, 'hire_date'):
            try:
                setattr(employee, 'hire_date', datetime.strptime(data['hire_date'], '%Y-%m-%d').date())
            except:
                pass
        
        # تحديث وقت التعديل إذا كان موجوداً
        if hasattr(employee, 'updated_at'):
            employee.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return api_response(
            serialize_model(employee, exclude=['national_id']),
            "تم تحديث بيانات الموظف بنجاح"
        )
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"خطأ في تحديث الموظف {employee_id}: {str(e)}")
        return api_error("خطأ في تحديث بيانات الموظف")

@api_bp.route('/employees/<int:employee_id>', methods=['DELETE'])
@login_required
def delete_employee(employee_id):
    """حذف موظف"""
    try:
        employee = Employee.query.filter_by(
            id=employee_id,
            company_id=current_user.company_id
        ).first()
        
        if not employee:
            return api_error("الموظف غير موجود", 404)
        
        employee_name = employee.name
        
        # تعطيل الموظف بدلاً من الحذف الفعلي
        employee.status = 'inactive'
        
        # تعيين تاريخ الحذف إذا كان الحقل موجوداً
        if hasattr(employee, 'deleted_at'):
            employee.deleted_at = datetime.utcnow()
        
        db.session.commit()
        
        return api_response(None, f"تم حذف الموظف {employee_name} بنجاح")
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"خطأ في حذف الموظف {employee_id}: {str(e)}")
        return api_error("خطأ في حذف الموظف")

# ==================== إدارة المركبات ====================

@api_bp.route('/vehicles', methods=['GET'])
@login_required
def get_vehicles():
    """جلب قائمة المركبات"""
    try:
        company_id = current_user.company_id
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        status = request.args.get('status', '')
        
        query = Vehicle.query.filter_by(company_id=company_id)
        
        if search:
            query = query.filter(
                or_(
                    Vehicle.plate_number.contains(search),
                    Vehicle.make.contains(search) if hasattr(Vehicle, 'make') else False,
                    Vehicle.model.contains(search) if hasattr(Vehicle, 'model') else False
                )
            )
        
        if status:
            query = query.filter_by(status=status)
        
        query = query.order_by(desc(Vehicle.id))
        
        result = paginate_query(query, page, per_page)
        vehicles = [serialize_model(vehicle) for vehicle in result['items']]
        
        return api_response(vehicles, meta=result['pagination'])
        
    except Exception as e:
        logger.error(f"خطأ في جلب المركبات: {str(e)}")
        return api_error("خطأ في جلب قائمة المركبات")

@api_bp.route('/vehicles/<int:vehicle_id>', methods=['GET'])
@login_required
def get_vehicle(vehicle_id):
    """جلب بيانات مركبة محددة"""
    try:
        vehicle = Vehicle.query.filter_by(
            id=vehicle_id,
            company_id=current_user.company_id
        ).first()
        
        if not vehicle:
            return api_error("المركبة غير موجودة", 404)
        
        vehicle_data = serialize_model(vehicle)
        
        # إضافة سجلات التسليم إذا كانت متوفرة
        try:
            handovers = VehicleHandover.query.filter_by(vehicle_id=vehicle_id)\
                .order_by(desc(VehicleHandover.id)).limit(10).all()
            vehicle_data['handovers'] = [serialize_model(h) for h in handovers]
        except:
            vehicle_data['handovers'] = []
        
        # إضافة سجلات الورشة إذا كانت متوفرة
        try:
            workshops = VehicleWorkshop.query.filter_by(vehicle_id=vehicle_id)\
                .order_by(desc(VehicleWorkshop.id)).limit(5).all()
            vehicle_data['workshops'] = [serialize_model(w) for w in workshops]
        except:
            vehicle_data['workshops'] = []
        
        return api_response(vehicle_data)
        
    except Exception as e:
        logger.error(f"خطأ في جلب بيانات المركبة {vehicle_id}: {str(e)}")
        return api_error("خطأ في جلب بيانات المركبة")

# ==================== إدارة الأقسام ====================

@api_bp.route('/departments', methods=['GET'])
@login_required
def get_departments():
    """جلب قائمة الأقسام"""
    try:
        departments = Department.query.filter_by(
            company_id=current_user.company_id
        ).order_by(Department.name).all()
        
        departments_data = []
        for dept in departments:
            dept_data = serialize_model(dept)
            
            # إضافة عدد الموظفين
            dept_data['employees_count'] = Employee.query.filter_by(
                department_id=dept.id
            ).count()
            
            # إضافة بيانات المدير إذا كان موجوداً
            try:
                if hasattr(dept, 'manager_id') and dept.manager_id:
                    manager = Employee.query.get(dept.manager_id)
                    if manager:
                        dept_data['manager'] = serialize_model(manager, fields=['id', 'name', 'employee_id'])
            except:
                pass
            
            departments_data.append(dept_data)
        
        return api_response(departments_data)
        
    except Exception as e:
        logger.error(f"خطأ في جلب الأقسام: {str(e)}")
        return api_error("خطأ في جلب قائمة الأقسام")

# ==================== إدارة الحضور ====================

@api_bp.route('/attendance', methods=['GET'])
@login_required
def get_attendance():
    """جلب سجلات الحضور"""
    try:
        company_id = current_user.company_id
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        employee_id = request.args.get('employee_id', type=int)
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        query = Attendance.query.filter_by(company_id=company_id)
        
        if employee_id:
            query = query.filter_by(employee_id=employee_id)
        
        if date_from:
            try:
                query = query.filter(Attendance.date >= datetime.strptime(date_from, '%Y-%m-%d').date())
            except:
                pass
        
        if date_to:
            try:
                query = query.filter(Attendance.date <= datetime.strptime(date_to, '%Y-%m-%d').date())
            except:
                pass
        
        query = query.order_by(desc(Attendance.date))
        
        result = paginate_query(query, page, per_page)
        
        attendance_data = []
        for att in result['items']:
            att_data = serialize_model(att)
            
            # إضافة بيانات الموظف
            try:
                if att.employee:
                    att_data['employee'] = serialize_model(att.employee, fields=['id', 'name', 'employee_id'])
            except:
                pass
            
            attendance_data.append(att_data)
        
        return api_response(attendance_data, meta=result['pagination'])
        
    except Exception as e:
        logger.error(f"خطأ في جلب سجلات الحضور: {str(e)}")
        return api_error("خطأ في جلب سجلات الحضور")

@api_bp.route('/attendance', methods=['POST'])
@login_required
def record_attendance():
    """تسجيل حضور"""
    try:
        data = request.get_json()
        
        if not data:
            return api_error("البيانات مطلوبة", 400)
        
        required_fields = ['employee_id', 'date', 'status']
        validation_errors = validate_required_fields(data, required_fields)
        if validation_errors:
            return api_error("بيانات مطلوبة مفقودة", 400, validation_errors)
        
        # التحقق من وجود الموظف
        employee = Employee.query.filter_by(
            id=data['employee_id'],
            company_id=current_user.company_id
        ).first()
        
        if not employee:
            return api_error("الموظف غير موجود", 404)
        
        try:
            attendance_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        except:
            return api_error("تنسيق التاريخ غير صحيح، استخدم YYYY-MM-DD", 400)
        
        # التحقق من عدم تكرار التسجيل لنفس اليوم
        existing = Attendance.query.filter_by(
            employee_id=data['employee_id'],
            date=attendance_date
        ).first()
        
        if existing:
            return api_error("تم تسجيل الحضور لهذا اليوم بالفعل", 409)
        
        # إنشاء سجل الحضور
        attendance_data = {
            'company_id': current_user.company_id,
            'employee_id': data['employee_id'],
            'date': attendance_date,
            'status': data['status']
        }
        
        # إضافة أوقات الدخول والخروج إذا كانت متوفرة
        if 'check_in_time' in data and hasattr(Attendance, 'check_in_time'):
            try:
                attendance_data['check_in_time'] = datetime.strptime(data['check_in_time'], '%H:%M').time()
            except:
                pass
        
        if 'check_out_time' in data and hasattr(Attendance, 'check_out_time'):
            try:
                attendance_data['check_out_time'] = datetime.strptime(data['check_out_time'], '%H:%M').time()
            except:
                pass
        
        if 'notes' in data and hasattr(Attendance, 'notes'):
            attendance_data['notes'] = data['notes']
        
        attendance = Attendance(**attendance_data)
        
        db.session.add(attendance)
        db.session.commit()
        
        return api_response(
            serialize_model(attendance),
            "تم تسجيل الحضور بنجاح",
            201
        )
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"خطأ في تسجيل الحضور: {str(e)}")
        return api_error("خطأ في تسجيل الحضور")

# ==================== إدارة الرواتب ====================

@api_bp.route('/employees/<int:employee_id>/salaries', methods=['GET'])
@login_required
def get_employee_salaries(employee_id):
    """جلب سجلات رواتب الموظف"""
    try:
        # التحقق من وجود الموظف
        employee = Employee.query.filter_by(
            id=employee_id,
            company_id=current_user.company_id
        ).first()
        
        if not employee:
            return api_error("الموظف غير موجود", 404)
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 12, type=int)
        
        query = Salary.query.filter_by(employee_id=employee_id)
        
        # ترتيب حسب التاريخ إذا كان متوفراً
        if hasattr(Salary, 'payment_date'):
            query = query.order_by(desc(Salary.payment_date))
        else:
            query = query.order_by(desc(Salary.id))
        
        result = paginate_query(query, page, per_page)
        salaries = [serialize_model(salary) for salary in result['items']]
        
        return api_response(salaries, meta=result['pagination'])
        
    except Exception as e:
        logger.error(f"خطأ في جلب رواتب الموظف {employee_id}: {str(e)}")
        return api_error("خطأ في جلب سجلات الرواتب")

# ==================== التقارير ====================

@api_bp.route('/reports/employees/summary', methods=['GET'])
@login_required
def employees_summary_report():
    """تقرير ملخص الموظفين"""
    try:
        company_id = current_user.company_id
        
        # إحصائيات الموظفين
        total_employees = Employee.query.filter_by(company_id=company_id).count()
        active_employees = Employee.query.filter_by(company_id=company_id, status='active').count()
        
        # التوزيع حسب الأقسام
        dept_stats = []
        try:
            dept_data = db.session.query(
                Department.name,
                func.count(Employee.id).label('count')
            ).join(Employee)\
             .filter(Employee.company_id == company_id)\
             .group_by(Department.name).all()
            
            dept_stats = [
                {"department": dept[0], "count": dept[1]} 
                for dept in dept_data
            ]
        except:
            pass
        
        # الموظفين الجدد هذا الشهر
        new_employees = 0
        try:
            if hasattr(Employee, 'hire_date'):
                month_start = date.today().replace(day=1)
                new_employees = Employee.query.filter(
                    Employee.company_id == company_id,
                    Employee.hire_date >= month_start
                ).count()
        except:
            pass
        
        report_data = {
            "summary": {
                "total_employees": total_employees,
                "active_employees": active_employees,
                "inactive_employees": total_employees - active_employees,
                "new_this_month": new_employees
            },
            "departments_distribution": dept_stats,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return api_response(report_data)
        
    except Exception as e:
        logger.error(f"خطأ في تقرير ملخص الموظفين: {str(e)}")
        return api_error("خطأ في إنشاء التقرير")

@api_bp.route('/reports/attendance/monthly', methods=['GET'])
@login_required
def monthly_attendance_report():
    """تقرير الحضور الشهري"""
    try:
        company_id = current_user.company_id
        year = request.args.get('year', date.today().year, type=int)
        month = request.args.get('month', date.today().month, type=int)
        
        # نطاق التواريخ
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            end_date = date(year, month + 1, 1) - timedelta(days=1)
        
        # إحصائيات الحضور
        status_distribution = {}
        daily_attendance = []
        
        try:
            # إحصائيات الحالات
            attendance_stats = db.session.query(
                Attendance.status,
                func.count(Attendance.id).label('count')
            ).filter(
                Attendance.company_id == company_id,
                Attendance.date >= start_date,
                Attendance.date <= end_date
            ).group_by(Attendance.status).all()
            
            status_distribution = {
                status[0]: status[1] for status in attendance_stats
            }
            
            # الحضور اليومي
            current_date = start_date
            while current_date <= end_date:
                daily_count = Attendance.query.filter(
                    Attendance.company_id == company_id,
                    Attendance.date == current_date,
                    Attendance.status == 'present'
                ).count()
                
                daily_attendance.append({
                    "date": current_date.isoformat(),
                    "present_count": daily_count
                })
                
                current_date += timedelta(days=1)
        except:
            pass
        
        report_data = {
            "period": {
                "year": year,
                "month": month,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "summary": status_distribution,
            "daily_attendance": daily_attendance,
            "generated_at": datetime.utcnow().isoformat()
        }
        
        return api_response(report_data)
        
    except Exception as e:
        logger.error(f"خطأ في تقرير الحضور الشهري: {str(e)}")
        return api_error("خطأ في إنشاء تقرير الحضور")

# ==================== البحث المتقدم ====================

@api_bp.route('/search', methods=['POST'])
@login_required
def advanced_search():
    """البحث المتقدم في النظام"""
    try:
        data = request.get_json()
        
        if not data:
            return api_error("البيانات مطلوبة", 400)
        
        query_text = data.get('query', '').strip()
        search_in = data.get('search_in', ['employees', 'vehicles'])
        
        if not query_text:
            return api_error("استعلام البحث مطلوب", 400)
        
        results = {}
        company_id = current_user.company_id
        
        # البحث في الموظفين
        if 'employees' in search_in:
            try:
                employees = Employee.query.filter(
                    Employee.company_id == company_id,
                    or_(
                        Employee.name.contains(query_text),
                        Employee.employee_id.contains(query_text),
                        Employee.email.contains(query_text) if hasattr(Employee, 'email') else False
                    )
                ).limit(10).all()
                
                results['employees'] = [
                    serialize_model(emp, fields=['id', 'name', 'employee_id', 'email', 'job_title'])
                    for emp in employees
                ]
            except:
                results['employees'] = []
        
        # البحث في المركبات
        if 'vehicles' in search_in:
            try:
                vehicles = Vehicle.query.filter(
                    Vehicle.company_id == company_id,
                    or_(
                        Vehicle.plate_number.contains(query_text),
                        Vehicle.make.contains(query_text) if hasattr(Vehicle, 'make') else False,
                        Vehicle.model.contains(query_text) if hasattr(Vehicle, 'model') else False
                    )
                ).limit(10).all()
                
                results['vehicles'] = [
                    serialize_model(veh, fields=['id', 'plate_number', 'make', 'model', 'status'])
                    for veh in vehicles
                ]
            except:
                results['vehicles'] = []
        
        return api_response(results)
        
    except Exception as e:
        logger.error(f"خطأ في البحث المتقدم: {str(e)}")
        return api_error("خطأ في البحث")

# ==================== الإشعارات ====================

@api_bp.route('/notifications', methods=['GET'])
@login_required
def get_notifications():
    """جلب الإشعارات"""
    try:
        # نظام إشعارات مبسط
        notifications = [
            {
                "id": 1,
                "type": "info",
                "title": "مرحباً بك في نظام نُظم",
                "message": "تم تسجيل دخولك بنجاح إلى النظام",
                "created_at": datetime.utcnow().isoformat(),
                "read": False
            }
        ]
        
        # يمكن إضافة منطق أكثر تعقيداً هنا لجلب الإشعارات من قاعدة البيانات
        
        return api_response(notifications)
        
    except Exception as e:
        logger.error(f"خطأ في جلب الإشعارات: {str(e)}")
        return api_error("خطأ في جلب الإشعارات")

# ==================== معالج الأخطاء العام ====================

@api_bp.errorhandler(404)
def not_found(error):
    return api_error("المسار غير موجود", 404)

@api_bp.errorhandler(405)
def method_not_allowed(error):
    return api_error("الطريقة غير مسموحة", 405)

@api_bp.errorhandler(500)
def internal_error(error):
    return api_error("خطأ داخلي في الخادم", 500)

# ==================== مسارات إضافية مفيدة ====================

@api_bp.route('/health', methods=['GET'])
def health_check():
    """فحص صحة API"""
    return api_response({
        "status": "healthy",
        "version": "1.0",
        "timestamp": datetime.utcnow().isoformat()
    }, "API يعمل بشكل طبيعي")

@api_bp.route('/info', methods=['GET'])
def api_info():
    """معلومات API"""
    endpoints = {
        "authentication": {
            "login": "POST /api/v1/auth/login",
            "employee_login": "POST /api/v1/auth/employee-login"
        },
        "dashboard": {
            "stats": "GET /api/v1/dashboard/stats"
        },
        "employees": {
            "list": "GET /api/v1/employees",
            "get": "GET /api/v1/employees/{id}",
            "create": "POST /api/v1/employees",
            "update": "PUT /api/v1/employees/{id}",
            "delete": "DELETE /api/v1/employees/{id}",
            "salaries": "GET /api/v1/employees/{id}/salaries"
        },
        "vehicles": {
            "list": "GET /api/v1/vehicles",
            "get": "GET /api/v1/vehicles/{id}"
        },
        "departments": {
            "list": "GET /api/v1/departments"
        },
        "attendance": {
            "list": "GET /api/v1/attendance",
            "create": "POST /api/v1/attendance"
        },
        "reports": {
            "employees_summary": "GET /api/v1/reports/employees/summary",
            "monthly_attendance": "GET /api/v1/reports/attendance/monthly"
        },
        "search": "POST /api/v1/search",
        "notifications": "GET /api/v1/notifications",
        "health": "GET /api/v1/health",
        "info": "GET /api/v1/info"
    }
    
    return api_response({
        "name": "نُظم API",
        "version": "1.0",
        "description": "RESTful API شامل لنظام إدارة الموظفين والمركبات",
        "endpoints": endpoints
    })

# تسجيل تحميل المودول
logger.info("تم تحميل RESTful API نُظم بنجاح")
logger.info("جميع المسارات متاحة ومحمية من الأخطاء")