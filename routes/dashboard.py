from flask import Blueprint, render_template, jsonify, redirect, url_for
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from flask_login import login_required, current_user
from models import Employee, Department, Attendance, Document, Salary
from app import db

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def index():
    """Main dashboard with overview of system statistics"""
    # Get basic statistics
    total_employees = Employee.query.filter_by(status='active').count()
    total_departments = Department.query.count()
    
    # Get attendance for today
    today = datetime.now().date()
    today_attendance = Attendance.query.filter_by(date=today).count()
    
    # Get documents expiring in the next 30 days
    expiry_date = today + timedelta(days=30)
    expiring_documents = Document.query.filter(Document.expiry_date <= expiry_date, 
                                              Document.expiry_date >= today).count()
    
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
    current_year = datetime.now().year
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
                          total_employees=total_employees,
                          total_departments=total_departments,
                          today_attendance=today_attendance,
                          expiring_documents=expiring_documents,
                          recent_employees=recent_employees,
                          dept_labels=dept_labels,
                          dept_data=dept_data,
                          salary_labels=salary_labels,
                          salary_data=salary_data)

@dashboard_bp.route('/employee-stats')
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
def department_employee_stats_api():
    """واجهة برمجة لإحصائيات الموظفين حسب القسم للرسوم البيانية"""
    # إحصائيات الموظفين حسب القسم
    department_stats = db.session.query(
        Department.name,
        func.count(Employee.id).label('employee_count')
    ).outerjoin(
        Employee, Department.id == Employee.department_id
    ).group_by(Department.id).order_by(func.count(Employee.id).desc()).all()
    
    # تنسيق البيانات للرسم البياني
    dept_data = {
        'labels': [stat.name for stat in department_stats],
        'data': [stat.employee_count for stat in department_stats],
        'colors': [
            'rgba(75, 192, 192, 0.8)',
            'rgba(54, 162, 235, 0.8)',
            'rgba(153, 102, 255, 0.8)',
            'rgba(255, 159, 64, 0.8)',
            'rgba(255, 99, 132, 0.8)',
            'rgba(255, 206, 86, 0.8)',
        ]
    }
    
    return jsonify(dept_data)
