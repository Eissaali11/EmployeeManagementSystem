from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy import extract, func, or_
import os
import uuid
import io
import urllib.parse
from fpdf import FPDF

from app import db
from models import (
    Vehicle, VehicleRental, VehicleWorkshop, VehicleWorkshopImage, 
    VehicleProject, VehicleHandover, VehicleHandoverImage, SystemAudit,
    VehiclePeriodicInspection, VehicleSafetyCheck, Employee
)
from utils.vehicles_export import export_vehicle_pdf, export_workshop_records_pdf, export_vehicle_excel, export_workshop_records_excel
from utils.vehicle_report import generate_complete_vehicle_report
from utils.vehicle_excel_report import generate_complete_vehicle_excel_report
from utils.workshop_report import generate_workshop_report_pdf

vehicles_bp = Blueprint('vehicles', __name__, url_prefix='/vehicles')

# قائمة بأهم حالات السيارة للاختيار منها في النماذج
VEHICLE_STATUS_CHOICES = [
    'available',  # متاحة
    'rented',  # مؤجرة
    'in_project',  # في المشروع
    'in_workshop',  # في الورشة
    'accident'  # حادث
]

# قائمة بأسباب دخول الورشة
WORKSHOP_REASON_CHOICES = [
    'maintenance',  # صيانة دورية
    'breakdown',  # عطل
    'accident'  # حادث
]

# قائمة بحالات الإصلاح في الورشة
REPAIR_STATUS_CHOICES = [
    'in_progress',  # قيد التنفيذ
    'completed',  # تم الإصلاح
    'pending_approval'  # بانتظار الموافقة
]

# قائمة بأنواع عمليات التسليم والاستلام
HANDOVER_TYPE_CHOICES = [
    'delivery',  # تسليم
    'return'  # استلام
]

# قائمة بأنواع الفحص الدوري
INSPECTION_TYPE_CHOICES = [
    'technical',  # فحص فني
    'periodic',   # فحص دوري
    'safety'      # فحص أمان
]

# قائمة بحالات الفحص الدوري
INSPECTION_STATUS_CHOICES = [
    'valid',          # ساري
    'expired',        # منتهي
    'expiring_soon'   # على وشك الانتهاء
]

# قائمة بأنواع فحص السلامة
SAFETY_CHECK_TYPE_CHOICES = [
    'daily',    # يومي
    'weekly',   # أسبوعي
    'monthly'   # شهري
]

# قائمة بحالات فحص السلامة
SAFETY_CHECK_STATUS_CHOICES = [
    'completed',      # مكتمل
    'in_progress',    # قيد التنفيذ
    'needs_review'    # بحاجة للمراجعة
]

# الوظائف المساعدة
def save_image(file, folder='vehicles'):
    """حفظ الصورة في المجلد المحدد وإرجاع المسار"""
    if not file:
        return None
    
    # إنشاء اسم فريد للملف
    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4()}_{filename}"
    
    # التأكد من وجود المجلد
    upload_folder = os.path.join(current_app.static_folder, 'uploads', folder)
    os.makedirs(upload_folder, exist_ok=True)
    
    # حفظ الملف
    file_path = os.path.join(upload_folder, unique_filename)
    file.save(file_path)
    
    # إرجاع المسار النسبي للملف
    return f"uploads/{folder}/{unique_filename}"

def format_date_arabic(date_obj):
    """تنسيق التاريخ باللغة العربية"""
    months = {
        1: 'يناير', 2: 'فبراير', 3: 'مارس', 4: 'أبريل', 
        5: 'مايو', 6: 'يونيو', 7: 'يوليو', 8: 'أغسطس',
        9: 'سبتمبر', 10: 'أكتوبر', 11: 'نوفمبر', 12: 'ديسمبر'
    }
    return f"{date_obj.day} {months[date_obj.month]} {date_obj.year}"

def log_audit(action, entity_type, entity_id, details=None):
    """تسجيل الإجراء في سجل النظام"""
    audit = SystemAudit(
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
        user_id=current_user.id if current_user.is_authenticated else None
    )
    db.session.add(audit)
    db.session.commit()

def calculate_rental_adjustment(vehicle_id, year, month):
    """حساب الخصم على إيجار السيارة بناءً على أيام وجودها في الورشة"""
    # الحصول على الإيجار النشط للسيارة
    rental = VehicleRental.query.filter_by(vehicle_id=vehicle_id, is_active=True).first()
    if not rental:
        return 0
    
    # الحصول على سجلات الورشة للسيارة في الشهر والسنة المحددين
    workshop_records = VehicleWorkshop.query.filter_by(vehicle_id=vehicle_id).filter(
        extract('year', VehicleWorkshop.entry_date) == year,
        extract('month', VehicleWorkshop.entry_date) == month
    ).all()
    
    # حساب عدد الأيام التي قضتها السيارة في الورشة
    total_days_in_workshop = 0
    for record in workshop_records:
        if record.exit_date:
            # إذا كان هناك تاريخ خروج، نحسب الفرق بين تاريخ الدخول والخروج
            delta = (record.exit_date - record.entry_date).days
            total_days_in_workshop += delta
        else:
            # إذا لم يكن هناك تاريخ خروج، نحسب الفرق حتى نهاية الشهر
            last_day_of_month = 30  # تقريبي، يمكن تحسينه
            entry_day = record.entry_date.day
            days_remaining = last_day_of_month - entry_day
            total_days_in_workshop += days_remaining
    
    # حساب الخصم اليومي (الإيجار الشهري / 30)
    daily_rent = rental.monthly_cost / 30
    adjustment = daily_rent * total_days_in_workshop
    
    return adjustment

# المسارات الأساسية
@vehicles_bp.route('/')
@login_required
def index():
    """عرض قائمة السيارات مع خيارات التصفية"""
    status_filter = request.args.get('status', '')
    make_filter = request.args.get('make', '')
    
    # قاعدة الاستعلام الأساسية
    query = Vehicle.query
    
    # إضافة التصفية حسب الحالة إذا تم تحديدها
    if status_filter:
        query = query.filter(Vehicle.status == status_filter)
    
    # إضافة التصفية حسب الشركة المصنعة إذا تم تحديدها
    if make_filter:
        query = query.filter(Vehicle.make == make_filter)
    
    # الحصول على قائمة بالشركات المصنعة لقائمة التصفية
    makes = db.session.query(Vehicle.make).distinct().all()
    makes = [make[0] for make in makes]
    
    # الحصول على قائمة السيارات
    vehicles = query.order_by(Vehicle.status, Vehicle.plate_number).all()
    
    # إحصائيات سريعة
    stats = {
        'total': Vehicle.query.count(),
        'available': Vehicle.query.filter_by(status='available').count(),
        'rented': Vehicle.query.filter_by(status='rented').count(),
        'in_project': Vehicle.query.filter_by(status='in_project').count(),
        'in_workshop': Vehicle.query.filter_by(status='in_workshop').count(),
        'accident': Vehicle.query.filter_by(status='accident').count()
    }
    
    return render_template(
        'vehicles/index.html',
        vehicles=vehicles,
        stats=stats,
        status_filter=status_filter,
        make_filter=make_filter,
        makes=makes,
        statuses=VEHICLE_STATUS_CHOICES
    )

@vehicles_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """إضافة سيارة جديدة"""
    if request.method == 'POST':
        # استخراج البيانات من النموذج
        plate_number = request.form.get('plate_number')
        make = request.form.get('make')
        model = request.form.get('model')
        year = request.form.get('year')
        color = request.form.get('color')
        status = request.form.get('status')
        notes = request.form.get('notes')
        
        # التحقق من عدم وجود سيارة بنفس رقم اللوحة
        if Vehicle.query.filter_by(plate_number=plate_number).first():
            flash('يوجد سيارة مسجلة بنفس رقم اللوحة!', 'danger')
            return redirect(url_for('vehicles.create'))
        
        # إنشاء سيارة جديدة
        vehicle = Vehicle(
            plate_number=plate_number,
            make=make,
            model=model,
            year=int(year),
            color=color,
            status=status,
            notes=notes
        )
        
        db.session.add(vehicle)
        db.session.commit()
        
        # تسجيل الإجراء
        log_audit('create', 'vehicle', vehicle.id, f'تمت إضافة سيارة جديدة: {vehicle.plate_number}')
        
        flash('تمت إضافة السيارة بنجاح!', 'success')
        return redirect(url_for('vehicles.index'))
    
    return render_template('vehicles/create.html', statuses=VEHICLE_STATUS_CHOICES)

@vehicles_bp.route('/<int:id>')
@login_required
def view(id):
    """عرض تفاصيل سيارة معينة"""
    vehicle = Vehicle.query.get_or_404(id)
    
    # الحصول على سجلات مختلفة للسيارة
    rental = VehicleRental.query.filter_by(vehicle_id=id, is_active=True).first()
    workshop_records = VehicleWorkshop.query.filter_by(vehicle_id=id).order_by(VehicleWorkshop.entry_date.desc()).all()
    project_assignments = VehicleProject.query.filter_by(vehicle_id=id).order_by(VehicleProject.start_date.desc()).all()
    handover_records = VehicleHandover.query.filter_by(vehicle_id=id).order_by(VehicleHandover.handover_date.desc()).all()
    
    # الحصول على سجلات الفحص الدوري وفحص السلامة
    periodic_inspections = VehiclePeriodicInspection.query.filter_by(vehicle_id=id).order_by(VehiclePeriodicInspection.inspection_date.desc()).all()
    safety_checks = VehicleSafetyCheck.query.filter_by(vehicle_id=id).order_by(VehicleSafetyCheck.check_date.desc()).all()
    
    # حساب تكلفة الإصلاحات الإجمالية
    total_maintenance_cost = db.session.query(func.sum(VehicleWorkshop.cost)).filter_by(vehicle_id=id).scalar() or 0
    
    # حساب عدد الأيام في الورشة (للسنة الحالية)
    current_year = datetime.now().year
    days_in_workshop = 0
    for record in workshop_records:
        if record.entry_date.year == current_year:
            if record.exit_date:
                days_in_workshop += (record.exit_date - record.entry_date).days
            else:
                days_in_workshop += (datetime.now().date() - record.entry_date).days
    
    # تنسيق التواريخ
    for record in workshop_records:
        record.formatted_entry_date = format_date_arabic(record.entry_date)
        if record.exit_date:
            record.formatted_exit_date = format_date_arabic(record.exit_date)
    
    for record in project_assignments:
        record.formatted_start_date = format_date_arabic(record.start_date)
        if record.end_date:
            record.formatted_end_date = format_date_arabic(record.end_date)
    
    for record in handover_records:
        record.formatted_handover_date = format_date_arabic(record.handover_date)
    
    for record in periodic_inspections:
        record.formatted_inspection_date = format_date_arabic(record.inspection_date)
        record.formatted_expiry_date = format_date_arabic(record.expiry_date)
    
    for record in safety_checks:
        record.formatted_check_date = format_date_arabic(record.check_date)
    
    if rental:
        rental.formatted_start_date = format_date_arabic(rental.start_date)
        if rental.end_date:
            rental.formatted_end_date = format_date_arabic(rental.end_date)
    
    # ملاحظات تنبيهية عن انتهاء الفحص الدوري
    inspection_warnings = []
    for inspection in periodic_inspections:
        if inspection.is_expired:
            inspection_warnings.append(f"الفحص الدوري منتهي الصلاحية منذ {(datetime.now().date() - inspection.expiry_date).days} يومًا")
            break
        elif inspection.is_expiring_soon:
            days_remaining = (inspection.expiry_date - datetime.now().date()).days
            inspection_warnings.append(f"الفحص الدوري سينتهي خلال {days_remaining} يومًا")
            break
    
    return render_template(
        'vehicles/view.html',
        vehicle=vehicle,
        rental=rental,
        workshop_records=workshop_records,
        project_assignments=project_assignments,
        handover_records=handover_records,
        periodic_inspections=periodic_inspections,
        safety_checks=safety_checks,
        total_maintenance_cost=total_maintenance_cost,
        days_in_workshop=days_in_workshop,
        inspection_warnings=inspection_warnings
    )

@vehicles_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """تعديل بيانات سيارة"""
    vehicle = Vehicle.query.get_or_404(id)
    
    if request.method == 'POST':
        # استخراج البيانات من النموذج
        plate_number = request.form.get('plate_number')
        make = request.form.get('make')
        model = request.form.get('model')
        year = request.form.get('year')
        color = request.form.get('color')
        status = request.form.get('status')
        notes = request.form.get('notes')
        
        # التحقق من عدم وجود سيارة أخرى بنفس رقم اللوحة
        existing = Vehicle.query.filter_by(plate_number=plate_number).first()
        if existing and existing.id != id:
            flash('يوجد سيارة أخرى مسجلة بنفس رقم اللوحة!', 'danger')
            return redirect(url_for('vehicles.edit', id=id))
        
        # تحديث بيانات السيارة
        vehicle.plate_number = plate_number
        vehicle.make = make
        vehicle.model = model
        vehicle.year = int(year)
        vehicle.color = color
        vehicle.status = status
        vehicle.notes = notes
        vehicle.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # تسجيل الإجراء
        log_audit('update', 'vehicle', vehicle.id, f'تم تعديل بيانات السيارة: {vehicle.plate_number}')
        
        flash('تم تعديل بيانات السيارة بنجاح!', 'success')
        return redirect(url_for('vehicles.view', id=id))
    
    return render_template('vehicles/edit.html', vehicle=vehicle, statuses=VEHICLE_STATUS_CHOICES)

@vehicles_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """حذف سيارة"""
    vehicle = Vehicle.query.get_or_404(id)
    
    # تسجيل الإجراء قبل الحذف
    plate_number = vehicle.plate_number
    log_audit('delete', 'vehicle', id, f'تم حذف السيارة: {plate_number}')
    
    db.session.delete(vehicle)
    db.session.commit()
    
    flash('تم حذف السيارة ومعلوماتها بنجاح!', 'success')
    return redirect(url_for('vehicles.index'))

# مسارات إدارة الإيجار
@vehicles_bp.route('/<int:id>/rental/create', methods=['GET', 'POST'])
@login_required
def create_rental(id):
    """إضافة معلومات إيجار لسيارة"""
    vehicle = Vehicle.query.get_or_404(id)
    
    # التحقق من عدم وجود إيجار نشط حالياً
    existing_rental = VehicleRental.query.filter_by(vehicle_id=id, is_active=True).first()
    if existing_rental and request.method == 'GET':
        flash('يوجد إيجار نشط بالفعل لهذه السيارة!', 'warning')
        return redirect(url_for('vehicles.view', id=id))
    
    if request.method == 'POST':
        # استخراج البيانات من النموذج
        start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
        end_date_str = request.form.get('end_date')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
        monthly_cost = float(request.form.get('monthly_cost'))
        lessor_name = request.form.get('lessor_name')
        lessor_contact = request.form.get('lessor_contact')
        contract_number = request.form.get('contract_number')
        city = request.form.get('city')
        notes = request.form.get('notes')
        
        # إلغاء تنشيط الإيجارات السابقة
        if existing_rental:
            existing_rental.is_active = False
            existing_rental.updated_at = datetime.utcnow()
        
        # إنشاء سجل إيجار جديد
        rental = VehicleRental(
            vehicle_id=id,
            start_date=start_date,
            end_date=end_date,
            monthly_cost=monthly_cost,
            is_active=True,
            lessor_name=lessor_name,
            lessor_contact=lessor_contact,
            contract_number=contract_number,
            city=city,
            notes=notes
        )
        
        db.session.add(rental)
        
        # تحديث حالة السيارة
        vehicle.status = 'rented'
        vehicle.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # تسجيل الإجراء
        log_audit('create', 'vehicle_rental', rental.id, f'تم إضافة معلومات إيجار للسيارة: {vehicle.plate_number}')
        
        flash('تم إضافة معلومات الإيجار بنجاح!', 'success')
        return redirect(url_for('vehicles.view', id=id))
    
    return render_template('vehicles/rental_create.html', vehicle=vehicle)

@vehicles_bp.route('/rental/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_rental(id):
    """تعديل معلومات إيجار"""
    rental = VehicleRental.query.get_or_404(id)
    vehicle = Vehicle.query.get_or_404(rental.vehicle_id)
    
    if request.method == 'POST':
        # استخراج البيانات من النموذج
        start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
        end_date_str = request.form.get('end_date')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
        monthly_cost = float(request.form.get('monthly_cost'))
        is_active = bool(request.form.get('is_active'))
        lessor_name = request.form.get('lessor_name')
        lessor_contact = request.form.get('lessor_contact')
        contract_number = request.form.get('contract_number')
        city = request.form.get('city')
        notes = request.form.get('notes')
        
        # تحديث معلومات الإيجار
        rental.start_date = start_date
        rental.end_date = end_date
        rental.monthly_cost = monthly_cost
        rental.is_active = is_active
        rental.lessor_name = lessor_name
        rental.lessor_contact = lessor_contact
        rental.contract_number = contract_number
        rental.city = city
        rental.notes = notes
        rental.updated_at = datetime.utcnow()
        
        # تحديث حالة السيارة حسب حالة الإيجار
        if is_active:
            vehicle.status = 'rented'
        else:
            vehicle.status = 'available'
        vehicle.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # تسجيل الإجراء
        log_audit('update', 'vehicle_rental', rental.id, f'تم تعديل معلومات إيجار السيارة: {vehicle.plate_number}')
        
        flash('تم تعديل معلومات الإيجار بنجاح!', 'success')
        return redirect(url_for('vehicles.view', id=vehicle.id))
    
    return render_template('vehicles/rental_edit.html', rental=rental, vehicle=vehicle)

# مسارات إدارة الورشة
@vehicles_bp.route('/<int:id>/workshop/create', methods=['GET', 'POST'])
@login_required
def create_workshop(id):
    """إضافة سجل دخول السيارة للورشة"""
    vehicle = Vehicle.query.get_or_404(id)
    
    if request.method == 'POST':
        # استخراج البيانات من النموذج
        entry_date = datetime.strptime(request.form.get('entry_date'), '%Y-%m-%d').date()
        exit_date_str = request.form.get('exit_date')
        exit_date = datetime.strptime(exit_date_str, '%Y-%m-%d').date() if exit_date_str else None
        reason = request.form.get('reason')
        description = request.form.get('description')
        repair_status = request.form.get('repair_status')
        cost = float(request.form.get('cost') or 0)
        workshop_name = request.form.get('workshop_name')
        technician_name = request.form.get('technician_name')
        delivery_link = request.form.get('delivery_link')
        notes = request.form.get('notes')
        
        # إنشاء سجل ورشة جديد
        workshop_record = VehicleWorkshop(
            vehicle_id=id,
            entry_date=entry_date,
            exit_date=exit_date,
            reason=reason,
            description=description,
            repair_status=repair_status,
            cost=cost,
            workshop_name=workshop_name,
            technician_name=technician_name,
            delivery_link=delivery_link,
            notes=notes
        )
        
        db.session.add(workshop_record)
        
        # تحديث حالة السيارة
        if not exit_date:
            vehicle.status = 'in_workshop'
        vehicle.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # معالجة الصور المرفقة
        before_images = request.files.getlist('before_images')
        after_images = request.files.getlist('after_images')
        
        for image in before_images:
            if image and image.filename:
                image_path = save_image(image, 'workshop')
                if image_path:
                    image_record = VehicleWorkshopImage(
                        workshop_record_id=workshop_record.id,
                        image_type='before',
                        image_path=image_path
                    )
                    db.session.add(image_record)
        
        for image in after_images:
            if image and image.filename:
                image_path = save_image(image, 'workshop')
                if image_path:
                    image_record = VehicleWorkshopImage(
                        workshop_record_id=workshop_record.id,
                        image_type='after',
                        image_path=image_path
                    )
                    db.session.add(image_record)
        
        db.session.commit()
        
        # تسجيل الإجراء
        log_audit('create', 'vehicle_workshop', workshop_record.id, 
                 f'تم إضافة سجل دخول الورشة للسيارة: {vehicle.plate_number}')
        
        flash('تم إضافة سجل دخول الورشة بنجاح!', 'success')
        return redirect(url_for('vehicles.view', id=id))
    
    return render_template(
        'vehicles/workshop_create.html', 
        vehicle=vehicle, 
        reasons=WORKSHOP_REASON_CHOICES,
        statuses=REPAIR_STATUS_CHOICES
    )

@vehicles_bp.route('/workshop/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_workshop(id):
    """تعديل سجل ورشة"""
    workshop = VehicleWorkshop.query.get_or_404(id)
    vehicle = Vehicle.query.get_or_404(workshop.vehicle_id)
    
    if request.method == 'POST':
        # استخراج البيانات من النموذج
        entry_date = datetime.strptime(request.form.get('entry_date'), '%Y-%m-%d').date()
        exit_date_str = request.form.get('exit_date')
        exit_date = datetime.strptime(exit_date_str, '%Y-%m-%d').date() if exit_date_str else None
        reason = request.form.get('reason')
        description = request.form.get('description')
        repair_status = request.form.get('repair_status')
        cost = float(request.form.get('cost') or 0)
        workshop_name = request.form.get('workshop_name')
        technician_name = request.form.get('technician_name')
        delivery_link = request.form.get('delivery_link')
        reception_link = request.form.get('reception_link')
        notes = request.form.get('notes')
        
        # تحديث سجل الورشة
        workshop.entry_date = entry_date
        workshop.exit_date = exit_date
        workshop.reason = reason
        workshop.description = description
        workshop.repair_status = repair_status
        workshop.cost = cost
        workshop.workshop_name = workshop_name
        workshop.technician_name = technician_name
        workshop.delivery_link = delivery_link
        workshop.reception_link = reception_link
        workshop.notes = notes
        workshop.updated_at = datetime.utcnow()
        
        # تحديث حالة السيارة
        if exit_date and repair_status == 'completed':
            # التحقق من وجود سجلات ورشة أخرى نشطة
            other_active_records = VehicleWorkshop.query.filter(
                VehicleWorkshop.vehicle_id == vehicle.id,
                VehicleWorkshop.id != id,
                VehicleWorkshop.exit_date.is_(None)
            ).count()
            
            if other_active_records == 0:
                # تحديث حالة السيارة إذا لم تكن هناك سجلات ورشة أخرى نشطة
                # إذا كانت السيارة مؤجرة، نعيدها إلى حالة "مؤجرة"
                active_rental = VehicleRental.query.filter_by(vehicle_id=vehicle.id, is_active=True).first()
                active_project = VehicleProject.query.filter_by(vehicle_id=vehicle.id, is_active=True).first()
                
                if active_rental:
                    vehicle.status = 'rented'
                elif active_project:
                    vehicle.status = 'in_project'
                else:
                    vehicle.status = 'available'
        
        vehicle.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # معالجة الصور المرفقة الجديدة
        before_images = request.files.getlist('before_images')
        after_images = request.files.getlist('after_images')
        
        for image in before_images:
            if image and image.filename:
                image_path = save_image(image, 'workshop')
                if image_path:
                    image_record = VehicleWorkshopImage(
                        workshop_record_id=id,
                        image_type='before',
                        image_path=image_path
                    )
                    db.session.add(image_record)
        
        for image in after_images:
            if image and image.filename:
                image_path = save_image(image, 'workshop')
                if image_path:
                    image_record = VehicleWorkshopImage(
                        workshop_record_id=id,
                        image_type='after',
                        image_path=image_path
                    )
                    db.session.add(image_record)
        
        db.session.commit()
        
        # تسجيل الإجراء
        log_audit('update', 'vehicle_workshop', workshop.id, 
                 f'تم تعديل سجل الورشة للسيارة: {vehicle.plate_number}')
        
        flash('تم تعديل سجل الورشة بنجاح!', 'success')
        return redirect(url_for('vehicles.view', id=vehicle.id))
    
    # الحصول على الصور الحالية مفصولة حسب النوع
    before_images = VehicleWorkshopImage.query.filter_by(
        workshop_record_id=id, image_type='before').all()
    after_images = VehicleWorkshopImage.query.filter_by(
        workshop_record_id=id, image_type='after').all()
    
    return render_template(
        'vehicles/workshop_edit.html', 
        workshop=workshop, 
        vehicle=vehicle,
        before_images=before_images,
        after_images=after_images,
        reasons=WORKSHOP_REASON_CHOICES,
        statuses=REPAIR_STATUS_CHOICES
    )

@vehicles_bp.route('/workshop/image/<int:id>/delete', methods=['POST'])
@login_required
def delete_workshop_image(id):
    """حذف صورة من سجل الورشة"""
    image = VehicleWorkshopImage.query.get_or_404(id)
    workshop_id = image.workshop_record_id
    workshop = VehicleWorkshop.query.get_or_404(workshop_id)
    
    # حذف الملف الفعلي إذا كان موجوداً
    file_path = os.path.join(current_app.static_folder, image.image_path)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    db.session.delete(image)
    db.session.commit()
    
    # تسجيل الإجراء
    log_audit('delete', 'vehicle_workshop_image', id, 
             f'تم حذف صورة من سجل الورشة للسيارة: {workshop.vehicle.plate_number}')
    
    flash('تم حذف الصورة بنجاح!', 'success')
    return redirect(url_for('vehicles.edit_workshop', id=workshop_id))

# مسارات إدارة المشاريع
@vehicles_bp.route('/<int:id>/project/create', methods=['GET', 'POST'])
@login_required
def create_project(id):
    """تخصيص السيارة لمشروع"""
    vehicle = Vehicle.query.get_or_404(id)
    
    # التحقق من عدم وجود تخصيص نشط حالياً
    existing_assignment = VehicleProject.query.filter_by(vehicle_id=id, is_active=True).first()
    if existing_assignment and request.method == 'GET':
        flash('هذه السيارة مخصصة بالفعل لمشروع نشط!', 'warning')
        return redirect(url_for('vehicles.view', id=id))
    
    if request.method == 'POST':
        # استخراج البيانات من النموذج
        project_name = request.form.get('project_name')
        location = request.form.get('location')
        manager_name = request.form.get('manager_name')
        start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
        end_date_str = request.form.get('end_date')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
        notes = request.form.get('notes')
        
        # إلغاء تنشيط التخصيصات السابقة
        if existing_assignment:
            existing_assignment.is_active = False
            existing_assignment.updated_at = datetime.utcnow()
        
        # إنشاء تخصيص جديد
        project = VehicleProject(
            vehicle_id=id,
            project_name=project_name,
            location=location,
            manager_name=manager_name,
            start_date=start_date,
            end_date=end_date,
            is_active=True,
            notes=notes
        )
        
        db.session.add(project)
        
        # تحديث حالة السيارة
        vehicle.status = 'in_project'
        vehicle.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # تسجيل الإجراء
        log_audit('create', 'vehicle_project', project.id, 
                 f'تم تخصيص السيارة {vehicle.plate_number} لمشروع {project_name}')
        
        flash('تم تخصيص السيارة للمشروع بنجاح!', 'success')
        return redirect(url_for('vehicles.view', id=id))
    
    return render_template('vehicles/project_create.html', vehicle=vehicle)

@vehicles_bp.route('/project/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(id):
    """تعديل تخصيص المشروع"""
    project = VehicleProject.query.get_or_404(id)
    vehicle = Vehicle.query.get_or_404(project.vehicle_id)
    
    if request.method == 'POST':
        # استخراج البيانات من النموذج
        project_name = request.form.get('project_name')
        location = request.form.get('location')
        manager_name = request.form.get('manager_name')
        start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
        end_date_str = request.form.get('end_date')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
        is_active = bool(request.form.get('is_active'))
        notes = request.form.get('notes')
        
        # تحديث التخصيص
        project.project_name = project_name
        project.location = location
        project.manager_name = manager_name
        project.start_date = start_date
        project.end_date = end_date
        project.is_active = is_active
        project.notes = notes
        project.updated_at = datetime.utcnow()
        
        # تحديث حالة السيارة
        if is_active:
            vehicle.status = 'in_project'
        else:
            # التحقق مما إذا كانت السيارة مؤجرة
            active_rental = VehicleRental.query.filter_by(vehicle_id=vehicle.id, is_active=True).first()
            
            if active_rental:
                vehicle.status = 'rented'
            else:
                vehicle.status = 'available'
        
        vehicle.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # تسجيل الإجراء
        log_audit('update', 'vehicle_project', project.id, 
                 f'تم تعديل تخصيص السيارة {vehicle.plate_number} للمشروع {project_name}')
        
        flash('تم تعديل تخصيص المشروع بنجاح!', 'success')
        return redirect(url_for('vehicles.view', id=vehicle.id))
    
    return render_template('vehicles/project_edit.html', project=project, vehicle=vehicle)

# مسارات تسليم واستلام السيارات
@vehicles_bp.route('/<int:id>/handover/create', methods=['GET', 'POST'])
@login_required
def create_handover(id):
    """إنشاء نموذج تسليم/استلام للسيارة"""
    vehicle = Vehicle.query.get_or_404(id)
    
    if request.method == 'POST':
        # استخراج البيانات من النموذج
        handover_type = request.form.get('handover_type')
        handover_date = datetime.strptime(request.form.get('handover_date'), '%Y-%m-%d').date()
        person_name = request.form.get('person_name')
        vehicle_condition = request.form.get('vehicle_condition')
        fuel_level = request.form.get('fuel_level')
        mileage = int(request.form.get('mileage'))
        has_spare_tire = 'has_spare_tire' in request.form
        has_fire_extinguisher = 'has_fire_extinguisher' in request.form
        has_first_aid_kit = 'has_first_aid_kit' in request.form
        has_warning_triangle = 'has_warning_triangle' in request.form
        has_tools = 'has_tools' in request.form
        form_link = request.form.get('form_link')
        notes = request.form.get('notes')
        
        # إنشاء سجل تسليم/استلام جديد
        handover = VehicleHandover(
            vehicle_id=id,
            handover_type=handover_type,
            handover_date=handover_date,
            person_name=person_name,
            vehicle_condition=vehicle_condition,
            fuel_level=fuel_level,
            mileage=mileage,
            has_spare_tire=has_spare_tire,
            has_fire_extinguisher=has_fire_extinguisher,
            has_first_aid_kit=has_first_aid_kit,
            has_warning_triangle=has_warning_triangle,
            has_tools=has_tools,
            form_link=form_link,
            notes=notes
        )
        
        db.session.add(handover)
        db.session.commit()
        
        # معالجة الصور المرفقة
        images = request.files.getlist('images')
        
        for image in images:
            if image and image.filename:
                image_path = save_image(image, 'handover')
                if image_path:
                    image_description = request.form.get(f'description_{image.filename}', '')
                    image_record = VehicleHandoverImage(
                        handover_record_id=handover.id,
                        image_path=image_path,
                        image_description=image_description
                    )
                    db.session.add(image_record)
        
        db.session.commit()
        
        # تسجيل الإجراء
        action_type = 'تسليم' if handover_type == 'delivery' else 'استلام'
        log_audit('create', 'vehicle_handover', handover.id, 
                 f'تم إنشاء نموذج {action_type} للسيارة: {vehicle.plate_number}')
        
        flash(f'تم إنشاء نموذج {action_type} بنجاح!', 'success')
        return redirect(url_for('vehicles.view', id=id))
    
    return render_template(
        'vehicles/handover_create.html', 
        vehicle=vehicle,
        handover_types=HANDOVER_TYPE_CHOICES
    )

@vehicles_bp.route('/handover/<int:id>/view')
@login_required
def view_handover(id):
    """عرض تفاصيل نموذج تسليم/استلام"""
    handover = VehicleHandover.query.get_or_404(id)
    vehicle = Vehicle.query.get_or_404(handover.vehicle_id)
    images = VehicleHandoverImage.query.filter_by(handover_record_id=id).all()
    
    # تنسيق التاريخ
    handover.formatted_handover_date = format_date_arabic(handover.handover_date)
    
    handover_type_name = 'تسليم' if handover.handover_type == 'delivery' else 'استلام'
    
    return render_template(
        'vehicles/handover_view.html',
        handover=handover,
        vehicle=vehicle,
        images=images,
        handover_type_name=handover_type_name
    )

@vehicles_bp.route('/handover/<int:id>/pdf')
@login_required
def handover_pdf(id):
    """إنشاء نموذج تسليم/استلام كملف PDF"""
    from flask import send_file, flash, redirect, url_for
    import io
    import os
    from datetime import datetime
    # استخدام ملف pdf_generator_fixed بدلاً من pdf_generator_new
    from utils.pdf_generator_fixed import generate_vehicle_handover_pdf
    
    try:
        # التأكد من تحويل المعرف إلى عدد صحيح
        id = int(id) if not isinstance(id, int) else id
        
        # جلب البيانات
        handover = VehicleHandover.query.get_or_404(id)
        vehicle = Vehicle.query.get_or_404(handover.vehicle_id)
        
        # تجهيز البيانات
        handover_data = {
            'vehicle': {
                'plate_number': str(vehicle.plate_number),
                'make': str(vehicle.make),
                'model': str(vehicle.model),
                'year': int(vehicle.year),
                'color': str(vehicle.color)
            },
            'handover_type': 'تسليم' if handover.handover_type == 'delivery' else 'استلام',
            'handover_date': handover.handover_date.strftime('%Y-%m-%d'),
            'person_name': str(handover.person_name),
            'vehicle_condition': str(handover.vehicle_condition),
            'fuel_level': str(handover.fuel_level),
            'mileage': int(handover.mileage),
            'has_spare_tire': bool(handover.has_spare_tire),
            'has_fire_extinguisher': bool(handover.has_fire_extinguisher),
            'has_first_aid_kit': bool(handover.has_first_aid_kit),
            'has_warning_triangle': bool(handover.has_warning_triangle),
            'has_tools': bool(handover.has_tools),
            'notes': str(handover.notes) if handover.notes else "",
            'form_link': str(handover.form_link) if handover.form_link else ""
        }
        
        # إنشاء ملف PDF باستخدام الوظيفة الجديدة
        pdf_bytes = generate_vehicle_handover_pdf(handover_data)
        
        # تحديد اسم الملف
        filename = f"handover_form_{vehicle.plate_number}.pdf"
        
        # إرسال الملف للمستخدم
        return send_file(
            io.BytesIO(pdf_bytes),
            download_name=filename,
            as_attachment=True,
            mimetype='application/pdf'
        )
    except Exception as e:
        # في حالة حدوث خطأ، عرض رسالة الخطأ والعودة إلى صفحة عرض السيارة
        flash(f'خطأ في إنشاء ملف PDF: {str(e)}', 'danger')
        return redirect(url_for('vehicles.view', id=vehicle.id if 'vehicle' in locals() else id))

# مسارات التقارير والإحصائيات
@vehicles_bp.route('/dashboard')
@login_required
def dashboard():
    """لوحة المعلومات والإحصائيات للسيارات"""
    # إجمالي عدد السيارات
    total_vehicles = Vehicle.query.count()
    
    # توزيع السيارات حسب الحالة
    status_stats = db.session.query(
        Vehicle.status, func.count(Vehicle.id)
    ).group_by(Vehicle.status).all()
    
    status_dict = {status: count for status, count in status_stats}
    
    # حساب قيمة الإيجارات الشهرية
    total_monthly_rent = db.session.query(
        func.sum(VehicleRental.monthly_cost)
    ).filter_by(is_active=True).scalar() or 0
    
    # السيارات في الورشة حالياً
    vehicles_in_workshop = VehicleWorkshop.query.filter(
        VehicleWorkshop.exit_date.is_(None)
    ).count()
    
    # تكاليف الصيانة الإجمالية (للسنة الحالية)
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    yearly_maintenance_cost = db.session.query(
        func.sum(VehicleWorkshop.cost)
    ).filter(
        extract('year', VehicleWorkshop.entry_date) == current_year
    ).scalar() or 0
    
    # تكاليف الصيانة الشهرية (للأشهر الستة الماضية)
    monthly_costs = []
    for i in range(6):
        month = current_month - i
        year = current_year
        if month <= 0:
            month += 12
            year -= 1
        
        month_cost = db.session.query(
            func.sum(VehicleWorkshop.cost)
        ).filter(
            extract('year', VehicleWorkshop.entry_date) == year,
            extract('month', VehicleWorkshop.entry_date) == month
        ).scalar() or 0
        
        month_name = [
            'يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو',
            'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'
        ][month - 1]
        
        monthly_costs.append({
            'month': month_name,
            'cost': month_cost
        })
    
    # عكس ترتيب القائمة لعرض الأشهر من الأقدم إلى الأحدث
    monthly_costs.reverse()
    
    # قائمة التنبيهات
    alerts = []
    
    # تنبيهات السيارات في الورشة لفترة طويلة (أكثر من أسبوعين)
    long_workshop_stays = VehicleWorkshop.query.filter(
        VehicleWorkshop.exit_date.is_(None),
        VehicleWorkshop.entry_date <= (datetime.now().date() - timedelta(days=14))
    ).all()
    
    for stay in long_workshop_stays:
        days = (datetime.now().date() - stay.entry_date).days
        vehicle = Vehicle.query.get(stay.vehicle_id)
        alerts.append({
            'type': 'workshop',
            'message': f'السيارة {vehicle.plate_number} في الورشة منذ {days} يوم',
            'vehicle_id': vehicle.id
        })
    
    # تنبيهات الإيجارات التي ستنتهي قريباً (خلال أسبوع)
    ending_rentals = VehicleRental.query.filter(
        VehicleRental.is_active == True,
        VehicleRental.end_date.isnot(None),
        VehicleRental.end_date <= (datetime.now().date() + timedelta(days=7)),
        VehicleRental.end_date >= datetime.now().date()
    ).all()
    
    for rental in ending_rentals:
        days = (rental.end_date - datetime.now().date()).days
        vehicle = Vehicle.query.get(rental.vehicle_id)
        alerts.append({
            'type': 'rental',
            'message': f'إيجار السيارة {vehicle.plate_number} سينتهي خلال {days} يوم',
            'vehicle_id': vehicle.id
        })
    
    # إعداد بيانات حالة السيارات بالتنسيق المطلوب في القالب
    status_counts = {
        'available': status_dict.get('available', 0),
        'rented': status_dict.get('rented', 0),
        'in_project': status_dict.get('in_project', 0),
        'in_workshop': status_dict.get('in_workshop', 0),
        'accident': status_dict.get('accident', 0)
    }
    
    # تجميع الإحصائيات في كائن واحد
    stats = {
        'total_vehicles': total_vehicles,
        'status_stats': status_dict,
        'status_counts': status_counts,  # إضافة حالات السيارات بالتنسيق المناسب للقالب
        'total_monthly_rent': total_monthly_rent,
        'total_rental_cost': total_monthly_rent,  # نفس القيمة تستخدم في القالب باسم مختلف
        'vehicles_in_workshop': vehicles_in_workshop,
        'yearly_maintenance_cost': yearly_maintenance_cost,
        'new_vehicles_last_month': Vehicle.query.filter(
            Vehicle.created_at >= (datetime.now() - timedelta(days=30))
        ).count(),  # عدد السيارات المضافة في الشهر الماضي
        
        # تكاليف الورشة للشهر الحالي
        'workshop_cost_current_month': db.session.query(
            func.sum(VehicleWorkshop.cost)
        ).filter(
            extract('year', VehicleWorkshop.entry_date) == current_year,
            extract('month', VehicleWorkshop.entry_date) == current_month
        ).scalar() or 0,
        
        # عدد السيارات في المشاريع
        'vehicles_in_projects': Vehicle.query.filter_by(status='in_project').count(),
        
        # عدد المشاريع النشطة
        'project_assignments_count': db.session.query(
            func.count(func.distinct(VehicleProject.project_name))
        ).filter_by(is_active=True).scalar() or 0
    }
    
    return render_template(
        'vehicles/dashboard.html',
        stats=stats,
        monthly_costs=monthly_costs,
        alerts=alerts
    )

@vehicles_bp.route('/reports')
@login_required
def reports():
    """صفحة تقارير السيارات"""
    # توزيع السيارات حسب الشركة المصنعة
    make_stats = db.session.query(
        Vehicle.make, func.count(Vehicle.id)
    ).group_by(Vehicle.make).all()
    
    # توزيع السيارات حسب سنة الصنع
    year_stats = db.session.query(
        Vehicle.year, func.count(Vehicle.id)
    ).group_by(Vehicle.year).order_by(Vehicle.year).all()
    
    # إحصائيات الورشة
    workshop_reason_stats = db.session.query(
        VehicleWorkshop.reason, func.count(VehicleWorkshop.id)
    ).group_by(VehicleWorkshop.reason).all()
    
    # إجمالي تكاليف الصيانة لكل سيارة (أعلى 10 سيارات)
    top_maintenance_costs = db.session.query(
        Vehicle.plate_number, Vehicle.make, Vehicle.model, 
        func.sum(VehicleWorkshop.cost).label('total_cost')
    ).join(
        VehicleWorkshop, Vehicle.id == VehicleWorkshop.vehicle_id
    ).group_by(
        Vehicle.id, Vehicle.plate_number, Vehicle.make, Vehicle.model
    ).order_by(
        func.sum(VehicleWorkshop.cost).desc()
    ).limit(10).all()
    
    return render_template(
        'vehicles/reports.html',
        make_stats=make_stats,
        year_stats=year_stats,
        workshop_reason_stats=workshop_reason_stats,
        top_maintenance_costs=top_maintenance_costs
    )

@vehicles_bp.route('/detailed')
@login_required
def detailed_list():
    """قائمة تفصيلية للسيارات مع معلومات إضافية لكل سيارة على حدة"""
    # إعداد قيم التصفية
    status = request.args.get('status')
    make = request.args.get('make')
    year = request.args.get('year')
    project = request.args.get('project')
    location = request.args.get('location')
    sort = request.args.get('sort', 'plate_number')
    search = request.args.get('search', '')
    
    # استعلام قاعدة البيانات مع التصفية
    query = Vehicle.query
    
    if status:
        query = query.filter(Vehicle.status == status)
    if make:
        query = query.filter(Vehicle.make == make)
    if year:
        query = query.filter(Vehicle.year == int(year))
    if search:
        query = query.filter(
            or_(
                Vehicle.plate_number.ilike(f'%{search}%'),
                Vehicle.make.ilike(f'%{search}%'),
                Vehicle.model.ilike(f'%{search}%'),
                Vehicle.color.ilike(f'%{search}%')
            )
        )
    
    # فلترة حسب المشروع
    if project:
        vehicle_ids = db.session.query(VehicleProject.vehicle_id).filter_by(
            project_name=project, is_active=True
        ).all()
        vehicle_ids = [v[0] for v in vehicle_ids]
        query = query.filter(Vehicle.id.in_(vehicle_ids))
    
    # فلترة حسب الموقع (المنطقة)
    if location:
        vehicle_ids = db.session.query(VehicleProject.vehicle_id).filter_by(
            location=location, is_active=True
        ).all()
        vehicle_ids = [v[0] for v in vehicle_ids]
        query = query.filter(Vehicle.id.in_(vehicle_ids))
    
    # ترتيب النتائج
    if sort == 'make':
        query = query.order_by(Vehicle.make, Vehicle.model)
    elif sort == 'year':
        query = query.order_by(Vehicle.year.desc())
    elif sort == 'status':
        query = query.order_by(Vehicle.status)
    elif sort == 'created_at':
        query = query.order_by(Vehicle.created_at.desc())
    else:
        query = query.order_by(Vehicle.plate_number)
    
    # الترقيم
    page = request.args.get('page', 1, type=int)
    pagination = query.paginate(page=page, per_page=20, error_out=False)
    vehicles = pagination.items
    
    # استخراج معلومات إضافية لكل سيارة
    for vehicle in vehicles:
        # معلومات الإيجار النشط
        vehicle.active_rental = VehicleRental.query.filter_by(
            vehicle_id=vehicle.id, is_active=True
        ).first()
        
        # معلومات آخر دخول للورشة
        vehicle.latest_workshop = VehicleWorkshop.query.filter_by(
            vehicle_id=vehicle.id
        ).order_by(VehicleWorkshop.entry_date.desc()).first()
        
        # معلومات المشروع الحالي
        vehicle.active_project = VehicleProject.query.filter_by(
            vehicle_id=vehicle.id, is_active=True
        ).first()
    
    # استخراج قوائم الفلاتر
    makes = db.session.query(Vehicle.make).distinct().order_by(Vehicle.make).all()
    makes = [make[0] for make in makes]
    
    years = db.session.query(Vehicle.year).distinct().order_by(Vehicle.year.desc()).all()
    years = [year[0] for year in years]
    
    # استخراج قائمة المشاريع النشطة
    projects = db.session.query(VehicleProject.project_name).filter_by(
        is_active=True
    ).distinct().order_by(VehicleProject.project_name).all()
    projects = [project[0] for project in projects]
    
    # استخراج قائمة المواقع (المناطق)
    locations = db.session.query(VehicleProject.location).distinct().order_by(
        VehicleProject.location
    ).all()
    locations = [location[0] for location in locations]
    
    return render_template(
        'vehicles/detailed_list.html',
        vehicles=vehicles,
        pagination=pagination,
        makes=makes,
        years=years,
        projects=projects,
        locations=locations,
        total_count=Vehicle.query.count(),
        request=request
    )

@vehicles_bp.route('/report/export/excel')
@login_required
def export_vehicles_excel():
    """تصدير بيانات السيارات إلى ملف Excel"""
    import io
    import pandas as pd
    from flask import send_file
    import datetime
    
    status_filter = request.args.get('status', '')
    make_filter = request.args.get('make', '')
    
    # قاعدة الاستعلام الأساسية
    query = Vehicle.query
    
    # إضافة التصفية حسب الحالة إذا تم تحديدها
    if status_filter:
        query = query.filter(Vehicle.status == status_filter)
    
    # إضافة التصفية حسب الشركة المصنعة إذا تم تحديدها
    if make_filter:
        query = query.filter(Vehicle.make == make_filter)
    
    # الحصول على قائمة السيارات
    vehicles = query.order_by(Vehicle.status, Vehicle.plate_number).all()
    
    # تحويل حالة السيارة إلى نص مقروء بالعربية
    status_map = {
        'available': 'متاحة',
        'rented': 'مؤجرة',
        'in_project': 'في المشروع',
        'in_workshop': 'في الورشة',
        'accident': 'حادث'
    }
    
    # إنشاء قائمة بالبيانات
    vehicle_data = []
    for vehicle in vehicles:
        # حساب تكاليف الصيانة الإجمالية
        total_maintenance_cost = db.session.query(
            func.sum(VehicleWorkshop.cost)
        ).filter(
            VehicleWorkshop.vehicle_id == vehicle.id
        ).scalar() or 0
        
        # الحصول على معلومات الإيجار النشط
        active_rental = VehicleRental.query.filter_by(
            vehicle_id=vehicle.id, is_active=True
        ).first()
        
        # الحصول على معلومات المشروع النشط
        active_project = VehicleProject.query.filter_by(
            vehicle_id=vehicle.id, is_active=True
        ).first()
        
        vehicle_data.append({
            'رقم اللوحة': vehicle.plate_number,
            'الشركة المصنعة': vehicle.make,
            'الموديل': vehicle.model,
            'السنة': vehicle.year,
            'اللون': vehicle.color,
            'الحالة': status_map.get(vehicle.status, vehicle.status),
            'تكاليف الصيانة الإجمالية': total_maintenance_cost,
            'المؤجر': active_rental.lessor_name if active_rental else '',
            'تكلفة الإيجار الشهرية': active_rental.monthly_cost if active_rental else 0,
            'المشروع': active_project.project_name if active_project else '',
            'الموقع': active_project.location if active_project else '',
            'ملاحظات': vehicle.notes or ''
        })
    
    # إنشاء DataFrame من البيانات
    df = pd.DataFrame(vehicle_data)
    
    # إنشاء ملف Excel في الذاكرة
    output = io.BytesIO()
    
    # استخدام ExcelWriter مع خيارات لتحسين المظهر
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='بيانات السيارات', index=False)
        
        # الحصول على ورقة العمل وworkbook للتنسيق
        workbook = writer.book
        worksheet = writer.sheets['بيانات السيارات']
        
        # تنسيق الخلايا
        header_format = workbook.add_format({
            'bold': True,
            'text_wrap': True,
            'valign': 'top',
            'fg_color': '#D7E4BC',
            'border': 1
        })
        
        # تنسيق عناوين الأعمدة
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_format)
            # ضبط عرض العمود
            worksheet.set_column(col_num, col_num, 15)
    
    # التحضير لإرسال الملف
    output.seek(0)
    
    # اسم الملف بالتاريخ الحالي
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    filename = f"تقرير_السيارات_{today}.xlsx"
    
    # إرسال الملف كمرفق للتنزيل
    return send_file(
        output,
        download_name=filename,
        as_attachment=True,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


# مسار عرض تفاصيل سجل الورشة
@vehicles_bp.route('/workshop-details/<int:workshop_id>')
@login_required
def workshop_details(workshop_id):
    """عرض تفاصيل سجل ورشة في صفحة منفصلة"""
    # الحصول على سجل الورشة
    record = VehicleWorkshop.query.get_or_404(workshop_id)
    vehicle = Vehicle.query.get_or_404(record.vehicle_id)
    
    # تنسيق التواريخ
    record.formatted_entry_date = format_date_arabic(record.entry_date)
    if record.exit_date:
        record.formatted_exit_date = format_date_arabic(record.exit_date)
    
    # استرجاع الصور المرتبطة بسجل الورشة
    images = VehicleWorkshopImage.query.filter_by(workshop_record_id=workshop_id).all()
    record.images = images
    
    # تسجيل الوقت الحالي
    current_date = format_date_arabic(datetime.now().date())
    
    return render_template(
        'vehicles/workshop_details.html',
        vehicle=vehicle,
        record=record,
        current_date=current_date
    )

# مسارات التصدير والمشاركة
@vehicles_bp.route('/<int:id>/export/pdf')
@login_required
def export_vehicle_to_pdf(id):
    """تصدير بيانات السيارة إلى ملف PDF"""
    vehicle = Vehicle.query.get_or_404(id)
    workshop_records = VehicleWorkshop.query.filter_by(vehicle_id=id).order_by(VehicleWorkshop.entry_date.desc()).all()
    rental_records = VehicleRental.query.filter_by(vehicle_id=id).order_by(VehicleRental.start_date.desc()).all()
    
    # إنشاء ملف PDF
    pdf_buffer = export_vehicle_pdf(vehicle, workshop_records, rental_records)
    
    # تسجيل الإجراء
    log_audit('export', 'vehicle', id, f'تم تصدير بيانات السيارة {vehicle.plate_number} إلى PDF')
    
    return send_file(
        pdf_buffer,
        download_name=f'vehicle_{vehicle.plate_number}_{datetime.now().strftime("%Y%m%d")}.pdf',
        as_attachment=True,
        mimetype='application/pdf'
    )


@vehicles_bp.route('/<int:id>/export/workshop/pdf')
@login_required
def export_workshop_to_pdf(id):
    """تصدير سجلات الورشة للسيارة إلى ملف PDF مع الشعار الدائري الجديد"""
    vehicle = Vehicle.query.get_or_404(id)
    workshop_records = VehicleWorkshop.query.filter_by(vehicle_id=id).order_by(VehicleWorkshop.entry_date.desc()).all()
    
    # إنشاء ملف PDF باستخدام الدالة الجديدة مع الشعار الدائري
    pdf_buffer = generate_workshop_report_pdf(vehicle, workshop_records)
    
    # تسجيل الإجراء
    log_audit('export', 'vehicle_workshop', id, f'تم تصدير سجلات ورشة السيارة {vehicle.plate_number} إلى PDF بالتصميم الجديد')
    
    return send_file(
        pdf_buffer,
        download_name=f'workshop_report_{vehicle.plate_number}_{datetime.now().strftime("%Y%m%d")}.pdf',
        as_attachment=True,
        mimetype='application/pdf'
    )


@vehicles_bp.route('/<int:id>/export/excel')
@login_required
def export_vehicle_to_excel(id):
    """تصدير بيانات السيارة إلى ملف Excel"""
    vehicle = Vehicle.query.get_or_404(id)
    workshop_records = VehicleWorkshop.query.filter_by(vehicle_id=id).order_by(VehicleWorkshop.entry_date.desc()).all()
    rental_records = VehicleRental.query.filter_by(vehicle_id=id).order_by(VehicleRental.start_date.desc()).all()
    
    # إنشاء ملف Excel
    excel_buffer = export_vehicle_excel(vehicle, workshop_records, rental_records)
    
    # تسجيل الإجراء
    log_audit('export', 'vehicle', id, f'تم تصدير بيانات السيارة {vehicle.plate_number} إلى Excel')
    
    return send_file(
        excel_buffer,
        download_name=f'vehicle_{vehicle.plate_number}_{datetime.now().strftime("%Y%m%d")}.xlsx',
        as_attachment=True,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


@vehicles_bp.route('/<int:id>/export/workshop/excel')
@login_required
def export_workshop_to_excel(id):
    """تصدير سجلات الورشة للسيارة إلى ملف Excel"""
    vehicle = Vehicle.query.get_or_404(id)
    workshop_records = VehicleWorkshop.query.filter_by(vehicle_id=id).order_by(VehicleWorkshop.entry_date.desc()).all()
    
    # إنشاء ملف Excel
    excel_buffer = export_workshop_records_excel(vehicle, workshop_records)
    
    # تسجيل الإجراء
    log_audit('export', 'vehicle_workshop', id, f'تم تصدير سجلات ورشة السيارة {vehicle.plate_number} إلى Excel')
    
    return send_file(
        excel_buffer,
        download_name=f'vehicle_workshop_{vehicle.plate_number}_{datetime.now().strftime("%Y%m%d")}.xlsx',
        as_attachment=True,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


@vehicles_bp.route('/<int:id>/share/workshop')
@login_required
def share_workshop_options(id):
    """خيارات مشاركة سجلات الورشة للسيارة"""
    vehicle = Vehicle.query.get_or_404(id)
    
    # إنشاء روابط التصدير والمشاركة
    app_url = request.host_url.rstrip('/')
    pdf_url = f"{app_url}{url_for('vehicles.export_workshop_to_pdf', id=id)}"
    excel_url = f"{app_url}{url_for('vehicles.export_workshop_to_excel', id=id)}"
    
    # إنشاء روابط المشاركة
    whatsapp_text = f"سجلات ورشة السيارة: {vehicle.plate_number} - {vehicle.make} {vehicle.model}"
    whatsapp_url = f"https://wa.me/?text={urllib.parse.quote(whatsapp_text)} PDF: {urllib.parse.quote(pdf_url)}"
    
    email_subject = f"سجلات ورشة السيارة: {vehicle.plate_number}"
    email_body = f"مرفق سجلات ورشة السيارة: {vehicle.plate_number} - {vehicle.make} {vehicle.model}\n\nرابط تحميل PDF: {pdf_url}\n\nرابط تحميل Excel: {excel_url}"
    email_url = f"mailto:?subject={urllib.parse.quote(email_subject)}&body={urllib.parse.quote(email_body)}"
    
    return render_template(
        'vehicles/share_workshop.html',
        vehicle=vehicle,
        pdf_url=pdf_url,
        excel_url=excel_url,
        whatsapp_url=whatsapp_url,
        email_url=email_url
    )


@vehicles_bp.route('/<int:id>/print/workshop')
@login_required
def print_workshop_records(id):
    """عرض سجلات الورشة للطباعة"""
    vehicle = Vehicle.query.get_or_404(id)
    workshop_records = VehicleWorkshop.query.filter_by(vehicle_id=id).order_by(VehicleWorkshop.entry_date.desc()).all()
    
    # تنسيق التواريخ
    for record in workshop_records:
        record.formatted_entry_date = format_date_arabic(record.entry_date)
        if record.exit_date:
            record.formatted_exit_date = format_date_arabic(record.exit_date)
    
    # حساب تكلفة الإصلاحات الإجمالية
    total_maintenance_cost = db.session.query(func.sum(VehicleWorkshop.cost)).filter_by(vehicle_id=id).scalar() or 0
    
    # حساب عدد الأيام في الورشة
    days_in_workshop = 0
    for record in workshop_records:
        if record.exit_date:
            days_in_workshop += (record.exit_date - record.entry_date).days
        else:
            days_in_workshop += (datetime.now().date() - record.entry_date).days
    
    return render_template(
        'vehicles/print_workshop.html',
        vehicle=vehicle,
        workshop_records=workshop_records,
        total_maintenance_cost=total_maintenance_cost,
        days_in_workshop=days_in_workshop,
        current_date=format_date_arabic(datetime.now().date())
    )


# إنشاء تقرير شامل للسيارة (PDF) - محتفظ به ولكن قد لا يعمل بشكل صحيح مع النصوص العربية
@vehicles_bp.route('/vehicle-report-pdf/<int:id>')
@login_required
def generate_vehicle_report_pdf(id):
    """إنشاء تقرير شامل للسيارة بصيغة PDF"""
    from flask import send_file, flash, redirect, url_for, make_response
    import io
    
    try:
        # الحصول على بيانات المركبة
        vehicle = Vehicle.query.get_or_404(id)
        
        # الحصول على بيانات الإيجار النشط
        rental = VehicleRental.query.filter_by(vehicle_id=id, is_active=True).first()
        
        # الحصول على سجلات الورشة
        workshop_records = VehicleWorkshop.query.filter_by(vehicle_id=id).order_by(
            VehicleWorkshop.entry_date.desc()
        ).all()
        
        # هذا الموديل قد لا يكون موجودًا، لذلك سنتجاهله الآن
        documents = None
        
        # إنشاء التقرير الشامل
        pdf_bytes = generate_complete_vehicle_report(
            vehicle, 
            rental=rental, 
            workshop_records=workshop_records,
            documents=documents
        )
        
        # إرسال الملف للمستخدم
        buffer = io.BytesIO(pdf_bytes)
        response = make_response(send_file(
            buffer,
            download_name=f'تقرير_شامل_{vehicle.plate_number}.pdf',
            mimetype='application/pdf',
            as_attachment=True
        ))
        
        # تسجيل الإجراء
        log_audit('generate_report', 'vehicle', id, f'تم إنشاء تقرير شامل للسيارة (PDF): {vehicle.plate_number}')
        
        return response
        
    except Exception as e:
        flash(f'حدث خطأ أثناء إنشاء التقرير PDF: {str(e)}', 'danger')
        return redirect(url_for('vehicles.view', id=id))


# مسارات إدارة الفحص الدوري
@vehicles_bp.route('/<int:id>/inspections', methods=['GET'])
@login_required
def vehicle_inspections(id):
    """عرض سجلات الفحص الدوري لسيارة محددة"""
    vehicle = Vehicle.query.get_or_404(id)
    inspections = VehiclePeriodicInspection.query.filter_by(vehicle_id=id).order_by(VehiclePeriodicInspection.inspection_date.desc()).all()
    
    # تنسيق التواريخ
    for inspection in inspections:
        inspection.formatted_inspection_date = format_date_arabic(inspection.inspection_date)
        inspection.formatted_expiry_date = format_date_arabic(inspection.expiry_date)
    
    return render_template(
        'vehicles/inspections.html',
        vehicle=vehicle,
        inspections=inspections,
        inspection_types=INSPECTION_TYPE_CHOICES,
        inspection_statuses=INSPECTION_STATUS_CHOICES
    )

@vehicles_bp.route('/<int:id>/inspections/create', methods=['GET', 'POST'])
@login_required
def create_inspection(id):
    """إضافة سجل فحص دوري جديد"""
    vehicle = Vehicle.query.get_or_404(id)
    
    if request.method == 'POST':
        inspection_date = datetime.strptime(request.form.get('inspection_date'), '%Y-%m-%d').date()
        expiry_date = datetime.strptime(request.form.get('expiry_date'), '%Y-%m-%d').date()
        inspection_number = request.form.get('inspection_number')
        inspector_name = request.form.get('inspector_name')
        inspection_type = request.form.get('inspection_type')
        inspection_status = 'valid'  # الحالة الافتراضية ساري
        cost = float(request.form.get('cost') or 0)
        results = request.form.get('results')
        recommendations = request.form.get('recommendations')
        notes = request.form.get('notes')
        
        # حفظ شهادة الفحص إذا تم تحميلها
        certificate_file = None
        if 'certificate_file' in request.files and request.files['certificate_file']:
            certificate_file = save_image(request.files['certificate_file'], 'inspections')
        
        # إنشاء سجل فحص جديد
        inspection = VehiclePeriodicInspection(
            vehicle_id=id,
            inspection_date=inspection_date,
            expiry_date=expiry_date,
            inspection_number=inspection_number,
            inspector_name=inspector_name,
            inspection_type=inspection_type,
            inspection_status=inspection_status,
            cost=cost,
            results=results,
            recommendations=recommendations,
            certificate_file=certificate_file,
            notes=notes
        )
        
        db.session.add(inspection)
        db.session.commit()
        
        # تسجيل الإجراء
        log_audit('create', 'vehicle_inspection', inspection.id, f'تم إضافة سجل فحص دوري للسيارة: {vehicle.plate_number}')
        
        flash('تم إضافة سجل الفحص الدوري بنجاح!', 'success')
        return redirect(url_for('vehicles.vehicle_inspections', id=id))
    
    return render_template(
        'vehicles/inspection_create.html',
        vehicle=vehicle,
        inspection_types=INSPECTION_TYPE_CHOICES
    )

@vehicles_bp.route('/inspection/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_inspection(id):
    """تعديل سجل فحص دوري"""
    inspection = VehiclePeriodicInspection.query.get_or_404(id)
    vehicle = Vehicle.query.get_or_404(inspection.vehicle_id)
    
    if request.method == 'POST':
        inspection.inspection_date = datetime.strptime(request.form.get('inspection_date'), '%Y-%m-%d').date()
        inspection.expiry_date = datetime.strptime(request.form.get('expiry_date'), '%Y-%m-%d').date()
        inspection.inspection_number = request.form.get('inspection_number')
        inspection.inspector_name = request.form.get('inspector_name')
        inspection.inspection_type = request.form.get('inspection_type')
        inspection.inspection_status = request.form.get('inspection_status')
        inspection.cost = float(request.form.get('cost') or 0)
        inspection.results = request.form.get('results')
        inspection.recommendations = request.form.get('recommendations')
        inspection.notes = request.form.get('notes')
        inspection.updated_at = datetime.utcnow()
        
        # حفظ شهادة الفحص الجديدة إذا تم تحميلها
        if 'certificate_file' in request.files and request.files['certificate_file']:
            inspection.certificate_file = save_image(request.files['certificate_file'], 'inspections')
        
        db.session.commit()
        
        # تسجيل الإجراء
        log_audit('update', 'vehicle_inspection', inspection.id, f'تم تعديل سجل فحص دوري للسيارة: {vehicle.plate_number}')
        
        flash('تم تعديل سجل الفحص الدوري بنجاح!', 'success')
        return redirect(url_for('vehicles.vehicle_inspections', id=vehicle.id))
    
    return render_template(
        'vehicles/inspection_edit.html',
        inspection=inspection,
        vehicle=vehicle,
        inspection_types=INSPECTION_TYPE_CHOICES,
        inspection_statuses=INSPECTION_STATUS_CHOICES
    )

@vehicles_bp.route('/inspection/<int:id>/delete', methods=['POST'])
@login_required
def delete_inspection(id):
    """حذف سجل فحص دوري"""
    inspection = VehiclePeriodicInspection.query.get_or_404(id)
    vehicle_id = inspection.vehicle_id
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    # تسجيل الإجراء قبل الحذف
    log_audit('delete', 'vehicle_inspection', id, f'تم حذف سجل فحص دوري للسيارة: {vehicle.plate_number}')
    
    db.session.delete(inspection)
    db.session.commit()
    
    flash('تم حذف سجل الفحص الدوري بنجاح!', 'success')
    return redirect(url_for('vehicles.vehicle_inspections', id=vehicle_id))

# مسارات إدارة فحص السلامة
@vehicles_bp.route('/<int:id>/safety-checks', methods=['GET'])
@login_required
def vehicle_safety_checks(id):
    """عرض سجلات فحص السلامة لسيارة محددة"""
    vehicle = Vehicle.query.get_or_404(id)
    checks = VehicleSafetyCheck.query.filter_by(vehicle_id=id).order_by(VehicleSafetyCheck.check_date.desc()).all()
    
    # تنسيق التواريخ
    for check in checks:
        check.formatted_check_date = format_date_arabic(check.check_date)
    
    return render_template(
        'vehicles/safety_checks.html',
        vehicle=vehicle,
        checks=checks,
        check_types=SAFETY_CHECK_TYPE_CHOICES,
        check_statuses=SAFETY_CHECK_STATUS_CHOICES
    )

@vehicles_bp.route('/<int:id>/safety-checks/create', methods=['GET', 'POST'])
@login_required
def create_safety_check(id):
    """إضافة سجل فحص سلامة جديد"""
    vehicle = Vehicle.query.get_or_404(id)
    
    # الحصول على قائمة السائقين والمشرفين
    supervisors = Employee.query.filter(Employee.job_title.contains('مشرف')).all()
    
    if request.method == 'POST':
        check_date = datetime.strptime(request.form.get('check_date'), '%Y-%m-%d').date()
        check_type = request.form.get('check_type')
        
        # معلومات السائق
        driver_id = request.form.get('driver_id')
        driver_name = request.form.get('driver_name')
        # تحويل قيمة فارغة إلى None
        if not driver_id or driver_id == '':
            driver_id = None
        else:
            driver = Employee.query.get(driver_id)
            if driver:
                driver_name = driver.name
        
        # معلومات المشرف
        supervisor_id = request.form.get('supervisor_id')
        supervisor_name = request.form.get('supervisor_name')
        # تحويل قيمة فارغة إلى None
        if not supervisor_id or supervisor_id == '':
            supervisor_id = None
        else:
            supervisor = Employee.query.get(supervisor_id)
            if supervisor:
                supervisor_name = supervisor.name
        
        status = request.form.get('status')
        check_form_link = request.form.get('check_form_link')
        issues_found = bool(request.form.get('issues_found'))
        issues_description = request.form.get('issues_description')
        actions_taken = request.form.get('actions_taken')
        notes = request.form.get('notes')
        
        # إنشاء سجل فحص سلامة جديد
        safety_check = VehicleSafetyCheck(
            vehicle_id=id,
            check_date=check_date,
            check_type=check_type,
            driver_id=driver_id,
            driver_name=driver_name,
            supervisor_id=supervisor_id,
            supervisor_name=supervisor_name,
            status=status,
            check_form_link=check_form_link,
            issues_found=issues_found,
            issues_description=issues_description,
            actions_taken=actions_taken,
            notes=notes
        )
        
        db.session.add(safety_check)
        db.session.commit()
        
        # تسجيل الإجراء
        log_audit('create', 'vehicle_safety_check', safety_check.id, f'تم إضافة سجل فحص سلامة للسيارة: {vehicle.plate_number}')
        
        flash('تم إضافة سجل فحص السلامة بنجاح!', 'success')
        return redirect(url_for('vehicles.vehicle_safety_checks', id=id))
    
    return render_template(
        'vehicles/safety_check_create.html',
        vehicle=vehicle,
        supervisors=supervisors,
        check_types=SAFETY_CHECK_TYPE_CHOICES,
        check_statuses=SAFETY_CHECK_STATUS_CHOICES
    )

@vehicles_bp.route('/safety-check/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_safety_check(id):
    """تعديل سجل فحص سلامة"""
    safety_check = VehicleSafetyCheck.query.get_or_404(id)
    vehicle = Vehicle.query.get_or_404(safety_check.vehicle_id)
    
    # الحصول على قائمة السائقين والمشرفين
    supervisors = Employee.query.filter(Employee.job_title.contains('مشرف')).all()
    
    if request.method == 'POST':
        safety_check.check_date = datetime.strptime(request.form.get('check_date'), '%Y-%m-%d').date()
        safety_check.check_type = request.form.get('check_type')
        
        # معلومات السائق
        driver_id = request.form.get('driver_id')
        safety_check.driver_name = request.form.get('driver_name')
        
        # تحويل قيمة فارغة إلى None
        if not driver_id or driver_id == '':
            safety_check.driver_id = None
        else:
            safety_check.driver_id = driver_id
            driver = Employee.query.get(driver_id)
            if driver:
                safety_check.driver_name = driver.name
        
        # معلومات المشرف
        supervisor_id = request.form.get('supervisor_id')
        safety_check.supervisor_name = request.form.get('supervisor_name')
        
        # تحويل قيمة فارغة إلى None
        if not supervisor_id or supervisor_id == '':
            safety_check.supervisor_id = None
        else:
            safety_check.supervisor_id = supervisor_id
            supervisor = Employee.query.get(supervisor_id)
            if supervisor:
                safety_check.supervisor_name = supervisor.name
        
        safety_check.status = request.form.get('status')
        safety_check.check_form_link = request.form.get('check_form_link')
        safety_check.issues_found = bool(request.form.get('issues_found'))
        safety_check.issues_description = request.form.get('issues_description')
        safety_check.actions_taken = request.form.get('actions_taken')
        safety_check.notes = request.form.get('notes')
        safety_check.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # تسجيل الإجراء
        log_audit('update', 'vehicle_safety_check', safety_check.id, f'تم تعديل سجل فحص سلامة للسيارة: {vehicle.plate_number}')
        
        flash('تم تعديل سجل فحص السلامة بنجاح!', 'success')
        return redirect(url_for('vehicles.vehicle_safety_checks', id=vehicle.id))
    
    return render_template(
        'vehicles/safety_check_edit.html',
        safety_check=safety_check,
        vehicle=vehicle,
        supervisors=supervisors,
        check_types=SAFETY_CHECK_TYPE_CHOICES,
        check_statuses=SAFETY_CHECK_STATUS_CHOICES
    )

@vehicles_bp.route('/safety-check/<int:id>/delete', methods=['POST'])
@login_required
def delete_safety_check(id):
    """حذف سجل فحص سلامة"""
    safety_check = VehicleSafetyCheck.query.get_or_404(id)
    vehicle_id = safety_check.vehicle_id
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    # تسجيل الإجراء قبل الحذف
    log_audit('delete', 'vehicle_safety_check', id, f'تم حذف سجل فحص سلامة للسيارة: {vehicle.plate_number}')
    
    db.session.delete(safety_check)
    db.session.commit()
    
    flash('تم حذف سجل فحص السلامة بنجاح!', 'success')
    return redirect(url_for('vehicles.vehicle_safety_checks', id=vehicle_id))

# إنشاء تقرير Excel شامل للسيارة
@vehicles_bp.route('/vehicle-report/<int:id>')
@login_required
def generate_vehicle_report(id):
    """إنشاء تقرير شامل للسيارة بصيغة Excel"""
    from flask import send_file, flash, redirect, url_for, make_response
    import io
    
    try:
        # الحصول على بيانات المركبة
        vehicle = Vehicle.query.get_or_404(id)
        
        # الحصول على بيانات الإيجار النشط
        rental = VehicleRental.query.filter_by(vehicle_id=id, is_active=True).first()
        
        # الحصول على سجلات الورشة
        workshop_records = VehicleWorkshop.query.filter_by(vehicle_id=id).order_by(
            VehicleWorkshop.entry_date.desc()
        ).all()
        
        # هذا الموديل قد لا يكون موجودًا، لذلك سنتجاهله الآن
        documents = None
        
        # إنشاء التقرير الشامل
        excel_bytes = generate_complete_vehicle_excel_report(
            vehicle, 
            rental=rental, 
            workshop_records=workshop_records,
            documents=documents
        )
        
        # إرسال الملف للمستخدم
        buffer = io.BytesIO(excel_bytes)
        response = make_response(send_file(
            buffer,
            download_name=f'تقرير_شامل_{vehicle.plate_number}.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True
        ))
        
        # تسجيل الإجراء
        log_audit('generate_report', 'vehicle', id, f'تم إنشاء تقرير شامل للسيارة (Excel): {vehicle.plate_number}')
        
        return response
        
    except Exception as e:
        flash(f'حدث خطأ أثناء إنشاء تقرير Excel: {str(e)}', 'danger')
        return redirect(url_for('vehicles.view', id=id))