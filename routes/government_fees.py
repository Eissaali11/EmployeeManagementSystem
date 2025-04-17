from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import func, extract
from app import db
from models import RenewalFee as GovernmentFee, Document, Employee, Department, SystemAudit

government_fees_bp = Blueprint('government_fees', __name__, url_prefix='/government-fees')

@government_fees_bp.route('/')
def index():
    """عرض قائمة الرسوم الحكومية للموظفين مع خيارات التصفية"""
    # خيارات الفلترة
    fee_type = request.args.get('fee_type')
    payment_status = request.args.get('payment_status')
    department_id = request.args.get('department_id')
    month = request.args.get('month')
    year = request.args.get('year')
    
    # بناء الاستعلام
    query = GovernmentFee.query.join(Document).join(Employee)
    
    # تطبيق الفلاتر
    if fee_type:
        query = query.filter(GovernmentFee.fee_type == fee_type)
    
    if payment_status:
        query = query.filter(GovernmentFee.payment_status == payment_status)
    
    if department_id and department_id.isdigit():
        query = query.filter(Employee.department_id == int(department_id))
    
    if month and month.isdigit():
        query = query.filter(extract('month', GovernmentFee.fee_date) == int(month))
    
    if year and year.isdigit():
        query = query.filter(extract('year', GovernmentFee.fee_date) == int(year))
    
    # تنفيذ الاستعلام
    fees = query.order_by(GovernmentFee.fee_date.desc()).all()
    
    # الحصول على قائمة الأقسام للفلترة
    departments = Department.query.all()
    
    # إحصائيات
    total_fees = query.with_entities(func.sum(GovernmentFee.amount)).scalar() or 0
    pending_fees = query.filter(GovernmentFee.payment_status == 'pending').with_entities(func.sum(GovernmentFee.amount)).scalar() or 0
    paid_fees = query.filter(GovernmentFee.payment_status == 'paid').with_entities(func.sum(GovernmentFee.amount)).scalar() or 0
    
    fee_types = {
        'passport': 'الجوازات',
        'labor_office': 'مكتب العمل',
        'insurance': 'التأمين',
        'social_insurance': 'التأمينات الاجتماعية',
        'transfer_sponsorship': 'نقل كفالة',
        'other': 'رسوم أخرى'
    }
    
    payment_statuses = {
        'pending': 'قيد الانتظار',
        'paid': 'مدفوع',
        'overdue': 'متأخر'
    }
    
    # بيانات للرسم البياني
    fee_type_stats = db.session.query(
        GovernmentFee.fee_type,
        func.sum(GovernmentFee.amount).label('total_amount')
    ).group_by(GovernmentFee.fee_type).all()
    
    fee_type_data = {fee_type: 0 for fee_type in fee_types.keys()}
    for fee_type, amount in fee_type_stats:
        fee_type_data[fee_type] = amount
    
    return render_template('government_fees/index.html',
                          fees=fees,
                          departments=departments,
                          fee_types=fee_types,
                          payment_statuses=payment_statuses,
                          fee_type=fee_type,
                          payment_status=payment_status,
                          department_id=department_id,
                          month=month,
                          year=year,
                          total_fees=total_fees,
                          pending_fees=pending_fees,
                          paid_fees=paid_fees,
                          fee_type_data=fee_type_data)

@government_fees_bp.route('/create', methods=['GET', 'POST'])
def create():
    """إنشاء رسم حكومي جديد"""
    if request.method == 'POST':
        try:
            # استلام البيانات من النموذج
            document_id = request.form.get('document_id')
            fee_date = request.form.get('fee_date')
            fee_type = request.form.get('fee_type')
            amount = request.form.get('amount')
            payment_status = request.form.get('payment_status', 'pending')
            payment_date = request.form.get('payment_date')
            receipt_number = request.form.get('receipt_number')
            transfer_number = request.form.get('transfer_number')
            notes = request.form.get('notes')
            
            # التحقق من البيانات
            if not all([document_id, fee_date, fee_type, amount]):
                flash('جميع الحقول المميزة بـ * مطلوبة', 'danger')
                return redirect(url_for('government_fees.create'))
            
            # تحويل التاريخ
            try:
                fee_date = datetime.strptime(fee_date, '%Y-%m-%d').date()
                if payment_date:
                    payment_date = datetime.strptime(payment_date, '%Y-%m-%d').date()
                else:
                    payment_date = None
            except ValueError:
                flash('تنسيق التاريخ غير صحيح', 'danger')
                return redirect(url_for('government_fees.create'))
            
            # التحقق من وجود الوثيقة
            document = Document.query.get(document_id)
            if not document:
                flash('الوثيقة غير موجودة', 'danger')
                return redirect(url_for('government_fees.create'))
            
            # إنشاء سجل جديد
            government_fee = GovernmentFee(
                document_id=document_id,
                fee_date=fee_date,
                fee_type=fee_type,
                amount=float(amount),
                payment_status=payment_status,
                payment_date=payment_date,
                receipt_number=receipt_number,
                transfer_number=transfer_number if fee_type == 'transfer_sponsorship' else None,
                notes=notes
            )
            
            db.session.add(government_fee)
            
            # إضافة سجل تدقيق
            audit = SystemAudit(
                action='create',
                entity_type='government_fee',
                entity_id=0,
                details=f'تم إنشاء رسم حكومي جديد للوثيقة رقم {document_id}'
            )
            db.session.add(audit)
            
            db.session.commit()
            
            # تحديث معرف السجل في سجل التدقيق
            audit.entity_id = government_fee.id
            db.session.commit()
            
            flash('تم إنشاء الرسم الحكومي بنجاح', 'success')
            return redirect(url_for('government_fees.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ: {str(e)}', 'danger')
    
    # الحصول على قائمة الوثائق المتاحة
    documents = Document.query.join(Employee).all()
    
    fee_types = {
        'passport': 'الجوازات',
        'labor_office': 'مكتب العمل',
        'insurance': 'التأمين',
        'social_insurance': 'التأمينات الاجتماعية',
        'transfer_sponsorship': 'نقل كفالة',
        'other': 'رسوم أخرى'
    }
    
    payment_statuses = {
        'pending': 'قيد الانتظار',
        'paid': 'مدفوع',
        'overdue': 'متأخر'
    }
    
    return render_template('government_fees/create.html',
                          documents=documents,
                          fee_types=fee_types,
                          payment_statuses=payment_statuses)

@government_fees_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    """تعديل رسم حكومي موجود"""
    government_fee = GovernmentFee.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # استلام البيانات من النموذج
            fee_date = request.form.get('fee_date')
            fee_type = request.form.get('fee_type')
            amount = request.form.get('amount')
            payment_status = request.form.get('payment_status')
            payment_date = request.form.get('payment_date')
            receipt_number = request.form.get('receipt_number')
            transfer_number = request.form.get('transfer_number')
            notes = request.form.get('notes')
            
            # التحقق من البيانات
            if not all([fee_date, fee_type, amount]):
                flash('جميع الحقول المميزة بـ * مطلوبة', 'danger')
                return redirect(url_for('government_fees.edit', id=id))
            
            # تحويل التاريخ
            try:
                fee_date = datetime.strptime(fee_date, '%Y-%m-%d').date()
                if payment_date:
                    payment_date = datetime.strptime(payment_date, '%Y-%m-%d').date()
                else:
                    payment_date = None
            except ValueError:
                flash('تنسيق التاريخ غير صحيح', 'danger')
                return redirect(url_for('government_fees.edit', id=id))
            
            # تحديث السجل
            government_fee.fee_date = fee_date
            government_fee.fee_type = fee_type
            government_fee.amount = float(amount)
            government_fee.payment_status = payment_status
            government_fee.payment_date = payment_date
            government_fee.receipt_number = receipt_number
            government_fee.transfer_number = transfer_number if fee_type == 'transfer_sponsorship' else None
            government_fee.notes = notes
            government_fee.updated_at = datetime.utcnow()
            
            # إضافة سجل تدقيق
            audit = SystemAudit(
                action='update',
                entity_type='government_fee',
                entity_id=id,
                details=f'تم تحديث الرسم الحكومي رقم {id}'
            )
            db.session.add(audit)
            
            db.session.commit()
            
            flash('تم تحديث الرسم الحكومي بنجاح', 'success')
            return redirect(url_for('government_fees.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ: {str(e)}', 'danger')
    
    # تهيئة البيانات للنموذج
    fee_date = government_fee.fee_date.strftime('%Y-%m-%d')
    if government_fee.payment_date:
        payment_date = government_fee.payment_date.strftime('%Y-%m-%d')
    else:
        payment_date = ''
    
    fee_types = {
        'passport': 'الجوازات',
        'labor_office': 'مكتب العمل',
        'insurance': 'التأمين',
        'social_insurance': 'التأمينات الاجتماعية',
        'transfer_sponsorship': 'نقل كفالة',
        'other': 'رسوم أخرى'
    }
    
    payment_statuses = {
        'pending': 'قيد الانتظار',
        'paid': 'مدفوع',
        'overdue': 'متأخر'
    }
    
    return render_template('government_fees/edit.html',
                          government_fee=government_fee,
                          fee_date=fee_date,
                          payment_date=payment_date,
                          fee_types=fee_types,
                          payment_statuses=payment_statuses)

@government_fees_bp.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    """حذف رسم حكومي"""
    try:
        government_fee = GovernmentFee.query.get_or_404(id)
        
        document_id = government_fee.document_id
        
        # إضافة سجل تدقيق
        audit = SystemAudit(
            action='delete',
            entity_type='government_fee',
            entity_id=id,
            details=f'تم حذف الرسم الحكومي للوثيقة رقم {document_id}'
        )
        db.session.add(audit)
        
        # حذف الرسم
        db.session.delete(government_fee)
        db.session.commit()
        
        flash('تم حذف الرسم الحكومي بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ: {str(e)}', 'danger')
    
    return redirect(url_for('government_fees.index'))

@government_fees_bp.route('/stats/monthly', methods=['GET'])
def monthly_stats():
    """إحصائيات شهرية للرسوم الحكومية"""
    year = request.args.get('year', datetime.now().year)
    try:
        year = int(year)
    except ValueError:
        year = datetime.now().year
    
    monthly_data = db.session.query(
        extract('month', GovernmentFee.fee_date).label('month'),
        func.sum(GovernmentFee.amount).label('total_amount')
    ).filter(extract('year', GovernmentFee.fee_date) == year)\
     .group_by('month')\
     .order_by('month')\
     .all()
    
    months = [0] * 12
    for month, amount in monthly_data:
        months[int(month)-1] = amount
    
    return jsonify({
        'months': ["يناير", "فبراير", "مارس", "إبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"],
        'data': months,
        'year': year
    })