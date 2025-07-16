from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime
from PIL import Image
from models import VehicleExternalSafetyCheck, VehicleSafetyImage, Vehicle, Employee, User, UserRole
from app import db
from utils.audit_logger import log_audit
from flask_login import current_user

external_safety_bp = Blueprint('external_safety', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def compress_image(image_path, max_size=1200, quality=85):
    """ضغط الصورة لتقليل حجمها"""
    try:
        with Image.open(image_path) as img:
            # تحويل RGBA إلى RGB إذا لزم الأمر
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # تغيير حجم الصورة إذا كانت أكبر من الحد المسموح
            if img.width > max_size or img.height > max_size:
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # حفظ الصورة المضغوطة
            img.save(image_path, 'JPEG', quality=quality, optimize=True)
            return True
    except Exception as e:
        current_app.logger.error(f"خطأ في ضغط الصورة: {str(e)}")
        return False

@external_safety_bp.route('/external-safety-check/<int:vehicle_id>')
def external_safety_check_form(vehicle_id):
    """عرض نموذج فحص السلامة الخارجي للسيارة"""
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    return render_template('external_safety_check.html', vehicle=vehicle)

@external_safety_bp.route('/share-links')
def share_links():
    """صفحة مشاركة روابط النماذج الخارجية لجميع السيارات مع الفلاتر"""
    # الحصول على معاملات الفلترة من الطلب
    status_filter = request.args.get('status', '')
    make_filter = request.args.get('make', '')
    search_plate = request.args.get('search_plate', '')
    project_filter = request.args.get('project', '')
    
    # قاعدة الاستعلام الأساسية
    query = Vehicle.query
    
    # إضافة التصفية حسب الحالة إذا تم تحديدها
    if status_filter:
        query = query.filter(Vehicle.status == status_filter)
    
    # إضافة التصفية حسب الشركة المصنعة إذا تم تحديدها
    if make_filter:
        query = query.filter(Vehicle.make == make_filter)
    
    # إضافة التصفية حسب المشروع إذا تم تحديده
    if project_filter:
        query = query.filter(Vehicle.project == project_filter)
    
    # إضافة البحث برقم السيارة إذا تم تحديده
    if search_plate:
        query = query.filter(Vehicle.plate_number.contains(search_plate))
    
    # الحصول على قائمة بالشركات المصنعة لقائمة التصفية
    makes = db.session.query(Vehicle.make).distinct().all()
    makes = [make[0] for make in makes]
    
    # الحصول على قائمة بالمشاريع لقائمة التصفية
    projects = db.session.query(Vehicle.project).filter(Vehicle.project.isnot(None)).distinct().all()
    projects = [project[0] for project in projects]
    
    # الحصول على قائمة السيارات
    vehicles = query.order_by(Vehicle.status, Vehicle.plate_number).all()
    
    # قائمة حالات السيارات
    statuses = ['available', 'rented', 'in_project', 'in_workshop', 'accident']
    
    return render_template('external_safety_share_links.html', 
                           vehicles=vehicles,
                           status_filter=status_filter,
                           make_filter=make_filter,
                           search_plate=search_plate,
                           project_filter=project_filter,
                           makes=makes,
                           projects=projects,
                           statuses=statuses)

@external_safety_bp.route('/external-safety-check', methods=['POST'])
def submit_external_safety_check():
    """إرسال طلب فحص السلامة الخارجي"""
    try:
        # التحقق من البيانات المطلوبة
        required_fields = ['vehicle_id', 'driver_national_id', 'driver_name', 'driver_department', 'driver_city']
        for field in required_fields:
            if not request.form.get(field):
                return jsonify({'error': f'الحقل {field} مطلوب'}), 400
        
        # التحقق من وجود السيارة
        vehicle = Vehicle.query.get(request.form.get('vehicle_id'))
        if not vehicle:
            return jsonify({'error': 'السيارة غير موجودة'}), 404
        
        # إنشاء سجل فحص السلامة
        safety_check = VehicleExternalSafetyCheck(
            vehicle_id=vehicle.id,
            driver_name=request.form.get('driver_name'),
            driver_national_id=request.form.get('driver_national_id'),
            driver_department=request.form.get('driver_department'),
            driver_city=request.form.get('driver_city'),
            vehicle_plate_number=request.form.get('vehicle_plate_number'),
            vehicle_make_model=request.form.get('vehicle_make_model'),
            current_delegate=request.form.get('current_delegate'),
            notes=request.form.get('notes'),
            inspection_date=datetime.now()
        )
        
        db.session.add(safety_check)
        db.session.flush()  # للحصول على ID
        
        # معالجة الصور المرفوعة
        uploaded_files = request.files.getlist('safety_images')
        descriptions = request.form.getlist('image_descriptions')
        
        if uploaded_files:
            # إنشاء مجلد للصور
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'safety_checks')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            
            for i, file in enumerate(uploaded_files):
                if file and file.filename and allowed_file(file.filename):
                    # إنشاء اسم ملف آمن
                    file_extension = file.filename.rsplit('.', 1)[1].lower()
                    filename = f"safety_{safety_check.id}_{uuid.uuid4().hex}.{file_extension}"
                    file_path = os.path.join(upload_folder, filename)
                    
                    # حفظ الملف
                    file.save(file_path)
                    
                    # ضغط الصورة
                    compress_image(file_path)
                    
                    # حفظ معلومات الصورة في قاعدة البيانات
                    description = descriptions[i] if i < len(descriptions) else None
                    
                    safety_image = VehicleSafetyImage(
                        safety_check_id=safety_check.id,
                        image_path=f'uploads/safety_checks/{filename}',
                        image_description=description
                    )
                    
                    db.session.add(safety_image)
        
        # حفظ جميع التغييرات
        db.session.commit()
        
        # تسجيل العملية في سجل المراجعة
        log_audit(
            user_id=current_user.id if current_user.is_authenticated else None,
            action='create',
            entity_type='VehicleExternalSafetyCheck',
            entity_id=safety_check.id,
            details=f'تم إنشاء طلب فحص السلامة الخارجي للسيارة {vehicle.plate_number} بواسطة {safety_check.driver_name}'
        )
        
        return jsonify({'success': True, 'message': 'تم إرسال طلب فحص السلامة بنجاح'}), 200
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"خطأ في إرسال طلب فحص السلامة: {str(e)}")
        return jsonify({'error': 'حدث خطأ في إرسال الطلب'}), 500

@external_safety_bp.route('/api/verify-employee/<national_id>')
def verify_employee(national_id):
    """التحقق من الموظف بواسطة رقم الهوية"""
    try:
        # البحث عن الموظف بواسطة رقم الهوية
        employee = Employee.query.filter_by(national_id=national_id).first()
        
        if not employee:
            return jsonify({'success': False, 'message': 'الموظف غير موجود'}), 404
        
        # الحصول على أسماء الأقسام
        department_names = [dept.name for dept in employee.departments] if employee.departments else []
        
        return jsonify({
            'success': True,
            'employee': {
                'id': employee.id,
                'name': employee.name,
                'department': ', '.join(department_names) if department_names else 'غير محدد',
                'city': employee.city if hasattr(employee, 'city') else 'الرياض',
                'national_id': employee.national_id
            }
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"خطأ في التحقق من الموظف: {str(e)}")
        return jsonify({'success': False, 'message': 'حدث خطأ في التحقق من الموظف'}), 500

@external_safety_bp.route('/external-safety-check/success')
def external_safety_success():
    """صفحة نجاح إرسال طلب فحص السلامة"""
    return render_template('external_safety_success.html')

@external_safety_bp.route('/admin/external-safety-checks')
def admin_external_safety_checks():
    """عرض جميع طلبات فحص السلامة للإدارة"""
    # التحقق من صلاحيات الإدارة
    if not current_user.is_authenticated or current_user.role != UserRole.ADMIN:
        flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('main.index'))
    
    # جلب جميع طلبات فحص السلامة
    safety_checks = VehicleExternalSafetyCheck.query.order_by(
        VehicleExternalSafetyCheck.created_at.desc()
    ).all()
    
    return render_template('admin_external_safety_checks.html', safety_checks=safety_checks)

@external_safety_bp.route('/admin/external-safety-check/<int:check_id>')
def admin_view_safety_check(check_id):
    """عرض تفاصيل طلب فحص السلامة"""
    if not current_user.is_authenticated or current_user.role != UserRole.ADMIN:
        flash('غير مصرح لك بالوصول إلى هذه الصفحة', 'error')
        return redirect(url_for('main.index'))
    
    safety_check = VehicleExternalSafetyCheck.query.get_or_404(check_id)
    return render_template('admin_view_safety_check.html', safety_check=safety_check)

@external_safety_bp.route('/admin/external-safety-check/<int:check_id>/approve', methods=['POST'])
def approve_safety_check(check_id):
    """اعتماد طلب فحص السلامة"""
    if not current_user.is_authenticated or current_user.role != UserRole.ADMIN:
        return jsonify({'error': 'غير مصرح لك'}), 403
    
    try:
        safety_check = VehicleExternalSafetyCheck.query.get_or_404(check_id)
        
        safety_check.approval_status = 'approved'
        safety_check.approved_by = current_user.id
        safety_check.approved_at = datetime.now()
        
        db.session.commit()
        
        # تسجيل العملية
        log_audit(
            user_id=current_user.id,
            action='approve',
            entity_type='VehicleExternalSafetyCheck',
            entity_id=safety_check.id,
            details=f'تم اعتماد طلب فحص السلامة للسيارة {safety_check.vehicle_plate_number}'
        )
        
        flash('تم اعتماد طلب فحص السلامة بنجاح', 'success')
        return redirect(url_for('external_safety.admin_view_safety_check', check_id=check_id))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"خطأ في اعتماد طلب فحص السلامة: {str(e)}")
        flash('حدث خطأ في اعتماد الطلب', 'error')
        return redirect(url_for('external_safety.admin_view_safety_check', check_id=check_id))

@external_safety_bp.route('/admin/external-safety-check/<int:check_id>/reject', methods=['POST'])
def reject_safety_check(check_id):
    """رفض طلب فحص السلامة"""
    if not current_user.is_authenticated or current_user.role != UserRole.ADMIN:
        return jsonify({'error': 'غير مصرح لك'}), 403
    
    try:
        safety_check = VehicleExternalSafetyCheck.query.get_or_404(check_id)
        
        safety_check.approval_status = 'rejected'
        safety_check.approved_by = current_user.id
        safety_check.approved_at = datetime.now()
        safety_check.rejection_reason = request.form.get('rejection_reason', '')
        
        db.session.commit()
        
        # تسجيل العملية
        log_audit(
            user_id=current_user.id,
            action='reject',
            entity_type='VehicleExternalSafetyCheck',
            entity_id=safety_check.id,
            details=f'تم رفض طلب فحص السلامة للسيارة {safety_check.vehicle_plate_number}. السبب: {safety_check.rejection_reason}'
        )
        
        flash('تم رفض طلب فحص السلامة', 'success')
        return redirect(url_for('external_safety.admin_view_safety_check', check_id=check_id))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"خطأ في رفض طلب فحص السلامة: {str(e)}")
        flash('حدث خطأ في رفض الطلب', 'error')
        return redirect(url_for('external_safety.admin_view_safety_check', check_id=check_id))