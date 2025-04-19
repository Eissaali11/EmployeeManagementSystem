"""
مسارات ومعالجات الواجهة المحمولة
نظام إدارة الموظفين - النسخة المحمولة
"""

from datetime import datetime, timedelta
from sqlalchemy import extract
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, DateField, TextAreaField, DecimalField
from wtforms.validators import DataRequired, Email, Length, ValidationError, Optional

from models import db, User, Employee, Department, Document, Vehicle, Attendance, Salary, FeesCost as Fee, VehicleChecklist, VehicleChecklistItem, VehicleMaintenance, VehicleMaintenanceImage
from utils.hijri_converter import convert_gregorian_to_hijri, format_hijri_date

# إنشاء مخطط المسارات
mobile_bp = Blueprint('mobile', __name__)

# نموذج تسجيل الدخول
class LoginForm(FlaskForm):
    username = StringField('اسم المستخدم', validators=[DataRequired('اسم المستخدم مطلوب')])
    password = PasswordField('كلمة المرور', validators=[DataRequired('كلمة المرور مطلوبة')])
    remember = BooleanField('تذكرني')
    submit = SubmitField('تسجيل الدخول')

# الصفحة الرئيسية - النسخة المحمولة
@mobile_bp.route('/')
def index():
    """الصفحة الرئيسية للنسخة المحمولة"""
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
    
    # الحصول على بيانات إضافية للموظف (يمكن استكمالها لاحقًا)
    attendance_records = []  # سجلات الحضور
    salary = None  # معلومات الراتب
    documents = []  # الوثائق
    current_date = datetime.now().date()
    
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
    employee_id = request.args.get('employee_id', None, type=int)
    
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
    employee_id = request.args.get('employee_id', type=int)
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
    departments = Department.query.all()
    employees = Employee.query.all()
    return render_template('mobile/report_employees.html', 
                         departments=departments,
                         employees=employees)

# تقرير الحضور - النسخة المحمولة
@mobile_bp.route('/reports/attendance')
@login_required
def report_attendance():
    """تقرير الحضور للنسخة المحمولة"""
    return render_template('mobile/report_attendance.html')

# تقرير الرواتب - النسخة المحمولة
@mobile_bp.route('/reports/salaries')
@login_required
def report_salaries():
    """تقرير الرواتب للنسخة المحمولة"""
    return render_template('mobile/report_salaries.html')

# تقرير الوثائق - النسخة المحمولة
@mobile_bp.route('/reports/documents')
@login_required
def report_documents():
    """تقرير الوثائق للنسخة المحمولة"""
    return render_template('mobile/report_documents.html')

# تقرير السيارات - النسخة المحمولة 
@mobile_bp.route('/reports/vehicles')
@login_required
def report_vehicles():
    """تقرير السيارات للنسخة المحمولة"""
    return render_template('mobile/report_vehicles.html')

# تقرير الرسوم - النسخة المحمولة
@mobile_bp.route('/reports/fees')
@login_required
def report_fees():
    """تقرير الرسوم للنسخة المحمولة"""
    return render_template('mobile/report_fees.html')

# صفحة السيارات - النسخة المحمولة
@mobile_bp.route('/vehicles')
@login_required
def vehicles():
    """صفحة السيارات للنسخة المحمولة"""
    # استخدام نفس البيانات الموجودة في قاعدة البيانات
    status_filter = request.args.get('status', '')
    make_filter = request.args.get('make', '')
    
    # قاعدة الاستعلام الأساسية
    query = Vehicle.query
    
    # إضافة التصفية حسب الحالة إذا تم تحديدها
    if status_filter:
        query = query.filter(Vehicle.status == status_filter)
    
    # إضافة التصفية حسب الشركة المصنعة إذا تم تحديدها
    if make_filter:
        query = query.filter(Vehicle.make == make_filter)
    
    # الحصول على قائمة السيارات
    vehicles = query.order_by(Vehicle.status, Vehicle.plate_number).all()
    
    # إحصائيات سريعة - نعدل المسميات لتتوافق مع النسخة المحمولة
    stats = {
        'total': Vehicle.query.count(),
        'active': Vehicle.query.filter_by(status='available').count(),
        'maintenance': Vehicle.query.filter_by(status='in_workshop').count(),
        'inactive': Vehicle.query.filter_by(status='accident').count() + Vehicle.query.filter_by(status='rented').count() + Vehicle.query.filter_by(status='in_project').count()
    }
    
    return render_template('mobile/vehicles.html', vehicles=vehicles, stats=stats)
    
# تفاصيل السيارة - النسخة المحمولة
@mobile_bp.route('/vehicles/<int:vehicle_id>')
@login_required
def vehicle_details(vehicle_id):
    """تفاصيل السيارة للنسخة المحمولة"""
    # الحصول على بيانات السيارة من قاعدة البيانات
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    # الحصول على سجل الصيانة الخاص بالسيارة
    # تحتاج هذه العملية إلى تعديل في النموذج لكي تعمل، الآن نستخدم بيانات تجريبية
    maintenance_records = []
    
    # الحصول على وثائق السيارة من قاعدة البيانات
    documents = []
    
    # الحصول على رسوم السيارة من قاعدة البيانات
    fees = []
    
    # تحويل البيانات إلى التنسيق المطلوب للعرض في النسخة المحمولة
    vehicle_data = {
        'id': vehicle.id,
        'name': f"{vehicle.make} {vehicle.model}",
        'plate_number': vehicle.plate_number,
        'model': vehicle.model,
        'year': vehicle.year,
        'color': vehicle.color,
        'status': vehicle.status,
        'status_display': vehicle.status,  # يمكن إضافة معالجة للترجمة
        # التحقق من وجود الحقول قبل إضافتها لتفادي أخطاء AttributeError
        'notes': vehicle.notes if hasattr(vehicle, 'notes') else ''
    }
    
    return render_template('mobile/vehicle_details.html',
                         vehicle=vehicle_data,
                         maintenance_records=maintenance_records,
                         documents=documents,
                         fees=fees)

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
    vehicle_id = request.args.get('vehicle_id', '', type=int)
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
    
    # تنسيق البيانات لعرضها
    formatted_data = {
        'id': maintenance.id,
        'date': maintenance.date,
        'maintenance_type': maintenance.maintenance_type,
        'description': maintenance.description,
        'status': maintenance.status,
        'status_class': status_class,
        'cost': maintenance.cost,
        'technician': maintenance.technician,
        'parts_replaced': maintenance.parts_replaced,
        'actions_taken': maintenance.actions_taken,
        'notes': maintenance.notes,
        'created_at': maintenance.created_at,
        'updated_at': maintenance.updated_at,
        'images': images
    }
    
    return render_template('mobile/maintenance_details.html',
                           maintenance=formatted_data,
                           vehicle=vehicle)


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

# مصروفات السيارات - النسخة المحمولة
@mobile_bp.route('/vehicles/expenses')
@login_required
def vehicle_expenses():
    """مصروفات السيارات للنسخة المحمولة"""
    # يمكن تنفيذ هذه الوظيفة لاحقًا
    return render_template('mobile/vehicle_expenses.html')

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
    
    return render_template('mobile/vehicle_checklist_details.html',
                          checklist=checklist,
                          vehicle=vehicle,
                          checklist_items=checklist_items)


# إضافة فحص جديد للسيارة - النسخة المحمولة
@mobile_bp.route('/vehicles/checklist/add', methods=['POST'])
@login_required
def add_vehicle_checklist():
    """إضافة فحص جديد للسيارة للنسخة المحمولة"""
    if request.method == 'POST':
        # استلام بيانات الفحص من النموذج
        data = request.get_json()
        
        if not data:
            return jsonify({'status': 'error', 'message': 'لم يتم استلام بيانات'})
        
        vehicle_id = data.get('vehicle_id')
        inspection_date = data.get('inspection_date')
        inspector_name = data.get('inspector_name')
        inspection_type = data.get('inspection_type')
        general_notes = data.get('general_notes', '')
        items_data = data.get('items', [])
        
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

# صفحة الرسوم والتكاليف - النسخة المحمولة
@mobile_bp.route('/fees')
@login_required
def fees():
    """صفحة الرسوم والتكاليف للنسخة المحمولة"""
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
@login_required
def notifications():
    """صفحة الإشعارات للنسخة المحمولة"""
    # يمكننا استكمال هذه الواجهة لاحقًا
    return render_template('mobile/notifications.html')

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