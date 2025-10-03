"""
وحدة التسجيل الجماعي للحضور
--------------------------
هذا الملف يحتوي على مسارات خاصة بتسجيل الحضور الجماعي للأقسام
"""

from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, flash

from app import db
from models import Department, Employee, Attendance, SystemAudit

# تعريف Blueprint للحضور الجماعي
mass_attendance_bp = Blueprint('mass', __name__)

@mass_attendance_bp.route('/departments', methods=['GET', 'POST'])
def departments():
    """صفحة تسجيل الحضور لجميع الأقسام"""
    # التاريخ الافتراضي هو اليوم
    today = datetime.now().date()
    
    # إعداد النموذج
    form = {}
    error = None
    
    if request.method == 'POST':
        try:
            # الحصول على البيانات من النموذج
            department_ids = request.form.getlist('department_ids')
            start_date_str = request.form.get('start_date', '')
            end_date_str = request.form.get('end_date', '')
            status = request.form.get('status', 'present')
            
            # التحقق من البيانات
            if not department_ids:
                flash('يرجى اختيار قسم واحد على الأقل', 'warning')
                return redirect(url_for('mass.departments'))
            
            # معالجة التواريخ
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
                
                if end_date < start_date:
                    flash('تاريخ النهاية يجب أن يكون بعد تاريخ البداية', 'warning')
                    return redirect(url_for('mass.departments'))
            except ValueError:
                flash('الرجاء إدخال تواريخ صالحة', 'warning')
                return redirect(url_for('mass.departments'))
            
            # معالجة كل قسم على حدة
            dept_count = 0
            emp_count = 0
            record_count = 0
            
            for dept_id_str in department_ids:
                dept_id = int(dept_id_str)
                department = Department.query.get(dept_id)
                
                if not department:
                    continue
                
                dept_count += 1
                
                # الحصول على الموظفين النشطين في القسم باستخدام علاقة many-to-many
                employees = [emp for emp in department.employees if emp.status == 'active']
                
                dept_emp_count = len(employees)
                emp_count += dept_emp_count
                
                # تسجيل الحضور لكل موظف لكل يوم
                current_date = start_date
                while current_date <= end_date:
                    for employee in employees:
                        # البحث عن سجل موجود
                        existing = Attendance.query.filter_by(
                            employee_id=employee.id,
                            date=current_date
                        ).first()
                        
                        if existing:
                            # تحديث السجل الموجود
                            existing.status = status
                            if status != 'present':
                                existing.check_in = None
                                existing.check_out = None
                        else:
                            # إنشاء سجل جديد
                            attendance = Attendance()
                            attendance.employee_id = employee.id
                            attendance.date = current_date
                            attendance.status = status
                            db.session.add(attendance)
                        
                        record_count += 1
                    
                    # الانتقال لليوم التالي
                    current_date += timedelta(days=1)
                
                # تسجيل النشاط في سجل النظام
                try:
                    SystemAudit.create_audit_record(
                        user_id=None,
                        action='mass_attendance',
                        entity_type='department',
                        entity_id=department.id,
                        entity_name=department.name,
                        details=f'تم تسجيل حضور جماعي لقسم {department.name} للفترة من {start_date} إلى {end_date}'
                    )
                except Exception as e:
                    print(f"خطأ في تسجيل النشاط: {str(e)}")
            
            # حفظ التغييرات
            db.session.commit()
            
            # عرض رسالة نجاح
            days_count = (end_date - start_date).days + 1
            flash(f'تم تسجيل الحضور لـ {dept_count} قسم و {emp_count} موظف خلال {days_count} يوم بإجمالي {record_count} سجل', 'success')
            
            # العودة لصفحة الحضور
            return redirect(url_for('attendance.index'))
            
        except Exception as e:
            db.session.rollback()
            error = str(e)
            flash(f'حدث خطأ: {error}', 'danger')
    
    # الحصول على قائمة الأقسام
    try:
        departments = Department.query.all()
    except Exception as e:
        departments = []
        flash(f'خطأ في تحميل الأقسام: {str(e)}', 'warning')
    
    # تقديم القالب
    return render_template(
        'attendance/mass_departments.html',
        departments=departments,
        today=today,
        form=form,
        error=error
    )