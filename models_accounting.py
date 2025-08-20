"""
نماذج قاعدة البيانات لنظام المحاسبة
"""
from app import db
from datetime import datetime
from sqlalchemy import Enum
from enum import Enum as PyEnum


class AccountType(PyEnum):
    """أنواع الحسابات المحاسبية"""
    ASSETS = "assets"  # أصول
    LIABILITIES = "liabilities"  # خصوم
    EQUITY = "equity"  # حقوق الملكية
    REVENUE = "revenue"  # إيرادات
    EXPENSES = "expenses"  # مصروفات


class TransactionType(PyEnum):
    """أنواع المعاملات المحاسبية"""
    JOURNAL = "JOURNAL"  # قيد يومية
    MANUAL = "MANUAL"  # قيد يدوي
    SALARY = "SALARY"  # راتب
    VEHICLE_EXPENSE = "VEHICLE_EXPENSE"  # مصروف مركبة
    DEPRECIATION = "DEPRECIATION"  # استهلاك
    PAYMENT = "PAYMENT"  # دفع
    RECEIPT = "RECEIPT"  # قبض



class PaymentMethod(PyEnum):
    """طرق الدفع"""
    CASH = "cash"  # نقدي
    BANK_TRANSFER = "bank_transfer"  # تحويل بنكي
    CHECK = "check"  # شيك
    CREDIT_CARD = "credit_card"  # بطاقة ائتمان


class EntryType(PyEnum):
    """نوع القيد"""
    DEBIT = "debit"  # مدين
    CREDIT = "credit"  # دائن


# جداول قاعدة البيانات المحاسبية

class FiscalYear(db.Model):
    """السنوات المالية"""
    __tablename__ = 'fiscal_years'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # مثل: السنة المالية 2025
    year = db.Column(db.Integer, nullable=False)  # سنة الميلاد
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_closed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    transactions = db.relationship('Transaction', backref='fiscal_year', lazy=True)
    budgets = db.relationship('Budget', backref='fiscal_year', lazy=True)


class Account(db.Model):
    """دليل الحسابات"""
    __tablename__ = 'accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)  # رمز الحساب
    name = db.Column(db.String(200), nullable=False)  # اسم الحساب
    name_en = db.Column(db.String(200))  # الاسم بالإنجليزية
    account_type = db.Column(Enum(AccountType), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))  # الحساب الأب
    level = db.Column(db.Integer, default=0)  # مستوى الحساب في الهيكل
    is_active = db.Column(db.Boolean, default=True)
    balance = db.Column(db.Numeric(15, 2), default=0)  # الرصيد الحالي
    description = db.Column(db.Text)  # وصف الحساب
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    parent = db.relationship('Account', remote_side=[id], backref='children')
    transaction_entries = db.relationship('TransactionEntry', backref='account', lazy=True)
    budgets = db.relationship('Budget', backref='account', lazy=True)


class CostCenter(db.Model):
    """مراكز التكلفة"""
    __tablename__ = 'cost_centers'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)  # رمز المركز
    name = db.Column(db.String(200), nullable=False)  # اسم المركز
    name_en = db.Column(db.String(200))  # الاسم بالإنجليزية
    description = db.Column(db.Text)  # وصف المركز
    parent_id = db.Column(db.Integer, db.ForeignKey('cost_centers.id'))  # مركز التكلفة الأب
    # manager_id = db.Column(db.Integer, db.ForeignKey('employees.id'))  # مسؤول المركز - سيتم إضافته لاحقاً
    budget_amount = db.Column(db.Numeric(15, 2), default=0)  # الميزانية المخصصة
    is_active = db.Column(db.Boolean, default=True)  # نشط
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    parent = db.relationship('CostCenter', remote_side=[id], backref='children')
    # manager = db.relationship('Employee', backref='managed_cost_centers')  # commented until Employee model is available
    
    def __repr__(self):
        return f'<CostCenter {self.code}: {self.name}>'
    
    @property 
    def full_name(self):
        """الاسم الكامل مع اسم المركز الأب"""
        if self.parent:
            return f"{self.parent.name} - {self.name}"
        return self.name
    
    @property
    def level(self):
        """مستوى المركز في الهيكل الهرمي"""
        if self.parent:
            return self.parent.level + 1
        return 0
    
    def get_total_budget(self):
        """إجمالي الميزانية شاملة المراكز الفرعية"""
        total = self.budget_amount or 0
        # إصلاح: استخدام relationship صحيح للحصول على المراكز الفرعية
        child_centers = CostCenter.query.filter_by(parent_id=self.id).all()
        for child in child_centers:
            total += child.get_total_budget()
        return total
    
    def get_actual_expenses(self):
        """إجمالي المصروفات الفعلية لهذا المركز"""
        entries = TransactionEntry.query.filter_by(cost_center_id=self.id).all()
        return sum(entry.amount for entry in entries if entry.entry_type == EntryType.DEBIT)
    transactions = db.relationship('Transaction', backref='cost_center', lazy=True)
    budgets = db.relationship('Budget', backref='cost_center', lazy=True)


class Vendor(db.Model):
    """الموردين"""
    __tablename__ = 'vendors'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    commercial_register = db.Column(db.String(50))  # السجل التجاري
    tax_number = db.Column(db.String(50))  # الرقم الضريبي
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    address = db.Column(db.Text)
    contact_person = db.Column(db.String(100))  # الشخص المسؤول
    payment_terms = db.Column(db.String(100))  # شروط الدفع
    credit_limit = db.Column(db.Numeric(15, 2), default=0)  # حد الائتمان
    current_balance = db.Column(db.Numeric(15, 2), default=0)  # الرصيد الحالي
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    transactions = db.relationship('Transaction', backref='vendor', lazy=True)


class Customer(db.Model):
    """العملاء"""
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    commercial_register = db.Column(db.String(50))
    tax_number = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    address = db.Column(db.Text)
    contact_person = db.Column(db.String(100))
    credit_limit = db.Column(db.Numeric(15, 2), default=0)
    current_balance = db.Column(db.Numeric(15, 2), default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    transactions = db.relationship('Transaction', backref='customer', lazy=True)


class Transaction(db.Model):
    """المعاملات المحاسبية (القيود)"""
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_number = db.Column(db.String(50), unique=True, nullable=False)  # رقم القيد
    transaction_date = db.Column(db.Date, nullable=False)
    transaction_type = db.Column(Enum(TransactionType), nullable=False)
    reference_number = db.Column(db.String(100))  # رقم المرجع (فاتورة، سند، إلخ)
    description = db.Column(db.Text, nullable=False)  # وصف المعاملة
    total_amount = db.Column(db.Numeric(15, 2), nullable=False)  # إجمالي المبلغ
    
    # المراجع الخارجية
    fiscal_year_id = db.Column(db.Integer, db.ForeignKey('fiscal_years.id'), nullable=False)
    cost_center_id = db.Column(db.Integer, db.ForeignKey('cost_centers.id'))
    vendor_id = db.Column(db.Integer, db.ForeignKey('vendors.id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))  # للرواتب
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'))  # لمصروفات المركبات
    
    # معلومات التدقيق
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    approved_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_approved = db.Column(db.Boolean, default=False)
    approval_date = db.Column(db.DateTime)
    is_posted = db.Column(db.Boolean, default=False)  # تم الترحيل
    posted_date = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    entries = db.relationship('TransactionEntry', backref='transaction', lazy=True, cascade='all, delete-orphan')
    created_by = db.relationship('User', foreign_keys=[created_by_id], backref='created_transactions')
    approved_by = db.relationship('User', foreign_keys=[approved_by_id], backref='approved_transactions')
    employee = db.relationship('Employee', backref='salary_transactions')
    vehicle = db.relationship('Vehicle', backref='expense_transactions')


class TransactionEntry(db.Model):
    """تفاصيل القيود المحاسبية"""
    __tablename__ = 'transaction_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.Integer, db.ForeignKey('transactions.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    cost_center_id = db.Column(db.Integer, db.ForeignKey('cost_centers.id'))  # مركز التكلفة اختياري
    entry_type = db.Column(Enum(EntryType), nullable=False)  # مدين أو دائن
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    description = db.Column(db.Text)  # وصف إضافي للقيد
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقة مع مركز التكلفة
    cost_center = db.relationship('CostCenter', backref='transaction_entries')


class Budget(db.Model):
    """الموازنات"""
    __tablename__ = 'budgets'
    
    id = db.Column(db.Integer, primary_key=True)
    fiscal_year_id = db.Column(db.Integer, db.ForeignKey('fiscal_years.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    cost_center_id = db.Column(db.Integer, db.ForeignKey('cost_centers.id'))
    
    # المبالغ المخططة شهرياً
    jan_amount = db.Column(db.Numeric(15, 2), default=0)
    feb_amount = db.Column(db.Numeric(15, 2), default=0)
    mar_amount = db.Column(db.Numeric(15, 2), default=0)
    apr_amount = db.Column(db.Numeric(15, 2), default=0)
    may_amount = db.Column(db.Numeric(15, 2), default=0)
    jun_amount = db.Column(db.Numeric(15, 2), default=0)
    jul_amount = db.Column(db.Numeric(15, 2), default=0)
    aug_amount = db.Column(db.Numeric(15, 2), default=0)
    sep_amount = db.Column(db.Numeric(15, 2), default=0)
    oct_amount = db.Column(db.Numeric(15, 2), default=0)
    nov_amount = db.Column(db.Numeric(15, 2), default=0)
    dec_amount = db.Column(db.Numeric(15, 2), default=0)
    
    total_budget = db.Column(db.Numeric(15, 2), nullable=False)  # إجمالي الموازنة
    actual_amount = db.Column(db.Numeric(15, 2), default=0)  # المبلغ الفعلي المنصرف
    
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # العلاقات
    created_by = db.relationship('User', backref='created_budgets')


class AccountingSettings(db.Model):
    """إعدادات النظام المحاسبي"""
    __tablename__ = 'accounting_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(200), nullable=False)
    tax_number = db.Column(db.String(50))
    commercial_register = db.Column(db.String(50))
    address = db.Column(db.Text)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    
    # إعدادات التقارير
    base_currency = db.Column(db.String(10), default='SAR')
    decimal_places = db.Column(db.Integer, default=2)
    
    # إعدادات الترقيم التلقائي
    next_transaction_number = db.Column(db.Integer, default=1)
    transaction_prefix = db.Column(db.String(10), default='JV')  # Journal Voucher
    
    # إعدادات السنة المالية
    fiscal_year_start_month = db.Column(db.Integer, default=1)  # يناير
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AuditLog(db.Model):
    """سجل التدقيق للعمليات المحاسبية"""
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    table_name = db.Column(db.String(100), nullable=False)  # اسم الجدول
    record_id = db.Column(db.Integer, nullable=False)  # معرف السجل
    action = db.Column(db.String(20), nullable=False)  # INSERT, UPDATE, DELETE
    old_values = db.Column(db.JSON)  # القيم القديمة
    new_values = db.Column(db.JSON)  # القيم الجديدة
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    user = db.relationship('User', backref='accounting_audit_logs')