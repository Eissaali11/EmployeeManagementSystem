"""
مسارات ومعالجات الواجهة المحمولة
نُظم - النسخة المحمولة
"""

import os
import json
import uuid
from datetime import datetime, timedelta, date
from sqlalchemy import extract, func, cast, Date
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, DateField, TextAreaField, DecimalField
from wtforms.validators import DataRequired, Email, Length, ValidationError, Optional

from models import db, User, Employee, Department, Document, Vehicle, Attendance, Salary, FeesCost as Fee, VehicleChecklist, VehicleChecklistItem, VehicleMaintenance, VehicleMaintenanceImage, VehicleFuelConsumption, UserPermission, Module, Permission, SystemAudit, UserRole, VehiclePeriodicInspection, VehicleSafetyCheck, VehicleHandover, VehicleHandoverImage, VehicleChecklistImage, VehicleDamageMarker
from app import app
from utils.hijri_converter import convert_gregorian_to_hijri, format_hijri_date
from utils.decorators import module_access_required, permission_required

# إنشاء مخطط المسارات
mobile_bp = Blueprint('mobile', __name__)

# نموذج تسجيل الدخول
class LoginForm(FlaskForm):
    username = StringField('اسم المستخدم', validators=[DataRequired('اسم المستخدم مطلوب')])
    password = PasswordField('كلمة المرور', validators=[DataRequired('كلمة المرور مطلوبة')])
    remember = BooleanField('تذكرني')
    submit = SubmitField('تسجيل الدخول')

# صفحة الـ Splash Screen
@mobile_bp.route('/splash')
def splash():
    """صفحة البداية الترحيبية للنسخة المحمولة"""
    return render_template('mobile/splash.html')

# الصفحة الرئيسية - النسخة المحمولة
@mobile_bp.route('/')
def root():
    """إعادة توجيه إلى صفحة البداية الترحيبية"""
    return redirect(url_for('mobile.splash'))

# لوحة المعلومات - النسخة المحمولة
@mobile_bp.route('/dashboard')
@login_required
def index():
    """الصفحة الرئيسية للنسخة المحمولة"""
    # التحقق من صلاحيات المستخدم للوصول إلى لوحة التحكم
    from models import Module, UserRole
    
    # إذا كان المستخدم لا يملك صلاحيات لرؤية لوحة التحكم، توجيهه إلى أول وحدة مصرح له بالوصول إليها
    if not (current_user.role == UserRole.ADMIN or current_user.has_module_access(Module.DASHBOARD)):
        # توجيه المستخدم إلى أول وحدة مصرح له بالوصول إليها
        if current_user.has_module_access(Module.EMPLOYEES):
            return redirect(url_for('mobile.employees'))
        elif current_user.has_module_access(Module.DEPARTMENTS):
            return redirect(url_for('mobile.departments'))
        elif current_user.has_module_access(Module.ATTENDANCE):
            return redirect(url_for('mobile.attendance'))
        elif current_user.has_module_access(Module.SALARIES):
            return redirect(url_for('mobile.salaries'))
        elif current_user.has_module_access(Module.DOCUMENTS):
            return redirect(url_for('mobile.documents'))
        elif current_user.has_module_access(Module.VEHICLES):
            return redirect(url_for('mobile.vehicles'))
        elif current_user.has_module_access(Module.REPORTS):
            return redirect(url_for('mobile.reports'))
        elif current_user.has_module_access(Module.FEES):
            return redirect(url_for('mobile.fees'))
        elif current_user.has_module_access(Module.USERS):
            return redirect(url_for('mobile.users'))
        # إذا لم يجد أي صلاحيات مناسبة، عرض صفحة مقيدة
    # الإحصائيات الأساسية
    stats = {
        'employees_count': Employee.query.count(),
        'departments_count': Department.query.count(),
        'documents_count': Document.query.count(),
        'vehicles_count': Vehicle.query.count(),
    }
    
    # التحقق من وجود إشعارات غير مقروءة (يمكن استبداله بالتنفيذ الفعلي)
    notifications_count = 3  # مثال: 3 إشعارات غير مقروءة
    
    # الوثائق التي ستنتهي قريباً
    today = datetime.now().date()
    expiring_documents = Document.query.filter(Document.expiry_date >= today).order_by(Document.expiry_date).limit(5).all()
    
    # إضافة عدد الأيام المتبقية لكل وثيقة
    for doc in expiring_documents:
        doc.days_remaining = (doc.expiry_date - today).days
    
    # السجلات الغائبة اليوم
    today_str = today.strftime('%Y-%m-%d')
    absences = Attendance.query.filter_by(date=today_str, status='غائب').all()
    
    return render_template('mobile/index.html', 
                            stats=stats,
                            expiring_documents=expiring_documents,
                            absences=absences,
                            notifications_count=notifications_count,
                            now=datetime.now())

# صفحة تسجيل الدخول - النسخة المحمولة
@mobile_bp.route('/login', methods=['GET', 'POST'])
def login():
    """صفحة تسجيل الدخول للنسخة المحمولة"""
    if current_user.is_authenticated:
        # نستخدم لوجيك التوجيه المدمج في mobile.index
        return redirect(url_for('mobile.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.username.data).first()
        
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('mobile.index'))
        else:
            flash('اسم المستخدم أو كلمة المرور غير صحيحة', 'danger')
    
    return render_template('mobile/login.html', form=form)

# تسجيل الدخول باستخدام Google - النسخة المحمولة
@mobile_bp.route('/login/google')
def google_login():
    """تسجيل الدخول باستخدام Google للنسخة المحمولة"""
    # هنا يتم التعامل مع تسجيل الدخول باستخدام Google
    # يمكن استخدام نفس الكود الموجود في النسخة الأصلية مع تعديل مسار التوجيه
    return redirect(url_for('auth.google_login', next=url_for('mobile.index')))

# تسجيل الخروج - النسخة المحمولة
@mobile_bp.route('/logout')
@login_required
def logout():
    """تسجيل الخروج من النسخة المحمولة"""
    logout_user()
    return redirect(url_for('mobile.login'))

# نسيت كلمة المرور - النسخة المحمولة
@mobile_bp.route('/forgot-password')
def forgot_password():
    """صفحة نسيت كلمة المرور للنسخة المحمولة"""
    # يمكن تنفيذ هذه الوظيفة لاحقًا
    return render_template('mobile/forgot_password.html')

# صفحة الموظفين - النسخة المحمولة
@mobile_bp.route('/employees')
@login_required
def employees():
    """صفحة الموظفين للنسخة المحمولة"""
    page = request.args.get('page', 1, type=int)
    per_page = 20  # عدد العناصر في الصفحة الواحدة
    
    # إنشاء الاستعلام الأساسي
    query = Employee.query
    
    # تطبيق الفلترة حسب الاستعلام
    if request.args.get('search'):
        search_term = f"%{request.args.get('search')}%"
        query = query.filter(
            (Employee.name.like(search_term)) |
            (Employee.employee_id.like(search_term)) |
            (Employee.job_title.like(search_term))
        )
    
    if request.args.get('department_id'):
        query = query.filter_by(department_id=request.args.get('department_id'))
    
    # ترتيب النتائج حسب الاسم
    query = query.order_by(Employee.name)
    
    # تنفيذ الاستعلام مع الصفحات
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    employees = pagination.items
    
    # الحصول على قائمة الأقسام للفلترة
    departments = Department.query.order_by(Department.name).all()
    
    return render_template('mobile/employees.html',
                           employees=employees,
                           pagination=pagination,
                           departments=departments)

# صفحة إضافة موظف جديد - النسخة المحمولة
@mobile_bp.route('/employees/add', methods=['GET', 'POST'])
@login_required
def add_employee():
    """صفحة إضافة موظف جديد للنسخة المحمولة"""
    # يمكن تنفيذ هذه الوظيفة لاحقًا
    return render_template('mobile/add_employee.html')

# صفحة تفاصيل الموظف - النسخة المحمولة
@mobile_bp.route('/employees/<int:employee_id>')
@login_required
def employee_details(employee_id):
    """صفحة تفاصيل الموظف للنسخة المحمولة"""
    employee = Employee.query.get_or_404(employee_id)
    
    # الحصول على التاريخ الحالي وتاريخ بداية ونهاية الشهر الحالي
    current_date = datetime.now().date()
    current_month_start = date(current_date.year, current_date.month, 1)
    next_month = current_date.month + 1 if current_date.month < 12 else 1
    next_year = current_date.year if current_date.month < 12 else current_date.year + 1
    current_month_end = date(next_year, next_month, 1) - timedelta(days=1)
    
    # استعلام سجلات الحضور للموظف خلال الشهر الحالي
    attendance_records = Attendance.query.filter(
        Attendance.employee_id == employee_id,
        Attendance.date >= current_month_start.strftime('%Y-%m-%d'),
        Attendance.date <= current_month_end.strftime('%Y-%m-%d')
    ).order_by(Attendance.date.desc()).all()
    
    # استعلام أحدث راتب للموظف
    # ترتيب حسب السنة ثم الشهر بترتيب تنازلي
    salary = Salary.query.filter_by(employee_id=employee_id).order_by(Salary.year.desc(), Salary.month.desc()).first()
    
    # استعلام الوثائق الخاصة بالموظف
    documents = Document.query.filter_by(employee_id=employee_id).all()
    
    return render_template('mobile/employee_details.html', 
                          employee=employee,
                          attendance_records=attendance_records,
                          salary=salary,
                          documents=documents,
                          current_date=current_date)

# صفحة تعديل موظف - النسخة المحمولة
@mobile_bp.route('/employees/<int:employee_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_employee(employee_id):
    """صفحة تعديل موظف للنسخة المحمولة"""
    employee = Employee.query.get_or_404(employee_id)
    # يمكن تنفيذ هذه الوظيفة لاحقًا
    return render_template('mobile/edit_employee.html', employee=employee)

# صفحة الحضور والغياب - النسخة المحمولة
@mobile_bp.route('/attendance')
@login_required
def attendance():
    """صفحة الحضور والغياب للنسخة المحمولة"""
    page = request.args.get('page', 1, type=int)
    per_page = 20  # عدد العناصر في الصفحة الواحدة
    
    # بيانات مؤقتة - يمكن استبدالها بالبيانات الفعلية من قاعدة البيانات
    employees = Employee.query.order_by(Employee.name).all()
    attendance_records = []
    
    # إحصائيات اليوم
    current_date = datetime.now().date()
    today_stats = {'present': 0, 'absent': 0, 'leave': 0, 'total': len(employees)}
    
    return render_template('mobile/attendance.html',
                          employees=employees,
                          attendance_records=attendance_records,
                          current_date=current_date,
                          today_stats=today_stats,
                          pagination=None)

# صفحة تصدير بيانات الحضور - النسخة المحمولة
@mobile_bp.route('/attendance/export', methods=['GET', 'POST'])
@login_required
def export_attendance():
    """صفحة تصدير بيانات الحضور إلى Excel للنسخة المحمولة"""
    # الحصول على قائمة الأقسام للاختيار
    departments = Department.query.order_by(Department.name).all()
    
    if request.method == 'POST':
        # معالجة النموذج المرسل
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        department_id = request.form.get('department_id')
        
        # إعادة توجيه إلى مسار التصدير في النسخة غير المحمولة مع وسيطات البحث
        redirect_url = url_for('attendance.export_excel')
        params = []
        
        if start_date:
            params.append(f'start_date={start_date}')
        if end_date:
            params.append(f'end_date={end_date}')
        if department_id:
            params.append(f'department_id={department_id}')
        
        if params:
            redirect_url = f"{redirect_url}?{'&'.join(params)}"
        
        return redirect(redirect_url)
    
    return render_template('mobile/attendance_export.html', departments=departments)

# إضافة سجل حضور جديد - النسخة المحمولة
@mobile_bp.route('/attendance/add', methods=['GET', 'POST'])
@login_required
def add_attendance():
    """إضافة سجل حضور جديد للنسخة المحمولة"""
    # الحصول على قائمة الموظفين
    employees = Employee.query.order_by(Employee.name).all()
    current_date = datetime.now().date()
    
    if request.method == 'POST':
        # معالجة النموذج المرسل
        employee_id = request.form.get('employee_id')
        date_str = request.form.get('date')
        status = request.form.get('status')
        check_in = request.form.get('check_in')
        check_out = request.form.get('check_out')
        notes = request.form.get('notes')
        quick = request.form.get('quick') == 'true'
        action = request.form.get('action')
        all_employees = request.form.get('all_employees') == 'true'
        
        # تحديد التاريخ
        if date_str:
            attendance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            attendance_date = current_date
        
        # معالجة تسجيل حضور الجميع
        if all_employees:
            # الحصول على جميع الموظفين
            all_emps = Employee.query.order_by(Employee.name).all()
            success_count = 0
            
            if all_emps and status:
                for emp in all_emps:
                    # إنشاء سجل حضور لكل موظف
                    new_attendance = Attendance(
                        employee_id=emp.id,
                        date=attendance_date,
                        status=status,
                        check_in=check_in if status == 'حاضر' else None,
                        check_out=check_out if status == 'حاضر' else None,
                        notes=notes
                    )
                    
                    try:
                        db.session.add(new_attendance)
                        success_count += 1
                    except Exception as e:
                        print(f"خطأ في إضافة سجل الحضور للموظف {emp.name}: {str(e)}")
                
                if success_count > 0:
                    try:
                        db.session.commit()
                        flash(f'تم تسجيل حضور {success_count} موظف بنجاح', 'success')
                        return redirect(url_for('mobile.attendance'))
                    except Exception as e:
                        db.session.rollback()
                        flash('حدث خطأ أثناء حفظ البيانات. يرجى المحاولة مرة أخرى.', 'danger')
                        print(f"خطأ في حفظ سجلات الحضور: {str(e)}")
                else:
                    flash('لم يتم تسجيل أي سجلات حضور', 'warning')
            else:
                flash('يرجى اختيار حالة الحضور', 'warning')
        else:
            # التحقق من أن الموظف موجود
            employee = Employee.query.get(employee_id) if employee_id else None
            
            if employee:
                if quick and action:
                    # معالجة التسجيل السريع
                    now_time = datetime.now().time()
                    
                    if action == 'check_in':
                        status = 'حاضر'
                        check_in = now_time.strftime('%H:%M')
                        check_out = None
                        notes = "تم تسجيل الحضور عبر النظام المحمول."
                    elif action == 'check_out':
                        status = 'حاضر'
                        check_in = None
                        check_out = now_time.strftime('%H:%M')
                        notes = "تم تسجيل الانصراف عبر النظام المحمول."
                
                # إنشاء سجل الحضور الجديد
                new_attendance = Attendance(
                    employee_id=employee.id,
                    date=attendance_date,
                    status=status,
                    check_in=check_in,
                    check_out=check_out,
                    notes=notes
                )
                
                try:
                    db.session.add(new_attendance)
                    db.session.commit()
                    flash('تم تسجيل الحضور بنجاح', 'success')
                    return redirect(url_for('mobile.attendance'))
                except Exception as e:
                    db.session.rollback()
                    flash('حدث خطأ أثناء تسجيل الحضور. يرجى المحاولة مرة أخرى.', 'danger')
                    print(f"خطأ في إضافة سجل الحضور: {str(e)}")
            else:
                flash('يرجى اختيار موظف صالح', 'warning')
    
    # المتغيرات المطلوبة لعرض الصفحة - استخدام الصفحة الجديدة لتجنب الخطأ
    return render_template('mobile/add_attendance_new.html',
                          employees=employees,
                          current_date=current_date)

# تعديل سجل حضور - النسخة المحمولة
@mobile_bp.route('/attendance/<int:record_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_attendance(record_id):
    """تعديل سجل حضور للنسخة المحمولة"""
    # يمكن تنفيذ هذه الوظيفة لاحقًا
    attendance = Attendance.query.get_or_404(record_id)
    employees = Employee.query.order_by(Employee.name).all()
    current_date = datetime.now().date()
    
    return render_template('mobile/edit_attendance.html',
                          attendance=attendance,
                          employees=employees,
                          current_date=current_date)

# صفحة الأقسام - النسخة المحمولة
@mobile_bp.route('/departments')
@login_required
def departments():
    """صفحة الأقسام للنسخة المحمولة"""
    # الحصول على قائمة الأقسام
    departments = Department.query.all()
    employees_count = Employee.query.count()
    
    return render_template('mobile/departments.html',
                          departments=departments,
                          employees_count=employees_count)

# صفحة إضافة قسم جديد - النسخة المحمولة
@mobile_bp.route('/departments/add', methods=['GET', 'POST'])
@login_required
def add_department():
    """صفحة إضافة قسم جديد للنسخة المحمولة"""
    # الموظفين كمديرين محتملين للقسم
    employees = Employee.query.order_by(Employee.name).all()
    
    # ستتم إضافة وظيفة إضافة قسم جديد لاحقاً
    return render_template('mobile/add_department.html', 
                          employees=employees)

# صفحة تفاصيل القسم - النسخة المحمولة
@mobile_bp.route('/departments/<int:department_id>')
@login_required
def department_details(department_id):
    """صفحة تفاصيل القسم للنسخة المحمولة"""
    department = Department.query.get_or_404(department_id)
    return render_template('mobile/department_details.html', department=department)

# صفحة الرواتب - النسخة المحمولة
@mobile_bp.route('/salaries')
@login_required
def salaries():
    """صفحة الرواتب للنسخة المحمولة"""
    page = request.args.get('page', 1, type=int)
    per_page = 20  # عدد العناصر في الصفحة الواحدة
    
    # جلب بيانات الموظفين
    employees = Employee.query.order_by(Employee.name).all()
    
    # إحصائيات الرواتب
    current_year = datetime.now().year
    current_month = datetime.now().month
    selected_year = request.args.get('year', current_year, type=int)
    selected_month = request.args.get('month', current_month, type=int)
    
    # فلترة الموظف
    employee_id_str = request.args.get('employee_id', '')
    employee_id = int(employee_id_str) if employee_id_str and employee_id_str.isdigit() else None
    
    # تحويل الشهر إلى اسمه بالعربية
    month_names = {
        1: 'يناير', 2: 'فبراير', 3: 'مارس', 4: 'أبريل', 
        5: 'مايو', 6: 'يونيو', 7: 'يوليو', 8: 'أغسطس',
        9: 'سبتمبر', 10: 'أكتوبر', 11: 'نوفمبر', 12: 'ديسمبر'
    }
    selected_month_name = month_names.get(selected_month, '')
    
    # قاعدة الاستعلام الأساسية للرواتب
    query = Salary.query.filter(
        Salary.year == selected_year,
        Salary.month == selected_month
    )
    
    # تطبيق فلتر الموظف إذا تم تحديده
    if employee_id:
        query = query.filter(Salary.employee_id == employee_id)
        
    # تطبيق فلتر حالة الدفع إذا تم تحديده
    is_paid = request.args.get('is_paid')
    if is_paid is not None:
        is_paid_bool = True if is_paid == '1' else False
        query = query.filter(Salary.is_paid == is_paid_bool)
        
    # تطبيق فلتر البحث إذا تم تحديده
    search_term = request.args.get('search', '')
    if search_term:
        search_pattern = f"%{search_term}%"
        query = query.join(Employee).filter(Employee.name.like(search_pattern))
    
    # تنفيذ الاستعلام والحصول على نتائج مع التصفح
    paginator = query.order_by(Salary.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    salaries = paginator.items
    
    # حساب إجماليات الرواتب
    total_salaries = query.all()
    salary_stats = {
        'total_basic': sum(salary.basic_salary for salary in total_salaries),
        'total_allowances': sum(salary.allowances for salary in total_salaries),
        'total_deductions': sum(salary.deductions for salary in total_salaries),
        'total_net': sum(salary.net_salary for salary in total_salaries)
    }
    
    return render_template('mobile/salaries.html',
                          employees=employees,
                          salaries=salaries,
                          current_year=current_year,
                          current_month=current_month,
                          selected_year=selected_year,
                          selected_month=selected_month,
                          selected_month_name=selected_month_name,
                          employee_id=employee_id,
                          salary_stats=salary_stats,
                          pagination=paginator)

# إضافة راتب جديد - النسخة المحمولة
@mobile_bp.route('/salaries/add', methods=['GET', 'POST'])
@login_required
def add_salary():
    """إضافة راتب جديد للنسخة المحمولة"""
    # يمكن تنفيذ هذه الوظيفة لاحقًا
    return render_template('mobile/add_salary.html')

# تفاصيل الراتب - النسخة المحمولة
@mobile_bp.route('/salaries/<int:salary_id>')
@login_required
def salary_details(salary_id):
    """تفاصيل الراتب للنسخة المحمولة"""
    # يمكن تنفيذ هذه الوظيفة لاحقًا
    return render_template('mobile/salary_details.html')

# صفحة الوثائق - النسخة المحمولة
@mobile_bp.route('/documents')
@login_required
def documents():
    """صفحة الوثائق للنسخة المحمولة"""
    # فلترة الوثائق بناءً على البارامترات
    employee_id_str = request.args.get('employee_id', '')
    employee_id = int(employee_id_str) if employee_id_str and employee_id_str.isdigit() else None
    document_type = request.args.get('document_type')
    status = request.args.get('status')  # valid, expiring, expired
    page = request.args.get('page', 1, type=int)
    per_page = 20  # عدد العناصر في الصفحة الواحدة
    
    # قم باستعلام قاعدة البيانات للحصول على قائمة الموظفين
    employees = Employee.query.order_by(Employee.name).all()
    
    # إنشاء استعلام أساسي للوثائق
    query = Document.query
    
    # إضافة فلاتر إلى الاستعلام إذا تم توفيرها
    if employee_id:
        query = query.filter(Document.employee_id == employee_id)
    
    if document_type:
        query = query.filter(Document.document_type == document_type)
    
    # الحصول على التاريخ الحالي
    current_date = datetime.now().date()
    
    # إضافة فلتر حالة الوثيقة
    if status:
        if status == 'valid':
            # وثائق سارية المفعول (تاريخ انتهاء الصلاحية بعد 60 يوم على الأقل من اليوم)
            valid_date = current_date + timedelta(days=60)
            query = query.filter(Document.expiry_date >= valid_date)
        elif status == 'expiring':
            # وثائق على وشك الانتهاء (تاريخ انتهاء الصلاحية خلال 60 يوم من اليوم)
            expiring_min_date = current_date
            expiring_max_date = current_date + timedelta(days=60)
            query = query.filter(Document.expiry_date >= expiring_min_date, 
                                Document.expiry_date <= expiring_max_date)
        elif status == 'expired':
            # وثائق منتهية الصلاحية (تاريخ انتهاء الصلاحية قبل اليوم)
            query = query.filter(Document.expiry_date < current_date)
    
    # تنفيذ الاستعلام مع ترتيب النتائج حسب تاريخ انتهاء الصلاحية
    query = query.order_by(Document.expiry_date)
    
    # تقسيم النتائج إلى صفحات
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    documents = pagination.items
    
    # حساب إحصائيات الوثائق
    valid_count = Document.query.filter(Document.expiry_date >= current_date + timedelta(days=60)).count()
    expiring_count = Document.query.filter(Document.expiry_date >= current_date, 
                                          Document.expiry_date <= current_date + timedelta(days=60)).count()
    expired_count = Document.query.filter(Document.expiry_date < current_date).count()
    total_count = Document.query.count()
    
    document_stats = {
        'valid': valid_count,
        'expiring': expiring_count,
        'expired': expired_count,
        'total': total_count
    }
    
    return render_template('mobile/documents.html',
                          employees=employees,
                          documents=documents,
                          current_date=current_date,
                          document_stats=document_stats,
                          pagination=pagination)

# إضافة وثيقة جديدة - النسخة المحمولة
@mobile_bp.route('/documents/add', methods=['GET', 'POST'])
@login_required
def add_document():
    """إضافة وثيقة جديدة للنسخة المحمولة"""
    # قائمة الموظفين للاختيار
    employees = Employee.query.order_by(Employee.name).all()
    current_date = datetime.now().date()
    
    # أنواع الوثائق المتاحة
    document_types = [
        'هوية وطنية',
        'إقامة',
        'جواز سفر',
        'رخصة قيادة',
        'شهادة صحية',
        'شهادة تأمين',
        'أخرى'
    ]
    
    # يمكن تنفيذ هذه الوظيفة لاحقًا
    return render_template('mobile/add_document.html',
                          employees=employees,
                          document_types=document_types,
                          current_date=current_date)

# تفاصيل وثيقة - النسخة المحمولة
@mobile_bp.route('/documents/<int:document_id>')
@login_required
def document_details(document_id):
    """تفاصيل وثيقة للنسخة المحمولة"""
    # الحصول على بيانات الوثيقة من قاعدة البيانات
    document = Document.query.get_or_404(document_id)
    
    # الحصول على التاريخ الحالي للمقارنة مع تاريخ انتهاء الصلاحية
    current_date = datetime.now().date()
    
    # حساب المدة المتبقية (أو المنقضية) لصلاحية الوثيقة
    days_remaining = None
    if document.expiry_date:
        days_remaining = (document.expiry_date - current_date).days
        
    return render_template('mobile/document_details.html',
                          document=document,
                          current_date=current_date,
                          days_remaining=days_remaining)

# صفحة التقارير - النسخة المحمولة
@mobile_bp.route('/reports')
@login_required
def reports():
    """صفحة التقارير للنسخة المحمولة"""
    # قائمة التقارير الأخيرة (يمكن جلبها من قاعدة البيانات لاحقًا)
    recent_reports = []
    return render_template('mobile/reports.html', recent_reports=recent_reports)

# تقرير الموظفين - النسخة المحمولة
@mobile_bp.route('/reports/employees')
@login_required
def report_employees():
    """تقرير الموظفين للنسخة المحمولة"""
    departments = Department.query.order_by(Department.name).all()
    
    # استخراج معلمات الاستعلام
    department_id = request.args.get('department_id')
    status = request.args.get('status')
    search = request.args.get('search')
    export_format = request.args.get('export')
    
    # إنشاء الاستعلام الأساسي
    query = Employee.query
    
    # تطبيق الفلترة
    if department_id:
        query = query.filter_by(department_id=department_id)
    
    if status:
        query = query.filter_by(status=status)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Employee.name.like(search_term)) |
            (Employee.employee_id.like(search_term)) |
            (Employee.national_id.like(search_term)) |
            (Employee.job_title.like(search_term))
        )
    
    # الحصول على جميع الموظفين المطابقين
    employees = query.order_by(Employee.name).all()
    
    # معالجة طلبات التصدير
    if export_format:
        try:
            if export_format == 'pdf':
                # استدعاء مسار التصدير PDF في النسخة الرئيسية
                return redirect(url_for('reports.export_employees_report', 
                                       export_type='pdf',
                                       department_id=department_id,
                                       status=status,
                                       search=search))
                                       
            elif export_format == 'excel':
                # استدعاء مسار التصدير Excel في النسخة الرئيسية
                return redirect(url_for('reports.export_employees_report',
                                       export_type='excel',
                                       department_id=department_id,
                                       status=status,
                                       search=search))
        except Exception as e:
            # تسجيل الخطأ في السجل
            print(f"خطأ في تصدير تقرير الموظفين: {str(e)}")
    
    # عرض الصفحة مع نتائج التقرير
    return render_template('mobile/report_employees.html', 
                         departments=departments,
                         employees=employees)

# تقرير الحضور - النسخة المحمولة
@mobile_bp.route('/reports/attendance')
@login_required
def report_attendance():
    """تقرير الحضور للنسخة المحمولة"""
    # الحصول على قائمة الأقسام للفلترة
    departments = Department.query.order_by(Department.name).all()
    
    # استخراج معلمات الاستعلام
    department_id = request.args.get('department_id')
    employee_id = request.args.get('employee_id')
    status = request.args.get('status')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    export_format = request.args.get('export')
    
    # استخراج الموظفين المطابقين للفلترة
    employees_query = Employee.query
    if department_id:
        employees_query = employees_query.filter_by(department_id=department_id)
    employees = employees_query.order_by(Employee.name).all()
    
    # إنشاء استعلام سجلات الحضور
    attendance_query = Attendance.query
    
    # تطبيق الفلترة على سجلات الحضور
    if employee_id:
        attendance_query = attendance_query.filter_by(employee_id=employee_id)
    elif department_id:
        # فلترة حسب القسم عن طريق الانضمام مع جدول الموظفين
        attendance_query = attendance_query.join(Employee).filter(Employee.department_id == department_id)
    
    if status:
        attendance_query = attendance_query.filter_by(status=status)
    
    if start_date:
        attendance_query = attendance_query.filter(Attendance.date >= start_date)
    
    if end_date:
        attendance_query = attendance_query.filter(Attendance.date <= end_date)
    
    # الحصول على سجلات الحضور المرتبة حسب التاريخ (تنازلياً)
    attendance_records = attendance_query.order_by(Attendance.date.desc()).all()
    
    # معالجة طلبات التصدير
    if export_format:
        try:
            if export_format == 'pdf':
                # استدعاء مسار التصدير PDF في النسخة الرئيسية
                return redirect(url_for('reports.attendance_pdf',
                                       department_id=department_id,
                                       employee_id=employee_id,
                                       status=status,
                                       start_date=start_date,
                                       end_date=end_date))
                                       
            elif export_format == 'excel':
                # استدعاء مسار التصدير Excel في النسخة الرئيسية
                return redirect(url_for('reports.attendance_excel',
                                       department_id=department_id,
                                       employee_id=employee_id,
                                       status=status,
                                       start_date=start_date,
                                       end_date=end_date))
        except Exception as e:
            # تسجيل الخطأ في السجل
            print(f"خطأ في تصدير تقرير الحضور: {str(e)}")
    
    # عرض الصفحة مع نتائج التقرير
    return render_template('mobile/report_attendance.html',
                         departments=departments,
                         employees=employees,
                         attendance_records=attendance_records)

# تقرير الرواتب - النسخة المحمولة
@mobile_bp.route('/reports/salaries')
@login_required
def report_salaries():
    """تقرير الرواتب للنسخة المحمولة"""
    # الحصول على قائمة الأقسام والموظفين للفلترة
    departments = Department.query.order_by(Department.name).all()
    
    # استخراج معلمات البحث
    department_id = request.args.get('department_id')
    employee_id = request.args.get('employee_id')
    is_paid = request.args.get('is_paid')
    year = request.args.get('year')
    month = request.args.get('month')
    export_format = request.args.get('export')
    
    # استخراج الموظفين المطابقين للفلترة
    employees_query = Employee.query
    if department_id:
        employees_query = employees_query.filter_by(department_id=department_id)
    employees = employees_query.order_by(Employee.name).all()
    
    # إنشاء استعلام الرواتب
    query = Salary.query
    
    # تطبيق الفلترة على الرواتب
    if employee_id:
        query = query.filter_by(employee_id=employee_id)
    elif department_id:
        # فلترة حسب القسم عن طريق الانضمام مع جدول الموظفين
        query = query.join(Employee).filter(Employee.department_id == department_id)
    
    if is_paid:
        is_paid_bool = (is_paid.lower() == 'true' or is_paid == '1')
        query = query.filter(Salary.is_paid == is_paid_bool)
    
    if year:
        query = query.filter(Salary.year == year)
    
    if month:
        query = query.filter(Salary.month == month)
    
    # الحصول على سجلات الرواتب المرتبة حسب التاريخ (تنازلياً)
    salaries = query.order_by(Salary.year.desc(), Salary.month.desc()).all()
    
    # معالجة طلبات التصدير
    if export_format:
        try:
            if export_format == 'pdf':
                # استدعاء مسار التصدير PDF في النسخة الرئيسية
                return redirect(url_for('reports.salaries_pdf',
                                      department_id=department_id,
                                      employee_id=employee_id,
                                      is_paid=is_paid,
                                      year=year,
                                      month=month))
                                      
            elif export_format == 'excel':
                # استدعاء مسار التصدير Excel في النسخة الرئيسية
                return redirect(url_for('reports.salaries_excel',
                                      department_id=department_id,
                                      employee_id=employee_id,
                                      is_paid=is_paid,
                                      year=year,
                                      month=month))
        except Exception as e:
            # تسجيل الخطأ في السجل
            print(f"خطأ في تصدير تقرير الرواتب: {str(e)}")
    
    # استخراج قائمة بالسنوات والأشهر المتاحة
    years_months = db.session.query(Salary.year, Salary.month)\
                  .order_by(Salary.year.desc(), Salary.month.desc())\
                  .distinct().all()
    
    # تجميع السنوات والأشهر
    available_years = sorted(list(set([ym[0] for ym in years_months])), reverse=True)
    available_months = sorted(list(set([ym[1] for ym in years_months])))
    
    return render_template('mobile/report_salaries.html',
                         departments=departments,
                         employees=employees,
                         salaries=salaries,
                         available_years=available_years,
                         available_months=available_months)

# تقرير الوثائق - النسخة المحمولة
@mobile_bp.route('/reports/documents')
@login_required
def report_documents():
    """تقرير الوثائق للنسخة المحمولة"""
    # الحصول على قائمة الأقسام والموظفين للفلترة
    departments = Department.query.order_by(Department.name).all()
    current_date = datetime.now().date()
    
    # استخراج معلمات البحث
    department_id = request.args.get('department_id')
    employee_id = request.args.get('employee_id')
    document_type = request.args.get('document_type')
    status = request.args.get('status')  # valid, expiring, expired
    export_format = request.args.get('export')
    
    # استخراج الموظفين المطابقين للفلترة
    employees_query = Employee.query
    if department_id:
        employees_query = employees_query.filter_by(department_id=department_id)
    employees = employees_query.order_by(Employee.name).all()
    
    # إنشاء استعلام الوثائق
    query = Document.query
    
    # تطبيق الفلترة على الوثائق
    if employee_id:
        query = query.filter_by(employee_id=employee_id)
    elif department_id:
        # فلترة حسب القسم عن طريق الانضمام مع جدول الموظفين
        query = query.join(Employee).filter(Employee.department_id == department_id)
    
    if document_type:
        query = query.filter_by(document_type=document_type)
    
    # فلترة حسب حالة الوثيقة (صالحة، على وشك الانتهاء، منتهية)
    if status:
        if status == 'valid':
            # وثائق سارية المفعول (تاريخ انتهاء الصلاحية بعد 60 يوم من الآن)
            valid_date = current_date + timedelta(days=60)
            query = query.filter(Document.expiry_date >= valid_date)
        elif status == 'expiring':
            # وثائق على وشك الانتهاء (تنتهي خلال 60 يوم)
            expiring_min_date = current_date
            expiring_max_date = current_date + timedelta(days=60)
            query = query.filter(Document.expiry_date >= expiring_min_date, 
                               Document.expiry_date <= expiring_max_date)
        elif status == 'expired':
            # وثائق منتهية الصلاحية
            query = query.filter(Document.expiry_date < current_date)
    
    # الحصول على الوثائق المرتبة حسب تاريخ انتهاء الصلاحية
    documents = query.order_by(Document.expiry_date).all()
    
    # معالجة طلبات التصدير
    if export_format:
        if export_format == 'pdf':
            # استدعاء مسار التصدير PDF في النسخة الرئيسية
            return redirect(url_for('reports.documents_pdf',
                                  department_id=department_id,
                                  employee_id=employee_id,
                                  document_type=document_type,
                                  status=status))
                                  
        elif export_format == 'excel':
            # استدعاء مسار التصدير Excel في النسخة الرئيسية
            return redirect(url_for('reports.documents_excel',
                                  department_id=department_id,
                                  employee_id=employee_id,
                                  document_type=document_type,
                                  status=status))
    
    # استخراج أنواع الوثائق المتاحة
    document_types = db.session.query(Document.document_type)\
                    .distinct().order_by(Document.document_type).all()
    document_types = [d[0] for d in document_types if d[0]]
    
    # إضافة عدد الأيام المتبقية لكل وثيقة
    for doc in documents:
        if doc.expiry_date:
            doc.days_remaining = (doc.expiry_date - current_date).days
        else:
            doc.days_remaining = None
    
    return render_template('mobile/report_documents.html',
                         departments=departments,
                         employees=employees,
                         documents=documents,
                         document_types=document_types,
                         current_date=current_date)

# تقرير السيارات - النسخة المحمولة 
@mobile_bp.route('/reports/vehicles')
@login_required
def report_vehicles():
    """تقرير السيارات للنسخة المحمولة"""
    # استخراج معلمات البحث
    vehicle_type = request.args.get('vehicle_type')
    status = request.args.get('status')
    search = request.args.get('search')
    export_format = request.args.get('export')
    
    # إنشاء استعلام المركبات
    query = Vehicle.query
    
    # تطبيق الفلترة على المركبات
    if vehicle_type:
        query = query.filter_by(make=vehicle_type)  # نستخدم make بدلاً من vehicle_type
    
    if status:
        query = query.filter_by(status=status)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Vehicle.plate_number.like(search_term)) |
            (Vehicle.make.like(search_term)) |
            (Vehicle.model.like(search_term)) |
            (Vehicle.color.like(search_term))
        )
    
    # الحصول على المركبات المرتبة حسب الترتيب
    vehicles = query.order_by(Vehicle.plate_number).all()
    
    # معالجة طلبات التصدير
    if export_format:
        try:
            if export_format == 'pdf':
                # استدعاء مسار التصدير PDF في النسخة الرئيسية
                return redirect(url_for('reports.export_vehicles_report',
                                      export_type='pdf',
                                      vehicle_type=vehicle_type,
                                      status=status,
                                      search=search))
                                      
            elif export_format == 'excel':
                # استدعاء مسار التصدير Excel في النسخة الرئيسية
                return redirect(url_for('reports.export_vehicles_report',
                                      export_type='excel',
                                      vehicle_type=vehicle_type,
                                      status=status,
                                      search=search))
        except Exception as e:
            # تسجيل الخطأ في السجل
            print(f"خطأ في تصدير تقرير المركبات: {str(e)}")
    
    # استخراج انواع المركبات وحالات المركبات المتاحة
    # استخراج الشركات المصنعة من قاعدة البيانات
    vehicle_types = db.session.query(Vehicle.make)\
                    .distinct().order_by(Vehicle.make).all()
    vehicle_types = [vt[0] for vt in vehicle_types if vt[0]]
    
    vehicle_statuses = db.session.query(Vehicle.status)\
                      .distinct().order_by(Vehicle.status).all()
    vehicle_statuses = [vs[0] for vs in vehicle_statuses if vs[0]]
    
    return render_template('mobile/report_vehicles.html',
                         vehicles=vehicles,
                         vehicle_types=vehicle_types,
                         vehicle_statuses=vehicle_statuses)

# تقرير الرسوم - النسخة المحمولة
@mobile_bp.route('/reports/fees')
@login_required
def report_fees():
    """تقرير الرسوم للنسخة المحمولة"""
    # استخراج معلمات البحث
    fee_type = request.args.get('fee_type')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    status = request.args.get('status')  # paid/unpaid
    export_format = request.args.get('export')
    
    # إنشاء استعلام الرسوم
    query = Fee.query
    
    # تطبيق الفلترة على الرسوم
    if fee_type:
        query = query.filter_by(fee_type=fee_type)
    
    if date_from:
        query = query.filter(Fee.due_date >= date_from)
    
    if date_to:
        query = query.filter(Fee.due_date <= date_to)
    
    if status:
        is_paid_bool = (status.lower() == 'paid')
        query = query.filter(Fee.is_paid == is_paid_bool)
    
    # الحصول على قائمة الرسوم المرتبة حسب تاريخ الاستحقاق
    fees = query.order_by(Fee.due_date).all()
    
    # معالجة طلبات التصدير
    if export_format:
        try:
            if export_format == 'pdf':
                # استدعاء مسار التصدير PDF في النسخة الرئيسية
                return redirect(url_for('reports.export_fees_report',
                                      export_type='pdf',
                                      fee_type=fee_type,
                                      date_from=date_from,
                                      date_to=date_to,
                                      status=status))
                                  
            elif export_format == 'excel':
                # استدعاء مسار التصدير Excel في النسخة الرئيسية
                return redirect(url_for('reports.export_fees_report',
                                      export_type='excel',
                                      fee_type=fee_type,
                                      date_from=date_from,
                                      date_to=date_to,
                                      status=status))
        except Exception as e:
            # تسجيل الخطأ في السجل
            print(f"خطأ في تصدير تقرير الرسوم: {str(e)}")
    
    # استخراج أنواع الرسوم المتاحة
    fee_types = db.session.query(Fee.fee_type)\
                .distinct().order_by(Fee.fee_type).all()
    fee_types = [f[0] for f in fee_types if f[0]]
    
    # احتساب إجماليات الرسوم
    total_fees = sum(fee.amount for fee in fees if fee.amount)
    total_paid = sum(fee.amount for fee in fees if fee.amount and fee.is_paid)
    total_unpaid = sum(fee.amount for fee in fees if fee.amount and not fee.is_paid)
    
    # الحصول على التاريخ الحالي
    current_date = datetime.now().date()
    
    return render_template('mobile/report_fees.html',
                         fees=fees,
                         fee_types=fee_types,
                         total_fees=total_fees,
                         total_paid=total_paid,
                         total_unpaid=total_unpaid,
                         current_date=current_date)

# صفحة السيارات - النسخة المحمولة
@mobile_bp.route('/vehicles')
@login_required
def vehicles():
    """صفحة السيارات للنسخة المحمولة"""
    # استخدام نفس البيانات الموجودة في قاعدة البيانات
    status_filter = request.args.get('status', '')
    make_filter = request.args.get('make', '')
    search_filter = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    per_page = 10  # عدد السيارات في الصفحة الواحدة
    
    # قاعدة الاستعلام الأساسية
    query = Vehicle.query
    
    # إضافة التصفية حسب الحالة إذا تم تحديدها
    if status_filter:
        query = query.filter(Vehicle.status == status_filter)
    
    # إضافة التصفية حسب الشركة المصنعة إذا تم تحديدها
    if make_filter:
        query = query.filter(Vehicle.make == make_filter)
    
    # إضافة التصفية حسب البحث
    if search_filter:
        search_pattern = f"%{search_filter}%"
        query = query.filter(
            (Vehicle.plate_number.like(search_pattern)) |
            (Vehicle.make.like(search_pattern)) |
            (Vehicle.model.like(search_pattern))
        )
    
    # الحصول على قائمة الشركات المصنعة المتوفرة
    makes = db.session.query(Vehicle.make).distinct().order_by(Vehicle.make).all()
    makes = [make[0] for make in makes if make[0]]  # استخراج أسماء الشركات وتجاهل القيم الفارغة
    
    # تنفيذ الاستعلام مع الترقيم
    pagination = query.order_by(Vehicle.status, Vehicle.plate_number).paginate(page=page, per_page=per_page, error_out=False)
    vehicles = pagination.items
    
    # إحصائيات سريعة - نعدل المسميات لتتوافق مع النسخة المحمولة
    stats = {
        'total': Vehicle.query.count(),
        'active': Vehicle.query.filter_by(status='available').count(),
        'maintenance': Vehicle.query.filter_by(status='in_workshop').count(),
        'inactive': Vehicle.query.filter_by(status='accident').count() + Vehicle.query.filter_by(status='rented').count() + Vehicle.query.filter_by(status='in_project').count()
    }
    
    return render_template('mobile/vehicles.html', 
                          vehicles=vehicles, 
                          stats=stats,
                          makes=makes,
                          pagination=pagination)
    
# تفاصيل السيارة - النسخة المحمولة
@mobile_bp.route('/vehicles/<int:vehicle_id>')
@login_required
def vehicle_details(vehicle_id):
    """تفاصيل السيارة للنسخة المحمولة"""
    # الحصول على بيانات السيارة من قاعدة البيانات
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    # الحصول على سجلات مختلفة للسيارة
    try:
        # الحصول على سجل الصيانة الخاص بالسيارة
        maintenance_records = VehicleMaintenance.query.filter_by(vehicle_id=vehicle_id).order_by(VehicleMaintenance.date.desc()).limit(5).all()
        
        # الحصول على سجلات الورشة
        workshop_records = VehicleWorkshop.query.filter_by(vehicle_id=vehicle_id).order_by(VehicleWorkshop.entry_date.desc()).limit(5).all()
        
        # الحصول على تعيينات المشاريع
        project_assignments = VehicleProject.query.filter_by(vehicle_id=vehicle_id).order_by(VehicleProject.start_date.desc()).limit(5).all()
        
        # الحصول على سجلات التسليم والاستلام
        handover_records = VehicleHandover.query.filter_by(vehicle_id=vehicle_id).order_by(VehicleHandover.handover_date.desc()).limit(5).all()
        
        # الحصول على سجلات الفحص الدوري
        periodic_inspections = VehiclePeriodicInspection.query.filter_by(vehicle_id=vehicle_id).order_by(VehiclePeriodicInspection.inspection_date.desc()).limit(3).all()
        
        # الحصول على سجلات فحص السلامة
        safety_checks = VehicleSafetyCheck.query.filter_by(vehicle_id=vehicle_id).order_by(VehicleSafetyCheck.check_date.desc()).limit(3).all()
        
        # حساب تكلفة الإصلاحات الإجمالية
        total_maintenance_cost = db.session.query(func.sum(VehicleWorkshop.cost)).filter_by(vehicle_id=vehicle_id).scalar() or 0
        
        # حساب عدد الأيام في الورشة (للسنة الحالية)
        current_year = datetime.now().year
        days_in_workshop = 0
        for record in workshop_records:
            if record.entry_date.year == current_year:
                if record.exit_date:
                    days_in_workshop += (record.exit_date - record.entry_date).days
                else:
                    days_in_workshop += (datetime.now().date() - record.entry_date).days
        
        # ملاحظات تنبيهية عن انتهاء الفحص الدوري
        inspection_warnings = []
        for inspection in periodic_inspections:
            if hasattr(inspection, 'is_expired') and inspection.is_expired:
                inspection_warnings.append(f"الفحص الدوري منتهي الصلاحية منذ {(datetime.now().date() - inspection.expiry_date).days} يومًا")
                break
            elif hasattr(inspection, 'is_expiring_soon') and inspection.is_expiring_soon:
                days_remaining = (inspection.expiry_date - datetime.now().date()).days
                inspection_warnings.append(f"الفحص الدوري سينتهي خلال {days_remaining} يومًا")
                break
            
    except Exception as e:
        print(f"خطأ في جلب بيانات السيارة: {str(e)}")
        maintenance_records = []
        workshop_records = []
        project_assignments = []
        handover_records = []
        periodic_inspections = []
        safety_checks = []
        total_maintenance_cost = 0
        days_in_workshop = 0
        inspection_warnings = []
    
    # الحصول على وثائق السيارة
    documents = []
    # سيتم إضافة منطق لجلب الوثائق لاحقًا
    
    # الحصول على رسوم السيارة
    fees = []
    # سيتم إضافة منطق لجلب الرسوم لاحقًا
    
    return render_template('mobile/vehicle_details.html',
                         vehicle=vehicle,
                         maintenance_records=maintenance_records,
                         workshop_records=workshop_records,
                         project_assignments=project_assignments,
                         handover_records=handover_records,
                         periodic_inspections=periodic_inspections,
                         safety_checks=safety_checks,
                         documents=documents,
                         fees=fees,
                         total_maintenance_cost=total_maintenance_cost,
                         days_in_workshop=days_in_workshop,
                         inspection_warnings=inspection_warnings)

# إضافة سيارة جديدة - النسخة المحمولة
@mobile_bp.route('/vehicles/add', methods=['GET', 'POST'])
@login_required
def add_vehicle():
    """إضافة سيارة جديدة للنسخة المحمولة"""
    # يمكن تنفيذ هذه الوظيفة لاحقًا
    return render_template('mobile/add_vehicle.html')

# سجل صيانة السيارات - النسخة المحمولة
@mobile_bp.route('/vehicles/maintenance')
@login_required
def vehicle_maintenance():
    """سجل صيانة السيارات للنسخة المحمولة"""
    # معايير التصفية
    status_filter = request.args.get('status', '')
    vehicle_id_str = request.args.get('vehicle_id', '')
    vehicle_id = int(vehicle_id_str) if vehicle_id_str and vehicle_id_str.isdigit() else None
    maintenance_type = request.args.get('maintenance_type', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    # استعلام قاعدة البيانات
    query = VehicleMaintenance.query
    
    # تطبيق الفلاتر
    if status_filter:
        query = query.filter(VehicleMaintenance.status == status_filter)
    
    if vehicle_id:
        query = query.filter(VehicleMaintenance.vehicle_id == vehicle_id)
    
    if maintenance_type:
        query = query.filter(VehicleMaintenance.maintenance_type == maintenance_type)
    
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            query = query.filter(VehicleMaintenance.date >= date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            query = query.filter(VehicleMaintenance.date <= date_to_obj)
        except ValueError:
            pass
    
    # الحصول على سجلات الصيانة
    maintenance_records = query.order_by(VehicleMaintenance.date.desc()).all()
    
    # الحصول على قائمة السيارات
    vehicles = Vehicle.query.all()
    
    # حساب إحصائيات الصيانة
    ongoing_count = VehicleMaintenance.query.filter(VehicleMaintenance.status == 'قيد التنفيذ').count()
    completed_count = VehicleMaintenance.query.filter(VehicleMaintenance.status == 'منجزة').count()
    
    # تحديد السجلات المتأخرة (قيد الانتظار وتاريخها قبل اليوم)
    today = datetime.now().date()
    late_count = VehicleMaintenance.query.filter(
        VehicleMaintenance.status == 'قيد الانتظار',
        VehicleMaintenance.date < today
    ).count()
    
    # سجلات اليوم
    today_count = VehicleMaintenance.query.filter(VehicleMaintenance.date == today).count()
    
    # حساب إجمالي التكاليف حسب نوع الصيانة
    all_records = VehicleMaintenance.query.all()
    cost_summary = {
        'total': sum(record.cost for record in all_records),
        'periodic': sum(record.cost for record in all_records if record.maintenance_type == 'دورية'),
        'emergency': sum(record.cost for record in all_records if record.maintenance_type == 'طارئة'),
        'repair': sum(record.cost for record in all_records if record.maintenance_type == 'إصلاح'),
        'other': sum(record.cost for record in all_records if record.maintenance_type not in ['دورية', 'طارئة', 'إصلاح'])
    }
    
    # إحصائيات سريعة
    stats = {
        'ongoing': ongoing_count,
        'completed': completed_count,
        'late': late_count,
        'today': today_count
    }
    
    # تمرير التاريخ الحالي لاستخدامه في القالب
    current_date = datetime.now().date()
    
    return render_template('mobile/vehicle_maintenance.html',
                         vehicles=vehicles,
                         maintenance_records=maintenance_records,
                         cost_summary=cost_summary,
                         stats=stats,
                         selected_status=status_filter,
                         selected_vehicle=vehicle_id,
                         selected_type=maintenance_type,
                         date_from=date_from,
                         date_to=date_to,
                         current_date=current_date)

# إضافة صيانة جديدة - النسخة المحمولة
@mobile_bp.route('/vehicles/maintenance/add', methods=['GET', 'POST'])
@login_required
def add_maintenance():
    """إضافة صيانة جديدة للنسخة المحمولة"""
    # الحصول على قائمة السيارات
    vehicles = Vehicle.query.all()
    
    if request.method == 'POST':
        try:
            # استخراج البيانات من النموذج
            vehicle_id = request.form.get('vehicle_id')
            maintenance_type = request.form.get('maintenance_type')
            description = request.form.get('description')
            cost = request.form.get('cost', 0.0, type=float)
            date_str = request.form.get('date')
            status = request.form.get('status')
            technician = request.form.get('technician')
            notes = request.form.get('notes', '')
            parts_replaced = request.form.get('parts_replaced', '')
            actions_taken = request.form.get('actions_taken', '')
            receipt_image_url = request.form.get('receipt_image_url', '')
            delivery_receipt_url = request.form.get('delivery_receipt_url', '')
            pickup_receipt_url = request.form.get('pickup_receipt_url', '')
            
            # التحقق من تعبئة الحقول المطلوبة
            if not vehicle_id or not maintenance_type or not description or not date_str or not status or not technician:
                flash('يرجى ملء جميع الحقول المطلوبة', 'warning')
                return render_template('mobile/add_maintenance.html', vehicles=vehicles, now=datetime.now())
            
            # تحويل التاريخ إلى كائن Date
            maintenance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # إنشاء سجل صيانة جديد
            new_maintenance = VehicleMaintenance(
                vehicle_id=vehicle_id,
                date=maintenance_date,
                maintenance_type=maintenance_type,
                description=description,
                status=status,
                cost=cost,
                technician=technician,
                receipt_image_url=receipt_image_url,
                delivery_receipt_url=delivery_receipt_url,
                pickup_receipt_url=pickup_receipt_url,
                parts_replaced=parts_replaced,
                actions_taken=actions_taken,
                notes=notes
            )
            
            # حفظ البيانات في قاعدة البيانات
            db.session.add(new_maintenance)
            db.session.commit()
            
            flash('تمت إضافة سجل الصيانة بنجاح', 'success')
            return redirect(url_for('mobile.vehicle_maintenance'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء إضافة سجل الصيانة: {str(e)}', 'danger')
    
    # عرض نموذج إضافة صيانة جديدة
    return render_template('mobile/add_maintenance.html', vehicles=vehicles, now=datetime.now())

# تفاصيل الصيانة - النسخة المحمولة
@mobile_bp.route('/vehicles/maintenance/<int:maintenance_id>')
@login_required
def maintenance_details(maintenance_id):
    """تفاصيل الصيانة للنسخة المحمولة"""
    # جلب سجل الصيانة من قاعدة البيانات
    maintenance = VehicleMaintenance.query.get_or_404(maintenance_id)
    
    print(f"DEBUG: Maintenance ID: {maintenance.id}, Type: {type(maintenance)}")
    
    # جلب بيانات السيارة
    vehicle = Vehicle.query.get(maintenance.vehicle_id)
    
    # تحديد الفئة المناسبة لحالة الصيانة
    status_class = ""
    if maintenance.status == "قيد التنفيذ":
        status_class = "ongoing"
    elif maintenance.status == "منجزة":
        status_class = "completed"
    elif maintenance.status == "قيد الانتظار":
        if maintenance.date < datetime.now().date():
            status_class = "late"
        else:
            status_class = "scheduled"
    elif maintenance.status == "ملغية":
        status_class = "canceled"
    
    # جلب صور الصيانة إن وجدت
    images = VehicleMaintenanceImage.query.filter_by(maintenance_id=maintenance_id).all()
    
    # تعيين حالة الصيانة لاستخدامها في العرض
    maintenance.status_class = status_class
    # إضافة الصور إلى كائن الصيانة
    maintenance.images = images
    
    return render_template('mobile/maintenance_details.html',
                           maintenance=maintenance,
                           vehicle=vehicle)


# تعديل سجل صيانة - النسخة المحمولة
@mobile_bp.route('/vehicles/maintenance/edit/<int:maintenance_id>', methods=['GET', 'POST'])
@login_required
def edit_maintenance(maintenance_id):
    """تعديل سجل صيانة للنسخة المحمولة"""
    # جلب سجل الصيانة
    maintenance = VehicleMaintenance.query.get_or_404(maintenance_id)
    
    # الحصول على قائمة السيارات
    vehicles = Vehicle.query.all()
    
    if request.method == 'POST':
        try:
            # استخراج البيانات من النموذج
            vehicle_id = request.form.get('vehicle_id')
            maintenance_type = request.form.get('maintenance_type')
            description = request.form.get('description')
            cost = request.form.get('cost', 0.0, type=float)
            date_str = request.form.get('date')
            status = request.form.get('status')
            technician = request.form.get('technician')
            notes = request.form.get('notes', '')
            parts_replaced = request.form.get('parts_replaced', '')
            actions_taken = request.form.get('actions_taken', '')
            
            # التحقق من تعبئة الحقول المطلوبة
            if not vehicle_id or not maintenance_type or not description or not date_str or not status or not technician:
                flash('يرجى ملء جميع الحقول المطلوبة', 'warning')
                return render_template('mobile/edit_maintenance.html', 
                                     maintenance=maintenance,
                                     vehicles=vehicles, 
                                     now=datetime.now())
            
            # تحويل التاريخ إلى كائن Date
            maintenance_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            
            # استخراج روابط الإيصالات
            receipt_image_url = request.form.get('receipt_image_url', '')
            delivery_receipt_url = request.form.get('delivery_receipt_url', '')
            pickup_receipt_url = request.form.get('pickup_receipt_url', '')
            
            # تحديث سجل الصيانة
            maintenance.vehicle_id = vehicle_id
            maintenance.date = maintenance_date
            maintenance.maintenance_type = maintenance_type
            maintenance.description = description
            maintenance.status = status
            maintenance.cost = cost
            maintenance.technician = technician
            maintenance.receipt_image_url = receipt_image_url
            maintenance.delivery_receipt_url = delivery_receipt_url
            maintenance.pickup_receipt_url = pickup_receipt_url
            maintenance.parts_replaced = parts_replaced
            maintenance.actions_taken = actions_taken
            maintenance.notes = notes
            
            # حفظ التغييرات في قاعدة البيانات
            db.session.commit()
            
            flash('تم تحديث سجل الصيانة بنجاح', 'success')
            return redirect(url_for('mobile.maintenance_details', maintenance_id=maintenance.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء تحديث سجل الصيانة: {str(e)}', 'danger')
    
    # عرض نموذج تعديل سجل الصيانة
    return render_template('mobile/edit_maintenance.html', 
                         maintenance=maintenance, 
                         vehicles=vehicles, 
                         now=datetime.now())


# حذف سجل صيانة - النسخة المحمولة
@mobile_bp.route('/vehicles/maintenance/delete/<int:maintenance_id>')
@login_required
def delete_maintenance(maintenance_id):
    """حذف سجل صيانة للنسخة المحمولة"""
    try:
        # جلب سجل الصيانة
        maintenance = VehicleMaintenance.query.get_or_404(maintenance_id)
        
        # حذف جميع الصور المرتبطة (إن وجدت)
        images = VehicleMaintenanceImage.query.filter_by(maintenance_id=maintenance_id).all()
        for image in images:
            # حذف ملف الصورة من المجلد (يمكن تنفيذه لاحقًا)
            # image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image.image_path)
            # if os.path.exists(image_path):
            #    os.remove(image_path)
            
            # حذف السجل من قاعدة البيانات
            db.session.delete(image)
        
        # حذف سجل الصيانة
        db.session.delete(maintenance)
        db.session.commit()
        
        flash('تم حذف سجل الصيانة بنجاح', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'حدث خطأ أثناء محاولة حذف سجل الصيانة: {str(e)}', 'danger')
    
    return redirect(url_for('mobile.vehicle_maintenance'))

# وثائق السيارات - النسخة المحمولة
@mobile_bp.route('/vehicles/documents')
@login_required
def vehicle_documents():
    """وثائق السيارات للنسخة المحمولة"""
    # يمكن تنفيذ هذه الوظيفة لاحقًا
    return render_template('mobile/vehicle_documents.html')

# مصروفات السيارات - النسخة المحمولة - تم تحديثها
# انظر إلى التنفيذ الجديد في نهاية الملف

# تشيك لست السيارة (إضافة فحص جديد) - النسخة المحمولة
@mobile_bp.route('/vehicles/checklist')
@login_required
def vehicle_checklist():
    """تشيك لست فحص أجزاء السيارة للنسخة المحمولة"""
    # قائمة السيارات للاختيار
    vehicles_data = Vehicle.query.all()
    vehicles = [
        {
            'id': vehicle.id,
            'name': f"{vehicle.make} {vehicle.model}",
            'plate_number': vehicle.plate_number,
        } for vehicle in vehicles_data
    ]
    
    # تاريخ اليوم
    now = datetime.now()
    
    return render_template('mobile/vehicle_checklist.html', vehicles=vehicles, now=now)


# قائمة فحوصات السيارة - النسخة المحمولة
@mobile_bp.route('/vehicles/checklist/list')
@login_required
def vehicle_checklist_list():
    """قائمة فحوصات السيارة للنسخة المحمولة"""
    page = request.args.get('page', 1, type=int)
    per_page = 20  # عدد العناصر في الصفحة الواحدة
    
    # فلترة حسب السيارة
    vehicle_id = request.args.get('vehicle_id', '')
    # فلترة حسب نوع الفحص
    inspection_type = request.args.get('inspection_type', '')
    # فلترة حسب التاريخ
    from_date = request.args.get('from_date', '')
    to_date = request.args.get('to_date', '')
    
    # بناء استعلام قاعدة البيانات
    query = VehicleChecklist.query
    
    # تطبيق الفلاتر إذا تم تحديدها
    if vehicle_id:
        query = query.filter(VehicleChecklist.vehicle_id == vehicle_id)
    
    if inspection_type:
        query = query.filter(VehicleChecklist.inspection_type == inspection_type)
    
    if from_date:
        try:
            from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
            query = query.filter(VehicleChecklist.inspection_date >= from_date_obj)
        except ValueError:
            pass
    
    if to_date:
        try:
            to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()
            query = query.filter(VehicleChecklist.inspection_date <= to_date_obj)
        except ValueError:
            pass
    
    # تنفيذ الاستعلام مع الترتيب والتصفح
    paginator = query.order_by(VehicleChecklist.inspection_date.desc()).paginate(page=page, per_page=per_page, error_out=False)
    checklists = paginator.items
    
    # الحصول على بيانات السيارات لعرضها في القائمة
    vehicles = Vehicle.query.all()
    
    # تحويل بيانات الفحوصات إلى تنسيق مناسب للعرض
    checklists_data = []
    for checklist in checklists:
        vehicle = Vehicle.query.get(checklist.vehicle_id)
        if vehicle:
            checklist_data = {
                'id': checklist.id,
                'vehicle_name': f"{vehicle.make} {vehicle.model}",
                'vehicle_plate': vehicle.plate_number,
                'inspection_date': checklist.inspection_date,
                'inspection_type': checklist.inspection_type,
                'inspector_name': checklist.inspector_name,
                'status': checklist.status,
                'completion_percentage': checklist.completion_percentage,
                'summary': checklist.summary
            }
            checklists_data.append(checklist_data)
    
    return render_template('mobile/vehicle_checklist_list.html',
                          checklists=checklists_data,
                          pagination=paginator,
                          vehicles=vehicles,
                          selected_vehicle=vehicle_id,
                          selected_type=inspection_type,
                          from_date=from_date,
                          to_date=to_date)


# تفاصيل فحص السيارة - النسخة المحمولة
@mobile_bp.route('/vehicles/checklist/<int:checklist_id>')
@login_required
def vehicle_checklist_details(checklist_id):
    """تفاصيل فحص السيارة للنسخة المحمولة"""
    # الحصول على بيانات الفحص من قاعدة البيانات
    checklist = VehicleChecklist.query.get_or_404(checklist_id)
    
    # الحصول على بيانات السيارة
    vehicle = Vehicle.query.get(checklist.vehicle_id)
    
    # جمع بيانات عناصر الفحص مرتبة حسب الفئة
    checklist_items = {}
    for item in checklist.checklist_items:
        if item.category not in checklist_items:
            checklist_items[item.category] = []
        
        checklist_items[item.category].append(item)
    
    # الحصول على علامات التلف المرتبطة بهذا الفحص
    damage_markers = VehicleDamageMarker.query.filter_by(checklist_id=checklist_id).all()
    
    # الحصول على صور الفحص المرفقة
    checklist_images = VehicleChecklistImage.query.filter_by(checklist_id=checklist_id).all()
    
    return render_template('mobile/vehicle_checklist_details.html',
                          checklist=checklist,
                          vehicle=vehicle,
                          checklist_items=checklist_items,
                          damage_markers=damage_markers,
                          checklist_images=checklist_images)

# تصدير فحص السيارة إلى PDF - النسخة المحمولة
@mobile_bp.route('/vehicles/checklist/<int:checklist_id>/pdf')
@login_required
def mobile_vehicle_checklist_pdf(checklist_id):
    """تصدير تقرير فحص المركبة إلى PDF مع عرض علامات التلف"""
    try:
        # الحصول على بيانات الفحص
        checklist = VehicleChecklist.query.get_or_404(checklist_id)
        
        # الحصول على بيانات المركبة
        vehicle = Vehicle.query.get_or_404(checklist.vehicle_id)
        
        # جمع بيانات عناصر الفحص مرتبة حسب الفئة
        checklist_items = {}
        for item in checklist.checklist_items:
            if item.category not in checklist_items:
                checklist_items[item.category] = []
            
            checklist_items[item.category].append(item)
        
        # الحصول على علامات التلف المرتبطة بهذا الفحص
        damage_markers = VehicleDamageMarker.query.filter_by(checklist_id=checklist_id).all()
        
        # الحصول على صور الفحص المرفقة
        checklist_images = VehicleChecklistImage.query.filter_by(checklist_id=checklist_id).all()
        
        # استيراد تابع إنشاء PDF
        from utils.vehicle_checklist_pdf import create_vehicle_checklist_pdf
        
        # إنشاء ملف PDF
        pdf_buffer = create_vehicle_checklist_pdf(
            checklist=checklist,
            vehicle=vehicle,
            checklist_items=checklist_items,
            damage_markers=damage_markers,
            checklist_images=checklist_images
        )
        
        # إنشاء استجابة تحميل للملف
        from flask import make_response
        response = make_response(pdf_buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=vehicle_checklist_{checklist_id}.pdf'
        
        return response
        
    except Exception as e:
        # تسجيل الخطأ للمساعدة في تشخيص المشكلة
        import traceback
        error_traceback = traceback.format_exc()
        app.logger.error(f"خطأ في إنشاء PDF لفحص المركبة: {str(e)}\n{error_traceback}")
        flash(f'حدث خطأ أثناء إنشاء ملف PDF: {str(e)}', 'danger')
        return redirect(url_for('mobile.vehicle_checklist_details', checklist_id=checklist_id))


# إضافة فحص جديد للسيارة - النسخة المحمولة
@mobile_bp.route('/vehicles/checklist/add', methods=['POST'])
@login_required
def add_vehicle_checklist():
    """إضافة فحص جديد للسيارة للنسخة المحمولة"""
    if request.method == 'POST':
        # التحقق من محتوى الطلب
        if request.is_json:
            # استلام بيانات الفحص من طلب JSON
            data = request.get_json()
            
            if not data:
                return jsonify({'status': 'error', 'message': 'لم يتم استلام بيانات'})
                
            vehicle_id = data.get('vehicle_id')
            inspection_date = data.get('inspection_date')
            inspector_name = data.get('inspector_name')
            inspection_type = data.get('inspection_type')
            general_notes = data.get('general_notes', '')
            items_data = data.get('items', [])
            damage_markers_data = data.get('damage_markers', [])
            
        elif request.content_type and 'multipart/form-data' in request.content_type:
            # استلام بيانات النموذج مع الصور
            try:
                form_data = request.form.get('data')
                if not form_data:
                    return jsonify({'status': 'error', 'message': 'لم يتم استلام بيانات النموذج'})
                
                # تحويل بيانات النموذج من JSON string إلى dict
                data = json.loads(form_data)
                
                vehicle_id = data.get('vehicle_id')
                inspection_date = data.get('inspection_date')
                inspector_name = data.get('inspector_name')
                inspection_type = data.get('inspection_type')
                general_notes = data.get('general_notes', '')
                items_data = data.get('items', [])
                
                # استلام علامات التلف إذا كانت موجودة
                damage_markers_str = request.form.get('damage_markers')
                damage_markers_data = json.loads(damage_markers_str) if damage_markers_str else []
                
                # معالجة الصور المرفقة
                images = []
                for key in request.files:
                    if key.startswith('image_'):
                        images.append(request.files[key])
                
                print(f"تم استلام {len(images)} صورة و {len(damage_markers_data)} علامة تلف")
                
            except Exception as e:
                app.logger.error(f"خطأ في معالجة بيانات النموذج: {str(e)}")
                return jsonify({'status': 'error', 'message': f'خطأ في معالجة البيانات: {str(e)}'})
        else:
            return jsonify({'status': 'error', 'message': 'نوع المحتوى غير مدعوم'})
        
        # التحقق من وجود البيانات المطلوبة
        if not all([vehicle_id, inspection_date, inspector_name, inspection_type]):
            return jsonify({'status': 'error', 'message': 'بيانات غير مكتملة، يرجى ملء جميع الحقول المطلوبة'})
        
        try:
            # تحويل التاريخ إلى كائن Date
            inspection_date = datetime.strptime(inspection_date, '%Y-%m-%d').date()
            
            # إنشاء فحص جديد
            new_checklist = VehicleChecklist(
                vehicle_id=vehicle_id,
                inspection_date=inspection_date,
                inspector_name=inspector_name,
                inspection_type=inspection_type,
                notes=general_notes
            )
            
            db.session.add(new_checklist)
            db.session.flush()  # للحصول على معرّف الفحص الجديد
            
            # إضافة عناصر الفحص
            for item_data in items_data:
                category = item_data.get('category')
                item_name = item_data.get('item_name')
                status = item_data.get('status')
                notes = item_data.get('notes', '')
                
                # التحقق من وجود البيانات المطلوبة
                if not all([category, item_name, status]):
                    continue
                
                # إنشاء عنصر فحص جديد
                new_item = VehicleChecklistItem(
                    checklist_id=new_checklist.id,
                    category=category,
                    item_name=item_name,
                    status=status,
                    notes=notes
                )
                
                db.session.add(new_item)
            
            # إضافة علامات التلف على صورة السيارة
            if damage_markers_data:
                app.logger.info(f"إضافة {len(damage_markers_data)} علامة تلف للفحص رقم {new_checklist.id}")
                
                for marker_data in damage_markers_data:
                    # التحقق من وجود البيانات المطلوبة
                    marker_type = marker_data.get('type', 'damage')
                    x = marker_data.get('x')
                    y = marker_data.get('y')
                    notes = marker_data.get('notes', '')
                    
                    if x is None or y is None:
                        continue
                    
                    # إنشاء علامة تلف جديدة
                    damage_marker = VehicleDamageMarker(
                        checklist_id=new_checklist.id,
                        marker_type=marker_type,
                        position_x=float(x),
                        position_y=float(y),
                        notes=notes,
                        color='red' if marker_type == 'damage' else 'yellow'
                    )
                    
                    db.session.add(damage_marker)
            
            # معالجة الصور المرفقة إذا وجدت
            if request.files and 'images' in request.files:
                # إنشاء مجلد لتخزين الصور إذا لم يكن موجودًا
                vehicle_images_dir = os.path.join(app.static_folder, 'uploads', 'vehicles', 'checklists')
                os.makedirs(vehicle_images_dir, exist_ok=True)
                
                # الحصول على الصور من الطلب
                images = request.files.getlist('images')
                
                for i, image in enumerate(images):
                    if image and image.filename:
                        # حفظ الصورة بإسم فريد في المجلد المناسب
                        filename = secure_filename(image.filename)
                        unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex}_{filename}"
                        image_path = os.path.join('uploads', 'vehicles', 'checklists', unique_filename)
                        full_path = os.path.join(app.static_folder, image_path)
                        
                        # حفظ الصورة
                        image.save(full_path)
                        
                        # الحصول على وصف الصورة (إذا وجد)
                        description_key = f'image_description_{i}'
                        description = request.form.get(description_key, f"صورة فحص بتاريخ {inspection_date}")
                        
                        # إنشاء سجل لصورة الفحص
                        checklist_image = VehicleChecklistImage(
                            checklist_id=new_checklist.id,
                            image_path=image_path,
                            image_type='inspection',
                            description=description
                        )
                        
                        db.session.add(checklist_image)
                        app.logger.info(f"تم حفظ صورة فحص: {full_path}")
            
            # حفظ التغييرات في قاعدة البيانات
            db.session.commit()
            
            return jsonify({
                'status': 'success',
                'message': 'تم إضافة الفحص بنجاح',
                'checklist_id': new_checklist.id
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': f'حدث خطأ أثناء إضافة الفحص: {str(e)}'})
    
    return jsonify({'status': 'error', 'message': 'طريقة غير مسموح بها'})

# صفحة الرسوم والتكاليف - النسخة المحمولة (النسخة الأصلية)
@mobile_bp.route('/fees_old')
@login_required
def fees_old():
    """صفحة الرسوم والتكاليف للنسخة المحمولة (النسخة القديمة)"""
    page = request.args.get('page', 1, type=int)
    per_page = 20  # عدد العناصر في الصفحة الواحدة
    
    # فلترة حسب نوع الوثيقة
    document_type = request.args.get('document_type', '')
    # فلترة حسب حالة الرسوم
    status = request.args.get('status', '')
    # فلترة حسب التاريخ
    from_date = request.args.get('from_date', '')
    to_date = request.args.get('to_date', '')
    
    # بناء استعلام قاعدة البيانات
    query = Fee.query
    
    # تطبيق الفلاتر إذا تم تحديدها
    if document_type:
        query = query.filter(Fee.document_type == document_type)
    
    if status:
        query = query.filter(Fee.payment_status == status)
    
    if from_date:
        try:
            from_date_obj = datetime.strptime(from_date, '%Y-%m-%d').date()
            query = query.filter(Fee.due_date >= from_date_obj)
        except ValueError:
            pass
    
    if to_date:
        try:
            to_date_obj = datetime.strptime(to_date, '%Y-%m-%d').date()
            query = query.filter(Fee.due_date <= to_date_obj)
        except ValueError:
            pass
    
    # تنفيذ الاستعلام مع الترتيب والتصفح
    paginator = query.order_by(Fee.due_date.asc()).paginate(page=page, per_page=per_page, error_out=False)
    fees = paginator.items
    
    # الحصول على أنواع الوثائق المتاحة
    document_types = db.session.query(Fee.document_type).distinct().all()
    document_types = [d[0] for d in document_types if d[0]]
    
    # حساب إجماليات الرسوم
    all_fees = query.all()
    fees_summary = {
        'pending_fees': sum(fee.total_fees for fee in all_fees if fee.payment_status == 'pending'),
        'paid_fees': sum(fee.total_fees for fee in all_fees if fee.payment_status == 'paid'),
        'total_fees': sum(fee.total_fees for fee in all_fees)
    }
    
    return render_template('mobile/fees.html', 
                          fees=fees, 
                          fees_summary=fees_summary,
                          pagination=paginator,
                          document_types=document_types,
                          selected_type=document_type,
                          selected_status=status,
                          from_date=from_date,
                          to_date=to_date)

# إضافة رسم جديد - النسخة المحمولة
@mobile_bp.route('/fees/add', methods=['GET', 'POST'])
@login_required
def add_fee():
    """إضافة رسم جديد للنسخة المحمولة"""
    # يمكن تنفيذ هذه الوظيفة لاحقًا
    return render_template('mobile/add_fee.html')
    
# تعديل رسم - النسخة المحمولة
@mobile_bp.route('/fees/<int:fee_id>/edit', methods=['POST'])
@login_required
def edit_fee(fee_id):
    """تعديل رسم قائم للنسخة المحمولة"""
    # الحصول على بيانات الرسم من قاعدة البيانات
    fee = Fee.query.get_or_404(fee_id)
    
    if request.method == 'POST':
        # تحديث بيانات الرسم من النموذج
        fee.document_type = request.form.get('document_type')
        
        # تحديث تاريخ الاستحقاق
        due_date_str = request.form.get('due_date')
        if due_date_str:
            fee.due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        
        # تحديث حالة الدفع
        fee.payment_status = request.form.get('payment_status')
        
        # تحديث تاريخ السداد إذا كانت الحالة "مدفوع"
        if fee.payment_status == 'paid':
            payment_date_str = request.form.get('payment_date')
            if payment_date_str:
                fee.payment_date = datetime.strptime(payment_date_str, '%Y-%m-%d').date()
        else:
            fee.payment_date = None
        
        # تحديث قيم الرسوم
        fee.passport_fee = float(request.form.get('passport_fee', 0))
        fee.labor_office_fee = float(request.form.get('labor_office_fee', 0))
        fee.insurance_fee = float(request.form.get('insurance_fee', 0))
        fee.social_insurance_fee = float(request.form.get('social_insurance_fee', 0))
        
        # تحديث حالة نقل الكفالة
        fee.transfer_sponsorship = 'transfer_sponsorship' in request.form
        
        # تحديث الملاحظات
        fee.notes = request.form.get('notes', '')
        
        # حفظ التغييرات في قاعدة البيانات
        try:
            db.session.commit()
            flash('تم تحديث الرسم بنجاح', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء تحديث الرسم: {str(e)}', 'danger')
        
    # العودة إلى صفحة تفاصيل الرسم
    return redirect(url_for('mobile.fee_details', fee_id=fee_id))

# تسجيل رسم كمدفوع - النسخة المحمولة
@mobile_bp.route('/fees/<int:fee_id>/mark-as-paid', methods=['POST'])
@login_required
def mark_fee_as_paid(fee_id):
    """تسجيل رسم كمدفوع للنسخة المحمولة"""
    # الحصول على بيانات الرسم من قاعدة البيانات
    fee = Fee.query.get_or_404(fee_id)
    
    if request.method == 'POST':
        # تحديث حالة الدفع
        fee.payment_status = 'paid'
        
        # تحديث تاريخ السداد
        payment_date_str = request.form.get('payment_date')
        if payment_date_str:
            fee.payment_date = datetime.strptime(payment_date_str, '%Y-%m-%d').date()
        else:
            fee.payment_date = datetime.now().date()
        
        # إضافة ملاحظات السداد إلى ملاحظات الرسم
        payment_notes = request.form.get('payment_notes')
        if payment_notes:
            if fee.notes:
                fee.notes = f"{fee.notes}\n\nملاحظات السداد ({fee.payment_date}):\n{payment_notes}"
            else:
                fee.notes = f"ملاحظات السداد ({fee.payment_date}):\n{payment_notes}"
        
        # حفظ التغييرات في قاعدة البيانات
        try:
            db.session.commit()
            flash('تم تسجيل الرسم كمدفوع بنجاح', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء تسجيل الرسم كمدفوع: {str(e)}', 'danger')
    
    # العودة إلى صفحة تفاصيل الرسم
    return redirect(url_for('mobile.fee_details', fee_id=fee_id))

# تفاصيل الرسم - النسخة المحمولة 
@mobile_bp.route('/fees/<int:fee_id>')
@login_required
def fee_details(fee_id):
    """تفاصيل الرسم للنسخة المحمولة"""
    # الحصول على بيانات الرسم من قاعدة البيانات
    fee = Fee.query.get_or_404(fee_id)
    
    # إرسال التاريخ الحالي لاستخدامه في النموذج
    now = datetime.now()
    
    return render_template('mobile/fee_details.html', fee=fee, now=now)

# صفحة الإشعارات - النسخة المحمولة
@mobile_bp.route('/notifications')
def notifications():
    """صفحة الإشعارات للنسخة المحمولة"""
    # إنشاء بيانات إشعارات تجريبية
    notifications = [
        {
            'id': '1',
            'type': 'document',
            'title': 'وثيقة على وشك الانتهاء: جواز سفر',
            'message': 'متبقي 10 أيام على انتهاء جواز السفر',
            'created_at': datetime.now().strftime('%Y-%m-%d'),
            'is_read': False
        },
        {
            'id': '2',
            'type': 'fee',
            'title': 'رسوم مستحقة قريباً: تأشيرة',
            'message': 'رسوم مستحقة بعد 5 أيام بقيمة 2000.00',
            'created_at': datetime.now().strftime('%Y-%m-%d'),
            'is_read': False
        },
        {
            'id': '3',
            'type': 'system',
            'title': 'تحديث في النظام',
            'message': 'تم تحديث النظام إلى الإصدار الجديد',
            'created_at': datetime.now().strftime('%Y-%m-%d'),
            'is_read': True
        }
    ]
    
    pagination = {
        'page': 1,
        'per_page': 20,
        'total': len(notifications),
        'pages': 1,
        'has_prev': False,
        'has_next': False,
        'prev_num': None,
        'next_num': None,
        'iter_pages': lambda: range(1, 2)
    }
    
    return render_template('mobile/notifications.html',
                          notifications=notifications,
                          pagination=pagination)

# API endpoint لتعليم إشعار كمقروء
@mobile_bp.route('/api/notifications/<notification_id>/read', methods=['POST'])
def mark_notification_as_read(notification_id):
    """تعليم إشعار كمقروء"""
    # في الإصدار الحقيقي سيتم حفظ حالة قراءة الإشعارات في قاعدة البيانات
    
    # للإصدار الحالي البسيط نستخدم session لتخزين الإشعارات المقروءة
    read_notifications = session.get('read_notifications', [])
    
    if notification_id not in read_notifications:
        read_notifications.append(notification_id)
        session['read_notifications'] = read_notifications
        
    return jsonify({'success': True})

# API endpoint لتعليم جميع الإشعارات كمقروءة
@mobile_bp.route('/api/notifications/read-all', methods=['POST'])
def mark_all_notifications_as_read():
    """تعليم جميع الإشعارات كمقروءة"""
    # في الإصدار التجريبي، نعلم فقط الإشعارات التجريبية كمقروءة
    read_notifications = ['1', '2', '3']
    session['read_notifications'] = read_notifications
    
    return jsonify({'success': True})

# API endpoint لحذف إشعار
@mobile_bp.route('/api/notifications/<notification_id>', methods=['DELETE'])
def delete_notification(notification_id):
    """حذف إشعار"""
    # في الإصدار الحقيقي سيتم حذف الإشعار من قاعدة البيانات أو تحديث حالته
    
    # للإصدار الحالي البسيط نستخدم session لتخزين الإشعارات المحذوفة
    deleted_notifications = session.get('deleted_notifications', [])
    
    if notification_id not in deleted_notifications:
        deleted_notifications.append(notification_id)
        session['deleted_notifications'] = deleted_notifications
    
    # إذا كان الإشعار مقروءاً، نحذفه من قائمة الإشعارات المقروءة
    read_notifications = session.get('read_notifications', [])
    if notification_id in read_notifications:
        read_notifications.remove(notification_id)
        session['read_notifications'] = read_notifications
    
    return jsonify({'success': True})

# صفحة الإعدادات - النسخة المحمولة
@mobile_bp.route('/settings')
@login_required
def settings():
    """صفحة الإعدادات للنسخة المحمولة"""
    current_year = datetime.now().year
    return render_template('mobile/settings.html', current_year=current_year)

# صفحة الملف الشخصي - النسخة المحمولة
@mobile_bp.route('/profile')
@login_required
def profile():
    """صفحة الملف الشخصي للنسخة المحمولة"""
    # يمكن تنفيذ هذه الوظيفة لاحقًا
    return render_template('mobile/profile.html')

# صفحة تغيير كلمة المرور - النسخة المحمولة
@mobile_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """صفحة تغيير كلمة المرور للنسخة المحمولة"""
    # يمكن تنفيذ هذه الوظيفة لاحقًا
    return render_template('mobile/change_password.html')

# صفحة شروط الاستخدام - النسخة المحمولة
@mobile_bp.route('/terms')
def terms():
    """صفحة شروط الاستخدام للنسخة المحمولة"""
    # يمكن تنفيذ هذه الوظيفة لاحقًا
    return render_template('mobile/terms.html')

# صفحة سياسة الخصوصية - النسخة المحمولة
@mobile_bp.route('/privacy')
def privacy():
    """صفحة سياسة الخصوصية للنسخة المحمولة"""
    # يمكن تنفيذ هذه الوظيفة لاحقًا
    return render_template('mobile/privacy.html')

# صفحة تواصل معنا - النسخة المحمولة
@mobile_bp.route('/contact')
def contact():
    """صفحة تواصل معنا للنسخة المحمولة"""
    # يمكن تنفيذ هذه الوظيفة لاحقًا
    return render_template('mobile/contact.html')

# صفحة التطبيق غير متصل بالإنترنت - النسخة المحمولة
@mobile_bp.route('/offline')
def offline():
    """صفحة التطبيق غير متصل بالإنترنت للنسخة المحمولة"""
    return render_template('mobile/offline.html')

# نقطة نهاية للتحقق من حالة الاتصال - النسخة المحمولة
@mobile_bp.route('/api/check-connection')
def check_connection():
    """نقطة نهاية للتحقق من حالة الاتصال للنسخة المحمولة"""
    return jsonify({'status': 'online', 'timestamp': datetime.now().isoformat()})


# صفحة مصروفات السيارات (الوقود) - النسخة المحمولة
@mobile_bp.route('/vehicles/expenses')
@login_required
def vehicle_expenses():
    """صفحة مصروفات الوقود للسيارات - النسخة المحمولة"""
    # الحصول على معلمات الفلاتر
    vehicle_id_str = request.args.get('vehicle_id', '')
    vehicle_id = int(vehicle_id_str) if vehicle_id_str and vehicle_id_str.isdigit() else None
    period = request.args.get('period', 'month')  # الفترة الزمنية: week, month, quarter, year
    
    # تحديد تاريخ البداية حسب الفترة
    today = date.today()
    if period == 'week':
        start_date = today - timedelta(days=7)
        period_text = 'الأسبوع الماضي'
    elif period == 'month':
        start_date = today.replace(day=1)
        period_text = 'الشهر الحالي'
    elif period == 'quarter':
        month = today.month - (today.month - 1) % 3
        start_date = today.replace(month=month, day=1)
        period_text = 'الربع الحالي'
    elif period == 'year':
        start_date = today.replace(month=1, day=1)
        period_text = 'السنة الحالية'
    else:
        start_date = today - timedelta(days=30)
        period_text = 'آخر 30 يوم'
    
    # استعلام سجلات الوقود
    query = VehicleFuelConsumption.query.filter(VehicleFuelConsumption.date >= start_date)
    
    # تطبيق فلتر السيارة إذا تم تحديده
    if vehicle_id:
        query = query.filter_by(vehicle_id=vehicle_id)
    
    # ترتيب السجلات حسب التاريخ (الأحدث أولاً)
    query = query.order_by(VehicleFuelConsumption.date.desc())
    
    # الحصول على سجلات تعبئة الوقود
    fuel_records = query.limit(20).all()
    
    # حساب الإحصائيات
    # إجمالي التكلفة والكمية للأسبوع الحالي
    week_start = today - timedelta(days=today.weekday())
    weekly_stats = db.session.query(
        func.sum(VehicleFuelConsumption.cost).label('total_cost'),
        func.sum(VehicleFuelConsumption.liters).label('total_liters')
    ).filter(VehicleFuelConsumption.date >= week_start)
    
    if vehicle_id:
        weekly_stats = weekly_stats.filter(VehicleFuelConsumption.vehicle_id == vehicle_id)
    
    weekly_stats = weekly_stats.first()
    weekly_cost = weekly_stats.total_cost if weekly_stats and weekly_stats.total_cost else 0
    weekly_liters = weekly_stats.total_liters if weekly_stats and weekly_stats.total_liters else 0
    
    # إجمالي التكلفة والكمية للشهر الحالي
    month_start = today.replace(day=1)
    monthly_stats = db.session.query(
        func.sum(VehicleFuelConsumption.cost).label('total_cost'),
        func.sum(VehicleFuelConsumption.liters).label('total_liters')
    ).filter(VehicleFuelConsumption.date >= month_start)
    
    if vehicle_id:
        monthly_stats = monthly_stats.filter(VehicleFuelConsumption.vehicle_id == vehicle_id)
    
    monthly_stats = monthly_stats.first()
    monthly_cost = monthly_stats.total_cost if monthly_stats and monthly_stats.total_cost else 0
    monthly_liters = monthly_stats.total_liters if monthly_stats and monthly_stats.total_liters else 0
    
    # الحصول على جميع السيارات للفلاتر
    vehicles = Vehicle.query.order_by(Vehicle.make, Vehicle.model).all()
    
    return render_template('mobile/vehicle_expenses.html',
                          fuel_records=fuel_records,
                          vehicles=vehicles,
                          selected_vehicle=vehicle_id,
                          period=period,
                          period_text=period_text,
                          weekly_cost=weekly_cost,
                          weekly_liters=weekly_liters,
                          monthly_cost=monthly_cost,
                          monthly_liters=monthly_liters)


# صفحة إضافة تعبئة وقود - النسخة المحمولة
@mobile_bp.route('/vehicles/expenses/add-fuel', methods=['GET', 'POST'])
@login_required
def add_fuel_consumption():
    """صفحة إضافة تعبئة وقود جديدة - النسخة المحمولة"""
    # الحصول على قائمة السيارات
    vehicles = Vehicle.query.order_by(Vehicle.make, Vehicle.model).all()
    
    if request.method == 'POST':
        try:
            # التحقق من نوع الطلب (واحد أو متعدد)
            repeat_type = request.form.get('repeat_type')
            
            # إذا كان هناك تكرار لعدة أيام
            if repeat_type and repeat_type != 'none' and 'dates[]' in request.form:
                # الحصول على البيانات المشتركة
                vehicle_id = request.form.get('vehicle_id', type=int)
                liters = request.form.get('liters', type=float)
                cost = request.form.get('cost', type=float)
                kilometer_reading = request.form.get('kilometer_reading', type=int)
                driver_name = request.form.get('driver_name')
                fuel_type = request.form.get('fuel_type')
                filling_station = request.form.get('filling_station')
                notes = request.form.get('notes')
                
                # التحقق من البيانات المطلوبة
                if not (vehicle_id and liters and cost):
                    return jsonify({
                        'status': 'error',
                        'message': 'جميع الحقول المطلوبة يجب ملؤها'
                    })
                
                # الحصول على التواريخ
                dates = request.form.getlist('dates[]')
                if not dates:
                    return jsonify({
                        'status': 'error',
                        'message': 'لم يتم تحديد أي تواريخ للتكرار'
                    })
                
                # إنشاء سجلات متعددة
                records_count = 0
                for date_str in dates:
                    try:
                        # تحويل التاريخ
                        consumption_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                        
                        # إنشاء سجل جديد لتعبئة الوقود
                        new_fuel_record = VehicleFuelConsumption(
                            vehicle_id=vehicle_id,
                            date=consumption_date,
                            liters=liters,
                            cost=cost,
                            kilometer_reading=kilometer_reading,
                            driver_name=driver_name,
                            fuel_type=fuel_type,
                            filling_station=filling_station,
                            notes=notes
                        )
                        
                        # إضافة السجل إلى قاعدة البيانات
                        db.session.add(new_fuel_record)
                        records_count += 1
                    except Exception as e:
                        print(f"خطأ في إضافة سجل لتاريخ {date_str}: {str(e)}")
                
                # حفظ جميع السجلات
                if records_count > 0:
                    db.session.commit()
                    
                    return jsonify({
                        'status': 'success',
                        'message': f'تم إضافة {records_count} سجل لتعبئة الوقود بنجاح',
                        'redirect_url': url_for('mobile.vehicle_expenses')
                    })
                else:
                    return jsonify({
                        'status': 'error',
                        'message': 'لم يتم إضافة أي سجلات'
                    })
                
            else:
                # معالجة النموذج العادي (تعبئة واحدة)
                vehicle_id = request.form.get('vehicle_id', type=int)
                date_str = request.form.get('date')
                liters = request.form.get('liters', type=float)
                cost = request.form.get('cost', type=float)
                kilometer_reading = request.form.get('kilometer_reading', type=int)
                driver_name = request.form.get('driver_name')
                fuel_type = request.form.get('fuel_type')
                filling_station = request.form.get('filling_station')
                notes = request.form.get('notes')
                
                # التحقق من البيانات المطلوبة
                if not (vehicle_id and date_str and liters and cost):
                    flash('جميع الحقول المطلوبة يجب ملؤها', 'danger')
                    return render_template('mobile/add_fuel_consumption.html', 
                                        vehicles=vehicles,
                                        now=datetime.now())
                
                # تحويل التاريخ
                consumption_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                
                # إنشاء سجل جديد لتعبئة الوقود
                new_fuel_record = VehicleFuelConsumption(
                    vehicle_id=vehicle_id,
                    date=consumption_date,
                    liters=liters,
                    cost=cost,
                    kilometer_reading=kilometer_reading,
                    driver_name=driver_name,
                    fuel_type=fuel_type,
                    filling_station=filling_station,
                    notes=notes
                )
                
                # حفظ السجل في قاعدة البيانات
                db.session.add(new_fuel_record)
                db.session.commit()
                
                flash('تم إضافة تعبئة الوقود بنجاح', 'success')
                return redirect(url_for('mobile.vehicle_expenses'))
            
        except Exception as e:
            db.session.rollback()
            if request.is_xhr or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'status': 'error',
                    'message': f'حدث خطأ أثناء حفظ البيانات: {str(e)}'
                })
            else:
                flash(f'حدث خطأ أثناء حفظ البيانات: {str(e)}', 'danger')
                print(f"خطأ في إضافة تعبئة الوقود: {str(e)}")
    
    # عرض النموذج
    return render_template('mobile/add_fuel_consumption.html', 
                          vehicles=vehicles,
                          now=datetime.now())


# صفحة إحصائيات استهلاك الوقود - النسخة المحمولة
@mobile_bp.route('/vehicles/expenses/stats')
@login_required
def fuel_consumption_stats():
    """صفحة إحصائيات استهلاك الوقود - النسخة المحمولة"""
    # الحصول على معلمات الفلاتر
    vehicle_id_str = request.args.get('vehicle_id', '')
    vehicle_id = int(vehicle_id_str) if vehicle_id_str and vehicle_id_str.isdigit() else None
    fuel_type = request.args.get('fuel_type', '')
    period = request.args.get('period', 'month')  # الفترة الزمنية: week, month, quarter, year, custom
    
    # فلاتر التاريخ المخصصة
    start_date_str = request.args.get('start_date', '')
    end_date_str = request.args.get('end_date', '')
    
    # فلاتر أيام الأسبوع
    weekdays = request.args.getlist('weekdays')
    
    # تحويل أيام الأسبوع إلى أرقام صحيحة
    selected_weekdays = weekdays.copy()
    weekday_filter = [int(day) for day in weekdays if day.isdigit()]
    
    # تحديد تاريخ البداية والنهاية حسب الفترة
    today = date.today()
    end_date = today
    
    if period == 'custom' and start_date_str and end_date_str:
        # استخدام التاريخ المخصص
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            period_text = f'من {start_date_str} إلى {end_date_str}'
        except ValueError:
            # إذا كان التاريخ غير صالح، استخدم الشهر الحالي كافتراضي
            start_date = today.replace(day=1)
            period_text = 'الشهر الحالي'
    elif period == 'week':
        start_date = today - timedelta(days=7)
        period_text = 'آخر أسبوع'
    elif period == 'month':
        start_date = today - timedelta(days=30)
        period_text = 'آخر 30 يوم'
    elif period == 'quarter':
        start_date = today - timedelta(days=90)
        period_text = 'آخر 3 أشهر'
    elif period == 'year':
        start_date = today - timedelta(days=365)
        period_text = 'آخر سنة'
    else:
        # الافتراضي: آخر شهر
        start_date = today - timedelta(days=30)
        period_text = 'آخر 30 يوم'
    
    # استعلام سجلات الوقود
    query = VehicleFuelConsumption.query.filter(
        VehicleFuelConsumption.date >= start_date,
        VehicleFuelConsumption.date <= end_date
    )
    
    # تطبيق فلتر السيارة إذا تم تحديده
    if vehicle_id:
        query = query.filter_by(vehicle_id=vehicle_id)
    
    # تطبيق فلتر نوع الوقود إذا تم تحديده
    if fuel_type:
        query = query.filter_by(fuel_type=fuel_type)
    
    # تطبيق فلتر أيام الأسبوع إذا تم تحديدها
    if weekday_filter:
        # إضافة وظيفة استخراج يوم الأسبوع من التاريخ
        query = query.filter(extract('dow', VehicleFuelConsumption.date).in_(weekday_filter))
    
    # ترتيب السجلات حسب التاريخ (الأحدث أولاً)
    fuel_records = query.order_by(VehicleFuelConsumption.date.desc()).all()
    
    # حساب الإحصائيات العامة
    total_liters = sum(record.liters for record in fuel_records) if fuel_records else 0
    total_cost = sum(record.cost for record in fuel_records) if fuel_records else 0
    
    # حساب متوسط التكلفة اليومي
    days_in_period = (end_date - start_date).days + 1
    daily_avg_cost = total_cost / days_in_period if days_in_period > 0 else 0
    
    # حساب متوسط تكلفة اللتر
    avg_cost_per_liter = total_cost / total_liters if total_liters > 0 else 0
    
    # إحصائيات حسب نوع الوقود
    fuel_types_stats = {}
    for record in fuel_records:
        fuel_type_name = record.fuel_type if record.fuel_type else 'غير محدد'
        
        if fuel_type_name not in fuel_types_stats:
            fuel_types_stats[fuel_type_name] = {
                'liters': 0,
                'cost': 0,
                'count': 0,
                'percentage': 0
            }
        
        fuel_types_stats[fuel_type_name]['liters'] += record.liters
        fuel_types_stats[fuel_type_name]['cost'] += record.cost
        fuel_types_stats[fuel_type_name]['count'] += 1
    
    # حساب النسبة المئوية لكل نوع وقود
    for fuel_type_name, stats in fuel_types_stats.items():
        if total_cost > 0:
            stats['percentage'] = (stats['cost'] / total_cost) * 100
    
    # إعداد بيانات الرسم البياني
    # تجميع البيانات حسب التاريخ والنوع
    chart_data = {}
    fuel_type_chart_data = {}
    
    for record in fuel_records:
        date_str = record.date.strftime('%Y-%m-%d')
        fuel_type_name = record.fuel_type if record.fuel_type else 'غير محدد'
        
        # البيانات الإجمالية
        if date_str not in chart_data:
            chart_data[date_str] = {'liters': 0, 'cost': 0}
        chart_data[date_str]['liters'] += record.liters
        chart_data[date_str]['cost'] += record.cost
        
        # البيانات حسب نوع الوقود
        if fuel_type_name not in fuel_type_chart_data:
            fuel_type_chart_data[fuel_type_name] = {
                'liters': {},
                'costs': {}
            }
        
        if date_str not in fuel_type_chart_data[fuel_type_name]['liters']:
            fuel_type_chart_data[fuel_type_name]['liters'][date_str] = 0
            fuel_type_chart_data[fuel_type_name]['costs'][date_str] = 0
            
        fuel_type_chart_data[fuel_type_name]['liters'][date_str] += record.liters
        fuel_type_chart_data[fuel_type_name]['costs'][date_str] += record.cost
    
    # ترتيب البيانات حسب التاريخ
    sorted_dates = sorted(chart_data.keys())
    chart_labels = sorted_dates
    chart_liters = [chart_data[date]['liters'] for date in sorted_dates]
    chart_costs = [chart_data[date]['cost'] for date in sorted_dates]
    
    # معالجة بيانات الرسم البياني حسب نوع الوقود
    for fuel_type_name, data in fuel_type_chart_data.items():
        # ضمان وجود جميع التواريخ
        for date_str in sorted_dates:
            if date_str not in data['liters']:
                data['liters'][date_str] = 0
            if date_str not in data['costs']:
                data['costs'][date_str] = 0
        
        # ترتيب البيانات حسب التاريخ
        data['liters'] = [data['liters'].get(date, 0) for date in sorted_dates]
        data['costs'] = [data['costs'].get(date, 0) for date in sorted_dates]
    
    # الحصول على جميع السيارات للفلاتر
    vehicles = Vehicle.query.order_by(Vehicle.make, Vehicle.model).all()
    
    return render_template('mobile/fuel_consumption_stats.html',
                          fuel_records=fuel_records,
                          vehicles=vehicles,
                          selected_vehicle=vehicle_id,
                          selected_fuel_type=fuel_type,
                          selected_weekdays=selected_weekdays,
                          period=period,
                          period_text=period_text,
                          start_date=start_date_str,
                          end_date=end_date_str,
                          total_liters=total_liters,
                          total_cost=total_cost,
                          daily_avg_cost=daily_avg_cost,
                          avg_cost_per_liter=avg_cost_per_liter,
                          fuel_types_stats=fuel_types_stats,
                          fuel_type_chart_data=fuel_type_chart_data,
                          chart_labels=chart_labels,
                          chart_liters=chart_liters,
                          chart_costs=chart_costs)


# ==================== مسارات إدارة المستخدمين - النسخة المحمولة المطورة ====================

# صفحة إدارة المستخدمين - النسخة المحمولة المطورة
@mobile_bp.route('/users_new')
@login_required
@module_access_required('users')
def users_new():
    """صفحة إدارة المستخدمين للنسخة المحمولة المطورة"""
    
    page = request.args.get('page', 1, type=int)
    per_page = 20  # عدد العناصر في الصفحة الواحدة
    
    # إنشاء الاستعلام الأساسي
    query = User.query
    
    # تطبيق الفلترة حسب الاستعلام
    if request.args.get('search'):
        search_term = f"%{request.args.get('search')}%"
        query = query.filter(
            (User.name.like(search_term)) |
            (User.email.like(search_term))
        )
    
    # ترتيب النتائج
    query = query.order_by(User.name)
    
    # تنفيذ الاستعلام مع الصفحات
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    users = pagination.items
    
    return render_template('mobile/users_new.html',
                          users=users,
                          pagination=pagination)

# إضافة مستخدم جديد - النسخة المحمولة المطورة
@mobile_bp.route('/users_new/add', methods=['GET', 'POST'])
@login_required
@module_access_required('users')
def add_user_new():
    """إضافة مستخدم جديد للنسخة المحمولة المطورة"""
    
    # معالجة النموذج المرسل
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        
        # التحقق من البيانات المطلوبة
        if not (username and email and password and role):
            flash('جميع الحقول المطلوبة يجب ملؤها', 'danger')
            return render_template('mobile/add_user_new.html', roles=UserRole)
        
        # التحقق من عدم وجود البريد الإلكتروني مسبقاً
        if User.query.filter_by(email=email).first():
            flash('البريد الإلكتروني مستخدم بالفعل', 'danger')
            return render_template('mobile/add_user_new.html', roles=UserRole)
        
        # إنشاء مستخدم جديد
        new_user = User(
            username=username,
            email=email,
            role=role
        )
        new_user.set_password(password)
        
        try:
            db.session.add(new_user)
            db.session.commit()
            
            flash('تم إضافة المستخدم بنجاح', 'success')
            return redirect(url_for('mobile.users_new'))
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء إضافة المستخدم: {str(e)}', 'danger')
    
    # عرض النموذج
    return render_template('mobile/add_user_new.html', roles=UserRole)

# تفاصيل المستخدم - النسخة المحمولة المطورة
@mobile_bp.route('/users_new/<int:user_id>')
@login_required
@module_access_required('users')
def user_details_new(user_id):
    """تفاصيل المستخدم للنسخة المحمولة المطورة"""
    
    user = User.query.get_or_404(user_id)
    
    return render_template('mobile/user_details_new.html', user=user)

# تعديل بيانات المستخدم - النسخة المحمولة المطورة
@mobile_bp.route('/users_new/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@module_access_required('users')
def edit_user_new(user_id):
    """تعديل بيانات المستخدم للنسخة المحمولة المطورة"""
    
    user = User.query.get_or_404(user_id)
    
    # معالجة النموذج المرسل
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        role = request.form.get('role')
        is_active = request.form.get('is_active') == 'on'
        
        # التحقق من البيانات المطلوبة
        if not (username and email and role):
            flash('جميع الحقول المطلوبة يجب ملؤها', 'danger')
            return render_template('mobile/edit_user_new.html', user=user, roles=UserRole)
        
        # التحقق من عدم وجود البريد الإلكتروني لمستخدم آخر
        email_user = User.query.filter_by(email=email).first()
        if email_user and email_user.id != user.id:
            flash('البريد الإلكتروني مستخدم بالفعل', 'danger')
            return render_template('mobile/edit_user_new.html', user=user, roles=UserRole)
        
        # تحديث بيانات المستخدم
        user.name = username
        user.email = email
        user.role = role
        user.is_active = is_active
        
        # تحديث كلمة المرور إذا تم تقديمها
        new_password = request.form.get('password')
        if new_password:
            user.set_password(new_password)
        
        try:
            db.session.commit()
            flash('تم تحديث بيانات المستخدم بنجاح', 'success')
            return redirect(url_for('mobile.user_details_new', user_id=user.id))
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء تحديث بيانات المستخدم: {str(e)}', 'danger')
    
    # عرض النموذج
    return render_template('mobile/edit_user_new.html', user=user, roles=UserRole)

# حذف مستخدم - النسخة المحمولة المطورة
@mobile_bp.route('/users_new/<int:user_id>/delete', methods=['GET', 'POST'])
@login_required
@permission_required('users', 'delete')
def delete_user_new(user_id):
    """حذف مستخدم من النسخة المحمولة المطورة"""
    
    user = User.query.get_or_404(user_id)
    
    # منع حذف المستخدم الحالي
    if user.id == current_user.id:
        flash('لا يمكنك حذف المستخدم الحالي', 'danger')
        return redirect(url_for('mobile.users_new'))
    
    if request.method == 'POST':
        try:
            # حذف المستخدم
            db.session.delete(user)
            db.session.commit()
            
            flash('تم حذف المستخدم بنجاح', 'success')
            return redirect(url_for('mobile.users_new'))
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء حذف المستخدم: {str(e)}', 'danger')
            return redirect(url_for('mobile.user_details_new', user_id=user.id))
    
    return render_template('mobile/delete_user_new.html', user=user)


# ==================== مسارات الرسوم والتكاليف - النسخة المحمولة المطورة ====================

# صفحة إدارة الرسوم والتكاليف - النسخة المحمولة المطورة
@mobile_bp.route('/fees_new')
@login_required
@module_access_required('fees')
def fees_new():
    """صفحة الرسوم والتكاليف للنسخة المحمولة المطورة"""
    
    page = request.args.get('page', 1, type=int)
    per_page = 20  # عدد العناصر في الصفحة الواحدة
    status = request.args.get('status', 'all')
    document_type = request.args.get('document_type', 'all')
    
    # إنشاء الاستعلام الأساسي
    query = Fee.query.join(Document)
    
    # تطبيق الفلاتر
    if status != 'all':
        query = query.filter(Fee.payment_status == status)
    
    if document_type != 'all':
        query = query.filter(Fee.document_type == document_type)
    
    # البحث
    if request.args.get('search'):
        search_term = f"%{request.args.get('search')}%"
        query = query.join(Document.employee).filter(
            (Employee.name.like(search_term)) |
            (Employee.employee_id.like(search_term)) |
            (Document.document_number.like(search_term))
        )
    
    # ترتيب النتائج حسب تاريخ الاستحقاق (الأقرب أولاً)
    query = query.order_by(Fee.due_date)
    
    # تنفيذ الاستعلام مع الصفحات
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    fees = pagination.items
    
    # حساب إحصائيات الرسوم
    current_date = datetime.now().date()
    due_count = Fee.query.filter(Fee.due_date <= current_date, Fee.payment_status == 'pending').count()
    paid_count = Fee.query.filter(Fee.payment_status == 'paid').count()
    overdue_count = Fee.query.filter(Fee.due_date < current_date, Fee.payment_status == 'pending').count()
    
    stats = {
        'due': due_count,
        'paid': paid_count,
        'overdue': overdue_count,
        'total': Fee.query.count()
    }
    
    # أنواع الوثائق للفلترة
    document_types = [
        'هوية وطنية',
        'إقامة',
        'جواز سفر',
        'رخصة قيادة',
        'شهادة صحية',
        'شهادة تأمين',
        'أخرى'
    ]
    
    return render_template('mobile/fees_new.html',
                          fees=fees,
                          pagination=pagination,
                          stats=stats,
                          document_types=document_types,
                          current_date=current_date,
                          selected_status=status,
                          selected_document_type=document_type)

# ==================== مسارات الإشعارات - النسخة المحمولة المطورة ====================

@mobile_bp.route('/notifications_new')
@login_required
def notifications_new():
    """صفحة الإشعارات للنسخة المحمولة المطورة"""
    page = request.args.get('page', 1, type=int)
    per_page = 20  # عدد العناصر في الصفحة الواحدة
    
    # هنا يمكن تنفيذ استعلام الإشعارات بناءً على نظام الإشعارات المستخدم
    
    # مثال: استعلام للوثائق التي على وشك الانتهاء كإشعارات
    current_date = datetime.now().date()
    expiring_30_days = current_date + timedelta(days=30)
    expiring_documents = Document.query.filter(
        Document.expiry_date > current_date,
        Document.expiry_date <= expiring_30_days
    ).order_by(Document.expiry_date).all()
    
    # مثال: الرسوم المستحقة (استخدام النموذج المتاح Fee المستورد من FeesCost)
    # ملاحظة: تم تعديل هذا الجزء لاستخدام النموذج المتاح بدلاً من الأصلي
    due_fees = Fee.query.join(Document).filter(
        Document.expiry_date > current_date,
        Document.expiry_date <= current_date + timedelta(days=30)
    ).order_by(Document.expiry_date).all()
    
    # تحضير قائمة الإشعارات المدمجة
    notifications = []
    
    for doc in expiring_documents:
        remaining_days = (doc.expiry_date - current_date).days
        notifications.append({
            'id': f'doc_{doc.id}',
            'type': 'document',
            'title': f'وثيقة على وشك الانتهاء: {doc.document_type}',
            'description': f'متبقي {remaining_days} يوم على انتهاء {doc.document_type} للموظف {doc.employee.name}',
            'date': doc.expiry_date,
            'url': url_for('mobile.document_details', document_id=doc.id),
            'is_read': False  # يمكن تنفيذ حالة القراءة لاحقاً
        })
    
    for fee in due_fees:
        # استخدام تاريخ انتهاء الوثيقة المرتبطة بالرسوم
        doc = Document.query.get(fee.document_id)
        if not doc:
            continue
            
        remaining_days = (doc.expiry_date - current_date).days
        document_type = fee.document_type
        total_amount = sum([
            fee.passport_fee or 0,
            fee.labor_office_fee or 0,
            fee.insurance_fee or 0,
            fee.social_insurance_fee or 0
        ])
        notifications.append({
            'id': f'fee_{fee.id}',
            'type': 'fee',
            'title': f'رسوم مستحقة قريباً: {document_type}',
            'description': f'رسوم مستحقة بعد {remaining_days} يوم بقيمة {total_amount:.2f}',
            'date': doc.expiry_date,
            'url': url_for('mobile.fee_details', fee_id=fee.id),
            'is_read': False
        })
    
    # ترتيب الإشعارات حسب التاريخ (الأقرب أولاً)
    notifications.sort(key=lambda x: x['date'])
    
    # تقسيم النتائج
    total_notifications = len(notifications)
    start_idx = (page - 1) * per_page
    end_idx = min(start_idx + per_page, total_notifications)
    current_notifications = notifications[start_idx:end_idx]
    
    # إنشاء كائن تقسيم صفحات بسيط
    # نستخدم قاموس بدلاً من كائن Pagination لتبسيط التنفيذ
    pagination = {
        'page': page,
        'per_page': per_page,
        'total': total_notifications,
        'pages': (total_notifications + per_page - 1) // per_page,
        'items': current_notifications,
        'has_prev': page > 1,
        'has_next': page < ((total_notifications + per_page - 1) // per_page),
        'prev_num': page - 1 if page > 1 else None,
        'next_num': page + 1 if page < ((total_notifications + per_page - 1) // per_page) else None
    }
    
    return render_template('mobile/notifications_new.html',
                          notifications=current_notifications,
                          pagination=pagination,
                          current_date=current_date)

# إنشاء نموذج تسليم/استلام - النسخة المحمولة
@mobile_bp.route('/vehicles/handover/create/<int:vehicle_id>', methods=['GET', 'POST'])
@login_required
def create_handover(vehicle_id):
    """إنشاء نموذج تسليم/استلام للسيارة للنسخة المحمولة"""
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    if request.method == 'POST':
        # استخراج البيانات من النموذج
        handover_type = request.form.get('handover_type')
        handover_date = datetime.strptime(request.form.get('handover_date'), '%Y-%m-%d').date()
        person_name = request.form.get('person_name')
        supervisor_name = request.form.get('supervisor_name', '')
        form_link = request.form.get('form_link', '')
        vehicle_condition = request.form.get('vehicle_condition')
        fuel_level = request.form.get('fuel_level')
        mileage_str = request.form.get('mileage', '0')
        mileage = int(mileage_str) if mileage_str and mileage_str.isdigit() else 0
        has_spare_tire = 'has_spare_tire' in request.form
        has_fire_extinguisher = 'has_fire_extinguisher' in request.form
        has_tools = 'has_tools' in request.form
        has_first_aid_kit = 'has_first_aid_kit' in request.form
        has_warning_triangle = 'has_warning_triangle' in request.form
        notes = request.form.get('notes', '')
        
        # إنشاء سجل تسليم/استلام جديد
        handover = VehicleHandover(
            vehicle_id=vehicle_id,
            handover_type=handover_type,
            handover_date=handover_date,
            person_name=person_name,
            supervisor_name=supervisor_name,
            form_link=form_link,
            vehicle_condition=vehicle_condition,
            fuel_level=fuel_level,
            mileage=mileage,
            has_spare_tire=has_spare_tire,
            has_fire_extinguisher=has_fire_extinguisher,
            has_tools=has_tools,
            has_first_aid_kit=has_first_aid_kit,
            has_warning_triangle=has_warning_triangle,
            notes=notes
        )
        
        try:
            db.session.add(handover)
            db.session.commit()
            
            # تسجيل نشاط النظام
            description = f"تم إنشاء نموذج {'تسليم' if handover_type == 'delivery' else 'استلام'} للسيارة {vehicle.plate_number}"
            SystemAudit.create_audit_record(
                current_user.id,
                'إنشاء',
                'VehicleHandover',
                handover.id,
                description,
                entity_name=f"سيارة: {vehicle.plate_number}"
            )
            
            flash('تم إنشاء نموذج التسليم/الاستلام بنجاح', 'success')
            return redirect(url_for('mobile.vehicle_details', vehicle_id=vehicle_id))
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء إنشاء النموذج: {str(e)}', 'danger')
    
    # عرض نموذج إنشاء تسليم/استلام
    return render_template('mobile/create_handover.html', 
                           vehicle=vehicle,
                           now=datetime.now())

# عرض تفاصيل نموذج تسليم/استلام - النسخة المحمولة
@mobile_bp.route('/vehicles/handover/<int:handover_id>')
@login_required
def view_handover(handover_id):
    """عرض تفاصيل نموذج تسليم/استلام للنسخة المحمولة"""
    handover = VehicleHandover.query.get_or_404(handover_id)
    vehicle = Vehicle.query.get_or_404(handover.vehicle_id)
    images = VehicleHandoverImage.query.filter_by(handover_record_id=handover_id).all()
    
    # تنسيق التاريخ للعرض
    handover.formatted_handover_date = handover.handover_date.strftime('%Y-%m-%d')
    
    handover_type_name = 'تسليم' if handover.handover_type == 'delivery' else 'استلام'
    
    return render_template('mobile/handover_view.html',
                           handover=handover,
                           vehicle=vehicle,
                           images=images,
                           handover_type_name=handover_type_name)

# إنشاء ملف PDF لنموذج تسليم/استلام - النسخة المحمولة
@mobile_bp.route('/vehicles/handover/<int:handover_id>/pdf')
@login_required
def handover_pdf(handover_id):
    """إنشاء نموذج تسليم/استلام كملف PDF للنسخة المحمولة"""
    from flask import send_file, flash, redirect, url_for
    import io
    import os
    from datetime import datetime
    from utils.pdf_generator_fixed import generate_vehicle_handover_pdf
    
    try:
        # الحصول على بيانات التسليم/الاستلام
        handover = VehicleHandover.query.get_or_404(handover_id)
        vehicle = Vehicle.query.get_or_404(handover.vehicle_id)
        images = VehicleHandoverImage.query.filter_by(handover_record_id=handover_id).all()
        
        # تجهيز البيانات لملف PDF
        handover_data = {
            'vehicle': {
                'plate_number': str(vehicle.plate_number),
                'make': str(vehicle.make),
                'model': str(vehicle.model),
                'year': int(vehicle.year),
                'color': str(vehicle.color)
            },
            'handover_type': 'تسليم' if handover.handover_type == 'delivery' else 'استلام',
            'handover_date': handover.handover_date.strftime('%Y-%m-%d'),
            'person_name': str(handover.person_name),
            'supervisor_name': str(handover.supervisor_name) if handover.supervisor_name else "",
            'vehicle_condition': str(handover.vehicle_condition),
            'fuel_level': str(handover.fuel_level),
            'mileage': int(handover.mileage),
            'has_spare_tire': bool(handover.has_spare_tire),
            'has_fire_extinguisher': bool(handover.has_fire_extinguisher),
            'has_first_aid_kit': bool(handover.has_first_aid_kit),
            'has_warning_triangle': bool(handover.has_warning_triangle),
            'has_tools': bool(handover.has_tools),
            'notes': str(handover.notes) if handover.notes else "",
            'form_link': str(handover.form_link) if handover.form_link else "",
            'image_paths': [image.image_path for image in images] if images else []
        }
        
        # إنشاء ملف PDF
        pdf_bytes = generate_vehicle_handover_pdf(handover_data)
        
        if not pdf_bytes:
            flash('حدث خطأ أثناء إنشاء ملف PDF', 'danger')
            return redirect(url_for('mobile.view_handover', handover_id=handover_id))
        
        # تحديد اسم الملف
        filename = f"handover_form_{vehicle.plate_number}.pdf"
        
        # إرسال الملف للمستخدم
        return send_file(
            io.BytesIO(pdf_bytes),
            download_name=filename,
            as_attachment=True,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        flash(f'حدث خطأ أثناء إنشاء ملف PDF: {str(e)}', 'danger')
        return redirect(url_for('mobile.view_handover', handover_id=handover_id))

# إنشاء فحص دوري جديد للسيارة - النسخة المحمولة
@mobile_bp.route('/vehicles/<int:vehicle_id>/periodic-inspection/create', methods=['GET', 'POST'])
@login_required
def create_periodic_inspection(vehicle_id):
    """إنشاء فحص دوري جديد للسيارة - النسخة المحمولة"""
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    if request.method == 'POST':
        try:
            # استخراج البيانات من النموذج
            inspection_date = datetime.strptime(request.form.get('inspection_date'), '%Y-%m-%d').date()
            expiry_date = datetime.strptime(request.form.get('expiry_date'), '%Y-%m-%d').date()
            inspection_center = request.form.get('inspection_center')
            result = request.form.get('result')
            driver_name = request.form.get('driver_name', '')
            supervisor_name = request.form.get('supervisor_name', '')
            notes = request.form.get('notes', '')
            
            # إنشاء سجل فحص دوري جديد
            inspection = VehiclePeriodicInspection(
                vehicle_id=vehicle_id,
                inspection_date=inspection_date,
                expiry_date=expiry_date,
                inspection_center=inspection_center,
                result=result,
                driver_name=driver_name,
                supervisor_name=supervisor_name,
                notes=notes
            )
            
            db.session.add(inspection)
            db.session.commit()
            
            # تسجيل نشاط النظام
            SystemAudit.create_audit_record(
                current_user.id,
                'إنشاء',
                'VehiclePeriodicInspection',
                inspection.id,
                f"تم إضافة سجل فحص دوري للسيارة: {vehicle.plate_number}",
                entity_name=f"سيارة: {vehicle.plate_number}"
            )
            
            flash('تم إضافة سجل الفحص الدوري بنجاح', 'success')
            return redirect(url_for('mobile.vehicle_details', vehicle_id=vehicle_id))
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء إضافة سجل الفحص: {str(e)}', 'danger')
    
    # عرض صفحة إنشاء فحص دوري
    return render_template('mobile/create_periodic_inspection.html',
                           vehicle=vehicle,
                           now=datetime.now())

# إنشاء فحص سلامة جديد للسيارة - النسخة المحمولة
@mobile_bp.route('/vehicles/<int:vehicle_id>/safety-check/create', methods=['GET', 'POST'])
@login_required
def create_safety_check(vehicle_id):
    """إنشاء فحص سلامة جديد للسيارة - النسخة المحمولة"""
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    if request.method == 'POST':
        try:
            # استخراج البيانات من النموذج
            check_date = datetime.strptime(request.form.get('check_date'), '%Y-%m-%d').date()
            check_type = request.form.get('check_type')
            driver_name = request.form.get('driver_name', '')
            supervisor_name = request.form.get('supervisor_name', '')
            result = request.form.get('result')
            notes = request.form.get('notes', '')
            
            # إنشاء سجل فحص سلامة جديد
            safety_check = VehicleSafetyCheck(
                vehicle_id=vehicle_id,
                check_date=check_date,
                check_type=check_type,
                driver_name=driver_name,
                supervisor_name=supervisor_name,
                result=result,
                notes=notes
            )
            
            db.session.add(safety_check)
            db.session.commit()
            
            # تسجيل نشاط النظام
            SystemAudit.create_audit_record(
                current_user.id,
                'إنشاء',
                'VehicleSafetyCheck',
                safety_check.id,
                f"تم إضافة سجل فحص سلامة للسيارة: {vehicle.plate_number}",
                entity_name=f"سيارة: {vehicle.plate_number}"
            )
            
            flash('تم إضافة سجل فحص السلامة بنجاح', 'success')
            return redirect(url_for('mobile.vehicle_details', vehicle_id=vehicle_id))
        except Exception as e:
            db.session.rollback()
            flash(f'حدث خطأ أثناء إضافة سجل الفحص: {str(e)}', 'danger')
    
    # الحصول على قائمة السائقين والمشرفين
    drivers = Employee.query.filter(Employee.job_title.like('%سائق%')).order_by(Employee.name).all()
    supervisors = Employee.query.filter(Employee.job_title.like('%مشرف%')).order_by(Employee.name).all()
    
    # عرض صفحة إنشاء فحص سلامة
    return render_template('mobile/create_safety_check.html',
                           vehicle=vehicle,
                           drivers=drivers,
                           supervisors=supervisors,
                           now=datetime.now())


