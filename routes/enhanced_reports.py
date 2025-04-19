"""
وحدة تقارير محسنة تستخدم وظائف PDF المحسنة مع دعم كامل للغة العربية
"""
from flask import Blueprint, render_template, request, jsonify, make_response, send_file
from sqlalchemy import func
from datetime import datetime, date, timedelta
from io import BytesIO
from app import db
from models import Department, Employee, Attendance, Salary, Document, SystemAudit
from utils.date_converter import parse_date, format_date_hijri, format_date_gregorian, get_month_name_ar
from utils.excel import generate_employee_excel, generate_salary_excel
# استخدام دالة تقرير الرواتب المحسنة من الملف الجديد
from utils.pdf_generator_fixed import generate_salary_report_pdf
# استيراد الدوال المتبقية من الملف الأصلي
from utils.pdf_generator_new import generate_salary_notification_pdf, generate_workshop_receipts_pdf as generate_vehicle_handover_pdf

# إنشاء موجه المسارات
enhanced_reports_bp = Blueprint('enhanced_reports', __name__)

@enhanced_reports_bp.route('/')
def index():
    """
    الصفحة الرئيسية للتقارير المحسنة
    """
    from datetime import datetime
    # الحصول على الشهر والسنة الحالية
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    # الحصول على قائمة الأقسام
    departments = Department.query.all()
    
    return render_template('reports/enhanced.html', 
                         departments=departments,
                         current_year=current_year,
                         current_month=current_month,
                         get_month_name_ar=get_month_name_ar)

@enhanced_reports_bp.route('/salaries/pdf')
def salaries_pdf():
    """
    تصدير تقرير الرواتب إلى PDF باستخدام النسخة المحسنة
    """
    # الحصول على معلمات الفلتر
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    month = int(request.args.get('month', current_month))
    year = int(request.args.get('year', current_year))
    department_id = request.args.get('department_id', '')
    
    # استعلام الرواتب
    salaries_query = Salary.query.filter_by(
        month=month,
        year=year
    )
    
    # تطبيق فلتر القسم إذا كان محدداً
    if department_id:
        # الحصول على معرفات الموظفين في القسم المحدد
        dept_employee_ids = [e.id for e in Employee.query.filter_by(department_id=department_id).all()]
        salaries_query = salaries_query.filter(Salary.employee_id.in_(dept_employee_ids))
        department = Department.query.get(department_id)
        department_name = department.name if department else ""
    else:
        department_name = "جميع الأقسام"
    
    # الحصول على بيانات الرواتب مع تفاصيل الموظفين
    salaries_data = []
    for salary in salaries_query.all():
        employee = Employee.query.get(salary.employee_id)
        if employee:
            salaries_data.append({
                'employee_name': employee.name,
                'employee_id': employee.employee_id,
                'basic_salary': float(salary.basic_salary),
                'allowances': float(salary.allowances),
                'deductions': float(salary.deductions),
                'bonus': float(salary.bonus),
                'net_salary': float(salary.net_salary)
            })
    
    try:
        # الحصول على اسم الشهر العربي
        month_name = get_month_name_ar(month)
        
        # استدعاء الدالة المحسنة من الملف الجديد التي تدعم اللغة العربية بشكل صحيح
        pdf_data = generate_salary_report_pdf(salaries_data, month_name, year)
        
        # إرجاع البيانات كملف تنزيل
        return send_file(
            BytesIO(pdf_data),
            as_attachment=True,
            download_name=f"salaries_report_{year}_{month}.pdf",
            mimetype='application/pdf'
        )
    
    except Exception as e:
        # في حالة حدوث خطأ، نسجله ونعرض رسالة خطأ للمستخدم
        print(f"حدث خطأ أثناء إنشاء تقرير الرواتب: {str(e)}")
        return jsonify({"error": "حدث خطأ أثناء إنشاء تقرير الرواتب"}), 500

@enhanced_reports_bp.route('/salary_notification/<int:salary_id>/pdf')
def salary_notification_pdf(salary_id):
    """
    إنشاء إشعار راتب فردي كملف PDF
    """
    # الحصول على الراتب
    salary = Salary.query.get_or_404(salary_id)
    
    # الحصول على معلومات الموظف
    employee = Employee.query.get_or_404(salary.employee_id)
    
    # الحصول على القسم إذا وجد
    department = Department.query.get(employee.department_id) if employee.department_id else None
    
    # إعداد البيانات لإنشاء PDF
    notification_data = {
        'employee_name': employee.name,
        'employee_id': employee.employee_id,
        'job_title': employee.job_title,
        'department_name': department.name if department else "",
        'month_name': get_month_name_ar(salary.month),
        'year': salary.year,
        'basic_salary': salary.basic_salary,
        'allowances': salary.allowances,
        'deductions': salary.deductions,
        'bonus': salary.bonus,
        'net_salary': salary.net_salary,
        'notes': salary.notes,
        'current_date': datetime.now().strftime('%Y-%m-%d')
    }
    
    try:
        # استدعاء الدالة المحسنة لإنشاء إشعار الراتب
        pdf_data = generate_salary_notification_pdf(notification_data)
        
        # إرجاع البيانات كملف تنزيل
        return send_file(
            BytesIO(pdf_data),
            as_attachment=True,
            download_name=f"salary_notification_{employee.employee_id}_{salary.month}_{salary.year}.pdf",
            mimetype='application/pdf'
        )
    
    except Exception as e:
        # في حالة حدوث خطأ، نسجله ونعرض رسالة خطأ للمستخدم
        print(f"حدث خطأ أثناء إنشاء إشعار الراتب: {str(e)}")
        return jsonify({"error": "حدث خطأ أثناء إنشاء إشعار الراتب"}), 500

@enhanced_reports_bp.route('/vehicle_handover/<int:handover_id>/pdf')
def vehicle_handover_pdf(handover_id):
    """
    إنشاء نموذج تسليم/استلام سيارة كملف PDF
    """
    # هنا يتم افتراض وجود نموذج VehicleHandover في النظام
    # في الحالة الفعلية، يجب استبدال هذا بالكود الفعلي للحصول على بيانات التسليم/الاستلام
    
    # نموذج بيانات للاختبار
    handover_data = {
        'vehicle': {
            'plate_number': 'أ ب ج 1234',
            'make': 'تويوتا',
            'model': 'كامري',
            'year': '2023',
            'color': 'أبيض'
        },
        'handover_type': 'تسليم',  # أو 'استلام'
        'handover_date': datetime.now().strftime('%Y-%m-%d'),
        'person_name': 'محمد أحمد',
        'vehicle_condition': 'حالة جيدة، لا توجد خدوش أو أضرار ظاهرة',
        'fuel_level': '3/4',
        'mileage': '15000',
        'has_spare_tire': True,
        'has_fire_extinguisher': True,
        'has_first_aid_kit': True,
        'has_warning_triangle': True,
        'has_tools': True,
        'notes': 'تم تسليم السيارة مع جميع المستندات المطلوبة',
        'form_link': 'https://example.com/vehicle-form/123'
    }
    
    try:
        # استدعاء الدالة المحسنة لإنشاء نموذج تسليم/استلام السيارة
        pdf_data = generate_vehicle_handover_pdf(handover_data)
        
        # إرجاع البيانات كملف تنزيل
        return send_file(
            BytesIO(pdf_data),
            as_attachment=True,
            download_name=f"vehicle_handover_{handover_data['vehicle']['plate_number']}.pdf",
            mimetype='application/pdf'
        )
    
    except Exception as e:
        # في حالة حدوث خطأ، نسجله ونعرض رسالة خطأ للمستخدم
        print(f"حدث خطأ أثناء إنشاء نموذج تسليم/استلام السيارة: {str(e)}")
        return jsonify({"error": "حدث خطأ أثناء إنشاء نموذج تسليم/استلام السيارة"}), 500