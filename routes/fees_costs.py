from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func, extract
from app import db
from models import FeesCost, Document, Employee, Department, SystemAudit

fees_costs_bp = Blueprint('fees_costs', __name__, url_prefix='/fees-costs')

@fees_costs_bp.route('/')
@login_required
def index():
    """عرض صفحة قائمة تكاليف الرسوم مع الوثائق المنتهية والمشرفة على الانتهاء"""
    # استخراج الوثائق المنتهية أو التي تقترب من الانتهاء
    today = datetime.now().date()
    expiry_date_limit = today + timedelta(days=90)  # 90 يومًا من الآن
    
    expired_docs = Document.query.filter(Document.expiry_date < today).join(Employee).order_by(Document.expiry_date.desc()).limit(10).all()
    expiring_docs = Document.query.filter(
        Document.expiry_date >= today,
        Document.expiry_date <= expiry_date_limit
    ).join(Employee).order_by(Document.expiry_date).limit(10).all()
    
    # استخراج تكاليف الرسوم المسجلة
    fees_costs = FeesCost.query.join(Document).join(Employee).all()
    
    # إحصائيات
    total_passport_fees = db.session.query(func.sum(FeesCost.passport_fee)).scalar() or 0
    total_labor_fees = db.session.query(func.sum(FeesCost.labor_office_fee)).scalar() or 0
    total_insurance_fees = db.session.query(func.sum(FeesCost.insurance_fee)).scalar() or 0
    total_social_insurance_fees = db.session.query(func.sum(FeesCost.social_insurance_fee)).scalar() or 0
    total_fees = total_passport_fees + total_labor_fees + total_insurance_fees + total_social_insurance_fees
    
    return render_template('fees_costs/index.html',
                          expired_docs=expired_docs,
                          expiring_docs=expiring_docs,
                          fees_costs=fees_costs,
                          total_passport_fees=total_passport_fees,
                          total_labor_fees=total_labor_fees,
                          total_insurance_fees=total_insurance_fees,
                          total_social_insurance_fees=total_social_insurance_fees,
                          total_fees=total_fees)

@fees_costs_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """إضافة تكاليف رسوم جديدة"""
    if request.method == 'POST':
        document_id = request.form.get('document_id')
        document_type = request.form.get('document_type')
        passport_fee = float(request.form.get('passport_fee', 0))
        labor_office_fee = float(request.form.get('labor_office_fee', 0))
        insurance_fee = float(request.form.get('insurance_fee', 0))
        social_insurance_fee = float(request.form.get('social_insurance_fee', 0))
        transfer_sponsorship = True if request.form.get('transfer_sponsorship') else False
        due_date = datetime.strptime(request.form.get('due_date'), '%Y-%m-%d').date()
        payment_status = request.form.get('payment_status')
        payment_date = None
        if request.form.get('payment_date'):
            payment_date = datetime.strptime(request.form.get('payment_date'), '%Y-%m-%d').date()
        notes = request.form.get('notes')
        
        try:
            # التحقق من وجود الوثيقة
            document = Document.query.get_or_404(document_id)
            
            # إنشاء كائن تكاليف الرسوم
            fees_cost = FeesCost(
                document_id=document_id,
                document_type=document_type,
                passport_fee=passport_fee,
                labor_office_fee=labor_office_fee,
                insurance_fee=insurance_fee,
                social_insurance_fee=social_insurance_fee,
                transfer_sponsorship=transfer_sponsorship,
                due_date=due_date,
                payment_status=payment_status,
                payment_date=payment_date,
                notes=notes
            )
            
            # حفظ البيانات
            db.session.add(fees_cost)
            db.session.commit()
            
            # سجل التدقيق
            audit = SystemAudit(
                action='create',
                entity_type='fees_cost',
                entity_id=fees_cost.id,
                details=f'تم إضافة تكاليف رسوم جديدة للوثيقة رقم {document_id}',
                user_id=current_user.id
            )
            db.session.add(audit)
            db.session.commit()
            
            flash('تمت إضافة تكاليف الرسوم بنجاح', 'success')
            return redirect(url_for('fees_costs.index'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء إضافة تكاليف الرسوم: {str(e)}', 'danger')
    
    # عرض نموذج إضافة تكاليف رسوم
    # الحصول على الوثائق المنتهية أو المشرفة على الانتهاء
    today = datetime.now().date()
    expiry_date_limit = today + timedelta(days=90)
    
    documents = Document.query.filter(
        (Document.expiry_date < today) | 
        ((Document.expiry_date >= today) & (Document.expiry_date <= expiry_date_limit))
    ).join(Employee).all()
    
    return render_template('fees_costs/create.html',
                          documents=documents,
                          today=today.strftime('%Y-%m-%d'),
                          next_month=today.replace(month=today.month+1 if today.month < 12 else 1, year=today.year+1 if today.month==12 else today.year).strftime('%Y-%m-%d'))

@fees_costs_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    """تعديل تكاليف رسوم موجودة"""
    fees_cost = FeesCost.query.get_or_404(id)
    
    if request.method == 'POST':
        fees_cost.passport_fee = float(request.form.get('passport_fee', 0))
        fees_cost.labor_office_fee = float(request.form.get('labor_office_fee', 0))
        fees_cost.insurance_fee = float(request.form.get('insurance_fee', 0))
        fees_cost.social_insurance_fee = float(request.form.get('social_insurance_fee', 0))
        fees_cost.transfer_sponsorship = True if request.form.get('transfer_sponsorship') else False
        fees_cost.due_date = datetime.strptime(request.form.get('due_date'), '%Y-%m-%d').date()
        fees_cost.payment_status = request.form.get('payment_status')
        
        if request.form.get('payment_date'):
            fees_cost.payment_date = datetime.strptime(request.form.get('payment_date'), '%Y-%m-%d').date()
        
        fees_cost.notes = request.form.get('notes')
        
        try:
            # سجل التدقيق
            audit = SystemAudit(
                action='update',
                entity_type='fees_cost',
                entity_id=fees_cost.id,
                details=f'تم تحديث تكاليف الرسوم للوثيقة رقم {fees_cost.document_id}',
                user_id=current_user.id
            )
            db.session.add(audit)
            
            # حفظ التغييرات
            db.session.commit()
            
            flash('تم تحديث تكاليف الرسوم بنجاح', 'success')
            return redirect(url_for('fees_costs.index'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء تحديث تكاليف الرسوم: {str(e)}', 'danger')
    
    return render_template('fees_costs/edit.html',
                          fees_cost=fees_cost,
                          today=datetime.now().date().strftime('%Y-%m-%d'))

@fees_costs_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    """حذف تكاليف رسوم"""
    try:
        fees_cost = FeesCost.query.get_or_404(id)
        document_id = fees_cost.document_id
        
        # سجل التدقيق
        audit = SystemAudit(
            action='delete',
            entity_type='fees_cost',
            entity_id=id,
            details=f'تم حذف تكاليف الرسوم للوثيقة رقم {document_id}',
            user_id=current_user.id
        )
        db.session.add(audit)
        
        # حذف تكاليف الرسوم
        db.session.delete(fees_cost)
        db.session.commit()
        
        flash('تم حذف تكاليف الرسوم بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء حذف تكاليف الرسوم: {str(e)}', 'danger')
    
    return redirect(url_for('fees_costs.index'))

@fees_costs_bp.route('/document/<int:document_id>')
@login_required
def document_details(document_id):
    """عرض تفاصيل الوثيقة وتكاليف الرسوم المرتبطة بها"""
    document = Document.query.get_or_404(document_id)
    fees_costs = FeesCost.query.filter_by(document_id=document_id).all()
    
    return render_template('fees_costs/document_details.html',
                          document=document,
                          fees_costs=fees_costs)

@fees_costs_bp.route('/expiring-documents')
@login_required
def expiring_documents():
    """عرض الوثائق التي تقترب من انتهاء صلاحيتها"""
    days = int(request.args.get('days', 90))
    
    today = datetime.now().date()
    expiry_date_limit = today + timedelta(days=days)
    
    documents = Document.query.filter(
        Document.expiry_date >= today,
        Document.expiry_date <= expiry_date_limit
    ).join(Employee).order_by(Document.expiry_date).all()
    
    return render_template('fees_costs/expiring_documents.html',
                          documents=documents,
                          days=days,
                          today=today)

@fees_costs_bp.route('/expired-documents')
@login_required
def expired_documents():
    """عرض الوثائق المنتهية"""
    today = datetime.now().date()
    
    documents = Document.query.filter(Document.expiry_date < today).join(Employee).order_by(Document.expiry_date.desc()).all()
    
    return render_template('fees_costs/expired_documents.html',
                          documents=documents,
                          today=today)