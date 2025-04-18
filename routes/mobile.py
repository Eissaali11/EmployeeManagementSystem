"""
مسارات ومعالجات الواجهة المحمولة
نظام إدارة الموظفين - النسخة المحمولة
"""

from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, DateField, TextAreaField, DecimalField
from wtforms.validators import DataRequired, Email, Length, ValidationError, Optional

from models import db, User, Employee, Department, Document, Vehicle, Attendance, Salary, FeesCost
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
                            now=datetime.now())

# صفحة تسجيل الدخول - النسخة المحمولة
@mobile_bp.route('/login', methods=['GET', 'POST'])
def login():
    """صفحة تسجيل الدخول للنسخة المحمولة"""
    if current_user.is_authenticated:
        return redirect(url_for('mobile.index'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
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
    # يمكن تنفيذ هذه الوظيفة لاحقًا
    return render_template('mobile/add_attendance.html')

# تعديل سجل حضور - النسخة المحمولة
@mobile_bp.route('/attendance/<int:record_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_attendance(record_id):
    """تعديل سجل حضور للنسخة المحمولة"""
    # يمكن تنفيذ هذه الوظيفة لاحقًا
    return render_template('mobile/edit_attendance.html')

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
    # ستتم إضافة وظيفة إضافة قسم جديد لاحقاً
    return render_template('mobile/add_department.html')

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
    
    # بيانات مؤقتة - يمكن استبدالها بالبيانات الفعلية من قاعدة البيانات
    employees = Employee.query.order_by(Employee.name).all()
    salaries = []
    
    # إحصائيات الرواتب
    current_year = datetime.now().year
    current_month = datetime.now().month
    selected_year = request.args.get('year', current_year, type=int)
    selected_month = request.args.get('month', current_month, type=int)
    
    # تحويل الشهر إلى اسمه بالعربية
    month_names = {
        1: 'يناير', 2: 'فبراير', 3: 'مارس', 4: 'أبريل', 
        5: 'مايو', 6: 'يونيو', 7: 'يوليو', 8: 'أغسطس',
        9: 'سبتمبر', 10: 'أكتوبر', 11: 'نوفمبر', 12: 'ديسمبر'
    }
    selected_month_name = month_names.get(selected_month, '')
    
    salary_stats = {
        'total_basic': 0,
        'total_allowances': 0,
        'total_deductions': 0,
        'total_net': 0
    }
    
    return render_template('mobile/salaries.html',
                          employees=employees,
                          salaries=salaries,
                          current_year=current_year,
                          selected_year=selected_year,
                          selected_month=selected_month_name,
                          salary_stats=salary_stats,
                          pagination=None)

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
    page = request.args.get('page', 1, type=int)
    per_page = 20  # عدد العناصر في الصفحة الواحدة
    
    # بيانات مؤقتة - يمكن استبدالها بالبيانات الفعلية من قاعدة البيانات
    employees = Employee.query.order_by(Employee.name).all()
    documents = []
    
    # إحصائيات الوثائق
    current_date = datetime.now().date()
    document_stats = {
        'valid': 0,
        'expiring': 0,
        'expired': 0,
        'total': 0
    }
    
    return render_template('mobile/documents.html',
                          employees=employees,
                          documents=documents,
                          current_date=current_date,
                          document_stats=document_stats,
                          pagination=None)

# إضافة وثيقة جديدة - النسخة المحمولة
@mobile_bp.route('/documents/add', methods=['GET', 'POST'])
@login_required
def add_document():
    """إضافة وثيقة جديدة للنسخة المحمولة"""
    # يمكن تنفيذ هذه الوظيفة لاحقًا
    return render_template('mobile/add_document.html')

# تفاصيل وثيقة - النسخة المحمولة
@mobile_bp.route('/documents/<int:document_id>')
@login_required
def document_details(document_id):
    """تفاصيل وثيقة للنسخة المحمولة"""
    # يمكن تنفيذ هذه الوظيفة لاحقًا
    return render_template('mobile/document_details.html')

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
    # بيانات مؤقتة
    vehicles = []
    stats = {
        'active': 0,
        'maintenance': 0,
        'inactive': 0,
        'total': 0
    }
    return render_template('mobile/vehicles.html', vehicles=vehicles, stats=stats)
    
# تفاصيل السيارة - النسخة المحمولة
@mobile_bp.route('/vehicles/<int:vehicle_id>')
@login_required
def vehicle_details(vehicle_id):
    """تفاصيل السيارة للنسخة المحمولة"""
    # بيانات مؤقتة للسيارة
    vehicle = {
        'id': vehicle_id,
        'name': 'تويوتا كامري',
        'plate_number': 'أ ب ج ١٢٣٤',
        'model': 'كامري',
        'year': 2022,
        'color': 'أبيض',
        'status': 'active',
        'status_display': 'نشطة',
        'purchase_date': datetime.now().date() - timedelta(days=365),
        'purchase_price': 120000.00,
        'insurance_expiry': datetime.now().date() + timedelta(days=180),
        'license_expiry': datetime.now().date() + timedelta(days=90),
        'odometer': 15000,
        'fuel_type': 'بنزين',
        'driver': 'أحمد محمد',
        'department': 'الإدارة العامة',
        'notes': 'سيارة بحالة ممتازة وتستخدم بشكل يومي للتنقلات الرسمية'
    }
    
    # بيانات مؤقتة لسجل الصيانة
    maintenance_records = [
        {
            'id': 1,
            'date': datetime.now().date() - timedelta(days=30),
            'maintenance_type': 'دورية',
            'description': 'تغيير زيت وفلتر',
            'cost': 500.00
        },
        {
            'id': 2,
            'date': datetime.now().date() - timedelta(days=90),
            'maintenance_type': 'إصلاح',
            'description': 'إصلاح نظام التكييف',
            'cost': 1200.00
        }
    ]
    
    # بيانات مؤقتة للوثائق
    documents = [
        {
            'id': 1,
            'name': 'تأمين شامل',
            'expiry_date': datetime.now().date() + timedelta(days=180),
            'status': 'valid'
        },
        {
            'id': 2,
            'name': 'رخصة تسيير',
            'expiry_date': datetime.now().date() + timedelta(days=90),
            'status': 'valid'
        },
        {
            'id': 3,
            'name': 'الفحص الدوري',
            'expiry_date': datetime.now().date() - timedelta(days=10),
            'status': 'expired'
        }
    ]
    
    # بيانات مؤقتة للرسوم
    fees = [
        {
            'id': 1,
            'name': 'تجديد التأمين',
            'amount': 3500.00,
            'due_date': datetime.now().date() + timedelta(days=180),
            'status': 'pending'
        },
        {
            'id': 2,
            'name': 'تجديد رخصة التسيير',
            'amount': 1200.00,
            'due_date': datetime.now().date() + timedelta(days=90),
            'status': 'pending'
        }
    ]
    
    return render_template('mobile/vehicle_details.html',
                         vehicle=vehicle,
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
    # بيانات مؤقتة للسيارات
    vehicles = [
        {
            'id': 1,
            'name': 'تويوتا كامري',
            'plate_number': 'أ ب ج ١٢٣٤',
        },
        {
            'id': 2,
            'name': 'هونداي سوناتا',
            'plate_number': 'س ع د ٥٦٧٨',
        }
    ]
    
    # بيانات مؤقتة لسجلات الصيانة
    maintenance_records = [
        {
            'id': 1,
            'date': datetime.now().date() - timedelta(days=30),
            'maintenance_type': 'دورية',
            'description': 'تغيير زيت وفلتر',
            'cost': 500.00,
            'vehicle': {'id': 1, 'name': 'تويوتا كامري', 'plate_number': 'أ ب ج ١٢٣٤'}
        },
        {
            'id': 2,
            'date': datetime.now().date() - timedelta(days=90),
            'maintenance_type': 'إصلاح',
            'description': 'إصلاح نظام التكييف',
            'cost': 1200.00,
            'vehicle': {'id': 1, 'name': 'تويوتا كامري', 'plate_number': 'أ ب ج ١٢٣٤'}
        },
        {
            'id': 3,
            'date': datetime.now().date() - timedelta(days=15),
            'maintenance_type': 'طارئة',
            'description': 'تغيير بطارية',
            'cost': 850.00,
            'vehicle': {'id': 2, 'name': 'هونداي سوناتا', 'plate_number': 'س ع د ٥٦٧٨'}
        }
    ]
    
    # ملخص تكاليف الصيانة
    cost_summary = {
        'total': sum(record['cost'] for record in maintenance_records),
        'periodic': sum(record['cost'] for record in maintenance_records if record['maintenance_type'] == 'دورية'),
        'emergency': sum(record['cost'] for record in maintenance_records if record['maintenance_type'] == 'طارئة'),
        'repair': sum(record['cost'] for record in maintenance_records if record['maintenance_type'] == 'إصلاح'),
        'other': sum(record['cost'] for record in maintenance_records if record['maintenance_type'] not in ['دورية', 'طارئة', 'إصلاح'])
    }
    
    return render_template('mobile/vehicle_maintenance.html',
                         vehicles=vehicles,
                         maintenance_records=maintenance_records,
                         cost_summary=cost_summary)

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

# صفحة الرسوم والتكاليف - النسخة المحمولة
@mobile_bp.route('/fees')
@login_required
def fees():
    """صفحة الرسوم والتكاليف للنسخة المحمولة"""
    # بيانات مؤقتة
    fees = []
    fees_summary = {
        'pending_fees': 0,
        'paid_fees': 0,
        'total_fees': 0
    }
    return render_template('mobile/fees.html', fees=fees, fees_summary=fees_summary)

# إضافة رسم جديد - النسخة المحمولة
@mobile_bp.route('/fees/add', methods=['GET', 'POST'])
@login_required
def add_fee():
    """إضافة رسم جديد للنسخة المحمولة"""
    # يمكن تنفيذ هذه الوظيفة لاحقًا
    return render_template('mobile/add_fee.html')

# تفاصيل الرسم - النسخة المحمولة 
@mobile_bp.route('/fees/<int:fee_id>')
@login_required
def fee_details(fee_id):
    """تفاصيل الرسم للنسخة المحمولة"""
    # يمكن تنفيذ هذه الوظيفة لاحقًا
    return render_template('mobile/fee_details.html')

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