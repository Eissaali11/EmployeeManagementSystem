from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy import extract, func, or_
import os
import uuid
import io
from fpdf import FPDF

from app import db
from models import Vehicle, VehicleRental, VehicleWorkshop, VehicleWorkshopImage, VehicleProject, VehicleHandover, VehicleHandoverImage, SystemAudit

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
    
    if rental:
        rental.formatted_start_date = format_date_arabic(rental.start_date)
        if rental.end_date:
            rental.formatted_end_date = format_date_arabic(rental.end_date)
    
    return render_template(
        'vehicles/view.html',
        vehicle=vehicle,
        rental=rental,
        workshop_records=workshop_records,
        project_assignments=project_assignments,
        handover_records=handover_records,
        total_maintenance_cost=total_maintenance_cost,
        days_in_workshop=days_in_workshop
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
    from utils.pdf_generator_new import generate_vehicle_handover_pdf
    
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