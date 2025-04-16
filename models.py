from datetime import datetime
from flask_login import UserMixin
from app import db

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

class User(UserMixin, db.Model):
    """User model for authentication"""
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100))
    firebase_uid = db.Column(db.String(128), unique=True, nullable=False)
    profile_picture = db.Column(db.String(255))
    role = db.Column(db.String(20), default='user')  # admin, manager, user
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # الربط مع الموظف إذا كان المستخدم موظفًا في النظام
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=True)
    employee = db.relationship('Employee', foreign_keys=[employee_id], uselist=False)
    
    def __repr__(self):
        return f'<User {self.email}>'

class SystemAudit(db.Model):
    """Audit trail for significant system actions"""
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(100), nullable=False)
    entity_type = db.Column(db.String(50), nullable=False)  # employee, department, salary, etc.
    entity_id = db.Column(db.Integer, nullable=False)
    details = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    # إضافة مرجع للمستخدم الذي قام بالإجراء
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    user = db.relationship('User', foreign_keys=[user_id])
    
    def __repr__(self):
        return f'<SystemAudit {self.action} on {self.entity_type} #{self.entity_id}>'
