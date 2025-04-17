"""
وحدة إنشاء إشعار راتب كملف PDF
استخدام FPDF لإنشاء ملفات PDF مع دعم للنصوص العربية
"""
from datetime import datetime
from utils.pdf_generator_new import generate_salary_notification_pdf as generate_fpdf_notification

def generate_salary_notification_pdf(salary):
    """
    إنشاء إشعار راتب لموظف كملف PDF
    
    Args:
        salary: كائن Salary يحتوي على بيانات الراتب
        
    Returns:
        bytes يحتوي على ملف PDF
    """
    try:
        # التأكد من تحويل الشهر إلى عدد صحيح
        month = int(salary.month) if not isinstance(salary.month, int) else salary.month
        
        # الحصول على اسم الشهر بالعربية
        month_names = {
            1: 'يناير', 2: 'فبراير', 3: 'مارس', 4: 'أبريل',
            5: 'مايو', 6: 'يونيو', 7: 'يوليو', 8: 'أغسطس',
            9: 'سبتمبر', 10: 'أكتوبر', 11: 'نوفمبر', 12: 'ديسمبر'
        }
        month_name = month_names.get(month, str(month))
        
        # تحضير البيانات للقالب مع التأكد من تحويل جميع البيانات إلى نوع مناسب
        data = {
            'employee_name': str(salary.employee.name),
            'employee_id': str(salary.employee.employee_id),
            'job_title': str(salary.employee.job_title),
            'department_name': str(salary.employee.department.name) if salary.employee.department else None,
            'month_name': str(month_name),
            'year': str(salary.year) if isinstance(salary.year, (int, float)) else salary.year,
            'basic_salary': float(salary.basic_salary),
            'allowances': float(salary.allowances),
            'bonus': float(salary.bonus),
            'deductions': float(salary.deductions),
            'net_salary': float(salary.net_salary),
            'notes': str(salary.notes) if salary.notes else None,
            'current_date': datetime.now().strftime('%Y-%m-%d')
        }
        
        # إنشاء ملف PDF باستخدام FPDF
        return generate_fpdf_notification(data)
        
    except Exception as e:
        print(f"خطأ في إنشاء إشعار الراتب: {str(e)}")
        raise Exception(f"خطأ في إنشاء إشعار الراتب: {str(e)}")


def generate_batch_salary_notifications(department_id=None, month=None, year=None):
    """
    إنشاء إشعارات رواتب مجمعة لموظفي قسم معين أو لكل الموظفين
    
    Args:
        department_id: معرف القسم (اختياري)
        month: رقم الشهر (إلزامي)
        year: السنة (إلزامي)
        
    Returns:
        قائمة بأسماء الموظفين الذين تم إنشاء إشعارات لهم
    """
    from models import Salary, Employee
    
    # التأكد من تحويل البيانات إلى النوع المناسب
    month = int(month) if month is not None and not isinstance(month, int) else month
    year = int(year) if year is not None and not isinstance(year, int) else year
    department_id = int(department_id) if department_id is not None and not isinstance(department_id, int) else department_id
    
    # بناء الاستعلام
    salary_query = Salary.query.filter_by(month=month, year=year)
    
    # إذا تم تحديد قسم معين
    if department_id:
        employees = Employee.query.filter_by(department_id=department_id).all()
        employee_ids = [emp.id for emp in employees]
        salary_query = salary_query.filter(Salary.employee_id.in_(employee_ids))
        
    # تنفيذ الاستعلام
    salaries = salary_query.all()
    
    # قائمة بأسماء الموظفين الذين تم إنشاء إشعارات لهم
    processed_employees = []
    
    # إنشاء إشعار لكل موظف
    for salary in salaries:
        try:
            # إنشاء إشعار وإضافة اسم الموظف إلى القائمة
            generate_salary_notification_pdf(salary)
            processed_employees.append(salary.employee.name)
        except Exception as e:
            # تسجيل الخطأ
            print(f"خطأ في إنشاء إشعار للموظف {salary.employee.name}: {str(e)}")
            
    return processed_employees