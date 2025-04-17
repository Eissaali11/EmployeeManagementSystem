from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from sqlalchemy import func, extract
from app import db
from models import GovernmentFee, Document, Employee, Department, SystemAudit
from utils.government_fees_export import export_government_fees_data, generate_monthly_report, generate_employee_report

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

@government_fees_bp.route('/dashboard')
def dashboard():
    """لوحة تحكم الرسوم الحكومية"""
    # الحصول على الإحصائيات العامة
    total_fees = db.session.query(func.sum(GovernmentFee.amount)).scalar() or 0
    pending_fees = db.session.query(func.sum(GovernmentFee.amount)).\
        filter(GovernmentFee.payment_status == 'pending').scalar() or 0
    
    # إحصائيات الموظفين
    total_employees = Employee.query.filter_by(status='active').count()
    saudi_employees = Employee.query.filter_by(contract_type='saudi').count()
    foreign_employees = total_employees - saudi_employees
    
    # الوثائق المنتهية قريبًا
    thirty_days_from_now = datetime.now().date() + timedelta(days=30)
    due_renewals = Document.query.filter(
        Document.expiry_date <= thirty_days_from_now,
        Document.expiry_date >= datetime.now().date()
    ).count()
    
    # إجمالي الرسوم حسب النوع
    fee_types_data = db.session.query(
        GovernmentFee.fee_type,
        func.sum(GovernmentFee.amount).label('total')
    ).group_by(GovernmentFee.fee_type).all()
    
    fee_types = {
        'passport': 'الجوازات',
        'labor_office': 'مكتب العمل',
        'insurance': 'التأمين الطبي',
        'social_insurance': 'التأمينات الاجتماعية',
        'transfer_sponsorship': 'نقل كفالة',
        'other': 'رسوم أخرى'
    }
    
    # الوثائق التي تنتهي قريبًا
    expiring_documents = Document.query.filter(
        Document.expiry_date <= thirty_days_from_now,
        Document.expiry_date >= datetime.now().date()
    ).join(Employee).order_by(Document.expiry_date).limit(5).all()
    
    # ملخص الرسوم السنوية
    current_year = datetime.now().year
    yearly_summary = {}
    
    for fee_type, label in fee_types.items():
        monthly_amount = db.session.query(func.sum(GovernmentFee.amount)).\
            filter(GovernmentFee.fee_type == fee_type).\
            filter(extract('year', GovernmentFee.fee_date) == current_year).\
            scalar() or 0
        
        yearly_amount = monthly_amount * 12 if fee_type in ['labor_office', 'social_insurance'] else monthly_amount
        
        yearly_summary[fee_type] = {
            'monthly': monthly_amount,
            'yearly': yearly_amount,
            'label': label
        }
    
    total_monthly = sum(item['monthly'] for item in yearly_summary.values())
    total_yearly = sum(item['yearly'] for item in yearly_summary.values())
    
    return render_template('government_fees/dashboard.html',
                          total_fees=total_fees,
                          pending_fees=pending_fees,
                          total_employees=total_employees,
                          saudi_employees=saudi_employees,
                          foreign_employees=foreign_employees,
                          due_renewals=due_renewals,
                          expiring_documents=expiring_documents,
                          fee_types=fee_types,
                          fee_types_data=fee_types_data,
                          yearly_summary=yearly_summary,
                          total_monthly=total_monthly,
                          total_yearly=total_yearly)

@government_fees_bp.route('/reports')
def reports():
    """تقارير الرسوم الحكومية"""
    return render_template('government_fees/reports.html')

@government_fees_bp.route('/reports/monthly')
def monthly_report():
    """تصدير تقرير شهري للرسوم الحكومية"""
    year = request.args.get('year', datetime.now().year)
    month = request.args.get('month', datetime.now().month)
    
    try:
        year = int(year)
        month = int(month)
    except ValueError:
        year = datetime.now().year
        month = datetime.now().month
    
    output, filename = generate_monthly_report(year, month)
    
    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@government_fees_bp.route('/reports/yearly')
def yearly_report():
    """تصدير تقرير سنوي للرسوم الحكومية"""
    year = request.args.get('year', datetime.now().year)
    fee_type = request.args.get('fee_type')
    
    try:
        year = int(year)
    except ValueError:
        year = datetime.now().year
    
    output, filename = export_government_fees_data(fee_type=fee_type, year=year)
    
    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@government_fees_bp.route('/reports/employee/<int:employee_id>')
def employee_report(employee_id):
    """تصدير تقرير الرسوم الحكومية لموظف محدد"""
    output, filename = generate_employee_report(employee_id)
    
    if output:
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    else:
        flash('لم يتم العثور على الموظف المحدد', 'danger')
        return redirect(url_for('government_fees.reports'))

@government_fees_bp.route('/reports/preview')
def preview_report():
    """معاينة التقرير المخصص"""
    # استلام معايير التصفية
    fee_type = request.args.get('fee_type')
    payment_status = request.args.get('payment_status')
    department_id = request.args.get('department_id')
    date_range = request.args.get('date_range')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    # بناء الاستعلام
    query = GovernmentFee.query.join(Employee)
    
    # تطبيق المعايير
    if fee_type:
        query = query.filter(GovernmentFee.fee_type == fee_type)
    
    if payment_status:
        query = query.filter(GovernmentFee.payment_status == payment_status)
    
    if department_id and department_id.isdigit():
        query = query.filter(Employee.department_id == int(department_id))
    
    # معالجة الفترة الزمنية
    today = datetime.now().date()
    if date_range == 'current_month':
        start_date = datetime(today.year, today.month, 1).date()
        end_date = today
        query = query.filter(GovernmentFee.fee_date >= start_date, GovernmentFee.fee_date <= end_date)
    elif date_range == 'current_year':
        start_date = datetime(today.year, 1, 1).date()
        end_date = today
        query = query.filter(GovernmentFee.fee_date >= start_date, GovernmentFee.fee_date <= end_date)
    elif date_range == 'last_three_months':
        start_date = (today - timedelta(days=90))
        end_date = today
        query = query.filter(GovernmentFee.fee_date >= start_date, GovernmentFee.fee_date <= end_date)
    elif date_range == 'last_six_months':
        start_date = (today - timedelta(days=180))
        end_date = today
        query = query.filter(GovernmentFee.fee_date >= start_date, GovernmentFee.fee_date <= end_date)
    elif date_range == 'custom' and date_from and date_to:
        try:
            start_date = datetime.strptime(date_from, '%Y-%m-%d').date()
            end_date = datetime.strptime(date_to, '%Y-%m-%d').date()
            query = query.filter(GovernmentFee.fee_date >= start_date, GovernmentFee.fee_date <= end_date)
        except ValueError:
            pass
    
    # تنفيذ الاستعلام
    fees = query.order_by(GovernmentFee.fee_date.desc()).all()
    
    # تحويل النتائج إلى قائمة
    result = []
    for fee in fees:
        result.append({
            'id': fee.id,
            'employee_id': fee.employee.id,
            'employee_name': fee.employee.name,
            'fee_type': fee.fee_type,
            'fee_date': fee.fee_date.strftime('%Y-%m-%d'),
            'amount': fee.amount,
            'payment_status': fee.payment_status
        })
    
    return jsonify(result)

@government_fees_bp.route('/reports/custom')
def custom_report():
    """تصدير تقرير مخصص"""
    # استلام معايير التصفية
    fee_type = request.args.get('fee_type')
    payment_status = request.args.get('payment_status')
    department_id = request.args.get('department_id')
    date_range = request.args.get('date_range')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    # معالجة الفترة الزمنية
    year = None
    month = None
    
    today = datetime.now().date()
    if date_range == 'current_month':
        year = today.year
        month = today.month
    elif date_range == 'current_year':
        year = today.year
    
    # تصدير البيانات
    output, filename = export_government_fees_data(
        fee_type=fee_type,
        payment_status=payment_status,
        department_id=department_id,
        year=year,
        month=month
    )
    
    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )

@government_fees_bp.route('/export')
def export_data():
    """تصدير جميع بيانات الرسوم الحكومية"""
    content = request.args.get('content', 'all')
    
    # تحديد المعايير حسب المحتوى المطلوب
    fee_type = None
    payment_status = None
    year = None
    
    if content == 'current_year':
        year = datetime.now().year
    elif content == 'pending':
        payment_status = 'pending'
    elif content == 'paid':
        payment_status = 'paid'
    
    # تصدير البيانات
    output, filename = export_government_fees_data(
        fee_type=fee_type,
        payment_status=payment_status,
        year=year
    )
    
    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )