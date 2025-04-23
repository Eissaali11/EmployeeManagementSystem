from datetime import datetime
from flask_login import UserMixin
from app import db
import enum

class Department(db.Model):
    """Department model for organizing employees"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    manager_id = db.Column(db.Integer, db.ForeignKey('employee.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    employees = db.relationship('Employee', back_populates='department', foreign_keys='Employee.department_id')
    manager = db.relationship('Employee', foreign_keys=[manager_id], uselist=False)
    
    def __repr__(self):
        return f'<Department {self.name}>'

class Employee(db.Model):
    """Employee model with all required personal and professional information"""
    id = db.Column(db.Integer, primary_key=True)
    employee_id = db.Column(db.String(20), unique=True, nullable=False)  # Internal employee ID
    national_id = db.Column(db.String(20), unique=True, nullable=False)  # National ID number
    name = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100))
    job_title = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='active')  # active, inactive, on_leave
    location = db.Column(db.String(100))
    project = db.Column(db.String(100))
    department_id = db.Column(db.Integer, db.ForeignKey('department.id', ondelete='SET NULL'), nullable=True)
    join_date = db.Column(db.Date)
    nationality = db.Column(db.String(50))  # جنسية الموظف
    contract_type = db.Column(db.String(20), default='foreign')  # سعودي / وافد - saudi / foreign
    basic_salary = db.Column(db.Float, default=0.0)  # الراتب الأساسي
    has_national_balance = db.Column(db.Boolean, default=False)  # هل يتوفر توازن وطني
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    department = db.relationship('Department', back_populates='employees', foreign_keys=[department_id])
    attendances = db.relationship('Attendance', back_populates='employee', cascade='all, delete-orphan')
    salaries = db.relationship('Salary', back_populates='employee', cascade='all, delete-orphan')
    documents = db.relationship('Document', back_populates='employee', cascade='all, delete-orphan')
    
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
    issue_date = db.Column(db.Date, nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)
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
    MANAGE = 0x10          # إدارة القسم الخاص
    ADMIN = 0xff           # كل الصلاحيات

# صلاحيات الأقسام
class Module(enum.Enum):
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
    name = db.Column(db.String(100))
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
    
    # العلاقة مع صلاحيات المستخدم
    permissions = db.relationship('UserPermission', back_populates='user', cascade='all, delete-orphan')
    
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
        
    def has_module_access(self, module):
        """التحقق مما إذا كان المستخدم لديه وصول إلى وحدة معينة"""
        # المديرون لديهم وصول إلى جميع الوحدات
        if self.role == UserRole.ADMIN:
            return True
            
        return any(p.module == module for p in self.permissions)
    
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


class VehicleHandover(db.Model):
    """نموذج تسليم واستلام السيارة"""
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id', ondelete='CASCADE'), nullable=False)
    handover_type = db.Column(db.String(20), nullable=False)  # النوع: تسليم، استلام
    handover_date = db.Column(db.Date, nullable=False)  # تاريخ التسليم/الاستلام
    person_name = db.Column(db.String(100), nullable=False)  # اسم الشخص المستلم/المسلم
    vehicle_condition = db.Column(db.Text, nullable=False)  # حالة السيارة عند التسليم/الاستلام
    fuel_level = db.Column(db.String(20), nullable=False)  # مستوى الوقود
    mileage = db.Column(db.Integer, nullable=False)  # عداد الكيلومترات
    has_spare_tire = db.Column(db.Boolean, default=True)  # وجود إطار احتياطي
    has_fire_extinguisher = db.Column(db.Boolean, default=True)  # وجود طفاية حريق
    has_first_aid_kit = db.Column(db.Boolean, default=True)  # وجود حقيبة إسعافات أولية
    has_warning_triangle = db.Column(db.Boolean, default=True)  # وجود مثلث تحذيري
    has_tools = db.Column(db.Boolean, default=True)  # وجود أدوات
    form_link = db.Column(db.String(255))  # رابط فورم التسليم/الاستلام
    notes = db.Column(db.Text)  # ملاحظات إضافية
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    vehicle = db.relationship('Vehicle', back_populates='handover_records')
    images = db.relationship('VehicleHandoverImage', back_populates='handover_record', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<VehicleHandover {self.vehicle_id} {self.handover_type} {self.handover_date}>'


class VehicleHandoverImage(db.Model):
    """صور توثيقية لحالة السيارة عند التسليم/الاستلام"""
    id = db.Column(db.Integer, primary_key=True)
    handover_record_id = db.Column(db.Integer, db.ForeignKey('vehicle_handover.id', ondelete='CASCADE'), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)  # مسار الصورة
    image_description = db.Column(db.String(100))  # وصف الصورة
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # العلاقات
    handover_record = db.relationship('VehicleHandover', back_populates='images')
    
    def __repr__(self):
        return f'<VehicleHandoverImage {self.handover_record_id}>'


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
    inspection_number = db.Column(db.String(50), nullable=False)  # رقم الفحص
    inspector_name = db.Column(db.String(100), nullable=False)  # اسم الفاحص أو مركز الفحص
    inspection_type = db.Column(db.String(50), nullable=False)  # نوع الفحص: فني، دوري، أمان
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


