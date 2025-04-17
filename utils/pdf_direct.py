"""
وحدة إنشاء ملفات PDF باستخدام ReportLab مع دعم للنصوص العربية
باستخدام طريقة مباشرة عبر canvas
"""
import os
from io import BytesIO
import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm, mm

# تسجيل الخطوط العربية
ARABIC_FONT = 'Helvetica'  # الخط الافتراضي

try:
    # قائمة بالخطوط العربية المتاحة
    arabic_fonts = [
        {'name': 'ArefRuqaa', 'path': os.path.join('static', 'fonts', 'ArefRuqaa-Regular.ttf')},
        {'name': 'Tajawal', 'path': os.path.join('static', 'fonts', 'Tajawal-Regular.ttf')}
    ]
    
    # محاولة تسجيل الخطوط العربية
    for font in arabic_fonts:
        if os.path.exists(font['path']):
            pdfmetrics.registerFont(TTFont(font['name'], font['path']))
            ARABIC_FONT = font['name']
            print(f"Registered Arabic font for direct PDF: {font['name']}")
            break
    
    # إذا لم يتم العثور على أي خط عربي
    if ARABIC_FONT == 'Helvetica':
        print("Warning: No Arabic fonts found, using default font")
        
except Exception as e:
    print(f"Error registering fonts: {str(e)}")


def reshape_arabic_text(text):
    """
    تشكيل النص العربي بشكل صحيح للعرض في ملفات PDF
    
    Args:
        text: النص العربي المراد تشكيله
        
    Returns:
        النص بعد التشكيل
    """
    if not text:
        return ""
    try:
        # تشكيل النص العربي
        reshaped_text = arabic_reshaper.reshape(str(text))
        # عكس النص لدعم اللغة العربية (من اليمين إلى اليسار)
        bidi_text = get_display(reshaped_text)
        return bidi_text
    except Exception as e:
        print(f"Error reshaping text: {str(e)}")
        return str(text)  # إرجاع النص الأصلي في حالة الخطأ


def generate_arabic_pdf_directly(data, filename=None, landscape_mode=False):
    """
    إنشاء ملف PDF باستخدام طريقة مباشرة مع دعم للنصوص العربية
    
    Args:
        data: القاموس الذي يحتوي على بيانات الراتب
        filename: اسم الملف (اختياري، إذا كان None سيتم إرجاع البيانات فقط)
        landscape_mode: هل التقرير بالوضع الأفقي (اختياري)
        
    Returns:
        BytesIO أو None
    """
    try:
        # تحديد حجم الصفحة
        pagesize = landscape(A4) if landscape_mode else A4
        
        # إنشاء كائن BytesIO لاحتواء البيانات
        buffer = BytesIO()
        
        # إنشاء كائن الرسم
        c = canvas.Canvas(buffer, pagesize=pagesize)
        
        # تعيين الخط العربي
        c.setFont(ARABIC_FONT, 16)
        
        # عنوان التقرير
        c.drawString(pagesize[0]/2 - 50, pagesize[1] - 3*cm, reshape_arabic_text("إشعار راتب"))
        
        # معلومات الموظف
        c.setFont(ARABIC_FONT, 12)
        
        # اسم الموظف
        employee_name = data.get('employee_name', '')
        c.drawString(15*cm, pagesize[1] - 5*cm, reshape_arabic_text(f"اسم الموظف: {employee_name}"))
        
        # معلومات الراتب
        c.setFont(ARABIC_FONT, 10)
        y_position = pagesize[1] - 7*cm
        
        # الراتب الأساسي
        basic_salary = data.get('basic_salary', 0)
        c.drawString(15*cm, y_position, reshape_arabic_text(f"الراتب الأساسي: {basic_salary}"))
        y_position -= 1*cm
        
        # البدلات
        allowances = data.get('allowances', 0)
        c.drawString(15*cm, y_position, reshape_arabic_text(f"البدلات: {allowances}"))
        y_position -= 1*cm
        
        # الخصومات
        deductions = data.get('deductions', 0)
        c.drawString(15*cm, y_position, reshape_arabic_text(f"الخصومات: {deductions}"))
        y_position -= 1*cm
        
        # المكافآت
        bonus = data.get('bonus', 0)
        c.drawString(15*cm, y_position, reshape_arabic_text(f"المكافآت: {bonus}"))
        y_position -= 1*cm
        
        # صافي الراتب
        net_salary = data.get('net_salary', 0)
        c.drawString(15*cm, y_position, reshape_arabic_text(f"صافي الراتب: {net_salary}"))
        
        # التوقيعات
        c.setFont(ARABIC_FONT, 12)
        c.drawString(15*cm, 5*cm, reshape_arabic_text("توقيع المدير المالي:"))
        c.drawString(5*cm, 5*cm, reshape_arabic_text("توقيع الموظف:"))
        
        # إتمام الصفحة
        c.save()
        
        # إذا كان هناك اسم ملف، يتم حفظ البيانات في الملف
        if filename:
            with open(filename, 'wb') as f:
                f.write(buffer.getvalue())
            return None
        
        # إعادة توجيه المؤشر إلى بداية البيانات
        buffer.seek(0)
        return buffer.getvalue()
    except Exception as e:
        print(f"Error creating PDF: {str(e)}")
        raise e