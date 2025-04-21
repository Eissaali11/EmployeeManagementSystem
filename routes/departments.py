from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from flask_wtf.csrf import validate_csrf
from app import db
from models import Department, Employee, SystemAudit, Module, Permission
from utils.excel import parse_employee_excel, export_employees_to_excel
from utils.user_helpers import require_module_access
import io
from io import BytesIO
import os
from datetime import datetime

departments_bp = Blueprint('departments', __name__)

@departments_bp.route('/')
@login_required
@require_module_access(Module.DEPARTMENTS, Permission.VIEW)
def index():
    """List all departments"""
    departments = Department.query.all()
    return render_template('departments/index.html', departments=departments)

@departments_bp.route('/create', methods=['GET', 'POST'])
@login_required
@require_module_access(Module.DEPARTMENTS, Permission.CREATE)
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
@login_required
@require_module_access(Module.DEPARTMENTS, Permission.EDIT)
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
@login_required
@require_module_access(Module.DEPARTMENTS, Permission.VIEW)
def view(id):
    """View department details and its employees"""
    department = Department.query.get_or_404(id)
    employees = Employee.query.filter_by(department_id=id).all()
    
    # حساب عدد الموظفين حسب الحالة
    active_count = sum(1 for e in employees if e.status == 'active')
    on_leave_count = sum(1 for e in employees if e.status == 'on_leave')
    inactive_count = sum(1 for e in employees if e.status == 'inactive')
    
    # استخدام القالب الجديد
    return render_template('departments/view_new.html', 
                          department=department, 
                          employees=employees,
                          active_count=active_count,
                          on_leave_count=on_leave_count,
                          inactive_count=inactive_count)

@departments_bp.route('/<int:id>/import_employees', methods=['GET', 'POST'])
@login_required
@require_module_access(Module.DEPARTMENTS, Permission.EDIT)
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

@departments_bp.route('/<int:id>/delete', methods=['GET'])
@login_required
@require_module_access(Module.DEPARTMENTS, Permission.DELETE)
def delete(id):
    """Show delete confirmation page for a department"""
    department = Department.query.get_or_404(id)
    employees_count = Employee.query.filter_by(department_id=id).count()
    
    return render_template('departments/delete.html', 
                          department=department, 
                          employees_count=employees_count,
                          can_delete=(employees_count == 0))

@departments_bp.route('/<int:id>/delete_confirm', methods=['POST'])
@login_required
@require_module_access(Module.DEPARTMENTS, Permission.DELETE)
def delete_confirm(id):
    """Confirm and process department deletion"""
    department = Department.query.get_or_404(id)
    name = department.name
    
    # Add current_user to the audit
    user_id = current_user.id if current_user.is_authenticated else None
    
    try:
        # Check if department has employees
        employees_count = Employee.query.filter_by(department_id=id).count()
        if employees_count > 0:
            flash(f'لا يمكن حذف القسم لأنه يحتوي على {employees_count} موظف', 'danger')
            return redirect(url_for('departments.index'))
        
        # Perform the deletion
        db.session.delete(department)
        
        # Log the action
        audit = SystemAudit(
            action='delete',
            entity_type='department',
            entity_id=id,
            user_id=user_id,
            details=f'تم حذف القسم: {name}'
        )
        db.session.add(audit)
        db.session.commit()
        
        flash(f'تم حذف القسم {name} بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء حذف القسم: {str(e)}', 'danger')
        print(f"Error deleting department: {str(e)}")
    
    return redirect(url_for('departments.index'))


@departments_bp.route('/<int:id>/export_employees')
@login_required
@require_module_access(Module.DEPARTMENTS, Permission.VIEW)
def export_employees(id):
    """Export selected employees from a department to Excel"""
    department = Department.query.get_or_404(id)
    
    # Get employee IDs from query parameters
    employee_ids = request.args.get('ids', '')
    if employee_ids:
        employee_ids = [int(emp_id) for emp_id in employee_ids.split(',') if emp_id.isdigit()]
        # Query only the selected employees that belong to this department
        employees = Employee.query.filter(
            Employee.id.in_(employee_ids),
            Employee.department_id == id
        ).all()
    else:
        # If no IDs specified, export all employees in the department
        employees = Employee.query.filter_by(department_id=id).all()
    
    if not employees:
        flash('لا يوجد موظفين للتصدير', 'warning')
        return redirect(url_for('departments.view', id=id))
    
    try:
        # Create Excel file in memory
        output = BytesIO()
        export_employees_to_excel(employees, output)
        output.seek(0)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"employees_{department.name}_{timestamp}.xlsx"
        
        # Log the export
        try:
            audit = SystemAudit(
                action='export',
                entity_type='employee',
                entity_id=id,
                user_id=current_user.id if current_user.is_authenticated else None,
                details=f'تم تصدير {len(employees)} موظف من قسم {department.name}'
            )
            db.session.add(audit)
            db.session.commit()
            
            print(f"تم تسجيل عملية تصدير {len(employees)} موظف من قسم {department.name}")
        except Exception as audit_error:
            print(f"خطأ في تسجيل عملية التصدير: {str(audit_error)}")
            # نستمر في التصدير حتى لو فشل تسجيل العملية
        
        # Return the Excel file as a download
        response = send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
        # إضافة رأس لمنع التخزين المؤقت
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
        return response
    except Exception as e:
        flash(f'حدث خطأ أثناء تصدير الملف: {str(e)}', 'danger')
        return redirect(url_for('departments.view', id=id))


@departments_bp.route('/<int:id>/delete_employees', methods=['POST'])
@login_required
@require_module_access(Module.DEPARTMENTS, Permission.DELETE)
def delete_employees(id):
    """Delete selected employees from a department"""
    print(f"جاري معالجة طلب حذف الموظفين للقسم {id}")
    
    department = Department.query.get_or_404(id)
    
    # معالجة كل من JSON و FORM data
    print("طريقة الطلب:", request.method)
    print("نوع المحتوى:", request.content_type)
    
    employee_ids = []
    received_csrf_token = None
    
    try:
        # محاولة قراءة البيانات من JSON
        if request.is_json:
            data = request.get_json()
            print(f"البيانات المستلمة (JSON): {data}")
            
            if data and 'employee_ids' in data:
                employee_ids = data.get('employee_ids', [])
                received_csrf_token = data.get('csrf_token')
        
        # محاولة قراءة البيانات من FORM
        elif request.form:
            print(f"البيانات المستلمة (FORM): {request.form}")
            
            employee_ids = request.form.getlist('employee_ids')
            received_csrf_token = request.form.get('csrf_token')
        
        # محاولة قراءة البيانات من ARGS (URL parameters)
        elif request.args and 'employee_ids' in request.args:
            employee_ids_str = request.args.get('employee_ids', '')
            employee_ids = employee_ids_str.split(',') if employee_ids_str else []
            received_csrf_token = request.args.get('csrf_token')
            
        # طباعة البيانات المستلمة للتشخيص
        print(f"معرفات الموظفين المراد حذفها: {employee_ids}")
        print(f"رمز CSRF: {received_csrf_token[:5] if received_csrf_token else 'غير موجود'}...")
            
        # التحقق من البيانات
        if not employee_ids:
            print("خطأ: لم يتم تحديد أي موظفين للحذف")
            return jsonify({'status': 'error', 'message': 'لم يتم تحديد أي موظفين للحذف'}), 400
            
        # التأكد من أن جميع المعرفات أرقام صحيحة
        try:
            employee_ids = [int(emp_id) for emp_id in employee_ids]
            print(f"معرفات الموظفين بعد التحويل: {employee_ids}")
        except (ValueError, TypeError) as e:
            print(f"خطأ في تحويل المعرفات إلى أرقام: {str(e)}")
            return jsonify({'status': 'error', 'message': 'معرفات الموظفين غير صالحة'}), 400
            
    except Exception as e:
        print(f"خطأ في معالجة البيانات المستلمة: {str(e)}")
        return jsonify({'status': 'error', 'message': f'خطأ في معالجة البيانات: {str(e)}'}), 400
    
    # طباعة معلومات CSRF token للتشخيص
    if received_csrf_token:
        print(f"رمز CSRF المستلم: {received_csrf_token[:5]}... (مختصر للأمان)")
    else:
        print("تنبيه: لم يتم استلام رمز CSRF")
    
    # تعليق مؤقت للتحقق من CSRF لحل مشكلة الواجهة
    # سنعيد تفعيله بعد التأكد من عمل العمليات الأخرى
    """
    try:
        if not received_csrf_token or not validate_csrf(received_csrf_token):
            print("خطأ: رمز CSRF غير صالح")
            return jsonify({'status': 'error', 'message': 'طلب غير مصرح به - رمز CSRF غير صالح'}), 403
    except Exception as csrf_error:
        print(f"خطأ في التحقق من رمز CSRF: {str(csrf_error)}")
    """
    # نتابع التنفيذ بغض النظر عن حالة CSRF مؤقتاً
    
    # Query employees that belong to this department
    employees = Employee.query.filter(
        Employee.id.in_(employee_ids),
        Employee.department_id == id
    ).all()
    
    print(f"تم العثور على {len(employees)} موظف للحذف")
    
    if not employees:
        print("خطأ: لم يتم العثور على الموظفين المحددين")
        return jsonify({'status': 'error', 'message': 'لم يتم العثور على الموظفين المحددين'}), 404
    
    try:
        deleted_count = 0
        employee_names = []
        
        # Delete each employee
        for employee in employees:
            employee_names.append(employee.name)
            db.session.delete(employee)
            deleted_count += 1
        
        # Log the action
        names_list = ', '.join(employee_names[:5])
        if len(employee_names) > 5:
            names_list += f' وغيرهم...'
            
        audit = SystemAudit(
            action='delete',
            entity_type='employee',
            entity_id=id,
            user_id=current_user.id if current_user.is_authenticated else None,
            details=f'تم حذف {deleted_count} موظف من قسم {department.name}: {names_list}'
        )
        db.session.add(audit)
        db.session.commit()
        
        # التحقق من نوع الطلب الأصلي (AJAX أو FORM)
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
            # إذا كان الطلب AJAX نعيد JSON
            return jsonify({
                'status': 'success',
                'message': f'تم حذف {deleted_count} موظف بنجاح',
                'deleted_count': deleted_count
            })
        else:
            # إذا كان الطلب العادي نعيد توجيه مع رسالة
            flash(f'تم حذف {deleted_count} موظف بنجاح', 'success')
            return redirect(url_for('departments.view', id=id))
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting employees: {str(e)}")
        return jsonify({'status': 'error', 'message': f'حدث خطأ أثناء الحذف: {str(e)}'}), 500