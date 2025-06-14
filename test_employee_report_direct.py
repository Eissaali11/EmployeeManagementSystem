"""
اختبار مباشر لتقرير الموظف بالتصميم المطلوب
"""
import os
import sys
sys.path.append('.')

from utils.employee_simple_designed_report import generate_simple_designed_employee_report

def test_employee_report():
    """اختبار إنشاء تقرير الموظف مباشرة"""
    try:
        # إنشاء التقرير للموظف رقم 178
        pdf_buffer, error = generate_simple_designed_employee_report(178)
        
        if pdf_buffer:
            # حفظ الملف
            with open('test_employee_178_designed_report.pdf', 'wb') as f:
                f.write(pdf_buffer)
            print("✓ تم إنشاء التقرير بنجاح!")
            print(f"حجم الملف: {len(pdf_buffer)} بايت")
            return True
        else:
            print(f"✗ خطأ في إنشاء التقرير: {error}")
            return False
            
    except Exception as e:
        print(f"✗ خطأ: {str(e)}")
        return False

if __name__ == "__main__":
    # تشغيل الاختبار
    success = test_employee_report()
    if success:
        print("التقرير جاهز للمعاينة!")
    else:
        print("فشل في إنشاء التقرير")