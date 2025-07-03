"""
مسارات إدارة الموظفين
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required
from models import Employee, Department, db
from datetime import datetime
import os

employees_bp = Blueprint('employees', __name__, url_prefix='/employees')

@employees_bp.route('/')
@login_required
def index():
    """صفحة عرض جميع الموظفين"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    department_id = request.args.get('department', '', type=str)
    
    query = Employee.query
    
    if search:
        query = query.filter(Employee.name.contains(search))
    
    if department_id:
        query = query.filter(Employee.department_id == department_id)
    
    employees = query.paginate(
        page=page, per_page=20, error_out=False
    )
    
    departments = Department.query.all()
    
    return render_template('employees/index.html', 
                         employees=employees, 
                         departments=departments,
                         search=search,
                         department_id=department_id)

@employees_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    """إضافة موظف جديد"""
    if request.method == 'POST':
        employee = Employee(
            name=request.form['name'],
            email=request.form['email'],
            phone=request.form['phone'],
            national_id=request.form['national_id'],
            department_id=request.form['department_id'],
            position=request.form['position'],
            hire_date=datetime.strptime(request.form['hire_date'], '%Y-%m-%d').date(),
            salary=float(request.form['salary'])
        )
        
        try:
            db.session.add(employee)
            db.session.commit()
            flash('تم إضافة الموظف بنجاح', 'success')
            return redirect(url_for('employees.index'))
        except Exception as e:
            db.session.rollback()
            flash('خطأ في إضافة الموظف', 'error')
    
    departments = Department.query.all()
    return render_template('employees/new.html', departments=departments)

@employees_bp.route('/<int:id>')
@login_required
def show(id):
    """عرض تفاصيل موظف"""
    employee = Employee.query.get_or_404(id)
    return render_template('employees/show.html', employee=employee)

@employees_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """تعديل موظف"""
    employee = Employee.query.get_or_404(id)
    
    if request.method == 'POST':
        employee.name = request.form['name']
        employee.email = request.form['email']
        employee.phone = request.form['phone']
        employee.national_id = request.form['national_id']
        employee.department_id = request.form['department_id']
        employee.position = request.form['position']
        employee.hire_date = datetime.strptime(request.form['hire_date'], '%Y-%m-%d').date()
        employee.salary = float(request.form['salary'])
        
        try:
            db.session.commit()
            flash('تم تحديث الموظف بنجاح', 'success')
            return redirect(url_for('employees.show', id=id))
        except Exception as e:
            db.session.rollback()
            flash('خطأ في تحديث الموظف', 'error')
    
    departments = Department.query.all()
    return render_template('employees/edit.html', employee=employee, departments=departments)

@employees_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """حذف موظف"""
    employee = Employee.query.get_or_404(id)
    
    try:
        db.session.delete(employee)
        db.session.commit()
        flash('تم حذف الموظف بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash('خطأ في حذف الموظف', 'error')
    
    return redirect(url_for('employees.index'))