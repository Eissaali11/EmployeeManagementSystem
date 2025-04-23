from flask import Blueprint, render_template, jsonify, redirect, url_for, flash
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from flask_login import login_required, current_user
from models import Employee, Department, Attendance, Document, Salary, Module, UserRole
from app import db
from utils.decorators import module_access_required

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
@module_access_required(Module.DASHBOARD)
def index():
    """Main dashboard with overview of system statistics"""
    # Get basic statistics
    total_employees = Employee.query.filter_by(status='active').count()
    total_departments = Department.query.count()
    
    # Get current date and time for calculations
    now = datetime.now()
    today = now.date()
    
    # Get attendance for today
    today_attendance = Attendance.query.filter_by(date=today).count()
    
    # Get documents statistics
    all_documents = Document.query.all()
    total_documents = len(all_documents)
    
    # Calculate document expiry statistics
    valid_documents = 0
    expired_documents = 0
    expiring_documents = 0
    
    for doc in all_documents:
        days_remaining = (doc.expiry_date - today).days
        if days_remaining < 0:
            expired_documents += 1
        elif days_remaining <= 30:
            expiring_documents += 1
        else:
            valid_documents += 1
    
    # Document statistics for template
    document_stats = {
        'total': total_documents,
        'valid': valid_documents,
        'expired': expired_documents,
        'expiring': expiring_documents
    }
    
    # Get department statistics
    departments = db.session.query(
        Department.name,
        func.count(Employee.id).label('employee_count')
    ).outerjoin(
        Employee, Department.id == Employee.department_id
    ).group_by(Department.id).all()
    
    # Get recent activity
    recent_employees = Employee.query.order_by(Employee.created_at.desc()).limit(5).all()
    
    # Get monthly salary totals for the current year
    current_year = now.year
    monthly_salaries = db.session.query(
        Salary.month,
        func.sum(Salary.net_salary).label('total')
    ).filter(
        Salary.year == current_year
    ).group_by(Salary.month).all()
    
    # Format data for charts
    dept_labels = [dept.name for dept in departments]
    dept_data = [count for _, count in departments]
    
    # If no departments, add default data to avoid empty chart error
    if not dept_labels:
        dept_labels = ["لا يوجد أقسام"]
        dept_data = [0]
    
    salary_labels = [f"شهر {month}" for month, _ in monthly_salaries]
    salary_data = [float(total) for _, total in monthly_salaries]
    
    # If no salary data, add default data to avoid empty chart error
    if not salary_labels:
        salary_labels = ["لا يوجد بيانات"]
        salary_data = [0]
    
    return render_template('dashboard.html',
                          now=now,
                          total_employees=total_employees,
                          total_departments=total_departments,
                          today_attendance=today_attendance,
                          document_stats=document_stats,
                          expiring_documents=expiring_documents,
                          recent_employees=recent_employees,
                          dept_labels=dept_labels,
                          dept_data=dept_data,
                          salary_labels=salary_labels,
                          salary_data=salary_data)

@dashboard_bp.route('/employee-stats')
@login_required
@module_access_required(Module.DASHBOARD)
def employee_stats():
    """عرض إحصائيات الموظفين حسب القسم والحالة"""
    # إحصائيات الموظفين حسب القسم
    department_stats = db.session.query(
        Department.id,
        Department.name,
        func.count(Employee.id).label('employee_count')
    ).outerjoin(
        Employee, Department.id == Employee.department_id
    ).group_by(Department.id).order_by(func.count(Employee.id).desc()).all()
    
    # إحصائيات الموظفين حسب الحالة
    status_stats = db.session.query(
        Employee.status,
        func.count(Employee.id).label('count')
    ).group_by(Employee.status).all()
    
    # ترجمة حالات الموظفين
    status_map = {
        'active': 'نشط',
        'inactive': 'غير نشط',
        'on_leave': 'في إجازة'
    }
    
    status_data = [
        {'status': status_map.get(stat.status, stat.status), 'count': stat.count}
        for stat in status_stats
    ]
    
    # إحصائيات الموظفين حسب القسم والحالة
    detailed_stats = []
    
    for dept in Department.query.all():
        dept_stats = {
            'department_id': dept.id,
            'department_name': dept.name,
            'active': Employee.query.filter_by(department_id=dept.id, status='active').count(),
            'inactive': Employee.query.filter_by(department_id=dept.id, status='inactive').count(),
            'on_leave': Employee.query.filter_by(department_id=dept.id, status='on_leave').count(),
            'total': Employee.query.filter_by(department_id=dept.id).count(),
        }
        detailed_stats.append(dept_stats)
    
    # ترتيب الإحصائيات حسب العدد الإجمالي للموظفين
    detailed_stats.sort(key=lambda x: x['total'], reverse=True)
    
    return render_template('employee_stats.html',
                           department_stats=department_stats,
                           status_stats=status_data,
                           detailed_stats=detailed_stats)

@dashboard_bp.route('/api/department-employee-stats')
@login_required
@module_access_required(Module.DASHBOARD)
def department_employee_stats_api():
    """واجهة برمجة لإحصائيات الموظفين حسب القسم للرسوم البيانية"""
    # إحصائيات الموظفين حسب القسم
    department_stats = db.session.query(
        Department.id,
        Department.name,
        func.count(Employee.id).label('employee_count')
    ).outerjoin(
        Employee, Department.id == Employee.department_id
    ).group_by(Department.id).order_by(func.count(Employee.id).desc()).all()
    
    # قائمة بالألوان الجميلة المتناسقة للمخطط
    gradient_colors = [
        ['rgba(24, 144, 255, 0.85)', 'rgba(24, 144, 255, 0.4)'],    # أزرق
        ['rgba(47, 194, 91, 0.85)', 'rgba(47, 194, 91, 0.4)'],      # أخضر
        ['rgba(250, 173, 20, 0.85)', 'rgba(250, 173, 20, 0.4)'],    # برتقالي
        ['rgba(245, 34, 45, 0.85)', 'rgba(245, 34, 45, 0.4)'],      # أحمر
        ['rgba(114, 46, 209, 0.85)', 'rgba(114, 46, 209, 0.4)'],    # بنفسجي
        ['rgba(19, 194, 194, 0.85)', 'rgba(19, 194, 194, 0.4)'],    # فيروزي
        ['rgba(82, 196, 26, 0.85)', 'rgba(82, 196, 26, 0.4)'],      # أخضر فاتح
        ['rgba(144, 19, 254, 0.85)', 'rgba(144, 19, 254, 0.4)'],    # أرجواني
        ['rgba(240, 72, 68, 0.85)', 'rgba(240, 72, 68, 0.4)'],      # أحمر فاتح
        ['rgba(250, 140, 22, 0.85)', 'rgba(250, 140, 22, 0.4)'],    # برتقالي داكن
    ]
    
    # تحضير البيانات للرسم البياني مع معلومات إضافية
    labels = []
    data = []
    background_colors = []
    hover_colors = []
    department_ids = []
    
    # إذا لم تكن هناك أقسام
    if not department_stats:
        return jsonify({
            'labels': ['لا توجد أقسام'],
            'data': [0],
            'backgroundColor': ['rgba(200, 200, 200, 0.6)'],
            'hoverBackgroundColor': ['rgba(200, 200, 200, 0.8)'],
            'departmentIds': [0],
            'percentages': [100],
            'total': 0
        })
    
    total_employees = sum(stat.employee_count for stat in department_stats)
    percentages = []
    
    for idx, stat in enumerate(department_stats):
        labels.append(stat.name)
        data.append(stat.employee_count)
        color_idx = idx % len(gradient_colors)
        background_colors.append(gradient_colors[color_idx][1])
        hover_colors.append(gradient_colors[color_idx][0])
        department_ids.append(stat.id)
        
        # حساب النسبة المئوية
        percentage = round((stat.employee_count / total_employees * 100), 1) if total_employees > 0 else 0
        percentages.append(percentage)
    
    # تنسيق البيانات للرسم البياني
    dept_data = {
        'labels': labels,
        'data': data,
        'backgroundColor': background_colors,
        'hoverBackgroundColor': hover_colors,
        'departmentIds': department_ids,
        'percentages': percentages,
        'total': total_employees
    }
    
    return jsonify(dept_data)
