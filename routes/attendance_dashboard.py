"""
وحدة لوحة معلومات الحضور المحسنة
-----------------------------
تعرض إحصائيات الحضور حسب القسم والتاريخ مع إمكانية تصدير البيانات
"""

from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import func
from flask import Blueprint, render_template, request, jsonify, send_file
from flask_login import login_required, current_user
import io
import tempfile
import os

from models import Department, Employee, Attendance, Module
from app import db
from utils.decorators import module_access_required

# إنشاء blueprint للوحة معلومات الحضور
attendance_dashboard_bp = Blueprint('attendance_dashboard', __name__)

@attendance_dashboard_bp.route('/')
@login_required
@module_access_required(Module.ATTENDANCE)
def index():
    """صفحة لوحة معلومات الحضور الرئيسية"""
    # التحقق من التاريخ المحدد أو استخدام اليوم الحالي
    date_str = request.args.get('date')
    department_id = request.args.get('department_id')
    
    try:
        if date_str:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            selected_date = datetime.now().date()
    except ValueError:
        selected_date = datetime.now().date()
    
    # الحصول على جميع الأقسام
    departments = Department.query.order_by(Department.name).all()
    
    # إحصائيات إجمالية
    total_employees = Employee.query.filter_by(status='active').count()
    
    # إحصائيات حسب القسم
    department_stats = []
    
    # جمع إحصائيات كل قسم
    for dept in departments:
        # عدد الموظفين في القسم
        employees_count = Employee.query.filter_by(
            department_id=dept.id, 
            status='active'
        ).count()
        
        # عدد الحاضرين
        present_count = db.session.query(func.count(Attendance.id)).join(
            Employee, Employee.id == Attendance.employee_id
        ).filter(
            Employee.department_id == dept.id,
            Employee.status == 'active',
            Attendance.date == selected_date,
            Attendance.status == 'present'
        ).scalar() or 0
        
        # عدد الغائبين
        absent_count = db.session.query(func.count(Attendance.id)).join(
            Employee, Employee.id == Attendance.employee_id
        ).filter(
            Employee.department_id == dept.id,
            Employee.status == 'active',
            Attendance.date == selected_date,
            Attendance.status == 'absent'
        ).scalar() or 0
        
        # عدد الإجازات
        leave_count = db.session.query(func.count(Attendance.id)).join(
            Employee, Employee.id == Attendance.employee_id
        ).filter(
            Employee.department_id == dept.id,
            Employee.status == 'active',
            Attendance.date == selected_date,
            Attendance.status == 'leave'
        ).scalar() or 0
        
        # عدد المرضي
        sick_count = db.session.query(func.count(Attendance.id)).join(
            Employee, Employee.id == Attendance.employee_id
        ).filter(
            Employee.department_id == dept.id,
            Employee.status == 'active',
            Attendance.date == selected_date,
            Attendance.status == 'sick'
        ).scalar() or 0
        
        # إجمالي السجلات
        total_records = present_count + absent_count + leave_count + sick_count
        
        # حساب نسب الحضور والغياب
        if employees_count > 0:
            present_percentage = round((present_count / employees_count) * 100, 1)
            absent_percentage = round((absent_count / employees_count) * 100, 1)
            missing_count = employees_count - total_records
            missing_percentage = round((missing_count / employees_count) * 100, 1) if missing_count > 0 else 0
        else:
            present_percentage = 0
            absent_percentage = 0
            missing_count = 0
            missing_percentage = 0
        
        # إضافة إحصائيات القسم للقائمة
        department_stats.append({
            'id': dept.id,
            'name': dept.name,
            'employees_count': employees_count,
            'present_count': present_count,
            'absent_count': absent_count,
            'leave_count': leave_count,
            'sick_count': sick_count,
            'missing_count': missing_count,
            'present_percentage': present_percentage,
            'absent_percentage': absent_percentage,
            'missing_percentage': missing_percentage
        })
    
    # الموظفون الغائبون
    absent_employees = []
    
    # إذا تم تحديد قسم معين
    if department_id:
        filter_conditions = [
            Employee.status == 'active',
            Employee.department_id == department_id
        ]
    else:
        filter_conditions = [Employee.status == 'active']
    
    # استعلام الموظفين الغائبين
    absent_records = db.session.query(
        Attendance, Employee, Department
    ).join(
        Employee, Employee.id == Attendance.employee_id
    ).join(
        Department, Department.id == Employee.department_id
    ).filter(
        Attendance.date == selected_date,
        Attendance.status.in_(['absent', 'leave', 'sick']),
        *filter_conditions
    ).all()
    
    # تجهيز بيانات الموظفين الغائبين
    for attendance, employee, department in absent_records:
        absent_employees.append({
            'id': employee.id,
            'name': employee.name,
            'employee_id': employee.employee_id,
            'department': department.name,
            'department_id': department.id,
            'status': attendance.status,
            'notes': attendance.notes
        })
    
    # تجهيز المعلومات حسب القسم
    absent_by_department = {}
    for emp in absent_employees:
        dept_id = emp['department_id']
        if dept_id not in absent_by_department:
            absent_by_department[dept_id] = {
                'name': emp['department'],
                'employees': []
            }
        absent_by_department[dept_id]['employees'].append(emp)
    
    # تقديم الصفحة
    return render_template(
        'attendance/enhanced_dashboard.html',
        selected_date=selected_date,
        departments=departments,
        selected_department_id=int(department_id) if department_id else None,
        total_employees=total_employees,
        department_stats=department_stats,
        absent_employees=absent_employees,
        absent_by_department=absent_by_department
    )

@attendance_dashboard_bp.route('/data')
@login_required
@module_access_required(Module.ATTENDANCE)
def dashboard_data():
    """API لبيانات لوحة المعلومات"""
    date_str = request.args.get('date')
    
    try:
        if date_str:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            selected_date = datetime.now().date()
    except ValueError:
        selected_date = datetime.now().date()
    
    # الحصول على بيانات الإحصائيات
    departments = Department.query.all()
    
    # بيانات للرسم البياني
    department_names = []
    present_counts = []
    absent_counts = []
    leave_counts = []
    sick_counts = []
    missing_counts = []
    
    for dept in departments:
        # إضافة اسم القسم
        department_names.append(dept.name)
        
        # عدد الموظفين في القسم
        employees_count = Employee.query.filter_by(
            department_id=dept.id, 
            status='active'
        ).count()
        
        # عدد الحاضرين
        present_count = db.session.query(func.count(Attendance.id)).join(
            Employee, Employee.id == Attendance.employee_id
        ).filter(
            Employee.department_id == dept.id,
            Employee.status == 'active',
            Attendance.date == selected_date,
            Attendance.status == 'present'
        ).scalar() or 0
        
        # عدد الغائبين
        absent_count = db.session.query(func.count(Attendance.id)).join(
            Employee, Employee.id == Attendance.employee_id
        ).filter(
            Employee.department_id == dept.id,
            Employee.status == 'active',
            Attendance.date == selected_date,
            Attendance.status == 'absent'
        ).scalar() or 0
        
        # عدد الإجازات
        leave_count = db.session.query(func.count(Attendance.id)).join(
            Employee, Employee.id == Attendance.employee_id
        ).filter(
            Employee.department_id == dept.id,
            Employee.status == 'active',
            Attendance.date == selected_date,
            Attendance.status == 'leave'
        ).scalar() or 0
        
        # عدد المرضي
        sick_count = db.session.query(func.count(Attendance.id)).join(
            Employee, Employee.id == Attendance.employee_id
        ).filter(
            Employee.department_id == dept.id,
            Employee.status == 'active',
            Attendance.date == selected_date,
            Attendance.status == 'sick'
        ).scalar() or 0
        
        # إجمالي السجلات
        total_records = present_count + absent_count + leave_count + sick_count
        
        # حساب عدد الموظفين بدون تسجيل
        missing_count = employees_count - total_records
        if missing_count < 0:
            missing_count = 0
        
        # إضافة الإحصائيات للقوائم
        present_counts.append(present_count)
        absent_counts.append(absent_count)
        leave_counts.append(leave_count)
        sick_counts.append(sick_count)
        missing_counts.append(missing_count)
    
    # تجهيز البيانات للرسم البياني
    chart_data = {
        'labels': department_names,
        'datasets': [
            {
                'label': 'حاضر',
                'data': present_counts,
                'backgroundColor': 'rgba(40, 167, 69, 0.7)',
                'borderColor': 'rgb(40, 167, 69)',
                'borderWidth': 1
            },
            {
                'label': 'غائب',
                'data': absent_counts,
                'backgroundColor': 'rgba(220, 53, 69, 0.7)',
                'borderColor': 'rgb(220, 53, 69)',
                'borderWidth': 1
            },
            {
                'label': 'إجازة',
                'data': leave_counts,
                'backgroundColor': 'rgba(255, 193, 7, 0.7)',
                'borderColor': 'rgb(255, 193, 7)',
                'borderWidth': 1
            },
            {
                'label': 'مرضي',
                'data': sick_counts,
                'backgroundColor': 'rgba(23, 162, 184, 0.7)',
                'borderColor': 'rgb(23, 162, 184)',
                'borderWidth': 1
            },
            {
                'label': 'غير مسجل',
                'data': missing_counts,
                'backgroundColor': 'rgba(108, 117, 125, 0.7)',
                'borderColor': 'rgb(108, 117, 125)',
                'borderWidth': 1
            }
        ]
    }
    
    return jsonify(chart_data)

@attendance_dashboard_bp.route('/export-excel')
@login_required
@module_access_required(Module.ATTENDANCE)
def export_excel():
    """تصدير بيانات الحضور لملف إكسل"""
    date_str = request.args.get('date')
    department_id = request.args.get('department_id')
    
    try:
        if date_str:
            selected_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            selected_date = datetime.now().date()
    except ValueError:
        selected_date = datetime.now().date()
    
    # بناء استعلام البيانات
    query = db.session.query(
        Employee.name.label('اسم الموظف'),
        Employee.employee_id.label('الرقم الوظيفي'),
        Department.name.label('القسم'),
        Attendance.status.label('الحالة'),
        Attendance.check_in.label('وقت الحضور'),
        Attendance.check_out.label('وقت الانصراف'),
        Attendance.notes.label('ملاحظات')
    ).join(
        Employee, Employee.id == Attendance.employee_id
    ).join(
        Department, Department.id == Employee.department_id
    ).filter(
        Attendance.date == selected_date
    )
    
    # إضافة فلتر القسم إذا تم تحديده
    if department_id:
        query = query.filter(Department.id == department_id)
    
    # تنفيذ الاستعلام
    results = query.all()
    
    # إنشاء DataFrame من النتائج
    df = pd.DataFrame(results)
    
    # معالجة الحالة
    def format_status(status):
        if status == 'present':
            return 'حاضر'
        elif status == 'absent':
            return 'غائب'
        elif status == 'leave':
            return 'إجازة'
        elif status == 'sick':
            return 'مرضي'
        else:
            return status
    
    if 'الحالة' in df.columns:
        df['الحالة'] = df['الحالة'].apply(format_status)
    
    # معالجة أوقات الحضور والانصراف
    for col in ['وقت الحضور', 'وقت الانصراف']:
        if col in df.columns:
            df[col] = df[col].apply(lambda x: x.strftime('%H:%M') if x else '-')
    
    # تحديد اسم الملف
    date_str = selected_date.strftime('%Y-%m-%d')
    filename = f"attendance_report_{date_str}.xlsx"
    
    # إنشاء ملف مؤقت
    with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
        # حفظ البيانات إلى الملف
        with pd.ExcelWriter(temp_file.name, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='تقرير الحضور')
        
        # إرسال الملف كملف للتحميل
        return send_file(
            temp_file.name,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )