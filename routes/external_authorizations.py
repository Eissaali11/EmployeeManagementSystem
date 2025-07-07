"""
مسارات إدارة التفويضات الخارجية للموظفين
"""

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from sqlalchemy import or_
from models import db, Employee, Department, Project, ExternalAuthorization
from functools import wraps
import os
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime

external_authorizations_bp = Blueprint('external_authorizations', __name__, url_prefix='/external-authorizations')

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

@external_authorizations_bp.route('/create', methods=['POST'])
def create_authorization():
    """إنشاء تفويض خارجي جديد"""
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