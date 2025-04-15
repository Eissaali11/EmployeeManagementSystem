from flask import Blueprint, render_template
from sqlalchemy import func
from datetime import datetime, timedelta
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
    
    salary_labels = [f"شهر {month}" for month, _ in monthly_salaries]
    salary_data = [float(total) for _, total in monthly_salaries]
    
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
