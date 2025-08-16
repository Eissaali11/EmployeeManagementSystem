"""
نظام الإدارة المتكامل - ربط السيارات والحضور والمحاسبة والرواتب
Integrated Management System - Linking Vehicles, Attendance, Accounting, and Salaries
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, send_file
from flask_login import login_required, current_user
from sqlalchemy import extract, func, desc, and_, or_
from datetime import datetime, date, timedelta
import calendar
from decimal import Decimal
import io
try:
    import pandas as pd
except ImportError:
    pd = None

from app import db
# استيراد النماذج الأساسية
from models import (
    Employee, Department, Vehicle, 
    Attendance, Salary, User
)

# استيراد آمن للنماذج المحاسبية والمتقدمة
try:
    from models_accounting import (
        Account, Transaction, TransactionEntry, CostCenter, FiscalYear,
        AccountType, TransactionType, EntryType
    )
except ImportError:
    Account = Transaction = TransactionEntry = CostCenter = FiscalYear = None
    AccountType = TransactionType = EntryType = None

try:
    from models import VehicleRental, VehicleWorkshop
except ImportError:
    VehicleRental = VehicleWorkshop = None
from utils.audit_logger import log_audit

integrated_bp = Blueprint('integrated', __name__)

# ============ لوحة التحكم الرئيسية المتكاملة ============

@integrated_bp.route('/dashboard')
@login_required
def dashboard():
    """لوحة التحكم الشاملة للنظام المتكامل"""
    
    # الحصول على التاريخ الحالي
    today = date.today()
    current_month = today.month
    current_year = today.year
    
    # === إحصائيات الموظفين والأقسام ===
    total_employees = Employee.query.filter_by(status='active').count()
    total_departments = Department.query.count()
    
    # === إحصائيات السيارات ===
    total_vehicles = Vehicle.query.count()
    vehicles_available = Vehicle.query.filter_by(status='available').count()
    vehicles_rented = Vehicle.query.filter_by(status='rented').count()
    vehicles_in_workshop = Vehicle.query.filter_by(status='in_workshop').count()
    
    # === إحصائيات الحضور لهذا الشهر ===
    attendance_stats = db.session.query(
        Attendance.status,
        func.count(Attendance.id).label('count')
    ).filter(
        extract('month', Attendance.date) == current_month,
        extract('year', Attendance.date) == current_year
    ).group_by(Attendance.status).all()
    
    attendance_summary = {status: count for status, count in attendance_stats}
    
    # === إحصائيات الرواتب لهذا الشهر ===
    salaries_this_month = Salary.query.filter_by(
        month=current_month,
        year=current_year
    ).all()
    
    total_payroll = sum(salary.net_salary for salary in salaries_this_month)
    paid_salaries = len([s for s in salaries_this_month if s.is_paid])
    unpaid_salaries = len([s for s in salaries_this_month if not s.is_paid])
    
    # === إحصائيات السيارات المالية ===
    total_rental_cost = 0
    workshop_expenses = 0
    total_expenses = 0
    total_revenue = 0
    
    if VehicleRental:
        active_rentals = VehicleRental.query.filter_by(is_active=True).all()
        total_rental_cost = sum(rental.monthly_cost for rental in active_rentals)
    
    if VehicleWorkshop:
        # مصروفات الورش لهذا الشهر
        workshop_expenses = db.session.query(
            func.sum(VehicleWorkshop.cost).label('total')
        ).filter(
            extract('month', VehicleWorkshop.entry_date) == current_month,
            extract('year', VehicleWorkshop.entry_date) == current_year
        ).scalar() or 0
    
    if Account and AccountType:
        # === احصائيات محاسبية سريعة ===
        # إجمالي المصروفات لهذا الشهر
        expense_accounts = Account.query.filter_by(account_type=AccountType.EXPENSES).all()
        total_expenses = sum(account.balance or 0 for account in expense_accounts)
        
        # إجمالي الإيرادات لهذا الشهر
        revenue_accounts = Account.query.filter_by(account_type=AccountType.REVENUE).all()
        total_revenue = sum(account.balance or 0 for account in revenue_accounts)
    
    # === بيانات الرسوم البيانية ===
    # رسم بياني لحالة السيارات
    vehicle_status_data = {
        'available': vehicles_available,
        'rented': vehicles_rented,
        'in_workshop': vehicles_in_workshop,
        'other': total_vehicles - vehicles_available - vehicles_rented - vehicles_in_workshop
    }
    
    # رسم بياني للحضور في آخر 7 أيام
    last_7_days = []
    attendance_7_days = []
    
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        last_7_days.append(day.strftime('%d/%m'))
        
        daily_attendance = Attendance.query.filter(
            Attendance.date == day,
            Attendance.status == 'present'
        ).count()
        attendance_7_days.append(daily_attendance)
    
    # === قائمة بالمهام العاجلة ===
    urgent_tasks = []
    
    # وثائق السيارات المنتهية
    expired_vehicles = Vehicle.query.filter(
        or_(
            Vehicle.registration_expiry_date < today,
            Vehicle.inspection_expiry_date < today,
            Vehicle.authorization_expiry_date < today
        )
    ).count()
    
    if expired_vehicles > 0:
        urgent_tasks.append({
            'title': f'{expired_vehicles} سيارة لديها وثائق منتهية',
            'url': url_for('vehicles.index'),
            'type': 'danger'
        })
    
    # رواتب غير مدفوعة
    if unpaid_salaries > 0:
        urgent_tasks.append({
            'title': f'{unpaid_salaries} راتب لم يتم دفعه',
            'url': url_for('salaries.index'),
            'type': 'warning'
        })
    
    # سيارات في الورشة لأكثر من 7 أيام
    long_workshop_stays = VehicleWorkshop.query.filter(
        VehicleWorkshop.exit_date.is_(None),
        VehicleWorkshop.entry_date < (today - timedelta(days=7))
    ).count()
    
    if long_workshop_stays > 0:
        urgent_tasks.append({
            'title': f'{long_workshop_stays} سيارة في الورشة أكثر من أسبوع',
            'url': url_for('vehicles.index'),
            'type': 'info'
        })
    
    return render_template('integrated/dashboard_improved.html',
        # إحصائيات عامة
        total_employees=total_employees,
        total_departments=total_departments,
        total_vehicles=total_vehicles,
        
        # حالة السيارات
        vehicles_available=vehicles_available,
        vehicles_rented=vehicles_rented,
        vehicles_in_workshop=vehicles_in_workshop,
        vehicle_status_data=vehicle_status_data,
        
        # إحصائيات الحضور
        attendance_summary=attendance_summary,
        attendance_7_days=attendance_7_days,
        last_7_days=last_7_days,
        
        # إحصائيات الرواتب
        total_payroll=total_payroll,
        paid_salaries=paid_salaries,
        unpaid_salaries=unpaid_salaries,
        
        # إحصائيات مالية
        total_rental_cost=total_rental_cost,
        workshop_expenses=workshop_expenses,
        total_expenses=total_expenses,
        total_revenue=total_revenue,
        
        # مهام عاجلة
        urgent_tasks=urgent_tasks,
        
        # معلومات التاريخ
        current_month=current_month,
        current_year=current_year,
        today=today
    )

# ============ نظام الربط المحاسبي التلقائي ============

@integrated_bp.route('/auto-accounting')
@login_required
def auto_accounting():
    """صفحة إعداد الربط المحاسبي التلقائي"""
    
    # متغيرات افتراضية
    active_fiscal_year = None
    cost_centers = []
    salary_accounts = []
    vehicle_accounts = []
    bank_accounts = []
    
    # محاولة الحصول على البيانات المحاسبية إذا كانت متاحة
    if FiscalYear:
        active_fiscal_year = FiscalYear.query.filter_by(is_active=True).first()
    
    if CostCenter:
        cost_centers = CostCenter.query.filter_by(is_active=True).all()
    
    if Account and AccountType:
        # الحصول على الحسابات المحاسبية المهمة
        salary_accounts = Account.query.filter_by(
            account_type=AccountType.EXPENSES
        ).filter(
            Account.name.contains('راتب')
        ).all()
        
        vehicle_accounts = Account.query.filter_by(
            account_type=AccountType.EXPENSES
        ).filter(
            or_(
                Account.name.contains('سيارة'),
                Account.name.contains('مركبة'),
                Account.name.contains('صيانة')
            )
        ).all()
        
        bank_accounts = Account.query.filter_by(
            account_type=AccountType.ASSETS
        ).filter(
            or_(
                Account.name.contains('بنك'),
                Account.name.contains('نقدية')
            )
        ).all()
    
    return render_template('integrated/auto_accounting.html',
        active_fiscal_year=active_fiscal_year,
        cost_centers=cost_centers or [],
        salary_accounts=salary_accounts or [],
        vehicle_accounts=vehicle_accounts or [],
        bank_accounts=bank_accounts or [],
        current_month=datetime.now().month,
        current_year=datetime.now().year
    )

@integrated_bp.route('/process-monthly-accounting', methods=['POST'])
@login_required
def process_monthly_accounting():
    """معالجة القيود المحاسبية الشهرية تلقائياً"""
    
    try:
        month = int(request.form['month'])
        year = int(request.form['year'])
        
        # معالجة رواتب الموظفين
        salaries_processed = process_salary_entries(month, year)
        
        # معالجة مصروفات السيارات
        vehicle_expenses_processed = process_vehicle_expenses(month, year)
        
        # معالجة خصومات الورش
        workshop_adjustments_processed = process_workshop_adjustments(month, year)
        
        flash(f'تم معالجة القيود المحاسبية بنجاح: {salaries_processed + vehicle_expenses_processed + workshop_adjustments_processed} قيد', 'success')
        
        log_audit('create', 'monthly_accounting', 0, 
                 f'تم معالجة القيود المحاسبية لشهر {month}/{year}')
        
    except Exception as e:
        flash(f'حدث خطأ في معالجة القيود: {str(e)}', 'danger')
    
    return redirect(url_for('integrated.auto_accounting'))

def process_salary_entries(month, year):
    """معالجة قيود الرواتب"""
    processed_count = 0
    
    # الحصول على رواتب الشهر
    salaries = Salary.query.filter_by(month=month, year=year, is_paid=True).all()
    
    # الحصول على السنة المالية النشطة
    fiscal_year = FiscalYear.query.filter_by(is_active=True).first()
    if not fiscal_year:
        return 0
    
    # الحصول على الحسابات المطلوبة
    salary_expense_account = Account.query.filter(
        Account.account_type == AccountType.EXPENSES,
        Account.name.contains('راتب')
    ).first()
    
    bank_account = Account.query.filter(
        Account.account_type == AccountType.ASSETS,
        Account.name.contains('بنك')
    ).first()
    
    if not salary_expense_account or not bank_account:
        return 0
    
    for salary in salaries:
        # التحقق من عدم وجود قيد سابق لهذا الراتب
        existing_transaction = Transaction.query.filter(
            Transaction.reference_number.contains(f'salary_{salary.id}')
        ).first()
        
        if existing_transaction:
            continue
        
        # إنشاء قيد الراتب
        transaction = Transaction()
        transaction.fiscal_year_id = fiscal_year.id
        transaction.transaction_type = TransactionType.SALARY
        transaction.reference_number = f'salary_{salary.id}'
        transaction.description = f'راتب {salary.employee.name} - {month}/{year}'
        transaction.transaction_date = date.today()
        transaction.total_amount = salary.net_salary
        transaction.transaction_number = f'SAL-{salary.id}-{month}-{year}'
        transaction.created_by_id = current_user.id if current_user.is_authenticated else 1
        db.session.add(transaction)
        db.session.flush()
        
        # قيد مدين: مصروف الراتب
        debit_entry = TransactionEntry()
        debit_entry.transaction_id = transaction.id
        debit_entry.account_id = salary_expense_account.id
        debit_entry.entry_type = EntryType.DEBIT
        debit_entry.amount = salary.net_salary
        debit_entry.cost_center_id = get_employee_cost_center(salary.employee_id)
        db.session.add(debit_entry)
        
        # قيد دائن: البنك
        credit_entry = TransactionEntry()
        credit_entry.transaction_id = transaction.id
        credit_entry.account_id = bank_account.id
        credit_entry.entry_type = EntryType.CREDIT
        credit_entry.amount = salary.net_salary
        db.session.add(credit_entry)
        
        processed_count += 1
    
    db.session.commit()
    return processed_count

def process_vehicle_expenses(month, year):
    """معالجة مصروفات السيارات"""
    processed_count = 0
    
    # الحصول على السنة المالية النشطة
    fiscal_year = FiscalYear.query.filter_by(is_active=True).first()
    if not fiscal_year:
        return 0
    
    # الحصول على مصروفات الورش لهذا الشهر
    workshop_records = VehicleWorkshop.query.filter(
        extract('month', VehicleWorkshop.entry_date) == month,
        extract('year', VehicleWorkshop.entry_date) == year,
        VehicleWorkshop.cost > 0
    ).all()
    
    # الحصول على الحسابات المطلوبة
    vehicle_expense_account = Account.query.filter(
        Account.account_type == AccountType.EXPENSES,
        Account.name.contains('صيانة')
    ).first()
    
    bank_account = Account.query.filter(
        Account.account_type == AccountType.ASSETS,
        Account.name.contains('بنك')
    ).first()
    
    if not vehicle_expense_account or not bank_account:
        return 0
    
    for record in workshop_records:
        # التحقق من عدم وجود قيد سابق
        existing_transaction = Transaction.query.filter(
            Transaction.reference_number.contains(f'workshop_{record.id}')
        ).first()
        
        if existing_transaction:
            continue
        
        # إنشاء قيد مصروف الصيانة
        transaction = Transaction()
        transaction.fiscal_year_id = fiscal_year.id
        transaction.transaction_type = TransactionType.VEHICLE_EXPENSE
        transaction.reference_number = f'workshop_{record.id}'
        transaction.description = f'صيانة سيارة {record.vehicle.plate_number} - {record.workshop_name}'
        transaction.transaction_date = record.entry_date
        transaction.total_amount = record.cost
        transaction.transaction_number = f'VEH-{record.id}-{record.entry_date.strftime("%Y%m%d")}'
        transaction.created_by_id = current_user.id if current_user.is_authenticated else 1
        db.session.add(transaction)
        db.session.flush()
        
        # قيد مدين: مصروف صيانة السيارات
        debit_entry = TransactionEntry()
        debit_entry.transaction_id = transaction.id
        debit_entry.account_id = vehicle_expense_account.id
        debit_entry.entry_type = EntryType.DEBIT
        debit_entry.amount = record.cost
        debit_entry.cost_center_id = get_vehicle_cost_center()
        db.session.add(debit_entry)
        
        # قيد دائن: البنك
        credit_entry = TransactionEntry()
        credit_entry.transaction_id = transaction.id
        credit_entry.account_id = bank_account.id
        credit_entry.entry_type = EntryType.CREDIT
        credit_entry.amount = record.cost
        db.session.add(credit_entry)
        
        processed_count += 1
    
    db.session.commit()
    return processed_count

def process_workshop_adjustments(month, year):
    """معالجة خصومات إيجار الورش"""
    processed_count = 0
    
    # الحصول على السيارات المؤجرة
    rented_vehicles = Vehicle.query.join(VehicleRental).filter(
        VehicleRental.is_active == True
    ).all()
    
    # الحصول على السنة المالية النشطة
    fiscal_year = FiscalYear.query.filter_by(is_active=True).first()
    if not fiscal_year:
        return 0
    
    # الحصول على الحسابات المطلوبة
    rental_expense_account = Account.query.filter(
        Account.account_type == AccountType.EXPENSES,
        Account.name.contains('إيجار')
    ).first()
    
    rental_discount_account = Account.query.filter(
        Account.account_type == AccountType.REVENUE,
        Account.name.contains('خصم')
    ).first()
    
    if not rental_expense_account or not rental_discount_account:
        return 0
    
    for vehicle in rented_vehicles:
        # حساب خصم الورشة لهذا الشهر
        adjustment = calculate_rental_adjustment(vehicle.id, year, month)
        
        if adjustment > 0:
            # التحقق من عدم وجود قيد سابق
            existing_transaction = Transaction.query.filter(
                Transaction.reference_number.contains(f'rental_adjustment_{vehicle.id}_{month}_{year}')
            ).first()
            
            if existing_transaction:
                continue
            
            # إنشاء قيد خصم الإيجار
            transaction = Transaction()
            transaction.fiscal_year_id = fiscal_year.id
            transaction.transaction_type = TransactionType.MANUAL
            transaction.reference_number = f'rental_adjustment_{vehicle.id}_{month}_{year}'
            transaction.description = f'خصم إيجار ورشة - سيارة {vehicle.plate_number}'
            transaction.transaction_date = date.today()
            transaction.total_amount = adjustment
            transaction.transaction_number = f'ADJ-{vehicle.id}-{month}-{year}'
            transaction.created_by_id = current_user.id if current_user.is_authenticated else 1
            db.session.add(transaction)
            db.session.flush()
            
            # قيد مدين: خصومات الإيجار (إيراد)
            debit_entry = TransactionEntry()
            debit_entry.transaction_id = transaction.id
            debit_entry.account_id = rental_discount_account.id
            debit_entry.entry_type = EntryType.DEBIT
            debit_entry.amount = adjustment
            debit_entry.cost_center_id = get_vehicle_cost_center()
            db.session.add(debit_entry)
            
            # قيد دائن: مصروف الإيجار (تقليل المصروف)
            credit_entry = TransactionEntry()
            credit_entry.transaction_id = transaction.id
            credit_entry.account_id = rental_expense_account.id
            credit_entry.entry_type = EntryType.CREDIT
            credit_entry.amount = adjustment
            db.session.add(credit_entry)
            
            processed_count += 1
    
    db.session.commit()
    return processed_count

def calculate_rental_adjustment(vehicle_id, year, month):
    """حساب خصم الإيجار بناءً على أيام الورشة"""
    try:
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
    except Exception as e:
        print(f"Error calculating rental adjustment: {e}")
        return 0

def get_employee_cost_center(employee_id):
    """الحصول على مركز تكلفة الموظف"""
    employee = Employee.query.get(employee_id)
    if employee and employee.departments:
        # ربط القسم بمركز التكلفة (يمكن تحسينه لاحقاً)
        cost_center = CostCenter.query.filter(
            CostCenter.name.contains(employee.departments[0].name)
        ).first()
        return cost_center.id if cost_center else None
    return None

def get_vehicle_cost_center():
    """الحصول على مركز تكلفة السيارات"""
    vehicle_cost_center = CostCenter.query.filter(
        or_(
            CostCenter.name.contains('سيارة'),
            CostCenter.name.contains('مركبة'),
            CostCenter.code.contains('VEH')
        )
    ).first()
    return vehicle_cost_center.id if vehicle_cost_center else None

# ============ تقارير شاملة ============

@integrated_bp.route('/comprehensive-report')
@login_required
def comprehensive_report():
    """تقرير شامل يجمع كل أنظمة الإدارة"""
    
    month = request.args.get('month', datetime.now().month, type=int)
    year = request.args.get('year', datetime.now().year, type=int)
    
    # === بيانات الموظفين والحضور ===
    employees_data = []
    employees = Employee.query.filter_by(status='active').all()
    
    for employee in employees:
        # حضور الموظف لهذا الشهر
        attendance_records = Attendance.query.filter(
            Attendance.employee_id == employee.id,
            extract('month', Attendance.date) == month,
            extract('year', Attendance.date) == year
        ).all()
        
        present_days = len([a for a in attendance_records if a.status == 'present'])
        absent_days = len([a for a in attendance_records if a.status == 'absent'])
        
        # راتب الموظف لهذا الشهر
        salary = Salary.query.filter_by(
            employee_id=employee.id,
            month=month,
            year=year
        ).first()
        
        employees_data.append({
            'employee': employee,
            'present_days': present_days,
            'absent_days': absent_days,
            'salary': salary
        })
    
    # === بيانات السيارات ===
    vehicles_data = []
    vehicles = Vehicle.query.all()
    
    for vehicle in vehicles:
        # إيجار السيارة
        rental = VehicleRental.query.filter_by(
            vehicle_id=vehicle.id,
            is_active=True
        ).first()
        
        # أيام الورشة هذا الشهر
        workshop_days = 0
        workshop_records = VehicleWorkshop.query.filter(
            VehicleWorkshop.vehicle_id == vehicle.id,
            extract('month', VehicleWorkshop.entry_date) == month,
            extract('year', VehicleWorkshop.entry_date) == year
        ).all()
        
        for record in workshop_records:
            if record.exit_date:
                workshop_days += (record.exit_date - record.entry_date).days
            else:
                # لا تزال في الورشة
                workshop_days += (date.today() - record.entry_date).days
        
        # حساب خصم الإيجار
        rental_adjustment = 0
        if rental:
            daily_rent = rental.monthly_cost / 30
            rental_adjustment = daily_rent * workshop_days
        
        vehicles_data.append({
            'vehicle': vehicle,
            'rental': rental,
            'workshop_days': workshop_days,
            'rental_adjustment': rental_adjustment
        })
    
    # === الملخص المالي ===
    total_salaries = sum(emp['salary'].net_salary if emp['salary'] else 0 for emp in employees_data)
    total_rental_cost = sum(v['rental'].monthly_cost if v['rental'] else 0 for v in vehicles_data)
    total_rental_adjustments = sum(v['rental_adjustment'] for v in vehicles_data)
    net_rental_cost = total_rental_cost - total_rental_adjustments
    
    # مصروفات الورش
    workshop_expenses = db.session.query(
        func.sum(VehicleWorkshop.cost).label('total')
    ).filter(
        extract('month', VehicleWorkshop.entry_date) == month,
        extract('year', VehicleWorkshop.entry_date) == year
    ).scalar() or 0
    
    return render_template('integrated/comprehensive_report.html',
        employees_data=employees_data,
        vehicles_data=vehicles_data,
        month=month,
        year=year,
        total_salaries=total_salaries,
        total_rental_cost=total_rental_cost,
        total_rental_adjustments=total_rental_adjustments,
        net_rental_cost=net_rental_cost,
        workshop_expenses=workshop_expenses,
        total_expenses=total_salaries + net_rental_cost + workshop_expenses
    )

# ============ واجهة برمجة التطبيقات للنظام المتكامل ============

@integrated_bp.route('/api/dashboard-stats')
@login_required
def dashboard_stats_api():
    """API لإحصائيات لوحة التحكم"""
    
    today = date.today()
    current_month = today.month
    current_year = today.year
    
    stats = {
        'employees': {
            'total': Employee.query.filter_by(status='active').count(),
            'present_today': Attendance.query.filter(
                Attendance.date == today,
                Attendance.status == 'present'
            ).count()
        },
        'vehicles': {
            'total': Vehicle.query.count(),
            'available': Vehicle.query.filter_by(status='available').count(),
            'rented': Vehicle.query.filter_by(status='rented').count(),
            'in_workshop': Vehicle.query.filter_by(status='in_workshop').count()
        },
        'financial': {
            'monthly_payroll': sum(s.net_salary for s in Salary.query.filter_by(
                month=current_month, year=current_year
            ).all()),
            'monthly_rentals': sum(r.monthly_cost for r in VehicleRental.query.filter_by(
                is_active=True
            ).all()),
            'workshop_expenses': db.session.query(
                func.sum(VehicleWorkshop.cost).label('total')
            ).filter(
                extract('month', VehicleWorkshop.entry_date) == current_month,
                extract('year', VehicleWorkshop.entry_date) == current_year
            ).scalar() or 0
        }
    }
    
    return jsonify(stats)

@integrated_bp.route('/export-comprehensive-excel')
@login_required
def export_comprehensive_excel():
    """تصدير التقرير الشامل إلى Excel"""
    
    month = request.args.get('month', datetime.now().month, type=int)
    year = request.args.get('year', datetime.now().year, type=int)
    
    # إعداد ملف Excel
    output = io.BytesIO()
    
    if pd:
        try:
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                # ورقة الموظفين والحضور
                employees_data = []
                employees = Employee.query.filter_by(status='active').all()
                
                for employee in employees:
                    attendance_count = Attendance.query.filter(
                        Attendance.employee_id == employee.id,
                        extract('month', Attendance.date) == month,
                        extract('year', Attendance.date) == year,
                        Attendance.status == 'present'
                    ).count()
                    
                    salary = Salary.query.filter_by(
                        employee_id=employee.id,
                        month=month,
                        year=year
                    ).first()
                    
                    employees_data.append({
                        'الرقم الوظيفي': employee.employee_number,
                        'الاسم': employee.name,
                        'القسم': employee.departments[0].name if employee.departments else '',
                        'أيام الحضور': attendance_count,
                        'الراتب الأساسي': salary.basic_salary if salary else 0,
                        'البدلات': salary.allowances if salary else 0,
                        'الخصومات': salary.deductions if salary else 0,
                        'صافي الراتب': salary.net_salary if salary else 0
                    })
                
                df_employees = pd.DataFrame(employees_data)
                df_employees.to_excel(writer, sheet_name='الموظفين والرواتب', index=False)
                
                # ورقة السيارات والإيجارات
                vehicles_data = []
                vehicles = Vehicle.query.all()
                
                for vehicle in vehicles:
                    rental = VehicleRental.query.filter_by(
                        vehicle_id=vehicle.id,
                        is_active=True
                    ).first()
                    
                    vehicles_data.append({
                        'رقم اللوحة': vehicle.plate_number,
                        'الماركة': vehicle.make,
                        'الموديل': vehicle.model,
                        'الحالة': vehicle.status,
                        'الإيجار الشهري': rental.monthly_cost if rental else 0,
                        'المؤجر': rental.lessor_name if rental else ''
                    })
                
                df_vehicles = pd.DataFrame(vehicles_data)
                df_vehicles.to_excel(writer, sheet_name='السيارات والإيجارات', index=False)
            
            output.seek(0)
            
            filename = f"تقرير_شامل_{month}_{year}.xlsx"
            
            return send_file(
                output,
                download_name=filename,
                as_attachment=True,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        except Exception as e:
            flash(f'خطأ في تصدير Excel: {str(e)}', 'danger')
            return redirect(url_for('integrated.comprehensive_report'))
    else:
        flash('مكتبة pandas غير متاحة لتصدير Excel', 'warning')
        return redirect(url_for('integrated.comprehensive_report'))