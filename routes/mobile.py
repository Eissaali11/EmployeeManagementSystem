"""
مسارات ومعالجات الواجهة المحمولة
نظام إدارة الموظفين - النسخة المحمولة
"""

from datetime import datetime
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
                            absences=absences)

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
    return render_template('mobile/employee_details.html', employee=employee)

# صفحة الحضور والغياب - النسخة المحمولة
@mobile_bp.route('/attendance')
@login_required
def attendance():
    """صفحة الحضور والغياب للنسخة المحمولة"""
    # يمكننا استكمال هذه الواجهة لاحقًا
    return render_template('mobile/attendance.html')

# صفحة الأقسام - النسخة المحمولة
@mobile_bp.route('/departments')
@login_required
def departments():
    """صفحة الأقسام للنسخة المحمولة"""
    # يمكننا استكمال هذه الواجهة لاحقًا
    return render_template('mobile/departments.html')

# صفحة الرواتب - النسخة المحمولة
@mobile_bp.route('/salaries')
@login_required
def salaries():
    """صفحة الرواتب للنسخة المحمولة"""
    # يمكننا استكمال هذه الواجهة لاحقًا
    return render_template('mobile/salaries.html')

# صفحة الوثائق - النسخة المحمولة
@mobile_bp.route('/documents')
@login_required
def documents():
    """صفحة الوثائق للنسخة المحمولة"""
    # يمكننا استكمال هذه الواجهة لاحقًا
    return render_template('mobile/documents.html')

# صفحة التقارير - النسخة المحمولة
@mobile_bp.route('/reports')
@login_required
def reports():
    """صفحة التقارير للنسخة المحمولة"""
    # يمكننا استكمال هذه الواجهة لاحقًا
    return render_template('mobile/reports.html')

# صفحة السيارات - النسخة المحمولة
@mobile_bp.route('/vehicles')
@login_required
def vehicles():
    """صفحة السيارات للنسخة المحمولة"""
    # يمكننا استكمال هذه الواجهة لاحقًا
    return render_template('mobile/vehicles.html')

# صفحة الرسوم والتكاليف - النسخة المحمولة
@mobile_bp.route('/fees')
@login_required
def fees():
    """صفحة الرسوم والتكاليف للنسخة المحمولة"""
    # يمكننا استكمال هذه الواجهة لاحقًا
    return render_template('mobile/fees.html')

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
    # يمكننا استكمال هذه الواجهة لاحقًا
    return render_template('mobile/settings.html')

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