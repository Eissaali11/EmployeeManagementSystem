from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy.exc import IntegrityError
from app import db
from models import Department, Employee, SystemAudit

departments_bp = Blueprint('departments', __name__)

@departments_bp.route('/')
def index():
    """List all departments"""
    departments = Department.query.all()
    return render_template('departments/index.html', departments=departments)

@departments_bp.route('/create', methods=['GET', 'POST'])
def create():
    """Create a new department"""
    if request.method == 'POST':
        try:
            name = request.form['name']
            description = request.form.get('description', '')
            manager_id = request.form.get('manager_id')
            
            # Convert empty manager_id to None
            if manager_id == '':
                manager_id = None
            
            department = Department(
                name=name,
                description=description,
                manager_id=manager_id
            )
            
            db.session.add(department)
            db.session.commit()
            
            # Log the action
            audit = SystemAudit(
                action='create',
                entity_type='department',
                entity_id=department.id,
                details=f'تم إنشاء قسم جديد: {name}'
            )
            db.session.add(audit)
            db.session.commit()
            
            flash('تم إنشاء القسم بنجاح', 'success')
            return redirect(url_for('departments.index'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ: {str(e)}', 'danger')
    
    # Get all employees for manager selection
    employees = Employee.query.filter_by(status='active').all()
    return render_template('departments/create.html', employees=employees)

@departments_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    """Edit an existing department"""
    department = Department.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            department.name = request.form['name']
            department.description = request.form.get('description', '')
            
            manager_id = request.form.get('manager_id')
            department.manager_id = None if manager_id == '' else manager_id
            
            db.session.commit()
            
            # Log the action
            audit = SystemAudit(
                action='update',
                entity_type='department',
                entity_id=department.id,
                details=f'تم تحديث بيانات القسم: {department.name}'
            )
            db.session.add(audit)
            db.session.commit()
            
            flash('تم تحديث بيانات القسم بنجاح', 'success')
            return redirect(url_for('departments.index'))
        
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ: {str(e)}', 'danger')
    
    employees = Employee.query.filter_by(status='active').all()
    return render_template('departments/edit.html', department=department, employees=employees)

@departments_bp.route('/<int:id>/view')
def view(id):
    """View department details and its employees"""
    department = Department.query.get_or_404(id)
    employees = Employee.query.filter_by(department_id=id).all()
    return render_template('departments/view.html', department=department, employees=employees)

@departments_bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    """Delete a department"""
    department = Department.query.get_or_404(id)
    name = department.name
    
    try:
        # Check if department has employees
        employees = Employee.query.filter_by(department_id=id).count()
        if employees > 0:
            flash(f'لا يمكن حذف القسم لأنه يحتوي على {employees} موظف', 'danger')
            return redirect(url_for('departments.index'))
        
        db.session.delete(department)
        
        # Log the action
        audit = SystemAudit(
            action='delete',
            entity_type='department',
            entity_id=id,
            details=f'تم حذف القسم: {name}'
        )
        db.session.add(audit)
        db.session.commit()
        
        flash('تم حذف القسم بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء حذف القسم: {str(e)}', 'danger')
    
    return redirect(url_for('departments.index'))
