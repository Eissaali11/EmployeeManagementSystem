"""
طرق النظام المحاسبي
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, make_response
from flask_login import login_required, current_user
from sqlalchemy import func, and_, or_, extract, desc, asc
from sqlalchemy.orm import joinedload
from datetime import datetime, date, timedelta
from decimal import Decimal
import json

from app import db
from models import UserRole
from models_accounting import *
from forms.accounting import *
from utils.helpers import log_activity

# إنشاء البلوبرينت
accounting_bp = Blueprint('accounting', __name__, url_prefix='/accounting')


# ==================== الصفحة الرئيسية ====================

@accounting_bp.route('/')
@login_required
def dashboard():
    """لوحة تحكم المحاسبة"""
    if current_user.role not in [UserRole.ADMIN, UserRole.FINANCE]:
        flash('غير مسموح لك بالوصول لهذه الصفحة', 'danger')
        return redirect(url_for('dashboard.index'))
    
    try:
        # السنة المالية النشطة
        active_fiscal_year = FiscalYear.query.filter_by(is_active=True).first()
        if not active_fiscal_year:
            flash('لا توجد سنة مالية نشطة. يرجى إنشاء سنة مالية أولاً.', 'warning')
            return redirect(url_for('accounting.fiscal_years'))
        
        # إحصائيات سريعة
        current_month_start = date.today().replace(day=1)
        current_month_end = (current_month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        # إجمالي الأصول
        total_assets = db.session.query(func.sum(Account.balance)).filter(
            Account.account_type == AccountType.ASSETS,
            Account.is_active == True
        ).scalar() or 0
        
        # إجمالي الخصوم
        total_liabilities = db.session.query(func.sum(Account.balance)).filter(
            Account.account_type == AccountType.LIABILITIES,
            Account.is_active == True
        ).scalar() or 0
        
        # صافي الأرباح هذا الشهر
        monthly_revenue = db.session.query(func.sum(Account.balance)).filter(
            Account.account_type == AccountType.REVENUE,
            Account.is_active == True
        ).scalar() or 0
        
        monthly_expenses = db.session.query(func.sum(Account.balance)).filter(
            Account.account_type == AccountType.EXPENSES,
            Account.is_active == True
        ).scalar() or 0
        
        net_profit = monthly_revenue - monthly_expenses
        
        # أحدث المعاملات
        recent_transactions = Transaction.query.filter(
            Transaction.fiscal_year_id == active_fiscal_year.id,
            Transaction.is_approved == True
        ).order_by(desc(Transaction.transaction_date)).limit(10).all()
        
        # معاملات في انتظار الاعتماد
        pending_transactions = Transaction.query.filter(
            Transaction.fiscal_year_id == active_fiscal_year.id,
            Transaction.is_approved == False
        ).count()
        
        # مراكز التكلفة الأكثر إنفاقاً هذا الشهر
        top_cost_centers = db.session.query(
            CostCenter.name,
            func.sum(Transaction.total_amount).label('total_spent')
        ).join(Transaction).filter(
            Transaction.transaction_date >= current_month_start,
            Transaction.transaction_date <= current_month_end,
            Transaction.is_approved == True,
            Transaction.transaction_type.in_(['expenses', 'vehicle_expense', 'salary'])
        ).group_by(CostCenter.id).order_by(desc('total_spent')).limit(5).all()
        
        return render_template('accounting/dashboard.html',
                             total_assets=total_assets,
                             total_liabilities=total_liabilities,
                             net_profit=net_profit,
                             recent_transactions=recent_transactions,
                             pending_transactions=pending_transactions,
                             top_cost_centers=top_cost_centers,
                             active_fiscal_year=active_fiscal_year)
    
    except Exception as e:
        flash(f'خطأ في تحميل لوحة التحكم: {str(e)}', 'danger')
        return redirect(url_for('dashboard.index'))


# ==================== دليل الحسابات ====================

@accounting_bp.route('/accounts')
@login_required
def accounts():
    """قائمة الحسابات"""
    if current_user.role not in [UserRole.ADMIN, UserRole.FINANCE]:
        flash('غير مسموح لك بالوصول لهذه الصفحة', 'danger')
        return redirect(url_for('dashboard.index'))
    
    search_term = request.args.get('search', '')
    account_type_filter = request.args.get('type', '')
    page = request.args.get('page', 1, type=int)
    
    query = Account.query
    
    if search_term:
        query = query.filter(or_(
            Account.name.contains(search_term),
            Account.code.contains(search_term)
        ))
    
    if account_type_filter:
        query = query.filter(Account.account_type == account_type_filter)
    
    accounts_list = query.order_by(Account.code).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('accounting/accounts/index.html',
                         accounts=accounts_list,
                         search_term=search_term,
                         account_type_filter=account_type_filter)


@accounting_bp.route('/accounts/new', methods=['GET', 'POST'])
@login_required
def add_account():
    """إضافة حساب جديد"""
    if current_user.role not in [UserRole.ADMIN, UserRole.FINANCE]:
        flash('غير مسموح لك بالوصول لهذه الصفحة', 'danger')
        return redirect(url_for('dashboard.index'))
    
    form = AccountForm()
    
    # تحميل الحسابات الأب
    parent_accounts = Account.query.filter_by(is_active=True).all()
    form.parent_id.choices = [('', 'لا يوجد')] + [(acc.id, f"{acc.code} - {acc.name}") for acc in parent_accounts]
    
    if form.validate_on_submit():
        try:
            # التحقق من عدم وجود رمز مكرر
            existing = Account.query.filter_by(code=form.code.data).first()
            if existing:
                flash('رمز الحساب موجود مسبقاً', 'danger')
                return render_template('accounting/accounts/form.html', form=form, title='إضافة حساب جديد')
            
            account = Account(
                code=form.code.data,
                name=form.name.data,
                name_en=form.name_en.data,
                account_type=AccountType(form.account_type.data),
                parent_id=form.parent_id.data if form.parent_id.data else None,
                description=form.description.data,
                is_active=form.is_active.data
            )
            
            # حساب المستوى
            if account.parent_id:
                parent = Account.query.get(account.parent_id)
                account.level = parent.level + 1
            else:
                account.level = 0
            
            db.session.add(account)
            db.session.commit()
            
            log_activity(f"إضافة حساب جديد: {account.name} ({account.code})")
            flash('تم إضافة الحساب بنجاح', 'success')
            return redirect(url_for('accounting.accounts'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'خطأ في إضافة الحساب: {str(e)}', 'danger')
    
    return render_template('accounting/accounts/form.html', form=form, title='إضافة حساب جديد')


@accounting_bp.route('/accounts/<int:account_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_account(account_id):
    """تعديل حساب"""
    if current_user.role not in [UserRole.ADMIN, UserRole.FINANCE]:
        flash('غير مسموح لك بالوصول لهذه الصفحة', 'danger')
        return redirect(url_for('dashboard.index'))
    
    account = Account.query.get_or_404(account_id)
    form = AccountForm(obj=account)
    
    # تحميل الحسابات الأب (ما عدا الحساب نفسه)
    parent_accounts = Account.query.filter(
        Account.is_active == True,
        Account.id != account.id
    ).all()
    form.parent_id.choices = [('', 'لا يوجد')] + [(acc.id, f"{acc.code} - {acc.name}") for acc in parent_accounts]
    
    if form.validate_on_submit():
        try:
            # التحقق من عدم وجود رمز مكرر
            existing = Account.query.filter(
                Account.code == form.code.data,
                Account.id != account.id
            ).first()
            if existing:
                flash('رمز الحساب موجود مسبقاً', 'danger')
                return render_template('accounting/accounts/form.html', form=form, title='تعديل حساب', account=account)
            
            account.code = form.code.data
            account.name = form.name.data
            account.name_en = form.name_en.data
            account.account_type = AccountType(form.account_type.data)
            account.parent_id = form.parent_id.data if form.parent_id.data else None
            account.description = form.description.data
            account.is_active = form.is_active.data
            account.updated_at = datetime.utcnow()
            
            # إعادة حساب المستوى
            if account.parent_id:
                parent = Account.query.get(account.parent_id)
                account.level = parent.level + 1
            else:
                account.level = 0
            
            db.session.commit()
            
            log_activity(f"تعديل حساب: {account.name} ({account.code})")
            flash('تم تعديل الحساب بنجاح', 'success')
            return redirect(url_for('accounting.accounts'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'خطأ في تعديل الحساب: {str(e)}', 'danger')
    
    return render_template('accounting/accounts/form.html', form=form, title='تعديل حساب', account=account)


@accounting_bp.route('/accounts/<int:account_id>/view')
@login_required
def view_account(account_id):
    """عرض تفاصيل حساب"""
    if current_user.role not in [UserRole.ADMIN, UserRole.FINANCE]:
        flash('غير مسموح لك بالوصول لهذه الصفحة', 'danger')
        return redirect(url_for('dashboard.index'))
    
    account = Account.query.get_or_404(account_id)
    
    # آخر المعاملات
    recent_entries = TransactionEntry.query.filter_by(account_id=account.id)\
        .join(Transaction)\
        .filter(Transaction.is_approved == True)\
        .order_by(desc(Transaction.transaction_date))\
        .limit(20).all()
    
    # الرصيد الشهري للسنة الحالية
    current_year = datetime.now().year
    monthly_balances = []
    
    for month in range(1, 13):
        month_start = date(current_year, month, 1)
        if month == 12:
            month_end = date(current_year + 1, 1, 1) - timedelta(days=1)
        else:
            month_end = date(current_year, month + 1, 1) - timedelta(days=1)
        
        # حساب الرصيد حتى نهاية الشهر
        debits = db.session.query(func.sum(TransactionEntry.amount)).join(Transaction).filter(
            TransactionEntry.account_id == account.id,
            TransactionEntry.entry_type == EntryType.DEBIT,
            Transaction.transaction_date <= month_end,
            Transaction.is_approved == True
        ).scalar() or 0
        
        credits = db.session.query(func.sum(TransactionEntry.amount)).join(Transaction).filter(
            TransactionEntry.account_id == account.id,
            TransactionEntry.entry_type == EntryType.CREDIT,
            Transaction.transaction_date <= month_end,
            Transaction.is_approved == True
        ).scalar() or 0
        
        balance = debits - credits if account.account_type in [AccountType.ASSETS, AccountType.EXPENSES] else credits - debits
        monthly_balances.append(balance)
    
    return render_template('accounting/accounts/view.html',
                         account=account,
                         recent_entries=recent_entries,
                         monthly_balances=monthly_balances)


# ==================== القيود المحاسبية ====================

@accounting_bp.route('/transactions')
@login_required
def transactions():
    """قائمة القيود المحاسبية"""
    if current_user.role not in [UserRole.ADMIN, UserRole.FINANCE]:
        flash('غير مسموح لك بالوصول لهذه الصفحة', 'danger')
        return redirect(url_for('dashboard.index'))
    
    search_term = request.args.get('search', '')
    transaction_type_filter = request.args.get('type', '')
    status_filter = request.args.get('status', '')
    from_date = request.args.get('from_date', '')
    to_date = request.args.get('to_date', '')
    page = request.args.get('page', 1, type=int)
    
    query = Transaction.query.options(joinedload(Transaction.created_by))
    
    if search_term:
        query = query.filter(or_(
            Transaction.description.contains(search_term),
            Transaction.reference_number.contains(search_term),
            Transaction.transaction_number.contains(search_term)
        ))
    
    if transaction_type_filter:
        query = query.filter(Transaction.transaction_type == transaction_type_filter)
    
    if status_filter == 'pending':
        query = query.filter(Transaction.is_approved == False)
    elif status_filter == 'approved':
        query = query.filter(Transaction.is_approved == True)
    
    if from_date:
        query = query.filter(Transaction.transaction_date >= datetime.strptime(from_date, '%Y-%m-%d').date())
    
    if to_date:
        query = query.filter(Transaction.transaction_date <= datetime.strptime(to_date, '%Y-%m-%d').date())
    
    transactions_list = query.order_by(desc(Transaction.transaction_date), desc(Transaction.id)).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('accounting/transactions/index.html',
                         transactions=transactions_list,
                         search_term=search_term,
                         transaction_type_filter=transaction_type_filter,
                         status_filter=status_filter,
                         from_date=from_date,
                         to_date=to_date)


@accounting_bp.route('/transactions/new', methods=['GET', 'POST'])
@login_required
def add_transaction():
    """إضافة قيد محاسبي جديد"""
    if current_user.role not in [UserRole.ADMIN, UserRole.FINANCE]:
        flash('غير مسموح لك بالوصول لهذه الصفحة', 'danger')
        return redirect(url_for('dashboard.index'))
    
    form = TransactionForm()
    
    # تحميل البيانات للقوائم المنسدلة
    accounts = Account.query.filter_by(is_active=True).order_by(Account.code).all()
    cost_centers = CostCenter.query.filter_by(is_active=True).all()
    vendors = Vendor.query.filter_by(is_active=True).all()
    customers = Customer.query.filter_by(is_active=True).all()
    
    # تحديث خيارات النماذج
    for entry_form in form.entries:
        entry_form.account_id.choices = [(acc.id, f"{acc.code} - {acc.name}") for acc in accounts]
    
    form.cost_center_id.choices = [('', 'لا يوجد')] + [(cc.id, cc.name) for cc in cost_centers]
    form.vendor_id.choices = [('', 'لا يوجد')] + [(v.id, v.name) for v in vendors]
    form.customer_id.choices = [('', 'لا يوجد')] + [(c.id, c.name) for c in customers]
    
    if request.method == 'POST':
        # التحقق من توازن القيد
        total_debits = sum(float(entry.amount.data) for entry in form.entries if entry.entry_type.data == 'debit' and entry.amount.data)
        total_credits = sum(float(entry.amount.data) for entry in form.entries if entry.entry_type.data == 'credit' and entry.amount.data)
        
        if abs(total_debits - total_credits) > 0.01:
            flash('خطأ: القيد غير متوازن. مجموع المدين يجب أن يساوي مجموع الدائن', 'danger')
        elif form.validate_on_submit() and total_debits > 0:
            try:
                # الحصول على رقم القيد التالي
                settings = AccountingSettings.query.first()
                if not settings:
                    settings = AccountingSettings(
                        company_name='شركة نُظم',
                        next_transaction_number=1
                    )
                    db.session.add(settings)
                    db.session.flush()
                
                transaction_number = f"{settings.transaction_prefix}{settings.next_transaction_number:06d}"
                
                # السنة المالية النشطة
                fiscal_year = FiscalYear.query.filter_by(is_active=True).first()
                if not fiscal_year:
                    flash('لا توجد سنة مالية نشطة', 'danger')
                    return render_template('accounting/transactions/form.html', form=form, title='إضافة قيد جديد')
                
                # إنشاء المعاملة
                transaction = Transaction(
                    transaction_number=transaction_number,
                    transaction_date=form.transaction_date.data,
                    transaction_type=TransactionType(form.transaction_type.data),
                    reference_number=form.reference_number.data,
                    description=form.description.data,
                    total_amount=Decimal(str(total_debits)),
                    fiscal_year_id=fiscal_year.id,
                    cost_center_id=form.cost_center_id.data if form.cost_center_id.data else None,
                    vendor_id=form.vendor_id.data if form.vendor_id.data else None,
                    customer_id=form.customer_id.data if form.customer_id.data else None,
                    created_by_id=current_user.id
                )
                
                db.session.add(transaction)
                db.session.flush()
                
                # إضافة تفاصيل القيد
                for entry_form in form.entries:
                    if entry_form.account_id.data and entry_form.amount.data:
                        entry = TransactionEntry(
                            transaction_id=transaction.id,
                            account_id=entry_form.account_id.data,
                            entry_type=EntryType(entry_form.entry_type.data),
                            amount=Decimal(str(entry_form.amount.data)),
                            description=entry_form.description.data
                        )
                        db.session.add(entry)
                
                # تحديث رقم القيد التالي
                settings.next_transaction_number += 1
                
                db.session.commit()
                
                log_activity(f"إضافة قيد محاسبي: {transaction.transaction_number}")
                flash('تم إضافة القيد بنجاح', 'success')
                return redirect(url_for('accounting.transactions'))
                
            except Exception as e:
                db.session.rollback()
                flash(f'خطأ في إضافة القيد: {str(e)}', 'danger')
    
    return render_template('accounting/transactions/form.html', form=form, title='إضافة قيد جديد')


# سأكمل باقي الطرق في ملف منفصل لتجنب كون الملف كبير جداً