"""
وحدة إنشاء تقارير PDF باستخدام FPDF
"""
from datetime import datetime
from utils.fpdf_arabic import generate_salary_report_pdf as generate_fpdf_report

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
        # الحصول على اسم الشهر بالعربية
        month_names = {
            1: 'يناير', 2: 'فبراير', 3: 'مارس', 4: 'أبريل',
            5: 'مايو', 6: 'يونيو', 7: 'يوليو', 8: 'أغسطس',
            9: 'سبتمبر', 10: 'أكتوبر', 11: 'نوفمبر', 12: 'ديسمبر'
        }
        month_name = month_names.get(month, str(month))
        
        # إعداد بيانات الرواتب للتقرير
        salary_data = []
        for salary in salaries:
            salary_data.append({
                'employee_name': salary.employee.name,
                'employee_id': salary.employee.employee_id,
                'basic_salary': salary.basic_salary,
                'allowances': salary.allowances,
                'deductions': salary.deductions,
                'bonus': salary.bonus,
                'net_salary': salary.net_salary
            })
        
        # إنشاء ملف PDF باستخدام FPDF
        return generate_fpdf_report(salary_data, month_name, year)
    
    except Exception as e:
        print(f"خطأ في إنشاء تقرير PDF: {str(e)}")
        raise Exception(f"خطأ في إنشاء تقرير PDF: {str(e)}")
