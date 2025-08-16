"""
خدمات النظام المحاسبي
"""
from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy import func, and_, or_
from app import db
from models_accounting import *
from models import Employee, Vehicle


class AccountingService:
    """خدمات النظام المحاسبي"""
    
    @staticmethod
    def initialize_chart_of_accounts():
        """إنشاء دليل الحسابات الأساسي"""
        try:
            # التحقق من وجود حسابات
            if Account.query.count() > 0:
                return True, "دليل الحسابات موجود مسبقاً"
            
            # الحسابات الأساسية
            base_accounts = [
                # الأصول (1xxx)
                {'code': '1000', 'name': 'الأصول', 'type': AccountType.ASSETS, 'parent': None},
                {'code': '1001', 'name': 'النقدية في الصندوق', 'type': AccountType.ASSETS, 'parent': '1000'},
                {'code': '1002', 'name': 'البنك - الراجحي', 'type': AccountType.ASSETS, 'parent': '1000'},
                {'code': '1003', 'name': 'البنك - الأهلي', 'type': AccountType.ASSETS, 'parent': '1000'},
                {'code': '1100', 'name': 'العملاء', 'type': AccountType.ASSETS, 'parent': '1000'},
                {'code': '1200', 'name': 'المخزون', 'type': AccountType.ASSETS, 'parent': '1000'},
                {'code': '1300', 'name': 'الأصول الثابتة', 'type': AccountType.ASSETS, 'parent': '1000'},
                {'code': '1301', 'name': 'المركبات', 'type': AccountType.ASSETS, 'parent': '1300'},
                {'code': '1302', 'name': 'الأثاث والتجهيزات', 'type': AccountType.ASSETS, 'parent': '1300'},
                {'code': '1303', 'name': 'الحاسب الآلي', 'type': AccountType.ASSETS, 'parent': '1300'},
                
                # الخصوم (2xxx)
                {'code': '2000', 'name': 'الخصوم', 'type': AccountType.LIABILITIES, 'parent': None},
                {'code': '2001', 'name': 'الموردون', 'type': AccountType.LIABILITIES, 'parent': '2000'},
                {'code': '2100', 'name': 'الرواتب المستحقة', 'type': AccountType.LIABILITIES, 'parent': '2000'},
                {'code': '2200', 'name': 'الضرائب المستحقة', 'type': AccountType.LIABILITIES, 'parent': '2000'},
                {'code': '2300', 'name': 'القروض طويلة الأجل', 'type': AccountType.LIABILITIES, 'parent': '2000'},
                
                # حقوق الملكية (3xxx)
                {'code': '3000', 'name': 'حقوق الملكية', 'type': AccountType.EQUITY, 'parent': None},
                {'code': '3001', 'name': 'رأس المال', 'type': AccountType.EQUITY, 'parent': '3000'},
                {'code': '3002', 'name': 'الأرباح المحتجزة', 'type': AccountType.EQUITY, 'parent': '3000'},
                
                # الإيرادات (4xxx)
                {'code': '4000', 'name': 'الإيرادات', 'type': AccountType.REVENUE, 'parent': None},
                {'code': '4001', 'name': 'إيرادات الخدمات', 'type': AccountType.REVENUE, 'parent': '4000'},
                {'code': '4002', 'name': 'إيرادات أخرى', 'type': AccountType.REVENUE, 'parent': '4000'},
                
                # المصروفات (5xxx)
                {'code': '5000', 'name': 'المصروفات', 'type': AccountType.EXPENSES, 'parent': None},
                {'code': '5001', 'name': 'مصروف الرواتب', 'type': AccountType.EXPENSES, 'parent': '5000'},
                {'code': '5002', 'name': 'مصروف البدلات', 'type': AccountType.EXPENSES, 'parent': '5000'},
                {'code': '5100', 'name': 'مصروفات المركبات', 'type': AccountType.EXPENSES, 'parent': '5000'},
                {'code': '5101', 'name': 'مصروف الوقود', 'type': AccountType.EXPENSES, 'parent': '5100'},
                {'code': '5102', 'name': 'مصروف الصيانة', 'type': AccountType.EXPENSES, 'parent': '5100'},
                {'code': '5103', 'name': 'مصروف التأمين', 'type': AccountType.EXPENSES, 'parent': '5100'},
                {'code': '5104', 'name': 'مصروف التسجيل', 'type': AccountType.EXPENSES, 'parent': '5100'},
                {'code': '5105', 'name': 'المخالفات', 'type': AccountType.EXPENSES, 'parent': '5100'},
                {'code': '5199', 'name': 'مصروفات مركبات أخرى', 'type': AccountType.EXPENSES, 'parent': '5100'},
                {'code': '5200', 'name': 'المصروفات الإدارية', 'type': AccountType.EXPENSES, 'parent': '5000'},
                {'code': '5201', 'name': 'مصروف الإيجار', 'type': AccountType.EXPENSES, 'parent': '5200'},
                {'code': '5202', 'name': 'مصروف الكهرباء', 'type': AccountType.EXPENSES, 'parent': '5200'},
                {'code': '5203', 'name': 'مصروف الاتصالات', 'type': AccountType.EXPENSES, 'parent': '5200'},
                {'code': '5204', 'name': 'مصروف القرطاسية', 'type': AccountType.EXPENSES, 'parent': '5200'},
                {'code': '5299', 'name': 'مصروفات إدارية أخرى', 'type': AccountType.EXPENSES, 'parent': '5200'},
            ]
            
            # إنشاء الحسابات
            account_map = {}
            for acc_data in base_accounts:
                parent_id = None
                if acc_data['parent']:
                    parent_id = account_map.get(acc_data['parent'])
                
                account = Account(
                    code=acc_data['code'],
                    name=acc_data['name'],
                    account_type=acc_data['type'],
                    parent_id=parent_id,
                    level=1 if parent_id else 0,
                    is_active=True
                )
                
                db.session.add(account)
                db.session.flush()
                account_map[acc_data['code']] = account.id
            
            db.session.commit()
            return True, "تم إنشاء دليل الحسابات بنجاح"
            
        except Exception as e:
            db.session.rollback()
            return False, f"خطأ في إنشاء دليل الحسابات: {str(e)}"
    
    @staticmethod
    def create_fiscal_year(year, name=None):
        """إنشاء سنة مالية جديدة"""
        try:
            if not name:
                name = f"السنة المالية {year}"
            
            # التحقق من عدم وجود سنة مالية مشابهة
            existing = FiscalYear.query.filter(
                func.extract('year', FiscalYear.start_date) == year
            ).first()
            
            if existing:
                return False, f"السنة المالية {year} موجودة مسبقاً"
            
            # إلغاء تفعيل السنوات السابقة
            FiscalYear.query.update({'is_active': False})
            
            fiscal_year = FiscalYear(
                name=name,
                start_date=date(year, 1, 1),
                end_date=date(year, 12, 31),
                is_active=True,
                is_closed=False
            )
            
            db.session.add(fiscal_year)
            db.session.commit()
            
            return True, f"تم إنشاء السنة المالية {year} بنجاح"
            
        except Exception as e:
            db.session.rollback()
            return False, f"خطأ في إنشاء السنة المالية: {str(e)}"
    
    @staticmethod
    def create_cost_centers():
        """إنشاء مراكز التكلفة من الأقسام الموجودة"""
        try:
            from models import Department
            
            departments = Department.query.all()
            created_count = 0
            
            for dept in departments:
                # التحقق من عدم وجود مركز تكلفة لهذا القسم
                existing = CostCenter.query.filter_by(name=dept.name).first()
                if existing:
                    continue
                
                cost_center = CostCenter(
                    code=f"CC{dept.id:03d}",
                    name=dept.name,
                    description=f"مركز تكلفة قسم {dept.name}",
                    is_active=True
                )
                
                db.session.add(cost_center)
                created_count += 1
            
            db.session.commit()
            return True, f"تم إنشاء {created_count} مركز تكلفة"
            
        except Exception as e:
            db.session.rollback()
            return False, f"خطأ في إنشاء مراكز التكلفة: {str(e)}"
    
    @staticmethod
    def auto_create_salary_entries(month, year, department_id=None):
        """إنشاء قيود الرواتب تلقائياً"""
        try:
            # التحقق من وجود معالجة سابقة
            existing = Transaction.query.filter(
                Transaction.transaction_type == TransactionType.SALARY,
                func.extract('month', Transaction.transaction_date) == month,
                func.extract('year', Transaction.transaction_date) == year
            ).first()
            
            if existing:
                return False, f"تم معالجة رواتب شهر {month}/{year} مسبقاً"
            
            # الحصول على الموظفين
            query = Employee.query.filter_by(status='نشط')
            if department_id:
                query = query.join(Employee.departments).filter(Department.id == department_id)
            
            employees = query.all()
            
            if not employees:
                return False, "لا يوجد موظفين للمعالجة"
            
            # الحسابات المطلوبة
            salary_account = Account.query.filter_by(code='5001').first()
            cash_account = Account.query.filter_by(code='1001').first()
            
            if not salary_account or not cash_account:
                return False, "الحسابات المحاسبية للرواتب غير موجودة"
            
            # الإعدادات
            settings = AccountingSettings.query.first()
            if not settings:
                settings = AccountingSettings(
                    company_name='شركة نُظم',
                    next_transaction_number=1
                )
                db.session.add(settings)
                db.session.flush()
            
            fiscal_year = FiscalYear.query.filter_by(is_active=True).first()
            
            total_processed = 0
            total_amount = Decimal('0')
            
            for employee in employees:
                if not employee.salary or employee.salary <= 0:
                    continue
                
                net_salary = Decimal(str(employee.salary))
                if employee.allowances:
                    net_salary += Decimal(str(employee.allowances))
                if employee.deductions:
                    net_salary -= Decimal(str(employee.deductions))
                
                if net_salary <= 0:
                    continue
                
                # إنشاء معاملة الراتب
                transaction_number = f"{settings.transaction_prefix}{settings.next_transaction_number:06d}"
                
                transaction = Transaction(
                    transaction_number=transaction_number,
                    transaction_date=date(year, month, 1),
                    transaction_type=TransactionType.SALARY,
                    description=f"راتب شهر {month}/{year} - {employee.name}",
                    total_amount=net_salary,
                    fiscal_year_id=fiscal_year.id,
                    employee_id=employee.id,
                    created_by_id=1,  # النظام
                    is_approved=True,
                    approval_date=datetime.utcnow()
                )
                
                db.session.add(transaction)
                db.session.flush()
                
                # القيود
                debit_entry = TransactionEntry(
                    transaction_id=transaction.id,
                    account_id=salary_account.id,
                    entry_type=EntryType.DEBIT,
                    amount=net_salary,
                    description=f"راتب {employee.name}"
                )
                
                credit_entry = TransactionEntry(
                    transaction_id=transaction.id,
                    account_id=cash_account.id,
                    entry_type=EntryType.CREDIT,
                    amount=net_salary,
                    description=f"صرف راتب {employee.name}"
                )
                
                db.session.add(debit_entry)
                db.session.add(credit_entry)
                
                # تحديث الأرصدة
                salary_account.balance += net_salary
                cash_account.balance -= net_salary
                
                total_processed += 1
                total_amount += net_salary
                settings.next_transaction_number += 1
            
            db.session.commit()
            return True, f"تم معالجة {total_processed} راتب بإجمالي {total_amount:,.2f} ريال"
            
        except Exception as e:
            db.session.rollback()
            return False, f"خطأ في معالجة الرواتب: {str(e)}"
    
    @staticmethod
    def calculate_account_balance(account_id, as_of_date=None):
        """حساب رصيد حساب معين"""
        try:
            if not as_of_date:
                as_of_date = date.today()
            
            account = Account.query.get(account_id)
            if not account:
                return Decimal('0')
            
            # جمع المدين والدائن
            debits = db.session.query(func.sum(TransactionEntry.amount)).join(Transaction).filter(
                TransactionEntry.account_id == account_id,
                TransactionEntry.entry_type == EntryType.DEBIT,
                Transaction.transaction_date <= as_of_date,
                Transaction.is_approved == True
            ).scalar() or Decimal('0')
            
            credits = db.session.query(func.sum(TransactionEntry.amount)).join(Transaction).filter(
                TransactionEntry.account_id == account_id,
                TransactionEntry.entry_type == EntryType.CREDIT,
                Transaction.transaction_date <= as_of_date,
                Transaction.is_approved == True
            ).scalar() or Decimal('0')
            
            # حساب الرصيد حسب نوع الحساب
            if account.account_type in [AccountType.ASSETS, AccountType.EXPENSES]:
                balance = debits - credits
            else:
                balance = credits - debits
            
            return balance
            
        except Exception as e:
            return Decimal('0')
    
    @staticmethod
    def get_financial_summary(as_of_date=None):
        """الحصول على الملخص المالي"""
        try:
            if not as_of_date:
                as_of_date = date.today()
            
            # إجمالي الأصول
            total_assets = db.session.query(func.sum(Account.balance)).filter(
                Account.account_type == AccountType.ASSETS,
                Account.is_active == True
            ).scalar() or Decimal('0')
            
            # إجمالي الخصوم
            total_liabilities = db.session.query(func.sum(Account.balance)).filter(
                Account.account_type == AccountType.LIABILITIES,
                Account.is_active == True
            ).scalar() or Decimal('0')
            
            # إجمالي الإيرادات
            total_revenue = db.session.query(func.sum(Account.balance)).filter(
                Account.account_type == AccountType.REVENUE,
                Account.is_active == True
            ).scalar() or Decimal('0')
            
            # إجمالي المصروفات
            total_expenses = db.session.query(func.sum(Account.balance)).filter(
                Account.account_type == AccountType.EXPENSES,
                Account.is_active == True
            ).scalar() or Decimal('0')
            
            # صافي الدخل
            net_income = total_revenue - total_expenses
            
            return {
                'total_assets': total_assets,
                'total_liabilities': total_liabilities,
                'total_revenue': total_revenue,
                'total_expenses': total_expenses,
                'net_income': net_income,
                'equity': total_assets - total_liabilities
            }
            
        except Exception as e:
            return None
    
    @staticmethod
    def update_account_balances():
        """تحديث أرصدة جميع الحسابات"""
        try:
            accounts = Account.query.filter_by(is_active=True).all()
            
            for account in accounts:
                balance = AccountingService.calculate_account_balance(account.id)
                account.balance = balance
                account.updated_at = datetime.utcnow()
            
            db.session.commit()
            return True, "تم تحديث الأرصدة بنجاح"
            
        except Exception as e:
            db.session.rollback()
            return False, f"خطأ في تحديث الأرصدة: {str(e)}"