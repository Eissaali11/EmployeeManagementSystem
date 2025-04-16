import os
import pandas as pd
from io import BytesIO
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from werkzeug.utils import secure_filename
from sqlalchemy.exc import IntegrityError
from app import db
from models import Employee, Department, SystemAudit, Document, Attendance, Salary
from utils.excel import parse_employee_excel, generate_employee_excel
from utils.date_converter import parse_date

employees_bp = Blueprint('employees', __name__)

@employees_bp.route('/')
def index():
    """List all employees"""
    employees = Employee.query.all()
    return render_template('employees/index.html', employees=employees)

@employees_bp.route('/create', methods=['GET', 'POST'])
def create():
    """Create a new employee"""
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form['name']
            employee_id = request.form['employee_id']
            national_id = request.form['national_id']
            mobile = request.form['mobile']
            status = request.form['status']
            job_title = request.form['job_title']
            location = request.form['location']
            project = request.form['project']
            email = request.form.get('email', '')
            department_id = request.form.get('department_id', None)
            join_date = parse_date(request.form.get('join_date', ''))
            
            # Convert empty department_id to None
            if department_id == '':
                department_id = None
                
            # Create new employee
            employee = Employee(
                name=name,
                employee_id=employee_id,
                national_id=national_id,
                mobile=mobile,
                status=status,
                job_title=job_title,
                location=location,
                project=project,
                email=email,
                department_id=department_id,
                join_date=join_date
            )
            
            db.session.add(employee)
            db.session.commit()
            
            # Log the action
            audit = SystemAudit(
                action='create',
                entity_type='employee',
                entity_id=employee.id,
                details=f'تم إنشاء موظف جديد: {name}'
            )
            db.session.add(audit)
            db.session.commit()
            
            flash('تم إنشاء الموظف بنجاح', 'success')
            return redirect(url_for('employees.index'))
        
        except IntegrityError:
            db.session.rollback()
            flash('هناك خطأ في البيانات. قد يكون رقم الموظف أو رقم الهوية موجود مسبقًا', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ: {str(e)}', 'danger')
    
    # Get all departments for the dropdown
    departments = Department.query.all()
    return render_template('employees/create.html', departments=departments)

@employees_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    """Edit an existing employee"""
    employee = Employee.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # Update employee data
            employee.name = request.form['name']
            employee.employee_id = request.form['employee_id']
            employee.national_id = request.form['national_id']
            employee.mobile = request.form['mobile']
            employee.status = request.form['status']
            employee.job_title = request.form['job_title']
            employee.location = request.form['location']
            employee.project = request.form['project']
            employee.email = request.form.get('email', '')
            
            department_id = request.form.get('department_id', None)
            employee.department_id = None if department_id == '' else department_id
            
            join_date = request.form.get('join_date', '')
            if join_date:
                employee.join_date = parse_date(join_date)
            
            db.session.commit()
            
            # Log the action
            audit = SystemAudit(
                action='update',
                entity_type='employee',
                entity_id=employee.id,
                details=f'تم تحديث بيانات الموظف: {employee.name}'
            )
            db.session.add(audit)
            db.session.commit()
            
            flash('تم تحديث بيانات الموظف بنجاح', 'success')
            return redirect(url_for('employees.index'))
        
        except IntegrityError:
            db.session.rollback()
            flash('هناك خطأ في البيانات. قد يكون رقم الموظف أو رقم الهوية موجود مسبقًا', 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ: {str(e)}', 'danger')
    
    departments = Department.query.all()
    return render_template('employees/edit.html', employee=employee, departments=departments)

@employees_bp.route('/<int:id>/view')
def view(id):
    """View detailed employee information"""
    employee = Employee.query.get_or_404(id)
    
    # Get employee documents
    documents = Document.query.filter_by(employee_id=id).all()
    
    # Get document types in Arabic
    document_types_map = {
        'national_id': 'الهوية الوطنية', 
        'passport': 'جواز السفر', 
        'health_certificate': 'الشهادة الصحية', 
        'work_permit': 'تصريح العمل', 
        'education_certificate': 'الشهادة الدراسية',
        'driving_license': 'رخصة القيادة',
        'annual_leave': 'الإجازة السنوية',
        'other': 'أخرى'
    }
    
    # Get documents by type for easier display
    documents_by_type = {}
    for doc_type in document_types_map.keys():
        documents_by_type[doc_type] = None
    
    today = datetime.now().date()
    
    for doc in documents:
        # Add expiry status
        days_to_expiry = (doc.expiry_date - today).days
        if days_to_expiry < 0:
            doc.status_class = "danger"
            doc.status_text = "منتهية"
        elif days_to_expiry < 30:
            doc.status_class = "warning"
            doc.status_text = f"تنتهي خلال {days_to_expiry} يوم"
        else:
            doc.status_class = "success"
            doc.status_text = "سارية"
        
        # Store document by type
        documents_by_type[doc.document_type] = doc
    
    # Get attendance records
    attendances = Attendance.query.filter_by(employee_id=id).order_by(Attendance.date.desc()).limit(30).all()
    
    # Get salary records
    salaries = Salary.query.filter_by(employee_id=id).order_by(Salary.year.desc(), Salary.month.desc()).all()
    
    return render_template('employees/view.html', 
                          employee=employee, 
                          documents=documents,
                          documents_by_type=documents_by_type,
                          document_types_map=document_types_map,
                          attendances=attendances,
                          salaries=salaries)

@employees_bp.route('/<int:id>/delete', methods=['POST'])
def delete(id):
    """Delete an employee"""
    employee = Employee.query.get_or_404(id)
    name = employee.name
    
    try:
        db.session.delete(employee)
        
        # Log the action
        audit = SystemAudit(
            action='delete',
            entity_type='employee',
            entity_id=id,
            details=f'تم حذف الموظف: {name}'
        )
        db.session.add(audit)
        db.session.commit()
        
        flash('تم حذف الموظف بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء حذف الموظف: {str(e)}', 'danger')
    
    return redirect(url_for('employees.index'))

@employees_bp.route('/import', methods=['GET', 'POST'])
def import_excel():
    """Import employees from Excel file"""
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
                print(f"Received file: {file.filename}")
                
                # Parse Excel file
                employees_data = parse_employee_excel(file)
                print(f"Parsed {len(employees_data)} employee records from Excel")
                
                success_count = 0
                error_count = 0
                error_details = []
                
                for index, data in enumerate(employees_data):
                    try:
                        print(f"Processing employee {index+1}: {data.get('name', 'Unknown')}")
                        
                        # Check if employee with same employee_id already exists
                        existing = Employee.query.filter_by(employee_id=data['employee_id']).first()
                        if existing:
                            print(f"Employee with ID {data['employee_id']} already exists")
                            error_count += 1
                            error_details.append(f"الموظف برقم {data['employee_id']} موجود مسبقا")
                            continue
                            
                        # Check if employee with same national_id already exists
                        existing = Employee.query.filter_by(national_id=data['national_id']).first()
                        if existing:
                            print(f"Employee with national ID {data['national_id']} already exists")
                            error_count += 1
                            error_details.append(f"الموظف برقم هوية {data['national_id']} موجود مسبقا")
                            continue
                        
                        employee = Employee(**data)
                        db.session.add(employee)
                        db.session.commit()
                        success_count += 1
                        print(f"Successfully added employee: {data.get('name')}")
                    except Exception as e:
                        db.session.rollback()
                        error_count += 1
                        print(f"Error adding employee {index+1}: {str(e)}")
                        error_details.append(f"خطأ في السجل {index+1}: {str(e)}")
                
                # Log the import
                error_detail_str = ", ".join(error_details[:5])
                if len(error_details) > 5:
                    error_detail_str += f" وغيرها من الأخطاء..."
                
                details = f'تم استيراد {success_count} موظف بنجاح و {error_count} فشل'
                if error_details:
                    details += f". أخطاء: {error_detail_str}"
                    
                audit = SystemAudit(
                    action='import',
                    entity_type='employee',
                    entity_id=0,
                    details=details
                )
                db.session.add(audit)
                db.session.commit()
                
                if error_count > 0:
                    flash(f'تم استيراد {success_count} موظف بنجاح و {error_count} فشل. {error_detail_str}', 'warning')
                else:
                    flash(f'تم استيراد {success_count} موظف بنجاح', 'success')
                return redirect(url_for('employees.index'))
            except Exception as e:
                flash(f'حدث خطأ أثناء استيراد الملف: {str(e)}', 'danger')
        else:
            flash('الملف يجب أن يكون بصيغة Excel (.xlsx, .xls)', 'danger')
    
    return render_template('employees/import.html')

@employees_bp.route('/export')
def export_excel():
    """Export employees to Excel file"""
    try:
        employees = Employee.query.all()
        output = generate_employee_excel(employees)
        
        # Log the export
        audit = SystemAudit(
            action='export',
            entity_type='employee',
            entity_id=0,
            details=f'تم تصدير {len(employees)} موظف إلى ملف Excel'
        )
        db.session.add(audit)
        db.session.commit()
        
        return send_file(
            BytesIO(output.getvalue()),
            download_name='employees.xlsx',
            as_attachment=True,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        flash(f'حدث خطأ أثناء تصدير البيانات: {str(e)}', 'danger')
        return redirect(url_for('employees.index'))
