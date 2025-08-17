"""
طرق إضافية للنظام المحاسبي - الجزء الثاني
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, make_response, send_file
from flask_login import login_required, current_user
from sqlalchemy import func, and_, or_, extract, desc, asc, text
from sqlalchemy.orm import joinedload
from datetime import datetime, date, timedelta
from decimal import Decimal
import json
import io
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

from app import db
from models import UserRole, Employee, Vehicle, Department, Module, Permission
from models_accounting import *
from forms.accounting import *
from utils.helpers import log_activity

# إنشاء البلوبرينت الثاني
accounting_ext_bp = Blueprint('accounting_ext', __name__, url_prefix='/accounting')


# ==================== القيد السريع ====================

@accounting_ext_bp.route('/quick-entry', methods=['GET', 'POST'])
@login_required
def quick_entry():
    """القيد السريع"""
    if not (current_user.role == UserRole.ADMIN or current_user.has_module_access(Module.ACCOUNTING)):
        flash('غير مسموح لك بالوصول لهذه الصفحة', 'danger')
        return redirect(url_for('dashboard.index'))
    
    form = QuickEntryForm()
    
    # تحميل الحسابات
    accounts = Account.query.filter_by(is_active=True).order_by(Account.code).all()
    cost_centers = CostCenter.query.filter_by(is_active=True).all()
    
    form.debit_account_id.choices = [(acc.id, f"{acc.code} - {acc.name}") for acc in accounts]
    form.credit_account_id.choices = [(acc.id, f"{acc.code} - {acc.name}") for acc in accounts]
    form.cost_center_id.choices = [('', 'لا يوجد')] + [(cc.id, cc.name) for cc in cost_centers]
    
    if form.validate_on_submit():
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
                return render_template('accounting/quick_entry.html', form=form)
            
            # إنشاء المعاملة
            transaction = Transaction(
                transaction_number=transaction_number,
                transaction_date=form.transaction_date.data,
                transaction_type=TransactionType.MANUAL,
                reference_number=form.reference_number.data,
                description=form.description.data,
                total_amount=form.amount.data,
                fiscal_year_id=fiscal_year.id,
                cost_center_id=form.cost_center_id.data if form.cost_center_id.data else None,
                created_by_id=current_user.id,
                is_approved=True,  # القيد السريع يتم اعتماده تلقائياً
                approval_date=datetime.utcnow(),
                approved_by_id=current_user.id
            )
            
            db.session.add(transaction)
            db.session.flush()
            
            # إضافة القيد المدين
            debit_entry = TransactionEntry(
                transaction_id=transaction.id,
                account_id=form.debit_account_id.data,
                entry_type=EntryType.DEBIT,
                amount=form.amount.data,
                description=form.description.data
            )
            db.session.add(debit_entry)
            
            # إضافة القيد الدائن
            credit_entry = TransactionEntry(
                transaction_id=transaction.id,
                account_id=form.credit_account_id.data,
                entry_type=EntryType.CREDIT,
                amount=form.amount.data,
                description=form.description.data
            )
            db.session.add(credit_entry)
            
            # تحديث أرصدة الحسابات
            debit_account = Account.query.get(form.debit_account_id.data)
            credit_account = Account.query.get(form.credit_account_id.data)
            
            if debit_account.account_type in [AccountType.ASSETS, AccountType.EXPENSES]:
                debit_account.balance += form.amount.data
            else:
                debit_account.balance -= form.amount.data
            
            if credit_account.account_type in [AccountType.ASSETS, AccountType.EXPENSES]:
                credit_account.balance -= form.amount.data
            else:
                credit_account.balance += form.amount.data
            
            # تحديث رقم القيد التالي
            settings.next_transaction_number += 1
            
            db.session.commit()
            
            log_activity(f"إضافة قيد سريع: {transaction.transaction_number}")
            flash('تم إضافة القيد بنجاح', 'success')
            return redirect(url_for('accounting.transactions'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'خطأ في إضافة القيد: {str(e)}', 'danger')
    
    return render_template('accounting/quick_entry.html', form=form)


# ==================== معالجة الرواتب ====================

@accounting_ext_bp.route('/salary-processing', methods=['GET', 'POST'])
@login_required
def salary_processing():
    """معالجة رواتب الموظفين"""
    if not (current_user.role == UserRole.ADMIN or current_user.has_module_access(Module.ACCOUNTING)):
        flash('غير مسموح لك بالوصول لهذه الصفحة', 'danger')
        return redirect(url_for('dashboard.index'))
    
    form = SalaryProcessingForm()
    
    # تحميل الأقسام والحسابات
    departments = Department.query.all()
    accounts = Account.query.filter_by(is_active=True).all()
    
    form.department_id.choices = [('', 'جميع الأقسام')] + [(d.id, d.name) for d in departments]
    form.salary_account_id.choices = [('', 'اختر حساب الرواتب')] + [(a.id, f"{a.code} - {a.name}") for a in accounts if 'راتب' in a.name or a.code.startswith('5')]
    form.payable_account_id.choices = [('', 'اختر حساب المستحقات')] + [(a.id, f"{a.code} - {a.name}") for a in accounts if 'دائن' in a.name or 'مستحق' in a.name or a.code.startswith('2')]
    
    if form.validate_on_submit():
        try:
            # التحقق من وجود معالجة سابقة لنفس الشهر
            existing_processing = Transaction.query.filter(
                Transaction.transaction_type == TransactionType.SALARY,
                extract('month', Transaction.transaction_date) == int(form.month.data),
                extract('year', Transaction.transaction_date) == form.year.data
            ).first()
            
            if existing_processing:
                flash(f'تم معالجة رواتب شهر {form.month.data}/{form.year.data} مسبقاً', 'warning')
                return render_template('accounting/salary_processing.html', form=form)
            
            # تحديد الموظفين المشمولين
            employees_query = Employee.query.filter_by(status='active')
            
            if not form.process_all.data and form.department_id.data:
                employees_query = employees_query.join(Employee.departments).filter(
                    Department.id == form.department_id.data
                )
            
            employees = employees_query.all()
            
            if not employees:
                flash('لا يوجد موظفين للمعالجة', 'warning')
                return render_template('accounting/salary_processing.html', form=form)
            
            # الحصول على الحسابات المحاسبية
            salary_expense_account = Account.query.filter_by(code='4101').first()  # مصروف رواتب
            cash_account = Account.query.filter_by(code='1001').first()  # النقدية
            
            print(f"DEBUG: salary_expense_account found: {salary_expense_account}")
            print(f"DEBUG: cash_account found: {cash_account}")
            
            if not salary_expense_account or not cash_account:
                missing_accounts = []
                if not salary_expense_account:
                    missing_accounts.append('مصروف رواتب (4101)')
                if not cash_account:
                    missing_accounts.append('النقدية (1001)')
                flash(f'الحسابات المحاسبية المفقودة: {", ".join(missing_accounts)}', 'danger')
                return render_template('accounting/salary_processing.html', form=form)
            
            # إعدادات النظام
            settings = AccountingSettings.query.first()
            if not settings:
                settings = AccountingSettings(company_name='شركة نُظم', next_transaction_number=1)
                db.session.add(settings)
                db.session.flush()
            
            fiscal_year = FiscalYear.query.filter_by(is_active=True).first()
            
            total_salaries = Decimal('0')
            processed_count = 0
            
            # معالجة كل موظف
            for employee in employees:
                if not employee.salary:
                    continue
                
                # حساب الراتب الفعلي (راتب أساسي + بدلات - خصومات)
                basic_salary = Decimal(str(employee.salary))
                allowances = Decimal(str(employee.allowances or 0))
                deductions = Decimal(str(employee.deductions or 0))
                net_salary = basic_salary + allowances - deductions
                
                if net_salary <= 0:
                    continue
                
                # إنشاء قيد الراتب
                transaction_number = f"{settings.transaction_prefix}{settings.next_transaction_number:06d}"
                
                transaction = Transaction(
                    transaction_number=transaction_number,
                    transaction_date=date(form.year.data, int(form.month.data), 1),
                    transaction_type=TransactionType.SALARY,
                    description=f"راتب شهر {form.month.data}/{form.year.data} - {employee.name}",
                    total_amount=net_salary,
                    fiscal_year_id=fiscal_year.id,
                    employee_id=employee.id,
                    created_by_id=current_user.id,
                    is_approved=True,
                    approval_date=datetime.utcnow(),
                    approved_by_id=current_user.id
                )
                
                db.session.add(transaction)
                db.session.flush()
                
                # قيد مدين: مصروف رواتب
                debit_entry = TransactionEntry(
                    transaction_id=transaction.id,
                    account_id=salary_expense_account.id,
                    entry_type=EntryType.DEBIT,
                    amount=net_salary,
                    description=f"راتب {employee.name}"
                )
                db.session.add(debit_entry)
                
                # قيد دائن: النقدية
                credit_entry = TransactionEntry(
                    transaction_id=transaction.id,
                    account_id=cash_account.id,
                    entry_type=EntryType.CREDIT,
                    amount=net_salary,
                    description=f"صرف راتب {employee.name}"
                )
                db.session.add(credit_entry)
                
                # تحديث أرصدة الحسابات
                salary_expense_account.balance += net_salary
                cash_account.balance -= net_salary
                
                total_salaries += net_salary
                processed_count += 1
                settings.next_transaction_number += 1
            
            db.session.commit()
            
            log_activity(f"معالجة رواتب شهر {form.month.data}/{form.year.data}: {processed_count} موظف بإجمالي {total_salaries} ريال")
            flash(f'تم معالجة رواتب {processed_count} موظف بإجمالي {total_salaries:,.2f} ريال', 'success')
            return redirect(url_for('accounting.transactions'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'خطأ في معالجة الرواتب: {str(e)}', 'danger')
    
    return render_template('accounting/salary_processing.html', form=form)


# ==================== مصروفات المركبات ====================

@accounting_ext_bp.route('/vehicle-expenses', methods=['GET', 'POST'])
@login_required
def vehicle_expenses():
    """إدخال مصروفات المركبات"""
    if not (current_user.role == UserRole.ADMIN or current_user.has_module_access(Module.ACCOUNTING)):
        flash('غير مسموح لك بالوصول لهذه الصفحة', 'danger')
        return redirect(url_for('dashboard.index'))
    
    form = VehicleExpenseForm()
    
    # تحميل المركبات والموردين
    vehicles = Vehicle.query.all()
    vendors = Vendor.query.filter_by(is_active=True).all()
    
    form.vehicle_id.choices = [(v.id, f"{v.plate_number} - {v.make} {v.model}") for v in vehicles]
    form.vendor_id.choices = [('', 'لا يوجد')] + [(v.id, v.name) for v in vendors]
    
    if form.validate_on_submit():
        try:
            # الحصول على الحسابات المحاسبية
            expense_accounts = {
                'fuel': Account.query.filter_by(code='5101').first(),  # مصروف وقود
                'maintenance': Account.query.filter_by(code='5102').first(),  # مصروف صيانة
                'insurance': Account.query.filter_by(code='5103').first(),  # مصروف تأمين
                'registration': Account.query.filter_by(code='5104').first(),  # مصروف تسجيل
                'fines': Account.query.filter_by(code='5105').first(),  # مخالفات
                'other': Account.query.filter_by(code='5199').first()  # مصروفات أخرى
            }
            
            expense_account = expense_accounts.get(form.expense_type.data)
            cash_account = Account.query.filter_by(code='1001').first()  # النقدية
            
            if not expense_account or not cash_account:
                flash('الحسابات المحاسبية للمصروفات غير موجودة', 'danger')
                return render_template('accounting/vehicle/expense_form.html', form=form)
            
            # إعدادات النظام
            settings = AccountingSettings.query.first()
            fiscal_year = FiscalYear.query.filter_by(is_active=True).first()
            
            transaction_number = f"{settings.transaction_prefix}{settings.next_transaction_number:06d}"
            
            vehicle = Vehicle.query.get(form.vehicle_id.data)
            
            # إنشاء المعاملة
            transaction = Transaction(
                transaction_number=transaction_number,
                transaction_date=form.expense_date.data,
                transaction_type=TransactionType.VEHICLE_EXPENSE,
                reference_number=form.receipt_number.data if hasattr(form, 'receipt_number') else '',
                description=form.description.data,
                total_amount=form.amount.data,
                fiscal_year_id=fiscal_year.id,
                vehicle_id=vehicle.id,
                vendor_id=form.vendor_id.data if form.vendor_id.data else None,
                created_by_id=current_user.id,
                is_approved=True,
                approval_date=datetime.utcnow(),
                approved_by_id=current_user.id
            )
            
            db.session.add(transaction)
            db.session.flush()
            
            # قيد مدين: مصروف
            debit_entry = TransactionEntry(
                transaction_id=transaction.id,
                account_id=expense_account.id,
                entry_type=EntryType.DEBIT,
                amount=form.amount.data,
                description=f"{form.description.data} - {vehicle.plate_number}"
            )
            db.session.add(debit_entry)
            
            # قيد دائن: النقدية أو حساب المورد
            if form.vendor_id.data:
                vendor = Vendor.query.get(form.vendor_id.data)
                vendor_account = Account.query.filter_by(code=f"2{vendor.id:03d}").first()
                if vendor_account:
                    credit_account = vendor_account
                else:
                    credit_account = cash_account
            else:
                credit_account = cash_account
            
            credit_entry = TransactionEntry(
                transaction_id=transaction.id,
                account_id=credit_account.id,
                entry_type=EntryType.CREDIT,
                amount=form.amount.data,
                description=f"دفع {form.description.data}"
            )
            db.session.add(credit_entry)
            
            # تحديث أرصدة الحسابات
            expense_account.balance += form.amount.data
            credit_account.balance -= form.amount.data
            
            settings.next_transaction_number += 1
            
            db.session.commit()
            
            log_activity(f"إضافة مصروف مركبة: {vehicle.plate_number} - {form.amount.data} ريال")
            flash('تم إضافة مصروف المركبة بنجاح', 'success')
            return redirect(url_for('accounting.transactions'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'خطأ في إضافة مصروف المركبة: {str(e)}', 'danger')
    
    return render_template('accounting/vehicle/expense_form.html', form=form)


# ==================== التقارير ====================

@accounting_ext_bp.route('/reports/trial-balance')
@login_required
def trial_balance():
    """تقرير ميزان المراجعة"""
    if not (current_user.role == UserRole.ADMIN or current_user.has_module_access(Module.ACCOUNTING)):
        flash('غير مسموح لك بالوصول لهذه الصفحة', 'danger')
        return redirect(url_for('dashboard.index'))
    
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    
    # تحديد الفترة الافتراضية (بداية السنة المالية إلى اليوم)
    fiscal_year = FiscalYear.query.filter_by(is_active=True).first()
    if not fiscal_year:
        flash('لا توجد سنة مالية نشطة', 'danger')
        return redirect(url_for('accounting.dashboard'))
    
    if not from_date:
        from_date = fiscal_year.start_date.strftime('%Y-%m-%d')
    if not to_date:
        to_date = date.today().strftime('%Y-%m-%d')
    
    # استعلام أرصدة الحسابات
    from sqlalchemy import case
    
    accounts_balances = db.session.query(
        Account.id,
        Account.code,
        Account.name,
        Account.account_type,
        func.sum(
            case(
                (TransactionEntry.entry_type == EntryType.DEBIT, TransactionEntry.amount),
                else_=0
            )
        ).label('total_debits'),
        func.sum(
            case(
                (TransactionEntry.entry_type == EntryType.CREDIT, TransactionEntry.amount),
                else_=0
            )
        ).label('total_credits')
    ).outerjoin(TransactionEntry).outerjoin(Transaction).filter(
        or_(Transaction.is_approved == True, Transaction.id.is_(None)),
        or_(
            and_(
                Transaction.transaction_date >= datetime.strptime(from_date, '%Y-%m-%d').date(),
                Transaction.transaction_date <= datetime.strptime(to_date, '%Y-%m-%d').date()
            ),
            Transaction.id.is_(None)
        ),
        Account.is_active == True
    ).group_by(Account.id, Account.code, Account.name, Account.account_type).order_by(Account.code).all()
    
    # حساب الأرصدة النهائية
    trial_balance_data = []
    total_debits = Decimal('0')
    total_credits = Decimal('0')
    
    for account in accounts_balances:
        debits = account.total_debits or Decimal('0')
        credits = account.total_credits or Decimal('0')
        
        # حساب الرصيد حسب نوع الحساب
        if account.account_type in [AccountType.ASSETS, AccountType.EXPENSES]:
            balance = debits - credits
            if balance > 0:
                debit_balance = balance
                credit_balance = Decimal('0')
            else:
                debit_balance = Decimal('0')
                credit_balance = abs(balance)
        else:
            balance = credits - debits
            if balance > 0:
                credit_balance = balance
                debit_balance = Decimal('0')
            else:
                credit_balance = Decimal('0')
                debit_balance = abs(balance)
        
        if debit_balance > 0 or credit_balance > 0:
            trial_balance_data.append({
                'code': account.code,
                'name': account.name,
                'account_type': account.account_type.value,
                'debit_balance': debit_balance,
                'credit_balance': credit_balance
            })
            
            total_debits += debit_balance
            total_credits += credit_balance
    
    return render_template('accounting/reports/trial_balance.html',
                         trial_balance_data=trial_balance_data,
                         total_debits=total_debits,
                         total_credits=total_credits,
                         from_date=from_date,
                         to_date=to_date,
                         fiscal_year=fiscal_year)


@accounting_ext_bp.route('/reports/balance-sheet')
@login_required
def balance_sheet():
    """تقرير الميزانية العمومية"""
    if not (current_user.role == UserRole.ADMIN or current_user.has_module_access(Module.ACCOUNTING)):
        flash('غير مسموح لك بالوصول لهذه الصفحة', 'danger')
        return redirect(url_for('dashboard.index'))
    
    as_of_date = request.args.get('as_of_date', date.today().strftime('%Y-%m-%d'))
    
    # أرصدة الحسابات كما في تاريخ محدد
    accounts_query = db.session.query(
        Account.code,
        Account.name,
        Account.account_type,
        func.sum(
            func.case(
                (TransactionEntry.entry_type == EntryType.DEBIT, TransactionEntry.amount),
                else_=0
            ) -
            func.case(
                (TransactionEntry.entry_type == EntryType.CREDIT, TransactionEntry.amount),
                else_=0
            )
        ).label('balance')
    ).outerjoin(TransactionEntry).outerjoin(Transaction).filter(
        Transaction.is_approved == True,
        Transaction.transaction_date <= datetime.strptime(as_of_date, '%Y-%m-%d').date(),
        Account.is_active == True,
        Account.account_type.in_([AccountType.ASSETS, AccountType.LIABILITIES, AccountType.EQUITY])
    ).group_by(Account.id).order_by(Account.code).all()
    
    # تصنيف الحسابات
    assets = []
    liabilities = []
    equity = []
    
    total_assets = Decimal('0')
    total_liabilities = Decimal('0')
    total_equity = Decimal('0')
    
    for account in accounts_query:
        balance = account.balance or Decimal('0')
        
        if account.account_type == AccountType.ASSETS:
            if balance != 0:
                assets.append({
                    'code': account.code,
                    'name': account.name,
                    'balance': balance
                })
                total_assets += balance
        elif account.account_type == AccountType.LIABILITIES:
            if balance != 0:
                liabilities.append({
                    'code': account.code,
                    'name': account.name,
                    'balance': abs(balance)
                })
                total_liabilities += abs(balance)
        elif account.account_type == AccountType.EQUITY:
            if balance != 0:
                equity.append({
                    'code': account.code,
                    'name': account.name,
                    'balance': abs(balance)
                })
                total_equity += abs(balance)
    
    # حساب الأرباح المحتجزة
    revenue_total = db.session.query(func.sum(Account.balance)).filter(
        Account.account_type == AccountType.REVENUE,
        Account.is_active == True
    ).scalar() or Decimal('0')
    
    expense_total = db.session.query(func.sum(Account.balance)).filter(
        Account.account_type == AccountType.EXPENSES,
        Account.is_active == True
    ).scalar() or Decimal('0')
    
    retained_earnings = revenue_total - expense_total
    total_equity += retained_earnings
    
    return render_template('accounting/reports/balance_sheet.html',
                         assets=assets,
                         liabilities=liabilities,
                         equity=equity,
                         retained_earnings=retained_earnings,
                         total_assets=total_assets,
                         total_liabilities=total_liabilities,
                         total_equity=total_equity,
                         as_of_date=as_of_date)