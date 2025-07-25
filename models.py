from datetime import datetime, timedelta, date
from flask_login import UserMixin
from app import db
import enum

# في ملف models.py، يفضل وضعه قبل تعريف كلاس Employee و Department
# في models.py، يفضل وضعه مع جداول الربط الأخرى

user_accessible_departments = db.Table('user_accessible_departments',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True),
    db.Column('department_id', db.Integer, db.ForeignKey('department.id', ondelete='CASCADE'), primary_key=True)
)
# جدول الربط بين الموظفين والأقسام
employee_departments = db.Table('employee_departments',
    db.Column('employee_id', db.Integer, db.ForeignKey('employee.id', ondelete='CASCADE'), primary_key=True),
    db.Column('department_id', db.Integer, db.ForeignKey('department.id', ondelete='CASCADE'), primary_key=True)
)

# جدول الربط بين المركبات والمستخدمين - يسمح لأكثر من مستخدم الوصول للمركبة الواحدة
vehicle_user_access = db.Table('vehicle_user_access',
    db.Column('vehicle_id', db.Integer, db.ForeignKey('vehicle.id', ondelete='CASCADE'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
)
class Department(db.Model):
    """Department model for organizing employees"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    manager_id = db.Column(db.Integer, db.ForeignKey('employee.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employees = db.relationship('Employee', secondary=employee_departments, back_populates='departments')
    # employees = db.relationship('Employee', secondary=employee_departments, back_populates='departments', lazy='dynamic')

    manager_id = db.Column(
        db.Integer,
        db.ForeignKey('employee.id', name='fk_department_manager', ondelete='SET NULL', use_alter=True),
        nullable=True
    )
    accessible_users = db.relationship('User', 
                                       secondary=user_accessible_departments,
                                       back_populates='departments')
    
    def __repr__(self):
        return f'<Department {self.name}>'

# في models.py (قبل class Employee)

class Nationality(db.Model):
    """جدول لتخزين الجنسيات المختلفة"""
    __tablename__ = 'nationalities'
    
    id = db.Column(db.Integer, primary_key=True)
    name_ar = db.Column(db.String(100), nullable=False, unique=True) # اسم الجنسية بالعربية (مثال: "سعودي")
    name_en = db.Column(db.String(100), nullable=True, unique=True) # اسم الجنسية بالإنجليزية (مثال: "Saudi")
    country_code = db.Column(db.String(3), nullable=True) # رمز الدولة ISO 3166-1 alpha-3 (مثال: "SAU")
    
    # علاقة عكسية لجلب جميع الموظفين الذين يحملون هذه الجنسية
    employees = db.relationship('Employee', back_populates='nationality_rel')

    def __repr__(self):
        return f'<Nationality {self.name_ar}>'


class Employee(db.Model):
    """Employee model with all required personal and professional information"""
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(20), unique=True, nullable=False)  # Internal employee ID
    national_id = db.Column(db.String(20), unique=True, nullable=False)  # National ID number
    name = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(20), nullable=False)
    mobilePersonal  = db.Column(db.String(20), nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id', ondelete='SET NULL'), nullable=True)
    email = db.Column(db.String(100))
    job_title = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='active')  # active, inactive, on_leave
    location = db.Column(db.String(100))
    project = db.Column(db.String(100))
    join_date = db.Column(db.Date)
    birth_date = db.Column(db.Date, nullable=True)  # تاريخ الميلاد
    nationality = db.Column(db.String(50))  # جنسية الموظف
    nationality_id = db.Column(db.Integer, db.ForeignKey('nationalities.id', name='fk_employee_nationality_id'), nullable=True)
    contract_type = db.Column(db.String(20), default='foreign')  # سعودي / وافد - saudi / foreign
    basic_salary = db.Column(db.Float, default=0.0)  # الراتب الأساسي
    has_national_balance = db.Column(db.Boolean, default=False)  # هل يتوفر توازن وطني
    profile_image = db.Column(db.String(255))  # الصورة الشخصية
    national_id_image = db.Column(db.String(255))  # صورة الهوية الوطنية
    license_image = db.Column(db.String(255))  # صورة رخصة القيادة
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    contract_status = db.Column(db.String(50), nullable=True) # مثال: "ساري", "منتهي", "في فترة التجربة"
    license_status = db.Column(db.String(50), nullable=True)  # مثال: "سارية", "منتهية", "موقوفة"
    
    # حقول نوع الموظف والعهدة
    employee_type = db.Column(db.String(20), default='regular')  # 'regular' أو 'driver'
    has_mobile_custody = db.Column(db.Boolean, default=False)  # هل لديه عهدة جوال
    mobile_type = db.Column(db.String(100), nullable=True)  # نوع الجوال

    mobile_imei = db.Column(db.String(20), nullable=True)  # رقم IMEI
    
    # حقول الكفالة
    sponsorship_status = db.Column(db.String(20), default='inside', nullable=True)  # 'inside' = على الكفالة، 'outside' = خارج الكفالة
    current_sponsor_name = db.Column(db.String(100), nullable=True)  # اسم الكفيل الحالي
    
    # حقول المعلومات البنكية
    bank_iban = db.Column(db.String(50), nullable=True)  # رقم الإيبان البنكي
    bank_iban_image = db.Column(db.String(255), nullable=True)  # صورة الإيبان البنكي


    def to_dict(self):
        """
        تقوم بتحويل كائن الموظف إلى قاموس (dictionary) يمكن تحويله بسهولة إلى JSON.
        """
        # جلب معلومات الأقسام
        departments_list = []
        if self.departments:
            departments_list = [{'id': dept.id, 'name': dept.name} for dept in self.departments]
        
        # إضافة department_id للتوافق مع النظام القديم (أول قسم)
        department_id = None
        department = None
        if self.departments:
            department_id = self.departments[0].id
            department = {'id': self.departments[0].id, 'name': self.departments[0].name}
        
        return {
            'id': self.id,
            'name': self.name,
            'employee_id': self.employee_id,
            'national_id': self.national_id,
            'department_id': department_id,  # للتوافق مع الفلترة الحالية
            'department': department,  # معلومات القسم الأساسي
            'departments': departments_list  # جميع الأقسام
        }
    
    # Relationships
    departments = db.relationship('Department', secondary=employee_departments, back_populates='employees') 
    attendances = db.relationship('Attendance', back_populates='employee', cascade='all, delete-orphan')
    salaries = db.relationship('Salary', back_populates='employee', cascade='all, delete-orphan')
    documents = db.relationship('Document', back_populates='employee', cascade='all, delete-orphan')
    # vehicle_handovers = db.relationship('VehicleHandover', back_populates='employee_rel', foreign_keys='VehicleHandover.employee_id')
    nationality_rel = db.relationship('Nationality', back_populates='employees')

    handovers_as_driver = db.relationship(
        'VehicleHandover', 
        foreign_keys='VehicleHandover.employee_id', 
        back_populates='driver_employee',
        cascade="all, delete" # اختياري: إذا حذفت موظف، تحذف سجلات التسليم المرتبطة به
    )
    handovers_as_supervisor = db.relationship(
        'VehicleHandover', 
        foreign_keys='VehicleHandover.supervisor_employee_id', 
        back_populates='supervisor_employee',
        cascade="all, delete" # اختياري: نفس الملاحظة أعلاه
    )
    def __repr__(self):
        return f'<Employee {self.name} ({self.employee_id})>'

class Attendance(db.Model):
    """Attendance records for employees"""
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    check_in = db.Column(db.Time, nullable=True)
    check_out = db.Column(db.Time, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='present')  # present, absent, leave, sick
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employee = db.relationship('Employee', back_populates='attendances')
    
    def __repr__(self):
        return f'<Attendance {self.employee.name} on {self.date}>'

class Salary(db.Model):
    """Employee salary information"""
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id', ondelete='CASCADE'), nullable=False)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    basic_salary = db.Column(db.Float, nullable=False)
    allowances = db.Column(db.Float, default=0.0)
    deductions = db.Column(db.Float, default=0.0)
    bonus = db.Column(db.Float, default=0.0)
    net_salary = db.Column(db.Float, nullable=False)
    is_paid = db.Column(db.Boolean, default=False, nullable=False)
    overtime_hours = db.Column(db.Float, default=0.0)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employee = db.relationship('Employee', back_populates='salaries')
    
    def __repr__(self):
        return f'<Salary {self.employee.name} for {self.month}/{self.year}>'

class Document(db.Model):
    """Employee documents like ID cards, passports, certificates"""
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id', ondelete='CASCADE'), nullable=False)
    document_type = db.Column(db.String(50), nullable=False)  # national_id, passport, health_certificate, etc.
    document_number = db.Column(db.String(100), nullable=False)
    issue_date = db.Column(db.Date, nullable=True)  # تم تعديلها للسماح بقيم NULL
    expiry_date = db.Column(db.Date, nullable=True)  # تم تعديلها للسماح بقيم NULL
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employee = db.relationship('Employee', back_populates='documents')
    
    def __repr__(self):
        return f'<Document {self.document_type} for {self.employee.name}>'

# تعريف أدوار المستخدمين
class UserRole(enum.Enum):
    ADMIN = 'admin'        # مدير النظام - كل الصلاحيات
    MANAGER = 'manager'    # مدير - جميع الصلاحيات عدا إدارة المستخدمين
    HR = 'hr'              # موارد بشرية - إدارة الموظفين والمستندات
    FINANCE = 'finance'    # مالية - إدارة الرواتب والتكاليف
    FLEET = 'fleet'        # أسطول - إدارة السيارات والمركبات
    USER = 'user'          # مستخدم عادي - صلاحيات محدودة للعرض

# تعريف الصلاحيات
class Permission:
    VIEW = 0x01            # عرض البيانات فقط
    CREATE = 0x02          # إنشاء سجلات جديدة
    EDIT = 0x04            # تعديل السجلات
    DELETE = 0x08          # حذف السجلات
    MANAGE = 0x16          # إدارة القسم الخاص
    ADMIN = 0xff           # كل الصلاحيات

# صلاحيات الأقسام
class Module(enum.Enum):
    DASHBOARD = 'dashboard'   # لوحة التحكم
    EMPLOYEES = 'employees'
    ATTENDANCE = 'attendance'
    DEPARTMENTS = 'departments'
    SALARIES = 'salaries'
    DOCUMENTS = 'documents'
    VEHICLES = 'vehicles'
    USERS = 'users'
    REPORTS = 'reports'
    FEES = 'fees'

class User(UserMixin, db.Model):
    """User model for authentication"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(100), nullable=True)  # اسم المستخدم
    name = db.Column(db.String(100))
    phone = db.Column(db.String(20), nullable=True)  # رقم الهاتف
    firebase_uid = db.Column(db.String(128), unique=True, nullable=True)  # جعلها اختيارية للسماح بتسجيل الدخول المحلي
    password_hash = db.Column(db.String(256), nullable=True)  # حقل لتخزين هاش كلمة المرور
    profile_picture = db.Column(db.String(255))
    role = db.Column(db.Enum(UserRole), default=UserRole.USER)  # دور المستخدم
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    auth_type = db.Column(db.String(20), default='local')  # local أو firebase
    
    # الربط مع الموظف إذا كان المستخدم موظفًا في النظام
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=True)
    employee = db.relationship('Employee', foreign_keys=[employee_id], uselist=False)
    
    # القسم المخصص للمستخدم (للتحكم في الوصول)
    assigned_department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=True)
    assigned_department = db.relationship('Department', foreign_keys=[assigned_department_id], uselist=False)
    departments = db.relationship('Department', 
                                  secondary=user_accessible_departments,
                                  back_populates='accessible_users')
    
    # العلاقة مع صلاحيات المستخدم
    permissions = db.relationship('UserPermission', back_populates='user', cascade='all, delete-orphan')

    # العلاقة مع المركبات التي يمكن للمستخدم الوصول إليها
    accessible_vehicles = db.relationship('Vehicle',
                                        secondary=vehicle_user_access,
                                        back_populates='authorized_users')

    
    def set_password(self, password):
        """تعيين كلمة المرور المشفرة"""
        from werkzeug.security import generate_password_hash
        self.password_hash = generate_password_hash(password)


   
    

    
    def check_password(self, password):
        """التحقق من كلمة المرور"""
        from werkzeug.security import check_password_hash
        if self.password_hash:
            return check_password_hash(self.password_hash, password)
        return False
    
    def has_permission(self, module, permission):
        """التحقق مما إذا كان المستخدم لديه صلاحية معينة"""
        # المديرون لديهم كل الصلاحيات
        if self.role == UserRole.ADMIN:
            return True
            
        # التحقق من صلاحيات القسم المحدد
        for user_permission in self.permissions:
            if user_permission.module == module:
                return user_permission.permissions & permission
                
        return False

    def can_access_department(self, department_id):
        if self.role == UserRole.ADMIN:
            return True
        
        # تحقق مما إذا كان معرف القسم موجوداً في قائمة الأقسام المخصصة للمستخدم
        return any(dept.id == department_id for dept in self.departments)

    def get_accessible_departments(self):
        if self.role == UserRole.ADMIN:
            from app.models import Department
            return Department.query.all()
        
        # أرجع قائمة الأقسام المرتبطة مباشرة
        return self.departments
        
    def has_module_access(self, module):
        """التحقق مما إذا كان المستخدم لديه وصول إلى وحدة معينة"""
        # المديرون لديهم وصول إلى جميع الوحدات
        if self.role == UserRole.ADMIN:
            return True
            
        return any(p.module == module for p in self.permissions)
    
    def can_access_department(self, department_id):
        """التحقق مما إذا كان المستخدم يمكنه الوصول إلى قسم معين"""
        # المديرون لديهم وصول إلى جميع الأقسام
        if self.role == UserRole.ADMIN:
            return True
            
        # إذا كان لديه قسم مخصص، يمكنه الوصول إليه فقط
        if self.assigned_department_id:
            return self.assigned_department_id == department_id
            
        # إذا لم يكن لديه قسم مخصص، لا يمكنه الوصول إلى أي قسم
        return False
    
    def get_accessible_departments(self):
        """جلب الأقسام التي يمكن للمستخدم الوصول إليها"""
        from app import db
        
        # المديرون لديهم وصول إلى جميع الأقسام
        if self.role == UserRole.ADMIN:
            return Department.query.all()
            
        # إذا كان لديه قسم مخصص، يعرض هذا القسم فقط
        if self.assigned_department_id:
            return [self.assigned_department]
            
        # إذا لم يكن لديه قسم مخصص، لا يعرض أي قسم
        return []
    
    def __repr__(self):
        return f'<User {self.email}>'

class UserPermission(db.Model):
    """صلاحيات المستخدم لكل وحدة"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    module = db.Column(db.Enum(Module), nullable=False)
    permissions = db.Column(db.Integer, default=Permission.VIEW)  # بتات الصلاحيات
    
    # العلاقات
    user = db.relationship('User', back_populates='permissions')
    
    def __repr__(self):
        return f'<UserPermission {self.user_id} - {self.module}>'

class RenewalFee(db.Model):
    """تكاليف رسوم تجديد أوراق الموظفين"""
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('document.id', ondelete='CASCADE'), nullable=False)
    fee_date = db.Column(db.Date, nullable=False)
    fee_type = db.Column(db.String(50), nullable=False)  # passport, labor_office, insurance, social_insurance, transfer_sponsorship, other
    amount = db.Column(db.Float, nullable=False)
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, overdue
    payment_date = db.Column(db.Date, nullable=True)
    receipt_number = db.Column(db.String(50), nullable=True)
    transfer_number = db.Column(db.String(50), nullable=True)  # رقم نقل الكفالة
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    document = db.relationship('Document', backref=db.backref('renewal_fees', cascade='all, delete-orphan'))
    
    def __repr__(self):
        return f'<RenewalFee {self.fee_type} for document #{self.document_id}>'
        
class Fee(db.Model):
    """نموذج الرسوم العامة - للاستخدام في تقارير الرسوم والمدفوعات"""
    id = db.Column(db.Integer, primary_key=True)
    fee_type = db.Column(db.String(50), nullable=False)  # نوع الرسم
    description = db.Column(db.String(255))  # وصف الرسم
    amount = db.Column(db.Float, nullable=False)  # مبلغ الرسم
    due_date = db.Column(db.Date)  # تاريخ استحقاق الرسم
    is_paid = db.Column(db.Boolean, default=False)  # هل تم دفع الرسم
    paid_date = db.Column(db.Date)  # تاريخ الدفع
    recipient = db.Column(db.String(100))  # الجهة المستلمة
    reference_number = db.Column(db.String(50))  # رقم المرجع
    notes = db.Column(db.Text)  # ملاحظات
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات (اختياري - يمكن ربط الرسم بموظف أو مركبة أو مستند)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id', ondelete='SET NULL'), nullable=True)
    document_id = db.Column(db.Integer, db.ForeignKey('document.id', ondelete='SET NULL'), nullable=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id', ondelete='SET NULL'), nullable=True)
    
    # العلاقات
    employee = db.relationship('Employee', backref=db.backref('fees', lazy='dynamic'))
    document = db.relationship('Document', backref=db.backref('fees', lazy='dynamic'))
    vehicle = db.relationship('Vehicle', backref=db.backref('fees', lazy='dynamic'))
    
    def __repr__(self):
        return f'<Fee {self.fee_type} - {self.amount} SAR>'

class FeesCost(db.Model):
    """تكاليف الرسوم للوثائق والمستندات"""
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('document.id', ondelete='CASCADE'), nullable=False)
    document_type = db.Column(db.String(50), nullable=False)  # نوع الوثيقة: national_id, residence, passport, etc.
    
    # تكاليف مختلف الرسوم
    passport_fee = db.Column(db.Float, default=0.0)  # رسوم الجوازات
    labor_office_fee = db.Column(db.Float, default=0.0)  # رسوم مكتب العمل
    insurance_fee = db.Column(db.Float, default=0.0)  # رسوم التأمين
    social_insurance_fee = db.Column(db.Float, default=0.0)  # رسوم التأمينات الاجتماعية
    transfer_sponsorship = db.Column(db.Boolean, default=False)  # هل يتطلب نقل كفالة
    
    # معلومات التواريخ والدفع
    due_date = db.Column(db.Date, nullable=False)  # تاريخ استحقاق الرسوم
    payment_status = db.Column(db.String(20), default='pending')  # حالة السداد: pending, paid, overdue
    payment_date = db.Column(db.Date, nullable=True)  # تاريخ السداد
    
    # معلومات إضافية
    notes = db.Column(db.Text)  # ملاحظات
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    document = db.relationship('Document', backref=db.backref('fees_costs', cascade='all, delete-orphan'))
    
    def __repr__(self):
        return f'<FeesCost for document #{self.document_id}, type: {self.document_type}>'
    
    @property
    def total_fees(self):
        """إجمالي تكاليف جميع الرسوم"""
        return self.passport_fee + self.labor_office_fee + self.insurance_fee + self.social_insurance_fee

class SystemAudit(db.Model):
    """سجل عمليات النظام للإجراءات المهمة - Audit trail"""
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(100), nullable=False)  # نوع الإجراء (إضافة، تعديل، حذف)
    entity_type = db.Column(db.String(50), nullable=False)  # نوع الكيان (موظف، قسم، راتب، الخ)
    entity_id = db.Column(db.Integer, nullable=False)  # معرف الكيان
    entity_name = db.Column(db.String(255))  # اسم الكيان للعرض
    previous_data = db.Column(db.Text)  # البيانات قبل التعديل (JSON)
    new_data = db.Column(db.Text)  # البيانات بعد التعديل (JSON)
    details = db.Column(db.Text)  # تفاصيل إضافية
    ip_address = db.Column(db.String(50))  # عنوان IP لمصدر العملية
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # وقت العملية
    
    # إضافة مرجع للمستخدم الذي قام بالإجراء
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    user = db.relationship('User', foreign_keys=[user_id])
    
    def __repr__(self):
        return f'<SystemAudit {self.action} on {self.entity_type} #{self.entity_id}>'
        
    @classmethod
    def create_audit_record(cls, user_id, action, entity_type, entity_id, details=None, entity_name=None):
        """
        إنشاء سجل نشاط جديد
        
        :param user_id: معرف المستخدم الذي قام بالإجراء
        :param action: نوع الإجراء (إضافة، تعديل، حذف)
        :param entity_type: نوع الكيان
        :param entity_id: معرف الكيان
        :param details: تفاصيل الإجراء (اختياري)
        :param entity_name: اسم الكيان (اختياري)
        :return: كائن SystemAudit
        """
        # إنشاء سجل جديد
        from flask import request
        
        ip_address = "127.0.0.1"
        if request:
            ip_address = request.remote_addr or "127.0.0.1"
        
        audit = cls(
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            entity_name=entity_name,
            details=details,
            ip_address=ip_address,
            timestamp=datetime.utcnow()
        )
        
        # حفظ السجل في قاعدة البيانات
        from app import db
        db.session.add(audit)
        db.session.commit()
        
        return audit

# نماذج إدارة السيارات
class Vehicle(db.Model):
    """نموذج السيارة مع المعلومات الأساسية"""
    id = db.Column(db.Integer, primary_key=True)
    plate_number = db.Column(db.String(20), nullable=False, unique=True)  # رقم اللوحة
    make = db.Column(db.String(50), nullable=False)  # الشركة المصنعة (تويوتا، نيسان، إلخ)
    model = db.Column(db.String(50), nullable=False)  # موديل السيارة
    year = db.Column(db.Integer, nullable=False)  # سنة الصنع
    color = db.Column(db.String(30), nullable=False)  # لون السيارة
    status = db.Column(db.String(30), nullable=False, default='available')  # الحالة: متاحة، مؤجرة، في المشروع، في الورشة، حادث
    driver_name = db.Column(db.String(100), nullable=True)  # اسم السائق
    type_of_car = db.Column(db.String(100),nullable=False)
    
    # تواريخ انتهاء الوثائق الهامة
    authorization_expiry_date = db.Column(db.Date)  # تاريخ انتهاء التفويض
    registration_expiry_date = db.Column(db.Date)  # تاريخ انتهاء استمارة السيارة
    inspection_expiry_date = db.Column(db.Date)  # تاريخ انتهاء الفحص الدوري
    
    # إضافة حقل صورة رخصة السيارة
    license_image = db.Column(db.String(255), nullable=True)  # صورة رخصة السيارة
    
    # إضافة حقول الصور الجديدة المطلوبة
    registration_form_image = db.Column(db.String(255), nullable=True)  # صورة استمارة السيارة
    plate_image = db.Column(db.String(255), nullable=True)  # صورة لوحة السيارة
    insurance_file = db.Column(db.String(255), nullable=True)  # ملف التأمين
    
    # إضافة حقل المشروع
    project = db.Column(db.String(100), nullable=True)  # اسم المشروع
    
    # إضافة حقل رابط مجلد Google Drive
    drive_folder_link = db.Column(db.String(500), nullable=True)  # رابط مجلد Google Drive
    
    notes = db.Column(db.Text)  # ملاحظات
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    rental_records = db.relationship('VehicleRental', back_populates='vehicle', cascade='all, delete-orphan')
    workshop_records = db.relationship('VehicleWorkshop', back_populates='vehicle', cascade='all, delete-orphan')
    project_assignments = db.relationship('VehicleProject', back_populates='vehicle', cascade='all, delete-orphan')
    handover_records = db.relationship('VehicleHandover', back_populates='vehicle', cascade='all, delete-orphan') 
    periodic_inspections = db.relationship('VehiclePeriodicInspection', back_populates='vehicle', cascade='all, delete-orphan')
    safety_checks = db.relationship('VehicleSafetyCheck', back_populates='vehicle', cascade='all, delete-orphan')
    accidents = db.relationship('VehicleAccident', back_populates='vehicle', cascade='all, delete-orphan')

    # علاقة many-to-many مع المستخدمين - المستخدمون الذين يمكنهم الوصول لهذه المركبة
    authorized_users = db.relationship('User',
                                      secondary=vehicle_user_access,
                                      back_populates='accessible_vehicles')

    def __repr__(self):
        return f'<Vehicle {self.plate_number} {self.make} {self.model}>'


class VehicleRental(db.Model):
    """معلومات إيجار السيارة"""
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id', ondelete='CASCADE'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)  # تاريخ بداية الإيجار
    end_date = db.Column(db.Date)  # تاريخ نهاية الإيجار (قد يكون فارغا إذا كان الإيجار مستمرا)
    monthly_cost = db.Column(db.Float, nullable=False)  # قيمة الإيجار الشهري
    is_active = db.Column(db.Boolean, default=True)  # هل الإيجار نشط حاليا
    lessor_name = db.Column(db.String(100))  # اسم المؤجر أو الشركة المؤجرة
    lessor_contact = db.Column(db.String(100))  # معلومات الاتصال بالمؤجر
    contract_number = db.Column(db.String(50))  # رقم العقد
    city = db.Column(db.String(100))  # المدينة/المكان الذي توجد فيه السيارة
    notes = db.Column(db.Text)  # ملاحظات
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    vehicle = db.relationship('Vehicle', back_populates='rental_records')
    
    def __repr__(self):
        return f'<VehicleRental {self.vehicle_id} {self.start_date} to {self.end_date}>'


class VehicleWorkshop(db.Model):
    """معلومات دخول وخروج السيارة من الورشة"""
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id', ondelete='CASCADE'), nullable=False)
    entry_date = db.Column(db.Date, nullable=False)  # تاريخ دخول الورشة
    exit_date = db.Column(db.Date)  # تاريخ الخروج (قد يكون فارغا إذا كانت ما زالت في الورشة)
    reason = db.Column(db.String(50), nullable=False)  # السبب: عطل، صيانة دورية، حادث
    description = db.Column(db.Text, nullable=False)  # وصف العطل أو الصيانة
    repair_status = db.Column(db.String(30), nullable=False, default='in_progress')  # الحالة: قيد التنفيذ، تم الإصلاح، بانتظار الموافقة
    cost = db.Column(db.Float, default=0.0)  # تكلفة الإصلاح
    workshop_name = db.Column(db.String(100))  # اسم الورشة
    technician_name = db.Column(db.String(100))  # اسم الفني المسؤول
    delivery_link = db.Column(db.String(255))  # رابط تسليم ورشة
    reception_link = db.Column(db.String(255))  # رابط استلام من ورشة
    notes = db.Column(db.Text)  # ملاحظات
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    vehicle = db.relationship('Vehicle', back_populates='workshop_records')
    images = db.relationship('VehicleWorkshopImage', back_populates='workshop_record', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<VehicleWorkshop {self.vehicle_id} {self.entry_date} {self.reason}>'


class VehicleWorkshopImage(db.Model):
    """صور توثيقية للسيارة في الورشة"""
    id = db.Column(db.Integer, primary_key=True)
    workshop_record_id = db.Column(db.Integer, db.ForeignKey('vehicle_workshop.id', ondelete='CASCADE'), nullable=False)
    image_type = db.Column(db.String(20), nullable=False)  # النوع: قبل الإصلاح، بعد الإصلاح
    image_path = db.Column(db.String(255), nullable=False)  # مسار الصورة
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)  # ملاحظات
    
    # العلاقات
    workshop_record = db.relationship('VehicleWorkshop', back_populates='images')
    
    def __repr__(self):
        return f'<VehicleWorkshopImage {self.workshop_record_id} {self.image_type}>'

class VehicleProject(db.Model):
    """معلومات تخصيص السيارة لمشروع معين"""
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id', ondelete='CASCADE'), nullable=False)
    project_name = db.Column(db.String(100), nullable=False)  # اسم المشروع
    location = db.Column(db.String(100), nullable=False)  # موقع المشروع (المدينة، المنطقة)
    manager_name = db.Column(db.String(100), nullable=False)  # اسم مسؤول المشروع
    start_date = db.Column(db.Date, nullable=False)  # تاريخ بداية تخصيص السيارة للمشروع
    end_date = db.Column(db.Date)  # تاريخ نهاية التخصيص (قد يكون فارغا إذا كان مستمرا)
    is_active = db.Column(db.Boolean, default=True)  # هل التخصيص نشط حاليا
    notes = db.Column(db.Text)  # ملاحظات
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    vehicle = db.relationship('Vehicle', back_populates='project_assignments')
    
    def __repr__(self):
        return f'<VehicleProject {self.vehicle_id} {self.project_name}>'


# في ملف models.py، استبدل الكلاس VehicleHandover القديم بالكامل بهذا الكود.

class VehicleHandover(db.Model):
    """
    نموذج تسليم واستلام السيارة (نسخة معدلة ومكتفية ذاتياً)
    يحتوي على نسخة من جميع المعلومات وقت حدوث العملية لضمان سلامة السجلات التاريخية.
    """
    __tablename__ = 'vehicle_handover'  # من الجيد تحديد اسم الجدول بشكل صريح

    id = db.Column(db.Integer, primary_key=True)
    
    # --- 1. معلومات العملية الأساسية ---
    # هذه الحقول موجودة بالفعل وتم الإبقاء عليها كما هي
    handover_type = db.Column(db.String(20), nullable=False)  # 'delivery' (تسليم) أو 'receipt' (استلام)
    handover_date = db.Column(db.Date, nullable=False)
    mileage = db.Column(db.Integer, nullable=False)

    # حقول جديدة تمت إضافتها بناءً على التصميم الجديد
    handover_time = db.Column(db.Time, nullable=True) # **جديد**: وقت العملية
    project_name = db.Column(db.String(100), nullable=True) # **جديد**: اسم المشروع وقت العملية
    city = db.Column(db.String(100), nullable=True) # **جديد**: اسم المدينة وقت العملية
    
    # --- 2. معلومات السيارة المنسوخة (Snapshot) ---
    # يبقى الربط فقط لسهولة الوصول للسيارة الحالية، ولكن بيانات التقرير تأتي من الحقول أدناه    
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id', ondelete='CASCADE'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id', name='fk_handover_driver_employee_id'), nullable=True)
    supervisor_employee_id = db.Column(db.Integer, db.ForeignKey('employee.id', name='fk_handover_supervisor_employee_id'), nullable=True)

    # **جديد**: حقول لحفظ نسخة من بيانات السيارة وقت التسليم
    vehicle_car_type = db.Column(db.String(100), nullable=True) # مثال: "Nissan urvan"
    vehicle_plate_number = db.Column(db.String(20), nullable=True)
    vehicle_model_year = db.Column(db.String(10), nullable=True) # مثال: "2021"

    # --- 3. بيانات السائق/المستلم (Recipient) المنسوخة ---
    # تم الإبقاء على الحقل القديم `person_name` ليمثل اسم السائق الرئيسي
    person_name = db.Column(db.String(100), nullable=False) # سابقاً: اسم الشخص المستلم/المسلم. الآن: اسم السائق/المستلم

    # **جديد**: حقول إضافية لبيانات السائق المنسوخة
    driver_company_id = db.Column(db.String(50), nullable=True) # رقم شركة السائق
    driver_phone_number = db.Column(db.String(20), nullable=True) # رقم جوال السائق
    driver_residency_number = db.Column(db.String(50), nullable=True) # رقم إقامة السائق
    driver_contract_status = db.Column(db.String(50), nullable=True) # حالة عقد السائق
    driver_license_status = db.Column(db.String(50), nullable=True) # حالة رخصة السائق
    driver_signature_path = db.Column(db.String(255), nullable=True) # مسار توقيع السائق (موجود بالفعل)

    # --- 4. بيانات المشرف/المسلِّم (Deliverer) المنسوخة ---
    # تم الإبقاء على الحقل القديم `supervisor_name` ليمثل اسم المشرف الرئيسي
    supervisor_name = db.Column(db.String(100))
    
    # **جديد**: حقول إضافية لبيانات المشرف المنسوخة
    supervisor_company_id = db.Column(db.String(50), nullable=True) # رقم شركة المشرف
    supervisor_phone_number = db.Column(db.String(20), nullable=True) # رقم جوال المشرف
    supervisor_residency_number = db.Column(db.String(50), nullable=True) # رقم إقامة المشرف
    supervisor_contract_status = db.Column(db.String(50), nullable=True) # حالة عقد المشرف
    supervisor_license_status = db.Column(db.String(50), nullable=True) # حالة رخصة المشرف
    supervisor_signature_path = db.Column(db.String(255), nullable=True) # مسار توقيع المشرف (موجود بالفعل)
    
    # --- 5. بيانات الفحص والملاحظات والتفويض ---
    # تم استبدال `vehicle_condition` بالحقول الأكثر تفصيلاً أدناه
    # vehicle_condition = db.Column(db.Text, nullable=False) # -> تم استبداله

    # **جديد**: حقول جديدة للملاحظات التفصيلية حسب التصميم
    reason_for_change = db.Column(db.Text, nullable=True) # سبب تغيير المركبة (النص الكبير في الجدول)
    vehicle_status_summary = db.Column(db.String(255), nullable=True) # ملخص الحالة (مثال: "يوجد ملاحظات")
    notes = db.Column(db.Text) # ملاحظات إضافية (موجود بالفعل)
    reason_for_authorization = db.Column(db.Text, nullable=True) # سبب التفويض
    authorization_details = db.Column(db.String(255), nullable=True) # تفاصيل التفويض (مثل "تفويض واصل")

    # حقول الـ Checklist (موجودة بالفعل ولا تحتاج تغيير)
    fuel_level = db.Column(db.String(20), nullable=False)
    has_spare_tire = db.Column(db.Boolean, default=True)
    has_fire_extinguisher = db.Column(db.Boolean, default=True)
    has_first_aid_kit = db.Column(db.Boolean, default=True)
    has_warning_triangle = db.Column(db.Boolean, default=True)
    has_tools = db.Column(db.Boolean, default=True)
    has_oil_leaks = db.Column(db.Boolean, nullable=False, default=False)
    has_gear_issue = db.Column(db.Boolean, nullable=False, default=False)
    has_clutch_issue = db.Column(db.Boolean, nullable=False, default=False)
    has_engine_issue = db.Column(db.Boolean, nullable=False, default=False)
    has_windows_issue = db.Column(db.Boolean, nullable=False, default=False)
    has_tires_issue = db.Column(db.Boolean, nullable=False, default=False)
    has_body_issue = db.Column(db.Boolean, nullable=False, default=False)
    has_electricity_issue = db.Column(db.Boolean, nullable=False, default=False)
    has_lights_issue = db.Column(db.Boolean, nullable=False, default=False)
    has_ac_issue = db.Column(db.Boolean, nullable=False, default=False)
    
    # --- 6. بيانات إضافية متنوعة ---
    # **جديد**: معلومات مسؤول الحركة
    movement_officer_name = db.Column(db.String(100), nullable=True)
    movement_officer_signature_path = db.Column(db.String(255), nullable=True)

    # الحقول التالية موجودة بالفعل
    damage_diagram_path = db.Column(db.String(255), nullable=True)
    form_link = db.Column(db.String(255), nullable=True)
    custom_company_name = db.Column(db.String(100), nullable=True)
    custom_logo_path = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # --- حقول وعلاقات تم حذفها أو تعديلها ---
    # employee_id: تم حذفه لأنه لم نعد نربط الموظف مباشرةً.
    # employee_rel: تم حذف هذه العلاقة.

    # --- العلاقات المتبقية ---
    # نعدل علاقة المركبة لتكون أبسط
    images = db.relationship('VehicleHandoverImage', back_populates='handover_record', cascade='all, delete-orphan')
    vehicle = db.relationship('Vehicle', back_populates='handover_records')

    driver_employee = db.relationship(
        'Employee', 
        foreign_keys=[employee_id], 
        back_populates='handovers_as_driver'
    )
    
    supervisor_employee = db.relationship(
        'Employee', 
        foreign_keys=[supervisor_employee_id], 
        back_populates='handovers_as_supervisor'
    )


    def __repr__(self):
        # استخدام البيانات المنسوخة في الـ repr لضمان عدم حدوث خطأ إذا حُذفت المركبة
        return f'<VehicleHandover {self.id} for vehicle {self.vehicle_plate_number} on {self.handover_date}>'

    def to_dict(self):
        """
        تحويل كائن VehicleHandover إلى قاموس قابل للتحويل إلى JSON
        """
        return {
            'id': self.id,
            'vehicle_id': self.vehicle_id,
            'handover_type': self.handover_type,
            'handover_date': self.handover_date.strftime('%Y-%m-%d') if self.handover_date else None,
            'handover_time': self.handover_time.strftime('%H:%M') if self.handover_time else None,
            'mileage': self.mileage,
            'project_name': self.project_name,
            'city': self.city,
            'vehicle_car_type': self.vehicle_car_type,
            'vehicle_plate_number': self.vehicle_plate_number,
            'vehicle_model_year': self.vehicle_model_year,
            'employee_id': self.employee_id,
            'person_name': self.person_name,
            'driver_company_id': self.driver_company_id,
            'driver_phone_number': self.driver_phone_number,
            'driver_residency_number': self.driver_residency_number,
            'driver_contract_status': self.driver_contract_status,
            'driver_license_status': self.driver_license_status,
            'driver_signature_path': self.driver_signature_path,
            'supervisor_employee_id': self.supervisor_employee_id,
            'supervisor_name': self.supervisor_name,
            'supervisor_company_id': self.supervisor_company_id,
            'supervisor_phone_number': self.supervisor_phone_number,
            'supervisor_residency_number': self.supervisor_residency_number,
            'supervisor_contract_status': self.supervisor_contract_status,
            'supervisor_license_status': self.supervisor_license_status,
            'supervisor_signature_path': self.supervisor_signature_path,
            'reason_for_change': self.reason_for_change,
            'vehicle_status_summary': self.vehicle_status_summary,
            'notes': self.notes,
            'reason_for_authorization': self.reason_for_authorization,
            'authorization_details': self.authorization_details,
            'fuel_level': self.fuel_level,
            'has_spare_tire': self.has_spare_tire,
            'has_fire_extinguisher': self.has_fire_extinguisher,
            'has_first_aid_kit': self.has_first_aid_kit,
            'has_warning_triangle': self.has_warning_triangle,
            'has_tools': self.has_tools,
            'has_oil_leaks': self.has_oil_leaks,
            'has_gear_issue': self.has_gear_issue,
            'has_clutch_issue': self.has_clutch_issue,
            'has_engine_issue': self.has_engine_issue,
            'has_windows_issue': self.has_windows_issue,
            'has_tires_issue': self.has_tires_issue,
            'has_body_issue': self.has_body_issue,
            'has_electricity_issue': self.has_electricity_issue,
            'has_lights_issue': self.has_lights_issue,
            'has_ac_issue': self.has_ac_issue,
            'movement_officer_name': self.movement_officer_name,
            'movement_officer_signature_path': self.movement_officer_signature_path,
            'damage_diagram_path': self.damage_diagram_path,
            'form_link': self.form_link,
            'custom_company_name': self.custom_company_name,
            'custom_logo_path': self.custom_logo_path,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }



# class VehicleHandover(db.Model):
#     """نموذج تسليم واستلام السيارة"""
#     id = db.Column(db.Integer, primary_key=True)
#     vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id', ondelete='CASCADE'), nullable=False)
#     handover_type = db.Column(db.String(20), nullable=False)  # النوع: تسليم، استلام
#     handover_date = db.Column(db.Date, nullable=False)  # تاريخ التسليم/الاستلام
#     person_name = db.Column(db.String(100), nullable=False)  # اسم الشخص المستلم/المسلم
#     employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=True)  # معرف الموظف المستلم/المسلم
#     supervisor_name = db.Column(db.String(100))  # اسم المشرف
#     vehicle_condition = db.Column(db.Text, nullable=False)  # حالة السيارة عند التسليم/الاستلام
#     fuel_level = db.Column(db.String(20), nullable=False)  # مستوى الوقود
#     mileage = db.Column(db.Integer, nullable=False)  # عداد الكيلومترات
#     has_spare_tire = db.Column(db.Boolean, default=True)  # وجود إطار احتياطي
#     has_fire_extinguisher = db.Column(db.Boolean, default=True)  # وجود طفاية حريق
#     has_first_aid_kit = db.Column(db.Boolean, default=True)  # وجود حقيبة إسعافات أولية
#     has_warning_triangle = db.Column(db.Boolean, default=True)  # وجود مثلث تحذيري
#     has_tools = db.Column(db.Boolean, default=True)  # وجود أدوات
#     form_link = db.Column(db.String(255))  # رابط فورم التسليم/الاستلام
#     notes = db.Column(db.Text)  # ملاحظات إضافية
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     damage_diagram_path = db.Column(db.String(255), nullable=True)
#     has_oil_leaks = db.Column(db.Boolean, nullable=False, default=False)
#     has_gear_issue = db.Column(db.Boolean, nullable=False, default=False)
#     has_clutch_issue = db.Column(db.Boolean, nullable=False, default=False)
#     has_engine_issue = db.Column(db.Boolean, nullable=False, default=False)
#     has_windows_issue = db.Column(db.Boolean, nullable=False, default=False)
#     has_tires_issue = db.Column(db.Boolean, nullable=False, default=False)
#     has_body_issue = db.Column(db.Boolean, nullable=False, default=False)
#     has_electricity_issue = db.Column(db.Boolean, nullable=False, default=False)
#     has_lights_issue = db.Column(db.Boolean, nullable=False, default=False)
#     has_ac_issue = db.Column(db.Boolean, nullable=False, default=False)
#     supervisor_signature_path = db.Column(db.String(255), nullable=True)
#     driver_signature_path = db.Column(db.String(255), nullable=True)
#     custom_company_name = db.Column(db.String(100), nullable=True)
#     custom_logo_path = db.Column(db.String(255), nullable=True)


#     # العلاقات
#     vehicle = db.relationship('Vehicle', back_populates='handover_records')
#     employee_rel = db.relationship('Employee', foreign_keys=[employee_id], back_populates='vehicle_handovers')
#     images = db.relationship('VehicleHandoverImage', back_populates='handover_record', cascade='all, delete-orphan')
#     def __repr__(self):
#         return f'<VehicleHandover {self.vehicle_id} {self.handover_type} {self.handover_date}>'


class VehicleHandoverImage(db.Model):
    """صور وملفات PDF توثيقية لحالة السيارة عند التسليم/الاستلام"""
    id = db.Column(db.Integer, primary_key=True)
    handover_record_id = db.Column(db.Integer, db.ForeignKey('vehicle_handover.id', ondelete='CASCADE'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)  # مسار الصورة (الاسم القديم للحقل)
    image_description = db.Column(db.String(100))  # وصف الصورة (الاسم القديم للحقل)
    file_path = db.Column(db.String(255))  # مسار الملف (الجديد)
    file_type = db.Column(db.String(20), default='image')  # نوع الملف (image/pdf)
    file_description = db.Column(db.String(200))  # وصف الملف (الجديد)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    handover_record = db.relationship('VehicleHandover', back_populates='images')
    
    def __repr__(self):
        return f'<VehicleHandoverImage {self.handover_record_id}>'
        
    # للحفاظ على التوافق بين الأعمدة القديمة والجديدة
    def get_path(self):
        """الحصول على مسار الملف بغض النظر عن طريقة التخزين (قديمة أو جديدة)"""
        return self.file_path or self.image_path
    
    def get_description(self):
        """الحصول على وصف الملف بغض النظر عن طريقة التخزين (قديمة أو جديدة)"""
        return self.file_description or self.image_description
    
    def get_type(self):
        """الحصول على نوع الملف، مع افتراض أنه صورة إذا لم يكن محدداً"""
        return self.file_type or 'image'
    
    def is_pdf(self):
        """التحقق مما إذا كان الملف PDF"""
        file_path = self.get_path()
        return self.get_type() == 'pdf' or (file_path and file_path.lower().endswith('.pdf'))

class VehicleChecklist(db.Model):
    """تشيك لست فحص السيارة"""
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id', ondelete='CASCADE'), nullable=False)
    inspection_date = db.Column(db.Date, nullable=False)  # تاريخ الفحص
    inspector_name = db.Column(db.String(100), nullable=False)  # اسم الفاحص
    inspection_type = db.Column(db.String(20), nullable=False)  # نوع الفحص: يومي، أسبوعي، شهري، ربع سنوي
    status = db.Column(db.String(20), default='completed')  # حالة الفحص: مكتمل، قيد التنفيذ، ملغي
    notes = db.Column(db.Text)  # ملاحظات عامة
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    vehicle = db.relationship('Vehicle', backref=db.backref('checklists', cascade='all, delete-orphan'))
    checklist_items = db.relationship('VehicleChecklistItem', back_populates='checklist', cascade='all, delete-orphan')
    images = db.relationship('VehicleChecklistImage', back_populates='checklist', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<VehicleChecklist {self.id} for vehicle {self.vehicle_id} on {self.inspection_date}>'
    
    @property
    def completion_percentage(self):
        """حساب نسبة اكتمال الفحص"""
        if not self.checklist_items:
            return 0
        
        total_items = len(self.checklist_items)
        completed_items = sum(1 for item in self.checklist_items if item.status != 'not_checked')
        
        return int((completed_items / total_items) * 100)
    
    @property
    def summary(self):
        """ملخص حالة الفحص"""
        if not self.checklist_items:
            return {'good': 0, 'fair': 0, 'poor': 0, 'not_checked': 0}
        
        summary = {'good': 0, 'fair': 0, 'poor': 0, 'not_checked': 0}
        for item in self.checklist_items:
            summary[item.status] += 1
        
        return summary


class VehicleChecklistItem(db.Model):
    """عناصر تشيك لست فحص السيارة"""
    id = db.Column(db.Integer, primary_key=True)
    checklist_id = db.Column(db.Integer, db.ForeignKey('vehicle_checklist.id', ondelete='CASCADE'), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # فئة العنصر: محرك، إطارات، إضاءة، مكونات داخلية، إلخ
    item_name = db.Column(db.String(100), nullable=False)  # اسم العنصر: زيت المحرك، ضغط الإطارات، إلخ
    status = db.Column(db.String(20), nullable=False, default='not_checked')  # الحالة: جيد، متوسط، سيء، لم يتم الفحص
    notes = db.Column(db.Text)  # ملاحظات خاصة بالعنصر
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    checklist = db.relationship('VehicleChecklist', back_populates='checklist_items')
    
    def __repr__(self):
        return f'<VehicleChecklistItem {self.id} {self.item_name} status: {self.status}>'


class VehicleChecklistImage(db.Model):
    """صور فحص السيارة (تشيك لست)"""
    id = db.Column(db.Integer, primary_key=True)
    checklist_id = db.Column(db.Integer, db.ForeignKey('vehicle_checklist.id', ondelete='CASCADE'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)  # مسار الصورة
    image_type = db.Column(db.String(50), default='inspection')  # نوع الصورة: فحص عام، ضرر، إلخ
    description = db.Column(db.Text)  # وصف الصورة
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    checklist = db.relationship('VehicleChecklist', back_populates='images')
    
    def __repr__(self):
        return f'<VehicleChecklistImage {self.id} for checklist {self.checklist_id}>'


class VehicleDamageMarker(db.Model):
    """علامات تلف السيارة المسجلة على الرسم البياني للمركبة"""
    id = db.Column(db.Integer, primary_key=True)
    checklist_id = db.Column(db.Integer, db.ForeignKey('vehicle_checklist.id', ondelete='CASCADE'), nullable=False)
    marker_type = db.Column(db.String(20), nullable=False, default='damage')  # نوع العلامة: تلف، خدش، كسر، إلخ
    position_x = db.Column(db.Float, nullable=False)  # الموقع س على الصورة (نسبة مئوية)
    position_y = db.Column(db.Float, nullable=False)  # الموقع ص على الصورة (نسبة مئوية)
    color = db.Column(db.String(20), default='red')  # لون العلامة
    size = db.Column(db.Float, default=10.0)  # حجم العلامة
    notes = db.Column(db.Text)  # ملاحظات حول التلف
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    checklist = db.relationship('VehicleChecklist', backref=db.backref('damage_markers', cascade='all, delete-orphan'))
    
    def __repr__(self):
        return f'<VehicleDamageMarker {self.id} for checklist {self.checklist_id} at ({self.position_x}, {self.position_y})>'








class VehicleMaintenance(db.Model):
    """سجل صيانة المركبات"""
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.Date, nullable=False)  # تاريخ الصيانة
    maintenance_type = db.Column(db.String(30), nullable=False)  # نوع الصيانة: دورية، طارئة، إصلاح، فحص
    description = db.Column(db.String(200), nullable=False)  # وصف الصيانة
    status = db.Column(db.String(20), nullable=False)  # حالة الصيانة: قيد الانتظار، قيد التنفيذ، منجزة، ملغية
    cost = db.Column(db.Float, default=0.0)  # تكلفة الصيانة
    technician = db.Column(db.String(100), nullable=False)  # الفني المسؤول
    receipt_image_url = db.Column(db.String(255))  # رابط صورة الإيصال
    delivery_receipt_url = db.Column(db.String(255))  # رابط إيصال تسليم السيارة للورشة
    pickup_receipt_url = db.Column(db.String(255))  # رابط إيصال استلام السيارة من الورشة
    parts_replaced = db.Column(db.Text)  # قطع الغيار المستبدلة
    actions_taken = db.Column(db.Text)  # الإجراءات المتخذة
    notes = db.Column(db.Text)  # ملاحظات إضافية
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    vehicle = db.relationship('Vehicle', backref=db.backref('maintenance_records', cascade='all, delete-orphan'))
    images = db.relationship('VehicleMaintenanceImage', back_populates='maintenance_record', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<VehicleMaintenance {self.id} {self.maintenance_type} for vehicle {self.vehicle_id}>'


class VehicleMaintenanceImage(db.Model):
    """صور توثيقية لصيانة السيارة"""
    id = db.Column(db.Integer, primary_key=True)
    maintenance_id = db.Column(db.Integer, db.ForeignKey('vehicle_maintenance.id', ondelete='CASCADE'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)  # مسار الصورة
    image_type = db.Column(db.String(20), nullable=False)  # النوع: قبل الصيانة، بعد الصيانة
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    maintenance_record = db.relationship('VehicleMaintenance', back_populates='images')
    
    def __repr__(self):
        return f'<VehicleMaintenanceImage {self.id} for maintenance {self.maintenance_id}>'


class VehicleFuelConsumption(db.Model):
    """تسجيل استهلاك الوقود اليومي للسيارات"""
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id', ondelete='CASCADE'), nullable=False)
    date = db.Column(db.Date, nullable=False)  # تاريخ تعبئة الوقود
    liters = db.Column(db.Float, nullable=False)  # كمية اللترات
    cost = db.Column(db.Float, nullable=False)  # التكلفة الإجمالية
    kilometer_reading = db.Column(db.Integer)  # قراءة عداد المسافة
    driver_name = db.Column(db.String(100))  # اسم السائق
    fuel_type = db.Column(db.String(20), default='بنزين')  # نوع الوقود (بنزين، ديزل، إلخ)
    filling_station = db.Column(db.String(100))  # محطة الوقود
    notes = db.Column(db.Text)  # ملاحظات إضافية
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    vehicle = db.relationship('Vehicle', backref=db.backref('fuel_records', cascade='all, delete-orphan'))
    
    def __repr__(self):
        return f'<VehicleFuelConsumption {self.id} {self.liters} liters for vehicle {self.vehicle_id}>'
    
    @property
    def cost_per_liter(self):
        """حساب تكلفة اللتر الواحد"""
        if self.liters and self.liters > 0:
            return self.cost / self.liters
        return 0


class VehiclePeriodicInspection(db.Model):
    """سجل الفحص الدوري للسيارات"""
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id', ondelete='CASCADE'), nullable=False)
    inspection_date = db.Column(db.Date, nullable=False)  # تاريخ الفحص
    expiry_date = db.Column(db.Date, nullable=False)  # تاريخ انتهاء الفحص
    
    # الحقول الجديدة
    inspection_center = db.Column(db.String(100), nullable=True)  # مركز الفحص
    result = db.Column(db.String(20), nullable=True)  # نتيجة الفحص
    driver_name = db.Column(db.String(100), nullable=True)  # اسم السائق
    supervisor_name = db.Column(db.String(100), nullable=True)  # اسم المشرف
    
    # الحقول القديمة (للتوافق مع قاعدة البيانات الحالية)
    inspection_number = db.Column(db.String(100), nullable=True)  # رقم الفحص (قديم)
    inspector_name = db.Column(db.String(100), nullable=True)  # اسم الفاحص (قديم)
    inspection_type = db.Column(db.String(20), nullable=True)  # نوع الفحص (قديم)
    
    inspection_status = db.Column(db.String(20), default='valid')  # حالة الفحص: ساري، منتهي، على وشك الانتهاء
    cost = db.Column(db.Float, default=0.0)  # تكلفة الفحص
    results = db.Column(db.Text)  # نتائج الفحص
    recommendations = db.Column(db.Text)  # التوصيات
    certificate_file = db.Column(db.String(255))  # مسار ملف شهادة الفحص
    notes = db.Column(db.Text)  # ملاحظات إضافية
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    vehicle = db.relationship('Vehicle', back_populates='periodic_inspections')
    
    def __repr__(self):
        return f'<VehiclePeriodicInspection {self.id} for vehicle {self.vehicle_id} expires on {self.expiry_date}>'
    
    @property
    def is_expired(self):
        """التحقق مما إذا كان الفحص منتهي الصلاحية"""
        return self.expiry_date < datetime.now().date()
    
    @property
    def is_expiring_soon(self):
        """التحقق مما إذا كان الفحص على وشك الانتهاء (خلال 30 يوم)"""
        delta = self.expiry_date - datetime.now().date()
        return 0 <= delta.days <= 30


class VehicleSafetyCheck(db.Model):
    """فحص السلامة للسيارات (يومي، أسبوعي، شهري)"""
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id', ondelete='CASCADE'), nullable=False)
    check_date = db.Column(db.Date, nullable=False)  # تاريخ الفحص
    check_type = db.Column(db.String(20), nullable=False)  # نوع الفحص: يومي، أسبوعي، شهري
    driver_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=True)  # معرف السائق
    driver_name = db.Column(db.String(100), nullable=False)  # اسم السائق
    supervisor_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=True)  # معرف المشرف
    supervisor_name = db.Column(db.String(100), nullable=False)  # اسم المشرف
    status = db.Column(db.String(20), default='completed')  # حالة الفحص: مكتمل، قيد التنفيذ، بحاجة للمراجعة
    check_form_link = db.Column(db.String(255))  # رابط نموذج الفحص
    issues_found = db.Column(db.Boolean, default=False)  # هل تم العثور على مشاكل؟
    issues_description = db.Column(db.Text)  # وصف المشاكل
    actions_taken = db.Column(db.Text)  # الإجراءات المتخذة
    notes = db.Column(db.Text)  # ملاحظات
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    vehicle = db.relationship('Vehicle', back_populates='safety_checks')
    driver = db.relationship('Employee', foreign_keys=[driver_id])
    supervisor = db.relationship('Employee', foreign_keys=[supervisor_id])
    
    def __repr__(self):
        return f'<VehicleSafetyCheck {self.id} {self.check_type} check for vehicle {self.vehicle_id}>'


class VehicleAccident(db.Model):
    """نموذج الحوادث المرورية للمركبات"""
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id', ondelete='CASCADE'), nullable=False)
    accident_date = db.Column(db.Date, nullable=False)  # تاريخ الحادث
    driver_name = db.Column(db.String(100), nullable=False)  # اسم السائق
    accident_status = db.Column(db.String(50), default='قيد المعالجة')  # حالة الحادث: قيد المعالجة، مغلق، معلق، إلخ
    vehicle_condition = db.Column(db.String(100))  # حالة السيارة بعد الحادث
    deduction_amount = db.Column(db.Float, default=0.0)  # مبلغ الخصم على السائق
    deduction_status = db.Column(db.Boolean, default=False)  # هل تم الخصم
    liability_percentage = db.Column(db.Integer, default=0)  # نسبة تحمل السائق للحادث (25%، 50%، 75%، 100%)
    accident_file_link = db.Column(db.String(255))  # رابط ملف الحادث
    location = db.Column(db.String(255))  # موقع الحادث
    description = db.Column(db.Text)  # وصف الحادث
    police_report = db.Column(db.Boolean, default=False)  # هل تم عمل محضر شرطة
    insurance_claim = db.Column(db.Boolean, default=False)  # هل تم رفع مطالبة للتأمين
    notes = db.Column(db.Text)  # ملاحظات إضافية
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    vehicle = db.relationship('Vehicle', back_populates='accidents')
    
    def __repr__(self):
        return f'<VehicleAccident {self.id} for vehicle {self.vehicle_id} on {self.accident_date}>'


class Project(db.Model):
    """نموذج المشاريع"""
    __tablename__ = 'project'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    external_authorizations = db.relationship('ExternalAuthorization', back_populates='project', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Project {self.name}>'

class ExternalAuthorization(db.Model):
    """نموذج التفويضات الخارجية"""
    __tablename__ = 'external_authorization'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)
    project_name = db.Column(db.String(200), nullable=True)  # اسم المشروع/القسم
    authorization_type = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    city = db.Column(db.String(100), nullable=True)  # المدينة
    file_path = db.Column(db.String(255))
    external_link = db.Column(db.String(500))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    vehicle = db.relationship('Vehicle', backref='external_authorizations')
    employee = db.relationship('Employee', backref='external_authorizations')
    project = db.relationship('Project', back_populates='external_authorizations')
    
    def __repr__(self):
        return f'<ExternalAuthorization {self.authorization_type} for {self.employee.name}>'

class AuditLog(db.Model):
    """نموذج سجل المراجعة لتتبع نشاط المستخدمين"""
    __tablename__ = 'audit_log'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)  # create, update, delete, view
    entity_type = db.Column(db.String(50), nullable=False)  # Employee, Department, etc.
    entity_id = db.Column(db.Integer)  # ID of the affected entity
    details = db.Column(db.Text)  # Description of the action
    ip_address = db.Column(db.String(45))  # IP address of the user
    user_agent = db.Column(db.Text)  # User agent string
    previous_data = db.Column(db.Text)  # Previous data (for updates/deletes)
    new_data = db.Column(db.Text)  # New data (for creates/updates)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # العلاقات
    user = db.relationship('User', backref='audit_logs')
    
    def __repr__(self):
        return f'<AuditLog {self.action} {self.entity_type} by {self.user_id}>'



class VehicleExternalSafetyCheck(db.Model):
    """فحوصات السلامة الخارجية للسيارات"""
    __tablename__ = 'vehicle_external_safety_check'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id', ondelete='CASCADE'), nullable=False)
    
    # بيانات السائق
    driver_name = db.Column(db.String(100), nullable=False)  # اسم السائق
    driver_national_id = db.Column(db.String(20), nullable=False)  # رقم الهوية
    driver_department = db.Column(db.String(100), nullable=False)  # القسم
    driver_city = db.Column(db.String(100), nullable=False)  # المدينة
    
    # بيانات السيارة (محملة تلقائياً)
    vehicle_plate_number = db.Column(db.String(20), nullable=False)  # رقم اللوحة
    vehicle_make_model = db.Column(db.String(100), nullable=False)  # النوع والموديل
    current_delegate = db.Column(db.String(100), nullable=True)  # المفوض الحالي
    
    # تاريخ ووقت الفحص
    inspection_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # حالة الاعتماد
    approval_status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # المعتمد من قبل
    approved_at = db.Column(db.DateTime, nullable=True)  # تاريخ الاعتماد
    rejection_reason = db.Column(db.Text, nullable=True)  # سبب الرفض
    
    # ملاحظات عامة
    notes = db.Column(db.Text)  # ملاحظات إضافية
    
    # معلومات النظام
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    vehicle = db.relationship('Vehicle', backref=db.backref('external_safety_checks', cascade='all, delete-orphan'))
    approver = db.relationship('User', foreign_keys=[approved_by])
    safety_images = db.relationship('VehicleSafetyImage', back_populates='safety_check', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<VehicleExternalSafetyCheck {self.vehicle_plate_number} by {self.driver_name}>'
        
    @property
    def is_approved(self):
        return self.approval_status == 'approved'
    
    @property
    def is_pending(self):
        return self.approval_status == 'pending'
    
    @property
    def is_rejected(self):
        return self.approval_status == 'rejected'


class VehicleSafetyImage(db.Model):
    """صور فحوصات السلامة"""
    __tablename__ = 'vehicle_safety_image'
    
    id = db.Column(db.Integer, primary_key=True)
    safety_check_id = db.Column(db.Integer, db.ForeignKey('vehicle_external_safety_check.id', ondelete='CASCADE'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)  # مسار الصورة
    image_description = db.Column(db.String(200), nullable=True)  # وصف الصورة (اختياري)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    safety_check = db.relationship('VehicleExternalSafetyCheck', back_populates='safety_images')
    
    def __repr__(self):
        return f'<VehicleSafetyImage {self.safety_check_id}>'


class SafetyInspection(db.Model):
    """نموذج فحص السلامة - نسخة مبسطة للاستخدام في routes/external_safety.py"""
    __tablename__ = 'safety_inspection'
    
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id', ondelete='CASCADE'), nullable=False)
    employee_id = db.Column(db.String(20), nullable=False)  # رقم الموظف
    driver_name = db.Column(db.String(100), nullable=False)
    
    # معلومات الفحص
    inspection_date = db.Column(db.DateTime, default=datetime.utcnow)
    issues_found = db.Column(db.Text)  # المشاكل المكتشفة
    recommendations = db.Column(db.Text)  # التوصيات
    
    # الصور المرفقة
    images = db.Column(db.Text)  # قائمة بمسارات الصور (JSON)
    
    # حالة الموافقة
    approval_status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    admin_notes = db.Column(db.Text)  # ملاحظات الإدارة
    approved_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    approved_at = db.Column(db.DateTime, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    vehicle = db.relationship('Vehicle', backref='safety_inspections')
    approver = db.relationship('User', foreign_keys=[approved_by])
    
    def __repr__(self):
        return f'<SafetyInspection {self.vehicle_id} by {self.driver_name}>'



class OperationRequest(db.Model):
    """نموذج لتتبع جميع العمليات التي تحتاج موافقة إدارية"""
    __tablename__ = "operation_requests"
    
    id = db.Column(db.Integer, primary_key=True)
    
    # نوع العملية
    operation_type = db.Column(db.String(50), nullable=False)  # handover, workshop, external_authorization, safety_inspection
    
    # معرف السجل المرتبط بالعملية
    related_record_id = db.Column(db.Integer, nullable=False)
    
    # معرف السيارة
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicle.id", ondelete="CASCADE"), nullable=False)
    
    # معلومات العملية
    title = db.Column(db.String(200), nullable=False)  # عنوان العملية
    description = db.Column(db.Text)  # وصف العملية
    
    # معلومات الطالب
    requested_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # حالة العملية
    status = db.Column(db.String(20), default="pending")  # pending, approved, rejected, under_review
    
    # معلومات المراجع
    reviewed_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    review_notes = db.Column(db.Text)  # ملاحظات المراجع
    
    # أولوية العملية
    priority = db.Column(db.String(20), default="normal")  # low, normal, high, urgent
    
    # تواريخ النظام
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    vehicle = db.relationship("Vehicle", backref="operation_requests")
    requester = db.relationship("User", foreign_keys=[requested_by], backref="operation_requests")
    reviewer = db.relationship("User", foreign_keys=[reviewed_by], backref="reviewed_operations")
    
    def get_related_record(self):
        """جلب السجل المرتبط بالعملية حسب نوعها"""
        if self.operation_type == "handover":
            return VehicleHandover.query.get(self.related_record_id)
        elif self.operation_type == "workshop" or self.operation_type == "workshop_record":
            return VehicleWorkshop.query.get(self.related_record_id)
        elif self.operation_type == "external_authorization":
            return ExternalAuthorization.query.get(self.related_record_id)
        elif self.operation_type == "safety_inspection":
            return SafetyInspection.query.get(self.related_record_id)
        return None
    
    def get_operation_url(self):
        """الحصول على رابط تعديل تواريخ الوثائق للسيارة الخاصة بالعملية"""
        # توجيه جميع العمليات إلى صفحة تعديل تواريخ الوثائق مباشرة
        return f"/vehicles/documents/edit/{self.vehicle_id}"
    
    def __repr__(self):
        return f"<OperationRequest {self.operation_type} for Vehicle {self.vehicle_id}>"


class OperationNotification(db.Model):
    """نموذج للإشعارات المرتبطة بالعمليات"""
    __tablename__ = "operation_notifications"
    
    id = db.Column(db.Integer, primary_key=True)
    
    # معرف العملية
    operation_request_id = db.Column(db.Integer, db.ForeignKey("operation_requests.id", ondelete="CASCADE"), nullable=False)
    
    # معرف المستلم
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    
    # نوع الإشعار
    notification_type = db.Column(db.String(50), nullable=False)  # new_operation, status_change, reminder
    
    # محتوى الإشعار
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    
    # حالة الإشعار
    is_read = db.Column(db.Boolean, default=False)
    is_sent = db.Column(db.Boolean, default=False)
    
    # تواريخ النظام
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime, nullable=True)
    
    # العلاقات
    operation_request = db.relationship("OperationRequest", backref="notifications")
    user = db.relationship("User", backref="notifications")
    
    def __repr__(self):
        return f"<OperationNotification {self.title} to {self.user_id}>"


class MobileDevice(db.Model):
    """نموذج لإدارة الأجهزة المحمولة والهواتف"""
    __tablename__ = 'mobile_devices'
    
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), nullable=False)  # رقم الهاتف
    imei = db.Column(db.String(20), unique=True, nullable=False)  # رقم الـ IMEI فريد
    email = db.Column(db.String(100), nullable=True)  # الإيميل المرتبط بالجهاز
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id', ondelete='SET NULL'), nullable=True)  # معرف الموظف
    device_model = db.Column(db.String(50), nullable=True)  # نوع الجهاز
    device_brand = db.Column(db.String(50), nullable=True)  # ماركة الجهاز
    status = db.Column(db.String(20), default='متاح', nullable=False)  # حالة الجهاز: متاح، مرتبط، معطل
    assigned_date = db.Column(db.DateTime, nullable=True)  # تاريخ الربط
    notes = db.Column(db.Text, nullable=True)  # ملاحظات إضافية
    
    # تواريخ النظام
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    employee = db.relationship('Employee', backref='mobile_devices', lazy=True)
    
    def __repr__(self):
        return f'<MobileDevice {self.imei} - {self.phone_number}>'
    
    @property
    def is_available(self):
        """تحقق من توفر الجهاز للتخصيص"""
        if self.status == 'معطل':
            return False
        if self.employee_id is None:
            return True
        # تحقق من حالة الموظف
        if self.employee and self.employee.status != 'نشط':
            return True
        return False
    
    @property
    def status_class(self):
        """إرجاع كلاس CSS حسب الحالة"""
        status_classes = {
            'متاح': 'success',
            'مرتبط': 'primary', 
            'معطل': 'danger'
        }
        return status_classes.get(self.status, 'secondary')


class SimCard(db.Model):
    """نموذج لإدارة بطائق SIM والأرقام"""
    __tablename__ = 'sim_cards'
    
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), nullable=False, unique=True)  # رقم الهاتف
    carrier = db.Column(db.String(50), nullable=False)  # شركة الاتصالات: STC, موبايلي, زين
    status = db.Column(db.String(20), default='متاحة', nullable=False)  # متاحة، نشطة، موقوفة، مرتبطة
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id', ondelete='SET NULL'), nullable=True)
    device_id = db.Column(db.Integer, db.ForeignKey('mobile_devices.id', ondelete='SET NULL'), nullable=True)
    
    # معلومات إضافية
    description = db.Column(db.String(200), nullable=True)  # وصف الرقم
    activation_date = db.Column(db.Date, nullable=True)  # تاريخ التفعيل
    monthly_cost = db.Column(db.Float, default=0.0)  # التكلفة الشهرية
    plan_type = db.Column(db.String(100), nullable=True)  # نوع الباقة
    
    # تواريخ النظام
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    assigned_date = db.Column(db.DateTime, nullable=True)  # تاريخ الربط
    
    # العلاقات
    employee = db.relationship('Employee', backref='sim_cards', lazy=True)
    device = db.relationship('MobileDevice', backref='sim_cards', lazy=True)
    
    def __repr__(self):
        return f'<SimCard {self.phone_number} - {self.carrier}>'
    
    @property
    def is_available(self):
        """تحقق من توفر الرقم للتخصيص"""
        if self.status in ['موقوفة', 'معطلة']:
            return False
        if self.employee_id is None and self.device_id is None:
            return True
        # تحقق من حالة الموظف إذا كان مربوط
        if self.employee and self.employee.status != 'نشط':
            return True
        return False
    
    @property
    def status_class(self):
        """إرجاع كلاس CSS حسب الحالة"""
        status_classes = {
            'متاحة': 'success',
            'نشطة': 'primary',
            'موقوفة': 'warning',
            'مرتبطة': 'info',
            'معطلة': 'danger'
        }
        return status_classes.get(self.status, 'secondary')

class ImportedPhoneNumber(db.Model):
    """نموذج لتخزين أرقام الهواتف المستوردة من Excel"""
    __tablename__ = 'imported_phone_numbers'
    
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), nullable=False)  # رقم الهاتف المستورد
    description = db.Column(db.String(100), nullable=True)  # وصف أو اسم صاحب الرقم
    is_used = db.Column(db.Boolean, default=False, nullable=False)  # هل تم استخدام الرقم أم لا
    imported_by = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'), nullable=True)  # المستخدم الذي استورد الرقم
    
    # تواريخ النظام
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    user = db.relationship('User', backref='imported_phone_numbers', lazy=True)
    
    def __repr__(self):
        return f'<ImportedPhoneNumber {self.phone_number}>'
    
    def mark_as_used(self):
        """تحديد الرقم كمستخدم"""
        self.is_used = True
        self.updated_at = datetime.utcnow()
        db.session.commit()
    
    @staticmethod
    def get_available_numbers():
        """جلب الأرقام المتاحة (غير المستخدمة)"""
        return ImportedPhoneNumber.query.filter_by(is_used=False).order_by(ImportedPhoneNumber.phone_number).all()


# نموذج ربط الأجهزة والأرقام بالموظفين
class DeviceAssignment(db.Model):
    """نموذج لتسجيل عمليات ربط الأجهزة والأرقام بالموظفين"""
    __tablename__ = 'device_assignments'
    
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id', ondelete='CASCADE'), nullable=False)
    device_id = db.Column(db.Integer, db.ForeignKey('mobile_devices.id', ondelete='SET NULL'), nullable=True)
    sim_id = db.Column(db.Integer, db.ForeignKey('sim_cards.id', ondelete='SET NULL'), nullable=True)
    
    # معلومات الربط
    assignment_type = db.Column(db.String(50), nullable=False)  # device_only, sim_only, device_and_sim
    assignment_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    unassignment_date = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # معلومات إضافية
    assigned_by = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='SET NULL'), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    reason = db.Column(db.String(200), nullable=True)  # سبب الربط أو فك الربط
    
    # تواريخ النظام
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # العلاقات
    employee = db.relationship('Employee', backref='device_assignments', lazy=True)
    device = db.relationship('MobileDevice', backref='assignments', lazy=True)
    sim_card = db.relationship('SimCard', backref='assignments', lazy=True)
    assigned_by_user = db.relationship('User', backref='assigned_devices', lazy=True)
    
    def __repr__(self):
        return f'<DeviceAssignment {self.employee_id} - {self.assignment_type}>'
    
    def unassign(self, reason=None):
        """فك ربط الجهاز/الرقم"""
        self.is_active = False
        self.unassignment_date = datetime.utcnow()
        self.reason = reason
        self.updated_at = datetime.utcnow()
        
        # تحديث حالة الجهاز والرقم
        if self.device:
            self.device.employee_id = None
            self.device.status = 'متاح'
        if self.sim_card:
            self.sim_card.employee_id = None
            self.sim_card.device_id = None
            self.sim_card.status = 'متاحة'

