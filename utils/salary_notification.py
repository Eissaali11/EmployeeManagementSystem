"""
وحدة إنشاء إشعار راتب كملف PDF محسنة - الإصدار الاحترافي العربي
تصميم احترافي مع دعم كامل للنصوص العربية
"""

from utils.professional_arabic_salary_pdf import create_professional_arabic_salary_pdf

def generate_salary_notification_pdf(salary):
    """
    إنشاء إشعار راتب محترف كملف PDF مع دعم كامل للعربية
    
    Args:
        salary: كائن Salary يحتوي على بيانات الراتب
        
    Returns:
        bytes: ملف PDF كـ bytes
    """
    try:
        # استخدام المولد الاحترافي الجديد مع دعم النصوص العربية
        return create_professional_arabic_salary_pdf(salary)
        
    except Exception as e:
        print(f"خطأ في إنشاء إشعار الراتب الاحترافي: {str(e)}")
        # في حالة الفشل، محاولة استخدام المولد القديم كاحتياطي
        try:
            from utils.ultra_safe_pdf import create_ultra_safe_salary_pdf
            return create_ultra_safe_salary_pdf(salary)
        except Exception as e2:
            print(f"فشل أيضاً في المولد الاحتياطي: {str(e2)}")
            raise Exception(f"فشل تام في إنشاء إشعار الراتب: {str(e)}")


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