"""
مسارات إدارة الأقسام
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from models import Department, Employee, db

departments_bp = Blueprint('departments', __name__, url_prefix='/departments')

@departments_bp.route('/')
@login_required
def index():
    """صفحة عرض جميع الأقسام"""
    departments = Department.query.all()
    return render_template('departments/index.html', departments=departments)

@departments_bp.route('/new', methods=['GET', 'POST'])
@login_required
def new():
    """إضافة قسم جديد"""
    if request.method == 'POST':
        department = Department(
            name=request.form['name'],
            description=request.form.get('description'),
            manager_id=request.form.get('manager_id') if request.form.get('manager_id') else None
        )
        
        try:
            db.session.add(department)
            db.session.commit()
            flash('تم إضافة القسم بنجاح', 'success')
            return redirect(url_for('departments.index'))
        except Exception as e:
            db.session.rollback()
            flash('خطأ في إضافة القسم', 'error')
    
    employees = Employee.query.all()
    return render_template('departments/new.html', employees=employees)

@departments_bp.route('/<int:id>')
@login_required
def show(id):
    """عرض تفاصيل قسم"""
    department = Department.query.get_or_404(id)
    employees = Employee.query.filter_by(department_id=id).all()
    return render_template('departments/show.html', department=department, employees=employees)

@departments_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """تعديل قسم"""
    department = Department.query.get_or_404(id)
    
    if request.method == 'POST':
        department.name = request.form['name']
        department.description = request.form.get('description')
        department.manager_id = request.form.get('manager_id') if request.form.get('manager_id') else None
        
        try:
            db.session.commit()
            flash('تم تحديث القسم بنجاح', 'success')
            return redirect(url_for('departments.show', id=id))
        except Exception as e:
            db.session.rollback()
            flash('خطأ في تحديث القسم', 'error')
    
    employees = Employee.query.all()
    return render_template('departments/edit.html', department=department, employees=employees)

@departments_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """حذف قسم"""
    department = Department.query.get_or_404(id)
    
    # التحقق من وجود موظفين في القسم
    if department.employees:
        flash('لا يمكن حذف القسم لوجود موظفين فيه', 'error')
        return redirect(url_for('departments.index'))
    
    try:
        db.session.delete(department)
        db.session.commit()
        flash('تم حذف القسم بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash('خطأ في حذف القسم', 'error')
    
    return redirect(url_for('departments.index'))