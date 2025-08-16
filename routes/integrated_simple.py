"""
نظام الإدارة المتكامل المبسط - نسخة مستقرة
Simple Integrated Management System - Stable Version
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from sqlalchemy import extract, func, desc, and_, or_
from datetime import datetime, date, timedelta
import calendar
from decimal import Decimal

from app import db
from models import Employee, Department, Vehicle, Attendance, Salary, User

integrated_bp = Blueprint('integrated', __name__)

# ============ لوحة التحكم الرئيسية المتكاملة ============

@integrated_bp.route('/dashboard')
@login_required
def dashboard():
    """لوحة التحكم الشاملة للنظام المتكامل"""
    
    # الحصول على التاريخ الحالي
    today = date.today()
    current_month = today.month
    current_year = today.year
    
    # === إحصائيات الموظفين والأقسام ===
    total_employees = Employee.query.filter_by(status='active').count()
    total_departments = Department.query.count()
    
    # === إحصائيات السيارات ===
    total_vehicles = Vehicle.query.count()
    vehicles_available = Vehicle.query.filter_by(status='available').count()
    vehicles_rented = Vehicle.query.filter_by(status='rented').count()
    vehicles_in_workshop = Vehicle.query.filter_by(status='in_workshop').count()
    
    # === إحصائيات الرواتب لهذا الشهر ===
    salaries_this_month = Salary.query.filter_by(
        month=current_month,
        year=current_year
    ).all()
    
    total_payroll = sum(salary.net_salary for salary in salaries_this_month)
    paid_salaries = len([s for s in salaries_this_month if s.is_paid])
    unpaid_salaries = len([s for s in salaries_this_month if not s.is_paid])
    
    # === إحصائيات السيارات المالية ===
    total_rental_cost = 0  # مبسط للاستقرار
    
    # === بيانات الرسوم البيانية ===
    # رسم بياني لحالة السيارات
    vehicle_status_data = {
        'available': vehicles_available,
        'rented': vehicles_rented,
        'in_workshop': vehicles_in_workshop,
        'other': max(0, total_vehicles - vehicles_available - vehicles_rented - vehicles_in_workshop)
    }
    
    # رسم بياني للحضور في آخر 7 أيام
    last_7_days = []
    attendance_7_days = []
    
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        last_7_days.append(day.strftime('%d/%m'))
        
        daily_attendance = Attendance.query.filter(
            Attendance.date == day,
            Attendance.status == 'present'
        ).count()
        attendance_7_days.append(daily_attendance)
    
    # === قائمة بالمهام العاجلة ===
    urgent_tasks = []
    
    # وثائق السيارات المنتهية
    expired_vehicles = Vehicle.query.filter(
        or_(
            Vehicle.registration_expiry_date < today,
            Vehicle.inspection_expiry_date < today,
            Vehicle.authorization_expiry_date < today
        )
    ).count()
    
    if expired_vehicles > 0:
        urgent_tasks.append({
            'title': f'{expired_vehicles} سيارة لديها وثائق منتهية',
            'url': url_for('vehicles.index'),
            'type': 'danger'
        })
    
    # رواتب لم يتم دفعها
    if unpaid_salaries > 0:
        urgent_tasks.append({
            'title': f'{unpaid_salaries} راتب في انتظار الدفع',
            'url': url_for('salaries.index'),
            'type': 'warning'
        })
    
    return render_template('integrated/dashboard_fixed.html',
        # إحصائيات عامة
        total_employees=total_employees,
        total_departments=total_departments,
        total_vehicles=total_vehicles,
        vehicles_available=vehicles_available,
        vehicles_rented=vehicles_rented,
        vehicles_in_workshop=vehicles_in_workshop,
        
        # إحصائيات مالية
        total_payroll=total_payroll,
        total_rental_cost=total_rental_cost,
        paid_salaries=paid_salaries,
        unpaid_salaries=unpaid_salaries,
        
        # بيانات الرسوم البيانية
        vehicle_status_data=vehicle_status_data,
        last_7_days=last_7_days,
        attendance_7_days=attendance_7_days,
        
        # مهام عاجلة
        urgent_tasks=urgent_tasks,
        
        # معلومات عامة
        current_month=current_month,
        current_year=current_year,
        today=today
    )

# ============ نظام الربط المحاسبي التلقائي ============

@integrated_bp.route('/auto-accounting')
@login_required
def auto_accounting():
    """صفحة إعداد الربط المحاسبي التلقائي"""
    
    return render_template('integrated/auto_accounting_simple.html',
        current_month=datetime.now().month,
        current_year=datetime.now().year
    )

# ============ التقرير الشامل ============

@integrated_bp.route('/comprehensive-report')
@login_required
def comprehensive_report():
    """تقرير شامل يجمع كافة البيانات"""
    
    # الحصول على التواريخ
    today = date.today()
    current_month = today.month
    current_year = today.year
    
    # معالجة فلاتر التاريخ
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    else:
        start_date = date(current_year, current_month, 1)
    
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    else:
        end_date = today
    
    # === بيانات الموظفين ===
    employees_query = Employee.query.filter_by(status='active')
    
    department_filter = request.args.get('department')
    if department_filter:
        employees_query = employees_query.filter_by(department_id=department_filter)
    
    employees = employees_query.all()
    
    # === بيانات السيارات ===
    vehicles = Vehicle.query.all()
    
    # === بيانات الحضور ===
    attendance_records = Attendance.query.filter(
        Attendance.date.between(start_date, end_date)
    ).all()
    
    # === بيانات الرواتب ===
    salaries = Salary.query.filter(
        Salary.month >= start_date.month,
        Salary.year >= start_date.year,
        Salary.month <= end_date.month,
        Salary.year <= end_date.year
    ).all()
    
    # === إحصائيات موجزة ===
    summary_stats = {
        'total_employees': len(employees),
        'total_vehicles': len(vehicles),
        'total_attendance_records': len(attendance_records),
        'total_salaries': len(salaries),
        'total_payroll': sum(s.net_salary for s in salaries),
        'period_start': start_date,
        'period_end': end_date
    }
    
    # الأقسام للفلتر
    departments = Department.query.all()
    
    return render_template('integrated/comprehensive_report_simple.html',
                         employees=employees,
                         vehicles=vehicles,
                         attendance_records=attendance_records,
                         salaries=salaries,
                         summary_stats=summary_stats,
                         departments=departments,
                         start_date=start_date,
                         end_date=end_date)

# ============ API للإحصائيات ============

@integrated_bp.route('/api/stats')
@login_required
def dashboard_stats_api():
    """API للحصول على الإحصائيات السريعة"""
    
    today = date.today()
    current_month = today.month
    current_year = today.year
    
    stats = {
        'employees': {
            'total': Employee.query.filter_by(status='active').count(),
            'departments': Department.query.count()
        },
        'vehicles': {
            'total': Vehicle.query.count(),
            'available': Vehicle.query.filter_by(status='available').count(),
            'rented': Vehicle.query.filter_by(status='rented').count(),
            'in_workshop': Vehicle.query.filter_by(status='in_workshop').count()
        },
        'attendance': {
            'today': Attendance.query.filter(
                Attendance.date == today,
                Attendance.status == 'present'
            ).count()
        },
        'salaries': {
            'this_month': Salary.query.filter_by(
                month=current_month,
                year=current_year
            ).count(),
            'paid': Salary.query.filter_by(
                month=current_month,
                year=current_year,
                is_paid=True
            ).count()
        },
        'timestamp': datetime.now().isoformat()
    }
    
    return jsonify(stats)