from flask import Blueprint, jsonify
from models import Employee, Department, Document, GovernmentFee
from app import db

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/employees')
def get_employees():
    """الحصول على قائمة الموظفين لاستخدامها في واجهات المستخدم"""
    employees = Employee.query.filter_by(status='active').all()
    employees_list = []
    
    for employee in employees:
        employee_data = {
            'id': employee.id,
            'employee_id': employee.employee_id,
            'name': employee.name,
            'job_title': employee.job_title,
            'department': employee.department.name if employee.department else None,
            'contract_type': employee.contract_type,
            'nationality': employee.nationality,
            'basic_salary': employee.basic_salary,
            'has_national_balance': employee.has_national_balance
        }
        employees_list.append(employee_data)
    
    return jsonify(employees_list)

@api_bp.route('/departments')
def get_departments():
    """الحصول على قائمة الأقسام لاستخدامها في واجهات المستخدم"""
    departments = Department.query.all()
    departments_list = []
    
    for department in departments:
        department_data = {
            'id': department.id,
            'name': department.name,
            'description': department.description,
            'manager': department.manager.name if department.manager else None,
            'employee_count': len(department.employees)
        }
        departments_list.append(department_data)
    
    return jsonify(departments_list)

@api_bp.route('/documents/expiring/<int:days>')
def get_expiring_documents(days):
    """الحصول على المستندات التي ستنتهي خلال عدد محدد من الأيام"""
    from datetime import datetime, timedelta
    
    # حساب تاريخ البداية والنهاية
    today = datetime.now().date()
    end_date = today + timedelta(days=days)
    
    # البحث عن المستندات التي تنتهي في هذه الفترة
    documents = Document.query.filter(
        Document.expiry_date >= today,
        Document.expiry_date <= end_date
    ).all()
    
    documents_list = []
    for doc in documents:
        days_remaining = (doc.expiry_date - today).days
        document_data = {
            'id': doc.id,
            'employee_id': doc.employee_id,
            'employee_name': doc.employee.name,
            'document_type': doc.document_type,
            'document_number': doc.document_number,
            'expiry_date': doc.expiry_date.strftime('%Y-%m-%d'),
            'days_remaining': days_remaining,
            'contract_type': doc.employee.contract_type,
            'nationality': doc.employee.nationality
        }
        documents_list.append(document_data)
    
    return jsonify(documents_list)

@api_bp.route('/fees/monthly/<int:year>')
def get_monthly_fees(year):
    """الحصول على إجمالي الرسوم الشهرية لسنة معينة"""
    from sqlalchemy import func, extract
    
    monthly_data = db.session.query(
        extract('month', GovernmentFee.fee_date).label('month'),
        func.sum(GovernmentFee.amount).label('total_amount')
    ).filter(extract('year', GovernmentFee.fee_date) == year)\
     .group_by('month')\
     .order_by('month')\
     .all()
    
    # تهيئة مصفوفة لجميع الشهور
    months_data = [0] * 12
    
    # ملء البيانات المتوفرة
    for month, amount in monthly_data:
        months_data[int(month)-1] = float(amount)
    
    return jsonify({
        'year': year,
        'months': ["يناير", "فبراير", "مارس", "إبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"],
        'data': months_data
    })

@api_bp.route('/fees/summary/<int:year>')
def get_fees_summary(year):
    """الحصول على ملخص الرسوم السنوية حسب النوع"""
    from sqlalchemy import func, extract
    
    # استخراج مجموع الرسوم حسب النوع لسنة معينة
    fee_types_data = db.session.query(
        GovernmentFee.fee_type,
        func.sum(GovernmentFee.amount).label('total_amount')
    ).filter(extract('year', GovernmentFee.fee_date) == year)\
     .group_by(GovernmentFee.fee_type)\
     .all()
    
    # تنظيم البيانات في قاموس
    fee_summary = {
        'labor_office': 0,
        'passport': 0,
        'insurance': 0,
        'social_insurance': 0,
        'other': 0
    }
    
    for fee_type, amount in fee_types_data:
        if fee_type in fee_summary:
            fee_summary[fee_type] = float(amount)
        else:
            fee_summary['other'] += float(amount)
    
    # حساب الإجمالي
    total_fees = sum(fee_summary.values())
    
    # حساب المتوسط الشهري
    monthly_average = {key: value / 12 for key, value in fee_summary.items()}
    monthly_total = total_fees / 12
    
    return jsonify({
        'year': year,
        'annual': fee_summary,
        'annual_total': total_fees,
        'monthly': monthly_average,
        'monthly_total': monthly_total
    })

@api_bp.route('/employees/nationality/stats')
def get_nationality_stats():
    """إحصائيات عدد الموظفين حسب الجنسية ونوع العقد"""
    from sqlalchemy import func
    
    # إحصائيات حسب نوع العقد
    contract_stats = db.session.query(
        Employee.contract_type,
        func.count(Employee.id).label('count')
    ).group_by(Employee.contract_type).all()
    
    contract_summary = {
        'saudi': 0,
        'foreign': 0
    }
    
    for contract_type, count in contract_stats:
        if contract_type in contract_summary:
            contract_summary[contract_type] = count
        else:
            # افتراضيًا، إذا لم يكن النوع محددًا نعتبره وافد
            contract_summary['foreign'] += count
    
    # إحصائيات حسب الجنسية
    nationality_stats = db.session.query(
        Employee.nationality,
        func.count(Employee.id).label('count')
    ).filter(Employee.nationality != None)\
     .group_by(Employee.nationality)\
     .order_by(func.count(Employee.id).desc())\
     .limit(5)\
     .all()
    
    nationality_summary = {}
    for nationality, count in nationality_stats:
        nationality_summary[nationality] = count
    
    return jsonify({
        'contract_stats': contract_summary,
        'nationality_stats': nationality_summary,
        'total_employees': sum(contract_summary.values())
    })