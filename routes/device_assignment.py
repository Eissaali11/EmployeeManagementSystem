from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, jsonify
from flask_login import login_required, current_user
from models import MobileDevice, SimCard, Employee, Department, db, UserRole, DeviceAssignment
from datetime import datetime
import logging
from utils.audit_logger import log_activity

device_assignment_bp = Blueprint('device_assignment', __name__)

@device_assignment_bp.route('/departments')
@login_required
def departments_view():
    """صفحة عرض الأجهزة والأرقام حسب الأقسام"""
    try:
        # جلب جميع الأقسام
        departments = Department.query.order_by(Department.name).all()
        
        # إضافة إحصائيات لكل قسم
        for department in departments:
            # عدد الموظفين في القسم
            department.employee_count = len(department.employees)
            
            # حساب عدد الأجهزة والأرقام لموظفي القسم
            device_count = 0
            sim_count = 0
            
            for employee in department.employees:
                # عدد الأجهزة المحمولة
                devices = MobileDevice.query.filter_by(employee_id=employee.id).all()
                device_count += len(devices)
                
                # عدد أرقام SIM
                sims = SimCard.query.filter_by(employee_id=employee.id).all()
                sim_count += len(sims)
                
                # إضافة الأجهزة والأرقام للموظف للعرض
                employee.mobile_devices = devices
                employee.sim_cards = sims
            
            department.device_count = device_count
            department.sim_count = sim_count
            
            # حساب نسب التغطية
            if department.employee_count > 0:
                department.device_coverage = round((device_count / department.employee_count) * 100, 1)
                department.sim_coverage = round((sim_count / department.employee_count) * 100, 1)
            else:
                department.device_coverage = 0
                department.sim_coverage = 0
        
        # إحصائيات عامة
        stats = {
            'total_departments': len(departments),
            'total_devices': MobileDevice.query.count(),
            'total_sims': SimCard.query.count(),
            'total_employees': Employee.query.count(),
        }
        
        return render_template('device_assignment/departments_view.html',
                             departments=departments,
                             stats=stats)
        
    except Exception as e:
        flash(f'حدث خطأ أثناء تحميل البيانات: {str(e)}', 'danger')
        return redirect(url_for('device_assignment.index'))

@device_assignment_bp.route('/')
@login_required
def index():
    """صفحة ربط الأجهزة والأرقام بالموظفين"""
    try:
        # فلاتر البحث
        department_filter = request.args.get('department_id', '')
        device_status = request.args.get('device_status', '')
        sim_status = request.args.get('sim_status', '')
        employee_search = request.args.get('employee_search', '')
        
        # الحصول على البيانات الأساسية
        departments = Department.query.order_by(Department.name).all()
        
        # فلترة الموظفين
        employees_query = Employee.query
        if department_filter:
            employees_query = employees_query.join(Employee.departments).filter(Department.id == department_filter)
        if employee_search:
            employees_query = employees_query.filter(
                Employee.name.contains(employee_search) | 
                Employee.employee_id.contains(employee_search)
            )
        employees = employees_query.order_by(Employee.name).all()
        
        # الأجهزة المتاحة فقط (غير مرتبطة بموظف)
        available_devices_query = MobileDevice.query.filter(MobileDevice.employee_id.is_(None))
        if device_status == 'available':
            available_devices_query = available_devices_query.filter(MobileDevice.employee_id.is_(None))
        elif device_status == 'assigned':
            available_devices_query = MobileDevice.query.filter(MobileDevice.employee_id.isnot(None))
        available_devices = available_devices_query.order_by(MobileDevice.device_brand, MobileDevice.device_model).all()
        
        # الأرقام المتاحة
        available_sims_query = SimCard.query
        if sim_status == 'available':
            available_sims_query = available_sims_query.filter(SimCard.employee_id.is_(None))
        elif sim_status == 'assigned':
            available_sims_query = available_sims_query.filter(SimCard.employee_id.isnot(None))
        available_sims = available_sims_query.order_by(SimCard.phone_number).all()
        
        # عمليات الربط النشطة
        active_assignments = DeviceAssignment.query.filter(
            DeviceAssignment.is_active == True
        ).order_by(DeviceAssignment.assignment_date.desc()).limit(10).all()
        
        # إحصائيات
        stats = {
            'total_devices': MobileDevice.query.count(),
            'available_devices': MobileDevice.query.filter(MobileDevice.employee_id.is_(None)).count(),
            'assigned_devices': MobileDevice.query.filter(MobileDevice.employee_id.isnot(None)).count(),
            'total_sims': SimCard.query.count(),
            'available_sims': SimCard.query.filter(SimCard.employee_id.is_(None)).count(),
            'assigned_sims': SimCard.query.filter(SimCard.employee_id.isnot(None)).count(),
        }
        
        return render_template('device_assignment/index.html',
                             departments=departments,
                             employees=employees,
                             available_devices=available_devices,
                             available_sims=available_sims,
                             active_assignments=active_assignments,
                             stats=stats,
                             department_filter=department_filter,
                             device_status=device_status,
                             sim_status=sim_status,
                             employee_search=employee_search)
    
    except Exception as e:
        current_app.logger.error(f"Error in device_assignment index: {str(e)}")
        flash('حدث خطأ أثناء تحميل البيانات', 'danger')
        return render_template('device_assignment/index.html',
                             departments=[],
                             employees=[],
                             available_devices=[],
                             available_sims=[],
                             active_assignments=[],
                             stats={},
                             department_filter='',
                             device_status='',
                             sim_status='',
                             employee_search='')

@device_assignment_bp.route('/assign', methods=['POST'])
@login_required
def assign():
    """ربط جهاز و/أو رقم بموظف"""
    try:
        assignment_type = request.form.get('assignment_type')
        employee_id = request.form.get('employee_id')
        device_id = request.form.get('device_id') if request.form.get('device_id') else None
        sim_id = request.form.get('sim_id') if request.form.get('sim_id') else None
        notes = request.form.get('notes', '').strip()
        
        # التحقق من البيانات المطلوبة
        if not assignment_type or not employee_id:
            flash('يرجى اختيار نوع الربط والموظف', 'danger')
            return redirect(url_for('device_assignment.index'))
        
        employee = Employee.query.get_or_404(employee_id)
        
        # التحقق من نوع الربط والمعلومات المطلوبة
        if assignment_type == 'device_only' and not device_id:
            flash('يرجى اختيار جهاز للربط', 'danger')
            return redirect(url_for('device_assignment.index'))
        elif assignment_type == 'sim_only' and not sim_id:
            flash('يرجى اختيار رقم للربط', 'danger')
            return redirect(url_for('device_assignment.index'))
        elif assignment_type == 'device_and_sim' and (not device_id or not sim_id):
            flash('يرجى اختيار جهاز ورقم للربط', 'danger')
            return redirect(url_for('device_assignment.index'))
        
        device = None
        sim_card = None
        
        # التحقق من الجهاز إذا تم تحديده
        if device_id:
            device = MobileDevice.query.get_or_404(device_id)
            if device.is_assigned:
                flash('هذا الجهاز مربوط بموظف آخر بالفعل', 'danger')
                return redirect(url_for('device_assignment.index'))
        
        # التحقق من الرقم إذا تم تحديده
        if sim_id:
            sim_card = ImportedPhoneNumber.query.get_or_404(sim_id)
            if sim_card.employee_id:
                flash('هذا الرقم مربوط بموظف آخر بالفعل', 'danger')
                return redirect(url_for('device_assignment.index'))
        
        # إنشاء سجل الربط
        assignment = DeviceAssignment(
            employee_id=employee_id,
            device_id=device_id,
            sim_card_id=sim_id,
            assignment_date=datetime.now(),
            assignment_type=assignment_type,
            notes=notes,
            assigned_by=current_user.id,
            is_active=True
        )
        
        db.session.add(assignment)
        
        # تحديث حالة الجهاز
        if device:
            device.is_assigned = True
            device.assigned_to = employee_id
            device.assignment_date = datetime.now()
        
        # تحديث حالة الرقم
        if sim_card:
            sim_card.employee_id = employee_id
            sim_card.assignment_date = datetime.now()
            sim_card.status = 'مربوط'
        
        db.session.commit()
        
        # تسجيل العملية
        action_details = []
        if device:
            action_details.append(f"جهاز: {device.phone_number}")
        if sim_card:
            action_details.append(f"رقم: {sim_card.phone_number}")
        
        log_activity(
            action="create",
            entity_type="DeviceAssignment",
            entity_id=assignment.id,
            details=f"ربط {assignment_type} بموظف - الموظف: {employee.name} ({employee.employee_id}), {', '.join(action_details)}"
        )
        
        success_message = f"تم ربط "
        if device and sim_card:
            success_message += f"الجهاز {device.phone_number} والرقم {sim_card.phone_number}"
        elif device:
            success_message += f"الجهاز {device.phone_number}"
        elif sim_card:
            success_message += f"الرقم {sim_card.phone_number}"
        success_message += f" بالموظف {employee.name} بنجاح"
        
        flash(success_message, 'success')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in device assignment: {str(e)}")
        flash('حدث خطأ أثناء عملية الربط', 'danger')
    
    return redirect(url_for('device_assignment.index'))

@device_assignment_bp.route('/unassign/<int:assignment_id>', methods=['POST'])
@login_required
def unassign(assignment_id):
    """فك ربط جهاز و/أو رقم من موظف"""
    try:
        assignment = DeviceAssignment.query.get_or_404(assignment_id)
        reason = request.form.get('reason', 'فك ربط يدوي')
        
        if not assignment.is_active:
            flash('هذا الربط غير نشط بالفعل', 'danger')
            return redirect(url_for('device_assignment.index'))
        
        # الحصول على معلومات العملية قبل فك الربط
        employee = assignment.employee
        device = assignment.device
        sim_card = assignment.sim_card
        
        # فك ربط الجهاز
        if device:
            device.is_assigned = False
            device.assigned_to = None
            device.assignment_date = None
        
        # فك ربط الرقم
        if sim_card:
            sim_card.employee_id = None
            sim_card.assignment_date = None
            sim_card.status = 'متاح'
        
        # تحديث سجل الربط
        assignment.is_active = False
        assignment.unassignment_date = datetime.now()
        assignment.unassignment_reason = reason
        assignment.unassigned_by = current_user.id
        
        db.session.commit()
        
        # تسجيل العملية
        action_details = []
        if device:
            action_details.append(f"جهاز: {device.phone_number}")
        if sim_card:
            action_details.append(f"رقم: {sim_card.phone_number}")
        
        log_activity(
            action="update",
            entity_type="DeviceAssignment",
            entity_id=assignment_id,
            details=f"فك ربط من موظف - الموظف: {employee.name} ({employee.employee_id}), {', '.join(action_details)}, السبب: {reason}"
        )
        
        flash(f'تم فك الربط من الموظف {employee.name} بنجاح', 'success')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in device unassignment: {str(e)}")
        flash('حدث خطأ أثناء فك الربط', 'danger')
    
    return redirect(url_for('device_assignment.index'))

@device_assignment_bp.route('/history')
@login_required
def history():
    """تاريخ عمليات الربط"""
    try:
        # فلاتر البحث
        employee_filter = request.args.get('employee_id', '')
        status_filter = request.args.get('status', '')
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')
        
        # استعلام أساسي
        query = DeviceAssignment.query
        
        # تطبيق فلاتر
        if employee_filter:
            query = query.filter(DeviceAssignment.employee_id == employee_filter)
        
        if status_filter == 'active':
            query = query.filter(DeviceAssignment.is_active == True)
        elif status_filter == 'inactive':
            query = query.filter(DeviceAssignment.is_active == False)
        
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
                query = query.filter(DeviceAssignment.assignment_date >= date_from_obj)
            except ValueError:
                pass
        
        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
                query = query.filter(DeviceAssignment.assignment_date <= date_to_obj)
            except ValueError:
                pass
        
        # ترتيب البيانات
        assignments = query.order_by(DeviceAssignment.assignment_date.desc()).all()
        
        # قائمة الموظفين للفلترة
        employees_with_assignments = Employee.query.join(DeviceAssignment).distinct().order_by(Employee.name).all()
        
        # إحصائيات
        stats = {
            'total_assignments': DeviceAssignment.query.count(),
            'active_assignments': DeviceAssignment.query.filter(DeviceAssignment.is_active == True).count(),
            'completed_assignments': DeviceAssignment.query.filter(DeviceAssignment.is_active == False).count(),
        }
        
        return render_template('device_assignment/history.html',
                             assignments=assignments,
                             employees=employees_with_assignments,
                             stats=stats,
                             employee_filter=employee_filter,
                             status_filter=status_filter,
                             date_from=date_from,
                             date_to=date_to)
    
    except Exception as e:
        current_app.logger.error(f"Error in assignment history: {str(e)}")
        flash('حدث خطأ أثناء تحميل التاريخ', 'danger')
        return render_template('device_assignment/history.html',
                             assignments=[],
                             employees=[],
                             stats={},
                             employee_filter='',
                             status_filter='',
                             date_from='',
                             date_to='')

@device_assignment_bp.route('/api/employee/<int:employee_id>')
@login_required
def api_employee_assignments(employee_id):
    """API للحصول على ربطات الموظف"""
    try:
        employee = Employee.query.get_or_404(employee_id)
        
        # الربطات النشطة
        active_assignments = DeviceAssignment.query.filter(
            DeviceAssignment.employee_id == employee_id,
            DeviceAssignment.is_active == True
        ).all()
        
        # الأجهزة المربوطة
        devices = []
        for assignment in active_assignments:
            if assignment.device:
                devices.append({
                    'id': assignment.device.id,
                    'phone_number': assignment.device.phone_number,
                    'imei': assignment.device.imei,
                    'brand': assignment.device.device_brand,
                    'model': assignment.device.device_model,
                    'assignment_date': assignment.assignment_date.strftime('%Y-%m-%d') if assignment.assignment_date else None
                })
        
        # الأرقام المربوطة
        sim_cards = []
        for assignment in active_assignments:
            if assignment.sim_card:
                sim_cards.append({
                    'id': assignment.sim_card.id,
                    'phone_number': assignment.sim_card.phone_number,
                    'carrier': assignment.sim_card.carrier,
                    'plan_type': assignment.sim_card.plan_type,
                    'assignment_date': assignment.assignment_date.strftime('%Y-%m-%d') if assignment.assignment_date else None
                })
        
        return jsonify({
            'success': True,
            'employee': {
                'id': employee.id,
                'name': employee.name,
                'employee_id': employee.employee_id,
                'mobile': employee.mobile
            },
            'devices': devices,
            'sim_cards': sim_cards
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting employee assignments: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'حدث خطأ أثناء جلب البيانات'
        }), 500

@device_assignment_bp.route('/department-management')
@login_required
def department_management():
    """صفحة إدارة ربط الأجهزة والأرقام بالأقسام مباشرة"""
    try:
        departments = Department.query.all()
        
        # جلب الأجهزة المتاحة (غير مربوطة بموظف أو قسم)
        available_devices = MobileDevice.query.filter(
            MobileDevice.employee_id.is_(None),
            MobileDevice.department_id.is_(None)
        ).all()
        
        # جلب الأرقام المتاحة (غير مربوطة بموظف)
        available_sims = ImportedPhoneNumber.query.filter_by(employee_id=None).all()
        
        return render_template('device_assignment/department_management.html',
                             departments=departments,
                             available_devices=available_devices,
                             available_sims=available_sims)
    
    except Exception as e:
        current_app.logger.error(f"Error in department management: {str(e)}")
        flash('حدث خطأ في تحميل البيانات', 'danger')
        return redirect(url_for('device_assignment.index'))

@device_assignment_bp.route('/assign-to-department', methods=['POST'])
@login_required
def assign_to_department():
    """ربط جهاز و/أو رقم بقسم مباشرة"""
    try:
        assignment_type = request.form.get('assignment_type')
        department_id = request.form.get('department_id')
        device_id = request.form.get('device_id') if request.form.get('device_id') else None
        sim_id = request.form.get('sim_id') if request.form.get('sim_id') else None
        notes = request.form.get('notes', '').strip()
        
        # التحقق من البيانات المطلوبة
        if not assignment_type or not department_id:
            flash('يرجى اختيار نوع الربط والقسم', 'danger')
            return redirect(url_for('device_assignment.department_management'))
        
        department = Department.query.get_or_404(department_id)
        
        # التحقق من نوع الربط والمعلومات المطلوبة
        if assignment_type == 'device_only' and not device_id:
            flash('يرجى اختيار جهاز للربط', 'danger')
            return redirect(url_for('device_assignment.department_management'))
        elif assignment_type == 'sim_only' and not sim_id:
            flash('يرجى اختيار رقم للربط', 'danger')
            return redirect(url_for('device_assignment.department_management'))
        elif assignment_type == 'device_and_sim' and (not device_id or not sim_id):
            flash('يرجى اختيار جهاز ورقم للربط', 'danger')
            return redirect(url_for('device_assignment.department_management'))
        
        # ربط الجهاز بالقسم
        if device_id:
            device = MobileDevice.query.get_or_404(device_id)
            if device.employee_id or device.department_id:
                flash('هذا الجهاز مربوط بالفعل', 'danger')
                return redirect(url_for('device_assignment.department_management'))
            
            device.department_id = department_id
            device.department_assignment_date = datetime.now()
            device.assignment_type = 'department'
            device.status = 'مرتبط'
            if notes:
                device.notes = notes
        
        # ربط الرقم (نحتاج لإنشاء DeviceAssignment)
        if sim_id:
            sim_card = ImportedPhoneNumber.query.get_or_404(sim_id)
            if sim_card.employee_id:
                flash('هذا الرقم مربوط بموظف آخر بالفعل', 'danger')
                return redirect(url_for('device_assignment.department_management'))
            
            # إنشاء سجل ربط للقسم
            assignment = DeviceAssignment(
                department_id=department_id,
                device_id=device_id,
                sim_card_id=sim_id,
                assignment_date=datetime.now(),
                assignment_type=assignment_type,
                notes=notes,
                assigned_by=current_user.id,
                is_active=True
            )
            db.session.add(assignment)
            
            sim_card.status = 'مربوط'
        
        db.session.commit()
        
        # رسالة النجاح
        success_message = f"تم ربط "
        if device_id and sim_id:
            success_message += f"الجهاز والرقم"
        elif device_id:
            success_message += f"الجهاز"
        elif sim_id:
            success_message += f"الرقم"
        success_message += f" بقسم {department.name} بنجاح"
        
        flash(success_message, 'success')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in department assignment: {str(e)}")
        flash('حدث خطأ أثناء عملية الربط', 'danger')
    
    return redirect(url_for('device_assignment.department_management'))

@device_assignment_bp.route('/unassign-from-department/<int:device_id>', methods=['POST'])
@login_required
def unassign_from_department(device_id):
    """فك ربط جهاز من قسم"""
    try:
        device = MobileDevice.query.get_or_404(device_id)
        
        if not device.department_id:
            flash('هذا الجهاز غير مربوط بأي قسم', 'danger')
            return redirect(url_for('device_assignment.department_management'))
        
        department_name = device.department.name if device.department else "غير محدد"
        
        # فك الربط
        device.department_id = None
        device.department_assignment_date = None
        device.assignment_type = 'employee'
        device.status = 'متاح'
        
        # فك ربط أي سجلات DeviceAssignment مرتبطة
        assignments = DeviceAssignment.query.filter_by(device_id=device_id, is_active=True).all()
        for assignment in assignments:
            if assignment.department_id:
                assignment.is_active = False
                if assignment.sim_card:
                    assignment.sim_card.status = 'متاح'
        
        db.session.commit()
        
        flash(f'تم فك ربط الجهاز من قسم {department_name} بنجاح', 'success')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in department unassignment: {str(e)}")
        flash('حدث خطأ أثناء فك الربط', 'danger')
    
    return redirect(url_for('device_assignment.department_management'))