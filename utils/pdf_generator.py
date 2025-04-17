"""
وحدة إنشاء تقارير PDF باستخدام FPDF
"""
from datetime import datetime
from utils.pdf_generator_new import generate_salary_report_pdf as generate_fpdf_report

def generate_salary_report_pdf(salaries, month, year):
    """
    إنشاء تقرير PDF للرواتب باستخدام FPDF مع دعم للغة العربية
    
    Args:
        salaries: قائمة بكائنات الرواتب
        month: رقم الشهر
        year: السنة
        
    Returns:
        bytes يحتوي على ملف PDF
    """
    try:
        # التأكد من تحويل الشهر والسنة إلى قيم عددية
        month = int(month) if not isinstance(month, int) else month
        year = int(year) if not isinstance(year, int) else year
        
        # الحصول على اسم الشهر بالعربية
        month_names = {
            1: 'يناير', 2: 'فبراير', 3: 'مارس', 4: 'أبريل',
            5: 'مايو', 6: 'يونيو', 7: 'يوليو', 8: 'أغسطس',
            9: 'سبتمبر', 10: 'أكتوبر', 11: 'نوفمبر', 12: 'ديسمبر'
        }
        month_name = month_names.get(month, str(month))
        
        # إعداد بيانات الرواتب للتقرير مع التأكد من تحويل جميع البيانات إلى نوع مناسب
        salary_data = []
        for salary in salaries:
            salary_data.append({
                'employee_name': str(salary.employee.name),
                'employee_id': str(salary.employee.employee_id),
                'basic_salary': float(salary.basic_salary),
                'allowances': float(salary.allowances),
                'deductions': float(salary.deductions),
                'bonus': float(salary.bonus),
                'net_salary': float(salary.net_salary)
            })
        
        # إنشاء ملف PDF باستخدام FPDF مع تحويل جميع المعاملات إلى سلاسل نصية
        return generate_fpdf_report(salary_data, month_name, str(year))
    
    except Exception as e:
        print(f"خطأ في إنشاء تقرير PDF: {str(e)}")
        raise Exception(f"خطأ في إنشاء تقرير PDF: {str(e)}")
