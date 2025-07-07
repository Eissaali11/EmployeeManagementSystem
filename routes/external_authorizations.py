from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
import os
import uuid
from datetime import datetime
from sqlalchemy.orm import joinedload
from sqlalchemy import or_, and_

from app import db
from models import ExternalAuthorization, Employee, Department, Project, User
from functools import wraps
from flask import abort

# دالة admin_required محلية
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        if not hasattr(current_user, 'role') or current_user.role.value not in ['ADMIN', 'SYSTEM_ADMIN']:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
from utils.audit_logger import log_activity
from werkzeug.utils import secure_filename

external_authorizations_bp = Blueprint('external_authorizations', __name__, url_prefix='/external-authorizations')

# تحديد أنواع الملفات المسموحة
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@external_authorizations_bp.route('/')
@login_required
def index():
    """صفحة عرض جميع التفويضات الخارجية"""
    
    # جلب الفلاتر من الطلب
    department_filter = request.args.get('department', '')
    project_filter = request.args.get('project', '')
    status_filter = request.args.get('status', '')
    search_query = request.args.get('search', '')
    
    # بناء الاستعلام الأساسي
    query = db.session.query(ExternalAuthorization)\
        .options(
            joinedload(ExternalAuthorization.employee)\
                .joinedload(Employee.departments),
            joinedload(ExternalAuthorization.project),
            joinedload(ExternalAuthorization.creator),
            joinedload(ExternalAuthorization.approver)
        )
    
    # تطبيق الفلاتر
    if department_filter:
        query = query.join(Employee).join(Employee.departments)\
            .filter(Department.id == department_filter)
    
    if project_filter:
        query = query.filter(ExternalAuthorization.project_id == project_filter)
    
    if status_filter:
        query = query.filter(ExternalAuthorization.status == status_filter)
    
    if search_query:
        query = query.join(Employee).filter(
            or_(
                Employee.name.ilike(f'%{search_query}%'),
                Employee.employee_id.ilike(f'%{search_query}%'),
                ExternalAuthorization.description.ilike(f'%{search_query}%')
            )
        )
    
    # ترتيب النتائج
    authorizations = query.order_by(ExternalAuthorization.created_at.desc()).all()
    
    # جلب بيانات الفلاتر
    departments = Department.query.order_by(Department.name).all()
    projects = Project.query.filter(Project.status == 'active').order_by(Project.name).all()
    
    # إحصائيات سريعة
    stats = {
        'total': ExternalAuthorization.query.count(),
        'pending': ExternalAuthorization.query.filter_by(status='pending').count(),
        'approved': ExternalAuthorization.query.filter_by(status='approved').count(),
        'rejected': ExternalAuthorization.query.filter_by(status='rejected').count()
    }
    
    return render_template('external_authorizations/index.html',
                         authorizations=authorizations,
                         departments=departments,
                         projects=projects,
                         stats=stats,
                         filters={
                             'department': department_filter,
                             'project': project_filter,
                             'status': status_filter,
                             'search': search_query
                         })

@external_authorizations_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """إنشاء تفويض خارجي جديد"""
    
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        project_id = request.form.get('project_id')
        description = request.form.get('description', '').strip()
        external_link = request.form.get('external_link', '').strip()
        
        # التحقق من صحة البيانات
        if not employee_id or not project_id:
            flash('يجب اختيار الموظف والمشروع', 'error')
            return redirect(url_for('external_authorizations.create'))
        
        # التحقق من وجود الموظف والمشروع
        employee = Employee.query.get(employee_id)
        project = Project.query.get(project_id)
        
        if not employee or not project:
            flash('الموظف أو المشروع غير موجود', 'error')
            return redirect(url_for('external_authorizations.create'))
        
        # معالجة رفع الملف
        file_path = None
        if 'authorization_file' in request.files:
            file = request.files['authorization_file']
            if file and file.filename and allowed_file(file.filename):
                # إنشاء اسم ملف آمن
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                
                # إنشاء مجلد التخزين إذا لم يكن موجوداً
                upload_folder = os.path.join(current_app.static_folder, 'uploads', 'authorizations')
                os.makedirs(upload_folder, exist_ok=True)
                
                # حفظ الملف
                file_path = os.path.join('uploads', 'authorizations', unique_filename)
                full_path = os.path.join(current_app.static_folder, 'uploads', 'authorizations', unique_filename)
                file.save(full_path)
        
        # إنشاء التفويض الجديد
        authorization = ExternalAuthorization(
            employee_id=employee_id,
            project_id=project_id,
            description=description,
            file_path=file_path,
            external_link=external_link if external_link else None,
            created_by=current_user.id,
            status='pending'
        )
        
        try:
            db.session.add(authorization)
            db.session.commit()
            
            # تسجيل العملية
            log_activity('create', 'external_authorization', 
                        f'تم إنشاء تفويض خارجي للموظف: {employee.name} في المشروع: {project.name}')
            
            flash('تم إنشاء التفويض الخارجي بنجاح', 'success')
            return redirect(url_for('external_authorizations.index'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating external authorization: {str(e)}")
            flash('حدث خطأ أثناء إنشاء التفويض', 'error')
    
    # جلب البيانات للنموذج
    departments = Department.query.order_by(Department.name).all()
    projects = Project.query.filter(Project.status == 'active').order_by(Project.name).all()
    
    return render_template('external_authorizations/create.html',
                         departments=departments,
                         projects=projects)

@external_authorizations_bp.route('/api/employees')
@login_required
def api_employees():
    """API لجلب الموظفين مع إمكانية الفلترة"""
    
    department_id = request.args.get('department_id')
    search_query = request.args.get('search', '').strip()
    
    # بناء الاستعلام
    query = db.session.query(Employee)\
        .options(joinedload(Employee.departments))\
        .filter(Employee.status == 'active')
    
    # فلترة حسب القسم
    if department_id:
        query = query.join(Employee.departments)\
            .filter(Department.id == department_id)
    
    # فلترة حسب البحث
    if search_query:
        query = query.filter(
            or_(
                Employee.name.ilike(f'%{search_query}%'),
                Employee.employee_id.ilike(f'%{search_query}%')
            )
        )
    
    employees = query.order_by(Employee.name).limit(50).all()
    
    # تحويل البيانات للتنسيق المطلوب
    result = []
    for employee in employees:
        departments_list = [dept.name for dept in employee.departments]
        result.append({
            'id': employee.id,
            'name': employee.name,
            'employee_id': employee.employee_id,
            'departments': departments_list,
            'departments_str': ', '.join(departments_list)
        })
    
    return jsonify(result)

@external_authorizations_bp.route('/<int:auth_id>')
@login_required
def view(auth_id):
    """عرض تفاصيل التفويض"""
    
    authorization = ExternalAuthorization.query\
        .options(
            joinedload(ExternalAuthorization.employee)\
                .joinedload(Employee.departments),
            joinedload(ExternalAuthorization.project),
            joinedload(ExternalAuthorization.creator),
            joinedload(ExternalAuthorization.approver)
        )\
        .get_or_404(auth_id)
    
    return render_template('external_authorizations/view.html',
                         authorization=authorization)

@external_authorizations_bp.route('/<int:auth_id>/approve', methods=['POST'])
@login_required
@admin_required
def approve(auth_id):
    """الموافقة على التفويض"""
    
    authorization = ExternalAuthorization.query.get_or_404(auth_id)
    notes = request.form.get('notes', '').strip()
    
    authorization.status = 'approved'
    authorization.approved_by = current_user.id
    authorization.approved_date = datetime.utcnow()
    if notes:
        authorization.notes = notes
    
    try:
        db.session.commit()
        
        # تسجيل العملية
        log_activity('approve', 'external_authorization', 
                    f'تم اعتماد التفويض الخارجي للموظف: {authorization.employee.name}')
        
        flash('تم اعتماد التفويض بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error approving authorization: {str(e)}")
        flash('حدث خطأ أثناء اعتماد التفويض', 'error')
    
    return redirect(url_for('external_authorizations.view', auth_id=auth_id))

@external_authorizations_bp.route('/<int:auth_id>/reject', methods=['POST'])
@login_required
@admin_required
def reject(auth_id):
    """رفض التفويض"""
    
    authorization = ExternalAuthorization.query.get_or_404(auth_id)
    notes = request.form.get('notes', '').strip()
    
    if not notes:
        flash('يجب إدخال سبب الرفض', 'error')
        return redirect(url_for('external_authorizations.view', auth_id=auth_id))
    
    authorization.status = 'rejected'
    authorization.approved_by = current_user.id
    authorization.approved_date = datetime.utcnow()
    authorization.notes = notes
    
    try:
        db.session.commit()
        
        # تسجيل العملية
        log_activity('reject', 'external_authorization', 
                    f'تم رفض التفويض الخارجي للموظف: {authorization.employee.name}')
        
        flash('تم رفض التفويض', 'info')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error rejecting authorization: {str(e)}")
        flash('حدث خطأ أثناء رفض التفويض', 'error')
    
    return redirect(url_for('external_authorizations.view', auth_id=auth_id))

@external_authorizations_bp.route('/<int:auth_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(auth_id):
    """حذف التفويض"""
    
    authorization = ExternalAuthorization.query.get_or_404(auth_id)
    employee_name = authorization.employee.name
    
    # حذف الملف المرفق إذا كان موجوداً
    if authorization.file_path:
        file_full_path = os.path.join(current_app.static_folder, authorization.file_path)
        if os.path.exists(file_full_path):
            try:
                os.remove(file_full_path)
            except Exception as e:
                current_app.logger.warning(f"Could not delete file {file_full_path}: {str(e)}")
    
    try:
        db.session.delete(authorization)
        db.session.commit()
        
        # تسجيل العملية
        log_activity('delete', 'external_authorization', 
                    f'تم حذف التفويض الخارجي للموظف: {employee_name}')
        
        flash('تم حذف التفويض بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting authorization: {str(e)}")
        flash('حدث خطأ أثناء حذف التفويض', 'error')
    
    return redirect(url_for('external_authorizations.index'))