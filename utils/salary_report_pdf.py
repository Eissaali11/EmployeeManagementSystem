from io import BytesIO
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import inch
import arabic_reshaper
from bidi.algorithm import get_display
from datetime import datetime

# --- !!! هام جداً !!! ---
# تأكد من أن لديك ملف خط عربي صالح في المسار المحدد.
# إذا كان ملف Cairo.ttf لديك صالحاً وموجوداً في static/fonts، استخدم المسار التالي:
# FONT_PATH = "static/fonts/Cairo-Regular.ttf" # أو اسم الخط المناسب
# FONT_NAME = "Cairo"
# حالياً، سأستخدم اسماً عاماً كعنصر نائب.

# ---!!! الرجاء تعديل هذا المسار واسم الخط حسب ملف الخط العربي المتوفر لديك !!!---
ARABIC_FONT_PATH = "static/fonts/Cairo.ttf" # مثال: تأكد أن هذا الملف موجود وصالح
ARABIC_FONT_NAME = "ArabicFont" # اسم ستستخدمه في ReportLab

try:
    pdfmetrics.registerFont(TTFont(ARABIC_FONT_NAME, ARABIC_FONT_PATH))
except Exception as e:
    print(f"خطأ في تسجيل الخط العربي: {e}. تأكد من صحة مسار واسم ملف الخط.")
    # يمكنك وضع خط احتياطي هنا إذا أردت، أو ترك الخطأ ليظهر
    # pdfmetrics.registerFont(TTFont(ARABIC_FONT_NAME, "Helvetica")) # خط احتياطي غير عربي


def arabic_text(text):
    """يعالج النص العربي للعرض الصحيح في PDF."""
    if not text:
        return ""
    reshaped_text = arabic_reshaper.reshape(str(text))
    bidi_text = get_display(reshaped_text)
    return bidi_text

def generate_salary_report_pdf(salaries, report_params=None):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4),
                            rightMargin=0.5*inch, leftMargin=0.5*inch,
                            topMargin=0.5*inch, bottomMargin=0.5*inch)

    styles = getSampleStyleSheet()
    style_normal = ParagraphStyle('normal', fontName=ARABIC_FONT_NAME, fontSize=10, parent=styles['Normal'])
    style_heading = ParagraphStyle('heading', fontName=ARABIC_FONT_NAME, fontSize=14, alignment=1, parent=styles['Heading1'], leading=16)
    style_table_header = ParagraphStyle('table_header', fontName=ARABIC_FONT_NAME, fontSize=10, alignment=1, parent=style_normal, textColor=colors.whitesmoke)
    style_table_cell = ParagraphStyle('table_cell', fontName=ARABIC_FONT_NAME, fontSize=9, parent=style_normal, alignment=1)

    elements = []

    title_text = "تقرير الرواتب"
    if report_params:
        if report_params.get("year") and report_params.get("month"):
            title_text += f" لشهر {report_params['month']}/{report_params['year']}"
        elif report_params.get("year"):
            title_text += f" لسنة {report_params['year']}"
        if report_params.get("department_name"):
            title_text += f" - قسم: {report_params['department_name']}"

    elements.append(Paragraph(arabic_text(title_text), style_heading))
    elements.append(Spacer(1, 0.2 * inch))

    data = [
        [Paragraph(arabic_text(col), style_table_header) for col in [
            "اسم الموظف", "القسم", "الشهر", "السنة", "الراتب الأساسي", "البدلات", "الخصومات", "المكافآت", "صافي الراتب"
        ]]
    ]

    for salary in salaries:
        employee_name = salary.employee.name if salary.employee else "غير محدد"
        department_name = salary.employee.department.name if salary.employee and salary.employee.department else "غير محدد"

        row = [
            Paragraph(arabic_text(employee_name), style_table_cell),
            Paragraph(arabic_text(department_name), style_table_cell),
            Paragraph(arabic_text(salary.month), style_table_cell),
            Paragraph(arabic_text(salary.year), style_table_cell),
            Paragraph(arabic_text(f"{salary.basic_salary:.2f}"), style_table_cell),
            Paragraph(arabic_text(f"{salary.allowances:.2f}"), style_table_cell),
            Paragraph(arabic_text(f"{salary.deductions:.2f}"), style_table_cell),
            Paragraph(arabic_text(f"{salary.bonus:.2f}"), style_table_cell),
            Paragraph(arabic_text(f"{salary.net_salary:.2f}"), style_table_cell),
        ]
        data.append(row)

    if not salaries:
        data.append([Paragraph(arabic_text("لا توجد بيانات لعرضها"), style_table_cell, colSpan=9)])

    table = Table(data, colWidths=[2*inch, 1.5*inch, 0.5*inch, 0.5*inch, 1*inch, 1*inch, 1*inch, 1*inch, 1.2*inch])
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4F81BD")), # لون رأس الجدول
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), ARABIC_FONT_NAME), # خط رأس الجدول
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor("#DCE6F1")), # لون خلفية الصفوف الفردية
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), ARABIC_FONT_NAME), # خط خلايا الجدول
    ])
    # تطبيق لون مختلف للصفوف الزوجية
    for i, row in enumerate(salaries):
        if i % 2 == 0: # الصفوف الزوجية (بعد الهيدر)
            table_style.add('BACKGROUND', (0, i + 1), (-1, i + 1), colors.HexColor("#B8CCE4"))

    table.setStyle(table_style)
    elements.append(table)

    elements.append(Spacer(1, 0.3 * inch))
    elements.append(Paragraph(arabic_text(f"تاريخ التقرير: {datetime.now().strftime('%Y-%m-%d %H:%M')}"), style_normal))

    doc.build(elements)
    buffer.seek(0)
    return buffer