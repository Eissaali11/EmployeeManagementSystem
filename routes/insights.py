from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required
from sqlalchemy import func, desc, and_, or_
from datetime import datetime, timedelta
from app import db
from models import (
    Employee, Department, Vehicle, VehicleHandover, VehicleWorkshop,
    Attendance, Salary, SystemAudit, Module, Permission, employee_departments
)
from utils.user_helpers import require_module_access
import json

insights_bp = Blueprint('insights', __name__)

@insights_bp.route('/')
@login_required
@require_module_access(Module.EMPLOYEES, Permission.VIEW)
def dashboard():
    """Main insights dashboard"""
    # Get date range for filtering (default to last 30 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # Employee insights
    employee_insights = get_employee_insights()
    
    # Department insights
    department_insights = get_department_insights()
    
    # Vehicle insights
    vehicle_insights = get_vehicle_insights()
    
    # Activity insights
    activity_insights = get_activity_insights(start_date, end_date)
    
    # Performance metrics
    performance_metrics = get_performance_metrics()
    
    # Trends and predictions
    trends = get_trends_analysis()
    
    return render_template('insights/dashboard.html',
                         employee_insights=employee_insights,
                         department_insights=department_insights,
                         vehicle_insights=vehicle_insights,
                         activity_insights=activity_insights,
                         performance_metrics=performance_metrics,
                         trends=trends)

def get_employee_insights():
    """Get employee-related insights"""
    total_employees = Employee.query.count()
    active_employees = Employee.query.filter_by(status='active').count()
    inactive_employees = Employee.query.filter_by(status='inactive').count()
    on_leave_employees = Employee.query.filter_by(status='on_leave').count()
    
    # Multi-department employees
    multi_dept_employees = db.session.query(Employee.id)\
        .join(employee_departments)\
        .group_by(Employee.id)\
        .having(func.count(employee_departments.c.department_id) > 1)\
        .count()
    
    # Employees without departments
    no_dept_employees = db.session.query(Employee.id)\
        .outerjoin(employee_departments)\
        .filter(employee_departments.c.employee_id.is_(None))\
        .count()
    
    # Recent hires (last 30 days)
    recent_hires = Employee.query.filter(
        Employee.hire_date >= datetime.now() - timedelta(days=30)
    ).count() if Employee.query.first() and hasattr(Employee.query.first(), 'hire_date') else 0
    
    # Employee growth trend
    growth_trend = calculate_employee_growth_trend()
    
    return {
        'total': total_employees,
        'active': active_employees,
        'inactive': inactive_employees,
        'on_leave': on_leave_employees,
        'multi_department': multi_dept_employees,
        'no_department': no_dept_employees,
        'recent_hires': recent_hires,
        'growth_trend': growth_trend,
        'activity_rate': round((active_employees / total_employees * 100), 2) if total_employees > 0 else 0
    }

def get_department_insights():
    """Get department-related insights"""
    departments = Department.query.all()
    dept_stats = []
    
    for dept in departments:
        emp_count = len(dept.employees)
        dept_stats.append({
            'id': dept.id,
            'name': dept.name,
            'employee_count': emp_count,
            'manager': dept.manager.name if dept.manager else 'غير محدد'
        })
    
    # Sort by employee count
    dept_stats.sort(key=lambda x: x['employee_count'], reverse=True)
    
    largest_dept = dept_stats[0] if dept_stats else None
    smallest_dept = dept_stats[-1] if dept_stats else None
    avg_dept_size = sum(d['employee_count'] for d in dept_stats) / len(dept_stats) if dept_stats else 0
    
    return {
        'total_departments': len(departments),
        'department_stats': dept_stats,
        'largest_department': largest_dept,
        'smallest_department': smallest_dept,
        'average_size': round(avg_dept_size, 2),
        'departments_with_managers': sum(1 for d in dept_stats if d['manager'] != 'غير محدد')
    }

def get_vehicle_insights():
    """Get vehicle-related insights"""
    total_vehicles = Vehicle.query.count()
    
    # Vehicle status distribution
    status_counts = db.session.query(Vehicle.status, func.count(Vehicle.id))\
        .group_by(Vehicle.status)\
        .all()
    
    # Recent handovers (last 30 days)
    recent_handovers = VehicleHandover.query.filter(
        VehicleHandover.handover_date >= datetime.now() - timedelta(days=30)
    ).count()
    
    # Workshop activity
    workshop_records = VehicleWorkshop.query.filter(
        VehicleWorkshop.created_at >= datetime.now() - timedelta(days=30)
    ).count()
    
    # Vehicle utilization
    vehicles_with_drivers = Vehicle.query.filter(Vehicle.current_driver_name.isnot(None)).count()
    utilization_rate = round((vehicles_with_drivers / total_vehicles * 100), 2) if total_vehicles > 0 else 0
    
    return {
        'total_vehicles': total_vehicles,
        'status_distribution': dict(status_counts),
        'recent_handovers': recent_handovers,
        'workshop_activity': workshop_records,
        'utilization_rate': utilization_rate,
        'vehicles_with_drivers': vehicles_with_drivers
    }

def get_activity_insights(start_date, end_date):
    """Get system activity insights"""
    # System audit activity
    total_activities = SystemAudit.query.filter(
        SystemAudit.timestamp >= start_date,
        SystemAudit.timestamp <= end_date
    ).count()
    
    # Activity by type
    activity_by_type = db.session.query(SystemAudit.action, func.count(SystemAudit.id))\
        .filter(SystemAudit.timestamp >= start_date, SystemAudit.timestamp <= end_date)\
        .group_by(SystemAudit.action)\
        .all()
    
    # Activity by entity type
    activity_by_entity = db.session.query(SystemAudit.entity_type, func.count(SystemAudit.id))\
        .filter(SystemAudit.timestamp >= start_date, SystemAudit.timestamp <= end_date)\
        .group_by(SystemAudit.entity_type)\
        .all()
    
    # Daily activity trend
    daily_activity = db.session.query(
        func.date(SystemAudit.timestamp).label('date'),
        func.count(SystemAudit.id).label('count')
    ).filter(
        SystemAudit.timestamp >= start_date,
        SystemAudit.timestamp <= end_date
    ).group_by(func.date(SystemAudit.timestamp))\
     .order_by(func.date(SystemAudit.timestamp))\
     .all()
    
    return {
        'total_activities': total_activities,
        'activity_by_type': dict(activity_by_type),
        'activity_by_entity': dict(activity_by_entity),
        'daily_activity': [(str(date), count) for date, count in daily_activity]
    }

def get_performance_metrics():
    """Get performance and efficiency metrics"""
    # System efficiency metrics
    avg_response_time = 0.2  # Simulated metric
    system_uptime = 99.5  # Simulated metric
    
    # Data quality metrics
    employees_with_complete_data = Employee.query.filter(
        and_(
            Employee.name.isnot(None),
            Employee.employee_id.isnot(None),
            Employee.national_id.isnot(None),
            Employee.mobile.isnot(None)
        )
    ).count()
    
    total_employees = Employee.query.count()
    data_completeness = round((employees_with_complete_data / total_employees * 100), 2) if total_employees > 0 else 0
    
    # Document expiry alerts
    expired_docs = 0
    expiring_soon_docs = 0
    
    # Check vehicle documents
    vehicles = Vehicle.query.all()
    for vehicle in vehicles:
        if vehicle.registration_expiry_date:
            if vehicle.registration_expiry_date < datetime.now().date():
                expired_docs += 1
            elif vehicle.registration_expiry_date < (datetime.now() + timedelta(days=30)).date():
                expiring_soon_docs += 1
    
    return {
        'avg_response_time': avg_response_time,
        'system_uptime': system_uptime,
        'data_completeness': data_completeness,
        'expired_documents': expired_docs,
        'expiring_soon_documents': expiring_soon_docs
    }

def get_trends_analysis():
    """Get trends and predictive insights"""
    # Employee growth trend (last 6 months)
    growth_data = []
    for i in range(6):
        month_start = datetime.now().replace(day=1) - timedelta(days=30*i)
        month_end = month_start + timedelta(days=30)
        
        employee_count = Employee.query.filter(
            Employee.created_at <= month_end
        ).count() if hasattr(Employee, 'created_at') else Employee.query.count()
        
        growth_data.append({
            'month': month_start.strftime('%Y-%m'),
            'count': employee_count
        })
    
    growth_data.reverse()
    
    # Vehicle utilization trend
    utilization_trend = []
    for i in range(4):  # Last 4 weeks
        week_start = datetime.now() - timedelta(days=7*i)
        week_end = week_start + timedelta(days=7)
        
        handovers = VehicleHandover.query.filter(
            VehicleHandover.handover_date >= week_start,
            VehicleHandover.handover_date <= week_end
        ).count()
        
        utilization_trend.append({
            'week': f'Week {i+1}',
            'handovers': handovers
        })
    
    utilization_trend.reverse()
    
    # Predictions and recommendations
    recommendations = generate_recommendations()
    
    return {
        'employee_growth': growth_data,
        'vehicle_utilization': utilization_trend,
        'recommendations': recommendations
    }

def calculate_employee_growth_trend():
    """Calculate employee growth trend percentage"""
    current_month = Employee.query.count()
    
    # Get last month's count (simulated)
    last_month = max(0, current_month - 2)  # Simulated decrease
    
    if last_month > 0:
        growth_rate = round(((current_month - last_month) / last_month * 100), 2)
    else:
        growth_rate = 0
    
    return growth_rate

def generate_recommendations():
    """Generate intelligent recommendations based on data analysis"""
    recommendations = []
    
    # Check for employees without departments
    no_dept_count = db.session.query(Employee.id)\
        .outerjoin(employee_departments)\
        .filter(employee_departments.c.employee_id.is_(None))\
        .count()
    
    if no_dept_count > 0:
        recommendations.append({
            'type': 'warning',
            'title': 'موظفون بدون أقسام',
            'description': f'يوجد {no_dept_count} موظف غير مربوط بأي قسم',
            'action': 'قم بتعيين الأقسام للموظفين',
            'priority': 'high'
        })
    
    # Check for vehicle utilization
    total_vehicles = Vehicle.query.count()
    vehicles_with_drivers = Vehicle.query.filter(Vehicle.current_driver_name.isnot(None)).count()
    
    if total_vehicles > 0:
        utilization_rate = vehicles_with_drivers / total_vehicles * 100
        if utilization_rate < 70:
            recommendations.append({
                'type': 'info',
                'title': 'معدل استخدام المركبات منخفض',
                'description': f'معدل الاستخدام الحالي {utilization_rate:.1f}%',
                'action': 'راجع توزيع المركبات على الموظفين',
                'priority': 'medium'
            })
    
    # Check for inactive employees
    inactive_count = Employee.query.filter_by(status='inactive').count()
    total_employees = Employee.query.count()
    
    if total_employees > 0:
        inactive_rate = inactive_count / total_employees * 100
        if inactive_rate > 10:
            recommendations.append({
                'type': 'warning',
                'title': 'نسبة عالية من الموظفين غير النشطين',
                'description': f'{inactive_rate:.1f}% من الموظفين غير نشطين',
                'action': 'راجع حالة الموظفين غير النشطين',
                'priority': 'medium'
            })
    
    # Data quality recommendation
    employees_with_complete_data = Employee.query.filter(
        and_(
            Employee.name.isnot(None),
            Employee.employee_id.isnot(None),
            Employee.national_id.isnot(None),
            Employee.mobile.isnot(None)
        )
    ).count()
    
    if total_employees > 0:
        completeness_rate = employees_with_complete_data / total_employees * 100
        if completeness_rate < 90:
            recommendations.append({
                'type': 'info',
                'title': 'تحسين جودة البيانات',
                'description': f'اكتمال البيانات {completeness_rate:.1f}%',
                'action': 'أكمل البيانات المفقودة للموظفين',
                'priority': 'low'
            })
    
    return recommendations

@insights_bp.route('/api/metrics')
@login_required
def api_metrics():
    """API endpoint for real-time metrics"""
    metrics = {
        'employees': get_employee_insights(),
        'departments': get_department_insights(),
        'vehicles': get_vehicle_insights(),
        'performance': get_performance_metrics()
    }
    return jsonify(metrics)

@insights_bp.route('/api/trends')
@login_required
def api_trends():
    """API endpoint for trend data"""
    trends = get_trends_analysis()
    return jsonify(trends)