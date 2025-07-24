from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, jsonify
from flask_login import login_required, current_user
from models import ImportedPhoneNumber, Employee, Department, db, UserRole
from datetime import datetime
import logging
from utils.audit_logger import log_activity

sim_management_bp = Blueprint('sim_management', __name__)

@sim_management_bp.route('/')
@login_required
def index():
    """صفحة عرض جميع بطاقات SIM"""
    try:
        # فلاتر البحث
        department_filter = request.args.get('department_id', '')
        carrier_filter = request.args.get('carrier', '')
        status_filter = request.args.get('status', '')
        search_term = request.args.get('search', '')
        
        # استعلام أساسي
        query = ImportedPhoneNumber.query
        
        # تطبيق فلاتر
        if search_term:
            query = query.filter(ImportedPhoneNumber.phone_number.contains(search_term))
        
        if carrier_filter:
            query = query.filter(ImportedPhoneNumber.carrier == carrier_filter)
            
        if status_filter == 'available':
            query = query.filter(ImportedPhoneNumber.employee_id.is_(None))
        elif status_filter == 'assigned':
            query = query.filter(ImportedPhoneNumber.employee_id.isnot(None))
        
        # ترتيب البيانات
        sim_cards = query.order_by(ImportedPhoneNumber.id.desc()).all()
        
        # الحصول على قائمة الأقسام للفلترة
        departments = Department.query.order_by(Department.name).all()
        
        # إحصائيات
        stats = {
            'total_sims': ImportedPhoneNumber.query.count(),
            'available_sims': ImportedPhoneNumber.query.filter(ImportedPhoneNumber.employee_id.is_(None)).count(),
            'assigned_sims': ImportedPhoneNumber.query.filter(ImportedPhoneNumber.employee_id.isnot(None)).count(),
            'stc_count': ImportedPhoneNumber.query.filter(ImportedPhoneNumber.carrier == 'STC').count(),
            'mobily_count': ImportedPhoneNumber.query.filter(ImportedPhoneNumber.carrier == 'موبايلي').count(),
            'zain_count': ImportedPhoneNumber.query.filter(ImportedPhoneNumber.carrier == 'زين').count(),
        }
        
        return render_template('sim_management/index.html', 
                             sim_cards=sim_cards, 
                             departments=departments,
                             stats=stats,
                             department_filter=department_filter,
                             carrier_filter=carrier_filter,
                             status_filter=status_filter,
                             search_term=search_term)
    
    except Exception as e:
        current_app.logger.error(f"Error in sim_management index: {str(e)}")
        flash('حدث خطأ أثناء تحميل البيانات', 'danger')
        return render_template('sim_management/index.html', 
                             sim_cards=[], 
                             departments=[],
                             stats={},
                             department_filter='',
                             carrier_filter='',
                             status_filter='',
                             search_term='')

@sim_management_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """إضافة رقم جديد"""
    if request.method == 'POST':
        try:
            # الحصول على البيانات من النموذج
            phone_number = request.form.get('phone_number', '').strip()
            carrier = request.form.get('carrier', '').strip()
            plan_type = request.form.get('plan_type', '').strip()
            monthly_cost = request.form.get('monthly_cost')
            description = request.form.get('description', '').strip()
            
            # التحقق من البيانات المطلوبة
            if not phone_number:
                flash('رقم الهاتف مطلوب', 'danger')
                return render_template('sim_management/create.html')
            
            if not carrier:
                flash('شركة الاتصالات مطلوبة', 'danger')
                return render_template('sim_management/create.html')
            
            # التحقق من عدم وجود الرقم مسبقاً
            existing_sim = ImportedPhoneNumber.query.filter_by(phone_number=phone_number).first()
            if existing_sim:
                flash('هذا الرقم موجود بالفعل في النظام', 'danger')
                return render_template('sim_management/create.html')
            
            # تحويل التكلفة الشهرية
            try:
                monthly_cost = float(monthly_cost) if monthly_cost else 0.0
            except ValueError:
                monthly_cost = 0.0
            
            # إنشاء رقم جديد
            new_sim = ImportedPhoneNumber(
                phone_number=phone_number,
                carrier=carrier,
                plan_type=plan_type if plan_type else None,
                monthly_cost=monthly_cost,
                description=description if description else None,
                import_date=datetime.now(),
                status='متاح'
            )
            
            db.session.add(new_sim)
            db.session.commit()
            
            # تسجيل العملية
            log_activity(
                action="create",
                entity_type="SIM",
                entity_id=new_sim.id,
                details=f"إضافة رقم SIM جديد: {phone_number} - الشركة: {carrier}, النوع: {plan_type or 'غير محدد'}, التكلفة: {monthly_cost} ريال"
            )
            
            flash(f'تم إضافة الرقم {phone_number} بنجاح', 'success')
            return redirect(url_for('sim_management.index'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating SIM card: {str(e)}")
            flash('حدث خطأ أثناء إضافة الرقم', 'danger')
            return render_template('sim_management/create.html')
    
    return render_template('sim_management/create.html')

@sim_management_bp.route('/edit/<int:sim_id>', methods=['GET', 'POST'])
@login_required
def edit(sim_id):
    """تعديل بيانات رقم"""
    sim_card = ImportedPhoneNumber.query.get_or_404(sim_id)
    
    if request.method == 'POST':
        try:
            # الحصول على البيانات من النموذج
            phone_number = request.form.get('phone_number', '').strip()
            carrier = request.form.get('carrier', '').strip()
            plan_type = request.form.get('plan_type', '').strip()
            monthly_cost = request.form.get('monthly_cost')
            description = request.form.get('description', '').strip()
            
            # التحقق من البيانات المطلوبة
            if not phone_number:
                flash('رقم الهاتف مطلوب', 'danger')
                return render_template('sim_management/edit.html', sim_card=sim_card)
            
            if not carrier:
                flash('شركة الاتصالات مطلوبة', 'danger')
                return render_template('sim_management/edit.html', sim_card=sim_card)
            
            # التحقق من عدم تكرار الرقم (باستثناء الرقم الحالي)
            existing_sim = ImportedPhoneNumber.query.filter(
                ImportedPhoneNumber.phone_number == phone_number,
                ImportedPhoneNumber.id != sim_id
            ).first()
            if existing_sim:
                flash('هذا الرقم موجود بالفعل في النظام', 'danger')
                return render_template('sim_management/edit.html', sim_card=sim_card)
            
            # تحويل التكلفة الشهرية
            try:
                monthly_cost = float(monthly_cost) if monthly_cost else 0.0
            except ValueError:
                monthly_cost = 0.0
            
            # حفظ البيانات القديمة للمقارنة
            old_data = {
                'phone_number': sim_card.phone_number,
                'carrier': sim_card.carrier,
                'plan_type': sim_card.plan_type,
                'monthly_cost': sim_card.monthly_cost
            }
            
            # تحديث البيانات
            sim_card.phone_number = phone_number
            sim_card.carrier = carrier
            sim_card.plan_type = plan_type if plan_type else None
            sim_card.monthly_cost = monthly_cost
            sim_card.description = description if description else None
            sim_card.updated_at = datetime.now()
            
            db.session.commit()
            
            # تسجيل العملية
            changes = []
            for key, old_value in old_data.items():
                new_value = getattr(sim_card, key)
                if old_value != new_value:
                    changes.append(f"{key}: {old_value} → {new_value}")
            
            if changes:
                log_activity(
                    action="update",
                    entity_type="SIM",
                    entity_id=sim_id,
                    details=f"تعديل رقم SIM: {phone_number} - التغييرات: {', '.join(changes)}"
                )
            
            flash(f'تم تحديث بيانات الرقم {phone_number} بنجاح', 'success')
            return redirect(url_for('sim_management.index'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating SIM card: {str(e)}")
            flash('حدث خطأ أثناء تحديث الرقم', 'danger')
            return render_template('sim_management/edit.html', sim_card=sim_card)
    
    return render_template('sim_management/edit.html', sim_card=sim_card)

@sim_management_bp.route('/delete/<int:sim_id>', methods=['POST'])
@login_required
def delete(sim_id):
    """حذف رقم"""
    try:
        sim_card = ImportedPhoneNumber.query.get_or_404(sim_id)
        
        # التحقق من عدم ربط الرقم بموظف
        if sim_card.employee_id:
            flash('لا يمكن حذف الرقم لأنه مربوط بموظف. يرجى فك الربط أولاً', 'danger')
            return redirect(url_for('sim_management.index'))
        
        # حفظ معلومات الرقم قبل الحذف
        phone_number = sim_card.phone_number
        carrier = sim_card.carrier
        
        db.session.delete(sim_card)
        db.session.commit()
        
        # تسجيل العملية
        log_activity(
            action="delete",
            entity_type="SIM",
            entity_id=sim_id,
            details=f"حذف رقم SIM: {phone_number} - الشركة: {carrier}"
        )
        
        flash(f'تم حذف الرقم {phone_number} بنجاح', 'success')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting SIM card: {str(e)}")
        flash('حدث خطأ أثناء حذف الرقم', 'danger')
    
    return redirect(url_for('sim_management.index'))

@sim_management_bp.route('/assign/<int:sim_id>', methods=['POST'])
@login_required
def assign_to_employee(sim_id):
    """ربط رقم بموظف"""
    try:
        sim_card = ImportedPhoneNumber.query.get_or_404(sim_id)
        employee_id = request.form.get('employee_id')
        
        if not employee_id:
            flash('يرجى اختيار موظف', 'danger')
            return redirect(url_for('sim_management.index'))
        
        employee = Employee.query.get_or_404(employee_id)
        
        # التحقق من عدم ربط الرقم بموظف آخر
        if sim_card.employee_id:
            flash('هذا الرقم مربوط بموظف آخر بالفعل', 'danger')
            return redirect(url_for('sim_management.index'))
        
        # ربط الرقم بالموظف
        sim_card.employee_id = employee_id
        sim_card.assignment_date = datetime.now()
        sim_card.status = 'مربوط'
        
        db.session.commit()
        
        # تسجيل العملية
        log_activity(
            action="update",
            entity_type="SIM",
            entity_id=sim_id,
            details=f"ربط رقم SIM بموظف - الرقم: {sim_card.phone_number}, الموظف: {employee.name} ({employee.employee_id})"
        )
        
        flash(f'تم ربط الرقم {sim_card.phone_number} بالموظف {employee.name} بنجاح', 'success')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error assigning SIM card: {str(e)}")
        flash('حدث خطأ أثناء ربط الرقم', 'danger')
    
    return redirect(url_for('sim_management.index'))

@sim_management_bp.route('/unassign/<int:sim_id>', methods=['POST'])
@login_required
def unassign_from_employee(sim_id):
    """فك ربط رقم من موظف"""
    try:
        sim_card = ImportedPhoneNumber.query.get_or_404(sim_id)
        
        if not sim_card.employee_id:
            flash('هذا الرقم غير مربوط بأي موظف', 'danger')
            return redirect(url_for('sim_management.index'))
        
        # الحصول على معلومات الموظف قبل فك الربط
        employee = Employee.query.get(sim_card.employee_id)
        employee_name = employee.name if employee else "غير معروف"
        employee_id_num = employee.employee_id if employee else "غير معروف"
        
        # فك الربط
        sim_card.employee_id = None
        sim_card.assignment_date = None
        sim_card.status = 'متاح'
        
        db.session.commit()
        
        # تسجيل العملية
        log_activity(
            action="update",
            entity_type="SIM",
            entity_id=sim_id,
            details=f"فك ربط رقم SIM من موظف - الرقم: {sim_card.phone_number}, الموظف السابق: {employee_name} ({employee_id_num})"
        )
        
        flash(f'تم فك ربط الرقم {sim_card.phone_number} من الموظف {employee_name} بنجاح', 'success')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error unassigning SIM card: {str(e)}")
        flash('حدث خطأ أثناء فك ربط الرقم', 'danger')
    
    return redirect(url_for('sim_management.index'))

@sim_management_bp.route('/api/available', methods=['GET'])
@login_required
def api_available_sims():
    """API للحصول على الأرقام المتاحة"""
    try:
        available_sims = ImportedPhoneNumber.query.filter(
            ImportedPhoneNumber.employee_id.is_(None)
        ).order_by(ImportedPhoneNumber.phone_number).all()
        
        sims_data = []
        for sim in available_sims:
            sims_data.append({
                'id': sim.id,
                'phone_number': sim.phone_number,
                'carrier': sim.carrier,
                'plan_type': sim.plan_type,
                'monthly_cost': sim.monthly_cost,
                'status_class': 'success'
            })
        
        return jsonify({
            'success': True,
            'sims': sims_data
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting available SIMs: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'حدث خطأ أثناء جلب البيانات'
        }), 500