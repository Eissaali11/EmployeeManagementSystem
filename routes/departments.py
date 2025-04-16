from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy.exc import IntegrityError
from app import db
from models import Department, Employee, SystemAudit
from utils.excel import parse_employee_excel

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

@departments_bp.route('/<int:id>/import_employees', methods=['GET', 'POST'])
def import_employees(id):
    """Import employees for specific department from Excel file"""
    department = Department.query.get_or_404(id)
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('لم يتم اختيار ملف', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('لم يتم اختيار ملف', 'danger')
            return redirect(request.url)
        
        if file and file.filename.endswith(('.xlsx', '.xls')):
            try:
                # Parse Excel file
                employees_data = parse_employee_excel(file)
                
                success_count = 0
                error_count = 0
                error_details = []
                
                for index, data in enumerate(employees_data):
                    try:
                        # Add department_id to employee data
                        data['department_id'] = id
                        
                        # Sanitize strings to ensure they're valid UTF-8
                        for key, value in data.items():
                            if isinstance(value, str):
                                # Replace any problematic characters that might cause encoding issues
                                data[key] = value.encode('utf-8', errors='replace').decode('utf-8')
                        
                        # Check if employee with same employee_id already exists - safely
                        try:
                            employee_id = data.get('employee_id', '')
                            existing = Employee.query.filter_by(employee_id=employee_id).first()
                            if existing:
                                error_count += 1
                                error_details.append(f"الموظف برقم {employee_id} موجود مسبقا")
                                continue
                        except Exception as e:
                            print(f"Error checking employee_id: {str(e)}")
                            # Continue processing even if there's an error here
                            
                        # Check if employee with same national_id already exists - safely  
                        try:
                            national_id = data.get('national_id', '')
                            existing = Employee.query.filter_by(national_id=national_id).first()
                            if existing:
                                error_count += 1
                                error_details.append(f"الموظف برقم هوية {national_id} موجود مسبقا")
                                continue
                        except Exception as e:
                            print(f"Error checking national_id: {str(e)}")
                            # Continue processing even if there's an error here
                        
                        # Create and save employee
                        employee = Employee(**data)
                        db.session.add(employee)
                        db.session.commit()
                        success_count += 1
                    except Exception as e:
                        db.session.rollback()
                        error_count += 1
                        error_details.append(f"خطأ في السجل {index+1}: {str(e)}")
                
                # Log the import
                error_detail_str = ", ".join(error_details[:5])
                if len(error_details) > 5:
                    error_detail_str += f" وغيرها من الأخطاء..."
                
                details = f'تم استيراد {success_count} موظف بنجاح لقسم {department.name} و {error_count} فشل'
                if error_details:
                    details += f". أخطاء: {error_detail_str}"
                    
                audit = SystemAudit(
                    action='import',
                    entity_type='employee',
                    entity_id=id,
                    details=details
                )
                db.session.add(audit)
                db.session.commit()
                
                if error_count > 0:
                    flash(f'تم استيراد {success_count} موظف بنجاح و {error_count} فشل. {error_detail_str}', 'warning')
                else:
                    flash(f'تم استيراد {success_count} موظف بنجاح', 'success')
                return redirect(url_for('departments.view', id=id))
            except Exception as e:
                flash(f'حدث خطأ أثناء استيراد الملف: {str(e)}', 'danger')
        else:
            flash('الملف يجب أن يكون بصيغة Excel (.xlsx, .xls)', 'danger')
    
    return render_template('departments/import_employees.html', department=department)

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
