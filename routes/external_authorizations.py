"""
مسارات إدارة التفويضات الخارجية للموظفين
"""

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash, current_app
from sqlalchemy import or_
from models import db, Employee, Department, Project, ExternalAuthorization
from functools import wraps
import os
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime

external_authorizations_bp = Blueprint('external_authorizations', __name__, url_prefix='/external-authorizations')

@external_authorizations_bp.route('/')
def index():
    """الصفحة الرئيسية لإدارة التفويضات الخارجية"""
    from models import ExternalAuthorization, Vehicle, Employee, Department
    
    # جلب جميع التفويضات مع بيانات المركبات والموظفين
    authorizations = ExternalAuthorization.query.all()
    current_app.logger.info(f"عدد التفويضات الموجودة: {len(authorizations)}")
    
    return render_template('external_authorizations/index.html', authorizations=authorizations)

@external_authorizations_bp.route('/view/<int:id>')
def view_authorization(id):
    """عرض تفاصيل التفويض الخارجي"""
    from models import ExternalAuthorization
    authorization = ExternalAuthorization.query.get_or_404(id)
    return render_template('external_authorizations/view.html', authorization=authorization)

@external_authorizations_bp.route('/edit/<int:id>')
def edit_authorization(id):
    """تعديل التفويض الخارجي"""
    from models import ExternalAuthorization
    authorization = ExternalAuthorization.query.get_or_404(id)
    return redirect(url_for('external_authorizations.create_authorization', vehicle_id=authorization.vehicle_id, edit_id=id))

@external_authorizations_bp.route('/approve/<int:id>')
def approve_authorization(id):
    """الموافقة على التفويض الخارجي"""
    from models import ExternalAuthorization
    authorization = ExternalAuthorization.query.get_or_404(id)
    authorization.status = 'approved'
    db.session.commit()
    flash('تم الموافقة على التفويض بنجاح', 'success')
    return redirect(url_for('vehicles.view', id=authorization.vehicle_id))

@external_authorizations_bp.route('/reject/<int:id>')
def reject_authorization(id):
    """رفض التفويض الخارجي"""
    from models import ExternalAuthorization
    authorization = ExternalAuthorization.query.get_or_404(id)
    authorization.status = 'rejected'
    db.session.commit()
    flash('تم رفض التفويض', 'warning')
    return redirect(url_for('vehicles.view', id=authorization.vehicle_id))

@external_authorizations_bp.route('/delete/<int:id>')
def delete_authorization(id):
    """حذف التفويض الخارجي"""
    from models import ExternalAuthorization
    authorization = ExternalAuthorization.query.get_or_404(id)
    vehicle_id = authorization.vehicle_id
    
    # حذف الملف المرفق إذا كان موجوداً
    if authorization.file_path and os.path.exists(authorization.file_path):
        try:
            os.remove(authorization.file_path)
        except:
            pass
    
    db.session.delete(authorization)
    db.session.commit()
    flash('تم حذف التفويض بنجاح', 'success')
    return redirect(url_for('vehicles.view', id=vehicle_id))

@external_authorizations_bp.route('/add/')
@external_authorizations_bp.route('/add/<int:vehicle_id>')
def create_authorization(vehicle_id=None):
    """صفحة إضافة تفويض خارجي جديد"""
    from models import Vehicle, Employee
    from flask_wtf import FlaskForm
    
    # إذا لم يتم تحديد مركبة، استخدم أول مركبة متاحة
    if vehicle_id is None:
        vehicle = Vehicle.query.first()
        if not vehicle:
            flash('لا توجد مركبات متاحة', 'error')
            return redirect(url_for('vehicles.index'))
    else:
        vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    form = FlaskForm()  # نموذج بسيط للحماية من CSRF
    
    # جلب جميع الموظفين مع أقسامهم
    employees = Employee.query.options(db.joinedload(Employee.departments)).all()
    
    # جلب جميع الأقسام للفلترة
    from models import Department
    departments = Department.query.all()
    
    return render_template('external_authorizations/create.html', 
                         vehicle=vehicle, form=form, employees=employees, departments=departments)

@external_authorizations_bp.route('/store', methods=['POST'])
def store_authorization():
    """حفظ التفويض الخارجي الجديد"""
    try:
        from models import ExternalAuthorization
        from flask import request, current_app, flash, redirect, url_for
        import os
        from datetime import datetime
        
        # بيانات النموذج
        vehicle_id = request.form.get('vehicle_id')
        employee_id = request.form.get('employee_id')
        project_id = request.form.get('project_id')
        city = request.form.get('city')
        authorization_type = request.form.get('authorization_type')
        duration = request.form.get('duration')
        authorization_form_link = request.form.get('authorization_form_link')
        external_reference = request.form.get('external_reference')
        notes = request.form.get('notes', '')
        
        # جلب بيانات الموظف والمشروع
        employee = Employee.query.get(employee_id) if employee_id else None
        department = Department.query.get(project_id) if project_id else None
        
        driver_name = employee.name if employee else None
        driver_phone = employee.mobile if employee else None
        project_name = department.name if department else None
        
        # إنشاء التفويض الجديد
        authorization = ExternalAuthorization(
            vehicle_id=vehicle_id,
            driver_name=driver_name,
            driver_phone=driver_phone,
            project_name=project_name,
            city=city,
            authorization_type=authorization_type,
            duration=duration,
            notes=notes,
            status='pending'
        )
        
        # معالجة رفع الملف إذا وجد
        uploaded_file = request.files.get('file_upload')
        if uploaded_file and uploaded_file.filename:
            # إنشاء مجلد للتفويضات إذا لم يكن موجوداً
            upload_dir = os.path.join('static', 'uploads', 'authorizations')
            os.makedirs(upload_dir, exist_ok=True)
            
            # حفظ الملف
            filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uploaded_file.filename}"
            file_path = os.path.join(upload_dir, filename)
            uploaded_file.save(file_path)
            authorization.file_path = file_path
        
        # حفظ في قاعدة البيانات
        db.session.add(authorization)
        db.session.commit()
        
        flash('تم إنشاء التفويض الخارجي بنجاح!', 'success')
        return redirect(url_for('vehicles.view', id=vehicle_id))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"خطأ أثناء حفظ التفويض: {str(e)}")
        flash(f'حدث خطأ أثناء حفظ التفويض: {str(e)}', 'danger')
        return redirect(url_for('external_authorizations.create_authorization', vehicle_id=vehicle_id))

# إعدادات رفع الملفات
UPLOAD_FOLDER = 'static/uploads/authorizations'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_upload_dir():
    """التأكد من وجود مجلد الرفع"""
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

@external_authorizations_bp.route('/api/employees')
def api_employees():
    """API للبحث في الموظفين مع الفلترة"""
    try:
        search = request.args.get('search', '').strip()
        department_id = request.args.get('department_id', '')
        
        # بناء الاستعلام الأساسي
        query = Employee.query
        
        # فلترة حسب القسم إذا تم تحديده
        if department_id:
            query = query.filter(Employee.departments.any(Department.id == department_id))
        
        # البحث في الاسم أو رقم الموظف
        if search:
            query = query.filter(
                or_(
                    Employee.name.ilike(f'%{search}%'),
                    Employee.employee_id.ilike(f'%{search}%'),
                    Employee.national_id.ilike(f'%{search}%')
                )
            )
        
        # تحديد النتائج
        employees = query.limit(20).all()
        
        # تنسيق البيانات للإرسال
        result = []
        for emp in employees:
            departments_list = [dept.name for dept in emp.departments]
            result.append({
                'id': emp.id,
                'name': emp.name,
                'employee_id': emp.employee_id,
                'national_id': emp.national_id,
                'departments_str': ', '.join(departments_list) if departments_list else 'غير محدد'
            })
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@external_authorizations_bp.route('/api/departments')
def api_departments():
    """API لجلب جميع الأقسام"""
    try:
        departments = Department.query.all()
        result = [{'id': dept.id, 'name': dept.name} for dept in departments]
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@external_authorizations_bp.route('/api/projects')
def api_projects():
    """API لجلب جميع المشاريع"""
    try:
        projects = Project.query.all()
        result = [{'id': proj.id, 'name': proj.name} for proj in projects]
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@external_authorizations_bp.route('/old-create', methods=['POST'])
def old_create_authorization():
    """إنشاء تفويض خارجي جديد - المسار القديم"""
    try:
        ensure_upload_dir()
        
        # جلب البيانات من النموذج
        employee_id = request.form.get('employee_id')
        vehicle_id = request.form.get('vehicle_id')
        project_id = request.form.get('project_id')
        authorization_type = request.form.get('authorization_type', 'تسليم')
        description = request.form.get('description', '')
        external_link = request.form.get('external_link', '')
        
        # التحقق من البيانات المطلوبة
        if not employee_id or not vehicle_id or not project_id:
            return jsonify({'error': 'البيانات المطلوبة مفقودة'}), 400
        
        # معالجة رفع الملف
        file_path = None
        if 'authorization_file' in request.files:
            file = request.files['authorization_file']
            if file and file.filename and allowed_file(file.filename):
                # إنشاء اسم ملف فريد
                filename = secure_filename(file.filename)
                unique_filename = f"{uuid.uuid4()}_{filename}"
                file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
                file.save(file_path)
                # حفظ المسار النسبي
                file_path = f"uploads/authorizations/{unique_filename}"
        
        # إنشاء سجل التفويض
        authorization = ExternalAuthorization(
            employee_id=employee_id,
            vehicle_id=vehicle_id,
            project_id=project_id,
            authorization_type=authorization_type,
            description=description,
            external_link=external_link if external_link else None,
            file_path=file_path,
            status='pending',
            created_at=datetime.utcnow()
        )
        
        db.session.add(authorization)
        db.session.commit()
        
        return jsonify({'message': 'تم إنشاء التفويض بنجاح', 'id': authorization.id}), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'حدث خطأ: {str(e)}'}), 500

@external_authorizations_bp.route('/vehicle/<int:vehicle_id>')
def get_vehicle_authorizations(vehicle_id):
    """جلب تفويضات سيارة معينة"""
    try:
        authorizations = ExternalAuthorization.query.filter_by(vehicle_id=vehicle_id).all()
        
        result = []
        for auth in authorizations:
            result.append({
                'id': auth.id,
                'employee_name': auth.employee.name if auth.employee else 'غير محدد',
                'project_name': auth.project.name if auth.project else 'غير محدد',
                'authorization_type': auth.authorization_type,
                'description': auth.description,
                'external_link': auth.external_link,
                'file_path': auth.file_path,
                'status': auth.status,
                'status_text': {
                    'pending': 'في الانتظار',
                    'approved': 'موافق عليه',
                    'rejected': 'مرفوض'
                }.get(auth.status, 'غير محدد'),
                'created_at': auth.created_at.strftime('%Y-%m-%d %H:%M') if auth.created_at else ''
            })
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500