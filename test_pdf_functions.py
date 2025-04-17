from datetime import datetime
import traceback
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# تجنب استيراد الموديل مباشرة لتفادي الاستيراد الدوري
# نستورد الوظائف مباشرة دون الحاجة لاستيراد الموديل
from utils.salary_notification import generate_salary_notification_pdf
from utils.pdf_generator import generate_salary_report_pdf

class SalaryMock:
    """Mock salary object for testing"""
    def __init__(self):
        self.month = 4
        self.year = 2025
        self.basic_salary = 5000
        self.allowances = 500
        self.deductions = 200
        self.bonus = 100
        self.net_salary = 5400
        self.notes = "ملاحظات اختبارية"
        self.employee = EmployeeMock()

class EmployeeMock:
    """Mock employee object for testing"""
    def __init__(self):
        self.name = "موظف اختباري"
        self.employee_id = "EMP12345"
        self.job_title = "مطور برمجيات"
        self.department = DepartmentMock()

class DepartmentMock:
    """Mock department object for testing"""
    def __init__(self):
        self.name = "قسم البرمجة"

def test_salary_notification():
    """Test the salary notification PDF generation function"""
    try:
        print("بدء اختبار وظيفة إشعار الراتب...")
        mock_salary = SalaryMock()
        pdf_data = generate_salary_notification_pdf(mock_salary)
        assert pdf_data is not None, "لم يتم إنشاء بيانات PDF"
        print("نجح اختبار إشعار الراتب!")
        return True
    except Exception as e:
        print(f"فشل اختبار إشعار الراتب بسبب: {str(e)}")
        traceback.print_exc()
        return False

def test_salary_report():
    """Test the salary report PDF generation function"""
    try:
        print("بدء اختبار وظيفة تقرير الرواتب...")
        salaries = [SalaryMock() for _ in range(3)]
        pdf_data = generate_salary_report_pdf(salaries, 4, 2025)
        assert pdf_data is not None, "لم يتم إنشاء بيانات PDF"
        print("نجح اختبار تقرير الرواتب!")
        return True
    except Exception as e:
        print(f"فشل اختبار تقرير الرواتب بسبب: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # تنفيذ الاختبارات
    notification_success = test_salary_notification()
    report_success = test_salary_report()
    
    if notification_success and report_success:
        print("نجحت جميع الاختبارات!")
    else:
        print("فشلت بعض الاختبارات، راجع الأخطاء أعلاه.")