import os
import pandas as pd
from io import BytesIO
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file
from werkzeug.utils import secure_filename
from sqlalchemy.exc import IntegrityError
from flask_login import login_required
from app import db
from models import Employee, Department, SystemAudit, Document, Attendance, Salary, Module, Permission, Vehicle, VehicleHandover,User,Nationality, employee_departments, MobileDevice
from sqlalchemy import func, or_
from utils.excel import parse_employee_excel, generate_employee_excel, export_employee_attendance_to_excel
from utils.date_converter import parse_date
from utils.user_helpers import require_module_access
from utils.employee_comprehensive_report_updated import generate_employee_comprehensive_pdf, generate_employee_comprehensive_excel
from utils.employee_basic_report import generate_employee_basic_pdf
from utils.audit_logger import log_activity

employees_bp = Blueprint('employees', __name__)

# المجلد المخصص لحفظ صور الموظفين
UPLOAD_FOLDER = 'static/uploads/employees'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """التحقق من أن الملف من الأنواع المسموحة"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_employee_image(file, employee_id, image_type):
    """حفظ صورة الموظف وإرجاع المسار"""
    if file and allowed_file(file.filename):
        # التأكد من وجود المجلد
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # إنشاء اسم ملف فريد
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        unique_filename = f"{employee_id}_{image_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
        
        filepath = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(filepath)
        
        # إرجاع المسار النسبي للحفظ في قاعدة البيانات
        return f"uploads/employees/{unique_filename}"
    return None

@employees_bp.route('/')
@login_required
@require_module_access(Module.EMPLOYEES, Permission.VIEW)
def index():
    """List all employees with filtering options"""
    # الحصول على معاملات الفلترة من URL
    department_filter = request.args.get('department', '')
    status_filter = request.args.get('status', '')
    multi_department_filter = request.args.get('multi_department', '')
    no_department_filter = request.args.get('no_department', '')
    duplicate_names_filter = request.args.get('duplicate_names', '')
    
    # بناء الاستعلام الأساسي
    query = Employee.query.options(
        db.joinedload(Employee.departments),
        db.joinedload(Employee.nationality_rel)
    )
    
    # تطبيق فلتر القسم
    if department_filter:
        query = query.join(Employee.departments).filter(Department.id == department_filter)
    
    # تطبيق فلتر الحالة
    if status_filter:
        query = query.filter(Employee.status == status_filter)
    
    # تطبيق فلتر الأسماء المكررة
    if duplicate_names_filter == 'yes':
        # البحث عن الأسماء المكررة
        duplicate_names_subquery = db.session.query(Employee.name, func.count(Employee.name).label('name_count'))\
                                           .group_by(Employee.name)\
                                           .having(func.count(Employee.name) > 1)\
                                           .subquery()
        query = query.join(duplicate_names_subquery, Employee.name == duplicate_names_subquery.c.name)
    
    # تطبيق فلتر الموظفين غير المربوطين بأي قسم
    if no_department_filter == 'yes':
        # الموظفين الذين لا يوجد لديهم أي أقسام
        query = query.outerjoin(employee_departments)\
                     .filter(employee_departments.c.employee_id.is_(None))
    elif multi_department_filter == 'yes':
        # الموظفين الذين لديهم أكثر من قسم
        subquery = db.session.query(employee_departments.c.employee_id, 
                                   func.count(employee_departments.c.department_id).label('dept_count'))\
                            .group_by(employee_departments.c.employee_id)\
                            .having(func.count(employee_departments.c.department_id) > 1)\
                            .subquery()
        query = query.join(subquery, Employee.id == subquery.c.employee_id)
    elif multi_department_filter == 'no':
        # الموظفين الذين لديهم قسم واحد فقط أو لا يوجد لديهم أقسام
        subquery = db.session.query(employee_departments.c.employee_id, 
                                   func.count(employee_departments.c.department_id).label('dept_count'))\
                            .group_by(employee_departments.c.employee_id)\
                            .having(func.count(employee_departments.c.department_id) <= 1)\
                            .subquery()
        query = query.outerjoin(subquery, Employee.id == subquery.c.employee_id)\
                     .filter(or_(subquery.c.employee_id.is_(None), 
                               subquery.c.dept_count <= 1))
    
    employees = query.all()
    
    # الحصول على جميع الأقسام للفلتر
    departments = Department.query.all()
    
    # حساب إحصائيات الموظفين متعددي الأقسام
    multi_dept_count = db.session.query(Employee.id)\
                                .join(employee_departments)\
                                .group_by(Employee.id)\
                                .having(func.count(employee_departments.c.department_id) > 1)\
                                .count()
    
    # حساب الموظفين بدون أقسام
    no_dept_count = db.session.query(Employee.id)\
                             .outerjoin(employee_departments)\
                             .filter(employee_departments.c.employee_id.is_(None))\
                             .count()
    
    # حساب الموظفين بأسماء مكررة - طريقة مبسطة
    duplicate_names_list = db.session.query(Employee.name)\
                                    .group_by(Employee.name)\
                                    .having(func.count(Employee.name) > 1)\
                                    .all()
    
    duplicate_names_count = 0
    duplicate_names_set = set()
    for name_tuple in duplicate_names_list:
        name = name_tuple[0]
        count = db.session.query(Employee).filter(Employee.name == name).count()
        duplicate_names_count += count
        duplicate_names_set.add(name)
    
    single_dept_count = db.session.query(Employee).count() - multi_dept_count - no_dept_count
    
    return render_template('employees/index.html', 
                         employees=employees, 
                         departments=departments,
                         current_department=department_filter,
                         current_status=status_filter,
                         current_multi_department=multi_department_filter,
                         current_no_department=no_department_filter,
                         current_duplicate_names=duplicate_names_filter,
                         multi_dept_count=multi_dept_count,
                         single_dept_count=single_dept_count,
                         no_dept_count=no_dept_count,
                         duplicate_names_count=duplicate_names_count,
                         duplicate_names_set=duplicate_names_set)

@employees_bp.route('/create', methods=['GET', 'POST'])
@login_required
@require_module_access(Module.EMPLOYEES, Permission.CREATE)
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
            birth_date = parse_date(request.form.get('birth_date', ''))
            mobilePersonal = request.form.get('mobilePersonal')
            nationality_id = request.form.get('nationality_id')
            contract_status = request.form.get('contract_status')
            license_status = request.form.get('license_status')
            
            # الحقول الجديدة لنوع الموظف والعهدة
            employee_type = request.form.get('employee_type', 'regular')
            has_mobile_custody = 'has_mobile_custody' in request.form
            mobile_type = request.form.get('mobile_type', '') if has_mobile_custody else None
            mobile_imei = request.form.get('mobile_imei', '') if has_mobile_custody else None
            
            # حقول الكفالة الجديدة
            sponsorship_status = request.form.get('sponsorship_status', 'inside')
            current_sponsor_name = request.form.get('current_sponsor_name', '')
            
            selected_dept_ids = {int(dept_id) for dept_id in request.form.getlist('department_ids')}
            
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
                join_date=join_date,
                birth_date=birth_date,
                mobilePersonal=mobilePersonal,
                nationality_id=int(nationality_id) if nationality_id else None,
                contract_status=contract_status,
                license_status=license_status,
                employee_type=employee_type,
                has_mobile_custody=has_mobile_custody,
                mobile_type=mobile_type,
                mobile_imei=mobile_imei,
                sponsorship_status=sponsorship_status,
                current_sponsor_name=current_sponsor_name
            )
            if selected_dept_ids:
                departments_to_assign = Department.query.filter(Department.id.in_(selected_dept_ids)).all()
                employee.departments.extend(departments_to_assign)
            
            db.session.add(employee)
            db.session.commit()
            
            # Log the action
            log_activity('create', 'Employee', employee.id, f'تم إنشاء موظف جديد: {name}')
            
            flash('تم إنشاء الموظف بنجاح', 'success')
            return redirect(url_for('employees.index'))
        
        except IntegrityError as e:
            db.session.rollback()
            error_message = str(e)
            if "employee_id" in error_message.lower():
                flash(f"هذه المعلومات مسجلة مسبقاً: رقم الموظف موجود بالفعل في النظام", "danger")
            elif "national_id" in error_message.lower():
                flash(f"هذه المعلومات مسجلة مسبقاً: رقم الهوية موجود بالفعل في النظام", "danger")
            else:
                flash("هذه المعلومات مسجلة مسبقاً، لا يمكن تكرار بيانات الموظفين", "danger")
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ: {str(e)}', 'danger')
    
    # Get all departments for the dropdown
    departments = Department.query.all()
    nationalities = Nationality.query.order_by(Nationality.name_ar).all()
    
    # جلب الأرقام المتاحة فقط (غير المربوطة بأي موظف)
    from models import ImportedPhoneNumber
    available_phone_numbers = ImportedPhoneNumber.query.filter(
        ImportedPhoneNumber.employee_id.is_(None)  # الأرقام المتاحة فقط
    ).order_by(ImportedPhoneNumber.phone_number).all()
    
    # جلب أرقام IMEI المتاحة من إدارة الأجهزة
    from models import MobileDevice
    available_imei_numbers = MobileDevice.query.filter(
        MobileDevice.status == 'متاح',  # الأجهزة المتاحة فقط
        MobileDevice.employee_id.is_(None)  # غير مربوطة بموظف
    ).order_by(MobileDevice.imei).all()
    
    return render_template('employees/create.html', 
                         departments=departments,
                         nationalities=nationalities,
                         available_phone_numbers=available_phone_numbers,
                         available_imei_numbers=available_imei_numbers)



@employees_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@require_module_access(Module.EMPLOYEES, Permission.EDIT)
def edit(id):
    """
    تعديل بيانات موظف موجود وأقسامه، مع التحقق من البيانات الفريدة،
    والتعامل الآمن مع تحديث العلاقات، ومزامنة المستخدم المرتبط.
    """
    employee = Employee.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            # 1. استخراج البيانات الجديدة من النموذج
            new_name = request.form.get('name', '').strip()
            new_employee_id = request.form.get('employee_id', '').strip()
            new_national_id = request.form.get('national_id', '').strip()

            # 2. التحقق من صحة البيانات الفريدة قبل أي تعديل
            # التحقق من الرقم الوظيفي
            existing_employee = Employee.query.filter(Employee.employee_id == new_employee_id, Employee.id != id).first()
            if existing_employee:
                flash(f"رقم الموظف '{new_employee_id}' مستخدم بالفعل.", "danger")
                return redirect(url_for('employees.edit', id=id))

            # التحقق من الرقم الوطني
            existing_national = Employee.query.filter(Employee.national_id == new_national_id, Employee.id != id).first()
            if existing_national:
                flash(f"الرقم الوطني '{new_national_id}' مستخدم بالفعل.", "danger")
                return redirect(url_for('employees.edit', id=id))

            # 3. تحديث البيانات الأساسية للموظف
            employee.name = new_name
            employee.employee_id = new_employee_id
            employee.national_id = new_national_id
            # معالجة رقم الجوال مع دعم الإدخال المخصص
            mobile_value = request.form.get('mobile', '')
            print(f"DEBUG: Received mobile value from form: '{mobile_value}'")
            if mobile_value == 'custom':
                mobile_value = request.form.get('mobile_custom', '')
                print(f"DEBUG: Using custom mobile value: '{mobile_value}'")
            employee.mobile = mobile_value
            print(f"DEBUG: Final mobile value set to employee: '{employee.mobile}'")
            employee.status = request.form.get('status', 'active')
            employee.job_title = request.form.get('job_title', '')
            employee.location = request.form.get('location', '')
            employee.project = request.form.get('project', '')
            employee.email = request.form.get('email', '')
            employee.mobilePersonal = request.form.get('mobilePersonal', '')
            employee.contract_status = request.form.get('contract_status', '')
            employee.license_status = request.form.get('license_status', '')
            nationality_id = request.form.get('nationality_id')
            employee.nationality_id = int(nationality_id) if nationality_id else None
            
            # تحديث الحقول الجديدة لنوع الموظف والعهدة
            employee.employee_type = request.form.get('employee_type', 'regular')
            employee.has_mobile_custody = 'has_mobile_custody' in request.form
            employee.mobile_type = request.form.get('mobile_type', '') if employee.has_mobile_custody else None
            employee.mobile_imei = request.form.get('mobile_imei', '') if employee.has_mobile_custody else None
            
            # تحديث حقول الكفالة
            employee.sponsorship_status = request.form.get('sponsorship_status', 'inside')
            employee.current_sponsor_name = request.form.get('current_sponsor_name', '') if employee.sponsorship_status == 'inside' else None
            
            join_date_str = request.form.get('join_date')
            employee.join_date = parse_date(join_date_str) if join_date_str else None
            
            # إضافة معالجة تاريخ الميلاد
            birth_date_str = request.form.get('birth_date')
            employee.birth_date = parse_date(birth_date_str) if birth_date_str else None

            selected_dept_ids = {int(dept_id) for dept_id in request.form.getlist('department_ids')}
            current_dept_ids = {dept.id for dept in employee.departments}

            depts_to_add_ids = selected_dept_ids - current_dept_ids

            if depts_to_add_ids:
                    depts_to_add = Department.query.filter(Department.id.in_(depts_to_add_ids)).all()
                    for dept in depts_to_add:
                        employee.departments.append(dept)
                
            depts_to_remove_ids = current_dept_ids - selected_dept_ids


            if depts_to_remove_ids:
                    depts_to_remove = Department.query.filter(Department.id.in_(depts_to_remove_ids)).all()
                    for dept in depts_to_remove:
                        employee.departments.remove(dept)

            user_linked = User.query.filter_by(employee_id=employee.id).first()

            if user_linked:
                    # الطريقة الأسهل هنا هي فقط تعيين القائمة النهائية بعد تعديلها
                    # بما أننا داخل no_autoflush، يمكننا تعيينها مباشرة
                    # سيقوم SQLAlchemy بحساب الفرق بنفسه عند الـ commit
                    final_departments = Department.query.filter(Department.id.in_(selected_dept_ids)).all()
                    user_linked.departments = final_departments
            

           
            # 7. حفظ كل التغييرات للموظف والمستخدم دفعة واحدة
            db.session.commit()
            
            log_activity('update', 'Employee', employee.id, f'تم تحديث بيانات الموظف: {employee.name}')
            flash('تم تحديث بيانات الموظف وأقسامه بنجاح.', 'success')
            
            # التحقق من مصدر الطلب للعودة إلى الصفحة المناسبة
            return_url = request.form.get('return_url')
            if not return_url:
                return_url = request.referrer
            
            if return_url and '/departments/' in return_url:
                # استخراج معرف القسم من الرابط المرجعي
                try:
                    department_id = return_url.split('/departments/')[1].split('/')[0]
                    return redirect(url_for('departments.view', id=department_id))
                except:
                    pass
            
            return redirect(url_for('employees.index'))
        
        except Exception as e:
            # تسجيل الخطأ للمطورين
            flash(f'حدث خطأ غير متوقع أثناء عملية التحديث. يرجى المحاولة مرة أخرى. Error updating employee (ID: {id}): {e}', 'danger')


    # في حالة GET request (عند فتح الصفحة لأول مرة)
    all_departments = Department.query.order_by(Department.name).all()
    all_nationalities = Nationality.query.order_by(Nationality.name_ar).all() # جلب كل الجنسيات
    
    # جلب الأرقام المتاحة فقط (غير المربوطة بأي موظف)
    from models import ImportedPhoneNumber
    available_phone_numbers = ImportedPhoneNumber.query.filter(
        ImportedPhoneNumber.employee_id.is_(None)  # الأرقام المتاحة فقط
    ).order_by(ImportedPhoneNumber.phone_number).all()
    
    # جلب أرقام IMEI المتاحة من إدارة الأجهزة
    from models import MobileDevice
    available_imei_numbers = MobileDevice.query.filter(
        MobileDevice.status == 'متاح',  # الأجهزة المتاحة فقط
        MobileDevice.employee_id.is_(None)  # غير مربوطة بموظف
    ).order_by(MobileDevice.imei).all()
    
    print(f"Passing {len(all_nationalities)} nationalities to the template.")
    return render_template('employees/edit.html', 
                         employee=employee, 
                         nationalities=all_nationalities, 
                         departments=all_departments,
                         available_phone_numbers=available_phone_numbers,
                         available_imei_numbers=available_imei_numbers)





# @employees_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
# @login_required
# @require_module_access(Module.EMPLOYEES, Permission.EDIT)
# def edit(id):
#     """
#     تعديل بيانات موظف موجود وأقسامه المرتبطة بها، مع مزامنة المستخدم المرتبط.
#     """
#     employee = Employee.query.get_or_404(id)
    
#     if request.method == 'POST':
#         try:
#             # 1. تحديث البيانات الأساسية للموظف
#             employee.name = request.form['name']
#             employee.employee_id = request.form['employee_id']
#             employee.national_id = request.form['national_id']
#             employee.mobile = request.form['mobile']
#             employee.status = request.form['status']
#             employee.job_title = request.form['job_title']
#             employee.location = request.form.get('location', '')
#             employee.project = request.form.get('project', '')
#             employee.email = request.form.get('email', '')
            
#             join_date_str = request.form.get('join_date', '')
#             if join_date_str:
#                 employee.join_date = parse_date(join_date_str) # افترض وجود دالة parse_date

#             # 2. *** تحديث الأقسام المرتبطة (منطق متعدد إلى متعدد) ***
#             # استلام قائمة معرفات الأقسام المحددة من مربعات الاختيار
#             selected_dept_ids = [int(dept_id) for dept_id in request.form.getlist('department_ids')]
            
#             # جلب كائنات الأقسام الفعلية من قاعدة البيانات
#             selected_departments = Department.query.filter(Department.id.in_(selected_dept_ids)).all()
            
#             # تعيين القائمة الجديدة للموظف، وSQLAlchemy سيتولى تحديث جدول الربط
#             employee.departments = selected_departments
            
#             # 3. *** المزامنة التلقائية للمستخدم المرتبط (مهم جداً) ***
#             # ابحث عن المستخدم المرتبط بهذا الموظف (إن وجد)
#             user_linked_to_employee = User.query.filter_by(employee_id=employee.id).first()
#             if user_linked_to_employee:
#                 # إذا وجد مستخدم، قم بمزامنة قائمة أقسامه لتكون مطابقة
#                 user_linked_to_employee.departments = selected_departments
#                 print(f"INFO: Synced departments for linked user: {user_linked_to_employee.name}")
            
#             # 4. حفظ كل التغييرات للموظف والمستخدم في قاعدة البيانات
#             db.session.commit()
            
#             # 5. تسجيل الإجراء والعودة
#             log_activity('update', 'Employee', employee.id, f'تم تحديث بيانات الموظف: {employee.name}')
#             flash('تم تحديث بيانات الموظف وأقسامه بنجاح.', 'success')
#             return redirect(url_for('employees.index'))
        
#         except  Exception as e:
#             db.session.rollback()
#             flash(f"خطأ في التكامل: رقم الموظف أو الرقم الوطني قد يكون مستخدماً بالفعل.{str(e)}", "danger")
#         except Exception as e:
#             db.session.rollback()
#             flash(f'حدث خطأ غير متوقع أثناء التحديث: {str(e)}', 'danger')
#             # من الجيد تسجيل الخطأ الكامل في السجلات للمطورين
#             # current_app.logger.error(f"Error editing employee {id}: {e}")
            
#     # في حالة GET request، جهز البيانات للعرض
#     all_departments = Department.query.order_by(Department.name).all()
#     return render_template('employees/edit.html', employee=employee, departments=all_departments)








@employees_bp.route('/<int:id>/view')
@login_required
@require_module_access(Module.EMPLOYEES, Permission.VIEW)
def view(id):
    """View detailed employee information"""
    employee = Employee.query.options(
        db.joinedload(Employee.departments),
        db.joinedload(Employee.nationality_rel)
    ).get_or_404(id)
    
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
    
    # Get all attendance records for this employee
    attendances = Attendance.query.filter_by(employee_id=id).order_by(Attendance.date.desc()).all()
    
    # Get salary records
    salaries = Salary.query.filter_by(employee_id=id).order_by(Salary.year.desc(), Salary.month.desc()).all()
    
    # Get vehicle handover records
    vehicle_handovers = VehicleHandover.query.filter_by(employee_id=id).order_by(VehicleHandover.handover_date.desc()).all()
    
    # Get mobile devices assigned to this employee
    mobile_devices = MobileDevice.query.filter_by(employee_id=id).order_by(MobileDevice.assigned_date.desc()).all()
    
    # Get device assignments for this employee
    from models import DeviceAssignment
    device_assignments = DeviceAssignment.query.filter_by(
        employee_id=id, 
        is_active=True
    ).options(
        db.joinedload(DeviceAssignment.device),
        db.joinedload(DeviceAssignment.sim_card)
    ).all()
    
    all_departments = Department.query.order_by(Department.name).all()
    return render_template('employees/view.html', 
                          employee=employee, 
                          documents=documents,
                          documents_by_type=documents_by_type,
                          document_types_map=document_types_map,
                          attendances=attendances,
                          salaries=salaries,
                          vehicle_handovers=vehicle_handovers,
                          mobile_devices=mobile_devices,
                          device_assignments=device_assignments,
                          departments=all_departments
                          )

@employees_bp.route('/<int:id>/upload_iban', methods=['POST'])
@login_required
@require_module_access(Module.EMPLOYEES, Permission.EDIT)
def upload_iban(id):
    """رفع صورة الإيبان البنكي للموظف"""
    employee = Employee.query.get_or_404(id)
    
    try:
        # الحصول على بيانات الإيبان والملف
        bank_iban = request.form.get('bank_iban', '').strip()
        iban_file = request.files.get('iban_image')
        
        # تحديث رقم الإيبان
        if bank_iban:
            employee.bank_iban = bank_iban
        
        # رفع صورة الإيبان إذا تم اختيارها
        if iban_file and iban_file.filename:
            # حذف الصورة القديمة إذا كانت موجودة
            if employee.bank_iban_image:
                old_image_path = os.path.join('static', employee.bank_iban_image)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
            
            # حفظ الصورة الجديدة
            image_path = save_employee_image(iban_file, employee.id, 'iban')
            if image_path:
                employee.bank_iban_image = image_path
        
        db.session.commit()
        
        # تسجيل العملية
        log_activity('update', 'Employee', employee.id, f'تم تحديث بيانات الإيبان البنكي للموظف: {employee.name}')
        
        flash('تم حفظ بيانات الإيبان البنكي بنجاح', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء حفظ بيانات الإيبان: {str(e)}', 'danger')
    
    return redirect(url_for('employees.view', id=id))

@employees_bp.route('/<int:id>/delete_iban_image', methods=['POST'])
@login_required
@require_module_access(Module.EMPLOYEES, Permission.EDIT)
def delete_iban_image(id):
    """حذف صورة الإيبان البنكي للموظف"""
    employee = Employee.query.get_or_404(id)
    
    try:
        if employee.bank_iban_image:
            # حذف الملف من الخادم
            image_path = os.path.join('static', employee.bank_iban_image)
            if os.path.exists(image_path):
                os.remove(image_path)
            
            # حذف المسار من قاعدة البيانات
            employee.bank_iban_image = None
            db.session.commit()
            
            # تسجيل العملية
            log_activity('delete', 'Employee', employee.id, f'تم حذف صورة الإيبان البنكي للموظف: {employee.name}')
            
            flash('تم حذف صورة الإيبان البنكي بنجاح', 'success')
        else:
            flash('لا توجد صورة إيبان لحذفها', 'warning')
            
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء حذف صورة الإيبان: {str(e)}', 'danger')
    
    return redirect(url_for('employees.view', id=id))

@employees_bp.route('/<int:id>/confirm_delete')
@login_required
@require_module_access(Module.EMPLOYEES, Permission.DELETE)
def confirm_delete(id):
    """صفحة تأكيد حذف الموظف"""
    employee = Employee.query.get_or_404(id)
    
    # تحديد عنوان الصفحة التي تم تحويلنا منها للعودة إليها عند الإلغاء
    return_url = request.referrer
    if not return_url or '/employees/' in return_url:
        return_url = url_for('employees.index')
    
    return render_template('employees/confirm_delete.html', 
                          employee=employee, 
                          return_url=return_url)

@employees_bp.route('/<int:id>/delete', methods=['GET', 'POST'])
@login_required
@require_module_access(Module.EMPLOYEES, Permission.DELETE)
def delete(id):
    """Delete an employee"""
    employee = Employee.query.get_or_404(id)
    name = employee.name
    
    # إذا كان الطلب GET، نعرض صفحة التأكيد
    if request.method == 'GET':
        return redirect(url_for('employees.confirm_delete', id=id))
    
    # إذا كان الطلب POST، نتحقق من تأكيد الحذف
    confirmed = request.form.get('confirmed', 'no')
    
    if confirmed != 'yes':
        flash('لم يتم تأكيد عملية الحذف', 'warning')
        return redirect(url_for('employees.view', id=id))
    
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
    
    # التحقق من مصدر الطلب للعودة إلى الصفحة المناسبة
    referrer = request.form.get('return_url')
    if referrer and '/departments/' in referrer:
        try:
            department_id = referrer.split('/departments/')[1].split('/')[0]
            return redirect(url_for('departments.view', id=department_id))
        except:
            pass
    
    return redirect(url_for('employees.index'))

@employees_bp.route('/import', methods=['GET', 'POST'])
@login_required
@require_module_access(Module.EMPLOYEES, Permission.CREATE)
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
                        
                        # Extract department data separately
                        department_name = data.pop('department', None)
                        
                        # Create employee without department field
                        employee = Employee(**data)
                        db.session.add(employee)
                        db.session.flush()  # Get the ID without committing
                        
                        # Handle department assignment if provided
                        if department_name:
                            department = Department.query.filter_by(name=department_name).first()
                            if department:
                                employee.departments.append(department)
                            else:
                                # Create new department if it doesn't exist
                                new_department = Department(name=department_name)
                                db.session.add(new_department)
                                db.session.flush()
                                employee.departments.append(new_department)
                        
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

@employees_bp.route('/import/template')
@login_required
@require_module_access(Module.EMPLOYEES, Permission.VIEW)
def import_template():
    """Download Excel template for employee import with all comprehensive fields"""
    try:
        import pandas as pd
        
        # إنشاء قالب Excel مع جميع الحقول المطلوبة والاختيارية
        template_data = {
            'الاسم الكامل': ['محمد أحمد علي', 'فاطمة سالم محمد'],
            'رقم الموظف': ['EMP001', 'EMP002'],
            'رقم الهوية الوطنية': ['1234567890', '0987654321'],
            'رقم الجوال': ['0501234567', '0509876543'],
            'الجوال الشخصي': ['0551234567', ''],
            'المسمى الوظيفي': ['مطور برمجيات', 'محاسبة'],
            'الحالة الوظيفية': ['active', 'active'],
            'الموقع': ['الرياض', 'جدة'],
            'المشروع': ['مشروع الرياض', 'مشروع جدة'],
            'البريد الإلكتروني': ['mohamed@company.com', 'fatima@company.com'],
            'الأقسام': ['تقنية المعلومات', 'المحاسبة'],
            'تاريخ الانضمام': ['2024-01-15', '2024-02-01'],
            'تاريخ انتهاء الإقامة': ['2025-12-31', '2025-11-30'],
            'حالة العقد': ['محدد المدة', 'دائم'],
            'حالة الرخصة': ['سارية', 'سارية'],
            'الجنسية': ['سعودي', 'مصري'],
            'ملاحظات': ['موظف متميز', '']
        }
        
        # إنشاء DataFrame
        df = pd.DataFrame(template_data)
        
        # إنشاء ملف Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # كتابة البيانات النموذجية
            df.to_excel(writer, sheet_name='البيانات النموذجية', index=False)
            
            # إنشاء ورقة فارغة للاستخدام
            empty_df = pd.DataFrame(columns=template_data.keys())
            empty_df.to_excel(writer, sheet_name='استيراد الموظفين', index=False)
            
            # إنشاء ورقة التعليمات
            instructions_data = {
                'العمود': list(template_data.keys()),
                'مطلوب/اختياري': ['مطلوب', 'مطلوب', 'مطلوب', 'مطلوب', 'اختياري', 'مطلوب', 'اختياري', 'اختياري', 'اختياري', 'اختياري', 'اختياري', 'اختياري', 'اختياري', 'اختياري', 'اختياري', 'اختياري', 'اختياري'],
                'التنسيق المطلوب': [
                    'نص',
                    'نص فريد',
                    'رقم من 10 أرقام',
                    'رقم جوال سعودي',
                    'رقم جوال (اختياري)',
                    'نص',
                    'active/inactive/on_leave',
                    'نص',
                    'نص',
                    'بريد إلكتروني صحيح',
                    'اسم القسم',
                    'YYYY-MM-DD',
                    'YYYY-MM-DD',
                    'نص',
                    'نص',
                    'اسم الجنسية',
                    'نص (اختياري)'
                ]
            }
            instructions_df = pd.DataFrame(instructions_data)
            instructions_df.to_excel(writer, sheet_name='التعليمات', index=False)
        
        output.seek(0)
        
        # تسجيل العملية
        audit = SystemAudit(
            action='download_template',
            entity_type='employee_import',
            entity_id=0,
            details='تم تحميل قالب استيراد الموظفين المحسن'
        )
        db.session.add(audit)
        db.session.commit()
        
        return send_file(
            output,
            download_name='قالب_استيراد_الموظفين_شامل.xlsx',
            as_attachment=True,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        flash(f'حدث خطأ في إنشاء القالب: {str(e)}', 'danger')
        return redirect(url_for('employees.import_excel'))

@employees_bp.route('/import/empty_template')
@login_required
@require_module_access(Module.EMPLOYEES, Permission.VIEW)
def empty_import_template():
    """Download empty Excel template for employee import"""
    try:
        import pandas as pd
        
        # إنشاء قالب فارغ مع جميع الحقول المطلوبة
        empty_template_data = {
            'الاسم الكامل': [],
            'رقم الموظف': [],
            'رقم الهوية الوطنية': [],
            'رقم الجوال': [],
            'الجوال الشخصي': [],
            'المسمى الوظيفي': [],
            'الحالة الوظيفية': [],
            'الموقع': [],
            'المشروع': [],
            'البريد الإلكتروني': [],
            'الأقسام': [],
            'تاريخ الانضمام': [],
            'تاريخ انتهاء الإقامة': [],
            'حالة العقد': [],
            'حالة الرخصة': [],
            'الجنسية': [],
            'ملاحظات': []
        }
        
        # إنشاء DataFrame فارغ
        df = pd.DataFrame(empty_template_data)
        
        # إنشاء ملف Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # كتابة القالب الفارغ
            df.to_excel(writer, sheet_name='استيراد الموظفين', index=False)
            
            # إنشاء ورقة التعليمات
            instructions_data = {
                'العمود': [
                    'الاسم الكامل', 'رقم الموظف', 'رقم الهوية الوطنية', 'رقم الجوال', 
                    'الجوال الشخصي', 'المسمى الوظيفي', 'الحالة الوظيفية', 'الموقع', 
                    'المشروع', 'البريد الإلكتروني', 'الأقسام', 'تاريخ الانضمام', 
                    'تاريخ انتهاء الإقامة', 'حالة العقد', 'حالة الرخصة', 'الجنسية', 'ملاحظات'
                ],
                'مطلوب/اختياري': [
                    'مطلوب', 'مطلوب', 'مطلوب', 'مطلوب', 'اختياري', 'مطلوب', 
                    'اختياري', 'اختياري', 'اختياري', 'اختياري', 'اختياري', 'اختياري', 
                    'اختياري', 'اختياري', 'اختياري', 'اختياري', 'اختياري'
                ],
                'التنسيق المطلوب': [
                    'نص', 'نص فريد', 'رقم من 10 أرقام', 'رقم جوال سعودي', 
                    'رقم جوال (اختياري)', 'نص', 'active/inactive/on_leave', 'نص', 
                    'نص', 'بريد إلكتروني صحيح', 'اسم القسم', 'YYYY-MM-DD', 
                    'YYYY-MM-DD', 'نص', 'نص', 'اسم الجنسية', 'نص (اختياري)'
                ],
                'مثال': [
                    'محمد أحمد علي', 'EMP001', '1234567890', '0501234567',
                    '0551234567', 'مطور برمجيات', 'active', 'الرياض',
                    'مشروع الرياض', 'mohamed@company.com', 'تقنية المعلومات', '2024-01-15',
                    '2025-12-31', 'محدد المدة', 'سارية', 'سعودي', 'موظف متميز'
                ]
            }
            instructions_df = pd.DataFrame(instructions_data)
            instructions_df.to_excel(writer, sheet_name='التعليمات والأمثلة', index=False)
        
        output.seek(0)
        
        # تسجيل العملية
        audit = SystemAudit(
            action='download_empty_template',
            entity_type='employee_import',
            entity_id=0,
            details='تم تحميل نموذج فارغ لاستيراد الموظفين'
        )
        db.session.add(audit)
        db.session.commit()
        
        return send_file(
            output,
            download_name='نموذج_استيراد_الموظفين_فارغ.xlsx',
            as_attachment=True,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        flash(f'حدث خطأ في إنشاء النموذج الفارغ: {str(e)}', 'danger')
        return redirect(url_for('employees.import_excel'))

@employees_bp.route('/<int:id>/update_status', methods=['POST'])
@login_required
@require_module_access(Module.EMPLOYEES, Permission.EDIT)
def update_status(id):
    """تحديث حالة الموظف"""
    employee = Employee.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            new_status = request.form.get('status')
            if new_status not in ['active', 'inactive', 'on_leave']:
                flash('حالة غير صالحة', 'danger')
                return redirect(url_for('employees.view', id=id))
            
            old_status = employee.status
            employee.status = new_status
            
            note = request.form.get('note', '')
            
            # إذا تم تغيير الحالة إلى غير نشط، فك ربط جميع أرقام SIM
            if new_status == 'inactive' and old_status != 'inactive':
                try:
                    # استيراد SimCard model
                    from models import SimCard
                    
                    # البحث عن جميع أرقام SIM المرتبطة بهذا الموظف
                    sim_cards = SimCard.query.filter_by(employee_id=employee.id).all()
                    
                    if sim_cards:
                        for sim_card in sim_cards:
                            # فك الربط
                            sim_card.employee_id = None
                            sim_card.assignment_date = None
                            
                            # تسجيل عملية فك الربط
                            from utils.audit_logger import log_activity
                            log_activity(
                                action="unassign_auto",
                                entity_type="SIM",
                                entity_id=sim_card.id,
                                details=f"فك ربط رقم SIM {sim_card.phone_number} تلقائياً بسبب تغيير حالة الموظف {employee.name} إلى غير نشط"
                            )
                        
                        flash(f'تم فك ربط {len(sim_cards)} رقم SIM مرتبط بالموظف تلقائياً', 'info')
                
                except Exception as e:
                    current_app.logger.error(f"Error unassigning SIM cards for inactive employee: {str(e)}")
                    # لا نتوقف عن تحديث حالة الموظف حتى لو فشل فك ربط الأرقام
            
            # توثيق التغيير في السجل
            status_names = {
                'active': 'نشط',
                'inactive': 'غير نشط',
                'on_leave': 'في إجازة'
            }
            
            details = f'تم تغيير حالة الموظف {employee.name} من "{status_names.get(old_status, old_status)}" إلى "{status_names.get(new_status, new_status)}"'
            if note:
                details += f" - ملاحظات: {note}"
                
            # تسجيل العملية
            audit = SystemAudit(
                action='update_status',
                entity_type='employee',
                entity_id=employee.id,
                details=details
            )
            db.session.add(audit)
            db.session.commit()
            
            flash(f'تم تحديث حالة الموظف إلى {status_names.get(new_status, new_status)} بنجاح', 'success')
            
            # العودة إلى الصفحة السابقة
            referrer = request.referrer
            if referrer and '/departments/' in referrer:
                department_id = referrer.split('/departments/')[1].split('/')[0]
                return redirect(url_for('departments.view', id=department_id))
            
            return redirect(url_for('employees.view', id=id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء تحديث حالة الموظف: {str(e)}', 'danger')
            return redirect(url_for('employees.view', id=id))

@employees_bp.route('/export')
@login_required
@require_module_access(Module.EMPLOYEES, Permission.VIEW)
def export_excel():
    """Export employees to Excel file"""
    try:
        employees = Employee.query.options(
            db.joinedload(Employee.departments),
            db.joinedload(Employee.nationality_rel)
        ).all()
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

@employees_bp.route('/export_comprehensive')
@login_required
@require_module_access(Module.EMPLOYEES, Permission.VIEW)
def export_comprehensive():
    """تصدير شامل لبيانات الموظفين مع جميع التفاصيل والعُهد والمعلومات البنكية"""
    try:
        from utils.basic_comprehensive_export import generate_comprehensive_employee_excel
        
        employees = Employee.query.options(
            db.joinedload(Employee.departments),
            db.joinedload(Employee.nationality_rel),
            db.joinedload(Employee.salaries),
            db.joinedload(Employee.attendances),
            db.joinedload(Employee.documents)
        ).all()
        
        output = generate_comprehensive_employee_excel(employees)
        
        # تسجيل العملية
        audit = SystemAudit(
            action='export_comprehensive',
            entity_type='employee',
            entity_id=0,
            details=f'تم التصدير الشامل لبيانات {len(employees)} موظف مع جميع التفاصيل'
        )
        db.session.add(audit)
        db.session.commit()
        
        # إنشاء اسم الملف مع التاريخ
        current_date = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'تصدير_شامل_الموظفين_{current_date}.xlsx'
        
        return send_file(
            output,
            download_name=filename,
            as_attachment=True,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        import traceback
        print(f"Error in comprehensive export: {str(e)}")
        print(traceback.format_exc())
        flash(f'حدث خطأ أثناء التصدير الشامل: {str(e)}', 'danger')
        return redirect(url_for('employees.index'))
        
@employees_bp.route('/<int:id>/export_attendance_excel')
@login_required
@require_module_access(Module.EMPLOYEES, Permission.VIEW)
def export_attendance_excel(id):
    """تصدير بيانات الحضور كملف إكسل"""
    try:
        # الحصول على بيانات الموظف
        employee = Employee.query.get_or_404(id)
        
        # الحصول على الشهر والسنة من معاملات الطلب
        month = request.args.get('month')
        year = request.args.get('year')
        
        # تحويل البيانات إلى أرقام صحيحة إذا كانت موجودة
        if month:
            try:
                month = int(month)
            except (ValueError, TypeError):
                flash('قيمة الشهر غير صالحة، تم استخدام الشهر الحالي', 'warning')
                month = None
                
        if year:
            try:
                year = int(year)
            except (ValueError, TypeError):
                flash('قيمة السنة غير صالحة، تم استخدام السنة الحالية', 'warning')
                year = None
        
        # توليد ملف الإكسل
        output = export_employee_attendance_to_excel(employee, month, year)
        
        # تعيين اسم الملف مع التاريخ الحالي
        current_date = datetime.now().strftime('%Y%m%d')
        
        # إضافة الشهر والسنة إلى اسم الملف إذا كانا موجودين
        if month and year:
            filename = f"attendance_{employee.name}_{year}_{month}_{current_date}.xlsx"
        else:
            # استخدام الشهر والسنة الحالية إذا لم يتم توفيرهما
            current_month = datetime.now().month
            current_year = datetime.now().year
            filename = f"attendance_{employee.name}_{current_year}_{current_month}_{current_date}.xlsx"
        
        # تسجيل الإجراء
        audit = SystemAudit(
            action='export',
            entity_type='attendance',
            entity_id=employee.id,
            details=f'تم تصدير سجل الحضور للموظف: {employee.name}'
        )
        db.session.add(audit)
        db.session.commit()
        
        # إرسال ملف الإكسل
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        # طباعة تتبع الخطأ في سجل الخادم للمساعدة في التشخيص
        import traceback
        print(f"Error exporting attendance: {str(e)}")
        print(traceback.format_exc())
        
        flash(f'حدث خطأ أثناء تصدير ملف الحضور: {str(e)}', 'danger')
        return redirect(url_for('employees.view', id=id))

@employees_bp.route('/<int:id>/upload_image', methods=['POST'])
@login_required
@require_module_access(Module.EMPLOYEES, Permission.EDIT)
def upload_image(id):
    """رفع صورة للموظف (الصورة الشخصية، صورة الهوية، أو صورة الرخصة)"""
    employee = Employee.query.get_or_404(id)
    
    image_type = request.form.get('image_type')
    if not image_type or image_type not in ['profile', 'national_id', 'license']:
        flash('نوع الصورة غير صحيح', 'danger')
        return redirect(url_for('employees.view', id=id))
    
    if 'image' not in request.files:
        flash('لم يتم اختيار ملف', 'danger')
        return redirect(url_for('employees.view', id=id))
    
    file = request.files['image']
    if file.filename == '':
        flash('لم يتم اختيار ملف', 'danger')
        return redirect(url_for('employees.view', id=id))
    
    # حفظ الصورة
    image_path = save_employee_image(file, employee.employee_id, image_type)
    if image_path:
        try:
            # حذف الصورة القديمة إذا كانت موجودة
            old_path = None
            if image_type == 'profile':
                old_path = employee.profile_image
                employee.profile_image = image_path
            elif image_type == 'national_id':
                old_path = employee.national_id_image
                employee.national_id_image = image_path
            elif image_type == 'license':
                old_path = employee.license_image
                employee.license_image = image_path
            
            # حذف الصورة القديمة من الملفات
            if old_path:
                old_file_path = os.path.join('static', old_path)
                if os.path.exists(old_file_path):
                    os.remove(old_file_path)
            
            db.session.commit()
            
            # رسائل النجاح حسب نوع الصورة
            success_messages = {
                'profile': 'تم رفع الصورة الشخصية بنجاح',
                'national_id': 'تم رفع صورة الهوية بنجاح',
                'license': 'تم رفع صورة الرخصة بنجاح'
            }
            flash(success_messages[image_type], 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'خطأ في حفظ الصورة: {str(e)}', 'danger')
    else:
        flash('فشل في رفع الصورة. تأكد من أن الملف من النوع المسموح (PNG, JPG, JPEG, GIF)', 'danger')
    
    return redirect(url_for('employees.view', id=id))


@employees_bp.route('/<int:id>/basic_report')
@login_required
@require_module_access(Module.EMPLOYEES, Permission.VIEW)
def basic_report(id):
    """تقرير المعلومات الأساسية للموظف"""
    try:
                # طباعة رسالة تشخيصية
        print("بدء إنشاء التقرير الشامل للموظف")
        
        # التحقق من وجود الموظف
        employee = Employee.query.get_or_404(id)
        print(f"تم العثور على الموظف: {employee.name}")
        
        # إنشاء ملف PDF
        print("استدعاء دالة إنشاء PDF")
        pdf_buffer = generate_employee_basic_pdf(id)
        print("تم استلام ناتج ملف PDF")
        
        if not pdf_buffer:
            flash('لم يتم العثور على بيانات كافية لإنشاء التقرير', 'warning')
            return redirect(url_for('employees.view', id=id))
        
        if pdf_buffer:
            employee = Employee.query.get_or_404(id)
            current_date = datetime.now().strftime('%Y%m%d')
            filename = f'تقرير_أساسي_{employee.name}_{current_date}.pdf'
            
            # تسجيل الإجراء
            audit = SystemAudit(
                action='export',
                entity_type='employee_basic_report',
                entity_id=employee.id,
                details=f'تم تصدير التقرير الأساسي للموظف: {employee.name}'
            )
            db.session.add(audit)
            db.session.commit()
            
            return send_file(
                pdf_buffer,
                as_attachment=True,
                download_name=filename,
                mimetype='application/pdf'
            )
        else:
            flash('خطأ في إنشاء ملف PDF', 'danger')
            return redirect(url_for('employees.view', id=id))
    except Exception as e:
        flash(f'خطأ في تصدير PDF: {str(e)}', 'danger')
        return redirect(url_for('employees.view', id=id))


@employees_bp.route('/<int:id>/comprehensive_report')
@login_required
@require_module_access(Module.EMPLOYEES, Permission.VIEW)
def comprehensive_report(id):
    """تقرير شامل عن الموظف بصيغة PDF"""
    try:
        # طباعة رسالة تشخيصية
        print("بدء إنشاء التقرير الشامل للموظف")
        
        # التحقق من وجود الموظف
        employee = Employee.query.get_or_404(id)
        print(f"تم العثور على الموظف: {employee.name}")
        
        # إنشاء ملف PDF
        print("استدعاء دالة إنشاء PDF")
        output = generate_employee_comprehensive_pdf(id)
        print("تم استلام ناتج ملف PDF")
        
        if not output:
            flash('لم يتم العثور على بيانات كافية لإنشاء التقرير', 'warning')
            return redirect(url_for('employees.view', id=id))
        
        # اسم الملف المُصدَّر
        filename = f"تقرير_شامل_{employee.name}_{datetime.now().strftime('%Y%m%d')}.pdf"
        print(f"اسم الملف: {filename}")
        
        # تسجيل عملية التصدير
        audit = SystemAudit(
            action='export',
            entity_type='employee_report',
            entity_id=employee.id,
            details=f'تم إنشاء تقرير شامل للموظف: {employee.name}'
        )
        db.session.add(audit)
        db.session.commit()
        print("تم تسجيل العملية في سجل النظام")
        
        # طباعة نوع ناتج الملف للتشخيص
        print(f"نوع ناتج الملف: {type(output)}")
        print(f"حجم البيانات: {output.getbuffer().nbytes} بايت")
        
        # إرسال ملف PDF
        print("إرسال الملف للمتصفح")
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        # طباعة تتبع الخطأ في سجل الخادم للمساعدة في التشخيص
        import traceback
        print(f"Error generating comprehensive report: {str(e)}")
        print(traceback.format_exc())
        
        flash(f'حدث خطأ أثناء إنشاء التقرير الشامل: {str(e)}', 'danger')
        return redirect(url_for('employees.view', id=id))


@employees_bp.route('/<int:id>/comprehensive_report_excel')
@login_required
@require_module_access(Module.EMPLOYEES, Permission.VIEW)
def comprehensive_report_excel(id):
    """تقرير شامل عن الموظف بصيغة Excel"""
    try:
        # التحقق من وجود الموظف
        employee = Employee.query.get_or_404(id)
        
        # إنشاء ملف Excel
        output = generate_employee_comprehensive_excel(id)
        
        if not output:
            flash('لم يتم العثور على بيانات كافية لإنشاء التقرير', 'warning')
            return redirect(url_for('employees.view', id=id))
        
        # اسم الملف المُصدَّر
        filename = f"تقرير_شامل_{employee.name}_{datetime.now().strftime('%Y%m%d')}.xlsx"
        
        # تسجيل عملية التصدير
        audit = SystemAudit(
            action='export',
            entity_type='employee_report_excel',
            entity_id=employee.id,
            details=f'تم تصدير تقرير شامل (إكسل) للموظف: {employee.name}'
        )
        db.session.add(audit)
        db.session.commit()
        
        # إرسال ملف الإكسل
        return send_file(
            output,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        # طباعة تتبع الخطأ في سجل الخادم للمساعدة في التشخيص
        import traceback
        print(f"Error generating comprehensive Excel report: {str(e)}")
        print(traceback.format_exc())
        
        flash(f'حدث خطأ أثناء إنشاء التقرير الشامل (إكسل): {str(e)}', 'danger')
        return redirect(url_for('employees.view', id=id))
